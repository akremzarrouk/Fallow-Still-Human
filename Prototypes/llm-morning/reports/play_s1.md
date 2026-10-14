# Playing Leo, step S1: the player in the engine (days 1 and 2 and their nights)

Mode: implement, from `reports/play_design.md` §10 S1, with the user's decisions on its open points:
- faces stay as designed (the face word on the screen only);
- no forced dozing;
- the repetition guard (`world.py:626-629`) is off for the player only.

Case C9 was added for the guard. No live call was made: every run here is a fake one, with `GEMINI_API_KEY` cleared.
Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/play_s1/`.

## Result

- **The seven tests (C1, C3, C4, C5, C7, C8 and C9) were seen failing** before the engine change (§3), **and pass
  after it** (§4).
- **The full suite passes:** 338 tests, OK (§5). At HEAD it was 331 tests OK.
- **§7 check 2 holds.** The fake 4-day run's story and transcript have the same sha256 before and after the change
  (§6). Its meta differs only in `run_seconds` and its own path, the same two fields that differ between two runs at
  HEAD.

## 1. What was built

**`player.py` (new):**
- `Player` keeps the standing order "wait" (`waiting`). It knows what reached the person since their last act
  (`mark` and `reached`: lines added to `memory` or `sure`, or a belief given). It renders a `Screen` from a view:
  - a header;
  - the card, on the first screen only: who you are, how you address them, note and values, and the backstory;
  - the body lines;
  - "Since you last chose": new `memory`, `sure` and belief lines, stamped, with the day's carry-in on the day's first
    screen;
  - "What you know", when it changed;
  - "Now";
  - the options, numbered;
  - the message, if the last answer could not be used.
- `check` applies §2.2's rules to an answer. A (speech) option without words gets "What do you say?"; `silent` with
  words gets "Staying silent means saying nothing"; at night, words on a non-speech option are refused; an unknown
  option gets "Choose one of the options". Words are tidied: whitespace collapsed, `"` turned into `'`, at most 240
  characters.
- `ScriptedPlayer(rule)` answers screens for the tests; `by_minute` builds such a rule from a table.
- `play_days(oracle, seed, player, scenario, days)` plays days 1 to `days` (1 or 2), each with its night and night mind,
  in `morning.run`'s order and with its scene counting (`oracle.new_scene`). It prints nothing.

**`world.py`:**
- `Morning(..., player=None)` and `is_player(p)`.
- `decide` hands the player's person to `decide_player`. The player is asked every played turn unless the standing
  order is "wait" and nothing has reached them since their last act; then the code's routine applies, mode `routine`
  (§4.1). Their decision has mode `player`. No food, inner or lull moment, and no `take_answer`.
- `decide_aside` and `decide_given` hand the player's person to `played` (§2.4).
- `player_choice` shows the screen and asks again, with the message, until the answer can be used; nothing happens
  meanwhile.
- `player_view` builds the person's own lines inside `truth.prompting()`:
  - body lines;
  - the "About …" lines, without the stance `About the can (…)` / `you have not settled`;
  - the Now lines;
  - `memory`, `sure` and today's beliefs;
  - the carry-in, the backstory and the options.
  It never reads the grudge lines, the conscience or the pattern block (§1.3).
- `now_lines(p, t, minute, lull, screen=False)` is the prompt's "Now" block moved out of `_prompt_for`, unchanged for a
  prompt. For the screen, a face names only the word that shows (`face_word`: "guilty and terrified" shows
  "terrified", L4), and "You are the first to act …" and the pattern block are left out.
- The repetition guard skips the player's person (C9).
- `add_grudge` never raises a grudge of the player's person (§3).
- In `apply`, the player's spoken lines are new (§5.1, change 1), and an explicit `silent` by the player writes the same
  own line a model's does.
- `turn`'s `act` marks the player after their act (for "wait").

**`night.py`:** `Night.ask` asks the player for their bedtime, reaction or answer (§4.3), with the night's Now lines.
`next_day` carries the player into the next day's Morning.

**`mind.py`:** `NightMind.run` skips the player's person; their night mind is theirs.

**With no player**, every one of these is behind `player is None` or `is_player`. Two edits change no-player code
without changing what it does:
- `_prompt_for` now calls `now_lines`, which builds the same lines in the same order;
- `Night.ask` builds `byid` before its first use rather than after `parse`.

The suite and §6 are the check.

**Not built here (S2, S3):** quiet days, the terminal, the play log, the session cap and resume. In S1 the screen shows
the player's own act as the line Leo's memory holds of it ("you accused Daniel.") without the typed words; echoing the
words is the terminal's job in S3.

**Where S1 differs from the design, written into its §10 "As built":**
- The entry point is `player.play_days`, not `morning.run(player=…)`. `morning.run` is not changed at all, so "with no
  player, nothing changes" holds by construction. C3's stdout check is made on `play_days`.
- C5 covers days 1 and 2 and their nights, not days 1 to 3, as day 3 is a quiet day (S2).
- On days 1 and 2 a "wait" is not broken by the hunger word rising. §4.1's "body stages" are the quiet day's needs
  (fasting, sleep debt, thirst), which days 1 and 2 do not count. The rise shows on the next screen ("Since you last
  decided, you have grown hungrier.").

`reports/play_design.md` was amended to match: §2.1 and §11 (the decisions), C9 in §9, and "As built" in §10.

## 2. The tests (`test_morning.PlayerS1Test`)

The others are a `ScriptedClient`. It answers each decision prompt by its first line, its "Now, minute NN," line and
its options, through a rule (default: `silent`, feeling "calm"). It answers night minds as `FakeClient` does, and keeps
every prompt. An option not offered (for example `silent` at bedtime) falls back as any unusable answer does. C5 uses
`FakeClient` itself, recording prompts.

| Test | What it holds |
|---|---|
| C1 | Leo accuses Daniel at minute 03 with Mara gone to the back room. The exact lines: Daniel's and Elena's with the words, Mara's "Voices from the kitchen." without them, Leo's "you accused Daniel.". `accused_by == {"leo": 3}`. Daniel's next decision is a model ask, ordered "just accused by Leo", with the line among its triggers. No grudge event of Daniel's against Leo. Leo's suspicion and grudges at 0. The chronicle's event: target Daniel, witnesses `leo did, daniel saw, elena saw, mara voices`. No prompt for Leo |
| C3 | One player script over `daniel_ate_it`, `mara_ate_it` and `miscount`, days 1 and 2 with their nights. The three lists of screen texts are byte-identical; none holds "you ate it yourself", "On your conscience", "eats a can", "Nobody sees" or "culprit"; nothing is printed |
| C4 | `reassure_mara`: Mara's line with the words, her next decision "just spoken to by Leo", nobody's `accused_by`, Daniel's guilt still 1. `search` with words: "Leo says to everyone, while searching: …", and Leo still searching at minute 06. `say_other` without words: "What do you say?", the same minute, no request between the two screens. `silent` with words: "Staying silent means saying nothing", the same. `He said "no"` heard as `He said 'no'` |
| C5 | Over `FakeClient`, days 1 and 2 with nights: no prompt begins "You are Leo,", none holds "Leo looks". Leo's decisions are only `player` and `routine`. Suspicion 0, no grudge, no feeling |
| C7 | Leo goes to the brothers room and waits. Screens: minute 00, minute 03, then bedtime with its four options. His 29 decisions from minute 03 are `routine` `silent`. Variant: Daniel speaks at his first ask from minute 20 on (minute 33). The next screen is at minute 36 with "min 33  Voices from the kitchen." |
| C8 | Daniel's feeling "guilty and terrified" at minute 00. Leo's minute-03 screen holds "- Daniel is here, staying put. Daniel looks terrified.", and no screen holds "guilty". Elena's minute-03 prompt holds "Daniel looks guilty and terrified." as today. No face on Leo's screens from minute 12 |
| C9 | The player's `accuse_daniel` at minutes 00, 03 and 06 is still offered at 09. For Mara, the model's, three accusations in a row withhold `accuse_daniel`, with a player in the house or not. With no player, Leo's guard is as before |

**A look at what the screens hold** (the C3 script run outside the tests; the commands and output are in §7):
- In both `daniel_ate_it` and `mara_ate_it`, Leo got 10 screens: day 1 at minutes 00 to 18, bedtime, day 2 at minute 00
  (then "wait"), and bedtime.
- The others were asked 35 times in each (Daniel 12, Elena 10, Leo 0, Mara 13), at the same minutes.
- Their prompts differ as they should: "On your conscience" is in Daniel's 12 prompts in `daniel_ate_it`, in Mara's 13
  in `mara_ate_it`, and in nobody's in `miscount`. So C3's identical screens are not identical because the scenario
  failed to switch.

## 3. Each test failing, before the engine change

`player.py` and the tests were written first, with no change to `world.py`, `night.py` or `mind.py`. The player was
therefore never asked, and Leo was still the model's. The outputs are `runs/play_s1/fail_c{1,3,4,5,7,8,9}.txt`, exit 1
each. The command for each:

```
$ .venv/Scripts/python.exe -m unittest test_morning.PlayerS1Test.<test> > runs/play_s1/fail_<c>.txt 2>&1
```

**C1** (`runs/play_s1/fail_c1.txt`):
```
F
======================================================================
FAIL: test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it (test_morning.PlayerS1Test.test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8696, in test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it
    self.assertIn((3, f'Leo accuses you of taking it: "{words}"'), P["daniel"].memory)
AssertionError: (3, 'Leo accuses you of taking it: "You were up last night, Daniel."') not found in [(0, 'you stayed where you were and said nothing. You felt calm.'), (0, 'Mara leaves for the back room.'), (33, 'you stayed where you were and said nothing. You felt calm.'), (66, 'you stayed where you were and said nothing. You felt calm.')]

----------------------------------------------------------------------
Ran 1 test in 0.064s

FAILED (failures=1)
```

**C3** (`runs/play_s1/fail_c3.txt`):
```
F
======================================================================
FAIL: test_c3_nothing_shown_to_leo_depends_on_who_took_the_can (test_morning.PlayerS1Test.test_c3_nothing_shown_to_leo_depends_on_who_took_the_can)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8730, in test_c3_nothing_shown_to_leo_depends_on_who_took_the_can
    self.assertTrue(texts["daniel_ate_it"], "the player was never asked")
AssertionError: [] is not true : the player was never asked

----------------------------------------------------------------------
Ran 1 test in 0.567s

FAILED (failures=1)
```

**C4** (`runs/play_s1/fail_c4.txt`):
```
F
======================================================================
FAIL: test_c4_the_act_decides_and_the_words_are_heard (test_morning.PlayerS1Test.test_c4_the_act_decides_and_the_words_are_heard)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8763, in test_c4_the_act_decides_and_the_words_are_heard
    self.assertIn((0, 'Leo reassures you: "Nobody thinks it was you, Mara."'), P["mara"].memory)
AssertionError: (0, 'Leo reassures you: "Nobody thinks it was you, Mara."') not found in [(0, 'you stayed where you were and said nothing. You felt calm.'), (54, 'you stayed where you were and said nothing. You felt calm.')]

----------------------------------------------------------------------
Ran 1 test in 0.069s

FAILED (failures=1)
```

**C5** (`runs/play_s1/fail_c5.txt`):
```
F
======================================================================
FAIL: test_c5_nobody_decides_for_leo_but_the_player (test_morning.PlayerS1Test.test_c5_nobody_decides_for_leo_but_the_player)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8789, in test_c5_nobody_decides_for_leo_but_the_player
    self.assertTrue([s for s in p.screens if s.kind == "bedtime"], "the premise: a night screen")
AssertionError: [] is not true : the premise: a night screen

----------------------------------------------------------------------
Ran 1 test in 1.585s

FAILED (failures=1)
```

**C7** (`runs/play_s1/fail_c7.txt`):
```
F
======================================================================
FAIL: test_c7_waiting_in_played_turns_shows_nothing_until_something_reaches_leo (test_morning.PlayerS1Test.test_c7_waiting_in_played_turns_shows_nothing_until_something_reaches_leo)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8805, in test_c7_waiting_in_played_turns_shows_nothing_until_something_reaches_leo
    self.assertEqual([(s.kind, s.minute) for s in p.screens], [("turn", 0), ("turn", 3), ("bedtime", None)])
AssertionError: Lists differ: [] != [('turn', 0), ('turn', 3), ('bedtime', None)]

Second list contains 3 additional elements.
First extra element 0:
('turn', 0)

- []
+ [('turn', 0), ('turn', 3), ('bedtime', None)]

----------------------------------------------------------------------
Ran 1 test in 0.095s

FAILED (failures=1)
```

**C8** (`runs/play_s1/fail_c8.txt`):
```
E
======================================================================
ERROR: test_c8_a_face_on_the_screen_names_only_what_a_face_shows (test_morning.PlayerS1Test.test_c8_a_face_on_the_screen_names_only_what_a_face_shows)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8830, in test_c8_a_face_on_the_screen_names_only_what_a_face_shows
    three = next(s for s in p.screens if s.minute == 3)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
StopIteration

----------------------------------------------------------------------
Ran 1 test in 0.095s

FAILED (errors=1)
```

**C9** (`runs/play_s1/fail_c9.txt`):
```
F
======================================================================
FAIL: test_c9_the_repetition_guard_is_off_for_the_player_only (test_morning.PlayerS1Test.test_c9_the_repetition_guard_is_off_for_the_player_only)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8843, in test_c9_the_repetition_guard_is_off_for_the_player_only
    self.assertEqual([d["option"] for d in self.decisions(m) if d["person"] == "leo"][:3], ["accuse_daniel"] * 3)
AssertionError: Lists differ: ['silent', 'silent', 'silent'] != ['accuse_daniel', 'accuse_daniel', 'accuse_daniel']

First differing element 0:
'silent'
'accuse_daniel'

- ['silent', 'silent', 'silent']
+ ['accuse_daniel', 'accuse_daniel', 'accuse_daniel']

----------------------------------------------------------------------
Ran 1 test in 0.071s

FAILED (failures=1)
```

## 4. Each test passing, after it

The command for each:

```
$ .venv/Scripts/python.exe -m unittest -v test_morning.PlayerS1Test.<test> > runs/play_s1/pass_<c>.txt 2>&1
```

**C1** (`runs/play_s1/pass_c1.txt`):
```
test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it (test_morning.PlayerS1Test.test_c1_leo_accuses_daniel_at_minute_03_and_who_hears_it) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.038s

OK
```

**C3** (`runs/play_s1/pass_c3.txt`):
```
test_c3_nothing_shown_to_leo_depends_on_who_took_the_can (test_morning.PlayerS1Test.test_c3_nothing_shown_to_leo_depends_on_who_took_the_can) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.544s

OK
```

**C4** (`runs/play_s1/pass_c4.txt`):
```
test_c4_the_act_decides_and_the_words_are_heard (test_morning.PlayerS1Test.test_c4_the_act_decides_and_the_words_are_heard) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.087s

OK
```

**C5** (`runs/play_s1/pass_c5.txt`):
```
test_c5_nobody_decides_for_leo_but_the_player (test_morning.PlayerS1Test.test_c5_nobody_decides_for_leo_but_the_player) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.179s

OK
```

**C7** (`runs/play_s1/pass_c7.txt`):
```
test_c7_waiting_in_played_turns_shows_nothing_until_something_reaches_leo (test_morning.PlayerS1Test.test_c7_waiting_in_played_turns_shows_nothing_until_something_reaches_leo) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.144s

OK
```

**C8** (`runs/play_s1/pass_c8.txt`):
```
test_c8_a_face_on_the_screen_names_only_what_a_face_shows (test_morning.PlayerS1Test.test_c8_a_face_on_the_screen_names_only_what_a_face_shows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.100s

OK
```

**C9** (`runs/play_s1/pass_c9.txt`):
```
test_c9_the_repetition_guard_is_off_for_the_player_only (test_morning.PlayerS1Test.test_c9_the_repetition_guard_is_off_for_the_player_only) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.078s

OK
```

## 5. The suite

```
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_s1/suite_before.stdout.txt 2>&1      # at HEAD 319937d
Ran 331 tests in 374.926s
OK
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_s1/suite_after.stdout.txt 2>&1       # with the change
Ran 338 tests in 386.931s
OK
```

Both runs print the same four `[429 RESOURCE_EXHAUSTED] waiting …` lines near their start. They come from the suite's
stubbed API (`StubApi`, `test_morning.py:178-191`), not from a request.

## 6. §7 check 2: the fake run before and after

The same command at HEAD `319937d` (twice, into two folders) and with the change:

```
$ .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_check_before   > runs/play_s1/before.stdout.txt   # exit 0
$ .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_check_before2  > runs/play_s1/before2.stdout.txt  # exit 0
$ .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_check_after    > runs/play_s1/after.stdout.txt    # exit 0
949bd5abf01b5d2bc66e65456360d88b7d4f1fc4cd6d866b51b09de3f13286ad  runs/play_check_before/fake/daniel_ate_it-seed1.md
949bd5abf01b5d2bc66e65456360d88b7d4f1fc4cd6d866b51b09de3f13286ad  runs/play_check_before2/fake/daniel_ate_it-seed1.md
949bd5abf01b5d2bc66e65456360d88b7d4f1fc4cd6d866b51b09de3f13286ad  runs/play_check_after/fake/daniel_ate_it-seed1.md
7d20b51864a1e39c0b563f57442e0948ffb7acf655e27cac061f9a934b50df68  runs/play_check_before/fake/daniel_ate_it-seed1.transcript.json
7d20b51864a1e39c0b563f57442e0948ffb7acf655e27cac061f9a934b50df68  runs/play_check_before2/fake/daniel_ate_it-seed1.transcript.json
7d20b51864a1e39c0b563f57442e0948ffb7acf655e27cac061f9a934b50df68  runs/play_check_after/fake/daniel_ate_it-seed1.transcript.json
```

The meta files, compared line by line:
```
before vs after:
  => "run_seconds": 4.0,
  => "story": "runs/play_check_after/fake/daniel_ate_it-seed1.md",
  <= "run_seconds": 4.2,
  <= "story": "runs/play_check_before/fake/daniel_ate_it-seed1.md",
before vs before2 (both at HEAD):
  => "run_seconds": 4.0,
  => "story": "runs/play_check_before2/fake/daniel_ate_it-seed1.md",
  <= "run_seconds": 4.2,
  <= "story": "runs/play_check_before/fake/daniel_ate_it-seed1.md",
```
(The hashes were taken with PowerShell's `Get-FileHash -Algorithm SHA256`, written in lower case.)

## 7. Other commands

The scenario-switch check behind §2's last paragraph, run with the change in (a here-document of `play_days` over the
three scenarios with the C3 script):
```
daniel_ate_it prompts with 'On your conscience': {'Daniel': 12, 'Mara': 0}
mara_ate_it prompts with 'On your conscience': {'Daniel': 0, 'Mara': 13}
miscount prompts with 'On your conscience': {'Daniel': 0, 'Mara': 0}
```
and the screen counts (`peek_screens.py`, in the session scratchpad):
```
== daniel_ate_it: 10 screens; kinds [('turn', 1, 0), ('turn', 1, 3), ('turn', 1, 6), ('turn', 1, 9), ('turn', 1, 12), ('turn', 1, 15), ('turn', 1, 18), ('bedtime', 1, None), ('turn', 2, 0), ('bedtime', 2, None)]
   prompts sent: 35; by person: {'Daniel': 12, 'Elena': 10, 'Leo': 0, 'Mara': 13}
== mara_ate_it: 10 screens; kinds [same]
   prompts sent: 35; by person: {'Daniel': 12, 'Elena': 10, 'Leo': 0, 'Mara': 13}
```

The diff of the code, before the commit:
```
$ git diff --stat -- world.py night.py mind.py test_morning.py
 Prototypes/llm-morning/mind.py         |   3 +-
 Prototypes/llm-morning/night.py        |  12 +-
 Prototypes/llm-morning/test_morning.py | 238 +++++++++++++++++++++++++++++++++
 Prototypes/llm-morning/world.py        | 142 ++++++++++++++++++--
 4 files changed, 378 insertions(+), 17 deletions(-)
```
`player.py` is new (186 lines).
