# Knowledge audit: what each person knows, believes and has been told

Prototypes/llm-morning, current version only (world.py, data.py, gemini.py, morning.py; also
talk.py where world.py imports from it). Audited 2026-09-26. Read-only: nothing was run and no API was
called. cache/v5 (426 prompts) and runs/v5 (11 transcripts) were read as examples. Paths are
relative to `Prototypes/llm-morning/`.

**Condition that applies to every example below:** in all 11 runs/v5 transcripts nobody ever
leaves the kitchen (0 moves; all four are in the kitchen every turn), and every one of the 426
cached prompts says "you are in the kitchen". The room-based filters (other rooms, voices
through walls, asides) exist in the code but no saved run exercises them.

---

## 1. Where per-person knowledge is stored

All of it is in fields of `Person` (world.py:191-235). None of it is a separate knowledge store.

| field | path:line | shape | what it holds |
|---|---|---|---|
| `backstory` | world.py:201-202 | list of str | "Day N: <summary> (you did/saw/heard it)". Only events whose `who` map names this person (data.py:128-160). |
| `memory` | world.py:203 | list of (minute, str) | This morning's perceptions and own acts, as free text. Trimmed to fit the prompt (see Q7). |
| `sure` | world.py:204 | list of str | "facts that are never trimmed": the opening, own culprit knowledge, confessions heard, own search results, eating/sharing seen. |
| `said_lines` | world.py:205 | list of str | Own words, with minute and act kind. |
| `triggers` | world.py:206 | list of (str, bool) | Social things since they last acted. These only decide *whether* the model is asked (world.py:776-788). They never enter the prompt text (grep §S2: `prompt_for` does not read them). |
| `history` | world.py:207 | list of {t, kind, seq} | Own acts per turn. Used for repetition limits and the "What you have been doing" line. |
| `heard` | world.py:208 | list of {seq, who, kind, target} | Structured record of lines heard: speaker, act kind, target. There are no words in it. |
| `addressed` | world.py:209 | dict or None | The last line aimed at them since they last acted. Sets turn order. |
| `aside_lead` | world.py:210 | id or None | Whom they took aside last turn. |
| `searched` | world.py:211 | set of rooms | Rooms they finished searching. |
| `knows_culprit` | world.py:212 | id or None | The culprit's own id at start; set to the confessor's id on hearing a confession (world.py:907). |
| `heard_question` | world.py:213 | bool | Has heard (or made) an "ask" or "accuse". Unlocks `deny` (world.py:325). |
| `confessed` | world.py:214 | bool | Has confessed. |
| `suspicion` | world.py:216 | `Track` (world.py:109-140): target id, strength 0-3, last_fall | Who they believe took the can. |
| `suspected_at` | world.py:217 | list of minutes | Minutes their answers named the current suspect. |
| `grudges` | world.py:218 | {person id: `Grudge`} (world.py:143-165): strength 0-3, last_change, events [(minute, fact, kind)] | Per-pair resentment (Q9). |
| `denials_heard` | world.py:219 | {person id: minute} | Last time they heard that person deny it. |
| `accused_by` | world.py:220 | {person id: minute} | Last time that person accused them. |
| `guilt`, `guilt_events` | world.py:222-223 | int 1-3 or None; list of (minute, fact) | The culprit only. |
| `seen` | world.py:224 | dict of levels | The levels shown at their last model decision. Used to detect a rise. |
| `feeling`, `feeling_until` | world.py:200 | str, turn | The last feeling the model gave. Others see it while it is "outward" (world.py:288-289). |

Outside `Person`, state that goes into a person's prompt without being stored for that person:
- `Morning.so_far[room]`: what was said and done in the room this turn, one shared list per room (world.py:646; appended throughout `apply`, world.py:845-1100).
- `Morning.portions`: the true count (world.py:245).
- Other people's `activity` and `feeling`, read directly at prompt time (world.py:501-503).

`Morning.said` (world.py:892-894) is a global log of every line. It is used only for the story and meta, not for any prompt.

## 2. How a person learns something, and which code updates it

**Seeing (in the same room at the moment of the act).**
- Recipients are `seen = self.others_here(p)`, the people still present in the actor's room this turn (world.py:851, 276-281).
- `perceive()` (world.py:818-822) appends to `memory` and optionally `triggers`. Seeing goes through it here:
  - search start: world.py:989
  - leaving: world.py:1006
  - taking someone aside: world.py:1015
  - two leaving together: world.py:1024
  - refusing to go aside: world.py:1039
  - sitting: world.py:1050-1053
  - arrivals, at the end of the turn: world.py:711-718
- Direct appends to `sure`: someone eats (world.py:1069); someone shares out the food (world.py:1095).
- `fact()` (world.py:962-968) calls `perceive(..., remember=False)`, so the fact becomes a trigger and is **not remembered**. It is used for a finished search (world.py:998), eating (world.py:1076) and sharing (world.py:1096).
  - Eating and sharing also go to `sure`.
  - "X finished searching … found nothing" goes nowhere that a prompt reads. Only the searcher gets it, in `sure` (world.py:996-997). In cache/v5, 0 prompts contain someone else's finished search, and 126 contain "you finished searching" (§S4).
- Computed at prompt time, not stored:
  - who is here, their activity label, and their feeling if outward (world.py:501-503)
  - the portions on the shelf (world.py:504-505)
  - this turn's `so_far` for the room (world.py:506-510)

**Hearing (speech in the same room).**
- world.py:896-940 runs for each `q in seen` when the actor gives words:
  - `perceive(q, …, heard, trigger=(heard, new))` → memory + trigger (world.py:897-899)
  - `q.heard.append({seq, who, kind, target})` (world.py:900-901)
  - `addressed` (world.py:902-903), `heard_question` (world.py:904-905)
  - on a confession: `knows_culprit` and a `sure` line (world.py:906-909)
  - `denials_heard` (world.py:920-921), `accused_by` (world.py:922-923)
  - grudges (world.py:910-928) and the culprit's guilt (world.py:929-940)
- Through walls (world.py:702-710): people in another room, outside the bathroom, get "Voices from the <room>." in `memory`. They get a trigger only if the line was new. No words and no speaker are passed.

**Being told.**
- Speech is the only way one person informs another. There is no structured "tell X that Y" act (option list: world.py:315-373).
- The only content from speech that the rules turn into structured knowledge is a confession: `q.knows_culprit = p.id` (world.py:907).

**Own acts** go into the actor's own `memory`, `sure` and `said_lines`:
- `memory`: world.py:945, 980, 990, 1008, 1016, 1032, 1041, 1054, 1061
- `sure`: world.py:951-952, 996-997, 1077, 1097
- `said_lines`: world.py:946
- A routine (non-model) "stay put" leaves no memory for anyone (world.py:979-980 writes only when `mode == "model"`). Others get it only in that turn's `so_far` (world.py:978).

**At the start.**
- Backstory filtered by `who` (world.py:201-202).
- The opening as a `sure` line for everyone (world.py:264).
- The culprit's `sure` line (world.py:265-266).
- The opening trigger (world.py:267).

**From their own model answer.**
- `suspects` → `suspicion.report` (world.py:749-756); naming yourself counts as "nobody" (world.py:748).
- `angry_at` → a grudge rises with kind "angry" (world.py:757-762).
- Grudges may fall (world.py:763-765).

## 3. When someone speaks, what the listener's state receives

Both the raw words and a structured act, but the structure comes from the **option id chosen, not from the words**.

- **Text:**
  - `line_text()` (world.py:824-840) builds `<gist>: "<words>"`. The gist comes from the act kind; "you" is used when the listener is the target (world.py:825).
  - That string goes to the listener's `memory` and `triggers` (world.py:897-899).
  - The same string, built without a listener, goes to the room's `so_far` (world.py:890-891, 895).
- **Structure:** `{seq, who, kind, target}` in `q.heard` (world.py:900-901). `kind` is `act_of(opt.id)` (world.py:849; talk.py:11-26). The words are not stored here.
- **Flags from the kind:**
  - `heard_question` (world.py:904-905)
  - `knows_culprit` + `sure` on confess (world.py:906-909)
  - `denials_heard` (world.py:920-921), `accused_by` (world.py:922-923)
  - grudges and guilt (world.py:910-940)
- **The words are never checked against the option.** `parse()` only checks that `say` is present and is a string (world.py:544-579). `Newness` says "the rules cannot tell what free words add" (talk.py:66).
- **No structured claim** (who took it, who is lying) is extracted from the words: NOT FOUND.

## 4. Can a false statement exist? Is it recorded?

**It can exist.**
- `say` is free text on every speech option (world.py:31-32, 570).
- `deny` is offered whenever `heard_question and not confessed` (world.py:325-326), with no check that the speaker is innocent. The culprit can therefore deny.
- `accuse_<x>` is offered to the culprit for anyone (world.py:328: the filter only restricts people who learned the culprit from someone else).
- `say_other` and `reassure_*` carry any words.

**How it is recorded:**
- **Culprit accuses someone else:** a guilt event for the culprit, "you accused X of what you did" (world.py:869-874).
- **Innocent person accused:** the *target* gets a grudge fact "…accused you of taking the can…, and you had not" (world.py:922-928). The rule reads the ground truth `self.culprit` (world.py:924). The speaker's record has nothing.
- **Earlier denial exposed by a confession:** the listener gets a grudge "admitted taking it … after denying it to you" (world.py:911-915). It is recorded only when a confession follows.
- **The culprit's denial itself:** no record. The code comment says "Their denials … add nothing" (world.py:929-931).
- **A truth flag** on `said` (world.py:892-894), `heard` (world.py:900-901) or transcript acts (world.py:658-664): NOT FOUND.
- **A false confession** is impossible: `confess` is offered only to the culprit (world.py:332-333).

**False statements that the rules themselves assert:**
- **The opening in miscount.** Every person's `sure` list gets "A can that should be on the shelf is not." (world.py:264, data.py:167). In miscount "nobody took anything; there were only ever two" (data.py:113). It appears in all 219 miscount prompts (§S4).
- **Elena's backstory line** "quite sure nobody in this house would take food from the others" (data.py:152). It is given to everyone as something they saw, and it is false in daniel_ate_it and mara_ate_it.
- **Wording that presupposes a taker** in every scenario, miscount included:
  - SYSTEM: "who they now believe took the can" (world.py:34-35)
  - `ask_who` (world.py:322), `accuse_*` (world.py:330), `search` (world.py:360)

## 5. Beliefs about other people's beliefs

NOT FOUND. No field holds what one person thinks another believes, knows or suspects.

The nearest records hold other people's **acts**, not their beliefs:
- `heard` (world.py:208)
- `denials_heard` (world.py:219) and `accused_by` (world.py:220)
- `pattern()` "Answered you differently from one time to the next" (world.py:449-474)

Each person's own `suspects` and `reason` answers are never shown to anyone else. They go only to their own `suspicion` (world.py:749-756) and to the transcript (world.py:662).

## 6. Source or confidence on a belief

- **Source, as text only:**
  - backstory "(you did/saw/heard it)" (world.py:201)
  - opening "(you did it / saw it)" (world.py:263-264)
  - confession "(you heard it)" (world.py:908-909)
  - eating "(you saw it)" (world.py:1069)
- **`memory` entries** carry a minute but no source field (world.py:203, 820).
- **Confidence:**
  - `suspicion` strength 0-3 (world.py:109-140). The prompt shows it as "a little / some / a lot" plus the minutes they named that suspect (world.py:67, 429-433).
  - Suspicion is fed **only** by the person's own model answer (world.py:749-756). Hearing an accusation or a confession does not change it.
  - In cache/v5, 9 of the 60 prompts written after someone had heard a confession still say "About the can: you have not settled on who took it" (§S5).
  - All 53 culprit prompts say "you have not settled on who took it", because naming yourself counts as nobody (world.py:748, 434-435), next to their `sure` line "you ate it yourself" (§S5; example below, lines 8 and 19).
- **Grudge** strength 0-3 plus the events behind it (world.py:143-165, 436-441).
- **Guilt** 1-3 (world.py:222, 409-416).
- **A per-fact confidence or source object:** NOT FOUND.

## 7. What of a person's past reaches their prompt, and how it is chosen or trimmed

`prompt_for` (world.py:483-540) assembles, in order:

1. **Head** (world.py:488-495): sheet, then `inside_lines` (world.py:424-446), then the house.
   - hunger in words; "grown hungrier" if hunger rose
   - suspicion: level word + the last 4 minutes named (`EVENTS_SHOWN` = 4, world.py:68)
   - each grudge: level word + its last 4 "event" facts + the minutes they were "angry" (world.py:173-183)
   - guilt: level word + the night + the last 4 guilt events
2. **Backstory** (world.py:515, 522). Can be trimmed.
3. **Pinned, never trimmed** (world.py:517-519): all of `sure` + the **last 3** `said_lines`.
4. **This morning's `memory`**, excluding entries from the current minute (world.py:516). Can be trimmed.
5. **Now** (world.py:497-512): room, who is here, the portions if in the kitchen, this turn's `so_far`, and `pattern()`, which covers only the current run of same-kind acts and the lines aimed at them or everyone since then (world.py:449-474).
6. **Options** (world.py:513).

**Trimming** (world.py:520-538):
- The budget is 1,400 *estimated* tokens (world.py:51), where the estimate is `len/3.6 + 1` (world.py:71-72) of SYSTEM + prompt.
- Order of cuts:
  1. the oldest memory while more than 8 remain
  2. then the oldest backstory while more than 4 remain
  3. then memory
  4. then backstory
- Any cut adds one marker, "- (earlier things, left out here)", under the *morning* heading (world.py:523-524), even when only backstory was cut.
- In cache/v5, 384 of 426 prompts carry the marker. 308 of 426 kept exactly 4 backstory lines (§S4, §S6).

**Past acts that never reach anyone's prompt later:**
- Others' routine "stay put" acts appear only in that turn's `so_far` (world.py:978-980).
- Another person's finished search reaches no one's prompt (see Q2).
- Triggers never reach a prompt (Q1).

## 8. Paths where a prompt could include something the person should not know

Each item is a path from world state into a prompt, with the check that gates it.

| # | path:line | what goes in | how it is gated |
|---|---|---|---|
| a | world.py:504-505 | exact `self.portions` whenever the person is in the kitchen | Only by room. It is read from the world, not from anything the person saw counted. |
| b | world.py:350-354, 291-301 | `aside_<x>` option names "take X aside to the <room>" | `empty_room()` reads every room's occupancy (`self.present`) and this turn's pending `self.moves` (world.py:296), including rooms the person is not in. |
| c | world.py:352 | `aside_<x>` offered only for people who have not acted this turn | Reads `self.acted`, which is also visible through `so_far`. |
| d | world.py:501-503 | other people's `activity` label and `feeling` | Same room. Feeling only if `outward` and recent (world.py:288-289). The label is read from their state, e.g. "sitting with X". |
| e | world.py:201-202, data.py:128-160 | backstory sentences | The event is included only if the person did/saw/heard it, but the sentence is the same omniscient summary for all. E.g. Leo "heard" "Mara cries in the night. Elena sits with her until it stops." (data.py:144-145). |
| f | world.py:264, data.py:167 | the opening "A can that should be on the shelf is not" | Everyone. False in miscount (Q4). |
| g | world.py:922-928 | the grudge fact "…and you had not" | Decided by the ground truth `self.culprit` (world.py:924). The text is the target's own knowledge. |
| h | world.py:321, 325, 328, 332, 356-361 | which options appear: `ask_who`, `deny`, `accuse_*`, `confess`, `search` | `knows_culprit`, `heard_question`, `confessed`, `self.culprit`. The option list itself carries this state. |
| i | world.py:434-435 with 748 | the culprit's prompt says "you have not settled on who took it" | Not a leak. It is a line that contradicts the culprit's own `sure` line (Q6). |

Checked in cache/v5, where no leak was found:
- Non-culprit prompts containing culprit-only text ("ate the can in the night", "You know where the can went"): 13 prompts, 17 lines. All are Mara's own words in a confession the reader heard: the `sure` line (world.py:908) or `so_far` (§S5).
- Voices through walls: 0 prompts, since nobody left the kitchen.

## 9. Per-pair relationship state

- **Resentment:** `grudges`, holder → {target: `Grudge`} (world.py:218, 143-165, 227-228).
  - Raised by:
    - a false accusation of the holder (world.py:922-928)
    - a confession after denying it to them (world.py:911-915)
    - a confession by someone who had accused them (world.py:916-919)
    - eating in front of them while they were hungry (world.py:1070-1075)
    - the model naming the target in `angry_at` (world.py:757-762)
  - Falls one step per 15 min when not named (world.py:54, 160-165, 763-765).
  - Used in:
    - the prompt text (world.py:436-441)
    - removing `reassure_<x>` at strength 3 (world.py:335-336)
    - inner moments (world.py:390-391)
- **Per-pair records of acts:** `denials_heard` and `accused_by` (world.py:219-220).
- **Trust:** NOT FOUND. **Affection or closeness toward a person:** NOT FOUND.
  - "closeness" appears only as a value word on the sheet (data.py:33, 42, 52).
  - Sitting together is an activity (world.py:1043-1057) and changes no pair state.
- **Suspicion** is one target per person (world.py:216), not a value per pair.

---

## Annotated prompt

Source: `cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed2.json`, key
`84fe22ea5b93b5c6fcc201c37c020e33a0e112210835aa1c96f4b87a360e7b9d`, Mara (the culprit), minute 54,
prompt_tokens 1374. The annotations are on the right after `⟵`. They are not part of the prompt.

```
 1 You are Mara, 17, the youngest, the daughter of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).   ⟵ world.py:489-490 (sheet data.py:45-54)
 2 How you address them: Elena "Mom"; Daniel "Daniel"; Leo "Leo".        ⟵ world.py:486, 491 (data.py:93-98)
 3 Who you are: Younger sister. Frightened and easy to read, …            ⟵ world.py:492 (data.py:47-49)
 4 Temperament: somewhat cautious, not dominant, very empathetic, …       ⟵ world.py:493, trait_words 95-106
 5 What matters to you: closeness, deciding for yourself, fairness.       ⟵ world.py:494
 6 Your body: hungry.                                                      ⟵ inside_lines world.py:426
 7 Since you last decided, you have grown hungrier.                        ⟵ world.py:427-428
 8 About the can: you have not settled on who took it.                     ⟵ world.py:434-435 (suspicion 0: own answers name "nobody"; self = nobody, world.py:748)
 9 Against Daniel (a lot): you were angry with Daniel at minutes 06, 12, 15 and 30.   ⟵ world.py:439-441, grudge_facts 173-183; "angry" events from world.py:757-762 (her own answers only)
10 On your conscience (a lot): you ate the can in the night, and nobody saw; Elena reassured you, at minute 06; Elena reassured you, at minute 09; Leo reassured you, at minute 12.   ⟵ world.py:442-445; events from add_guilt world.py:938-940 (reassured the culprit)
11 The house: The family has shut itself in the house. … Do not mention any other object or place.   ⟵ world.py:495 (data.py:79-80, 84-90)
12 What you remember from the days before:                                 ⟵ world.py:522
13 - Day 3: In the night Mara eats a can sitting on the kitchen floor. Nobody sees. (you did it)   ⟵ backstory world.py:201-202 (scenario night data.py:110-111); only Mara has it
14 - Day 4: Leo says maybe they should let someone else handle this one. (you saw it)             ⟵ backstory (data.py:149)
15 - Day 4: Daniel empties Mara's bag onto the bed while she is standing there. (you saw it)      ⟵ backstory (data.py:150-151)
16 - Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)   ⟵ backstory (data.py:152-153); Days 1-3 (9 lines) cut by world.py:533-534
17 What you are sure of this morning:                                      ⟵ world.py:517
18 - min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)   ⟵ world.py:263-264 (data.py:167)
19 - You know where the can went: you ate it yourself in the night, and nobody saw.   ⟵ world.py:265-266 (culprit only)
20 - min 09: you admitted aloud that you took the can, in front of Daniel, Elena, Leo.   ⟵ world.py:949-952 (own confession)
21 - min 24: Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; you had your part.   ⟵ world.py:1092-1095 (saw it)
22 Your own last words this morning:                                       ⟵ world.py:518-519 (last 3 said_lines)
23 - min 09, you admitted taking it: "I can't lie anymore, I was just so hungry in the night and I ate it."   ⟵ said_lines world.py:946
24 - min 12, you reassured everyone: "I'm sorry, I really didn't mean to cause any trouble for anyone."        ⟵ world.py:946
25 - min 30, you reassured everyone: "I really am sorry, I'll never do anything like that again."             ⟵ world.py:946
26 What else happened this morning, most recent last:                      ⟵ world.py:523
27 - (earlier things, left out here)                                       ⟵ world.py:524 (cut = True, world.py:530)
28 - min 30: Daniel accuses you of taking it: "You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open."   ⟵ memory via perceive world.py:897-899, line_text 824-840 ("you" = listener is target, 825)
29 - min 30: you reassured everyone: "I really am sorry, I'll never do anything like that again.". You felt guilty.   ⟵ own memory world.py:945 (+ feel, world.py:853)
30 - min 30: Elena reassures everyone: "Let us stop arguing now, we have shared the food and we must hold together."   ⟵ memory via world.py:897-899
31 Now, minute 54, you are in the kitchen.                                 ⟵ world.py:497
32 - Daniel is here, staying put.                                          ⟵ world.py:501-503 (activity label set at world.py:977; no "looks" because the feeling is not shown, world.py:288-289)
33 - Elena is here, staying put.                                           ⟵ same
34 - Leo is here, staying put.                                             ⟵ same
35 - 0 portions on the shelf.                                              ⟵ world.py:504-505 (self.portions, world state)
36 Said and done in the kitchen this turn, before you, in order:           ⟵ world.py:506-508
37 1. Daniel stays put and says nothing.                                   ⟵ so_far, world.py:978
38 2. Leo stays put and says nothing.                                      ⟵ so_far, world.py:978
39 What you have been doing: you have stayed put and said nothing, 7 turns in a row.   ⟵ pattern world.py:452-456 (KIND_DONE 56-64)
40 In that time nobody has said anything to you or to everyone.            ⟵ world.py:461-463 (from Mara.heard)
41 Your options:                                                           ⟵ world.py:513, options_for 315-373
42 - silent: stay put and say nothing                                      ⟵ world.py:319
43 - reassure_elena: (speech) reassure Elena                               ⟵ world.py:334-338
44 - reassure_leo: (speech) reassure Leo                                   ⟵ world.py:334-338 (no reassure_daniel: grudge 3/3, world.py:335-336)
45 - reassure_all: (speech) reassure everyone here                         ⟵ world.py:339-340
46 - say_other: (speech) say something else                                ⟵ world.py:341
47 - sit_daniel: sit with Daniel                                           ⟵ world.py:342-347
48 - sit_elena: sit with Elena                                             ⟵ same
49 - sit_leo: sit with Leo                                                 ⟵ same
50 - aside_elena: take Elena aside to the back room                        ⟵ world.py:350-354 (empty_room 291-301; Daniel, Leo already acted, world.py:352)
51 - go_brothers_room: go to the brothers room                             ⟵ world.py:362-364
52 - go_back_room: go to the back room                                     ⟵ same
53 - go_bathroom: go to the bathroom                                       ⟵ same
```

Options that are absent, and why:
- `ask_who`: `knows_culprit` (world.py:321)
- `deny` and `accuse_*`: `confessed` (world.py:325, 328)
- `confess`: already confessed (world.py:332)
- `search`: settled (world.py:356)
- `eat` and `share`: 0 portions (world.py:365)

The line SYSTEM (world.py:27-39) is sent as the system instruction, not in this text.

Cached answer:

```
{"option": "silent", "say": null, "feeling": "ashamed",
 "reason": "I have nothing left to say after everything that happened, so I will just stay quiet.",
 "suspects": "nobody", "angry_at": "Daniel"}
```

This answer feeds back as follows:
- `suspects` "nobody" → `suspicion.report(None)` (world.py:749-751)
- `angry_at` "Daniel" → another "angry" grudge event against Daniel (world.py:757-762)
- `silent` in model mode → "you stayed where you were…" in Mara's memory (world.py:979-980)

Lines 28-30 are the newest memory entries even at minute 54: nothing after minute 30 was remembered, because every later act in the room was a silent stay-put (world.py:976-980).

---

## Search commands and output

Run from `Prototypes/llm-morning/` in Git Bash.

**§S1: writes to knowledge fields**

```
$ grep -n -E "sure\.append|memory\.append|said_lines\.append|heard\.append|self\.perceive\(|knows_culprit|denials_heard|accused_by|heard_question" world.py
212:        self.knows_culprit = culprit if pid == culprit else None
213:        self.heard_question = False
219:        self.denials_heard = {}     # person -> minute they last heard that person deny it
220:        self.accused_by = {}        # person -> minute that person last accused them
264:            p.sure.append(f"min 00: {data.OPENING} (you {how})")
266:                p.sure.append("You know where the can went: you ate it yourself in the night, and nobody saw.")
321:            if not p.knows_culprit:
325:            if p.heard_question and not p.confessed:
328:                if p.confessed or (p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit):
356:        settled = p.confessed or (p.knows_culprit and p.knows_culprit != p.id)
708:                    q.memory.append((minute, line + "."))
718:                self.perceive(q, minute, text + ".", trigger=(text, True))
820:            q.memory.append((minute, text))
899:                self.perceive(q, minute, heard, trigger=(heard, new))
900:                q.heard.append({"seq": self.seq, "who": p.id, "kind": spoken_kind,
905:                    q.heard_question = True
907:                    q.knows_culprit = p.id
908:                    q.sure.append(f"min {minute:02d}: {p.name} admitted taking the can: \"{words}\" "
911:                    if p.id in q.denials_heard:
914:                                        f"denying it to you at minute {q.denials_heard[p.id]:02d}",
916:                    if p.id in q.accused_by:
918:                                        f"{p.name} had accused you of it at minute {q.accused_by[p.id]:02d}",
921:                    q.denials_heard[p.id] = minute
923:                    q.accused_by[p.id] = minute
945:            p.memory.append((minute, f"you {mine}: \"{words}\".{feel}"))
946:            p.said_lines.append(f"min {minute:02d}, you {mine}: \"{words}\"")
948:                p.heard_question = True
951:                p.sure.append(f"min {minute:02d}: you admitted aloud that you took the can"
968:                    self.perceive(q, minute, trig + ".", trigger=(trig, True), remember=False)
980:                p.memory.append((minute, f"you stayed where you were and said nothing.{feel}"))
989:                    self.perceive(q, minute, f"{p.name} starts going through the {data.ROOMS[room]}.")
990:                p.memory.append((minute, f"you started searching the {data.ROOMS[room]}.{feel}"))
996:                p.sure.append(f"min {minute:02d}: you finished searching the {data.ROOMS[room]}: "
1006:                self.perceive(q, minute, f"{p.name} leaves for the {data.ROOMS[to]}.")
1008:            p.memory.append((minute, f"you went to the {data.ROOMS[to]}.{feel}"))
1015:                    self.perceive(q, minute, f"{p.name} asks {target.name} to come aside to the {data.ROOMS[to]}.")
1016:            p.memory.append((minute, f"you asked {target.name} to come aside to the {data.ROOMS[to]}.{feel}"))
1024:                    self.perceive(q, minute, f"{partner.name} and {p.name} leave for the {data.ROOMS[to]} together.")
1032:            p.memory.append((minute, f"you went with {partner.name} to the {data.ROOMS[to]}.{feel}"))
1033:            partner.memory.append((minute, f"{p.name} came with you to the {data.ROOMS[to]}."))
1039:                self.perceive(q, minute, text + ".", trigger=(text, False) if q is partner else None)
1041:            p.memory.append((minute, f"you refused to go aside with {partner.name}.{feel}"))
1050:                        self.perceive(q, minute, f"{p.name} comes and sits with you.",
1053:                        self.perceive(q, minute, f"{p.name} sits with {target.name}.")
1054:                p.memory.append((minute, f"you sat with {target.name}.{feel}"))
1061:                p.memory.append((minute, "you reached for the shelf; it was empty."))
1069:                q.sure.append(f"min {minute:02d}: {p.name} ate one of the portions (you saw it).")
1077:            p.sure.append(f"min {minute:02d}: you ate one of the portions. {self.portions} left.")
1095:                q.sure.append(f"min {minute:02d}: {trig}; you had your part.")
1097:            p.sure.append(f"min {minute:02d}: you shared out the last {n} portions between {names}.")
```

**§S2: whether triggers, reasons, suspects or feelings reach a prompt**

`prompt_for` spans world.py:483-540, and the only hit inside it is 502.

```
$ grep -n -E "triggers|\breason\b|\"suspects\"|suspects_|feeling" world.py
6:(or just took someone aside) goes first, then whoever shows the strongest feeling, then
33:    "doing it, or null. `feeling` names what they feel right now in one or two words. "
34:    "`reason` is their reason in one sentence, as they would think it. `suspects` is who they "
37:    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
38:    '"suspects": "<name or nobody>", "angry_at": "<name or nobody>"}'
75:def strength(feeling):
76:    f = (feeling or "").lower()
83:def outward(feeling):
84:    return strength(feeling) > 0
200:        self.feeling, self.feeling_until = None, -1
206:        self.triggers = []          # (text, is it new) social things since they last acted
267:            p.triggers.append(("the count came up short in front of everyone", True))
289:        return outward(q.feeling) and q.feeling_until >= t
502:            look = f" {q.name} looks {q.feeling}." if self.shown(q, t) else ""
554:        for field in ("option", "feeling", "reason"):
560:        for field in ("suspects", "angry_at"):
578:        return {"option": opt.id, "say": say, "feeling": " ".join(ans["feeling"].split()).lower(),
579:                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None
604:    def social_triggers(self, p, t):
607:        found = list(dict.fromkeys(text for text, new in p.triggers if new or talking))
611:                    found.append(f"{q.name} looks {q.feeling}")
620:            return (0 if first else 1, -(a["seq"] if a else 0), -strength(q.feeling) * self.shown(q, t), draw[pid])
631:        mine = strength(q.feeling) * self.shown(q, t)
632:        if mine > max(strength(o.feeling) * self.shown(o, t) for o in rest):
633:            return pid, f"shows the strongest feeling here ({q.feeling})"
662:                     "inner": d.get("inner_families"), "suspects": d.get("suspects"),
710:                    q.triggers.append((line, True))
749:        suspect = named("suspects")
751:        d["suspects_result"] = p.suspicion.report(suspect, minute)
756:        d["suspects_now"] = p.suspicion.short("suspicion")
776:        triggers = self.social_triggers(p, t)
777:        p.triggers = []
779:        d = {"person": p.id, "triggers": triggers, "offered": len(opts),
781:        if not triggers:
788:        if triggers or d.get("inner_kinds"):
805:        triggers = [asked] + [text for text, new in q.triggers if text != asked]
806:        q.triggers = []
807:        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
822:            q.triggers.append(trigger)
853:        feel = f" You felt {d['feeling']}." if d.get("feeling") else ""
855:            p.feeling = d["feeling"]
856:            p.feeling_until = t + FEELING_SHOWS_FOR_TURNS if outward(d["feeling"]) else -1
```

**§S3: belief, trust and truth vocabulary, and ground-truth reads**

```
$ grep -n -i -E "believ|trust|confiden|certain|source|\blie\b|\blies\b|lying|false|truth|true_|knows_|thinks|opinion" world.py data.py gemini.py morning.py
world.py:35:    "now believe took the can, and `angry_at` is who they are angry with right now: each is "
world.py:158:        return False
world.py:165:        return False
world.py:187:    def __init__(self, id, label, speech=False, **act):
world.py:212:        self.knows_culprit = culprit if pid == culprit else None
world.py:213:        self.heard_question = False
world.py:214:        self.confessed = False
world.py:269:        self.started("kitchen", 0, "the count came up short", False)
world.py:321:            if not p.knows_culprit:
world.py:328:                if p.confessed or (p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit):
world.py:356:        settled = p.confessed or (p.knows_culprit and p.knows_culprit != p.id)
world.py:520:        cut = False
world.py:575:        dropped = False
world.py:720:                self.arrivals.append((to, p.name, self.moved_by_inner.get(p.id, False)))
world.py:907:                    q.knows_culprit = p.id
world.py:924:                    if q.id != self.culprit:        # a false accusation
world.py:928:                                        f"{p.name} accused {q.name} falsely", record)
world.py:968:                    self.perceive(q, minute, trig + ".", trigger=(trig, True), remember=False)
world.py:1025:            by_inner = self.moved_by_inner.get(partner.id, False)   # how the asking came about
world.py:1039:                self.perceive(q, minute, text + ".", trigger=(text, False) if q is partner else None)
world.py:1040:            partner.addressed = {"seq": self.seq, "who": p.id, "accused": False}
world.py:1051:                                      trigger=(f"{p.name} came to sit with you", False))
data.py:20:                "Proud, poor at reading a room, genuinely protective. Believes responsibility "
data.py:29:        "note": "Mother. Reads everyone, says little, holds it in. Will lie to keep the family "
gemini.py:208:            json.dump(self.entries, f, ensure_ascii=False, indent=1)
gemini.py:215:    def __init__(self, cache, model_name, seed, client=None, replay=False, max_calls=None):
morning.py:34:def run(seed, replay=False, fake=False, config_path=None, runs_dir=None, cache_dir=None,
morning.py:35:        client=None, quiet=False, scenario=data.DEFAULT_SCENARIO, model_key=None, out="v5"):
morning.py:122:        json.dump(morning.transcript, f, ensure_ascii=False, indent=1)

$ grep -n -E "self\.culprit|data\.culprit|self\.portions|self\.present\[|self\.moves" world.py
194:        culprit = data.culprit(scenario)
243:        self.culprit = data.culprit(scenario)       # who took the can, or None
245:        self.portions = data.PORTIONS
257:        self.moves = None           # during a turn: (person, room, partner) to move at its end
260:        self.transcript = {"seed": seed, "scenario": scenario, "culprit": self.culprit, "turns": []}
265:            if p.id == self.culprit:
278:            ids = self.present[p.room]
284:        count = len(self.present[room]) if self.present is not None else \
296:                return bool(self.present[r]) or any(to == r for _, to, _ in self.moves)
332:            if p.id == self.culprit and not p.confessed:
365:        if p.room == "kitchen" and self.portions > 0:
412:        culprit = self.people[self.culprit]
505:            now.append(f"- {self.portions} portion{'s' if self.portions != 1 else ''} on the shelf.")
647:        self.acted, self.moves = set(), []
669:            remaining = list(self.present[room])
696:        for p, to, partner in self.moves:
711:        for p, to, partner in self.moves:
725:        self.present, self.so_far, self.acted, self.moves = None, None, None, None
729:        record["portions"] = self.portions
852:        culprit = self.people[self.culprit] if self.culprit else None
924:                    if q.id != self.culprit:        # a false accusation
972:            self.present[room].remove(person.id)
973:            self.moves.append((person, to, with_whom))
1028:                self.present[room].remove(person.id)
1029:                self.moves.append((person, to, other.id))
1060:            if self.portions <= 0:
1064:            self.portions -= 1
1077:            p.sure.append(f"min {minute:02d}: you ate one of the portions. {self.portions} left.")
1079:            return f"ate a portion; {self.portions} left."
1082:            if self.portions <= 0:
1086:            each = self.portions / len(eaters)
1091:            n, self.portions = self.portions, 0
```

**§S4-S6: checks over cache/v5 prompts and runs/v5 transcripts**

These used read-only Python over the JSON files, which imports nothing from the prototype. The checks were:
- For each `cache/v5/*.json` entry, take the speaker from `^You are (\w+)` and the minute from `Now, minute (\d+)`, then test the prompt text with the regexes below.
- For each `runs/v5/*.transcript.json`, count acts with `moved_to` set and the occupied rooms per turn.

```
prompts: 426
non-culprit prompt with 'ate the can in the night' or 'You know where the can went': 13
    (17 matching lines; e.g. Leo, min 27: '- min 27: Mara admitted taking the can: "I took it! I ate
     the can in the night, okay?" (you heard it)' and '1. Mara admits taking it, to everyone: "…"')
miscount prompt with the opening 'A can that should be on the shelf is not': 219
prompt with someone else's 'finishes going through' / 'finished searching' (not 'you finished'): 0
prompt containing 'you finished searching': 126
prompt with '(earlier things, left out here)': 384
prompt with 'looks ' (a shown feeling): 115
prompt with 'Voices from the': 0
rooms in 'Now' line: {'kitchen': 426}
backstory lines kept per prompt: {1: 1, 2: 7, 3: 26, 4: 308, 5: 11, 6: 12, 7: 3, 8: 8, 9: 3, 10: 22, 11: 6, 12: 19}
culprit prompts: 53
culprit prompts saying 'not settled': 53
prompts after hearing a confession: 60
  ... of which 'not settled': 9
transcripts (all 11 in runs/v5): moves: 0; rooms occupied: {'kitchen': 30}; final: all four in the kitchen
```

The quoted prompt was printed with a filter on `startswith("You are Mara")` and `"Now, minute 54,"` in
`cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed2.json`.

---

## NOT FOUND

- Beliefs about other people's beliefs, knowledge or suspicions (Q5).
- Trust between two people. Affection or closeness toward a person as state (Q9).
- A structured claim extracted from spoken words. The act kind comes from the option id and the words are never parsed (Q3).
- A truth or falsity flag on any spoken line, and any record of a culprit's denial as a lie (Q4).
- A per-fact source or confidence field. Sources exist only inside text strings (Q6).
- Any update to `suspicion` from evidence (an accusation heard, a confession heard, a search). It changes only from the person's own answer (Q6).
- Others' "found nothing" search results in anyone's memory or prompt (Q2, Q7).
- Any "tell" act that passes a specific fact from one person to another other than a confession (Q2).
- In the saved runs: any movement out of the kitchen, any voices through walls, and any aside. These code paths are not exercised by cache/v5 or runs/v5.
