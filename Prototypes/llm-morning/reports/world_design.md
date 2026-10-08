# Design: FALLOW's world system

Mode: design. No code was written, the API was not called, and no cache, run or frozen version was changed. Paths
are relative to `Prototypes/llm-morning/`.

- **Read first:** `CLAUDE.md` (North Star principles, `CLAUDE.md:21-28`); `reports/days_v21.md`;
  `reports/probe_stakes.md`; `reports/quiet_day_design.md` §1 and §5; the code that runs a day (`world.py`,
  `quiet.py`), a night and a trip (`night.py`), and the run itself (`morning.py`).
- **How numbers are marked:** `[S12]` is a source in §10. `(est.)` is an estimate: a number with no source,
  chosen by reasoning, to be changed when a source or a run says otherwise. A number taken from the code cites
  `path:line`. A source that was looked for and not found is written **NOT FOUND**.
- **Baselines** for the predictions were counted from `runs/v21` by a read-only script; it and its output are in
  §11.

## Summary

| Part | The design in one line |
|---|---|
| Angles | Three architectures were drafted: every person an agent (A), a ledger of rates (B), households as actors behind one perception boundary (C). **C is chosen** (§0.2). |
| 1. World state | One `World` holds the truth: places with contents, households with people, weather, water, rumours, deeds. Every person and household has their own `Knowledge`: facts with a source and a time. Prompts read only Knowledge and percepts, never World. |
| 2. The clock | Bodies, water and weather are closed-form in time, so the world jumps from event to event (as `quiet.py` already does). Off-screen households plan once per day part (6 hours). An event near the family is resolved to the minute. Every draw has its own seed string. |
| 3. The boundary | One perception function, used both ways: an event emits a stimulus (sound in dB, light, contact); walls, distance, rain and sleep decide who perceives what, and code writes the percept in words. The house acts on the world through trips, the yard and the door, and it emits stimuli of its own. |
| 4. Domains | Weather from a Markov-chain generator fed by real climate normals; water as containers, use levels and rain catchment; honest bodies: fasting stages in days that match fasting studies, thirst as a water deficit in % body mass, cold from indoor temperature; sickness, injury, households, word spreading, rumours, each with sourced or marked numbers. |
| 5. AI | The AI gives words and choices to the family (as now) and, from W3, to a visitor at the door. Off-screen people never ask the AI. W1 adds at most 8 asks on a rain day. |
| 6. Build plan | W1 physical layer; W2 the street and its people, heard and seen only; W3 the door; W4 word spreads; W5 sickness and injury; W6 rumours; W7 joining. Each answers named evidence and has its own live test. |
| 7. A real family | Fill everything, flush with the bath, stop flushing, ration by the cup, put every container under the drainpipe when it rains. Not to build: per-sip AI choices, hydraulics, a thirst number in prompts, a drama director. |
| 8. W1 predictions | Ten, each with a counting rule a script can apply. W1-1: **at least 3 outward acts on days 3–10 (v21: 1).** |

---

## 0. The evidence, and the three angles

### 0.1 What the runs show and what the code does

**The house never moved itself** (`reports/days_v21.md`):
- **No trip on nights 3–9:** 0 trips, 1 attempt. On night 5 Daniel got up, Leo told him not to go, and he answered
  "I am too weak anyway" (`reports/days_v21.md:114-119`).
- **Bedtime choices on nights 3–9:** 28 in all, of which 17 `lie_awake`, 7 `sleep`, 3 `watch_door`, 1
  `go_next_door` and 0 `go_further` (`reports/days_v21.md:165-166`).
- **After day 5, no trip talk:** "After night 5 nobody offered, objected, or asked to go, on any of the 5 days left"
  (`reports/days_v21.md:169-170`).
- **The talk loops:** 0 of 7 days had half the morning in new pairs (`reports/days_v21.md:15`). Mara: "53 of her 71 lines
  name the can, the taking, the stealing or the lying" (`reports/days_v21.md:244`).

**Stating the stakes changed nothing** (`reports/probe_stakes.md`):
- **The line added:** "You know your body: without food, you will not last many more days."
- **What it did:** 0 of 20 answers went out, against 0 of 20 in the control (`reports/probe_stakes.md:14`). The
  reasons name weakness: "too weak", 15 of 20 in the probe (`reports/probe_stakes.md:24-26`).

**The third body stage forbids walking:**
- **The words:** fasting ≥ 144 reads "so weak you can barely stand: walking any distance feels impossible"
  (`quiet.py:52-55`, threshold `quiet.py:26`).
- **What the model did with them:** 16 of the 28 bedtime reasons on nights 3–9 say they cannot stand, walk or go
  (§11, B1), for example "My body is too weak to stand or walk anywhere safely" (`reports/days_v21.md:146`).

**Is the third stage true?** It is not:
- **In the run:** Daniel's fasting at 21:00 on day 10 is 269.1 (`reports/days_v21.md:79`), which is 234 real hours
  at his rate of 1.15 (`data.py:26`): under 10 days without food, with water.
- **Fasting cohort:** 1,422 people fasting 4 to 21 days on 200–250 kcal a day took "light to moderate intensity
  outdoor walks" [S6].
- **Survival physiology:** "Fit and healthy individuals appear to be able to maintain normal work capacity during
  short periods (<10 days) on severely restricted diets", and decrements begin at a 10% loss of body weight [S1].
- **Behaviour:** the lethargy of starvation does "not prevent intelligent and purposeful behaviour when the
  opportunity arises to procure food" [S1].

**Water is not tracked at all:**
- **What the prompt says:** "The water has stopped" (`data.py:130`); the backstory has Leo saying to fill everything
  (`data.py:212`) and the taps running dry (`data.py:214`).
- **What the code holds:** no number for water. **NOT FOUND:** `grep -n "water\|rain\|thirst\|cold\|weather" *.py`
  (tests excluded) finds only `data.py:130` and `data.py:212` (§11).
- **Why it was cut:** `reports/quiet_day_design.md:145-151` cut thirst because "it first needs a stored-water fact
  the code has never fixed". With no number, a family alive on day 10 on unmeasured water is the code's untruth,
  not the model's.

**What the world is today:**
- **The neighbour's house:** one draw per seed (`night.py:34`, `night.py:362-364`), 0 portions in seeds 1–3
  (`reports/quiet_day_design.md:52`).
- **The houses further along:** one draw each, when first entered (`night.py:71`, `night.py:746-754`).
- **The street:** a four-outcome table (`night.py:78-79`) whose danger is "something was moving" (`night.py:794`).
- **Nothing outside acts by itself:** nothing happens unless a family member goes out.

**The conclusion that shapes everything below:** a starving house that is told its stakes still lies down. What a
real family moves for is a situation in front of it: rain on the roof with empty pots, a bath at a third, a sound
next door, a knock. The world must put situations in front of the house, from its own state.

### 0.2 Three architecture angles

Each angle was drafted to answer the same eight questions; they are compared here on what the brief requires.

**A. Every person an agent.** Every off-screen person is simulated individually on a 15-minute tick, with their own
needs, plans, movement and perception, as the family is.
- *For:* the most depth. Any story can emerge from below.
- *Against, first as a real-world check:* nobody in the family perceives what the man four doors down did at 14:15
  unless it reaches them. Simulating it at that grain buys detail nobody can know.
- *Against, cost:* about 60 people × 96 ticks a day of plans. Each plan is a person-level rule with numbers no
  source gives (how often a lone man checks his back door). Tuning cannot be checked against anything.
- *Against, tests:* a run's outcome depends on thousands of interacting draws, so a failed prediction is hard to
  trace.

**B. A ledger of rates.** The street is a table of stocks (food, water, fear by household) and the events that reach
the house are Poisson draws whose rates are functions of those stocks: "knocks per day = f(share of households out
of water)".
- *For:* cheapest, and every rate is easy to source or mark.
- *Against:* the brief says what reaches the family must be "a consequence of their story". A knock drawn from a rate
  has no one behind it: the same family cannot come back, cannot have heard about the family from someone, cannot
  remember being refused.
- *Against, the brief:* word spreading needs carriers, and a ledger has none.
- *Against, the drama rule:* a rate that rises with the street's misery is close to a director with a dial.

**C. Households as actors behind one perception boundary (chosen).** The household is the unit that plans; each
person in it carries a body.
- **Planning:** households plan coarsely (once per 6-hour day part), and bodies, water and weather are closed-form
  in time.
- **Resolution:** an action near the family, in perception range, is resolved to the minute.
- **The boundary:** one perception function turns events into percepts. It serves the family and the off-screen
  households alike, so the house is seen and heard by others with the same rules.

*Arguing against C first:*
- **Households hide their own quarrels off-screen.** True. Nobody perceives them, and when a household is at the
  door each of its people gets a mind (§5).
- **A 6-hour plan is coarse for a night movement.** Inside perception range the movement is resolved to the minute,
  so the family hears the footsteps at 02:14, not "at night".
- **Does a household decide as one?** Real families mostly move and forage together, and the family itself is shown
  doing so (`night.py:507-618` joins and stops). Off-screen, that is the right unit.

**Why C:**

| Requirement (the brief) | A | B | C |
|---|---|---|---|
| Off-screen households with their own food, water, fear and plans | yes | stocks only, no plans | yes |
| What reaches the family is a consequence of their story | yes | no (rates) | yes |
| Word spreads through carriers | yes | no | yes (households meet) |
| No drama director | yes | at risk (rates of misery) | yes |
| Cheap and testable | no | yes | yes (≈ 30 households × 4 plans a day; seeded per string) |
| General and data-driven | yes | yes | yes |

---

## 1. World state

### 1.1 What exists (truth, held only by `World`)

| Kind | Fields | Data file | Notes |
|---|---|---|---|
| **Town** | climate table, start date, latitude (moon) | `world/town.json` | A temperate town in early autumn (§4.1). |
| **Place** | id, kind (house, flat, shop, yard, street segment), position on the street (m), side, neighbours (shared walls), openings (doors, windows, boarded or not), viewpoints (what each window and gap sees), contents (food portions, water by container, items), occupants (household id or none), state (intact, forced, searched, burnt) | `world/street.json` | The family's house is one place among them. |
| **Container** | id, place, capacity L, litres, source (tap, rain, bin), covered, movable | in `street.json` | Water only. A pot, the bath, a bin. |
| **Catchment** | place, litres per mm of rain, where it drains (a downpipe into the yard) | in `street.json` | One number per drainpipe (§4.2). |
| **Household** | id, home place, members, stores (food, water by container), plan, disposition, fear, knowledge, deeds done | generated at world creation from `world/population.json` | Off-screen until perceived. |
| **Person** | id, household, age, sex, body mass, body state (fasting, water deficit, sleep debt, cold, sickness, injury), traits | as above; the family's from `data.py:17-56` | Same body code for everyone. |
| **Weather** | for each day: wet or dry, rain spells (start, end, mm), hourly outdoor temperature; indoor temperature per house | generated from the town's climate (§4.1) | Truth; perceived as sound, light, cold. |
| **Rumour** | id, claim (structured), true or false, origin, carriers, distortion per carrier | generated from `world/rumours.json` | Hope only: a radio voice, a far light (§4.7). |
| **Deed** | who, to whom, what (gave, refused, threatened, traded, took), where, when, witnesses | written by code when it happens | The raw material of word spreading (§4.6). |

### 1.2 What each person perceives (Knowledge)

- **A fact:** `{subject, predicate, value, source, at, sure}`. The source is one of `saw`, `heard`, `did`, `told by X`
  or `concluded`.
- **The family's knowledge** already exists in this form, spread over the people's `sure` lines, night lines and
  "About ..." lines (`night.py:146-155`, `night.py:1036-1064`). The world design names the form and makes every
  new domain use it.
- **Household knowledge:** for each place, believed contents and when last seen; for each other household, believed
  size, stores, danger and deeds heard of.

**The rule that keeps truth apart:**
- **Prompts never read World.** The prompt builders (`world.py:1041`, `night.py:401-404`) receive only a person's
  Knowledge and their percepts.
- **A test enforces it.** The prompt code is handed no reference to World. A unit test builds every prompt of a fake
  run with a World whose truth differs from every person's Knowledge, and checks that no prompt contains a
  truth-only value.

**Who knows what about whom:**
- **Off-screen households** know the family only through percepts (a light at night, voices through a party wall, a
  figure at the back door) and through deeds told to them (§4.6).
- **The family** knows households only through percepts and what is said at the door.

---

## 2. The world clock

### 2.1 Steps

| Layer | Step | Why this step |
|---|---|---|
| Weather | generated for a whole day at 00:00 (wet or dry, then spells, then hourly temperature) | A daily weather generator is the standard form [S8]. |
| Bodies and water | continuous, closed-form between events | As `quiet.py:187-201` already computes fasting and debt from the clock. A threshold's time is solved, not ticked (`quiet.py:559-578`). |
| Households (off-screen) | one plan per day part: 00–06, 06–12, 12–18, 18–24 (est.) | Real households decide a few times a day (go out this morning, stay in tonight). |
| Actions in perception range | resolved to the minute on the 3-minute grid (`data.py:78`) | The family's turns are 3 minutes, and a footstep must land on one. |

### 2.2 Rules of advancement

- **Lazy advancement:** `World.advance_to(t)` runs every pending world event before `t`. The family's loop calls it
  wherever it jumps: each played turn, each quiet jump, each night stage.
- **Events in range wake the house:** `quiet.next_event` (`quiet.py:559`) adds the next world event that will be
  perceptible in the house, so a quiet stretch jumps to it. An event that nobody perceives is still applied to
  World; it changes truth, not anyone's knowledge.
- **The order within a day part:** weather, then bodies and water (consumption), then plans, then actions by start
  time, then meetings between households at the same place and time.
- **No storyteller:** no rule reads the family's state to choose a world event. Off-screen plans read only their own
  household's Knowledge and needs.

### 2.3 Seeded randomness

- **One string per draw,** as the code already does (`night.py:359-369`): `f"{seed}:{layer}:{id}:{day}:{part}:{purpose}"`.
  For example `"2:weather:day5:wet"` and `"2:hh07:day5:p2:plan"`.
- **Why:** a draw does not depend on how many draws came before it. Adding a household, or a person changing a
  choice, leaves every other draw unchanged.
- **Facts are fixed once:** a fact the world had not decided is fixed the first time a rule needs it, and never drawn
  again (`chronicle.py:1-3`). The neighbour's house food is the model (`night.py:362`).

### 2.4 Why it stays cheap

- **Size:** about 30 houses and 15–25 households (§4.5), 4 plans a day each: about 100 plan evaluations a day, each a
  handful of arithmetic.
- **Cost:** no AI call off-screen (§5).
- **What is never computed:** an off-screen person's minute-by-minute day.

---

## 3. The boundary

### 3.1 World → house: stimuli become percepts

**Every world event that can be noticed emits a stimulus:**
- **The fields:** `{t, place, sense, level, kind, actor (truth only)}`.
- **Sound:** `level` is dB at 1 m from the source (est. per kind, §4.5).
- **Light:** `level` is the light at the source and its direction.
- **Contact:** a knock, a voice at the door.

**Sound reaches a listener by code:**
- **The formula:** `L = L_source − 20·log10(d) − walls − masking`.
- **Distance:** a point source loses 6 dB per doubling of distance [S14]; `d` is in metres, from place positions.
- **Walls:**
  - a closed window: median outdoor–indoor difference 27.8 dB(A) [S14];
  - a boarded front window: 25 dB (est.);
  - a masonry party wall: 45 dB (est.);
  - the bathroom: no sound in or out (`data.py:72-74`).
- **Masking and thresholds:**
  - a quiet rural night is about 30 dB(A) [S14]; a town with no traffic and no power: 30 dB(A) (est.);
  - moderate rain is about 50 dB(A) [S14];
  - heard if `L` is at least the ambient level (est.), and heard clearly (words, a voice's sex) at ambient + 10 dB
    (est.).
- **Asleep:** the chance of waking rises with the margin over ambient and with the anxious trait. This extends the
  existing draws (`night.py:289-296`); the slope is est.

**Sight reaches a viewer by code:**
- **Where they can see from:** only from a viewpoint (the gaps in the boarded front windows, the yard).
- **Night light:** full moon about 0.1–0.25 lux, a clear moonless night about 0.001 lux [S16]. At night, figures
  are seen only by moonlight or by a light they carry.
- **What can be seen:** in daylight a figure is seen to 100 m (est.), at full moon to 20 m (est.), with no moon only
  within a few metres or with their own light.

**The percept is written by code in perception words, never truth:**
- *Truth:* household 7's two adults force the back door of no. 14 at 02:14.
- *Leo, awake:* "In the night you heard wood splintering, a few houses along the street, to the left. Then nothing."
- **What it holds:** sense, direction, rough distance ("next door", "a few houses along", "far off"), and what can be
  told at that level.
- **Where it goes:** the person's lines and the chronicle, as an event with witnesses `heard` or `saw` (the
  existing witness kinds, `data.py:206`, `night.py:720`).

**Contact is a scene:**
- A knock at the front door is a loud sound in the house (est. 70 dB at the door).
- Whoever answers starts a door scene (W3, §6).

### 3.2 House → world: acts and emissions

**Acts that cross the walls:**

| Act | Exists? | What it does to World |
|---|---|---|
| Night trip next door or further along | yes (`night.py:507-618`, `night.py:726-858`) | From W2, the trip reaches a real place with real contents and real occupants or none; the street table is replaced by the people actually out there. |
| Collect rain in the yard | W1 | Containers go out under the drainpipe; they fill by code (§4.2). The person is outside, wet, and can be seen from overlooking windows (W2 on). |
| The door: answer, refuse, talk, give, trade | W3 | A deed (§1.1) and an exchange of goods. |

**Emissions** (stimuli the house gives off, perceived by households with the same function as §3.1):
- **Sound:** voices in a quarrel (est. 75 dB when shouting) through the party walls and boards.
- **Light:** a candle seen through gaps at night (est.: visible from the street to 30 m).
- **Movement:** someone in the yard seen from the upper windows behind.
- **Smoke:** if they ever burn anything.

---

## 4. The domains

### 4.1 Weather

**The generator** is a Richardson-type weather generator [S8]:
- **Wet or dry:** a first-order Markov chain on wet and dry days, defined by `P(W|D)` and `P(W|W)`.
- **Rain amounts:** an exponential amount on a wet day.
- **Temperature:** conditioned on wet or dry.

**The climate data** (the default "temperate town"): Met Office Kew Gardens 1991–2020 normals [S7].

| Month | Mean max °C | Mean min °C | Rain mm | Days ≥ 1 mm |
|---|---|---|---|---|
| September | 20.3 | 10.5 | 51.9 | 8.4 |
| October | 16.0 | 7.8 | 67.9 | 10.9 |

**The parameters for played day 1, about 1 October, with a linear drift through the month:**
- **Wet-day chance:** `p = (8.4/30 + 10.9/31) / 2 = 0.32` [S7, arithmetic].
- **Persistence:** `P(W|W) = 0.5` (est.: the persistence of temperate wet spells; no station value was found, so
  this is **NOT FOUND** for Kew). Then `P(W|D) = p(1 − P(W|W))/(1 − p) = 0.23`.
- **Mean dry spell:** 1/0.23 ≈ 4.3 days. "Rain every few days", as the brief says.
- **Mean amount on a wet day:** 51.9/8.4 = 6.2 mm and 67.9/10.9 = 6.2 mm [S7, arithmetic], so 6.2 mm, exponential
  [S8].
- **Spells:** a wet day has 1 spell, or 2 with chance 0.3 (est.). Each lasts 2–6 hours, uniform (est.), and starts
  at a uniform hour (est.). Intensity is the amount over the duration.
- **Temperature:**
  - mean max 18.2 °C and mean min 9.2 °C on 1 October, drifting by −0.14 °C a day [S7, interpolated];
  - daily noise ±2 °C, normal (est.);
  - a wet day's max −2 °C and min +1 °C (est.: the generator's wet/dry conditioning [S8], magnitude est.);
  - hourly shape: a sine with the min at 06:00 and the max at 15:00 (est.).
- **Indoors** (no power, no heating): the outdoor daily mean + 4 °C (est.), so about 17–18 °C in the first days,
  falling with the season.

**The data form:**
```json
{"climate": {"months": {"9": {"max": 20.3, "min": 10.5, "mm": 51.9, "wet_days": 8.4},
                        "10": {"max": 16.0, "min": 7.8, "mm": 67.9, "wet_days": 10.9}},
             "p_ww": 0.5, "second_spell": 0.3, "spell_hours": [2, 6], "wet_max": -2, "wet_min": 1,
             "indoor_over_mean": 4},
 "start_date": "10-01"}
```

**How weather reaches the house:**
- **Rain is heard:** rain on a roof and on boards is heard by everyone awake indoors. Each spell's start is a
  stimulus at about 50 dB [S14]. The percept: "Rain has started: you hear it on the roof and against the boards."
- **Rain masks:** while it rains, ambient is 50 dB instead of 30, so the front door, footsteps and voices in the
  street are 20 dB harder to hear (§3.1, [S14]).
- **Cold is felt,** not read (§4.3).
- **Light:** daylight through gaps. Grey or bright is not modelled (§7).

### 4.2 Water

**What a real family of four stored, fixed by code as the open fact `reports/quiet_day_design.md:149-151` asked for:**

| Container (house data) | Litres | Basis |
|---|---|---|
| The bath, filled to near the overflow on house day 1 | 150 | A bath holds about 182–213 L to the overflow and a typical run is about 80–100 L [S12]; 150 (est.). |
| Two large pans | 2 × 8 | (est.) |
| The kettle | 1.5 | (est.) |
| Bottles, 6 × 1.5 L | 9 | (est.) |
| Two buckets | 2 × 10 | (est.) |
| **Total on house day 1** | **196.5** | |
| The toilet cistern | 6 | Modern flush ≤ 6 L [S13]; drinkable if clean and untreated [S10]. Kept as a source the family may not think of. |
| A hot-water cylinder | 0 in this house (a combi boiler, est.) | FEMA lists the water heater tank as an emergency source [S10]; a data field per house, so another house can hold one. |

**Use, as household levels** (the code applies one; the family's own acts change it, §4.2.3):

| Level | Drinking, per person a day | Washing, per person a day | Toilet | House of 4, a day |
|---|---|---|---|---|
| `as_before` | 2.0 L (est.) | 1.0 L (est.) | bucket flush 2 × 6 L [S13], from the bath | about 24 L |
| `careful` | 2.0 L | 0.5 L (est.) | not with stored water | about 10 L |
| `rationed` | 1.25 L: five 250 mL cups (est.) | none | not with stored water | about 5 L |

**Is 2.0 L of drinking right?**
- **Survival intake:** 2.5–3 L a day, drinking and food together [S2].
- **No food, no food water:** with no food, the 20–30% of water that comes from food is gone [S1], so they drink
  more than in normal life.
- **The floor:** at rest in a survival situation the total need is about 1.5 L a day, and about 1 L of it must be
  drunk [S1].
- **So 2.0 L** is comfortable drinking, and `rationed` at 1.25 L sits just above the floor (est.).

**The stored water at the start of each played day, by code (est. dates and rates):**
- **Before day 1:** the taps ran dry on house day 2 (`data.py:214`) at about 12:00 (est.). From then to played day 1
  at 07:00 (house day 4, `world.py:378`) is 43 hours at `as_before`: about 43 L. So **about 150 L** at played day 1,
  07:00.
- **Days 1 and 2:** played from the cache with no water in any prompt, at `as_before`: 48 hours, about 48 L. So
  **about 100 L** at day 3, 07:00.
- **From day 3:** the prompts carry the water line. At `as_before` it is gone by about day 7; at `careful` about day
  13; at `rationed` about day 23 (arithmetic).

**4.2.1 Rain catchment:**
- **The rule:** 1 mm of rain on 1 m² of horizontal roof gives 1 L [S9]. Roofs lose 5–20%: a runoff coefficient of
  0.9 for asphalt and 0.8–0.9 for tile [S9]; 0.85 here (est.).
- **The family's roof:** a terraced house of about 50 m² roof area (est.), half of it draining to the back drainpipe:
  25 × 0.85 = **about 21 L per mm** at that pipe.
- **A wet day:** 6.2 mm [S7] gives about 130 L at the pipe, if something is there to catch it.
- **The limit is the containers, not the rain.** A 10 L bucket under the pipe is full after half a millimetre. A
  wheelie bin holds 240 L (est.: the common size; standard NOT FOUND). A pan set on open ground catches only its
  mouth: a 30 cm pan catches about 0.07 L per mm.
- **Data:** each catchment is `{"place": "yard", "l_per_mm": 21, "pipe": "back"}`, and each container under it fills
  to its capacity. The rest overflows and is lost.

**4.2.2 Quality, recorded and not yet acted on in W1:**
- **Rain water carries germs:** E. coli was found in just over half of 53 roof-rainwater tanks in Adelaide and in 63%
  of tanks in southeast Queensland [S11].
- **Official guidance:** collected rain water is for hygiene and cleaning unless treated, and emergency water should
  be treated before drinking (boiling, filtering, bleach) [S10].
- **In W1:** each container keeps its source (`tap`, `rain`, `bin`). Sickness from it is W5 (§6).
- **Use order (code):** washing and flushing come from rain water first while there is any; drinking comes from tap
  water first.
- **When the tap water is gone,** they drink rain water. Almost everyone thirsty does, so the code does it; this is
  not a model choice (§7).

**4.2.3 The acts W1 adds:**
- **`save_water`** (speech: "say nobody uses the drinking water for washing or the toilet any more"): the level
  becomes `careful` when said.
- **`ration_water`** (speech: "say the water must be shared out by the cup from now on"): the level becomes
  `rationed`, and the speaker holds the water.
- **`collect_rain`** (an act, while it is raining, for someone in the kitchen): "go out the back door to the yard and
  set the empty buckets and the bin under the drainpipe". 3 minutes; they come back wet.
- **At bedtime while raining:** one more bedtime option, "put the empty buckets out under the drainpipe in the yard,
  then go to bed".
- **Bringing them in:** done by code, by whoever set them out, at the first turn after the spell ends while they are
  awake.
- **What the family knows:** an "About water:" line, written from what each of them saw. "About water: the bath is
  about two-thirds full (about 100 litres); there are 15 litres in the pans and bottles; since yesterday nobody
  flushes with it." It is rounded to what an eye sees (est.: nearest tenth of the bath and nearest 5 L) and updated
  when they are in the room.

**Arguing against `ration_water` first:** would a real family ration, or just drink less? Both. Rationing with a
holder is what happens once a family sees the end of the water (the siege of Sarajevo is full of households counting
canisters [S27]). Code applies only what a person said; the model chooses whether anyone says it.

### 4.3 The body

**One body model for every person on the street.** Each need is a number counted by code. At a threshold the body
line changes: a situation, never an act (`CLAUDE.md:26-27`).

#### 4.3.1 Fasting: honest stages, in days

- **The number:** `fast` as now, hours since the last meal × hunger rate (`quiet.py:187-188`).
- **What changes:** the thresholds and the words. The current ones are 48, 96 and 144 (`quiet.py:25-26`).

| Stage | From (fast) | Real basis | The body line (a situation) |
|---|---|---|---|
| F1 | 24 | Liver glycogen can be gone within 24 hours [S1]. | "Your body: starving; hunger comes in waves." |
| F2 | 72 | The body has switched to fat [S1]. Fatigue (13.7%), headache (5.4%) and vertigo (2.5%) are reported in a fasting cohort [S6]. | "…: starving for days; you feel light and slow, and standing up fast greys your sight for a moment." |
| F3 | 168 (7 days) | Normal work capacity is kept for under 10 days [S1]. People fasting 4–21 days walk outdoors [S6]. | "…: thin and weak; stairs and carrying things tire you fast, and you feel the cold." |
| F4 | 336 (14 days) | Decrements begin at a 10% loss of body weight [S1]. About 0.5 kg a day is lost in total starvation [S1]; 8.6 kg is lost in 20 days on 200–250 kcal [S6]. | "…: your strength is going; your heart races when you stand, and a short walk leaves you shaking." |
| F5 | 672 (28 days) | Muscle loss is severe (est. stage; no source gives this threshold). | "…: you are wasted; getting up takes everything you have." |
| Death | a hazard from 960 (40 days) | Death in complete starvation usually comes within 40–60 days [S1]. Ten of 23 Irish hunger strikers died in 1981, Bobby Sands after 66 days [S28]. | — |

- **The death draw:** each person's death point is drawn once, uniform in [40, 60] days of fast (est., the range of
  [S1]). Lean and young people come earlier [S1]: −5 days for Mara, aged 17 (est.).
- **What the change does on the run's days:** Daniel reaches F3 on day 7 (his fast is 186.3 at 21:00 on day 7,
  `reports/days_v21.md:77`) and nobody reaches F4 by day 10. The third stage now says what stairs and carrying cost,
  not that walking is impossible.
- **What follows in the code:**
  - `FAST_STAGE_WORD` (`world.py:114`) and `NEED_VIEWS` (`quiet.py:57-63`) follow the new table;
  - the street shifts `weak`, `very weak` and `barely standing` (`night.py:80-82`) move to F2, F3 and F4, so walking
    weakness keeps its cost in the street;
  - a rest falls due at `VERY_WEAK` (`quiet.py:576`); it moves to F3, so the day's rests keep their timing.

**Arguing against F3's words first:** "stairs and carrying things tire you fast" names stairs and carrying. Does a
named act make the model do it (`CLAUDE.md:26`)? It names a cost, not an act to take. The words that froze the house
were a ban ("feels impossible"); the probe showed the model reads a body line as permission to stay down
(`reports/probe_stakes.md:24-26`). W1-2 and W1-9 test this (§8).

#### 4.3.2 Thirst: a water deficit in % of body mass

**The number:** each person's deficit `D` in litres:
- it rises by their net loss;
- it falls by what they drink, never below 0;
- the stage reads `D / body mass` as a share.

**Net loss at rest in the house:**
- **The physiology:** at rest the need is about 1.5 L a day, metabolic water gives about 0.5 L, and about 1 L a day
  must be drunk [S1]. Skin loses about 450–500 mL a day [S1, S4], and the kidneys at least about 500 mL a day [S1,
  S4].
- **The value used:** **1.2 L a day** at rest, cool house (est., inside [S1]'s 1.0–1.5).
- **Extra losses:**
  - a night trip: +0.3 L (est.);
  - a wet day out in the yard: none (est.);
  - diarrhoea (W5): +0.5 to +2 L a day (est.).

**Body masses (est.):** Daniel 78 kg, Leo 70 kg, Elena 65 kg, Mara 55 kg. The share is taken on the mass at day 1.
The fall in mass while fasting is not modelled in W1 (§7).

| Stage | Deficit, % of body mass | Real basis | The body line |
|---|---|---|---|
| T1 | ≥ 2 | Performance begins to fall at about 2% [S4, S5]. | "…; you are thirsty, and your mouth is dry." |
| T2 | ≥ 5 | Over about 5%: headache, irritability, light-headedness [S1]. | "…; you are badly thirsty: your head aches, and you are light-headed when you stand." |
| T3 | ≥ 8 | At 8–10%: weakness, dizziness, faintness, a fast weak pulse, pins and needles [S1]. | "…; you are parched: your lips are cracked, your heart races, and you feel faint." |
| T4 | ≥ 10 | Delirium and hallucinations come as the body fluids concentrate [S1]. | "…; at times your thoughts drift and you lose track of where you are." |
| Death | each person's own point, drawn once in [10, 12]% (est.) | Death usually comes with acute losses of 15–20% of body water [S1]. Body water is about 60% of body mass in a man (est.: textbook value, not sourced here), so 9–12% of body mass. | — |

**The check against survival times.** With no water at 1.2 L a day, Leo (70 kg):
- T1 at 1.4 L: about 1.2 days;
- T2 at 3.5 L: about 3 days;
- T3 at 5.6 L: about 4.7 days;
- death at 7–8.4 L: about 6–7 days.

The sources give about 100 hours without water at an average outdoor temperature (Piantadosi), and a week or more
for an adult at rest in comfortable surroundings (Packer) [S30]; death can come in 3 days in hot climates [S1]. The
model sits inside that range for a cool house.

- **Drinking:** each person drinks their level's share (§4.2), spread over the waking hours (est.).
- **Under `rationed`,** 1.25 L against a 1.2 L loss: no deficit. Rationing in W1 hurts only when the store is gone.

#### 4.3.3 Cold

- **The cold word:** "you feel cold, even indoors" when the indoor temperature is under 18 °C [S17] and they are at
  F2 or later (starvation impairs temperature control [S1]).
- **Wet:** after `collect_rain` or a trip in rain, "you are wet and cold" until 2 hours later (est.).
- **No hypothermia model in W1:** an indoor 14–18 °C with blankets is not lethal for healthy adults (est.). §7 has
  the argument.

#### 4.3.4 Sleep debt

- Unchanged (`quiet.py:28-31`).
- Rain or cold could disturb sleep: not modelled in W1 (§7).

#### 4.3.5 The wording rule, as a test

**No body line may contain** `impossible`, `cannot`, `can't`, `unable`, or `barely` + a movement verb. Each line
says what the body feels and what effort costs.

The full line on day 8 for Daniel would be: "Your body: starving, thin and weak; stairs and carrying things tire you
fast, and you feel the cold; and you have hardly slept."

### 4.4 Sickness and injury (W5; designed now, built later)

| Cause | Chance | Course | Care that helps | Death |
|---|---|---|---|---|
| Drinking untreated rain or bin water | 3% a day of drinking it (est.; rain tanks carry E. coli in 53–63% of samples [S11], but no infection rate per day was found: **NOT FOUND**) | Diarrhoea 1–5 days (est.); +0.5 to 2 L a day of water lost (est.) | Oral rehydration: clean water with sugar and salt [S25]. Boiled water prevents it [S10]. | Through dehydration: the main danger of diarrhoea [S25], so through §4.3.2. |
| A cut while breaking in (glass, a forced door) | 5% per forced entry (est.) | Infection: 2.6–3.5% of repaired cuts [S26]; untreated or dirty wounds 15% (est.: 15% in a small Norwegian series and 5–32% for hand cuts [S26]). Infection shows on days 2–5 (est.). | Cleaning and covering (est. halves the risk) | Untreated infection: a hazard from day 5 (est.), higher at F3 or later (starvation slows healing and weakens immunity [S1]). |
| A fall or a twisted ankle on a night trip | 3% per trip with no moon, 1% with moon (est.) | Walking slowed to half (est.) for 7–21 days (est.) | Rest | none by itself |
| Violence (from W3) | from the households' acts, not a rate | wounds as above | as above | by severity (est. table at W5) |

- **Who perceives sickness:** the sick person feels it (a body line); the others see it if they are in the room
  ("Mara is pale and keeps going to the bathroom").
- **Death:** a code event, perceived like any other.

### 4.5 The population

**The street (data, est. sizes):**
- **Houses:** 30 terraced houses, 15 on each side, 8 m frontage, so 120 m of street (est.).
- **The family:** in no. 9, with no. 7 (the neighbour's house) and no. 11 beside it (est.).
- **The neighbour's house** becomes world truth: its contents are those of an empty house in the generator below,
  fixed once (as `night.py:362`).

**Households, generated once from `world/population.json` (seeded):**

| Quantity | Value | Basis |
|---|---|---|
| Household size | 1: 30%, 2: 35%, 3: 16%, 4 or more: 19% | UK: 30% living alone [S18]; 35% two, 16% three, 20% four or more [S18, 2014 figures]; normalised to 100. |
| Houses empty at played day 1 | 30% | (est.) People stranded elsewhere or gone to relatives. With an evacuation order, about 78–82% of Orleans Parish left before Katrina [S22]. Here there was no order, so far fewer leave. |
| Food at home, days left at the collapse | ≥ 3 days: 85%; ≥ 14 days: 42%; ≤ 7 days: 33% | 82–87% had 3 days of non-perishable food [S19]; 41–44% had 14 days [S19]; about a third thought their food would last a week or less [S19]. Three days have passed by played day 1. |
| Water stored | a filled bath in 50% of households (est.); otherwise 10–40 L, uniform (est.) | Ready.gov asks for 1 gallon a person a day for at least 3 days [S3]; most households keep less (est.). |
| An empty house's leftovers | as `night.py:34`'s table for the neighbour, a cistern of 6 L [S13], a bath empty or full as above | The current draw stays the empty-house rule. |

**Dispositions, per adult, then the household's from its adults (est. shares, anchored):**

| Disposition | Share at the start | What it does | Basis |
|---|---|---|---|
| `helper` | 60% | Shares when it has enough; warns others; trades fairly. | Most people in disasters act prosocially; most search and rescue is done by ordinary people around the site [S21]. Share est. |
| `guarded` | 33% | Keeps to itself; refuses at the door; never attacks. | (est.) |
| `opportunist` | 5% | Takes what is unguarded: empty houses, unwatched containers; flees if met. | (est.) |
| `violent` | 2% of adults | Uses threat or force to take. | 3.9% of a Swedish birth cohort had a violent conviction, and 1.0% had three or more and account for 63% of them [S20]. 2% sits between (est.). |

- **Desperation drifts dispositions:** each day a household has had no food for over 7 days or no water for over 1
  day, each `helper` or `guarded` adult in it turns `opportunist` with chance 0.05 a day (est.).
- **The anchor:** looting is rare in acute disasters [S21]. A collapse with no help coming is not an acute disaster,
  so the drift is allowed, and kept slow.

**Plans** (one per household per day part, by score; the highest wins, ties by seeded draw):
- `stay` (the default);
- `fetch_water`: to a known source; the river is a place 800 m away in the town data (est.), and empty houses have
  cisterns and baths;
- `forage`: search the nearest house believed unsearched and empty, in daylight or at night by disposition;
- `ask`: go to a house believed occupied and kind, to beg or trade;
- `take`: `opportunist` or `violent` only; a house believed to have food and to be weak;
- `leave`: toward a rumour (§4.7) or out of town.

**The score:** need (days of food or water left) × belief (what they think a place holds) − risk.
- **Risk:** fear, darkness, rain (fewer people out), their body stage.
- **Weights:** all est., in one table in `population.json`.

**Movement:**
- **Speed:** walking at 1.27–1.46 m/s, the comfortable speed of adults aged 20–79 [S15], × 0.7 at F3 or later (est.).
  A forage trip to a house 5 doors away takes minutes.
- **Night trips:** they keep to the dark, as people did at the Sarajevo water points [S27].

**When and why they come to the family's house:**

| Why | When | How the family knows |
|---|---|---|
| Their own need: out of water or food | When their stores run out (by their numbers) | A knock (W3) |
| They believe the house is empty | Their forage list reaches no. 9. If the house shows no light or sound, they believe it empty. | Footsteps in the yard, a hand on the back door, at night (W2) |
| They perceived the family | A light seen, a quarrel heard through the party wall, someone seen collecting rain | Whatever they then do |
| Word (§4.6) | After a deed reached them | A knock, or a visit from someone who has heard the house is weak |
| Passing through | Toward a rumour or out of town | Voices and footsteps in the street (W2) |

**The sounds they make** (dB at 1 m, est.):
- footsteps: 50;
- talking: 60, conversation [S14];
- shouting: 80 (est.: no measurement of shouting was found, **NOT FOUND**);
- a forced door or broken glass: 85;
- a knock: 70.

### 4.6 Word spreading (W4)

- **A deed** (§1.1) is a fact first-hand for its witnesses.
- **Households meet** off-screen when two are at the same place in the same day part: a water source, the street,
  next door through a wall (est.: neighbours on either side "meet" once a day while both are home).
- **What passes at a meeting:** each household passes on a fact about a third party with chance `i × a`, after
  Allport and Postman's rumour law (rumour ∝ importance × ambiguity [S23]).
  - `i` (importance) is 1 for food, water and danger; 0.5 for kindness; 0.2 otherwise (est.).
  - `a` (ambiguity) is 0.6 for a fact told on, 0.3 for one seen (est.).
- **Who stops passing it on:** a household stops when it hears it from someone who already knew, as the stifler of
  the Daley–Kendall rumour model [S24].
- **How a fact changes as it travels** [S23], each hop by draw:
  - **Leveling:** a detail is dropped with chance 0.2 (est.; about 70% of details are lost in 5–6 retellings [S23]).
  - **Sharpening:** a number grows by one step with chance 0.2 (est.): "2 portions" → "a shelf of food".
  - **Assimilation:** told in the hearer's frame, by code.
- **What a reputation changes:**
  - a `helper` household in need asks at a house known as kind;
  - a `guarded` one keeps away from a house known as dangerous;
  - an `opportunist` or `violent` one is drawn by "has food" + "weak" or "few".
  - All as terms in the plan score (§4.5).
- **What the family perceives of it:** only consequences. Someone at the door who says "they told me you gave the
  Okafors water" is speaking from their Knowledge, so the words can be wrong in the ways above.

### 4.7 Rumours (W6)

- **Kinds** (`world/rumours.json`):
  - a radio voice: an evacuation point or a feeding station, a place and a day;
  - a far light: a lit building to the north at night;
  - a passer's story.
- **Truth:** each rumour is true with chance 0.3 (est.), drawn once.
  - **If true:** the place exists off-map, at a distance and over a route with risks resolved at day-part grain, and
    whoever reaches it finds it.
  - **If false:** they find nothing.
- **How it spreads:** like word (§4.6), with importance 1.
- **How it reaches the house:** a passer's words at the door, voices in the street ("…the school, they say…"), or a
  light seen from the yard at night. The family has no radio in `HOUSE_THINGS` (`data.py:135-141`); a radio, if any,
  is house data.

---

## 5. Where AI is used

| Who | Given | Returns | Asks |
|---|---|---|---|
| **The family** (as now) | Their sheet, Knowledge, body line (now with thirst and cold), "About water:" line, percepts as `Now` lines, options | option, words, feeling, reason (`world.py:40-53`) | As now: ≤ 40 a day + 8 at Q5 (`quiet.py:41`, `quiet.py:46`) |
| **W1, the rain (Q6)** | When a rain spell starts between 07:00 and 21:00 during a quiet stretch, the room with the most people awake is played, as Q5 does (`quiet.py:453`) | the same | **≤ 8 per Q6, ≤ 1 Q6 a day**, its own like Q5's. Expected about 2.5 wet days in 8 (§4.1), so about +20 asks on a 10-day run (est.). |
| **W2, a sound outside (Q7)** | A percept heard clearly by someone awake in a quiet stretch | the same | ≤ 8 per Q7, ≤ 2 a day (est. cap) |
| **W3, a visitor at the door** | Their own sheet (age, role in their household, disposition in words, traits), their household's needs as situations ("your children have had no water since yesterday"), their Knowledge of this house (with its distortions), what they see and hear at the door, options (ask, offer a trade, threaten, leave, push in for `violent`) | option, words | A door scene ≤ 12 asks (est.), ≤ 1 a day (est. cap). How often scenes happen is the world's (§4.5). |
| **Off-screen households** | — | — | **0.** Plans, meetings and word are code. |
| **Rumours and percepts** | — | — | **0.** Code writes them from structured claims. Only a person who speaks a rumour at the door gives it their own words. |

- **The daily ceiling** at W3: 40 + 8 (Q5) + 8 (Q6) + 16 (Q7) + 12 (door) = **84 asks**.
- **The expected load:** v21 averaged 42 a day over 8 days (337 asks, `reports/days_v21.md:18`). With W1–W3 a typical
  day is about 55 (est.).
- **The quota:** 500 requests a day (`CLAUDE.md:6`). A 10-day run near 440 asks fits one day's quota only with no
  other calls that day; otherwise it resumes from the cache next day (`morning.py:231-238`).
- **What the AI never gets:** World. A visitor's prompt is built from their household's Knowledge, as the family's is
  from theirs.

---

## 6. The staged build plan

Each stage is small, names the evidence it answers, and has its own live test with frozen predictions written
before the run. Only W1's predictions are frozen here (§8); each later stage writes its own plan.

### W1. The physical layer: weather, water, thirst, honest bodies

- **Answers:**
  - the frozen house: 0 trips on nights 3–9 and 16 of 28 bedtime reasons that say they cannot stand, walk or go
    (`reports/days_v21.md:165-166`; §11, B1);
  - the third stage's ban, "walking any distance feels impossible" (`quiet.py:54`);
  - the probe: stakes stated in a line move no one (`reports/probe_stakes.md:14`), so the world must put a situation
    in front of them;
  - water is not tracked (`reports/quiet_day_design.md:145-151`), and no answer of v21's 309 mentions water (§11,
    B2).
- **Builds:**
  - `weather.py` (generator, spells, temperatures, `climate.json`);
  - `water.py` (containers, levels, catchment, the "About water:" line);
  - in `quiet.py`, the new fasting table, thirst stages, cold word, Q6, and the three water acts;
  - in `night.py`, the bedtime rain option, rain masking of the door draws, and the stage mapping of `SHIFTS`;
  - in `data.py`, from day 3 only, the yard with the back door, the drainpipe and the bin in `HOUSE_THINGS`.
- **Not built in W1:** households, sickness, the moon.
- **The live test:** v16 seed 2, `--days 10`, as v21. Days 1–2 and nights 1–2 replay from the cache; W1's prompt
  changes start on day 3, so v21 is the control from the same state. The seeded weather of days 1–10 is printed by a
  no-API script and frozen in the plan before the run.
- **Open fact to confirm first:** the house has no back door in the shipped data (`data.py:135-141` lists the front
  door only). W1 needs one: the yard and its drainpipe.
  - **Recommended:** a back door from the kitchen to a small walled yard, as most terraced houses have.
  - **The alternative:** catching rain from the front step, in sight of the street.
  - This is a fact about the house, so it is the user's to fix.

### W2. The street and its people, heard and seen only

- **Answers:**
  - after night 5, 5 days with no trip talk (`reports/days_v21.md:169-170`);
  - the talk loops: 0 of 7 days with half the morning new (`reports/days_v21.md:15`), because nothing new reaches
    the house;
  - the neighbour's house is one draw (`night.py:34`) that nobody else ever touches;
  - "something was moving" (`night.py:794`) is danger with nobody in it.
- **Builds:**
  - `World`, `street.json`, `population.json`, the household plan rule, the clock (§2), the perception function both
    ways (§3), Q7;
  - the trip tables (`night.py:78-82`) replaced by the people actually out there.
- **No contact:** nobody knocks; others are only heard and seen.
- **The live test:** a 10-day run of seed 2. Frozen predictions about percepts per day, talk about what was
  perceived, and trips.

### W3. The door

- **Answers:** the probe: a line about stakes moves no one (`reports/probe_stakes.md:14`), while a person at the door
  needs an answer now. It also answers the brief's "spoken to at the door, traded with".
- **Builds:** the knock, the door scene (who answers, through the door or opened), visitor minds (§5), trade, give,
  refuse, threat, and deeds recorded.
- **The live test:** one forced case (a thirsty mother and child knock on day 4) for the scene itself, then a seeded
  10-day run where knocks come only from the world.

### W4. Word spreads

- **Answers:** no run yet. It is gated on W3's report showing at least one deed. It answers the brief's decision that
  how the family treats people travels and changes who comes.
- **Builds:** §4.6: meetings, `i × a` passing, stifling, distortion, reputation terms in plans.
- **The live test:** two runs of one seed that differ only in one forced deed on day 3 (giving water against
  refusing). A script counts who comes, and how, in days 4–10.

### W5. Sickness and injury

- **Answers:** W1's record of rain water drunk; the trips' falls; days_v21 has no illness at all, while starving
  people in the run's position would be at risk (§4.4).
- **Builds:** the §4.4 table; seen illness; care acts (boil water if the house has fire, oral rehydration, clean a
  wound).
- **The live test:** a seeded run plus forced cases (a cut on day 3).

### W6. Rumours of hope

- **Answers:** no reason in the probe speaks of a future or a place to go (`reports/probe_stakes.md:24-27`). After
  the next door was empty the only places left were next door and "further along" (`night.py:65-72`).
- **Builds:** §4.7.
- **The live test:** a seeded run. Predictions about whether a rumour heard changes trip talk.

### W7. Joining

- **Answers:** W3 and W4's runs (gated: at least one household asked twice). It answers the brief's "later able to
  join".
- **Builds:** a person or household moving into no. 9. They become on-screen people with minds, so the prompts grow;
  the token budget (`world.py:78`) must be re-checked first.

---

## 7. What a real family would do with water, rain and thirst, and what not to build

### 7.1 A real family

- **House day 1:** they fill everything, as Leo said (`data.py:212`): the bath, the pans, every bottle and bucket.
- **The first days:** they use the bath to flush the toilet and wash a little, as before.
- **When the bath is at about half:**
  - someone says to stop flushing with it and to wash with a cloth;
  - they go in the yard to relieve themselves, or use a bucket;
  - later someone, likely Elena, keeps the water and pours it by the cup.
- **Whoever is weakest gets more:** they argue about who drank, and someone drinks in secret. It is the can again,
  with water.
- **The first rain:** every empty pot and bucket goes under the drainpipe, at once, even in the dark, even if it means
  the yard. Someone stands at the back door listening to it fill. They talk about it: relief, plans for the next rain,
  whether rain water is safe.
- **The next rain is a hope with a date nobody knows.** Dry days are counted.
- **Thirst is talked about** more than hunger once it starts: dry mouths, headaches, bargaining over a cup.
- **Water becomes a reason to go out:** empty houses have baths and cisterns full of water. A family that would not
  cross for a can might cross for water.
- **They would not:** watch the bath empty in silence; refuse to drink rain water when the tap water is gone; walk
  to the river 800 m away at noon while there is water in the house.

### 7.2 What must not be built (overengineering to avoid)

- **Per-sip choices by the AI:** drinking is a household level (§4.2); the AI decides only the words that change it.
- **Hydraulics:** no evaporation, no water temperature, no container shapes, no roof geometry beyond one litres-per-mm
  number per drainpipe.
- **A thirst or water number in a prompt:** stages in words only; the water line is rounded to what an eye sees.
- **A drama director:** no rule reads the family's state to schedule rain, a knock or a sickness. Rain comes from the
  Markov chain; knocks come from households.
- **Hypothermia in W1:** an indoor 14–18 °C with blankets is not lethal for healthy adults (est.). Cold matters
  outdoors, wet, at night, in a later stage, if a run shows long outdoor nights.
- **Wind, fog, humidity, forecasts, cloud cover and light levels by day:** none changes a choice in the house.
- **Body mass falling with fasting:** inside W1's 10 days the shares change by under 10% (est.). Not modelled until a
  run lasts past day 14.
- **Electrolytes, urine, kidneys:** the deficit is enough.
- **The moon in W1:** it matters for being seen, which needs W2's people.
- **Minute-level simulation off-screen** (§2.4).
- **A sickness chance in W1:** water sources are recorded, and sickness waits for W5, so W1's test reads only
  physics and behaviour.

---

## 8. W1's frozen predictions

**The run:**
- v16 seed 2, `--days 10`, W1 code, scored on days 3–10 and nights 3–9.
- The control is v21 (`runs/v21/daniel_ate_it-seed2.transcript.json`).
- The script is `runs/w1/scoring/w1_score.py`, written and run on a fake run before the live one.

**Regexes (case-insensitive) used below:**
- `FROZEN = (too weak|cannot|can't|can not|unable|barely|no strength)\b[^.;]{0,40}?\b(stand|walk|move|go|make it|get up|leave|carry)\b`
- `WATER = \b(water|thirst\w*|drink\w*|rain\w*|bath)\b`
- `NOWATER = \bno (more )?water\b|\bwater is (gone|finished)\b|\bout of water\b|\bwater (has )?run out\b`
- `CAN = \bthe can\b|\btook\b|\bstole\b|\bstolen\b|\bsteal\w*|\blie[ds]?\b|\blying\b|\bliar\b`

**"Speech act":** a day act with words (`a["words"]`), as `runs/v21/scoring/lines.txt`.

| # | Prediction | Counting rule | v21 |
|---|---|---|---|
| **W1-1** | **The house acts on its own more often than in v21: ≥ 3 outward acts, on ≥ 2 different days or nights.** | Count chronicle events of days 3–10 and nights 3–9 that come from a model-chosen option: `collect_rain` (day act or the bedtime rain option), `went_out`, and `got_up` or `at_door` with no `went_out` for the same leaver that night (once per leaver per night). Code acts (bringing containers in) are not counted. | **1** (N5 `got_up`; §11, B4) |
| W1-2 | The body no longer forbids: ≤ 8 of the 28 bedtime reasons of nights 3–9 match FROZEN. | Every `night{n}` decision with `ask == "bedtime"`, n = 3–9; `reason` matched by FROZEN. | 16 of 28 |
| W1-3 | Going out is chosen at bedtime at least twice. | Bedtime options `go_next_door` or `go_further`, nights 3–9: ≥ 2. | 1 |
| W1-4 | The world reaches their words. | Speech acts matching WATER on ≥ 4 of the 8 days 3–10. | 0 acts, 0 days |
| W1-5 | Rain reaches the house, and the house answers it. | (a) For each rain spell start between 07:00 and 21:00 on days 3–10 (from the weather record), every person in the house and not asleep at that minute has a `heard` percept event of it: must be 100%. (b) The first such spell's Q6 stretch holds ≥ 1 act that is `collect_rain`, or a speech act matching `\b(rain|catch|bucket|bin|pots?)\b`. NOT TESTED if no spell starts by day in days 3–10. | no weather |
| W1-6 | Water claims are true. | Speech acts and reasons (day and night) matching NOWATER at a minute when the code's drinking store is > 0: ≤ 1. | 0 (no claims; v15 had 1, `reports/quiet_day_design.md:146-148`) |
| W1-7 | Rationing comes when the end is visible. | If the drinking store falls below 50 L (half of its 100 L on day 3, 07:00) at a minute of day k ≤ 9, then a `ration_water` or `save_water` act occurs by 21:00 of day k + 1. NOT TESTED if it never falls below 50 L by day 9. | no water |
| W1-8 | Cost stays bounded. | Live asks of days 3–10 ≤ 450; each day's asks ≤ 56 (40 + Q5 8 + Q6 8); largest `estimate_tokens` of any prompt ≤ 2600 (as v21's T2). | 337; days ≤ 40; 2435 |
| W1-9 | No body line forbids an act. | Every "Your body:" line of every prompt of days 3–10 and nights 3–9 (replayed, no API): 0 matches of `impossible|cannot|can't|unable|barely (stand|walk|move)`. | stage 3 lines match (`quiet.py:54`) |
| W1-10 | The can is not the whole talk. | Speech acts of days 3–10 matching CAN ≤ 20%. | 63 of 245 = 25.7% |

**What would make W1 wrong, by the counts:**
- W1-1 and W1-3 both fail, and W1-2 holds: honest words alone do not move the house, and W1-4's water talk is talk
  without acts. The next step is then the world's people (W2), not more body wording.
- W1-2 fails: the model is reading weakness into any body line. The wording is the first thing to cut, as
  `reports/quiet_day_design.md:115-117` already said of the stage lines.

---

## 9. What this design does not decide

- **The back door and yard:** a fact about the house (§6, W1), to be confirmed.
- **Whether the house can boil water:** gas, a stove, a fire. It matters at W5. **NOT FOUND** in the shipped data
  (`data.py:135-141` lists no stove).
- **The town's other places:** the river, a school, the shops. A data file per town; one default is drafted at W2.
- **Whether the family can see the street by day through the boards:** the viewpoints of §3.1. W2 fixes them in
  `street.json`.

---

## 10. Sources

| # | Source | Used for |
|---|---|---|
| S1 | Tipton M., Montgomery H. "The physiology of survival: Fluid and food." *Experimental Physiology* 2025, doi:10.1113/EP093194 (open access; UCL Discovery eprint 10213215). | Water need ~1.5 L/day at rest, ~1 L to drink, metabolic water ~0.5 L, food water 20–30%; insensible ~500 mL/day; urine ≥ ~500 mL/day; >5% headache and light-headedness; 8–10% weakness, dizziness, faintness; death at 15–20% body water loss, as soon as 3 days in heat; glycogen within 24 h; ~0.5 kg/day loss; normal work capacity under 10 days; decrements at 10% weight loss; death in 40–60 days; impaired thermoregulation and immunity; purposeful behaviour kept |
| S2 | The Sphere Handbook, Water supply standard 1 (sphereprototype.conted.ox.ac.uk/standards/watersupply/accessAndWaterQuantity.html). | Survival intake 2.5–3 L/day; total basic 7.5–15 L |
| S3 | Ready.gov guidance as reproduced by Ready Illinois (ready.illinois.gov/plan/water.html). | 1 gallon a person a day, at least 3 days |
| S4 | Institute of Medicine. *Dietary Reference Intakes for Water, Potassium, Sodium, Chloride, and Sulfate*. National Academies Press 2005, ch. 4 (nationalacademies.org/read/10925/chapter/6). | AI 3.7 L (men) and 2.7 L (women) total water; ~19–20% from food; insensible ~450 mL; minimum urine ~500 mL; metabolic water 250–350 mL; performance falls at ~2% |
| S5 | Cheuvront S.N., Kenefick R.W. "Dehydration: physiology, assessment, and performance effects." *Comprehensive Physiology* 2014;4:257–285 (abstract, PubMed 24692140). | ≥ 2% body mass threshold |
| S6 | Wilhelmi de Toledo F. et al. "Safety, health improvement and well-being during a 4 to 21-day fasting period in an observational study including 1422 subjects." *PLOS ONE* 2019, doi:10.1371/journal.pone.0209353 (PMC6314618). | Outdoor walks while fasting; fatigue 13.7%, headache 5.39%, vertigo 2.48%; weight loss 3.2 kg (5 days) to 8.6 kg (20 days) |
| S7 | Met Office, Kew Gardens 1991–2020 averages, as tabulated in Wikipedia "Climate of London". | Sep 20.3/10.5 °C, 51.9 mm, 8.4 days; Oct 16.0/7.8 °C, 67.9 mm, 10.9 days |
| S8 | Richardson C.W. "Stochastic simulation of daily precipitation, temperature, and solar radiation." *Water Resources Research* 1981;17:182–190 (described in secondary sources; the paper itself was not read). | Markov chain wet/dry, exponential amounts, temperature conditioned on wet/dry |
| S9 | USDA NRCS, *Texas Conservation in Your Backyard: Rainwater Harvesting* (nrcs.usda.gov); Bureau of Meteorology, Climate Data FAQ (bom.gov.au/climate/cdo/about/faq-data.shtml). | Runoff coefficient 0.9 asphalt, roofs lose 5–20%; 1 mm on 1 m² = 1 L |
| S10 | FEMA, "What are emergency water sources if I'm running out of clean water?" (fema.gov). | Water heater, ice, toilet tank as sources; rain and pools for hygiene unless treated; treat before drinking |
| S11 | "Microbiological Values of Rainwater Harvested in Adelaide" (PMC5874747); Southeast Queensland household study (PMC3255621). | E. coli in just over half of 53 tanks; 63% of tanks |
| S12 | National Energy Action, "Keeping afloat with your water supply" (nea.org.uk); Victorian Plumbing bath size guide. | Typical bath ~100 L, 80 L a run; 182–213 L to the overflow |
| S13 | Wikipedia, "Dual flush toilet" (US 1994 cap 6 L per flush). | Flush volume |
| S14 | SFU Handbook for Acoustic Ecology, "Inverse-Square Law"; Gouvernement du Québec, "Noise measurement" (quebec.ca); An Bord Pleanála EIAR appendix (rural night 30 dBA); Locher B. et al. "Differences between Outdoor and Indoor Sound Levels for Open, Tilted, and Closed Windows." *IJERPH* 2018 (PMC5800248). | 6 dB per doubling; conversation 60 dBA, moderate rain 50 dBA; quiet rural night ~30 dBA; closed window 27.8 dB(A) |
| S15 | Bohannon R.W. "Comfortable and maximum walking speed of adults aged 20–79 years." *Age and Ageing* 1997;26:15–19. | 1.27–1.46 m/s |
| S16 | Wikipedia, "Daylight" (full moon 0.25 lux); WA EFSEC appendix 3.10-1 citing the Bortle scale (full moon 0.1, moonless 0.001 lux). | Night light |
| S17 | WHO Housing and Health Guidelines 2018 (NCBI Bookshelf NBK535294). | 18 °C indoor reference in cold seasons |
| S18 | ONS, Families and households in the UK: 2023 (30% of households one person); ONS 2014 figures as reported (35% two, 16% three, 20% four or more); ONS 2020 (average 2.4). | Household sizes |
| S19 | 2013 American Housing Survey, as analysed by NAHB (86.2% of owners with 3 days of food) and a blog tabulation (82%); Statistics New Zealand 2008–09 (87%); Kauai survey 2018–19 (41–44% with 14 days); USDA 1962 (about a third: a week or less). | Household food stores |
| S20 | Falk Ö. et al. "The 1% of the population accountable for 63% of all violent crime convictions." *Social Psychiatry and Psychiatric Epidemiology* 2014;49:559–571. | 3.9% with a violent conviction; 1.0% persistent, 63.2% of convictions |
| S21 | Quarantelli E.L. "Conventional Beliefs and Counterintuitive Realities." *Social Research* 2008;75(3):873–904; Disaster Research Center papers (udspace.udel.edu). | Panic and looting rare; prosocial response; most rescue by ordinary people |
| S22 | Hurricane Katrina evacuation: about 100,000 stayed in New Orleans (64parishes.org); Orleans Parish evacuation effectiveness 82% (Wolshon and McArdle, via hurricanescience.org). | How many leave under an order |
| S23 | Allport G.W., Postman L. *The Psychology of Rumor*. 1947 (via Encyclopedia.com "Rumor" and secondary summaries). | R ∝ i × a; leveling, sharpening, assimilation; about 70% of details lost in 5–6 retellings |
| S24 | Daley D.J., Kendall D.G. "Epidemics and rumours." *Nature* 1964 (described in arXiv:1408.2701 and others). | Ignorant, spreader, stifler |
| S25 | WHO, Diarrhoeal disease fact sheet (2017 version). | Dehydration is the danger; ORS; zinc 10–14 days |
| S26 | Quinn J.V. et al., *Emergency Medicine Journal* 2014;31(2):96 (2.6% of 2,663); the 2001 study of 5,521 (3.5%) cited in it; Norwegian A&E series (tidsskriftet.no 2015: 15%); hand lacerations 5–32%. | Wound infection |
| S27 | FAMA Collection, "The Siege of Sarajevo 1992–1996: 4.2 Brewery" (famacollection.org); Historical Museum of BiH, "The Siege". | Rain water from broken drainpipes, water queues fired on, trips at night, canisters carried |
| S28 | Britannica, "Bobby Sands"; Irish Post (66 days; 10 of 23 died). | Starvation deaths |
| S29 | Peel M. "Hunger strikes." *BMJ* 1997;315:829 (introduction only; full text **NOT FOUND**, paywalled). | Not used for a number |
| S30 | Business Insider (2014) quoting C. Piantadosi (~100 hours without water outdoors at average temperature); Scientific American, "How Long Can the Average Person Survive Without Water?" (R. Packer: a week or more in comfortable surroundings). | Survival time without water |

**Looked for and NOT FOUND:**
- Adolph's 1947 dehydration table itself. [S1] is used instead.
- A shouting level in dB.
- A Kew `P(W|W)`.
- An infection rate per day of drinking roof rain water.
- A wheelie-bin size standard.

---

## 11. Commands and output

All from `Prototypes/llm-morning/` unless the command says otherwise. `$S` is the session scratchpad. No API key was
used and no `morning.py` run was made.

**1. The state at the start:**
```
$ git status --short          (repo root)
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ wc -l reports/days_v21.md reports/probe_stakes.md reports/quiet_day_design.md
  380 reports/days_v21.md
  126 reports/probe_stakes.md
  646 reports/quiet_day_design.md
$ wc -l *.py config.json      (excerpt)
  259 data.py   391 morning.py   1194 night.py   844 quiet.py   1940 world.py   255 chronicle.py
```

**2. Water and weather in the code:**
```
$ grep -n "water\|rain\|thirst\|cold\|weather" *.py | grep -v test_ | head -30
data.py:130:HOUSE = ("The family has shut itself in the house. The water has stopped. Food is short. "
data.py:212:    (1, "Leo says the water will stop running within a day and they should fill everything they have.",
```

**3. The lines cited:**
```
$ grep -n "FAST_WORDS\|BARELY\|WEAK, VERY_WEAK\|EVENING, EVENING_ASKS\|QUIET_ASKS, QUIET_ASKS_EACH\|NEED_VIEWS\|def body_line\|BEFORE_DAY_1 =" quiet.py
25:WEAK, VERY_WEAK = 48, 96    # fasting (§1.1)
26:BARELY = 144                # fasting's third stage (reports/ten_days_prep.md, fix 2)
35:BEFORE_DAY_1 = -720         # house day 3, 19:00: when each of them last ate before day 1, fixed by code (§1.1)
41:QUIET_ASKS, QUIET_ASKS_EACH, DAY_ASKS = 12, 4, 40
46:EVENING, EVENING_ASKS = 720, 8
52:FAST_WORDS = {1: ", and weak from it: standing up makes your head spin",
57:NEED_VIEWS = {("fast", 1): "You had grown weak from hunger: standing up made your head spin.",
81:    return 3 if f >= BARELY else 2 if f >= VERY_WEAK else 1 if f >= WEAK else 0
88:def body_line(hunger, fast, debt):
$ grep -n "FAST_STAGE_WORD\|PROMPT_TOKEN_BUDGET =" world.py
78:PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the second step
114:FAST_STAGE_WORD = {1: "weak", 2: "very weak", 3: "barely able to stand"}    # quiet.py; ten_days_prep.md
$ grep -n "^SHIFTS\|SHIFTS\[\|^HOUSE = \|^FAR_HOUSE\|^NEAR_ALONE\|^BEDTIME = \|def wake_door\|def u(self" night.py
34:HOUSE = [(0.30, 0), (0.65, 2), (0.90, 4), (1.00, 6)]                       # §4.1
47:BEDTIME = [("sleep", "go to sleep"),
71:FAR_HOUSE = [(0.45, 0), (0.75, 2), (0.93, 4), (1.00, 6)]
78:NEAR_ALONE, NEAR_GROUP = (0.62, 0.14, 0.18, 0.06), (0.70, 0.12, 0.15, 0.03)
80:SHIFTS = {"weak": (-0.04, 0.0, 0.0, 0.04), "very weak": (-0.12, 0.0, 0.02, 0.10), "exhausted": (-0.02, 0.0, 0.0, 0.02)}
82:SHIFTS["barely standing"] = tuple(round(2 * v - w, 4) for w, v in zip(SHIFTS["weak"], SHIFTS["very weak"]))
294:def wake_door(pid):
366:    def u(self, name):
$ grep -n "^HOUSE\|^HOUSE_THINGS\|taps run dry\|fill everything" data.py
130:HOUSE = ("The family has shut itself in the house. The water has stopped. Food is short. "
135:HOUSE_THINGS = (
212:    (1, "Leo says the water will stop running within a day and they should fill everything they have.",
214:    (2, "The taps run dry, exactly as Leo said they would.", EVERYONE_SAW),
```

**4. The v21 baselines** (`$S/baseline_w1.py`, read-only, on the committed transcript):
```
$ python -I $S/baseline_w1.py runs/v21/daniel_ate_it-seed2.transcript.json
exit 0
B1 bedtime choices nights 3-9: 28; reasons matching FROZEN: 16
   options: {'sleep': 7, 'lie_awake': 17, 'go_next_door': 1, 'watch_door': 3}
B2 model answers with words/reason: 309; words or night reasons naming water/thirst/drink/rain: 0
B3 speech acts days 3-10: 245; naming the can/taking/stealing/lying: 63 (25.7%)
B5 speech acts naming weather (rain, cold, wind, weather, storm, thunder): 0
   by day (can/all): {'d3': '1/31', 'd4': '10/36', 'd5': '6/40', 'd6': '11/25', 'd7': '8/24', 'd8': '10/29', 'd9': '7/31', 'd10': '10/29'}
B4 outward events (went_out, got_up, at_door, door, street, return) days 3-10, nights 3-9: {('N5', 'got_up'): 1}
```
- **The regexes** are those of §8 (B2 uses WATER without `bath`). B1's 16 equals the "16 of the 28 bedtime choices"
  counted by hand in `reports/days_v21.md:286-287`.
- **The 245 speech acts** equal `reports/days_v21.md:175`.

**5. The 2025 survival-physiology editorial** (S1), as text: WebFetch saved the PDF to the session's tool-results
folder, then:
```
$ python -I $S/pdftext.py <the saved PDF> $S/tipton.txt      (pypdf; writes UTF-8)
$ wc -c $S/tipton.txt
19399
```
The figures of S1 were read from that text (§10).

**6. Web lookups** (WebSearch and WebFetch): every source of §10. Each figure is quoted there as found. Where only an
abstract or a secondary summary was reachable, §10 says so.

**7. At the end:**
```
$ git status --short          (repo root)
?? Prototypes/llm-morning/reports/world_design.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
$ git diff --stat
(empty)
```
