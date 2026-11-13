"""Step 6's gate (Docs/fable-audit-2026-11.md, section 9, step 6; 7.5, "Leo's screen"; section 8, L9): Leo's hour.

    python -m unittest -v test_hour

A script plays Leo through the week with no model: the week completes in about sixty choices; no screen shows more than
seven; the same seed and the same choices give the same week, so a saved week can be gone on with; a sick or hurt Leo
is offered less and told why; what the others do to Leo because of what he did is said on his screen; the end page
says where each of the three stands with him and what put them there; and a kind Leo and a cold Leo are treated
differently by at least two of the others by day 3, each for a recorded act of his (L9).
"""
import json
import os
import tempfile
import unittest

from test_brain import SEEDS, NoModel

import hour
import week


def played(seed, name, _kept={}):
    """(the week's transcript as text, the choices made, the most choices on a screen, the screens that said
    "Because of what you did", the end page) for a script's week."""
    if (seed, name) not in _kept:
        because = []
        inner = hour.SCRIPTS[name]()

        def pick(screen, rows):
            if "Because of what you did:" in screen.text:
                because.append(screen.text.split("Because of what you did:")[1].split("What you do:")[0].strip())
            return inner(screen, rows)
        w, p = hour.play(seed, pick)
        _kept[(seed, name)] = (json.dumps(w.transcript(), sort_keys=True, default=str), list(p.choices), p.most,
                               because, hour.end_page(w), len(w.days))
        del w, p
    return _kept[(seed, name)]


class Hour(NoModel):
    def test_h1_the_week_completes_in_about_sixty_choices(self):
        for seed in SEEDS:
            _, choices, _, _, _, days = played(seed, "kind")
            self.assertEqual(days, week.DAYS)
            self.assertGreaterEqual(len(choices), 40, f"seed {seed}")
            self.assertLessEqual(len(choices), 90, f"seed {seed}")

    def test_h2_no_screen_shows_more_than_seven_choices(self):
        for seed in SEEDS:
            for name in ("kind", "cold"):
                self.assertLessEqual(played(seed, name)[2], hour.MAX, f"seed {seed} {name}")

    def test_h3_the_same_choices_give_the_same_week_and_a_saved_week_goes_on(self):
        tr, choices, _, _, _, _ = played(2, "kind")

        def nobody(screen, rows):
            raise AssertionError("asked for a choice the saved week did not hold")
        w, p = hour.play(2, nobody, replay=choices)
        self.assertEqual(json.dumps(w.transcript(), sort_keys=True, default=str), tr)
        # Stopped half way and gone on with: the saved half is replayed, then the script plays on to the end.
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "seed2.json")
            half = choices[:len(choices) // 2]
            w, p = hour.play(2, hour.SCRIPTS["kind"](), replay=half, save=path)
            self.assertEqual(len(w.days), week.DAYS)
            self.assertEqual(p.choices[:len(half)], half)
            with open(path, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual((saved["seed"], saved["choices"]), (2, p.choices))
        with self.assertRaises(hour.LogDiffers):
            hour.play(2, nobody, replay=["no_such_choice"])

    def test_h4_a_sick_or_hurt_leo_is_offered_less_and_told_why(self):
        class Health:
            def __init__(self, level):
                self.n = level

            def level(self, pid):
                return self.n

            def what(self, pid):
                return "a twisted ankle"

        class M:
            def __init__(self, level):
                self.b = type("B", (), {"health": Health(level)})()

            def brain(self):
                return self.b
        rows = [{"id": x} for x in ("silent", "task_boards", "task_stores", "volunteer_far", "reassure_mara", "go_kitchen",
                                    "plate_eat")]
        p = hour.HourPlayer(None)
        kept, line = p.limits(M(0), rows)
        self.assertEqual((len(kept), line), (len(rows), None))
        kept, line = p.limits(M(1), rows)
        self.assertEqual([r["id"] for r in kept], ["silent", "task_stores", "reassure_mara", "go_kitchen", "plate_eat"])
        self.assertIn("a twisted ankle", line)
        kept, line = p.limits(M(2), rows)
        self.assertEqual([r["id"] for r in kept], ["silent", "reassure_mara", "plate_eat"])
        self.assertIn("laid up", line)

    def test_h5_what_they_do_because_of_what_he_did_is_on_his_screen(self):
        for seed in SEEDS:
            because = played(seed, "kind")[3] + played(seed, "cold")[3]
            self.assertTrue(because, f"seed {seed}")
            for text in because:
                self.assertIn("because you ", text)

    def test_h6_the_end_page_says_where_each_stands_and_what_put_them_there(self):
        for seed in SEEDS:
            kind, cold = played(seed, "kind")[4], played(seed, "cold")[4]
            for page in (kind, cold):
                for name in ("Daniel", "Elena", "Mara"):
                    self.assertIn(name, page)
                self.assertRegex(page, r"day \d: you ")
            self.assertRegex(kind, r"(close|warm) to you")
            self.assertRegex(cold, r"(wary of|cold to) you")

    def test_l09_leo_matters(self):
        for seed in SEEDS:
            found = hour.leo_matters(seed)
            self.assertGreaterEqual(len(found), 2, f"seed {seed}: {found}")
            for q, acts in found.items():
                for option, which, named in acts:
                    self.assertTrue(named.startswith("Leo "), f"seed {seed}: {q} {option}: {named}")


if __name__ == "__main__":
    unittest.main()
