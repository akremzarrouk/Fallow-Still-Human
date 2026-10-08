"""DONE 3 of reports/ten_days_prep.md: a fake run of seed 3 to day 10 (no API), with each day's largest prompt and
what the size limits cut.

    python runs/ten_days/done3.py          (from Prototypes/llm-morning/, GEMINI_API_KEY unset)

`morning.run(3, fake=True, days=10)`, as `morning.py --seed 3 --fake --days 10` runs it, into a temp cache; the run's
files go to runs/ten_days/fake10/. Two wrappers record, without changing anything:
- `Morning.prompt_parts` (world.py), for every day and night prompt: the size estimate as max_prompt_tokens counts it,
  the part counted against the 1400 budget, and the lines the budget cut: "today" (the day's own lines) and "before"
  (the backstory lines);
- `memory.bounded` (memory.py), once per person per morning: whether block A was shortened, and how many of C's older
  thoughts, C's lines and B's lines the 560 bound removed.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import data                 # noqa: E402
import gemini               # noqa: E402
import memory               # noqa: E402
import morning              # noqa: E402
import world                # noqa: E402
from talk import act_of     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DAYS = 10
SCENES = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, DAYS + 1):
    SCENES += [f"night{k - 1}", f"mind{k - 1}", f"day{k}"]
state = {"scene": 0}
records, bounds = [], []
orig_new, orig_parts, orig_bounded = gemini.Oracle.new_scene, world.Morning.prompt_parts, memory.bounded


def new_scene(self):
    state["scene"] += 1
    return orig_new(self)


def prompt_parts(self, p, opts, head, now, system, when, minute):
    today_all = [f"- {data.clock(m)}: {x}" for m, x in p.memory if m != minute] + [f"- tonight: {x}" for x in p.tonight]
    back_all = [f"- {x}" for x in p.backstory]
    tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]
    keep = p.trip_memories if self.trip else set()
    block = 0
    if self.trip:
        house = head[-1][len(f"The house: {data.HOUSE} "):]
        block += sum(len(x) + 1 for x in self.trip_lines(p))
        block += sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in world.TRIP_KINDS)
        block += sum(len(f"- {x}") + 1 for x in keep)
        block += max(0, len(house) - len(data.HOUSE_THINGS))
    block += sum(len(x) + 1 for x in self.carry.get(p.id, []))
    text = orig_parts(self, p, opts, head, now, system, when, minute)
    lines = set(text.split("\n"))
    records.append({"scene": SCENES[state["scene"]], "person": p.id, "minute": minute,
                    "estimate": world.estimate_tokens(system + text),
                    "budget": world.estimate_tokens(system + text, block),
                    "cut_today": sum(1 for x in today_all if x not in lines),
                    "cut_before": sum(1 for x in back_all if x not in lines)})
    return text


def bounded(a_variants, b_lines, c_items, cap=memory.MEMORY_MAX):
    r = orig_bounded(a_variants, b_lines, c_items, cap)
    bounds.append({"scene": SCENES[state["scene"]], "a_variant": a_variants.index(r["A"]),
                   "c_thoughts": sum(1 for it in c_items if it.get("thought"))
                   - sum(1 for it in r["C_items"] if it.get("thought")),
                   "c_lines": len(c_items) - len(r["C_items"]), "b_lines": len(b_lines) - len(r["B"])})
    return r


def main():
    gemini.Oracle.new_scene, world.Morning.prompt_parts, memory.bounded = new_scene, prompt_parts, bounded
    runs_dir = os.path.join(HERE, "fake10")
    meta, code = morning.run(3, fake=True, runs_dir=runs_dir, cache_dir=tempfile.mkdtemp(), quiet=True, days=DAYS)
    print(f"exit {code}; days {meta.get('days')}; api_requests {meta['api_requests']} (the fake client's)")
    tr = json.load(open(os.path.join(runs_dir, "daniel_ate_it-seed3.transcript.json"), encoding="utf-8"))
    print(f"scenes in the transcript: {[k for k in tr if k != 'chronicle']}")
    last = tr[f"day{DAYS}"]["quiet"]
    print(f"day {DAYS}: last span ends {data.clock(max(s['end'] for s in last['spans']))}; "
          f"stretches {[(data.clock(s['start']), s['trigger']) for s in last['stretches']]}")
    print("\nthird fasting stage (need events with fast stage 3), by day:")
    for k in range(3, DAYS + 1):
        q = tr[f"day{k}"]["quiet"]
        third = [(data.clock(e["minute"]), e["who"]) for e in q["need_events"] if e["need"] == "fast" and e["stage"] == 3]
        q1 = [(data.clock(e["minute"]), e["who"], e["fired"], e["why"]) for e in q["log"]
              if e["kind"] == "Q1" and e["need"] == "fast" and e["stage"] == 3]
        stages = {p: max((s for _, s in []), default=None) for p in data.ORDER}
        fasting = {p: round(q["needs"][p][-1][1], 1) for p in data.ORDER if p in q["needs"]}
        print(f"  day {k}: crossings {third}; Q1 {q1}; fasting at 21:00 {fasting}; day asks {q['asks']['day']}; "
              f"away {tr[f'day{k}'].get('away', [])}")
    print("\nper day: prompts; largest estimate / against the budget; most cut by the budget in one prompt "
          "(today / before); prompts with any cut; the memory bound's trims that morning (A shortened, C thoughts, "
          "C lines, B lines)")
    for k in range(1, DAYS + 1):
        for scene in ([f"day{k}"] + ([f"night{k}"] if k < DAYS else [])):
            rs = [r for r in records if r["scene"] == scene]
            if not rs:
                continue
            big = max(rs, key=lambda r: r["estimate"])
            b = [x for x in bounds if x["scene"] == scene]
            trims = ((sum(x["a_variant"] > 0 for x in b), sum(x["c_thoughts"] for x in b), sum(x["c_lines"] for x in b),
                      sum(x["b_lines"] for x in b)) if b else None)
            print(f"  {scene}: {len(rs)} prompts; largest {big['estimate']} / {big['budget']} ({big['person']}, "
                  f"{data.clock(big['minute']) if big['minute'] is not None else 'night'}); most cut "
                  f"{max(r['cut_today'] for r in rs)} / {max(r['cut_before'] for r in rs)}; prompts with a cut "
                  f"{sum(1 for r in rs if r['cut_today'] or r['cut_before'])}; memory bound {trims}")
    over = [r for r in records if r["budget"] > world.PROMPT_TOKEN_BUDGET]
    print(f"\nprompts over the 1400 budget after cutting: {len(over)}"
          + (f" (e.g. {over[0]})" if over else ""))


if __name__ == "__main__":
    main()
