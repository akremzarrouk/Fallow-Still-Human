"""No-API replay of v16 seed 2 with --days 10 from cache/v23 (a copy of cache/v16) at HEAD; on the first prompt with no
cached answer, prints its scene index, speaker and "Now" line (reports/v23_plan.md, section 1, guard 1: it must be
scene index 6, day 3). Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset. Same as runs/w22/scoring/premiss.py
with out="v23", and the replay's own files written to a temp folder."""
import os, re, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning

seed = int(sys.argv[1])
orig = gemini.Oracle.ask
state = {"scene": 0, "asks": 0}
orig_new = gemini.Oracle.new_scene
def new_scene(self):
    state["scene"] += 1
    return orig_new(self)
def ask(self, system, prompt, schema=None):
    try:
        r = orig(self, system, prompt, schema)
        state["asks"] += 1
        return r
    except gemini.CacheMiss:
        who = re.match(r"You are (\w+),", prompt).group(1)
        now = [l for l in prompt.splitlines() if l.startswith("Now")]
        first_today = [l for l in prompt.splitlines() if l.startswith("- min 00")]
        print(f"FIRST MISS: scene index {state['scene']}, speaker {who}; Now line: {now[:1]}; "
              f"first 'min 00' line: {first_today[:1]}; answered from the cache before it: {state['asks']}", flush=True)
        raise
gemini.Oracle.ask = ask
gemini.Oracle.new_scene = new_scene
_, code = morning.run(seed, replay=True, out="v23", days=10, runs_dir=tempfile.mkdtemp())
print(f"exit {code}")
sys.exit(code)
