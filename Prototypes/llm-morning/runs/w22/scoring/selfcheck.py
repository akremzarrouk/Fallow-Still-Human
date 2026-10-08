"""Checks w1_score.py's rules on edited copies of the fake run (runs/w22/fake), for the rules the fake model's own
words never exercise (water words, "no water" claims, rationing, a trip with water in the reason, rain heard). No API.
Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset; prints one line per check and exits 1 if any fails."""
import copy
import os
import sys

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join("runs", "w22", "scoring"))
sys.argv = [sys.argv[0]]
import w1_score as S                                   # noqa: E402

base, _ = S.load("runs/w22/fake")
bad = []


def check(name, got, want):
    ok = got == want
    print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got!r}" + ("" if ok else f", wanted {want!r}"))
    if not ok:
        bad.append(name)


def speech_acts(t, k):
    return S.speech(t[f"day{k}"])


def edit(t, k, i, words):
    """Set the words of the i-th speech act of day k (by decided_at) in the transcript's own act record."""
    target = speech_acts(t, k)[i]
    target["words"] = words
    return target


# W1-4 -----------------------------------------------------------------
t = copy.deepcopy(base)
for k in (3, 4, 5):
    edit(t, k, 0, "We should drink the water slowly.")
check("W1-4 three days with water words", (S.w14(t)["days"], S.w14(t)["acts"]), (3, 3))
edit(t, 6, 0, "Is it going to rain?")
check("W1-4 four days (rain counts)", S.w14(t)["days"], 4)
t2 = copy.deepcopy(base)
edit(t2, 3, 0, "Waterproof? No. Drinking, thirsty, bathroom.")
check("W1-4 whole words only (waterproof no; drinking, thirsty yes)", S.w14(t2)["acts"], 1)

# W1-6 -----------------------------------------------------------------
t = copy.deepcopy(base)
a = edit(t, 4, 0, "There is no water left, none at all.")
check("W1-6 claim while the store is > 0", len(S.w16(t)["violations"]), 1)
for k in (3, 4, 5):
    for e in t[f"day{k}"]["quiet"]["water"]:
        e[1] = e[2] = 0.0
check("W1-6 claim while the store is 0 (day 4) is not a violation", len(S.w16(t)["violations"]), 0)
t = copy.deepcopy(base)
night = t["night4"]["decisions"][0]
night["reason"] = "We are out of water and I cannot sleep."
check("W1-6 a night reason counts", len(S.w16(t)["violations"]), 1)
t = copy.deepcopy(base)
edit(t, 4, 0, "No more water!")
edit(t, 5, 0, "The water has run out.")
edit(t, 6, 0, "Water is gone.")
edit(t, 7, 0, "We have no water.")
check("W1-6 four claims, all while water is stored", (S.w16(t)["claims"], len(S.w16(t)["violations"])), (4, 4))
check("W1-6 verdict FAIL over 1", S.verdicts({**S.score("runs/w22/fake", "runs/w22/fake/cache/fake-daniel_ate_it-seed2.json", 0),
                                              "w16": S.w16(t)})["W1-6"].split()[0], "FAIL")

# W1-7 -----------------------------------------------------------------
t = copy.deepcopy(base)
for e in t["day5"]["quiet"]["water"]:
    e[1], e[2] = 30.0, 0.0
r = S.w17(t)
check("W1-7 drop below 50 L on day 5, a ration act on day 3 holds", (r["k"], r["tested"], r["holds"]), (5, True, True))
for k in range(3, 11):
    for a in S.model_acts(t[f"day{k}"]):
        if a["option"] in S.WATER_RULES:
            a["option"] = "reassure_all"
check("W1-7 no rationing act at all fails", S.w17(t)["holds"], False)
a = S.model_acts(t["day6"])[0]
a["option"] = "save_water"
check("W1-7 a save_water on day 6 = k + 1 holds", S.w17(t)["holds"], True)
a["option"] = "reassure_all"
a = S.model_acts(t["day7"])[0]
a["option"] = "ration_water"
check("W1-7 a ration on day 7 = k + 2 is late", S.w17(t)["holds"], False)
t = copy.deepcopy(base)
for e in t["day10"]["quiet"]["water"]:
    e[1], e[2] = 10.0, 0.0
check("W1-7 a drop only on day 10 is not tested", S.w17(t)["tested"], False)
check("W1-7 the unedited fake never falls below 50 L", S.w17(base)["drop"], None)

# W1-11 ----------------------------------------------------------------
r = S.w111(base)
check("W1-11 fake: went_out nights exist and no water in reasons", (r["tested"], r["holds"]), (True, False))
t = copy.deepcopy(base)
for b in S.bedtimes(t["night3"]):
    if b["person"] == "daniel":
        b["reason"] = "There is no water and I am thirsty."
check("W1-11 a leaver's bedtime reason with water holds", S.w111(t)["holds"], True)
t = copy.deepcopy(base)
leavers = {r_["leaver"] for r_ in S.w111(t)["rows"] if r_["night"] == 4}
for a in S.speech(t["day4"]):
    if S.NAME[a["who"]] in leavers and S.act_of(a["option"])[0] in S.world.TRIP_KINDS:
        a["words"] = "We have to find water."
        break
else:
    # no trip-position act by a night-4 leaver: make one
    target = next(a for a in S.speech(t["day4"]) if S.NAME[a["who"]] in leavers)
    target["option"] = "volunteer"
    target["words"] = "I will go and find some water."
check("W1-11 trip words of that day with water hold", S.w111(t)["holds"], True)
t = copy.deepcopy(base)
t["chronicle"]["events"] = [e for e in t["chronicle"]["events"] if e["kind"] != "went_out"]
check("W1-11 no went_out: NOT TESTED", S.w111(t)["tested"], False)

# W1-1 -----------------------------------------------------------------
t = copy.deepcopy(base)
t["chronicle"]["events"] = [e for e in t["chronicle"]["events"] if e["kind"] not in ("went_out", "got_up", "at_door")]
check("W1-1 none", S.w11(t)["count"], 0)
ev = {"id": "N6-99", "scene": "N6", "kind": "got_up", "actor": "mara", "members": None}
t["chronicle"]["events"] += [ev, dict(ev, id="N6-98")]
check("W1-1 a leaver's two got_up in one night count once", S.w11(t)["count"], 1)
t["chronicle"]["events"] += [dict(ev, id="N6-97", kind="went_out", members=["mara"])]
check("W1-1 got_up with a went_out for that leaver counts once as went_out",
      (S.w11(t)["count"], S.w11(t)["items"]), (1, [(6, "Mara", "went_out")]))
t["chronicle"]["events"] += [dict(ev, id="N2-99", scene="N2", actor="daniel"), dict(ev, id="N10-1", scene="N10")]
check("W1-1 nights 2 and 10 are outside 3-9", S.w11(t)["count"], 1)
t["chronicle"]["events"] += [dict(ev, id="N7-1", scene="N7", kind="at_door", actor="leo", members=["leo", "mara"])]
check("W1-1 at_door counts its group", (S.w11(t)["count"], S.w11(t)["nights"]), (3, [6, 7]))

# W1-5 -----------------------------------------------------------------
r = S.w15(base)
check("W1-5 fake: 2 qualifying spells (day 7 17:18, day 9 11:30), all heard", ([(s["day"], s["start"]) for s in r["spells"]], r["a_all"]),
      ([(7, "17:18"), (9, "11:30")], True))
t = copy.deepcopy(base)
t["day7"]["quiet"]["rain"][0]["heard"].remove("leo")
check("W1-5(a) someone not heard: not 100%", S.w15(t)["a_all"], False)
t = copy.deepcopy(base)
d7 = t["day7"]["quiet"]
d7["spans"].append({"who": "leo", "routine": "rest", "room": "x", "start": 600, "end": 700, "planned": 100, "ended": "time",
                    "seen_start": [], "seen_end": [], "seen_leave": [], "left": "x"})
d7["rain"][0]["heard"].remove("leo")
check("W1-5(a) a resting person need not hear", S.w15(t)["a_all"], True)
t = copy.deepcopy(base)
q6 = next(s for s in t["day7"]["quiet"]["stretches"] if s["trigger"] == "Q6")
act = next(a for a in S.model_acts(t["day7"]) if q6["start"] <= a["minute"] < q6["end"])
act["option"] = "collect_rain"
r = S.w15(t)
check("W1-5(b) a collect_rain in the Q6 stretch holds; counted", (r["b"]["holds"], len(r["collect_rain"])), (True, 2))
t = copy.deepcopy(base)
act = next(a for a in S.model_acts(t["day7"]) if q6["start"] <= a["minute"] < q6["end"] and a["words"])
act["words"] = "Quick, get the bin out under the pipe!"
check("W1-5(b) a speech act matching bin holds", S.w15(t)["b"]["holds"], True)
act["words"] = "The bindings are loose."
check("W1-5(b) whole words only", S.w15(t)["b"]["holds"], False)
t = copy.deepcopy(base)
t["day7"]["quiet"]["stretches"] = [s for s in t["day7"]["quiet"]["stretches"] if s["trigger"] != "Q6"]
check("W1-5(b) no Q6 stretch: 30 minutes read instead", "30 minutes" in S.w15(t)["b"]["window"], True)
for b in t["night4"]["decisions"]:
    if b["ask"] == "bedtime":
        b["option"] = "rain_out"
        break
check("W1-5 rain_out counted", len(S.w15(t)["rain_out"]), 1)

# W1-2, W1-3, W1-9, W1-10 ---------------------------------------------
t = copy.deepcopy(base)
bs = [b for n in S.nights_of(t).values() for b in S.bedtimes(n)]
for b, text in zip(bs[:9], ["I am too weak to walk.", "I cannot go out.", "no strength to move", "barely able to stand",
                            "I am unable to leave.", "too weak and cannot carry anything", "I can't make it", "too weak to get up",
                            "I am too weak to go"]):
    b["reason"] = text
check("W1-2 nine frozen reasons fail", S.verdicts({**S.score("runs/w22/fake", "runs/w22/fake/cache/fake-daniel_ate_it-seed2.json", 0),
                                                   "w12": S.w12(t)})["W1-2"].split()[0], "FAIL")
check("W1-2 count", S.w12(t)["frozen"], 9)
p = [{"kind": "day", "who": "Leo", "estimate": 1, "api": 1, "text": "x\nYour body: starving. Walking any distance feels impossible.\nYour body: hungry."}]
check("W1-9 one forbidding line", (S.w19(p)["body_lines"], S.w19(p)["matches"]), (2, 1))
t = copy.deepcopy(base)
sp = [a for d in S.days_of(t).values() for a in S.speech(d)]
for a in sp[:int(len(sp) * 0.25)]:
    a["words"] = "You took the can."
check("W1-10 over 20% fails", S.w110(t)["share"] > 0.2, True)

print("\n%d failed" % len(bad) if bad else "\nall checks ok")
sys.exit(1 if bad else 0)
