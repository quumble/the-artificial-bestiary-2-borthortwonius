#!/usr/bin/env python3
"""Code responses with the published Artificial Bestiary 2 scorers.

Example:
  python code_responses.py --repo /path/to/bestiary2 --input /path/to/bestiary2/analysis/response-features.jsonl --out /path/to/coded
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys

from coding_heuristic import (CLASSES, GPT_PRIMARY, VERSION, code_one,
                             load_upstream, normalized_codebook, sha256_file)


def as_bool(value, label):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.strip().lower() in ("true", "1", "yes"):
            return True
        if value.strip().lower() in ("false", "0", "no"):
            return False
    raise ValueError(f"Invalid boolean value {value!r} in {label}")


def read_rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for n, row in enumerate(csv.DictReader(f), 2):
                for key in ("terminal", "complete", "truncated", "refusal", "issue", "protocol_violation", "valid"):
                    if key in row:
                        row[key] = as_bool(row[key], f"{path.name}:{n}.{key}")
                yield n, row
    elif path.suffix.lower() in (".jsonl", ".ndjson"):
        with path.open("r", encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Malformed JSONL row {path}:{n}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"Expected object at {path}:{n}")
                yield n, row
    else:
        raise ValueError("Input must be a .jsonl, .ndjson, or .csv with raw response text")


def _mean(numer, denom):
    return round(numer / denom, 8) if denom else ""


def summaries(rows, *, cell=False):
    """Descriptive rates only. Never use response-level N for inferential sample size."""
    groups = defaultdict(list)
    for r in rows:
        key = (r["batch"], r["model"], r["condition"])
        if cell:
            key = key[:2] + (r["word"],) + key[2:]
        groups[key].append(r)
    columns = ["batch", "model"] + (["word"] if cell else []) + ["condition", "n_records", "n_gpt_usable", "n_fable_eligible"]
    for fam in GPT_PRIMARY:
        columns.extend([fam + "_hits", fam + "_rate"])
    for f in ("F_E", "F_U", "F_N"):
        columns.extend([f + "_hits", f + "_rate"])
    for class_name in CLASSES:
        columns.extend([class_name + "_n", class_name + "_share_eligible"])
    columns.extend(["X_UNUSABLE_n", "n_fable_eligibility_unknown", "n_truncated"])
    result = []
    for key, items in sorted(groups.items()):
        a = dict(zip(columns[:len(key)], key))
        g = [r for r in items if r["gpt_primary_eligible"] == 1]
        f = [r for r in items if r["fable_primary_eligible"] == 1]
        a.update(n_records=len(items), n_gpt_usable=len(g), n_fable_eligible=len(f))
        for fam in GPT_PRIMARY:
            hits = sum(r[fam] for r in g)
            a.update({fam + "_hits": hits, fam + "_rate": _mean(hits, len(g))})
        for fam in ("F_E", "F_U", "F_N"):
            hits = sum(r[fam] for r in f)
            a.update({fam + "_hits": hits, fam + "_rate": _mean(hits, len(f))})
        for class_name in CLASSES:
            hits = sum(r["response_class"] == class_name for r in f)
            a.update({class_name + "_n": hits, class_name + "_share_eligible": _mean(hits, len(f))})
        a["X_UNUSABLE_n"] = sum(r["usable"] == 0 for r in items)
        a["n_fable_eligibility_unknown"] = sum(r["fable_primary_eligible"] == "" for r in items)
        a["n_truncated"] = sum(r["truncated"] == 1 for r in items)
        result.append(a)
    return columns, result


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run(input_path: Path, repo: Path, outdir: Path, *, verify_embedded=False, redact=False):
    input_path = input_path.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input not found: {input_path}")
    if input_path.name == "attempts.jsonl":
        raise ValueError("Do not use the raw attempt ledger: first run the original audited analyzer; input analysis/response-features.jsonl")
    outdir = outdir.resolve()
    if input_path == outdir or outdir in input_path.parents:
        raise ValueError("Output directory must not contain the input file")
    gpt, fable, provenance = load_upstream(repo)
    output_rows, evidence_rows = [], []
    seen_keys = set()
    for index, row in read_rows(input_path):
        # Each released row is a planned slot, not an independent word.
        trial = (row.get("batch"), row.get("model_requested") or row.get("model"), row.get("word"), row.get("condition"), str(row.get("rep", "")))
        if all(x not in ("", None) for x in trial):
            if trial in seen_keys:
                raise ValueError(f"Repeated batch/model/word/condition/rep slot at row {index}: {trial}")
            seen_keys.add(trial)
        try:
            coded, evidence = code_one(row, gpt, fable, index=index,
                                       verify_embedded=verify_embedded, redact=redact)
        except Exception as exc:
            raise ValueError(f"Coding failed on input line/row {index}: {exc}") from exc
        output_rows.append(coded)
        evidence_rows.append(evidence)
    if not output_rows:
        raise ValueError("No response records found")
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "coded_responses.csv", output_rows, list(output_rows[0].keys()))
    for filename, is_cell in (("descriptive_by_model_condition.csv", False),
                              ("descriptive_by_word_cell.csv", True)):
        columns, data = summaries(output_rows, cell=is_cell)
        write_csv(outdir / filename, data, columns)
    with (outdir / "match_evidence.jsonl").open("w", encoding="utf-8") as f:
        for item in evidence_rows:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    audit = {
        "coding_version": VERSION,
        "purpose": "Post-publication descriptive coding; not a preregistered confirmatory analysis or new significance test",
        "input_sha256": sha256_file(input_path),
        "input_file_name": input_path.name,
        "n_input_rows": len(output_rows),
        "n_usable": sum(r["usable"] for r in output_rows),
        "n_fable_primary_eligible": sum(r["fable_primary_eligible"] == 1 for r in output_rows),
        "n_fable_eligibility_unknown": sum(r["fable_primary_eligible"] == "" for r in output_rows),
        "n_truncated": sum(r["truncated"] == 1 for r in output_rows),
        "counts_by_response_class_all_usable": dict(Counter(r["response_class"] for r in output_rows if r["usable"])),
        "embedded_gpt_scoring": sum(r["gpt_scorer_origin"] == "published_embedded" for r in output_rows),
        "rescore_verified": verify_embedded,
        "evidence_snippets_redacted": redact,
        "codebook": normalized_codebook(),
        "upstream_provenance": provenance,
        "coding_tool_sha256": {
            "coding_heuristic.py": sha256_file(Path(__file__).with_name("coding_heuristic.py")),
            "code_responses.py": sha256_file(Path(__file__)),
        },
    }
    (outdir / "coding_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, type=Path, help="Checked-out Bestiary 2 repository or frozen source snapshot")
    ap.add_argument("--input", required=True, type=Path, help="Selected response-features.jsonl (preferred), or raw-text JSONL/CSV")
    ap.add_argument("--out", required=True, type=Path, help="New output directory")
    ap.add_argument("--verify-embedded", action="store_true", help="Recompute GPT scores and assert exact registered flags and match spans")
    ap.add_argument("--redact-evidence", action="store_true", help="Retain matched spans/entries but not matched-text excerpts")
    args = ap.parse_args(argv)
    try:
        audit = run(args.input, args.repo, args.out,
                    verify_embedded=args.verify_embedded, redact=args.redact_evidence)
    except (ValueError, OSError, ImportError) as exc:
        ap.exit(2, f"ERROR: {exc}\n")
    print(f"Coded {audit['n_input_rows']} rows ({audit['n_usable']} usable); outputs in {args.out}")
    if audit["n_fable_eligibility_unknown"]:
        print(f"WARNING: {audit['n_fable_eligibility_unknown']} rows have unknown truncation status and are excluded from Fable registered-eligibility summaries", file=sys.stderr)


if __name__ == "__main__":
    main()
