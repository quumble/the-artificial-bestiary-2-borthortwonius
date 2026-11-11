#!/usr/bin/env python3
"""
The Artificial Bestiary 2: Borthortwonius -- collection runner.

Standard library only. No packages to install.

    python run_bestiary.py check          one tiny call per model; locks request settings
    python run_bestiary.py run fresh      collect the fresh-word batch
    python run_bestiary.py run known      collect the known-word replication batch
    python run_bestiary.py status         what is on disk: counts, truncation, spend

Safe to stop with Ctrl+C and rerun the same command: finished trials are skipped.
Response text is written to disk and never printed.

Keys: set ANTHROPIC_API_KEY and OPENAI_API_KEY in the environment, or put them
in a file named keys.local next to this script, one per line:
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...
"""
import argparse
import datetime
import hashlib
import json
import os
import platform
import random
import ssl
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STIM = ROOT / "stimuli"
DATA = ROOT / "data" / "raw"
KEYFILE = ROOT / "keys.local"
VARIANTS_FILE = DATA / "request-settings.json"

# ---------------------------------------------------------------- settings
VISIBLE_CAP = 1024          # requested cap on visible output tokens
THINKING_ALLOWANCE = 4096   # extra room, only when reasoning cannot be turned off
SPEND_CAP_USD = 20.0        # per provider, across every batch on disk
SEED = 20261110
DEFAULT_REPS = {"fresh": 5, "known": 10}
DEFAULT_WORKERS = 2         # parallel requests per model
MAX_ATTEMPTS = 6            # per trial, for rate limits and server errors
LANE_ERROR_LIMIT = 5        # consecutive hard errors before a model is paused
PREFLIGHT_PROMPT = "Reply with the single word: ready."

ANTHROPIC_BASE = os.environ.get("BESTIARY_ANTHROPIC_BASE", "https://api.anthropic.com")
OPENAI_BASE = os.environ.get("BESTIARY_OPENAI_BASE", "https://api.openai.com")

# Request settings are tried in the order listed. `check` keeps the first one
# the API accepts and every later run reuses it, so settings cannot drift
# between batches. allowance=True means reasoning is active and shares the
# output limit, so the limit is raised by THINKING_ALLOWANCE.
A_TEMP = [
    {"name": "temperature-1.0", "params": {"temperature": 1.0}, "allowance": False},
    {"name": "api-default", "params": {}, "allowance": False},
]
O_OLD = [
    {"name": "reasoning-none+temperature-1.0",
     "params": {"reasoning": {"effort": "none"}, "temperature": 1.0, "top_p": 1.0}, "allowance": False},
    {"name": "temperature-1.0", "params": {"temperature": 1.0, "top_p": 1.0}, "allowance": False},
    {"name": "api-default", "params": {}, "allowance": True},
]
O_NEW = [
    {"name": "reasoning-none+temperature-1.0",
     "params": {"reasoning": {"effort": "none"}, "temperature": 1.0}, "allowance": False},
    {"name": "reasoning-none", "params": {"reasoning": {"effort": "none"}}, "allowance": False},
    {"name": "reasoning-low", "params": {"reasoning": {"effort": "low"}}, "allowance": True},
]

# Prices are USD per million tokens and are used only for the running estimate
# and the spend stop. Edit them if the provider's price page says otherwise.
MODELS = [
    {"id": "claude-sonnet-4-6", "provider": "anthropic", "role": "historical",
     "price_in": 3.00, "price_out": 15.00, "variants": A_TEMP},
    {"id": "claude-haiku-4-5", "provider": "anthropic", "role": "historical",
     "price_in": 1.00, "price_out": 5.00, "variants": A_TEMP},
    {"id": "claude-sonnet-5-5", "provider": "anthropic", "role": "current",
     "price_in": 2.00, "price_out": 10.00, "variants": [
         {"name": "thinking-between-tools", "params": {"thinking": {"type": "between_tools"}}, "allowance": False},
         {"name": "adaptive-thinking-default", "params": {}, "allowance": True}]},
    {"id": "claude-haiku-5-5", "provider": "anthropic", "role": "current",
     "price_in": 0.10, "price_out": 0.50, "variants": [
         {"name": "thinking-disabled", "params": {"thinking": {"type": "disabled"}}, "allowance": False},
         {"name": "adaptive-thinking-default", "params": {}, "allowance": True}]},
    {"id": "gpt-5.4-mini", "provider": "openai", "role": "historical",
     "price_in": 0.75, "price_out": 4.50, "variants": O_OLD},
    {"id": "gpt-5.4-nano", "provider": "openai", "role": "historical",
     "price_in": 0.20, "price_out": 1.25, "variants": O_OLD},
    {"id": "gpt-6-sol", "provider": "openai", "role": "current",
     "price_in": 2.00, "price_out": 10.00, "variants": O_NEW},
    {"id": "gpt-6-luna", "provider": "openai", "role": "current",
     "price_in": 0.10, "price_out": 0.50, "variants": O_NEW},
]
MODEL_BY_ID = {m["id"]: m for m in MODELS}
PROVIDERS = ["anthropic", "openai"]
KEY_NAMES = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}

REALITIES = ["real", "imaginary", "type of"]
CATEGORIES = ["animal", "object", "idea"]
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}
AUTH_STATUS = {401, 403}


# ---------------------------------------------------------------- helpers
def say(text=""):
    print(text, flush=True)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clock():
    return datetime.datetime.now().strftime("%H:%M:%S")


def fmt_dur(seconds):
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return "%dh%02dm" % (h, m) if h else "%dm%02ds" % (m, s)


def ssl_context():
    try:
        import certifi  # used only if it happens to be installed
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


SSL_CTX = ssl_context()


def load_keys():
    keys = {}
    # Notepad likes to add .txt, so accept that name too.
    for path in (KEYFILE, KEYFILE.with_name("keys.local.txt")):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = v.strip().strip('"').strip("'")
    for name in KEY_NAMES.values():
        if os.environ.get(name):
            keys[name] = os.environ[name].strip()
    return keys


def post_json(url, headers, body, timeout=180):
    """Returns (status, parsed_json, headers). Raises OSError on network failure."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = {"raw": raw[:500]}
        return e.code, payload, dict(e.headers or {})


def error_text(payload):
    err = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(err, dict):
        return str(err.get("message") or err)[:400]
    return json.dumps(payload)[:400]


def call_model(model, variant, prompt, key):
    """One request. Returns (status, record_fields). Raises OSError on network failure."""
    cap = VISIBLE_CAP + (THINKING_ALLOWANCE if variant["allowance"] else 0)
    if model["provider"] == "anthropic":
        body = {"model": model["id"], "max_tokens": cap,
                "messages": [{"role": "user", "content": prompt}]}
        body.update(variant["params"])
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        status, js, hdrs = post_json(ANTHROPIC_BASE + "/v1/messages", headers, body)
        if status != 200:
            return status, {"error": "HTTP %s: %s" % (status, error_text(js)), "_headers": hdrs}
        blocks = js.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        thinking = sum(1 for b in blocks if b.get("type") in ("thinking", "redacted_thinking"))
        usage = js.get("usage") or {}
        out_tok = int(usage.get("output_tokens") or 0)
        stop = js.get("stop_reason")
        fields = {"response": text, "stop_reason": stop, "truncated": stop == "max_tokens",
                  "input_tokens": int(usage.get("input_tokens") or 0), "output_tokens": out_tok,
                  "reasoning_tokens": None, "thinking_blocks": thinking,
                  "visible_output_tokens": None if thinking else out_tok,
                  "model_returned": js.get("model"), "response_id": js.get("id")}
    else:
        body = {"model": model["id"], "max_output_tokens": cap, "store": False,
                "input": [{"role": "user", "content": prompt}]}
        body.update(variant["params"])
        headers = {"Authorization": "Bearer " + key, "content-type": "application/json"}
        status, js, hdrs = post_json(OPENAI_BASE + "/v1/responses", headers, body)
        if status != 200:
            return status, {"error": "HTTP %s: %s" % (status, error_text(js)), "_headers": hdrs}
        parts = []
        for item in js.get("output") or []:
            if item.get("type") == "message":
                for part in item.get("content") or []:
                    if part.get("type") == "output_text":
                        parts.append(part.get("text", ""))
        usage = js.get("usage") or {}
        out_tok = int(usage.get("output_tokens") or 0)
        reasoning = int((usage.get("output_tokens_details") or {}).get("reasoning_tokens") or 0)
        st = js.get("status")
        reason = (js.get("incomplete_details") or {}).get("reason")
        fields = {"response": "".join(parts),
                  "stop_reason": st if not reason else "%s:%s" % (st, reason),
                  "truncated": st == "incomplete" and reason == "max_output_tokens",
                  "input_tokens": int(usage.get("input_tokens") or 0), "output_tokens": out_tok,
                  "reasoning_tokens": reasoning, "thinking_blocks": None,
                  "visible_output_tokens": out_tok - reasoning,
                  "model_returned": js.get("model"), "response_id": js.get("id")}
    fields["cap_sent"] = cap
    fields["est_cost_usd"] = round((fields["input_tokens"] * model["price_in"]
                                    + fields["output_tokens"] * model["price_out"]) / 1e6, 6)
    fields["error"] = None
    return 200, fields


# ---------------------------------------------------------------- stimuli and trials
def load_words(batch):
    path = STIM / ("%s-words.txt" % batch)
    if not path.exists():
        sys.exit("Missing word list: %s\nSave the %s word list there first." % (path, batch))
    words = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            sys.exit("Bad line in %s: %r (expected: set<TAB>word)" % (path.name, line))
        words.append((parts[0], parts[1]))
    if len({w for _, w in words}) != len(words):
        sys.exit("Duplicate words in %s" % path.name)
    return words, hashlib.sha256(path.read_bytes()).hexdigest()


def build_prompt(word, reality, category):
    art = "an" if word[0].lower() in "aeiou" else "a"
    head = "Describe %s %s." % (art, word)
    if reality is None:
        return head
    r_art = "an" if reality[0] in "aeiou" else "a"
    return "%s It is %s %s %s." % (head, r_art, reality, category)


def build_trials(batch, words, reps):
    conds = [("neutral", None, None)]
    for r in REALITIES:
        for c in CATEGORIES:
            conds.append(("%s_%s" % (r.replace(" ", "_"), c), r, c))
    trials = []
    for wset, word in words:
        for label, r, c in conds:
            for rep in range(1, reps + 1):
                trials.append({"trial_id": "%s|%s|%s|%02d" % (batch, word, label, rep),
                               "batch": batch, "word": word, "word_set": wset,
                               "condition": label, "reality": r, "category": c, "rep": rep,
                               "prompt": build_prompt(word, r, c)})
    return trials


def read_records(path):
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass  # a half-written last line after a crash; that trial reruns
    return out


def spend_on_disk():
    spent = {p: 0.0 for p in PROVIDERS}
    if DATA.exists():
        for path in DATA.glob("*/*.jsonl"):
            for rec in read_records(path):
                prov = rec.get("provider")
                if prov in spent:
                    spent[prov] += float(rec.get("est_cost_usd") or 0)
    return spent


def load_variants():
    if VARIANTS_FILE.exists():
        return json.loads(VARIANTS_FILE.read_text(encoding="utf-8"))
    return {}


def pick_models(names):
    if not names:
        return list(MODELS)
    bad = [n for n in names if n not in MODEL_BY_ID]
    if bad:
        sys.exit("Unknown model(s): %s\nKnown: %s" % (", ".join(bad), ", ".join(MODEL_BY_ID)))
    return [MODEL_BY_ID[n] for n in names]


# ---------------------------------------------------------------- check
def cmd_check(args):
    keys = load_keys()
    models = pick_models(args.models)
    locked = load_variants()
    say("Preflight: one small call per model. Nothing here is study data.\n")
    ok_all = True
    for model in models:
        key = keys.get(KEY_NAMES[model["provider"]])
        if not key:
            say("  %-20s NO KEY   set %s (environment or keys.local)" % (model["id"], KEY_NAMES[model["provider"]]))
            ok_all = False
            continue
        chosen, last_err, stop = None, "", False
        for variant in model["variants"]:
            for attempt in range(1, 5):  # ride out rate limits and brief outages
                transient = False
                try:
                    status, fields = call_model(model, variant, PREFLIGHT_PROMPT, key)
                except Exception as e:
                    last_err, transient = "network: %s: %s" % (type(e).__name__, e), True
                else:
                    if status == 200:
                        chosen = (variant, fields)
                        break
                    last_err = fields["error"]
                    transient = status in RETRY_STATUS
                    if status in AUTH_STATUS or status == 404:
                        stop = True  # a bad key or an unknown model: other settings will not help
                if not transient:
                    break
                if attempt == 4:
                    stop = True
                else:
                    time.sleep(min(20, 2 ** attempt))
            if chosen or stop:
                break
        if not chosen:
            say("  %-20s FAILED   %s" % (model["id"], last_err))
            ok_all = False
            continue
        variant, f = chosen
        thinking = f["reasoning_tokens"] if f["reasoning_tokens"] is not None else f["thinking_blocks"]
        note = ""
        if variant["allowance"] or thinking:
            note = "   <-- reasoning is ON for this model"
        say("  %-20s OK       settings: %-32s returned: %s%s"
            % (model["id"], variant["name"], f["model_returned"], note))
        locked[model["id"]] = {"variant": variant["name"], "checked_utc": now_utc(),
                               "model_returned": f["model_returned"],
                               "reasoning_observed": bool(variant["allowance"] or thinking)}
    DATA.mkdir(parents=True, exist_ok=True)
    VARIANTS_FILE.write_text(json.dumps(locked, indent=2), encoding="utf-8")
    say("\nSettings saved to %s" % VARIANTS_FILE.relative_to(ROOT))
    say("All models ready." if ok_all else "Some models are not ready. Fix those, or run with --models to leave them out.")
    return 0 if ok_all else 1


# ---------------------------------------------------------------- run
class Lane:
    """One model's queue of trials and its counters."""

    def __init__(self, model, variant, path, todo, already_done, planned):
        self.model, self.variant, self.path = model, variant, path
        self.todo, self.planned = todo, planned
        self.next_i = 0
        self.done = already_done      # good records on disk, including earlier sessions
        self.session_done = 0
        self.errors = 0
        self.truncated = 0
        self.session_cost = 0.0
        self.consecutive_errors = 0
        self.halted = None            # reason string when the lane stops early
        self.lock = threading.Lock()


class Run:
    def __init__(self, args, keys):
        self.args, self.keys = args, keys
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.spent = spend_on_disk()
        self.reserved = {p: 0.0 for p in PROVIDERS}
        self.cap = args.spend_cap
        self.lanes = []
        self.started = time.time()

    def worst_case(self, lane):
        cap = VISIBLE_CAP + (THINKING_ALLOWANCE if lane.variant["allowance"] else 0)
        return (cap * lane.model["price_out"] + 200 * lane.model["price_in"]) / 1e6

    def take(self, lane):
        prov = lane.model["provider"]
        with self.lock:
            if self.stop.is_set() or lane.halted or lane.next_i >= len(lane.todo):
                return None
            worst = self.worst_case(lane)
            if self.spent[prov] + self.reserved[prov] + worst > self.cap:
                lane.halted = "spend cap reached for %s" % prov
                return None
            self.reserved[prov] += worst
            trial = lane.todo[lane.next_i]
            lane.next_i += 1
            return trial

    def finish(self, lane, record, hard_error):
        prov = lane.model["provider"]
        with lane.lock:
            with lane.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        with self.lock:
            self.reserved[prov] -= self.worst_case(lane)
            cost = float(record.get("est_cost_usd") or 0)
            self.spent[prov] += cost
            lane.session_cost += cost
            if record["error"] is None:
                lane.done += 1
                lane.session_done += 1
                lane.consecutive_errors = 0
                if record.get("truncated"):
                    lane.truncated += 1
            else:
                lane.errors += 1
                if hard_error:
                    lane.consecutive_errors += 1
                    if lane.consecutive_errors >= LANE_ERROR_LIMIT and not lane.halted:
                        lane.halted = "paused after repeated errors: %s" % record["error"][:120]

    def worker(self, lane):
        key = self.keys[KEY_NAMES[lane.model["provider"]]]
        while True:
            trial = self.take(lane)
            if trial is None:
                return
            record = dict(trial)
            record.update({"provider": lane.model["provider"], "model_requested": lane.model["id"],
                           "request_settings": lane.variant["name"], "timestamp_utc": now_utc()})
            t0 = time.time()
            fields, hard = None, False
            for attempt in range(1, MAX_ATTEMPTS + 1):
                record["attempts"] = attempt
                wait = min(60, 2 ** attempt) + random.uniform(0, 1)
                try:
                    status, fields = call_model(lane.model, lane.variant, trial["prompt"], key)
                except Exception as e:  # network trouble or an unreadable reply: retry
                    fields = {"error": "network: %s: %s" % (type(e).__name__, e)}
                else:
                    if status == 200:
                        break
                    hdrs = fields.pop("_headers", {})
                    if status in AUTH_STATUS:
                        hard = True
                        with self.lock:
                            lane.halted = "key rejected: %s" % fields["error"][:120]
                        break
                    if status not in RETRY_STATUS:
                        hard = True
                        break
                    retry_after = hdrs.get("retry-after") or hdrs.get("Retry-After")
                    try:
                        wait = min(120.0, float(retry_after)) + random.uniform(0, 0.5)
                    except (TypeError, ValueError):
                        pass
                if attempt < MAX_ATTEMPTS and not self.stop.is_set():
                    self.stop.wait(wait)
                else:
                    break
            fields.pop("_headers", None)
            record.update(fields)
            record["latency_sec"] = round(time.time() - t0, 3)
            self.finish(lane, record, hard)

    def print_status(self, final=False):
        with self.lock:
            planned = sum(l.planned for l in self.lanes)
            done = sum(l.done for l in self.lanes)
            session = sum(l.session_done for l in self.lanes)
            elapsed = time.time() - self.started
            eta = "--"
            if session and not final:
                eta = fmt_dur((planned - done) * elapsed / session)
            money = []
            for p in PROVIDERS:
                proj = self.spent[p]
                for l in self.lanes:
                    if l.model["provider"] == p and l.session_done:
                        proj += (l.planned - l.done) * l.session_cost / l.session_done
                money.append("%s $%.2f (heading for $%.2f of $%g)" % (p, self.spent[p], proj, self.cap))
            pct = 100.0 * done / planned if planned else 100.0
            say("[%s] %d/%d trials (%.0f%%)   running %s   time left %s"
                % (clock(), done, planned, pct, fmt_dur(elapsed), eta))
            say("           " + "   ".join(money))
            for l in self.lanes:
                frac = l.done / l.planned if l.planned else 1.0
                bar = "#" * int(20 * frac) + "-" * (20 - int(20 * frac))
                tail = ""
                if l.halted:
                    tail = "   STOPPED: " + l.halted
                elif l.done >= l.planned:
                    tail = "   done"
                say("  %-20s [%s] %5d/%-5d cut off %-3d errors %-3d $%.2f%s"
                    % (l.model["id"], bar, l.done, l.planned, l.truncated, l.errors, l.session_cost, tail))
            say()


def cmd_run(args):
    batch = args.batch
    reps = args.reps or DEFAULT_REPS[batch]
    models = pick_models(args.models)
    words, word_hash = load_words(batch)
    base_trials = build_trials(batch, words, reps)
    keys = load_keys()
    locked = load_variants()

    if args.dry_run:
        say("Dry run: no API calls.")
        say("Batch %s: %d words x 10 conditions x %d repetitions = %d trials per model, %d models."
            % (batch, len(words), reps, len(base_trials), len(models)))
        say("Word list sha256: %s" % word_hash)
        for t in random.Random(1).sample(base_trials, 3):
            say("  example prompt: " + t["prompt"])
        return 0

    missing = [m["id"] for m in models if m["id"] not in locked]
    if missing:
        sys.exit("No saved request settings for: %s\nRun this first:  python run_bestiary.py check"
                 % ", ".join(missing))
    for m in models:
        if not keys.get(KEY_NAMES[m["provider"]]):
            sys.exit("Missing %s (environment or keys.local)." % KEY_NAMES[m["provider"]])

    out_dir = DATA / batch
    out_dir.mkdir(parents=True, exist_ok=True)
    run = Run(args, keys)
    for m in models:
        variant = next(v for v in m["variants"] if v["name"] == locked[m["id"]]["variant"])
        path = out_dir / ("%s.jsonl" % m["id"])
        done_ids = {r["trial_id"] for r in read_records(path) if r.get("error") is None}
        order = list(base_trials)
        random.Random("%s|%s|%s" % (SEED, batch, m["id"])).shuffle(order)
        if args.limit:
            order = order[:args.limit]
        todo = [t for t in order if t["trial_id"] not in done_ids]
        run.lanes.append(Lane(m, variant, path, todo, len(order) - len(todo), len(order)))

    manifest = out_dir / "manifest.json"
    sessions = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    sessions.append({"started_utc": now_utc(), "batch": batch, "reps": reps, "seed": SEED,
                     "limit": args.limit, "visible_cap": VISIBLE_CAP,
                     "thinking_allowance": THINKING_ALLOWANCE, "workers_per_model": args.workers,
                     "word_list_sha256": word_hash,
                     "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     "python": platform.python_version(),
                     "models": {m["id"]: locked[m["id"]] for m in models}})
    manifest.write_text(json.dumps(sessions, indent=2), encoding="utf-8")

    total_todo = sum(len(l.todo) for l in run.lanes)
    say("Batch '%s': %d trials planned, %d already on disk, %d to collect."
        % (batch, sum(l.planned for l in run.lanes), sum(l.done for l in run.lanes), total_todo))
    say("Spend so far on disk: " + ", ".join("%s $%.2f" % (p, run.spent[p]) for p in PROVIDERS)
        + "   (stop at $%g each)" % run.cap)
    say("Stop any time with Ctrl+C. Rerun the same command to pick up where it left off.\n")
    if not total_todo:
        say("Nothing left to collect for this batch.")
        return 0

    threads = []
    for lane in run.lanes:
        for _ in range(args.workers):
            th = threading.Thread(target=run.worker, args=(lane,), daemon=True)
            th.start()
            threads.append(th)
    last = time.time()
    try:
        while any(th.is_alive() for th in threads):
            time.sleep(0.25)
            if time.time() - last >= args.status_every:
                run.print_status()
                last = time.time()
    except KeyboardInterrupt:
        say("\nStopping: letting requests already in flight finish...")
        run.stop.set()
        for th in threads:
            th.join(timeout=200)
    say("---- final ----")
    run.print_status(final=True)
    left = sum(l.planned - l.done for l in run.lanes)
    if left:
        say("%d trials still to collect. Rerun the same command to continue." % left)
    else:
        say("Batch '%s' is complete." % batch)
    say("Summary any time:  python run_bestiary.py status")
    return 0


# ---------------------------------------------------------------- status
def cmd_status(args):
    if not DATA.exists():
        say("No data yet.")
        return 0
    spent = spend_on_disk()
    for bdir in sorted(p for p in DATA.iterdir() if p.is_dir()):
        say("Batch '%s'" % bdir.name)
        say("  %-20s %7s %7s %8s %9s %8s  %s"
            % ("model", "good", "errors", "cut off", "median", "spent", "flags"))
        for path in sorted(bdir.glob("*.jsonl")):
            best = {}
            errors = 0
            cost = 0.0
            for r in read_records(path):
                cost += float(r.get("est_cost_usd") or 0)
                if r.get("error") is None:
                    best[r["trial_id"]] = r
                else:
                    errors += 1
            recs = list(best.values())
            trunc = [r for r in recs if r.get("truncated")]
            vis = [r["visible_output_tokens"] for r in recs if r.get("visible_output_tokens") is not None]
            flags = []
            cells = {}
            for r in recs:
                c = cells.setdefault(r["condition"], [0, 0])
                c[0] += 1
                c[1] += 1 if r.get("truncated") else 0
            hot = [k for k, (n, t) in cells.items() if n and t / n > 0.01]
            if hot:
                flags.append("TRUNCATION >1% in: " + ", ".join(sorted(hot)))
            if any((r.get("reasoning_tokens") or 0) > 0 or (r.get("thinking_blocks") or 0) > 0 for r in recs):
                flags.append("reasoning present")
            empty = sum(1 for r in recs if not (r.get("response") or "").strip())
            if empty:
                flags.append("%d empty responses" % empty)
            med = "%d tok" % statistics.median(vis) if vis else "--"
            say("  %-20s %7d %7d %8d %9s %8s  %s"
                % (path.stem, len(recs), errors, len(trunc), med, "$%.2f" % cost, "; ".join(flags)))
        say()
    say("Total spend on disk: " + ", ".join("%s $%.2f" % (p, spent[p]) for p in PROVIDERS))
    return 0


# ---------------------------------------------------------------- main
def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description="Bestiary 2 collection runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="one small call per model; saves request settings")
    c.add_argument("--models", nargs="*", help="only these model ids")
    r = sub.add_parser("run", help="collect a batch")
    r.add_argument("batch", choices=["fresh", "known"])
    r.add_argument("--models", nargs="*", help="only these model ids")
    r.add_argument("--reps", type=int, help="repetitions per word and condition")
    r.add_argument("--limit", type=int, help="only the first N trials per model (a short first pass)")
    r.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="parallel requests per model")
    r.add_argument("--spend-cap", type=float, default=SPEND_CAP_USD, help="USD per provider")
    r.add_argument("--status-every", type=float, default=15.0, help="seconds between progress reports")
    r.add_argument("--dry-run", action="store_true", help="show the plan, make no API calls")
    sub.add_parser("status", help="summarize what is on disk")
    args = ap.parse_args()
    return {"check": cmd_check, "run": cmd_run, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
