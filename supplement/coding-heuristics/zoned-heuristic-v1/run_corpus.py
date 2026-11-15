"""Score every response in the published export with the frozen zoned heuristic. Standard library only."""
import argparse, csv, json, hashlib
from collections import Counter, defaultdict
from pathlib import Path
from zoned_heuristic import score, VERSION

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True, type=Path); ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    rows, ev = [], (a.out / "evidence.jsonl").open("w", encoding="utf-8")
    for line in a.input.open(encoding="utf-8"):
        r = json.loads(line)
        cond = r["condition"]; framing = "neutral" if cond == "neutral" else cond.rsplit("_", 1)[0]
        s = score(r["response"], r["word"], framing)
        key = f"{r['batch']}|{r['model_requested']}|{r['trial_id']}"
        row = dict(key=key, batch=r["batch"], model=r["model_requested"], word=r["word"], source=r.get("source_set_label", ""), condition=cond, framing=framing, rep=r["rep"],
                   response_sha256=hashlib.sha256(r["response"].encode()).hexdigest(), response_type=s["response_type"], marking_position=s["marking_position"],
                   **s["fields"], **s["outcomes"], fragile="|".join(s["fragile"]))
        rows.append(row); ev.write(json.dumps(dict(key=key, counts=s["counts"], evidence=s["evidence"]), ensure_ascii=False) + "\n")
    ev.close()
    with (a.out / "response_codes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    num = [k for k, v in rows[0].items() if isinstance(v, int) and k != "rep"]
    def summarise(dims, name):
        g = defaultdict(list)
        for r in rows: g[tuple(r[d] for d in dims)].append(r)
        types = sorted({r["response_type"] for r in rows})
        with (a.out / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(list(dims) + ["n"] + num + types + ["any_fragile"])
            for k, rs in sorted(g.items()):
                c = Counter(r["response_type"] for r in rs)
                w.writerow(list(k) + [len(rs)] + [round(sum(r[x] for r in rs) / len(rs), 4) for x in num] + [round(c[t] / len(rs), 4) for t in types] + [round(sum(bool(r["fragile"]) for r in rs) / len(rs), 4)])
    summarise(("batch", "framing"), "rates_by_bank_framing.csv"); summarise(("batch", "model", "framing"), "rates_by_bank_model_framing.csv"); summarise(("batch", "word", "model", "condition"), "rates_by_word_cell.csv")
    json.dump(dict(version=VERSION, n=len(rows), input_sha256=hashlib.sha256(a.input.read_bytes()).hexdigest(), heuristic_sha256=hashlib.sha256(Path(__file__).with_name("zoned_heuristic.py").read_bytes()).hexdigest(),
                   response_types=Counter(r["response_type"] for r in rows), fragile_reasons=Counter(x for r in rows for x in r["fragile"].split("|") if x)), (a.out / "execution.json").open("w"), indent=1)
    print(len(rows), Counter(r["response_type"] for r in rows))

if __name__ == "__main__": main()
