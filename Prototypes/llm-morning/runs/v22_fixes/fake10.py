"""No API: a fake 10-day run of seed 2 on the changed code, into a temp folder; prints the exit code, the Q6 lines of the
log and the number of 'Q6 skipped' entries."""
import contextlib, io, json, os, shutil, sys, tempfile
sys.path.insert(0, os.getcwd()); assert not os.environ.get("GEMINI_API_KEY")
import morning
tmp = tempfile.mkdtemp()
try:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        meta, code = morning.run(2, fake=True, days=10, runs_dir=tmp, cache_dir=tmp, config_path=os.path.join(os.getcwd(), "config.json"))
    t = json.load(open(os.path.join(tmp, "daniel_ate_it-seed2.transcript.json"), encoding="utf-8"))
    print(f"morning.run(2, fake=True, days=10): exit {code}; asks {meta.get('answers_live')}")
    for k in range(3, 11):
        for e in t[f"day{k}"]["quiet"]["log"]:
            if e["kind"] == "Q6":
                print(f"  day {k} Q6 at minute {e['minute']}: fired={e['fired']} asked={e['asked']} why={e['why']}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
