"""The calm variants probe (reports/calm_variants_plan.md): which prompt change, if any, lets people tell Daniel about
the visit in a quiet moment?

reports/calm_probe.md: 0 of 14 tells. Each person's 10:00 and 10:30 prompts differed only in their "Now" line and
ended on the 09:48 quarrel, and tell_daniel_visit sat 18th or 19th of 27 or 28 options.

From runs/calm_probe/probe.py: the same replay (scenes 1 and 3 of the talk probe, from a copy of
cache/talk_probe/scene<k>.json, 0 live asks), the same 18 calm prompts (10:00, 10:30, 11:00; each awake person in
Daniel's room who knows the visit first-hand) and the same client seeds (201 scene 1, 202 scene 3). Each calm prompt
is rebuilt as calm_probe built it (World.prompt_for with World.options_for), checked equal to the prompt calm_probe
recorded, and asked in three variants, changed here only:
- T: one line added right before the "Now" line, built from the replay's state: when anyone in that room last spoke,
  how many minutes ago, and that everyone there has stayed sitting there since. Checked true before it is used.
- O: the topic options (talk_*, tell_*) moved to the top of the option list; nothing else changed.
- TO: both (the T line added to the O prompt).
No prompt is asked twice: where a person was offered no topic option, the O prompt is calm_probe's own prompt (its
answer, same client seed, is taken from runs/calm_probe/scene<k>.json) and the TO prompt is the T prompt (T's answer).
Answers are recorded and never applied. No live ask past CAP (60) in all. The key is read from GEMINI_API_KEY only.

    python runs/calm_variants/probe.py --fake     a temp folder and the fake model; writes nothing in the repository
    python runs/calm_variants/probe.py --live     cache/calm_variants/, runs/calm_variants/; asks Gemini
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import data                                             # noqa: E402
import quiet                                            # noqa: E402
import world                                            # noqa: E402
from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config   # noqa: E402
from talk import SPEECH, act_of                         # noqa: E402

CAP = 60
MINUTES = (180, 210, 240)                               # 10:00, 10:30, 11:00
SEEDS = {1: 201, 3: 202}                                # the calm asks' client seed, per scene (calm_probe's)
SOURCE = os.path.join("cache", "talk_probe")            # scene<k>.json: the talk probe's caches
BASELINE = os.path.join("runs", "calm_probe")           # scene<k>.json: calm_probe's 18 asks and answers
VARIANTS = ("T", "O", "TO")
TOPIC = ("talk_", "tell_")
clock = quiet.clock

_spec = importlib.util.spec_from_file_location("talk_probe_probe", os.path.join("runs", "talk_probe", "probe.py"))
talk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(talk)


class Stop(Exception):
    pass


class Done(Exception):
    pass


class NoLive:
    """The replay's client: nothing may be asked of it."""
    requests, allow, last_prompt_tokens = 0, True, None

    def generate(self, system, prompt, schema=None):
        raise Stop("a replayed ask missed the talk probe's cache")


class Capped:
    """The variants' client: no live answer past CAP in all."""

    def __init__(self, inner, ledger):
        self.inner, self.ledger = inner, ledger

    @property
    def requests(self):
        return self.inner.requests

    @property
    def last_prompt_tokens(self):
        return getattr(self.inner, "last_prompt_tokens", None)

    def generate(self, system, prompt, schema=None):
        if self.ledger["live"] >= CAP:
            raise Stop(f"the cap of {CAP} live asks is reached")
        text = self.inner.generate(system, prompt)
        self.ledger["live"] += 1
        return text


def answer_fields(text):
    try:
        a = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip()))
    except ValueError:
        return {"raw": text}
    return a if isinstance(a, dict) else {"raw": text}


def spoke(act):
    """An act in which someone spoke: a speech option, or any words said."""
    return act_of(act["option"])[0] in SPEECH or bool(act.get("words"))


def quiet_line(m, p, minute, seen):
    """The T line for p at `minute`, and the checks that make it true. seen: (minute, {person: (room, activity
    label, resting)}) recorded at every quiet step and jump of the replay."""
    room = p.room
    acts = [a for turn in m.transcript["turns"] for a in turn["acts"]]
    said = [a for a in acts if a["room"] == room and a["minute"] <= minute and spoke(a)]
    last = max(a["minute"] for a in said)
    here = [q for q in m.people.values() if q.room == room]
    since = [(mm, snap) for mm, snap in seen if last < mm <= minute]
    checks = {
        "last_spoke": clock(last),
        "last_speakers": sorted({a["who"] for a in said if a["minute"] == last}),
        "spoke_after": [(clock(a["minute"]), a["who"], a["option"]) for a in acts
                        if a["minute"] > last and spoke(a)],
        "acts_after": [(clock(a["minute"]), a["who"], a["option"]) for a in acts if a["minute"] > last],
        "here": sorted(q.id for q in here),
        "in_room_at_last": sorted(a["who"] for a in acts if a["minute"] == last and a["room"] == room),
        "snapshots_since": len(since),
        "all_stayed": all(snap[q.id][0] == room and not snap[q.id][2] for _, snap in since for q in here),
        "sitting_now": {q.id: q.activity["label"] for q in here},
    }
    checks["true"] = (not checks["spoke_after"] and not checks["acts_after"] and checks["all_stayed"]
                      and len(since) > 0 and set(checks["here"]) <= set(checks["in_room_at_last"])
                      and all(lab == f"sitting in the {data.ROOMS[room]}" for lab in checks["sitting_now"].values()))
    line = (f"Nobody in the {data.ROOMS[room]} has said anything since {clock(last)}, {minute - last} minutes ago; "
            f"you have all stayed sitting here.")
    return line, checks


def with_line(prompt, line):
    lines = prompt.split("\n")
    now = [i for i, x in enumerate(lines) if x.startswith("Now, ")]
    assert len(now) == 1, now
    return "\n".join(lines[:now[0]] + [line] + lines[now[0]:])


def option_block(prompt):
    lines = prompt.split("\n")
    i = lines.index("Your options:")
    j = i + 1
    while j < len(lines) and lines[j].startswith("- "):
        j += 1
    return lines[:i + 1], lines[i + 1:j], lines[j:]


def calm_asks(m, minute, calm, out, seen, baseline):
    """At `minute`: each awake person in Daniel's room who knows the visit first-hand, asked in T, O and TO."""
    q = m.quiet
    dan = m.people["daniel"]
    here = [p for p in m.people.values() if p.room == dan.room and p.id != "daniel"]
    moment = {"minute": minute, "clock": clock(minute), "daniel_room": dan.room,
              "daniel_resting": q.resting("daniel"), "daniel_beliefs": len(dan.beliefs),
              "here": {p.id: {"resting": q.resting(p.id),
                              "first_hand": any(t["first"] for t in p.topics.values()),
                              "activity": p.activity["label"]} for p in here},
              "asks": []}
    out["moments"].append(moment)
    saved_now = m.now
    m.now = minute
    try:
        for p in sorted(here, key=lambda x: data.ORDER.index(x.id)):
            if q.resting(p.id) or not any(t["first"] for t in p.topics.values()):
                continue
            t = minute // data.MINUTES_PER_TURN
            opts = m.options_for(p)
            base = m.prompt_for(p, t, opts)
            b = baseline[(clock(minute), p.id)]
            if base != b["prompt"]:
                raise Stop(f"{clock(minute)} {p.id}: the rebuilt prompt is not calm_probe's")
            reordered = [o for o in opts if o.id.startswith(TOPIC)] + [o for o in opts if not o.id.startswith(TOPIC)]
            o_prompt = m.prompt_for(p, t, reordered)
            # O changes the order of the option lines only.
            h0, b0, t0 = option_block(base)
            h1, b1, t1 = option_block(o_prompt)
            assert h0 == h1 and t0 == t1 and sorted(b0) == sorted(b1), f"{clock(minute)} {p.id}: O changed more"
            line, checks = quiet_line(m, p, minute, seen)
            if not checks["true"]:
                raise Stop(f"{clock(minute)} {p.id}: the T line is not true: {checks}")
            prompts = {"T": (with_line(base, line), opts), "O": (o_prompt, reordered),
                       "TO": (with_line(o_prompt, line), reordered)}
            answers = {}
            for v in VARIANTS:
                prompt, order = prompts[v]
                if prompt == base:
                    how, text = "calm_probe's answer: the same prompt, not asked again", b["answer"]
                elif v == "TO" and prompt == prompts["T"][0]:
                    how, text = "T's answer: the same prompt, not asked again", answers["T"]
                else:
                    live0 = calm.live
                    text = calm.ask(world.SYSTEM, prompt)
                    how = "live" if calm.live > live0 else "from this probe's cache"
                answers[v] = text
                a = answer_fields(text)
                offered = [o.id for o in order]
                moment["asks"].append({
                    "variant": v, "who": p.id, "minute": minute, "clock": clock(minute), "seed": out["seed"],
                    "how": how, "t_line": line if "T" in v else None, "t_checks": checks if "T" in v else None,
                    "offered": offered, "labels": {o.id: o.label for o in order},
                    "topic_offered": [o for o in offered if o.startswith(TOPIC)],
                    "tell_position": next((i + 1 for i, o in enumerate(offered)
                                           if o.startswith("tell_") and o.endswith("_visit")), None),
                    "n_options": len(offered),
                    "option": a.get("option"), "say": a.get("say"), "feeling": a.get("feeling"),
                    "reason": a.get("reason"), "suspects": a.get("suspects"), "angry_at": a.get("angry_at"),
                    "valid": a.get("option") in offered, "prompt": prompt, "answer": text,
                    "baseline": {"option": b["option"], "say": b["say"], "feeling": b["feeling"],
                                 "reason": b["reason"]}})
    finally:
        m.now = saved_now


def run_scene(k, calm_cache, client, out):
    src = os.path.join(out["tmp"], f"replay{k}.json")
    shutil.copyfile(os.path.join(SOURCE, f"scene{k}.json"), src)
    rec = json.load(open(os.path.join(BASELINE, f"scene{k}.json"), encoding="utf-8"))
    baseline = {(a["clock"], a["who"]): a for mo in rec["moments"] for a in mo["asks"]}
    assert len(baseline) == 9 and rec["seed"] == out["seed"]
    m, replay, chron = talk.day3(src, NoLive())
    spec = next(v for v in talk.VISITORS if v["scene"] == k)
    talk.visitor(m, spec, talk.KNOCK)
    calm = Oracle(Cache(calm_cache), talk.MODEL, out["seed"], client=client)
    out["moments"] = []
    out["how"] = {}
    seen = []                                           # (minute, {person: (room, activity, resting)})
    real_step, real_advance = quiet.Quiet.step, quiet.Quiet.advance

    def snap(minute):
        seen.append((minute, {p.id: (p.room, p.activity["label"], m.quiet.resting(p.id))
                              for p in m.people.values()}))

    def at(minute, how):
        out["how"][clock(minute)] = how
        calm_asks(m, minute, calm, out, seen, baseline)
        if minute == MINUTES[-1]:
            raise Done(minute)

    def step(q, minute):
        """A quiet step falls on the minute: the asks come after it, as a trigger's would."""
        fired = real_step(q, minute)
        snap(minute)
        if minute in MINUTES:
            at(minute, f"after the quiet step at that minute (a trigger fired: {bool(fired)})")
        return fired

    def advance(q, minute, to):
        """Quiet time jumps from one event to the next (Quiet.next_event). A jump over the minute is split there: the
        jump to it, its needs ticked (no need crosses a line between events), the asks, then the rest of the jump."""
        for mm in MINUTES:
            if minute < mm < to:
                real_advance(q, minute, mm)
                crossed = q.tick(mm)
                snap(mm)
                at(mm, f"inside a quiet jump from {clock(minute)} to {clock(to)}, its needs ticked at the minute "
                       f"(lines crossed: {crossed})")
                minute = mm
        real_advance(q, minute, to)
        snap(to)
    quiet.Quiet.step, quiet.Quiet.advance = step, advance
    try:
        quiet.play(m)
    except Done:
        pass
    finally:
        quiet.Quiet.step, quiet.Quiet.advance = real_step, real_advance
        out["replay"] = {"live": replay.live, "from_cache": replay.from_cache, "api_requests": replay.api_requests}
        out["calm"] = {"live": calm.live, "from_cache": calm.from_cache, "api_requests": calm.api_requests}
        sc = m.quiet.door_scenes[0] if m.quiet.door_scenes else None
        out["visit"] = {"start": sc["start"], "end": sc["end"], "outcome": sc["outcome"],
                        "acts": sc["acts"]} if sc else None
        out["asked_after_0945"] = [(clock(r["minute"]), d["person"], d["mode"]) for r in m.log
                                   for d in r["decisions"] if r["minute"] >= 165]
        out["snapshots"] = [(clock(mm), s) for mm, s in seen if mm >= 165]


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
    tmp = tempfile.mkdtemp()
    cache_dir = tmp if args.fake else os.path.join("cache", "calm_variants")
    out_dir = tmp if args.fake else os.path.join("runs", "calm_variants")
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
        for k, seed in SEEDS.items():
            if any(p["phase"] == f"scene{k}" for p in ledger["phases"]):
                print(f"scene {k}: started already, not run again", flush=True)
                continue
            inner = FakeClient(invalid_every=0, max_calls=10 ** 6) if args.fake else GeminiClient(config, seed)
            client = Capped(inner, ledger)
            phase = {"phase": f"scene{k}", "seed": seed, "live_before": ledger["live"]}
            ledger["phases"].append(phase)
            save_ledger()
            out = {"scene": k, "seed": seed, "tmp": tmp}
            stopped = None
            try:
                run_scene(k, os.path.join(cache_dir, f"scene{k}.json"), client, out)
            except (Stop, StopMorning) as e:
                stopped = f"{type(e).__name__}: {e}"
                code = 3
            out.pop("tmp")
            out["stopped"] = stopped
            with open(os.path.join(out_dir, f"scene{k}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
                f.write("\n")
            phase.update(stopped=stopped, replay=out.get("replay"), calm=out.get("calm"), live_after=ledger["live"])
            save_ledger()
            print(f"scene {k} (client seed {seed}): replay {out.get('replay')}; variant asks {out.get('calm')}; "
                  f"stopped {stopped}", flush=True)
            print(f"  decisions after 09:45 in the replay: {out.get('asked_after_0945')}", flush=True)
            print(f"  how each minute was reached: {out.get('how')}", flush=True)
            for mo in out.get("moments", []):
                print(f"  {mo['clock']}: Daniel in {mo['daniel_room']} (resting {mo['daniel_resting']}); here "
                      f"{ {q: (h['resting'], h['first_hand'], h['activity']) for q, h in mo['here'].items()} }",
                      flush=True)
                for a in mo["asks"]:
                    print(f"    {a['variant']:2} {a['who']}: {a['how']}; tell at {a['tell_position']} of "
                          f"{a['n_options']}; chose {a['option']} (valid {a['valid']}; calm_probe "
                          f"{a['baseline']['option']}); say {a['say']!r}", flush=True)
                    if a["t_line"]:
                        print(f"       T line: {a['t_line']}", flush=True)
            if stopped:
                print(f"scene {k} STOPPED: {stopped}", flush=True)
    finally:
        save_ledger()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"live asks in all: {ledger['live']}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
