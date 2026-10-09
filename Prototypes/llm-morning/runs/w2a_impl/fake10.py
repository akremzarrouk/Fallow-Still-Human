"""reports/w2a_impl.md, DONE 5: a fake 10-day run of seed 2 (morning.run, as `morning.py --seed 2 --fake --days 10`
runs it), into a temp folder; no API. Writes its stdout to runs/w2a_impl/fake10.stdout.txt and its story to
runs/w2a_impl/fake10.story.md; prints the exit code, every door scene in full (the knock, each line said at the door,
each family act there, the end), every Q7 stretch and its asks, and each day's asks.

    python runs/w2a_impl/fake10.py          (from Prototypes/llm-morning/)
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import morning                              # noqa: E402
import quiet                                # noqa: E402

tmp = tempfile.mkdtemp()
try:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        meta, code = morning.run(2, fake=True, days=10, runs_dir=tmp, cache_dir=tmp,
                                 config_path=os.path.join(os.getcwd(), "config.json"))
    out = buf.getvalue()
    with open("runs/w2a_impl/fake10.stdout.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    shutil.copyfile(os.path.join(tmp, "daniel_ate_it-seed2.md"), "runs/w2a_impl/fake10.story.md")
    t = json.load(open(os.path.join(tmp, "daniel_ate_it-seed2.transcript.json"), encoding="utf-8"))
    print(f"morning.run(2, fake=True, days=10): exit {code}; asks {meta.get('answers_live')} (fake)")
    print("\n".join(x for x in out.splitlines() if x.startswith("  street")))
    scenes, worst_q7, worst_day = 0, 0, 0
    for k in range(3, 11):
        q = t[f"day{k}"]["quiet"]
        worst_day = max(worst_day, q["asks"]["day"])
        q7 = [s for s in q["stretches"] if s["trigger"] == "Q7"]
        worst_q7 = max([worst_q7] + [s["asks"] for s in q7])
        print(f"day {k}: day asks {q['asks']['day']}; Q7 stretches {[(quiet.clock(s['start']), s['asks']) for s in q7]}")
        for e in q["log"]:
            if e["kind"] == "Q7":
                print(f"  {quiet.clock(e['minute'])} Q7 visit {e['visit']} ({e['household']}, {e['purpose']}): "
                      f"fired={e['fired']} room={e['room']} asked={e['asked']} why={e['why']}")
        for sc in q["door"]:
            scenes += 1
            print(f"  DOOR SCENE day {k}, {quiet.clock(sc['start'])} to {quiet.clock(sc['end'])}: {sc['who']} from "
                  f"{sc['household']} ({sc['purpose']}); heard {sc['heard']}; woken {sc['woken']}; outcome "
                  f"{sc['outcome']}; asks {sc['asks']}; give {sc['give']}")
            for turn in t[f"day{k}"]["turns"]:
                for a in turn["acts"]:
                    if sc["start"] <= a["minute"] <= sc["end"] and a["mode"] != "routine":
                        print(f"    {quiet.clock(a['minute'])} {a['who']} {a['room']}: {a['option']}"
                              + (f" \"{a['words']}\"" if a["words"] else "") + f" [{a['mode']}]")
            for at, text in sc["said"]:
                print(f"    {quiet.clock(at)} at the door: \"{text}\"")
            for q_, line in sc["summary"].items():
                print(f"    {q_}'s line of it: {line}")
    print(f"door scenes {scenes}; largest Q7 stretch {worst_q7} asks; largest day {worst_day} asks")
    sys.exit(0 if code == 0 and scenes >= 1 and worst_q7 <= 6 and worst_day <= 56 else 1)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
