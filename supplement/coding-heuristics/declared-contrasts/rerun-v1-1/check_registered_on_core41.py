#!/usr/bin/env python3
"""Undeclared descriptive check: the registered Fable v1.1 outputs (B) against
the investigator's 41 core labels, beside zoned 1.0 and 1.1.

Run after the declared rerun, at the investigator's request, to test one
inference in REPORT.md. It adds no estimate to the declared list. The 41 items
were selected on zoned 1.0/1.1 disagreement, not on B, so these counts are not
corpus error rates for B.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH = HERE.parents[1]
sys.path.insert(0, str(CH / "zoned-heuristic-v1-1"))
import audit  # noqa: E402  (frozen; human_outcomes only)

manifest = json.loads((CH / "zoned-heuristic-v1-1/quick/manifest-core41.json").read_text(encoding="utf-8"))
labels = {l["item_id"]: l for l in json.loads(
    (CH / "zoned-heuristic-v1-1/quick/human-labels-core41.json").read_text(encoding="utf-8"))["items"]}
B = {r["row_id"]: r for r in csv.DictReader(
    (CH / "mechanical-coding-heuristic-v1/run-2026-11-15_claude-fable-5-2/coded_responses.csv").open(encoding="utf-8"))}

counts, misses_N = Counter(), Counter()
recovered = {"R": Counter(), "N": Counter()}
for item in manifest["items"]:
    human = audit.human_outcomes(labels[item["item_id"]])
    b = B[item["key"]]
    reg = {"E": int(b["F_E"]), "R": int(b["F_nonrec"]), "N": int(b["F_N"]), "U": int(b["F_U"])}
    group = "changed" if item["stratum"].endswith("|changed") else "control"
    for o in "ERNU":
        for name, p in (("registered", reg[o]), ("zoned_1.0", item["predictions"]["1.0"][o]),
                        ("zoned_1.1", item["predictions"]["1.1"][o])):
            counts[f"{o}|{name}|correct_{group}"] += p == human[o]
            counts[f"{o}|{name}|false_positive"] += p == 1 and human[o] == 0
            counts[f"{o}|{name}|false_negative"] += p == 0 and human[o] == 1
    if human["N"] == 1 and reg["N"] == 0:
        misses_N[f"{b['frame']}|registered_E={reg['E']}|registered_R={reg['R']}"] += 1
    for o in "RN":
        if item["predictions"]["1.0"][o] == 0 and item["predictions"]["1.1"][o] == 1 and human[o] == 1:
            recovered[o]["v1.1_recovered_and_human_agrees"] += 1
            recovered[o]["registered_also_detects"] += reg[o]

result = {
    "schema": "bestiary2-registered-on-core41/1", "status": "undeclared descriptive check",
    "n": len(manifest["items"]), "changed": 25, "controls": 16,
    "table": {o: {name: {"correct_of_41": counts[f"{o}|{name}|correct_changed"] + counts[f"{o}|{name}|correct_control"],
                         "correct_changed_of_25": counts[f"{o}|{name}|correct_changed"],
                         "correct_controls_of_16": counts[f"{o}|{name}|correct_control"],
                         "false_positive": counts[f"{o}|{name}|false_positive"],
                         "false_negative": counts[f"{o}|{name}|false_negative"]}
                  for name in ("registered", "zoned_1.0", "zoned_1.1")} for o in "ERNU"},
    "registered_N_misses_by_frame": dict(sorted(misses_N.items())),
    "v1_1_recoveries_also_detected_by_registered": {o: dict(c) for o, c in recovered.items()},
    "limits": "One reader; items selected on zoned disagreement, not on the registered scorer; not a corpus error rate.",
}
out = HERE / "results/registered_on_core41.json"
out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(result["table"]["N"]), json.dumps(result["v1_1_recoveries_also_detected_by_registered"]))
