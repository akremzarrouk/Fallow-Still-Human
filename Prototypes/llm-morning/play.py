"""Play Leo in a terminal (reports/play_design.md, §6.1 and §8; step S3, for days 1 and 2): Elena, Daniel and Mara are
the model's, as in every run; Leo is yours.

    python play.py --seed 2                    a new session; the others' answers come from Gemini (GEMINI_API_KEY)
    python play.py --seed 2 --fake             the same against the fake model: no API call
    python play.py --resume runs/play/<name>   go on with a session that stopped: its choices are replayed from its
                                               log, the others' answers from the cache, then play goes on live

    --days 1|2         the last day to play (default 2); each day is followed by its night
    --scenario NAME    daniel_ate_it (default), or another of data.SCENARIOS
    --model KEY        another model from config.json `models`
    --max-requests N   stop the session once it has sent N API requests (default: config.json `play_max_requests`)

Each session has a folder runs/play/<scenario>-seed<N>-<UTC time>/ holding play.jsonl (every screen, every choice and
every act of the others, in order), shown.md (only what you were shown and what you typed) and session.log; the
answers go to cache/play/. play.jsonl holds what you were not shown too: read shown.md while you play.

Exit codes: 0 done; 3 stopped part way (the session's requests, the daily quota, a rate limit, or you stopped it), and
it can be resumed; 1 the log and the game differ on resume.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import types

import data
import player as playermod
from gemini import Cache, FakeClient, GeminiClient, Oracle, SessionCapReached, StopMorning, load_config
from world import day_index

HERE = os.path.dirname(os.path.abspath(__file__))
HELP = """How to play
  Type the number of an option to do it.          5
  Type words after the number to say them too.    5 You were up last night, Daniel.
  Type words alone to say something else.         I heard the shelf in the night.
  An option marked (say it) needs words; if you give none you are asked for them.
  w   wait: carry on as you are until something reaches you (on a turn only)
  l   look: everything you remember and know
  h   this help
  q   save and stop; go on later with  python play.py --resume <the session folder>"""
WAIT_HINT = "w wait · l look · h help · q save and stop"
HINT = "l look · h help · q save and stop"


class Quit(StopMorning):
    """The player stopped the session (q, or the end of their input)."""


class LogDiffers(StopMorning):
    """On resume, a replayed screen is not the one the log holds."""


class Capped:
    """A client that sends no request once `limit` have been sent, retries included (reports/play_design.md, §5.3).
    A GeminiClient also checks it before each retry."""

    def __init__(self, client, limit):
        self.client, self.limit = client, limit
        if hasattr(client, "stop_at"):
            client.stop_at = limit

    @property
    def requests(self):
        return self.client.requests

    @property
    def last_prompt_tokens(self):
        return getattr(self.client, "last_prompt_tokens", None)

    def new_scene(self):
        if hasattr(self.client, "new_scene"):
            self.client.new_scene()

    def generate(self, system, prompt, schema=None):
        if self.client.requests >= self.limit:
            raise SessionCapReached(f"stopped: this session's {self.limit} requests are spent.")
        return (self.client.generate(system, prompt) if schema is None
                else self.client.generate(system, prompt, schema=schema))


# ---------- the log (§8) ----------
class PlayLog:
    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def _append(self, name, text):
        with open(os.path.join(self.folder, name), "a", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def write(self, rec):
        self._append("play.jsonl", json.dumps(rec, ensure_ascii=False) + "\n")

    def say(self, line):
        self._append("session.log", line.rstrip("\n") + "\n")

    def shown(self, text):
        self._append("shown.md", text.rstrip("\n") + "\n")


def read_log(folder):
    """(the session's first start record, {screen n: text}, the choices in order of n, what of the others is logged
    already: {"acts": {house day: turns}, "scenes": [names]}) from play.jsonl."""
    start, screens, choices, done = None, {}, {}, {"acts": {}, "scenes": []}
    with open(os.path.join(folder, "play.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["t"] == "start" and start is None:
                start = r
            elif r["t"] == "screen":
                screens[r["n"]] = r["text"]
            elif r["t"] == "choice":
                choices[r["n"]] = r
            elif r["t"] == "session":
                for day, turns in r.get("acts_done", {}).items():
                    done["acts"][int(day)] = max(done["acts"].get(int(day), 0), turns)
                done["scenes"] += [x for x in r.get("scenes_done", []) if x not in done["scenes"]]
    return start, screens, [choices[n] for n in sorted(choices)], done


def answer_of(rec):
    return playermod.WAIT if rec["option"] == playermod.WAIT else (rec["option"], rec.get("say"))


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SessionPlayer(playermod.Player):
    """The player of a session: replays the logged choices first, each against its logged screen, then asks `live`
    (live(screen) -> (answer, the lines typed, seconds)); logs every screen and choice, and every act of the others."""

    def __init__(self, log, live, replay=(), logged=None, write=print, pid="leo", done=None):
        super().__init__(pid)
        self.log, self.live, self.write = log, live, write
        self.queue, self.logged = list(replay), dict(logged or {})
        self.n = 0
        self.replay_end = None      # {"n", "live"} at the last replayed screen: what was live by then
        # What of the others is in the log already (from earlier parts, on resume): house day -> how many of its played
        # turns' acts; the days, nights and night minds whose records are written.
        self.acts_done = dict((done or {}).get("acts", {}))
        self.scenes_done = list((done or {}).get("scenes", []))
        self.m = None

    def screen(self, m, p, view, kind, message=None):
        self.m = m
        self.acts(m)
        return super().screen(m, p, view, kind, message)

    def decide(self, screen):
        self.n += 1
        self.screens.append(screen)
        if self.queue:
            if self.logged.get(self.n) != screen.text:
                raise LogDiffers(f"stopped: the log and the game differ at screen {self.n}.")
            rec = self.queue.pop(0)
            if not self.queue:
                self.replay_end = {"n": self.n, "live": self.m.oracle.live}
                self.write(f"(replayed {self.n} screens from the log, {self.m.oracle.live} live asks; "
                           f"from here you play)")
            return answer_of(rec)
        if self.n not in self.logged:
            self.log.write({"t": "screen", "n": self.n, "day": screen.day, "minute": screen.minute,
                            "kind": screen.kind, "text": screen.text, "options": screen.options})
            self.log.shown("\n" + screen.text)
        answer, typed, seconds = self.live(screen)
        option, say = (answer, None) if answer == playermod.WAIT else answer
        self.log.write({"t": "choice", "n": self.n, "option": option, "say": say, "input": typed, "seconds": seconds})
        self.log.shown("".join(f"> {x}\n" for x in typed))
        return answer

    # ---------- what the others did, in the full log ----------
    def acts(self, m):
        """Every act of the others in the turns played so far today that is not yet in the log, with whether a line
        of it reached the player's person: "saw" (their words or the act), "voices", or None."""
        turns = m.transcript["turns"]
        done = self.acts_done.get(m.day, 0)
        if done >= len(turns):
            return
        decided = {d["seq"]: d for rec in m.log for d in rec["decisions"] if "seq" in d}
        for turn in turns[done:]:
            for a in turn["acts"]:
                if a["who"] == self.pid or (a["mode"] == "routine" and a["option"] == "silent"):
                    continue
                seq = a["decided_at"][1]
                d = decided.get(seq, {})
                seen = ("saw" if self.pid in m.views.get(seq, {}) else
                        "voices" if self.pid in m.voices_heard.get(seq, {}) else None)
                self.log.write({"t": "act", "day": day_index(m.day), "minute": a["minute"], "who": a["who"],
                                "room": a["room"], "option": a["option"], "words": a["words"], "mode": a["mode"],
                                "feeling": d.get("feeling"), "reason": d.get("reason"), "seen_by_leo": seen})
        self.acts_done[m.day] = len(turns)

    def scene(self, name, scene):
        """A day, night or night mind has ended (player.play_days, on_scene)."""
        if name in self.scenes_done:
            return
        self.scenes_done.append(name)
        if name.startswith("day"):
            self.acts(scene)
        elif name.startswith("night"):
            k = int(name[len("night"):])
            for d in scene.decisions:
                if d["person"] != self.pid:
                    self.log.write({"t": "night", "night": k, "who": d["person"], "ask": d["ask"],
                                    "option": d["option"], "words": d.get("say"), "mode": d["mode"],
                                    "feeling": d.get("feeling"), "reason": d.get("reason")})
            for e in scene.events:
                self.log.write({"t": "night_event", "night": k, "kind": e["kind"], "actor": e["actor"],
                                "witnesses": e["witnesses"], "outcome": e.get("outcome")})
        else:
            k = int(name[len("mind"):])
            for pid, r in scene.results.items():
                self.log.write({"t": "mind", "night": k, "who": pid, "feeling": r.get("feeling"),
                                "intent": r.get("intent"),
                                "memories": [x.get("meaning") for x in r.get("memories", [])]})


# ---------- the terminal (§6.1) ----------
def look(view):
    """`l`: everything they remember and know, untrimmed."""
    out = ["What you remember from the days before:"] + [f"  - {x}" for x in view["backstory"]]
    if view["carry"]:
        out += ["What you carried into today:"] + [f"  {x}" for x in view["carry"]]
    out += ["What you are sure of today:"] + [f"  - {x}" for x in view["sure"]]
    out += [f"  - {data.clock(b['minute'])}: {b['claim']}" for b in view["beliefs"]]
    out += ["What else happened today:"] + ([f"  {data.clock(mm):6}  {x}" for mm, x in view["memory"]] or
                                            ["  nothing yet"])
    if view["know"]:
        out += ["What you know:"] + [f"  - {x}" for x in view["know"]]
    return "\n".join(out)


def terminal(read=input, write=print):
    """The live player of a terminal: shows a screen and reads one answer, with §2.2's checks on the spot (nothing
    happens until an answer can be used)."""
    def live(screen):
        write("")
        write(screen.text)
        write(WAIT_HINT if screen.kind == "turn" else HINT)
        opts = [types.SimpleNamespace(id=o, speech=s) for o, _, s in screen.view["options"]]
        ids = [o.id for o in opts]
        night = screen.minute is None
        typed, start = [], time.monotonic()

        def ask(prompt):
            try:
                line = read(prompt)
            except (EOFError, KeyboardInterrupt):
                raise Quit("stopped: you chose to stop.")
            typed.append(line.strip())
            return line.strip()
        while True:
            line = ask("> ")
            if not line:
                continue
            low = line.lower()
            if low == "q":
                raise Quit("stopped: you chose to stop.")
            if low == "h":
                write(HELP)
                continue
            if low == "l":
                write(look(screen.view))
                continue
            if low == "w":
                if screen.kind == "turn":
                    return playermod.WAIT, typed, round(time.monotonic() - start, 1)
                write("! There is nothing to wait for here: choose one of the options by its number.")
                continue
            m = re.match(r"(\d+)\s*(.*)$", line)
            if m:
                n = int(m.group(1))
                if not 1 <= n <= len(opts):
                    write(f"! Choose a number from 1 to {len(opts)}.")
                    continue
                option, words = ids[n - 1], m.group(2) or None
            elif "say_other" in ids:
                option, words = "say_other", line
            else:
                write("! Choose one of the options by its number.")
                continue
            choice, why = playermod.check((option, words), opts, night=night)
            if why == playermod.SPEECH_NEEDS:
                words = ask(f"{playermod.SPEECH_NEEDS} ")
                choice, why = playermod.check((option, words), opts, night=night)
            if why:
                write(f"! {why}")
                continue
            write("…")
            return (choice["option"], choice["say"]), typed, round(time.monotonic() - start, 1)
    return live


# ---------- a session ----------
def session(seed=None, days=2, scenario=data.DEFAULT_SCENARIO, fake=False, model_key=None, root=HERE, resume=None,
            client=None, live=None, read=input, write=print, max_requests=None, config_path=None):
    """One session, new or resumed. Returns (exit code, its folder, {"player", "oracle", "stopped"}). client: for tests
    (otherwise the fake or Gemini, by `fake`); live: the live player (otherwise the terminal's, on read and write)."""
    config = load_config(config_path or os.path.join(HERE, "config.json"))
    replay, logged, done = [], {}, None
    if resume:
        folder = resume
        start, logged, replay, done = read_log(folder)
        seed, days, scenario, fake, model_key = (start["seed"], start["days"], start["scenario"], start["fake"],
                                                 start["model_key"])
    if model_key:
        config = {**config, **config["models"][model_key]}
    model_name = "fake" if fake else config["model"]
    if not resume:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        folder = os.path.join(root, "runs", "play", f"{scenario}-seed{seed}-{stamp}")
        n = 1
        while os.path.exists(folder):
            n += 1
            folder = os.path.join(root, "runs", "play", f"{scenario}-seed{seed}-{stamp}-{n}")
        start = {"cache": os.path.join(root, "cache", "play", f"{model_name}-{scenario}-seed{seed}.json")}
    cache_path = start["cache"]
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    limit = max_requests or config.get("play_max_requests", 250)
    if client is None:
        client = (FakeClient(max_calls=config["max_calls_per_morning"]) if fake else GeminiClient(config, seed))
    oracle = Oracle(Cache(cache_path), model_name, seed, client=Capped(client, limit),
                    max_calls=config["max_calls_per_morning"])
    log = PlayLog(folder)
    parts = 0
    if resume:
        with open(os.path.join(folder, "play.jsonl"), encoding="utf-8") as f:
            parts = sum(1 for line in f if json.loads(line)["t"] == "start")
    started = utc()
    log.write({"t": "start", "part": parts + 1, "utc": started, "seed": seed, "days": days, "scenario": scenario,
               "fake": fake, "model_key": model_key, "model": model_name, "cache": cache_path,
               "max_requests": limit, "replay": len(replay)})
    log.shown(f"\n# Session part {parts + 1}, {started}: seed {seed}, {scenario}, days 1 to {days}, model {model_name}"
              + (f" (resumed: {len(replay)} choices replayed)" if resume else ""))
    log.say(f"{started} part {parts + 1}: seed {seed}, {scenario}, days {days}, model {model_name}, "
            f"at most {limit} requests, cache {cache_path}")
    sp = SessionPlayer(log, live or terminal(read, write), replay, logged, write, done=done)
    if resume:
        write(f"Resuming {folder}: replaying {len(replay)} choices…")
    code, stopped = 0, None
    try:
        playermod.play_days(oracle, seed, sp, scenario, days=days, log=log.say, on_scene=sp.scene)
    except (StopMorning, KeyboardInterrupt) as stop:      # Ctrl-C while the others answer: as q
        stopped = str(stop) if isinstance(stop, StopMorning) else "stopped: you chose to stop."
        code = 1 if isinstance(stop, LogDiffers) else 3
        if sp.m is not None:
            sp.acts(sp.m)
    log.write({"t": "session", "part": parts + 1, "start": started, "end": utc(), "asks_live": oracle.live,
               "asks_cached": oracle.from_cache, "api_requests": oracle.api_requests, "stopped": stopped,
               "acts_done": sp.acts_done, "scenes_done": sp.scenes_done})
    log.say(f"{utc()} part {parts + 1} ended: {stopped or 'done'}; {oracle.live} live, {oracle.from_cache} cached, "
            f"{oracle.api_requests} API requests")
    if stopped:
        write(f"\n{stopped}")
        if code == 3:
            write(f"The session is saved in {folder}.")
            write(f"To go on: python play.py --resume {folder}")
            if not fake:
                write("(The free daily quota resets at midnight Pacific time.)")
    else:
        write(f"\nThe session is over: days 1 to {days} played. Its log is in {folder}.")
    return code, folder, {"player": sp, "oracle": oracle, "stopped": stopped}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--days", type=int, default=2, choices=(1, 2))
    ap.add_argument("--fake", action="store_true", help="the fake model; no API call")
    ap.add_argument("--resume", default=None, help="a session folder to go on with")
    ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
    ap.add_argument("--model", default=None, help="a key of config.json `models`")
    ap.add_argument("--max-requests", type=int, default=None)
    ap.add_argument("--root", default=HERE, help=argparse.SUPPRESS)        # where runs/ and cache/ are (tests)
    args = ap.parse_args()
    if args.resume is None and args.seed is None:
        ap.error("--seed is needed for a new session")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    code, _, _ = session(args.seed, args.days, args.scenario, args.fake, args.model, args.root,
                         args.resume and os.path.abspath(args.resume), max_requests=args.max_requests,
                         write=lambda *a: print(*a, flush=True))
    sys.exit(code)


if __name__ == "__main__":
    main()
