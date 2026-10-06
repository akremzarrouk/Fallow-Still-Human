"""Writes a finished morning as a story, in the style of Tools/narrate-morning.

Everything here comes from the morning's own record, so the same answers always give
the same bytes: no clock, no call counts, no run time.
"""
import data
from world import (FALL_EVERY, FEELING_SHOWS_FOR_TURNS, INNER_EVERY, KIND_DONE, LULL_EVERY, LULL_QUIET,
                   QUIET_TURNS, grudge_facts, hunger_words, trait_words)

DAYS_KNOWN = {"did": "did it", "saw": "saw it", "heard": "heard it"}
ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}   # 5th: an extra answer to a give (body_design §2.5)


def fold_runs(log):
    """(turn index, person) -> ("head", n, last minute) | ("hidden",) for routine runs."""
    folds = {}
    for pid in data.ORDER:
        run = []

        def close():
            if len(run) > 1:
                folds[(run[0], pid)] = ("head", len(run), log[run[-1]]["minute"])
                for i in run[1:]:
                    folds[(i, pid)] = ("hidden",)
            run.clear()

        prev = None
        for i, rec in enumerate(log):
            d = next((x for x in rec["decisions"] if x["person"] == pid), None)   # None: away on day 2
            sig = (d["label"], d["came_of_it"]) if d and d["mode"] == "routine" else None
            if sig is None or sig != prev:
                close()
            if sig is not None:
                run.append(i)
            prev = sig
        close()
    return folds


def quoted(words):
    return f"“{words}”"


def cap(text):
    return text[0].upper() + text[1:]


def newness(d):
    if "new" not in d or d.get("new") is None:
        return ""
    return f" *({'new' if d['new'] else 'not new'}: {d['new_why']})*"


def decision_line(d, fold=None):
    name = data.PEOPLE[d["person"]]["name"]
    if fold:
        _, n, last = fold
        return (f"- **{name}, minutes {d['minute']:02d}–{last:02d} ({n} decisions, the same each "
                f"time).** Rules: nothing social happened to them. **{cap(d['label'])}** each "
                f"time. Came of it: {d['came_of_it']}")
    fact = f" New in the room: {d['new_fact']}." if d.get("new_fact") else ""
    if d["mode"] == "routine":
        return (f"- **{name}.** Rules: nothing social happened to them. **{cap(d['label'])}**. "
                f"Came of it: {d['came_of_it']}{fact}")
    order = f" ({ORDINAL[d['place']]} to act in the {data.ROOMS[d['room']]}: {d['order_reason']})"
    if d.get("food_moment"):
        f = d["food_moment"]
        last = "not since before yesterday" if f["band"] == "before yesterday" else f["band"]
        because = (f"**Food moment**, starving in the kitchen with {f['portions']} portion"
                   f"{'s' if f['portions'] != 1 else ''} on the shelf; last ate: {last} (chance {f['chance']:g} a "
                   f"turn, draw {f['draw']:.4f})")
    elif d.get("trip_moment") is not None:
        because = f"**The food**: {d['trip_why']}"
        if d.get("inner"):
            because += "; also an inner moment: " + "; ".join(d["inner"])
        elif d["triggers"]:
            because += "; also a social moment: " + "; ".join(d["triggers"])
    elif d.get("inner"):
        because = "**Inner moment**, nothing social happening: " + "; ".join(d["inner"])
    elif d.get("lull") is not None:
        because = f"**Lull**, nothing said or done in the {data.ROOMS[d['room']]} since minute {d['lull']:02d}"
    else:
        because = "Social moment: " + "; ".join(d["triggers"])
    held = (f" Not offered: {KIND_DONE[d['held_back']]} three turns in a row, so no more of it "
            f"this turn." if d.get("held_back") else "")
    if d["mode"] == "fallback":
        return (f"- **{name}**{order}. {because}.{held} **FALLBACK**: the model's "
                f"answer could not be used ({d['invalid']}), so the rules chose: **{d['label']}**. "
                f"Came of it: {d['came_of_it']}{fact}")
    said = f", saying {quoted(d['say'])}" if d.get("say") else ""

    def kept(result):
        return f" (kept: it falls at most one step per {FALL_EVERY} minutes)" if result == "held" else ""
    inside = (f" Suspects: {d['suspects']}, so {d['suspects_now']}{kept(d['suspects_result'])}. "
              f"Angry at: {d['angry_at']}; {d['grudge_note']}.")
    return (f"- **{name}**{order}. {because}.{held} **Chose: {d['label']}**{said}"
            f"{newness(d)} (one of {d['offered']} options). Feeling: *{d['feeling']}*. "
            f"Reason: {quoted(d['reason'])}{inside} Came of it: {d['came_of_it']}{fact}")


def room_line(rec):
    parts, empty = [], []
    for r, people in rec["rooms"].items():
        if people:
            parts.append(f"{data.ROOMS[r]}: " + ", ".join(f"{n} {what}" for n, what in people))
        else:
            empty.append(data.ROOMS[r])
    if empty:
        parts.append("nobody in " + ", ".join(empty))
    return f"**min {rec['minute']:02d}** · " + " · ".join(parts)


def convo_line(entry):
    minute, room, what, why = entry
    if what == "started":
        return f"- *The {data.ROOMS[room]}'s conversation starts (minute {minute:02d}): {why}.*"
    return f"- *The {data.ROOMS[room]}'s conversation ends (minute {minute:02d}): {why}.*"


def render(morning, seed, model_name, command):
    log = morning.log
    for rec in log:
        for d in rec["decisions"]:
            d["minute"] = rec["minute"]
    all_d = [d for rec in log for d in rec["decisions"]]
    n_model = sum(d["mode"] == "model" for d in all_d)
    n_fall = sum(d["mode"] == "fallback" for d in all_d)
    n_rout = sum(d["mode"] == "routine" for d in all_d)
    n_new = sum(1 for s in morning.said if s["new"])
    ends = [e for e in morning.convos.log if e[2] == "ended"]
    n_inner = sum(1 for d in all_d if d.get("inner"))
    asides = [d for d in all_d if d["option"] in ("accept_aside", "refuse_aside")]
    n_went = sum(d["option"] == "accept_aside" for d in asides)
    out = []
    w = out.append

    culprit = morning.culprit                       # who took the can, or None
    who = data.PEOPLE[culprit]["name"] if culprit else None
    pro = data.PRONOUNS[culprit] if culprit else None
    w(f"# The morning as a story: {morning.scenario}, rules and a language model, seed {seed}")
    w("")
    w(f"Generated by `{command}` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. "
      "Rules keep the house and each person's memory, and list what each of them may do. When "
      f"something social has just happened to someone, the model `{model_name}` chooses among "
      "those options for them, says the words, and names a feeling. Every other turn is settled "
      "by the rules. Within a turn the people in a room act one after another, each seeing what "
      "was said before them. Do not edit it by hand; run the script again.")
    w("")
    w(f"**{len(all_d)} decisions** in {data.MINUTES} minutes, one per person every "
      f"{data.MINUTES_PER_TURN} minutes: {n_model} by the model at social moments, {n_fall} where "
      f"the model's answer could not be used and the rules chose instead, {n_rout} routine ones "
      f"settled by the rules. {len(morning.said)} lines were spoken aloud, {n_new} of them new. "
      f"Conversations ended {len(ends)} time{'s' if len(ends) != 1 else ''}. {n_inner} inner "
      f"moment{'s' if n_inner != 1 else ''}. {len(asides)} private talk{'s' if len(asides) != 1 else ''} "
      f"asked for ({n_went} accepted, {len(asides) - n_went} refused). The pantry held "
      f"{data.PORTIONS} portions at the start and {morning.portions} at the end.")
    w("")
    w("## How to read it")
    w("")
    w("- **Order**: in each room people act one after another. Whoever was just spoken to or "
      "accused goes first (the most recent first), then whoever shows the strongest feeling, "
      "then an order drawn from the seed. Each line says who was how many-th to act in the room "
      "and why.")
    w("- **Social moment**: something social had just happened to this person (someone spoke "
      "where they could hear it, accused them, came to sit with them, ate in front of them, "
      "looks upset in the same room, or someone came in). Only then is the model asked. What "
      "happened is listed.")
    w("- **Chose**: the option the model picked from those the rules offered. Its words are in "
      "quotes. The feeling and the one-sentence reason are the model's, as it wrote them.")
    w("- **New / not new**: a line is new if it is a question, an accusation, a denial of a new "
      "accusation, or a confession, and the speaker has not taken that stance before. "
      "Reassurance, repeated stances and other remarks are not new. Something eaten, shared or "
      "found, or someone coming in, is new too.")
    w(f"- **Conversation ends**: after {QUIET_TURNS} full turns in a row with nothing new in a "
      "room, or when fewer than two people are left in it. From then on only something new there "
      "is a social moment, and it starts the conversation again.")
    w("- **Inside each of them** the rules keep hunger (" + ", ".join(
        f"*{x}*" for x in ["a little hungry", "hungry", "very hungry", "starving"]) + "), a "
      "suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others "
      + (f"(0 to 3), and for {who}, guilt (1 to 3). " if culprit else
         "(0 to 3); nobody took the can, so nobody carries guilt. ") + "The model is shown the events behind them as "
      "plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an "
      "inner moment comes.")
    w("- **Suspects**: every model answer names who they now believe took the can, or nobody. "
      "Naming the same person again raises it a step. Naming nobody or someone else lets it fall "
      f"a step, but never more than one step per {FALL_EVERY} minutes (*kept* when it could not "
      "fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.")
    w("- **Grudges** rise a step from events the rules see: being accused of taking the can when "
      "you had not; hearing someone admit it after denying it to you, and a step more if they had "
      "accused you; seeing someone eat a portion while you are hungry (not when food is shared "
      "out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when "
      f"{FALL_EVERY} minutes have passed since it last changed, and only on an answer that does not "
      "name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.")
    if culprit:
        w(f"- **{who}'s guilt** starts at 1 and rises a step when someone else is accused of what {pro['he']} "
          f"did in {pro['his']} hearing (by anyone, {pro['himself']} included), or when someone reassures {pro['him']} "
          f"personally. {pro['his'].capitalize()} denials, and reassurance of everyone, add nothing. It never falls, and it "
          "never decides anything: the model still chooses.")
    else:
        w("- **Guilt**: in this scenario nobody took the can, so nobody carries guilt and nobody is "
          "offered *admit taking it*.")
    w(f"- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has "
      f"risen a level since they last decided with the model; the model is asked, at most once "
      f"every {INNER_EVERY} minutes per person. What rose is listed.")
    w("- **The food** (once per morning): at the start of the first turn when the shelf is empty or "
      "someone is very hungry, everyone learns that there is no food for tomorrow and that the "
      "neighbour's house may have some, and may then say whether someone should go there tonight. "
      "Whoever is in the kitchen at the empty shelf, or whoever became very hungry, is asked the "
      "model that turn. What brought it on is listed.")
    w(f"- **Lull**: nothing social or inner, but nothing has been said or done in their room for at "
      f"least {LULL_QUIET} minutes (staying put in silence and staying seated do not count), and they "
      f"have not been asked for at least {LULL_EVERY} minutes; the model is asked, and told since when "
      "the room has been still.")
    w("- **Take aside**: someone can ask a person in the room who has not acted yet this turn to "
      "come to an empty room. That person answers at once (their decision for the turn): go, and "
      "both move there and can talk alone; or refuse.")
    w("- **Not offered**: a speech act someone used three turns in a row is not offered a fourth "
      "time.")
    w("- **Rules**: nothing social happened to this person; they carried on with what they were "
      "doing, or stayed put.")
    w("- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose "
      "as on a routine turn.")
    w(f"- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in "
      f"the room for {data.MINUTES_PER_TURN * FEELING_SHOWS_FOR_TURNS} minutes. One that does not "
      "(guilty, ashamed, anxious, tense...) stays with the person who feels it.")
    w("- Voices carry between rooms without the words, except into or out of the bathroom.")
    w("- Each **min** line lists every room at that minute: who is in it and what they are doing. "
      "A minute is shown only when something is told there.")
    w("- A line headed with a minute range folds a run of identical routine decisions by one person.")
    w("")

    w("## The cast at minute 0")
    w("")
    names = [data.PEOPLE[p]["name"] for p in data.ORDER]
    w("| | " + " | ".join(names) + " |")
    w("|---|" + "---|" * len(names))

    def knows(p):
        pid = next(q for q in data.ORDER if data.PEOPLE[q] is p)
        if pid == culprit:
            return "ate it in the night; nobody saw"
        note = data.about_the_can(morning.scenario, pid)
        return "only that it is missing" + (f"; told: {quoted(note)}" if note else "")
    rows = [
        ("Age", lambda p: str(p["age"])),
        ("Role in the family", lambda p: p["role_short"]),
        ("Where, how hungry", lambda p: f"kitchen, hunger {p['hunger']:.2f} ({hunger_words(p['hunger'])})"),
        ("Temperament", lambda p: trait_words(p["traits"])),
        ("What matters to them", lambda p: ", ".join(p["values"])),
        ("Knows about the can", knows),
    ]
    for label, f in rows:
        w(f"| {label} | " + " | ".join(f(data.PEOPLE[p]) for p in data.ORDER) + " |")
    w("")
    w("### What each of them remembers at minute 0")
    w("")
    w("One row per thing that happened, with how each of them came to know it. This is all the "
      "model is ever told about the days before.")
    w("")
    w("| Day | What happened | " + " | ".join(names) + " |")
    w("|---|---|" + "---|" * len(names))
    for day, text, knew in data.backstory(morning.scenario):
        w(f"| {day} | {text} | " + " | ".join(DAYS_KNOWN.get(knew.get(p), "not there") for p in data.ORDER) + " |")
    w(f"| 4 | {data.OPENING} | " + " | ".join("did it" if p == "elena" else "saw it" for p in data.ORDER) + " |")
    w("")
    body(morning, out, all_d, names, culprit, who, pro)
    return "\n".join(out)


def body(morning, out, all_d, names, culprit, who, pro):
    """The morning turn by turn, what was said, and how it ended: day 1's, and day 2's too
    (reports/night_design.md, §8)."""
    w = out.append
    log = morning.log
    w("## The morning")
    w("")
    folds = fold_runs(log)
    for i, rec in enumerate(log):
        lines = []
        for d in rec["decisions"]:
            f = folds.get((i, d["person"]))
            if f and f[0] == "hidden":
                continue
            lines.append(decision_line(d, f))
        lines += [f"- *{who}'s guilt, now {level} of 3: {why}.*" for _, level, why in rec["guilt"]]
        lines += [f"- *{data.PEOPLE[h]['name']}'s grudge against {data.PEOPLE[a]['name']}, now {g} of 3: {why}.*"
                  for _, h, a, g, why in rec["grudges"]]
        lines += [convo_line(e) for e in rec["convo"]]
        if not lines:
            continue
        w(room_line(rec))
        out.extend(lines)
        w("")

    w("## What was said")
    w("")
    if not morning.said:
        w("Nobody said anything all morning.")
    for s in morning.said:
        tag = f"new: {s['why']}" if s["new"] else f"not new: {s['why']}"
        w(f"- min {s['minute']:02d}, {s['room']}. {s['text']} *({tag})*")
    w("")

    w("## At the end")
    w("")
    where = []
    for r in data.ROOMS:
        people = [q.name for q in morning.people.values() if q.room == r]
        if people:
            where.append(f"{data.ROOMS[r]}: {', '.join(people)}")
    if morning.away:
        where.append("away: " + ", ".join(data.PEOPLE[q]["name"] for q in data.ORDER if q in morning.away))
    eaten = [f"{q.name} {q.eaten:g}" for q in morning.people.values() if q.eaten]
    w(f"At minute {data.MINUTES}: {'; '.join(where)}. {morning.portions} of {morning.start_portions} portions "
      f"left; eaten this morning: {', '.join(eaten) if eaten else 'none'}.")
    w("")
    confessed = [d for d in all_d if d["option"] == "confess" and d["mode"] == "model"]
    w("- Who admitted taking it: " + (", ".join(f"{data.PEOPLE[d['person']]['name']} at minute "
                                                 f"{d['minute']:02d}" for d in confessed) or "nobody") + ".")
    acc = [f"{data.PEOPLE[d['person']]['name']} accused {data.PEOPLE[d['option'][7:]]['name']} "
           f"(minute {d['minute']:02d})" for d in all_d if d["option"].startswith("accuse_")]
    w("- Accusations: " + ("; ".join(acc) if acc else "none") + ".")
    if culprit:
        knowers = [q.name for q in morning.people.values() if q.knows_culprit == culprit and q.id != culprit]
        w(f"- Who else knows {who} took it: " + (", ".join(knowers) if knowers else "nobody") + ".")
    else:
        w("- Nobody took the can: the count was wrong from the start.")
    talk = [f"{data.ROOMS[r]} {what} at minute {m:02d} ({why})" for m, r, what, why in morning.convos.log]
    w("- Conversations: " + "; ".join(talk) + ".")
    trip = morning.trip
    if morning.day != 4:
        w("- The food: carried over from yesterday.")
    elif trip:
        asked = ", ".join(data.PEOPLE[q]["name"] for q in trip["asked"])
        w(f"- The food: came up at minute {trip['minute']:02d} ({'; '.join(trip['why'])}); asked then: {asked}.")
    else:
        w("- The food: never came up.")
    w(f"- The plan for tonight: {morning.plan_text()}.")
    w("")
    w("What is inside each of them at minute 90:")
    w("")
    w("| | " + " | ".join(names) + " |")
    w("|---|" + "---|" * len(names))
    w("| Suspicion | " + " | ".join(f"{morning.people[p].suspicion.short('suspects')}" for p in data.ORDER) + " |")

    def grudges(p):
        held = [(t, g) for t, g in morning.people[p].grudges.items() if g.strength]
        return ", ".join(f"{data.PEOPLE[t]['name']} {g.strength}/3" for t, g in held) or "none"
    w("| Grudges | " + " | ".join(grudges(p) for p in data.ORDER) + " |")
    w("| Hunger | " + " | ".join(hunger_words(morning.people[p].hunger) for p in data.ORDER) + " |")
    w("| Guilt | " + " | ".join(f"{morning.people[p].guilt}/3" if morning.people[p].guilt is not None
                               else "-" for p in data.ORDER) + " |")
    w("")
    w("The events behind each grudge still held at minute 90" + (f", and behind {who}'s guilt:" if culprit else ":"))
    w("")
    any_held = False
    for p in data.ORDER:
        person = morning.people[p]
        for t, g in person.grudges.items():
            if g.strength:
                any_held = True
                facts = "; ".join(grudge_facts(data.PEOPLE[t]["name"], g.events))
                w(f"- {person.name} against {data.PEOPLE[t]['name']} ({g.strength}/3): {facts}.")
    if not any_held:
        w("- Nobody holds a grudge at minute 90.")
    if culprit:
        guilty = morning.people[culprit]
        facts = "; ".join(e[1] for e in guilty.guilt_events) or "nothing since"
        w(f"- {who}'s guilt ({guilty.guilt}/3): {pro['he']} ate the can in the night, and nobody saw; {facts}.")
    w("")
    last = []
    for pid in data.ORDER:
        mine = [d for d in all_d if d["person"] == pid and d["mode"] == "model"]
        name = data.PEOPLE[pid]["name"]
        last.append(f"{name} *{mine[-1]['feeling']}* (minute {mine[-1]['minute']:02d})" if mine
                    else f"{name}: never asked")
    w("- The last feeling each of them named: " + "; ".join(last) + ".")
    w("")


# ---------- the night and day 2 (reports/night_design.md, §8) ----------
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
NIGHT_TITLE = {1: "# The night", 2: "# The second night", 3: "# The third night"}
DAY_TITLE = {5: "# The next morning (day 5)", 6: "# The third morning (day 6)"}
ASKED = {"bedtime": "at bedtime", "reaction": "noticing it", "answer": "told not to go"}


def night_decision_line(d, where):
    head = f"Bedtime, {NAME[d['person']]}" if d["ask"] == "bedtime" else NAME[d["person"]]
    place = f" ({where}, {ASKED[d['ask']]})" if d["ask"] != "bedtime" else f" ({where})"
    if d["mode"] == "fallback":
        return (f"- **{head}**{place}. **FALLBACK**: the model's answer could not be used ({d['invalid']}), so "
                f"the rules chose: **{d['label']}**.")
    said = f", saying {quoted(d['say'])}" if d.get("say") else ""
    dropped = " (its words were dropped: only speech has words at night)" if d.get("dropped_line") else ""
    return (f"- **{head}**{place}. **Chose: {d['label']}**{said}{dropped} (one of {len(d['options'])} options). "
            f"Feeling: *{d['feeling']}*. Reason: {quoted(d['reason'])} Suspects: {d['suspects']}, so "
            f"{d['suspects_now']}. Angry at: {d['angry_at']}; {d['grudge_note']}.")


def noticing_line(n):
    who, of = NAME[n["who"]], NAME[n["of"]]
    place = "by the front door" if n["where"] == "kitchen" else f"in the {data.ROOMS[n['where']]}"
    draw = f" (draw {n['draw']:.3f}; wakes under {n['under']:.2f})" if n["draw"] is not None else ""
    if n["how"] == "door watch":
        return f"- Noticing: {who}, sitting up {place}, sees {of} come to the front door."
    if n["how"] == "room":
        if n["draw"] is None:
            return f"- Noticing: {who}, awake {place}, sees {of} get up."
        return f"- Noticing: {who}, asleep {place}, {'wakes and sees' if n['noticed'] else 'does not wake as'} {of} get{'' if n['noticed'] else 's'} up{draw}."
    if n["how"] == "front door":
        if n["draw"] is None:
            return f"- Noticing: {who}, awake {place}, hears the front door open."
        return f"- Noticing: {who}, asleep {place}, {'wakes at' if n['noticed'] else 'sleeps through'} the front door{draw}."
    if n["where"] == "kitchen":
        return f"- Noticing: {who}, {place}, sees who comes back."
    if n["draw"] is None:
        return f"- Noticing: {who}, awake {place}, hears the front door again."
    return f"- Noticing: {who}, asleep {place}, {'wakes at' if n['noticed'] else 'sleeps through'} the front door again{draw}."


def place_of(where):
    return "by the front door" if where == "kitchen" else data.ROOMS[where]


def render_night(n):
    """The night: bedtime, who noticed whom with each draw, the street and the house."""
    import night as night_mod
    out = []
    w = out.append
    w(NIGHT_TITLE.get(n.number, f"# Night {n.number}"))
    w("")
    w(f"{data.GAP} Before bed, hunger rose by {night_mod.GAP_HUNGER} × each person's hunger rate, and by "
      f"{night_mod.NIGHT_HUNGER} × more in the night. Everyone went to bed in their own room: {night_mod.BEDS}. "
      f"Each of them was asked one private decision. Whoever was awake saw or heard what happened near them; "
      f"whoever was asleep woke only on a draw under their threshold (roommate getting up: 0.30 + 0.40 × "
      f"anxious; the front door through a wall: 0.10 + 0.20 × anxious). Whoever noticed someone leave was "
      f"asked once more, and a leaver told not to go answered. Nothing else in the night was asked of the model.")
    w("")
    w("| | " + " | ".join(NAME[p] for p in data.ORDER) + " |")
    w("|---|" + "---|" * len(data.ORDER))
    w("| Hunger at bedtime | " + " | ".join("away" if n.bedtime_hunger[p] is None else
                                           f"{n.bedtime_hunger[p]:.2f} ({hunger_words(n.bedtime_hunger[p])})"
                                           for p in data.ORDER) + " |")
    w("| Wakes when the roommate gets up | " + " | ".join(f"{night_mod.wake_room(p):.2f}" for p in data.ORDER) + " |")
    w("| Wakes at the front door | " + " | ".join(f"{night_mod.wake_door(p):.2f}" for p in data.ORDER) + " |")
    w("")
    w("## Bedtime")
    w("")
    items = list(n.story)
    bedtime = [x for x in items if x[0] == "decision" and x[1]["ask"] == "bedtime"]
    for _, d in bedtime:
        w(night_decision_line(d, place_of(d["where"])))
    w("")
    w("## In the night")
    w("")
    rest = [x for x in items if not (x[0] == "decision" and x[1]["ask"] == "bedtime")]
    if not rest:
        w("Nobody got up. The night passed.")
    order = n.order()
    w("The order in which anyone who meant to go would get up: " + ", ".join(NAME[p] for p in order) + ".")
    w("")
    for kind, x in rest:
        if kind == "text":
            w(f"- {x}")
        elif kind == "noticing":
            w(noticing_line(x))
        else:
            w(night_decision_line(x, place_of(x["where"])))
    w("")
    w("## The neighbour's house and the street")
    w("")
    w(f"- The neighbour's house held {n.house} portion{'s' if n.house != 1 else ''} (draw {n.house_u:.3f}: 0 under "
      f"0.30, 2 under 0.65, 4 under 0.90, else 6).")
    if not n.groups:
        w("- Nobody went out.")
    for g in n.groups:
        who = " and ".join(NAME[p] for p in g["members"])
        alone = len(g["members"]) == 1
        cut = ("clean under 0.62, scared on the way there under 0.76, scared on the way back under 0.94, else not "
               "back" if alone else "clean under 0.70, scared on the way there under 0.82, scared on the way back "
               "under 0.97, else one of them not back")
        lost = (f" The lost draw {g['lost_u']:.3f} chose {NAME[g['lost']]}." if g.get("lost_u") is not None else "")
        took = (f" Found {g['found']} portion{'s' if g['found'] != 1 else ''} there; took {g['took']}."
                if g["found"] is not None else " Did not get inside.")
        w(f"- {who}, {'alone' if alone else 'together'}: street draw {g['u']:.3f} → {g['street']} ({cut}).{took}{lost} "
          f"Outcome: **{g['outcome']}**.")
    w("")
    w("## By morning")
    w("")
    away = ", ".join(NAME[p] for p in data.ORDER if p in n.away) or "nobody"
    w(f"- The shelf held {n.day1.portions} portion{'s' if n.day1.portions != 1 else ''} last night and holds "
      f"{n.portions} now. Not back: {away}.")
    w("")
    w("| | " + " | ".join(NAME[p] for p in data.ORDER) + " |")
    w("|---|" + "---|" * len(data.ORDER))
    w("| Hunger by morning | " + " | ".join("away" if n.morning_hunger[p] is None else
                                            f"{n.morning_hunger[p]:.2f} ({hunger_words(n.morning_hunger[p])})"
                                            for p in data.ORDER) + " |")
    w("")
    return "\n".join(out) + "\n"


def render_day2(morning):
    """Day 2 (house day 5): what each of them carried in, then the morning as day 1's."""
    log = morning.log
    for rec in log:
        for d in rec["decisions"]:
            d["minute"] = rec["minute"]
    all_d = [d for rec in log for d in rec["decisions"]]
    out = []
    w = out.append
    culprit = morning.culprit
    who = data.PEOPLE[culprit]["name"] if culprit else None
    pro = data.PRONOUNS[culprit] if culprit else None
    names = [NAME[p] for p in data.ORDER]
    n_model = sum(d["mode"] == "model" for d in all_d)
    n_fall = sum(d["mode"] == "fallback" for d in all_d)
    n_rout = sum(d["mode"] == "routine" for d in all_d)
    w(DAY_TITLE.get(morning.day, f"# The morning of day {morning.day}"))
    w("")
    w(f"The same rules as day 1, from the people as the night left them. **{len(all_d)} decisions**: {n_model} by "
      f"the model, {n_fall} fallbacks, {n_rout} routine. {len(morning.said)} lines were spoken aloud. The shelf held "
      f"{morning.start_portions} portion{'s' if morning.start_portions != 1 else ''} at minute 00.")
    w("")
    w("## What each of them carried in")
    w("")
    w("Each block is printed as their prompts carry it, with the opening of the morning and their lines about the "
      "food and the neighbour's house.")
    w("")
    for p in data.ORDER:
        if p in morning.away:
            w(f"**{NAME[p]}**: away, not back from the night.")
            w("")
            continue
        w(f"**{NAME[p]}**")
        w("")
        w("```")
        out.extend(morning.carry[p])
        out.extend(morning.carried[p])
        w("```")
        w("")
    body(morning, out, all_d, names, culprit, who, pro)
    return "\n".join(out)


def render_mind(mind):
    """What the night left in them (reports/days_design.md, §2.8): each person's night mind, every memory it
    proposed with the records it cites and its verdict, the feeling and the intent."""
    out = []
    w = out.append
    w("## What the night left in them")
    w("")
    w("Once the night was over, each person in the house was asked once what the day leaves in them. Each memory "
      "cites the records it is about; one that fails a check (reports/days_design.md, §2.6) never reaches a prompt.")
    w("")
    for pid in data.ORDER:
        r = mind.results.get(pid)
        if r is None:
            w(f"- **{NAME[pid]}**: away, not asked.")
            continue
        if r["mode"] == "fallback":
            w(f"- **{NAME[pid]}** ({r['prompt_tokens']} estimated tokens). **FALLBACK**: the answer could not be used "
              f"({r['invalid']}), so {NAME[pid]} carries nothing from this night.")
            continue
        feeling = r["feeling"] if r["feeling"] else f"({r['feeling_verdict']})"
        intent = quoted(r["intent"]) if r["intent"] else f"({r['intent_verdict']})"
        w(f"- **{NAME[pid]}** ({r['prompt_tokens']} estimated tokens). Feeling: *{feeling}*. Intent: {intent}")
        for m in r["memories"]:
            ids = m["ids"] if isinstance(m["ids"], list) else []
            w(f"  - {', '.join(str(i) for i in ids) or '(no ids)'}: {quoted(m['meaning'])} **{m['verdict']}**")
            for i in ids:
                e = mind.chron.event(i)
                if e is not None and e["views"].get(pid):
                    w(f"    - {i}: {e['views'][pid]}")
    w("")
    return "\n".join(out) + "\n"
