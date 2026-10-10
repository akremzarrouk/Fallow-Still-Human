"""The probe after the door (reports/probe_after_plan.md): what the family does once a stranger has gone, and what
each one keeps that night. From runs/probe_door2/probe.py (its visitors, client seeds, cap and ledger) and
runs/door_after/trace.py (its full mode: the day to bedtime, night 3, the night minds, day 4's blocks).

Scenes 1, 3 and 4 of probe_door2 only, each with its visitor and its client seed (101, 103, 104). v16 seed 2 to day 3
from the cache, the probe's visitor at the front door at 09:42, as in probe_door2.

How the cache and the seed are used:
- Scene k's cache, cache/probe_after/scene<k>.json, starts as a copy of cache/probe_door2/scene<k>.json. So days 1
  and 2, nights 1 and 2, the morning of day 3 and the asks of 09:42 are probe_door2's answers. The cache key keeps the
  run's seed (2). The client sends seed 100+k with every request, as in probe_door2.
- No live ask before the visit ends (09:45): any ask before it not in the copied cache stops the scene. From 09:45 on,
  every ask is live: the rest of day 3, night 3, the night minds. Then day 4 is set up (next_day) and its blocks
  recorded. Day 4 is not played.
- A scene already started (in runs/probe_after/ledger.json) is not run again, even if it stopped part way.

No live ask past CAP (200) in all three scenes together. The key is read from GEMINI_API_KEY only.

    python runs/probe_after/probe.py --fake     a temp folder and the fake model; writes nothing in the repository
    python runs/probe_after/probe.py --live     cache/probe_after/, runs/probe_after/; asks Gemini
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import data                                             # noqa: E402
import memory                                           # noqa: E402
import night as nightmod                                # noqa: E402
import quiet                                            # noqa: E402
import street as streetmod                              # noqa: E402
import world                                            # noqa: E402
from chronicle import Chronicle                         # noqa: E402
from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config   # noqa: E402
from mind import NightMind, bound_records, records      # noqa: E402
from night import Night                                 # noqa: E402
from world import Morning                               # noqa: E402

SEED, MODEL = 2, "gemini-3.5-flash-lite"
KNOCK = 162                                             # 09:42, probe_door2's knock in every scene
CAP = 200
SCENE_SEED = 100                                        # scene k's client seed is SCENE_SEED + k
SOURCE = os.path.join("cache", "probe_door2")           # scene<k>.json: probe_door2's scene caches
# probe_door2's visitors for scenes 1, 3 and 4 (runs/probe_door2/probe.py, VISITORS).
VISITORS = [
    {"scene": 1, "household": "h13", "purpose": "ask_water", "water": "under", "note": "no child, helper, urgency under 0.8"},
    {"scene": 3, "household": "h16", "purpose": "ask_water", "water": "under", "note": "a child, helper, urgency under 0.8"},
    {"scene": 4, "household": "h23", "purpose": "ask_water", "water": "over", "note": "children, helper, urgency over 0.8"},
]
DOOR_KINDS = ("knock", "door_line", "door_end", "door_look", "door_call", "door_open", "door_give", "door_refuse",
              "save_water")
clock = quiet.clock


class Stop(Exception):
    pass


class Capped:
    """The client, with no live answer past CAP in all, and none before the visit has ended."""

    def __init__(self, inner, ledger):
        self.inner, self.ledger = inner, ledger
        self.allow = False                              # set when the visit ends (09:45)

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
        if not self.allow:
            raise Stop("an ask before the visit's end was not in the copied cache")
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
    """v16 seed 2 through night 2 and mind 2 from the cache, then day 3 set up (runs/probe_door2/probe.py, day3),
    keeping the chronicle (runs/door_after/trace.py, day3_keep)."""
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
    return Morning.next_day(d2, n2, oracle, chronicle=chron), oracle, chron


def clear_street(m):
    st = m.quiet.world.street
    st["factor"] = 0.0
    st["visits"] = [v for v in st["visits"] if v["state"] == "done"]
    for hh in st["households"].values():
        hh["waiting"] = None


def visitor(m, spec, knock):
    """The probe's visit (runs/probe_door2/probe.py, visitor): the street cleared, the household's stores set to the
    need the probe gives it."""
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


def state(m, household):
    """Each one's grudges (strength and facts), suspicion, guilt and feeling; the visiting household's view of no. 9."""
    out = {}
    for p in m.people.values():
        out[p.id] = {"grudges": {t: {"strength": g.strength, "events": [list(e) for e in g.events]}
                                 for t, g in p.grudges.items()},
                     "suspicion": p.suspicion.state(), "guilt": p.guilt, "feeling": p.feeling}
    st = m.quiet.world.street
    n = st["street"]["family"]
    hh = st["households"][household]
    out["street"] = {"household": hh["id"], "kind": hh["kind"].get(n), "surplus": hh["surplus"].get(n),
                     "refused": hh["refused"].get(n), "water": hh["water"]}
    return out


def answer_fields(text):
    try:
        a = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip()))
    except ValueError:
        return {"raw": text}
    return a if isinstance(a, dict) else {"raw": text}


def run_scene(spec, cache_path, client, out):
    """Plays scene k from the knock to day 4's blocks, filling `out` as it goes (so a stop leaves what was done)."""
    m, oracle, chron = day3(cache_path, client)
    v = visitor(m, spec, KNOCK)
    q = m.quiet
    out["visitor"] = {"household": spec["household"], "purpose": v["purpose"]}
    out["oracle"] = oracle
    cur = {"phase": "day"}
    out["asks"] = []                                    # every ask from the knock: who, when, source, prompt, answer
    real_ask = oracle.ask

    def ask(system, prompt, schema=None, real_ask=real_ask):
        c0, l0 = oracle.from_cache, oracle.live
        text = real_ask(system, prompt, schema)
        src = "cache" if oracle.from_cache > c0 else "live" if oracle.live > l0 else "?"
        minute = now_minute(prompt)
        if cur["phase"] != "day" or (minute is not None and minute >= KNOCK):
            who = cur.get("who")
            if who is None:
                w = re.search(r"You are (\w+)", prompt)
                who = w.group(1).lower() if w else None
            out["asks"].append({"phase": cur["phase"], "minute": minute, "who": who, "mind": schema is not None,
                                "source": src, "prompt": prompt, "answer": text})
        return text
    oracle.ask = ask
    real_model = world.Morning.ask_model

    def ask_model(self, p, t, opts, d, extra=None):
        cur["who"] = p.id
        try:
            return real_model(self, p, t, opts, d, extra)
        finally:
            cur.pop("who", None)
    real_knock, real_end = quiet.Quiet.hear_knock, quiet.Quiet.door_end
    out["states"] = {}

    def hear_knock(self, minute, played):
        if minute >= KNOCK and "before_knock" not in out["states"]:
            out["states"]["before_knock"] = {"minute": minute, **state(m, spec["household"])}
        return real_knock(self, minute, played)

    def door_end(self, minute):
        real_end(self, minute)
        out["states"]["visit_end"] = {"minute": minute, **state(m, spec["household"])}
        client.allow = True
    world.Morning.ask_model = ask_model
    quiet.Quiet.hear_knock, quiet.Quiet.door_end = hear_knock, door_end
    out["reached"] = "day 3"
    try:
        quiet.play(m)
    finally:
        world.Morning.ask_model = real_model
        quiet.Quiet.hear_knock, quiet.Quiet.door_end = real_knock, real_end
        day_record(m, q, out, spec)
    out["reached"] = "night 3"
    chron.add_day(m)
    out["day3_events"] = [{k: e[k] for k in ("id", "minute", "kind", "actor", "words", "witnesses", "views", "text")}
                          for e in chron.events if e["scene"] == "D3" and e["kind"] in DOOR_KINDS]
    cur["phase"] = "night"
    n3 = Night(m, oracle, number=3, house=chron.house_state()).run()
    chron.add_night(n3)
    out["night_lines"] = {pid: list(n3.lines[pid]) for pid in data.ORDER}
    out["night_transcript"] = n3.transcript() if hasattr(n3, "transcript") else None
    out["reached"] = "night minds"
    cur["phase"] = "mind"
    nm = NightMind(n3, chron, oracle)
    out["mind_input"] = {}
    for pid in data.ORDER:
        if pid in n3.away:
            continue
        prompt, _ = nm.prompt_for(n3.people[pid])
        out["mind_input"][pid] = {"records": bound_records(records(chron, pid, 3)), "prompt": prompt}
    nm.run()
    out["minds"] = {pid: {k: r.get(k) for k in ("mode", "invalid", "memories", "kept", "feeling", "intent", "answer",
                                                 "warnings")}
                    for pid, r in chron.minds[3].items()}
    out["reached"] = "day 4's blocks"
    cur["phase"] = "day4"
    d4 = nightmod.next_day(m, n3, oracle, chronicle=chron)
    out["day4_blocks"] = d4.blocks
    out["block_c_day8"] = {pid: memory.render_c(memory.block_c(chron, pid, 8)) for pid in data.ORDER}
    out["reached"] = "done"


def day_record(m, q, out, spec):
    """Day 3 from the knock: every decision (option, words, feeling, reason), the quiet log, the stretches, the door
    scene, each one's memory and sure lines, the end state."""
    decisions = []
    for rec in m.log:
        if rec["minute"] < KNOCK:
            continue
        for d in rec["decisions"]:
            decisions.append({"minute": rec["minute"], "clock": clock(rec["minute"]), "who": d["person"],
                              "room": d.get("room"), "mode": d["mode"], "option": d["option"], "label": d.get("label"),
                              "say": d.get("say"), "feeling": d.get("feeling"), "reason": d.get("reason"),
                              "triggers": d.get("triggers"), "quiet": d.get("quiet"), "invalid": d.get("invalid"),
                              "order": [d.get("place"), d.get("order_reason")]})
    out["decisions"] = decisions
    sc = q.door_scenes[0] if q.door_scenes else q.door
    out["scene"] = {k: sc.get(k) for k in ("start", "end", "outcome", "said", "acts", "give", "summary", "heard_said",
                                           "saw", "door_asks", "by_knock", "perceived")} if sc else None
    out["quiet_log"] = [e for e in q.log if e["minute"] >= KNOCK]
    out["stretches"] = [s for s in q.stretches if s["end"] is None or s["end"] > KNOCK - 1]
    out["memory"] = {p.id: [[mm, x] for mm, x in p.memory if mm >= KNOCK] for p in m.people.values()}
    out["sure"] = {p.id: list(p.sure) for p in m.people.values()}
    out["day_asks"] = {"all": q.asks, "reserved": getattr(q, "reserved_asks", None)}
    out["states"]["end_of_day"] = {"minute": quiet.DAY_END, **state(m, spec["household"])}


def scene_json(out):
    keep = dict(out)
    o = keep.pop("oracle", None)
    if o is not None:
        keep["counts"] = {"live": o.live, "from_cache": o.from_cache, "api_requests": o.api_requests}
    return keep


def summary(k, spec, rec):
    """The scene in a few lines, for stdout."""
    lines = [f"scene {k} ({spec['note']}, client seed {SCENE_SEED + k}): reached {rec.get('reached')}; "
             f"counts {rec.get('counts')}"]
    sc = rec.get("scene")
    if sc:
        lines.append(f"  visit {clock(sc['start'])} to {sc['end'] if sc['end'] is None else clock(sc['end'])}; "
                     f"outcome {sc['outcome']}; acts {[(clock(a[0]), a[1], a[2]) for a in sc['acts']]}")
    for s in rec.get("stretches", []):
        lines.append(f"  stretch {clock(s['start'])} to {s['end'] if s['end'] is None else clock(s['end'])} "
                     f"{s['trigger']} in {s['room']}: {s.get('asks')} asks")
    fired = [(clock(e["minute"]), e["kind"], e.get("asked")) for e in rec.get("quiet_log", [])
             if e["kind"] in ("Q1", "Q2") and e["fired"] and 180 <= e["minute"] <= 720]
    lines.append(f"  Q1 or Q2 fired 10:00 to 19:00: {fired}")
    lines.append(f"  day 3 asks {rec.get('day_asks')}")
    for pid, r in (rec.get("minds") or {}).items():
        lines.append(f"  night mind {pid}: mode {r['mode']}; kept {[(x['ids'], x['meaning']) for x in r['kept']]}")
    for pid, b in (rec.get("day4_blocks") or {}).items():
        door = [ln for part in ("A", "B") for ln in b[part]
                if re.search(r"front door|knock|handed|stored water|go away|woman|visitor", ln, re.I)]
        lines.append(f"  day 4 {pid} A/B door lines: {door}")
    return "\n".join(lines)


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
    cache_dir = tmp or os.path.join("cache", "probe_after")
    out_dir = tmp or os.path.join("runs", "probe_after")
    os.makedirs(cache_dir, exist_ok=True)
    ledger_path = os.path.join(out_dir, "ledger.json")
    ledger = (json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path)
              else {"live": 0, "phases": []})

    def save_ledger():
        with open(ledger_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ledger, f, indent=1)
            f.write("\n")
    code = 0
    try:
        for spec in VISITORS:
            k = spec["scene"]
            if any(p["phase"] == f"scene{k}" for p in ledger["phases"]):
                print(f"scene {k}: started already, not run again", flush=True)
                continue
            if ledger["live"] >= CAP:
                print(f"scene {k}: not run, the cap of {CAP} live asks is reached", flush=True)
                code = 3
                continue
            path = os.path.join(cache_dir, f"scene{k}.json")
            shutil.copyfile(os.path.join(SOURCE, f"scene{k}.json"), path)
            seed = SCENE_SEED + k
            inner = FakeClient(invalid_every=0, max_calls=10 ** 6) if args.fake else GeminiClient(config, seed)
            client = Capped(inner, ledger)
            phase = {"phase": f"scene{k}", "seed": seed, "live_before": ledger["live"]}
            ledger["phases"].append(phase)
            save_ledger()
            out = {"spec": spec, "client_seed": seed, "knock": KNOCK}
            stopped = None
            try:
                run_scene(spec, path, client, out)
            except (Stop, StopMorning) as e:
                stopped = f"{type(e).__name__}: {e}"
                code = 3
            rec = scene_json(out)
            rec["stopped"] = stopped
            with open(os.path.join(out_dir, f"scene{k}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
                f.write("\n")
            phase.update(reached=rec.get("reached"), stopped=stopped, counts=rec.get("counts"),
                         live_after=ledger["live"])
            save_ledger()
            print(summary(k, spec, rec), flush=True)
            if stopped:
                print(f"scene {k} STOPPED: {stopped}", flush=True)
    finally:
        save_ledger()
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f"live asks in all: {ledger['live']}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
