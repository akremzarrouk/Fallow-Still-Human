"""DONE 2 of reports/multiday.md: morning.run(days=5) for v16 seed 2, days 1-2 and nights 1-2 from a copy of
cache/v16 (read only), day 3 on from gemini.FakeClient. No API call. Every prompt the fake client is sent is kept,
with its scene: a day's prompts (day SYSTEM), the night's (NIGHT_SYSTEM), the night mind's (a schema); the scenes come
in order from day 3, so each new run of day prompts is the next day.

    python runs/multiday_fake/fake_run.py        (from Prototypes/llm-morning/)

Writes the run to runs/multiday_fake/run/, the prompts to runs/multiday_fake/prompts.json, and prints the checks.
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402
import morning                                        # noqa: E402
from gemini import FakeClient                         # noqa: E402
from world import NIGHT_SYSTEM, SYSTEM                # noqa: E402

MODEL = "gemini-3.5-flash-lite"
NAME = "daniel_ate_it-seed2"
OUT = os.path.join("runs", "multiday_fake")
RUN = os.path.join(OUT, "run")


class Recording(FakeClient):
    def __init__(self):
        super().__init__(invalid_every=0, max_calls=10 ** 6)
        self.prompts = []           # (scene, prompt)
        self.order = iter(["day3", "night3", "mind3", "day4", "night4", "mind4", "day5"])
        self.scene, self.kind = None, None

    def generate(self, system, prompt, schema=None):
        kind = "mind" if schema is not None else "night" if system == NIGHT_SYSTEM else "day"
        assert kind != "day" or system == SYSTEM
        if kind != self.kind:
            self.scene, self.kind = next(self.order), kind
            assert self.scene.startswith(kind), (self.scene, kind)
        self.prompts.append((self.scene, prompt))
        return super().generate(system, prompt, schema)


tmp = tempfile.mkdtemp()
shutil.copyfile(os.path.join("cache", "v16", f"{MODEL}-{NAME}.json"), os.path.join(tmp, f"{MODEL}-{NAME}.json"))
shutil.rmtree(RUN, ignore_errors=True)
client = Recording()
meta, code = morning.run(2, client=client, runs_dir=RUN, cache_dir=tmp, days=5)
shutil.rmtree(tmp)
json.dump(client.prompts, open(os.path.join(OUT, "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nexit code {code}")
if code:
    sys.exit(code)

tr = json.load(open(os.path.join(RUN, f"{NAME}.transcript.json"), encoding="utf-8"))
by = {}
for scene, p in client.prompts:
    by.setdefault(scene, []).append(p)
print("prompts sent to the fake client, by scene:", {k: len(v) for k, v in by.items()})
print(f"days in the transcript: {[k for k in tr if k.startswith('day')]}; day 5's last span ends at "
      f"{data.clock(max(s['end'] for s in tr['day5']['quiet']['spans']))}; meta days {meta['days']}")

# Day-3 afternoon anger: each model act from 08:30 on that named someone.
afternoon = [(a["who"], a["angry_at"], a["minute"]) for t in tr["day3"]["turns"] for a in t["acts"]
             if a["mode"] == "model" and a["minute"] >= data.CLOCK_FROM
             and a.get("angry_at") not in (None, "nobody", data.PEOPLE[a["who"]]["name"])]   # naming yourself: nobody
print(f"day-3 model acts from 08:30 on naming someone as angry_at: {len(afternoon)}")
later = [(s, p) for s in ("night3", "mind3", "day4", "night4", "mind4", "day5") for p in by.get(s, [])]
days45 = [(s, p) for s, p in later if s in ("day4", "day5")]
bad_last = [(s, line) for s, p in days45 for line in p.splitlines()
            if re.search(r"last night at|the night before last at|tonight at", line)]
print(f"day-4 and day-5 prompts: {len(days45)}; lines with a night word followed by 'at' (a minute): {len(bad_last)}")
# Each holder's first day-4 prompt: the 'Against <target>' line names yesterday, with the clock of their latest
# afternoon anger at that target.
seen = set()
for who, target, minute in sorted(afternoon, key=lambda x: -x[2]):
    if (who, target) in seen:
        continue
    seen.add((who, target))
    first = next(p for p in by["day4"] if p.startswith(f"You are {data.PEOPLE[who]['name']},"))
    line = next((x for x in first.splitlines() if x.startswith(f"Against {target} ")), None)
    ok = None if line is None else re.search(rf"yesterday at [^;]*{data.clock(minute)}", line) is not None
    print(f"  {data.PEOPLE[who]['name']} -> {target}, last afternoon anger {data.clock(minute)}: day-4 line has "
          f"'yesterday at … {data.clock(minute)}': {'no such line (no grudge held at 07:00)' if ok is None else ok}")
    if line is not None:
        print(f"    {line}")
# A night event never as a clock: the night's answers keep 21:00 after a quiet day. Outside the span ends
# ("… to 21:00)", "from 20:33 to 21:00.") of the gap line and the records, no 21:00 anywhere; and 08:30 only if a played turn was at minute 90.
stray = [(s, line) for s, p in later for line in p.splitlines() if "21:00" in re.sub(r"to 21:00\b", "", line)]
at90 = [k for k in ("day3", "day4", "day5") if any(t["minute"] == 90 for t in tr[k]["turns"])]
eighty = [(s, line) for s, p in later for line in p.splitlines() if "08:30" in line]
print(f"prompts from night 3 to day 5: {len(later)}; lines with 21:00 outside a span's end: {len(stray)}; days with a "
      f"played turn at 08:30: {at90}; lines with 08:30: {len(eighty)}")
for s, line in (stray + eighty)[:6]:
    print(f"  {s}: {line[:200]}")
# The scene of every grudge and guilt event at the end of day 5, as tag_events wrote it: a day's event is before
# 21:00, a night's at 21:00 (days 3 and 4) or 90 (days 1 and 2).
wrong, n = [], 0
for pid, st in tr["day5"]["final_state"].items():
    for target, g in st["grudges"].items():
        for e in g["events"]:
            if len(e) < 5:
                continue                    # day 5's own events, not tagged yet
            n += 1
            kind, k = e[4]
            night_from = 840 if k >= 3 else 90
            if (kind == "N") != (e[0] >= night_from):
                wrong.append((pid, target, e[:5]))
print(f"tagged grudge events at the end of day 5: {n}; with a scene that does not match their minute: {len(wrong)}")
for x in wrong[:5]:
    print(f"  {x}")
tagged = {}
for pid, st in tr["day5"]["final_state"].items():
    for target, g in st["grudges"].items():
        for e in g["events"]:
            if len(e) >= 5 and e[4][1] >= 3:
                tagged.setdefault(tuple(e[4]), []).append(e[0])
print("minutes by scene, days and nights 3-4: "
      + "; ".join(f"{s[0]}{s[1]}: {min(v)}..{max(v)} ({len(v)})" for s, v in sorted(tagged.items())))
