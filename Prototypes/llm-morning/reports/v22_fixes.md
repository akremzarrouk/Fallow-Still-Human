# v22 fixes: own words in the night mind, the stale intent, Q6's empty stretch

Mode: implement. The findings are `reports/v22_gaps.md` (§1b, §1a, §3 and §5). The parent commit is `966d5b5` (v22's plan, run and
report). No API call was made, no cache was written, and no frozen version was touched. Paths are relative to
`Prototypes/llm-morning/`. Raw outputs are in `runs/v22_fixes/`.

## Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| 1 | The three tests fail before and pass after | **yes** | `runs/v22_fixes/red.stdout.txt` (3 failures, each on the new rule's own assertion) and `runs/v22_fixes/green.stdout.txt` (3 OK) |
| 2 | The full suite passes | **yes** | **288 tests OK** in 5 min 35 s (`runs/v22_fixes/unittest.stdout.txt`). A first run had 1 failure, traced to rule 1 and accounted for in the test (§3) |
| 3 | v9 to v14 frozen replays identical | **yes** | 18 replays (seeds 1–3 of 6 versions): story and transcript IDENTICAL, 6 exits 0 (`runs/v22_fixes/frozen.stdout.txt`) |
| 4 | A no-API replay of v22 seed 2 names its first cache miss and the rule | **yes** | Ask 100, day 3, Daniel, min 03: **rule 2** (the intent line is gone). Rule 1's first miss is day 7, Leo, min 00; rule 3's is day 7, Mara, 19:00 (§4) |
| 5 | One commit with the fixes, the tests, `reports/v22_gaps.md`, `runs/v22gaps/` and this report, no key | **yes** | The commit that adds this file (hash and `git status` in §6 and in the reply) |

**Two choices the brief left open** (both traced in §1 and §2):
- **Rule 2 applies from day 3 on** (`self.quiet is not None`). Applied to days 1 and 2 as well, it changes day 2's prompts and v16's cache no longer answers them: the premise of
  every test that starts from v16 seed 2 (`runs/v22_fixes/which_rule.py`: first miss at day 2 with it, at day 3 without). It is the rule W1 followed: "nothing before day 3 changes".
- **A skipped Q6 does not use up the day's Q6** (`q6_done` stays false), so a later spell the same day, with the bin not out, still fires it.

## 1. Rule 1: own words in the night mind (`mind.py`)

**The change.**
- `mind.py:164-190`: `own_sentences(chron, pid)` (every sentence in the `words` of `pid`'s events, whole and sentence by sentence, as `norm()` writes them) and `quotes_own_words(text, chron, pid)`:
  - true if words in quotation marks are part of a sentence they spoke (any length, whole words), or
  - if a whole sentence of theirs of 5 words or more (`MIN_OWN_SENTENCE`) is in the text, quoted or not.
  The second case is the real one: Leo's memory in v22 was his own sentence with no quotation marks (`reports/v22_gaps.md` §1b), and block B printed it inside quotes.
- `mind.py:308` (`check_memory`) and `mind.py:368` (`intent_verdict`): after the existing quotation check, `quotes_own_words` returns the same verdict string, `"rejected: S6 a quotation not in the records"`.
- Quotations of other people's words are unchanged: the first S6 loop is as it was, and the new check reads only `pid`'s own events.

**The test** (`test_morning.py:3962`, `DaysTest.test_s6_a_sentence_the_person_spoke_is_a_quotation_not_in_the_records`):

| Case | Before | After |
|---|---|---|
| Leo's own sentence as the meaning, unquoted | `kept` | `rejected: S6 …` |
| `I told Daniel "<his sentence>"` | `kept` | `rejected: S6 …` |
| part of it quoted ("put everyone else in danger") | `kept` | `rejected: S6 …` |
| Daniel quoting his own confession | `kept` | `rejected: S6 …` |
| Daniel's words quoted by Leo (`Daniel said "I took it in the night" at last.`) | `kept` | `kept` |
| Daniel's sentence as Leo's meaning, no quotes | `kept` | `kept` |
| Leo's gist in other words | `kept` | `kept` |
| intent = his own sentence, or quoting it | `kept` | `rejected: S6 …` |
| intent quoting Daniel's words | `kept` | `kept` |

**Red** (`runs/v22_fixes/red.stdout.txt`, before any change to `mind.py`, `world.py` or `quiet.py`):
```
FAIL: test_s6_a_sentence_the_person_spoke_is_a_quotation_not_in_the_records
  File "test_morning.py", line 3979, in test_s6_a_sentence_the_person_spoke_is_a_quotation_not_in_the_records
    self.assertEqual(verdict("leo", mine), S6)
AssertionError: 'kept' != 'rejected: S6 a quotation not in the records'
```

**Reach, on the two live runs** (`runs/v22_fixes/rule1_reach.stdout.txt`, kept memories and intents of minds 3–9 re-judged against their own chronicle): v21 78 kept, **1** now rejected (Leo, mind 5, the "lying about the can" sentence);
v22 73 kept, **2** (Leo, mind 6, the "Risking your life…" sentence; Daniel, mind 6, a memory that contains his whole sentence "I am only trying to keep us safe."). The second is the rule's edge: a paraphrase that holds one of the person's own sentences of 8 words.

## 2. Rule 2: the stale intent (`world.py`)

**The change.**
- `world.py:78`: `INTENT_LINE = "- You meant to:"` (the line `memory.block_b` writes, `memory.py:52-53`).
- `world.py:1159-1162`, in `prompt_parts`: on a quiet day (`self.quiet is not None`), once the person has a spoken line today (`p.said_lines`, written at `world.py:1782`), the carry loses any line starting with `INTENT_LINE`. The rest of block B ("How it left you", the memories) stays. The carry sits outside the trimming budget, so no
  memory or "days before" line is cut or added by this. Their first prompt of the day, before they speak, has it; every later prompt, the bedtime prompt included, does not.
- Not touched: the trimming budget, any other line, days 1 and 2.

**The test** (`test_morning.py:6629`, `PhysicalLayerTest.test_you_meant_to_is_shown_only_until_the_first_speech_act_of_the_day`): v16 seed 2 to day 3, everyone `reassure_all` whenever offered, Mara's prompts recorded:
her first prompt has `- You meant to: "`; all later ones do not and still have "- How it left you:" and the B heading; the bedtime prompt does not; with `said_lines` cleared the intent is back; Leo's and Mara's are independent; on day 2 someone who spoke still sees theirs.

**Red** (before the change):
```
FAIL: test_you_meant_to_is_shown_only_until_the_first_speech_act_of_the_day
    self.assertNotIn(meant, later)
AssertionError: '- You meant to: "' unexpectedly found in 'You are Mara, 17, the youngest, the daughter of the family …
```
An earlier red had the wrong premise (others silent: only 2 prompts of Mara); the test was changed so that 3 or more are recorded, before any production code.

## 3. Rule 3: Q6 with nothing to do (`world.py`, `quiet.py`)

**The change.**
- `world.py:738-741`: `Morning.rain_action(p)`: in the kitchen, raining for them, the bin not out. It is the condition `options_for` already had for `collect_rain` (`world.py:595`, now calling it), so the offer and the skip cannot differ.
- `quiet.py:370-373`, in `hear_rain`: after the room is chosen, if nobody in it has `rain_action`, the entry's `why` is `"Q6 skipped: no rain action"`, and the loop continues: no `ask`, no `q6_done`, no stretch (so no reserved 8 asks). The onset memory (`RAIN_HEARD`), the record of the day's rain and the played-turns branch are as before.

**The test** (`test_morning.py:6671`, `PhysicalLayerTest.test_q6_is_skipped_when_nobody_in_its_room_is_offered_a_rain_action`): day 3 rain at 300–420 with the bin out: the Q6 entry is `(300, False, [], "Q6 skipped: no rain action")`; no Q6 stretch; no Q6 decision; the onset is in the memory of everyone awake and in the day's record;
`q6_done` false; the day's asks equal those of the same day without rain; with the bin not out Q6 fires and plays the room, as before.

**Red:**
```
FAIL: test_q6_is_skipped_when_nobody_in_its_room_is_offered_a_rain_action
AssertionError: Tuples differ: (300, True, ['daniel'], None) != (300, False, [], 'Q6 skipped: no rain action')
```

**Green, the three** (`runs/v22_fixes/green.stdout.txt`):
```
test_s6_a_sentence_the_person_spoke_is_a_quotation_not_in_the_records … ok
test_you_meant_to_is_shown_only_until_the_first_speech_act_of_the_day … ok
test_q6_is_skipped_when_nobody_in_its_room_is_offered_a_rain_action … ok
Ran 3 tests in 4.132s    OK
```

## 4. The replays

**The frozen versions** (`runs/v22_fixes/frozen.stdout.txt`): `v14` to `v9` `check.py`, seeds 1–3 each: **18 of 18 story IDENTICAL and transcript IDENTICAL**; six exits 0. No difference to trace.

**v22 seed 2, no API, on a temp copy of `cache/v22`, `--days 10`** (`runs/v22_fixes/first_miss.py`, `runs/v22_fixes/first_miss.stdout.txt`): the replay asks in the order of the 402 live prompts, and stops at the first prompt that is not in the cache. The control, with the three rules switched off in the script, replays all 498 asks (96 + 402) without a miss.

| Rules on | First cache miss | The first differing line against the cached v22 prompt |
|---|---|---|
| **all three** | **ask 100, day 3, Daniel, min 03** (the 5th live ask) | `-- You meant to: "I will face whatever they say to me in the morning and try to keep us all alive."` (1 differing line): **rule 2**. Daniel spoke at min 00; his next prompt has no intent |
| rule 2 only | the same | the same |
| rule 1 only | ask 295, day 7, Leo, min 00 (live ask 199) | `-- About confronting Daniel: "Risking your life doesn't give you the right to put everyone else in danger by sneaking out without a word, Daniel."` (1 line): **rule 1**. Leo's mind 6 memory fails S6 |
| rule 3 only | ask 326, day 7, Mara, 19:00 (live ask 230) | body line, the 13:57–14:57 memory lines, `+- 17:18: Rain began…` and `Now, 19:00` for the cached `Now, 17:18` (8 lines): **rule 3**. There is no Q6 stretch at 17:18, so the next ask is the evening's |
| none | none: 498 asks from the cache | |

So v22's cache stops answering at day 3, min 03: the run can no longer be replayed past that point, and its answers were given to prompts that had the stale intent. It is the run's own answers that the rules are meant to change.

**A fake 10-day run of seed 2** on the changed code (`runs/v22_fixes/fake10.stdout.txt`): exit 0, 360 fake asks; Q6 fired on days 7 and 9 (the bin is never put out by the fake).

## 5. The full suite

- **First run** (`runs/v22_fixes/unittest_first.stdout.txt`): 288 tests, **1 failure**: `CheckErrorsTest.test_every_other_v15_verdict_stands`, `(1, 2, 'mara', 1)`: "'rejected: S6 a quotation not in the records' != 'kept'".
  The test re-judges the night-mind answers of v15 with today's checks, and keeps a list of verdicts that were deliberately changed (`FIXED`, `test_morning.py:4408`). Two of Mara's memories (seed 1, night 2) were her own spoken sentences, kept in v15 and now rejected by S6, which is the rule:
  - `(1, 2, 'mara', 1)`: "You think you can just sneak out and fix everything by yourself, Daniel, but you can't."
  - `(1, 2, 'mara', 2)`: "You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad."
  Both were added to `FIXED` with a comment (`test_morning.py:4408-4411`), and the docstring says so. No other verdict of v15 moved (`runs/v22_fixes/v15_differences.txt` lists every difference: 6, all in `FIXED`).
- **Second run, after that edit** (`runs/v22_fixes/unittest.stdout.txt`): **288 tests, OK**, exit 0, 5 min 35 s.

## 6. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset; `$PY` is `.venv/Scripts/python.exe`, with `PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`.

```
$ $PY -m unittest test_morning.DaysTest.test_s6_… test_morning.PhysicalLayerTest.test_you_meant_to_… test_morning.PhysicalLayerTest.test_q6_is_skipped_…     (before: Ran 3 tests, FAILED (failures=3), exit 1; after: Ran 3 tests in 4.132s, OK, exit 0)
$ for v in v14 v13 v12 v11 v10 v9; do $PY $v/check.py; done                       18 × "story IDENTICAL, transcript IDENTICAL"; 6 × exit 0
$ $PY runs/v22_fixes/which_rule.py          rule 2 on days 1 and 2: first miss at day 2 (scene 3); scoped to day 3 on: scene 6 (day 3) in all four settings
$ $PY runs/v22_fixes/first_miss.py          the table of §4
$ $PY runs/v22_fixes/rule1_reach.py         v21 1 of 78; v22 2 of 73
$ $PY runs/v22_fixes/fake10.py              exit 0; asks 360
$ $PY -m unittest test_morning              Ran 288 tests in 333.438s   OK   exit 0     (first run: 1 failure, §5)
$ git diff --stat (before the commit)
 mind.py 30 +, quiet.py 3 +, test_morning.py 122 lines, world.py 12 lines: 4 files, 163 insertions, 4 deletions
```

The commit (`git add` of the four code and test files, `reports/v22_gaps.md`, `reports/v22_fixes.md`, `runs/v22gaps/`, `runs/v22_fixes/`) is the one that adds this file: its hash cannot be inside the file it commits, so it is given in the reply and by `git log --oneline -1` (the parent is `966d5b5`).
Before it, `git grep --cached` for the one-off key's middle and for the shape `AQ.` plus 30 or more characters found nothing in the staged files (`runs/v22_fixes/commit_checks.txt`). After it, the same searches over `HEAD`, `git diff --stat` (empty) and `git status --short`
(only the three old `runs/v6/daniel_ate_it-seed{1,2,3}.replay.md`) are in the reply.
