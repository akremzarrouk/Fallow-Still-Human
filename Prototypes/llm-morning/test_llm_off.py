"""The LLM-off test (Docs/fable-audit-2026-11.md, section 8, amended 2026-11-11).

    python -m unittest -v test_llm_off

It plays the seven-day week (week.py), seeds 1, 2 and 3, twice each: with Leo played by code, and with a scripted
player as Leo. It passes only if every clause in force holds for every run. In force from step 3: L1 to L8 and L10
to L13. L9 comes into force in step 6 and is listed here as skipped.

The slow half of L8 (50 seeded weeks) is run apart: `python week.py --count 50` (about two minutes).

A week is kept only as what the clauses read (its transcript, its acts, a few numbers), never as the played objects,
so the test stays small in memory.
"""
import collections
import json
import os
import shutil
import tempfile
import time
import unittest

from test_brain import SEEDS, NoModel, Recording

import brain as brainmod
import data
import night
import play
import player
import week
from health import Health
from world import Morning

STARTED = time.monotonic()
ALLOWED = {"code", "routine", "player"}
QUIET_ACTS = ("silent", "sleep", "plate_eat", "cup_drink")      # staying put, sleeping, eating or drinking one's share
OFFERS = ("volunteer", "still_going", "volunteer_far")


def played(seed, who="code", again=0, remove=None, _kept={}):
    """One week, kept for the other clauses as a dict: "tr" (its transcript), "acts", "text" (the transcript as one
    string, for L2), "asked" (model calls), "days", "made" (every choice the brain made and what was offered),
    "spoken" (every line said), "events" (the world's), "bodies" (per day: the shelf at its start and end, the water
    log, the needs that crossed a line). who: "code" (Leo is played by code) or "script" (a scripted player: he
    accuses Daniel at minute 09 of day 1 and otherwise stays as he is; at night he sleeps)."""
    key = (seed, who, again, remove)
    if key not in _kept:
        b = Recording(seed)
        p = None
        if who == "script":
            rule = player.by_minute({(1, 9): ("accuse_daniel", "Daniel. Was it you?")}, default=("silent", None))
            p = player.ScriptedPlayer(rule)
        w = week.run(seed, brain=b, player=p, remove=remove)
        tr = w.transcript()
        _kept[key] = {
            "tr": tr, "acts": week.acts(tr), "text": json.dumps(tr, sort_keys=True), "asked": w.oracle.asked,
            "days": len(w.days), "made": b.made, "spoken": b.spoken, "events": week.world_events(w),
            "bodies": [{"start": m.start_portions, "end": m.portions, "water": [list(r) for r in m.quiet.water_log],
                        "needs": [dict(e) for e in m.quiet.need_events]} for m in w.days]}
        if again:                       # a second run is only compared with the first: keep its text and moods
            _kept[key] = {"text": _kept[key]["text"], "moods": tr["moods"]}
        del w, b, p
    return _kept[key]


def runs():
    return [(seed, who, played(seed, who)) for seed in SEEDS for who in ("code", "script")]


def able(tr, k, pid):
    """At home on day k, and not laid up as it began."""
    levels = tr["health"]["levels"].get(str(k), {})
    return pid in levels and levels[pid] < 2


class LlmOff(NoModel):
    # ---------- L1 ----------
    def test_l01_no_model(self):
        self.assertNotIn("GEMINI_API_KEY", os.environ)
        with self.assertRaises(ImportError):
            import google.genai     # noqa: F401
        for seed, who, r in runs():
            self.assertEqual(r["asked"], 0, f"seed {seed} {who}")
            self.assertEqual(r["days"], week.DAYS)
        with self.assertRaises(brainmod.LLMCalled):
            brainmod.CodeOracle(brainmod.CodeBrain(1)).ask("system", "prompt")

    # ---------- L2 ----------
    def test_l02_the_same_seed_gives_the_same_week(self):
        for seed in SEEDS:
            for who in ("code", "script"):
                first, second = played(seed, who), played(seed, who, again=1)
                self.assertEqual(first["text"], second["text"], f"seed {seed} {who}: the weeks differ")
                self.assertEqual(first["tr"]["moods"], second["moods"])
        self.assertGreaterEqual(len({played(seed)["text"] for seed in SEEDS}), 2)

    # ---------- L3 ----------
    def test_l03_code_decided_everything(self):
        for seed, who, r in runs():
            modes = collections.Counter(a["mode"] for a in r["acts"])
            self.assertLessEqual(set(modes), ALLOWED, f"seed {seed} {who}: {modes}")
            self.assertGreater(modes["code"], 0)
            if who == "script":
                self.assertGreater(modes["player"], 0)

    # ---------- L4 ----------
    def test_l04_every_move_was_offered_and_every_spoken_one_has_words_from_the_file(self):
        for seed, who, r in runs():
            for made in r["made"]:
                offered = dict(made["offered"])
                c = made["choice"]
                self.assertIn(c["option"], offered)
                if offered[c["option"]]:
                    self.assertTrue(c["say"])
                if c["say"]:
                    self.assertIn(c["say"], r["spoken"])

    def test_l04_a_session_in_code_mode_plays_and_resumes(self):
        """play.py --code: a day of Leo's from the terminal's side, then the same session resumed from its log."""
        root = tempfile.mkdtemp(prefix="llm-off-")
        try:
            def live(screen):
                if screen.kind == "plate":
                    return (screen.options[0], None), ["1"], 0.0
                if screen.minute is None:
                    return ("sleep" if screen.kind == "bedtime" else screen.options[0], None), [], 0.0
                return ("silent", None), ["1"], 0.0
            code, folder, info = play.session(seed=2, days=1, root=root, live=live, write=lambda *a: None, code=True)
            self.assertEqual(code, 0, info["stopped"])
            self.assertEqual(info["oracle"].asked, 0)
            self.assertGreaterEqual(len(info["player"].screens), 30)
            self.assertFalse(os.path.exists(os.path.join(root, "cache")))
            code, again, info = play.session(resume=folder, live=live, write=[].append)
            self.assertEqual(code, 0, info["stopped"])
            self.assertEqual(info["oracle"].asked, 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    # ---------- L5 ----------
    def alive(self, seed, who, r, script=False):
        tr, acts = r["tr"], r["acts"]
        empty = week.empty_days(tr)
        for k in sorted(empty):
            day = [a for a in acts if a["day"] == k]
            for pid in data.ORDER:
                if not able(tr, k, pid) or (script and pid == "leo"):   # the player's Leo does what the player does
                    continue
                mine = [a for a in day if a["who"] == pid and a["option"] not in ("silent", "sleep")
                        and a["mode"] != "routine"]
                self.assertGreaterEqual(len(mine), 3, f"seed {seed} {who} day {k}: {pid} did {[a['option'] for a in mine]}")
            spoken = sum(1 for a in day if a["words"])
            self.assertLessEqual(spoken, 80, f"seed {seed} {who} day {k}")
            if empty[k]:
                self.assertGreaterEqual(spoken, 8, f"seed {seed} {who} day {k}: {spoken} lines; {empty[k][:4]}")

    def test_l05_alive(self):
        for seed, who, r in runs():
            self.alive(seed, who, r, script=who == "script")

    # ---------- L6 ----------
    def not_stuck(self, seed, who, acts):
        per = collections.Counter((a["day"], a["who"], a["option"]) for a in acts
                                  if a["option"] not in QUIET_ACTS and a["mode"] != "routine")
        worst = per.most_common(1)
        self.assertTrue(not worst or worst[0][1] <= 2, f"seed {seed} {who}: {worst}")
        said = collections.Counter((a["day"], a["who"], a["words"]) for a in acts if a["words"] and a["mode"] != "player")
        twice = [k for k, n in said.items() if n > 1]
        self.assertFalse(twice, f"seed {seed} {who}: said twice in a day: {twice[:3]}")
        seen = set()
        for a in acts:          # a move that is once for the week comes back only with a new cause, named
            if a["mode"] != "code" or not (a["option"] in OFFERS or a["option"].startswith(("accuse_", "stop_"))):
                continue
            key = (a["who"], "far" if a["option"] == "volunteer_far" else "near" if a["option"] in OFFERS
                   else a["option"])
            if key in seen:
                self.assertTrue(a["why"].get("new_cause"), f"seed {seed} {who}: {a['who']} {a['option']} day {a['day']}")
            seen.add(key)
        one_move = 0
        for k in range(1, week.DAYS + 1):
            for pid in data.ORDER:
                mine = [a["option"] for a in acts if a["day"] == k and a["who"] == pid
                        and a["option"] not in QUIET_ACTS and a["mode"] != "routine"]
                if len(mine) >= 4 and collections.Counter(mine).most_common(1)[0][1] * 2 >= len(mine):
                    one_move += 1       # judged only where there are four acts or more: half of two is one
        self.assertLessEqual(one_move, 4, f"seed {seed} {who}: {one_move} person-days of one move")

    def test_l06_not_stuck(self):
        for seed, who, r in runs():
            self.not_stuck(seed, who, r["acts"])

    # ---------- L7 ----------
    def bodies(self, seed, who, r):
        for k, day in enumerate(r["bodies"], 1):
            if day["start"] > 0:
                ate = [a for a in r["acts"] if a["day"] == k and a["option"] in ("plate_eat", "eat", "share", "eat_given")]
                self.assertTrue(ate, f"seed {seed} {who} day {k}: food on the shelf and nobody ate")
            water = {row[0]: row[1] + row[2] for row in day["water"]}
            for e in day["needs"]:
                if e["need"] == "fast" and e["stage"] >= 3:
                    self.assertFalse(day["start"] > 0 and day["end"] > 0,
                                     f"seed {seed} {who} day {k}: {e['who']} thin and weak with food on the shelf")
                if e["need"] == "thirst" and e["stage"] >= 2:
                    stored = water[max(t for t in water if t <= e["minute"])] if water else 0
                    self.assertLessEqual(stored, 5, f"seed {seed} {who} day {k}: {e['who']} badly thirsty with "
                                                    f"{stored:.0f} L stored")

    def test_l07_bodies_make_sense(self):
        for seed, who, r in runs():
            self.bodies(seed, who, r)

    # ---------- L8 ----------
    def test_l08_no_run_of_empty_days(self):
        """The fast half: no three empty days in a row in these weeks. The slow half is `python week.py --count 50`:
        at most 1 empty day a week on average, and no week with three in a row."""
        for seed, who, r in runs():
            self.assertLess(week.longest_empty_run(week.empty_days(r["tr"])), 3, f"seed {seed} {who}")

    # ---------- L9: not yet in force ----------
    @unittest.skip("L9 Leo matters: in force from step 6")
    def test_l09_leo_matters(self):
        pass

    # ---------- L11 ----------
    def test_l11_carries_on_after_a_loss(self):
        for gone in ("elena", "daniel", "mara"):
            r = played(1, remove=(3, gone))
            tr, acts = r["tr"], r["acts"]
            self.assertEqual(r["days"], week.DAYS, f"{gone} removed: the week stopped")
            self.assertEqual(tr["removed"], {"day": 3, "who": gone})
            for made in r["made"]:
                if made["day"] >= 3:
                    aimed = [o for o, _ in made["offered"] if o.endswith(f"_{gone}") or f"_{gone}_" in o]
                    self.assertFalse(aimed, f"{gone} removed: {made['who']} was offered {aimed} on day {made['day']}")
            self.assertFalse([a for a in acts if a["day"] >= 3 and a["who"] == gone])
            tasks = {a["option"] for a in acts if a["day"] == 3 and a["option"].startswith("task_")}
            self.assertEqual(len(tasks), 4, f"{gone} removed: day 3's work was {sorted(tasks)}")
            self.assertLessEqual({a["mode"] for a in acts}, ALLOWED)
            self.alive(1, f"without {gone}", r)
            self.not_stuck(1, f"without {gone}", acts)
            self.bodies(1, f"without {gone}", r)
            moods = [m for k in ("3", "4") for m in tr["moods"][k].values()]
            self.assertTrue(any("not coming back" in (m["cause"] or "") for m in moods), f"{gone} removed: nobody grieved")

    # ---------- L12 ----------
    def test_l12_nothing_staged(self):
        for seed, who, r in runs():
            self.assertTrue(r["events"])
            for e in r["events"]:
                self.assertIsInstance(e["chance"], float, e)
                self.assertTrue(0.0 <= e["chance"] <= 1.0, e)
                self.assertTrue(e["conditions"], e)
        # No chance reads the number of the day: the same cause is drawn at the same chance on any day.
        chances = brainmod.load("chances.json")
        for name in ("rain_water", "wet_cold", "long_hunger", "boards", "carrying", "night_scare"):
            got = set()
            for day in range(1, 8):
                h = Health(1, chances)
                h.fall("mara", name, day, ["test"])
                got.add(h.draws[0]["chance"])
            self.assertEqual(got, {chances[name]["chance"]}, name)
        self.assertFalse(hasattr(week, "nudge"))        # the count did not call for one (week.py --count 50)

    # ---------- L13 ----------
    def test_l13_causes_and_choices(self):
        for seed, who, r in runs():
            tr = r["tr"]
            for e in tr["health"]["events"]:
                self.assertTrue(e["cause"], e)
            lost = set()
            for k in range(1, week.DAYS):
                for g in tr[f"night{k}"]["groups"]:
                    if g["lost"]:
                        lost.add(g["lost"])
                        chose = next(d for d in tr[f"night{k}"]["decisions"]
                                     if d["person"] == g["leader"] and d["ask"] == "bedtime")
                        self.assertIn(chose["option"], ("go_next_door", "go_further"), g)
            self.assertEqual(set(tr[f"day{week.DAYS}"]["away"]), lost, f"seed {seed} {who}: someone was lost at home")
            self.assertNotIn("leo", lost)
            for q, c in tr["health"]["now"].items():        # at home, never past bedridden
                self.assertLessEqual(c["level"], 3)

    def test_l13_a_draw_that_would_lose_leo_brings_him_back_hurt(self):
        b = brainmod.CodeBrain(1)
        b.health = Health(1, brainmod.load("chances.json"))
        m = Morning(brainmod.CodeOracle(b), 1)
        m.run()
        m.people["leo"].trip_heard["leo"] = (60, "volunteer", None, 5)      # he said he would go
        n = night.Night(m, m.oracle, draws={"trip:leo": 0.999, "order": ["leo", "daniel", "elena", "mara"]}).run()
        g = next(g for g in n.groups if "leo" in g["members"])
        self.assertEqual((g["lost"], g.get("spared")), (None, "leo"))
        self.assertNotIn("leo", n.away)
        rec = b.night_step(n)
        self.assertEqual(b.health.now["leo"]["cause"], "a night trip that nearly ended it")
        self.assertTrue(any("Leo came back badly hurt" in line for line in rec["health"]))

    # ---------- L10 ----------
    def test_l99_l10_the_whole_test_is_fast(self):
        """Named to run last: everything above, from the first import, in under 60 s."""
        for seed in SEEDS:
            for who in ("code", "script"):
                played(seed, who), played(seed, who, again=1)
        took = time.monotonic() - STARTED
        self.assertLess(took, 60, f"the LLM-off test took {took:.1f} s")


if __name__ == "__main__":
    unittest.main()
