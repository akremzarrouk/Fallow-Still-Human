"""DONE 2 and 3 of reports/stage_b.md: morning.run(days=5) for v16 seed 2, days 1-2 and nights 1-2 from a copy of
cache/v16 (read only), day 3 on from gemini.FakeClient. No API call, and no production code is changed: night 3's
draws are forced here by wrapping Night.u.

    python runs/stage_b_fake/fake_run.py food     night 3: the far trip is clean, and the first house holds 4
    python runs/stage_b_fake/fake_run.py lost     night 3: the far trip does not come back

The first time anyone is offered `go_further` at bedtime, they take it; every other answer is FakeClient's. Every
prompt is kept with its scene (runs/stage_b_fake/<mode>/prompts.json); the run is in runs/stage_b_fake/<mode>/run/.
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import morning                                        # noqa: E402
import night                                          # noqa: E402
from gemini import FakeClient                         # noqa: E402
from world import NIGHT_SYSTEM, SYSTEM                # noqa: E402

MODE = sys.argv[1]
MODEL = "gemini-3.5-flash-lite"
NAME = "daniel_ate_it-seed2"
OUT = os.path.join("runs", "stage_b_fake", MODE)
RUN = os.path.join(OUT, "run")
FORCE = {"food": {(3, "trip_far:daniel"): 0.0, (3, "far_house:0"): 0.8},
         "lost": {(3, "trip_far:daniel"): 0.99}}[MODE]

real_u = night.Night.u


def forced_u(self, name):
    key = (self.number, name)
    return FORCE[key] if key in FORCE else real_u(self, name)


night.Night.u = forced_u


class Recording(FakeClient):
    def __init__(self):
        super().__init__(invalid_every=0, max_calls=10 ** 6)
        self.prompts = []
        self.order = iter(["day3", "night3", "mind3", "day4", "night4", "mind4", "day5"])
        self.scene, self.kind = None, None
        self.first_far = None

    def generate(self, system, prompt, schema=None):
        kind = "mind" if schema is not None else "night" if system == NIGHT_SYSTEM else "day"
        assert kind != "day" or system == SYSTEM
        if kind != self.kind:
            self.scene, self.kind = next(self.order), kind
        self.prompts.append((self.scene, prompt))
        if kind == "night" and "\n- go_further:" in prompt and self.first_far is None:
            self.first_far = (self.scene, prompt)
            self.far_who = re.match(r"You are (\w+),", prompt).group(1)
            return self.answer("go_further", "Next door is empty; the houses further along are the only chance.")
        # That night, whoever chose it keeps to it: lets anyone else go their way, goes later, goes all the same.
        if (kind == "night" and self.first_far and self.scene == self.first_far[0]
                and prompt.startswith(f"You are {self.far_who},")):
            opts = re.findall(r"^- (\w+):", prompt.split("Your options:")[-1], flags=re.M)
            mine = next((o for o in opts if o.startswith("let_") or o in ("go_later", "go_anyway")), None)
            if mine:
                return self.answer(mine, "I am going further along, on my own.")
        return super().generate(system, prompt, schema)

    def answer(self, option, reason):
        self.requests += 1
        return json.dumps({"option": option, "say": None, "feeling": "determined", "reason": reason,
                           "suspects": "nobody", "angry_at": "nobody"})


tmp = tempfile.mkdtemp()
shutil.copyfile(os.path.join("cache", "v16", f"{MODEL}-{NAME}.json"), os.path.join(tmp, f"{MODEL}-{NAME}.json"))
shutil.rmtree(RUN, ignore_errors=True)
os.makedirs(OUT, exist_ok=True)
client = Recording()
meta, code = morning.run(2, client=client, runs_dir=RUN, cache_dir=tmp, days=5)
shutil.rmtree(tmp)
json.dump(client.prompts, open(os.path.join(OUT, "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if client.first_far:
    open(os.path.join(OUT, "first_w5_bedtime_prompt.txt"), "w", encoding="utf-8", newline="\n").write(
        client.first_far[1] + "\n")
print(f"\nexit code {code}")
if code:
    sys.exit(code)
tr = json.load(open(os.path.join(RUN, f"{NAME}.transcript.json"), encoding="utf-8"))
by = {}
for scene, p in client.prompts:
    by.setdefault(scene, []).append(p)
print("prompts by scene:", {k: len(v) for k, v in by.items()})
who = re.match(r"You are (\w+),", client.first_far[1]).group(1) if client.first_far else None
print(f"first offered go_further at bedtime: {who} ({client.first_far[0] if client.first_far else None})")
n3 = tr["night3"]
for g in n3["groups"]:
    print(f"night 3 group: members {g['members']}, far {g.get('far')}, street {g['street']} (u {g['u']}), found "
          f"{g['found']}, took {g['took']}, lost {g['lost']}, table {g.get('table')}")
print(f"night 3: shelf {n3['portions_before']} -> {n3['portions_after']}; away {n3['away']}; far {n3.get('far')}")
q5 = tr["day5"]["quiet"]
print(f"day 5 reaches bedtime: last span ends {max(s['end'] for s in q5['spans'])}, last played stretch ends "
      f"{q5['stretches'][-1]['end']} (bedtime is 840); meta days {meta['days']}")
if MODE == "food":
    opening = tr["day4"]["final_state"]          # the shelf at day 4's start is in the opening line
    first4 = by["day4"][0]
    sure = next(x for x in first4.splitlines() if x.startswith("- min 00: "))
    print(f"day 4 opening line (first day-4 prompt): {sure}")
    eats = sum("\n- eat: eat one of the portions" in p for p in by["day4"])
    print(f"day-4 prompts offering eat: {eats} of {len(by['day4'])}")
    ate = [(a["minute"], a["who"], a["option"]) for t in tr["day4"]["turns"] for a in t["acts"]
           if a["option"] in ("eat", "share", "eat_given") or a["option"].startswith("give_")]
    print(f"day-4 food acts: {ate}; shelf at day 4's end {tr['day4']['final_state'].get('portions') if isinstance(tr['day4']['final_state'], dict) else None}")
else:
    later = [(s, p) for s in ("night3", "mind3", "day4", "night4", "mind4", "day5") for s_, p in client.prompts
             if s_ == s]
    after = [s for s, p in later if p.startswith("You are Daniel,")]
    n3_daniel = [p for p in by["night3"] if p.startswith("You are Daniel,")]
    print(f"Daniel's night-3 prompts: {len(n3_daniel)} (bedtime, before he went)")
    print(f"prompts to Daniel after he went out on night 3 (mind 3 to day 5): "
          f"{sum(1 for s, p in later if s != 'night3' and p.startswith('You are Daniel,'))}")
    for k in ("day4", "day5"):
        d = tr[k]
        acts = [a for t in d["turns"] for a in t["acts"] if a["who"] == "daniel"]
        rooms = [r for t in d["turns"] for r, ids in t["rooms"].items() if "daniel" in ids]
        print(f"{k}: Daniel's acts {len(acts)}, rooms holding him {len(rooms)}, in its needs log "
              f"{'daniel' in d['quiet']['needs']}, spans of his {sum(s['who'] == 'daniel' for s in d['quiet']['spans'])}")
    print(f"night4: asked {sorted({x['person'] for x in tr['night4']['decisions']})}; mind4: asked {sorted(tr['mind4'])}")
    for q in (x for x in ("elena", "leo", "mara") if x not in n3["away"]):
        p = next(p for p in by["day4"] if p.startswith(f"You are {q.capitalize()},"))
        print(f"  {q}'s first day-4 prompt: " + " | ".join(
            x for x in p.splitlines() if "Daniel is not here" in x or x.startswith("About Daniel:")))
