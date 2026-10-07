"""Scores reports/days_v17_plan.md's D1 to D7 by its counting rules, read only, no API.

    python runs/v17/scoring/scripts/score.py d6 v16      N11 by P2's rule on v16's day 3s (the check: 3 of 3)
    python runs/v17/scoring/scripts/score.py all v17     every prediction on v17
    python runs/v17/scoring/scripts/score.py lines v17   asks per stretch, and every spoken line after the morning

Run from Prototypes/llm-morning/.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import data                                          # noqa: E402
from talk import act_of                              # noqa: E402

MODEL = "gemini-3.5-flash-lite"
NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
NEED = ("weak", "dizzy", "faint", "head spin")
TIRED = ("tired", "exhausted", "weary", "sleep", "weak", "dizzy", "faint")


def clock(m):
    return data.clock(m)


def load(v, seed):
    name = f"daniel_ate_it-seed{seed}"
    t = json.load(open(f"runs/{v}/{name}.transcript.json", encoding="utf-8"))
    meta = json.load(open(f"runs/{v}/{name}.meta.json", encoding="utf-8"))
    return t, meta


def acts(day):
    return [a for turn in day["turns"] for a in turn["acts"]]


def model_acts(day):
    return sorted((a for a in acts(day) if a["mode"] == "model"), key=lambda a: tuple(a["decided_at"]))


def speech(a):
    return a["mode"] == "model" and bool(a["words"])


def in_stretch(a, s):
    return s["start"] <= a["minute"] < s["end"]


# ---------- D6: N11 by P2's rule ----------
def kind6(option):
    k, target = act_of(option)
    if option in ("volunteer", "still_going", "propose_trip") or k in ("volunteer", "propose"):
        return "volunteer kind", None
    if option == "nobody_goes" or k == "object":
        return "against kind", target
    if k in ("accuse", "confront", "reassure", "ask", "deny"):
        return k, target
    return None, target


def convo_of(day, a):
    """(room, start minute) of the conversation an act falls in, or None."""
    start = None
    for e in day["convo_log"]:
        if e["room"] != a["room"] or e["minute"] > a["minute"]:
            continue
        if e["what"] == "started":
            start = e["minute"]
        elif e["what"] == "ended" and e["minute"] <= a["minute"]:
            start = None
    return (a["room"], start) if start is not None else None


def n11(day, clause=True):
    """Every run that counts on this day: (who, kind, target, minutes). clause=False drops P2's target clause (the
    design's §9.2 "N11-mech")."""
    found = []
    ms = model_acts(day)
    for p in data.ORDER:
        mine = [a for a in ms if a["who"] == p]
        for i in range(len(mine) - 2):
            run = mine[i:i + 3]
            kinds = [kind6(a["option"]) for a in run]
            if kinds[0][0] is None or len(set(kinds)) != 1:
                continue
            convos = [convo_of(day, a) for a in run]
            if None in convos or len(set(convos)) != 1:
                continue
            kind, target = kinds[0]
            if clause and target is not None and target in data.ORDER:
                first, last = tuple(run[0]["decided_at"]), tuple(run[-1]["decided_at"])
                theirs = {act_of(a["option"])[0] for a in ms
                          if a["who"] == target and first <= tuple(a["decided_at"]) <= last}
                if len(theirs) > 1:
                    continue
            found.append((NAME[p], kind, NAME.get(target, target or "everyone"),
                          [clock(a["minute"]) for a in run]))
    return found


# ---------- the cache answers of day 3 (D4) ----------
def now_minute(prompt):
    m = re.search(r"^Now, (?:minute (\d+)|(\d\d):(\d\d)),", prompt, flags=re.M)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else int(m.group(2)) * 60 + int(m.group(3)) - data.DAY_START


def new_answers(v, seed):
    name = f"daniel_ate_it-seed{seed}"
    old = json.load(open(f"cache/v16/{MODEL}-{name}.json", encoding="utf-8"))
    new = json.load(open(f"cache/{v}/{MODEL}-{name}.json", encoding="utf-8"))
    out = []
    for k, e in new.items():
        if k in old:
            continue
        who = re.match(r"You are (\w+),", e["prompt"]).group(1).lower()
        try:
            ans = json.loads(e["response"])
        except ValueError:
            ans = {}
        out.append({"who": who, "minute": now_minute(e["prompt"]), "answer": ans})
    return out


def fasting(day, pid, minute):
    log = [x for x in day["quiet"]["needs"][pid] if x[0] <= minute]
    m0, f0 = log[-1][0], log[-1][1]
    ate = [a["minute"] for a in acts(day) if a["who"] == pid and a["option"] in ("eat", "eat_given", "share")
           and m0 < a["minute"] <= minute]
    if ate:
        m0, f0 = max(ate), 0.0
    return f0 + (minute - m0) / 60 * data.PEOPLE[pid]["hunger_rate"]


def has(text, words):
    t = (text or "").lower()
    return [w for w in words if w in t]


# ---------- per seed ----------
def seed_scores(v, seed):
    t, meta = load(v, seed)
    day = t["day3"]
    q = day["quiet"]
    st = q["stretches"]
    morning, later = st[0], st[1:]
    ms = model_acts(day)
    out = {"seed": seed, "meta": meta}
    # D1
    out["d1"] = [(s["trigger"], clock(s["start"]), sum(1 for a in ms if in_stretch(a, s) and speech(a))) for s in later]
    # D2
    pairs = {act_of(a["option"]) for a in ms if in_stretch(a, morning) and speech(a)}
    if later:
        sp = [a for a in ms if in_stretch(a, later[0]) and speech(a)]
        fresh = [a for a in sp if act_of(a["option"]) not in pairs]
        out["d2"] = {"stretch": (later[0]["trigger"], clock(later[0]["start"]), clock(later[0]["end"])),
                     "speech": [(NAME[a["who"]], clock(a["minute"]), a["option"], act_of(a["option"]) not in pairs)
                                for a in sp],
                     "fresh": len(fresh), "of": len(sp),
                     "holds": bool(sp) and 2 * len(fresh) >= len(sp)}
    else:
        out["d2"] = {"stretch": None, "speech": [], "fresh": 0, "of": 0, "holds": False}
    out["morning_pairs"] = sorted(f"{k}:{x}" for k, x in pairs)
    # D3
    late = [a for a in ms if a["minute"] >= 540]
    out["d3"] = {"last_model_act": clock(ms[-1]["minute"]) if ms else None,
                 "at_or_after_1600": [(NAME[a["who"]], clock(a["minute"]), a["option"]) for a in late]}
    # D4
    answers = new_answers(v, seed)
    hits, unmatched = [], 0
    for a in ms:
        cands = [x for x in answers if x["who"] == a["who"] and x["minute"] == a["minute"]
                 and x["answer"].get("option") == a["option"]]
        if not cands:
            unmatched += 1
            continue
        ans = cands[0]["answer"]
        words = sorted(set(has(ans.get("feeling"), NEED) + has(ans.get("reason"), NEED) + has(a["words"], NEED)))
        if words:
            f = fasting(day, a["who"], a["minute"])
            hits.append({"who": NAME[a["who"]], "minute": clock(a["minute"]), "words": words,
                         "fasting": round(f, 2), "ok": f >= 48, "feeling": ans.get("feeling"),
                         "reason": ans.get("reason"), "said": a["words"]})
    out["d4"] = {"hits": hits, "model_acts": len(ms), "answers_new": len(answers), "unmatched": unmatched}
    # D5
    worst = {}
    for p in data.ORDER:
        n = best = 0
        for a in (x for x in ms if x["who"] == p):
            n = n + 1 if has(a["words"], TIRED) else 0
            best = max(best, n)
        worst[NAME[p]] = best
    out["d5"] = {"longest_run": worst,
                 "acts_with_words": [(NAME[a["who"]], clock(a["minute"]), has(a["words"], TIRED)) for a in ms
                                     if has(a["words"], TIRED)]}
    # D6
    out["d6"] = n11(day)
    # D7
    out["d7"] = {"day3_asks": meta["day3_asks"], "answers_live": meta["answers_live"],
                 "api_requests": meta["api_requests"]}
    return out


def main():
    what, v = sys.argv[1], sys.argv[2]
    if what == "d6":
        n = 0
        for seed in (1, 2, 3):
            t, _ = load(v, seed)
            runs = n11(t["day3"])
            n += bool(runs)
            print(f"{v} seed {seed} day 3: N11 {'present' if runs else 'absent'}: {runs}")
        print(f"{v}: N11 on {n} of 3 days")
        return
    if what == "lines":
        for seed in (1, 2, 3):
            t, meta = load(v, seed)
            day = t["day3"]
            q = day["quiet"]
            print(f"## seed {seed}: morning_end {clock(q['morning_end'])}; asks {q['asks']}")
            for s in q["stretches"]:
                n = sum(1 for rec in day["turns"] if s["start"] <= rec["minute"] < s["end"]
                        for a in rec["acts"] if a["mode"] == "model")
                print(f"  stretch {clock(s['start'])} to {clock(s['end'])} ({s['trigger']}, {s['room']}): "
                      f"{s['asks']} asks; {n} model acts")
            for a in sorted(acts(day), key=lambda a: tuple(a["decided_at"])):
                if a["minute"] >= q["morning_end"] and a["words"]:
                    print(f"  {clock(a['minute'])} {NAME[a['who']]} ({a['option']}, {a['room']}): \"{a['words']}\"")
        return
    res = [seed_scores(v, s) for s in (1, 2, 3)]
    print(json.dumps([{k: r[k] for k in r if k != "meta"} for r in res], ensure_ascii=False, indent=1))
    d1 = all(any(n for _, _, n in r["d1"]) for r in res)
    d2 = sum(r["d2"]["holds"] for r in res)
    d3 = sum(bool(r["d3"]["at_or_after_1600"]) for r in res)
    hits = [h for r in res for h in r["d4"]["hits"]]
    ok = sum(h["ok"] for h in hits)
    d5 = all(n < 3 for r in res for n in r["d5"]["longest_run"].values())
    d6 = sum(bool(r["d6"]) for r in res)
    asks = [r["d7"]["day3_asks"] for r in res]
    live = sum(r["d7"]["answers_live"] for r in res)
    print("\nSUMMARY")
    print(f"D1 every seed has a triggered stretch with model speech: {d1} "
          f"({[[n for _, _, n in r['d1']] for r in res]})")
    print(f"D2 seeds holding: {d2} of 3 ({[(r['d2']['fresh'], r['d2']['of']) for r in res]}) -> {'PASS' if d2 >= 2 else 'FAIL'}")
    print(f"D3 seeds with a model act at or after 16:00: {d3} -> {'PASS' if d3 <= 1 else 'FAIL'}; last model acts "
          f"{[r['d3']['last_model_act'] for r in res]}")
    print(f"D4 acts with need words: {len(hits)}; with fasting >= 48: {ok} -> "
          + ("NOT TESTED" if not hits else f"{100 * ok / len(hits):.1f}% {'PASS' if ok >= 0.9 * len(hits) else 'FAIL'}")
          + f"; unmatched model acts {[r['d4']['unmatched'] for r in res]}")
    print(f"D5 longest runs: {[r['d5']['longest_run'] for r in res]} -> {'PASS' if d5 else 'FAIL'}")
    print(f"D6 days with N11: {d6} of 3 -> {'PASS' if d6 <= 2 else 'FAIL'}")
    print(f"D7 day-3 asks {asks}; live total {live} -> "
          f"{'PASS' if all(a <= 40 for a in asks) and live <= 130 else 'FAIL'}")


if __name__ == "__main__":
    main()
