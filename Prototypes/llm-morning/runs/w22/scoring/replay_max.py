"""No API: replays runs/v22's seed 2 from a temp copy of cache/v22 and prints the largest estimate_tokens(system + prompt)
of the prompts asked from day 3 on, with its scene, as reports/days_v21_plan.md's T2 counted it (the cross-check of W1-8)."""
import os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning, world
SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11):
    SC += [f"night{k-1}", f"mind{k-1}", f"day{k}"]
tmp = tempfile.mkdtemp()
n = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
shutil.copy(os.path.join("cache", "v22", n), os.path.join(tmp, n))
asks, st = [], {"s": 0}
oa, on = gemini.Oracle.ask, gemini.Oracle.new_scene
def new_scene(self):
    st["s"] += 1
    return on(self)
def ask(self, system, prompt, schema=None):
    asks.append((SC[min(st["s"], len(SC) - 1)], re.match(r"You are (\w+),", prompt).group(1), world.estimate_tokens(system + prompt)))
    return oa(self, system, prompt, schema)
gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
try:
    _, code = morning.run(2, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True, days=10)
finally:
    shutil.rmtree(tmp)
a3 = [x for x in asks if SC.index(x[0]) >= SC.index("day3")]
print("replay exit", code, "prompts", len(asks), "from day 3 on", len(a3))
for x in sorted(a3, key=lambda x: -x[2])[:6]:
    print(x)
print("largest by scene:", {sc: max(y[2] for y in a3 if y[0] == sc) for sc in SC[6:] if any(y[0] == sc for y in a3)})
