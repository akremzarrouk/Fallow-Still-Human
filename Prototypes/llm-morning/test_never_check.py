"""The six CHECKABLE-NOW Never checks (design/never-checker-design.md, commit 6d6abc1).
Reads cached transcripts only. No network, no quota.

    python -m unittest -v test_never_check

Two kinds of test:
- ReplayVerdicts: one test per (replay, item), asserting the verdict predicted in the design's §3 table,
  frozen before any check existed. A test whose check disagrees with its prediction is marked as an
  expected failure in DISAGREEMENTS with the reason; neither the check nor the prediction is changed.
- SyntheticTraces: a small hand-built morning per item that must fail it, and its mirror that must pass.
"""
import os
import unittest

import never_check

HERE = os.path.dirname(os.path.abspath(__file__))

# design/never-checker-design.md §2.
REPLAYS = {
    "S1": os.path.join(HERE, "runs", "v18", "daniel_ate_it-seed1.transcript.json"),
    "S2": os.path.join(HERE, "runs", "v22", "daniel_ate_it-seed2.transcript.json"),
    "S3": os.path.join(HERE, "runs", "v20", "daniel_ate_it-seed3.transcript.json"),
}

# design/never-checker-design.md §3, the six CHECKABLE-NOW rows, as frozen in 6d6abc1.
PREDICTED = {
    ("S1", "N2"): "pass", ("S2", "N2"): "pass", ("S3", "N2"): "pass",
    ("S1", "N3"): "pass", ("S2", "N3"): "pass", ("S3", "N3"): "pass",
    ("S1", "N4"): "pass", ("S2", "N4"): "pass", ("S3", "N4"): "pass",
    ("S1", "N6"): "pass", ("S2", "N6"): "pass", ("S3", "N6"): "pass",
    ("S1", "N8"): "pass", ("S2", "N8"): "pass", ("S3", "N8"): "pass",
    ("S1", "N11"): "pass", ("S2", "N11"): "fail", ("S3", "N11"): "fail",
}

# (replay, item) -> why the check, as specified, disagrees with the frozen prediction.
# Filled in only after the checker has run; see investigations/never-check-run-1.md.
DISAGREEMENTS = {}


class ReplayVerdicts(unittest.TestCase):
    _results = {}

    @classmethod
    def result(cls, replay):
        if replay not in cls._results:
            cls._results[replay] = never_check.check(never_check.load(REPLAYS[replay]))
        return cls._results[replay]


def _replay_test(replay, item, expected):
    def test(self):
        verdict, hits = self.result(replay)[item]
        self.assertEqual(verdict, expected, f"{replay} {item}: triggering acts {hits}")
    test.__doc__ = f"{replay} {item}: predicted {expected}"
    if (replay, item) in DISAGREEMENTS:
        test.__doc__ += f" (expected failure: {DISAGREEMENTS[replay, item]})"
        test = unittest.expectedFailure(test)
    return test


for (_r, _i), _v in PREDICTED.items():
    setattr(ReplayVerdicts, f"test_{_r}_{_i}", _replay_test(_r, _i, _v))


# ---- synthetic traces ------------------------------------------------------------------------------------

ALL = ["daniel", "elena", "leo", "mara"]


def act(minute, seq, who, option, words=None, room="kitchen", mode="model", new=None, came_of_it="",
        moved_to=None, audience=None, suspects="nobody"):
    return {"minute": minute, "who": who, "room": room, "option": option, "words": words,
            "audience": [p for p in ALL if p != who] if audience is None else audience,
            "mode": mode, "decided_at": [minute, seq], "said_at": [minute, seq], "came_of_it": came_of_it,
            "new": new, "new_why": None, "inner": None, "suspects": suspects, "angry_at": "nobody",
            "lull": None, "trip_moment": None, "moved_to": moved_to}


def morning(*acts, culprit="daniel"):
    """A top-level morning (no day1 key): turns grouped by minute, everyone in the kitchen."""
    turns = {}
    for a in acts:
        turns.setdefault(a["minute"], []).append(a)
    return {"seed": 0, "scenario": "daniel_ate_it", "culprit": culprit,
            "turns": [{"minute": m, "rooms": {"kitchen": list(ALL)}, "acts": turns[m]} for m in sorted(turns)]}


FOUND_NOTHING = "went through the room and found nothing."
OPENING = act(0, 1, "elena", "ask_who", "Who took it?", new=True)


class SyntheticTraces(unittest.TestCase):
    def verdict(self, m, item):
        return never_check.check(m)[item]

    def assertFails(self, m, item, hits):
        verdict, got = self.verdict(m, item)
        self.assertEqual(verdict, "fail")
        self.assertEqual([tuple(h) for h in got], hits)

    def assertPasses(self, m, item):
        verdict, got = self.verdict(m, item)
        self.assertEqual((verdict, got), ("pass", []))

    def test_load_reads_day1_or_the_top_level(self):
        m = morning(OPENING)
        self.assertIs(never_check.morning_of({"day1": m, "day2": {}}), m)
        self.assertIs(never_check.morning_of(m), m)

    # N2: Leo watches Mara finish searching the kitchen (found nothing), then searches it himself.
    def test_n2_searching_what_you_just_watched_fail(self):
        m = morning(OPENING, act(3, 2, "mara", "search", came_of_it="started going through the room."),
                    act(6, 3, "mara", "keep_searching", came_of_it=FOUND_NOTHING),
                    act(9, 4, "leo", "search", came_of_it="started going through the room."))
        self.assertFails(m, "N2", [(9, "leo", "search")])

    def test_n2_the_culprit_or_later_than_nine_minutes_passes(self):
        finish = [OPENING, act(3, 2, "mara", "search"), act(6, 3, "mara", "keep_searching", came_of_it=FOUND_NOTHING)]
        self.assertPasses(morning(*finish, act(9, 4, "daniel", "search")), "N2")
        self.assertPasses(morning(*finish, act(18, 4, "leo", "search")), "N2")
        # Not there to see it: Leo was not in the audience of Mara's finish.
        away = [OPENING, act(3, 2, "mara", "search"),
                act(6, 3, "mara", "keep_searching", came_of_it=FOUND_NOTHING, audience=["daniel", "elena"]),
                act(9, 4, "leo", "search")]
        self.assertPasses(morning(*away), "N2")

    # N3: Mara searches the kitchen to the end, then searches it again; Daniel confesses then denies;
    # Leo hears the confession then asks who took it.
    def test_n3_own_finished_search_again_fail(self):
        m = morning(OPENING, act(3, 2, "mara", "search"), act(6, 3, "mara", "keep_searching", came_of_it=FOUND_NOTHING),
                    act(12, 4, "mara", "search"))
        self.assertFails(m, "N3", [(12, "mara", "search")])

    def test_n3_deny_after_own_confession_fail(self):
        m = morning(OPENING, act(3, 2, "daniel", "confess", "I took it.", new=True),
                    act(6, 3, "daniel", "deny", "I didn't take it.", new=False))
        self.assertFails(m, "N3", [(6, "daniel", "deny")])

    def test_n3_ask_after_hearing_a_confession_fail(self):
        m = morning(OPENING, act(3, 2, "daniel", "confess", "I took it.", new=True),
                    act(6, 3, "leo", "ask_who", "Who took it?", new=False))
        self.assertFails(m, "N3", [(6, "leo", "ask_who")])

    def test_n3_an_unfinished_search_may_be_started_again(self):
        m = morning(OPENING, act(3, 2, "mara", "search"), act(6, 3, "mara", "ask_who", "Who?", new=False),
                    act(12, 4, "mara", "search"))
        self.assertPasses(m, "N3")

    # N4: Elena sits with Mara while Mara is searching; Leo sits with Daniel as Daniel leaves the room.
    def test_n4_sitting_with_someone_searching_fail(self):
        m = morning(OPENING, act(3, 2, "mara", "search", came_of_it="started going through the room."),
                    act(3, 3, "elena", "sit_mara"))
        self.assertFails(m, "N4", [(3, "elena", "sit_mara")])

    def test_n4_sitting_with_someone_leaving_fail(self):
        m = morning(OPENING, act(3, 2, "daniel", "go_brothers_room", moved_to="brothers_room"),
                    act(3, 3, "leo", "sit_daniel"))
        self.assertFails(m, "N4", [(3, "leo", "sit_daniel")])

    def test_n4_sitting_with_someone_who_finished_searching_passes(self):
        m = morning(OPENING, act(3, 2, "mara", "search"), act(6, 3, "mara", "keep_searching", came_of_it=FOUND_NOTHING),
                    act(9, 4, "elena", "sit_mara"))
        self.assertPasses(m, "N4")

    # N6: the count comes up short and nobody says a word at minute 0.
    def test_n6_silence_at_the_discovery_fail(self):
        m = morning(*[act(0, i + 1, p, "silent") for i, p in enumerate(ALL)], act(3, 5, "elena", "ask_who", "Who?"))
        self.assertFails(m, "N6", [(0, p, "silent") for p in ALL])

    def test_n6_one_line_at_minute_0_passes(self):
        self.assertPasses(morning(OPENING), "N6")

    # N8: the code, not the person, chose whom to reassure, and whom to suspect.
    def test_n8_a_target_chosen_outside_the_model_fail(self):
        m = morning(OPENING, act(3, 2, "elena", "reassure_mara", "It's alright.", mode="fallback"),
                    act(3, 3, "leo", "silent", mode="routine", suspects="Daniel"))
        self.assertFails(m, "N8", [(3, "elena", "reassure_mara"), (3, "leo", "silent")])

    def test_n8_routine_silence_and_model_targets_pass(self):
        m = morning(OPENING, act(3, 2, "elena", "reassure_mara", "It's alright.", suspects="Daniel"),
                    act(3, 3, "leo", "silent", mode="routine", suspects=None),
                    act(3, 4, "mara", "keep_searching", mode="routine", suspects=None))
        self.assertPasses(m, "N8")

    # N11: Daniel denies in three model acts running, none new; routine silence between does not break it.
    def test_n11_three_same_kind_none_new_fail(self):
        m = morning(OPENING, act(3, 2, "daniel", "deny", "No.", new=False),
                    act(6, 3, "daniel", "silent", mode="routine"),
                    act(9, 4, "daniel", "deny", "Not me.", new=False),
                    act(12, 5, "daniel", "deny", "I said no.", new=False))
        self.assertFails(m, "N11", [(3, "daniel", "deny"), (9, "daniel", "deny"), (12, "daniel", "deny")])

    def test_n11_reassure_all_and_one_person_are_one_kind(self):
        m = morning(OPENING, act(3, 2, "elena", "reassure_all", "We'll be fine.", new=False),
                    act(6, 3, "elena", "reassure_mara", "It's alright.", new=False),
                    act(9, 4, "elena", "reassure_all", "Together.", new=False))
        self.assertFails(m, "N11", [(3, "elena", "reassure_all"), (6, "elena", "reassure_mara"),
                                    (9, "elena", "reassure_all")])

    def test_n11_a_new_line_or_a_model_silence_breaks_it(self):
        one_new = morning(OPENING, act(3, 2, "daniel", "deny", "No.", new=False),
                          act(6, 3, "daniel", "deny", "No.", new=True),
                          act(9, 4, "daniel", "deny", "No.", new=False))
        self.assertPasses(one_new, "N11")
        broken = morning(OPENING, act(3, 2, "daniel", "deny", "No.", new=False),
                         act(6, 3, "daniel", "silent"),
                         act(9, 4, "daniel", "deny", "No.", new=False),
                         act(12, 5, "daniel", "deny", "No.", new=False))
        self.assertPasses(broken, "N11")


if __name__ == "__main__":
    unittest.main()
