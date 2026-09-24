#!/usr/bin/env python
"""The arithmetic behind the analytic predictions of the route-applicability experiment.

Written and run BEFORE the fixture existed, and committed with the predictions. It is an
independent second reading of route-applicability.json and causal-routes.json: every
count it prints is a prediction the fixture must reproduce. A disagreement means a bug in
one of the two, not a result.

Usage: python prediction-model.py            (families A to J; a few minutes)
       python prediction-model.py frozen     (the frozen file, 30,618 cells)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "Assets/_Project/Data/Experiments"
SPEC = json.loads((EXP / "route-applicability.json").read_text(encoding="utf-8"))
ROUTES = json.loads((EXP / "causal-routes.json").read_text(encoding="utf-8"))
FROZEN = json.loads((EXP / "intentions.json").read_text(encoding="utf-8"))["candidates"]
SWEEP = json.loads((EXP / "held-out-people.json").read_text(encoding="utf-8"))["sweep"]
TIE = 1e-9
SAME = 1e-12
REPS = ["S", "A", "B", "C", "C-entity", "C-conditions", "C-split", "C-kind"]

TRAITS, LEVELS, RING, BELIEFS = SWEEP["traits"], SWEEP["levels"], SWEEP["value_ring"], SWEEP["belief_sets"]


def key(t):
    if t["kind"] == "belief":
        return "belief:%s(%s)" % (t["predicate"], ",".join(t["args"]))
    if t["kind"] == "emotion":
        return "emotion:%s@%s" % (t["name"], t.get("target") or "situation")
    return t["kind"] + ":" + t["name"]


def profile(i):
    lv, n = {}, i
    for name in TRAITS:
        lv["trait:" + name] = LEVELS[n % len(LEVELS)]
        n //= len(LEVELS)
    shift = i % len(RING)
    for k, name in enumerate(RING[shift:] + RING[:shift]):
        lv["value:" + name] = max(0.0, 1.0 - 0.25 * k)
    for seed in BELIEFS[i % len(BELIEFS)]:
        lv["belief:%s(%s)" % (seed["predicate"], ",".join(seed["args"]))] = seed["confidence"]
    return lv


PROFILES = [profile(i) for i in range(len(LEVELS) ** len(TRAITS))]
SITS = SPEC["situations"]


def gate_ok(when, present):
    if not when:
        return True
    if "alone" in when and (len(present) == 0) != when["alone"]:
        return False
    if "others_present_min" in when and len(present) < when["others_present_min"]:
        return False
    return True


def gate_key(when):
    parts = []
    if "alone" in when:
        parts.append("alone" if when["alone"] else "not alone")
    if "others_present_min" in when:
        parts.append("others>=%d" % when["others_present_min"])
    return ",".join(parts) if parts else "any"


def gate_as_preds(when):
    if "alone" in when:
        return ["absent:anyone"] if when["alone"] else ["present:anyone"]
    if "others_present_min" in when:
        return ["present:anyone"]
    return []


def pred_holds(p, present, target):
    if p == "present:anyone":
        return len(present) > 0
    if p == "absent:anyone":
        return len(present) == 0
    if p == "present:$target":
        return target is not None and target in present
    if p == "absent:$target":
        return target is None or target not in present
    raise ValueError(p)


def read_preds(preds, rep, target):
    out = []
    for p in preds:
        if rep == "C-entity":
            if p == "present:$target":
                p = "present:anyone"
            elif p == "absent:$target":
                continue
        if rep == "C-kind" and target is not None:
            p = {"present:anyone": "present:$target", "absent:anyone": "absent:$target"}.get(p, p)
        out.append(p)
    return out


def role_of(t, rep):
    r = t.get("role", "support")
    if rep == "C-kind" and t["kind"] == "belief":
        return "condition"
    if rep in ("S", "A", "C-conditions") and r == "condition":
        return "support"
    return r


def build(case):
    """Rules (with intent) and routes (key -> dict) of a case, the rival included."""
    rules = [dict(r, intent=case["intent"]) for r in case["rules"]]
    routes = {r["key"]: {"key": r["key"], "intent": case["intent"], "applies_when": r.get("applies_when")} for r in case["routes"]}
    if case.get("rival"):
        rv = SPEC["rival"]
        rules.append(dict(rv["rule"], intent=rv["intent"], route=rv["route"]))
        routes[rv["route"]] = {"key": rv["route"], "intent": rv["intent"], "applies_when": rv["applies_when"]}
    return rules, routes


def evaluate(rules, routes, lv, present, target, rep, alternatives=(), canon=None, policy="P0"):
    canon = canon or {}
    if rep == "S":
        by = {}
        route_w = {}
        for r in rules:
            if not gate_ok(r.get("when", {}), present):
                continue
            w = r["base"] + sum(t["factor"] * lv.get(key(t), 0.0) for t in r["terms"])
            if w <= 0.0:
                continue
            by[r["intent"]] = by.get(r["intent"], 0.0) + w
            route_w[r["route"]] = route_w.get(r["route"], 0.0) + w
        app = {k: k in route_w for k in routes}
        state = {}
        for i in {x["intent"] for x in routes.values()}:
            state[i] = "applicable" if i in by else "no candidate"
        tok = "none" if not by else sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        return {"app": app, "strength": route_w, "support": by, "P0": tok, "P1": tok, "state": state, "trace": tok, "flags": 0, "recognised": 0, "ambiguous": 0}
    stmts = {k: {} for k in routes}
    conds = {k: [] for k in routes}
    roles_seen = {k: {} for k in routes}
    admitted = {k: False for k in routes}
    restated = conflicts = 0
    circ = rep in ("C", "C-entity", "C-conditions", "C-split", "C-kind")
    for r in rules:
        rk = r["route"]
        g = gate_ok(r.get("when", {}), present)
        if not circ and not g:
            continue
        if not circ:
            admitted[rk] = True
        entries = []
        if r["base"] != 0.0:
            entries.append(("circumstance:" + gate_key(r.get("when", {})), r["base"], 1.0, "support"))
        for t in r["terms"]:
            role = role_of(t, rep)
            roles_seen[rk].setdefault(key(t), set()).add(t.get("role", "support"))
            if role == "condition" and rep not in ("S", "A", "C-conditions"):
                conds[rk].append(key(t))
                if rep == "B+w":
                    entries.append((key(t), t["factor"], lv.get(key(t), 0.0), "support"))
                continue
            entries.append((key(t), t["factor"], lv.get(key(t), 0.0), role))
        for k, coef, level, role in entries:
            had = stmts[rk].get(k)
            if had is not None:
                if abs(had[0] - coef) < SAME:
                    restated += 1
                    continue
                conflicts += 1
                if (abs(coef), coef) <= (abs(had[0]), had[0]):
                    continue
            stmts[rk][k] = (coef, coef * level if k.startswith("circumstance:") is False else coef)
    app, strength = {}, {}
    ambiguous = sum(1 for rk in routes for k, s in roles_seen[rk].items() if len(s) > 1)
    for rk, rd in routes.items():
        if circ:
            preds = rd["applies_when"]
            if preds is None or (not preds and rd.get("from_gate")):
                preds = []
            ok = all(pred_holds(p, present, target) for p in read_preds(preds, rep, target))
        else:
            ok = admitted[rk]
        if rep not in ("S", "A", "C-conditions"):
            ok = ok and all(lv.get(k, 0.0) > 0.0 for k in conds[rk])
        app[rk] = ok
        strength[rk] = sum(v[1] for v in stmts[rk].values())
    # Candidates.
    intents = []
    for rd in routes.values():
        if rd["intent"] not in intents:
            intents.append(rd["intent"])
    cand = []
    for i in intents:
        rks = [k for k, rd in routes.items() if rd["intent"] == i]
        if rep in ("A", "B", "B+w"):
            ok = any(admitted[k] for k in rks)
        elif rep == "C-split":
            ok = any(all(pred_holds(p, present, target) for p in read_preds(routes[k]["applies_when"] or [], rep, target)) for k in rks)
        else:
            ok = True
        if ok:
            cand.append(i)
    support, state = {}, {}
    for i in intents:
        rks = [k for k, rd in routes.items() if rd["intent"] == i]
        s = 0.0
        grouped = set()
        for g in alternatives:
            live = [k for k in g if k in rks and app[k]]
            if live:
                s += max(strength[k] for k in live)
            grouped |= set(g)
        for k in rks:
            if k not in grouped and app[k]:
                s += strength[k]
        support[i] = s
        if i not in cand:
            state[i] = "no candidate"
        else:
            state[i] = "applicable" if any(app[k] for k in rks) else "no applicable route"

    def choose(pool):
        if not pool:
            return "none"
        top = max(support[i] for i in pool)
        tied = sorted(i for i in pool if support[i] >= top - TIE)
        return tied[0] if len(tied) == 1 else "tie(" + "=".join(tied) + ")"

    p0 = choose(cand)
    p1 = choose([i for i in cand if state[i] == "applicable"])
    parts = []
    for i in sorted(cand):
        rs = []
        for k in (k for k, rd in routes.items() if rd["intent"] == i):
            if not app[k] or not stmts[k]:
                continue
            rs.append(canon.get(k, k) + "{" + ";".join("%s=%.9f" % (kk, v[1]) for kk, v in sorted(stmts[k].items())) + "}")
        parts.append(i + ": " + " + ".join(sorted(rs)))
    flags = 0
    rks = list(routes)
    for x in range(len(rks)):
        for y in range(x + 1, len(rks)):
            a, b = rks[x], rks[y]
            if routes[a]["intent"] == routes[b]["intent"] and app[a] and app[b] and \
                    {k: v[0] for k, v in stmts[a].items()} == {k: v[0] for k, v in stmts[b].items()} and sorted(conds[a]) == sorted(conds[b]):
                flags += 1
    return {"app": app, "strength": strength, "support": support, "P0": p0, "P1": p1, "state": state,
            "trace": " | ".join(parts), "flags": flags, "recognised": restated + conflicts, "ambiguous": ambiguous}


def declared(case, lv, present):
    """The declared meaning: applicability and strength of the focal route(s)."""
    out = {}
    for rd in case["routes"]:
        ok = all(pred_holds(p, present, case["target"]) for p in rd["applies_when"])
        for r in case["rules"]:
            if r["route"] != rd["key"]:
                continue
            for t in r["terms"]:
                if t["role"] == "condition" and lv.get(key(t), 0.0) <= 0.0:
                    ok = False
        out[rd["key"]] = ok
    return out


CASES = {c["id"]: c for c in SPEC["cases"]}


def ev(case, lv, present, rep):
    rules, routes = build(case)
    return evaluate(rules, routes, lv, present, case["target"], rep)


def cells():
    for lv in PROFILES:
        for s in SITS:
            yield lv, s["present"]


def act_errors(case_ids, rep, override=None):
    fa = fs = n = 0
    for cid in case_ids:
        c = CASES[cid]
        for lv, present in cells():
            lv = dict(lv, **(override or {}))
            o = ev(c, lv, present, rep)
            d = declared(c, lv, present)
            for rk, want in d.items():
                n += 1
                if o["app"][rk] and not want:
                    fa += 1
                if want and not o["app"][rk]:
                    fs += 1
    return n, fa, fs


def family_a(rep):
    res = []
    for cid, fact, conf in (("owning_c", "belief:answerable_for($self,missing_can)", 0.9), ("settling_c", "belief:role_claim($self,leads_family)", 0.8)):
        for lvl in (0.0, conf):
            res.append(act_errors([cid], rep, {fact: lvl}))
    n = sum(r[0] for r in res)
    return n, sum(r[1] for r in res), sum(r[2] for r in res)


def family_b(rep):
    bad = n = 0
    for (a, b), fact, conf in ((("owning_c", "owning_e"), "belief:answerable_for($self,missing_can)", 0.9), (("settling_c", "settling_e"), "belief:role_claim($self,leads_family)", 0.8)):
        for lvl in (0.0, conf):
            for lv, present in cells():
                lv = dict(lv, **{fact: lvl})
                oa, ob = ev(CASES[a], lv, present, rep), ev(CASES[b], lv, present, rep)
                ra, rb = CASES[a]["routes"][0]["key"], CASES[b]["routes"][0]["key"]
                n += 1
                want_a = lvl > 0
                if oa["app"][ra] != want_a or ob["app"][rb] is not True:
                    bad += 1
    return n, bad


def family_e(rep):
    viol = strength_bad = n = 0
    for cid, fact, coef in (("side_mara", "trait:empathetic", 0.40), ("owning_c", "trait:honest", 0.30)):
        c = CASES[cid]
        rk = c["routes"][0]["key"]
        for lv, present in cells():
            outs = [ev(c, dict(lv, **{fact: x}), present, rep) for x in LEVELS]
            n += 1
            if len({o["app"][rk] for o in outs}) > 1:
                viol += 1
            if rep != "S" and outs[0]["app"][rk]:
                for k in range(2):
                    if abs((outs[k + 1]["strength"][rk] - outs[k]["strength"][rk]) - coef * (LEVELS[k + 1] - LEVELS[k])) > TIE:
                        strength_bad += 1
                        break
    return n, viol, strength_bad


def family_f(rep):
    viol = strength_bad = negative = n = 0
    c = CASES["stepping_in"]
    for lv, present in cells():
        outs = [ev(c, dict(lv, **{"trait:anxious": x}), present, rep) for x in LEVELS]
        n += 1
        if len({o["app"]["stepping_in"] for o in outs}) > 1:
            viol += 1
        if rep != "S":
            for k in range(2):
                if abs((outs[k]["strength"]["stepping_in"] - outs[k + 1]["strength"]["stepping_in"]) - 0.60 * (LEVELS[k + 1] - LEVELS[k])) > TIE:
                    strength_bad += 1
                    break
            negative += sum(1 for o in outs if o["strength"]["stepping_in"] <= 0.0)
    return n, viol, strength_bad, negative


def family_g(rep):
    res = {}
    for cid in ("only_side_mara", "only_owning", "only_fair", "weak_pull"):
        c = CASES[cid]
        counts = {"applicable": 0, "no applicable route": 0, "no candidate": 0}
        bad = 0
        p0 = {}
        p1 = {}
        for lv, present in cells():
            o = ev(c, lv, present, rep)
            st = o["state"][c["intent"]]
            counts[st] += 1
            want = declared(c, lv, present)[c["routes"][0]["key"]]
            if (st == "applicable") != want:
                bad += 1
            p0[o["P0"]] = p0.get(o["P0"], 0) + 1
            p1[o["P1"]] = p1.get(o["P1"], 0) + 1
        res[cid] = (counts, bad, p0, p1)
    return res


def family_j(rep):
    return act_errors(["side_mara", "scene_mara"], rep)


def families_18(rep):
    """The causal-route synthetic families, re-read by this representation."""
    syn = ROUTES["synthetic"]
    decl = {d["rule"]: d for d in ROUTES["frozen"]["routes"]}
    rivals = []
    rival_routes = {}
    for rid in syn["rivals"]:
        fr = next(c for c in FROZEN if c["id"] == rid)
        roles = decl[rid].get("roles", {})
        terms = []
        for s in fr["scaled_by"]:
            role = {"enabler": "condition", "inhibitor": "inhibitor"}.get(roles.get(key(s)), "inhibitor" if s["factor"] < 0 else "support")
            terms.append(dict(s, role=role))
        rivals.append({"id": rid, "route": decl[rid]["route"], "intent": fr["intent"], "when": fr.get("when", {}), "base": fr.get("base", 0.0), "terms": terms})
        rival_routes[decl[rid]["route"]] = {"key": decl[rid]["route"], "intent": fr["intent"], "applies_when": gate_as_preds(fr.get("when", {}))}
    variants = {}
    for name, rs in syn["variants"].items():
        rules = [{"id": r["id"], "route": r["route"], "intent": r["intent"], "when": {}, "base": r.get("base", 0.0),
                  "terms": [dict(t, role="inhibitor" if t["factor"] < 0 else "support") for t in r.get("scaled_by", [])]} for r in rs]
        routes = {}
        for r in rules:
            routes.setdefault(r["route"], {"key": r["route"], "intent": r["intent"], "applies_when": []})
        routes.update(rival_routes)
        alts = [g["routes"] for g in syn.get("variant_relations", {}).get(name, []) if g["type"] == "alternative"]
        canon = syn.get("renamings", {}).get(name, {})
        variants[name] = (rules + rivals, routes, alts, canon)
    company = ["a", "b", "c"]
    out = {}
    for pair in syn["pairs"]:
        a, b = pair["a"], pair["b"]
        sd = td = od = fl = 0
        for lv in PROFILES:
            ra = evaluate(*variants[a][:2], lv, company, "a", rep, variants[a][2], variants[a][3])
            rb = evaluate(*variants[b][:2], lv, company, "a", rep, variants[b][2], variants[b][3])
            if abs(ra["support"].get("protect", 0.0) - rb["support"].get("protect", 0.0)) > TIE:
                sd += 1
            if ra["trace"] != rb["trace"]:
                td += 1
            if ra["P0"] != rb["P0"]:
                od += 1
            if rb["recognised"] > ra["recognised"]:
                fl += 1
        out[a + "|" + b] = (sd, td, od, fl)
    return out


def main():
    n1 = len(PROFILES) * len(SITS)
    print("profiles %d, situations %d, cells per case %d" % (len(PROFILES), len(SITS), n1))
    for rep in REPS:
        print("==", rep)
        print("  A condition: cells %d, false activations %d, false suppressions %d" % family_a(rep))
        print("  B condition vs evidence: cells %d, not told apart %d" % family_b(rep))
        for fam, ids in (("C circumstance", ["side_mara", "away_mara", "duty_mara"]), ("D person", ["side_mara", "side_daniel", "side_elena"])):
            print("  %s: cells %d, false activations %d, false suppressions %d" % ((fam,) + act_errors(ids, rep)))
        print("  E support: cells %d, applicability changed %d, strength wrong %d" % family_e(rep))
        print("  F inhibitor: cells %d, applicability changed %d, strength wrong %d, applicable-with-nonpositive-strength %d" % family_f(rep))
        for cid, (counts, bad, p0, p1) in family_g(rep).items():
            print("  G %s: %s; wrong %d; P0 %s; P1 %s" % (cid, counts, bad, p0, p1))
        print("  J target vs generic: cells %d, false activations %d, false suppressions %d" % family_j(rep))
    for rep in ("A", "B", "C"):
        got = families_18(rep)
        want = SPEC["causal_route_d_counts"]
        bad = [k for k, v in got.items() if list(v[:3]) != want[k][:3] or (len(want[k]) > 3 and v[3] != want[k][3])]
        print("I 18 pairs under %s: %d of 18 reproduce D%s" % (rep, 18 - len(bad), (" ; differ: " + str({k: got[k] for k in bad})) if bad else ""))


def frozen():
    decl = {d["rule"]: d for d in ROUTES["frozen"]["routes"]}
    rules = []
    for c in FROZEN:
        roles = decl[c["id"]].get("roles", {})
        terms = []
        for s in c.get("scaled_by", []):
            role = {"enabler": "condition", "inhibitor": "inhibitor"}.get(roles.get(key(s)), "inhibitor" if s["factor"] < 0 else "support")
            terms.append(dict(s, role=role))
        rules.append({"id": c["id"], "route": decl[c["id"]]["route"], "intent": c["intent"], "when": c.get("when", {}), "base": c.get("base", 0.0), "terms": terms, "motives": c["motives"]})
    wants = ["avoid_exposure", "find_out", "get_food", "guard_supplies", "keep_peace", "look_after", "restore_standing"]
    reps = ["A", "B", "C", "C-split", "B+w"]
    res = {(r, p): [] for r in reps for p in ("P0", "P1")}
    groups = []
    for lv in PROFILES:
        for w in wants:
            rs = [r for r in rules if w in r["motives"]]
            routes = {r["route"]: {"key": r["route"], "intent": r["intent"], "applies_when": gate_as_preds(r["when"])} for r in rs}
            for present in (["a", "b", "c"], []):
                groups.append((w, "company" if present else "alone", lv.get("belief:answerable_for($self,missing_can)", 0.0) > 0))
                for rep in reps:
                    o = evaluate(rs, routes, lv, present, "a", rep)
                    res[(rep, "P0")].append(o["P0"])
                    res[(rep, "P1")].append(o["P1"])
    n = len(groups)
    base = res[("A", "P0")]
    print("frozen cells %d" % n)
    for (rep, pol), toks in res.items():
        diff = sum(1 for x, y in zip(toks, base) if x != y)
        none = sum(1 for x in toks if x == "none")
        ties = sum(1 for x in toks if x.startswith("tie("))
        print("%-8s %s: differs from A/P0 %5d (%.1f %%), none %5d, ties %4d" % (rep, pol, diff, 100.0 * diff / n, none, ties))
    by = {}
    for g, x, y in zip(groups, res[("B", "P0")], base):
        if x != y:
            k = "%s %s %s: %s -> %s" % (g[0], g[1], "believer" if g[2] else "no belief", y, x)
            by[k] = by.get(k, 0) + 1
    for k, v in sorted(by.items(), key=lambda kv: -kv[1]):
        print("  B/P0 against A: %-80s %d" % (k, v))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "frozen":
        frozen()
    else:
        main()
