# The door heard: the visitor speaks first, records hold what each one perceived, 18 door asks a visit

Mode: implement. From `reports/probe_door.md` (scenes 1 and 8, §3). The parent commit is `3e3d357`. No API call was
made (every run here removes `GEMINI_API_KEY`), no cache was written, and no frozen version, seed, model client or
street odds changed. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/door_heard/`.

## Result

| DONE | What | Verdict | Evidence |
|---|---|---|---|
| (a) | The visitor's first line is in the prompt of everyone who heard the knock in words, at the knock minute | **yes** | `test_a_…`: red, then green (§2) |
| (b) | A child visitor's first line names the child and their age | **yes** | `test_b_…`: red, then green |
| (c) | Whoever heard only knocking has no need in their sure line or block A; no record says "asked for" unless that person heard an ask | **yes** | `test_c_…` and `test_c2_…`: red, then green |
| (d) | No parting line that refers to asking without an ask | **yes** | `test_d_…`: red, then green |
| (e) | Fake model: a visitor who stays 6 turns with 3 in the room gets family decisions after the second knock; no visit over 18 door asks | **yes** | `test_e_…`: red, then green |
| suite | The full suite passes | **yes**: 307 tests OK, exit 0, run alone | §3 |
| probe | `runs/probe_door/probe.py --fake` exits 0, with the visitor's words in each scene's knock-minute prompt | **yes**: exit 0; 8 of 8 | §4 |

**For the user to decide (not changed: outside the brief).** `DAY_MAX` (56) and `KNOCK_UNDER` (52) are as before.
With 18 door asks a visit:
- the day cap can now cut a door scene: a knock with 51 asks spent begins and stops after 5;
- a long door scene after 14:00 can leave Q5's evening none of its 8;
- the 10-day bound in `w2_design.md` §6.2 rises from 450 to 546, over the run cap of 450.

All three are written into the design (§5 below).

## 1. The changes

### 1.1 The visitor speaks first (brief item 1)
- **At the first knock** (`quiet.py:519-523`, in `hear_knock`), after the knock, the visitor says one line through the
  shut door: `street.first_words` (`street.py:672-684`). It is heard in words by everyone who heard that knock in
  words: each one's memory, the scene's `heard_said`, and a `door_line` event with them as witnesses.
- **The line.** Without a child it is the household's `voice_ask_water`/`voice_ask_food` line, chosen as a reply to a
  call was (the same string, so the same line). With a child it is a `first` line of the household's disposition
  (helper, or guarded for any other). Code puts in `{kids}` a sentence naming each child and their age, true of the
  household (`street.kids_words`, `street.py:659-669`): "I've a little boy at home, he's six." / "I've two at home, a
  girl of five and a boy of five."
- **At a later knock** (`quiet.py:669-674`, in `door_before`): a short ask again, heard by whoever heard that knock in
  words. It is `insist` if urgency ≥ 0.8, else `again`, the rule a reply to a second call already used.
- **One function says a line** (`Quiet.door_speak`, `quiet.py:684-707`): the knock's line, a later knock's, and the
  replies queued after a call, an open, a give or a refusal. The listeners get a trigger and their room's talk only in
  played turns; a released scene in quiet time is remembered, as fix 3 had it. A line of an ask slot
  (`ASK_SLOTS`, `quiet.py:96`: `voice_ask_`, `open_ask_`, `again_`) marks the visit as asked (`v["asked"]`).
- **New lines** (`runs/w2a_impl/write_lines.py:16-17`, `:32-37`, `:50-55`; written to `streetdata/lines.json` by that
  script). The pool had no line naming a child's age, so I added 12 `first` lines: 3 per need and disposition, each to
  be said through a shut door:

  | Slot | `by` | Lines (`{kids}` filled by code) |
  |---|---|---|
  | voice_ask_water | helper | "Hello? I'm sorry to knock. {kids} We've no water left. Could you spare a little?" · "Please, is anyone in? {kids} There's not a drop of water left. Just a cup would help." · "I'm sorry to trouble you. {kids} Our water's gone. Anything you could spare, I'd be grateful." |
  | voice_ask_water | guarded | "I'm not here for trouble. {kids} We're out of water. Can you spare any?" · "Is anyone there? {kids} Our water's gone. A cup, that's all I'm asking." · "I won't come in. {kids} There's no water left at home. Have you any?" |
  | voice_ask_food | helper | "Hello? I'm sorry to knock. {kids} We've nothing left to eat. Could you spare a little?" · "Please, is anyone in? {kids} There's no food left at home. Anything at all would help." · "I'm sorry to trouble you. {kids} Our food's gone. Anything you could spare, I'd be grateful." |
  | voice_ask_food | guarded | "I'm not here for trouble. {kids} We've nothing to eat. Can you spare anything?" · "Is anyone there? {kids} Our food's gone. A little, that's all I'm asking." · "I won't come in. {kids} There's no food left at home. Have you anything?" |

  `street.line` never picks a `first` line (`street.py:648-656`), so no other draw sees them. `streetdata/lines.json`
  goes from 102 to 114 lines; `git diff --stat`: 81 insertions, 5 deletions.
- *Arguing against it first.* Would a real person at a boarded door speak before anyone answers? They have walked down
  a dead street with empty bottles and chosen this house. Standing silent on the step for three minutes, then leaving
  when told to go, is what nobody does. Saying "Hello? I'm sorry to knock" and what they need is the ordinary act. The
  case against: some would wait to be answered. But nothing in W2a lets a visitor be heard any other way, and the probe
  showed the family weighing nothing.
- **Fixed in passing:** `street.who_words` (`street.py:702`) said "A old man's voice" / "A old woman's voice". It now
  says "An old …". The voice now names the visitor in records ("a woman"), so the article showed.

### 1.2 Records hold only what each one perceived (brief item 2)
- **What each one perceived is kept per person:**
  - `heard_said` (`quiet.py:515-517`): each line a person heard, with whether it said the need;
  - `saw`: who looked (`door_act`, `quiet.py:722`), or was in the kitchen with the door open (`quiet.py:626`, `:658`);
  - `by_knock`: who heard each knock, and how.
- **`door_end`** (`quiet.py:786-812`) replaces `if sc["said"]` with what each person perceived of the ask:
  - "who asked for {good}" and "asked for {good} and went away" only if that person heard a line saying the need;
  - the visitor is their face only to whoever saw them, their voice ("a woman") to whoever only heard them, and
    "someone" otherwise.

  The sure line and the next day's block A (`night.py:1067-1069`, from `sc["summary"]`) both come from this.
- **Who gets a line** (`quiet.py:792-794`): whoever was at the door, heard any knock in words, or heard the visitor
  speak. Before, it came from `sc["heard"]`, which keeps only each person's last knock. The fake probe's scene 3 showed
  why that matters (§4): Elena and Mara heard the 09:42 line in the kitchen, then left. They heard the second knock
  through a wall, so their records said only "you heard knocking". Test `c2` holds this.
- **The kitchen's view of the door** (`door_views`, `quiet.py:598-630`) shows each person the last line *they* heard,
  not the last line said. Someone who comes into the kitchen later sees "Someone is at the front door; there was a
  knock at …" and no words they did not hear. A person outside the kitchen who heard a knock in words gets the
  visitor's words with it, at that minute.
- **Not changed:** `door_give` is offered to everyone in the kitchen once the visitor has stated a need
  (`need_known`), as before. The brief excludes option availability. Because the visitor now states the need at the
  knock, `door_give` is offered from the first turn; T7 was amended for that (§2.3).

### 1.3 Parting lines (brief item 3)
- Four lines are tagged `after: ask` (`runs/w2a_impl/write_lines.py:130`, `:135`, `:139`, `:143`):
  - "That's all right. I'm sorry I asked. Goodbye."
  - "No, I understand. I'm sorry. I'll leave you be."
  - "Right. Thanks for nothing."
  - "Fine. I'll find it somewhere else."

  The first two are the ones `reports/probe_door.md` §2 found reading as if an ask had been heard. The other two answer
  an ask: "nothing" given, "it" asked for.
- `street.line` leaves them out unless the visit has asked (`street.py:653-654`). Their places in the pool are kept, so
  a visit that has asked draws the same line as before.
- Since the visitor now asks at every first knock, every refusal in a scene follows an ask; the rule is the guard.

### 1.4 18 door asks a visit (brief item 4)
- `DOOR_ASKS` is 18 (`quiet.py:95`), with the reason in the comment. The Q7 stretch begins with it (`play`), and a
  knock inside a played stretch grows that stretch's cap by it.
- **Every played turn the visitor is at the door** (`Quiet.turn`, `quiet.py:1219`), everyone awake who perceives the
  door (`p.door`) is asked: `Quiet.door_asks` (`quiet.py:829-837`) puts them in `pending`. It is not a quiet ask, so
  the day's 12 `QUIET_ASKS` are untouched.
- **Counted where the model is asked** (`world.py:1483-1489`): `door_asked` counts an ask of someone at the door, and
  `door_full` (`quiet.py:839-845`) stops them at the visit's 18.
- **The stretch's cap does not stop a door ask** (`Quiet.spent(p)`, `quiet.py:407-414`; `world.py:1538`). It still
  holds everyone else's asks; the day's 56 holds all of them.
  - Without this, test (e) found Daniel, alone in the bathroom with a trigger of his own, taking one of the stretch's 18.
    Leo was then not asked at 09:15, after the second knock, with only 17 door asks made.
  - So a Q7 stretch can ask at most 18 at the door plus 17 others (T8 checks ≤ 35). In the fake probe the most was 19
    (17 at the door).
- **How a visit ends is unchanged**: given, refused, or gone after 6 turns with nothing from the house. A stretch
  released because nobody in its room perceives the door (`reports/w2a_fixes.md` fix 3) is released as before. The turns
  after it are quiet time, and nobody is asked for the door in them.

## 2. The tests

`test_morning.py:7528-7787`: `DoorRecording` (a `PolicyFake` that keeps every prompt) and `DoorHeardTest`. Each
day-3 test starts from v16 seed 2 through night 2, replayed from `cache/v16` with no API call. The visit is made at
09:00 with everyone's routine ended and each person put in a room.

| Test | Line | What it does |
|---|---|---|
| `test_a_the_visitors_first_line_is_in_the_prompt_of_everyone_who_heard_the_knock_in_words` | 7594 | Elena, Mara, Leo in the kitchen, Daniel in the back room. The first line is said at 09:00, is a pool line, and is in each words-hearer's 09:00 prompt after "Someone is knocking", and in their memory; not in Daniel's (he heard knocking) |
| `test_b_a_child_visitors_first_line_names_the_child_and_their_age` | 7621 | Every household of seed 2's street with a child, for water and for food: the first line names each child's sex and age, says the need, has no `{` left; more than 3 distinct lines |
| `test_c_a_record_states_the_need_and_the_visitor_only_as_that_person_perceived_them` | 7672 | Elena refuses in the knock's minute, Mara looks, Leo listens, Daniel hears knocking. Every summary and sure line has "asked"/"water" only if that person heard the need, and the face only if they saw it. Daniel's summary is "At 09:00 you heard knocking at the front of the house."; Elena's has "who asked for water"; Leo's has the voice, not the face. Then Daniel comes into the kitchen at 09:03 and looks: he has the face and no ask |
| `test_c2_someone_who_heard_the_ask_and_then_only_a_later_knock_keeps_the_ask_in_their_record` | 7714 | Mara hears the first line, goes to the back room, hears the second knock through the wall: her record keeps the ask |
| `test_d_no_parting_line_that_refers_to_asking_without_an_ask` | 7732 | Seeds 1 to 10, every household, visits 1 to 5: no `refused_*` line matching `ask/asked/asking`, "no, I understand", "thanks for nothing" or "find it somewhere" without an ask, and such lines still said after one. In a scene, the refusal follows the ask and the visit records it |
| `test_e_a_visitor_who_stays_6_turns_is_answered_after_the_second_knock_and_no_visit_asks_more_than_18` | 7756 | All three in the kitchen look every turn; the visitor knocks at 09:00 and 09:09 and goes at 09:18. Elena, Leo and Mara are asked at 09:09, 09:12 and 09:15; 18 door asks. With all four in the kitchen (24 would be due): exactly 18 |

### 2.1 Red: the five tests against the original code

The production files were stashed and the final tests run against `3e3d357`'s code (`runs/door_heard/red.stdout.txt`):

```
$ git stash push -- quiet.py street.py world.py streetdata/lines.json runs/w2a_impl/write_lines.py
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.DoorHeardTest
FAIL: test_a_the_visitors_first_line_is_in_the_prompt_of_everyone_who_heard_the_knock_in_words
    self.assertTrue(sc["said"], "the visitor said nothing at the knock")
AssertionError: [] is not true : the visitor said nothing at the knock
FAIL: test_b_a_child_visitors_first_line_names_the_child_and_their_age
    self.assertTrue(sc["said"], f"the visitor from {hid} said nothing at the knock")
AssertionError: [] is not true : the visitor from h8 said nothing at the knock
FAIL: test_c_a_record_states_the_need_and_the_visitor_only_as_that_person_perceived_them
    self.assertNotRegex(line, r"\basked\b|\bwater\b", (pid, line))
AssertionError: Regex matched: 'asked' matches '\\basked\\b|\\bwater\\b' in 'At 09:00 someone knocked at the front door: you told a woman of about sixty-five, who asked for water, to go away.' : ('elena', 'At 09:00 someone knocked at the front door: you told a woman of about sixty-five, who asked for water, to go away.')
FAIL: test_d_no_parting_line_that_refers_to_asking_without_an_ask
    self.assertNotRegex(text, self.ASK_REF, (seed, hid, n, slot))
AssertionError: Regex matched: 'Thanks for nothing' matches '…' in 'Right. Thanks for nothing.' : (1, 'h1', 4, 'refused_flat')
FAIL: test_e_a_visitor_who_stays_6_turns_is_answered_after_the_second_knock_and_no_visit_asks_more_than_18
    self.assertEqual(after, sorted((mm, pid) for mm in (129, 132, 135) for pid in ("elena", "leo", "mara")),
AssertionError: Lists differ: [] != [(129, 'elena'), (129, 'leo'), (129, 'mara'), …, (135, 'mara')]
  … : [(120, 'leo'), (120, 'elena'), (120, 'mara'), (123, 'elena'), (123, 'leo')]
Ran 5 tests in 1.694s
FAILED (failures=5)
exit 1
$ git stash pop
```
Each fails on its own assertion, for the reason the probe found:
- (a), (b): the visitor said nothing.
- (c): Elena's record says "who asked for water" when the visitor had only said a parting line, the leak of
  `quiet.py:750`.
- (d): an ask-referring parting line with no ask.
- (e): after the 6 were spent at 09:03, nobody was asked again.

`test_c2` was written after a fix, which I took back out to see it fail (`runs/door_heard/red_c2.stdout.txt`, the fix
removed, the rest of the change in place):
```
FAIL: test_c2_someone_who_heard_the_ask_and_then_only_a_later_knock_keeps_the_ask_in_their_record
    self.assertIn("asked for water", sc["summary"]["mara"])
AssertionError: 'asked for water' not found in 'At 09:00 you heard knocking at the front of the house.'
Ran 1 test in 0.624s
FAILED (failures=1)
```

**Two test corrections during the work, said plainly:**
- (b)'s first version left the scene's own childless visit due at 09:00, so that one knocked first. It failed red for
  the right reason, but after the change it measured the wrong household. The visit is now set aside
  (`v0["state"] = "done"`), and the red above is of the corrected test.
- (e) at first counted every model decision in the window as a door ask, Daniel's in the bathroom included. It now
  counts the three at the door, and the visit's own `door_asks`.

### 2.2 Green (`runs/door_heard/green.stdout.txt`)
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest -v test_morning.DoorHeardTest test_morning.KnockTest test_morning.KnockFixTest
test_a_the_visitors_first_line_is_in_the_prompt_of_everyone_who_heard_the_knock_in_words ... ok
test_b_a_child_visitors_first_line_names_the_child_and_their_age ... ok
test_c2_someone_who_heard_the_ask_and_then_only_a_later_knock_keeps_the_ask_in_their_record ... ok
test_c_a_record_states_the_need_and_the_visitor_only_as_that_person_perceived_them ... ok
test_d_no_parting_line_that_refers_to_asking_without_an_ask ... ok
test_e_a_visitor_who_stays_6_turns_is_answered_after_the_second_knock_and_no_visit_asks_more_than_18 ... ok
test_t1_… to test_t9_… ... ok (9)
test_f1_… to test_f4_… ... ok (4)
Ran 19 tests in 18.210s
OK
exit 0
```

### 2.3 Existing tests amended (each one states the 6, or the visitor's silence)
- **T7** (`test_morning.py:7293-7298`) expected `door_give` absent right after the knock. The visitor now states the need
  at the knock, so it is offered from the first turn. The option rule is unchanged.
- **T8** is renamed `test_t8_a_visit_asks_at_most_18_at_the_door_and_a_day_at_most_56` (`:7330`). It asserts each
  visit's `door_asks` ≤ 18, a Q7 stretch ≤ 35 (18 at the door plus 17 others, §1.4), the day ≤ 56, and
  `DOOR_ASKS == 18`.
- **F3** (`:7496`): `sc["door_asks"] ≤ 18`, was `sc["asks"] ≤ 6`. Its other assertions are as they were.

## 3. The full suite

Run alone, with nothing else running (`runs/door_heard/unittest.stdout.txt`, 14:05:23Z to 14:10:46Z):
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning
----------------------------------------------------------------------
Ran 307 tests in 320.297s

OK
exit 0
```
307 is the 301 tests of `reports/w2a_fixes.md` plus the 6 new ones. The frozen-version replays (v8 to v14) are among
them and pass.

An earlier run, started at 10:16:10Z while the fake probe (§4) was running too, reported 306 tests and 3 failures:
`test_t11_v8_still_replays`, `test_t14_v11_v10_and_v9_still_replay` and `test_t13_v10_and_v9_still_replay`, each
`AssertionError: 3221225794 != 0`. 3221225794 is 0xC0000142: Windows could not start the replay's subprocess. Nothing
was compared, so it was not a replay difference. Run alone, all three pass. Its output was overwritten by the run
above. Why it counted 306 and not 307 is NOT FOUND (the output is gone).

## 4. The fake probe

The probe is unchanged (sha256 `6d1c98c3…f951f4`, the frozen value in `runs/probe_door/plan_frozen.txt`). Its `--fake`
makes its own temp folder, uses the fake model, writes nothing in the repository, and deletes the folder.

```
$ sha256sum runs/probe_door/probe.py
6d1c98c3728ba3c0b1a026a2afde51e21e2a32b063f262cc62eecd1591f951f4 *runs/probe_door/probe.py
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_door/probe.py --fake        (runs/door_heard/probe_fake.stdout.txt)
phase 0: the knock comes at 09:42; 21 live asks; the morning's talk ended at 18; rooms {'daniel': 'brothers_room', 'elena': 'kitchen', 'leo': 'kitchen', 'mara': 'kitchen'}; resting ['daniel']
scene 1 (no child, helper, urgency under 0.8): 3 live asks; …; outcome refused; door asks 3; acts [('leo', 'door_refuse')]; live in all 24
scene 2 (no child, helper, urgency over 0.8): 3 live asks; …; outcome refused; door asks 3; acts [('elena', 'door_refuse')]; live in all 27
scene 3 (a child, helper, urgency under 0.8): 19 live asks; …; outcome ignored; door asks 19; acts [('daniel', 'door_open')]; live in all 46
scene 4 (children, helper, urgency over 0.8): 10 live asks; …; outcome refused; door asks 10; acts [('leo', 'door_look'), ('mara', 'door_refuse')]; live in all 56
scene 5 (no child, guarded, urgency over 0.8): 3 live asks; …; outcome ignored; door asks 3; acts []; live in all 59
scene 6 (a child, guarded, urgency under 0.8): 14 live asks; …; outcome refused; door asks 14; acts [('leo', 'door_look'), ('elena', 'door_refuse')]; live in all 73
scene 7 (no child, helper, food gone 4 days): 3 live asks; …; outcome refused; door asks 3; acts [('mara', 'door_refuse')]; live in all 76
scene 8 (a child, guarded, food gone 4 days): 7 live asks; …; outcome refused; door asks 7; acts [('elena', 'door_refuse')]; live in all 83
live asks in all: 83
exit 0
```
("live asks" are the fake model's answers. The probe's "door asks" is the scene's `asks`, every ask of its Q7 stretch,
not the new `door_asks`; scene 3's 19 is 17 at the door and 2 elsewhere.)

**The visitor's words in each knock-minute prompt.** The probe deletes its temp folder, so the scene records were read
through `runs/door_heard/probe_check.py`. It runs the same `probe.main()` with `--fake`, keeps the probe's temp folder,
and adds the scene's new fields to the probe's record (a wrapper, no change to the probe). For each scene it checks that
the first line was said at the knock minute and is in the knock-minute prompt of everyone asked then who heard the
first knock in words. Output (`runs/door_heard/probe_check.stdout.txt`, the probe's own lines left out):
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/door_heard/probe_check.py
scene 1 (no child, helper, urgency under 0.8): OK
  first line at 09:42: "Sorry to bother you. Is there any water in the house you could spare? I've nothing left."
  heard the knock in words: ['elena', 'leo', 'mara']; asked at 09:42: ['mara', 'elena', 'leo']; the words in their prompt: {'mara': True, 'elena': True, 'leo': True}
  outcome refused; door asks 3; stretch asks 3; said [('09:45', "Of course. I'm sorry I knocked. Take care.")]
  elena: At 09:42 someone knocked at the front door: Leo told a woman, who asked for water, to go away.
  leo: At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away.
  mara: At 09:42 someone knocked at the front door: Leo told a woman, who asked for water, to go away.
scene 3 (a child, helper, urgency under 0.8): OK
  first line at 09:42: "Hello? I'm sorry to knock. I've a little boy at home, he's six. We've no water left. Could you spare a little?"
  heard the knock in words: ['elena', 'leo', 'mara']; asked at 09:42: ['mara', 'elena', 'leo']; the words in their prompt: {'mara': True, 'elena': True, 'leo': True}
  outcome ignored; door asks 17; stretch asks 19; said [('09:51', "I'm not going to cause trouble. It's only water I'm asking for."), ('09:57', 'Thank you. I know what it costs to open a door now. I just need some water.')]
  daniel: At 09:42 someone knocked at the front door: a woman of about fifty-five asked for water and went away with nothing.
  elena: … (the same)   leo: … (the same)   mara: … (the same)
scene 4 (children, helper, urgency over 0.8): OK
  first line at 09:42: "I'm sorry to trouble you. I've two at home, a girl of five and a boy of five. Our water's gone. Anything you could spare, I'd be grateful."
  outcome refused; door asks 8; stretch asks 10; said [('09:51', "Right. I'm sorry. I'll try somewhere else.")]
  elena: At 09:42 someone knocked at the front door: Mara told a woman, who asked for water, to go away.
  leo: At 09:42 someone knocked at the front door: Mara told a woman of about forty-five, who asked for water, to go away.
scene 6 (a child, guarded, urgency under 0.8): OK
  first line at 09:42: "I'm not here for trouble. I've a little girl at home, she's six. We're out of water. Can you spare any?"
scene 8 (a child, guarded, food gone 4 days): OK
  first line at 09:42: "I won't come in. I've a little girl at home, she's twelve. There's no food left at home. Have you anything?"
  outcome refused; door asks 6; stretch asks 7; said [('09:48', "Fine. I'll find it somewhere else.")]
… (scenes 2, 5, 7: OK; the full output is in the file)
scenes without the visitor's words at the knock: 0
exit 0
```
Read against the probe: Leo, who looked in scene 4, has the face; Elena, who only heard, has "a woman". Scene 8's
"Fine. I'll find it somewhere else." now follows an ask. The family's answers here are the fake model's and say nothing
about what the real model would do.

## 5. The amended design text (`reports/w2_design.md`, `git diff`)

Every place `w2_design.md` states the 6-ask door budget now says what changed and why, citing `reports/probe_door.md`.
Earlier reports (`w2a_impl.md`, `w2a_fixes.md`, `probe_door.md`) record what ran then and are not changed.

Each amendment is marked **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`)** or "(amended: …)": the
header, the Summary row 6, §4.1, §4.2.4, §4.2.5, §4.2.6, §4.3, §6.1 (four places), §6.2, §7.2 (two), §8.2 W2a-8, §8.3.

```diff
$ git diff reports/w2_design.md
diff --git a/Prototypes/llm-morning/reports/w2_design.md b/Prototypes/llm-morning/reports/w2_design.md
index ac85040..9812aa5 100644
--- a/Prototypes/llm-morning/reports/w2_design.md
+++ b/Prototypes/llm-morning/reports/w2_design.md
@@ -12,6 +12,11 @@ touched. The only file added is this one. Paths are relative to `Prototypes/llm-
   otherwise. A number from the code cites `path:line`. A thing looked for and absent is **NOT FOUND**.
 - **Baselines** for the predictions were counted from `runs/v22` by read-only scripts; the commands, their output and the
   script are in §11 and the appendix.
+- **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** the door scene as the probe found it did not show the family what a real visitor would.
+  The visitor now speaks first, in the minute of each knock (§4.2.5); each one's record of a visit holds only what they
+  perceived (§4.2.6); a parting line that refers to an ask comes only after one (§4.3); and the Q7 reserve of 6 is
+  replaced by everyone at the door asked each turn, up to 18 door asks a visit (§4.1, §4.2.4, §6.1, §6.2, §7.2, §8.2,
+  §8.3). Each place says what it was.
 - **How the design argues.** `CLAUDE.md:18-19` says to argue against a mechanism before proposing it. Each mechanism has a
   paragraph "Arguing against X first". `CLAUDE.md:16-17` says a metric is a clue and not the goal, so §8 also has a
   reading check that is not a number.
@@ -25,7 +30,7 @@ touched. The only file added is this one. Paths are relative to `Prototypes/llm-
 | 3 | The noticing rule | One function, `perceive(stimulus, observer)`, used both ways: sound by distance and walls, sight by viewpoint and distance. The family hears a knock, a shout, breaking wood; it sees through one gap in the boards. The street learns of the family only what leaves the house: voices, a door, a person in the yard, an answer at the door. W2a uses the knock only. |
 | 4 | Meetings | A knock is a scene: code decides who, when and what they want; the **model decides what the family does** (five door options); the stranger's words come from a **hand-authored line pool chosen by code**, never from the model, in W2a. A person met on a trip is W2c; someone seen from the gap is W2b. |
 | 5 | Word, rumours, trips | A deed is a fact that passes between households by `importance × ambiguity` and changes how they plan. A rumour of hope is a structured claim, true with chance 0.3 (est.), never confirmed by code. Trip risk is the people actually out, not `night.py:36-37` (32% scare, 6% not back, alone): about 3% a night trip at first (est.), rising as households run short. |
-| 6 | Cost | Door scenes: **≤ 6 asks, ≤ 1 a day, taken from a hard day cap of 56**. v22 spent 402 live asks; W2a expects about 420 and is held to 450 by the run cap. W2a's prompt lines total **≤ 122 estimated tokens** and sit **inside** `PROMPT_TOKEN_BUDGET`. |
+| 6 | Cost | Door scenes: **≤ 18 door asks a visit (was ≤ 6 asks; amended, §6.1), ≤ 1 a day, taken from a hard day cap of 56**. v22 spent 402 live asks; W2a expects about 420 and is held to 450 by the run cap. W2a's prompt lines total **≤ 122 estimated tokens** and sit **inside** `PROMPT_TOKEN_BUDGET`. |
 | 7 | Stages | W2a knock → W2b the street heard and seen → W2c trips among people → W2d danger at the house → W2e deeds and word → W2f rumours. Only W2a is specified: 1 new module, 3 data files, 11 existing files touched. |
 | 8 | W2a predictions | Ten, each with a counting rule and a v22 baseline. **W2a-2: at least half of the heard knocks (and at least 2) are answered, v22 baseline 0 of 0.** The result that proves W2a wrong is in §8.3. |
 
@@ -386,7 +391,7 @@ where a mistake would matter, whether the family hears a knock, is tested direct
 
 | Meeting | Stage | Code decides | Asks the model | What the stranger says, and who writes it | Asks |
 |---|---|---|---|---|---|
-| **A knock at the door** | W2a | who comes, when, what they need, how they react, what changes hands | the family: five door options, plus the family's ordinary options | **A hand-authored line from a pool, chosen by code** by purpose, urgency and temperament (§4.3) | ≤ 6 a scene, ≤ 1 a day |
+| **A knock at the door** | W2a | who comes, when, what they need, how they react, what changes hands | the family: five door options, plus the family's ordinary options | **A hand-authored line from a pool, chosen by code** by purpose, urgency and temperament (§4.3) | ≤ 18 door asks a visit (was ≤ 6 a scene; amended, §6.1), ≤ 1 a day |
 | **Someone seen from the gap** | W2b | whether anyone passes; what is seen (§3.3) | nobody, unless the house is already talking | nothing is said; a `Now` line of what is seen | 0 |
 | **A person met on a trip** | W2c | who is out and where; the outcome | the leaver (and a companion): 2 options | from the same pool kind (`street` slots); model-written only after the gate in §4.3 | ≤ 2 an encounter |
 | **A person at the back door, at night** | W2d | the approach, the noise | the sleepers and watchers | words only if the person speaks (`demand`, `plead` slots) | ≤ 4 an event |
@@ -406,10 +411,31 @@ where a mistake would matter, whether the family hears a knock, is tested direct
 4. **Q7.** `Quiet.hear_knock`, the sibling of `hear_rain` (`quiet.py:342-381`): if the house is already playing a stretch, the knock is a trigger
    inside it and its cap grows by the reserved allowance; otherwise it plays the **kitchen** if anyone awake is in it (the door is there), else the room with most awake
    (whose people then choose whether to go to the door), `begin(stretch, 6, reserved=True)` (`quiet.py:393-397`) and `ask`s everyone awake in that room.
+   - **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** the stretch begins with `DOOR_ASKS` = 18, not 6. **Every played turn the visitor is at the door, everyone
+     awake who perceives the door (`p.door`) is asked** (`Quiet.door_asks`), whatever else they have to answer, until
+     the visit has made 18 door asks (`Quiet.door_full`). A door ask is limited by the visit's 18 and the day's 56, not
+     by the stretch's own cap, which still holds everyone else's asks (`Quiet.spent(p)`). A door ask is not a quiet ask:
+     it does not count against the day's 12 (`QUIET_ASKS`). How a visit ends is unchanged: given, refused, or gone after
+     6 turns with nothing from the house. *Why:* in `reports/probe_door.md` scene 8, two turns of three people spent the
+     6 asks; the man knocked again at 09:51 and nobody was asked, so a real family that had watched an old, thin man
+     stand at its door for nine minutes did nothing (§2 there). 18 is 6 turns of 3: a visitor who stays until they give
+     up is answerable at every turn, the second knock's included. A Q7 stretch that ends because nobody in its room
+     perceives the door (`reports/w2a_fixes.md` fix 3) still frees what is left; the turns after it are not played.
    Skipped, as Q6 is when `rain_action` is false for all (`world.py:738-740`; `reports/v22_fixes.md:79-83`), only if nobody is awake after the wake draws.
-5. **Played turns (3 minutes each).** What each option does:
+5. **The visitor speaks first.** **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** in the minute of each knock, after the knock, the visitor says one line through the
+   shut door, heard in words by everyone who hears that knock in words (`Quiet.door_speak`). At the first knock it is a
+   `voice_ask` line; a visitor with a child names the child and their age in it (a `first` line, by disposition, §4.3).
+   At a later knock it is a short ask again (`insist` if urgency ≥ 0.8, else `again`), as after a call. *Was:* "the
+   visitor replies **next turn** with a `voice` line" only after a `door_call`, so a visitor who was not called to said
+   nothing until they were sent away. *Why:* in all eight scenes of `reports/probe_door.md` the stranger stood silent on
+   the step for a full turn; no need, no child and no "please" reached the family, and `door_give` was never offered.
+   A person who knocks on a boarded house where they have heard people calls out ("Hello? I'm sorry to knock…"); the
+   pool's `voice_ask` lines were written to be said through a shut door. This changes what the family is shown, as
+   §8.3's first row asks, not what the street does.
+   **Played turns (3 minutes each).** What each option does:
    - `door_look`: a sight percept to the actor (§3.3), nothing else changes.
-   - `door_call` (speech): the words go through the door; the visitor replies **next turn** with a `voice` line.
+   - `door_call` (speech): the words go through the door; the visitor replies **next turn** with a `voice` line (amended:
+     having spoken at the knock, an `insist` or `again` line).
    - `door_open`: this turn unbars it (O4); next turn the envoy is on the step, described, and says its `open` line.
    - `door_give`: only if the visitor asked for water and the house holds any; code moves `min(3 L, store)` out of the kitchen's tap water (then the bin,
      the order of `truth.py:91`) into the household's stock; the visitor says `given` and leaves.
@@ -418,6 +444,16 @@ where a mistake would matter, whether the family hears a knock, is tested direct
 6. **After.** The visit is a **deed** (§5.1) in `World`; the household's stock, *kind*, and *has_surplus* for no. 9 are updated; the chronicle gets
    `knock`, `door_line`, the family's door acts, and `door_end`; each person who was at the door gets one `sure` line of the outcome ("you handed a woman at
    the door two bottles of water"); the stretch closes.
+   - **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** **each one's line holds only what they perceived.** The visitor's need ("who asked for water") is in a
+     person's sure line and next day's block A only if that person heard words saying it (a line of `voice_ask`,
+     `open_ask` or `again`); the visitor is described by their face ("a woman of about forty-five") only to someone who
+     looked or was in the kitchen with the door open, by their voice ("a woman") to someone who only heard them, and as
+     "someone" otherwise. Whoever heard any knock in words, or heard the visitor speak, has a line. *Was:* "who asked
+     for …" whenever the visitor had said anything (`quiet.py:750`, `if sc["said"]`), and the face for everyone if
+     anyone had looked. *Why:* in every refused scene of `reports/probe_door.md` the record said "you told a woman of
+     about forty-five, who asked for water, to go away" when she had asked for nothing: the code's truth in the
+     family's memory, the boundary `CLAUDE.md:21-24` draws. The kitchen's view of the door shows each person the last
+     line *they* heard, not the last line said.
 
 ### 4.3 The stranger's words
 
@@ -432,6 +468,14 @@ where a mistake would matter, whether the family hears a knock, is tested direct
   | `given` | after `door_give` | "God bless you. I won't forget this." |
   | `refused_polite` / `refused_flat` | after `door_refuse`, by temperament | "I understand. I'm sorry to have bothered you. Look after yourselves." / "Right. Never mind." |
 
+- **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** **a `first` line** (in `voice_ask_water` and `voice_ask_food`, 6 each): said at the first knock by a household with a
+  child, 3 for a helper and 3 for any other disposition (guarded in register). Code puts in `{kids}` a sentence that
+  names each child and their age, true of the household: "I've a little boy at home, he's six." or "I've two at home,
+  a girl of five and a boy of five." The number words in it are the household's own, the one exception to "no number
+  word". **A line that refers to an ask** (`after: ask`: "I'm sorry I asked", "No, I understand. I'm sorry. I'll leave
+  you be.", "Thanks for nothing", "I'll find it somewhere else") is said only once the visitor has asked
+  (`street.line`, `v["asked"]`); `reports/probe_door.md` §2 found three of eight parting lines reading as if the family
+  had heard an ask that was never made.
 - **Rules for a line:** at most 25 words; no house number and no weekday; nothing outside the family's known world (no radio, no police);
   never says what the family should do or must feel (a request is allowed, a duty is not); it states a need the household really has
   (the envoy's `ask_water` means the household's `need_w` is above 0.5). A line is chosen by
@@ -534,26 +578,38 @@ quiet, a family that stays in is afraid, not prudent, and the family can find th
 | Q1/Q2 stretches, within the day's 40 | 8 each | 8 each | `quiet.py:43` |
 | Q5 the evening, reserved | ≤ 8 | ≤ 8 | `quiet.py:48` |
 | Q6 rain, reserved | ≤ 8 | ≤ 8 | `quiet.py:88` |
-| **Q7 the door, reserved** | none | **≤ 6, ≤ 1 a day** | new |
+| **Q7 the door, reserved** | none | **≤ 18 door asks a visit, ≤ 1 a day** (was ≤ 6; amended) | new |
 | **Day cap** | implicit 56 | **`DAY_MAX = 56`**, checked in `spent()` (`quiet.py:384-388`) | new; priority by time |
-| Worst case without the cap | 56 | 62 | |
+| Worst case without the cap | 56 | 62 (amended: 74; the cap holds it at 56) | |
 
 - **Why 6.** The first turn asks everyone awake in the room, 2.16 persons on average at a daylight minute (B7 in §11), the second asks those still engaged, so a
   scene costs about 4.5 asks (est.). A reserve of 6 covers two turns of three.
+- **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** **why 18, not 6.** Two turns of three are not a visit: a visitor who waits knocks again after 3 turns and goes after
+  6. In `reports/probe_door.md` the 6 were spent by 09:45 in every scene; scene 8's second knock, at 09:51, asked
+  nobody. 18 is 6 turns of 3 people, so a visitor who stays until they give up is answerable at every turn. A visit
+  that is refused or given in the first turn still costs only that turn's asks (the fake probe:
+  `runs/door_heard/probe_check.stdout.txt`, 3 to 17 door asks a scene).
+- **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** **what 18 does to the day cap, not changed here.** `DAY_MAX` (56) and `KNOCK_UNDER` (52) are as before. A knock
+  with 51 asks spent still begins, and the day cap then stops it after 5 asks; a door scene of 18 after 40 asks leaves
+  Q5's evening none of its 8. Whether to raise the day cap, or defer a knock that cannot have its 18, is for the user.
 - **Why Q7 is not starved.** A knock is only between 07:30 and 17:30; Q5 starts at 19:00 (`quiet.py:48`), so Q5 comes after it. Where Q6 and Q7 meet, whichever begins
   first has its asks first. A visit that would begin with fewer than 52 asks spent is deferred, not run with no one to ask (§4.2.2).
 - **v22's busiest day** (day 9): morning 24, Q2 8, Q6 8 (= 40 by 14:00), a knock at 14:00 adds ≤ 6 → 46, Q5 adds 8 → 54 ≤ 56. No starvation (B3, B12).
+  **Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** with 18, a knock at 14:00 can add up to 16 before the day cap (→ 56), and then Q5 has none. Starvation is now
+  possible on such a day.
 
 ### 6.2 A 10-day run
 
 | | v22 | W2a, expected | W2a, bound |
 |---|---|---|---|
-| Day-scene asks, days 3–10 | 342 | 342 + about 4 scenes × 4.5 = 360 | 342 + 8 × 6 = 390 |
+| Day-scene asks, days 3–10 | 342 | 342 + about 4 scenes × 4.5 = 360 | 342 + 8 × 6 = 390 (amended: 342 + 8 × 18 = 486) |
 | Night asks, nights 3–9 | 32 | 32 (nights untouched) | 32 |
 | Night-mind asks, minds 3–9 | 28 | 28 | 28 |
 | **Live total** | **402** | **about 420** | **450** |
 
-The bound of 450 holds if the non-door asks do not exceed v22's. It is **enforced** by the run's own cap, set to 450, not 470 (`runs/v22/run_capped.py`); the run
+**Amended (`reports/door_heard_impl.md`, from `reports/probe_door.md`):** the bound is now 486 + 32 + 28 = 546, over the run cap of 450, which is unchanged; the run would stop at 450 and
+resume from its cache. The expected total is not re-estimated here: it needs a scene's cost under the new rule, which
+only a run can give. The bound of 450 holds if the non-door asks do not exceed v22's. It is **enforced** by the run's own cap, set to 450, not 470 (`runs/v22/run_capped.py`); the run
 stops cleanly there and resumes from its cache. The busiest calendar day in v22 was 56 asks (day + night + mind, days 8 and 9; B11), so the day cap of 56 and the run cap
 are separate limits. A day scene stays far under the per-scene call cap of `config.json` (`max_calls_per_morning` 150).
 
@@ -625,7 +681,7 @@ households, trips among people, a model-written stranger, a standing line, a cha
 | File | Change |
 |---|---|
 | `truth.py` | `World.street` (the state, guarded by `Guarded`, `truth.py:34-45`); the street is advanced from `Quiet.tick`, **not** from `World.advance_to`, so the copy `next_change` makes (`truth.py:147-161`) stays cheap |
-| `quiet.py` | `Quiet.tick` (`:255`) advances the street; `world_events` (`:740`) and `next_event` (`:718`) add the next visit; `step` (`:702`) calls `hear_knock`, new (sibling of `hear_rain`, `:342`); `turn` (`:760`) the played branch; `play` (`:961`) starts the Q7 stretch with 6 reserved; `spent` (`:384`) gets `DAY_MAX`; `sense` (`:295`) sets `p.door`; `items` (`:919`) and `transcript` (`:945`) record the knock and the street log |
+| `quiet.py` | `Quiet.tick` (`:255`) advances the street; `world_events` (`:740`) and `next_event` (`:718`) add the next visit; `step` (`:702`) calls `hear_knock`, new (sibling of `hear_rain`, `:342`); `turn` (`:760`) the played branch; `play` (`:961`) starts the Q7 stretch with 6 reserved (amended: 18, and every turn of a visit asks whoever perceives the door, §4.2.4); `spent` (`:384`) gets `DAY_MAX`; `sense` (`:295`) sets `p.door`; `items` (`:919`) and `transcript` (`:945`) record the knock and the street log |
 | `world.py` | `Person.door` (`:304`); `options_for` (`:532`) the five door options (like the one at `:595-597`); `_prompt_for` (`:1086`) the door `Now` lines next to `:1123`; `apply` (`:1635`) the door kinds, with a case like `collect_rain`'s (`:1833-1844`); `KIND_DONE` (`:98`) and `line_text` (`:1577`) |
 | `talk.py` | `SPEECH` (`:8`) gets `door_call`, `door_refuse`; `act_of` (`:15`) leaves the door ids as their own kinds; `Newness` (`:64`) treats a door act as new the first time in a scene |
 | `data.py` | `HOUSE_THINGS` (`:135`): a variant for door scenes naming "the people at the door" (as `with_yard`, `:150`), because the house line says "Do not mention any other object or place" |
@@ -644,7 +700,8 @@ households, trips among people, a model-written stranger, a standing line, a cha
 5. T5 for any prompt, `block` is the same with and without a door state; the door lines total ≤ 140 tokens.
 6. T6 a knock at 07:30–17:30 only; ≤ 1 a day; deferred when 52 asks are spent; never in the bathroom; a resting person wakes by the draw.
 7. T7 the door options exist only in a scene, in the kitchen; `door_give` only with water to give; `door_open` only when shut.
-8. T8 the Q7 stretch ≤ 6 asks, and the day ≤ 56.
+8. T8 the Q7 stretch ≤ 6 asks, and the day ≤ 56. (Amended: a visit ≤ 18 door asks, and the day ≤ 56;
+   `test_t8_a_visit_asks_at_most_18_at_the_door_and_a_day_at_most_56`.)
 9. T9 every stranger's line in the pool is ≤ 25 words, has no digit or weekday, and no word from a list of what the house does not have.
 
 **The live test:** v16 seed 2, `--days 10`, `cache/v23` copied from `cache/v16` (as v22 did), through a capped runner at 450. The plan, with the printed first-visit
@@ -676,7 +733,7 @@ schedule and the scorer's sha256, is written and hashed **before** the first liv
 | **W2a-5** | **The house acts outward more than in v22.** At least 5 outward acts on at least 3 different days or nights, at least 3 of them door acts. | `went_out` and `got_up`/`at_door` once per leaver per night (`w1_score.py w11`), `collect_rain`, and the door acts above | **2** on 2 days (N5 `went_out`; D6 `collect_rain`), 1 by `w11` alone (B2) |
 | W2a-6 | **The loop gives way** (jointly with the v22 fixes, §8.4). At most 4 of the 32 person-days have an exact repeat, and at most 12 acts sit in repeated texts. No stranger's line is repeated word for word in the run more than once. | the exact-repeat rule over the 326-or-so speech acts of days 3–10 | **7 of 32; 24 acts; 9 distinct texts** (B4; equal to `reports/v22_gaps.md:117-123`) |
 | W2a-7 | **The talk reaches the person at the door.** On at least 60% of the days that follow or contain a heard knock, at least one speech act matches FOLK. | days d with a heard knock on d−1 or d; speech acts of d | **0 acts on 0 days** of 326 acts (B5b) |
-| **W2a-8** | **Cost is bounded.** Live asks of days 3–10 ≤ 450; each day-scene's asks ≤ 56; each Q7 stretch ≤ 6 asks; at most 1 a day. | `meta.answers_live`; `quiet.asks.day`; Q7 stretches | **402**; days ≤ 48; none (B3; §11 cmd 3) |
+| **W2a-8** | **Cost is bounded.** Live asks of days 3–10 ≤ 450; each day-scene's asks ≤ 56; each Q7 stretch ≤ 6 asks (amended: each visit ≤ 18 door asks); at most 1 a day. | `meta.answers_live`; `quiet.asks.day`; Q7 stretches | **402**; days ≤ 48; none (B3; §11 cmd 3) |
 | W2a-9 | **The prompt does not grow.** The largest estimate of any prompt ≤ 2650; the test T5 passes. | `estimate_tokens(system + prompt)` over the live prompts | **2602**, two prompts over 2600 (§11 cmd 3) |
 | W2a-10 | **Truth.** Every `door_give` changes the stores by the exact amount; each visitor's stated need matches its household's computed need; no `TruthLeak`; days 1–2 replay as before (T4). | the street log against the chronicle; the run finishing | n/a (no door events) |
 
@@ -693,7 +750,7 @@ move this number. W2a-9's 2650 is v22's 2602 plus 48 for the case in which nothi
 | W2a-2 holds, W2a-3 and W2a-4 fail | The family **talks to the door and keeps it shut**: a reason produces conversation, not an act. | The reason is too small, or the boards are too strong: a stranger who offers something (`trade`, W2b) is the next reason; read the scenes (§8.4) first |
 | W2a-2, 3 and 4 hold, W2a-5 fails | The door moves the house and the rest of it stays put. This is **not** W2a wrong: W2a gives no reason to go out (§7.2). | W2c (trips among people), W2f (a place to go) |
 | W2a-2 to W2a-5 hold, W2a-6 and W2a-7 fail | The door acts occur but do not displace the loop: the family keeps accusing | The reason is a side event. The loop is in the minds, and the next work is the memory (`reports/v22_gaps.md:262-269`), not more street |
-| W2a-8 or W2a-9 fails | A cost limit, not a hypothesis. Cut the Q7 reserve to 4 or drop `door_look`. | |
+| W2a-8 or W2a-9 fails | A cost limit, not a hypothesis. Cut the Q7 reserve to 4 or drop `door_look`. (Amended: cut the door asks a visit below 18, or drop `door_look`; with 18, W2a-8's 450 can be reached, §6.2.) | |
 
 **The hypothesis W2a tests:** *a stranger at the door with a stated need makes the house act at the door.* It is wrong if W2a-2, W2a-3 and W2a-4 all fail.
 
```

## 6. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` removed from the environment. Outputs in `runs/door_heard/`.

| Command | Output file | Result |
|---|---|---|
| `git stash push -- quiet.py street.py world.py streetdata/lines.json runs/w2a_impl/write_lines.py`; `python -m unittest -v test_morning.DoorHeardTest`; `git stash pop` | `red.stdout.txt` | 5 failures, exit 1 (§2.1) |
| `python -m unittest -v test_morning.DoorHeardTest.test_c2_…` (the witness fix removed) | `red_c2.stdout.txt` | 1 failure, exit 1 |
| `python -m unittest -v test_morning.DoorHeardTest test_morning.KnockTest test_morning.KnockFixTest` | `green.stdout.txt` | 19 OK, exit 0 |
| `python runs/w2a_impl/write_lines.py` | `streetdata/lines.json` | 114 lines in 11 slots; before the edit it reproduced the file byte for byte (`git diff --stat` empty) |
| `python -m unittest test_morning` (alone) | `unittest.stdout.txt` | 307 tests OK, exit 0 (§3) |
| `python runs/probe_door/probe.py --fake` | `probe_fake.stdout.txt` | exit 0 |
| `python runs/door_heard/probe_check.py` | `probe_check.stdout.txt` | 8 of 8 OK, exit 0 |

**Changed files:** `quiet.py`, `street.py`, `world.py`, `streetdata/lines.json`, `runs/w2a_impl/write_lines.py`,
`test_morning.py`, `reports/w2_design.md`. **New:** this report and `runs/door_heard/`.
