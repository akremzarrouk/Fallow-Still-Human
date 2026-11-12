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

## Step 4: the diary. First stop

**Built.** `diary.py`: a played week as a page a day (`python diary.py --seed 2` writes
`runs/week/week-seed2.md`). A day opens with the shelf and who woke how, with the cause. Then the morning, the
day's work, the afternoon, the evening, the night. What was said is quoted as it was said; where the brain weighed
something the line ends with why, in its own words. A meal and its eating are one line, the day's tasks one line, a
run of small talk one line. Nothing is invented: every sentence is built from the record.

**Gate.** `python -m unittest test_diary`: 5 tests, OK. Seeds 1 to 3: days take 7 to 21 lines (limit 60); a quiet
day takes 7 (limit 8); no spoken move took the filler line; the diary had a sentence for every act; every quoted
sentence was said. All clauses in force still pass: `test_llm_off` 15 OK (1 skipped), `test_brain test_heart` 42
OK, old suite 349 OK (skipped=141). No live call.

**Changed after reading the diary.** Three people gave Daniel their share one after another: now one does. He
refused his share and then took from the shelf: after owning up he eats like anyone. The shelf could go below
zero. He left for his room after every talk: now once a day. "0.25 portions" is now "a quarter of a portion".

**Yours, at this stop.**
1. Read `runs/week/week-seed2.md`, then `week-seed3.md` or `week-seed1.md`. About 20 minutes. Mark what sounds
   wrong: a line, a reason, a thing nobody would do.
2. Read `content/voices.md` and approve or mark the four sheets. The bulk of the lines (step 5) waits for that.

**What I would look at, reading it as you will.**
- The lines are plain and shared: Mara and Daniel say "I lay awake half the night" in the same minute. Step 5.
- Daniel goes out most nights once the food is short, and in seeds 1 and 2 he does not come back (nights 4 and
  5). In seed 3 he lives. It follows from the street's own odds, but two weeks in three end the same way.
- Days 1 and 2 are thin: after the denials nothing points at anyone, so the can goes quiet until what is on Daniel
  grows and he tells Elena (day 3) or everyone (day 5).
- Leo, played by code, is the calm one who says little. Whether you care about the family is the hour of play.


## Step 4b: the week lands (added after the first stop)

**Why.** The user read part of seed 2 and gave four notes: after Daniel owns up the others carry on as if nothing
happened; Daniel setting the meal out of guilt is good; the guilty one would not say "I have not forgotten
yesterday"; a night out should cost sleep. I read the three weeks against the goal (audit 4a): two of its five
tests were met. The faults were in what people do, so this step comes before the lines (audit changelog 31).

**Built.** Whoever is told in private tells the others (`reveal`), and each has it out in their own words. Small
talk waits in an hour in which a blow fell; nobody thanks, tends or feeds someone they are angry with that day. The
food is Elena's to set out; another does it to make amends or when she is worn out, and the diary says which. She
cuts the shares at less than three days of full meals, and says so. A night with no sleep is said in the morning
line, slept off, and whoever was up sleeps through the day's work (Elena only after two such nights). Daniel's
offer to go is tied to the can. Nobody forbids the same person twice; a loss is named against the next to go.
Elena, told someone will go, is at the door before they are. Nobody searches or looks where they just watched
someone look. The one who took the can does not take from the shelf again. The diary: no trait as a reason, who
heard a confession, the knock, the rest.

**Checked.** Each run alone, under a time and memory cap. `test_brain test_heart`: 42 OK. `test_llm_off`: 15 OK
(skipped=1). `test_diary`: 5 OK. Old suite: 349 OK (skipped=141). `week.py --count 50`: 42 empty days of 350, 0.84
a week, none with three in a row. Three test lines changed, each for a deliberate change of output: the grief
wording (H11, L11), a watcher who has since said he will go himself (H10), and D4, which counted reasons (more
than 15) and now asks for at least 8, none of them a trait.

**Not done, and what still reads wrong.** Days 1, 2 and the day after the confession are thin. The same answer
lines ("Thank you", "You would do the same") are everywhere: step 5. Elena, starving, offers to go out herself on
day 7 with food on the shelf. No apology move, no going out together, no arguing over the split.
