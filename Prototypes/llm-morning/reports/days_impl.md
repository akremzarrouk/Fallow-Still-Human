# Implementation: multi-day life (days_design.md §1–§7, with the amendment to §3.3)

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, or in replay mode, which has no
client.
- Paths are relative to `Prototypes/llm-morning/`.
- `$S` is the session scratchpad (`…/scratchpad/days`). Its read-only scripts are in §9.

## Result

| | |
|---|---|
| Commits | **`65ff403`** the North Star principles in `CLAUDE.md`, on its own. **`ecd8b3a`** freeze v14, new runs default to v15. **`a2e1cdf`** the design and its tests. This report is committed on its own after them. |
| New tests | 15, in class `DaysTest`: N-T1 to N-T14 of the design's §7.1, and one for the amendment. N-T15 is the full suite itself. **Before the change: 15 of 15 error.** **After: 15 pass.** |
| Before, test by test | All 15 stop at `setUp`, on the missing module `chronicle`. Two bodies need no new module, so they were also run on their own against the unchanged code (§5.2): **N-T11 fails** on the old "Elena said you is the one who should go"; **N-T14 passes**, because it guards the frozen versions and can only pass. |
| Full suite | **178 tests, OK** in 209.9 s, on the committed code (before: 163). |
| Existing tests changed | **6**, plus two test helpers (§6). Each pinned the run ending on day 2. |
| Day 1 from the v11 caches | 55, 53 and 45 answers, 0 API requests; story and transcript **IDENTICAL** to `runs/v11` (§7). |
| Frozen versions | **v1 to v14 all IDENTICAL**, 0 API calls (§7). |
| git status | Clean apart from the three old `runs/v6/*.replay.md` files. |

**Three things to know first:**
1. **The run goes to v15, not v14.** The brief said to freeze the current code "as before". Before meant: copy the
   code to the next `vN/` and move `--out` on by one (`7b899e5`). So `v14/` holds the code at `c717b0f`, and
   `morning.py` now defaults to `--out v15`.
   - The design's run plan (§7.3) says "output v14". Read it as v15: `runs/v15/`, `cache/v15/`, and R3 copies
     `cache/v11/…seedN.json` into `cache/v15/`.
   - No run was ever made with the frozen v14 code. So `v14/check.py` replays the one thing it made: day 1, from
     `cache/v11`, against `runs/v11`.
2. **The amendment adds two acts:** `reassure_<q>` and `sit_<q>` (§2). No `comfort_<name>` exists. `reassure_<q>`
   is the comforting act, and its line uses the act's own word: "<When>, <Q> reassured you."
3. **The tests found three bugs on the way, all fixed** (§4.3). One was in the existing code since v12: the day-2
   "About the neighbour's house" line crashed if someone saw a leaver get up and then talk themselves back to bed.

## 1. What was built

| Design | Where | What |
|---|---|---|
| §1 the cycle | `morning.py` `run` | Day 1, night 1, mind 1, day 2, night 2, mind 2, day 3. Each is a scene of its own against the call cap. The gap stays inside `Night.run`, as before. There is no night 3. |
| §1.3 a second night | `night.py` `Night(…, number, house)` | Its own draw strings (`draw_string`). The neighbour's house is taken from the night before (`house_state`) and never drawn again. Whoever is away stays out of bed, noticing and asks. |
| §1.3, §3 the next morning from any day | `night.py` `next_day(prev, n, oracle, chronicle)` | `Morning(day=prev.day + 1)`. Grudge and guilt events keep their scene and get their day words at each new morning (`tag_events`). Without a chronicle, day 2 is exactly as before. |
| §2 the night mind | `mind.py` | `NIGHT_MIND_SYSTEM` (the design's text, verbatim), `schema(ids)`, `records` (R1–R7), `bound_records` (R8), `NightMind.prompt_for` (§2.4), `check_answer` (S1–S9, feeling, intent), and `claims` (S8, §2.7's table and rules). |
| §2.5 schema plumbing | `gemini.py` | `GeminiClient.generate(…, schema=None)`, `FakeClient.generate(…, schema=None)` with a night-mind branch that is broken every n-th time, and `Oracle.ask(…, schema=None)`. The cache key is unchanged. |
| §3.2 A from day 3 | `night.py` `carry_in_later` | Lines Y1–Y8, then the night's lines. Bounded at 360 as before. |
| §3.2 B, §3.3 C, §3.4 the bound | `memory.py` | `block_b`, `block_c` (standing lines, the weight table with the amendment, repeats, older thoughts), `bounded` (`MEMORY_MAX` = 560, the trimming order of §3.4). |
| §3.5 day words | `world.py` | `when_words`. The can line, suspicion minutes, conscience, late-confession grudges and the neighbour line all get computed words. |
| §3.2 the plan-line fix | `world.py` `heard_plan` | "Elena said you **are** the one who should go". |
| §4 the chronicle | `chronicle.py` | Events with ids, witnesses, the line each person got (`views`), gists, folding groups, effects; `fixed` (the culprit; the neighbour's house at first entry) and `open`. Written into `transcript["chronicle"]`. |
| §2.8 records and story | `story.py`, `morning.py` | "## What the night left in them" after each night; "# The second night"; "# The third morning (day 6)". Meta: `night1_asks` to `day3_asks`, `mind<n>` with `memories_proposed/kept/rejected`, and the transcript keys `mind1`, `night2`, `mind2`, `day3` and `chronicle`. |

**How the chronicle learns who perceived what.**
- `Morning.turn` takes a snapshot of each person's memory and pinned facts around every `apply`. What each of them
  gained is that act's view (`Morning.views`).
- Voices through a wall and arrivals are added at the end of the turn, where the rules already write them.
- `Night.line` takes the event each night line tells of.
- So every record is a line the code had already written for that person; nothing is re-derived. These additions
  read state and change no output: day 1 still replays byte for byte (§7).

## 2. The amendment: kind acts between two people

**Every option `world.py` can offer that one person aims at another:**

| Option | Where | Kind act? |
|---|---|---|
| `reassure_<q>` "reassure <Name>" | `world.py:507` | **Yes, added at weight 3.** |
| `sit_<q>` "sit with <Name>" | `world.py:517` | **Yes, added at weight 3.** |
| `give_<q>` "give one of the portions to <Name>" (a food moment) | `world.py:771` | Yes, already in the design's table at 3 ("gave you a portion"). |
| `reassure_all` "reassure everyone here" | `world.py:510` | No: it is to everyone, not between two people. |
| `aside_<q>` "take <Name> aside" | `world.py:524` | No: taking someone aside can be for anything, comfort or reproach. |
| `accuse_<q>`, `confront_<q>`, `send_<q>`, `keep_<q>_home` | `world.py:494`, `502`, … | No: not kind. |
| Night: `stop_<q>`, `go_with_<q>`, `let_<q>_go` | `night.py` | `stop_<q>` is already in the table at 2. The others are not acts on the other person. |

**`comfort_<name>`: NOT FOUND.** `reassure_<q>` is the comforting act.

**The lines** (`memory.py` `person_line`, keys `reassure` and `sit`, counted like accusations):
- someone else: "<When>, <Q> reassured you{ twice| three times| n times}." and "<When>, <Q> sat with you{…}.";
- the self line: "<When>, you reassured <Q>{…}." and "<When>, you sat with <Q>{…}.".

At weight 3 they tie with "accused you" and "gave you a portion", and a tie keeps the older event (§3.3).

**The amendment's test.** `test_amendment_kind_acts_between_two_people` checks:
- `KIND_ACTS == ("reassure", "sit")`, both at weight 3;
- Elena's sit (minute 06) beating her later reassurance (minute 09) on the tie;
- "you reassured Mara twice", and from Mara's side "Leo reassured you twice";
- that `reassure_all` never becomes a line.

## 3. What the design left open, decided here

- **Record text** (§2.3, R1–R3):
  - a pinned fact first, with `, saying: "<words>"` if words came with it;
  - else the person's own line "you <did>, saying: "<words>" You felt <feeling>.";
  - else what they heard.
  - Folding (R7) applies to speech kinds only, by speaker and option.
- **Night records** use the night's own lines, with "Last night you slept in" → "You went to bed in" and a leading
  "In the night " dropped (R5).
- **The night 2 "earlier days" lines** hold the morning's B memories and C lines, each with its ids. The intent and
  feeling lines have no ids, so they are left out.
- **When someone is away on night 2,** the bedtime lines are "Everyone in the house has gone to bed in their own
  room: …" and "<X>'s bed is empty."
  - The design does not word these.
  - **No test covers this case:** no test's draws leave anyone away on a second night.
- **Day words are stamped on the person and the event** (`confessed_day`, `confession_heard_day`, `denial_day`,
  `accused_day`, `suspected_past`, and a scene on each carried grudge or guilt event). They are not looked up in the
  chronicle. The words are the ones §3.5 specifies. `p.yesterday` is no longer used.
- **Transcript keys:** night 1 keeps `"night"` and the meta keeps `night_asks`. Both are what earlier tests and
  reports read. `night1_asks` is added beside it.
- **§3.3's optional "while you were hungry"** on an eat line is not written. The chronicle keeps no hunger at the
  moment of the act.

## 4. On the way

### 4.1 Test corrections, all in the new tests

- **Before any implementation:** N-T8 expected house day 7 to call day 4 "two days ago". Day 4 is today. It now
  asks about day 2 and night 2, as intended.
- **After the first implementation run, two expectations of mine were wrong. The behaviour asserted is the same:**
  - N-T8 expected Leo's grudge line to show the minute-03 accusation. The existing rule shows the last 4 events
    (`world.py:111`), so minute 03 is cut. It now asserts "…accused you of taking the can at minute", as T10 does
    for day 2.
  - N-T6 compared block C's item lines, but the older thought is added when the block is rendered (`render_c`). It
    now compares the rendered lines.

### 4.2 Runs of the new tests

- **First run:** 5 pass, 9 errors (`Morning.next_day` did not pass `chronicle` on), 1 failure (N-T5, S8).
- **Second run:** 9 pass. 3 errors: the latent neighbour-line crash, in the three-day fake runs. 3 failures:
  N-T5, plus the two expectations above.
- **Third run:** 15 pass.

### 4.3 The bugs the tests found

1. **`Morning.next_day` dropped the chronicle.** It had kept day 2's old signature. It now passes `chronicle` on.
2. **The claim screen missed "Leo ate mine too and lied to my face about it."** The second clause has no subject of
   its own, so it should take "Leo". But the subject search ran past the verb and stopped at the object "it",
   which it read as an unresolved subject. The search now stops at the first verb. §2.7's example is rejected under
   S8, as designed.
3. **The neighbour line could crash (present since v12, in `night.py`'s `neighbour_line`).**
   - `Night.knows` holds anyone a person saw get up to go, including a leaver who was stopped and went back to bed.
   - The day-2 line then looked for that person's trip group with `next(…)` and found none: `StopIteration`.
   - It had never happened in a test or a run. The three-day fake runs reached it.
   - Only people who actually went out now count as known goers.

## 5. Tests

### 5.1 Before the change

The new tests were written first, on the code at `ecd8b3a`:
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.DaysTest
test_amendment_kind_acts_between_two_people (test_morning.DaysTest.test_amendment_kind_acts_between_two_people) ... ERROR
test_n_t10_thoughts_stay_private (test_morning.DaysTest.test_n_t10_thoughts_stay_private) ... ERROR
test_n_t11_the_plan_line_says_you_are (test_morning.DaysTest.test_n_t11_the_plan_line_says_you_are) ... ERROR
test_n_t12_schema_plumbing (test_morning.DaysTest.test_n_t12_schema_plumbing) ... ERROR
test_n_t13_counting (test_morning.DaysTest.test_n_t13_counting) ... ERROR
test_n_t14_frozen_versions_still_replay (test_morning.DaysTest.test_n_t14_frozen_versions_still_replay) ... ERROR
test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone (test_morning.DaysTest.test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone) ... ERROR
test_n_t2_the_cycle (test_morning.DaysTest.test_n_t2_the_cycle) ... ERROR
test_n_t3_the_night_minds_prompt_exactly (test_morning.DaysTest.test_n_t3_the_night_minds_prompt_exactly) ... ERROR
test_n_t4_records_hold_only_what_was_perceived (test_morning.DaysTest.test_n_t4_records_hold_only_what_was_perceived) ... ERROR
test_n_t5_the_checks (test_morning.DaysTest.test_n_t5_the_checks) ... ERROR
test_n_t6_the_blocks_exactly (test_morning.DaysTest.test_n_t6_the_blocks_exactly) ... ERROR
test_n_t7_the_bound (test_morning.DaysTest.test_n_t7_the_bound) ... ERROR
test_n_t8_day_words (test_morning.DaysTest.test_n_t8_day_words) ... ERROR
test_n_t9_the_chronicle (test_morning.DaysTest.test_n_t9_the_chronicle) ... ERROR

======================================================================
ERROR: test_amendment_kind_acts_between_two_people (test_morning.DaysTest.test_amendment_kind_acts_between_two_people)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t10_thoughts_stay_private (test_morning.DaysTest.test_n_t10_thoughts_stay_private)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t11_the_plan_line_says_you_are (test_morning.DaysTest.test_n_t11_the_plan_line_says_you_are)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t12_schema_plumbing (test_morning.DaysTest.test_n_t12_schema_plumbing)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t13_counting (test_morning.DaysTest.test_n_t13_counting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t14_frozen_versions_still_replay (test_morning.DaysTest.test_n_t14_frozen_versions_still_replay)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone (test_morning.DaysTest.test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t2_the_cycle (test_morning.DaysTest.test_n_t2_the_cycle)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t3_the_night_minds_prompt_exactly (test_morning.DaysTest.test_n_t3_the_night_minds_prompt_exactly)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t4_records_hold_only_what_was_perceived (test_morning.DaysTest.test_n_t4_records_hold_only_what_was_perceived)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t5_the_checks (test_morning.DaysTest.test_n_t5_the_checks)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t6_the_blocks_exactly (test_morning.DaysTest.test_n_t6_the_blocks_exactly)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t7_the_bound (test_morning.DaysTest.test_n_t7_the_bound)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t8_day_words (test_morning.DaysTest.test_n_t8_day_words)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

======================================================================
ERROR: test_n_t9_the_chronicle (test_morning.DaysTest.test_n_t9_the_chronicle)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3651, in setUp
    self.chron = importlib.import_module("chronicle")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'chronicle'

----------------------------------------------------------------------
Ran 15 tests in 0.059s

FAILED (errors=15)
exit=1
```

### 5.2 Two bodies on their own, before the change

`$S/before_own.py` runs N-T11's and N-T14's bodies with NightTest's `setUp`, without the new modules:
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/before_own.py
test_n_t11_the_plan_line_says_you_are (__main__.Own.test_n_t11_the_plan_line_says_you_are) ... FAIL
test_n_t14_frozen_versions_still_replay (__main__.Own.test_n_t14_frozen_versions_still_replay) ... ok

======================================================================
FAIL: test_n_t11_the_plan_line_says_you_are (__main__.Own.test_n_t11_the_plan_line_says_you_are)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4143, in test_n_t11_the_plan_line_says_you_are
    self.assertEqual(plan, "About going there tonight: Elena said you are the one who should go (min 00).")
AssertionError: 'About going there tonight: Elena said you is the one who should go (min 00).' != 'About going there tonight: Elena said you are the one who should go (min 00).'
- About going there tonight: Elena said you is the one who should go (min 00).
?                                           ^^
+ About going there tonight: Elena said you are the one who should go (min 00).
?                                           ^^^


----------------------------------------------------------------------
Ran 2 tests in 3.754s

FAILED (failures=1)
```

### 5.3 After the change

The new tests on the committed code (`a2e1cdf`):
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.DaysTest
test_amendment_kind_acts_between_two_people (test_morning.DaysTest.test_amendment_kind_acts_between_two_people) ... ok
test_n_t10_thoughts_stay_private (test_morning.DaysTest.test_n_t10_thoughts_stay_private) ... ok
test_n_t11_the_plan_line_says_you_are (test_morning.DaysTest.test_n_t11_the_plan_line_says_you_are) ... ok
test_n_t12_schema_plumbing (test_morning.DaysTest.test_n_t12_schema_plumbing) ... ok
test_n_t13_counting (test_morning.DaysTest.test_n_t13_counting) ... ok
test_n_t14_frozen_versions_still_replay (test_morning.DaysTest.test_n_t14_frozen_versions_still_replay) ... ok
test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone (test_morning.DaysTest.test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone) ... ok
test_n_t2_the_cycle (test_morning.DaysTest.test_n_t2_the_cycle) ... ok
test_n_t3_the_night_minds_prompt_exactly (test_morning.DaysTest.test_n_t3_the_night_minds_prompt_exactly) ... ok
test_n_t4_records_hold_only_what_was_perceived (test_morning.DaysTest.test_n_t4_records_hold_only_what_was_perceived) ... ok
test_n_t5_the_checks (test_morning.DaysTest.test_n_t5_the_checks) ... ok
test_n_t6_the_blocks_exactly (test_morning.DaysTest.test_n_t6_the_blocks_exactly) ... ok
test_n_t7_the_bound (test_morning.DaysTest.test_n_t7_the_bound) ... ok
test_n_t8_day_words (test_morning.DaysTest.test_n_t8_day_words) ... ok
test_n_t9_the_chronicle (test_morning.DaysTest.test_n_t9_the_chronicle) ... ok

----------------------------------------------------------------------
Ran 15 tests in 30.600s

OK
exit=0
```

The full suite on the committed code. These are the new tests, the six changed tests and the summary; every other
test line reads `ok`. The two 429 tests print their retry message before `ok`, on the next line.
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning
…
test_amendment_kind_acts_between_two_people (test_morning.DaysTest.test_amendment_kind_acts_between_two_people) ... ok
test_n_t10_thoughts_stay_private (test_morning.DaysTest.test_n_t10_thoughts_stay_private) ... ok
test_n_t11_the_plan_line_says_you_are (test_morning.DaysTest.test_n_t11_the_plan_line_says_you_are) ... ok
test_n_t12_schema_plumbing (test_morning.DaysTest.test_n_t12_schema_plumbing) ... ok
test_n_t13_counting (test_morning.DaysTest.test_n_t13_counting) ... ok
test_n_t14_frozen_versions_still_replay (test_morning.DaysTest.test_n_t14_frozen_versions_still_replay) ... ok
test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone (test_morning.DaysTest.test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone) ... ok
test_n_t2_the_cycle (test_morning.DaysTest.test_n_t2_the_cycle) ... ok
test_n_t3_the_night_minds_prompt_exactly (test_morning.DaysTest.test_n_t3_the_night_minds_prompt_exactly) ... ok
test_n_t4_records_hold_only_what_was_perceived (test_morning.DaysTest.test_n_t4_records_hold_only_what_was_perceived) ... ok
test_n_t5_the_checks (test_morning.DaysTest.test_n_t5_the_checks) ... ok
test_n_t6_the_blocks_exactly (test_morning.DaysTest.test_n_t6_the_blocks_exactly) ... ok
test_n_t7_the_bound (test_morning.DaysTest.test_n_t7_the_bound) ... ok
test_n_t8_day_words (test_morning.DaysTest.test_n_t8_day_words) ... ok
test_n_t9_the_chronicle (test_morning.DaysTest.test_n_t9_the_chronicle) ... ok
test_a_morning_completes_and_writes_a_story (test_morning.FakeMorningTest.test_a_morning_completes_and_writes_a_story) ... ok
test_t12_the_budget (test_morning.NightTest.test_t12_the_budget) ... ok
test_t13_counting_and_the_story (test_morning.NightTest.test_t13_counting_and_the_story) ... ok
test_t1_the_story_begins_with_day1_unchanged (test_morning.NightTest.test_t1_the_story_begins_with_day1_unchanged) ... ok
test_daniels_prompt_never_mentions_being_heard (test_morning.WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard) ... ok
test_no_prompt_says_who_leo_heard (test_morning.WitnessScenarioTest.test_no_prompt_says_who_leo_heard) ... ok
…
Ran 178 tests in 209.868s

OK
exit=0
```

## 6. Existing tests changed

| Test | Why | Change |
|---|---|---|
| `FakeMorningTest.test_a_morning_completes_and_writes_a_story` | Pinned at most 150 API requests for the whole run (failed: 212). The cap counts each scene apart, and a run now has seven. | At most 150 for each scene. |
| `NightTest.test_t1_the_story_begins_with_day1_unchanged` | Pinned the transcript keys `day1`, `night`, `day2`. | Adds `mind1`, `night2`, `mind2`, `day3`, `chronicle`. |
| `NightTest.test_t12_the_budget` | Bounded night prompts at 1,450 + 380, with no carried block (failed: 1,834 against 1,830). A second night's prompts carry day 2's A and B. | Night prompts that carry blocks, and every morning, at most 1,450 + 380 + 610 (`MEMORY_HARD`, §3.4's ceiling). `without_blocks` also strips B and C. |
| `NightTest.test_t13_counting_and_the_story` | The asks of day 1, night and day 2 summed to the answers (failed: 177 against 276). | Adds mind 1, night 2, mind 2 and day 3. |
| `WitnessScenarioTest.test_daniels_prompt_never_mentions_being_heard` | "woke and heard" and "did not see who" were never to appear in Daniel's prompts. From the second night, Daniel can himself wake at the front door, and the night's lines say just that. | Lines about the front door are left out of the check. Every other phrase is still checked. |
| `WitnessScenarioTest.test_no_prompt_says_who_leo_heard` | Leo's can line had to match day 2's words. On day 3 it says "two days ago" or "the night before last". | The pattern also accepts §3.5's words for earlier days and nights. |
| helper `NightScripted` | Had no answer for a night-mind prompt. | Takes `schema`, and answers a night mind with queued answers or one memory citing the first record. |
| helper `without_blocks` | Stripped block A only. | Also strips B and C. `MEMORY_HARD = 610` is added beside `CARRY_MAX`. |

## 7. Replays

**Day 1 with the new code, from `cache/v11`** (`$S/replay_day1.py`, §9). The chronicle is built on it before the
story is rendered:
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/replay_day1.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL; chronicle: 40 day-1 events
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL; chronicle: 45 day-1 events
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL; chronicle: 33 day-1 events
exit=0
```

**Every frozen version's `check.py`:**
```
$ python v14/check.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v13/check.py
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v12/check.py
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v11/check.py
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v8/check.py
daniel_ate_it_leo_heard-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v7/check.py
daniel_ate_it-seed1: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 48 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 33 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 18 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 67 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v6/check.py
daniel_ate_it-seed1: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 66 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed1: replayed 44 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed2: replayed 43 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it_leo_heard-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v5/check.py
daniel_ate_it-gemma-seed1: replayed 21 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed2: replayed 13 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed3: replayed 20 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed4: replayed 19 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-gemma-seed5: replayed 14 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed1: replayed 46 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed2: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
mara_ate_it-seed3: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed1: replayed 56 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed2: replayed 93 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
miscount-seed3: replayed 70 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v4/check.py
seed 1: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 39 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 4: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 5: replayed 41 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v3/check.py
seed 1: replayed 37 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 36 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 30 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v2/check.py
seed 1: replayed 7 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 2: replayed 25 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
seed 3: replayed 11 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
```

**v1** has no `check.py`. `$S/v1_replay.py` (as in food_confront_impl §4) replays it in a scratch copy:
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe $S/v1_replay.py
v1 seed 1: exit 0; api_requests 0; IDENTICAL
v1 seed 2: exit 0; api_requests 0; IDENTICAL
v1 seed 3: exit 0; api_requests 0; IDENTICAL
exit=0
```

## 8. The diffs

### `65ff403` the North Star principles

```diff
commit 65ff403f11d11d6a29563cbd1a01c3680596728a
Author: Akrem <akremzarrouk2222@gmail.com>
Date:   Mon Oct 5 11:26:02 2026 +0100

    CLAUDE.md: North Star principles
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/CLAUDE.md b/CLAUDE.md
index 184f5f3..482422e 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -17,3 +17,12 @@ Never stop processes by name or broad filters; only by the exact process ID you
   not by whether a number moves. A metric is a clue, never the goal.
 - Before proposing a mechanism, argue against it first: would a real
   person do this, and for what reason?
+
+## North Star principles
+- The code owns the truth: what happened, who perceived it, every
+  number. The AI owns judgment and words. The AI never owns state.
+- The code draws conclusions from what people perceive; the AI decides
+  what they do about it.
+- A line that describes an act makes the small model do that act. State
+  situations; leave the choice open.
+- Mechanisms may be unhuman; the output must read as human.
```

### `ecd8b3a` the freeze

The eleven copied files were compared with `git show HEAD:<file> | cmp - v14/<file>` before the commit. All were
identical (§10). Without them:

```diff
commit ecd8b3a3de465d7007d7f9d1a1ac7fc38149af33
Author: Akrem <akremzarrouk2222@gmail.com>
Date:   Mon Oct 5 11:27:34 2026 +0100

    LLM morning: freeze v14, new runs default to v15
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

 Prototypes/llm-morning/.gitignore      |    2 +
 Prototypes/llm-morning/morning.py      |   12 +-
 Prototypes/llm-morning/v14/check.py    |   52 +
 Prototypes/llm-morning/v14/data.py     |  208 ++++
 Prototypes/llm-morning/v14/gemini.py   |  270 +++++
 Prototypes/llm-morning/v14/metrics.py  |  182 ++++
 Prototypes/llm-morning/v14/metrics3.py |  141 +++
 Prototypes/llm-morning/v14/metrics4.py |  149 +++
 Prototypes/llm-morning/v14/metrics5.py |  152 +++
 Prototypes/llm-morning/v14/morning.py  |  230 +++++
 Prototypes/llm-morning/v14/night.py    |  668 ++++++++++++
 Prototypes/llm-morning/v14/story.py    |  541 ++++++++++
 Prototypes/llm-morning/v14/talk.py     |  139 +++
 Prototypes/llm-morning/v14/world.py    | 1750 ++++++++++++++++++++++++++++++++
 14 files changed, 4490 insertions(+), 6 deletions(-)

diff --git a/Prototypes/llm-morning/.gitignore b/Prototypes/llm-morning/.gitignore
index f306f41..084ecdf 100644
--- a/Prototypes/llm-morning/.gitignore
+++ b/Prototypes/llm-morning/.gitignore
@@ -29,3 +29,5 @@ runs/v13/fake/
 cache/v13/fake-*
 runs/v14/fake/
 cache/v14/fake-*
+runs/v15/fake/
+cache/v15/fake-*
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index 96c450a..aa3aa92 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -9,9 +9,9 @@ writes them as one story (reports/night_design.md).
 
     --scenario NAME   daniel_ate_it (default), mara_ate_it or miscount (data.SCENARIOS)
     --model KEY       another model from config.json `models` (default: config.json `model`)
-    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v14; v4 replays
-                      the fourth version's runs; v5/check.py to v13/check.py replay the
-                      fifth's to thirteenth's)
+    --out DIR         where runs and answers go: runs/DIR and cache/DIR (default v15; v4 replays
+                      the fourth version's runs; v5/check.py to v14/check.py replay the
+                      fifth's to fourteenth's)
 
 Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
 are in config.json; the call limit counts each of the three apart. The key is read from
@@ -80,13 +80,13 @@ def day_meta(m, scene):
 
 
 def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
-        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v14"):
+        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v15"):
     config = load_config(config_path or os.path.join(HERE, "config.json"))
     if model_key:
         config = {**config, **config["models"][model_key]}
     model_name = "fake" if fake else config["model"]
     # Each version's runs and answers live apart (runs/ and cache/ for the first, runs/vN and
-    # cache/vN after), which v1/ to v13/ can still replay.
+    # cache/vN after), which v1/ to v14/ can still replay.
     runs_dir = runs_dir or os.path.join(HERE, "runs", out, "fake" if fake else "")
     cache_dir = cache_dir or os.path.join(HERE, "cache", out)
     os.makedirs(runs_dir, exist_ok=True)
@@ -219,7 +219,7 @@ def main():
     ap.add_argument("--config", default=None)
     ap.add_argument("--scenario", default=data.DEFAULT_SCENARIO, choices=sorted(data.SCENARIOS))
     ap.add_argument("--model", default=None, help="a key of config.json `models`")
-    ap.add_argument("--out", default="v14")
+    ap.add_argument("--out", default="v15")
     args = ap.parse_args()
     _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
                   scenario=args.scenario, model_key=args.model, out=args.out)
diff --git a/Prototypes/llm-morning/v14/check.py b/Prototypes/llm-morning/v14/check.py
new file mode 100644
index 0000000..dda8829
--- /dev/null
+++ b/Prototypes/llm-morning/v14/check.py
@@ -0,0 +1,52 @@
+"""Replays what the fourteenth version's code made, and checks it.
+
+    python v14/check.py
+
+v14/ is a frozen copy of the code at 90133b4 and c717b0f: v13 plus the neutral food moment line and
+confront_<name> from the night on (reports/food_confront_impl.md). No run was ever made with it: it was
+frozen before multi-day life (reports/days_design.md) was built on top. What it can still be held to is day 1,
+which it replays from the v11 answers. Each replayed day-1 story must come out byte for byte as runs/v11/<name>.md,
+and its transcript as the one saved beside it. Replaying makes no API calls.
+"""
+import json
+import os
+import sys
+
+HERE = os.path.dirname(os.path.abspath(__file__))
+ROOT = os.path.dirname(HERE)
+sys.path.insert(0, HERE)
+
+from gemini import Cache, Oracle                         # noqa: E402  (v14's own modules)
+from story import render                                 # noqa: E402
+from world import Morning                                # noqa: E402
+
+# (scenario, model name, seeds): day 1 of these, from cache/v11, against runs/v11.
+RUNS = [("daniel_ate_it", "gemini-3.5-flash-lite", (1, 2, 3))]
+
+
+def main():
+    ok = True
+    for scenario, model, seeds in RUNS:
+        for seed in seeds:
+            name = f"{scenario}-seed{seed}"
+            cache = Cache(os.path.join(ROOT, "cache", "v11", f"{model}-{name}.json"))
+            oracle = Oracle(cache, model, seed, client=None, replay=True)
+            morning = Morning(oracle, seed, scenario)
+            for t in range(morning.turns):
+                morning.turn(t)
+            morning.finish()
+            text = render(morning, seed, model, f"python morning.py --seed {seed}")
+            base = os.path.join(ROOT, "runs", "v11", name)
+            with open(base + ".md", "rb") as f:
+                same_story = f.read() == text.encode("utf-8")
+            with open(base + ".transcript.json", encoding="utf-8") as f:
+                same_transcript = json.load(f) == json.loads(json.dumps(morning.transcript))
+            ok &= same_story and same_transcript
+            print(f"{name}: day 1 replayed {oracle.from_cache} answers from cache/v11, 0 API calls; "
+                  f"story {'IDENTICAL' if same_story else 'DIFFERS'}, transcript "
+                  f"{'IDENTICAL' if same_transcript else 'DIFFERS'}")
+    return 0 if ok else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
```

### `a2e1cdf` the design and its tests

````diff
commit a2e1cdfe843583a957ae72a7b6714abb163d7d21
Author: Akrem <akremzarrouk2222@gmail.com>
Date:   Tue Oct 6 09:32:58 2026 +0100

    LLM morning: multi-day life (night mind, chronicle, memory blocks, night 2, day 3)
    
    As reports/days_design.md §1-§7: a second night and a third morning; one night-mind
    call per person per night, its memories checked (S1-S9) before any reaches a prompt;
    blocks A, B and C under one bound (560); the chronicle with the neighbour's house
    fixed once; day words computed; the plan line says "you are". Amendment to §3.3's
    table: the kind acts between two people (reassure_<q>, sit_<q>) at weight 3.
    Tests N-T1 to N-T14 and the amendment's (DaysTest); six existing tests updated.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/Prototypes/llm-morning/chronicle.py b/Prototypes/llm-morning/chronicle.py
new file mode 100644
index 0000000..29e9f45
--- /dev/null
+++ b/Prototypes/llm-morning/chronicle.py
@@ -0,0 +1,234 @@
+"""The world chronicle (reports/days_design.md, §4): the code's record of what happened each day and night, facts
+only. Each event is one thing done, with who did it, who perceived it and how, and the line each of them got of it.
+Facts the world had not decided are fixed here the first time a rule needs them, and never drawn again.
+
+It reads the scenes once they are over (a finished Morning, a finished Night) and changes nothing in them. The
+night minds' answers are kept beside it (`minds`), never among the events: they are what a person made of the
+facts, not facts.
+"""
+import data
+from talk import SPEECH, act_of
+from world import NAMES, day_index
+
+KEYS = ("id", "scene", "minute", "kind", "option", "actor", "target", "members", "words", "room", "witnesses",
+        "text", "gist", "group", "effects", "views", "outcome")
+
+
+def he(pid):
+    return data.PRONOUNS[pid]["he"]
+
+
+def gist(e, pid):
+    """A short name for an event, as `pid` would call it (reports/days_design.md, §3.2, block B)."""
+    actor, target, kind, option = e.get("actor"), e.get("target"), e["kind"], e.get("option") or ""
+    t = "you" if target == pid else NAMES.get(target, "")
+    pronoun = he(actor) if actor else "they"
+    phrases = {
+        "opening": "the count of the pantry" if e["scene"] == "D1" else "everyone coming into the kitchen",
+        "ask": "asking who took the can", "deny": "denying taking it", "accuse": f"accusing {t} of taking the can",
+        "confess": "admitting taking the can", "confront": f"confronting {t}",
+        "reassure": f"reassuring {t}" if target else "reassuring everyone", "say": "speaking to everyone",
+        "propose": "saying someone should go to the neighbour's house",
+        "volunteer": (f"saying {pronoun} still means to go" if option == "still_going"
+                      else "offering to go to the neighbour's house"),
+        "object": f"saying {t} must stay home" if target else "saying nobody should go",
+        "back": f"saying {t} should go", "decline": f"saying {pronoun} will not go",
+        "eat": "eating a portion", "eat_empty": "reaching for the empty shelf", "share": "sharing out the food",
+        "give": f"giving {t} a portion", "eat_given": "eating a portion handed over",
+        "refuse_given": "putting a handed portion back", "search": "searching", "search_done": "searching",
+        "go": "leaving the room", "sit": f"sitting with {t}", "aside": f"taking {t} aside",
+        "accept_aside": "going aside", "refuse_aside": "refusing to go aside", "gap": "the afternoon and evening",
+        "bedtime": "going to bed", "got_up": "getting up in the night", "at_door": "going to the front door in the night",
+        "door": "the front door opening in the night", "reaction": "what you did in the night",
+        "stop": f"telling {t}, low, not to go", "answer": "answering, low, in the night",
+        "went_out": "going out to the neighbour's house", "street": "the neighbour's house and the street",
+        "return": "coming back in before dawn"}
+    phrase = phrases.get(kind, kind)
+    if kind in ("door", "gap", "street"):
+        return phrase
+    if actor == pid:
+        return phrase + (" yourself" if kind in ("eat", "went_out") else "")
+    return f"{NAMES[actor]} {phrase}" if actor else phrase
+
+
+def view_text(pid, actor, words, view):
+    """The record of an act for `pid`, from the lines they got of it (§2.3, R1-R3): a pinned fact first, with the
+    words said while doing it; their own speech with its words and the feeling they gave; or what they heard."""
+    sure, memory = view.get("sure", []), view.get("memory", [])
+    if sure:
+        text = sure[0]
+        if words and words not in text:
+            text = text.rstrip(".") + f', saying: "{words}"'
+        return text
+    if pid == actor and memory:
+        verb, sep, feel = memory[0].partition(". You felt ")
+        if words:
+            return f'{verb.rstrip(".")}, saying: "{words}"' + (f" You felt {feel}" if sep else "")
+        return memory[0]
+    return " ".join(memory)
+
+
+def night_text(line):
+    """A night line in the night's own words (§2.3, R5)."""
+    line = line.replace("Last night you slept in", "You went to bed in")
+    if line.startswith("In the night "):
+        line = line[len("In the night "):]
+    return line[0].upper() + line[1:]
+
+
+class Chronicle:
+    def __init__(self, seed, culprit=None):
+        self.seed, self.culprit = seed, culprit
+        self.scenes, self.events, self.open = [], [], []
+        self.fixed = {"culprit": {"value": culprit, "draw": None, "string": None, "scene": "before D1",
+                                  "why": "the scenario says who took the can, if anyone"}}
+        self.by_id = {}
+        self.minds = {}             # night number -> person -> the night mind's checked answer (mind.py)
+        self.nights = []            # the Night objects, in order (not saved)
+        self._house = None
+
+    # ---------- reading ----------
+    def event(self, eid):
+        return self.by_id.get(eid)
+
+    def perceived(self, pid):
+        return [e for e in self.events if pid in e["witnesses"]]
+
+    def knows_culprit(self, pid):
+        """Who took the can, as `pid` knows it: themselves, or a confession they perceived."""
+        if self.culprit is None:
+            return None
+        if pid == self.culprit:
+            return pid
+        if any(e["kind"] == "confess" and e["actor"] == self.culprit and pid in e["witnesses"] for e in self.events):
+            return self.culprit
+        return None
+
+    def house_state(self):
+        """The neighbour's house as the last night left it, for the next night (§4.3)."""
+        return self._house
+
+    def to_json(self):
+        return {"scenes": self.scenes, "events": self.events, "fixed": self.fixed, "open": self.open}
+
+    # ---------- writing ----------
+    def add(self, e):
+        """One event, its missing fields filled; returns it."""
+        e = {**{k: None for k in KEYS}, "witnesses": {}, "gist": {}, "effects": {}, "views": {}, "text": "", **e}
+        e = {k: e[k] for k in KEYS}
+        if not e["gist"]:
+            e["gist"] = {pid: gist(e, pid) for pid in e["witnesses"]}
+        self.events.append(e)
+        self.by_id[e["id"]] = e
+        return e
+
+    @staticmethod
+    def state(m):
+        """A scene's end, in the rules' numbers."""
+        people = m.people.values()
+        return {"shelf": m.portions, "away": sorted(m.away),
+                "rooms": {p.id: p.room for p in people},
+                "hunger": {p.id: round(p.hunger, 4) for p in people},
+                "grudges": {p.id: {t: g.strength for t, g in p.grudges.items() if g.strength} for p in people},
+                "suspicion": {p.id: p.suspicion.state() for p in people},
+                "guilt": {p.id: p.guilt for p in people if p.guilt is not None},
+                "knows_culprit": {p.id: p.knows_culprit for p in people}}
+
+    def add_day(self, m):
+        """A finished morning: the opening, then every act that is not silence and that someone perceived (§4.2)."""
+        k = day_index(m.day)
+        sid = f"D{k}"
+        self.scenes.append({"id": sid, "kind": "day", "house_day": m.day,
+                            "start": {"shelf": m.start_portions, "away": sorted(m.away)}, "end": self.state(m)})
+        n = 0
+
+        def new_id():
+            nonlocal n
+            n += 1
+            return f"{sid}-{n:03d}"
+        present = [q for q in data.ORDER if q not in m.away]
+        opening = {q: m.people[q].sure[0][8:] for q in present if m.people[q].sure}
+        first = next(iter(opening.values()), "")
+        self.add({"id": new_id(), "scene": sid, "minute": 0, "kind": "opening", "room": "kitchen",
+                  "actor": "elena" if m.day == 4 else None,
+                  "witnesses": {q: ("did" if m.day == 4 and q == "elena" else "saw") for q in opening},
+                  "text": first.rsplit(" (you ", 1)[0], "views": opening})
+        said = iter(m.said)
+        shelf = m.start_portions
+        groups = {}
+        for turn in m.transcript["turns"]:
+            for a in turn["acts"]:
+                text = (next(said, None) or {}).get("text") if a["words"] else None
+                seq = a["decided_at"][1]
+                views = m.views.get(seq, {})
+                heard = m.voices_heard.get(seq, {})
+                if a["option"] == "silent" or (a["mode"] == "routine" and not views):
+                    continue
+                kind, target = act_of(a["option"])
+                came = a.get("came_of_it") or ""
+                if kind == "eat" and "found it empty" in came:
+                    kind = "eat_empty"
+                if came.startswith("went through the room and found nothing"):
+                    kind = "search_done"
+                # The person an act is aimed at, if one: never a room (go_<room>) or everyone (reassure_all).
+                if kind not in ("accuse", "reassure", "confront", "back", "object", "give", "sit", "aside") \
+                        or target not in data.PEOPLE:
+                    target = None
+                effects = {}
+                if kind in ("eat", "give", "refuse_given", "share"):
+                    after = {"eat": shelf - 1, "give": shelf - 1, "refuse_given": shelf + 1, "share": 0}[kind]
+                    effects, shelf = {"shelf": [shelf, after]}, after
+                witnesses = {a["who"]: "did"}
+                witnesses.update({q: "saw" for q in views if q != a["who"]})
+                witnesses.update({q: "voices" for q in heard if q not in witnesses})
+                texts = {q: view_text(q, a["who"], a["words"], v) for q, v in views.items()}
+                texts.update({q: f"Voices from the {data.ROOMS[r]}." for q, r in heard.items() if q not in texts})
+                e = self.add({"id": new_id(), "scene": sid, "minute": turn["minute"], "kind": kind,
+                              "option": a["option"], "actor": a["who"], "target": target, "words": a["words"],
+                              "room": a["room"], "witnesses": witnesses,
+                              "text": text or f"{NAMES[a['who']]} {came}".strip(), "effects": effects, "views": texts})
+                if a["words"] and kind in SPEECH:
+                    groups.setdefault((a["who"], a["option"]), []).append(e["id"])
+        for ids in groups.values():
+            if len(ids) > 1:
+                for i in ids:
+                    self.by_id[i]["group"] = list(ids)
+
+    def add_night(self, n):
+        """A finished night, after its gap: the gap, then every event of the night with the line each person
+        got of it; the neighbour's house fixed the first time anyone got inside (§4.3)."""
+        k = n.number
+        present = [q for q in data.ORDER if q not in n.prev.away]
+        self.scenes.append({"id": f"G{k}", "kind": "gap"})
+        self.add({"id": f"G{k}-01", "scene": f"G{k}", "minute": data.MINUTES, "kind": "gap",
+                  "witnesses": {q: "saw" for q in present}, "text": data.GAP})
+        ids = {e["key"]: f"N{k}-{i:02d}" for i, e in enumerate(n.events, 1)}
+        views = {}
+        for pid in data.ORDER:
+            for line, key in zip(n.lines[pid], n.line_events[pid]):
+                if key is None:
+                    continue
+                v = views.setdefault(key, {})
+                v[pid] = (v[pid] + " " if pid in v else "") + night_text(line)
+        for e in n.events:
+            self.add({"id": ids[e["key"]], "scene": f"N{k}", "minute": data.MINUTES, "kind": e["kind"],
+                      "option": e.get("option"), "actor": e["actor"], "target": e.get("target"),
+                      "members": e.get("members"), "words": e.get("words"), "witnesses": e["witnesses"],
+                      "outcome": e.get("outcome"),
+                      "text": f"{NAMES[e['actor']]}: {e['kind']}" + (f" ({e['outcome']})" if e.get("outcome") else ""),
+                      "views": views.get(e["key"], {})})
+        self.scenes.append({"id": f"N{k}", "kind": "night", "end": self.state(n.m) | {"shelf": n.portions,
+                                                                                      "away": sorted(n.away)}})
+        got_in = [g for g in n.groups if g["street"] in ("clean", "scare_back")]
+        if got_in and "neighbour_house" not in self.fixed:
+            self.fixed["neighbour_house"] = {"value": n.house, "draw": n.house_u, "string": n.draw_string("house"),
+                                             "scene": f"N{k}", "why": "someone got inside for the first time"}
+        if k == 1:
+            self.open.append({"name": "the street", "since": "N1",
+                              "what": "beyond 'something was moving', nothing about the street is fixed"})
+        for x in data.ORDER:
+            if x in n.away and x not in n.prev.away:
+                self.open.append({"name": f"where {NAMES[x]} is", "since": f"N{k}",
+                                  "what": "went out in the night and has not come back"})
+        self._house = n.house_state()
+        self.nights.append(n)
diff --git a/Prototypes/llm-morning/gemini.py b/Prototypes/llm-morning/gemini.py
index 909e6df..c94d9ea 100644
--- a/Prototypes/llm-morning/gemini.py
+++ b/Prototypes/llm-morning/gemini.py
@@ -91,14 +91,16 @@ class GeminiClient:
                 self._sleep(wait)
         self._last = self._clock()
 
-    def generate(self, system, prompt):
+    def generate(self, system, prompt, schema=None):
+        """schema: the response schema; RESPONSE_SCHEMA (a decision) unless given (a night mind,
+        reports/days_design.md, §2.5)."""
         from google.genai import errors
         config = self._types.GenerateContentConfig(
             system_instruction=system,
             temperature=self.temperature,
             seed=self.seed,
             response_mime_type="application/json",
-            response_schema=RESPONSE_SCHEMA,
+            response_schema=schema or RESPONSE_SCHEMA,
             max_output_tokens=self.max_output_tokens,
             automatic_function_calling=self._types.AutomaticFunctionCallingConfig(disable=True),
         )
@@ -144,6 +146,8 @@ class FakeClient:
     broken in one of several ways, in turn, so the fallback path is exercised."""
 
     BROKEN = ["not json", "unknown option", "missing field", "speech without words"]
+    # A night mind's broken answers: each fails one of the checks of reports/days_design.md, §2.6.
+    BROKEN_MIND = ["not json", "unknown id", "number", "time word"]
 
     def __init__(self, invalid_every=5, fail_with=None, max_calls=150):
         self.invalid_every = invalid_every
@@ -156,12 +160,14 @@ class FakeClient:
     def new_scene(self):
         self.scene_base = self.requests
 
-    def generate(self, system, prompt):
+    def generate(self, system, prompt, schema=None):
         if self.requests - self.scene_base >= self.max_calls:
             raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
         self.requests += 1
         if self.requests in self.fail_with:
             raise self.fail_with[self.requests]
+        if schema is not None:
+            return self.mind(prompt)
         block = prompt.split("Your options:")[-1]
         options = re.findall(r"^- (\w+):", block, flags=re.M)
         h = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
@@ -189,6 +195,24 @@ class FakeClient:
                 answer["say"] = None
         return json.dumps(answer)
 
+    def mind(self, prompt):
+        """A night mind's answer: one memory citing an id of the prompt, a feeling and an intent."""
+        ids = re.findall(r"^\[([DN]\d+-\d+)\] ", prompt, flags=re.M)
+        h = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
+        memory = {"ids": [ids[h % len(ids)]] if ids else [], "meaning": f"Fake thought {self.requests}."}
+        if self.invalid_every and self.requests % self.invalid_every == 0:
+            kind = self.BROKEN_MIND[(self.requests // self.invalid_every - 1) % len(self.BROKEN_MIND)]
+            if kind == "not json":
+                return "I would rather not think about it."
+            if kind == "unknown id":
+                memory["ids"] = ["X9-999"]
+            elif kind == "number":
+                memory["meaning"] = "Two portions were eaten."
+            else:
+                memory["meaning"] = "Today was long."
+        return json.dumps({"memories": [memory], "feeling": ["tired", "afraid", "numb"][h % 3],
+                           "intent": f"Fake intent {self.requests}."})
+
 
 class Cache:
     """Every answer ever received, keyed by model, seed and the exact prompt."""
@@ -245,7 +269,9 @@ class Oracle:
     def api_requests(self):
         return self.client.requests if self.client else 0
 
-    def ask(self, system, prompt):
+    def ask(self, system, prompt, schema=None):
+        """schema: passed to the client only when given (a night mind); the cache key does not hold it,
+        since the prompt decides it (reports/days_design.md, §2.5)."""
         key = Cache.key(self.model_name, self.seed, system, prompt)
         cached = self.cache.get(key)
         if cached is not None:
@@ -261,7 +287,8 @@ class Oracle:
                 and self.from_cache - self.base[0] + self.client.requests - self.base[1] >= self.max_calls):
             raise CallCapReached(f"stopped: this morning reached {self.max_calls} model calls "
                                  f"({self.from_cache - self.base[0]} of them answered in an earlier run).")
-        text = self.client.generate(system, prompt)
+        text = (self.client.generate(system, prompt) if schema is None
+                else self.client.generate(system, prompt, schema=schema))
         self.live += 1
         tokens = getattr(self.client, "last_prompt_tokens", None)
         if tokens:
diff --git a/Prototypes/llm-morning/memory.py b/Prototypes/llm-morning/memory.py
new file mode 100644
index 0000000..d1d2300
--- /dev/null
+++ b/Prototypes/llm-morning/memory.py
@@ -0,0 +1,245 @@
+"""What each morning carries of the days before (reports/days_design.md, §3): block A (yesterday's facts, written by
+night.py), block B (last night's thoughts, from the night mind), block C (the earlier days: standing matters and one
+line per person, by a fixed weight table), and the one bound the three share.
+"""
+import data
+from chronicle import gist
+from world import NAMES, day_index, estimate_tokens, when_words
+
+MEMORY_MAX = 560            # estimated tokens of A, B and C together (§3.4)
+B_HEAD = "What yesterday left in you (your own thoughts, last night):"
+C_HEAD = "What stays with you from earlier days:"
+
+# §3.3's table C2, by the line's key: how heavy each kind of event is. The amendment (reports/days_impl.md): every
+# kind act between two people that the rules have, at weight 3. world.py has two: `reassure_<q>` and `sit_<q>`.
+# (`give_<q>` was already in the table at 3; `reassure_all` is to everyone, not between two people.)
+KIND_ACTS = ("reassure", "sit")
+WEIGHT = {"confess": 5, "eat": 4, "went_out": 4, "accuse": 3, "give": 3, "share": 3, "reassure": 3, "sit": 3,
+          "stop": 2, "confront": 2, "accuse_other": 2}
+COUNTED = ("accuse", "accuse_other", "confront", "reassure", "sit")     # repeats are counted, not "again"
+TIMES = {1: "", 2: " twice", 3: " three times"}
+
+
+def times(n):
+    return TIMES.get(n, f" {n} times")
+
+
+def cap(text):
+    return text[0].upper() + text[1:]
+
+
+# ---------- B ----------
+def b_items(result, chron, pid):
+    """(ids, line without "- ") for each kept memory of last night (§3.2)."""
+    out = []
+    for m in (result or {}).get("kept", []):
+        names = [gist(chron.event(i), pid) for i in m["ids"][:2] if chron.event(i)]
+        out.append((list(m["ids"]), f'About {" and ".join(names)}: "{m["meaning"]}"'))
+    return out
+
+
+def block_b(result, chron, pid):
+    """Block B: last night's kept memories, then the intent and the feeling, in their own words (§3.2)."""
+    if not result:
+        return []
+    lines = [f"- {line}" for _, line in b_items(result, chron, pid)]
+    if result.get("intent"):
+        lines.append(f'- You meant to: "{result["intent"]}"')
+    if result.get("feeling"):
+        lines.append(f"- How it left you: {result['feeling']}.")
+    return [B_HEAD] + lines if lines else []
+
+
+# ---------- C ----------
+def scene_key(scene):
+    """(k, 0 for a day, 1 for its night): the order scenes happened in."""
+    return int(scene[1:]), 0 if scene[0] == "D" else 1
+
+
+def scene_when(scene, day):
+    return when_words((scene[0], int(scene[1:])), day)
+
+
+def block_c(chron, pid, day, away=()):
+    """Block C for `pid` on the morning of house day `day` (§3.3): from day `day` - 2 and before, at most two standing
+    matters, then one line for each person, themself included, each with at most one older thought. Each item is
+    {"line", "ids", "weight", "standing", "self", "order", "thought"}."""
+    today = day_index(day)
+    old = [e for e in chron.events
+           if e["scene"][0] in "DN" and scene_key(e["scene"])[0] <= today - 2 and pid in e["witnesses"]]
+    items = []
+    # C1: standing matters.
+    known = chron.knows_culprit(pid)
+    if today >= 3 and known is None and pid != chron.culprit:
+        when = cap(when_words(("D", 1), day))
+        count = next((e for e in chron.events if e["scene"] == "D1" and e["kind"] == "opening"), None)
+        line = (f"{when} you counted the pantry and found one can fewer than you expected. Nobody has admitted taking it."
+                if pid == "elena" else
+                f"{when} Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.")
+        items.append({"line": line, "ids": [count["id"]] if count else [], "weight": 9, "standing": True,
+                      "self": False, "order": -1, "thought": None})
+    for x in data.ORDER:
+        if x in away and x != pid:
+            went = next((e for e in reversed(chron.events) if e["kind"] == "went_out" and x in (e["members"] or [])),
+                        None)
+            when = scene_when(went["scene"], day) if went else "in the night"
+            items.append({"line": f"{NAMES[x]} went out {when} and has not come back.",
+                          "ids": [went["id"]] if went else [], "weight": 6, "standing": True, "self": False,
+                          "order": -1, "thought": None})
+    # C2: people. Each event of the past, as a candidate line for the person it is about.
+    groups = {}                 # (q, key, other) -> events in order
+    for e in old:
+        a, kind, target = e["actor"], e["kind"], e["target"]
+        if a is None:
+            continue
+        movers = e["members"] or [a]
+        if kind == "went_out":
+            for q in movers:
+                if q not in away:
+                    groups.setdefault((q, "went_out", None), []).append(e)
+            continue
+        key = None
+        if kind == "confess":
+            key = ("confess", None)
+        elif kind in ("eat", "eat_given"):
+            key = ("eat", None)
+        elif kind == "accuse" and target:
+            key = ("accuse", target) if (a == pid or target == pid) else ("accuse_other", target)
+        elif kind == "confront" and target and (a == pid or target == pid):
+            key = ("confront", target)
+        elif kind == "give" and target and (a == pid or target == pid):
+            key = ("give", target)
+        elif kind == "share":
+            key = ("share", None)
+        elif kind in KIND_ACTS and target and (a == pid or target == pid):
+            key = (kind, target)
+        elif kind == "stop" and target and (a == pid or target == pid):
+            key = ("stop", target)
+        if key and a not in away:
+            groups.setdefault((a, *key), []).append(e)
+    order = {e["id"]: i for i, e in enumerate(chron.events)}
+    best = {}
+    for (q, key, other), evs in groups.items():
+        cand = (WEIGHT[key], -order[evs[0]["id"]])        # heavier first; at equal weight, the older
+        if q not in best or cand > best[q][0]:
+            best[q] = (cand, key, other, evs)
+    for q in data.ORDER:
+        if q not in best:
+            continue
+        _, key, other, evs = best[q]
+        line = person_line(chron, pid, q, key, other, evs, day)
+        ids = [i for e in evs for i in (e["group"] or [e["id"]])]
+        items.append({"line": line, "ids": list(dict.fromkeys(ids)), "weight": WEIGHT[key], "standing": False,
+                      "self": q == pid, "order": order[evs[0]["id"]], "thought": None})
+    # C3: one older thought per line, the most recent that cites its events.
+    for it in items:
+        ids = set(it["ids"])
+        for k in sorted((k for k in chron.minds if k <= today - 2), reverse=True):
+            mine = (chron.minds[k].get(pid) or {}).get("kept", [])
+            hit = [m for m in mine if ids & set(m["ids"])]
+            if hit:
+                it["thought"] = hit[-1]["meaning"]
+                break
+    return items
+
+
+def person_line(chron, pid, q, key, other, evs, day):
+    first, last = evs[0], evs[-1]
+    when = cap(scene_when(first["scene"], day))
+    again = ""
+    if key not in COUNTED and scene_key(last["scene"]) != scene_key(first["scene"]):
+        again = f", and again {scene_when(last['scene'], day)}"
+    n = len(evs)
+    me = q == pid
+    Q = NAMES[q]
+    T = "you" if other == pid else NAMES.get(other, "")
+    him = data.PRONOUNS[q]["him"]
+    if key == "confess":
+        if me:
+            return f"{when}, you admitted taking the can, in front of everyone{again}."
+        before = [e for e in chron.events if chron.events.index(e) < chron.events.index(first)
+                  and e["actor"] == q and pid in e["witnesses"]]
+        denied = ", after denying it to you" if any(e["kind"] == "deny" for e in before) else ""
+        accused = (", after accusing you of it" if any(e["kind"] == "accuse" and e["target"] == pid for e in before)
+                   else "")
+        return f"{when}, {Q} admitted taking the can{denied}{accused}{again}."
+    if key == "eat":
+        return (f"{when}, you ate a portion in front of the others{again}." if me else
+                f"{when}, {Q} ate a portion in front of you{again}.")
+    if key == "went_out":
+        told = any(e["kind"] == "stop" and e["actor"] == pid and e["target"] == q and e["scene"] == first["scene"]
+                   for e in chron.events) and not me
+        back = next((e for e in chron.events if e["kind"] == "return" and e["scene"] == first["scene"]
+                     and q in (e["members"] or []) and pid in e["witnesses"]), None)
+        street = next((e for e in chron.events if e["kind"] == "street" and e["scene"] == first["scene"]
+                       and q in (e["members"] or [])), None)
+        how = ""
+        if back and street:
+            outcome = street["outcome"] or ""
+            how = (" and came back shaken" if "shaken" in outcome else
+                   " and came back with food" if "with food" in outcome else " and came back with nothing")
+        who = "you" if me else Q
+        return f"{when}, {who} went out to the neighbour's house{f' after you told {him} not to' if told else ''}{how}{again}."
+    if key == "accuse":
+        if me:
+            return f"{when}, you accused {T} of taking the can{times(n)}."
+        innocent = ", and you had not" if pid != chron.culprit else ""
+        return f"{when}, {Q} accused you of taking the can{times(n)}{innocent}."
+    if key == "accuse_other":
+        return f"{when}, {Q} accused {T} of taking the can{times(n)}."
+    if key == "confront":
+        return f"{when}, you confronted {T}{times(n)}." if me else f"{when}, {Q} confronted you{times(n)}."
+    if key == "give":
+        return f"{when}, you gave {T} a portion{again}." if me else f"{when}, {Q} gave you a portion{again}."
+    if key == "share":
+        return f"{when}, you shared out the food{again}." if me else f"{when}, {Q} shared out the food with you{again}."
+    if key == "reassure":
+        return f"{when}, you reassured {T}{times(n)}." if me else f"{when}, {Q} reassured you{times(n)}."
+    if key == "sit":
+        return f"{when}, you sat with {T}{times(n)}." if me else f"{when}, {Q} sat with you{times(n)}."
+    if key == "stop":
+        return (f"{when}, you told {T}, low, not to go{again}." if me else
+                f"{when}, {Q} told you, low, not to go{again}.")
+    raise ValueError(key)
+
+
+# ---------- the bound ----------
+def render_c(items):
+    if not items:
+        return []
+    return [C_HEAD] + [f"- {it['line']}" + (f' You thought then: "{it["thought"]}"' if it.get("thought") else "")
+                       for it in items]
+
+
+def bounded(a_variants, b_lines, c_items, cap=MEMORY_MAX):
+    """A, B and C within `cap` estimated tokens (§3.4), trimmed in this order: A's quoted night words, A's minutes,
+    C's older thoughts (oldest first), C's people lines (lowest weight first; within a weight the oldest, the self
+    line last), B's feeling, then B's intent. Never: C's standing lines, B's memories, A's lines themselves."""
+    ai = 0
+    items = [dict(it) for it in c_items]
+    b = list(b_lines)
+
+    def size():
+        return estimate_tokens("\n".join(render_c(items) + a_variants[ai] + b))
+    while size() > cap:
+        if ai < len(a_variants) - 1:
+            ai += 1
+            continue
+        thoughts = sorted((it for it in items if it.get("thought")), key=lambda it: it["order"])
+        if thoughts:
+            thoughts[0]["thought"] = None
+            continue
+        people = sorted((it for it in items if not it["standing"]), key=lambda it: (it["weight"], it["self"], it["order"]))
+        if people:
+            items.remove(people[0])
+            continue
+        feeling = next((x for x in b if x.startswith("- How it left you:")), None)
+        if feeling:
+            b.remove(feeling)
+            continue
+        intent = next((x for x in b if x.startswith("- You meant to:")), None)
+        if intent:
+            b.remove(intent)
+            continue
+        break
+    return {"A": a_variants[ai], "B": b, "C": render_c(items), "C_items": items}
diff --git a/Prototypes/llm-morning/mind.py b/Prototypes/llm-morning/mind.py
new file mode 100644
index 0000000..cfae391
--- /dev/null
+++ b/Prototypes/llm-morning/mind.py
@@ -0,0 +1,389 @@
+"""The night mind (reports/days_design.md, §2): at the end of each night, one call per person in the house. It is
+given what they did, saw and heard that day and night as numbered records written by the code, and answers with one
+to three lasting memories (each citing record ids), a feeling and an intent for tomorrow. The code checks every
+memory (S1-S9, §2.6-§2.7): one that cites something the person did not perceive, or states as fact something the
+chronicle says is false, never reaches a prompt. The night mind changes no number.
+"""
+import json
+import re
+
+import data
+from talk import SPEECH
+from world import estimate_tokens, trait_words
+
+NIGHT_MIND_SYSTEM = (
+    "You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who "
+    "they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, "
+    "saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things from "
+    "these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one sentence "
+    "of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, forgive or "
+    "doubt, as this person would, but it must not add anything that happened beyond the records: no other event, no "
+    "number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, tomorrow). "
+    "`feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do tomorrow, in one "
+    "sentence, as they would think it. Reply with JSON only: {\"memories\": [{\"ids\": [\"<id>\"], \"meaning\": "
+    "\"<sentence>\"}], \"feeling\": \"<words>\", \"intent\": \"<sentence>\"}")
+EARLIER = "What stays with you from earlier days:"
+RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
+END = "The night is over. What does today leave in you?"
+RECORDS_MAX = 1600          # estimated tokens of records at most (§2.3, R8)
+MEANING_WORDS = 30
+INSIDE_LEFT_OUT = ("About food:", "About the neighbour's house:", "About going there tonight:")
+
+
+def schema(ids):
+    """The response schema of a night mind (§2.5): ids limited to those the prompt shows."""
+    return {"type": "object",
+            "properties": {
+                "memories": {"type": "array", "items": {
+                    "type": "object",
+                    "properties": {"ids": {"type": "array", "items": {"type": "string", "enum": list(ids)}},
+                                   "meaning": {"type": "string"}},
+                    "required": ["ids", "meaning"]}},
+                "feeling": {"type": "string"},
+                "intent": {"type": "string"}},
+            "required": ["memories", "feeling", "intent"]}
+
+
+# ---------- the records (§2.3) ----------
+def records(chron, pid, k):
+    """(id, text) for every event of day k and night k that pid took part in or perceived, in order: R1-R5, folded by
+    R7 (the same speaker and option again), and voices through a wall once per room and minute."""
+    out, folds, voices = [], {}, set()
+    for e in chron.events:
+        if e["scene"] not in (f"D{k}", f"N{k}") or pid not in e["witnesses"]:
+            continue
+        text = e["views"].get(pid)
+        if e["scene"][0] == "N":
+            if text:
+                out.append({"id": e["id"], "text": f"tonight: {text}", "n": 1})
+            continue
+        if e["witnesses"][pid] == "voices":
+            key = (e["minute"], e["room"])
+            if key not in voices:
+                voices.add(key)
+                out.append({"id": e["id"], "text": f"min {e['minute']:02d}: {text}", "n": 1})
+            continue
+        if not text:
+            continue
+        fold = (e["actor"], e["option"]) if e["words"] and e["kind"] in SPEECH else None
+        if fold and fold in folds:
+            r = folds[fold]
+            r["n"] += 1
+            r["to"], r["last"] = e["minute"], e["words"]
+            continue
+        r = {"id": e["id"], "text": f"min {e['minute']:02d}: {text}", "n": 1}
+        out.append(r)
+        if fold:
+            folds[fold] = r
+    return [(r["id"], r["text"] + (f' Then {r["n"] - 1} more time{"s" if r["n"] > 2 else ""}, to min {r["to"]:02d}; '
+                                   f'last: "{r["last"]}"' if r["n"] > 1 else "")) for r in out]
+
+
+QUOTED = re.compile(r'(:\s*|,\s*saying:\s*)"[^"]*"|\s*Then \d+ more times?, to min \d\d; last: "[^"]*"')
+
+
+def without_words(text):
+    """A record without its quoted words, keeping its gist (§2.3, R8)."""
+    text = QUOTED.sub("", text).rstrip()
+    return text if text.endswith((".", "!", "?", ")")) else text + "."
+
+
+def bound_records(recs, limit=RECORDS_MAX):
+    """At most `limit` estimated tokens of records (R8): words go from the oldest records first, reassurances, then
+    trip positions, then the rest; never from the night's or a confession."""
+    recs = list(recs)
+
+    def size():
+        return estimate_tokens("\n".join(f"[{i}] {x}" for i, x in recs))
+    classes = (lambda x: re.search(r"\breassur", x),
+               lambda x: re.search(r"(neighbour's house|should go|stay home|will not go|offers? to go|still means? to go|"
+                                   r"nobody should go)", x),
+               lambda x: True)
+    for in_class in classes:
+        for i, (rid, text) in enumerate(recs):
+            if size() <= limit:
+                return recs
+            if text.startswith("tonight:") or "admitted" in text or '"' not in text or not in_class(text):
+                continue
+            recs[i] = (rid, without_words(text))
+    return recs
+
+
+# ---------- the checks (§2.6, §2.7) ----------
+NUMBERS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "both", "twice", "half"}
+THINGS = {"portion", "portions", "can", "cans", "food", "meal", "meals", "time", "times", "day", "days", "night",
+          "nights", "bite", "bites", "share", "shares"}
+WHEN = re.compile(r"\b(today|tonight|yesterday|tomorrow|this morning|last night|this afternoon|this evening)\b", re.I)
+DENY = re.compile(r"\b(bread|rice|meat|soup|car|truck|gun|knife|phone|radio|police|soldiers?|army|doctor|hospital|store|"
+                  r"shop|market|town|city|money|medicine|garden|basement|cellar|attic|garage)\b", re.I)
+NAME = re.compile(r"\b(Daniel|Elena|Leo|Mara|Mom)\b")
+QUOTE = re.compile(r'"([^"]+)"|“([^”]+)”')
+SUBJECT = {"i": "self", "daniel": "daniel", "elena": "elena", "leo": "leo", "mara": "mara", "mom": "elena",
+           "nobody": None, "noone": None}
+UNRESOLVED = {"he", "she", "they", "we", "you", "it", "everyone", "everybody", "someone", "somebody", "brother",
+              "sister", "son", "daughter", "mother", "father", "family", "people"}
+EXEMPT = {"would", "could", "should", "might", "may", "if", "wish", "want", "wanted", "tried", "meant", "going", "will"}
+NEGATION = {"not", "never", "nothing"}
+FAMILIES = [("eat", [("ate",), ("eaten",), ("eats",), ("eating",)]),
+            ("take", [("took",), ("taken",), ("stole",), ("stolen",)]),
+            ("admit", [("admitted",), ("confessed",), ("owned", "up")]),
+            ("deny", [("denied",)]),
+            ("lie", [("lied",), ("lying",)]),
+            ("accuse", [("accused",), ("blamed",)]),
+            ("go out", [("went", "out"), ("left", "the", "house"), ("went", "next", "door"),
+                        ("went", "to", "the", "neighbour's")]),
+            ("come back", [("came", "back"), ("returned",)]),
+            ("find", [("found",)]),
+            ("give", [("gave",), ("handed",)]),
+            ("share", [("shared",), ("divided",), ("split",)]),
+            ("search", [("searched",)]),
+            ("stop", [("stopped",), ("told", "*", "not", "to", "go"), ("told", "*", "*", "not", "to", "go")]),
+            ("offer", [("offered",), ("volunteered",), ("promised", "to", "go")]),
+            ("hide", [("hid",), ("hidden",), ("hides",), ("stashed",)])]
+
+
+def norm(text):
+    return " ".join(re.findall(r"[a-z0-9']+", (text or "").lower()))
+
+
+def tokens(text):
+    return re.findall(r"[a-z0-9']+", text.lower().replace("no one", "noone"))
+
+
+def verb_at(toks, j):
+    """The family whose words start at toks[j], if any."""
+    for family, patterns in FAMILIES:
+        for pat in patterns:
+            if len(toks) - j >= len(pat) and all(w == "*" or toks[j + i] == w for i, w in enumerate(pat)):
+                return family
+    return None
+
+
+def matching(chron, pid, family, subject, can):
+    """How many events of this family by `subject` (None: anyone) `pid` perceived, on any day."""
+    known = chron.knows_culprit(pid)
+    seen = [e for e in chron.events if pid in e["witnesses"]]
+
+    def by(e):
+        return subject is None or e["actor"] == subject or subject in (e["members"] or [])
+    if family in ("eat", "take"):
+        if can:
+            return 1 if known and (subject is None or subject == known) else 0
+        n = sum(1 for e in seen if e["kind"] in ("eat", "eat_given") and by(e))
+        n += sum(1 for e in seen if e["kind"] == "share" and (subject is None or subject == e["actor"]
+                                                              or e["witnesses"].get(subject) in ("saw", "did")))
+        return n + (1 if known and (subject is None or subject == known) else 0)
+    if family == "lie":
+        return sum(1 for e in seen if e["kind"] == "deny" and by(e) and e["actor"] == known)
+    if family == "find":
+        return sum(1 for e in seen if e["kind"] == "street" and by(e) and e["outcome"]
+                   and "shaken, with nothing" not in e["outcome"] and e["outcome"] != "not back by morning")
+    kinds = {"admit": ("confess",), "deny": ("deny",), "accuse": ("accuse", "confront"), "go out": ("went_out",),
+             "come back": ("return",), "give": ("give",), "share": ("share",), "search": ("search", "search_done"),
+             "stop": ("stop",), "offer": ("volunteer",), "hide": ()}[family]
+    return sum(1 for e in seen if e["kind"] in kinds and by(e))
+
+
+def claims(meaning, pid, chron):
+    """S8 (§2.7): every claim of fact with a named subject, read clause by clause, against what `pid` perceived.
+    A clause with no subject of its own takes the subject of the clause before it. Returns the false claims."""
+    false = []
+    subject, nobody, resolved = None, False, False
+    for clause in re.split(r"[.;,!?]| and | but | because | so | while ", meaning):
+        toks = tokens(clause)
+        if not toks:
+            continue
+        si = -1                                   # -1: the subject of the clause before
+        for i, w in enumerate(toks):
+            if verb_at(toks, i):                  # a subject comes before its verb
+                break
+            if w in SUBJECT:
+                si, resolved, nobody = i, True, SUBJECT[w] is None
+                subject = None if nobody else (pid if SUBJECT[w] == "self" else SUBJECT[w])
+                break
+            if w in UNRESOLVED:                   # he, she, they...: not checked here (M2's reading is)
+                si, resolved = i, False
+                break
+        if not resolved:
+            continue
+        for j in range(si + 1, min(len(toks), si + 5)):
+            family = verb_at(toks, j)
+            if family is None:
+                continue
+            if any(w in EXEMPT or w.endswith("'ll") for w in toks[:j]):
+                break                             # a wish, a plan, a counterfactual: meaning, not a claim
+            negative = nobody or any(w in NEGATION or w.endswith("n't") for w in toks[si + 1:j])
+            n = matching(chron, pid, family, subject, "can" in toks)
+            need = 2 if "again" in toks[j:] else 1
+            who = "nobody" if nobody else subject
+            if negative and n >= 1:
+                false.append(f"{who} {family}: it happened")
+            elif not negative and n < need:
+                false.append(f"{who} {family}: " + ("no such event" if need == 1 else "not twice"))
+            break
+    return false
+
+
+def check_memory(m, pid, shown, chron, carried):
+    """The verdict on one memory: "kept", or "rejected: <check> <why>" (S1-S9)."""
+    ids = m.get("ids") if isinstance(m, dict) else None
+    meaning = m.get("meaning") if isinstance(m, dict) else None
+    if not isinstance(ids, list) or not (1 <= len(ids) <= 3) or not all(isinstance(i, str) for i in ids):
+        return "rejected: S1 ids"
+    if not isinstance(meaning, str) or not meaning.strip():
+        return "rejected: S1 no meaning"
+    if len(meaning.split()) > MEANING_WORDS:
+        return "rejected: S1 too long"
+    if re.search(r"[.!?]", meaning.strip().rstrip('.!?"\'” ')):
+        return "rejected: S1 more than one sentence"
+    for i in ids:
+        e = chron.event(i)
+        if i not in shown or e is None or pid not in e["witnesses"]:
+            return f"rejected: S2 {i}"
+    toks = tokens(meaning)
+    for i, w in enumerate(toks):
+        if (w.isdigit() or w in NUMBERS) and not (w == "one" and i and toks[i - 1] == "no"):
+            if THINGS & set(toks[max(0, i - 3):i + 4]):
+                return f"rejected: S3 {w}"
+    allowed = {pid}
+    for i in ids:
+        e = chron.event(i)
+        allowed |= {e["actor"], e["target"], *(e["members"] or [])}
+    for n in NAME.findall(meaning):
+        who = "elena" if n == "Mom" else n.lower()
+        if who not in allowed:
+            return f"rejected: S4 {n}"
+    w = WHEN.search(meaning)
+    if w:
+        return f"rejected: S5 {w.group(0)}"
+    said = norm(" ".join(shown.values()))
+    for q in QUOTE.findall(meaning):
+        if norm(q[0] or q[1]) not in said:
+            return "rejected: S6 a quotation not in the records"
+    d = DENY.search(meaning)
+    if d:
+        return f"rejected: S7 {d.group(0)}"
+    false = claims(meaning, pid, chron)
+    if false:
+        return "rejected: S8 " + "; ".join(false)
+    if norm(meaning) in {norm(x) for x in carried}:
+        return "rejected: S9 a repeat"
+    return "kept"
+
+
+def check_answer(text, pid, shown, chron, carried=()):
+    """The night mind's answer, checked (§2.6). `shown`: id -> the text the prompt showed for it; `carried`: the
+    meanings they already carry."""
+    r = {"mode": "model", "invalid": None, "memories": [], "kept": [], "feeling": None, "feeling_verdict": None,
+         "intent": None, "intent_verdict": None}
+    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
+    try:
+        ans = json.loads(raw)
+    except ValueError:
+        ans = None
+    if not isinstance(ans, dict) or not ({"memories", "feeling", "intent"} & set(ans)):
+        r.update(mode="fallback", invalid="not JSON" if ans is None else "none of the three fields")
+        return r
+    memories = ans.get("memories") if isinstance(ans.get("memories"), list) else []
+    carried = list(carried)
+    for m in memories[:3]:
+        verdict = check_memory(m, pid, shown, chron, carried)
+        entry = {"ids": m.get("ids") if isinstance(m, dict) else None,
+                 "meaning": m.get("meaning") if isinstance(m, dict) else None, "verdict": verdict}
+        r["memories"].append(entry)
+        if verdict == "kept":
+            r["kept"].append({"ids": list(entry["ids"]), "meaning": " ".join(entry["meaning"].split())})
+            carried.append(entry["meaning"])
+    feeling = ans.get("feeling")
+    if isinstance(feeling, str) and 1 <= len(feeling.split()) <= 3:
+        r["feeling"], r["feeling_verdict"] = " ".join(feeling.split()).lower(), "kept"
+    else:
+        r["feeling_verdict"] = f"rejected: feeling {feeling!r}"
+    intent = ans.get("intent")
+    r["intent_verdict"] = intent_verdict(intent, pid, shown, chron)
+    if r["intent_verdict"] == "kept":
+        r["intent"] = " ".join(intent.split())
+    return r
+
+
+def intent_verdict(intent, pid, shown, chron):
+    if not isinstance(intent, str) or not intent.strip():
+        return "rejected: intent empty"
+    if len(intent.split()) > MEANING_WORDS:
+        return "rejected: intent too long"
+    said = norm(" ".join(shown.values()))
+    for q in QUOTE.findall(intent):
+        if norm(q[0] or q[1]) not in said:
+            return "rejected: S6 a quotation not in the records"
+    d = DENY.search(intent)
+    if d:
+        return f"rejected: S7 {d.group(0)}"
+    false = claims(intent, pid, chron)
+    if false:
+        return "rejected: S8 " + "; ".join(false)
+    return "kept"
+
+
+# ---------- one night ----------
+class NightMind:
+    """The night minds of one night: everyone in the house at dawn, in the family's order (§2.1)."""
+
+    def __init__(self, night, chron, oracle):
+        self.n, self.chron, self.oracle = night, chron, oracle
+        self.k = night.number
+        self.results = {}
+
+    def carried(self, pid):
+        return [m["meaning"] for k in sorted(self.chron.minds) if k < self.k
+                for m in (self.chron.minds[k].get(pid) or {}).get("kept", [])]
+
+    def prompt_for(self, p):
+        """The prompt (§2.4), and id -> the text it shows for that id."""
+        s = p.sheet
+        calls = "; ".join(f"{data.PEOPLE[q]['name']} \"{word}\"" for q, word in data.ADDRESS[p.id].items())
+        head = [f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; Daniel, 25; "
+                f"Leo, 21; Mara, 17).",
+                f"How you address them: {calls}.",
+                f"Who you are: {s['note']}",
+                f"Temperament: {trait_words(s['traits'])}.",
+                f"What matters to you: {', '.join(s['values'])}."]
+        head += [x for x in self.n.m.inside_lines(p) if not x.startswith(INSIDE_LEFT_OUT)]
+        shown = {}
+        earlier = (getattr(self.n.prev, "blocks", {}).get(p.id) or {}).get("earlier") or []
+        if earlier:
+            lines = [EARLIER]
+            for ids, text in earlier:
+                lines.append(f"- [{', '.join(ids)}] {text}")
+                for i in ids:
+                    shown.setdefault(i, text)
+        else:
+            lines = [EARLIER + " nothing yet."]
+        recs = bound_records(records(self.chron, p.id, self.k))
+        for i, text in recs:
+            shown.setdefault(i, text)
+        prompt = "\n".join(head + lines + [RECORDS] + [f"[{i}] {text}" for i, text in recs] + [END])
+        return prompt, shown
+
+    def run(self):
+        for pid in data.ORDER:
+            if pid in self.n.away:
+                continue
+            p = self.n.people[pid]
+            prompt, shown = self.prompt_for(p)
+            text = self.oracle.ask(NIGHT_MIND_SYSTEM, prompt, schema=schema(list(shown)))
+            r = check_answer(text, pid, shown, self.chron, self.carried(pid))
+            r.update(prompt_tokens=estimate_tokens(NIGHT_MIND_SYSTEM + prompt), answer=text)
+            self.results[pid] = r
+        self.chron.minds[self.k] = self.results
+        return self
+
+    def transcript(self):
+        keep = ("mode", "invalid", "prompt_tokens", "memories", "feeling", "feeling_verdict", "intent",
+                "intent_verdict", "answer")
+        return {pid: {k: r[k] for k in keep} for pid, r in self.results.items()}
+
+    def counts(self):
+        mems = [m for r in self.results.values() for m in r["memories"]]
+        kept = sum(m["verdict"] == "kept" for m in mems)
+        return {"memories_proposed": len(mems), "memories_kept": kept, "memories_rejected": len(mems) - kept,
+                "max_prompt_tokens_estimated": max((r["prompt_tokens"] for r in self.results.values()), default=None)}
diff --git a/Prototypes/llm-morning/morning.py b/Prototypes/llm-morning/morning.py
index aa3aa92..95e8d89 100644
--- a/Prototypes/llm-morning/morning.py
+++ b/Prototypes/llm-morning/morning.py
@@ -1,5 +1,5 @@
-"""Runs a morning, the night after it and the next morning, with rules plus a language model, and
-writes them as one story (reports/night_design.md).
+"""Runs a morning, the night after it, the next morning, a second night and a third morning, with rules plus a
+language model, and writes them as one story (reports/night_design.md; reports/days_design.md).
 
     python morning.py --seed 1              a fresh run; answers not in the cache are asked of Gemini
     python morning.py --seed 1 --replay     the same run from the cache only, with no API calls;
@@ -13,9 +13,9 @@ writes them as one story (reports/night_design.md).
                       the fourth version's runs; v5/check.py to v14/check.py replay the
                       fifth's to fourteenth's)
 
-Day 1 is the morning of the count; then the night; then day 2. The model names and call limits
-are in config.json; the call limit counts each of the three apart. The key is read from
-GEMINI_API_KEY.
+Day 1 is the morning of the count; then the night, the night mind, day 2, the second night, its night
+mind and day 3. The model names and call limits are in config.json; the call limit counts each scene
+apart. The key is read from GEMINI_API_KEY.
 
 Exit codes: 0 done (and, for --replay, identical); 1 replay differs; 3 stopped cleanly part way
 (quota, rate limit, call cap, or a replay cache miss): see the message.
@@ -29,8 +29,10 @@ import time
 
 import data
 from gemini import Cache, FakeClient, GeminiClient, Oracle, StopMorning, load_config
+from chronicle import Chronicle
+from mind import NightMind
 from night import Night
-from story import render, render_day2, render_night
+from story import render, render_day2, render_mind, render_night
 from world import Morning
 
 HERE = os.path.dirname(os.path.abspath(__file__))
@@ -119,24 +121,52 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         m.finish()
 
     scenes = {}
+
+    def scene(name, step):
+        """One scene, counted on its own against the call cap (reports/night_design.md, §8)."""
+        if scenes:
+            oracle.new_scene()
+        scenes[name] = Scene(oracle)
+        out = step()
+        scenes[name].close()
+        return out
+
+    def night_of(day, number):
+        n = Night(day, oracle, number=number, house=chron.house_state()).run()
+        say(f"  night {number}: model asked for {len(n.decisions)}; so far {oracle.live} live, "
+            f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
+        chron.add_night(n)
+        return n
+
+    def mind_of(n):
+        mind = NightMind(n, chron, oracle).run()
+        say(f"  night {n.number}, the night mind: model asked for {len(mind.results)}; so far {oracle.live} live, "
+            f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
+        return mind
+
+    def day_after(day, n, tag):
+        m = Morning.next_day(day, n, oracle, chronicle=chron)
+        morning_turns(m, tag)
+        chron.add_day(m)
+        return m
+    # Days that follow one another (reports/days_design.md, §1): day 1, night 1 and its night mind, day 2, night 2
+    # and its night mind, day 3; and the chronicle of all of it.
+    chron = Chronicle(seed, data.culprit(scenario))
     try:
-        scenes["day1"] = Scene(oracle)
-        morning = Morning(oracle, seed, scenario)
-        morning_turns(morning, "")
+        def day_one():
+            m = Morning(oracle, seed, scenario)
+            morning_turns(m, "")
+            chron.add_day(m)
+            return m
+        morning = scene("day1", day_one)
         # Day 1's story is written as it ended, before the night touches anything.
         day1_text = render(morning, seed, model_name, command)
-        scenes["day1"].close()
-        oracle.new_scene()
-        scenes["night"] = Scene(oracle)
-        night = Night(morning, oracle).run()
-        scenes["night"].close()
-        say(f"  night: model asked for {len(night.decisions)}; so far {oracle.live} live, "
-            f"{oracle.from_cache} cached, {oracle.api_requests} API requests")
-        oracle.new_scene()
-        scenes["day2"] = Scene(oracle)
-        day2 = Morning.next_day(morning, night, oracle)
-        morning_turns(day2, "day 2 ")
-        scenes["day2"].close()
+        night = scene("night", lambda: night_of(morning, 1))
+        mind1 = scene("mind1", lambda: mind_of(night))
+        day2 = scene("day2", lambda: day_after(morning, night, "day 2 "))
+        night2 = scene("night2", lambda: night_of(day2, 2))
+        mind2 = scene("mind2", lambda: mind_of(night2))
+        day3 = scene("day3", lambda: day_after(day2, night2, "day 3 "))
     except StopMorning as stop:
         say(f"\n{stop}")
         say(f"Answers received so far ({len(cache.entries)}) are kept in {os.path.relpath(cache_path, HERE)}.")
@@ -147,13 +177,18 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         return {"stopped": str(stop), "api_requests": oracle.api_requests}, 3
     seconds = time.monotonic() - started
 
-    text = day1_text + render_night(night) + render_day2(day2)
+    text = (day1_text + render_night(night) + render_mind(mind1) + render_day2(day2)
+            + render_night(night2) + render_mind(mind2) + render_day2(day3))
     story_path = os.path.join(runs_dir, f"{name}.md")
     out_path = os.path.join(runs_dir, f"{name}.replay.md") if replay else story_path
     with open(out_path, "w", encoding="utf-8", newline="\n") as f:
         f.write(text)
     night_counts = scenes["night"].counts()
     day2_counts = scenes["day2"].counts()
+    later = {k: scenes[k].counts() for k in ("mind1", "night2", "mind2", "day3")}
+
+    def asks(k):
+        return later[k]["answers_live"] + later[k]["answers_from_cache"]
     meta = {
         "model": model_name, "scenario": scenario, "seed": seed, "replay": replay,
         "api_requests": oracle.api_requests, "answers_live": oracle.live,
@@ -171,8 +206,24 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         "day2": {**day_meta(day2, scenes["day2"]),
                  "food_moments": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("food_moment")),
                  "give_answers": sum(1 for rec in day2.log for d in rec["decisions"] if d.get("given_by"))},
+        # Days that follow one another (reports/days_design.md, §2.8, §7.1 N-T13).
+        "night1_asks": night_counts["answers_live"] + night_counts["answers_from_cache"],
+        "mind1_asks": asks("mind1"), "mind1_api_requests": later["mind1"]["api_requests"],
+        "mind1": {**later["mind1"], **mind1.counts()},
+        "night2_asks": asks("night2"), "night2_api_requests": later["night2"]["api_requests"],
+        "leavers2": night2.leavers, "outcome2": [g["outcome"] for g in night2.groups],
+        "night2": {**later["night2"], "house_left": night2.house_left,
+                   "away": [q for q in data.ORDER if q in night2.away],
+                   "max_prompt_tokens_estimated": night2.m.max_prompt_tokens},
+        "mind2_asks": asks("mind2"), "mind2_api_requests": later["mind2"]["api_requests"],
+        "mind2": {**later["mind2"], **mind2.counts()},
+        "day3_asks": asks("day3"), "day3_api_requests": later["day3"]["api_requests"],
+        "day3": {**day_meta(day3, scenes["day3"]),
+                 "food_moments": sum(1 for rec in day3.log for d in rec["decisions"] if d.get("food_moment")),
+                 "give_answers": sum(1 for rec in day3.log for d in rec["decisions"] if d.get("given_by"))},
         "max_prompt_tokens_estimated": max(morning.max_prompt_tokens, night.m.max_prompt_tokens,
-                                           day2.max_prompt_tokens),
+                                           day2.max_prompt_tokens, night2.m.max_prompt_tokens,
+                                           day3.max_prompt_tokens),
         "max_prompt_tokens_counted_by_api": max(oracle.prompt_tokens, default=None),
         "run_seconds": round(seconds, 1),
         "story": os.path.relpath(out_path, HERE).replace("\\", "/"),
@@ -188,7 +239,16 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
     say(f"  night house: {night.house}; away: {meta['night']['away']}")
     for k in DAY_KEYS + ("food_moments", "give_answers"):
         say(f"  day2 {k}: {meta['day2'][k]}")
-    for k in ("day2_asks", "day2_api_requests", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api",
+    for k in ("day2_asks", "day2_api_requests"):
+        say(f"  {k}: {meta[k]}")
+    for k in ("night1_asks", "mind1_asks", "mind1_api_requests", "night2_asks", "night2_api_requests", "leavers2",
+              "outcome2", "mind2_asks", "mind2_api_requests"):
+        say(f"  {k}: {meta[k]}")
+    for k in ("memories_proposed", "memories_kept", "memories_rejected"):
+        say(f"  mind1 {k}: {meta['mind1'][k]}; mind2 {k}: {meta['mind2'][k]}")
+    for k in DAY_KEYS + ("food_moments", "give_answers"):
+        say(f"  day3 {k}: {meta['day3'][k]}")
+    for k in ("day3_asks", "day3_api_requests", "max_prompt_tokens_estimated", "max_prompt_tokens_counted_by_api",
               "run_seconds", "story_sha256"):
         say(f"  {k}: {meta[k]}")
     if replay:
@@ -201,7 +261,9 @@ def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_d
         say(f"  byte for byte against {os.path.relpath(story_path, HERE)}: "
             f"{'IDENTICAL' if same else 'DIFFERS'}")
         return meta, 0 if same else 1
-    transcript = {"day1": morning.transcript, "night": night.transcript(), "day2": day2.transcript}
+    transcript = {"day1": morning.transcript, "night": night.transcript(), "mind1": mind1.transcript(),
+                  "day2": day2.transcript, "night2": night2.transcript(), "mind2": mind2.transcript(),
+                  "day3": day3.transcript, "chronicle": chron.to_json()}
     with open(os.path.join(runs_dir, f"{name}.transcript.json"), "w", encoding="utf-8", newline="\n") as f:
         json.dump(transcript, f, ensure_ascii=False, indent=1)
         f.write("\n")
diff --git a/Prototypes/llm-morning/night.py b/Prototypes/llm-morning/night.py
index e01ec4a..c79813f 100644
--- a/Prototypes/llm-morning/night.py
+++ b/Prototypes/llm-morning/night.py
@@ -9,14 +9,22 @@ whoever crosses it. Nothing in the night is asked of the model but those decisio
 
 `next_day` then hands day 2 each person as the night left them, with what they carry in: a block
 of facts and conclusions the code writes from what they did, saw or heard.
+
+Days that follow one another (reports/days_design.md): a night can be the second (`number`), finds the
+neighbour's house as the last night left it, keeps whoever is away out of it, and records each thing that
+happened as an event for the chronicle (chronicle.py), with each night line tied to the event it tells of.
+`next_day` sets up day 3 the same way, and, given the chronicle, adds last night's thoughts (B) and the earlier
+days (C) to what each person carries in (memory.py).
 """
 import copy
 import json
 import random
+import re
 
 import data
 import world
-from world import NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, estimate_tokens, portions_text
+from world import (NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, day_index, estimate_tokens,
+                   portions_text, when_words)
 
 GAP_HUNGER = 0.3            # × hunger_rate, the afternoon and evening (§2)
 NIGHT_HUNGER = 0.1          # × hunger_rate, the night
@@ -33,6 +41,7 @@ BEDS = ", ".join(" and ".join(NAMES[x] for x in data.ORDER if x in owners) + f"
                  for room, owners in sorted(data.OWNERS.items(),
                                             key=lambda kv: min(data.ORDER.index(x) for x in kv[1])))
 TRIGGER = "the family is together in the kitchen for the first time since last night"
+CARRY_VARIANTS = ((False, True), (True, True), (True, False))     # (short, minutes), in the order they are tried
 
 BEDTIME = [("sleep", "go to sleep"),
            ("lie_awake", "lie awake in your bed and listen"),
@@ -105,10 +114,14 @@ def names(pids):
 
 class Night:
     """One night. `draws` forces named draws (tests): "order" (a list of leavers), "house",
-    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed."""
-
-    def __init__(self, day1, oracle, draws=None):
-        self.day1 = day1
+    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed.
+    number: which night this is (reports/days_design.md, §1.3); house: the neighbour's house as the night
+    before left it ({"value", "u", "left", "entered"}), so it is never drawn again."""
+
+    def __init__(self, day1, oracle, draws=None, number=1, house=None):
+        self.day1 = self.prev = day1            # the day this night follows
+        self.number = number
+        self.house_given = house
         self.oracle = oracle
         self.seed = day1.seed
         self.draws = dict(draws or {})
@@ -123,7 +136,10 @@ class Night:
         self.noticing = []          # every check of who notices whom, in order
         self.story = []             # ("decision", d) | ("noticing", n) | ("text", line), in order
         self.groups = []
-        self.away = set()
+        self.away = set(day1.away)  # whoever did not come back from an earlier night is not in the house
+        self.entered = bool(house and house.get("entered"))
+        self.events = []            # what happened, for the chronicle: dicts with "key", in order
+        self.line_events = {p: [] for p in data.ORDER}    # the event each night line tells of
         self.leavers = []           # everyone who went out, in order
         self.lines = {p: [] for p in data.ORDER}          # night lines for the carry-in, with words
         self.lines_short = {p: [] for p in data.ORDER}    # the same without quoted words
@@ -134,23 +150,41 @@ class Night:
         self.morning_hunger = {}
 
     # ---------- chance ----------
+    def draw_string(self, name):
+        """The seed string of a draw (reports/days_design.md, §4.4): the first night keeps night_design's;
+        a later night has its own; the neighbour's house is one fact, whatever the night."""
+        if self.number == 1 or name == "house":
+            return f"{self.seed}:night:{name}"
+        return f"{self.seed}:night{self.number}:{name}"
+
     def u(self, name):
         if name in self.draws:
             return self.draws[name]
-        return random.Random(f"{self.seed}:night:{name}").random()
+        return random.Random(self.draw_string(name)).random()
+
+    def house_state(self):
+        """The neighbour's house as this night leaves it, for the next night (reports/days_design.md, §4.3)."""
+        return {"value": self.house, "u": self.house_u, "left": self.house_left, "entered": self.entered}
 
     def order(self):
         """Everyone, in the order they would leave: lowest draw first."""
         if "order" in self.draws:
             return list(self.draws["order"])
-        rng = random.Random(f"{self.seed}:night:order")
+        rng = random.Random(self.draw_string("order"))
         draw = {q: rng.random() for q in data.ORDER}
         return sorted(data.ORDER, key=draw.get)
 
     # ---------- lines ----------
-    def line(self, pid, full, short=None):
+    def line(self, pid, full, short=None, event=None):
         self.lines[pid].append(full)
         self.lines_short[pid].append(full if short is None else short)
+        self.line_events[pid].append(event)
+
+    def event(self, kind, actor=None, witnesses=None, **more):
+        """Something that happened tonight, for the chronicle; returns its key."""
+        self.events.append({"key": len(self.events), "kind": kind, "actor": actor, "witnesses": dict(witnesses or {}),
+                            **more})
+        return len(self.events) - 1
 
     def text(self, line):
         self.story.append(("text", line))
@@ -188,20 +222,31 @@ class Night:
     # ---------- the night ----------
     def run(self):
         for p in self.people.values():                                  # the gap (§2)
+            if p.id in self.away:
+                p.room = None
+                continue
             p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
             p.room = OWN_ROOM[p.id]
             p.activity = {"kind": "idle", "label": "in bed"}
-        self.bedtime_hunger = {q: self.people[q].hunger for q in data.ORDER}
+        self.bedtime_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
         self.rooms_at_bedtime = {q: self.people[q].room for q in data.ORDER}
         self.state_at_bedtime = {
             q: [json.dumps({t: [g.strength, g.events] for t, g in p.grudges.items()}), p.suspicion.state(), p.guilt]
             for q, p in self.people.items()}
-        for q in data.ORDER:                                            # bedtime (§3.2)
+        present = [q for q in data.ORDER if q not in self.away]
+        beds = BEDS if not self.away else ", ".join(
+            " and ".join(NAMES[x] for x in present if x in owners) + f" in the {data.ROOMS[room]}"
+            for room, owners in sorted(data.OWNERS.items(), key=lambda kv: min(data.ORDER.index(x) for x in kv[1]))
+            if any(x in present for x in owners))
+        for q in present:                                               # bedtime (§3.2)
             room = OWN_ROOM[q]
             r = ROOMMATE[q]
+            mate = (f"{NAMES[r]}'s bed is empty." if r in self.away else
+                    f"{NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.")
             now = ["Now it is night. " + data.GAP,
-                   f"Everyone has gone to bed in their own room: {BEDS}.",
-                   f"You are in the {data.ROOMS[room]}, in your bed. {NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.",
+                   (f"Everyone has gone to bed in their own room: {beds}." if not self.away else
+                    f"Everyone in the house has gone to bed in their own room: {beds}."),
+                   f"You are in the {data.ROOMS[room]}, in your bed. {mate}",
                    f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]
             own = self.people[q].trip_heard.get(q)
             if own and own[1] == "volunteer":           # `volunteer`, or day 2's `still_going`
@@ -212,10 +257,15 @@ class Night:
             self.where[q] = "kitchen" if choice == "watch_door" else room
             self.awake[q] = choice != "sleep"
             self.people[q].tonight.append(TONIGHT[choice])
-            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}")
-        self.house_u = self.u("house")
-        self.house = self.house_left = house_portions(self.house_u)
-        pending = [q for q in self.order() if self.choices[q] == "go_next_door"]
+            e = self.event("bedtime", q, {q: "did"}, option=choice)
+            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}", event=e)
+        if self.house_given:                # fixed the night it first mattered, and as that night left it (§4.3)
+            self.house, self.house_u = self.house_given["value"], self.house_given["u"]
+            self.house_left = self.house_given["left"]
+        else:
+            self.house_u = self.u("house")
+            self.house = self.house_left = house_portions(self.house_u)
+        pending = [q for q in self.order() if self.choices.get(q) == "go_next_door"]
         while pending:
             self.leave(pending.pop(0), pending)
         for p in self.people.values():                                  # the rest of the night
@@ -225,6 +275,11 @@ class Night:
             p.hunger = min(1.0, p.hunger + NIGHT_HUNGER * p.sheet["hunger_rate"])
             p.room = OWN_ROOM[p.id]
         self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
+        for e in self.events:               # who knew that someone went out (§4.2)
+            if e["kind"] == "went_out":
+                for P in data.ORDER:
+                    if P not in e["members"] and any(x in self.knows[P] for x in e["members"]):
+                        e["witnesses"].setdefault(P, "knew")
         return self
 
     def leave(self, L, pending):
@@ -263,8 +318,9 @@ class Night:
                 self.awake[R] = True
                 seen_by.add(R)
                 self.knows[R].append(L)
+                e = self.event("got_up", L, {L: "did", R: "saw"})
                 self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
-                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).")
+                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).", event=e)
                 if R not in self.reacted:
                     self.reacted.add(R)
                     now = [f"Now it is night, in the {data.ROOMS[room]}. "
@@ -277,6 +333,7 @@ class Night:
                         return
         # 2. L passes through the kitchen: whoever sits up by the front door.
         stops = []
+        at_door = None
         for S in data.ORDER:
             if self.where.get(S) != "kitchen" or S in group:
                 continue
@@ -284,7 +341,11 @@ class Night:
             seen_by.add(S)
             self.knows[S] += [x for x in group if x not in self.knows[S]]
             who = names(group)
-            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).")
+            if at_door is None:
+                at_door = self.event("at_door", L, {x: "did" for x in group}, members=list(group))
+            self.events[at_door]["witnesses"][S] = "saw"
+            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).",
+                      event=at_door)
             if S not in self.reacted:
                 self.reacted.add(S)
                 now = ["Now it is night. You are sitting up in the kitchen by the front door.",
@@ -297,6 +358,7 @@ class Night:
             back_to_bed()
             return
         # 3. The front door opens: everyone in a bedroom who has not seen L go.
+        door = None
         for P in data.ORDER:
             if self.where.get(P) not in BEDROOMS or P in group or P in seen_by:
                 continue
@@ -311,8 +373,11 @@ class Night:
             if not heard:
                 continue
             self.awake[P] = True
+            if door is None:
+                door = self.event("door", L, {x: "did" for x in group}, members=list(group))
+            self.events[door]["witnesses"][P] = "heard"
             self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
-                         f"You did not see who.")
+                         f"You did not see who.", event=door)
             if P in self.reacted:
                 continue
             self.reacted.add(P)
@@ -324,6 +389,7 @@ class Night:
         for P in group:
             self.where[P] = "out"
         self.leavers += group
+        self.event("went_out", L, {x: "did" for x in group}, members=list(group))
         self.trip(L, group)
 
     def react_seen(self, P, L, now, pending, join):
@@ -342,20 +408,21 @@ class Night:
             fallback = f"let_{L}_go"
         waiting = P in pending
         choice, words = self.ask(P, "reaction", now, opts, fallback)
+        e = None if choice == f"stop_{L}" else self.event("reaction", P, {P: "did"}, option=choice, target=L)
         if choice == f"go_with_{L}":
             join(P)
-            self.line(P, f"You went with {him(L)}.")
+            self.line(P, f"You went with {him(L)}.", event=e)
             self.people[P].tonight.append(f"you went with {n}.")
         elif choice == f"stop_{L}":
             self.people[P].tonight.append(f"you told {n} not to go.")
             return P, words
         elif choice == "stay_home":
             pending.remove(P)
-            self.line(P, f"You let {him(L)} go, and stayed in bed after all.")
+            self.line(P, f"You let {him(L)} go, and stayed in bed after all.", event=e)
         elif waiting:
-            self.line(P, f"You let {him(L)} go, to go yourself later.")
+            self.line(P, f"You let {him(L)} go, to go yourself later.", event=e)
         else:
-            self.line(P, f"You let {him(L)} go without a word.")
+            self.line(P, f"You let {him(L)} go without a word.", event=e)
             self.people[P].tonight.append(f"you let {n} go.")
         return None
 
@@ -366,18 +433,20 @@ class Night:
                     Option("go_later", "wait, then go yourself later, alone"),
                     Option("stay_home", "stay in bed after all")]
             choice, _ = self.ask(P, "reaction", now, opts, "go_later")
+            e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
             if choice == "go_after":
                 join(P)
-                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.")
+                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.", event=e)
             elif choice == "stay_home":
                 pending.remove(P)
-                self.line(P, "You stayed in bed after all.")
+                self.line(P, "You stayed in bed after all.", event=e)
             else:
-                self.line(P, "You waited, to go yourself later.")
+                self.line(P, "You waited, to go yourself later.", event=e)
             return
         opts = [Option("stay_in_bed", "stay in bed"),
                 Option("get_up_and_look", "get up, see whose bed is empty, and wait up by the front door until morning")]
         choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
+        e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
         if choice == "get_up_and_look":
             gone = [x for x in group]
             beds = (f"{NAMES[gone[0]]}'s bed was empty" if len(gone) == 1 else
@@ -387,7 +456,7 @@ class Night:
             self.where[P] = "kitchen"
             self.knows[P] += [x for x in gone if x not in self.knows[P]]
         else:
-            self.line(P, "You stayed in bed.")
+            self.line(P, "You stayed in bed.", event=e)
 
     def answer(self, L, stops, place, group):
         """L, told not to go, answers once. Returns True if L goes all the same."""
@@ -402,22 +471,28 @@ class Night:
         choice, a = self.ask(L, "answer", now, opts, "go_anyway")
         goes = choice == "go_anyway"
         went = "went all the same" if goes else "went back to bed"
+        stop_events = [self.event("stop", S, {S: "did", L: "heard"}, option=f"stop_{L}", target=L, words=w)
+                       for S, w in stops]
+        self.event("answer", L, {L: "did", **{S: "heard" for S, _ in stops}}, option=choice, words=a,
+                   target=stops[0][0])
         said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
         told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
                         for S, w in stops)
-        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.")
+        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.",
+                  event=stop_events[0])
         He = he(L).capitalize()
-        for S, w in stops:
+        for (S, w), e in zip(stops, stop_events):
             told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
             answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
-            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.")
+            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.", event=e)
         # Low voices: heard, without words, by anyone awake elsewhere; nobody wakes for a whisper.
         talkers = {L} | {S for S, _ in stops} | set(group)
         for P in data.ORDER:
             w = self.where.get(P)
             if P in talkers or w in (None, "out", place) or not self.awake[P]:
                 continue
-            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.")
+            self.events[stop_events[0]]["witnesses"][P] = "voices"
+            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.", event=stop_events[0])
         if not goes:
             self.people[L].tonight.append("you went back to bed.")
         return goes
@@ -445,28 +520,33 @@ class Night:
             self.away.add(g["lost"])
         g["outcome"] = outcome_class(st, found)
         self.groups.append(g)
+        if st in ("clean", "scare_back"):
+            self.entered = True
+        street_e = self.event("street", L, {x: "did" for x in group}, members=list(group), outcome=g["outcome"])
         back = [x for x in group if x != g["lost"]]
+        return_e = self.event("return", L, {x: "did" for x in back}, members=list(back)) if back else None
         k, F = g["took"], g["found"]
         for P in back:
             if st == "clean" and F:
                 rest = F - k
                 took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
                 self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
-                             f"Nothing troubled you in the street.")
+                             f"Nothing troubled you in the street.", event=street_e)
             elif st == "clean":
                 self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
-                             "the street.")
+                             "the street.", event=street_e)
             elif st == "scare_there":
-                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.")
+                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.",
+                          event=street_e)
             elif st == "scare_back":
                 got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
                 self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
-                             f"street, and you ran the rest of the way.")
+                             f"street, and you ran the rest of the way.", event=street_e)
             else:
                 self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
-                             f"and came back without {him(g['lost'])}.")
+                             f"and came back without {him(g['lost'])}.", event=street_e)
             self.line(P, "You came back in by the front door before dawn"
-                      + (f" and put the {portions_text(k)} on the shelf." if k else "."))
+                      + (f" and put the {portions_text(k)} on the shelf." if k else "."), event=return_e)
             self.visit[P] = {"got_in": st in ("clean", "scare_back"), "found": F, "took": k}
         if not back:
             return
@@ -485,18 +565,22 @@ class Night:
             if w == "kitchen":
                 self.notice(P, L, "return")
                 self.knows[P] += [x for x in back if x not in self.knows[P]]
+                self.events[return_e]["witnesses"][P] = "saw"
                 self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
-                             f"(you saw it).")
+                             f"(you saw it).", event=return_e)
             elif self.awake[P]:
                 self.notice(P, L, "return")
-                self.line(P, "Before dawn you heard the front door again. You did not see who.")
+                self.events[return_e]["witnesses"][P] = "heard"
+                self.line(P, "Before dawn you heard the front door again. You did not see who.", event=return_e)
             else:
                 draw = self.u(f"return:{L}:{P}")
                 woke = draw < wake_door(P)
                 self.notice(P, L, "return", draw, wake_door(P), woke)
                 if woke:
                     self.awake[P] = True
-                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.")
+                    self.events[return_e]["witnesses"][P] = "heard"
+                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.",
+                              event=return_e)
 
     # ---------- the record ----------
     def transcript(self):
@@ -506,7 +590,10 @@ class Night:
                 "choices": self.choices, "leavers": self.leavers, "away": [q for q in data.ORDER if q in self.away],
                 "decisions": [{k: v for k, v in d.items()} for d in self.decisions],
                 "noticing": self.noticing, "groups": self.groups,
-                "lines": self.lines}
+                "lines": self.lines,
+                # Days that follow one another (reports/days_design.md, §4.2): which night, what happened, and the
+                # event each night line tells of.
+                "number": self.number, "events": self.events, "line_events": self.line_events}
 
 
 # ---------- day 2 ----------
@@ -570,67 +657,188 @@ def carry_in(day1, n, p, short=False, minutes=True):
 
 def bounded_carry_in(day1, n, p):
     """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
-    for short, minutes in ((False, True), (True, True), (True, False)):
-        block = carry_in(day1, n, p, short, minutes)
-        if estimate_tokens("\n".join(block)) <= CARRY_IN_MAX:
-            break
-    return block
+    return carry_variants(day1, n, p)[0]
+
+
+def carry_variants(prev, n, p):
+    """Block A as it can be trimmed (reports/days_design.md, §3.4): from the first form within CARRY_IN_MAX, then
+    the shorter ones. Day 2's is night_design's carry-in; a later day's is carry_in_later."""
+    make = carry_in if prev.day == 4 else carry_in_later
+    blocks = [make(prev, n, p, short, minutes) for short, minutes in CARRY_VARIANTS]
+    first = next((i for i, b in enumerate(blocks) if estimate_tokens("\n".join(b)) <= CARRY_IN_MAX), 2)
+    blocks = blocks[first:]
+    return blocks + [blocks[-1]] * (3 - len(blocks))
+
+
+def carry_in_later(prev, n, p, short=False, minutes=True):
+    """Block A from day 3 on (reports/days_design.md, §3.2, lines Y1-Y8): yesterday's facts as p had them, then
+    their own night. `prev` is yesterday's Morning, as it ended."""
+    out = [f"Yesterday morning the shelf held {portions_text(prev.start_portions)}."]
+    if p.confessed and p.confessed_day == prev.day:                               # Y2
+        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
+        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
+        out.append(f"You admitted at minute {sure[4:6]} that you took the can"
+                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
+    elif p.knows_culprit and p.knows_culprit != p.id and p.confession_heard_day == prev.day:
+        sure = next(x for x in p.sure if " admitted taking the can: " in x)
+        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
+        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
+        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at minute {p.confession_heard_at:02d}{after}: "
+                   f"{words} (you heard it).")
+    for label, prefix, verb in (("Accusations", "accuse_", "accused"), ("Confrontations", "confront_", "confronted")):
+        acts = {}                                                                 # Y3, Y4
+        for turn in prev.transcript["turns"]:
+            for a in turn["acts"]:
+                if a["option"].startswith(prefix) and (a["who"] == p.id or p.id in a["audience"]):
+                    acts.setdefault((a["who"], a["option"][len(prefix):]), []).append(turn["minute"])
+        if acts:
+            parts = []
+            for (a, tgt), ms in acts.items():
+                times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
+                when = f" (min {', '.join(f'{x:02d}' for x in ms)})" if minutes else ""
+                parts.append(f"{'you' if a == p.id else NAMES[a]} {verb} {'you' if tgt == p.id else NAMES[tgt]}{times}{when}")
+            out.append(f"{label}: " + "; ".join(parts) + ".")
+    for x in p.sure:                                                              # Y5
+        if x[8:].startswith("you finished searching the "):
+            out.append(f"You searched the {x[8 + len('you finished searching the '):].split(':')[0]} at minute "
+                       f"{x[4:6]} and found nothing.")
+    ate = {}                                                                      # Y6
+    for x in p.sure:
+        if " ate one of the portions" in x:
+            mm, rest = x[4:6], x[8:]
+            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
+    for mm, who in ate.items():
+        mine = "you" in who
+        who = (["You"] if mine else []) + [w for w in who if w != "you"]
+        each = " each" if len(who) > 1 else ""
+        out.append(f"{' and '.join(who)} ate a portion{each} at minute {mm}" + ("." if mine else " (you saw it)."))
+    for x in p.sure:
+        mm, rest = x[4:6], x[8:]
+        g = re.match(r"^(\w+) gave one of the portions to (\w+), and \w+ (ate it|put it back on the shelf)", rest)
+        if g:
+            giver = "You" if g.group(1) == "you" else g.group(1)
+            done = "ate it" if g.group(3) == "ate it" else "put it back"
+            out.append(f"{giver} gave {g.group(2)} a portion at minute {mm}, and {g.group(2)} {done}"
+                       + ("." if giver == "You" else " (you saw it)."))
+            continue
+        g = re.match(r"^(\w+) gave you one of the portions, and you (ate it|put it back on the shelf)", rest)
+        if g:
+            done = "ate it" if g.group(2) == "ate it" else "put it back"
+            out.append(f"{g.group(1)} gave you a portion at minute {mm}, and you {done}.")
+            continue
+        if rest.startswith("you shared out the last "):
+            out.append(f"You shared out the food at minute {mm}.")
+        elif " shares out the last " in rest and rest.endswith("you had your part."):
+            out.append(f"{rest.split(' shares out the last ')[0]} shared out the food at minute {mm}; you had your part.")
+    plan = prev.heard_plan(p)                                                     # Y7
+    if plan:
+        out.append("About going to the neighbour's house last night, where it was left: "
+                   + plan[len("About going there tonight: "):])
+    out.append(data.GAP)                                                          # Y8
+    out += (n.lines_short if short else n.lines)[p.id]
+    return ["Yesterday and last night:"] + [f"- {x}" for x in out]
 
 
-def neighbour_line(n, pid):
-    """Their "About the neighbour's house:" line on day 2 (§5.3)."""
-    v = n.visit.get(pid)
-    if v:
+def neighbour_line(n, pid, history=None, day=None, away=None):
+    """Their "About the neighbour's house:" line (night_design §5.3): their own visit on any night outranks one
+    they know of, and a later night outranks an earlier one (reports/days_design.md, §3.5)."""
+    history = history or [n]
+    day = day or n.prev.day + 1
+    away = n.away if away is None else away
+    for night in reversed(history):
+        v = night.visit.get(pid)
+        if not v:
+            continue
+        when = when_words(("N", night.number), day)
         if v["got_in"] and v["found"]:
             rest = v["found"] - v["took"]
             left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
-            return (f"About the neighbour's house: you went in last night and found {portions_text(v['found'])}; "
+            return (f"About the neighbour's house: you went in {when} and found {portions_text(v['found'])}; "
                     f"you brought back {v['took']}{left}. Outside is dangerous.")
         if v["got_in"]:
-            return "About the neighbour's house: you went in last night and found no food there. Outside is dangerous."
-        return "About the neighbour's house: you did not get inside last night. Outside is dangerous."
-    known = [x for x in n.knows[pid] if x != pid]
-    if not known:
-        return NEIGHBOUR_UNKNOWN
-    x = known[0]
-    g = next(g for g in n.groups if x in g["members"])
-    if x in n.away:
-        how = " and has not come back"
-    else:
-        how = " and came back with food" if g["took"] else " and came back with nothing"
-    return f"About the neighbour's house: {NAMES[x]} went there last night{how}. Outside is dangerous."
-
-
-def next_day(day1, n, oracle):
-    """Day 2: a Morning of day 5 with each person as the night left them (§5.1)."""
-    m = world.Morning(oracle, day1.seed, day1.scenario, day=5)
+            return f"About the neighbour's house: you went in {when} and found no food there. Outside is dangerous."
+        return f"About the neighbour's house: you did not get inside {when}. Outside is dangerous."
+    for night in reversed(history):
+        # Whom they know went out: not whoever got up and was talked back to bed.
+        known = [x for x in night.knows[pid] if x != pid and any(x in g["members"] for g in night.groups)]
+        if not known:
+            continue
+        x = known[0]
+        g = next(g for g in night.groups if x in g["members"])
+        if x in away:
+            how = " and has not come back"
+        else:
+            how = " and came back with food" if g["took"] else " and came back with nothing"
+        return (f"About the neighbour's house: {NAMES[x]} went there {when_words(('N', night.number), day)}{how}. "
+                f"Outside is dangerous.")
+    return NEIGHBOUR_UNKNOWN
+
+
+def tag_events(p, k, day):
+    """Grudge and guilt events keep the scene they happened in, and their day words are written for `day`
+    (reports/days_design.md, §3.5): (minute, text with its word, kind, word, scene, text) for a grudge,
+    (minute, text with its word, scene, text) for guilt. k: the played day that has just ended."""
+    for g in p.grudges.values():
+        events = []
+        for e in g.events:
+            scene, raw = ((("N", k) if e[0] >= NIGHT_MINUTE else ("D", k)), e[1]) if len(e) == 3 else (e[4], e[5])
+            word = when_words(scene, day)
+            events.append((e[0], f"{word}, {raw}" if e[2] == "event" else raw, e[2], word, scene, raw))
+        g.events = events
+    tagged = []
+    for e in p.guilt_events:
+        scene, raw = ((("N", k) if e[0] >= NIGHT_MINUTE else ("D", k)), e[1]) if len(e) == 2 else (e[2], e[3])
+        tagged.append((e[0], f"{when_words(scene, day)}, {raw}", scene, raw))
+    p.guilt_events = tagged
+
+
+def next_day(day1, n, oracle, chronicle=None):
+    """The next morning: a Morning of the next house day with each person as the night left them (§5.1). `day1` is
+    the day the night followed. Given the chronicle, each person also carries last night's thoughts (B) and, from
+    day 3 on, the earlier days (C), under one bound with A (reports/days_design.md, §3)."""
+    import memory
+    day = day1.day + 1
+    k = day_index(day1.day)
+    m = world.Morning(oracle, day1.seed, day1.scenario, day=day)
     m.people = n.people
     m.portions = m.start_portions = n.portions
     m.away = set(n.away)
     m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
     present = [q for q in data.ORDER if q not in m.away]
     before, after = n.day1.portions, n.portions
+    history = chronicle.nights if chronicle is not None and chronicle.nights else [n]
     for q in data.ORDER:
         p = m.people[q]
-        m.carry[q] = bounded_carry_in(day1, n, p)
-        m.neighbour[q] = neighbour_line(n, q)
+        variants = carry_variants(day1, n, p)
+        if chronicle is None:
+            m.carry[q] = variants[0]
+            m.blocks[q] = {"A": variants[0], "B": [], "C": [], "earlier": []}
+        else:
+            b_items = memory.b_items(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
+            b = memory.block_b(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
+            c = memory.block_c(chronicle, q, day, away=m.away) if day >= 6 else []
+            r = memory.bounded(variants, b, c, memory.MEMORY_MAX)
+            m.carry[q] = r["C"] + r["A"] + r["B"]
+            earlier = [(it["ids"][:3], it["line"] + (f' You thought then: "{it["thought"]}"' if it.get("thought") else ""))
+                       for it in r["C_items"] if it.get("ids")]
+            earlier += [(ids, line) for ids, line in b_items if f"- {line}" in r["B"]]
+            m.blocks[q] = {"A": r["A"], "B": r["B"], "C": r["C"], "earlier": earlier}
+        m.neighbour[q] = neighbour_line(n, q, history, day, m.away)
     brought = {P: g["took"] for g in n.groups for P in g["members"] if g["took"] and P not in m.away}
     shaken = {P for g in n.groups for P in g["shaken"] if P not in m.away}
     for q in data.ORDER:
         p = m.people[q]
-        p.yesterday = {"confessed": p.confessed,
-                       "confession_heard": bool(p.knows_culprit and p.knows_culprit != p.id),
-                       "suspected_at": [mm for mm in p.suspected_at if mm < NIGHT_MINUTE],
-                       "suspected_last_night": any(mm >= NIGHT_MINUTE for mm in p.suspected_at),
-                       "denials": set(p.denials_heard),
-                       "accused_by": set(p.accused_by)}
+        # The suspicion minutes of the day that ended, and of its night, keep their scene (§3.5).
+        day_ms = [mm for mm in p.suspected_at if mm < NIGHT_MINUTE]
+        if day_ms:
+            p.suspected_past.append((("D", k), day_ms))
+        if any(mm >= NIGHT_MINUTE for mm in p.suspected_at):
+            p.suspected_past.append((("N", k), True))
+        tag_events(p, k, day)
         for g in p.grudges.values():
-            g.events = [(e[0], ("yesterday, " + e[1]) if e[2] == "event" else e[1], e[2],
-                         "last night" if e[0] >= NIGHT_MINUTE else "yesterday") for e in g.events]
             g.last_change = 0
         p.suspicion.last_fall = 0
         p.suspected_at = []
-        p.guilt_events = [(mm, "yesterday, " + fact) for mm, fact in p.guilt_events]
         p.memory, p.said_lines, p.history, p.heard, p.triggers, p.tonight = [], [], [], [], [], []
         p.trip_heard, p.proposed, p.trip_raised = {}, False, False
         p.addressed = p.aside_lead = None
diff --git a/Prototypes/llm-morning/story.py b/Prototypes/llm-morning/story.py
index 7e9fd50..afbaf91 100644
--- a/Prototypes/llm-morning/story.py
+++ b/Prototypes/llm-morning/story.py
@@ -365,7 +365,7 @@ def body(morning, out, all_d, names, culprit, who, pro):
         w("- Nobody holds a grudge at minute 90.")
     if culprit:
         guilty = morning.people[culprit]
-        facts = "; ".join(fact for m, fact in guilty.guilt_events) or "nothing since"
+        facts = "; ".join(e[1] for e in guilty.guilt_events) or "nothing since"
         w(f"- {who}'s guilt ({guilty.guilt}/3): {pro['he']} ate the can in the night, and nobody saw; {facts}.")
     w("")
     last = []
@@ -380,6 +380,8 @@ def body(morning, out, all_d, names, culprit, who, pro):
 
 # ---------- the night and day 2 (reports/night_design.md, §8) ----------
 NAME = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
+NIGHT_TITLE = {1: "# The night", 2: "# The second night", 3: "# The third night"}
+DAY_TITLE = {5: "# The next morning (day 5)", 6: "# The third morning (day 6)"}
 ASKED = {"bedtime": "at bedtime", "reaction": "noticing it", "answer": "told not to go"}
 
 
@@ -426,7 +428,7 @@ def render_night(n):
     import night as night_mod
     out = []
     w = out.append
-    w("# The night")
+    w(NIGHT_TITLE.get(n.number, f"# Night {n.number}"))
     w("")
     w(f"{data.GAP} Before bed, hunger rose by {night_mod.GAP_HUNGER} × each person's hunger rate, and by "
       f"{night_mod.NIGHT_HUNGER} × more in the night. Everyone went to bed in their own room: {night_mod.BEDS}. "
@@ -437,7 +439,8 @@ def render_night(n):
     w("")
     w("| | " + " | ".join(NAME[p] for p in data.ORDER) + " |")
     w("|---|" + "---|" * len(data.ORDER))
-    w("| Hunger at bedtime | " + " | ".join(f"{n.bedtime_hunger[p]:.2f} ({hunger_words(n.bedtime_hunger[p])})"
+    w("| Hunger at bedtime | " + " | ".join("away" if n.bedtime_hunger[p] is None else
+                                           f"{n.bedtime_hunger[p]:.2f} ({hunger_words(n.bedtime_hunger[p])})"
                                            for p in data.ORDER) + " |")
     w("| Wakes when the roommate gets up | " + " | ".join(f"{night_mod.wake_room(p):.2f}" for p in data.ORDER) + " |")
     w("| Wakes at the front door | " + " | ".join(f"{night_mod.wake_door(p):.2f}" for p in data.ORDER) + " |")
@@ -514,7 +517,7 @@ def render_day2(morning):
     n_model = sum(d["mode"] == "model" for d in all_d)
     n_fall = sum(d["mode"] == "fallback" for d in all_d)
     n_rout = sum(d["mode"] == "routine" for d in all_d)
-    w("# The next morning (day 5)")
+    w(DAY_TITLE.get(morning.day, f"# The morning of day {morning.day}"))
     w("")
     w(f"The same rules as day 1, from the people as the night left them. **{len(all_d)} decisions**: {n_model} by "
       f"the model, {n_fall} fallbacks, {n_rout} routine. {len(morning.said)} lines were spoken aloud. The shelf held "
@@ -539,3 +542,36 @@ def render_day2(morning):
         w("")
     body(morning, out, all_d, names, culprit, who, pro)
     return "\n".join(out)
+
+
+def render_mind(mind):
+    """What the night left in them (reports/days_design.md, §2.8): each person's night mind, every memory it
+    proposed with the records it cites and its verdict, the feeling and the intent."""
+    out = []
+    w = out.append
+    w("## What the night left in them")
+    w("")
+    w("Once the night was over, each person in the house was asked once what the day leaves in them. Each memory "
+      "cites the records it is about; one that fails a check (reports/days_design.md, §2.6) never reaches a prompt.")
+    w("")
+    for pid in data.ORDER:
+        r = mind.results.get(pid)
+        if r is None:
+            w(f"- **{NAME[pid]}**: away, not asked.")
+            continue
+        if r["mode"] == "fallback":
+            w(f"- **{NAME[pid]}** ({r['prompt_tokens']} estimated tokens). **FALLBACK**: the answer could not be used "
+              f"({r['invalid']}), so {NAME[pid]} carries nothing from this night.")
+            continue
+        feeling = r["feeling"] if r["feeling"] else f"({r['feeling_verdict']})"
+        intent = quoted(r["intent"]) if r["intent"] else f"({r['intent_verdict']})"
+        w(f"- **{NAME[pid]}** ({r['prompt_tokens']} estimated tokens). Feeling: *{feeling}*. Intent: {intent}")
+        for m in r["memories"]:
+            ids = m["ids"] if isinstance(m["ids"], list) else []
+            w(f"  - {', '.join(str(i) for i in ids) or '(no ids)'}: {quoted(m['meaning'])} **{m['verdict']}**")
+            for i in ids:
+                e = mind.chron.event(i)
+                if e is not None and e["views"].get(pid):
+                    w(f"    - {i}: {e['views'][pid]}")
+    w("")
+    return "\n".join(out) + "\n"
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index ec4c0de..9e93ab4 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -208,7 +208,9 @@ class FakeMorningTest(unittest.TestCase):
         story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed7.md"))
         self.assertIn("## The morning", story)
         self.assertIn("## What was said", story)
-        self.assertLessEqual(meta["api_requests"], 150)
+        # The call cap counts each scene apart (reports/night_design.md, §8; days_design.md, §2.1).
+        for scene in ("day1", "night", "mind1", "day2", "night2", "mind2", "day3"):
+            self.assertLessEqual(meta[scene]["api_requests"], 150, scene)
         self.assertGreater(meta["day1"]["model_decisions"], 0)
         self.assertGreater(meta["day1"]["routine_decisions"], 0)
 
@@ -1181,6 +1183,9 @@ class WitnessScenarioTest(unittest.TestCase):
         daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
         self.assertTrue(daniel)
         for p in daniel:
+            # From the second night on, Daniel can himself wake at the front door (reports/days_design.md): those
+            # lines are the night's, not Leo's can.
+            p = "\n".join(x for x in p.split("\n") if "the front door" not in x)
             for words in (NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can",
                           "did not see who", "does not see who", "heard someone",
                           "someone in this house took it"):
@@ -1203,13 +1208,16 @@ class WitnessScenarioTest(unittest.TestCase):
                 self.assertEqual(len(lines), 1)
                 self.assertTrue(lines[0].endswith(" " + NOTE), lines[0])
                 self.assertEqual([x for x in p.splitlines() if x.startswith("About the can")], lines)
-                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3).
+                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3); day 3's
+                # also "two days ago" and "the night before last" (reports/days_design.md, §3.5).
+                day = r"(yesterday|two days ago|\w+ days ago)"
+                night = r"(last night|the night before last|\w+ nights ago)"
                 self.assertRegex(lines[0][:-len(" " + NOTE)],
                                  r"^About the can(: you have not settled on who took it\."
                                  r"| \([a-z ]+\): you thought \w+ took it, at minutes? [\d, and]+\."
-                                 r"| \([a-z ]+\): you thought \w+ took it(, (and )?(yesterday at minutes? [\d, and]+"
-                                 r"|last night|this morning at minutes? [\d, and]+))*\."
-                                 r"|: \w+ admitted taking it( yesterday,)? at minute \d\d\.)$")
+                                 rf"| \([a-z ]+\): you thought \w+ took it(, (and )?({day} at minutes? [\d, and]+"
+                                 rf"|{night}|this morning at minutes? [\d, and]+))*\."
+                                 rf"|: \w+ admitted taking it( {day},)? at minute \d\d\.)$")
                 for words in ("Daniel eats a can", "you ate it yourself", "On your conscience"):
                     self.assertNotIn(words, p)
             else:
@@ -2230,6 +2238,7 @@ BEDTIME_OPTIONS = ("Your options:\n"
 GAP = "The afternoon and evening passed in the house. Nobody ate."
 CARRY_HEAD = "Yesterday and last night:"
 CARRY_MAX = 360
+MEMORY_HARD = 610           # blocks A, B and C at most, once trimmed (reports/days_design.md, §3.4)
 DAY2_TRIP_IDS = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")
 FATE = re.compile(r"\b(dead|die[sd]?|dying|kill\w*|hurt|wound\w*|blood\w*|corpse|injur\w*|bit(e|ten)|attack\w*|"
                   r"taken)\b", flags=re.I)
@@ -2244,14 +2253,25 @@ class NightScripted:
     first one offered is chosen, with words if it is speech. Otherwise the first option of the
     night (sleep, let them go, stay in bed, go anyway), or `silent` by day."""
 
-    def __init__(self, prefs=None, angry=None):
+    def __init__(self, prefs=None, angry=None, minds=None):
         self.prefs, self.angry = prefs or {}, angry or {}
+        self.minds = minds or {}    # who -> answers to their night-mind prompts, in turn (reports/days_design.md, §2)
         self.requests = 0
         self.prompts = []           # (minute or "night", who, prompt)
+        self.mind_prompts = []      # (who, system, prompt, schema)
 
-    def generate(self, system, prompt):
+    def generate(self, system, prompt, schema=None):
         self.requests += 1
         who = re.match(r"You are (\w+),", prompt).group(1).lower()
+        if schema is not None:      # a night mind: the queued answer, or one memory citing the first record
+            self.mind_prompts.append((who, system, prompt, schema))
+            queue = self.minds.get(who)
+            if queue:
+                answer = queue.pop(0)
+                return answer if isinstance(answer, str) else json.dumps(answer)
+            ids = re.findall(r"^\[([DN]\d+-\d+)\] ", prompt, flags=re.M)
+            return json.dumps({"memories": [{"ids": ids[:1], "meaning": f"A thought of {who}, {self.requests}."}],
+                               "feeling": "tired", "intent": f"Get through it, {who}."})
         m = re.search(r"^Now, minute (\d+)", prompt, flags=re.M)
         where = int(m.group(1)) if m else "night"
         block = prompt.split("Your options:")[-1]
@@ -2281,10 +2301,11 @@ def option_lines(prompt):
 
 
 def without_blocks(prompt):
-    """A day-2 or night prompt without its trip block and its carry-in block."""
+    """A day-2 or night prompt without its trip block and its carry-in block (from day 3 on, the memory blocks A, B
+    and C: reports/days_design.md, §3)."""
     out, skipping = [], False
     for line in prompt.split("\n"):
-        if line == CARRY_HEAD:
+        if line in (CARRY_HEAD, B_HEAD, EARLIER):
             skipping = True
             continue
         if skipping and line.startswith("- "):
@@ -2383,7 +2404,7 @@ class NightTest(unittest.TestCase):
         self.assertIn("\n# The next morning (day 5)\n", story)
         tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
         self.assertEqual(tr["day1"], json.loads(json.dumps(day1.transcript)))
-        self.assertEqual(set(tr), {"day1", "night", "day2"})
+        self.assertEqual(set(tr), {"day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"})
 
     # T2
     def test_t2_the_gap(self):
@@ -2960,14 +2981,17 @@ class NightTest(unittest.TestCase):
             (_, code), out = fake_morning(self.dirs, seed=seed)
             self.assertEqual(code, 0, out)
         for p in cached_prompts(self.dirs):
+            # A second night's prompts carry day 2's blocks; every morning's blocks are bounded together at most at
+            # MEMORY_HARD (reports/days_design.md, §3.4).
             if "\nNow it is night" in p:
                 night_n += 1
                 self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
-                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p), 1450 + TRIP_BLOCK_MAX)
+                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p),
+                                1450 + TRIP_BLOCK_MAX + (MEMORY_HARD if CARRY_HEAD in p else 0))
             elif CARRY_HEAD in p:
                 day2_n += 1
                 self.assertLess(estimate_tokens(SYSTEM + without_blocks(p)), 1450)
-                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + CARRY_MAX)
+                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + MEMORY_HARD)
         self.assertGreater(night_n, 0)
         self.assertGreater(day2_n, 0)
         # The carry-in costs this morning no line.
@@ -2998,7 +3022,8 @@ class NightTest(unittest.TestCase):
         self.assertEqual(meta["night_asks"], len(tr["night"]["decisions"]))
         self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for t in tr["day2"]["turns"] for a in t["acts"]))
         self.assertEqual(meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night_asks"]
-                         + meta["day2_asks"], meta["answers_live"] + meta["answers_from_cache"])
+                         + meta["day2_asks"] + meta["mind1_asks"] + meta["night2_asks"] + meta["mind2_asks"]
+                         + meta["day3_asks"], meta["answers_live"] + meta["answers_from_cache"])
         self.assertEqual(meta["leavers"], tr["night"]["leavers"])
         for key in ("night_asks", "day2_asks", "night_api_requests", "day2_api_requests"):
             self.assertIn(f"{key}: {meta[key]}", out)
@@ -3598,6 +3623,650 @@ def render_day2_text(day2):
     return render_day2(day2)
 
 
+NIGHT_MIND_TEXT = (
+    "You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who "
+    "they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, "
+    "saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things from "
+    "these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one sentence "
+    "of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, forgive or "
+    "doubt, as this person would, but it must not add anything that happened beyond the records: no other event, no "
+    "number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, tomorrow). "
+    "`feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do tomorrow, in one "
+    "sentence, as they would think it. Reply with JSON only: {\"memories\": [{\"ids\": [\"<id>\"], \"meaning\": "
+    "\"<sentence>\"}], \"feeling\": \"<words>\", \"intent\": \"<sentence>\"}")
+MIND_END = "The night is over. What does today leave in you?"
+MIND_RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
+EARLIER = "What stays with you from earlier days:"
+B_HEAD = "What yesterday left in you (your own thoughts, last night):"
+RECORD_LINE = re.compile(r"^\[([DN]\d+-\d+)\] (min \d\d|tonight): ")
+WITNESS_MODES = {"did", "saw", "heard", "voices", "knew"}
+EVENT_KEYS = {"id", "scene", "minute", "kind", "option", "actor", "target", "members", "words", "room", "witnesses",
+              "text", "gist", "group", "effects", "views", "outcome"}
+
+
+def mind_answer(ids, meaning, feeling="tired", intent="Keep watch over them."):
+    return json.dumps({"memories": [{"ids": ids, "meaning": meaning}], "feeling": feeling, "intent": intent})
+
+
+class DaysTest(unittest.TestCase):
+    """Days that follow one another: the night mind, the chronicle, the memory blocks and the second night and third
+    morning (reports/days_design.md, tests N-T1 to N-T14 of §7.1, and the amendment to §3.3's table)."""
+
+    setUp_ = NightTest.setUp
+    tearDown = NightTest.tearDown
+    path = NightTest.path
+    v11_day1 = NightTest.v11_day1
+    short_day1 = NightTest.short_day1
+    night_of = NightTest.night_of
+    act = NightTest.act
+
+    def setUp(self):
+        self.setUp_()
+        self.chron = importlib.import_module("chronicle")
+        self.mind = importlib.import_module("mind")
+        self.memory = importlib.import_module("memory")
+
+    def three_days(self, seed=2, client=None, draws1=None, draws2=None, day2_turns=1, day2_food=never, prefs2=None):
+        """Day 1 of seed N from v11's answers, then night 1, mind 1, a short day 2, night 2, mind 2 and day 3 (not
+        played), all answered by `client`. prefs2 replaces the client's preferences before night 2."""
+        client = client or NightScripted()
+        day1, oracle = self.v11_day1(seed, client)
+        chron = self.chron.Chronicle(seed, day1.culprit)
+        chron.add_day(day1)
+        n1 = self.night.Night(day1, oracle, draws=draws1 or {}).run()
+        chron.add_night(n1)
+        self.mind.NightMind(n1, chron, oracle).run()
+        day2 = Morning.next_day(day1, n1, oracle, chronicle=chron)
+        day2.food_draw = day2_food
+        for t in range(day2_turns):
+            day2.turn(t)
+        day2.finish()
+        chron.add_day(day2)
+        if prefs2 is not None:
+            client.prefs = prefs2
+        n2 = self.night.Night(day2, oracle, draws=draws2 or {}, number=2, house=chron.house_state()).run()
+        chron.add_night(n2)
+        self.mind.NightMind(n2, chron, oracle).run()
+        day3 = Morning.next_day(day2, n2, oracle, chronicle=chron)
+        return type("Days", (), dict(day1=day1, n1=n1, day2=day2, n2=n2, day3=day3, chron=chron, client=client,
+                                     oracle=oracle))
+
+    def handmade(self, events, culprit="daniel"):
+        """A chronicle written by hand: each event a dict, with defaults filled by Chronicle.add."""
+        c = self.chron.Chronicle(1, culprit)
+        for e in events:
+            c.add(e)
+        return c
+
+    # N-T1
+    def test_n_t1_day1_replays_and_the_chronicle_leaves_it_alone(self):
+        for seed, served in V11_SERVED.items():
+            name = f"daniel_ate_it-seed{seed}"
+            day1, oracle = self.v11_day1(seed)
+            chron = self.chron.Chronicle(seed, day1.culprit)
+            chron.add_day(day1)
+            text = render(day1, seed, V6_MODEL, f"python morning.py --seed {seed}")
+            self.assertEqual(text.encode("utf-8"), read(os.path.join(V11_RUNS, name + ".md"), "rb"), seed)
+            self.assertEqual(json.loads(json.dumps(day1.transcript)),
+                             json.loads(read(os.path.join(V11_RUNS, name + ".transcript.json"))), seed)
+            self.assertEqual((oracle.from_cache, oracle.api_requests), (served, 0), seed)
+            self.assertTrue(chron.events and all(e["scene"] == "D1" for e in chron.events), seed)
+
+    # N-T2
+    def test_n_t2_the_cycle(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+        self.assertEqual(set(tr), {"day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"})
+        self.assertEqual([s["id"] for s in tr["chronicle"]["scenes"]], ["D1", "G1", "N1", "D2", "G2", "N2", "D3"])
+        self.assertEqual(len(tr["day3"]["turns"]), 30)
+        story = read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.md"))
+        heads = ["# The night\n", "## What the night left in them\n", "# The next morning (day 5)\n",
+                 "# The second night\n", "## What the night left in them\n", "# The third morning (day 6)\n"]
+        at = 0
+        for h in heads:
+            at = story.index(h, at) + 1
+        self.assertNotIn("# The third night", story)
+        for key in ("night1_asks", "mind1_asks", "day2_asks", "night2_asks", "mind2_asks", "day3_asks"):
+            self.assertIn(key, meta)
+        # Hunger over gap 2 and night 2; day 3 is a Morning of day 6 with the trip open from minute 00.
+        d = self.three_days(seed=2)
+        for pid in data.ORDER:
+            rate = data.PEOPLE[pid]["hunger_rate"]
+            bed = min(1.0, d.day2.people[pid].hunger + 0.3 * rate)
+            self.assertAlmostEqual(d.n2.bedtime_hunger[pid], bed, places=9, msg=pid)
+            self.assertAlmostEqual(d.day3.people[pid].hunger, min(1.0, bed + 0.1 * rate), places=9, msg=pid)
+        self.assertEqual(d.day3.day, 6)
+        self.assertEqual(d.day3.trip, {"minute": 0, "why": ["carried over from yesterday"], "asked": []})
+        self.assertEqual(d.n2.number, 2)
+
+    # N-T3
+    def test_n_t3_the_night_minds_prompt_exactly(self):
+        self.assertEqual(self.mind.NIGHT_MIND_SYSTEM, NIGHT_MIND_TEXT)
+        d = self.three_days(seed=2)
+        night1 = [x for x in d.client.mind_prompts if "[N1-" in x[2] and "[N2-" not in x[2]]
+        self.assertEqual([w for w, *_ in night1], data.ORDER)
+        who, system, prompt, schema = next(x for x in night1 if x[0] == "leo")
+        self.assertEqual(system, NIGHT_MIND_TEXT)
+        lines = prompt.split("\n")
+        self.assertEqual(lines[0], "You are Leo, 21, the younger son of the family (Elena, 42, the mother; Daniel, 25; "
+                                   "Leo, 21; Mara, 17).")
+        for i, start in enumerate(("How you address them: ", "Who you are: ", "Temperament: ", "What matters to you: ",
+                                   "Your body: ", "About the can: Daniel admitted taking it at minute 33.")):
+            self.assertTrue(lines[1 + i].startswith(start), lines[1 + i])
+        for gone in ("About food:", "About the neighbour's house:", "About going there tonight:"):
+            self.assertFalse([x for x in lines if x.startswith(gone)], gone)
+        at = lines.index(EARLIER + " nothing yet.")
+        self.assertEqual(lines[at + 1], MIND_RECORDS)
+        self.assertEqual(lines[-1], MIND_END)
+        records = lines[at + 2:-1]
+        self.assertTrue(records and all(RECORD_LINE.match(x) for x in records), records)
+        ids = [RECORD_LINE.match(x).group(1) for x in records]
+        self.assertEqual(ids, sorted(ids, key=lambda i: (i[0] == "N", int(i[1:].split("-")[0]), int(i.split("-")[1]))))
+        self.assertEqual(records[0], "[D1-001] min 00: Elena counts the pantry with everyone standing there. She finds one "
+                                     "can fewer than she expected and says so. 2 portions are left. (you saw it)")
+        # R1 and R7: Daniel's three accusations of Leo, folded into the first.
+        self.assertTrue([x for x in records if re.match(r'^\[D1-\d{3}\] min 03: Daniel accuses you of taking it: ".+" '
+                                                        r'Then 2 more times, to min 12; last: ".+"$', x)], records)
+        # R2: Leo's own words, with the feeling he gave.
+        self.assertTrue([x for x in records if re.match(r'^\[D1-\d{3}\] min \d\d: you [^"]+, saying: ".+"', x)], records)
+        # R3: an act seen, one record, from the pinned line; a confession heard, with its words.
+        self.assertTrue([x for x in records if "min 54: Mara ate one of the portions (you saw it)" in x])
+        self.assertEqual(sum("Mara ate one of the portions" in x or "Mara says to everyone, while eating" in x
+                             for x in records), 1)
+        self.assertIn("min 33: Daniel admitted taking the can: \"I took it in the night, I'm sorry.\" (you heard it)",
+                      "\n".join(records))
+        # R5: the night, in the night's own words.
+        self.assertRegex(records[-1], r"^\[N1-\d\d\] tonight: You went to bed in the brothers room with Daniel\. "
+                                      r"You went to sleep\.$")
+        enum = schema["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"]
+        self.assertEqual(enum, ids)
+        # Night 2: the earlier days are B of day 2, each line with its ids.
+        who, _, prompt2, schema2 = next(x for x in d.client.mind_prompts if x[0] == "leo" and "[N2-" in x[2])
+        lines2 = prompt2.split("\n")
+        at = lines2.index(EARLIER)
+        self.assertTrue(lines2[at + 1].startswith("- [D1-"), lines2[at + 1])
+        self.assertIn('A thought of leo', lines2[at + 1])
+        shown = re.findall(r"\[([DN]\d+-\d+)", "\n".join(lines2[at:]))
+        self.assertEqual(schema2["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"],
+                         list(dict.fromkeys(shown)))
+        # R8: at most 1,600 tokens of records; reassurances lose their words first, never the night's or a confession.
+        many = [(f"D1-{i:03d}", f'min 03: Elena reassures you: "{"so very long words " * 12}"') for i in range(1, 60)]
+        many += [("D1-060", 'min 33: Daniel admitted taking the can: "I took it in the night." (you heard it)'),
+                 ("N1-01", 'tonight: Leo told you, low, not to go: "Do not go." You answered: "I must.", and went all '
+                           'the same.')]
+        bounded = self.mind.bound_records(many)
+        self.assertLessEqual(estimate_tokens("\n".join(f"[{i}] {x}" for i, x in bounded)), self.mind.RECORDS_MAX)
+        self.assertEqual(bounded[-2:], many[-2:])
+        self.assertEqual(bounded[0][1], "min 03: Elena reassures you.")
+
+    # N-T4
+    def test_n_t4_records_hold_only_what_was_perceived(self):
+        (meta, code), out = fake_morning(self.dirs, seed=3)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed3.transcript.json")))
+        events = {e["id"]: e for e in tr["chronicle"]["events"]}
+        minds = [p for p in cached_prompts(self.dirs) if p.endswith(MIND_END)]
+        self.assertTrue(minds)
+        for prompt in minds:
+            who = re.match(r"You are (\w+),", prompt).group(1).lower()
+            for line in prompt.split("\n"):
+                m = re.match(r"^\[([DN]\d+-\d+)\] ", line)
+                if m:
+                    self.assertIn(who, events[m.group(1)]["witnesses"], line)
+                if "Voices from the" in line:
+                    self.assertNotIn('"', line)
+        # By day: whoever saw an act was in its room when the turn began; nobody hears into or out of the bathroom.
+        for scene in ("day1", "day2", "day3"):
+            k = scene[-1]
+            for turn in tr[scene]["turns"]:
+                for a in turn["acts"]:
+                    e = next((e for e in events.values() if e["scene"] == f"D{k}" and e["minute"] == turn["minute"]
+                              and e["actor"] == a["who"] and e["option"] == a["option"]), None)
+                    if e is None:
+                        continue
+                    for w, how in e["witnesses"].items():
+                        self.assertIn(how, WITNESS_MODES)
+                        if how == "saw" and e["kind"] not in ("go", "aside", "accept_aside"):   # arrivals are seen
+                            self.assertIn(w, turn["rooms"][a["room"]] + [a["who"]], (scene, e["id"]))
+                        if how == "voices":
+                            self.assertNotEqual(a["room"], "bathroom", e["id"])
+
+    # N-T5
+    def test_n_t5_the_checks(self):
+        c = self.handmade([
+            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
+             "target": "leo", "words": "You took it, Leo.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
+            {"id": "D1-002", "scene": "D1", "minute": 9, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
+             "target": "leo", "words": "It was you.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
+            {"id": "D1-003", "scene": "D1", "minute": 21, "kind": "eat", "option": "eat", "actor": "mara",
+             "witnesses": {p: "saw" for p in data.ORDER} | {"mara": "did"}},
+            {"id": "D1-004", "scene": "D1", "minute": 30, "kind": "eat", "option": "eat", "actor": "leo",
+             "witnesses": {p: "saw" for p in data.ORDER} | {"leo": "did"}},
+            {"id": "D1-005", "scene": "D1", "minute": 30, "kind": "deny", "option": "deny", "actor": "leo",
+             "words": "I did not.", "witnesses": {p: "saw" for p in data.ORDER} | {"leo": "did"}},
+            {"id": "D1-006", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess", "actor": "daniel",
+             "words": "I took it in the night, I'm sorry.", "witnesses": {p: "saw" for p in data.ORDER} | {"daniel": "did"}},
+            {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "bedtime", "option": "go_next_door", "actor": "daniel",
+             "witnesses": {"daniel": "did"}},
+            {"id": "N1-02", "scene": "N1", "minute": 90, "kind": "stop", "option": "stop_daniel", "actor": "leo",
+             "target": "daniel", "words": "Daniel, stop, you are not going out there tonight.",
+             "witnesses": {"leo": "did", "daniel": "heard"}},
+            {"id": "N1-03", "scene": "N1", "minute": 90, "kind": "went_out", "actor": "daniel", "members": ["daniel"],
+             "witnesses": {"daniel": "did", "leo": "knew"}},
+        ])
+        shown = {i: f"text of {i}" for i in ("D1-001", "D1-002", "D1-003", "D1-004", "D1-005", "D1-006", "N1-02", "N1-03")}
+        shown["D1-006"] = "min 33: Daniel admitted taking the can: \"I took it in the night, I'm sorry.\" (you heard it)"
+
+        def verdict(pid, ids, meaning, carried=(), shown_ids=shown):
+            r = self.mind.check_answer(mind_answer(ids, meaning), pid, shown_ids, c, carried)
+            return r["memories"][0]["verdict"]
+        # §2.7's five examples.
+        self.assertEqual(verdict("daniel", ["N1-02"], "Leo had no right to stop me when I was the only one willing to "
+                                                     "act."), "kept")
+        self.assertTrue(verdict("mara", ["D1-004", "D1-005"], "Leo ate mine too and lied to my face about it.")
+                        .startswith("rejected: S8"))
+        self.assertTrue(verdict("leo", ["D1-006"], "Daniel never admitted anything until he was cornered.")
+                        .startswith("rejected: S8"))
+        self.assertEqual(verdict("mara", ["D1-006"], "If Daniel had gone out instead of eating, we might have food."),
+                         "kept")
+        self.assertEqual(verdict("mara", ["D1-003"], "He hid food in his bag."), "kept")
+        # One failing case for each check.
+        cases = [
+            ([], "He blamed me.", "S1"),
+            (["D1-001", "D1-002", "D1-003", "D1-004"], "He blamed me.", "S1"),
+            (["D1-001"], " ".join(["word"] * 31) + ".", "S1"),
+            (["D1-001"], "He lied. He knew.", "S1"),
+            (["D1-999"], "He blamed me.", "S2"),
+            (["N1-01"], "He went to bed.", "S2"),
+            (["D1-003"], "Mara ate two portions.", "S3"),
+            (["D1-001"], "Mom never trusted me.", "S4"),
+            (["D1-001"], "Tonight I saw who he really is.", "S5"),
+            (["D1-006"], 'Daniel said "I will fix everything" and smiled.', "S6"),
+            (["D1-006"], "Daniel probably hid bread somewhere.", "S7"),
+            (["D1-003"], "Mara stole the can.", "S8"),
+            (["D1-003"], "Mara ate again.", "S8"),
+        ]
+        for ids, meaning, check in cases:
+            got = verdict("leo", ids, meaning, shown_ids={**shown, "N1-01": "x"} if "N1-01" in ids else shown)
+            self.assertTrue(got.startswith(f"rejected: {check}"), (meaning, got))
+        self.assertEqual(verdict("leo", ["D1-001", "D1-002"], "Daniel accused me again."), "kept")
+        self.assertEqual(verdict("leo", ["D1-001"], "Daniel would have let me take the blame."), "kept")
+        self.assertEqual(verdict("leo", ["D1-006"], 'Daniel said "I took it in the night" at last.'), "kept")
+        self.assertTrue(verdict("leo", ["D1-001"], "Daniel let me take the blame.",
+                                carried=["Daniel let me take the blame."]).startswith("rejected: S9"))
+        # Feeling and intent; a fourth memory is dropped unread; an answer that is not usable carries nothing.
+        r = self.mind.check_answer(json.dumps({"memories": [{"ids": ["D1-001"], "meaning": "He blamed me."}] * 4,
+                                               "feeling": "very very tired and sad", "intent": "Find bread for Mara."}),
+                                   "leo", shown, c, ())
+        self.assertEqual(len(r["memories"]), 3)
+        self.assertEqual(r["memories"][0]["verdict"], "kept")
+        self.assertTrue(r["memories"][1]["verdict"].startswith("rejected: S9"))
+        self.assertTrue(r["feeling_verdict"].startswith("rejected"))
+        self.assertTrue(r["intent_verdict"].startswith("rejected: S7"))
+        self.assertEqual([m["meaning"] for m in r["kept"]], ["He blamed me."])
+        r = self.mind.check_answer("not json", "leo", shown, c, ())
+        self.assertEqual((r["mode"], r["kept"], r["feeling"], r["intent"]), ("fallback", [], None, None))
+
+    # N-T6
+    def test_n_t6_the_blocks_exactly(self):
+        # A on day 2 is v13's carry-in, byte for byte; B follows it.
+        client = NightScripted()
+        day1, oracle = self.v11_day1(3, client)
+        n = self.night.Night(day1, oracle).run()
+        plain = Morning.next_day(day1, n, oracle)
+        d = self.three_days(seed=3)
+        for p in data.ORDER:
+            self.assertEqual(d.day2.carry[p][:len(plain.carry[p])], plain.carry[p], p)
+            self.assertEqual(d.day2.carry[p][len(plain.carry[p])], B_HEAD, p)
+        # A on day 3: yesterday's facts by the Y lines, then the night.
+        d = self.three_days(seed=2, client=NightScripted({"mara": ["confront_daniel"], "leo": ["eat"]}))
+        a = d.day3.blocks["mara"]["A"]
+        self.assertEqual(a, [CARRY_HEAD,
+                             "- Yesterday morning the shelf held 1 portion.",
+                             "- Confrontations: you confronted Daniel (min 00).",
+                             "- Leo ate a portion at minute 00 (you saw it).",
+                             "- " + GAP,
+                             "- Last night you slept in the back room with Elena. You went to sleep."])
+        # B, written around the night mind's words.
+        c = self.handmade([{"id": "D1-001", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess",
+                            "actor": "daniel", "witnesses": {"daniel": "did", "leo": "saw"}}])
+        b = self.memory.block_b({"kept": [{"ids": ["D1-001"], "meaning": "He let me take the blame."}],
+                                 "feeling": "bitter", "intent": "Make him answer for it."}, c, "leo")
+        self.assertEqual(b, [B_HEAD, '- About Daniel admitting taking the can: "He let me take the blame."',
+                             '- You meant to: "Make him answer for it."', "- How it left you: bitter."])
+        # C: one line per person by weight, older on a tie, the night's words, one older thought per line.
+        everyone = {p: "saw" for p in data.ORDER}
+        events = [
+            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
+             "target": "leo", "witnesses": everyone | {"daniel": "did"}},
+            {"id": "D1-002", "scene": "D1", "minute": 3, "kind": "reassure", "option": "reassure_leo", "actor": "elena",
+             "target": "leo", "witnesses": everyone | {"elena": "did"}},
+            {"id": "D1-003", "scene": "D1", "minute": 9, "kind": "accuse", "option": "accuse_leo", "actor": "daniel",
+             "target": "leo", "witnesses": everyone | {"daniel": "did"}},
+            {"id": "D1-004", "scene": "D1", "minute": 21, "kind": "eat", "option": "eat", "actor": "mara",
+             "witnesses": everyone | {"mara": "did"}},
+            {"id": "D1-005", "scene": "D1", "minute": 30, "kind": "give", "option": "give_leo", "actor": "elena",
+             "target": "leo", "witnesses": everyone | {"elena": "did"}},
+            {"id": "D1-006", "scene": "D1", "minute": 33, "kind": "confess", "option": "confess", "actor": "daniel",
+             "witnesses": everyone | {"daniel": "did"}},
+            {"id": "D1-007", "scene": "D1", "minute": 36, "kind": "accuse", "option": "accuse_mara", "actor": "elena",
+             "target": "mara", "witnesses": everyone | {"elena": "did"}},
+            {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "stop", "option": "stop_daniel", "actor": "leo",
+             "target": "daniel", "witnesses": {"leo": "did", "daniel": "heard"}},
+            {"id": "D2-001", "scene": "D2", "minute": 0, "kind": "eat", "option": "eat", "actor": "daniel",
+             "witnesses": everyone | {"daniel": "did"}},
+        ]
+        c = self.handmade(events)
+        c.minds[1] = {"leo": {"kept": [{"ids": ["D1-006"], "meaning": "He let me take the blame."},
+                                        {"ids": ["D1-006"], "meaning": "He only spoke when cornered."}]}}
+        lines = [x[2:] for x in self.memory.render_c(self.memory.block_c(c, "leo", 6))[1:]]
+        self.assertEqual(lines, ['Two days ago, Daniel admitted taking the can, after accusing you of it. You thought '
+                                 'then: "He only spoke when cornered."',
+                                 "Two days ago, Elena reassured you.",
+                                 "The night before last, you told Daniel, low, not to go.",
+                                 "Two days ago, Mara ate a portion in front of you."])
+        # Without the confession: the can is a standing line, and the accusations are counted.
+        c = self.handmade([e for e in events if e["id"] != "D1-006"])
+        lines = [x["line"] for x in self.memory.block_c(c, "leo", 6)]
+        self.assertEqual(lines[:2], ["Two days ago Elena counted the pantry and found one can fewer than she expected. "
+                                     "Nobody has admitted taking it.",
+                                     "Two days ago, Daniel accused you of taking the can twice, and you had not."])
+        # Someone not back is a standing line.
+        c = self.handmade(events + [{"id": "N1-02", "scene": "N1", "minute": 90, "kind": "went_out", "actor": "mara",
+                                     "members": ["mara"], "witnesses": {"mara": "did", "leo": "knew"}}])
+        lines = [x["line"] for x in self.memory.block_c(c, "leo", 6, away={"mara"})]
+        self.assertEqual(lines[0], "Mara went out the night before last and has not come back.")
+        self.assertFalse([x for x in lines[1:] if x.startswith("Two days ago, Mara")])
+
+    # N-T7
+    def test_n_t7_the_bound(self):
+        M = self.memory
+        self.assertEqual(M.MEMORY_MAX, 560)
+        a = [[CARRY_HEAD] + [f'- line {i}: "{"quoted words " * 6}" (min 01, 02, 03)' for i in range(9)],
+             [CARRY_HEAD] + [f"- line {i}. (min 01, 02, 03)" for i in range(9)],
+             [CARRY_HEAD] + [f"- line {i}." for i in range(9)]]
+        b = [B_HEAD, '- About Daniel eating a portion: "' + "word " * 25 + '"', '- You meant to: "' + "word " * 25 + '"',
+             "- How it left you: bitter."]
+        c = [{"line": "Two days ago Elena counted the pantry. Nobody has admitted taking it.", "weight": 9,
+              "standing": True, "thought": None, "self": False, "order": 0},
+             {"line": "Two days ago, Daniel admitted taking the can.", "weight": 5, "standing": False,
+              "thought": "He only spoke when cornered and never once said sorry to any of us at all.",
+              "self": False, "order": 1},
+             {"line": "Two days ago, Elena reassured you.", "weight": 3, "standing": False, "thought": None,
+              "self": False, "order": 2},
+             {"line": "Two days ago, you ate a portion in front of the others.", "weight": 4, "standing": False,
+              "thought": None, "self": True, "order": 3}]
+        full = M.bounded(a, b, c, 10 ** 6)
+        size = lambda r: estimate_tokens("\n".join(r["C"] + r["A"] + r["B"]))
+        steps = []
+        cap = size(full)
+        while True:
+            r = M.bounded(a, b, c, cap - 1)
+            if size(r) >= cap:
+                break
+            steps.append(r)
+            cap = size(r)
+        trail = [(r["A"] == a[0], r["A"] == a[1], r["A"] == a[2], any("You thought then" in x for x in r["C"]),
+                  len(r["C"]), "- How it left you: bitter." in r["B"], any("You meant to" in x for x in r["B"]))
+                 for r in steps]
+        self.assertEqual(trail, [(False, True, False, True, 5, True, True),        # 1. A's quoted words
+                                 (False, False, True, True, 5, True, True),        # 2. A's minutes
+                                 (False, False, True, False, 5, True, True),       # 3. the older thought
+                                 (False, False, True, False, 4, True, True),       # 4. lowest weight: Elena's line
+                                 (False, False, True, False, 3, True, True),       # 5. then the self line (weight 4)
+                                 (False, False, True, False, 2, True, True),       # 6. then Daniel's (weight 5)
+                                 (False, False, True, False, 2, False, True),      # 7. B's feeling
+                                 (False, False, True, False, 2, False, False)])    # 8. B's intent
+        last = M.bounded(a, b, c, 0)
+        self.assertIn("- Two days ago Elena counted the pantry. Nobody has admitted taking it.", last["C"])
+        self.assertIn(b[1], last["B"])
+        # Thirty days of everything: C keeps at most 6 lines, the blocks at most 610, the prompt at most 2,420.
+        events, kinds = [], [("accuse", "accuse_leo", "leo"), ("eat", "eat", None), ("reassure", "reassure_leo", "leo"),
+                             ("sit", "sit_leo", "leo"), ("confront", "confront_leo", "leo"), ("give", "give_leo", "leo")]
+        for day in range(1, 31):
+            for i, (kind, option, target) in enumerate(kinds):
+                for actor in ("daniel", "elena", "mara", "leo"):
+                    if actor == target:
+                        continue
+                    events.append({"id": f"D{day}-{len(events) + 1:03d}", "scene": f"D{day}", "minute": 3 * i,
+                                   "kind": kind, "option": option, "actor": actor, "target": target,
+                                   "witnesses": {p: "saw" for p in data.ORDER} | {actor: "did"}})
+            events.append({"id": f"N{day}-01", "scene": f"N{day}", "minute": 90, "kind": "went_out", "actor": "daniel",
+                           "members": ["daniel"], "witnesses": {"daniel": "did", "leo": "knew"}})
+        c = self.handmade(events)
+        items = M.block_c(c, "leo", 3 + 33)
+        self.assertLessEqual(len(items), 6)
+        big_a = [CARRY_HEAD] + [f"- {'fact ' * 20}{i}." for i in range(12)]
+        big_a = [big_a[:1 + 11]] * 3
+        self.assertGreater(estimate_tokens("\n".join(big_a[0])), 300)
+        big_b = [B_HEAD] + [f'- About Daniel eating a portion: "{"word " * 29}end."'] * 3 + \
+                [f'- You meant to: "{"word " * 29}end."', "- How it left you: very tired."]
+        r = M.bounded(big_a, big_b, items, M.MEMORY_MAX)
+        self.assertLessEqual(estimate_tokens("\n".join(r["C"] + r["A"] + r["B"])), 610)
+        d = self.three_days(seed=2)
+        leo = d.day3.people["leo"]
+        d.day3.carry["leo"] = r["C"] + r["A"] + r["B"]
+        leo.memory += [(0, f"filler line number {i} " + "about nothing much at all " * 12) for i in range(200)]
+        self.assertLessEqual(estimate_tokens(SYSTEM + d.day3.prompt_for(leo, 0, d.day3.options_for(leo))), 2420)
+
+    # N-T8
+    def test_n_t8_day_words(self):
+        w = world.when_words
+        self.assertEqual([w(s, 6) for s in (("D", 2), ("N", 2), ("D", 1), ("N", 1))],
+                         ["yesterday", "last night", "two days ago", "the night before last"])
+        self.assertEqual([w(s, 7) for s in (("D", 1), ("N", 1), ("D", 2), ("N", 2))],
+                         ["three days ago", "three nights ago", "two days ago", "the night before last"])
+        d = self.three_days(seed=2, client=NightScripted({"daniel": ["go_next_door"]}, angry={"leo": "Daniel"}),
+                            draws1={**QUIET, "house": 0.1}, prefs2={})
+        leo, dan = d.day3.people["leo"], d.day3.people["daniel"]
+        text = d.day3.prompt_for(leo, 0, d.day3.options_for(leo))
+        self.assertIn("About the can: Daniel admitted taking it two days ago, at minute 33.", text)
+        self.assertIn("Against Daniel (a lot): two days ago, Daniel accused you of taking the can at minute", text)
+        self.assertRegex(text, r"you were angry with Daniel two days ago at minutes? ")
+        self.assertNotIn("yesterday, yesterday", text)
+        for p in d.day3.people.values():
+            for g in p.grudges.values():
+                for e in g.events:
+                    self.assertFalse(e[1].startswith(("yesterday, yesterday", "two days ago, yesterday")), e)
+        lines = d.day3.inside_lines(dan)
+        self.assertIn("About the can: you ate it yourself, and you admitted it two days ago.", lines)
+        self.assertIn("About the neighbour's house: you went in the night before last and found no food there. Outside is "
+                      "dangerous.", lines)
+        conscience = next(x for x in lines if x.startswith("On your conscience"))
+        self.assertIn("two days ago, you accused Leo of what you did, at minute 03", conscience)
+        # Suspicion minutes keep the day they were named on.
+        mara = d.day3.people["mara"]
+        mara.knows_culprit, mara.confessed = None, False
+        mara.suspicion.target, mara.suspicion.strength = "leo", 1
+        mara.suspected_past = [(("D", 1), [3]), (("N", 2), True)]
+        mara.suspected_at = [3]
+        about = next(x for x in d.day3.inside_lines(mara) if x.startswith("About the can"))
+        self.assertEqual(about, "About the can (a little): you thought Leo took it, two days ago at minute 03, and last "
+                                "night, and this morning at minute 03.")
+
+    # N-T9
+    def test_n_t9_the_chronicle(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+        ch = tr["chronicle"]
+        for e in ch["events"]:
+            self.assertLessEqual(set(e), EVENT_KEYS, e)
+            self.assertTrue(set(e["witnesses"].values()) <= WITNESS_MODES, e)
+        ids = [e["id"] for e in ch["events"]]
+        self.assertEqual(len(ids), len(set(ids)))
+        # Every model act that is not silence is an event of its day, with its actor as `did`.
+        for k, scene in ((1, "day1"), (2, "day2"), (3, "day3")):
+            for turn in tr[scene]["turns"]:
+                for a in turn["acts"]:
+                    if a["mode"] != "model" or a["option"] == "silent":
+                        continue
+                    e = [e for e in ch["events"] if e["scene"] == f"D{k}" and e["minute"] == turn["minute"]
+                         and e["actor"] == a["who"] and e["option"] == a["option"]]
+                    self.assertEqual(len(e), 1, (scene, turn["minute"], a["who"], a["option"]))
+                    self.assertEqual(e[0]["witnesses"][a["who"]], "did")
+        # Run again: the same chronicle, byte for byte.
+        dirs = Dirs()
+        try:
+            (meta2, code2), out2 = fake_morning(dirs, seed=1)
+            self.assertEqual(code2, 0, out2)
+            tr2 = json.loads(read(os.path.join(dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+            self.assertEqual(json.dumps(tr2["chronicle"]), json.dumps(ch))
+        finally:
+            dirs.cleanup()
+        # The neighbour's house is fixed once, at the first entry, and night 2 finds what night 1 left.
+        draws = {**QUIET, "house": 0.95, "trip:daniel": 0.1}
+        d = self.three_days(seed=2, client=NightScripted({"daniel": ["go_next_door"]}), draws1=draws, draws2=draws)
+        self.assertEqual((d.n1.house, d.n1.house_left), (6, 3))
+        self.assertEqual(d.chron.fixed["neighbour_house"]["scene"], "N1")
+        self.assertEqual(d.chron.fixed["neighbour_house"]["value"], 6)
+        self.assertEqual(d.chron.fixed["neighbour_house"]["string"], "2:night:house")
+        self.assertEqual((d.n2.groups[0]["found"], d.n2.groups[0]["took"], d.n2.house_left), (3, 3, 0))
+        # The draw strings (§4.4).
+        self.assertEqual((d.n1.draw_string("trip:daniel"), d.n2.draw_string("trip:daniel"), d.n2.draw_string("house")),
+                         ("2:night:trip:daniel", "2:night2:trip:daniel", "2:night:house"))
+        self.assertEqual((d.day1.order_string(4, "kitchen"), d.day2.order_string(4, "kitchen"),
+                          d.day3.order_string(4, "kitchen")), ("2:4:kitchen", "2:4:kitchen", "2:day3:4:kitchen"))
+        self.assertEqual((d.day2.food_string(4, "leo"), d.day3.food_string(4, "leo")),
+                         ("2:day2:food:4:leo", "2:day3:food:4:leo"))
+        self.assertIn("culprit", d.chron.fixed)
+
+    # N-T10
+    def test_n_t10_thoughts_stay_private(self):
+        (meta, code), out = fake_morning(self.dirs, seed=2)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed2.transcript.json")))
+        prompts = cached_prompts(self.dirs)
+        kept = [(pid, m["meaning"]) for night in ("mind1", "mind2") for pid, r in tr[night].items()
+                for m in r["memories"] if m["verdict"] == "kept"]
+        self.assertTrue(kept)
+        for pid, meaning in kept:
+            holders = {re.match(r"You are (\w+),", p).group(1).lower() for p in prompts if f'"{meaning}"' in p}
+            self.assertLessEqual(holders, {pid}, meaning)
+
+    # N-T11
+    def test_n_t11_the_plan_line_says_you_are(self):
+        client = NightScripted()
+        day1, oracle = self.v11_day1(3, client)
+        n = self.night.Night(day1, oracle).run()
+        day2 = Morning.next_day(day1, n, oracle)
+        ele, leo = day2.people["elena"], day2.people["leo"]
+        self.act(day2, ele, "send_leo", "Leo should.")
+        plan = next(x for x in day2.inside_lines(leo) if x.startswith("About going there tonight:"))
+        self.assertEqual(plan, "About going there tonight: Elena said you are the one who should go (min 00).")
+        plan = next(x for x in day2.inside_lines(day2.people["mara"]) if x.startswith("About going there tonight:"))
+        self.assertEqual(plan, "About going there tonight: Elena said Leo is the one who should go (min 00).")
+
+    # N-T12
+    def test_n_t12_schema_plumbing(self):
+        class Spy:
+            requests = 0
+
+            def __init__(self):
+                self.calls = []
+
+            def generate(self, system, prompt, schema=None):
+                self.calls.append(schema)
+                self.requests += 1
+                return "{}"
+        spy = Spy()
+        oracle = Oracle(Cache(self.path("spy")), "fake", 1, client=spy)
+        oracle.ask("s", "p1")
+        oracle.ask("s", "p2", schema={"type": "object"})
+        self.assertEqual(spy.calls, [None, {"type": "object"}])
+        self.assertEqual(Cache.key("m", 1, "s", "p"), frozen("v13", "gemini").Cache.key("m", 1, "s", "p"))
+        # The API gets RESPONSE_SCHEMA for decisions and the night mind's own for a night mind.
+        seen = []
+
+        class Api(StubApi):
+            def generate_content(self, model, contents, config):
+                seen.append(config.response_schema)
+                return super().generate_content(model, contents, config)
+        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": SECRET}):
+            client = GeminiClient({**json.loads(read(CONFIG)), "min_seconds_between_calls": 0}, 1, api=Api([]),
+                                  sleep=lambda s: None)
+            client.generate("s", "You are Leo, 21\nYour options:\n- silent: stay put")
+            schema = self.mind.schema(["D1-001", "N1-01"])
+            client.generate("s", "You are Leo, 21\n[D1-001] min 00: x\n" + MIND_END, schema=schema)
+        self.assertEqual(seen, [gemini.RESPONSE_SCHEMA, schema])
+        self.assertEqual(schema["properties"]["memories"]["items"]["properties"]["ids"]["items"]["enum"],
+                         ["D1-001", "N1-01"])
+        self.assertEqual(set(schema["required"]), {"memories", "feeling", "intent"})
+        # The fake answers a night mind in shape, citing ids of the prompt, and breaks every n-th answer.
+        fake = FakeClient(invalid_every=2)
+        prompt = "You are Leo, 21\n[D1-001] min 00: x\n[N1-01] tonight: y\n" + MIND_END
+        good = json.loads(fake.generate("s", prompt, schema=schema))
+        self.assertTrue(good["memories"] and set(good["memories"][0]["ids"]) <= {"D1-001", "N1-01"})
+        self.assertTrue(good["feeling"] and good["intent"])
+        bad = fake.generate("s", prompt, schema=schema)
+        c = self.handmade([{"id": "D1-001", "scene": "D1", "minute": 0, "kind": "opening", "actor": "elena",
+                            "witnesses": {"leo": "saw", "elena": "did"}},
+                           {"id": "N1-01", "scene": "N1", "minute": 90, "kind": "bedtime", "actor": "leo",
+                            "witnesses": {"leo": "did"}}])
+        r = self.mind.check_answer(bad, "leo", {"D1-001": "x", "N1-01": "y"}, c, ())
+        self.assertTrue(r["mode"] == "fallback" or not r["kept"], r)
+
+    # N-T13
+    def test_n_t13_counting(self):
+        (meta, code), out = fake_morning(self.dirs, seed=1)
+        self.assertEqual(code, 0, out)
+        tr = json.loads(read(os.path.join(self.dirs.runs, "daniel_ate_it-seed1.transcript.json")))
+        self.assertEqual(meta["night1_asks"], len(tr["night"]["decisions"]))
+        self.assertEqual(meta["night2_asks"], len(tr["night2"]["decisions"]))
+        self.assertEqual(meta["mind1_asks"], len(tr["mind1"]))
+        self.assertEqual(meta["mind2_asks"], len(tr["mind2"]))
+        for k in ("day2", "day3"):
+            self.assertEqual(meta[f"{k}_asks"], sum(a["mode"] != "routine" for t in tr[k]["turns"] for a in t["acts"]))
+        total = (meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night1_asks"] + meta["mind1_asks"]
+                 + meta["day2_asks"] + meta["night2_asks"] + meta["mind2_asks"] + meta["day3_asks"])
+        self.assertEqual(total, meta["answers_live"] + meta["answers_from_cache"])
+        for k in ("mind1", "mind2"):
+            m = meta[k]
+            self.assertEqual(m["memories_proposed"], m["memories_kept"] + m["memories_rejected"])
+            self.assertEqual(m["memories_proposed"], sum(len(r["memories"]) for r in tr[k].values()))
+        for key in ("night2_asks", "mind1_asks", "mind2_asks", "day3_asks"):
+            self.assertIn(f"{key}: {meta[key]}", out)
+
+    # N-T14
+    def test_n_t14_frozen_versions_still_replay(self):
+        for version in ("v14", "v13", "v12", "v11", "v10", "v9"):
+            done = run_check(version)
+            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
+            self.assertEqual(done.stdout.count("story IDENTICAL, transcript IDENTICAL"), 3, done.stdout)
+            self.assertIn("0 API calls", done.stdout)
+
+    # The amendment to §3.3's table C2: the kind acts between two people, at weight 3.
+    def test_amendment_kind_acts_between_two_people(self):
+        M = self.memory
+        self.assertEqual(M.KIND_ACTS, ("reassure", "sit"))
+        self.assertEqual({k: M.WEIGHT[k] for k in M.KIND_ACTS}, {"reassure": 3, "sit": 3})
+        everyone = {p: "saw" for p in data.ORDER}
+        c = self.handmade([
+            {"id": "D1-001", "scene": "D1", "minute": 3, "kind": "reassure", "option": "reassure_all", "actor": "daniel",
+             "witnesses": everyone | {"daniel": "did"}},
+            {"id": "D1-002", "scene": "D1", "minute": 6, "kind": "sit", "option": "sit_leo", "actor": "elena",
+             "target": "leo", "witnesses": everyone | {"elena": "did"}},
+            {"id": "D1-003", "scene": "D1", "minute": 9, "kind": "reassure", "option": "reassure_leo", "actor": "elena",
+             "target": "leo", "witnesses": everyone | {"elena": "did"}},
+            {"id": "D1-004", "scene": "D1", "minute": 12, "kind": "reassure", "option": "reassure_mara", "actor": "leo",
+             "target": "mara", "witnesses": everyone | {"leo": "did"}},
+            {"id": "D1-005", "scene": "D1", "minute": 15, "kind": "reassure", "option": "reassure_mara", "actor": "leo",
+             "target": "mara", "witnesses": everyone | {"leo": "did"}},
+            {"id": "D1-006", "scene": "D1", "minute": 18, "kind": "confess", "option": "confess", "actor": "daniel",
+             "witnesses": everyone | {"daniel": "did"}},
+        ])
+        lines = [x["line"] for x in M.block_c(c, "leo", 6)]
+        self.assertEqual(lines, ["Two days ago, Daniel admitted taking the can.",
+                                 "Two days ago, Elena sat with you.",              # a tie at 3 keeps the older
+                                 "Two days ago, you reassured Mara twice."])
+        lines = [x["line"] for x in M.block_c(c, "mara", 6)]
+        self.assertIn("Two days ago, Leo reassured you twice.", lines)
+        # Reassuring everyone is not an act between two people: Daniel's line is his confession, and nobody's
+        # line comes from reassure_all.
+        self.assertFalse([x for p in data.ORDER for x in M.block_c(c, p, 6) if "D1-001" in x["ids"]])
+
+
 class GeminiClientTest(unittest.TestCase):
     def setUp(self):
         self.old = os.environ.get("GEMINI_API_KEY")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 5090863..a981d83 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -116,6 +116,28 @@ def estimate_tokens(text, less=0):
     return int((len(text) - less) / 3.6) + 1
 
 
+NUMBER_WORDS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
+
+
+def day_index(day):
+    """The played day of a house day: day 4 is day 1 (reports/days_design.md)."""
+    return day - 3
+
+
+def when_words(scene, day):
+    """When a scene was, seen from the morning of house day `day` (reports/days_design.md, §3.5): scene is
+    ("D", k), the k-th played day, or ("N", k), the night after it."""
+    kind, k = scene
+    ago = day_index(day) - k
+    if kind == "D":
+        if ago <= 0:
+            return "this morning"
+        return {1: "yesterday", 2: "two days ago"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} days ago"
+    if ago <= 0:
+        return "tonight"
+    return {1: "last night", 2: "the night before last"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} nights ago"
+
+
 def strength(feeling):
     f = (feeling or "").lower()
     s = max((level for level, stems in SHOWN.items() if any(x in f for x in stems)), default=0)
@@ -226,8 +248,9 @@ def minutes_text(ms):
 
 def grudge_facts(name, events, limit=None):
     """The facts behind a grudge: each event the rules saw, then one line for the times the
-    person named them as who they were angry with. On day 2 an event carried from day 1 or the
-    night has a fourth element, "yesterday" or "last night" (reports/night_design.md, §5.3)."""
+    person named them as who they were angry with. An event carried from an earlier day or night
+    is (minute, text with its day word, kind, day word, scene, text) (reports/night_design.md, §5.3;
+    reports/days_design.md, §3.5): its words are written when the next morning is set up."""
     facts = [e[1] for e in events if e[2] == "event"]
     angry = [e for e in events if e[2] == "angry"]
     if limit:
@@ -236,13 +259,13 @@ def grudge_facts(name, events, limit=None):
         ms = [e[0] for e in angry]
         facts.append(f"you were angry with {name} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
     elif angry:
-        parts = []
-        for when in ("yesterday", "last night", "this morning"):
-            ms = [e[0] for e in angry if (e[3] if len(e) > 3 else "this morning") == when]
-            if not ms:
-                continue
-            parts.append(when if when == "last night" else
-                         f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
+        groups = {}             # day word -> (a night?, minutes), oldest first
+        for e in angry:
+            when = e[3] if len(e) > 3 else "this morning"
+            night = e[4][0] == "N" if len(e) > 4 else when == "last night"
+            groups.setdefault(when, (night, []))[1].append(e[0])
+        parts = [when if night else f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}"
+                 for when, (night, ms) in groups.items()]
         facts.append(f"you were angry with {name} " + "; and ".join(parts))
     return facts
 
@@ -310,6 +333,14 @@ class Person:
         # prompts; and on day 2, what of day 1 still counts as yesterday's (None on day 1).
         self.tonight = []
         self.yesterday = None
+        # Days that follow one another (reports/days_design.md, §3.5): the house day of their confession, of the
+        # confession they heard, of each denial and accusation heard; and the earlier days' suspicion minutes,
+        # as (scene, minutes, or True for a night).
+        self.confessed_day = None
+        self.confession_heard_day = None
+        self.denial_day = {}
+        self.accused_day = {}
+        self.suspected_past = []
         # The food moment (reports/body_design.md, §2): the minute they last ate this morning; on day 2,
         # the minute of yesterday's last meal (None: not since before yesterday); their last moment.
         self.last_meal = None
@@ -368,6 +399,11 @@ class Morning:
         self.trip_now = set()       # during the turn it starts: who is asked because of it
         self.food_turn = None       # day 2: the turn of the house's last food moment
         self.holding = None         # day 2: (who, from whom) while someone decides about a handed portion
+        # For the chronicle (reports/days_design.md, §4): act seq -> person -> {"memory": [...], "sure": [...]},
+        # the lines each of them got of it; act seq -> person -> the room whose voices they heard.
+        self.views = {}
+        self.voices_heard = {}
+        self.blocks = {}            # day 2 on: person -> the memory blocks A, B and C (reports/days_design.md, §3)
         if day != 4:
             return                  # day 2's opening is set up by next_day
         for p in self.people.values():
@@ -380,10 +416,21 @@ class Morning:
         self.started("kitchen", 0, "the count came up short", False)
 
     @classmethod
-    def next_day(cls, day1, night, oracle):
-        """Day 2, from day 1 and the night that followed it (reports/night_design.md, §5)."""
+    def next_day(cls, day1, night, oracle, chronicle=None):
+        """The next morning, from the day before and the night that followed it (reports/night_design.md, §5;
+        reports/days_design.md, §3, with the chronicle)."""
         import night as night_mod
-        return night_mod.next_day(day1, night, oracle)
+        return night_mod.next_day(day1, night, oracle, chronicle)
+
+    def order_string(self, t, room):
+        """The seed string of a room's turn order (reports/days_design.md, §4.4): days 1 and 2 share one."""
+        if self.day <= 5:
+            return f"{self.seed}:{t}:{room}"
+        return f"{self.seed}:day{day_index(self.day)}:{t}:{room}"
+
+    def food_string(self, t, pid):
+        """The seed string of a food moment's draw (reports/body_design.md, §2.1; days_design.md, §4.4)."""
+        return f"{self.seed}:day{day_index(self.day)}:food:{t}:{pid}"
 
     def started(self, room, minute, why, by_inner):
         if self.convos.new_thing(room, minute, why):
@@ -606,7 +653,8 @@ class Morning:
                 said = (f"{x} said nobody should go" if q is None else f"{x} said {q} must stay home"
                         if option else f"{x} said {q} should not go")
             elif kind == "back":
-                said = f"{x} said {q} is the one who should go" if option else f"{x} said {q} should go"
+                said = (f"{x} said {q} {'are' if q == 'you' else 'is'} the one who should go" if option
+                        else f"{x} said {q} should go")
             else:
                 said = f"{x} said {he} will not go"
             parts.append(f"{said} (min {minute:02d})")
@@ -700,7 +748,7 @@ class Morning:
 
     def food_draw(self, t, pid):
         """This person's draw for this turn (F9): a string of its own, so no draw depends on order."""
-        return random.Random(f"{self.seed}:day2:food:{t}:{pid}").random()
+        return random.Random(self.food_string(t, pid)).random()
 
     def food_due(self, p, t):
         """F1-F9 (§2.1): day 2, in the kitchen with food on the shelf and someone else there, starving,
@@ -817,21 +865,24 @@ class Morning:
         if "hunger" in self.risen(p):
             out.append("Since you last decided, you have grown hungrier.")
         s = p.suspicion
-        y = p.yesterday             # day 2 only (reports/night_design.md, §5.3)
-        # What they know about the can wins over what their answers guessed.
+        # What they know about the can wins over what their answers guessed. From day 2 on, a confession of an
+        # earlier day says when (reports/night_design.md, §5.3; reports/days_design.md, §3.5).
         if p.knows_culprit == p.id:
-            about = ("About the can: you ate it yourself, and you admitted it yesterday." if y and y["confessed"]
+            about = (f"About the can: you ate it yourself, and you admitted it "
+                     f"{when_words(('D', day_index(p.confessed_day)), self.day)}."
+                     if p.confessed and p.confessed_day not in (None, self.day)
                      else "About the can: you ate it yourself.")
-        elif p.knows_culprit and y and y["confession_heard"]:
-            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it yesterday, at minute "
+        elif p.knows_culprit and p.confession_heard_day not in (None, self.day):
+            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it "
+                     f"{when_words(('D', day_index(p.confession_heard_day)), self.day)}, at minute "
                      f"{p.confession_heard_at:02d}.")
         elif p.knows_culprit:
             about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it at minute "
                      f"{p.confession_heard_at:02d}.")
-        elif s.strength and y is not None:
+        elif s.strength and self.day != 4:
             when = []
-            for word, ms in (("yesterday", y["suspected_at"]), ("last night", y["suspected_last_night"]),
-                             ("this morning", p.suspected_at)):
+            past = [(when_words(scene, self.day), ms) for scene, ms in p.suspected_past]
+            for word, ms in past + [("this morning", p.suspected_at)]:
                 if ms is True:
                     when.append(word)
                 elif ms:
@@ -855,7 +906,7 @@ class Morning:
             out.append(f"Against {NAMES[t]} ({LEVEL_WORDS[g.strength]}): {facts}.")
         if p.guilt is not None:
             facts = ["you ate the can in the night, and nobody saw"]
-            facts += [fact for _, fact in p.guilt_events[-EVENTS_SHOWN:]]
+            facts += [e[1] for e in p.guilt_events[-EVENTS_SHOWN:]]
             out.append(f"On your conscience ({LEVEL_WORDS[p.guilt]}): " + "; ".join(facts) + ".")
         return out
 
@@ -1120,7 +1171,17 @@ class Morning:
             opt = d.pop("_opt")
             audience = [q.id for q in self.others_here(p)]
             self.acted.add(p.id)
+            before = {q.id: (len(q.memory), len(q.sure)) for q in self.people.values()}
             d["came_of_it"] = self.apply(p, opt, d, t, voices, record)
+            # What each person got of this act, in their own lines (reports/days_design.md, §2.3, §4.2).
+            got = {}
+            for q in self.people.values():
+                m0, s0 = before[q.id]
+                memory = [x for _, x in q.memory[m0:]]
+                sure = [x[8:] if x.startswith("min ") else x for x in q.sure[s0:]]
+                if memory or sure:
+                    got[q.id] = {"memory": memory, "sure": sure}
+            self.views[d["seq"]] = got
             record["decisions"].append(d)
             entry = {"minute": minute, "who": p.id, "room": room, "option": d["option"],
                      "words": d.get("say"), "audience": audience, "mode": d["mode"],
@@ -1137,7 +1198,7 @@ class Morning:
 
         for room in data.ROOMS:
             remaining = list(self.present[room])
-            rng = random.Random(f"{self.seed}:{t}:{room}")
+            rng = random.Random(self.order_string(t, room))
             draw = {q: rng.random() for q in data.ORDER}
             place = 0
             while remaining:
@@ -1181,10 +1242,11 @@ class Morning:
         # Voices carry to everyone who did not hear the words, wherever they are at the end of
         # the turn, never into or out of the bathroom. Only a new line is a social moment for
         # someone who hears it through a wall.
-        for room, new, heard_it in voices:
+        for room, new, heard_it, seq in voices:
             for q in self.people.values():
                 if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                     continue
+                self.voices_heard.setdefault(seq, {})[q.id] = room
                 line = f"Voices from the {data.ROOMS[room]}"
                 if (minute, line + ".") not in q.memory:
                     q.memory.append((minute, line + "."))
@@ -1198,6 +1260,9 @@ class Morning:
                 else:
                     text = f"{p.name} comes into the {data.ROOMS[to]}"
                 self.perceive(q, minute, text + ".", trigger=(text, True))
+                if p.history:            # seen as part of the act that moved them (reports/days_design.md, §4.2)
+                    view = self.views.setdefault(p.history[-1]["seq"], {})
+                    view.setdefault(q.id, {"memory": [], "sure": []})["memory"].append(text + ".")
             if there:
                 self.arrivals.append((to, p.name, self.moved_by_inner.get(p.id, False)))
         at_end = {r: sum(q.room == r for q in self.people.values()) for r in data.ROOMS}
@@ -1242,8 +1307,7 @@ class Morning:
         d["suspects_result"] = p.suspicion.report(suspect, minute)
         if p.suspicion.target != before:
             p.suspected_at = []
-            if p.yesterday is not None:
-                p.yesterday["suspected_at"], p.yesterday["suspected_last_night"] = [], False
+            p.suspected_past = []
         if suspect is not None and suspect == p.suspicion.target:
             p.suspected_at.append(minute)
         d["suspects_now"] = p.suspicion.short("suspicion")
@@ -1454,31 +1518,31 @@ class Morning:
                 if kind == "confess":
                     if q.knows_culprit is None:
                         q.confession_heard_at = minute
+                        q.confession_heard_day = self.day
                     q.knows_culprit = p.id
                     q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
                                   "(you heard it)")
-                    # Grudges: it was admitted after being denied to them, or after accusing them.
-                    # On day 2 a denial or accusation of day 1 is yesterday's (reports/night_design.md, §5.1).
-                    y = q.yesterday or {"denials": (), "accused_by": ()}
+                    # Grudges: it was admitted after being denied to them, or after accusing them. A denial or
+                    # accusation of an earlier day says when (reports/night_design.md, §5.1; days_design.md, §3.5).
+                    def at(day):
+                        return "at" if day in (None, self.day) else f"{when_words(('D', day_index(day)), self.day)} at"
                     if p.id in q.denials_heard:
-                        when = "yesterday at" if p.id in y["denials"] else "at"
+                        when = at(q.denial_day.get(p.id))
                         self.add_grudge(q, p, minute,
                                         f"{p.name} admitted taking it at minute {minute:02d}, after "
                                         f"denying it to you {when} minute {q.denials_heard[p.id]:02d}",
                                         f"{p.name} admitted it after denying it to {q.name}", record)
                     if p.id in q.accused_by:
-                        when = "yesterday at" if p.id in y["accused_by"] else "at"
+                        when = at(q.accused_day.get(p.id))
                         self.add_grudge(q, p, minute,
                                         f"{p.name} had accused you of it {when} minute {q.accused_by[p.id]:02d}",
                                         f"{p.name} had accused {q.name} of it", record)
                 if kind == "deny":
                     q.denials_heard[p.id] = minute
-                    if q.yesterday:
-                        q.yesterday["denials"].discard(p.id)
+                    q.denial_day[p.id] = self.day
                 if kind == "accuse" and q is target:
                     q.accused_by[p.id] = minute
-                    if q.yesterday:
-                        q.yesterday["accused_by"].discard(p.id)
+                    q.accused_day[p.id] = self.day
                     if q.id != self.culprit:        # a false accusation
                         self.add_grudge(q, p, minute,
                                         f"{p.name} accused you of taking the can at minute {minute:02d}, "
@@ -1496,7 +1560,7 @@ class Morning:
                     elif kind == "reassure" and target is culprit:
                         self.add_guilt(minute, f"{p.name} reassured you, at minute {minute:02d}",
                                        f"{p.name} reassured {pro['him']}", record)
-            voices.append((room, new, {p.id} | {q.id for q in seen}))
+            voices.append((room, new, {p.id} | {q.id for q in seen}, self.seq))
             mine = {"ask": "asked who took it", "deny": "denied taking it",
                     "accuse": f"accused {target.name if target else ''}", "confess": "admitted taking it",
                     "confront": f"confronted {target.name if target else ''}",
@@ -1539,6 +1603,7 @@ class Morning:
                 p.heard_question = True
             if kind == "confess":
                 p.confessed = True
+                p.confessed_day = self.day
                 p.sure.append(f"min {minute:02d}: you admitted aloud that you took the can"
                               + (f", in front of {', '.join(q.name for q in seen)}." if seen else "."))
             names = ", ".join(q.name for q in seen)
````

## 9. Scratch scripts

`$S/before_own.py`:

```python
"""Runs the bodies of N-T11 and N-T14 (which need no new module) on the code as it is, without DaysTest.setUp."""
import sys, unittest
sys.path.insert(0, ".")
import test_morning as T

class Own(unittest.TestCase):
    setUp = T.NightTest.setUp
    tearDown = T.NightTest.tearDown
    path = T.NightTest.path
    v11_day1 = T.NightTest.v11_day1
    act = T.NightTest.act
    test_n_t11_the_plan_line_says_you_are = T.DaysTest.test_n_t11_the_plan_line_says_you_are
    test_n_t14_frozen_versions_still_replay = T.DaysTest.test_n_t14_frozen_versions_still_replay

unittest.main(argv=["own", "-v"], exit=False)
```

`$S/replay_day1.py`:

```python
"""Read-only: day 1 of seeds 1-3 with the current code, from cache/v11 in replay mode (no client, no API), against
runs/v11; and the chronicle built on it, which must leave the story and transcript as they were."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from chronicle import Chronicle
from gemini import Cache, Oracle
from story import render
from world import Morning
for seed in (1, 2, 3):
    name = f"daniel_ate_it-seed{seed}"
    o = Oracle(Cache(f"cache/v11/gemini-3.5-flash-lite-{name}.json"), "gemini-3.5-flash-lite", seed, client=None, replay=True)
    m = Morning(o, seed).run()
    c = Chronicle(seed, m.culprit)
    c.add_day(m)
    text = render(m, seed, "gemini-3.5-flash-lite", f"python morning.py --seed {seed}")
    same_story = text.encode("utf-8") == open(f"runs/v11/{name}.md", "rb").read()
    same_tr = json.loads(json.dumps(m.transcript)) == json.load(open(f"runs/v11/{name}.transcript.json", encoding="utf-8"))
    print(f"{name}: day 1 replayed {o.from_cache} answers from cache/v11, {o.api_requests} API requests; "
          f"story {'IDENTICAL' if same_story else 'DIFFERS'} to runs/v11, transcript {'IDENTICAL' if same_tr else 'DIFFERS'}; "
          f"chronicle: {len(c.events)} day-1 events")
```

`$S/v1_replay.py`:

```python
"""Read-only: replays v1's three runs (runs/daniel_ate_it-seedN.md, cache/) with v1's own code in replay mode. Its
replay.md is written into a scratch copy of the run folder, never into the repo (as in food_confront_impl.md §6)."""
import io, contextlib, os, shutil, sys, tempfile
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "v1"))
from morning import run                                       # v1's own
tmp = tempfile.mkdtemp(prefix="v1-replay-")
for seed in (1, 2, 3):
    shutil.copy(os.path.join(ROOT, "runs", f"daniel_ate_it-seed{seed}.md"), tmp)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run(seed, replay=True, config_path=os.path.join(ROOT, "config.json"), runs_dir=tmp,
                     cache_dir=os.path.join(ROOT, "cache"))
    meta, code = result if isinstance(result, tuple) else (result, None)
    out = buf.getvalue()
    line = next((x.strip() for x in out.split("\n") if "byte for byte" in x), out.strip().split("\n")[-1])
    print(f"v1 seed {seed}: exit {code}; api_requests {meta.get('api_requests') if isinstance(meta, dict) else '?'}; "
          f"{'IDENTICAL' if 'IDENTICAL' in line else line}")
shutil.rmtree(tmp)
```

`$S/patch_world.py`:

```python
"""Patches world.py for reports/days_design.md: day words, views of each act, draw strings, the plan line."""
p = "world.py"
t = open(p, encoding="utf-8").read()


def sub(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:80], t.count(old))
    t = t.replace(old, new)


# Day words (days_design §3.5).
sub('''def strength(feeling):''', '''NUMBER_WORDS = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def day_index(day):
    """The played day of a house day: day 4 is day 1 (reports/days_design.md)."""
    return day - 3


def when_words(scene, day):
    """When a scene was, seen from the morning of house day `day` (reports/days_design.md, §3.5): scene is
    ("D", k), the k-th played day, or ("N", k), the night after it."""
    kind, k = scene
    ago = day_index(day) - k
    if kind == "D":
        if ago <= 0:
            return "this morning"
        return {1: "yesterday", 2: "two days ago"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} days ago"
    if ago <= 0:
        return "tonight"
    return {1: "last night", 2: "the night before last"}.get(ago) or f"{NUMBER_WORDS.get(ago, ago)} nights ago"


def strength(feeling):''')

# grudge_facts: group angry events by their day word, oldest first.
sub('''def grudge_facts(name, events, limit=None):
    """The facts behind a grudge: each event the rules saw, then one line for the times the
    person named them as who they were angry with. On day 2 an event carried from day 1 or the
    night has a fourth element, "yesterday" or "last night" (reports/night_design.md, §5.3)."""''',
    '''def grudge_facts(name, events, limit=None):
    """The facts behind a grudge: each event the rules saw, then one line for the times the
    person named them as who they were angry with. An event carried from an earlier day or night
    is (minute, text with its day word, kind, day word, scene, text) (reports/night_design.md, §5.3;
    reports/days_design.md, §3.5): its words are written when the next morning is set up."""''')
sub('''    elif angry:
        parts = []
        for when in ("yesterday", "last night", "this morning"):
            ms = [e[0] for e in angry if (e[3] if len(e) > 3 else "this morning") == when]
            if not ms:
                continue
            parts.append(when if when == "last night" else
                         f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}")
        facts.append(f"you were angry with {name} " + "; and ".join(parts))''',
    '''    elif angry:
        groups = {}             # day word -> (a night?, minutes), oldest first
        for e in angry:
            when = e[3] if len(e) > 3 else "this morning"
            night = e[4][0] == "N" if len(e) > 4 else when == "last night"
            groups.setdefault(when, (night, []))[1].append(e[0])
        parts = [when if night else f"{when} at minute{'s' if len(ms) > 1 else ''} {minutes_text(ms)}"
                 for when, (night, ms) in groups.items()]
        facts.append(f"you were angry with {name} " + "; and ".join(parts))''')

# Person: when things happened.
sub('''        self.tonight = []
        self.yesterday = None
''', '''        self.tonight = []
        self.yesterday = None
        # Days that follow one another (reports/days_design.md, §3.5): the house day of their confession, of the
        # confession they heard, of each denial and accusation heard; and the earlier days' suspicion minutes,
        # as (scene, minutes, or True for a night).
        self.confessed_day = None
        self.confession_heard_day = None
        self.denial_day = {}
        self.accused_day = {}
        self.suspected_past = []
''')

# Morning: views of each act, voices through walls, the blocks.
sub('''        self.holding = None         # day 2: (who, from whom) while someone decides about a handed portion
''', '''        self.holding = None         # day 2: (who, from whom) while someone decides about a handed portion
        # For the chronicle (reports/days_design.md, §4): act seq -> person -> {"memory": [...], "sure": [...]},
        # the lines each of them got of it; act seq -> person -> the room whose voices they heard.
        self.views = {}
        self.voices_heard = {}
        self.blocks = {}            # day 2 on: person -> the memory blocks A, B and C (reports/days_design.md, §3)
''')
sub('''    def started(self, room, minute, why, by_inner):''', '''    def order_string(self, t, room):
        """The seed string of a room's turn order (reports/days_design.md, §4.4): days 1 and 2 share one."""
        if self.day <= 5:
            return f"{self.seed}:{t}:{room}"
        return f"{self.seed}:day{day_index(self.day)}:{t}:{room}"

    def food_string(self, t, pid):
        """The seed string of a food moment's draw (reports/body_design.md, §2.1; days_design.md, §4.4)."""
        return f"{self.seed}:day{day_index(self.day)}:food:{t}:{pid}"

    def started(self, room, minute, why, by_inner):''')
sub('''        return random.Random(f"{self.seed}:day2:food:{t}:{pid}").random()''',
    '''        return random.Random(self.food_string(t, pid)).random()''')
sub('''            rng = random.Random(f"{self.seed}:{t}:{room}")''', '''            rng = random.Random(self.order_string(t, room))''')

# The plan line: "you are" (days_design §3.2).
sub('''                said = f"{x} said {q} is the one who should go" if option else f"{x} said {q} should go"''',
    '''                said = (f"{x} said {q} {'are' if q == 'you' else 'is'} the one who should go" if option
                        else f"{x} said {q} should go")''')

# inside_lines: the can, suspicion and conscience with computed day words.
sub('''        s = p.suspicion
        y = p.yesterday             # day 2 only (reports/night_design.md, §5.3)
        # What they know about the can wins over what their answers guessed.
        if p.knows_culprit == p.id:
            about = ("About the can: you ate it yourself, and you admitted it yesterday." if y and y["confessed"]
                     else "About the can: you ate it yourself.")
        elif p.knows_culprit and y and y["confession_heard"]:
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it yesterday, at minute "
                     f"{p.confession_heard_at:02d}.")''', '''        s = p.suspicion
        # What they know about the can wins over what their answers guessed. From day 2 on, a confession of an
        # earlier day says when (reports/night_design.md, §5.3; reports/days_design.md, §3.5).
        if p.knows_culprit == p.id:
            about = (f"About the can: you ate it yourself, and you admitted it "
                     f"{when_words(('D', day_index(p.confessed_day)), self.day)}."
                     if p.confessed and p.confessed_day not in (None, self.day)
                     else "About the can: you ate it yourself.")
        elif p.knows_culprit and p.confession_heard_day not in (None, self.day):
            about = (f"About the can: {NAMES[p.knows_culprit]} admitted taking it "
                     f"{when_words(('D', day_index(p.confession_heard_day)), self.day)}, at minute "
                     f"{p.confession_heard_at:02d}.")''')
sub('''        elif s.strength and y is not None:
            when = []
            for word, ms in (("yesterday", y["suspected_at"]), ("last night", y["suspected_last_night"]),
                             ("this morning", p.suspected_at)):''', '''        elif s.strength and self.day != 4:
            when = []
            past = [(when_words(scene, self.day), ms) for scene, ms in p.suspected_past]
            for word, ms in past + [("this morning", p.suspected_at)]:''')
sub('''            facts += [fact for _, fact in p.guilt_events[-EVENTS_SHOWN:]]''',
    '''            facts += [e[1] for e in p.guilt_events[-EVENTS_SHOWN:]]''')

# take_answer: a new suspect clears the earlier days' minutes too.
sub('''        if p.suspicion.target != before:
            p.suspected_at = []
            if p.yesterday is not None:
                p.yesterday["suspected_at"], p.yesterday["suspected_last_night"] = [], False''',
    '''        if p.suspicion.target != before:
            p.suspected_at = []
            p.suspected_past = []''')

# turn(): views, voices with their act, arrivals seen.
sub('''            audience = [q.id for q in self.others_here(p)]
            self.acted.add(p.id)
            d["came_of_it"] = self.apply(p, opt, d, t, voices, record)''', '''            audience = [q.id for q in self.others_here(p)]
            self.acted.add(p.id)
            before = {q.id: (len(q.memory), len(q.sure)) for q in self.people.values()}
            d["came_of_it"] = self.apply(p, opt, d, t, voices, record)
            # What each person got of this act, in their own lines (reports/days_design.md, §2.3, §4.2).
            got = {}
            for q in self.people.values():
                m0, s0 = before[q.id]
                memory = [x for _, x in q.memory[m0:]]
                sure = [x[8:] if x.startswith("min ") else x for x in q.sure[s0:]]
                if memory or sure:
                    got[q.id] = {"memory": memory, "sure": sure}
            self.views[d["seq"]] = got''')
sub('''        for room, new, heard_it in voices:
            for q in self.people.values():
                if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                    continue
''', '''        for room, new, heard_it, seq in voices:
            for q in self.people.values():
                if q.id in heard_it or q.room == room or q.room is None or data.SOUNDPROOF & {room, q.room}:
                    continue
                self.voices_heard.setdefault(seq, {})[q.id] = room
''')
sub('''                else:
                    text = f"{p.name} comes into the {data.ROOMS[to]}"
                self.perceive(q, minute, text + ".", trigger=(text, True))''', '''                else:
                    text = f"{p.name} comes into the {data.ROOMS[to]}"
                self.perceive(q, minute, text + ".", trigger=(text, True))
                if p.history:            # seen as part of the act that moved them (reports/days_design.md, §4.2)
                    view = self.views.setdefault(p.history[-1]["seq"], {})
                    view.setdefault(q.id, {"memory": [], "sure": []})["memory"].append(text + ".")''')
sub('''            voices.append((room, new, {p.id} | {q.id for q in seen}))''',
    '''            voices.append((room, new, {p.id} | {q.id for q in seen}, self.seq))''')

# apply(): when each confession, denial and accusation was heard.
sub('''                if kind == "confess":
                    if q.knows_culprit is None:
                        q.confession_heard_at = minute''', '''                if kind == "confess":
                    if q.knows_culprit is None:
                        q.confession_heard_at = minute
                        q.confession_heard_day = self.day''')
sub('''                    # Grudges: it was admitted after being denied to them, or after accusing them.
                    # On day 2 a denial or accusation of day 1 is yesterday's (reports/night_design.md, §5.1).
                    y = q.yesterday or {"denials": (), "accused_by": ()}
                    if p.id in q.denials_heard:
                        when = "yesterday at" if p.id in y["denials"] else "at"''', '''                    # Grudges: it was admitted after being denied to them, or after accusing them. A denial or
                    # accusation of an earlier day says when (reports/night_design.md, §5.1; days_design.md, §3.5).
                    def at(day):
                        return "at" if day in (None, self.day) else f"{when_words(('D', day_index(day)), self.day)} at"
                    if p.id in q.denials_heard:
                        when = at(q.denial_day.get(p.id))''')
sub('''                    if p.id in q.accused_by:
                        when = "yesterday at" if p.id in y["accused_by"] else "at"''', '''                    if p.id in q.accused_by:
                        when = at(q.accused_day.get(p.id))''')
sub('''                if kind == "deny":
                    q.denials_heard[p.id] = minute
                    if q.yesterday:
                        q.yesterday["denials"].discard(p.id)
                if kind == "accuse" and q is target:
                    q.accused_by[p.id] = minute
                    if q.yesterday:
                        q.yesterday["accused_by"].discard(p.id)''', '''                if kind == "deny":
                    q.denials_heard[p.id] = minute
                    q.denial_day[p.id] = self.day
                if kind == "accuse" and q is target:
                    q.accused_by[p.id] = minute
                    q.accused_day[p.id] = self.day''')
sub('''            if kind == "confess":
                p.confessed = True''', '''            if kind == "confess":
                p.confessed = True
                p.confessed_day = self.day''')
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("world.py patched")
```

`$S/patch_night.py`:

```python
"""Patches night.py for reports/days_design.md: a second night, the night's events for the chronicle, the house
fixed once, and the next morning from any day (blocks A, B and C)."""
p = "night.py"
t = open(p, encoding="utf-8").read()


def sub(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:90], t.count(old))
    t = t.replace(old, new)


sub('''`next_day` then hands day 2 each person as the night left them, with what they carry in: a block
of facts and conclusions the code writes from what they did, saw or heard.
"""''', '''`next_day` then hands day 2 each person as the night left them, with what they carry in: a block
of facts and conclusions the code writes from what they did, saw or heard.

Days that follow one another (reports/days_design.md): a night can be the second (`number`), finds the
neighbour's house as the last night left it, keeps whoever is away out of it, and records each thing that
happened as an event for the chronicle (chronicle.py), with each night line tied to the event it tells of.
`next_day` sets up day 3 the same way, and, given the chronicle, adds last night's thoughts (B) and the earlier
days (C) to what each person carries in (memory.py).
"""''')
sub('''from world import NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, estimate_tokens, portions_text''',
    '''from world import (NAMES, NIGHT_MINUTE, NIGHT_SYSTEM, NEIGHBOUR_UNKNOWN, Option, day_index, estimate_tokens,
                   portions_text, when_words)''')
sub('''TRIGGER = "the family is together in the kitchen for the first time since last night"''',
    '''TRIGGER = "the family is together in the kitchen for the first time since last night"
CARRY_VARIANTS = ((False, True), (True, True), (True, False))     # (short, minutes), in the order they are tried''')

# ---------- Night ----------
sub('''class Night:
    """One night. `draws` forces named draws (tests): "order" (a list of leavers), "house",
    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed."""

    def __init__(self, day1, oracle, draws=None):
        self.day1 = day1''', '''class Night:
    """One night. `draws` forces named draws (tests): "order" (a list of leavers), "house",
    "wake:L:R", "door:L:P", "return:L:P", "trip:L" and "lost:L"; any other is drawn from the seed.
    number: which night this is (reports/days_design.md, §1.3); house: the neighbour's house as the night
    before left it ({"value", "u", "left", "entered"}), so it is never drawn again."""

    def __init__(self, day1, oracle, draws=None, number=1, house=None):
        self.day1 = self.prev = day1            # the day this night follows
        self.number = number
        self.house_given = house''')
sub('''        self.groups = []
        self.away = set()''', '''        self.groups = []
        self.away = set(day1.away)  # whoever did not come back from an earlier night is not in the house
        self.entered = bool(house and house.get("entered"))
        self.events = []            # what happened, for the chronicle: dicts with "key", in order
        self.line_events = {p: [] for p in data.ORDER}    # the event each night line tells of''')
sub('''    def u(self, name):
        if name in self.draws:
            return self.draws[name]
        return random.Random(f"{self.seed}:night:{name}").random()

    def order(self):
        """Everyone, in the order they would leave: lowest draw first."""
        if "order" in self.draws:
            return list(self.draws["order"])
        rng = random.Random(f"{self.seed}:night:order")''', '''    def draw_string(self, name):
        """The seed string of a draw (reports/days_design.md, §4.4): the first night keeps night_design's;
        a later night has its own; the neighbour's house is one fact, whatever the night."""
        if self.number == 1 or name == "house":
            return f"{self.seed}:night:{name}"
        return f"{self.seed}:night{self.number}:{name}"

    def u(self, name):
        if name in self.draws:
            return self.draws[name]
        return random.Random(self.draw_string(name)).random()

    def house_state(self):
        """The neighbour's house as this night leaves it, for the next night (reports/days_design.md, §4.3)."""
        return {"value": self.house, "u": self.house_u, "left": self.house_left, "entered": self.entered}

    def order(self):
        """Everyone, in the order they would leave: lowest draw first."""
        if "order" in self.draws:
            return list(self.draws["order"])
        rng = random.Random(self.draw_string("order"))''')
sub('''    def line(self, pid, full, short=None):
        self.lines[pid].append(full)
        self.lines_short[pid].append(full if short is None else short)''', '''    def line(self, pid, full, short=None, event=None):
        self.lines[pid].append(full)
        self.lines_short[pid].append(full if short is None else short)
        self.line_events[pid].append(event)

    def event(self, kind, actor=None, witnesses=None, **more):
        """Something that happened tonight, for the chronicle; returns its key."""
        self.events.append({"key": len(self.events), "kind": kind, "actor": actor, "witnesses": dict(witnesses or {}),
                            **more})
        return len(self.events) - 1''')

# run(): away people stay out; bedtime events; the house given or drawn; who knew of each going out.
sub('''        for p in self.people.values():                                  # the gap (§2)
            p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
            p.activity = {"kind": "idle", "label": "in bed"}
        self.bedtime_hunger = {q: self.people[q].hunger for q in data.ORDER}''', '''        for p in self.people.values():                                  # the gap (§2)
            if p.id in self.away:
                p.room = None
                continue
            p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
            p.room = OWN_ROOM[p.id]
            p.activity = {"kind": "idle", "label": "in bed"}
        self.bedtime_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}''')
sub('''        for q in data.ORDER:                                            # bedtime (§3.2)
            room = OWN_ROOM[q]
            r = ROOMMATE[q]
            now = ["Now it is night. " + data.GAP,
                   f"Everyone has gone to bed in their own room: {BEDS}.",
                   f"You are in the {data.ROOMS[room]}, in your bed. {NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.",
                   f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]''', '''        present = [q for q in data.ORDER if q not in self.away]
        beds = BEDS if not self.away else ", ".join(
            " and ".join(NAMES[x] for x in present if x in owners) + f" in the {data.ROOMS[room]}"
            for room, owners in sorted(data.OWNERS.items(), key=lambda kv: min(data.ORDER.index(x) for x in kv[1]))
            if any(x in present for x in owners))
        for q in present:                                               # bedtime (§3.2)
            room = OWN_ROOM[q]
            r = ROOMMATE[q]
            mate = (f"{NAMES[r]}'s bed is empty." if r in self.away else
                    f"{NAMES[r]} is in {data.PRONOUNS[r]['his']} bed.")
            now = ["Now it is night. " + data.GAP,
                   (f"Everyone has gone to bed in their own room: {beds}." if not self.away else
                    f"Everyone in the house has gone to bed in their own room: {beds}."),
                   f"You are in the {data.ROOMS[room]}, in your bed. {mate}",
                   f"The kitchen is dark. The shelf holds {portions_text(self.portions)}."]''')
sub('''            self.people[q].tonight.append(TONIGHT[choice])
            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}")
        self.house_u = self.u("house")
        self.house = self.house_left = house_portions(self.house_u)''', '''            self.people[q].tonight.append(TONIGHT[choice])
            e = self.event("bedtime", q, {q: "did"}, option=choice)
            self.line(q, f"Last night you slept in the {data.ROOMS[room]} with {NAMES[r]}. {BED_LINE[choice]}", event=e)
        if self.house_given:                # fixed the night it first mattered, and as that night left it (§4.3)
            self.house, self.house_u = self.house_given["value"], self.house_given["u"]
            self.house_left = self.house_given["left"]
        else:
            self.house_u = self.u("house")
            self.house = self.house_left = house_portions(self.house_u)''')
sub('''        self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
        return self''', '''        self.morning_hunger = {q: (None if q in self.away else self.people[q].hunger) for q in data.ORDER}
        for e in self.events:               # who knew that someone went out (§4.2)
            if e["kind"] == "went_out":
                for P in data.ORDER:
                    if P not in e["members"] and any(x in self.knows[P] for x in e["members"]):
                        e["witnesses"].setdefault(P, "knew")
        return self''')

# leave(): the roommate sees L get up; the door sitter; the front door; going out.
sub('''            if noticed:
                self.awake[R] = True
                seen_by.add(R)
                self.knows[R].append(L)
                self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).")''', '''            if noticed:
                self.awake[R] = True
                seen_by.add(R)
                self.knows[R].append(L)
                e = self.event("got_up", L, {L: "did", R: "saw"})
                self.line(R, f"In the night {NAMES[L]} got up in the dark and left the room toward the kitchen and the "
                             f"front door ({'you saw it' if awake else 'you woke and saw it'}).", event=e)''')
sub('''        stops = []
        for S in data.ORDER:
            if self.where.get(S) != "kitchen" or S in group:
                continue
            self.notice(S, L, "door watch")
            seen_by.add(S)
            self.knows[S] += [x for x in group if x not in self.knows[S]]
            who = names(group)
            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).")''', '''        stops = []
        at_door = None
        for S in data.ORDER:
            if self.where.get(S) != "kitchen" or S in group:
                continue
            self.notice(S, L, "door watch")
            seen_by.add(S)
            self.knows[S] += [x for x in group if x not in self.knows[S]]
            who = names(group)
            if at_door is None:
                at_door = self.event("at_door", L, {x: "did" for x in group}, members=list(group))
            self.events[at_door]["witnesses"][S] = "saw"
            self.line(S, f"In the night {who} came into the kitchen and went to the front door (you saw it).",
                      event=at_door)''')
sub('''        # 3. The front door opens: everyone in a bedroom who has not seen L go.
        for P in data.ORDER:''', '''        # 3. The front door opens: everyone in a bedroom who has not seen L go.
        door = None
        for P in data.ORDER:''')
sub('''            self.awake[P] = True
            self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
                         f"You did not see who.")''', '''            self.awake[P] = True
            if door is None:
                door = self.event("door", L, {x: "did" for x in group}, members=list(group))
            self.events[door]["witnesses"][P] = "heard"
            self.line(P, f"In the night you {'' if awake else 'woke and '}heard the front door being opened. "
                         f"You did not see who.", event=door)''')
sub('''        # 4. The street.
        for P in group:
            self.where[P] = "out"
        self.leavers += group''', '''        # 4. The street.
        for P in group:
            self.where[P] = "out"
        self.leavers += group
        self.event("went_out", L, {x: "did" for x in group}, members=list(group))''')

# react_seen / react_heard: each reaction an event.
sub('''        waiting = P in pending
        choice, words = self.ask(P, "reaction", now, opts, fallback)
        if choice == f"go_with_{L}":
            join(P)
            self.line(P, f"You went with {him(L)}.")
            self.people[P].tonight.append(f"you went with {n}.")
        elif choice == f"stop_{L}":
            self.people[P].tonight.append(f"you told {n} not to go.")
            return P, words
        elif choice == "stay_home":
            pending.remove(P)
            self.line(P, f"You let {him(L)} go, and stayed in bed after all.")
        elif waiting:
            self.line(P, f"You let {him(L)} go, to go yourself later.")
        else:
            self.line(P, f"You let {him(L)} go without a word.")''', '''        waiting = P in pending
        choice, words = self.ask(P, "reaction", now, opts, fallback)
        e = None if choice == f"stop_{L}" else self.event("reaction", P, {P: "did"}, option=choice, target=L)
        if choice == f"go_with_{L}":
            join(P)
            self.line(P, f"You went with {him(L)}.", event=e)
            self.people[P].tonight.append(f"you went with {n}.")
        elif choice == f"stop_{L}":
            self.people[P].tonight.append(f"you told {n} not to go.")
            return P, words
        elif choice == "stay_home":
            pending.remove(P)
            self.line(P, f"You let {him(L)} go, and stayed in bed after all.", event=e)
        elif waiting:
            self.line(P, f"You let {him(L)} go, to go yourself later.", event=e)
        else:
            self.line(P, f"You let {him(L)} go without a word.", event=e)''')
sub('''            choice, _ = self.ask(P, "reaction", now, opts, "go_later")
            if choice == "go_after":
                join(P)
                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.")
            elif choice == "stay_home":
                pending.remove(P)
                self.line(P, "You stayed in bed after all.")
            else:
                self.line(P, "You waited, to go yourself later.")
            return''', '''            choice, _ = self.ask(P, "reaction", now, opts, "go_later")
            e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
            if choice == "go_after":
                join(P)
                self.line(P, f"You followed whoever it was: it was {NAMES[L]}.", event=e)
            elif choice == "stay_home":
                pending.remove(P)
                self.line(P, "You stayed in bed after all.", event=e)
            else:
                self.line(P, "You waited, to go yourself later.", event=e)
            return''')
sub('''        choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
        if choice == "get_up_and_look":''', '''        choice, _ = self.ask(P, "reaction", now, opts, "stay_in_bed")
        e = self.event("reaction", P, {P: "did"}, option=choice, target=L)
        if choice == "get_up_and_look":''')
sub('''        else:
            self.line(P, "You stayed in bed.")

    def answer(self, L, stops, place, group):''', '''        else:
            self.line(P, "You stayed in bed.", event=e)

    def answer(self, L, stops, place, group):''')

# answer(): each stop an event, and the answer.
sub('''        choice, a = self.ask(L, "answer", now, opts, "go_anyway")
        goes = choice == "go_anyway"
        went = "went all the same" if goes else "went back to bed"
        said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
        told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
                        for S, w in stops)
        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.")
        He = he(L).capitalize()
        for S, w in stops:
            told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
            answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.")''', '''        choice, a = self.ask(L, "answer", now, opts, "go_anyway")
        goes = choice == "go_anyway"
        went = "went all the same" if goes else "went back to bed"
        stop_events = [self.event("stop", S, {S: "did", L: "heard"}, option=f"stop_{L}", target=L, words=w)
                       for S, w in stops]
        self.event("answer", L, {L: "did", **{S: "heard" for S, _ in stops}}, option=choice, words=a,
                   target=stops[0][0])
        said = f' You answered: "{a}", and {went}.' if a else f" You {went}."
        told = " ".join(f"{NAMES[S]} told you, low, not to go: {quoted(w)}" if w else f"{NAMES[S]} told you, low, not to go."
                        for S, w in stops)
        self.line(L, told + said, " ".join(f"{NAMES[S]} told you, low, not to go." for S, _ in stops) + f" You {went}.",
                  event=stop_events[0])
        He = he(L).capitalize()
        for (S, w), e in zip(stops, stop_events):
            told = f"You told {NAMES[L]}, low, not to go" + (f": {quoted(w)}" if w else ".")
            answered = f' {He} answered: "{a}", and {went}.' if a else f" {He} {went}."
            self.line(S, told + answered, f"You told {NAMES[L]}, low, not to go. {He} {went}.", event=e)''')
sub('''            if P in talkers or w in (None, "out", place) or not self.awake[P]:
                continue
            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.")''', '''            if P in talkers or w in (None, "out", place) or not self.awake[P]:
                continue
            self.events[stop_events[0]]["witnesses"][P] = "voices"
            self.line(P, f"In the night you heard low voices from the {data.ROOMS[place]}.", event=stop_events[0])''')

# trip(): the street, and the return, as events; the house entered.
sub('''        g["outcome"] = outcome_class(st, found)
        self.groups.append(g)
        back = [x for x in group if x != g["lost"]]
        k, F = g["took"], g["found"]''', '''        g["outcome"] = outcome_class(st, found)
        self.groups.append(g)
        if st in ("clean", "scare_back"):
            self.entered = True
        street_e = self.event("street", L, {x: "did" for x in group}, members=list(group), outcome=g["outcome"])
        back = [x for x in group if x != g["lost"]]
        return_e = self.event("return", L, {x: "did" for x in back}, members=list(back)) if back else None
        k, F = g["took"], g["found"]''')
sub('''                took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
                self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
                             f"Nothing troubled you in the street.")
            elif st == "clean":
                self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
                             "the street.")
            elif st == "scare_there":
                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.")
            elif st == "scare_back":
                got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
                self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
                             f"street, and you ran the rest of the way.")
            else:
                self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
                             f"and came back without {him(g['lost'])}.")
            self.line(P, "You came back in by the front door before dawn"
                      + (f" and put the {portions_text(k)} on the shelf." if k else "."))''', '''                took = (f"You took {k}; {rest} {'is' if rest == 1 else 'are'} still there." if rest else "You took all of it.")
                self.line(P, f"You got inside the neighbour's house and found {portions_text(F)} of food. {took} "
                             f"Nothing troubled you in the street.", event=street_e)
            elif st == "clean":
                self.line(P, "You got inside the neighbour's house and found no food there. Nothing troubled you in "
                             "the street.", event=street_e)
            elif st == "scare_there":
                self.line(P, "On the way there, something was moving in the street. You ran back without getting inside.",
                          event=street_e)
            elif st == "scare_back":
                got = (f"and found {portions_text(F)} of food and took {k}" if F else "but found no food")
                self.line(P, f"You got inside the neighbour's house {got}. On the way back, something was moving in the "
                             f"street, and you ran the rest of the way.", event=street_e)
            else:
                self.line(P, f"In the street, something was moving. You lost sight of {NAMES[g['lost']]} in the dark "
                             f"and came back without {him(g['lost'])}.", event=street_e)
            self.line(P, "You came back in by the front door before dawn"
                      + (f" and put the {portions_text(k)} on the shelf." if k else "."), event=return_e)''')
sub('''            if w == "kitchen":
                self.notice(P, L, "return")
                self.knows[P] += [x for x in back if x not in self.knows[P]]
                self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
                             f"(you saw it).")
            elif self.awake[P]:
                self.notice(P, L, "return")
                self.line(P, "Before dawn you heard the front door again. You did not see who.")
            else:
                draw = self.u(f"return:{L}:{P}")
                woke = draw < wake_door(P)
                self.notice(P, L, "return", draw, wake_door(P), woke)
                if woke:
                    self.awake[P] = True
                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.")''', '''            if w == "kitchen":
                self.notice(P, L, "return")
                self.knows[P] += [x for x in back if x not in self.knows[P]]
                self.events[return_e]["witnesses"][P] = "saw"
                self.line(P, f"Before dawn {names(back)} came back in{alone} by the front door{carrying}{shaken} "
                             f"(you saw it).", event=return_e)
            elif self.awake[P]:
                self.notice(P, L, "return")
                self.events[return_e]["witnesses"][P] = "heard"
                self.line(P, "Before dawn you heard the front door again. You did not see who.", event=return_e)
            else:
                draw = self.u(f"return:{L}:{P}")
                woke = draw < wake_door(P)
                self.notice(P, L, "return", draw, wake_door(P), woke)
                if woke:
                    self.awake[P] = True
                    self.events[return_e]["witnesses"][P] = "heard"
                    self.line(P, "Before dawn you woke and heard the front door again. You did not see who.",
                              event=return_e)''')
sub('''                "noticing": self.noticing, "groups": self.groups,
                "lines": self.lines}''', '''                "noticing": self.noticing, "groups": self.groups,
                "lines": self.lines,
                # Days that follow one another (reports/days_design.md, §4.2): which night, what happened, and the
                # event each night line tells of.
                "number": self.number, "events": self.events, "line_events": self.line_events}''')

# ---------- day 2 and after ----------
sub('''def bounded_carry_in(day1, n, p):
    """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
    for short, minutes in ((False, True), (True, True), (True, False)):
        block = carry_in(day1, n, p, short, minutes)
        if estimate_tokens("\\n".join(block)) <= CARRY_IN_MAX:
            break
    return block


def neighbour_line(n, pid):
    """Their "About the neighbour's house:" line on day 2 (§5.3)."""
    v = n.visit.get(pid)
    if v:
        if v["got_in"] and v["found"]:
            rest = v["found"] - v["took"]
            left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
            return (f"About the neighbour's house: you went in last night and found {portions_text(v['found'])}; "
                    f"you brought back {v['took']}{left}. Outside is dangerous.")
        if v["got_in"]:
            return "About the neighbour's house: you went in last night and found no food there. Outside is dangerous."
        return "About the neighbour's house: you did not get inside last night. Outside is dangerous."
    known = [x for x in n.knows[pid] if x != pid]
    if not known:
        return NEIGHBOUR_UNKNOWN
    x = known[0]
    g = next(g for g in n.groups if x in g["members"])
    if x in n.away:
        how = " and has not come back"
    else:
        how = " and came back with food" if g["took"] else " and came back with nothing"
    return f"About the neighbour's house: {NAMES[x]} went there last night{how}. Outside is dangerous."


def next_day(day1, n, oracle):
    """Day 2: a Morning of day 5 with each person as the night left them (§5.1)."""
    m = world.Morning(oracle, day1.seed, day1.scenario, day=5)
    m.people = n.people
    m.portions = m.start_portions = n.portions
    m.away = set(n.away)
    m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
    present = [q for q in data.ORDER if q not in m.away]
    before, after = n.day1.portions, n.portions
    for q in data.ORDER:
        p = m.people[q]
        m.carry[q] = bounded_carry_in(day1, n, p)
        m.neighbour[q] = neighbour_line(n, q)''', '''def bounded_carry_in(day1, n, p):
    """The block within CARRY_IN_MAX: the quoted night words go first, then the accusations' minutes."""
    return carry_variants(day1, n, p)[0]


def carry_variants(prev, n, p):
    """Block A as it can be trimmed (reports/days_design.md, §3.4): from the first form within CARRY_IN_MAX, then
    the shorter ones. Day 2's is night_design's carry-in; a later day's is carry_in_later."""
    make = carry_in if prev.day == 4 else carry_in_later
    blocks = [make(prev, n, p, short, minutes) for short, minutes in CARRY_VARIANTS]
    first = next((i for i, b in enumerate(blocks) if estimate_tokens("\\n".join(b)) <= CARRY_IN_MAX), 2)
    blocks = blocks[first:]
    return blocks + [blocks[-1]] * (3 - len(blocks))


def carry_in_later(prev, n, p, short=False, minutes=True):
    """Block A from day 3 on (reports/days_design.md, §3.2, lines Y1-Y8): yesterday's facts as p had them, then
    their own night. `prev` is yesterday's Morning, as it ended."""
    out = [f"Yesterday morning the shelf held {portions_text(prev.start_portions)}."]
    if p.confessed and p.confessed_day == prev.day:                               # Y2
        sure = next(x for x in p.sure if "you admitted aloud that you took the can" in x)
        front = sure.split(", in front of ", 1)[1].rstrip(".").split(", ") if ", in front of " in sure else None
        out.append(f"You admitted at minute {sure[4:6]} that you took the can"
                   + (f", in front of {names([q for q in data.ORDER if NAMES[q] in front])}." if front else "."))
    elif p.knows_culprit and p.knows_culprit != p.id and p.confession_heard_day == prev.day:
        sure = next(x for x in p.sure if " admitted taking the can: " in x)
        words = sure.split(" admitted taking the can: ", 1)[1].rsplit(" (you heard it)", 1)[0]
        after = ", after denying it to you" if p.knows_culprit in p.denials_heard else ""
        out.append(f"{NAMES[p.knows_culprit]} admitted taking the can at minute {p.confession_heard_at:02d}{after}: "
                   f"{words} (you heard it).")
    for label, prefix, verb in (("Accusations", "accuse_", "accused"), ("Confrontations", "confront_", "confronted")):
        acts = {}                                                                 # Y3, Y4
        for turn in prev.transcript["turns"]:
            for a in turn["acts"]:
                if a["option"].startswith(prefix) and (a["who"] == p.id or p.id in a["audience"]):
                    acts.setdefault((a["who"], a["option"][len(prefix):]), []).append(turn["minute"])
        if acts:
            parts = []
            for (a, tgt), ms in acts.items():
                times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
                when = f" (min {', '.join(f'{x:02d}' for x in ms)})" if minutes else ""
                parts.append(f"{'you' if a == p.id else NAMES[a]} {verb} {'you' if tgt == p.id else NAMES[tgt]}{times}{when}")
            out.append(f"{label}: " + "; ".join(parts) + ".")
    for x in p.sure:                                                              # Y5
        if x[8:].startswith("you finished searching the "):
            out.append(f"You searched the {x[8 + len('you finished searching the '):].split(':')[0]} at minute "
                       f"{x[4:6]} and found nothing.")
    ate = {}                                                                      # Y6
    for x in p.sure:
        if " ate one of the portions" in x:
            mm, rest = x[4:6], x[8:]
            ate.setdefault(mm, []).append("you" if rest.startswith("you ate") else rest.split(" ate one")[0])
    for mm, who in ate.items():
        mine = "you" in who
        who = (["You"] if mine else []) + [w for w in who if w != "you"]
        each = " each" if len(who) > 1 else ""
        out.append(f"{' and '.join(who)} ate a portion{each} at minute {mm}" + ("." if mine else " (you saw it)."))
    for x in p.sure:
        mm, rest = x[4:6], x[8:]
        g = re.match(r"^(\\w+) gave one of the portions to (\\w+), and \\w+ (ate it|put it back on the shelf)", rest)
        if g:
            giver = "You" if g.group(1) == "you" else g.group(1)
            done = "ate it" if g.group(3) == "ate it" else "put it back"
            out.append(f"{giver} gave {g.group(2)} a portion at minute {mm}, and {g.group(2)} {done}"
                       + ("." if giver == "You" else " (you saw it)."))
            continue
        g = re.match(r"^(\\w+) gave you one of the portions, and you (ate it|put it back on the shelf)", rest)
        if g:
            done = "ate it" if g.group(2) == "ate it" else "put it back"
            out.append(f"{g.group(1)} gave you a portion at minute {mm}, and you {done}.")
            continue
        if rest.startswith("you shared out the last "):
            out.append(f"You shared out the food at minute {mm}.")
        elif " shares out the last " in rest and rest.endswith("you had your part."):
            out.append(f"{rest.split(' shares out the last ')[0]} shared out the food at minute {mm}; you had your part.")
    plan = prev.heard_plan(p)                                                     # Y7
    if plan:
        out.append("About going to the neighbour's house last night, where it was left: "
                   + plan[len("About going there tonight: "):])
    out.append(data.GAP)                                                          # Y8
    out += (n.lines_short if short else n.lines)[p.id]
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]


def neighbour_line(n, pid, history=None, day=None, away=None):
    """Their "About the neighbour's house:" line (night_design §5.3): their own visit on any night outranks one
    they know of, and a later night outranks an earlier one (reports/days_design.md, §3.5)."""
    history = history or [n]
    day = day or n.prev.day + 1
    away = n.away if away is None else away
    for night in reversed(history):
        v = night.visit.get(pid)
        if not v:
            continue
        when = when_words(("N", night.number), day)
        if v["got_in"] and v["found"]:
            rest = v["found"] - v["took"]
            left = f", and {rest} {'is' if rest == 1 else 'are'} still there" if rest else ", and none are left there"
            return (f"About the neighbour's house: you went in {when} and found {portions_text(v['found'])}; "
                    f"you brought back {v['took']}{left}. Outside is dangerous.")
        if v["got_in"]:
            return f"About the neighbour's house: you went in {when} and found no food there. Outside is dangerous."
        return f"About the neighbour's house: you did not get inside {when}. Outside is dangerous."
    for night in reversed(history):
        known = [x for x in night.knows[pid] if x != pid]
        if not known:
            continue
        x = known[0]
        g = next(g for g in night.groups if x in g["members"])
        if x in away:
            how = " and has not come back"
        else:
            how = " and came back with food" if g["took"] else " and came back with nothing"
        return (f"About the neighbour's house: {NAMES[x]} went there {when_words(('N', night.number), day)}{how}. "
                f"Outside is dangerous.")
    return NEIGHBOUR_UNKNOWN


def tag_events(p, k, day):
    """Grudge and guilt events keep the scene they happened in, and their day words are written for `day`
    (reports/days_design.md, §3.5): (minute, text with its word, kind, word, scene, text) for a grudge,
    (minute, text with its word, scene, text) for guilt. k: the played day that has just ended."""
    for g in p.grudges.values():
        events = []
        for e in g.events:
            scene, raw = ((("N", k) if e[0] >= NIGHT_MINUTE else ("D", k)), e[1]) if len(e) == 3 else (e[4], e[5])
            word = when_words(scene, day)
            events.append((e[0], f"{word}, {raw}" if e[2] == "event" else raw, e[2], word, scene, raw))
        g.events = events
    tagged = []
    for e in p.guilt_events:
        scene, raw = ((("N", k) if e[0] >= NIGHT_MINUTE else ("D", k)), e[1]) if len(e) == 2 else (e[2], e[3])
        tagged.append((e[0], f"{when_words(scene, day)}, {raw}", scene, raw))
    p.guilt_events = tagged


def next_day(day1, n, oracle, chronicle=None):
    """The next morning: a Morning of the next house day with each person as the night left them (§5.1). `day1` is
    the day the night followed. Given the chronicle, each person also carries last night's thoughts (B) and, from
    day 3 on, the earlier days (C), under one bound with A (reports/days_design.md, §3)."""
    import memory
    day = day1.day + 1
    k = day_index(day1.day)
    m = world.Morning(oracle, day1.seed, day1.scenario, day=day)
    m.people = n.people
    m.portions = m.start_portions = n.portions
    m.away = set(n.away)
    m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}
    present = [q for q in data.ORDER if q not in m.away]
    before, after = n.day1.portions, n.portions
    history = chronicle.nights if chronicle is not None and chronicle.nights else [n]
    for q in data.ORDER:
        p = m.people[q]
        variants = carry_variants(day1, n, p)
        if chronicle is None:
            m.carry[q] = variants[0]
            m.blocks[q] = {"A": variants[0], "B": [], "C": [], "earlier": []}
        else:
            b_items = memory.b_items(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
            b = memory.block_b(chronicle.minds.get(n.number, {}).get(q), chronicle, q)
            c = memory.block_c(chronicle, q, day, away=m.away) if day >= 6 else []
            r = memory.bounded(variants, b, c, memory.MEMORY_MAX)
            m.carry[q] = r["C"] + r["A"] + r["B"]
            earlier = [(it["ids"][:3], it["line"] + (f' You thought then: "{it["thought"]}"' if it.get("thought") else ""))
                       for it in r["C_items"] if it.get("ids")]
            earlier += [(ids, line) for ids, line in b_items if f"- {line}" in r["B"]]
            m.blocks[q] = {"A": r["A"], "B": r["B"], "C": r["C"], "earlier": earlier}
        m.neighbour[q] = neighbour_line(n, q, history, day, m.away)''')
sub('''        p.yesterday = {"confessed": p.confessed,
                       "confession_heard": bool(p.knows_culprit and p.knows_culprit != p.id),
                       "suspected_at": [mm for mm in p.suspected_at if mm < NIGHT_MINUTE],
                       "suspected_last_night": any(mm >= NIGHT_MINUTE for mm in p.suspected_at),
                       "denials": set(p.denials_heard),
                       "accused_by": set(p.accused_by)}
        for g in p.grudges.values():
            g.events = [(e[0], ("yesterday, " + e[1]) if e[2] == "event" else e[1], e[2],
                         "last night" if e[0] >= NIGHT_MINUTE else "yesterday") for e in g.events]
            g.last_change = 0
        p.suspicion.last_fall = 0
        p.suspected_at = []
        p.guilt_events = [(mm, "yesterday, " + fact) for mm, fact in p.guilt_events]''', '''        # The suspicion minutes of the day that ended, and of its night, keep their scene (§3.5).
        day_ms = [mm for mm in p.suspected_at if mm < NIGHT_MINUTE]
        if day_ms:
            p.suspected_past.append((("D", k), day_ms))
        if any(mm >= NIGHT_MINUTE for mm in p.suspected_at):
            p.suspected_past.append((("N", k), True))
        tag_events(p, k, day)
        for g in p.grudges.values():
            g.last_change = 0
        p.suspicion.last_fall = 0
        p.suspected_at = []''')
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("night.py patched")
t = open(p, encoding="utf-8").read()
sub('''import copy
import json
import random
''', '''import copy
import json
import random
import re
''')
sub('''        pending = [q for q in self.order() if self.choices[q] == "go_next_door"]''',
    '''        pending = [q for q in self.order() if self.choices.get(q) == "go_next_door"]''')
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("night.py imports and leaving order patched")
```

`$S/patch_tests.py`:

```python
"""Updates the six existing tests whose expectations change with days 2-3 (listed in reports/days_impl.md)."""
p = "test_morning.py"
t = open(p, encoding="utf-8").read()


def sub(old, new, n=1):
    global t
    assert t.count(old) == n, (old[:90], t.count(old))
    t = t.replace(old, new)


# FakeMorningTest: the cap counts each scene apart.
sub('''        self.assertLessEqual(meta["api_requests"], 150)
        self.assertGreater(meta["day1"]["model_decisions"], 0)''', '''        # The call cap counts each scene apart (reports/night_design.md, §8; days_design.md, §2.1).
        for scene in ("day1", "night", "mind1", "day2", "night2", "mind2", "day3"):
            self.assertLessEqual(meta[scene]["api_requests"], 150, scene)
        self.assertGreater(meta["day1"]["model_decisions"], 0)''')

# Witness T4: the night's own front-door lines may say "woke and heard" and "did not see who"; nothing else may.
sub('''        daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
        self.assertTrue(daniel)
        for p in daniel:
            for words in (NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can",''', '''        daniel = [p for p in self.fake_prompts() if p.startswith("You are Daniel,")]
        self.assertTrue(daniel)
        for p in daniel:
            # From the second night on, Daniel can himself wake at the front door (reports/days_design.md): those
            # lines are the night's, not Leo's can.
            p = "\\n".join(x for x in p.split("\\n") if "the front door" not in x)
            for words in (NOTE, OLD_NOTE, HEARD, "woke and heard", "wakes and hears", "open a can",''')

# Witness T5: day 3's words for the days before (reports/days_design.md, §3.5).
sub('''                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3).
                self.assertRegex(lines[0][:-len(" " + NOTE)],
                                 r"^About the can(: you have not settled on who took it\\."
                                 r"| \\([a-z ]+\\): you thought \\w+ took it, at minutes? [\\d, and]+\\."
                                 r"| \\([a-z ]+\\): you thought \\w+ took it(, (and )?(yesterday at minutes? [\\d, and]+"
                                 r"|last night|this morning at minutes? [\\d, and]+))*\\."
                                 r"|: \\w+ admitted taking it( yesterday,)? at minute \\d\\d\\.)$")''', '''                # Day 2's forms say "yesterday", "last night" or "this morning" (reports/night_design.md, §5.3); day 3's
                # also "two days ago" and "the night before last" (reports/days_design.md, §3.5).
                day = r"(yesterday|two days ago|\\w+ days ago)"
                night = r"(last night|the night before last|\\w+ nights ago)"
                self.assertRegex(lines[0][:-len(" " + NOTE)],
                                 r"^About the can(: you have not settled on who took it\\."
                                 r"| \\([a-z ]+\\): you thought \\w+ took it, at minutes? [\\d, and]+\\."
                                 rf"| \\([a-z ]+\\): you thought \\w+ took it(, (and )?({day} at minutes? [\\d, and]+"
                                 rf"|{night}|this morning at minutes? [\\d, and]+))*\\."
                                 rf"|: \\w+ admitted taking it( {day},)? at minute \\d\\d\\.)$")''')

# NightTest T1: the transcript holds the new scenes and the chronicle.
sub('''        self.assertEqual(set(tr), {"day1", "night", "day2"})''',
    '''        self.assertEqual(set(tr), {"day1", "night", "mind1", "day2", "night2", "mind2", "day3", "chronicle"})''')

# NightTest T12: a second night's prompts and day 3's carry the memory blocks, bounded together (days_design §3.4).
sub('''def without_blocks(prompt):
    """A day-2 or night prompt without its trip block and its carry-in block."""
    out, skipping = [], False
    for line in prompt.split("\\n"):
        if line == CARRY_HEAD:
            skipping = True
            continue''', '''def without_blocks(prompt):
    """A day-2 or night prompt without its trip block and its carry-in block (from day 3 on, the memory blocks A, B
    and C: reports/days_design.md, §3)."""
    out, skipping = [], False
    for line in prompt.split("\\n"):
        if line in (CARRY_HEAD, B_HEAD, EARLIER):
            skipping = True
            continue''')
sub('''            if "\\nNow it is night" in p:
                night_n += 1
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p), 1450 + TRIP_BLOCK_MAX)
            elif CARRY_HEAD in p:
                day2_n += 1
                self.assertLess(estimate_tokens(SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + CARRY_MAX)''', '''            # A second night's prompts carry day 2's blocks; every morning's blocks are bounded together at most at
            # MEMORY_HARD (reports/days_design.md, §3.4).
            if "\\nNow it is night" in p:
                night_n += 1
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(world.NIGHT_SYSTEM + p),
                                1450 + TRIP_BLOCK_MAX + (MEMORY_HARD if CARRY_HEAD in p else 0))
            elif CARRY_HEAD in p:
                day2_n += 1
                self.assertLess(estimate_tokens(SYSTEM + without_blocks(p)), 1450)
                self.assertLess(estimate_tokens(SYSTEM + p), 1450 + TRIP_BLOCK_MAX + MEMORY_HARD)''')
sub('''CARRY_HEAD = "Yesterday and last night:"
CARRY_MAX = 360''', '''CARRY_HEAD = "Yesterday and last night:"
CARRY_MAX = 360
MEMORY_HARD = 610           # blocks A, B and C at most, once trimmed (reports/days_design.md, §3.4)''')

# NightTest T13: the asks of every scene.
sub('''        self.assertEqual(meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night_asks"]
                         + meta["day2_asks"], meta["answers_live"] + meta["answers_from_cache"])''',
    '''        self.assertEqual(meta["day1"]["model_decisions"] + meta["day1"]["fallbacks"] + meta["night_asks"]
                         + meta["day2_asks"] + meta["mind1_asks"] + meta["night2_asks"] + meta["mind2_asks"]
                         + meta["day3_asks"], meta["answers_live"] + meta["answers_from_cache"])''')
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("tests updated")
```

## 10. Commands, in order

From `Prototypes/llm-morning/` unless shown, all with `GEMINI_API_KEY` unset.
1. From the repo root: append the North Star section to `CLAUDE.md`; commit `65ff403`.
2. `mkdir v14 && cp data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py night.py story.py
   talk.py world.py v14/`. Then `git show HEAD:…/<file> | cmp - v14/<file>` for each: "all copies identical to
   HEAD".
3. `v14/check.py` written. `--out` default v15. `.gitignore` gets v15's fake runs. `python v14/check.py`: IDENTICAL
   ×3. Commit `ecd8b3a`.
4. `DaysTest` written; `NightScripted` taught to answer night minds.
   `python -m unittest -v test_morning.DaysTest`: 15 errors (§5.1).
   `$S/before_own.py`: N-T11 fails, N-T14 passes (§5.2).
5. N-T8's day-7 scenes corrected (§4.1).
6. The change: `gemini.py`, `world.py` (`$S/patch_world.py`), `night.py` (`$S/patch_night.py`), `chronicle.py`,
   `memory.py`, `mind.py`, `story.py`, `morning.py`.
   - One fake run wrote to `C:\c\Users\…\scratchpad\days\fake`: a POSIX scratchpad path was given to Windows Python
     inside a `-c` string.
   - That folder held only that run's four files, created minutes before. They were moved into the scratchpad, and
     the emptied folders removed with `rmdir`.
7. `DaysTest`, three runs (§4.2), with the fixes of §4.3 and the corrections of §4.1. Then 15 OK.
8. The full suite: 6 failures (§6). `$S/patch_tests.py` updates them. Those tests: 13 OK. The full suite: 178 OK.
9. The replays (§7). Commit `a2e1cdf`. `git status`: the three old replay files only.
