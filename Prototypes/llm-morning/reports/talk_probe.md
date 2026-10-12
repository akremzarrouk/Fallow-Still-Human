# The talk probe: does the stranger become part of the family's day, and does Daniel come to know?

Mode: run. The plan is `reports/talk_probe_plan.md`. Its sha256 `b70eab2e…6dd9` was recorded at 2026-10-12T16:04:22Z,
HEAD `095931a`, before any live call, and it was the same at the end. The live run went from 16:04:25 to 16:11:35
UTC: **96 live asks** (cap 150; 32 in each scene, cap 60), exit 0. Paths are from `Prototypes/llm-morning/`. Raw
outputs are in `runs/talk_probe/`. No production file, test, prediction or counting rule was changed, and no scene was
run twice.

## Verdicts

**Validity: V1 to V5 pass**, so the predictions are read.

| # | Check | Result |
|---|---|---|
| V1 | `probe.py --fake` exits 0 for all three scenes and reaches `done` | exit 0; scenes 1, 3, 4 `done` (`fake.stdout.txt`) |
| V2 | each scene: `from_cache` = 123, no ask refused before `door_end` | 123, 123, 123; `stopped` None in all three |
| V3 | no topic option in any prompt before 09:45 | none, over 27 day prompts before 09:45 in each scene |
| V4 | each listener's claim equals the builder's, recomputed (as the plan reads V4 under A3) | 1 tell, 1 listener: equal |
| V5 | the guard holds (P3) | the highest count is 1 |

**Predictions:**

| # | Prediction (word for word) | Result | Verdict |
|---|---|---|---|
| P1 | Daniel learns of the visit by night 3 in at least 2 of 3 scenes. | **1 of 3.** Scene 4: Leo tells him at 09:48. Scenes 1 and 3: never, though `tell_daniel_visit` was offered at 10 and 11 asks with Daniel in the room. | **fails** |
| P2 | The visitor or the children are brought up after 10:00 in at least 1 of 3 scenes. | **0 of 3.** Every topic choice was at 09:45 or 09:48. After 10:00 a topic option was offered at 30 asks (8, 9 and 13) and never taken, and no words matched. | **fails** |
| P3 | Repetition guard: no person chooses one topic more than 2 times on day 3. | At most 1 (Leo in 1, Mara in 3, Elena and Leo in 4). | **holds** |
| P4 | The topic is not chosen at most chances: … at most 40% of the day-3 decisions that offered one. | **4 of 41 (9.8%).** | **holds** |
| P5 | Whoever is told keeps it into day 4. | Scene 4, the one scene that counts for P1: `Yesterday at 09:48, Leo told you that at 09:42 a woman knocked at the front door and asked for water for her girl and boy of five; that Elena told her to go away.` | **holds** (1 scene) |
| P6 | A told claim names the children where the teller heard them. | Scene 4: Leo heard the line; the claim names "girl and boy of five". Scene 3: Daniel was not told. | **holds in scene 4; scene 3 NOT TESTED** (no claim to count) |

The plan says: "P1 rests on ordinary asks only (no Q8, A2); if it fails, that is evidence for Q8, not for changing P1."
P1 stands as written. The fact that bears on Q8: in scenes 1 and 3 the ordinary asks did put the tell in front of
someone, at 10 and 11 asks, with Daniel in the room each time. The missing step was the choosing, not an ask at
his arrival.

**In one line:** the visit was now spoken of, but only in the first two turns after it. In scene 4 Leo told Daniel,
and Daniel at once challenged his mother for turning away "a desperate mother", a fact he had only from the claim.
In scenes 1 and 3, nobody told Daniel all day: they were offered it 21 times and chose the quarrel with him instead.

## 0. What the run did

- **The 09:42 answers are probe_door2's.** In each scene, 123 asks came from the copied cache. The client refuses
  every ask until `door_end` has run, and none was refused. The visit went as in `probe_after`: given in scenes 1 and
  3 (Elena refused, Mara gave), and refused in scene 4. It ended at 09:45.
- **Live from 09:45:** 32 asks in each scene. That is the rest of day 3, night 3's 4 asks and the 4 night minds.
  API requests equal live asks.
- **Day 3's asks:** 51 of 56 in each scene, 11 reserved. Q5 was refused at 19:00 in each scene ("no trip position
  today").
- **The budget fix** (`two_fixes_impl.md`) fired one Q1 that `probe_after` had refused: scene 4, 17:39, Daniel (fast,
  stage 2). `probe_after` refused it with "50 asks spent and the evening's 8 still owed reach the day's 56". No other.

## 1. The scenes

From `runs/talk_probe/read_talk.stdout.txt` and `runs/talk_probe/scene<k>.json`. "Offered" counts day-3 asks from
09:45 whose prompt listed a topic option.

### Scene 1: no child; Elena refused, Mara gave (client seed 101)

**Talk and tell decisions:**
- 09:45 Leo, `talk_visit`: *"Giving water away to strangers at the door when we have none ourselves isn't helping us
  survive, Mara."* Feeling wary. Reason: "We cannot afford to give away our stored water to random people when our own
  supplies are critically low."

**Offered and not taken:**

| Person | Offered | What they chose instead |
|---|---|---|
| Elena | `talk_visit` at 09:45; `tell_daniel_visit` at 09:48 and 16:57 | reassure (everyone, Leo) each time |
| Mara | `tell_daniel_visit` at 09:48, 16:54, 16:57 | `accuse_daniel` twice, silent once |
| Leo | `tell_daniel_visit` at 11:45, 11:48, 11:51, 16:54, 16:57 | `confront_daniel` twice, silent twice, `accuse_daniel` once |

**Daniel:** not told. At night he goes to sleep ("I am too weak to stand and my body simply gives out").

**Children named aloud:** none (scene 1 has no child).

**Night minds (kept):**
- Elena `[D3-030, D3-033]` "Mara gave water away to the stranger at the door because she has a good heart, even though
  we have none left to spare."; `[D3-038, D3-039]` "Leo is right to ration what little water remains so carefully…"
- Leo `[D3-030, D3-035]` "Mara gave away our precious water to a stranger while we starve."; and two others, about
  Daniel and his body.
- Mara `[D3-030, D3-033]` "We could not just turn her away with nothing when she was begging for it, even if we had
  to share what we had stored."
- Daniel: two memories, none of the visit: "…Leo and Mara only want to blame me."; "Leo took charge of the water
  rationing, and every drop now has to be counted." (warned S4 Mara, S8 leo take).

**Day 4's door lines:**
- Elena, Leo and Mara each have their block-A door summary, and a block-B line from the memories above.
- Daniel has none.
- Daniel's water line: about 50 and 45 litres, "Since yesterday, Leo shares it out by the cup".

### Scene 3: a boy of six; Elena refused, Mara gave (client seed 103)

The first door line: *"Hello? I'm sorry to knock. I've a little boy at home, he's six. We've no water left. Could you
spare a little?"*

**Talk and tell decisions:**
- 09:45 Mara, `talk_visit`: *"She was so thirsty and had nothing, I couldn't just leave her there without a drop."*
  Feeling defensive. Reason: "I had to help that poor woman at the door no matter what Leo says."

**Offered and not taken:**

| Person | Offered | What they chose instead |
|---|---|---|
| Elena | `talk_visit` at 09:45; `tell_daniel_visit` at 09:48, 16:54, 16:57 | `reassure_all` each time |
| Leo | `talk_visit` at 09:45 (chose `ration_water`); `tell_daniel_visit` at 09:48, 11:45, 11:48, 11:51, 16:54, 16:57 | `confront_daniel` four times, `accuse_daniel` twice |
| Mara | `tell_daniel_visit` at 16:54, 16:57 | `accuse_daniel` both times |

**Daniel:** not told. At night he sleeps.

**Children named aloud:** none, by day or at night.

**Night minds (kept):**
- Elena `[D3-029, D3-030, D3-033]` "I had to turn the woman away because we have nothing left, but Mara gave her water
  anyway."
- Leo `[D3-030, D3-031]` "Mara gave away our drinking water when we have nothing left ourselves…"
- **Mara `[D3-030, D3-036]` "I had to give her some of our water because she and her little boy had nothing left at
  all."** The boy is kept; in `probe_after` he was mentioned nowhere.
- Daniel: nothing of the visit.

**Day 4's door lines:**
- Block A as in scene 1.
- Block B: Mara's "…she and her little boy…"; Elena's and Leo's lines above.
- Daniel has none.

### Scene 4: a girl and a boy of five; Elena refused, nobody gave (client seed 104)

The first door line: *"I'm sorry to trouble you. I've two at home, a girl of five and a boy of five. Our water's gone.
Anything you could spare, I'd be grateful."*

**Talk and tell decisions:**
- 09:45 Elena, `talk_visit`: *"That woman had children to feed, but we have nothing left to give anyone."* Feeling
  pained. Reason: "I need to acknowledge what happened at the door so the children understand why I sent her away."
- 09:48 Leo, `tell_daniel_visit`: *"Daniel, a woman knocked at the front door a few minutes ago asking for water, and
  Mom sent her away."* Feeling weary. Reason: "Daniel just woke up, so he needs to know what happened while he was
  asleep."
  - Daniel's claim: *"Leo told you that at 09:42 a woman knocked at the front door and asked for water for her girl and
    boy of five; that Elena told her to go away."*
  - T1: no warning.

**Offered and not taken:**

| Person | Offered `talk_visit` at | What they chose instead |
|---|---|---|
| Leo | 11:45, 11:48, 11:51 | `confront_daniel` twice, silent |
| Daniel | 11:45, 11:48, 11:51, 14:51, 14:54 | reassure or confront Leo, confront Mara |
| Elena | 14:51, 14:54 | `reassure_all` |
| Mara | 14:51, 14:54, 14:57 | `accuse_daniel` |

**Daniel's decisions after he is told:**

| Time | Option | Words | Feeling | Reason |
|---|---|---|---|---|
| 09:48 | `confront_elena` | *"Mom, you can't just turn someone away when they're begging for water."* | anxious | "I need to know why Mom sent a desperate mother away from our door." |
| 11:45 | `reassure_leo` | "Leo, I shouldn't have shut you out last night, but I'm going to keep us safe." | anxious | |
| 11:48 | `reassure_leo` | "I had to see for myself, Leo, but I'm back now and I'm looking out for us." | anxious | |
| 11:51 | `confront_leo` | "Leo, you can't just judge every move I make…" | defensive | |
| 14:51 | `confront_mara` | | defensive | |
| 14:54 | `confront_mara` | "Mara, you ate a portion right in front of me when we had almost nothing left." | resentful | |
| 14:57 | silent | | | (routine) |
| 17:39 | `confront_mara` | | resentful | (the Q1 the budget fix let through) |

At night he sleeps.

His 09:48 prompt (`daniel_0948.stdout.txt`) held the claim, `- 09:48: Leo told you that … for her girl and boy of five;
that Elena told her to go away.`, and under "Said and done in the kitchen this turn", Leo's words. Leo's words named no
child. "A desperate mother" in his reason can only come from the claim.

**Children named aloud:**
- 09:45 Elena: "That woman had children to feed…". This is before 10:00, so it does not count for P2.
- Nobody else, by day or at night.

**Night minds (kept):**
- Elena `[D3-029, D3-033]` "I had to turn a desperate mother away because we have nothing left, and the pain of it
  stays heavy in my chest."; **`[D3-037, D3-038]` "Daniel questioned me for turning her away, but he does not
  understand that we have no water to spare and the street is too dangerous."**
- Leo `[D3-032, D3-033]` "A mother came begging for water for her small children, but we had nothing left to give
  anyone."
- Mara `[D3-030]` "That poor woman came begging for water with her empty bottles while we have nothing left to give."
- Daniel: nothing of the visit. "They accuse me of failing…"; "My body is giving out…".

**Day 4's lines:**
- **Daniel's block A:** `- Yesterday at 09:48, Leo told you that at 09:42 a woman knocked at the front door and asked
  for water for her girl and boy of five; that Elena told her to go away.`
- Elena, Leo and Mara: their door summaries, and block-B lines from the memories above.
- Daniel's water line: about 30 and 45 litres, "It is also used to flush the toilet and to wash." Nobody made a water
  rule in this scene's day.

## 2. T1 and the Q1s

- **T1:** 0 warnings in 1 tell. Leo's words name the front door, the woman, the water and "Mom".
- **Q1 that `probe_after` refused and this run fired:** one, scene 4 at 17:39, Daniel (fast, stage 2). In
  `probe_after` it was refused with "50 asks spent and the evening's 8 still owed reach the day's 56". Scenes 1 and 3
  fired no Q1.

## 3. Reading each scene

The question for each (`CLAUDE.md:16-19`): would a real family in that room, that hungry, do this, and why? This
section is a reading, not a count.

**What all three share.** Right after the visit, the visit is now what someone says something about. Leo scolds
Mara (scene 1), Mara defends herself (scene 3), Elena explains herself to the children (scene 4). Each line is in
character and about the door, which `probe_after` never had. From 09:51 the day goes back to Daniel's night out, as in
`probe_after`: every Q2 after that is a grievance with Daniel, and every topic option after 10:00 is passed over.

**What Daniel does with what he was told (scene 4).**
- He takes it as a reason to challenge his mother at once: "Mom, you can't just turn someone away when they're
  begging for water". And he does it in terms of what he was told and not what Leo said: "a desperate mother".
- A real eldest son who came in a minute late and hears his mother turned away a woman with two small children
  might well say exactly that. It is also Daniel at odds with everyone, and his stance costs him nothing.
- Elena kept it. Her night mind holds "Daniel questioned me for turning her away", which ties the visit into the
  family's quarrel the way a real one would.
- After 09:48 he never comes back to it. He was offered `talk_visit` five times and chose his fights with Leo and
  Mara. His night mind keeps nothing of it.
- Next morning he has the told line in block A, so day 4 can still carry it.

**Whether anyone says the children aloud.**
- Once: Elena in scene 4, "That woman had children to feed", at 09:45.
- In scene 3 nobody says "the boy" aloud. But Mara's night mind keeps "she and her little boy". In `probe_after` the
  boy was gone after 09:42.
- In scene 4 the children reach Daniel only through the claim, and he uses them. Leo, the one who told him, did not
  say them aloud. A real Leo telling his brother in passing might well leave them out; Daniel then knows something
  his brother did not say.
- That gap comes from the design (§3, words versus claim, left for v2). It is the clearest place in this run where
  the claim outruns the words.

**Whether a teller avoids telling when the story shows their own refusal.**
- Elena, whose refusal is in every account, was offered `tell_daniel_visit` at 2 asks in scene 1 and 3 in scene 3. She
  never took it, and reassured instead each time. A mother avoiding telling her eldest that she sent a thirsty woman
  away, and that her daughter defied her, is believable.
- But the data do not single her out:
  - Leo, who did nothing at the door, passed on it 5 times in scene 1 and 6 in scene 3, choosing to confront or
    accuse Daniel.
  - Mara, the giver, passed 3 and 2 times, choosing to accuse Daniel.
- So in scenes 1 and 3 nobody tells, whoever's act it shows. In scene 4, where the refusal was Elena's and nobody
  defied her, Leo told at the first chance, and Elena had already spoken of it to the room.
- What these scenes show is that the quarrel with Daniel wins over the news. A real family on day 3, starving, with
  the eldest just back from a night out that came to nothing, might well do this for an hour. For a whole day, in a
  kitchen they share for hours, it is less likely. In scenes 1 and 3 Daniel sat with Elena and Mara from 09:51 to
  11:45, and the give is the thing that happened to them that day.

**"None left" stays.** Elena "none left to spare" (scene 1); Leo "nothing left ourselves" (scene 3); Elena, Leo and
Mara "nothing left" (scene 4). Day 4's water line says about 95 litres (scenes 1 and 3) and about 75 (scene 4). This was not predicted. The design does not
touch claims about the stores (§3).

**One thing seen in the prompt.** Daniel's 09:48 prompt shows Leo's line to him in the third person: "1. Leo tells
Daniel about the woman at the front door…". The turn's "Said and done" list is one text for everyone in the room, as
it already is for an accusation aimed at someone. That is how `world.py` builds `so_far`, and nothing was changed
here.

## 4. Commands and output

All from `Prototypes/llm-morning/`.

**Before any live call:**
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/talk_probe/probe.py --fake      exit 0   fake.stdout.txt (stderr empty)
scene 1 (…, client seed 101): reached done; counts {'live': 40, 'from_cache': 123, 'api_requests': 40}
scene 3 (…, client seed 103): reached done; counts {'live': 37, 'from_cache': 123, 'api_requests': 37}
scene 4 (…, client seed 104): reached done; counts {'live': 37, 'from_cache': 123, 'api_requests': 37}
live asks in all: 114                      (fake answers)
```
The reading script was also checked on a kept copy of a fake run, in the session's scratchpad and not in the
repository.

```
runs/talk_probe/plan_frozen.txt
plan:   b70eab2e6c2624a9b0803b72c72a67b96b2086b63d9548d50ab868a1c32a6dd9 *reports/talk_probe_plan.md
probe:  05d092792557281b00a4356ae115b9510eec3f0eae88a9f7ea93d26c56f58208 *runs/talk_probe/probe.py
reader: ce5d612a747a45a4d07326ea55355ebfa1b159266abd69bb4c897e71ab8e6222 *runs/talk_probe/read_talk.py
time:   2026-10-12T16:04:22Z
HEAD:   095931a22c78b831a8ff439594cfc9ceeb8ac549
git diff --stat: 0 lines;  cache/talk_probe exists before the run: no;  runs/talk_probe/ledger.json exists before the run: no
```

**The run.** `GEMINI_API_KEY` came from the session's environment; the process read it and wrote it to no file.
```
$ .venv/Scripts/python.exe runs/talk_probe/probe.py --live      exit 0   live.stdout.txt (stderr empty), 16:04:25 to 16:11:35 UTC
scene 1 (no child, helper, urgency under 0.8, client seed 101): reached done; counts {'live': 32, 'from_cache': 123, 'api_requests': 32}
  visit 09:42 to 09:45; outcome given; acts [('09:42', 'elena', 'door_refuse'), ('09:42', 'mara', 'door_give')]
  stretch 09:42 to 09:51 Q7 in kitchen: 11 asks;  11:45 to 11:54 Q2 in brothers_room: 8 asks;  16:54 to 17:03 Q2 in kitchen: 8 asks
  day 3 asks {'all': 51, 'reserved': 11}
scene 3 (a child, …, client seed 103): reached done; counts {'live': 32, 'from_cache': 123, 'api_requests': 32}
  stretch 09:42 to 09:51 Q7: 11 asks;  11:45 to 11:54 Q2: 8;  16:54 to 17:00 Q2: 8
scene 4 (children, …, client seed 104): reached done; counts {'live': 32, 'from_cache': 123, 'api_requests': 32}
  visit 09:42 to 09:45; outcome refused; acts [('09:42', 'elena', 'door_refuse'), ('09:42', 'mara', 'door_look')]
  stretch 09:42 to 09:51 Q7: 11 asks;  11:45 to 11:54 Q2: 6;  14:51 to 15:00 Q2: 8;  17:39 to 17:42 Q1: 2
live asks in all: 96
```

**Reading the records** (read-only):
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/talk_probe/read_talk.py > runs/talk_probe/read_talk.stdout.txt      exit 0, 134 lines, stderr empty
V2 from_cache and stop, per scene: {1: (123, None), 3: (123, None), 4: (123, None)}
V3 prompts before 09:45 with a topic option: {1: [], 3: [], 4: []}; … day prompts before 09:45 {1: 27, 3: 27, 4: 27}
V4 (teller, listener) claims equal to the builder's: [(4, '09:48', 'leo', 'daniel', True)]
V5 / P3 topic choices per (person, topic), day 3: {1: {('leo', 'visit'): 1}, 3: {('mara', 'visit'): 1}, 4: {('elena', 'visit'): 1, ('leo', 'visit'): 1}}
P1 scenes that count: [4]
P2 scenes that count: []
P3 counts > 2: []
P4 decisions offering a topic option: 41; choosing one: 4; share 0.0975609756097561
P5 … {4: ['Yesterday at 09:48, Leo told you that at 09:42 a woman knocked at the front door and asked for water for her girl and boy of five; that Elena told her to go away.']}
P6 per scene, Daniel's claims (minute, teller, teller heard the line naming the children, names them): {3: [], 4: [('09:48', 'leo', True, True)]}
T1 over all tells: 0 warnings in 1 tells
$ (inline) scene 4, Daniel's 09:48 prompt > runs/talk_probe/daniel_0948.stdout.txt      exit 0
$ (inline) P2's offers from 10:00 > runs/talk_probe/offers_after_1000.stdout.txt      exit 0
scene 1: 8 …  scene 3: 9 …  scene 4: 13 …  total 30
```

**At the end** (`runs/talk_probe/end_checks.txt`):
```
plan sha256 now:   b70eab2e6c2624a9b0803b72c72a67b96b2086b63d9548d50ab868a1c32a6dd9   (= frozen)
probe sha256 now:  05d092792557281b00a4356ae115b9510eec3f0eae88a9f7ea93d26c56f58208   (= frozen)
reader sha256 now: ce5d612a747a45a4d07326ea55355ebfa1b159266abd69bb4c897e71ab8e6222   (= frozen)
plan copy equal:   yes
git diff --stat: []      git diff --cached --stat: []
HEAD: 095931a22c78b831a8ff439594cfc9ceeb8ac549
key search (grep -rlF over the repository, but .venv, __pycache__, .git, Library, node_modules): 0 files
ledger: 96 [('scene1', 101, 'done', None, 0, 32), ('scene3', 103, 'done', None, 32, 64), ('scene4', 104, 'done', None, 64, 96)]
```

**Raw outputs in `runs/talk_probe/`:**
- the probe and its run: `probe.py`, `plan.md` (a copy of the plan), `plan_frozen.txt`, `fake.stdout.txt`,
  `fake.stderr.txt` (empty), `fake.exit.txt`, `live.stdout.txt`, `live.stderr.txt` (empty), `live.exit.txt`,
  `live.started_utc.txt`, `live.ended_utc.txt`, `ledger.json`;
- the records: `scene1.json`, `scene3.json`, `scene4.json` (every prompt and answer from 09:42, the topic scan of every
  day-3 prompt, the topics, tells and beliefs, the night minds' input and answers, the blocks);
- the reading: `read_talk.py`, `read_talk.stdout.txt`, `daniel_0948.stdout.txt`, `offers_after_1000.stdout.txt`,
  `end_checks.txt`;
- `report.md` (a copy of this report) and `talk_probe-all.md` (merged).

The live caches are in `cache/talk_probe/`.
