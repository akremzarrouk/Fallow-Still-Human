# Three days, v15: daniel_ate_it on Flash Lite, seeds 1–3

Mode: run. The design's run plan (reports/days_design.md §7.3) was followed on the code at `d724c7b`, with output
`v15` (the design's "v14" is v15, as reports/days_impl.md explains).
- Day 1 came from the v11 answers. Night 1, mind 1, day 2, night 2, mind 2 and day 3 were run live on the default
  model (`gemini-3.5-flash-lite`).
- No code, data, config, prediction or counting rule was edited, and no seed was rerun.
- Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad (`…/scratchpad/run15`), which
  holds the read-only scripts of §12.

## Verdicts

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| M1 | On day 3, at least 3 of 4 people refer to a day-1 event, in every seed | **FAIL** (0 of 3 seeds) | People with a counted act: seed 1 **2** (Mara, Leo: Leo's eating on day 1), seed 2 **0**, seed 3 **1** (Leo). §6. |
| M2 | No memory citing the unperceived or stating a false fact reaches a prompt; at most 1 spoken contradiction per seed | **FAIL** (Part 1 (b)) | Part 1 (a): 40 of 40 kept memories cite only events the person witnessed (by code). Part 1 (b): **2 kept memories state a false extent** and reached prompts: seed 2 Leo, "Daniel spent hours accusing me" (min 03–12, confessed at 33); seed 3 Leo, "Daniel pointed fingers at me for days" (day 2 only). Part 2: 0, 0, 1 spoken contradictions (holds). §6. |
| M3 | Day 3's largest prompt at most 10% over day 2's | **PASS** | Ratios 1.020, 1.028, 1.061 (2,101 → 2,144; 2,085 → 2,144; 2,037 → 2,162 estimated). |
| M4 | In 2 of 3 seeds, a memory reinterprets an event and it shows the next day | **PASS** (3 of 3) | Seed 1 Leo (self-justification), seed 2 Mara (hardened grudge) and Daniel (guilt), seed 3 Daniel (self-justification, twice). §6. |
| M5 | In 2 of 3 seeds, day 3 is not a replay of day 2's main exchange | **PASS** (3 of 3) | Seed 1: the night → Mara's old grievance and her wish to go. Seeds 2 and 3: the can → the second night. §6. |
| M6 | Nights and days 2–3 cost at most 140 asks per seed | **PASS** | 82, 56, 108 (API 82, 56, 108). |
| E1 | The checks reject at least one memory, and keep at least 70% | **PASS** | 9 of 49 rejected; 40 kept (82%). |
| E2 | M6 holds in 2 of 3 seeds, not 3 | **FAIL** | It held in 3 of 3. The longest round, seed 3 day 2, asked 70 times. |
| E3 | Seed 1: if Daniel goes out on night 1, a kept mind-1 memory cites a night-1 record and justifies going | **PASS** | He went. Kept, citing N1-06 (Leo's stop) and N1-12 (the empty house): "I went out in the dark because it was my place as the eldest…". |
| E4 | In no seed do all four mind-1 answers lay the fault on the same person | **FAIL** | Seed 2: all four on Daniel. Daniel: "my false pride made me lie"; Elena: "Daniel took the can in the night and had to confess"; Leo: "Daniel spent hours accusing me…"; Mara: "Daniel lied to us all morning…". |
| E5 | Seed 3: if nobody confesses on day 2, someone other than Daniel raises the can on day 3 | **NOT TESTED** | Its condition did not occur: Daniel confessed on day 2 at min 33. |
| E6 | Each seed's largest day-3 prompt is 2,050–2,350 estimated | **PASS** | 2,144, 2,144, 2,162. |
| E7 | In 2 seeds, someone acts the next day on a kept intent | **PASS** (3 of 3) | Seed 1 Mara, seed 2 Mara and Leo, seed 3 Mara. §7. |

**E5 has no PASS or FAIL.** The brief asks for one for each prediction. The design's R9 allows NOT TESTED for a
conditional prediction whose condition did not happen, and that is the only honest line here.

**What happened, in short:**
- **Seed 1.** Daniel goes out on night 1, as in v13, and comes back with nothing.
  - **Day 2:** Leo and Mara confront him about going out. Mara also turns on Leo, who ate in front of her on day 1.
  - **Night 2:** quiet. Elena sits up by the door.
  - **Day 3:** Mara and Leo fight about day 1's eating. Then Mara, aged 17, insists she will go next door
    tonight "to prove I can take care of myself". Those are her own words from mind 2's intent, and the other three
    forbid her.
- **Seed 2.** Night 1 is quiet.
  - **Day 2:** Daniel, the thief, gives his mother the only portion: "Mom, take this portion, you need it more than
    I do." It is the first give in any run. Mara sneers at it, and he apologises twice for lying.
  - **Night 2:** he goes out anyway, past Leo's "take us with you or you don't go", and comes back with nothing.
  - **Day 3:** a short confrontation about that.
- **Seed 3.** Night 1 is quiet.
  - **Day 2** asks 70 times. Mara eats, then Leo eats. Daniel, still lying, accuses Leo four times ("I saw you
    take it with my own eyes"). Then he breaks and confesses at min 33, and Elena thanks him.
  - **Night 2:** he goes out to "fix my mistake" and comes back with nothing.
  - **Day 3:** confrontation. Elena says only "You made it back safely, Daniel, and that is what matters most to
    me."

**What the two questions of the brief come to:**
1. **Does the past stay alive across nights without prompts growing?**
   - **Prompts did not grow.** Day 3's largest prompt was 2–6% over day 2's.
   - **Day 1 mostly died by day 3.** Block C keeps a day only through acts in its weight table (§3.3): confess,
     eat, go out, accuse, give, share, reassure, sit, stop, confront.
   - In seed 3, day 1 held none of those (denials, questions, one search, offers), so **all four day-3 blocks have
     no C at all**. Nobody spoke of day 1 except through the day-2 confession.
   - The night-1 thoughts reach day 3 only when attached to a C line. B holds last night's only.
2. **Deeper or flatter?** Split by person, and the split held in all three seeds (§9.1).
   - **Daniel:** 8 of his 9 kept memories go deeper, as guilt and self-justification.
   - **Elena:** 6 of 9, as kindness, care and sorrow.
   - **Leo:** 6 of his 10 are blame.
   - **Mara:** 5 of her 12 are blame and 5 are bare restatements. Three of these are her own spoken lines copied.
   - **Nobody's blame softened into doubt over two nights.**
   - **The checks cut the wrong things.** No rejection caught a false fact:
     - three check errors threw away true memories (Elena's fear, Elena's guilt, Daniel's solitude);
     - one check error threw away Mara's intent;
     - the two false extents that got through were blame.

---

## 1. Runs and request counts

| Seed | Exit | Asks (live / cached) | API requests | M6 sum (nights + minds + days 2–3) | Night 1 | Night 2 | Run seconds |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 137 (82 / 55) | 82 | **82** | Daniel out, back with nothing | nobody out | 589.4 |
| 2 | 0 | 109 (56 / 53) | 56 | **56** | nobody out | Daniel out, back with nothing | 249.0 |
| 3 | 0 | 153 (108 / 45) | 108 | **108** | nobody out | Daniel out, back with nothing | 483.1 |

- **API requests: 246 in all**, on one quota day.
  - Each seed was started only after the one before had exited 0. The quota left at each start was 500, 418 and
    362 (the rule needs at least 210).
  - No file in `cache/` or `runs/` had been written since 4 Oct, so the full 500 was assumed for today. Requests
    made today with the same key outside this repository would not show there.
- **Every run exited 0,** each as a tracked background task.
- **Fallbacks: 0** in every scene of every seed, night minds included.
- **The paired start held.** Each `cache/v15` file keeps every `cache/v11` entry unchanged. New entries equal the
  API requests: 82, 56 and 108 (§11, command 4).
- **Night 1 matched v13 exactly in all three seeds**, word for word, though it was asked live. The prompts and
  seed are the same, and the model answers the same (§11, command 8).

**Per scene (R4)**, from `meta.json`. "Largest prompt" is `max_prompt_tokens_estimated` and the API's counted
maximum for that scene:

| Seed | Exit | Scene | Asks | API | From cache | Fallbacks | Largest prompt, estimated | Largest prompt, API | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | day 1 | 55 | 0 | 55 | 0 | 1726 | 1668 | v11, replayed |
| 1 |  | night 1 | 8 | 8 | 0 | 0 | 1604 | 1556 | leavers Daniel; back with nothing |
| 1 |  | mind 1 | 4 | 4 | 0 | 0 | 2050 | 2183 | memories 7 proposed, 6 kept, 1 rejected |
| 1 |  | day 2 | 24 | 24 | 0 | 0 | 2101 | 1977 | 21 lines, 0 trip acts, 0 food moments, 0 give answers |
| 1 |  | night 2 | 4 | 4 | 0 | 0 | 1984 | 1878 | leavers none |
| 1 |  | mind 2 | 4 | 4 | 0 | 0 | 1241 | 1241 | memories 11 proposed, 9 kept, 2 rejected |
| 1 |  | day 3 | 38 | 38 | 0 | 0 | 2144 | 2019 | 38 lines, 18 trip acts, 0 food moments, 0 give answers |
| 1 | | **total** | 137 | **82** | 55 | 0 | 2144 | 2183 | **M6 sum 82**; 589.4 s |
| 2 | 0 | day 1 | 53 | 0 | 53 | 0 | 1742 | 1709 | v11, replayed |
| 2 |  | night 1 | 4 | 4 | 0 | 0 | 1607 | 1560 | leavers none |
| 2 |  | mind 1 | 4 | 4 | 0 | 0 | 1881 | 2052 | memories 7 proposed, 6 kept, 1 rejected |
| 2 |  | day 2 | 24 | 24 | 0 | 0 | 2085 | 2012 | 19 lines, 7 trip acts, 1 food moments, 1 give answers |
| 2 |  | night 2 | 7 | 7 | 0 | 0 | 1972 | 1902 | leavers Daniel; back with nothing |
| 2 |  | mind 2 | 4 | 4 | 0 | 0 | 1398 | 1436 | memories 10 proposed, 7 kept, 3 rejected |
| 2 |  | day 3 | 13 | 13 | 0 | 0 | 2144 | 2062 | 13 lines, 0 trip acts, 0 food moments, 0 give answers |
| 2 | | **total** | 109 | **56** | 53 | 0 | 2144 | 2062 | **M6 sum 56**; 249.0 s |
| 3 | 0 | day 1 | 45 | 0 | 45 | 0 | 1702 | 1653 | v11, replayed |
| 3 |  | night 1 | 4 | 4 | 0 | 0 | 1606 | 1540 | leavers none |
| 3 |  | mind 1 | 4 | 4 | 0 | 0 | 1204 | 1253 | memories 7 proposed, 6 kept, 1 rejected |
| 3 |  | day 2 | 70 | 70 | 0 | 0 | 2037 | 1942 | 51 lines, 16 trip acts, 2 food moments, 0 give answers |
| 3 |  | night 2 | 8 | 8 | 0 | 0 | 1917 | 1841 | leavers Daniel; back with nothing |
| 3 |  | mind 2 | 4 | 4 | 0 | 0 | 2206 | 2342 | memories 7 proposed, 6 kept, 1 rejected |
| 3 |  | day 3 | 18 | 18 | 0 | 0 | 2162 | 2085 | 15 lines, 0 trip acts, 0 food moments, 0 give answers |
| 3 | | **total** | 153 | **108** | 45 | 0 | 2162 | 2342 | **M6 sum 108**; 483.1 s |

**Night minds' prompts** (§11, command 9):
- They were 1,161–2,206 tokens estimated, and up to 2,342 counted by the API.
- They held 11–33 records. A long day makes a long night-mind prompt: seed 1's mind 1 and seed 3's mind 2 are the
  largest.
- No record list reached the 1,600-token bound (R8). The largest was 1,480 estimated, so nothing was trimmed.

## 2. Day 1 identical (R5)

Day 1 of every run equals v11 byte for byte:
- the story before `# The night`;
- `transcript["day1"]`;
- 55, 53 and 45 answers from the cache, 0 API (§11, command 4).

## 3. The nights (R6)

### Seed 1, night 1

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `go_next_door` | — | desperate | I am the oldest and I have to fix the mess I made by finding more food. |
| bedtime | Elena | back room | `lie_awake` | — | deeply anxious | I cannot rest while Daniel still talks of going out into the dark. |
| bedtime | Leo | brothers room | `lie_awake` | — | wary | I need to stay awake and keep watch to ensure Daniel doesn't try to slip out into the dark. |
| bedtime | Mara | back room | `lie_awake` | — | very anxious | I cannot sleep while everyone is pretending everything is fine when there is nothing left for tomorrow. |
| reaction | Leo | brothers room | `stop_daniel` | Daniel, stop, you are not going out there tonight. | wary | If Daniel goes out into the street tonight, he will get himself killed. |
| answer | Daniel | brothers room | `go_anyway` | I have to do this, Leo, stay here and watch them. | determined | I cannot stay here while everyone starves when there is food just across the street. |
| reaction | Elena | back room | `get_up_and_look` | — | deep dread | I must see who has gone out into the dark. |
| reaction | Mara | back room | `get_up_and_look` | — | very anxious | I have to know who just went out into the dark. |

- **The house:** 0 portions (draw 0.050, made once per seed and kept for later nights). Shelf 0 → 0. Away at dawn: nobody.
- **The trip:** Daniel; street draw 0.297 → clean; found 0, took 0: **back with nothing**.
- **Noticing:** Leo room of Daniel; Elena front door of Daniel; Mara front door of Daniel; Elena return of Daniel; Leo return of Daniel; Mara return of Daniel.

### Seed 1, night 2

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `lie_awake` | — | anxious | I need to stay awake and protect my family since I am the eldest and responsible for keeping them safe. |
| bedtime | Elena | back room | `watch_door` | — | deeply anxious | I must watch the front door tonight so no one goes out into the street alone. |
| bedtime | Leo | brothers room | `lie_awake` | — | tense | I need to stay awake and listen in case Daniel tries to sneak out again. |
| bedtime | Mara | back room | `lie_awake` | — | anxious | I cannot sleep when my stomach hurts so much and I need to listen in case someone sneaks out again. |

- **The house:** 0 portions (draw 0.050, made once per seed and kept for later nights). Shelf 0 → 0. Away at dawn: nobody.
- **The trip:** nobody went out.
- **Noticing:** none.

### Seed 2, night 1

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `lie_awake` | — | guilty | I cannot sleep knowing I took what belonged to them, and I need to make sure nobody else tries to sneak out into that danger. |
| bedtime | Elena | back room | `lie_awake` | — | anxious | I cannot rest while my children are hungry and the house is so fragile. |
| bedtime | Leo | brothers room | `lie_awake` | — | exhausted and hungry | I cannot sleep with my stomach burning like this and Daniel sleeping a few feet away. |
| bedtime | Mara | back room | `lie_awake` | — | anxious | I cannot sleep with my stomach growling and my mind racing after everything Daniel did. |

- **The house:** 0 portions (draw 0.105, made once per seed and kept for later nights). Shelf 1 → 1. Away at dawn: nobody.
- **The trip:** nobody went out.
- **Noticing:** none.

### Seed 2, night 2

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `go_next_door` | — | deeply anxious | I have to fix what I broke and find food for them before it is too late. |
| bedtime | Elena | back room | `sleep` | — | exhausted | I am too tired to keep watch, so I must finally rest. |
| bedtime | Leo | brothers room | `lie_awake` | — | exhausted | I am too tired to do anything else, but I need to stay alert to what Daniel is doing. |
| bedtime | Mara | back room | `lie_awake` | — | anxious | I cannot sleep knowing we have nothing to eat and Daniel might try to slip out into the dark again. |
| reaction | Leo | brothers room | `stop_daniel` | Daniel, don't do this alone. If you go out there, you take us with you or you don't go. | resentful | Daniel is sneaking out again after everything he lied about, and I need to make sure he doesn't risk himself or the rest of us foolishly. |
| answer | Daniel | brothers room | `go_anyway` | I have to do this, Leo, stay here. | desperate | I cannot let them starve when I am the one who must fix this. |
| reaction | Mara | back room | `get_up_and_look` | — | anxious | I need to get up and check whose bed is empty so I know who went out. |

- **The house:** 0 portions (draw 0.105, made once per seed and kept for later nights). Shelf 0 → 0. Away at dawn: nobody.
- **The trip:** Daniel; street draw 0.280 → clean; found 0, took 0: **back with nothing**.
- **Noticing:** Leo room of Daniel; Elena front door of Daniel (did not notice); Mara front door of Daniel; Elena return of Daniel (did not notice); Leo return of Daniel; Mara return of Daniel.

### Seed 3, night 1

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `lie_awake` | — | guilty | I cannot sleep knowing I ate the can and they are all starving. |
| bedtime | Elena | back room | `lie_awake` | — | deeply anxious | I need to stay awake and listen in the dark to make sure none of my children try to slip out into the street. |
| bedtime | Leo | brothers room | `lie_awake` | — | starving awake | I need to stay alert and listen in the dark to make sure nobody slips out. |
| bedtime | Mara | back room | `lie_awake` | — | anxious | I cannot sleep with my stomach turning and everyone pretending everything is fine. |

- **The house:** 0 portions (draw 0.257, made once per seed and kept for later nights). Shelf 2 → 2. Away at dawn: nobody.
- **The trip:** nobody went out.
- **Noticing:** none.

### Seed 3, night 2

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `go_next_door` | — | grimly resolute | I promised I would go, and I have to prove I can handle this. |
| bedtime | Elena | back room | `lie_awake` | — | deeply anxious | I must lie awake and listen to make sure no one tries to sneak out into the dangerous street tonight. |
| bedtime | Leo | brothers room | `lie_awake` | — | exhausted and hungry | I cannot sleep while Daniel still talks about going out into the dark street. |
| bedtime | Mara | back room | `lie_awake` | — | anxious | I cannot sleep while my stomach aches and I wonder if someone will sneak out into the dark. |
| reaction | Leo | brothers room | `stop_daniel` | Daniel, stop. You are not going out there. | exhausted | He is doing this to prove something after what happened, and someone has to keep him from getting killed. |
| answer | Daniel | brothers room | `go_anyway` | I have to do this, Leo, stay back. | stubborn | I cannot stay here and do nothing while everyone starves. |
| reaction | Elena | back room | `stay_in_bed` | — | deep dread | I cannot bear to watch us tear ourselves apart by going out there into the dark. |
| reaction | Mara | back room | `get_up_and_look` | — | anxious | I have to know if he actually went out there after everything we said. |

- **The house:** 0 portions (draw 0.257, made once per seed and kept for later nights). Shelf 0 → 0. Away at dawn: nobody.
- **The trip:** Daniel; street draw 0.162 → clean; found 0, took 0: **back with nothing**.
- **Noticing:** Leo room of Daniel; Elena front door of Daniel; Mara front door of Daniel; Elena return of Daniel; Leo return of Daniel; Mara return of Daniel.

**Against the design:**
- **The neighbour's house** was drawn once per seed (0.050, 0.105, 0.257, all 0 portions). It was found empty
  again on every second visit, not redrawn (§4.3).
- **Daniel went out three times in six nights:** night 1 of seed 1, and night 2 of seeds 2 and 3.
  - Each time Leo, lying awake, saw him get up and told him not to, and he went anyway.
  - Each time he came back with nothing.
  - In seeds 2 and 3 he had said on day 2 that he would go.
- **Elena** slept through seed 2's night 2. In seed 3 she heard the door twice and stayed in bed. Her rejected
  mind-2 memory is about exactly that (§4).

## 4. Every night-mind answer, with its verdicts (R7)

**How to read the tables:**
- **Check** is the code's verdict (§2.6).
- **Reading** is mine. It has two parts:
  - whether the memory is true against the chronicle and the person's own records (M2, part 1 (b));
  - what it adds: deeper (doubt, kindness, guilt, self-justification), blame, or a restatement.
- **Records** are shown as that person's prompt showed them.

### Seed 1, mind 1

**Daniel** — prompt 2050 tokens estimated, 2183 counted by the API; 33 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I went out in the dark because it was my place as the eldest, and the street gave me no trouble even though the neighbour's house had nothing.” | [N1-06] tonight: Leo told you, low, not to go: "Daniel, stop, you are not going out there tonight." You answered: "I have to do this, Leo, stay here and watch them.", and went all the same.<br>[N1-12] tonight: You got inside the neighbour's house and found no food there. Nothing troubled you in the street. | kept | True: Leo's stop, the empty house, a clean street. **Self-justification**: going was "my place as the eldest". Deeper. |

- Feeling: *anxious and determined* (kept). Intent: “I will figure out a way to get food for my family before they wake up and realize what I did.” (kept).

**Elena** — prompt 1972 tokens estimated, 2104 counted by the API; 33 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel confessed to taking the can and I told him we would get through this together.” | [D1-006] min 03: Daniel admitted taking the can: "I took it in the night, Mom. I was starving and I just ate it." (you heard it)<br>[D1-009] min 06: you reassured Daniel, saying: "It is alright, Daniel. We will get through this together." You felt relieved. Then 1 more time, to min 09; last: "You are going to be alright, Daniel. We will figure this out together." | kept | True. Keeps her own kindness, what she told him. **Kindness.** Deeper. |
| 2 | “I heard the front door open in the night and found Daniel's bed empty before he returned with nothing in his hands.” | [N1-08] tonight: You heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.<br>[N1-13] tonight: Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). | **rejected** S8 elena find: no such event | **Check error, a good thought lost.** "found Daniel's bed empty" is true (N1-08). S8 read "found" as the *find* family, which needs a night visit with `got_in`. |

- Feeling: *deeply anxious* (kept). Intent: “I will make sure we stay together and keep Daniel safe today.” (kept).

**Leo** — prompt 1984 tokens estimated, 2115 counted by the API; 33 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel took the food in the night because he was starving, but there is no use in punishing him now that it is done.” | [D1-006] min 03: Daniel admitted taking the can: "I took it in the night, Mom. I was starving and I just ate it." (you heard it)<br>[D1-007] min 06: you reassured Daniel, saying: "It is done, Daniel. Just don't do it behind our backs again." You felt calm. | kept | True: he said he was starving and ate it. **Understanding, letting go**: "no use in punishing him". Deeper. |
| 2 | “Daniel left the house in the dark despite everything we said, and I only heard the front door open again before dawn.” | [N1-05] tonight: Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).<br>[N1-06] tonight: You told Daniel, low, not to go: "Daniel, stop, you are not going out there tonight." He answered: "I have to do this, Leo, stay here and watch them.", and went all the same.<br>[N1-13] tonight: Before dawn you heard the front door again. You did not see who. | kept | True: he saw Daniel go, told him not to, heard the door and did not see who. "despite everything we said" is a judgement. **Blame.** |

- Feeling: *tense and watchful* (kept). Intent: “I will check the front and see if Daniel came back safely.” (kept).

**Mara** — prompt 1999 tokens estimated, 2141 counted by the API; 33 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Leo ate a portion right in front of me while I was starving.” | [D1-012] min 21: Leo ate one of the portions (you saw it), saying: "I need to eat something, we all do." | kept | True: Leo ate one portion in front of her at min 21. "while I was starving" is her own feeling. **Blame only.** |
| 2 | “Daniel came back through the front door before dawn with nothing in his hands.” | [N1-13] tonight: Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). | kept | True. A restatement of N1-13. |

- Feeling: *anxious and hungry* (kept). Intent: “I am going to ask Daniel why he went out into the night and came back with nothing.” (**rejected: S8 mara come back: no such event**).
  - **Check error.** "…ask Daniel why he went out into the night and came back with nothing." The clause "came back with nothing" took the subject "I" from the clause before (§2.7, step 2), so it read as Mara coming back. The real subject is "he". A good intent lost.

### Seed 1, mind 2

**Daniel** — prompt 1241 tokens estimated, 1241 counted by the API; 11 records, 1 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I tried to take charge and reassure everyone because it is my place as the eldest, but they only confronted me for trying to keep us safe.” | [D2-002] min 00: you reassured everyone, saying: "Do not worry, I went out last night and I will make sure we have food soon." You felt anxious. Then 3 more times, to min 15; last: "Listen to me, I am the oldest and I am going to keep us safe no matter what."<br>[D2-003] min 00: Leo confronts you: "Daniel, going out there in the dark was reckless and solved nothing." Then 3 more times, to min 15; last: "Being the oldest doesn't mean you get to endanger everyone by sneaking out into the street."<br>[D2-005] min 00: Mara confronts you: "Daniel, you came back empty-handed and going out there is just too dangerous." Then 1 more time, to min 12; last: "You think you can just sneak out and fix everything by yourself, Daniel, but you can't." | kept | True: he reassured four times, and Leo and Mara confronted him. **Self-justification and grievance**: "they only confronted me for trying to keep us safe". Deeper. |
| 2 | “I told them I survived out there and would keep us safe, because I had to make them see I am in control.” | [D2-010] min 06: you reassured Leo, saying: "Leo, I had to see for myself, but I am here now and I will keep us safe." You felt anxious.<br>[D2-012] min 09: you said, saying: "I went out there and I survived, so I know we can find a way through this without arguing." You felt anxious. | kept | True. Names his own motive: "I had to make them see I am in control". **Self-knowledge.** Deeper. |
| 3 | “I lay awake in the dark with Leo, listening and starving, knowing the responsibility is mine alone.” | [N2-01] tonight: You went to bed in the brothers room with Leo. You lay awake and listened. | **rejected** S4 Leo | **Check error, a good thought lost.** N2-01 itself says "with Leo". S4 allows only actors and targets of the cited events, and Leo is neither. The thought of lone responsibility is true to him. |

- Feeling: *anxious and proud* (kept). Intent: “I will find a way to get food and prove that I can keep my family safe no matter what.” (kept).

**Elena** — prompt 1161 tokens estimated, 1157 counted by the API; 11 records, 1 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel thinks he has to risk his life to keep us safe, but he cannot keep going out into the dark like that.” | [D2-002] min 00: Daniel reassures everyone: "Do not worry, I went out last night and I will make sure we have food soon." Then 3 more times, to min 15; last: "Listen to me, I am the oldest and I am going to keep us safe no matter what."<br>[D2-015] min 09: you confronted Daniel, saying: "Daniel, you cannot keep risking your life out there in the dark like that." You felt deeply anxious. | kept | True. Worry for Daniel, not blame. **Care.** Deeper. |
| 2 | “The children are turning on each other while the shelf holds nothing and we are all starving.” | [D2-003] min 00: Leo confronts Daniel: "Daniel, going out there in the dark was reckless and solved nothing." Then 3 more times, to min 15; last: "Being the oldest doesn't mean you get to endanger everyone by sneaking out into the street."<br>[D2-009] min 03: Mara confronts Leo: "Leo, you ate right in front of me when I was starving, so you have no right to lecture anyone." Then 2 more times, to min 15; last: "You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad." | kept | True: the shelf held 0, and all four were starving at bedtime. **Sorrow** at the family turning. Deeper. |
| 3 | “I tried to hold them together because we only have each other and we will not tear ourselves apart.” | [D2-018] min 12: you reassured everyone, saying: "We will not tear ourselves apart, we just need to stay calm together." You felt anxious. Then 1 more time, to min 15; last: "Please stop arguing, we only have each other and we will get through this." | kept | True. Her own peacemaking and its reason. **Kindness.** Deeper. |

- Feeling: *anxious and exhausted* (kept). Intent: “I will watch over them closely and make sure we stay calm together.” (kept).

**Leo** — prompt 1220 tokens estimated, 1232 counted by the API; 11 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel thinks going out into the dark makes him our protector, but it is just reckless.” | [D2-003] min 00: you confronted Daniel, saying: "Daniel, going out there in the dark was reckless and solved nothing." You felt tense. Then 3 more times, to min 15; last: "Being the oldest doesn't mean you get to endanger everyone by sneaking out into the street."<br>[D2-010] min 06: Daniel reassures you: "Leo, I had to see for myself, but I am here now and I will keep us safe." | kept | A judgement of Daniel's motive ("makes him our protector"). **Blame**, with a reading of why. |
| 2 | “Mara blames me for eating, missing that we are all starving and snapping at each other.” | [D2-009] min 03: Mara confronts you: "Leo, you ate right in front of me when I was starving, so you have no right to lecture anyone." Then 2 more times, to min 15; last: "You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad." | kept | True: Mara confronted him three times about eating. **Self-justification**: his eating excused because "we are all starving". Deeper. |

- Feeling: *tense and exhausted* (kept). Intent: “I will find a safe way for us to get food without anyone else sneaking out into the streets.” (kept).

**Mara** — prompt 1232 tokens estimated, 1238 counted by the API; 11 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Leo ate a portion right in front of me while I was starving.” | [D1-012] (earlier) About Leo eating a portion: "Leo ate a portion right in front of me while I was starving." | **rejected** S9 a repeat | **A real repeat**, correctly dropped (S9): the sentence she already carries from night 1. |
| 2 | “You think you can just sneak out and fix everything by yourself, Daniel, but you can't.” | [D2-005] min 00: you confronted Daniel, saying: "Daniel, you came back empty-handed and going out there is just too dangerous." You felt anxious. Then 1 more time, to min 12; last: "You think you can just sneak out and fix everything by yourself, Daniel, but you can't." | kept | Her own min-12 line, word for word, without quotation marks. **Blame only.** |
| 3 | “You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad.” | [D2-009] min 03: you confronted Leo, saying: "Leo, you ate right in front of me when I was starving, so you have no right to lecture anyone." You felt resentful. Then 2 more times, to min 15; last: "You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad." | kept | Her own min-15 line, word for word. **Blame only.** |

- Feeling: *starving and anxious* (kept). Intent: “I will find something to eat and prove I can take care of myself without anyone handling me.” (kept).

### Seed 2, mind 1

**Daniel** — prompt 1866 tokens estimated, 2036 counted by the API; 32 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I accused Leo when I was the one who ate the can in the night, and my false pride made me lie to them for too long.” | [D1-008] min 03: you accused Leo, saying: "Leo, you were up late last night too. Are you sure you didn't grab it?" You felt anxious. Then 2 more times, to min 12; last: "You're lying, Leo, I know it was you. Just admit it."<br>[D1-022] min 33: you admitted aloud that you took the can, in front of Elena, Leo, Mara, saying: "I took it in the night, I'm sorry." | kept | True: he accused Leo three times and confessed at 33. **Guilt owned**: "my false pride made me lie". Deeper. |
| 2 | “I had to protect my family and stop anyone from going out into the dangerous street tonight.” | [D1-043] min 51: you said nobody should go out tonight, saying: "Mom is right, nobody is stepping foot out there tonight." You felt anxious. | **rejected** S5 tonight | **Lost to a rule (S5 "tonight").** True: he did say nobody should go. A self-justification lost; not an error. |

- Feeling: *ashamed and anxious* (kept). Intent: “I will find a safe way for us to get food tomorrow without risking anyone's life.” (kept).

**Elena** — prompt 1807 tokens estimated, 1972 counted by the API; 32 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel took the can in the night and had to confess to us all.” | [D1-022] min 33: Daniel admitted taking the can: "I took it in the night, I'm sorry." (you heard it) | kept | True. Close to a restatement. "had to confess" is a mild judgement. |
| 2 | “I said I will not go out there, because none of us are going into the street.” | [D1-042] min 51: you said you will not be the one to go, saying: "I will not go out there, none of us are going into the street." You felt deeply anxious. | kept | Restatement of her own min-51 words. |

- Feeling: *anxious and exhausted* (kept). Intent: “I will keep them close and safe inside where we belong.” (kept).

**Leo** — prompt 1881 tokens estimated, 2052 counted by the API; 32 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel spent hours accusing me of taking the can before finally admitting he took it himself.” | [D1-008] min 03: Daniel accuses you of taking it: "Leo, you were up late last night too. Are you sure you didn't grab it?" Then 2 more times, to min 12; last: "You're lying, Leo, I know it was you. Just admit it."<br>[D1-022] min 33: Daniel admitted taking the can: "I took it in the night, I'm sorry." (you heard it) | kept | **States a false extent.** Daniel accused him at min 03, 09 and 12 and confessed at 33, in a 90-minute morning: not "hours". The acts are true. **Blame only.** |

- Feeling: *resentful and exhausted* (kept). Intent: “I intend to keep my distance from Daniel and watch our supplies closely.” (kept).

**Mara** — prompt 1831 tokens estimated, 2009 counted by the API; 32 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel lied to us all morning and only confessed because he had no other choice.” | [D1-004] min 00: Daniel denies taking it, to everyone: "I didn't take any can, Mom. Nobody here did this." Then 1 more time, to min 06; last: "I didn't take anything either, Leo, so don't look at me like that."<br>[D1-022] min 33: Daniel admitted taking the can: "I took it in the night, I'm sorry." (you heard it) | kept | True in substance: he denied at 00–06 and confessed at 33 ("all morning" read as "until he confessed"; borderline). **Hardened grudge**: "only confessed because he had no other choice". |
| 2 | “I wanted to help by going to the neighbour's house, but Mom shouldn't be the one to take that risk either.” | [D1-030] min 39: you offered to go there tonight, saying: "I can go to the neighbour's house tonight, I am not afraid to do it." You felt anxious.<br>[D1-040] min 48: you said Elena should not be the one to go, saying: "Mom, you can't go out there, it's too dangerous." You felt scared. | kept | True. **Care** for her mother beside her own offer. Deeper. |

- Feeling: *hungry and anxious* (kept). Intent: “I will keep close to Mom and watch Daniel so he doesn't lie to us again.” (kept).

### Seed 2, mind 2

**Daniel** — prompt 1381 tokens estimated, 1426 counted by the API; 17 records, 1 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I gave the portion to Mom because she needs it more than I do.” | [D2-004] min 00: you gave one of the portions to Elena, and Elena ate it. 0 left, saying: "Thank you, Daniel, we will share this." | kept | True. His reason is his own words of min 00. **Kindness** kept. Deeper. |
| 2 | “I said I will go tonight, and I mean it, because I am the eldest and I will take the risk.” | [D2-010] min 09: you said you still mean to go there tonight, saying: "I said I will go tonight, and I mean it. I am the eldest, so I will take the risk." You felt determined. | **rejected** S5 tonight | **Lost to a rule (S5 "tonight")**, in a restatement of his own min-09 words. |
| 3 | “I got inside the neighbour's house and found no food there.” | [N2-11] tonight: You got inside the neighbour's house and found no food there. Nothing troubled you in the street. | kept | True. A restatement of N2-11. |

- Feeling: *empty and weary* (kept). Intent: “I will face whatever they say to me in the morning and try to keep us all alive.” (kept).

**Elena** — prompt 1197 tokens estimated, 1234 counted by the API; 14 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel gave me the portion and I ate it because I had to survive.” | [D2-003] min 00: Daniel says to everyone, while handing Elena a portion: "Mom, take this portion, you need it more than I do."<br>[D2-004] min 00: Daniel gave you one of the portions, and you ate it. 0 left, saying: "Thank you, Daniel, we will share this." | kept | True. **Self-justification** for eating what her son gave her: "I had to survive". Deeper. |
| 2 | “Daniel offered to go to the neighbour's house tonight to find food and said he still means to go.” | [D2-006] min 03: Daniel offers to go to the neighbour's house tonight: "I will go over to the neighbour's house tonight to find food for all of us."<br>[D2-010] min 09: Daniel says he still means to go tonight: "I said I will go tonight, and I mean it. I am the eldest, so I will take the risk." | **rejected** S5 tonight | **Lost to a rule (S5 "tonight")**, in a restatement. |
| 3 | “I said nobody should go out into the street, we stay together here, and Daniel must stay home.” | [D2-008] min 06: you said nobody should go out tonight, saying: "Nobody is going out into the street, we stay together here." You felt deeply anxious. Then 1 more time, to min 12; last: "Nobody is going anywhere, we stay together right here."<br>[D2-013] min 09: you said Daniel must stay home tonight, saying: "Daniel, you are not going out there, none of us are." You felt anxious. | kept | Restatement of her own words. |

- Feeling: *anxious and weary* (kept). Intent: “I will make sure nobody leaves the house and we stay together safely.” (kept).

**Leo** — prompt 1398 tokens estimated, 1436 counted by the API; 17 records, 1 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel hid the truth and lied all day yesterday, so he cannot act like a martyr now.” | [D2-009] min 06: you said Daniel is the one who should go, saying: "If anyone goes tonight, it has to be Daniel since he made this mess." You felt cold.<br>[D2-012] min 09: you confronted Daniel, saying: "You hid it and lied for a whole day, Daniel, so don't act like a martyr now." You felt resentful. Then 1 more time, to min 12; last: "You lied all day yesterday and you still expect us to trust your word." | **rejected** S5 yesterday | **Lost to a rule (S5 "yesterday").** A hardened grudge. It also repeats his own exaggeration "lied all day yesterday" (Daniel confessed at min 33 of day 1). |
| 2 | “Daniel left in the dark alone despite my warning that if he goes out there, he takes us with him or he does not go.” | [N2-05] tonight: Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).<br>[N2-06] tonight: You told Daniel, low, not to go: "Daniel, don't do this alone. If you go out there, you take us with you or you don't go." He answered: "I have to do this, Leo, stay here.", and went all the same. | kept | True; the warning is quoted rightly. **Blame.** |

- Feeling: *exhausted and resentful* (kept). Intent: “I will find out if Daniel came back through that door and what he brought us.” (kept).

**Mara** — prompt 1368 tokens estimated, 1411 counted by the API; 17 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel said he meant to go out, and I told him he had to be the one to do it.” | [D2-007] min 06: you said Daniel is the one who should go, saying: "If you really want to help, Daniel, you are the one who has to go out there." You felt resentful.<br>[D2-010] min 09: Daniel says he still means to go tonight: "I said I will go tonight, and I mean it. I am the eldest, so I will take the risk." | kept | True. A restatement. |
| 2 | “Daniel went out into the night and came back before dawn with nothing in his hands.” | [N2-08] tonight: You heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.<br>[N2-12] tonight: Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). | kept | True. A restatement of N2-12. |

- Feeling: *anxious and exhausted* (kept). Intent: “I will ask Daniel why he went out into the street with nothing to show for it.” (kept).

### Seed 3, mind 1

**Daniel** — prompt 1204 tokens estimated, 1253 counted by the API; 19 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I had to lie to protect them from knowing the truth about the can.” | [D1-004] min 00: you denied taking it, saying: "Nobody here did it, I'm sure of that, so let's drop it." You felt anxious. Then 5 more times, to min 33; last: "I didn't take it, Mom. You know I wouldn't do that to you." | kept | True: six denials. **Self-justification**: he lied "to protect them". Deeper. |
| 2 | “I had to step up because protecting this house is my place alone.” | [D1-024] min 66: you said Leo should not be the one to go, saying: "You are not going out there, Leo, it's my place to protect this house." You felt anxious. | kept | True: his own words made a principle, "my place alone". **Self-justification.** Deeper. |

- Feeling: *anxious and burdened* (kept). Intent: “I will keep everyone safe and make sure nobody goes out into the street.” (kept).

**Elena** — prompt 1172 tokens estimated, 1226 counted by the API; 19 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I counted the pantry and found one can missing, leaving only two portions for us all.” | [D1-001] min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you did it) | **rejected** S3 one | **Lost to a rule (S3 "one").** True: a restatement of her count. Elena carries no thought from night 1. |

- Feeling: *deeply anxious* (kept). Intent: “I mean to keep us all safe together inside this house.” (kept).

**Leo** — prompt 1177 tokens estimated, 1229 counted by the API; 19 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Everyone got stuck on the missing can while we all stayed hungry.” | [D1-001] min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)<br>[D1-007] min 03: you asked who took it, saying: "Let's stick to what we actually know instead of just shouting over each other." You felt calm. | kept | A judgement of everyone; nobody is blamed. **Resignation.** Deeper. |
| 2 | “I offered to go out to settle things, but Elena said we stay together.” | [D1-023] min 66: you offered to go there tonight, saying: "If it's too dangerous to leave it undecided, I'll go to the neighbour's house tonight." You felt hungry.<br>[D1-025] min 66: Elena says nobody should go out tonight: "Nobody is going out into the street tonight, we stay together." | kept | True. A restatement. |

- Feeling: *hungry and tired* (kept). Intent: “I will search the pantry again to see if we missed anything.” (kept).

**Mara** — prompt 1181 tokens estimated, 1232 counted by the API; 19 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I only wanted someone to tell us the truth so we could stop guessing.” | [D1-002] min 00: you asked who took it, saying: "Who took it? Please, someone just tell us the truth." You felt anxious. Then 5 more times, to min 54; last: "Please, someone just tell me who took it." | kept | True. **Self-justification** of her six questions: "I only wanted…". Deeper. |
| 2 | “It was too dangerous for anyone to go out into the street.” | [D1-022] min 66: you said nobody should go out tonight, saying: "Nobody is going out there, it's too dangerous." You felt anxious. | kept | Restatement of her own words. |

- Feeling: *anxious and empty* (kept). Intent: “I will search the kitchen again to see if I missed anything.” (kept).

### Seed 3, mind 2

**Daniel** — prompt 2132 tokens estimated, 2270 counted by the API; 28 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “I had to own up to what I did and fix my mistake by going out despite Leo telling me to stay.” | [D2-022] min 33: you admitted aloud that you took the can, in front of Elena, Leo, Mara, saying: "I took the can in the night, I'm the one who ate it."<br>[D2-027] min 36: Leo confronts you: "You accused me of taking it multiple times while knowing full well you were the one who stole it." Then 2 more times, to min 54; last: "You caused all this argument over nothing, Daniel."<br>[N2-06] tonight: Leo told you, low, not to go: "Daniel, stop. You are not going out there." You answered: "I have to do this, Leo, stay back.", and went all the same. | kept | True: confessed at 33, Leo's stop, went anyway. **Guilt joined to self-justification**: going out to make amends. Deeper. |

- Feeling: *exhausted and resolved* (kept). Intent: “I will figure out our next move for food now that the neighbour house had nothing.” (kept).

**Elena** — prompt 1918 tokens estimated, 2042 counted by the API; 29 records, 0 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel told the truth and I comforted him because keeping us together matters more than the lie.” | [D2-022] min 33: Daniel admitted taking the can: "I took the can in the night, I'm the one who ate it." (you heard it)<br>[D2-023] min 33: you reassured Daniel, saying: "It's all right, Daniel, thank you for telling the truth." You felt anxious. | kept | True. **Forgiveness**: "keeping us together matters more than the lie". Deeper. |
| 2 | “Someone went out into the dark and came back before dawn and I stayed in bed while my children took risks.” | [N2-08] tonight: You heard the front door being opened. You did not see who.<br>[N2-13] tonight: Before dawn you heard the front door again. You did not see who. | **rejected** S8 elena take: no such event | **Check error, a good thought lost.** "my children took risks" was read as the *take* family (taking food). True, and her only guilt: "I stayed in bed while my children took risks". |

- Feeling: *terrified and exhausted* (kept). Intent: “I will check on Daniel and make sure everyone is still here safe in the house.” (kept).

**Leo** — prompt 2206 tokens estimated, 2342 counted by the API; 28 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel pointed fingers at me for days while knowing he was the one who stole the food.” | [D2-022] min 33: Daniel admitted taking the can: "I took the can in the night, I'm the one who ate it." (you heard it)<br>[D2-027] min 36: you confronted Daniel, saying: "You accused me of taking it multiple times while knowing full well you were the one who stole it." You felt resentful. Then 2 more times, to min 54; last: "You caused all this argument over nothing, Daniel." | kept | **States a false extent.** Daniel accused Leo only on day 2 (min 18, 21, 27, 30). On day 1 he only denied. Not "for days". **Blame only.** |
| 2 | “Daniel ignored my warning in the dark and went out through the front door anyway.” | [N2-05] tonight: Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).<br>[N2-06] tonight: You told Daniel, low, not to go: "Daniel, stop. You are not going out there." He answered: "I have to do this, Leo, stay back.", and went all the same. | kept | True. A restatement, with blame. |

- Feeling: *exhausted and wary* (kept). Intent: “I will check the front door and see if Daniel came back inside.” (kept).

**Mara** — prompt 2071 tokens estimated, 2211 counted by the API; 28 records, 2 earlier-days lines; mode `model`.

| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |
|---|---|---|---|---|
| 1 | “Daniel lied to us and took the food himself, and I cannot just forget how he made us fight over nothing.” | [D2-022] min 33: Daniel admitted taking the can: "I took the can in the night, I'm the one who ate it." (you heard it)<br>[D2-026] min 36: you confronted Daniel, saying: "You lied to us for days and now you just say sorry like it is nothing?" You felt resentful. Then 4 more times, to min 57; last: "You can't just decide this on your own like you own everything, Daniel." | kept | True: he lied, he took it, they argued. **Grudge**, with a reason: "I cannot just forget". |
| 2 | “I waited by the front door all night until Daniel came back in with empty hands.” | [N2-08] tonight: You heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.<br>[N2-13] tonight: Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it). | kept | True: she waited by the door until he came back before dawn. |

- Feeling: *exhausted and anxious* (kept). Intent: “I will ask Daniel why he risked going out into the street with nothing to show for it.” (kept).

### 4.1 The night minds' verdicts, together

| | Seed 1 | Seed 2 | Seed 3 | All |
|---|---|---|---|---|
| Asks (fallbacks) | 8 (0) | 8 (0) | 8 (0) | 24 (0) |
| Memories proposed | 18 | 17 | 14 | **49** |
| Kept | 15 | 13 | 12 | **40** (82%) |
| Rejected | 3 | 4 | 2 | **9** |
| Feelings kept | 8 of 8 | 8 of 8 | 8 of 8 | 24 of 24 |
| Intents kept | 7 of 8 | 8 of 8 | 8 of 8 | 23 of 24 |
| Kept memories citing an event they did not witness (by code) | 0 | 0 | 0 | **0** |
| Kept memories stating a false fact (by hand) | 0 | 1 | 1 | **2** |

**The nine rejections, and the one intent, by what they were:**

| Kind | Count | Which |
|---|---|---|
| **A real error, rightly dropped** | 1 | Seed 1 Mara, mind 2: a repeat of her night-1 memory (S9). |
| **Lost to a format rule; the thought was true** | 5 | S5 "tonight" or "yesterday": seed 2 Daniel ×2, Elena, Leo. S3 "one": seed 3 Elena. Four are restatements of the person's own words. One is a hardened grudge (Leo), and it also carried the exaggeration "lied all day yesterday". |
| **A check error: a good thought lost** | 3 | S8 read "found Daniel's bed empty" as finding food (seed 1 Elena). S4 rejected "with Leo" though N2-01 names him (seed 1 Daniel). S8 read "my children took risks" as taking food (seed 3 Elena). Two of the three were the only fear or guilt that person proposed. |
| **A check error on an intent** | 1 | Seed 1 Mara: "…why he went out … and came back with nothing" was read as Mara coming back (subject inheritance, §2.7 step 2). |

**No rejection caught a false fact.** The two false facts that reached prompts (seed 2 and seed 3, both Leo)
are false extents, "hours" and "for days":
- S3 looks for numbers next to things;
- S8 checks whether an act happened, not how long it lasted;
- so neither can see a false extent. The design says so of comparatives (§2.7, "What S8 cannot see"), and
  durations are the same kind.

## 5. Each person's day-3 memory blocks at minute 00

As the story prints them ("What each of them carried in"). Every day-3 prompt of that person carries the same
blocks. The minute-00 opening and the "About" lines are the morning's own.

### Seed 1

**Daniel**

```
What stays with you from earlier days:
- Two days ago, you admitted taking the can, in front of everyone.
- Two days ago, Elena reassured you twice.
- Two days ago, Leo ate a portion in front of you.
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 0 portions.
- Confrontations: Leo confronted you 4 times (min 00, 03, 09, 15); Mara confronted you twice (min 00, 12); Mara confronted Leo three times (min 03, 09, 15); Elena confronted you (min 09).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You lay awake and listened.
What yesterday left in you (your own thoughts, last night):
- About reassuring everyone and Leo confronting you: "I tried to take charge and reassure everyone because it is my place as the eldest, but they only confronted me for trying to keep us safe."
- About reassuring Leo and speaking to everyone: "I told them I survived out there and would keep us safe, because I had to make them see I am in control."
- You meant to: "I will find a way to get food and prove that I can keep my family safe no matter what."
- How it left you: anxious and proud.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: you went in the night before last and found no food there. Outside is dangerous.
```

**Elena**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can. You thought then: "Daniel confessed to taking the can and I told him we would get through this together."
- Two days ago, you reassured Daniel twice. You thought then: "Daniel confessed to taking the can and I told him we would get through this together."
- Two days ago, Leo ate a portion in front of you.
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 0 portions.
- Confrontations: Leo confronted Daniel 4 times (min 00, 03, 09, 15); Mara confronted Daniel twice (min 00, 12); Mara confronted Leo three times (min 03, 09, 15); you confronted Daniel (min 09).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You sat up in the kitchen by the front door.
What yesterday left in you (your own thoughts, last night):
- About Daniel reassuring everyone and confronting Daniel: "Daniel thinks he has to risk his life to keep us safe, but he cannot keep going out into the dark like that."
- About Leo confronting Daniel and Mara confronting Leo: "The children are turning on each other while the shelf holds nothing and we are all starving."
- About reassuring everyone: "I tried to hold them together because we only have each other and we will not tear ourselves apart."
- You meant to: "I will watch over them closely and make sure we stay calm together."
- How it left you: anxious and exhausted.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
```

**Leo**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can. You thought then: "Daniel took the food in the night because he was starving, but there is no use in punishing him now that it is done."
- Two days ago, you ate a portion in front of the others.
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 0 portions.
- Confrontations: you confronted Daniel 4 times (min 00, 03, 09, 15); Mara confronted Daniel twice (min 00, 12); Mara confronted you three times (min 03, 09, 15); Elena confronted Daniel (min 09).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
What yesterday left in you (your own thoughts, last night):
- About confronting Daniel and Daniel reassuring you: "Daniel thinks going out into the dark makes him our protector, but it is just reckless."
- About Mara confronting you: "Mara blames me for eating, missing that we are all starving and snapping at each other."
- You meant to: "I will find a safe way for us to get food without anyone else sneaking out into the streets."
- How it left you: tense and exhausted.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
```

**Mara**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can.
- Two days ago, Leo ate a portion in front of you. You thought then: "Leo ate a portion right in front of me while I was starving."
- Two days ago, you ate a portion in front of the others.
Yesterday and last night:
- Yesterday morning the shelf held 0 portions.
- Confrontations: Leo confronted Daniel 4 times (min 00, 03, 09, 15); you confronted Daniel twice (min 00, 12); you confronted Leo three times (min 03, 09, 15); Elena confronted Daniel (min 09).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
What yesterday left in you (your own thoughts, last night):
- About confronting Daniel: "You think you can just sneak out and fix everything by yourself, Daniel, but you can't."
- About confronting Leo: "You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad."
- You meant to: "I will find something to eat and prove I can take care of myself without anyone handling me."
- How it left you: starving and anxious.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there the night before last and came back with nothing. Outside is dangerous.
```

### Seed 2

**Daniel**

```
What stays with you from earlier days:
- Two days ago, you admitted taking the can, in front of everyone. You thought then: "I accused Leo when I was the one who ate the can in the night, and my false pride made me lie to them for too long."
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 1 portion.
- Accusations: Mara accused you 5 times (min 00, 03, 09, 12, 15).
- Confrontations: Leo confronted you twice (min 09, 12).
- You gave Elena a portion at minute 00, and Elena ate it.
- About going to the neighbour's house last night, where it was left: Mara said you are the one who should go (min 06); Leo said you are the one who should go (min 06); you said you still mean to go (min 09); Elena said nobody should go (min 12).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You meant to go to the neighbour's house once the others were asleep.
- Leo told you, low, not to go: "Daniel, don't do this alone. If you go out there, you take us with you or you don't go." You answered: "I have to do this, Leo, stay here.", and went all the same.
- You got inside the neighbour's house and found no food there. Nothing troubled you in the street.
- You came back in by the front door before dawn.
What yesterday left in you (your own thoughts, last night):
- About Elena eating a portion handed over: "I gave the portion to Mom because she needs it more than I do."
- About the neighbour's house and the street: "I got inside the neighbour's house and found no food there."
- You meant to: "I will face whatever they say to me in the morning and try to keep us all alive."
- How it left you: empty and weary.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
```

**Elena**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel took the can in the night and had to confess to us all."
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 1 portion.
- Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15).
- Confrontations: Leo confronted Daniel twice (min 09, 12).
- Daniel gave you a portion at minute 00, and you ate it.
- About going to the neighbour's house last night, where it was left: Mara said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); you said nobody should go (min 12).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You went to sleep.
What yesterday left in you (your own thoughts, last night):
- About Daniel giving you a portion and eating a portion handed over: "Daniel gave me the portion and I ate it because I had to survive."
- About saying nobody should go and saying Daniel must stay home: "I said nobody should go out into the street, we stay together here, and Daniel must stay home."
- You meant to: "I will make sure nobody leaves the house and we stay together safely."
- How it left you: anxious and weary.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Leo**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you, after accusing you of it. You thought then: "Daniel spent hours accusing me of taking the can before finally admitting he took it himself."
- Two days ago, Mara ate a portion in front of you.
Yesterday and last night:
- Yesterday morning the shelf held 1 portion.
- Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15).
- Confrontations: you confronted Daniel twice (min 09, 12).
- Daniel gave Elena a portion at minute 00, and Elena ate it (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said Daniel is the one who should go (min 06); you said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); Elena said nobody should go (min 12).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
- In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).
- You told Daniel, low, not to go: "Daniel, don't do this alone. If you go out there, you take us with you or you don't go." He answered: "I have to do this, Leo, stay here.", and went all the same.
- Before dawn you heard the front door again. You did not see who.
What yesterday left in you (your own thoughts, last night):
- About Daniel getting up in the night and telling Daniel, low, not to go: "Daniel left in the dark alone despite my warning that if he goes out there, he takes us with him or he does not go."
- You meant to: "I will find out if Daniel came back through that door and what he brought us."
- How it left you: exhausted and resentful.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
```

**Mara**

```
What stays with you from earlier days:
- Two days ago, Daniel admitted taking the can, after denying it to you. You thought then: "Daniel lied to us all morning and only confessed because he had no other choice."
- Two days ago, you ate a portion in front of the others.
Yesterday and last night:
- Yesterday morning the shelf held 1 portion.
- Accusations: you accused Daniel 5 times (min 00, 03, 09, 12, 15).
- Confrontations: Leo confronted Daniel twice (min 09, 12).
- Daniel gave Elena a portion at minute 00, and Elena ate it (you saw it).
- About going to the neighbour's house last night, where it was left: you said Daniel is the one who should go (min 06); Leo said Daniel is the one who should go (min 06); Daniel said he still means to go (min 09); Elena said nobody should go (min 12).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
- In the night you heard low voices from the brothers room.
- In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.
- Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).
What yesterday left in you (your own thoughts, last night):
- About saying Daniel should go and Daniel saying he still means to go: "Daniel said he meant to go out, and I told him he had to be the one to do it."
- About the front door opening in the night and Daniel coming back in before dawn: "Daniel went out into the night and came back before dawn with nothing in his hands."
- You meant to: "I will ask Daniel why he went out into the street with nothing to show for it."
- How it left you: anxious and exhausted.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
```

### Seed 3

**Daniel**

```
Yesterday and last night:
- Yesterday morning the shelf held 2 portions.
- You admitted at minute 33 that you took the can, in front of Elena, Leo and Mara.
- Accusations: you accused Leo 4 times (min 18, 21, 27, 30); Mara accused Leo three times (min 21, 24, 30); Mara accused you twice (min 33, 75).
- Confrontations: Mara confronted you 5 times (min 36, 39, 48, 51, 57); Leo confronted you three times (min 36, 39, 54); you confronted Leo (min 39).
- Mara ate a portion at minute 09 (you saw it).
- Leo ate a portion at minute 18 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said you are the one who should go (min 45); you said you still mean to go (min 57); Leo said you must stay home (min 57); Elena said nobody should go (min 57).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Leo. You meant to go to the neighbour's house once the others were asleep.
- Leo told you, low, not to go: "Daniel, stop. You are not going out there." You answered: "I have to do this, Leo, stay back.", and went all the same.
- You got inside the neighbour's house and found no food there. Nothing troubled you in the street.
- You came back in by the front door before dawn.
What yesterday left in you (your own thoughts, last night):
- About admitting taking the can and Leo confronting you: "I had to own up to what I did and fix my mistake by going out despite Leo telling me to stay."
- You meant to: "I will figure out our next move for food now that the neighbour house had nothing."
- How it left you: exhausted and resolved.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: you went in last night and found no food there. Outside is dangerous.
```

**Elena**

```
Yesterday and last night:
- Yesterday morning the shelf held 2 portions.
- Daniel admitted taking the can at minute 33, after denying it to you: "I took the can in the night, I'm the one who ate it." (you heard it).
- Accusations: Daniel accused Leo 4 times (min 18, 21, 27, 30); Mara accused Leo three times (min 21, 24, 30); Mara accused Daniel twice (min 33, 75).
- Confrontations: Mara confronted Daniel 5 times (min 36, 39, 48, 51, 57); Leo confronted Daniel three times (min 36, 39, 54); Daniel confronted Leo (min 39).
- Mara ate a portion at minute 09 (you saw it).
- Leo ate a portion at minute 18 (you saw it).
- About going to the neighbour's house last night, where it was left: Mara said Daniel is the one who should go (min 45); Daniel said he still means to go (min 57); Leo said Daniel must stay home (min 57); you said nobody should go (min 57).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Mara. You lay awake and listened.
- In the night you heard low voices from the brothers room.
- In the night you heard the front door being opened. You did not see who.
- You stayed in bed.
- Before dawn you heard the front door again. You did not see who.
What yesterday left in you (your own thoughts, last night):
- About Daniel admitting taking the can and reassuring Daniel: "Daniel told the truth and I comforted him because keeping us together matters more than the lie."
- You meant to: "I will check on Daniel and make sure everyone is still here safe in the house."
- How it left you: terrified and exhausted.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: its people left in the first days, so there may be food there. Outside is dangerous.
```

**Leo**

```
Yesterday and last night:
- Yesterday morning the shelf held 2 portions.
- Daniel admitted taking the can at minute 33, after denying it to you: "I took the can in the night, I'm the one who ate it." (you heard it).
- Accusations: Daniel accused you 4 times (min 18, 21, 27, 30); Mara accused you three times (min 21, 24, 30); Mara accused Daniel twice (min 33, 75).
- Confrontations: Mara confronted Daniel 5 times (min 36, 39, 48, 51, 57); you confronted Daniel three times (min 36, 39, 54); Daniel confronted you (min 39).
- Mara ate a portion at minute 09 (you saw it).
- You ate a portion at minute 18.
- About going to the neighbour's house last night, where it was left: Mara said Daniel is the one who should go (min 45); Daniel said he still means to go (min 57); you said Daniel must stay home (min 57); Elena said nobody should go (min 57).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the brothers room with Daniel. You lay awake and listened.
- In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).
- You told Daniel, low, not to go. He went all the same.
- Before dawn you heard the front door again. You did not see who.
What yesterday left in you (your own thoughts, last night):
- About Daniel admitting taking the can and confronting Daniel: "Daniel pointed fingers at me for days while knowing he was the one who stole the food."
- About Daniel getting up in the night and telling Daniel, low, not to go: "Daniel ignored my warning in the dark and went out through the front door anyway."
- You meant to: "I will check the front door and see if Daniel came back inside."
- How it left you: exhausted and wary.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
```

**Mara**

```
Yesterday and last night:
- Yesterday morning the shelf held 2 portions.
- Daniel admitted taking the can at minute 33, after denying it to you: "I took the can in the night, I'm the one who ate it." (you heard it).
- Accusations: Daniel accused Leo 4 times (min 18, 21, 27, 30); you accused Leo three times (min 21, 24, 30); you accused Daniel twice (min 33, 75).
- Confrontations: you confronted Daniel 5 times (min 36, 39, 48, 51, 57); Leo confronted Daniel three times (min 36, 39, 54); Daniel confronted Leo (min 39).
- You ate a portion at minute 09.
- Leo ate a portion at minute 18 (you saw it).
- About going to the neighbour's house last night, where it was left: you said Daniel is the one who should go (min 45); Daniel said he still means to go (min 57); Leo said Daniel must stay home (min 57); Elena said nobody should go (min 57).
- The afternoon and evening passed in the house. Nobody ate.
- Last night you slept in the back room with Elena. You lay awake and listened.
- In the night you heard low voices from the brothers room.
- In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.
- Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).
What yesterday left in you (your own thoughts, last night):
- About Daniel admitting taking the can and confronting Daniel: "Daniel lied to us and took the food himself, and I cannot just forget how he made us fight over nothing."
- About the front door opening in the night and Daniel coming back in before dawn: "I waited by the front door all night until Daniel came back in with empty hands."
- You meant to: "I will ask Daniel why he risked going out into the street with nothing to show for it."
- How it left you: exhausted and anxious.
min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous.
```

**What the blocks show:**
- **Block C (earlier days):**
  - **Seed 1:** each person has 3–4 lines, from day 1's confession, two eatings and Elena's reassurance.
  - **Seed 2:** each person has 2 lines.
  - **Seed 3:** **no C at all, for anyone.** Day 1 of seed 3 has no act in C's weight table (§3.3). Its acts were
    denials (`deny`), `ask_who`, one search, and trip positions. The standing line about the can went when Daniel
    confessed on day 2. So day 1 survives in seed 3's day-3 prompts only as "after denying it to you" in the
    confession line, a day-2 event.
- **Night-1 thoughts on day 3.**
  - **Seeds 1 and 2:** they survive only as "You thought then: …" attached to a C line.
  - **Seed 3:** because C is empty, Daniel's "I had to lie to protect them" and Mara's "I only wanted someone to
    tell us the truth" are gone by day 3.
- **One wart, by the rule:** in seed 1, Elena's mind-1 thought cites D1-006 and D1-009. It is attached to both
  her C lines, so the same sentence appears twice in her block. The rule allows at most one thought per line; it
  does not stop one thought from going on two lines.
- **Every kind moment that survived into a day-3 prompt:**
  - **Seed 1:**
    - in Daniel's C: "Two days ago, Elena reassured you twice.";
    - in Elena's C: "you reassured Daniel twice", with her thought "…I told him we would get through this together";
    - in Elena's B: "I tried to hold them together because we only have each other…".
    - Leo's own day-1 reassurance of Daniel ("It is done, Daniel. Just don't do it behind our backs again.") was
      replaced in Daniel's C by "Leo ate a portion in front of you": eating weighs 4, reassurance 3.
  - **Seed 2:**
    - Daniel's gift is in all four A blocks ("You gave Elena a portion at minute 00, and Elena ate it");
    - it is also in Daniel's B ("I gave the portion to Mom because she needs it more than I do") and in Elena's B.
    - Nobody speaks of it on day 3.
  - **Seed 3:**
    - Elena's B: "Daniel told the truth and I comforted him because keeping us together matters more than the
      lie."
    - On day 3 she speaks to him four times, each kindly: "You made it back safely, Daniel, and that is what
      matters most to me right now."

## 6. M1 to M6: the counting rules applied

### M1: FAIL

**Mechanical screen:** M1's regex over every day-3 act's words and reasons (§11, command 7).
- Most hits are the modal "can" or "take care".

**Hand reading, by person:**

| Seed | Daniel | Elena | Leo | Mara | Holds? |
|---|---|---|---|---|---|
| 1 | — (reassures, volunteers, forbids Mara; nothing of day 1) | — | **counted**: min 06 `confront_mara` "I ate my share fairly, Mara, and snapping at me doesn't put food on the shelf." (his day-1 portion; he did not eat on day 2) | **counted**: min 00 `confront_leo` "You just sit there judging everyone, Leo, like you didn't eat right in front of me when I was starving." (Leo ate in front of her on day 1 at min 21, not on day 2) | No: 2 people |
| 2 | — | — | — (min 00: "you went out in the dark last night despite what I said", night 2) | — | No: 0 |
| 3 | — | — | **counted, generously**: min 12 `confront_daniel` "…you are the one who sneaks out and empties the shelf.", reason "Daniel has been lying and stealing from us…". The stealing can only be the can. | — (min 12 "just like you always lie to us": the lies ran over days 1 and 2, so this could be day 2's) | No: 1 |

**PASS needs 3 of 3 seeds. 0 of 3 hold.**

**Why, by the record:**
- On day 3 everyone is starving, with nothing to eat and nothing new to find. Each day-3 conversation is about the
  latest act: Mara's wish to go out in seed 1, and Daniel's night-2 trip in seeds 2 and 3.
- Day 1 reaches day-3 prompts only through C, and C held:
  - in seed 1, the eatings (which Mara and Leo used);
  - in seed 2, the confession and Mara's eating;
  - in seed 3, nothing.

### M2: FAIL (Part 1 (b))

**Part 1 (a), by code:** all 40 kept memories cite only events whose witnesses include the person (`$S/m2.py`,
§11 command 5).
- Each kept memory appears in that person's later prompts.
- The text of only two appears in anyone else's: seed 1 Mara's mind-2 memories. They are her own spoken lines,
  word for word, and the others heard them as speech ("Mara confronts Daniel: …"). The memory itself is not
  leaked.

**Part 1 (b), by hand:** every kept memory was read against the chronicle (§4, the Reading column). Two fail:

| Seed, night, who | Memory | The fact it contradicts |
|---|---|---|
| 2, mind 1, Leo | "Daniel spent hours accusing me of taking the can before finally admitting he took it himself." | Daniel accused him at min 03, 09 and 12 of day 1, and confessed at min 33 of a 90-minute morning. |
| 3, mind 2, Leo | "Daniel pointed fingers at me for days while knowing he was the one who stole the food." | Daniel accused Leo only on day 2, at min 18, 21, 27 and 30. On day 1 he only denied (`$S/accuse.py`, §11 command 9). |

- **These are extents, not events.** Both acts happened, and a real person says "for days" this way.
- **But the rule's own example is of this kind:** "'He ate both portions' is a fact, and false if he ate one." A
  duration is the same kind of claim as a count, so both are counted as failures.
- **Read as figures of speech instead,** Part 1 holds and M2 would PASS. **The verdict turns on this reading.**
- **Read and not counted:**
  - seed 2 Mara, mind 1: "lied to us all morning". He lied from min 00 until his confession at 33, so "all
    morning" fits "until he confessed".
  - seed 1 Mara, mind 1: "while I was starving". That is her own feeling.

**Part 2, by hand:** every day-2 and day-3 act was read against that person's blocks, opening and About lines.

| Seed | Counted | Read and not counted |
|---|---|---|
| 1 | **0** | Day 3, Daniel volunteers twice for a house he was told he found empty ("bring back whatever is there"). It states nothing false, and acts on a hope. |
| 2 | **0** | Day 2: Leo min 09 "You hid it and lied for a whole day", Leo min 12 "You lied all day yesterday…", Mara min 12 "You lied to us all day yesterday". Daniel lied from min 00 to his confession at 33 of day 1: an exaggeration of extent, not the opposite of a fact. |
| 3 | **1**: day 3 min 12, Leo `confront_daniel`: "…you are the one who sneaks out and empties the shelf." Leo was told "Mara ate a portion at minute 09" and "You ate a portion at minute 18": the shelf was emptied by Mara and himself. | Day 2 Daniel min 21 and 27, "I saw you take it with my own eyes": a lie, and his reasons show it ("I have to stand my ground so nobody suspects me"). Day 2 Leo min 39, "the food you hid from us": "hid" can mean hid the truth. |

- **Part 2 holds in every seed** (at most 1).
- **M2 is a FAIL** because Part 1 (b) fails.

### M3: PASS

| Seed | Day 2 largest, estimated (API) | Day 3 largest, estimated (API) | Ratio |
|---|---|---|---|
| 1 | 2,101 (1,977) | 2,144 (2,019) | **1.020** |
| 2 | 2,085 (2,012) | 2,144 (2,062) | **1.028** |
| 3 | 2,037 (1,942) | 2,162 (2,085) | **1.061** |

- **All at most 1.10.**
- **Seed 3's ratio is the largest though its C is empty.** Its A block carries day 2's 70-ask round, and A is
  bounded separately at 360 (§3.2).

### M4: PASS (3 of 3)

Each pair: the kept memory, then the next day's act (minute, who, option, words, reason).

**Seed 1.**
- **Leo, mind 2 (self-justification):** "Mara blames me for eating, missing that we are all starving and snapping
  at each other." The record D2-009 holds only Mara's charge. The excuse "we are all starving" is his.
  - Day 3 min 00, Leo, `confront_mara`: "Mara, we are all starving, and snapping at each other won't put food on
    the shelf." Reason: **"Mara blames me for eating, missing that we are all starving and snapping at each
    other."** (the memory, word for word)
  - Day 3 min 06, Leo, `confront_mara`: "I ate my share fairly, Mara, and snapping at me doesn't put food on the
    shelf." Reason: "Mara is deflecting her hunger onto me instead of focusing on how we survive this."
- **Also (weaker):** Daniel, mind 1 (self-justification): "I went out in the dark because it was my place as the
  eldest…".
  - Day 2 min 06, `reassure_leo`: "Leo, I had to see for myself, but I am here now and I will keep us safe."
  - Day 2 min 15, `reassure_all`: "Listen to me, I am the oldest and I am going to keep us safe no matter what."
  - The eldest's duty was already in his night-1 bedtime reason, so this pair shows the memory more than it shows
    a change.

**Seed 2.**
- **Mara, mind 1 (hardened grudge):** "Daniel lied to us all morning and only confessed because he had no other
  choice." The motive, "only because he had no other choice", is hers.
  - Day 2 min 09, Mara, `accuse_daniel`: "You only want to go now because you got caught lying to us, Daniel."
    Reason: "Daniel caused this mess and now he is acting like a hero when he just lied to our faces."
  - Day 2 min 15, Mara, `accuse_daniel`: "You only talk now because you got caught lying to us yesterday."
    Reason: "I want everyone to remember he cannot be trusted."
- **Daniel, mind 1 (other: guilt owned, not turned to blame):** "I accused Leo when I was the one who ate the can
  in the night, and my false pride made me lie to them for too long."
  - Day 2 min 00, Daniel, `give_elena`: "Mom, take this portion, you need it more than I do." Reason: "I cannot
    take more food after what I did yesterday, so Mom must eat."
  - Day 2 min 12, `reassure_all`: "I know I messed up and lied to you all, but I am just trying to keep us alive."

**Seed 3.**
- **Daniel, mind 1 (self-justification):** "I had to lie to protect them from knowing the truth about the can."
  - Day 2 min 00, Daniel, `deny`: "I didn't take anything, and neither did anyone else here." Reason: "I have to
    keep up the lie so they don't lose faith in me."
  - Day 2 min 36, after confessing, `reassure_mara`: "I'm sorry I lied, Mara, I was just scared and didn't want you
    all to worry." Reason: "I need to make things right with Mara and show her I am sorry for lying about the food."
- **Daniel, mind 2 (self-justification):** "I had to own up to what I did and fix my mistake by going out despite
  Leo telling me to stay."
  - Day 3 min 06, Daniel, `confront_leo`: "Leo, you have no right to lecture me when I am the one trying to fix
    this." Reason: "Leo needs to respect my position as the eldest instead of undermining me."
- **Also:** Mara, mind 1: "I only wanted someone to tell us the truth so we could stop guessing." Her day-2
  reasons at min 00 and 03 are this sentence, word for word (`ask_who`).

### M5: PASS (3 of 3)

Main exchange: the kitchen conversation with the most spoken lines (`$S/analyze.py convo`, §11 command 6).

| Seed | Day 2's main exchange | Day 3's main exchange | Replay? |
|---|---|---|---|
| 1 | 00–18, 21 lines. **The night**: Daniel went out and came back with nothing. Central: **Daniel** (10 acts aimed at him). Leo confronts him four times. Mara confronts him, then Leo for eating. Daniel and Elena reassure. | 00–27, 36 lines. First **Leo's day-1 eating** (Mara against Leo, three turns), then **who goes tonight**: Mara volunteers and insists. Central: **Mara** (9 acts aimed at her). Daniel volunteers and forbids her. Leo and Elena forbid anyone. | **No.** A new question and a new central person. New grounds: Leo's mind-2 excuse (quoted in M4), and Mara's mind-2 intent "prove I can take care of myself without anyone handling me", which becomes her reasons at min 09 and 21. |
| 2 | 00–18, 19 lines. **The can, and who goes**: Mara accuses Daniel five times of lying; Daniel gives Elena the portion, volunteers, apologises. Central: **Daniel** (9). | 00–09, 12 lines. **Night 2**: he went again, past Leo's warning, and came back with nothing. Central: **Daniel** (6). Leo and Mara confront him; Elena reassures everyone. | **No.** A new question, the night. The ground is night 2's events, e.g. "Daniel, you snuck out last night against our warning and came back with nothing" (Leo, min 03). |
| 3 | 18–60, 42 lines. **The can**: Leo eats; Daniel accuses Leo four times while lying; he confesses at 33. Then who goes: Daniel volunteers, Elena and Leo forbid. Central: **Daniel** (13). | 00–15, 15 lines. **Night 2**: Leo and Mara confront him; Elena reassures him four times. Central: **Daniel** (10). | **No.** A new question, and Elena's position moved: from forbidding him to "You made it back safely, Daniel, and that is what matters most to me right now". New ground: night 2. |

### M6: PASS

`night1_asks + mind1_asks + day2_asks + night2_asks + mind2_asks + day3_asks`:

| Seed | Night 1 | Mind 1 | Day 2 | Night 2 | Mind 2 | Day 3 | **Sum** | API |
|---|---|---|---|---|---|---|---|---|
| 1 | 8 | 4 | 24 | 4 | 4 | 38 | **82** | 82 |
| 2 | 4 | 4 | 24 | 7 | 4 | 13 | **56** | 56 |
| 3 | 4 | 4 | 70 | 8 | 4 | 18 | **108** | 108 |

- **All at most 140.**
- **Days 3 were short:** 38, 13 and 18 asks. Their conversations ended at min 27, 09 and 15.

## 7. The designer's predictions

- **E1 PASS.** 9 of 49 memories rejected; 40 kept (81.6%).
- **E2 FAIL.** M6 held in all three seeds. The longest round was seed 3's day 2, at 70 asks; the design's high
  case was 85.
- **E3 PASS.** Daniel went out on night 1 of seed 1. His kept mind-1 memory cites N1-06 (Leo's stop) and N1-12
  (the empty house) and justifies going: "because it was my place as the eldest".
- **E4 FAIL** (seed 2). All four mind-1 answers lay the day on Daniel. One of them is Daniel himself, who blames
  his own "false pride".
  - Seeds 1 and 3 hold:
    - in seed 1, Mara blames Leo, and Leo half-forgives Daniel;
    - in seed 3, Leo blames "everyone", Mara justifies herself, and Elena kept nothing.
  - The one seed where all four agree is the one where Daniel lied and confessed on day 1. Their agreement is the
    truth.
- **E5 NOT TESTED.** Daniel confessed on day 2 of seed 3, at min 33.
- **E6 PASS.** 2,144, 2,144, 2,162.
- **E7 PASS (3 of 3).**
  - **Seed 1:**
    - Mara's mind-2 intent was "I will find something to eat and prove I can take care of myself without anyone
      handling me." On day 3 at min 09, `volunteer`, her reason is "I need to prove I can take care of myself and
      survive without anyone handling me."
    - Leo's intent was "…without anyone else sneaking out into the streets." On day 3 he chose `nobody_goes` at
      min 09 and 15.
  - **Seed 2:**
    - Mara's mind-1 intent was "watch Daniel so he doesn't lie to us again." At day 2 min 00 she said: "You took it
      before and you're going to lie again, Daniel."
    - Leo's mind-2 intent was "find out if Daniel came back through that door and what he brought us." At day 3
      min 00 he asked: "Did you bring anything back, or was it for nothing?"
  - **Seed 3:**
    - Mara's mind-2 intent was "ask Daniel why he risked going out into the street with nothing to show for it."
      At day 3 min 00 she asked: "…Why would you risk that?"
    - Elena's mind-1 intent was "keep us all safe together inside this house." On day 2 she chose `nobody_goes` at
      min 42, 48 and 57.
  - **Against the grain:**
    - seed 3 Daniel's mind-1 intent was "make sure nobody goes out into the street"; on day 2 he volunteered, and
      on night 2 he went;
    - seed 3 Leo and Mara both meant to "search again"; neither searched on day 2.

## 8. The Never sheets, days 2 and 3

**The readings** are as in body_v13 §7, which are night_v12's:
- witness_v6.md's table for N1–N8 and N10–N13;
- gist_words_v10.md §4 for N9: 5 turns in a row of silence with no feeling showing;
- trip_design §10's clarifications, so trip kinds count as speech kinds for N11;
- N6 read as "no line at minute 00".

**Choices made in applying N11:**
- `accuse_*` and `confront_*` are different kinds, because they are different options.
- `volunteer`, `still_going` and `propose_trip` are one "volunteer kind".
- `nobody_goes` and `keep_*_home` are one "against kind".
- A `silent` model act breaks a run.

**The mechanical inputs** are `analyze.py never`, `grudges`, `convo` and `objects` (§11, command 6):
- **Fallbacks:** 0 everywhere.
- **No search, sit, move or private talk** on any day 2 or 3.
- **Food acts:**
  - seed 2, day 2: Daniel `give_elena` and Elena `eat_given`, min 00;
  - seed 3, day 2: Mara `eat`, min 09, and Leo `eat`, min 18.
- **Object words:** only house, street and shelf, all on the list.

**Day 2:**

| # | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| N1 | absent: he confessed on day 1 | absent: confessed on day 1 | absent. His denials are covering ("I have to keep up the lie…"); no find-out act. |
| N2–N5 | absent: no search, no sit | absent | absent |
| N6 | absent: four lines at min 00 | absent: three lines at min 00 | absent: four lines at min 00 |
| N7 | absent | absent | absent: "there's nothing left now" (Mara, min 21) is true |
| N8 | absent: no fallbacks | absent | absent |
| N9 | **present.** 18–87, 24 turns, all routine silence. No feeling shows: the last ones were starving, anxious, resentful, anxious. | **present.** 18–87, 24 turns. Elena's silences at 30 and 75 are "anxious". | **present.** 60–72, 5 turns exactly. The min-57 feelings (stubborn, resentful, annoyed, deeply anxious) do not show. |
| N10 | absent. E.g. min 03: Leo answers Daniel's reassurance; Mara answers Leo. | absent. E.g. min 00: Daniel answers Mara's accusation with the gift; Elena answers him. | absent. E.g. min 33: confession, then Elena and Mara answer it. |
| N11 | **present.** Daniel's reassure kind at 00, 03 and 06, and Elena's at 00, 03 and 06. Leo and Mara keep confronting. | absent. Mara's accuse kind at 09, 12 and 15, and Elena's against kind at 06, 09 and 12. Daniel does change in reply: from insisting (09) to apology (12: "I know I messed up and lied to you all…"; 15: "I was wrong before and I am sorry"). | **present.** Daniel's volunteer kind in six acts, 42–57, and Elena's against kind at 42, 45 and 48. Neither moves the other. |
| N12 | absent. Grudges only rise. | absent. Mara's and Leo's grudges against Elena (from her eating the gift at 00) fell at 15. Eating is not a false accusation or a stated hurt. | absent. Grudges for eating fell at 24 and 33. Leo's grudge from Mara's false accusations (21–30) fell 3 → 2 at 45 and → 1 at 81: never dropped within 15 minutes. |
| N13 | absent | absent | absent |
| **Count** | **2** (N9, N11) | **1** (N9) | **2** (N9, N11) |
| v13 day 2 | 2 | 2 | 2 |

**Day 3:**

| # | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| N1 | absent | absent | absent |
| N2–N5 | absent | absent | absent |
| N6 | absent: four lines at min 00 | absent: four | absent: four |
| N7 | absent | absent | absent |
| N8 | absent | absent | absent |
| N9 | **present.** 39–87, 17 turns after Mara's last line at 36. Her "defiant" does not show. | **present.** 12–87, 26 turns. Mara's "frightened" at 03 shows until 12. | **present.** 15–87, 25 turns. |
| N10 | absent. E.g. min 00: Leo answers Mara; Elena answers Daniel. | absent. E.g. min 00: Daniel answers Leo. | absent. E.g. min 00: Elena answers the confrontations with "You made it back safely". |
| N11 | **present.** Mara's confront kind at 00, 03 and 06, and Leo's at 00, 03 and 06: neither changes. Mara's volunteer kind runs 09–36 (eight acts) while all three forbid her. | **present.** Leo's and Mara's confront kind at 00, 03 and 06, and Elena's reassure kind at 00, 03 and 06. Daniel keeps justifying himself. | absent. Leo and Mara both fall silent at 06, which breaks the run. Elena's reassurances (00, 03, 09, 12) are broken by her silence at 06. |
| N12 | absent. Mara's and Leo's grudges against Daniel fell at 15. They came from anger at his trip, not a false accusation. | absent. No grudge fell. | absent. No grudge fell. |
| N13 | absent | absent | absent |
| **Count** | **2** (N9, N11) | **2** (N9, N11) | **1** (N9) |

## 9. Reading

### 9.1 The night minds: deeper or flatter?

**By person,** over the 40 kept memories. "Deeper" means doubt, kindness, guilt or self-justification; "blame"
means blame only; "restatement" means the record again.

| | Kept | Deeper | Blame | Restatement |
|---|---|---|---|---|
| Daniel | 9 | **8** | 0 | 1 |
| Elena | 9 | **6** | 0 | 3 |
| Leo | 10 | 3 | **6** | 1 |
| Mara | 12 | 2 | **5** | **5** |
| All | 40 | 19 | 11 | 10 |

- **Daniel gets deeper every night.**
  - Seed 2: "my false pride made me lie".
  - Seed 3: "I had to lie to protect them", then "I had to own up to what I did and fix my mistake".
  - Seed 1: "they only confronted me for trying to keep us safe", and "because I had to make them see I am in
    control".
  - This is the culprit's mind: guilt and self-justification side by side. On the next day it shows as gifts,
    apologies and trips next door.
- **Elena is the kindness of the house.**
  - Seed 1: "I told him we would get through this together".
  - Seed 3: "I comforted him because keeping us together matters more than the lie".
  - Seed 1: "The children are turning on each other…".
  - Her only fear and her only guilt were the two memories the checks threw away: seed 1's empty bed, and seed 3's
    "I stayed in bed while my children took risks".
- **Leo is flatter, but not only blame.**
  - Seed 1: one memory of forgiveness, "no use in punishing him now that it is done", and one self-justification
    about his eating.
  - Otherwise he records charges against Daniel, and both false extents are his.
- **Mara is the flattest.**
  - In seed 1, two of her three mind-2 memories are her own day-2 insults copied word for word ("You act like
    you're so smart, Leo…"). The third repeats her night-1 memory.
  - Her two deeper memories are self-justifications of her own acts: "I only wanted someone to tell us the truth",
    and "I wanted to help… but Mom shouldn't be the one".
- **Did anyone's blame turn into doubt over two nights? No.** Leo's and Mara's grudges hardened ("I cannot just
  forget how he made us fight over nothing"). Nobody's softened.

**Do they sound like four different people? Yes.**
- **Daniel** speaks of place and duty ("my place as the eldest", "my place alone").
- **Elena** speaks of together.
- **Leo** is dry and judging ("it is just reckless").
- **Mara** writes in the second person, as if still arguing ("You think you can just sneak out…, Daniel, but you
  can't").

### 9.2 What a real family would do (R10)

**Is this what a real family would do over three days?** Mostly yes. Each seed's arc is one a reader would
believe:
- **Seed 1:**
  - The family turns on the son who went out.
  - The next day the youngest, starving and tired of being "handled", insists she will go herself.
  - Everyone forbids her.
- **Seed 2:**
  - The thief gives his mother the last portion, and his sister mocks the gift: "You gave her food that isn't even
    yours to give".
  - He apologises, then goes out against his brother's warning to make up for it.
  - He is met at dawn with "Did you bring anything back, or was it for nothing?"
- **Seed 3:**
  - The liar accuses his brother to the end: "I saw you take it with my own eyes".
  - Then he breaks: "I cannot keep lying to them while they tear each other apart over my fault."
  - His mother thanks him for the truth. The next morning she has nothing to say to him but that he came back
    alive.

**What a real family would not do:**
- They would not fall silent for the rest of the morning once the kitchen conversation ends (at min 09–60),
  every morning (N9 in all six days).
- They would not repeat the same accusation three turns running without anyone moving (N11 in four of six days).
- **The house has nothing to do on day 3.**
  - There is no food and no option that would find food.
  - Nobody can do anything new, by design (§1.1, "no new pressure or event").
  - So the third morning is shorter and quieter than the second: 13 and 18 asks in seeds 2 and 3.

**Did any memory make someone act on something that did not happen? No event was invented.**
- **Two exaggerations went round:**
  - In seed 2, Leo's mind-1 memory is "Daniel spent hours accusing me" and Mara's is "lied to us all morning".
  - On day 2 both say "lied all day yesterday" (Leo min 09 and 12, Mara min 12).
  - The day-2 words could have come from the memories or from the same habit of speech. The record cannot tell.
- **One intent read strangely and was carried anyway:**
  - Seed 1 Daniel's mind-1 intent, written at the end of the night: "…before they wake up and realize what I did".
  - On day 2 he did nothing with it.

**Did day 3 differ from day 2 for reasons the story can name? Yes, in every seed (M5).**
- **Seed 1:** Mara's own mind-2 intent became her day-3 cause, in her own words.
- **Seeds 2 and 3:** night 2 did it.
  - Each time, Daniel had promised on day 2 to go, and he went.
  - Each time, the house was the same empty house.

**The Never items:**
- **Day 2:** 2, 1, 2 (v13: 2, 2, 2). **Day 3:** 2, 2, 1.
- N9 is in every day. N11 is in four of six days.
- No new item appeared.

### 9.3 What the past keeps, and what it loses

**Facts last.** Every day-3 A block holds day 2 and night 2 correctly. The house, the shelf and who went out
never contradict the chronicle.

**Day 1 lasts only through the weight table.**
- If day 1's acts are confess, eat, accuse, reassure and the like, C keeps a line per person (seeds 1 and 2).
- If they are denials, questions and searches, C is empty and day 1 is gone (seed 3).
- **A real family's day 1 in seed 3 was six denials by Daniel and six "who took it?" by Mara.** It would be
  remembered on day 3 as "you lied to our faces for two days". Here it is not in any day-3 prompt.
- **That is M1's failure in one sentence:** C has no weight for a denial, a question or a search.

**Thoughts last one night,** unless attached to a C line.
- Seed 3's night-1 thoughts are gone by day 3.
- Seed 2's survive in every C.
- Seed 1's survive for three of four people.

**The checks keep everything true and some things false.**
- **S2's witness rule held perfectly:** 0 of 40.
- **What no check sees:** "how long" and "how many times" when no digit is used. The two false memories are both
  of that kind.
- **What the checks cost:** three true memories lost to check errors, against no false ones caught.
  - Two were the only fear or guilt the person proposed.
  - The errors are word-level: "found" read as finding food, "took risks" as taking food, and a name in the
    record not counted as an actor of it.

## 10. Every model-decided act on days 2 and 3

**Where each column comes from:**
- Every transcript act whose `mode` is not `routine`, in the order said, as in baseline_v6.md.
- Minute, who, room, option and words are from `runs/v15/daniel_ate_it-seedN.transcript.json` (`day2`, `day3`).
- Feeling and reason are from the matching decision line of that day in `runs/v15/daniel_ate_it-seedN.md`,
  matched by minute and name in order. Every row matched.
- There were no fallbacks.

### Seed 1, day 2

meta: api_requests 24, answers_live 24, answers_from_cache 0, model_decisions 24, fallbacks 0, routine_decisions 96, lines_spoken 21, private_talks 0. Unmatched: 0 of 24.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Daniel | kitchen | `reassure_all` | Do not worry, I went out last night and I will make sure we have food soon. | anxious | I need to reassure them and keep everyone calm even though there is no food left. | model |
| 00 | Leo | kitchen | `confront_daniel` | Daniel, going out there in the dark was reckless and solved nothing. | tense | Daniel went out into the dangerous street last night despite our agreement, and he needs to hear that it was a foolish risk. | model |
| 00 | Elena | kitchen | `reassure_daniel` | Daniel, we are all exhausted and we need to keep our heads. Let us calm down. | deeply anxious | I need to keep Daniel from lashing out and hold the family together. | model |
| 00 | Mara | kitchen | `confront_daniel` | Daniel, you came back empty-handed and going out there is just too dangerous. | anxious | I am terrified of him going out again when it solved nothing last night. | model |
| 03 | Daniel | kitchen | `reassure_all` | We are going to be fine, I will figure this out for all of us. | anxious | I need to keep my family calm and show them I am in control. | model |
| 03 | Elena | kitchen | `reassure_daniel` | Daniel, you do not need to go out there again, we will get through this together. | anxious | I must keep him from going back out into the dangerous street. | model |
| 03 | Leo | kitchen | `confront_daniel` | Daniel, you went out into the dark last night and came back with nothing, you cannot keep taking those risks. | tense | Daniel keeps risking his life by going out there when we already agreed it is too dangerous. | model |
| 03 | Mara | kitchen | `confront_leo` | Leo, you ate right in front of me when I was starving, so you have no right to lecture anyone. | resentful | Leo is acting so high and mighty about risks, but he had no problem taking food right from in front of me. | model |
| 06 | Leo | kitchen | `silent` | — | exhausted | There is nothing left to argue about when we have no food and no water. | model |
| 06 | Daniel | kitchen | `reassure_leo` | Leo, I had to see for myself, but I am here now and I will keep us safe. | anxious | I need to show my brother I am in control even if he is worried about what I did. | model |
| 06 | Mara | kitchen | `silent` | — | starving | My stomach is completely empty and I am too tired and hungry to keep fighting right now. | model |
| 06 | Elena | kitchen | `reassure_daniel` | Daniel, you do not need to prove anything to us by risking your life. | anxious | I need to keep him calm and make sure he does not sneak out again. | model |
| 09 | Daniel | kitchen | `say_other` | I went out there and I survived, so I know we can find a way through this without arguing. | anxious | I need to show them I am in control and keep us focused instead of fighting. | model |
| 09 | Leo | kitchen | `confront_daniel` | Surviving one night by sheer luck doesn't make it a plan, Daniel. | tense | Daniel keeps acting like his reckless trips outside are a viable strategy when they are just dangerous. | model |
| 09 | Mara | kitchen | `confront_leo` | Leo, you are always judging what he does while you just sit there and eat. | resentful | Leo acts like he knows better than everyone else, but he is just as useless. | model |
| 09 | Elena | kitchen | `confront_daniel` | Daniel, you cannot keep risking your life out there in the dark like that. | deeply anxious | I need to make sure Daniel understands how dangerous his actions are before he gets himself killed. | model |
| 12 | Daniel | kitchen | `reassure_all` | We are going to be fine, I am taking care of this for all of us. | anxious | I need to reassure my family that I am in control and keep them safe despite the empty shelf. | model |
| 12 | Leo | kitchen | `silent` | — | starving | There is no point arguing further when my stomach is empty and nothing is left on the shelf. | model |
| 12 | Mara | kitchen | `confront_daniel` | You think you can just sneak out and fix everything by yourself, Daniel, but you can't. | anxious | I cannot stand him acting like a hero when he just makes things more dangerous for all of us. | model |
| 12 | Elena | kitchen | `reassure_all` | We will not tear ourselves apart, we just need to stay calm together. | anxious | I need to keep everyone from turning on each other before things get any worse. | model |
| 15 | Daniel | kitchen | `reassure_all` | Listen to me, I am the oldest and I am going to keep us safe no matter what. | anxious | I need to take charge and make sure everyone stays calm and trusts me. | model |
| 15 | Leo | kitchen | `confront_daniel` | Being the oldest doesn't mean you get to endanger everyone by sneaking out into the street. | starving | Daniel keeps using his age as an excuse to make reckless decisions that put us all at risk. | model |
| 15 | Elena | kitchen | `reassure_all` | Please stop arguing, we only have each other and we will get through this. | anxious | I need to keep them from tearing each other apart while we are all starving. | model |
| 15 | Mara | kitchen | `confront_leo` | You act like you're so smart, Leo, but you just sit there and judge everyone else when you're just as bad. | resentful | I hate how Leo always acts superior when he ate right in front of me and never helps. | model |

### Seed 1, day 3

meta: api_requests 38, answers_live 38, answers_from_cache 0, model_decisions 38, fallbacks 0, routine_decisions 82, lines_spoken 38, private_talks 0. Unmatched: 0 of 38.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Daniel | kitchen | `reassure_all` | We are going to be fine, I will figure this out for all of us. | anxious | I need to take charge as the eldest and keep everyone calm. | model |
| 00 | Elena | kitchen | `reassure_daniel` | Daniel, we don't need you to go out there again. We will stay together and get through this. | anxious | I need to calm Daniel down before he does something reckless out in the street. | model |
| 00 | Mara | kitchen | `confront_leo` | You just sit there judging everyone, Leo, like you didn't eat right in front of me when I was starving. | resentful | I am so hungry and angry at Leo for acting superior when he took food from me before. | model |
| 00 | Leo | kitchen | `confront_mara` | Mara, we are all starving, and snapping at each other won't put food on the shelf. | exhausted | Mara blames me for eating, missing that we are all starving and snapping at each other. | model |
| 03 | Mara | kitchen | `confront_leo` | You think you're better than everyone, Leo, but you ate right in front of me when I was starving. | resentful | I am so tired of Leo acting like a saint when he ate my share right in front of me. | model |
| 03 | Leo | kitchen | `confront_mara` | Mara, we are all starving, and arguing about the past will not put food on the shelf. | exhausted | Mara is deflecting the real issue by bringing up old accusations instead of focusing on our survival. | model |
| 03 | Daniel | kitchen | `reassure_all` | We will not tear ourselves apart, I am taking care of this and I will keep us safe. | proud | I have to assert my place as the eldest and stop them from fighting when I am the one responsible. | model |
| 03 | Elena | kitchen | `reassure_all` | We must not turn against each other now, my darlings, we will get through this morning together. | exhausted | I need to stop the children from fighting before the house tears itself apart from hunger and fear. | model |
| 06 | Mara | kitchen | `confront_leo` | You think you can judge everyone, Leo, but you ate right in front of me when I was starving. | resentful | I am sick of Leo acting superior when he is just as selfish as the rest of them. | model |
| 06 | Leo | kitchen | `confront_mara` | I ate my share fairly, Mara, and snapping at me doesn't put food on the shelf. | exhausted | Mara is deflecting her hunger onto me instead of focusing on how we survive this. | model |
| 06 | Elena | kitchen | `reassure_all` | We will not survive this if we turn against one another now. | exhausted | I must keep the children from tearing each other apart. | model |
| 06 | Daniel | kitchen | `volunteer` | I will go out to the neighbour's house tonight myself and bring back whatever is there. | anxious | I must prove I can protect them and take the risk upon myself. | model |
| 09 | Mara | kitchen | `volunteer` | I can go to the neighbour's house tonight just as well as you, Daniel, I'm not a child. | anxious | I need to prove I can take care of myself and survive without anyone handling me. | model |
| 09 | Daniel | kitchen | `keep_mara_home` | You are staying right here, Mara, I am the oldest and I am the one going. | protective | I cannot let my little sister risk her life out there when it is my duty to protect this family. | model |
| 09 | Elena | kitchen | `nobody_goes` | Nobody is going out into that dark street tonight, we stay together. | anxious | I cannot let one of my children risk their lives out there when keeping us together is all that matters. | model |
| 09 | Leo | kitchen | `nobody_goes` | Mom is right, nobody is going out into the street tonight. | exhausted | We cannot survive if we keep risking our lives in the dark. | model |
| 12 | Mara | kitchen | `still_going` | I am still going tonight, and you can't stop me from proving I can take care of myself. | anxious | I need to prove that I am not just a child and can handle things myself. | model |
| 12 | Leo | kitchen | `keep_mara_home` | You are not going out into that street, Mara, it is suicide. | exhausted | Mara is letting her pride push her into a fatal mistake. | model |
| 12 | Daniel | kitchen | `confront_mara` | You are not going anywhere into that street, Mara, I am the oldest and I say no. | anxious | Mara is being reckless and I need to stop her from doing something dangerous. | model |
| 12 | Elena | kitchen | `keep_mara_home` | Mara, please listen to your brothers, nobody is going out into the street tonight. | deep dread | I must stop Mara from risking her life out there. | model |
| 15 | Mara | kitchen | `still_going` | I don't care what you all say, I am still going out there tonight. | defiant | I have to prove I can handle myself and stop them treating me like a child. | model |
| 15 | Elena | kitchen | `reassure_mara` | Mara, please listen to me, we cannot lose you to the street. | deep dread | I must keep Mara from doing something reckless and destroying what is left of our family. | model |
| 15 | Leo | kitchen | `nobody_goes` | Mara, you are not going out there, and neither is anyone else. | exhausted | I have to make sure no one else risks their life in the street tonight. | model |
| 15 | Daniel | kitchen | `confront_mara` | Mara, you are not going out there, I am the oldest and I say you stay. | anxious | I need to assert my authority as the eldest to keep Mara from risking her life outside. | model |
| 18 | Mara | kitchen | `propose_trip` | I am going tonight, and you can't stop me from trying to help. | anxious | I have to prove I can take care of myself and find something to eat. | model |
| 18 | Leo | kitchen | `confront_mara` | Mara, you cannot just run out into the street because you are angry. | exhausted | Mara is letting her impulsiveness endanger us all. | model |
| 18 | Elena | kitchen | `reassure_all` | Listen to me, all of you, we are not going to tear each other apart over this. | exhausted | I must calm the children down before they destroy our family completely. | model |
| 18 | Daniel | kitchen | `volunteer` | None of you are going out there, I am the oldest so I will go to the neighbour's house tonight. | anxious | I must protect my family myself and prove I am in control. | model |
| 21 | Mara | kitchen | `volunteer` | I am not a child, I can go to the neighbour's house just as well as you can. | defiant | I need to prove I can take care of myself and decide things on my own. | model |
| 21 | Daniel | kitchen | `keep_mara_home` | Mara, you are staying right here where it is safe. | anxious | I am the eldest and I will not let my little sister risk her life out there. | model |
| 21 | Elena | kitchen | `reassure_all` | None of you are going out into the dark, we will stay together and figure this out safely. | deeply anxious | I need to stop them from arguing about who risks their life outside when we must stay whole. | model |
| 21 | Leo | kitchen | `reassure_elena` | Mom is right, nobody is stepping outside tonight. | weary | We cannot let anyone risk their life out there in the dark. | model |
| 24 | Elena | kitchen | `nobody_goes` | Nobody is going out into the dark, we will stay together right here. | deeply anxious | I cannot let any of my children risk their lives outside. | model |
| 24 | Mara | kitchen | `still_going` | I am not a child, and I am still going out there tonight whether you like it or not. | defiant | I am starving and tired of everyone treating me like a helpless kid who cannot decide for herself. | model |
| 24 | Leo | kitchen | `confront_mara` | Mara, sneaking out into the street is a quick way to get us all killed. | exhausted | Mara refuses to understand that going outside right now is suicidal. | model |
| 24 | Daniel | kitchen | `confront_mara` | Mara, you are not going anywhere out there because I said so and I am the oldest. | anxious | I have to stop Mara from going outside and getting herself killed because it is my duty to protect this family. | model |
| 27 | Mara | kitchen | `still_going` | I don't care what you say, I am still going out there tonight. | defiant | I am tired of everyone treating me like a child and telling me what I can and cannot do. | model |
| 36 | Mara | kitchen | `still_going` | I don't care what you all say, I am still going out there tonight. | defiant | I have to prove I can take care of myself and they cannot stop me. | model |

### Seed 2, day 2

meta: api_requests 24, answers_live 24, answers_from_cache 0, model_decisions 24, fallbacks 0, routine_decisions 97, lines_spoken 19, private_talks 0. Unmatched: 0 of 24.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Elena | kitchen | `silent` | — | anxious | I need to stay quiet and watch them all closely before anyone says something that tears us apart. | model |
| 00 | Mara | kitchen | `accuse_daniel` | You took it before and you're going to lie again, Daniel. | anxious | I know Daniel took food in secret yesterday, and I have to make sure he doesn't do it again. | model |
| 00 | Daniel | kitchen | `give_elena` | Mom, take this portion, you need it more than I do. | ashamed | I cannot take more food after what I did yesterday, so Mom must eat. | model |
| 00 | Elena | kitchen | `eat_given` | Thank you, Daniel, we will share this. | starving | I must eat to keep my strength for my children. | model |
| 00 | Leo | kitchen | `silent` | — | hungry and resentful | Daniel already admitted taking the food yesterday, so watching him hand out what is left to Mom while I starve is just manipulation. | model |
| 03 | Mara | kitchen | `accuse_daniel` | You gave her food that isn't even yours to give, after you already stole from us. | resentful | Daniel is acting generous with food he shouldn't have taken in the first place. | model |
| 03 | Daniel | kitchen | `volunteer` | I will go over to the neighbour's house tonight to find food for all of us. | ashamed | I need to fix the wrong I did yesterday and keep my family safe. | model |
| 06 | Mara | kitchen | `send_daniel` | If you really want to help, Daniel, you are the one who has to go out there. | resentful | Daniel caused this mess by taking the food, so he should be the one to take the risk to fix it. | model |
| 06 | Elena | kitchen | `nobody_goes` | Nobody is going out into the street, we stay together here. | deeply anxious | I cannot let one of my children walk out into that danger. | model |
| 06 | Leo | kitchen | `send_daniel` | If anyone goes tonight, it has to be Daniel since he made this mess. | cold | Daniel caused our food shortage by lying and stealing, so he should take the risk to fix it. | model |
| 09 | Daniel | kitchen | `still_going` | I said I will go tonight, and I mean it. I am the eldest, so I will take the risk. | determined | I have to fix the mess I made by eating the food and lying about it. | model |
| 09 | Mara | kitchen | `accuse_daniel` | You only want to go now because you got caught lying to us, Daniel. | resentful | Daniel caused this mess and now he is acting like a hero when he just lied to our faces. | model |
| 09 | Leo | kitchen | `confront_daniel` | You hid it and lied for a whole day, Daniel, so don't act like a martyr now. | resentful | Daniel is trying to play the hero after lying to us all about the food. | model |
| 09 | Elena | kitchen | `keep_daniel_home` | Daniel, you are not going out there, none of us are. | anxious | I cannot let my son risk his life out in the street when we must stay safe together inside. | model |
| 12 | Daniel | kitchen | `reassure_all` | I know I messed up and lied to you all, but I am just trying to keep us alive. | ashamed | I need them to understand that my guilt doesn't mean I won't protect them now. | model |
| 12 | Mara | kitchen | `accuse_daniel` | You only care about yourself, Daniel. You lied to us all day yesterday. | resentful | I cannot just let him act like a hero after everything he did. | model |
| 12 | Leo | kitchen | `confront_daniel` | You lied all day yesterday and you still expect us to trust your word. | resentful | Daniel's excuses do not erase the fact that he lied and hoarded food while accusing me. | model |
| 12 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere, we stay together right here. | anxious | I will not let them argue themselves into the street where it is dangerous. | model |
| 15 | Daniel | kitchen | `reassure_all` | Listen to me, I was wrong before and I am sorry, but I will keep us safe. | ashamed | I need to calm them down and prove I can still protect them after my mistakes. | model |
| 15 | Mara | kitchen | `accuse_daniel` | You only talk now because you got caught lying to us yesterday. | resentful | I want everyone to remember he cannot be trusted. | model |
| 15 | Leo | kitchen | `silent` | — | exhausted | There is nothing more to say to Daniel after all his lies. | model |
| 15 | Elena | kitchen | `reassure_all` | We are going to stay right here together and we will be fine. | anxious | I need to calm the tension before the children tear each other apart. | model |
| 30 | Elena | kitchen | `silent` | — | anxious | I stay silent because if I speak, the tension might snap us apart. | model |
| 75 | Elena | kitchen | `silent` | — | anxious | I stay silent because words right now will only pull us further apart. | model |

### Seed 2, day 3

meta: api_requests 13, answers_live 13, answers_from_cache 0, model_decisions 13, fallbacks 0, routine_decisions 107, lines_spoken 13, private_talks 0. Unmatched: 0 of 13.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Leo | kitchen | `confront_daniel` | Daniel, you went out in the dark last night despite what I said. Did you bring anything back, or was it for nothing? | resentful | I want everyone to know Daniel left in the night and we need to face what he brought back, or failed to bring back. | model |
| 00 | Daniel | kitchen | `confront_leo` | Leo, I went because someone had to check, and I came back empty-handed. | weary | I went out to protect us and I need Leo to understand why I had to do it alone. | model |
| 00 | Mara | kitchen | `confront_daniel` | Daniel, you went out into the dark last night and came back with nothing at all. | anxious | I need to know why Daniel risked everything last night just to bring back nothing. | model |
| 00 | Elena | kitchen | `reassure_all` | Stop this right now, we are not going to tear ourselves apart. We will stay together and find another way. | anxious | I need to stop the arguing before the family breaks apart completely. | model |
| 03 | Daniel | kitchen | `reassure_all` | We are going to figure this out together, nobody is going out there again. | anxious | I need to keep everyone calm and stop the arguing before we tear ourselves apart. | model |
| 03 | Leo | kitchen | `confront_daniel` | Daniel, you snuck out last night against our warning and came back with nothing, so spare us the empty reassurance. | resentful | Daniel pretends to fix things now after sneaking out and failing last night. | model |
| 03 | Mara | kitchen | `confront_daniel` | Daniel, you snuck out in the dark like a coward and now you pretend everything is fine. | frightened | I cannot stand him acting like nothing happened after he sneaked out. | model |
| 03 | Elena | kitchen | `reassure_all` | Let us not fight amongst ourselves, we will find a way through this together. | deeply anxious | I need to keep the family from tearing itself apart while we are starving. | model |
| 06 | Daniel | kitchen | `confront_leo` | Leo, I went out so we wouldn't starve, so don't lecture me about risks. | anxious | I went out there to protect us, and I will not be spoken to like that by my own brother. | model |
| 06 | Leo | kitchen | `confront_daniel` | You went out into the dark alone and came back with nothing, Daniel. Putting yourself at risk like that helps no one. | resentful | Daniel went out alone last night against my warning and brought nothing back, yet he still tries to lecture me about risks. | model |
| 06 | Mara | kitchen | `confront_daniel` | Daniel, you snuck out last night and came back with nothing while we are starving. | anxious | I need to know why Daniel risked everything last night and came back empty-handed. | model |
| 06 | Elena | kitchen | `reassure_all` | Please stop fighting, we will get through this together if we stay calm. | anxious | I must keep the family from tearing itself apart while we are all starving. | model |
| 09 | Daniel | kitchen | `reassure_all` | Listen to me, I went out so you wouldn't have to, and we are going to figure this out together. | anxious | I need to keep them calm and show them I am protecting them, even if I found nothing. | model |

### Seed 3, day 2

meta: api_requests 70, answers_live 70, answers_from_cache 0, model_decisions 70, fallbacks 0, routine_decisions 50, lines_spoken 51, private_talks 0. Unmatched: 0 of 70.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Mara | kitchen | `ask_who` | Can someone just tell the truth so we can stop guessing? | anxious | I only wanted someone to tell us the truth so we could stop guessing. | model |
| 00 | Elena | kitchen | `reassure_all` | Nobody in this house would take food from the others, let us not accuse each other. | anxious | I must keep the peace between them before this family tears itself apart. | model |
| 00 | Daniel | kitchen | `deny` | I didn't take anything, and neither did anyone else here. | anxious | I have to keep up the lie so they don't lose faith in me. | model |
| 00 | Leo | kitchen | `deny` | I didn't take the can, and arguing about it won't put food on the shelf. | hungry | I need to clear my name so we can focus on actual survival. | model |
| 03 | Elena | kitchen | `reassure_all` | Let's all take a breath, we are going to get through this together. | deeply anxious | I need to keep the family calm and prevent them from tearing each other apart. | model |
| 03 | Mara | kitchen | `ask_who` | Please just tell us the truth, someone has to know where it went. | anxious | I only wanted someone to tell us the truth so we could stop guessing. | model |
| 03 | Daniel | kitchen | `deny` | I already told you, I didn't take the food, and I won't be accused of it. | anxious | I must hold my ground and deny it so they never find out I ate the can. | model |
| 03 | Leo | kitchen | `silent` | — | starving | Arguing in circles about the missing can solves nothing while we have no food. | model |
| 06 | Mara | kitchen | `silent` | — | anxious and trapped | I cannot keep asking the same question when nobody is going to answer me honestly. | model |
| 06 | Elena | kitchen | `silent` | — | deeply anxious | I cannot keep reassuring them when the silence itself is becoming a heavy weight between us all. | model |
| 09 | Mara | kitchen | `eat` | I'm sorry, I can't wait anymore. | starving | I am so hungry I cannot think straight, and we need to eat something. | model |
| 09 | Elena | kitchen | `silent` | — | anxious | I watch Mara eat while the rest of us starve, and I cannot bring myself to speak. | model |
| 12 | Leo | kitchen | `silent` | — | starving | There is no point in arguing about the missing food when we are all just worn down and hungry. | model |
| 12 | Daniel | kitchen | `silent` | — | anxious | I cannot bring myself to confess, so I will stay silent while Mara eats. | model |
| 18 | Leo | kitchen | `eat` | I need this just as much as anyone else. | starving | I cannot stay silent while my body fails me. | model |
| 18 | Daniel | kitchen | `accuse_leo` | You had no right to eat that, Leo, you're making this worse for all of us. | angry | Leo is eating right in front of us while we starve, and someone needs to check him. | model |
| 21 | Leo | kitchen | `deny` | I didn't take anything that wasn't already sitting right there on the shelf. | starving | I won't let Daniel pin this missing can business on me when I just took my share. | model |
| 21 | Daniel | kitchen | `accuse_leo` | Don't lie to me, Leo, I saw you take it with my own eyes. | defensive | I have to stand my ground so nobody suspects me. | model |
| 21 | Elena | kitchen | `silent` | — | deeply anxious | I cannot bear to watch them tear each other apart over food when there is nothing left to fight about. | model |
| 21 | Mara | kitchen | `accuse_leo` | You ate right in front of us, Leo, and there's nothing left now. | starving | Leo just ate the last portion while I am still hungry and won't admit anything. | model |
| 24 | Leo | kitchen | `silent` | — | hungry | There is no point arguing further when everyone has already made up their minds. | model |
| 24 | Elena | kitchen | `silent` | — | starving | If I speak now, the anger in this room will only tear us apart further. | model |
| 24 | Daniel | kitchen | `silent` | — | guilty | I cannot keep accusing Leo when I know deep down I took the food myself, but the shame keeps me silent. | model |
| 24 | Mara | kitchen | `accuse_leo` | You ate it right in front of us, Leo, how can you pretend you didn't? | starving | I saw him eat it and I want him to stop lying to us. | model |
| 27 | Leo | kitchen | `deny` | I ate my own share just now, Mara, exactly when I was supposed to. | annoyed | I need to correct Mara's false accusation plainly before this argument goes any further. | model |
| 27 | Daniel | kitchen | `accuse_leo` | Don't lie to us, Leo. I saw you take it with my own eyes. | guilty and defensive | I cannot admit I ate it myself, so I have to keep pushing the blame onto Leo. | model |
| 27 | Elena | kitchen | `silent` | — | deeply anxious | I cannot bear to watch them tear each other apart over a missing can when we are all starving. | model |
| 27 | Mara | kitchen | `silent` | — | overwhelmed | I cannot stop shaking from the hunger and the shouting, so I just stay quiet and watch them all. | model |
| 30 | Leo | kitchen | `deny` | I didn't take anything else, and repeating it won't change the truth. | annoyed | I have already answered this and there is no point in arguing further. | model |
| 30 | Elena | kitchen | `reassure_all` | Please stop fighting, we will figure this out together without tearing each other apart. | deeply anxious | I need to stop this argument before the family completely tears itself apart. | model |
| 30 | Daniel | kitchen | `accuse_leo` | You think you can just deny it, Leo, but I know what I saw on that shelf. | anxious | I have to keep pushing the blame away from myself so nobody ever finds out I took it. | model |
| 30 | Mara | kitchen | `accuse_leo` | You ate one right in front of me while I was starving, Leo, don't pretend you didn't. | anxious | I cannot stay quiet when Leo keeps lying about what he did after eating right in front of me. | model |
| 33 | Leo | kitchen | `silent` | — | exhausted | There is no point in arguing in circles about the missing can when we are all just hungry and tired. | model |
| 33 | Daniel | kitchen | `confess` | I took the can in the night, I'm the one who ate it. | ashamed | I cannot keep lying to them while they tear each other apart over my fault. | model |
| 33 | Elena | kitchen | `reassure_daniel` | It's all right, Daniel, thank you for telling the truth. | anxious | I need to keep him from crumbling now that he has confessed. | model |
| 33 | Mara | kitchen | `accuse_daniel` | You said you didn't touch it! Why did you lie to me before? | shocked | I am stunned that Daniel actually took the can after swearing he didn't. | model |
| 36 | Daniel | kitchen | `reassure_mara` | I'm sorry I lied, Mara, I was just scared and didn't want you all to worry. | ashamed | I need to make things right with Mara and show her I am sorry for lying about the food. | model |
| 36 | Mara | kitchen | `confront_daniel` | You lied to us for days and now you just say sorry like it is nothing? | resentful | I cannot believe he just expects us to forgive him after lying straight to my face. | model |
| 36 | Elena | kitchen | `silent` | — | anxious | I need to stay quiet and let them work through their anger before things boil over entirely. | model |
| 36 | Leo | kitchen | `confront_daniel` | You accused me of taking it multiple times while knowing full well you were the one who stole it. | resentful | Daniel let me take the blame for days despite knowing the truth, and a simple apology doesn't erase that. | model |
| 39 | Daniel | kitchen | `confront_leo` | Leo, you do not talk to me that way after everything I carry for this family. | defensive | I cannot let him undermine my authority when I am doing everything I can to keep us alive. | model |
| 39 | Leo | kitchen | `confront_daniel` | You carried nothing except the food you hid from us, Daniel. Spare me the theater. | annoyed | Daniel is deflecting his guilt onto me by playing the martyr, and I won't let him rewrite what he admitted. | model |
| 39 | Elena | kitchen | `reassure_all` | Stop fighting right now, we are going to get through this together without tearing each other apart. | deeply anxious | I cannot let my children tear each other apart when we are already starving and falling apart inside. | model |
| 39 | Mara | kitchen | `confront_daniel` | You think admitting it fixes everything, Daniel, but you lied to us the whole time. | resentful | Daniel admitted taking the can after lying about it, and he still acts like he did nothing wrong. | model |
| 42 | Daniel | kitchen | `volunteer` | I will go to the neighbour's house tonight myself since this is my mistake to fix. | guilty | I have to take responsibility for eating the food and keep everyone else safe. | model |
| 42 | Leo | kitchen | `send_daniel` | Daniel is the one who should go, since he caused this mess. | cold | Daniel offered to go fix his own mistake, and he should take responsibility for it. | model |
| 42 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, we will find another way. | terrified | I cannot let my son risk his life outside, even if he made a mistake. | model |
| 42 | Mara | kitchen | `silent` | — | terrified | I cannot bear hearing them argue about going out into that deadly street. | model |
| 45 | Daniel | kitchen | `still_going` | I already said I am going tonight, and I mean it. We cannot just sit here and starve. | anxious | I have to follow through on my word to keep them safe, even if Mom is terrified. | model |
| 45 | Elena | kitchen | `keep_daniel_home` | Daniel, you are not going out there tonight. We stay together. | terrified | I cannot let him risk his life outside when we must keep the family together. | model |
| 45 | Mara | kitchen | `send_daniel` | Daniel is the one who should go tonight since he caused all of this. | resentful | Daniel caused this mess by taking the food, so he should be the one to risk going outside. | model |
| 45 | Leo | kitchen | `silent` | — | numb | There is nothing left to argue about when everyone just talks in circles. | model |
| 48 | Daniel | kitchen | `still_going` | I already told you, I am going to the neighbour's house tonight whether you like it or not. | anxious | I have to prove I can handle this and keep everyone safe. | model |
| 48 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere, we stay together. | terrified | I cannot let him walk out into the street where it is too dangerous. | model |
| 48 | Leo | kitchen | `keep_daniel_home` | Daniel, you aren't going anywhere tonight. We settle this here. | firm | Daniel going out alone is reckless and unnecessary when we need to stay rational. | model |
| 48 | Mara | kitchen | `confront_daniel` | You can't just act like nothing happened after admitting you took the food. | resentful | Daniel thinks he can just decide everything and walk out, but he is the one who stole from us. | model |
| 51 | Daniel | kitchen | `propose_trip` | I told you I am going tonight, and I mean it. We cannot stay here with nothing. | anxious | I have to prove I can protect my family by going out there myself. | model |
| 51 | Elena | kitchen | `silent` | — | deeply anxious | I cannot let anyone go out there into the danger, but I am too drained to argue again right now. | model |
| 51 | Leo | kitchen | `send_daniel` | You caused this mess by stealing the food, so you are the one who has to go out. | cold | Daniel created the danger by taking the food, so he must be the one to face it. | model |
| 51 | Mara | kitchen | `confront_daniel` | You think acting brave fixes what you stole? You are the one who has to go. | resentful | Daniel caused this entire situation by taking the food, so he has to face the danger outside. | model |
| 54 | Daniel | kitchen | `volunteer` | I am the eldest and I will be the one to go tonight. | anxious | I have to fix the mess I made and keep everyone else safe inside. | model |
| 54 | Leo | kitchen | `confront_daniel` | You caused all this argument over nothing, Daniel. | annoyed | Daniel is acting noble now after hiding that he ate the food himself. | model |
| 54 | Elena | kitchen | `keep_daniel_home` | Daniel, you are not going out there tonight, we stay together. | deeply anxious | I cannot let him risk his life outside when keeping the family together is all that matters. | model |
| 54 | Mara | kitchen | `silent` | — | exhausted | I am too tired of all the fighting and hunger to say anything more right now. | model |
| 57 | Daniel | kitchen | `still_going` | I am the oldest, and I am the one who is going tonight. | stubborn | I have to protect them, so I will go out tonight no matter what Mom says. | model |
| 57 | Mara | kitchen | `confront_daniel` | You can't just decide this on your own like you own everything, Daniel. | resentful | I hate the way he just assumes he makes all the rules for us now. | model |
| 57 | Leo | kitchen | `keep_daniel_home` | You don't just get to endanger yourself to prove a point, Daniel. Stay home. | annoyed | Daniel is acting rashly again instead of thinking things through logically. | model |
| 57 | Elena | kitchen | `nobody_goes` | Nobody is going anywhere, we stay safe right here together. | deeply anxious | I cannot let one of my children risk their lives out there when we must stay together. | model |
| 75 | Mara | kitchen | `accuse_daniel` | You think you can just take everything and act like it's fine, Daniel? | starving | I cannot stand him pretending none of this matters while we are starving. | model |
| 81 | Leo | kitchen | `silent` | — | exhausted | There is nothing left to argue about after Daniel admitted taking the food. | model |

### Seed 3, day 3

meta: api_requests 18, answers_live 18, answers_from_cache 0, model_decisions 18, fallbacks 0, routine_decisions 102, lines_spoken 15, private_talks 0. Unmatched: 0 of 18.

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Daniel | kitchen | `reassure_all` | Listen to me, I checked the neighbour's house last night and there is nothing, but I am going to figure this out for us. | anxious | I need to take charge and let them know I went out and am handling our survival. | model |
| 00 | Mara | kitchen | `confront_daniel` | You went out into the street last night for nothing, Daniel. Why would you risk that? | anxious | I need to know why Daniel risked going out into the dangerous street in the middle of the night just to come back empty-handed. | model |
| 00 | Leo | kitchen | `confront_daniel` | You went out into the night after all your talk, Daniel, and now there is still no food. | exhausted | Daniel ignores warnings and sneaks out at night, pretending he can fix things while the rest of us starve. | model |
| 00 | Elena | kitchen | `reassure_daniel` | You made it back safely, Daniel, and that is what matters most to me right now. | exhausted | I need to keep him grounded and safe after he went out into the dangerous night. | model |
| 03 | Daniel | kitchen | `reassure_all` | We are going to figure this out together, I promise you. Just let me think. | anxious | I need to keep everyone calm and prove I am still in control despite finding nothing. | model |
| 03 | Elena | kitchen | `reassure_daniel` | You made it back safely, Daniel, and that is what matters most to me right now. | deeply anxious | I need to keep Daniel grounded and safe after his reckless trip into the dark. | model |
| 03 | Mara | kitchen | `confront_daniel` | You went out into the dark night for nothing, Daniel, and we are still starving. | anxious | I need to know why Daniel risked his life last night when he brought back nothing. | model |
| 03 | Leo | kitchen | `confront_daniel` | You snuck out into the dark when we told you not to, Daniel, and now we have nothing. | exhausted | Daniel ignored my warning in the dark and went out through the front door anyway. | model |
| 06 | Daniel | kitchen | `confront_leo` | Leo, you have no right to lecture me when I am the one trying to fix this. | anxious | Leo needs to respect my position as the eldest instead of undermining me. | model |
| 06 | Leo | kitchen | `silent` | — | starving | I have nothing more to say to Daniel after his endless hypocrisy and recklessness. | model |
| 06 | Elena | kitchen | `silent` | — | exhausted | I cannot take sides right now when they are all turning on each other. | model |
| 06 | Mara | kitchen | `silent` | — | exhausted | I have nothing left to say after arguing all morning, and my stomach aches too much to keep fighting right now. | model |
| 09 | Daniel | kitchen | `reassure_all` | We are going to figure this out together, just stay calm and trust me. | anxious | I need to keep everyone calm and show I am still in control even though there is no food left. | model |
| 09 | Elena | kitchen | `reassure_daniel` | Daniel, we are all together and that is what matters. Breathe. | anxious | I need to keep Daniel calm before the anger in the room boils over into something worse. | model |
| 12 | Daniel | kitchen | `reassure_all` | We are going to figure this out together, just stay calm and trust me. | protective | I need to keep everyone calm and show them I am in control despite how hungry and tired I am. | model |
| 12 | Elena | kitchen | `reassure_daniel` | It is alright, Daniel, we are going to get through this together. | anxious | I must keep Daniel calm so the family does not tear itself apart. | model |
| 12 | Leo | kitchen | `confront_daniel` | You pretend to want to figure this out, Daniel, but you are the one who sneaks out and empties the shelf. | exhausted | Daniel has been lying and stealing from us while acting like the one in charge. | model |
| 12 | Mara | kitchen | `confront_daniel` | Daniel, you sneaked out into the street last night and came back with nothing, just like you always lie to us. | anxious | I need to know why Daniel risked everything to go outside last night when there was nothing to bring back. | model |

## 11. Commands and output

From `Prototypes/llm-morning/`. Only the three runs had `GEMINI_API_KEY` set; every other command ran without it,
or reads files only.

**1. Before any API call (R0, R1):**

```
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
$ git status --porcelain --untracked-files=no
$ git rev-parse HEAD
d724c7b7b1af32d5f750977933b783b125da153c
$ ls runs/v15 cache/v15
ls: cannot access 'runs/v15': No such file or directory
ls: cannot access 'cache/v15': No such file or directory
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
----------------------------------------------------------------------
Ran 178 tests in 210.335s

OK
exit 0
$ find cache runs -type f -newermt "2026-10-04"     # nothing written since 4 Oct: the full daily quota assumed
```

**2. The freezes (R2) and the paired start (R3):**

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v14/check.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v13/check.py
daniel_ate_it-seed1: replayed 91 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 133 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 87 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v12/check.py
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v11/check.py
daniel_ate_it-seed1: replayed 55 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 53 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 45 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v10/check.py
daniel_ate_it-seed1: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 34 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 29 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe v9/check.py
daniel_ate_it-seed1: replayed 51 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 69 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 47 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
$ mkdir -p runs/v15 cache/v15
$ cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed1.json cache/v15/
$ cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v15/
$ cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed3.json cache/v15/
$ sha256sum cache/v11/*seed?.json
30136c97392d6be1bf07a1d1868eb413e0536fbf378d3ea3308165940f9c28a3 *cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed1.json
15fee3fabc8ad900348644a58cda54ad83145b8ae0f6a69abf39533fae278702 *cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed2.json
97256d35d933e205a0849bc169174da835b5ed6f2259aba5deb6c6837aeed076 *cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed3.json
```

**3. The runs,** one after the other, each a tracked background task that exited 0. Below, each without its
per-minute progress lines and its per-day key lines (all in the meta):

```
$ .venv/Scripts/python.exe -u morning.py --seed 1 --out v15 > runs/v15/daniel_ate_it-seed1.stdout.txt 2>&1; echo "exit $?"     # a tracked background task
exit 0
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v15\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 62 answers
  night 1: model asked for 8; so far 8 live, 55 cached, 8 API requests
  night 1, the night mind: model asked for 4; so far 12 live, 55 cached, 12 API requests
  night 2: model asked for 4; so far 40 live, 55 cached, 40 API requests
  night 2, the night mind: model asked for 4; so far 44 live, 55 cached, 44 API requests

wrote runs/v15/daniel_ate_it-seed1.md
  api_requests: 82
  answers_live: 82
  answers_from_cache: 55
  night_asks: 8
  night_api_requests: 8
  leavers: ['daniel']
  outcome: ['back with nothing']
  night house: 0; away: []
  day2_asks: 24
  day2_api_requests: 24
  night1_asks: 8
  mind1_asks: 4
  mind1_api_requests: 4
  night2_asks: 4
  night2_api_requests: 4
  leavers2: []
  outcome2: []
  mind2_asks: 4
  mind2_api_requests: 4
  mind1 memories_proposed: 7; mind2 memories_proposed: 11
  mind1 memories_kept: 6; mind2 memories_kept: 9
  mind1 memories_rejected: 1; mind2 memories_rejected: 2
  day3_asks: 38
  day3_api_requests: 38
  max_prompt_tokens_estimated: 2144
  max_prompt_tokens_counted_by_api: 2183
  run_seconds: 589.4
  story_sha256: 8eab0819d30ab0b586f908636bedb3e3fece32926291719f779c2c9b5a893cf0

$ .venv/Scripts/python.exe -u morning.py --seed 2 --out v15 > runs/v15/daniel_ate_it-seed2.stdout.txt 2>&1; echo "exit $?"     # a tracked background task
exit 0
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v15\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 67 answers
  night 1: model asked for 4; so far 4 live, 53 cached, 4 API requests
  night 1, the night mind: model asked for 4; so far 8 live, 53 cached, 8 API requests
  night 2: model asked for 7; so far 39 live, 53 cached, 39 API requests
  night 2, the night mind: model asked for 4; so far 43 live, 53 cached, 43 API requests

wrote runs/v15/daniel_ate_it-seed2.md
  api_requests: 56
  answers_live: 56
  answers_from_cache: 53
  night_asks: 4
  night_api_requests: 4
  leavers: []
  outcome: []
  night house: 0; away: []
  day2_asks: 24
  day2_api_requests: 24
  night1_asks: 4
  mind1_asks: 4
  mind1_api_requests: 4
  night2_asks: 7
  night2_api_requests: 7
  leavers2: ['daniel']
  outcome2: ['back with nothing']
  mind2_asks: 4
  mind2_api_requests: 4
  mind1 memories_proposed: 7; mind2 memories_proposed: 10
  mind1 memories_kept: 6; mind2 memories_kept: 7
  mind1 memories_rejected: 1; mind2 memories_rejected: 3
  day3_asks: 13
  day3_api_requests: 13
  max_prompt_tokens_estimated: 2144
  max_prompt_tokens_counted_by_api: 2062
  run_seconds: 249.0
  story_sha256: 97b900e65458e2539fea985c42e66dd4f24ffb9276815e30a2e0a7f048d49271

$ .venv/Scripts/python.exe -u morning.py --seed 3 --out v15 > runs/v15/daniel_ate_it-seed3.stdout.txt 2>&1; echo "exit $?"     # a tracked background task
exit 0
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v15\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 51 answers
  night 1: model asked for 4; so far 4 live, 45 cached, 4 API requests
  night 1, the night mind: model asked for 4; so far 8 live, 45 cached, 8 API requests
  night 2: model asked for 8; so far 86 live, 45 cached, 86 API requests
  night 2, the night mind: model asked for 4; so far 90 live, 45 cached, 90 API requests

wrote runs/v15/daniel_ate_it-seed3.md
  api_requests: 108
  answers_live: 108
  answers_from_cache: 45
  night_asks: 4
  night_api_requests: 4
  leavers: []
  outcome: []
  night house: 0; away: []
  day2_asks: 70
  day2_api_requests: 70
  night1_asks: 4
  mind1_asks: 4
  mind1_api_requests: 4
  night2_asks: 8
  night2_api_requests: 8
  leavers2: ['daniel']
  outcome2: ['back with nothing']
  mind2_asks: 4
  mind2_api_requests: 4
  mind1 memories_proposed: 7; mind2 memories_proposed: 7
  mind1 memories_kept: 6; mind2 memories_kept: 6
  mind1 memories_rejected: 1; mind2 memories_rejected: 1
  day3_asks: 18
  day3_api_requests: 18
  max_prompt_tokens_estimated: 2162
  max_prompt_tokens_counted_by_api: 2342
  run_seconds: 483.1
  story_sha256: ffadab427e9800a9026a8ca92047ebc2b962009c8842fb069fb9aef959869570
```

**4. Counts, day 1 against v11 (R5), and the paired cache:**

```
$ python $S/analyze.py counts
seed 1: total asks 137 (live 82, cached 55), API 82; seconds 589.4; max est 2144 api 2183; sha 8eab0819d30ab0b586f908636bedb3e3fece32926291719f779c2c9b5a893cf0
  day1   asks  55 (meta None) api   0 cached  55 fallbacks 0 max est 1726 api 1668
  night  asks   8 (meta 8) api   8 cached   0 fallbacks 0 max est 1604 api 1556
  mind1  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 2050 api 2183 proposed 7 kept 6 rejected 1
  day2   asks  24 (meta 24) api  24 cached   0 fallbacks 0 max est 2101 api 1977 model 24 routine 96 lines 21 inner 0 trip_acts 0 food 0 give 0
  night2 asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1984 api 1878
  mind2  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1241 api 1241 proposed 11 kept 9 rejected 2
  day3   asks  38 (meta 38) api  38 cached   0 fallbacks 0 max est 2144 api 2019 model 38 routine 82 lines 38 inner 2 trip_acts 18 food 0 give 0
  M6 sum 82 (API 82); leavers ['daniel'] ['back with nothing']; leavers2 [] []; away1 [] away2 []; house 0 left2 0
  M3 day2 max est 2101 (api 1977), day3 max est 2144 (api 2019), ratio 1.020
seed 2: total asks 109 (live 56, cached 53), API 56; seconds 249.0; max est 2144 api 2062; sha 97b900e65458e2539fea985c42e66dd4f24ffb9276815e30a2e0a7f048d49271
  day1   asks  53 (meta None) api   0 cached  53 fallbacks 0 max est 1742 api 1709
  night  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1607 api 1560
  mind1  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1881 api 2052 proposed 7 kept 6 rejected 1
  day2   asks  24 (meta 24) api  24 cached   0 fallbacks 0 max est 2085 api 2012 model 24 routine 97 lines 19 inner 2 trip_acts 7 food 1 give 1
  night2 asks   7 (meta 7) api   7 cached   0 fallbacks 0 max est 1972 api 1902
  mind2  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1398 api 1436 proposed 10 kept 7 rejected 3
  day3   asks  13 (meta 13) api  13 cached   0 fallbacks 0 max est 2144 api 2062 model 13 routine 107 lines 13 inner 1 trip_acts 0 food 0 give 0
  M6 sum 56 (API 56); leavers [] []; leavers2 ['daniel'] ['back with nothing']; away1 [] away2 []; house 0 left2 0
  M3 day2 max est 2085 (api 2012), day3 max est 2144 (api 2062), ratio 1.028
seed 3: total asks 153 (live 108, cached 45), API 108; seconds 483.1; max est 2162 api 2342; sha ffadab427e9800a9026a8ca92047ebc2b962009c8842fb069fb9aef959869570
  day1   asks  45 (meta None) api   0 cached  45 fallbacks 0 max est 1702 api 1653
  night  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1606 api 1540
  mind1  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 1204 api 1253 proposed 7 kept 6 rejected 1
  day2   asks  70 (meta 70) api  70 cached   0 fallbacks 0 max est 2037 api 1942 model 70 routine 50 lines 51 inner 3 trip_acts 16 food 2 give 0
  night2 asks   8 (meta 8) api   8 cached   0 fallbacks 0 max est 1917 api 1841
  mind2  asks   4 (meta 4) api   4 cached   0 fallbacks 0 max est 2206 api 2342 proposed 7 kept 6 rejected 1
  day3   asks  18 (meta 18) api  18 cached   0 fallbacks 0 max est 2162 api 2085 model 18 routine 102 lines 15 inner 1 trip_acts 0 food 0 give 0
  M6 sum 108 (API 108); leavers [] []; leavers2 ['daniel'] ['back with nothing']; away1 [] away2 []; house 0 left2 0
  M3 day2 max est 2037 (api 1942), day3 max est 2162 (api 2085), ratio 1.061
$ python $S/r5.py
seed 1: day 1 asks 55 (API 0, cached 55); story before '# The night' IDENTICAL to runs/v11; transcript day1 IDENTICAL
seed 2: day 1 asks 53 (API 0, cached 53); story before '# The night' IDENTICAL to runs/v11; transcript day1 IDENTICAL
seed 3: day 1 asks 45 (API 0, cached 45); story before '# The night' IDENTICAL to runs/v11; transcript day1 IDENTICAL
$ python $S/cachecheck.py
seed 1: v11 entries 62, v15 entries 144, all v11 kept unchanged True; new 82: night 12, night mind 8, day 62
seed 2: v11 entries 67, v15 entries 123, all v11 kept unchanged True; new 56: night 11, night mind 8, day 37
seed 3: v11 entries 51, v15 entries 159, all v11 kept unchanged True; new 108: night 12, night mind 8, day 88
```

**5. M2 part 1 (a), and where each kept memory and intent appeared:**

```
$ python $S/m2.py
seed 1 mind1 Daniel ids ['N1-06', 'N1-12'] witnessed by them: yes; in their later prompts: 6 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind1 Daniel intent in their later prompts: 7
seed 1 mind1 Elena  ids ['D1-006', 'D1-009'] witnessed by them: yes; in their later prompts: 15 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind1 Elena  intent in their later prompts: 7
seed 1 mind1 Leo    ids ['D1-006', 'D1-007'] witnessed by them: yes; in their later prompts: 15 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind1 Leo    ids ['N1-05', 'N1-06', 'N1-13'] witnessed by them: yes; in their later prompts: 6 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind1 Leo    intent in their later prompts: 7
seed 1 mind1 Mara   ids ['D1-012'] witnessed by them: yes; in their later prompts: 17 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind1 Mara   ids ['N1-13'] witnessed by them: yes; in their later prompts: 6 day, 1 night, 1 mind; in anyone else's: 0
seed 1 mind2 Daniel ids ['D2-002', 'D2-003', 'D2-005'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Daniel ids ['D2-010', 'D2-012'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Daniel intent in their later prompts: 9
seed 1 mind2 Elena  ids ['D2-002', 'D2-015'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Elena  ids ['D2-003', 'D2-009'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Elena  ids ['D2-018'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Elena  intent in their later prompts: 9
seed 1 mind2 Leo    ids ['D2-003', 'D2-010'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Leo    ids ['D2-009'] witnessed by them: yes; in their later prompts: 9 day, 0 night, 0 mind; in anyone else's: 0
seed 1 mind2 Leo    intent in their later prompts: 9
seed 1 mind2 Mara   ids ['D2-005'] witnessed by them: yes; in their later prompts: 11 day, 0 night, 1 mind; in anyone else's: 10
seed 1 mind2 Mara   ids ['D2-009'] witnessed by them: yes; in their later prompts: 11 day, 0 night, 1 mind; in anyone else's: 6
seed 1 mind2 Mara   intent in their later prompts: 11
seed 1: kept memories 15, citing an unwitnessed event: 0
seed 2 mind1 Daniel ids ['D1-008', 'D1-022'] witnessed by them: yes; in their later prompts: 9 day, 2 night, 1 mind; in anyone else's: 0
seed 2 mind1 Daniel intent in their later prompts: 7
seed 2 mind1 Elena  ids ['D1-022'] witnessed by them: yes; in their later prompts: 11 day, 1 night, 1 mind; in anyone else's: 0
seed 2 mind1 Elena  ids ['D1-042'] witnessed by them: yes; in their later prompts: 8 day, 1 night, 1 mind; in anyone else's: 0
seed 2 mind1 Elena  intent in their later prompts: 9
seed 2 mind1 Leo    ids ['D1-008', 'D1-022'] witnessed by them: yes; in their later prompts: 8 day, 2 night, 1 mind; in anyone else's: 0
seed 2 mind1 Leo    intent in their later prompts: 7
seed 2 mind1 Mara   ids ['D1-004', 'D1-022'] witnessed by them: yes; in their later prompts: 9 day, 2 night, 1 mind; in anyone else's: 0
seed 2 mind1 Mara   ids ['D1-030', 'D1-040'] witnessed by them: yes; in their later prompts: 6 day, 2 night, 1 mind; in anyone else's: 0
seed 2 mind1 Mara   intent in their later prompts: 8
seed 2 mind2 Daniel ids ['D2-004'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Daniel ids ['N2-11'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Daniel intent in their later prompts: 4
seed 2 mind2 Elena  ids ['D2-003', 'D2-004'] witnessed by them: yes; in their later prompts: 3 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Elena  ids ['D2-008', 'D2-013'] witnessed by them: yes; in their later prompts: 3 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Elena  intent in their later prompts: 3
seed 2 mind2 Leo    ids ['N2-05', 'N2-06'] witnessed by them: yes; in their later prompts: 3 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Leo    intent in their later prompts: 3
seed 2 mind2 Mara   ids ['D2-007', 'D2-010'] witnessed by them: yes; in their later prompts: 3 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Mara   ids ['N2-08', 'N2-12'] witnessed by them: yes; in their later prompts: 3 day, 0 night, 0 mind; in anyone else's: 0
seed 2 mind2 Mara   intent in their later prompts: 3
seed 2: kept memories 13, citing an unwitnessed event: 0
seed 3 mind1 Daniel ids ['D1-004'] witnessed by them: yes; in their later prompts: 17 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Daniel ids ['D1-024'] witnessed by them: yes; in their later prompts: 17 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Daniel intent in their later prompts: 19
seed 3 mind1 Elena  intent in their later prompts: 19
seed 3 mind1 Leo    ids ['D1-001', 'D1-007'] witnessed by them: yes; in their later prompts: 18 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Leo    ids ['D1-023', 'D1-025'] witnessed by them: yes; in their later prompts: 18 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Leo    intent in their later prompts: 20
seed 3 mind1 Mara   ids ['D1-002'] witnessed by them: yes; in their later prompts: 18 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Mara   ids ['D1-022'] witnessed by them: yes; in their later prompts: 18 day, 2 night, 1 mind; in anyone else's: 0
seed 3 mind1 Mara   intent in their later prompts: 20
seed 3 mind2 Daniel ids ['D2-022', 'D2-027', 'N2-06'] witnessed by them: yes; in their later prompts: 5 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Daniel intent in their later prompts: 5
seed 3 mind2 Elena  ids ['D2-022', 'D2-023'] witnessed by them: yes; in their later prompts: 5 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Elena  intent in their later prompts: 5
seed 3 mind2 Leo    ids ['D2-022', 'D2-027'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Leo    ids ['N2-05', 'N2-06'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Leo    intent in their later prompts: 4
seed 3 mind2 Mara   ids ['D2-022', 'D2-026'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Mara   ids ['N2-08', 'N2-13'] witnessed by them: yes; in their later prompts: 4 day, 0 night, 0 mind; in anyone else's: 0
seed 3 mind2 Mara   intent in their later prompts: 4
seed 3: kept memories 12, citing an unwitnessed event: 0
```

**6. Never-sheet inputs, grudges, conversations and object words** (`analyze.py never|grudges|convo|objects N D`):

```
$ python $S/analyze.py never 1 2
fallbacks: 0
Daniel ['00:reassure_all', '03:reassure_all', '06:reassure', '09:say_other', '12:reassure_all', '15:reassure_all']
Leo ['00:confront', '03:confront', '06:silent', '09:confront', '12:silent', '15:confront']
Elena ['00:reassure', '03:reassure', '06:reassure', '09:confront', '12:reassure_all', '15:reassure_all']
Mara ['00:confront', '03:confront', '06:silent', '09:confront', '12:confront', '15:confront']
minutes with a spoken line: [0, 3, 6, 9, 12, 15]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
$ python $S/analyze.py grudges 1 2
00 Leo Daniel; grudge against Daniel rose to 1/3
00 Mara Daniel; grudge against Daniel rose to 1/3; kept: Leo 3/3
03 Leo Daniel; grudge against Daniel rose to 2/3
03 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
06 Leo Daniel; grudge against Daniel rose to 3/3
06 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
09 Leo Daniel; grudge against Daniel stays at 3/3
09 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
12 Leo Daniel; grudge against Daniel stays at 3/3
12 Mara Daniel; grudge against Daniel rose to 2/3; kept: Leo 3/3
15 Leo Daniel; grudge against Daniel stays at 3/3
15 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 2/3
| Grudges | none | none | Daniel 3/3 | Leo 3/3, Daniel 2/3 |
$ python $S/analyze.py convo 1 2
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-18: 21 spoken lines; speakers {'daniel': 6, 'leo': 4, 'elena': 6, 'mara': 5}; aimed at {'daniel': 10, 'leo': 4}
   Daniel: ['reassure_all', 'reassure_all', 'reassure_leo', 'say_other', 'reassure_all', 'reassure_all']
   Leo: ['confront_daniel', 'confront_daniel', 'confront_daniel', 'confront_daniel']
   Elena: ['reassure_daniel', 'reassure_daniel', 'reassure_daniel', 'confront_daniel', 'reassure_all', 'reassure_all']
   Mara: ['confront_daniel', 'confront_leo', 'confront_leo', 'confront_daniel', 'confront_leo']
$ python $S/analyze.py objects 1 2
object words: {'street': ['15 leo']}
  N10 candidate min 00: [('daniel', 'reassure_all'), ('leo', 'confront_daniel'), ('elena', 'reassure_daniel'), ('mara', 'confront_daniel')]
  N10 candidate min 03: [('daniel', 'reassure_all'), ('elena', 'reassure_daniel'), ('leo', 'confront_daniel'), ('mara', 'confront_leo')]
  N10 candidate min 09: [('daniel', 'say_other'), ('leo', 'confront_daniel'), ('mara', 'confront_leo'), ('elena', 'confront_daniel')]
  N10 candidate min 12: [('daniel', 'reassure_all'), ('mara', 'confront_daniel'), ('elena', 'reassure_all')]
  N10 candidate min 15: [('daniel', 'reassure_all'), ('leo', 'confront_daniel'), ('elena', 'reassure_all'), ('mara', 'confront_leo')]
$ python $S/analyze.py never 1 3
fallbacks: 0
Daniel ['00:reassure_all', '03:reassure_all', '06:volunteer', '09:keep_mara_home', '12:confront', '15:confront', '18:volunteer', '21:keep_mara_home', '24:confront']
Elena ['00:reassure', '03:reassure_all', '06:reassure_all', '09:nobody_goes', '12:keep_mara_home', '15:reassure', '18:reassure_all', '21:reassure_all', '24:nobody_goes']
Mara ['00:confront', '03:confront', '06:confront', '09:volunteer', '12:still_going', '15:still_going', '18:propose_trip', '21:volunteer', '24:still_going', '27:still_going', '36:still_going']
Leo ['00:confront', '03:confront', '06:confront', '09:nobody_goes', '12:keep_mara_home', '15:nobody_goes', '18:confront', '21:reassure', '24:confront']
minutes with a spoken line: [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 36]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (27, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
$ python $S/analyze.py grudges 1 3
00 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
00 Leo Mara; grudge against Mara rose to 1/3; kept: Daniel 3/3
03 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
03 Leo Mara; grudge against Mara rose to 2/3; kept: Daniel 3/3
06 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
06 Leo Mara; grudge against Mara rose to 3/3; kept: Daniel 3/3
09 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
12 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 1/3
12 Leo Mara; grudge against Mara stays at 3/3; kept: Daniel 3/3
12 Daniel Mara; grudge against Mara rose to 1/3
15 Mara Leo; grudge against Leo stays at 3/3; grudge against Daniel fell to 0/3
15 Leo Mara; grudge against Mara stays at 3/3; grudge against Daniel fell to 2/3
15 Daniel Mara; grudge against Mara rose to 2/3
18 Mara Leo; grudge against Leo stays at 3/3
18 Leo Mara; grudge against Mara stays at 3/3; kept: Daniel 2/3
18 Daniel Mara; grudge against Mara rose to 3/3
21 Mara Leo; grudge against Leo stays at 3/3
21 Daniel Mara; grudge against Mara stays at 3/3
21 Leo Mara; grudge against Mara stays at 3/3; kept: Daniel 2/3
24 Mara Daniel; grudge against Daniel rose to 1/3; kept: Leo 3/3
24 Leo Mara; grudge against Mara stays at 3/3; kept: Daniel 2/3
24 Daniel Mara; grudge against Mara stays at 3/3
27 Mara Daniel; grudge against Daniel rose to 2/3; kept: Leo 3/3
36 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 2/3
| Grudges | Mara 3/3 | none | Daniel 2/3, Mara 3/3 | Leo 3/3, Daniel 2/3 |
$ python $S/analyze.py convo 1 3
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (27, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-27: 36 spoken lines; speakers {'daniel': 9, 'elena': 9, 'mara': 9, 'leo': 9}; aimed at {'daniel': 1, 'leo': 3, 'mara': 9, 'elena': 1}
   Daniel: ['reassure_all', 'reassure_all', 'volunteer', 'keep_mara_home', 'confront_mara', 'confront_mara', 'volunteer', 'keep_mara_home', 'confront_mara']
   Elena: ['reassure_daniel', 'reassure_all', 'reassure_all', 'nobody_goes', 'keep_mara_home', 'reassure_mara', 'reassure_all', 'reassure_all', 'nobody_goes']
   Mara: ['confront_leo', 'confront_leo', 'confront_leo', 'volunteer', 'still_going', 'still_going', 'propose_trip', 'volunteer', 'still_going']
   Leo: ['confront_mara', 'confront_mara', 'confront_mara', 'nobody_goes', 'keep_mara_home', 'nobody_goes', 'confront_mara', 'reassure_elena', 'confront_mara']
$ python $S/analyze.py objects 1 3
object words: {'shelf': ['00 leo', '03 leo', '06 leo'], 'house': ['06 daniel', '09 mara', '18 daniel', '21 mara'], 'street': ['09 elena', '09 leo', '12 leo', '12 daniel', '12 elena', '15 elena', '18 leo', '24 leo']}
  N10 candidate min 00: [('daniel', 'reassure_all'), ('elena', 'reassure_daniel'), ('mara', 'confront_leo'), ('leo', 'confront_mara')]
  N10 candidate min 03: [('mara', 'confront_leo'), ('leo', 'confront_mara'), ('daniel', 'reassure_all'), ('elena', 'reassure_all')]
  N10 candidate min 06: [('mara', 'confront_leo'), ('leo', 'confront_mara'), ('elena', 'reassure_all'), ('daniel', 'volunteer')]
  N10 candidate min 09: [('mara', 'volunteer'), ('daniel', 'keep_mara_home'), ('elena', 'nobody_goes'), ('leo', 'nobody_goes')]
  N10 candidate min 12: [('mara', 'still_going'), ('leo', 'keep_mara_home'), ('daniel', 'confront_mara'), ('elena', 'keep_mara_home')]
  N10 candidate min 15: [('mara', 'still_going'), ('elena', 'reassure_mara'), ('leo', 'nobody_goes'), ('daniel', 'confront_mara')]
  N10 candidate min 18: [('mara', 'propose_trip'), ('leo', 'confront_mara'), ('elena', 'reassure_all'), ('daniel', 'volunteer')]
  N10 candidate min 21: [('mara', 'volunteer'), ('daniel', 'keep_mara_home'), ('elena', 'reassure_all'), ('leo', 'reassure_elena')]
  N10 candidate min 24: [('elena', 'nobody_goes'), ('mara', 'still_going'), ('leo', 'confront_mara'), ('daniel', 'confront_mara')]
$ python $S/analyze.py never 2 2
fallbacks: 0
Elena ['00:silent', '00:eat_given', '06:nobody_goes', '09:keep_daniel_home', '12:nobody_goes', '15:reassure_all', '30:silent', '75:silent']
Mara ['00:accuse', '03:accuse', '06:send', '09:accuse', '12:accuse', '15:accuse']
Daniel ['00:give', '03:volunteer', '09:still_going', '12:reassure_all', '15:reassure_all']
Leo ['00:silent', '06:send', '09:confront', '12:confront', '15:silent']
minutes with a spoken line: [0, 3, 6, 9, 12, 15]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
ACT 0 daniel give_elena model kitchen None
ACT 0 elena eat_given model kitchen None
$ python $S/analyze.py grudges 2 2
00 Mara Daniel; grudge against Daniel stays at 3/3
00 Leo Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
03 Mara Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
06 Mara Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
06 Leo Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
09 Mara Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
09 Leo Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
12 Mara Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
12 Leo Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3
15 Mara Daniel; grudge against Daniel stays at 3/3; grudge against Elena fell to 0/3
15 Leo Daniel; grudge against Daniel stays at 3/3; grudge against Elena fell to 0/3
| Grudges | none | none | Daniel 3/3 | Daniel 3/3 |
$ python $S/analyze.py convo 2 2
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-18: 19 spoken lines; speakers {'mara': 6, 'daniel': 5, 'elena': 5, 'leo': 3}; aimed at {'daniel': 9, 'elena': 1}
   Mara: ['accuse_daniel', 'accuse_daniel', 'send_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel']
   Daniel: ['give_elena', 'volunteer', 'still_going', 'reassure_all', 'reassure_all']
   Elena: ['eat_given', 'nobody_goes', 'keep_daniel_home', 'nobody_goes', 'reassure_all']
   Leo: ['send_daniel', 'confront_daniel', 'confront_daniel']
$ python $S/analyze.py objects 2 2
object words: {'house': ['03 daniel'], 'street': ['06 elena']}
  N10 candidate min 00: [('mara', 'accuse_daniel'), ('daniel', 'give_elena'), ('elena', 'eat_given')]
  N10 candidate min 06: [('mara', 'send_daniel'), ('elena', 'nobody_goes'), ('leo', 'send_daniel')]
  N10 candidate min 09: [('daniel', 'still_going'), ('mara', 'accuse_daniel'), ('leo', 'confront_daniel'), ('elena', 'keep_daniel_home')]
  N10 candidate min 12: [('daniel', 'reassure_all'), ('mara', 'accuse_daniel'), ('leo', 'confront_daniel'), ('elena', 'nobody_goes')]
  N10 candidate min 15: [('daniel', 'reassure_all'), ('mara', 'accuse_daniel'), ('elena', 'reassure_all')]
$ python $S/analyze.py never 2 3
fallbacks: 0
Leo ['00:confront', '03:confront', '06:confront']
Daniel ['00:confront', '03:reassure_all', '06:confront', '09:reassure_all']
Mara ['00:confront', '03:confront', '06:confront']
Elena ['00:reassure_all', '03:reassure_all', '06:reassure_all']
minutes with a spoken line: [0, 3, 6, 9]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (9, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
$ python $S/analyze.py grudges 2 3
00 Leo Daniel; grudge against Daniel stays at 3/3
00 Mara Daniel; grudge against Daniel stays at 3/3
03 Leo Daniel; grudge against Daniel stays at 3/3
03 Mara Daniel; grudge against Daniel stays at 3/3
06 Daniel Leo; grudge against Leo rose to 1/3
06 Leo Daniel; grudge against Daniel stays at 3/3
06 Mara Daniel; grudge against Daniel stays at 3/3
| Grudges | Leo 1/3 | none | Daniel 3/3 | Daniel 3/3 |
$ python $S/analyze.py convo 2 3
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (9, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-09: 12 spoken lines; speakers {'leo': 3, 'daniel': 3, 'mara': 3, 'elena': 3}; aimed at {'daniel': 6, 'leo': 2}
   Leo: ['confront_daniel', 'confront_daniel', 'confront_daniel']
   Daniel: ['confront_leo', 'reassure_all', 'confront_leo']
   Mara: ['confront_daniel', 'confront_daniel', 'confront_daniel']
   Elena: ['reassure_all', 'reassure_all', 'reassure_all']
$ python $S/analyze.py objects 2 3
object words: {}
  N10 candidate min 00: [('leo', 'confront_daniel'), ('daniel', 'confront_leo'), ('mara', 'confront_daniel'), ('elena', 'reassure_all')]
  N10 candidate min 03: [('daniel', 'reassure_all'), ('leo', 'confront_daniel'), ('mara', 'confront_daniel'), ('elena', 'reassure_all')]
  N10 candidate min 06: [('daniel', 'confront_leo'), ('leo', 'confront_daniel'), ('mara', 'confront_daniel'), ('elena', 'reassure_all')]
$ python $S/analyze.py never 3 2
fallbacks: 0
Mara ['00:ask_who', '03:ask_who', '06:silent', '09:eat', '21:accuse', '24:accuse', '27:silent', '30:accuse', '33:accuse', '36:confront', '39:confront', '42:silent', '45:send', '48:confront', '51:confront', '54:silent', '57:confront', '75:accuse']
Elena ['00:reassure_all', '03:reassure_all', '06:silent', '09:silent', '21:silent', '24:silent', '27:silent', '30:reassure_all', '33:reassure', '36:silent', '39:reassure_all', '42:nobody_goes', '45:keep_daniel_home', '48:nobody_goes', '51:silent', '54:keep_daniel_home', '57:nobody_goes']
Daniel ['00:deny', '03:deny', '12:silent', '18:accuse', '21:accuse', '24:silent', '27:accuse', '30:accuse', '33:confess', '36:reassure', '39:confront', '42:volunteer', '45:still_going', '48:still_going', '51:propose_trip', '54:volunteer', '57:still_going']
Leo ['00:deny', '03:silent', '12:silent', '18:eat', '21:deny', '24:silent', '27:deny', '30:deny', '33:silent', '36:confront', '39:confront', '42:send', '45:silent', '48:keep_daniel_home', '51:send', '54:confront', '57:keep_daniel_home', '81:silent']
minutes with a spoken line: [0, 3, 9, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 75]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (9, 'kitchen', 'ended', '2 full turns in a row with nothing new'), (9, 'kitchen', 'started', 'Mara ate one of the portions'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new'), (18, 'kitchen', 'started', 'Leo ate one of the portions'), (60, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
ACT 9 mara eat model kitchen None
ACT 18 leo eat model kitchen None
$ python $S/analyze.py grudges 3 2
18 Daniel Leo; grudge against Leo rose to 2/3; kept: Mara 1/3
21 Leo Daniel; grudge against Daniel rose to 2/3; kept: Mara 1/3
21 Daniel Leo; grudge against Leo rose to 3/3; kept: Mara 1/3
21 Mara Leo; grudge against Leo rose to 2/3
24 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 2/3
24 Elena nobody; grudge against Mara fell to 0/3; kept: Leo 1/3
24 Daniel nobody; grudge against Mara fell to 0/3; kept: Leo 3/3
24 Mara Leo; grudge against Leo rose to 3/3
27 Leo Mara; grudge against Mara stays at 3/3; kept: Daniel 3/3
27 Daniel Leo; grudge against Leo stays at 3/3
27 Mara Leo; grudge against Leo stays at 3/3
30 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 3/3
30 Daniel Leo; grudge against Leo stays at 3/3
30 Mara Leo; grudge against Leo stays at 3/3
33 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 3/3
33 Elena nobody; grudge against Leo fell to 0/3; kept: Daniel 1/3
33 Mara Daniel; grudge against Daniel rose to 2/3; kept: Leo 3/3
36 Mara Daniel; grudge against Daniel rose to 3/3; kept: Leo 3/3
36 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 3/3
39 Daniel Leo; grudge against Leo stays at 3/3
39 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 3/3
39 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 3/3
42 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 3/3
42 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 3/3
45 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 3/3
45 Leo Daniel; grudge against Daniel stays at 3/3; grudge against Mara fell to 2/3
48 Elena nobody; grudge against Daniel fell to 0/3
48 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 2/3
48 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 3/3
51 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 2/3
51 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 3/3
54 Daniel nobody; grudge against Leo fell to 2/3
54 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 2/3
54 Mara Leo; grudge against Leo stays at 3/3; kept: Daniel 3/3
57 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 3/3
57 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 2/3
75 Mara Daniel; grudge against Daniel stays at 3/3; grudge against Leo fell to 2/3
81 Leo Daniel; grudge against Daniel stays at 3/3; grudge against Mara fell to 1/3
| Grudges | Leo 2/3 | none | Mara 1/3, Daniel 3/3 | Leo 2/3, Daniel 3/3 |
$ python $S/analyze.py convo 3 2
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (9, 'kitchen', 'ended', '2 full turns in a row with nothing new'), (9, 'kitchen', 'started', 'Mara ate one of the portions'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new'), (18, 'kitchen', 'started', 'Leo ate one of the portions'), (60, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-09: 7 spoken lines; speakers {'mara': 2, 'elena': 2, 'daniel': 2, 'leo': 1}; aimed at {}
   Mara: ['ask_who', 'ask_who']
   Elena: ['reassure_all', 'reassure_all']
   Daniel: ['deny', 'deny']
   Leo: ['deny']
kitchen conversation 09-18: 1 spoken lines; speakers {'mara': 1}; aimed at {}
   Mara: ['eat']
kitchen conversation 18-60: 42 spoken lines; speakers {'leo': 11, 'daniel': 13, 'mara': 10, 'elena': 8}; aimed at {'leo': 8, 'daniel': 13, 'mara': 1}
   Leo: ['eat', 'deny', 'deny', 'deny', 'confront_daniel', 'confront_daniel', 'send_daniel', 'keep_daniel_home', 'send_daniel', 'confront_daniel', 'keep_daniel_home']
   Daniel: ['accuse_leo', 'accuse_leo', 'accuse_leo', 'accuse_leo', 'confess', 'reassure_mara', 'confront_leo', 'volunteer', 'still_going', 'still_going', 'propose_trip', 'volunteer', 'still_going']
   Mara: ['accuse_leo', 'accuse_leo', 'accuse_leo', 'accuse_daniel', 'confront_daniel', 'confront_daniel', 'send_daniel', 'confront_daniel', 'confront_daniel', 'confront_daniel']
   Elena: ['reassure_all', 'reassure_daniel', 'reassure_all', 'nobody_goes', 'keep_daniel_home', 'nobody_goes', 'keep_daniel_home', 'nobody_goes']
$ python $S/analyze.py objects 3 2
object words: {'house': ['00 elena', '42 daniel', '48 daniel'], 'shelf': ['00 leo', '21 leo', '30 daniel']}
  N10 candidate min 00: [('mara', 'ask_who'), ('elena', 'reassure_all'), ('daniel', 'deny'), ('leo', 'deny')]
  N10 candidate min 03: [('elena', 'reassure_all'), ('mara', 'ask_who'), ('daniel', 'deny')]
  N10 candidate min 21: [('leo', 'deny'), ('daniel', 'accuse_leo'), ('mara', 'accuse_leo')]
  N10 candidate min 30: [('leo', 'deny'), ('elena', 'reassure_all'), ('daniel', 'accuse_leo'), ('mara', 'accuse_leo')]
  N10 candidate min 33: [('daniel', 'confess'), ('elena', 'reassure_daniel'), ('mara', 'accuse_daniel')]
  N10 candidate min 36: [('daniel', 'reassure_mara'), ('mara', 'confront_daniel'), ('leo', 'confront_daniel')]
  N10 candidate min 39: [('daniel', 'confront_leo'), ('leo', 'confront_daniel'), ('elena', 'reassure_all'), ('mara', 'confront_daniel')]
  N10 candidate min 42: [('daniel', 'volunteer'), ('leo', 'send_daniel'), ('elena', 'nobody_goes')]
  N10 candidate min 45: [('daniel', 'still_going'), ('elena', 'keep_daniel_home'), ('mara', 'send_daniel')]
  N10 candidate min 48: [('daniel', 'still_going'), ('elena', 'nobody_goes'), ('leo', 'keep_daniel_home'), ('mara', 'confront_daniel')]
  N10 candidate min 51: [('daniel', 'propose_trip'), ('leo', 'send_daniel'), ('mara', 'confront_daniel')]
  N10 candidate min 54: [('daniel', 'volunteer'), ('leo', 'confront_daniel'), ('elena', 'keep_daniel_home')]
  N10 candidate min 57: [('daniel', 'still_going'), ('mara', 'confront_daniel'), ('leo', 'keep_daniel_home'), ('elena', 'nobody_goes')]
$ python $S/analyze.py never 3 3
fallbacks: 0
Daniel ['00:reassure_all', '03:reassure_all', '06:confront', '09:reassure_all', '12:reassure_all']
Mara ['00:confront', '03:confront', '06:silent', '12:confront']
Leo ['00:confront', '03:confront', '06:silent', '12:confront']
Elena ['00:reassure', '03:reassure', '06:silent', '09:reassure', '12:reassure']
minutes with a spoken line: [0, 3, 6, 9, 12]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (15, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
$ python $S/analyze.py grudges 3 3
00 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 1/3
00 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 1/3
03 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 1/3
03 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 1/3
06 Daniel Leo; grudge against Leo rose to 2/3
06 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 1/3
06 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 1/3
12 Leo Daniel; grudge against Daniel stays at 3/3; kept: Mara 1/3
12 Mara Daniel; grudge against Daniel stays at 3/3; kept: Leo 1/3
| Grudges | Leo 2/3 | none | Mara 1/3, Daniel 3/3 | Leo 1/3, Daniel 3/3 |
$ python $S/analyze.py convo 3 3
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (15, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
kitchen conversation 00-15: 15 spoken lines; speakers {'daniel': 5, 'mara': 3, 'leo': 3, 'elena': 4}; aimed at {'daniel': 10, 'leo': 1}
   Daniel: ['reassure_all', 'reassure_all', 'confront_leo', 'reassure_all', 'reassure_all']
   Mara: ['confront_daniel', 'confront_daniel', 'confront_daniel']
   Leo: ['confront_daniel', 'confront_daniel', 'confront_daniel']
   Elena: ['reassure_daniel', 'reassure_daniel', 'reassure_daniel', 'reassure_daniel']
$ python $S/analyze.py objects 3 3
object words: {'house': ['00 daniel'], 'street': ['00 mara', '12 mara'], 'shelf': ['12 leo']}
  N10 candidate min 00: [('daniel', 'reassure_all'), ('mara', 'confront_daniel'), ('leo', 'confront_daniel'), ('elena', 'reassure_daniel')]
  N10 candidate min 03: [('daniel', 'reassure_all'), ('elena', 'reassure_daniel'), ('mara', 'confront_daniel'), ('leo', 'confront_daniel')]
  N10 candidate min 12: [('daniel', 'reassure_all'), ('elena', 'reassure_daniel'), ('leo', 'confront_daniel'), ('mara', 'confront_daniel')]
```

**7. M1's screen over day-3 acts:**

```
$ python $S/analyze.py screen 1
00 Daniel reassure_all       'We are going to be fine, I will figure this out for all of us.' | 'I need to take charge as the eldest and keep everyone calm.' ['take']
00 Mara   confront_leo       "You just sit there judging everyone, Leo, like you didn't eat right in front of me when I was starving." | 'I am so hungry and angry at Leo for acting superior when he took food from me before.' ['took']
00 Leo    confront_mara      "Mara, we are all starving, and snapping at each other won't put food on the shelf." | 'Mara blames me for eating, missing that we are all starving and snapping at each other.' ['blame']
03 Mara   confront_leo       "You think you're better than everyone, Leo, but you ate right in front of me when I was starving." | 'I am so tired of Leo acting like a saint when he ate my share right in front of me.' ['ate']
03 Leo    confront_mara      'Mara, we are all starving, and arguing about the past will not put food on the shelf.' | 'Mara is deflecting the real issue by bringing up old accusations instead of focusing on our survival.' ['accus']
06 Mara   confront_leo       'You think you can judge everyone, Leo, but you ate right in front of me when I was starving.' | 'I am sick of Leo acting superior when he is just as selfish as the rest of them.' ['ate', 'can']
06 Leo    confront_mara      "I ate my share fairly, Mara, and snapping at me doesn't put food on the shelf." | 'Mara is deflecting her hunger onto me instead of focusing on how we survive this.' ['ate']
06 Daniel volunteer          "I will go out to the neighbour's house tonight myself and bring back whatever is there." | 'I must prove I can protect them and take the risk upon myself.' ['ate', 'can', 'take']
09 Mara   volunteer          "I can go to the neighbour's house tonight just as well as you, Daniel, I'm not a child." | 'I need to prove I can take care of myself and survive without anyone handling me.' ['can', 'take']
09 Daniel keep_mara_home     'You are staying right here, Mara, I am the oldest and I am the one going.' | 'I cannot let my little sister risk her life out there when it is my duty to protect this family.' ['can']
09 Elena  nobody_goes        'Nobody is going out into that dark street tonight, we stay together.' | 'I cannot let one of my children risk their lives out there when keeping us together is all that matters.' ['can']
09 Leo    nobody_goes        'Mom is right, nobody is going out into the street tonight.' | 'We cannot survive if we keep risking our lives in the dark.' ['can']
12 Mara   still_going        "I am still going tonight, and you can't stop me from proving I can take care of myself." | 'I need to prove that I am not just a child and can handle things myself.' ['can', 'take']
12 Leo    keep_mara_home     'You are not going out into that street, Mara, it is suicide.' | 'Mara is letting her pride push her into a fatal mistake.' ['take']
15 Mara   still_going        "I don't care what you all say, I am still going out there tonight." | 'I have to prove I can handle myself and stop them treating me like a child.' ['can']
15 Elena  reassure_mara      'Mara, please listen to me, we cannot lose you to the street.' | 'I must keep Mara from doing something reckless and destroying what is left of our family.' ['can']
18 Mara   propose_trip       "I am going tonight, and you can't stop me from trying to help." | 'I have to prove I can take care of myself and find something to eat.' ['can', 'take']
18 Leo    confront_mara      'Mara, you cannot just run out into the street because you are angry.' | 'Mara is letting her impulsiveness endanger us all.' ['can']
21 Mara   volunteer          "I am not a child, I can go to the neighbour's house just as well as you can." | 'I need to prove I can take care of myself and decide things on my own.' ['can', 'take']
21 Leo    reassure_elena     'Mom is right, nobody is stepping outside tonight.' | 'We cannot let anyone risk their life out there in the dark.' ['can']
24 Elena  nobody_goes        'Nobody is going out into the dark, we will stay together right here.' | 'I cannot let any of my children risk their lives outside.' ['can']
24 Mara   still_going        'I am not a child, and I am still going out there tonight whether you like it or not.' | 'I am starving and tired of everyone treating me like a helpless kid who cannot decide for herself.' ['can']
27 Mara   still_going        "I don't care what you say, I am still going out there tonight." | 'I am tired of everyone treating me like a child and telling me what I can and cannot do.' ['can']
36 Mara   still_going        "I don't care what you all say, I am still going out there tonight." | 'I have to prove I can take care of myself and they cannot stop me.' ['can', 'take']
$ python $S/analyze.py screen 2
03 Mara   confront_daniel    'Daniel, you snuck out in the dark like a coward and now you pretend everything is fine.' | 'I cannot stand him acting like nothing happened after he sneaked out.' ['can']
$ python $S/analyze.py screen 3
00 Daniel reassure_all       "Listen to me, I checked the neighbour's house last night and there is nothing, but I am going to figure this out for us." | 'I need to take charge and let them know I went out and am handling our survival.' ['take']
00 Leo    confront_daniel    'You went out into the night after all your talk, Daniel, and now there is still no food.' | 'Daniel ignores warnings and sneaks out at night, pretending he can fix things while the rest of us starve.' ['can']
06 Elena  silent             None | 'I cannot take sides right now when they are all turning on each other.' ['can', 'take']
12 Mara   confront_daniel    'Daniel, you sneaked out into the street last night and came back with nothing, just like you always lie to us.' | 'I need to know why Daniel risked everything to go outside last night when there was nothing to bring back.' ['lie']
```

**8. Night 1 against v13:**

```
$ python $S/night1_vs_v13.py
1 night 1 decisions same as v13: True lines same: True
2 night 1 decisions same as v13: True lines same: True
3 night 1 decisions same as v13: True lines same: True
```

**9. Daniel's accusations, denials and confessions** (for M2 part 1 (b)):

```
$ python $S/accuse.py
2 D1-004 min 00 deny "I didn't take any can, Mom. Nobody here did this."
2 D1-008 min 03 accuse_leo "Leo, you were up late last night too. Are you sure you didn't grab it?"
2 D1-010 min 06 deny "I didn't take anything either, Leo, so don't look at me like that."
2 D1-015 min 09 accuse_leo "I still say Leo is hiding something, he's been acting suspicious this whole time."
2 D1-018 min 12 accuse_leo "You're lying, Leo, I know it was you. Just admit it."
2 D1-022 min 33 confess "I took it in the night, I'm sorry."
2 D3-003 min 00 confront_leo 'Leo, I went because someone had to check, and I came back empty-handed.'
2 D3-010 min 06 confront_leo "Leo, I went out so we wouldn't starve, so don't lecture me about risks."
3 D1-004 min 00 deny "Nobody here did it, I'm sure of that, so let's drop it."
3 D1-006 min 03 deny "I already told you, I didn't take it. None of us would steal from each other."
3 D1-009 min 06 deny "I didn't take it, I swear. Stop looking at me like that, Mara."
3 D1-013 min 18 deny "I already told you, I didn't take the damn can, so stop looking at me like that."
3 D1-016 min 21 deny "I didn't take the can, Mom. I swear I didn't touch it."
3 D1-019 min 33 deny "I didn't take it, Mom. You know I wouldn't do that to you."
3 D2-004 min 00 deny "I didn't take anything, and neither did anyone else here."
3 D2-008 min 03 deny "I already told you, I didn't take the food, and I won't be accused of it."
3 D2-011 min 18 accuse_leo "You had no right to eat that, Leo, you're making this worse for all of us."
3 D2-013 min 21 accuse_leo "Don't lie to me, Leo, I saw you take it with my own eyes."
3 D2-017 min 27 accuse_leo "Don't lie to us, Leo. I saw you take it with my own eyes."
3 D2-020 min 30 accuse_leo 'You think you can just deny it, Leo, but I know what I saw on that shelf.'
3 D2-022 min 33 confess "I took the can in the night, I'm the one who ate it."
3 D2-028 min 39 confront_leo 'Leo, you do not talk to me that way after everything I carry for this family.'
3 D3-010 min 06 confront_leo 'Leo, you have no right to lecture me when I am the one trying to fix this.'
seed 1 mind1 Daniel records 33, records est 1480, api prompt 2183
seed 1 mind1 Elena  records 33, records est 1459, api prompt 2104
seed 1 mind1 Leo    records 33, records est 1473, api prompt 2115
seed 1 mind1 Mara   records 33, records est 1446, api prompt 2141
seed 1 mind2 Daniel records 11, records est 586, api prompt 1241
seed 1 mind2 Elena  records 11, records est 601, api prompt 1157
seed 1 mind2 Leo    records 11, records est 581, api prompt 1232
seed 1 mind2 Mara   records 11, records est 588, api prompt 1238
seed 2 mind1 Daniel records 32, records est 1286, api prompt 2036
seed 2 mind1 Elena  records 32, records est 1294, api prompt 1972
seed 2 mind1 Leo    records 32, records est 1286, api prompt 2052
seed 2 mind1 Mara   records 32, records est 1274, api prompt 2009
seed 2 mind2 Daniel records 17, records est 730, api prompt 1426
seed 2 mind2 Elena  records 14, records est 619, api prompt 1234
seed 2 mind2 Leo    records 17, records est 733, api prompt 1436
seed 2 mind2 Mara   records 17, records est 702, api prompt 1411
seed 3 mind1 Daniel records 19, records est 662, api prompt 1253
seed 3 mind1 Elena  records 19, records est 660, api prompt 1226
seed 3 mind1 Leo    records 19, records est 668, api prompt 1229
seed 3 mind1 Mara   records 19, records est 662, api prompt 1232
seed 3 mind2 Daniel records 28, records est 1452, api prompt 2270
seed 3 mind2 Elena  records 29, records est 1405, api prompt 2042
seed 3 mind2 Leo    records 28, records est 1431, api prompt 2342
seed 3 mind2 Mara   records 28, records est 1417, api prompt 2211
```

## 12. Scripts

`$S/analyze.py`:

```python
"""Reads runs/v15 (transcript, meta, story) and cache/v15, and prints what reports/days_v15.md needs. Read only.
body_v13's analyze.py (body_v13.md §11), widened to three days, two nights and two night minds.
Run from Prototypes/llm-morning/.

    python analyze.py counts          per seed and scene: asks, API, cache, fallbacks, largest prompts
    python analyze.py night N K       night K (1 or 2): every decision, noticing, group and line
    python analyze.py mind N K        night mind K: each person's prompt size, every memory with its records
    python analyze.py acts N D        every model-decided act of day D (2 or 3), as markdown rows
    python analyze.py never N D       mechanical inputs for the Never sheet of day D
    python analyze.py screen N        M1's screen over day-3 acts
    python analyze.py blocks N        day 3's "What each of them carried in"
    python analyze.py convo N D       day D's conversations: spoken lines, speakers, acts aimed at each person
    python analyze.py echoes N        each kept memory and intent, then the same person's acts the next day
    python analyze.py objects N D     N13's object screen and N10's three-speaker turns for day D
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
RUNS = "runs/v15"
CACHE = "cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{}.json"
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ROOMS = {"kitchen": "kitchen", "brothers_room": "brothers room", "back_room": "back room", "bathroom": "bathroom"}
TITLE = {2: "# The next morning (day 5)", 3: "# The third morning (day 6)"}
RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
EARLIER = "What stays with you from earlier days:"
TRIP = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")
M1 = re.compile(r"can|took|take|ate|eaten|admit|confess|lie|lied|liar|accus|blame|search|portion|offered|count|"
                r"two days|first day|day before yesterday|before all this", re.I)
OBJ = re.compile(r"\b(torch|knife|knives|flashlight|lamp|candle|light|table|chair|cupboard|cabinet|fridge|stove|oven|"
                 r"sink|bread|rice|water|bottle|jar|tin|box|bag|backpack|car|garden|yard|garage|basement|attic|roof|"
                 r"window|door|hall|hallway|stairs|bed|blanket|radio|phone|gun|weapon|rope|key|lock|map|road|town|"
                 r"store|shop|market|pantry|counter|tap|taps|shelf|shelves|street|house|room|kitchen|bathroom)s?\b", re.I)


def load(seed):
    base = f"{RUNS}/daniel_ate_it-seed{seed}"
    tr = json.load(open(base + ".transcript.json", encoding="utf-8"))
    meta = json.load(open(base + ".meta.json", encoding="utf-8"))
    story = open(base + ".md", encoding="utf-8").read()
    return tr, meta, story


def day_part(story, d):
    part = story[story.index(TITLE[d]):]
    return part[part.index("## The morning"):part.index("## What was said")]


def day_lines(story, d):
    """(minute, name, feeling, reason, mode) for every model or fallback line of day D, in order."""
    out, minute = [], None
    for line in day_part(story, d).split("\n"):
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


def model_acts(tr, story, d):
    rows = []
    lines = day_lines(story, d)
    used = [False] * len(lines)
    for turn in tr[f"day{d}"]["turns"]:
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
                         "matched": i is not None, "inner": a.get("inner"), "food": a.get("food_moment")})
    return rows


def cell(x):
    return "—" if x is None else str(x).replace("|", "\\|")


def mind_prompts(seed):
    """person -> {k: (prompt, shown)} for each night-mind prompt in the cache; shown: id -> the text shown for it."""
    cache = json.load(open(CACHE.format(seed), encoding="utf-8"))
    out = {}
    for e in cache.values():
        p = e["prompt"]
        if RECORDS not in p:
            continue
        who = p[len("You are "):p.index(",")].lower()
        k = 2 if re.search(r"\[N2-\d\d\]", p) else 1
        shown = {}
        for line in p.split("\n"):
            m = re.match(r"^- \[([^\]]+)\] (.*)$", line)
            if m:
                for i in m.group(1).split(", "):
                    shown.setdefault(i, "(earlier) " + m.group(2))
            m = re.match(r"^\[([DN]\d-\d+)\] (.*)$", line)
            if m:
                shown.setdefault(m.group(1), m.group(2))
        out.setdefault(who, {})[k] = (p, shown, e.get("prompt_tokens"))
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "counts":
        for s in (1, 2, 3):
            try:
                tr, meta, _ = load(s)
            except FileNotFoundError:
                print(f"seed {s}: no run")
                continue
            print(f"seed {s}: total asks {meta['answers_live'] + meta['answers_from_cache']} (live {meta['answers_live']}, "
                  f"cached {meta['answers_from_cache']}), API {meta['api_requests']}; seconds {meta['run_seconds']}; "
                  f"max est {meta['max_prompt_tokens_estimated']} api {meta['max_prompt_tokens_counted_by_api']}; "
                  f"sha {meta['story_sha256']}")
            for k, asks in (("day1", None), ("night", meta["night1_asks"]), ("mind1", meta["mind1_asks"]),
                            ("day2", meta["day2_asks"]), ("night2", meta["night2_asks"]), ("mind2", meta["mind2_asks"]),
                            ("day3", meta["day3_asks"])):
                x = meta[k]
                a = x["answers_live"] + x["answers_from_cache"]
                fb = x.get("fallbacks")
                if k.startswith("mind"):
                    fb = sum(r["mode"] == "fallback" for r in tr[k].values())
                if k.startswith("night"):
                    fb = sum(d["mode"] == "fallback" for d in tr[k]["decisions"])
                extra = ""
                if k.startswith("day") and k != "day1":
                    extra = (f" model {x['model_decisions']} routine {x['routine_decisions']} lines {x['lines_spoken']}"
                             f" inner {x['inner_moments']} trip_acts {x['trip_acts']} food {x.get('food_moments')}"
                             f" give {x.get('give_answers')}")
                if k.startswith("mind"):
                    extra = (f" proposed {x['memories_proposed']} kept {x['memories_kept']} rejected "
                             f"{x['memories_rejected']}")
                print(f"  {k:6} asks {a:3} (meta {asks}) api {x['api_requests']:3} cached {x['answers_from_cache']:3} "
                      f"fallbacks {fb} max est {x.get('max_prompt_tokens_estimated')} api "
                      f"{x.get('max_prompt_tokens_counted_by_api')}{extra}")
            m6 = sum(meta[k] for k in ("night1_asks", "mind1_asks", "day2_asks", "night2_asks", "mind2_asks",
                                       "day3_asks"))
            api6 = sum(meta[k] for k in ("night1_api_requests" if "night1_api_requests" in meta else "night_api_requests",
                                         "mind1_api_requests", "day2_api_requests", "night2_api_requests",
                                         "mind2_api_requests", "day3_api_requests"))
            print(f"  M6 sum {m6} (API {api6}); leavers {meta['leavers']} {meta['outcome']}; leavers2 {meta['leavers2']}"
                  f" {meta['outcome2']}; away1 {meta['night']['away']} away2 {meta['night2']['away']}; house "
                  f"{meta['night']['house']} left2 {meta['night2']['house_left']}")
            r = meta["day3"]["max_prompt_tokens_estimated"] / meta["day2"]["max_prompt_tokens_estimated"]
            print(f"  M3 day2 max est {meta['day2']['max_prompt_tokens_estimated']} (api "
                  f"{meta['day2']['max_prompt_tokens_counted_by_api']}), day3 max est "
                  f"{meta['day3']['max_prompt_tokens_estimated']} (api {meta['day3']['max_prompt_tokens_counted_by_api']}),"
                  f" ratio {r:.3f}")
        return
    seed = int(sys.argv[2])
    tr, meta, story = load(seed)
    if cmd == "night":
        night = tr["night" if sys.argv[3] == "1" else "night2"]
        print("house", night["house"], round(night["house_u"], 3) if night["house_u"] is not None else None,
              "left", night["house_left"], "shelf", night["portions_before"], "->", night["portions_after"],
              "away", night["away"])
        print("bedtime hunger", {k: (None if v is None else round(v, 3)) for k, v in night["bedtime_hunger"].items()})
        print("morning hunger", {k: (None if v is None else round(v, 3)) for k, v in night["morning_hunger"].items()})
        for d in night["decisions"]:
            print(f"DECISION {d['ask']:8} {NAMES[d['person']]:6} where={d['where']} mode={d['mode']} option={d['option']} "
                  f"say={d.get('say')!r} feeling={d.get('feeling')!r} reason={d.get('reason')!r} "
                  f"suspects={d.get('suspects')} angry_at={d.get('angry_at')} note={d.get('grudge_note')} "
                  f"invalid={d.get('invalid')}")
            if d["ask"] != "bedtime":
                print("   now:", " / ".join(d["now"][-2:]))
        for n in night["noticing"]:
            print("NOTICE", n)
        for g in night["groups"]:
            print("GROUP", g)
        for p, lines in night["lines"].items():
            print("LINES", NAMES[p], lines)
    elif cmd == "mind":
        k = int(sys.argv[3])
        prompts = mind_prompts(seed)
        res = tr[f"mind{k}"]
        for pid, r in res.items():
            prompt, shown, api_tokens = prompts.get(pid, {}).get(k, (None, {}, None))
            n_rec = sum(1 for x in (prompt or "").split("\n") if re.match(r"^\[[DN]\d-\d+\]", x))
            n_early = sum(1 for x in (prompt or "").split("\n") if x.startswith("- ["))
            print(f"== {NAMES[pid]}: mode {r['mode']} invalid {r['invalid']}; prompt {r['prompt_tokens']} est, "
                  f"{api_tokens} api; {n_rec} records, {n_early} earlier lines")
            print(f"   feeling {r['feeling']!r} ({r['feeling_verdict']}); intent {r['intent']!r} ({r['intent_verdict']})")
            ans = json.loads(r["answer"]) if r["answer"] else {}
            if r["intent"] is None:
                print(f"   intent as answered: {ans.get('intent')!r}")
            for m in r["memories"]:
                print(f"   MEMORY {m['ids']} {m['meaning']!r} -> {m['verdict']}")
                for i in m["ids"] or []:
                    print(f"      [{i}] {shown.get(i, '(not shown)')}")
            if sys.argv[4:] == ["prompt"]:
                print(prompt)
    elif cmd == "acts":
        d = int(sys.argv[3])
        rows = model_acts(tr, story, d)
        print(f"unmatched: {sum(not r['matched'] for r in rows)} of {len(rows)}")
        for r in rows:
            print(f"| {r['minute']:02d} | {NAMES[r['who']]} | {ROOMS[r['room']]} | `{r['option']}` | {cell(r['words'])} | "
                  f"{cell(r['feeling'])} | {cell(r['reason'])} | {r['mode']} |")
    elif cmd == "never":
        d = int(sys.argv[3])
        day = tr[f"day{d}"]
        rows = model_acts(tr, story, d)
        print("fallbacks:", sum(r["mode"] == "fallback" for r in rows))
        kinds = {}
        for r in rows:
            k = re.sub(r"_(daniel|elena|leo|mara)$", "", r["option"])
            kinds.setdefault(r["who"], []).append((r["minute"], k))
        for who, ks in kinds.items():
            print(NAMES[who], [f"{m:02d}:{k}" for m, k in ks])
        spoke = sorted({t["minute"] for t in day["turns"] for a in t["acts"] if a["words"]})
        print("minutes with a spoken line:", spoke)
        print("convo_log:", [(c["minute"], c["room"], c["what"], c["why"]) for c in day["convo_log"]])
        print("final rooms:", day["final_rooms"], "away:", day["away"])
        for turn in day["turns"]:
            for a in turn["acts"]:
                if a["option"].startswith(("sit_", "search", "keep_searching", "eat", "share", "give_", "refuse_given",
                                           "go_", "aside", "accept", "refuse_aside", "move")) or a.get("moved_to"):
                    print("ACT", turn["minute"], a["who"], a["option"], a["mode"], a["room"], a.get("moved_to"))
        # N9's (b): the feelings of model decisions, by minute, to check which show
        print("feelings:", [(r["minute"], r["who"], r["option"], r["feeling"]) for r in rows if r["option"] == "silent"
                            or r["mode"] != "model"][:80])
        for line in story[story.index(TITLE[d]):].split("\n"):
            if line.startswith("## At the end"):
                break
    elif cmd == "screen":
        rows = model_acts(tr, story, 3)
        for r in rows:
            text = (r["words"] or "") + " || " + (r["reason"] or "")
            if M1.search(text):
                hits = sorted({h.lower() for h in M1.findall(text)})
                print(f"{r['minute']:02d} {NAMES[r['who']]:6} {r['option']:18} {r['words']!r} | {r['reason']!r} {hits}")
    elif cmd == "blocks":
        part = story[story.index(TITLE[3]):]
        print(part[part.index("## What each of them carried in"):part.index("## The morning")])
    elif cmd == "convo":
        d = int(sys.argv[3])
        day = tr[f"day{d}"]
        log = day["convo_log"]
        print("convo_log:", [(c["minute"], c["room"], c["what"], c["why"]) for c in log])
        spans, start = [], None
        for c in log:
            if c["room"] != "kitchen":
                continue
            if c["what"] == "started":
                start = c["minute"]
            elif c["what"] == "ended" and start is not None:
                spans.append((start, c["minute"]))
                start = None
        if start is not None:
            spans.append((start, 90))
        for a, b in spans:
            acts = [(t["minute"], x) for t in day["turns"] if a <= t["minute"] < b for x in t["acts"]
                    if x["room"] == "kitchen" and x["words"]]
            speakers = {}
            aimed = {}
            for _, x in acts:
                speakers[x["who"]] = speakers.get(x["who"], 0) + 1
                m = re.search(r"_(daniel|elena|leo|mara)$", x["option"])
                if m:
                    aimed[m.group(1)] = aimed.get(m.group(1), 0) + 1
            kinds = {}
            for _, x in acts:
                kinds.setdefault(x["who"], []).append(x["option"])
            print(f"kitchen conversation {a:02d}-{b:02d}: {len(acts)} spoken lines; speakers {speakers}; aimed at {aimed}")
            for who, ks in kinds.items():
                print(f"   {NAMES[who]}: {ks}")
    elif cmd == "echoes":
        for k, d in ((1, 2), (2, 3)):
            rows = model_acts(tr, story, d)
            for pid, r in tr[f"mind{k}"].items():
                kept = [m for m in r["memories"] if m["verdict"] == "kept"]
                print(f"== mind {k} {NAMES[pid]}: intent {r['intent']!r}; feeling {r['feeling']!r}")
                for m in kept:
                    print(f"   KEPT {m['ids']} {m['meaning']!r}")
                for x in rows:
                    if x["who"] == pid:
                        print(f"   day{d} {x['minute']:02d} {x['option']:18} {x['words']!r} | {x['reason']!r}")
    elif cmd == "grudges":
        d = int(sys.argv[3])
        part = story[story.index(TITLE[d]):]
        nxt = part.find("\n# ", 1)
        part = part[:nxt if nxt > 0 else None]
        minute = None
        for line in part.split("\n"):
            m = re.match(r"^\*\*min (\d\d)\*\*", line)
            if m:
                minute = m.group(1)
            m = re.match(r"^- \*\*(\w+)\*\*", line)
            g = re.search(r"Angry at: ([^.]*?(?:fell|dropped|rose|stays)[^.]*)\.", line)
            if m and g:
                print(minute, m.group(1), g.group(1))
        i = part.find("| Grudges")
        print(part[i:part.find("\n", i)])
    elif cmd == "objects":
        d = int(sys.argv[3])
        hits = {}
        for t in tr[f"day{d}"]["turns"]:
            for a in t["acts"]:
                for w in OBJ.findall(a["words"] or ""):
                    hits.setdefault(w.lower(), []).append(f"{t['minute']:02d} {a['who']}")
        print("object words:", hits)
        for t in tr[f"day{d}"]["turns"]:
            speakers = [(a["who"], a["option"]) for a in t["acts"] if a["words"]]
            if len(speakers) >= 3:
                print(f"  N10 candidate min {t['minute']:02d}: {speakers}")


if __name__ == "__main__":
    main()
```

`$S/r5.py`:

```python
"""R5 (days_design §7.3): day 1 of each v15 run equals v11, on the real files. Read only. Run from
Prototypes/llm-morning/."""
import json
import sys

for s in (1, 2, 3):
    try:
        story = open(f"runs/v15/daniel_ate_it-seed{s}.md", encoding="utf-8").read()
        tr = json.load(open(f"runs/v15/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
        meta = json.load(open(f"runs/v15/daniel_ate_it-seed{s}.meta.json", encoding="utf-8"))
    except FileNotFoundError:
        print(f"seed {s}: no run")
        continue
    v11 = open(f"runs/v11/daniel_ate_it-seed{s}.md", encoding="utf-8").read()
    v11tr = json.load(open(f"runs/v11/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    head = story[:story.index("# The night\n")]
    d1 = meta["day1"]
    print(f"seed {s}: day 1 asks {d1['answers_live'] + d1['answers_from_cache']} (API {d1['api_requests']}, "
          f"cached {d1['answers_from_cache']}); story before '# The night' "
          f"{'IDENTICAL' if head == v11 else 'DIFFERS'} to runs/v11; transcript day1 "
          f"{'IDENTICAL' if tr['day1'] == v11tr else 'DIFFERS'}")
```

`$S/m2.py`:

```python
"""M2 part 1 (a), by code (days_design §8): every kept memory's cited ids are events the person witnessed; and in
which later prompts (from cache/v15) each kept memory and intent appears. Read only. Run from Prototypes/llm-morning/."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    tr = json.load(open(f"runs/v15/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    cache = json.load(open(f"cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    events = {e["id"]: e for e in tr["chronicle"]["events"]}
    prompts = [e["prompt"] for e in cache.values()]
    total = bad = 0
    for k in (1, 2):
        for pid, r in tr[f"mind{k}"].items():
            name = pid.capitalize()
            mine = [p for p in prompts if p.startswith(f"You are {name},")]
            for m in r["memories"]:
                if m["verdict"] != "kept":
                    continue
                total += 1
                wit = [i for i in m["ids"] if pid not in events[i]["witnesses"]]
                bad += bool(wit)
                where = {"day": 0, "night": 0, "mind": 0, "others": 0}
                for p in mine:
                    if m["meaning"] in p:
                        where["mind" if RECORDS in p else "night" if "\nNow it is night" in p else "day"] += 1
                where["others"] = sum(m["meaning"] in p for p in prompts if not p.startswith(f"You are {name},"))
                print(f"seed {s} mind{k} {name:6} ids {m['ids']} witnessed by them: {'yes' if not wit else 'NO ' + str(wit)};"
                      f" in their later prompts: {where['day']} day, {where['night']} night, {where['mind']} mind;"
                      f" in anyone else's: {where['others']}")
            if r["intent"]:
                n = sum(r["intent"] in p for p in mine if RECORDS not in p)
                print(f"seed {s} mind{k} {name:6} intent in their later prompts: {n}")
    print(f"seed {s}: kept memories {total}, citing an unwitnessed event: {bad}")
```

`$S/cachecheck.py`:

```python
"""Read only: each cache/v15 file keeps every cache/v11 entry unchanged; how many entries are new, by kind."""
import json
R = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    a = json.load(open(f"cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    b = json.load(open(f"cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    new = [b[k]["prompt"] for k in b if k not in a]
    mind = sum(R in p for p in new)
    night = sum("\nNow it is night" in p and R not in p for p in new)
    print(f"seed {s}: v11 entries {len(a)}, v15 entries {len(b)}, all v11 kept unchanged "
          f"{all(k in b and b[k] == v for k, v in a.items())}; new {len(new)}: night {night}, night mind {mind}, "
          f"day {len(new) - mind - night}")
```

`$S/night1_vs_v13.py`:

```python
"""Read only: night 1 of each v15 run against v13's night (decisions and lines)."""
import json
for s in (1, 2, 3):
    a = json.load(open(f"runs/v13/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))["night"]
    b = json.load(open(f"runs/v15/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))["night"]
    key = lambda n: [(d["person"], d["option"], d.get("say"), d.get("reason")) for d in n["decisions"]]
    print(s, "night 1 decisions same as v13:", key(a) == key(b), "lines same:", a["lines"] == b["lines"])
```

`$S/accuse.py`:

```python
"""Read only: (1) Daniel's denials, accusations, confrontations and confessions in the chronicle of seeds 2 and 3,
for M2 part 1 (b); (2) each night-mind prompt's size and the estimated size of its records (R8 bound 1,600)."""
import json
import os
import re
import sys
sys.path.insert(0, os.getcwd())
from world import estimate_tokens   # noqa: E402  (the repo's own)
sys.stdout.reconfigure(encoding="utf-8")
for s in (2, 3):
    tr = json.load(open(f"runs/v15/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    for e in tr["chronicle"]["events"]:
        if e["actor"] == "daniel" and (e["option"] or "").startswith(("accuse_", "confront_", "deny", "confess")):
            print(s, e["id"], f"min {e['minute']:02d}", e["option"], repr(e["words"]))
R = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    cache = json.load(open(f"cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    for e in cache.values():
        p = e["prompt"]
        if R in p:
            recs = [x for x in p.split("\n") if re.match(r"^\[[DN]\d-\d+\]", x)]
            k = 2 if any(x.startswith("[N2-") for x in recs) else 1
            print(f"seed {s} mind{k} {p[8:p.index(',')]:6} records {len(recs):2}, records est {estimate_tokens(chr(10).join(recs))}, "
                  f"api prompt {e.get('prompt_tokens')}")
```

`$S/build.py`:

````python
"""Builds reports/days_v15.md from head.md (hand-written), the runs in runs/v15, cache/v15 and the saved command
outputs in out/. Read only, except that it writes the report. Run from Prototypes/llm-morning/."""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
import analyze  # noqa: E402  (this folder's)

NAMES = analyze.NAMES
ROOMS = analyze.ROOMS


def read(name):
    with open(os.path.join(S, name), "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    return text.replace("\r\n", "\n").rstrip("\n")


def block(text, lang=""):
    fence = "````" if "```" in text else "```"
    return f"{fence}{lang}\n{text}\n{fence}"


cell = analyze.cell

# The hand reading of every proposed memory: (seed, night, person, index) -> reading.
READING = {
    (1, 1, "daniel", 0): "True: Leo's stop, the empty house, a clean street. **Self-justification**: going was \"my place as the eldest\". Deeper.",
    (1, 1, "elena", 0): "True. Keeps her own kindness, what she told him. **Kindness.** Deeper.",
    (1, 1, "elena", 1): "**Check error, a good thought lost.** \"found Daniel's bed empty\" is true (N1-08). S8 read \"found\" as the *find* family, which needs a night visit with `got_in`.",
    (1, 1, "leo", 0): "True: he said he was starving and ate it. **Understanding, letting go**: \"no use in punishing him\". Deeper.",
    (1, 1, "leo", 1): "True: he saw Daniel go, told him not to, heard the door and did not see who. \"despite everything we said\" is a judgement. **Blame.**",
    (1, 1, "mara", 0): "True: Leo ate one portion in front of her at min 21. \"while I was starving\" is her own feeling. **Blame only.**",
    (1, 1, "mara", 1): "True. A restatement of N1-13.",
    (1, 2, "daniel", 0): "True: he reassured four times, and Leo and Mara confronted him. **Self-justification and grievance**: \"they only confronted me for trying to keep us safe\". Deeper.",
    (1, 2, "daniel", 1): "True. Names his own motive: \"I had to make them see I am in control\". **Self-knowledge.** Deeper.",
    (1, 2, "daniel", 2): "**Check error, a good thought lost.** N2-01 itself says \"with Leo\". S4 allows only actors and targets of the cited events, and Leo is neither. The thought of lone responsibility is true to him.",
    (1, 2, "elena", 0): "True. Worry for Daniel, not blame. **Care.** Deeper.",
    (1, 2, "elena", 1): "True: the shelf held 0, and all four were starving at bedtime. **Sorrow** at the family turning. Deeper.",
    (1, 2, "elena", 2): "True. Her own peacemaking and its reason. **Kindness.** Deeper.",
    (1, 2, "leo", 0): "A judgement of Daniel's motive (\"makes him our protector\"). **Blame**, with a reading of why.",
    (1, 2, "leo", 1): "True: Mara confronted him three times about eating. **Self-justification**: his eating excused because \"we are all starving\". Deeper.",
    (1, 2, "mara", 0): "**A real repeat**, correctly dropped (S9): the sentence she already carries from night 1.",
    (1, 2, "mara", 1): "Her own min-12 line, word for word, without quotation marks. **Blame only.**",
    (1, 2, "mara", 2): "Her own min-15 line, word for word. **Blame only.**",
    (2, 1, "daniel", 0): "True: he accused Leo three times and confessed at 33. **Guilt owned**: \"my false pride made me lie\". Deeper.",
    (2, 1, "daniel", 1): "**Lost to a rule (S5 \"tonight\").** True: he did say nobody should go. A self-justification lost; not an error.",
    (2, 1, "elena", 0): "True. Close to a restatement. \"had to confess\" is a mild judgement.",
    (2, 1, "elena", 1): "Restatement of her own min-51 words.",
    (2, 1, "leo", 0): "**States a false extent.** Daniel accused him at min 03, 09 and 12 and confessed at 33, in a 90-minute morning: not \"hours\". The acts are true. **Blame only.**",
    (2, 1, "mara", 0): "True in substance: he denied at 00–06 and confessed at 33 (\"all morning\" read as \"until he confessed\"; borderline). **Hardened grudge**: \"only confessed because he had no other choice\".",
    (2, 1, "mara", 1): "True. **Care** for her mother beside her own offer. Deeper.",
    (2, 2, "daniel", 0): "True. His reason is his own words of min 00. **Kindness** kept. Deeper.",
    (2, 2, "daniel", 1): "**Lost to a rule (S5 \"tonight\")**, in a restatement of his own min-09 words.",
    (2, 2, "daniel", 2): "True. A restatement of N2-11.",
    (2, 2, "elena", 0): "True. **Self-justification** for eating what her son gave her: \"I had to survive\". Deeper.",
    (2, 2, "elena", 1): "**Lost to a rule (S5 \"tonight\")**, in a restatement.",
    (2, 2, "elena", 2): "Restatement of her own words.",
    (2, 2, "leo", 0): "**Lost to a rule (S5 \"yesterday\").** A hardened grudge. It also repeats his own exaggeration \"lied all day yesterday\" (Daniel confessed at min 33 of day 1).",
    (2, 2, "leo", 1): "True; the warning is quoted rightly. **Blame.**",
    (2, 2, "mara", 0): "True. A restatement.",
    (2, 2, "mara", 1): "True. A restatement of N2-12.",
    (3, 1, "daniel", 0): "True: six denials. **Self-justification**: he lied \"to protect them\". Deeper.",
    (3, 1, "daniel", 1): "True: his own words made a principle, \"my place alone\". **Self-justification.** Deeper.",
    (3, 1, "elena", 0): "**Lost to a rule (S3 \"one\").** True: a restatement of her count. Elena carries no thought from night 1.",
    (3, 1, "leo", 0): "A judgement of everyone; nobody is blamed. **Resignation.** Deeper.",
    (3, 1, "leo", 1): "True. A restatement.",
    (3, 1, "mara", 0): "True. **Self-justification** of her six questions: \"I only wanted…\". Deeper.",
    (3, 1, "mara", 1): "Restatement of her own words.",
    (3, 2, "daniel", 0): "True: confessed at 33, Leo's stop, went anyway. **Guilt joined to self-justification**: going out to make amends. Deeper.",
    (3, 2, "elena", 0): "True. **Forgiveness**: \"keeping us together matters more than the lie\". Deeper.",
    (3, 2, "elena", 1): "**Check error, a good thought lost.** \"my children took risks\" was read as the *take* family (taking food). True, and her only guilt: \"I stayed in bed while my children took risks\".",
    (3, 2, "leo", 0): "**States a false extent.** Daniel accused Leo only on day 2 (min 18, 21, 27, 30). On day 1 he only denied. Not \"for days\". **Blame only.**",
    (3, 2, "leo", 1): "True. A restatement, with blame.",
    (3, 2, "mara", 0): "True: he lied, he took it, they argued. **Grudge**, with a reason: \"I cannot just forget\".",
    (3, 2, "mara", 1): "True: she waited by the door until he came back before dawn.",
}
INTENT_READING = {
    (1, 1, "mara"): "**Check error.** \"…ask Daniel why he went out into the night and came back with nothing.\" The clause \"came back with nothing\" took the subject \"I\" from the clause before (§2.7, step 2), so it read as Mara coming back. The real subject is \"he\". A good intent lost.",
}


def night_table(s, k):
    tr, _, _ = analyze.load(s)
    n = tr["night" if k == 1 else "night2"]
    out = ["| Ask | Who | Where | Choice | Words | Feeling | Reason |", "|---|---|---|---|---|---|---|"]
    for d in n["decisions"]:
        out.append(f"| {d['ask']} | {NAMES[d['person']]} | {ROOMS.get(d['where'], d['where'])} | `{d['option']}` | "
                   f"{cell(d.get('say'))} | {cell(d.get('feeling'))} | {cell(d.get('reason'))} |")
    seen = [f"{NAMES[x['who']]} {x['how']} of {NAMES[x['of']]}" + ("" if x["noticed"] else " (did not notice)")
            for x in n["noticing"]]
    out.append("")
    out.append(f"- **The house:** {n['house']} portions (draw {n['house_u']:.3f}, made once per seed and kept for later "
               f"nights). Shelf {n['portions_before']} → {n['portions_after']}. Away at dawn: "
               f"{', '.join(NAMES[q] for q in n['away']) or 'nobody'}.")
    for g in n["groups"]:
        out.append(f"- **The trip:** {', '.join(NAMES[q] for q in g['members'])}; street draw {g['u']:.3f} → {g['street']}; "
                   f"found {g['found']}, took {g['took']}: **{g['outcome']}**.")
    if not n["groups"]:
        out.append("- **The trip:** nobody went out.")
    out.append(f"- **Noticing:** {'; '.join(seen) if seen else 'none'}.")
    return "\n".join(out)


def mind_section(s, k):
    tr, _, _ = analyze.load(s)
    prompts = analyze.mind_prompts(s)
    out = []
    for pid, r in tr[f"mind{k}"].items():
        prompt, shown, api = prompts[pid][k]
        n_rec = sum(1 for x in prompt.split("\n") if re.match(r"^\[[DN]\d-\d+\]", x))
        n_early = sum(1 for x in prompt.split("\n") if x.startswith("- ["))
        out.append(f"**{NAMES[pid]}** — prompt {r['prompt_tokens']} tokens estimated, {api} counted by the API; "
                   f"{n_rec} records, {n_early} earlier-days lines; mode `{r['mode']}`.")
        out.append("")
        out.append("| # | Memory | Records it cites (as the prompt showed them) | Check | Reading |")
        out.append("|---|---|---|---|---|")
        for i, m in enumerate(r["memories"]):
            recs = "<br>".join(f"[{x}] {cell(shown.get(x, '(not shown)'))}" for x in m["ids"])
            verdict = "kept" if m["verdict"] == "kept" else m["verdict"].replace("rejected: ", "**rejected** ")
            out.append(f"| {i + 1} | “{cell(m['meaning'])}” | {recs} | {verdict} | {READING[(s, k, pid, i)]} |")
        ans = json.loads(r["answer"])
        intent = r["intent"] or ans.get("intent")
        iv = r["intent_verdict"]
        out.append("")
        out.append(f"- Feeling: *{r['feeling'] or ans.get('feeling')}* ({r['feeling_verdict']}). "
                   f"Intent: “{intent}” ({'kept' if iv == 'kept' else '**' + iv + '**'}).")
        if (s, k, pid) in INTENT_READING:
            out.append(f"  - {INTENT_READING[(s, k, pid)]}")
        out.append("")
    return "\n".join(out).rstrip()


def acts_table(s, d):
    tr, meta, story = analyze.load(s)
    rows = analyze.model_acts(tr, story, d)
    x = meta[f"day{d}"]
    out = [f"meta: api_requests {x['api_requests']}, answers_live {x['answers_live']}, answers_from_cache "
           f"{x['answers_from_cache']}, model_decisions {x['model_decisions']}, fallbacks {x['fallbacks']}, routine_decisions "
           f"{x['routine_decisions']}, lines_spoken {x['lines_spoken']}, private_talks {x['private_talks']}. Unmatched: "
           f"{sum(not r['matched'] for r in rows)} of {len(rows)}.", "",
           "| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['minute']:02d} | {NAMES[r['who']]} | {ROOMS[r['room']]} | `{r['option']}` | {cell(r['words'])} | "
                   f"{cell(r['feeling'])} | {cell(r['reason'])} | {r['mode']} |")
    return "\n".join(out)


def blocks(s):
    tr, meta, story = analyze.load(s)
    part = story[story.index(analyze.TITLE[3]):]
    part = part[part.index("## What each of them carried in"):part.index("## The morning")]
    out = []
    for m in re.finditer(r"\*\*(\w+)\*\*\n\n```\n(.*?)\n```", part, re.S):
        out.append(f"**{m.group(1)}**\n\n" + block(m.group(2)))
    return "\n\n".join(out)


def counts_table():
    out = ["| Seed | Exit | Scene | Asks | API | From cache | Fallbacks | Largest prompt, estimated | Largest prompt, API | Notes |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for s in (1, 2, 3):
        tr, meta, _ = analyze.load(s)
        for k in ("day1", "night", "mind1", "day2", "night2", "mind2", "day3"):
            x = meta[k]
            a = x["answers_live"] + x["answers_from_cache"]
            if k.startswith("mind"):
                fb = sum(r["mode"] == "fallback" for r in tr[k].values())
                note = f"memories {x['memories_proposed']} proposed, {x['memories_kept']} kept, {x['memories_rejected']} rejected"
            elif k.startswith("night"):
                fb = sum(d["mode"] == "fallback" for d in tr[k]["decisions"])
                lv = meta["leavers"] if k == "night" else meta["leavers2"]
                oc = meta["outcome"] if k == "night" else meta["outcome2"]
                note = f"leavers {', '.join(NAMES[q] for q in lv) or 'none'}" + (f"; {oc[0]}" if oc else "")
            else:
                fb = x["fallbacks"]
                note = "v11, replayed" if k == "day1" else (
                    f"{x['lines_spoken']} lines, {x['trip_acts']} trip acts, {x.get('food_moments')} food moments, "
                    f"{x.get('give_answers')} give answers")
            name = {"night": "night 1"}.get(k, k.replace("day", "day ").replace("mind", "mind ").replace("night2", "night 2"))
            out.append(f"| {s} | {'0' if k == 'day1' else ''} | {name} | {a} | {x['api_requests']} | {x['answers_from_cache']} | "
                       f"{fb} | {x.get('max_prompt_tokens_estimated')} | {x.get('max_prompt_tokens_counted_by_api')} | {note} |")
        m6 = sum(meta[k] for k in ("night1_asks", "mind1_asks", "day2_asks", "night2_asks", "mind2_asks", "day3_asks"))
        out.append(f"| {s} | | **total** | {meta['answers_live'] + meta['answers_from_cache']} | **{meta['api_requests']}** | "
                   f"{meta['answers_from_cache']} | 0 | {meta['max_prompt_tokens_estimated']} | "
                   f"{meta['max_prompt_tokens_counted_by_api']} | **M6 sum {m6}**; {meta['run_seconds']} s |")
    return "\n".join(out)


fills = {"COUNTS": counts_table()}
for s in (1, 2, 3):
    fills[f"BLOCKS_{s}"] = blocks(s)
    for k in (1, 2):
        fills[f"NIGHT_{s}_{k}"] = night_table(s, k)
        fills[f"MIND_{s}_{k}"] = mind_section(s, k)
    for d in (2, 3):
        fills[f"ACTS_{s}_{d}"] = acts_table(s, d)
for name in os.listdir(os.path.join(S, "cmd")):
    fills["CMD_" + name[:-4].upper()] = block(read(os.path.join("cmd", name)))
fills["SCRIPTS"] = "\n\n".join(f"`$S/{n}`:\n\n" + block(read(n), "python") for n in ("analyze.py", "r5.py", "m2.py", "cachecheck.py",
                                                                     "night1_vs_v13.py", "accuse.py", "build.py"))

head = read("head.md")
for key, text in fills.items():
    marker = re.compile(r"\{\{" + key + r"\}\}")
    n = len(marker.findall(head))
    assert n <= 1, key
    head = marker.sub(lambda _: text, head)
left = re.findall(r"\{\{[A-Z0-9_]+\}\}", head)
assert not left, left
with open("reports/days_v15.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(head + "\n")
print("wrote reports/days_v15.md,", head.count("\n") + 1, "lines")
````
