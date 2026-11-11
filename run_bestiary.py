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
ISSUE_RATE, ISSUE_MIN = 0.05, 200   # a model lane stops when issues exceed 5% of its closed slots, once 200 are closed
FRESH_SETS = {"fresh-animal-intent": "fresh-animal-intent", "fresh-no-intent-claude": "fresh-no-intent", "fresh-no-intent-gpt": "fresh-no-intent"}
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
# Extra files frozen for each selectable protocol. Both keep the GPT analysis; the second adds Claude's amended family.
CLAUDE_FILES = ["prereg/CLAUDE_PREREG_AMENDMENT_1.md", "prereg/claude_scorer_v1_1.py", "analyze_claude.py"]
PROTOCOLS = {"gpt-v1": [], "gpt-v1+claude-v1.1": CLAUDE_FILES}
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
        if counts != {label: 8 for label in FRESH_SETS}:
            raise StudyError("Fresh stimuli require eight words under each of: " + ", ".join(FRESH_SETS))
        # Both model-authored sets are analysed as no-intent; the original label keeps the author.
        mapping = dict(FRESH_SETS)
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
            if (out["input_tokens"] is None or out["output_tokens"] is None
                    or not isinstance(out.get("model_returned"), str) or not out["model_returned"]):
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
            if phase != "preflight" and self.get("lane_stopped:"+model["id"]):
                return None, "lane_stopped"
            old = self.rows(phase, model["id"], trial["trial_id"])
            h = digest(canonical(body).encode())
            if any(r["request_hash"] != h or r["trial"] != canonical(trial) for r in old):
                raise StudyError("Stored trial/request differs from frozen trial.")
            if any(r["fields"] and json.loads(r["fields"]).get("issue") for r in old):
                return None, "issue_closed"
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
            violation = fields.get("protocol_violation")
            if violation:
                fields["valid"] = False
                if row["phase"] == "preflight" or violation == "usage_exceeded_reservation":
                    self.put("halt", violation)
                else:
                    fields["issue"] = fields.get("issue") or violation
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
        self.counts, self.count_lock = {}, threading.RLock()
        for batch in REPS:
            self.load_counts(batch)

    def tally(self, phase, model_id):
        return self.counts.setdefault((phase, model_id), dict(good=0, issues=0, cut=0, gave_up=0, new=0))

    def load_counts(self, batch):
        """Replay closed slots in completion order, recovering a stop lost after a committed result."""
        with self.count_lock:
            for model in MODELS:
                self.counts[(batch, model["id"])] = dict(good=0, issues=0, cut=0, gave_up=0, new=0)
            slots = {}
            for row in self.ledger.rows(batch):
                fields = json.loads(row["fields"]) if row["fields"] else {}
                slots.setdefault((row["model"], row["trial_id"]), []).append((row, fields))
            events = []
            for (model_id, _), attempts in slots.items():
                closed = [(row, fields) for row, fields in attempts
                          if fields.get("issue") or (fields.get("terminal") and fields.get("valid"))]
                if closed:
                    row, fields = min(closed, key=lambda pair: (pair[0]["finished"] or pair[0]["started"], pair[0]["id"]))
                    outcome = ("identity" if fields["issue"] == "returned_model_changed" else "issue") if fields.get("issue") else "terminal"
                elif len(attempts) >= 6:
                    row, fields = attempts[-1]
                    outcome = "exhausted"
                else:
                    continue
                events.append((row["finished"] or row["started"], row["id"], model_id, outcome, fields))
            for closed_at, _, model_id, outcome, fields in sorted(events):
                c = self.tally(batch, model_id)
                if outcome in {"issue", "identity"}:
                    c["issues"] += 1
                elif outcome == "terminal":
                    c["good"] += 1
                    c["cut"] += bool(fields.get("truncated"))
                else:
                    c["gave_up"] += 1
                self.lane_should_stop({"id": model_id}, batch, outcome, closed_at=closed_at)

    def observe(self, model, phase, outcome, fields):
        if phase == "preflight":
            return
        with self.count_lock:
            c = self.tally(phase, model["id"])
            c["new"] += 1
            if outcome in {"issue", "identity"}:
                c["issues"] += 1
            elif outcome == "exhausted":
                c["gave_up"] += 1
            else:
                c["good"] += 1
                c["cut"] += bool(fields.get("truncated"))
            # The 200th qualifying closure may be valid, so check every closure.
            self.lane_should_stop(model, phase, outcome)

    def lane_should_stop(self, model, phase, outcome, closed_at=None):
        """Stop on identity drift or ISSUE_RATE after ISSUE_MIN valid-or-issue closures.

        Exhausted retries are reported separately and are excluded from this
        issue-rate denominator, preserving the registered implementation.
        """
        if self.ledger.get("lane_stopped:"+model["id"]):
            return True
        with self.count_lock:
            c = dict(self.tally(phase, model["id"]))
        closed = c["good"] + c["issues"]
        if outcome == "identity":
            reason = "returned model identifier changed"
        elif closed >= ISSUE_MIN and c["issues"] > ISSUE_RATE * closed:
            reason = "issues exceeded %d%% of closed slots (%d of %d)" % (round(ISSUE_RATE*100), c["issues"], closed)
        else:
            return False
        with self.ledger.lock, self.ledger.db:
            if not self.ledger.get("lane_stopped:"+model["id"]):
                record = dict(reason=reason, phase=phase, stopped_utc=closed_at or now(), issues=c["issues"], closed=closed)
                if closed_at is not None:
                    record["recovered_utc"] = now()
                self.ledger.put("lane_stopped:"+model["id"], record)
        return True

    def progress(self, batch, doc, started, final=False):
        def clock(seconds):
            seconds = int(max(0, seconds))
            return "%dh%02dm" % (seconds//3600, seconds % 3600//60) if seconds >= 3600 else "%dm%02ds" % (seconds//60, seconds % 60)
        with self.count_lock:
            counts = {m["id"]: dict(self.tally(batch, m["id"])) for m in MODELS}
        planned = {m["id"]: len(doc["batches"][batch][m["id"]]) for m in MODELS}
        closed = {k: c["good"]+c["issues"]+c["gave_up"] for k, c in counts.items()}
        stopped = {m["id"]: self.ledger.get("lane_stopped:"+m["id"]) for m in MODELS}
        budget = {p: self.ledger.get("budget_stopped:"+p) for p in KEY_NAMES}
        live = [k for k in planned if not stopped[k] and not budget[BY_ID[k]["provider"]]]
        total, done, new = sum(planned.values()), sum(closed.values()), sum(c["new"] for c in counts.values())
        elapsed = time.monotonic() - started
        left = sum(planned[k]-closed[k] for k in live)
        eta = clock(left*elapsed/new) if new and left and not final else "--"
        print("[%s] %s: %d/%d slots closed (%.0f%%)   running %s   time left %s"
              % (time.strftime("%H:%M:%S"), batch, done, total, 100*done/total if total else 100, clock(elapsed), eta))
        print("           " + "   ".join("%s $%.2f of $%d" % (p, self.ledger.total(p)/USD, BUDGET//USD) for p in KEY_NAMES))
        for model in MODELS:
            k, c = model["id"], counts[model["id"]]
            filled = int(20*closed[k]/planned[k]) if planned[k] else 20
            note = ""
            if stopped[k]:
                note = "   STOPPED: " + stopped[k]["reason"]
            elif budget[model["provider"]]:
                note = "   STOPPED: budget"
            elif closed[k] >= planned[k]:
                note = "   done"
            print("  %-18s [%s] %5d/%-5d cut off %-3d issues %-3d gave up %-3d%s"
                  % (k, "#"*filled + "-"*(20-filled), closed[k], planned[k], c["cut"], c["issues"], c["gave_up"], note))
        print(flush=True)

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
            if fields.get("valid") or status == 200:
                returned = fields.get("model_returned")
                has_identifier = isinstance(returned, str) and bool(returned)
                # A reported identity change takes priority even if the rest of
                # the successful HTTP payload is malformed or contains reasoning.
                if expected and has_identifier and returned != expected:
                    fields["protocol_violation"] = "returned_model_changed"
                elif not expected and has_identifier and not (returned == model["id"] or re.fullmatch(re.escape(model["id"])+r"-(?:\d{8}|\d{4}-\d{2}-\d{2})", returned)):
                    fields["protocol_violation"] = "unexpected_preflight_model"
                elif (fields.get("reasoning_tokens") or 0) > 0 or fields.get("thinking_blocks", 0):
                    fields["protocol_violation"] = "reasoning_observed_in_reasoning_off_run"
            if phase != "preflight" and not fields.get("protocol_violation"):
                if fields.get("terminal") and not fields.get("valid"):
                    fields["issue"] = "schema_error"            # unexpected content type or payload shape
                elif not fields.get("terminal") and not fields.get("retryable") and status not in {401, 403}:
                    fields["issue"] = "hard_error:"+str(fields.get("error", "unknown"))
            # Serialize completion and its stop decision against other dispatches.
            # If the process dies between their commits, load_counts replays it.
            with self.count_lock, self.ledger.lock:
                self.ledger.finish(aid, model, status, raw, headers, fields, time.monotonic()-t0)
                violation = fields.get("protocol_violation")
                if violation and (phase == "preflight" or violation == "usage_exceeded_reservation"):
                    raise StudyError("Protocol mismatch recorded: "+violation)
                if fields.get("issue"):                              # recorded, slot closed, not regenerated
                    outcome = "identity" if fields["issue"] == "returned_model_changed" else "issue"
                    self.observe(model, phase, outcome, fields)
                    return outcome
                if fields.get("terminal"):
                    if not fields.get("valid"):
                        raise StudyError("Terminal schema requires review; raw payload preserved.")
                    self.observe(model, phase, "terminal", fields)
                    return "terminal"
                if not fields.get("retryable"):
                    raise StudyError("Request failed without changing settings: "+fields.get("error", "unknown"))
                count = len(self.ledger.rows(phase, model["id"], trial["trial_id"]))
                if count >= maximum:
                    self.observe(model, phase, "exhausted", fields)
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
        if protocol not in PROTOCOLS:
            raise StudyError("Unknown protocol: "+protocol)
        import numpy
        paths = ["run_bestiary.py", "bestiary_scorer.py", "analyze_bestiary.py", "requirements-analysis.txt", "docs/implementation-protocol.md",
                 "docs/gpt-proposal/PREREGISTRATION_GPT.md", "docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md", "docs/gpt-proposal/inventories-gpt-v1.json",
                 "prereg/CLAUDE_PREREG.md", "prereg/claude_scorer.py"] + PROTOCOLS[protocol]
        test_paths = [str(p.relative_to(self.root)) for p in sorted((self.root/"tests").glob("test_*.py"))]
        if not test_paths:
            raise StudyError("The source test suite must be present before freezing.")
        paths += test_paths
        hashes = {p: digest((self.root/p).read_bytes()) for p in paths}
        if "analyze_claude.py" in PROTOCOLS[protocol]:
            amendment = (self.root/"prereg/CLAUDE_PREREG_AMENDMENT_1.md").read_text(encoding="utf-8")
            committed = re.findall(r"`analyze_claude\.py`, SHA-256 `([0-9a-f]{64})`", amendment)
            if len(committed) != 1 or committed[0] != hashes["analyze_claude.py"]:
                raise StudyError("Claude analyzer SHA-256 does not match CLAUDE_PREREG_AMENDMENT_1.md. Review and update the amendment before freezing.")
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
            raise StudyError("Review protocol, then freeze --protocol <name> before collection.")
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
        self.load_counts(batch)
        started = time.monotonic()
        def lane(model):
            queue, lock = iter(doc["batches"][batch][model["id"]]), threading.Lock()
            def worker():
                while not self.stop.is_set():
                    with lock:
                        trial = next(queue, None)
                    if trial is None:
                        return
                    outcome = self.one(model, batch, trial, doc["settings"][model["id"]]["model_returned"])
                    if outcome in {"budget", "stopped", "lane_stopped"}:
                        return
                    if outcome in {"issue", "identity"} and self.lane_should_stop(model, batch, outcome):
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
                    self.progress(batch, doc, started)
            except BaseException as exc:
                failure = exc
                self.stop.set()
        self.export()
        if failure:
            raise failure
        with self.ledger.lock, self.ledger.db:
            self.ledger.put("collection_closed:"+batch, dict(closed_utc=now()))
        self.export()
        print("---- %s closed ----" % batch)
        self.progress(batch, doc, started, final=True)
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
                  "cap-truncated:", sum(f.get("truncated", False) for f in fields), "issues:", sum(bool(f.get("issue")) for f in fields),
                  "attempts:", sum(r["phase"] == batch for r in rows))
        for model in MODELS:
            lane = self.ledger.get("lane_stopped:"+model["id"])
            if lane:
                print(model["id"], "lane stopped:", lane["reason"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="paid content-neutral preflight, immutable compliant settings")
    check.add_argument("--models", nargs="+", choices=list(BY_ID))
    freeze = sub.add_parser("freeze", help="explicit protocol selection, code/settings/private stimulus freeze")
    freeze.add_argument("--protocol", required=True, choices=list(PROTOCOLS))
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
