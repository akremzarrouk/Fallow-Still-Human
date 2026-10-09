"""The door probe (reports/probe_door_plan.md): what the real model does with a stranger at the door.

v16 seed 2 from cache, to day 3. One visit is put at the front door: a probe visitor, not one the street sent (the
street's own visits are taken away and its asks stopped). It knocks at 07:30 if someone awake is in the kitchen then;
otherwise at the first minute after 07:30 at which someone awake is in the kitchen (the user's choice, before any live
call: in v22's day 3 the family rested from 07:21 to 09:45, and a knock into a sleeping house tests the schedule, not
the model). That minute is found once, in phase 0, and is the same in all eight scenes. The day is played until the
visit ends, then the scene stops. Eight scenes, each a different visitor (VISITORS): 6 asking for water, 2 for food.

How the cache is used:
- Phase 0: cache/probe_door/<model>-daniel_ate_it-seed2.json starts as a copy of cache/v16's. Day 3 is played with no
  visit until the knock's minute is found, and stops there, before anything at that minute is asked. Every ask before
  it is the same in all eight scenes (nothing of the visit is perceived before then), so it is asked live once and
  cached there.
- Scene k: cache/probe_door/scene<k>.json starts as a copy of that file, so the day to the knock comes from the cache
  and every ask from the knock on is the scene's own. The knock's first prompt is word for word the same in all eight
  scenes (nothing of the visitor is perceived yet); with one shared cache, scenes 2 to 8 would replay scene 1's answer.
- A phase already done (in runs/probe_door/ledger.json) is not run again.

No live ask past CAP in all (phase 0 and the eight scenes together). The key is read from GEMINI_API_KEY only.

    python runs/probe_door/probe.py --fake     a temp folder and the fake model; writes nothing in the repository
    python runs/probe_door/probe.py --live     cache/probe_door/, runs/probe_door/; asks Gemini
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import quiet                                            # noqa: E402
import street as streetmod                              # noqa: E402
from chronicle import Chronicle                         # noqa: E402
from gemini import Cache, FakeClient, GeminiClient, Oracle, load_config   # noqa: E402
from mind import NightMind                              # noqa: E402
from night import Night                                 # noqa: E402
from world import Morning                               # noqa: E402

SEED, MODEL = 2, "gemini-3.5-flash-lite"
NAME = f"{MODEL}-daniel_ate_it-seed{SEED}.json"
FROM, LAST = 30, 630                                    # 07:30 to 17:30, the knock's window (w2_design §4.2)
CAP = 150
# Each visitor: a household of seed 2's street, what it asks for, and the need the probe gives it at the knock.
VISITORS = [
    {"scene": 1, "household": "h13", "purpose": "ask_water", "water": "under", "note": "no child, helper, urgency under 0.8"},
    {"scene": 2, "household": "h29", "purpose": "ask_water", "water": "over", "note": "no child, helper, urgency over 0.8"},
    {"scene": 3, "household": "h16", "purpose": "ask_water", "water": "under", "note": "a child, helper, urgency under 0.8"},
    {"scene": 4, "household": "h23", "purpose": "ask_water", "water": "over", "note": "children, helper, urgency over 0.8"},
    {"scene": 5, "household": "h5", "purpose": "ask_water", "water": "over", "note": "no child, guarded, urgency over 0.8"},
    {"scene": 6, "household": "h15", "purpose": "ask_water", "water": "under", "note": "a child, guarded, urgency under 0.8"},
    {"scene": 7, "household": "h6", "purpose": "ask_food", "water": "plenty", "note": "no child, helper, food gone 4 days"},
    {"scene": 8, "household": "h18", "purpose": "ask_food", "water": "plenty", "note": "a child, guarded, food gone 4 days"},
]


class Stop(Exception):
    pass


class Capped:
    """The client, with no live answer past CAP in all."""

    def __init__(self, inner, ledger):
        self.inner, self.ledger = inner, ledger

    @property
    def requests(self):
        return self.inner.requests

    @property
    def last_prompt_tokens(self):
        return getattr(self.inner, "last_prompt_tokens", None)

    def new_scene(self):
        if hasattr(self.inner, "new_scene"):
            self.inner.new_scene()

    def generate(self, system, prompt, schema=None):
        if self.ledger["live"] >= CAP:
            raise Stop(f"the cap of {CAP} live asks is reached")
        text = self.inner.generate(system, prompt) if schema is None else self.inner.generate(system, prompt, schema)
        self.ledger["live"] += 1
        return text


def now_minute(prompt):
    m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - 7 * 60


def day3(cache_path, client):
    """v16 seed 2 through night 2 and mind 2 from the cache, then day 3 set up (as test_morning's QuietDayTest.v16)."""
    oracle = Oracle(Cache(cache_path), MODEL, SEED, client=client)
    chron = Chronicle(SEED, "daniel")

    def play(m):
        for t in range(m.turns):
            m.turn(t)
        m.finish()
        chron.add_day(m)
        return m
    d1 = play(Morning(oracle, SEED))
    n1 = Night(d1, oracle, number=1).run()
    chron.add_night(n1)
    NightMind(n1, chron, oracle).run()
    d2 = play(Morning.next_day(d1, n1, oracle, chronicle=chron))
    n2 = Night(d2, oracle, number=2, house=chron.house_state()).run()
    chron.add_night(n2)
    NightMind(n2, chron, oracle).run()
    assert oracle.live == 0, "v16 through night 2 must come from the cache"
    return Morning.next_day(d2, n2, oracle, chronicle=chron), oracle


def clear_street(m):
    st = m.quiet.world.street
    st["factor"] = 0.0
    st["visits"] = [v for v in st["visits"] if v["state"] == "done"]
    for hh in st["households"].values():
        hh["waiting"] = None


def visitor(m, spec, knock):
    """The probe's visit: the street cleared, the household's stores set to the need the probe gives it."""
    clear_street(m)
    st = m.quiet.world.street
    hh = st["households"][spec["household"]]
    n = streetmod.size(hh)
    drink = st["pop"]["drink"]
    at = quiet.absolute(3, knock)
    if spec["water"] == "under":            # one day of drinking water: need 0.67
        hh["water"], hh["food"], hh["food_out_since"] = 1.0 * n * drink, 3.0, None
    elif spec["water"] == "over":           # none: need 1.0
        hh["water"], hh["food"], hh["food_out_since"] = 0.0, 3.0, None
    else:                                   # water for six days; no food for four
        hh["water"], hh["food"], hh["food_out_since"] = 6.0 * n * drink, 0.0, at - 4 * 1440
    assert streetmod.purpose(hh, st["pop"]) == spec["purpose"], (spec, streetmod.needs(hh, st["pop"]))
    return streetmod.make_visit(st, spec["household"], at, spec["purpose"])


def find_knock(m):
    """Plays the day with no visit until the first minute from 07:30 at which someone awake is in the kitchen; stops
    there, before anything at that minute is asked. Checked where hear_knock is called: at every quiet step (after the
    routines are placed) and every played turn (before anyone decides). A sit in the kitchen begun before 07:30 and
    still going counts from 07:30."""
    original = quiet.Quiet.hear_knock

    def watch(self, minute, played):
        if minute >= FROM:
            found = [minute] if any(p.room == "kitchen" and not self.resting(p.id) for p in self.people()) else []
            found += [max(FROM, s["start"]) for s in self.open.values()
                      if s["routine"] == "sit" and s["room"] == "kitchen" and s["start"] <= minute]
            if found:
                raise Stop(min(found))
        return original(self, minute, played)
    quiet.Quiet.hear_knock = watch
    try:
        quiet.play(m)
    except Stop as e:
        return e.args[0]
    finally:
        quiet.Quiet.hear_knock = original
    return None


def record(m, spec, v, oracle, prompts, knock):
    """The scene as it was: the visitor, every line said at the door, every decision from the knock with its words,
    feeling and reason, the outcome."""
    q = m.quiet
    st = q.world.street
    hh = st["households"][spec["household"]]
    sc = q.door_scenes[0] if q.door_scenes else q.door
    need_w, need_f, u = streetmod.needs(hh, st["pop"])
    decisions = []
    for rec in m.log:
        if rec["minute"] < knock:
            continue
        for d in rec["decisions"]:
            decisions.append({"minute": rec["minute"], "clock": quiet.clock(rec["minute"]), "who": d["person"],
                              "room": d.get("room"), "mode": d["mode"], "option": d["option"], "label": d.get("label"),
                              "say": d.get("say"), "feeling": d.get("feeling"), "reason": d.get("reason"),
                              "triggers": d.get("triggers"), "quiet": d.get("quiet"), "invalid": d.get("invalid")})
    keys = ("start", "end", "door", "outcome", "said", "acts", "heard", "woken", "knocks", "played", "give", "asks",
            "q7_asks", "summary", "who", "voice")
    return {"spec": spec, "knock": knock,
            "visitor": {"household": hh["id"], "home": hh["home"], "members": hh["drawn"]["members"],
                        "disposition": hh["drawn"]["disposition"], "impulsive": hh["drawn"]["traits"]["impulsive"],
                        "need_w": need_w, "need_f": need_f, "urgency": u, "purpose": v["purpose"]},
            "scene": {k: sc[k] for k in keys} if sc else None,
            "q7": [e for e in q.log if e["kind"] == "Q7"],
            "stretches": [s for s in q.stretches if s["end"] is None or s["end"] > knock],
            "decisions": decisions, "live": oracle.live, "prompts": prompts}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fake", action="store_true")
    g.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if args.fake:
        os.environ.pop("GEMINI_API_KEY", None)
    else:
        assert os.environ.get("GEMINI_API_KEY"), "the live probe reads GEMINI_API_KEY"
    config = load_config("config.json")
    tmp = tempfile.mkdtemp() if args.fake else None
    cache_dir = tmp or os.path.join("cache", "probe_door")
    out_dir = tmp or os.path.join("runs", "probe_door")
    os.makedirs(cache_dir, exist_ok=True)
    base = os.path.join(cache_dir, NAME)
    ledger_path = os.path.join(out_dir, "ledger.json")
    ledger = (json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path)
              else {"live": 0, "phases": []})

    def client():
        inner = FakeClient(invalid_every=0, max_calls=10 ** 6) if args.fake else GeminiClient(config, SEED)
        return Capped(inner, ledger)

    def save_ledger():
        with open(ledger_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ledger, f, indent=1)
            f.write("\n")
    try:
        if "morning" not in [p["phase"] for p in ledger["phases"]]:
            if not os.path.exists(base):
                shutil.copyfile(os.path.join("cache", "v16", NAME), base)
            m, oracle = day3(base, client())
            clear_street(m)
            knock = find_knock(m)
            q = m.quiet
            ledger["phases"].append({"phase": "morning", "live": oracle.live, "knock": knock,
                                     "rooms": {p.id: p.room for p in m.people.values()},
                                     "resting": [p.id for p in q.people() if q.resting(p.id)],
                                     "morning_end": q.morning_end})
            save_ledger()
            print(f"phase 0: the knock comes at {knock if knock is None else quiet.clock(knock)}; {oracle.live} live "
                  f"asks; the morning's talk ended at {q.morning_end}; rooms {ledger['phases'][-1]['rooms']}; "
                  f"resting {ledger['phases'][-1]['resting']}", flush=True)
        knock = next(p["knock"] for p in ledger["phases"] if p["phase"] == "morning")
        if knock is None or knock > LAST:
            raise Stop(f"no minute from 07:30 to 17:30 with someone awake in the kitchen ({knock})")
        done = {p["phase"] for p in ledger["phases"]}
        for spec in VISITORS:
            k = spec["scene"]
            if f"scene{k}" in done:
                print(f"scene {k}: done already, not run again")
                continue
            path = os.path.join(cache_dir, f"scene{k}.json")
            shutil.copyfile(base, path)
            m, oracle = day3(path, client())
            v = visitor(m, spec, knock)
            prompts = []
            real = oracle.ask

            def keep(system, prompt, schema=None, real=real, prompts=prompts):
                text = real(system, prompt, schema)
                if schema is None and (now_minute(prompt) or -1) >= knock:
                    prompts.append({"minute": now_minute(prompt), "prompt": prompt, "answer": text})
                return text
            oracle.ask = keep
            original = quiet.Quiet.door_end

            def door_end(self, minute, original=original):
                original(self, minute)
                raise Stop("the visit ended")
            quiet.Quiet.door_end = door_end
            try:
                quiet.play(m)
                print(f"scene {k}: the day ended with no end to the visit", flush=True)
            except Stop as e:
                print(f"scene {k}: {e}", flush=True)
            finally:
                quiet.Quiet.door_end = original
            rec = record(m, spec, v, oracle, prompts, knock)
            with open(os.path.join(out_dir, f"scene{k}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
                f.write("\n")
            sc = rec["scene"]
            ledger["phases"].append({"phase": f"scene{k}", "live": oracle.live, "outcome": sc and sc["outcome"],
                                     "played": sc and sc["played"], "asks": sc and sc["asks"],
                                     "acts": sc and [(a[1], a[2]) for a in sc["acts"]]})
            save_ledger()
            print(f"scene {k} ({spec['note']}): {oracle.live} live asks; knock {quiet.clock(knock)}, in played turns "
                  f"{sc and sc['played']}; outcome {sc and sc['outcome']}; door asks {sc and sc['asks']}; acts "
                  f"{sc and [(a[1], a[2]) for a in sc['acts']]}; live in all {ledger['live']}", flush=True)
    except Stop as e:
        print(f"STOPPED: {e}", flush=True)
        save_ledger()
        return 3
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f"live asks in all: {ledger['live']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
