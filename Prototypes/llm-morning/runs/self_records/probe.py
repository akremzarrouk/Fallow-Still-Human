"""The self-records probe (reports/self_records_plan.md): do people's own records of their acts keep them on one act?

reports/stuck_facts.md: in the calm prompts, with no pattern line, Elena chose reassure_all 24 of 24 and Mara
accuse_daniel 20 of 20. Mara's grudge line lists the times she was angry, yesterday's block counts acts, and
"Your own last words today" lists each person's own last acts.

The 18 stored calm_probe prompts (runs/calm_probe/scene<k>.json: scenes 1 and 3, 10:00 / 10:30 / 11:00, each awake
person in Daniel's room who knows the visit first-hand) are changed by text edits only, every other line byte for byte
the same, in three versions:
- S (self-tallies): in each "Against <Name> (...)" line, the clause "you were angry with <Name> ..." is deleted and its
  causes kept; a line with nothing left is deleted. In "Yesterday and last night:", each "- Accusations: ..." or
  "- Confrontations: ..." line is rewritten as who did it to whom, once, with no count and no minutes
  ("- Mara accused Daniel of taking it.", "- Leo confronted Daniel.").
- W (own acts): "Your own last words today:" and its "- " lines are deleted.
- SW: both.
Each is asked once with calm_probe's client seed (201 scene 1, 202 scene 3), the model and system instruction
calm_probe used (checked: each stored prompt's key, built here with world.SYSTEM, is in cache/calm_probe with the stored
answer). A version that leaves a prompt unchanged takes calm_probe's answer, marked; a prompt already asked in this
probe is not asked again. Answers are recorded and never applied. No live ask past CAP (60) in all. The key is read
from GEMINI_API_KEY only.

    python runs/self_records/probe.py --fake     a temp folder and the fake model; writes nothing in the repository
    python runs/self_records/probe.py --live     cache/self_records/, runs/self_records/; asks Gemini
"""
import argparse
import difflib
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import world                                            # noqa: E402
from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config   # noqa: E402

CAP = 60
MODEL = "gemini-3.5-flash-lite"                         # runs/talk_probe/probe.py, as calm_probe asked
SEEDS = {1: 201, 3: 202}                                # calm_probe's client seed, per scene
BASELINE = os.path.join("runs", "calm_probe")           # scene<k>.json: the 18 stored prompts and answers
BASE_CACHE = os.path.join("cache", "calm_probe")        # scene<k>.json: calm_probe's cache
VERSIONS = ("S", "W", "SW")
NAMES = ("Daniel", "Elena", "Leo", "Mara")
YESTERDAY = "Yesterday and last night:"
OWN = "Your own last words today:"


class Stop(Exception):
    pass


class Capped:
    """The probe's client: no live answer past CAP in all."""

    def __init__(self, inner, ledger):
        self.inner, self.ledger = inner, ledger

    @property
    def requests(self):
        return self.inner.requests

    @property
    def last_prompt_tokens(self):
        return getattr(self.inner, "last_prompt_tokens", None)

    def generate(self, system, prompt, schema=None):
        if self.ledger["live"] >= CAP:
            raise Stop(f"the cap of {CAP} live asks is reached")
        text = self.inner.generate(system, prompt)
        self.ledger["live"] += 1
        return text


def answer_fields(text):
    try:
        a = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip()))
    except ValueError:
        return {"raw": text}
    return a if isinstance(a, dict) else {"raw": text}


def block_end(lines, i):
    """The index after the "- " lines that follow the header at i."""
    j = i + 1
    while j < len(lines) and lines[j].startswith("- "):
        j += 1
    return j


def edit_grudges(lines):
    """S, part 1: the anger clause out of every "Against <Name> (<level>): ..." line."""
    out, edits = [], []
    for x in lines:
        m = re.match(r"^Against (\w+) \(([^)]*)\): (.*)\.$", x)
        if not m or m.group(1) not in NAMES:
            if x.startswith("Against ") and x != "Against the others: nothing.":
                raise Stop(f"an Against line not understood: {x!r}")
            out.append(x)
            continue
        name, level, facts = m.groups()
        c = re.search(r"(?:^|; )you were angry with " + name + r" (.*)$", facts)
        if not c:
            out.append(x)
            continue
        if "you were angry with" in c.group(1):
            raise Stop(f"two anger clauses in one line: {x!r}")
        kept = facts[:c.start()]
        new = f"Against {name} ({level}): {kept}." if kept else None
        if new is not None:
            out.append(new)
        edits.append((x, new))
    return out, edits


def edit_tallies(lines):
    """S, part 2: each Accusations / Confrontations line of "Yesterday and last night:" as who did it to whom, once."""
    if YESTERDAY not in lines:
        return lines, []
    i = lines.index(YESTERDAY)
    j = block_end(lines, i)
    body, edits = [], []
    for x in lines[i + 1:j]:
        m = re.match(r"^- (Accusations|Confrontations): (.*)\.$", x)
        if not m:
            body.append(x)
            continue
        new = []
        for part in m.group(2).split("; "):
            p = re.match(r"^(\w+) (accused|confronted) (\w+)(?: twice| three times| \d+ times)?(?: \(min [^)]*\))?$",
                         part)
            if not p:
                raise Stop(f"a tally not understood: {part!r} in {x!r}")
            who, verb, whom = p.groups()
            who = "You" if who == "you" else who
            new.append(f"- {who} accused {whom} of taking it." if verb == "accused" else f"- {who} confronted {whom}.")
        body += new
        edits.append((x, new))
    return lines[:i + 1] + body + lines[j:], edits


def edit_own(lines):
    """W: "Your own last words today:" and its lines out."""
    if OWN not in lines:
        return lines, []
    i = lines.index(OWN)
    j = block_end(lines, i)
    return lines[:i] + lines[j:], [(x, None) for x in lines[i:j]]


def version(prompt, v):
    lines = prompt.split("\n")
    edits = []
    if "S" in v:
        lines, e1 = edit_grudges(lines)
        lines, e2 = edit_tallies(lines)
        edits += e1 + e2
    if "W" in v:
        lines, e3 = edit_own(lines)
        edits += e3
    return "\n".join(lines), edits


def check_only_edits(base, new, edits):
    """Every line not named in an edit is byte for byte the same, in the same order."""
    old_lines = base.split("\n")
    new_lines = new.split("\n")
    removed = [x for x, _ in edits]
    added = [y for _, n in edits for y in ([n] if isinstance(n, str) else (n or []))]
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    gone, came = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            gone += old_lines[i1:i2]
            came += new_lines[j1:j2]
    assert sorted(gone) == sorted(removed), (gone, removed)
    assert sorted(came) == sorted(added), (came, added)
    kept_old = [x for x in old_lines if x not in removed]
    kept_new = [x for x in new_lines if x not in added]
    assert kept_old == kept_new
    return len(gone), len(came)


def run_scene(k, seed, client, cache_path, out_dir, diff_dir):
    rec = json.load(open(os.path.join(BASELINE, f"scene{k}.json"), encoding="utf-8"))
    assert rec["seed"] == seed
    base_cache = Cache(os.path.join(BASE_CACHE, f"scene{k}.json"))
    oracle = Oracle(Cache(cache_path), MODEL, seed, client=client)
    asked = {}                                          # prompt -> (answer, the ask it came from)
    rows = []
    for mo in rec["moments"]:
        for b in mo["asks"]:
            key = Cache.key(MODEL, seed, world.SYSTEM, b["prompt"])
            if base_cache.get(key) != b["answer"]:
                raise Stop(f"scene {k} {b['clock']} {b['who']}: the stored prompt is not in cache/calm_probe with "
                           f"world.SYSTEM at HEAD")
            for v in VERSIONS:
                prompt, edits = version(b["prompt"], v)
                n_gone, n_came = check_only_edits(b["prompt"], prompt, edits)
                if v == "SW":
                    s_then_w = version(version(b["prompt"], "S")[0], "W")[0]
                    assert prompt == s_then_w
                diff ="\n".join(difflib.unified_diff(
                    b["prompt"].split("\n"), prompt.split("\n"), lineterm="",
                    fromfile=f"calm_probe scene{k} {b['clock']} {b['who']}",
                    tofile=f"{v} scene{k} {b['clock']} {b['who']}", n=1)) + "\n"
                if diff_dir:
                    name = f"scene{k}_{b['clock'].replace(':', '')}_{b['who']}_{v}.diff"
                    with open(os.path.join(diff_dir, name), "w", encoding="utf-8", newline="\n") as f:
                        f.write(diff if prompt != b["prompt"] else "(unchanged)\n")
                if prompt == b["prompt"]:
                    how, text = "calm_probe's answer: the prompt is unchanged, not asked again", b["answer"]
                elif prompt in asked:
                    how, text = f"{asked[prompt][1]}'s answer: the same prompt, not asked again", asked[prompt][0]
                else:
                    live0 = oracle.live
                    text = oracle.ask(world.SYSTEM, prompt)
                    how = "live" if oracle.live > live0 else "from this probe's cache"
                    asked[prompt] = (text, f"{v} {b['clock']} {b['who']}")
                a = answer_fields(text)
                row = {"version": v, "scene": k, "seed": seed, "minute": b["minute"], "clock": b["clock"],
                       "who": b["who"], "how": how, "lines_removed": n_gone, "lines_added": n_came,
                       "edits": [{"old": x, "new": n} for x, n in edits],
                       "offered": b["offered"], "option": a.get("option"), "say": a.get("say"),
                       "feeling": a.get("feeling"), "reason": a.get("reason"), "suspects": a.get("suspects"),
                       "angry_at": a.get("angry_at"), "valid": a.get("option") in b["offered"],
                       "prompt": prompt, "diff": diff, "answer": text,
                       "baseline": {"option": b["option"], "say": b["say"], "feeling": b["feeling"],
                                    "reason": b["reason"]}}
                rows.append(row)
                print(f"  {v:2} scene {k} {b['clock']} {b['who']:5}: -{n_gone} +{n_came} lines; {how}; chose "
                      f"{row['option']} (valid {row['valid']}; calm_probe {b['option']}); say {row['say']!r}",
                      flush=True)
    return rows, {"live": oracle.live, "from_cache": oracle.from_cache, "api_requests": oracle.api_requests}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fake", action="store_true")
    g.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if args.fake:
        os.environ.pop("GEMINI_API_KEY", None)
    else:
        assert os.environ.get("GEMINI_API_KEY"), "the live probe reads GEMINI_API_KEY"
    config = load_config("config.json")
    tmp = tempfile.mkdtemp()
    cache_dir = tmp if args.fake else os.path.join("cache", "self_records")
    out_dir = tmp if args.fake else os.path.join("runs", "self_records")
    diff_dir = os.path.join(out_dir, "diffs")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(diff_dir, exist_ok=True)
    ledger_path = os.path.join(out_dir, "ledger.json")
    ledger = (json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path)
              else {"live": 0, "phases": []})

    def save_ledger():
        with open(ledger_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ledger, f, indent=1)
            f.write("\n")
    code = 0
    try:
        for k, seed in SEEDS.items():
            if any(p["phase"] == f"scene{k}" for p in ledger["phases"]):
                print(f"scene {k}: started already, not run again", flush=True)
                continue
            inner = FakeClient(invalid_every=0, max_calls=10 ** 6) if args.fake else GeminiClient(config, seed)
            client = Capped(inner, ledger)
            phase = {"phase": f"scene{k}", "seed": seed, "live_before": ledger["live"]}
            ledger["phases"].append(phase)
            save_ledger()
            print(f"scene {k} (client seed {seed}):", flush=True)
            stopped, rows, counts = None, [], None
            try:
                rows, counts = run_scene(k, seed, client, os.path.join(cache_dir, f"scene{k}.json"), out_dir,
                                         diff_dir)
            except (Stop, StopMorning) as e:
                stopped = f"{type(e).__name__}: {e}"
                code = 3
            out = {"scene": k, "seed": seed, "asks": rows, "counts": counts, "stopped": stopped}
            with open(os.path.join(out_dir, f"scene{k}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
                f.write("\n")
            phase.update(stopped=stopped, counts=counts, live_after=ledger["live"])
            save_ledger()
            print(f"scene {k}: {len(rows)} rows; counts {counts}; stopped {stopped}", flush=True)
            if stopped:
                break
    finally:
        save_ledger()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"live asks in all: {ledger['live']}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
