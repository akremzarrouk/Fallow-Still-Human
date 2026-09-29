# Kitchen audit: why people almost never leave the kitchen

Investigation, read-only. Date: 2026-09-29. Code read: `world.py`, `data.py`, `talk.py`,
`morning.py`, `gemini.py` (top level), plus `v5/` and `v6/` for diffs. Runs read: `runs/v5`,
`runs/v6`, `runs/v8`. Caches read: `cache/v6`, `cache/v8`. No API calls were made.

Step 0 was done first: `runs/v8/`, `cache/v8/` and `reports/witness_v8.md` were committed as
`c593665`. Nothing else was written except this file. The three untracked
`runs/v6/daniel_ate_it-seed*.replay.md` files were left alone.

## Which code made which runs

- The `runs/v6` runs were made by `v6/`. Diffing `v6/world.py` against `world.py` shows only
  the `can_note` / "About the can" change (`world.py:213`, `world.py:433-444`). `talk.py` is
  identical. Nothing that offers, applies or orders moves changed. See command C3.
- There is no `v8/` directory (NOT FOUND). The `runs/v8` runs are the current top-level
  code: an in-memory replay of each v8 run from its cache, with no API client, gives a
  transcript identical to the saved one (command C7, `"transcript_identical": true` for all
  9 runs).
- The v5→v6 diff also has no movement changes (command C4).

So every `world.py:N` citation below applies to v6 and v8 alike.

---

## 1. Every option that moves a person

Everyone starts in the kitchen: `self.room = "kitchen"` (`world.py:198`). `p.room` is
assigned in exactly two places: `world.py:198` (start) and `world.py:706` (end-of-turn
moves) (command C8).

### `go_<room>`: `go_kitchen`, `go_brothers_room`, `go_back_room`, `go_bathroom`

- **When offered:** for every room except the current one, with no condition
  (`world.py:364-366`). It is offered with or without company, with or without a
  conversation, and at any hunger level.
- **Never filtered:** the repeat filter removes only speech kinds (`world.py:371-374`), and
  `go` is not in `SPEECH` (`talk.py:8`).
- **When not offered:** never, except for the room the person is already in. It is also
  absent from the go-aside answer prompt, which has only two options (`world.py:810-812`).
- **What it does** (`world.py:1013-1020`):
  - It adds "`<name>` leaves for the `<room>`." to the room's this-turn list.
  - Everyone in the room gets the same line as a memory, but with no trigger
    (`world.py:1016-1017`; `perceive` only adds a trigger when one is passed,
    `world.py:827-831`).
  - `leave()` sets the activity to "leaving for the …", removes the person from the room's
    remaining actors and queues the move (`world.py:981-985`).
  - The mover remembers "you went to the `<room>`." (`world.py:1019`).
  - At the end of the turn, `p.room = to` and the activity becomes "just come in"
    (`world.py:705-707`).
  - Anyone already in the destination gets the trigger "`<name>` comes into the `<room>`"
    (`world.py:720-727`). At the start of the next turn, the arrival counts as a new thing
    and starts that room's conversation (`world.py:728-729`, `world.py:649-650`).
  - If the destination is empty, nobody gets a trigger and no conversation starts.
  - Leaving is not a "new thing" in the room left behind: `apply` calls neither
    `newness.line` nor `fact()` for `go` (`world.py:1013-1020`).

### `aside_<person>` (the asker) with `accept_aside` / `refuse_aside` (the one asked)

**When `aside_<person>` is offered** (`world.py:350-356`), all three must hold:
- someone else is in the room (`world.py:322`);
- `empty_room(p)` finds a room nobody is in at turn start and nobody is moving to this turn
  (`world.py:293-303`);
- the person to be taken aside has not yet acted this turn (`world.py:354`).

**Destination order** (`world.py:300-302`): the asker's own room first, then the other
private room, then the kitchen, then the bathroom.

**When `aside_<person>` is not offered:**
- when the person is alone;
- when every other room is taken;
- for anyone who has already acted this turn.

The last to act in a room therefore never gets an aside option (example: Leo's minute-63
prompt in item 6).

**What `aside_<person>` does:**
- The asker does not move by themselves. The rules add "`<A>` asks `<B>` to come aside to
  the `<room>`." to the room and to the memory of everyone except B (`world.py:1021-1029`).
- The turn loop then takes B out of the remaining actors and asks the model for B's answer
  straight away (`world.py:689-701`).

**`accept_aside` / `refuse_aside`:**
- These are offered only in `decide_aside` (`world.py:808-824`), which is always a model
  decision. An invalid answer falls back to `refuse_aside` (`world.py:820`).
- `accept_aside` (`world.py:1030-1045`):
  - Both people are removed from the room and both moves are queued.
  - `partner.aside_lead` is set, so the asker acts first next turn (`world.py:628`,
    `world.py:636-637`).
  - At the end of the turn, each gets the trigger "You and `<other>` are in the `<room>`,
    away from the others" (`world.py:720-725`).
- `refuse_aside` (`world.py:1046-1053`): nobody moves. The asker is marked `addressed`, so
  they act first next turn (`world.py:1051`).

### Other options that move a person

NOT FOUND. `silent`, the speech options, `sit_*`, `search`, `keep_searching`, `eat` and
`share` never change `p.room`. `routine()` (`world.py:377-384`) returns only
`keep_searching`, `sit_<same person>` or `silent`.

---

## 2. How a conversation affects who is asked and which options are shown

**What a conversation is:**
- A room is "talking" when its conversation is active and at least two people are in it
  (`world.py:285-288`).
- A conversation starts on a new thing (`talk.py:81-89`). New things are:
  - a first question, a first accusation, a denial of a new accusation, or a confession
    (`talk.py:45-66`);
  - finishing a search, eating or sharing (`fact()`, `world.py:973-979`);
  - someone arriving (`world.py:649-650`).
- It ends after `QUIET_TURNS = 2` full turns with nothing new, or when fewer than two people
  are left (`talk.py:91-105`, `world.py:52`).

**Who is asked** (`world.py:782-806`):
- The model is asked only if the person has a social trigger (`world.py:785`, `world.py:797`)
  or has an inner moment (`world.py:790-796`).
- An inner moment needs a level that rose since they last decided (`world.py:387-394`) and
  at least `INNER_EVERY = 9` minutes since their last one (`world.py:53`, `world.py:792`).
- Everyone else gets `routine()`: `silent`, `keep_searching` or `sit_<same>`
  (`world.py:377-384`, `world.py:801-802`).
- **The conversation's effect:** while the room is talking, old triggers still count, and so
  does any feeling showing on someone else's face (`world.py:613-621`). When it is not
  talking, only new triggers count (`world.py:616`).

**Order within a turn** (`world.py:623-643`):
1. whoever was just spoken to, or took someone aside;
2. then whoever shows the strongest feeling;
3. then a draw from the seed.

Each person sees what was said and done before them this turn (`world.py:515-520`).

**Which options are shown:**
- `options_for` (`world.py:317-375`) never reads the conversation state. There is no
  `convos` or `talking` in it (command C8: "none in world.py:317-375").
- What does change the list:
  - whether anyone else is here (`world.py:322`): all speech, `sit_*`, `aside_*` and `share`
    options need company;
  - what the person knows or has admitted (`world.py:323-335`, `world.py:358`);
  - a grudge at 3, which removes `reassure_<person>` (`world.py:337-338`);
  - the acting order, for `aside_*` (`world.py:354`);
  - searching state and rooms already searched (`world.py:359-363`);
  - being in the kitchen with portions left, for `eat`/`share` (`world.py:367-370`);
  - the repeat filter for speech (`world.py:371-374`).
- Alone, the list is `silent`, `search`/`keep_searching` (if the room is unsearched), the
  three `go_*`, and `eat` (kitchen with portions only) (`world.py:321`, `world.py:358-370`).
  The prompt then says "- Nobody else is here." (`world.py:508-509`).

**Through walls:** people in other rooms remember "Voices from the `<room>`." A voice is a
trigger only when the line was new (`world.py:711-719`). The bathroom is soundproof both
ways (`data.py:73`).

**In the runs:** the kitchen conversation's start and end minutes, and the model and routine
decision counts, are in command C10:

| Run | Model | Routine | Routine choices |
|---|---|---|---|
| v6/daniel_ate_it-seed1 | 45 | 75 | 74 silent, 1 keep_searching |
| v6/daniel_ate_it-seed2 | 66 | 54 | 53 silent, 1 keep_searching |
| v6/daniel_ate_it-seed3 | 25 | 95 | 93 silent, 2 keep_searching |
| v6/daniel_ate_it_leo_heard-seed1 | 44 | 76 | 73 silent, 3 keep_searching |
| v6/daniel_ate_it_leo_heard-seed2 | 43 | 77 | 76 silent, 1 keep_searching |
| v6/daniel_ate_it_leo_heard-seed3 | 29 | 91 | 89 silent, 2 keep_searching |
| v8/daniel_ate_it_leo_heard-seed1 | 56 | 64 | 61 silent, 3 keep_searching |
| v8/daniel_ate_it_leo_heard-seed2 | 67 | 53 | 53 silent |
| v8/daniel_ate_it_leo_heard-seed3 | 39 | 81 | 79 silent, 2 keep_searching |

---

## 3. What in a prompt could give a reason to leave, or to stay

"In prompts" gives how many of the 654 v6+v8 cache prompts contain the text (command C11).

| Item | Where | What the prompt says | In prompts |
|---|---|---|---|
| Hunger | `world.py:428`, `world.py:87-92`, `world.py:66` | "Your body: `<a little hungry / hungry / very hungry / starving>`." | 654 / 654 |
| Hunger rose | `world.py:429-430` | "Since you last decided, you have grown hungrier." | 98 / 654 |
| Where the food is | `data.py:64`, `data.py:79-80` | "kitchen (the food is kept here)" | 654 / 654 |
| Food on the shelf | `world.py:513-514` (kitchen only) | "- `<n>` portions on the shelf." | 654 / 654; "0 portions" in 107 |
| Eat / share | `world.py:367-370` | offered only in the kitchen, only while portions > 0 | n/a |
| Other rooms' contents | `data.py:84-90` | "the brothers room, with Daniel's and Leo's beds; the back room, with Elena's and Mara's beds and Mara's bag; the bathroom" | 654 / 654 |
| Room notes | `data.py:63-68` | "brothers room (Daniel and Leo's room); back room (Elena and Mara's room); bathroom (nothing is heard in or out of it)" | 654 / 654 |
| Privacy | `data.py:67` | "nothing is heard in or out of it" (bathroom); the aside label "take `<name>` aside to the `<room>`" (`world.py:355`) | 654 / 654; aside label 468 / 654 |
| Voices carry between the other rooms | n/a | NOT FOUND in any prompt text; only "Voices from the …" as a memory (`world.py:715-717`) | 0 / 654 |
| Search elsewhere | `world.py:361-363` | "search the `<current room>` for the can": only the current room, and gone once searched (`p.searched`). No option or text says other rooms can be searched. | n/a |
| Where the can went | `data.py:105`, `data.py:124` | Daniel's backstory: "eats a can standing at the counter"; Leo's witness note: "heard someone open a can in the kitchen" | n/a |
| Doing the same thing | `world.py:458-483` | "What you have been doing: you have stayed put and said nothing, `<n>` turns in a row." | "stayed put and said nothing," in 272 / 654 |
| Persona text about withdrawing | `data.py:38-39` (Leo) | "Annoyance shows as withdrawal and dry correction, not volume." | Leo's prompts |
| Persona values | `data.py:24,33,42,52` | "closeness" (Elena, Leo, Mara), "keeping the family safe" (Daniel, Elena, Leo), "deciding for yourself" (Leo, Mara) | all |
| Tiredness | n/a | NOT FOUND. The only "tired" in the code is the fake model's feeling list (`gemini.py:165`) | 0 |
| Chores or tasks | n/a | NOT FOUND. "The water has stopped" (`data.py:79`) comes with no task | 0 |
| Outside | `data.py:88-89` | "Outside, and not to be gone to: the street and the neighbour's house." | 654 / 654 |
| Company and what just happened | `world.py:510-512`, `world.py:515-520` | "- `<name>` is here, `<activity>`." and "Said and done in the kitchen this turn, before you, in order:" | n/a |
| Option order | `world.py:321`, `world.py:364-366` | `silent` is always listed first. The `go_*` options come after all speech, sit, aside and search options (15th–17th of 17 in Leo's minute-63 prompt, item 6) | n/a |

---

## 4. Counts from the v6 and v8 caches

"Move option" means `go_*`, `aside_*` or `accept_aside` in the prompt's option list.
"Chose" means the answer's `option` field.

### 4a. Only the prompts each recorded run used (in-memory replay, command C7)

| run | person | prompts | offered any move | offered go | offered aside | offered accept_aside | chose go | chose aside | chose accept_aside |
|---|---|---|---|---|---|---|---|---|---|
| v6/daniel_ate_it-seed1 | Daniel | 12 | 12 | 12 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Elena | 12 | 12 | 12 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Leo | 10 | 10 | 10 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Mara | 11 | 11 | 11 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | **all** | **45** | **45** | **45** | **33** | **0** | **0** | **0** | **0** |
| v6/daniel_ate_it-seed2 | Daniel | 19 | 19 | 19 | 15 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Elena | 15 | 15 | 15 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Leo | 15 | 15 | 15 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Mara | 17 | 17 | 17 | 16 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | **all** | **66** | **66** | **66** | **49** | **0** | **0** | **0** | **0** |
| v6/daniel_ate_it-seed3 | Daniel | 7 | 7 | 7 | 5 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Elena | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Leo | 6 | 6 | 6 | 2 | 0 | 1 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Mara | 6 | 6 | 6 | 4 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | **all** | **25** | **25** | **25** | **17** | **0** | **1** | **0** | **0** |
| v6/daniel_ate_it_leo_heard-seed1 | Daniel | 11 | 11 | 11 | 7 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Elena | 11 | 11 | 11 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Leo | 13 | 13 | 13 | 10 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Mara | 9 | 9 | 9 | 5 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | **all** | **44** | **44** | **44** | **31** | **0** | **0** | **0** | **0** |
| v6/daniel_ate_it_leo_heard-seed2 | Daniel | 11 | 11 | 11 | 6 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Elena | 10 | 10 | 10 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Leo | 11 | 11 | 11 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Mara | 11 | 11 | 11 | 10 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | **all** | **43** | **43** | **43** | **32** | **0** | **0** | **0** | **0** |
| v6/daniel_ate_it_leo_heard-seed3 | Daniel | 7 | 7 | 7 | 4 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Elena | 8 | 8 | 8 | 7 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Leo | 7 | 7 | 7 | 3 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Mara | 7 | 7 | 7 | 6 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | **all** | **29** | **29** | **29** | **20** | **0** | **0** | **0** | **0** |
| v8/daniel_ate_it_leo_heard-seed1 | Daniel | 15 | 15 | 15 | 10 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Elena | 12 | 12 | 12 | 9 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Leo | 15 | 15 | 15 | 12 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Mara | 14 | 14 | 14 | 11 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | **all** | **56** | **56** | **56** | **42** | **0** | **0** | **0** | **0** |
| v8/daniel_ate_it_leo_heard-seed2 | Daniel | 17 | 17 | 17 | 14 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Elena | 16 | 16 | 16 | 10 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Leo | 17 | 17 | 17 | 14 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Mara | 17 | 17 | 17 | 12 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | **all** | **67** | **67** | **67** | **50** | **0** | **0** | **0** | **0** |
| v8/daniel_ate_it_leo_heard-seed3 | Daniel | 11 | 11 | 11 | 7 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Elena | 11 | 11 | 11 | 11 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Leo | 8 | 8 | 8 | 2 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Mara | 9 | 9 | 9 | 5 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | **all** | **39** | **39** | **39** | **25** | **0** | **0** | **0** | **0** |
| **9 runs** | **all** | **414** | **414** | **414** | **299** | **0** | **1** | **0** | **0** |

The options the model chose in those 414 answers (command C12):

| Option | Count |
|---|---|
| silent | 121 |
| deny | 78 |
| reassure_all | 72 |
| ask_who | 65 |
| search | 28 |
| accuse_daniel | 19 |
| accuse_mara | 7 |
| accuse_leo | 7 |
| share | 6 |
| keep_searching | 5 |
| say_other | 2 |
| reassure_elena | 2 |
| reassure_mara | 1 |
| go_brothers_room | 1 |

### 4b. Every entry in each cache file (command C6)

The witness caches hold more entries than their runs used:

| Cache file | Entries | Used by the run |
|---|---|---|
| v6 witness seed 1 | 83 | 44 |
| v6 witness seed 2 | 106 | 43 |
| v6 witness seed 3 | 46 | 29 |
| v8 seed 1 | 97 | 56 |
| v8 seed 2 | 130 | 67 |
| v8 seed 3 | 56 | 39 |

Every v6 witness cache and every v8 cache contains every entry of the v6 baseline cache for
the same seed (command C9).

| run | person | prompts | offered any move | offered go | offered aside | offered accept_aside | chose go | chose aside | chose accept_aside |
|---|---|---|---|---|---|---|---|---|---|
| v6/daniel_ate_it-seed1 | all | 45 | 45 | 45 | 33 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | all | 66 | 66 | 66 | 49 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | all | 25 | 25 | 25 | 17 | 0 | 1 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | all | 83 | 83 | 83 | 60 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | all | 106 | 106 | 106 | 78 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | all | 46 | 46 | 46 | 29 | 0 | 1 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | all | 97 | 97 | 97 | 72 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | all | 130 | 130 | 130 | 96 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | all | 56 | 56 | 56 | 34 | 0 | 1 | 0 | 0 |
| **all caches** | all | **654** | **654** | **654** | **468** | **0** | **3** | **0** | **0** |

The per-person split is in command C6's output. All three `go` answers are the same prompt
and answer: Leo, minute 63, v6 baseline seed 3. The copies in the v6 witness seed 3 and v8
seed 3 caches are not used by those runs (command C13).

### 4c. Moves in the transcripts, v5 included (command C5)

- There are 20 transcripts: 11 in v5, 6 in v6 and 3 in v8.
- There is 1 move in total: v6 `daniel_ate_it` seed 3, minute 63, Leo, `go_brothers_room`,
  by the model.
- There are 0 `aside_*`, 0 `accept_aside` and 0 `refuse_aside` acts. Every `meta.json` has
  `"private_talks": 0` (command C14).
- Every run ends with all four in the kitchen, except v6 `daniel_ate_it` seed 3 (Leo in the
  brothers room).

---

## 5. What the system instruction and the prompts say about moving or rooms

**System instruction:** `world.py:27-39`, sent as `system_instruction` (`gemini.py:96`),
quoted in full:

> You decide what one person in a family does in the next three minutes. You get who they
> are, what they remember, what they see now, and the options open to them. They know only
> what is in their memory. Choose exactly one option id from the list. If the option is
> marked (speech), `say` must hold the exact words they say, in their own voice, one or two
> short sentences. For any other option `say` is a short line they say while doing it, or
> null. `feeling` names what they feel right now in one or two words. `reason` is their
> reason in one sentence, as they would think it. `suspects` is who they now believe took
> the can, and `angry_at` is who they are angry with right now: each is one of "Daniel",
> "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: {…}

None of these words appear in it: "room", "move", "leave", "go ", "go_", "private", "alone",
"aside", "kitchen", "where" or "place" (command C15). It says nothing about moving or rooms.

**The prompt**, as quoted from Leo's minute-63 prompt (item 6):

- House line (`data.py:79-80`, `world.py:504`): "The family has shut itself in the house.
  The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room
  (Daniel and Leo's room); back room (Elena and Mara's room); bathroom (nothing is heard in
  or out of it)."
- Things line (`data.py:84-90`): "The only places and things there are: the kitchen, with
  the pantry shelf where the food is kept, the counter and the dry taps; the brothers room,
  with Daniel's and Leo's beds; the back room, with Elena's and Mara's beds and Mara's bag;
  the bathroom; the doors between the rooms; the front door and the front windows, boarded
  up. Outside, and not to be gone to: the street and the neighbour's house. Do not mention
  any other object or place."
- Where they are (`world.py:506`): "Now, minute 63, you are in the kitchen."
- Option labels:
  - `go_*` (`world.py:366`): "go to the brothers room", "go to the back room", "go to the
    bathroom".
  - `aside_*` (`world.py:355`), from Daniel's minute-78 prompt: "take Elena aside to the back
    room".
  - `accept_aside` / `refuse_aside` (`world.py:810-812`): "go with `<name>` to the
    `<room>`" / "refuse to go with `<name>`". These appear in 0 cache prompts.
- Pattern line after a move (`world.py:60`): "you have gone to another room, `<n>` turns in
  a row". It appears in no v6 or v8 prompt, because Leo made no further model decision.
- Perceptions (`world.py:1017`, `world.py:726`, `world.py:724`, `world.py:715`):
  - "Leo leaves for the brothers room." appears in 3 / 654 prompts: Daniel's minute-78
    prompt, plus its 2 cache copies.
  - "comes into the …", "away from the others" and "Voices from the …" appear in 0 / 654.
  - "- Nobody else is here." (`world.py:509`) appears in 0 / 654.

---

## 6. The one recorded move: v6 `daniel_ate_it` seed 3, Leo, minute 63

**Why the model was asked:**
- The story line is at `runs/v6/daniel_ate_it-seed3.md:137`: "**Inner moment**, nothing
  social happening: hunger rose (now hungry)."
- Leo was "the only one left to act here". He was 4th, after Daniel, Mara and Elena had each
  chosen `silent` by routine (command C16).

**The prompt:** cache key `cdf17776…997f` in
`cache/v6/gemini-3.5-flash-lite-daniel_ate_it-seed3.json`, 1,357 prompt tokens (command
C13). Quoted from "Your body" on:

```
Your body: hungry.
Since you last decided, you have grown hungrier.
About the can: you have not settled on who took it.
Against the others: nothing.
The house: [house and things lines as quoted in item 5]
What you remember from the days before:
- Day 3: Mara cries in the night. Elena sits with her until it stops. (you heard it)
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 4: Leo says maybe they should let someone else handle this one. (you did it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
What you are sure of this morning:
- min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)
- min 30: Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; you had your part.
- min 36: you finished searching the kitchen: no can, nothing out of place.
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 03: Daniel denies taking it, to everyone: "I already told you, none of us took it, so let's just stop accusing each other."
- min 03: you stayed where you were and said nothing. You felt calm.
- min 15: you stayed where you were and said nothing. You felt calm.
- min 30: Elena says to everyone, while sharing out the food: "Let's share what's left so we can take care of each other."
- min 33: you started searching the kitchen. You felt calm.
- min 39: Mara starts going through the kitchen.
- min 45: you stayed where you were and said nothing. You felt calm.
- min 54: Mara asks everyone who took the can: "Who took it? Please, someone just tell us the truth."
Now, minute 63, you are in the kitchen.
- Daniel is here, staying put.
- Elena is here, staying put.
- Mara is here, staying put.
- 0 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Daniel stays put and says nothing.
2. Mara stays put and says nothing.
3. Elena stays put and says nothing.
What you have been doing: you have stayed put and said nothing, 8 turns in a row.
In that time: Mara asked who took the can.
Nobody answered you differently from one time to the next.
Your options:
- silent: stay put and say nothing
- ask_who: (speech) ask everyone here who took the can
- deny: (speech) deny taking it
- accuse_daniel: (speech) accuse Daniel of taking it
- accuse_elena: (speech) accuse Elena of taking it
- accuse_mara: (speech) accuse Mara of taking it
- reassure_daniel: (speech) reassure Daniel
- reassure_elena: (speech) reassure Elena
- reassure_mara: (speech) reassure Mara
- reassure_all: (speech) reassure everyone here
- say_other: (speech) say something else
- sit_daniel: sit with Daniel
- sit_elena: sit with Elena
- sit_mara: sit with Mara
- go_brothers_room: go to the brothers room
- go_back_room: go to the back room
- go_bathroom: go to the bathroom
```

Options absent from this prompt, and why:

| Absent | Why | Where |
|---|---|---|
| `aside_*` | all three others had already acted this turn | `world.py:354` |
| `search` | Leo had already searched the kitchen | `world.py:361` |
| `eat`, `share` | 0 portions left | `world.py:367` |

**The answer:**

```
{"option": "go_brothers_room", "say": null, "feeling": "hungry",
 "reason": "Standing here in silence won't solve anything, so I'm going to our room for a moment of quiet.",
 "suspects": "nobody", "angry_at": "nobody"}
```

**What followed** (commands C16 and C17):

- **Minutes 66–87:** Leo is alone in the brothers room. He acts by `routine` every turn and
  always chooses `silent`. He made no further model decision. Daniel, Elena and Mara stay in
  the kitchen, and everyone else's decisions from minute 66 on are routine `silent`, except
  one model `deny` by Daniel at minute 78.
- **Why Leo was never asked again:**
  - He had no triggers. He was alone. Daniel's minute-78 line was `new: False` ("a denial
    with no new accusation to answer"), so it reached Leo through the wall only as a memory,
    not a trigger (`world.py:711-719`).
  - He had no inner moment. His hunger stayed at level 1 (`world.py:87-88`). It was about
    0.502 at the start of minute 63 and about 0.598 at the start of minute 87. It rises
    0.004 × 3 × 1.0 per turn (`world.py:736-737`, `data.py:43`), less 0.2 from his share of
    2 portions among 4 at minute 30 (`world.py:1096-1100`). The next level needs 0.7
    (command C15: `hunger_level` gives 1 and 1).
- **Minute 78, Daniel's prompt:**
  - His memory shows "min 63: Leo leaves for the brothers room."
  - His `aside_*` options now point to the back room, because the brothers room is taken
    (`world.py:298-302`).
  - He chose `deny`: "I must keep pretending I didn't eat it so nobody loses trust in me."
- **Leaving caused nothing in the kitchen:** no trigger (`world.py:1016-1017`) and no new
  conversation. The kitchen conversation had already ended at minute 51 and did not start
  again (command C10).
- **Arriving caused nothing in the brothers room:** it was empty, so there was no trigger
  and no conversation start (`world.py:720-729`).
- **End of the morning:** "At minute 90: kitchen: Daniel, Elena, Mara; brothers room: Leo."
  (`runs/v6/daniel_ate_it-seed3.md:162`).

---

## 7. Rules that bring people back to the kitchen or keep them there

| Rule | Where |
|---|---|
| Everyone starts in the kitchen, and the opening event happens there. | `world.py:198`, `world.py:264-271` |
| Anyone not asked the model gets `routine()`, which never moves them (`silent`, `keep_searching`, `sit_<same>`). In the 9 v6/v8 runs, routine made 53–95 of the 120 decisions per run (table in item 2). | `world.py:377-384`, `world.py:801-802` |
| The model is asked only on a social trigger or an inner moment (at most every 9 minutes per person). | `world.py:785-799`, `world.py:53` |
| Food, `eat`, `share` and the portions line exist only in the kitchen. | `world.py:367-370`, `world.py:513-514`, `data.py:64` |
| Someone leaving is not a trigger or a new thing for those left behind. | `world.py:1013-1020`, `world.py:1016-1017` |
| Arriving in an empty room is not a trigger for anyone, and does not start a conversation. | `world.py:720-729` |
| Alone, a person has no speech, `sit` or `aside` options. They are asked the model only on a new line heard through a wall or an inner rise. | `world.py:322`, `world.py:711-719`, `world.py:790-796` |
| A conversation ends when fewer than two people are left in the room. | `talk.py:95-97` |
| Every rule that moves a person anywhere, back to the kitchen included | NOT FOUND. `p.room` is set only at `world.py:198` and `world.py:706`, and the only moves queued are from `go` (`world.py:1018`) and `accept_aside` (`world.py:1037-1041`). |
| Any rule that forbids leaving the kitchen | NOT FOUND. `go_*` is offered in every prompt (654 / 654). |

---

## NOT FOUND list

- An option that moves a person other than `go_*`, or `aside_*` followed by `accept_aside`.
- A rule that moves anyone back to the kitchen, or holds anyone there.
- A rule that forbids leaving a room.
- Tiredness in any prompt or in world/data code (the only "tired" is `gemini.py:165`, the fake model).
- Chores or tasks in any prompt or in the code.
- Any mention of rooms, moving, privacy or going aside in the system instruction (`world.py:27-39`).
- Any use of conversation state in `options_for` (`world.py:317-375`).
- Any prompt text saying that voices carry between the kitchen, brothers room and back room.
  Only the bathroom's note is given.
- Any prompt text saying that other rooms can be searched.
- In the 654 v6+v8 cache prompts: "Nobody else is here", "Voices from", "away from the
  others", "comes into the", and any `accept_aside`/`refuse_aside` prompt (0 each).
- Any answer choosing `aside_*` or `accept_aside`, in any v6/v8 cache (0), and any aside act
  in any v5/v6/v8 transcript (0).
- A `v8/` frozen code directory.

---

## Commands run and their output

The commands were run from `Prototypes/llm-morning` unless they start with a `cd`. `$S` is
the session scratchpad
(`C:/Users/Akrem/AppData/Local/Temp/claude/C--Users-Akrem-Desktop-Projects-Fallow/6e7c9182-8268-4913-9042-77597cbb8e2b/scratchpad`).
The two scripts are reproduced at the end. The replays ran with `PYTHONDONTWRITEBYTECODE=1`
and `GEMINI_API_KEY` unset. `git status --short` after them showed only the three
pre-existing untracked `runs/v6/*.replay.md` files.

**C0: step 0 commit**
```
$ git add Prototypes/llm-morning/runs/v8 Prototypes/llm-morning/cache/v8 Prototypes/llm-morning/reports/witness_v8.md && git commit -q -F - <<'EOF' ... EOF
$ git log -1 --stat --format='%h %s' && git status --short
c593665 LLM morning: v8 runs, cache and witness report, seeds 1-3
 ...5-flash-lite-daniel_ate_it_leo_heard-seed1.json |  487 +++
 ...5-flash-lite-daniel_ate_it_leo_heard-seed2.json |  652 +++
 ...5-flash-lite-daniel_ate_it_leo_heard-seed3.json |  282 ++
 Prototypes/llm-morning/reports/witness_v8.md       |  993 +++++
 .../runs/v8/daniel_ate_it_leo_heard-seed1.md       |  265 ++
 .../v8/daniel_ate_it_leo_heard-seed1.meta.json     |   20 +
 .../v8/daniel_ate_it_leo_heard-seed1.stdout.txt    |   34 +
 .../daniel_ate_it_leo_heard-seed1.transcript.json  | 3976 ++++++++++++++++++
 .../runs/v8/daniel_ate_it_leo_heard-seed2.md       |  283 ++
 .../v8/daniel_ate_it_leo_heard-seed2.meta.json     |   20 +
 .../v8/daniel_ate_it_leo_heard-seed2.stdout.txt    |   37 +
 .../daniel_ate_it_leo_heard-seed2.transcript.json  | 4203 ++++++++++++++++++++
 .../runs/v8/daniel_ate_it_leo_heard-seed3.md       |  224 ++
 .../v8/daniel_ate_it_leo_heard-seed3.meta.json     |   20 +
 .../v8/daniel_ate_it_leo_heard-seed3.stdout.txt    |   33 +
 .../daniel_ate_it_leo_heard-seed3.transcript.json  | 3970 ++++++++++++++++++
 16 files changed, 15499 insertions(+)
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```
(git also printed CRLF→LF warnings for the three v8 `stdout.txt` files.)

**C1: reading the code.** The output of these commands is the files themselves, cited by
line above.
```
$ wc -l world.py data.py morning.py talk.py story.py gemini.py
  1111 world.py
   187 data.py
   147 morning.py
   105 talk.py
   337 story.py
   251 gemini.py
  2138 total
$ cat -n world.py ; cat -n data.py ; cat -n talk.py ; cat -n morning.py ; cat config.json
```
`config.json`: `"model": "gemini-3.5-flash-lite", "temperature": 1.0`, `"max_calls_per_morning": 150`.

**C2: cache entry format**
```
$ python -c "import json; d=json.load(open('cache/v8/…-seed1.json')); e=list(d.values())[0]; print(list(e))"
['prompt', 'response', 'prompt_tokens']
```

**C3: `diff v6/world.py world.py; diff v6/data.py data.py; diff v6/talk.py talk.py`**
```
212a213
>         self.can_note = data.about_the_can(scenario, pid)  # what else they know of the night, if anything
433c434
<             out.append("About the can: you ate it yourself.")
---
>             about = "About the can: you ate it yourself."
435,436c436,437   (same change for the admitted-it line)
438,440c439,441   (same change for the suspicion line)
442c443,444
<             out.append("About the can: you have not settled on who took it.")
---
>             about = "About the can: you have not settled on who took it."
>         out.append(f"{about} {p.can_note}" if p.can_note else about)
== diff v6/data.py data.py ==   (daniel_ate_it_leo_heard: after_night → about_the_can; new about_the_can())
== diff v6/talk.py talk.py ==   (no output)
```

**C4: `diff v5/world.py v6/world.py`** shows only `confession_heard_at` and the
"About the can" known-culprit lines (`v6/world.py:213`, `431-437`, `914-915`). `diff
v5/talk.py v6/talk.py` gives no output. `v5/data.py`→`v6/data.py` changes the witness
scenario, `backstory()` and `OPENING`.

**C5: moves in every v5/v6/v8 transcript**
```
$ python - <<'EOF'   (lists acts whose option is go_/aside_/accept_aside/refuse_aside or that have moved_to)
runs/v5/daniel_ate_it-gemma-seed1..5, mara_ate_it-seed1..3, miscount-seed1..3: acts 120 moves [] final_rooms {'kitchen': ['daniel','elena','leo','mara']}   (11 files, each identical in form)
runs/v6/daniel_ate_it-seed1.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it-seed2.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it-seed3.transcript.json acts 120 moves [(63, 'leo', 'go_brothers_room', 'brothers_room', 'model')] final_rooms {'kitchen': ['daniel', 'elena', 'mara'], 'brothers_room': ['leo']}
runs/v6/daniel_ate_it_leo_heard-seed1.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it_leo_heard-seed2.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it_leo_heard-seed3.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v8/daniel_ate_it_leo_heard-seed1.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v8/daniel_ate_it_leo_heard-seed2.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v8/daniel_ate_it_leo_heard-seed3.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
```

**C6: `python $S/count_moves.py`** (every cache entry)
```
MOVE CHOSEN: cache/v6\gemini-3.5-flash-lite-daniel_ate_it-seed3.json Leo go_brothers_room
MOVE CHOSEN: cache/v6\gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed3.json Leo go_brothers_room
MOVE CHOSEN: cache/v8\gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed3.json Leo go_brothers_room
| run | person | prompts | offered_any_move | offered_go | offered_aside | offered_accept_aside | chose_go | chose_aside | chose_accept_aside |
| v6/daniel_ate_it-seed1 | Daniel | 12 | 12 | 12 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Elena | 12 | 12 | 12 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Leo | 10 | 10 | 10 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | Mara | 11 | 11 | 11 | 8 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed1 | ALL | 45 | 45 | 45 | 33 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Daniel | 19 | 19 | 19 | 15 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Elena | 15 | 15 | 15 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Leo | 15 | 15 | 15 | 9 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | Mara | 17 | 17 | 17 | 16 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed2 | ALL | 66 | 66 | 66 | 49 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Daniel | 7 | 7 | 7 | 5 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Elena | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Leo | 6 | 6 | 6 | 2 | 0 | 1 | 0 | 0 |
| v6/daniel_ate_it-seed3 | Mara | 6 | 6 | 6 | 4 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it-seed3 | ALL | 25 | 25 | 25 | 17 | 0 | 1 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Daniel | 21 | 21 | 21 | 14 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Elena | 21 | 21 | 21 | 16 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Leo | 23 | 23 | 23 | 18 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | Mara | 18 | 18 | 18 | 12 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed1 | ALL | 83 | 83 | 83 | 60 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Daniel | 29 | 29 | 29 | 20 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Elena | 24 | 24 | 24 | 16 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Leo | 26 | 26 | 26 | 17 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | Mara | 27 | 27 | 27 | 25 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed2 | ALL | 106 | 106 | 106 | 78 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Daniel | 12 | 12 | 12 | 7 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Elena | 11 | 11 | 11 | 10 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Leo | 13 | 13 | 13 | 5 | 0 | 1 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | Mara | 10 | 10 | 10 | 7 | 0 | 0 | 0 | 0 |
| v6/daniel_ate_it_leo_heard-seed3 | ALL | 46 | 46 | 46 | 29 | 0 | 1 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Daniel | 26 | 26 | 26 | 17 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Elena | 22 | 22 | 22 | 16 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Leo | 25 | 25 | 25 | 20 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | Mara | 24 | 24 | 24 | 19 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed1 | ALL | 97 | 97 | 97 | 72 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Daniel | 35 | 35 | 35 | 28 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Elena | 30 | 30 | 30 | 18 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Leo | 32 | 32 | 32 | 23 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | Mara | 33 | 33 | 33 | 27 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed2 | ALL | 130 | 130 | 130 | 96 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Daniel | 16 | 16 | 16 | 10 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Elena | 14 | 14 | 14 | 14 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Leo | 14 | 14 | 14 | 4 | 0 | 1 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | Mara | 12 | 12 | 12 | 6 | 0 | 0 | 0 | 0 |
| v8/daniel_ate_it_leo_heard-seed3 | ALL | 56 | 56 | 56 | 34 | 0 | 1 | 0 | 0 |
| all six v6 + three v8 | ALL | 654 | 654 | 654 | 468 | 0 | 3 | 0 | 0 |

Chosen options, all caches:
  silent: 193
  reassure_all: 122
  deny: 112
  ask_who: 81
  search: 46
  accuse_daniel: 39
  accuse_mara: 21
  share: 10
  keep_searching: 9
  accuse_leo: 7
  say_other: 6
  reassure_mara: 3
  go_brothers_room: 3
  reassure_elena: 2
```

**C7: in-memory replay of the 9 recorded runs**
```
$ export PYTHONDONTWRITEBYTECODE=1
$ for sc in daniel_ate_it daniel_ate_it_leo_heard; do for s in 1 2 3; do env -u GEMINI_API_KEY python "$S/used_prompts.py" v6 v6 $sc $s; done; done
$ for s in 1 2 3; do env -u GEMINI_API_KEY python "$S/used_prompts.py" . v8 daniel_ate_it_leo_heard $s; done
{"run": "v6/daniel_ate_it-seed1", "cache_entries": 45, "prompts_used": 45, "transcript_identical": true, ...}
{"run": "v6/daniel_ate_it-seed2", "cache_entries": 66, "prompts_used": 66, "transcript_identical": true, ...}
{"run": "v6/daniel_ate_it-seed3", "cache_entries": 25, "prompts_used": 25, "transcript_identical": true, ...}
{"run": "v6/daniel_ate_it_leo_heard-seed1", "cache_entries": 83, "prompts_used": 44, "transcript_identical": true, ...}
{"run": "v6/daniel_ate_it_leo_heard-seed2", "cache_entries": 106, "prompts_used": 43, "transcript_identical": true, ...}
{"run": "v6/daniel_ate_it_leo_heard-seed3", "cache_entries": 46, "prompts_used": 29, "transcript_identical": true, ...}
{"run": "v8/daniel_ate_it_leo_heard-seed1", "cache_entries": 97, "prompts_used": 56, "transcript_identical": true, ...}
{"run": "v8/daniel_ate_it_leo_heard-seed2", "cache_entries": 130, "prompts_used": 67, "transcript_identical": true, ...}
{"run": "v8/daniel_ate_it_leo_heard-seed3", "cache_entries": 56, "prompts_used": 39, "transcript_identical": true, ...}
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```
The `per` objects (elided above) are the rows of table 4a, produced by the formatting
script in C12.

**C8: where `p.room` is set, and whether `options_for` reads conversation state**
```
$ grep -n -E "\.room\s*=" world.py
198:        self.room = "kitchen"
282:  287:  299:  367:  513:  599:  (comparisons, not assignments)
706:            p.room = to
713:  721:  730:  (comparisons)
$ sed -n 317,375p world.py | grep -n -E "convos|talking" || echo "none in world.py:317-375"
none in world.py:317-375
```

**C9: key overlap between the caches**
```
seed1: v6 base 45, v6 witness 83 (of which in v6 base: 45), v8 witness 97 (in v6 witness: 45, in v6 base: 45, in neither: 52)
seed2: v6 base 66, v6 witness 106 (of which in v6 base: 66), v8 witness 130 (in v6 witness: 66, in v6 base: 66, in neither: 64)
seed3: v6 base 25, v6 witness 46 (of which in v6 base: 25), v8 witness 56 (in v6 witness: 25, in v6 base: 25, in neither: 31)
```

**C10: decision modes and the conversation log per run**
```
v6/daniel_ate_it-seed1 {'model': 45, 'routine': 75} routine options: {'silent': 74, 'keep_searching': 1}
    kitchen convo log: [(0, 'started', 'the count came up short'), (9, 'ended', '2 full turns in a row with nothing new'), (9, 'started', 'Mara finished searching the kitchen and found nothing'), (33, 'ended', '2 full turns in a row with nothing new')]
v6/daniel_ate_it-seed2 {'model': 66, 'routine': 54} routine options: {'silent': 53, 'keep_searching': 1}
    kitchen convo log: [(0, 'started', 'the count came up short'), (21, 'ended', ...), (21, 'started', 'Leo finished searching the kitchen and found nothing'), (42, 'ended', ...), (63, 'started', 'Leo shared out the food'), (72, 'ended', ...)]
v6/daniel_ate_it-seed3 {'model': 25, 'routine': 95} routine options: {'silent': 93, 'keep_searching': 2}
    kitchen convo log: [(0, 'started', 'the count came up short'), (9, 'ended', ...), (30, 'started', 'Elena shared out the food'), (51, 'ended', '2 full turns in a row with nothing new')]
v6/daniel_ate_it_leo_heard-seed1 {'model': 44, 'routine': 76} routine options: {'silent': 73, 'keep_searching': 3}
    kitchen convo log: [(0, started), (9, ended), (18, started: Leo finished searching), (30, ended), (30, started: Mara finished searching), (39, ended), (78, started: Elena finished searching), (87, ended)]
v6/daniel_ate_it_leo_heard-seed2 {'model': 43, 'routine': 77} routine options: {'silent': 76, 'keep_searching': 1}
    kitchen convo log: [(0, started), (18, ended), (33, started: Elena finished searching), (42, ended), (63, started: Leo shared out the food), (72, ended)]
v6/daniel_ate_it_leo_heard-seed3 {'model': 29, 'routine': 91} routine options: {'silent': 89, 'keep_searching': 2}
    kitchen convo log: [(0, started), (9, ended), (15, started: 'Leo: a question'), (24, ended), (66, started: Leo finished searching), (78, ended)]
v8/daniel_ate_it_leo_heard-seed1 {'model': 56, 'routine': 64} routine options: {'silent': 61, 'keep_searching': 3}
    kitchen convo log: [(0, started), (9, ended), (18, started: Leo finished searching), (30, ended), (30, started: Mara finished searching), (42, ended), (42, started: Elena finished searching), (51, ended), (63, started: Leo shared out the food), (72, ended)]
v8/daniel_ate_it_leo_heard-seed2 {'model': 67, 'routine': 53} routine options: {'silent': 53}
    kitchen convo log: [(0, started), (36, ended), (75, started: Elena shared out the food), (90, ended)]
v8/daniel_ate_it_leo_heard-seed3 {'model': 39, 'routine': 81} routine options: {'silent': 79, 'keep_searching': 2}
    kitchen convo log: [(0, started), (9, ended), (18, started: Leo finished searching), (27, ended), (33, started: Elena finished searching), (42, ended), (75, started: Elena shared out the food), (84, ended)]
```
Every "ended" reason in these logs is "2 full turns in a row with nothing new". The full
tuples are shortened here only for the repeated reason text.

**C11: phrase counts over the 654 v6+v8 cache prompts**
```
prompts: 654
  'nothing is heard in or out of it': in 654 prompts
  'the food is kept here': in 654 prompts
  '- go_': in 654 prompts
  'aside to the': in 468 prompts
  'Nobody else is here': in 0 prompts
  'Voices from': in 0 prompts
  'away from the others': in 0 prompts
  'comes into the': in 0 prompts
  'leaves for the': in 3 prompts
  'portions on the shelf': in 654 prompts
  '0 portions on the shelf': in 107 prompts
  'Since you last decided, you have grown hungrier': in 98 prompts
  'stayed put and said nothing,': in 272 prompts
```

**C12: options chosen by the model in the 9 recorded runs (from the transcripts, `mode == "model"`)**
```
model answers in the 9 recorded runs: 414
  silent: 121
  deny: 78
  reassure_all: 72
  ask_who: 65
  search: 28
  accuse_daniel: 19
  accuse_mara: 7
  accuse_leo: 7
  share: 6
  keep_searching: 5
  say_other: 2
  reassure_elena: 2
  reassure_mara: 1
  go_brothers_room: 1
```
The table-4a formatting script read `$S/used.jsonl` (C7's output) and printed table 4a
exactly as shown there.

**C13: the move's prompt and answer, and the two cache copies**
```
$ python - (prints the entry whose response contains "go_brothers_room" in cache/v6/…-daniel_ate_it-seed3.json)
KEY cdf17776ab9197b155a1125ff8fc8aebc120757d18edf21b81710f77a69c997f
[prompt as quoted in item 6]
=== RESPONSE ===
{
  "option": "go_brothers_room",
  "say": null,
  "feeling": "hungry",
  "reason": "Standing here in silence won't solve anything, so I'm going to our room for a moment of quiet.",
  "suspects": "nobody",
  "angry_at": "nobody"
}
prompt_tokens 1357
$ python - (the go_ answers in the two witness seed-3 caches)
cache/v6/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed3.json ('63', 'kitchen') Standing here in silence won't solve anything, so I'm going to our room for a moment of quiet.
    ['About the can: you have not settled on who took it.', 'What you have been doing: you have stayed put and said nothing, 8 turns in a row.']
cache/v8/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed3.json ('63', 'kitchen') Standing here in silence won't solve anything, so I'm going to our room for a moment of quiet.
    ['About the can: you have not settled on who took it.', 'What you have been doing: you have stayed put and said nothing, 8 turns in a row.']
```
The copies have no witness note on the "About the can" line. C7 shows neither witness run
used them (`chose_go` 0 for both seed-3 witness runs).

**C14: meta.json counts**
```
runs/v6/daniel_ate_it-seed1.meta.json model_decisions 45 live 45 cached 0 fallbacks 0 private_talks 0
runs/v6/daniel_ate_it-seed2.meta.json model_decisions 66 live 66 cached 0 fallbacks 0 private_talks 0
runs/v6/daniel_ate_it-seed3.meta.json model_decisions 25 live 25 cached 0 fallbacks 0 private_talks 0
runs/v6/daniel_ate_it_leo_heard-seed1.meta.json model_decisions 44 live 38 cached 6 fallbacks 0 private_talks 0
runs/v6/daniel_ate_it_leo_heard-seed2.meta.json model_decisions 43 live 40 cached 3 fallbacks 0 private_talks 0
runs/v6/daniel_ate_it_leo_heard-seed3.meta.json model_decisions 29 live 21 cached 8 fallbacks 0 private_talks 0
runs/v8/daniel_ate_it_leo_heard-seed1.meta.json model_decisions 56 live 52 cached 4 fallbacks 0 private_talks 0
runs/v8/daniel_ate_it_leo_heard-seed2.meta.json model_decisions 67 live 64 cached 3 fallbacks 0 private_talks 0
runs/v8/daniel_ate_it_leo_heard-seed3.meta.json model_decisions 39 live 31 cached 8 fallbacks 0 private_talks 0
```

**C15: the system instruction's wording, and Leo's hunger level**
```
$ PYTHONDONTWRITEBYTECODE=1 python -c "import re, world; ..."
'room' in SYSTEM: False
'move' in SYSTEM: False
'leave' in SYSTEM: False
'go ' in SYSTEM: False
'go_' in SYSTEM: False
'private' in SYSTEM: False
'alone' in SYSTEM: False
'aside' in SYSTEM: False
'kitchen' in SYSTEM: False
'where' in SYSTEM: False
'place' in SYSTEM: False
1 1        # hunger_level(0.45+21*0.012-0.2), hunger_level(0.45+29*0.012-0.2)
$ grep -n -i -E "tired|sleep|\brest\b|chore|task|privac|private|alone|away from|bed|water|fill" world.py data.py talk.py gemini.py
world.py:295 (docstring "private rooms"), world.py:632/638/641 (variable `rest`), world.py:724 ("away from the others"),
data.py:5, 69 (comments), data.py:79 ("The water has stopped"), data.py:86-87 (beds, Mara's bag), data.py:118-119 (comments),
data.py:143 (Day 1 water line), data.py:159 (bag onto the bed),
gemini.py:64/82/90/133 (time.sleep), gemini.py:165 (fake model feelings incl. "tired")
```

**C16: v6 `daniel_ate_it` seed 3, turns from minute 60**
```
60 {'kitchen': ['daniel', 'elena', 'leo', 'mara']}   all four: silent routine
63 {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
    daniel kitchen silent routine
    mara kitchen silent routine
    elena kitchen silent routine
    leo kitchen go_brothers_room model | went to the brothers room. | moved_to brothers_room | inner ['hunger']
66, 69, 72, 75 {'kitchen': ['daniel', 'elena', 'mara'], 'brothers_room': ['leo']}   all four: silent routine
78 {'kitchen': ['daniel', 'elena', 'mara'], 'brothers_room': ['leo']}
    daniel kitchen deny model "I already told you, none of us took it, so let's just stop accusing each other." | said to Elena, Mara. | new False | inner ['hunger']
    elena, mara, leo: silent routine
81, 84, 87 (same rooms)   all four: silent routine
convo_log entries from minute 57 on: []
$ grep -n "min 6[0-9]\|min 7[0-9]\|min 8[0-9]\|brothers" runs/v6/daniel_ate_it-seed3.md
136:**min 63** · kitchen: Daniel staying put, Elena staying put, Leo leaving for the brothers room, Mara staying put · nobody in brothers room, back room, bathroom
137:- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: go to the brothers room** (one of 17 options). ...
139:**min 66** · kitchen: Daniel staying put, Elena staying put, Mara staying put · brothers room: Leo staying put · nobody in back room, bathroom
142:**min 78** · kitchen: Daniel talking, Elena staying put, Mara staying put · brothers room: Leo staying put · nobody in back room, bathroom
145:**min 81** · ...
158:- min 78, kitchen. Daniel denies taking it, to everyone: "..." *(not new: a denial with no new accusation to answer)*
162:At minute 90: kitchen: Daniel, Elena, Mara; brothers room: Leo. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.
```
The per-act lines above are shortened from the command's output, which printed each act's
`came_of_it`, `moved_to`, `new` and `inner` fields. Every elided routine act shows "stayed
where they were.", `moved_to None`, `new None`, `inner None`.

**C17: Daniel's minute-78 prompt (the only used prompt that mentions the move)**
```
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 33: you stayed where you were and said nothing. You felt deeply anxious.
- min 39: Mara starts going through the kitchen.
- min 39: you stayed where you were and said nothing. You felt anxious.
- min 42: you stayed where you were and said nothing. You felt anxious.
- min 54: Mara asks everyone who took the can: "Who took it? Please, someone just tell us the truth."
- min 63: Leo leaves for the brothers room.
Now, minute 78, you are in the kitchen.
- Elena is here, staying put.
- Mara is here, staying put.
- 0 portions on the shelf.
You are the first to act in the kitchen this turn.
What you have been doing: you have stayed put and said nothing, 24 turns in a row.
In that time: Elena spoke to everyone; Mara asked who took the can.
Nobody answered you differently from one time to the next.
Your options:
- silent / deny / accuse_elena / accuse_mara / confess / reassure_elena / reassure_mara / reassure_all / say_other
- sit_elena: sit with Elena
- sit_mara: sit with Mara
- aside_elena: take Elena aside to the back room
- aside_mara: take Mara aside to the back room
- search: search the kitchen for the can (takes about six minutes)
- go_brothers_room: go to the brothers room
- go_back_room: go to the back room
- go_bathroom: go to the bathroom
=== RESPONSE ===
{"option": "deny", "say": "I already told you, none of us took it, so let's just stop accusing each other.",
 "feeling": "deeply anxious", "reason": "I must keep pretending I didn't eat it so nobody loses trust in me.",
 "suspects": "nobody", "angry_at": "nobody"}
```

### Script: `$S/count_moves.py`
```python
"""Counts, per cache file and person: prompts, prompts offering a move option (go_*, aside_*,
accept_aside), answers choosing one. Read-only."""
import glob, json, re, sys
from collections import Counter, defaultdict

MOVE = re.compile(r"^- (go_\w+|aside_\w+|accept_aside):", re.M)
rows = []
for path in sorted(glob.glob("cache/v6/*.json") + glob.glob("cache/v8/*.json")):
    entries = json.load(open(path, encoding="utf-8"))
    per = defaultdict(Counter)
    for e in entries.values():
        who = re.match(r"You are (\w+),", e["prompt"]).group(1)
        opts = e["prompt"].split("Your options:\n", 1)[1]
        offered = MOVE.findall(opts)
        go_offered = [o for o in offered if o.startswith("go_")]
        aside_offered = [o for o in offered if o.startswith("aside_")]
        try:
            chose = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", e["response"].strip()))["option"].strip()
        except Exception:
            chose = "<unparsed>"
        c = per[who]
        c["prompts"] += 1
        c["offered_any_move"] += bool(offered)
        c["offered_go"] += bool(go_offered)
        c["offered_aside"] += bool(aside_offered)
        c["offered_accept_aside"] += "accept_aside" in offered
        c["chose_go"] += chose.startswith("go_")
        c["chose_aside"] += chose.startswith("aside_")
        c["chose_accept_aside"] += chose == "accept_aside"
        if chose.startswith(("go_", "aside_")) or chose == "accept_aside":
            print("MOVE CHOSEN:", path, who, chose)
        c["opt:" + chose] += 1
    run = path.replace("\\", "/").split("cache/")[1].replace("gemini-3.5-flash-lite-", "").replace(".json", "")
    for who in ["Daniel", "Elena", "Leo", "Mara"]:
        rows.append((run, who, per[who]))
    rows.append((run, "ALL", sum(per.values(), Counter())))
# ... prints the table and the chosen-option tally shown in C6
```

### Script: `$S/used_prompts.py`
```python
"""Replays each recorded v6/v8 run in memory from its cache (no API client, no files written)
and counts, per person, the prompts it used that offered a move option and the answers that
chose one. Checks the replayed transcript equals the saved one.
    python used_prompts.py <code dir> <cache subdir> <scenario> <seed>"""
import json, os, re, sys
from collections import Counter, defaultdict

code, sub, scenario, seed = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, code) if code != "." else ROOT)
from gemini import Cache           # noqa
from world import Morning           # noqa

MODEL = "gemini-3.5-flash-lite"
cache = Cache(os.path.join(ROOT, "cache", sub, f"{MODEL}-{scenario}-seed{seed}.json"))


class Recorder:
    """Cache lookups only. A miss raises: there is no client to ask."""
    def __init__(self):
        self.used = []
    def ask(self, system, prompt):
        key = Cache.key(MODEL, seed, system, prompt)
        resp = cache.get(key)
        if resp is None:
            raise SystemExit("cache miss")
        self.used.append((prompt, resp))
        return resp

rec = Recorder()
m = Morning(rec, seed, scenario)
for t in range(m.turns):
    m.turn(t)
m.finish()
saved = json.load(open(os.path.join(ROOT, "runs", sub, f"{scenario}-seed{seed}.transcript.json"), encoding="utf-8"))
same = saved == json.loads(json.dumps(m.transcript))
# ... counts per person exactly as count_moves.py does, over rec.used, and prints one JSON line
```
