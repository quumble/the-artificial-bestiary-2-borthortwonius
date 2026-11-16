"""Declared word-cluster estimators and paired, source-stratified bootstrap.

This module operates on frozen exported codes, never on response text. All
returned estimates are proportions (multiply by 100 for percentage points).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from math import comb

import numpy as np

from inputs import CONDITIONS, MODELS, SOURCES

ALL_MODELS = tuple(sorted(MODELS))
ALL_CONDITIONS = tuple(sorted(CONDITIONS))
REAL = tuple(f"real_{c}" for c in ("animal", "object", "idea"))
TYPE = tuple(f"type_of_{c}" for c in ("animal", "object", "idea"))
IMAGINARY = tuple(f"imaginary_{c}" for c in ("animal", "object", "idea"))
PRESUP = REAL + TYPE
NONIMAGINARY = PRESUP + ("neutral",)


def row_value(row, arm, field):
    if field in ("E", "N", "U", "R"):
        return row[arm][field]
    if arm != "C":
        raise ValueError(f"Unsupported field for {arm}: {field}")
    z = row["zoned"]
    if field.startswith("type:"):
        return int(z["response_type"] == field.split(":", 1)[1])
    if field == "decline":
        return int(z["response_type"] in ("DECLINE_PLAIN", "DECLINE_WITH_POSSIBILITIES"))
    if field == "described_grounding":
        return int(row["C"]["E"] == 1 and z["grounding_claim"] == 1)
    if field == "described_mark":
        return int(row["C"]["E"] == 1 and z["marking_position"] != "none")
    if field == "described_late_mark":
        return int(row["C"]["E"] == 1 and z["marking_position"] == "after")
    return z[field]


def pair_agreement(values):
    """Unordered distinct-pair agreement, omitting unresolved repetitions."""
    resolved = [v for v in values if v is not None]
    denominator = comb(len(resolved), 2) if len(resolved) >= 2 else 0
    numerator = sum(comb(n, 2) for n in Counter(resolved).values() if n >= 2)
    return (numerator / denominator if denominator else np.nan,
            numerator, denominator, comb(len(values), 2))


def _mean(values):
    values = [v for v in values if np.isfinite(v)]
    return float(np.mean(values)) if values else np.nan


def _finite_number(value):
    return float(value) if np.isfinite(value) else None


@dataclass
class Prepared:
    selection: dict
    weights: dict
    numerator: dict
    denominator: dict
    support: dict


class Estimator:
    def __init__(self, rows, draws=10000, seed=20261115):
        if draws < 1:
            raise ValueError("draws must be positive")
        self.rows = rows
        self.draws = draws
        self.seed = seed
        self.words = {s: sorted({r["word"] for r in rows if r["source"] == s})
                      for s in sorted({r["source"] for r in rows})}
        self.cells = defaultdict(list)
        for row in rows:
            self.cells[(row["source"], row["word"], row["model"], row["condition"])].append(row)
        self.counts = {}
        rng = np.random.Generator(np.random.PCG64(seed))
        for source, words in self.words.items():
            n = len(words)
            indexes = rng.integers(0, n, size=(draws, n))
            counts = (indexes[:, :, None] == np.arange(n)[None, None, :]).sum(axis=1)
            self.counts[source] = np.vstack([np.ones(n, dtype=np.int64), counts])
        self.cache = {}

    def bootstrap_metadata(self):
        return {"draws": self.draws, "seed": self.seed, "rng": "numpy.Generator(PCG64)",
                "interval": "95% percentile, numpy.quantile(method='linear')",
                "source_order": list(self.words), "word_order": self.words,
                "shared_draws_sha256": hashlib.sha256(b"".join(
                    self.counts[s][1:].astype("<i8").tobytes() for s in self.words)).hexdigest(),
                "resampling_unit": "whole word within source/intent stratum",
                "endpoint_sampling": "fixed endpoints; no endpoint resampling"}

    def prepare(self, selection):
        canonical = json.dumps(selection, sort_keys=True)
        if canonical in self.cache:
            return self.cache[canonical]
        arm, field = selection["arm"], selection["field"]
        bank = selection.get("bank", "fresh")
        models = selection.get("models", ALL_MODELS)
        conditions = selection.get("conditions", ALL_CONDITIONS)
        sources = selection.get("sources", [s for s in self.words if SOURCES[s][0] == bank])
        if not models or not conditions or not sources:
            raise ValueError("Selections must have endpoints, conditions and sources")
        if len(set(models)) != len(models) or len(set(conditions)) != len(conditions):
            raise ValueError("Duplicate endpoint/condition in selection")
        if any(s not in self.words or SOURCES[s][0] != bank for s in sources):
            raise ValueError("Invalid source selection")
        if any(m not in MODELS for m in models) or any(c not in CONDITIONS for c in conditions):
            raise ValueError("Invalid endpoint or condition")
        weights = selection.get("source_weights", {s: 1 / len(sources) for s in sources})
        if set(weights) != set(sources) or any(w <= 0 for w in weights.values()) or not np.isclose(sum(weights.values()), 1):
            raise ValueError("Positive source weights must cover selected sources and sum to one")
        statistic = selection.get("statistic", "mean")
        if statistic not in ("mean", "pair_agreement"):
            raise ValueError(f"Unknown statistic: {statistic}")
        denominator_field = selection.get("denominator")
        if statistic == "pair_agreement" and denominator_field:
            raise ValueError("Pair agreement cannot have a conditional denominator")
        numerator, denominator = {}, {}
        support = {"responses": 0, "resolved_responses": 0, "null_responses": 0,
                   "cells": 0, "omitted_cells": 0, "endpoint_word_groups": 0,
                   "omitted_endpoint_word_groups": 0, "words_by_source": {},
                   "qualifying_responses": 0 if denominator_field else None}
        if statistic == "pair_agreement":
            support.update(matching_pairs=0, resolved_pairs=0, all_pairs=0)
        for source in sources:
            nums, dens = [], []
            for word in self.words[source]:
                model_nums, model_dens = [], []
                for model in models:
                    cell_nums, cell_dens = [], []
                    support["endpoint_word_groups"] += 1
                    for condition in conditions:
                        records = self.cells.get((source, word, model, condition), [])
                        values = [row_value(r, arm, field) for r in records]
                        den_values = [row_value(r, arm, denominator_field) for r in records] if denominator_field else [1] * len(records)
                        valid = [(v, d) for v, d in zip(values, den_values) if v is not None and d is not None]
                        support["responses"] += len(records)
                        support["resolved_responses"] += len(valid)
                        support["null_responses"] += len(records) - len(valid)
                        support["cells"] += 1
                        if statistic == "pair_agreement":
                            n, match, resolved, possible = pair_agreement(values)
                            d = 1.0 if np.isfinite(n) else np.nan
                            support["matching_pairs"] += match
                            support["resolved_pairs"] += resolved
                            support["all_pairs"] += possible
                        elif valid:
                            n = float(np.mean([v for v, _ in valid]))
                            d = float(np.mean([v for _, v in valid]))
                            if denominator_field:
                                if any(v not in (0, 1) or dv not in (0, 1) or v > dv for v, dv in valid):
                                    raise ValueError("Conditional numerator must be a subset of binary denominator")
                                support["qualifying_responses"] += sum(dv for _, dv in valid)
                        else:
                            n = d = np.nan
                        if not np.isfinite(n):
                            support["omitted_cells"] += 1
                        cell_nums.append(n)
                        cell_dens.append(d)
                    mn, md = _mean(cell_nums), _mean(cell_dens)
                    if not np.isfinite(mn):
                        support["omitted_endpoint_word_groups"] += 1
                    model_nums.append(mn)
                    model_dens.append(md)
                nums.append(_mean(model_nums))
                dens.append(_mean(model_dens))
            numerator[source], denominator[source] = np.array(nums), np.array(dens)
            support["words_by_source"][source] = {
                "planned": len(nums), "retained": int(np.isfinite(nums).sum()),
                "omitted": int((~np.isfinite(nums)).sum())}
        if statistic == "pair_agreement":
            support["pair_coverage"] = support["resolved_pairs"] / support["all_pairs"] if support["all_pairs"] else None
        prepared = Prepared(deepcopy(selection), dict(weights), numerator, denominator, support)
        self.cache[canonical] = prepared
        return prepared

    def _aggregate(self, prepared, masks):
        nums = np.zeros(self.draws + 1)
        dens = np.zeros(self.draws + 1)
        empty = np.zeros(self.draws + 1, dtype=bool)
        support = deepcopy(prepared.support)
        for source, weight in prepared.weights.items():
            keep = masks[source]
            counts = self.counts[source]
            available = counts @ keep.astype(float)
            empty |= available == 0
            with np.errstate(invalid="ignore", divide="ignore"):
                ns = counts @ np.where(keep, prepared.numerator[source], 0) / available
                ds = counts @ np.where(keep, prepared.denominator[source], 0) / available
            nums += weight * ns
            dens += weight * ds
            support["words_by_source"][source]["retained_after_within_word_pairing"] = int(keep.sum())
        zero_denominator = (~empty) & (dens == 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            result = nums / dens
        result[empty | zero_denominator] = np.nan
        return result, {"selection": prepared.selection, "source_weights": prepared.weights,
                        "support": support, "weighted_numerator": _finite_number(nums[0]),
                        "weighted_denominator": _finite_number(dens[0]),
                        "bootstrap_empty_stratum_draws": int(empty[1:].sum()),
                        "bootstrap_zero_denominator_draws": int(zero_denominator[1:].sum())}

    def evaluate(self, specification):
        prepared = [self.prepare(term["selection"]) for term in specification["terms"]]
        # Pair the sides of within-word contrasts within an instrument. Across
        # instruments preserve each estimator's available-case population.
        masks = []
        for p in prepared:
            masks.append({s: np.isfinite(p.numerator[s]) & np.isfinite(p.denominator[s]) for s in p.weights})
        for i, p in enumerate(prepared):
            for source in p.weights:
                for j, q in enumerate(prepared):
                    if p.selection["arm"] == q.selection["arm"] and source in q.weights:
                        masks[i][source] &= masks[j][source]
        values = np.zeros(self.draws + 1)
        components = []
        for term, p, mask in zip(specification["terms"], prepared, masks):
            component, details = self._aggregate(p, mask)
            values += term["coefficient"] * component
            details["coefficient"] = term["coefficient"]
            components.append(details)
        finite = values[1:][np.isfinite(values[1:])]
        point = _finite_number(values[0])
        interval = [float(v) for v in np.quantile(finite, [.025, .975], method="linear")] if point is not None and len(finite) else None
        result = {k: deepcopy(v) for k, v in specification.items() if k != "terms"}
        result.update(estimate=point, ci95=interval, bootstrap_defined=int(len(finite)),
                      bootstrap_undefined=int(self.draws - len(finite)), components=components,
                      units="proportion", interval_status=("not_estimable" if point is None else
                          "no_defined_draws" if not len(finite) else
                          "conditional_on_defined_draws" if len(finite) < self.draws else "all_draws_defined"))
        return result, values[1:]


def interpretation(arm_results, pairwise_results):
    """Direction and magnitude sensitivity are separate descriptive statements."""
    estimates = [r["estimate"] for r in arm_results]
    intervals = [r["ci95"] for r in arm_results]
    if any(x is None for x in estimates):
        direction = "not_estimable_in_all_arms"
    elif all(ci and ci[0] > 0 for ci in intervals):
        direction = "common_positive_direction"
    elif all(ci and ci[1] < 0 for ci in intervals):
        direction = "common_negative_direction"
    elif any(x < 0 for x in estimates) and any(x > 0 for x in estimates):
        direction = "mixed_point_estimate_directions"
    else:
        direction = "common_direction_not_established"
    gaps = [r["id"] for r in pairwise_results if r["ci95"] and (r["ci95"][0] > 0 or r["ci95"][1] < 0)]
    return {"status": "direction_robust" if direction in ("common_positive_direction", "common_negative_direction") else "direction_unresolved",
            "direction": direction,
            "mixed_point_estimate_directions": any(x is not None and x < 0 for x in estimates) and any(x is not None and x > 0 for x in estimates),
            "paired_differences_excluding_zero": gaps,
            "interpretation": "Exploratory unadjusted intervals; no equivalence or familywise claim."}
