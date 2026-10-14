"""Runs a morning, the night after it and the next morning, with rules plus a language model, and
writes them as one story (reports/night_design.md).

    python morning.py --seed 1              a fresh run; answers not in the cache are asked of Gemini
    python morning.py --seed 1 --replay     the same run from the cache only, with no API calls;
                                            writes runs/<out>/<name>.replay.md and compares it with
                                            runs/<out>/<name>.md
    python morning.py --seed 1 --fake       the same, against the fake model (for building and testing)

    --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
    --model KEY       another model from config.json `models` (default: config.json `model`)
    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v13; v4 replays
                      the fourth version's runs; v5/check.py to v12/check.py replay the
                      fifth's to twelfth's)

Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
are in config.json; the call limit counts each of the three apart. The key is read from
GEMINI_API_KEY.

Exit codes: 0 done (and, for --replay, identical); 1 replay differs; 3 stopped cleanly part way
(quota, rate limit, call cap, or a replay cache miss): see the message.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import data
from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config
from night import Night
from story import render, render_day2, render_night
from world import Morning

HERE = os.path.dirname(os.path.abspath(__file__))
DAY_KEYS = ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
            "routine_decisions", "lines_spoken", "inner_moments", "lull_moments", "private_talks",
            "trip_minute", "trip_acts", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api")


class Scene:
    """What one scene asked of the oracle: the counts since it began."""

    def __init__(self, oracle):
        self.oracle = oracle
        self.start = self.now()
        self.end = None

    def now(self):
        o = self.oracle
        return o.from_cache, o.live, o.api_requests, len(o.prompt_tokens)

    def close(self):
        self.end = self.now()

    def counts(self):
        (cached, live, api, tokens), (cached2, live2, api2, tokens2) = self.start, self.end or self.now()
        return {"api_requests": api2 - api, "answers_live": live2 - live, "answers_from_cache": cached2 - cached,
                "max_prompt_tokens_counted_by_api": max(self.oracle.prompt_tokens[tokens:tokens2], default=None)}


def day_meta(m, scene):
    """A morning's numbers (day 1's are v11's)."""
    all_d = [d for rec in m.log for d in rec["decisions"]]
    meta = {
        **scene.counts(),
        "model_decisions": sum(d["mode"] == "model" for d in all_d),
        "fallbacks": sum(d["mode"] == "fallback" for d in all_d),
        "routine_decisions": sum(d["mode"] == "routine" for d in all_d),
        "lines_spoken": len(m.said),
        "inner_moments": sum(1 for d in all_d if d.get("inner")),
        "lull_moments": sum(1 for d in all_d if d.get("lull") is not None),
        "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
        "trip_minute": m.trip["minute"] if m.trip else None,
        "trip_acts": len(m.trip_acts),
        "max_prompt_tokens_estimated": m.max_prompt_tokens,
    }
    return {k: meta[k] for k in DAY_KEYS}


def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v13"):
    config = load_config(config_path or os.path.join(HERE, "config.json"))
    if model_key:
        config = {**config, **config["models"][model_key]}
    model_name = "fake" if fake else config["model"]
    # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
    # cache/vN after), which v1/ to v12/ can still replay.
    runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
    cache_dir = cache_dir or os.path.join(HERE, "cache", out)
    os.makedirs(runs_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    name = f"{scenario}-{model_key}-seed{seed}" if model_key else f"{scenario}-seed{seed}"
    cache_path = os.path.join(cache_dir, f"{model_name}-{name}.json")
    cache = Cache(cache_path)
    if client is None and not replay:
        client = (FakeClient(max_calls=config["max_calls_per_morning"]) if fake
                  else GeminiClient(config, seed))
    oracle = Oracle(cache, model_name, seed, client=None if replay else client, replay=replay,
                    max_calls=config["max_calls_per_morning"])

    command = ("python morning.py"
               + (f" --scenario {scenario}" if scenario != data.DEFAULT_SCENARIO else "")
               + (f" --model {model_key}" if model_key else "")
               + f" --seed {seed}" + (" --fake" if fake else ""))
    say = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    say(f"{name}: model {model_name}, {'replay from cache only' if replay else 'fresh'}; "
        f"cache {os.path.relpath(cache_path, HERE)} holds {len(cache.entries)} answers")
    started = time.monotonic()

    def morning_turns(m, tag):
        for t in range(m.turns):
            m.turn(t)
            asked = sum(d["mode"] != "routine" for d in m.log[-1]["decisions"])
            if asked:
                say(f"  {tag}min {t * 3:02d}: model asked for {asked}; so far {oracle.live} live, "
                    f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
        m.finish()

    scenes = {}
    try:
        scenes["day1"] = Scene(oracle)
        morning = Morning(oracle, seed, scenario)
        morning_turns(morning, "")
        # Day 1's story is written as it ended, before the night touches anything.
        day1_text = render(morning, seed, model_name, command)
        scenes["day1"].close()
        oracle.new_scene()
        scenes["night"] = Scene(oracle)
        night = Night(morning, oracle).run()
        scenes["night"].close()
        say(f"  night: model asked for {len(night.decisions)}; so far {oracle.live} live, "
            f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
        oracle.new_scene()
        scenes["day2"] = Scene(oracle)
        day2 = Morning.next_day(morning, night, oracle)
        morning_turns(day2, "day 2 ")
        scenes["day2"].close()
    except StopMorning as stop:
        say(f"\n{stop}")
        say(f"Answers received so far ({len(cache.entries)}) are kept in {os.path.relpath(cache_path, HERE)}.")
        if not replay:
            say(f"To resume, run the same command again once the limit has passed "
                f"(the free daily quota resets at midnight Pacific time): {command}")
            say("Cached answers are reused, so only the prompts not yet answered are sent.")
        return {"stopped": str(stop), "api_requests": oracle.api_requests}, 3
    seconds = time.monotonic() - started

    text = day1_text + render_night(night) + render_day2(day2)
    story_path = os.path.join(runs_dir, f"{name}.md")
    out_path = os.path.join(runs_dir, f"{name}.replay.md") if replay else story_path
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    night_counts = scenes["night"].counts()
    day2_counts = scenes["day2"].counts()
    meta = {
        "model": model_name, "scenario": scenario, "seed": seed, "replay": replay,
        "api_requests": oracle.api_requests, "answers_live": oracle.live,
        "answers_from_cache": oracle.from_cache,
        "day1": day_meta(morning, scenes["day1"]),
        "night_asks": night_counts["answers_live"] + night_counts["answers_from_cache"],
        "night_api_requests": night_counts["api_requests"],
        "leavers": night.leavers,
        "outcome": [g["outcome"] for g in night.groups],
        "night": {**night_counts, "house": night.house, "away": [q for q in data.ORDER if q in night.away],
                  "max_prompt_tokens_estimated": night.m.max_prompt_tokens},
        "day2_asks": day2_counts["answers_live"] + day2_counts["answers_from_cache"],
        "day2_api_requests": day2_counts["api_requests"],
        # The body's food moments, and the answers of those handed a portion (reports/body_design.md, §2.7).
        "day2": {**day_meta(day2, scenes["day2"]),
                 "food_moments": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("food_moment")),
                 "give_answers": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("given_by"))},
        "max_prompt_tokens_estimated": max(morning.max_prompt_tokens, night.m.max_prompt_tokens,
                                           day2.max_prompt_tokens),
        "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
        "run_seconds": round(seconds, 1),
        "story": os.path.relpath(out_path, HERE).replace("\\", "/"),
        "story_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    say(f"\nwrote {meta['story']}")
    for k in ("api_requests", "answers_live", "answers_from_cache"):
        say(f"  {k}: {meta[k]}")
    for k in DAY_KEYS:
        say(f"  day1 {k}: {meta['day1'][k]}")
    for k in ("night_asks", "night_api_requests", "leavers", "outcome"):
        say(f"  {k}: {meta[k]}")
    say(f"  night house: {night.house}; away: {meta['night']['away']}")
    for k in DAY_KEYS + ("food_moments", "give_answers"):
        say(f"  day2 {k}: {meta['day2'][k]}")
    for k in ("day2_asks", "day2_api_requests", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api",
              "run_seconds", "story_sha256"):
        say(f"  {k}: {meta[k]}")
    if replay:
        if not os.path.exists(story_path):
            say(f"no original story at {os.path.relpath(story_path, HERE)} to compare with")
            return meta, 1
        with open(story_path, "rb") as f:
            same = f.read() == text.encode("utf-8")
        meta["identical_to_original"] = same
        say(f"  byte for byte against {os.path.relpath(story_path, HERE)}: "
            f"{'IDENTICAL' if same else 'DIFFERS'}")
        return meta, 0 if same else 1
    transcript = {"day1": morning.transcript, "night": night.transcript(), "day2": day2.transcript}
    with open(os.path.join(runs_dir, f"{name}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(runs_dir, f"{name}.meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    return meta, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--replay", action="store_true", help="cache only, no API calls")
    ap.add_argument("--fake", action="store_true", help="use the fake model, never the API")
    ap.add_argument("--config", default=None)
    ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
    ap.add_argument("--model", default=None, help="a key of config.json `models`")
    ap.add_argument("--out", default="v13")
    args = ap.parse_args()
    _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                  scenario=args.scenario, model_key=args.model, out=args.out)
    sys.exit(code)


if __name__ == "__main__":
    main()
