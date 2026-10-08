"""The weather (reports/world_design.md, §4.1): a Richardson-type generator fed by real climate normals.

Each day is wet or dry by a first-order Markov chain on P(W|W) and P(W|D); a wet day's rain is an exponential amount,
in one spell or two; the day's highest and lowest temperatures are the month's normals with noise, cooler by day and
milder by night when it is wet. Indoors, with no power and no heating, is the day's mean + 4 °C. Every draw has its own
seed string, so a day's weather never depends on how many draws came before it.

Minutes are absolute: minutes since 07:00 of played day 1 (quiet.absolute), on the house's 3-minute grid.
"""
import math
import random

# Met Office, Kew Gardens 1991–2020 normals [S7]; the rest est. (world_design §4.1).
CLIMATE = {
    "months": {9: {"max": 20.3, "min": 10.5, "mm": 51.9, "wet_days": 8.4, "days": 30},
               10: {"max": 16.0, "min": 7.8, "mm": 67.9, "wet_days": 10.9, "days": 31}},
    "p_ww": 0.5,            # est.: no Kew value found
    "second_spell": 0.3,    # est.
    "spell_hours": (2, 6),  # est.
    "wet_max": -2.0, "wet_min": 1.0,    # est.
    "noise": 2.0,           # est., °C
    "indoor_over_mean": 4.0,            # est.
    "day1_after_mid_september": 16,     # played day 1 is 1 October (est.)
}
DAY = 1440
GRID = 3


def _frac(k):
    """How far day k is from mid-September (0) to mid-October (1)."""
    return min(1.0, (CLIMATE["day1_after_mid_september"] + k - 1) / 31)


def _mix(k, key):
    sep, octo = CLIMATE["months"][9], CLIMATE["months"][10]
    f = _frac(k)
    if key == "p":
        a, b = sep["wet_days"] / sep["days"], octo["wet_days"] / octo["days"]
    elif key == "amount":
        a, b = sep["mm"] / sep["wet_days"], octo["mm"] / octo["wet_days"]
    else:
        a, b = sep[key], octo[key]
    return a + (b - a) * f


def wet_chance(k):
    """The chance that day k is wet, from the month's days with 1 mm or more."""
    return _mix(k, "p")


def _u(seed, k, what):
    return random.Random(f"{seed}:weather:day{k}:{what}")


def hhmm(minute):
    """An absolute minute as a time of day, "13:12"."""
    h, m = divmod((minute + 7 * 60) % DAY, 60)
    return f"{h:02d}:{m:02d}"


def midnight(k):
    """The absolute minute of 00:00 that begins day k."""
    return (k - 1) * DAY - 7 * 60


class Weather:
    """The weather of one seed, drawn day by day on demand. force(k, spells) fixes a day (tests)."""

    def __init__(self, seed):
        self.seed = seed
        self.days = {}
        self.forced = {}

    def force(self, k, spells, **more):
        """Day k's rain is these (start, end, mm) spells, in absolute minutes; more: other fields (indoor, tmax...)."""
        spells = [tuple(s) for s in spells]
        self.forced[k] = {"spells": spells, **more}
        self.days.pop(k, None)

    def wet(self, k):
        if k in self.forced:
            return bool(self.forced[k]["spells"])
        p = wet_chance(k)
        u = _u(self.seed, k, "wet").random()
        if k == 1:
            return u < p
        ww = CLIMATE["p_ww"]
        return u < (ww if self.wet(k - 1) else p * (1 - ww) / (1 - p))

    def day(self, k):
        if k in self.days:
            return self.days[k]
        wet = self.wet(k)
        mm = 0.0
        spells = []
        if k in self.forced:
            spells = list(self.forced[k]["spells"])
            mm = sum(s[2] for s in spells)
        elif wet:
            mm = -_mix(k, "amount") * math.log(1 - _u(self.seed, k, "mm").random())
            n = 2 if _u(self.seed, k, "spells").random() < CLIMATE["second_spell"] else 1
            lo, hi = CLIMATE["spell_hours"]
            for i in range(n):
                start = midnight(k) + _u(self.seed, k, f"spell{i}:start").randrange(0, DAY, GRID)
                length = _u(self.seed, k, f"spell{i}:hours").randrange(lo * 60, hi * 60 + 1, GRID)
                spells.append((start, start + length, mm / n))
        tmax = _mix(k, "max") + _u(self.seed, k, "tmax").gauss(0, CLIMATE["noise"]) + (CLIMATE["wet_max"] if wet else 0)
        tmin = _mix(k, "min") + _u(self.seed, k, "tmin").gauss(0, CLIMATE["noise"]) + (CLIMATE["wet_min"] if wet else 0)
        if tmax <= tmin + 1:
            tmax = tmin + 1
        out = {"k": k, "wet": wet, "mm": mm, "spells": sorted(spells), "tmax": tmax, "tmin": tmin,
               "indoor": (tmax + tmin) / 2 + CLIMATE["indoor_over_mean"]}
        out.update({key: v for key, v in self.forced.get(k, {}).items() if key != "spells"})
        self.days[k] = out
        return out

    def spells(self, start, end):
        """Every spell that overlaps [start, end), as (start, end, mm), from the days around them."""
        k0 = int((start + 7 * 60) // DAY) + 1
        k1 = int((end + 7 * 60) // DAY) + 1
        out = []
        for k in range(max(1, k0 - 1), k1 + 1):
            out += [s for s in self.day(k)["spells"] if s[0] < end and s[1] > start]
        return sorted(out)

    def rate(self, minute):
        """mm of rain in the minute that begins at `minute`."""
        return sum(mm / (b - a) for a, b, mm in self.spells(minute, minute + 1))

    def raining(self, minute):
        return bool(self.spells(minute, minute + 1))

    def indoor(self, minute):
        k = int((minute + 7 * 60) // DAY) + 1
        return self.day(k)["indoor"]
