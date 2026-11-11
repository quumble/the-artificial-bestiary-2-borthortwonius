#!/usr/bin/env python3
"""
Confirmatory analysis for the Claude Fable 5.2 preregistration, as amended by
prereg/CLAUDE_PREREG_AMENDMENT_1.md. Uses the frozen analysis runtime.

    python analyze_claude.py            # after both batches close

Validates the freeze and both batch closures, audits data/attempts.jsonl, then scores response text with
the frozen scorer (version 1.1, with version 1.0 alongside for comparison), and
writes analysis/claude/. No response text is written to any output.
"""
import argparse
import csv
import importlib.util
import json
import random
import statistics
import sys
from pathlib import Path
from collections import Counter

import analyze_bestiary as integrity
import run_bestiary as collector

ROOT = Path(__file__).resolve().parent
SEED = 20261110
PERMUTATIONS, BOOTSTRAPS = 100_000, 10_000
MIN_SHARE = 0.60          # share of planned trials a word needs, per model, to have a value
FLOOR = 0.02              # both arms below this: the test is reported and labelled uninformative
MARGIN = 0.10             # descriptive reading of the H4 interval only
REPS = {"fresh": 5, "known": 10}
REAL = ["real_animal", "real_object", "real_idea"]
TYPE = ["type_of_animal", "type_of_object", "type_of_idea"]
IMAG = ["imaginary_animal", "imaginary_object", "imaginary_idea"]
PRESUP = REAL + TYPE
PRESUP_NEUTRAL = PRESUP + ["neutral"]
OUTCOMES = {"U": "unmarked_description", "N": "nonrec_no_description", "E": "desc_form"}
HISTORICAL = ["claude-sonnet-4-6", "claude-haiku-4-5", "gpt-5.4-mini", "gpt-5.4-nano"]
CURRENT = ["claude-sonnet-5-5", "claude-haiku-5-5", "gpt-6-sol", "gpt-6-luna"]
ANTHROPIC = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
OPENAI = ["gpt-5.4-mini", "gpt-5.4-nano", "gpt-6-sol", "gpt-6-luna"]
ALL = HISTORICAL + CURRENT


def load_scorer(name, root=ROOT):
    spec = importlib.util.spec_from_file_location(name.replace(".", "_"), root / "prereg" / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------ data
def eligible(rec):
    return bool(rec.get("terminal") and rec.get("valid") and not rec.get("error")
                and not rec.get("protocol_violation") and not rec.get("issue"))


def load_inputs(root):
    """Validate before reading any attempt/response text; return audited planned and retained slots."""
    status = root / "data" / "collection-status.json"
    closed = json.loads(status.read_text(encoding="utf-8")) if status.exists() else {}
    if not all(isinstance(closed.get(batch), dict) and closed[batch].get("closed_utc") for batch in REPS):
        raise ValueError("Both batches must finish or be formally stopped before scoring.")
    manifest = json.loads((root / "data" / "freeze.json").read_text(encoding="utf-8"))
    if manifest.get("protocol") != "gpt-v1+claude-v1.1":
        raise ValueError("Claude analysis requires the frozen gpt-v1+claude-v1.1 protocol.")
    required = set(collector.CLAUDE_FILES) | {
        "run_bestiary.py", "bestiary_scorer.py", "analyze_bestiary.py", "requirements-analysis.txt",
        "docs/gpt-proposal/inventories-gpt-v1.json", "prereg/CLAUDE_PREREG.md", "prereg/claude_scorer.py",
    }
    missing = required - set(manifest.get("code_hashes", {}))
    if missing:
        raise ValueError("Required sources absent from freeze: " + ", ".join(sorted(missing)))
    integrity.validate_manifest(manifest, root)
    if root.resolve() != ROOT.resolve():
        # --root can locate another copy of the data, but the code actually running
        # must also match the freeze, including the imported integrity helpers.
        integrity.validate_manifest(manifest, ROOT)
    path = root / "data" / "attempts.jsonl"
    if not path.exists():
        raise ValueError("The attempt ledger export is missing; regenerate it with run_bestiary.py export.")
    attempts = integrity.read_jsonl(path)
    planned, selected, exclusions, _ = integrity.select_records(manifest, attempts)
    reasons = Counter(item["reason"] for item in exclusions)
    by_id = {attempt["attempt_id"]: attempt for attempt in attempts}
    grouped = Counter()
    for item in exclusions:
        batch, model, _ = item["slot"]
        trial = planned.get(tuple(item["slot"])) or by_id[item["attempt_id"]].get("trial") or {}
        grouped[(batch, model, trial.get("condition"), item["reason"])] += 1
    audit = {"records": sum(a["phase"] in REPS for a in attempts),
             "ineligible": len(exclusions) - reasons["duplicate_terminal"],
             "duplicates": reasons["duplicate_terminal"], "planned_slots": len(planned),
             "retained_slots": len(selected), "exclusions": exclusions,
             "exclusions_by_model_condition": [dict(batch=b, model=m, condition=c, reason=why, count=n)
                                                for (b, m, c, why), n in grouped.items()]}
    return manifest, planned, selected, audit


def load_rows(root, scorer, inputs=None):
    """Score only the earliest eligible terminal attempt in each validated frozen slot."""
    _, planned, selected, audit = inputs if inputs is not None else load_inputs(root)
    rows = []
    for key, attempt in selected.items():
        batch, model, _ = key
        trial, fields = planned[key], attempt["fields"]
        score = scorer.score_text(fields.get("response") or "", trial["word"])
        rows.append({"batch": batch, "model": model, "word": trial["word"],
                     "word_set": trial["word_set"], "source": trial.get("source_set_label") or trial["word_set"],
                     "condition": trial["condition"], "rep": trial["rep"], "truncated": bool(fields.get("truncated")),
                     **{k: score[v] for k, v in OUTCOMES.items()}, "n_words": score["n_words"]})
    return rows, audit


class Data:
    def __init__(self, rows, manifest, include_truncated=False):
        self.cells, self.words = {}, {}
        self.per_model, self.planned_per_model = {}, {}
        for batch, models in manifest["batches"].items():
            for model, trials in models.items():
                self.planned_per_model[(batch, model)] = len(trials)
                for trial in trials:
                    self.words.setdefault(batch, {})[trial["word"]] = (
                        trial["word_set"], trial.get("source_set_label") or trial["word_set"])
        for r in rows:
            if r["truncated"] and not include_truncated:
                continue
            self.cells.setdefault((r["batch"], r["model"], r["word"], r["condition"]), []).append(r)
            self.per_model[(r["batch"], r["model"])] = self.per_model.get((r["batch"], r["model"]), 0) + 1

    def models_in(self, batch, models):
        """Models with at least MIN_SHARE of the batch's planned slots usable."""
        return [m for m in models if self.planned_per_model.get((batch, m), 0)
                and self.per_model.get((batch, m), 0) >= MIN_SHARE * self.planned_per_model[(batch, m)]]

    def model_eligibility(self):
        return [dict(batch=batch, model=model, planned=planned,
                     eligible=self.per_model.get((batch, model), 0), minimum_share=MIN_SHARE,
                     eligible_share=self.per_model.get((batch, model), 0) / planned if planned else None,
                     included=model in self.models_in(batch, [model]))
                for (batch, model), planned in sorted(self.planned_per_model.items())]

    def word_model(self, batch, model, word, conditions, outcome):
        means, total = [], 0
        for c in conditions:
            cell = self.cells.get((batch, model, word, c))
            if not cell:
                return None                               # every condition in the set must be observed
            means.append(statistics.fmean(r[outcome] for r in cell))
            total += len(cell)
        if total < MIN_SHARE * len(conditions) * REPS[batch]:
            return None
        return statistics.fmean(means)                    # conditions weighted equally

    def word_group(self, batch, models, word, conditions, outcome):
        values = [self.word_model(batch, m, word, conditions, outcome) for m in models]
        if not values or any(v is None for v in values):
            return None                                   # a word needs every model in the group
        return statistics.fmean(values)                   # models weighted equally


# ------------------------------------------------------------------ tests
def p_value(observed, draws):
    return (1 + sum(abs(d) >= abs(observed) - 1e-12 for d in draws)) / (1 + len(draws))


def percentile(sorted_values, q):
    return sorted_values[min(len(sorted_values) - 1, max(0, int(round(q * (len(sorted_values) - 1)))))]


def interval(draws):
    draws = sorted(draws)
    return [percentile(draws, 0.025), percentile(draws, 0.975)]


def paired_test(diffs, label, permutations, bootstraps):
    rng = random.Random("%s|%s|perm" % (SEED, label))
    observed = statistics.fmean(diffs)
    perm = [statistics.fmean(d if rng.random() < 0.5 else -d for d in diffs) for _ in range(permutations)]
    rng = random.Random("%s|%s|boot" % (SEED, label))
    boot = [statistics.fmean(rng.choices(diffs, k=len(diffs))) for _ in range(bootstraps)]
    return observed, p_value(observed, perm), interval(boot)


def strata_stat(strata):
    return statistics.fmean(statistics.fmean(a) - statistics.fmean(b) for a, b in strata)


def stratified_test(strata, label, permutations, bootstraps):
    """strata: list of (group A values, group B values). Statistic: equal-weight mean of A-minus-B differences."""
    rng = random.Random("%s|%s|perm" % (SEED, label))
    observed = strata_stat(strata)
    perm = []
    for _ in range(permutations):
        shuffled = []
        for a, b in strata:
            pool = a + b
            rng.shuffle(pool)
            shuffled.append((pool[:len(a)], pool[len(a):]))
        perm.append(strata_stat(shuffled))
    rng = random.Random("%s|%s|boot" % (SEED, label))
    boot = [strata_stat([(rng.choices(a, k=len(a)), rng.choices(b, k=len(b))) for a, b in strata]) for _ in range(bootstraps)]
    return observed, p_value(observed, perm), interval(boot)


def holm(pvalues):
    order = sorted((p, k) for k, p in pvalues.items() if p is not None)
    adjusted, running = {}, 0.0
    for rank, (p, k) in enumerate(order):
        running = max(running, min(1.0, (len(order) - rank) * p))
        adjusted[k] = running
    return adjusted


def confirmatory(data, permutations=PERMUTATIONS, bootstraps=BOOTSTRAPS):
    fresh = data.words.get("fresh", {})
    known = data.words.get("known", {})
    results = {}

    def groups(batches, wanted):
        kept = [m for m in wanted if all(m in data.models_in(b, wanted) for b in batches)]
        return kept, [m for m in wanted if m not in kept]

    def finish(key, title, observed, p, ci, arms, n, dropped, missing_models, note=""):
        floor = all(a is not None and abs(a) < FLOOR for a in arms.values()) if arms else False
        results[key] = dict(title=title, estimate=observed, p=p, ci95=ci, arms=arms, n_words=n, dropped_words=len(dropped),
                            models_missing=missing_models, uninformative_floor=floor, note=note)

    def untestable(key, title, why, missing_models=()):
        results[key] = dict(title=title, estimate=None, p=None, ci95=None, arms={}, n_words=0, dropped_words=0,
                            models_missing=list(missing_models), uninformative_floor=False, note="untested: " + why)

    def paired(key, title, models_wanted, outcome, cond_a, cond_b=None, models_b=None):
        """Either two condition sets on one model group, or one condition set on two model groups."""
        ga, miss_a = groups(["fresh"], models_wanted)
        gb, miss_b = groups(["fresh"], models_b) if models_b else (ga, [])
        if not ga or not gb:
            return untestable(key, title, "no usable model in a required group", miss_a + miss_b)
        diffs, arm_a, arm_b, dropped = [], [], [], []
        for w in sorted(fresh):
            a = data.word_group("fresh", ga, w, cond_a, outcome)
            b = data.word_group("fresh", gb, w, cond_b or cond_a, outcome)
            if a is None or b is None:
                dropped.append(w)
                continue
            diffs.append(a - b); arm_a.append(a); arm_b.append(b)
        if len(diffs) < 2:
            return untestable(key, title, "fewer than two usable words", miss_a + miss_b)
        observed, p, ci = paired_test(diffs, key, permutations, bootstraps)
        finish(key, title, observed, p, ci, {"first": statistics.fmean(arm_a), "second": statistics.fmean(arm_b)},
               len(diffs), dropped, miss_a + miss_b)

    paired("H1", "E: imaginary minus real, all models", ALL, "E", IMAG, REAL)
    paired("H2", "N: type-of minus real, OpenAI models", OPENAI, "N", TYPE, REAL)
    paired("H5", "U under presupposition: current minus historical models", CURRENT, "U", PRESUP, models_b=HISTORICAL)

    # H3: animal-intent words against no-intent words, U under presupposition, all models
    g, miss = groups(["fresh"], ALL)
    values = {w: data.word_group("fresh", g, w, PRESUP, "U") for w in sorted(fresh)} if g else {}
    a = [v for w, v in values.items() if v is not None and fresh[w][0] == "fresh-animal-intent"]
    b = [v for w, v in values.items() if v is not None and fresh[w][0] == "fresh-no-intent"]
    if len(a) >= 2 and len(b) >= 2:
        observed, p, ci = stratified_test([(a, b)], "H3", permutations, bootstraps)
        finish("H3", "U under presupposition: animal-intent minus no-intent words", observed, p, ci,
               {"first": statistics.fmean(a), "second": statistics.fmean(b)}, len(a) + len(b),
               [w for w, v in values.items() if v is None], miss)
    else:
        untestable("H3", "U under presupposition: animal-intent minus no-intent words", "too few usable words", miss)

    # H4: (current minus historical) on N, known words against fresh words, standardised over intent
    title = "N: generation contrast, known minus fresh words, intent-standardised"
    cur, miss_c = groups(["fresh", "known"], CURRENT)
    his, miss_h = groups(["fresh", "known"], HISTORICAL)
    if not known:
        untestable("H4", title, "known-word batch not collected")
    elif not cur or not his:
        untestable("H4", title, "needs a historical and a current model in both batches", miss_c + miss_h)
    else:
        strata, dropped, arms = [], [], {}
        for intent in ("animal-intent", "no-intent"):
            pair = []
            for batch, bank in (("known", known), ("fresh", fresh)):
                vals = []
                for w in sorted(bank):
                    if not bank[w][0].endswith("-" + intent):
                        continue
                    c = data.word_group(batch, cur, w, PRESUP_NEUTRAL, "N")
                    h = data.word_group(batch, his, w, PRESUP_NEUTRAL, "N")
                    if c is None or h is None:
                        dropped.append(w)
                    else:
                        vals.append(c - h)
                pair.append(vals)
            strata.append(tuple(pair))
        if all(len(k) >= 2 and len(f) >= 2 for k, f in strata):
            observed, p, ci = stratified_test(strata, "H4", permutations, bootstraps)
            arms = {"first": statistics.fmean(statistics.fmean(k) for k, _ in strata),
                    "second": statistics.fmean(statistics.fmean(f) for _, f in strata)}
            inside = ci[0] > -MARGIN and ci[1] < MARGIN
            finish("H4", title, observed, p, ci, {}, sum(len(k) + len(f) for k, f in strata), dropped, miss_c + miss_h,
                   note="descriptive only: 95%% interval %s the +/-%.2f margin; arm means are differences, so the floor rule does not apply"
                        % ("inside" if inside else "not inside", MARGIN))
            results["H4"]["arms"] = arms
        else:
            untestable("H4", title, "too few usable words in a stratum", miss_c + miss_h)

    # H6: authorship by model family, N, fresh no-intent words
    title = "N: (Anthropic minus OpenAI models), Claude-made minus GPT-made words"
    ant, miss_a = groups(["fresh"], ANTHROPIC)
    oai, miss_o = groups(["fresh"], OPENAI)
    made = {"claude": [], "gpt": []}
    dropped = []
    if ant and oai:
        for w in sorted(fresh):
            source = fresh[w][1]
            author = "claude" if source.endswith("-claude") else "gpt" if source.endswith("-gpt") else None
            if author is None:
                continue
            x = data.word_group("fresh", ant, w, PRESUP_NEUTRAL, "N")
            y = data.word_group("fresh", oai, w, PRESUP_NEUTRAL, "N")
            if x is None or y is None:
                dropped.append(w)
            else:
                made[author].append(x - y)
    if len(made["claude"]) >= 2 and len(made["gpt"]) >= 2:
        observed, p, ci = stratified_test([(made["claude"], made["gpt"])], "H6", permutations, bootstraps)
        finish("H6", title, observed, p, ci, {}, len(made["claude"]) + len(made["gpt"]), dropped, miss_a + miss_o,
               note="arm means are differences, so the floor rule does not apply")
        results["H6"]["arms"] = {"first": statistics.fmean(made["claude"]), "second": statistics.fmean(made["gpt"])}
    else:
        untestable("H6", title, "needs both author sets and both providers", miss_a + miss_o)

    # The family is always the six registered tests. An untestable one keeps its place with p = 1
    # for the adjustment, so the others are not corrected more leniently because it dropped out.
    adjusted = holm({k: (v["p"] if v["p"] is not None else 1.0) for k, v in results.items()})
    for k, v in results.items():
        v["p_holm"] = adjusted.get(k) if v["p"] is not None else None
        v["holm_family_size"] = len(results)
        v["confirmed_at_0.05"] = bool(v["p_holm"] is not None and v["p_holm"] < 0.05 and not v["uninformative_floor"])
    return dict(sorted(results.items()))


def descriptive(rows):
    table = {}
    for r in rows:
        key = (r["batch"], r["model"], r["condition"])
        t = table.setdefault(key, {"n": 0, "truncated": 0, "U": 0, "N": 0, "E": 0})
        t["n"] += 1
        t["truncated"] += r["truncated"]
        for o in OUTCOMES:
            t[o] += r[o]
    return [dict(batch=b, model=m, condition=c, n=t["n"], truncated=t["truncated"],
                 **{o: round(t[o] / t["n"], 4) for o in OUTCOMES}) for (b, m, c), t in sorted(table.items())]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--permutations", type=int, default=PERMUTATIONS)
    ap.add_argument("--bootstraps", type=int, default=BOOTSTRAPS)
    args = ap.parse_args()
    root = Path(args.root)
    inputs = load_inputs(root)
    manifest = inputs[0]
    out = root / "analysis" / "claude"
    out.mkdir(parents=True, exist_ok=True)
    report = {"registered": {"permutations": PERMUTATIONS, "bootstraps": BOOTSTRAPS, "seed": SEED},
              "used": {"permutations": args.permutations, "bootstraps": args.bootstraps},
              "known_batch_closed": True, "protocol": manifest["protocol"],
              "manifest_sha256": manifest["manifest_sha256"],
              "attempts_sha256": collector.digest((root / "data" / "attempts.jsonl").read_bytes())}
    for version, filename in (("v1.1", "claude_scorer_v1_1.py"), ("v1.0", "claude_scorer.py")):
        rows, audit = load_rows(root, load_scorer(filename, root), inputs=inputs)
        primary = Data(rows, manifest)
        sensitivity = Data(rows, manifest, include_truncated=True)
        block = {"audit": audit, "scorer_file": "prereg/" + filename,
                 "scorer_sha256": collector.digest((root / "prereg" / filename).read_bytes()),
                 "model_eligibility_primary": primary.model_eligibility(),
                 "model_eligibility_truncated_included": sensitivity.model_eligibility(),
                 "primary": confirmatory(primary, args.permutations, args.bootstraps),
                 "sensitivity_truncated_included": confirmatory(sensitivity, args.permutations, args.bootstraps),
                 "by_model_condition": descriptive(rows)}
        report[version] = block
        with open(out / ("scores_%s.csv" % version), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["batch"])
            w.writeheader()
            w.writerows(rows)
    (out / "claude_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["Claude Fable 5.2 confirmatory family (scorer v1.1, truncated responses excluded)", ""]
    for key, r in report["v1.1"]["primary"].items():
        if r["estimate"] is None:
            lines.append("%s  %s\n    %s" % (key, r["title"], r["note"]))
            continue
        lines.append("%s  %s" % (key, r["title"]))
        lines.append("    estimate %+.3f   95%% interval [%+.3f, %+.3f]   p %.5f   Holm p %.5f   words %d%s%s"
                     % (r["estimate"], r["ci95"][0], r["ci95"][1], r["p"], r["p_holm"], r["n_words"],
                        "   FLOOR: uninformative" if r["uninformative_floor"] else "",
                        "   models missing: " + ", ".join(r["models_missing"]) if r["models_missing"] else ""))
        if r["note"]:
            lines.append("    " + r["note"])
    (out / "claude_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nWritten to", out)


if __name__ == "__main__":
    main()
