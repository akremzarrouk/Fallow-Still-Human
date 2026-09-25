"""Runs the daniel_ate_it morning with rules plus a language model, and writes it as a story.

    python morning.py --seed 1              a fresh morning; answers not in the cache are asked of Gemini
    python morning.py --seed 1 --replay     the same morning from the cache only, with no API calls;
                                            writes runs/<name>.replay.md and compares it with runs/<name>.md
    python morning.py --seed 1 --fake       the same, against the fake model (for building and testing)

The model name and call limits are in config.json. The key is read from GEMINI_API_KEY.

Exit codes: 0 done (and, for --replay, identical); 1 replay differs; 3 stopped cleanly part way
(quota, rate limit, call cap, or a replay cache miss): see the message.
"""
import argparse
import hashlib
import json
import os
import sys
import time

from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config
from story import render
from world import Morning

HERE = os.path.dirname(os.path.abspath(__file__))


def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
        client=None, quiet=False):
    config = load_config(config_path or os.path.join(HERE, "config.json"))
    model_name = "fake" if fake else config["model"]
    # This version's runs and answers live apart from the earlier versions' (runs/ and cache/
    # for the first, runs/vN and cache/vN after), which v1/, v2/ and v3/ can still replay.
    runs_dir = runs_dir or os.path.join(HERE, "runs", "v4", "fake" if fake else "")
    cache_dir = cache_dir or os.path.join(HERE, "cache", "v4")
    os.makedirs(runs_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    name = f"daniel_ate_it-seed{seed}"
    cache_path = os.path.join(cache_dir, f"{model_name}-{name}.json")
    cache = Cache(cache_path)
    if client is None and not replay:
        client = (FakeClient(max_calls=config["max_calls_per_morning"]) if fake
                  else GeminiClient(config, seed))
    oracle = Oracle(cache, model_name, seed, client=None if replay else client, replay=replay,
                    max_calls=config["max_calls_per_morning"])

    command = f"python morning.py --seed {seed}" + (" --fake" if fake else "")
    say = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    say(f"{name}: model {model_name}, {'replay from cache only' if replay else 'fresh'}; "
        f"cache {os.path.relpath(cache_path, HERE)} holds {len(cache.entries)} answers")
    started = time.monotonic()
    morning = Morning(oracle, seed)
    try:
        for t in range(morning.turns):
            morning.turn(t)
            asked = sum(d["mode"] != "routine" for d in morning.log[-1]["decisions"])
            if asked:
                say(f"  min {t * 3:02d}: model asked for {asked}; so far {oracle.live} live, "
                    f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
    except StopMorning as stop:
        say(f"\n{stop}")
        say(f"Answers received so far ({len(cache.entries)}) are kept in {os.path.relpath(cache_path, HERE)}.")
        if not replay:
            say(f"To resume, run the same command again once the limit has passed "
                f"(the free daily quota resets at midnight Pacific time): {command}")
            say("Cached answers are reused, so only the prompts not yet answered are sent.")
        return {"stopped": str(stop), "api_requests": oracle.api_requests}, 3
    seconds = time.monotonic() - started
    morning.finish()

    text = render(morning, seed, model_name, command)
    story_path = os.path.join(runs_dir, f"{name}.md")
    out_path = os.path.join(runs_dir, f"{name}.replay.md") if replay else story_path
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    all_d = [d for rec in morning.log for d in rec["decisions"]]
    meta = {
        "model": model_name, "seed": seed, "replay": replay,
        "api_requests": oracle.api_requests, "answers_live": oracle.live,
        "answers_from_cache": oracle.from_cache,
        "model_decisions": sum(d["mode"] == "model" for d in all_d),
        "fallbacks": sum(d["mode"] == "fallback" for d in all_d),
        "routine_decisions": sum(d["mode"] == "routine" for d in all_d),
        "lines_spoken": len(morning.said),
        "inner_moments": sum(1 for d in all_d if d.get("inner")),
        "private_talks": sum(1 for d in all_d if d["option"] in ("accept_aside", "refuse_aside")),
        "max_prompt_tokens_estimated": morning.max_prompt_tokens,
        "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
        "run_seconds": round(seconds, 1),
        "story": os.path.relpath(out_path, HERE).replace("\\", "/"),
        "story_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    say(f"\nwrote {meta['story']}")
    for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",
              "routine_decisions", "lines_spoken", "inner_moments", "private_talks",
              "max_prompt_tokens_estimated",
              "max_prompt_tokens_counted_by_api", "run_seconds",
              "story_sha256"):
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
    with open(os.path.join(runs_dir, f"{name}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(morning.transcript, f, ensure_ascii=False, indent=1)
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
    args = ap.parse_args()
    _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config)
    sys.exit(code)


if __name__ == "__main__":
    main()
