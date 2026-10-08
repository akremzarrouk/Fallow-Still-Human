"""Rebuild the four night-8 bedtime prompts of v21 exactly (no API): a replay of cache/v21 from a temp copy, keeping the
system prompt and prompt of every night8 ask, and checking each against its cache key. Run from llm-morning/ with
GEMINI_API_KEY unset. Writes runs/probe_stakes/cases/<person>_control.txt and system.txt."""
import os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning
MODEL, SEED = "gemini-3.5-flash-lite", 2
SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11): SC += [f"night{k-1}", f"mind{k-1}", f"day{k}"]
st, got = {"s": 0}, []
on, oa = gemini.Oracle.new_scene, gemini.Oracle.ask
def ns(self): st["s"] += 1; return on(self)
def ask(self, system, prompt, schema=None):
    if SC[st["s"]] == "night8":
        got.append((system, prompt))
    return oa(self, system, prompt, schema)
gemini.Oracle.new_scene, gemini.Oracle.ask = ns, ask
tmp = tempfile.mkdtemp(); n = f"{MODEL}-daniel_ate_it-seed2.json"
shutil.copy("cache/v21/" + n, os.path.join(tmp, n))
morning.run(SEED, replay=True, runs_dir=os.path.join(tmp, "r"), cache_dir=tmp, quiet=True, days=10)
cache = gemini.Cache(os.path.join("cache", "v21", n))
os.makedirs("runs/probe_stakes/cases", exist_ok=True)
print("night8 asks:", len(got))
for system, prompt in got:
    who = re.match(r"You are (\w+),", prompt).group(1).lower()
    key = gemini.Cache.key(MODEL, SEED, system, prompt)
    print(who, "cache key recomputed matches an entry of cache/v21:", key in cache.entries, "|", len(prompt.split("\n")), "lines")
    open(f"runs/probe_stakes/cases/{who}_control.txt", "w", encoding="utf-8", newline="\n").write(prompt)
    open("runs/probe_stakes/cases/system.txt", "w", encoding="utf-8", newline="\n").write(system)
shutil.rmtree(tmp)
