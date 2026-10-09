"""reports/w2a_impl.md, DONE 4: a no-API replay of v16 seed 2 with --days 10, from a temp copy of cache/v16 (never
written); prints the first prompt with no cached answer: its scene, speaker and "Now" line. Run from
Prototypes/llm-morning/ with GEMINI_API_KEY unset."""
import hashlib, os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning

NAME = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
src = os.path.join("cache", "v16", NAME)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
before = sha(src)
tmp = tempfile.mkdtemp()
shutil.copyfile(src, os.path.join(tmp, NAME))
state = {"scene": 0}
orig, orig_new = gemini.Oracle.ask, gemini.Oracle.new_scene
def new_scene(self):
    state["scene"] += 1
    return orig_new(self)
def ask(self, system, prompt, schema=None):
    try:
        return orig(self, system, prompt, schema)
    except gemini.CacheMiss:
        who = re.match(r"You are (\w+),", prompt).group(1)
        now = [l for l in prompt.splitlines() if l.startswith("Now")]
        print(f"FIRST MISS: scene index {state['scene']}, speaker {who}; Now line: {now[:1]}", flush=True)
        raise
gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
try:
    _, code = morning.run(2, replay=True, days=10, runs_dir=tmp, cache_dir=tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"exit {code}; cache/v16 sha256 before {before[:16]}, after {sha(src)[:16]}: {'unchanged' if before == sha(src) else 'CHANGED'}")
