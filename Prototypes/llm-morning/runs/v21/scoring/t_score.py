"""Scores reports/days_v21_plan.md's T1, T2 and T4 to T7, read only, no API. T3 is read by hand; `--lines` writes what
is read.

    python runs/v21/scoring/t_score.py                          runs/v21 and cache/v21, seed 2
    python runs/v21/scoring/t_score.py DIR CACHE [SEED] [--fake]  another run (a check of the script)
    python runs/v21/scoring/t_score.py --account [DIR]          the day and night account
    python runs/v21/scoring/t_score.py --lines [DIR]            every speech act of days 3-10, for T3

Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset. T2 replays the run from a temp copy of its cache
(morning.run, replay) and keeps every prompt with its scene, and every call of the memory bound.
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import data                                           # noqa: E402
import gemini                                         # noqa: E402
import memory                                         # noqa: E402
import morning                                        # noqa: E402
import world                                          # noqa: E402
from talk import act_of                               # noqa: E402

MODEL = "gemini-3.5-flash-lite"
FAKE = "--fake" in sys.argv          # a check of this script on a fake run: the fake model's cache
if FAKE:
    sys.argv.remove("--fake")
    MODEL = "fake"
DAYS = 10
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
FOOD = ("eat", "eat_given", "share")
TIRED = re.compile(r"\b(tired|exhaust|weary|sleep|weak|dizz|faint|stand)", re.I)
SCENES = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for _k in range(4, DAYS + 1):
    SCENES += [f"night{_k - 1}", f"mind{_k - 1}", f"day{_k}"]


def nkey(k):
    return "night" if k == 1 else f"night{k}"


def load(d, seed):
    name = f"daniel_ate_it-seed{seed}"
    t = json.load(open(os.path.join(d, f"{name}.transcript.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(d, f"{name}.meta.json"), encoding="utf-8"))
    return t, meta


def acts(day):
    return sorted((a for turn in day["turns"] for a in turn["acts"]), key=lambda a: tuple(a["decided_at"]))


def model_acts(day):
    return [a for a in acts(day) if a["mode"] == "model"]


def speech(day):
    return [a for a in model_acts(day) if a["words"]]


def morning_speech(day):
    s = day["quiet"]["stretches"][0]
    return [a for a in speech(day) if s["start"] <= a["minute"] < s["end"]]


def bedtimes(night):
    return [d for d in night["decisions"] if d["ask"] == "bedtime"]


def names_them(words, speaker, x):
    terms = {NAME[x]} | ({data.ADDRESS[speaker][x]} if x in data.ADDRESS.get(speaker, {}) else set())
    return any(re.search(rf"\b{re.escape(w)}\b", words, flags=re.I) for w in terms)


def replay_records(cache_dir, seed):
    """A no-API replay of the run from a temp copy of its cache. Returns (asks, bounds, parts, exit code):
    every prompt asked with its scene, every call of the memory bound, and every day and night prompt's budget."""
    tmp = tempfile.mkdtemp()
    name = f"{MODEL}-daniel_ate_it-seed{seed}.json"
    shutil.copy(os.path.join(cache_dir, name), os.path.join(tmp, name))
    asks, bounds, parts, state = [], [], [], {"scene": 0}
    orig_ask, orig_new = gemini.Oracle.ask, gemini.Oracle.new_scene
    orig_parts, orig_bounded = world.Morning.prompt_parts, memory.bounded

    def scene():
        return SCENES[min(state["scene"], len(SCENES) - 1)]

    def new_scene(self):
        state["scene"] += 1
        return orig_new(self)

    def ask(self, system, prompt, schema=None):
        m = re.match(r"You are (\w+),", prompt)
        asks.append({"scene": scene(), "who": m.group(1) if m else "?", "estimate": world.estimate_tokens(system + prompt)})
        return orig_ask(self, system, prompt, schema)

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
        parts.append({"scene": scene(), "person": p.id, "minute": minute,
                      "estimate": world.estimate_tokens(system + text),
                      "budget": world.estimate_tokens(system + text, block),
                      "cut_today": sum(1 for x in today_all if x not in lines),
                      "cut_before": sum(1 for x in back_all if x not in lines)})
        return text

    def bounded(a_variants, b_lines, c_items, cap=memory.MEMORY_MAX):
        r = orig_bounded(a_variants, b_lines, c_items, cap)
        bounds.append({"scene": scene(), "a_variant": a_variants.index(r["A"]),
                       "c_thoughts": sum(1 for it in c_items if it.get("thought"))
                       - sum(1 for it in r["C_items"] if it.get("thought")),
                       "c_lines": len(c_items) - len(r["C_items"]), "b_lines": len(b_lines) - len(r["B"])})
        return r
    gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
    world.Morning.prompt_parts, memory.bounded = prompt_parts, bounded
    try:
        _, code = morning.run(seed, replay=True, fake=FAKE, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp,
                              quiet=True, days=DAYS)
    finally:
        gemini.Oracle.ask, gemini.Oracle.new_scene = orig_ask, orig_new
        world.Morning.prompt_parts, memory.bounded = orig_parts, orig_bounded
        shutil.rmtree(tmp)
    return asks, bounds, parts, code


def scores(t, meta, asks, bounds):
    r = {}
    nights = {k: t[nkey(k)] for k in range(1, DAYS) if nkey(k) in t}
    days = {k: t[f"day{k}"] for k in range(3, DAYS + 1) if f"day{k}" in t}
    # T1
    r["t1"] = {k: {"bedtimes": [(NAME[d["person"]], d["option"], d["mode"]) for d in bedtimes(n)],
                   "groups": [(g["members"], g.get("far", False), g["outcome"], g["took"], g["lost"])
                              for g in n["groups"]]} for k, n in nights.items() if k >= 3}
    # T2
    big = max(asks, key=lambda a: a["estimate"]) if asks else None
    morning_bounds = [b for b in bounds if re.fullmatch(r"day([3-9]|10)", b["scene"])]
    removed = [b for b in morning_bounds if b["a_variant"] > 0 or b["c_thoughts"] or b["c_lines"] or b["b_lines"]]
    r["t2"] = {"prompts_from_day3": len(asks), "largest": big, "meta_max_estimated": meta.get("max_prompt_tokens_estimated"),
               "bound_calls": len(morning_bounds), "bound_removals": removed}
    # T4
    r["t4"] = {}
    for k in range(4, DAYS + 1):
        if k not in days or k - 1 not in days:
            r["t4"][k] = {"holds": False, "reached": False}
            continue
        old = {act_of(a["option"]) for a in morning_speech(days[k - 1])}
        m = morning_speech(days[k])
        fresh = [a for a in m if act_of(a["option"]) not in old]
        r["t4"][k] = {"of": len(m), "fresh": len(fresh), "holds": bool(m) and 2 * len(fresh) >= len(m), "reached": True,
                      "acts": [(data.clock(a["minute"]), NAME[a["who"]], a["option"], act_of(a["option"]) not in old)
                               for a in m]}
    # T5
    stage3 = [(k, data.clock(e["minute"]), NAME[e["who"]]) for k, d in days.items()
              for e in d["quiet"]["need_events"] if e["need"] == "fast" and e["stage"] == 3]
    runs = {}
    for p in data.ORDER:
        seq = [(k, data.clock(a["minute"]), bool(TIRED.search(a["words"])), a["words"])
               for k in sorted(days) for a in speech(days[k]) if a["who"] == p]
        best = cur = 0
        where = None
        for i, s in enumerate(seq):
            cur = cur + 1 if s[2] else 0
            if cur > best:
                best, where = cur, i
        runs[NAME[p]] = {"speech_acts": len(seq), "with_word": sum(s[2] for s in seq), "longest_run": best,
                         "run_at": [(s[0], s[1], s[3]) for s in seq[where - best + 1:where + 1]] if best >= 2 else []}
    r["t5"] = {"stage3": stage3, "runs": runs}
    # T6
    r["t6_food"], r["t6_loss"] = [], []
    for k, n in nights.items():
        if k < 3 or (k + 1) not in days:
            continue
        home = [g for g in n["groups"] if g["took"] >= 1 and g["lost"] is None]
        if home:
            food = [(data.clock(a["minute"]), NAME[a["who"]], a["option"]) for a in model_acts(days[k + 1])
                    if a["option"] in FOOD or a["option"].startswith("give_")]
            r["t6_food"].append({"night": k, "took": [(g["members"], g["took"], g.get("far", False)) for g in home],
                                 "food_acts": food, "holds": bool(food)})
        before = set(nights[k - 1]["away"]) if (k - 1) in nights else set()
        for x in [q for q in n["away"] if q not in before]:
            others = [q for q in data.ORDER if q != x and q not in n["away"]]
            hits = {}
            for a in speech(days[k + 1]):
                if a["who"] in others and names_them(a["words"], a["who"], x):
                    hits.setdefault(NAME[a["who"]], []).append((data.clock(a["minute"]), a["words"]))
            r["t6_loss"].append({"night": k, "lost": NAME[x], "others": [NAME[q] for q in others], "speakers": hits,
                                 "tested": len(others) >= 2, "holds": len(hits) >= 2})
    # T7
    r["t7"] = {"answers_live": meta["answers_live"], "api_requests": meta["api_requests"],
               "day_asks": {k: (meta.get(f"day{k}_quiet") or {}).get("day_asks") for k in range(3, DAYS + 1)}}
    return r


def verdicts(r):
    out = {}
    trip_nights = [k for k, v in r["t1"].items() if k <= 9 and v["groups"]]
    out["T1"] = ("PASS" if trip_nights else "FAIL") + f" (nights with a trip: {trip_nights})"
    t2 = r["t2"]
    p1 = t2["largest"] is not None and t2["largest"]["estimate"] <= 2600
    p2 = not t2["bound_removals"]
    out["T2"] = ("PASS" if p1 and p2 else "FAIL") + (f" (largest {t2['largest']['estimate']}; "
                                                     f"bound calls {t2['bound_calls']}, removals {len(t2['bound_removals'])})")
    held = [k for k, v in r["t4"].items() if v["holds"]]
    out["T4"] = ("PASS" if len(held) >= 3 else "FAIL") + f" (days that hold: {held})"
    t5 = r["t5"]
    p2 = all(v["longest_run"] < 3 for v in t5["runs"].values())
    out["T5"] = ("PASS" if t5["stage3"] and p2 else "FAIL") + (
        f" (stage 3: {len(t5['stage3'])} crossings; longest runs {({n: v['longest_run'] for n, v in t5['runs'].items()})})")
    fv = "NOT TESTED" if not r["t6_food"] else ("PASS" if all(c["holds"] for c in r["t6_food"]) else "FAIL")
    loss = [c for c in r["t6_loss"] if c["tested"]]
    lv = "NOT TESTED" if not loss else ("PASS" if all(c["holds"] for c in loss) else "FAIL")
    out["T6"] = ("FAIL" if "FAIL" in (fv, lv) else "NOT TESTED" if fv == lv == "NOT TESTED" else "PASS") \
        + f" (food: {fv}; loss: {lv})"
    t7 = r["t7"]
    ok = all(v is not None and v <= 48 for v in t7["day_asks"].values())
    out["T7"] = ("PASS" if t7["answers_live"] <= 450 and ok else "FAIL") + f" (live {t7['answers_live']})"
    return out


def account(t):
    lines = []
    for k in range(3, DAYS + 1):
        if f"day{k}" not in t:
            continue
        d = t[f"day{k}"]
        q = d["quiet"]
        lines.append(f"== day {k}: shelf at 07:00 {d['turns'][0].get('portions', '?') if d['turns'] else '?'}; "
                     f"morning_end {data.clock(q['morning_end'])}; stretches "
                     f"{[(data.clock(s['start']), data.clock(s['end']), s['trigger'], s['asks']) for s in q['stretches']]}; "
                     f"day asks {q['asks']['day']}; away {[NAME[x] for x in d.get('away', [])]}")
        for e in q["log"]:
            if e["kind"] in ("Q5", "Q1") and e["fired"]:
                lines.append(f"  {e['kind']} {data.clock(e['minute'])}: asked {e['asked']}, room {e['room']}, awake "
                             f"{e.get('awake')}, positions {e.get('positions')}, why {e['why']}")
        for e in q["need_events"]:
            if e["need"] == "fast":
                lines.append(f"  fast stage {e['stage']} {data.clock(e['minute'])} {NAME[e['who']]} "
                             f"({e['value']:.1f} h)")
        for a in model_acts(d):
            if a["option"] in FOOD or a["option"].startswith("give_"):
                lines.append(f"  FOOD ACT {data.clock(a['minute'])} {NAME[a['who']]} {a['option']}: {a['words']!r}")
        nk = nkey(k) if k < DAYS else None
        if k < DAYS and nk in t:
            n = t[nk]
            lines.append(f"== night {k}: portions {n['portions_before']} -> {n['portions_after']}; away {n['away']}; "
                         f"far {n.get('far')}; leavers {n['leavers']}")
            for b in bedtimes(n):
                lines.append(f"  bedtime {NAME[b['person']]}: {b['option']} (options {b['options']}; mode "
                             f"{b['mode']}); reason {b.get('reason')!r}")
            for x in n["decisions"]:
                if x["ask"] != "bedtime":
                    lines.append(f"  {x['ask']} {NAME[x['person']]}: {x['option']} say {x.get('say')!r}")
            for g in n["groups"]:
                lines.append(f"  group {g['members']} far={g.get('far', False)} house={g.get('house')} street "
                             f"{g['street']} found {g['found']} took {g['took']} lost {g['lost']}: {g['outcome']}")
    return lines


def main():
    args = sys.argv[1:]
    seed = 2
    if args and args[0] in ("--account", "--lines"):
        d = args[1] if len(args) > 1 else "runs/v21"
        t, _ = load(d, seed)
        if args[0] == "--account":
            print("\n".join(account(t)))
        else:
            for k in range(3, DAYS + 1):
                if f"day{k}" in t:
                    for a in speech(t[f"day{k}"]):
                        print(f"d{k} {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}]: {a['words']}")
        return
    d = args[0] if args else "runs/v21"
    cache = args[1] if len(args) > 1 else "cache/v21"
    if len(args) > 2:
        seed = int(args[2])
    asks, bounds, parts, code = replay_records(cache, seed)
    asks3 = [a for a in asks if SCENES.index(a["scene"]) >= SCENES.index("day3")]
    print(f"seed {seed}: replay exit {code}, prompts {len(asks)}, from day 3 on {len(asks3)}")
    t, meta = load(d, seed)
    r = scores(t, meta, asks3, bounds)
    for k, v in r.items():
        print(f"  {k.upper()} {json.dumps(v, ensure_ascii=False)}")
    print("\nPROMPTS per scene: n; largest estimate (who); largest budget / most cut today / before (day and night)")
    for sc in SCENES[SCENES.index("day3"):]:
        a = [x for x in asks3 if x["scene"] == sc]
        p = [x for x in parts if x["scene"] == sc]
        if not a:
            continue
        big = max(a, key=lambda x: x["estimate"])
        extra = ""
        if p:
            extra = (f"; budget max {max(x['budget'] for x in p)}; cut today max {max(x['cut_today'] for x in p)}, "
                     f"before max {max(x['cut_before'] for x in p)}; over 1400: "
                     f"{sum(1 for x in p if x['budget'] > world.PROMPT_TOKEN_BUDGET)}")
        print(f"  {sc}: {len(a)} prompts; largest {big['estimate']} ({big['who']}){extra}")
    print("\nMEMORY BOUND per morning scene: calls; mornings with A shortened; C thoughts, C lines, B lines removed")
    for k in range(3, DAYS + 1):
        b = [x for x in bounds if x["scene"] == f"day{k}"]
        if b:
            print(f"  day{k}: {len(b)} calls; {sum(x['a_variant'] > 0 for x in b)} / {sum(x['c_thoughts'] for x in b)} / "
                  f"{sum(x['c_lines'] for x in b)} / {sum(x['b_lines'] for x in b)}")
    print("\nSUMMARY " + d)
    for g, x in verdicts(r).items():
        print(f"{g} {x}")


if __name__ == "__main__":
    main()
