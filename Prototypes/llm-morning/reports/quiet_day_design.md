# Design: the quiet day (days 3 to 7, the starving house)

Mode: design. No code was written, no API was called, no cache was touched. The night mind and block C are not
changed by anything here. No character, creature or new person is added. Paths are relative to
`Prototypes/llm-morning/`.
- **Sources read:** `reports/days_v15.md` (§1, §8, §9.2), `reports/days_v16.md`, the code that ends a day
  (`world.py`, `talk.py`) and decides trips (`night.py`), and the runs in `runs/v15` and `runs/v16`.
- **"§1.1" of days_v15.md:** days_v15.md has no §1.1. Its §9.2 cites "§1.1, 'no new pressure or event'", which is
  `reports/days_design.md` §1.1. Both were read.
- **The North Star doc:** no document by that name exists besides the "North Star principles" section of
  `CLAUDE.md:21-28` (**NOT FOUND** elsewhere; `reports/days_design.md:11` found the same). It is used only as a far
  reference.
- **Scripts:** the read-only scripts behind every number are in the session scratchpad `$S`, with their output in
  §9.

## Summary

| Part | The design in one line |
|---|---|
| 1. Needs | Two needs. **Fasting** (hours since food × hunger rate) takes over where hunger stops at "starving"; it has thresholds at 48 and 96. **Sleep debt** (+1 an hour awake, paid back by the night's choice) has thresholds at 16 and 24. Cold is cut (nothing cites it). Thirst is cut: one reason in 12 days cites it, and it first needs a stored-water fact the code has never fixed. |
| 2. Routines | Four, chosen by code when no conversation is going: **withdraw** to one's own room after going silent in a quarrel, **rest** on one's bed when tired, **keep watch** by the front door for whoever is against a trip, **watch the street** at the boarded window for whoever means to go. The fifth, sitting in the kitchen, is today's default. |
| 3. Time skipping | The morning is played in 3-minute turns, as now, until its conversation ends. Then the day jumps from one event to the next (a routine ending, a need crossing a line, an arrival), up to bedtime at 21:00. Each span is a chronicle event with witnesses, and block A's "the afternoon and evening passed" line becomes those spans. |
| 4. LLM triggers | Four quiet-stretch triggers: a need crossing a line with company (Q1), a grievance meeting after an hour apart (Q2), the door collision between going and stopping (Q3), and someone showing distress to an empathetic person (Q4). **At most 12 quiet asks and 40 day asks per game day.** |
| 5. Ways out | Existing: food on the shelf (empty), the night trip next door (empty in seeds 1–3), stopping or joining, and waiting. Proposed: the street table gets worse with weakness, and one new way, **further along the street**, the only one that can bring food in seeds 1–3. |
| 6. Frozen cases | v16 seed 2 day 3 becomes a sleepless family going back to bed, then a confrontation at 10:21 when they meet again: **about 30–40 day asks** (v16: 24). A day 5 of the same seed is 20–40, shaped by weakness and the door. |
| 7. Predictions | Six, each with a counting rule, among them N9 (P1) and N11 (P2). |

---

## 0. What the code does now, and what the runs show

**How a day ends:**
- **A morning is 30 turns of 3 minutes** (`data.py:76-77`, `world.py:378`), min 00 to 87. Then the day is over.
- **A conversation ends after two full turns with nothing new** (`world.py:79`, `talk.py:125-138`).
- **After that, the model is asked only for** a trigger (something new, or anything while a room is talking), an
  inner moment (a level rose), the trip moment, or a lull (`world.py:1354`). **Lulls are off**
  (`world.py:82`, `reports/lulls_off.md`), because they "mostly replaced silence with repeated reassurance, three
  times word for word, which is less human than the silence".
- **Without the model, `routine` is "stay put"** (`world.py:726-733`): keep searching, keep sitting, or `silent`. A
  routine never moves anyone.
- **The afternoon and evening are one line**, "The afternoon and evening passed in the house. Nobody ate."
  (`data.py:102`). They add hunger 0.3 × rate (`night.py:228`); the night adds 0.1 × rate (`night.py:275`).
- **Hunger stops at 1.0** (`world.py:1278`). An inner moment needs a level to rise (`world.py:823-830`).

**How trips are decided:**
- **The trip concern opens** when the shelf is empty or someone is very hungry (`world.py:616-632`). On day 2 and
  later it is open from min 00.
- **Positions** (volunteer, send, nobody goes, keep X home, refuse) are speech options (`world.py:576-605`). At
  bedtime, whoever last said they will go gets the PROMISE line (`night.py:56`, `night.py:252-253`).
- **Bedtime has four choices:** sleep, lie awake, watch the door, go next door (`night.py:46`).
- **The world answers with two draws:**
  - the neighbour's house, once per seed (`night.py:33`; **0 portions in seeds 1–3**, night_design §4.4);
  - the street, from the ALONE or GROUP table (`night.py:34-35`): not back 6% alone, 3% in a group.

**What v15 and v16 show on days 2 and 3** (12 days; `$S/baseline.py`, §9.2):
- **The house goes silent:** 12 of 12 days have at least 5 turns in a row in which every act is `silent`. Day 3 of
  v16 seed 2 is silent from min 18 to 87, 24 turns.
- **Nobody ever leaves the kitchen:** 0 moves in all 12 days. days_v15 §8 also records "No search, sit, move or
  private talk".
- **Repetition:** the same person makes the same kind of act 3 or more times running in 11 of 12 days. N11 is
  present by hand in 4 of 6 v15 days (days_v15 §8).
- **Hunger is spent:** in v16 seed 2, all four are at hunger 1.0 by night 2's bedtime
  (`night2.bedtime_hunger`). On day 3 there are **0 inner moments**: no level can rise.
- **The body is invented by the model:**
  - 26 acts on v16 days 2–3 have the feeling "exhausted", "weary" or "tired";
  - 20 of 24 mind-2 feelings in v15 and v16 say exhausted or weary;
  - 46 of 48 bedtime choices were not "sleep";
  - the code has no number for any of it.
- **Day 3 is short when nothing is new:** 13 and 18 asks in v15 seeds 2 and 3, 24 and 25 in v16. Day 2 asked 24 and
  70.

**What a real family would do here.** A family three days into hunger, after nights of lying awake, would:
- argue in the kitchen in the morning;
- go back to bed, or walk out of the room when it gets too much;
- sit near the door if they feared someone going out;
- stare at the street if they meant to go;
- meet again in the kitchen later, and pick the quarrel up again or not.

They would not sit together in silence for 75 minutes, every morning. Their talk would be about their bodies:
"I can't stand up without my head spinning." The design gives the code the bodies and the comings and goings, and
asks the model only when two people meet with something between them.

---

## 1. Needs

**Kept to two.** Each grows by code, and each changes situations at a threshold, never acts. The body line states
the situation. The choice stays the model's (`CLAUDE.md:26-27`).

### 1.1 Fasting (hunger past "starving")

| | |
|---|---|
| **Fixes** | **(a)** Hunger is stuck at 1.0 from day 2, so it can never rise again. v16 seed 2 has all four at 1.0 at night-2 bedtime, and day 3 has 0 inner moments (§9.2). **(b)** The family speaks of the body: "we are all starving" (v16 seed 2, day 3, min 00, Elena); "my stomach is completely empty" (v16 seed 3, day 3, min 09, Mara's reason). The code has no stage beyond "starving" to back them. **(c)** N9: with nothing able to change inside anyone, nothing triggers anyone. |
| **The number** | `fast` = hours since that person last ate × their `hunger_rate` (`data.py`: Daniel 1.15, Elena 0.85, Leo 1.0, Mara 0.95). It is counted by code from the chronicle's eat events, and set to 0 by eating. The 0–1 hunger stays for its words ("starving"). |
| **An open fact, fixed by code** | When each of them last ate before day 1 is not in the data. It is fixed the first time it matters (days_design §4.3): the evening meal of house day 3, 19:00, 12 hours before the count. Daniel's is the can, at 03:00 on house day 4. |
| **Rough rate** | Without food, about 1 an hour (1.15 for Daniel). From the last meal, "weak" comes about 2 days later and "very weak" about 4 days later. |
| **Thresholds** | **weak at 48**, **very weak at 96**. |

**At each threshold:**

| Stage | The body line (a situation, no act) | Options | Routine | The world |
|---|---|---|---|---|
| **weak** (≥ 48) | "Your body: starving, and weak from it: standing up makes your head spin." | none added, none removed | rest is preferred when quiet (§2) | the street table shifts (§5, W2) |
| **very weak** (≥ 96) | "Your body: starving, and very weak: your legs shake when you stand." | none removed: going out stays their choice | rest starts as soon as the morning's talk ends | a larger shift (§5) |

**Mood:** no mood number. The body line is what the model reads, and the model owns how it feels
(`CLAUDE.md:22-23`). Nothing in v15 or v16 cites a code mood, so none is added.

**Arguing against it first:**
- **Is "weak after two days, very weak after four" real?** With some water, people last weeks without food. But
  dizziness on standing and weakness are common within two to four days. Their water is stored, not running
  (`data.py:131-134`), and no thirst is modelled.
- **Does a stage make the model act weak?** The line states a situation ("your head spins"), not an act ("you sit
  down"). The North Star rule against act lines holds.
- **The risk:** the model may lean on the body line as a reason to do nothing. If the predictions show more
  `silent` acts with weakness as the reason and no other change, the stage line is the first thing to cut.

### 1.2 Sleep debt (tiredness)

| | |
|---|---|
| **Fixes** | **(a)** 46 of 48 bedtime choices in v15 and v16 were `lie_awake`, `watch_door` or `go_next_door` (§9.3), and none of them cost anything. **(b)** The model makes them tired with no code state: 20 of 24 mind-2 feelings say exhausted or weary (v16 seed 2: "empty and weary", "anxious and weary", "exhausted and resentful", "anxious and exhausted"). 26 day acts have a tired feeling. "There is no point in arguing in circles about the missing can when we are all just hungry and tired" (v16 seed 3, day 2, min 33, Leo). "I am too tired of all the fighting and hunger to say anything more right now" (v16 seed 3, day 2, min 54, Mara). This is the AI owning state (`CLAUDE.md:22-23`). |
| **The number** | `debt`: +1 for each hour awake. At night: `sleep` pays back 8, or 6 while starving; `lie_awake` 3; `watch_door` and `go_next_door` 0. Resting on one's bed by day pays back 1.5 an hour. The floor is 0. Everyone starts day 1 at 0. |
| **Rough rate** | A 14-hour day adds 14. Two nights lying awake leave anyone at about 22 by morning (§6.1). |
| **Thresholds** | **tired at 16**, **exhausted at 24**. |

**At each threshold:**

| Stage | The body line | Options | Routine | Night |
|---|---|---|---|---|
| **tired** (≥ 16) | "…and you have hardly slept." | unchanged | rest when quiet (§2.2) | unchanged |
| **exhausted** (≥ 24) | "…and you have barely slept for nights; your eyes close on their own." | unchanged | rest as soon as the talk ends | someone watching the door or lying awake may doze: a draw `0.3 + 0.05 × (debt − 24)`, at most 0.7. A dozer notices nothing (`night.py:87-95` noticing is skipped for them). |

**Arguing against it first:**
- **Would a real person sleep in the day while starving?** Yes. Hunger and sleepless nights make people lie down;
  rest by day is a common way to bear hunger.
- **Would a mother doze at the door she meant to watch?** On her third sleepless night, yes. The draw is unhuman,
  and the output ("you woke at the door; you had dozed") reads as human (`CLAUDE.md:28`).
- **What it costs:** a night someone was watching for can now pass unseen. That changes who knows who went out,
  which is the point: no v15/v16 watcher ever failed.

### 1.3 Cut, because nothing in v15 or v16 cites them

- **Thirst.** The taps are dry (`data.py:91`), and Leo said to fill everything (backstory, day 1).
  - **One line cites it**, in 12 days: v15 seed 1, day 2, min 06, Leo, `silent`, feeling exhausted, reason "There is
    nothing left to argue about when we have no food and no water." (§9.4). The code holds no water number, so this
    reason claims a state the code does not own, as tiredness does.
  - **It is still cut.** One reason in 12 days does not earn a need, and a water need first needs an open fact the
    code has never fixed: how much was stored on day 1.
  - **What to do before any later design adds it:** fix that fact, so a line like Leo's is checked against something.
- **Cold.** "You felt cold" (v15/v16 seed 2, D2-009) is a feeling about Daniel, not the body. Cut.
- **Boredom or company.** No line asks for it. Being apart and meeting again is done by routines and triggers, not
  by a need.

---

## 2. Routines

**What a routine is:**
- **Who chooses it:** code, from the needs, the standing trip position and the last act. Only when no
  conversation is going in the person's room.
- **What it is:** a place and a posture. It is never words, and never a choice of whom to comfort or suspect (N8
  keeps those for the model).
- **How it is recorded:** each routine is a chronicle event with witnesses (§3).
- **Priority, highest first:** withdraw > rest (exhausted) > keep watch / watch the street > rest (tired) > sit in
  the kitchen.

### 2.1 Withdraw to one's own room

| | |
|---|---|
| **Fixes** | **N9 and N11.** v16 seed 2, day 3, min 12: Leo chooses `silent`, feeling exhausted, reason "I have said enough to Daniel and nothing changes his reckless behavior". He then stays silent in the kitchen with Daniel until min 87. v16 seed 1, day 2, min 06 and 15: Leo, `silent`, "There is no point in arguing further when words change nothing". He stays too. 0 moves in 12 of 12 days. |
| **Rule** | At the end of a played turn, a person withdraws to their own room when all of these hold: they chose `silent`; they spoke earlier in this conversation; they hold a grudge of 3 against someone still in the room; and they are neither Daniel (dominant 0.85) nor Elena (empathetic 0.9). Withdrawing is moving, as `go_*` does now (`world.py:1243-1246`). The others see "Leo goes to the brothers room". |
| **Interrupted by** | anyone coming into their room (an arrival, §4 Q2), voices, or bedtime. |

**Arguing against it first:**
- **Is "silent" the same as wanting to leave?** Not always. So the rule needs both a grudge at 3 and having
  spoken: this is the person who has said their piece and holds the anger.
- **Daniel** (proud, dominant, "believes responsibility is his", `data.py:20-24`) would stay and argue.
- **Elena** ("fears the household breaking apart", `data.py:29-31`) would stay.
- **Why code rather than the model:** the existing `go_brothers_room` option has been offered on every one of
  these turns and was never chosen. The trait gate is unhuman; the walk-out reads as human.

### 2.2 Rest on one's own bed

| | |
|---|---|
| **Fixes** | §1.2 (a)–(b). v16 seed 3, day 3, min 09: Mara chooses `silent`, "I am too tired of arguing and having my anger dismissed when my stomach is completely empty". She stays in the kitchen. |
| **Rule** | When quiet: debt ≥ 16, or fasting ≥ 96 → lie on one's own bed. It lasts until debt < 12 or 3 hours have passed, at most twice a day and at least 2 hours apart. |
| **Interrupted by** | an arrival in the room with a Q2 grievance, voices of a new line through the wall (existing triggers, `world.py:1258-1270`), the front door, or bedtime. |

**Arguing against it first:**
- **Does it hide the family away all day,** leaving four people asleep and nothing to read?
- The cap of two rests a day, with 2 hours between them, keeps them awake for most of the afternoon and all of the
  evening.
- Sleep after nights of lying awake is the most human thing in the list.

### 2.3 Keep watch by the front door

| | |
|---|---|
| **Fixes** | **N11 (the against kind):** v15 seed 3, day 2: Elena's against kind at 42, 45, 48. v16 seed 1, day 3: Elena's against kind ×4 and Leo's ×3. Also v16 seed 2, mind 2, Elena's intent "I will make sure nobody leaves the house and we stay together safely", which today has no act but words. |
| **Rule** | When quiet, someone whose standing trip position is "against" (`nobody_goes` or `keep_X_home`) sits in the kitchen by the front door. The standing position is their latest trip act on any day. It is cleared when a trip happens that night (it has been tested), or when they take another position. |
| **Interrupted by** | someone coming to the door (Q3), tiredness (exhausted → rest wins), or bedtime. At bedtime it is not a choice: the four bedtime options stay as they are. |

**Arguing against it first:**
- **Would she sit by a boarded door all afternoon?** A mother who fears a son going out would stay where she can
  see the door. The night option "sit up in the kitchen by the front door" (`night.py:48-49`) is the same act by
  night, and the model chose it (v15 seed 1, night 2, Elena).
- **The risk:** it makes Elena the jailer. It is cut if the run shows her watch preventing nothing and adding
  nothing.

### 2.4 Watch the street at the boarded window

| | |
|---|---|
| **Fixes** | **N11 (the volunteer kind):** v16 seed 1, day 3: Mara's volunteer kind ×7, 06–36, while all three forbid her. v15 seed 3, day 2: Daniel's ×6, 42–57. The position is said over and over because it can only be said. |
| **Rule** | When quiet, someone whose standing trip position is "volunteer" stands at the front windows (boarded, `data.py:95`) and looks out through the gaps. Once an hour the code tells them what they see, from a draw tied to tonight's street draw: "Something was moving in the street" is more likely when tonight's draw is a scare or worse. The wording is the outcome table's own; nothing new is in the street. |
| **Interrupted by** | Q3, rest, or bedtime. |

**Arguing against it first:**
- **Does tying the window to tonight's draw leak the future?** It gives evidence, not the outcome. A real person
  watching the street learns something about it.
- **The code draws a conclusion from what they perceive; the AI decides** (`CLAUDE.md:24-25`).
- **The risk:** a cautious model may treat any movement as a reason never to go. That would be a real family's
  reason too.

### 2.5 Sit in the kitchen (today's default)

When nothing above applies, they sit in the kitchen, where the family gathers. This is today's `silent`
(`world.py:733`). It cites N9 as the thing the other four replace. It is not a new routine.

---

## 3. Time skipping

**The clock.** Min 00 is 07:00, when they get up and the opening is seen. Bedtime is 21:00 (min 840). The night is
as now.

**When the sim jumps:**
1. **The morning is played** in 3-minute turns exactly as now, from the opening, until every room's conversation
   has ended (`talk.py:125-138`), or the day budget is spent (§4).
2. **Then quiet mode:**
   - code assigns each person a routine (§2);
   - it computes the next event: someone's routine ending; a need crossing a line (§1); an arrival from a
     routine's move; the window's hourly look; 21:00;
   - **it jumps straight there,** with no turn-by-turn silence;
   - at that event, if a trigger fires (§4), played 3-minute turns resume in that room until its conversation ends,
     then quiet mode again;
   - **the largest possible jump** is from one event to the next. No jump crosses 21:00.
3. **The needs** are advanced by exact hours across the jump: fasting by rate, debt by awake or resting hours.

**What it records,** so the night mind and memory see the skipped hours:
- **One chronicle event per routine span:** `{"scene": "D{k}", "minute": start, "kind": "routine", "routine":
  "rest"|"withdraw"|"watch_door"|"watch_street"|"sit", "actor", "room", "until": end, "witnesses",
  "views"}`.
- **Witnesses:** the actor did it; whoever was in the room at its start or its end saw it. A routine is silent, so
  nobody hears it through a wall.
- **Views** in each person's own words, as now (`world.py` views): "You lay on your bed in the brothers room from
  min 18 to min 198; Daniel came in at min 21 and lay down." Window looks and need crossings are their own events,
  with the actor alone as witness.
- **The night mind needs no change** (`mind.py:48-79`): `records()` takes every D-scene event the person
  witnessed, in order, with its view. Spans arrive as "min 018: …", one record per span. The 1,600-token bound
  holds: a quiet day adds about 8–16 records, against the 11–33 the night minds saw (days_v15 §1).
- **The cost of not touching the night mind:** a record reads "min 330", a strange way to say mid-afternoon.
  Changing it would change the night mind, which is out of scope.
- **Block A:** its last line is `data.GAP` (Y8, `night.py:737`). From day 3 on, that line becomes a code-written
  summary of the person's own spans, e.g. "After the morning: you lay on your bed (min 18–198); you sat in the
  kitchen with Elena, Leo and Daniel (min 198–…). Nobody ate." Block C is untouched: a routine is not in its
  weight table, so C never shows one.
- **The bedtime prompt** says "Now it is night." followed by the same summary in place of `data.GAP`
  (`night.py:243-246`).

**Arguing against it first:**
- **Does skipping hide life?** It skips only what is the same: a person on a bed is still on the bed. Every change
  is an event.
- **The real risk:** what happens between two events is never played, so a quarrel that would have flared at
  14:00 waits for an arrival. Q2 is designed for that meeting.

---

## 4. LLM triggers during a quiet stretch

**General rules:**
- Outside these four, the quiet stretch calls the model **zero** times.
- Each trigger asks one person. If they speak to someone, the existing addressed-first order
  (`world.py:1131-1151`) plays the reply, and the room is back in played turns until its conversation ends.
- The options are today's, unchanged.

| # | Exact condition | Who is asked | Fixes (citation) |
|---|---|---|---|
| **Q1. A need crosses a line with company** | Fasting reaches 48 or 96, or debt reaches 24, during quiet mode, while at least one other awake person is in the same room. Once per person per threshold. With nobody there, it is recorded only. | the person; their prompt has the existing inner line ("Since you last decided, you have grown weaker.") | §1.1 (a): 0 inner moments on v16 seed 2's day 3. Hunger can no longer rise, so nothing inside anyone ever asks. |
| **Q2. A grievance meets** | A routine brings A into a room where B is. B holds a grudge ≥ 2 against A, or A against B. The two have not exchanged a line for ≥ 60 game minutes. Once per pair per 2 hours. | the holder of the higher grudge (B first on a tie) | **N9:** v16 seed 2, day 3: Leo and Mara hold 3 against Daniel and sit with him in silence from min 18 to 87. **N11:** their confrontations at 00, 03, 06 and 09 come in one unbroken sitting. Meeting again after hours apart puts the quarrel in a new situation (the time, the bodies, where each was). |
| **Q3. The door** | Someone watching the street (§2.4) and someone keeping watch at the door (§2.3) are in the kitchen together, at the start of the stretch or by an arrival. Once per pair per day. | the one watching the street first, then the watcher by the existing order | **N11:** v16 seed 1, day 3: Mara's volunteer kind ×7 and Elena's against kind ×4, said across the table and never meeting at the door. |
| **Q4. Distress with someone near** | In quiet mode, someone's shown feeling has strength ≥ 2 (`world.py:141-147`; e.g. "frightened", "deeply anxious"), and an awake person with empathetic ≥ 0.7 and no grudge ≥ 2 against them is in the same room or the next. Once per pair per day. | the empathetic person (Elena 0.9, Mara 0.75, Leo 0.7); whom to comfort stays the model's choice (N8) | **N9:** v15 seed 2, day 3: Mara's "frightened" at min 03 shows until 12, then silence to 87 (days_v15 §8). There is no sit act on any day 2 or 3 (days_v15 §8). |

**Cut from the list:**
- **Asking on an intent.** The intent is the AI's words; the code cannot read whom it names without parsing them.
  Intents already reach acts the next morning (E7 PASS 3 of 3, days_v15 §7).
- **Lulls.** They were tried, and turned silence into repeated reassurance (`reports/lulls_off.md`).

**The budget per game day** (day 3 on):

| Part | At most |
|---|---|
| Quiet triggers (Q1–Q4) | **12**, and 4 per person |
| All day asks (the played morning + every played stretch the triggers start + the quiet triggers) | **40**. When reached, every room's conversation ends and everyone goes to routines until bedtime. |
| Night | today's rules (4–12) |
| Night mind | one per person in the house (4) |
| **A game day** | **at most 56**, typically 30–45 |

- **For five days (3–7) and one seed:** about 150–225, at most 280. Three seeds do not fit in one 500-request
  quota day. Run one seed per quota day.
- **Arguing against the cap:** a family does not stop arguing at a count. But v15 and v16 day 3s asked 13–63, and
  the highest (v16 seed 1, 63) was Mara's 8 volunteer acts while three people forbade her. That is the
  repetition the cap cuts.

---

## 5. Ways out

**These are the decisions on days 3–7 that could change the house's situation:** food in the house, someone gone,
or the family's place. "Exists" means the code has it today.

| # | Decision | Exists? | How the world answers |
|---|---|---|---|
| **W1** | Eat, give or share from the shelf | **yes** (`world.py:529-532`, `world.py:768-775`) | Exactly. In seed 2 the shelf is empty from day 2 min 00. It changes nothing unless food comes in. |
| **W2** | Go next door at night, alone or joined | **yes** (`night.py:46`, `night.py:500-585`) | **The house** is drawn once per seed (`night.py:33`): 0 portions in seeds 1–3, so every trip brings nothing. **The street:** today ALONE (clean .62, scare there .14, scare back .18, not back .06) and GROUP (.70/.12/.15/.03). **Proposed, weighted by the body:** weak: ALONE .58/.14/.18/.10; very weak: .50/.14/.20/.16; exhausted: +.02 not back, taken from clean. A group takes its weakest member's shift at half size. |
| **W3** | Stop someone at night, or watch the door | **yes** (night stops; `watch_door`) | The existing noticing draws (`night.py:87-95`), with the proposed doze draw for the exhausted (§1.2). |
| **W4** | Wait | **yes** (the default) | Fasting stages (§1.1), and W2's table worsens each day they wait. |
| **W5** | **Go further along the street,** past the neighbour's, to the next houses | **no** (`HOUSE_THINGS` names only the street and the neighbour's house, `data.py:91-99`) | **The only way out that can bring food in seeds 1–3.** Each further house's food is drawn once from the HOUSE table (`night.py:33`), fixed when first entered. **Street:** FAR_ALONE .45/.17/.23/.15; FAR_GROUP .55/.15/.22/.08; with the body shifts of W2. It adds places, but no person and no creature. Offered as one more bedtime choice and one more day trip position, only after someone has been inside the neighbour's house. |
| **W6** | Go by day | **no** ("not to be gone to this morning", `data.py:104-106`) | **Not proposed.** No v15 or v16 line asks for a day trip; every trip line is about tonight. |
| **W7** | All four leave the house for good | **no** | **Not proposed here.** It ends the house's story; it is the Director's decision (days_design §5, item 6). The world's answer would be GROUP-type draws for four, per crossing. |
| **W8** | Signal for help, or look for other survivors | **no** | **Excluded:** it adds characters, which the brief rules out. |

**What a real family would do.** Once next door is known empty, a starving family's question becomes whether to
go further, who goes, and who can still walk. W2's shift and W5 make that question one the world answers
differently each day: waiting costs strength, and strength is what the street needs.

**Arguing against W5:**
- **Is it a new pressure from outside,** which days_design §1.1 kept out? It is a place, not a pressure, and its
  danger is higher than next door's.
- Without it, seeds 1–3 have no way out at all after night 2. Days 3–7 would be a slow wait for the cap.

---

## 6. Frozen cases

**The starting point** is everything as it happened through night 2 of v16 seed 2. The quiet layer applies from day
3. The needs are counted from day 1 (§1).

**Fasting at day 3, 07:00:**

| Person | Last ate | Fasting | Stage |
|---|---|---|---|
| Daniel | the can, 03:00 house day 4 | 59.8 | weak |
| Leo | house day 3, 19:00 (the fixed fact) | 60 | weak |
| Mara | day 1, min 54 | 44.7 | not yet; weak at 10:24 |
| Elena | the given portion, day 2, min 00 | 20.4 | not yet |

**Sleep debt at day 3, 07:00:** night 1, all four lay awake; night 2, Daniel went out, Elena slept, Leo and Mara lay
awake (§9.3). Daniel 25 (exhausted); Leo 22, Mara 22, Elena 19 (tired).

**Grudges at the start of day 3:** Leo → Daniel 3, Mara → Daniel 3; all others 0 (day 2 end state, §9.5).

**Standing positions:** none. Night 2's trip happened, which clears them.

### 6.1 v16 seed 2, day 3: the predicted shape

| Time (min) | What code does | Where the model is called | Asks (expected) |
|---|---|---|---|
| 07:00–07:15 (00–15) | The opening, as v16. The body lines are new: weak for Daniel and Leo; hardly slept for all four, barely slept for Daniel. So every prompt is new and live. | the played morning, as v16: Leo and Mara confront Daniel about night 2, and Elena reassures | **18–24** (v16: 24) |
| ~07:15 (12–15) | If Leo again chooses `silent` with a grudge of 3 (as v16 min 12), **withdraw**: Leo goes to the brothers room. The others see it. | — | 0 |
| ~07:18–07:21 | The kitchen conversation ends: two quiet turns. **Quiet mode.** Routines: all four are tired, so all four **rest**. Daniel goes to the brothers room, where Leo is. | Q2 does not fire: Leo and Daniel spoke within the last 60 minutes | 0 |
| 07:21–10:21 | One jump. Four rest spans are recorded: Daniel and Leo in the brothers room, Elena and Mara in the back room. Each sees the other in their room. Debt falls by 4.5 (Daniel 25 → 20.5, Leo → 17.5, Mara → 17.5, Elena → 14.5). | none | 0 |
| ~10:15–10:21 | The rests end (3 hours). Leo goes to the kitchen at 10:15. Daniel, Elena and Mara follow at 10:21: these are arrivals. | **Q2:** Leo (3 against Daniel; last line between them ~07:12) is asked first, then Mara. Daniel answers when addressed. Played turns resume in the kitchen. | **6–12** |
| ~10:24 | Mara's fasting reaches 48: **weak**. She is in company, inside the played conversation, so it is her inner moment there (no extra ask). | inside the played turns | 0 extra |
| ~10:40 | The conversation ends. Leo may withdraw again (§2.1). Elena, debt 14.5 and not tired, sits in the kitchen. | — | 0 |
| ~12:40–15:40 | Second rests: Daniel, Leo and Mara (debt back to ≥ 16). Elena is alone in the kitchen: no trigger (nobody there; Q4 needs someone's feeling shown). | **Q4** at most once, if Mara's feeling shows strength ≥ 2 when she lies down in the back room next door to Elena | **0–2** |
| ~15:40–18:00 | Back in the kitchen. Arrivals: Q2 only if 60 minutes have passed since the 10:21–10:40 exchange (yes for both pairs). A second meeting, about the same night. | **Q2**, at most once per pair in 2 hours | **4–10** |
| 18:00–21:00 | Everyone is awake (no third rest). If someone takes a trip position in these turns, it becomes a standing position, for W2 tonight. | only if a trip position is spoken | **0–6** |
| 21:00 | Bedtime, as now. Daniel's debt is ~24: if he watches or lies awake, he may doze. | the night | **4–8** |
| dawn | The night mind, unchanged. It sees about 8–14 new records (the spans). | mind 3 | **4** |

- **Day asks:** about 28–40 (v16: 24), with 2–3 meetings instead of one morning.
- **Moves:** at least 8 (v16: 0).
- **The longest frozen stretch** of two or more awake people together: under 60 minutes, if the rests land as
  above. That is P1's test.

### 6.2 v16 seed 2, day 5: the predicted shape

**Conditions:** nights 3 and 4 bring no food (next door is empty and W5 is not taken), and nobody is lost. Every
time and count below follows only if those hold.

**At day 5, 07:00:**

| Person | Fasting | Stage |
|---|---|---|
| Daniel | 101 | very weak (since day 4, 14:30) |
| Leo | 108 | very weak (since day 4, 19:00) |
| Mara | 91 | weak; very weak at 12:57 |
| Elena | 61 | weak (since day 4, 15:30) |

**Sleep debt** hovers at 15–22 for everyone: each day adds 14, naps take back 9–13, lying awake takes back 3. So
all four are tired most mornings, and anyone who watched a night is exhausted.

**Standing positions:** likely someone has volunteered on day 3 or 4 (v15/v16 seed 1's Mara, and seeds 2 and 3's
Daniel). Elena's against position likely stands again.

| Time | What code does | Where the model is called | Asks (expected) |
|---|---|---|---|
| 07:00–~07:15 | The opening. The body lines say very weak for Daniel and Leo. | the played morning | **12–24** |
| ~07:15 | The talk ends. Daniel and Leo **rest** at once (very weak). Mara rests (tired). Elena **keeps watch** by the door if her against position stands, otherwise she rests. | none | 0 |
| ~07:15–10:15 | A jump of rest spans; Elena's watch span. | none | 0 |
| ~10:15 | The rests end. If someone holds a volunteer position, **watch the street** begins at the window. The window's first look is drawn. | **Q3** if Elena is at the door: the volunteer first, then Elena. **Q2** for the grudge pairs on arrival. | **6–14** |
| ~12:57 | Mara reaches **very weak**. If she has company, **Q1** asks her; alone, it is recorded only. | **Q1** | **0–1** |
| ~13:00–16:00 | Second rests. The window's looks are hourly for whoever watches the street. | **Q4** at most once | **0–2** |
| 16:00–21:00 | All awake in the kitchen. The trip question: the volunteer's standing position, W2's weakened table (their body is not shown as a number, only as the body line), W5 only if someone was inside next door (Daniel was, on night 2). | **Q2/Q3** if not used in the last 2 hours | **2–10** |
| 21:00 | Bedtime: whoever holds a volunteer position gets PROMISE. The doze draw applies to exhausted watchers. | the night | **4–12** |
| dawn | mind 5 | | **4** |

- **Day asks:** about 20–40.
- **What changes from day 3:**
  - fewer and later meetings (very weak people rest longer);
  - a door collision (Q3) instead of seven "I will go" acts;
  - a night trip with worse odds.

---

## 7. Predictions

**The run they apply to:** seeds 1–3, days 3–7 (15 game days), on the design's implementation, from v16's days 1–2
and nights 1–2.
- **What the transcript must hold for scripts:** per day, the played `turns`, a `quiet` list of spans
  (`who`, `start`, `end`, `room`, `routine`), each person's `fast` and `debt` by minute, the trigger kind of each
  quiet ask, and meta per scene.
- **Baselines** are from v15 and v16 days 2–3 (`$S/baseline.py`, §9.2).

| # | Prediction | Counting rule | Baseline |
|---|---|---|---|
| **P1 (N9)** | Frozen silence on **at most 3 of the 15 days** | A day counts if, between min 00 and bedtime: **(a)** ≥ 5 played turns in a row have every act `silent`; or **(b)** a span of ≥ 60 game minutes has ≥ 2 awake people in one room, none of whom changes room or routine, speaks, or shows a feeling (`strength ≥ 1`). **Note:** (a) is nearly impossible by construction, because quiet mode starts when talk ends. The prediction stands on (b). | (a) in **12 of 12** days |
| **P2 (N11)** | Same-kind runs on **at most 7 of the 15 days** | A day counts if one person makes ≥ 3 consecutive model acts of one kind (accuse, confront, reassure; the volunteer kind; the against kind; ask; deny), all in one conversation (between one `started` and the next `ended` in `convo_log`), all at the same target (or all at everyone). **And** the target's model acts between the first and the last are all one kind. | without the target clause: **11 of 12** days |
| **P3** | Someone changes room on **every** day: 15 of 15 days have ≥ 2 room changes | Played `moved_to` plus room changes between consecutive quiet spans of one person, counted on awake hours. | **0 of 12** days had any move |
| **P4** | Needs are owned by code | Of all model acts on days 3–7 whose feeling or reason contains `tired`, `exhausted`, `weary` or `sleep*`, **≥ 90%** are by someone with `debt ≥ 16` at that minute. Of those containing `weak`, `dizzy`, `faint` or `head spin*`, ≥ 90% have `fast ≥ 48`. | 26 tired acts in v16 days 2–3, with no code state (**0%**) |
| **P5** | The budget holds | Every day 3–7 of every seed: quiet-trigger asks ≤ 12, day asks ≤ 40, night ≤ 12, mind = people in the house. Each seed's days 3–7 total ≤ 280. From meta. | — |
| **P6** | Life spreads across the day | The last model-decided act of the day (before bedtime) is at or after min 540 (16:00) on **≥ 10 of 15** days. | last line between min 9 and 75 on 12 of 12 days |

**Two of these could pass for the wrong reason:**
- **P1 (a)** passes by construction.
- **P3** passes as long as routines move people, even if nobody's move means anything.

By CLAUDE.md:16-17, they are clues, not the goal. The hand reading after a run should still ask whether each
withdrawal, rest and meeting is what this family would do.

---

## 8. What this design does not decide

- **Exact rates.** Every number in §1 and §5 is rough, to be argued again before code.
- **Whether W5 is built.** It adds places. Without it, seeds 1–3 have no way out after night 2.
- **The clock words in the night mind's records** ("min 330"): changing them changes the night mind (§3).
- **Days 1 and 2.** The layer starts at day 3, so v16's days 1–2 stay valid as the frozen start.
- **What happens at fasting ≥ 144 or a lost person past one night.** That is the Director's question
  (days_design §5).

---

## 9. Commands and output

From `Prototypes/llm-morning/`. Every script is read only. `$S` is
`C:\Users\Akrem\AppData\Local\Temp\claude\C--Users-Akrem-Desktop-Projects-Fallow\3d4abf2b-2a12-458f-a54a-ddc81eb1a114\scratchpad`.

### 9.1 v16 seed 2, day 3: the end state

```
$ .venv/Scripts/python.exe -c "…day3 final_rooms, away, final_state, convo_log, trip, turns with model acts…"
rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []}
away []
daniel guilt 3 {'leo': 2, 'mara': 0} [None, 0]
elena guilt None {'daniel': 0, 'mara': 0} ['daniel', 3]
leo guilt None {'daniel': 3, 'mara': 0, 'elena': 0} ['daniel', 3]
mara guilt None {'daniel': 3, 'elena': 0} ['daniel', 3]
convo [{'minute': 0, 'room': 'kitchen', 'what': 'started', 'why': 'the family is together in the kitchen for the first time since last night', 'by_inner': False}, {'minute': 18, 'room': 'kitchen', 'what': 'ended', 'why': '2 full turns in a row with nothing new', 'by_inner': None}]
trip {'minute': 0, 'why': ['carried over from yesterday'], 'asked': [], 'plan': 'no plan'}
day3 turns with any model act: [0, 3, 6, 9, 12, 15]
day3 options after 15: ['silent']
```

### 9.2 Baselines, v15 and v16 days 2–3 (`$S/baseline.py`)

The script reads each transcript's day turns. For each day it prints:
- model asks, inner moments and moves;
- the last minute with words;
- all-silent turns, and stretches of ≥ 5 all-silent turns;
- runs of ≥ 3 consecutive model acts of one kind by one person (N11 without the target clause).

```
$ .venv/Scripts/python.exe "$S/baseline.py"
v15 s1 day2: asks 24, inner 0, moves 0, last line min 15, silent turns 24/30, N9 stretches [(18, 87, 24)]; N11-mech ['daniel reassure x3 from 00', 'elena reassure x3 from 00', 'mara confront x3 from 09']
v15 s1 day3: asks 38, inner 2, moves 0, last line min 36, silent turns 19/30, N9 stretches [(39, 87, 17)]; N11-mech ['elena reassure x3 from 00', 'elena reassure x3 from 15', 'leo confront x3 from 00', 'leo against x3 from 09', 'mara confront x3 from 00', 'mara volunteer x8 from 09']
v15 s2 day2: asks 24, inner 2, moves 0, last line min 15, silent turns 24/30, N9 stretches [(18, 87, 24)]; N11-mech ['elena against x3 from 06', 'mara accuse x3 from 09']
v15 s2 day3: asks 13, inner 1, moves 0, last line min 9, silent turns 26/30, N9 stretches [(12, 87, 26)]; N11-mech ['elena reassure x3 from 00', 'leo confront x3 from 00', 'mara confront x3 from 00']
v15 s3 day2: asks 70, inner 3, moves 0, last line min 75, silent turns 12/30, N9 stretches [(60, 72, 5)]; N11-mech ['daniel volunteer x6 from 42', 'elena against x3 from 42']
v15 s3 day3: asks 18, inner 1, moves 0, last line min 12, silent turns 25/30, N9 stretches [(15, 87, 25)]; N11-mech []
v16 s1 day2: asks 23, inner 1, moves 0, last line min 15, silent turns 24/30, N9 stretches [(18, 87, 24)]; N11-mech ['daniel reassure x5 from 00', 'elena reassure x3 from 00']
v16 s1 day3: asks 63, inner 1, moves 0, last line min 45, silent turns 14/30, N9 stretches [(48, 87, 14)]; N11-mech ['daniel volunteer x3 from 06', 'elena against x4 from 06', 'elena reassure x3 from 30', 'leo against x3 from 06', 'mara volunteer x7 from 06', 'mara accuse x3 from 30']
v16 s2 day2: asks 24, inner 2, moves 0, last line min 15, silent turns 24/30, N9 stretches [(18, 87, 24)]; N11-mech ['elena against x3 from 06', 'mara accuse x3 from 09']
v16 s2 day3: asks 24, inner 0, moves 0, last line min 15, silent turns 24/30, N9 stretches [(18, 87, 24)]; N11-mech ['elena reassure x3 from 00', 'leo confront x3 from 03', 'mara confront x3 from 00']
v16 s3 day2: asks 70, inner 3, moves 0, last line min 75, silent turns 12/30, N9 stretches [(60, 72, 5)]; N11-mech ['daniel volunteer x6 from 42', 'elena against x3 from 42']
v16 s3 day3: asks 25, inner 1, moves 0, last line min 18, silent turns 23/30, N9 stretches [(21, 87, 23)]; N11-mech ['elena reassure x3 from 00', 'leo confront x3 from 09', 'mara confront x3 from 00']
```

### 9.3 Bedtime choices and mind-2 feelings, v15 and v16

```
$ .venv/Scripts/python.exe -c "…night and night2 choices; mind2 feelings…"
v15 1 night1 {'daniel': 'go_next_door', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'lie_awake', 'elena': 'watch_door', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'anxious and proud', 'elena': 'anxious and exhausted', 'leo': 'tense and exhausted', 'mara': 'starving and anxious'}
v15 2 night1 {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'go_next_door', 'elena': 'sleep', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'empty and weary', 'elena': 'anxious and weary', 'leo': 'exhausted and resentful', 'mara': 'anxious and exhausted'}
v15 3 night1 {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'go_next_door', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'exhausted and resolved', 'elena': 'terrified and exhausted', 'leo': 'exhausted and wary', 'mara': 'exhausted and anxious'}
v16 1 night1 {'daniel': 'go_next_door', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'anxious and exposed', 'elena': 'anxious and exhausted', 'leo': 'exhausted and wary', 'mara': 'anxious and resentful'}
v16 2 night1 {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'go_next_door', 'elena': 'sleep', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'empty and weary', 'elena': 'anxious and weary', 'leo': 'exhausted and resentful', 'mara': 'anxious and exhausted'}
v16 3 night1 {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} | night2 {'daniel': 'go_next_door', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'}
   mind2 feelings {'daniel': 'exhausted and resolved', 'elena': 'terrified and exhausted', 'leo': 'exhausted and wary', 'mara': 'exhausted and anxious'}
```

**Counted from this output:** 2 `sleep` of 48 bedtime choices; 20 of 24 mind-2 feelings contain "exhausted" or
"weary".

```
$ .venv/Scripts/python.exe -c "…v16 seed 2 night and night2: choices, house, portions, hunger, groups; mind2 intents…"
night choices {'daniel': 'lie_awake', 'elena': 'lie_awake', 'leo': 'lie_awake', 'mara': 'lie_awake'} house 0 0 portions 1 1
  bed hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 1.0, 'mara': 0.7269999999999996}
  morning hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 1.0, 'mara': 0.8219999999999996}
  groups []
night2 choices {'daniel': 'go_next_door', 'elena': 'sleep', 'leo': 'lie_awake', 'mara': 'lie_awake'} house 0 0 portions 0 0
  bed hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 1.0, 'mara': 1.0}
  morning hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 1.0, 'mara': 1.0}
  groups [{'leader': 'daniel', 'members': ['daniel'], 'street': 'clean', 'outcome': 'back with nothing', 'u': 0.2798719507999635}]
mind2 intents {'daniel': 'I will face whatever they say to me in the morning and try to keep us all alive.', 'elena': 'I will make sure nobody leaves the house and we stay together safely.', 'leo': 'I will find out if Daniel came back through that door and what he brought us.', 'mara': 'I will ask Daniel why he went out into the street with nothing to show for it.'}
mind2 feelings {'daniel': 'empty and weary', 'elena': 'anxious and weary', 'leo': 'exhausted and resentful', 'mara': 'anxious and exhausted'}
day2 trip plan Daniel will go; Mara wants Daniel to go; Leo wants Daniel to go; Elena is against anyone going
```

### 9.4 Need words in the v15 and v16 stories, and tired feelings in v16's day acts

```
$ grep -hoiE '\b(tired|exhausted|exhaustion|weary|sleep|asleep|water|thirsty|thirst|drink|weak|weakness|cold|dizzy|faint)\b' runs/v1[56]/daniel_ate_it-seed?.md | tr A-Z a-z | sort | uniq -c | sort -rn
    111 exhausted
     28 asleep
     25 sleep
     18 tired
     16 cold
     15 weary
      7 water
$ grep -noiE '\bwater\b' runs/v1[56]/daniel_ate_it-seed?.md
runs/v15/daniel_ate_it-seed1.md:48:water
runs/v15/daniel_ate_it-seed1.md:439:water
runs/v15/daniel_ate_it-seed2.md:48:water
runs/v15/daniel_ate_it-seed3.md:48:water
runs/v16/daniel_ate_it-seed1.md:48:water
runs/v16/daniel_ate_it-seed2.md:48:water
runs/v16/daniel_ate_it-seed3.md:48:water
$ grep -n -iE '\bwater\b' runs/v1[56]/daniel_ate_it-seed?.md | grep -v ":48:" | cut -c1-400
runs/v15/daniel_ate_it-seed1.md:439:- **Leo** (1st to act in the kitchen: just spoken to by Mara). Social moment: Mara confronts you: "Leo, you ate right in front of me when I was starving, so you have no right to lecture anyone.". **Chose: stay put and say nothing** (one of 25 options). Feeling: *exhausted*. Reason: “There is nothing left to argue about when we have no food and no water.” Sus
$ grep -ciE "\| (exhausted|weary|tired)[^|]*\|" runs/v16/scoring/s?_acts?.txt
runs/v16/scoring/s1_acts2.txt:3
runs/v16/scoring/s1_acts3.txt:10
runs/v16/scoring/s2_acts2.txt:1
runs/v16/scoring/s2_acts3.txt:3
runs/v16/scoring/s3_acts2.txt:3
runs/v16/scoring/s3_acts3.txt:6
```

**How to read the water lines.**
- **6 of the 7 "water" matches** are line 48 of each story: the day-1 backstory row.
- **The 7th** is v15 seed 1, line 439. It sits under "## The morning" of "# The next morning (day 5)" (line 324),
  after the "min 06" header, so it is day 2, min 06: Leo's reason, quoted in §1.3.
- **"Cold"** matches are feelings ("You felt cold", "cold anger"), not the body.
- **The tired-feeling acts** total 3 + 10 + 1 + 3 + 3 + 6 = **26**.

### 9.5 v16 seed 2: food acts and the day-2 end state

```
$ .venv/Scripts/python.exe -c "…food acts by day; day2 final grudges; day2 last line; day2 trip acts…"
day1 food acts [(54, 'mara', 'eat')]
day2 food acts [(0, 'daniel', 'give_elena'), (0, 'elena', 'eat_given')]
day3 food acts []
day2 end daniel {'leo': 0, 'mara': 0}
day2 end elena {'daniel': 0, 'mara': 0}
day2 end leo {'daniel': 3, 'mara': 0, 'elena': 0}
day2 end mara {'daniel': 3, 'elena': 0}
day2 last line 15
day2 trip acts [(3, 'daniel', 'volunteer'), (6, 'mara', 'send_daniel'), (6, 'elena', 'nobody_goes'), (6, 'leo', 'send_daniel'), (9, 'daniel', 'still_going'), (9, 'elena', 'keep_daniel_home'), (12, 'elena', 'nobody_goes')]
```

### 9.6 The code lines cited

```
$ grep -n "p.hunger = min(1.0\|QUIET_TURNS = \|LULL_QUIET = \|def routine\|def decide(self\|def start_trip\|if triggers or d.get\|self.turns = \|kind in SPEECH and n >= 3" world.py
79:QUIET_TURNS = 2              # full turns with nothing new that end a conversation
82:LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
378:        self.turns = data.MINUTES // data.MINUTES_PER_TURN
542:        if kind in SPEECH and n >= 3:
616:    def start_trip(self, minute):
726:    def routine(self, p, opts):
1278:            p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
1329:    def decide(self, p, t):
1354:        if triggers or d.get("inner_kinds") or "trip_moment" in d or "lull" in d:
$ grep -n "GAP_HUNGER\|NIGHT_HUNGER\|^HOUSE = \|^ALONE\|^GROUP\|^BEDTIME\|def trip(self\|PROMISE\b\|out.append(data.GAP)" night.py
29:GAP_HUNGER = 0.3            # × hunger_rate, the afternoon and evening (§2)
30:NIGHT_HUNGER = 0.1          # × hunger_rate, the night
33:HOUSE = [(0.30, 0), (0.65, 2), (0.90, 4), (1.00, 6)]                       # §4.1
34:ALONE = [(0.62, "clean"), (0.76, "scare_there"), (0.94, "scare_back"), (1.00, "not_back")]   # §4.2
35:GROUP = [(0.70, "clean"), (0.82, "scare_there"), (0.97, "scare_back"), (1.00, "not_back")]
46:BEDTIME = [("sleep", "go to sleep"),
56:PROMISE = "You said you would go to the neighbour's house tonight. If you are going, it is now."
228:            p.hunger = min(1.0, p.hunger + GAP_HUNGER * p.sheet["hunger_rate"])
253:                now.append(PROMISE)
275:            p.hunger = min(1.0, p.hunger + NIGHT_HUNGER * p.sheet["hunger_rate"])
500:    def trip(self, L, group):
653:    out.append(data.GAP)
737:    out.append(data.GAP)                                                          # Y8
$ grep -n "MINUTES = \|MINUTES_PER_TURN\|^GAP\|^PORTIONS" data.py
75:PORTIONS = 2
76:MINUTES = 90
77:MINUTES_PER_TURN = 3
102:GAP = "The afternoon and evening passed in the house. Nobody ate."
```

### 9.7 The North Star search

```
$ grep -rli "north star\|northstar\|north-star" --include=*.md . | grep -v "/Library/\|node_modules"
./CLAUDE.md
./Prototypes/llm-morning/reports/check_errors.md
./Prototypes/llm-morning/reports/c_patterns.md
./Prototypes/llm-morning/reports/days_design.md
./Prototypes/llm-morning/reports/days_impl.md
```
The only document holding the principles is `CLAUDE.md` (lines 21–28). The reports only quote it.
