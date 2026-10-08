"""A fake 10-day run of seed 2 on the current code (no API), into runs/w22/fake/ (runs) and runs/w22/fake/cache.
For checking w1_score.py. Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset."""
import contextlib, io, os, sys
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import morning
base = os.path.join("runs", "w22", "fake")
os.makedirs(base, exist_ok=True)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    meta, code = morning.run(2, fake=True, days=10, runs_dir=base, cache_dir=os.path.join(base, "cache"),
                             config_path=os.path.join(os.getcwd(), "config.json"))
open(os.path.join(base, "stdout.txt"), "w", encoding="utf-8", newline="\n").write(buf.getvalue())
print("exit", code, "asks", meta.get("answers_live"))
