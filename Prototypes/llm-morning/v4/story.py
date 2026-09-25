"""Writes a finished morning as a story, in the style of Tools/narrate-morning.

Everything here comes from the morning's own record, so the same answers always give
the same bytes: no clock, no call counts, no run time.
"""
import data
from world import (FALL_EVERY, FEELING_SHOWS_FOR_TURNS, INNER_EVERY, KIND_DONE, QUIET_TURNS,
                   grudge_facts, hunger_words, trait_words)

DAYS_KNOWN = {"did": "did it", "saw": "saw it", "heard": "heard it"}
ORDINAL = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}


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
            d = next(x for x in rec["decisions"] if x["person"] == pid)
            sig = (d["label"], d["came_of_it"]) if d["mode"] == "routine" else None
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
    if d.get("inner"):
        because = "**Inner moment**, nothing social happening: " + "; ".join(d["inner"])
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

    w(f"# The morning as a story: daniel_ate_it, rules and a language model, seed {seed}")
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
      "(0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as "
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
    w("- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he "
      "did in his hearing (by anyone, himself included), or when someone reassures him "
      "personally. His denials, and reassurance of everyone, add nothing. It never falls, and it "
      "never decides anything: the model still chooses.")
    w(f"- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has "
      f"risen a level since they last decided with the model; the model is asked, at most once "
      f"every {INNER_EVERY} minutes per person. What rose is listed.")
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
    rows = [
        ("Age", lambda p: str(p["age"])),
        ("Role in the family", lambda p: p["role_short"]),
        ("Where, how hungry", lambda p: f"kitchen, hunger {p['hunger']:.2f} ({hunger_words(p['hunger'])})"),
        ("Temperament", lambda p: trait_words(p["traits"])),
        ("What matters to them", lambda p: ", ".join(p["values"])),
        ("Knows about the can", lambda p: "ate it in the night; nobody saw" if p is data.PEOPLE[data.CULPRIT]
         else "only that it is missing"),
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
    for day, text, who in data.BACKSTORY:
        w(f"| {day} | {text} | " + " | ".join(DAYS_KNOWN.get(who.get(p), "not there") for p in data.ORDER) + " |")
    w(f"| 4 | {data.OPENING} | " + " | ".join("did it" if p == "elena" else "saw it" for p in data.ORDER) + " |")
    w("")

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
        lines += [f"- *Daniel's guilt, now {level} of 3: {why}.*" for _, level, why in rec["guilt"]]
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
    eaten = [f"{q.name} {q.eaten:g}" for q in morning.people.values() if q.eaten]
    w(f"At minute {data.MINUTES}: {'; '.join(where)}. {morning.portions} of {data.PORTIONS} portions "
      f"left; eaten this morning: {', '.join(eaten) if eaten else 'none'}.")
    w("")
    confessed = [d for d in all_d if d["option"] == "confess" and d["mode"] == "model"]
    w("- Who admitted taking it: " + (", ".join(f"{data.PEOPLE[d['person']]['name']} at minute "
                                                 f"{d['minute']:02d}" for d in confessed) or "nobody") + ".")
    acc = [f"{data.PEOPLE[d['person']]['name']} accused {data.PEOPLE[d['option'][7:]]['name']} "
           f"(minute {d['minute']:02d})" for d in all_d if d["option"].startswith("accuse_")]
    w("- Accusations: " + ("; ".join(acc) if acc else "none") + ".")
    knowers = [q.name for q in morning.people.values() if q.knows_culprit == data.CULPRIT and q.id != data.CULPRIT]
    w("- Who else knows Daniel took it: " + (", ".join(knowers) if knowers else "nobody") + ".")
    talk = [f"{data.ROOMS[r]} {what} at minute {m:02d} ({why})" for m, r, what, why in morning.convos.log]
    w("- Conversations: " + "; ".join(talk) + ".")
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
    w("The events behind each grudge still held at minute 90, and behind Daniel's guilt:")
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
    daniel = morning.people[data.CULPRIT]
    facts = "; ".join(fact for m, fact in daniel.guilt_events) or "nothing since"
    w(f"- Daniel's guilt ({daniel.guilt}/3): he ate the can in the night, and nobody saw; {facts}.")
    w("")
    last = []
    for pid in data.ORDER:
        mine = [d for d in all_d if d["person"] == pid and d["mode"] == "model"]
        name = data.PEOPLE[pid]["name"]
        last.append(f"{name} *{mine[-1]['feeling']}* (minute {mine[-1]['minute']:02d})" if mine
                    else f"{name}: never asked")
    w("- The last feeling each of them named: " + "; ".join(last) + ".")
    w("")
    return "\n".join(out)
