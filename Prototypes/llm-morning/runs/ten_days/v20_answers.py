"""v20 seed N's answers from day 3 on, each with its scene, speaker, minute and options, for DONE 2 of
reports/ten_days_prep.md. Replays cache/v20 (a temp copy) with no API on the code in CODE_DIR: v20's own code, HEAD
361eb30, exported there.

    python runs/ten_days/v20_answers.py CODE_DIR SEED OUT_JSON      (from Prototypes/llm-morning/)
"""
import json
import os
import re
import shutil
import sys
import tempfile

code_dir, seed, out_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
here = os.getcwd()
sys.path.insert(0, os.path.abspath(code_dir))
assert not os.environ.get("GEMINI_API_KEY")
import gemini               # noqa: E402
import morning              # noqa: E402

SCENES = ["day1", "night", "mind1", "day2", "night2", "mind2", "day3", "night3", "mind3", "day4", "night4", "mind4",
          "day5"]
name = f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"
tmp = tempfile.mkdtemp()
shutil.copy(os.path.join(here, "cache", "v20", name), os.path.join(tmp, name))
state, out = {"scene": 0}, []
orig_ask, orig_new = gemini.Oracle.ask, gemini.Oracle.new_scene


def new_scene(self):
    state["scene"] += 1
    return orig_new(self)


def ask(self, system, prompt, schema=None):
    text = orig_ask(self, system, prompt, schema)
    scene = SCENES[state["scene"]]
    if SCENES.index(scene) >= SCENES.index("day3"):
        m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
        minute = None if not m else int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - 420
        out.append({"scene": scene, "person": re.match(r"You are (\w+),", prompt).group(1).lower(), "minute": minute,
                    "options": None if schema is not None else
                    re.findall(r"^- (\w+):", prompt.split("Your options:")[-1], flags=re.M),
                    "response": text})
    return text


gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
_, code = morning.run(seed, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True, days=5)
shutil.rmtree(tmp)
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"seed {seed}: replay exit {code} (1: no original story in the temp folder); answers from day 3 on: {len(out)}; "
      f"by scene {dict((s, sum(a['scene'] == s for a in out)) for s in SCENES[6:])}")
