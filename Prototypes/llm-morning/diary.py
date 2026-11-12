"""The diary of a week: what you read (Docs/fable-audit-2026-11.md, 7.5; section 9, step 4).

    python diary.py --seed 2          # plays the week and writes runs/week/week-seed2.md

One section a day, at most 60 lines; an empty day (week.empty_days) takes at most 8. A day opens with one line of
moods, each with its cause where it has one. Then the day by its hours: the morning, the day's work, the afternoon,
the evening, the night. Each line says who did or said what; what was said is quoted as it was said. Where the brain
weighed something, the line ends with why, in the brain's own plain words (content/weights.json, "words").

Routine is folded: a meal and its eating are one line, the day's tasks are one line, a run of small talk is one line,
the night's sleepers are one line. Nothing is invented here: every sentence is built from the week's record.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import data         # noqa: E402
import week as weekmod      # noqa: E402
from brain import left_words        # noqa: E402

NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
MAX_LINES, MAX_EMPTY = 60, 8
UNKNOWN = []        # acts the diary had no sentence of its own for (the gate: none)
BEATS = (("Morning", 0, 180), ("The day's work", 180, 480), ("Afternoon", 480, 720), ("Evening", 720, 10 ** 6))
TASK_DID = {"boards": "went round the boards", "water": "saw to the water", "watch": "kept watch",
            "stores": "counted the stores"}
BED = {"sleep": "slept", "lie_awake": "lay awake", "watch_door": "sat up by the front door",
       "go_next_door": "waited until the house was quiet and went out to the neighbour's house",
       "go_further": "waited until the house was quiet and went out along the street", "rain_out": "set the bin out"}


def names(ids):
    return data._and([NAMES[x] for x in ids])


def he(pid, form="he"):
    return data.PRONOUNS[pid][form]


def quoted(words):
    return f" “{words}”" if words else ""


def why_of(a):
    """The brain's reasons for an act, in its own plain words: the two that weighed most for it, and a new cause."""
    why = a.get("why") or {}
    terms = [n for n, v in why.get("terms", []) if v > 0 and n != "as a rule"][:2]
    parts = ([f"new: {why['new_cause']}"] if why.get("new_cause") else []) + terms
    return f" *({'; '.join(parts)})*" if parts else ""


def target_of(option, prefixes):
    for pre in prefixes:
        if option.startswith(pre):
            rest = option[len(pre):]
            for q in data.ORDER:
                if rest == q or rest.startswith(q + "_"):
                    return q
    return None


def sentence(a):
    """One act as one sentence, without its reason; None for an act the diary folds or leaves out."""
    o, A, w = a["option"], NAMES[a["who"]], quoted(a["words"])
    t = target_of(o, ("accuse_", "confront_", "reassure_", "say_to_", "keep_", "object_", "send_", "back_", "aside_",
                      "sit_", "plate_to_", "task_tend_", "give_"))
    T = NAMES[t] if t else None
    his = he(a["who"], "his")
    simple = {
        "ask_who": f"{A} asked who took the can:{w}", "deny": f"{A} said it was not {he(a['who'], 'him')}:{w}",
        "confess": f"{A} owned up:{w}", "reassure_all": f"{A} tried to calm everyone:{w}",
        "volunteer": f"{A} said {he(a['who'])} would go next door tonight:{w}",
        "still_going": f"{A} said {he(a['who'])} still meant to go tonight:{w}",
        "volunteer_far": f"{A} said {he(a['who'])} would go further along the street tonight:{w}",
        "propose_trip": f"{A} said someone should go next door tonight:{w}",
        "propose_far": f"{A} said someone should try the houses further along:{w}",
        "nobody_goes": f"{A} said nobody should go out:{w}", "object_trip": f"{A} said nobody should go out:{w}",
        "refuse_to_go": f"{A} said {he(a['who'])} would not go:{w}", "decline": f"{A} said {he(a['who'])} would not go:{w}",
        "ration_water": f"{A} said the water would go out by the cup from now on:{w}",
        "save_water": f"{A} said the stored water was for drinking only:{w}",
        "collect_rain": f"{A} went out the back into the rain and set the bin under the drainpipe.",
        "door_look": f"{A} looked through the gap in the boards.", "door_call": f"{A} called out through the door:{w}",
        "door_open": f"{A} unbarred the front door and opened it.", "door_give": f"{A} handed water out at the door.",
        "door_refuse": f"{A} sent whoever it was away:{w}",
        "plate_back": f"{A} put {his} share back and did not eat:{w}",
        "eat": f"{A} took a portion from the shelf and ate it.", "share": f"{A} shared out the last of the food.",
        "search": f"{A} searched the {data.ROOMS.get(a['room'], 'room')} for the can.",
        "water_round": f"{A} handed out the water, a cup each:{w}",
    }
    if o in simple:
        return simple[o]
    if o in ("silent", "keep_searching", "plate_eat", "cup_drink", "accept_aside", "refuse_aside", "eat_given",
             "refuse_given") or (o.startswith("task_") and not o.startswith("task_tend_")):
        return None
    if o in ("meal", "meal_small"):
        what = "a small meal" if o == "meal_small" else "the meal"
        return f"{A} set out {what}:{w}"
    if o.startswith("accuse_"):
        return f"{A} accused {T}:{w}"
    if o.startswith("confront_"):
        return f"{A} had it out with {T}:{w}"
    if o.startswith("reassure_"):
        return f"{A} comforted {T}:{w}"
    if o.startswith("say_to_"):
        return f"{A} to {T}:{w}"
    if o == "say_other":
        return f"{A}:{w}"
    if o.startswith("keep_") or o.startswith("object_"):
        return f"{A} told {T} to stay home:{w}"
    if o.startswith(("send_", "back_")):
        return f"{A} said {T} should be the one to go:{w}"
    if o.startswith("aside_"):
        came = (a.get("aside") or {}).get("accepted")
        return f"{A} took {T} aside." if came else f"{A} asked {T} to come aside; {he(t)} would not."
    if o.startswith("sit_"):
        return f"{A} sat with {T}."
    if o.startswith("plate_to_"):
        return f"{A} gave {his} share to {T}:{w}"
    if o.startswith("task_tend_"):
        return f"{A} looked after {T}."
    if o.startswith("go_"):
        room = o[len("go_"):]
        return f"{A} went to the {data.ROOMS[room]}." if room in data.ROOMS else None
    UNKNOWN.append(o)
    return f"{A} {a.get('came_of_it') or o}{w}"       # anything else: as the record itself puts it


def moods_line(moods):
    """One line: who woke how, and from what. Steady is not said."""
    parts, plain = [], {}
    for pid, m in moods.items():
        if m["mood"] == "steady":
            continue
        if m["cause"]:
            parts.append(f"{NAMES[pid]} woke {m['mood']}: {m['cause']}.")
        else:
            plain.setdefault(m["mood"], []).append(pid)
    parts += [f"{names(ids)} woke {mood}." for mood, ids in plain.items()]
    return " ".join(parts)


def day_section(tr, k, start_shelf, away, empty):
    acts = tr[f"day{k}"]["turns"]
    lines = []
    head = f"## Day {k}" + (" (a quiet day)" if empty else "")
    shelf = left_words(start_shelf) if start_shelf > 0 else "Nothing"
    opening = f"{shelf[0].upper() + shelf[1:]} on the shelf."
    if away:
        opening += f" {names(away)} {'is' if len(away) == 1 else 'are'} gone."
    moods = moods_line(tr["moods"].get(str(k), {}))
    lines.append(opening + (" " + moods if moods else ""))
    for label, lo, hi in BEATS:
        items, talk, tasks, eaters = [], [], [], []
        served, some_did_not, verb = None, False, "ate"

        def flush_talk():
            if talk:
                items.append(" ".join(talk))
                talk.clear()

        def flush_meal():
            nonlocal served, some_did_not, verb
            if served is not None:
                everyone = f"The others {verb}." if some_did_not else f"Everyone {verb}."
                items[served] += (f" {everyone}" if len(set(eaters)) > 2
                                  else f" {names(sorted(set(eaters), key=data.ORDER.index))} {verb}." if eaters else "")
                served, some_did_not = None, False
                eaters.clear()
        for turn in acts:
            if not lo <= turn["minute"] < hi:
                continue
            for a in turn["acts"]:
                o = a["option"]
                if o == "silent" or (a["mode"] == "routine" and o != "silent"):
                    continue
                if o in ("plate_eat", "cup_drink"):
                    eaters.append(a["who"])
                    continue
                if o.startswith("task_") and not o.startswith("task_tend_"):
                    tasks.append(f"{NAMES[a['who']]} {TASK_DID.get(o[len('task_'):], o)}")
                    continue
                s = sentence(a)
                if s is None:
                    continue
                if o.startswith("say_to_") or o == "say_other":     # a run of small talk is one line
                    talk.append(s + why_of(a) if (a.get("why") or {}).get("new_cause") else s)
                    continue
                flush_talk()
                if o == "plate_back" or o.startswith("plate_to_"):
                    some_did_not = True
                if o in ("meal", "meal_small", "water_round"):
                    flush_meal()
                    items.append(s)
                    served, verb = len(items) - 1, "drank" if o == "water_round" else "ate"
                    continue
                items.append(s + why_of(a))
        flush_talk()
        flush_meal()
        if tasks:
            hurt = [e["line"] for e in (tr.get("health") or {}).get("events", [])
                    if e["day"] == k and e["change"] == "onset" and e["kind_of_cause"] == "work"]
            items.insert(0, "; ".join(tasks) + "." + ("".join(" " + x for x in hurt)))
        if items:
            lines.append(f"**{label}.** {items[0]}")
            lines += items[1:]
    return head, lines


def night_section(tr, k):
    n = tr.get(f"night{k}")
    if n is None:
        return []
    lines = []
    beds = {}
    for d in n["decisions"]:
        if d["ask"] == "bedtime":
            beds.setdefault(d["option"], []).append(d["person"])
    quiet = "; ".join(f"{names(ids)} {BED[o]}" for o, ids in beds.items() if o in ("sleep", "lie_awake", "watch_door",
                                                                                   "rain_out"))
    goers = [(o, ids) for o, ids in beds.items() if o in ("go_next_door", "go_further")]
    lines.append(f"**Night.** {quiet[0].upper() + quiet[1:]}." if quiet else "**Night.**")
    for o, ids in goers:
        d = next(x for x in n["decisions"] if x["person"] == ids[0] and x["ask"] == "bedtime")
        lines.append(f"{names(ids)} {BED[o]}." + why_of(d))
    for d in n["decisions"]:
        o, A, w = d["option"], NAMES[d["person"]], quoted(d.get("say"))
        t = target_of(o, ("stop_", "let_", "go_with_"))
        if d["ask"] == "reaction":
            s = {"stay_in_bed": f"{A} heard the front door and stayed in bed.",
                 "get_up_and_look": f"{A} heard the front door, got up, and waited by it until morning.",
                 "go_after": f"{A} got up and followed.", "go_later": f"{A} waited, meaning to go later.",
                 "stay_home": f"{A} stayed in bed after all."}.get(o)
            if o.startswith("stop_"):
                s = f"{A} told {NAMES[t]} not to go:{w}"
            elif o.startswith("let_"):
                s = f"{A} saw {NAMES[t]} go and said nothing."
            elif o.startswith("go_with_"):
                s = f"{A} went with {NAMES[t]}."
            if s:
                lines.append(s + why_of(d))
        elif d["ask"] == "answer":
            lines.append((f"{A} went all the same:{w}" if o == "go_anyway" else f"{A} went back to bed:{w}") + why_of(d))
    for g in n["groups"]:
        who = names(g["members"])
        was = "was" if len(g["members"]) == 1 else "were"
        out = g["outcome"]
        if g["took"]:
            out += f" ({g['took']:g} portion{'' if g['took'] == 1 else 's'})"
        lines.append(f"{who} {was} {out}." + (" Leo should not have come back from that one: the game spares him."
                                               if g.get("spared") else ""))
    step = (tr.get(f"mind{k}") or {}).get("night_step") or {}
    tail = list(step.get("lines", [])) + list(step.get("health", []))
    if step.get("guilt"):
        tail.append(f"It weighed more on {NAMES[step['guilt']['who']]}: {step['guilt']['why']}.")
    if tail and len(lines) == 1:           # a night with nothing but sleep: one line, with what the night settled
        lines[0] += " " + " ".join(tail)
    elif tail:
        lines.append(" ".join(tail))
    return lines


def render(w):
    """The whole week as markdown."""
    tr = w.transcript()
    empties = weekmod.empty_days(tr)
    out = [f"# The week, seed {w.seed}", "",
           "Elena, 42, the mother. Daniel, 25. Leo, 21. Mara, 17. The house is shut; the taps are dry; a can is "
           "missing from the shelf.", ""]
    for k, m in enumerate(w.days, 1):
        head, lines = day_section(tr, k, m.start_portions, sorted(m.away, key=data.ORDER.index), not empties[k])
        out += [head, ""] + [x for line in lines + night_section(tr, k) for x in (line, "")]
    return "\n".join(out).rstrip() + "\n"


def day_lengths(text):
    """{day: its number of lines} of a rendered diary, and which days it marks as quiet."""
    lengths, quiet, day = {}, set(), None
    for line in text.splitlines():
        if line.startswith("## Day "):
            day = int(line.split()[2])
            lengths[day] = 0
            if "(a quiet day)" in line:
                quiet.add(day)
        elif day is not None and line.strip():
            lengths[day] += 1
    return lengths, quiet


def main(argv=None):
    ap = argparse.ArgumentParser(description="Play one week in code mode and write its diary.")
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--days", type=int, default=weekmod.DAYS)
    args = ap.parse_args(argv)
    text = render(weekmod.run(args.seed, args.days))
    out = os.path.join(HERE, "runs", "week")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"week-seed{args.seed}.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote {os.path.relpath(path, HERE)}: " + ", ".join(f"day {k} {n} lines" for k, n in day_lengths(text)[0].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
