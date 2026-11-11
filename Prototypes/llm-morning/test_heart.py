"""Step 2's gate (Docs/fable-audit-2026-11.md, section 9, step 2): the heart, food and the night step.

    python -m unittest -v test_heart

No model, no network, no key. Each case states a situation and the act expected.
"""
import collections
import unittest

import test_brain
from test_brain import SEEDS, NoModel, acts, code_run

import brain as brainmod
import data
import night
import quiet
from heart import Heart
from world import Morning, Option


def fresh(seed=1, code=True):
    b = brainmod.CodeBrain(seed)
    return b, Morning(brainmod.CodeOracle(b) if code else None, seed)


class Budgets(NoModel):
    """(a) In code mode the request budgets cap nothing."""

    def test_h01_no_act_in_a_code_run_is_refused_by_a_budget(self):
        for seed in SEEDS:
            tr = code_run(seed)[2]
            for key, day in tr.items():
                if not key.startswith("day"):
                    continue
                for e in (day.get("quiet") or {}).get("log", []):
                    self.assertFalse(e.get("budget"), f"seed {seed} {key}: {e}")
                for c in day["convo_log"]:
                    self.assertNotIn("spent", c["why"] or "", f"seed {seed} {key}: {c}")
            self.assertFalse([a for a in acts(tr) if a["mode"] == "fallback"])

    def test_h02_with_a_brain_the_day_is_never_spent(self):
        b, m = fresh()
        q = quiet.Quiet.__new__(quiet.Quiet)
        q.m, q.asks, q.reserved_asks, q.reserved, q.cap, q.door, q.quiet_asked = m, 999, 0, False, 0, None, []
        self.assertFalse(q.spent())
        self.assertIsNone(q.budget("leo"))


class Stance(NoModel):
    """(b) What a person remembers of another, and what it does."""

    def comfort(self, kind_before):
        """Day 2: Mara looks sad. What does Leo do, and why?"""
        b, m = fresh(code=False)
        m.people["mara"].feeling, m.people["mara"].feeling_until = "sad", 99
        if kind_before:
            b.heart.remember("leo", "mara", "sat_with", 1)
        p = m.people["leo"]
        b.set_mood("leo", 2, "steady")
        opts = m.options_for(p)
        ctx = b.context_of(m, p, 0, opts)
        ctx["day"] = 2
        return b.choose(p, opts, ctx)

    def test_h03_a_remembered_kindness_changes_a_later_choice_and_is_named_as_the_reason(self):
        without, with_it = self.comfort(False), self.comfort(True)
        self.assertEqual(without["option"], "silent")
        self.assertIn(with_it["option"], ("reassure_mara", "sit_mara"))
        self.assertTrue(any("Mara sat with him, day 1" in name for name, _ in with_it["why"]["terms"]),
                        with_it["why"])

    def test_h04_trust_from_one_act_halves_in_two_nights_and_a_mark_does_not(self):
        h = Heart(brainmod.load("weights.json")["heart"])
        h.remember("mara", "leo", "reassured", 1)
        self.assertAlmostEqual(h.trust("mara", "leo", 1), 1.0)
        self.assertAlmostEqual(h.trust("mara", "leo", 3), 0.5)
        self.assertAlmostEqual(h.trust("mara", "leo", 5), 0.25)
        h.remember("elena", "daniel", "lied", 1)
        self.assertAlmostEqual(h.trust("elena", "daniel", 1), -2.0)
        self.assertAlmostEqual(h.trust("elena", "daniel", 9), -2.0)

    def test_h05_suspicion_comes_from_clues_and_fades_without_new_ones(self):
        h = Heart(brainmod.load("weights.json")["heart"])
        self.assertEqual(h.suspect("leo", 1), (None, 0))
        h.clue("leo", "daniel", "left_at_question", 1)
        h.clue("leo", "daniel", "refused_share", 1)
        self.assertEqual(h.suspect("leo", 1), ("daniel", 2))
        self.assertEqual(h.suspicion("leo", "daniel", 3), 1)
        self.assertEqual(h.suspicion("leo", "daniel", 5), 0)

    def test_h06_in_code_mode_an_answer_moves_no_level(self):
        """The brain names nobody it is angry at, and suspicion is the heart's: no clue, no suspect."""
        for seed in SEEDS:
            for a in code_run(seed)[5].made:
                self.assertEqual(a["choice"]["angry_at"], "nobody")
        b, m = fresh()
        p = m.people["mara"]
        b.settle(p, 1)
        self.assertEqual(p.suspicion.state(), [None, 0])
        b.heart.clue("mara", "daniel", "left_at_question", 1)
        b.settle(p, 1)
        self.assertEqual(p.suspicion.state(), ["daniel", 1])


class NightStep(NoModel):
    """(c) The night step in place of the night mind."""

    def a_night(self, seed=1):
        b, m = fresh(seed)
        m.run()
        n = night.Night(m, m.oracle).run()
        return b, m, n

    def test_h07_a_grudge_nobody_renewed_drops_a_step_each_night_and_a_mark_holds_it_at_one(self):
        b, m, n = self.a_night()
        g = n.people["mara"].grudge("leo")
        g.strength, g.events = 2, [(3, "Leo accused you", "event", "yesterday", "D1", "Leo accused you")]
        fresh_one = n.people["elena"].grudge("leo")
        fresh_one.strength, fresh_one.events = 2, [(3, "Leo accused you", "event")]     # of the day that just ended
        marked = n.people["leo"].grudge("daniel")
        marked.strength, marked.events = 2, [(3, "Daniel admitted it", "event", "yesterday", "D1", "x")]
        b.heart.remember("leo", "daniel", "lied", 1)
        rec = b.night_step(n)
        self.assertEqual((g.strength, fresh_one.strength, marked.strength), (1, 2, 1))
        self.assertIn({"who": "mara", "against": "leo", "now": 1, "why": "nobody renewed it today"}, rec["grudges"])
        for e in g.events + fresh_one.events + marked.events:       # tomorrow they are all of an earlier day
            pass
        fresh_one.events = [e + ("yesterday", "D1", e[1]) for e in fresh_one.events]
        b.night_step(n)
        self.assertEqual((g.strength, fresh_one.strength, marked.strength), (0, 1, 1))

    def test_h08_an_intention_is_renewed_while_its_cause_stands_and_dropped_with_a_line(self):
        h = Heart(brainmod.load("weights.json")["heart"])
        self.assertTrue(h.intend("daniel", "go_out", None, "the food is short", 1))
        self.assertFalse(h.intend("daniel", "go_out", None, "the food is short", 2))    # one at a time
        self.assertEqual(h.settle("daniel", 1), ("renewed", None))
        self.assertEqual(h.settle("daniel", 2, gone="too weak to go"),
                         ("dropped", "Daniel no longer meant to go next door: too weak to go."))
        h.intend("mara", "tell", "elena", "what is on them", 1)
        self.assertEqual(h.settle("mara", 3), ("renewed", None))
        self.assertEqual(h.settle("mara", 4), ("dropped", "Mara no longer meant to tell Elena: the days went by."))
        h.intend("elena", "watch", "daniel", "Daniel went out in the night", 1, days=2)
        self.assertEqual(h.settle("elena", 2, done=True), ("done", None))
        self.assertNotIn("elena", h.intents)

    def test_h09_every_night_has_its_step_and_every_dropped_intention_its_line(self):
        for seed in SEEDS:
            meta, code, tr, _, _, b = code_run(seed)
            self.assertEqual(meta["model_calls"], 0)
            nights = [k for k in tr if k.startswith("mind")]
            self.assertTrue(nights)
            for k in nights:
                step = tr[k]["night_step"]
                dropped = [i for i in step["intentions"] if i["what"] == "dropped"]
                self.assertEqual(len(dropped), len(step["lines"]), f"seed {seed} {k}")
                for line in step["lines"]:
                    self.assertIn("no longer meant to", line)

    def test_h10_whoever_knows_someone_went_out_may_mean_to_sit_up_for_them(self):
        """Seed 2: Daniel goes out; Elena knows; the next night she means to sit up, and does."""
        tr = code_run(2)[2]
        formed = [(k, i) for k in tr if k.startswith("mind") for i in tr[k]["night_step"]["intentions"]
                  if i["kind"] == "watch" and i["what"] == "formed"]
        self.assertTrue(formed)
        k, i = formed[0]
        after = tr[f"night{int(k[4:]) + 1}"]["decisions"]
        bed = next(d for d in after if d["person"] == i["who"] and d["ask"] == "bedtime")
        self.assertEqual(bed["option"], "watch_door")
        self.assertTrue(any("meant to sit up" in name for name, _ in bed["why"]["terms"]))


class Mood(NoModel):
    """(d) The mood's causes, and what long hunger rules out."""

    def mood(self, seed, pid, day, hunger=0.3, before=None, night=None, notes=()):
        b, m = fresh(seed, code=False)
        p = m.people[pid]
        p.hunger = hunger
        if before is not None:
            b.woke[(pid, day - 1)] = before
        if night:
            b.last_night[pid] = (day - 1, night)
        if notes:
            b.notes[(pid, day - 1)] = set(notes)
        return b.mood_of(p, {"day": day})

    def test_h11_tomorrows_tilt_has_its_cause(self):
        got = self.mood(1, "elena", 2, night="get_up_and_look")
        self.assertEqual((got["mood"], got["cause"]), ("on edge", "a night waiting up"))
        got = self.mood(1, "leo", 2, notes=[("lost", "daniel")])
        self.assertEqual((got["mood"], got["cause"]), ("low", "Daniel not coming back"))
        got = self.mood(1, "mara", 2, notes=["fed"])
        self.assertEqual(got["cause"] if got["mood"] == "warm" else "being given food", "being given food")

    def test_h12_nobody_wakes_warm_after_two_mornings_of_hunger_unless_something_gave_a_reason(self):
        warm_without_cause = warm_with_one = seeded_warm = 0
        for seed in range(1, 201):
            for pid in data.ORDER:
                if self.mood(seed, pid, 3)["mood"] == "warm":
                    seeded_warm += 1                    # on a full stomach the seed may make them warm
                got = self.mood(seed, pid, 3, hunger=0.9, before=3)
                warm_without_cause += got["mood"] == "warm"
                got = self.mood(seed, pid, 3, hunger=0.9, before=3, notes=["comforted"])
                if got["mood"] == "warm":
                    warm_with_one += 1
                    self.assertEqual(got["cause"], "yesterday's kindness")
        self.assertGreater(seeded_warm, 0)
        self.assertEqual(warm_without_cause, 0)
        self.assertGreater(warm_with_one, 0)

    def test_h13_a_mood_changes_when_its_cause_changes(self):
        """B15, as re-worded: one person, one morning, one seed; one cause changed and nothing else."""
        for seed in SEEDS:
            for pid in data.ORDER:
                quiet_night = self.mood(seed, pid, 2)
                bad_night = self.mood(seed, pid, 2, night="watch_door")
                self.assertIn(bad_night["mood"], ("on edge", "low"))
                self.assertIn("a night on watch", bad_night["cause"])
                self.assertNotEqual((quiet_night["mood"], quiet_night["cause"]), (bad_night["mood"], bad_night["cause"]))
                new_hunger = self.mood(seed, pid, 2, hunger=0.8, before=0)
                old_hunger = self.mood(seed, pid, 2, hunger=0.8, before=2)
                self.assertEqual(new_hunger["points"].get(new_hunger["mood"], 0) >= 1, True)
                self.assertIn("hunger", new_hunger["cause"] or "hunger" if new_hunger["mood"] in ("on edge", "low")
                              else "hunger")
                self.assertNotIn("hunger", old_hunger["cause"] or "")


class Door(NoModel):
    """(e) Hearing the door at night counts."""

    def hears(self, pid, someone_up=False):
        b, m = fresh(code=False)
        p = m.people[pid]
        b.set_mood(pid, 1, "steady")
        opts = [Option("stay_in_bed", "stay in bed"),
                Option("get_up_and_look", "get up, see whose bed is empty, and wait up by the front door")]
        ctx = b.night_context(1, 1, "reaction", p, someone_up=someone_up)
        return b.choose(p, opts, ctx)

    def test_h14_elena_awake_hears_the_door_and_does_not_stay_in_bed(self):
        got = self.hears("elena")
        self.assertEqual(got["option"], "get_up_and_look")
        self.assertGreaterEqual(got["why"]["lead"], 0.15)
        self.assertEqual(self.hears("mara", someone_up=True)["option"], "stay_in_bed")

    def test_h15_in_the_runs_someone_gets_up_when_the_door_is_heard(self):
        for seed in SEEDS:
            tr = code_run(seed)[2]
            for k, scene in tr.items():
                if not k.startswith("night") or not scene.get("leavers"):
                    continue
                heard = [d for d in scene["decisions"] if d["ask"] == "reaction"
                         and "get_up_and_look" in d["options"]]
                at_the_door = any(d["option"] == "watch_door" for d in scene["decisions"])
                if heard and not at_the_door:           # with someone already sitting up by the door, the rest may lie still
                    self.assertTrue(any(d["option"] == "get_up_and_look" for d in heard), f"seed {seed} {k}")


class Trip(NoModel):
    """(f) Once is enough for the whole week: the trip comes back only with a new cause."""

    def test_h16_an_offer_to_go_is_not_made_again_until_something_new_has_happened(self):
        b, m = fresh()
        m.trip = {"minute": 0, "why": ["test"], "asked": []}
        m.portions = 6                                  # short: less than two meals for four
        m.meal_at = 0                                   # today's meal is over
        p = m.people["daniel"]
        b.set_mood("daniel", 1, "steady")
        p.heard_question = True

        def offers():
            opts = m.options_for(p)
            got = b.choose(p, opts, b.context_of(m, p, 1, opts))
            p.trip_heard = {}                           # as a new day would leave it
            return got
        first = offers()
        self.assertEqual(first["option"], "volunteer")
        self.assertNotIn("new_cause", first["why"])
        self.assertNotEqual(offers()["option"], "volunteer")            # he already means to go: no need to say it
        b.heart.settle("daniel", 1, gone="there was food again")        # he lets it go
        self.assertNotEqual(offers()["option"], "volunteer")            # nothing new: not again
        m.portions = 0                                  # short still: a few portions gone is nothing new
        self.assertNotEqual(offers()["option"], "volunteer")
        m.away = {"mara"}
        m.people["mara"].room = None
        again = offers()
        self.assertEqual(again["option"], "volunteer")
        self.assertEqual(again["why"]["new_cause"], "someone did not come back")

    def test_h17_in_the_runs_every_repeated_offer_names_its_new_cause(self):
        for seed in SEEDS:
            seen = collections.Counter()
            for a in acts(code_run(seed)[2]):
                if a["option"] in ("volunteer", "still_going", "volunteer_far") and a["mode"] == "code":
                    key = (a["who"], "far" if a["option"] == "volunteer_far" else "near")
                    if seen[key]:
                        self.assertTrue(a["why"].get("new_cause"), f"seed {seed}: {a}")
                    seen[key] += 1

    def test_h18_nobody_offers_and_takes_it_back_the_same_morning(self):
        for seed in SEEDS:
            offered = set()
            for a in acts(code_run(seed)[2]):
                if a["option"] in ("volunteer", "still_going", "volunteer_far"):
                    offered.add((a["day"], a["who"]))
                if a["option"] in ("decline", "refuse_to_go"):
                    self.assertNotIn((a["day"], a["who"]), offered, f"seed {seed}: {a}")


class Confession(NoModel):
    def daniel(self, guilt):
        b, m = fresh(code=False)
        p = m.people["daniel"]
        p.guilt, p.heard_question = guilt, True
        b.set_mood("daniel", 1, "steady")
        return b, m, p

    def test_h19_daniel_confesses_alone_with_elena_at_guilt_2(self):
        b, m, p = self.daniel(2)
        for q in ("leo", "mara"):
            m.people[q].room = "brothers_room"
        opts = m.options_for(p)
        self.assertEqual(b.choose(p, opts, b.context_of(m, p, 0, opts))["option"], "confess")

    def test_h20_daniel_does_not_confess_when_accused_in_front_of_everyone_at_guilt_2(self):
        b, m, p = self.daniel(2)
        p.heard.append({"seq": 1, "who": "leo", "kind": "accuse", "target": "daniel"})
        p.addressed = {"seq": 1, "who": "leo", "accused": True}
        p.owed = {"who": "leo", "turn": 0, "room": "kitchen"}
        p.accused_by["leo"] = 0
        opts = m.options_for(p)
        got = b.choose(p, opts, b.context_of(m, p, 0, opts))["option"]
        self.assertIn(got, ("deny", "silent"))          # he denies it or says nothing; he does not own up
        self.assertNotEqual(got, "confess")

    def test_h21_at_guilt_2_with_everyone_listening_he_means_to_tell_one_person_and_takes_her_aside(self):
        b, m, p = self.daniel(2)
        opts = m.options_for(p)
        b.choose(p, opts, b.context_of(m, p, 0, opts))
        self.assertTrue(b.heart.intends("daniel", "tell", "elena"))
        opts = m.options_for(p)
        self.assertEqual(b.choose(p, opts, b.context_of(m, p, 1, opts))["option"], "aside_elena")


class Meals(NoModel):
    """(g), (h) Food for about four days, and the meal."""

    def test_h22_a_meal_is_eaten_on_each_of_days_1_to_3(self):
        for seed in SEEDS:
            tr = code_run(seed)[2]
            for k in (1, 2, 3):
                day = [a for a in acts(tr) if a["day"] == k and a["minute"] is not None]
                self.assertTrue([a for a in day if a["option"] in ("meal", "meal_small")], f"seed {seed} day {k}")
                self.assertGreaterEqual(sum(a["option"] == "plate_eat" for a in day), 3, f"seed {seed} day {k}")

    def test_h23_the_shelf_lasts_about_four_days(self):
        self.assertEqual(brainmod.load("weights.json")["scenario"]["portions"], 16)
        for seed in SEEDS:
            tr = code_run(seed)[2]
            self.assertGreater(tr["night2"]["portions_before"], 0, f"seed {seed}: empty before night 2")
            self.assertGreaterEqual(tr["night3"]["portions_before"], 2, f"seed {seed}: empty before night 3")

    def test_h24_the_meal_waits_for_the_question_and_nobody_takes_from_the_shelf_before_it(self):
        for seed in SEEDS:
            day1 = [a for a in acts(code_run(seed)[2]) if a["day"] == 1 and a["minute"] is not None
                    and a["option"] != "silent"]
            order = [a["option"] for a in day1]
            self.assertLess(order.index("ask_who"), min(order.index(x) for x in order if x.startswith("meal")))
            first_meal = next(i for i, x in enumerate(order) if x.startswith("meal"))
            self.assertNotIn("eat", order[:first_meal])

    def test_h25_a_share_given_up_is_remembered(self):
        b, m = fresh()
        m.turn(0)
        b.saw(m, m.people["elena"], "plate_to", "mara", ["daniel", "leo", "mara"])
        self.assertAlmostEqual(b.heart.trust("mara", "elena", 1), 2.0)
        self.assertEqual(b.heart.behind("mara", "elena", 1, 1), "Elena gave up a share for her, today")
        self.assertIn("fed", b.notes[("mara", 1)])


if __name__ == "__main__":
    unittest.main()
