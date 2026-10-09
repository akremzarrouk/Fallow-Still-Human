"""The street (reports/w2_design.md, §1, §2, §3 and §4.2; W2a): who lives in the thirty houses, what they hold, how each
household decides four times a day, what passes between households, and their visits to the family's door.

Pure functions over plain dicts. Every random value comes from one argument, `draw(string) -> float` in [0, 1), and
each by a string of its own, f"{seed}:street:...", so a draw never depends on how many came before it (as weather.py
and water.py). The weather enters as a value (`wet(minute) -> bool`), never as a read of World. World (truth.py) holds
the state; no prompt builder reads it.

Minutes are absolute, as in weather.py: minutes since 07:00 of played day 1.

W2a builds the plans `stay`, `search` and `ask` (§2.7), the exchange between two households resolved in code (§2.5),
and the visit to no. 9 by day (§4.2). Not built: trade, offer, warn, take, leave, perception of the family by the
street, word between households, rumours, night visits, and the households' bodies (W2b to W2f).
"""
import json
import math
import os
import random
import statistics

import water

HERE = os.path.dirname(os.path.abspath(__file__))
PART = 360                  # minutes in a part of the day: 00-06, 06-12, 12-18, 18-24 (§2.2)
DAY = 1440
DAYLIGHT_PARTS = (1, 2)     # the parts a visit to no. 9 can be made in (§4.2.1)


def load(name):
    with open(os.path.join(HERE, "streetdata", f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def default_draw(s):
    return random.Random(s).random()


def midnight(k):
    """The absolute minute of 00:00 that begins played day k (weather.midnight)."""
    return (k - 1) * DAY - 7 * 60


def day_of(minute):
    """The played day an absolute minute falls in."""
    return (minute + 7 * 60) // DAY + 1


def part_of(minute):
    return ((minute + 7 * 60) % DAY) // PART


def _pick(u, table):
    """table: [[value, share], ...]; the value whose band holds u."""
    acc = 0.0
    for value, share in table:
        acc += share
        if u < acc:
            return value
    return table[-1][0]


def _normal(u, sd):
    return statistics.NormalDist(0, sd).inv_cdf(min(max(u, 1e-12), 1 - 1e-12))


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ---------- §1: who lives on the street ----------
def generate(seed, street=None, pop=None, draw=None):
    """The street of one seed, drawn once (§1). Facts drawn once are under each household's "drawn"; what changes
    after is beside them."""
    street = street or load("street")
    pop = pop or load("population")
    draw = draw or default_draw
    S = f"{seed}:street"
    houses = {h["n"]: dict(h) for h in sorted(street["houses"], key=lambda h: h["n"])}
    others = [n for n in houses if n not in (street["family"], street["neighbour"])]
    # Balanced, not independent (§1.2): exactly round(share × drawn houses) are empty, the lowest keys.
    keys = {n: draw(f"{S}:empty:{n}") for n in others}
    empty = set(sorted(others, key=lambda n: (keys[n], n))[:round(pop["empty_share"] * len(others))])
    state = {"seed": seed, "street": street, "pop": pop, "houses": {}, "households": {},
             "clock": water.DRY_AT, "next_part": midnight(1), "factor": pop["approach"]["factor"],
             "visits": [], "deeds": [], "log": [], "ledger": [], "used": {"water": 0.0, "food": 0.0},
             "found": {"water": 0.0, "food": 0.0}, "visits_made": {}}
    for n, h in houses.items():
        status = ("family" if n == street["family"] else "neighbour" if n == street["neighbour"]
                  else "empty" if n in empty else "occupied")
        rec = {"n": n, "side": h["side"], "x": h["x"], "status": status, "household": None, "state": "intact",
               "left_on": None, "contents": None}
        if status == "empty":
            rec["left_on"] = 1 + int(draw(f"{S}:left_on:{n}") * 3)       # house day 1 to 3 (§1.5)
        state["houses"][n] = rec
    for n in sorted(houses):
        if state["houses"][n]["status"] != "occupied":
            continue
        hh = _household(seed, n, pop, draw)
        state["households"][hh["id"]] = hh
        state["houses"][n]["household"] = hh["id"]
    for hh in state["households"].values():
        _priors(state, hh)
    return state


def _household(seed, n, pop, draw):
    S = f"{seed}:street"
    size = _pick(draw(f"{S}:size:{n}"), pop["size"])
    adults = 1 + (1 if size >= 2 and draw(f"{S}:second_adult:{n}") < pop["second_adult"] else 0)
    old = draw(f"{S}:over_65:{n}") < pop["over_65"]
    members = []
    for i in range(size):
        mid = f"h{n}{'abcdef'[i]}"
        role = "adult" if i < adults else "child"
        band = pop["ages"]["child" if role == "child" else "old" if (old and i == adults - 1) else "adult"]
        age = band[0] + int(draw(f"{S}:age:{mid}") * (band[1] - band[0] + 1))
        sex = "f" if draw(f"{S}:sex:{mid}") < 0.5 else "m"
        m = {"id": mid, "sex": sex, "age": age, "role": role, "health": round(draw(f"{S}:health:{mid}"), 6)}
        if role == "adult":
            m["disposition"] = _pick(draw(f"{S}:disposition:{mid}"), pop["disposition"])
            m["dominant"] = round(draw(f"{S}:dominant:{mid}"), 6)
        members.append(m)
    lead = max((m for m in members if m["role"] == "adult"), key=lambda m: (m["dominant"], m["id"]))
    lo, hi = pop["traits"]
    traits = {t: round(lo + (hi - lo) * draw(f"{S}:trait:{t}:{n}"), 6)
              for t in ("cautious", "anxious", "empathetic", "impulsive")}
    band = _pick(draw(f"{S}:food_band:{n}"), [[b, b[0]] for b in pop["food_bands"]])
    food0 = band[1] + (band[2] - band[1]) * draw(f"{S}:food:{n}")
    bottles = pop["bottles"][0] + (pop["bottles"][1] - pop["bottles"][0]) * draw(f"{S}:water:{n}")
    bath = pop["bath"] if draw(f"{S}:bath:{n}") < pop["bath_full"] else 0.0
    drawn = {"members": members, "disposition": lead["disposition"],
             "violent": any(m.get("disposition") == "violent" for m in members), "traits": traits,
             "stores": {"food_days_at_collapse": round(food0, 6), "bottles": round(bottles, 6), "bath": bath}}
    return {"id": f"h{n}", "home": n, "drawn": drawn,
            "food": max(0.0, food0 - pop["food_gone_by_day1"]),        # food-days at played day 1, 07:00
            "water": bottles + bath,                                   # litres when the taps ran dry
            "level": "as_before", "fear": pop["fear"]["base"] + pop["fear"]["anxious"] * traits["anxious"],
            "food_out_since": None, "hope": pop["priors"]["hope"], "searched": [],
            "occupied": {}, "kind": {}, "surplus": {}, "refused": {}, "waiting": None, "plans": 0}


def size(hh):
    return len(hh["drawn"]["members"])


def has_child(hh):
    return any(m["role"] == "child" for m in hh["drawn"]["members"])


def envoy(hh, pop):
    """Who goes to a door (§1.2): the healthiest adult under 65, any adult, or the oldest child of 10 or more."""
    ms = hh["drawn"]["members"]
    young = [m for m in ms if m["role"] == "adult" and m["age"] < 65]
    if young:
        return max(young, key=lambda m: (m["health"], m["id"]))
    adults = [m for m in ms if m["role"] == "adult"]
    if adults:
        return max(adults, key=lambda m: (m["health"], m["id"]))
    kids = [m for m in ms if m["age"] >= pop["envoy_child_from"]]
    return max(kids, key=lambda m: (m["age"], m["id"])) if kids else None


def distance(a, b, street):
    dx = abs(a["x"] - b["x"])
    return dx if a["side"] == b["side"] else math.hypot(dx, street["across"])


def known(a, b, pop, street):
    """Whether a household at house a knows who lives at house b (§2.1): within 5 doors on either side, or across."""
    w = pop["knows_within"] * street["frontage"]
    return abs(a["x"] - b["x"]) <= w


def _priors(state, hh):
    pop, street = state["pop"], state["street"]
    home = state["houses"][hh["home"]]
    for n, h in state["houses"].items():
        if n == hh["home"]:
            continue
        if known(home, h, pop, street):
            hh["occupied"][n] = 1.0 if h["status"] in ("occupied", "family") else 0.0
        else:
            hh["occupied"][n] = pop["priors"]["occupied"]
        hh["kind"][n] = pop["priors"]["kind"]
        hh["surplus"][n] = pop["priors"]["surplus"]


# ---------- needs and stores ----------
def needs(hh, pop):
    """(need_w, need_f, u) from the stores (§2.1)."""
    n = size(hh)
    dw = hh["water"] / (n * pop["drink"])
    df = hh["food"]
    need_w = clamp(1 - dw / pop["need"]["water_days"])
    need_f = clamp(1 - df / pop["need"]["food_days"])
    return need_w, need_f, max(need_w, pop["need"]["food_weight"] * need_f)


def purpose(hh, pop):
    """What an envoy asks for: water when the household's need of water is above 0.5 and outweighs its food need,
    else food (§4.3: a line states a need the household really has)."""
    need_w, need_f, _ = needs(hh, pop)
    return "ask_water" if need_w > 0.5 and need_w >= pop["need"]["food_weight"] * need_f else "ask_food"


def _level(hh, pop):
    days = hh["water"] / (size(hh) * pop["drink"])
    a, b = pop["need"]["levels_under"]
    return "as_before" if days >= a else "careful" if days >= b else "rationed"


def consume(state, to):
    """Every household's water (from the taps running dry) and food (from played day 1, 07:00) used up to `to`."""
    pop = state["pop"]
    t0 = state["clock"]
    if to <= t0:
        return
    for hid in sorted(state["households"]):
        hh = state["households"][hid]
        n = size(hh)
        hh["level"] = _level(hh, pop)
        use = water.LEVELS[hh["level"]]
        litres = min(hh["water"], ((use["drink"] + use["wash"]) * n + use["toilet"]) * (to - t0) / DAY)
        hh["water"] -= litres
        state["used"]["water"] += litres
        f0 = max(t0, 0)
        if to > f0:
            days = min(hh["food"], (to - f0) / DAY)
            hh["food"] -= days
            state["used"]["food"] += days * n
            if hh["food"] <= 1e-12 and hh["food_out_since"] is None:
                hh["food_out_since"] = f0 + days * DAY
        hh["fear"] *= (1 - pop["fear"]["fall_a_day"]) ** ((to - t0) / DAY)
    state["clock"] = to


def totals(state):
    """Water (litres) and food (person-days) the street holds: households, and empty houses as far as drawn."""
    out = {"water": 0.0, "food": 0.0}
    for hh in state["households"].values():
        out["water"] += hh["water"]
        out["food"] += hh["food"] * size(hh)
    for h in state["houses"].values():
        if h["contents"] is not None:
            out["water"] += h["contents"]["water"]
            out["food"] += h["contents"]["food"]
    return out


def contents(state, n):
    """What an empty house holds, drawn once, the first time it is needed (§1.5): {"water", "food"}."""
    h = state["houses"][n]
    if h["contents"] is None:
        e = state["pop"]["empty_house"]
        S = f"{state['seed']}:street"
        bath = state["pop"]["bath"] if default_or(state)(f"{S}:empty_bath:{n}") < e["bath_full"] else 0.0
        bottles = e["bottle"] * int(default_or(state)(f"{S}:empty_bottles:{n}") * (e["bottles_max"] + 1))
        food = _pick(default_or(state)(f"{S}:empty_food:{n}"), [[v, s] for s, v in e["food"]])
        h["contents"] = {"water": bath + e["cistern"] + bottles, "food": float(food)}
        state["found"]["water"] += h["contents"]["water"]
        state["found"]["food"] += h["contents"]["food"]
    return dict(h["contents"])


def default_or(state):
    return state.get("draw") or default_draw


def _move(state, good, qty, src, dst, at):
    state["ledger"].append({"at": at, "good": good, "qty": qty, "from": src, "to": dst})


def search(state, hid, n, at):
    """A household takes everything an empty house holds; the house is searched (§2.2)."""
    hh = state["households"][hid]
    got = contents(state, n)
    h = state["houses"][n]
    h["contents"] = {"water": 0.0, "food": 0.0}
    h["state"] = "searched"
    hh["water"] += got["water"]
    hh["food"] += got["food"] / size(hh)
    if hh["food"] > 0:
        hh["food_out_since"] = None
    for good in ("water", "food"):
        if got[good]:
            _move(state, good, got[good], f"house:{n}", hid, at)
    hh["searched"].append(n)
    need_w, need_f, _ = needs(hh, state["pop"])
    useful = got["water"] if need_w >= state["pop"]["need"]["food_weight"] * need_f else got["food"]
    hh["hope"] = state["pop"]["priors"]["hope" if useful > 0 else "hope_after_nothing"]
    deed = {"at": at, "from": hid, "to": n, "kind": "searched", "good": None, "qty": got, "place": n}
    state["deeds"].append(deed)
    return deed


def resolve(state, approach, at):
    """An ask between two street households, resolved at once (§2.5). approach: {"by": household id, "to": house,
    "good": "water" | "food"}. A house nobody lives in does not answer."""
    pop, draw = state["pop"], default_or(state)
    hh = state["households"][approach["by"]]
    n = approach["to"]
    target = state["households"].get(state["houses"][n]["household"])
    S = f"{state['seed']}:street:{hh['id']}:{at}"
    good = approach["good"]
    if target is None:
        hh["occupied"][n] = min(hh["occupied"][n], 0.2)
        hh["refused"][n] = hh["refused"].get(n, 0) + 1
        deed = {"at": at, "from": hh["id"], "to": n, "kind": "ignored", "good": good, "qty": 0.0, "place": n}
        state["deeds"].append(deed)
        return deed
    g = pop["give"]
    chance = g["chance"][target["drawn"]["disposition"]] + (g["child"] if has_child(hh) else 0.0)
    if good == "water":
        request = g["request_days"] * size(hh) * pop["drink"]
        surplus = target["water"] - g["keep_days"] * size(target) * pop["drink"]
    else:
        request = g["request_days"] * size(hh)
        surplus = (target["food"] - g["keep_days"]) * size(target)
    qty = min(request, g["share"] * surplus) if surplus > 0 else 0.0
    gave = qty > 0 and draw(f"{S}:give") < chance
    if gave:
        if good == "water":
            target["water"] -= qty
            hh["water"] += qty
        else:
            target["food"] -= qty / size(target)
            hh["food"] += qty / size(hh)
            hh["food_out_since"] = None
        _move(state, good, qty, target["id"], hh["id"], at)
        hh["kind"][n] = clamp(hh["kind"][n] + g["kind_step"])
    else:
        qty = 0.0
        hh["kind"][n] = clamp(hh["kind"][n] - g["kind_step"])
        hh["refused"][n] = hh["refused"].get(n, 0) + 1
        if hh["refused"][n] >= 2:
            hh["kind"][n] = g["refused_twice"]
    deed = {"at": at, "from": hh["id"], "to": n, "kind": "gave" if gave else "refused", "good": good, "qty": qty,
            "place": n}
    state["deeds"].append(deed)
    return deed


# ---------- §2: how a household decides ----------
def plan(state, hh, s, wet):
    """The plan of one household for the part of the day that begins at `s` (§2.2, §2.3): (plan, target, scores).
    Reads only the household's own stores and beliefs, and the weather as a value."""
    pop, street = state["pop"], state["street"]
    P = pop["plans"]
    draw = default_or(state)
    k, p = day_of(s), part_of(s)
    need_w, need_f, u = needs(hh, pop)
    d = hh["drawn"]["disposition"]
    tr = hh["drawn"]["traits"]
    caution = P["caution"][d] * (0.7 + 0.6 * tr["cautious"])
    mult = (P["night"] if p in (0, 3) else 1.0) * (P["rain"] if wet else 1.0) * (1 + hh["fear"])
    if hh["food_out_since"] is not None and s - hh["food_out_since"] >= P["fasting_after_days"] * DAY:
        mult *= P["fasting"]
    S = f"{state['seed']}:street:{hh['id']}:day{k}:part{p}"
    sd = P["noise"][0] + P["noise"][1] * tr["impulsive"]
    scores = {"stay": (1 - u) * P["stay"]}
    targets = {}
    allowed = {"search", "ask"}
    if p == 0:
        allowed = {"search"} if u >= P["night_search_from"] else set()
    elif p == 3 and u < P["evening_from"]:
        allowed = set()
    if envoy(hh, pop) is None:
        allowed = set()
    home = state["houses"][hh["home"]]
    water_first = need_w >= pop["need"]["food_weight"] * need_f
    if "search" in allowed:
        cands = [n for n, h in state["houses"].items() if h["status"] in ("empty",)
                 and hh["occupied"].get(n, 1.0) == 0.0 and n not in hh["searched"]
                 and distance(home, h, street) <= pop["reach_m"]]
        if cands:
            n = min(cands, key=lambda n: (distance(home, state["houses"][n], street), n))
            gain = P["gain"]["search_water" if water_first else "search_food"]
            scores["search"] = (u * gain * hh["hope"] * P["weights"][d]["search"]
                                - (1 - u) * P["risk"]["search"] * mult * caution)
            targets["search"] = n
    if "ask" in allowed:
        cands = []
        for n, h in state["houses"].items():
            if n == hh["home"] or hh["occupied"].get(n, 0.0) <= 0.0 or hh["refused"].get(n, 0) >= 2:
                continue
            if distance(home, h, street) > pop["reach_m"]:
                continue
            if n == street["family"] and (k < 3 or p not in DAYLIGHT_PARTS):
                continue                        # nobody comes to no. 9 before day 3, nor in the dark (§7.2)
            cands.append(n)
        if cands:
            weights = [hh["occupied"][n] * hh["kind"][n] * hh["surplus"][n]
                       / max(distance(home, state["houses"][n], street), 1.0) for n in cands]
            tot = sum(weights)
            if tot > 0:
                x, acc, pick = draw(f"{S}:ask_target") * tot, 0.0, cands[-1]
                for n, w in zip(cands, weights):
                    acc += w
                    if x < acc:
                        pick = n
                        break
                chance = hh["occupied"][pick] * hh["kind"][pick] * hh["surplus"][pick]
                scores["ask"] = (u * P["gain"]["ask"] * chance * P["weights"][d]["ask"]
                                 - (1 - u) * P["risk"]["ask"] * mult * caution)
                targets["ask"] = pick
    for a in sorted(scores):
        scores[a] += _normal(draw(f"{S}:noise:{a}"), sd)
    best = max(sorted(scores), key=lambda a: scores[a])
    return best, targets.get(best), {a: round(v, 4) for a, v in scores.items()}


def advance(state, to, wet):
    """The street up to absolute minute `to`: at each part's start, the stores used up to it, then every household's
    plan for the part, carried out at once (§2.2). A household waiting on a visit to no. 9 makes no plan."""
    while state["next_part"] <= to:
        s = state["next_part"]
        consume(state, s)
        state["log"].append({"what": "part", "at": s})
        rain = bool(wet(s))
        for hid in sorted(state["households"], key=lambda h: state["households"][h]["home"]):
            hh = state["households"][hid]
            if hh["waiting"] is not None:
                continue
            what, target, scores = plan(state, hh, s, rain)
            hh["plans"] += 1
            entry = {"what": "plan", "at": s, "household": hid, "plan": what, "target": target, "scores": scores}
            state["log"].append(entry)
            if what == "search":
                search(state, hid, target, s)
            elif what == "ask":
                go = default_or(state)(f"{state['seed']}:street:{hid}:day{day_of(s)}:part{part_of(s)}:go")
                if go >= state["factor"] * state["pop"]["approach"]["trips_a_part"]:
                    entry["gone"] = False
                    continue
                entry["gone"] = True
                good = "water" if purpose(hh, state["pop"]) == "ask_water" else "food"
                if target == state["street"]["family"]:
                    at = visit_minute(state, hid, day_of(s), part_of(s))
                    make_visit(state, hid, at, purpose(hh, state["pop"]))
                else:
                    resolve(state, {"by": hid, "to": target, "good": good}, s)
        state["next_part"] = s + PART
    consume(state, to)


# ---------- §4.2: visits to no. 9 ----------
def visit_minute(state, hid, k, p, after=None, tag="visit"):
    """A minute on the 3-minute grid inside part p's daylight window of day k (§4.2.1), after `after` if given."""
    lo, hi = state["pop"]["visit"]["windows"][p - 1]
    grid = state["pop"]["visit"]["grid"]
    if after is not None:
        lo = max(lo, after - midnight(k) - 7 * 60)
        lo = -(-lo // grid) * grid
    if lo > hi:
        return None
    u = default_or(state)(f"{state['seed']}:street:{hid}:day{k}:{tag}")
    return midnight(k) + 7 * 60 + lo + int(u * ((hi - lo) // grid + 1)) * grid


def make_visit(state, hid, at, purpose_):
    """A visit to the family's door at absolute minute `at`; the household waits on it."""
    hh = state["households"][hid]
    n = state["visits_made"].get(hid, 0) + 1
    state["visits_made"][hid] = n
    e = envoy(hh, state["pop"])
    v = {"id": f"v{len(state['visits']) + 1}", "household": hid, "home": hh["home"], "n": n, "envoy": dict(e),
         "purpose": purpose_, "made": at, "at": at, "state": "due", "outcome": None, "qty": 0.0, "deferrals": []}
    state["visits"].append(v)
    hh["waiting"] = v["id"]
    return v


def due(state, start, end):
    """The visits not yet made whose minute is in [start, end], in time order."""
    return sorted((v for v in state["visits"] if v["state"] == "due" and start <= v["at"] <= end),
                  key=lambda v: (v["at"], v["id"]))


def next_visit(state, after):
    xs = [v["at"] for v in state["visits"] if v["state"] == "due" and v["at"] > after]
    return min(xs) if xs else None


def defer(state, v, now, why, tomorrow=False):
    """The visit cannot be made now (§4.2.2): it moves to the next daylight part (to the next day's first if
    `tomorrow`), logged."""
    k = day_of(now)
    p = part_of(now)
    tries = [(k + 1, 1)] if tomorrow else ([(k, 2), (k + 1, 1)] if p <= 1 else [(k + 1, 1)])
    n = len(v["deferrals"]) + 1
    for kk, pp in tries:
        at = visit_minute(state, v["household"], kk, pp, after=now + 1 if kk == k else None, tag=f"visit:deferred{n}")
        if at is not None:
            v["deferrals"].append({"at": now, "why": why, "to": at})
            v["at"] = at
            return at
    return None


def end_visit(state, v, outcome, qty, at):
    """The family's door is done with (given, refused or ignored): the household's beliefs about no. 9, its stock,
    and a deed (§4.2.6)."""
    g = state["pop"]["give"]
    hh = state["households"][v["household"]]
    n = state["street"]["family"]
    v.update(state="done", outcome=outcome, qty=qty, ended=at)
    hh["waiting"] = None
    if outcome == "given":
        if v["purpose"] == "ask_water":
            hh["water"] += qty
        else:
            hh["food"] += qty / size(hh)
        _move(state, "water" if v["purpose"] == "ask_water" else "food", qty, f"house:{n}", hh["id"], at)
        hh["kind"][n] = clamp(hh["kind"][n] + g["kind_step"])
        hh["surplus"][n] = clamp(hh["surplus"][n] + g["kind_step"])
    else:
        hh["refused"][n] = hh["refused"].get(n, 0) + 1
        if outcome == "refused":
            hh["kind"][n] = clamp(hh["kind"][n] - g["kind_step"])
        if hh["refused"][n] >= 2:
            hh["kind"][n] = g["refused_twice"]
    state["deeds"].append({"at": at, "from": hh["id"], "to": n, "kind": outcome, "qty": qty,
                           "good": "water" if v["purpose"] == "ask_water" else "food", "place": n, "visit": v["id"]})


def schedule(seed, days, factor=None, wet=None):
    """The visits to no. 9 the seed makes on days 3 to `days` if no knock is ever answered: at most one a day, the
    rest deferred to the next day, as Q7 does (§4.2). The family can move later visits; the first are the seed's."""
    state = generate(seed)
    if factor is not None:
        state["factor"] = factor
    if wet is None:
        import weather
        w = weather.Weather(seed)
        wet = w.raining
    out = []
    knocked = set()
    for k in range(1, days + 1):
        for p in range(4):
            s = midnight(k) + p * PART
            advance(state, s, wet)
            for v in due(state, s, s + PART - 1):
                if k in knocked:
                    defer(state, v, v["at"], "a knock has come today already", tomorrow=True)
                    continue
                knocked.add(k)
                out.append(dict(v, day=k))
                end_visit(state, v, "ignored", 0.0, v["at"])
    advance(state, midnight(days + 1), wet)
    return out


# ---------- §3: the noticing rule ----------
def perceive(stimulus, observer):
    """None, "heard" or "words" (§3.1): L = level − 20·log10(max(d, 1)) − what is between; heard if L ≥ ambient,
    words if L ≥ ambient + 10."""
    if observer is None:
        return None
    level = stimulus["level"] - 20 * math.log10(max(observer["metres"], 1.0)) - observer["between"]
    if level >= observer["ambient"] + stimulus.get("words_over", 10):
        return "words"
    return "heard" if level >= observer["ambient"] else None


def wake_chance(anxious, pop=None):
    a, b, top = (pop or load("population"))["sound"]["wake"]
    return min(top, 2 * (a + b * anxious))


def wakes(state, v, n, pid, anxious):
    """Whether knock n of a visit wakes someone resting (§3.1), by a string of its own."""
    return default_or(state)(f"{state['seed']}:street:{v['id']}:knock{n}:wake:{pid}") < wake_chance(anxious, state["pop"])


# ---------- §4.3: the stranger's words, chosen by code ----------
_LINES = []


def lines():
    if not _LINES:
        _LINES.append(load("lines")["slots"])
    return _LINES[0]


def line(state, v, slot, i=0):
    """A line of the pool for this visit's household (`with`: a child, or two or more), by the string
    <seed>:street:<household>:visit<n>:<slot>."""
    hh = state["households"][v["household"]]
    ok = [x for x in lines()[slot] if x.get("with") is None or (x["with"] == "child" and has_child(hh))
          or (x["with"] == "others" and size(hh) >= 2)]
    u = default_or(state)(f"{state['seed']}:street:{v['household']}:visit{v['n']}:{slot}" + (f":{i}" if i else ""))
    return ok[int(u * len(ok))]["text"]


AGE_WORDS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
             12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 20: "twenty", 25: "twenty-five",
             30: "thirty", 35: "thirty-five", 40: "forty", 45: "forty-five", 50: "fifty", 55: "fifty-five",
             60: "sixty", 65: "sixty-five", 70: "seventy", 75: "seventy-five", 80: "eighty", 85: "eighty-five"}


def who_words(m):
    """("a woman of about forty", "A woman's voice") for an envoy, as an eye and an ear would have it."""
    if m["age"] < 16:
        noun = "girl" if m["sex"] == "f" else "boy"
        age = AGE_WORDS[m["age"]]
    else:
        noun = ("old woman" if m["sex"] == "f" else "old man") if m["age"] >= 65 else \
               ("woman" if m["sex"] == "f" else "man")
        age = AGE_WORDS[min(85, max(20, int(round(m["age"] / 5.0)) * 5))]
    voice = {"girl": "A girl's voice", "boy": "A boy's voice"}.get(noun, f"A {noun}'s voice")
    article = "an" if noun[0] in "aeiou" else "a"
    return f"{article} {noun} of about {age}", voice


def looks(state, v, at):
    """What an eye sees of the envoy on the step: who, thin or not, and what they carry."""
    hh = state["households"][v["household"]]
    who, _ = who_words(v["envoy"])
    thin = hh["food_out_since"] is not None and at - hh["food_out_since"] >= 3 * DAY
    carry = "holding two empty bottles" if v["purpose"] == "ask_water" else "holding an empty bag"
    return who + (", thin," if thin else ",") + " " + carry


def urgency(state, v):
    return needs(state["households"][v["household"]], state["pop"])[2]
