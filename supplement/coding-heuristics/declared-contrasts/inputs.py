"""Load and validate the three frozen heuristic exports from published files.

No extraction, private intermediate files, response text, or model calls are
required. The original records remain available for reproducing old summaries.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

MODELS = {
    "claude-sonnet-4-6": ("Anthropic", "historical"),
    "claude-haiku-4-5": ("Anthropic", "historical"),
    "claude-sonnet-5-5": ("Anthropic", "current"),
    "claude-haiku-5-5": ("Anthropic", "current"),
    "gpt-5.4-mini": ("OpenAI", "historical"),
    "gpt-5.4-nano": ("OpenAI", "historical"),
    "gpt-6-sol": ("OpenAI", "current"),
    "gpt-6-luna": ("OpenAI", "current"),
}
SOURCES = {
    "fresh-animal-intent": ("fresh", 8),
    "fresh-no-intent-claude": ("fresh", 8),
    "fresh-no-intent-gpt": ("fresh", 8),
    "known-animal-intent": ("known", 4),
    "known-no-intent": ("known", 4),
}
CONDITIONS = {"neutral"} | {
    f"{frame}_{category}"
    for frame in ("real", "type_of", "imaginary")
    for category in ("animal", "object", "idea")
}
C_BINARY = {
    "description_asserted", "description_hypothetical", "description_any",
    "nonrec_personal", "nonrec_external", "refusal_to_invent",
    "possibility_list", "context_request", "offer", "mark_fiction",
    "mark_construction", "mark_interpretation", "mark_hedge",
    "grounding_claim", "substitute_description", "nonrec_any",
    "fiction_mark_is_prompt_echo", "E_description",
    "N_nonrecognition_without_description", "U_unmarked_description",
    "U_bare_description", "U_unmarked_discounting_prompt_echo",
}


@dataclass
class Dataset:
    rows: list[dict]
    A: dict[str, dict]
    B: dict[str, dict]
    C: dict[str, dict]
    provenance: dict


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _binary(value, label: str, *, nullable: bool = False):
    if nullable and value is None:
        return None
    _require(value in (0, 1, "0", "1"), f"Invalid binary {label}: {value!r}")
    return int(value)


def index_unique(records, key, name: str) -> dict:
    """Index records without silently overwriting a repeated trial."""
    result = {}
    for record in records:
        trial = key(record)
        _require(trial not in result, f"Duplicate {name} key: {trial}")
        result[trial] = record
    return result


def load_inputs(repo_root: Path) -> Dataset:
    root = Path(repo_root).resolve()
    base = root / "supplement/coding-heuristics"
    hashes = {}

    def read(relative: str) -> bytes:
        blob = (base / relative).read_bytes()
        hashes[relative] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
        return blob

    archive_name = "archives/Bestiary_2_Context_Heuristic_v1.zip"
    archive_checksums = dict(line.split(None, 1)[::-1] for line in
                             read("archives/SHA256SUMS.txt").decode("utf-8").splitlines() if line.strip())
    archive_bytes = read(archive_name)
    _require(hashlib.sha256(archive_bytes).hexdigest() == archive_checksums[Path(archive_name).name],
             "Context archive does not match published SHA256SUMS.txt")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = [n for n in archive.namelist() if n.endswith("/results/response_codes.jsonl")]
        _require(len(members) == 1, "Context archive needs exactly one response_codes.jsonl")
        member = members[0]
        blob = archive.read(member)
        hashes[f"{archive_name}!{member}"] = {
            "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)
        }
        A = index_unique((json.loads(line) for line in blob.splitlines() if line),
                         lambda r: "|".join(r["key"]), "A")
    B = index_unique(csv.DictReader(io.StringIO(read(
        "mechanical-coding-heuristic-v1/run-2026-11-15_claude-fable-5-2/coded_responses.csv"
    ).decode("utf-8"))), lambda r: r["row_id"], "B")
    c_blob = read("zoned-heuristic-v1/results/response_codes.csv")
    c_archive_name = "archives/Bestiary_2_Zoned_Heuristic_v1.zip"
    c_archive_blob = read(c_archive_name)
    _require(hashlib.sha256(c_archive_blob).hexdigest() == archive_checksums[Path(c_archive_name).name],
             "Zoned archive does not match published SHA256SUMS.txt")
    with zipfile.ZipFile(io.BytesIO(c_archive_blob)) as archive:
        members = [n for n in archive.namelist() if n.endswith("/results/response_codes.csv")]
        _require(len(members) == 1, "Zoned archive needs exactly one response_codes.csv")
        _require(archive.read(members[0]) == c_blob, "Expanded zoned codes differ from frozen archive")
    C = index_unique(csv.DictReader(io.StringIO(c_blob.decode("utf-8"))), lambda r: r["key"], "C")
    _require(len(A) == 16000, f"Expected 16000 rows; found {len(A)}")
    _require(set(A) == set(B) == set(C), "The three exports have different trial keys")

    rows = []
    cell_reps = defaultdict(list)
    source_words = defaultdict(set)
    word_sources = defaultdict(set)
    for key in sorted(A):
        a, b, c = A[key], B[key], C[key]
        model = a["model"]
        _require(model in MODELS, f"Unexpected model: {model}")
        provider, generation = MODELS[model]
        _require(a["source"] in SOURCES, f"Unexpected source: {a['source']}")
        _require(a["batch"] == SOURCES[a["source"]][0], f"Source/bank mismatch: {key}")
        for field in ("batch", "model", "word", "condition"):
            _require(a[field] == b[field] == c[field], f"Metadata mismatch {field}: {key}")
        _require(a["source"] == b["source_set_label"] == c["source"], f"Source mismatch: {key}")
        _require(a["framing"] == b["frame"] == c["framing"], f"Framing mismatch: {key}")
        _require(a["response_sha256"] == c["response_sha256"], f"Response hash mismatch: {key}")
        _require(len(a["response_sha256"]) == 64, f"Invalid response hash: {key}")
        _require(provider == b["provider_group"] and generation == b["generation"],
                 f"Endpoint-group mismatch: {key}")
        rep = int(a["rep"])
        _require(rep == int(b["rep"]) == int(c["rep"]), f"Repetition mismatch: {key}")
        category = a["category"]
        _require((category or "none") == b["category"], f"Category mismatch: {key}")
        condition = a["condition"]
        _require(condition in CONDITIONS, f"Unknown condition: {key}")
        expected_condition = "neutral" if category is None else f"{a['framing']}_{category}"
        _require(condition == expected_condition, f"Condition fields disagree: {key}")
        _require(key == f"{a['batch']}|{model}|{a['batch']}|{a['word']}|{condition}|{rep:02d}",
                 f"Noncanonical trial key: {key}")
        av = a["values"]
        va = {out: _binary(av[field], f"A.{field}:{key}", nullable=True)
              for out, field in {"E": "description_produced", "N": "nonrecognition_without_description",
                                 "U": "unmarked_target_description"}.items()}
        personal = _binary(av["knowledge_limit"], f"A.knowledge_limit:{key}")
        external = _binary(av["external_negative"], f"A.external_negative:{key}")
        va["R"] = int(personal == 1 or external == 1)
        vb = {out: _binary(b[field], f"B.{field}:{key}") for out, field in
              {"E": "F_E", "N": "F_N", "U": "F_U", "R": "F_nonrec"}.items()}
        zoned = dict(c)
        for field in C_BINARY:
            zoned[field] = _binary(c[field], f"C.{field}:{key}")
        zoned["rep"] = rep
        vc = {out: zoned[field] for out, field in
              {"E": "E_description", "N": "N_nonrecognition_without_description",
               "U": "U_unmarked_description", "R": "nonrec_any"}.items()}
        rows.append({"key": key, "batch": a["batch"], "model": model,
                     "word": a["word"], "source": a["source"], "condition": condition,
                     "framing": a["framing"], "category": category, "rep": rep,
                     "provider": provider, "generation": generation,
                     "A": va, "B": vb, "C": vc, "zoned": zoned})
        cell_reps[(a["batch"], model, a["word"], condition)].append(rep)
        source_words[a["source"]].add(a["word"])
        word_sources[a["word"]].add(a["source"])
    _require(Counter(r["batch"] for r in rows) == {"fresh": 9600, "known": 6400}, "Wrong bank counts")
    _require(set(source_words) == set(SOURCES), "Missing source stratum")
    _require(len(word_sources) == 32 and all(len(v) == 1 for v in word_sources.values()),
             "Expected 32 unique words, each in one source")
    for source, (_, n_words) in SOURCES.items():
        _require(len(source_words[source]) == n_words, f"Wrong word count for {source}")
    _require(len(cell_reps) == 32 * 8 * 10, "Incomplete word/endpoint/condition panel")
    for cell, repetitions in cell_reps.items():
        n_reps = 5 if cell[0] == "fresh" else 10
        _require(sorted(repetitions) == list(range(1, n_reps + 1)), f"Invalid repetition panel: {cell}")
    provenance = {
        "files": hashes,
        "validation": {
            "rows": len(rows), "banks": dict(Counter(r["batch"] for r in rows)),
            "words": 32, "endpoints": 8, "conditions": 10, "complete_cells": len(cell_reps),
            "source_word_counts": {s: len(w) for s, w in sorted(source_words.items())},
            "joined_keys_equal": True, "A_C_response_hashes_equal": True,
            "used_archives_match_published_checksums": True, "C_export_matches_archive": True,
            "metadata_equal": True,
            "null_outcomes_A": {out: sum(r["A"][out] is None for r in rows) for out in ("E", "N", "U", "R")},
        },
        "crosswalk": {
            "A": {"E": "description_produced", "N": "nonrecognition_without_description",
                  "U": "unmarked_target_description", "R": "knowledge_limit OR external_negative"},
            "B": {"E": "F_E", "N": "F_N", "U": "F_U", "R": "F_nonrec"},
            "C": {"E": "E_description", "N": "N_nonrecognition_without_description",
                  "U": "U_unmarked_description", "R": "nonrec_any"},
        },
    }
    return Dataset(rows=rows, A=A, B=B, C=C, provenance=provenance)
