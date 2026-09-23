#!/usr/bin/env python
"""The arithmetic behind the analytic predictions of the reason-semantics experiment.

Written and run BEFORE the fixture existed, and committed with the predictions. It is a
second, independent reading of reason-semantics.json: it re-derives every check's
expected pass or failure and its cell count from the declared reading rules, so that a
disagreement with the fixture points at a bug in one of the two, not at the result.

It models only what the checks need: the 2,187 sweep profiles (traits, value weights by
rank, belief confidence; no feelings, as in the sweep), the five synthetic situations,
and the six representations; and, with the argument `frozen`, the frozen intentions.json
read with the causal-route declarations over the sweep's 30,618 cells. It does not model
the negative controls (identities by construction) or real mornings.

Usage: python prediction-model.py          (the checks and the ablations; about 5 minutes)
       python prediction-model.py frozen   (the frozen file)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = json.loads((ROOT / "Assets/_Project/Data/Experiments/reason-semantics.json").read_text(encoding="utf-8"))
SWEEP = json.loads((ROOT / "Assets/_Project/Data/Experiments/held-out-people.json").read_text(encoding="utf-8"))["sweep"]
EPS = 1e-9
REPS = ["S", "A", "B-parts", "B-circ", "B", "C"]
ABLATIONS = ["A-Sel2", "B-Sel0", "B-Sel1"]

TRAITS, LEVELS, RING, BELIEFS = SWEEP["traits"], SWEEP["levels"], SWEEP["value_ring"], SWEEP["belief_sets"]
DECAY = 0.25


def profile(i):
    t, n = {}, i
    for name in TRAITS:
        t[name] = LEVELS[n % len(LEVELS)]
        n //= len(LEVELS)
    shift = i % len(RING)
    values = RING[shift:] + RING[:shift]
    v = {name: max(0.0, 1.0 - k * DECAY) for k, name in enumerate(values)}
    b = {}
    for seed in BELIEFS[i % len(BELIEFS)]:
        b["belief:%s(%s)" % (seed["predicate"], ",".join(seed["args"]))] = seed["confidence"]
    return t, v, b


PROFILES = [profile(i) for i in range(len(LEVELS) ** len(TRAITS))]
SITS = SPEC["situations"]
CIRC = SPEC["circumstances"]


def key(term):
    if term["kind"] == "belief":
        return "belief:%s(%s)" % (term["predicate"], ",".join(term["args"]))
    return term["kind"] + ":" + term["name"]


def level(p, k):
    t, v, b = p
    kind, name = k.split(":", 1)
    if kind == "trait":
        return t.get(name, 0.0)
    if kind == "value":
        return v.get(name, 0.0)
    if kind == "belief":
        return b.get(k, 0.0)
    return 0.0


def gate(when, s):
    if not when:
        return True
    if "alone" in when and (not s["others_present"]) != when["alone"]:
        return False
    if "others_present_min" in when and not s["others_present"]:
        return False
    return True


def holds(circ, s):
    return all(s[f] == val for f, val in CIRC[circ].items())


def feature(name, s):
    return {"unwatched": not s["watched"], "watched": s["watched"],
            "target_present": s["target_present"], "target_absent": not s["target_present"]}[name]


def reads_parts(r): return r in ("B-parts", "B", "C", "B-Sel0", "B-Sel1")
def reads_circ(r): return r in ("B-circ", "B", "C", "B-Sel0", "B-Sel1")
def reads_rel(r): return r == "C"


def rules_of(case):
    rules = [dict(r, intent=case["intent"]) for r in case["rules"]]
    if case.get("rival"):
        rv = SPEC["rival"]
        rules.append(dict(rv["rule"], intent=rv["intent"], route=rv["route"]))
    return rules


def routes_of(case):
    rs = {r["key"]: dict(r, intent=case["intent"]) for r in case["routes"]}
    if case.get("rival"):
        rv = SPEC["rival"]
        rs[rv["route"]] = {"key": rv["route"], "intent": rv["intent"], "direction": "toward", "circumstance": rv["circumstance"]}
    return rs


def evaluate_shipped(case, p, s):
    """S: IntentionSelector.Form, rule by rule."""
    by, rule_amounts, route_amt = {}, {}, {}
    for r in rules_of(case):
        if not gate(r.get("when", {}), s):
            continue
        w = r["base"] + sum(t["factor"] * level(p, key(t)) for t in r["terms"])
        if w <= 0.0:
            continue
        by[r["intent"]] = by.get(r["intent"], 0.0) + w
        rule_amounts.setdefault(r["intent"], []).append(w)
        route_amt[r["route"]] = route_amt.get(r["route"], 0.0) + w
    if not by:
        return {"outcome": None, "support": by, "routes": route_amt, "attributed": {}, "flags": 0}
    top = sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))
    return {"outcome": top[0][0], "support": by, "routes": route_amt, "attributed": {}, "flags": 0}


def evaluate(case, p, s, rep):
    if rep == "S":
        return evaluate_shipped(case, p, s)
    parts, circ, rel = reads_parts(rep), reads_circ(rep), reads_rel(rep)
    routes = routes_of(case)
    stmts = {}      # route -> key -> amount
    coefs = {}      # route -> key -> coef
    conds = {}      # route -> [condition keys]
    admitted = {}   # route -> admitted by a shipped gate (for representations without circumstances)
    pushes = {}     # route -> situational push amount
    for r in rules_of(case):
        base_route = r["route"]
        g = gate(r.get("when", {}), s)
        stands = r.get("stands_for")
        if circ and stands:
            f = stands["situational_push"]
            pushes[base_route] = pushes.get(base_route, 0.0) + (r["base"] if feature(f, s) else 0.0)
            admitted.setdefault(base_route, False)
            continue
        if not circ and not g:
            admitted.setdefault(base_route, False)
            for t in r["terms"]:
                admitted.setdefault(t.get("route", base_route), False)
            continue
        if not circ:
            admitted[base_route] = True
        if r["base"] != 0.0:
            k = "base|" + json.dumps(r.get("when", {}), sort_keys=True)
            stmts.setdefault(base_route, {})
            coefs.setdefault(base_route, {})
            if k in coefs[base_route] and abs(coefs[base_route][k] - r["base"]) > EPS:
                if abs(r["base"]) > abs(coefs[base_route][k]):
                    coefs[base_route][k] = r["base"]
                    stmts[base_route][k] = r["base"]
            else:
                coefs[base_route][k] = r["base"]
                stmts[base_route][k] = r["base"]
        for t in r["terms"]:
            rt = t.get("route", base_route)
            if not circ:
                admitted[rt] = True
            k = key(t)
            if parts and t["part"] == "condition":
                conds.setdefault(rt, []).append(k)
                continue
            stmts.setdefault(rt, {})
            coefs.setdefault(rt, {})
            if k in coefs[rt]:
                if abs(coefs[rt][k] - t["factor"]) <= EPS:
                    continue
                if abs(t["factor"]) <= abs(coefs[rt][k]):
                    continue
            coefs[rt][k] = t["factor"]
            stmts[rt][k] = t["factor"] * level(p, k)

    applicable, contrib, total = {}, {}, {}
    for rk, rd in routes.items():
        if circ:
            c = rd["circumstance"]
            if not rel and rd.get("circumstance_as_copied"):
                c = rd["circumstance_as_copied"]
            ok = holds(c, s)
        else:
            ok = admitted.get(rk, False)
        if parts:
            ok = ok and all(level(p, k) > 0.0 for k in conds.get(rk, []))
        applicable[rk] = ok
    if rel:
        for rl in case.get("relations", []):
            if rl["kind"] == "reinforces":
                a, b = rl["routes"]
                applicable[a] = applicable[a] and applicable[b]
    for rk, rd in routes.items():
        if not applicable[rk]:
            total[rk] = contrib[rk] = 0.0
            continue
        t = sum(stmts.get(rk, {}).values()) + pushes.get(rk, 0.0)
        total[rk] = t
        if parts:
            t = max(0.0, t) if rd["direction"] == "toward" else min(0.0, t)
        contrib[rk] = t
    operating = {rk: applicable[rk] for rk in routes}
    if rel:
        for rl in case.get("relations", []):
            if rl["kind"] == "alternative":
                live = [r for r in rl["routes"] if applicable[r]]
                if live:
                    best = max(live, key=lambda r: (contrib[r], -rl["routes"].index(r)))
                    for r in live:
                        if r != best:
                            operating[r] = False
    final = {rk: (contrib[rk] if operating[rk] else 0.0) for rk in routes}
    support, admitted_intent, toward_applies = {}, {}, {}
    for rk, rd in routes.items():
        i = rd["intent"]
        support[i] = support.get(i, 0.0) + final[rk]
        adm = holds(rd.get("circumstance_as_copied") if (not rel and rd.get("circumstance_as_copied")) else rd["circumstance"], s) if circ else admitted.get(rk, False)
        admitted_intent[i] = admitted_intent.get(i, False) or adm
        toward_applies[i] = toward_applies.get(i, False) or (applicable[rk] and rd["direction"] == "toward")
    sel = {"A": 0, "S": None, "A-Sel2": 2, "B-Sel0": 0, "B-Sel1": 1}.get(rep, 2)
    cands = []
    for i in support:
        if sel == 0 and admitted_intent[i]:
            cands.append(i)
        elif sel == 1 and toward_applies[i]:
            cands.append(i)
        elif sel == 2 and support[i] > EPS:
            cands.append(i)
    outcome = None
    if cands:
        top = sorted(cands, key=lambda i: -support[i])
        if len(top) > 1 and abs(support[top[0]] - support[top[1]]) <= EPS:
            outcome = "tie"
        else:
            outcome = top[0]
    attributed = {rk: dict(stmts.get(rk, {})) if applicable[rk] else {} for rk in routes}
    flags = 0
    if rep != "S":
        focal = [rk for rk, rd in routes.items() if rd["intent"] == case["intent"]]
        for x in range(len(focal)):
            for y in range(x + 1, len(focal)):
                a, b = focal[x], focal[y]
                if not (applicable[a] and applicable[b]):
                    continue
                same = coefs.get(a, {}) == coefs.get(b, {}) and sorted(conds.get(a, [])) == sorted(conds.get(b, []))
                if circ:
                    same = same and routes[a]["circumstance"] == routes[b]["circumstance"]
                if parts:
                    same = same and routes[a]["direction"] == routes[b]["direction"]
                if same:
                    flags += 1
    return {"outcome": outcome, "support": support, "routes": final, "applicable": applicable,
            "attributed": attributed, "operating": operating, "flags": flags}


CASES = {c["id"]: c for c in SPEC["cases"]}


def cells():
    for pi, p in enumerate(PROFILES):
        for s in SITS:
            yield pi, p, s


def contributes(o, rk):
    return abs(o["routes"].get(rk, 0.0)) > EPS


def run_check(ch, rep):
    """Returns (passed, violating cells) for one check under one representation."""
    kind = ch["kind"]
    bad = 0
    if kind == "same_as":
        c, ref = CASES[ch["case"]], CASES[ch["reference"]]
        for _, p, s in cells():
            a, b = evaluate(c, p, s, rep), evaluate(ref, p, s, rep)
            fa, fb = a["support"].get(c["intent"], 0.0), b["support"].get(ref["intent"], 0.0)
            ea = sorted(round(v, 9) for v in a["routes"].values()) if rep == "S" else sorted((k, round(v, 9)) for k, v in a["routes"].items())
            eb = sorted(round(v, 9) for v in b["routes"].values()) if rep == "S" else sorted((k, round(v, 9)) for k, v in b["routes"].items())
            if rep == "S":
                ea = sorted(round(v, 9) for v in shipped_rule_amounts(c, p, s))
                eb = sorted(round(v, 9) for v in shipped_rule_amounts(ref, p, s))
            if abs(fa - fb) > EPS or ea != eb or a["outcome"] != b["outcome"]:
                bad += 1
        return bad == 0, bad
    if kind == "differs_from":
        c, ref = CASES[ch["case"]], CASES[ch["reference"]]
        diff = 0
        for _, p, s in cells():
            if abs(evaluate(c, p, s, rep)["support"].get(c["intent"], 0.0) - evaluate(ref, p, s, rep)["support"].get(ref["intent"], 0.0)) > EPS:
                diff += 1
        return diff > 0, diff
    if kind == "flag_identical":
        c = CASES[ch["case"]]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            if o["flags"] == 0:
                bad += 1
        return bad == 0, bad
    if kind == "applies_exactly":
        c = CASES[ch["case"]]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            if contributes(o, ch["route"]) != holds(ch["circumstance"], s):
                bad += 1
        return bad == 0, bad
    if kind in ("evidence", "condition"):
        c = CASES[ch["case"]]
        coef = [t for r in c["rules"] for t in r["terms"] if key(t) == ch["fact"]][0]["factor"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            lv = level(p, ch["fact"])
            if rep == "S":
                att = coef * lv
                applies = contributes(o, ch["route"])
            else:
                att = o["attributed"].get(ch["route"], {}).get(ch["fact"], 0.0)
                applies = o["applicable"].get(ch["route"], False) and contributes(o, ch["route"])
            if kind == "evidence":
                ok = applies and abs(att - coef * lv) <= EPS
            else:
                ok = (not applies) if lv == 0.0 else (applies and abs(att) <= EPS)
            if not ok:
                bad += 1
        return bad == 0, bad
    if kind == "not_a_strength":
        ref = CASES[ch["reference"]]
        for cid in ch["cases"]:
            c = CASES[cid]
            rk = c["routes"][0]["key"]
            for _, p, s in cells():
                o = evaluate(c, p, s, rep)
                if not contributes(o, rk):
                    continue
                r = evaluate(ref, p, SITS[0], rep)["routes"][ch["reference_route"]]
                if abs(o["routes"][rk] - r) > EPS:
                    bad += 1
        return bad == 0, bad
    if kind == "situational_push":
        c, ref = CASES[ch["case"]], CASES[ch["reference"]]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            r = evaluate(ref, p, SITS[0], rep)["routes"][ch["reference_route"]]
            want = r + (ch["amount"] if feature(ch["feature"], s) else 0.0)
            if abs(o["routes"].get(ch["route"], 0.0) - want) > EPS:
                bad += 1
        return bad == 0, bad
    if kind == "co_active":
        c = CASES[ch["case"]]
        a, b = ch["routes"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            ca, cb = o["routes"].get(a, 0.0), o["routes"].get(b, 0.0)
            if not (ca > EPS and cb > EPS and o["support"][c["intent"]] > max(ca, cb) + EPS):
                bad += 1
        return bad == 0, bad
    if kind == "alternative":
        c = CASES[ch["case"]]
        a, b = ch["routes"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            alone = []
            for keep in (a, b):
                solo = dict(c, rules=[r for r in c["rules"] if r["route"] == keep], relations=[])
                alone.append(evaluate(solo, p, s, rep)["support"].get(c["intent"], 0.0))
            if o["support"][c["intent"]] > max(alone) + EPS:
                bad += 1
        return bad == 0, bad
    if kind == "exclusive":
        c = CASES[ch["case"]]
        a, b = ch["routes"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            if contributes(o, a) and contributes(o, b):
                bad += 1
        return bad == 0, bad
    if kind == "reinforces":
        c = CASES[ch["case"]]
        of = [r for r in c["routes"] if r["key"] == ch["of"]][0]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            strength = sum(t["factor"] * level(p, key(t)) for r in c["rules"] if r["route"] == ch["route"] for t in r["terms"])
            want = holds(of["circumstance"], s) and strength > EPS
            if contributes(o, ch["route"]) != want:
                bad += 1
        return bad == 0, bad
    if kind == "against":
        c = CASES[ch["case"]]
        toward = [r["key"] for r in c["routes"] if r["direction"] == "toward"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            tsum = sum(max(0.0, o["routes"].get(k, 0.0)) for k in toward)
            if not (o["support"][c["intent"]] < tsum - EPS):
                bad += 1
        return bad == 0, bad
    if kind == "hold_back_local":
        c = CASES[ch["case"]]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            other = sum(r["base"] + sum(t["factor"] * level(p, key(t)) for t in r["terms"]) for r in c["rules"] if r["route"] == ch["other"])
            if o["support"][c["intent"]] < other - EPS or o["routes"].get(ch["route"], 0.0) < -EPS:
                bad += 1
        return bad == 0, bad
    if kind == "forms_iff":
        c = CASES[ch["case"]]
        w = ch["when"]
        for _, p, s in cells():
            o = evaluate(c, p, s, rep)
            if "held" in w:
                want = level(p, w["held"]) > 0.0
            elif "circumstance" in w:
                want = holds(w["circumstance"], s)
            elif "positive" in w:
                want = w["positive"]["const"] + sum(f * level(p, k) for k, f in w["positive"]["terms"].items()) > EPS
            else:
                want = True
            if (o["outcome"] == c["intent"]) != want:
                bad += 1
        return bad == 0, bad
    if kind == "same_outcome":
        c, ref = CASES[ch["case"]], CASES[ch["reference"]]
        for _, p, s in cells():
            if evaluate(c, p, s, rep)["outcome"] != evaluate(ref, p, s, rep)["outcome"]:
                bad += 1
        return bad == 0, bad
    raise ValueError(kind)


def shipped_rule_amounts(case, p, s):
    out = []
    for r in rules_of(case):
        if not gate(r.get("when", {}), s):
            continue
        w = r["base"] + sum(t["factor"] * level(p, key(t)) for t in r["terms"])
        if w > 0.0:
            out.append(w)
    return out


def selection_changes(case, a, b):
    n = 0
    for _, p, s in cells():
        if evaluate(case, p, s, a)["outcome"] != evaluate(case, p, s, b)["outcome"]:
            n += 1
    return n


def main():
    n = len(PROFILES) * len(SITS)
    print("profiles %d, situations %d, cells per case %d" % (len(PROFILES), len(SITS), n))
    fams = {}
    for ch in SPEC["checks"]:
        row = []
        for rep in REPS:
            ok, cnt = run_check(ch, rep)
            row.append((ok, cnt))
            fams.setdefault(ch["family"], {}).setdefault(rep, 0)
            fams[ch["family"]][rep] += 1 if ok else 0
        print("%-4s %-18s " % (ch["id"], ch["kind"]) + "  ".join("%s:%s(%d)" % (r, "pass" if ok else "FAIL", cnt) for r, (ok, cnt) in zip(REPS, row)))
    total = {r: sum(f[r] for f in fams.values()) for r in REPS}
    counts = {}
    for ch in SPEC["checks"]:
        counts[ch["family"]] = counts.get(ch["family"], 0) + 1
    print()
    for f in sorted(fams):
        print("family %s (%d checks): " % (f, counts[f]) + "  ".join("%s %d" % (r, fams[f][r]) for r in REPS))
    print("total (%d checks): " % len(SPEC["checks"]) + "  ".join("%s %d" % (r, total[r]) for r in REPS))
    print()
    print("ablations, family F:")
    for ch in [c for c in SPEC["checks"] if c["family"] == "F"]:
        print("%-4s " % ch["id"] + "  ".join("%s:%s(%d)" % (r, *(("pass" if ok else "FAIL"), cnt)) for r in ABLATIONS for ok, cnt in [run_check(ch, r)]))
    print()
    print("selection changes against C (cells, of %d):" % n)
    for cid, c in CASES.items():
        print("%-4s " % cid + "  ".join("%s %d" % (r, selection_changes(c, r, "C")) for r in REPS[:-1]))


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


# ------------------------------------------------------------------ the frozen file

def frozen():
    """The frozen intentions.json, read with the causal-route declarations, over the
    30,618 cells of the generalization sweep (2 circumstances). Feelings are zero in the
    sweep, as in every earlier experiment."""
    rules = json.loads((ROOT / "Assets/_Project/Data/Experiments/intentions.json").read_text(encoding="utf-8"))["candidates"]
    decl = json.loads((ROOT / "Assets/_Project/Data/Experiments/causal-routes.json").read_text(encoding="utf-8"))["frozen"]["routes"]
    roles = {d["rule"]: d.get("roles", {}) for d in decl}
    route_of = {d["rule"]: d["route"] for d in decl}
    part_of = SPEC["frozen_reading"]["role_to_part"]
    wants = ["avoid_exposure", "find_out", "get_food", "guard_supplies", "keep_peace", "look_after", "restore_standing"]
    circs = [{"others_present": True, "target_present": True, "watched": False}, {"others_present": False, "target_present": False, "watched": False}]
    reps = ["S", "A", "B-parts", "B-circ", "B-parts+w", "A-Sel2", "B-Sel0", "B-Sel1"]
    out = {r: [] for r in reps}
    groups = []
    for pi, p in enumerate(PROFILES):
        for w in wants:
            for ci, s in enumerate(circs):
                groups.append((w, ci, pi))
                cand = [r for r in rules if w in r["motives"]]
                for rep in reps:
                    out[rep].append(decide_frozen(cand, roles, route_of, part_of, p, s, rep))
    return reps, out, groups


def decide_frozen(cand, roles, route_of, part_of, p, s, rep):
    if rep == "S":
        by = {}
        for r in cand:
            if not gate(r.get("when", {}), s):
                continue
            w = r.get("base", 0.0) + sum(t["factor"] * level(p, key(t)) for t in r.get("scaled_by", []))
            if w <= 0.0:
                continue
            by[r["intent"]] = by.get(r["intent"], 0.0) + w
        if not by:
            return None
        return sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    parts = rep in ("B-parts", "B-parts+w", "B-Sel0", "B-Sel1")
    support, admitted, applies = {}, {}, {}
    for r in cand:
        i = r["intent"]
        if not gate(r.get("when", {}), s):
            continue
        admitted[i] = True
        ok, total = True, r.get("base", 0.0)
        for t in r.get("scaled_by", []):
            k = key(t)
            role = roles[r["id"]].get(k, "inhibitor" if t["factor"] < 0 else "driver")
            part = part_of[role]
            lv = level(p, k)
            if parts and part == "condition":
                if lv <= 0.0:
                    ok = False
                if rep == "B-parts+w":
                    total += t["factor"] * lv
                continue
            total += t["factor"] * lv
        if parts:
            total = max(0.0, total) if ok else 0.0
        applies[i] = applies.get(i, False) or ok
        support[i] = support.get(i, 0.0) + total
    sel = {"A": 0, "B-Sel0": 0, "B-Sel1": 1}.get(rep, 2)
    cands = [i for i in support if (sel == 0 and admitted.get(i)) or (sel == 1 and applies.get(i)) or (sel == 2 and support[i] > EPS)]
    if not cands:
        return None
    top = sorted(cands, key=lambda i: -support[i])
    if len(top) > 1 and abs(support[top[0]] - support[top[1]]) <= EPS:
        return "tie"
    return top[0]


def frozen_report():
    reps, out, groups = frozen()
    n = len(groups)
    print("frozen file: %d cells" % n)
    for rep in reps:
        none = sum(1 for o in out[rep] if o is None)
        ties = sum(1 for o in out[rep] if o == "tie")
        vs_a = sum(1 for a, b in zip(out[rep], out["A"]) if a != b)
        vs_s = sum(1 for a, b in zip(out[rep], out["S"]) if a != b)
        print("%-10s none %5d  ties %3d  differs from A %5d  from S %5d" % (rep, none, ties, vs_a, vs_s))
    for rep in ("B-parts", "B-parts+w", "B-circ"):
        by = {}
        for (w, ci, pi), a, b in zip(groups, out[rep], out["A"]):
            if a != b:
                g = w + (" in company" if ci == 0 else " alone")
                by[g] = by.get(g, 0) + 1
        print(rep, "changes against A by group:", by)
    theft = {}
    for (w, ci, pi), a, b in zip(groups, out["B-parts"], out["A"]):
        if a != b:
            believer = level(PROFILES[pi], "belief:answerable_for($self,missing_can)") > 0
            k = ("believer" if believer else "no belief") + ": " + str(b) + " -> " + str(a)
            theft[k] = theft.get(k, 0) + 1
    print("B-parts against A, by belief and change:", theft)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "frozen":
    frozen_report()
