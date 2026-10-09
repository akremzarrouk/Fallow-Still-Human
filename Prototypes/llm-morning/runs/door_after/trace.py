"""reports/door_after_facts.md: what the house does and keeps after a door visit ends. Read-only on the repository:
each trace plays from a copy of a probe_door2 scene cache in a temp folder, which is deleted after.

From probe_door2 scene k's state: v16 seed 2 to day 3, the probe's visitor at 09:42, the asks of the knock's minute
answered from cache/probe_door2/scene<k>.json (the live answers), every later ask by the fake model (gemini.FakeClient,
no API call; GEMINI_API_KEY is removed from the environment).

    python runs/door_after/trace.py noon 1     scene 1 to 12:00: every ask, its trigger, the door lines in its prompt
    python runs/door_after/trace.py noon 2     the same for scene 2 (refused)
    python runs/door_after/trace.py full 1     scene 1 to bedtime, night 3, the night minds, day 4's blocks
Writes runs/door_after/<mode>_scene<k>.json; prints a readable form.
"""
import json
import os
import random
import re
import shutil
import sys
import tempfile

os.environ.pop("GEMINI_API_KEY", None)
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "runs", "probe_door2"))
import data                                             # noqa: E402
import night as nightmod                                # noqa: E402
import probe                                            # noqa: E402  (runs/probe_door2/probe.py, imported, not run)
import quiet                                            # noqa: E402
import world                                            # noqa: E402
from gemini import FakeClient                           # noqa: E402
from mind import NightMind, records, bound_records       # noqa: E402

KNOCK, NOON = 162, 300
DOOR = re.compile(r"front door|knock|gap in the boards|on the step|voice at|person at|stored water out|handed|"
                  r"hands some|three litres|go away|went away|goes away|footsteps", re.I)
WATER = re.compile(r"^About water:")
clock = quiet.clock


class Stop(Exception):
    pass


def state(m):
    """Each one's grudges (strength and the facts that raised them), suspicion, guilt and feeling."""
    out = {}
    for p in m.people.values():
        out[p.id] = {"grudges": {t: {"strength": g.strength, "events": [list(e) for e in g.events]}
                                 for t, g in p.grudges.items()},
                     "suspicion": p.suspicion.state(), "guilt": p.guilt, "feeling": p.feeling}
    st = m.quiet.world.street
    n = st["street"]["family"]
    hh = st["households"][HOUSEHOLD[0]]
    out["street"] = {"household": hh["id"], "family_home": n, "kind": hh["kind"].get(n), "surplus": hh["surplus"].get(n),
                     "refused": hh["refused"].get(n), "water": hh["water"],
                     "deeds": [d for d in st["deeds"] if d.get("visit") is not None]}
    return out


HOUSEHOLD = []


def door_lines(prompt):
    lines = prompt.split("Your options:")[0].splitlines()      # the options are listed apart (door_options)
    keep = []
    for ln in lines:
        if ln.startswith("The house:"):
            continue
        if DOOR.search(ln) or WATER.search(ln):
            keep.append(ln)
    opts = re.findall(r"^- (door_\w+):", prompt.split("Your options:")[-1], flags=re.M)
    return keep, opts


def main():
    mode, k = sys.argv[1], int(sys.argv[2])
    assert mode in ("noon", "full")
    spec = next(v for v in probe.VISITORS if v["scene"] == k)
    HOUSEHOLD.append(spec["household"])
    tmp = tempfile.mkdtemp(prefix="door_after_")
    try:
        path = os.path.join(tmp, f"scene{k}.json")
        shutil.copyfile(os.path.join("cache", "probe_door2", f"scene{k}.json"), path)
        client = FakeClient(invalid_every=0, max_calls=10 ** 6)
        m, oracle = probe.day3(path, client)
        assert oracle.live == 0
        v = probe.visitor(m, spec, KNOCK)
        q = m.quiet
        out = {"scene": k, "spec": spec, "states": {}, "asks": [], "prompts": [], "night_prompts": []}
        cur = {}
        real_ask = oracle.ask

        def ask(system, prompt, schema=None):
            c0, l0 = oracle.from_cache, oracle.live
            text = real_ask(system, prompt, schema)
            src = "cache" if oracle.from_cache > c0 else "fake" if oracle.live > l0 else "?"
            if schema is None and cur.get("in_ask"):
                cur.update(prompt=prompt, answer=text, source=src)
            elif cur.get("night"):
                lines, _ = door_lines(prompt)
                out["night_prompts"].append({"who": re.match(r"You are (\w+)", prompt).group(1), "source": src,
                                             "schema": schema is not None, "door_lines": lines})
            return text
        oracle.ask = ask
        traced = {}
        real_model = world.Morning.ask_model

        def ask_model(self, p, t, opts, d, extra=None):
            minute = t * data.MINUTES_PER_TURN
            cur.clear()
            cur.update(in_ask=True)
            rec = {"minute": minute, "clock": clock(minute), "who": p.id, "room": p.room, "quiet": d.get("quiet"),
                   "triggers": list(d.get("triggers") or []), "inner": d.get("inner"), "lull": d.get("lull"),
                   "trip_moment": d.get("trip_moment"), "at_door": p.door is not None}
            result = real_model(self, p, t, opts, d, extra)
            rec.update(asked="prompt" in cur, source=cur.get("source"), refused_why=None if "prompt" in cur else
                       result[1])
            if "prompt" in cur and minute >= KNOCK:
                lines, door_opts = door_lines(cur["prompt"])
                rec.update(door_lines=lines, door_options=door_opts)
                out["prompts"].append({"minute": minute, "who": p.id, "prompt": cur["prompt"], "answer": cur["answer"]})
            cur.clear()
            traced[id(d)] = rec
            return result
        world.Morning.ask_model = ask_model

        real_knock, real_end = quiet.Quiet.hear_knock, quiet.Quiet.door_end

        def hear_knock(self, minute, played):
            if minute >= KNOCK and "before_knock" not in out["states"]:
                out["states"]["before_knock"] = {"minute": minute, **state(m)}
            if mode == "noon" and minute >= NOON:
                raise Stop(minute)
            return real_knock(self, minute, played)

        def door_end(self, minute):
            real_end(self, minute)
            out["states"]["visit_end"] = {"minute": minute, **state(m)}
        quiet.Quiet.hear_knock, quiet.Quiet.door_end = hear_knock, door_end
        stopped = None
        try:
            quiet.play(m)
        except Stop as e:
            stopped = e.args[0]
        finally:
            quiet.Quiet.hear_knock, quiet.Quiet.door_end = real_knock, real_end
            world.Morning.ask_model = real_model
        out["stopped_at"] = stopped
        out["states"]["end"] = {"minute": stopped if stopped is not None else quiet.DAY_END, **state(m)}
        # Every decision from the knock, with its ask if there was one.
        for rec in m.log:
            if rec["minute"] < KNOCK:
                continue
            for d in rec["decisions"]:
                t = traced.get(id(d), {})
                out["asks"].append({"minute": rec["minute"], "clock": clock(rec["minute"]), "who": d["person"],
                                    "room": d.get("room"), "mode": d["mode"], "option": d["option"],
                                    "say": d.get("say"), "quiet": d.get("quiet"), "triggers": d.get("triggers"),
                                    "order": [d.get("place"), d.get("order_reason")],
                                    "inner": d.get("inner"), "lull": d.get("lull"),
                                    "invalid": d.get("invalid"), "asked": t.get("asked", False),
                                    "source": t.get("source"), "at_door": t.get("at_door"),
                                    "door_lines": t.get("door_lines"), "door_options": t.get("door_options")})
        sc = q.door_scenes[0] if q.door_scenes else q.door
        out["scene_record"] = {kk: sc.get(kk) for kk in ("start", "end", "outcome", "said", "acts", "give", "summary",
                                                          "heard_said", "saw", "door_asks")} if sc else None
        out["quiet_log"] = [e for e in q.log if e["minute"] >= KNOCK]
        out["stretches"] = [s for s in q.stretches if s["end"] is None or s["end"] > KNOCK - 1]
        out["spans"] = [{kk: s.get(kk) for kk in ("who", "routine", "room", "start", "end", "ended")}
                        for s in q.spans if (s["end"] or 10 ** 6) > KNOCK]
        out["withdrawals"] = [w for w in q.withdrawals if w["minute"] >= KNOCK]
        out["door_events"] = q.door_events
        out["memory"] = {p.id: [[mm, x] for mm, x in p.memory if mm >= KNOCK] for p in m.people.values()}
        out["sure"] = {p.id: list(p.sure) for p in m.people.values()}
        out["asks_count"] = {"day": q.asks, "from_cache": oracle.from_cache, "fake": oracle.live}
        # Turn order (world.py:468-472): the seeded draw of the kitchen at t = 54..58 (09:42 to 09:54).
        out["order_draws"] = []
        for t in range(54, 59):
            s = m.order_string(t, "kitchen")
            rng = random.Random(s)
            draw = {x: rng.random() for x in data.ORDER}
            three = sorted(("elena", "leo", "mara"), key=lambda x: draw[x])
            out["order_draws"].append({"t": t, "clock": clock(t * 3), "string": s,
                                       "draw": {x: round(draw[x], 4) for x in data.ORDER}, "by_draw": three})
        if mode == "full":
            full_after(m, oracle, out, cur)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join("runs", "door_after", f"{mode}_scene{k}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    report(out, mode)


def full_after(m, oracle, out, cur):
    """Day 3's chronicle, night 3, the night minds' prompts (their input) and answers, and day 4's blocks."""
    chron = CHRON[0]
    chron.add_day(m)
    kinds = ("knock", "door_line", "door_end", "door_look", "door_call", "door_open", "door_give", "door_refuse",
             "save_water")
    out["day3_events"] = [{k: e[k] for k in ("id", "minute", "kind", "actor", "words", "witnesses", "views", "text")}
                          for e in chron.events if e["scene"] == "D3" and e["kind"] in kinds]
    cur["night"] = True
    n3 = nightmod.Night(m, oracle, number=3, house=chron.house_state()).run()
    chron.add_night(n3)
    nm = NightMind(n3, chron, oracle)
    out["mind_input"] = {}
    for pid in data.ORDER:
        if pid in n3.away:
            continue
        prompt, shown = nm.prompt_for(n3.people[pid])
        recs = bound_records(records(chron, pid, 3))
        out["mind_input"][pid] = {"records": recs, "prompt": prompt}
    nm.run()
    out["minds"] = {pid: {"answer": r.get("answer"), "kept": r.get("kept"), "mode": r.get("mode")}
                    for pid, r in chron.minds[3].items()}
    # Block C reads days up to (day index - 2): D3 first reaches it on house day 8 (day index 5). Computed here on the
    # chronicle through night 3, as memory.block_c would see D3 then if nothing later outweighed it (memory.py:70-76).
    import memory
    out["block_c_day8"] = {pid: memory.render_c(memory.block_c(chron, pid, 8)) for pid in data.ORDER}
    d4 = nightmod.next_day(m, n3, oracle, chronicle=chron)
    out["day4_blocks"] = d4.blocks
    out["night_lines"] = {pid: list(n3.lines[pid]) for pid in data.ORDER}
    cur.pop("night", None)


CHRON = []


def report(out, mode):
    print(f"=== {mode}, scene {out['scene']} ({out['spec']['note']}); stopped at "
          f"{out['stopped_at'] if out['stopped_at'] is None else clock(out['stopped_at'])}; asks {out['asks_count']}")
    sc = out["scene_record"]
    print(f"visit: {clock(sc['start'])} to {clock(sc['end'])}; outcome {sc['outcome']}; acts {sc['acts']}")
    print(f"said: {[(clock(a), b) for a, b in sc['said']]}")
    print("summary:", json.dumps(sc["summary"], ensure_ascii=False))
    print("\n--- every decision from the knock")
    for a in out["asks"]:
        if mode == "full" and a["minute"] > NOON and not a["asked"]:
            continue
        words = f' "{a["say"]}"' if a["say"] else ""
        print(f"{a['clock']} {a['who']} ({a['room']}) mode {a['mode']}, asked {a['asked']} [{a['source']}], "
              f"quiet {a['quiet']}, order {a['order']}: {a['option']}{words}")
        print(f"    triggers: {a['triggers']}" + (f"; inner: {a['inner']}" if a["inner"] else "")
              + (f"; lull: {a['lull']}" if a["lull"] is not None else "") + (f"; invalid: {a['invalid']}" if a["invalid"] else ""))
        if a["asked"]:
            print(f"    door options offered: {a['door_options']}")
            for ln in a["door_lines"] or []:
                print(f"    | {ln}")
    print("\n--- quiet log from the knock (Q1, Q2, Q5, Q6, Q7 checked)")
    for e in out["quiet_log"]:
        print(f"  {clock(e['minute'])} {e['kind']} fired {e['fired']} asked {e.get('asked')} room {e.get('room')} "
              f"why {e.get('why')}" + (f" pair {e.get('pair')} grudges {e.get('grudges')}" if e["kind"] == "Q2" else "")
              + (f" who {e.get('who')} need {e.get('need')} stage {e.get('stage')}" if e["kind"] == "Q1" else ""))
    print("\n--- stretches")
    for s in out["stretches"]:
        print(f"  {clock(s['start'])} to {s['end'] if s['end'] is None else clock(s['end'])} room {s['room']} "
              f"trigger {s['trigger']} asks {s.get('asks')}")
    print("\n--- routine spans from the knock")
    for s in out["spans"]:
        print(f"  {s['who']} {s['routine']} in {s['room']} {clock(s['start'])} to "
              f"{s['end'] if s['end'] is None else clock(s['end'])} ended {s['ended']}")
    print("\n--- each one's memory from the knock, at the end of the trace")
    for pid, lines in out["memory"].items():
        print(f"  {pid}:")
        for mm, x in lines:
            print(f"    {clock(mm)}: {x}")
    print("\n--- each one's sure lines, at the end of the trace")
    for pid, lines in out["sure"].items():
        print(f"  {pid}: {lines}")
    print("\n--- state (grudges, suspicion, guilt, feeling)")
    for when, st in out["states"].items():
        print(f"  {when} ({clock(st['minute'])}):")
        for pid in data.ORDER:
            s = st[pid]
            g = {t: x["strength"] for t, x in s["grudges"].items() if x["strength"]}
            print(f"    {pid}: grudges {g}; suspicion {s['suspicion']}; guilt {s['guilt']}; feeling {s['feeling']}")
        print(f"    street: {st['street']}")
    end, start = out["states"]["end"], out["states"]["before_knock"]
    print("  grudge events added after the knock:")
    for pid in data.ORDER:
        for t, x in end[pid]["grudges"].items():
            before = len(start[pid]["grudges"].get(t, {}).get("events", []))
            for ev in x["events"][before:]:
                print(f"    {pid} against {t}: {ev}")
    print("\n--- the kitchen's seeded order draws (world.py:468-472), t = 54..58")
    for o in out["order_draws"]:
        print(f"  t {o['t']} ({o['clock']}) '{o['string']}': draw {o['draw']}; the three by draw {o['by_draw']}")
    if mode == "full":
        print("\n--- day 3's chronicle events of the door (and save_water)")
        for e in out["day3_events"]:
            print(f"  [{e['id']}] {clock(e['minute'])} {e['kind']} actor {e['actor']} witnesses {e['witnesses']}")
            for pid, t in e["views"].items():
                print(f"      {pid}: {t}")
        print("\n--- night 3's prompts: door lines")
        for p in out["night_prompts"]:
            print(f"  {p['who']} (mind {p['schema']}, {p['source']}): {p['door_lines']}")
        print("\n--- the night minds' input: records about the door, by person")
        for pid, mi in out["mind_input"].items():
            print(f"  {pid}:")
            door_ids = {e["id"] for e in out["day3_events"]}
            for rid, text in mi["records"]:
                if rid in door_ids or DOOR.search(text):
                    print(f"    [{rid}] {text}")
        print("\n--- night minds' answers (fake model)")
        for pid, r in out["minds"].items():
            print(f"  {pid}: {r['answer']}")
        print("\n--- day 4's blocks A, B, C")
        for pid, b in out["day4_blocks"].items():
            print(f"  {pid}:")
            for part in ("A", "B", "C"):
                for ln in b[part]:
                    print(f"    {part} | {ln}")
        print("\n--- block C on house day 8 (day index 5), from the chronicle through night 3")
        for pid, lines in out["block_c_day8"].items():
            print(f"  {pid}:")
            for ln in lines:
                print(f"    C | {ln}")


if __name__ == "__main__":
    real_day3 = probe.day3

    def day3_keep(cache_path, client):
        """probe.day3, with its chronicle kept (it is a local there): the same calls, in the same order."""
        from chronicle import Chronicle
        from gemini import Cache, Oracle
        from mind import NightMind as NM
        from night import Night
        from world import Morning
        oracle = Oracle(Cache(cache_path), probe.MODEL, probe.SEED, client=client)
        chron = Chronicle(probe.SEED, "daniel")

        def play(m):
            for t in range(m.turns):
                m.turn(t)
            m.finish()
            chron.add_day(m)
            return m
        d1 = play(Morning(oracle, probe.SEED))
        n1 = Night(d1, oracle, number=1).run()
        chron.add_night(n1)
        NM(n1, chron, oracle).run()
        d2 = play(Morning.next_day(d1, n1, oracle, chronicle=chron))
        n2 = Night(d2, oracle, number=2, house=chron.house_state()).run()
        chron.add_night(n2)
        NM(n2, chron, oracle).run()
        assert oracle.live == 0, "v16 through night 2 must come from the cache"
        CHRON.append(chron)
        return Morning.next_day(d2, n2, oracle, chronicle=chron), oracle
    probe.day3 = day3_keep
    main()
