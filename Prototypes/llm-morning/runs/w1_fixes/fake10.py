"""reports/w1_impl.md, DONE 3 and 4: a fake run of seed 2 to day 10 (morning.run, as `morning.py --seed 2 --fake
--days 10` runs it), into a temp folder; no API. Writes its full stdout to runs/w1_fixes/fake10.stdout.txt, then
prints what DONE 3 asks (the weather of days 1 to 10, the water each morning, the stages each evening, every Q6 and
each night's rain and water) and DONE 4's scan of every "Your body:" line the fake run's prompts hold.

    python runs/w1_impl/done3.py          (from Prototypes/llm-morning/)
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import morning                              # noqa: E402

FORBIDS = re.compile(r"impossible|cannot|can't|unable|barely (stand|walk|move)", re.I)
tmp = tempfile.mkdtemp()
try:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        meta, code = morning.run(2, fake=True, days=10, runs_dir=tmp, cache_dir=tmp,
                                 config_path=os.path.join(os.getcwd(), "config.json"))
    out = buf.getvalue()
    with open("runs/w1_fixes/fake10.stdout.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"morning.run(2, fake=True, days=10): exit {code}; asks {meta.get('answers_live')} (fake)")
    for line in out.splitlines():
        if re.match(r"^  (weather day \d+:|day \d+ (07:00 water|21:00 stages):|day \d+ \d\d:\d\d: Q6|night \d+: (rainy|dry))",
                    line):
            print(line)
    prompts = []
    for name in os.listdir(tmp):
        if name.endswith(".json") and name.startswith("fake-"):
            with open(os.path.join(tmp, name), encoding="utf-8") as f:
                prompts += [e["prompt"] for e in json.load(f).values()]
    body = [x for p in prompts for x in p.splitlines() if x.startswith("Your body:")]
    bad = [x for x in body if FORBIDS.search(x)]
    print(f"DONE 4: prompts {len(prompts)}; 'Your body:' lines {len(body)} ({len(set(body))} distinct); matching "
          f"{FORBIDS.pattern!r}: {len(bad)}")
    for x in sorted(set(body)):
        print(f"  {body.count(x):4d} × {x}")
    sys.exit(0 if code == 0 and not bad else 1)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
