"""The LLM-off test (Docs/fable-audit-2026-11.md, section 8, amended 2026-11-11).

    python -m unittest -v test_llm_off

It passes only if every clause in force holds for every run. In force from step 1: L1 to L4 and L10. L5 to L13 come
into force in steps 3 and 6 (section 9); until then they are listed here as skipped, with their step.

Until the seven-day week exists (step 3) the runs go through the existing day loop: ten days with Leo played by code,
and days 1 and 2 with a scripted player as Leo, which is as far as the existing loop plays a player (play.py: --days
1|2).
"""
import collections
import os
import shutil
import tempfile
import time
import unittest

import test_brain
from test_brain import DAYS, SEEDS, NoModel, Recording, acts, code_run

import brain as brainmod
import play
import player

STARTED = time.monotonic()
ALLOWED = {"code", "routine", "player"}


def scripted(seed, again=0, _kept={}):
    """Days 1 and 2 and their nights with a scripted Leo: he accuses Daniel at minute 09 of day 1, sits with Mara
    at minute 30, and otherwise stays as he is. Returns (the scenes, the brain, every decision in order)."""
    if (seed, again) not in _kept:
        b = Recording(seed)
        rule = player.by_minute({9: ("accuse_daniel", "Daniel. Was it you?"), 30: ("sit_mara", None)},
                                default=("silent", None))
        out = player.play_days(brainmod.CodeOracle(b), seed, player.ScriptedPlayer(rule), days=2)
        ds = []
        for k in (1, 2):
            ds += [{"scene": f"day{k}", "who": d["person"], "option": d["option"], "mode": d["mode"],
                    "say": d.get("say")} for rec in out[f"day{k}"].log for d in rec["decisions"]]
            ds += [{"scene": f"night{k}", "who": d["person"], "option": d["option"], "mode": d["mode"],
                    "say": d.get("say")} for d in out[f"night{k}"].decisions]
        _kept[(seed, again)] = (out, b, ds)
    return _kept[(seed, again)]


class LlmOff(NoModel):
    # ---------- L1 ----------
    def test_l01_no_model(self):
        self.assertNotIn("GEMINI_API_KEY", os.environ)
        with self.assertRaises(ImportError):
            import google.genai     # noqa: F401
        for seed in SEEDS:
            meta, code, _, _, _, _ = code_run(seed)
            self.assertEqual((code, meta["model"], meta["model_calls"], meta["api_requests"]), (0, "code", 0, 0))
            out, b, _ = scripted(seed)
            self.assertEqual(out["day1"].oracle.asked, 0)
        with self.assertRaises(brainmod.LLMCalled):
            brainmod.CodeOracle(brainmod.CodeBrain(1)).ask("system", "prompt")

    # ---------- L2 ----------
    def test_l02_the_same_seed_gives_the_same_week(self):
        for seed in SEEDS:
            first, second = code_run(seed), code_run(seed, again=1)
            self.assertEqual(first[3], second[3], f"seed {seed}: the transcripts differ")
            self.assertEqual(first[2]["moods"], second[2]["moods"])
            self.assertEqual(scripted(seed)[2], scripted(seed, again=1)[2], f"seed {seed}, scripted Leo")
        different = len({code_run(seed)[3] for seed in SEEDS})
        self.assertGreaterEqual(different, 2)

    # ---------- L3 ----------
    def test_l03_code_decided_everything(self):
        for seed in SEEDS:
            modes = collections.Counter(a["mode"] for a in acts(code_run(seed)[2]))
            self.assertLessEqual(set(modes), ALLOWED, f"seed {seed}: {modes}")
            modes = collections.Counter(d["mode"] for d in scripted(seed)[2])
            self.assertLessEqual(set(modes), ALLOWED, f"seed {seed}, scripted Leo: {modes}")
            self.assertGreater(modes["player"], 0)
            self.assertGreater(modes["code"], 0)

    # ---------- L4 ----------
    def test_l04_every_move_was_offered_and_every_spoken_one_has_words_from_the_file(self):
        for seed in SEEDS:
            for b in (code_run(seed)[5], scripted(seed)[1]):
                for made in b.made:
                    offered = dict(made["offered"])
                    c = made["choice"]
                    self.assertIn(c["option"], offered)
                    if offered[c["option"]]:
                        self.assertTrue(c["say"])
                    if c["say"]:
                        self.assertIn(c["say"], b.spoken)

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
            said = []
            code, again, info = play.session(resume=folder, live=live, write=said.append)
            self.assertEqual(code, 0, info["stopped"])
            self.assertEqual(info["oracle"].asked, 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    # ---------- L5 to L9, L11 to L13: not yet in force ----------
    @unittest.skip("L5 alive: in force from step 3")
    def test_l05_alive(self):
        pass

    @unittest.skip("L6 not stuck: in force from step 3")
    def test_l06_not_stuck(self):
        pass

    @unittest.skip("L7 bodies make sense: in force from step 3")
    def test_l07_bodies_make_sense(self):
        pass

    @unittest.skip("L8 no run of empty days: in force from step 3")
    def test_l08_no_run_of_empty_days(self):
        pass

    @unittest.skip("L9 Leo matters: in force from step 6")
    def test_l09_leo_matters(self):
        pass

    @unittest.skip("L11 carries on after a loss: in force from step 3")
    def test_l11_carries_on_after_a_loss(self):
        pass

    @unittest.skip("L12 nothing staged: in force from step 3")
    def test_l12_nothing_staged(self):
        pass

    @unittest.skip("L13 causes and choices: in force from step 3")
    def test_l13_causes_and_choices(self):
        pass

    # ---------- L10 ----------
    def test_l99_l10_the_whole_test_is_fast(self):
        """Named to run last: everything above, from the first import, in under 60 s."""
        for seed in SEEDS:
            code_run(seed), code_run(seed, again=1), scripted(seed), scripted(seed, again=1)
        took = time.monotonic() - STARTED
        self.assertLess(took, 60, f"the LLM-off test took {took:.1f} s")
        self.assertEqual(DAYS, 10)
        self.assertTrue(test_brain.STORY_SHA)


if __name__ == "__main__":
    unittest.main()
