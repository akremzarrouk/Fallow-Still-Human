# Playing Leo, fix 2: a moment demands a response

Mode: implement. The fix answers what the play sessions showed (`runs/play/`, the session of 2026-10-14T22:50:37Z, and the
reports `reports/model_probe_play.md`, `reports/model_probe_play2.md`):
- Elena, falsely accused by Leo, thanked Daniel for confessing and never turned to Leo.
- Mara kept searching while Leo accused his mother.
- `reassure_all` is offered in every moment, and wins.
- Stronger free models are capped at 20 requests a day (`reports/model_probe_play2.md`), so flash-lite stays.

No live call was made. Every run here used the fake model or a scripted client, with `GEMINI_API_KEY` cleared. Paths are
relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/play_fix2/`.

## Result

- **The four new tests (`test_morning.PlayFix2Test`) were seen failing, and pass after the change** (§3).
- **The full suite passes:** 349 tests, OK (skipped=141), 0 failures, 0 errors (§5). Before the change: 345 tests, OK
  (skipped=145). Four of the 145 retired replay tests were ported first, as `CLAUDE.md` asks (§2). Four more tests had
  to be adapted to the new rules (§4).
- **The fake 4-day run** (`morning.py --seed 1 --fake --days 4`) **exits 0** (§6). New baseline for later steps:
  - story `3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9`;
  - transcript `dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8`.
  They differ from fix 1's (`b1bbe7f2…`, `6656351a…`), as expected: Elena's card is in her prompts, so the fake model's
  hash-picked answers change.
- **Deviations from the request, to be read before the rest** (each is argued in §1 and listed in §8):
  1. `confess` stays in the owed list for the one who took the can.
  2. The wronged are told only if they heard the confession.
  3. The minute in the wronged line is the accuser's last accusation of that person.
  4. The player gets the new sure line but not the new option order.
  5. Heads turn for the player too (only their activity; their options are unchanged).

## 1. What changed

All in `world.py` unless said. Constants at `world.py:84-86`; new `Person` fields `owed` and `wronged`
(`world.py:381-382`).

**1. The owed answer** (`answer_owed`, `world.py:697`; set in `apply`, `world.py:1940-1941`; cleared at `world.py:1874`).
- When X says something aimed at Y with an accusation, a confrontation, a reassurance or `say_to_<Y>`, Y's `owed` is
  `{who: X, turn, room}`.
- In `options_for`, the next decision of Y in that room, in the same turn or the next 2 turns (`OWED_TURNS`), offers only:
  `silent`, `deny` (where it is offered today), `confess` (the one who took it, see §8), every option aimed at X
  (`talk.aimed_at`: accuse, reassure, say_to, confront, aside, back, object), and the `go_*` moves.
- It is one decision: any act of Y clears it (`world.py:1874`). Y leaving the room, or the window running out, ends it.
- Only during a turn (`self.present` is set), so a check made between turns (quiet.py) is never filtered.
- Not for the player (`options_for` skips both new steps for `is_player`).
- What Elena was offered after Leo's accusation, in the scripted run of test 3 (test 1's run offered 26 before the change):
  ```
  silent, deny, accuse_leo, reassure_leo, say_to_leo, go_brothers_room, go_back_room, go_bathroom
  ```
  (no `aside_leo`: every other room was taken.)

**2. Heads turn** (`world.py:1931-1935`). For every hearer of an accusation or a confession (`HEADS_TURN`):
- their trigger counts whether or not the line is new (`trigger=(heard, new or kind in HEADS_TURN)`), so their next
  decision is a model ask with that line as its trigger;
- if they were searching or sitting, they stand: `{"kind": "idle", "label": "standing"}`. Their search is abandoned
  (the room is not marked searched), and `keep_searching` is no longer offered.

**3. The wronged remember** (`world.py:1950-1957` for the line, `wronged_first`, `world.py:710`, for the order). When
the one who took the can confesses, each hearer who was accused that day, and is not the one who took it, gets the sure
line, stamped with the confession's minute like the heard-confession line before it:
```
min 06: Leo accused you of taking it at minute 03. It was Daniel.
```
and the accuser goes into `p.wronged`. Their options aimed at the accuser then come first, in their current order, for
the rest of the day (a Morning lasts a day; day 2 starts with `wronged` empty). Elena after the confession, same run:
```
reassure_leo, say_to_leo, silent, accuse_daniel, reassure_daniel, reassure_mara, reassure_all, say_other, …
```
(`accuse_leo` is gone: once the culprit is known, accusations are offered only against him, `world.py:616-617`.)

**4. Elena's card** (`data.py:28-34`). The sentence is added to her `note`: "Gentle by habit, but she will not be accused
or talked down to by her own children; when wronged, she says so plainly." Her prompt shows it after "Who you are: …".
The night mind (`mind.py:415`) reads the same note, so it shows there too.

### Argued against first (`CLAUDE.md`, "Judging changes")
- **1, the owed answer.** Would a real person do this? Someone just accused answers the accuser: denies, hits back,
  says something to them, goes quiet or leaves. They do not usually turn to the room and say "let's all stay calm". For
  the reason it holds: the accusation is addressed to them. Against it: `reassure_leo` stays on the list, and a model
  that soothes will soothe him ("It's okay, Leo"). The fix removes the generic exit, not the soothing. Whether Elena turns on
  Leo is still up to the model.
- **2, heads turn.** A shocking line stops what people are doing: yes, searching and sitting end, and everyone looks.
  Cost: more asks. People who would have been routine (silent) are now asked in the turn after, so a session spends more
  of its 250.
- **3, the wronged remember.** After "I took it", a person who was accused of it remembers who accused them and is
  likelier to answer them. Against it: the options aimed at the accuser come first, and the first of them is
  `reassure_<accuser>`, a soothing option (§8).
- **4, the card.** "when wronged, she says so plainly" describes an act, and `CLAUDE.md`'s North Star says a line that
  describes an act makes the small model do that act. It is the user's wording and was added as asked.

## 2. The retired tests ported first

`CLAUDE.md`: "before changing code in an area they cover, port the ones for that area to the fake client and make them
pass, then make the change." The area is accusations, confessions and what they leave in the records. Of the 145 retired
tests (`PLAY_FIX1_RETIRED`), the four that read accusation and confession records (found by searching their
source for accuse, confess, search and sit; the rest are about the quiet day, water, the door, trips and prompt
budgets) are the ones I took as this area. They replayed the v11 caches
of seeds 1 to 3. They now play three scripted first mornings (`SCRIPTED_STORIES`, `test_morning.py:2296`) on a Morning
that asks everyone every turn (`AskAllMorning`, `test_morning.py:2284`), with `ScriptedClient`, and Leo angry with
Daniel in seed 2's story (`StoryClient`, `test_morning.py:8846`):
- seed 2: Daniel denies at 00, accuses Leo at 03, 06 and 09, confesses at 33; Mara accuses Daniel at 36 and eats at 54;
- seed 1: Daniel confesses at 03; Leo and Mara eat at 21;
- seed 3: nobody confesses; Mara's search ends at 75, Daniel's at 78.

| Test | Ported by | Assertions changed |
|---|---|---|
| `NightTest.test_t10_what_day2_carries_and_resets` | `scripted_day1(2, client)` for `v11_day1(2, client)` | none |
| `DaysTest.test_n_t8_day_words` | `three_days(..., scripted=True)` | none |
| `DaysTest.test_n_t3_the_night_minds_prompt_exactly` | `three_days(seed=2, scripted=True)` | R1: "to min 12" is "to min 09" (accusations at 03, 06, 09) |
| `NightTest.test_t9_the_carry_in_exactly` | `scripted_day1(seed, NightScripted())` for seeds 1 to 3 | the trip's "About going to the neighbour's house" lines are not in the blocks (the stories have no trip); "(min 03, 09, 12)" is "(min 03, 06, 09)" |

They pass on the code before the change (suite: 345 tests, OK, skipped=141, `runs/play_fix2/suite_baseline_ported.txt`) and
after it (`runs/play_fix2/pass_ported.txt`). The other 141 stay retired.

## 3. The four new tests, failing before and passing after

Day 1, seed 1. A scripted player plays Leo; the others are a `ScriptedClient`. A screen the player's answer refused fails
the test (`once`), as in fix 1.

1. `test_fix1_someone_accused_owes_the_accuser_an_answer_but_the_player_does_not`
   - Leo accuses Elena at 03; the first prompt of Elena's that holds Leo's words offers `silent`, `deny`, `go_*` and
     options aimed at Leo, and none of `reassure_all`, `say_other`, `search`, `ask_who`, `eat`, `share`, `accuse_daniel`,
     `sit_leo`;
   - Daniel accused Leo at 00, and every one of Leo's screens still offers `say_other` and `reassure_all`;
   - on a fresh Morning: the filter holds at turn 3 and is gone at turn 4 (a decision at turn 1 + 2 turns);
     once Elena has answered, `reassure_all` is back.
2. `test_fix2_an_accusation_or_a_confession_stops_what_the_others_were_doing`
   - Mara sits with Daniel at 00, 03, … (scripted); a `WatchingMorning` notes each person's activity before and after
     every act;
   - after Leo's accusation of Elena at 03, Mara's activity is `idle` (it was `sitting`); after Daniel's confession (the
     first chance from 09), the same;
   - Mara's next decision is a model ask, and Leo's words are in its triggers.
3. `test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser`
   - Leo accuses Elena at 03; Daniel accuses Leo at the first chance from 03 and confesses 3 minutes later;
   - Elena's sure lines hold "Leo accused you of taking it at minute 03. It was Daniel."; Leo's, "Daniel accused you of
     taking it at minute 06. It was Daniel."; Mara and Daniel have none;
   - every prompt of Elena's with the line starts with her options aimed at Leo, in their order, then `silent`; so does
     `options_for(elena)` at the end of the day; Mara's starts with `silent`;
   - Leo is played: all of his screens still start with `silent`.
4. `test_fix4_elenas_card_says_she_will_not_be_accused_or_talked_down_to`: Elena's "Who you are:" line ends with the
   sentence and keeps the rest of her note; nobody else's prompt holds "Gentle by habit".

```
$ timeout 300 .venv/Scripts/python.exe -m unittest test_morning.PlayFix2Test.<test> > runs/play_fix2/fail_fix<n>.txt 2>&1    # exit 1 each
```

**fix1** (`runs/play_fix2/fail_fix1.txt`): the whole list is offered.
```
FAIL: test_fix1_someone_accused_owes_the_accuser_an_answer_but_the_player_does_not
    self.assertTrue(i in ("silent", "deny") or i.startswith("go_") or i in aimed, f"{i} is not an answer: {ids}")
AssertionError: False is not true : ask_who is not an answer: ['silent', 'ask_who', 'deny', 'accuse_daniel', 'accuse_leo', 'accuse_mara', 'reassure_daniel', 'reassure_leo', 'reassure_mara', 'reassure_all', 'say_other', 'say_to_daniel', 'say_to_leo', 'say_to_mara', 'sit_daniel', 'sit_leo', 'sit_mara', 'aside_daniel', 'aside_leo', 'aside_mara', 'search', 'go_brothers_room', 'go_back_room', 'go_bathroom', 'eat', 'share']
Ran 1 test in 0.087s
FAILED (failures=1)
```

**fix2** (`runs/play_fix2/fail_fix2.txt`): Mara goes on sitting after the accusation.
```
FAIL: test_fix2_an_accusation_or_a_confession_stops_what_the_others_were_doing
    self.assertEqual(accusation["after"]["mara"]["kind"], "idle", "the accusation ends her sitting")
AssertionError: 'sitting' != 'idle'
Ran 1 test in 0.071s
FAILED (failures=1)
```
The test stopped there, so the confession half was not reached. After the accusation half was in place, the confession
half was seen failing by leaving `confess` out of `HEADS_TURN` for one run (`runs/play_fix2/fail_fix2_confession_half.txt`):
```
    self.assertEqual(confession["after"]["mara"]["kind"], "idle", "the confession ends her sitting")
AssertionError: 'sitting' != 'idle'
```
The test also changed once between these two (Daniel confesses at the first chance from minute 09, not at exactly 09, since
he is not asked at exactly 09).

**fix3** (`runs/play_fix2/fail_fix3.txt`). The first run failed on its own premise (Daniel was not asked at the minute
the test had set); the test was rewritten so that he acts at the first chance, and then failed for the right reason:
```
FAIL: test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser
    self.assertIn("Leo accused you of taking it at minute 03. It was Daniel.", [data.unstamp(x)[1] for x in P["elena"].sure])
AssertionError: 'Leo accused you of taking it at minute 03. It was Daniel.' not found in ['Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you did it)', 'Daniel admitted taking the can: "It was me, I ate it in the night." (you heard it)']
Ran 1 test in 0.078s
FAILED (failures=1)
```

**fix4** (`runs/play_fix2/fail_fix4.txt`):
```
FAIL: test_fix4_elenas_card_says_she_will_not_be_accused_or_talked_down_to
    self.assertTrue(who.endswith(card), who)
AssertionError: False is not true : Who you are: Mother. Reads everyone, says little, holds it in. Will lie to keep the family whole. Fears the household breaking apart more than she fears the outside.
Ran 1 test in 0.009s
FAILED (failures=1)
```

After the change:
```
$ timeout 300 .venv/Scripts/python.exe -m unittest -v test_morning.PlayFix2Test.<test> > runs/play_fix2/pass_fix<n>.txt 2>&1   # exit 0 each
test_fix1_someone_accused_owes_the_accuser_an_answer_but_the_player_does_not (…) ... ok               Ran 1 test  OK
test_fix2_an_accusation_or_a_confession_stops_what_the_others_were_doing (…) ... ok                   Ran 1 test  OK
test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser (…) ... ok        Ran 1 test  OK
test_fix4_elenas_card_says_she_will_not_be_accused_or_talked_down_to (…) ... ok                       Ran 1 test  OK
```

## 4. Tests adapted to the new rules

The first full run after the change (`runs/play_fix2/suite_first.txt`) had 4 failures in 349 tests. Each is a real
consequence of a fix, or of the fake story moving; none hides a failure of the new behaviour.

| Test | Why it failed | Change |
|---|---|---|
| `SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn` | the second to act is the one just accused; he owes the first an answer, so `ask_who` and `say_other` are no longer offered, and "LINE-TWO" was never said | the second says `say_to_<first>`; the line is "to <name>", not "to everyone" |
| `SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again` | the others accused Daniel every turn, so he owed them an answer and `reassure_all` was not offered | the others ask who took it, then accuse anyone but Daniel (the guard under test is unchanged) |
| `FakeMorningTest.test_prompts_are_short` | the fake story moved (Elena's card changes every hash), and a night mind's prompt of 1,564 tokens is over a day's 1,450 | night-mind prompts are checked against their own bound, `mind.RECORDS_MAX` (days_design R8), as the night's and day 2's already have their own |
| `PlayS3Test.test_play_py_on_scripted_stdin_reaches_night_1_bedtime` | in the moved fake story Daniel confesses at 00, so "2" is `accuse_daniel`, not `ask_who` | the first input is the words alone, which `play.py` says to everyone whatever is offered |

## 5. The suite

```
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_fix2/suite.txt 2>&1
Ran 349 tests in 209.528s

OK (skipped=141)
```
349 is 345 plus the four new tests. The 141 skipped are the 145 retired by fix 1 less the four ported (§2).

## 6. The fake 4-day run

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_fix2_check > runs/play_fix2/check.stdout.txt 2>&1   # exit 0
$ sha256sum runs/play_fix2_check/fake/daniel_ate_it-seed1.md runs/play_fix2_check/fake/daniel_ate_it-seed1.transcript.json
3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9 *runs/play_fix2_check/fake/daniel_ate_it-seed1.md
dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8 *runs/play_fix2_check/fake/daniel_ate_it-seed1.transcript.json
```
Run again at the end (`--out play_fix2_check2`, after a line of `world.py` was only re-wrapped): the same two hashes, exit 0
(`runs/play_fix2/check3.stdout.txt`), and `PlayFix2Test`, `SequentialTalkTest`, `NightTest` and `DaysTest` pass (64 tests,
`runs/play_fix2/pass_after_format.txt`).

## 7. What went wrong on the way

- **A mistake of mine, caught at once.** An alias line added for `DaysTest` was first put in the wrong classes by a
  `replace` that hit the first of three identical lines. It was found by reading the diff and removed from the two
  classes that did not need it.
- **A broken line.** Writing `answer_owed` through a script joined its backslash continuation into one 150-character
  line. It worked; it was re-wrapped (§6).
- **Tests that did not reach their premise.** Test 2's confession and test 3's second accusation depended on when Daniel
  is asked; both were changed to "the first chance from minute N" (§3).

## 8. Open points for the user

- **`confess` stays in the owed list.** The request's list is `deny`, the acts aimed at X, `silent` and `go_*`. Read
  literally, the one who took the can, accused to his face, could not confess; the goal is that a moment gets a response,
  and a confession is one. To remove it, take `"confess"` out of the tuple in `answer_owed` (`world.py:706`).
- **Only hearers of the confession are told.** The request says "each person falsely accused that day". A person in another
  room did not hear it, and the sure line states "It was Daniel", so they do not get it. A person who was accused but did
  not hear the accusation has no `accused_by` and gets nothing either.
- **The minute is the accuser's last accusation** of that person that day (`accused_by` keeps the last). Daniel accusing
  Leo at 03, 06 and 09 gives "at minute 09".
- **The player (Leo) gets the sure line, not the order.** "Do not change the player's options" is read as options only;
  the line is a true fact, like the heard confession's. Heads turn also ends the player's own searching or sitting
  (activity, not an option).
- **The first option of the wronged is a reassurance.** Elena after the confession starts with `reassure_leo`, then
  `say_to_leo`: the order is the current one, as asked. If the model favours the first option, it may soothe Leo again
  where the request wants her to say so plainly; `say_to_<accuser>` first would answer that, and is not done here.
- **Heads turn costs asks.** Everyone else in the room is asked in the turn after an accusation or a confession, whether or
  not they would have been. No count is measured here (no live run).

## 9. Amendment: for a wronged person, `say_to_<accuser>` first

Answers the open point in §8 ("The first option of the wronged is a reassurance"). The request: this model leans
strongly to the first option (`reports/food_wording_probe.md`, variant C: 1 in 6 to 6 in 6), so what a wronged person
would say to the accuser goes first. No live call; outputs in `runs/play_fix2b/`.

**What changed** (`wronged_first`, `world.py:710`). The options aimed at someone who accused the person falsely still come
first. Within them, `say_to_<accuser>` is first, then the others aimed at the accuser in their current order (accuse,
reassure, back, object, aside, as `options_for` and `trip_options` build them). Everything else keeps its order. With two
accusers, every `say_to` comes first (in the current order), then the other aimed options. Elena after the confession in
test 3's run now starts:
```
say_to_leo, reassure_leo, silent, accuse_daniel, reassure_daniel, reassure_mara, reassure_all, say_other, …
```
Still not for the player, and still for the rest of the day.

**Test 3, updated first.** Its expected order was "the options aimed at Leo, in their order, then `silent`"; it is now
`say_to_leo`, then the rest aimed at Leo in build order, then `silent`; and `options_for(elena)[0]` is `say_to_leo`
(`runs/play_fix2b/fail_fix3.txt`):
```
$ timeout 300 .venv/Scripts/python.exe -m unittest test_morning.PlayFix2Test.test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser > runs/play_fix2b/fail_fix3.txt 2>&1   # exit 1
FAIL: test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser
    self.assertEqual(ids[:len(leo)], ["say_to_leo"] + built, "her options aimed at Leo come first, say_to first")
AssertionError: Lists differ: ['reassure_leo', 'say_to_leo'] != ['say_to_leo', 'reassure_leo']
Ran 1 test in 0.125s
FAILED (failures=1)
```
After the change the same test failed once more, on the test's own list: a later prompt of Elena's also holds `back_leo` (a
trip option aimed at Leo, built after `reassure` and before `object` and `aside`), which the list I had written left out
(`['say_to_leo', 'reassure_leo', 'back_leo', 'aside_leo']` against `['say_to_leo', 'reassure_leo', 'aside_leo']`). The list
now names all five in build order. The first failure above is the one that shows the change was missing.

Passing (`runs/play_fix2b/pass_fix3.txt`, `runs/play_fix2b/pass_PlayFix2Test.txt`):
```
$ timeout 300 .venv/Scripts/python.exe -m unittest -v test_morning.PlayFix2Test.test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser   # exit 0
test_fix3_after_a_confession_the_falsely_accused_remember_and_turn_to_their_accuser (…) ... ok
$ .venv/Scripts/python.exe -m unittest -v test_morning.PlayFix2Test   # exit 0
Ran 4 tests in 0.231s

OK
```

**The suite** (`runs/play_fix2b/suite.txt`):
```
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_fix2b/suite.txt 2>&1
Ran 349 tests in 227.044s

OK (skipped=141)
```
(A first full run, started before the test's list was corrected, had that one failure and nothing else: 349 tests,
`FAILED (failures=1, skipped=141)`, kept as `runs/play_fix2b/suite_with_old_test.txt`.)

**The fake 4-day run** (exit 0, `runs/play_fix2b/check.stdout.txt`):
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_fix2b_check > runs/play_fix2b/check.stdout.txt 2>&1
$ sha256sum runs/play_fix2b_check/fake/daniel_ate_it-seed1.md runs/play_fix2b_check/fake/daniel_ate_it-seed1.transcript.json
3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9 *runs/play_fix2b_check/fake/daniel_ate_it-seed1.md
dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8 *runs/play_fix2b_check/fake/daniel_ate_it-seed1.transcript.json
```
The same pair as §6. I did not check why (the likely reason is that no prompt of the fake run has a wronged person in it),
so the order is covered by test 3 alone.
