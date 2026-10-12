"""The calm probe (reports/calm_probe_plan.md): do people tell Daniel about the visit when asked in a calm moment?

reports/talk_probe.md: the tell was offered 21 times in scenes 1 and 3 and never taken, but every offer came inside
the door stretch or a grudge meeting; from 09:51 to 11:45 Daniel sat with the others and nobody was asked at all.

For scenes 1 and 3 of the talk probe:
- Replay. Day 3 is played again from a copy of cache/talk_probe/scene<k>.json (v16 seed 2 to day 3, the talk probe's
  visitor at 09:42). Every ask must come from the cache: a miss stops the scene (0 live asks in the replay).
- The calm asks. At 10:00, 10:30 and 11:00, after that minute's quiet step, each awake person in Daniel's room who
  knows the visit first-hand gets the prompt they would get if asked at that minute: World.prompt_for with
  World.options_for, no trigger, lull or extra line (World.ask_model builds it the same way). It is asked live on an
  oracle of its own (cache/calm_probe/scene<k>.json), client seed 201 (scene 1) or 202 (scene 3), once. The answer is
  recorded and never applied: the replayed day goes on from the cache as the talk probe played it. The scene stops
  after 11:00's asks.

No live ask past CAP (40) in all. The key is read from GEMINI_API_KEY only.

    python runs/calm_probe/probe.py --fake     a temp folder and the fake model; writes nothing in the repository
    python runs/calm_probe/probe.py --live     cache/calm_probe/, runs/calm_probe/; asks Gemini
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

CAP = 40
MINUTES = (180, 210, 240)                               # 10:00, 10:30, 11:00
SEEDS = {1: 201, 3: 202}                                # the calm asks' client seed, per scene
SOURCE = os.path.join("cache", "talk_probe")            # scene<k>.json: the talk probe's caches
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
    """The calm asks' client: no live answer past CAP in all."""

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


def calm_asks(m, minute, calm, out):
    """The calm asks at `minute`: each awake person in Daniel's room who knows the visit first-hand."""
    q = m.quiet
    dan = m.people["daniel"]
    here = [p for p in m.people.values() if p.room == dan.room and p.id != "daniel"]
    moment = {"minute": minute, "clock": clock(minute), "daniel_room": dan.room,
              "daniel_resting": q.resting("daniel"), "daniel_beliefs": len(dan.beliefs),
              "here": {p.id: {"resting": q.resting(p.id),
                              "first_hand": any(t["first"] for t in p.topics.values()),
                              "topic_said": {k: v for k, v in p.topic_said.items()}} for p in here},
              "asks": []}
    out["moments"].append(moment)
    saved_now = m.now
    m.now = minute
    try:
        for p in sorted(here, key=lambda x: data.ORDER.index(x.id)):
            if q.resting(p.id) or not any(t["first"] for t in p.topics.values()):
                continue
            opts = m.options_for(p)
            prompt = m.prompt_for(p, minute // data.MINUTES_PER_TURN, opts)
            text = calm.ask(world.SYSTEM, prompt)
            a = answer_fields(text)
            offered = [o.id for o in opts]
            moment["asks"].append({
                "who": p.id, "minute": minute, "clock": clock(minute), "seed": out["seed"],
                "offered": offered, "labels": {o.id: o.label for o in opts},
                "topic_offered": [o for o in offered if o.startswith(("talk_", "tell_"))],
                "option": a.get("option"), "say": a.get("say"), "feeling": a.get("feeling"),
                "reason": a.get("reason"), "suspects": a.get("suspects"), "angry_at": a.get("angry_at"),
                "valid": a.get("option") in offered, "prompt": prompt, "answer": text})
    finally:
        m.now = saved_now


def run_scene(k, calm_cache, client, out):
    src = os.path.join(out["tmp"], f"replay{k}.json")
    shutil.copyfile(os.path.join(SOURCE, f"scene{k}.json"), src)
    m, replay, chron = talk.day3(src, NoLive())
    spec = next(v for v in talk.VISITORS if v["scene"] == k)
    talk.visitor(m, spec, talk.KNOCK)
    calm = Oracle(Cache(calm_cache), talk.MODEL, out["seed"], client=client)
    out["moments"] = []
    out["how"] = {}
    real_step, real_advance = quiet.Quiet.step, quiet.Quiet.advance

    def at(minute, how):
        out["how"][clock(minute)] = how
        calm_asks(m, minute, calm, out)
        if minute == MINUTES[-1]:
            raise Done(minute)

    def step(q, minute):
        """A quiet step falls on the minute: the asks come after it, as a trigger's would."""
        fired = real_step(q, minute)
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
                at(mm, f"inside a quiet jump from {clock(minute)} to {clock(to)}, its needs ticked at the minute "
                       f"(lines crossed: {crossed})")
                minute = mm
        real_advance(q, minute, to)
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
    cache_dir = tmp if args.fake else os.path.join("cache", "calm_probe")
    out_dir = tmp if args.fake else os.path.join("runs", "calm_probe")
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
            print(f"scene {k} (client seed {seed}): replay {out.get('replay')}; calm asks {out.get('calm')}; "
                  f"stopped {stopped}", flush=True)
            print(f"  decisions after 09:45 in the replay: {out.get('asked_after_0945')}", flush=True)
            print(f"  how each minute was reached: {out.get('how')}", flush=True)
            for mo in out.get("moments", []):
                print(f"  {mo['clock']}: Daniel in {mo['daniel_room']} (resting {mo['daniel_resting']}); here "
                      f"{ {q: (h['resting'], h['first_hand']) for q, h in mo['here'].items()} }", flush=True)
                for a in mo["asks"]:
                    print(f"    {a['who']}: topic options {a['topic_offered']}; chose {a['option']} (valid {a['valid']})"
                          f"; say {a['say']!r}", flush=True)
            if stopped:
                print(f"scene {k} STOPPED: {stopped}", flush=True)
    finally:
        save_ledger()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"live asks in all: {ledger['live']}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
