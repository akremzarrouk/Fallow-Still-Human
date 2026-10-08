# v22 gaps: why three v22 failures happen

Mode: investigate. Read only: no code, test or prompt was changed and the API was not called. Paths are relative to
`Prototypes/llm-morning/`. The scripts and raw outputs are in `runs/v22gaps/` (cited by path); the prompts quoted are the
live prompts of `cache/v22` (entries 147 on, the 402 live asks). Clock stamps are the run's own. Where a thing was looked for
and absent, it says NOT FOUND.

## Commit

- **Commit `966d5b5`** (`966d5b5fa0bb58ae28e76c9516aaf1a457248358`): 40 files, 191,011 insertions. It holds
  `reports/days_v22.md`, `reports/days_v22_plan.md`, `runs/v22/` (incl. `merged/`), `runs/w22/` (the scorer, its
  fake run and checks) and `cache/v22/`; the same kinds of files as v21's commit `3be6e10`. `runs/v6`'s three replay files
  were left out, as before. No file outside those four paths is in it (0).
- **The API key is in no file of the commit.** Before the commit, `git grep --cached` for the key's middle part and for the
  general shape `AQ.` plus 30 or more characters found nothing (exit 1); after it, the same two searches over `HEAD` found
  nothing (`runs/v22gaps/commit_checks.txt`). A `grep -rl` over the whole repository finds the key's middle in no file.
- **After the commit:** `git diff --stat` is empty; `git status --short` shows `runs/v22gaps/` (this investigation, not
  committed) and the three old `runs/v6` replay files.

## Answers, short

| # | Question | Answer |
|---|---|---|
| 1 | Why does Mara say one line seven times, and does the own-words hiding apply? | **The hiding applies** on day 3 and in every stretch (306 of 342 day prompts carry the block, **0** quote a line of their own). The repeats come from **standing lines**: Mara's night-mind *intent* ("I will ask Daniel why he went out… with nothing to show for it") is in all 7 prompts, with 5 more that say he came back with nothing (four facts and her own night thought). A second channel is open: the **night mind quotes the person's own spoken line** and block B shows it back verbatim (Leo, day 7: 9 prompts, 4 verbatim repeats). |
| 2 | Words vs deeds: does a day's trip position reach the night? | **Yes, it does** (a promise line, the plan line, the person's own last words), on nights 8 and 9. Nights 6 and 7 had **no** position that day. **No option or chance depends on a position** (NOT FOUND). Daniel read "You said you would go… If you are going, it is now." and chose `sleep` twice. |
| 3 | Day 7 17:18 Q6 | `collect_rain` is offered only while the bin is not out (`world.py:594`); the bin went out on day 6 and nothing ever brings it in. Q6 itself does not look at the options. |
| 4 | Cost, day 9 Daniel, 2602 | **1205 of the 2602 tokens sit outside the trimming budget**; the part the budget sees is 1397 of 1400. Block A, B, C alone are 560. |

**An error in `reports/days_v22.md` (not corrected there, so that the commit stays as it was):** §2 day 3 says Mara's line
was "the same line 7 times in the morning". Counted exactly it is **7 lines of one frame on the day, 6 of them in the
morning, in two wordings** ("into the night": 3, "into the dark": 4; §1).

## 1. Repeats

### 1a. Mara, day 3: the seven lines

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

### 1b. Is the own-words hiding applied on day 3+ and in quiet-day stretches?

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

### 1c. Lines said word for word 2+ times, per person per day

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

## 2. Words versus deeds: Daniel, nights 6 to 9

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

### 2a. Does a day's trip position reach the night prompt or its options?

| Path | Reaches | path:line |
|---|---|---|
| The speaker's own latest position `volunteer` (also `still_going`) | **The prompt**: the promise line, a `Now` line | `night.py:497-499` (`own = p.trip_heard.get(q)`; `PROMISE`, `night.py:58`); far: `night.py:500-501` (`FAR_PROMISE`, `night.py:71`) |
| Every position heard that day, each speaker's latest | **The prompt**: "About going there tonight: …" | `world.py:703-734` (`heard_plan`), `world.py:736-748` (`trip_lines`), `world.py:1017`; outside the trimming budget, `world.py:1161` |
| The speaker's own lines | **The prompt**: "Your own last words today" (minute and verb) | `world.py:1151`, `world.py:1781-1782` |
| Everyone's lines of the evening | **The prompt**: the last lines of "What else happened today" | `world.py:1146` |
| The previous day's positions and what came of the night | **The next night's prompt**: "What was said yesterday about going out last night…" | `night.py:1066-1069`, `night_came_to` `night.py:1075-1089` |
| A position changing the **bedtime options or any chance** | **NOT FOUND.** The options are the same five for everyone (`night.py:502`: `BEDTIME`, `night.py:48-53`, plus `go_further` if they know next door is empty); in `night.py`, `p.trip_heard` is read only at `497, 1081, 1225` (the last resets it) | |

A position never moves a person; it is a line in a prompt. Leaving is `go_next_door` at bedtime (`night.py:502`, `night.py:507-509`).

### 2b. Q5, the evening, days 4 to 10

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

## 3. Q6 with nothing to do: day 7, 17:18

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

## 4. Cost: day 9, Daniel, 2602

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

## 5. One line per finding

1. **Own words in the night mind's `meaning` and `intent`:** the mind's S6 check passes a quotation that is in the person's own record, so block B quotes the speaker's own sentence; drop a quotation that matches the speaker's own spoken line (`mind.py:278-281`, `336-339`).
2. **The standing intent repeats as the next day's line:** Mara's intent is in every morning prompt; show an intent only until the person has spoken it once that day, or drop it from the prompts that follow a spoken line.
3. **The promise and plan lines read, and the model sleeps ("too weak to stand"):** nothing links a spoken position to the bedtime choice; it is the model's, so nothing in code is wrong, and what W2 needs is a situation at the door, not another line.
4. **`collect_rain` is a one-shot:** nothing brings the bin in, so the option is gone after day 6; whether the bin should be emptied or brought in is a design question for the next water stage.
5. **Q6 on a rain with no action:** it still spends a reserved 8-ask stretch on a conversation that continues; Q6 could be skipped (or shortened) when no rain option is offered.
6. **Cost:** the 1205-token outside-the-budget part (carry 560, trip 515, W1 126) is what makes the largest prompt; the cheapest cut is the day-2 "kept" memories (101 tokens) or the trip lines.

## 6. Commands and output

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
