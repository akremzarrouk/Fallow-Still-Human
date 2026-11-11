"""The week: seven full days and the nights between them, in code mode (Docs/fable-audit-2026-11.md, 7.4; section 9,
step 3).

    python week.py --seed 2            # writes runs/week/seed2.transcript.json and prints one line per act

Every day is played from 07:00 to bedtime, day 1 and day 2 included, on the quiet-day loop (quiet.py). In code mode
that loop has beats (quiet.BEATS): at set hours everyone who is up comes into the kitchen, and what the hour is for is
offered there: the meal in the morning and the evening, the day's work, the plan for the night. Nothing is staged:
what happens besides comes from the weather, the water, the street, the nights out, and from sickness and injury,
which are drawn only when a cause holds (health.py, content/chances.json).

No model is asked anywhere: the brain decides (brain.py), and the night step settles the hearts (heart.py).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import brain as brainmod    # noqa: E402
import data                 # noqa: E402
import quiet as quietday    # noqa: E402
from chronicle import Chronicle     # noqa: E402
from health import Health   # noqa: E402
from mind import NightMind  # noqa: E402
from night import Night     # noqa: E402
from world import Morning, day_index    # noqa: E402

DAYS = 7


class Week:
    """One played week: its days, its nights and their night steps, and the brain that decided."""

    def __init__(self, seed, scenario, brain, oracle, chron):
        self.seed, self.scenario, self.brain, self.oracle, self.chron = seed, scenario, brain, oracle, chron
        self.days, self.nights, self.minds = [], [], []
        self.removed = None

    def transcript(self):
        out = {}
        for k, m in enumerate(self.days, 1):
            out[f"day{k}"] = m.transcript
            if k <= len(self.nights):
                out[f"night{k}"] = self.nights[k - 1].transcript()
                out[f"mind{k}"] = self.minds[k - 1].transcript()
        out["moods"] = self.brain.moods_json()
        out["health"] = self.brain.health.record() if getattr(self.brain, "health", None) is not None else []
        out["removed"] = self.removed
        return out


def run(seed, days=DAYS, brain=None, player=None, scenario=data.DEFAULT_SCENARIO, remove=None, tilt=True,
        told=None):
    """Plays the week. remove: (day k, person): that person is gone when day k begins, as if lost in the night
    before (the LLM-off test's L11). told(m, t): called after each played turn."""
    brain = brain or brainmod.CodeBrain(seed, tilt=tilt)
    brain.full_days = True
    brain.health = Health(seed, brainmod.load("chances.json"))
    oracle = brainmod.CodeOracle(brain)
    chron = Chronicle(seed, data.culprit(scenario))
    week = Week(seed, scenario, brain, oracle, chron)
    m = Morning(oracle, seed, scenario, player=player)
    quietday.setup(m, chron)                # day 1 is a full day too
    brain.new_day(m)
    for k in range(1, days + 1):
        quietday.play(m, (lambda t, m=m: told(m, t)) if told else None)
        chron.add_day(m)
        week.days.append(m)
        if k == days:
            break
        n = Night(m, oracle, number=k, house=chron.house_state()).run()
        if remove is not None and remove[0] == k + 1 and remove[1] not in n.away:
            n.away.add(remove[1])
            n.people[remove[1]].room = None
            week.removed = {"day": k + 1, "who": remove[1]}
            brain.removed(n, remove[1])
        chron.add_night(n)
        week.nights.append(n)
        week.minds.append(NightMind(n, chron, oracle).run())    # in code mode: the night step
        m = Morning.next_day(m, n, oracle, chronicle=chron)
    return week


# ---------- reading a week: its acts, its world events, its empty days ----------
def acts(tr):
    """Every act of a week, in order: {"day", "night", "who", "option", "mode", "words", "minute", "why", "room"}.
    A night belongs to the day it follows."""
    out = []
    k = 1
    while f"day{k}" in tr:
        for turn in tr[f"day{k}"]["turns"]:
            for a in turn["acts"]:
                out.append({"day": k, "night": False, "who": a["who"], "option": a["option"], "mode": a["mode"],
                            "words": a["words"], "minute": a["minute"], "why": a.get("why") or {}, "room": a["room"]})
        for d in (tr.get(f"night{k}") or {}).get("decisions", []):
            out.append({"day": k, "night": True, "who": d["person"], "option": d["option"], "mode": d["mode"],
                        "words": d.get("say"), "minute": None, "why": d.get("why") or {}, "room": d.get("where")})
        k += 1
    return out


def world_reason(option):
    """An act that answers something from the world: the rain, a knock, the water running low, someone sick or hurt."""
    return (option == "collect_rain" or option.startswith("door_") or option in ("ration_water", "save_water")
            or option.startswith("task_tend_"))


ROUTINE_ACTS = ("silent", "sleep", "lie_awake", "meal", "meal_small", "plate_eat", "keep_searching", "search",
                "stay_in_bed", "deny", "say_other", "water_round", "cup_drink")
ROUTINE_STARTS = ("task_", "say_to_", "go_kitchen", "go_brothers", "go_back_", "go_bath", "let_")


def between_people(option):
    """An act that is something between people, if it is new: not a meal, not the day's work, not sleep, not staying
    as they are, not an answer of a few words."""
    if option in ROUTINE_ACTS or option.startswith(ROUTINE_STARTS):
        return False
    return not world_reason(option)


def empty_days(tr):
    """For each day, what made it a day on which something happened; an empty list is an empty day (7.4): nothing
    beyond meals, routine work and sleep. Something from the world counts if an act of the day answers it. Something
    between people counts if it is new: the first time that person does it at that person this week, or a repeat
    whose record names a new cause. A night out counts the first time for whoever goes, and whenever someone does
    not come back. Falling sick or getting hurt, or getting worse, counts."""
    seen, out = set(), {}
    gone = set()
    k = 1
    all_acts = acts(tr)
    while f"day{k}" in tr:
        why = []
        for a in (x for x in all_acts if x["day"] == k):
            if a["mode"] == "routine":
                continue
            key = (a["who"], a["option"])
            if world_reason(a["option"]):
                why.append(f"{a['who']} {a['option']} (the world)")
            elif between_people(a["option"]) and (key not in seen or a["why"].get("new_cause")):
                if a["option"] in ("go_next_door", "go_further") and a["who"] in gone:
                    seen.add(key)
                    continue
                why.append(f"{a['who']} {a['option']}" + (f" ({a['why']['new_cause']})" if a["why"].get("new_cause")
                                                           else ""))
            seen.add(key)
        for g in (tr.get(f"night{k}") or {}).get("groups", []):
            gone |= set(g["members"])
            if g["lost"]:
                why.append(f"{g['lost']} did not come back")
        for e in (tr.get("health") or {}).get("events", []):
            if e["day"] == k and e["change"] in ("onset", "worse"):
                why.append(e["line"])
        out[k] = why
        k += 1
    return out


def longest_empty_run(empties):
    best = run_now = 0
    for k in sorted(empties):
        run_now = run_now + 1 if not empties[k] else 0
        best = max(best, run_now)
    return best


def world_events(week):
    """Everything that came from the world this week, each with the chance it was drawn at and the conditions that
    held (the LLM-off test, L12). The rain is the sky's draw for the day, by the calendar's climate (weather.py: Kew
    normals); a knock is a neighbouring household's own decision, from its needs (street.py), so its chance is 1 once
    they have decided; a night out is the street's table for the group and their bodies (night.py); sickness and
    injury are health.py's draws."""
    import night as nightmod
    import weather
    out = []
    for k, m in enumerate(week.days, 1):
        q = m.quiet
        for r in q.rain_events:
            out.append({"what": "rain began", "day": k, "minute": r["minute"], "chance": round(weather.wet_chance(k), 3),
                        "conditions": ["the sky's own draw for the day", "by the calendar's climate"]})
        for sc in q.door_scenes:
            out.append({"what": "a knock at the front door", "day": k, "minute": sc.get("start"), "chance": 1.0,
                        "conditions": [f"the household at no. {sc.get('home')} decided to come",
                                       f"what they came for: {str(sc.get('purpose')).replace('_', ' ')}"]})
    for k, n in enumerate(week.nights, 1):
        for g in n.groups:
            base = nightmod.ALONE if len(g["members"]) == 1 else nightmod.GROUP
            cum = [c for c, _ in base]
            table = g.get("table") or [c - b for c, b in zip(cum, [0] + cum[:-1])]
            st = "not_back" if g.get("spared") else g["street"]
            chance = dict(zip(nightmod.STREETS, table))[st]
            out.append({"what": f"the street at night: {g['outcome']}", "day": k, "who": g["members"],
                        "chance": round(chance, 4), "draw": round(g["u"], 4),
                        "conditions": [("alone" if len(g["members"]) == 1 else "together"),
                                       ("further along the street" if g.get("far") else "next door"),
                                       "the street's table for those who went, shifted by how weak they were"]
                        + (["Leo is not lost: he came back hurt instead"] if g.get("spared") else []),
                        "chosen": n.choices.get(g["leader"]), "lost": g["lost"]})
    for d in week.brain.health.draws:
        out.append({"what": f"health: {d['what']}", "day": d["day"], "who": d["who"], "chance": d["chance"],
                    "draw": d["draw"], "conditions": d["conditions"], "hit": d["hit"]})
    return out


def count(n, days=DAYS):
    """Seeds 1 to n at the world's own odds: how many days were empty, and whether any week had three in a row
    (7.4, "The nudge, only if measured to be needed"; the LLM-off test, L8)."""
    empty = total = in_a_row = 0
    per_week = {}
    for seed in range(1, n + 1):
        em = empty_days(run(seed, days).transcript())
        mine = sum(1 for k in em if not em[k])
        empty, total = empty + mine, total + len(em)
        in_a_row += longest_empty_run(em) >= 3
        per_week[mine] = per_week.get(mine, 0) + 1
    rate = empty / total * 7
    line = (f"{n} weeks of {days} days: {empty} empty days of {total}, {rate:.2f} a week; weeks with 3 empty days in a "
            f"row: {in_a_row}; weeks by number of empty days: {dict(sorted(per_week.items()))}. The nudge is "
            + ("not needed" if rate <= 1 and not in_a_row else "called for")
            + ": it is built only at more than 1 empty day a week, or 3 in a row in any week.")
    return {"empty": empty, "days": total, "a_week": rate, "three_in_a_row": in_a_row, "line": line}


def lines(week):
    """One line per act of the week that is not staying put, for reading at the terminal."""
    tr = week.transcript()
    out = []
    for k in range(1, len(week.days) + 1):
        moods = tr["moods"].get(str(k), {})
        out.append(f"== day {k}: " + "; ".join(f"{data.PEOPLE[p]['name']} {m['mood']}"
                                               + (f" ({m['cause']})" if m["cause"] else "") for p, m in moods.items()))
        for turn in tr[f"day{k}"]["turns"]:
            for a in turn["acts"]:
                if a["option"] == "silent":
                    continue
                why = a.get("why") or {}
                terms = "; ".join(f"{n} {v:+.2f}" for n, v in why.get("terms", []))
                new = f" NEW: {why['new_cause']}" if why.get("new_cause") else ""
                out.append(f"  {data.clock(a['minute']):>6} {a['who']:7} {a['option']:17} "
                           f"{(a['words'] or ''):50.50} | {terms}{new}")
        n = tr.get(f"night{k}")
        if n:
            for d in n["decisions"]:
                why = d.get("why") or {}
                terms = "; ".join(f"{nm} {v:+.2f}" for nm, v in why.get("terms", []))
                out.append(f"   night {d['person']:7} {d['ask']:9} {d['option']:17} {(d.get('say') or ''):40.40} | {terms}")
            out.append("   night: " + "; ".join(f"{g['members']} {g['outcome']}, food {g['took']}"
                                                + (f", {g['lost']} lost" if g["lost"] else "") for g in n["groups"])
                       + f" | shelf {n['portions_after'] if 'portions_after' in n else ''}")
            step = tr[f"mind{k}"].get("night_step") or {}
            for line in step.get("lines", []) + step.get("health", []):
                out.append(f"   step: {line}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Play one week in code mode.")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--days", type=int, default=DAYS)
    ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
    ap.add_argument("--count", type=int, default=0, metavar="N",
                    help="play seeds 1 to N and count the empty days (the slow check of L8); nothing is written")
    args = ap.parse_args(argv)
    if args.count:
        print(count(args.count, args.days)["line"])
        return 0
    week = run(args.seed, args.days, scenario=args.scenario)
    for line in lines(week):
        print(line)
    out = os.path.join(HERE, "runs", "week")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"seed{args.seed}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(week.transcript(), f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
