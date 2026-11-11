# Journal

## 2026-11-11
- Fable audit received (Docs/fable-audit-2026-11.md); its proposed direction is not yet accepted.
- Decisions pending: whether the LLM-off direction is adopted, and what the rebuild keeps.
- Branch quiet-day-stage-a (50 commits) pushed to origin so the work is no longer only on this laptop.

## 2026-11-11, evening: the 12 Nov step (the scoring brain), done a day early
Plan: `Docs/fable-audit-2026-11.md`, sections 9 and 10 (re-frozen 2026-11-11). No model was called. Not committed.

**Built**
- `brain.py`: the scoring brain, the once-a-day rule, the daily mood tilt. Weights in `content/weights.json`,
  starter lines in `content/lines.json`.
- The brain is asked where the model was: `world.py` (`ask_model`), `night.py` (`ask`). The night mind is skipped.
- `python morning.py --seed N --code --days 10` (writes `runs/code/`), `python play.py --seed N --code`.
- `test_brain.py` (B1 to B17), `test_llm_off.py` (L1 to L4, L10; L5 to L13 skipped with their dates).

**Tests**
- `test_brain` + `test_llm_off`: 31 tests in 17 s, 22 pass, 8 skipped, **1 fails: B15**.
- Old suite after the engine edits: 349 tests, OK (skipped=141). Fake 4-day hashes unchanged (B14).
- A ten-day week in code mode: 2.1 s, 0 model calls.

**B15 fails, and is left as frozen.** In seed 2 Mara is "on edge" on all ten days; the case asks for two moods. Cause:
she is very hungry every morning, so the same cause wins every day. Every other person passes by one day only.
Daniel and Elena vary; Leo is "low" from day 2 on. The fix belongs with 13 Nov (meals, the night step).

**Predictions** (seeds 1, 2, 3)
- F1 all of B1 to B17 pass on the first full run: **FAIL** (B15).
- F2 at least 50 acts that are not silent or sleep, 20 spoken lines: **PASS** (82/40, 73/39, 61/24).
- F3 Daniel denies, no confession on day 1: **PASS** (denies at minute 3, 0, 0; no confession in ten days).
- F4 both portions gone by the end of day 2: **PASS** (3 of 3, shared on day 1).
- F5 days 3 to 10 thin, under 10 lines on at least 5 of 8 days: **PASS** (8, 8, 8 of 8). As predicted, the gap to fill.
- F6 at most 6 equal line pairs: **PASS** (0, 0, 0).
- F7 a scripted day 1 under 5 s, 0 requests: **PASS** (0.05 s, 0).
- F8 your verdict after 15 minutes of play: open.
- F9 the tilt changes at least 3 decisions and none of B1 to B14: **PASS** (30, 42, 3 decisions; B7, B9, B12 hold).

**Changed from section 10.2 after reading one run** (seed 2, days 1 to 3)
- `share` was empathetic × H. Elena shared out the last food at minute 9 on a coin flip, with people only "hungry".
  Now 1.2 × empathetic × how far past "hungry" the hungriest is. She shares at minute 30, when someone is very hungry.
- `deny` needed only that the question had ever been heard, so everyone said "it wasn't me" every morning (37 to 40
  denials a run). Now a denial needs a question, or an accusation of them, heard since they last denied: 3 a run.

**Decided on the way**
- When the day's ask budget is spent, the act is marked "routine" in code mode, not "fallback". Budgets unchanged.
- No retired test was ported (the plan says `test_morning.py` is not edited; the model path is unchanged, by B14).
- The scripted-player half of the LLM-off test plays days 1 and 2 only: the existing loop plays a player no further.

**Seen, not fixed** (for 13 and 14 Nov)
- The trip is argued once a day, every day: Daniel offers, the others object (13 to 15 objections a run in seed 1).
- Nobody stops Daniel at night: those awake hear the door and stay in bed.
- Days 5 to 10 can have no spoken line at all (seed 3).

**Yours:** `python play.py --seed 2 --code` for 15 minutes; three things that felt wrong.

## 2026-11-11, late: B15 fixed, on your word ("Fix it now")

**What was wrong.** From day 2 on everyone wakes very hungry, every day. Hunger gave the same mood point every
morning, and a mood with a cause beats the seeded part, so the mood was fixed by temperament alone: Mara on edge
ten days running, Leo low from day 2. Seen in the record: seed 2, Mara, days 6 to 10, points `{'on edge': 1}` from
hunger alone, beating a seeded `warm` or `low` on days 6, 7 and 8.

**Against the fix first.** Someone who has not eaten for a week is not over it on day 6. True, and the hunger still
weighs in every decision through the hunger terms. But a mood is the colour of one day, and what colours a day is
what is different about it. "Mara woke on edge from hunger" ten mornings running is what a machine writes; a
person says it the morning it starts and the morning it gets worse.

**The change** (`brain.py`, `mood_of`; one rule, nothing else touched). Hunger gives its mood point only on a
morning the person wakes very hungry or worse *and* hungrier than they woke the morning before. This departs from
7.2 and 10.2, which say "very hungry or worse on waking". The case B15 and its expected result are unchanged.

**Result**
- `python -m unittest test_brain test_llm_off`: 31 tests, OK, 8 skipped by date. B15 passes.
- F1 stays **FAIL** as scored: the first full run failed B15. F2 to F7 and F9 still pass (F2 77/38, 76/39, 61/24;
  F9 38, 47, 3 decisions).
- Seed 2, Mara: on edge (seeded), on edge (a bad night and hunger), on edge, on edge, on edge (a bad night each),
  warm, low, on edge (a bad night), steady, on edge (a bad night). Leo: warm, low (hunger), warm, steady, low, low,
  steady, restless, steady, restless.

**Seen, not fixed**
- Elena lies awake nearly every night, so she is on edge from a bad night on 6 days of 10 in every seed. The night step of
  13 Nov decides sleep; left for it.
- With hunger no longer naming the day, moods from day 5 on are mostly the seeded part: "Leo woke warm" on a
  day nobody has eaten, with no cause. Yesterday's events will give causes once days have events (14 Nov).
- The entry above says 13 to 15 objections a run in seed 1. Counted now, seed 1: 3 objections (`object_*`) and
  12 `keep_daniel_home`. I did not check which of the two the earlier figure counted.
- Old suite after the change: `python -m unittest test_morning`, 349 tests, OK, skipped=141, 181 s.

## Step 2: the heart, food and the night step

**Budgets.** Counted first: in ten-day runs of seeds 1 to 3, the budgets refused **0** acts, 0 quiet triggers and
ended 0 talks; no day used more than 21 of its 40 asks. They are lifted in code mode all the same. What did cap
people was the rule that someone is asked only when a trigger fires (day 1, seed 2: 93 of 120 decisions never
reached the brain). In code mode everyone in a talk now decides every turn.

**Built.** `heart.py` (remembered acts and trust, suspicion from clues, one intention); the night step in place of
the night mind; the mood's full causes, and no warm morning after two mornings of hunger without a reason; someone
awake who hears the door gets up; "once is enough" for the week, with a new cause named; 16 portions and a meal a
day; `content/voices.md`. `test_heart.py`, 25 cases.

**Tests.** `python -m unittest test_brain test_llm_off test_heart`: 56 tests, OK, 8 skipped (clauses of later
steps). Old suite: 349, OK, skipped=141. No live call.

**What a week now looks like** (seed 2). Days 1 and 2: the question, three denials, a meal; little else. Day 3 the
food runs short: Daniel offers to go, Leo and Elena say no, he goes in the night; Leo tells him not to, Elena hears
the door and waits up. Next door is empty. Day 4: half portions; he offers to go further, and goes. Day 5 he goes
again without a word; Elena is sitting by the door: "Daniel, no. Not in the dark." He does not come back. Day 6:
the three sit together; Elena gives Leo her share.

**Changed after reading runs** (each because it read wrong, not to move a number): people took from the shelf
before the meal; everyone was "starving" by evening (the engine's hunger rate was built for a 90-minute morning);
Daniel confessed on a coin flip; all four offered to go on one night; Elena offered and took it back in three
minutes; Elena and Leo reassured each other every morning for nothing; the trip came back daily through a shelf
that flipped between short and empty. The rules that fixed them are in the audit's changelog, item 28.

**Not built, or thin.** No apology, so no "drops two steps". The meal has no arguing over the split. Days 1 and 2
have 4 and 0 spoken lines; nobody raises the can again after day 1, because nothing points at anyone. Daniel is
lost in all three seeds (nights 4, 5 and 7): he goes out most nights and the street's own odds catch him. The
fuller days and the evening meal are step 3's.

## Step 3: the week, at the world's own odds

**Built.** `week.py`: seven days, each played from 07:00 to bedtime, day 1 and day 2 included (`python week.py
--seed 2`). Beats at 10:00, 15:00 and 19:00 bring everyone who is up into the kitchen: the morning and evening meal
(half a portion each, or the water round when the shelf is empty), the day's four tasks (boards, water, watch,
stores) and looking after whoever is sick or hurt, the afternoon's reports ("I counted. 10 portions on the shelf."),
the plan for the night. `health.py` and `content/chances.json`: sickness and injury from causes only, three levels,
mending or worsening each night by rest, food, water and care; catching it from a room-mate or a patient. Leo is
never lost: the draw that would lose him brings him back hurt. Unspoken guilt grows a step every second night.

**Gate.** `python -m unittest test_llm_off`: 15 tests, OK, 1 skipped (L9, step 6): L1 to L8 and L10 to L13 on the
week, seeds 1 to 3, with Leo by code and with a scripted Leo, in 34 s. `test_brain test_heart`: 42, OK. Old suite:
349, OK, skipped=141. No live call.

**Empty days** (`python week.py --count 50`): 44 of 350 days, **0.88 a week**; no week with three in a row; weeks
with 0, 1, 2 empty days: 16, 24, 10. The limit is 1 a week, so **the nudge is not built**. It is close to the
limit: day 2 is the usual empty day.

**What a week reads like now** (seed 2). Day 2: Mara strains her back carrying the water and Elena looks after
her. Day 3: Daniel takes Elena aside and says it: "It was me. I took the can in the night and ate it." She: "Daniel,
you looked at me and said it was not you." Day 4: half shares; he offers to go next door and goes, against her
word. Day 5: "I told you not to go, Daniel. You went." That evening she gives him her share. He goes further along
the street and does not come back. Day 6: water only; the three of them; a knock at the door.

**Speech.** The house said 3 to 5 lines a day; now 7 to 17, because the ordinary acts are spoken: taking a task,
setting out the meal, thanks, asking after someone hurt, a word about how one woke, having it out the morning
after. The lines are plain starter lines, and two people sometimes say the same sentence; the voices are step 5.

**Cut or not built.** In the work practice: assigning a task, refusing one, doing one together. The nudge (not
needed). Rain water never made anyone sick in these weeks: the stored water outlasts seven days.

**The crash.** The machine ran out of memory once during this step. A week takes 25 MB and the full tests about
100 MB, so the likely cause was an earlier hung test in which a scripted player was asked the same question for
ever and every screen was kept. That loop now stops itself after 200 tries, and every run since goes one at a
time under a time and memory cap.
