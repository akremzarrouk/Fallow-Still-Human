"""Read-only. Replays the v22 run (v16 seed 2, days 3 to 10 live) from a temp copy of cache/v22, with the code of the commit
the run used (a4edf84, runs/v22/plan_frozen.txt), and writes every ask's prompt and answer, by scene, to
runs/stuck_facts/asks_v22.json. No API call: the key must be unset, and a replay refuses a prompt that is not cached.
Usage (cwd = the extracted a4edf84 copy of Prototypes/llm-morning): python collect_v22.py <cache file> <out json>"""
import json, os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY"), "a key is set: this script must make no live call"
src, out = sys.argv[1], sys.argv[2]
import gemini, morning, world
SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11):
    SC += [f"night{k-1}", f"mind{k-1}", f"day{k}"]
tmp = tempfile.mkdtemp()
n = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
shutil.copy(src, os.path.join(tmp, n))
st, asks = {"s": 0}, []
oa, on = gemini.Oracle.ask, gemini.Oracle.new_scene
def new_scene(self):
    st["s"] += 1
    return on(self)
def ask(self, system, prompt, schema=None):
    r = oa(self, system, prompt, schema)
    asks.append({"scene": SC[min(st["s"], len(SC) - 1)], "prompt": prompt, "answer": r})
    return r
gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
try:
    result, code = morning.run(2, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True, days=10)
finally:
    shutil.rmtree(tmp)
print("replay exit", code, "asks", len(asks))
print("answer type", type(asks[0]["answer"]).__name__ if asks else None)
json.dump(asks, open(out, "w"), indent=1, default=str)
