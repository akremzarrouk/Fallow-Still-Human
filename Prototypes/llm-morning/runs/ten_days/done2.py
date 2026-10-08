"""DONE 2 of reports/ten_days_prep.md: v20 seed 3 rebuilt on the new code, with no API call, and its day-4 positions.

    python runs/ten_days/done2.py          (from Prototypes/llm-morning/, GEMINI_API_KEY unset)

As runs/household/done2.py, from v20: days 1-2, nights 1-2 and minds 1-2 from a temp copy of cache/v20; from day 3
on, v20's own recorded answers (runs/ten_days/v20_seed3_answers.json, by runs/ten_days/v20_answers.py). By day: the
same scene, speaker and minute. By night: the same scene and speaker, with the recorded options all still offered. A
night mind: the same scene and speaker. An ask v20 did not have is answered "silent" (or the first option).
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
ANSWERS = json.load(open(os.path.join(HERE, "v20_seed3_answers.json"), encoding="utf-8"))
SAID = "- What was said yesterday about going out last night, where it was left: "


class Recorded:
    def __init__(self):
        self.requests, self.scene, self.model = 0, 0, "recorded"
        self.used, self.prompts, self.how = set(), [], []

    def new_scene(self):
        self.scene += 1

    def generate(self, system, prompt, schema=None):
        self.requests += 1
        scene = SCENES[self.scene]
        self.prompts.append((scene, prompt))
        who = re.match(r"You are (\w+),", prompt).group(1).lower()
        m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
        minute = None if not m else int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - 420
        options = None if schema is not None else re.findall(r"^- (\w+):", prompt.split("Your options:")[-1],
                                                             flags=re.M)
        for i, a in enumerate(ANSWERS):
            if i in self.used or a["scene"] != scene or a["person"] != who:
                continue
            if schema is not None or (a["minute"] == minute and (minute is not None or set(a["options"]) <= set(options))
                                      and json.loads(a["response"])["option"] in options):
                self.used.add(i)
                self.how.append((scene, who, minute, "recorded"))
                return a["response"]
        pick = "silent" if "silent" in options else options[0]
        self.how.append((scene, who, minute, f"not recorded: {pick}"))
        return json.dumps({"option": pick, "say": None, "feeling": "tired", "reason": "Not recorded in v20.",
                           "suspects": "nobody", "angry_at": "nobody"})


def main():
    tmp = tempfile.mkdtemp()
    name = "gemini-3.5-flash-lite-daniel_ate_it-seed3.json"
    shutil.copy(os.path.join("cache", "v20", name), os.path.join(tmp, name))
    client = Recorded()
    meta, code = morning.run(3, client=client, runs_dir=os.path.join(HERE, "run"), cache_dir=tmp, quiet=True, days=5)
    shutil.rmtree(tmp)
    print(f"exit {code}; answers from cache/v20 (days 1-2, nights 1-2, minds 1-2): {meta['answers_from_cache']}; sent to "
          f"the recorded client: {client.requests}; v20's recorded answers used: {len(client.used)} of {len(ANSWERS)}")
    for s in SCENES[6:]:
        rec = [h for h in client.how if h[0] == s]
        print(f"  {s}: {len(rec)} asks; recorded {sum(h[3] == 'recorded' for h in rec)}; not recorded "
              f"{[(h[1], h[2], h[3]) for h in rec if h[3] != 'recorded']}")
    tr = json.load(open(os.path.join(HERE, "run", "daniel_ate_it-seed3.transcript.json"), encoding="utf-8"))
    for k in ("night2", "night3", "night4"):
        print(f"  {k} groups: {[(g['members'], g.get('far', False), g['street'], g['found'], g['took']) for g in tr[k]['groups']]}")
    for scene in ("day4", "day5"):
        print(f"\n{scene}, each one's carried-in positions line:")
        for who in ("Daniel", "Elena", "Leo", "Mara"):
            lines = sorted({x for s, p in client.prompts if s == scene and p.startswith(f"You are {who},")
                            for x in p.split("\n") if x.startswith(SAID)})
            for x in lines:
                print(f"  {who}: {x}")


if __name__ == "__main__":
    main()
