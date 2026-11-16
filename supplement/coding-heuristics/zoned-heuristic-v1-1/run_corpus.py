"""Replay the separately frozen candidate on the original successful responses.

Offline; standard library only. Never overwrites an output directory. Full texts
are read only after freeze verification and are not printed or copied to outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import zipfile

from zoned_heuristic import VERSION, score

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RAW_SHA = "f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6"
# Byte-identical to the codes inside the original published zoned v1 archive.
BASELINE_SHA = "84afb45c6b50563486b668dd148d7fc9798da571c1acfc9ccae9b4d7b002afb2"
CHANGED_FIELDS = (
    "E_description", "nonrec_any", "N_nonrecognition_without_description",
    "U_unmarked_description", "substitute_description", "response_type",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def verify_freeze(commit, root=ROOT, repo=REPO):
    """Require a concrete published commit and unchanged frozen file bytes."""
    require(bool(re.fullmatch(r"[0-9a-f]{40}", commit)), "Use the full freeze commit SHA")
    manifest = root / "FREEZE.sha256"
    relative = manifest.relative_to(repo).as_posix()
    published = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=repo)
    require(manifest.read_bytes() == published, "Freeze manifest differs from commit")
    seen = set()
    for line in published.decode("utf-8").splitlines():
        expected, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        require(name not in seen, "Duplicate freeze entry")
        seen.add(name)
        path = (root / name).resolve()
        require(path.is_relative_to(root.resolve()), "Freeze path escapes candidate directory")
        require(sha(path.read_bytes()) == expected, f"Frozen file changed: {name}")
        committed = subprocess.check_output(
            ["git", "show", f"{commit}:{path.relative_to(repo).as_posix()}"], cwd=repo)
        require(sha(committed) == expected, f"Committed file differs: {name}")
    require({"PLAN.md", "zoned_heuristic.py", "run_corpus.py", "test_zoned.py",
             "METHOD.md", "audit.py"} <= seen, "Incomplete freeze")
    return sha(published)


def load_raw(path):
    """Same release/eligibility checks as the context arm's frozen reader."""
    require(sha(path.read_bytes()) == RAW_SHA, "Raw archive checksum mismatch")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate archive member")
        for line in archive.read("SHA256SUMS.txt").decode().splitlines():
            if not line.strip():
                continue
            expected, name = line.split(maxsplit=1)
            name = name.strip().replace("\\", "/")
            require(sha(archive.read(name)) == expected, f"Release member checksum: {name}")
        freeze = json.loads(archive.read("data/freeze.json"))
        claimed = freeze.pop("manifest_sha256")
        require(sha(canonical(freeze).encode()) == claimed, "Collection manifest mismatch")
        planned = {(bank, model, trial["trial_id"]): trial
                   for bank, models in freeze["batches"].items()
                   for model, trials in models.items() for trial in trials}
        rows = []
        for name in sorted(names):
            if name.startswith(("data/raw/fresh/", "data/raw/known/")) and name.endswith(".jsonl"):
                rows.extend(json.loads(line) for line in archive.read(name).decode().splitlines()
                            if line.strip())
    keys = [(r["batch"], r["model_requested"], r["trial_id"]) for r in rows]
    require(len(keys) == len(set(keys)) == 16000, "Response count or duplicate key")
    require(set(keys) == set(planned), "Schedule and exports differ")
    for key, row in zip(keys, rows):
        require(all(row[name] == value for name, value in planned[key].items()),
                "Schedule metadata mismatch")
        require(row["valid"] and row["terminal"] and row["complete"] and not row["truncated"],
                "Ineligible response")
        require(not any(row.get(name) for name in
                        ("error", "issue", "protocol_violation", "reasoning_tokens", "thinking_blocks")),
                "Unexpected response issue")
        require(isinstance(row["response"], str) and row["response"].strip(), "Empty response")
    require(Counter(r["batch"] for r in rows) == {"fresh": 9600, "known": 6400}, "Bank counts")
    return sorted(rows, key=lambda r: (r["batch"], r["model_requested"], r["trial_id"])), claimed


def read_codes(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    keyed = {row["key"]: row for row in rows}
    require(len(keyed) == len(rows), "Duplicate code keys")
    return keyed


def write_csv(path, rows):
    require(bool(rows), "Cannot write an empty code table")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(archive, out, freeze_commit, repo=REPO):
    freeze_sha = verify_freeze(freeze_commit, ROOT, repo)
    require(not out.exists(), "Output directory exists; preserve the previous execution")
    records, collection_sha = load_raw(archive)
    old_path = repo / "supplement/coding-heuristics/zoned-heuristic-v1/results/response_codes.csv"
    require(sha(old_path.read_bytes()) == BASELINE_SHA, "Original code checksum mismatch")
    old = read_codes(old_path)
    require(len(old) == 16000, "Original code count differs")
    rows, changes = [], []
    field_changes = Counter()
    outcome_movements = {field: Counter() for field in CHANGED_FIELDS}
    for record in records:
        condition = record["condition"]
        framing = "neutral" if condition == "neutral" else condition.rsplit("_", 1)[0]
        key = f"{record['batch']}|{record['model_requested']}|{record['trial_id']}"
        baseline = old[key]
        response_sha = sha(record["response"].encode("utf-8"))
        require(response_sha == baseline["response_sha256"], f"Response mismatch: {key}")
        for field, source in (("batch", "batch"), ("model", "model_requested"), ("word", "word"),
                              ("source", "source_set_label"), ("condition", "condition"), ("rep", "rep")):
            require(str(record[source]) == baseline[field], f"Metadata mismatch: {key}/{field}")
        result = score(record["response"], record["word"], framing)
        row = dict(key=key, batch=record["batch"], model=record["model_requested"],
                   word=record["word"], source=record["source_set_label"], condition=condition,
                   framing=framing, rep=record["rep"], response_sha256=response_sha,
                   response_type=result["response_type"], marking_position=result["marking_position"],
                   **result["fields"], **result["outcomes"], fragile="|".join(result["fragile"]))
        require(set(row) == set(baseline), "Candidate CSV schema differs")
        rows.append(row)
        delta = {field: [baseline[field], str(row[field])] for field in row
                 if str(row[field]) != baseline[field]}
        field_changes.update(delta.keys())
        for field in CHANGED_FIELDS:
            outcome_movements[field][f"{baseline[field]} -> {row[field]}"] += 1
        if delta:
            changes.append(dict(key=key, audit_changed=int(any(f in delta for f in CHANGED_FIELDS)),
                                differences=canonical(delta)))
    require({r["key"] for r in rows} == set(old), "Original/candidate keys differ")
    out.mkdir(parents=True)
    write_csv(out / "response_codes.csv", rows)
    if changes:
        write_csv(out / "changes.csv", changes)
    else:
        (out / "changes.csv").write_text("key,audit_changed,differences\n", encoding="utf-8")
    receipt = dict(version=VERSION, freeze_commit=freeze_commit, freeze_manifest_sha256=freeze_sha,
                   python=platform.python_version(), n=len(rows), input_archive_sha256=RAW_SHA,
                   collection_manifest_sha256=collection_sha, baseline_codes_sha256=sha(old_path.read_bytes()),
                   changed_any_field=len(changes), changed_audit_fields=sum(r["audit_changed"] for r in changes),
                   changed_counts_by_field=dict(sorted(field_changes.items())),
                   outcome_transitions=outcome_movements,
                   response_types=Counter(r["response_type"] for r in rows),
                   fragile_reasons=Counter(x for r in rows for x in r["fragile"].split("|") if x),
                   outputs={p.name: sha(p.read_bytes()) for p in sorted(out.iterdir())},
                   interpretation="Candidate detections only; human validation pending.")
    dump(out / "execution.json", receipt)
    print(json.dumps({"n": len(rows), "changed_audit_fields": receipt["changed_audit_fields"],
                      "changed_any_field": len(changes), "validation": "pending"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=REPO / "data.zip")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    run(args.archive, args.out, args.freeze_commit)


if __name__ == "__main__":
    main()
