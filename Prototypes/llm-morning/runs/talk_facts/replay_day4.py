"""reports/talk_facts.md, question 5: scene 1 of runs/probe_after replayed from its own cache, with no live call, to
read day 4's water lines, which the probe built (night.next_day -> quiet.setup -> Quiet.tick(0) -> Quiet.sense) but did
not save. The code is the repository at cb5b6bf (the probe's code: its .py files equal f4f2d2c's, the HEAD the probe
ran at), unpacked outside the repository; this script reads it and writes nothing there.

The client raises on any ask: every answer must come from the cache, or the replay stops (CacheMiss / NoLiveCall).
A replay is taken as the probe's run only if its day-4 blocks equal those saved in runs/probe_after/scene1.json.

    python runs/talk_facts/replay_day4.py <unpacked Prototypes/llm-morning at cb5b6bf>      from Prototypes/llm-morning/
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.getcwd()
CODE = os.path.abspath(sys.argv[1])
SAVED = json.load(open(os.path.join(HERE, "runs", "probe_after", "scene1.json"), encoding="utf-8"))
os.chdir(CODE)
sys.path.insert(0, CODE)
os.environ.pop("GEMINI_API_KEY", None)

spec_ = importlib.util.spec_from_file_location("probe_after_probe", os.path.join(CODE, "runs", "probe_after", "probe.py"))
probe = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(probe)
import night as nightmod        # noqa: E402  (the unpacked code's)


class NoLiveCall(Exception):
    pass


class NoClient:
    """Stands where the Gemini client stood: any ask the cache cannot answer stops the replay."""
    requests, allow, last_prompt_tokens = 0, True, None

    def generate(self, system, prompt, schema=None):
        raise NoLiveCall("an ask with no cached answer: the replay is not the probe's run")


tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "scene1.json")
shutil.copyfile(os.path.join(CODE, "cache", "probe_after", "scene1.json"), path)
spec = next(v for v in probe.VISITORS if v["scene"] == 1)
captured = {}
real_next_day = nightmod.next_day


def next_day(*a, **k):
    m = real_next_day(*a, **k)
    captured["d4"] = m
    return m


nightmod.next_day = next_day
out = {"spec": spec}
probe.run_scene(spec, path, NoClient(), out)
oracle = out["oracle"]
print(f"code: {CODE}")
print(f"replay reached: {out['reached']}; from_cache {oracle.from_cache}; live {oracle.live}; "
      f"api_requests {oracle.api_requests}")
same = json.dumps(out["day4_blocks"], sort_keys=True) == json.dumps(SAVED["day4_blocks"], sort_keys=True)
print(f"day-4 blocks equal to runs/probe_after/scene1.json's: {same}")
same_minds = all(out["minds"][p]["answer"] == SAVED["minds"][p]["answer"] for p in SAVED["minds"])
print(f"night-3 mind answers equal to the saved ones: {same_minds}")

d4 = captured["d4"]
print(f"\nday 4: m.day {d4.day}; quiet {'set up' if d4.quiet is not None else 'None'}; away {sorted(d4.away)}")
for pid in ("daniel", "elena", "leo", "mara"):
    p = d4.people[pid]
    print(f"\n== {pid}")
    print(f"  p.water['line'] at day 4 min 00: {p.water['line'] if p.water else None}")
    print(f"  m.carry[{pid}] (C + A + B, as next_day sets it):")
    for x in d4.carry[pid]:
        print(f"    | {x}")
    try:
        prompt = d4.prompt_for(p, 0, d4.options_for(p))
    except Exception as e:          # the prompt needs a turn's state; say so rather than guess
        print(f"  a day-4 min-00 prompt could not be built outside a turn: {type(e).__name__}: {e}")
        continue
    lines = prompt.splitlines()
    for i, l in enumerate(lines, 1):
        if l.startswith("About water:") or "none left" in l or "nothing left" in l or l.startswith(
                ("What yesterday left", "What you remember", "Your options")):
            print(f"  prompt line {i}/{len(lines)}: {l}")
shutil.rmtree(tmp, ignore_errors=True)
