"""The code brain's acceptance cases, B1 to B17 (Docs/fable-audit-2026-11.md, section 10.3, re-frozen 2026-11-11).

    python -m unittest -v test_brain

No model, no network, no key. B14's first half (the old suite, 349 tests) is run on its own:
    python -m unittest test_morning
"""
import collections
import hashlib
import json
import os
import shutil
import socket
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("GEMINI_API_KEY", None)

import data             # noqa: E402
import gemini           # noqa: E402
import morning          # noqa: E402
import night            # noqa: E402
import player           # noqa: E402
import truth            # noqa: E402
from talk import aimed_at   # noqa: E402
from world import Morning, Option   # noqa: E402

import brain as brainmod    # noqa: E402

SEEDS = (1, 2, 3)
DAYS = 10
MOODS = ("steady", "on edge", "low", "warm", "restless")
# B14: the fake 4-day run of seed 1 without a brain (reports/play_fix2.md:20-21; reproduced 2026-11-11).
STORY_SHA = "3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9"
TRANSCRIPT_SHA = "dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8"


class Recording(brainmod.CodeBrain):
    """The brain, keeping every choice it made and what was offered (B4, B17)."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.made = []

    def choose(self, p, opts, ctx):
        choice = super().choose(p, opts, ctx)
        self.made.append({"who": p.id, "day": ctx["day"], "offered": [(o.id, o.speech) for o in opts],
                          "keys": dict(self.last_keys), "choice": choice})
        return choice


_RUNS = {}
_TIMES = {}


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def code_run(seed, scenario=data.DEFAULT_SCENARIO, days=DAYS, tilt=True, again=0):
    """One run in code mode, kept for the other cases: (meta, exit code, transcript, its bytes, the story's bytes,
    the brain)."""
    key = (seed, scenario, days, tilt, again)
    if key not in _RUNS:
        root = tempfile.mkdtemp(prefix="brain-test-")
        try:
            b = Recording(seed, tilt=tilt)
            started = time.monotonic()
            meta, code = morning.run(seed, brain=b, runs_dir=root, cache_dir=root, quiet=True, scenario=scenario,
                                     days=days)
            _TIMES[key] = time.monotonic() - started
            name = f"{scenario}-seed{seed}"
            raw = read_bytes(os.path.join(root, f"{name}.transcript.json")) if code == 0 else b""
            story = read_bytes(os.path.join(root, f"{name}.md")) if code == 0 else b""
            _RUNS[key] = (meta, code, json.loads(raw) if raw else None, raw, story, b)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    return _RUNS[key]


def acts(transcript):
    """Every act of a run: {"day", "who", "option", "mode", "words", "minute", "why", "mood"}. A night belongs to the
    day it follows."""
    out = []
    for key, scene in transcript.items():
        if key.startswith("day"):
            k = int(key[3:])
            for turn in scene["turns"]:
                for a in turn["acts"]:
                    out.append({"day": k, "who": a["who"], "option": a["option"], "mode": a["mode"],
                                "words": a["words"], "minute": a["minute"], "why": a.get("why"), "mood": a.get("mood")})
        elif key.startswith("night"):
            k = int(key[5:] or 1)
            for d in scene["decisions"]:
                out.append({"day": k, "who": d["person"], "option": d["option"], "mode": d["mode"],
                            "words": d.get("say"), "minute": None, "why": d.get("why"), "mood": d.get("mood")})
    return out


def blocked(*a, **k):
    raise AssertionError("the game tried to reach a model or the network")


class NoModel(unittest.TestCase):
    """Every case runs with the key unset, the network shut and the model client unbuildable (L1)."""

    @classmethod
    def setUpClass(cls):
        cls._connect = socket.socket.connect
        cls._client = gemini.GeminiClient.__init__
        cls._genai = sys.modules.get("google.genai", "absent")
        socket.socket.connect = blocked
        gemini.GeminiClient.__init__ = blocked
        sys.modules["google.genai"] = None          # importing it now raises ImportError
        os.environ.pop("GEMINI_API_KEY", None)

    @classmethod
    def tearDownClass(cls):
        socket.socket.connect = cls._connect
        gemini.GeminiClient.__init__ = cls._client
        if cls._genai == "absent":
            sys.modules.pop("google.genai", None)
        else:
            sys.modules["google.genai"] = cls._genai


class RunCases(NoModel):
    def test_b01_ten_days_with_no_model_and_under_a_minute(self):
        for seed in SEEDS:
            meta, code, tr, _, _, b = code_run(seed)
            self.assertEqual(code, 0, f"seed {seed}: {meta}")
            self.assertEqual(meta["model"], "code")
            self.assertEqual(meta["model_calls"], 0)
            self.assertEqual(meta["api_requests"], 0)
            self.assertEqual(meta["days"], DAYS)
            self.assertGreater(len(b.made), 0)
        total = sum(_TIMES[(seed, data.DEFAULT_SCENARIO, DAYS, True, 0)] for seed in SEEDS)
        self.assertLess(total, 60, f"three ten-day runs took {total:.1f} s")
        self.assertNotIn("GEMINI_API_KEY", os.environ)

    def test_b02_the_same_seed_gives_the_same_week(self):
        first, second = code_run(2), code_run(2, again=1)
        self.assertEqual(first[3], second[3])
        self.assertEqual(first[4], second[4])
        self.assertNotEqual(code_run(1)[3], code_run(2)[3])

    def test_b03_code_decided_everything(self):
        for seed in SEEDS:
            modes = collections.Counter(a["mode"] for a in acts(code_run(seed)[2]))
            self.assertLessEqual(set(modes), {"code", "routine"}, f"seed {seed}: {modes}")
            self.assertGreater(modes["code"], 0)

    def test_b04_every_choice_was_offered_and_every_spoken_one_has_words(self):
        for seed in SEEDS:
            b = code_run(seed)[5]
            lines = set(b.spoken)
            for made in b.made:
                offered = dict(made["offered"])
                c = made["choice"]
                self.assertIn(c["option"], offered)
                if offered[c["option"]]:
                    self.assertTrue(c["say"] and c["say"].strip(), f"{made['who']} {c['option']} has no words")
                if c["say"]:
                    self.assertNotIn("[fake", c["say"])
                    self.assertIn(c["say"], lines, "words that are not from the line file")
            for a in acts(code_run(seed)[2]):
                self.assertNotIn("[fake", a["words"] or "")

    def test_b06_leo_cannot_tell_who_took_it(self):
        first = {}
        for scenario in ("daniel_ate_it", "mara_ate_it"):
            tr = code_run(2, scenario=scenario, days=3)[2]
            first[scenario] = next(a["option"] for a in acts(tr) if a["day"] == 1 and a["who"] == "leo")
        self.assertEqual(first["daniel_ate_it"], first["mara_ate_it"])

    def test_b07_elena_asks_first(self):
        for seed in SEEDS:
            first = next(a for a in acts(code_run(seed)[2]) if a["day"] == 1 and a["who"] == "elena")
            self.assertEqual((first["minute"], first["option"]), (0, "ask_who"), f"seed {seed}")

    def test_b08_elena_accused_by_leo_answers_leo(self):
        for seed in SEEDS:
            b = brainmod.CodeBrain(seed)
            rule = player.by_minute({9: ("accuse_elena", "I think it was you, Mom.")}, default=("silent", None))
            out = player.play_days(brainmod.CodeOracle(b), seed, player.ScriptedPlayer(rule), days=1)
            ds = [d for rec in out["day1"].log for d in rec["decisions"]]
            said = next(d for d in ds if d["person"] == "leo" and d["option"] == "accuse_elena")
            self.assertEqual(said["minute"] if "minute" in said else 9, 9)
            after = next(d for d in ds if d["person"] == "elena" and d["seq"] > said["seq"])
            self.assertEqual(after["option"], "deny", f"seed {seed}: {after['option']}")
            self.assertNotEqual(after["option"], "reassure_all")
            self.assertNotEqual(aimed_at(after["option"]), "daniel")
            self.assertEqual(after["mode"], "code")

    def test_b09_daniel_never_looks_for_the_can_he_ate(self):
        for seed in SEEDS:
            his = [a["option"] for a in acts(code_run(seed)[2]) if a["who"] == "daniel"]
            self.assertTrue(his)
            self.assertFalse({"ask_who", "search", "keep_searching"} & set(his), f"seed {seed}")

    def test_b12_nobody_does_the_same_thing_three_times_in_a_day(self):
        for seed in SEEDS:
            n = collections.Counter((a["day"], a["who"], a["option"]) for a in acts(code_run(seed)[2])
                                    if a["mode"] == "code" and a["option"] not in ("silent", "sleep"))
            worst = n.most_common(1)
            self.assertTrue(not worst or worst[0][1] <= 2, f"seed {seed}: {worst}")

    def test_b14_without_a_brain_nothing_has_changed(self):
        root = tempfile.mkdtemp(prefix="brain-test-")
        try:
            meta, code = morning.run(1, fake=True, runs_dir=root, cache_dir=root, quiet=True, days=4)
            self.assertEqual(code, 0)
            self.assertEqual(meta["story_sha256"], STORY_SHA)
            raw = read_bytes(os.path.join(root, "daniel_ate_it-seed1.transcript.json"))
            self.assertEqual(hashlib.sha256(raw).hexdigest(), TRANSCRIPT_SHA)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_b15_the_mood_is_repeatable_small_and_has_causes(self):
        self.assertLessEqual(brainmod.CodeBrain(1).weights["tilt"], 0.04)
        for seed in SEEDS:
            tr, again = code_run(seed)[2], code_run(seed, again=1)[2]
            self.assertEqual(tr["moods"], again["moods"])
            by_person = collections.defaultdict(set)
            for day, people in tr["moods"].items():
                for pid, m in people.items():
                    self.assertIn(m["mood"], MOODS)
                    by_person[pid].add(m["mood"])
                    if m["mood"] != "steady":
                        self.assertTrue(m["cause"] or m["seeded"], f"seed {seed} day {day} {pid}: {m}")
            self.assertEqual(set(by_person), set(data.ORDER))
            for pid, moods in by_person.items():
                self.assertGreaterEqual(len(moods), 2, f"seed {seed}: {pid} had only {moods} in {DAYS} days")
            for a in acts(tr):
                if a["mode"] == "code":
                    self.assertLessEqual(abs(a["why"]["tilt"]), 0.04 + 1e-9)

    def test_b17_every_decision_keeps_its_reasons_and_every_option_has_a_weight(self):
        for seed in SEEDS:
            _, _, tr, _, _, b = code_run(seed)
            for a in acts(tr):
                if a["mode"] != "code":
                    continue
                self.assertIsInstance(a["why"]["terms"], list)
                self.assertLessEqual(len(a["why"]["terms"]), 3)
                self.assertIn(a["mood"]["mood"], MOODS)
            for made in b.made:
                for option, _ in made["offered"]:
                    self.assertTrue(made["keys"].get(option), f"{option} has no weight")


class UnitCases(NoModel):
    def setUp(self):
        self.m = Morning(None, 1)
        self.b = brainmod.CodeBrain(1)

    def person(self, pid):
        return self.m.people[pid]

    def choose(self, pid, mood="steady", opts=None, ctx=None):
        p = self.person(pid)
        self.b.set_mood(pid, 1, mood)
        opts = self.m.options_for(p) if opts is None else opts
        ctx = ctx or self.b.context_of(self.m, p, 0, opts)
        return self.b.choose(p, opts, ctx)

    def test_b05_what_the_brain_sees_is_built_with_the_world_out_of_reach(self):
        seen = []
        inner = self.b._context
        self.b._context = lambda *a, **k: (seen.append(truth._PROMPTING[0]), inner(*a, **k))[1]
        p = self.person("leo")
        self.b.context_of(self.m, p, 0, self.m.options_for(p))
        self.assertEqual(seen, [1])
        self.assertEqual(truth._PROMPTING[0], 0)

    # ---------- B10, B11, B13, each as a function of the mood, for B16 ----------
    def daniel_asked(self, mood):
        self.setUp()
        p = self.person("daniel")
        p.heard_question = True
        p.heard.append({"seq": 1, "who": "elena", "kind": "ask", "target": None})
        self.assertEqual(p.guilt, 1)
        return self.choose("daniel", mood)["option"], "deny"

    def daniel_accused(self, mood):
        self.setUp()
        p = self.person("daniel")
        p.guilt = 3
        p.heard_question = True
        p.heard.append({"seq": 1, "who": "leo", "kind": "accuse", "target": "daniel"})
        p.addressed = {"seq": 1, "who": "leo", "accused": True}
        p.owed = {"who": "leo", "turn": 0, "room": "kitchen"}
        p.accused_by["leo"] = 0
        return self.choose("daniel", mood)["option"], "confess"

    def elena_with_mara_hungry(self, mood):
        self.setUp()
        self.assertEqual(self.choose("elena", mood)["option"], "ask_who")      # she has asked; then:
        self.person("mara").hunger = 0.75
        self.assertEqual(self.m.portions, 2)
        return self.choose("elena", mood)["option"], "share"

    def mara_alone_starving(self, mood):
        self.setUp()
        for q in ("daniel", "elena", "leo"):
            self.person(q).room = "back_room"
        self.person("mara").hunger = 0.9
        return self.choose("mara", mood)["option"], "eat"

    def leo_alone_very_hungry(self, mood):
        self.setUp()
        for q in ("daniel", "elena", "mara"):
            self.person(q).room = "back_room"
        self.person("leo").hunger = 0.75
        got = self.choose("leo", mood)["option"]
        return ("eat" if got == "eat" else "not eat"), "not eat"

    def bedtime(self, pid, mood):
        self.setUp()
        p = self.person(pid)
        if pid == "daniel":
            p.trip_heard["daniel"] = (60, "volunteer", None, 5)
            p.needs = {"fast_stage": 1, "debt_stage": 0}
        opts = [Option(i, label) for i, label in night.BEDTIME]
        ctx = self.b.night_context(1, 1, "bedtime", p)
        return self.choose(pid, mood, opts, ctx)["option"], {"daniel": "go_next_door", "mara": "lie_awake",
                                                             "leo": "sleep"}[pid]

    def cases(self):
        return [("B10 Daniel asked, guilt 1", self.daniel_asked),
                ("B10 Daniel accused, guilt 3", self.daniel_accused),
                ("B11 Elena, Mara very hungry", self.elena_with_mara_hungry),
                ("B11 Mara alone, starving", self.mara_alone_starving),
                ("B11 Leo alone, very hungry", self.leo_alone_very_hungry),
                ("B13 Daniel at bedtime", lambda mood: self.bedtime("daniel", mood)),
                ("B13 Mara at bedtime", lambda mood: self.bedtime("mara", mood)),
                ("B13 Leo at bedtime", lambda mood: self.bedtime("leo", mood))]

    def test_b10_daniel_denies_at_guilt_1_and_confesses_at_guilt_3(self):
        self.assertEqual(*self.daniel_asked("steady"))
        self.assertEqual(*self.daniel_accused("steady"))

    def test_b11_food(self):
        self.assertEqual(*self.elena_with_mara_hungry("steady"))
        self.assertEqual(*self.mara_alone_starving("steady"))
        self.assertEqual(*self.leo_alone_very_hungry("steady"))

    def test_b13_bedtime(self):
        for pid in ("daniel", "mara", "leo"):
            self.assertEqual(*self.bedtime(pid, "steady"), pid)

    def test_b16_the_unit_cases_hold_under_every_mood_with_a_lead_of_015(self):
        for name, case in self.cases():
            for mood in MOODS:
                got, expected = case(mood)
                self.assertEqual(got, expected, f"{name}, mood {mood}")
            got, expected = case("steady")
            scores = self.b.last_scores
            if expected == "not eat":
                lead = max(v for k, v in scores.items() if k != "eat") - scores["eat"]
            else:
                lead = scores[expected] - max(v for k, v in scores.items() if k != expected)
            self.assertGreaterEqual(round(lead, 6), 0.15, f"{name}: lead {lead:.3f}")


if __name__ == "__main__":
    unittest.main()
