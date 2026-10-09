# The door remembered: a give over a refusal kept in each one's memory

Mode: implement. From `reports/door_after_facts.md` §3 and §4. Branch `quiet-day-stage-a`, on HEAD `d26d264`, not
committed. Paths are relative to `Prototypes/llm-morning/`. No API call was made: every command ran with
`GEMINI_API_KEY` removed from the environment. Evidence is in `runs/door_memory/`.

## Summary

| # | Asked | Done |
|---|---|---|
| 1 | Door summary: a refusal and a give by different people, both in each summary, in the order done, each only if perceived | `quiet.py:806-825`, `:849-875`; who perceived each act kept in `sc["perceived"]` (`quiet.py:520`, `:721`) |
| 2 | Own acts at the door in the own-act verb table | `world.py:1814-1816`: `door_look`, `door_open`, `door_give` |
| 3 | Block C key for `door_refuse`, weight 3 | `memory.py:27`, `:127`, `:228-229`. No other weight and not the tie rule changed |
| – | Tests | `DoorMemoryTest`, 6 tests (`test_morning.py:7786-7926`). 5 seen failing first; (b) passes on the old code (see §2) |
| – | Trace | `runs/door_after/trace.py full 1`: day 4's block A holds both acts for Elena, Leo and Mara (§3) |

Nothing else changed: no grudge, trigger or option; the street's records (`street.end_visit`) are untouched.

## 1. The changes

### 1.1 Door summary (`quiet.py`)

- `quiet.py:518-520`: the scene gets `"perceived": []` (for each act in `sc["acts"]`, by its index: the actor and
  everyone in their room when they did it) and `"them"` ("her" or "him", from the envoy's sex; used only for the
  second mention of the visitor).
- `quiet.py:721`: `door_act` appends `[p.id] + [q.id for q in self.m.others_here(p)]` with each act. This is the same
  set `world.apply` perceives the act to (`seen = self.others_here(p)`, `world.py:1683`).
- `quiet.py:849-875`: `refusal_seen(sc, q)` (the first refusal q perceived), `give_seen(sc, q)` (the give, if q perceived
  it), `refused_and_given(sc, q)` (both, by different people, both perceived by q, in the order done) and
  `perceived_refusal_only(sc, q)`.
- `quiet.py:806-825`, in `door_end`:
  - both perceived, refusal first: `{who1} told {them}{asked} to go away, and {who2} handed {her} about three litres of
    the stored water anyway`;
  - both perceived, give first: `{who1} handed {them}{asked} about three litres of the stored water, and then {who2}
    told {her} to go away`;
  - a give over another's refusal, of which q perceived only the refusal: the refusal's own wording;
  - otherwise the wording of today, unchanged (a give alone, a refusal alone, a give over a refusal that q perceived
    neither of, a refusal and a give by the same person, nobody answering).
  - `{her}` is "them" when q only knows "someone" was there.

The sure line (`p.sure`) and the `door_end` record's views are built from the same line (`quiet.py:833-834`,
`:843`), so the night mind's D3-033 and day 4's block A (`night.py:1066-1069`) hold it too.

### 1.2 Own acts at the door (`world.py:1814-1816`)

Added to the `mine` table, used when an act is done with words:
`"door_look": "looked through the gap in the boards"`, `"door_open": "unbarred the front door"`,
`"door_give": "handed water out at the front door"`. (`door_call` and `door_refuse` were in it already.)

The own memory line keeps the existing rule (`world.py:1841-1844`): one's own line is "minute and verb only", without the
words. The words reach the chronicle view, which `view_text` builds from that line plus the words
(`chronicle.py:80-83`). So the memory line says Mara handed water out, and her view of D3-030 says it with her words.
Mara still has her act's own line after it (`world.py:1906`): `you handed a woman of about forty-five at the door about
three litres of the stored water.`

### 1.3 Block C (`memory.py`)

- `memory.py:27`: `WEIGHT["door_refuse"] = WEIGHT["door_open"]` (3).
- `memory.py:127`: `door_refuse` added to the door kinds keyed `(kind, None)`.
- `memory.py:228-229`: its line: `{when}, {you | Name} told someone at the front door to go away{again}.`

## 2. Tests (`test_morning.py`)

`SayingPolicy` (`test_morning.py:7786`): PolicyFake whose answers all carry words, as the live answers at the door did.
`DoorMemoryTest` (`test_morning.py:7800`) plays v16 seed 2 to day 3 from `cache/v16`, with h13 (scene 1's household) at
the door at 09:42, Elena, Mara and Leo in the kitchen and Daniel in the brothers' room.

| Test | Line | What it checks |
|---|---|---|
| (a) `test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done` | 7829 | the three summaries exactly as asked; Daniel's line holds neither act; Elena's sure line |
| (a2) `test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived` | 7846 | the other order; Leo, out of the room for both, keeps the outcome's line |
| (a3) `test_a3_whoever_perceived_only_the_refusal_has_only_the_refusal` | 7866 | Leo saw only the refusal: only the refusal |
| (b) `test_b_a_give_alone_and_a_refusal_alone_keep_their_summaries` | 7880 | a give alone; a refusal alone: today's wording, exactly |
| (c) `test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out` | 7892 | Mara's memory line; her view of the `door_give` event in `Chronicle.add_day` |
| (d) `test_d_block_c_keeps_a_refusal_at_the_door_when_it_is_the_heaviest` | 7910 | the weight; Elena's refusal is Leo's line for her and her own line, over a lighter confront |

On (a)'s Daniel: here he is awake and hears the knock as knocking, so he has the unchanged line `At 09:42 you heard
knocking at the front of the house.` In scene 1 he did not hear the knock and has no line; the trace shows that (§3).

### 2.1 Failing first

**First run** (`runs/door_memory/red1.stdout.txt`). (c) failed on its premise, not on the change: `PolicyFake` gives
words only to speech options, so Mara's give had none. (d) raised `KeyError` rather than failing. The fixture was given
words (`SayingPolicy`) and (d) changed to `WEIGHT.get`:

```
FF.FE
ERROR: test_d_block_c_keeps_a_refusal_at_the_door_when_it_is_the_heaviest
KeyError: 'door_refuse'
FAIL: test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived
FAIL: test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done
FAIL: test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out
AssertionError: None is not true : the premise: Mara spoke as she gave
Ran 5 tests in 2.281s
FAILED (failures=3, errors=1)
```

**Second run, before any production change** (`runs/door_memory/red2.stdout.txt`):

```
FF.FF
======================================================================
FAIL: test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived
AssertionError: 'At 0[93 chars] litres of the stored water.' != 'At 0[93 chars] litres of the stored water, and then you told her to go away.'
- At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water.
+ At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water, and then you told her to go away.
======================================================================
FAIL: test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done
- At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water.
+ At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away, and Mara handed her about three litres of the stored water anyway.
======================================================================
FAIL: test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out
AssertionError: 'you handed water out at the front door. You felt tense.' not found in ['Someone knocked at the front door.', 'A woman\'s voice at the front door says: "Sorry to bother you. Is there any water in the house you could spare? I\'ve nothing left.".', 'Elena tells the person at the front door to go away: "Words of elena at 162."', 'you said. You felt tense.', 'you handed a woman of about forty-five at the door about three litres of the stored water. You felt tense.', 'Leo says nobody should use the stored water for washing or the toilet any more: "Words of leo at 162."']
======================================================================
FAIL: test_d_block_c_keeps_a_refusal_at_the_door_when_it_is_the_heaviest
AssertionError: None != 3
----------------------------------------------------------------------
Ran 5 tests in 2.099s
FAILED (failures=4)
```

**(b) passed on the old code**, as it must: it checks that the wording of a give alone and a refusal alone does not
change. It cannot fail before the change.

**(a3)** was written after its branch (`perceived_refusal_only`). To see it fail, the branch's condition was replaced
by `not False` in a scratch edit, the test run, and the file restored (`runs/door_memory/red_a3.stdout.txt`):

```
AssertionError: 'At 0[35 chars]oor: Mara handed a woman, who asked for water,[36 chars]ter.' != 'At 0[35 chars]oor: Elena told a woman, who asked for water, to go away.'
- At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water.
+ At 09:42 someone knocked at the front door: Elena told a woman, who asked for water, to go away.
Ran 1 test in 0.355s
FAILED (failures=1)
```

### 2.2 Passing (`runs/door_memory/green.stdout.txt`)

```
test_a2_the_give_first_then_the_refusal_and_each_act_only_if_perceived ... ok
test_a3_whoever_perceived_only_the_refusal_has_only_the_refusal ... ok
test_a_a_give_over_a_refusal_is_in_each_summary_with_the_refusal_in_the_order_done ... ok
test_b_a_give_alone_and_a_refusal_alone_keep_their_summaries ... ok
test_c_maras_own_line_and_her_chronicle_view_of_her_give_say_she_handed_water_out ... ok
test_d_block_c_keeps_a_refusal_at_the_door_when_it_is_the_heaviest ... ok
----------------------------------------------------------------------
Ran 6 tests in 2.723s
OK
```

### 2.3 The full suite

With the project's interpreter (`.venv/Scripts/python.exe`, as in `reports/door_heard_impl.md`):
`Ran 313 tests in 357.337s`, `OK`, exit 0 (`runs/door_memory/suite.stdout.txt`). That is 307 before plus the 6 new.

A first run with the system Python 3.12 (`runs/door_memory/suite_system_python.stdout.txt`) gave
`Ran 313 tests`, `FAILED (errors=6)`. All six were `ModuleNotFoundError: No module named 'google'`
(`DaysTest.test_n_t12_schema_plumbing` and five `GeminiClientTest` tests): that interpreter does not have the Gemini
SDK. None of them involves the door. The `DoorMemoryTest` runs and the trace above used the system Python too; they do
not import the SDK.

## 3. The trace: `runs/door_after/trace.py full 1`

Run unchanged. It writes `runs/door_after/full_scene1.json`, which is the investigation's evidence: that file was copied
aside first, the new one moved to `runs/door_memory/full_scene1.json`, and the old one put back (`cmp`: identical).
Stdout in `runs/door_memory/full_scene1.stdout.txt`. The 09:42 answers are the live ones from
`cache/probe_door2/scene1.json`; every answer after is the fake model's.

**Day 4's block A, the door lines** (`full_scene1.stdout.txt:602`, `:623`, `:644`):

- Elena: `- At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away, and Mara handed her about three litres of the stored water anyway.`
- Leo: `- At 09:42 someone knocked at the front door: Elena told a woman, who asked for water, to go away, and Mara handed her about three litres of the stored water anyway.`
- Mara: `- At 09:42 someone knocked at the front door: Elena told a woman, who asked for water, to go away, and you handed her about three litres of the stored water anyway.`
- Daniel: no door line (`scene_record.summary` has no key for him).

Before (`reports/door_after_facts.md` §3.4): `Mara handed a woman, who asked for water, about three litres of the stored
water.` for Elena and Leo, `you handed …` for Mara.

**Mara at 09:42** (`full_scene1.json`, `memory.mara`): `you handed water out at the front door. You felt anxious.`, then
`you handed a woman of about forty-five at the door about three litres of the stored water. You felt anxious.` (was
`you said. You felt anxious.`).

**D3-030, Mara's view** (`full_scene1.stdout.txt:504`): `you handed water out at the front door, saying: "Mom, we have
to give her some, we have enough stored." You felt anxious.` (was `you said, saying: "Mom, …"`). Her night mind's input
has the same line (`full_scene1.stdout.txt:532`).

**D3-033** (`door_end`), each view: the three summaries above.

**Block C on house day 8**: still no door line for anyone. Elena's own line is her `eat` (weight 4), which is heavier
than her refusal (weight 3); the tie rule did not change. The other lines of block C differ from the investigation's
trace (Leo's went_out on N3 there; `denied taking the can 4 times` here): the night after 09:42 is the fake model's,
and its answers follow from prompts that now differ, so this is not evidence of anything.

## 4. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` removed.

```
$ env -u GEMINI_API_KEY python -m unittest test_morning.DoorMemoryTest      # first run, before any production change
FF.FE  … FAILED (failures=3, errors=1)                                     # runs/door_memory/red1.stdout.txt
$ env -u GEMINI_API_KEY python -m unittest test_morning.DoorMemoryTest      # fixture given words; still no change
FF.FF  … FAILED (failures=4)                                               # runs/door_memory/red2.stdout.txt
$ env -u GEMINI_API_KEY python -m unittest test_morning.DoorMemoryTest      # after the changes
.F...  … FAILED (failures=1)    # (a): Daniel had "you heard knocking"; the assertion changed (see §2)
$ env -u GEMINI_API_KEY python -m unittest test_morning.DoorMemoryTest.test_a3_whoever_perceived_only_the_refusal_has_only_the_refusal   # branch disabled
FAILED (failures=1)                                                         # runs/door_memory/red_a3.stdout.txt
$ env -u GEMINI_API_KEY python -m unittest -v test_morning.DoorMemoryTest
Ran 6 tests in 2.723s
OK                                                                          # runs/door_memory/green.stdout.txt
$ cp runs/door_after/full_scene1.json $TEMP/full_scene1.facts.json
$ env -u GEMINI_API_KEY python runs/door_after/trace.py full 1 > runs/door_memory/full_scene1.stdout.txt 2> runs/door_memory/full_scene1.stderr.txt
exit 0                                                                      # stderr empty
$ mv runs/door_after/full_scene1.json runs/door_memory/full_scene1.json
$ cp $TEMP/full_scene1.facts.json runs/door_after/full_scene1.json
$ cmp runs/door_after/full_scene1.json $TEMP/full_scene1.facts.json && echo restored-identical
restored-identical
$ env -u GEMINI_API_KEY python -m unittest test_morning                     # system Python
Ran 313 tests in 362.083s
FAILED (errors=6)                                                           # all: No module named 'google'
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
Ran 313 tests in 357.337s
OK                                                                          # runs/door_memory/suite.stdout.txt
$ git diff --stat
 Prototypes/llm-morning/memory.py       |   5 +-
 Prototypes/llm-morning/quiet.py        |  53 +++++++++++-
 Prototypes/llm-morning/test_morning.py | 142 +++++++++++++++++++++++++++++++++
 Prototypes/llm-morning/world.py        |   5 +-
```


---

## 5. After the visit: the door's stretch and the knock's budget

Mode: implement, on top of §1 to §4 above (not committed when this began). From `reports/door_after_facts.md` §1.2:
in probe_door2's scene 1, after the visit had ended, the door stretch's 18-ask reserve paid for 15 asks of ordinary
talk. The day's 40 were spent by 10:00, and every quiet trigger until evening was refused. No API call: every command
ran with `GEMINI_API_KEY` removed. Evidence is in `runs/door_after_fix/`.

**Line numbers in §1 to §4 are of `quiet.py` before this section's change.** Since then, lines from 95 on are 4 later,
from 551 on 13 later, and from 919 on 23 later (e.g. `door_end`'s summary, cited there at `:806-825`, is now at
`:819-838`).

### 5.1 The changes

1. **A Q7 stretch closes at the latest at the end of the 2nd turn after the visit's last turn** (`quiet.py:1511-1517`,
   in `play`).
   - The stretch knows its visit (`stretch["visit"]`, `quiet.py:1529`). A visit ends (`door_end`) at the first turn
     after its last, so the turns after it are `end` and `end` + 3.
   - Once `AFTER_VISIT` (2, `quiet.py:99`) of them have been played, `Quiet.door_after_close` (`quiet.py:919-928`) ends
     the talk, as when a stretch's asks are spent. It clears arrivals and pending asks, and the stretch closes on the
     existing test.
   - It ends earlier if the talk stops by itself, as before. While the visitor is there, nothing changes: up to 18
     door asks a visit.
   - *Arguing against it first.* Would a family that has just given water away over a refusal stop talking after six
     minutes? Not necessarily. But after this change the talk is not cut off; it is no longer paid for by the door's
     reserve. If the argument goes on, it does so as any other talk does: the triggers it raises are played within
     the day's 40, like a grudge meeting. What the 18 paid for in the facts was not an argument about the door. From
     09:48 on, no trigger referred to it (`door_after_facts.md` §1.3).
2. **A knock comes only if the day can give it 6 asks without touching what the evening is still owed**
   (`Quiet.knock_short`, `quiet.py:551-559`, called from `hear_knock`, `quiet.py:500`; the rule is in the comment at
   `quiet.py:94-99`).
   - The rule: `DAY_MAX − asks spent − owed ≥ KNOCK_NEEDS` (6). `owed` is `EVENING_ASKS` (8) until Q5 has been
     checked (`evening_done`), else 0. So a knock comes with at most 42 asks spent before 19:00, and 50 after.
   - It replaces `KNOCK_UNDER` (52), which is gone. A deferral says why: "the day cannot give a knock 6 asks beyond the
     evening's 8".
3. **Not changed:** `DAY_MAX` (56), `QUIET_ASKS` (12), Q5's 8, the door's 18, and how a visit ends. A knock that
   comes inside a stretch already under way (played) is not a Q7 stretch: the brief's item 1 does not reach it, and
   its stretch's cap still grows by 18.

### 5.2 Scene 1 to noon after the change (`runs/door_after_fix/noon1.stdout.txt`)

`python runs/door_after_fix/noon1.py`: the same play as `trace.py noon 1`, in this process, writing nothing in the
repository (the facts' own traces in `runs/door_after/` are untouched).
```
visit 09:42 to 09:45, given; door asks 3
stretch 09:42 to 09:51 Q7 in kitchen: 9 asks
stretch 10:27 to 10:33 Q2 in kitchen: 7 asks
asked from the knock:
  09:42: elena, mara, leo
  09:45: elena, leo, mara, daniel
  09:48: elena, leo
  10:27: daniel, elena, mara, leo
  10:30: elena, mara, daniel
quiet log from 09:45:
  09:51 Q2 fired False why a line between them 3 minutes before
  10:27 Q2 fired True why None
  10:27 Q2 fired True why None
day's asks at 12:00: 40
exit 0
```
Before (`door_after_facts.md` §1.2): the Q7 stretch ran 09:42 to 10:00 on 18 asks, and every Q2 to noon was refused,
"the day's 40 asks are spent".

**A finding, not changed (outside the brief).** The day's 40 are still spent by 10:33. A reserved stretch (Q5, Q6, Q7)
may ask past the day's 40, but its asks count in `Quiet.asks`, which every ordinary trigger after it is checked
against (`spent`, `budget`). So the door's 9 asks still come out of the 16 that the morning's 24 leave for the rest of
the day. Before, it was 18 of the 16. Whether a reserved stretch's asks should count toward the ordinary 40 is for the
user.

### 5.3 The tests (`test_morning.py:7929-8018`, `DoorAfterTest`)

| Test | Line | What it does |
|---|---|---|
| `test_a_after_a_visit_its_stretch_asks_for_2_turns_at_most_and_the_10_00_q2_is_not_refused_for_the_budget` | 7967 | probe_door2's scene 1 as `trace.py noon 1` (the 09:42 asks from `cache/probe_door2/scene1.json`, the fake model after). The visit is 09:42 to 09:45; the Q7 stretch ends by 09:51; nobody is asked from 09:51 until the next stretch; no Q1 or Q2 from the visit to noon is refused for the day's asks, and a Q2 fires |
| `test_b_a_knock_is_deferred_unless_the_day_can_give_it_6_asks_beyond_the_evenings_owed_asks` | 7993 | Before the evening: 42 spent, the knock comes; 43, deferred, saying why. After Q5: 50 comes; 51 deferred |

**Amended:** T6 (`test_morning.py:7250-7256`) checked the deferral's reason, "52 asks are spent". It now checks "the day
cannot give a knock 6 asks beyond the evening's 8"; the knock at 52 spent is still deferred.

**Red.** The final tests, against `quiet.py` with only this section's replacements reversed: the file was copied, the
six replacements undone, the tests run, the copy put back. The sha256 is the same before and after, `0cabf333…ee595a`.
`runs/door_after_fix/red.stdout.txt`:
```
FAIL: test_a_after_a_visit_its_stretch_asks_for_2_turns_at_most_and_the_10_00_q2_is_not_refused_for_the_budget
    self.assertLessEqual(q7[0]["end"], latest, q7[0])
AssertionError: 183 not less than or equal to 171 : {'start': 162, 'end': 183, 'room': 'kitchen', 'trigger': 'Q7', 'asks': 18}
FAIL: test_b_a_knock_is_deferred_unless_the_day_can_give_it_6_asks_beyond_the_evenings_owed_asks
    self.assertFalse(fired, "with 43 spent, the knock would take from the evening's 8")
AssertionError: [{'kind': 'Q7', 'minute': 120, 'room': 'kitchen', … 'fired': True, 'why': None, …}] is not false : with 43 spent, the knock would take from the evening's 8
Ran 2 tests in 0.774s
FAILED (failures=2)
exit 1
```
**One test change after the code, said plainly.** Test (a) first required a Q2 check at exactly 10:00, the minute the
facts found refused. With the stretch over at 09:51, the house's next minutes moved: Q2 was checked at 09:51 (refused,
"a line between them 3 minutes before", not the budget) and fired at 10:27. The premise now asks that every Q1 and Q2
check from the visit to noon is free of a budget refusal, and that a Q2 fires. The red above is of the final test; it
fails on the stretch's end, before that premise.

**Green** (`runs/door_after_fix/green.stdout.txt`): `DoorAfterTest`, `KnockTest`, `KnockFixTest`, `DoorHeardTest`,
`DoorMemoryTest`:
```
Ran 27 tests in 19.077s
OK
exit 0
```

### 5.4 The 10-day bound (`reports/w2_design.md` §6.2, amended)

**448 + 32 + 28 = 508 live asks, still over the run cap of 450.**
- No day scene asks more than `DAY_MAX` (56), reserved or not, so days 3 to 10 ask at most 8 × 56 = 448.
- The bound of 546 in `door_heard_impl.md` added the door's 18 to every v22 day without that cap, and so overstated it.
- This section's two changes lower what a door scene costs in a run, but not this bound, which the day cap sets.
- As the brief says, nothing else was changed for it: the run cap is 450.

The design's statements of the 52 rule (§4.2.2, §6.1 twice, §7.2 T6) are amended to the new rule, each marked
**Amended (`reports/door_memory_impl.md`, …)**. `git diff --stat reports/w2_design.md` for this section: 14
insertions, 3 deletions.

### 5.5 The full suite, run alone (`runs/door_after_fix/unittest.stdout.txt`, 17:01:07Z to 17:06:35Z)

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
----------------------------------------------------------------------
Ran 315 tests in 326.060s

OK
exit 0
```
315 is §2.3's 313 plus the 2 of `DoorAfterTest`.

### 5.6 Commands

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` removed.

| Command | Output | Result |
|---|---|---|
| `python -m unittest -v test_morning.DoorAfterTest` (this section's replacements reversed in a copy of `quiet.py`) | `runs/door_after_fix/red.stdout.txt` | 2 failures, exit 1 |
| `python -m unittest -v test_morning.DoorAfterTest test_morning.KnockTest test_morning.KnockFixTest test_morning.DoorHeardTest test_morning.DoorMemoryTest` | `runs/door_after_fix/green.stdout.txt` | 27 OK, exit 0 |
| `python runs/door_after_fix/noon1.py` | `runs/door_after_fix/noon1.stdout.txt` | exit 0 (§5.2) |
| `python -m unittest test_morning` | `runs/door_after_fix/unittest.stdout.txt` | 315 OK, exit 0 |
