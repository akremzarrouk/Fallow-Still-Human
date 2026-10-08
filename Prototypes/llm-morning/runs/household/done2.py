"""DONE 2 of reports/household_knowledge.md: v19 seed 3 rebuilt on the new code, with no API call, and Elena's day 4.

    python runs/household/done2.py          (from Prototypes/llm-morning/, GEMINI_API_KEY unset)

As runs/facts_evening/done2.py: days 1-2, nights 1-2 and minds 1-2 from a temp copy of cache/v19; from day 3 on, v19's
own recorded answers (runs/facts_evening/v19_seed3_answers.json). By day: the same scene, speaker and minute. By night:
the same scene and speaker, with the recorded options all still offered (Elena's bedtimes now also offer go_further).
A night mind: the same scene and speaker. An ask v19 did not have is answered "silent" (or the first option).
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import morning              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = ["day1", "night", "mind1", "day2", "night2", "mind2", "day3", "night3", "mind3", "day4", "night4", "mind4",
          "day5"]
ANSWERS = json.load(open(os.path.join(HERE, "..", "facts_evening", "v19_seed3_answers.json"), encoding="utf-8"))


class Recorded:
    def __init__(self):
        self.requests, self.scene, self.model = 0, 0, "recorded"
        self.used = set()
        self.prompts = []           # (scene, prompt)
        self.how = []               # (scene, who, minute, "recorded" | "not recorded", option)

    def new_scene(self):
        self.scene += 1

    def generate(self, system, prompt, schema=None):
        self.requests += 1
        scene = SCENES[self.scene]
        self.prompts.append((scene, prompt))
        who = re.match(r"You are (\w+),", prompt).group(1).lower()
        if schema is not None:
            hit = next((i for i, a in enumerate(ANSWERS) if i not in self.used and a["scene"] == scene
                        and a["person"] == who), None)
            self.used.add(hit)
            self.how.append((scene, who, None, "recorded", None))
            return ANSWERS[hit]["response"]
        m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
        minute = None if not m else int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - 420
        options = re.findall(r"^- (\w+):", prompt.split("Your options:")[-1], flags=re.M)
        hit = next((i for i, a in enumerate(ANSWERS) if i not in self.used and a["scene"] == scene
                    and a["person"] == who and a["minute"] == minute
                    and (minute is not None or set(a["options"]) <= set(options))
                    and json.loads(a["response"])["option"] in options), None)
        if hit is not None:
            self.used.add(hit)
            ans = ANSWERS[hit]["response"]
            self.how.append((scene, who, minute, "recorded", json.loads(ans)["option"]))
            return ans
        pick = "silent" if "silent" in options else options[0]
        self.how.append((scene, who, minute, "not recorded", pick))
        return json.dumps({"option": pick, "say": None, "feeling": "tired", "reason": "Not recorded in v19.",
                           "suspects": "nobody", "angry_at": "nobody"})


def main():
    tmp = tempfile.mkdtemp()
    name = "gemini-3.5-flash-lite-daniel_ate_it-seed3.json"
    os.makedirs(os.path.join(tmp, "cache"))
    shutil.copy(os.path.join("cache", "v19", name), os.path.join(tmp, "cache", name))
    client = Recorded()
    meta, code = morning.run(3, client=client, runs_dir=os.path.join(HERE, "run"),
                             cache_dir=os.path.join(tmp, "cache"), quiet=True, days=5)
    shutil.rmtree(tmp)
    print(f"exit {code}; answers from cache/v19 (days 1-2, nights 1-2, minds 1-2): {meta['answers_from_cache']}; "
          f"sent to the recorded client: {client.requests}; v19's recorded answers used: {len(client.used)} of "
          f"{len(ANSWERS)}")
    for s in SCENES[6:]:
        rec = [h for h in client.how if h[0] == s]
        print(f"  {s}: {len(rec)} asks; v19's recorded answer: {sum(h[3] == 'recorded' for h in rec)}; not recorded "
              f"in v19: {[(h[1], h[2], h[4]) for h in rec if h[3] != 'recorded']}")
    tr = json.load(open(os.path.join(HERE, "run", "daniel_ate_it-seed3.transcript.json"), encoding="utf-8"))
    for k in ("night2", "night3", "night4"):
        print(f"  {k} groups: {[(g['members'], g.get('far', False), g['street'], g['found'], g['took']) for g in tr[k]['groups']]}")
    print(f"  night3 bedtimes: {tr['night3']['choices']}")

    elena4 = [p for s, p in client.prompts if s == "day4" and p.startswith("You are Elena,")]
    print(f"\nElena's day-4 prompts: {len(elena4)}")
    for prefix in ("About the neighbour's house:", "About the street:", "About going out at night:", "The house:"):
        lines = sorted({x for p in elena4 for x in p.split("\n") if x.startswith(prefix)})
        for x in lines:
            print(f"  {x if prefix != 'The house:' else '... ' + x[x.index('Outside'):]}")
    far = [p for p in elena4 if "\n- propose_far: " in p and "\n- volunteer_far: " in p]
    print(f"  with propose_far and volunteer_far offered: {len(far)} of {len(elena4)}")
    for x in sorted({x for p in elena4 for x in p.split("\n") if x.startswith(("- propose_far:", "- volunteer_far:"))}):
        print("  " + x)
    beds = [p for s, p in client.prompts if s == "night4" and p.startswith("You are Elena,") and "- sleep:" in p]
    print(f"  her night-4 bedtime offers go_further: {[('- go_further: ' in p) for p in beds]}")


if __name__ == "__main__":
    main()
