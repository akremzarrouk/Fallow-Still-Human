"""reports/w1_fixes.md: both fixes, each shown failing without it (block C's water line too). For each: the file is
copied aside, the rule is taken out, the one test is run, and the file is put back and checked by sha256.

    python runs/w1_fixes/red_check.py          (from Prototypes/llm-morning/; no API)
"""
import hashlib
import shutil
import subprocess
import sys

T = "test_morning.PhysicalLayerTest."
CASES = [
    ("quiet.py", "fix 1 out: eating does not move ate_at",
     '''        p.needs["ate_at"] = absolute(self.k, minute)''', '''        return''',
     T + "test_eating_on_a_quiet_day_resets_fasting_at_that_minute"),
    ("night.py", "fix 2 out: the outcome without the water",
     '''        g["outcome"] = outcome_class(st, found, g.get("water", 0))''',
     '''        g["outcome"] = outcome_class(st, found)''',
     T + "test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food"),
    ("memory.py", "fix 2 out: block C's line without the water",
     '''                   " and came back with water" if "with water" in outcome else      # W1 (reports/w1_fixes.md)''',
     '''''',
     T + "test_a_water_haul_from_next_door_still_tells_the_house_it_has_no_food"),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


ok = True
for path, what, old, new, test in CASES:
    before = sha(path)
    shutil.copyfile(path, path + ".bak")
    try:
        s = open(path, encoding="utf-8").read()
        assert s.count(old) == 1, (path, old)
        open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "unittest", test], capture_output=True, text=True, encoding="utf-8",
                           errors="replace",
                           stdin=subprocess.DEVNULL)
        last = [x for x in r.stderr.splitlines() if x.startswith(("FAILED", "OK", "AssertionError", "KeyError"))]
        print(f"{what} ({path}): {test.split('.')[-1]}: exit {r.returncode}; " + " | ".join(x[:160] for x in last[-2:]))
        ok &= r.returncode != 0
    finally:
        shutil.move(path + ".bak", path)
    print(f"  {path} restored: {'sha256 same' if sha(path) == before else 'SHA256 DIFFERS'}")
    ok &= sha(path) == before
print("every one failed without its rule, and every file is restored" if ok else "NOT AS EXPECTED")
sys.exit(0 if ok else 1)
