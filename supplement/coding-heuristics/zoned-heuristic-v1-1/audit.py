"""Prepare the declared, metadata-blinded audit; score only submitted human labels.

Standard library only. Preparing reads response text only after checking the
committed freeze. Neither command calls a model or supplies human judgments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECT_SEED = "bestiary2-zoned-v1.1-audit-select-20261115"
ORDER_SEED = "bestiary2-zoned-v1.1-audit-order-20261115"
MANIFEST_SCHEMA = "bestiary2-zoned-v1.1-audit-manifest/1"
LABEL_SCHEMA = "bestiary2-zoned-v1.1-human-labels/1"
RAW_SHA = "f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6"
BASELINE_SHA = "84afb45c6b50563486b668dd148d7fc9798da571c1acfc9ccae9b4d7b002afb2"
OUTCOMES = {
    "E": "E_description", "R": "nonrec_any",
    "N": "N_nonrecognition_without_description", "U": "U_unmarked_description",
    "S": "substitute_description",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def dump(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def rank(seed, key):
    return digest((seed + "\n" + key).encode("utf-8")), key


def load_codes(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    rows = {}
    for record in records:
        key = record["key"]
        require(key not in rows, "Duplicate codes key: " + key)
        for field in OUTCOMES.values():
            require(record[field] in ("0", "1"), "Nonbinary field: " + field)
            record[field] = int(record[field])
        require(re.fullmatch(r"[0-9a-f]{64}", record["response_sha256"]), "Bad response hash")
        rows[key] = record
    require(rows, "Empty codes file")
    return rows


def check_freeze(repo, manifest, commit):
    """Require bytes of every frozen file and the manifest in a real commit."""
    repo, manifest = Path(repo).resolve(), Path(manifest).resolve()
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "Use the full 40-character freeze commit")
    relative = manifest.relative_to(repo).as_posix()

    def committed(path):
        return subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path])

    blob = manifest.read_bytes()
    require(committed(relative) == blob, "Freeze manifest differs from committed file")
    names = set()
    for line in blob.decode("utf-8").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        require(match, "Invalid sha256sum freeze line")
        expected, name = match.groups()
        require(name not in names, "Duplicate frozen path")
        names.add(name)
        path = (manifest.parent / name).resolve()
        require(path.is_relative_to(manifest.parent), "Frozen path escapes its directory")
        content = path.read_bytes()
        require(digest(content) == expected, "Frozen file changed: " + name)
        require(committed(path.relative_to(repo).as_posix()) == content,
                "Frozen file differs from committed file: " + name)
    require({"PLAN.md", "METHOD.md", "zoned_heuristic.py", "run_corpus.py", "audit.py",
             "audit-template.html"} <= names, "Freeze omits required scorer or audit files")
    return {"commit": commit, "manifest": relative, "sha256": digest(blob), "files": sorted(names)}


def exposure_exclusions(repo, codes):
    """Recover documented exposure, then close exclusions over response hashes.

    The original context hashes and already-inspected fixture text are read here;
    no uninspected corpus response text is used to reconstruct exposure.
    """
    base = Path(repo) / "supplement/coding-heuristics"
    keys, hashes, sources = defaultdict(set), defaultdict(set), {}

    def read(name):
        blob = (base / name).read_bytes()
        sources[name] = {"sha256": digest(blob)}
        return json.loads(blob)

    for name in ("zoned-heuristic-v1/dev_keys.json", "zoned-heuristic-v1/holdout_keys.json"):
        values = read(name)
        require(isinstance(values, list) and all(isinstance(k, str) for k in values), "Bad exposure keys")
        sources[name]["documented_keys"] = len(values)
        for key in values:
            require(key in codes, "Prior inspection key absent from corpus: " + key)
            keys[key].add(name)
    name = "human-pass/human_labels.json"
    human = read(name)
    for item in human["items"]:
        require(item["key"] in codes, "Prior human key absent from corpus")
        keys[item["key"]].add(name)
    sources[name]["documented_keys"] = len(human["items"])

    name = "context-heuristic-v1/fixtures/development_allowlist.json"
    allowlist = read(name)
    for item in allowlist["items"].values():
        hashes[item["response_sha256"]].add(name)
    sources[name]["documented_response_hashes"] = len(allowlist["items"])
    name = "context-heuristic-v1/fixtures/development_texts.json"
    development = read(name)
    for item in development["items"]:
        hashes[digest(item["response"].encode("utf-8"))].add(name)
    sources[name]["documented_texts"] = len(development["items"])
    name = "context-heuristic-v1/fixtures/boundary_texts.json"
    boundary = [item for item in read(name) if item["origin"] == "previously_inspected_development"]
    for item in boundary:
        hashes[digest(item["response"].encode("utf-8"))].add(name)
    sources[name]["corpus_derived_cards"] = len(boundary)

    # Include old page practice material too; exact-match synthetic text simply
    # produces no corpus exclusion. Parse data, never execute the page script.
    name = "human-pass/labelling-page.html"
    blob = (base / name).read_bytes()
    found = re.search(r'<script id="data" type="application/json">(.*?)</script>', blob.decode(), re.S)
    require(found, "Cannot locate prior page data")
    page = json.loads(found.group(1))
    texts = page["items"] + page.get("practice", [])
    for item in texts:
        hashes[digest(item["r"].encode("utf-8"))].add(name)
    sources[name] = {"sha256": digest(blob), "documented_page_texts": len(texts)}

    for key, reasons in list(keys.items()):
        hashes[codes[key]["response_sha256"]].update(reasons)
    direct_keys = set(keys)
    for key, row in codes.items():
        if row["response_sha256"] in hashes:
            keys[key].update(hashes[row["response_sha256"]])
    for name in sources:
        sources[name]["excluded_matching_corpus_rows"] = sum(name in reasons for reasons in keys.values())
    return {
        "rule": "Recorded inspection keys plus every exact response-hash duplicate of recorded exposure",
        "sources": sources, "direct_key_count": len(direct_keys), "excluded_count": len(keys),
        "hash_only_additional_count": len(set(keys) - direct_keys),
        "excluded": [{"key": k, "response_sha256": codes[k]["response_sha256"],
                      "sources": sorted(keys[k])} for k in sorted(keys)],
        "unrecoverable_history": ["earlier audit64", "earlier targeted4", "earlier check32",
                                  "informal snippet exposure without complete key logs"],
        "freshness": "Disjoint from documented prior inspection; historical exposure is incompletely logged",
    }


def select_sample(old, new, excluded, size=96):
    require(set(old) == set(new), "Original and repaired corpus keys differ")
    strata = defaultdict(list)
    endpoints = sorted({r["model"] for r in old.values()})
    for endpoint in endpoints:
        for bank in ("fresh", "known"):
            for changed in ("changed", "unchanged"):
                strata[(endpoint, bank, changed)] = []
    for key, previous in old.items():
        candidate = new[key]
        for field in ("batch", "model", "word", "source", "condition", "framing", "rep", "response_sha256"):
            require(previous[field] == candidate[field], "Original/repaired metadata differs: " + field)
        if key in excluded:
            continue
        changed = any(previous[f] != candidate[f] for f in (*OUTCOMES.values(), "response_type"))
        strata[(previous["model"], previous["batch"], "changed" if changed else "unchanged")].append(key)
    population = sum(map(len, strata.values()))
    target = min(size, population)
    allocated = {s: min(3, len(keys)) for s, keys in strata.items()}
    require(sum(allocated.values()) <= target, "Audit target is smaller than initial stratum allocation")
    while sum(allocated.values()) < target:
        available = [s for s in strata if allocated[s] < len(strata[s])]
        chosen = min(available, key=lambda s: (-(len(strata[s]) - allocated[s]), s))
        allocated[chosen] += 1
    selected, counts = [], []
    for stratum, keys in sorted(strata.items()):
        n, N = allocated[stratum], len(keys)
        name = "|".join(stratum)
        counts.append({"stratum": name, "population": N, "selected": n,
                       "inclusion_probability": n / N if N else None,
                       "weight": N / n if n else None})
        for key in sorted(keys, key=lambda k: rank(SELECT_SEED, k))[:n]:
            selected.append({"key": key, "stratum": name})
    selected.sort(key=lambda item: rank(ORDER_SEED, item["key"]))
    for index, item in enumerate(selected, 1):
        item["item_id"] = f"item-{index:03d}"
    return selected, counts


def load_selected_texts(archive_path, selected, codes):
    """Read full study text only after a committed freeze, without printing it."""
    wanted = {item["key"] for item in selected}
    found, seen = {}, set()
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate raw archive members")
        for name in sorted(names):
            if not (name.startswith(("data/raw/fresh/", "data/raw/known/")) and name.endswith(".jsonl")):
                continue
            for line in archive.read(name).splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                key = f"{row['batch']}|{row['model_requested']}|{row['trial_id']}"
                require(key not in seen, "Duplicate raw response key")
                seen.add(key)
                require(key in codes, "Raw response absent from codes")
                require(digest(row["response"].encode("utf-8")) == codes[key]["response_sha256"],
                        "Raw response hash differs from frozen codes")
                if key in wanted:
                    require(isinstance(row["prompt"], str) and isinstance(row["response"], str), "Invalid text")
                    found[key] = {"prompt": row["prompt"], "response": row["response"],
                                  "imaginary": codes[key]["framing"] == "imaginary"}
    require(seen == set(codes), "Raw and coded corpus keys differ")
    require(set(found) == wanted, "Selected responses missing from raw archive")
    return found


def page_html(payload, template):
    require(template.count("__AUDIT_PAYLOAD__") == 1, "Expected exactly one page data placeholder")
    # Escaping '<' prevents response text from closing the JSON script element.
    encoded = canonical(payload).decode().replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace("__AUDIT_PAYLOAD__", encoded)


def prepare(args):
    repo = args.repo_root.resolve()
    require(not args.out.exists(), "Preserve existing audit output; do not overwrite or redraw")
    freeze = check_freeze(repo, args.freeze_manifest, args.freeze_commit)
    original = repo / "supplement/coding-heuristics/zoned-heuristic-v1/results/response_codes.csv"
    old, new = load_codes(original), load_codes(args.repaired_codes)
    require(len(old) == len(new) == 16000, "Expected the complete 16000-row corpus")
    exclusions = exposure_exclusions(repo, old)
    selected, strata = select_sample(old, new, {i["key"] for i in exclusions["excluded"]})
    sources = {"original_codes_sha256": digest(original.read_bytes()),
               "repaired_codes_sha256": digest(args.repaired_codes.read_bytes()),
               "raw_archive_sha256": digest(args.raw_archive.read_bytes())}
    require(sources["original_codes_sha256"] == BASELINE_SHA, "Original codes differ from published 1.0 baseline")
    require(sources["raw_archive_sha256"] == RAW_SHA, "Raw archive differs from published data.zip")
    receipt_path = args.repaired_codes.parent / "execution.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt["version"] == "bestiary2-zoned-heuristic/1.1.0", "Repaired codes receipt has wrong version")
    require(receipt["freeze_commit"] == args.freeze_commit, "Repaired codes belong to a different freeze")
    require(receipt["freeze_manifest_sha256"] == freeze["sha256"], "Repaired codes freeze manifest differs")
    require(receipt["input_archive_sha256"] == RAW_SHA and receipt["n"] == 16000, "Repaired input receipt differs")
    require(receipt["baseline_codes_sha256"] == sources["original_codes_sha256"], "Repaired baseline differs from original codes")
    require(receipt["outputs"][args.repaired_codes.name] == sources["repaired_codes_sha256"], "Repaired CSV differs from its execution receipt")
    sources["repaired_execution_sha256"] = digest(receipt_path.read_bytes())
    identity = {"freeze": freeze, "sources": sources, "selection_seed": SELECT_SEED,
                "order_seed": ORDER_SEED, "selected": selected, "exclusions": exclusions}
    audit_id = "zoned-v1.1-" + digest(canonical(identity))[:20]
    texts = load_selected_texts(args.raw_archive, selected, old)
    items = []
    for item in selected:
        key = item["key"]
        predictions = {version: {o: codes[key][f] for o, f in OUTCOMES.items()}
                       for version, codes in (("1.0", old), ("1.1", new))}
        for version, codes in (("1.0", old), ("1.1", new)):
            predictions[version]["S"] = int(codes[key]["response_type"] == "DESCRIBE_SUBSTITUTE")
        items.append({**item, "response_sha256": old[key]["response_sha256"],
                      "prompt_sha256": digest(texts[key]["prompt"].encode("utf-8")),
                      "imaginary": texts[key]["imaginary"],
                      "predictions": predictions})
    manifest = {"schema": MANIFEST_SCHEMA, "audit_id": audit_id, "freeze": freeze,
                "sources": sources, "selection_seed": SELECT_SEED, "order_seed": ORDER_SEED,
                "eligible_population": sum(s["population"] for s in strata),
                "selected_count": len(items), "strata": strata, "exclusions": exclusions,
                "instrument_masks": {version: {o: len(items) for o in OUTCOMES} for version in ("1.0", "1.1")},
                "items": items, "labels_status": "Unlabelled; no model judgments supplied",
                "substitution_reference": "Human D=S versus response_type=DESCRIBE_SUBSTITUTE; raw substitute flag is used only for sampling changed status",
                "masking": "Page includes only opaque IDs, full prompt/response and prompt-imaginary flag"}
    payload = {"schema": "bestiary2-zoned-v1.1-audit-page/1", "audit_id": audit_id,
               "items": [{"item_id": i["item_id"], **texts[i["key"]]} for i in items]}
    html = page_html(payload, (HERE / "audit-template.html").read_text(encoding="utf-8"))
    args.out.mkdir(parents=True)
    dump(args.out / "manifest.json", manifest)
    (args.out / "labelling-page.html").write_text(html, encoding="utf-8")
    print(json.dumps({"audit_id": audit_id, "selected": len(items), "eligible": manifest["eligible_population"],
                      "excluded": exclusions["excluded_count"], "page": str(args.out / "labelling-page.html")}))


def validate_labels(manifest, labels, *, complete=True):
    require(manifest["schema"] == MANIFEST_SCHEMA, "Wrong audit manifest schema")
    require(labels.get("schema") == LABEL_SCHEMA, "Wrong human labels schema")
    require(labels.get("audit_id") == manifest["audit_id"], "Labels belong to another audit")
    selected = {i["item_id"]: i for i in manifest["items"]}
    require(len(selected) == len(manifest["items"]) == manifest["selected_count"], "Duplicate or inconsistent audit IDs")
    require(isinstance(labels.get("items"), list), "Labels items must be a list")
    found = {}
    for label in labels["items"]:
        require(isinstance(label, dict), "Each label must be an object")
        item_id = label.get("item_id")
        require(item_id in selected and item_id not in found, "Unknown or repeated label item ID")
        require(label.get("nonrecognition") in ("Y", "N"), "Invalid nonrecognition answer")
        require(label.get("description") in ("Y", "H", "S", "N"), "Invalid description answer")
        if label["description"] in ("Y", "H"):
            require(label.get("mark") in ("Y", "E", "N"), "Description requires a mark answer")
            require(label["mark"] != "E" or selected[item_id]["imaginary"], "Prompt-echo mark outside imaginary prompt")
        else:
            require(label.get("mark") is None, "No mark answer is applicable without a target description")
        require(type(label.get("flagged_unsure")) is bool, "Unsure flag must be boolean")
        require(type(label.get("ms")) in (int, float) and 0 <= label["ms"] < 1e12, "Invalid elapsed time")
        require(isinstance(label.get("notes", ""), str), "Notes must be text")
        found[item_id] = label
    if complete:
        require(set(found) == set(selected), f"Human labels incomplete: {len(found)}/{len(selected)}; no scoring performed")
    return found


def human_outcomes(label):
    E, R = int(label["description"] in ("Y", "H")), int(label["nonrecognition"] == "Y")
    return {"E": E, "R": R, "N": int(R and not E),
            "U": int(E and not R and label["mark"] == "N"), "S": int(label["description"] == "S")}


def score_labels(manifest, labels):
    human = validate_labels(manifest, labels)
    strata = {s["stratum"]: s for s in manifest["strata"]}
    require(len(strata) == len(manifest["strata"]), "Duplicate stratum")
    actual = Counter(item["stratum"] for item in manifest["items"])
    for name, stratum in strata.items():
        require(0 <= stratum["selected"] <= stratum["population"] and actual[name] == stratum["selected"], "Invalid stratum counts")
        require(stratum["population"] == 0 or stratum["selected"] > 0, "Unsampled nonempty stratum")
    require(set(actual) <= set(strata), "Unknown selected stratum")
    total_population = sum(s["population"] for s in strata.values())
    require(total_population == manifest["eligible_population"], "Eligible population count mismatch")
    output = {}
    for name, include_unsure in (("all_labels", True), ("excluding_unsure_sensitivity", False)):
        records = [(i, human[i["item_id"]], strata[i["stratum"]]["population"] / strata[i["stratum"]]["selected"])
                   for i in manifest["items"] if include_unsure or not human[i["item_id"]]["flagged_unsure"]]
        weight_sum = sum(w for _, _, w in records)
        results = {}
        for outcome in OUTCOMES:
            sums = Counter()
            for item, label, weight in records:
                truth = human_outcomes(label)[outcome]
                correct = {}
                for version in ("1.0", "1.1"):
                    prediction = item["predictions"][version][outcome]
                    require(type(prediction) is int and prediction in (0, 1), "Invalid instrument prediction")
                    correct[version] = int(prediction == truth)
                    sums[version + "_correct"] += correct[version]
                    sums[version + "_weighted_correct"] += weight * correct[version]
                    sums[version + "_false_positive"] += int(prediction == 1 and truth == 0)
                    sums[version + "_false_negative"] += int(prediction == 0 and truth == 1)
                    if not label["flagged_unsure"]:
                        sums[version + "_certain_correct"] += correct[version]
                        sums[version + "_certain_weighted_correct"] += weight * correct[version]
                sums["new_only_correct"] += correct["1.1"] and not correct["1.0"]
                sums["old_only_correct"] += correct["1.0"] and not correct["1.1"]
                sums["paired_weighted_correctness_difference"] += weight * (correct["1.1"] - correct["1.0"])
                if label["flagged_unsure"]:
                    sums["unsure_n"] += 1
                    sums["unsure_weight"] += weight
                    if item["predictions"]["1.0"][outcome] != item["predictions"]["1.1"][outcome]:
                        sums["unsure_disagree_n"] += 1
                        sums["unsure_disagree_weight"] += weight
                else:
                    sums["certain_paired_difference"] += correct["1.1"] - correct["1.0"]
                    sums["certain_weighted_paired_difference"] += weight * (correct["1.1"] - correct["1.0"])
            results[outcome] = {
                "n": len(records), "weight_denominator": weight_sum,
                "versions": {v: {"correct": sums[v + "_correct"],
                                  "raw_accuracy": sums[v + "_correct"] / len(records) if records else None,
                                  "weighted_accuracy": sums[v + "_weighted_correct"] / weight_sum if weight_sum else None,
                                  "false_positive": sums[v + "_false_positive"], "false_negative": sums[v + "_false_negative"],
                                  "unsure_truth_weighted_accuracy_bounds": [sums[v + "_certain_weighted_correct"] / weight_sum,
                                      (sums[v + "_certain_weighted_correct"] + sums["unsure_weight"]) / weight_sum] if weight_sum else None}
                             for v in ("1.0", "1.1")},
                "paired_raw_correctness_difference": (sums["1.1_correct"] - sums["1.0_correct"]) / len(records) if records else None,
                "paired_weighted_correctness_difference": sums["paired_weighted_correctness_difference"] / weight_sum if weight_sum else None,
                "new_only_correct": sums["new_only_correct"], "old_only_correct": sums["old_only_correct"],
                "unsure_truth_weighted_paired_difference_bounds": [
                    (sums["certain_weighted_paired_difference"] - sums["unsure_disagree_weight"]) / weight_sum,
                    (sums["certain_weighted_paired_difference"] + sums["unsure_disagree_weight"]) / weight_sum] if weight_sum else None,
            }
        output[name] = {"included_labels": len(records), "excluded_unsure": len(human) - len(records),
                        "weight_coverage": weight_sum / total_population if total_population else None,
                        "outcomes": results}
    return {"schema": "bestiary2-zoned-v1.1-human-audit-results/1", "audit_id": manifest["audit_id"],
            "human_labels_sha256": digest(canonical(labels)), "n": len(human),
            "unsure_count": sum(l["flagged_unsure"] for l in human.values()),
            "estimand": "Agreement with this human pass on the eligible corpus; inverse stratum inclusion weights N_h/n_h",
            "limitations": "One informed investigator; historical exposure incompletely logged; unsure exclusion is a sensitivity on the retained labels, not a full-corpus accuracy estimate; no new hypothesis tests",
            "main_outcomes": ["E", "R", "N", "U"], "separate_substitution_outcome": "S", **output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--repo-root", type=Path, default=HERE.parents[2])
    prepare_parser.add_argument("--repaired-codes", type=Path, default=HERE / "results/response_codes.csv")
    prepare_parser.add_argument("--raw-archive", type=Path, required=True)
    prepare_parser.add_argument("--freeze-manifest", type=Path, default=HERE / "FREEZE.sha256")
    prepare_parser.add_argument("--freeze-commit", required=True)
    prepare_parser.add_argument("--out", type=Path, required=True)
    for command in ("validate", "score"):
        child = sub.add_parser(command)
        child.add_argument("--manifest", type=Path, required=True)
        child.add_argument("--labels", type=Path, required=True)
        if command == "score":
            child.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args)
    else:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        labels = json.loads(args.labels.read_text(encoding="utf-8"))
        if args.command == "validate":
            found = validate_labels(manifest, labels, complete=False)
            print(json.dumps({"valid": True, "completed": len(found), "required": manifest["selected_count"],
                              "complete": len(found) == manifest["selected_count"]}))
        else:
            result = score_labels(manifest, labels)
            dump(args.out, result)
            print(json.dumps({"scored": result["n"], "unsure": result["unsure_count"], "output": str(args.out)}))


if __name__ == "__main__":
    main()
