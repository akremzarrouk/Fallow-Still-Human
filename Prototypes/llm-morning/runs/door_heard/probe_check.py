"""reports/door_heard_impl.md: runs/probe_door/probe.py --fake, unchanged, with its temp folder kept, then a check of
each scene: the visitor's words in the knock-minute prompt of everyone asked then who heard the knock in words; what
each one's line of the visit says; the visit's door asks. No API call (the fake model; GEMINI_API_KEY is removed).

    python runs/door_heard/probe_check.py        from Prototypes/llm-morning/
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "runs", "probe_door"))
os.environ.pop("GEMINI_API_KEY", None)
import probe                                            # noqa: E402

keep = tempfile.mkdtemp(prefix="probe_door_fake_")
real_rmtree = shutil.rmtree
probe.tempfile.mkdtemp = lambda: keep                   # the probe's own temp folder, kept for this check
probe.shutil.rmtree = lambda path, ignore_errors=False: None if path == keep else real_rmtree(path, ignore_errors)
real_record = probe.record


def record(m, spec, v, oracle, prompts, knock):
    """The probe's record, plus the scene's new fields (door asks, who saw, what each heard)."""
    rec = real_record(m, spec, v, oracle, prompts, knock)
    q = m.quiet
    sc = q.door_scenes[0] if q.door_scenes else q.door
    if sc and rec["scene"]:
        rec["scene"].update({k: sc[k] for k in ("door_asks", "saw", "heard_said", "by_knock")})
    return rec


probe.record = record
sys.argv = ["probe.py", "--fake"]
code = probe.main()
probe.shutil.rmtree = real_rmtree
print(f"probe.main() returned {code}; scenes in {keep}")
bad = 0
for k in range(1, 9):
    rec = json.load(open(os.path.join(keep, f"scene{k}.json"), encoding="utf-8"))
    sc, knock = rec["scene"], rec["knock"]
    first_at, first = sc["said"][0]
    words = sorted(q for q, how in sc["by_knock"][0][1].items() if how == "words")      # the first knock
    at_knock = [p for p in rec["prompts"] if p["minute"] == knock]
    who_asked = [re.match(r"You are (\w+),", p["prompt"]).group(1).lower() for p in at_knock]
    has = {w: any(f'voice at the front door says: "{first}"' in p["prompt"] for p, w2 in zip(at_knock, who_asked)
                  if w2 == w) for w in who_asked}
    ok = first_at == knock and all(has.get(w) for w in words)
    bad += not ok
    print(f"scene {k} ({rec['spec']['note']}): {'OK' if ok else 'MISSING'}")
    print(f"  first line at {probe.quiet.clock(first_at)}: \"{first}\"")
    print(f"  heard the knock in words: {words}; asked at {probe.quiet.clock(knock)}: {who_asked}; "
          f"the words in their prompt: {has}")
    print(f"  outcome {sc['outcome']}; door asks {sc.get('door_asks')}; stretch asks {sc['asks']}; "
          f"said {[(probe.quiet.clock(m), t) for m, t in sc['said'][1:]]}")
    for q, line in sc["summary"].items():
        print(f"  {q}: {line}")
shutil.rmtree(keep, ignore_errors=True)
print(f"scenes without the visitor's words at the knock: {bad}")
sys.exit(1 if code or bad else 0)
