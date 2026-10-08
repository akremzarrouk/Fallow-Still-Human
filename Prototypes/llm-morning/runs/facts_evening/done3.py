"""DONE 3 of reports/facts_and_evening.md: fake runs to day 5 (no API), and Q5 on each quiet day.

    python runs/facts_evening/done3.py          (from Prototypes/llm-morning/, GEMINI_API_KEY unset)

A: `morning.run(2, fake=True, days=5)`, as `morning.py --seed 2 --fake --days 5` runs it, into a temp cache.
B: the same fake model, but on day 4 nobody takes a trip position: an answer that picks a trip act is turned into
   "silent" (or the first option that is not a trip act).
"""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import morning              # noqa: E402
from gemini import FakeClient       # noqa: E402
from talk import act_of             # noqa: E402
from world import TRIP_KINDS        # noqa: E402
import data                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = ["day1", "night", "mind1", "day2", "night2", "mind2", "day3", "night3", "mind3", "day4", "night4", "mind4",
          "day5"]


class NoTripOn(FakeClient):
    def __init__(self, scenes):
        super().__init__(max_calls=150)
        self.no_trip, self.scene, self.changed = scenes, 0, 0

    def new_scene(self):
        super().new_scene()
        self.scene += 1

    def generate(self, system, prompt, schema=None):
        text = super().generate(system, prompt, schema)
        if schema is not None or SCENES[self.scene] not in self.no_trip:
            return text
        try:
            ans = json.loads(text)
        except ValueError:
            return text
        if act_of(ans.get("option", ""))[0] not in TRIP_KINDS:
            return text
        block = prompt.split("Your options:")[-1]
        options = re.findall(r"^- (\w+):", block, flags=re.M)
        speech = set(re.findall(r"^- (\w+): \(speech\)", block, flags=re.M))
        rest = [o for o in options if act_of(o)[0] not in TRIP_KINDS]
        pick = "silent" if "silent" in rest else rest[0]
        self.changed += 1
        ans.update(option=pick, say=f"[fake line {self.requests}]" if pick in speech else None)
        return json.dumps(ans)


def report(label, runs_dir):
    tr = json.load(open(os.path.join(runs_dir, "daniel_ate_it-seed2.transcript.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(runs_dir, "daniel_ate_it-seed2.meta.json"), encoding="utf-8"))
    for k in ("day3", "day4", "day5"):
        d = tr[k]
        pos = [(data.clock(a["minute"]), a["who"], a["option"]) for t in d["turns"] for a in t["acts"]
               if act_of(a["option"])[0] in TRIP_KINDS]
        q5 = [e for e in d["quiet"]["log"] if e["kind"] == "Q5"]
        st = [s for s in d["quiet"]["stretches"] if s["trigger"] == "Q5"]
        asks = meta[f"{k}_quiet"]["day_asks"] if k != "day3" else meta["day3_quiet"]["day_asks"]
        print(f"  {label} {k}: trip positions {len(pos)} (last {pos[-1] if pos else None}); day asks {asks}; "
              f"Q5 {[(data.clock(e['minute']), e['fired'], e['asked'], e['why'], e['room']) for e in q5]}; "
              f"Q5 stretch {[(data.clock(s['start']), data.clock(s['end']), s['asks']) for s in st]}")
        asked = [(data.clock(t["minute"]), a["who"], a["option"], a["mode"]) for t in d["turns"] for a in t["acts"]
                 if q5 and q5[0]["fired"] and t["minute"] == q5[0]["minute"]]
        if asked:
            print(f"      acts at {asked[0][0]}: {[x[1:] for x in asked]}")
    return meta


def main():
    for label, client in (("A", None), ("B", NoTripOn({"day4"}))):
        tmp = tempfile.mkdtemp()
        runs_dir = os.path.join(HERE, f"fake_{label}")
        meta, code = morning.run(2, fake=client is None, client=client, runs_dir=runs_dir, cache_dir=tmp, quiet=True,
                                 days=5)
        print(f"{label}: exit {code}; api_requests {meta['api_requests']}; days {meta.get('days')}"
              + (f"; day-4 answers turned from a trip act to another: {client.changed}" if client else ""))
        report(label, runs_dir)


if __name__ == "__main__":
    main()
