"""Leo's hour: the week played as Leo, with no model anywhere (Docs/fable-audit-2026-11.md, 7.5, "Leo's screen";
section 9, step 6).

    python hour.py --seed 2                     play the week as Leo; the others are the code brain's, at once
    python hour.py --resume runs/hour/seed2.json  go on with a week that stopped: its choices are replayed first
    python hour.py --seed 2 --script kind       let a script play Leo ("kind" or "cold"), and print the end page

A screen is the situation in a few lines, then at most seven choices. A choice is shown as the line Leo would say, or
as the thing he would do; "something else…" opens the rest, seven at a time. Nothing is typed but a number. The
choices are put in the order the code brain would weigh them for Leo: the brain orders, the player decides. "Say
nothing and wait" lets the house go on until something reaches Leo. When Leo is sick or hurt his body limits what
he is offered, and the screen says why. When someone does something to Leo because of what he did, the screen says so.

Every choice is saved as it is made (runs/hour/seed<N>.json): the same seed and the same choices give the same week,
so resuming is replaying. At the end: where each of the three stands with Leo, and the three things he did that put
them there; and the week's diary (runs/hour/seed<N>-diary.md).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import data                 # noqa: E402
import player as playermod  # noqa: E402
import week as weekmod      # noqa: E402

MAX = 7                     # choices on a screen, "something else…" included
NAMES = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
FLOOR = -0.3                # a move the brain weighs below this is not on the first page
# What a body that is sick or hurt (health.py, level 1) cannot do, and what one laid up (level 2) cannot.
HURT = ("task_boards", "task_water", "volunteer", "still_going", "propose", "collect_rain", "go_next_door",
        "go_further", "go_with_", "go_after", "watch_door")
LAID_UP = HURT + ("go_", "search", "keep_searching", "sit_", "aside_", "eat", "meal", "water_round", "door_", "task_",
                  "look_out")


class Quit(Exception):
    """The player stopped: the week can be resumed from its saved choices."""


class LogDiffers(Exception):
    """A saved choice is not among the choices the game offers at that point."""


def order(rows):
    """The choices in the order they are shown: the five the brain weighs most, then saying nothing, then the rest."""
    good = [r for r in rows if r["id"] != "silent" and r["open"] and r["score"] > FLOOR]
    rest = [r for r in rows if r["id"] != "silent" and r not in good]
    silent = [r for r in rows if r["id"] == "silent"]
    return good[:MAX - 2] + silent + good[MAX - 2:] + rest


def page_of(rows, page):
    """(the choices on this page, whether "something else…" follows them)."""
    if len(rows) <= MAX:
        return rows, False
    per = MAX - 1
    return rows[page * per:(page + 1) * per], True


def shown(r):
    if r["id"] == "silent":
        return "say nothing and wait"
    return f"“{r['words']}”  ({r['label']})" if r["words"] else r["label"]


def render(rows, page):
    items, more = page_of(rows, page)
    out = [f"  {n:2} {shown(r)}" for n, r in enumerate(items, 1)]
    if more:
        out.append(f"  {len(items) + 1:2} something else…")
    return "\n".join(out)


def compact(head, night):
    """The situation in a few lines: what reached Leo since his last choice without the comings and goings (the
    last ten lines of it), and of "Now" only where he is, who is there and what the shelf holds. A night's screen is
    left as it is: it is short, and all of it matters."""
    out, since, block, at = [], [], None, None
    for line in head.split("\n"):
        if line in ("Since you last chose:", "Now:", "What you know:"):
            block = line
            if line == "Since you last chose:":
                at = len(out)
            else:
                out.append(line)
            continue
        if line and not line.startswith(" "):
            block = None
        if block == "Since you last chose:":
            if not any(x in line for x in (" goes to the ", " comes into the ", "you went to the ")):
                since.append(line)
            continue
        if block == "Now:" and not night and not line.startswith(("  - ", "  Now,")):
            continue
        out.append(line)
    if since and at is not None:
        out[at:at] = ["Since you last chose:"] + since[-10:]
    return "\n".join(out)


class HourPlayer(playermod.Player):
    """Leo, played from a ranked screen. pick(screen, rows) gives the option id chosen. replay: saved choices, used
    first. save: a path the choices are written to as they are made."""

    def __init__(self, pick, replay=(), save=None, seed=None, pid="leo"):
        super().__init__(pid)
        self.pick, self.replay, self.save, self.seed = pick, list(replay), save, seed
        self.choices = []           # every choice, in order: option ids
        self.rows = []
        self.offered = None         # (options, turn, kind): set by the engine before each screen
        self.most = 0               # the most choices any screen showed
        self._read = {}             # house day -> how many of its turns have been read for "because of what you did"
        self._called = set()        # the moments Leo has been asked at: (day, the hour's business), (day, "door")
        self._seen = (0, 0, 0)      # (blows, trip positions, questions) as they stood when he was last asked
        self.asking = True

    # ---------- the screen ----------
    def limits(self, m, rows):
        """(the rows the body allows, the line that says why some are missing or None)."""
        health = getattr(m.brain(), "health", None)
        level = health.level(self.pid) if health is not None else 0
        if not level:
            return rows, None
        barred = LAID_UP if level >= 2 else HURT
        kept = [r for r in rows if not r["id"].startswith(barred)]
        if len(kept) == len(rows):
            return rows, None
        what = health.what(self.pid)
        return kept, (f"You are laid up ({what}): you can speak, eat and rest, nothing more." if level >= 2 else
                      f"Your body ({what}): no carrying, no climbing, no going out today.")

    def because(self, m):
        """What the others did to Leo since his last screen for a reason that names something he did."""
        turns = m.transcript["turns"]
        start = self._read.get(m.day, 0)
        self._read[m.day] = len(turns)
        me = NAMES[self.pid]
        out = []
        for turn in turns[start:]:
            for a in turn["acts"]:
                if a["who"] == self.pid or not a["option"].endswith("_" + self.pid):
                    continue
                for name, _ in (a.get("why") or {}).get("terms", []):
                    for part in name.split(", "):
                        if part.startswith(me + " "):
                            said = f": “{a['words']}”" if a.get("words") else ""
                            out.append(f"  {NAMES[a['who']]}{said} — because you {part[len(me) + 1:]}.")
        return list(dict.fromkeys(out))

    def calls(self, m, p, rows, kind, day):
        """Whether this moment calls on Leo: his share is in front of him, it is night, an hour's business begins
        (the meal, the work, the afternoon, the evening), someone has spoken to him, someone is at the door, news has
        come for the whole house, someone has said they will go out, or the can is asked about. Otherwise the house
        goes on and he is not asked: about sixty choices in a week, not one every three minutes."""
        if kind != "turn":
            return True
        brain = m.brain()
        now = (brain.blows, len(m.trip_acts), sum(1 for h in p.heard if h["kind"] in ("ask", "accuse")))
        beat = getattr(m, "beat", None)
        why = []
        if beat is not None and (day, beat) not in self._called:
            self._called.add((day, beat))
            why.append("hour")
        # Someone has opened something with him. An answer to what he said himself closes the exchange: it is on
        # his screen the next time he is asked, and does not call him again.
        who = (p.owed or p.addressed or {}).get("who")
        if who is not None and not brain.answered.get((who, p.id)):
            why.append("spoken to")
        if any(r["id"].startswith("door_") for r in rows) and (day, "door") not in self._called:
            self._called.add((day, "door"))
            why.append("door")
        if now != self._seen:
            why.append("news")
        self._seen = now
        return bool(why)

    def screen(self, m, p, view, kind, message=None):
        base = super().screen(m, p, view, kind, message)
        brain = m.brain()
        opts, t, _ = self.offered
        if view["minute"] is not None:
            rows = brain.rank(m, p, t, opts)
        else:               # at night: the few choices as they are, a spoken one with the words Leo would say
            rows = [{"id": o.id, "label": o.label, "speech": o.speech, "score": 0.0, "open": True, "key": o.id,
                     "words": brain.night_words(p, o.id, kind, view["day"], m.away) if o.speech else None}
                    for o in opts]
        rows, limit = self.limits(m, rows)
        self.asking = bool(message) or self.calls(m, p, rows, kind, view["day"])
        self.rows = order(rows) if view["minute"] is not None else rows
        self.most = max(self.most, len(page_of(self.rows, 0)[0]) + page_of(self.rows, 0)[1])
        head = compact(base.text.split("What you do:")[0].rstrip("\n"), view["minute"] is None)
        extra = ([limit] if limit else [])
        why = self.because(m) if view["minute"] is not None else []
        if why:
            extra += ["Because of what you did:"] + why
        text = "\n".join([head] + extra + ["What you do:", render(self.rows, 0)] + ([f"! {message}"] if message else []))
        return playermod.Screen(kind, base.day, base.minute, base.options, text, message, None)

    def decide(self, screen):
        if not self.asking:
            return playermod.WAIT       # nothing calls on him: the house goes on
        if self.replay:
            oid = self.replay.pop(0)
            if oid not in screen.options:
                raise LogDiffers(f"the saved choice {oid!r} is not offered: day {screen.day}, {screen.kind}")
        else:
            oid = self.pick(screen, self.rows)
        self.choices.append(oid)
        if self.save and not self.replay:
            with open(self.save, "w", encoding="utf-8", newline="\n") as f:
                json.dump({"seed": self.seed, "choices": self.choices}, f)
        row = next((r for r in self.rows if r["id"] == oid), None)
        words = row["words"] if row else None
        if oid == "silent":
            return playermod.WAIT if screen.kind == "turn" else (oid, None)
        return (oid, words)

    def chose(self, m, view, choice, opt):
        super().chose(m, view, choice, opt)
        m.brain().said_by_player(self.pid, view["day"], choice.get("say"))


# ---------- playing ----------
def play(seed, pick, replay=(), save=None, days=weekmod.DAYS, scenario=data.DEFAULT_SCENARIO):
    """(the week, the player). The same seed and the same choices give the same week."""
    p = HourPlayer(pick, replay, save, seed)
    return weekmod.run(seed, days, player=p, scenario=scenario), p


def end_page(w, pid="leo"):
    """Where each of the others stands with Leo at the end, and the three things he did that put them there."""
    h, day = w.brain.heart, len(w.days)
    away = w.days[-1].away
    me = NAMES[pid]
    out = ["── The week is over ──"]
    for q in data.ORDER:
        if q == pid:
            continue
        acts = sorted(h.acts.get((q, pid), ()), key=lambda a: (-abs(h.weight_now(a, day)), -a["day"]))[:3]
        t = h.trust(q, pid, day)
        stand = ("close to you" if t >= 2 else "warm to you" if t >= 1 else "wary of you" if t <= -1 and t > -2
                 else "cold to you" if t <= -2 else "as she was with you at the start" if q != "daniel"
                 else "as he was with you at the start")
        gone = ", who did not come back," if q in away else ""
        out.append(f"{NAMES[q]}{gone} is {stand}.")
        for a in acts:
            said = a["says"]
            said = "you " + said[len(me) + 1:] if said.startswith(me + " ") else said
            out.append(f"   day {a['day']}: {said}")
        if not acts:
            out.append("   Nothing you did stayed with " + data.PRONOUNS[q]["him"] + ".")
    return "\n".join(out)


# ---------- scripts, for the tests and for showing ----------
def script(prefer, days_for=None):
    """A Leo who does the first of `prefer` (prefixes of option ids) that is offered and that he has not done at that
    person today, and otherwise what the brain weighs most. days_for: {prefix: last day it is used}."""
    done = set()

    def pick(screen, rows):
        for pre in prefer:
            if days_for and screen.day > days_for.get(pre, 99):
                continue
            for r in rows:
                if r["id"].startswith(pre) and (screen.day, r["id"]) not in done:
                    done.add((screen.day, r["id"]))
                    return r["id"]
        return rows[0]["id"]
    return pick


SCRIPTS = {
    # gives up his share, looks after whoever is hurt, comforts, sits with people
    "kind": lambda: script(("plate_to_", "task_tend_", "reassure_", "sit_"), {"plate_to_": 2}),
    # accuses, has things out, eats from the shelf in front of the others
    "cold": lambda: script(("plate_eat", "accuse_", "confront_", "eat"), {"accuse_": 2}),
}


def toward(w, pid="leo", upto=3):
    """{person: {(what they did to Leo, the act of Leo's its record names)}} for the others' acts aimed at Leo on
    days 1 to upto. The day is left out of the reason: "Leo sat with her", not "today"."""
    me = NAMES[pid]
    out = {}
    for a in weekmod.acts(w.transcript()):
        if a["day"] > upto or a["who"] == pid or not a["option"].endswith("_" + pid):
            continue
        for name, _ in a["why"].get("terms", []):
            for part in name.split(", "):
                if part.startswith(me + " "):
                    out.setdefault(a["who"], set()).add((a["option"], part))
    return out


def leo_matters(seed, upto=3):
    """L9: the same seed, a kind Leo and a cold Leo. {person: [(the act only one of the two weeks has, in which week,
    the act of Leo's its record names)]}, for acts toward Leo by day `upto`."""
    got = {name: toward(play(seed, SCRIPTS[name]())[0], upto=upto) for name in ("kind", "cold")}
    out = {}
    for q in data.ORDER:
        for name, other in (("kind", "cold"), ("cold", "kind")):
            for option, named in sorted(got[name].get(q, set()) - got[other].get(q, set())):
                out.setdefault(q, []).append((option, name, named))
    return out


# ---------- the terminal ----------
def terminal(read=input, write=print):
    def pick(screen, rows):
        write(screen.text)
        page = 0
        while True:
            items, more = page_of(rows, page)
            answer = read("> ").strip().lower()
            if answer in ("q", "quit"):
                raise Quit()
            if answer.isdigit() and 1 <= int(answer) <= len(items) + more:
                n = int(answer)
                if more and n == len(items) + 1:
                    page = page + 1 if (page + 1) * (MAX - 1) < len(rows) else 0
                    write(render(rows, page))
                    continue
                return items[n - 1]["id"]
            write("Type the number of a choice, or q to stop (the week is saved).")
    return pick


def main(argv=None):
    ap = argparse.ArgumentParser(description="Play the week as Leo, with no model.")
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--resume", metavar="FILE", help="a saved week (runs/hour/seed<N>.json) to go on with")
    ap.add_argument("--script", choices=sorted(SCRIPTS), help="let a script play Leo instead of you")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):      # a Windows console: the screens use quotes and rules outside cp1252
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    out = os.path.join(HERE, "runs", "hour")
    os.makedirs(out, exist_ok=True)
    seed, replay = args.seed, []
    if args.resume:
        with open(args.resume, encoding="utf-8") as f:
            saved = json.load(f)
        seed, replay = saved["seed"], saved["choices"]
    save = os.path.join(out, f"seed{seed}.json")
    pick = SCRIPTS[args.script]() if args.script else terminal()
    try:
        w, p = play(seed, pick, replay, None if args.script else save)
    except Quit:
        print(f"Stopped. To go on: python hour.py --resume {os.path.relpath(save, HERE)}")
        return 3
    print(end_page(w))
    import diary
    path = os.path.join(out, f"seed{seed}-diary.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(diary.render(w))
    print(f"{len(p.choices)} choices. The week's diary: {os.path.relpath(path, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
