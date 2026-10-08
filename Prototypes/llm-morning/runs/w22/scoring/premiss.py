"""No-API replay of one seed with --days 10 from cache/v21; on the first prompt with no cached answer, prints its
scene, speaker and "Now" line. Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset."""
import os, re, sys
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning

seed = int(sys.argv[1])
orig = gemini.Oracle.ask
state = {"scene": 0}
orig_new = gemini.Oracle.new_scene
def new_scene(self):
    state["scene"] += 1
    return orig_new(self)
def ask(self, system, prompt, schema=None):
    try:
        return orig(self, system, prompt, schema)
    except gemini.CacheMiss:
        who = re.match(r"You are (\w+),", prompt).group(1)
        now = [l for l in prompt.splitlines() if l.startswith("Now")]
        first_today = [l for l in prompt.splitlines() if l.startswith("- min 00")]
        print(f"FIRST MISS: scene index {state['scene']}, speaker {who}; Now line: {now[:1]}; "
              f"first 'min 00' line: {first_today[:1]}", flush=True)
        raise
gemini.Oracle.ask = ask
gemini.Oracle.new_scene = new_scene
_, code = morning.run(seed, replay=True, out="v22", days=10)
print(f"exit {code}")
sys.exit(code)
