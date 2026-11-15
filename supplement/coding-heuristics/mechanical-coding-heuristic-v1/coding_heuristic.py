"""Post-publication coding layer for Artificial Bestiary 2.

Relies on upstream GPT and Fable v1.1 scorers for their registered surface
features; never replaces them. Standard-library only; no model/API judge.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

VERSION = "bestiary2-response-categories/1.0.0"
GPT_PRIMARY = ("M01", "M02", "M03", "M09")
GPT_SECONDARY = ("M04", "M05", "M07", "M08", "M10", "M32")
FABLE_CUES = ("nonrec", "fiction", "construct", "interp")
CLASSES = (
    "D0_UNMARKED", "D1_NONREC_MARKED", "D2_OTHER_MARKED",
    "N0_NONRECOGNITION", "O0_CUED_OTHER", "O1_UNMARKED_OTHER",
)
MODEL_GROUPS = {
    "claude-sonnet-4-6": ("Anthropic", "historical"),
    "claude-haiku-4-5": ("Anthropic", "historical"),
    "claude-sonnet-5-5": ("Anthropic", "current"),
    "claude-haiku-5-5": ("Anthropic", "current"),
    "gpt-5.4-mini": ("OpenAI", "historical"),
    "gpt-5.4-nano": ("OpenAI", "historical"),
    "gpt-6-sol": ("OpenAI", "current"),
    "gpt-6-luna": ("OpenAI", "current"),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path: Path, label: str):
    if not path.is_file():
        raise FileNotFoundError(f"Required upstream scorer not found: {path}")
    spec = importlib.util.spec_from_file_location(label, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load upstream scorer {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_upstream(repo: Path):
    """Load the provided repository's scoring code; never modify its files."""
    repo = Path(repo).resolve()
    gpt_path = repo / "bestiary_scorer.py"
    fable_path = repo / "prereg" / "claude_scorer_v1_1.py"
    inventory = repo / "docs" / "gpt-proposal" / "inventories-gpt-v1.json"
    if not inventory.is_file():
        raise FileNotFoundError(f"Required GPT inventory not found: {inventory}")
    gpt = load_module(gpt_path, "b2_original_gpt")
    fable = load_module(fable_path, "b2_original_fable")
    if getattr(gpt, "VERSION", None) != "gpt-bestiary-2-v1.0":
        raise ValueError("Expected GPT scorer v1.0; aborting rather than silently changing definitions")
    if getattr(fable, "SCORER_VERSION", None) != "claude-fable-5-2/1.1":
        raise ValueError("Expected amended Fable scorer v1.1; aborting")
    provenance = {
        "gpt_scorer_version": gpt.VERSION,
        "fable_scorer_version": fable.SCORER_VERSION,
        "source_hash_sha256": {
            "bestiary_scorer.py": sha256_file(gpt_path),
            "docs/gpt-proposal/inventories-gpt-v1.json": sha256_file(inventory),
            "prereg/claude_scorer_v1_1.py": sha256_file(fable_path),
        },
    }
    return gpt, fable, provenance


def split_condition(condition: str) -> tuple[str, str]:
    if condition == "neutral":
        return "neutral", "none"
    for prefix in ("type_of", "imaginary", "real"):
        for kind in ("animal", "object", "idea"):
            if condition == f"{prefix}_{kind}":
                return prefix, kind
    raise ValueError(f"Unsupported condition {condition!r}; expected neutral or [real|imaginary|type_of]_[animal|object|idea]")


def classify_fable(desc: int, nonrec: int, cues: int) -> str:
    """Six exhaustive, mutually exclusive *derived* bins for usable responses."""
    if desc not in (0, 1) or nonrec not in (0, 1) or cues not in (0, 1):
        raise ValueError("Fable E/nonrecognition/cue indicators must be binary")
    if desc:
        if not cues:
            if nonrec:
                raise ValueError("Fable invariant violated: nonrecognition is itself a cue")
            return "D0_UNMARKED"
        return "D1_NONREC_MARKED" if nonrec else "D2_OTHER_MARKED"
    if nonrec:
        return "N0_NONRECOGNITION"
    return "O0_CUED_OTHER" if cues else "O1_UNMARKED_OTHER"


def definition_agreement(gpt_m09: int, fable_e: int) -> str:
    if gpt_m09 and fable_e:
        return "BOTH"
    if gpt_m09:
        return "GPT_ONLY"
    if fable_e:
        return "FABLE_ONLY"
    return "NEITHER"


def get_response(row):
    """Accept a published response-features row or a minimal response JSON row."""
    if "fields" in row and "phase" in row and "response" not in row:
        raise ValueError("An attempts.jsonl ledger is not a selected-response export. Use analysis/response-features.jsonl after repository's audited analysis")
    response = row.get("response")
    if response is not None and not isinstance(response, str):
        raise ValueError("response must be a string or null")
    return response


def _any_feature(features, family):
    value = features.get(family)
    if not isinstance(value, dict) or value.get("any") not in (0, 1):
        raise ValueError(f"Missing registered GPT feature {family}.any")
    return int(value["any"])


def _flag(value):
    return int(bool(value))


def _excerpts(gpt_record, wanted, redact=False):
    entries = []
    for m in gpt_record.get("matches", []):
        if m.get("family") not in wanted:
            continue
        item = {
            "family": m.get("family"), "entry": m.get("entry"),
            "raw_span": m.get("raw_span"),
            "local_negation_window": m.get("local_negation"),
            "quotation_overlap": m.get("quotation_overlap"),
        }
        if not redact:
            item["matched_text"] = m.get("raw_text")
        entries.append(item)
    return entries


def fable_evidence(response, word, fable, redact=False):
    """Fable offsets are in its normalized text, NOT offsets in raw response."""
    norm = fable.normalize(response)
    hit_list = []
    for family in FABLE_CUES:
        for a, b, matched in fable.find_all(norm, family):
            hit = {"family": family, "normalized_span": [a, b]}
            if not redact:
                hit["matched_normalized_text"] = matched
            hit_list.append(hit)
    pos, neg = fable.definition_forms(norm, word)
    for key, group in (("definition_positive", pos), ("definition_negated", neg)):
        for a, b, matched in group:
            hit = {"family": key, "normalized_span": [a, b]}
            if not redact:
                hit["matched_normalized_text"] = matched
            hit_list.append(hit)
    return sorted(hit_list, key=lambda item: (item["normalized_span"][0], item["family"]))


def code_one(row: dict, gpt, fable, *, index=0, verify_embedded=False, redact=False):
    response = get_response(row)
    word = row.get("word")
    prompt = row.get("prompt")
    if not isinstance(word, str) or not word.strip():
        raise ValueError(f"Row {index}: missing word (target)")
    condition = row.get("condition", "")
    frame, category = split_condition(condition)
    model = row.get("model_requested") or row.get("model") or ""
    batch = row.get("batch") or ""
    group, generation = MODEL_GROUPS.get(model, ("unknown", "unknown"))
    is_selected = (row.get("terminal") is not False and row.get("valid") is not False
                   and not any(bool(row.get(k)) for k in ("issue", "protocol_violation", "error")))
    usable = bool(is_selected and isinstance(response, str) and response.strip())
    truncated = row.get("truncated") if "truncated" in row else None
    if truncated is not None and not isinstance(truncated, bool):
        raise ValueError(f"Row {index}: truncated must be boolean or null")
    rid = (f"{batch}|{model}|{row['trial_id']}" if row.get("trial_id")
           else f"{batch}|{model}|{word}|{condition}|{row.get('rep','')}|{index}")
    out = {
        "row_id": rid, "source_row": index, "batch": batch, "model": model,
        "provider_group": group, "generation": generation,
        "word": word, "word_set": row.get("word_set") or "",
        "source_set_label": row.get("source_set_label") or row.get("source") or "",
        "condition": condition, "frame": frame, "category": category,
        "rep": row.get("rep", ""),
        "terminal": int(is_selected), "complete": "" if row.get("complete") is None else int(bool(row["complete"])),
        "truncated": "" if truncated is None else int(truncated),
        "refusal": "" if row.get("refusal") is None else int(bool(row["refusal"])),
        "usable": int(usable), "gpt_primary_eligible": int(usable),
        "fable_primary_eligible": (int(usable and not truncated) if truncated is not None else ""),
        "gpt_scorer_origin": "", "gpt_definition_fable_E": "", "response_class": "X_UNUSABLE",
        "secondary_tags": "", "secondary_tag_count": "",
    }
    flag_names = ["M01", "M02", "M03", "M09", "M04", "M05", "M07", "M08", "M10", "M32"]
    for fam in flag_names:
        out[fam] = ""
    for key in (
        "M01_without_imaginary", "M02_modal_only", "M09_local_negation", "M09_quoted",
        "M13_state", "M31_animal", "M31_object", "M31_idea",
        "F_E", "F_U", "F_N", "F_cue_any", "F_nonrec", "F_fiction", "F_construct", "F_interp",
        "F_hedge", "F_def_positive_n", "F_def_negated_n", "F_attr_n",
        "S_FICTION", "S_NONRECOGNITION", "S_CONSTRUCTION", "S_INTERPRETATION",
        "S_QUALIFICATION", "S_CONTEXT_REQUEST", "S_OFFER", "S_NEGATED_DEFINITION",
        "S_GPT_DEF_LOCAL_NEGATION", "S_QUOTED_GPT_CUE", "S_PROMPT_IMAGINARY_OVERLAP",
        "S_TARGET_DEFINITION_DISAGREEMENT", "S_WORD_REPAIR", "S_CATEGORY_WORDS",
    ):
        out[key] = ""
    evidence = {"row_id": rid, "source_row": index, "usable": int(usable), "gpt_matches": [], "fable_matches_normalized": [],
                "note": "GPT spans are raw-response offsets; Fable spans are normalized-text offsets, not raw offsets."}
    if not usable:
        return out, evidence
    if not isinstance(prompt, str):
        raise ValueError(f"Row {index}: prompt is required for published GPT scoring or newly scored rows")
    stored = row.get("scoring")
    if stored is not None:
        if not isinstance(stored, dict) or stored.get("version") != gpt.VERSION or not stored.get("usable"):
            raise ValueError(f"Row {index}: incompatible or unusable embedded GPT score")
        grecord = stored
        out["gpt_scorer_origin"] = "published_embedded"
        if verify_embedded:
            rerun = gpt.score(response, word, prompt)
            # Compare registered features and all match spans, not environment-sensitive JSON formatting.
            if any(_any_feature(rerun["features"], k) != _any_feature(grecord["features"], k) for k in GPT_PRIMARY):
                raise ValueError(f"Row {index}: embedded primary GPT scores differ from recomputed scores")
            if rerun["matches"] != grecord["matches"]:
                raise ValueError(f"Row {index}: embedded GPT match evidence differs from recomputed score")
    else:
        grecord = gpt.score(response, word, prompt)
        out["gpt_scorer_origin"] = "recomputed_from_input"
    if not grecord["usable"]:
        raise ValueError(f"Row {index}: GPT scorer unexpectedly marked nonempty response unusable")
    fscore = fable.score_text(response, word)
    gfeat = grecord["features"]
    for fam in flag_names:
        out[fam] = _any_feature(gfeat, fam)
    # These are exactly the registered binary values; no recoding or vetoes.
    out["M01_without_imaginary"] = int(any(m.get("family") == "M01" and m.get("entry") != "imaginary" for m in grecord.get("matches", [])))
    out["M02_modal_only"] = int(gfeat["M02"]["components"]["modal"]["any"])
    def_matches = [m for m in grecord.get("matches", []) if m.get("family") == "M09"]
    out["M09_local_negation"] = int(any(m.get("local_negation") for m in def_matches))
    out["M09_quoted"] = int(any(m.get("quotation_overlap") for m in def_matches))
    out["M13_state"] = gfeat["M13"]["state"]
    for kind in ("animal", "object", "idea"):
        out["M31_" + kind] = int(gfeat["M31"]["components"][kind]["any"])
    e = int(fscore["desc_form"])
    u = int(fscore["unmarked_description"])
    n = int(fscore["nonrec_no_description"])
    cue = int(fscore["cue_any"])
    nonrec = int(fscore["any_nonrec"])
    if u != int(e and not cue) or n != int(nonrec and not e) or (u and not e) or (e and n):
        raise ValueError(f"Row {index}: Fable E/U/N scorer invariants violated")
    out.update(F_E=e, F_U=u, F_N=n, F_cue_any=cue, F_nonrec=nonrec,
               F_fiction=int(fscore["any_fiction"]), F_construct=int(fscore["any_construct"]),
               F_interp=int(fscore["any_interp"]), F_hedge=int(fscore["any_hedge"]),
               F_def_positive_n=int(fscore["n_def"]), F_def_negated_n=int(fscore["n_def_negated"]),
               F_attr_n=int(fscore["n_attr"]))
    out["response_class"] = classify_fable(e, nonrec, cue)
    out["gpt_definition_fable_E"] = definition_agreement(out["M09"], e)
    out.update(
        S_FICTION=int(fscore["any_fiction"]),
        S_NONRECOGNITION=nonrec,
        S_CONSTRUCTION=int(fscore["any_construct"]),
        S_INTERPRETATION=int(fscore["any_interp"]),
        S_QUALIFICATION=out["M02"],
        S_CONTEXT_REQUEST=out["M07"],
        S_OFFER=out["M08"],
        S_NEGATED_DEFINITION=int(fscore["n_def_negated"] > 0),
        S_GPT_DEF_LOCAL_NEGATION=out["M09_local_negation"],
        S_QUOTED_GPT_CUE=int(any(m.get("quotation_overlap") for m in grecord.get("matches", []) if m.get("family") in ("M01", "M02", "M03", "M04"))),
        S_PROMPT_IMAGINARY_OVERLAP=int(frame == "imaginary" and any(m.get("family") == "M01" and m.get("entry") == "imaginary" for m in grecord.get("matches", []))),
        S_TARGET_DEFINITION_DISAGREEMENT=int(out["gpt_definition_fable_E"] in ("GPT_ONLY", "FABLE_ONLY")),
        S_WORD_REPAIR=out["M32"],
        S_CATEGORY_WORDS=int(any(out["M31_" + k] for k in ("animal", "object", "idea"))),
    )
    tags = sorted(k for k, value in out.items() if k.startswith("S_") and value == 1)
    out["secondary_tags"] = "|".join(tags)
    out["secondary_tag_count"] = len(tags)
    evidence["gpt_matches"] = _excerpts(grecord, set(GPT_PRIMARY) | set(GPT_SECONDARY), redact=redact)
    evidence["fable_matches_normalized"] = fable_evidence(response, word, fable, redact=redact)
    evidence["registered_gpt"] = {k: out[k] for k in GPT_PRIMARY}
    evidence["registered_fable"] = {"E": e, "U": u, "N": n}
    return out, evidence


def normalized_codebook():
    return {"version": VERSION, "registered_primary_gpt": GPT_PRIMARY,
            "registered_fable": ("F_E", "F_U", "F_N"),
            "derived_response_classes": CLASSES,
            "exclusion_code": "X_UNUSABLE"}
