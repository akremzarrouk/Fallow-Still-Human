"""Runs `python morning.py --seed 2 --out v23 --days 10` with two additions (reports/v23_plan.md):

- a 450-ask cap: a counter on GeminiClient.generate. When CAP live asks have been sent (this process and the earlier
  ones recorded in runs/v23/asks_live_before.txt, if a resume needs it), the next one raises gemini.CallCapReached
  (a StopMorning) before any request goes out; the run then exits 3 as for any stop.
- a record of every ask: scene, prompt, answer, and whether it was live or from the cache, written to
  runs/v23/asks<suffix>.json at the end (also on a stop). Days 1 and 2, nights 1 and 2 and minds 1 and 2 must all come
  from the cache: a live ask in those scenes raises before any request goes out.

No prompt, option or answer is changed.

    GEMINI_API_KEY=... python runs/v23/run_capped.py           (from Prototypes/llm-morning/)
    python runs/v23/run_capped.py --fake                        the same against the fake model (runs/v23/fake/)
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import gemini    # noqa: E402
import morning   # noqa: E402

CAP = 450
FAKE = "--fake" in sys.argv
ARGS = ["morning.py", "--seed", "2", "--out", "v23", "--days", "10"] + (["--fake"] if FAKE else [])
HERE = os.path.dirname(os.path.abspath(__file__))
SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11):
    SC += [f"night{k - 1}", f"mind{k - 1}", f"day{k}"]
CACHED_ONLY = set(SC[:6])
state = {"sent": 0, "scene": 0, "asks": []}
before_path = os.path.join(HERE, "asks_live_before.txt")
BEFORE = int(open(before_path).read().split()[0]) if os.path.exists(before_path) and not FAKE else 0


def scene():
    return SC[min(state["scene"], len(SC) - 1)]


def install(cap=CAP):
    orig = gemini.GeminiClient.generate

    def generate(self, system, prompt, schema=None):
        if scene() in CACHED_ONLY:
            raise gemini.CallCapReached(f"stopped: a live ask in {scene()}, which must come from cache/v16 "
                                        f"(reports/v23_plan.md); no request sent.")
        if BEFORE + state["sent"] >= cap:
            raise gemini.CallCapReached(f"stopped: the {cap}-ask cap of reports/v23_plan.md was reached "
                                        f"({BEFORE} + {state['sent']} live asks sent).")
        state["sent"] += 1
        return orig(self, system, prompt) if schema is None else orig(self, system, prompt, schema=schema)
    gemini.GeminiClient.generate = generate

    on, oa = gemini.Oracle.new_scene, gemini.Oracle.ask

    def new_scene(self):
        state["scene"] += 1
        return on(self)

    def ask(self, system, prompt, schema=None):
        live = self.live
        r = oa(self, system, prompt, schema)
        state["asks"].append({"scene": scene(), "live": self.live > live, "prompt": prompt, "answer": r})
        return r
    gemini.Oracle.new_scene, gemini.Oracle.ask = new_scene, ask


def dump():
    n = 1
    path = os.path.join(HERE, "fake" if FAKE else "", "asks.json")
    while os.path.exists(path):         # a resumed run keeps the earlier record
        n += 1
        path = os.path.join(HERE, "fake" if FAKE else "", f"asks{n}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state["asks"], f, ensure_ascii=False, indent=1, default=str)
    print(f"asks recorded: {len(state['asks'])} ({sum(a['live'] for a in state['asks'])} live) -> "
          f"{os.path.relpath(path, os.getcwd())}", flush=True)


if __name__ == "__main__":
    install()
    sys.argv = ARGS
    try:
        morning.main()
    finally:
        dump()
