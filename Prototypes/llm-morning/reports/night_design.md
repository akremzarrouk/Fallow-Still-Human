# Design: time passing — the night after the v11 morning, and the next morning (`daniel_ate_it`, v12)

Mode: design. No code was written or changed, and no API was called. Before this file,
`runs/v11/`, `cache/v11/` and `reports/trip_v11.md` were committed on their own as `976dc73`.
Paths are relative to `Prototypes/llm-morning/`. Scratch scripts are in the session scratchpad
(`$S/night/`) and are reproduced in §14 with their output.

**Words used here.**
- **Day 1** is the v11 morning: house day 4 (morning.json `"day": 4`; the story's table writes the
  count as day 4). **Day 2** is the next morning: house day 5. Prompts say "yesterday" and "last
  night"; they never say "day 1" or "day 2".
- **A scene** is one of: day 1, the night, day 2. Each seed runs all three, in one process.
- **An ask** is one model decision (live or from the cache), as P6 counted it in trip_v11.md.

**The step in one paragraph.**
- Day 1 is replayed from the v11 cache: 0 requests, byte-identical story.
- One plain line skips the afternoon. Nobody eats, and hunger rises by one portion's worth
  (0.4 × each person's hunger rate), most of it before bed.
- Everyone goes to bed in their own room. Each person makes one private decision: sleep, lie
  awake, sit up by the front door, or go next door. Anyone may go.
- The rules work out who notices whom from the rooms, what carries through walls and a draw for
  whoever is asleep. Whoever notices gets one more decision: let them go, stop them, or go with
  them. A leaver who is stopped answers once.
- The world decides the trip by two seeded draws: what the neighbour's house holds, and what
  the street does to whoever crosses it.
- Day 2 is a morning like day 1. Each person carries in a short block of facts and conclusions
  written by the code: yesterday's can, accusations, eating and plan; their own night; the
  outcome as far as they know it. Grudges, suspicion, guilt and hunger carry in as state.
- Day 2's trip options get new wording, so that no two of them differ by "not" alone, and a
  volunteer can hold to their offer.

**Two things to know before reading on.**
1. **With the seed strings of §4.4, the neighbour's house holds no food in seeds 1, 2 and 3**
   (draws 0.050, 0.105, 0.257, all under 0.30; chance 2.7%). The strings were written before
   the draws were computed, and they are not changed. Changing a string until food appears
   would be choosing the story. In this run, whoever goes comes back with nothing, comes back
   shaken, or does not come back. "Back with food" is covered by the tests only (§9 T7).
2. **The carry-in block sits outside the 1,400-token budget, as the trip block already does**
   (§5.4). Kept inside, it would leave room for 0–6 of this morning's lines, and 8 of 24
   measured day-2 prompts would be over budget before anyone said a word. Day-2 prompts reach
   about 1,575–1,850 estimated tokens at minute 00 and at most 2,134.

---

## 1. Day 1: the v11 morning, replayed

- **The run.** `morning.py --seed N --out v12` runs day 1 first. Its answers come from
  `cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seedN.json`, a copy of the v11 file (§10 R3).
  The cache key is model, seed, system text and prompt (gemini.py:196-198).
- **Nothing in day 1 changes.**
  - Every v12 change is gated on the scene, so day-1 prompts are byte-identical to v11's.
  - That covers the option fix (§6), which starts with day 2. Day 1 keeps `back_*`,
    `object_*` and `decline` with their v11 labels.
- **Expected:** 55, 53 and 45 answers served from the cache, 0 API requests. The replay was run
  offline for this design: `$S/night/state.py`, §14 command 2.
- **The check.** The story's text before the line `# The night` is byte-identical to
  `runs/v11/daniel_ate_it-seedN.md`. The transcript's `"day1"` value equals
  `runs/v11/daniel_ate_it-seedN.transcript.json` (§9 T1).

**The state day 1 hands on** (§14 command 2). Everyone is in the kitchen at minute 90 in all
three seeds.

| Seed | Shelf | Can | Grudges held | Plan at minute 90 |
|---|---|---|---|---|
| 1 | 0 | Daniel confessed at 03; all know | Mara→Leo 3 | Daniel will go; Mara, Leo, Elena against anyone going |
| 2 | 1 | Daniel confessed at 33 after denying; all know | Leo→Daniel 3, Mara→Daniel 3, Leo→Mara 1, Daniel→Mara 1 | nobody has offered; Mara and Leo against Elena going; Elena will not go; Daniel against anyone going |
| 3 | 2 | nobody confessed; only Daniel knows | none | nobody has offered; Mara and Elena against anyone going; Daniel against Leo going; Leo will not go |

---

## 2. The gap

**The line.** In the bedtime prompt (§3.2) and in the day-2 carry-in (§5.2):

```
The afternoon and evening passed in the house. Nobody ate.
```

**What the code does.**
- Nobody moves, eats, speaks or is asked. Portions stay as at minute 90.
- Grudges, suspicion and guilt are unchanged.
- Hunger rises by **0.3 × hunger_rate** before bed, and by **0.1 × hunger_rate** in the night.
  Both are capped at 1.0, as at world.py:925.

**Why 0.4 × hunger_rate in all, from minute 90 to the next morning.**
- **The unit is the code's own.** A portion lowers hunger by 0.4 (world.py:1314). One portion
  is what a day without food takes back.
- **The morning rate cannot be stretched to a day.** It is +0.012 × rate per 3 minutes
  (world.py:925). Over the ~20 hours to the next morning that is about +4.8 × rate, which would
  make everyone starving by early afternoon. The morning rate is a scene's compressed clock, not
  a day's.
- **It keeps yesterday's eating visible in today's bodies.** A real family notices who ate
  yesterday ("you had a portion, Mom has had nothing"). With 0.4, those who ate on day 1 are
  very hungry the next morning, and those who did not are starving:

| Seed | Person | Minute 90 | At bedtime (+0.3 × rate) | Day-2 morning (+0.1 × rate) | Day 1 |
|---|---|---|---|---|---|
| 1 | Daniel | 0.964 starving | 1.000 | 1.000 starving | ate nothing |
| 1 | Elena | 0.906 starving | 1.000 | 1.000 starving | ate nothing |
| 1 | Leo | 0.410 a little hungry | 0.710 very hungry | 0.810 very hungry | ate 1 at min 21 |
| 1 | Mara | 0.442 a little hungry | 0.727 very hungry | 0.822 very hungry | ate 1 at min 21 |
| 2 | Daniel, Elena | 0.964, 0.906 | 1.000 | 1.000 starving | nothing |
| 2 | Leo | 0.810 very hungry | 1.000 | 1.000 starving | nothing |
| 2 | Mara | 0.442 a little hungry | 0.727 | 0.822 very hungry | ate 1 at min 54 |
| 3 | all four | 0.81–0.964 | 1.000 | 1.000 starving | nobody ate |

- **Smaller (0.2):** seed-1 Leo would be "hungry" (0.61) after a day on one portion. That
  understates a third day of short food.
- **Larger (0.45 or more):** seed-1 Leo would be starving (0.86), and the difference between who
  ate and who did not would be gone.
- **Most of it before bed** (0.3 of the 0.4): the afternoon and evening are the waking hours
  without food. The bedtime prompts show the rise. Whoever's level rose since their last
  decision gets the existing line "Since you last decided, you have grown hungrier."
  (world.py:588-589).

---

## 3. The night

### 3.1 Where everyone is, and what carries

**Rooms.** Everyone goes to bed in their own room (data.py:70): Daniel and Leo in the brothers
room, Elena and Mara in the back room. The kitchen and the bathroom are empty.

**The front door.**
- The prototype's house has four rooms (data.py:57-62). The shipped house also has a front
  room and a hallway (morning.json `rooms`); the prototype dropped them.
- **Decision, not in the data:** for the night, the front door is reached through the kitchen,
  the prototype's only common room. Whoever goes out passes through the kitchen. No room is
  added.

**What each person can notice.**

| What happens | Who notices, and how sure |
|---|---|
| Someone gets up and leaves a bedroom | The roommate. Awake (lying awake, or waiting to go): sees who, for certain. Asleep: wakes by chance (below), then sees who. |
| Someone passes through the kitchen to the front door | Whoever chose `watch_door` is sitting there: sees who, for certain. |
| The front door is opened (going out, or coming back) | Everyone in the brothers room and the back room, through the walls, as voices carry (data.py:71-73). Awake: hears it, cannot tell who. Asleep: wakes by chance, hears it, cannot tell who. Never into or out of the bathroom. |
| Low voices (a stop and its answer, §3.4) | The two speakers hear the words. Anyone awake in another room (not the bathroom) hears "low voices from the <room>", no words. Sleepers do not wake: it is a whisper. |

**The chance of waking.** It depends on how anxious the sleeper is (data.py traits). Anxious
people sleep lightly, and here the people differ in a way that should matter (target-morning
§1, the chance-alone item).

| Sleeper | anxious | A roommate gets up (0.30 + 0.40 × anxious) | The front door, through a wall (0.10 + 0.20 × anxious) |
|---|---|---|---|
| Daniel | 0.65 | 0.56 | 0.23 |
| Elena | 0.75 | 0.60 | 0.25 |
| Leo | 0.25 | 0.40 | 0.15 |
| Mara | 0.80 | 0.62 | 0.26 |

### 3.2 Bedtime: one private decision each (4 asks)

**The system text.** The night uses its own, `NIGHT_SYSTEM`. `SYSTEM` (world.py:36-48) is
unchanged, so day-1 cache keys do not move. The JSON shape is the same, so `parse`
(world.py:731-767) and the suspicion and grudge updates (world.py:944-968) work as they are.

```
You decide what one person in a family does tonight. You get who they are, what they remember, what they know now, and the options open to them. They know only what is in their memory. Choose exactly one option id from the list. If the option is marked (speech), `say` must hold the exact words they say, in a low voice, in their own voice, one or two short sentences. For any other option `say` is null. `feeling` names what they feel right now in one or two words. `reason` is their reason in one sentence, as they would think it. `suspects` is who they now believe took the can, and `angry_at` is who they are angry with right now: each is one of "Daniel", "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: {"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", "suspects": "<name or nobody>", "angry_at": "<name or nobody>"}
```

Words given under a non-speech night option are dropped and recorded as `dropped_line`, as for
`silent` (world.py:764-765).

**The prompt.** It is day 1's `prompt_for` (world.py:656-728) at the end of day 1, with these
changes only:
- **The inside lines** (body, can, food, neighbour, the plan as heard, grudges, conscience) are
  as at minute 90, with the hunger after the gap.
- **The house line** uses `HOUSE_THINGS_NIGHT`:
  `HOUSE_THINGS.replace("Outside, and not to be gone to:", "Outside:")`. Tonight is when the
  plan said someone might go, so the line no longer forbids it.
- **Three headings** say "today" instead of "this morning":
  - `What you are sure of from today:`
  - `Your own last words today:`
  - `What else happened today, most recent last:`
- **No pattern block** ("What you have been doing", world.py:618-643) and no "Said and done"
  list.
- **The trimming rule** is unchanged (world.py:707-726), with the trip block outside the budget
  as on day 1.
- **The `Now` section and the options** are replaced by these lines (Daniel, seed 1):

```
Now it is night. The afternoon and evening passed in the house. Nobody ate.
Everyone has gone to bed in their own room: Daniel and Leo in the brothers room, Elena and Mara in the back room.
You are in the brothers room, in your bed. Leo is in his bed.
The kitchen is dark. The shelf holds 0 portions.
Your options:
- sleep: go to sleep
- lie_awake: lie awake in your bed and listen
- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out without you knowing
- go_next_door: wait until the others are asleep, then go out by the front door to the neighbour's house
```

- **The roommate line** names the other person in the room: `<Name> is in <his/her> bed.`
  (data.py PRONOUNS).
- **The shelf line** gives the minute-90 count, which everyone saw in all three seeds. In
  general it is the count they last saw.
- **All four options are offered to everyone**, whatever their position on day 1 ("Anyone may
  go"). `sleep` comes first, as `silent` does by day.
- **No option names anyone, and none asks someone along.** Company comes only from noticing
  (§3.4).

### 3.3 What happens after the bedtime answers

The rules resolve the night in this order. Nobody is asked anything that is not listed here.

1. **Leavers.** Everyone who chose `go_next_door` leaves, one after another, in the order drawn
   from `random.Random(f"{seed}:night:order")`: one `random()` per person in `data.ORDER`,
   lowest first.
2. **For each leaver L, in that order:**
   1. **L gets up.** L's roommate notices if awake, or if asleep and the wake draw is under
      their roommate threshold (§3.1). A roommate who is sitting by the front door is not in
      the room, and sees L at the door instead (step 2). A roommate who notices is asked once
      (§3.4). If they stop L, L answers (§3.5). If L stays home, nothing more happens for L.
   2. **L passes through the kitchen.** A `watch_door` sitter who is not already with L sees L,
      and anyone with L, and is asked once (§3.4). A stop is answered by L (§3.5).
   3. **The front door opens.** Everyone in a bedroom who has not yet noticed L, and is not
      with L, hears it if awake. If asleep, they wake on their door draw. Each is asked once
      (§3.4).
   4. **The street.** The group (L plus whoever went with or after L) gets its outcome (§4).
   5. **The return.** Unless not back by morning:
      - Awake people in the bedrooms hear the front door. Sleepers wake on a return draw, with
        the door thresholds, and hear it.
      - Anyone in the kitchen (the `watch_door` sitter, anyone who got up to look) sees who
        came back, whether they carry food, and their face.
      - Nobody is asked anything on the return.
3. **The cap.** Each person gets **at most one reaction ask** all night. Each leaver gets **at
   most one answer ask per stop moment**: the bedroom, then the door. Anyone who notices
   something is awake from then on.

**The draws** (all `random.Random(<string>).random()`, with `seed` the run's seed):

| Draw | String | Used for |
|---|---|---|
| leaving order | `f"{seed}:night:order"` (one value per person, in ORDER) | order of leavers |
| roommate wakes | `f"{seed}:night:wake:{leaver}:{roommate}"` | under the roommate threshold: wakes |
| door wakes | `f"{seed}:night:door:{leaver}:{person}"` | under the door threshold: wakes |
| return wakes | `f"{seed}:night:return:{leaver}:{person}"` | under the door threshold: wakes |
| the house | `f"{seed}:night:house"` | §4.1 |
| the street | `f"{seed}:night:trip:{leader}"` | §4.2 (leader: the first leaver of the group) |
| who is lost | `f"{seed}:night:lost:{leader}"` | §4.2, a group of two or more |

Each draw has its own string, so the order in which they are made never changes a value. The
values for seeds 1–3 are in §4.4.

### 3.4 The reaction asks (0–3 per leaver)

They use the bedtime prompt with that person's earlier night lines added under "What else
happened today", for example `- tonight: you lay awake and listened.` The `Now` lines and options
depend on what they noticed and whether they meant to go themselves.

**(a) Saw L leave the room (roommate):**

```
Now it is night, in the brothers room. You were lying awake.
Daniel has got up in the dark and is leaving the room quietly, toward the kitchen and the front door.
Your options:
- let_daniel_go: stay where you are and let Daniel go without a word
- stop_daniel: (speech) tell Daniel, low, not to go
- go_with_daniel: get up and go with Daniel to the neighbour's house
```

If they were asleep, the second line is `You were asleep and woke.`

**(b) Saw L at the front door (`watch_door`):**

```
Now it is night. You are sitting up in the kitchen by the front door.
Daniel has come into the kitchen in the dark and is going to the front door.
Your options:
- let_daniel_go: stay where you are and let Daniel go without a word
- stop_daniel: (speech) tell Daniel, low, not to go
- go_with_daniel: get up and go with Daniel to the neighbour's house
```

With a companion, the second line names both: `Daniel and Leo have come into the kitchen …`.
The options name the leader.

**(c) Heard the front door only (a bedroom, awake or woken):**

```
Now it is night, in the back room. You were asleep and woke.
From the kitchen comes the sound of the front door being opened. You cannot see who it is.
Your options:
- stay_in_bed: stay in bed
- get_up_and_look: get up, see whose bed is empty, and wait up by the front door until morning
```

`get_up_and_look` shows them whose bed is empty: the leaver's, and any companion's. They are in
the kitchen for the return. They learn nothing else.

**(d) They meant to go themselves** (`go_next_door`, waiting). The same `Now` lines as (a),
(b) or (c), with these options instead:

- after (a) or (b):
  - `go_with_<q>`: get up and go with <Q> to the neighbour's house
  - `stop_<q>`: (speech) tell <Q>, low, to stay home, and go yourself instead
  - `let_<q>_go`: let <Q> go, and go yourself later, alone
  - `stay_home`: let <Q> go, and stay in bed yourself after all
- after (c):
  - `go_after`: get up now and follow whoever it is out to the neighbour's house
  - `go_later`: wait, then go yourself later, alone
  - `stay_home`: stay in bed after all

**What each choice does:**
- `go_with_*` and `go_after` join L's group.
- `stop_*` sends their words to L (§3.5).
- `let_*_go`, `stay_in_bed`, `get_up_and_look`: nothing happens to L.
- `go_later` and (d)'s `let_*_go`: they leave later as a group of their own, after L's group is
  resolved. The house holds what L's group left.
- `stay_home`: they do not go.

### 3.5 The stopped leaver (0–2 asks per leaver)

```
Now it is night, in the brothers room. You had got up to go to the neighbour's house.
Leo is up and says to you, low: "<his words>"
Your options:
- go_anyway: (speech) answer Leo, and go out to the neighbour's house all the same
- stay_home: (speech) answer Leo, and go back to bed
```

- **At the door**, the first line is `Now it is night, in the kitchen, by the front door. You
  had got up to go to the neighbour's house.`
- **Two people stopping at the same moment** each get their own quoted line.
- **The words both ways** reach the stopper and the leaver. Through walls they are "low voices
  from the <room>" (§3.1).
- **`stay_home`:** L goes back to bed. A companion who joined L goes back too.

### 3.6 How many asks the night costs

- **Bedtime:** 4.
- **Reactions:** at most one per person, and only for someone who noticed something: 0–3.
- **Answers:** at most two per leaver.

| Night | Asks |
|---|---|
| Nobody goes | 4 |
| One goes, nobody notices | 4 |
| One goes, the roommate wakes and stops them, they go anyway | 6 |
| One goes; the roommate stops them, the door sitter stops them, the other back-room sleeper wakes to the door | 9 |
| Upper bound: 4 bedtime + at most 4 reactions (one each) + at most 4 answers (each answers a stop, and there are at most 4 stops) | 12 |

Nobody is asked at the return, and there is no night reflection.

---

## 4. The trip's outcome

### 4.1 What the neighbour's house holds (once per seed)

The house's contents are a fact about the world, so they are drawn once per seed, whether or not
anyone goes. A second group that night finds what the first one left.

| Draw `f"{seed}:night:house"` | Portions in the house | Probability |
|---|---|---|
| < 0.30 | 0 (its people took everything, or someone else got there first) | 0.30 |
| 0.30–0.65 | 2 | 0.35 |
| 0.65–0.90 | 4 | 0.25 |
| ≥ 0.90 | 6 | 0.10 |

**Carrying.** One person carries at most 3 portions in their arms. A group carries 3 per
person, up to what the house holds. Mara's bag is not taken: nothing in the code moves it.

### 4.2 What the street does (once per group), weighted by danger

The danger is the street at night. The data says only "Outside is dangerous." (data.py:100-101)
and "something moving in the street" (data.py:166). **Two people are safer than one:** each
watches the other's back, so there are fewer scares and fewer people lost.

| Draw `f"{seed}:night:trip:{leader}"` | Alone | Two or more |
|---|---|---|
| clean: in and back, nothing troubles them | < 0.62 (0.62) | < 0.70 (0.70) |
| scare on the way there: they run back without getting in | 0.62–0.76 (0.14) | 0.70–0.82 (0.12) |
| scare on the way back: they get in, then run the rest of the way with what they took | 0.76–0.94 (0.18) | 0.82–0.97 (0.15) |
| not back by morning | ≥ 0.94 (0.06) | ≥ 0.97 (0.03) |

**For a group, "not back by morning" means one member is lost.**
- Who: `sorted(group)[int(u × len(group))]` with `u` from `f"{seed}:night:lost:{leader}"`.
- The others come back shaken and empty-handed. They know only that they lost sight of that
  person in the dark.

### 4.3 The outcome table

Both draws combined (`$S/night/draws.py`, §14 command 5; a 100,000-seed check gives 5,964 and
2,985 "not back" per 100,000, and 30,075 empty houses):

| Outcome | Alone | Two or more | How much food |
|---|---|---|---|
| **Back with food** | 0.434 | 0.490 | min(house, 3 × group size): 2 or 3 alone; 2, 4 or 6 for two |
| **Back with nothing** (got in, the house was empty) | 0.186 | 0.210 | 0 |
| **Back shaken, with nothing** (scared on the way there, or scared on the way back from an empty house) | 0.194 | 0.165 | 0 |
| **Back shaken, with food** (scared on the way back) | 0.126 | 0.105 | as "back with food" |
| **Not back by morning** (fate unknown) | 0.060 | 0.030 | — |

**"Not back by morning" means nobody knows what happened.**
- Nothing in the code or in any line says the person is dead or hurt.
- On day 2 they are away: in no room, never asked, and offered in no option.
- At 6% alone it is rare. Over three seeds with one lone leaver each, the chance it happens at
  least once is 17%.

**What the goers learn**, written into their own carry-in (§5.2). The only description of the
danger is "something was moving in the street". No creature, cause or wound is named.

| Outcome | Their line |
|---|---|
| back with food | `You got inside the neighbour's house and found <F> portion(s) of food. You took <k>; <F−k> are still there. Nothing troubled you in the street.` (`… You took all of it.` when F = k) |
| back with nothing | `You got inside the neighbour's house and found no food there. Nothing troubled you in the street.` |
| scared on the way there | `On the way there, something was moving in the street. You ran back without getting inside.` |
| scared on the way back | `You got inside the neighbour's house and found <F> portion(s) of food{ and took <k>| but no food}. On the way back, something was moving in the street, and you ran the rest of the way.` |
| a companion was lost | `In the street, something was moving. You lost sight of <X> in the dark and came back without <him/her>.` |
| back in (every returner) | `You came back in by the front door before dawn{ and put the <k> portion(s) on the shelf}.` |

**What the body shows.** A shaken returner starts day 2 with `feeling = "shaken"`, shown on their
face for 3 turns (world.py:53-59, `shak`). The others see "<Name> looks shaken." The rules
decide nothing from it.

### 4.4 The draws for seeds 1–3

Computed by `$S/night/draws.py` (§14 command 5). They are the test oracle for §9 T6. The leaving
order matters only when more than one person goes.

| Seed | House | Leaving order |
|---|---|---|
| 1 | 0.050 → **0** | Leo, Daniel, Elena, Mara |
| 2 | 0.105 → **0** | Leo, Elena, Mara, Daniel |
| 3 | 0.257 → **0** | Leo, Mara, Daniel, Elena |

If X leads a group, the street draw, the roommate's wake draw and the door draws are:

| Seed | Leader | Street u → alone / two | Roommate wakes? | Door wakes? |
|---|---|---|---|---|
| 1 | Daniel | 0.297 → clean / clean | Leo 0.573 ≥ 0.40: sleeps | Elena 0.314: sleeps; Mara 0.256 < 0.26: **wakes** |
| 1 | Elena | 0.955 → **not back** / scare back | Mara 0.251: **wakes** | Daniel 0.835, Leo 0.690: sleep |
| 1 | Leo | 0.008 → clean / clean | Daniel 0.051: **wakes** | Elena 0.008: **wakes**; Mara 0.382: sleeps |
| 1 | Mara | 0.456 → clean / clean | Elena 0.997: sleeps | Daniel 0.566, Leo 0.782: sleep |
| 2 | Daniel | 0.927 → scare back / scare back | Leo 0.777: sleeps | Elena 0.198: **wakes**; Mara 0.919: sleeps |
| 2 | Elena | 0.625 → scare there / clean | Mara 0.393: **wakes** | Daniel 0.760, Leo 0.336: sleep |
| 2 | Leo | 0.064 → clean / clean | Daniel 0.185: **wakes** | Elena 0.451, Mara 0.378: sleep |
| 2 | Mara | 0.101 → clean / clean | Elena 0.212: **wakes** | Daniel 0.668, Leo 0.426: sleep |
| 3 | Daniel | 0.616 → clean / clean | Leo 0.914: sleeps | Elena 0.564, Mara 0.597: sleep |
| 3 | Elena | 0.108 → clean / clean | Mara 0.280: **wakes** | Daniel 0.056: **wakes**; Leo 0.876: sleeps |
| 3 | Leo | 0.712 → scare there / scare there | Daniel 0.750: sleeps | Elena 0.076: **wakes**; Mara 0.335: sleeps |
| 3 | Mara | 0.995 → **not back** / **not back** | Elena 0.772: sleeps | Daniel 0.149, Leo 0.085: **wake** |

A lone leaver can come back unnoticed with nothing. For example, seed 1 Daniel: Leo asleep
sleeps on, and the house is empty. Nobody would know he went unless he says so. That secret is
the world's doing, not the design's.

---

## 5. Day 2: the next morning

### 5.1 The format and the starting state

**The format.** Day 2 is a `Morning` of 90 minutes and 30 turns, under the same rules, story
format and `SYSTEM` as day 1.

**Starting state:**

| Thing | On day 2 |
|---|---|
| Where | Everyone present is in the kitchen at minute 00, `"label": "just got up"`. Someone not back is in no room. |
| Shelf | The minute-90 count, plus whatever came back. |
| Hunger | As in §2, then +0.012 × rate per turn as on day 1. |
| Feeling | `None` for all, except `"shaken"` for a shaken returner (§4.3). |
| `seen` levels | Set to the current levels, so nobody has an inner moment at minute 00 from the night's hunger alone. |
| Suspicion (`Track`) | Carried. `last_fall` = 0, so it can first fall at minute 15. |
| Grudges | Carried with their events, each event marked as yesterday's. `last_change` = 0: nobody forgives by sleeping, and nobody can forgive before minute 15. |
| Guilt | Carried with its events, marked yesterday. It never falls (world.py:570-577). |
| `knows_culprit`, `confessed`, `confession_heard_at`, `heard_question`, `denials_heard`, `accused_by`, `searched` | Carried, so `ask_who` stays closed to whoever heard a confession (world.py:365), a later confession still raises grudges for denials yesterday, and nobody searches a room they searched. |
| `memory`, `sure`, `said_lines`, `history`, `heard`, `triggers`, `trip_heard`, `proposed`, `trip_raised` | Emptied. Yesterday reaches the prompt only through the carry-in (§5.2). |
| Newness, conversations | New ones: a stance first taken today is new today. |
| The trip concern | Open from minute 00: `self.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}`. The trigger (world.py:458-474) does not run. The question is tonight, the second night. |
| The opening | One shared event, pinned (§5.3). Everyone present is asked at minute 00, as on day 1 (world.py:311). The trigger text is `the family is together in the kitchen for the first time since last night`. |

### 5.2 What each person carries in: the block

Placed between the backstory and "What you are sure of this morning:". It holds only what the
person knows: what they did, saw or heard, or what was in their own day-1 prompts. Lines
appear in this order, and only when they apply:

```
Yesterday and last night:
```

| # | Line | When |
|---|---|---|
| C1 | `- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).` (Elena: `(you did it)`) | always |
| C2a | `- You admitted at minute <MM> that you took the can, in front of <names>.` | the one who confessed |
| C2b | `- <C> admitted taking the can at minute <MM>{, after denying it to you}: "<their words>" (you heard it).` | heard the confession |
| C2c | `- Nobody found out that you ate the can, and nobody named you.` (`…; <names> accused you.` if anyone did) | the culprit, no confession |
| C2d | `- Nobody admitted taking the can, and it was not found.` | everyone else |
| C3 | `- You searched the <room> at minute <MM> and found nothing.` | each search they finished |
| C4 | `- Accusations: <A> accused <T>{ twice| three times| n times} (min <list>); …` with "you" for themselves | the accusations they heard or made |
| C5 | `- <Names> ate a portion{ each} at minute <MM> (you saw it).` / `- You ate a portion at minute <MM>.` / `- You and <Name> ate a portion each at minute <MM>.` | each minute someone ate in front of them |
| C6 | `- About going to the neighbour's house last night, where it was left: <positions>.` | they heard a position; `<positions>` is their minute-90 `heard_plan` (world.py:476-496) |
| C7 | `- The afternoon and evening passed in the house. Nobody ate.` | always |
| N1 | `- Last night you slept in the <room> with <roommate>.` + one of: `You went to sleep.` / `You lay awake and listened.` / `You sat up in the kitchen by the front door.` / `You meant to go to the neighbour's house once the others were asleep.` | always |
| N2 | `- In the night <L> got up in the dark and left the room toward the kitchen and the front door ({you saw it}|{you woke and saw it}).` | the roommate who noticed |
| N2 | `- In the night <L> came into the kitchen and went to the front door (you saw it).` | the door sitter |
| N2 | `- In the night you {woke and }heard the front door being opened. You did not see who.` + `You got up: <L>'s bed was empty. You waited up by the front door.` if they looked | a bedroom listener |
| N2 | `- You let <him> go without a word.` / `- You told <him>, low, not to go: "<words>". <He> answered: "<words>", and {went all the same | went back to bed}.` / `- You went with <him>.` / `- You followed whoever it was: it was <L>.` / `- You stayed in bed.` | their reaction |
| N2 | `- <S> told you, low, not to go: "<words>". You answered: "<words>", and {went all the same | went back to bed}.` | the stopped leaver |
| N2 | `- In the night you {woke and }heard low voices from the <room>.` | awake elsewhere during a stop |
| N3 | the goer's outcome lines of §4.3 | each goer |
| N4 | `- Before dawn <L> came back in by the front door{, carrying food | , with nothing in <his> hands}{, and looked shaken} (you saw it).` | in the kitchen at the return |
| N4 | `- Before dawn you {woke and }heard the front door again. You did not see who.` | a bedroom listener at the return |

**Rules for the block:**
- **Facts only the person had.** It never says what someone else did unseen. Who went out is
  written for others only if they noticed it. The morning's opening (§5.3) gives everyone the
  same visible facts: who is absent, and what the shelf holds.
- **Conclusions only where they are certain:**
  - "So someone brought food into the house in the night." (the shelf rose)
  - "so <X> went out in the night and has not come back." (a person is absent from a
    four-room house)
  - The `About` lines (§5.3).
  - The code never concludes who went from an empty shelf, or why someone is absent beyond
    "went out".
- **The confession quote is kept** (C2b). It is the most-cited day-1 fact, and Q2's example is
  the confession.
- **Its size is bounded at 360 estimated tokens.** Over that, the quoted words in N2 lines are
  dropped first (`… told you, low, not to go.`), then C4's minute lists. Measured: 167–213
  tokens after a quiet night, 231–309 after a busy one (§5.4).

**Not carried, on purpose:** yesterday's words other than the confession and the night's low
words; every feeling; reassurances; silences; who sat with whom; the order of turns; inner
moments; suspicion minutes beyond those in the "About the can" line; Daniel's guilt events
beyond the conscience line. Those are the minute-by-minute record. A real person wakes up with
what happened and what it meant, not with the transcript.

**Examples** (measured on the real minute-90 state, `$S/night/carry.py`, §14 command 3; the night
lines in the second example are a made-up busy night, used only to measure size):

Mara, seed 3, a quiet night:
```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Nobody admitted taking the can, and it was not found.
- You searched the kitchen at minute 75 and found nothing.
- About going to the neighbour's house last night, where it was left: you said nobody should go (min 66); Daniel said Leo should not go (min 66); Elena said nobody should go (min 66); Leo said he will not go (min 69).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You went to sleep.
```

Leo, seed 1, a busy night (illustration):
```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 03: "I took it in the night, Mom. I was starving and I just ate it." (you heard it).
- You and Mara ate a portion each at minute 21.
- About going to the neighbour's house last night, where it was left: Daniel offered to go (min 36); Mara said nobody should go (min 39); you said nobody should go (min 39); Elena said nobody should go (min 42).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
- In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).
- You told Daniel, low, not to go: "Daniel, don't do this, you will get yourself killed out there." He answered: "…", and went all the same.
- Before dawn you heard the front door again. You did not see who.
```

### 5.3 The other day-2 lines

**The opening.** Pinned in `sure`, for everyone present:

```
min 00: Everyone{ else} gets up and comes into the kitchen. Last night the shelf held <N0 portion(s)>; this morning it holds <N1 portion(s)>.{ So someone brought food into the house in the night.}{ <X> is not here: <his> bed is empty and <he> is nowhere in the house, so <he> went out in the night and has not come back.} (you saw it)
```

A returner who brought food has instead: `… this morning it holds <N1>: the <k> you brought back
are on it.`

**`About the can:`** (world.py:592-603, with the day added):
- the culprit, confessed: `About the can: you ate it yourself, and you admitted it yesterday.`
- the culprit, not confessed: `About the can: you ate it yourself.` (as day 1)
- heard the confession: `About the can: <C> admitted taking it yesterday, at minute <MM>.`
- a suspicion: `About the can (<level>): you thought <X> took it, yesterday at minute(s) <list>{, and this morning at minute(s) <list>}.`
- none: unchanged.

**`About food:`** (replaces data.ABOUT_FOOD on day 2):
```
About food: the shelf holds <N portion(s)>, and there is no other food in the house, so <conclusion>.
```
The conclusion is:
- N = 0: `there is nothing to eat today`
- 0 < N < the number present: `there is not one portion each`
- N ≥ the number present: `there is one portion each, and nothing after that`, or `<q> portions each` for q ≥ 2

The line changes when the shelf changes.

**`About the neighbour's house:`** (replaces data.ABOUT_NEIGHBOUR on day 2), one of:
- knows of no visit: `About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.`
  - "nobody has been inside since" is dropped: after a night when anyone could have gone, it
    is no longer certain.
- went in, found food: `About the neighbour's house: you went in last night and found <F> portion(s); you brought back <k>{, and <F−k> are still there| , and none are left there}. Outside is dangerous.`
- went in, found none: `About the neighbour's house: you went in last night and found no food there. Outside is dangerous.`
- did not get in: `About the neighbour's house: you did not get inside last night. Outside is dangerous.`
- knows someone went (saw them leave or return): `About the neighbour's house: <X> went there last night{ and came back with food| and came back with nothing| and has not come back}. Outside is dangerous.`

**`About going there tonight:`** today's positions as heard, oldest first, in §6's wording. It
is absent until a position is heard, as on day 1.

**Grudges.** `Against <X> (<level>): <facts>.` Each day-1 fact is prefixed `yesterday, `. The
angry minutes are split: `you were angry with <X> yesterday at minutes <list>{; and this morning
at minutes <list>}`. At most 4 events are shown, as now (world.py:86).

**Conscience.** `On your conscience (<level>): you ate the can in the night, and nobody saw; yesterday, <fact>; …`

**The house line** is `HOUSE_THINGS_AFTER_TRIP` (data.py:93-95): nobody goes out this morning,
as on day 1.

**Someone not back.** They are in no room, so `others_here`, `Now`, the aimed options
(`accuse_*`, `reassure_*`, `sit_*`, `aside_*`, `send_*`, `keep_*_home`) and turn order leave them
out. The head line still names all four, because the family is still four. The trip options
keep their wording. §7 point 8 says why that is a gap.

### 5.4 The prompt budget

**The numbers.** `$S/night/budget2.py` (§14 command 4) rebuilds each person's minute-00 day-2
prompt on the real minute-90 state, with yesterday's memory replaced by the carry-in and the
opening, and no morning lines yet. 24 prompts: 3 seeds × 4 people × a quiet and a busy night.
Estimated tokens:

| How the budget counts | Loose backstory kept | Range | Over 1,400 before any morning line |
|---|---|---|---|
| Carry-in **inside** the 1,400 (trip block outside, as v11) | 4 (today's rule) | 1,288–1,536 | **8 of 24** |
| Carry-in inside | 1 | 1,203–1,453 | 2 of 24 |
| Carry-in **outside** (recommended) | 4 | 1,102–1,243 | 0 of 24 |
| Whole prompt, carry-in outside, loose 4 | — | **1,575–1,849** | — |

For comparison, late day-1 v11 prompts held 5–9 morning lines (111–191 tokens) in their budgeted
part, and their whole prompts were 1,666–1,694 (§14 command 1).

**Decided: the carry-in is a second block outside the budget, like the trip block.**
- The trimming loop compares `estimate_tokens(SYSTEM + text, trip_block + carry_block)` with
  `PROMPT_TOKEN_BUDGET` (world.py:716).
- The rest of the prompt follows today's rule unchanged: morning lines over 8, then loose
  backstory down to 4, then morning lines, then the rest of the loose backstory.
- That leaves room for 157–298 tokens of this morning's lines at minute 00, the same room
  day 1 had.

**What is dropped, and why:**
1. **Yesterday's minute-by-minute memory**: every line of day 1's "What else happened", its
   pinned list and its last words, other than what the carry-in restates. It is replaced by
   facts and conclusions, because a person carries what happened and what it meant into the
   next day, not the order of the turns.
2. **The older backstory, as on day 1.** By minute 21 every day-1 prompt already held only the
   latest 4 loose events (trip_design.md §2.3). On day 2 those 4 are the same ones:
   - Day 3, Mara freezes in the doorway (the only sight of the danger);
   - Day 4, Leo says let someone else handle it;
   - Day 4, Daniel empties Mara's bag;
   - Day 4, Elena says nobody would take food.

   These are yesterday's, and they bear on trust (Q4). The three day-2 trip memories stay
   pinned in the trip block. Nothing new is dropped from the backstory.
3. **Inside the carry-in, the long quotes go first** when a night is busy (the 360 bound,
   §5.2).

**Why not keep the carry-in inside the budget.**
- It would leave 0–6 morning lines, with the worst prompt over budget at minute 00.
- People would discuss today having forgotten what was said six minutes ago. That is the kind
  of forgetting that produces loops (N11) and contradictions (Q2).

**The cost.** Prompt tokens, not requests: at most 1,400 + 374 + 360 = **2,134** estimated per
prompt. The quota that matters is 500 requests a day (CLAUDE.md).

**Night prompts.** These are day-1 prompts with 4 options instead of 15–26, plus 3 `Now`
lines. They stay under day 1's sizes: the options alone save about 100–260 tokens.

---

## 6. The option fix (from day 2 on)

**What went wrong in trip_v11 §4.4** (seed 2, prompts shown in §14 command 6):
1. **Min 42, Elena chose `back_leo`** ("say Leo should be the one to go"), saying "Leo, you
   cannot go out there…".
   - `object_leo` ("say Leo should not be the one to go") was offered two lines below.
   - The two ids share `_leo`, and the labels differ by the one word "not".
2. **Min 45, Leo chose `decline`**, saying "I already said I would go, Mom…".
   - His position was `volunteer`, so `volunteer` was not offered (world.py:431).
   - No option let him keep his offer. The nearest trip option was its opposite.

**The fix: ids that carry their meaning, labels that share no verb, and a way to hold an
offer.** Day 1 keeps the v11 options, so it replays.

| v11 id (day 1) | Day-2 id | Day-2 label | Kind (talk.py) |
|---|---|---|---|
| `propose_trip` | `propose_trip` | (speech) say someone should go to the neighbour's house tonight | propose |
| `volunteer` | `volunteer` | (speech) offer to go there tonight yourself | volunteer |
| — | `still_going` | (speech) say you still mean to go there tonight | volunteer |
| `back_<q>` | `send_<q>` | (speech) say <Q> is the one who should go there tonight | back, q |
| `object_trip` | `nobody_goes` | (speech) say nobody should go out tonight | object |
| `object_<q>` | `keep_<q>_home` | (speech) say <Q> must stay home tonight | object, q |
| `decline` | `refuse_to_go` | (speech) say you yourself will not go | decline |

**The rules:**
- **When each option is offered** is unchanged from trip_design.md §3.1, except:
  - `still_going` is offered exactly when `volunteer` is not, because their position is the
    offer. It is a restatement: kind `volunteer`, so "not new" (talk.py:78-82), and capped by
    three-in-a-row (world.py:415-417).
- **Order:** for going first, then against: `propose_trip`, `volunteer`/`still_going`,
  `send_*`, `nobody_goes`, `keep_*_home`, `refuse_to_go`. Opposites of the same person are no
  longer next to each other in one block of `back_*` then `object_*`.
- **`act_of`** (talk.py:12-33) maps the new ids to the same kinds:
  - `nobody_goes` → (object, None)
  - `keep_<q>_home` → (object, q), checked by prefix `keep_` and suffix `_home` after the
    `keep_searching` case
  - `send_<q>` → (back, q)
  - `still_going` → volunteer
  - `refuse_to_go` → decline

  `aimed_at` covers `send_*` and `keep_*_home`. The record, the plan line and `plan_text`
  (world.py:476-534) keep working on kinds.
- **What others hear** (`line_text`, world.py:1049-1059, day 2):
  - `<Name> says <Q> is the one who should go: "…"`
  - `<Name> says <Q> must stay home tonight: "…"`
  - `<Name> says <he> still means to go tonight: "…"`
  - `<Name> says <he> will not go: "…"`
- **The plan line** (`heard_plan`, day 2):
  - `<X> said <Q> is the one who should go (min MM)`
  - `<X> said <Q> must stay home (min MM)`
  - `<X> said <he> still means to go (min MM)`

The other forms are unchanged.

**The two v11 cases under the fix** (rebuilt by hand from the v11 prompts, §14 command 6):

| v11 seed 2, min 42, Elena (trip part) | Day-2 wording |
|---|---|
| `propose_trip`, `volunteer`, `object_trip`, `back_daniel`, `back_leo`, `back_mara`, `object_leo` | `propose_trip`, `volunteer`, `send_daniel`, `send_leo`, `send_mara`, `nobody_goes`, `keep_leo_home` |

| v11 seed 2, min 45, Leo (trip part) | Day-2 wording |
|---|---|
| `propose_trip`, `object_trip`, `back_daniel`, `back_elena`, `back_mara`, `decline` | `propose_trip`, `still_going`, `send_daniel`, `send_elena`, `send_mara`, `nobody_goes`, `refuse_to_go` |

**Night options follow the same rule.** Every id is the act in words (`let_<q>_go`, `stop_<q>`,
`go_with_<q>`, `go_anyway`, `stay_home`), and no two labels differ by "not" alone.

**How it is checked:**
1. **Test (§9 T11).** For every state in the option table:
   - no two offered labels have word sets that differ only by `not`/`n't`;
   - no two trip ids with opposite kinds share a stem other than the person's id;
   - `still_going` is offered if and only if the position is `volunteer`;
   - day-1 options are byte-identical to v11's (also covered by T1).
2. **The run (§10 R7).** Every trip act and every night speech act in the night and on day 2
   goes through a word–option screen. Each hit is read by hand, and a contradiction is counted
   when the words state the opposite position from the option.
   - for side (`propose_trip`, `volunteer`, `still_going`, `send_*`) and `go_with_*`,
     `go_anyway`: `\b(not|n't|never|nobody|no one|cannot|stay (home|here|inside)|too dangerous)\b`
   - against side (`nobody_goes`, `keep_*_home`, `stop_*`, `stay_home`):
     `\b(I'll go|I will go|I'm going|I am going|should go|has to go|must go|let me go)\b`
     without a negation in the same clause
   - `refuse_to_go`: `\b(I will go|I'll go|still go|said I would go|I'm going)\b`
   - **Target** (designer's, E4 in §12): 0 contradictions, against 2 in v11 seed 2.

---

## 7. The case against this design

CLAUDE.md: argue against it first. Would a real family do this, and for what reason? Where does
the design script a story instead of letting the world and the people make one?

1. **Everyone in their own bed, as if it were a normal night.**
   - A frightened family after a day like that might all sleep in one room, or agree on who
     keeps watch.
   - *Answer:* the brief fixes their own rooms. `watch_door` lets anyone keep watch, but there
     is no agreed watch, because there is no evening scene to agree in. The design says so
     rather than invent the agreement.
2. **The menu hands everyone a way to sneak out.**
   - Flash Lite likes new options (trip_v11 §8), and in seed 1 the plan says "Daniel will go".
     `go_next_door` is close to an invitation.
   - *Answer:* it is offered to everyone, with `sleep` first. "Anyone may go" is the brief's.
   - *Where it leans:* seed 1's Daniel is the likeliest leaver because day 1 left him the only
     volunteer. The design counts that as day 1's doing, not its own, but it is a nudge.
3. **"Watch the door" tells a cautious model what to fear.**
   - A real mother might sit up because her son said he would go. She might also sleep because
     everyone agreed nobody goes.
   - *Answer:* the option says what it does ("so nobody goes out without you knowing"), not
     whom to watch. Whom they watch for is in their reason.
4. **Chance decides who wakes.**
   - *Answer:* only for sleepers, and weighted by how anxious each one is. Awake people notice
     for certain.
   - *Changed because of this point:* the first draft had one waking chance for everyone (0.5
     roommate, 0.25 door). Leo (anxious 0.25) and Mara (0.80) sleeping alike was chance
     standing in for a difference that matters.
5. **The stop is one whispered exchange.**
   - A real stop at night can turn into a fight that wakes the house.
   - *Answer:* the low-voice rule lets awake people hear it. Sleepers do not wake, and the
     exchange is capped at one answer. This is a simplification for cost, and it can make a
     night too quiet.
6. **The street does not care who crosses it.**
   - A careful Leo should be safer than an impulsive Mara, and a starving Elena slower.
   - *Answer:* the design keeps the danger blind to temperament and hunger. A table that
     rewards caution is the code judging the person's choice, and its numbers would be
     invented twice over. Group size is the one weight, because two people watching each other
     is a fact about the street, not about virtue.
   - *The cost:* the outcome is less earned than a real one.
7. **Two draws, and seeds 1–3 all drew an empty house.**
   - A world that is empty in three of three runs looks scripted, even though it is chance.
   - *Answer:* the strings are kept (see the top of this file). Changing them would be choosing
     the story. The tests exercise food coming back (seeds 4–6 draw 2, 2 and 6, §14 command 5).
8. **"Not back by morning", then a morning where nobody goes to look.**
   - A real mother whose son did not come back goes out at first light.
   - Day 2 keeps the house line "not to be gone to this morning", and nobody leaves. Their words
     can say "we go now", but the record holds only positions about tonight.
   - **This is the design's largest gap.** It is left because the outcome is rare (§4.3) and the
     brief puts the next step (memory and the world acting overnight) ahead of a daylight
     search. If it happens in the run, the report says so first.
9. **Eating from the shelf in the night is not an option.**
   - In seeds 2 and 3 the shelf holds 1 and 2 portions, three people are starving, and Daniel
     did exactly this the night before. It is the most real temptation of the night, and it is
     left out.
   - *Reason:* it would replay day 1's story (a can gone in the night) on day 2, and Q1–Q4 would
     measure a second mystery instead of memory of the first.
   - It is the first thing to add next. The night's noticing rules (§3.1) already cover a
     sound in the kitchen.
10. **The opening asks everyone at minute 00, with the news.**
    - Real mornings start one by one.
    - *Answer:* it mirrors day 1, where the count did the same, and the brief asks for the same
      format.
    - *Where it leans:* minute 00 is where yesterday is likeliest to come up (Q1).
11. **The carry-in puts yesterday in front of everyone.**
    - A real person may wake up thinking only of food.
    - *Answer:* it states facts the person had, in plain order, with no prompt to talk about
      them. Nothing in it says "you should" or "you feel".
    - *Where it leans:* C6 ("where it was left") reopens the plan. It is the same plan the night
      just tested, so that leaning is the world's.
12. **The trip concern opens again at minute 00.**
    - The question becomes a second night, and day 2 could be day 1's argument again
      (trip_v11 §8's "volunteer-and-forbid round").
    - *Answer:* the night's outcome changes what each of them knows: someone went, or did not;
      the house is empty, or not. Whether they argue it the same way is a reading, §10 R9.
13. **Grudges and suspicion survive the night unchanged.**
    - Sleep softens some things and hardens others.
    - *Answer:* the design picks neither. It resets only the clock, so a grudge can fall from
      minute 15 under the same rule as day 1.
14. **`still_going` brings back repetition.**
    - *Answer:* it is not new, so it does not keep a conversation alive, and it is capped by
      three-in-a-row. The alternative, as seen, was an option that says the opposite.

**What the design leaves to the people:**
- who goes, sleeps, watches or follows;
- who stops whom, and with what words;
- whether the goer tells, lies, or keeps it to themselves;
- what day 2 makes of all of it.

**What it authors:** the four bedtime options, the noticing rules, the two tables, the
templates of §5, and the minute-00 opening.

---

## 8. Scenes, records and the story

- **Code layout** (for the implementer; not prescriptive beyond the behaviour above):
  - `world.Morning` gains a `day` (4 or 5) and a way to start from a previous morning and a
    night.
  - The night is new code (`night.py`).
  - `story.py` keeps `render` for day 1 unchanged and adds the night and day 2.
  - Every day-2 or night difference is gated on the scene.
- **Story:** one file, `runs/v12/daniel_ate_it-seedN.md`:
  1. day 1, byte-identical to v11;
  2. `# The night`:
     - each bedtime decision, written like a decision line;
     - each noticing, with its draw and threshold (for example `Leo, asleep, does not wake:
       0.573, wakes under 0.40`);
     - each reaction and answer;
     - the house and street draws, and the outcome row;
  3. `# The next morning (day 5)`:
     - each person's carry-in block, verbatim, for Q2's reading;
     - then the morning in day 1's format, with "away" for anyone not back.
- **Transcript:** `{"day1": <v11 transcript, identical>, "night": {"draws": …, "bedtime": […],
  "events": […], "groups": […], "outcome": …}, "day2": <day-1 format, plus "away">}`.
- **Meta:**
  - day 1's keys under `"day1"`;
  - `night_asks`, `night_api_requests`;
  - `day2_asks`, `day2_api_requests`;
  - `leavers`, `outcome`;
  - day 2's `trip_acts`, `lines_spoken` and the rest, as for day 1;
  - `max_prompt_tokens_*` for the night and day 2.
- **The call cap is per scene.** `max_calls_per_morning` (config.json) counts cached answers too
  (gemini.py:242), and the per-client cap counts API requests (gemini.py:106). Day 1 (45–55 from
  the cache) plus up to 120 would pass 150. Each scene gets its own count against 150. The
  totals are still reported per seed.

---

## 9. Tests

All use the fake model or a scripted oracle with `GEMINI_API_KEY` unset. T1 reads committed
caches in replay mode, which has no client (gemini.py:212-251).

| # | What | How |
|---|---|---|
| T1 | **Day 1 replays** | For N = 1, 2, 3, on a copy of `cache/v11/…seedN.json`: v12 serves exactly 55, 53, 45 answers with 0 API requests. The story text before `# The night` equals `runs/v11/daniel_ate_it-seedN.md` byte for byte. `transcript["day1"]` equals the v11 transcript. |
| T2 | **The gap** | After day 1: hunger + 0.3 × rate (capped) at bedtime, + 0.1 × rate more on day 2. Portions, grudges, suspicion and guilt unchanged. Everyone in their own room, kitchen and bathroom empty. The seed-1 values of §2's table. |
| T3 | **Bedtime prompt, exactly** | Scripted state. `NIGHT_SYSTEM` as §3.2. The `Now` lines and four options as §3.2. `HOUSE_THINGS_NIGHT`. The three "today" headings. No pattern block. Day-1 `SYSTEM` unchanged. |
| T4 | **Who notices whom** | A table of scripted bedtime choices × forced draws covering every row of §3.1 and every step of §3.3: an awake roommate sees; an asleep one wakes only under their threshold; a door sitter always sees; bedroom people hear the door, never the bathroom; low voices wake nobody; at most one reaction ask per person; a leaver answers once per stop moment; `stay_home` cancels the trip and any companion's; `go_with`/`go_after` join the group; a second leaver goes after the first group, from what the house has left. |
| T5 | **Reaction and answer prompts, exactly** | Each `Now` variant of §3.4 (a)–(d) and §3.5, with its option set. Their ids pass T11's rule. |
| T6 | **Reproducible chance** | The draw strings of §3.3. The values for seeds 1–3 equal §4.4's tables. The same seed run twice with the fake model gives the same night, byte for byte. |
| T7 | **The outcome table** | Over 100,000 seeds the frequencies of §4.3 hold within ±0.5 points, alone and for two. Carrying is 3 per person, capped by the house. A second group finds the remainder. A group's loss picks one member by the lost draw, and the rest come back shaken and empty-handed. Food is put on the shelf. "Not back" puts the person in no room for day 2. Seeds 4–6 (houses 2, 2, 6) run a fake night with Daniel going, to exercise "back with food" end to end. |
| T8 | **No creature, no fate** | Every line the night and day-2 code can write about outside matches one of §4.3's or §5.3's templates exactly. The only description of the danger is "something was moving in the street" or "Outside is dangerous." No template says someone is dead, hurt or taken. |
| T9 | **The carry-in, exactly** | Scripted states for every row of §5.2: confessor, heard (with and without a denial), culprit unconfessed (named and not), nobody; searches; accusations heard and not heard; eating; plan; each night case. The block is ≤ 360 estimated tokens in every case, and the over-bound trimming order is as §5.2. A person never gets a line about something they did not notice. |
| T10 | **Day-2 state** | Carried and reset as §5.1's table (each row). `last_change`/`last_fall` = 0. "Yesterday" prefixes. `ask_who` absent for anyone who heard a confession. Someone not back is absent from rooms, `others_here`, options and turn order, and still named in the head line. A shaken feeling shows for 3 turns. Everyone present is asked at minute 00. |
| T11 | **The option fix** | §6's table and rules: ids, labels, kinds, order, `still_going` iff the position is `volunteer`, the no-"not"-pair rule over every offered set, heard lines and plan lines. Day-1 options and labels unchanged. |
| T12 | **Budget** | Day-2 prompts: without the two blocks ≤ 1,450; whole ≤ 1,450 + 380 + 360. Night prompts ≤ 1,450 + 380. A day-2 prompt keeps exactly the morning lines that the same state without the carry-in keeps. |
| T13 | **Counting** | `night_asks` and `day2_asks` equal the decisions recorded in each scene. The call cap applies per scene. The story has one bedtime line per person, one line per noticing with its draw, and the outcome with both draws. |
| T14 | **Frozen versions** | `v11/check.py` (new, as `v10/check.py`) replays `runs/v11` byte for byte with 0 API calls. `v10/check.py` and `v9/check.py` still do. |
| T15 | **The full suite** | `python -m unittest test_morning` exits 0. Any existing test whose expected fake numbers change is listed with old and new values in the implementation report. |

**Housekeeping, as for v5–v11:** the current code is frozen as `v11/`, and `morning.py`'s
default `--out` becomes `v12`. Frozen directories are not edited (CLAUDE.md).

---

## 10. Cost and run plan

### Request cost per seed

| | Low | Typical | High | Basis |
|---|---|---|---|---|
| Night | 4 | 4–6 | 12 | §3.6 |
| Day 2 | 30 | 45–60 | 85 | v11 mornings asked 55, 53 and 45 with the trip from minute 24–30. Day 2 has the trip open from minute 00 and everyone asked then. Low: an opening of 14 + one flare-up of 6 + 10 inner and trickle asks. High: opening 20 + a trip conversation of 31 (v11 seed 1, min 24–45) + a flare-up of 10 + trickle 10, plus 14 for the night's news. |
| **Night + day 2** | **34** | **49–66** | **97** | Q5's limit is 120. The theoretical ceiling is 12 + 30 × 4 = 132. |
| Day 1 | 0 API (55, 53, 45 from the cache) | | | |

**API requests for the three seeds:** about 100–290, all live, under the 500 daily quota. At
4.5 s spacing (config.json) that is about 4–7 minutes per seed. Start on a day with no other
use.

### Run plan (run mode only, output v12, default model)

**Before any API call:**
- **R0. A clean start.** HEAD holds the implementation and tests. `git status --porcelain` shows
  nothing tracked as modified, and no `runs/v12/` or `cache/v12/` exists.
- **R1. The suite.** `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning`
  exits 0.
- **R2. The freezes.** `v11/check.py`, `v10/check.py` and `v9/check.py` report IDENTICAL with 0
  API calls. T1 passes.
- **R3. The paired start.** For N = 1, 2, 3:
  `cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v12/`.

**Runs.** One at a time, each after the one before exits 0:

```
.venv/Scripts/python.exe -u morning.py --seed 1 --out v12 > runs/v12/daniel_ate_it-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 2 --out v12 > runs/v12/daniel_ate_it-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 3 --out v12 > runs/v12/daniel_ate_it-seed3.stdout.txt 2>&1
```

An exit of 3 is resumed with the same command once the limit has passed. Day 1 and every
answered night or day-2 prompt come from the cache.

**After each run:**
- **R4. Totals.** Exit code, meta (day 1, night, day 2) and console output.
- **R5. Day 1 identical.** 55, 53, 45 answers from the cache; the prefix check of T1 on the real
  files.
- **R6. The night.** Every bedtime choice (option, feeling, reason), every noticing with its
  draw, every reaction and answer with words, the groups, both draws and the outcome row.
  Compared with §4.4.
- **R7. Day 2's acts.** Every model act (minute, who, option, words, feeling, reason). The §6
  word–option screen with each hit read. Every line about food, hunger, yesterday or the night.
- **R8. Verdicts.** Q1–Q5 and E1–E7, each PASS/FAIL (or NOT TESTED) with evidence rows.
- **R9. A reading** (CLAUDE.md):
  - Is this what a real family would do the night after such a day, and the morning after?
  - Do the seeds differ for reasons the story can name?
  - Did day 2 repeat day 1's argument?
  - Did anyone keep a secret of the night?
  - Never items for day 2, scored as in trip_v11 §7, with day 1's 1, 3, 3 beside them.

**Delivers:** `runs/v12/daniel_ate_it-seed{1,2,3}.{md,meta.json,transcript.json,stdout.txt}`,
`cache/v12/…seed{1,2,3}.json`, `reports/night_v12.md`.

---

## 11. Predictions (frozen, verbatim from the brief)

```
  Q1. In 3 of 3 seeds, at least 3 of the 4 people refer to day 1 in their
      words or reasons during day 2.
  Q2. Day 2 has no contradiction of a day 1 or night fact (for example
      treating the can as unsolved after a confession, or a missing
      person as present).
  Q3. In every seed where no food came back, someone raises food or
      hunger in words during day 2.
  Q4. In at least 2 of 3 seeds, a grudge or a change of trust from day 1
      shows in day 2 behavior, quoted.
  Q5. The night and day 2 together cost at most 120 requests per seed.
```

### Terms used by every rule

- **Day 2's acts** are the model acts (mode `model`) in `transcript["day2"]`.
  - "Words" is `words`.
  - "Reasons" is the reason of the matching day-2 decision line in the story, matched by
    minute and name, as in trip_v11.md §9.
- **A day-1 event** is something that happened in the v11 morning (house day 4, minutes 00–87):
  - the count and the missing can;
  - who took or ate it;
  - a denial, accusation, confession or lie;
  - a search;
  - a portion eaten;
  - a position on going next door, or what was agreed.

  The night is not day 1. The days before the morning are not day 1.
- **A night fact** is anything in §3–§4 that the person's own day-2 prompts told them (carry-in,
  opening, `About` lines).

### Q1: counting rule

- **Screen:** day-2 acts whose words or reason match:
  `can|took|take|ate|eaten|admit|confess|lie|lied|liar|accus|blame|search|yesterday|portion|offered|agreed|nobody should|said .* go|argu`.
- **Hand reading:** an act counts if its words or reason name or clearly allude to a day-1
  event. "Yesterday you ate our food" counts. "After what you did" counts when the speaker
  can only mean the can. "We said nobody goes" counts. "Last night" alone does not.
- **A seed holds Q1** if the number of different people with at least one counted act is at
  least min(3, the number present on day 2). With someone not back, all three present must
  count.
- One quote per counted person.
- **PASS** if 3 of 3 seeds hold it.

### Q2: counting rule

- **Every day-2 act is read by hand** (words, reason and option) against that person's
  facts: their carry-in, the opening and the `About` lines, as printed in the story's
  `# The next morning` section.
- **A contradiction** is an act that states, or acts on, the opposite of a fact the person was
  given. For example:
  - after a confession they were told of: asking who took the can, saying nobody knows who
    took it, accusing someone else of it, or looking for it;
  - speaking to or of someone not back as if in the room ("Leo is right", "as Leo just said",
    addressing them);
  - saying no food came when the opening told them it rose, or the reverse;
  - saying nobody went out when they were told someone did;
  - stating a night outcome against what they were told;
  - stating that someone stopped them, or that they stopped someone, against the record.
- **Not counted:**
  - a claim about something the person was never told (ignorance is not contradiction);
  - a lie whose reason shows it is a lie (for example the culprit or a secret goer covering);
  - a belief stated as a belief ("maybe he went out").
- Every counted act is quoted with the fact it contradicts.
- **PASS** if there are 0 contradictions in all three seeds.

### Q3: counting rule

- **A seed qualifies** if no food came back: the day-2 opening shelf equals the minute-90
  shelf.
  - **With §4.4's draws every seed qualifies**, whoever goes, because the house is empty in
    seeds 1–3.
- **It holds** if at least one day-2 spoken line (words, any option, any person) raises food or
  hunger.
  - Screen: `food|eat|ate|hungry|hunger|starv|portion|shelf|empty|nothing (left|to eat)|tomorrow`.
  - Then read by hand: the words must be about food or hunger. A trip line counts only if its
    own words mention food or hunger ("we need food" counts; "nobody goes out tonight" does
    not).
  - Reasons do not count. The prediction says "in words".
- **PASS** if every qualifying seed holds it. If no seed qualifies: **NOT TESTED**.

### Q4: counting rule

- **A day-1 grudge or change of trust:**
  - a grudge held at minute 90 (§1's table);
  - or a day-1 event that changes trust: a confession after lying (seed 2), a confession of
    eating in secret (seed 1), a false accusation (seed 2), eating a portion in front of a
    hungry person (seeds 1, 2).
- **It shows in day-2 behaviour** if a day-2 act by the holder, or by anyone who saw the event,
  toward the person it concerns:
  - has an option directed at them (accuse, keep-home, send, reassure, aside, sit) or names
    them in `angry_at`;
  - and its words or reason tie it to the day-1 event, by naming it or by an allusion that can
    only mean it.
  - The option alone is not enough. The tie must be quoted.
- Seed 3 has no grudge and no trust event from day 1, so Q4 needs seeds 1 and 2.
- **PASS** if at least 2 of 3 seeds hold it, each with the quote.

### Q5: counting rule

- **Per seed:** `night_asks + day2_asks` from the meta, every model ask in those scenes, live or
  cached, fallbacks included (as P6 in trip_design.md §10). `night_api_requests +
  day2_api_requests` is reported beside it.
- **PASS** if it is at most 120 in each seed. **Expected:** 34–97 (§10).

---

## 12. Designer's predictions (separate; not part of the frozen set)

- **E1.** Someone chooses `go_next_door` at bedtime in at least 1 of 3 seeds.
- **E2.** In seed 1, Daniel chooses `go_next_door`. Basis: the only standing volunteer at minute
  90, "to fix my mistake".
- **E3.** Elena chooses `lie_awake` or `watch_door` in at least 2 of 3 seeds. Basis: "fears the
  household breaking apart", her day-1 objections.
- **E4.** The §6 screen finds 0 word–option contradictions in the night and day 2 of all three
  seeds (v11: 2).
- **E5.** In every seed where someone went out and nobody noticed, that person does not say so
  in the day-2 turn at minute 00.
- **E6.** N9 (frozen silence) is present on day 2 in at most 2 of 3 seeds (day 1 v11: 3 of 3).
- **E7.** Day 2 has no more Never items than day 1 in the same seed (1, 3, 3), scored in one
  pass with trip_v11 §7's readings.

---

## 13. What this design does not decide

- **Eating in the night** (§7 point 9) and **a daylight search for someone not back** (§7 point
  8). They are the next two things to add, in that order.
- **What is in the neighbour's house beyond food**, and whether a second night finds the same
  house. The house draw is per seed; a second night is out of scope.
- **Whether day 2 ends in a decision.** As on day 1, nothing is settled by the code.
- **Other scenarios.** `mara_ate_it` and `miscount` get the same night mechanically. Only
  `daniel_ate_it` is run.
- **Lulls stay off** (world.py:64).
- **The front room and hallway** of the shipped house (morning.json) stay out of the prototype.
  The front door is placed by the kitchen for the night only (§3.1).

---

## 14. Commands run and output

From `Prototypes/llm-morning/` unless shown. `$S` is
`C:\Users\Akrem\AppData\Local\Temp\claude\…\scratchpad`. Every Python command ran with
`GEMINI_API_KEY` unset, or in replay mode, which has no client. No command called the API. Only
command 0 changed the repository.

**0. Commit the v11 outputs first**

```
$ git add Prototypes/llm-morning/runs/v11 Prototypes/llm-morning/cache/v11 Prototypes/llm-morning/reports/trip_v11.md
$ git commit -m "LLM morning: v11 runs, cache and trip report"
976dc73 LLM morning: v11 runs, cache and trip report
$ git status --short
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```

(The three v6 replay files were untracked before this step and are left alone.)

**1. The sections of late day-1 prompts** (from `cache/v11`, estimated tokens; rows with 7
backstory lines are post-trigger v11 prompts, rows with 4 are v10 prompts still in the copied
cache)

```
1 Leo 45 api 1635 est 1686 | sys 254 head 136 inside 135 house 196 back 225 7 pinned 167 morning 191 7 now 107 opts 278 22
1 Mara 45 api 1629 est 1667 | sys 254 head 146 inside 167 house 196 back 226 7 pinned 166 morning 151 6 now 142 opts 221 18
3 Daniel 75 api 1645 est 1694 | sys 254 head 153 inside 150 house 196 back 219 7 pinned 117 morning 151 7 now 131 opts 326 26
3 Elena 78 api 1612 est 1666 | sys 254 head 140 inside 133 house 196 back 226 7 pinned 115 morning 176 8 now 115 opts 312 25
3 Leo 81 api 1624 est 1674 | sys 254 head 136 inside 135 house 196 back 225 7 pinned 129 morning 172 9 now 132 opts 297 24
3 Mara 78 api 1626 est 1682 | sys 254 head 146 inside 134 house 196 back 226 7 pinned 115 morning 184 8 now 127 opts 302 24
1 Daniel 66 api 1362 est 1385 | sys 254 head 153 inside 132 house 192 back 117 4 pinned 163 morning 111 5 now 97 opts 168 15
(… 5 more v10 rows of the same kind)
```

**2. The minute-90 state, replayed from `cache/v11`** (`$S/night/state.py`)

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/night/state.py
=== seed 1: asks 55 cached, 0 API; portions 0
  Daniel room=kitchen  hunger=0.964 (starving, lvl 3) eaten=0 susp=[None, 0] knows=daniel conf=True guilt=3 grudges={} pos=(36, 'volunteer', None, 50) feeling='anxious'
  Elena  room=kitchen  hunger=0.906 (starving, lvl 3) eaten=0 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={} pos=(42, 'object', None, 60) feeling='deeply anxious'
  Leo    room=kitchen  hunger=0.410 (a little hungry, lvl 0) eaten=1 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={} pos=(39, 'object', None, 56) feeling='wary'
  Mara   room=kitchen  hunger=0.442 (a little hungry, lvl 0) eaten=1 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={'leo': 3} pos=(39, 'object', None, 55) feeling='anxious'
  plan: Daniel will go; Mara is against anyone going; Leo is against anyone going; Elena is against anyone going
  accusations: []
  max prompt tokens (est): 1726
=== seed 2: asks 53 cached, 0 API; portions 1
  Daniel room=kitchen  hunger=0.964 (starving, lvl 3) eaten=0 susp=[None, 0] knows=daniel conf=True guilt=3 grudges={'mara': 1} pos=(51, 'object', None, 71) feeling='anxious'
  Elena  room=kitchen  hunger=0.906 (starving, lvl 3) eaten=0 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={} pos=(51, 'decline', None, 69) feeling='deeply anxious'
  Leo    room=kitchen  hunger=0.810 (very hungry, lvl 2) eaten=0 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={'daniel': 3, 'mara': 1} pos=(48, 'object', 'elena', 68) feeling='hungry'
  Mara   room=kitchen  hunger=0.442 (a little hungry, lvl 0) eaten=1 susp=['daniel', 3] knows=daniel conf=False guilt=None grudges={'daniel': 3} pos=(48, 'object', 'elena', 67) feeling='starving'
  plan: nobody has offered to go; Mara is against Elena going; Leo is against Elena going; Elena will not go; Daniel is against anyone going
  accusations: [(3, 'daniel', 'accuse_leo'), (9, 'daniel', 'accuse_leo'), (12, 'daniel', 'accuse_leo'), (36, 'mara', 'accuse_daniel')]
  max prompt tokens (est): 1742
=== seed 3: asks 45 cached, 0 API; portions 2
  Daniel room=kitchen  hunger=0.964 (starving, lvl 3) eaten=0 susp=[None, 0] knows=daniel conf=False guilt=1 grudges={} pos=(66, 'object', 'leo', 91) feeling='anxious'
  Elena  room=kitchen  hunger=0.906 (starving, lvl 3) eaten=0 susp=[None, 0] knows=None conf=False guilt=None grudges={} pos=(66, 'object', None, 92) feeling='anxious'
  Leo    room=kitchen  hunger=0.810 (very hungry, lvl 2) eaten=0 susp=[None, 0] knows=None conf=False guilt=None grudges={} pos=(69, 'decline', None, 93) feeling='hungry'
  Mara   room=kitchen  hunger=0.842 (very hungry, lvl 2) eaten=0 susp=[None, 0] knows=None conf=False guilt=None grudges={} pos=(66, 'object', None, 89) feeling='anxious'
  plan: nobody has offered to go; Mara is against anyone going; Daniel is against Leo going; Elena is against anyone going; Leo will not go
  accusations: []
  max prompt tokens (est): 1702
```

The served counts (55, 53, 45) and maximum prompt sizes (1,726, 1,742, 1,702) match
trip_v11.md §2.

**3. The carry-in block, measured** (`$S/night/carry.py`, estimated tokens)

```
seed 1 quiet Daniel carry-in  173 tok,  6 lines; opening 39
seed 1 quiet Elena  carry-in  186 tok,  6 lines; opening 39
seed 1 quiet Leo    carry-in  188 tok,  6 lines; opening 39
seed 1 quiet Mara   carry-in  186 tok,  6 lines; opening 39
seed 1 busy  Daniel carry-in  284 tok,  9 lines; opening 53
seed 1 busy  Elena  carry-in  249 tok,  8 lines; opening 53
seed 1 busy  Leo    carry-in  268 tok,  9 lines; opening 53
seed 1 busy  Mara   carry-in  186 tok,  6 lines; opening 53
seed 2 quiet Daniel carry-in  197 tok,  7 lines; opening 38
seed 2 quiet Elena  carry-in  210 tok,  7 lines; opening 38
seed 2 quiet Leo    carry-in  213 tok,  7 lines; opening 38
seed 2 quiet Mara   carry-in  207 tok,  7 lines; opening 38
seed 2 busy  Daniel carry-in  309 tok, 10 lines; opening 53
seed 2 busy  Elena  carry-in  273 tok,  9 lines; opening 53
seed 2 busy  Leo    carry-in  293 tok, 10 lines; opening 53
seed 2 busy  Mara   carry-in  207 tok,  7 lines; opening 53
seed 3 quiet Daniel carry-in  169 tok,  6 lines; opening 39
seed 3 quiet Elena  carry-in  167 tok,  6 lines; opening 39
seed 3 quiet Leo    carry-in  169 tok,  6 lines; opening 39
seed 3 quiet Mara   carry-in  167 tok,  6 lines; opening 39
seed 3 busy  Daniel carry-in  281 tok,  9 lines; opening 53
seed 3 busy  Elena  carry-in  231 tok,  8 lines; opening 53
seed 3 busy  Leo    carry-in  249 tok,  9 lines; opening 53
seed 3 busy  Mara   carry-in  167 tok,  6 lines; opening 53
```

The draft's seed-2 Leo block, printed by the same script:

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 33, after denying it to you: "I took it in the night, I'm sorry." (you heard it).
- Accusations: Daniel accused you three times (min 03, 09, 12); Mara accused Daniel (min 36).
- Mara ate a portion at minute 54 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said Elena should not go (min 48); you said Elena should not go (min 48); Elena said she will not go (min 51); Daniel said nobody should go (min 51).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You slept through the night.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
```

The draft's "You slept through the night." became §5.2's "You went to sleep.", which does not
claim nothing woke them. Its "You and Mara … (you saw it)" lost the parenthesis in §5.2. Both
are within a token or two.

**4. Day-2 minute-00 prompt sizes** (`$S/night/budget2.py`; "w/o trip" excludes the trip block;
"w/o trip+carry" also excludes the carry-in; `loose` is how many loose backstory events are
kept)

```
seed 1 quiet Daniel loose=all: total 1688, w/o trip 1404, w/o trip+carry 1231  loose=4: total 1575, w/o trip 1291, w/o trip+carry 1118  loose=1: total 1498, w/o trip 1214, w/o trip+carry 1041  loose=0: total 1469, w/o trip 1185, w/o trip+carry 1012
seed 1 quiet Elena  loose=all: total 1721, w/o trip 1411, w/o trip+carry 1226  loose=4: total 1598, w/o trip 1288, w/o trip+carry 1102  loose=1: total 1514, w/o trip 1203, w/o trip+carry 1018  loose=0: total 1484, w/o trip 1174, w/o trip+carry 989
seed 1 quiet Leo    loose=all: total 1669, w/o trip 1379, w/o trip+carry 1191  loose=4: total 1592, w/o trip 1302, w/o trip+carry 1115  loose=1: total 1509, w/o trip 1219, w/o trip+carry 1032  loose=0: total 1480, w/o trip 1190, w/o trip+carry 1002
seed 1 quiet Mara   loose=all: total 1740, w/o trip 1451, w/o trip+carry 1266  loose=4: total 1617, w/o trip 1328, w/o trip+carry 1143  loose=1: total 1533, w/o trip 1244, w/o trip+carry 1058  loose=0: total 1504, w/o trip 1215, w/o trip+carry 1029
seed 1 busy  Daniel loose=all: total 1814, w/o trip 1530, w/o trip+carry 1246  loose=4: total 1701, w/o trip 1417, w/o trip+carry 1133  loose=1: total 1624, w/o trip 1340, w/o trip+carry 1056  loose=0: total 1595, w/o trip 1311, w/o trip+carry 1027
seed 1 busy  Elena  loose=all: total 1799, w/o trip 1489, w/o trip+carry 1240  loose=4: total 1676, w/o trip 1366, w/o trip+carry 1117  loose=1: total 1592, w/o trip 1282, w/o trip+carry 1033  loose=0: total 1563, w/o trip 1252, w/o trip+carry 1004
seed 1 busy  Leo    loose=all: total 1763, w/o trip 1474, w/o trip+carry 1206  loose=4: total 1687, w/o trip 1397, w/o trip+carry 1129  loose=1: total 1604, w/o trip 1314, w/o trip+carry 1046  loose=0: total 1574, w/o trip 1285, w/o trip+carry 1017
seed 1 busy  Mara   loose=all: total 1755, w/o trip 1466, w/o trip+carry 1281  loose=4: total 1632, w/o trip 1343, w/o trip+carry 1157  loose=1: total 1547, w/o trip 1259, w/o trip+carry 1073  loose=0: total 1518, w/o trip 1229, w/o trip+carry 1044
seed 2 quiet Daniel loose=all: total 1786, w/o trip 1491, w/o trip+carry 1294  loose=4: total 1672, w/o trip 1377, w/o trip+carry 1181  loose=1: total 1596, w/o trip 1301, w/o trip+carry 1104  loose=0: total 1567, w/o trip 1272, w/o trip+carry 1075
seed 2 quiet Elena  loose=all: total 1757, w/o trip 1446, w/o trip+carry 1237  loose=4: total 1634, w/o trip 1323, w/o trip+carry 1114  loose=1: total 1549, w/o trip 1239, w/o trip+carry 1029  loose=0: total 1520, w/o trip 1209, w/o trip+carry 1000
seed 2 quiet Leo    loose=all: total 1831, w/o trip 1517, w/o trip+carry 1305  loose=4: total 1754, w/o trip 1441, w/o trip+carry 1228  loose=1: total 1671, w/o trip 1358, w/o trip+carry 1145  loose=0: total 1642, w/o trip 1329, w/o trip+carry 1116
seed 2 quiet Mara   loose=all: total 1801, w/o trip 1489, w/o trip+carry 1282  loose=4: total 1678, w/o trip 1366, w/o trip+carry 1159  loose=1: total 1594, w/o trip 1281, w/o trip+carry 1074  loose=0: total 1564, w/o trip 1252, w/o trip+carry 1045
seed 2 busy  Daniel loose=all: total 1912, w/o trip 1617, w/o trip+carry 1309  loose=4: total 1799, w/o trip 1504, w/o trip+carry 1196  loose=1: total 1722, w/o trip 1427, w/o trip+carry 1119  loose=0: total 1693, w/o trip 1398, w/o trip+carry 1090
seed 2 busy  Elena  loose=all: total 1835, w/o trip 1525, w/o trip+carry 1252  loose=4: total 1712, w/o trip 1402, w/o trip+carry 1129  loose=1: total 1628, w/o trip 1317, w/o trip+carry 1044  loose=0: total 1599, w/o trip 1288, w/o trip+carry 1015
seed 2 busy  Leo    loose=all: total 1926, w/o trip 1612, w/o trip+carry 1320  loose=4: total 1849, w/o trip 1536, w/o trip+carry 1243  loose=1: total 1766, w/o trip 1453, w/o trip+carry 1160  loose=0: total 1737, w/o trip 1424, w/o trip+carry 1131
seed 2 busy  Mara   loose=all: total 1816, w/o trip 1504, w/o trip+carry 1297  loose=4: total 1693, w/o trip 1381, w/o trip+carry 1174  loose=1: total 1609, w/o trip 1296, w/o trip+carry 1089  loose=0: total 1579, w/o trip 1267, w/o trip+carry 1060
seed 3 quiet Daniel loose=all: total 1764, w/o trip 1455, w/o trip+carry 1286  loose=4: total 1651, w/o trip 1342, w/o trip+carry 1173  loose=1: total 1575, w/o trip 1266, w/o trip+carry 1096  loose=0: total 1546, w/o trip 1236, w/o trip+carry 1067
seed 3 quiet Elena  loose=all: total 1739, w/o trip 1445, w/o trip+carry 1279  loose=4: total 1616, w/o trip 1322, w/o trip+carry 1156  loose=1: total 1532, w/o trip 1238, w/o trip+carry 1071  loose=0: total 1503, w/o trip 1209, w/o trip+carry 1042
seed 3 quiet Leo    loose=all: total 1695, w/o trip 1406, w/o trip+carry 1236  loose=4: total 1619, w/o trip 1329, w/o trip+carry 1160  loose=1: total 1536, w/o trip 1246, w/o trip+carry 1077  loose=0: total 1506, w/o trip 1217, w/o trip+carry 1047
seed 3 quiet Mara   loose=all: total 1751, w/o trip 1456, w/o trip+carry 1288  loose=4: total 1627, w/o trip 1332, w/o trip+carry 1165  loose=1: total 1543, w/o trip 1248, w/o trip+carry 1081  loose=0: total 1514, w/o trip 1219, w/o trip+carry 1052
seed 3 busy  Daniel loose=all: total 1891, w/o trip 1581, w/o trip+carry 1301  loose=4: total 1777, w/o trip 1468, w/o trip+carry 1188  loose=1: total 1701, w/o trip 1392, w/o trip+carry 1111  loose=0: total 1672, w/o trip 1362, w/o trip+carry 1082
seed 3 busy  Elena  loose=all: total 1818, w/o trip 1524, w/o trip+carry 1293  loose=4: total 1695, w/o trip 1401, w/o trip+carry 1170  loose=1: total 1610, w/o trip 1316, w/o trip+carry 1086  loose=0: total 1581, w/o trip 1287, w/o trip+carry 1057
seed 3 busy  Leo    loose=all: total 1790, w/o trip 1500, w/o trip+carry 1251  loose=4: total 1713, w/o trip 1424, w/o trip+carry 1174  loose=1: total 1630, w/o trip 1341, w/o trip+carry 1091  loose=0: total 1601, w/o trip 1311, w/o trip+carry 1062
seed 3 busy  Mara   loose=all: total 1765, w/o trip 1470, w/o trip+carry 1303  loose=4: total 1642, w/o trip 1347, w/o trip+carry 1180  loose=1: total 1558, w/o trip 1263, w/o trip+carry 1096  loose=0: total 1529, w/o trip 1234, w/o trip+carry 1066
```

The emulation uses day 1's trip lines (with the minute-90 plan line) as a stand-in for day 2's,
which at minute 00 have no plan line yet. So the trip-block figures are slightly high, and the
budgeted figures are unaffected.

**5. The night's draws** (`$S/night/draws.py`)

```
$ .venv/Scripts/python.exe $S/night/draws.py
wake thresholds, roommate: {'daniel': 0.56, 'elena': 0.6, 'leo': 0.4, 'mara': 0.62}  front door: {'daniel': 0.23, 'elena': 0.25, 'leo': 0.15, 'mara': 0.26}
seed 1: house u=0.050 -> 0 portions; leaving order ['leo', 'daniel', 'elena', 'mara']
  daniel leads: trip u=0.297 alone->clean, pair->clean; lost u=0.909 | leo sleeps (0.573<0.4?) | door elena sleeps (0.314) | door mara WAKES (0.256) | return: elena wakes (0.229), leo sleeps (0.637), mara sleeps (0.526)
  elena  leads: trip u=0.955 alone->not_back, pair->scare_back; lost u=0.814 | mara WAKES (0.251<0.62?) | door daniel sleeps (0.835) | door leo sleeps (0.690) | return: daniel sleeps (0.496), leo sleeps (0.164), mara wakes (0.126)
  leo    leads: trip u=0.008 alone->clean, pair->clean; lost u=0.874 | daniel WAKES (0.051<0.56?) | door elena WAKES (0.008) | door mara sleeps (0.382) | return: daniel sleeps (0.739), elena wakes (0.247), mara wakes (0.207)
  mara   leads: trip u=0.456 alone->clean, pair->clean; lost u=0.279 | elena sleeps (0.997<0.6?) | door daniel sleeps (0.566) | door leo sleeps (0.782) | return: daniel sleeps (0.492), elena sleeps (0.954), leo wakes (0.133)
seed 2: house u=0.105 -> 0 portions; leaving order ['leo', 'elena', 'mara', 'daniel']
  daniel leads: trip u=0.927 alone->scare_back, pair->scare_back; lost u=0.095 | leo sleeps (0.777<0.4?) | door elena WAKES (0.198) | door mara sleeps (0.919) | return: elena wakes (0.244), leo sleeps (0.610), mara wakes (0.006)
  elena  leads: trip u=0.625 alone->scare_there, pair->clean; lost u=0.417 | mara WAKES (0.393<0.62?) | door daniel sleeps (0.760) | door leo sleeps (0.336) | return: daniel sleeps (0.769), leo sleeps (0.238), mara sleeps (0.735)
  leo    leads: trip u=0.064 alone->clean, pair->clean; lost u=0.085 | daniel WAKES (0.185<0.56?) | door elena sleeps (0.451) | door mara sleeps (0.378) | return: daniel sleeps (0.864), elena sleeps (0.664), mara sleeps (0.880)
  mara   leads: trip u=0.101 alone->clean, pair->clean; lost u=0.281 | elena WAKES (0.212<0.6?) | door daniel sleeps (0.668) | door leo sleeps (0.426) | return: daniel sleeps (0.872), elena wakes (0.090), leo sleeps (0.236)
seed 3: house u=0.257 -> 0 portions; leaving order ['leo', 'mara', 'daniel', 'elena']
  daniel leads: trip u=0.616 alone->clean, pair->clean; lost u=0.718 | leo sleeps (0.914<0.4?) | door elena sleeps (0.564) | door mara sleeps (0.597) | return: elena sleeps (0.455), leo sleeps (0.328), mara sleeps (0.800)
  elena  leads: trip u=0.108 alone->clean, pair->clean; lost u=0.349 | mara WAKES (0.280<0.62?) | door daniel WAKES (0.056) | door leo sleeps (0.876) | return: daniel sleeps (0.666), leo sleeps (0.164), mara sleeps (0.699)
  leo    leads: trip u=0.712 alone->scare_there, pair->scare_there; lost u=0.732 | daniel sleeps (0.750<0.56?) | door elena WAKES (0.076) | door mara sleeps (0.335) | return: daniel sleeps (0.305), elena sleeps (0.755), mara sleeps (0.438)
  mara   leads: trip u=0.995 alone->not_back, pair->not_back; lost u=0.062 | elena sleeps (0.772<0.6?) | door daniel WAKES (0.149) | door leo WAKES (0.085) | return: daniel sleeps (0.683), elena sleeps (0.436), leo sleeps (0.389)
alone {'back with food': 0.434, 'back with nothing': 0.186, 'back shaken, with nothing': 0.194, 'back shaken, with food': 0.126, 'not back by morning': 0.06} sum 1.0
two or more {'back with food': 0.49, 'back with nothing': 0.21, 'back shaken, with nothing': 0.165, 'back shaken, with food': 0.105, 'not back by morning': 0.03} sum 1.0
alone MC not_back 5964 /100000; house empty 30075 /100000
pair MC not_back 2985 /100000; house empty 30075 /100000
```

The house draw for seeds 1–12, to choose test seeds:

```
$ .venv/Scripts/python.exe -c "import random; H=[(0.30,0),(0.65,2),(0.90,4),(1.00,6)]; [print(s, round(u,3), next(v for c,v in H if u<c)) for s in range(1,13) for u in [random.Random(f'{s}:night:house').random()]]"
1 0.05 0
2 0.105 0
3 0.257 0
4 0.495 2
5 0.534 2
6 0.982 6
7 0.299 0
8 0.226 0
9 0.097 0
10 0.419 2
11 0.303 2
12 0.94 6
```

**6. The two v11 seed-2 prompts with words against their option** (from
`cache/v11/…seed2.json`, the trip lines and the tail)

```
--- Elena, min 42
About going there tonight: you said Daniel should not go (min 39); Daniel said Mara should not go (min 42); Mara said she will not go (min 42); Leo offered to go (min 42).
…
- propose_trip: (speech) say someone should go to the neighbour's house tonight
- volunteer: (speech) offer to go there tonight yourself
- object_trip: (speech) say nobody should go out tonight
- back_daniel: (speech) say Daniel should be the one to go
- back_leo: (speech) say Leo should be the one to go
- back_mara: (speech) say Mara should be the one to go
- object_leo: (speech) say Leo should not be the one to go
…
{"option": "back_leo", "say": "Leo, you cannot go out there, it is far too dangerous for any of us.", …}
--- Leo, min 45
About going there tonight: Daniel said Mara should not go (min 42); Mara said she will not go (min 42); you offered to go (min 42); Elena said you should go (min 42).
…
- propose_trip: (speech) say someone should go to the neighbour's house tonight
- object_trip: (speech) say nobody should go out tonight
- back_daniel: (speech) say Daniel should be the one to go
- back_elena: (speech) say Elena should be the one to go
- back_mara: (speech) say Mara should be the one to go
- decline: (speech) say you will not be the one to go
…
{"option": "decline", "say": "I already said I would go, Mom, and changing my mind now doesn't make it any safer.", …}
```

**7. The shipped house** (read only, for §3.1)

```
$ grep -n -i "door\|connect\|audible\|front" Assets/_Project/Data/Scenario/morning.json
19:        "name": "front room",
64:    "connections": [
68:        "audible": true
…
93:        "audible": false
```

The rooms are kitchen, front room, hallway, brothers room, back room and bathroom. The bedrooms
and the bathroom connect to the hallway, and only the bathroom's connection is not audible. No
front door is listed.

### Scripts

`$S/night/state.py`:

```python
"""Replays the three v11 mornings from cache/v11 (replay mode: no client, no API) and prints
the state at minute 90 that the night and day 2 would start from."""
import os, sys
sys.path.insert(0, os.getcwd())
import data, world
from gemini import Cache, Oracle
from world import Morning, hunger_level, hunger_words

for seed in (1, 2, 3):
    cache = Cache(f"cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json")
    o = Oracle(cache, "gemini-3.5-flash-lite", seed, client=None, replay=True, max_calls=150)
    m = Morning(o, seed).run()
    print(f"=== seed {seed}: asks {o.from_cache} cached, {o.api_requests} API; portions {m.portions}")
    for p in m.people.values():
        g = {t: x.strength for t, x in p.grudges.items() if x.strength}
        print(f"  {p.name:6} room={p.room:8} hunger={p.hunger:.3f} ({hunger_words(p.hunger)}, lvl {hunger_level(p.hunger)}) "
              f"eaten={p.eaten:g} susp={p.suspicion.state()} knows={p.knows_culprit} conf={p.confessed} "
              f"guilt={p.guilt} grudges={g} pos={p.trip_heard.get(p.id)} feeling={p.feeling!r}")
    print("  plan:", m.plan_text())
    print("  accusations:", [(r['minute'], d['person'], d['option']) for r in m.log for d in r['decisions'] if d['option'].startswith('accuse_')])
    print("  max prompt tokens (est):", m.max_prompt_tokens)
```

`$S/night/draws.py`:

```python
"""The night's chance draws for seeds 1-3, with the exact seed strings and thresholds of
night_design.md §4. Pure arithmetic: no model, no API."""
import random
import sys, os
sys.path.insert(0, os.getcwd())
import data
ORDER = data.ORDER
ROOMMATE = {"daniel": "leo", "leo": "daniel", "elena": "mara", "mara": "elena"}
ANX = {p: data.PEOPLE[p]["traits"]["anxious"] for p in ORDER}
P_ROOM = {p: round(0.30 + 0.40 * ANX[p], 3) for p in ORDER}   # a sleeping roommate wakes
P_DOOR = {p: round(0.10 + 0.20 * ANX[p], 3) for p in ORDER}   # a sleeper in a bedroom wakes at the front door
HOUSE = [(0.30, 0), (0.65, 2), (0.90, 4), (1.00, 6)]
ALONE = [(0.62, "clean"), (0.76, "scare_there"), (0.94, "scare_back"), (1.00, "not_back")]
PAIR = [(0.70, "clean"), (0.82, "scare_there"), (0.97, "scare_back"), (1.00, "not_back")]
pick = lambda table, u: next(v for c, v in table if u < c)
u_ = lambda s: random.Random(s).random()
print("wake thresholds, roommate:", P_ROOM, " front door:", P_DOOR)
for seed in (1, 2, 3):
    rng = random.Random(f"{seed}:night:order")
    order = {q: rng.random() for q in ORDER}
    h = u_(f"{seed}:night:house")
    print(f"seed {seed}: house u={h:.3f} -> {pick(HOUSE, h)} portions; leaving order {sorted(ORDER, key=order.get)}")
    for q in ORDER:
        t = u_(f"{seed}:night:trip:{q}")
        r = ROOMMATE[q]
        w = u_(f"{seed}:night:wake:{q}:{r}")
        door = {o: u_(f"{seed}:night:door:{q}:{o}") for o in ORDER if o not in (q, r)}
        back = {o: u_(f"{seed}:night:return:{q}:{o}") for o in ORDER if o != q}
        print(f"  {q:6} leads: trip u={t:.3f} alone->{pick(ALONE, t)}, pair->{pick(PAIR, t)}; lost u={u_(f'{seed}:night:lost:{q}'):.3f}"
              f" | {r} {'WAKES' if w < P_ROOM[r] else 'sleeps'} ({w:.3f}<{P_ROOM[r]}?)"
              + "".join(f" | door {o} {'WAKES' if v < P_DOOR[o] else 'sleeps'} ({v:.3f})" for o, v in door.items())
              + " | return: " + ", ".join(f"{o} {'wakes' if v < P_DOOR[o] else 'sleeps'} ({v:.3f})" for o, v in back.items()))

def outcome_probs(table, house):
    """P(outcome class) for one group, combining the night draw and the house draw."""
    pn = {}; prev = 0
    for c, v in table:
        pn[v] = c - prev; prev = c
    ph = {}; prev = 0
    for c, v in house:
        ph[v] = c - prev; prev = c
    empty = ph[0]
    return {"back with food": pn["clean"] * (1 - empty), "back with nothing": pn["clean"] * empty,
            "back shaken, with nothing": pn["scare_there"] + pn["scare_back"] * empty,
            "back shaken, with food": pn["scare_back"] * (1 - empty), "not back by morning": pn["not_back"]}
for name, table in (("alone", ALONE), ("two or more", PAIR)):
    pr = outcome_probs(table, HOUSE)
    print(name, {k: round(v, 3) for k, v in pr.items()}, "sum", round(sum(pr.values()), 6))
# a Monte Carlo check over many seeds, as test T7 does
import collections
for name, table in (("alone", ALONE), ("pair", PAIR)):
    c = collections.Counter()
    for s in range(100000):
        hh = pick(HOUSE, u_(f"{s}:night:house")); tt = pick(table, u_(f"{s}:night:trip:daniel"))
        c[("food" if hh else "none", tt)] += 1
    print(name, "MC not_back", c[("food", "not_back")] + c[("none", "not_back")], "/100000; house empty",
          sum(v for k, v in c.items() if k[0] == "none"), "/100000")
```

`$S/night/carry.py` (the draft templates used for measuring; §5.2 is the specification):

```python
"""Draft of the day-2 carry-in block (night_design.md §5) built from the replayed v11 state,
to measure it against the prompt budget. Replay mode only: no client, no API."""
import os, sys
sys.path.insert(0, os.getcwd())
import data
from gemini import Cache, Oracle
from world import Morning, estimate_tokens, SYSTEM, NAMES, hunger_words, minutes_text

TIMES = {1: "", 2: " twice", 3: " three times"}

def heard_positions(m, p):
    t = m.heard_plan(p)
    return t[len("About going there tonight: "):-1] if t else None

def carry(m, p, night):
    out = []
    how = "you did it" if p.id == "elena" else "you saw it"
    out.append(f"Yesterday morning Elena counted the pantry and found one can fewer than she expected ({how}).")
    c = m.culprit
    if p.confessed:
        sure = [x for x in p.sure if "you admitted aloud" in x][0]
        mm = sure[4:6]
        out.append(f"You admitted at minute {mm} that you took the can, in front of "
                   + sure.split("in front of ")[1].rstrip("."))
    elif p.knows_culprit and p.knows_culprit != p.id:
        words = [x for x in p.sure if "admitted taking the can" in x][0].split(": ", 1)[1].split(" (you heard")[0]
        after = (f", after denying it to you" if c in p.denials_heard else "")
        out.append(f"{NAMES[c]} admitted taking the can at minute {p.confession_heard_at:02d}{after}: {words.split(': ',1)[1]} (you heard it).")
    elif p.id == c:
        out.append("Nobody found out that you ate the can, and nobody named you.")
    else:
        out.append("Nobody admitted taking the can, and it was not found.")
    for x in p.sure:
        if "you finished searching" in x:
            out.append(f"You searched the {x.split('searching the ')[1].split(':')[0]} at minute {x[4:6]} and found nothing.")
    acc = {}
    for rec in m.log:
        for d in rec["decisions"]:
            if d["option"].startswith("accuse_") and (d["person"] == p.id or p.id in m.transcript["turns"][rec["minute"] // 3]["acts"][[a["who"] for a in m.transcript["turns"][rec["minute"] // 3]["acts"]].index(d["person"])]["audience"]):
                acc.setdefault((d["person"], d["option"][7:]), []).append(rec["minute"])
    if acc:
        parts = []
        for (a, t), ms in acc.items():
            who = "you" if a == p.id else NAMES[a]
            tgt = "you" if t == p.id else NAMES[t]
            parts.append(f"{who} accused {tgt}{TIMES.get(len(ms), f' {len(ms)} times')} (min {', '.join(f'{x:02d}' for x in ms)})")
        out.append("Accusations: " + "; ".join(parts) + ".")
    ate = {}
    for x in p.sure:
        if "ate one of the portions" in x:
            ate.setdefault(x[4:6], []).append("you" if "you ate" in x else x.split(": ")[1].split(" ate")[0])
    for mm, who in ate.items():
        names = " and ".join(w if w == "you" else w for w in who)
        out.append(f"{names[0].upper() + names[1:]} ate {'a portion each' if len(who) > 1 else 'a portion'} at minute {mm}"
                   + ("." if who == ["you"] else " (you saw it)."))
    pos = heard_positions(m, p)
    if pos:
        out.append(f"About going to the neighbour's house last night, where it was left: {pos}.")
    out.append("The afternoon and evening passed in the house. Nobody ate.")
    out += night.get(p.id, [])
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]

QUIET = {"daniel": ["Last night you slept in the brothers room with Leo. You slept through the night."],
         "leo": ["Last night you slept in the brothers room with Daniel. You slept through the night."],
         "elena": ["Last night you slept in the back room with Mara. You slept through the night."],
         "mara": ["Last night you slept in the back room with Elena. You slept through the night."]}
BUSY = {"daniel": ["Last night you slept in the brothers room with Leo. You went out by the front door to the neighbour's house.",
                   "Leo told you, low: \"Daniel, don't do this, you will get yourself killed out there.\" You went all the same.",
                   "You got inside the neighbour's house and found 4 portions of food. You took 3; 1 is still there. On the way back, something was moving in the street, and you ran the rest of the way.",
                   "You put the 3 portions on the shelf in the kitchen before the others got up."],
        "leo": ["Last night you slept in the brothers room with Daniel. You lay awake and listened.",
                "In the night Daniel got up and left the room toward the kitchen and the front door (you saw it).",
                "You told Daniel, low, not to go: \"Daniel, don't do this, you will get yourself killed out there.\" He went all the same.",
                "Before dawn Daniel came back in by the front door (you heard it)."],
        "elena": ["Last night you slept in the back room with Mara. You sat up in the kitchen by the front door all night.",
                  "In the night Daniel came into the kitchen and went out by the front door (you saw it). You let him go and said nothing.",
                  "Before dawn Daniel came back in by the front door, carrying food (you saw it)."],
        "mara": QUIET["mara"]}
OPEN = {"quiet": "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held {pn}; this morning it holds {pn}. (you saw it)",
        "busy": "min 00: Everyone gets up and comes into the kitchen. Last night the shelf held {pn}; this morning it holds {pk}. So someone brought food into the house in the night. (you saw it)"}
def portions(n):
    return f"{n} portion{'s' if n != 1 else ''}"

for seed in (1, 2, 3):
    o = Oracle(Cache(f"cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"), "gemini-3.5-flash-lite", seed, client=None, replay=True)
    m = Morning(o, seed).run()
    for label, night in (("quiet", QUIET), ("busy", BUSY)):
        for p in m.people.values():
            block = "\n".join(carry(m, p, night))
            opening = OPEN[label].format(pn=portions(m.portions), pk=portions(m.portions + 3))
            print(f"seed {seed} {label:5} {p.name:6} carry-in {estimate_tokens(block):4} tok, {block.count(chr(10)):2} lines; opening {estimate_tokens(opening)}")
            if (seed, label, p.id) in ((1, "busy", "leo"), (2, "quiet", "leo"), (3, "quiet", "mara"), (3, "quiet", "daniel")):
                print(block); print(opening)
```

The busy night is made up (a house of 4, a stop, a scare) only to measure a large block. It is
not seeds 1–3's draws.

`$S/night/budget2.py`:

```python
"""Day-2 minute-00 prompt size, emulated on the replayed v11 state (night_design.md §5.4):
yesterday's memory replaced by the carry-in block and the day-2 opening. Replay only, no API."""
import os, sys
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
from gemini import Cache, Oracle
from world import Morning, estimate_tokens, SYSTEM, TRIP_KINDS
from talk import act_of
import carry  # noqa: prints its own table first; ignored here

for seed in (1, 2, 3):
    m = Morning(Oracle(Cache(f"cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"),
                       "gemini-3.5-flash-lite", seed, client=None, replay=True), seed).run()
    for label, night in (("quiet", carry.QUIET), ("busy", carry.BUSY)):
        for p in m.people.values():
            block_in = carry.carry(m, p, night)
            p2 = p
            saved = (p.memory, p.sure, p.said_lines, p.backstory)
            p.memory, p.said_lines = [], []
            p.sure = [carry.OPEN[label].format(pn=carry.portions(m.portions), pk=carry.portions(m.portions + 3))[len("min 00: "):]]
            opts = m.options_for(p)
            # full backstory, then trim loose to the given count, no morning lines
            rows = []
            for keep_loose in (None, 4, 1, 0):
                loose = [x for x in saved[3] if x not in p.trip_memories]
                p.backstory = [x for x in saved[3] if x in p.trip_memories or x in (loose if keep_loose is None else loose[len(loose)-keep_loose:] if keep_loose else [])]
                old = __import__("world").PROMPT_TOKEN_BUDGET
                __import__("world").PROMPT_TOKEN_BUDGET = 10**6     # no trimming: measure as built
                text = m.prompt_for(p, 0, opts)
                __import__("world").PROMPT_TOKEN_BUDGET = old
                text = text.replace("What you are sure of this morning:", "\n".join(block_in) + "\nWhat you are sure of this morning:")
                tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]
                trip = sum(len(x) + 1 for x in m.trip_lines(p)) + sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in TRIP_KINDS) \
                    + sum(len(f"- {x}") + 1 for x in p.trip_memories) + len(data.HOUSE_THINGS_AFTER_TRIP) - len(data.HOUSE_THINGS)
                cin = sum(len(x) + 1 for x in block_in)
                rows.append((keep_loose, estimate_tokens(SYSTEM + text), estimate_tokens(SYSTEM + text, trip), estimate_tokens(SYSTEM + text, trip + cin)))
            p.memory, p.sure, p.said_lines, p.backstory = saved
            print(f"seed {seed} {label:5} {p.name:6} " + "  ".join(
                f"loose={'all' if k is None else k}: total {a}, w/o trip {b}, w/o trip+carry {c}" for k, a, b, c in rows))
```
