"""reports/w1_impl.md: the four rules added while building W1, each shown failing without it. For each: the file is
copied aside, the rule is taken out, the one test is run, and the file is put back and checked by sha256.

    python runs/w1_impl/red_late.py          (from Prototypes/llm-morning/; no API)
"""
import hashlib
import shutil
import subprocess
import sys

T = "test_morning.PhysicalLayerTest."
CASES = [
    ("world.py", "without the W1 block",
     '''            block += sum(len(x) + 1 for x in head + now if x.startswith("About water:") or x in W1_NOW)''',
     '''            pass''', T + "test_w1_lines_sit_outside_the_budget_and_cut_no_memory_line"),
    ("quiet.py", "Q1 for fasting and debt only",
     '''            if stage < 2 or (pid, need, stage) in self.q1_done:''',
     '''            if stage < 2 or need == "thirst" or (pid, need, stage) in self.q1_done:''',
     T + "test_q1_asks_when_thirst_reaches_badly_thirsty"),
    ("chronicle.py", "the chronicle not keeping World's facts",
     '''            if name not in self.fixed:
                self.fixed[name] =''', '''            if False:
                self.fixed[name] =''', T + "test_the_chronicle_keeps_the_water_fixed_once"),
    ("story.py", "the story without rain and Q6",
     '''    for r in tr.get("rain", []):''', '''    for r in []:''', T + "test_the_story_shows_rain_and_q6"),
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
