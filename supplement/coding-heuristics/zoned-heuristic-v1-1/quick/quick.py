"""Streamlined labelling for the zoned v1.1 audit: core subset, one-key page, scoring.

Standard library only. Reads the frozen audit manifest and the frozen labelling
page (for the response texts), never the raw archive and never a model. The
frozen audit.py is imported unchanged; its scorer does all the scoring.

    python quick.py build                      # writes manifest-core41.json and labelling-page-quick.html
    python quick.py score --labels L.json --set core --out results.json
    python quick.py score --labels L.json --set all  --out results.json
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import audit  # noqa: E402  (frozen module, imported unchanged)

FULL_MANIFEST = PARENT / "audit" / "manifest.json"
FULL_PAGE = PARENT / "audit" / "labelling-page.html"
CORE_MANIFEST = HERE / "manifest-core41.json"
QUICK_PAGE = HERE / "labelling-page-quick.html"
TEMPLATE = HERE / "quick-template.html"
PAGE_SCHEMA = "bestiary2-zoned-v1.1-quick-page/1"
CORE_RULE = ("Every selected item in a changed stratum, plus, in each populated unchanged "
             "stratum, the one selected item with the lowest selection rank "
             "(SHA-256 of the frozen selection seed, newline, canonical key).")
WORD = re.compile(r"^Describe an? (.+?)\.(?:\s|$)")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load_full():
    manifest = json.loads(FULL_MANIFEST.read_text(encoding="utf-8"))
    html = FULL_PAGE.read_text(encoding="utf-8")
    found = re.search(r'<script id="audit-data" type="application/json">(.*?)</script>', html, re.S)
    audit.require(found is not None, "Frozen page has no data block")
    payload = json.loads(found.group(1))
    audit.require(payload["audit_id"] == manifest["audit_id"], "Page and manifest audit IDs differ")
    by_id = {i["item_id"]: i for i in manifest["items"]}
    audit.require([i["item_id"] for i in payload["items"]] == [i["item_id"] for i in manifest["items"]],
                  "Page order differs from manifest order")
    for item in payload["items"]:
        ref = by_id[item["item_id"]]
        audit.require(sha(item["response"].encode("utf-8")) == ref["response_sha256"], "Response hash differs")
        audit.require(sha(item["prompt"].encode("utf-8")) == ref["prompt_sha256"], "Prompt hash differs")
        audit.require(item["imaginary"] is ref["imaginary"], "Imaginary flag differs")
    return manifest, payload, sha(FULL_MANIFEST.read_bytes())


def core_ids(manifest):
    """The 41-item core set. Uses stratum names and the frozen selection rank only."""
    chosen, best = [], {}
    for item in manifest["items"]:
        stratum = item["stratum"]
        if stratum.endswith("|changed"):
            chosen.append(item["item_id"])
        else:
            r = audit.rank(manifest["selection_seed"], item["key"])
            if stratum not in best or r < best[stratum][0]:
                best[stratum] = (r, item["item_id"])
    chosen += [item_id for _, item_id in best.values()]
    return set(chosen)


def subset_manifest(manifest, keep, parent_sha):
    sub = copy.deepcopy(manifest)
    sub["items"] = [i for i in manifest["items"] if i["item_id"] in keep]
    counts = Counter(i["stratum"] for i in sub["items"])
    for s in sub["strata"]:
        s["selected"] = counts.get(s["stratum"], 0)
        s["weight"] = s["population"] / s["selected"] if s["selected"] else None
    sub["selected_count"] = len(sub["items"])
    sub["instrument_masks"] = {v: {o: len(sub["items"]) for o in audit.OUTCOMES} for v in ("1.0", "1.1")}
    sub["subset"] = {"name": "core41", "rule": CORE_RULE, "parent_manifest_sha256": parent_sha,
                     "declared_in": "quick/STREAMLINE.md",
                     "note": "Same audit_id as the parent so labels from either page validate against both."}
    return sub


def page_payload(manifest, payload, keep):
    texts = {i["item_id"]: i for i in payload["items"]}
    order = [i["item_id"] for i in manifest["items"]]  # frozen display order
    ordered = [i for i in order if i in keep] + [i for i in order if i not in keep]
    items = []
    for item_id in ordered:
        t = texts[item_id]
        m = WORD.match(t["prompt"])
        audit.require(m is not None, "Prompt does not follow the study template")
        items.append({"item_id": item_id, "prompt": t["prompt"], "response": t["response"],
                      "imaginary": t["imaginary"], "word": m.group(1)})
    return {"schema": PAGE_SCHEMA, "label_schema": audit.LABEL_SCHEMA, "audit_id": manifest["audit_id"],
            "core_count": len(keep), "items": items}


def build(_args=None):
    manifest, payload, parent_sha = load_full()
    keep = core_ids(manifest)
    sub = subset_manifest(manifest, keep, parent_sha)
    for s in sub["strata"]:
        audit.require(s["population"] == 0 or s["selected"] > 0, "Core set leaves a populated stratum empty")
    audit.dump(CORE_MANIFEST, sub)
    html = audit.page_html(page_payload(manifest, payload, keep), TEMPLATE.read_text(encoding="utf-8"))
    QUICK_PAGE.write_text(html, encoding="utf-8")
    print(json.dumps({"audit_id": manifest["audit_id"], "core": len(keep), "total": len(manifest["items"]),
                      "changed_in_core": sum(i["stratum"].endswith("|changed") for i in sub["items"]),
                      "core_manifest_sha256": sha(CORE_MANIFEST.read_bytes()),
                      "page_sha256": sha(QUICK_PAGE.read_bytes())}))


def labels_for(labels, manifest):
    wanted = {i["item_id"] for i in manifest["items"]}
    return {**labels, "items": [l for l in labels["items"] if l.get("item_id") in wanted]}


def score(args):
    full = json.loads(FULL_MANIFEST.read_text(encoding="utf-8"))
    audit.validate_labels(full, json.loads(args.labels.read_text(encoding="utf-8")), complete=False)
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    manifest = full if args.set == "all" else json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    result = audit.score_labels(manifest, labels_for(labels, manifest))
    result["scored_set"] = args.set
    audit.dump(args.out, result)
    print(json.dumps({"set": args.set, "scored": result["n"], "unsure": result["unsure_count"], "output": str(args.out)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    s = sub.add_parser("score")
    s.add_argument("--labels", type=Path, required=True)
    s.add_argument("--set", choices=("core", "all"), required=True)
    s.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args) if args.command == "build" else score(args)


if __name__ == "__main__":
    main()
