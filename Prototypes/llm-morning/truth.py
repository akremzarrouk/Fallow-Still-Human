"""World: the single owner of truth for the weather and the water (reports/world_design.md, §1; W1).

The house's stored water, the rain caught in the yard, how much each person lacks to drink, and what the houses next
door and further along hold are World's. People never read it: the code reads it and writes what each of them
perceives into their own lines (quiet.py), and no prompt builder may touch it. Every prompt is built inside
`prompting()`, and while one is, reading anything of a World raises TruthLeak (§1.2).

Time is absolute: minutes since 07:00 of played day 1. The world advances minute by minute, so a use, a rain spell
and a thirst all fall where they happen.
"""
import contextlib
import copy

import water
from weather import Weather

_PROMPTING = [0]


class TruthLeak(RuntimeError):
    """World was read while a prompt was being built."""


@contextlib.contextmanager
def prompting():
    """Every prompt is built inside this: World cannot be read until it is over."""
    _PROMPTING[0] += 1
    try:
        yield
    finally:
        _PROMPTING[0] -= 1


class Guarded:
    def __getattribute__(self, name):
        if _PROMPTING[0] and not name.startswith("__"):
            raise TruthLeak(f"World.{name} read while a prompt was being built")
        return object.__getattribute__(self, name)

    def __deepcopy__(self, memo):
        out = object.__new__(type(self))
        memo[id(self)] = out
        for k, v in object.__getattribute__(self, "__dict__").items():
            out.__dict__[k] = copy.deepcopy(v, memo)
        return out


class World(Guarded):
    def __init__(self, seed, people=("daniel", "elena", "leo", "mara")):
        self.seed = seed
        self.weather = Weather(seed)
        self.clock = water.DRY_AT
        self.tap = water.FILLED         # tap water stored in the house
        self.rain = 0.0                 # rain water in the bin
        self.caught = 0.0               # all the rain water the bin has caught
        self.bin_out = False
        self.level, self.level_since, self.holder = "as_before", water.DRY_AT, None
        self.deficit = {q: 0.0 for q in people}
        self.wet_until = {}
        self.places = {"neighbour": None, "far": {}}
        self.fixed = {}                 # facts fixed once, as the chronicle's: name -> {"value", "string", "at"}
        self.received = []              # (minute, litres): water carried in from outside

    # ---------- reading ----------
    def store(self):
        return {"tap": self.tap, "rain": self.rain}

    def thirst_stage(self, pid):
        return water.thirst_stage(self.deficit[pid], water.MASS[pid])

    def wet(self, pid, minute):
        return self.wet_until.get(pid, -1) > minute

    # ---------- the clock ----------
    def advance_to(self, minute, present):
        """Every minute from the clock to `minute`: rain into the bin while it is out, then each present person's
        drinking (tap water first), the house's washing and toilet (rain water first), and thirst."""
        present = [q for q in present if q in self.deficit]
        while self.clock < minute:
            t = self.clock
            if self.bin_out:
                r = self.weather.rate(t) * water.CATCH
                if r:
                    got = min(r, water.BIN - self.rain)
                    self.rain += got
                    self.caught += got
            use = water.LEVELS[self.level]
            other = (use["wash"] * len(present) + use["toilet"]) / 1440 if present else 0.0
            self._draw(other, ("rain", "tap"))
            for q in present:
                got = self._draw(use["drink"] / 1440, ("tap", "rain"))
                self.deficit[q] = max(0.0, self.deficit[q] + water.NET_LOSS / 1440 - got)
                if self.deficit[q] > 0:
                    self.deficit[q] -= self._draw(self.deficit[q], ("tap", "rain"))
            self.clock = t + 1

    def _draw(self, litres, order):
        got = 0.0
        for src in order:
            x = min(getattr(self, src), litres - got)
            if x > 0:
                setattr(self, src, getattr(self, src) - x)
                got += x
        return got

    # ---------- what people do to it ----------
    def set_level(self, level, minute, holder=None):
        self.level, self.level_since = level, minute
        self.holder = holder if level == "rationed" else None

    def put_bin_out(self, pid, minute, wet=True):
        self.bin_out = True
        if wet:
            self.wet_until[pid] = minute + water.WET_FOR

    def receive(self, litres, minute=None):
        self.tap += litres
        self.received.append((self.clock if minute is None else minute, litres))

    def house_water(self, place, minute):
        """What an empty house holds: drawn once, the first time it is needed, and kept as it is left. place:
        "neighbour" or ("far", i)."""
        if place == "neighbour":
            got = self.places["neighbour"]
            name, key = "neighbour_water", "neighbour"
        else:
            got = self.places["far"].get(place[1])
            name, key = f"far_house_{place[1]}_water", f"far:{place[1]}"
        if got is None:
            held = water.house_water(self.seed, key)
            got = {"held": held, "left_by": dict(held), "left": sum(held.values())}
            if place == "neighbour":
                self.places["neighbour"] = got
            else:
                self.places["far"][place[1]] = got
            self.fixed[name] = {"value": dict(held), "string": f"{self.seed}:world:water:{key}:*", "at": minute}
        return got

    def carry_home(self, place, litres, minute):
        """Up to `litres` of a house's water, carried away; returns what was taken."""
        got = self.house_water(place, minute)
        took = water.take_from(got["left_by"], litres)
        got["left"] = sum(got["left_by"].values())
        return took

    # ---------- what comes next ----------
    def next_change(self, start, end, present):
        """The first minute in (start, end] at which the tap water runs out, the bin fills, or someone's thirst
        reaches a new stage, by a copy of the world run forward; or None."""
        if not self.deficit:
            return None
        ahead = copy.deepcopy(self)
        stages = {q: ahead.thirst_stage(q) for q in present if q in ahead.deficit}
        empty = ahead.tap <= 0
        t = start
        while t < end:
            ahead.advance_to(t + 1, present)
            t += 1
            if (ahead.tap <= 0) != empty or any(ahead.thirst_stage(q) != s for q, s in stages.items()):
                return t
        return None
