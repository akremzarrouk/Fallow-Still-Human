# v19: false statements about the past, and whether the speaker's prompt held the true fact

Mode: investigate, read only. No API call, no code change. `runs/v19` and `cache/v19` were only read: their sha256s are
unchanged (§5). Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad,
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\ba344a5c-5509-4487-aefe-3209becb4468\scratchpad\contra`.

**Method:**
- **The lines.** Every spoken line of days 3–5 (seed 2: 115, seed 3: 111) was read against the chronicle
  (`runs/v19/daniel_ate_it-seed{2,3}.transcript.json`, key `chronicle`).
- **The prompts.** Each listed line's exact prompt comes from a no-API replay of a temp copy of `cache/v19`
  (`$S/replay_trace.py`). The replay wraps `Morning.prompt_parts` (`world.py:1088`) and `memory.bounded`
  (`memory.py:229`) to record each prompt, its size estimates and the lines each limit removed. Its story is byte-
  identical to `runs/v19/daniel_ate_it-seed{2,3}.md`. "Prompt line N" is the line number in `$S/prompts/<id>.txt`.

## Result

| # | Seed, day, time, speaker | The statement | The true fact (chronicle) | In the prompt? |
|---|---|---|---|---|
| S2-1 | 2, day 3, min 00, Leo | "Daniel went out in the night and came back with nothing, just like before." | Night 2 was the first trip by anyone: night 1 had no group (`night.groups` empty); N2-10 is the only `went_out`. | NOT FOUND as a fact; nothing trimmed |
| S2-2 | 2, day 3, min 06, Leo | "Daniel, you snuck out last night and brought nothing back, just like you always do." | As S2-1. | NOT FOUND as a fact; not among the trimmed lines |
| S2-3 | 2, day 4, min 00, Daniel | "Mara, stop saying that, I already told you I didn't take anything." | Daniel took the can and admitted it: D1-022, min 33, "I took it in the night, I'm sorry." | **FOUND** |
| S2-4 | 2, day 5, 10:27, Daniel | "Mara, stop lying about what I did and watch your tongue in front of Mom." | As S2-3. Mara's line it answers: "You are the one who took the food, Daniel …" (10:24). | **FOUND** |
| S2-5 | 2, day 5, 11:06, Daniel | "Mara, stop lying about what happened and blaming me for everything." | As S2-3. | **FOUND** |
| S3-1 | 3, day 4, min 00, Mara | "You sneaked out into the dark street last night while we were sleeping, Daniel, and you came back with nothing." | Night 3: all three others chose `lie_awake`. Leo saw Daniel go (N3-06). Mara heard the door, got up and waited by it (N3-10), and saw him come back. | **FOUND** |
| S3-2 | 3, day 4, min 03, Leo | "You stayed home last night because it was suicide, Daniel, and nothing has changed tonight." | Night 3: Daniel went further along after Leo's "Don't go out there, Daniel. It's suicide." (N3-06, N3-07, N3-11), and came back with nothing. | **FOUND** |
| S3-3 | 3, day 5, min 00, Leo | "Daniel, you aren't going anywhere. We agreed last night." | Night 4 has only the four bedtime events (N4-01…04): nobody got up and nothing was said. The last talk of going was day 4 at 11:00 (D4-050…053): Daniel offered, and Mara, Leo and Elena said he must stay home. | **FOUND** |
| S3-4 | 3, day 5, min 03, Leo | "Daniel, you went three days ago and came back empty-handed, and you're not going again tonight." | Daniel went out twice: next door three nights ago (N2-11), and further along the night before last (N3-11). Both came back with nothing. | Night 2: FOUND. **Night 3: NOT FOUND, not trimmed** |
| S3-5 | 3, day 5, min 09, Mara | "Daniel, you already lied about the food once and you are not going anywhere tonight." | Daniel denied taking it 8 times before admitting it: D1-004, 006, 009, 013, 016, 019; D2-004, 008. He admitted it at D2-022. | One denial FOUND; **the other 7 NOT FOUND, not trimmed** |
| S3-6 | 3, day 5, min 15, Leo | "Daniel, you nearly got Mara killed last time, and staying here is the only safe choice." | No night's group ever included Mara (nights 1–4). Daniel went alone both times (N2-11, N3-11). | **NOT FOUND, not trimmed.** The nearest line is the backstory, below. |
| S3-7 | 3, day 5, 09:57, Leo | "You went out once and came back with nothing, Daniel, and going again is just throwing your life away." | As S3-4: twice. | As S3-4 |

**Counts:**
- **Statements: 12.** The prompt held the whole true fact for 6 (S2-3, S2-4, S2-5, S3-1, S3-2, S3-3), and part of
  it for 3 (S3-4 and S3-7: night 2 only; S3-5: one denial of 8).
- **Not held:** S2-1, S2-2 and S3-6 entirely; the night-3 trip of S3-4 and S3-7; 7 of S3-5's 8 denials.
- **The size limits trimmed none of these facts** from the prompt that produced the statement.

## 1. The prompt lines, statement by statement

**S2-1, S2-2 (Leo, seed 2, day 3).**
- **NOT FOUND:** no line says that night 2 was Daniel's first trip, or that nobody went out on night 1.
- **The lines nearest to it** (S2-1 prompt lines 9, 17, 18; S2-2 lines 9, 14, 15):
  - `About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.`
  - `- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)`
  - `- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you did it)`
- **What the limit cut.** S2-1's prompt was cut nothing. S2-2's prompt was cut 7 of this morning's lines and 3
  backstory lines ("Day 1: Daniel boards…", "Day 1: Leo says the water…", "Day 2: The taps run dry…"). None of them is
  about a trip.

**S2-3 (Daniel, seed 2, day 4, min 00).** FOUND. Prompt lines 7, 12, 22, 27:
- `About the can: you ate it yourself, and you admitted it three days ago.`
- `On your conscience (a lot): you ate the can in the night, and nobody saw; three days ago, you accused Leo of what you did, at minute 03; …`
- `- Day 3: In the night Daniel eats a can standing at the counter in the dark. Nobody sees. (you did it)`
- `- Three days ago, you admitted taking the can, in front of everyone. You thought then: "I accused Leo when I was the one who ate the can in the night, and my false pride made me lie to them for too long."`
- The answer's own `reason`: "I have to defend myself against her accusations even though I know I took it." Cut: nothing.

**S2-4, S2-5 (Daniel, seed 2, day 5, 10:27 and 11:06).** FOUND. Prompt lines 7, 14, 20, 25 of each: the same four
lines as S2-3, with "four days ago": `About the can: you ate it yourself, and you admitted it four days ago.`, the
conscience line, "Day 3: In the night Daniel eats a can …", and `- Four days ago, you admitted taking the can, …`.
The answers' `reason`s: "I will not let Mara undermine me and point fingers when I am the only one trying to keep
this family afloat." (10:27) and "I cannot sit here and let Mara keep throwing false accusations in my face." (11:06).
The limit cut 30 and 32 of the day's lines, and 4 backstory lines (Day 1, Day 2). None is about the can.

**S3-1 (Mara, seed 3, day 4, min 00).** FOUND. Prompt lines 38, 40, 41:
- `- Last night you slept in the back room with Elena. You lay awake and listened.`
- `- In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.`
- `- Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).`
- Her `reason`: "I cannot let him pretend he did nothing wrong when I waited up all night for him by the front door." Cut: nothing.

**S3-2 (Leo, seed 3, day 4, min 03).** FOUND. Prompt lines 34, 35, 36, 54:
- `- In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).`
- `- You told Daniel, low, not to go: "Don't go out there, Daniel. It's suicide." He answered: "I have to do this, Leo, stay back.", and went all the same.`
- `- Before dawn you heard the front door again. You did not see who.`
- `2. Mara confronts Daniel: "Daniel, you snuck out into the dark street last night behind our backs and you are just putting us all in danger again."`
- **What the limit cut:** 4 of this morning's lines and 3 backstory lines. One cut line also says it:
  ``- min 00: Daniel says he will not go: "I went out past the neighbour's house last night to look further down the street, …"``
  §4.1 covers its "says he will not go".

**S3-3 (Leo, seed 3, day 5, min 00).** FOUND. Prompt lines 34, 36:
- `- About going to the neighbour's house last night, where it was left: Daniel offered to go (11:00); Mara said Daniel must stay home (11:00); you said Daniel must stay home (11:00); Elena said Daniel must stay home (11:00).`
- `- Last night you slept in the brothers room with Daniel. You lay awake and listened.`
- No other line describes night 4. Cut: nothing.

**S3-4, S3-7 (Leo, seed 3, day 5, min 03 and 09:57).**
- **Night 2: FOUND** (prompt line 9): `About the neighbour's house: Daniel went there three nights ago and came back with nothing. Outside is dangerous.`
- **Night 3 (further along): NOT FOUND,** in all of Leo's day-5 prompts. Prompt line 10 reads:
  `About the street: the houses further along it have not been searched; nobody knows what is left in them, …`
  But house 1 was searched on night 3 (`fixed.far_house_0`, N3).
- **Not trimmed.** S3-4's cut lines are three of this morning's min-00 lines and 3 backstory lines (Day 1 ×2, Day 2).
  S3-7's are 20 of the day's lines (min 00 to min 12) and 2 backstory lines (Day 1). None is about night 3. §2 shows
  where the night-3 trip went.

**S3-5 (Mara, seed 3, day 5, min 09).**
- **One denial FOUND** (prompt lines 12 and 23):
  - `Against Daniel (a lot): three days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 03; …`
  - `- Three days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us and took the food himself, …"`
- **The other 7 denials: NOT FOUND, and not trimmed.** The cut lines are 10 of this morning's lines and 5 backstory
  lines. Block C picks one line for each person (§2), and Daniel's is his admission.

**S3-6 (Leo, seed 3, day 5, min 15).**
- **NOT FOUND:** no line says who went out on any night, beyond "Daniel went there three nights ago" (line 9).
- **The one line with Mara, Daniel and the street** (prompt line 19, backstory, before played day 1):
  `- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)`
- **Not trimmed.** The cut lines are 20 of this morning's lines and 3 backstory lines (Day 1 ×2, Day 2).

## 2. Where a fact from two nights back goes (S3-4, S3-6, S3-7)

A day-5 prompt can carry night 3 only through these blocks:
- **Block A, "Yesterday and last night".** It covers day 4 and night 4 only (`night.py:858`, `night.py:942`).
  Leo's day-4 prompts carried night 3 in block A (S3-2, lines 34–36).
- **Block B, "What yesterday left in you".** Leo's night-4 mind gave one memory of the trip. It was rejected:
  `{"ids": ["D4-002", "D4-004", "D4-010"], "meaning": "Daniel went out last night behind our backs and came back with nothing, yet he still insists on throwing his life away by going out again.", "verdict": "rejected: S5 last night"}`
  (`runs/v19/daniel_ate_it-seed3.transcript.json`, `mind4.leo`). S5 rejects any meaning holding a time word
  (`mind.py:123`, `mind.py:275-277`).
- **Block C, "What stays with you from earlier days".**
  - From day 5 it reads scenes of played day 3 and before: `scene_key(...)[0] <= today - 2` (`memory.py:76`). Night 3
    counts, and Leo witnessed `N3-11` (`went_out`, witnesses `leo: knew`).
  - It keeps **one line per person**, the heaviest (`memory.py:132-137`).
  - For Daniel, `confess` weighs 5 and `went_out` 4 (`memory.py:19`). So Daniel's line is the admission:
    `- Three days ago, Daniel admitted taking the can, …` (S3-4 prompt line 23).
- **The 560-token bound** (`memory.py:229`) removed nothing from Leo's day-5 blocks (§3).
- **The neighbour's-house line** counts only trips next door (`reports/stage_b.md` §1), so it names night 2. **The
  street line** names a far trip only to the person who made it (`night.py:181-195`); everyone else gets
  `STREET_UNSEARCHED` (`night.py:72`).

## 3. Prompt sizes and what the limits trimmed, days 3–5

**Two limits.** (1) `PROMPT_TOKEN_BUDGET = 1400` estimated tokens (`world.py:78`; characters / 3.6 + 1,
`world.py:116`) trims two blocks (`world.py:1120-1132`): **today**, the day's "What else happened" lines, and
**before**, the backstory "What you remember from the days before" lines. The trip block and the carried-in blocks A,
B, C do not count against it (`world.py:1101-1115`). (2) `MEMORY_MAX = 560` (`memory.py:9`) bounds A, B and C, once
per person per morning (`night.py:1041`).

**Columns:** *estimate* is the whole prompt, as `max_prompt_tokens` counts it (`world.py:1134`); *budget* is the part
counted against the 1400; *cut* is lines removed from that prompt (today / before); *most cut* is the largest cuts in
any of their prompts that day; the last column is the memory bound's trims that morning.

| Seed | Person | Day | Prompts | Largest: estimate / budget (at) | Its cut: today / before | Most cut that day | Memory bound: A, B, C |
|---|---|---|---|---|---|---|---|
| 2 | Daniel | 3 | 10 | 2260 / 1400 (20:09) | 35 / 4 | 41 / 4 | none |
| 2 | Daniel | 4 | 10 | 2306 / 1389 (11:06) | 32 / 4 | 48 / 4 | none |
| 2 | Daniel | 5 | 11 | 2378 / 1393 (min 12) | 16 / 5 | 40 / 5 | A shortened (variant 2 of 2: no quoted night words, no minutes) |
| 2 | Elena | 3 | 10 | 2061 / 1399 (10:27) | 27 / 5 | 43 / 5 | none |
| 2 | Elena | 4 | 11 | 2181 / 1394 (11:03) | 28 / 5 | 45 / 5 | none |
| 2 | Elena | 5 | 9 | 2275 / 1395 (min 09) | 8 / 5 | 35 / 5 | none |
| 2 | Leo | 3 | 10 | 2264 / 1397 (10:21) | 22 / 3 | 51 / 4 | none |
| 2 | Leo | 4 | 8 | 2217 / 1399 (11:03) | 27 / 3 | 32 / 3 | none |
| 2 | Leo | 5 | 9 | 2358 / 1399 (min 09) | 12 / 3 | 36 / 6 | none |
| 2 | Mara | 3 | 10 | 2268 / 1399 (10:21) | 15 / 5 | 47 / 5 | none |
| 2 | Mara | 4 | 11 | 2290 / 1397 (11:00) | 23 / 5 | 39 / 5 | none |
| 2 | Mara | 5 | 11 | 2357 / 1396 (min 15) | 18 / 5 | 41 / 5 | none |
| 3 | Daniel | 3 | 8 | 2340 / 1399 (min 06) | 7 / 4 | 30 / 4 | none |
| 3 | Daniel | 4 | 11 | 2366 / 1400 (min 12) | 15 / 4 | 39 / 4 | none |
| 3 | Daniel | 5 | 11 | 2254 / 1397 (min 06) | 6 / 4 | 40 / 4 | none |
| 3 | Elena | 3 | 8 | 2273 / 1399 (10:51) | 30 / 5 | 30 / 5 | none |
| 3 | Elena | 4 | 11 | 2238 / 1389 (11:00) | 41 / 5 | 41 / 5 | none |
| 3 | Elena | 5 | 9 | 2172 / 1400 (10:33) | 24 / 3 | 34 / 5 | none |
| 3 | Leo | 3 | 8 | 2357 / 1397 (min 15) | 20 / 3 | 32 / 7 | none |
| 3 | Leo | 4 | 10 | 2384 / 1395 (10:57) | 38 / 3 | 44 / 3 | none |
| 3 | Leo | 5 | 11 | 2252 / 1400 (10:36) | 41 / 3 | 41 / 4 | none |
| 3 | Mara | 3 | 8 | 2374 / 1400 (min 09) | 9 / 5 | 34 / 5 | A shortened (variant 2 of 2); 1 C thought dropped |
| 3 | Mara | 4 | 8 | 2376 / 1392 (10:57) | 32 / 7 | 33 / 7 | none |
| 3 | Mara | 5 | 9 | 2297 / 1400 (min 12) | 12 / 5 | 35 / 7 | none |

- **The "before" cuts** are always the oldest backstory lines first ("Day 1: …", "Day 2: …"), per `world.py:1127-1132`.
- **The "today" cuts** are the day's oldest lines. The prompt shows `- (earlier things, left out here)` in their place.
- **The memory bound removed no line** of A, B or C in any of the 24 mornings: `c_lines_removed` and
  `b_lines_removed` are empty everywhere (`$S/sizes.txt`).

## 4. Seen while reading the prompts (not statements)

**4.1 A far offer is shown to the others as "says he will not go".**
- **The cause.** `trip_gist` (`world.py:1541-1554`) has no case for the kinds `propose_far` and `volunteer_far`, so
  both fall to its last line: `return f"{p.name} says {he} will not go"` (`world.py:1554`). It is called at
  `world.py:1510`.
- **How often.**
  - In `cache/v19`, 63 prompt lines (38 in seed 2, 25 in seed 3) read "X says he/she will not go" followed by a far
    act's words.
  - Every such line in v19 quotes a `propose_far` or `volunteer_far` act. None quotes a refusal (§5, step 4).
- **An example:** Daniel's day-4 min-00 offer is the line cut from S3-2, quoted in §1.

**4.2 The street line after a far search.** In seed 3, house 1 was searched on night 3. All of Leo's, Mara's and
Elena's day-4 and day-5 prompts that carry the street line still read "the houses further along it have not been
searched" (§2, last point).

**4.3 Read and not listed in §1.** Each is shown with the record beside it:
- **"Behind our backs":** seed 3, day 4: Leo, min 00, "You went out last night behind our backs"; Mara, min 03 and
  min 12, "behind our backs". Leo saw Daniel go and spoke to him (N3-06). Mara heard the door (N3-10).
- **"The empty houses":** seed 3, day 3, 10:48, Leo: "Doing it again won't change the empty houses." Only next door
  had been searched by then.
- **"Without anyone saying a word":** seed 2, day 5, 10:24, Daniel to Mara: "… you think you can take whatever you
  want without anyone saying a word." Mara ate one portion on day 1 (D1-044).

## 5. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset.

**1.** Before anything: `sha256sum cache/v19/*.json runs/v19/*.md runs/v19/*.json > $S/v19.sha`. **2. The traced replay**, twice: once for the prompts, then again with the memory-bound wrapper added.
```
$ for n in 2 3; do env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/replay_trace.py" $n "$S"; echo "exit $?"; cmp "$S/runs$n/daniel_ate_it-seed$n.replay.md" runs/v19/daniel_ate_it-seed$n.md && echo "IDENTICAL"; done
seed 2: replay exit 1; prompts built 216, sent 216; by scene {'day1': 53, 'night': 4, 'day2': 24, 'night2': 7, 'day3': 40, 'night3': 4, 'day4': 40, 'night4': 4, 'day5': 40, (minds 0)}
seed 2 replay story IDENTICAL to runs/v19/daniel_ate_it-seed2.md
seed 3: replay exit 1; prompts built 251, sent 251; by scene {'day1': 45, 'night': 4, 'day2': 70, 'night2': 8, 'day3': 32, 'night3': 8, 'day4': 40, 'night4': 4, 'day5': 40, (minds 0)}
seed 3 replay story IDENTICAL to runs/v19/daniel_ate_it-seed3.md
$ sha256sum -c "$S/v19.sha" | grep -c ": OK"
8
```
- **Exit 1** is `morning.py:326-328`: the temp folder has no original story to compare with. `cmp` against
  `runs/v19` is the comparison.
- **The counts per scene** match `runs/v19`'s meta (asks of days 3–5 and nights 3–4). Night-mind prompts are built
  elsewhere (`mind.py:401`), so they are not traced.

**3. Each statement's prompt** (`$S/targets.py`). Each matched exactly one prompt, by scene, speaker and the
answer's `say`.
```
$ env -u GEMINI_API_KEY … .venv/Scripts/python.exe "$S/targets.py" "$S"
S2-1 seed 2 day 3 leo [('min 00', 2176, 1309, 0, 0)]        (minute, estimate, budget estimate, today cut, before cut)
S2-2 seed 2 day 3 leo [('min 06', 2246, 1379, 7, 3)]
S2-3 seed 2 day 4 daniel [('min 00', 2189, 1340, 0, 0)]
S2-4 seed 2 day 5 daniel [('10:27', 2342, 1379, 30, 4)]
S2-5 seed 2 day 5 daniel [('11:06', 2364, 1382, 32, 4)]
S3-1 seed 3 day 4 mara [('min 00', 2334, 1358, 0, 0)]
S3-2 seed 3 day 4 leo [('min 03', 2356, 1367, 4, 3)]
S3-3 seed 3 day 5 leo [('min 00', 2200, 1356, 0, 0)]
S3-4 seed 3 day 5 leo [('min 03', 2242, 1390, 3, 3)]
S3-5 seed 3 day 5 mara [('min 09', 2269, 1370, 10, 5)]
S3-6 seed 3 day 5 leo [('min 15', 2250, 1398, 20, 3)]
S3-7 seed 3 day 5 leo [('09:57', 2201, 1387, 20, 2)]
```

**4. "Says he will not go" in the cache** (a regex over every `cache/v19` prompt, matched to the day 3–5 act with
the quoted words):
```
seed 2: 9 distinct quotes, in 3, 8, 7, 4, 4, 3, 1, 3, 5 prompts = 38; each quote's act: propose_far (Mara d4 min 15,
        Daniel d4 19:00, Daniel d5 min 03, Mara d5 min 06, Daniel d5 min 09) or volunteer_far (Daniel d4 11:06,
        Daniel d5 min 06, Mara d5 min 09, Daniel d5 min 15)
seed 3: 5 distinct quotes, in 7, 7, 3, 4, 4 prompts = 25; each quote's act: volunteer_far (Daniel d3 min 06,
        d4 min 00, min 12, 09:57, 10:57)
```

**5. The chronicle facts** (`python -c` over `transcript.json`):
```
seed 3  Daniel denies: D1-004, D1-006, D1-009, D1-013, D1-016, D1-019, D2-004, D2-008
        went_out: N2-11 ['daniel'] and N3-11 ['daniel'], witnesses {daniel: did, leo: knew, mara: knew}
        N4: N4-01..N4-04, all bedtime; groups: night [], night2 [['daniel']], night3 [['daniel']], night4 []
seed 2  groups: night [], night2 [['daniel']], night3 [], night4 []; went_out: N2-10 only; D1-022 confess
```

**6. At the end:** `sha256sum -c "$S/v19.sha"`: 8 OK. No file under `runs/v19` or `cache/v19` was written.
