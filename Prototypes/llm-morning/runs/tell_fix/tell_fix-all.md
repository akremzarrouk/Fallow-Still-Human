# tell_fix: all documents

Merged by `merge-slice-docs.py` from the 1 Markdown files in `Prototypes/llm-morning/runs/tell_fix/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)

---

## report.md

### Tell fix: the believable teller can tell, with the facts right

Mode: implement. No live call. Paths are from `Prototypes/llm-morning/`; line numbers are in the working tree at
commit time, on top of HEAD `76edaa9`. Raw outputs are in `runs/tell_fix/`.

**Why** (`reports/calm_variants.md`):
- With the topic options moved to the top, Leo told Daniel in 7 of 8 offers. At position 18 or 19 he told in 0 of 4.
- Elena and Mara never told, at any position.
- All 7 tells placed Daniel wrongly ("while you were sitting there"). The teller's prompt had no line on where Daniel
  was at 09:42.

#### 1. The changes

| # | What | Where |
|---|---|---|
| 1 | **Topic options first.** `options_for` collects the topic options in `lead` instead of appending them after `say_other`, and puts `lead` in front of the list once it is built. Their order is `topics.options`' own (§1.3: a tell before a talk, then the heavier topic, then the more recent). No other option moves, and the "three in a row" filter keeps the order. | `world.py:553`, `world.py:592`, `world.py:625` |
| 2a | **Where each one was at the knock.** The door scene records each person's room when the knock comes (`sc["rooms"]`), and each holder's topic entry keeps a copy, so that the line still works the next day (F1 offers the tell then too). | `quiet.py:547-549`, `topics.py:44-45` |
| 2b | **The whereabouts line.** `topics.whereabouts(m, p, opts)` returns one line for each listener of each tell option in `opts`. See below. | `topics.py:24` (`DOOR_ROOM`), `topics.py:150-173` |
| 2c | **In the prompt.** `prompt_parts` adds the lines to the sure block, after the beliefs. Like the topic options (§5), they sit outside the trimming budget. | `world.py:1205-1207`, `world.py:1237` |
| 3 | **The design amended.** §1.3, §4 ("Place", and the "Why it stands" note), Summary row 4, and a note under "Amended by the user", each citing `calm_variants.md`. | `reports/talk_design.md` |

**What the line says, and when** (`topics.py:150-173`):
- It is shown only while a `tell_<names>_<T>` is offered to p, so it goes as soon as F5 closes the tell (the listener
  knows T). Nothing is stored on the person.
- It is written only if **p was in the kitchen at the knock** (the door scene is played in the kitchen:
  `quiet.Quiet.door_views`, `door_before`), and **the listener was not**. Only then did p perceive the listener's
  absence.
  - A teller who reached the kitchen only after the knock gets no line. This is the conservative choice. In scenes 1
    and 3 all three tellers were in the kitchen at the knock.
- The text: `<Name> was not in the kitchen when the woman came to the door`.
  - The visitor is `the <noun>` of p's own account ("a woman of about forty-five": "the woman"), or `someone`.
  - The room is `data.ROOMS["kitchen"]`.
- `; <he|she> came in at HH:MM` is added only if p's memory holds "`<Name>` comes into the kitchen." at or after the
  visit's start. That line is written for whoever is there at an arrival (`world.turn`, `quiet.Quiet.arrive`).
- **On the next day** (F1 still offers the tell), the line ends "came to the door yesterday", from the same
  `topics.when` the option's label uses. It gives no arrival time, because yesterday's clock would read as today's.
  This case was not in the brief; the full suite found it (§3).

**Not changed:**
- the T time line;
- `topics.claim`, F1 to F5, Daniel's belief;
- any door summary (`sc["summary"]`, `p.sure`);
- any other option's place.

**One consequence of the new order:** every prompt that offers a topic option changes. So caches recorded before
this commit (for example `cache/talk_probe`, `cache/calm_probe`) answer such prompts only up to the end of the visit.

#### 2. The tests (`test_morning.py`, `TellFixTest`, from line 8477)

Each was run first with the production changes stashed (`git stash push -- world.py topics.py quiet.py`), then with
them (`runs/tell_fix/red.stdout.txt`, `green.stdout.txt`).

| Test | Line | Red (changes out) | Green |
|---|---|---|---|
| (a) `test_a_in_scene_1_at_0948_elenas_options_start_with_the_tell_and_the_rest_keep_their_order` | 8512 | `AssertionError: 'silent' != 'tell_daniel_visit'` | ok |
| (b) `test_b_leos_prompt_in_scene_3_holds_the_whereabouts_line_and_daniels_does_not` | 8536 | `AssertionError: '- Daniel was not in the kitchen when the woman came to the door; he came in at 09:45.' not found in ['- min 00: …', '- 09:45: at 09:42 someone knocked at the front door: …']` | ok |
| (c) `test_c_the_line_says_nothing_of_coming_in_when_the_teller_did_not_see_the_arrival` | 8549 | `AssertionError: '- Daniel was not in the kitchen when the woman came to the door.' not found in [...]` | ok |
| (d) `test_d_after_daniel_is_told_the_line_is_gone_and_his_claim_is_talk_impls` | 8567 | `AssertionError: False is not true : the premise: the line, while the tell is open` | ok |
| (e) `test_e_on_the_next_day_the_line_says_yesterday_and_gives_no_arrival_time` (added, §3) | 8581 | `AssertionError: '- Daniel was not in the kitchen when the woman came to the door yesterday.' not found in ['- min 00: …']` | ok |

**What each test does:**
- **(a)** Scene 1, with Daniel coming into the kitchen when he can, played to 09:51.
  - `Morning.options_for` is wrapped. At every call it also builds the same moment's list with `topics.options`
    returning nothing: "the former order".
  - At Elena's 09:48 ask: the list is `["tell_daniel_visit"] + former`.
  - At every ask: the list minus its leading topic options equals the former list.
- **(b)** Scene 3, same policy.
  - In each of Leo's prompts that offers `tell_daniel_visit`, the sure block holds
    `- Daniel was not in the kitchen when the woman came to the door; he came in at 09:45.` exactly.
  - No prompt of Daniel's after 09:45 holds "was not in the kitchen when".
- **(c)** Scene 1. At 09:45 Daniel comes into the kitchen as Leo leaves it for the brothers room, so Leo does not see
  him come in (his memory has no "Daniel comes into the kitchen."). Leo comes back at 09:51 (a routine) and is offered
  the tell.
  - His line is `- Daniel was not in the kitchen when the woman came to the door.`
  - His prompt holds no "came in at".
- **(d)** Scene 1 with `TalkTest.elena_tells`, the whole of day 3.
  - The one tell is Elena's, at 09:48.
  - Every prompt up to the one she told at that offered the tell holds the line.
  - No prompt after it holds the line.
  - Daniel's one claim equals `TalkTest.CLAIMS[1]`, `talk_impl`'s string: "Elena told you that at 09:42 a woman
    knocked at the front door and asked for water; that Elena herself told her to go away, and that Mara handed her
    about three litres of the stored water anyway."
- **(e)** Scene 1 with nobody telling, night 3, its night mind, then day 4 to minute 30.
  - Every day-4 prompt that offers `tell_daniel_visit` holds
    `- Daniel was not in the kitchen when the woman came to the door yesterday.`
  - None holds "came in at".

**How (c) and (d) got their final form** (both re-seen failing in that form, in `red.stdout.txt`):
- **(c)** The first scenario (Leo going to Daniel in the brothers room) failed on its premise, not on the feature:
  Leo was never offered the tell there. It was replaced by the scenario above.
- **(d)** First played to 10:21, it failed with no ask after the tell. It now plays the whole day, and counts the
  prompts after the one the tell was made at.

**TalkTest** (`runs/tell_fix/talktest.stdout.txt`): its 7 tests pass. Among them is
`test_a_v16_replays_with_0_requests_and_no_topic_option_appears_before_a_visit_ends`.

#### 3. A bug the full suite found

The first full run with the changes had one error. Its output file was overwritten by the final run, and this
excerpt is from it as read at the time. The same error, run alone, is in `runs/tell_fix/red_nextday.stdout.txt`:

```
ERROR: test_a_ten_day_fake_run_never_reads_world_in_a_prompt (test_morning.PhysicalLayerTest...)
  File "...topics.py", line 160, in whereabouts
    sc = next(s for s in m.quiet.door_scenes if f"visit:{s['visit']}" == t["key"])
StopIteration
Ran 330 tests in 378.183s
FAILED (errors=1)
```

- **The cause.** On the day after a visit, F1 still offers the tell. But `m.quiet` is that day's `Quiet`, whose
  `door_scenes` do not hold yesterday's scene.
- **The test.** (e) was written for this case and seen failing with the same `StopIteration`
  (`runs/tell_fix/red_e.stdout.txt`); the ten-day test failed alone too (`red_nextday.stdout.txt`).
- **The fix.** The topic entry carries the rooms at the knock (`topics.py:45`), and the line says "yesterday" with no
  arrival time.
- **After it:** (a) to (e) and the ten-day test pass: "Ran 6 tests … OK".

#### 4. Commands and output

All from `Prototypes/llm-morning/`, with `env -u GEMINI_API_KEY`.

```
$ .venv/Scripts/python.exe -m unittest test_morning.TellFixTest -v      # changes stashed: exit 1
FAILED (failures=5)
$ .venv/Scripts/python.exe -m unittest test_morning.TellFixTest -v      # changes in: exit 0
Ran 5 tests in 3.540s
OK
$ .venv/Scripts/python.exe -m unittest test_morning.TalkTest -v
Ran 7 tests in 4.216s
OK
$ .venv/Scripts/python.exe -m unittest test_morning > runs/tell_fix/suite.stdout.txt 2>&1      # alone; its last 5 lines:
----------------------------------------------------------------------
Ran 331 tests in 367.756s

OK
exit 0
```

- **Merged file.** `python merge-slice-docs.py Prototypes/llm-morning/runs/tell_fix` (from the repository root)
  writes `runs/tell_fix/tell_fix-all.md`.
- **Live calls:** none. Every run above had `GEMINI_API_KEY` unset.

