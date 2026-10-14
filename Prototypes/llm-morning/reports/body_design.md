# Design: the promise at bedtime and the body's food moment (`daniel_ate_it`, v13)

Mode: design. No code was written or changed, and no API was called.
- Before this file, `reports/framing_probe.md` was committed on its own as `6747b83`.
  `reports/model_probe.md` was already committed (`973f9d2`).
- Paths are relative to `Prototypes/llm-morning/`.
- Scratch scripts are in the session scratchpad (`$S` = `…/scratchpad/body`). They read the repo
  and write nothing in it, and they are reproduced in §9 with their output.

**Why two changes** (framing_probe.md):
- **The promise.** A line that restated seed 1 Daniel's offer sent him next door 6 of 6 times.
  Without it he went 0 of 6.
  - But the line also said "The house is asleep". Daniel cannot know that: he is asked first at
    bedtime (`night.py:197-216`), and in v12 his roommate Leo lay awake watching for exactly this
    (night_v12 §2).
- **Food.** Food framing failed in every form tried, 0 of 72.
  - In v12, seeds 2 and 3 started day 2 with 1 and 2 portions on the shelf and everyone
    starving. Nobody ate, shared or proposed sharing in 30 turns (night_v12 §1, §8).
  - The R9 reading put it plainly: "the morning ignores the food on the shelf" (night_v12 §9).
  - So the code makes the moment, and the person chooses what to do in it.

**The two changes in one paragraph each.**
1. **The promise line.** At bedtime, a person whose latest position on the trip is to go gets
   one true line before their options: they said they would go, and if they are going, it is now.
   It says nothing about who is asleep. Nobody else's prompt changes.
2. **The food moment.** On day 2, a starving person in the kitchen with food on the shelf and
   someone else present may have a food moment when their turn comes.
   - The chance per turn depends on how long since they last ate and how impulsive they are.
   - The moment replaces their decision for the turn. Their options are food only: eat a
     portion, give one to a named person present, or share out what is left among everyone
     present.
   - A person handed a portion answers at once: eat it, or refuse it and put it back.

**Nothing else changes.** Day 1, the gap, the night's other prompts and rules, the outcome
tables (§4 of night_design.md), the carry-in, the day-2 options outside a moment, the system
texts and the budget are all as in v12.

---

## 1. The promise line

### Who gets it

- **At bedtime only** (night_design §3.2): the person's own latest position on the trip has the kind
  `volunteer`.
  - Their latest position is `p.trip_heard[p.id]` (`world.py:1377-1389`).
  - On day 1 that is the option `volunteer`; on day 2, `volunteer` or `still_going`
    (`world.py:509-537`).
- **Not** to someone who was only named by others (`back`/`send_*`): they never promised.
- **Not** to someone who offered and later took another position, for example `decline` or
  `object_trip`: their latest word was not to go.
- **Not** in the reaction or answer asks (§3.4, §3.5 of night_design). Those people are
  already up and facing someone.

**In the v12 states** (§9, command 3), the line goes to one person in three seeds:

| Seed | Latest day-1 position of each | Gets the line |
|---|---|---|
| 1 | Daniel `volunteer` (min 36); Leo, Mara `object_trip` (39); Elena `object_trip` (42) | **Daniel** |
| 2 | Daniel `object_trip` (51); Elena `decline` (51); Leo, Mara `object_elena` (48) | nobody |
| 3 | Leo `decline` (69); Daniel `object_leo` (66); Elena, Mara `object_trip` (66) | nobody |

### The exact line, and where it goes

It is the last `Now` line, after the shelf line and just before `Your options:`. That is where
the framing probe's line sat. Seed 1, Daniel:

```
Now it is night. The afternoon and evening passed in the house. Nobody ate.
Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the back room.
You are in the brothers room, in your bed. Leo is in his bed.
The kitchen is dark. The shelf holds 0 portions.
You said you would go to the neighbour's house tonight. If you are going, it is now.
Your options:
- sleep: go to sleep
- lie_awake: lie awake in your bed and listen
- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out without you knowing
- go_next_door: wait until the others are asleep, then go out by the front door to the neighbour's house
```

The line, alone: `You said you would go to the neighbour's house tonight. If you are going, it is now.`

**Why each part is true for that person:**
- **"You said you would go to the neighbour's house tonight."**
  - `volunteer` is a speech option labelled "offer to go there tonight yourself"
    (`world.py:493`, `world.py:521`), so the person said it aloud, for tonight.
  - It is their latest word on it. Seed 1 Daniel at minute 36: "I will go to the neighbour's
    house tonight myself because I am the eldest." (§9, command 3).
  - `still_going` is "say you still mean to go there tonight". It is the same claim.
- **"If you are going, it is now."**
  - The bedtime answer is the only time the night asks whether a person goes. Afterwards only
    those who notice something are asked (`night.py:197-224`).
  - "Now" is the point at which they decide, not a time on a clock. The option itself still
    says "wait until the others are asleep".
- **What it leaves out.** It says nothing about who is asleep, who agreed, or whether going is
  right.
  - The objections stay where they already were, in the same prompt: "About going there
    tonight: you offered to go (min 36); Mara said nobody should go (min 39); Leo said nobody
    should go (min 39); Elena said nobody should go (min 42)."

**The difference from the probed line.** framing_probe P-B was this line with "The house is
asleep." between the two sentences. **This exact line has not been sent to the model.** B2 (§6)
is its first test.

---

## 2. The food moment

### 2.1 When it can fire

When a person's turn to act comes on day 2 (`decide`, `world.py:1132-1163`), the rules check, in
this order:

| # | Condition | Why |
|---|---|---|
| F1 | It is day 2 (`day == 5`). Never on day 1, never in the night. | Day 1 replays the v11 cache byte for byte. Eating in the night stays out for night_design §7.9's reason: it would replay the can on day 2. |
| F2 | They are in the kitchen, and the shelf holds at least 1 portion. | The kitchen is the only room with food (`data.py:64`). |
| F3 | At least one other person is in the kitchen at that moment. | §3 point 7: alone, the choice is "eat" only, and the code would be eating for them. |
| F4 | Their hunger level is 3, "starving" (hunger ≥ 0.85, `world.py:124-125`). | The brief: a starving person. "Very hungry" people are left to the ordinary options. |
| F5 | They have eaten nothing this morning: no portion, no part of a share, no portion given to them. | A portion takes 0.4 off hunger (`world.py:1514`). After eating they are no longer the person the rule is about, even when a small share leaves them starving. |
| F6 | They have had no food moment in the last 30 minutes (10 turns). | §2.3. |
| F7 | Nobody in the house has had a food moment this turn. | §2.3. |
| F8 | They are not answering an aside (`world.py:1028-1040`) or a give (§2.5). | Those answers are already fixed. |
| F9 | The draw `u = random.Random(f"{seed}:day2:food:{t}:{pid}").random()` is under their chance (§2.2). | Each person and turn has its own string, so no draw depends on order. |

**It fires whatever else is happening.** It replaces their decision for the turn ahead of
everything else: a social trigger, being spoken to, an inner moment, the trip moment or a lull.
- An inner moment fires only when nothing social is happening (`world.py:1140-1146`), and on
  day 2 the kitchen is never quiet in the first half hour.
- Hunger cannot rise past 1.0 either, so in v12 it never fired: inner moments 0, 0, 3
  (night_v12 §8).
- A rule that waits for quiet would wait all morning.
- The person still sees what was said this turn. Their `say` can answer it.

### 2.2 The chance per turn

```
chance = RATE[band] × (0.5 + impulsive)
RATE["not since before yesterday"] = 0.07
RATE["yesterday"]                  = 0.035
RATE["this morning"]               = 0       (F5: no moment)
```

**The band comes from the person's own records:**
- **"yesterday"** if they ate any portion or part on day 1: `eat`, a `share` part, or a given
  portion. Seed 2 Mara (min 54) and seed 1 Leo and Mara (min 21): §9, command 2, with the
  minutes from night_design §2's table.
- **"not since before yesterday"** otherwise. That includes Daniel, whose can was eaten the
  night before day 1.
- They are the two forms the framing probe's F-B line used, from the same records.

**Why bands of a day, not hours.**
- The records hold only the day-1 minute of a meal. Before day 1 they hold no meal time at all.
- The gap between days is a skipped "afternoon and evening" (night_design §2), not a clock.
- An hourly curve would be precision the world does not have.

**The values** (§9, command 2):

| Person | impulsive | × (0.5 + impulsive) | Not since before yesterday | Within 10 turns | Ate yesterday | Within 10 turns |
|---|---|---|---|---|---|---|
| Daniel | 0.60 | 1.10 | 0.077 | 0.55 | 0.0385 | 0.32 |
| Elena | 0.25 | 0.75 | 0.0525 | 0.42 | 0.0263 | 0.23 |
| Leo | 0.20 | 0.70 | 0.049 | 0.39 | 0.0245 | 0.22 |
| Mara | 0.70 | 1.20 | 0.084 | 0.58 | 0.042 | 0.35 |

**Why 0.07.**
- **The target:** a starving person of middling impulsiveness (0.5, factor 1.0) who has not
  eaten since before yesterday, standing at the food with others around. They give in within
  half an hour about half the time: 1 − 0.93¹⁰ = 0.52.
- **Not much lower:** v12's day 2 ran 90 minutes in a starving house with 1–2 portions in
  reach and nobody touched them.
  - No real family a day and a half without food does that.
  - A real one deals with the shelf at the first meal it can, or decides out loud to keep it.
- **Not much higher:** at 0.2 a turn the moment would come at once, every morning, before
  anything is said. The can and the plan, which day 2 carries in, are what a real family also
  talks about first (night_v12 §8).
- **What it means for the house:** when three or four people are starving and present, their
  chances add up to about 0.17–0.24 a turn. The first moment then comes, more often than not,
  within the first fifteen minutes (seed 2: 0.63 by minute 12; §9, command 5). That is
  breakfast.

**Why × (0.5 + impulsive).**
- The factor runs from 0.70 (Leo) to 1.20 (Mara): the least controlled gives in about 1.7 times
  as often as the most.
- It follows the sheets:
  - Mara is 17, "everything she feels reaches her face before she decides to show it" (`data.py:47-49`);
  - Leo "knows survival" (`data.py:38`).
- **Not steeper** (e.g. × 2 × impulsive, 0.4 to 1.4): Leo would almost never break. But a careful
  survivor still breaks after a day and a half without food. The body acts on everyone.
- **Not flatter:** temperament would stop mattering, and only the seed would pick who reaches
  for the shelf.

**Why "yesterday" is half.** A portion eaten yesterday is, by night_design §2's numbers, the
difference between "very hungry" and "starving" the next morning. Halving keeps such a person
behind those who have not eaten, without shutting them out.

**The order of the work.** The rates were fixed before any draw was computed, and the draws (§2.7)
did not change them. As in night_design (its first note), changing a rate until a moment lands
where wanted would be choosing the story.

### 2.3 How often at most

- **A person: at most one food moment per 30 minutes** (F6).
  - A person who eats is out for the morning anyway (F5).
  - The 30 minutes matter for one who gives or shares and stays starving. Without the gap, the
    same moment would be put to them turn after turn.
  - Each moment moves food, so the gap is longer than the inner moment's 9 minutes
    (`world.py:80`).
- **The house: at most one food moment per turn** (F7). One hand at the shelf at a time. Two
  people reaching at once is a struggle the rules do not model.
- **The limit is the food itself:**
  - every moment ends with a portion eaten, given, shared, or refused back to the shelf;
  - seed 2 holds 1 portion and seed 3 holds 2.

### 2.4 The prompt at the moment

**The prompt.** It is the ordinary day-2 prompt for that turn: head, carry-in, pinned facts,
memory, the `Now` lines with who is here and what was said and done this turn, and the pattern
block. Two things change:
1. **One line is added as the last `Now` line,** before `Your options:`. It takes one of two
   forms, by band:

```
Your hunger has the better of you: you have not eaten since before yesterday, and the food is on the shelf in front of you. You cannot leave it there any longer.
```
```
Your hunger has the better of you: you last ate yesterday, at minute 54, and the food is on the shelf in front of you. You cannot leave it there any longer.
```

2. **The options are food only**, in this order:

```
Your options:
- eat: eat one of the portions
- give_<q>: give one of the portions to <Q>          (one per person present, in the family's order)
- share: share out what is left among everyone here
```

Seed 2, minute 00, Daniel (Elena, Leo and Mara present):

```
Your options:
- eat: eat one of the portions
- give_elena: give one of the portions to Elena
- give_leo: give one of the portions to Leo
- give_mara: give one of the portions to Mara
- share: share out what is left among everyone here
```

**Notes on the options:**
- **`eat` and `share` keep their ids and labels** (`world.py:469-472`). Their effects are as
  now (`world.py:1507-1548`).
- **None is marked (speech).** As `SYSTEM` allows (`world.py:45-46`), `say` may hold a short line
  said while doing it.
- **No `silent`, no talk, no move.** §3 point 1 is the argument against this.
- **The line's facts are all true:** they are starving (F4), the food is on the shelf in the
  room they are in (F2), and the last-ate clause is their own record (§2.2).
  - "You cannot leave it there any longer" is the rule itself, said as the body. Each option
    takes the food off the shelf for now: a refused gift puts it back (§2.5).
- **The budget:** the line is about 45 estimated tokens, and the options are 3–5 lines instead
  of 20–27. The prompt is shorter than the turn's ordinary one.

### 2.5 Giving, and the answer of the one who is given

**What happens:**
- `give_<q>` takes a portion off the shelf and puts it in Q's hands.
- **Q answers at once,** as someone taken aside does (`world.py:1028-1040`, `world.py:1173-1189`):
  - If Q had not acted yet this turn, the answer is Q's decision for the turn, and Q is taken
    out of the turn's remaining order.
  - If Q had already acted, the answer is an extra decision, and Q does not act again this
    turn.

**Q's prompt.**
- It is Q's ordinary prompt, with the social moment `<P> hands you one of the portions` and
  this last `Now` line:

```
<P> has just handed you one of the portions.
```

- And these options:

```
Your options:
- eat_given: eat the portion <P> gave you
- refuse_given: refuse it, and put it back on the shelf
```

**What each choice does:**
- **`eat_given`:**
  - Q eats it: hunger −0.4 (floor 0), eaten +1. The shelf keeps the one fewer.
  - For F5, Q has eaten this morning.
- **`refuse_given`:**
  - The portion goes back on the shelf.
  - The giver gets the trigger `<Q> puts the portion you gave back on the shelf` (new).
- **Neither is speech.** A refusal usually comes with words ("You have it, Mom"). They are
  heard as any words said while doing something are (`world.py:1283-1301`), with the doing
  text `putting the portion back on the shelf` or `eating`.

### 2.6 What the others perceive

**Nobody perceives the moment itself.** It is inside the person: no line, no trigger, no change
on their face. What the others perceive is the act. It is a new fact for everyone in the
kitchen, which makes it a trigger for each of them (the `fact` helper, `world.py:1411-1417`),
and it starts a conversation in the room as any new fact does.

| Act | Said and done this turn (seen by the room) | Pinned for each watcher | The actor's own pinned line | Grudge |
|---|---|---|---|---|
| `eat` | `<P> eats one of the portions.` (as now) | `min MM: <P> ate one of the portions (you saw it).` (as now) | `min MM: you ate one of the portions. <N> left.` (as now) | as now: each watcher at hunger level ≥ 1 holds it against P (`world.py:1519-1524`) |
| `share` | `<P> shares out the last <N> portion(s) between <names>.` (as now) | `min MM: <that>; you had your part.` (as now) | as now | none (as now) |
| `give_<q>`, then `eat_given` | `<P> gives one of the portions to <Q>, and <Q> eats it.` | `min MM: <P> gave one of the portions to <Q>, and <Q> ate it (you saw it).` Q: `min MM: <P> gave you one of the portions, and you ate it. <N> left.` | `min MM: you gave one of the portions to <Q>, and <Q> ate it. <N> left.` | each watcher at level ≥ 1, **not the giver**, against Q: `<Q> ate a portion <P> gave <him/her>, in front of you at minute MM, while you were hungry` |
| `give_<q>`, then `refuse_given` | `<P> gives one of the portions to <Q>; <Q> puts it back on the shelf.` | `min MM: <P> gave one of the portions to <Q>, and <Q> put it back on the shelf (you saw it).` | `min MM: you gave one of the portions to <Q>, and <Q> put it back on the shelf.` | none |

- **Through walls:** nothing but words, as now. Acts without words are not heard
  (`world.py:1048-1059`).
- **Hunger for `share`:** as now, each eater's hunger falls by 0.4 × their part
  (`world.py:1534-1539`).
- **The "About food:" line** changes with the shelf, as now (`world.py:605-617`).

### 2.7 Fallbacks, records and the story

**Fallbacks.** The code never eats for anyone:
- **An invalid answer at a food moment:** the person stays put and says nothing (`mode:
  fallback`), and the food stays. The moment counts for F6.
- **An invalid answer from Q:** `refuse_given`.

**Records:**
- The decision has `food_moment: {"band", "chance", "draw", "portions"}`. The transcript act
  carries the same.
- The meta counts `food_moments` and `give_answers` for day 2.

**The story:** the decision line starts like an inner moment's:

```
**Food moment**, starving in the kitchen with 1 portion on the shelf; last ate: not since before yesterday (chance 0.077 a turn, draw 0.0762).
```

### 2.8 Where the first moment falls in seeds 2 and 3

On day 2 of v13, every prompt before the first food moment is the same as v12's. Nothing else
changed (§1: nobody in seeds 2 and 3 gets the promise line), so with the v12 cache each of those
prompts gets v12's answer. v12 kept all four people in the kitchen for all 30 turns of day 2 in
every seed (§9, command 3). So where the first moment falls can be read now from the draws and
v12's turn order (§9, command 2):

| Seed | Shelf | First moment | Draw / chance | Their place in v12's turn | Then |
|---|---|---|---|---|---|
| 1 | 0 (the house draw is empty, night_design §4.4) | **none possible** | — | — | — |
| 2 | 1 | **minute 00, Daniel** | 0.0762 < 0.077 | 3rd, after Elena and Mara (their asks are cached) | Mara is not starving until minute 09 (0.822 → 0.856) |
| 3 | 2 | **minute 09, Mara** | 0.060 < 0.084 | 3rd, after Daniel (routine) and Leo | — |

- **Seed 2's moment sits on a knife edge.** A rate of 0.069 instead of 0.07 would move it.
  That is the point of §2.2's last paragraph: the rate was set first.
- **What follows the first moment cannot be read ahead.** The answer is new, so it comes live,
  and so does everything after it.

---

## 3. The case against

CLAUDE.md: argue against it first. Would a real person do this, and for what reason? Where does
the rule script the story?

**The food moment:**
1. **It forbids saving the food.** A real family with one portion and four starving people
   might keep it:
   - for tonight;
   - for the youngest;
   - for whoever goes next door, who needs strength in the street.

   Once the moment fires, no option leaves the food alone; only the person given a portion can
   put it back.
   - *Answer:* holding off is what happens on every turn the moment does not fire, and it is
     still open through the ordinary options. The moment is the turn the holding off breaks.
   - *Where it scripts:* that the shelf is touched on day 2 is all but decided by the rule, not
     by the family.
     - With everyone in the kitchen, the chance of no moment in 30 turns is 0.125% in seed 2 and
       0.03% in seed 3 (§2.2's table; §9, command 5).
     - **B1 therefore tests the code more than the people.** What the people decide is how the
       food goes, and who gets it.
2. **It hands the shelf to the impulsive, not to whoever keeps the food.**
   - In a real house the mother often divides it. Here the factor gives Elena the second-lowest
     chance (0.75).
   - The rule models the body breaking, not authority over food. A family's rule about who
     divides it is not in the data.
3. **It ignores what the room is doing.** It fires in the middle of an accusation or a plea.
   - *Answer:* hunger does interrupt. And the person sees the turn so far, and their words can
     answer it.
   - *The cost:* a moment at minute 00 of seed 2, while Daniel is being accused, can read as
     the code cutting in.
4. **One line, word for word, every time.**
   - framing_probe's P-B reasons were near copies of each other: five of six said "no matter
     the risk", "the danger" or "what it takes". A fixed line invites a fixed reason ("I can't
     wait any longer").
   - If every moment's reason echoes the line, it reads as a timer going off.
   - The run counts it (R7).
5. **The gift is answered at once.** A real offer of food can be argued over for minutes ("No,
   you have it." "Take it."). Here it is one answer, and a refusal ends it.
6. **The grudge from a gift falls on the one who ate it, not on the one who chose.**
   - Leo, starving, watching Elena give Mara the only portion may resent Elena's choice more
     than Mara.
   - The rule keeps the existing one (watching someone eat while hungry) and names the giver in
     the fact. It does not decide whom else to blame.
7. **Alone in the kitchen, no moment** (F3). This leaves out the most real temptation of all,
   the one that began the story: Daniel's can.
   - *Reason:* alone, the only food option is "eat", so the code would be eating for them. And
     a secret meal would replay the can (night_design §7.9).
8. **"Very hungry" never triggers it**, and nor does the night. Seed 2's Mara (0.822 at minute
   00) has to wait until minute 09.
   - This is the brief's line ("a starving person"). A moment for every hungry person would
     make the rule the morning's main event.
9. **It could look mechanical.** It would, if moments land at even intervals, always on the
   most impulsive, or always end the same way: everyone eats, or everyone gives.
   - The draws are independent per turn, and the options leave the outcome to the person.
   - But with 1–2 portions only one or two moments can happen. Three seeds are too few to show
     variety, which is a gap.

**The promise line:**

10. **It is a nudge, and it leans.**
    - It restates one fact (the offer) and adds a deadline ("it is now"). The probe showed that
      such a line nearly decides the choice: 6 of 6.
    - It speaks only to a promise to go. Someone who said "nobody should go" gets no matching
      line, such as "you said nobody should go; if you mean to stop it, it is now".
    - *Answer:* the brief is about keeping a promise to act. A position against going is kept
      by doing nothing, and every bedtime option already allows that.
    - *The cost:* the night now leans toward the volunteer acting, by design.
11. **Would Daniel go?** Seed 1's Daniel offered at minute 36, and all three forbade him at
    39–42.
    - He is impulsive (0.60), very proud (0.85), "takes charge because he is frightened", and
      he "believes responsibility is his by right of age" (`data.py:19-23`). The shelf is
      empty, and he ate the can.
    - Going while the house sleeps is in character. So is a frightened man lying awake. If
      every run sends him, that is the line deciding, not Daniel (R6 reads his reason).
12. **The tested line had a false sentence; this one does not.**
    - "The house is asleep" may have been part of what sent him: it says nobody will see.
    - Without it, Daniel may go less often than 6 of 6. B2 is a single draw at the run's seed,
      so one run cannot tell 6 of 6 from 3 of 6.
13. **He may be stopped.** Leo's bedtime prompt is unchanged, so his v12 answer, `lie_awake`,
    comes from the cache. An awake roommate sees him get up for certain (`night.py:248-252`).
    - Whether Daniel goes then depends on Leo's reaction and Daniel's answer. This is the night
      working as designed, and it is why B2's rule (§6) counts leaving, not the bedtime choice.

**What the rules decide:**
- when a food moment comes, and that the shelf is touched in it;
- that a promise is restated at bedtime.

**What the people decide:**
- whether to eat, give or divide, and to whom;
- whether to take a gift;
- what to say;
- whether to go;
- what they make of it on day 2.

---

## 4. Tests

All use the fake model or a scripted oracle, with `GEMINI_API_KEY` unset. Each B test names the
behaviour of §1–§2.

| # | What | How |
|---|---|---|
| B-T1 | **Day 1 replays** | For N = 1, 2, 3, from a copy of `cache/v12/…seedN.json`, which holds every v11 entry unchanged (§9, command 4): day 1 serves 55, 53 and 45 answers with 0 API requests. Its story text before `# The night` equals `runs/v11/daniel_ate_it-seedN.md` byte for byte. |
| B-T2 | **The promise line: who** | Scripted states: latest own position `volunteer` (day 1); `still_going` and `volunteer` (day 2); `volunteer` then `decline`; `volunteer` then `object_trip`; backed by others but never offered; no position. The line appears exactly in the first two kinds of state and in no other. It never appears in reaction or answer prompts. |
| B-T3 | **The promise line: exactly** | The text of §1, as the last `Now` line before `Your options:`. Every other bedtime line is byte-identical to v12's. Rebuilt from the v12 day-1 states: seed 1 Daniel's prompt differs from `cache/v12`'s by that one line only. The other 11 bedtime prompts are byte-identical to the cached ones. |
| B-T4 | **Eligibility** | A table over F1–F9, one case failing each condition and one passing all: day 1, night, other room, empty shelf, alone, very hungry, ate this morning (eat, share part, given), 29 vs 30 minutes since their last moment, a second moment in the same turn, answering an aside or a give, draw at and just under the chance. |
| B-T5 | **The chance** | The table of §2.2, exactly, from the sheets and the bands. The bands come from day-1 eating (eat, share, given) and the can (before yesterday). The draw string of F9. Over 100,000 draws, the firing frequency is within ±0.3 points of each chance. |
| B-T6 | **The moment's prompt, exactly** | The line of §2.4 in both band forms (with the minute), as the last `Now` line. The options are `eat`, `give_<q>` in family order for each person present, and `share`, with their labels, and nothing else. The rest of the prompt is byte-identical to the same turn's ordinary prompt, apart from the options. |
| B-T7 | **Giving** | Q answers at once, with the prompt line and two options of §2.5, and Q's answer is or is not their turn as §2.5 says. `eat_given`: shelf −1, Q's hunger −0.4, Q counts as eaten. `refuse_given`: shelf unchanged, and the giver gets the trigger. |
| B-T8 | **Perception** | Each row of §2.6's table: the turn's lines, the pinned lines, the triggers (new) for everyone in the kitchen, the grudges, and none through walls. Nobody perceives the moment itself. |
| B-T9 | **Fallbacks** | An invalid moment answer: the person stays put, the food stays, and F6 counts the moment. An invalid answer from Q: `refuse_given`. |
| B-T10 | **The paired day 2** | A scripted oracle serves the v12 cache for seeds 2 and 3 and stops at the first prompt not in it. The first food moment fires at seed 2 minute 00 for Daniel (3rd to act) and at seed 3 minute 09 for Mara (3rd), with §2.8's draws. Every prompt before it is a cache hit. Seed 1's day 2 has no moment (shelf 0). |
| B-T11 | **Records and story** | The `food_moment` fields; `food_moments` and `give_answers` in the meta; the story line of §2.7; asks counted per scene, as now. |
| B-T12 | **Frozen versions** | `v12/check.py` (new, as `v11/check.py`) replays `runs/v12` byte for byte with 0 API calls. `v11/check.py`, `v10/check.py` and `v9/check.py` still do. |
| B-T13 | **The full suite** | `python -m unittest test_morning` exits 0. Any existing test whose fake numbers change is listed, with old and new values, in the implementation report. |

**Housekeeping, as for v5–v12:** the current code is frozen as `v12/`, and `morning.py`'s
default `--out` becomes `v13` (`morning.py:219`). Frozen directories are not edited (CLAUDE.md).

---

## 5. Cost and run plan

### Request cost per seed

**What each part costs:**
- Day 1: 0 API requests (55, 53 and 45 answers from the cache).
- The promise line costs no ask: it is a line in a prompt that is asked anyway.
- Each food moment costs at most 1 ask: it replaces the person's decision for the turn, which
  may have been routine.
- Each give costs 1 more ask, Q's answer.

| Seed | Night asks | Day-2 asks | Night + day 2 | API requests | Basis |
|---|---|---|---|---|---|
| 1 | 4 if Daniel stays; 5–9 if he goes (Leo's reaction, Daniel's answer if stopped, then Elena and Mara hearing the door); at most 12 | 45–85; v12 was 54 | **50–97** | all but 3 (the other three bedtime prompts are cached) | night_design §3.6, §10. The night's news changes every day-2 prompt from minute 00. |
| 2 | 4, all cached | v12's 39, plus 1–4 (1–2 moments, 0–2 gives) | **44–60** | 2 cached at minute 00, then live: about 40–55 | §2.8: the first moment comes at minute 00 |
| 3 | 4, all cached | v12's 51, plus 1–4 | **56–75** | about 12 cached (minutes 00–06), then live: about 45–65 | §2.8: minute 09 |

**The ceilings:**
- **Theoretical:** 12 (night) + 30 turns × 4 + 30 (at most one give answer per turn) = **162**.
  It cannot be reached:
  - with 1 or 2 portions, at most 2 eat, share or `eat_given` acts happen in seeds 2 and 3;
  - each refusal puts a portion back, and each giver then waits 30 minutes.
- **Expected:** at most **97** in every seed, so B5's 120 holds with room to spare.

**The quota:** about 135–215 API requests for the three seeds, against the 500 a day (CLAUDE.md).
- On 2026-10-03 the framing probe already sent 86. Start on a day with no other use.

### Run plan (run mode only, output v13, default model)

**Before any API call:**
- **R0. A clean start.** HEAD holds the implementation and its tests. `git status --porcelain`
  shows nothing tracked as modified, and no `runs/v13/` or `cache/v13/` exists.
- **R1. The suite.** `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning`
  exits 0.
- **R2. The freezes.** `v12/check.py`, `v11/check.py`, `v10/check.py` and `v9/check.py` report
  IDENTICAL with 0 API calls. B-T1 passes.
- **R3. The paired start.** For N = 1, 2, 3:
  `cp cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v13/`.
  - It holds v11's day-1 answers unchanged, plus v12's night and day 2 (§9, command 4).
  - So day 1 comes from the v11 answers, and every night or day-2 prompt that is unchanged is
    answered as in v12.

**Runs.** One at a time, each after the one before exits 0:

```
.venv/Scripts/python.exe -u morning.py --seed 1 --out v13 > runs/v13/daniel_ate_it-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 2 --out v13 > runs/v13/daniel_ate_it-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 3 --out v13 > runs/v13/daniel_ate_it-seed3.stdout.txt 2>&1
```

An exit of 3 is resumed with the same command once the limit has passed.

**After each run:**
- **R4. Totals.** Exit code, the meta (day 1, night, day 2) and the console output. How many
  answers came from the cache and how many from the API, per scene.
- **R5. The paired checks.**
  - Day 1 identical, as in B-T1.
  - Seeds 2 and 3: every bedtime answer, and every day-2 answer before the first food moment,
    is a cache hit.
  - Where the first moment fell, against §2.8.
- **R6. The night.**
  - Seed 1 Daniel's bedtime prompt: the promise line present, as §1.
  - His choice, feeling and reason. Does the reason cite the promise, the food or the risk?
  - Every noticing with its draw, every reaction and answer with its words, and the outcome.
- **R7. Every food moment.**
  - Who, when, band, chance and draw.
  - The option, words, feeling and reason, and Q's answer and words.
  - What the watchers did next, and any grudge.
  - The reasons, set side by side and checked for the line's words echoed back (§3 point 4).
- **R8. Verdicts.** B1–B5, then the designer's D1–D5, each PASS or FAIL (or NOT TESTED) with
  evidence rows.
- **R9. A reading** (CLAUDE.md):
  - Is this what a real family would do with one or two portions and four starving people?
  - Did the moment read as the body or as a timer?
  - Did Daniel go because of who he is, or because of the line?
  - What did day 2 make of a goer, if there was one?
  - Never items, scored as in night_v12 §7.

**Delivers:** `runs/v13/daniel_ate_it-seed{1,2,3}.{md,meta.json,transcript.json,stdout.txt}`,
`cache/v13/…seed{1,2,3}.json` and `reports/body_v13.md`.

---

## 6. Predictions (frozen, verbatim from the brief)

```
  B1. In seeds 2 and 3, where food is on the shelf, the food is eaten,
      given or divided on day 2 (2 of 2 seeds).
  B2. In seed 1, Daniel goes next door at night.
  B3. In seeds 2 and 3, nobody who never offered to go goes next door
      because of the new lines.
  B4. No seed has more day-2 Never items than v12 (2, 2, 2).
  B5. The night and day 2 cost at most 120 requests per seed.
```

### B1: pass or fail rule

- **A seed holds B1** if at least one portion leaves the shelf on day 2 by an act. It may come at
  a food moment or from an ordinary option:
  - `eat`;
  - `share`;
  - `give_<q>` followed by `eat_given`.
- These do not count:
  - a give that is refused (the portion goes back);
  - food that leaves the shelf any other way (there is no other way).
- Evidence: the transcript's day-2 acts, and the shelf count each turn (`record["portions"]`).
- **PASS** if seeds 2 and 3 both hold it. Otherwise **FAIL**, with each seed's food moments and
  their answers listed.

### B2: pass or fail rule

- **PASS** if `daniel` is in seed 1's `leavers` (the meta and `transcript["night"]["leavers"]`,
  `night.py:321`). That means he went out by the front door, whatever followed in the street.
- **FAIL** if he did not leave.
  - That includes choosing `go_next_door` and then going back to bed after a stop (`stay_home`).
  - The bedtime choice and every reaction and answer are reported either way.

### B3: pass or fail rule

- **Who "never offered":** a person with no `volunteer` act on day 1 and no `volunteer` or
  `still_going` act before the night. In seed 3 that is Daniel, Elena and Mara. In seed 2 it is
  nobody: all four offered at some time on day 1 (§9, command 3).
- **"Because of the new lines":** the person's bedtime prompt contains the promise line.
  - A leaver whose bedtime prompt is byte-identical to v12's did not leave because of the new
    lines.
  - Those prompts are answered from the cache, so with the cached answers (all `lie_awake`)
    there would be no leaver at all.
- **PASS** if, in seeds 2 and 3, no person who never offered is a leaver with the promise line
  in their bedtime prompt, **and** no person who never offered has the promise line at all. The
  second part checks the rule of §1 itself.
- **FAIL** otherwise, naming the person and quoting the prompt line.

### B4: pass or fail rule

- **Scored as in night_v12 §7:** the readings of trip_v11.md §7, N1–N13, on day 2 only, one
  pass per seed, with the mechanical inputs listed first.
- A food act is read under the existing items. N9's frozen silence is broken only by an act that
  is not silent. That includes a food moment's act, which is not routine.
- **PASS** if each seed's count is at most 2. **FAIL** if any seed has 3 or more, with the items
  that are new against v12 quoted.

### B5: pass or fail rule

- **Per seed:** `night_asks + day2_asks` from the meta. That is every model ask in those scenes,
  live or cached, fallbacks and give answers included (as Q5 in night_design §11).
  `night_api_requests + day2_api_requests` is reported beside it.
- **PASS** if it is at most 120 in each seed. **Expected:** 50–97, 44–60 and 56–75 (§5).

---

## 7. Designer's predictions (separate; not part of the frozen set)

- **D1. The paired start holds.** The first food moment fires at seed 2 minute 00 for Daniel
  and at seed 3 minute 09 for Mara. Every earlier answer of those days, and every night answer
  of seeds 2 and 3, comes from the cache.
  - Basis: §2.8. A miss means the implementation changed a prompt it should not have.
- **D2. Seed 2 Daniel does not eat the portion himself at his moment** (he gives it or shares
  it).
  - Basis: he confessed the can yesterday after denying it, his guilt is 3 of 3 (`runs/v12/daniel_ate_it-seed2.md:265`),
    and he wants "being respected".
- **D3. In at least one of the two first moments (seeds 2, 3), the chooser does not keep the
  food for themselves:** `give_*` or `share`.
- **D4. In seed 1, Daniel chooses `go_next_door` at bedtime, and his reason does not mention
  the promise.**
  - Basis: framing_probe P-B, where none of the 6 reasons named the promise, and five named the
    food.
- **D5. In seed 1, Leo notices Daniel get up and chooses `stop_daniel`.**
  - Basis: his v12 bedtime reason was "to ensure Daniel doesn't try to slip out into the dark"
    (night_v12 §2), and that answer is cached.

---

## 8. What this design does not decide

- **Keeping food back on purpose.** An option to set food aside "for tonight" or "for Mara" is
  §3 point 1's gap. It is the first thing to add if the run reads as the code emptying the shelf.
- **Who in the family controls the food** (§3 point 2). The data says nothing about it.
- **Eating in the night**, and a food moment when alone (§3 point 7).
- **A mirror line for those who said nobody should go** (§3 point 10).
- **Whether the probed and unprobed promise lines differ in effect.** A 6-request probe of §1's
  exact line, as framing_probe P-B, would answer it. It is not part of this design's run.
- **A second night.** Day 2 still ends at minute 87, and the promise line would first matter
  again at a second bedtime.

---

## 9. Commands run and output

From `Prototypes/llm-morning/` unless shown. `$S` is
`C:\Users\Akrem\AppData\Local\Temp\claude\…\scratchpad\body`. No command called the API, and no
script writes anything in the repo.

1. **The commit before this design** (from the repo root):

```
$ git status --short
?? Prototypes/llm-morning/reports/framing_probe.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ git log --oneline -3 -- Prototypes/llm-morning/reports/model_probe.md Prototypes/llm-morning/reports/framing_probe.md
973f9d2 LLM morning: model probe of the v12 prompts on gemini-3.8-flash (stopped on the quota, 6 of 20)
$ git add Prototypes/llm-morning/reports/framing_probe.md && git commit -m "LLM morning: framing probe on Flash-Lite (promise line 6 of 6, food framing 0 of 72) …"
$ git log --oneline -1
6747b83 LLM morning: framing probe on Flash-Lite (promise line 6 of 6, food framing 0 of 72)
```

2. **The chances, and where the first moment falls** (`$S/food_draws.py`, source below):

```
$ python $S/food_draws.py
chance per turn, by band:
  daniel impulsive 0.60 factor 1.10 yesterday        0.0385  within 10 turns 0.32
  daniel impulsive 0.60 factor 1.10 before_yesterday 0.0770  within 10 turns 0.55
  elena  impulsive 0.25 factor 0.75 yesterday        0.0263  within 10 turns 0.23
  elena  impulsive 0.25 factor 0.75 before_yesterday 0.0525  within 10 turns 0.42
  leo    impulsive 0.20 factor 0.70 yesterday        0.0245  within 10 turns 0.22
  leo    impulsive 0.20 factor 0.70 before_yesterday 0.0490  within 10 turns 0.39
  mara   impulsive 0.70 factor 1.20 yesterday        0.0420  within 10 turns 0.35
  mara   impulsive 0.70 factor 1.20 before_yesterday 0.0840  within 10 turns 0.58

seed 1: ate on day 1: ['leo', 'mara']; bands {'daniel': 'before_yesterday', 'elena': 'before_yesterday', 'leo': 'yesterday', 'mara': 'yesterday'}
  first food moment if the shelf held food (v12 order, everyone in the kitchen): (30, ('mara', 0.0047, 0.042), [('mara', 0.0047, 0.042)])

seed 2: ate on day 1: ['mara']; bands {'daniel': 'before_yesterday', 'elena': 'before_yesterday', 'leo': 'before_yesterday', 'mara': 'yesterday'}
  first food moment if the shelf held food (v12 order, everyone in the kitchen): (0, ('daniel', 0.0762, 0.077), [('daniel', 0.0762, 0.077)])

seed 3: ate on day 1: nobody; bands {'daniel': 'before_yesterday', 'elena': 'before_yesterday', 'leo': 'before_yesterday', 'mara': 'before_yesterday'}
  first food moment if the shelf held food (v12 order, everyone in the kitchen): (9, ('mara', 0.06, 0.084), [('mara', 0.06, 0.084)])
```

3. **The v12 states the design reads** (`$S/v12_state.py`):

```
$ python $S/v12_state.py
seed 1
  latest day-1 trip position: {'leo': 'object_trip (min 39)', 'elena': 'object_trip (min 42)', 'mara': 'object_trip (min 39)', 'daniel': 'volunteer (min 36)'}
  gets the promise line (latest is volunteer): ['daniel']
  day-1 volunteer acts: [('24', 'daniel'), ('30', 'mara'), ('30', 'leo'), ('33', 'elena'), ('36', 'daniel')]
  night choices: {'daniel': 'sleep', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} leavers: []
  day 2: all four in the kitchen in all 30 turns: True
  day-2 eat/share acts: none
  min 00 order: [('daniel', 'reassure_all', 'model'), ('leo', 'send_daniel', 'model'), ('elena', 'send_daniel', 'model'), ('mara', 'send_daniel', 'model')]
  min 03 order: [('daniel', 'volunteer', 'model'), ('elena', 'reassure_daniel', 'model'), ('leo', 'volunteer', 'model'), ('mara', 'send_leo', 'model')]
  min 06 order: [('leo', 'still_going', 'model'), ('daniel', 'still_going', 'model'), ('mara', 'send_daniel', 'model'), ('elena', 'reassure_daniel', 'model')]
  min 09 order: [('daniel', 'still_going', 'model'), ('leo', 'still_going', 'model'), ('mara', 'volunteer', 'model'), ('elena', 'reassure_all', 'model')]
seed 2
  latest day-1 trip position: {'daniel': 'object_trip (min 51)', 'leo': 'object_elena (min 48)', 'elena': 'decline (min 51)', 'mara': 'object_elena (min 48)'}
  gets the promise line (latest is volunteer): nobody
  day-1 volunteer acts: [('36', 'daniel'), ('39', 'mara'), ('42', 'leo'), ('45', 'daniel'), ('48', 'elena')]
  night choices: {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} leavers: []
  day 2: all four in the kitchen in all 30 turns: True
  day-2 eat/share acts: none
  min 00 order: [('elena', 'reassure_all', 'model'), ('mara', 'accuse_daniel', 'model'), ('daniel', 'reassure_mara', 'model'), ('leo', 'accuse_daniel', 'model')]
  min 03 order: [('daniel', 'reassure_all', 'model'), ('mara', 'accuse_daniel', 'model'), ('elena', 'reassure_all', 'model'), ('leo', 'accuse_daniel', 'model')]
  min 06 order: [('daniel', 'propose_trip', 'model'), ('mara', 'send_daniel', 'model'), ('elena', 'nobody_goes', 'model'), ('leo', 'send_daniel', 'model')]
  min 09 order: [('daniel', 'volunteer', 'model'), ('mara', 'accuse_daniel', 'model'), ('leo', 'propose_trip', 'model'), ('elena', 'keep_daniel_home', 'model')]
seed 3
  latest day-1 trip position: {'leo': 'decline (min 69)', 'mara': 'object_trip (min 66)', 'daniel': 'object_leo (min 66)', 'elena': 'object_trip (min 66)'}
  gets the promise line (latest is volunteer): nobody
  day-1 volunteer acts: [('66', 'leo')]
  night choices: {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} leavers: []
  day 2: all four in the kitchen in all 30 turns: True
  day-2 eat/share acts: none
  min 00 order: [('mara', 'ask_who', 'model'), ('elena', 'reassure_all', 'model'), ('daniel', 'deny', 'model'), ('leo', 'silent', 'model')]
  min 03 order: [('elena', 'ask_who', 'model'), ('mara', 'ask_who', 'model'), ('daniel', 'deny', 'model'), ('leo', 'silent', 'model')]
  min 06 order: [('leo', 'silent', 'routine'), ('mara', 'ask_who', 'model'), ('elena', 'silent', 'model'), ('daniel', 'deny', 'model')]
  min 09 order: [('daniel', 'silent', 'routine'), ('leo', 'silent', 'model'), ('mara', 'accuse_daniel', 'model'), ('elena', 'silent', 'model')]
```

4. **The paired cache, and v12's ask counts** (`$S/cache_check.py`):

```
$ python $S/cache_check.py
seed 1: v11 entries 62, v12 entries 120, every v11 entry in v12 unchanged: True; night_asks 4, day2_asks 54, night_api 4, day2_api 54, leavers []
seed 2: v11 entries 67, v12 entries 110, every v11 entry in v12 unchanged: True; night_asks 4, day2_asks 39, night_api 4, day2_api 40, leavers []
seed 3: v11 entries 51, v12 entries 106, every v11 entry in v12 unchanged: True; night_asks 4, day2_asks 51, night_api 4, day2_api 51, leavers []
```

5. **The house's chance of a moment, and of none** (`$S/no_moment.py`, arithmetic only):

```
$ python $S/no_moment.py
seed 2: house chance a turn 0.168 (turns 0-2), 0.203 (from turn 3); some moment by minute 12 0.63; none in 30 turns 0.00125
seed 3: house chance a turn 0.238; none in 30 turns 0.00029
```

### Scripts

`$S/food_draws.py`:

```python
"""Read-only: the food moment's chances (reports/body_design.md §2), its draws for seeds 1-3, and where
the first moment would fire on day 2 if v13 follows v12 until then (it does: same prompts, same cache).
Run from Prototypes/llm-morning/. Reads data.py and runs/v12 transcripts; writes nothing."""
import json, os, random, sys
sys.path.insert(0, os.getcwd())
import data

RATE = {"yesterday": 0.035, "before_yesterday": 0.07}   # per turn, at impulsive 0.5
EVERY = 30                                               # minutes between one person's moments
def factor(pid): return 0.5 + data.PEOPLE[pid]["traits"]["impulsive"]
def chance(pid, band): return round(RATE[band] * factor(pid), 4)
def u(seed, t, pid): return random.Random(f"{seed}:day2:food:{t}:{pid}").random()
def level(h): return 0 if h < 0.5 else 1 if h < 0.7 else 2 if h < 0.85 else 3

print("chance per turn, by band:")
for pid in data.ORDER:
    for band in RATE:
        c = chance(pid, band)
        print(f"  {pid:6} impulsive {data.PEOPLE[pid]['traits']['impulsive']:.2f} factor {factor(pid):.2f} "
              f"{band:16} {c:.4f}  within 10 turns {1-(1-c)**10:.2f}")

# Who last ate when, at day-2 minute 00 (day-1 eating from the v12 transcripts; the can was the night before day 1).
for seed in (1, 2, 3):
    tr = json.load(open(f"runs/v12/daniel_ate_it-seed{seed}.transcript.json", encoding="utf-8"))
    ate = {a["who"] for turn in tr["day1"]["turns"] for a in turn["acts"] if a["option"] in ("eat", "share")}
    band = {p: "yesterday" if p in ate else "before_yesterday" for p in data.ORDER}
    print(f"\nseed {seed}: ate on day 1: {sorted(ate) or 'nobody'}; bands {band}")
    # day-2 morning hunger, from night_design §2 / night_v12 §2
    h = {1: {"daniel": 1.0, "elena": 1.0, "leo": 0.81, "mara": 0.822},
         2: {"daniel": 1.0, "elena": 1.0, "leo": 1.0, "mara": 0.822},
         3: {"daniel": 1.0, "elena": 1.0, "leo": 1.0, "mara": 1.0}}[seed]
    first = None
    for turn in tr["day2"]["turns"]:
        t = turn["minute"] // 3
        order = [a["who"] for a in turn["acts"]]
        kitchen = turn["rooms"]["kitchen"]
        fired = [(p, round(u(seed, t, p), 4), chance(p, band[p])) for p in order
                 if p in kitchen and level(h[p]) == 3 and len(kitchen) > 1 and u(seed, t, p) < chance(p, band[p])]
        if fired and first is None:
            first = (turn["minute"], fired[0], fired)
        for p in data.ORDER:
            h[p] = min(1.0, h[p] + 0.012 * data.PEOPLE[p]["hunger_rate"])
    print(f"  first food moment if the shelf held food (v12 order, everyone in the kitchen): {first}")
```

`$S/v12_state.py`:

```python
"""Read-only: from runs/v12 transcripts, each person's latest day-1 trip position (the bedtime promise
rule), every day-1 volunteer act, the night's choices, and where everyone was on day 2 with the act
order of the turns before the first food moment."""
import json
for s in (1, 2, 3):
    t = json.load(open(f"runs/v12/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    latest = {}
    for m, who, i, words in t["day1"]["trip"]["acts"]:
        latest[who] = (m, i)
    print(f"seed {s}")
    print("  latest day-1 trip position:", {w: f"{i} (min {m:02d})" for w, (m, i) in latest.items()})
    print("  gets the promise line (latest is volunteer):", [w for w, (m, i) in latest.items() if i == "volunteer"] or "nobody")
    print("  day-1 volunteer acts:", [(f"{m:02d}", w) for m, w, i, _ in t["day1"]["trip"]["acts"] if i == "volunteer"])
    print("  night choices:", t["night"]["choices"], "leavers:", t["night"]["leavers"])
    turns = t["day2"]["turns"]
    allk = all(sorted(x["rooms"]["kitchen"]) == ["daniel", "elena", "leo", "mara"] for x in turns)
    print(f"  day 2: all four in the kitchen in all {len(turns)} turns: {allk}")
    food = [(x["minute"], a["who"], a["option"]) for x in turns for a in x["acts"] if a["option"] in ("eat", "share")]
    print("  day-2 eat/share acts:", food or "none")
    for x in turns[:4]:
        print(f"  min {x['minute']:02d} order:", [(a["who"], a["option"], a["mode"]) for a in x["acts"]])
```

`$S/cache_check.py`:

```python
"""Read-only: is every v11 cache entry in the v12 cache, unchanged? And what the v12 meta records per seed."""
import json
for s in (1, 2, 3):
    f = f"gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json"
    a = json.load(open(f"cache/v11/{f}", encoding="utf-8"))
    b = json.load(open(f"cache/v12/{f}", encoding="utf-8"))
    same = all(k in b and b[k] == v for k, v in a.items())
    m = json.load(open(f"runs/v12/daniel_ate_it-seed{s}.meta.json", encoding="utf-8"))
    print(f"seed {s}: v11 entries {len(a)}, v12 entries {len(b)}, every v11 entry in v12 unchanged: {same}; "
          f"night_asks {m.get('night_asks')}, day2_asks {m.get('day2_asks')}, "
          f"night_api {m.get('night_api_requests')}, day2_api {m.get('day2_api_requests')}, leavers {m.get('leavers')}")
```

`$S/no_moment.py`:

```python
"""Read-only arithmetic: with everyone in the kitchen all morning, the house's chance of a food moment per
turn and of none in 30 turns (seed 2: Mara is not starving until turn 3 and last ate yesterday)."""
q = lambda c: 1 - c
d, e, l = 0.077, 0.0525, 0.049                      # not since before yesterday: Daniel, Elena, Leo
s2_early = q(d) * q(e) * q(l)                         # seed 2, turns 0-2 (Mara very hungry)
s2_late = s2_early * q(0.042)                         # seed 2, turns 3-29 (Mara, ate yesterday)
s3 = q(d) * q(e) * q(l) * q(0.084)                    # seed 3, all four, none ate yesterday
print(f"seed 2: house chance a turn {1 - s2_early:.3f} (turns 0-2), {1 - s2_late:.3f} (from turn 3); "
      f"some moment by minute 12 {1 - s2_early**3 * s2_late**2:.2f}; none in 30 turns {s2_early**3 * s2_late**27:.5f}")
print(f"seed 3: house chance a turn {1 - s3:.3f}; none in 30 turns {s3**30:.5f}")
```
