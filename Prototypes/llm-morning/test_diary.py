"""Step 4's gate (Docs/fable-audit-2026-11.md, section 9, step 4; 7.5): the diary.

    python -m unittest -v test_diary

For seeds 1 to 3: no day takes more than 60 lines; an empty day takes at most 8; no spoken move fell back to the
filler line; the diary had a sentence of its own for every act; and every sentence it quotes was said in the week.
"""
import re
import unittest

from test_brain import SEEDS, NoModel, Recording

import diary
import week


def written(seed, _kept={}):
    """(the diary's text, the week's empty days, the lines the brain spoke, the moves that fell back to the filler,
    the acts the diary had no sentence for)."""
    if seed not in _kept:
        b = Recording(seed)
        w = week.run(seed, brain=b)
        del diary.UNKNOWN[:]
        text = diary.render(w)
        _kept[seed] = (text, week.empty_days(w.transcript()), set(b.spoken), list(b.fell_back), list(diary.UNKNOWN))
        del w, b
    return _kept[seed]


class Diary(NoModel):
    def test_d1_no_day_takes_more_than_60_lines_and_an_empty_day_at_most_8(self):
        for seed in SEEDS:
            text, empty, _, _, _ = written(seed)
            lengths, quiet = diary.day_lengths(text)
            self.assertEqual(sorted(lengths), list(range(1, week.DAYS + 1)))
            self.assertEqual(quiet, {k for k in empty if not empty[k]}, f"seed {seed}")
            for k, n in lengths.items():
                self.assertLessEqual(n, diary.MAX_LINES, f"seed {seed} day {k}")
                self.assertGreaterEqual(n, 3, f"seed {seed} day {k}")
                if k in quiet:
                    self.assertLessEqual(n, diary.MAX_EMPTY, f"seed {seed} day {k}: a quiet day of {n} lines")

    def test_d2_no_move_without_a_line(self):
        for seed in SEEDS:
            _, _, _, fell_back, unknown = written(seed)
            self.assertFalse(fell_back, f"seed {seed}: spoken with the filler line: {sorted(set(fell_back))[:5]}")
            self.assertFalse(unknown, f"seed {seed}: the diary had no sentence for {sorted(set(unknown))[:5]}")

    def test_d3_every_quoted_sentence_was_said(self):
        for seed in SEEDS:
            text, _, spoken, _, _ = written(seed)
            quotes = re.findall("“(.*?)”", text)
            self.assertGreater(len(quotes), 40, f"seed {seed}")
            for q in quotes:
                self.assertIn(q, spoken, f"seed {seed}")

    def test_d4_a_mood_with_a_cause_is_told_with_it_and_reasons_are_given(self):
        for seed in SEEDS:
            text = written(seed)[0]
            self.assertRegex(text, r"woke (on edge|low|warm|restless): ")
            # A reason is something in the situation, as the person might give it: never what they are like (step
            # 4b: the trait labels were taken out, so there are fewer reasons than before, and each one is one).
            reasons = re.findall(r"\*\((.+?)\)\*", text)
            self.assertGreaterEqual(len(reasons), 8, f"seed {seed}")
            for r in reasons:
                for part in r.split("; "):
                    self.assertNotIn(part, diary.NOT_A_REASON, f"seed {seed}: {r}")

    def test_d5_the_same_seed_gives_the_same_diary(self):
        first = written(1)[0]
        again = diary.render(week.run(1))
        self.assertEqual(first, again)


if __name__ == "__main__":
    unittest.main()
