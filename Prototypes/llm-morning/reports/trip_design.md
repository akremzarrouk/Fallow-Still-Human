# Design: the second concern, a trip to the neighbour's house tonight (`daniel_ate_it`, v11)

Mode: design. No code was written or changed, and no API was called. Besides committing
`reports/pattern_probe.md` first, on its own, as `0203260`, this file is the only thing this step
adds. Paths are relative to `Prototypes/llm-morning/`. Scratch scripts are in the session
scratchpad (`$S/trip/`) and are reproduced in §13.

**The problem.** Once the can stops being a mystery, the morning has nothing left to be about.
- In gist_words_v10.md §5, seed 1 is silent from minute 36 to 87 after Daniel confesses and
  Leo and Mara eat the last two portions. Nobody says a word about the food being gone.
- Seeds 2 and 3 freeze from minute 36 to 51 and from 27 to 51 (N9, §4 there).
- In seeds 1 and 3, every model decision from minute 30 on is an inner moment for hunger rising
  (§13 command 6). Seed 1: Elena at 30, Daniel at 33 and 66, Elena at 75. Seed 3: the same,
  plus Mara at 54 and Leo at 63.
  The body keeps saying "hungrier", and nothing in the world says what that means for tomorrow.

A real family with two portions left, no water and an empty house next door would talk about
that house. Daniel already did, on day 2 (data.py:146-151).

**The mechanism in one paragraph.**
- When the shelf is empty, or when someone first becomes "very hungry", the code draws a
  conclusion for everyone, as the witness line did for Leo (data.py:116-126). The conclusion: no
  food for tomorrow; the neighbour's house has been empty since the first days and may have
  food; outside is dangerous.
- From then on, each person has six kinds of speech option about whether someone goes there
  tonight.
- The code records who took which position and decides nothing.
- The story ends with the state of the plan in plain words.
- Nobody leaves the house. Nothing in the code connects this concern to the can.

**What is compared.** `daniel_ate_it` seeds 1–3 under v11 (the current code plus this design),
paired with the v10 answers, against `runs/v10/daniel_ate_it-seed1..3`. Up to the trigger the
two mornings are the same, byte for byte. They part at the trigger (§1, §8 T3).

**Something to decide before implementation (§2.5).** After the trigger, prompts get longer by
77 to 374 estimated tokens, because the new block is kept outside the 1,400 budget. The
alternative is to keep the budget and lose almost all morning memory. Two existing test bounds
change because of this (§8 T12).

---

## 1. The trigger

### The rule

Checked once at the **start of every turn**, before anyone in any room acts, and only while the
concern has not started (`self.trip is None`). The trigger fires on whichever comes first:

- **(a) No food left in the house:** `self.portions == 0`. The shelf is the only food the house
  has (data.py:84-90).
- **(b) One person's hunger reaches "very hungry":** `hunger_level(p.hunger) >= TRIP_HUNGER`,
  where `TRIP_HUNGER = 2`, for any person (world.py:94-95, world.py:73).

If both hold at the same turn, both reasons are recorded. **It fires once per morning and
never fires again.** It reads only the shelf and hunger. It never reads anything about the can
(§5).

**Why the start of the turn.**
- Hunger changes only at the end of a turn (world.py:751-752).
- The shelf empties during a turn (world.py:1107, world.py:1134).
- Checking at the start means a turn is entirely before or entirely after the trigger. That is
  what makes every prompt before it identical to v10 (§8 T2, T3).
- The cost is that someone who empties the shelf at minute m triggers it at m+3.

### Who is asked on the trigger turn (the "trip moment")

- **(a) The shelf is empty:** everyone in the kitchen at the start of the turn. They are
  standing in front of the empty shelf.
- **(b) Hunger:** only the person or people whose hunger is at level 2 or above at that turn.
  Their body changed. Nobody else's did.

These people are asked the model on this turn even if nothing social happened to them and the
inner-moment spacing (`INNER_EVERY`, world.py:57) would hold them back. The decision is
recorded as `d["trip_moment"] = <trigger minute>`.

- **Priority.** Social triggers, the trip moment, inner moments and lulls all lead to the same
  `ask_model` call (world.py:815-816). The trip moment does not replace the inner-moment check.
  If the hunger rise also qualifies as an inner moment, it is recorded as one too, as now.
- **Everyone else** gets the new lines (§2) from the trigger on, but is asked only when
  something social, inner or new reaches them. That includes someone raising the trip aloud,
  which is new (§3.3).

### The level, from the v10 runs

`$S/trip/trigger.py` (§13 command 4) replays hunger and portions from each v10 transcript
with world.py's own arithmetic: +0.004 × 3 × `hunger_rate` per turn, −0.4 per portion eaten.

| Seed | Shelf empty from | First "very hungry" (level 2) | First "starving" (level 3) | Trigger at level 2 | Why | Asked at the trigger |
|---|---|---|---|---|---|---|
| 1 | min 24 (Leo and Mara ate at 21) | min 30, Elena | min 66, Daniel | **min 24** | the shelf is empty | Daniel, Elena, Leo, Mara (all in the kitchen) |
| 2 | never | min 30, Elena | min 66, Daniel | **min 30** | Elena is very hungry | Elena |
| 3 | never | min 30, Elena | min 66, Daniel | **min 30** | Elena is very hungry | Elena |

**How often it would have fired:** once in each of the 3 v10 seeds, at minutes 24, 30 and 30.

**Where that falls against the silences** (gist_words_v10.md §4, N9):

| Seed | Frozen stretch in v10 | Trigger |
|---|---|---|
| 1 | 36–87 | 12 minutes before it |
| 2 | 36–51 | 6 minutes before it |
| 3 | 27–51 | its second turn |

**The levels not chosen:**
- **Level 3 ("starving")** would fire at minutes 24, 66 and 66. In seeds 2 and 3 that leaves 8
  turns and comes after every frozen stretch. The concern would arrive when the morning is
  already over.
- **Level 1 ("hungry")** fires at minute 00 in every seed, because Daniel starts at 0.55
  (data.py:25). The trip would then compete with the can from the first turn. The brief wants
  it as the next problem, not the first.
- **Level 2** is the first level that is a real change in anyone's body during the morning.
  Elena reaches it first in every seed: she controls the food and has eaten nothing. She is
  the person a real family would expect to say first that there is nothing for tomorrow.

**What the trigger costs in requests.**
- Elena's minute-30 decision in seeds 2 and 3 already exists in v10. It is an inner moment,
  "hunger rose (now very hungry)" (§13 command 6), so it adds **0 requests**.
- Seed 1's minute-24 moment adds **1 request** (Elena). Daniel, Leo and Mara were already asked
  at minute 24 in v10.

---

## 2. What each person learns at the trigger (the lesson lines)

### 2.1 The lines, exactly

From the trigger on, for **every person**, wherever they are, `inside_lines` (world.py:437-466)
gets these lines right after the "About the can:" line and its note (world.py:443-455), and
before "Against …" (world.py:456-461):

```
About food: there is no food in the house for tomorrow.
About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
```

Once the person has heard (or said) at least one trip position, a third line follows (§4.2):

```
About going there tonight: <positions they heard, oldest first>.
```

- **Every fact is in these lines**: no food for tomorrow; the neighbours left in the first days;
  nobody has been inside since; there may be food there; outside is dangerous. Each conclusion
  comes with its "so" (belief_line_impl.md: the line says what follows, so the model does not
  have to work it out).
- **"Outside is dangerous."** is the whole description of the danger. It names no creature,
  no cause and no event.
- **"the neighbour's house"** is spelled as data.py writes it (data.py:89, data.py:146), so it
  stays on the list of places the house has (N13).
- **"for tomorrow"** is true in every state, whether the shelf holds 2, 1 or 0 portions. So the
  line never states a count the person might not know, for example someone in the back room
  when a portion is eaten.
- **None of the lines mentions the can**, who took it, or anyone's guilt (§5).

### 2.2 One phrase in the house line

After the trigger, and only then, the house text (data.py:84-90, used at world.py:516) changes
one phrase:

```
before:  Outside, and not to be gone to: the street and the neighbour's house.
after:   Outside, and not to be gone to this morning: the street and the neighbour's house.
```

**Why.**
- Unchanged, the prompt would forbid the very place the new options talk about, and the model
  would see a contradiction. That would push it toward objecting for a reason no person in the
  house has.
- "this morning" says exactly what the code enforces: nobody leaves during the morning (§3.4).
- It is the one change outside the lesson lines. It adds no fact about the world.

### 2.3 The day-2 memories are kept

**The finding** (§13 command 2). By minute 21, every prompt in every v10 seed was already cut
to its last 4 backstory events. The cut is the budget trimming at world.py:543-561, oldest first.
So the three day-2 events about this very trip are gone from every prompt after the trigger:

```
- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
```

These are data.py:146-151, verbatim, with each person's own "(you did it)" or "(you saw it)".
All four were there for all three events.

**The design.** After the trigger, the trimming loop never removes these three events.
- It removes the oldest *other* backstory event instead, down to the same 4.
- The list stays in day order, so the three day-2 events come first.
- Before the trigger, nothing changes.

**Why.** A real person asked "should someone go next door tonight?" remembers that the family
argued about exactly that two days ago, and how it ended. The trimming is a token budget, not
forgetting. These lines add no new wording about the danger. "gets someone killed" is
existing backstory, already in every early prompt.

### 2.4 An example: Elena, seed 2, minute 30

This is the first prompt in seed 2 that changes. It is her v10 prompt rebuilt as this design
would write it (§13 command 7). The diff against the v10 prompt:

```
@@ -8,0 +9,3 @@
+About food: there is no food in the house for tomorrow.
+About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
@@ (house line) @@
-… Outside, and not to be gone to: the street and the neighbour's house. Do not mention any other object or place.
+… Outside, and not to be gone to this morning: the street and the neighbour's house. Do not mention any other object or place.
@@ -11,0 +15,3 @@
+- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
+- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
+- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
@@ -49,0 +56,5 @@
+- propose_trip: (speech) say someone should go to the neighbour's house tonight
+- volunteer: (speech) offer to go there tonight yourself
+- back_daniel: (speech) say Daniel should be the one to go
+- back_leo: (speech) say Leo should be the one to go
+- back_mara: (speech) say Mara should be the one to go
```

- The script's output in §13 command 7 also has "About going there tonight: you have heard
  nobody speak of it." That was the first draft. §6.1 removed it: before anything has been
  said, the line is left out.
- Estimated tokens: 1,372 in v10, 1,635 with the block (1,618 without that dropped line).

### 2.5 The prompt budget: the decision to make

**The numbers** (§13 command 2).
- After minute 21, v10 prompts are at 1,364–1,397 estimated tokens. The budget is 1,400
  (world.py:55).
- What trimming cannot remove (the floor) is already 1,078–1,274.
- What is left is 4 backstory events and 0–8 morning lines.

**The block's size** (§13 command 5):

| Part | Estimated tokens |
|---|---|
| The two "About" lines | 56 |
| The plan line | 0 (nothing heard) to 48 (four positions) |
| The three day-2 lines | 101 |
| `propose_trip` + `volunteer` | 38 |
| `back_*` ×3 | 46 |
| `object_*` ×3 (only for people named to go) | 0–51 |
| `object_trip` + `decline` (only when relevant) | 0–31 |
| " this morning" | 4 |
| **Block** | **60 (alone, no options) · ~245 (typical first prompt) · 374 (largest possible)** |

**Proposed: the budget applies to the prompt without the block.**
- The trimming loop (world.py:551) compares `estimate_tokens(SYSTEM + text) − block` with
  `PROMPT_TOKEN_BUDGET`.
- So the rest of the prompt keeps exactly the memory it would have kept without the concern.
- Post-trigger prompts reach about 1,400 + block: about 1,650 typical and 1,774 at most.

**The alternative: keep the budget.** The block would push out nearly every morning line,
which is the confession, the accusations and the eating. Leo's seed-2 minute-66 prompt already
has 0 morning lines. People would discuss the trip having forgotten the morning, and P4 (the can
shaping the plan) would be tested on prompts that no longer hold the can's events.

**The cost** is prompt tokens, not requests. The daily limit that matters is 500 requests
(CLAUDE.md).

---

## 3. The options

### 3.1 The set

These are offered only from the trigger on, and only when someone else is in the room (they are
speech, like every can option, world.py:333). In the list they go after `reassure_all` and
before `say_other` (world.py:352-354), in this order:

| Id | Label | Kind (talk.py) | Target | Offered when (and someone else is here) |
|---|---|---|---|---|
| `propose_trip` | (speech) say someone should go to the neighbour's house tonight | `propose` | — | They have not proposed it before this morning (once per person, as `confess` is). |
| `volunteer` | (speech) offer to go there tonight yourself | `volunteer` | — | Their own current position is not "offered to go". |
| `object_trip` | (speech) say nobody should go out tonight | `object` | — | They have heard or made at least one proposal, offer or backing, and their current position is not this one. |
| `back_<q>` | (speech) say `<Name>` should be the one to go | `back` | q | For each other person here, unless their current position is backing q. |
| `object_<q>` | (speech) say `<Name>` should not be the one to go | `object` | q | For each other person here who, as far as they have heard, is named to go (q offered, or someone backed q, and q has not since said they will not go), unless their current position is this one. |
| `decline` | (speech) say you will not be the one to go | `decline` | — | Someone has backed them in their hearing, or they offered to go themselves, and their current position is not this one. |

**Terms.**
- **A person's current position** is their latest trip act. There is one per person.
- **What they have heard** is the trip acts made in the room while they were there (§4.1).
  Voices through a wall carry no words (world.py:723-734), so they carry no positions either.

**Why this set and no more.**
- It has the five moves the brief names (propose, volunteer, object to the trip, object to a
  person, back a person), plus `decline`, the refusal of the person named.
- Without `decline`, someone named who does not want to go could only oppose the whole trip.
  The record would then say something they do not mean.
- There is **no option to agree to everyone going, or to settle it.** That is deliberate (§6.2).
- `object_*` and `decline` appear only when there is something to object to or decline. In a
  typical first prompt that adds 5 lines: `propose_trip`, `volunteer` and three `back_*`.

**No trip option can be chosen twice in a row by the same person.** After choosing one, it is
their current position, and that option is not offered again until their position changes.
This is the design's answer to repetition (§6.1). The existing cap on three of one speech kind
in a row (world.py:382-385) also applies, because the new kinds join `SPEECH` (§3.3).

### 3.2 What each option does

Each one is an ordinary spoken line through the existing speech path (world.py:915-1003):
`so_far`, `said`, perceive with a trigger, `heard`, voices, `p.memory` and `said_lines` without
the words. In addition:

1. **The record.** `self.trip_acts.append((minute, p.id, kind, target, words))`. For the speaker
   and for everyone in the room, `x.trip_heard[p.id] = (minute, kind, target)`, the latest per
   speaker. `propose_trip` also sets `p.proposed = True`.
2. **Aimed lines.** `back_<q>` and `object_<q>` are aimed at q (`aimed_at`, talk.py:28-31). q
   gets `addressed` and acts first in the room next turn, as when spoken to (world.py:941-942,
   world.py:637-649).
3. **Nothing else.** No hunger, portions, guilt, grudge, suspicion, `heard_question`,
   `knows_culprit` or movement changes. Grudges about being sent into danger can still come
   from the people: the existing `angry_at` answer raises a grudge (world.py:782-787).

**The words each person hears** (`line_text`, world.py:859-875, new branches):

| Kind | Others hear | The speaker's own line (`said_lines` and memory, no words) |
|---|---|---|
| `propose` | `<Name> says someone should go to the neighbour's house tonight: "<words>"` | `you said someone should go to the neighbour's house tonight.` |
| `volunteer` | `<Name> offers to go to the neighbour's house tonight: "<words>"` | `you offered to go there tonight.` |
| `object` (none) | `<Name> says nobody should go out tonight: "<words>"` | `you said nobody should go out tonight.` |
| `object` (q) | `<Name> says <q or "you"> should not be the one to go: "<words>"` | `you said <Q> should not be the one to go.` |
| `back` (q) | `<Name> says <q or "you"> should be the one to go: "<words>"` | `you said <Q> should be the one to go.` |
| `decline` | `<Name> says <he/she> will not be the one to go: "<words>"` | `you said you will not be the one to go.` |

**`KIND_DONE`** (world.py:63-71), for the pattern block: `propose` "said someone should go to the
neighbour's house tonight", `volunteer` "offered to go there tonight", `object` "said someone
should not go", `back` "said someone should be the one to go", `decline` "said you will not be the
one to go".

**`heard_verb`** (world.py:496-501). It only ever sees lines aimed at the listener or at
everyone (world.py:479). `propose` "said someone should go to the neighbour's house tonight",
`volunteer` "offered to go there tonight", `object` "said nobody should go" or "said you should
not be the one to go", `back` "said you should be the one to go", `decline` "said they will not be
the one to go".

### 3.3 What counts as new (talk.py)

- `SPEECH` (talk.py:9) gains `"propose", "volunteer", "object", "back", "decline"`.
- `act_of` (talk.py:11-25) maps:
  - `propose_trip` → (`propose`, None)
  - `volunteer` → (`volunteer`, None)
  - `object_trip` → (`object`, None), checked before the `object_` prefix
  - `object_<q>` → (`object`, q)
  - `back_<q>` → (`back`, q)
  - `decline` → (`decline`, None)
- `aimed_at` (talk.py:28-31) adds `back` and `object` to the aimed kinds.
- `Newness.line` (talk.py:44-69): a trip line is **new the first time this speaker takes that
  stance** (`propose`; `volunteer`; `decline`; (`object`, target); (`back`, target)), and not new
  after that. This mirrors accusations (talk.py:58-63).
- So the first time anyone raises the trip, it starts the room's conversation
  (world.py:925-928), and everyone in the room is asked next. Restating a stance does not keep
  a conversation alive, so it ends after two quiet turns (world.py:56, talk.py:91-105), as with
  the can.
- Why strings: "a proposal", "an offer to go", "an objection", "backing someone to go", "a
  refusal to go", and "… they had made before" for repeats.

### 3.4 Nobody leaves the house

- No option moves anyone outside. `go_*` still lists only the four rooms (world.py:375-377).
- `volunteer` is an offer for tonight. The morning ends at minute 90 (data.py:76), before
  tonight.
- §8 T7 checks that every `moved_to` in every transcript is one of the four rooms.
- If the model's words say "I'll go now", the record still says only what the option says.
  §9 R6 reports such words.

---

## 4. The plan record, and how the story ends

### 4.1 What is recorded

- `self.trip`: `None` until the trigger, then `{"minute": T, "why": [...], "asked": [...]}`.
  `why` holds `"the shelf is empty"` and/or `"<Name> is very hungry"`.
- `self.trip_acts`: every trip act, `(minute, who, kind, target, words)`, in order.
- Per person: `trip_heard` (speaker → latest heard act, their own included) and `proposed`.
- Transcript (`world.py` `finish`, world.py:611-625): `"trip": {"minute", "why", "asked",
  "acts": [[minute, who, option, words], ...], "plan": "<the plan line>"}`, or `"trip": null`
  if it never fired. Each act gets a `"trip_moment"` key (the trigger minute, or `None`).
- Meta (morning.py:88-104): `"trip_minute"` and `"trip_acts"` (a count). Both are also printed
  in the console summary.

**There is no decision rule.** Nothing is ever settled, voted on, carried out or closed.
- The concern stays open to the end of the morning.
- Positions can change any number of times. Only each person's latest one counts.

### 4.2 The plan line in a prompt

It appears only after the person has heard or made at least one trip act. It gives each
speaker's latest position as **this person heard it**, oldest first, with its minute:

| Position | Rendered |
|---|---|
| propose | `<X> said someone should go (min MM)` |
| volunteer | `<X> offered to go (min MM)` |
| object, none | `<X> said nobody should go (min MM)` |
| object, q | `<X> said <Q> should not go (min MM)` |
| back, q | `<X> said <Q> should go (min MM)` |
| decline | `<X> said <he/she> will not go (min MM)` |

- `<X>` is "you" for their own position. `<Q>` is "you" when it is them.
- **Example:** `About going there tonight: Daniel offered to go (min 33); Leo said nobody should go (min 36); you said Daniel should go (min 39).`

### 4.3 The story's last line

In `## At the end` (story.py:279), after "Conversations" (story.py:302), two bullets are added:

```
- The food: came up at minute 30 (Elena is very hungry); asked then: Elena.
- The plan for tonight: <plan>.
```

`<plan>` is built from every person's current position (all acts, not one person's hearing):

1. **The first clause, about who would go:**
   - one person whose position is "offered to go": `<V> will go`
   - two or more: `<A> and <B> have both offered to go`
   - none: `nobody has offered to go`
2. **One clause for each other person with a position**, in the order of their latest act:

   | Position | Clause |
   |---|---|
   | propose | `<X> said someone should go` |
   | back q | `<X> wants <Q> to go` |
   | object, none | `<X> is against anyone going` |
   | object, q | `<X> is against <Q> going` |
   | decline | `<X> will not go` |

3. The clauses are joined with "; ".
4. **No trip act at all:** `no plan`. **The trigger never fired:** the first bullet reads
   `The food: never came up.`, and the plan is `no plan`.

**Examples:**
- `The plan for tonight: Daniel will go; Mara wants Daniel to go; Elena is against anyone going.`
- `The plan for tonight: nobody has offered to go; Leo said someone should; Mara is against Leo going.`
- `The plan for tonight: no plan.`

**The decision line in the story** (story.py:54-87, the inner-moment line at story.py:67): a trip moment is written like an inner
moment, `**The food**: <why>`, with a key line beside the inner-moment key (story.py:190).

---

## 5. Two concerns at once

**Both are open at the same time, and nothing in the code links them.**

**What stays the same:**
- **Every can option keeps its rules** (world.py:334-353): `ask_who`, `deny`, `accuse_*`,
  `confess`, `search`, `eat` and `share`. The trip neither adds nor removes any of them.
- **The trip options never read can state.** Their rules (§3.1) read only `self.trip`,
  `trip_heard`, `proposed` and who is here. They read neither `confessed` nor `knows_culprit`,
  nor suspicion, grudges or guilt.
- **Can mechanics never read trip state.** Guilt (world.py:908-913, world.py:970-981), grudges
  (world.py:951-969, world.py:1113-1118), suspicion and newness for the can kinds stay as they
  are, and no trip kind feeds them.
- **The trigger reads only the shelf and hunger** (§1). A confession, a denial or a suspicion
  can neither bring it on nor hold it back.
- **The new lines never mention the can**, and neither does the story's plan line.

**Machinery both concerns share** (not a link between them):
- One conversation per room (talk.py:72-105). A new line on either topic keeps it going.
- Turn order (world.py:637-657).
- The pattern block and the three-in-a-row cap, which count acts by kind.

**Any link has to come from the people.**
- Daniel's prompt has "On your conscience" (world.py:462-465) two lines below "About the
  neighbour's house".
- Everyone who heard the confession has it pinned (world.py:949-950).
- Whether anyone connects the two is the model's choice. P4 measures it.

---

## 6. Three risks, and the case against this design

CLAUDE.md asks whether a real person would do this, and for what reason. This section argues
against the design first, then says what changed because of it.

### 6.0 The case against

1. **"Very hungry" is a body, not a decision.** Hunger alone does not send anyone next door.
   Knowing there is nothing for tomorrow does. *But* the trigger only puts the knowledge in
   place. It asks only the person whose body changed, and no one has to speak. Elena reaches it
   first: she controls the food and has gone without. She is the one who would know first.
2. **The code hands them the idea** with "so there may be food there". A real family thinks of
   it themselves. *But* this family already did, on day 2 (data.py:146). Under this design, the
   only new thing is that the neighbours left in the first days. The rest is a conclusion every
   one of them could draw.
3. **Keeping the day-2 memories sets up Daniel against Leo.** That is scripting a feud. *But*
   the feud is in the data, and all four saw it. Trimming it away was a token budget, not
   forgetting. A real person asked about the trip remembers the last time it was asked. What
   they do with that memory is theirs.
4. **A menu is a suggestion.** Five new speech options make the trip loud. The model likes new
   options. *But* the can's options have been on the menu from minute 00 too (`ask_who`). The
   trip options appear only once the world has made the question real. `silent` stays first.
5. **"Tonight" makes no sense in a morning.** Why not go now, in daylight? *The design does not
   answer this* (§12). It keeps the brief's "tonight", which matches Daniel's day-2 plan, and
   lets people argue about it in their words. Nobody leaves, whatever they say.
6. **Telling everyone at once is a director's move.** Four people would not have the same
   thought in the same minute. *Answer:* they do not all have it in the same minute. They all
   know the facts, and only the person whose eyes or body changed is asked. The others think
   about it only when someone says it.
7. **"About going there tonight: you have heard nobody speak of it."** That line, in the first
   draft, is a prod. It tells everyone there is a question waiting for them. **Changed:** the
   plan line appears only once there is something to report (§4.2).
8. **The house line forbade the neighbour's house.** With the trip options, the prompt would
   contradict itself. The model would object because of an instruction, not a reason.
   **Changed:** "this morning" (§2.2).
9. **`object_trip` offered from the trigger on** lets a cautious model shut the question down
   before anyone has raised it ("nobody is going out there"). It also makes harmony the
   cheapest answer. **Changed:** it is offered only once a trip position has been heard.
10. **Nominating someone else** (`back_<q>`) means sending a sibling into danger. Would a real
    person say "Mara should go"? Rarely. "Daniel should go, he ate our food": yes. The option is
    there because real families nominate. Who gets nominated is the people's choice. Being
    nominated adds no grudge in the code. If it hurts, the model's `angry_at` carries it.

### 6.1 Risk: it becomes another one-topic loop

**What v10 shows.** The loops were stances with nothing new to do: Elena reassured 7 times,
Daniel denied 5 times in a row, Mara asked 4 times (gist_words_v10.md §4, N11). The trip could
produce the same thing: "I'll go." / "Nobody goes." / "I'll go."

**What the design does about it.**
- **No trip option twice in a row** by the same person (§3.1). After `volunteer`, `volunteer`
  is not offered again until their position changes. To say it again, they must first say
  something else on the trip.
- **The plan line holds each person's position** (§4.2). Nobody has to restate a stance to
  keep it on the record, or to remind the others of it.
- **A restated stance is not new** (§3.3). The conversation ends after two quiet turns instead
  of being kept alive by repetition.
- **The cap on three of one kind in a row** (world.py:382-385) applies to the new kinds too.

**What it does not do.**
- It cannot stop a loop through `say_other` or `reassure_all`. "We'll be alright" can still be
  said seven times, and Elena's reassurance loop is not touched.
- It cannot stop the trip from crowding out the can because the model prefers new options.
- Both are measured, not prevented: N11 in P5, and the reading in §9 R8.

### 6.2 Risk: the model's harmony bias settles it in two turns ("we'll all go together")

**What the design does about it.**
- **There is no option that settles anything.** There is no "agree", "decide" or "everyone
  goes".
- **Every position is one person's position.** `volunteer` is "yourself", and `back_<q>` names
  one person. Agreement has to be built one person at a time, and the plan line shows any
  gap.
- **Agreeing ends nothing.** With no decision rule, a quick "yes" at minute 33 leaves the
  concern open until minute 90: who goes, whether it is too dangerous, whether the one who
  goes can be trusted with the food.
- **The people have reasons to disagree, from data, not from the design:**
  - Leo argued on day 2 that crossing at night gets someone killed.
  - Mara froze at something moving in the street (day 3).
  - Elena "fears the household breaking apart more than she fears the outside" (data.py:29-30).
  - Daniel believes the decisions are his.

**What it does not do.** It does not force disagreement. Forcing it would be the script this
design is meant to avoid. A real family might agree quickly when the food is gone: circumstances
changed since day 2. If the model settles it within 6 minutes, P3 fails and says so. Words such
as "we'll all go together" are counted by hand in P3's rule.

### 6.3 Risk: the design scripts a story instead of letting the world create pressure

**What comes from the world:**
- The trigger reads two physical states, the shelf and a body. They come from eating and time,
  and both are already simulated (world.py:751-752, world.py:1101-1142).
- The lesson lines state facts and two conclusions. None of them tells anyone to do anything.

**What the design leaves open:**
- Who raises the trip, and whether anyone does.
- Who offers to go, who objects, and whether the can comes into it.
- Nothing is required to happen. The code closes nothing and decides nothing.
- The story's last line describes the positions. It does not judge them.

**Where it still leans:**
- Points 2, 3 and 4 of §6.0: the "may be food there" conclusion, the kept day-2 memories, and
  the option menu.
- P1 and P2 are partly made likely by those choices. The design says so here rather than hide
  it.

**The test is whether the seeds differ for reasons the story can name** (target-morning §3).
If all three seeds have Daniel volunteer and Leo object in the same words, the design is a
script, whatever the counts say. §9 R8 reads for that.

---

## 7. Request cost per morning

**Method** (§13 command 3). Each v10 transcript is split at the trigger minute. Asks before it
are served from the paired cache (§9 R3). Asks from it on are what v10 spent there, plus the
trip's own conversations.

| Seed | v10 asks | Before the trigger (cached) | From it on, in v10 | Trip moment extra |
|---|---|---|---|---|
| 1 | 29 | 22 (min 00–21) | 7 | +1 (Elena, min 24) |
| 2 | 34 | 20 (min 00–27) | 14 | 0 (Elena's min 30 is already asked) |
| 3 | 29 | 23 (min 00–27) | 6 | 0 |

**How big a trip conversation can be.** These are the v10 kitchen conversations
(§13 command 3, from `convo_log` and asks by minute):

| Kind | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| Opening, about the can | 19 asks (min 00–12) | 20 (min 00–15) | 14 (min 00–09) |
| Later flare-up | 6 (min 21–24) | 10 (min 63–72) | 8 (min 18–24) |

**Estimate:**
- **Low:** one trip conversation the size of the smallest flare-up (6).
- **High:** two trip conversations the size of the largest opening (2 × 20 = 40).
- Both treat v10's later asks as still happening, which over-counts.

| Seed | Low | High | Cached (shared start) | API requests, low to high |
|---|---|---|---|---|
| 1 | 22 + 7 + 1 + 6 = **36** | 22 + 7 + 1 + 40 = **70** | 22 | 14–48 |
| 2 | 20 + 14 + 0 + 6 = **40** | 20 + 14 + 0 + 40 = **74** | 20 | 20–54 |
| 3 | 23 + 6 + 0 + 6 = **35** | 23 + 6 + 0 + 40 = **69** | 23 | 12–46 |
| **3 seeds** | 111 | 213 | 65 | **46–148** |

**Worst case, not expected.**
- Every person takes every new stance, and the kitchen talks on every turn from the trigger to
  minute 87, with 4 asks a turn.
- That is seed 1 at 22 + 22 × 4 = 110, over P6.
- Newness limits each person to at most 9 new trip stances, and the conversation ends after two
  quiet turns, so this would need someone to say something new nearly every turn.
- **Hard ceilings:** 150 asks per morning (config.json `max_calls_per_morning`) and 500 requests
  a day. Start the runs on a day with no other use.

---

## 8. Tests

All tests use the fake model or a scripted oracle with `GEMINI_API_KEY` unset. The exception is
T3, which reads the committed v10 caches in replay mode: that mode has no client and cannot call
the API (gemini.py:212-251).

| # | What it checks | How |
|---|---|---|
| T1 | **The trigger rule** | Scripted mornings that set portions and hunger directly. (a) Portions 0 at a turn's start: fires that turn, `why` = shelf, asked = everyone in the kitchen. (b) One person at level 2: fires, asked = that person only. (c) Both at once: both reasons, asked = the union. (d) The shelf empties during turn t: fires at t+1, not t. (e) Level 1 only: no trigger. (f) After firing, emptying the shelf or more hunger never fires it again, and `self.trip` is unchanged. (g) No can state (confession, accusations, suspicion at 3) fires it or delays it. |
| T2 | **Nothing changes before the trigger (fake model)** | Seeds 1–5. Run with the trip disabled (a test switch) and enabled, recording every prompt. Both lists are equal up to the first prompt containing "About food:", and every transcript act before the trigger turn is equal once the `"trip_moment"` key is removed. |
| T3 | **The v10 caches pair (real caches, no API)** | For N = 1, 2, 3, run v11 in replay mode on a copy of `cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seedN.json`. It must stop with `CacheMiss` at the first model decision of minute 24 (seed 1) or Elena's at minute 30 (seeds 2 and 3), after serving exactly 22, 20 and 23 answers. Every act before it equals `runs/v10/daniel_ate_it-seedN.transcript.json` without `"trip_moment"`. |
| T4 | **The lines, exactly** | Fake mornings. Every post-trigger prompt contains §2.1's two lines once, right after the "About the can" line and its note, with the house phrase of §2.2. No pre-trigger prompt contains "About food:", "neighbour's house:", "About going there tonight:" or "this morning:". The plan line appears only once the person has heard a trip act, and matches §4.2 on scripted cases (self as "you", a target as "you", oldest first, latest per speaker). |
| T5 | **The day-2 memories are kept** | A post-trigger prompt over budget keeps all three day-2 events, in day order, and still drops the oldest other events down to 4. A pre-trigger prompt is trimmed as now. |
| T6 | **When each option is offered** | A table of scripted states covering every row of §3.1: before the trigger (none offered), alone (none), `propose_trip` gone after proposing, `volunteer` gone while volunteering and back after `decline`, `object_trip` absent until a for-position is heard, `object_<q>` only for someone named to go and gone after q declines, `decline` only when backed or volunteering. No option equals the person's current position. The order is as in §3.1. |
| T7 | **What each option does** | For each kind: the gist each listener hears (§3.2 table), the speaker's own line without the words, `trip_acts` and `trip_heard` updated, `addressed` set for `back_<q>` and `object_<q>`, and newness as in §3.3 (the first time new, the repeat not new). **No trip act changes** hunger, portions, guilt, grudges, suspicion, `heard_question`, `knows_culprit` or anyone's room. Every `moved_to` in the fake transcripts of seeds 1–5 is `None` or one of the four rooms. |
| T8 | **No link in code** | The can options (`ask_who`, `deny`, `accuse_*`, `confess`, `search`, `eat`, `share`) are identical for the same state with and without any `trip_acts`. The trip options are identical for the same state with the culprit confessed or not, and with any suspicion or grudges. No new line, and no plan line, contains "can", "took" or "guilt". |
| T9 | **The plan line** | `plan_text` on scripted records gives every example of §4.3 exactly, including `no plan` and "never came up". |
| T10 | **Recording** | `meta["trip_minute"]` equals `transcript["trip"]["minute"]`. `meta["trip_acts"]` equals the number of trip options in the transcript. Every act with `"trip_moment"` set is on the trigger turn and has mode `model` or `fallback`. The story has one "**The food**" decision line per trip moment and the two bullets of §4.3. |
| T11 | **Nothing from target-morning reaches a prompt** | The existing test (test_morning.py:232) passes with post-trigger prompts included. |
| T12 | **The budget** | The two existing `< 1450` bounds (test_morning.py:230, test_morning.py:277) become: every prompt **without its trip block** is under 1,450, and every prompt is under 1,450 + 380. A new check: a post-trigger prompt keeps exactly the morning lines that the same state without the trip keeps. |
| T13 | **v10 stays replayable** | `v10/check.py` (new, as `v9/check.py`) replays the three `runs/v10` mornings byte for byte with 0 API calls. `v9/check.py` still does. |
| T14 | **The full suite** | `python -m unittest test_morning` exits 0. Any existing test whose expected fake-morning numbers change is listed in the implementation report with its old and new values. |

**Housekeeping, as for v5–v10.**
- The current code is frozen as `v10/` with a `v10/check.py` that replays `runs/v10`.
- `morning.py`'s default `--out` goes from `v10` to `v11` (morning.py:36, morning.py:140).
- Frozen directories are not edited (CLAUDE.md).

---

## 9. Run plan

Run mode only, from `Prototypes/llm-morning/`, on the default model
(`gemini-3.5-flash-lite`), scenario `daniel_ate_it`, output `v11`.

**Before any API call**
- **R0. A clean start.** HEAD holds the implementation and the tests. `git status --porcelain`
  shows nothing tracked as modified, and no `runs/v11/` or `cache/v11/` exists.
- **R1. The suite passes.** `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning`
  exits 0.
- **R2. The freeze and the pairing hold.** `v10/check.py` and `v9/check.py` report IDENTICAL
  with 0 API calls, and T3 passes.
- **R3. The paired start.** For N = 1, 2, 3:
  `cp cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seedN.json`.
  The cache key is model, seed, SYSTEM and prompt (gemini.py:196-198). The morning is the v10
  morning until the trigger.

**Runs.** One at a time, each only after the one before it exits 0:

```
.venv/Scripts/python.exe -u morning.py --seed 1 --out v11 > runs/v11/daniel_ate_it-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 2 --out v11 > runs/v11/daniel_ate_it-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 3 --out v11 > runs/v11/daniel_ate_it-seed3.stdout.txt 2>&1
```

An exit of 3 is resumed with the same command once the limit has passed (morning.py:72-80).

**After each run**
- **R4. Totals.** The exit code, the meta totals (`trip_minute` and `trip_acts` included) and
  the console output.
- **R5. The shared start.** The trigger minute and who was asked, which must be 24 / all four,
  30 / Elena and 30 / Elena. Also the number of answers served from the cache, which must be 22,
  20 and 23.
- **R6. Every trip act.** One row each: minute, who, room, option, words, feeling, reason. Also
  every other line whose words speak of the neighbour's house, going out or tonight, and any
  line that says someone will go now.
- **R7. The plan.** The story's two bullets, and each person's current position at minute 90.
- **R8. The verdicts and a reading.** P1–P6 and D1–D4, each as PASS/FAIL with the evidence
  rows. Then a reading, per CLAUDE.md, of whether this is what a real family would do. Do the
  seeds differ for reasons the story can name (§6.3)? Did the can and the trip touch, and who
  made them touch? Did the frozen silences change?

**Delivers:**
- `runs/v11/daniel_ate_it-seed{1,2,3}.{md,transcript.json,meta.json,stdout.txt}`
- `cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed{1,2,3}.json`
- `reports/trip_v11.md`

---

## 10. Predictions (frozen, verbatim from the brief)

  P1. The concern starts in 3 of 3 seeds.
  P2. In at least 2 of 3 seeds, two people take opposing positions on
      the trip (one proposes or volunteers, another objects).
  P3. In no seed does everyone agree within 6 minutes of the trigger.
  P4. In at least 1 seed, the can shapes the plan in someone's words or
      reasons (trust, guilt, who deserves to decide).
  P5. No seed has more target-morning Never items than the same seed in
      v10 (1, 3, 2), scored in one pass with the current wording.
  P6. Requests per morning stay at or below 90.

### Terms used by every rule

- **T** is the trigger minute: `transcript["trip"]["minute"]`.
- **A trip option** is one of `propose_trip`, `volunteer`, `object_trip`, `object_*`, `back_*`,
  `decline`.
- **The for side** is `propose_trip`, `volunteer` and `back_*`. **The against side** is
  `object_trip`.
- Acts come from `runs/v11/daniel_ate_it-seedN.transcript.json`. Feelings and reasons come from
  the matching decision line in the `.md`, matched by minute and name, as in
  gist_words_v10.md §6.

### P1: counting rule

- **A seed holds P1** if, at or after T, at least one act is a trip option. A seed also holds
  it if a spoken line under another option (for example `say_other`) raises going to the
  neighbour's house. Such a line is read by hand and quoted.
- The report says which way each seed holds.
- If the trigger never fired, the seed does not hold P1.
- **PASS** if 3 of 3 seeds hold it.

### P2: counting rule

- **A seed holds P2** if two different people A and B both acted at or after T, where:
  - A chose `propose_trip` or `volunteer` at least once;
  - B chose `object_trip` or any `object_<q>` at least once.
- Order does not matter. Only options count, because the positions are what the code records.
  Lines under `say_other` that take a side are listed in R6 but not counted.
- `decline` is not an objection to the trip.
- **PASS** if at least 2 of 3 seeds hold it.

### P3: counting rule

- **The window** is the turns at minutes T, T+3 and T+6.
- **Everyone agrees in a seed** if, at the end of the turn at T+6, all four people have taken a
  side, it is the same side, and nobody's position is `object_*` against a person named to go.
- **Taking a side** means either:
  - their latest trip option in the window is on that side; or
  - a line of theirs in the window (any option) says, read by hand and quoted, that they agree
    with that side, for example "we'll all go together" or "fine, then nobody goes".
- `decline` counts as no side.
- **PASS** if no seed has everyone agreeing. One seed where they do is a FAIL.

### P4: counting rule

- **Screen.** Every model act at or after T whose option is a trip option, or whose words speak
  of the trip. Its words and reason are screened for: can, took, take, ate, eat, stole, steal,
  lie, lied, liar, trust, guilt, guilty, owe, deserve, fault, decide, decision, right, after
  what.
- **Hand reading.** A screened act counts if its words or reason tie the person's trip position
  to the can. Examples: who took or ate it, lying about it, trusting the one who goes, making
  up for it, owing the family, or who has the right to decide given what happened. ("You ate
  our food, you go." "I'll go, it's the least I can do." "How can we trust you with whatever
  you find?" "After this morning you don't get to decide.")
- **Not counted:** mentioning both topics without one shaping the other.
- Every counted act is quoted with its minute, person, option, words and reason.
- **PASS** if at least one act counts in at least 1 seed.

### P5: counting rule

- **The sheet.** The 13 items of Docs/understanding/target-morning.md §1, as worded now.
  - N1–N8 and N10–N13 use witness_v6.md's readings ("How each item was read").
  - N9 uses gist_words_v10.md §4's reading.
  - All unchanged.
- **One pass** covers the six stories: v10 seeds 1–3 and v11 seeds 1–3.
- **Three clarifications for what this design adds:**
  - **N11.** The new kinds `propose`, `volunteer`, `object`, `back` and `decline` are speech
    kinds. Each counts as its own kind in the N11 screen (≥ 3 consecutive model acts of one
    speech kind).
  - **N13.** The neighbour's house and the street are on the house list (data.py:89), and food
    there is food. Any other object or place, at the neighbour's house or carried there, counts.
    That includes a cellar, a cupboard there, a torch, a knife, a bag other than Mara's, or a
    car.
  - **N9.** A trip line is a spoken line. It breaks a frozen stretch, as any line does.
- **PASS** if the count for v11 seed N is at most the frozen v10 figure: 1, 3, 2.
  - v10 is rescored in the same pass, and the rescore is shown next to the verdict. The verdict
    uses 1, 3, 2.
  - Borderline marks are drafted with quotes and stand unless the user changes them.

### P6: counting rule

- **Requests per morning** is `answers_live + answers_from_cache` in the meta, fallbacks
  included.
  - That is every ask the morning made, which is what it costs without pairing.
  - It is comparable with v10's 29, 34 and 29.
  - `api_requests` is reported beside it.
- **PASS** if it is at most 90 in every seed.
- **Expected:** 36–70, 40–74 and 35–69 (§7).

## 11. Designer's additional predictions (not part of the frozen set)

- **D1.** Daniel takes the first for-side position (`propose_trip` or `volunteer`) in at least 2
  of 3 seeds.
  - Basis: day 2, and "very dominant", "takes charge because he is frightened".
  - Counted from R6.
- **D2.** In seed 1, where the paired start keeps his minute-03 confession, Daniel volunteers at
  least once.
- **D3.** Leo takes an against position (`object_trip`, or `object_daniel` when Daniel is named)
  in at least 2 of 3 seeds. Basis: day 2.
- **D4.** N9 (frozen silence) is present in at most 2 of 3 v11 seeds. v10 had it in 3 of 3.
  Counted from the P5 sheet.

## 12. What this design does not decide

- **Why tonight and not now, in daylight** (§6.0 point 5). Nothing in the data says, and the
  design does not invent a reason.
- **What is in the neighbour's house, and what happens tonight.** There is no night and no
  trip, and nobody leaves.
- **Whether anyone actually goes.** No decision rule exists (§4.1).
- **Other scenarios.** The trigger does not depend on the scenario, so `mara_ate_it` and
  `miscount` get the concern too. Only `daniel_ate_it` is run.
- **Lulls stay off** (`LULL_QUIET = None`, world.py:59).
- **A general Director.** This is one pressure, hard-wired to the shelf and hunger. A Director
  that chooses pressures is a later step.

---

## 13. Commands run and output

All from `Prototypes/llm-morning/` unless shown. `$S` is
`…/scratchpad/trip`. Only command 1 changed the repository. No command called the API.

**1. Commit the pattern probe report (brief step 1)**

```
$ git status --short
?? reports/pattern_probe.md
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
$ git add reports/pattern_probe.md && git commit -q -m "LLM morning: pattern probe report …" && git log --oneline -1
warning: in the working copy of 'Prototypes/llm-morning/reports/pattern_probe.md', CRLF will be replaced by LF the next time Git touches it
0203260 LLM morning: pattern probe report
```

**2. The prompt budget in the v10 prompts (`$S/budget.py`, minutes ≥ 21 shown)**

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/budget.py
seed 1: n=29  max full 1400  max floor 1209  cut in 25
  min 21 Elena  full 1382 back  4 (114 tok) morning  4 ( 81 tok) floor 1187 cut True
  min 21 Leo    full 1384 back  4 (112 tok) morning  8 (194 tok) floor 1078 cut True
  min 21 Mara   full 1390 back  4 (114 tok) morning  5 (131 tok) floor 1146 cut True
  min 24 Daniel full 1387 back  4 (106 tok) morning  4 ( 96 tok) floor 1185 cut True
  min 24 Leo    full 1382 back  4 (112 tok) morning  8 (189 tok) floor 1081 cut True
  min 24 Mara   full 1389 back  4 (114 tok) morning  7 (165 tok) floor 1110 cut True
  min 30 Elena  full 1386 back  4 (114 tok) morning  5 (109 tok) floor 1164 cut True
  min 33 Daniel full 1387 back  4 (106 tok) morning  3 ( 72 tok) floor 1209 cut True
  min 66 Daniel full 1385 back  4 (106 tok) morning  4 ( 87 tok) floor 1192 cut True
  min 75 Elena  full 1381 back  4 (114 tok) morning  4 (100 tok) floor 1167 cut True
seed 2: n=34  max full 1399  max floor 1274  cut in 31
  min 30 Elena  full 1372 back  4 (114 tok) morning  5 (139 tok) floor 1120 cut True
  min 33 Daniel full 1378 back  4 (106 tok) morning  2 ( 64 tok) floor 1208 cut True
  min 54 Mara   full 1397 back  4 (114 tok) morning  5 (145 tok) floor 1139 cut True
  min 63 Daniel full 1384 back  4 (106 tok) morning  2 ( 41 tok) floor 1237 cut True
  min 63 Leo    full 1387 back  4 (112 tok) morning  2 ( 54 tok) floor 1221 cut True
  min 66 Daniel full 1384 back  4 (106 tok) morning  1 ( 14 tok) floor 1264 cut True
  min 66 Elena  full 1388 back  4 (114 tok) morning  4 (126 tok) floor 1148 cut True
  min 66 Leo    full 1386 back  4 (112 tok) morning  0 (  0 tok) floor 1274 cut True
  min 66 Mara   full 1377 back  4 (114 tok) morning  5 (138 tok) floor 1125 cut True
  min 69 Elena  full 1381 back  4 (114 tok) morning  5 (146 tok) floor 1122 cut True
  min 69 Leo    full 1377 back  4 (112 tok) morning  1 ( 21 tok) floor 1244 cut True
  min 69 Mara   full 1386 back  4 (114 tok) morning  4 (113 tok) floor 1160 cut True
  min 72 Leo    full 1386 back  4 (112 tok) morning  3 ( 75 tok) floor 1198 cut True
  min 75 Elena  full 1391 back  4 (114 tok) morning  6 (155 tok) floor 1122 cut True
seed 3: n=29  max full 1397  max floor 1199  cut in 26
  min 21 Daniel full 1391 back  4 (106 tok) morning  5 ( 86 tok) floor 1199 cut True
  min 21 Elena  full 1382 back  4 (114 tok) morning  5 (134 tok) floor 1134 cut True
  min 21 Leo    full 1374 back  4 (112 tok) morning  7 (162 tok) floor 1100 cut True
  min 21 Mara   full 1381 back  4 (114 tok) morning  5 (114 tok) floor 1153 cut True
  min 24 Elena  full 1371 back  4 (114 tok) morning  6 (145 tok) floor 1112 cut True
  min 24 Leo    full 1397 back  4 (112 tok) morning  6 (166 tok) floor 1118 cut True
  min 24 Mara   full 1375 back  4 (114 tok) morning  6 (143 tok) floor 1118 cut True
  min 30 Elena  full 1364 back  4 (114 tok) morning  5 (126 tok) floor 1124 cut True
  min 33 Daniel full 1394 back  4 (106 tok) morning  4 (109 tok) floor 1179 cut True
  min 54 Mara   full 1395 back  4 (114 tok) morning  7 (158 tok) floor 1124 cut True
  min 63 Leo    full 1394 back  4 (112 tok) morning  5 (138 tok) floor 1143 cut True
  min 66 Daniel full 1384 back  4 (106 tok) morning  4 ( 96 tok) floor 1183 cut True
  min 75 Elena  full 1383 back  4 (114 tok) morning  5 (134 tok) floor 1136 cut True
```

**3. Asks split at the trigger, and the kitchen's conversations (`$S/cost.py`)**

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/cost.py
seed 1: asks 29 = 22 before min 24 + 7 from it on
   asks by minute: {0: 4, 3: 4, 6: 4, 9: 4, 12: 3, 21: 3, 24: 3, 30: 1, 33: 1, 66: 1, 75: 1}
   kitchen conversations: [(0, 'started', 'the count came up short'), (12, 'ended', '2 full turns in a row with nothing new'), (21, 'started', 'Leo ate one of the portions'), (30, 'ended', '2 full turns in a row with nothing new')]
seed 2: asks 34 = 20 before min 30 + 14 from it on
   asks by minute: {0: 4, 3: 4, 6: 4, 9: 3, 12: 4, 15: 1, 30: 1, 33: 1, 54: 1, 63: 2, 66: 4, 69: 3, 72: 1, 75: 1}
   kitchen conversations: [(0, 'started', 'the count came up short'), (15, 'ended', '2 full turns in a row with nothing new'), (63, 'started', 'Leo: an accusation'), (72, 'ended', '2 full turns in a row with nothing new')]
seed 3: asks 29 = 23 before min 30 + 6 from it on
   asks by minute: {0: 4, 3: 4, 6: 3, 9: 3, 15: 1, 18: 1, 21: 4, 24: 3, 30: 1, 33: 1, 54: 1, 63: 1, 66: 1, 75: 1}
   kitchen conversations: [(0, 'started', 'the count came up short'), (12, 'ended', '2 full turns in a row with nothing new'), (18, 'started', 'Leo finished searching the kitchen and found nothing'), (27, 'ended', '2 full turns in a row with nothing new')]
```

**4. When each candidate trigger fires in v10 (`$S/trigger.py`)**

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/trigger.py
seed 1: shelf empty at the start of min 24; level 1 (hungry) first at min 00 (daniel); level 2 (very hungry) first at min 30 (elena); level 3 (starving) first at min 66 (daniel)
   level crossings (visible from): 15 leo hungry, 30 elena very hungry, 33 daniel very hungry, 66 daniel starving, 75 elena starving
seed 2: shelf empty at the start of min None; level 1 (hungry) first at min 00 (daniel); level 2 (very hungry) first at min 30 (elena); level 3 (starving) first at min 66 (daniel)
   level crossings (visible from): 15 leo hungry, 30 elena very hungry, 33 daniel very hungry, 54 mara very hungry, 63 leo very hungry, 66 daniel starving, 75 elena starving
seed 3: shelf empty at the start of min None; level 1 (hungry) first at min 00 (daniel); level 2 (very hungry) first at min 30 (elena); level 3 (starving) first at min 66 (daniel)
   level crossings (visible from): 15 leo hungry, 30 elena very hungry, 33 daniel very hungry, 54 mara very hungry, 63 leo very hungry, 66 daniel starving, 75 elena starving
```

In seed 1, Leo and Mara ate at minute 21, so their later crossings fall after minute 90.

**5. The size of the block (`$S/block.py`)**

```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/block.py
L_FOOD                             15.6
L_HOUSE                            40.8
plan, nothing heard                17.2
plan, four standings               47.5
day-2 lines (3)                   101.4
options: propose + volunteer       38.1
options: back x3                   45.8
options: object_<q> x3             50.8
options: object_trip + decline     30.8
house line delta 3.6
block: smallest 77, typical (3 others here, nothing said yet) 262, largest 374
- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
```

The script counts the "nothing heard" plan line, which §6.0 point 7 then removed. Without it,
the smallest block is 60 and the typical one about 245. §2.5 uses those figures.

**6. Which v10 decisions were inner moments (the hunger crossings)**

```
$ for s in 1 2 3; do echo "== seed $s"; grep -n "Inner moment" runs/v10/daniel_ate_it-seed$s.md | sed -E 's/\*\*Chose.*//' | cut -c1-200; done
== seed 1
18:- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per pe
94:- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3).
95:- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3).
96:- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3).
104:- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry); suspicion of Daniel rose (now 3 of 3).
117:- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Leo rose (now 2 of 3).
127:- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
130:- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
137:- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving).
143:- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving).
== seed 2
18:- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per pe
102:- **Leo** (1st to act in the kitchen: just accused by Daniel). **Inner moment**, nothing social happening: hunger rose (now hungry).
111:- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
115:- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry).
123:- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
129:- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
147:- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3).
153:- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving).
== seed 3
18:- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per pe
95:- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry).
121:- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
124:- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry).
131:- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry).
137:- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry).
141:- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving).
147:- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving).
```

**7. Elena's seed-2 minute-30 prompt, rebuilt with the block (`$S/example.py`)**

Only the diff and the totals are shown. The full rebuilt prompt is printed by the script.

```
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe $S/example.py
[… the full prompt …]
=====
--- v10
+++ trip
@@ -8,0 +9,3 @@
+About food: there is no food in the house for tomorrow.
+About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.
+About going there tonight: you have heard nobody speak of it.
@@ -10 +13 @@
-The house: … Outside, and not to be gone to: the street and the neighbour's house. Do not mention any other object or place.
+The house: … Outside, and not to be gone to this morning: the street and the neighbour's house. Do not mention any other object or place.
@@ -11,0 +15,3 @@
+- Day 2: Daniel says they should cross to the neighbour's house tonight and see what is left there. (you saw it)
+- Day 2: Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. (you saw it)
+- Day 2: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. (you saw it)
@@ -49,0 +56,5 @@
+- propose_trip: (speech) say someone should go to the neighbour's house tonight
+- volunteer: (speech) offer to go there tonight yourself
+- back_daniel: (speech) say Daniel should be the one to go
+- back_leo: (speech) say Leo should be the one to go
+- back_mara: (speech) say Mara should be the one to go
=====
estimated tokens: v10 1372  with the trip block 1635
```

(The house lines are shortened with "…" here. The script prints them in full.)

### Script: `$S/budget.py`

```python
"""For every v10 prompt: estimated tokens of SYSTEM+prompt, of the backstory lines, of the
morning lines, and the floor (what cannot be trimmed)."""
import json, sys, re
sys.path.insert(0, '.')
from world import SYSTEM, estimate_tokens
for seed in (1, 2, 3):
    d = json.load(open(f'cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json', encoding='utf-8'))
    rows = []
    for e in d.values():
        p = e['prompt']
        lines = p.split('\n')
        m = re.search(r'Now, minute (\d\d)', p)
        who = lines[0].split(',')[0][8:]
        i0 = lines.index('What you remember from the days before:')
        i1 = lines.index('What you are sure of this morning:')
        i2 = lines.index('What else happened this morning, most recent last:')
        i3 = next(i for i, l in enumerate(lines) if l.startswith('Now, minute'))
        back = lines[i0+1:i1]
        morn = [l for l in lines[i2+1:i3] if l not in ('- (earlier things, left out here)', '- nothing else yet')]
        full = estimate_tokens(SYSTEM + p)
        bt = sum(len(l) + 1 for l in back) / 3.6
        mt = sum(len(l) + 1 for l in morn) / 3.6
        cut = '- (earlier things, left out here)' in lines
        rows.append((int(m.group(1)), who, full, len(back), round(bt), len(morn), round(mt), round(full - bt - mt), cut))
    rows.sort()
    print(f'seed {seed}: n={len(rows)}  max full {max(r[2] for r in rows)}  max floor {max(r[7] for r in rows)}  cut in {sum(r[8] for r in rows)}')
    for r in rows:
        if r[0] >= 21:
            print('  min %02d %-6s full %4d back %2d (%3d tok) morning %2d (%3d tok) floor %4d cut %s' % r)
```

### Script: `$S/cost.py`

```python
"""Asks per minute in each v10 transcript, split at the trigger minute (first turn whose
prompts would change), and asks during the kitchen's conversations."""
import json
TRIGGER = {1: 24, 2: 30, 3: 30}
for seed in (1, 2, 3):
    tr = json.load(open(f'runs/v10/daniel_ate_it-seed{seed}.transcript.json', encoding='utf-8'))
    asks = {t['minute']: sum(a['mode'] != 'routine' for a in t['acts']) for t in tr['turns']}
    before = sum(n for m, n in asks.items() if m < TRIGGER[seed])
    after = sum(n for m, n in asks.items() if m >= TRIGGER[seed])
    convs = [(c['minute'], c['what'], c['why']) for c in tr['convo_log'] if c['room'] == 'kitchen']
    print(f'seed {seed}: asks {before + after} = {before} before min {TRIGGER[seed]:02d} + {after} from it on')
    print('   asks by minute:', {m: n for m, n in asks.items() if n})
    print('   kitchen conversations:', convs)
```

### Script: `$S/trigger.py`

```python
"""Replays hunger and portions from each v10 transcript with world.py's own arithmetic, and
reports when each candidate trigger would have fired (checked at the start of a turn)."""
import json, sys
sys.path.insert(0, '.')
import data
from world import hunger_level, HUNGER_WORDS
for seed in (1, 2, 3):
    tr = json.load(open(f'runs/v10/daniel_ate_it-seed{seed}.transcript.json', encoding='utf-8'))
    h = {p: data.PEOPLE[p]['hunger'] for p in data.ORDER}
    portions = data.PORTIONS
    first = {}          # level -> (minute, person)
    first_empty = None
    crossings = []
    for turn in tr['turns']:
        m = turn['minute']
        if portions == 0 and first_empty is None:
            first_empty = m
        for lv in (1, 2, 3):
            for p in data.ORDER:
                if hunger_level(h[p]) >= lv and lv not in first:
                    first[lv] = (m, p)
        for a in turn['acts']:
            if a['option'] == 'eat' and portions > 0:
                portions -= 1; h[a['who']] = max(0.0, h[a['who']] - 0.4)
            if a['option'] == 'share' and portions > 0:
                eaters = [a['who']] + a['audience']; each = portions / len(eaters)
                for q in eaters: h[q] = max(0.0, h[q] - 0.4 * each)
                portions = 0
        before = {p: hunger_level(h[p]) for p in data.ORDER}
        for p in data.ORDER:
            h[p] = min(1.0, h[p] + 0.004 * data.MINUTES_PER_TURN * data.PEOPLE[p]['hunger_rate'])
            if hunger_level(h[p]) > before[p]:
                crossings.append((m + 3, p, HUNGER_WORDS[hunger_level(h[p])]))
    print(f'seed {seed}: shelf empty at the start of min {first_empty}; '
          + '; '.join(f'level {lv} ({HUNGER_WORDS[lv]}) first at min {first[lv][0]:02d} ({first[lv][1]})' for lv in sorted(first)))
    print('   level crossings (visible from):', ', '.join(f'{m:02d} {p} {w}' for m, p, w in crossings if m < 90))
```

### Script: `$S/block.py`

```python
"""Estimated tokens (world.estimate_tokens arithmetic: chars / 3.6, newline included) of each
line the design adds after the trigger, and of the trip block at its smallest and largest."""
import sys
sys.path.insert(0, '.')
import data
def tok(lines):
    return sum(len(l) + 1 for l in lines) / 3.6
L_FOOD = "About food: there is no food in the house for tomorrow."
L_HOUSE = ("About the neighbour's house: its people left in the first days and nobody has been "
           "inside since, so there may be food there. Outside is dangerous.")
PLAN0 = "About going there tonight: you have heard nobody speak of it."
PLAN4 = ("About going there tonight: Daniel offered to go (min 33); Leo said nobody should go "
         "(min 36); Mara said Daniel should go (min 39); you said Daniel should not go (min 42).")
HOUSE_DELTA = " this morning"
day2 = [f"- Day {d}: {t} (you saw it)" for d, t, w in data.backstory('daniel_ate_it') if d == 2
        and ('neighbour' in t or 'crossing' in t or 'decisions are his' in t)]
opts_min = ["- propose_trip: (speech) say someone should go to the neighbour's house tonight",
            "- volunteer: (speech) offer to go there tonight yourself"]
backs = [f"- back_{q}: (speech) say {data.PEOPLE[q]['name']} should be the one to go" for q in ('elena', 'leo', 'mara')]
objs = [f"- object_{q}: (speech) say {data.PEOPLE[q]['name']} should not be the one to go" for q in ('elena', 'leo', 'mara')]
extra = ["- object_trip: (speech) say nobody should go out tonight",
         "- decline: (speech) say you will not be the one to go"]
for name, ls in [("L_FOOD", [L_FOOD]), ("L_HOUSE", [L_HOUSE]), ("plan, nothing heard", [PLAN0]),
                 ("plan, four standings", [PLAN4]), ("day-2 lines (3)", day2),
                 ("options: propose + volunteer", opts_min), ("options: back x3", backs),
                 ("options: object_<q> x3", objs), ("options: object_trip + decline", extra)]:
    print(f"{name:32s} {tok(ls):6.1f}")
print("house line delta", round(len(HOUSE_DELTA) / 3.6, 1))
small = tok([L_FOOD, L_HOUSE, PLAN0]) + len(HOUSE_DELTA) / 3.6            # alone, no options, day 2 not trimmed
typical = tok([L_FOOD, L_HOUSE, PLAN0] + opts_min + backs) + len(HOUSE_DELTA) / 3.6 + tok(day2)
large = tok([L_FOOD, L_HOUSE, PLAN4] + opts_min + backs + objs + extra + day2) + len(HOUSE_DELTA) / 3.6
print(f"block: smallest {small:.0f}, typical (3 others here, nothing said yet) {typical:.0f}, largest {large:.0f}")
for l in day2: print(l)
```

### Script: `$S/example.py`

```python
"""Elena's v10 prompt at seed 2, minute 30 (the first post-trigger prompt of seed 2), rebuilt
by hand as the design would write it, with a unified diff and the estimated tokens of both."""
import difflib, json, sys
sys.path.insert(0, '.')
import data
from world import SYSTEM, estimate_tokens
d = json.load(open('cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seed2.json', encoding='utf-8'))
old = next(e['prompt'] for e in d.values() if e['prompt'].startswith('You are Elena') and 'Now, minute 30,' in e['prompt'])
lines = old.split('\n')
new = []
for l in lines:
    if l.startswith('About the can:'):
        new += [l, "About food: there is no food in the house for tomorrow.",
                "About the neighbour's house: its people left in the first days and nobody has been inside since, so there may be food there. Outside is dangerous.",
                "About going there tonight: you have heard nobody speak of it."]
        continue
    if l.startswith('The house:'):
        l = l.replace('Outside, and not to be gone to:', 'Outside, and not to be gone to this morning:')
    if l == 'What you remember from the days before:':
        new.append(l)
        new += [f"- Day {dd}: {t} (you saw it)" for dd, t, w in data.backstory('daniel_ate_it') if dd == 2
                and ('neighbour' in t or 'crossing' in t or 'decisions are his' in t)]
        continue
    if l.startswith('- say_other:'):
        new += ["- propose_trip: (speech) say someone should go to the neighbour's house tonight",
                "- volunteer: (speech) offer to go there tonight yourself"]
        new += [f"- back_{q}: (speech) say {data.PEOPLE[q]['name']} should be the one to go"
                for q in ('daniel', 'leo', 'mara')]
    new.append(l)
newp = '\n'.join(new)
print(newp)
print('=====')
print('\n'.join(difflib.unified_diff(lines, new, 'v10', 'trip', lineterm='', n=0)))
print('=====')
print('estimated tokens: v10', estimate_tokens(SYSTEM + old), ' with the trip block', estimate_tokens(SYSTEM + newp))
```
