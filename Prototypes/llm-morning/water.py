"""The water (reports/world_design.md, §4.2) and thirst (§4.3.2): what the house stored, how it is used, how rain fills
the bin, how much the houses next door hold, and the words an eye gives a store. The numbers; World (truth.py) holds
the state.
"""
import random

# What the family filled on house day 1 (§4.2): the bath, 150; the kitchen's two large pans (2 × 8), kettle (1.5), six
# 1.5 L bottles (9) and two 10 L buckets (20). All est. but the bath, which is anchored on [S12].
BATH, KITCHEN = 150.0, 46.5
FILLED = BATH + KITCHEN
DRY_AT = -2580              # house day 2, 12:00 (est.), in minutes since played day 1, 07:00
# Each level, a day: drinking and washing per person, the toilet for the house (bucket flushes, 2 × 6 L [S13]). est.
LEVELS = {"as_before": {"drink": 2.0, "wash": 1.0, "toilet": 12.0},
          "careful": {"drink": 2.0, "wash": 0.5, "toilet": 0.0},
          "rationed": {"drink": 1.25, "wash": 0.0, "toilet": 0.0}}
NET_LOSS = 1.2              # litres a day at rest in a cool house, with no food (§4.3.2; [S1] gives 1.0 to 1.5)
MASS = {"daniel": 78, "elena": 65, "leo": 70, "mara": 55}     # kg, est.
THIRST = (0.02, 0.05, 0.08, 0.10)                             # share of body mass lost: T1 to T4 [S1, S4, S5]
CATCH = 25 * 0.85           # litres per mm at the back drainpipe: 25 m² of roof [est.] × runoff 0.85 [S9]
BIN = 240.0                 # the wheelie bin, litres (est.)
CARRY = 10.0                # litres one person carries home from a night trip (est.)
WET_FOR = 120               # minutes someone back from the rain in the yard is wet and cold (est.)
# An empty house's water (§4.5; amendment 2): its bath full with chance 0.5 (est.), its cistern 6 L [S13], a few
# bottles: 0 to 4 of 1.5 L (est.).
EMPTY_BATH_FULL = 0.5
CISTERN = 6.0


def thirst_stage(deficit, mass):
    share = deficit / mass
    return sum(1 for x in THIRST if share >= x - 1e-12)


def house_water(seed, place):
    """What an empty house holds, drawn once from its own strings: {"bath", "cistern", "bottles"} in litres."""
    bath = BATH if random.Random(f"{seed}:world:water:{place}:bath").random() < EMPTY_BATH_FULL else 0.0
    bottles = 1.5 * random.Random(f"{seed}:world:water:{place}:bottles").randint(0, 4)
    return {"bath": bath, "cistern": CISTERN, "bottles": bottles}


def take_from(left, litres):
    """Carry `litres` from what a house has left, bottles first, then the cistern, then the bath. Returns what was
    taken; `left` is changed in place."""
    took = 0.0
    for k in ("bottles", "cistern", "bath"):
        x = min(left[k], litres - took)
        left[k] -= x
        took += x
    return took


def split(tap):
    """The tap water as an eye sees it: the kitchen's containers kept full from the bath first (§4.2)."""
    kitchen = min(tap, KITCHEN)
    return tap - kitchen, kitchen


def about(x, step):
    return int(round(x / step)) * step


RULE = {"careful": "{since}, none of it goes on the toilet or on washing.",
        "rationed": "{since}, {holder} {verb} it out by the cup: five cups each a day."}


def describe(store, level, since, holder, bin_out):
    """The "About water:" line: the bath to the nearest 10 litres, the kitchen's containers and the bin to the nearest
    5 and 10, the rule and since when. holder: "you", a name, or None."""
    bath, kitchen = split(store["tap"])
    b, k = about(bath, 10), about(kitchen, 5)
    if store["tap"] <= 0:
        out = "About water: the bath and the pans are empty: no stored tap water is left."
    elif b == 0:
        out = (f"About water: the bath is empty and the pans, kettle, bottles and buckets in the kitchen hold about "
               f"{k} litres: tap water stored before the taps ran dry.")
    else:
        out = (f"About water: the bath holds about {b} litres and the pans, kettle, bottles and buckets in the kitchen "
               f"about {k} litres: tap water stored before the taps ran dry.")
    if level == "as_before":
        if store["tap"] > 0:
            out += " It is also used to flush the toilet and to wash."
    else:
        rule = RULE[level].format(since=since[0].upper() + since[1:], holder=holder,
                                  verb="share" if holder == "you" else "shares")
        out += " " + rule
    if bin_out:
        r = about(store["rain"], 10)
        out += (f" The bin under the drainpipe in the yard holds about {r} litres of rain water." if r
                else " The bin is under the drainpipe in the yard, with no rain water in it yet.")
    return out
