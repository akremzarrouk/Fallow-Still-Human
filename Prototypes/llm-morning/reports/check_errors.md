# The four check errors of v15, fixed

Mode: implement. No API was called. Every command ran with `GEMINI_API_KEY` unset. No cache was regenerated or
written: `cache/v15` was only read, to recover the records each night mind was shown. The repeat check (S9) and
the other wording rules (S3, S5) were not touched.

Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\78f61fe4-2d67-47e7-980d-db8a042af872\scratchpad`.

## Result

| # | Done when | Verdict | Evidence |
|---|---|---|---|
| 1 | The 4 new tests fail before the change and pass after | **PASS** | Before (old `mind.py`, stashed): the 4 FAIL with v15's own verdicts. After: 4 ok. §5.2, §5.3. |
| 2 | Every other v15 rejection is still rejected, by a test on its real text | **PASS** | `test_every_other_v15_verdict_stands`: the S9 repeat and the 5 wording rejections keep their exact v15 verdicts, and so does every other one of the 73 verdicts. §5.3. |
| 3 | Full suite passes; v9 to v14 IDENTICAL | **PASS** | `Ran 186 tests in 162.077s`, `OK`, exit 0. Frozen: 18 of 18 IDENTICAL, 0 API calls. §5.4, §5.5. |

## 1. The tests rebuild each night mind's real input

`CheckErrorsTest` (`test_morning.py:4311`) checks each v15 night-mind answer again, on the input it had:
- **the answer:** `runs/v15/<seed>.transcript.json`, `mind<k>[pid]["answer"]`;
- **the records it was shown:** parsed from that answer's own prompt in `cache/v15`, read only. Each record line is
  `[id] text`, and each earlier-days line is `- [ids] text`, so `shown` is exactly what the check saw;
- **the chronicle up to that night:** the transcript's chronicle, scenes 1 to k only;
- **the meanings it already carried:** the earlier kept meanings, which S9 needs.

**The rebuild is exact.** On the code before the change, it gives all **73** v15 verdicts (memories and intents)
exactly as recorded (`$S/recheck.py`, §5.1: "0 differ").

## 2. The rule changes (`mind.py`)

Each is cut to the one case, and each was argued against first (CLAUDE.md, "Judging changes").

| Error (v15) | Change | Why this and no more |
|---|---|---|
| **Seed 1, mind 1, Elena:** "…and found Daniel's bed empty before he returned…". Rejected `S8 elena find: no such event`. | "found" is a *find* claim only when food or nothing is what was found: `food`, `portion(s)`, `can(s)`, `nothing`, `anything` or `something` within the 3 words after it (`FOUND`). | S8's *find* family is checked only against getting into the neighbour's house (`matching`). A person finds a bed empty, a door open, a brother gone, and none of these is a visit. "found food" and "found nothing there" are still checked (guard test). |
| **Seed 3, mind 2, Elena:** "…I stayed in bed while my children took risks." Rejected `S8 elena take: no such event`. | "took" is not a *take* claim when `risk(s)` or `chance(s)` is within the 2 words after it (`NOT_TAKEN`). | **Not** "took needs a food object": "Daniel took it" is the theft claim itself and must stay checked. Only the idiom is let out. "took the can" next to "took risks" is still checked (guard test). |
| **Seed 1, mind 2, Daniel:** "I lay awake in the dark with Leo…", citing N2-01, "You went to bed in the brothers room with Leo". Rejected `S4 Leo`. | S4 also allows every name that appears in the text of a cited record, as the prompt showed it. | S4 exists to stop a memory bringing in someone the cited records do not hold. A name the record itself shows is held by it. "Mom never trusted me", with a record naming nobody, is still rejected (existing N-T test, §5.4). |
| **Seed 1, mind 1, Mara's intent:** "I am going to ask Daniel why he went out into the night and came back with nothing." Rejected `S8 mara come back: no such event`. | **Intents only:** a clause with no subject of its own, following a clause with a plan word (`EXEMPT`, or `'ll`), is part of that plan and not read as an event. | The clause "came back with nothing" took "I" from the clause before (§2.7, step 2), but it sits inside what she means to ask. Memories are left alone: none of their v15 errors was of this kind. A subject-less clause after a non-plan clause is still read as an event ("Leo went out and came back, so…" is rejected for both acts), and so is a clause with its own subject inside an intent (guard test). |

**What it costs:**
- Two checks are now narrower: "found" without food, and "took risks".
- So a false "Leo found the house empty" is no longer caught, if Leo never went. It was never a food claim.
- **Pre-existing, unchanged, seen while writing the guard test:**
  - "Leo took it" with no "can" counts any eating by Leo (`matching`, `eat`/`take`). In seed 1 Leo ate, so it
    is kept.
  - A *find* counts a clean trip that found nothing (`matching` excludes only "shaken, with nothing"). So
    "Daniel found food" would be kept after seed 1's empty trip.
  - Neither was touched (out of scope).

## 3. The 5 wording-rule rejections: justified or not

| v15 | Memory | Verdict |
|---|---|---|
| Seed 2, mind 1, Daniel, `S5 tonight` | "I had to protect my family and stop anyone from going out into the dangerous street tonight." | **Justified:** it means night 1, but carried into day 2's prompt "tonight" reads as night 2. |
| Seed 2, mind 2, Daniel, `S5 tonight` | "I said I will go tonight, and I mean it, because I am the eldest and I will take the risk." | **Justified:** it means night 2, which he did go out on; read on day 3, "tonight" points to a night still to come. |
| Seed 2, mind 2, Elena, `S5 tonight` | "Daniel offered to go to the neighbour's house tonight to find food and said he still means to go." | **Justified:** the same shift. On day 3 it reads as an offer for night 3. |
| Seed 2, mind 2, Leo, `S5 yesterday` | "Daniel hid the truth and lied all day yesterday, so he cannot act like a martyr now." | **Justified:** it means day 1; read on day 3, "yesterday" is day 2. "All day" is also false: Daniel confessed at min 33 of day 1. |
| Seed 3, mind 1, Elena, `S3 one` | "I counted the pantry and found one can missing, leaving only two portions for us all." | **Justified:** the numbers are true, but the code owns every number (North Star). The lost thought is a restatement of her count. |

The genuine repeat (seed 1, mind 2, Mara, `S9 a repeat`: "Leo ate a portion right in front of me while I was
starving.") is still rejected.

## 4. Diff summary and what else changes

```
$ git diff --stat
 Prototypes/llm-morning/memory.py       |  12 +++
 Prototypes/llm-morning/mind.py         |  21 +++--
 Prototypes/llm-morning/test_morning.py | 156 +++++++++++++++++++++++++++++++++
 3 files changed, 184 insertions(+), 5 deletions(-)
```

- **`memory.py` (12 lines) is not this work.** It is the uncommitted block C pattern rule of
  `reports/c_patterns.md`. Nothing is committed.
- **`mind.py`:** `FOUND` and `NOT_TAKEN`, a `plan` flag on `claims` (passed by `intent_verdict` only), the two
  narrowings in `claims`, and one line in S4.
- **`test_morning.py`:** the class `CheckErrorsTest`, 6 tests. About 41 of the 156 lines are the pattern rule's
  two tests from `reports/c_patterns.md`.

**Tests:**
- `test_found_is_not_finding_food`
- `test_took_risks_is_not_taking_food`
- `test_a_name_in_the_cited_record_counts`
- `test_coming_back_in_an_intent_is_not_an_event`
- `test_every_other_v15_verdict_stands`: the 73 v15 verdicts, the 4 aside. It also pins the 6 rejections and
  their exact reasons.
- `test_false_finds_thefts_and_events_in_intents_are_still_rejected`: a guard. On seed 1's real input it holds
  four cases: a false "found food", a false "found nothing", a false "took the can" next to "took risks", and
  a false event in an intent.

**What the v15 runs would now do differently.** Not run: that needs the API. Four verdicts change, so later
prompts change:
- **Seed 1:** day 2 carries Elena's empty-bed memory and Mara's intent. Daniel's night-2 memory reaches day 3.
- **Seed 3:** Elena's guilt, "I stayed in bed while my children took risks", reaches day 3.
- Replaying v15 from `cache/v15` would therefore miss from those points on. There is no `v15/check.py`, and none
  was asked for.

## 5. Commands and raw output

From `Prototypes/llm-morning/`.

### 5.1 The rebuild on the code before the change

```
$ timeout 100 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S\recheck.py" < /dev/null
seed 1 mind 1 elena: v15 'rejected: S8 elena find: no such event' -> now 'rejected: S8 elena find: no such event' | I heard the front door open in the night and found Daniel's bed empty before he returned with nothing in his hands.
seed 1 mind 1 mara: v15 'rejected: S8 mara come back: no such event' -> now 'rejected: S8 mara come back: no such event' | INTENT: I am going to ask Daniel why he went out into the night and came back with nothing.
seed 1 mind 2 daniel: v15 'rejected: S4 Leo' -> now 'rejected: S4 Leo' | I lay awake in the dark with Leo, listening and starving, knowing the responsibility is mine alone.
seed 1 mind 2 mara: v15 'rejected: S9 a repeat' -> now 'rejected: S9 a repeat' | Leo ate a portion right in front of me while I was starving.
seed 2 mind 1 daniel: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | I had to protect my family and stop anyone from going out into the dangerous street tonight.
seed 2 mind 2 daniel: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | I said I will go tonight, and I mean it, because I am the eldest and I will take the risk.
seed 2 mind 2 elena: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | Daniel offered to go to the neighbour's house tonight to find food and said he still means to go.
seed 2 mind 2 leo: v15 'rejected: S5 yesterday' -> now 'rejected: S5 yesterday' | Daniel hid the truth and lied all day yesterday, so he cannot act like a martyr now.
seed 3 mind 1 elena: v15 'rejected: S3 one' -> now 'rejected: S3 one' | I counted the pantry and found one can missing, leaving only two portions for us all.
seed 3 mind 2 elena: v15 'rejected: S8 elena take: no such event' -> now 'rejected: S8 elena take: no such event' | Someone went out into the dark and came back before dawn and I stayed in bed while my children took risks.
73 verdicts (memories and intents); 0 differ from the v15 record
```

**After the change:**

```
$ timeout 100 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S\recheck.py" < /dev/null
seed 1 mind 1 elena: v15 'rejected: S8 elena find: no such event' -> now 'kept' | I heard the front door open in the night and found Daniel's bed empty before he returned with nothing in his hands.
seed 1 mind 1 mara: v15 'rejected: S8 mara come back: no such event' -> now 'kept' | INTENT: I am going to ask Daniel why he went out into the night and came back with nothing.
seed 1 mind 2 daniel: v15 'rejected: S4 Leo' -> now 'kept' | I lay awake in the dark with Leo, listening and starving, knowing the responsibility is mine alone.
seed 1 mind 2 mara: v15 'rejected: S9 a repeat' -> now 'rejected: S9 a repeat' | Leo ate a portion right in front of me while I was starving.
seed 2 mind 1 daniel: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | I had to protect my family and stop anyone from going out into the dangerous street tonight.
seed 2 mind 2 daniel: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | I said I will go tonight, and I mean it, because I am the eldest and I will take the risk.
seed 2 mind 2 elena: v15 'rejected: S5 tonight' -> now 'rejected: S5 tonight' | Daniel offered to go to the neighbour's house tonight to find food and said he still means to go.
seed 2 mind 2 leo: v15 'rejected: S5 yesterday' -> now 'rejected: S5 yesterday' | Daniel hid the truth and lied all day yesterday, so he cannot act like a martyr now.
seed 3 mind 1 elena: v15 'rejected: S3 one' -> now 'rejected: S3 one' | I counted the pantry and found one can missing, leaving only two portions for us all.
seed 3 mind 2 elena: v15 'rejected: S8 elena take: no such event' -> now 'kept' | Someone went out into the dark and came back before dawn and I stayed in bed while my children took risks.
73 verdicts (memories and intents); 4 differ from the v15 record
```

### 5.2 The tests before the change (RED)

The old `mind.py` was put back with `git stash push mind.py` for this run, and restored with `git stash pop`:

```
$ git stash push mind.py -q && timeout 300 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.CheckErrorsTest < /dev/null; git stash pop -q
test_a_name_in_the_cited_record_counts (test_morning.CheckErrorsTest.test_a_name_in_the_cited_record_counts) ... FAIL
test_coming_back_in_an_intent_is_not_an_event (test_morning.CheckErrorsTest.test_coming_back_in_an_intent_is_not_an_event) ... FAIL
test_every_other_v15_verdict_stands (test_morning.CheckErrorsTest.test_every_other_v15_verdict_stands) ... ok
test_false_finds_thefts_and_events_in_intents_are_still_rejected (test_morning.CheckErrorsTest.test_false_finds_thefts_and_events_in_intents_are_still_rejected) ... ok
test_found_is_not_finding_food (test_morning.CheckErrorsTest.test_found_is_not_finding_food) ... FAIL
test_took_risks_is_not_taking_food (test_morning.CheckErrorsTest.test_took_risks_is_not_taking_food) ... FAIL

======================================================================
FAIL: test_a_name_in_the_cited_record_counts (test_morning.CheckErrorsTest.test_a_name_in_the_cited_record_counts)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4374, in test_a_name_in_the_cited_record_counts
    self.assertEqual(self.memory(1, 2, "daniel", 2, "I lay awake in the dark with Leo, listening and starving, "
AssertionError: 'rejected: S4 Leo' != 'kept'
- rejected: S4 Leo
+ kept


======================================================================
FAIL: test_coming_back_in_an_intent_is_not_an_event (test_morning.CheckErrorsTest.test_coming_back_in_an_intent_is_not_an_event)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4384, in test_coming_back_in_an_intent_is_not_an_event
    self.assertEqual(r["intent_verdict"], "kept")
AssertionError: 'rejected: S8 mara come back: no such event' != 'kept'
- rejected: S8 mara come back: no such event
+ kept


======================================================================
FAIL: test_found_is_not_finding_food (test_morning.CheckErrorsTest.test_found_is_not_finding_food)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4362, in test_found_is_not_finding_food
    self.assertEqual(self.memory(1, 1, "elena", 1, "I heard the front door open in the night and found Daniel's "
AssertionError: 'rejected: S8 elena find: no such event' != 'kept'
- rejected: S8 elena find: no such event
+ kept


======================================================================
FAIL: test_took_risks_is_not_taking_food (test_morning.CheckErrorsTest.test_took_risks_is_not_taking_food)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 4368, in test_took_risks_is_not_taking_food
    self.assertEqual(self.memory(3, 2, "elena", 1, "Someone went out into the dark and came back before dawn and "
AssertionError: 'rejected: S8 elena take: no such event' != 'kept'
- rejected: S8 elena take: no such event
+ kept


----------------------------------------------------------------------
Ran 6 tests in 0.110s

FAILED (failures=4)
```

### 5.3 The tests after the change (GREEN)

```
$ timeout 300 env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.CheckErrorsTest < /dev/null
test_a_name_in_the_cited_record_counts (test_morning.CheckErrorsTest.test_a_name_in_the_cited_record_counts) ... ok
test_coming_back_in_an_intent_is_not_an_event (test_morning.CheckErrorsTest.test_coming_back_in_an_intent_is_not_an_event) ... ok
test_every_other_v15_verdict_stands (test_morning.CheckErrorsTest.test_every_other_v15_verdict_stands) ... ok
test_false_finds_thefts_and_events_in_intents_are_still_rejected (test_morning.CheckErrorsTest.test_false_finds_thefts_and_events_in_intents_are_still_rejected) ... ok
test_found_is_not_finding_food (test_morning.CheckErrorsTest.test_found_is_not_finding_food) ... ok
test_took_risks_is_not_taking_food (test_morning.CheckErrorsTest.test_took_risks_is_not_taking_food) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.109s

OK
```

**On the way:** the guard test failed twice, each time on my expectation, never on the code:
- **"Leo took it and took risks."** was kept, on the old code as on the new. "took it" without "can" counts
  Leo's eating (§2, "Pre-existing"). It became "Leo took risks and took the can."
- **The intent "Leo went out and came back, so I will thank him."** was rejected for both acts, not one. The
  expectation was corrected to both.

### 5.4 The full suite

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
.............................................................    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
.    [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
............................................................................................................................
----------------------------------------------------------------------
Ran 186 tests in 162.077s

OK
exit 0
```

The `[429 RESOURCE_EXHAUSTED]` lines are GeminiClientTest's stub API (key `SENTINEL-not-a-real-key-7731`), not real requests.

### 5.5 The frozen versions, v14 to v9

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

## 6. Script

**`$S/recheck.py`** (read only)

```python
"""Every v15 night-mind answer, checked again by the code as it is now, on the input it had: the answer from the
transcript, the records it was shown (parsed from its prompt in cache/v15, read only), the chronicle up to that night,
and the meanings it already carried. Prints each verdict that differs from the v15 record, and every non-kept one."""
import json
import os
import re
import sys

ROOT = r"C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning"
sys.path.insert(0, ROOT)
import mind                                   # noqa: E402
from chronicle import Chronicle               # noqa: E402
from world import NAMES                       # noqa: E402


def load(seed):
    tr = json.load(open(os.path.join(ROOT, "runs", "v15", f"daniel_ate_it-seed{seed}.transcript.json"), encoding="utf-8"))
    cache = json.load(open(os.path.join(ROOT, "cache", "v15", f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"),
                           encoding="utf-8"))
    return tr, cache


def v15_mind(tr, cache, seed, k, pid):
    ans = tr[f"mind{k}"][pid]["answer"]
    prompts = [e["prompt"] for e in cache.values()
               if e["response"] == ans and e["prompt"].startswith(f"You are {NAMES[pid]},")]
    assert len(prompts) == 1, (seed, k, pid, len(prompts))
    shown = {}
    for line in prompts[0].split("\n"):
        m = re.match(r"^(?:- )?\[([A-Z0-9, -]+)\] (.*)$", line)
        if m:
            for i in m.group(1).split(", "):
                shown.setdefault(i, m.group(2))
    c = Chronicle(seed, tr["chronicle"]["fixed"]["culprit"]["value"])
    for e in tr["chronicle"]["events"]:
        if int(e["scene"][1:]) <= k:
            c.add(e)
    carried = [m["meaning"] for kk in range(1, k) for m in tr[f"mind{kk}"][pid]["memories"] if m["verdict"] == "kept"]
    return ans, shown, c, carried


def main():
    n = differ = 0
    for seed in (1, 2, 3):
        tr, cache = load(seed)
        for k in (1, 2):
            for pid, rec in tr[f"mind{k}"].items():
                r = mind.check_answer(*((ans := v15_mind(tr, cache, seed, k, pid))[0], pid, *ans[1:]))
                items = [(m["meaning"], m["verdict"], g["verdict"]) for m, g in zip(rec["memories"], r["memories"])]
                items.append(("INTENT: " + str(tr[f"mind{k}"][pid]["answer"] and json.loads(
                    re.sub(r"^```(?:json)?\s*|\s*```$", "", rec["answer"].strip())).get("intent")),
                              rec["intent_verdict"], r["intent_verdict"]))
                for text, was, now in items:
                    n += 1
                    if was != now:
                        differ += 1
                    if was != "kept" or now != "kept":
                        print(f"seed {seed} mind {k} {pid}: v15 {was!r} -> now {now!r} | {text}")
    print(f"{n} verdicts (memories and intents); {differ} differ from the v15 record")


if __name__ == "__main__":
    main()
```
