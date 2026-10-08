# merged: all documents

Merged by `merge-slice-docs.py` from the 3 Markdown files in `Prototypes/llm-morning/runs/v22gaps/merged/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`days_v22.md`](#days_v22md)
- [`days_v22_plan.md`](#days_v22_planmd)

---

## report.md

### v22 gaps: why three v22 failures happen

Mode: investigate. Read only: no code, test or prompt was changed and the API was not called. Paths are relative to
`Prototypes/llm-morning/`. The scripts and raw outputs are in `runs/v22gaps/` (cited by path); the prompts quoted are the
live prompts of `cache/v22` (entries 147 on, the 402 live asks). Clock stamps are the run's own. Where a thing was looked for
and absent, it says NOT FOUND.

#### Commit

- **Commit `966d5b5`** (`966d5b5fa0bb58ae28e76c9516aaf1a457248358`): 40 files, 191,011 insertions. It holds
  `reports/days_v22.md`, `reports/days_v22_plan.md`, `runs/v22/` (incl. `merged/`), `runs/w22/` (the scorer, its
  fake run and checks) and `cache/v22/`; the same kinds of files as v21's commit `3be6e10`. `runs/v6`'s three replay files
  were left out, as before. No file outside those four paths is in it (0).
- **The API key is in no file of the commit.** Before the commit, `git grep --cached` for the key's middle part and for the
  general shape `AQ.` plus 30 or more characters found nothing (exit 1); after it, the same two searches over `HEAD` found
  nothing (`runs/v22gaps/commit_checks.txt`). A `grep -rl` over the whole repository finds the key's middle in no file.
- **After the commit:** `git diff --stat` is empty; `git status --short` shows `runs/v22gaps/` (this investigation, not
  committed) and the three old `runs/v6` replay files.

#### Answers, short

| # | Question | Answer |
|---|---|---|
| 1 | Why does Mara say one line seven times, and does the own-words hiding apply? | **The hiding applies** on day 3 and in every stretch (306 of 342 day prompts carry the block, **0** quote a line of their own). The repeats come from **standing lines**: Mara's night-mind *intent* ("I will ask Daniel why he went out… with nothing to show for it") is in all 7 prompts, with 5 more that say he came back with nothing (four facts and her own night thought). A second channel is open: the **night mind quotes the person's own spoken line** and block B shows it back verbatim (Leo, day 7: 9 prompts, 4 verbatim repeats). |
| 2 | Words vs deeds: does a day's trip position reach the night? | **Yes, it does** (a promise line, the plan line, the person's own last words), on nights 8 and 9. Nights 6 and 7 had **no** position that day. **No option or chance depends on a position** (NOT FOUND). Daniel read "You said you would go… If you are going, it is now." and chose `sleep` twice. |
| 3 | Day 7 17:18 Q6 | `collect_rain` is offered only while the bin is not out (`world.py:594`); the bin went out on day 6 and nothing ever brings it in. Q6 itself does not look at the options. |
| 4 | Cost, day 9 Daniel, 2602 | **1205 of the 2602 tokens sit outside the trimming budget**; the part the budget sees is 1397 of 1400. Block A, B, C alone are 560. |

**An error in `reports/days_v22.md` (not corrected there, so that the commit stays as it was):** §2 day 3 says Mara's line
was "the same line 7 times in the morning". Counted exactly it is **7 lines of one frame on the day, 6 of them in the
morning, in two wordings** ("into the night": 3, "into the dark": 4; §1).

#### 1. Repeats

##### 1a. Mara, day 3: the seven lines

`runs/v22gaps/part1.txt` (script `runs/v22gaps/part1.py`). Mara's day 3 has 11 speech acts. The frame is "You went out into
the night/dark and came back with nothing, Daniel. Why did you even go?" Seven of the eleven; six in the morning (min 00–18),
one at 10:30.

| Time | Option | Words | Her prompt showed of her own earlier words (`Your own last words this morning`) |
|---|---|---|---|
| min 00 | `confront_daniel` | "You went out into the **night** and came back with nothing, Daniel. Why did you even go?" | no block (nothing said yet) |
| min 03 | `confront_daniel` | "…into the **dark**…" | "- min 00, you confronted Daniel." |
| min 06 | `confront_daniel` | "…into the **dark**…" | "- min 00, you confronted Daniel." "- min 03, you confronted Daniel." |
| min 12 | `confront_daniel` | "…into the **night**…" | "- min 03, you confronted Daniel." "- min 06, you confronted Daniel." "- min 09, you accused Daniel." |
| min 15 | `confront_daniel` | "…into the **dark**…" | "- min 06, you confronted Daniel." "- min 09, you accused Daniel." "- min 12, you confronted Daniel." |
| min 18 | `confront_daniel` | "…into the **dark**…" | "- min 09, you accused Daniel." "- min 12, you confronted Daniel." "- min 15, you confronted Daniel." |
| 10:30 | `confront_daniel` | "…into the **night**…" | "- min 12, you confronted Daniel." "- min 15, you confronted Daniel." "- min 18, you confronted Daniel." |

- **Word for word:** "night" 3 times (min 00, 12, 10:30) and "dark" 4 times (min 03, 06, 15, 18). The four other acts of
  the day are different (min 09 `accuse_daniel`: "You went out there in the dark and you still have nothing to show for it,
  Daniel."; 10:33; 17:39; 17:42, all about the same trip).
- **Her own earlier words were not in the prompt.** In each of the seven prompts the block holds the minute and the verb
  only, and the "What else happened this morning" memory holds her own lines the same way, e.g. at min 12: "- min 06: you
  confronted Daniel. You felt anxious." (`runs/v22gaps/mara_d3_*.txt`, one file per prompt).
- **What was in every one of the seven prompts** (`runs/v22gaps/part1.txt`, lines 22–110):
  - the night mind's intent, in block B: `- You meant to: "I will ask Daniel why he went out into the street with nothing to show for it."`
  - her own thought in block B: "Daniel went out into the night and came back before dawn with nothing in his hands."
  - four standing lines that say he came back with nothing: "About the neighbour's house: Daniel went there last night and came
    back with nothing."; "About going out at night: Daniel went to the neighbour's house last night and came back with
    nothing."; "- Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).";
    "- What was said yesterday about going out last night, where it was left: …then Daniel went to the neighbour's house
    anyway and came back with nothing."
  - the pattern block, which counts her turns and does not change her words: "What you have been doing: you have accused
    someone of taking it, 1 turn in a row." / "Nobody answered you differently from one time to the next."
- **So the sentence is the intent line, said again each turn.** "Why did you even go?" is the intent ("I will ask Daniel why
  he went out"); "night" and "dark" differ by sampling.

##### 1b. Is the own-words hiding applied on day 3+ and in quiet-day stretches?

**Yes.** The code:
- `world.py:1781-1782`: when anyone speaks, their own memory line is `you {verb}.` and their `said_lines` entry is
  `{clock}, you {verb}.`; "Their own lines reach them without the words: minute and verb only" (`world.py:1779-1780`).
  The others hear the words (`world.perceive`, `world.py:1561`).
- `world.py:1150-1151`: the block "Your own last words {when}:" lists the last 3 of those, in every prompt built by `prompt_parts`
  (`world.py:1140`). `apply` (`world.py:1625`) is called for quiet-day turns too (`quiet.py:1326`); `{when}` is "this morning",
  or "today" from minute 90 (`world.py:1140-1141`).

**The count over the live prompts** (`runs/v22gaps/part1.txt`, §1b): 342 day prompts; 306 have the block (154 under "this
morning", 152 under "today"; the 36 without are first asks, before anything was said); **0** lines of the block or of the
memory list quote the speaker's own words. Mara's own sentences appear verbatim in none of her later prompts
(`runs/v22gaps/part1b.txt`: only Leo has hits).

**But a second channel carries own words, and the hiding does not cover it.** `runs/v22gaps/part1b.txt`: in v22, 5 later
prompts held a person's own earlier sentence word for word (v21: 6), all Leo's, all in block B ("What yesterday left in you").
Counting the ones he repeated: Leo's day-7 prompts, **9 of them, held** "Risking your life doesn't give you the right to put
everyone else in danger by sneaking out without a word, Daniel." under "- About confronting Daniel: …", and **4 of his 9
answers repeat it verbatim** (min 03, 10:09, 17:18, 17:21; `runs/v22gaps/part1c.txt`). The path:
- The night mind's prompt shows his own line with its words ("min 03: you confronted Daniel, saying: "Risking your life…"…
  Then 4 more times… last: …", mind 6, `runs/v22gaps/part1c.txt`).
- The model copies it as a memory's `meaning`. The check allows a quotation that is in the shown records
  (`mind.py:278-281`, S6: rejected only if "a quotation not in the records"; the same for intents, `mind.py:336-339`). His own
  spoken sentence is in the records, so it is allowed.
- Block B prints it next morning in full (`memory.py:48-56`, `B_HEAD` at `memory.py:10`).
- Nothing removes a person's own spoken words from a mind's `meaning`: NOT FOUND (`grep` of `mind.py` for the speaker's own
  words: only S6, which passes them).

##### 1c. Lines said word for word 2+ times, per person per day

`runs/v22gaps/part1.txt` §1c. A row counts a speech act if the same person said the same words at least twice that day.
Rows with a repeat (a zero row is not shown; all 32 person-days are in the file):

| Day | Person | v21: acts / in a repeated text / texts | v22: acts / in a repeated text / texts (most repeats) |
|---|---|---|---|
| 3 | Elena | 8 / 0 / 0 | 9 / 2 / 1 (2) |
| 3 | Mara | 9 / 3 / 1 | 11 / **7** / 2 (4) |
| 5 | Elena | 10 / 2 / 1 | 8 / 0 / 0 |
| 6 | Daniel | 8 / 3 / 1 | 11 / 0 / 0 |
| 6 | Mara | 9 / 0 / 0 | 10 / 3 / 1 (3) |
| 7 | Leo | 2 / 0 / 0 | 6 / **4** / 1 (4) |
| 8 | Daniel | 10 / 0 / 0 | 12 / 2 / 1 (2) |
| 9 | Elena | 9 / 3 / 1 | 13 / 0 / 0 |
| 9 | Mara | 8 / 0 / 0 | 9 / 4 / 2 (2) |
| 10 | Daniel | 11 / 0 / 0 | 14 / 2 / 1 (2) |

| Totals, days 3–10 | v21 | v22 |
|---|---|---|
| Speech acts | 245 | 326 |
| In a repeated text (same person, same day) | 11 | **24** |
| Distinct repeated texts | 4 | 9 |
| Person-days with a repeat (of 32) | 4 | 7 |
| By person (acts in repeated texts) | Daniel 3, Elena 5, Leo 0, Mara 3 | Daniel 4, Elena 2, Leo 4, Mara **14** |
| Same line on 2+ different days (same person) | 4 | 5 (Daniel 3, Elena 1, Leo 1) |

Exact repeats are the narrow count: near-repeats (the same frame with a word changed, like Mara's) are not in it.

#### 2. Words versus deeds: Daniel, nights 6 to 9

`runs/v22gaps/part2.txt` (script `runs/v22gaps/part2.py`); his four bedtime prompts in full:
`runs/v22gaps/daniel_night{6,7,8,9}_bedtime_prompt.txt`. A bedtime prompt is built by the same `prompt_parts` as a day prompt
(`world.py:1140`), with the night's `Now` lines. The lines from the day just played:

**Night 6** (day 6 had **no** trip-position act; Daniel chose `lie_awake`: "I need to rest my body while staying alert to protect
everyone in the house."):
- "What you are sure of from today": "- min 00: Everyone gets up and comes into the kitchen… The water you brought back is in the kitchen: about 10 litres."
- "Your own last words today": "- 10:09, you reassured Mara." "- 10:36, you confronted Mara." "- 10:39, you reassured everyone."
- "What else happened today": "- 10:39: Leo confronts you: "You went out into the dark again and risked everything just to prove you can do whatever you want."" and the afternoon's moves.
- "Against Mara (some)… you were angry with Mara today at 10:03, 10:06, 10:36 and 10:39."
- A trip line, from the **day before**: "What was said yesterday about going out last night, where it was left: Mara said you must stay home (min 06); you said you still mean to go (19:03); Leo said nobody should go (19:03); Elena said you must stay home (19:03); then you went to the neighbour's house…" (night 5).
- No promise line. No position line for the day.

**Night 7** (day 7 had no position; `lie_awake`: "I cannot rest properly while the family is falling apart around us and I need to keep watch over everything."):
- Own last words: "- 10:42, you confronted Mara." "- 17:18, you confronted Mara." "- 17:21, you confronted Leo."
- Last lines of the day: "- 17:21: Leo confronts you: "Risking your life doesn't give you the right…"" "- 17:21: Mara confronts you: …" "- 17:21: Elena reassures everyone: …".
- "Against Leo (some)… today at 10:06, 10:09, 10:12 and 17:21." "Against Mara (a lot)… today at 10:36, 10:39, 10:42 and 17:18."
- No trip line, no promise line.

**Night 8** (day 8: 24 trip-position acts, Daniel `volunteer` and `still_going` 8 times; Daniel chose `sleep`: "I am too weak and tired to make it out there tonight."):
- Own last words: "- 16:48, you said you still mean to go there tonight." "- 19:00, you said you still mean to go there tonight." "- 19:03, you said you still mean to go there tonight."
- The plan line: "About going there tonight: Mara said you must stay home (min 12); Leo said you must stay home (19:00); you said you still mean to go (19:03); Elena said nobody should go (19:03)."
- **The promise line (a `Now` line):** "You said you would go to the neighbour's house tonight. If you are going, it is now."
- Last lines of the day: "- 19:03: Leo confronts you: "You are not going anywhere tonight, Daniel, and we are not having this argument again."" "- 19:03: Elena says nobody should go out tonight: "Nobody is going out into the dark tonight, we must stay together and keep safe.""
- "Against Mara (a lot)… today at 16:45, 16:48, 19:00 and 19:03."

**Night 9** (day 9: 31 acts, Daniel 9; Daniel chose `sleep`: "My starving body is too weak to stand, so I cannot go out tonight."):
- Own last words: "- 11:33, you said." "- 19:00, you said you still mean to go there tonight." "- 19:03, you said you still mean to go there tonight." (The 11:33 act, `go_kitchen`, "I need to see what is happening out there.", is only "you said."; the verb table has no gist for it, `world.py:1741-1757`.)
- The plan line, the promise line (as night 8), and the 19:03 lines of Leo ("You are not going out there, Daniel. We stay inside."), Elena and Mara.
- The body line of nights 8 and 9: "starving, for days now: you are thin and weak; stairs and carrying things tire you fast; you feel cold, even indoors; and you have hardly slept."

##### 2a. Does a day's trip position reach the night prompt or its options?

| Path | Reaches | path:line |
|---|---|---|
| The speaker's own latest position `volunteer` (also `still_going`) | **The prompt**: the promise line, a `Now` line | `night.py:497-499` (`own = p.trip_heard.get(q)`; `PROMISE`, `night.py:58`); far: `night.py:500-501` (`FAR_PROMISE`, `night.py:71`) |
| Every position heard that day, each speaker's latest | **The prompt**: "About going there tonight: …" | `world.py:703-734` (`heard_plan`), `world.py:736-748` (`trip_lines`), `world.py:1017`; outside the trimming budget, `world.py:1161` |
| The speaker's own lines | **The prompt**: "Your own last words today" (minute and verb) | `world.py:1151`, `world.py:1781-1782` |
| Everyone's lines of the evening | **The prompt**: the last lines of "What else happened today" | `world.py:1146` |
| The previous day's positions and what came of the night | **The next night's prompt**: "What was said yesterday about going out last night…" | `night.py:1066-1069`, `night_came_to` `night.py:1075-1089` |
| A position changing the **bedtime options or any chance** | **NOT FOUND.** The options are the same five for everyone (`night.py:502`: `BEDTIME`, `night.py:48-53`, plus `go_further` if they know next door is empty); in `night.py`, `p.trip_heard` is read only at `497, 1081, 1225` (the last resets it) | |

A position never moves a person; it is a line in a prompt. Leaving is `go_next_door` at bedtime (`night.py:502`, `night.py:507-509`).

##### 2b. Q5, the evening, days 4 to 10

Q5 is one ask at the first quiet minute from 19:00 (`quiet.py:608-638`): of those awake with someone, the person whose trip act is the latest is
asked, with 8 asks of their own past the day's 40 (`quiet.py:47-48`, `quiet.py:981-982`). **It stores no outcome**: its only trace is the
`EVENING_LINE` memory ("It is evening; in two hours everyone goes to bed.", `quiet.py:49`, appended `quiet.py:637`), which none of Daniel's
four bedtime prompts holds (0 of 4), and the stretch's lines in "What else happened today". A separate "Q5 outcome" line: NOT FOUND.

| Day | Trip-position acts (Daniel's) | Q5 | Q5 stretch: what was said | Daniel's bedtime, that night |
|---|---|---|---|---|
| 4 | 12 (5) | fired; asked Mara | 8 lines: accusations about the food; Daniel "Trust me, I will keep us safe" (`reassure_all`) twice. No position. | `lie_awake` |
| 5 | 21 (9) | fired; asked Daniel | Daniel `still_going` twice ("I told you, I am going out tonight…"); Leo, Elena, Mara against. | **`go_next_door`; went** (night 5) |
| 6 | 0 | not fired: "no trip position today" | — | `lie_awake` |
| 7 | 0 | not fired: "no trip position today" | — | `lie_awake` |
| 8 | 24 (8) | fired; asked Elena | Daniel `still_going` twice; Elena `keep_daniel_home`, `nobody_goes`; Leo `keep_daniel_home`; Mara accuses. | `sleep` |
| 9 | 31 (9) | fired; asked Leo | Daniel `still_going` twice ("I am the eldest, and I will decide when it is time to go."); Leo, Elena, Mara against. | `sleep` |
| 10 | 27 (13) | fired; asked Daniel | Daniel `still_going` twice; Elena, Leo, Mara against. | no night 10 |

On day 5 the evening ended as on days 8 and 9: Daniel says he is going and three say no. The difference on day 5 is the night, not the evening.

#### 3. Q6 with nothing to do: day 7, 17:18

`runs/v22gaps/part3.txt`; Mara's prompt in full: `runs/v22gaps/q6_day7_1718_mara_prompt.txt`.

- **Who and what they were offered:** all four were in the kitchen. Options: Mara 29, Daniel 26, Elena 27, Leo 26. The usual ones: `silent`,
  `deny`, `accuse_*`, `confront_*`, `reassure_*`, `propose_trip`, `volunteer`, `send_*`, `propose_far`, `volunteer_far`,
  **`save_water`, `ration_water`**, `say_other`, `sit_*`, `aside_*`, `go_*`. **No `collect_rain`**. No `keep_daniel_home` or `nobody_goes`
  either (no position had been taken that day).
- **Why `collect_rain` was absent:** it is offered only if the person is in the kitchen, it is raining for them, **and the bin is not out**
  (`world.py:594`: `p.water["bin_out"]` false). Daniel set the bin out on day 6 at min 00 (`quiet.py:334-340`, `truth.py:111-115`); it was out
  at 17:18 ("The bin under the drainpipe in the yard holds about 70 litres of rain water." in the water line). `bin_out` is set true
  only there (`truth.py:111-115`) and is never set false: the only `bin_out = False` in the code is the initial value (`truth.py:56`). Nothing brings the bin in
  or empties it (`reports/w1_impl.md` §2, point 6). **So `collect_rain` could be offered once in the run**, and was: in 1 of the 402 prompts (Daniel, day 6, min 00).
- **What the prompt said of the rain:** one `Now` line, "- Rain is falling: you hear it on the roof and against the boards." (`world.py:1117-1118`), the same line as in
  the 80 day prompts that were written while it rained. The memory line for the onset, "Rain began: you heard it on the roof and against the boards."
  (`quiet.py:85`, appended `quiet.py:351`), is **not** in the 17:18 prompts: the memory list leaves out the current minute
  (`world.py:1146`, `if m != minute`), and at 17:21 it had been cut as an earlier thing ("(earlier things, left out here)", `runs/v22gaps/part3.txt`).
  On day 9 it is in the three 11:33 prompts only because nothing else came before it.
- **What Q6 does** (`quiet.py:342-378`, `hear_rain`): for each spell that began, it writes the onset into every awake person's memory, and then:
  - if the house is already talking, the rain is a trigger and nothing else (`quiet.py:358-363`);
  - nobody awake, or Q6 already fired today: logged only (`quiet.py:364-369`);
  - otherwise it takes the room with the most awake, marks `q6_done`, and **asks every awake person there** (`quiet.py:370-375`, through `ask`, `quiet.py:414-428`), in
    a reserved stretch of 8 asks (`RAIN_ASKS`, `quiet.py:88`, `quiet.py:983-984`).
  - **It does not look at what can be done.** The text `RAIN_TRIGGER` goes only into `pending["texts"]`, which opens the ask (`world.py:1499-1500`); it is not a prompt line for
    anyone awake (the `quiet.py:424-427` branch writes it to memory only for someone resting). A check that a rain action exists: NOT FOUND (`hear_rain` reads no option and no `bin_out`).
  So with the bin out, Q6 is a standard 8-ask stretch with one extra `Now` line. At 17:18 it played Mara's accusation, Daniel's answer, Elena's `reassure_all` and Leo's `confront_daniel`, and the next turn continued it.

#### 4. Cost: day 9, Daniel, 2602

`runs/v22gaps/part4.txt` (script `runs/v22gaps/part4.py`, a no-API replay with `prompt_parts` wrapped to read the exact `block`); the prompt:
`runs/v22gaps/day9_daniel_2602_prompt.txt`. System + prompt = **2602** (the system prompt 913 characters = 254 tokens; the prompt 8452 characters = 2348 tokens;
`estimate_tokens` = characters / 3.6, `world.py:130`). **`block`, the characters `estimate_tokens` is told not to count: 4337 = 1205 tokens. Counted against
`PROMPT_TOKEN_BUDGET` (1400, `world.py:78`): 1397.** The trimming loop (`world.py:1175-1190`) cuts only "What else happened" lines and "days before" lines; it stopped at 1397, under 1400, after cutting "What else happened" lines (2 remain).

Sections, in prompt order (tokens = characters / 3.6):

| Chars | Tokens | Section | Budget |
|---|---|---|---|
| 913 | 254 | system prompt (`world.SYSTEM`) | inside, not trimmable |
| 105 + 59 + 192 + 112 + 81 | 29 + 16 + 53 + 31 + 22 = 151 | who you are, address, traits, what matters | inside, not trimmable |
| 133 | 37 | Your body | inside, not trimmable |
| 72 | 20 | About the can | inside, not trimmable |
| 115 | 32 | About food | **outside** (trip lines) |
| 175 | 49 | About the neighbour's house | **outside** (trip lines) |
| 158 | 44 | About the street | **outside** (trip lines) |
| 232 | 64 | About going out at night | **outside** (trip lines) |
| 179 | 50 | About going there tonight | **outside** (trip lines) |
| 278 | 77 | About water (W1) | **outside** (W1) |
| 125 + 174 + 314 | 35 + 48 + 87 = 170 | Against Leo, Against Mara, On your conscience | inside, not trimmable |
| 846 | 235 | The house | inside; **156 chars (43 tokens) outside** (the trip's "this morning" and the yard) |
| 786 | 218 | What you remember from the days before (7 lines) | inside, **trimmable**; 365 chars (101 tokens) outside (day-2 memories kept from trimming) |
| 489 | 136 | What stays with you from earlier days (block C) | **outside** (carry) |
| 947 | 263 | Yesterday and last night (block A) | **outside** (carry) |
| 580 | 161 | What yesterday left in you (block B) | **outside** (carry) |
| 168 + 190 | 47 + 53 = 100 | What you are sure of today; Your own last words today | inside, not trimmable |
| 198 | 55 | What else happened today (2 lines left) | inside, **trimmable** (oldest cut first) |
| 113 + 51 | 31 + 14 = 45 | Now lines (09:57, kitchen); "first to act" | inside, not trimmable |
| 82 + 156 + 64 | 23 + 43 + 18 = 84 | the pattern block ("What you have been doing", "In that time", "Answered you differently") | inside, not trimmable |
| 1279 | 355 | Your options (24 lines) | inside; **663 chars (184 tokens) outside** (trip options 485, W1 options 178) |

The parts of `block`, characters / tokens: trip lines 859 / 239; trip options 485 / 135; kept day-2 memories 365 / 101; house line 156 / 43;
**carry 2016 / 560**; W1 water line 278 / 77; W1 options 178 / 49. Their sum is 4337 / 1205.

- **The carry is exactly 560 tokens: the cap of `memory.MEMORY_MAX`** (`memory.py:9`, "estimated tokens of A, B and C together"), so blocks A, B and C sit at their bound in this prompt.
- **W1 added** 126 tokens here (the water line 77 and the two water options 49), plus the yard in the house line (43 tokens counted with the trip's 156 characters). Against v21's largest
  day prompt (2358, day 5, Elena) the 2602 is 244 tokens more; the W1 lines are about half of that.
- **The loop stopped at 1397, under 1400.** The marker "(earlier things, left out here)" is in the prompt. A prompt is therefore about the budget (1400) plus what sits outside it (here 1205); the outside part grows with the trip lines (five lines) and the memory blocks.
- **Two prompts exceed 2600**: 2602 and 2601, both Daniel, day 9 (`runs/v22/scoring/replay_max.txt`).

#### 5. One line per finding

1. **Own words in the night mind's `meaning` and `intent`:** the mind's S6 check passes a quotation that is in the person's own record, so block B quotes the speaker's own sentence; drop a quotation that matches the speaker's own spoken line (`mind.py:278-281`, `336-339`).
2. **The standing intent repeats as the next day's line:** Mara's intent is in every morning prompt; show an intent only until the person has spoken it once that day, or drop it from the prompts that follow a spoken line.
3. **The promise and plan lines read, and the model sleeps ("too weak to stand"):** nothing links a spoken position to the bedtime choice; it is the model's, so nothing in code is wrong, and what W2 needs is a situation at the door, not another line.
4. **`collect_rain` is a one-shot:** nothing brings the bin in, so the option is gone after day 6; whether the bin should be emptied or brought in is a design question for the next water stage.
5. **Q6 on a rain with no action:** it still spends a reserved 8-ask stretch on a conversation that continues; Q6 could be skipped (or shortened) when no rain option is offered.
6. **Cost:** the 1205-token outside-the-budget part (carry 560, trip 515, W1 126) is what makes the largest prompt; the cheapest cut is the day-2 "kept" memories (101 tokens) or the trip lines.

#### 6. Commands and output

All from `Prototypes/llm-morning/` unless stated, with `GEMINI_API_KEY` unset (no API call was made). `$PY` = `.venv/Scripts/python.exe`,
`PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`.

**0. The commit** (repository root; `runs/v22gaps/commit_checks.txt`)
```
$ git add Prototypes/llm-morning/reports/days_v22.md Prototypes/llm-morning/reports/days_v22_plan.md \
          Prototypes/llm-morning/runs/v22 Prototypes/llm-morning/runs/w22 Prototypes/llm-morning/cache/v22
$ git diff --cached --name-only | wc -l                                   40
$ git grep --cached -c "<middle of the one-off key>"; echo "exit $?"      exit 1   (no match)
$ git grep --cached -cE "AQ\.[A-Za-z0-9_-]{30,}"; echo "exit $?"          exit 1   (no match)
$ git commit -F -      (message ends with the Co-Authored-By line)        966d5b5
$ git rev-parse HEAD                                                      966d5b5fa0bb58ae28e76c9516aaf1a457248358
$ git grep -c "<middle of the one-off key>" HEAD; echo "exit $?"          exit 1
$ git grep -cE "AQ\.[A-Za-z0-9_-]{30,}" HEAD; echo "exit $?"              exit 1
$ git diff HEAD~1 HEAD --name-only | grep -vc "^Prototypes/llm-morning/\(reports/days_v22\|runs/v22\|runs/w22\|cache/v22\)"    0
$ git diff --stat                                                         (empty)
$ git status --short
?? Prototypes/llm-morning/runs/v22gaps/
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

**1. Repeats** (`runs/v22gaps/part1.txt`, `part1b.txt`, `part1c.txt`)
```
$ $PY runs/v22gaps/part1.py > runs/v22gaps/part1.txt            exit 0
  frame lines: 7; word for word: {'…into the night…': 3, '…into the dark…': 4}
  morning (min 00-18, the first stretch): 6; after: 1
  Mara's speech acts on day 3: 11
  day prompts 342; with the 'Your own last words' block 306; lines with quoted own words 0
  block headings: {'none': 36, 'this morning': 154, 'today': 152}
  v21: speech acts 245; in a repeated text 11; distinct repeated texts 4; person-days with a repeat 4 of 32
  v22: speech acts 326; in a repeated text 24; distinct repeated texts 9; person-days with a repeat 7 of 32
$ $PY runs/v22gaps/part1b.py > runs/v22gaps/part1b.txt          exit 0
  runs/v22: … own earlier words (>= 25 chars) found in a later prompt of the same person: 5 lines   (Leo 5, all in block B)
  runs/v21: … 6 lines   (Leo 6, all in block B)
  runs/v22: lines said word for word on 2+ different days: 5;  runs/v21: 4
$ (inline, output appended to runs/v22gaps/part1c.txt)  Leo's mind-6 prompt, his answer's memory, and his 9 day-7 prompts holding the sentence
  Leo day-7 prompts holding his own sentence in block B: 9; answers repeating it verbatim: 4 (min 03, 10:09, 17:18, 17:21)
```
Part 1b's count of 5 leaves out the prompts whose answer is that sentence itself; part 1c's 9 includes them.

**2. Words versus deeds** (`runs/v22gaps/part2.txt`; Daniel's bedtime prompts extracted by matching the night prompts of the cache to the night decisions of the transcript, in order, checked by name)
```
$ $PY runs/v22gaps/part2.py > runs/v22gaps/part2.txt            exit 0
night 6 chose lie_awake; night 7 lie_awake; night 8 sleep; night 9 sleep
$ grep -c "It is evening" runs/v22gaps/daniel_night{6,7,8,9}_bedtime_prompt.txt        0 0 0 0
$ grep -n "own = p.trip_heard\|now.append(PROMISE)" night.py          497, 499
$ grep -n "bin_out" quiet.py world.py truth.py                        world.py:594 (read); truth.py:56 (False, init), truth.py:111-115 (True)
```

**3. Q6** (`runs/v22gaps/part3.txt`)
```
prompts with a Now line at 17:1x: Mara, Daniel, Elena, Leo ('Now, 17:18, you are in the kitchen.')
options: Mara 29, Daniel 26, Elena 27, Leo 26; collect_rain in none.   prompts with '- collect_rain:' in the whole run: 1 (Daniel, Now, minute 00, day 6; chose collect_rain)
prompts holding the 'Rain began' memory line: Leo, Elena, Mara at 11:33 (day 9) only
day 7 17:21 prompts: 'Rain began' not among the last lines ('- (earlier things, left out here)')
```

**4. Cost** (`runs/v22gaps/part4.txt`)
```
$ $PY runs/v22gaps/part4.py > runs/v22gaps/part4.txt            exit 0
largest day/night prompt: scene day9, daniel, estimate 2602; `block` passed to estimate_tokens 4337 characters = 1205 tokens; counted against the budget: 1397 (PROMPT_TOKEN_BUDGET 1400)
outside the budget: {'trip lines': 859, 'trip options': 485, 'kept day-2 memories': 365, 'house line beyond HOUSE_THINGS': 156, 'carry': 2016, 'W1 water line + rain Now line': 278, 'W1 options (save/ration/collect)': 178}  = 4337 characters
```

---

## days_v22.md

### v22: W1's live run, v16 seed 2, days 3 to 10

Mode: run. The plan is `reports/days_v22_plan.md`, recorded before any live call (`runs/v22/plan_frozen.txt`). The code is
HEAD `a4edf84` (W1, its fixes, and block C's went_out line). No code, test or plan line was edited. The control is v21
(`reports/days_v21.md`). Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/v22/`, the scoring
outputs in `runs/v22/scoring/`, the scorer and its checks in `runs/w22/scoring/`. Clock stamps are the run's own
("min 75", "10:24"), as in the transcript.

#### Result

| # | Prediction | v21 | v22 | Verdict |
|---|---|---|---|---|
| W1-1 | ≥ 3 outward acts, on ≥ 2 different nights | 1 (N5 `got_up`) | **1**: N5, Daniel `went_out`. One night. | **FAIL** |
| W1-2 | ≤ 8 of 28 bedtime reasons match FROZEN | 16 of 28 | **6 of 28** (nights 3, 4, 7, 8, 8, 9) | **PASS** |
| W1-3 | ≥ 2 bedtime `go_next_door` / `go_further` | 1 | **1** (N5 Daniel `go_next_door`) | **FAIL** |
| W1-4 | WATER speech acts on ≥ 4 of 8 days | 0 acts, 0 days | **12 acts on 4 days** (days 6, 7, 8, 9: 8, 2, 1, 1) | **PASS**, at the threshold |
| W1-5 | (a) every awake person hears each rain start, 100%; (b) the first spell's Q6 stretch holds a `collect_rain` or a rain word | no weather | (a) **100%** over 2 spells (day 7 17:18, day 9 11:30); (b) **does not hold**; `collect_rain` 1, `rain_out` 0 | **FAIL** |
| W1-6 | ≤ 1 "no water" claim while the store is > 0 | 0 | **0** claims | **PASS** |
| W1-7 | store < 50 L on day k ≤ 9 → a ration or save act by 21:00 of day k + 1 | no water | below 50 L on **day 5**; first act **day 9, 11:33** (Leo `ration_water`) | **FAIL** |
| W1-8 | live asks ≤ 450; each day ≤ 56; largest estimate ≤ 2600 | 337; ≤ 40; 2435 | **402**; ≤ 48; **2602** | **FAIL**, by 2 tokens |
| W1-9 | 0 "Your body:" lines match `impossible\|cannot\|can't\|unable\|barely (stand\|walk\|move)` | stage 3 lines match (141 of 337) | **0 of 402** | **PASS** |
| W1-10 | CAN ≤ 20% of speech acts | 63 of 245 = 25.7% | **38 of 326 = 11.7%** | **PASS** |
| W1-11 | a `went_out` night has a leaver whose bedtime reason or trip words that day match WATER | no trip | N5, Daniel: reason and trip words have no water word | **FAIL** |

**5 PASS (W1-2, 4, 6, 9, 10), 6 FAIL (W1-1, 3, 5, 7, 8, 11), 0 NOT TESTED.**

**The section-8 test of the idea, by the counts:** W1-1 and W1-3 both fail and W1-2 holds. That is the case
`reports/world_design.md:814-816` names ("honest words alone do not move the house, and W1-4's water talk is talk
without acts"). In W1-4's 12 acts, 9 are about the 9 L Daniel carried home on night 5, and 3 about the house's own
water or rain (§8).

**DONE:**
- **The plan.** Recorded at **2026-10-08T19:59:11Z**, sha256 `eb3758cc…a3a6bf` (full in §9). The first live ask was at
  day 3 min 00, the run started at **20:04:14Z**. At the end (20:35:48Z) the sha256 is the same, and the 23 code and
  config sha256s of `plan_frozen.txt` are unchanged (23 OK). `git diff --stat` is empty; no tracked file is modified.
- **The scorer.** It reproduces v21's column on all 11 rows (`ALL MATCH`, §9, command 3). A fake 10-day run exercises
  it, and 35 checks on edited copies of that fake exercise the rules the fake never reaches (§9, command 4).
- **The exit.** The run exited **0** (`echo "exit $?"` after the process, `runs/v22/seed2.exit.txt`). The cap (470) was
  not reached: **402** live asks. Stderr is empty.
- **Verdicts.** All 11 predictions have one.

**What differed from the plan's wording:**
- **The key.** The run used an API key the user gave in chat for this one run, as `GEMINI_API_KEY` for that process
  only. `grep -rl` for it over the repository finds it in no file.
- **The start.** Through `runs/v22/run_capped.py` (cap 470), `morning.main()` with `--seed 2 --out v22 --days 10`. The cap
  was not reached.
- **Three 503s.** `[503 UNAVAILABLE]` three times (stdout lines 180, 181, 192), each retried; `api_requests` 405 for 402
  answers. No 429; no ask lost.
- **The scorer's path.** `runs/w22/scoring/w1_score.py`, as the brief says (the design said `runs/w1/scoring/`).
- **W1-8's marker.** The plan marks it "restated": the design already had 56 a day.
- **W1-9's prompts.** Read from the cache file's 402 live prompts (day, night and night-mind), not from a replay: a
  superset of the plan's day and night prompts, with the same body lines. A replay (`runs/v22/scoring/replay_max.txt`)
  gives the same 402 prompts from day 3 on and the same largest estimate.

#### 1. Asks per day

From `runs/v22/daniel_ate_it-seed2.meta.json`. Days 1–2, nights 1–2 and minds 1–2 came from the cache: 96 answers. Every
ask from day 3 on was live: **402** (`answers_live` 402, `answers_from_cache` 96, `api_requests` 405). Run time 1875 s
(31.3 min).

| Day | Day asks | Night after | Mind after | Stretches (trigger: asks) | Morning ends |
|---|---|---|---|---|---|
| 3 | 40 | 4 | 4 | morning 24, Q2 8, Q1 8 | min 21 |
| 4 | 40 | 4 | 4 | morning 24, Q2 8, Q5 8 | min 21 |
| 5 | 40 | 8 | 4 | morning 24, Q2 8, Q5 8 | min 18 |
| 6 | 40 | 4 | 4 | morning 24, Q2 8, Q2 8 | min 21 |
| 7 | 42 | 4 | 4 | morning 22, Q2 6, Q2 6, **Q6 8** | min 18 |
| 8 | 48 | 4 | 4 | morning 24, Q2 8, Q1 8, Q5 8 | min 18 |
| 9 | 48 | 4 | 4 | morning 24, Q2 8, **Q6 8**, Q5 8 | min 18 |
| 10 | 44 | — | — | morning 24, Q2 6, Q2 6, Q5 8 | min 18 |
| Sum | 342 | 32 | 28 | | |

342 + 32 + 28 = 402. Night 5 has 8 asks: its 4 bedtime choices, Leo's `stop_daniel`, Daniel's `go_anyway`, and
Elena's and Mara's reactions. Q6 fired twice (days 7 and 9). The day that had the most asks has 48, under the 56 of
W1-8. Day asks by day in v21 were 30 to 40.

#### 2. Each day and night

**The bodies, every day.** Nobody ate, shared or gave on any day (`runs/v22/scoring/account.txt`: no food act), and the
shelf was 0. The fasting hours are therefore v21's table (`reports/days_v21.md` §2), e.g. Daniel 75.9 at 21:00 on day 3 and
269.1 on day 10. **Thirst: every person was at stage 0, "short 0.00 L", at 21:00 on every day.** Stage crossings from
the transcript's need events:

| Fasting stage (hours) | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| 2 ("light and slow", ≥ 72 h) | day 3, 17:39 | day 5, 19:45 | day 3, 19:00 | day 4, 11:42 |
| 3 ("thin and weak", ≥ 168 h) | night 6 (170.2 h at 07:00 of day 7) | day 10, 12:39 | day 7, 19:00 | day 8, 16:45 |

"You feel cold, even indoors" is in the body lines from night 4 (17.2 °C indoors, under 18) for those at stage 2.

**The water, every day** (the World's log, `quiet.water`, litres; tap = the stored tap water, bin = rain water):

| Day | Weather | Tap, 07:00 → 21:00 | Bin | Level |
|---|---|---|---|---|
| 3 | dry, 18.4 °C indoors | 105.5 → 91.5 | — | as_before |
| 4 | dry, 17.2 | 81.5 → 67.5 | — | as_before |
| 5 | wet 12.3 mm from 22:03 | 57.5 → 43.5 | — | as_before |
| 6 | wet 4.5 mm, raining at 07:00 | 42.5 → 37.8 | set out at 07:00; 67.1 at 21:00 | as_before |
| 7 | wet 1.2 mm (04:36–10:09, 17:18–20:21) | 34.5 → 29.8 | 66.0 → 76.6 | as_before |
| 8 | dry, 17.5 | 26.5 → 21.8 | 69.9 → 60.6 | as_before |
| 9 | wet 17.8 mm (11:30–16:30) | 18.5 → 15.0 | 53.9 → **240.0** (full) | **rationed at 11:33** |
| 10 | dry, 17.6 | 12.9 → 10.0 | 240.0 | rationed |

The drinking store (tap + bin) first read below 50 L at day 5, 21:00 (43.5 L), and after day 6's rain it was 104.9 L at
21:00.

**Day 3.** Dry. Morning to min 21; Q2 at 10:30; Q1 at 17:39 (Daniel). The talk is Daniel's night-2 trip. No water, rain
or trip words.
- Mara (min 00): "You went out into the night and came back with nothing, Daniel. Why did you even go?" (the same
  line 7 times in the morning).
- Daniel (min 03): "I went to see what was there so we wouldn't have to guess, and I will keep us safe."
- Leo (10:33): "You snuck out alone last night and came back empty-handed just like I knew you would, Daniel."

**Night 3.** Daniel `lie_awake`, Elena `sleep`, Leo and Mara `lie_awake`. All four were offered `go_next_door` and
`go_further`. Nobody got up. Leo's reason (FROZEN): "I am too weak to go out again, but I need to stay alert if Daniel
tries to leave in the dark once more." Mara: "I cannot sleep knowing Daniel might sneak out again into the dark."

**Day 4.** Dry. Q2 at 11:00, Q5 at 19:00 (Mara). **Trip talk begins: 12 trip-position acts** (v21 had none on day 4).
- Mara (min 06, `propose_trip`): "Daniel went into the dark before, so one of us has to check the neighbour's house
  tonight."
- Daniel (min 09, `still_going`): "I am the oldest, and I am going whether you like it or not."
- Leo (min 09): "You are not going anywhere tonight, Daniel, because it is suicide and you know it."
- Daniel (min 15, `volunteer_far`): "I will go further down the street myself to find what we need."

**Night 4.** All four `lie_awake`. Leo (FROZEN): "I have no strength left to go out tonight, so I will lie awake and
listen." Daniel: "I cannot sleep while my family is starving and I carry the weight of what I did." No trip.

**Day 5.** Wet from 22:03 that night. Q2 at 10:03, Q5 at 19:00 (Daniel). **21 trip-position acts** (v21's 21).
Daniel `still_going` 6 times.
- Daniel (min 06): "I will go out tonight to check the neighbor's house again, because I am the oldest and it's my duty to
  keep us safe."
- Elena (min 06): "Daniel, you must stay home tonight. We cannot risk losing you out there in the dark."
- Leo (19:00): "Daniel, you went before and found nothing, and going out again will just get you killed."
- Daniel (19:03): "I have to go out and find something for us, no matter what you all say."

**Night 5: the one trip.** A rainy night (22:03 to 03:42; the front-door draws are halved). Bedtimes: **Daniel
`go_next_door`** ("I must go out to find food tonight because I am the oldest and it is my duty to protect them."),
Elena, Leo and Mara `lie_awake`. Daniel got up. The house answered, in order:
- Leo, `stop_daniel`: "Daniel, stop. You are not going out there."
- Daniel, **`go_anyway`**: "I have to do this, Leo, so move aside and let me go." (v21: `stay_home`, "I am too weak
  anyway".)
- Elena, `stay_in_bed`: reason "I will lie here and pray he turns back before the dark takes him." Mara,
  `get_up_and_look`.
- The street: `scare_back`. Nothing found; **9 L of water carried home** (seed 2's neighbour holds 9 L: an empty bath,
  the cistern, two bottles). Outcome: "back shaken, with water". No food came home.

**Day 6.** Rain already falling at 07:00. **The one `collect_rain` of the run**, the first ask of the day:
- Daniel (min 00, `collect_rain`): "It's raining out, I'm setting the bin under the drainpipe to catch water."
  The bin caught 67.1 L by 21:00. No other prompt of the run offered `collect_rain` (the option goes when the bin is out).
- Leo (min 00): "You brought back water in the dark while everyone was asleep, Daniel, so don't pretend you were just
  resting."
- Daniel (min 03): "I risked my life in the dark for that water, Leo, so stop accusing me when you stayed safely in bed."
- Elena (min 06): "Leo, your brother came back safe with the water, so let us try to calm down and listen to each other."
- Leo (min 15, `go_kitchen`): "I heard rain on the roof, so we should check the yard bin before it misses any water."
- No trip positions. 8 of the run's 12 WATER acts are here.

**Night 6.** All four `lie_awake`. Elena: "I need to listen through the night to protect my children from slipping out into
the dark again." No trip.

**Day 7.** Wet: 04:36–10:09 (already falling when the day began) and **17:18–20:21**. Q6 at 17:18, **4 asked**. Leo
reaches stage 3 (19:00). Daniel's body line has changed to "thin and weak".
- Daniel (min 09): "Mara, stop accusing me when I'm the one who went out into the dark to bring back water for all of us."
- The Q6 stretch (17:18–17:24, 8 asks) is the day's argument continuing: Mara "You took the can, Daniel, and you're the
  reason we have nothing left."; Elena "Please, let us not fight anymore…"; Leo "Risking your life doesn't give you the
  right to put everyone else in danger by sneaking out without a word, Daniel." **No rain word, no `collect_rain`** (the
  bin was already out).
- Daniel (17:21): "Leo, you weren't out there in the dark risking your neck to bring back water for us."

**Night 7.** Daniel, Elena, Mara `lie_awake`; Leo `sleep` ("I have no strength left to stay awake, so I need to sleep and
save what little energy I have."). Mara (FROZEN): "I am too weak and cold to get up, so I will lie here in the dark and
listen." No trip.

**Day 8.** Dry. Q2 at 09:51, Q1 at 16:45 (Mara, stage 3), Q5 at 19:00 (Elena). **24 trip-position acts**, Daniel
`still_going` 7 times.
- Leo (min 09): "Bringing back water doesn't erase the fact that you lied to us and stole the food."
- Daniel (min 12, `volunteer`): "I will go out there myself tonight and find us something to eat."
- Leo (16:45): "You are not going out there tonight, Daniel. We agreed on this."
- Daniel (19:03): "I am the oldest, and I am the one who is going out there tonight."

**Night 8.** Daniel `sleep` (FROZEN): "I am too weak and tired to make it out there tonight." Elena, Leo, Mara `lie_awake`
(Mara, FROZEN: "I am too weak and tired to go out, but I will lie here awake and listen in the dark."). No trip.

**Day 9.** Wet 11:30–16:30, 17.8 mm. **31 trip-position acts**, Daniel `still_going` 7 times. Q6 at 11:30: **3 asked**
(Elena, Leo, Mara; Daniel was resting from 10:27 to 11:33). The bin reaches its 240 L.
- Daniel (min 06, `propose_trip`): "We can't just sit here arguing while we starve; I say someone has to check the
  neighbour's house again tonight."
- Q6 (11:30): Leo, Mara, Elena all `nobody_goes`: "We are not going out there, and neither is Daniel."
- **Leo (11:33, `ration_water`)**: "We need to ration what is left in the pans and the bin so it actually lasts." The
  level goes to `rationed` at 11:33. Elena: "You are right to look after the water, Leo, we will make it last together."
- Leo (11:36): "You are not going anywhere tonight, Daniel. We stay inside."

**Night 9.** Daniel `sleep` (FROZEN): "My starving body is too weak to stand, so I cannot go out tonight." Elena
`watch_door`; Leo and Mara `lie_awake`. No trip. There is no night 10.

**Day 10.** Dry. Elena reaches stage 3 (12:39). **27 trip-position acts**, Daniel `still_going` 10 times. Q5 at 19:00 (Daniel).
- Daniel (min 03, `volunteer`): "I am the oldest, so I will go out to the neighbour's house tonight to find what we need."
- Leo (min 06): "You nearly got yourself killed last time, Daniel. Going out again is just stupid."
- Mara (min 03): "You are not going anywhere, Daniel. You have no right to decide this for us."
- Daniel (19:03): "I have to go, Mom, because someone has to find something for us."

#### 3. W1-1, W1-3, W1-11 by the counts

- **Bedtime choices, nights 3–9 (28):** v22: `lie_awake` 22, `sleep` 4, `go_next_door` 1, `watch_door` 1, `go_further` 0.
  v21: `lie_awake` 17, `sleep` 7, `watch_door` 3, `go_next_door` 1, `go_further` 0.
- **The one trip** is night 5, as in v21. In v21 Leo's `stop_daniel` ended it ("I am too weak anyway"); in v22 Daniel
  answered `go_anyway` and went. Groups on every other night: none.
- **Trip talk:** 115 trip-position acts on days 4, 5, 8, 9 and 10 (12, 21, 24, 31, 27), Daniel `still_going` 32 times
  (2, 6, 7, 7, 10). v21: 21 acts, on day 5 only, `still_going` 5. After night 5 Daniel said on 3 of the 5 days left (8, 9, 10) that he was
  going that night. His bedtimes on nights 6, 7, 8, 9 were `lie_awake`, `lie_awake`, `sleep`, `sleep`.
- **W1-11:** the one leaver is Daniel. His night-5 reason ("I must go out to find food…") and his day-5 trip words (his nine
  `volunteer`, `propose_trip` and `still_going` acts) have no WATER word. He did not go for water, and came back
  with it.
- **W1-1's two ways to count:** the plan counts `went_out`, and `got_up` or `at_door` with no `went_out`. `collect_rain`
  (1, day 6) and `rain_out` (0) do not count. With `collect_rain` added the count would be 2, still under 3.

#### 4. W1-2 and W1-9: the body

- **W1-2: 6 of 28 reasons match FROZEN** (v21: 16). The six: Leo night 3, Leo night 4, Mara night 7, Daniel night 8, Mara
  night 8, Daniel night 9 (all quoted in §2). By the looser count of "weak, dizzy, tired or stand" in a reason: 6 of 28 (v21: 16).
- **The reasons became about Daniel, not the body:** 9 of the 28 name Daniel together with sneaking, slipping or going
  out ("…listen to make sure Daniel does not try to slip out into the dark again"). In v21: 4.
- **W1-9: 0 of 402 body lines** match. The distinct lines are in `runs/v22/scoring/score_v22.txt` (W19). The stage 2
  line is "you feel light and slow, and standing up fast greys your sight for a moment"; the stage 3 line is "you are thin
  and weak; stairs and carrying things tire you fast".

#### 5. W1-4, W1-5, W1-6, W1-7: water and rain

- **W1-4 (12 acts, 4 days):** by day 0, 0, 0, 8, 2, 1, 1, 0. The 12 lines (`runs/v22/scoring/score_v22.txt`, W14):
  **9 are about the 9 L Daniel carried home** (day 6: 6 acts, day 7: 2, day 8: 1), **2 about rain on the bin** (Daniel's `collect_rain`, Leo's "check the yard bin") and
  **1 about the stored water** (Elena after Leo's rationing). Days 3, 4, 5 and 10 have none.
- **W1-5 (a):** both qualifying spells were heard by every person awake. Day 7 at 17:18: Daniel, Elena, Leo, Mara. Day 9
  at 11:30: Elena, Leo, Mara (Daniel was resting). **(b):** the first spell is day 7 at 17:18; its Q6 stretch had 8
  speech acts and none of the words rain, catch, bucket, bin or pot, and no `collect_rain` (not offered: the bin had been out since
  day 6). By the plan's rule this is a FAIL. The house's one answer to rain came a spell earlier, on day 6 at min 00 (§2),
  which the plan's rule does not read.
- **`rain_out`: 0.** No bedtime prompt of nights 3–9 says it is raining (0 of 32 night prompts), because no rain fell at
  21:00 on any of those nights (night 5's started at 22:03). The option was never offered.
- **Day lines:** 80 day prompts carry "Rain is falling". The "About water:" line is in every day prompt.
- **W1-6: 0 claims** that match NOWATER in 326 speech acts and the nights' reasons and words.
- **W1-7:** the store fell below 50 L on day 5 (57.5 L at 07:00, 43.5 L at 21:00), so the deadline was 21:00 of day 6. The
  `ration_water` option (with `save_water`) was listed in 280 of the 402 prompts; the first act is Leo's, day 9 at 11:33
  (the store then: tap 17.0 + bin 54.6 = 71.6 L, with 17.8 mm falling). `save_water` was never said. By 21:00 of day 6
  the bin had 67.1 L (store 104.9 L), so by the plan's rule this is a FAIL while the store was not short.
- **Thirst never began:** stage 0 for all four at 21:00 on all 8 days. The tap fell from 105.5 to 10.0 L, and the bin
  (rain water, drawn first for washing and the toilet) covered the rest. The thirst words, the thirst need events and
  the thirst-stage Q1 were therefore not exercised.

#### 6. W1-8: cost

- **Live asks 402** (≤ 450); the cap (470) was not reached. **Day asks** 40, 40, 40, 40, 42, 48, 48, 44 (≤ 56).
- **Largest estimate 2602** (day 9, Daniel); a second prompt of day 9 has 2601; the next are 2599 and 2597 (day 8). Under
  the plan's rule (`estimate_tokens(system + prompt)` ≤ 2600) this is a FAIL by 2 tokens. Two prompts exceed 2600.
  Largest by kind: day 2602, night 2407 (night 9), mind 2543 (mind 9). v21: day 2358, night 2193, mind 2435.
- **The API's own count** is higher: largest 3000 (mind 9), against 2854 in v21. The day 9 Daniel prompt counted 2567 by
  the API. In that prompt the W1 lines are the "About water:" line (277 characters), the two water-rule options
  (96 and 80), and the body line (132); W1's lines sit outside the trimming budget by design (`reports/w1_impl.md` §2,
  point 10).
- **The meta's `max_prompt_tokens_estimated` (2453)** covers only the scenes up to day 3, as in v21.

#### 7. Against v21

| | v21 | v22 |
|---|---|---|
| Trips, nights 3–9 | 0 (1 attempt, N5) | 1 (N5) |
| Bedtime `go_next_door` / `go_further` | 1 / 0 | 1 / 0 |
| Bedtime reasons FROZEN | 16 of 28 | 6 of 28 |
| Trip-position acts, by day | 21 on day 5 | 12, 21, 0, 0, 24, 31, 27 on days 4–10 |
| Daniel `still_going` | 5 | 32 |
| WATER speech acts | 0 | 12 |
| CAN share | 25.7% | 11.7% |
| `ration_water` / `save_water` said | no water line | 1 (day 9) / 0 |
| `collect_rain` / `rain_out` | — | 1 / 0 |
| Stage 3 reached | Daniel, Leo (day 6), Mara (7), Elena (9) | Daniel (night 6), Leo (7), Mara (8), Elena (10) |
| Live asks, largest estimate | 337, 2435 | 402, 2602 |

#### 8. What the run shows, by the counts

- **The body no longer forbids, and the house still stays home.** FROZEN reasons fell from 16 to 6 and the body lines
  contain no forbidding word. Bedtime choices did not move toward going out: 1 of 28, as in v21.
- **The trip talk came back, but not the trips.** After Daniel's successful trip the house spoke of trips on 3 of the 5
  following days (8, 9, 10), and nobody went; `still_going` is 32 over the run. The reasons at bedtime were mostly about watching Daniel.
- **The talk about water is the talk about the haul.** 9 of 12 acts. The water in the house (a tap falling from 105.5 to
  10 L) was in every prompt and was spoken of once, on day 9, by Leo, and rationing began then.
- **The weather reached the house and the house hardly spoke of it.** All rain onsets from 07:00 to 21:00 were heard; one
  act answered the rain (Daniel's `collect_rain`, a day before the first qualifying spell).
- **Thirst and the water acts' consequences were not tested**: no one was ever short, so the thirst stages, the
  rain-water drinking and the cold-and-wet word did not matter. A run with a smaller store, or a drier week, is needed for that.
- **Cost:** the largest prompt grew by 167 tokens against v21 (2435 → 2602) and is 2 over the line W1-8 drew.

#### 9. Commands and output

All from `Prototypes/llm-morning/`.

**1. The plan record** (`runs/v22/plan_frozen.txt`: time, sha256, HEAD, `git status --short`, `git diff --stat`, every `*.py`
and `config.json` sha256):
```
recorded_utc: 2026-10-08T19:59:11Z
eb3758cc599b9967e8d918d917e42ed1ac51bebb17f66c7e0fc8418ba2c3a6bf *reports/days_v22_plan.md
$ git rev-parse HEAD
a4edf849aff12bad1bfa0daa31258878375cf686
$ git status --short
?? reports/days_v22_plan.md
?? runs/v22/
?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
$ git diff --stat
(empty)
```
The seeded weather of days 1–10 is in the plan and in `runs/v22/weather_days1_10.txt`; the run's own stdout prints the
same ten lines (`runs/v22/daniel_ate_it-seed2.stdout.txt`, lines 2–11).

**2. The copy and the check** (`runs/v22/cache_copy.sha256.txt`, `runs/v22/premiss-seed2.stdout.txt`):
```
$ mkdir -p cache/v22 && cp cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v22/
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v16/…seed2.json
d79a49396e91a3beb0789e7c03b371e00ae3435e72ee1ac6f27864087406a959 *cache/v22/…seed2.json
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/premiss.py 2
  day 3 07:00 water: tap 105.5 L (bath 59.0, kitchen 46.5), bin 0.0 L, level as_before
FIRST MISS: scene index 6, speaker Leo; Now line: ['Now, minute 00, you are in the kitchen.']; first 'min 00' line: ['- min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)']
exit 3
```
Scene index 6 is day 3, min 00. The cache file was unchanged by the check (same sha256).

**3. The scorer on v21** (`runs/w22/scoring/control_v21.txt`):
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/w1_score.py --control
W1-1: table '1' | scorer '1' | MATCH
W1-2: table '16 of 28' | scorer '16 of 28' | MATCH
W1-3: table '1' | scorer '1' | MATCH
W1-4: table '0 acts, 0 days' | scorer '0 acts, 0 days' | MATCH
W1-5: table 'no weather' | scorer 'no weather' | MATCH
W1-6: table '0 (no claims)' | scorer '0 (no claims)' | MATCH
W1-7: table 'no water' | scorer 'no water' | MATCH
W1-8: table '337; days <= 40; 2435' | scorer '337; days <= 40; 2435' | MATCH
W1-9: table 'stage 3 lines match' | scorer 'stage 3 lines match' | MATCH
W1-10: table '63 of 245 = 25.7%' | scorer '63 of 245 = 25.7%' | MATCH
W1-11: table 'no trip' | scorer 'no trip' | MATCH
ALL MATCH
```

**4. The scorer, checked before the run** (no API):
```
$ … runs/w22/scoring/make_fake.py       exit 0 asks 525      (a fake 10-day run, runs/w22/fake/)
$ … runs/w22/scoring/w1_score.py runs/w22/fake runs/w22/fake/cache/fake-daniel_ate_it-seed2.json 0
                                        exit 0; every rule computed (runs/w22/scoring/fake_score.txt)
$ … runs/w22/scoring/selfcheck.py       35 ok lines; "all checks ok"; exit 0 (runs/w22/scoring/selfcheck.txt)
$ … runs/w22/scoring/cap_check.py       cap raised: stopped: the 3-ask cap … (3 live asks sent). | requests sent to api: 3
```
`selfcheck.py` edits copies of the fake run to test W1-1, 2, 4, 5, 6, 7, 9, 10 and 11 where the fake model's own words never reach.

**5. The run** (`runs/v22/daniel_ate_it-seed2.stdout.txt`, `.stderr.txt` (empty), `seed2.started_utc.txt`, `seed2.ended_utc.txt`,
`seed2.exit.txt`):
```
$ GEMINI_API_KEY=<the one-off key, process only> PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 \
    .venv/Scripts/python.exe -u runs/v22/run_capped.py > runs/v22/daniel_ate_it-seed2.stdout.txt 2> …stderr.txt
started 2026-10-08T20:04:14Z    ended 2026-10-08T20:35:39Z    exit 0
  day 3 min 00: model asked for 4; day asks 4 of 40; so far 4 live, 96 cached, 4 API requests
  night 5: rainy; bedtime Daniel go_next_door, Elena lie_awake, Leo lie_awake, Mara lie_awake; Daniel out (back shaken, with water), water 9 L
  day 7 17:18: Q6, rain began: Daniel, Elena, Leo, Mara asked in the kitchen
  day 9 11:30: Q6, rain began: Elena, Leo, Mara asked in the kitchen
  api_requests 405   answers_live 402   answers_from_cache 96   run_seconds 1875.4
  story_sha256: cff2506323eea49af0cc07d1186ffc8072f084b25bc4800d27047bde09617f11
```
The story is `runs/v22/daniel_ate_it-seed2.md`; transcript and meta beside it. The run was started in the background by this
session; nothing was stopped.

**6. Scoring** (`runs/v22/scoring/score_v22.txt`; the account in `account.txt`; the lines in `lines.txt`):
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe runs/w22/scoring/w1_score.py > runs/v22/scoring/score_v22.txt
exit 0
W1-1 FAIL (1 outward acts on nights [5]: [(5, 'Daniel', 'went_out')])
W1-2 PASS (6 of 28 bedtime reasons match FROZEN)
W1-3 FAIL (1 bedtime go_next_door or go_further: [(5, 'Daniel', 'go_next_door')])
W1-4 PASS (12 WATER speech acts on 4 of 8 days; by day {3: 0, 4: 0, 5: 0, 6: 8, 7: 2, 8: 1, 9: 1, 10: 0})
W1-5 FAIL ((a) 100% over 2 spells; (b) does not hold; collect_rain 1, rain_out 0)
W1-6 PASS (0 NOWATER claims; 0 while the store was > 0; 0 unsure)
W1-7 FAIL (below 50 L at ((5, 840), 43.5); water-rule acts [(9, 273, '11:33', 'Leo', 'ration_water', 'We need to ration what is left in the pans and the bin so it actually lasts.')])
W1-8 FAIL (live 402; day asks {3: 40, 4: 40, 5: 40, 6: 40, 7: 42, 8: 48, 9: 48, 10: 44}; largest estimate (2602, 'day', 'Daniel'))
W1-9 PASS (0 of 402 body lines match)
W1-10 PASS (38 of 326 = 11.7%)
W1-11 FAIL (went_out nights [5])
```
**The largest estimate, by a replay** (`runs/v22/scoring/replay_max.txt`; `runs/w22/scoring/replay_max.py`, no API, a temp
copy of `cache/v22`):
```
replay exit 1 prompts 498 from day 3 on 402
('day9', 'Daniel', 2602)  ('day9', 'Daniel', 2601)  ('day8', 'Daniel', 2599)  ('day8', 'Daniel', 2597)  ('day9', 'Daniel', 2597)
```
The replay's "exit 1" is `morning.py:326-328` (its temp folder has no original story to compare with), as in v21. 498 =
96 + 402.

**7. At the end** (`runs/v22/end_checks.txt`):
```
checked_utc: 2026-10-08T20:35:48Z
eb3758cc599b9967e8d918d917e42ed1ac51bebb17f66c7e0fc8418ba2c3a6bf *reports/days_v22_plan.md   (as recorded)
     23 OK                                                    (the *.py and config.json sha256s of plan_frozen.txt)
git status --short:  ?? cache/v22/  ?? reports/days_v22_plan.md  ?? runs/v22/  ?? runs/w22/  (and runs/v6's three replay files)
git diff --stat:     (empty)
cache/v16 seed2:     d79a4939… (unchanged)
```

---

## days_v22_plan.md

### v22 plan: W1's live run, v16 seed 2, days 3 to 10

Mode: run. v16's seed 2, played on to day 10 (`--days 10`), on the W1 code (HEAD `a4edf84`, clean tree apart from three
untracked `runs/v6` replay files). Output `v22`: `runs/v22`, `cache/v22`. The control is v21 (`reports/days_v21.md`,
`runs/v21/daniel_ate_it-seed2.transcript.json`), the same seed from the same state on the code before W1.

**Why:** to see whether honest bodies, water and rain change what the house does over ten days, compared with v21,
where it never moved (0 trips on nights 3–9; 16 of 28 bedtime reasons that say they cannot stand, walk or go).

**How it runs:**
- **The cache.** `cache/v22` starts as a copy of `cache/v16`'s seed 2 file. Days 1–2, nights 1–2 and minds 1–2 are
  answered from it.
- **The check before.** A no-API replay with `--days 10` must go live first at day 3, min 00. If not, the run stops
  and is reported.
- **The run.** Seed 2 runs live once, `--days 10`, out `v22`. It is not rerun or resumed. If it stops part way, it is
  reported with how far it got.
- **The 470 cap.** The run is started through `runs/v22/run_capped.py` (as v21's, cap 470): when 470 live asks have
  been sent, the next one raises `gemini.CallCapReached` before any request goes out. No prompt, option or answer
  is changed. If that happens the run is reported with how far it got. W1-8's own limit (450) is a prediction; the
  cap (470) is the stop.
- **The key.** The run uses an API key the user gave in chat for this one run, as the process's `GEMINI_API_KEY`
  only. It is written nowhere.
- **No edits after this plan is recorded.** Once it is recorded (sha256 and time, `runs/v22/plan_frozen.txt`), no
  code, test or line of this plan is edited. The scorer `runs/w22/scoring/w1_score.py` and `run_capped.py` are new
  files, written after the plan and before the first live call; they are checked on a fake 10-day run and the
  scorer on v21.

#### The seeded weather of days 1 to 10 (no API; `runs/v22/weather_days1_10.txt`)

Printed by `weather.Weather(2)`, the generator the run uses (`morning.py` prints the same lines):
```
  weather day 1: wet, 2.5 mm (09:00 to 13:09); 7.7 to 14.2 C outdoors, 15.0 C indoors
  weather day 2: dry; 11.2 to 15.2 C outdoors, 17.2 C indoors
  weather day 3: dry; 12.6 to 16.1 C outdoors, 18.4 C indoors
  weather day 4: dry; 7.1 to 19.4 C outdoors, 17.2 C indoors
  weather day 5: wet, 12.3 mm (22:03 to 03:42 the next day); 7.1 to 14.3 C outdoors, 14.7 C indoors
  weather day 6: wet, 4.5 mm (05:27 to 11:03, 06:30 to 10:45); 11.6 to 13.6 C outdoors, 16.6 C indoors
  weather day 7: wet, 1.2 mm (04:36 to 10:09, 17:18 to 20:21); 11.8 to 13.3 C outdoors, 16.6 C indoors
  weather day 8: dry; 8.0 to 19.1 C outdoors, 17.5 C indoors
  weather day 9: wet, 17.8 mm (11:30 to 16:30); 7.8 to 14.0 C outdoors, 14.9 C indoors
  weather day 10: dry; 8.6 to 18.6 C outdoors, 17.6 C indoors
```
- **Rain spells that start between 07:00 and 21:00 on days 3–10 (W1-5's spells): two.** Day 7 at 17:18 (to 20:21) and
  day 9 at 11:30 (to 16:30). The first is day 7 at 17:18.
- **Rain at other times** (not W1-5's spells, but the house hears or meets it): day 5, 22:03 to 03:42 (a rainy night 5:
  the bedtime rain option is offered, and the front-door draws are halved); day 6, 05:27 to 11:03 and 06:30 to 10:45
  (it is already raining at 07:00 of day 6, so "Rain is falling" is in the day's lines, with no onset in the day);
  day 7, 04:36 to 10:09 (the same, day 7 morning).
- **Days 3 and 4 are dry**, with 18.4 and 17.2 °C indoors; days 8 and 10 are dry. Days 5, 6, 7 and 9 are wet.

#### Predictions (frozen)

W1's section 8 (`reports/world_design.md:785-819`), verbatim, with the changes marked **[changed]** or **[added]** (W1-1, W1-5, W1-11; W1-8 is restated as the design has it).

**The run:**
- v16 seed 2, `--days 10`, W1 code, scored on days 3–10 and nights 3–9.
- The control is v21 (`runs/v21/daniel_ate_it-seed2.transcript.json`).
- The script is `runs/w22/scoring/w1_score.py` (the design said `runs/w1/scoring/w1_score.py`), written and run on a
  fake run before the live one.

**Regexes (case-insensitive) used below:**
- `FROZEN = (too weak|cannot|can't|can not|unable|barely|no strength)\b[^.;]{0,40}?\b(stand|walk|move|go|make it|get up|leave|carry)\b`
- `WATER = \b(water|thirst\w*|drink\w*|rain\w*|bath)\b`
- `NOWATER = \bno (more )?water\b|\bwater is (gone|finished)\b|\bout of water\b|\bwater (has )?run out\b`
- `CAN = \bthe can\b|\btook\b|\bstole\b|\bstolen\b|\bsteal\w*|\blie[ds]?\b|\blying\b|\bliar\b`

**"Speech act":** a day act with words (`a["words"]`), as `runs/v21/scoring/lines.txt`.

| # | Prediction | Counting rule | v21 |
|---|---|---|---|
| **W1-1** | **The house acts on its own more often than in v21: ≥ 3 outward acts, on ≥ 2 different days or nights.** | **[changed]** Count only chronicle events of nights 3–9 that are `went_out`, and `got_up` or `at_door` with no `went_out` for that leaver that night (once per leaver per night). `collect_rain` and `rain_out` do not count. Code acts (bringing containers in) are not counted. | **1** (N5 `got_up`; §11, B4) |
| W1-2 | The body no longer forbids: ≤ 8 of the 28 bedtime reasons of nights 3–9 match FROZEN. | Every `night{n}` decision with `ask == "bedtime"`, n = 3–9; `reason` matched by FROZEN. | 16 of 28 |
| W1-3 | Going out is chosen at bedtime at least twice. | Bedtime options `go_next_door` or `go_further`, nights 3–9: ≥ 2. | 1 |
| W1-4 | The world reaches their words. | Speech acts matching WATER on ≥ 4 of the 8 days 3–10. | 0 acts, 0 days |
| W1-5 | Rain reaches the house, and the house answers it. | (a) For each rain spell start between 07:00 and 21:00 on days 3–10 (from the weather record), every person in the house and not asleep at that minute has a `heard` percept event of it: must be 100%. (b) The first such spell's Q6 stretch holds ≥ 1 act that is `collect_rain`, or a speech act matching `\b(rain|catch|bucket|bin|pots?)\b`. NOT TESTED if no spell starts by day in days 3–10. **[added]** Also reported: how many `collect_rain` and `rain_out` acts there were (day acts and bedtime choices). | no weather |
| W1-6 | Water claims are true. | Speech acts and reasons (day and night) matching NOWATER at a minute when the code's drinking store is > 0: ≤ 1. | 0 (no claims; v15 had 1, `reports/quiet_day_design.md:146-148`) |
| W1-7 | Rationing comes when the end is visible. | If the drinking store falls below 50 L (half of its 100 L on day 3, 07:00) at a minute of day k ≤ 9, then a `ration_water` or `save_water` act occurs by 21:00 of day k + 1. NOT TESTED if it never falls below 50 L by day 9. | no water |
| W1-8 | Cost stays bounded. | **[restated: the design already has these figures]** Live asks of days 3–10 ≤ 450; each day's asks ≤ 56 (40 + Q5 8 + Q6 8); largest `estimate_tokens` of any prompt ≤ 2600 (as v21's T2). | 337; days ≤ 40; 2435 |
| W1-9 | No body line forbids an act. | Every "Your body:" line of every prompt of days 3–10 and nights 3–9 (replayed, no API): 0 matches of `impossible\|cannot\|can't\|unable\|barely (stand\|walk\|move)`. | stage 3 lines match (`quiet.py:54`) |
| W1-10 | The can is not the whole talk. | Speech acts of days 3–10 matching CAN ≤ 20%. | 63 of 245 = 25.7% |
| **W1-11** | **[added]** The world is in the leaver's own reasons. | At least one `went_out` night (nights 3–9) has a leaver whose bedtime reason, or whose trip position spoken that day, matches WATER. | no trip |

**What would make W1 wrong, by the counts:**
- W1-1 and W1-3 both fail, and W1-2 holds: honest words alone do not move the house, and W1-4's water talk is talk
  without acts. The next step is then the world's people (W2), not more body wording.
- W1-2 fails: the model is reading weakness into any body line. The wording is the first thing to cut, as
  `reports/quiet_day_design.md:115-117` already said of the stage lines.

#### Counting rules (fixed with the plan; they spell out the table, they change no prediction)

All from `runs/v22/daniel_ate_it-seed2.transcript.json` and `.meta.json`, `cache/v22`'s seed 2 file (its prompts), and
`weather.Weather(2)`. They are read by `runs/w22/scoring/w1_score.py`, which gives the same rules for v21
(`runs/v21`, `cache/v21`) as the control column. Days 3–10 = the transcript's `day3` to `day10`; nights 3–9 = `night3`
to `night9`. Clock: day minute 0 is 07:00; 21:00 is minute 840.

- **A model act:** a day act with `mode == "model"`. **A speech act:** a model act with non-empty `words`.
- **W1-1.** The chronicle events (`chronicle.events`) with scene `N3` to `N9`. For each night and each leaver
  (`actor`, and every name in `members` of a `went_out`): 1 if the leaver has a `went_out` that night, else 1 if the
  leaver has a `got_up` or `at_door` that night, else 0. The sum is the count; the nights with any 1 are the
  different nights. PASS if the count ≥ 3 and the nights ≥ 2.
- **W1-2, W1-3.** As the table, from `night{n}["decisions"]`, `ask == "bedtime"`. W1-3 counts `option`.
- **W1-4.** The `words` of each speech act of day k, matched by WATER; PASS if ≥ 4 of the days 3–10 have ≥ 1.
- **W1-5.**
  - **(a)** For each qualifying spell (start between 07:00 and 21:00 of day k, k = 3–10, from `Weather(2)`), the set
    that must have heard it: the people not in `away` and not in a rest span (`quiet.spans`, routine `rest`, covering
    that minute) at the spell's start minute. The set that heard it: the `heard` list of the `quiet.rain` entry at
    that minute. 100% = every one of the first set is in the second. All such spells are checked.
  - **(b)** The "Q6 stretch" is the stretch (`quiet.stretches`) whose trigger is Q6 and whose start is that of the
    first qualifying spell. If Q6 did not fire for that spell (it was in played turns, it had fired today, nobody was
    awake: the Q6 entry in `quiet.log`), the acts from the spell's start to 30 minutes later are read instead, and
    the report says so. Its acts hold (b) if any is `collect_rain` or a speech act matching the regex.
  - **Reported:** the count of day acts `collect_rain` (days 3–10) and of bedtime decisions `rain_out` (nights 3–9).
- **W1-6.** The text read: the `words` of speech acts of days 3–10, and the `reason` and `say` of each decision of
  nights 3–9. The code's drinking store at a minute = `tap + rain` of `quiet.water` (the World's log: 07:00, each
  water rule, each bin set out, bedtime). A claim at a minute is a violation when the log entry at or before it shows
  `tap + rain` > 0 and the first entry after it (if any) does too. A claim between two entries that disagree is listed
  as unsure and not counted. A night's reason is read at that day's bedtime entry. PASS if violations ≤ 1.
- **W1-7.** The first `quiet.water` entry (by day and minute) with `tap + rain` < 50 gives day k. NOT TESTED if there is
  none by day 9 (k ≤ 9). Otherwise PASS if some model act with option `ration_water` or `save_water` has its
  `decided_at` at or before day k + 1, minute 840. When it was said, and by whom, is reported.
- **W1-8.** `answers_live` from the meta (the cap stop: 470 reported with how far it got); `day{k}_quiet.day_asks` for
  k = 3–10; the largest `estimate_tokens(system + prompt)` over every live prompt (the system of its scene: day,
  night or night mind), read from the cache file's entries after the 147 of `cache/v16`.
- **W1-9.** Every line starting "Your body:" in those same live prompts (day, night and night-mind prompts alike: a
  superset of the days and nights the table names). Matched by the pattern; every distinct line is listed with its count.
- **W1-10.** The CAN share of all speech acts of days 3–10; PASS if ≤ 20%.
- **W1-11.** The nights of 3–9 with a `went_out` event. For each leaver of each such night: their bedtime decision's
  `reason` in that night, or their speech act on the day before it (day k, for night k) whose option is a trip
  kind (`talk.act_of(option)[0] in world.TRIP_KINDS`), matched by WATER. PASS if any does. NOT TESTED if no night has
  a `went_out`.
- **Verdicts:** PASS / FAIL / NOT TESTED for each, with the evidence. If the run stops before it writes a transcript,
  the predictions that need it are NOT TESTED, and the report says how far the cache shows it got.

