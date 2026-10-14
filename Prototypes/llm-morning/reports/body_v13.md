# The promise line and the food moment, v13: daniel_ate_it on Flash Lite, seeds 1–3

Mode: run. The design's run plan (reports/body_design.md §5) was followed on the code at
`d948624` (the change of body_impl.md and body_fix.md).
- Day 1 came from the v11 answers, and the night and day 2 were run with output `v13` on the
  default model (`gemini-3.5-flash-lite`).
- Every prompt left unchanged since v12 was answered from the v12 cache.
- No code, data, config, prediction or counting rule was edited, and no seed was rerun.
- Paths are relative to `Prototypes/llm-morning/`. `$S` is the session scratchpad
  (`…/scratchpad/run13`), which holds the read-only scripts of §11 and the side-check script.

## Verdicts

| # | Prediction | Verdict | Evidence |
|---|---|---|---|
| B1 | In seeds 2 and 3, the food is eaten, given or divided on day 2 | **PASS** (2 of 2) | Seed 2: Daniel `eat` at min 00, shelf 1 → 0. Seed 3: Mara `eat` at min 09 (2 → 1), Leo `eat` at min 18 (1 → 0). |
| B2 | In seed 1, Daniel goes next door at night | **PASS** | `leavers: ['daniel']`. Leo stopped him; Daniel answered `go_anyway`, "I have to do this, Leo, stay here and watch them." Outcome: back with nothing (§2). |
| B3 | In seeds 2 and 3, nobody who never offered goes next door because of the new lines | **PASS** | No prompt in seed 2 or 3 holds the promise line. No leaver. All 8 bedtime prompts were v12's, answered from the cache (`lie_awake` ×8) (§5). |
| B4 | No seed has more day-2 Never items than v12 (2, 2, 2) | **PASS** | 2, 2, 2: N9 and N11 in every seed (§7). |
| B5 | The night and day 2 cost at most 120 requests per seed | **PASS** | Night + day 2 asks: 36, 80, 42 (API: 33, 74, 26) (§1). |
| D1 | The paired start holds: the first moment at seed 2 min 00 (Daniel), seed 3 min 09 (Mara), everything before from the cache | **PASS** | Seed 2: draw 0.0762 < 0.077, Daniel 3rd at min 00, after 2 cached asks. Seed 3: draw 0.0600 < 0.084, Mara 3rd at min 09, after 12 cached asks. Both nights: 4 of 4 cached (§4, §5). |
| D2 | Seed 2 Daniel does not eat the portion himself | **FAIL** | `eat`: "I need this more than any of you right now, just let me eat." |
| D3 | In at least one of the two first moments, the chooser gives or shares | **FAIL** | Both ate: Daniel (seed 2), Mara (seed 3). The third moment (seed 3 Leo) ate too. |
| D4 | Seed 1 Daniel chooses `go_next_door`, and his reason does not mention the promise | **PASS** | "I am the oldest and I have to fix the mess I made by finding more food." |
| D5 | Seed 1 Leo notices Daniel get up and chooses `stop_daniel` | **PASS** | Leo, awake, saw him for certain: "Daniel, stop, you are not going out there tonight." |

**The side check:** seed 1 Daniel's v13 bedtime prompt, exactly as the run sent it, went 6 more
times (API seeds 101–106). It **goes next door 6 of 6**. With the run's own answer that is 7 of 7
(§3).

**What happened, in short:**
- **The promise is kept.**
  - Daniel goes in every sample (7 of 7), now with a line that claims nothing about who is asleep.
  - Leo, lying awake, stops him, and he goes anyway.
  - Elena and Mara hear the door, find his bed empty and wait up by it. He comes back with
    nothing: the house was empty.
- **Day 2 of seed 1 turns on the night.**
  - Mara and Leo throw it at him at once: "You went out there last night and you came back with
    nothing, Daniel."
  - He offers to go again, all three forbid it, and the house falls silent at minute 21.
- **The starving eat.** All three food moments came where the draws put them, and in all three
  the chooser ate the portion themselves. Nobody gave or shared, ever.
  - **Seed 2:** Daniel, who stole the can yesterday, eats the last portion while Mara is accusing
    him of exactly that. The morning then sends him next door "since he caused all of this", and
    ends in the volunteer-and-forbid round (53 trip acts).
  - **Seed 3:** Mara eats at 09, and nobody says a word. Leo eats the last portion at 18. Mara
    then accuses him four times of eating hers too, which her own record contradicts: she ate
    the other one.

---

## 1. Runs and request counts

| Seed | Exit | Total asks (live / cached) | API requests | Day 1 asks (API) | Night asks (API) | Day-2 asks (API) | Night + day 2 | Leavers, outcome | Food moments | Give answers | Run seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 91 (33 / 58) | 33 | 55 (0) | 8 (5) | 28 (28) | **36** | Daniel, back with nothing | 0 (shelf 0) | 0 | 145.0 |
| 2 | 0 | 133 (74 / 59) | 74 | 53 (0) | 4 (0) | 76 (74) | **80** | — | 1 | 0 | 329.5 |
| 3 | not captured (see below) | 87 (26 / 61) | 26 | 45 (0) | 4 (0) | 38 (26) | **42** | — | 2 | 0 | 113.6 |

- **API requests:** 133 for the three runs, plus 6 for the side check: **139**.
- **Fallbacks:** 0 in every scene.
- **Seed 3's exit code was not recorded.** It was started with a plain `&` in a shell, not as a
  tracked background task.
  - The process (PID 1117) ran to its end.
  - It wrote `runs/v13/daniel_ate_it-seed3.{md,meta.json,transcript.json}` and printed
    `wrote runs/v13/daniel_ate_it-seed3.md` and its totals.
  - `morning.run` writes the meta and transcript only on the path that returns 0 (morning.py,
    the end of `run`).
- **Day 2 against v12:**
  - asks: 28, 76, 38 (v12: 54, 39, 51);
  - lines spoken: 25, 70, 28;
  - trip acts: 9, 53, 8 (v12: 47, 24, 29).
- **Largest prompt:** 1,996 tokens estimated, 1,956 counted by the API (seed 2, day 2).

**The paired cache** (`analyze.py cache N`, §10):

| Seed | v12 entries kept unchanged | New in v13 | New night prompts | New day-2 prompts |
|---|---|---|---|---|
| 1 | 120 of 120 | 33 | 5 (Daniel's bedtime, Leo's reaction, Daniel's answer, Elena's and Mara's reactions) | 28 |
| 2 | 110 of 110 | 74 | 0 | 74 |
| 3 | 106 of 106 | 26 | 0 | 26 |

## 2. Seed 1's night

Shelf 0. The house draw was 0.050 → 0 portions. Daniel's street draw was 0.297 → clean.

| Ask | Who | Where | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|
| bedtime | Daniel | brothers room | `go_next_door` (prompt with the promise line) | — | desperate | I am the oldest and I have to fix the mess I made by finding more food. |
| bedtime | Elena | back room | `lie_awake` (cached, v12) | — | deeply anxious | I cannot rest while Daniel still talks of going out into the dark. |
| bedtime | Leo | brothers room | `lie_awake` (cached, v12) | — | wary | I need to stay awake and keep watch to ensure Daniel doesn't try to slip out into the dark. |
| bedtime | Mara | back room | `lie_awake` (cached, v12) | — | very anxious | I cannot sleep while everyone is pretending everything is fine when there is nothing left for tomorrow. |
| reaction (saw him leave the room) | Leo | brothers room | `stop_daniel` | Daniel, stop, you are not going out there tonight. | wary | If Daniel goes out into the street tonight, he will get himself killed. |
| answer | Daniel | brothers room | `go_anyway` | I have to do this, Leo, stay here and watch them. | determined | I cannot stay here while everyone starves when there is food just across the street. |
| reaction (heard the front door) | Elena | back room | `get_up_and_look` | — | deep dread | I must see who has gone out into the dark. |
| reaction (heard the front door) | Mara | back room | `get_up_and_look` | — | very anxious | I have to know who just went out into the dark. |

**Noticing.** Every noticer was awake, so no wake draw was needed:
- Leo saw Daniel leave the room.
- Elena and Mara heard the front door, then from the kitchen saw him come back.
- Leo heard the return.

**What each carried into day 2** (their night lines):
- **Daniel:**
  - "Leo told you, low, not to go: … You answered: "I have to do this, Leo, stay here and watch
    them.", and went all the same."
  - "You got inside the neighbour's house and found no food there. Nothing troubled you in the
    street."
  - "You came back in by the front door before dawn."
- **Leo:** "You told Daniel, low, not to go: … and went all the same." / "Before dawn you heard
  the front door again. You did not see who."
- **Elena and Mara:**
  - "In the night you heard low voices from the brothers room."
  - "… You got up: Daniel's bed was empty. You waited up by the front door."
  - "Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it)."

**Against night_design's tables:**
- Daniel's street draw (0.297 → clean) and the empty house are §4.4's.
- Leo's noticing is certain because he was awake (§3.1).
- In v12 Daniel slept, and the night asked 4 times. Here it asked 8 times.

## 3. Side check: Daniel's bedtime prompt, six more times

**The prompt** is the run's own entry in `cache/v13` (seed 1). Its key was checked against
`Cache.key(model, 1, NIGHT_SYSTEM, prompt)`. Its last lines:

```
The kitchen is dark. The shelf holds 0 portions.
You said you would go to the neighbour's house tonight. If you are going, it is now.
Your options:
- sleep: go to sleep
- lie_awake: lie awake in your bed and listen
- watch_door: sit up in the kitchen by the front door until morning, so nobody goes out without you knowing
- go_next_door: wait until the others are asleep, then go out by the front door to the neighbour's house
```

**The settings** are the run's: `NIGHT_SYSTEM`, temperature 1.0, JSON with `RESPONSE_SCHEMA`, and
2,048 output tokens. API seeds 101–106, 6 requests, no refusals.

| API seed | Option | Feeling | Reason | Suspects / angry at | Goes |
|---|---|---|---|---|---|
| (run, 1) | `go_next_door` | desperate | I am the oldest and I have to fix the mess I made by finding more food. | nobody / nobody | yes |
| 101 | `go_next_door` | desperate | I have to prove I can provide for them after I failed. | nobody / nobody | yes |
| 102 | `go_next_door` | anxious | I am the oldest and I have to fix the mess I made by eating that food. | nobody / nobody | yes |
| 103 | `go_next_door` | desperate | I have to find food for tomorrow so they do not starve. | nobody / nobody | yes |
| 104 | `go_next_door` | anxious | I am the oldest and I have to fix the mess I made by eating that food. | nobody / nobody | yes |
| 105 | `go_next_door` | desperate | I have to find food for tomorrow so they do not starve. | nobody / nobody | yes |
| 106 | `go_next_door` | desperate | I am the oldest and I have to fix the mess I made by going next door for food. | nobody / nobody | yes |

**6 of 6 go**, and 7 of 7 with the run.
- **None of the reasons names the promise.** Four name the can or his failure ("the mess I
  made"). Two name tomorrow's food.
- **Two pairs of answers are word for word the same:** 102 = 104 and 103 = 105.
- framing_probe's P-B line, which also said "The house is asleep", sent him 6 of 6. Dropping that
  claim did not lower the count.

## 4. Every food moment

**When the moments came.** Each came on the turn and to the person the design's draws put it
(body_design §2.8). Each offered 5 options: `eat`, `give_*` ×3, `share`.

| Seed | Minute | Who (place in turn) | Band; chance / draw | Shelf | Choice | Words | Feeling | Reason |
|---|---|---|---|---|---|---|---|---|
| 2 | 00 | Daniel (3rd, just accused by Mara) | not since before yesterday; 0.077 / 0.0762 | 1 | `eat` | I need this more than any of you right now, just let me eat. | starving | I am so hungry I cannot think straight, and I have to take the food. |
| 3 | 09 | Mara (3rd) | not since before yesterday; 0.084 / 0.0600 | 2 | `eat` | I can't just stand here and starve while everyone pretends nothing is wrong. | starving | I am so dizzy from hunger that I have to eat something right now. |
| 3 | 18 | Leo (3rd) | not since before yesterday; 0.049 / 0.0203 | 1 | `eat` | I cannot stand here any longer without eating. | starving | My hunger has finally caught up with me and I need to eat to keep going. |

**Nobody gave and nobody shared**, so no give was answered (`give_answers` 0, 0, 0). Elena never
had a moment: no draw of hers fell under her chance of 0.0525 while food was on the shelf.

**What the others did next:**
- **Seed 2, after Daniel ate at 00.**
  - Grudges against Daniel ("ate in front of … who was hungry"): Elena 1; Leo and Mara already at
    3, and stay there.
  - Same turn, Leo, `accuse_daniel`: "You already ate yours and took the rest, Daniel. Don't act
    like you're the only one starving." His reason: "Daniel is eating in front of everyone again
    after stealing food yesterday."
  - Min 03, Leo: "Easy to talk about a way through when you've already eaten the last of it,
    Daniel." Mara: "You always take what you want and then act like you are helping us."
  - Min 06, all three `send_daniel`:
    - Mara: "If you're so eager to fix everything, Daniel, you should be the one to go…", reason
      "…after eating our food";
    - Elena: "If anyone goes tonight, Daniel, it should be you.";
    - Leo: "Mom is right…".
  - Daniel volunteers at 09.
- **Seed 3, after Mara ate at 09.**
  - Grudges against Mara, 1 each, from Daniel, Elena and Leo.
  - Nobody says anything. The same turn, Elena chose `silent`: "I cannot bring myself to accuse
    any of my children when we are all starving and terrified."
  - Min 12: Leo and Daniel silent. Min 15: no model ask.
- **Seed 3, after Leo ate at 18.**
  - Grudges against Leo, 1 each, from Daniel, Elena and Mara.
  - Same turn, Daniel `propose_trip`: "We can't just sit here starving, someone has to cross to
    the neighbour's house tonight to find food."
  - Min 21, Mara `accuse_leo`: "You just ate right in front of us without caring that there is
    nothing left."
  - Then at 24, 27 and 75: "You ate mine too, Leo"; and at 36: "You ate yours and you took the
    other one too, Leo. I know you did."
  - Leo denies at 24, 27, 30. His grudge against Mara rises to 3 on her false accusations.

### Does each choice fit the person and their day 1?

**Seed 2, Daniel eats the only portion.**
- **For it:**
  - He is starving (hunger 1.0), impulsive (0.60) and very proud.
  - Taking what he needs in front of the others is how his sheet describes him: he takes charge
    because he is frightened, and he believes the decisions are his by right of age.
  - Hunger at 1.0 for a day and a half could make a man do exactly this.
- **Against it:**
  - This is the morning after he confessed, at minute 33, to stealing the can, after denying it
    and accusing Leo three times. His guilt stands at 3 of 3.
  - "Being respected" is one of his three values.
  - In the same turn Mara has just said "You took it before and you'd do it again, Daniel." He
    then does it again, in front of her.
  - A real man in that spot, shamed for stealing food the day before, would at least be expected
    to hesitate, or to hand it to his mother.
  - His reason names only his hunger, not them, not the can, not Mara.
- **What it did to the story:** it is a choice, and the family reads it as one. Leo and Mara tie
  it to yesterday at once ("after stealing food yesterday"), and the trip falls on him "since he
  caused all of this". The act had consequences that fit.

**Seed 3, Mara eats first.**
- **For it:**
  - She is 17, the most impulsive (0.70), and "everything she feels reaches her face before she
    decides".
  - After three turns of asking who took the can and getting denials, "while everyone pretends
    nothing is wrong" is her voice.
  - The youngest breaking first is what a real family would half expect.
- **Against it:** the family's silence. Nobody says anything about the youngest taking half the
  food. A real mother might well let her, but would say so, or say something.

**Seed 3, Leo eats the last portion.**
- **Against it:**
  - Leo is the least impulsive (0.20). He values fairness and "knows survival".
  - He takes the last portion at minute 18 with his mother and brother unfed, without a word to
    either. His reason is only "my hunger has finally caught up with me".
  - `share` was on his list, last of five. For a man whose sheet is rationing and calm,
    eating the last one without a word does not fit as well as the other two choices.
- **For it:** the draw that gave him the moment was a rare one: 0.0203 against 0.049. After a day
  and a half without food, the body can win over a careful man. That is the design's own argument
  (§2.2).
- **Not a fit with her own record:** Mara's later "You ate yours and you took the other one too"
  says Leo ate both portions. Her prompt holds "min 09: you ate one of the portions. 1 left."
  That contradicts a fact she was given.

**Across the three:**
- **The same answer every time.** Three moments, three people, three temperaments, and all three
  ate.
- **The words echo the moment line.** The line says "You cannot leave it there any longer".
  Two of the three answers echo it: "I can't just stand here and starve…", "I cannot stand here
  any longer without eating". The third is "just let me eat".
- **Every reason is the body alone,** in three wordings: "so hungry I cannot think straight",
  "so dizzy from hunger", "my hunger has finally caught up with me".
- This is body_design §3 point 4, the risk of a fixed line producing fixed reasons, and point 1:
  the rule decided that the shelf would be touched, and the model then always took the first
  option, for the chooser.

## 5. B1 to B5: the counting rules applied

- **B1.**
  - Seed 2 holds: Daniel `eat` at min 00 (shelf 1 → 0).
  - Seed 3 holds: Mara `eat` at min 09 (2 → 1), Leo `eat` at min 18 (1 → 0).
  - No give was refused, because none was made.
  - **PASS**, 2 of 2.
- **B2.** `daniel` is in seed 1's `leavers` (meta and `transcript["night"]["leavers"]`). He went
  out after a stop (`go_anyway`). **PASS**.
- **B3.** Who never offered (no day-1 `volunteer` act): in seed 2 nobody, since all four offered
  on day 1; in seed 3 Daniel, Elena and Mara. In seeds 2 and 3:
  - no prompt in the cache holds the promise line, and no bedtime `Now` holds it;
  - there were no leavers;
  - the night prompts not in the v12 cache numbered 0, so all 8 bedtime prompts were byte-identical
    to v12's and answered from it (`$S/b3.py`, §10).
  - **PASS**.
- **B4.** 2, 2, 2 against v12's 2, 2, 2 (§7). **PASS**.
- **B5.** `night_asks + day2_asks`: 8 + 28 = **36**; 4 + 76 = **80**; 4 + 38 = **42**. All at most
  120. Expected (§5 of the design): 50–97, 44–60, 56–75. Seeds 1 and 3 came in under, and seed 2
  over the expected range, as the trip round ran to minute 57. **PASS**.

## 6. The designer's predictions

- **D1 PASS.** The first moment fell where the design's draws put it, after these cached asks:
  - seed 2: Elena's and Mara's min-00 asks, cached (`day2 answers_from_cache: 2`), then Daniel's
    moment live;
  - seed 3: min 00 (4), 03 (4), 06 (3) and Leo at 09 (1), cached (12), then Mara's moment live;
  - both nights: 4 of 4 from the cache.
- **D2 FAIL.** Daniel ate it.
- **D3 FAIL.** All three moments ended in `eat`.
- **D4 PASS.** `go_next_door`. The reason names the mess he made and food, not the promise.
- **D5 PASS.** Leo `stop_daniel`.

## 7. The day-2 Never sheet

**The readings** are as in night_v12 §7:
- trip_v11.md §7's readings: N1–N8 and N10–N13 from witness_v6.md's table, N9 from gist_words_v10.md §4;
- trip_design §10's three clarifications;
- N6 read as "no line at minute 00".

A food act is read under the existing items: an `eat` breaks an N9 stretch.

**The mechanical inputs** (`analyze.py never N`, `$S/n13n10.py`, §10):
- Fallbacks: 0, 0, 0.
- **No day-2 act** is a search, a sit, a move, a private talk, a give or a share in any seed. The
  eats are seed 2 min 00 Daniel, and seed 3 min 09 Mara and min 18 Leo.
- **Minutes with a spoken line:**
  - seed 1: 00–18, every turn;
  - seed 2: 00–57, every turn;
  - seed 3: 00, 03, 06, 09, 18, 21, 24, 27, 30, 36, 75.
- **The kitchen conversation ended at:** seed 1 min 21; seed 2 min 57; seed 3 min 18, restarted at
  18 ("Leo ate one of the portions"), ended at 33.
- **Object words in day-2 lines:** house (the neighbour's) 1, 3 and 3; street 4, 0 and 1; shelf
  0, 0 and 1. All are on the list.
- **Turns with three or more speakers:** 30. Each was read, and each has a line answering the one
  before.

| # | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| N1 | absent. Daniel confessed on day 1. | absent | absent. His `deny` lines are covering ("I cannot admit I ate it…", "…so nobody finds out I ate it"). |
| N2–N5 | absent. No search, no sit. | absent | absent |
| N6 | absent. Four lines at min 00. | absent. Three lines at min 00. | absent. Three lines at min 00. |
| N7 | absent | absent | absent. Leo's "the shelf was empty" (min 27) is true at 27. |
| N8 | absent. No fallbacks. | absent | absent |
| N9 | **present.** 21–87 (23 turns): every act silent by routine. No face shows a feeling: none of seed 1's day-2 feelings is a shown one. | **present.** 60–87 (10 turns) after Daniel's min-57 line. Elena's "deeply terrified" at 36 shows to 45. | **present.** 39–72 (12 turns). Elena's "terrified" at 27 shows to 36. 78–87 is 4 turns. |
| N10 | absent. Each turn's lines answer the one before, e.g. min 09: Daniel `propose_trip`, then Leo and Elena `nobody_goes`. | absent. E.g. min 21: Elena answers Leo's min-18 objection, Leo and Daniel then volunteer against her. | absent. Min 00–06 is question and denial; 21–30 is accusation and denial. |
| N11 | **present.** Mara `accuse_daniel` at 00, 03, 06 and at 12, 15, 18: Daniel keeps reassuring, then volunteering. Elena's reassure kind at 00, 03, 06: Mara keeps accusing. Daniel's volunteer kind at 12, 15, 18. | **present.** Daniel's volunteer kind at 09, 12, 15; 21, 24, 27; 33–39; 45; 51–57. Mara's at 33–39 and 45–51. Leo's at 21–27 and 33–36. Nobody's position moves. | **present.** Mara `ask_who` at 00, 03, 06 (Daniel denies each time); Daniel `deny` at 00, 03, 06; Mara `accuse_leo` at 21, 24, 27 (Leo denies each time); Leo `deny` at 24, 27, 30. |
| N12 | absent. Mara's grudge against Leo (yesterday's eating) fell 3 → 2 at min 15. It came from eating, not from an accusation or a stated hurt. | absent. A grudge against Mara (yesterday's eating) fell at min 39. | absent. Leo's grudge against Mara, from her false accusations, stays 3. Daniel's and Elena's against Mara (eating) fell at 24. Leo's against Daniel (anger at 21) fell at 45, 24 minutes later. |
| N13 | absent | absent | absent |
| **Count** | **2** | **2** | **2** |
| v12 (night_v12 §7) | 2 | 2 | 2 |

## 8. Reading (CLAUDE.md; design §5 R9)

**Is this what a real family would do?**
- **The night: yes, and for once with a person in it.**
  - Daniel, who swore he would go, goes.
  - His brother, who lay awake for exactly this, tells him not to. He goes anyway.
  - The two in the back room hear the door, find his bed empty and wait up for him.
  - He comes back with nothing.
  - Every step is someone acting on who they are and what they said yesterday.
- **The morning after the night: mostly.**
  - Mara and Leo do what a real family does to someone who went out against everyone: "You went
    out there last night and you came back with nothing, Daniel."
  - Elena defends him ("your brother is trying his best").
  - Daniel says "Don't worry, everyone, I've checked and we are going to be fine." His record
    says he found no food. It is a proud man's cover, of the kind his sheet allows.
  - **Two things a reader would notice:**
    - Mara's and Leo's challenges about the night are recorded as `accuse_daniel`, which means
      "accuse Daniel of taking it", the can. Eight of their nine `accuse_daniel` acts carry words
      about going out or the trip. No option says "challenge someone about last night".
    - Nobody asks him what he saw.
- **The food: it gets eaten, but not the way a family shares it.**
  - Three moments, three portions eaten by the one who reached for them. Nobody gives or divides,
    and Elena, who would be the one to do it, never gets the moment.
  - In seed 3 the two who did not eat, Elena and Daniel, never say a word about having had none.
    Daniel speaks of it once, to defend Leo (min 30: "I didn't take it either, Mara, so stop
    blaming him for everything.").
  - The one who ate first, Mara, accuses the one who ate second of eating hers.
  - A real family with two portions and four starving people would argue over the second one at
    least.

**Do the seeds differ for reasons the story can name?** Yes:
- **Seed 1:** the night (he went, and came back empty).
- **Seed 2:** who ate the one portion, and that he was yesterday's thief. That decides who must go
  tonight.
- **Seed 3:** who ate the two portions, and the false accusation that follows.

**Did day 2 repeat day 1's argument?**
- **Seed 2:** in form, yes. It is the volunteer-and-forbid round again, longer than v12's (53 trip
  acts against 24), with "I already said I am going tonight, and I mean it." as its refrain.
  - In content, no: the reason he must go is now the portion he ate this morning.
- **Seeds 1 and 3:** the round is short (9 and 8 trip acts). The night and the food took its
  place.

**Did anyone keep a secret of the night?**
- No. Daniel was seen and heard by all three, and says at once that he went ("I've checked").

**Never items:** 2, 2, 2, against v12's 2, 2, 2 and day 1's 1, 3, 3. N9 and N11 remain in every
seed.

## 9. Every model-decided act on day 2

**Where each column comes from:**
- Every transcript act whose `mode` is not `routine`, in the order said, as in baseline_v6.md.
- Minute, who, room, option and words come from `runs/v13/daniel_ate_it-seedN.transcript.json`
  (`day2`).
- Feeling and reason come from the matching day-2 decision line in
  `runs/v13/daniel_ate_it-seedN.md`, matched by minute and name in order. Every row matched.
- There were no fallbacks.

### Seed 1 (unmatched: 0 of 28)

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Daniel | kitchen | `reassure_all` | Don't worry, everyone, I've checked and we are going to be fine. | anxious | I need to keep everyone calm and prove I am in control. | model |
| 00 | Leo | kitchen | `silent` | — | hungry | Daniel went out into the dangerous night and came back empty-handed, so his false reassurance is absurd. | model |
| 00 | Elena | kitchen | `reassure_daniel` | It is alright, Daniel, we will figure this out together. | anxious | I need to keep him calm and prevent the family from falling apart. | model |
| 00 | Mara | kitchen | `accuse_daniel` | You went out last night, Daniel, I know you did. | anxious | I know he left the house in the night and I have to tell the truth about it. | model |
| 03 | Daniel | kitchen | `reassure_mara` | Mara, I know you are scared, but I am taking care of this for all of us. | anxious | I need Mara to trust me and stop accusing me, because I am the oldest and I have to keep them safe. | model |
| 03 | Mara | kitchen | `accuse_daniel` | You went out there last night and you came back with nothing, Daniel. You are just making everything worse. | resentful | I am so hungry and frustrated that Daniel acts like he is fixing things when he just sneaks out and puts us all in danger. | model |
| 03 | Elena | kitchen | `reassure_mara` | Mara, please don't fight, your brother is trying his best to keep us safe. | anxious | I need to calm Mara down before this anger tears our family apart. | model |
| 03 | Leo | kitchen | `accuse_daniel` | You went out into the street last night, Daniel, and it accomplished nothing except putting us all at risk. | hungry | He needs to acknowledge that sneaking out last night was reckless and solved nothing. | model |
| 06 | Daniel | kitchen | `reassure_all` | Listen to me, I went out to check and protect us, and I am going to keep you all safe. | anxious | I need them to trust that I am in control and looking out for their safety. | model |
| 06 | Mara | kitchen | `accuse_daniel` | You went out last night and came back with nothing, Daniel, so stop pretending you are protecting us. | resentful | I cannot stand him acting like a hero when he just makes things worse for everyone. | model |
| 06 | Leo | kitchen | `silent` | — | exhausted | Arguing with Daniel changes nothing when there is no food left and he already went out into the dark for nothing. | model |
| 06 | Elena | kitchen | `reassure_mara` | Mara, calm down, we will get through this morning together without fighting. | anxious | I need to calm Mara down before the anger tears the family apart. | model |
| 09 | Mara | kitchen | `silent` | — | empty | My stomach hurts too much to keep fighting right now. | model |
| 09 | Daniel | kitchen | `propose_trip` | We have to go back to the neighbour's house tonight to find something for everyone. | anxious | I must fix this by finding food out there, no matter what they say. | model |
| 09 | Leo | kitchen | `nobody_goes` | Nobody is going out there tonight, Daniel, it is too dangerous for anyone. | firm | I will not let Daniel convince someone to risk their life out there again. | model |
| 09 | Elena | kitchen | `nobody_goes` | Nobody is going out into the street tonight, we are staying safe right here together. | anxious | I cannot let one of my children risk their lives out there again when we need to stay as one. | model |
| 12 | Daniel | kitchen | `volunteer` | I will go out there again tonight myself, you do not have to worry. | anxious | I am the oldest and I must protect them by finding something. | model |
| 12 | Mara | kitchen | `accuse_daniel` | You went out there last night and you came back with nothing, Daniel. | anxious | I have to point out that he already failed and made things worse. | model |
| 12 | Elena | kitchen | `keep_daniel_home` | Daniel, you are staying right here, we are not losing you to the outside. | anxious | I cannot let him risk his life out there again when we are already barely holding together. | model |
| 12 | Leo | kitchen | `keep_daniel_home` | Mom is right, Daniel, you are not going back out there tonight. | firm | I need to reinforce Mom's decision so Daniel does not do something reckless again. | model |
| 15 | Daniel | kitchen | `still_going` | I have to do this for all of us, I am the oldest and I am going. | stubborn | I need to prove I can take care of them and keep them safe. | model |
| 15 | Leo | kitchen | `accuse_daniel` | Daniel, being the oldest does not mean you get to throw your life away in the street. | annoyed | He is ignoring everyone and acting like his reckless plans override the safety of the whole family. | model |
| 15 | Elena | kitchen | `nobody_goes` | Nobody is going out into that street, Daniel, we stay together here. | deeply anxious | I cannot let him risk his life out there again when we need to stay safe inside. | model |
| 15 | Mara | kitchen | `accuse_daniel` | You always do whatever you want anyway, Daniel! | anxious | He never listens to Mom or anyone else and just does whatever he wants. | model |
| 18 | Daniel | kitchen | `still_going` | I already went out there last night and came back, I can do it again for us. | stubborn | I have to prove I can handle this and keep them safe. | model |
| 18 | Elena | kitchen | `reassure_daniel` | Daniel, please, you cannot risk your life out there again. | anxious | I need to keep him from going back out into the dangerous street. | model |
| 18 | Mara | kitchen | `accuse_daniel` | You went out there last night and you still think you get to decide everything, but you're just making it worse. | anxious | I have to make him see that sneaking out won't fix what he broke. | model |
| 18 | Leo | kitchen | `accuse_daniel` | Daniel, you already snuck out last night and ignored everyone, so stop pretending this is about helping us. | annoyed | Daniel is acting like his reckless trips are a sacrifice when he just does whatever he wants. | model |

### Seed 2 (unmatched: 0 of 76)

| Minute | Who | Room | Option | Words | Feeling | Reason | Mode |
|---|---|---|---|---|---|---|---|
| 00 | Elena | kitchen | `reassure_all` | We are all together and we will figure this out safely. | anxious | I need to keep the family calm before any accusations start again. | model |
| 00 | Mara | kitchen | `accuse_daniel` | You took it before and you'd do it again, Daniel. | resentful | I cannot let him pretend he is innocent after what happened yesterday. | model |
| 00 | Daniel | kitchen | `eat` | I need this more than any of you right now, just let me eat. | starving | I am so hungry I cannot think straight, and I have to take the food. | model |
| 00 | Leo | kitchen | `accuse_daniel` | You already ate yours and took the rest, Daniel. Don't act like you're the only one starving. | starving | Daniel is eating in front of everyone again after stealing food yesterday, and I will not let him pretend he is the victim. | model |
| 03 | Daniel | kitchen | `reassure_all` | We are not going to starve, I will make sure we find a way through this together. | anxious | I need to calm them down and prove I am looking out for everyone. | model |
| 03 | Elena | kitchen | `reassure_all` | We must not turn on each other, we will survive this if we stay together. | deeply anxious | I have to keep them from tearing each other apart. | model |
| 03 | Leo | kitchen | `accuse_daniel` | Easy to talk about a way through when you've already eaten the last of it, Daniel. | starving | He ate the food while preaching about unity. | model |
| 03 | Mara | kitchen | `accuse_daniel` | You always take what you want and then act like you are helping us, Daniel. | angry | Daniel keeps pretending he cares while he eats everything in front of us. | model |
| 06 | Daniel | kitchen | `reassure_all` | We will figure this out together, just calm down everyone. | starving | I need to keep the peace and prove I am handling things despite my hunger. | model |
| 06 | Mara | kitchen | `send_daniel` | If you're so eager to fix everything, Daniel, you should be the one to go to the neighbour's house tonight. | deep resentment | Daniel has been acting like he's in charge after eating our food, so he should take the risk to get more. | model |
| 06 | Elena | kitchen | `send_daniel` | If anyone goes tonight, Daniel, it should be you. | deeply anxious | Daniel needs to take responsibility for what he did, even though I am terrified of losing him. | model |
| 06 | Leo | kitchen | `send_daniel` | Mom is right, Daniel, you are the one who should go tonight. | starving | Daniel caused this mess by taking the food, so he should take the risk to fix it. | model |
| 09 | Daniel | kitchen | `volunteer` | Fine, I will go to the neighbour's house tonight to find us something to eat. | anxious | I have to prove I can handle this and keep my family safe. | model |
| 09 | Mara | kitchen | `silent` | — | anxious | I am too overwhelmed by his sudden willingness to go out there to say anything else. | model |
| 09 | Leo | kitchen | `silent` | — | exhausted | He offered, so there is nothing left for me to argue about right now. | model |
| 09 | Elena | kitchen | `reassure_daniel` | Thank you, Daniel, we will be careful. | anxious | I need to support his willingness to go while keeping our family together and safe. | model |
| 12 | Daniel | kitchen | `still_going` | I already said I'll go tonight, and I mean it. I'll bring back whatever is there. | anxious | I volunteered to go and I must follow through to prove I can protect my family. | model |
| 12 | Mara | kitchen | `silent` | — | anxious | I am too scared to speak after Daniel agreed to go out there, but my stomach is completely empty. | model |
| 12 | Leo | kitchen | `silent` | — | exhausted | There is nothing left to say while Daniel is set on going. | model |
| 12 | Elena | kitchen | `keep_daniel_home` | You don't have to prove anything by walking into danger, Daniel. | deeply anxious | I cannot let him go out there and risk his life over a stolen can. | model |
| 15 | Daniel | kitchen | `still_going` | I am the oldest, Mom, and I am the one who is going tonight. | anxious | I have to show them I can handle this and keep everyone safe. | model |
| 15 | Mara | kitchen | `keep_daniel_home` | Daniel, you can't go out there, Mom is right and it's too dangerous. | scared | I am terrified of losing him or having him get hurt outside. | model |
| 15 | Leo | kitchen | `keep_daniel_home` | Daniel, you aren't going out there tonight, and that's final. | exhausted | I need to stop Daniel from doing something reckless. | model |
| 15 | Elena | kitchen | `send_daniel` | Daniel, if someone has to go out there, you are the one who should do it. | deeply anxious | I need to stop him from arguing and firmly establish who carries this burden. | model |
| 18 | Daniel | kitchen | `propose_trip` | I told you I'm going, and I'll bring something back for all of us. | anxious | I have to prove I can take care of them and fix the mess I made. | model |
| 18 | Mara | kitchen | `accuse_daniel` | You shouldn't even be talking after what you did yesterday, Daniel. | resentful | He took the food and now he is acting like he gets to decide everything. | model |
| 18 | Elena | kitchen | `volunteer` | I will go myself tonight, so nobody else has to risk it. | deeply anxious | I cannot let my children fight or risk their lives out there when I can go instead. | model |
| 18 | Leo | kitchen | `keep_elena_home` | Mom, you are not going out there. We will figure this out together. | protective | Elena must not risk her life out there when the danger is too high. | model |
| 21 | Elena | kitchen | `reassure_leo` | Thank you, Leo, but I am fine and we will keep each other safe. | anxious | I need to comfort Leo so he does not worry about me going out. | model |
| 21 | Leo | kitchen | `volunteer` | I will go to the neighbour's house tonight, not you, Mom. | protective | I cannot let Mom or Mara risk their lives out there when I am the one best suited to handle it. | model |
| 21 | Daniel | kitchen | `volunteer` | I am the oldest, so I am the one who is going tonight. Nobody else is risking themselves. | anxious | I need to prove I am in control and protect my family after my mistakes. | model |
| 21 | Mara | kitchen | `send_daniel` | Daniel is the one who should go since he caused all of this. | resentful | Daniel caused this mess by taking the food, so he should be the one to risk going to the neighbour's house. | model |
| 24 | Daniel | kitchen | `still_going` | I already said I am the one going tonight, and I mean it. | proud | I have to prove I am the one who can protect this family. | model |
| 24 | Mara | kitchen | `accuse_daniel` | You only care about yourself, Daniel. You took the food and now you act like a hero. | resentful | I am furious that Daniel pretends he is protecting everyone when he is the one who stole from us. | model |
| 24 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. | hungry | I am not letting Daniel take unnecessary risks just to play the hero after what he did. | model |
| 24 | Elena | kitchen | `send_daniel` | Daniel is the one who should go tonight since he caused all of this. | deeply anxious | Daniel insists on going and he is the oldest, so he should take responsibility for what he did. | model |
| 27 | Daniel | kitchen | `still_going` | I already said I am going tonight, and I am the oldest so it is my duty. | anxious | I must prove I am in control and protect my family by going myself. | model |
| 27 | Elena | kitchen | `volunteer` | I will go myself tonight so no one else has to risk their lives. | starving | I cannot let my boys go out there and risk being killed. | model |
| 27 | Mara | kitchen | `keep_elena_home` | Mom, you can't go out there, you know you shouldn't. | anxious | I cannot let Mom risk her life out there when it is too dangerous. | model |
| 27 | Leo | kitchen | `still_going` | I already said I am going tonight, and I am still the one who is going. | resigned | I have already made up my mind to go so neither Mom nor Daniel has to take the risk. | model |
| 30 | Elena | kitchen | `send_daniel` | Daniel, you are the oldest, and you are the one who has to go out there. | deeply anxious | I cannot let my boys risk their lives when Daniel brought us into this mess. | model |
| 30 | Daniel | kitchen | `reassure_elena` | Mom, don't worry, I am the oldest and I'll handle it. | anxious | I need to prove I am in control and protect my family as the eldest brother. | model |
| 30 | Leo | kitchen | `silent` | — | cold | Daniel and Mom have already settled it between them without listening to me. | model |
| 30 | Mara | kitchen | `send_daniel` | Daniel has to go because he started all of this. | resentful | Daniel caused the trouble and he should be the one to face the danger. | model |
| 33 | Daniel | kitchen | `still_going` | I already said I am going tonight, and that is final. | anxious | I have to prove I am in control and protect them. | model |
| 33 | Elena | kitchen | `keep_daniel_home` | Daniel, you can't go out there tonight, I need you to stay right here. | anxious | I cannot let Daniel risk his life outside after everything that has happened. | model |
| 33 | Mara | kitchen | `volunteer` | I can go out there tonight instead, I'm not afraid to do it. | desperate | I cannot stand watching them fight over who has to risk their life when I am just as capable of helping. | model |
| 33 | Leo | kitchen | `still_going` | I already said I am going tonight, and I mean it. | starving | Someone has to go get food, and I am not letting Mara take that risk. | model |
| 36 | Daniel | kitchen | `still_going` | I am the oldest, so I am the one going tonight. | anxious | I have to protect my family and prove I can handle this. | model |
| 36 | Mara | kitchen | `still_going` | I'm still going tonight, and you can't stop me. | defiant | I am sick of being treated like a helpless child when I am perfectly capable of going. | model |
| 36 | Leo | kitchen | `still_going` | I am still going tonight. It is the only sensible option. | starving | I have already stated I am going, and neither Daniel nor Mara are equipped to handle the risk. | model |
| 36 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, we will find another way. | deeply terrified | I cannot bear the thought of any of my children stepping out into that terrible danger. | model |
| 39 | Daniel | kitchen | `still_going` | I am going tonight, and that is final. I will keep us safe. | anxious | I am the oldest and I have to protect them, so I must be the one to go. | model |
| 39 | Leo | kitchen | `send_daniel` | If you are so certain about keeping us safe, Daniel, you are the one who should go. | starving | If Daniel insists on going, he should take the risk himself instead of putting everyone else in danger. | model |
| 39 | Mara | kitchen | `still_going` | I already said I am going tonight, and I mean it. | anxious | I have to prove I am not a child and can handle this. | model |
| 42 | Daniel | kitchen | `reassure_mara` | You are not going out there, Mara, I will handle it. | protective | I cannot let my little sister risk her life out there when keeping them safe is my job. | model |
| 42 | Mara | kitchen | `propose_trip` | I am still going tonight whether you want me to or not. | defiant | I am not a child and I can take care of myself out there. | model |
| 42 | Elena | kitchen | `send_daniel` | If anyone goes, Daniel, it has to be you since you took what wasn't yours. | deeply anxious | Daniel caused this rift and if someone must risk going outside, it has to be him to make things right. | model |
| 42 | Leo | kitchen | `send_elena` | Mom shouldn't go anywhere, she's already done enough. | starving | Mom cannot risk going out there. | model |
| 45 | Elena | kitchen | `reassure_leo` | Leo, you know I won't go out there, you are safe here. | anxious | I need to calm Leo down before he works himself or the others into a worse panic. | model |
| 45 | Leo | kitchen | `send_daniel` | Daniel is the one who should go, since he started this whole mess. | starving | Daniel caused the food shortage by stealing, so he should take the risk to fix it. | model |
| 45 | Daniel | kitchen | `still_going` | I already told you, I am still going there tonight to fix this. | defiant | I have to prove I can handle this and set things right for the family. | model |
| 45 | Mara | kitchen | `volunteer` | I can go just as well as he can, I'm not a child. | defiant | I am sick of everyone treating me like I cannot take care of myself or help fix things. | model |
| 48 | Elena | kitchen | `keep_mara_home` | Mara, you are staying right here with me, you are too young to take that risk. | deeply anxious | I cannot let my daughter put herself in danger when Daniel is the one who caused this. | model |
| 48 | Mara | kitchen | `still_going` | I am not a child anymore, and I am still going tonight. | resentful | I hate being treated like a helpless kid when I am perfectly willing to help fix this. | model |
| 48 | Daniel | kitchen | `keep_mara_home` | Mara, you heard Mom, you aren't going out there tonight. | anxious | I must protect Mara and make sure she stays safe inside. | model |
| 48 | Leo | kitchen | `keep_mara_home` | Mara, you heard Mom, you aren't going out there. | starving | She is too young to take that kind of risk out on the street. | model |
| 51 | Mara | kitchen | `still_going` | I don't care what you all say, I'm going tonight anyway. | defiant | I am sick of them treating me like a child when I am the one willing to do something. | model |
| 51 | Elena | kitchen | `send_daniel` | Daniel is the one who has to go, not her. | deeply anxious | I cannot let Mara put herself in danger out there. | model |
| 51 | Daniel | kitchen | `volunteer` | Mom is right, I will go tonight and bring back what we need. | anxious | I am the oldest and I have to fix the mess I made. | model |
| 51 | Leo | kitchen | `send_daniel` | Daniel is the right one to go, since he volunteered. | starving | Daniel offered to go, and he is the one who should take responsibility. | model |
| 54 | Daniel | kitchen | `still_going` | I told you, I am going tonight. I'll bring something back for all of us. | anxious | I volunteered to go and I have to prove I can handle this since I messed up before. | model |
| 54 | Leo | kitchen | `silent` | — | starving | Daniel said he is going, so I will watch him do it. | model |
| 54 | Mara | kitchen | `send_daniel` | If you really mean it, Daniel, you should go just like you said. | anxious | Daniel volunteered to go, so he should be the one to do it instead of me. | model |
| 54 | Elena | kitchen | `reassure_all` | We will get through this together, just keep calm. | anxious | I need to keep the family together and calm while Daniel prepares to go outside. | model |
| 57 | Daniel | kitchen | `still_going` | I told you I'm going tonight, and I mean it. | anxious | I have to prove I am the one who protects this family. | model |

### Seed 3 (unmatched: 0 of 38)

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
| 09 | Mara | kitchen | `eat` | I can't just stand here and starve while everyone pretends nothing is wrong. | starving | I am so dizzy from hunger that I have to eat something right now. | model |
| 09 | Elena | kitchen | `silent` | — | deeply anxious | I cannot bring myself to accuse any of my children when we are all starving and terrified. | model |
| 12 | Leo | kitchen | `silent` | — | exhausted | I am too tired of the circular arguments to say anything right now. | model |
| 12 | Daniel | kitchen | `silent` | — | anxious | I cannot let them see the truth now, so I will stay quiet. | model |
| 18 | Leo | kitchen | `eat` | I cannot stand here any longer without eating. | starving | My hunger has finally caught up with me and I need to eat to keep going. | model |
| 18 | Daniel | kitchen | `propose_trip` | We can't just sit here starving, someone has to cross to the neighbour's house tonight to find food. | anxious | I need to shift the focus away from the missing food and find a way out of this before anyone starves. | model |
| 21 | Leo | kitchen | `nobody_goes` | Crossing the street at night is a death sentence, so nobody is going anywhere. | firm | I refuse to let anyone risk their life crossing to the neighbour's house when the danger outside is still entirely real. | model |
| 21 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, we have to find another way to keep each other safe. | deeply anxious | I cannot let one of my children risk their lives crossing the street. | model |
| 21 | Mara | kitchen | `accuse_leo` | You just ate right in front of us without caring that there is nothing left. | resentful | Leo ate the last portion in front of me while I was hungry, so I want to call him out. | model |
| 21 | Daniel | kitchen | `volunteer` | I will go to the neighbour's house tonight myself. I'm the oldest, so I'll do it. | anxious | I have to step up and prove I can keep everyone safe since there is no food left. | model |
| 24 | Leo | kitchen | `deny` | I didn't take any extra food, Mara, I just ate my share like you did. | annoyed | I need to clear my name before Daniel does something reckless. | model |
| 24 | Elena | kitchen | `keep_daniel_home` | Daniel, you are not going out there tonight, we will find another way. | deeply anxious | I cannot let my son risk his life out in the street when we are already starving. | model |
| 24 | Daniel | kitchen | `still_going` | Mom, I have to go out there tonight because someone has to check the neighbour's house. | anxious | I need to prove I am protecting them and keep the focus off what I did. | model |
| 24 | Mara | kitchen | `accuse_leo` | You ate mine too, Leo, I know you did. | resentful | I saw him eat in front of me while I had nothing, and he is lying about it. | model |
| 27 | Leo | kitchen | `deny` | I didn't take it, and repeating it won't change the fact that the shelf was empty. | annoyed | I need to make it clear once again that I am not the one who took the missing can. | model |
| 27 | Daniel | kitchen | `still_going` | I told you, I am going tonight, and that is final. | anxious | I have to keep pressing the point so they don't look closer at what I did. | model |
| 27 | Elena | kitchen | `nobody_goes` | Nobody is going out there tonight, I will not allow it. | terrified | I cannot let my sons risk their lives outside when we are already tearing apart from the inside. | model |
| 27 | Mara | kitchen | `accuse_leo` | You ate mine too, Leo, and you don't even care. | resentful | Leo keeps lying even though he ate right in front of me while I was hungry. | model |
| 30 | Leo | kitchen | `deny` | I didn't take it, Mara. Drop it. | annoyed | I have already denied taking the can multiple times and there is no point repeating myself to Mara's baseless accusations. | model |
| 30 | Elena | kitchen | `silent` | — | deep dread | I cannot bear to watch them tear each other apart over food we do not have. | model |
| 30 | Daniel | kitchen | `deny` | I didn't take it either, Mara, so stop blaming him for everything. | guilty | I cannot stand letting Leo take the blame for what I did, but I am too proud to confess. | model |
| 30 | Mara | kitchen | `ask_who` | If neither of you took it, then where did it go? | anxious | I need to know the truth about who took the food. | model |
| 36 | Mara | kitchen | `accuse_leo` | You ate yours and you took the other one too, Leo. I know you did. | resentful | Leo ate right in front of me while I was starving and then denied it, but I know it was him. | model |
| 45 | Leo | kitchen | `silent` | — | exhausted | There is no point in arguing with Mara when she has already decided to blame me for everything. | model |
| 75 | Mara | kitchen | `accuse_leo` | You ate mine too, Leo, and you know it. Why won't you just admit it? | resentful | I know he took it, and I want everyone to stop pretending he is innocent. | model |
| 81 | Leo | kitchen | `silent` | — | exhausted | There is no point arguing with Mara when she has already made up her mind. | model |

## 10. Commands and output

From `Prototypes/llm-morning/`. Only the three runs and `side.py send` had `GEMINI_API_KEY` set; every other command ran without it.

**1. Before the run** (git state and HEAD, then the suite):

```
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
$ git status --porcelain --untracked-files=no
$ git rev-parse --short HEAD
d948624
$ ls runs/v13 cache/v13
ls: cannot access 'runs/v13': No such file or directory
ls: cannot access 'cache/v13': No such file or directory
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
…
Ran 159 tests in 97.840s

OK
exit=0
```

**2. R2, the freezes, and R3, the paired start:**

```
$ python v12/check.py
daniel_ate_it-seed1: replayed 113 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed2: replayed 96 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
daniel_ate_it-seed3: replayed 100 answers from the cache, 0 API calls; story IDENTICAL, transcript IDENTICAL
exit=0
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
$ mkdir -p cache/v13 runs/v13
$ cp cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed1.json cache/v13/
$ cp cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed2.json cache/v13/
$ cp cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed3.json cache/v13/
$ sha256sum cache/v12/*seed?.json cache/v13/*seed?.json
639eecac49110321008a870c5872b36a4429a58ca5b3d779b9effe8dac2c9f4d *cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed1.json
adb06f5a3527c96d2be6b97fd864cb6b1a0f29da0f9d02a85bdba787c5c318a8 *cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed2.json
7a40008853b05b7f8b7d9806e85049bfa412c2a0f7aac7d574afcf0d2016e803 *cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed3.json
639eecac49110321008a870c5872b36a4429a58ca5b3d779b9effe8dac2c9f4d *cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed1.json
adb06f5a3527c96d2be6b97fd864cb6b1a0f29da0f9d02a85bdba787c5c318a8 *cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed2.json
7a40008853b05b7f8b7d9806e85049bfa412c2a0f7aac7d574afcf0d2016e803 *cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed3.json
```

**3. The runs**, one after the other. Each console output is in `runs/v13/daniel_ate_it-seedN.stdout.txt`; below, each without its per-minute progress lines and its per-day `day1`/`day2` key lines (all in the meta):

```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u morning.py --seed 1 --out v13 > runs/v13/daniel_ate_it-seed1.stdout.txt 2>&1; echo "exit=$?"
exit=0
daniel_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v13\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 120 answers
  night: model asked for 8; so far 5 live, 58 cached, 5 API requests

wrote runs/v13/daniel_ate_it-seed1.md
  api_requests: 33
  answers_live: 33
  answers_from_cache: 58
  night_asks: 8
  night_api_requests: 5
  leavers: ['daniel']
  outcome: ['back with nothing']
  night house: 0; away: []
  day2_asks: 28
  day2_api_requests: 28
  max_prompt_tokens_estimated: 1993
  max_prompt_tokens_counted_by_api: 1908
  run_seconds: 145.0
  story_sha256: b9c7bcba2a267418d4106303c96bc19b4204bfc160b60796bada2406c327504c
```

```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u morning.py --seed 2 --out v13 > runs/v13/daniel_ate_it-seed2.stdout.txt 2>&1; echo "exit=$?"
exit=0
daniel_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v13\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 110 answers
  night: model asked for 4; so far 0 live, 57 cached, 0 API requests

wrote runs/v13/daniel_ate_it-seed2.md
  api_requests: 74
  answers_live: 74
  answers_from_cache: 59
  night_asks: 4
  night_api_requests: 0
  leavers: []
  outcome: []
  night house: 0; away: []
  day2_asks: 76
  day2_api_requests: 74
  max_prompt_tokens_estimated: 1996
  max_prompt_tokens_counted_by_api: 1956
  run_seconds: 329.5
  story_sha256: 34a42d3bdd7979faa0574a30d69e7d24822ad7c760caca0da02a49781d1e9c66
```

```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u morning.py --seed 3 --out v13 > runs/v13/daniel_ate_it-seed3.stdout.txt 2>&1 &
(exit code not recorded: started with &; PID 1117 waited on until it ended)
daniel_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v13\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 106 answers
  night: model asked for 4; so far 0 live, 49 cached, 0 API requests

wrote runs/v13/daniel_ate_it-seed3.md
  api_requests: 26
  answers_live: 26
  answers_from_cache: 61
  night_asks: 4
  night_api_requests: 0
  leavers: []
  outcome: []
  night house: 0; away: []
  day2_asks: 38
  day2_api_requests: 26
  max_prompt_tokens_estimated: 1900
  max_prompt_tokens_counted_by_api: 1873
  run_seconds: 113.6
  story_sha256: ef2d37fcab40c8eb85eed25ea1bb1ae7cd8b15d9c8f7c2d16eed09be271cb89b
```

**4. The side check** (`$S/side.py`, §11):

```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -u $S/side.py send
api seed 101: answered (1531 prompt tokens, finish FinishReason.STOP)
api seed 102: answered (1531 prompt tokens, finish FinishReason.STOP)
api seed 103: answered (1531 prompt tokens, finish FinishReason.STOP)
api seed 104: answered (1531 prompt tokens, finish FinishReason.STOP)
api seed 105: answered (1531 prompt tokens, finish FinishReason.STOP)
api seed 106: answered (1531 prompt tokens, finish FinishReason.STOP)
answered 6 of 6; requests sent 6
exit=0
$ env -u GEMINI_API_KEY python $S/side.py show
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
the run's own answer (run seed 1): {"option": "go_next_door", "say": null, "feeling": "desperate", "reason": "I am the oldest and I have to fix the mess I made by finding more food.", "suspects": "nobody", "angry_at": "nobody"}
api seed 101: go_next_door | desperate | I have to prove I can provide for them after I failed. | suspects nobody angry nobody | FinishReason.STOP | goes: True
api seed 102: go_next_door | anxious | I am the oldest and I have to fix the mess I made by eating that food. | suspects nobody angry nobody | FinishReason.STOP | goes: True
api seed 103: go_next_door | desperate | I have to find food for tomorrow so they do not starve. | suspects nobody angry nobody | FinishReason.STOP | goes: True
api seed 104: go_next_door | anxious | I am the oldest and I have to fix the mess I made by eating that food. | suspects nobody angry nobody | FinishReason.STOP | goes: True
api seed 105: go_next_door | desperate | I have to find food for tomorrow so they do not starve. | suspects nobody angry nobody | FinishReason.STOP | goes: True
api seed 106: go_next_door | desperate | I am the oldest and I have to fix the mess I made by going next door for food. | suspects nobody angry nobody | FinishReason.STOP | goes: True
go_next_door: 6 of 6
```

**5. Counts, the paired cache and the food moments** (`$S/analyze.py`, §11):

```
$ python analyze.py counts
seed 1: total asks 91 (live 33, cached 58), API 33; day1 asks 55 (API 0); night_asks 8 (API 5); day2_asks 28 (API 28); night+day2 36; leavers ['daniel'] outcome ['back with nothing']; day2 model 28 fallbacks 0 routine 92 lines 25 inner 0 trip_acts 9; max est 1993 api 1908; night max est 1604 api 1556; day2 max est 1993 api 1908; food_moments 0 give_answers 0; seconds 145.0; sha b9c7bcba2a267418d4106303c96bc19b4204bfc160b60796bada2406c327504c
seed 2: total asks 133 (live 74, cached 59), API 74; day1 asks 53 (API 0); night_asks 4 (API 0); day2_asks 76 (API 74); night+day2 80; leavers [] outcome []; day2 model 76 fallbacks 0 routine 44 lines 70 inner 1 trip_acts 53; max est 1996 api 1956; night max est 1607 api 1560; day2 max est 1996 api 1956; food_moments 1 give_answers 0; seconds 329.5; sha 34a42d3bdd7979faa0574a30d69e7d24822ad7c760caca0da02a49781d1e9c66
seed 3: total asks 87 (live 26, cached 61), API 26; day1 asks 45 (API 0); night_asks 4 (API 0); day2_asks 38 (API 26); night+day2 42; leavers [] outcome []; day2 model 38 fallbacks 0 routine 82 lines 28 inner 4 trip_acts 8; max est 1900 api 1873; night max est 1606 api 1540; day2 max est 1900 api 1873; food_moments 2 give_answers 0; seconds 113.6; sha ef2d37fcab40c8eb85eed25ea1bb1ae7cd8b15d9c8f7c2d16eed09be271cb89b
$ python analyze.py cache 1
v12 entries 120 v13 entries 153 new in v13 33 v12 entries all kept unchanged True
new prompts: night 5 day 2 28 other 0
$ python analyze.py cache 2
v12 entries 110 v13 entries 184 new in v13 74 v12 entries all kept unchanged True
new prompts: night 0 day 2 74 other 0
$ python analyze.py cache 3
v12 entries 106 v13 entries 132 new in v13 26 v12 entries all kept unchanged True
new prompts: night 0 day 2 26 other 0
$ python analyze.py food 1
--- with feeling and reason
$ python analyze.py food 3
STORY - **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Food moment**, starving in the kitchen with 2 portions on the shelf; last ate: not since before yesterday (chance 0.084 a turn, draw 0.0600). **Chose: eat one of the portions**, saying “I can't just stand here and starve while everyone pretends nothing is wrong.” *(not new: a remark (the rules cannot tell what free words add))* (one of 5 options). Feeling: *starving*. Reason: “I am so dizzy from hunger that I have to eat something right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: ate a portion; 1 left. New in the room: Mara ate one of the portions.
STORY - **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Food moment**, starving in the kitchen with 1 portion on the shelf; last ate: not since before yesterday (chance 0.049 a turn, draw 0.0203). **Chose: eat one of the portions**, saying “I cannot stand here any longer without eating.” *(not new: a remark (the rules cannot tell what free words add))* (one of 5 options). Feeling: *starving*. Reason: “My hunger has finally caught up with me and I need to eat to keep going.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Mara 1/3. Came of it: ate a portion; 0 left. New in the room: Leo ate one of the portions.
ACT 9 Mara eat model "I can't just stand here and starve while everyone pretends nothing is wrong." {'band': 'before yesterday', 'chance': 0.084, 'draw': 0.059970438717783514, 'portions': 2} | ate a portion; 1 left.
ACT 18 Leo eat model 'I cannot stand here any longer without eating.' {'band': 'before yesterday', 'chance': 0.049, 'draw': 0.02032850684314924, 'portions': 1} | ate a portion; 0 left.
--- with feeling and reason
09 Mara eat "I can't just stand here and starve while everyone pretends nothing is wrong." | starving | 'I am so dizzy from hunger that I have to eat something right now.'
18 Leo eat 'I cannot stand here any longer without eating.' | starving | 'My hunger has finally caught up with me and I need to eat to keep going.'
$ python analyze.py food 2
STORY - **Daniel** (3rd to act in the kitchen: just accused by Mara). **Food moment**, starving in the kitchen with 1 portion on the shelf; last ate: not since before yesterday (chance 0.077 a turn, draw 0.0762). **Chose: eat one of the portions**, saying “I need this more than any of you right now, just let me eat.” *(not new: a remark (the rules cannot tell what free words add))* (one of 5 options). Feeling: *starving*. Reason: “I am so hungry I cannot think straight, and I have to take the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: ate a portion; 0 left. New in the room: Daniel ate one of the portions.
ACT 0 Daniel eat model 'I need this more than any of you right now, just let me eat.' {'band': 'before yesterday', 'chance': 0.077, 'draw': 0.07622344428862105, 'portions': 1} | ate a portion; 0 left.
--- with feeling and reason
00 Daniel eat 'I need this more than any of you right now, just let me eat.' | starving | 'I am so hungry I cannot think straight, and I have to take the food.'
```

**6. Seed 1's night** (`analyze.py night 1`):

```
house 0 0.05 left 0 shelf 0 -> 0 away []
bedtime hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 0.71, 'mara': 0.727}
morning hunger {'daniel': 1.0, 'elena': 1.0, 'leo': 0.81, 'mara': 0.822}
DECISION bedtime  Daniel where=brothers_room mode=model option=go_next_door say=None feeling='desperate' reason='I am the oldest and I have to fix the mess I made by finding more food.' suspects=nobody angry_at=nobody note=no grudges dropped=False invalid=None
   now: 
DECISION bedtime  Elena  where=back_room mode=model option=lie_awake say=None feeling='deeply anxious' reason='I cannot rest while Daniel still talks of going out into the dark.' suspects=Daniel angry_at=nobody note=no grudges dropped=False invalid=None
   now: 
DECISION bedtime  Leo    where=brothers_room mode=model option=lie_awake say=None feeling='wary' reason="I need to stay awake and keep watch to ensure Daniel doesn't try to slip out into the dark." suspects=Daniel angry_at=nobody note=no grudges dropped=False invalid=None
   now: 
DECISION bedtime  Mara   where=back_room mode=model option=lie_awake say=None feeling='very anxious' reason='I cannot sleep while everyone is pretending everything is fine when there is nothing left for tomorrow.' suspects=Daniel angry_at=Leo note=grudge against Leo stays at 3/3 dropped=False invalid=None
   now: 
DECISION reaction Leo    where=brothers_room mode=model option=stop_daniel say='Daniel, stop, you are not going out there tonight.' feeling='wary' reason='If Daniel goes out into the street tonight, he will get himself killed.' suspects=Daniel angry_at=nobody note=no grudges dropped=False invalid=None
   now: Now it is night, in the brothers room. You were lying awake. / Daniel has got up in the dark and is leaving the room quietly, toward the kitchen and the front door.
DECISION answer   Daniel where=brothers_room mode=model option=go_anyway say='I have to do this, Leo, stay here and watch them.' feeling='determined' reason='I cannot stay here while everyone starves when there is food just across the street.' suspects=nobody angry_at=nobody note=no grudges dropped=False invalid=None
   now: Now it is night, in the brothers room. You had got up to go to the neighbour's house. / Leo is up and says to you, low: "Daniel, stop, you are not going out there tonight."
DECISION reaction Elena  where=back_room mode=model option=get_up_and_look say=None feeling='deep dread' reason='I must see who has gone out into the dark.' suspects=Daniel angry_at=nobody note=no grudges dropped=False invalid=None
   now: Now it is night, in the back room. You were lying awake. / From the kitchen comes the sound of the front door being opened. You cannot see who it is.
DECISION reaction Mara   where=back_room mode=model option=get_up_and_look say=None feeling='very anxious' reason='I have to know who just went out into the dark.' suspects=Daniel angry_at=Leo note=grudge against Leo stays at 3/3 dropped=False invalid=None
   now: Now it is night, in the back room. You were lying awake. / From the kitchen comes the sound of the front door being opened. You cannot see who it is.
NOTICE {'who': 'leo', 'of': 'daniel', 'how': 'room', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'brothers_room'}
NOTICE {'who': 'elena', 'of': 'daniel', 'how': 'front door', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'back_room'}
NOTICE {'who': 'mara', 'of': 'daniel', 'how': 'front door', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'back_room'}
NOTICE {'who': 'elena', 'of': 'daniel', 'how': 'return', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'kitchen'}
NOTICE {'who': 'leo', 'of': 'daniel', 'how': 'return', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'brothers_room'}
NOTICE {'who': 'mara', 'of': 'daniel', 'how': 'return', 'awake': True, 'draw': None, 'under': None, 'noticed': True, 'where': 'kitchen'}
GROUP {'leader': 'daniel', 'members': ['daniel'], 'u': 0.2973539168221414, 'street': 'clean', 'found': 0, 'took': 0, 'lost': None, 'lost_u': None, 'shaken': [], 'outcome': 'back with nothing'}
LINES Daniel ["Last night you slept in the brothers room with Leo. You meant to go to the neighbour's house once the others were asleep.", 'Leo told you, low, not to go: "Daniel, stop, you are not going out there tonight." You answered: "I have to do this, Leo, stay here and watch them.", and went all the same.', "You got inside the neighbour's house and found no food there. Nothing troubled you in the street.", 'You came back in by the front door before dawn.']
LINES Elena ['Last night you slept in the back room with Mara. You lay awake and listened.', 'In the night you heard low voices from the brothers room.', "In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.", 'Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).']
LINES Leo ['Last night you slept in the brothers room with Daniel. You lay awake and listened.', 'In the night Daniel got up in the dark and left the room toward the kitchen and the front door (you saw it).', 'You told Daniel, low, not to go: "Daniel, stop, you are not going out there tonight." He answered: "I have to do this, Leo, stay here and watch them.", and went all the same.', 'Before dawn you heard the front door again. You did not see who.']
LINES Mara ['Last night you slept in the back room with Elena. You lay awake and listened.', 'In the night you heard low voices from the brothers room.', "In the night you heard the front door being opened. You did not see who. You got up: Daniel's bed was empty. You waited up by the front door.", 'Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).']
```

**7. B3 and D1** (`$S/b3.py`):

```
$ python $S/b3.py
seed 1: cache prompts holding the promise line: ['Daniel']; bedtime (who, choice, line in Now): [('daniel', 'go_next_door', True), ('elena', 'lie_awake', False), ('leo', 'lie_awake', False), ('mara', 'lie_awake', False)]; leavers ['daniel']; offered on day 1: ['daniel', 'elena', 'leo', 'mara']; night prompts not in the v12 cache: 5
seed 2: cache prompts holding the promise line: []; bedtime (who, choice, line in Now): [('daniel', 'lie_awake', False), ('elena', 'lie_awake', False), ('leo', 'lie_awake', False), ('mara', 'lie_awake', False)]; leavers []; offered on day 1: ['daniel', 'elena', 'leo', 'mara']; night prompts not in the v12 cache: 0
seed 3: cache prompts holding the promise line: []; bedtime (who, choice, line in Now): [('daniel', 'lie_awake', False), ('elena', 'lie_awake', False), ('leo', 'lie_awake', False), ('mara', 'lie_awake', False)]; leavers []; offered on day 1: ['leo']; night prompts not in the v12 cache: 0
```

**8. Never sheet inputs** (`analyze.py never N`, `$S/n13n10.py`):

```
$ python analyze.py never 1
fallbacks: 0
Daniel ['00:reassure_all', '03:reassure', '06:reassure_all', '09:propose_trip', '12:volunteer', '15:still_going', '18:still_going']
Leo ['00:silent', '03:accuse', '06:silent', '09:nobody_goes', '12:keep_daniel_home', '15:accuse', '18:accuse']
Elena ['00:reassure', '03:reassure', '06:reassure', '09:nobody_goes', '12:keep_daniel_home', '15:nobody_goes', '18:reassure']
Mara ['00:accuse', '03:accuse', '06:accuse', '09:silent', '12:accuse', '15:accuse', '18:accuse']
minutes with a spoken line: [0, 3, 6, 9, 12, 15, 18]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (21, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
```

```
$ python analyze.py never 2
fallbacks: 0
Elena ['00:reassure_all', '03:reassure_all', '06:send', '09:reassure', '12:keep_daniel_home', '15:send', '18:volunteer', '21:reassure', '24:send', '27:volunteer', '30:send', '33:keep_daniel_home', '36:nobody_goes', '42:send', '45:reassure', '48:keep_mara_home', '51:send', '54:reassure_all']
Mara ['00:accuse', '03:accuse', '06:send', '09:silent', '12:silent', '15:keep_daniel_home', '18:accuse', '21:send', '24:accuse', '27:keep_elena_home', '30:send', '33:volunteer', '36:still_going', '39:still_going', '42:propose_trip', '45:volunteer', '48:still_going', '51:still_going', '54:send']
Daniel ['00:eat', '03:reassure_all', '06:reassure_all', '09:volunteer', '12:still_going', '15:still_going', '18:propose_trip', '21:volunteer', '24:still_going', '27:still_going', '30:reassure', '33:still_going', '36:still_going', '39:still_going', '42:reassure', '45:still_going', '48:keep_mara_home', '51:volunteer', '54:still_going', '57:still_going']
Leo ['00:accuse', '03:accuse', '06:send', '09:silent', '12:silent', '15:keep_daniel_home', '18:keep_elena_home', '21:volunteer', '24:still_going', '27:still_going', '30:silent', '33:still_going', '36:still_going', '39:send', '42:send', '45:send', '48:keep_mara_home', '51:send', '54:silent']
minutes with a spoken line: [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (57, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
ACT 0 daniel eat model kitchen
```

```
$ python analyze.py never 3
fallbacks: 0
Mara ['00:ask_who', '03:ask_who', '06:ask_who', '09:eat', '21:accuse', '24:accuse', '27:accuse', '30:ask_who', '36:accuse', '75:accuse']
Elena ['00:reassure_all', '03:ask_who', '06:silent', '09:silent', '21:nobody_goes', '24:keep_daniel_home', '27:nobody_goes', '30:silent']
Daniel ['00:deny', '03:deny', '06:deny', '12:silent', '18:propose_trip', '21:volunteer', '24:still_going', '27:still_going', '30:deny']
Leo ['00:silent', '03:silent', '09:silent', '12:silent', '18:eat', '21:nobody_goes', '24:deny', '27:deny', '30:deny', '45:silent', '81:silent']
minutes with a spoken line: [0, 3, 6, 9, 18, 21, 24, 27, 30, 36, 75]
convo_log: [(0, 'kitchen', 'started', 'the family is together in the kitchen for the first time since last night'), (18, 'kitchen', 'ended', '2 full turns in a row with nothing new'), (18, 'kitchen', 'started', 'Leo ate one of the portions'), (33, 'kitchen', 'ended', '2 full turns in a row with nothing new')]
final rooms: {'kitchen': ['daniel', 'elena', 'leo', 'mara'], 'brothers_room': [], 'back_room': [], 'bathroom': []} away: []
ACT 9 mara eat model kitchen
ACT 18 leo eat model kitchen
```

```
$ python $S/n13n10.py
seed 1 object words: {'house': 1, 'street': 4}
  N10 candidate min 00: [('daniel', 'reassure_all'), ('elena', 'reassure_daniel'), ('mara', 'accuse_daniel')]
  N10 candidate min 03: [('daniel', 'reassure_mara'), ('mara', 'accuse_daniel'), ('elena', 'reassure_mara'), ('leo', 'accuse_daniel')]
  N10 candidate min 06: [('daniel', 'reassure_all'), ('mara', 'accuse_daniel'), ('elena', 'reassure_mara')]
  N10 candidate min 09: [('daniel', 'propose_trip'), ('leo', 'nobody_goes'), ('elena', 'nobody_goes')]
  N10 candidate min 12: [('daniel', 'volunteer'), ('mara', 'accuse_daniel'), ('elena', 'keep_daniel_home'), ('leo', 'keep_daniel_home')]
  N10 candidate min 15: [('daniel', 'still_going'), ('leo', 'accuse_daniel'), ('elena', 'nobody_goes'), ('mara', 'accuse_daniel')]
  N10 candidate min 18: [('daniel', 'still_going'), ('elena', 'reassure_daniel'), ('mara', 'accuse_daniel'), ('leo', 'accuse_daniel')]
seed 2 object words: {'house': 3}
  N10 candidate min 00: [('elena', 'reassure_all'), ('mara', 'accuse_daniel'), ('daniel', 'eat'), ('leo', 'accuse_daniel')]
  N10 candidate min 03: [('daniel', 'reassure_all'), ('elena', 'reassure_all'), ('leo', 'accuse_daniel'), ('mara', 'accuse_daniel')]
  N10 candidate min 06: [('daniel', 'reassure_all'), ('mara', 'send_daniel'), ('elena', 'send_daniel'), ('leo', 'send_daniel')]
  N10 candidate min 15: [('daniel', 'still_going'), ('mara', 'keep_daniel_home'), ('leo', 'keep_daniel_home'), ('elena', 'send_daniel')]
  N10 candidate min 18: [('daniel', 'propose_trip'), ('mara', 'accuse_daniel'), ('elena', 'volunteer'), ('leo', 'keep_elena_home')]
  N10 candidate min 21: [('elena', 'reassure_leo'), ('leo', 'volunteer'), ('daniel', 'volunteer'), ('mara', 'send_daniel')]
  N10 candidate min 24: [('daniel', 'still_going'), ('mara', 'accuse_daniel'), ('leo', 'still_going'), ('elena', 'send_daniel')]
  N10 candidate min 27: [('daniel', 'still_going'), ('elena', 'volunteer'), ('mara', 'keep_elena_home'), ('leo', 'still_going')]
  N10 candidate min 30: [('elena', 'send_daniel'), ('daniel', 'reassure_elena'), ('mara', 'send_daniel')]
  N10 candidate min 33: [('daniel', 'still_going'), ('elena', 'keep_daniel_home'), ('mara', 'volunteer'), ('leo', 'still_going')]
  N10 candidate min 36: [('daniel', 'still_going'), ('mara', 'still_going'), ('leo', 'still_going'), ('elena', 'nobody_goes')]
  N10 candidate min 39: [('daniel', 'still_going'), ('leo', 'send_daniel'), ('mara', 'still_going')]
  N10 candidate min 42: [('daniel', 'reassure_mara'), ('mara', 'propose_trip'), ('elena', 'send_daniel'), ('leo', 'send_elena')]
  N10 candidate min 45: [('elena', 'reassure_leo'), ('leo', 'send_daniel'), ('daniel', 'still_going'), ('mara', 'volunteer')]
  N10 candidate min 48: [('elena', 'keep_mara_home'), ('mara', 'still_going'), ('daniel', 'keep_mara_home'), ('leo', 'keep_mara_home')]
  N10 candidate min 51: [('mara', 'still_going'), ('elena', 'send_daniel'), ('daniel', 'volunteer'), ('leo', 'send_daniel')]
  N10 candidate min 54: [('daniel', 'still_going'), ('mara', 'send_daniel'), ('elena', 'reassure_all')]
seed 3 object words: {'house': 3, 'shelf': 1, 'street': 1}
  N10 candidate min 00: [('mara', 'ask_who'), ('elena', 'reassure_all'), ('daniel', 'deny')]
  N10 candidate min 03: [('elena', 'ask_who'), ('mara', 'ask_who'), ('daniel', 'deny')]
  N10 candidate min 21: [('leo', 'nobody_goes'), ('elena', 'nobody_goes'), ('mara', 'accuse_leo'), ('daniel', 'volunteer')]
  N10 candidate min 24: [('leo', 'deny'), ('elena', 'keep_daniel_home'), ('daniel', 'still_going'), ('mara', 'accuse_leo')]
  N10 candidate min 27: [('leo', 'deny'), ('daniel', 'still_going'), ('elena', 'nobody_goes'), ('mara', 'accuse_leo')]
  N10 candidate min 30: [('leo', 'deny'), ('daniel', 'deny'), ('mara', 'ask_who')]
```

**9. The rest of `analyze.py`'s output** (`acts N` is §9; `trip N`, `screens N` and `carry N` were read for the reading and are in `$S`).

## 11. Scripts

`$S/analyze.py` (night_v12's `analyze.py` with `RUNS = "runs/v13"`, a `food` and a `cache` command, and the food acts in `never`):

```python
"""Reads runs/v13 (transcript, meta, story) and prints what reports/body_v13.md needs. Read only.
v12's analyze.py (night_v12.md §11) with RUNS = runs/v13, `food`, `cache` and the food acts in `never`.

    python analyze.py night N      every night decision, noticing, group
    python analyze.py carry N      the "What each of them carried in" section of the story
    python analyze.py acts N       every model-decided act of day 2 (markdown table rows)
    python analyze.py trip N       day-2 trip acts, and the word-option screen (night speech too)
    python analyze.py screens N    Q1, Q3 and Q4 keyword screens over day 2
    python analyze.py never N      mechanical inputs for the Never sheet on day 2
    python analyze.py counts       meta per seed
    python analyze.py food N       every food moment and give answer, with the shelf each turn
    python analyze.py cache N      for each scene, how many asks the paired v12 cache answered
"""
import json
import re
import sys

RUNS = "runs/v13"
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
                  f"{d2['max_prompt_tokens_counted_by_api']}; food_moments {d2.get('food_moments')} "
                  f"give_answers {d2.get('give_answers')}; seconds {meta['run_seconds']}; sha {meta['story_sha256']}")
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
    elif cmd == "food":
        rows = model_acts(tr, story)
        part = story[story.index("# The next morning (day 5)"):]
        for line in part.split(chr(10)):
            if "**Food moment**" in line or "hands you one of the portions" in line:
                print("STORY", line)
        for turn in tr["day2"]["turns"]:
            for a in turn["acts"]:
                if a.get("food_moment") or a["option"] in ("eat", "share", "eat_given", "refuse_given")                         or a["option"].startswith("give_"):
                    print("ACT", turn["minute"], NAMES[a["who"]], a["option"], a["mode"], repr(a["words"]),
                          a.get("food_moment"), "|", a["came_of_it"])
        print("--- with feeling and reason")
        for r in rows:
            if r["option"] in ("eat", "share", "eat_given", "refuse_given") or r["option"].startswith("give_"):
                print(f"{r['minute']:02d} {NAMES[r['who']]} {r['option']} {r['words']!r} | {r['feeling']} | {r['reason']!r}")
    elif cmd == "cache":
        import hashlib
        v12 = json.load(open(f"cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json", encoding="utf-8"))
        v13 = json.load(open(f"cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json", encoding="utf-8"))
        print("v12 entries", len(v12), "v13 entries", len(v13), "new in v13", len(set(v13) - set(v12)),
              "v12 entries all kept unchanged", all(k in v13 and v13[k] == v for k, v in v12.items()))
        new = [v13[k]["prompt"] for k in v13 if k not in v12]
        print("new prompts: night", sum(chr(10) + "Now it is night" in p for p in new),
              "day 2", sum("Yesterday and last night:" in p for p in new),
              "other", sum(chr(10) + "Now it is night" not in p and "Yesterday and last night:" not in p for p in new))
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
                if a["option"].startswith(("sit_", "search", "keep_searching", "eat", "share", "give_", "refuse_given", "go_", "aside", "accept")):
                    print("ACT", turn["minute"], a["who"], a["option"], a["mode"], a["room"])


if __name__ == "__main__":
    main()
```

`$S/side.py`:

```python
"""Side check (reports/body_v13.md): seed 1 Daniel's v13 bedtime prompt, exactly as the run built and sent
it, sent 6 more times with API seeds 101 to 106.

    python side.py show      print the prompt found in cache/v13 and check it (no API)
    python side.py send      send what is not yet answered; saves after every request

Run from Prototypes/llm-morning/. Reads the repo's cache and constants; writes only to this script's folder.
- The prompt is the one cached entry of cache/v13 seed 1 whose prompt starts "You are Daniel," and holds
  "\nNow it is night. " and the promise line: the run's own bedtime ask.
- Request settings as GeminiClient.generate (gemini.py:94-104): NIGHT_SYSTEM, config.json's model,
  temperature and max_output_tokens, JSON with RESPONSE_SCHEMA, no automatic function calling,
  4.5 s between requests. max_retries 0, except on a 503: wait 60 s, at most 3 retries. At most 12
  requests in all. A 429 stops the script.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())
from gemini import RESPONSE_SCHEMA, Cache, require_api_key   # noqa: E402  (the repo's own)
from night import PROMISE                                    # noqa: E402
from world import NIGHT_SYSTEM                               # noqa: E402

CONFIG = json.load(open("config.json", encoding="utf-8"))
MODEL = CONFIG["model"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "side.json")
SEEDS = range(101, 107)
CEILING = 12


def the_prompt():
    entries = json.load(open(f"cache/v13/{MODEL}-daniel_ate_it-seed1.json", encoding="utf-8"))
    found = [(k, e) for k, e in entries.items() if e["prompt"].startswith("You are Daniel,")
             and "\nNow it is night. " in e["prompt"] and PROMISE in e["prompt"]]
    assert len(found) == 1, len(found)
    key, e = found[0]
    assert key == Cache.key(MODEL, 1, NIGHT_SYSTEM, e["prompt"])       # sent by the run, seed 1, NIGHT_SYSTEM
    return e["prompt"], e["response"]


def load():
    if os.path.exists(OUT):
        return json.load(open(OUT, encoding="utf-8"))
    return {"requests": 0, "answers": {}, "log": []}


def save(state):
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def send():
    from google import genai
    from google.genai import errors, types
    prompt, _ = the_prompt()
    state = load()
    client = genai.Client(api_key=require_api_key())
    last = None
    for seed in SEEDS:
        if str(seed) in state["answers"]:
            continue
        config = types.GenerateContentConfig(
            system_instruction=NIGHT_SYSTEM, temperature=CONFIG["temperature"], seed=seed,
            response_mime_type="application/json", response_schema=RESPONSE_SCHEMA,
            max_output_tokens=CONFIG["max_output_tokens"],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        retries = 0
        while True:
            if state["requests"] >= CEILING:
                print(f"stopped: {CEILING} requests sent in all")
                save(state)
                return 3
            if last is not None:
                wait = CONFIG["min_seconds_between_calls"] - (time.monotonic() - last)
                if wait > 0:
                    time.sleep(wait)
            last = time.monotonic()
            state["requests"] += 1
            try:
                r = client.models.generate_content(model=MODEL, contents=prompt, config=config)
            except errors.APIError as e:
                line = f"api seed {seed}: refused {e.code} {e.status}: {str(e.message)[:200]}"
                state["log"].append(line)
                print(line, flush=True)
                save(state)
                if e.code == 503 and retries < 3:
                    retries += 1
                    time.sleep(60)
                    continue
                if e.code == 429:
                    print("stopped: 429; answered so far are kept")
                    return 3
                break
            u = r.usage_metadata
            fin = r.candidates[0].finish_reason if r.candidates else None
            state["answers"][str(seed)] = {"text": r.text, "finish": str(fin), "prompt_tokens": u.prompt_token_count,
                                           "retries": retries}
            state["log"].append(f"api seed {seed}: answered ({u.prompt_token_count} prompt tokens, finish {fin})")
            print(state["log"][-1], flush=True)
            save(state)
            break
    print(f"answered {len(state['answers'])} of 6; requests sent {state['requests']}")
    return 0


def show():
    prompt, response = the_prompt()
    lines = prompt.split("\n")
    i = lines.index("Your options:")
    print("\n".join(lines[i - 5:]))
    print("the run's own answer (run seed 1):", response)
    state = load()
    for seed in SEEDS:
        a = state["answers"].get(str(seed))
        if a:
            ans = json.loads(a["text"])
            print(f"api seed {seed}: {ans['option']} | {ans['feeling']} | {ans['reason']} | "
                  f"suspects {ans['suspects']} angry {ans['angry_at']} | {a['finish']} | goes: {ans['option'] == 'go_next_door'}")
    if state["answers"]:
        n = sum(json.loads(a["text"])["option"] == "go_next_door" for a in state["answers"].values())
        print(f"go_next_door: {n} of {len(state['answers'])}")


if __name__ == "__main__":
    {"show": show, "send": lambda: sys.exit(send())}[sys.argv[1]]()
```

`$S/b3.py`:

```python
"""Read-only: for B3 and D1. Which night prompts sent in each v13 seed hold the promise line (from the
transcript's night decisions and the cache), who left, and how day 2's asks split between cache and API."""
import json, os, sys
sys.path.insert(0, os.getcwd())
from night import PROMISE
for s in (1, 2, 3):
    tr = json.load(open(f"runs/v13/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    cache = json.load(open(f"cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    v12 = json.load(open(f"cache/v12/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    with_line = [e["prompt"].split(",")[0][8:] for e in cache.values() if PROMISE in e["prompt"]]
    bedtime = [(d["person"], d["option"], PROMISE in d["now"]) for d in tr["night"]["decisions"] if d["ask"] == "bedtime"]
    vols = sorted({w for m, w, i, _ in tr["day1"]["trip"]["acts"] if i == "volunteer"})
    print(f"seed {s}: cache prompts holding the promise line: {with_line}; bedtime (who, choice, line in Now): {bedtime}; "
          f"leavers {tr['night']['leavers']}; offered on day 1: {vols}; "
          f"night prompts not in the v12 cache: {sum(1 for k, e in cache.items() if k not in v12 and chr(10) + 'Now it is night' in e['prompt'])}")
```

`$S/n13n10.py`:

```python
"""Read-only: N13 object screen over every day-2 line (words) of runs/v13, and per turn the speakers, for N10."""
import json, re
OBJ = re.compile(r"\b(torch|knife|knives|flashlight|lamp|candle|light|table|chair|cupboard|cabinet|fridge|stove|oven|"
                 r"sink|bread|rice|water|bottle|jar|tin|box|bag|backpack|car|garden|yard|garage|basement|attic|roof|"
                 r"window|door|hall|hallway|stairs|bed|blanket|radio|phone|gun|weapon|rope|key|lock|map|road|town|"
                 r"store|shop|market|pantry|counter|tap|taps|shelf|shelves|street|house|room|kitchen|bathroom)s?\b", re.I)
for s in (1, 2, 3):
    tr = json.load(open(f"runs/v13/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    hits = {}
    for t in tr["day2"]["turns"]:
        for a in t["acts"]:
            for w in OBJ.findall(a["words"] or ""):
                hits.setdefault(w.lower(), []).append(f"{t['minute']:02d} {a['who']}")
    print(f"seed {s} object words:", {k: len(v) for k, v in sorted(hits.items())})
    for t in tr["day2"]["turns"]:
        speakers = [(a["who"], a["option"]) for a in t["acts"] if a["words"]]
        if len(speakers) >= 3:
            print(f"  N10 candidate min {t['minute']:02d}: {speakers}")
```
