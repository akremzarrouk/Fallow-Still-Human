"""DONE 2 of reports/facts_and_evening.md: v19 seed 3 rebuilt on the new code, with no API call.

    python runs/facts_evening/done2.py          (from Prototypes/llm-morning/, GEMINI_API_KEY unset)

Days 1-2, nights 1-2 and their minds are answered from a temp copy of cache/v19 (their prompts are unchanged). From
day 3 on every prompt is new (the outings line), so each is answered with v19's own recorded answer
(runs/facts_evening/v19_seed3_answers.json): by day, the same scene, speaker and minute, in order; by night, the same
scene, speaker and options; a night mind, the same scene and speaker. An ask v19 did not have (Q5's, or a turn that
went otherwise) is answered "silent", or the first option, and counted. Every prompt sent is kept, by scene.
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
ANSWERS = json.load(open(os.path.join(HERE, "v19_seed3_answers.json"), encoding="utf-8"))


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
                    and (minute is not None or a["options"] == options)), None)
        if hit is not None and json.loads(ANSWERS[hit]["response"])["option"] in options:
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
          f"sent to the recorded client: {client.requests}")
    for s in SCENES[6:]:
        rec = [h for h in client.how if h[0] == s]
        print(f"  {s}: {len(rec)} asks; v19's recorded answer: {sum(h[3] == 'recorded' for h in rec)}; not recorded "
              f"in v19: {[(h[1], h[2], h[4]) for h in rec if h[3] != 'recorded']}")
    json.dump(client.prompts, open(os.path.join(HERE, "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False)
    tr = json.load(open(os.path.join(HERE, "run", "daniel_ate_it-seed3.transcript.json"), encoding="utf-8"))
    for k in ("night2", "night3", "night4"):
        print(f"  {k} groups: {[(g['members'], g.get('far', False), g['street'], g['found'], g['took']) for g in tr[k]['groups']]}")

    def lines(scene, who, prefix):
        return sorted({x for s, p in client.prompts if s == scene and p.startswith(f"You are {who},")
                       for x in p.split("\n") if x.startswith(prefix)})
    print("\n(a) Leo's day-5 prompts, their outings line:")
    for x in lines("day5", "Leo", "About going out at night:"):
        print("  " + x)
    leo5 = [p for s, p in client.prompts if s == "day5" and p.startswith("You are Leo,")]
    both = [p for p in leo5 if "Daniel went to the neighbour's house" in p and "Daniel went further along the street" in p]
    print(f"  Leo's day-5 prompts: {len(leo5)}; carrying both of Daniel's trips: {len(both)}")
    print("\n(b) Leo's day-4 prompts, every line naming Daniel's far offer or 'Daniel says he will not go':")
    leo4 = [p for s, p in client.prompts if s == "day4" and p.startswith("You are Leo,")]
    seen = sorted({x for p in leo4 for x in p.split("\n")
                   if "Daniel offers to go further along" in x or "Daniel says he will not go" in x})
    for x in seen:
        print("  " + x)
    print(f"  Leo's day-4 prompts: {len(leo4)}; with 'Daniel offers to go further along the street tonight': "
          f"{sum('Daniel offers to go further along the street tonight' in p for p in leo4)}; with 'Daniel says he will "
          f"not go': {sum('Daniel says he will not go' in p for p in leo4)}")
    print("\n(c) Mara's day-4 prompts, their street line:")
    for x in lines("day4", "Mara", "About the street:"):
        print("  " + x)
    print("\nAlso, each one's day-4 and day-5 outings and street lines:")
    for scene in ("day4", "day5"):
        for who in ("Daniel", "Elena", "Leo", "Mara"):
            for x in lines(scene, who, "About going out at night:") + lines(scene, who, "About the street:"):
                print(f"  {scene} {who}: {x}")


if __name__ == "__main__":
    main()
