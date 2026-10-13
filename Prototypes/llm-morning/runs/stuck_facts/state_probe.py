"""Read-only, no live call. For the calm probe's 18 asks (runs/calm_probe/probe.py, scenes 1 and 3, 10:00/10:30/11:00):
rebuild the replayed world with the code of the commit that ran calm_variants (76edaa9), and at each calm ask record, for
each person asked: p.history's last entries, World.repeating(p), World.pattern(p), p.activity, and whether the guard
(world.py options_for, last lines) removed any option. The calm probe's own `calm_asks` is called as it is, on the
fake model (FakeClient), in a temp folder; answers are not applied. Usage: cwd = the extracted 76edaa9 copy;
python state_probe.py <out json>"""
import importlib.util, json, os, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
os.environ.pop("GEMINI_API_KEY", None)
import data, quiet, world
from gemini import Cache, FakeClient, Oracle
from talk import SPEECH, act_of
spec = importlib.util.spec_from_file_location("calm_probe_probe", os.path.join("runs", "calm_probe", "probe.py"))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
rows = []
real = probe.calm_asks
def calm_asks(m, minute, calm, out):
    dan = m.people["daniel"]
    for p in sorted([p for p in m.people.values() if p.room == dan.room], key=lambda x: data.ORDER.index(x.id)):
        kind, n = m.repeating(p)
        opts = m.options_for(p)
        rows.append({"scene": out["scene"], "clock": probe.clock(minute), "who": p.id,
                     "resting": m.quiet.resting(p.id), "activity": p.activity,
                     "history_tail": [[h["t"], h["kind"], h["seq"]] for h in p.history[-8:]],
                     "history_len": len(p.history), "repeating": [kind, n],
                     "pattern": m.pattern(p), "guard_would_apply": bool(kind in SPEECH and n >= 3),
                     "options_of_that_kind": [o.id for o in opts if act_of(o.id)[0] == kind],
                     "said_lines": list(p.said_lines[-3:])})
    return real(m, minute, calm, out)
probe.calm_asks = calm_asks
tmp = tempfile.mkdtemp()
try:
    for k, seed in probe.SEEDS.items():
        ledger = {"live": 0, "phases": []}
        client = probe.Capped(FakeClient(invalid_every=0, max_calls=10 ** 6), ledger)
        out = {"scene": k, "seed": seed, "tmp": tmp}
        probe.run_scene(k, os.path.join(tmp, f"scene{k}.json"), client, out)
        print("scene", k, "replay", out["replay"], "calm (fake)", out["calm"], "live ledger", ledger["live"])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1, default=str)
print("rows", len(rows))
