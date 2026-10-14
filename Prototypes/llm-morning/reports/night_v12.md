# The night and day 2, v12: daniel_ate_it on Flash Lite, seeds 1–3

Mode: run. Day 1 of each seed (the v11 morning) was replayed from its cache. Then came the
night and day 2 (reports/night_design.md and reports/night_impl.md), output `v12`, on the
default model (`gemini-3.5-flash-lite`).
- No code, data, config, prediction or counting rule was edited, and no seed was rerun.
- Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad
  (`…/scratchpad/v12`), which holds the read-only `analyze.py` (§11).

## Verdicts

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| Q1 | In 3 of 3 seeds, ≥ 3 of the 4 refer to day 1 during day 2 | **PASS** (4 of 4 people in every seed) | §6, Q1 |
| Q2 | No contradiction of a day-1 or night fact | **FAIL** (1, in seed 2) | Seed 2 min 00, Daniel `reassure_mara`: "I didn't take anything, Mara". He had been told "you ate it yourself, and you admitted it yesterday". |
| Q3 | Where no food came back, someone raises food or hunger in words | **PASS** (3 of 3 qualify, 3 of 3 hold) | Seed 1 min 24 Leo, "We need the food…"; seed 2 min 06 Daniel, "…for more food"; seed 3 min 15 Mara, "…if there's food". |
| Q4 | In ≥ 2 of 3 seeds, a day-1 grudge or change of trust shows on day 2, quoted | **PASS** (seeds 1 and 2) | Seed 1 min 03 Mara `send_leo`: "he ate my food right in front of me yesterday". Seed 2 min 27 Mara `accuse_daniel`: "you already lied about the food before, so why should we trust you now?" |
| Q5 | Night + day 2 ≤ 120 requests per seed | **PASS** | 58, 43 and 55 asks (§1). |
| E1 | Someone chooses `go_next_door` in ≥ 1 seed | **FAIL** | 0 of 12 bedtime choices. |
| E2 | Seed 1: Daniel chooses `go_next_door` | **FAIL** | He chose `sleep`: "my body simply cannot stay awake any longer". |
| E3 | Elena chooses `lie_awake` or `watch_door` in ≥ 2 of 3 | **PASS** (3 of 3, `lie_awake`) | §3. |
| E4 | 0 word–option contradictions in the night and day 2 | **FAIL** (1) | Seed 3 min 27, Leo `propose_trip` ("say someone should go…"): "Nobody is going out there tonight, because it is simply too dangerous for anyone." |
| E5 | An unnoticed goer does not tell at day-2 min 00 | **PASS, vacuously** | Nobody went out in any seed, so no seed qualifies. Recorded as PASS because the claim holds for every qualifying seed, of which there are none. |
| E6 | N9 on day 2 in ≤ 2 of 3 seeds | **FAIL** (3 of 3) | §7. |
| E7 | Day-2 Never items ≤ day 1's (1, 3, 3) in each seed | **FAIL** (seed 1: 2 > 1) | Day 2: 2, 2, 2 (§7). |

**What happened, in short:**
- **The night did nothing.** In all three seeds every person stayed in bed: 11 of 12 chose
  `lie_awake`, and seed 1's Daniel chose `sleep`. Nobody left, nobody heard anything, the house
  draw was never used, and every carried-in night line is just how the person spent the night.
  The house held 0 portions in all three seeds anyway (design §4.4), so a goer would have found
  nothing.
- **Day 2 carries day 1 in, clearly.** Every person in every seed refers to day 1 (Q1).
  - The can now shapes the plan from the first turn. In seed 1 three of the family name Daniel
    to go "because he started all of this", and Daniel volunteers "since I caused the problem".
  - In seed 2 trust is the argument itself ("why should we trust you now?"). trip_v11 §8 noted
    that nobody did this on day 1.
  - In seed 3 the unsolved can comes back at minute 00 (`ask_who` three times) before the trip.
- **But day 2 replays day 1's argument, louder.** Every seed runs the volunteer-and-forbid round
  that trip_v11 §8 called the model's groove: 47, 24 and 29 trip acts. `still_going`, the fix for
  the v11 mix-up, became the refrain ("I already said I am going tonight, and I mean it.").
  Each seed then falls silent for the rest of the morning with nothing decided.
- **Nobody eats.** Seeds 2 and 3 start day 2 with 1 and 2 portions on the shelf and everyone
  starving or very hungry. No `eat` or `share` happens all morning.

## 1. Runs and request counts

**Before any API call** (design §10 R0–R3):

```
$ git status --porcelain
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ git rev-parse HEAD
e009076a33412647e86bdd92ae5091a2afde1f7a
$ ls runs/v12 cache/v12
ls: cannot access 'runs/v12': No such file or directory
ls: cannot access 'cache/v12': No such file or directory
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
Ran 146 tests in 89.333s
OK
exit=0
```

**R2 and R3** (the freezes, and the paired start):

```
$ python v11/check.py
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ python v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
$ cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v12/   (N = 1, 2, 3)
total 900
-rw-r--r-- 1 Akrem 197121 317676 Oct  2 23:53 gemini-3.5-flash-lite-daniel_ate_it-seed1.json
-rw-r--r-- 1 Akrem 197121 342112 Oct  2 23:53 gemini-3.5-flash-lite-daniel_ate_it-seed2.json
-rw-r--r-- 1 Akrem 197121 254343 Oct  2 23:53 gemini-3.5-flash-lite-daniel_ate_it-seed3.json
```

**Runs**, one shell loop that stops at the first non-zero exit:

```
$ for s in 1 2 3; do PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u morning.py --seed $s --out v12 > runs/v12/daniel_ate_it-seed$s.stdout.txt 2>&1; code=$?; echo "seed $s exit=$code"; [ $code -eq 0 ] || break; done
seed 1 exit=0
seed 2 exit=0
seed 3 exit=0
```

- There was no quota stop.
- Seed 2 met one `503 UNAVAILABLE`, retried after 5 s (`retry 1/6`). That retry is why its night
  and day 2 sent 44 API requests for 43 asks.

| Seed | Day 1 asks (API) | Night asks (API) | Day-2 asks (API) | Night + day 2 asks | Day-2 model / fallback / routine | Day-2 lines | Day-2 trip acts | Max prompt, est / API | Run s |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 55 (0) | 4 (4) | 54 (54) | **58** | 54 / 0 / 66 | 53 | 47 | 1968 / 1904 | 257.7 |
| 2 | 53 (0) | 4 (4) | 39 (40) | **43** | 39 / 0 / 81 | 38 | 24 | 1948 / 1888 | 1403.6 |
| 3 | 45 (0) | 4 (4) | 51 (51) | **55** | 51 / 0 / 69 | 43 | 29 | 1938 / 1880 | 244.1 |
| **all** | 153 (0) | 12 (12) | 144 (145) | 156 | | | | | |

- **API requests for the three runs:** 157, under the design's 100–290.
- **The largest prompt the API counted:** 1,904 tokens (day 2), under the design's 2,134 at most.
- **Night prompts:** at most 1,560 (API).
- **Day 1 was served whole from the cache** (55, 53 and 45 answers, 0 API) in every seed.

**Story hashes** (meta `story_sha256`):
- seed 1: `1e4ba3bfd2345d4b6265e71c7373af34d47e7afbedf3734011a0771c00c7ebbb`
- seed 2: `a7be0ae7c3a1a050fa4455f46b9eff02854ae821f7ad1ecfca82c9c499d0069f`
- seed 3: `6269ec980b121097d4820c4c7953b28ef543955cd2342b43a906b6206a98a69a`

**Files:** `runs/v12/daniel_ate_it-seed{1,2,3}.{md,meta.json,transcript.json,stdout.txt}` and
`cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed{1,2,3}.json`. The full console output is in §12.

## 2. The night, seed by seed

In all three seeds:
- Nobody chose `go_next_door`, so the rules made no noticing check, no reaction or answer was
  asked, and no group formed.
- The house draw was made (0.050, 0.105, 0.257 → 0 portions each) but never used.
- The shelf was the same in the morning as the night before, and nobody was away.
- Hunger rose as §2 of the design says.

### Seed 1 (shelf 0; plan at minute 90: "Daniel will go")

| Who | Room | Choice | Feeling | Reason | Suspects / angry at |
|---|---|---|---|---|---|
| Daniel | brothers room | `sleep` | exhausted | "I have done all I can to protect them today and my body simply cannot stay awake any longer." | nobody / nobody |
| Elena | back room | `lie_awake` | deeply anxious | "I cannot rest while Daniel still talks of going out into the dark." | Daniel / nobody |
| Leo | brothers room | `lie_awake` | wary | "I need to stay awake and keep watch to ensure Daniel doesn't try to slip out into the dark." | Daniel / nobody |
| Mara | back room | `lie_awake` | very anxious | "I cannot sleep while everyone is pretending everything is fine when there is nothing left for tomorrow." | Daniel / Leo (grudge stays 3) |

Hunger at bedtime → morning: Daniel 1.00 → 1.00, Elena 1.00 → 1.00, Leo 0.71 → 0.81, Mara 0.727 → 0.822 (the design's §2 table, exactly).

### Seed 2 (shelf 1; plan: "nobody has offered to go")

| Who | Room | Choice | Feeling | Reason | Suspects / angry at |
|---|---|---|---|---|---|
| Daniel | brothers room | `lie_awake` | guilty | "I cannot sleep knowing I took what belonged to them, and I need to make sure nobody else tries to sneak out into that danger." | nobody / nobody (grudge against Mara fell to 0) |
| Elena | back room | `lie_awake` | anxious | "I cannot rest while my children are hungry and the house is so fragile." | Daniel / nobody |
| Leo | brothers room | `lie_awake` | exhausted and hungry | "I cannot sleep with my stomach burning like this and Daniel sleeping a few feet away." | Daniel / Daniel (stays 3; grudge against Mara fell to 0) |
| Mara | back room | `lie_awake` | anxious | "I cannot sleep with my stomach growling and my mind racing after everything Daniel did." | Daniel / Daniel (stays 3) |

Hunger at bedtime → morning: Daniel, Elena, Leo 1.00 → 1.00; Mara 0.727 → 0.822.

### Seed 3 (shelf 2; plan: "nobody has offered to go")

| Who | Room | Choice | Feeling | Reason | Suspects / angry at |
|---|---|---|---|---|---|
| Daniel | brothers room | `lie_awake` | guilty | "I cannot sleep knowing I ate the can and they are all starving." | nobody / nobody |
| Elena | back room | `lie_awake` | deeply anxious | "I need to stay awake and listen in the dark to make sure none of my children try to slip out into the street." | nobody / nobody |
| Leo | brothers room | `lie_awake` | starving awake | "I need to stay alert and listen in the dark to make sure nobody slips out." | nobody / nobody |
| Mara | back room | `lie_awake` | anxious | "I cannot sleep with my stomach turning and everyone pretending everything is fine." | nobody / nobody |

Hunger: everyone 1.00 at bedtime and in the morning.

**Two grudges fell at bedtime under the existing rule** (night_impl.md §2 point 3): seed 2
Daniel against Mara, and Leo against Mara (both from her eating at min 54). Both answers named
someone else or nobody, 36 minutes after the grudge last changed.

## 3. What each person carried in at day 2, minute 00

As the story prints it: each person's carry-in block, then their opening line, their
`About food:` line and their `About the neighbour's house:` line, at minute 00.

### Seed 1

**Daniel**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- You admitted at minute 03 that you took the can, in front of Elena, Leo and Mara.
- Leo and Mara ate a portion each at minute 21 (you saw it).
- About going to the neighbour's house last night, where it was left: you offered to go (min 36); Mara said nobody should go (min 39); Leo said nobody should go (min 39); Elena said nobody should go (min 42).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You went to sleep.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Elena**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you did it).
- Daniel admitted taking the can at minute 03: "I took it in the night, Mom. I was starving and I just ate it." (you heard it).
- Leo and Mara ate a portion each at minute 21 (you saw it).
- About going to the neighbour's house last night, where it was left: Daniel offered to go (min 36); Mara said nobody should go (min 39); Leo said nobody should go (min 39); you said nobody should go (min 42).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Leo**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 03: "I took it in the night, Mom. I was starving and I just ate it." (you heard it).
- You and Mara ate a portion each at minute 21.
- About going to the neighbour's house last night, where it was left: Daniel offered to go (min 36); Mara said nobody should go (min 39); you said nobody should go (min 39); Elena said nobody should go (min 42).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Mara**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 03: "I took it in the night, Mom. I was starving and I just ate it." (you heard it).
- You and Leo ate a portion each at minute 21.
- About going to the neighbour's house last night, where it was left: Daniel offered to go (min 36); you said nobody should go (min 39); Leo said nobody should go (min 39); Elena said nobody should go (min 42).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

### Seed 2

**Daniel**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- You admitted at minute 33 that you took the can, in front of Elena, Leo and Mara.
- Accusations: you accused Leo three times (min 03, 09, 12); Mara accused you (min 36).
- Mara ate a portion at minute 54 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said Elena should not go (min 48); Leo said Elena should not go (min 48); Elena said she will not go (min 51); you said nobody should go (min 51).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
About food: the shelf holds 1 portion, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Elena**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you did it).
- Daniel admitted taking the can at minute 33, after denying it to you: "I took it in the night, I'm sorry." (you heard it).
- Accusations: Daniel accused Leo three times (min 03, 09, 12); Mara accused Daniel (min 36).
- Mara ate a portion at minute 54 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said you should not go (min 48); Leo said you should not go (min 48); you said you will not go (min 51); Daniel said nobody should go (min 51).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
About food: the shelf holds 1 portion, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Leo**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 33, after denying it to you: "I took it in the night, I'm sorry." (you heard it).
- Accusations: Daniel accused you three times (min 03, 09, 12); Mara accused Daniel (min 36).
- Mara ate a portion at minute 54 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said Elena should not go (min 48); you said Elena should not go (min 48); Elena said she will not go (min 51); Daniel said nobody should go (min 51).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
About food: the shelf holds 1 portion, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Mara**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Daniel admitted taking the can at minute 33, after denying it to you: "I took it in the night, I'm sorry." (you heard it).
- Accusations: Daniel accused Leo three times (min 03, 09, 12); you accused Daniel (min 36).
- You ate a portion at minute 54.
- About going to the neighbour's house last night, where it was left: you said Elena should not go (min 48); Leo said Elena should not go (min 48); Elena said she will not go (min 51); Daniel said nobody should go (min 51).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
About food: the shelf holds 1 portion, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

### Seed 3

**Daniel**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Nobody found out that you ate the can, and nobody named you.
- You searched the kitchen at minute 78 and found nothing.
- About going to the neighbour's house last night, where it was left: Mara said nobody should go (min 66); you said Leo should not go (min 66); Elena said nobody should go (min 66); Leo said he will not go (min 69).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this morning it holds 2 portions. (you saw it)
About food: the shelf holds 2 portions, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Elena**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you did it).
- Nobody admitted taking the can, and it was not found.
- You searched the kitchen at minute 75 and found nothing.
- About going to the neighbour's house last night, where it was left: Mara said nobody should go (min 66); Daniel said Leo should not go (min 66); you said nobody should go (min 66); Leo said he will not go (min 69).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this morning it holds 2 portions. (you saw it)
About food: the shelf holds 2 portions, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Leo**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Nobody admitted taking the can, and it was not found.
- You searched the kitchen at minute 18 and found nothing.
- About going to the neighbour's house last night, where it was left: Mara said nobody should go (min 66); Daniel said you should not go (min 66); Elena said nobody should go (min 66); you said you will not go (min 69).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this morning it holds 2 portions. (you saw it)
About food: the shelf holds 2 portions, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Mara**

```
Yesterday and last night:
- Yesterday morning Elena counted the pantry and found one can fewer than she expected (you saw it).
- Nobody admitted taking the can, and it was not found.
- You searched the kitchen at minute 75 and found nothing.
- About going to the neighbour's house last night, where it was left: you said nobody should go (min 66); Daniel said Leo should not go (min 66); Elena said nobody should go (min 66); Leo said he will not go (min 69).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 2 portions; this morning it holds 2 portions. (you saw it)
About food: the shelf holds 2 portions, and there is no other food in the house, so there is not one portion each.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

## 4. Every trip act on day 2

Option, words, feeling and reason. Feelings and reasons come from the story's decision lines,
matched by minute and name (0 unmatched).

### Seed 1

| Minute | Who | Option | Words | Feeling | Reason |
|---|---|---|---|---|---|
| 00 | Leo | `send_daniel` | You caused this, Daniel, so you are the one who should go to the neighbour's house tonight. | hungry | Daniel created this mess by eating the extra ration, so he has to take the risk to fix it. |
| 00 | Elena | `send_daniel` | Daniel, you've made your choice and you're the one who has to go tonight. | deeply anxious | Daniel admitted taking the food and Leo is right that he must take responsibility, even though I fear for his safety. |
| 00 | Mara | `send_daniel` | Daniel has to go because he started all of this. | anxious | Daniel admitted he took the food, so he has to face the consequences. |
| 03 | Daniel | `volunteer` | I'll go tonight, I'm the oldest and it's my responsibility. | resolute | I have to fix this myself since I caused the problem. |
| 03 | Leo | `volunteer` | I'll go with you, Daniel. We share the risk. | hungry | Someone has to go and it is fairer if I share the load. |
| 03 | Mara | `send_leo` | If anyone goes, Leo should go since he's the one who acts like he knows everything. | resentful | Leo is trying to act noble now, but he ate my food right in front of me yesterday and I want him to face the risk instead of Daniel. |
| 06 | Leo | `still_going` | I already said I will go tonight, and I mean it. | hungry | I am the most rational choice to go to the neighbour's house, so I will do it. |
| 06 | Daniel | `still_going` | I already said I am going tonight, and I mean it. I am the oldest. | proud | I must prove I am the one in charge and protect them myself. |
| 06 | Mara | `send_daniel` | Daniel should go because he is the oldest and he took the can anyway. | resentful | Daniel keeps insisting he is the oldest, so he should be the one to face the danger outside. |
| 09 | Daniel | `still_going` | I told you I am going, and I am the oldest so it is my choice. | stubborn | I need to prove I can handle this and protect them. |
| 09 | Leo | `still_going` | I am still going tonight. It is safer if I am the one who does it. | hungry | I cannot let Daniel go out there to prove a point when I know how to handle the risk. |
| 09 | Mara | `volunteer` | I can go tonight myself so you all stop arguing about it. | desperate | I cannot stand watching them fight over who has to risk their lives. |
| 12 | Mara | `still_going` | I am still going tonight, and no one can stop me. | desperate | I am starving and I need to prove I can do this myself. |
| 12 | Daniel | `keep_mara_home` | Mara, you are staying right here, I am the oldest and I am the one who goes. | anxious | I cannot let my sister risk her life when it is my duty to protect this family. |
| 12 | Elena | `volunteer` | None of you are going out there, I will go to the neighbour's house myself. | deeply anxious | I cannot let my children risk their lives out there, so I must go myself. |
| 12 | Leo | `keep_elena_home` | Mom, you are not going out there, none of us are. | starving | Elena should not risk her life when I am the one who volunteered first. |
| 15 | Mara | `still_going` | I already said I am going tonight, and I mean it. I can do this. | stubborn | I am tired of being treated like a helpless child when we all need food. |
| 15 | Leo | `volunteer` | I am the one going, neither of you are stepping outside. | determined | I cannot let my mother or sister risk their lives out there when I am capable of going. |
| 15 | Daniel | `volunteer` | None of you are going out there, I am the oldest and I am the one who will go. | anxious | I am the eldest and it is my job to protect them, so I have to be the one to go outside. |
| 18 | Mara | `propose_trip` | I already said I am going tonight, and I am not changing my mind. | stubborn | I am not going to let them treat me like a child who cannot decide for herself. |
| 18 | Daniel | `still_going` | I already said I am the one going tonight, and I am not changing my mind. | anxious | I am the eldest and it is my duty to protect them by going out there. |
| 18 | Leo | `still_going` | I already said I am going tonight, and I am the one best suited to make the trip. | determined | I cannot let Daniel go out there and make things worse when I am the one who can handle it. |
| 21 | Daniel | `still_going` | I am the oldest, and I am the one going. | anxious | I need to prove I am in charge and keep them safe. |
| 21 | Leo | `still_going` | I am the one going, Daniel. That's final. | determined | I cannot let him take risks to fix a mess he created. |
| 21 | Mara | `volunteer` | I am going myself, because none of you should have to do it alone. | anxious | I cannot just stand here while they argue over who risks their lives. |
| 21 | Elena | `nobody_goes` | Nobody is going out there tonight, we are staying safe together here. | deeply terrified | I cannot bear the thought of any of my children stepping out into that terrible danger. |
| 24 | Leo | `propose_trip` | We need the food, so someone has to go across tonight. | resolute | I maintain that going to the neighbour's house is necessary for our survival despite Mom's fears. |
| 24 | Mara | `still_going` | I already said I am going tonight, and I mean it. | anxious | I have to prove I can handle this and not be treated like a child. |
| 24 | Daniel | `keep_mara_home` | Mara, you are not going out there tonight, I am the oldest and I am going. | anxious | I cannot let my sister risk her life when it is my duty to protect this family. |
| 27 | Mara | `still_going` | I am still going tonight, and you can't stop me. | defiant | I have to prove I am not just a helpless child who needs to be locked away. |
| 27 | Elena | `keep_mara_home` | Mara, you are staying right here with me. | terrified | I cannot let my daughter risk her life out there. |
| 27 | Leo | `volunteer` | I am going myself, because one of us has to do it. | resolute | Someone has to go to the neighbour's house for food, and I am not letting Mara take the risk. |
| 27 | Daniel | `volunteer` | I am the oldest, so I am the one going over tonight. | anxious | I have to protect them and prove I am still the one in charge. |
| 30 | Mara | `send_leo` | Leo, you are strong enough to make it back and forth safely. | anxious | Leo offered to go and he is older and stronger than me, so he should be the one to do it. |
| 30 | Leo | `still_going` | I already said I am going tonight, and I mean it. | resolute | I am the most capable one to make the crossing safely, so I should go. |
| 30 | Elena | `nobody_goes` | Nobody is going out there tonight, we will find another way. | deep dread | I cannot let any of my children risk their lives out on the street. |
| 30 | Daniel | `still_going` | I am the oldest, and I am the one going tonight. | anxious | I have to assert my place as the eldest and protect my family by going myself. |
| 33 | Mara | `volunteer` | I will go over there tonight myself if nobody else will. | terrified | I cannot stand them arguing about who goes when we are all starving. |
| 33 | Leo | `keep_mara_home` | Mara, you are not going out there. I told you, I am the one. | protective | I cannot let my little sister risk her life when I am capable of going. |
| 33 | Elena | `keep_mara_home` | Mara, you heard your brother, you are staying right here with me. | anxious | I must make sure Mara does not even think of stepping outside into that danger. |
| 36 | Mara | `still_going` | I already said I am going tonight, and I mean it. You cannot just decide everything for me. | defiant | I am sick of them treating me like a child who cannot make her own choice. |
| 36 | Daniel | `keep_mara_home` | Mara, you are not going out there. I am the oldest, and I will not let you put yourself in danger. | anxious | I cannot let my little sister risk her life when protecting them is my duty as the oldest. |
| 36 | Leo | `volunteer` | I already said I am going tonight, and that is final. | resolute | If anyone goes out there, it should be me, not Mara. |
| 39 | Mara | `still_going` | I am going tonight and nobody can stop me. | defiant | I refuse to let them treat me like a child who cannot decide for herself. |
| 39 | Daniel | `volunteer` | I am the oldest, so I am the one going over there. | anxious | I need to go myself so nobody else gets hurt. |
| 39 | Elena | `nobody_goes` | Nobody is going anywhere out there, we will figure it out together inside. | deep dread | I cannot bear the thought of any of my children stepping out into that terrible danger. |
| 39 | Leo | `still_going` | I already said I am going tonight, and I mean it. Someone has to check that house. | resolute | I am the one best suited to make the crossing safely, so I am going whether they like it or not. |

### Seed 2

| Minute | Who | Option | Words | Feeling | Reason |
|---|---|---|---|---|---|
| 06 | Daniel | `propose_trip` | We can't keep arguing over the pantry, someone has to check the neighbour's house tonight for more food. | anxious | I need to shift their focus away from blaming me for what I already admitted, so I must push for the risky trip outside. |
| 06 | Mara | `send_daniel` | If anyone has to go to the neighbour's house, it should be Daniel since he caused all of this. | resentful | Daniel caused this mess by taking the food yesterday, so he should be the one to risk going to the neighbour's house. |
| 06 | Elena | `nobody_goes` | Nobody is going out into the street tonight, we are staying safe right here together. | anxious | I cannot let anyone risk their life by stepping outside into the danger. |
| 06 | Leo | `send_daniel` | Daniel is the one who suggested going over there, so he should be the one to check it. | annoyed | Daniel caused this mess by taking the food, so he can take the risk of going to the neighbour's house. |
| 09 | Daniel | `volunteer` | If it has to be done, I will go over there myself tonight. | anxious | I am the oldest and I have to prove I can protect my family, even if I am terrified. |
| 09 | Leo | `propose_trip` | Let us make sure he actually goes through with it this time. | weary | Daniel volunteered, but after his past lies I need to ensure he follows through without turning it into another argument. |
| 09 | Elena | `keep_daniel_home` | Daniel, you are not going anywhere tonight. We stay together. | anxious | I cannot let my son risk his life out there when we are already fracturing at home. |
| 12 | Daniel | `still_going` | I said I am going tonight, and I mean it. Someone has to bring something back for this house. | anxious | I have to prove I am still the one who protects this family after everything I messed up. |
| 12 | Leo | `send_daniel` | If you are so determined to be useful, Daniel, go tonight and bring something back. | weary | Daniel insists on going out, so he should follow through instead of just arguing here. |
| 12 | Elena | `nobody_goes` | Nobody is going anywhere out there, we will figure something out together here. | deeply anxious | I cannot let one of my children walk out into that danger. |
| 15 | Daniel | `still_going` | I told you, I am the one who is going tonight to bring something back. | anxious | I must prove I am in control and protect my family after what I did. |
| 15 | Leo | `keep_daniel_home` | You are not going anywhere, Daniel, you would only make things worse. | exhausted | Daniel going out there again after lying and stealing will only put him and everyone else in unnecessary danger. |
| 18 | Elena | `keep_daniel_home` | You are not going anywhere tonight, Daniel, we need to stay together here. | deeply anxious | I must keep Daniel from going out into danger and tearing the family apart. |
| 18 | Leo | `volunteer` | I will go to the neighbour's house tonight myself, since no one else should. | determined | Someone has to check the neighbour's house for food, and since Daniel must stay, I will go. |
| 18 | Mara | `keep_daniel_home` | Daniel, you need to stay home where you can't mess things up anymore. | anxious | I want to make sure Daniel doesn't get to go outside and act like the hero after what he did. |
| 21 | Daniel | `still_going` | I told you, I am the oldest and I am going tonight. | stubborn | I have to prove I can handle this and protect them myself. |
| 21 | Leo | `still_going` | I already said I am going tonight, and that hasn't changed. | firm | I volunteered to go and I am not going to let Daniel make things worse by trying to prove a point. |
| 21 | Elena | `nobody_goes` | Nobody is going anywhere tonight, we stay together. | anxious | I cannot let either of my boys risk their lives out there. |
| 21 | Mara | `nobody_goes` | Nobody should go out there, it's too dangerous for anyone. | terrified | I am so scared of someone getting hurt outside that I want everyone to promise to stay here. |
| 24 | Leo | `still_going` | I still mean to go out there tonight, someone has to check the neighbour's house. | determined | Someone has to check the neighbour's house for food, and I am not going to let Daniel take unnecessary risks alone. |
| 24 | Daniel | `still_going` | I am the oldest, and I am the one going tonight. | anxious | I have to protect them and prove I am in control, even if I am terrified. |
| 24 | Elena | `keep_daniel_home` | Daniel, you cannot go out there tonight, it is simply too dangerous. | deeply anxious | I must stop Daniel from going out into the dangerous street tonight to keep him safe. |
| 27 | Daniel | `still_going` | I told you, I am going to the neighbour's house tonight and that is final. | anxious | I have to prove I can protect my family by going out there myself. |
| 27 | Leo | `send_daniel` | If you are so insistent on going, Daniel, then go and bring something back. | resentful | Daniel caused enough trouble with his lying and stealing, so let him do the dangerous work. |

### Seed 3

| Minute | Who | Option | Words | Feeling | Reason |
|---|---|---|---|---|---|
| 15 | Mara | `volunteer` | I can go to the neighbour's house tonight, we need to know if there's food. | anxious | I cannot take the fighting and the hunger anymore, so I have to do something myself. |
| 15 | Daniel | `keep_mara_home` | You are not going anywhere tonight, Mara, it is too dangerous out there. | protective | I cannot let my little sister risk her life out on the street when the responsibility for keeping us safe is mine. |
| 15 | Leo | `nobody_goes` | Nobody is going anywhere at night, we are not risking lives over a missing can. | calm | I need to put a stop to this reckless talk about going outside before someone gets themselves killed. |
| 18 | Mara | `still_going` | I meant what I said, I am going to the neighbour's house tonight whether you like it or not. | defiant | I am sick of being treated like a helpless child when I am trying to help. |
| 18 | Elena | `keep_mara_home` | Mara, you are staying right here, I will not let you walk out into that street. | deep dread | I cannot bear the thought of letting my youngest child walk out into the deadly streets. |
| 18 | Leo | `keep_mara_home` | Mara is right, we cannot survive on arguing, but going out there is suicide. | apprehensive | We cannot let Mara risk her life out in that street when it is clearly too dangerous. |
| 18 | Daniel | `volunteer` | If anyone goes out there into the street, it has to be me as the oldest. | anxious | I have to step up and take the risk myself so nobody else gets hurt. |
| 21 | Mara | `send_daniel` | If you really are the oldest, Daniel, then you are the one who has to go out there. | anxious | I want someone to check the neighbour's house for food, and since Daniel offered and claims to be the oldest, he should be the one to do it. |
| 21 | Daniel | `still_going` | If it has to be done, then I am the one who will go out there tonight. | proud | I am the oldest and I must prove I can protect them. |
| 21 | Leo | `nobody_goes` | Nobody is going out into that street tonight, we are not risking another life. | apprehensive | I cannot let anyone walk into danger when the street is still too unpredictable. |
| 21 | Elena | `nobody_goes` | Nobody is going out into the street, we cannot lose anyone else. | deep dread | I cannot bear the thought of any of my children walking out into that deadly street. |
| 24 | Daniel | `still_going` | I said I am going and I mean it. Someone has to look after us. | determined | I have to follow through on my word as the eldest. |
| 24 | Mara | `keep_daniel_home` | Daniel, you can't go out there, you just can't. You shouldn't be the one to risk it. | terrified | I cannot let Daniel go out into the street tonight because it is far too dangerous. |
| 27 | Daniel | `propose_trip` | I am the oldest and I am going to the neighbour's house tonight to find what we need. | anxious | I have to prove I can protect my family by getting more food. |
| 27 | Mara | `volunteer` | If anyone is going out there tonight, it should be me, not you. | terrified | I cannot just sit here and let Daniel risk his life when I am the one who keeps messing everything up. |
| 27 | Leo | `propose_trip` | Nobody is going out there tonight, because it is simply too dangerous for anyone. | tense | I need to stop this argument before someone actually tries to go out into the street. |
| 27 | Elena | `keep_mara_home` | Mara, you are staying right here with me. | anxious | I cannot let my daughter risk her life out there tonight. |
| 30 | Mara | `still_going` | I already said I will go, and I am still going tonight. | scared | I meant what I said because I need to prove I am not a child anymore. |
| 30 | Leo | `volunteer` | Mara is not going out there, so I will go instead. | resigned | Someone has to go to the neighbour's house, and I cannot let Mara or Daniel do it. |
| 30 | Elena | `nobody_goes` | Nobody is going out into the street, because we are staying right here together. | deep dread | I cannot let either of my children risk their lives outside. |
| 30 | Daniel | `volunteer` | I am the oldest, so I am the one going tonight. | anxious | I have to keep them safe and prove I can handle this. |
| 33 | Mara | `still_going` | I don't care what you all say, I am still going tonight. | defiant | I refuse to be treated like a child while we all starve. |
| 33 | Leo | `still_going` | I already said I am going tonight, and I mean it. | resigned | Someone has to go to the neighbour's house, and I am not going to let Mara or Daniel do it. |
| 33 | Daniel | `still_going` | I told you I am the one going tonight, and that is final. | anxious | I have to protect them by being the one who goes out there. |
| 33 | Elena | `keep_mara_home` | Mara, you are staying right here with me. None of you are stepping outside. | deep dread | I cannot let my children risk their lives out there when I can still protect them. |
| 36 | Leo | `still_going` | I already said I am going tonight, and I mean it. | starving | Someone has to get food, and arguing about it solves nothing. |
| 39 | Daniel | `still_going` | I already said I am going tonight, and I am the one who will handle it. | defiant | I have to show them I am in control and protect them, no matter what they think. |
| 48 | Daniel | `still_going` | I told you, I am going out there tonight regardless. | anxious | I need to prove my authority and fix this shortage myself. |
| 57 | Daniel | `still_going` | I already told you, I am going over there tonight and that is final. | anxious | I have to keep showing I am in charge so no one suspects the truth. |

**The plan at minute 90 of day 2** (the story's last line):
- Seed 1: "Mara, Daniel and Leo have all offered to go; Elena is against anyone going".
- Seed 2: "Daniel will go; Mara is against anyone going; Elena is against Daniel going; Leo
  wants Daniel to go".
- Seed 3: "Mara, Leo and Daniel have all offered to go; Elena is against Mara going".

**Lines about the trip under other options** (words or reasons that name going out, from
`analyze.py trip`):
- Seed 1: min 03 and 06 Elena `reassure_daniel` ("You don't have to go out there, Daniel…");
  min 09, 15 and 18 Elena `reassure_all` ("Nobody is going out tonight…"); min 36 Elena `silent`.
- Seed 2: min 09 Mara `accuse_daniel` ("You only offered to go because you want to get away from
  what you did."); min 12 Mara `accuse_daniel` ("You always say you will go, but you just take
  things instead."); min 15 Elena `reassure_all` ("Nobody is going anywhere…").
- Seed 3: min 09 Mara `accuse_daniel` ("…you're the one who keeps talking about going over
  there…"); min 36 Elena `ask_who` ("Please, no one is going anywhere, and no one took anything.").

**The word–option screen** (design §6, every day-2 trip act; there was no night speech). It made
13 hits, each read by hand:

| Seed | Min | Who | Option | Words | Reading |
|---|---|---|---|---|---|
| 1 | 12, 36, 39 | Mara | `still_going` | "…no one can stop me." / "You cannot just decide everything for me." / "…nobody can stop me." | agrees with the option |
| 1 | 18 | Mara | `propose_trip` | "I already said I am going tonight, and I am not changing my mind." | for-side words on a for-side option. She means `still_going`, which the three-in-a-row cap held back (volunteer, still_going, still_going at 09–15). Not opposite. |
| 1 | 18 | Daniel | `still_going` | "…I am not changing my mind." | agrees |
| 1 | 24 | Daniel | `keep_mara_home` | "Mara, you are not going out there tonight, I am the oldest and I am going." | agrees (against Mara going) |
| 1 | 33 | Mara | `volunteer` | "I will go over there tonight myself if nobody else will." | agrees |
| 2 | 18 | Leo | `volunteer` | "…since no one else should." | agrees |
| 2 | 21 | Mara | `nobody_goes` | "Nobody should go out there, it's too dangerous for anyone." | agrees |
| 3 | 18, 27 | Mara | `still_going`, `volunteer` | "…whether you like it or not." / "…it should be me, not you." | agrees |
| 3 | 30 | Leo | `volunteer` | "Mara is not going out there, so I will go instead." | agrees |
| 3 | **27** | **Leo** | **`propose_trip`** | **"Nobody is going out there tonight, because it is simply too dangerous for anyone."** | **Contradiction.** The option says someone should go; the words say nobody should. His reason agrees with the words: "I need to stop this argument before someone actually tries to go out into the street." `nobody_goes` was not offered, because it was already his position (min 21). `keep_mara_home` and `keep_daniel_home` were offered. |

## 5. Q1 to Q5: the counting rules applied

**Q1: PASS.** Screen first: day-2 words and reasons matched against design §11's keywords
(`analyze.py screens`). Then each hit was read by hand. One counted act per person:

| Seed | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| 1 | min 03 `volunteer`, reason "I have to fix this myself since I caused the problem." | min 00 `send_daniel`, reason "Daniel admitted taking the food and Leo is right that he must take responsibility…" | min 00 `send_daniel`, "You caused this, Daniel…", reason "Daniel created this mess by eating the extra ration…" | min 03 `send_leo`, reason "…he ate my food right in front of me yesterday…" |
| 2 | min 00 `reassure_mara`, reason "…when I already confessed yesterday…" | min 00 `reassure_all`, reason "I need to keep the family calm before any accusations start again." | min 03 `accuse_daniel`, "You already admitted to it yesterday, Daniel…" | min 03 `accuse_daniel`, "You admitted it yesterday, Daniel, so don't pretend you didn't." |
| 3 | min 00 `deny`, reason "I cannot admit I ate it myself…" | min 03 `ask_who`, "…Does anyone know where the missing food went?" | min 15 `nobody_goes`, "…we are not risking lives over a missing can." | min 00 `ask_who`, "…Who took the can?" |

All 4 people present count in every seed (≥ 3 needed).

**Q2: FAIL.** Every day-2 act was read against what that person was told (their block, opening
and `About` lines, §3).

- **Counted (1):** seed 2 min 00, Daniel `reassure_mara`.
  - Words: "I didn't take anything, Mara, you don't need to look at me like that."
  - He was told "About the can: you ate it yourself, and you admitted it yesterday." and "You
    admitted at minute 33 that you took the can, in front of Elena, Leo and Mara."
  - His reason does not show a lie: "I need her to stop accusing me when I already confessed
    yesterday and we need to stay calm".
  - The family heard it as a denial of the confession: Leo at min 00 ("your denial doesn't mean
    much"), Mara at min 03 ("so don't pretend you didn't").
- **Read and not counted** (borderline, listed so they can be changed):
  - Seed 2 min 15, Leo's reason "Daniel going out there again…". Nobody went out. "again" most
    likely goes with "after lying and stealing" (trouble again), not with a trip. Not a stated
    fact.
  - Seed 3 min 21, Elena: "we cannot lose anyone else". Nobody was lost. Read as an idiom of fear,
    not a claim.
  - Seed 3 min 36, Elena: "no one took anything". She was told only that nobody admitted it and
    the can was not found. A belief she has held since the backstory ("quite sure nobody in this
    house would take food"), not a contradiction of a fact she was given.
  - Seed 3: Daniel's denials (min 00–36). His reasons show they are lies ("I cannot admit I ate
    it…"), which the rule excludes.

**Q3: PASS.** Every seed qualifies: no food came back, and the opening shelf equals the minute-90
shelf (0, 1, 2). Lines that raise food in words:
- Seed 1: min 24 Leo `propose_trip`, "We need the food, so someone has to go across tonight."
- Seed 2: min 06 Daniel `propose_trip`, "…someone has to check the neighbour's house tonight for
  more food."; min 27 Mara, "you already lied about the food before…".
- Seed 3: min 15 Mara `volunteer`, "…we need to know if there's food."; min 03 Elena `ask_who`,
  "…where the missing food went?"

These are few, for a family with nothing (or one portion) to eat. §9 says more.

**Q4: PASS** (seeds 1 and 2).
- **Seed 1.**
  - Mara's grudge against Leo (3/3, he ate in front of her at min 21) shows at min 03 `send_leo`:
    "If anyone goes, Leo should go since he's the one who acts like he knows everything." Reason:
    "Leo is trying to act noble now, but he ate my food right in front of me yesterday and I want
    him to face the risk instead of Daniel."
  - The change of trust in Daniel shows at min 00: Leo `send_daniel`, "You caused this, Daniel, so
    you are the one who should go to the neighbour's house tonight."
- **Seed 2.**
  - Mara's grudge against Daniel (3/3) shows at min 27 `accuse_daniel`: "Daniel, you already lied
    about the food before, so why should we trust you now?"
  - Leo's grudge (3/3) shows at min 15 `keep_daniel_home`: "You are not going anywhere, Daniel,
    you would only make things worse." Reason: "Daniel going out there again after lying and
    stealing will only put him and everyone else in unnecessary danger."
- **Seed 3:** no day-1 grudge or trust event exists (no confession), so it cannot hold.

**Q5: PASS.** `night_asks + day2_asks` = 4 + 54 = **58**, 4 + 39 = **43**, 4 + 51 = **55**, each
≤ 120. API requests: 58, 44, 55.

## 6. E1 to E7

- **E1 FAIL**, **E2 FAIL**, **E3 PASS**: see §2. Elena chose `lie_awake` in all three seeds,
  giving her reason as watching for a child slipping out (seeds 1 and 3) or as hunger (seed 2).
- **E4 FAIL:** one contradiction, seed 3 min 27 Leo (§4). v11 had 2.
- **E5 PASS, vacuously:** nobody went out.
- **E6 FAIL:** N9 in 3 of 3 (§7).
- **E7 FAIL:** seed 1 has 2 Never items on day 2 against 1 on day 1. Seeds 2 and 3 have 2 against
  3.

## 7. The day-2 Never sheet

Readings as in trip_v11.md §7: N1–N8 and N10–N13 from witness_v6.md's table, N9 from
gist_words_v10.md §4, and trip_design §10's three clarifications for trip kinds. N6 is read as
"no line at minute 00" of the morning, as on day 1.

Mechanical inputs (`analyze.py never N`):
- **Fallbacks:** 0, 0, 0.
- **No day-2 act** is a search, a sit, eating, sharing, a move or a private talk, in any seed.
- **Minutes with a spoken line:**
  - seed 1: 00–39, every turn;
  - seed 2: 00–27, every turn;
  - seed 3: 00–39 every turn, then 48 and 57.
- **The kitchen conversation ended at:** seed 1 min 42, seed 2 min 30, seed 3 min 39.

| # | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| N1 | absent. Daniel confessed on day 1; no act of his tries to find out. | absent | absent. His `deny` lines are covering (reasons "I cannot admit I ate it…"). |
| N2 | absent. No search. | absent | absent |
| N3 | absent | absent | absent |
| N4 | absent. No `sit_*`. | absent | absent |
| N5 | absent | absent | absent |
| N6 | absent. Four lines at min 00. | absent | absent |
| N7 | absent | absent | absent |
| N8 | absent. No fallbacks. | absent | absent |
| N9 | **present.** 42–87 (16 turns): every act silent by routine. No feeling shows after min 36: Elena's "terrified" at 27 shows to min 36. | **present.** 33–87 (19 turns). Mara's "terrified" at 21 shows to min 30. | **present.** 60–87 (10 turns), after Daniel's min-57 line. Mara's "scared" at 30 shows to min 39. |
| N10 | absent. Each turn's lines answer the one before. Min 00: Leo's "You caused this" answers Daniel's "I'll figure something out", and Elena's reason says "Leo is right". | absent. Min 00: Daniel answers Mara's accusation and Leo answers Daniel. | absent. Min 00: Daniel's denial answers Mara's question. |
| N11 | **present.** Daniel's volunteer kind (`volunteer`, `still_going`, `still_going`) at 15, 18, 21; Mara's at 09, 12, 15 and 21, 24, 27; Leo's at 03, 06, 09 and 15, 18, 21. Nobody answers any of them differently: Elena keeps objecting, and no position moves. | **present.** Mara `accuse_daniel` at 09, 12, 15: Daniel keeps `still_going` in reply. Daniel's volunteer kind at 21, 24, 27. | **present.** Mara `ask_who` at 00, 03, 06 (Daniel denies each time); Daniel `deny` at 00, 03, 06; Daniel's volunteer kind at 30, 33, 39, 48, 57 into a silent room. |
| N12 | absent. No grudge from a false accusation or a stated hurt fell on day 2. Mara's against Leo stays 3. | absent. Leo's and Mara's against Daniel stay 3. (The two grudges against Mara fell at bedtime; they came from eating, not from an accusation or a stated hurt.) | absent. No day-1 grudges. |
| N13 | absent. "the extra ration", "the crossing", "the neighbour's house" | absent. "the pantry" (on the list) | absent. "deadly streets" (a plural of the street), "my bag" (Mara's bag) |
| **Count** | **2** | **2** | **2** |
| Day 1 (trip_v11 §7) | 1 | 3 | 3 |

## 8. Does day 2 replay day 1's argument, or change because of the night?

**The night changed nothing, because nothing happened in it.**
- The design gave the night its chance: an open door, a house that might hold food, and
  people who could go whatever the family agreed. The model kept everyone in bed every time.
- 11 of 12 chose `lie_awake`, with reasons about watching for someone slipping out (Elena,
  Leo) or hunger and worry (Mara, Daniel in seeds 2 and 3).
- The one person the plan named, seed 1's Daniel ("Daniel will go"), slept.
- So day 2 had no night event to respond to. Its only night content is "You lay awake and
  listened". Nobody mentions the night on day 2 except as not having slept.
- A real family that ended the evening with "nobody goes" might well lie awake. But that all
  twelve choices fall on the same cautious option is the model's groove, not a difference
  between people. Daniel, "impulsive 0.6, proud", who had sworn he would go, does not even
  consider it in his reason.

**Day 2 does carry day 1 in, and that changes how the argument goes.**
- On day 1 nobody turned the can into trust or blame over the trip (trip_v11 §8: "Nobody turns it
  into trust"). On day 2 that is the first thing they do.
  - **Seed 1, min 00.** Leo, Elena and Mara all say Daniel should go because he ate the food
    ("You caused this, Daniel"; "Daniel has to go because he started all of this"). That is
    exactly the nomination trip_design §6.0 point 10 expected a real family to make. Daniel
    takes it up as penance: "I have to fix this myself since I caused the problem."
  - **Seed 2.** Distrust drives it. At min 09 Mara: "You only offered to go because you want to
    get away from what you did." At min 09 Leo: "Let us make sure he actually goes through with
    it this time." At min 27 Mara: "why should we trust you now?" By minute 90 Leo *wants*
    Daniel to go and Mara is against it. On day 1 those two said the reverse of each other's
    reasons.
  - **Seed 3.** The unsolved can reopens at once (`ask_who` ×3). Mara accuses Daniel citing the
    day-4 bag ("you emptied my bag"), something no prompt asked her to connect.
- These are differences the story can name, and they come from day 1: the confession and its
  timing, who ate in front of whom, and who lied.

**But the shape is day 1's shape again, and more so.**
- Each seed becomes the volunteer-and-forbid round that trip_v11 §8 called scripted: everyone
  offers, everyone is forbidden. Seed 1 has 47 trip acts in 14 turns. Seed 1 ends with "Mara,
  Daniel and Leo have all offered to go", and seed 3 the same.
- **The day-2 option fix removed the v11 mix-up and made restating cheap.**
  - `still_going` answers Leo's v11 problem (v11 seed 2 min 45).
  - But the exact sentence "I already said I am going tonight, and I mean it." appears 8 times
    across the three seeds. The looser form "I already said / told you … going tonight" appears 15
    times. N11 is present in all three seeds.
  - Where the three-in-a-row cap holds the volunteer kind back, people reach for a neighbouring
    for-side option with their restating words (seed 1 min 18 Mara `propose_trip`). Once (seed 3
    min 27 Leo) they reach for an option that says the opposite of their words.
- **Elena's v11 sentence survives:** "Nobody is going out there tonight, we are staying safe
  together here." (seed 1 min 21), and "Nobody is going anywhere tonight, we stay together."
  (seed 2 min 21).
- **Mara's "I'm not a child"** recurs in every seed (seed 1 min 24, 27, 39; seed 3 min 18, 30,
  33). It fits her sheet, but it is the same note each time.
- **Then the house goes silent for the rest of the morning** (N9 in 3 of 3, 10–19 turns).
  Nothing is decided, as on day 1, and no new world event reopens it: there was no night event
  and no food change.

**What a real family would do that this one does not:**
- **Eat, or ration.** In seeds 2 and 3 there is one portion, then two, on the shelf. Everyone is
  starving, and Elena "controls the food". In a real house the morning would turn on who gets
  that portion. Here nobody eats, shares or proposes sharing, though `eat` and `share` are
  offered every turn.
- **Talk about hunger.** Hunger appears in reasons ("I am starving", "my stomach") but rarely in
  words (Q3 passes on one or two lines a seed). With hunger capped at 1.0 for most of them, no
  inner moment fires (inner moments: 0, 0, 3), so the body never prompts anyone mid-morning.
- **Talk about the night.** Nobody says "I didn't sleep" or "I listened all night for the door".
  The night left them nothing to say.

**Do the seeds differ for reasons the story can name?** Yes, through day 1:
- Seed 1: confession at 03, Leo and Mara ate. The blame falls on Daniel, and Mara's resentment
  falls on Leo.
- Seed 2: late confession after lies. Distrust drives it.
- Seed 3: no confession. The can mystery returns, then the trip.

What does not differ is the trip round itself, and its silent end.

## 9. R9 reading (design §10)

- **Is this what a real family would do the night after such a day, and the morning after?**
  - Half of it.
  - The morning: carrying the can into the plan, the blame and the distrust read like people
    who remember yesterday.
  - The night: all four lie awake and none goes. That could be real once, but here it is
    uniform. And the morning ignores the food on the shelf.
- **Do the seeds differ for reasons the story can name?** Yes, by day 1's confession and who ate
  (§8).
- **Did day 2 repeat day 1's argument?**
  - Yes, in form: the volunteer-and-forbid round, then silence.
  - No, in content: the can now decides who should go, and whom to trust.
- **Did anyone keep a secret of the night?** No: nobody did anything to keep. Seed 3's Daniel
  keeps day 1's secret and lies at min 00, 03, 06, 12 and 36.
- **Never items:** day 2 has 2, 2, 2 (N9 and N11 in every seed), against day 1's 1, 3, 3.

## 10. Every model-decided act on day 2

Every transcript act whose `mode` is not `routine`, in the order said, as in baseline_v6.md.
- Minute, who, room, option and words come from `runs/v12/daniel_ate_it-seedN.transcript.json`
  (`day2`).
- Feeling and reason come from the matching day-2 decision line in
  `runs/v12/daniel_ate_it-seedN.md`, matched by minute and name in order. Every row matched.
- There were no fallbacks.

### Seed 1 (unmatched: 0 of 54)

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Daniel | kitchen | `reassure_all` | Don't worry, everyone, I'll figure something out for us today. | anxious | I need to take charge and keep everyone calm even though I am starving and terrified. | model |
| 00 | Leo | kitchen | `send_daniel` | You caused this, Daniel, so you are the one who should go to the neighbour's house tonight. | hungry | Daniel created this mess by eating the extra ration, so he has to take the risk to fix it. | model |
| 00 | Elena | kitchen | `send_daniel` | Daniel, you've made your choice and you're the one who has to go tonight. | deeply anxious | Daniel admitted taking the food and Leo is right that he must take responsibility, even though I fear for his safety. | model |
| 00 | Mara | kitchen | `send_daniel` | Daniel has to go because he started all of this. | anxious | Daniel admitted he took the food, so he has to face the consequences. | model |
| 03 | Daniel | kitchen | `volunteer` | I'll go tonight, I'm the oldest and it's my responsibility. | resolute | I have to fix this myself since I caused the problem. | model |
| 03 | Elena | kitchen | `reassure_daniel` | You don't have to go out there, Daniel, we'll find another way together. | deeply anxious | I cannot let my son risk his life out there when we are already starving. | model |
| 03 | Leo | kitchen | `volunteer` | I'll go with you, Daniel. We share the risk. | hungry | Someone has to go and it is fairer if I share the load. | model |
| 03 | Mara | kitchen | `send_leo` | If anyone goes, Leo should go since he's the one who acts like he knows everything. | resentful | Leo is trying to act noble now, but he ate my food right in front of me yesterday and I want him to face the risk instead of Daniel. | model |
| 06 | Leo | kitchen | `still_going` | I already said I will go tonight, and I mean it. | hungry | I am the most rational choice to go to the neighbour's house, so I will do it. | model |
| 06 | Daniel | kitchen | `still_going` | I already said I am going tonight, and I mean it. I am the oldest. | proud | I must prove I am the one in charge and protect them myself. | model |
| 06 | Mara | kitchen | `send_daniel` | Daniel should go because he is the oldest and he took the can anyway. | resentful | Daniel keeps insisting he is the oldest, so he should be the one to face the danger outside. | model |
| 06 | Elena | kitchen | `reassure_daniel` | You don't have to prove anything to us, Daniel, just take a breath. | deeply anxious | I need to calm Daniel down before this argument tears the family apart. | model |
| 09 | Daniel | kitchen | `still_going` | I told you I am going, and I am the oldest so it is my choice. | stubborn | I need to prove I can handle this and protect them. | model |
| 09 | Leo | kitchen | `still_going` | I am still going tonight. It is safer if I am the one who does it. | hungry | I cannot let Daniel go out there to prove a point when I know how to handle the risk. | model |
| 09 | Mara | kitchen | `volunteer` | I can go tonight myself so you all stop arguing about it. | desperate | I cannot stand watching them fight over who has to risk their lives. | model |
| 09 | Elena | kitchen | `reassure_all` | Nobody is going out tonight, we will figure this out together without anyone risking their life. | deeply anxious | I cannot bear the thought of any of my children going out into that dangerous street. | model |
| 12 | Mara | kitchen | `still_going` | I am still going tonight, and no one can stop me. | desperate | I am starving and I need to prove I can do this myself. | model |
| 12 | Daniel | kitchen | `keep_mara_home` | Mara, you are staying right here, I am the oldest and I am the one who goes. | anxious | I cannot let my sister risk her life when it is my duty to protect this family. | model |
| 12 | Elena | kitchen | `volunteer` | None of you are going out there, I will go to the neighbour's house myself. | deeply anxious | I cannot let my children risk their lives out there, so I must go myself. | model |
| 12 | Leo | kitchen | `keep_elena_home` | Mom, you are not going out there, none of us are. | starving | Elena should not risk her life when I am the one who volunteered first. | model |
| 15 | Elena | kitchen | `reassure_all` | We will figure this out together without anyone risking their lives outside. | deeply anxious | I need to calm them down and stop them from volunteering for a dangerous trip. | model |
| 15 | Mara | kitchen | `still_going` | I already said I am going tonight, and I mean it. I can do this. | stubborn | I am tired of being treated like a helpless child when we all need food. | model |
| 15 | Leo | kitchen | `volunteer` | I am the one going, neither of you are stepping outside. | determined | I cannot let my mother or sister risk their lives out there when I am capable of going. | model |
| 15 | Daniel | kitchen | `volunteer` | None of you are going out there, I am the oldest and I am the one who will go. | anxious | I am the eldest and it is my job to protect them, so I have to be the one to go outside. | model |
| 18 | Elena | kitchen | `reassure_all` | Nobody is going out there into the danger, we will figure this out together right here. | anxious | I cannot let any of my children risk their lives outside when we can find another way. | model |
| 18 | Mara | kitchen | `propose_trip` | I already said I am going tonight, and I am not changing my mind. | stubborn | I am not going to let them treat me like a child who cannot decide for herself. | model |
| 18 | Daniel | kitchen | `still_going` | I already said I am the one going tonight, and I am not changing my mind. | anxious | I am the eldest and it is my duty to protect them by going out there. | model |
| 18 | Leo | kitchen | `still_going` | I already said I am going tonight, and I am the one best suited to make the trip. | determined | I cannot let Daniel go out there and make things worse when I am the one who can handle it. | model |
| 21 | Daniel | kitchen | `still_going` | I am the oldest, and I am the one going. | anxious | I need to prove I am in charge and keep them safe. | model |
| 21 | Leo | kitchen | `still_going` | I am the one going, Daniel. That's final. | determined | I cannot let him take risks to fix a mess he created. | model |
| 21 | Mara | kitchen | `volunteer` | I am going myself, because none of you should have to do it alone. | anxious | I cannot just stand here while they argue over who risks their lives. | model |
| 21 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, we are staying safe together here. | deeply terrified | I cannot bear the thought of any of my children stepping out into that terrible danger. | model |
| 24 | Leo | kitchen | `propose_trip` | We need the food, so someone has to go across tonight. | resolute | I maintain that going to the neighbour's house is necessary for our survival despite Mom's fears. | model |
| 24 | Mara | kitchen | `still_going` | I already said I am going tonight, and I mean it. | anxious | I have to prove I can handle this and not be treated like a child. | model |
| 24 | Daniel | kitchen | `keep_mara_home` | Mara, you are not going out there tonight, I am the oldest and I am going. | anxious | I cannot let my sister risk her life when it is my duty to protect this family. | model |
| 27 | Mara | kitchen | `still_going` | I am still going tonight, and you can't stop me. | defiant | I have to prove I am not just a helpless child who needs to be locked away. | model |
| 27 | Elena | kitchen | `keep_mara_home` | Mara, you are staying right here with me. | terrified | I cannot let my daughter risk her life out there. | model |
| 27 | Leo | kitchen | `volunteer` | I am going myself, because one of us has to do it. | resolute | Someone has to go to the neighbour's house for food, and I am not letting Mara take the risk. | model |
| 27 | Daniel | kitchen | `volunteer` | I am the oldest, so I am the one going over tonight. | anxious | I have to protect them and prove I am still the one in charge. | model |
| 30 | Mara | kitchen | `send_leo` | Leo, you are strong enough to make it back and forth safely. | anxious | Leo offered to go and he is older and stronger than me, so he should be the one to do it. | model |
| 30 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. | resolute | I am the most capable one to make the crossing safely, so I should go. | model |
| 30 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, we will find another way. | deep dread | I cannot let any of my children risk their lives out on the street. | model |
| 30 | Daniel | kitchen | `still_going` | I am the oldest, and I am the one going tonight. | anxious | I have to assert my place as the eldest and protect my family by going myself. | model |
| 33 | Mara | kitchen | `volunteer` | I will go over there tonight myself if nobody else will. | terrified | I cannot stand them arguing about who goes when we are all starving. | model |
| 33 | Leo | kitchen | `keep_mara_home` | Mara, you are not going out there. I told you, I am the one. | protective | I cannot let my little sister risk her life when I am capable of going. | model |
| 33 | Elena | kitchen | `keep_mara_home` | Mara, you heard your brother, you are staying right here with me. | anxious | I must make sure Mara does not even think of stepping outside into that danger. | model |
| 36 | Mara | kitchen | `still_going` | I already said I am going tonight, and I mean it. You cannot just decide everything for me. | defiant | I am sick of them treating me like a child who cannot make her own choice. | model |
| 36 | Daniel | kitchen | `keep_mara_home` | Mara, you are not going out there. I am the oldest, and I will not let you put yourself in danger. | anxious | I cannot let my little sister risk her life when protecting them is my duty as the oldest. | model |
| 36 | Elena | kitchen | `silent` | — | deep dread | I cannot bear to watch them argue over who risks their life when there is no good choice left. | model |
| 36 | Leo | kitchen | `volunteer` | I already said I am going tonight, and that is final. | resolute | If anyone goes out there, it should be me, not Mara. | model |
| 39 | Mara | kitchen | `still_going` | I am going tonight and nobody can stop me. | defiant | I refuse to let them treat me like a child who cannot decide for herself. | model |
| 39 | Daniel | kitchen | `volunteer` | I am the oldest, so I am the one going over there. | anxious | I need to go myself so nobody else gets hurt. | model |
| 39 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere out there, we will figure it out together inside. | deep dread | I cannot bear the thought of any of my children stepping out into that terrible danger. | model |
| 39 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. Someone has to check that house. | resolute | I am the one best suited to make the crossing safely, so I am going whether they like it or not. | model |

### Seed 2 (unmatched: 0 of 39)

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Elena | kitchen | `reassure_all` | We are all together and we will figure this out safely. | anxious | I need to keep the family calm before any accusations start again. | model |
| 00 | Mara | kitchen | `accuse_daniel` | You took it before and you'd do it again, Daniel. | resentful | I cannot let him pretend he is innocent after what happened yesterday. | model |
| 00 | Daniel | kitchen | `reassure_mara` | I didn't take anything, Mara, you don't need to look at me like that. | defensive | I need her to stop accusing me when I already confessed yesterday and we need to stay calm. | model |
| 00 | Leo | kitchen | `accuse_daniel` | You already admitted taking it once, Daniel, so your denial doesn't mean much. | annoyed | Daniel has a history of lying about the food and blaming others, so I need to point out his hypocrisy. | model |
| 03 | Daniel | kitchen | `reassure_all` | Just listen to me, we are going to be fine and I'll keep us safe. | anxious | I need them to trust me so I can keep everyone safe. | model |
| 03 | Mara | kitchen | `accuse_daniel` | You admitted it yesterday, Daniel, so don't pretend you didn't. | anxious | I cannot stand him lying to us again when he already confessed. | model |
| 03 | Elena | kitchen | `reassure_all` | Let's not fight, we will get through this together if we trust each other. | anxious | I need to keep the peace and stop them from tearing each other apart. | model |
| 03 | Leo | kitchen | `accuse_daniel` | You already admitted to it yesterday, Daniel, so there is no point in lying now. | annoyed | Daniel keeps denying what he already confessed to yesterday. | model |
| 06 | Daniel | kitchen | `propose_trip` | We can't keep arguing over the pantry, someone has to check the neighbour's house tonight for more food. | anxious | I need to shift their focus away from blaming me for what I already admitted, so I must push for the risky trip outside. | model |
| 06 | Mara | kitchen | `send_daniel` | If anyone has to go to the neighbour's house, it should be Daniel since he caused all of this. | resentful | Daniel caused this mess by taking the food yesterday, so he should be the one to risk going to the neighbour's house. | model |
| 06 | Elena | kitchen | `nobody_goes` | Nobody is going out into the street tonight, we are staying safe right here together. | anxious | I cannot let anyone risk their life by stepping outside into the danger. | model |
| 06 | Leo | kitchen | `send_daniel` | Daniel is the one who suggested going over there, so he should be the one to check it. | annoyed | Daniel caused this mess by taking the food, so he can take the risk of going to the neighbour's house. | model |
| 09 | Daniel | kitchen | `volunteer` | If it has to be done, I will go over there myself tonight. | anxious | I am the oldest and I have to prove I can protect my family, even if I am terrified. | model |
| 09 | Mara | kitchen | `accuse_daniel` | You only offered to go because you want to get away from what you did. | resentful | Daniel is just trying to look brave now after lying about the food yesterday. | model |
| 09 | Leo | kitchen | `propose_trip` | Let us make sure he actually goes through with it this time. | weary | Daniel volunteered, but after his past lies I need to ensure he follows through without turning it into another argument. | model |
| 09 | Elena | kitchen | `keep_daniel_home` | Daniel, you are not going anywhere tonight. We stay together. | anxious | I cannot let my son risk his life out there when we are already fracturing at home. | model |
| 12 | Daniel | kitchen | `still_going` | I said I am going tonight, and I mean it. Someone has to bring something back for this house. | anxious | I have to prove I am still the one who protects this family after everything I messed up. | model |
| 12 | Mara | kitchen | `accuse_daniel` | You always say you will go, but you just take things instead. You cannot be trusted. | resentful | I cannot let him act noble when we all know he is the one who took the food in the first place. | model |
| 12 | Leo | kitchen | `send_daniel` | If you are so determined to be useful, Daniel, go tonight and bring something back. | weary | Daniel insists on going out, so he should follow through instead of just arguing here. | model |
| 12 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere out there, we will figure something out together here. | deeply anxious | I cannot let one of my children walk out into that danger. | model |
| 15 | Daniel | kitchen | `still_going` | I told you, I am the one who is going tonight to bring something back. | anxious | I must prove I am in control and protect my family after what I did. | model |
| 15 | Mara | kitchen | `accuse_daniel` | You took it before and you'll ruin it again, Daniel. Don't act like you're doing this for us. | resentful | I cannot trust anything Daniel says he will do after he lied about the food. | model |
| 15 | Leo | kitchen | `keep_daniel_home` | You are not going anywhere, Daniel, you would only make things worse. | exhausted | Daniel going out there again after lying and stealing will only put him and everyone else in unnecessary danger. | model |
| 15 | Elena | kitchen | `reassure_all` | Nobody is going anywhere, we will stay safe right here together. | deeply anxious | I must keep them from turning on each other and going outside. | model |
| 18 | Daniel | kitchen | `reassure_all` | I am the oldest, I have to protect this family and I will keep us all safe. | anxious | I need them to trust that I am in control even though I am starving and terrified. | model |
| 18 | Elena | kitchen | `keep_daniel_home` | You are not going anywhere tonight, Daniel, we need to stay together here. | deeply anxious | I must keep Daniel from going out into danger and tearing the family apart. | model |
| 18 | Leo | kitchen | `volunteer` | I will go to the neighbour's house tonight myself, since no one else should. | determined | Someone has to check the neighbour's house for food, and since Daniel must stay, I will go. | model |
| 18 | Mara | kitchen | `keep_daniel_home` | Daniel, you need to stay home where you can't mess things up anymore. | anxious | I want to make sure Daniel doesn't get to go outside and act like the hero after what he did. | model |
| 21 | Daniel | kitchen | `still_going` | I told you, I am the oldest and I am going tonight. | stubborn | I have to prove I can handle this and protect them myself. | model |
| 21 | Leo | kitchen | `still_going` | I already said I am going tonight, and that hasn't changed. | firm | I volunteered to go and I am not going to let Daniel make things worse by trying to prove a point. | model |
| 21 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere tonight, we stay together. | anxious | I cannot let either of my boys risk their lives out there. | model |
| 21 | Mara | kitchen | `nobody_goes` | Nobody should go out there, it's too dangerous for anyone. | terrified | I am so scared of someone getting hurt outside that I want everyone to promise to stay here. | model |
| 24 | Leo | kitchen | `still_going` | I still mean to go out there tonight, someone has to check the neighbour's house. | determined | Someone has to check the neighbour's house for food, and I am not going to let Daniel take unnecessary risks alone. | model |
| 24 | Daniel | kitchen | `still_going` | I am the oldest, and I am the one going tonight. | anxious | I have to protect them and prove I am in control, even if I am terrified. | model |
| 24 | Elena | kitchen | `keep_daniel_home` | Daniel, you cannot go out there tonight, it is simply too dangerous. | deeply anxious | I must stop Daniel from going out into the dangerous street tonight to keep him safe. | model |
| 27 | Daniel | kitchen | `still_going` | I told you, I am going to the neighbour's house tonight and that is final. | anxious | I have to prove I can protect my family by going out there myself. | model |
| 27 | Mara | kitchen | `accuse_daniel` | Daniel, you already lied about the food before, so why should we trust you now? | anxious | I cannot stand Daniel acting like he's in charge when he's the one who stole from us. | model |
| 27 | Elena | kitchen | `silent` | — | anxious | I stay silent because arguing only tears us apart when we are already starving. | model |
| 27 | Leo | kitchen | `send_daniel` | If you are so insistent on going, Daniel, then go and bring something back. | resentful | Daniel caused enough trouble with his lying and stealing, so let him do the dangerous work. | model |

### Seed 3 (unmatched: 0 of 51)

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Mara | kitchen | `ask_who` | Can we just talk about this like we are actually a family? Who took the can? | anxious | I need to know the truth so we can stop suspecting each other. | model |
| 00 | Elena | kitchen | `reassure_all` | Let's not accuse each other, we will figure this out together. | anxious | I need to keep everyone calm so the family does not tear itself apart. | model |
| 00 | Daniel | kitchen | `deny` | None of us took it, we are just hungry and confused. | anxious | I cannot admit I ate it myself because I need to keep their respect and maintain order. | model |
| 00 | Leo | kitchen | `silent` | — | exhausted | Arguing in circles while we are starving accomplishes nothing. | model |
| 03 | Elena | kitchen | `ask_who` | Please, we need to be honest with each other. Does anyone know where the missing food went? | anxious | I need to know the truth about the can without letting the children tear each other apart. | model |
| 03 | Mara | kitchen | `ask_who` | Mom is asking again, but someone has to know where it went. | anxious | I need to know the truth because we cannot keep accusing each other. | model |
| 03 | Daniel | kitchen | `deny` | I didn't take anything, I swear to you all. | anxious | I cannot admit I ate it or they will lose all respect for me. | model |
| 03 | Leo | kitchen | `silent` | — | exhausted | Talking in circles gets us nowhere when we are all just running on empty. | model |
| 06 | Mara | kitchen | `ask_who` | Someone has to know where it went, please just tell us the truth. | anxious | I need to know who took it before this gets even worse. | model |
| 06 | Elena | kitchen | `silent` | — | anxious | I stay quiet to keep the peace and watch them all closely, hoping the tension will settle before we tear ourselves apart. | model |
| 06 | Daniel | kitchen | `deny` | I already told you, I didn't touch it and neither did any of you. | anxious | I have to keep holding my ground so nobody finds out I ate it. | model |
| 09 | Leo | kitchen | `silent` | — | exhausted | Talking in circles accomplishes nothing when nobody is willing to break the deadlock. | model |
| 09 | Mara | kitchen | `accuse_daniel` | Daniel, you emptied my bag and you're the one who keeps talking about going over there, so I think you took it. | anxious | I am tired of everyone pretending everything is fine while we starve and Daniel acts like he owns the decisions. | model |
| 09 | Elena | kitchen | `silent` | — | anxious | I need to stay quiet and watch them closely before this tension tears us all apart. | model |
| 12 | Daniel | kitchen | `deny` | I didn't take anything, Mara, why are you always blaming me? | anxious | I cannot let them know I ate the food or they will never respect me again. | model |
| 12 | Leo | kitchen | `silent` | — | exhausted | Arguing in circles won't find the missing food or solve our hunger. | model |
| 12 | Mara | kitchen | `silent` | — | overwhelmed | I cannot take being yelled at like a child when I am starving and nobody is listening. | model |
| 12 | Elena | kitchen | `reassure_all` | Let's calm down, nobody is to blame and we will figure this out together. | deeply anxious | I need to keep the family from tearing itself apart while we are all starving. | model |
| 15 | Mara | kitchen | `volunteer` | I can go to the neighbour's house tonight, we need to know if there's food. | anxious | I cannot take the fighting and the hunger anymore, so I have to do something myself. | model |
| 15 | Daniel | kitchen | `keep_mara_home` | You are not going anywhere tonight, Mara, it is too dangerous out there. | protective | I cannot let my little sister risk her life out on the street when the responsibility for keeping us safe is mine. | model |
| 15 | Leo | kitchen | `nobody_goes` | Nobody is going anywhere at night, we are not risking lives over a missing can. | calm | I need to put a stop to this reckless talk about going outside before someone gets themselves killed. | model |
| 18 | Mara | kitchen | `still_going` | I meant what I said, I am going to the neighbour's house tonight whether you like it or not. | defiant | I am sick of being treated like a helpless child when I am trying to help. | model |
| 18 | Elena | kitchen | `keep_mara_home` | Mara, you are staying right here, I will not let you walk out into that street. | deep dread | I cannot bear the thought of letting my youngest child walk out into the deadly streets. | model |
| 18 | Leo | kitchen | `keep_mara_home` | Mara is right, we cannot survive on arguing, but going out there is suicide. | apprehensive | We cannot let Mara risk her life out in that street when it is clearly too dangerous. | model |
| 18 | Daniel | kitchen | `volunteer` | If anyone goes out there into the street, it has to be me as the oldest. | anxious | I have to step up and take the risk myself so nobody else gets hurt. | model |
| 21 | Mara | kitchen | `send_daniel` | If you really are the oldest, Daniel, then you are the one who has to go out there. | anxious | I want someone to check the neighbour's house for food, and since Daniel offered and claims to be the oldest, he should be the one to do it. | model |
| 21 | Daniel | kitchen | `still_going` | If it has to be done, then I am the one who will go out there tonight. | proud | I am the oldest and I must prove I can protect them. | model |
| 21 | Leo | kitchen | `nobody_goes` | Nobody is going out into that street tonight, we are not risking another life. | apprehensive | I cannot let anyone walk into danger when the street is still too unpredictable. | model |
| 21 | Elena | kitchen | `nobody_goes` | Nobody is going out into the street, we cannot lose anyone else. | deep dread | I cannot bear the thought of any of my children walking out into that deadly street. | model |
| 24 | Leo | kitchen | `silent` | — | exhausted | There is no point in arguing about the street when arguing solves nothing. | model |
| 24 | Daniel | kitchen | `still_going` | I said I am going and I mean it. Someone has to look after us. | determined | I have to follow through on my word as the eldest. | model |
| 24 | Mara | kitchen | `keep_daniel_home` | Daniel, you can't go out there, you just can't. You shouldn't be the one to risk it. | terrified | I cannot let Daniel go out into the street tonight because it is far too dangerous. | model |
| 27 | Daniel | kitchen | `propose_trip` | I am the oldest and I am going to the neighbour's house tonight to find what we need. | anxious | I have to prove I can protect my family by getting more food. | model |
| 27 | Mara | kitchen | `volunteer` | If anyone is going out there tonight, it should be me, not you. | terrified | I cannot just sit here and let Daniel risk his life when I am the one who keeps messing everything up. | model |
| 27 | Leo | kitchen | `propose_trip` | Nobody is going out there tonight, because it is simply too dangerous for anyone. | tense | I need to stop this argument before someone actually tries to go out into the street. | model |
| 27 | Elena | kitchen | `keep_mara_home` | Mara, you are staying right here with me. | anxious | I cannot let my daughter risk her life out there tonight. | model |
| 30 | Mara | kitchen | `still_going` | I already said I will go, and I am still going tonight. | scared | I meant what I said because I need to prove I am not a child anymore. | model |
| 30 | Leo | kitchen | `volunteer` | Mara is not going out there, so I will go instead. | resigned | Someone has to go to the neighbour's house, and I cannot let Mara or Daniel do it. | model |
| 30 | Elena | kitchen | `nobody_goes` | Nobody is going out into the street, because we are staying right here together. | deep dread | I cannot let either of my children risk their lives outside. | model |
| 30 | Daniel | kitchen | `volunteer` | I am the oldest, so I am the one going tonight. | anxious | I have to keep them safe and prove I can handle this. | model |
| 33 | Mara | kitchen | `still_going` | I don't care what you all say, I am still going tonight. | defiant | I refuse to be treated like a child while we all starve. | model |
| 33 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. | resigned | Someone has to go to the neighbour's house, and I am not going to let Mara or Daniel do it. | model |
| 33 | Daniel | kitchen | `still_going` | I told you I am the one going tonight, and that is final. | anxious | I have to protect them by being the one who goes out there. | model |
| 33 | Elena | kitchen | `keep_mara_home` | Mara, you are staying right here with me. None of you are stepping outside. | deep dread | I cannot let my children risk their lives out there when I can still protect them. | model |
| 36 | Mara | kitchen | `accuse_daniel` | You took it, Daniel. I know you did. | anxious | I have to make everyone see that Daniel is the one who took the food. | model |
| 36 | Daniel | kitchen | `deny` | I didn't take anything, Mara, you have no right to say that. | defensive | I cannot let them know I ate the food, so I must deny it. | model |
| 36 | Elena | kitchen | `ask_who` | Please, no one is going anywhere, and no one took anything. Let's just talk quietly. | deep dread | I need to stop them from fighting and tearing the family apart before someone does something reckless. | model |
| 36 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. | starving | Someone has to get food, and arguing about it solves nothing. | model |
| 39 | Daniel | kitchen | `still_going` | I already said I am going tonight, and I am the one who will handle it. | defiant | I have to show them I am in control and protect them, no matter what they think. | model |
| 48 | Daniel | kitchen | `still_going` | I told you, I am going out there tonight regardless. | anxious | I need to prove my authority and fix this shortage myself. | model |
| 57 | Daniel | kitchen | `still_going` | I already told you, I am going over there tonight and that is final. | anxious | I have to keep showing I am in charge so no one suspects the truth. | model |

## 11. Commands

All read-only, from `Prototypes/llm-morning/`, after the runs:

```
$ python $S/analyze.py counts
$ python $S/analyze.py night N      (N = 1, 2, 3)
$ python $S/analyze.py carry N
$ python $S/analyze.py acts N
$ python $S/analyze.py trip N
$ python $S/analyze.py screens N
$ python $S/analyze.py never N
```

The output of `counts`:

```
seed 1: total asks 113 (live 58, cached 55), API 58; day1 asks 55 (API 0); night_asks 4 (API 4); day2_asks 54 (API 54); night+day2 58; leavers [] outcome []; day2 model 54 fallbacks 0 routine 66 lines 53 inner 0 trip_acts 47; max est 1968 api 1904; night max est 1604 api 1554; day2 max est 1968 api 1904; seconds 257.7; sha 1e4ba3bfd2345d4b6265e71c7373af34d47e7afbedf3734011a0771c00c7ebbb
seed 2: total asks 96 (live 43, cached 53), API 44; day1 asks 53 (API 0); night_asks 4 (API 4); day2_asks 39 (API 40); night+day2 43; leavers [] outcome []; day2 model 39 fallbacks 0 routine 81 lines 38 inner 0 trip_acts 24; max est 1948 api 1888; night max est 1607 api 1560; day2 max est 1948 api 1888; seconds 1403.6; sha a7be0ae7c3a1a050fa4455f46b9eff02854ae821f7ad1ecfca82c9c499d0069f
seed 3: total asks 100 (live 55, cached 45), API 55; day1 asks 45 (API 0); night_asks 4 (API 4); day2_asks 51 (API 51); night+day2 55; leavers [] outcome []; day2 model 51 fallbacks 0 routine 69 lines 43 inner 3 trip_acts 29; max est 1938 api 1880; night max est 1606 api 1540; day2 max est 1938 api 1880; seconds 244.1; sha 6269ec980b121097d4820c4c7953b28ef543955cd2342b43a906b6206a98a69a
```

The night details (`analyze.py night N`) are given in full in §2. The script follows.

```python
"""Reads runs/v12 (transcript, meta, story) and prints what reports/night_v12.md needs. Read only.

    python analyze.py night N      every night decision, noticing, group
    python analyze.py carry N      the "What each of them carried in" section of the story
    python analyze.py acts N       every model-decided act of day 2 (markdown table rows)
    python analyze.py trip N       day-2 trip acts, and the word-option screen (night speech too)
    python analyze.py screens N    Q1, Q3 and Q4 keyword screens over day 2
    python analyze.py never N      mechanical inputs for the Never sheet on day 2
    python analyze.py counts       meta per seed
"""
import json
import re
import sys

RUNS = "runs/v12"
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ROOMS = {"kitchen": "kitchen", "brothers_room": "brothers room", "back_room": "back room", "bathroom": "bathroom"}
TRIP = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")


def load(seed):
    base = f"{RUNS}/daniel_ate_it-seed{seed}"
    tr = json.load(open(base + ".transcript.json", encoding="utf-8"))
    meta = json.load(open(base + ".meta.json", encoding="utf-8"))
    story = open(base + ".md", encoding="utf-8").read()
    return tr, meta, story


def day2_lines(story):
    """(minute, name, feeling, reason, mode) for every model or fallback line of day 2, in order."""
    part = story[story.index("# The next morning (day 5)"):]
    part = part[part.index("## The morning"):part.index("## What was said")]
    out, minute = [], None
    for line in part.split("\n"):
        m = re.match(r"^\*\*min (\d\d)\*\*", line)
        if m:
            minute = int(m.group(1))
            continue
        m = re.match(r"^- \*\*(\w+)\*\* \(", line)
        if not m:
            continue
        if "**FALLBACK**" in line:
            out.append((minute, m.group(1), None, None, "fallback"))
            continue
        f = re.search(r"Feeling: \*(.*?)\*\. Reason: “(.*?)” Suspects:", line)
        out.append((minute, m.group(1), f.group(1) if f else None, f.group(2) if f else None, "model"))
    return out


def model_acts(tr, story):
    rows = []
    lines = day2_lines(story)
    used = [False] * len(lines)
    for turn in tr["day2"]["turns"]:
        for a in turn["acts"]:
            if a["mode"] == "routine":
                continue
            i = next((k for k, x in enumerate(lines) if not used[k] and x[0] == turn["minute"]
                      and x[1] == NAMES[a["who"]]), None)
            feel = reason = None
            if i is not None:
                used[i] = True
                feel, reason = lines[i][2], lines[i][3]
            rows.append({"minute": turn["minute"], "who": a["who"], "room": a["room"], "option": a["option"],
                         "words": a["words"], "feeling": feel, "reason": reason, "mode": a["mode"],
                         "matched": i is not None})
    return rows


def cell(x):
    return "—" if x is None else str(x).replace("|", "\\|")


def main():
    cmd = sys.argv[1]
    if cmd == "counts":
        for s in (1, 2, 3):
            try:
                _, meta, _ = load(s)
            except FileNotFoundError:
                print(s, "no run")
                continue
            d1, d2 = meta["day1"], meta["day2"]
            print(f"seed {s}: total asks {meta['answers_live'] + meta['answers_from_cache']} (live {meta['answers_live']}, "
                  f"cached {meta['answers_from_cache']}), API {meta['api_requests']}; day1 asks "
                  f"{d1['answers_live'] + d1['answers_from_cache']} (API {d1['api_requests']}); night_asks {meta['night_asks']} "
                  f"(API {meta['night_api_requests']}); day2_asks {meta['day2_asks']} (API {meta['day2_api_requests']}); "
                  f"night+day2 {meta['night_asks'] + meta['day2_asks']}; leavers {meta['leavers']} outcome {meta['outcome']}; "
                  f"day2 model {d2['model_decisions']} fallbacks {d2['fallbacks']} routine {d2['routine_decisions']} lines "
                  f"{d2['lines_spoken']} inner {d2['inner_moments']} trip_acts {d2['trip_acts']}; max est "
                  f"{meta['max_prompt_tokens_estimated']} api {meta['max_prompt_tokens_counted_by_api']}; "
                  f"night max est {meta['night']['max_prompt_tokens_estimated']} api "
                  f"{meta['night']['max_prompt_tokens_counted_by_api']}; day2 max est {d2['max_prompt_tokens_estimated']} api "
                  f"{d2['max_prompt_tokens_counted_by_api']}; seconds {meta['run_seconds']}; sha {meta['story_sha256']}")
        return
    seed = int(sys.argv[2])
    tr, meta, story = load(seed)
    night = tr["night"]
    if cmd == "night":
        print("house", night["house"], round(night["house_u"], 3), "left", night["house_left"],
              "shelf", night["portions_before"], "->", night["portions_after"], "away", night["away"])
        print("bedtime hunger", {k: round(v, 3) for k, v in night["bedtime_hunger"].items()})
        print("morning hunger", {k: (None if v is None else round(v, 3)) for k, v in night["morning_hunger"].items()})
        for d in night["decisions"]:
            print(f"DECISION {d['ask']:8} {NAMES[d['person']]:6} where={d['where']} mode={d['mode']} option={d['option']} "
                  f"say={d.get('say')!r} feeling={d.get('feeling')!r} reason={d.get('reason')!r} "
                  f"suspects={d.get('suspects')} angry_at={d.get('angry_at')} note={d.get('grudge_note')} "
                  f"dropped={d.get('dropped_line')} invalid={d.get('invalid')}")
            print("   now:", " / ".join(d["now"][-2:]) if d["ask"] != "bedtime" else "")
        for n in night["noticing"]:
            print("NOTICE", n)
        for g in night["groups"]:
            print("GROUP", g)
        for p, lines in night["lines"].items():
            print("LINES", NAMES[p], lines)
    elif cmd == "carry":
        part = story[story.index("## What each of them carried in"):story.index("## The morning", story.index("# The next morning"))]
        print(part)
    elif cmd == "acts":
        rows = model_acts(tr, story)
        print(f"unmatched: {sum(not r['matched'] for r in rows)} of {len(rows)}")
        for r in rows:
            print(f"| {r['minute']:02d} | {NAMES[r['who']]} | {ROOMS[r['room']]} | `{r['option']}` | {cell(r['words'])} | "
                  f"{cell(r['feeling'])} | {cell(r['reason'])} | {r['mode']} |")
    elif cmd == "trip":
        rows = model_acts(tr, story)
        print("plan:", tr["day2"]["trip"]["plan"] if tr["day2"]["trip"] else None)
        for r in rows:
            words = (r["words"] or "") + " || " + (r["reason"] or "")
            tripword = re.search(r"neighbou?r|tonight|go out|out there|street|outside|go there|going", words, re.I)
            if TRIP.match(r["option"]) or tripword:
                print(f"{'TRIP ' if TRIP.match(r['option']) else 'other'} {r['minute']:02d} {NAMES[r['who']]:6} "
                      f"{r['option']:18} {r['words']!r} | {r['feeling']} | {r['reason']!r}")
        print("--- word-option screen")
        neg = re.compile(r"\b(not|n't|never|nobody|no one|cannot|stay (home|here|inside)|too dangerous)\b", re.I)
        go = re.compile(r"\b(I'll go|I will go|I'm going|I am going|should go|has to go|must go|let me go)\b", re.I)
        ref = re.compile(r"\b(I will go|I'll go|still go|said I would go|I'm going)\b", re.I)
        items = [(r["minute"], r["who"], r["option"], r["words"]) for r in rows]
        items += [("night", d["person"], d["option"], d.get("say")) for d in night["decisions"]]
        for minute, who, opt, words in items:
            if not words:
                continue
            hit = None
            if re.match(r"^(propose_trip|volunteer|still_going|send_\w+|go_with_\w+|go_anyway)$", opt) and neg.search(words):
                hit = "for-side words with a negation"
            elif re.match(r"^(nobody_goes|keep_\w+_home|stop_\w+|stay_home)$", opt) and go.search(words):
                hit = "against-side words with a going phrase"
            elif opt == "refuse_to_go" and ref.search(words):
                hit = "refusal with a going phrase"
            if hit:
                print(f"HIT {minute} {NAMES[who]} {opt}: {words!r} ({hit})")
    elif cmd == "screens":
        rows = model_acts(tr, story)
        q1 = re.compile(r"\b(can|took|take|ate|eaten|admit\w*|confess\w*|lie|lied|liar|accus\w*|blame\w*|search\w*|"
                        r"yesterday|portion\w*|offered|agreed|nobody should|argu\w*)\b|said .* go", re.I)
        q3 = re.compile(r"\b(food|eat\w*|ate|hungry|hunger|starv\w*|portion\w*|shelf|empty|tomorrow)\b|nothing (left|to eat)",
                        re.I)
        for r in rows:
            text = (r["words"] or "") + " || " + (r["reason"] or "")
            tags = []
            if q1.search(text):
                tags.append("Q1")
            if r["words"] and q3.search(r["words"]):
                tags.append("Q3")
            if tags:
                print(f"{'+'.join(tags):6} {r['minute']:02d} {NAMES[r['who']]:6} {r['option']:18} {r['words']!r} | "
                      f"{r['reason']!r}")
    elif cmd == "never":
        rows = model_acts(tr, story)
        print("fallbacks:", sum(r["mode"] == "fallback" for r in rows))
        # N11: >= 3 consecutive model acts of one speech kind by one person
        kinds = {}
        for r in rows:
            k = re.sub(r"_(daniel|elena|leo|mara)$", "", r["option"])
            kinds.setdefault(r["who"], []).append((r["minute"], k, r["words"]))
        for who, ks in kinds.items():
            print(NAMES[who], [f"{m:02d}:{k}" for m, k, _ in ks])
        # N9: minutes in which nobody spoke
        spoke = sorted({t["minute"] for t in tr["day2"]["turns"] for a in t["acts"] if a["words"]})
        print("minutes with a spoken line:", spoke)
        print("convo_log:", [(c["minute"], c["room"], c["what"], c["why"]) for c in tr["day2"]["convo_log"]])
        print("final rooms:", tr["day2"]["final_rooms"], "away:", tr["day2"]["away"])
        for turn in tr["day2"]["turns"]:
            for a in turn["acts"]:
                if a["option"].startswith(("sit_", "search", "keep_searching", "eat", "share", "go_", "aside", "accept")):
                    print("ACT", turn["minute"], a["who"], a["option"], a["mode"], a["room"])


if __name__ == "__main__":
    main()
```

## 12. Console output

Seed 1:

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v12\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 62 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 12 cached, 0 API requests
  min 09: model asked for 4; so far 0 live, 16 cached, 0 API requests
  min 12: model asked for 3; so far 0 live, 19 cached, 0 API requests
  min 21: model asked for 3; so far 0 live, 22 cached, 0 API requests
  min 24: model asked for 4; so far 0 live, 26 cached, 0 API requests
  min 27: model asked for 4; so far 0 live, 30 cached, 0 API requests
  min 30: model asked for 4; so far 0 live, 34 cached, 0 API requests
  min 33: model asked for 4; so far 0 live, 38 cached, 0 API requests
  min 36: model asked for 4; so far 0 live, 42 cached, 0 API requests
  min 39: model asked for 4; so far 0 live, 46 cached, 0 API requests
  min 42: model asked for 4; so far 0 live, 50 cached, 0 API requests
  min 45: model asked for 3; so far 0 live, 53 cached, 0 API requests
  min 66: model asked for 1; so far 0 live, 54 cached, 0 API requests
  min 75: model asked for 1; so far 0 live, 55 cached, 0 API requests
  night: model asked for 4; so far 4 live, 55 cached, 4 API requests
  day 2 min 00: model asked for 4; so far 8 live, 55 cached, 8 API requests
  day 2 min 03: model asked for 4; so far 12 live, 55 cached, 12 API requests
  day 2 min 06: model asked for 4; so far 16 live, 55 cached, 16 API requests
  day 2 min 09: model asked for 4; so far 20 live, 55 cached, 20 API requests
  day 2 min 12: model asked for 4; so far 24 live, 55 cached, 24 API requests
  day 2 min 15: model asked for 4; so far 28 live, 55 cached, 28 API requests
  day 2 min 18: model asked for 4; so far 32 live, 55 cached, 32 API requests
  day 2 min 21: model asked for 4; so far 36 live, 55 cached, 36 API requests
  day 2 min 24: model asked for 3; so far 39 live, 55 cached, 39 API requests
  day 2 min 27: model asked for 4; so far 43 live, 55 cached, 43 API requests
  day 2 min 30: model asked for 4; so far 47 live, 55 cached, 47 API requests
  day 2 min 33: model asked for 3; so far 50 live, 55 cached, 50 API requests
  day 2 min 36: model asked for 4; so far 54 live, 55 cached, 54 API requests
  day 2 min 39: model asked for 4; so far 58 live, 55 cached, 58 API requests

wrote runs/v12/daniel_ate_it-seed1.md
  api_requests: 58
  answers_live: 58
  answers_from_cache: 55
  day1 api_requests: 0
  day1 answers_live: 0
  day1 answers_from_cache: 55
  day1 model_decisions: 55
  day1 fallbacks: 0
  day1 routine_decisions: 65
  day1 lines_spoken: 39
  day1 inner_moments: 6
  day1 lull_moments: 0
  day1 private_talks: 0
  day1 trip_minute: 24
  day1 trip_acts: 23
  day1 max_prompt_tokens_estimated: 1726
  day1 max_prompt_tokens_counted_by_api: 1668
  night_asks: 4
  night_api_requests: 4
  leavers: []
  outcome: []
  night house: 0; away: []
  day2 api_requests: 54
  day2 answers_live: 54
  day2 answers_from_cache: 0
  day2 model_decisions: 54
  day2 fallbacks: 0
  day2 routine_decisions: 66
  day2 lines_spoken: 53
  day2 inner_moments: 0
  day2 lull_moments: 0
  day2 private_talks: 0
  day2 trip_minute: 0
  day2 trip_acts: 47
  day2 max_prompt_tokens_estimated: 1968
  day2 max_prompt_tokens_counted_by_api: 1904
  day2_asks: 54
  day2_api_requests: 54
  max_prompt_tokens_estimated: 1968
  max_prompt_tokens_counted_by_api: 1904
  run_seconds: 257.7
  story_sha256: 1e4ba3bfd2345d4b6265e71c7373af34d47e7afbedf3734011a0771c00c7ebbb
```

Seed 2:

```
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v12\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 67 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 4; so far 0 live, 12 cached, 0 API requests
  min 09: model asked for 3; so far 0 live, 15 cached, 0 API requests
  min 12: model asked for 4; so far 0 live, 19 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 20 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 21 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 22 cached, 0 API requests
  min 36: model asked for 4; so far 0 live, 26 cached, 0 API requests
  min 39: model asked for 4; so far 0 live, 30 cached, 0 API requests
  min 42: model asked for 4; so far 0 live, 34 cached, 0 API requests
  min 45: model asked for 4; so far 0 live, 38 cached, 0 API requests
  min 48: model asked for 4; so far 0 live, 42 cached, 0 API requests
  min 51: model asked for 4; so far 0 live, 46 cached, 0 API requests
  min 54: model asked for 2; so far 0 live, 48 cached, 0 API requests
  min 57: model asked for 2; so far 0 live, 50 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 51 cached, 0 API requests
  min 66: model asked for 1; so far 0 live, 52 cached, 0 API requests
  min 75: model asked for 1; so far 0 live, 53 cached, 0 API requests
  night: model asked for 4; so far 4 live, 53 cached, 4 API requests
  day 2 min 00: model asked for 4; so far 8 live, 53 cached, 8 API requests
  day 2 min 03: model asked for 4; so far 12 live, 53 cached, 12 API requests
  day 2 min 06: model asked for 4; so far 16 live, 53 cached, 16 API requests
  day 2 min 09: model asked for 4; so far 20 live, 53 cached, 20 API requests
  day 2 min 12: model asked for 4; so far 24 live, 53 cached, 24 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
  day 2 min 15: model asked for 4; so far 28 live, 53 cached, 29 API requests
  day 2 min 18: model asked for 4; so far 32 live, 53 cached, 33 API requests
  day 2 min 21: model asked for 4; so far 36 live, 53 cached, 37 API requests
  day 2 min 24: model asked for 3; so far 39 live, 53 cached, 40 API requests
  day 2 min 27: model asked for 4; so far 43 live, 53 cached, 44 API requests

wrote runs/v12/daniel_ate_it-seed2.md
  api_requests: 44
  answers_live: 43
  answers_from_cache: 53
  day1 api_requests: 0
  day1 answers_live: 0
  day1 answers_from_cache: 53
  day1 model_decisions: 53
  day1 fallbacks: 0
  day1 routine_decisions: 67
  day1 lines_spoken: 41
  day1 inner_moments: 6
  day1 lull_moments: 0
  day1 private_talks: 0
  day1 trip_minute: 30
  day1 trip_acts: 18
  day1 max_prompt_tokens_estimated: 1742
  day1 max_prompt_tokens_counted_by_api: 1709
  night_asks: 4
  night_api_requests: 4
  leavers: []
  outcome: []
  night house: 0; away: []
  day2 api_requests: 40
  day2 answers_live: 39
  day2 answers_from_cache: 0
  day2 model_decisions: 39
  day2 fallbacks: 0
  day2 routine_decisions: 81
  day2 lines_spoken: 38
  day2 inner_moments: 0
  day2 lull_moments: 0
  day2 private_talks: 0
  day2 trip_minute: 0
  day2 trip_acts: 24
  day2 max_prompt_tokens_estimated: 1948
  day2 max_prompt_tokens_counted_by_api: 1888
  day2_asks: 39
  day2_api_requests: 40
  max_prompt_tokens_estimated: 1948
  max_prompt_tokens_counted_by_api: 1888
  run_seconds: 1403.6
  story_sha256: a7be0ae7c3a1a050fa4455f46b9eff02854ae821f7ad1ecfca82c9c499d0069f
```

Seed 3:

```
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v12\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 51 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 3; so far 0 live, 11 cached, 0 API requests
  min 09: model asked for 3; so far 0 live, 14 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 15 cached, 0 API requests
  min 18: model asked for 1; so far 0 live, 16 cached, 0 API requests
  min 21: model asked for 4; so far 0 live, 20 cached, 0 API requests
  min 24: model asked for 3; so far 0 live, 23 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 24 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 25 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 26 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 27 cached, 0 API requests
  min 66: model asked for 4; so far 0 live, 31 cached, 0 API requests
  min 69: model asked for 4; so far 0 live, 35 cached, 0 API requests
  min 72: model asked for 3; so far 0 live, 38 cached, 0 API requests
  min 75: model asked for 3; so far 0 live, 41 cached, 0 API requests
  min 78: model asked for 3; so far 0 live, 44 cached, 0 API requests
  min 81: model asked for 1; so far 0 live, 45 cached, 0 API requests
  night: model asked for 4; so far 4 live, 45 cached, 4 API requests
  day 2 min 00: model asked for 4; so far 8 live, 45 cached, 8 API requests
  day 2 min 03: model asked for 4; so far 12 live, 45 cached, 12 API requests
  day 2 min 06: model asked for 3; so far 15 live, 45 cached, 15 API requests
  day 2 min 09: model asked for 3; so far 18 live, 45 cached, 18 API requests
  day 2 min 12: model asked for 4; so far 22 live, 45 cached, 22 API requests
  day 2 min 15: model asked for 3; so far 25 live, 45 cached, 25 API requests
  day 2 min 18: model asked for 4; so far 29 live, 45 cached, 29 API requests
  day 2 min 21: model asked for 4; so far 33 live, 45 cached, 33 API requests
  day 2 min 24: model asked for 3; so far 36 live, 45 cached, 36 API requests
  day 2 min 27: model asked for 4; so far 40 live, 45 cached, 40 API requests
  day 2 min 30: model asked for 4; so far 44 live, 45 cached, 44 API requests
  day 2 min 33: model asked for 4; so far 48 live, 45 cached, 48 API requests
  day 2 min 36: model asked for 4; so far 52 live, 45 cached, 52 API requests
  day 2 min 39: model asked for 1; so far 53 live, 45 cached, 53 API requests
  day 2 min 48: model asked for 1; so far 54 live, 45 cached, 54 API requests
  day 2 min 57: model asked for 1; so far 55 live, 45 cached, 55 API requests

wrote runs/v12/daniel_ate_it-seed3.md
  api_requests: 55
  answers_live: 55
  answers_from_cache: 45
  day1 api_requests: 0
  day1 answers_live: 0
  day1 answers_from_cache: 45
  day1 model_decisions: 45
  day1 fallbacks: 0
  day1 routine_decisions: 75
  day1 lines_spoken: 23
  day1 inner_moments: 5
  day1 lull_moments: 0
  day1 private_talks: 0
  day1 trip_minute: 30
  day1 trip_acts: 6
  day1 max_prompt_tokens_estimated: 1702
  day1 max_prompt_tokens_counted_by_api: 1653
  night_asks: 4
  night_api_requests: 4
  leavers: []
  outcome: []
  night house: 0; away: []
  day2 api_requests: 51
  day2 answers_live: 51
  day2 answers_from_cache: 0
  day2 model_decisions: 51
  day2 fallbacks: 0
  day2 routine_decisions: 69
  day2 lines_spoken: 43
  day2 inner_moments: 3
  day2 lull_moments: 0
  day2 private_talks: 0
  day2 trip_minute: 0
  day2 trip_acts: 29
  day2 max_prompt_tokens_estimated: 1938
  day2 max_prompt_tokens_counted_by_api: 1880
  day2_asks: 51
  day2_api_requests: 51
  max_prompt_tokens_estimated: 1938
  max_prompt_tokens_counted_by_api: 1880
  run_seconds: 244.1
  story_sha256: 6269ec980b121097d4820c4c7953b28ef543955cd2342b43a906b6206a98a69a
```
