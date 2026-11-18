#!/usr/bin/env python3
"""The one-time rerun of the declared list with C = zoned heuristic 1.1.0.

Declared in ../FINAL_INSTRUMENT.md. Uses the merged estimators unchanged:
`load_inputs` builds the v1.0 rows; this script swaps in the verified 1.1 codes
for C, evaluates all 225 declared rows on both row sets with the same seed and
word draws, and reports C 1.1 beside C 1.0 with draw-by-draw paired differences.

    python rerun_v1_1.py [--out results]
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
ROOT = PARENT.parents[2]
sys.path.insert(0, str(PARENT))
from inputs import load_inputs, C_BINARY, _binary, _require  # noqa: E402
from estimation import Estimator, interpretation  # noqa: E402
from contrasts import build_contrasts  # noqa: E402
from questions import build_questions  # noqa: E402

V11_CODES = "supplement/coding-heuristics/zoned-heuristic-v1-1/results/response_codes.csv"
V11_RECEIPT = "supplement/coding-heuristics/zoned-heuristic-v1-1/results/execution.json"
V11_SHA = "ea071089abc9467e721d0e2d3cea25b25e646263ce3eed6ed737737bbc4dd237"
V11_VERSION = "bestiary2-zoned-heuristic/1.1.0"
V11_FREEZE = "3d8b4c35961fbdfb6ca88084dab3c63b9d4df03b"
MERGED = PARENT / "results/estimates.json"
OUTPUTS = ("estimates_c_v1_1.json", "c_v1_1_minus_v1_0.json", "interpretation_c_v1_1.json", "tables_v1_1.md")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def load_v11(root, rows):
    blob = (root / V11_CODES).read_bytes()
    _require(sha(blob) == V11_SHA, "Zoned 1.1 codes differ from the hash in FINAL_INSTRUMENT.md")
    receipt = json.loads((root / V11_RECEIPT).read_text(encoding="utf-8"))
    _require(receipt["version"] == V11_VERSION and receipt["freeze_commit"] == V11_FREEZE
             and receipt["n"] == 16000 and receipt["outputs"]["response_codes.csv"] == V11_SHA,
             "Zoned 1.1 codes do not match their execution receipt")
    codes = {}
    for r in csv.DictReader(io.StringIO(blob.decode("utf-8"))):
        _require(r["key"] not in codes, f"Duplicate 1.1 key: {r['key']}")
        codes[r["key"]] = r
    _require(set(codes) == {r["key"] for r in rows}, "1.1 keys differ from the declared rows")
    new_rows = []
    for row in rows:
        c = codes[row["key"]]
        old = row["zoned"]
        for field in ("batch", "model", "word", "condition", "source", "framing", "response_sha256"):
            _require(c[field] == old[field], f"1.1 metadata differs from 1.0 ({field}): {row['key']}")
        _require(int(c["rep"]) == row["rep"], f"1.1 repetition differs: {row['key']}")
        zoned = dict(c)
        for field in C_BINARY:
            zoned[field] = _binary(c[field], f"C11.{field}:{row['key']}")
        zoned["rep"] = row["rep"]
        new = copy.copy(row)
        new["zoned"] = zoned
        new["C"] = {out: zoned[field] for out, field in
                    {"E": "E_description", "N": "N_nonrecognition_without_description",
                     "U": "U_unmarked_description", "R": "nonrec_any"}.items()}
        new_rows.append(new)
    return new_rows


def uses_only_c(spec):
    return "comparison" not in spec and all(t["selection"]["arm"] == "C" for t in spec["terms"])


def uses_c(spec):
    return any(t["selection"]["arm"] == "C" for t in spec["terms"])


def paired(diff_samples, point, draws):
    finite = diff_samples[np.isfinite(diff_samples)]
    ci = [float(v) for v in np.quantile(finite, [.025, .975], method="linear")] if point is not None and len(finite) else None
    return {"estimate": point, "ci95": ci, "bootstrap_defined": int(len(finite)),
            "bootstrap_undefined": int(draws - len(finite)),
            "excludes_zero": bool(ci and (ci[0] > 0 or ci[1] < 0))}


def fmt(estimate, ci, flag=False):
    if estimate is None:
        return "not estimable"
    d = lambda v: f"{round(100 * v, 10) + 0.0:.2f}"
    return f"{d(estimate)} [no interval]" if ci is None else f"{d(estimate)} [{d(ci[0])}, {d(ci[1])}]" + ("*" if flag else "")


def run(out: Path, draws=10000, seed=20261115):
    started = time.monotonic()
    _require(not any((out / n).exists() for n in OUTPUTS), "Outputs exist; this rerun is declared to happen once.")
    dataset = load_inputs(ROOT)
    rows10 = dataset.rows
    rows11 = load_v11(ROOT, rows10)
    specs = build_contrasts() + build_questions()
    _require(len(specs) == 225, "Expected the 225 declared rows")
    e10, e11 = Estimator(rows10, draws=draws, seed=seed), Estimator(rows11, draws=draws, seed=seed)
    m10, m11 = e10.bootstrap_metadata(), e11.bootstrap_metadata()
    _require(m10["shared_draws_sha256"] == m11["shared_draws_sha256"], "Word draws differ between runs")

    merged = {r["id"]: r for r in json.loads(MERGED.read_text(encoding="utf-8"))}
    r10, r11, s10, s11 = {}, {}, {}, {}
    for spec in specs:
        r10[spec["id"]], s10[spec["id"]] = e10.evaluate(spec)
        r11[spec["id"]], s11[spec["id"]] = e11.evaluate(spec)
    # Gate 1: the 1.0 run reproduces every merged estimate and interval exactly.
    for i, r in r10.items():
        _require(r["estimate"] == merged[i]["estimate"] and r["ci95"] == merged[i]["ci95"]
                 and r["bootstrap_undefined"] == merged[i]["bootstrap_undefined"],
                 f"1.0 run does not reproduce the merged result for {i}")
    # Gate 2: rows that never touch C are identical in both runs.
    for spec in specs:
        if not uses_c(spec):
            _require(np.array_equal(s10[spec["id"]], s11[spec["id"]], equal_nan=True)
                     and r10[spec["id"]]["estimate"] == r11[spec["id"]]["estimate"],
                     f"A/B-only row changed between runs: {spec['id']}")

    diffs = {}
    for spec in specs:
        if uses_only_c(spec):
            i = spec["id"]
            a, b = r11[i]["estimate"], r10[i]["estimate"]
            point = None if a is None or b is None else a - b
            diffs[i] = {"id": i, "label": spec.get("label"), "block": spec["block"], "tier": spec.get("tier"),
                        "c_v1_0": {k: r10[i][k] for k in ("estimate", "ci95", "bootstrap_undefined")},
                        "c_v1_1": {k: r11[i][k] for k in ("estimate", "ci95", "bootstrap_undefined")},
                        "c_v1_1_minus_v1_0": paired(s11[i] - s10[i], point, draws)}

    old_interp = json.loads((PARENT / "results/interpretation.json").read_text(encoding="utf-8"))
    interp = {}
    for spec in specs:
        if spec["block"] != 1 or spec.get("arm") != "A":
            continue
        key = f"{spec['shape']}.{spec['outcome']}"
        arms = [r11[f"{key}.{x}"] for x in "ABC"]
        pairs = [r11[f"{key}.{x}-{y}"] for x, y in (("A", "B"), ("A", "C"), ("B", "C"))]
        interp[key] = {"c_v1_1": interpretation(arms, pairs), "c_v1_0": old_interp[key]}
        for x, y in (("A", "B"), ("A", "C"), ("B", "C")):
            np.testing.assert_allclose(s11[f"{key}.{x}-{y}"], s11[f"{key}.{x}"] - s11[f"{key}.{y}"],
                                       rtol=0, atol=2e-15, equal_nan=True)

    out.mkdir(parents=True, exist_ok=True)
    dump(out / "estimates_c_v1_1.json", [r11[s["id"]] for s in specs])
    dump(out / "c_v1_1_minus_v1_0.json", list(diffs.values()))
    dump(out / "interpretation_c_v1_1.json", interp)
    write_tables(out / "tables_v1_1.md", specs, r10, r11, diffs, interp)
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    dump(out / "execution.json", {
        "schema": "bestiary2-declared-exploratory-rerun-v1-1/1",
        "declaration": "FINAL_INSTRUMENT.md", "declaration_sha256": sha((PARENT / "FINAL_INSTRUMENT.md").read_bytes()),
        "completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": round(time.monotonic() - started, 3),
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "git_head": head, "worktree_has_changes": dirty,
        "c_v1_1_codes": {"path": V11_CODES, "sha256": V11_SHA, "version": V11_VERSION, "freeze_commit": V11_FREEZE},
        "bootstrap": m11, "shared_draws_sha256_equal": True,
        "gates": {"v1_0_run_reproduces_merged_estimates_and_intervals": True,
                  "rows_without_C_identical_across_runs": True,
                  "paired_instrument_differences_match_native_estimators": True},
        "rows": len(specs), "c_only_rows_compared": len(diffs), "provider_calls": 0, "response_text_read": False,
        "source_files": {p.name: sha(p.read_bytes()) for p in sorted(PARENT.glob("*.py"))} | {HERE.name + "/" + Path(__file__).name: sha(Path(__file__).read_bytes())},
        "output_files": {n: sha((out / n).read_bytes()) for n in OUTPUTS},
    })
    print(json.dumps({"rows": len(specs), "c_only_rows": len(diffs), "seconds": round(time.monotonic() - started, 1), "out": str(out)}))


def write_tables(path, specs, r10, r11, diffs, interp):
    L = ["# Declared exploratory estimates: C = zoned 1.1 beside C = zoned 1.0", "",
         "Rerun declared in `../FINAL_INSTRUMENT.md`. A and B are unchanged. Percentages and percentage points; brackets are unadjusted 95% word-bootstrap intervals with the same 10,000 word draws in both runs. `*` marks intervals conditional on defined draws. No p-values.", "",
         "## Block 1", "",
         "| Shape/outcome | A | B | C 1.0 | C 1.1 | C 1.1 minus C 1.0 | Direction (C 1.0) | Direction (C 1.1) |",
         "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
    for key, it in interp.items():
        c = diffs[f"{key}.C"]
        L.append("| " + " | ".join([key, fmt(r11[f"{key}.A"]["estimate"], r11[f"{key}.A"]["ci95"]),
                                     fmt(r11[f"{key}.B"]["estimate"], r11[f"{key}.B"]["ci95"]),
                                     fmt(c["c_v1_0"]["estimate"], c["c_v1_0"]["ci95"]),
                                     fmt(c["c_v1_1"]["estimate"], c["c_v1_1"]["ci95"]),
                                     fmt(c["c_v1_1_minus_v1_0"]["estimate"], c["c_v1_1_minus_v1_0"]["ci95"]),
                                     it["c_v1_0"]["direction"], it["c_v1_1"]["direction"]]) + " |")
    L += ["", "### Paired instrument differences with C = 1.1", "", "| Shape/outcome | A minus B | A minus C 1.1 | B minus C 1.1 |", "| --- | ---: | ---: | ---: |"]
    for key in interp:
        L.append("| " + " | ".join([key] + [fmt(r11[f"{key}.{p}"]["estimate"], r11[f"{key}.{p}"]["ci95"]) for p in ("A-B", "A-C", "B-C")]) + " |")
    for q in range(1, 9):
        rows = [d for d in diffs.values() if d["block"] == 2 and r11[d["id"]]["metadata"]["question"] == q]
        if not rows:
            continue
        L += ["", f"## Question {q} (zoned rows)", "", "| ID | C 1.0 | C 1.1 | C 1.1 minus C 1.0 |", "| --- | ---: | ---: | ---: |"]
        for d in rows:
            L.append(f"| `{d['id']}` | {fmt(d['c_v1_0']['estimate'], d['c_v1_0']['ci95'], d['c_v1_0']['bootstrap_undefined'] > 0)} | "
                     f"{fmt(d['c_v1_1']['estimate'], d['c_v1_1']['ci95'], d['c_v1_1']['bootstrap_undefined'] > 0)} | "
                     f"{fmt(d['c_v1_1_minus_v1_0']['estimate'], d['c_v1_1_minus_v1_0']['ci95'], d['c_v1_1_minus_v1_0']['bootstrap_undefined'] > 0)} |")
    L += ["", "Rows of Questions 6 and 7 computed under A or B are unchanged and appear in the merged tables. Intervals reflect word resampling with fixed endpoints; they exclude detector error.", ""]
    path.write_text("\n".join(L), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=HERE / "results")
    a = p.parse_args()
    run(a.out.resolve())
