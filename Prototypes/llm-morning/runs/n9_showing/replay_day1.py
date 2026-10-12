"""Replays day 1 of daniel_ate_it seeds 1-3 from the cache only, on the current code (which records
turns[].showing), and proves the morning is unchanged: sha256 of day1.turns with `showing` stripped must equal the
hashes of design/never-checker-design.md §2. No API: the Oracle is in replay mode with no client, and a cache miss
raises gemini.CacheMiss, which stops the script.

Each seed's cache is copied to cache/n9_showing/ first, so the original caches are only read. Writes
runs/n9_showing/daniel_ate_it-seed<k>.transcript.json ({"day1": ...}). Run from Prototypes/llm-morning/:

    env -u GEMINI_API_KEY python runs/n9_showing/replay_day1.py
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, HERE)

from gemini import Cache, Oracle    # noqa: E402
from world import Morning           # noqa: E402

MODEL = "gemini-3.5-flash-lite"
# name -> (seed, source version, §2 hash of day1.turns)
REPLAYS = {"S1": (1, "v18", "cf9f5f36c4"), "S2": (2, "v22", "db5de15235"), "S3": (3, "v20", "36b4a4a0ff")}
OUT_RUNS = os.path.join(HERE, "runs", "n9_showing")
OUT_CACHE = os.path.join(HERE, "cache", "n9_showing")


def turns_hash(turns):
    """design §7 command 2: sha256 of json.dumps(turns, sort_keys=True), first 10 hex digits."""
    return hashlib.sha256(json.dumps(turns, sort_keys=True).encode()).hexdigest()[:10]


def main():
    if os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY is set; run with it unset")
    os.makedirs(OUT_CACHE, exist_ok=True)
    ok = True
    for name, (seed, version, expected) in REPLAYS.items():
        base = f"daniel_ate_it-seed{seed}"
        src = os.path.join(HERE, "cache", version, f"{MODEL}-{base}.json")
        cache_path = os.path.join(OUT_CACHE, f"{MODEL}-{base}.json")
        shutil.copyfile(src, cache_path)
        oracle = Oracle(Cache(cache_path), MODEL, seed, client=None, replay=True)
        m = Morning(oracle, seed, "daniel_ate_it").run()      # gemini.CacheMiss stops here on any miss
        day1 = m.transcript
        with open(os.path.join(OUT_RUNS, f"{base}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"day1": day1}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        stripped = [{k: v for k, v in t.items() if k != "showing"} for t in day1["turns"]]
        with open(os.path.join(HERE, "runs", version, f"{base}.transcript.json"), encoding="utf-8") as f:
            old = json.load(f)["day1"]
        new_h, old_h = turns_hash(stripped), turns_hash(old["turns"])
        rest = {k: day1[k] == old[k] for k in old if k != "turns"}
        same = new_h == expected == old_h
        ok &= same and all(rest.values())
        print(f"{name} seed {seed}: from cache {oracle.from_cache}, live {oracle.live}, API {oracle.api_requests}")
        print(f"  day1.turns sha256 stripped {new_h} | runs/{version} {old_h} | design §2 {expected} | "
              f"{'MATCH' if same else 'DIFFERS'}")
        print(f"  every turn has showing: {all('showing' in t for t in day1['turns'])}; "
              f"other day1 keys equal to runs/{version}: {rest}")
    print("ALL MATCH" if ok else "MISMATCH: stop")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
