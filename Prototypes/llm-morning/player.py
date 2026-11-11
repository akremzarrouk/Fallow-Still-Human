"""The player (reports/play_design.md, §1 to §4.1 and §4.3; step S1): one person of the family, Leo by default, decided
by whoever plays them instead of by the model. The code still owns their body, knowledge, place and acts; the player
owns what they do and say.

The engine asks a Player through `decide(screen)` wherever it would have asked the model for that person (world.py:
Morning.decide, decide_aside, decide_given; night.py: Night.ask); their night mind is not asked (mind.py). A screen is
built only from that person's own lines (Morning.player_view, inside truth.prompting()), never from the World or from
anyone else's state. With no player (the default everywhere) nothing changes.

S1 plays days 1 and 2 and their nights (`play_days`). Quiet days, the terminal, the play log, the cap and resume are
S2 and S3.
"""
import data

WAIT = "w"                  # a standing order: carry on until something reaches you (§4.1)
WORDS_MAX = 240             # the model's "one or two short sentences" (§2.2)
SPEECH_NEEDS = "What do you say?"
SILENT_WORDS = "Staying silent means saying nothing"
UNKNOWN = "Choose one of the options"
NIGHT_WORDS = "At night only a (speech) option is said aloud"
CAN_STANCE = ("About the can (", "About the can: you have not settled")     # a stance the model's answers built (§1.3)
HEARD_CONFESSION = (" admitted taking the can: ", "(you heard it)")    # a sure line the heard line already shows


def tidy(words):
    """The player's words as the others will hear them: whitespace collapsed, at most WORDS_MAX characters, and a
    double quote turned into a single one, since every hearer's line puts the words in double quotes (§2.2)."""
    if words is None:
        return None
    words = " ".join(str(words).split()).replace('"', "'").strip()
    return words[:WORDS_MAX].rstrip() or None


def check(answer, opts, night=False):
    """(choice, None), or (None, what to tell the player); nothing happens until a choice is good. answer:
    (option id, words) or {"option", "say"}. The rules are the model's (world.Morning.parse), told instead of dropped."""
    if isinstance(answer, dict):
        option, words = answer.get("option"), answer.get("say")
    else:
        option, words = answer
    byid = {o.id: o for o in opts}
    opt = byid.get(option)
    if opt is None:
        return None, UNKNOWN
    words = tidy(words)
    if opt.speech and not words:
        return None, SPEECH_NEEDS
    if opt.id == "silent" and words:
        return None, SILENT_WORDS
    if night and words and not opt.speech:
        return None, NIGHT_WORDS
    return {"option": opt.id, "say": words}, None


class Screen:
    """What the player is shown before one decision: its kind ("turn", "aside", "given", "bedtime", "reaction",
    "answer"), the played day, the minute (None at night), the option ids, the text, and the message if the last answer
    could not be used. `view` is the person's own lines it was written from (world.Morning.player_view)."""

    def __init__(self, kind, day, minute, options, text, message, view):
        self.kind, self.day, self.minute, self.options = kind, day, minute, options
        self.text, self.message, self.view = text, message, view


class Player:
    def __init__(self, pid="leo"):
        self.pid = pid
        self.waiting = False        # the standing order "wait" (§4.1)
        self.screens = []
        self._marks = {}            # house day -> their line counts just after their last act
        self._shown = {}            # house day -> their line counts at their last screen
        self._know = None           # the "What you know" lines last shown
        self._card = False          # the card has been shown
        self._said = None           # (house day, minute, words) of their last act with words, to echo (S3)

    # ---------- what reached them ----------
    @staticmethod
    def counts(p):
        return len(p.memory), len(p.sure), len(p.beliefs)

    def mark(self, m, p):
        """Their act this turn is done: what reaches them from now on is new for "wait"."""
        self._marks[m.day] = self.counts(p)

    def reached(self, m, p):
        """A line has been added to their memory or sure lines, or a belief given, since their last act."""
        mark = self._marks.get(m.day)
        return mark is None or self.counts(p) != mark

    def chose(self, m, view, choice, opt):
        """Their answer was taken (world.Morning.player_choice): its words are echoed with their act on the next
        screen (reports/play_s3.md); speech as to whom it was said (reports/play_fix1.md, fix 1)."""
        from talk import act_of, aimed_at
        if not choice.get("say") or view["minute"] is None:
            self._said = None
            return
        to = None
        if opt.speech:
            aim = aimed_at(opt.id)
            to = m.spoken_to(m.people[self.pid], act_of(opt.id)[0], m.people[aim] if aim else None, None,
                             opt.act.get("listeners"))
        self._said = (m.day, view["minute"], choice["say"], to)

    # ---------- the screen ----------
    def screen(self, m, p, view, kind, message=None):
        """The screen for one decision, from `view`: the header, the card (the first screen only), the body, what is
        new since their last screen (the day's carry-in on its first screen), what they know when it changed, Now,
        and the options."""
        k, minute = view["day"], view["minute"]
        if minute is None:
            header = f"Night {k} · {kind}"
        else:
            header = f"Day {k} · {data.minute_words(minute)} · the {data.ROOMS[view['room']]}"
        lines = [f"── {header} ──"]
        if not self._card:
            self._card = True
            s = p.sheet
            calls = "; ".join(f"{data.PEOPLE[q]['name']} \"{w}\"" for q, w in data.ADDRESS[p.id].items())
            lines += [f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; Daniel, 25; "
                      f"Leo, 21; Mara, 17).", f"How you address them: {calls}.", f"Who you are: {s['note']}",
                      f"What matters to you: {', '.join(s['values'])}.", "What you remember from the days before:"]
            lines += [f"  - {x}" for x in view["backstory"]]
        lines += view["body"]
        first = m.day not in self._shown
        i, j, b = self._shown.get(m.day, (0, 0, 0))
        # A minute's lines in the order they happened (reports/play_fix1.md, fix 4): a sure line goes after the memory
        # lines that came before it, so day 1's count comes first; a heard confession's sure line is left out, as its
        # heard line shows it. Beliefs come first at their minute.
        after = view.get("sure_after") or [0] * len(view["sure"])
        new = []
        for n in range(j, len(view["sure"])):
            mm, x = data.unstamp(view["sure"][n])
            if not (HEARD_CONFESSION[0] in x and x.endswith(HEARD_CONFESSION[1])):
                new.append(((mm, after[n], 0), mm, x))
        new += [((x["minute"], -1, 0), x["minute"], x["claim"]) for x in view["beliefs"][b:]]
        mine = [((mm, n, 1), mm, x) for n, (mm, x) in enumerate(view["memory"][i:], i)]
        if self._said and self._said[0] == m.day:       # their own act's line, with the words they typed
            n = next((n for n, (_, mm, x) in enumerate(mine) if mm == self._said[1] and x.startswith("you ")), None)
            if n is not None:
                key, mm, x = mine[n]
                said, words, to = x.rstrip("."), self._said[2], self._said[3]
                mine[n] = (key, mm, f'you, {to}: "{words}"' if to else f'{said}: "{words}"' if said == "you said"
                           else f'{said}, saying: "{words}"')
            self._said = None
        new += mine
        new.sort(key=lambda x: (-1 if x[1] is None else x[1],) + x[0][1:])
        new = [(mm, x) for _, mm, x in new]
        out = ([f"  {x}" for x in view["carry"]] if first else []) + \
              [f"  {data.clock(mm) if mm is not None else '':6}  {x}".rstrip() for mm, x in new]
        if out:
            lines += ["Since you last chose:"] + out
        self._shown[m.day] = (len(view["memory"]), len(view["sure"]), len(view["beliefs"]))
        if view["know"] != self._know:
            self._know = list(view["know"])
            if view["know"]:
                lines += ["What you know:"] + [f"  - {x}" for x in view["know"]]
        lines += ["Now:"] + [f"  {x}" for x in view["now"]]
        lines += ["What you do:"] + [f"  {n:2} {label}" + ("  (say it)" if speech else "")
                                     for n, (_, label, speech) in enumerate(view["options"], 1)]
        if message:
            lines.append(f"! {message}")
        return Screen(kind, k, minute, [o for o, _, _ in view["options"]], "\n".join(lines), message, view)

    def decide(self, screen):
        """(option id, words), or WAIT on a turn. Overridden by every kind of player."""
        raise NotImplementedError


class ScriptedPlayer(Player):
    """For tests: rule(screen) gives each answer."""

    def __init__(self, rule, pid="leo"):
        super().__init__(pid)
        self.rule = rule

    def decide(self, screen):
        self.screens.append(screen)
        answer = self.rule(screen)
        # A share of the meal set in front of them (code mode) is eaten unless the script says what else to do with
        # it: a script written for turns answers nothing that a share can take.
        if screen.kind == "plate" and (answer == WAIT or answer[0] not in screen.options):
            return (screen.options[0], None)
        return answer


def by_minute(table, default=WAIT, night="sleep"):
    """A rule: on a turn, table[(day, minute)] or table[minute] (day 1), else `default`; at night, `night` (an
    option id) for bedtime and the first option for anything else."""
    def rule(screen):
        if screen.minute is None:
            return (night, None) if screen.kind == "bedtime" else (screen.options[0], None)
        got = table.get((screen.day, screen.minute), table.get(screen.minute) if screen.day == 1 else None)
        return default if got is None else got
    return rule


def play_days(oracle, seed, player, scenario=data.DEFAULT_SCENARIO, days=2, log=None, on_scene=None):
    """Days 1 to `days` (1 or 2), each with its night and night mind, in morning.run's order, with `player` playing
    their person. Nothing is printed: what morning.run would say goes to `log` (a list, or a function of one line), if
    given. on_scene(name, scene), if given, is called as each day, night and night mind ends ("day1", "night1",
    "mind1", ...). Returns the scenes and the chronicle."""
    from chronicle import Chronicle
    from mind import NightMind
    from night import Night
    from world import Morning
    put = (lambda x: None) if log is None else log if callable(log) else log.append
    say = (lambda *a: put(" ".join(str(x) for x in a)))
    seen = on_scene or (lambda name, scene: None)
    chron = Chronicle(seed, data.culprit(scenario))
    out = {"chronicle": chron}
    m = Morning(oracle, seed, scenario)
    m.player = player
    for k in range(1, days + 1):
        if k > 1:
            oracle.new_scene()
            m = Morning.next_day(m, n, oracle, chronicle=chron)
            m.player = player
        m.run()
        chron.add_day(m)
        say(f"day {k}: so far {oracle.live} live, {oracle.from_cache} cached")
        seen(f"day{k}", m)
        oracle.new_scene()
        n = Night(m, oracle, number=k, house=chron.house_state()).run()
        chron.add_night(n)
        seen(f"night{k}", n)
        oracle.new_scene()
        mind = NightMind(n, chron, oracle).run()
        say(f"night {k}: {len(n.decisions)} decisions; mind {len(mind.results)}")
        seen(f"mind{k}", mind)
        out.update({f"day{k}": m, f"night{k}": n, f"mind{k}": mind})
    return out
