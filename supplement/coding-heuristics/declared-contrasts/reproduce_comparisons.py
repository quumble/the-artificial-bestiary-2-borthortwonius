"""Reproduce the published three-way and human-pass comparisons.

These are historical response-weighted summaries, not the new declared
word-weighted estimates. Frozen source files and results are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from inputs import Dataset, MODELS, load_inputs

OUTCOMES = {
    "description": "E",
    "nonrecognition": "R",
    "nonrec_without_description": "N",
    "unmarked_description": "U",
}


def agreement(x: list, y: list) -> dict:
    """Pairwise-complete binary agreement, preserving marginal denominators."""
    pairs = [(a, b) for a, b in zip(x, y, strict=True) if a is not None and b is not None]
    n = len(pairs)
    if not n:
        raise ValueError("No jointly resolved judgments")
    observed = sum(a == b for a, b in pairs) / n
    px = sum(a for a, _ in pairs) / n
    py = sum(b for _, b in pairs) / n
    expected = px * py + (1 - px) * (1 - py)
    return {
        "n": n, "agree": observed,
        "kappa": (observed - expected) / (1 - expected) if expected < 1 else None,
        "rate_x": px, "rate_y": py,
        "x_only": sum(a == 1 and b == 0 for a, b in pairs),
        "y_only": sum(a == 0 and b == 1 for a, b in pairs),
    }


def label_values(description: str, nonrecognition: str, mark: str) -> dict:
    if description not in {"Y", "H", "S", "N"} or nonrecognition not in {"Y", "N"}:
        raise ValueError("Unknown reader code")
    desc = description in {"Y", "H"}
    if mark not in ({"Y", "E", "N"} if desc else {""}):
        raise ValueError("Reader mark is inconsistent with description code")
    nonrec = nonrecognition == "Y"
    return {
        "description": int(desc), "nonrecognition": int(nonrec),
        "nonrec_without_description": int(nonrec and not desc),
        "unmarked_description": int(desc and not nonrec and mark == "N"),
        "unmarked_echo": int(desc and not nonrec and mark in {"N", "E"}),
    }


def _mean(values) -> float:
    resolved = [v for v in values if v is not None]
    if not resolved:
        raise ValueError("No resolved observations")
    return sum(resolved) / len(resolved)


def sampling_weights(rows: list[dict], selected: list[str]) -> tuple[dict, dict]:
    """Recreate the published A/B-description disagreement-stratum weights.

    The target pool excludes A's 11 unresolved description calls, as the
    original sampling procedure did. These are not word-bootstrap weights.
    """
    indexed = {r["key"]: r for r in rows}
    pool = [r for r in rows if r["A"]["E"] is not None]

    def stratum(row):
        return row["A"]["E"], row["B"]["E"]

    population = Counter(stratum(r) for r in pool)
    sample = Counter(stratum(indexed[k]) for k in selected)
    if any(indexed[k]["A"]["E"] is None for k in selected):
        raise ValueError("Holdout includes a trial outside its original sampling pool")
    if set(sample) != set(population):
        raise ValueError("Holdout does not cover every population sampling stratum")
    weights = {k: (population[stratum(indexed[k])] / len(pool)) /
               (sample[stratum(indexed[k])] / len(selected)) for k in selected}
    strata = {str(s): [sample[s], population[s]] for s in sample}
    return weights, strata


def score_against_labels(selected, values, labels, weights, *, historical_names: bool) -> dict:
    n = raw = tp = fp = fn = 0
    weighted_correct = total_weight = 0.0
    for key in selected:
        value = values[key]
        if value is None:
            continue
        truth = labels[key]
        n += 1
        raw += value == truth
        weighted_correct += weights[key] * (value == truth)
        total_weight += weights[key]
        tp += value == 1 and truth == 1
        fp += value == 1 and truth == 0
        fn += value == 0 and truth == 1
    weighted = weighted_correct / total_weight if total_weight else None
    if historical_names:
        return dict(n=n, raw_correct=raw, weighted_accuracy=weighted,
                    false_pos=fp, false_neg=fn, true_pos=tp)
    return dict(n=n, correct=raw, weighted=weighted, fp=fp, fn=fn)


def reproduce(dataset: Dataset, repo_root: Path) -> dict:
    base = repo_root / "supplement/coding-heuristics"
    source_hashes = {}

    def read_json(relative):
        blob = (base / relative).read_bytes()
        source_hashes[relative] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
        return json.loads(blob)

    selected = read_json("zoned-heuristic-v1/holdout_keys.json")
    model_raw = read_json("zoned-heuristic-v1/holdout_labels.json")["labels"]
    human_file = read_json("human-pass/human_labels.json")
    if len(selected) != 84 or len(set(selected)) != 84 or len(model_raw) != 84:
        raise ValueError("Expected 84 unique held-out trials and model labels")
    human_items = human_file["items"]
    if [x["key"] for x in human_items] != selected or [x["index"] for x in human_items] != list(range(84)):
        raise ValueError("Human labels do not align with the held-out key order")
    rows = dataset.rows
    indexed = {r["key"]: r for r in rows}
    model_labels, human_labels = {}, {}
    for key, model_code, human_item in zip(selected, model_raw, human_items, strict=True):
        d, r, m = model_code.split(",")
        model_labels[key] = label_values(d, r, m)
        if human_item["claude_reader"] != {"description": d, "nonrecognition": r, "mark": m}:
            raise ValueError(f"Duplicated model-reader label changed: {key}")
        h = human_item["human"]
        human_labels[key] = label_values(h["description"], h["nonrecognition"], h["mark"])
    weights, strata = sampling_weights(rows, selected)

    three = {"pairwise": {}, "rates": {}, "holdout": {"n": 84, "strata": strata, "scores": {}},
             "framing": {}, "models": {}, "contrasts": {}}
    fresh = [r for r in rows if r["batch"] == "fresh"]
    real_type = [r for r in fresh if r["framing"] in {"real", "type_of"}]
    human_scores = {}
    for name, outcome in OUTCOMES.items():
        three["pairwise"][name] = {
            f"{a}_{b}": agreement([r[a][outcome] for r in rows], [r[b][outcome] for r in rows])
            for a, b in (("A", "B"), ("A", "C"), ("B", "C"))
        }
        three["rates"][name] = {arm: _mean(r[arm][outcome] for r in rows) for arm in "ABC"}
        three["holdout"]["scores"][name] = {}
        human_scores[name] = {}
        for arm in "ABC":
            values = {key: indexed[key][arm][outcome] for key in selected}
            three["holdout"]["scores"][name][arm] = score_against_labels(
                selected, values, {k: model_labels[k][name] for k in selected}, weights, historical_names=True)
            human_scores[name][arm] = score_against_labels(
                selected, values, {k: human_labels[k][name] for k in selected}, weights, historical_names=False)
        three["framing"][name] = {
            frame: [_mean(r[arm][outcome] for r in fresh if r["framing"] == frame) for arm in "ABC"]
            for frame in ("neutral", "real", "type_of", "imaginary")
        }
        three["models"][name] = {
            model: [_mean(r[arm][outcome] for r in real_type if r["model"] == model) for arm in "ABC"]
            for model in MODELS
        }
        fr = three["framing"][name]
        three["contrasts"][name] = {
            "imaginary-real": [x - y for x, y in zip(fr["imaginary"], fr["real"], strict=True)],
            "type_of-real": [x - y for x, y in zip(fr["type_of"], fr["real"], strict=True)],
            "Anthropic-OpenAI": [
                _mean(r[arm][outcome] for r in real_type if r["provider"] == "Anthropic") -
                _mean(r[arm][outcome] for r in real_type if r["provider"] == "OpenAI") for arm in "ABC"
            ],
        }
    echo_values = {key: indexed[key]["zoned"]["U_unmarked_discounting_prompt_echo"] for key in selected}
    three["holdout"]["scores"]["unmarked_echo"] = {"C": score_against_labels(
        selected, echo_values, {k: model_labels[k]["unmarked_echo"] for k in selected}, weights, historical_names=True)}
    human_scores["unmarked_echo"] = {"C": score_against_labels(
        selected, echo_values, {k: human_labels[k]["unmarked_echo"] for k in selected}, weights, historical_names=False)}
    three["holdout"]["scores"]["nonrecognition_personal_only"] = {"A": score_against_labels(
        selected, {k: dataset.A[k]["values"]["knowledge_limit"] for k in selected},
        {k: model_labels[k]["nonrecognition"] for k in selected}, weights, historical_names=True)}
    three["C_vs_B_class"] = dict(Counter(
        f"{dataset.C[r['key']]['response_type']}|{dataset.B[r['key']]['response_class']}" for r in rows))
    three["triples"] = dict(Counter(str((r["A"]["E"], r["B"]["E"], r["C"]["E"]))
                                    for r in rows if r["A"]["E"] is not None))
    three["C_types_by_model"] = {
        model: dict(Counter(r["zoned"]["response_type"] for r in real_type if r["model"] == model))
        for model in MODELS
    }
    human_result = {"scores": human_scores, "strata": strata}
    reader_agreement = {
        name: agreement([human_labels[k][name] for k in selected], [model_labels[k][name] for k in selected])
        for name in (*OUTCOMES, "unmarked_echo")
    }
    for entry in reader_agreement.values():
        entry["correct"] = round(entry["agree"] * entry["n"])
    both_described = [item for item in human_items if item["human"]["description"] in {"Y", "H"}
                      and item["claude_reader"]["description"] in {"Y", "H"}]
    marking_agreement = {
        "n": len(both_described),
        "correct": sum(i["human"]["mark"] == i["claude_reader"]["mark"] for i in both_described),
        "definition": "Exact Y/E/N mark agreement among trials both readers called descriptions",
    }
    expected_three = read_json("zoned-heuristic-v1/comparison/three_way.json")
    three_diagnostic = compare_nested(expected_three, three)
    human_diagnostic = compare_nested(human_file["scores_against_human"], human_result)
    return {
        "schema": "bestiary2-reproduced-comparisons/1",
        "purpose": "Reproduction of published response-weighted comparisons; no new declared bootstrap estimates",
        "provenance": {**dataset.provenance, "comparison_files": source_hashes},
        "verification": {"absolute_tolerance": 1e-12, "relative_tolerance": 1e-12,
                         "three_way": three_diagnostic, "human_pass": human_diagnostic,
                         "all_matched": three_diagnostic["matched"] and human_diagnostic["matched"]},
        "three_way": three,
        "human_pass": human_result,
        "reader_agreement": reader_agreement,
        "marking_agreement": marking_agreement,
        "holdout_sampling": {"n": len(selected), "population_n": sum(r["A"]["E"] is not None for r in rows),
                             "excluded_unresolved_A_description": sum(r["A"]["E"] is None for r in rows),
                             "strata": strata},
    }


def compare_nested(expected, observed, *, abs_tol=1e-12, rel_tol=1e-12) -> dict:
    """Compare every leaf, key, list length and ordering in a released output."""
    differences = []
    leaves = 0
    max_abs_error = 0.0

    def walk(a, b, path):
        nonlocal leaves, max_abs_error
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a) != set(b):
                differences.append({"path": path, "missing_keys": sorted(set(a) - set(b)),
                                    "extra_keys": sorted(set(b) - set(a))})
            for key in sorted(set(a) & set(b)):
                walk(a[key], b[key], f"{path}.{key}")
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                differences.append({"path": path, "expected_length": len(a), "observed_length": len(b)})
            for index, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{index}]")
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            leaves += 1
            max_abs_error = max(max_abs_error, abs(a - b))
            # Integer counts must match exactly; tolerance is only for computed fractions.
            equal = a == b if isinstance(a, int) and isinstance(b, int) else math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not equal:
                differences.append({"path": path, "expected": a, "observed": b})
        else:
            leaves += 1
            if a != b:
                differences.append({"path": path, "expected": a, "observed": b})

    walk(expected, observed, "$")
    return {"matched": not differences, "compared_leaves": leaves,
            "maximum_absolute_numeric_difference": max_abs_error, "differences": differences}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[3]
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "results/reproduction.json")
    args = parser.parse_args()
    result = reproduce(load_inputs(args.repo_root), args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["verification"], indent=2))
    if not result["verification"]["all_matched"]:
        raise SystemExit("Published comparisons were not reproduced; inspect the diagnostics")


if __name__ == "__main__":
    main()
