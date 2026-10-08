"""Which person's morning memory the 560 bound shortened (T2 part 2), and by how much. No API; replay of cache/v21."""
import os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini, memory, morning
SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11): SC += [f"night{k-1}", f"mind{k-1}", f"day{k}"]
st = {"s": 0}
on, ob = gemini.Oracle.new_scene, memory.bounded
def ns(self): st["s"] += 1; return on(self)
def bounded(a, b, c, cap=memory.MEMORY_MAX):
    r = ob(a, b, c, cap)
    f = sys._getframe(1).f_locals
    who = f.get("p") or f.get("pid") or f.get("person") or f.get("who")
    if r["A"] != a[0]:
        print("scene", SC[st["s"]], "person", getattr(who, "id", who), "A variants", [len(x) for x in a], "kept", len(r["A"]), "cap", cap)
        print("A first variant:", a[0][:400]); print("A kept:", r["A"][:400])
    return r
gemini.Oracle.new_scene, memory.bounded = ns, bounded
tmp = tempfile.mkdtemp(); n = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
shutil.copy("cache/v21/" + n, os.path.join(tmp, n))
morning.run(2, replay=True, runs_dir=os.path.join(tmp, "r"), cache_dir=tmp, quiet=True, days=10)
shutil.rmtree(tmp)
