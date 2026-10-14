# Block C keeps a repeated act: the pattern rule

Mode: implement. No API was called. Every command ran with `GEMINI_API_KEY` unset, or in replay mode, which
cannot reach a client. No cache was regenerated or written, and no model prompt text was edited.

Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad, which holds the read-only scripts
of §7.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | A test on the real seed 3 day-1 chronicle fails before and passes after; Daniel and Mara each get a pattern line in their day-3 C, with the chronicle's count | **PASS** | `test_c_pattern_seed3_day1_denials_and_questions`: FAIL before (`'Two days ago, you denied taking the can 6 times.' not found in [] : daniel`), ok after. §6.1, §6.2. |
| 2 | A test shows the rule does not fire at 2 repeats | **PASS** | `test_c_pattern_not_at_two_repeats`, ok. It also passed before the change, since then nothing fired at any count. §6.1, §6.2. |
| 3 | Full suite passes | **PASS** | `Ran 180 tests in 217.162s`, `OK`, exit 0. §6.3. |
| 4 | Replays of v9 to v14 IDENTICAL | **PASS** | 18 of 18 IDENTICAL, 0 API calls. §6.4. |
| 5 | Seed 3's largest day-3 prompt at most 1.10 × day 2's | **PASS** | 2,037 → **2,191** estimated: ratio **1.076** (it was 2,162, ratio 1.061). §4, §6.5. |

## 1. The rule

`memory.py:20-25`, `:124-128`, `:212-214`:

- **Which acts:** three kinds, each counted by the option that starts it:
  - `deny` (option `deny`);
  - `ask` (option `ask_who`);
  - `search` (option `search`). A search carried on (`keep_searching`) is the same search, not another one.
- **When:** one person does that act **3 or more times in one day** (`PATTERN_MIN = 3`). Counts are per scene:
  2 on day 1 and 2 on day 2 is never 3.
- **What it counts:** the events of that day that the reader of the block perceived. This is the same rule as
  every other C line (`block_c` reads only events with the reader among the witnesses). In seed 3 everyone
  witnessed every denial and every question, so every count is the chronicle's count.
- **Its line:** a fixed template, the count by `times()`, as the accusation lines already use it:
  - `<When>, <Q> denied taking the can <n times>.` / `<When>, you denied taking the can <n times>.`
  - `<When>, <Q> asked who took the can <n times>.` / `<When>, you asked …`
  - `<When>, <Q> searched for the can <n times>.` / `<When>, you searched …`
- **Its weight:** 3, set from `WEIGHT["accuse"]` (`memory.py:25`). Nothing else in `WEIGHT` changed.
- **How it fits C:** it is one more candidate in C2's existing choice: one line per person, the heaviest, and the
  older at equal weight. So C keeps its bound of 2 + 4 lines, and the existing trimming order (`bounded`) still
  applies.

**Not covered:** other kinds outside the table, e.g. `say`, `object`, `volunteer`, `propose`, `go`. The brief named
denials, "who took it?" and searches. Any other kind would need its own template.

## 2. Arguing against it first (CLAUDE.md, "Judging changes")

- **Would a real person remember it?**
  - Six denials to your face, the same morning: yes. A family says "you lied to our faces" days later.
  - Six "who took it?" from Mara: yes. Repeated insistence is what people remember about each other.
  - Three searches: weaker, but still a fact a person would have seen.
  - Two of anything: often not. The threshold at 3 follows that.
- **Is an exact count human?** No, but it is a mechanism. C's accusation lines already say "4 times". The
  output is the model's speech, which states no count unless it chooses to.
- **Does a line describing an act make the small model do that act?** (North Star)
  - Daniel's day-3 C now says "you denied taking the can 6 times".
  - His A block says he admitted it at minute 33 of day 2, and both are facts of the past. The line states a
    situation; it is not an option.
  - Whether it pulls him toward denying again can be seen only in a live run. None was made (MODE implement).
- **Does it state anything false?** No. Each line is the chronicle's act and count, with its day word. "Two days
  ago" also fixes when it happened, which is the kind of extent M2's two failures got wrong ("for days").

## 3. Diff summary

```
$ git diff --stat
 Prototypes/llm-morning/memory.py       | 12 ++++++++++
 Prototypes/llm-morning/test_morning.py | 41 ++++++++++++++++++++++++++++++++++
 2 files changed, 53 insertions(+)
```

`memory.py`:
- **New constants:** `PATTERNS` (kind → the option that starts it) and `PATTERN_MIN = 3`. `WEIGHT` gets the three
  kinds, each at `WEIGHT["accuse"]`.
- **`block_c`:** a starting act of a pattern kind is grouped under `(actor, kind, scene)`. After grouping, pattern
  groups with fewer than 3 events are dropped.
- **`person_line`:** the three templates.
- **Unchanged:** no other weight, and no other block (A, B, the bound, standing lines, thoughts).

`test_morning.py`, in `DaysTest`: two new tests (§6.1).

No file under `v1/` to `v14/`, `cache/` or `runs/` was touched:

```
$ git status --short
 M memory.py
 M test_morning.py
?? reports/c_patterns.md
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```

(The three `runs/v6/*.replay.md` files were untracked before this work began.)

## 4. How M3 was measured offline

Day 3's prompts depend on day 3's answers, and the cache holds those only for the old prompts. So `$S/c_replay.py`
replays seed 3 from `cache/v15` as follows:
1. Day 1, night 1, mind 1, day 2, night 2 and mind 2 replay as cached. C does not exist before day 3, so their
   prompts are unchanged: all 135 were found.
2. Day 3 is built with the new code. Each day-3 prompt is looked up with that person's new memory block swapped
   back to the old one, which is saved from the code before the change. So day 3 runs on the same 18 answers.
3. The largest prompt is `Morning.max_prompt_tokens`, set inside `prompt_for` by `world.estimate_tokens`, the
   same estimator the run used.

**Checks that the method is exact:**
- **Before the change:** the replay gives day 2 = 2,037 and day 3 = 2,162, both equal to `runs/v15`'s meta. Its
  day-3 transcript is IDENTICAL to `runs/v15`'s.
- **After the change:**
  - all 18 day-3 asks were found with the swap;
  - the day-3 transcript differs from `runs/v15`'s **only** in `carry_in`, the memory block itself (`$S/c_diff.py`).
  - The memory block is outside the prompt budget (`world.py:1015`, `:1024`, `:1034`), so a longer block cuts no other line.
    The prompt grows by exactly the block's growth.
- **Switching the rule off** (`PATTERNS = {}`) gives a seed 3 memory block byte for byte the one saved before the
  change (`cmp`, §6.5).

**Result:**

| Seed | Day 2 largest, estimated | Day 3 largest, estimated, before | Day 3 largest, estimated, after | Ratio after |
|---|---|---|---|---|
| 3 | 2,037 | 2,162 | **2,191** | **1.076** |
| 1 (for the record) | 2,101 | 2,144 | 2,144 | 1.020 (no block changed) |
| 2 (for the record) | 2,085 | 2,144 | 2,158 | 1.035 |

## 5. The new day-3 block C, seed 3, all four people

As the prompt carries it, after the bound (`$S/c_replay.py after`, §6.5). Before the change, all four were empty.

**Daniel**
```
What stays with you from earlier days:
- Two days ago, you denied taking the can 6 times. You thought then: "I had to lie to protect them from knowing the truth about the can."
- Two days ago, Elena asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.
```

**Elena**
```
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, you asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.
```

**Leo**
```
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, Elena asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.
```

**Mara**
```
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, Elena asked who took the can three times.
- Two days ago, you asked who took the can 6 times.
```

**What came with them:**
- **Elena** also gets a line. She asked "who took it?" three times on day 1 (D1-003, D1-014, D1-018). The rule
  applies to everyone, and the brief's test does not exclude her.
- **Leo** gets no line about himself. On day 1 he asked once, started one search and took trip positions, and
  none of these reaches 3.
- **Night-1 thoughts are back:**
  - Daniel's mind-1 memory cites D1-004, a denial, so it rides on his own line. The v15 report (§5) recorded it
    as lost by day 3.
  - Mara's mind-1 memory cites D1-002, one of her questions, so it attached to her own line too: "I only
    wanted someone to tell us the truth so we could stop guessing."
- **Mara's block hit the bound.** With the thought, her A + B + C is **561** estimated tokens even after A drops
  its minutes, against `MEMORY_MAX = 560`. So `bounded` trimmed in its fixed order:
  1. A's quoted night words (she had none);
  2. **A's minutes**: her Accusations and Confrontations lines lost their "(min …)" lists;
  3. **her older thought**, which brought her to 536.
  - No line was dropped. Her B is unchanged.
  - The other three blocks are untrimmed: Daniel 532, Elena 498, Leo 536. (`$S/c_bound.py`, §6.5)

**Seed 2, for the record:** every person's C gains "Leo denied taking the can 4 times" (or "you denied …" for
Leo), as a third line. Mara's three questions on day 1 do not show: her line stays her eating (weight 4). Nothing
was trimmed. **Seed 1:** no C changed. Elena and Mara asked or denied only twice, and everyone already had a
heavier line.

## 6. Commands and raw output

From `Prototypes/llm-morning/`. `$S` = `C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\78f61fe4-2d67-47e7-980d-db8a042af872\scratchpad`.

### 6.0 Baseline, before any code change

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" before
replayed 153 answers from cache/v15, 0 API calls; day 3: 18 asks, 0 found with the old carry swapped back; day-3 transcript IDENTICAL to runs/v15
day 2 largest prompt, estimated: 2037 (meta: 2037)
day 3 largest prompt, estimated: 2162 (meta: 2162)
ratio day 3 / day 2: 1.061 (M3 limit 1.10)

--- daniel: day-3 block C (0 lines; memory block 1628 chars)
(no C)

--- elena: day-3 block C (0 lines; memory block 1589 chars)
(no C)

--- leo: day-3 block C (0 lines; memory block 1726 chars)
(no C)

--- mara: day-3 block C (0 lines; memory block 1829 chars)
(no C)
```

### 6.1 The tests, before the change (RED)

- **`test_c_pattern_seed3_day1_denials_and_questions`:**
  - It loads `runs/v15/daniel_ate_it-seed3.transcript.json`'s chronicle into a `Chronicle`.
  - It counts Daniel's `deny` and Mara's and Elena's `ask_who` on D1 from that chronicle: 6, 6, 3.
  - It asserts that each of the four day-3 Cs (house day 6) holds the three lines with those counts, "you" for
    the reader's own.
  - It also asserts the weight of the pattern kinds is the weight of `accuse`.
- **`test_c_pattern_not_at_two_repeats`:**
  - A handmade chronicle. Day 1: Daniel denies twice, Mara asks twice and starts two searches, Leo starts one
    search and carries it on twice. Day 2: one more of each of Daniel's and Mara's.
  - It asserts no person line in anyone's C on day 3 (house day 6) or day 4 (house day 7).
  - Standing lines (the can) are left out of the comparison: they are not the rule's.

The first RED run of the second test failed for the wrong reason: the can's standing line. It was fixed to compare
person lines only, and the weight check was moved after the line checks, so the first test fails on its lines:

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning.DaysTest.test_c_pattern_seed3_day1_denials_and_questions test_morning.DaysTest.test_c_pattern_not_at_two_repeats
F.
======================================================================
FAIL: test_c_pattern_seed3_day1_denials_and_questions (test_morning.DaysTest.test_c_pattern_seed3_day1_denials_and_questions)
v15 seed 3's day 1 was Daniel's denials and Mara's "who took it?", none in the table: on day 3 every C
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4288, in test_c_pattern_seed3_day1_denials_and_questions
    self.assertIn(f"Two days ago, {d} taking the can {n(denied)}.", lines, pid)
AssertionError: 'Two days ago, you denied taking the can 6 times.' not found in [] : daniel

----------------------------------------------------------------------
Ran 2 tests in 0.024s

FAILED (failures=1)
```

### 6.2 The tests, after the change (GREEN)

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.DaysTest.test_c_pattern_seed3_day1_denials_and_questions test_morning.DaysTest.test_c_pattern_not_at_two_repeats
test_c_pattern_seed3_day1_denials_and_questions (test_morning.DaysTest.test_c_pattern_seed3_day1_denials_and_questions)
v15 seed 3's day 1 was Daniel's denials and Mara's "who took it?", none in the table: on day 3 every C ... ok
test_c_pattern_not_at_two_repeats (test_morning.DaysTest.test_c_pattern_not_at_two_repeats) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.026s

OK
```

### 6.3 The full suite

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
.......................................................    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
.    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
............................................................................................................................
----------------------------------------------------------------------
Ran 180 tests in 217.162s

OK
exit 0
```

The `[429 RESOURCE_EXHAUSTED]` lines are GeminiClientTest's stub API (key `SENTINEL-not-a-real-key-7731`), not real requests.

### 6.4 The frozen versions, v14 to v9

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v14/check.py; echo "exit $?"
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v13/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v12/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v11/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v10/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v9/check.py; echo "exit $?"
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit 0
```

### 6.5 M3, the new blocks, and what the bound did

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" after
people whose day-3 memory block changed: ['daniel', 'elena', 'leo', 'mara']
replayed 153 answers from cache/v15, 0 API calls; day 3: 18 asks, 18 found with the old carry swapped back; day-3 transcript DIFFERS to runs/v15
day 2 largest prompt, estimated: 2037 (meta: 2037)
day 3 largest prompt, estimated: 2191 (meta: 2162)
ratio day 3 / day 2: 1.076 (M3 limit 1.10)

--- daniel: day-3 block C (4 lines; memory block 1916 chars)
What stays with you from earlier days:
- Two days ago, you denied taking the can 6 times. You thought then: "I had to lie to protect them from knowing the truth about the can."
- Two days ago, Elena asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.

--- elena: day-3 block C (4 lines; memory block 1791 chars)
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, you asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.

--- leo: day-3 block C (4 lines; memory block 1930 chars)
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, Elena asked who took the can three times.
- Two days ago, Mara asked who took the can 6 times.

--- mara: day-3 block C (4 lines; memory block 1930 chars)
What stays with you from earlier days:
- Two days ago, Daniel denied taking the can 6 times.
- Two days ago, Elena asked who took the can three times.
- Two days ago, you asked who took the can 6 times.
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_bound.py" after 3
daniel: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 532 (MEMORY_MAX 560), untrimmed 532
elena: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 498 (MEMORY_MAX 560), untrimmed 498
leo: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 536 (MEMORY_MAX 560), untrimmed 536
mara: A+B unchanged: False; C as rendered == C untrimmed: False; estimated tokens: A+B+C 536 (MEMORY_MAX 560), untrimmed 561
   untrimmed C:
   What stays with you from earlier days:
   - Two days ago, Daniel denied taking the can 6 times.
   - Two days ago, Elena asked who took the can three times.
   - Two days ago, you asked who took the can 6 times. You thought then: "I only wanted someone to tell us the truth so we could stop guessing."

mara: old memory block -> new memory block (A and B lines only)
   --- 
   +++ 
   @@ -4,2 +4,2 @@
   -- Accusations: Daniel accused Leo 4 times (min 18, 21, 27, 30); you accused Leo three times (min 21, 24, 30); you accused Daniel twice (min 33, 75).
   -- Confrontations: you confronted Daniel 5 times (min 36, 39, 48, 51, 57); Leo confronted Daniel three times (min 36, 39, 54); Daniel confronted Leo (min 39).
   +- Accusations: Daniel accused Leo 4 times; you accused Leo three times; you accused Daniel twice.
   +- Confrontations: you confronted Daniel 5 times; Leo confronted Daniel three times; Daniel confronted Leo.
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_diff.py" | grep -v '^   ' | sed -E 's/\[[0-9]+\].*//' | sort | uniq -c
     17 day3/carry_in/daniel
      1 day3/carry_in/daniel len 17 21
     18 day3/carry_in/elena
      1 day3/carry_in/elena len 18 22
     18 day3/carry_in/leo
      1 day3/carry_in/leo len 18 22
     18 day3/carry_in/mara
      1 day3/carry_in/mara len 18 22
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" off 3 | head -4
replayed 153 answers from cache/v15, 0 API calls; day 3: 18 asks, 0 found with the old carry swapped back; day-3 transcript IDENTICAL to runs/v15
day 2 largest prompt, estimated: 2037 (meta: 2037)
day 3 largest prompt, estimated: 2162 (meta: 2162)
ratio day 3 / day 2: 1.061 (M3 limit 1.10)
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" off 1 | head -4
replayed 137 answers from cache/v15, 0 API calls; day 3: 38 asks, 0 found with the old carry swapped back; day-3 transcript IDENTICAL to runs/v15
day 2 largest prompt, estimated: 2101 (meta: 2101)
day 3 largest prompt, estimated: 2144 (meta: 2144)
ratio day 3 / day 2: 1.020 (M3 limit 1.10)
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" off 2 | head -4
replayed 109 answers from cache/v15, 0 API calls; day 3: 13 asks, 0 found with the old carry swapped back; day-3 transcript IDENTICAL to runs/v15
day 2 largest prompt, estimated: 2085 (meta: 2085)
day 3 largest prompt, estimated: 2144 (meta: 2144)
ratio day 3 / day 2: 1.028 (M3 limit 1.10)
$ cmp "$S/carry_before.json" "$S/carry_off_seed3.json" && echo same
same
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" after 1
people whose day-3 memory block changed: []
replayed 137 answers from cache/v15, 0 API calls; day 3: 38 asks, 0 found with the old carry swapped back; day-3 transcript IDENTICAL to runs/v15
day 2 largest prompt, estimated: 2101 (meta: 2101)
day 3 largest prompt, estimated: 2144 (meta: 2144)
ratio day 3 / day 2: 1.020 (M3 limit 1.10)

--- daniel: day-3 block C (5 lines; memory block 1209 chars)
What stays with you from earlier days:
- Two days ago, you admitted taking the can, in front of everyone.
- Two days ago, Elena reassured you twice.
- Two days ago, Leo ate a portion in front of you.
- Two days ago, Mara ate a portion in front of you.

--- elena: day-3 block C (5 lines; memory block 1513 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can. You thought then: "Daniel confessed to taking the can and I told him we would get through this together."
- Two days ago, you reassured Daniel twice. You thought then: "Daniel confessed to taking the can and I told him we would get through this together."
- Two days ago, Leo ate a portion in front of you.
- Two days ago, Mara ate a portion in front of you.

--- leo: day-3 block C (4 lines; memory block 1225 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can. You thought then: "Daniel took the food in the night because he was starving, but there is no use in punishing him now that it is done."
- Two days ago, you ate a portion in front of the others.
- Two days ago, Mara ate a portion in front of you.

--- mara: day-3 block C (4 lines; memory block 1150 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can.
- Two days ago, Leo ate a portion in front of you. You thought then: "Leo ate a portion right in front of me while I was starving."
- Two days ago, you ate a portion in front of the others.
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_replay.py" after 2
people whose day-3 memory block changed: ['daniel', 'elena', 'leo', 'mara']
replayed 109 answers from cache/v15, 0 API calls; day 3: 13 asks, 13 found with the old carry swapped back; day-3 transcript DIFFERS to runs/v15
day 2 largest prompt, estimated: 2085 (meta: 2085)
day 3 largest prompt, estimated: 2158 (meta: 2144)
ratio day 3 / day 2: 1.035 (M3 limit 1.10)

--- daniel: day-3 block C (4 lines; memory block 1790 chars)
What stays with you from earlier days:
- Two days ago, you admitted taking the can, in front of everyone. You thought then: "I accused Leo when I was the one who ate the can in the night, and my false pride made me lie to them for too long."
- Two days ago, Leo denied taking the can 4 times.
- Two days ago, Mara ate a portion in front of you.

--- elena: day-3 block C (4 lines; memory block 1427 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel took the can in the night and had to confess to us all."
- Two days ago, Leo denied taking the can 4 times.
- Two days ago, Mara ate a portion in front of you.

--- leo: day-3 block C (4 lines; memory block 1801 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you, after accusing you of it. You thought then: "Daniel spent hours accusing me of taking the can before finally admitting he took it himself."
- Two days ago, you denied taking the can 4 times.
- Two days ago, Mara ate a portion in front of you.

--- mara: day-3 block C (4 lines; memory block 1808 chars)
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all morning and only confessed because he had no other choice."
- Two days ago, Leo denied taking the can 4 times.
- Two days ago, you ate a portion in front of the others.
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/c_bound.py" after 2
daniel: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 497 (MEMORY_MAX 560), untrimmed 497
elena: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 397 (MEMORY_MAX 560), untrimmed 397
leo: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 501 (MEMORY_MAX 560), untrimmed 501
mara: A+B unchanged: True; C as rendered == C untrimmed: True; estimated tokens: A+B+C 502 (MEMORY_MAX 560), untrimmed 502

mara: old memory block -> new memory block (A and B lines only)
```

## 7. Scripts

All read-only, in `$S`.

**`$S/c_replay.py`**

```python
"""A seed of v15 (3 by default), replayed from cache/v15 with no API: day 1 to mind 2 as cached, then day 3.

    python c_replay.py before        the code before the change: day 3 replays from the cache as-is; saves each
                                     person's day-3 memory block (carry) to carry_before.json (seed 3)
    python c_replay.py off SEED      the new code with the pattern rule switched off (PATTERNS = {}): the same, saved
                                     to carry_off_seed<N>.json
    python c_replay.py after [SEED]  the new code: each day-3 prompt is looked up in the cache with the person's new
                                     carry swapped back for the saved old one, so day 3 runs on the same answers;
                                     prints the day-2 and day-3 largest prompt estimates (world.estimate_tokens, as
                                     the run counts them) and each person's day-3 block C.

Reads only; writes nothing outside this scratchpad (the cache is never written in replay).
"""
import json
import os
import sys

ROOT = r"C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning"
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

import data                                   # noqa: E402
from chronicle import Chronicle               # noqa: E402
from gemini import Cache, Oracle              # noqa: E402
from mind import NightMind                    # noqa: E402
from night import Night                       # noqa: E402
from world import Morning                     # noqa: E402

import memory                                 # noqa: E402

SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 3
MODEL, NAME = "gemini-3.5-flash-lite", f"daniel_ate_it-seed{SEED}"
SAVED = os.path.join(HERE, "carry_before.json" if SEED == 3 else f"carry_off_seed{SEED}.json")


class Swapped(Oracle):
    """Replay; a prompt not in the cache is tried again with each person's new carry put back to the old one."""
    swap = {}
    swapped = 0

    def ask(self, system, prompt, schema=None):
        key = Cache.key(self.model_name, self.seed, system, prompt)
        if self.cache.get(key) is None:
            for new, old in self.swap.items():
                if new in prompt:
                    prompt = prompt.replace(new, old)
                    self.swapped += 1
                    break
        return super().ask(system, prompt, schema)


def play(m):
    for t in range(m.turns):
        m.turn(t)
    m.finish()


def main(mode):
    cache = Cache(os.path.join(ROOT, "cache", "v15", f"{MODEL}-{NAME}.json"))
    oracle = Swapped(cache, MODEL, SEED, client=None, replay=True)
    chron = Chronicle(SEED, data.culprit("daniel_ate_it"))
    day1 = Morning(oracle, SEED, "daniel_ate_it")
    play(day1)
    chron.add_day(day1)
    n1 = Night(day1, oracle, number=1, house=chron.house_state()).run()
    chron.add_night(n1)
    NightMind(n1, chron, oracle).run()
    day2 = Morning.next_day(day1, n1, oracle, chronicle=chron)
    play(day2)
    chron.add_day(day2)
    n2 = Night(day2, oracle, number=2, house=chron.house_state()).run()
    chron.add_night(n2)
    NightMind(n2, chron, oracle).run()
    day3 = Morning.next_day(day2, n2, oracle, chronicle=chron)
    carry = {q: day3.carry[q] for q in data.ORDER}
    if mode == "off":
        with open(os.path.join(HERE, f"carry_off_seed{SEED}.json"), "w", encoding="utf-8") as f:
            json.dump(carry, f, ensure_ascii=False, indent=1)
    elif mode == "before":
        with open(SAVED, "w", encoding="utf-8") as f:
            json.dump(carry, f, ensure_ascii=False, indent=1)
    else:
        with open(SAVED, encoding="utf-8") as f:
            old = json.load(f)
        Swapped.swap = {"\n".join(carry[q]): "\n".join(old[q]) for q in data.ORDER if carry[q] != old[q]}
        print("people whose day-3 memory block changed:", [q for q in data.ORDER if carry[q] != old[q]])
    asked_before = oracle.from_cache
    play(day3)
    chron.add_day(day3)
    meta = json.load(open(os.path.join(ROOT, "runs", "v15", NAME + ".meta.json"), encoding="utf-8"))
    tr = json.load(open(os.path.join(ROOT, "runs", "v15", NAME + ".transcript.json"), encoding="utf-8"))
    same3 = json.loads(json.dumps(day3.transcript)) == tr["day3"]
    print(f"replayed {oracle.from_cache} answers from cache/v15, 0 API calls; day 3: {oracle.from_cache - asked_before} "
          f"asks, {oracle.swapped} found with the old carry swapped back; day-3 transcript "
          f"{'IDENTICAL' if same3 else 'DIFFERS'} to runs/v15")
    d2, d3 = day2.max_prompt_tokens, day3.max_prompt_tokens
    print(f"day 2 largest prompt, estimated: {d2} (meta: {meta['day2']['max_prompt_tokens_estimated']})")
    print(f"day 3 largest prompt, estimated: {d3} (meta: {meta['day3']['max_prompt_tokens_estimated']})")
    print(f"ratio day 3 / day 2: {d3 / d2:.3f} (M3 limit 1.10)")
    for q in data.ORDER:
        size = sum(len(x) + 1 for x in carry[q])
        print(f"\n--- {q}: day-3 block C ({len(day3.blocks[q]['C'])} lines; memory block {size} chars)")
        print("\n".join(day3.blocks[q]["C"]) or "(no C)")


if __name__ == "__main__":
    if sys.argv[1] == "off":
        memory.PATTERNS = {}
    main(sys.argv[1])
```

**`$S/c_bound.py`**

```python
"""Per person on day 3 of seed 3: is the new memory block the old one with C put in front, and what did the bound
(memory.bounded, MEMORY_MAX) drop? Prints the estimated size of each block and of C untrimmed."""
import json, os, sys, io, contextlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import c_replay, memory, data
from world import Morning, estimate_tokens
seen = {}
orig = Morning.next_day
def spy(*a, **k):
    m = orig(*a, **k)
    if m.day == 6:
        seen["m"], seen["chron"] = m, k["chronicle"]
    return m
Morning.next_day = staticmethod(spy)
with contextlib.redirect_stdout(io.StringIO()):
    c_replay.main("after")
m, chron = seen["m"], seen["chron"]
old = {q: x[x.index("Yesterday and last night:"):] for q, x in json.load(open(c_replay.SAVED, encoding="utf-8")).items()}   # A and B: the old carry without its C
for q in data.ORDER:
    b = m.blocks[q]
    full = memory.render_c(memory.block_c(chron, q, 6, away=m.away))
    print(f"{q}: A+B unchanged: {b['A'] + b['B'] == old[q]}; C as rendered == C untrimmed: {b['C'] == full}; "
          f"estimated tokens: A+B+C {estimate_tokens(chr(10).join(b['C'] + b['A'] + b['B']))} "
          f"(MEMORY_MAX {memory.MEMORY_MAX}), untrimmed {estimate_tokens(chr(10).join(full + b['A'] + b['B']))}")
    if b["C"] != full:
        print("   untrimmed C:", *full, sep="\n   ")
import difflib
print("\nmara: old memory block -> new memory block (A and B lines only)")
for line in difflib.unified_diff(old["mara"], m.blocks["mara"]["A"] + m.blocks["mara"]["B"], lineterm="", n=0):
    print("  ", line)
```

**`$S/c_diff.py`**

```python
"""Where the replayed day-3 transcript (new code, same answers) differs from runs/v15's, key by key."""
import json, os, sys
sys.argv = [sys.argv[0], "after"]
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import c_replay
from world import Morning
got = {}
orig = Morning.finish
def finish(self):
    orig(self)
    if self.day == 6:
        got["t"] = json.loads(json.dumps(self.transcript))
Morning.finish = finish
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    c_replay.main("after")
old = json.load(open(os.path.join(c_replay.ROOT, "runs", "v15", c_replay.NAME + ".transcript.json"), encoding="utf-8"))["day3"]
new = got["t"]
def walk(a, b, path):
    if type(a) != type(b):
        print(path, "type", type(a).__name__, type(b).__name__); return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b: print(path + "/" + k, "only in", "new" if k in b else "old"); continue
            walk(a[k], b[k], path + "/" + k)
    elif isinstance(a, list):
        if len(a) != len(b): print(path, "len", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{path}[{i}]")
    elif a != b:
        print(path, "\n   old:", repr(a)[:300], "\n   new:", repr(b)[:300])
walk(old, new, "day3")
```
