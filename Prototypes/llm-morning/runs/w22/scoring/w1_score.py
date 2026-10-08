"""Scores reports/days_v22_plan.md's W1-1 to W1-11, read only, no API. Run from Prototypes/llm-morning/ with
GEMINI_API_KEY unset.

    python runs/w22/scoring/w1_score.py                      runs/v22 and cache/v22, seed 2
    python runs/w22/scoring/w1_score.py --control            runs/v21 and cache/v21: v21's column of the plan's table
    python runs/w22/scoring/w1_score.py DIR CACHE_FILE BASE  another run (a check of the script); BASE: the entries of
                                                             the cache file that came from cache/v16 (147; 0 for a fake)
    python runs/w22/scoring/w1_score.py --account [DIR]      the day and night account (weather, water, bodies, bedtimes,
                                                             trips, rain) for the report
    python runs/w22/scoring/w1_score.py --lines [DIR]        every speech act of days 3-10
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import data                                           # noqa: E402
import mind                                           # noqa: E402
import weather                                        # noqa: E402
import world                                          # noqa: E402
from talk import act_of                               # noqa: E402

SEED = 2
DAYS = 10
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
DAY_END = 840
FROZEN = re.compile(r"(too weak|cannot|can't|can not|unable|barely|no strength)\b[^.;]{0,40}?\b"
                    r"(stand|walk|move|go|make it|get up|leave|carry)\b", re.I)
WATER = re.compile(r"\b(water|thirst\w*|drink\w*|rain\w*|bath)\b", re.I)
NOWATER = re.compile(r"\bno (more )?water\b|\bwater is (gone|finished)\b|\bout of water\b|\bwater (has )?run out\b", re.I)
CAN = re.compile(r"\bthe can\b|\btook\b|\bstole\b|\bstolen\b|\bsteal\w*|\blie[ds]?\b|\blying\b|\bliar\b", re.I)
RAINWORDS = re.compile(r"\b(rain|catch|bucket|bin|pots?)\b", re.I)
FORBID = re.compile(r"impossible|cannot|can't|unable|barely (stand|walk|move)", re.I)
WATER_RULES = ("ration_water", "save_water")


def nkey(k):
    return "night" if k == 1 else f"night{k}"


def load(d):
    name = f"daniel_ate_it-seed{SEED}"
    t = json.load(open(os.path.join(d, f"{name}.transcript.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(d, f"{name}.meta.json"), encoding="utf-8"))
    return t, meta


def acts(day):
    return sorted((a for turn in day["turns"] for a in turn["acts"]), key=lambda a: tuple(a["decided_at"]))


def model_acts(day):
    return [a for a in acts(day) if a["mode"] == "model"]


def speech(day):
    return [a for a in model_acts(day) if a["words"]]


def bedtimes(night):
    return [d for d in night["decisions"] if d["ask"] == "bedtime"]


def days_of(t):
    return {k: t[f"day{k}"] for k in range(3, DAYS + 1) if f"day{k}" in t}


def nights_of(t):
    return {k: t[nkey(k)] for k in range(3, DAYS) if nkey(k) in t}


def clk(k, minute):
    return f"day {k} {data.clock(minute)}"


# ---------- the prompts, from the cache file ----------
def live_prompts(cache_file, base):
    """(kind, person, estimate, api_count, text) for each live prompt (the entries after the `base` first ones)."""
    c = json.load(open(cache_file, encoding="utf-8"))
    out = []
    for key in list(c)[base:]:
        p = c[key]["prompt"]
        if "Your options:" not in p:
            kind, system = "mind", mind.NIGHT_MIND_SYSTEM
        elif "Now it is night" in p:
            kind, system = "night", world.NIGHT_SYSTEM
        else:
            kind, system = "day", world.SYSTEM
        who = re.match(r"You are (\w+),", p)
        out.append({"kind": kind, "who": who.group(1) if who else "?", "estimate": world.estimate_tokens(system + p),
                    "api": int(c[key].get("prompt_tokens") or 0), "text": p})
    return out


# ---------- the rules ----------
def w11(t):
    """Outward acts of nights 3-9: per night and leaver, 1 for went_out, else 1 for got_up or at_door."""
    ev = [e for e in t["chronicle"]["events"] if e["kind"] in ("went_out", "got_up", "at_door") and re.fullmatch(r"N\d+", e["scene"])]
    per = {}
    for e in ev:
        k = int(e["scene"][1:])
        if not 3 <= k <= 9:
            continue
        who = set(e["members"] or []) | ({e["actor"]} if e["kind"] == "got_up" or not e["members"] else set())
        for q in who:
            cur = per.setdefault((k, q), set())
            cur.add(e["kind"])
    items = {key: ("went_out" if "went_out" in v else "got_up/at_door") for key, v in per.items()}
    nights = sorted({k for k, _ in items})
    return {"count": len(items), "nights": nights,
            "items": [(k, NAME[q], kind) for (k, q), kind in sorted(items.items())]}


def w12(t):
    rows = []
    for k, n in nights_of(t).items():
        for b in bedtimes(n):
            rows.append((k, NAME[b["person"]], b["option"], b.get("reason") or "", bool(FROZEN.search(b.get("reason") or ""))))
    return {"of": len(rows), "frozen": sum(r[4] for r in rows), "rows": rows}


def w13(t):
    rows = [(k, NAME[b["person"]], b["option"]) for k, n in nights_of(t).items() for b in bedtimes(n)
            if b["option"] in ("go_next_door", "go_further")]
    return {"count": len(rows), "rows": rows}


def w14(t):
    by_day, lines = {}, []
    for k, d in days_of(t).items():
        hits = [a for a in speech(d) if WATER.search(a["words"])]
        by_day[k] = len(hits)
        lines += [(k, data.clock(a["minute"]), NAME[a["who"]], a["option"], a["words"]) for a in hits]
    return {"acts": sum(by_day.values()), "by_day": by_day, "days": sum(1 for v in by_day.values() if v), "lines": lines}


def spells_by_day():
    w = weather.Weather(SEED)
    out = []
    for k in range(3, DAYS + 1):
        for a, b, _ in w.day(k)["spells"]:
            dm = a - (k - 1) * 1440
            if 0 <= dm < DAY_END:
                out.append((k, dm, a, b))
    return sorted(out)


def w15(t):
    days = days_of(t)
    spells = spells_by_day()
    has_log = any("rain" in d.get("quiet", {}) for d in days.values())
    res = {"spells": [], "has_weather_record": has_log}
    for k, dm, a, b in spells:
        d = days.get(k)
        row = {"day": k, "start": data.clock(dm), "minute": dm, "reached": d is not None}
        if d is not None and has_log:
            q = d["quiet"]
            away = set(d.get("away", []))
            resting = {s["who"] for s in q["spans"] if s["routine"] == "rest" and s["start"] <= dm < s["end"]}
            must = [p for p in data.ORDER if p not in away and p not in resting]
            ev = [r for r in q["rain"] if r["minute"] == dm]
            heard = set(ev[0]["heard"]) if ev else set()
            row.update(must=[NAME[p] for p in must], heard=[NAME[p] for p in sorted(heard, key=data.ORDER.index)],
                       resting=[NAME[p] for p in sorted(resting, key=data.ORDER.index)], away=[NAME[p] for p in away],
                       event=bool(ev), all_heard=bool(ev) and all(p in heard for p in must),
                       q6=[(e["fired"], e["why"], e["asked"]) for e in q["log"] if e["kind"] == "Q6" and e["minute"] == dm])
        res["spells"].append(row)
    done = [r for r in res["spells"] if r["reached"] and has_log]
    res["a_all"] = bool(done) and all(r["all_heard"] for r in done)
    # (b) the first qualifying spell
    res["b"] = None
    if done:
        r = done[0]
        d = days[r["day"]]
        q = d["quiet"]
        stretch = next((s for s in q["stretches"] if s["trigger"] == "Q6" and s["start"] == r["minute"]), None)
        if stretch:
            lo, hi, how = stretch["start"], stretch["end"], "its Q6 stretch"
        else:
            lo, hi, how = r["minute"], r["minute"] + 30, "30 minutes from the spell's start (Q6 did not play it)"
        sel = [a for a in model_acts(d) if lo <= a["minute"] < hi]
        hit = [(data.clock(a["minute"]), NAME[a["who"]], a["option"], a["words"]) for a in sel
               if a["option"] == "collect_rain" or (a["words"] and RAINWORDS.search(a["words"]))]
        res["b"] = {"day": r["day"], "window": how, "from": data.clock(lo), "to": data.clock(hi), "acts": len(sel),
                    "hits": hit, "holds": bool(hit)}
    res["collect_rain"] = [(k, data.clock(a["minute"]), NAME[a["who"]]) for k, d in days.items() for a in model_acts(d)
                           if a["option"] == "collect_rain"]
    res["rain_out"] = [(k, NAME[b["person"]]) for k, n in nights_of(t).items() for b in bedtimes(n) if b["option"] == "rain_out"]
    return res


def store_at(days, k, minute):
    """(entry at or before, the first entry after) of the World's water log, as (minute label, tap + rain)."""
    flat = []
    for kk in sorted(days):
        for e in days[kk]["quiet"].get("water", []):
            flat.append(((kk, e[0]), e[1] + e[2]))
    before = [x for x in flat if x[0] <= (k, minute)]
    after = [x for x in flat if x[0] > (k, minute)]
    return (before[-1] if before else None), (after[0] if after else None)


def w16(t):
    days = days_of(t)
    has_log = any(d.get("quiet", {}).get("water") for d in days.values())
    texts = []
    for k, d in days.items():
        texts += [(k, a["minute"], f"day speech {NAME[a['who']]} [{a['option']}]", a["words"]) for a in speech(d)]
    for k, n in nights_of(t).items():
        for x in n["decisions"]:
            for field in ("reason", "say"):
                if x.get(field):
                    texts.append((k, DAY_END, f"night {k} {x['ask']} {NAME[x['person']]} {field}", x[field]))
    claims = [x for x in texts if NOWATER.search(x[3])]
    viol, unsure = [], []
    for k, minute, who, text in claims:
        if not has_log:
            unsure.append((k, data.clock(minute), who, text, "no water record in this run"))
            continue
        b, a = store_at(days, k, minute)
        b_pos = b is not None and b[1] > 0
        a_pos = a is None or a[1] > 0
        row = (k, data.clock(minute), who, text, f"before {b}, after {a}")
        if b_pos and a_pos:
            viol.append(row)
        elif b_pos != a_pos:
            unsure.append(row)
    return {"claims": len(claims), "violations": viol, "unsure": unsure, "has_water_record": has_log}


def w17(t):
    days = days_of(t)
    flat = [((kk, e[0]), e[1] + e[2]) for kk in sorted(days) for e in days[kk]["quiet"].get("water", [])]
    drop = next((x for x in flat if x[1] < 50), None)
    res = {"has_water_record": bool(flat), "drop": drop, "acts": []}
    if drop is None:
        res["tested"] = False
        return res
    k = drop[0][0]
    res["k"] = k
    res["tested"] = k <= 9
    for kk, d in days.items():
        for a in model_acts(d):
            if a["option"] in WATER_RULES:
                res["acts"].append((kk, a["minute"], data.clock(a["minute"]), NAME[a["who"]], a["option"], a["words"]))
    res["holds"] = any((x[0], x[1]) <= (k + 1, DAY_END) for x in res["acts"])
    return res


def w18(t, meta, prompts):
    est = {kind: max((p for p in prompts if p["kind"] == kind), key=lambda p: p["estimate"], default=None)
           for kind in ("day", "night", "mind")}
    big = max(prompts, key=lambda p: p["estimate"]) if prompts else None
    api = max(prompts, key=lambda p: p["api"]) if prompts else None
    return {"answers_live": meta["answers_live"], "api_requests": meta["api_requests"],
            "day_asks": {k: (meta.get(f"day{k}_quiet") or {}).get("day_asks") for k in range(3, DAYS + 1)},
            "prompts": len(prompts), "by_kind": {kd: sum(1 for p in prompts if p["kind"] == kd) for kd in ("day", "night", "mind")},
            "largest": (big["estimate"], big["kind"], big["who"]) if big else None,
            "largest_by_kind": {kd: (p["estimate"], p["who"]) for kd, p in est.items() if p},
            "largest_api_count": (api["api"], api["kind"], api["who"]) if api else None}


def w19(prompts):
    lines = [x for p in prompts for x in p["text"].splitlines() if x.startswith("Your body:")]
    bad = [x for x in lines if FORBID.search(x)]
    counts = {}
    for x in lines:
        counts[x] = counts.get(x, 0) + 1
    return {"prompts": len(prompts), "body_lines": len(lines), "distinct": len(counts), "matches": len(bad),
            "matching": sorted({x for x in bad}), "counts": sorted(counts.items(), key=lambda kv: -kv[1])}


def w110(t):
    sp = [a for d in days_of(t).values() for a in speech(d)]
    hits = [a for a in sp if CAN.search(a["words"])]
    return {"can": len(hits), "of": len(sp), "share": (len(hits) / len(sp)) if sp else None}


def w111(t):
    days = days_of(t)
    evs = [e for e in t["chronicle"]["events"] if e["kind"] == "went_out" and re.fullmatch(r"N\d+", e["scene"])]
    rows = []
    for e in evs:
        k = int(e["scene"][1:])
        if not 3 <= k <= 9:
            continue
        for q in e["members"] or [e["actor"]]:
            reason = next(((b.get("reason") or "") for b in bedtimes(t[nkey(k)]) if b["person"] == q), "")
            said = [(data.clock(a["minute"]), a["option"], a["words"]) for a in speech(days[k])
                    if k in days and a["who"] == q and act_of(a["option"])[0] in world.TRIP_KINDS] if k in days else []
            water_said = [x for x in said if WATER.search(x[2])]
            rows.append({"night": k, "leaver": NAME[q], "reason": reason, "reason_water": bool(WATER.search(reason)),
                         "trip_words": said, "trip_words_water": water_said,
                         "holds": bool(WATER.search(reason)) or bool(water_said)})
    return {"nights": sorted({r["night"] for r in rows}), "rows": rows, "tested": bool(rows),
            "holds": any(r["holds"] for r in rows)}


# ---------- verdicts ----------
def verdicts(r):
    v = {}
    a = r["w11"]
    v["W1-1"] = ("PASS" if a["count"] >= 3 and len(a["nights"]) >= 2 else "FAIL") + \
        f" ({a['count']} outward acts on nights {a['nights']}: {a['items']})"
    b = r["w12"]
    v["W1-2"] = ("PASS" if b["frozen"] <= 8 else "FAIL") + f" ({b['frozen']} of {b['of']} bedtime reasons match FROZEN)"
    c = r["w13"]
    v["W1-3"] = ("PASS" if c["count"] >= 2 else "FAIL") + f" ({c['count']} bedtime go_next_door or go_further: {c['rows']})"
    d = r["w14"]
    v["W1-4"] = ("PASS" if d["days"] >= 4 else "FAIL") + f" ({d['acts']} WATER speech acts on {d['days']} of 8 days; by day {d['by_day']})"
    e = r["w15"]
    if not e["spells"] or not any(s["reached"] for s in e["spells"]) or not e["has_weather_record"]:
        v["W1-5"] = "NOT TESTED" + (" (no weather record in this run)" if not e["has_weather_record"] else
                                    " (no qualifying rain spell reached)") + \
            f"; collect_rain {len(e['collect_rain'])}, rain_out {len(e['rain_out'])}"
    else:
        bb = e["b"]
        ok = e["a_all"] and bb is not None and bb["holds"]
        v["W1-5"] = ("PASS" if ok else "FAIL") + (f" ((a) {'100%' if e['a_all'] else 'NOT 100%'} over "
                                                  f"{sum(1 for s in e['spells'] if s['reached'])} spells; (b) {'holds' if bb and bb['holds'] else 'does not hold'}; "
                                                  f"collect_rain {len(e['collect_rain'])}, rain_out {len(e['rain_out'])})")
    f = r["w16"]
    v["W1-6"] = ("PASS" if len(f["violations"]) <= 1 else "FAIL") + \
        f" ({f['claims']} NOWATER claims; {len(f['violations'])} while the store was > 0; {len(f['unsure'])} unsure)"
    g = r["w17"]
    if not g["has_water_record"] or not g.get("tested"):
        v["W1-7"] = "NOT TESTED (" + ("no water record in this run" if not g["has_water_record"] else
                                      "the drinking store never fell below 50 L by day 9") + ")"
    else:
        v["W1-7"] = ("PASS" if g["holds"] else "FAIL") + f" (below 50 L at {g['drop']}; water-rule acts {g['acts']})"
    h = r["w18"]
    okd = all(x is not None and x <= 56 for x in h["day_asks"].values())
    v["W1-8"] = ("PASS" if h["answers_live"] <= 450 and okd and h["largest"][0] <= 2600 else "FAIL") + \
        f" (live {h['answers_live']}; day asks {h['day_asks']}; largest estimate {h['largest']})"
    i = r["w19"]
    v["W1-9"] = ("PASS" if i["matches"] == 0 else "FAIL") + f" ({i['matches']} of {i['body_lines']} body lines match)"
    j = r["w110"]
    v["W1-10"] = ("PASS" if j["share"] is not None and j["share"] <= 0.2 else "FAIL") + \
        f" ({j['can']} of {j['of']} = {100 * j['share']:.1f}%)"
    m = r["w111"]
    v["W1-11"] = ("NOT TESTED (no night has a went_out)" if not m["tested"] else
                  ("PASS" if m["holds"] else "FAIL") + f" (went_out nights {m['nights']})")
    return v


# ---------- the account and the lines ----------
def body_of_decisions(t, prompts):
    """The 'Your body:' line of each model-chosen night decision, by (night, person, ask, order): the night prompts of
    the run, in the order they were asked, are the night decisions with mode model, in order (checked by name)."""
    npr = [p for p in prompts if p["kind"] == "night"]
    dec = [(k, x) for k, n in sorted(nights_of(t).items()) for x in n["decisions"] if x["mode"] == "model"]
    npr = npr[-len(dec):] if dec else []
    if len(npr) != len(dec) or any(NAME[x["person"]] != p["who"] for (_, x), p in zip(dec, npr)):
        return {}
    return {(k, x["person"], x["ask"]): next((l for l in p["text"].splitlines() if l.startswith("Your body:")), "")
            for (k, x), p in zip(dec, npr)}


def account(t, prompts=()):
    body = body_of_decisions(t, list(prompts))
    shelf = {sc["id"]: sc for sc in t["chronicle"]["scenes"] if sc["kind"] == "day"}
    out = []
    days = days_of(t)
    w = weather.Weather(SEED)
    for k in range(3, DAYS + 1):
        if k not in days:
            continue
        d = days[k]
        q = d["quiet"]
        x = w.day(k)
        out.append(f"== day {k}: weather {'wet %.1f mm' % x['mm'] if x['wet'] else 'dry'}, indoors {x['indoor']:.1f} C; "
                   f"shelf {shelf.get(f'D{k}', {}).get('start', {}).get('shelf', '?')}; morning_end {data.clock(q['morning_end'])}; "
                   f"day asks {q['asks']['day']}; away {[NAME[p] for p in d.get('away', [])]}")
        out.append("  stretches: " + str([(data.clock(s['start']), data.clock(s['end']), s['trigger'], s['asks']) for s in q["stretches"]]))
        for e in q.get("water", []):
            out.append(f"  water {data.clock(e[0])}: tap {e[1]:.1f} L + bin {e[2]:.1f} L; level {e[3]}; bin out {e[4]}")
        for e in q.get("rain", []):
            out.append(f"  rain heard {data.clock(e['minute'])}: {[NAME[p] for p in e['heard']]}")
        for e in q["log"]:
            if e["kind"] in ("Q5", "Q6", "Q1") and e["fired"]:
                out.append(f"  {e['kind']} {data.clock(e['minute'])}: asked {e['asked']}, room {e['room']}, why {e['why']}")
        for e in q["need_events"]:
            out.append(f"  {e['need']} stage {e['stage']} {data.clock(e['minute'])} {NAME[e['who']]} ({e['value']})")
        th = q.get("thirst", {})
        if isinstance(th, dict):
            for p, rows in th.items():
                if rows:
                    last = rows[-1]
                    out.append(f"  thirst {NAME[p]}: at {data.clock(last[0])} short {last[1]:.2f} L, stage {last[2]}")
        for a in model_acts(d):
            if a["option"] in WATER_RULES or a["option"] == "collect_rain" or a["option"] in ("eat", "eat_given", "share") \
                    or a["option"].startswith("give_"):
                out.append(f"  ACT {data.clock(a['minute'])} {NAME[a['who']]} {a['option']}: {a['words']!r}")
        if k < DAYS and nkey(k) in t:
            n = t[nkey(k)]
            out.append(f"== night {k}: away {n['away']}; far {n.get('far')}; leavers {n['leavers']}")
            for b in bedtimes(n):
                out.append(f"  bedtime {NAME[b['person']]}: {b['option']} (options {b['options']}; mode {b['mode']}); "
                           f"reason {b.get('reason')!r}")
                if body.get((k, b["person"], "bedtime")):
                    out.append("      " + body[(k, b["person"], "bedtime")])
            for xx in n["decisions"]:
                if xx["ask"] != "bedtime":
                    out.append(f"  {xx['ask']} {NAME[xx['person']]}: {xx['option']} say {xx.get('say')!r} reason {xx.get('reason')!r}")
            for g in n["groups"]:
                out.append(f"  group {g['members']} far={g.get('far', False)} house={g.get('house')} street {g['street']} "
                           f"found {g['found']} took {g['took']} lost {g['lost']} water {g.get('water')}: {g['outcome']}")
    return out


def lines(t):
    return [f"d{k} {data.clock(a['minute'])} {NAME[a['who']]} [{a['option']}]: {a['words']}"
            for k, d in days_of(t).items() for a in speech(d)]


# ---------- the control column ----------
CONTROL = {"W1-1": "1", "W1-2": "16 of 28", "W1-3": "1", "W1-4": "0 acts, 0 days", "W1-5": "no weather",
           "W1-6": "0 (no claims)", "W1-7": "no water", "W1-8": "337; days <= 40; 2435",
           "W1-9": "stage 3 lines match", "W1-10": "63 of 245 = 25.7%", "W1-11": "no trip"}


def control_check(r):
    h = r["w18"]
    got = {"W1-1": str(r["w11"]["count"]), "W1-2": f"{r['w12']['frozen']} of {r['w12']['of']}",
           "W1-3": str(r["w13"]["count"]), "W1-4": f"{r['w14']['acts']} acts, {r['w14']['days']} days",
           "W1-5": "no weather" if not r["w15"]["has_weather_record"] else "weather",
           "W1-6": f"{len(r['w16']['violations'])} ({r['w16']['claims']} claims)" if r["w16"]["claims"] else "0 (no claims)",
           "W1-7": "no water" if not r["w17"]["has_water_record"] else "water",
           "W1-8": f"{h['answers_live']}; days <= {max(x for x in h['day_asks'].values() if x)}; {h['largest'][0]}",
           "W1-9": "stage 3 lines match" if r["w19"]["matches"] else "no match",
           "W1-10": f"{r['w110']['can']} of {r['w110']['of']} = {100 * r['w110']['share']:.1f}%",
           "W1-11": "no trip" if not r["w111"]["tested"] else "trips"}
    return [(k, CONTROL[k], got[k], CONTROL[k] == got[k]) for k in CONTROL]


def score(d, cache_file, base):
    t, meta = load(d)
    prompts = live_prompts(cache_file, base)
    return {"w11": w11(t), "w12": w12(t), "w13": w13(t), "w14": w14(t), "w15": w15(t), "w16": w16(t), "w17": w17(t),
            "w18": w18(t, meta, prompts), "w19": w19(prompts), "w110": w110(t), "w111": w111(t)}


def main():
    args = sys.argv[1:]
    d, cache_file, base = "runs/v22", os.path.join("cache", "v22", "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"), 147
    if args and args[0] in ("--account", "--lines"):
        dd = args[1] if len(args) > 1 else d
        cf, bs = (args[2], int(args[3])) if len(args) > 3 else (cache_file, base)
        t, _ = load(dd)
        print("\n".join(account(t, live_prompts(cf, bs)) if args[0] == "--account" else lines(t)))
        return
    control = bool(args) and args[0] == "--control"
    if control:
        d, cache_file = "runs/v21", os.path.join("cache", "v21", "gemini-3.5-flash-lite-daniel_ate_it-seed2.json")
    elif args:
        d, cache_file, base = args[0], args[1], int(args[2])
    r = score(d, cache_file, base)
    for k, v in r.items():
        print(f"  {k.upper()} {json.dumps(v, ensure_ascii=False, default=str)}")
    print("\nSUMMARY " + d)
    for g, x in verdicts(r).items():
        print(f"{g} {x}")
    if control:
        print("\nCONTROL COLUMN (plan's table against this run)")
        ok = True
        for k, want, got, same in control_check(r):
            ok &= same
            print(f"{k}: table {want!r} | scorer {got!r} | {'MATCH' if same else 'DIFFERENT'}")
        print("ALL MATCH" if ok else "SOME DIFFER")


if __name__ == "__main__":
    main()
