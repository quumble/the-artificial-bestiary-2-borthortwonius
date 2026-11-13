#!/usr/bin/env python3
"""Fable descriptive supplement for The Artificial Bestiary 2.

Produces the descriptive summaries listed in section 7 of prereg/CLAUDE_PREREG.md
that the frozen analyzer (analyze_claude.py) did not generate.

Status: written on November 12, 2026, AFTER the confirmatory results were known.
The list of summaries was registered before collection; this code was not frozen.
Nothing here is confirmatory and no p-values are computed. Intervals are 95%
percentile intervals from a word bootstrap (10,000 draws, whole words resampled
within their source group) and are unadjusted.

Usage:
    python supplement/fable_descriptives.py --data data --orig path/to/the-artificial-bestiary
`--orig` is a checkout of quumble/the-artificial-bestiary (commit 7fec51a) and is
only needed for the historical stability check. Requires NumPy.
"""
import argparse, collections, csv, importlib.util, json, re, statistics, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SCORER = ROOT / "prereg" / "claude_scorer_v1_1.py"
DRAWS, SEED = 10000, 20261112
MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-sonnet-5-5", "claude-haiku-5-5",
          "gpt-5.4-mini", "gpt-5.4-nano", "gpt-6-sol", "gpt-6-luna"]
HISTORICAL = MODELS[:2] + MODELS[4:6]
FRAMES = ["neutral", "real", "type_of", "imaginary"]
CATS = ["animal", "object", "idea"]
CONDS = ["neutral"] + [f + "_" + c for f in FRAMES[1:] for c in CATS]
REAL = [c for c in CONDS if c.startswith("real_")]
TYPE = [c for c in CONDS if c.startswith("type_of_")]
IMAG = [c for c in CONDS if c.startswith("imaginary_")]
PRESUP = REAL + TYPE
OUT = {"U": "unmarked_description", "N": "nonrec_no_description", "E": "desc_form"}
EXPOSURE = re.compile(r"bestiary|chesterton", re.I)


def frame(cond):
    return "neutral" if cond == "neutral" else cond.rsplit("_", 1)[0]


def load_scorer():
    spec = importlib.util.spec_from_file_location("claude_scorer_v1_1", SCORER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_study(data, scorer):
    rows = []
    with open(data / "attempts.jsonl", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec["phase"] not in ("fresh", "known"):
                continue
            f, t = rec["fields"], rec["trial"]
            if not (f.get("valid") and f.get("terminal")) or f.get("truncated"):
                raise SystemExit("Unexpected ineligible or truncated record: " + t["trial_id"])
            text = f.get("response") or ""
            s = scorer.score_text(text, t["word"])
            rows.append({"batch": rec["phase"], "model": rec["model"], "word": t["word"],
                         "set": t["word_set"], "source": t.get("source_set_label") or t["word_set"],
                         "condition": t["condition"], "rep": t["rep"], "trial_id": t["trial_id"],
                         "text": text, **s, **{k: s[v] for k, v in OUT.items()}})
    return rows


def load_original(orig, scorer):
    """Original-study responses for the four historical models on the same eight words."""
    rows = []

    def add(model, word, cond, text):
        s = scorer.score_text(text or "", word)
        rows.append({"batch": "original", "model": model, "word": word, "condition": cond,
                     **{k: s[v] for k, v in OUT.items()}, "n_words": s["n_words"]})
    for name, model in (("Retest_nonanimal_nonsense/Results/retest.jsonl", "claude-sonnet-4-6"),
                        ("Haiku v3 Retest/Results/haiku_results.jsonl", "claude-haiku-4-5")):
        with open(orig / name, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    add(model, r["word"], r["condition"], r["response"])
    with open(orig / "GPT_Retest_1600_nanomini/gpt_full_800_nano_mini_results.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            add(r["model"], r["word"], r["condition"], r["output_text"])
    return rows


class Boot:
    """Word bootstrap. Statistics are functions of per-word values."""

    def __init__(self):
        self.rng = np.random.default_rng(SEED)

    def mean(self, values_by_group):
        """values_by_group: list of 1-D arrays, one per source group; words weighted equally."""
        allv = np.concatenate(values_by_group)
        draws = np.zeros(DRAWS)
        for v in values_by_group:
            idx = self.rng.integers(0, len(v), size=(DRAWS, len(v)))
            draws += v[idx].sum(axis=1)
        draws /= len(allv)
        return est(allv.mean(), draws)

    def diff(self, a, b):
        """Two independent word sets: mean(a) - mean(b)."""
        da = a[self.rng.integers(0, len(a), size=(DRAWS, len(a)))].mean(axis=1)
        db = b[self.rng.integers(0, len(b), size=(DRAWS, len(b)))].mean(axis=1)
        return est(a.mean() - b.mean(), da - db)


def est(point, draws):
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"estimate": round(float(point), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)]}


class Cells:
    """Per-word values: mean over conditions of each condition's mean over repetitions."""

    def __init__(self, rows):
        self.cell = collections.defaultdict(list)
        self.words = collections.defaultdict(dict)   # batch -> word -> source
        for r in rows:
            self.words[r["batch"]][r["word"]] = r.get("source", "")
            for k in ("U", "N", "E", "n_words", "any_context", "any_offer"):
                if k in r:
                    self.cell[(r["batch"], r["model"], r["word"], r["condition"], k)].append(r[k])

    def value(self, batch, model, word, conds, k):
        return float(np.mean([np.mean(self.cell[(batch, model, word, c, k)]) for c in conds]))

    def groups(self, batch, fn, sources=None):
        by = collections.defaultdict(list)
        for w, src in sorted(self.words[batch].items()):
            if sources is None or src in sources:
                by[src].append(fn(w))
        return [np.array(v) for _, v in sorted(by.items())]


def build(rows, original):
    boot, c, res = Boot(), Cells(rows), {}
    m = lambda b, fn, sources=None: boot.mean(c.groups(b, fn, sources))

    # 1. U, N, E for every model and condition, by frame, and by category
    t = []
    for b in ("fresh", "known"):
        for mod in MODELS:
            for label, conds in ([(x, [x]) for x in CONDS] + [("frame:" + f, [x for x in CONDS if frame(x) == f]) for f in FRAMES]
                                 + [("category:" + k, [x for x in CONDS if x.endswith("_" + k)]) for k in CATS]):
                t.append({"batch": b, "model": mod, "cell": label,
                          **{k: m(b, lambda w, k=k: c.value(b, mod, w, conds, k)) for k in OUT}})
    res["rates"] = t

    # 2. Every confirmatory contrast, model by model (fresh batch unless stated)
    t = []
    animal, claude, gpt = "fresh-animal-intent", "fresh-no-intent-claude", "fresh-no-intent-gpt"
    for mod in MODELS:
        v = lambda w, conds, k, b="fresh": c.value(b, mod, w, conds, k)
        row = {"model": mod}
        row["H1 E imaginary-real"] = m("fresh", lambda w: v(w, IMAG, "E") - v(w, REAL, "E"))
        row["H2 N type_of-real"] = m("fresh", lambda w: v(w, TYPE, "N") - v(w, REAL, "N"))
        g = lambda srcs, conds, k, b="fresh": np.concatenate(c.groups(b, lambda w: v(w, conds, k, b), srcs))
        row["H3 U animal-no_intent"] = boot.diff(g({animal}, PRESUP, "U"), g({claude, gpt}, PRESUP, "U"))
        pn = PRESUP + ["neutral"]
        strata = [boot.diff(g({ks}, pn, "N", "known"), g(fs, pn, "N"))
                  for ks, fs in (("known-animal-intent", {animal}), ("known-no-intent", {claude, gpt}))]
        row["H4 N known-fresh (intent-standardised; point only)"] = {"estimate": round((strata[0]["estimate"] + strata[1]["estimate"]) / 2, 4)}
        row["H5 U presupposition (level)"] = m("fresh", lambda w: v(w, PRESUP, "U"))
        row["H6 N claude_made-gpt_made"] = boot.diff(g({claude}, pn, "N"), g({gpt}, pn, "N"))
        t.append(row)
    res["contrasts_by_model"] = t

    # 3-5. Order, first-cue position, length, context requests and offers
    t = []
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["batch"], r["model"], frame(r["condition"]))].append(r)
    for (b, mod, f), rs in sorted(by.items(), key=lambda kv: (kv[0][0], MODELS.index(kv[0][1]), FRAMES.index(kv[0][2]))):
        order = collections.Counter(r["def_cue_order"] for r in rs)
        fracs = [r["first_cue_frac"] for r in rs if r["first_cue_frac"] != ""]
        conds = [x for x in CONDS if frame(x) == f]
        t.append({"batch": b, "model": mod, "frame": f, "n": len(rs),
                  "order": {k: round(order[k] / len(rs), 4) for k in ("definition_first", "cue_first", "definition_only", "cue_only", "neither")},
                  "first_cue_frac_median": round(statistics.median(fracs), 4) if fracs else None,
                  "words_mean": m(b, lambda w: c.value(b, mod, w, conds, "n_words")),
                  "words_median": statistics.median(r["n_words"] for r in rs),
                  "context_request": m(b, lambda w: c.value(b, mod, w, conds, "any_context")),
                  "offer": m(b, lambda w: c.value(b, mod, w, conds, "any_offer"))})
    res["form"] = t

    # 6. Reality-assertion wording inside unmarked descriptions under real_* conditions
    t, hits = [], []
    for b in ("fresh", "known"):
        for mod in MODELS:
            rs = [r for r in rows if r["batch"] == b and r["model"] == mod and r["condition"] in REAL]
            u = [r for r in rs if r["U"]]
            h = [r for r in u if r["any_reality"]]
            hits += [{"batch": b, "model": mod, "trial_id": r["trial_id"]} for r in h]
            t.append({"batch": b, "model": mod, "real_trials": len(rs), "unmarked": len(u), "with_reality_wording": len(h)})
    res["reality_wording"] = {"table": t, "trials": hits}

    # 7. Exposure strings
    hits = []
    for r in rows:
        ms = list(EXPOSURE.finditer(r["text"]))
        if ms:
            x = ms[0]
            hits.append({"batch": r["batch"], "model": r["model"], "trial_id": r["trial_id"],
                         "matches": sorted({y.group().lower() for y in ms}),
                         "context": " ".join(r["text"][max(0, x.start() - 70):x.end() + 50].split())})
    count = collections.Counter((h["batch"], h["model"], t) for h in hits for t in h["matches"])
    res["exposure_strings"] = {"pattern": EXPOSURE.pattern, "responses_searched": len(rows), "hits": len(hits),
                               "by_batch_model_term": [{"batch": k[0], "model": k[1], "term": k[2], "responses": v} for k, v in sorted(count.items())],
                               "trials": hits}

    # 8. Historical models: known batch now against the original study, same words, same scorer
    if original is not None:
        o, t = Cells(original), []
        for mod in HISTORICAL:
            for f in FRAMES:
                conds = [x for x in CONDS if frame(x) == f]
                for k in OUT:
                    words = sorted(o.words["original"])
                    old = np.array([o.value("original", mod, w, conds, k) for w in words])
                    new = np.array([c.value("known", mod, w, conds, k) for w in words])
                    t.append({"model": mod, "frame": f, "outcome": k, "original": round(float(old.mean()), 4),
                              "known_batch": round(float(new.mean()), 4), "change": boot.mean([new - old])})
        res["historical_stability"] = t
    return res


def fmt(e, signed=False):
    if e is None:
        return ""
    s = ("{:+.2f}" if signed else "{:.2f}").format(e["estimate"])
    if "ci95" in e:
        s += (" [{:+.2f}, {:+.2f}]" if signed else " [{:.2f}, {:.2f}]").format(*e["ci95"])
    return s


def table(head, body):
    return "\n".join(["| " + " | ".join(head) + " |", "| " + " | ".join(["---"] * len(head)) + " |"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in body]) + "\n"


def markdown(res, check):
    p = ["# Fable descriptive supplement\n",
         "**Post hoc. Not confirmatory.** These are the descriptive summaries listed in section 7 of "
         "`prereg/CLAUDE_PREREG.md`. The frozen analyzer did not produce them, so they were generated on "
         "November 12, 2026 by `supplement/fable_descriptives.py`, after the confirmatory results were known. "
         "The list of summaries was registered before collection. The code that makes them was not frozen.\n",
         "- Scorer: `prereg/claude_scorer_v1_1.py`, unchanged. " + check,
         "- U is a description form with no matched cue. N is nonrecognition with no description form. E is any description form. "
         "They are surface measures, not accuracy judgments.",
         "- Brackets are unadjusted 95% word-bootstrap intervals (10,000 draws, words resampled within source group). No tests are run.",
         "- Per-model intervals rest on 24 fresh or 8 known words and are wide. Absolute U rates are not comparable across providers.",
         "- Full per-condition and per-category tables are in `descriptives.json`.\n"]
    for b, title in (("fresh", "Fresh words"), ("known", "Previously published words")):
        p.append("## 1. U, N and E by model and framing: " + title + "\n")
        body = []
        for r in res["rates"]:
            if r["batch"] == b and r["cell"].startswith("frame:"):
                body.append([r["model"], r["cell"][6:]] + [fmt(r[k]) for k in OUT])
        p.append(table(["Model", "Framing", "U", "N", "E"], body))
    p.append("## 2. Confirmatory contrasts, model by model\n")
    p.append("Fresh batch, except H4, which uses both. H4 and H5 are contrasts between model groups, so each model's "
             "contribution is shown: for H4 the known-minus-fresh difference in N, for H5 the level of U.\n")
    keys = [k for k in res["contrasts_by_model"][0] if k != "model"]
    p.append(table(["Model"] + keys, [[r["model"]] + [fmt(r[k], signed=not k.startswith("H5")) for k in keys] for r in res["contrasts_by_model"]]))
    p.append("## 3. Definition and cue order, length, context requests and offers: fresh words\n")
    p.append("Order columns are shares of responses. \"First cue\" is the median position of the first cue as a fraction of the response, among responses with a cue.\n")
    body = []
    for r in res["form"]:
        if r["batch"] == "fresh":
            o = r["order"]
            body.append([r["model"], r["frame"]] + ["{:.2f}".format(o[k]) for k in o]
                        + ["" if r["first_cue_frac_median"] is None else "{:.2f}".format(r["first_cue_frac_median"]),
                           "{:.0f}".format(r["words_mean"]["estimate"]), "{:.0f}".format(r["words_median"]), fmt(r["context_request"]), fmt(r["offer"])])
    p.append(table(["Model", "Framing", "Def. first", "Cue first", "Def. only", "Cue only", "Neither", "First cue",
                    "Words, mean", "Words, median", "Context request", "Offer"], body))
    p.append("The known-batch version of this table is in `descriptives.json`.\n")
    p.append("## 4. Reality-assertion wording in unmarked descriptions under real framings\n")
    p.append(table(["Batch", "Model", "Real-framed trials", "Unmarked descriptions", "With reality wording"],
                   [[r["batch"], r["model"], r["real_trials"], r["unmarked"], r["with_reality_wording"]] for r in res["reality_wording"]["table"]]))
    e = res["exposure_strings"]
    p.append("## 5. Exposure strings\n")
    p.append("Responses containing \"bestiary\" or \"chesterton\", any case: **{} of {}**.\n".format(e["hits"], e["responses_searched"]))
    if e["trials"]:
        p.append(table(["Batch", "Model", "Term", "Responses"], [[x["batch"], x["model"], x["term"], x["responses"]] for x in e["by_batch_model_term"]]))
        fresh = sum(h["batch"] == "fresh" for h in e["trials"])
        p.append("The preregistration said any hit would be direct evidence of exposure. That was wrong about \"bestiary\", which is an "
                 "ordinary word for a book of creatures. {} of the {} hits are on fresh words, which were unpublished and cannot reflect "
                 "exposure to the original study. No response contains \"chesterton\". Every hit is listed with its surrounding text in "
                 "`descriptives.json`. On my reading of all of them, after the fact, each uses the word generically (for example, an offer "
                 "to write \"a fantasy bestiary entry\") and none refers to the original study. These hits are not evidence of exposure.\n"
                 .format(fresh, len(e["trials"])) if not any("chesterton" in h["matches"] for h in e["trials"]) else
                 "At least one response contains \"chesterton\". Read the listed trials in `descriptives.json` before interpreting.\n")
    if "historical_stability" in res:
        p.append("## 6. Historical models: known batch against the original study\n")
        p.append("Same eight words, same scorer, ten responses per word and condition in each run. The original runs used lower output caps (400 Anthropic, 700 OpenAI) and earlier dates. "
                 "This is a stability check, not a controlled comparison. Change is known batch minus original, with an interval over the eight words.\n")
        body = []
        for mod in HISTORICAL:
            for f in FRAMES:
                cells = {r["outcome"]: r for r in res["historical_stability"] if r["model"] == mod and r["frame"] == f}
                body.append([mod, f] + ["{:.2f} → {:.2f} ({})".format(cells[k]["original"], cells[k]["known_batch"], fmt(cells[k]["change"], True)) for k in OUT])
        p.append(table(["Model", "Framing", "U: original → now (change)", "N: original → now (change)", "E: original → now (change)"], body))
    return "\n".join(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    ap.add_argument("--orig", type=Path)
    ap.add_argument("--released-scores", type=Path, help="scores_v1.1.csv from the analysis release, for a cross-check")
    ap.add_argument("--out", type=Path, default=ROOT / "supplement" / "fable-descriptives")
    a = ap.parse_args()
    scorer = load_scorer()
    rows = load_study(a.data, scorer)
    if len(rows) != 16000:
        raise SystemExit("Expected 16,000 study responses, found %d" % len(rows))
    check = "Cross-check against the released scores was not run."
    if a.released_scores:
        with open(a.released_scores, encoding="utf-8", newline="") as fh:
            rel = {(r["batch"], r["model"], r["word"], r["condition"], int(r["rep"])): (int(r["U"]), int(r["N"]), int(r["E"])) for r in csv.DictReader(fh)}
        bad = sum(rel.get((r["batch"], r["model"], r["word"], r["condition"], r["rep"])) != (r["U"], r["N"], r["E"]) for r in rows)
        if bad or len(rel) != len(rows):
            raise SystemExit("U/N/E differ from the released scores in %d rows" % bad)
        check = "U, N and E here match the released `scores_v1.1.csv` on all 16,000 responses."
    original = load_original(a.orig, scorer) if a.orig else None
    res = build(rows, original)
    res = {"status": "post hoc descriptive supplement; not confirmatory; code not frozen", "scorer": scorer.SCORER_VERSION,
           "bootstrap": {"draws": DRAWS, "seed": SEED, "unit": "word, within source group"}, **res}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "descriptives.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    (a.out / "summary.md").write_text(markdown(res, check), encoding="utf-8", newline="\n")
    print("Written to", a.out)


if __name__ == "__main__":
    sys.exit(main())
