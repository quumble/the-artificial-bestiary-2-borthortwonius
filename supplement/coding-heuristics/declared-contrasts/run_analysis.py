#!/usr/bin/env python3
"""Compute every declared exploratory row from the published frozen codes.

Run from any directory. No provider keys, response text, model calls, private
intermediates or extraction are required. Frozen files are never changed.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

from inputs import load_inputs
from estimation import Estimator, interpretation
from contrasts import build_contrasts
from questions import build_questions

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[2]
OUTPUT_NAMES = ("specifications.json", "estimates.json", "estimates.csv", "interpretation.json", "tables.md", "execution.json")


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def format_estimate(result):
    if result["estimate"] is None:
        return "not estimable"
    # Remove arithmetic noise below displayed precision, including -0.00.
    display = lambda value: f"{round(100 * value, 10) + 0.0:.2f}"
    point = display(result["estimate"])
    ci = result["ci95"]
    if ci is None:
        return f"{point} [no interval]"
    suffix = "*" if result["bootstrap_undefined"] else ""
    return f"{point} [{display(ci[0])}, {display(ci[1])}]{suffix}"


def write_tables(path, results, interpretations):
    by_id = {r["id"]: r for r in results}
    lines = ["# Complete declared exploratory estimates", "",
        "Post hoc exploratory estimates from the frozen instruments. Rates are percentages; differences are percentage points. Brackets are unadjusted 95% word-bootstrap intervals. No p-values or familywise claims. Asterisks denote intervals conditional on defined bootstrap draws; exact counts and all support information are in `estimates.json`.", "",
        "## Block 1", "", "A = GPT context; B = registered Fable outcomes exported by the mechanical arm; C = zoned. H1 is the G1/E alias, not another estimate.", "",
        "| Shape/outcome | A | B | C | Direction |", "| --- | ---: | ---: | ---: | --- |"]
    for key, inter in interpretations.items():
        lines.append("| " + " | ".join([key] + [format_estimate(by_id[f"{key}.{arm}"]) for arm in "ABC"] + [inter["direction"]]) + " |")
    lines += ["", "### Paired instrument differences", "", "Each arm retains its own available-case estimator. Intervals use the same sampled words across arms. Differences involving A may reflect both coding and unresolved-value support.", "",
              "| Shape/outcome | A minus B | A minus C | B minus C |", "| --- | ---: | ---: | ---: |"]
    for key in interpretations:
        lines.append("| " + " | ".join([key] + [format_estimate(by_id[f"{key}.{pair}"]) for pair in ("A-B", "A-C", "B-C")]) + " |")
    for question in range(1, 9):
        rows = [r for r in results if r["block"] == 2 and r["metadata"]["question"] == question]
        lines += ["", f"## Question {question}", "", f"Tier: {rows[0]['tier']}.", "",
                  "| ID | Estimate and interval | Undefined draws |", "| --- | ---: | ---: |"]
        for r in rows:
            lines.append(f"| `{r['id']}` | {format_estimate(r)} | {r['bootstrap_undefined']} |")
    lines += ["", "Intervals reflect word resampling in the selected strata with fixed endpoints and frozen detectors. They do not account for detector error or establish equivalence when an interval contains zero.", ""]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run(root, out, draws=10000, seed=20261115, overwrite=False):
    started = time.monotonic()
    if not overwrite and any((out / n).exists() for n in OUTPUT_NAMES):
        raise FileExistsError("Analysis outputs already exist; choose a new --out directory or explicitly use --overwrite.")
    dataset = load_inputs(root)
    specifications = build_contrasts() + build_questions()
    if len(specifications) != 225 or len({s["id"] for s in specifications}) != 225:
        raise ValueError("Expected exactly 66 Block 1 and 159 Block 2 unique rows")
    engine = Estimator(dataset.rows, draws=draws, seed=seed)
    results = []
    bootstrap_results = {}
    for n, specification in enumerate(specifications, 1):
        result, samples = engine.evaluate(specification)
        results.append(result)
        bootstrap_results[result["id"]] = samples
        if n % 50 == 0:
            print(f"Estimated {n}/{len(specifications)} rows", flush=True)
    by_id = {r["id"]: r for r in results}
    interpretations = {}
    for s in specifications:
        if s["block"] != 1 or s.get("arm") != "A":
            continue
        key = f"{s['shape']}.{s['outcome']}"
        arms = [by_id[f"{key}.{a}"] for a in "ABC"]
        pairs = [by_id[f"{key}.{a}-{b}"] for a, b in (("A", "B"), ("A", "C"), ("B", "C"))]
        interpretations[key] = interpretation(arms, pairs)
        # Audit that pairwise output is the difference of native estimators
        # on identical draws, not a newly imposed common-case analysis.
        for a, b in (("A", "B"), ("A", "C"), ("B", "C")):
            np.testing.assert_allclose(bootstrap_results[f"{key}.{a}-{b}"],
                bootstrap_results[f"{key}.{a}"] - bootstrap_results[f"{key}.{b}"],
                rtol=0, atol=2e-15, equal_nan=True)
    shares = [by_id[f"Q3.description_share.{c}"]["estimate"] for c in ("bare", "hedged", "framed", "disclaimed")]
    if any(v is None for v in shares) or not np.isclose(sum(shares), 1):
        raise ValueError("The four description shares must partition E")
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "specifications.json", specifications)
    dump(out / "estimates.json", results)
    dump(out / "interpretation.json", interpretations)
    with (out / "estimates.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "block", "tier", "label", "estimate", "ci95_low", "ci95_high", "bootstrap_defined", "bootstrap_undefined", "interval_status", "units"], lineterminator="\n")
        writer.writeheader()
        for result in results:
            ci = result["ci95"] or [None, None]
            writer.writerow({**{k: result[k] for k in ("id", "block", "tier", "label", "estimate", "bootstrap_defined", "bootstrap_undefined", "interval_status", "units")},
                             "ci95_low": ci[0], "ci95_high": ci[1]})
    write_tables(out / "tables.md", results, interpretations)
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    receipt = {
        "schema": "bestiary2-declared-exploratory/1",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
        "git_head": head, "worktree_has_changes": dirty,
        "source_identity_note": "Source file hashes identify the implementation, including any code not yet committed at execution.",
        "source_files": {p.name: digest(p) for p in sorted(DIRECTORY.glob("*.py"))},
        "declaration_sha256": digest(DIRECTORY / "DECLARATION.md"),
        "bootstrap": engine.bootstrap_metadata(), "inputs": dataset.provenance,
        "rows_reported": len(results), "block1_rows": 66, "block2_rows": 159,
        "H1_alias": "G1.E", "provider_calls": 0, "response_text_read": False,
        "frozen_instruments_changed": False,
        "verification": {"paired_differences_match_native_estimators": True, "description_shares_sum_to_one": True},
        "undefined_intervals": [r["id"] for r in results if r["ci95"] is None],
        "conditional_intervals": {r["id"]: r["bootstrap_undefined"] for r in results if r["bootstrap_undefined"]},
        "output_files": {name: digest(out / name) for name in OUTPUT_NAMES if name != "execution.json"},
    }
    dump(out / "execution.json", receipt)
    print(json.dumps({"rows": len(results), "draws": draws, "undefined_intervals": receipt["undefined_intervals"],
                      "conditional_intervals": receipt["conditional_intervals"], "out": str(out)}), flush=True)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=DIRECTORY / "results")
    parser.add_argument("--draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261115)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    run(args.root.resolve(), args.out.resolve(), args.draws, args.seed, args.overwrite)
