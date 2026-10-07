"""No-API replay of runs/v17 seeds 1-3 from a copy of cache/v17 (read only), recording for day 3:
every ask (prompt, answer, minute, speaker), every grudge's level at 07:00, after each played turn and at 21:00,
and the trip state. Checks that the replayed story is byte-identical to runs/v17/<name>.md.

    python runs/v17_meetings/scripts/replay_v17.py OUT        (from Prototypes/llm-morning/)

Writes OUT/seedN.json.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import data                                           # noqa: E402
import quiet                                          # noqa: E402
from chronicle import Chronicle                       # noqa: E402
from gemini import Cache, Oracle                      # noqa: E402
from mind import NightMind                            # noqa: E402
from night import Night                               # noqa: E402
from story import render, render_day2, render_mind, render_night       # noqa: E402
from world import Morning                             # noqa: E402

MODEL = "gemini-3.5-flash-lite"
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()


def grudges(m):
    return {p: {t: g.strength for t, g in m.people[p].grudges.items()} for p in data.ORDER}


for seed in (1, 2, 3):
    name = f"daniel_ate_it-seed{seed}"
    copy = os.path.join(tmp, f"{name}.json")
    shutil.copyfile(os.path.join("cache", "v17", f"{MODEL}-{name}.json"), copy)
    oracle = Oracle(Cache(copy), MODEL, seed, client=None, replay=True)
    asks = []
    real_ask = oracle.ask

    def ask(system, prompt, schema=None, asks=asks, real_ask=real_ask):
        text = real_ask(system, prompt, schema)
        asks.append({"prompt": prompt, "response": text})
        return text
    oracle.ask = ask
    chron = Chronicle(seed, data.culprit("daniel_ate_it"))

    def play(m):
        for t in range(m.turns):
            m.turn(t)
        m.finish()
        chron.add_day(m)
        return m
    day1 = play(Morning(oracle, seed, "daniel_ate_it"))
    text = render(day1, seed, MODEL, f"python morning.py --seed {seed}")
    n1 = Night(day1, oracle, number=1, house=chron.house_state()).run()
    chron.add_night(n1)
    oracle.new_scene()
    mind1 = NightMind(n1, chron, oracle).run()
    oracle.new_scene()
    day2 = play(Morning.next_day(day1, n1, oracle, chronicle=chron))
    oracle.new_scene()
    n2 = Night(day2, oracle, number=2, house=chron.house_state()).run()
    chron.add_night(n2)
    oracle.new_scene()
    mind2 = NightMind(n2, chron, oracle).run()
    oracle.new_scene()
    before = len(asks)
    m = Morning.next_day(day2, n2, oracle, chronicle=chron)
    record = {"start": grudges(m), "turns": [], "trip_at_start": m.trip,
              "trip_heard_at_start": {p: m.people[p].trip_heard for p in data.ORDER}}

    def told(t, m=m, record=record, asks=asks):
        record["turns"].append({"minute": t * data.MINUTES_PER_TURN, "grudges": grudges(m), "asks_so_far": len(asks)})
    quiet.play(m, told)
    chron.add_day(m)
    record["end"] = grudges(m)
    record["day3_asks"] = asks[before:]
    record["trip_heard_at_end"] = {p: {k: list(v) for k, v in m.people[p].trip_heard.items()} for p in data.ORDER}
    record["trip_at_end"] = m.trip
    text += render_night(n1) + render_mind(mind1) + render_day2(day2) + render_night(n2) + render_mind(mind2) \
        + render_day2(m)
    orig = open(os.path.join("runs", "v17", f"{name}.md"), encoding="utf-8").read()
    record["story_identical_to_runs_v17"] = text == orig
    record["day3_grudge_events"] = {p: {t: [list(e[:3]) for e in g.events] for t, g in m.people[p].grudges.items()}
                                    for p in data.ORDER}
    json.dump(record, open(os.path.join(OUT, f"seed{seed}.json"), "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    print(f"{name}: day-3 asks {len(record['day3_asks'])}; live {oracle.live}; story identical to runs/v17: "
          f"{record['story_identical_to_runs_v17']}")
shutil.rmtree(tmp)
