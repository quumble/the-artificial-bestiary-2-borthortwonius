#!/usr/bin/env python3
"""Independently verify nine declared estimates and their bootstrap intervals.

Uses only the two published B/C CSVs, NumPy, and the standard library. It does
not import the analysis pipeline, estimator, input loader, or specifications.
The direct implementation groups raw records into cells and indexes sampled
word arrays, rather than reusing the pipeline's bootstrap count matrices.

Example, from any working directory:
    python check_selected_estimates.py --root /path/to/repository

The selected analysis must use 10,000 PCG64 draws at seed 20261115 and linear
percentiles. Each selected value must agree within an absolute tolerance of
2e-14. A failed check exits nonzero, including when Python runs with -O.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from math import comb
from pathlib import Path
import sys

import numpy as np

SCRIPT = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT.parent.parents[2]
DRAWS = 10000
SEED = 20261115
TOLERANCE = 2e-14

MODELS = (
    "claude-sonnet-4-6", "claude-haiku-4-5", "claude-sonnet-5-5", "claude-haiku-5-5",
    "gpt-5.4-mini", "gpt-5.4-nano", "gpt-6-sol", "gpt-6-luna",
)
ANTHROPIC = tuple(m for m in MODELS if m.startswith("claude"))
OPENAI = tuple(m for m in MODELS if m.startswith("gpt"))
CURRENT = ("claude-sonnet-5-5", "claude-haiku-5-5", "gpt-6-sol", "gpt-6-luna")
HISTORICAL = tuple(m for m in MODELS if m not in CURRENT)
REAL = tuple(f"real_{c}" for c in ("animal", "object", "idea"))
TYPE = tuple(f"type_of_{c}" for c in ("animal", "object", "idea"))
IMAGINARY = tuple(f"imaginary_{c}" for c in ("animal", "object", "idea"))
SEVEN = REAL + TYPE + ("neutral",)
ALL_CONDITIONS = SEVEN + IMAGINARY
SOURCE_SIZES = {
    "fresh-animal-intent": 8,
    "fresh-no-intent-claude": 8,
    "fresh-no-intent-gpt": 8,
    "known-animal-intent": 4,
    "known-no-intent": 4,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def predicate(record, arm, field):
    if field in ("E", "N"):
        name = {
            "B": {"E": "F_E", "N": "F_N"},
            "C": {"E": "E_description", "N": "N_nonrecognition_without_description"},
        }[arm][field]
        value = int(record[name])
        require(value in (0, 1), f"Nonbinary {arm}.{field}")
        return value
    if field == "possibility":
        return int(record["response_type"] == "DECLINE_WITH_POSSIBILITIES")
    if field == "decline":
        return int(record["response_type"] in ("DECLINE_WITH_POSSIBILITIES", "DECLINE_PLAIN"))
    raise ValueError(f"Unknown independent-check field {field}")


def run(root, estimates_path, output_path):
    base = root / "supplement/coding-heuristics"
    input_paths = {
        "B": base / "mechanical-coding-heuristic-v1/run-2026-11-15_claude-fable-5-2/coded_responses.csv",
        "C": base / "zoned-heuristic-v1/results/response_codes.csv",
    }
    execution_path = estimates_path.with_name("execution.json")
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    bootstrap = execution["bootstrap"]
    require(bootstrap["draws"] == DRAWS, "Expected an analysis with 10,000 draws")
    require(bootstrap["seed"] == SEED, "Expected analysis seed 20261115")
    require(bootstrap["rng"] == "numpy.Generator(PCG64)", "Expected PCG64 bootstrap")
    require(bootstrap["interval"] == "95% percentile, numpy.quantile(method='linear')",
            "Expected unadjusted 95% linear percentile intervals")
    require(execution["output_files"]["estimates.json"] == digest(estimates_path),
            "estimates.json does not match its execution receipt")

    exports = {arm: load_csv(path) for arm, path in input_paths.items()}
    require(all(len(records) == 16000 for records in exports.values()), "Expected 16,000 rows in each CSV")
    cells, keys = {}, {}
    for arm, source_column, key_column in (("B", "source_set_label", "row_id"), ("C", "source", "key")):
        grouped = defaultdict(list)
        indexed = {}
        for record in exports[arm]:
            key = record[key_column]
            require(key not in indexed, f"Duplicate {arm} trial {key}")
            indexed[key] = record
            cell = (record[source_column], record["word"], record["model"], record["condition"])
            grouped[cell].append(record)
        cells[arm] = grouped
        keys[arm] = indexed
        require(len(grouped) == 2560, f"Incomplete {arm} cell panel")
        for (source, word, model, condition), records in grouped.items():
            require(source in SOURCE_SIZES and model in MODELS and condition in ALL_CONDITIONS,
                    f"Unexpected {arm} panel member")
            repetitions = 5 if source.startswith("fresh") else 10
            require(sorted(int(r["rep"]) for r in records) == list(range(1, repetitions + 1)),
                    f"Unexpected repetition panel for {arm}: {source}, {word}, {model}, {condition}")
    require(keys["B"].keys() == keys["C"].keys(), "B and C trial keys differ")
    for key, b in keys["B"].items():
        c = keys["C"][key]
        require(all(b[field] == c[field] for field in ("batch", "word", "model", "condition", "rep")),
                f"B/C metadata differs for {key}")
        require(b["source_set_label"] == c["source"], f"B/C source differs for {key}")

    words = {
        source: sorted({r["word"] for r in exports["C"] if r["source"] == source})
        for source in sorted(SOURCE_SIZES)
    }
    require(all(len(words[s]) == n for s, n in SOURCE_SIZES.items()), "Unexpected source word counts")
    require(bootstrap["source_order"] == list(words) and bootstrap["word_order"] == words,
            "Analysis bootstrap word/source order differs from independent ordering")
    rng = np.random.Generator(np.random.PCG64(SEED))
    indexes = {s: rng.integers(0, len(ws), size=(DRAWS, len(ws))) for s, ws in words.items()}

    def mean(arm, field, conditions, models=MODELS, bank="fresh", sources=None, weights=None, pairs=False):
        sources = sources or [s for s in words if s.startswith(bank)]
        weights = weights or {s: 1 / len(sources) for s in sources}
        point = 0.0
        draws = np.zeros(DRAWS)
        for source in sources:
            word_values = []
            for word in words[source]:
                endpoint_values = []
                for model in models:
                    cell_values = []
                    for condition in conditions:
                        records = cells[arm][source, word, model, condition]
                        values = [predicate(r, arm, field) for r in records]
                        if pairs:
                            frequencies = Counter(values)
                            value = sum(comb(n, 2) for n in frequencies.values()) / comb(len(values), 2)
                        else:
                            value = sum(values) / len(values)
                        cell_values.append(value)
                    endpoint_values.append(sum(cell_values) / len(cell_values))
                word_values.append(sum(endpoint_values) / len(endpoint_values))
            vector = np.array(word_values)
            point += weights[source] * vector.mean()
            draws += weights[source] * vector[indexes[source]].mean(axis=1)
        return float(point), draws

    def difference(left, right):
        require(left[0] is not None and right[0] is not None, "Undefined selected difference")
        return left[0] - right[0], left[1] - right[1]

    def ratio(numerator, denominator):
        with np.errstate(invalid="ignore", divide="ignore"):
            draws = numerator[1] / denominator[1]
        draws[denominator[1] == 0] = np.nan
        point = numerator[0] / denominator[0] if denominator[0] else None
        return point, draws

    checks = {}
    for arm in ("B", "C"):
        checks[f"G1.E.{arm}"] = difference(mean(arm, "E", IMAGINARY), mean(arm, "E", REAL))
        known = difference(mean(arm, "N", SEVEN, CURRENT, bank="known"),
                           mean(arm, "N", SEVEN, HISTORICAL, bank="known"))
        fresh_weights = {"fresh-animal-intent": .5, "fresh-no-intent-claude": .25, "fresh-no-intent-gpt": .25}
        fresh = difference(mean(arm, "N", SEVEN, CURRENT, weights=fresh_weights),
                           mean(arm, "N", SEVEN, HISTORICAL, weights=fresh_weights))
        checks[f"H4.N.{arm}"] = difference(known, fresh)
        source_gaps = [difference(mean(arm, "N", SEVEN, ANTHROPIC, sources=[source]),
                                  mean(arm, "N", SEVEN, OPENAI, sources=[source]))
                       for source in ("fresh-no-intent-claude", "fresh-no-intent-gpt")]
        checks[f"H6.N.{arm}"] = difference(*source_gaps)
        checks[f"Q7.binary_consistency.fresh.gpt-6-sol.{arm}"] = mean(
            arm, "E", ALL_CONDITIONS, ("gpt-6-sol",), pairs=True)
    provider_ratios = [ratio(mean("C", "possibility", SEVEN, group), mean("C", "decline", SEVEN, group))
                       for group in (ANTHROPIC, OPENAI)]
    checks["Q1.possibility_share.Anthropic_minus_OpenAI"] = difference(*provider_ratios)

    result_list = json.loads(estimates_path.read_text(encoding="utf-8"))
    expected = {result["id"]: result for result in result_list}
    require(len(expected) == len(result_list), "Duplicate result IDs")
    comparisons = []
    for name, (point, samples) in checks.items():
        require(name in expected, f"Missing selected estimate {name}")
        finite = samples[np.isfinite(samples)]
        interval = np.quantile(finite, [.025, .975], method="linear") if len(finite) else None
        target = expected[name]
        require(point is not None and target["estimate"] is not None and
                np.isclose(point, target["estimate"], rtol=0, atol=TOLERANCE), f"Point mismatch: {name}")
        require(interval is not None and target["ci95"] is not None and
                np.allclose(interval, target["ci95"], rtol=0, atol=TOLERANCE), f"Interval mismatch: {name}")
        require(len(finite) == target["bootstrap_defined"], f"Defined-draw mismatch: {name}")
        comparisons.append({"id": name, "estimate": point, "ci95": interval.tolist(),
                            "bootstrap_defined": len(finite), "matches": True,
                            "absolute_point_difference": abs(point - target["estimate"]),
                            "max_absolute_interval_difference": float(np.max(np.abs(interval - target["ci95"])))})
    receipt = {
        "schema": "bestiary2-independent-selected-check/1",
        "method": "Independent raw-CSV cell grouping and bootstrap index-array means; no analysis-pipeline imports",
        "scope": "Nine selected B/C estimates, intervals and defined-draw counts; not a full independent replication",
        "draws": DRAWS, "seed": SEED, "rng": "numpy.Generator(PCG64)",
        "interval": "95% percentile with linear interpolation", "absolute_tolerance": TOLERANCE,
        "numpy": np.__version__, "python": sys.version,
        "input_csv_sha256": {str(p.relative_to(root)): digest(p) for p in input_paths.values()},
        "estimates_sha256": digest(estimates_path), "execution_sha256": digest(execution_path),
        "verifier_sha256": digest(SCRIPT), "checks_passed": len(comparisons), "comparisons": comparisons,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"checks_passed": len(comparisons), "absolute_tolerance": TOLERANCE,
                      "output": str(output_path)}))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--estimates", type=Path, help="Defaults to declared-contrasts/results/estimates.json")
    parser.add_argument("--output", type=Path, help="Defaults to declared-contrasts/results/independent_check.json")
    args = parser.parse_args()
    root = args.root.resolve()
    defaults = root / "supplement/coding-heuristics/declared-contrasts/results"
    try:
        run(root, (args.estimates or defaults / "estimates.json").resolve(),
            (args.output or defaults / "independent_check.json").resolve())
    except (ValueError, KeyError, OSError, ZeroDivisionError) as exc:
        raise SystemExit(f"Independent verification failed: {exc}") from exc
