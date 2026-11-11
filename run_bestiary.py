#!/usr/bin/env python3
"""Durable Bestiary collector. Standard library only. Never prints response text."""
import argparse
import concurrent.futures as futures
import contextlib
import datetime as dt
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sqlite3
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
CAP, SEED, USD = 1024, 20261110, 1_000_000_000
BUDGET = 20 * USD
REPS = {"fresh": 5, "known": 10}
EXPECTED_HASH = {"fresh": "ba900e410b907a8dc02cab7835a3aaace5473eea72402d40b5f4b0ad209209e3", "known": "ee338d944aa0c6e2de68ce18c8a38af1eb3de34790ab87828f2afe6f9eb0dfe2"}
REALITIES, CATEGORIES = ["real", "imaginary", "type of"], ["animal", "object", "idea"]
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}
PREFLIGHT = "Reply with the single word: ready."
MODELS = [
    dict(id="claude-sonnet-4-6", provider="anthropic", role="historical", price_in=3, price_out=15, params={"temperature": 1.0}),
    dict(id="claude-haiku-4-5", provider="anthropic", role="historical", price_in=1, price_out=5, params={"temperature": 1.0}),
    dict(id="claude-sonnet-5-5", provider="anthropic", role="current", price_in=2, price_out=10, params={"thinking": {"type": "between_tools"}}),
    dict(id="claude-haiku-5-5", provider="anthropic", role="current", price_in=.1, price_out=.5, params={"thinking": {"type": "disabled"}}),
    dict(id="gpt-5.4-mini", provider="openai", role="historical", price_in=.75, price_out=4.5, params={"reasoning": {"effort": "none"}, "temperature": 1.0, "top_p": 1.0}),
    dict(id="gpt-5.4-nano", provider="openai", role="historical", price_in=.2, price_out=1.25, params={"reasoning": {"effort": "none"}, "temperature": 1.0, "top_p": 1.0}),
    dict(id="gpt-6-sol", provider="openai", role="current", price_in=2, price_out=10, params={"reasoning": {"effort": "none"}, "temperature": 1.0}),
    dict(id="gpt-6-luna", provider="openai", role="current", price_in=.1, price_out=.5, params={"reasoning": {"effort": "none"}, "temperature": 1.0}),
]
BY_ID = {m["id"]: m for m in MODELS}
KEY_NAMES = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}


class StudyError(RuntimeError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


@contextlib.contextmanager
def process_lock(root):
    path = root / "data" / "collector.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise StudyError("Another collector/export process holds this directory.") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def load_keys(root):
    keys = {}
    for name in ("keys.local", "keys.local.txt"):
        path = root / name
        if path.exists():
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.split("=", 1)
                    if key.strip() in KEY_NAMES.values():
                        keys[key.strip()] = value.strip().strip('"').strip("'")
    for key in KEY_NAMES.values():
        if os.environ.get(key):
            keys[key] = os.environ[key].strip()
    return keys


def load_words(root, batch):
    path = root / "stimuli" / (batch + "-words.txt")
    if not path.exists():
        raise StudyError("Missing stimulus file: " + str(path))
    raw = path.read_bytes()
    if digest(raw) != EXPECTED_HASH[batch]:
        raise StudyError(batch + " stimulus SHA-256 differs from committed bytes.")
    words = []
    for line in raw.decode("utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2 or "|" in parts[1]:
            raise StudyError("Expected set and word, without a trial separator.")
        words.append(tuple(parts))
    if len({w.casefold() for _, w in words}) != len(words):
        raise StudyError("Duplicate normalized stimulus.")
    counts = {s: sum(s == t for t, _ in words) for s, _ in words}
    if batch == "fresh":
        if sorted(counts.values()) != [8, 16]:
            raise StudyError("Fresh stimuli require exactly two sets of 8 and 16.")
        # Private committed bytes fix membership: eight is human animal-intent.
        mapping = {s: "fresh-animal-intent" if n == 8 else "fresh-no-intent" for s, n in counts.items()}
    else:
        if counts != {"known-animal-intent": 4, "known-no-intent": 4}:
            raise StudyError("Known stimuli require the committed four/four labels.")
        mapping = {s: s for s in counts}
    return [(mapping[s], w, s) for s, w in words], digest(raw)


def build_prompt(word, reality=None, category=None):
    article = "an" if word[0].lower() in "aeiou" else "a"
    head = f"Describe {article} {word}."
    return head if reality is None else f"{head} It is {'an' if reality == 'imaginary' else 'a'} {reality} {category}."


def build_trials(batch, words):
    conditions = [("neutral", None, None)] + [(r.replace(" ", "_")+"_"+c, r, c) for r in REALITIES for c in CATEGORIES]
    return [dict(trial_id=f"{batch}|{w}|{label}|{rep:02}", batch=batch, word=w, word_set=s, source_set_label=original,
                 condition=label, reality=r, category=c, rep=rep, prompt=build_prompt(w, r, c))
            for s, w, original in words for label, r, c in conditions for rep in range(1, REPS[batch]+1)]


def payload(model, prompt):
    messages = [{"role": "user", "content": prompt}]
    body = dict(model=model["id"], max_tokens=CAP, messages=messages) if model["provider"] == "anthropic" else dict(model=model["id"], max_output_tokens=CAP, store=False, input=messages)
    return dict(body, **model["params"])


def transport(model, body, key):
    if model["provider"] == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    else:
        url = "https://api.openai.com/v1/responses"
        headers = {"Authorization": "Bearer "+key, "content-type": "application/json"}
    request = urllib.request.Request(url, data=canonical(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180, context=ssl.create_default_context()) as response:
            return response.status, response.read().decode("utf-8"), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace"), dict(error.headers)


def parse_response(model, status_code, raw):
    out = dict(terminal=False, retryable=status_code in RETRY_STATUS, valid=False, error="http_error", response=None,
               visible_blocks=[], refusal=False, truncated=False, complete=False, input_tokens=None, output_tokens=None,
               reasoning_tokens=None, thinking_blocks=0)
    try:
        js = json.loads(raw)
        if not isinstance(js, dict):
            raise ValueError()
    except (ValueError, TypeError):
        out["error"] = "unreadable_payload"
        return out
    out.update(model_returned=js.get("model"), response_id=js.get("id"), provider_error=js.get("error"))
    usage = js.get("usage") or {}
    if isinstance(usage, dict):
        for name in ("input_tokens", "output_tokens"):
            value = usage.get(name)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                out[name] = value
    if status_code != 200:
        return out
    try:
        if model["provider"] == "openai":
            if not isinstance(js.get("output"), list):
                raise ValueError()
            status, reason = js.get("status"), (js.get("incomplete_details") or {}).get("reason")
            out.update(stop_reason=status, incomplete_reason=reason)
            if status == "failed":
                out.update(error="generation_failed", retryable=(js.get("error") or {}).get("code") in {"server_error", "rate_limit_exceeded"})
            elif status == "completed" or (status == "incomplete" and reason in {"max_output_tokens", "content_filter"}):
                out.update(terminal=True, complete=status == "completed", truncated=reason == "max_output_tokens")
            else:
                out["error"] = "unknown_or_nonterminal_status"
            for item in js.get("output", []):
                if item.get("type") == "message":
                    for part in item.get("content", []):
                        kind = part.get("type")
                        if kind not in {"output_text", "refusal"}:
                            raise ValueError()
                        text = part.get("text" if kind == "output_text" else "refusal")
                        if not isinstance(text, str):
                            raise ValueError()
                        out["visible_blocks"].append(dict(type=kind, text=text))
                        out["refusal"] |= kind == "refusal"
            reasoning = (usage.get("output_tokens_details") or {}).get("reasoning_tokens")
            if not isinstance(reasoning, int) or isinstance(reasoning, bool) or reasoning < 0:
                if out["terminal"]:
                    raise ValueError()
            out["reasoning_tokens"] = reasoning
        else:
            if not isinstance(js.get("content"), list):
                raise ValueError()
            stop = js.get("stop_reason")
            out.update(stop_reason=stop, stop_details=js.get("stop_details"))
            if stop in {"end_turn", "stop_sequence", "refusal", "max_tokens"}:
                out.update(terminal=True, complete=stop != "max_tokens", truncated=stop == "max_tokens", refusal=stop == "refusal")
            else:
                out["error"] = "unknown_or_nonterminal_status"
            for block in js.get("content", []):
                kind = block.get("type")
                if kind == "text" and isinstance(block.get("text"), str):
                    out["visible_blocks"].append(dict(type=kind, text=block["text"]))
                elif kind in {"thinking", "redacted_thinking"}:
                    out["thinking_blocks"] += 1
                else:
                    raise ValueError()
        out["response"] = "\n".join(b["text"] for b in out["visible_blocks"])
        if out["terminal"]:
            if out["input_tokens"] is None or out["output_tokens"] is None or not out.get("model_returned"):
                raise ValueError()
            out.update(valid=True, error=None)
    except (AttributeError, TypeError, ValueError):
        out.update(valid=False, error="schema_error", retryable=False)
    return out


def token_cost(model, n_in, n_out):
    value = (Decimal(str(model["price_in"]))*n_in + Decimal(str(model["price_out"]))*n_out)*1000
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def reservation(model, body):
    bound = len(canonical(body).encode()) + 4096  # conservative framing allowance, audited against usage
    return token_cost(model, bound, CAP), bound


class Ledger:
    def __init__(self, root):
        directory = root/"data"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory/"state.sqlite3"
        if not path.exists() and any((directory/"raw").glob("*/*.jsonl")):
            raise StudyError("Legacy JSONL data exists. Reconcile/migrate before using this collector.")
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,attempt_id TEXT UNIQUE,phase TEXT,model TEXT,
          provider TEXT,trial_id TEXT,ordinal INTEGER,started TEXT,finished TEXT,trial TEXT,request TEXT,
          request_hash TEXT,input_bound INTEGER,reservation INTEGER,liability INTEGER,state TEXT,http_status INTEGER,
          raw TEXT,response_headers TEXT,fields TEXT,latency REAL);
        CREATE UNIQUE INDEX IF NOT EXISTS attempt_ordinal ON attempts(phase,model,trial_id,ordinal);
        CREATE TABLE IF NOT EXISTS reconciliation(id INTEGER PRIMARY KEY,attempt_id TEXT,previous INTEGER,
          corrected INTEGER,note TEXT,timestamp TEXT);
        ''')
        self.db.execute("UPDATE attempts SET state='ambiguous' WHERE state='started'")
        self.db.commit()

    def get(self, key):
        with self.lock:
            row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else None

    def put(self, key, value, immutable=False):
        with self.lock:
            previous = self.get(key)
            if immutable and previous is not None and previous != value:
                raise StudyError("Immutable metadata differs: "+key)
            self.db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, canonical(value)))
            # Caller manages transactions for multi-step updates.

    def total(self, provider):
        with self.lock:
            return self.db.execute("SELECT COALESCE(SUM(liability),0) FROM attempts WHERE provider=?", (provider,)).fetchone()[0]

    def rows(self, phase=None, model=None, trial_id=None):
        clauses, values = [], []
        for k, v in (("phase", phase), ("model", model), ("trial_id", trial_id)):
            if v is not None:
                clauses.append(k+"=?")
                values.append(v)
        with self.lock:
            return [dict(r) for r in self.db.execute("SELECT * FROM attempts"+(" WHERE "+" AND ".join(clauses) if clauses else "")+" ORDER BY id", values)]

    def start(self, model, phase, trial, body, maximum):
        with self.lock, self.db:
            if self.get("halt"):
                raise StudyError("Persistent protocol halt: "+self.get("halt"))
            old = self.rows(phase, model["id"], trial["trial_id"])
            h = digest(canonical(body).encode())
            if any(r["request_hash"] != h or r["trial"] != canonical(trial) for r in old):
                raise StudyError("Stored trial/request differs from frozen trial.")
            terminal = [r for r in old if r["fields"] and json.loads(r["fields"]).get("terminal")]
            if terminal:
                if not json.loads(terminal[0]["fields"]).get("valid"):
                    raise StudyError("Invalid terminal payload requires review; it will not be regenerated.")
                return None, "terminal"
            if old and old[-1]["fields"]:
                last = json.loads(old[-1]["fields"])
                if not last.get("retryable") and old[-1]["http_status"] not in {401,403}:
                    raise StudyError("A prior hard error requires review; it will not be retried automatically.")
            if len(old) >= maximum:
                return None, "exhausted"
            amount, bound = reservation(model, body)
            if self.total(model["provider"]) + amount > BUDGET:
                self.put("budget_stopped:"+model["provider"], True)
                return None, "budget"
            if self.get("budget_stopped:"+model["provider"]):
                return None, "budget"
            aid = uuid.uuid4().hex
            self.db.execute('''INSERT INTO attempts(attempt_id,phase,model,provider,trial_id,ordinal,started,
                trial,request,request_hash,input_bound,reservation,liability,state) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (aid, phase, model["id"], model["provider"], trial["trial_id"], len(old)+1, now(), canonical(trial),
                 canonical(body), h, bound, amount, amount, "started"))
            return aid, "started"

    def finish(self, aid, model, status, raw, headers, fields, elapsed):
        with self.lock, self.db:
            row = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (aid,)).fetchone()
            known = fields.get("input_tokens") is not None and fields.get("output_tokens") is not None
            liability = token_cost(model, fields["input_tokens"], fields["output_tokens"]) if known else row["reservation"]
            if known and (fields["input_tokens"] > row["input_bound"] or liability > row["reservation"]):
                fields["protocol_violation"] = "usage_exceeded_reservation"
            if fields.get("protocol_violation"):
                self.put("halt", fields["protocol_violation"])
                fields["valid"] = False
            safe = {k: v for k, v in headers.items() if k.lower() in {"request-id", "x-request-id", "retry-after"}}
            self.db.execute('''UPDATE attempts SET finished=?,liability=?,state=?,http_status=?,raw=?,response_headers=?,
                fields=?,latency=? WHERE attempt_id=?''', (now(), liability, "finished" if known else "ambiguous",
                status, raw, canonical(safe), canonical(fields), elapsed, aid))

    def reconcile(self, aid, amount, note):
        with self.lock, self.db:
            row = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (aid,)).fetchone()
            if row is None or row["state"] != "ambiguous" or amount < 0 or not note.strip():
                raise StudyError("Reconcile an ambiguous attempt with a nonnegative amount and billing evidence.")
            self.db.execute("INSERT INTO reconciliation(attempt_id,previous,corrected,note,timestamp) VALUES (?,?,?,?,?)", (aid, row["liability"], amount, note, now()))
            self.db.execute("UPDATE attempts SET liability=?,state='reconciled' WHERE attempt_id=?", (amount, aid))


class Collector:
    def __init__(self, root=ROOT, keys=None, request=transport, wait=None):
        self.root, self.request = root, request
        self.keys = keys if keys is not None else load_keys(root)
        self.ledger, self.stop = Ledger(root), threading.Event()
        self.wait = wait if wait is not None else self.stop.wait

    def one(self, model, phase, trial, expected=None):
        key = self.keys.get(KEY_NAMES[model["provider"]])
        if not key:
            raise StudyError("Missing "+KEY_NAMES[model["provider"]])
        body, maximum = payload(model, trial["prompt"]), 4 if phase == "preflight" else 6
        while not self.stop.is_set():
            aid, reason = self.ledger.start(model, phase, trial, body, maximum)
            if aid is None:
                return reason
            t0 = time.monotonic()
            status, raw, headers = None, None, {}
            try:
                status, raw, headers = self.request(model, body, key)
                fields = parse_response(model, status, raw)
            except (OSError, TimeoutError, UnicodeError) as exc:
                fields = dict(valid=False, terminal=False, retryable=True, error="transport:"+type(exc).__name__)
            if fields.get("valid"):
                returned = fields.get("model_returned", "")
                if not expected and not (returned == model["id"] or re.fullmatch(re.escape(model["id"])+r"-(?:\d{8}|\d{4}-\d{2}-\d{2})", returned)):
                    fields["protocol_violation"] = "unexpected_preflight_model"
                if expected and fields.get("model_returned") != expected:
                    fields["protocol_violation"] = "returned_model_changed"
                if (fields.get("reasoning_tokens") or 0) > 0 or fields.get("thinking_blocks", 0):
                    fields["protocol_violation"] = "reasoning_observed_in_reasoning_off_run"
            self.ledger.finish(aid, model, status, raw, headers, fields, time.monotonic()-t0)
            if fields.get("protocol_violation"):
                raise StudyError("Protocol mismatch recorded: "+fields["protocol_violation"])
            if fields.get("terminal"):
                if not fields.get("valid"):
                    raise StudyError("Terminal schema requires review; raw payload preserved.")
                return "terminal"
            if not fields.get("retryable"):
                raise StudyError("Request failed without changing settings: "+fields.get("error", "unknown"))
            count = len(self.ledger.rows(phase, model["id"], trial["trial_id"]))
            if count >= maximum:
                return "exhausted"
            retry = next((v for k, v in headers.items() if k.lower() == "retry-after"), None)
            try:
                delay = min(120, max(0, float(retry)))
            except (TypeError, ValueError):
                delay = min(60, 2**count)
            self.wait(delay)
        return "stopped"

    def check(self, selected):
        for model in selected:
            saved = self.ledger.get("settings:"+model["id"])
            if saved:
                if saved["model_config"] != model:
                    raise StudyError("Saved settings differ from code; not overwritten.")
                print(model["id"], "already checked; no request")
                continue
            if self.ledger.get("freeze"):
                raise StudyError("Cannot change settings after freeze.")
            result = self.one(model, "preflight", dict(trial_id="preflight", prompt=PREFLIGHT))
            good = [json.loads(r["fields"]) for r in self.ledger.rows("preflight", model["id"], "preflight") if r["fields"] and json.loads(r["fields"]).get("valid")]
            if result != "terminal" or not good or not good[0].get("complete") or not good[0].get("response", "").strip():
                raise StudyError("Preflight needs a complete nonempty response: "+model["id"])
            with self.ledger.lock, self.ledger.db:
                self.ledger.put("settings:"+model["id"], dict(model_config=model, model_returned=good[0]["model_returned"], checked_utc=now()), immutable=True)
            print(model["id"], "checked; settings locked")
        self.export()

    def freeze(self, protocol):
        if protocol != "gpt-v1":
            raise StudyError("Only gpt-v1 is implemented; Claude's hypothesis-analysis script is still outstanding.")
        import numpy
        paths = ["run_bestiary.py", "bestiary_scorer.py", "analyze_bestiary.py", "requirements-analysis.txt", "docs/implementation-protocol.md",
                 "docs/gpt-proposal/PREREGISTRATION_GPT.md", "docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md", "docs/gpt-proposal/inventories-gpt-v1.json",
                 "prereg/CLAUDE_PREREG.md", "prereg/claude_scorer.py"]
        test_paths = [str(p.relative_to(self.root)) for p in sorted((self.root/"tests").glob("test_*.py"))]
        if not test_paths:
            raise StudyError("The source test suite must be present before freezing.")
        paths += test_paths
        hashes = {p: digest((self.root/p).read_bytes()) for p in paths}
        settings = {m["id"]: self.ledger.get("settings:"+m["id"]) for m in MODELS}
        if not all(settings.values()):
            raise StudyError("Check all eight models before freezing.")
        batches, word_hashes = {}, {}
        for batch in REPS:
            words, word_hashes[batch] = load_words(self.root, batch)
            base = build_trials(batch, words)
            batches[batch] = {}
            for model in MODELS:
                order = list(base)
                random.Random(f"{SEED}|{batch}|{model['id']}").shuffle(order)
                batches[batch][model["id"]] = order
        doc = dict(version=2, protocol=protocol, code_hashes=hashes, word_hashes=word_hashes, settings=settings,
                   batches=batches, budget_nanodollars=BUDGET, python=sys.version, numpy=numpy.__version__)
        doc["manifest_sha256"] = digest(canonical(doc).encode())
        with self.ledger.lock, self.ledger.db:
            self.ledger.put("freeze", doc, immutable=True)
        self.export()
        print("Frozen:", doc["manifest_sha256"], "(private manifest contains fresh words)")

    def verify_freeze(self):
        doc = self.ledger.get("freeze")
        if not doc:
            raise StudyError("Review protocol, then freeze --protocol gpt-v1 before collection.")
        import numpy
        if doc["python"] != sys.version or doc["numpy"] != numpy.__version__:
            raise StudyError("Runtime differs from frozen manifest.")
        for p, h in doc["code_hashes"].items():
            if not (self.root/p).exists() or digest((self.root/p).read_bytes()) != h:
                raise StudyError("Frozen file changed: "+p)
        for batch in REPS:
            if load_words(self.root, batch)[1] != doc["word_hashes"][batch]:
                raise StudyError("Frozen stimuli changed.")
        for model in MODELS:
            saved = doc["settings"][model["id"]]
            if saved != self.ledger.get("settings:"+model["id"]) or saved["model_config"] != model:
                raise StudyError("Frozen settings changed.")
        return doc

    def run(self, batch):
        doc = self.verify_freeze()
        if batch == "known" and not self.ledger.get("collection_closed:fresh"):
            raise StudyError("Finish or budget-stop fresh before known.")
        if self.ledger.get("collection_closed:"+batch):
            print(batch, "already closed; no requests")
            return
        def lane(model):
            queue, lock = iter(doc["batches"][batch][model["id"]]), threading.Lock()
            def worker():
                while not self.stop.is_set():
                    with lock:
                        trial = next(queue, None)
                    if trial is None:
                        return
                    if self.one(model, batch, trial, doc["settings"][model["id"]]["model_returned"]) in {"budget", "stopped"}:
                        return
            with futures.ThreadPoolExecutor(max_workers=2) as pool:
                tasks = [pool.submit(worker) for _ in range(2)]
                try:
                    for task in futures.as_completed(tasks):
                        task.result()
                except BaseException:
                    self.stop.set()
                    raise
        failure = None
        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            tasks = [pool.submit(lane, model) for model in MODELS]
            try:
                pending = set(tasks)
                while pending:
                    done, pending = futures.wait(pending, timeout=15, return_when=futures.FIRST_EXCEPTION)
                    for task in done:
                        task.result()
                    self.status()
            except BaseException as exc:
                failure = exc
                self.stop.set()
        self.export()
        if failure:
            raise failure
        with self.ledger.lock, self.ledger.db:
            self.ledger.put("collection_closed:"+batch, dict(closed_utc=now()))
        self.export()
        self.status()

    def export(self):
        grouped, attempts = {}, []
        for row in self.ledger.rows():
            rec = dict(row)
            for key in ("trial", "request", "response_headers", "fields"):
                rec[key] = json.loads(rec[key]) if rec[key] else None
            attempts.append(rec)
            fields = rec["fields"] or {}
            if row["phase"] in REPS and fields.get("terminal"):
                item = dict(rec["trial"], **fields, model_requested=row["model"], provider=row["provider"], attempt_id=row["attempt_id"],
                            attempt_ordinal=row["ordinal"], timestamp_utc=row["started"], request_payload=rec["request"], request_sha256=row["request_hash"],
                            liability_nanodollars=row["liability"], http_status=row["http_status"])
                grouped.setdefault((row["phase"], row["model"]), []).append(item)
        for (batch, model), values in grouped.items():
            atomic_write(self.root/"data"/"raw"/batch/(model+".jsonl"), "".join(canonical(v)+"\n" for v in values))
        atomic_write(self.root/"data"/"attempts.jsonl", "".join(canonical(r)+"\n" for r in attempts))
        doc = self.ledger.get("freeze")
        if doc:
            atomic_write(self.root/"data"/"freeze.json", json.dumps(doc, indent=2, ensure_ascii=False)+"\n")
        settings = {m["id"]: self.ledger.get("settings:"+m["id"]) for m in MODELS}
        atomic_write(self.root/"data"/"raw"/"request-settings.json", json.dumps(settings, indent=2)+"\n")
        with self.ledger.lock:
            reconciliations = [dict(r) for r in self.ledger.db.execute("SELECT * FROM reconciliation ORDER BY id")]
        atomic_write(self.root/"data"/"reconciliations.json", json.dumps(reconciliations, indent=2)+"\n")
        atomic_write(self.root/"data"/"collection-status.json", json.dumps({batch:self.ledger.get("collection_closed:"+batch) for batch in REPS},indent=2)+"\n")

    def status(self):
        rows = self.ledger.rows()
        for provider in KEY_NAMES:
            uncertain = sum(r["state"] in {"ambiguous", "started"} for r in rows if r["provider"] == provider)
            print(f"{provider}: ${self.ledger.total(provider)/USD:.6f} charged/reserved; {uncertain} unresolved/in-flight; cap $20")
        for batch in REPS:
            fields = [json.loads(r["fields"]) for r in rows if r["phase"] == batch and r["fields"]]
            print(batch, "valid terminal:", sum(f.get("valid", False) and f.get("terminal", False) for f in fields),
                  "cap-truncated:", sum(f.get("truncated", False) for f in fields), "attempts:", sum(r["phase"] == batch for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="paid content-neutral preflight, immutable compliant settings")
    check.add_argument("--models", nargs="+", choices=list(BY_ID))
    freeze = sub.add_parser("freeze", help="explicit protocol selection, code/settings/private stimulus freeze")
    freeze.add_argument("--protocol", required=True, choices=["gpt-v1"])
    run = sub.add_parser("run")
    run.add_argument("batch", choices=list(REPS))
    run.add_argument("--dry-run", action="store_true")
    for command in ("status", "export"):
        sub.add_parser(command)
    rec = sub.add_parser("reconcile", help="record billing evidence for an ambiguous charge")
    rec.add_argument("attempt_id")
    rec.add_argument("--usd", required=True, type=Decimal)
    rec.add_argument("--note", required=True)
    args = parser.parse_args()
    if args.command == "run" and args.dry_run:
        words, h = load_words(ROOT, args.batch)
        print(args.batch, len(build_trials(args.batch, words)), "trials/model; 8 models; word SHA-256", h)
        return 0
    with process_lock(ROOT):
        collector = Collector()
        try:
            if args.command == "check":
                collector.check([BY_ID[k] for k in args.models] if args.models else MODELS)
            elif args.command == "freeze":
                collector.freeze(args.protocol)
            elif args.command == "run":
                collector.run(args.batch)
            elif args.command == "status":
                collector.status()
            elif args.command == "export":
                collector.export()
            elif args.command == "reconcile":
                if not args.usd.is_finite():
                    raise StudyError("Billing amount must be finite.")
                collector.ledger.reconcile(args.attempt_id, int((args.usd*USD).to_integral_value(rounding=ROUND_CEILING)), args.note)
                collector.export()
        finally:
            collector.ledger.db.close()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except StudyError as exc:
        print("Stopped:", str(exc), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted. Durable ledger retained; resume with the same command.", file=sys.stderr)
        sys.exit(130)
