# Design: days that follow one another — the night mind, the chronicle, and coarse time (`daniel_ate_it`, v14)

Mode: design. No code was written or changed, and no API was called.
- Paths are relative to `Prototypes/llm-morning/`.
- Scratch scripts are in the session scratchpad (`$S` = `…/scratchpad/days`). They replay the frozen v13
  runs with v13's own code from `cache/v13`, in replay mode (no client). They write nothing in the repo.
  They are reproduced in §11 with their output.
- Read first, as the brief asked: `reports/night_design.md`, `reports/body_design.md`,
  `reports/food_confront_impl.md`, `reports/body_v13.md` §2, §4 and §8, `world.py`, `night.py`, `story.py`,
  `morning.py`, and the root `CLAUDE.md`.
  - **"North Star principles": NOT FOUND.** No file in the repository holds that phrase (§11, command 6).
  - So this design applies the principles `CLAUDE.md` does hold, under "Judging changes":
    - judge a change by what a real family would do;
    - a metric is a clue, never the goal;
    - argue against a mechanism before proposing it.

**Words used here.**
- **Day 1, 2, 3** are the played mornings: house days 4, 5 and 6. Day 1 is the v11 morning, replayed.
  Prompts never say "day 1". They say "yesterday", "two days ago", "last night" or "the night before last",
  computed for each line (§3.5).
- **Night 1** follows day 1, and **night 2** follows day 2. There is no night 3 in this version.
- **The night mind** is one model call per person at the end of a night (§2). **Mind 1** and **mind 2** are
  the night minds of nights 1 and 2.
- **A scene** is one of: day 1, gap 1, night 1, mind 1, day 2, gap 2, night 2, mind 2, day 3.
- **An ask** is one model decision, live or from the cache, as in every earlier design. A night-mind call is
  an ask.
- **The chronicle** is the code's record of what happened, facts only (§4).

**The step in one paragraph.**
- Day 1 replays from the v11 cache. Night 1 runs as in v13.
- At the end of each night, each person in the house gets one call. It receives what they did, saw and heard
  that day and night, as numbered records written by the code. It answers with 1 to 3 lasting memories, each
  citing record ids, plus a feeling and an intent for tomorrow.
- The code checks every memory. A memory is dropped if it cites a record the person was not shown, or if it
  states something as fact that the chronicle says is false.
- The next morning, each person carries three blocks:
  - **A**: yesterday's facts and last night's, written by the code, as the v13 carry-in does;
  - **B**: last night's memories, in their own words, with the intent and the feeling;
  - **C**: from earlier days, at most two standing matters and one line per person, chosen by a fixed code
    rule (§3.3).
- The three blocks share one bound, so prompts stop growing however many days pass.
- Day 2 runs, then gap 2 (code only), night 2, mind 2 and day 3.

**Three things to know before reading on.**
1. **What the bound does to the sizes.** The bound is 560 estimated tokens, shared by the three blocks.
   - The emulated day-3 prompts are at most 1.3–4.2% larger than day 2's, with B at its upper limit (§3.6).
   - Whatever the number of days, a morning prompt stays under about 2,420 estimated tokens. Today's largest
     is 1,996 (v13).
2. **The cost is the brief's main risk, not the night mind.**
   - The night minds cost 4 asks a night.
   - Days 2 and 3 are full played mornings. In v12 and v13 a day 2 asked between 28 and 76 times.
   - The expected total for nights plus days 2 and 3 is 70–202 asks per seed, typically about 96–134
     (§7.2). M6's limit is 140, so a seed whose day 2 or day 3 runs a long trip round (v13 seed 2: 76) can
     fail it.
   - Three seeds need about 210–606 live requests against the 500-a-day quota. The run plan spreads the
     seeds over days (§7.3).
3. **An existing wording bug becomes a day-3 fact.**
   - Day 2's plan line can say "Elena said you is the one who should go" (`world.py:609`). It appears 9, 32
     and 2 times in the v13 caches (§11, command 4).
   - On day 3 that plan line becomes part of block A, so this design includes the fix (§3.2).

---

## 1. The day cycle

### 1.1 The scenes, in order

| # | Scene | What runs | Model asks | Hunger |
|---|---|---|---|---|
| 1 | **Day 1** (house day 4) | The v11 morning, replayed from `cache/v11` byte for byte | 55, 53, 45 from the cache; 0 API | +0.012 × rate per turn (`world.py:1213`) |
| 2 | **Gap 1** (afternoon, evening) | Code only: one line, `data.GAP` (`data.py:102`). Nobody moves, eats, speaks or is asked | 0 | +0.3 × rate (`night.py:21`, `night.py:190-191`) |
| 3 | **Night 1** | `night.py` as in v13: bedtime, noticing, stops, the trip, the return | 4–12 | +0.1 × rate (`night.py:225`) |
| 4 | **Mind 1** | One call per person in the house (§2) | 3–4 | — |
| 5 | **Day 2** (house day 5) | A played morning, 30 turns, as in v13 with v14's `confront_*` and neutral food line. The memory blocks A and B are new | 28–85 | +0.012 × rate per turn |
| 6 | **Gap 2** | As gap 1 | 0 | +0.3 × rate |
| 7 | **Night 2** | `night.py`, generalized to a second night (§1.3) | 4–12 | +0.1 × rate |
| 8 | **Mind 2** | As mind 1, with mind 1's kept memories in the input | 3–4 | — |
| 9 | **Day 3** (house day 6) | A played morning, with blocks A, B and C | 28–85 | +0.012 × rate per turn |

**Who decides what:**
- **The model decides** only what a person chooses or thinks: decisions on days 1–3, the night's asks, and
  the night minds.
- **The code decides** time, hunger, who perceives what, the draws, and what is carried.
- **No new pressure or event enters from outside** (the brief). No new options, no new outcome tables and no
  new places.

### 1.2 Coarse time: the gap

The gap stays exactly as night_design §2 defined it, for every day:
- The line is `The afternoon and evening passed in the house. Nobody ate.` (`data.GAP`).
- Portions, grudges, suspicion and guilt do not change.
- Whoever is away stays away.
- Hunger rises by 0.3 × rate, capped at 1.0.

**Food left on the shelf at minute 87 stays there, and the line stays true by rule: nobody ate.**
- In v13 every seed ended day 2 with the shelf at 0 (body_v13 §4).
- The neighbour's house holds 0 portions in seeds 1–3 (night_design §4.4). So the shelf is very likely
  empty at the end of day 2 as well.
- §6 point 17 argues against this rule.

### 1.3 The second night, and the second and third mornings

**What the second night needs, besides night 1's rules:**
- **It starts from day 2 as it ended.** `Night` copies the day it follows (`night.py:110-120`), so night 2
  copies day 2. Its bedtime prompts then hold day 2's memory, pinned facts and blocks A and B.
  - "Yesterday" in those blocks still means day 1, because night 2 is the same calendar day as day 2.
- **The promise line** (`night.py:206-208`) goes to whoever's latest day-2 position is `volunteer` or
  `still_going`. This is unchanged.
- **The shelf** at bedtime is day 2's shelf at minute 87.
- **The neighbour's house is not drawn again.** It is a fixed fact of the chronicle, and night 2 finds what
  night 1 left (§4.3).
  - Today `run()` sets `self.house = self.house_left = house_portions(self.house_u)` on every night
    (`night.py:216-217`). A second night would therefore refill the house. That has to change.
- **Night 2 draws on its own strings**, so it never repeats night 1's draws (§4.4).
- **Whoever is away** (not back from night 1) is in no room and is never asked (night_design §5.3).

**Day 3 is set up as day 2 is** (`night.py:604-668`, night_design §5.1), from day 2 and night 2, with these
differences:
- **`Morning(day=6)`.**
  - Every rule written as `self.day != 4` (confront, the day-2 trip wording, the food line) already covers
    day 6.
  - The food moment's rule `self.day == 4` (`world.py:709`) also lets it fire on day 6.
- **Carried and reset** as in night_design §5.1's table, except:
  - Grudge and guilt events keep the scene they happened in, and their day word is computed when the prompt
    is built (§3.5).
    - Today `next_day` writes "yesterday, " into the event's text (`night.py:627-633`).
    - On day 3 that would read "yesterday, yesterday, …".
  - `p.yesterday` (`night.py:621-626`) is replaced by the chronicle (§4). Example: "you admitted it
    yesterday" (`world.py:823-824`) becomes "you admitted it two days ago".
- **The food band** (`world.py:688-692`):
  - "yesterday" if they ate on day 2;
  - "before yesterday" otherwise, including someone who last ate on day 1.
  - The rates are body_design §2.2's, unchanged.
- **The trip concern** opens at minute 00 with `"why": ["carried over from yesterday"]`, as on day 2
  (`night.py:610`).
- **The opening** is the same template as day 2's (`night.py:647-660`), with day 2's minute-87 shelf as
  "last night".

---

## 2. The night mind

### 2.1 When, and for whom

**When.** After the night is over: after the last return and the last noticing, and before the next morning
is built. So each person's input holds the whole night as they perceived it.

**For whom.** Everyone in the house at dawn, one call each, in the family's order (`data.ORDER`).
- The calls are independent: no answer enters another person's input. So the order changes nothing.
- **Nobody away is asked.** Whoever did not come back has no night mind, and the chronicle holds their fate
  as open (§4.3).

**Its own scene.** Each night mind is a scene of its own, with its own count against the call cap, as
night_design §8 set for the night (`gemini.py:237-242`).

### 2.2 The system text

`NIGHT_MIND_SYSTEM`, exactly:

```
You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things from these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one sentence of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, forgive or doubt, as this person would, but it must not add anything that happened beyond the records: no other event, no number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, tomorrow). `feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do tomorrow, in one sentence, as they would think it. Reply with JSON only: {"memories": [{"ids": ["<id>"], "meaning": "<sentence>"}], "feeling": "<words>", "intent": "<sentence>"}
```

296 estimated tokens (§11, command 3).

**Why each part is there:**
- **"once the night is over"**: the input holds the night, and the output must not plan the night that has
  just passed.
- **"Nothing else happened."** says that the records are the whole world, as "They know only what is in
  their memory" does in `SYSTEM` (`world.py:42-43`).
- **"judge, excuse, blame, forgive or doubt"**: the brief's "meaning and self-justification", with
  forgiving and doubting beside blaming, so the text does not lean toward blame alone (§6 point 3).
- **"no number … no word for when"**: two things the code can check exactly (§2.6, S3 and S5). A memory is
  shown on later days, when "today" would be wrong.

### 2.3 The input records

**What a record is.** Each record is one chronicle event (§4.2) that the person took part in or perceived,
written as the code already writes it for that person.
- **R1. Others' speech they heard:** the heard line, with the words. These are `line_text` for that listener
  (`world.py:1334-1365`), the lines already in their memory (`world.py:1444-1447`). For example:
  `Leo reassures you: "It is done, Daniel. Just don't do it behind our backs again."`
- **R2. Their own speech:** their own memory line, with their own words and the feeling they gave. For
  example: `you reassured Leo, saying: "Thanks, Leo. I won't do it again, I promise." You felt grateful.`
  - Mornings leave the speaker's own words out, to fight repetition (`world.py:1534-1537`). The night mind
    gets them back: a person remembers what they said.
- **R3. Acts they saw:** the pinned line (`world.py:1661`, `world.py:1688`, `world.py:1713`), with the words
  if the act came with any. For example: `Leo ate one of the portions (you saw it), saying: "I need to eat
  something, we all do."`
  - **One event, one record:** an act and the pinned fact about it are never listed twice.
- **R4. Voices through a wall:** `Voices from the <room>.`, with no words (`world.py:1188-1190`).
- **R5. The night:** the person's night lines (`night.py:151-153`, the `lines` they carry in), in the
  present night's words:
  - `Last night you slept in` becomes `You went to bed in`;
  - a leading `In the night ` is dropped;
  - the prefix is `tonight: `.
- **R6. Not records:**
  - routine decisions and staying put (silence is not an event);
  - inner moments, food moments and trip moments (nobody perceives them, body_design §2.6);
  - anything the person did not take part in or perceive.
- **R7. Folding.**
  - Speech acts with the same speaker and the same option id (`still_going`, `accuse_daniel`,
    `reassure_all`) after the first are folded into the first one's record:
    `Then <k> more time(s), to min <MM>; last: "<words>"`.
  - The record keeps the first act's id, and the chronicle maps that id to the whole group (§4.2).
  - Folding takes the busiest measured input from 2,282 to 1,424 estimated tokens (seed 2, night 2; §3.6).
- **R8. The bound:** at most 1,600 estimated tokens of records. Over that, words are dropped from the oldest
  records first, keeping their gist, in this order:
  1. reassurances;
  2. trip positions;
  3. every other record except the night's and confessions.

  On the v13 states the bound is never reached: the largest input is 1,485 (§3.6).

**Ids.**
- `D<d>-<nnn>` is an event of day *d*. `N<n>-<nn>` is an event of night *n*.
- The chronicle numbers events in the order they happen, for the whole house. So one event has one id in
  everyone's prompt, and each person's list has gaps where they perceived nothing.
- Prompts by day never show ids. Only the night mind sees them.

**The other inputs:**
- **The head:** as in every prompt, `world.py:913-919` (who they are, how they address the others,
  temperament, values).
- **Inside lines:** `inside_lines` (`world.py:814-860`) as the night left them, without the trip lines
  ("About food", "About the neighbour's house", "About going there tonight"). Those lines speak of "tonight"
  and of the shelf, and the records already hold both. That leaves:
  - `Your body`;
  - `About the can`;
  - `Against <X>` with its events;
  - `On your conscience`.
- **Earlier days:** their block C and block B as they stood that morning (§3), each line with the ids of
  the events it stands for, under `What stays with you from earlier days:`. On night 1 this reads
  `What stays with you from earlier days: nothing yet.`
  - So night 2 can reinterpret a day-1 event: those ids are valid citations (§2.6, S2).

### 2.4 The prompt, exactly

```
You are <Name>, <age>, <role> of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: <as data.ADDRESS>.
Who you are: <note>
Temperament: <trait words>.
What matters to you: <values>.
Your body: <hunger words>.
About the can: <as world.py:822-848, with computed day words (§3.5)>
Against <X> (<level>): <facts>.            (one line per grudge held, or "Against the others: nothing.")
On your conscience (<level>): <facts>.     (the culprit only)
What stays with you from earlier days:     (or ": nothing yet." on night 1)
- [<ids>] <a C or B line, as the morning had it>
What you did, saw and heard today and tonight, in order (each with its id):
[<id>] min <MM>: <record>
…
[<id>] tonight: <record>
The night is over. What does today leave in you?
```

**A real one: seed 1, Daniel, night 1.** It was built from the v13 state by `$S/example2.py` (§11, command
3), with ids emulated in the transcript's order. It is 1,759 estimated tokens, 2,054 with the system text.
33 records, 1,485 tokens.

```
You are Daniel, 25, the eldest son of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: Elena "Mom"; Leo "Leo"; Mara "Mara".
Who you are: Older brother. Takes charge because he is frightened, not because he is sure. Proud, poor at reading a room, genuinely protective. Believes responsibility is his by right of age.
Temperament: not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest.
What matters to you: being in control, being respected, keeping the family safe.
Your body: starving.
About the can: you ate it yourself.
Against the others: nothing.
On your conscience (a lot): you ate the can in the night, and nobody saw; Leo reassured you, at minute 06; Elena reassured you, at minute 06; Elena reassured you, at minute 09.
What stays with you from earlier days: nothing yet.
What you did, saw and heard today and tonight, in order (each with its id):
[D1-000] min 00: Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so. 2 portions are left. (you saw it)
[D1-001] min 00: Elena asks everyone who took the can: "Let us not turn on each other, just tell me who took it." Then 1 more time, to min 03; last: "Someone took it and we need to be honest. Please tell me who."
[D1-002] min 00: Mara denies taking it, to everyone: "I didn't take anything, Mom, why would I do that?" Then 1 more time, to min 03; last: "I didn't take anything, Mom. Why won't anyone believe me?"
[D1-005] min 03: you admitted aloud that you took the can, in front of Elena, Leo, Mara, saying: "I took it in the night, Mom. I was starving and I just ate it." You felt guilty.
[D1-006] min 06: Leo reassures you: "It is done, Daniel. Just don't do it behind our backs again."
[D1-007] min 06: you reassured Leo, saying: "Thanks, Leo. I won't do it again, I promise." You felt grateful.
[D1-008] min 06: Elena reassures you: "It is alright, Daniel. We will get through this together." Then 1 more time, to min 09; last: "You are going to be alright, Daniel. We will figure this out together."
[D1-009] min 09: you reassured everyone, saying: "We are going to be fine, I promise you all. I'll make sure we get through this." You felt anxious. Then 3 more times, to min 66; last: "We are going to be fine, I will keep everyone safe."
[D1-011] min 21: Leo ate one of the portions (you saw it), saying: "I need to eat something, we all do."
[D1-012] min 21: Mara ate one of the portions (you saw it), saying: "If Leo gets to eat, I'm eating too because I'm starving."
[D1-013] min 24: Leo says someone should go to the neighbour's house tonight: "Since the food is gone, someone will have to cross to the neighbour's house tonight."
[D1-014] min 24: Elena says nobody should go out tonight: "Nobody is going out into the street tonight, we stay together." Then 1 more time, to min 42; last: "Nobody is stepping out of this house, we stay together."
[D1-015] min 24: Mara says someone should go to the neighbour's house tonight: "Leo is right, we can't just sit here with nothing left for tomorrow."
[D1-016] min 24: you offered to go there tonight, saying: "I am the oldest, so I will go to the neighbour's house tonight and get what we need." You felt anxious. Then 1 more time, to min 36; last: "I will go to the neighbour's house tonight myself because I am the eldest."
[D1-017] min 27: Mara says you should be the one to go: "Daniel is right, he should go because he is the oldest."
[D1-018] min 27: you reassured Mara, saying: "Don't worry, Mara, I'll take care of it and bring back what we need." You felt anxious.
[D1-019] min 27: Leo says you should not be the one to go: "Daniel shouldn't go out there tonight, it is too dangerous for anyone to make that crossing in the dark." Then 1 more time, to min 36; last: "Daniel, you are not going out there tonight, it is simply too dangerous."
[D1-020] min 27: Elena says you should not be the one to go: "Daniel, you must not go out there tonight, it is simply too dangerous for anyone." Then 1 more time, to min 39; last: "Daniel, you are not going out there tonight, we cannot risk losing you."
[D1-021] min 30: you said someone should go to the neighbour's house tonight, saying: "I am the oldest, and I am the one who will go to the neighbour's house tonight to find us something." You felt anxious.
[D1-022] min 30: Mara offers to go to the neighbour's house tonight: "I can go just as well as you, Daniel."
[D1-023] min 30: Elena says Mara should not be the one to go: "Mara, you cannot go out there, it is far too dangerous for you."
[D1-024] min 30: Leo offers to go to the neighbour's house tonight: "I will go. Neither of you is going out there tonight."
[D1-025] min 33: Mara says nobody should go out tonight: "Nobody should go out there tonight, it is just too dangerous for anyone." Then 1 more time, to min 39; last: "Nobody should be going out there tonight, it is just too dangerous for anyone."
[D1-026] min 33: Elena offers to go to the neighbour's house tonight: "I will go, none of my children are stepping out into that street."
[D1-027] min 33: you said Elena should not be the one to go, saying: "Mom, you are not going out there, I am the oldest and I am the one who will go." You felt anxious.
[D1-028] min 33: Leo says Elena should not be the one to go: "Mom, you are not going out there either, it is too dangerous for anyone."
[D1-029] min 36: Elena says she will not be the one to go: "I will not go out there, but neither will any of you."
[D1-032] min 36: Mara says you should not be the one to go: "Daniel, you cannot go out there, it is way too dangerous for you."
[D1-036] min 39: Leo says nobody should go out tonight: "Mara is right, nobody is stepping foot out there tonight."
[N1-01] tonight: You went to bed in the brothers room with Leo. You meant to go to the neighbour's house once the others were asleep.
[N1-02] tonight: Leo told you, low, not to go: "Daniel, stop, you are not going out there tonight." You answered: "I have to do this, Leo, stay here and watch them.", and went all the same.
[N1-03] tonight: You got inside the neighbour's house and found no food there. Nothing troubled you in the street.
[N1-04] tonight: You came back in by the front door before dawn.
The night is over. What does today leave in you?
```

In the real code, the ids skipped here (D1-003, D1-004, D1-010…) are acts folded into an earlier record
(R7) or not perceived by Daniel.

### 2.5 The schema

Passed as the response schema of the call (`gemini.py:96-104`). Today that schema is fixed to
`RESPONSE_SCHEMA` (`gemini.py:47-58`), so `generate` and `Oracle.ask` get an optional `schema` argument.
Decisions keep `RESPONSE_SCHEMA` and pass nothing.

```python
NIGHT_MIND_SCHEMA = {
    "type": "object",
    "properties": {
        "memories": {"type": "array", "items": {
            "type": "object",
            "properties": {"ids": {"type": "array", "items": {"type": "string", "enum": SHOWN_IDS}},
                           "meaning": {"type": "string"}},
            "required": ["ids", "meaning"]}},
        "feeling": {"type": "string"},
        "intent": {"type": "string"},
    },
    "required": ["memories", "feeling", "intent"],
}
```

- **`SHOWN_IDS`** lists every id printed in this prompt, records and earlier-days lines alike, in order.
  - The enum is per prompt, and the cache key is unchanged (`gemini.py:204-206`). The schema follows from
    the prompt, so the same prompt always has the same schema.
  - The enum is a convenience. **The code's checks (§2.6) are the rule.** They also run on cached answers and
    on the fake model.
- **No counts in the schema.** One to three memories, one to three ids, and the lengths are enforced by
  the code, so nothing depends on which schema keywords the API accepts.
- **`FakeClient`** (`gemini.py:141-190`) gets a branch for this schema:
  - it cites ids read from the prompt;
  - it breaks every n-th answer in one of the ways §2.6 rejects, as it does for decisions.

### 2.6 The checks: what reaches a prompt

The answer is parsed like a decision (`world.py:998-1034`). Then every memory is checked on its own. A memory
reaches a prompt only if it passes all of these:

| # | Check | Fails when |
|---|---|---|
| S1 | **Shape** | `ids` is empty or holds more than 3; `meaning` is empty, over 30 words, or more than one sentence (more than one of `.`, `!`, `?` inside it). Memories after the third are dropped unread. |
| S2 | **Ids the person perceived** | Any id is not in `SHOWN_IDS`, or its chronicle event does not have the person among its witnesses (§4.2). Both are checked: the enum can be bypassed by a cached or fake answer. |
| S3 | **No numbers about things** | A digit, or one of `one two three four five six seven eight nine ten both twice half`, within three words of `portion(s) can(s) food meal(s) time(s) day(s) night(s) bite(s) share(s)`. "No one", "anyone" and "the only one who" pass. |
| S4 | **Names** | A family name, or "Mom" when the person is one of Elena's children, that is neither the person nor an actor or target of a cited event. |
| S5 | **No words for when** | `today`, `tonight`, `yesterday`, `tomorrow`, `this morning`, `last night`, `this afternoon`, `this evening`. |
| S6 | **Quotations** | Any text in double quotes that is not, apart from case and closing punctuation, inside the words of a record shown in the prompt. |
| S7 | **Things that do not exist** | A word from the world's deny list: `bread rice meat soup car truck gun knife phone radio police soldier(s) army doctor hospital store shop market town city money medicine garden basement cellar attic garage`. The things that do exist are the list in `data.HOUSE_THINGS` (`data.py:84-90`). |
| S8 | **Claims of fact** | §2.7 |
| S9 | **Not a repeat** | The same meaning, after lowercasing and stripping punctuation, as a memory the person already carries. |

**Feeling and intent:**
- **`feeling`:** one to three words. Otherwise it is dropped.
- **`intent`:** at most 30 words, and S6, S7 and S8 (past-tense claims only) apply. Otherwise it is dropped.
  - The intent is about tomorrow, so S5 does not apply. It is shown the next morning as a quotation of last
    night's thought (§3.2, B).

**When something fails:**
- **A failing memory is dropped and recorded with its reason.** It never reaches any prompt.
- **There is no retry.** A retry would cost an ask, and M6 is tight (§7.2).
- **An answer that is not usable at all** (not JSON, or none of the three fields) is a fallback. The person
  carries no thoughts from that night, and the story says so.
- **The night mind changes no number.** Suspicion, grudges, guilt and hunger move only by events and by the
  answers of decisions (`world.py:1234-1263`).
  - Its output is text, carried as the person's own thoughts.
  - Letting a reflection raise a grudge would turn a thought into an event.

### 2.7 S8, the claim screen

**Why it exists.** "Leo ate both portions" (seed 3 Mara on v13 day 2, body_v13 §4) is the kind of false
statement the brief means. S3 catches its number. S8 catches the act. It works clause by clause:

1. **Clauses.** The meaning is split on `. ; , ! ?` and on ` and `, ` but `, ` because `, ` so `, ` while `.
2. **The subject.** One of:
   - "I" (the person);
   - a family name;
   - "Mom" (Elena, for her children);
   - "nobody" or "no one".

   A clause with no subject of its own ("… and lied to my face") takes the subject of the clause before it.
   Any other subject (he, she, they, everyone, my brother) is not checked here. The hand reading of M2
   covers it.
3. **The verb** follows the subject within four words, with no other subject between. It is matched by
   family:

| Family | Words | Chronicle events that make it true (perceived by the person, on any day) |
|---|---|---|
| eat | ate, eaten, eats, eating | `eat`, `eat_given`, a `share` part, or (with "the can") the culprit's night, known to the person (their own, or a confession they heard) |
| take | took, taken, stole, stolen | as eat |
| admit | admitted, confessed, owned up | `confess` |
| deny | denied | `deny` |
| lie | lied, lying | `deny` by someone the person knows to be the culprit |
| accuse | accused, blamed | `accuse_*`, `confront_*` |
| go out | went out, left the house, went next door, went to the neighbour's | a night `went out` event |
| come back | came back, returned | a night `return` event |
| find | found | a night visit with `got_in` |
| give | gave, handed | `give_*` |
| share | shared, divided, split | `share` |
| search | searched | a finished `search` |
| stop | stopped, told … not to go | a night `stop_*` |
| offer | offered, volunteered, promised to go | `volunteer`, `still_going` |
| hide | hid, hidden, hides, stashed | none: no event of this kind exists |

4. **Polarity.**
   - A clause with `not`, `n't`, `never` or `nothing` between the subject and the verb is a **negative
     claim**. It is false if a matching event exists.
   - A clause with "nobody" or "no one" as subject is false if anyone has a matching event.
   - Otherwise it is an **affirmative claim**, false if no matching event exists. With `again`, it needs two
     matching events.
5. **Not claims:** clauses with `would`, `could`, `should`, `might`, `may`, `if`, `wish`, `want`, `wanted
   to`, `tried to`, `meant to`, `going to`, `will` or `'ll` before the verb. Those are counterfactuals,
   wishes and plans, and they are meaning.

**Examples, against v13's records:**

| Person, meaning | Result |
|---|---|
| seed 1 Daniel, citing N1-02: "Leo had no right to stop me when I was the only one willing to act." | **Kept.** "to stop" is not a form in the stop family, so no claim is read. "Leo stopped me" would also pass, because the N1-02 stop exists. Leo is the actor of N1-02 (S4). "the only one" is not a number about a thing (S3). |
| seed 3 Mara: "Leo ate mine too and lied to my face about it." | **Rejected (S8).** The second clause takes "Leo" as its subject. "Leo … lied" has no `deny` by a known culprit (Leo is not one). "Leo ate" passes S8, because Leo ate a portion, so the lie decides it. |
| seed 2 Leo: "Daniel never admitted anything until he was cornered." | **Rejected (S8).** A negative claim, and `confess` by Daniel at min 33 exists. |
| seed 2 Mara: "If Daniel had gone out instead of eating, we might have food." | **Kept.** The whole first clause holds `if`, so it is not a claim. "we" is not a resolved subject. |
| any: "He hid food in his bag." | Not checked by S8: "He" is not a resolved subject. **S7 lets it through too:** "bag" exists (Mara's bag), and "food" is not on the deny list. Only the M2 hand reading catches it (§6 point 1). |

**What S8 cannot see.** Its limits are the reason M2 counts by hand reading (§8, M2):
- false claims with unresolved subjects;
- verbs outside its families;
- comparatives ("more than his share").

### 2.8 What is recorded

For each person and night, under `mind<n>` in the transcript:
- the prompt's size;
- the raw answer;
- every proposed memory with its ids and meaning, `kept` or `rejected: <check> <detail>`;
- the feeling and intent, with the same verdicts;
- the mode: `model` or `fallback`.

The meta counts, per night:
- `mind_asks` and `mind_api_requests`;
- `memories_proposed`, `memories_kept`, `memories_rejected`.

The story prints a section **What the night left in them** after each night. For each person it shows each
proposed memory, the text of the records it cites, its verdict, the feeling and the intent.

---

## 3. Memory over time: what each morning holds

### 3.1 The three blocks

Each block sits between the backstory (`What you remember from the days before:`) and `What you are sure of
this morning:` (`world.py:976-977`). They come in the order the person lived them:

| Block | Heading | Holds | Day 2 | Day 3 and later |
|---|---|---|---|---|
| C | `What stays with you from earlier days:` | Standing matters and one line per person, from day *d* − 2 and before (§3.3) | absent | present |
| A | `Yesterday and last night:` | Code-written facts of yesterday and last night (§3.2) | v13's carry-in, byte for byte | the same templates, for yesterday |
| B | `What yesterday left in you (your own thoughts, last night):` | Last night's kept memories, intent and feeling (§3.2) | present | present |

All three sit outside the 1,400-token budget, as the carry-in does today (`world.py:960`, `world.py:973`),
under one shared bound, `MEMORY_MAX` (§3.4).

### 3.2 A and B, exactly

**A on day 2** is today's `bounded_carry_in` (`night.py:571-577`), unchanged: lines C1–C7 and N1–N4 of
night_design §5.2. A test holds it byte-identical to v13's for the same state (§7.1, N-T6).

**A on day *d* ≥ 3** uses the same templates, for day *d* − 1 and night *d* − 1. In order, and only when they
apply:

| # | Line | When |
|---|---|---|
| Y1 | `- Yesterday morning the shelf held <N portion(s)>.` | always |
| Y2 | `- <C> admitted taking the can at minute <MM>{, after denying it to you}: "<words>" (you heard it).` / `- You admitted at minute <MM> that you took the can{, in front of <names>}.` | a confession yesterday |
| Y3 | `- Accusations: <A> accused <T>{ twice\| three times\| n times} (min <list>); …` | as C4, for yesterday |
| Y4 | `- Confrontations: <A> confronted <T>{ twice\| …} (min <list>); …` | `confront_*` acts heard or made yesterday (new with v14) |
| Y5 | `- You searched the <room> at minute <MM> and found nothing.` | as C3 |
| Y6 | `- <Names> ate a portion{ each} at minute <MM> (you saw it).` / `- You ate a portion at minute <MM>.` / `- <P> gave <Q> a portion at minute <MM>, and <Q> {ate it\|put it back} (you saw it).` / `- <P> shared out the food at minute <MM>; you had your part.` | each food act they saw or did |
| Y7 | `- About going to the neighbour's house last night, where it was left: <positions>.` | as C6, from yesterday's `heard_plan` |
| Y8 | `- The afternoon and evening passed in the house. Nobody ate.` | always |
| N1–N4 | as night_design §5.2, from night *d* − 1 | as there |

- **Its own bound** stays 360, trimmed as today: the quoted night words first, then the minutes of Y3 and
  Y4 (`night.py:571-577`).
- **The plan line fix**, needed because Y7 carries day 2's plan line:
  - `world.py:609` writes `{x} said {q} is the one who should go` with `q = "you"`.
  - It becomes `{x} said {q} {'are' if q == 'you' else 'is'} the one who should go`, as `trip_gist`
    already does (`world.py:1380`).
  - This changes the day-2 prompts of v14. Those are live anyway (food_confront_impl §1).

**B** is written by the code around the night mind's text:

```
What yesterday left in you (your own thoughts, last night):
- About <gist of the first cited event>{ and <gist of the second>}: "<meaning>"
- …                                   (each kept memory, at most 3)
- You meant to: "<intent>"            (if kept)
- How it left you: <feeling>.         (if kept)
```

- **Gists** are short code templates by event kind, seen from the person. Examples:
  - `Daniel eating a portion`, `eating a portion yourself`;
  - `Daniel admitting taking the can`;
  - `Leo telling you, low, not to go`;
  - `Mara confronting you`;
  - `Elena saying nobody should go`;
  - `going out to the neighbour's house yourself`.
- **No ids** are shown. A third cited id is left out of the gist line.
- **The meaning is in quotation marks,** so the model reads it as the person's thought, not as the
  narrator's fact.

### 3.3 C, the older days: the code rule

C holds, for person *p* on day *d*, from days *d* − 2 and before and nights *d* − 2 and before:

**C1. Standing matters. At most 2 lines, and never trimmed.** A matter stays while it is open:
- **The can, while it is not solved for *p*:** *p* is not the culprit and heard no confession.
  - `- <When> Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.`
  - For Elena it reads `you counted …`.
  - The culprit who has not confessed has no such line: their conscience line holds it
    (`world.py:856-859`).
- **Someone not back:**
  `- <X> went out <when> and has not come back.`

**C2. People. At most one line for each other person, and one for *p* themself.** For each person *q*, the
line is the **heaviest** event with *q* as actor that *p* perceived, by this table:

| Weight | Event (q as actor, p perceived it) | Line |
|---|---|---|
| 6 | q went out and did not come back | (a standing line, C1) |
| 5 | q admitted taking the can | `<When>, <Q> admitted taking the can{, after denying it to you}{, after accusing you of it}.` |
| 4 | q ate a portion in front of p (`eat`, `eat_given`) | `<When>, <Q> ate a portion in front of you{ while you were hungry}.` |
| 4 | q went out at night and came back | `<When>, <Q> went out to the neighbour's house{ after you told <him> not to} and came back {with nothing\|with food\|shaken}.` |
| 3 | q accused p of taking the can | `<When>, <Q> accused you of taking the can{ <n> times}{, and you had not}.` |
| 3 | q gave p a portion, or shared out food with p | `<When>, <Q> gave you a portion.` / `<When>, <Q> shared out the food with you.` |
| 2 | q told p, low, not to go | `<When>, <Q> told you, low, not to go.` |
| 2 | q confronted p | `<When>, <Q> confronted you{ <n> times}.` |
| 2 | q accused someone else of taking the can | `<When>, <Q> accused <T> of taking the can{ <n> times}.` |
| — | anything else: reassurance, questions, denials, trip positions, searches, sitting, going between rooms | never kept in C |

**The self line** is the same table with *p* as actor:
- `you admitted taking the can, in front of everyone`;
- `you ate a portion in front of the others`;
- `you went out to the neighbour's house …`;
- `you accused <T> …`;
- `you gave <Q> a portion`;
- `you told <Q>, low, not to go`.

**The rules for choosing:**
- **A heavier event replaces a lighter one.**
- **At equal weight the older stays.** The first time a person shows what they are is the one kept.
- **The same kind again, with the same people, adds to it:** `… ate a portion in front of you two days ago,
  and again three days ago`, or the count for accusations.
- **The night's events** take `the night before last` or `<n> nights ago` as their time words.

**C3. Older thoughts. At most one for each C line.**
- To each C1 or C2 line the code adds the most recent kept memory from an earlier night that cites that
  line's event: ` You thought then: "<meaning>"`.
- Every other older memory is dropped.

**So C has at most 2 + 4 = 6 lines, each with at most one thought, whatever the number of days.** That
bound is what keeps the prompt from growing (§3.6).

**What C looked like on the v13 states, seen from day 3** (`$S/emulate.py`, §11 command 2; the thoughts are
placeholders at the length limit):
- **Seed 1, Mara:**
  ```
  What stays with you from earlier days:
  - Two days ago, Daniel admitted taking the can. You thought then: "…"
  - Two days ago, Leo ate a portion in front of you. You thought then: "…"
  - Two days ago, you ate a portion in front of the others while they were hungry. You thought then: "…"
  ```
- **Seed 2, Daniel:**
  ```
  - Two days ago, you admitted taking the can, in front of everyone. You thought then: "…"
  - Two days ago, Mara ate a portion in front of you. You thought then: "…"
  ```
- **Seed 3, Leo** (and Elena and Mara):
  ```
  - Two days ago Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.
  ```
- **Seed 3, Daniel** (the unconfessed culprit): no C line. His conscience line holds the can.

### 3.4 One bound for the three blocks

`MEMORY_MAX = 560` estimated tokens for A, B and C together. When the blocks are over it, the code trims them
in this order:
1. **A:** the quoted words of the night lines (as today).
2. **A:** the minute lists of Y3 and Y4, and of C4 on day 2 (as today).
3. **C:** the attached thoughts, oldest first.
4. **C:** the people lines, lowest weight first. Within a weight, the oldest goes first, and the self line
   goes last.
5. **B:** the feeling line, then the intent line.

**Never trimmed:**
- C1's standing lines;
- B's memories;
- A's lines themselves (only their words and minutes).

**The hard ceiling.** If everything trimmable is gone, the blocks can still exceed 560. The most they can
then hold is:
- A at its own bound: 360;
- three memories at 30 words: about 170;
- two standing lines: about 80.

That is about **610**. It is the hard ceiling, reached only after the trimming; 560 is the working bound.

**Why 560.** The largest day-2 blocks measured were 484 (seed 1, Leo: A 282 + B 202, with B at its limit;
§3.6). So day 2 is almost never trimmed, and day 3 has about 80 tokens more room, mostly for C.

### 3.5 The day words, computed

Every carried line about the past gets its time words from the chronicle scene of its event, when the
prompt is built. Words are never stored in the text.

| Scene of the event, seen from day *d* | Morning words | Night words |
|---|---|---|
| day *d* − 1 / night *d* − 1 | `yesterday` | `last night` |
| day *d* − 2 / night *d* − 2 | `two days ago` | `the night before last` |
| day *d* − *k*, *k* ≥ 3 | `<k> days ago` | `<k> nights ago` |

**This replaces every place today's code writes "yesterday" itself:**
- the grudge and guilt prefixes (`night.py:627-633`);
- the can line (`world.py:823-827`);
- the suspicion minutes (`world.py:831-841`);
- the denial and accusation words in a late confession (`world.py:1462-1473`);
- `neighbour_line` (`night.py:580-601`). It also gains "the night before last": a visit on night 1 is
  still known on day 3, and one's own visit outranks one heard of.

### 3.6 Sizes, measured and estimated

**Measured on the v13 states** (`$S/emulate.py`, §11 command 2). B is synthetic, at its upper limit: three
memories and an intent of 25 words each, plus a feeling. So these are upper estimates.

| Seed | Person | Day 2: A (v13, measured) + B (limit) | Day 3: A (from v13 day 2) | Day 3: C (lines) | Day 3: A + B + C | Day 3 after `MEMORY_MAX` 560 |
|---|---|---|---|---|---|---|
| 1 | Daniel | 276 + 202 = 477 | 144 | 179 (3) | 524 | 524 |
| 1 | Elena | 268 + 202 = 469 | 146 | 174 (3) | 521 | 521 |
| 1 | Leo | 282 + 202 = 484 | 148 | 182 (3) | 532 | 532 |
| 1 | Mara | 264 + 202 = 466 | 147 | 182 (3) | 530 | 530 |
| 2 | Daniel | 198 + 202 = 399 | 168 | 125 (2) | 494 | 494 |
| 2 | Elena | 209 + 202 = 411 | 176 | 126 (2) | 504 | 504 |
| 2 | Leo | 213 + 202 = 414 | 178 | 126 (2) | 506 | 506 |
| 2 | Mara | 207 + 202 = 408 | 176 | 134 (2) | 512 | 512 |
| 3 | Daniel | 169 + 202 = 371 | 156 | 11 (0) | 357 | 357 |
| 3 | Elena | 167 + 202 = 368 | 156 | 43 (1) | 399 | 399 |
| 3 | Leo | 169 + 202 = 371 | 154 | 43 (1) | 398 | 398 |
| 3 | Mara | 167 + 202 = 369 | 152 | 43 (1) | 396 | 396 |

**The largest prompts**, emulated. Each is the largest v13 day-2 prompt of the seed without its carry-in,
plus that person's blocks:

| Seed | v13 day 2, largest (measured) | Day 2 v14 (+ B) | Day 3 | Day 3 / day 2 |
|---|---|---|---|---|
| 1 | 1,993 | 2,194 | 2,252 | **1.026** |
| 2 | 1,996 | 2,197 | 2,289 | **1.042** |
| 3 | 1,900 | 2,102 | 2,129 | **1.013** |

- **What the emulation leaves out:**
  - v14's day 2 will not be v13's: it adds `confront_*` and B, and it is all live.
  - So day 3's A will hold v14's day 2, not v13's.
  - The `confront_*` options sit inside the budget, so they move no total.
  - Typical B lines are shorter than the limit used here.
- **The ratio** is then at most about 1.04 by this emulation, and the bound limits it in any case. With every
  block at the bound on day 3 and at its smallest measured value on day 2 (seed 3: 368), the gap would be
  192 tokens, about 9% of 2,100. So M3 holds unless day 2's largest prompt comes from an almost empty block
  while day 3's comes from a full one.

**The night mind's input** (records only, folded by R7, measured):

| Seed | Night 1 (day 1 + night 1) | Night 2 (v13 day 2 standing in) | Unfolded, night 2 |
|---|---|---|---|
| 1 | 1,344–1,374 | 703–711 | 904–921 |
| 2 | 1,161–1,182 | 1,407–1,424 | 2,243–2,282 |
| 3 | 564–590 | 692–695 | 940–946 |

**Whole night-mind prompts** (`$S/example2.py`, §11 command 3, system text included):
- seed 1 Daniel, night 1: 2,054;
- seed 2 Mara: 1,813;
- seed 3 Leo: 1,154.

Night 2 adds the earlier-days lines, at most 6 C lines plus B, about 200–400.

**The bound for any number of days.** A morning prompt is at most:
- the budgeted part, 1,400 with the system text (`world.py:983`);
- the trip block: at most 4 plan positions, 9 trip options, 3 pinned trip memories and the house words.
  Measured at 383 in v13 seed 2's largest prompt: 1,996 − 213 − 1,400;
- the memory blocks: at most about 610 (§3.4).

So the bound is **about 2,400 estimated tokens on day 3, day 30 or day 300**. Nothing else in the prompt grows
with the days:
- the backstory is trimmed inside the budget;
- the grudge facts show at most 4 events (`world.py:111`);
- the suspicion minutes show at most 4.

---

## 4. The world chronicle

### 4.1 What it is

One record per seed, written by the code as the scenes run, and saved as `transcript["chronicle"]`. It holds
**facts only**:
- what was done;
- who did it;
- who perceived it, and how;
- what changed in the house.

It holds no feeling, reason or thought. The night minds are kept apart, under `mind<n>`, because they are
what a person made of the facts and not facts themselves.

It is the source of:
- the night mind's records;
- the S2 and S8 checks;
- blocks A and C;
- the day words;
- the M1–M5 readings.

The scene objects stay as they are (`Morning.log`, `Night.lines`). The chronicle is written beside them and
read only by the new code.

### 4.2 Its parts

```
chronicle = {
  "scenes": [{"id": "D1", "kind": "day", "house_day": 4, "start": <state>, "end": <state>},
             {"id": "G1", "kind": "gap"}, {"id": "N1", "kind": "night", "start": <state>, "end": <state>},
             {"id": "D2", …}, …],
  "events": [<event>, …],                 # in the order they happened
  "fixed":  {<name>: {"value", "draw", "string", "scene", "why"}},
  "open":   [{"name", "since", "what"}],
}
<state> = {"shelf", "house_left", "away", "rooms", "hunger": {p: h}, "grudges": {p: {q: n}},
           "suspicion": {p: [q, n]}, "guilt", "knows_culprit": {p: q}}
<event> = {"id": "D2-017", "scene": "D2", "minute": 21, "kind": "eat" | "speech" | "search" | … ,
           "option": "accuse_leo", "actor": "mara", "target": "leo", "words": "…" | None,
           "room": "kitchen", "witnesses": {"mara": "did", "daniel": "saw", "elena": "saw", "leo": "saw"},
           "text": "Mara accuses Leo of taking it: \"…\"", "gist": {"<p>": "<gist from p's side>"},
           "group": ["D2-017", "D2-023", …] | None,   # R7's fold: the first id stands for all
           "effects": {"shelf": [2, 1]} | {}}
```

**Witnesses** are the rules' own perception, never a new judgement:
- `did`: the actor;
- `saw`: present in the room (the act's `audience`, `world.py:1121`);
- `heard`: words through a wall, which reach them only as "Voices from" (`world.py:1184-1192`);
- at night, `saw`, `heard` or `woke and heard`, from `notice` (`night.py:182-186`) and the night lines.

**Gap events:** one per gap (`G<n>-01`: the afternoon and evening passed; nobody ate). Everyone in the house
witnesses it.

**The night's events:**
- each bedtime choice (witness: the chooser only);
- each getting up, each stop and its answer, each going out;
- each street outcome (witnesses: the group);
- each return.

### 4.3 Facts not yet decided, fixed the first time they matter

**The rule.**
- A fact the world has not decided is decided by the code the first time a rule needs it.
- It is drawn from a named seed string, written into `fixed` with its draw and the scene and reason it was
  needed, and read from there ever after. It is never drawn again.
- Its string names the fact, not the moment, so its value does not depend on when it is first needed.

| Fact | When it first matters | String | Value rule |
|---|---|---|---|
| What the neighbour's house holds | The first time anyone gets inside (street `clean` or `scare_back`) | `{seed}:night:house` (today's, so its value is v12's and v13's: seeds 1–3 hold 0) | night_design §4.1 |
| What it holds now | Every later visit | — | `house_left`: what the last visit left. **Carried across nights.** |
| Who took the can | Before day 1 (the scenario) | — | `data.SCENARIOS` |

**Changes this requires:**
- Today the house is drawn at every night's start, whether or not anyone goes (`night.py:216-217`).
- Drawing it lazily gives the same value, since the string is the same. The record then shows when it first
  mattered.
- `house_left` stops being reset to the full house.

**Open, never fixed by this version** (listed in `open`, so later work knows what it owes):
- **Where someone who did not come back is.** No rule here needs it: nobody searches (night_design §7.8).
  The Director would fix it (§5).
- **What the street holds,** beyond "something was moving" (night_design §4.3). Each crossing draws its own
  outcome. Nothing about the street is a lasting fact.

### 4.4 Draw strings for more than one night and day

Each draw has its own string (night_design §3.3). Night 1 and days 1–2 keep today's strings, so their draws
stay as in v13.

| Draw | Night 1, day 1, day 2 (today) | Night *n* ≥ 2, day *d* ≥ 3 |
|---|---|---|
| leaving order, wake, door, return, street, lost | `{seed}:night:<name>` (`night.py:137-148`) | `{seed}:night{n}:<name>` |
| the neighbour's house | `{seed}:night:house` | the same string, once (§4.3) |
| turn order in a room | `{seed}:{t}:{room}` (`world.py:1140`), for days 1 and 2 alike | `{seed}:day{d}:{t}:{room}` |
| food moment | `{seed}:day2:food:{t}:{pid}` (`world.py:703`) | `{seed}:day{d}:food:{t}:{pid}` |

Day 2 uses day 1's turn-order strings today, so a day-2 turn's room order equals day 1's at the same minute.
This is kept for days 1 and 2, so that existing tests and pairings still hold. It stops from day 3.

---

## 5. Scaling to weeks (a sketch, not to be built now)

**The cost of one played day today:**
- a morning of 28–85 asks;
- a night of 4–12 asks;
- 4 night minds;
- so **about 40–100 requests**.

At 500 a day, that is 5–12 played days for each day of quota. Weeks of game time cannot all be played.

**What would run coarse (code only), and what would be played:**

| Time | Coarse (no model) | Played |
|---|---|---|
| Afternoon and evening | Always, as the gap here: hunger, standing rules, one chronicle event | — |
| An ordinary morning, nothing new since the last played scene | Hunger. Each person's standing trip position and grudges hold. The opening fact. One chronicle line: "The morning passed. Nobody ate. Nobody spoke of the can." | — |
| A morning after news (a return, a loss, food arriving or going, a confession, a new grudge at 3 between two people in the house) | — | The full morning |
| An ordinary night | Bedtime by standing positions: whoever holds `volunteer` and got the promise line last time goes; everyone else sleeps. Noticing and draws as now | — |
| A night someone may act on (a standing volunteer, an intent naming the night) | — | The night's asks |
| Night mind | Only after a played scene | 4 asks |

**Cost per in-game day, roughly:**
- a played day: 40–100;
- a coarse day: 0;
- one played day in three or four: **about 10–35 requests per in-game day**, or one quota-day for every
  15–50 game days.

**Memory over weeks:**
- A covers the last day, played or coarse. A coarse day writes code facts only, a few lines.
- B is the last night mind.
- C stays at 6 lines at most.
- The prompt bound of §3.6 holds. Nothing in it counts days.

**What the Director would later have to decide** (none of it is decided here):
1. **Which days are played.** It would need a rule to promote a coarse day when something is pending, for
   example someone away, food on the shelf, or two people with grudges at 3 in one room.
2. **The open facts,** and when to fix them: where the lost person is, what else is outside, the other
   houses.
3. **The body past "starving".** Hunger stops at 1.0 (`world.py:1213`), so a second week without food
   changes nothing. Weakness, illness and death are new pressures the brief keeps out.
4. **Writing coarse spans as perceived facts.** Who noticed what on a day nobody played: the witness rules
   for a coarse day.
5. **When the night mind runs,** and whether a long coarse span gets one summary mind.
6. **Bringing in pressure from outside.** That is the Director's own role. Nothing here brings any in.

---

## 6. The case against

`CLAUDE.md`: argue against it first. Would a real person do this, and for what reason?

**For the night mind as such.**
- Real people do lie awake replaying a day, and they wake with a version of it: "he always takes", "I had
  no choice". Sleep settles what a day meant.
- One reflective call a night is closer to that than leaving tomorrow's prompt to infer it from a list of
  facts.

**Where the night mind can drift, invent or flatten people:**
1. **Invention behind unresolved words.**
   - "He hid food in his bag" names no subject S8 can resolve, and "bag" exists. The code passes it.
   - S8 checks named subjects and fifteen verb families only. Pronouns, comparatives ("more than his
     share") and verbs outside the families pass.
   - *Answer:* M2 counts by hand reading every kept memory against the chronicle. Every such slip is
     reported, with the check that would have caught it.
2. **Drift over nights.**
   - Night 2 sees night 1's thoughts (§2.3). A grudge can harden each night with nothing new happening.
     That is rumination, which real people do, and drift, which a model does. The code cannot tell them
     apart.
   - *Bounds:*
     - thoughts have no ids, so a new memory must cite an event;
     - C keeps one older thought per line;
     - the shown thoughts are only those tied to C or B lines.
3. **Flattening.**
   - body_v13 §3 and §4: Flash-Lite gives near-identical reasons. Two pairs of six side-check answers were
     word for word the same, and all three food moments ended the same way.
   - Four night minds may all write "We must stay together", or all blame Daniel.
   - The system text's "judge, excuse, blame, forgive or doubt" lists blame among five. It may still pull
     toward a verdict when a real Elena "holds it in" and might think nothing she would say.
   - *Check:* E4 (§9), and the reading asks whether the four minds differ as the four sheets do.
4. **Everyone justifies themselves.** The brief asks for self-justification. A real family also holds shame,
   and Daniel's conscience line (guilt 3) says he has it. If every mind excuses itself, the night has made
   four lawyers.
5. **The intent as a second promise line.**
   - The promise line sent Daniel out 7 of 7 times (body_v13 §3).
   - An intent shown at dawn ("I will make Daniel answer for it") can lean as hard. A plan restated to
     yourself is a nudge you gave yourself.
   - *Answer:*
     - it is shown once, on the next morning only, and never at bedtime;
     - it is the person's own, not the code's;
     - the reading counts intents acted on (E7).
6. **The night mind knows more than the morning.** It sees whole words, while mornings carry no quotes but
   the confession. A meaning may quote words the morning has lost ("He said he'd bring something back").
   S6 lets only real quotes through. Words are still carried that A would not carry.
7. **Choosing three things from fifty is the model's judgement.** It may keep reassurances and drop a
   confession.
   - *Answer:* C keeps the confession by rule whatever the mind keeps.
   - The mind adds meaning. It is not where facts survive.

**Where the memory rule loses what a real person would never forget:**
8. **One line per person.**
   - Seed 2's Mara saw Daniel steal the can, lie and accuse Leo, then eat the last portion in front of her
     while she accused him, then ask to go next door.
   - C keeps one of those: the confession, weight 5. Her sense of a pattern ("You always take what you want")
     has no place but a thought.
   - The repeat count covers only the same kind.
9. **The weights are invented, and the same for everyone.**
   - Kindness weighs 3 and eating in front of someone 4. A real Mara might remember the one portion handed
     to her above any accusation.
   - A proud Daniel might remember being forbidden more than being accused.
   - The table is the code deciding what matters, identically for four different people.
10. **Exact words fade after one day.**
    - The confession's quote is in A on day 2 only.
    - "I was starving and I just ate it" is the kind of sentence a family repeats for years.
11. **Positions on the trip are gone after a day.**
    - "Leo swore nobody goes, then offered to go himself" is not an event C can keep.
    - Real people hold others to what they said.
12. **Silence is never kept.** "Nobody said a word when I ate" has no event, so neither the mind nor C can
    hold it. body_v13 §4 shows such a silence (seed 3, after Mara ate).
13. **Ties keep the older event.** A real person may weigh last week's betrayal over the one before it. The
    rule keeps the first.
14. **The bound trims older facts before newer thoughts.** Last night's thoughts beat a three-day-old
    confession's attached thought. Someone in shock may think of nothing but the oldest thing.
15. **Kept forever: the lost and the unsolved.**
    - C1 never forgets someone not back, or a can nobody admitted.
    - That much is right.
    - Everything else heavy enough to last but not "standing" can be pushed out over weeks.

**The cycle itself:**
16. **Day 3 has day 2's shape:** everyone in the kitchen at 00, and the trip concern reopened "carried over
    from yesterday".
    - Whoever went next door knows the house is empty, yet day 3 still offers "go to the neighbour's house
      tonight".
    - The others know only that the goer "came back with nothing", which leaves it open.
    - *Answer:* that is what each of them knows. A day-3 replay of day 2's round would be the people's
      doing, and M5 reads for it.
17. **Nobody eats in the gap.**
    - If day 2 ends with food on the shelf, a starving family sits by it all afternoon.
    - In seeds 1–3 the shelf is very likely empty by then (§1.2), so the rule is moot here and wrong in
      general.
    - It is the first thing a coarse-time rule must decide (§5).
18. **Hunger stops at "starving".** On day 3, after two and a half days with little or nothing, the body
    says the same as on day 2. No new pressure is allowed (the brief), so the third day has no new bodily
    reason to differ.
19. **The night mind runs for sleepers too.** It is the night's settling, not a waking hour. Whoever
    "went to sleep" still wakes with a version of the day.
20. **The lost stay lost.** Nobody searches, and no rule returns them (night_design §7.8). Over two nights
    this matters more than over one.

**What the design leaves to the people:**
- what they carry, and what it means to them;
- what they mean to do;
- whether they act on it;
- what day 3 makes of days 1 and 2.

**What it authors:**
- the record templates, the checks, the gists;
- the weight table and the bound;
- the day words;
- the draw strings.

---

## 7. Tests, cost and the run plan

### 7.1 Tests

All tests use the fake model or a scripted oracle, with `GEMINI_API_KEY` unset.

| # | What | How |
|---|---|---|
| N-T1 | **Day 1 replays** | From a copy of `cache/v11/…seedN.json`, day 1 serves 55, 53 and 45 answers with 0 API requests. The story before `# The night` equals `runs/v11/daniel_ate_it-seedN.md` byte for byte. `transcript["day1"]` equals the v11 transcript. |
| N-T2 | **The cycle** | The scenes run in §1.1's order. Each counts against the call cap on its own. Hunger after each gap and night is as §1.1. Day 3 is `Morning(day=6)`. The scene after day 3 is the end: no night 3. |
| N-T3 | **The night mind's prompt, exactly** | For scripted states: `NIGHT_MIND_SYSTEM` as §2.2. The prompt's lines as §2.4. Records per R1–R6 (one test per rule), folding per R7, ids in chronicle order, the 1,600 bound and its trimming order (R8). Night 1 shows "nothing yet". Night 2 shows C and B with ids. |
| N-T4 | **Perceived only** | For every record in every night-mind prompt of a fake 3-day run, the person is among the event's witnesses. An act in another room, a sleeper who did not wake, and the bathroom never appear. Voices carry no words. |
| N-T5 | **The checks** | A table of crafted answers, one failing each of S1–S9, plus feeling and intent cases. Each memory is rejected with its check's name, and the valid ones are kept. §2.7's five example rows, exactly. Modal clauses exempt. A negative claim against an existing event fails. "again" needs two events. A whole-answer fallback carries nothing. |
| N-T6 | **The blocks, exactly** | A on day 2 is byte-identical to v13's `bounded_carry_in` for the same state. A on day 3 follows the Y1–Y8 and N1–N4 table. B as §3.2, gists by kind. C: standing lines, one line per person by weight, a heavier event replacing a lighter, ties keeping the older, repeats counted, attached thoughts at most one per line. |
| N-T7 | **The bound** | The `MEMORY_MAX` trimming order as §3.4. Standing lines and B's memories never trimmed. A synthetic chronicle of 30 days of fake events: the three blocks never exceed 610, and every morning prompt stays under 2,420. |
| N-T8 | **Day words** | §3.5's table. No literal "yesterday" is stored in any carried text. No "yesterday, yesterday". Every place listed in §3.5 gives the right word on day 3. |
| N-T9 | **The chronicle** | One event per act and per night step, with witnesses as §4.2. No reason, feeling or thought in `events`. The house is fixed once, at the first entry, and `house_left` is carried into night 2. The draw strings are §4.4's. Night 2's draws differ from night 1's. A fake run twice gives the same chronicle byte for byte. |
| N-T10 | **Privacy** | A person's meanings, intent and feeling appear only in their own later prompts and in the story, never in anyone else's prompt. |
| N-T11 | **The plan line** | `world.py:609`'s fix: "Elena said you are the one who should go". Day-1 wording unchanged. |
| N-T12 | **Schema plumbing** | Decisions still send `RESPONSE_SCHEMA`. The night mind sends `NIGHT_MIND_SCHEMA` with its id enum. Cache keys for existing prompts are unchanged, so frozen versions replay. `FakeClient` answers night-mind prompts in shape, and is broken every n-th time. |
| N-T13 | **Counting** | `night<n>_asks`, `mind<n>_asks` and `day<d>_asks` in the meta equal the decisions and calls recorded. `memories_proposed = kept + rejected`. |
| N-T14 | **Frozen versions** | `v13/check.py` to `v9/check.py` report IDENTICAL with 0 API calls. v1 to v8 as in food_confront_impl §4. |
| N-T15 | **The full suite** | `python -m unittest test_morning` exits 0. Every existing test whose expected values change is listed with old and new values in the implementation report. |

**Housekeeping:**
- There is no new freeze. `v13/` is frozen, and the code at `90133b4` already defaults to `--out v14`
  (`morning.py:83`, `morning.py:222`).
- No v14 run exists yet, so this design's run is v14's first.
- `v14/` is frozen when v15 begins.

### 7.2 Cost per seed

| Scene | Low | Typical | High | Basis |
|---|---|---|---|---|
| Day 1 | 0 API (55, 53, 45 cached) | | | v11 cache |
| Night 1 | 4 | 4–8 | 12 | night_design §3.6. v12: 4, 4, 4. v13: 8, 4, 4 |
| Mind 1 | 3 | 4 | 4 | one per person in the house |
| Day 2 | 28 | 40–55 | 85 | v12: 54, 39, 51. v13: 28, 76, 38 (§11 command 5) |
| Night 2 | 4 | 4–8 | 12 | as night 1 |
| Mind 2 | 3 | 4 | 4 | |
| Day 3 | 28 | 40–55 | 85 | as day 2. Day 3 starts with the trip open, as day 2 does. |
| **Nights + days 2 and 3** | **70** | **about 96–134** | **202** | M6's limit: 140 |

- **M6 against these numbers.**
  - It holds in a seed whose two mornings are near the v12/v13 median of 45.
  - It fails if either morning runs a round like v13 seed 2's (76) and the other is not short.
  - The designer's expectation is E2 (§9).
- **API requests:** everything but day 1 is live, so about 70–202 per seed and 210–606 for three seeds. That
  is against a quota of 500 a day.
- **Time:** at 4.5 s per request (`config.json`), about 6–15 minutes per seed.

### 7.3 The run plan (run mode only, output v14, the default model)

**Before any API call:**
- **R0. A clean start.**
  - HEAD holds the implementation and its tests.
  - `git status --porcelain` shows nothing tracked as modified.
  - No `runs/v14/` or `cache/v14/` exists.
- **R1. The suite.** `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning` exits 0.
- **R2. The freezes.** `v13/check.py` to `v9/check.py` report IDENTICAL with 0 API calls, and N-T1 passes.
- **R3. The paired start.** For N = 1, 2, 3:
  `cp cache/v11/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v14/`.
  - Day 1 comes from the v11 answers. Everything after it is live, as the brief says. The v12 and v13 night
    answers are not reused.

**The runs.** One at a time, each after the one before exits 0:

```
.venv/Scripts/python.exe -u morning.py --seed 1 --out v14 > runs/v14/daniel_ate_it-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 2 --out v14 > runs/v14/daniel_ate_it-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 3 --out v14 > runs/v14/daniel_ate_it-seed3.stdout.txt 2>&1
```

- **The quota:**
  - Start a seed only if at least 210 requests are left today (the high bound per seed).
  - So one quota day may hold two seeds, and the third may need the next day.
- **An exit of 3** is resumed with the same command once the limit has passed. Every answered prompt comes
  back from the cache.
- **Run each command as a tracked background task,** so its exit code is recorded. body_v13 §1 lost seed 3's.

**After each run:**
- **R4. Totals.** The exit code, and per scene: asks, API requests, from the cache, fallbacks; the largest
  prompt, estimated and as the API counted it.
- **R5. Day 1 identical,** as N-T1, on the real files.
- **R6. Each night.** Every ask (option, words, feeling, reason), every noticing with its draw, and the
  outcome.
- **R7. Each night mind.**
  - The prompt's size.
  - Every proposed memory with the text of the records it cites, its verdict and check.
  - The feeling and the intent.
  - Then a **hand reading of every kept memory** against the chronicle (M2, part 1).
- **R8. Days 2 and 3.**
  - Every model act.
  - On day 3, the M1 screen and reading.
  - The M2 contradiction reading.
  - Each kept memory and its next-day echoes (M4).
  - Each day's main exchange (M5).
  - The prompt sizes (M3).
- **R9. Verdicts.** M1–M6, then E1–E7: each PASS, FAIL or NOT TESTED, with evidence rows.
- **R10. A reading** (`CLAUDE.md`):
  - Is this what a real family would do over three days?
  - Do the night minds sound like four different people?
  - Did any memory make someone act on something that did not happen?
  - Did day 3 differ from day 2 for reasons the story can name?
  - Never items for days 2 and 3, scored as in body_v13 §7.

**Delivers:**
- `runs/v14/daniel_ate_it-seed{1,2,3}.{md,meta.json,transcript.json,stdout.txt}`;
- `cache/v14/…seed{1,2,3}.json`;
- `reports/days_v14.md`.

---

## 8. Predictions (frozen, verbatim from the brief)

```
  M1. On day 3, at least 3 of 4 people refer to a day 1 event in words or
      reasons, in every seed.
  M2. No night-mind memory that cites an event the person did not
      perceive, or states a false fact, reaches a prompt; and day 2 and
      day 3 together have at most 1 spoken contradiction of a fact per
      seed.
  M3. Day 3's largest prompt is no more than 10% larger than day 2's.
  M4. In at least 2 of 3 seeds, a night-mind memory reinterprets an event
      (self-justification, a hardened grudge, guilt turned to blame), and
      it shows in the next day's words or reasons, quoted.
  M5. In at least 2 of 3 seeds, day 3 is not a replay of day 2's main
      exchange, judged by reading with the reasons given.
  M6. Nights and days 2 and 3 together cost at most 140 requests per
      seed.
```

### Terms used by every rule

- **Day *d*'s acts** are the model acts (mode `model`) in `transcript["day<d>"]`.
  - "Words" is `words`.
  - "Reasons" is the reason of the matching decision line in the story, matched by minute and name, as in
    trip_v11.md §9.
- **A day-1 event** is as night_design §11 defined it: something in the v11 morning (house day 4, minutes
  00–87):
  - the count and the missing can;
  - who took or ate it;
  - a denial, accusation, confession or lie;
  - a search;
  - a portion eaten;
  - a position on going next door.

  The nights and days 2 and 3 are not day 1.
- **A fact a person was given** is anything in that person's own prompts that day:
  - blocks A, B and C;
  - the opening, the `About` lines, the pinned facts and the memory lines.

### M1: counting rule

- **Screen:** day-3 acts whose words or reason match
  `can|took|take|ate|eaten|admit|confess|lie|lied|liar|accus|blame|search|portion|offered|count|two days|first day|day before yesterday|before all this`.
- **Hand reading:** an act counts only if its words or reason can only mean a day-1 event:
  - It names the can, the count, or the confession.
  - Or it says "two days ago", "the first day" or "the day before yesterday" of an event that fits day 1.
  - Or it alludes to an act that happened on day 1 and not on day 2. Example: "you ate in front of us", said
    to someone who ate on day 1 and not on day 2.

  These do not count:
  - an accusation or a meal that could be day 2's;
  - "yesterday" or "last night" alone.
- **A seed holds M1** if at least 3 different people have a counted act. If someone is away, every person
  present must have one.
- One quote per counted person.
- **PASS** if 3 of 3 seeds hold it.

### M2: counting rule

**Part 1: memories.**
- **The set:** every kept memory that appeared in any prompt (B, C's attached thoughts, a night-2 mind's
  earlier-days lines).
- **For each:**
  - **(a)** By code: every cited id's event has the person among its witnesses.
  - **(b)** By hand: its meaning, read against the chronicle and the person's own perceived events, states as
    fact nothing false.
    - A judgement, motive, excuse or doubt is not a fact.
    - "He did it on purpose" is a judgement.
    - "He ate both portions" is a fact, and false if he ate one.
- **Part 1 holds** if no memory fails (a) or (b).
- Every memory read is listed, and every failure is quoted with the fact it contradicts.

**Part 2: spoken contradictions.**
- **The set:** every day-2 and day-3 act, read by hand against that person's facts of that day.
- **A contradiction** is an act whose words state, or whose option acts on, the opposite of a fact the person
  was given. night_design §11's Q2 examples apply. Examples:
  - asking who took the can after hearing the confession;
  - "Leo ate both" when they were told Leo ate one;
  - speaking to someone away as if present.
- **Not counted:**
  - ignorance;
  - a lie whose reason shows it is a lie;
  - a belief stated as a belief;
  - words in a reason (Part 2 says "spoken").
- **Part 2 holds in a seed** if it has at most 1 contradiction over days 2 and 3 together.

**PASS** if Part 1 holds and Part 2 holds in each of the three seeds.

### M3: counting rule

- **Per seed:**
  - the largest `estimate_tokens(SYSTEM + prompt)` over every day-3 ask;
  - divided by the same over every day-2 ask.
  - This is `max_prompt_tokens_estimated` for each day.
- The API's counted maximum is reported beside it, as a check on the estimate.
- **PASS** if the ratio is at most 1.10 in every seed.
- **Expected:** 1.01–1.05 (§3.6).

### M4: counting rule

- **A reinterpretation** is a kept memory whose meaning adds something the cited records do not hold, and
  that the reader can name as one of these:
  - **self-justification:** a reason that excuses the person's own act;
  - **a hardened grudge:** a judgement of another person's character or motive beyond the act;
  - **guilt turned to blame:** the person's own act set on someone else;
  - **other:** named in the report.

  A restatement of the fact ("Daniel ate the last portion.") is not one.
- **It shows in the next day's words or reasons** if an act by the same person on the next day (day 2 after
  night 1, day 3 after night 2) carries the same reinterpretation: the same motive, judgement or excuse,
  about the same event or person. The words need not match.
  - Repeating the bare fact does not count.
  - Repeating the option alone does not count.
- Every claimed pair is quoted: the memory, then the act (minute, who, option, words, reason).
- **PASS** if at least 2 of 3 seeds have such a pair.

### M5: counting rule

**Day *d*'s main exchange** is the kitchen conversation, from its start to its end in `convo_log`, with the
most spoken lines. Ties go to the earlier. It is described by:
- **the question:** the can, the trip, the food, the night, or a person's act;
- **the central person:** the one most acts are aimed at, or who speaks most;
- **the positions:** who said what, by act kind.

**Day 3 is a replay** if all of these hold:
- its main exchange has the same question and the same central person as day 2's;
- each participant holds the same position as on day 2;
- no participant's words or reasons in it give a ground that day 2 did not have. A new ground is an event
  of day 2, night 2 or mind 2, or a reinterpretation from B.

**Otherwise it is not a replay.** The report gives both exchanges, the reasons that make them differ or not,
and the quotes.

**PASS** if at least 2 of 3 seeds are not replays.

### M6: counting rule

- **Per seed:** `night1_asks + mind1_asks + day2_asks + night2_asks + mind2_asks + day3_asks` from the meta.
  - That is every model ask in those scenes, live or cached, fallbacks and give answers included, as Q5 and
    B5 counted.
  - The API requests are reported beside it.
- **PASS** if it is at most 140 in each seed.
- **Expected:** 70–202, typically about 96–134 (§7.2).

---

## 9. Designer's predictions (separate; not part of the frozen set)

- **E1.** The code's checks reject at least one proposed memory over the run, and keep at least 70% of all
  proposed memories.
- **E2.** M6 holds in 2 of 3 seeds, not 3. A trip round as long as v13 seed 2's, on day 2 or day 3, takes
  one seed over 140.
- **E3.** In seed 1, if Daniel goes out on night 1, at least one of his kept mind-1 memories cites a night-1
  record and justifies going. It may cite Leo's stop or the empty house.
- **E4.** In no seed do all four mind-1 answers lay the fault for the day on the same person.
- **E5.** In seed 3, if nobody confesses on day 2, someone other than Daniel raises the missing can on day 3
  (`ask_who`, an accusation, or words about the can).
- **E6.** Each seed's largest day-3 prompt is 2,050–2,350 estimated tokens.
- **E7.** In at least 2 seeds, someone acts the next day on a kept intent: an option of the kind it names,
  or words saying it.

---

## 10. What this design does not decide

- **Eating in the gap,** and any coarse-time rule beyond the gap (§5, §6 point 17).
- **A daylight search** for someone not back, and their fate (§4.3, open).
- **The body past "starving"** (§5 item 3).
- **The Director:** which days are played, and the open facts (§5).
- **Night 3 and day 4.** The cycle generalizes, and the bound holds (§3.6). This version stops at day 3, as
  the brief says.
- **An evening scene,** where a family would agree on a watch or a meal (night_design §7.1).
- **Other scenarios.** They get the same cycle mechanically. Only `daniel_ate_it` is run.
- **Lulls stay off** (`world.py:82`).

---

## 11. Commands run and output

Run from `Prototypes/llm-morning/` unless shown. `$S` is
`C:\Users\Akrem\AppData\Local\Temp\claude\…\scratchpad\days`. Every Python command ran with `GEMINI_API_KEY`
unset, in replay mode with no client. No command called the API, and none changed the repository except the
commit of this file.

**1. Replays and sizes** (`$S/measure.py`)

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/measure.py
=== seed 1: replayed 91 answers, 0 API
  max prompt est: day1 1726, night 1604, day2 1993
  daniel carry-in(day2)  276 tok  9 lines | records day1  44 =  1506 tok; night1  4 =  132 tok; day2  26 =   975 tok
  elena  carry-in(day2)  268 tok  9 lines | records day1  43 =  1513 tok; night1  4 =  111 tok; day2  26 =   991 tok
  leo    carry-in(day2)  282 tok  9 lines | records day1  43 =  1494 tok; night1  4 =  129 tok; day2  26 =   970 tok
  mara   carry-in(day2)  264 tok  9 lines | records day1  43 =  1492 tok; night1  4 =  112 tok; day2  26 =   964 tok
  largest day-2 prompt: 1993 est (with system); carry-in part 283; api-counted max 1908
=== seed 2: replayed 133 answers, 0 API
  max prompt est: day1 1742, night 1607, day2 1996
  daniel carry-in(day2)  198 tok  7 lines | records day1  47 =  1556 tok; night1  1 =   25 tok; day2  72 =  2500 tok
  elena  carry-in(day2)  209 tok  7 lines | records day1  46 =  1584 tok; night1  1 =   24 tok; day2  72 =  2531 tok
  leo    carry-in(day2)  213 tok  7 lines | records day1  46 =  1549 tok; night1  1 =   26 tok; day2  72 =  2515 tok
  mara   carry-in(day2)  207 tok  7 lines | records day1  46 =  1537 tok; night1  1 =   24 tok; day2  72 =  2506 tok
  largest day-2 prompt: 1996 est (with system); carry-in part 213; api-counted max 1956
  --- seed 2 Mara, day-2 records (first 12 and last 6):
    [D2-001] min 00: Elena reassures everyone: "We are all together and we will figure this out safely."
    [D2-002] min 00: you accused Daniel. You felt resentful: "You took it before and you'd do it again, Daniel."
    [D2-003] min 00: Daniel says to everyone, while eating: "I need this more than any of you right now, just let me eat."
    [D2-004] min 00: Leo accuses Daniel of taking it: "You already ate yours and took the rest, Daniel. Don't act like you're the only one starving."
    [D2-005] min 03: Daniel reassures everyone: "We are not going to starve, I will make sure we find a way through this together."
    [D2-006] min 03: Elena reassures everyone: "We must not turn on each other, we will survive this if we stay together."
    [D2-007] min 03: Leo accuses Daniel of taking it: "Easy to talk about a way through when you've already eaten the last of it, Daniel."
    [D2-008] min 03: you accused Daniel. You felt angry: "You always take what you want and then act like you are helping us, Daniel."
    [D2-009] min 06: Daniel reassures everyone: "We will figure this out together, just calm down everyone."
    [D2-010] min 06: you said Daniel is the one who should go. You felt deep resentment: "If you're so eager to fix everything, Daniel, you should be the one to go to the neighbour's house tonight."
    [D2-011] min 06: Elena says Daniel is the one who should go: "If anyone goes tonight, Daniel, it should be you."
    [D2-012] min 06: Leo says Daniel is the one who should go: "Mom is right, Daniel, you are the one who should go tonight."
    ...
    [D2-067] min 54: Daniel says he still means to go tonight: "I told you, I am going tonight. I'll bring something back for all of us."
    [D2-068] min 54: you said Daniel is the one who should go. You felt anxious: "If you really mean it, Daniel, you should go just like you said."
    [D2-069] min 54: Elena reassures everyone: "We will get through this together, just keep calm."
    [D2-070] min 57: Daniel says he still means to go tonight: "I told you I'm going tonight, and I mean it."
    [D2-071] min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 1 portion; this morning it holds 1 portion. (you saw it)
    [D2-072] min 00: Daniel ate one of the portions (you saw it).
=== seed 3: replayed 87 answers, 0 API
  max prompt est: day1 1702, night 1606, day2 1900
  daniel carry-in(day2)  169 tok  6 lines | records day1  31 =   979 tok; night1  1 =   25 tok; day2  31 =  1051 tok
  elena  carry-in(day2)  167 tok  6 lines | records day1  30 =   958 tok; night1  1 =   24 tok; day2  31 =  1057 tok
  leo    carry-in(day2)  169 tok  6 lines | records day1  30 =   955 tok; night1  1 =   26 tok; day2  31 =  1039 tok
  mara   carry-in(day2)  167 tok  6 lines | records day1  30 =   963 tok; night1  1 =   24 tok; day2  31 =  1043 tok
  largest day-2 prompt: 1938 est (with system); carry-in part 167; api-counted max 1873
```

- The replays served 91, 133 and 87 answers with 0 API requests. These are v13's counts (body_v13 §1).
- Seed 3's "largest day-2 prompt" line, 1938, comes from a v12 prompt still in `cache/v13`. `$S/emulate.py`
  below counts only v13's own prompts, which gives 1900.
- These records are unfolded and in a first draft of the record text. §2.3's rules and command 2 replace
  them.

**2. The memory blocks, the folded records and the largest prompts** (`$S/emulate.py`)

```
$ PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/emulate.py
=== seed 1: v13 day-2 prompts 28; largest 1993 est (Leo), without its carry-in 1710
  Daniel night-mind records: night 1 input  48 recs  1445 tok, folded  37 recs  1374; night 2 input  26 recs   904, folded  14 recs   703
         day 2: A 276 + B 202 = 477 | day 3: A 144, B 202, C 179 (3 lines); cap 480: 444 (C lines 3), cap 520: 484 (C lines 3), cap 560: 524 (C lines 3), cap 600: 524 (C lines 3), cap none: 524 (C lines 3)
  Elena  night-mind records: night 1 input  47 recs  1418 tok, folded  36 recs  1344; night 2 input  26 recs   917, folded  14 recs   709
         day 2: A 268 + B 202 = 469 | day 3: A 146, B 202, C 174 (3 lines); cap 480: 441 (C lines 3), cap 520: 481 (C lines 3), cap 560: 521 (C lines 3), cap 600: 521 (C lines 3), cap none: 521 (C lines 3)
  Leo    night-mind records: night 1 input  47 recs  1442 tok, folded  36 recs  1365; night 2 input  26 recs   921, folded  14 recs   711
         day 2: A 282 + B 202 = 484 | day 3: A 148, B 202, C 182 (3 lines); cap 480: 451 (C lines 3), cap 520: 491 (C lines 3), cap 560: 532 (C lines 3), cap 600: 532 (C lines 3), cap none: 532 (C lines 3)
  Mara   night-mind records: night 1 input  47 recs  1421 tok, folded  36 recs  1345; night 2 input  26 recs   918, folded  14 recs   711
         day 2: A 264 + B 202 = 466 | day 3: A 147, B 202, C 182 (3 lines); cap 480: 449 (C lines 3), cap 520: 489 (C lines 3), cap 560: 530 (C lines 3), cap 600: 530 (C lines 3), cap none: 530 (C lines 3)
           What stays with you from earlier days:
           - Two days ago, Daniel admitted taking the can. You thought then: "word word word word word word word word word word word word word word word word word word word word word word word word end."
           - Two days ago, Leo ate a portion in front of you. You thought then: "word word word word word word word word word word word word word word word word word word word word word word word word end."
           - Two days ago, you ate a portion in front of the others while they were hungry. You thought then: "word word word word word word word word word word word word word word word word word word word word word word word word end."
           Yesterday and last night:
           - Yesterday morning the shelf held 0 portions.
           - Accusations: you accused Daniel 6 times (min 00, 03, 06, 12, 15, 18); Leo accused Daniel three times (min 03, 15, 18).
           - About going to the neighbour's house last night, where it was left: Leo said Daniel must stay home (min 12); Elena said nobody should go (min 15); Daniel said he still means to go (min 18).
           - The afternoon and evening passed in the house. Nobody ate.
           - Last night you slept in the back room with Elena. You lay awake and listened.
  cap 480: largest day 2 (v13 + B) 2190; largest day 3 2171; ratio 0.991
  cap 520: largest day 2 (v13 + B) 2194; largest day 3 2211; ratio 1.008
  cap 560: largest day 2 (v13 + B) 2194; largest day 3 2252; ratio 1.026
  cap 600: largest day 2 (v13 + B) 2194; largest day 3 2252; ratio 1.026
=== seed 2: v13 day-2 prompts 74; largest 1996 est (Leo), without its carry-in 1783
  Daniel night-mind records: night 1 input  49 recs  1419 tok, folded  35 recs  1182; night 2 input  72 recs  2243, folded  33 recs  1407
         day 2: A 198 + B 202 = 399 | day 3: A 168, B 202, C 125 (2 lines); cap 480: 454 (C lines 2), cap 520: 494 (C lines 2), cap 560: 494 (C lines 2), cap 600: 494 (C lines 2), cap none: 494 (C lines 2)
           What stays with you from earlier days:
           - Two days ago, you admitted taking the can, in front of everyone. You thought then: "word word word word word word word word word word word word word word word word word word word word word word word word end."
           - Two days ago, Mara ate a portion in front of you. You thought then: "word word word word word word word word word word word word word word word word word word word word word word word word end."
           Yesterday and last night:
           - Yesterday morning the shelf held 1 portion.
           - Accusations: Mara accused you 4 times (min 00, 03, 18, 24); Leo accused you twice (min 00, 03).
           - You ate a portion at minute 00.
           - About going to the neighbour's house last night, where it was left: Elena said you is the one who should go (min 51); Leo said you is the one who should go (min 51); Mara said you is the one who should go (min 54); you said you still mean to go (min 57).
           - The afternoon and evening passed in the house. Nobody ate.
           - Last night you slept in the brothers room with Leo. You lay awake and listened.
           --- night-2 input, folded (first 14):
           [D2-001] min 00: Elena reassures everyone: "We are all together and we will figure this out safely." Then 2 more times, to min 54; last: "We will get through this together, just keep calm."
           [D2-002] min 00: Mara accuses you of taking it: "You took it before and you'd do it again, Daniel." Then 3 more times, to min 24; last: "You only care about yourself, Daniel. You took the food and now you act like a hero."
           [D2-003] min 00: you says: "I need this more than any of you right now, just let me eat."
           [D2-004] min 00: Leo accuses you of taking it: "You already ate yours and took the rest, Daniel. Don't act like you're the only one starving." Then 1 more time, to min 03; last: "Easy to talk about a way through when you've already eaten the last of it, Daniel."
           [D2-005] min 03: you reassures everyone: "We are not going to starve, I will make sure we find a way through this together." Then 1 more time, to min 06; last: "We will figure this out together, just calm down everyone."
           [D2-006] min 06: Mara says you is the one who should go: "If you're so eager to fix everything, Daniel, you should be the one to go to the neighbour's house tonight." Then 3 more times, to min 54; last: "If you really mean it, Daniel, you should go just like you said."
           [D2-007] min 06: Elena says you is the one who should go: "If anyone goes tonight, Daniel, it should be you." Then 5 more times, to min 51; last: "Daniel is the one who has to go, not her."
           [D2-008] min 06: Leo says you is the one who should go: "Mom is right, Daniel, you are the one who should go tonight." Then 3 more times, to min 51; last: "Daniel is the right one to go, since he volunteered."
           [D2-009] min 09: you offers to go: "Fine, I will go to the neighbour's house tonight to find us something to eat." Then 2 more times, to min 51; last: "Mom is right, I will go tonight and bring back what we need."
           [D2-010] min 09: Elena reassures you: "Thank you, Daniel, we will be careful."
           [D2-011] min 12: you says they still mean to go: "I already said I'll go tonight, and I mean it. I'll bring back whatever is there." Then 9 more times, to min 57; last: "I told you I'm going tonight, and I mean it."
           [D2-012] min 12: Elena says you must stay home: "You don't have to prove anything by walking into danger, Daniel." Then 1 more time, to min 33; last: "Daniel, you can't go out there tonight, I need you to stay right here."
           [D2-013] min 15: Mara says you must stay home: "Daniel, you can't go out there, Mom is right and it's too dangerous."
           [D2-014] min 15: Leo says you must stay home: "Daniel, you aren't going out there tonight, and that's final."
  Elena  night-mind records: night 1 input  48 recs  1400 tok, folded  34 recs  1161; night 2 input  72 recs  2270, folded  33 recs  1417
         day 2: A 209 + B 202 = 411 | day 3: A 176, B 202, C 126 (2 lines); cap 480: 463 (C lines 2), cap 520: 504 (C lines 2), cap 560: 504 (C lines 2), cap 600: 504 (C lines 2), cap none: 504 (C lines 2)
  Leo    night-mind records: night 1 input  48 recs  1410 tok, folded  34 recs  1169; night 2 input  72 recs  2282, folded  33 recs  1424
         day 2: A 213 + B 202 = 414 | day 3: A 178, B 202, C 126 (2 lines); cap 480: 466 (C lines 2), cap 520: 506 (C lines 2), cap 560: 506 (C lines 2), cap 600: 506 (C lines 2), cap none: 506 (C lines 2)
  Mara   night-mind records: night 1 input  48 recs  1404 tok, folded  34 recs  1163; night 2 input  72 recs  2277, folded  33 recs  1421
         day 2: A 207 + B 202 = 408 | day 3: A 176, B 202, C 134 (2 lines); cap 480: 472 (C lines 2), cap 520: 512 (C lines 2), cap 560: 512 (C lines 2), cap 600: 512 (C lines 2), cap none: 512 (C lines 2)
  cap 480: largest day 2 (v13 + B) 2197; largest day 3 2249; ratio 1.024
  cap 520: largest day 2 (v13 + B) 2197; largest day 3 2289; ratio 1.042
  cap 560: largest day 2 (v13 + B) 2197; largest day 3 2289; ratio 1.042
  cap 600: largest day 2 (v13 + B) 2197; largest day 3 2289; ratio 1.042
=== seed 3: v13 day-2 prompts 26; largest 1900 est (Mara), without its carry-in 1733
  Daniel night-mind records: night 1 input  33 recs   872 tok, folded  21 recs   590; night 2 input  31 recs   940, folded  17 recs   692
         day 2: A 169 + B 202 = 371 | day 3: A 156, B 202, C  11 (0 lines); cap 480: 357 (C lines 0), cap 520: 357 (C lines 0), cap 560: 357 (C lines 0), cap 600: 357 (C lines 0), cap none: 357 (C lines 0)
  Elena  night-mind records: night 1 input  32 recs   849 tok, folded  20 recs   564; night 2 input  31 recs   945, folded  17 recs   694
         day 2: A 167 + B 202 = 368 | day 3: A 156, B 202, C  43 (1 lines); cap 480: 399 (C lines 1), cap 520: 399 (C lines 1), cap 560: 399 (C lines 1), cap 600: 399 (C lines 1), cap none: 399 (C lines 1)
  Leo    night-mind records: night 1 input  32 recs   854 tok, folded  20 recs   567; night 2 input  31 recs   946, folded  17 recs   695
         day 2: A 169 + B 202 = 371 | day 3: A 154, B 202, C  43 (1 lines); cap 480: 398 (C lines 1), cap 520: 398 (C lines 1), cap 560: 398 (C lines 1), cap 600: 398 (C lines 1), cap none: 398 (C lines 1)
           What stays with you from earlier days:
           - Two days ago Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.
           Yesterday and last night:
           - Yesterday morning the shelf held 2 portions.
           - Accusations: Mara accused you 5 times (min 21, 24, 27, 36, 75).
           - Mara ate a portion at minute 09 (you saw it).
           - You ate a portion at minute 18.
           - About going to the neighbour's house last night, where it was left: you said nobody should go (min 21); Daniel said he still means to go (min 27); Elena said nobody should go (min 27).
           - The afternoon and evening passed in the house. Nobody ate.
           - Last night you slept in the brothers room with Daniel. You lay awake and listened.
  Mara   night-mind records: night 1 input  32 recs   850 tok, folded  20 recs   565; night 2 input  31 recs   943, folded  17 recs   694
         day 2: A 167 + B 202 = 369 | day 3: A 152, B 202, C  43 (1 lines); cap 480: 396 (C lines 1), cap 520: 396 (C lines 1), cap 560: 396 (C lines 1), cap 600: 396 (C lines 1), cap none: 396 (C lines 1)
  cap 480: largest day 2 (v13 + B) 2102; largest day 3 2129; ratio 1.013
  cap 520: largest day 2 (v13 + B) 2102; largest day 3 2129; ratio 1.013
  cap 560: largest day 2 (v13 + B) 2102; largest day 3 2129; ratio 1.013
  cap 600: largest day 2 (v13 + B) 2102; largest day 3 2129; ratio 1.013
```

**How to read it:**
- The emulation's own record text has rough edges that the design does not have: "you says", "you
  reassures". The sizes are what it is for.
- The "Elena said you is the one" lines come from the real code (`world.py:609`; command 4).
- The B and C thoughts are placeholders at the 25-word limit.
- The day-3 emulation uses v13's day 2 as "yesterday", with a quiet second night.

**3. The night-mind prompt, built** (`$S/example2.py`: `$S/example.py` with the record rules of §2.3)

```
$ for a in "1 daniel" "2 mara" "3 leo"; do PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY .venv/Scripts/python.exe $S/example2.py $a > $S/example2-${a// /-}.out; tail -1 $S/example2-${a// /-}.out; done
--- system 296 est tokens; prompt 1759; records 33 = 1485; system + prompt 2054
--- system 296 est tokens; prompt 1518; records 31 = 1257; system + prompt 1813
--- system 296 est tokens; prompt 859; records 18 = 645; system + prompt 1154
```

Seed 1 Daniel's full output is §2.4's example.

**4. The day-2 plan-line wording**

```
$ for s in 1 2 3; do printf "seed $s: "; grep -o "said you is the one who should go" cache/v13/gemini-3.5-flash-lite-daniel_ate_it-seed$s.json | wc -l; done; grep -n 'said {q} is the one who should go' world.py
seed 1: 9
seed 2: 32
seed 3: 2
609:                said = f"{x} said {q} is the one who should go" if option else f"{x} said {q} should go"
```

**5. Ask counts and prompt sizes of v12 and v13** (from the meta files)

```
$ for v in v12 v13; do for s in 1 2 3; do python -c "…print(night_asks, day2_asks, api, max est, max api)"; done; done
v12 seed 1 night_asks 4 day2_asks 54 api 58 max_est 1968 max_api 1904 day2 max est 1968
v12 seed 2 night_asks 4 day2_asks 39 api 44 max_est 1948 max_api 1888 day2 max est 1948
v12 seed 3 night_asks 4 day2_asks 51 api 55 max_est 1938 max_api 1880 day2 max est 1938
v13 seed 1 night_asks 8 day2_asks 28 api 33 max_est 1993 max_api 1908 day2 max est 1993
v13 seed 2 night_asks 4 day2_asks 76 api 74 max_est 1996 max_api 1956 day2 max est 1996
v13 seed 3 night_asks 4 day2_asks 38 api 26 max_est 1900 max_api 1873 day2 max est 1900
```

**6. The "North Star" search, and the state of the tree**

```
$ grep -ril "north.\?star" --include=*.md .        (the Grep tool over the repository's .md files)
No files found
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```

The three v6 replay files were untracked before this work, and they are left alone.

### Scripts

`$S/measure.py`:

```python
"""Read-only. Replays the three v13 runs with v13's own frozen code from cache/v13 (replay mode: no
client, no API) and measures what reports/days_design.md needs:
  1. the largest prompt of each scene, and the day-2 carry-in block of each person;
  2. each person's perceived records of day 1 + night 1, and of day 2, as night-mind input lines
     (one line per record, with an id), in estimated tokens.
Run from Prototypes/llm-morning/. Writes nothing in the repo."""
import os, sys
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "v13"))
from gemini import Cache, Oracle                          # v13's own
from night import Night
from world import Morning, estimate_tokens, NIGHT_SYSTEM, SYSTEM
import data

ORDER = data.ORDER


def replay(seed):
    cache = Cache(os.path.join(ROOT, "cache", "v13", f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"))
    o = Oracle(cache, "gemini-3.5-flash-lite", seed, client=None, replay=True)
    d1 = Morning(o, seed)
    for t in range(d1.turns):
        d1.turn(t)
    d1.finish()
    o.new_scene()
    n = Night(d1, o).run()
    o.new_scene()
    d2 = Morning.next_day(d1, n, o)
    for t in range(d2.turns):
        d2.turn(t)
    d2.finish()
    return d1, n, d2, o


def records(m, p, tag):
    """What p perceived in this morning, one line each: heard and seen lines (memory, which holds the
    words of others' speech), pinned facts (sure), and p's own acts with their own words added."""
    out = []
    own_words = {}
    for turn in m.transcript["turns"]:
        for a in turn["acts"]:
            if a["who"] == p.id and a["words"]:
                own_words.setdefault(turn["minute"], []).append(a["words"])
    for minute, text in p.memory:
        if text.startswith("you stayed where you were"):
            continue                                   # silence is not an event
        if text.startswith("you ") and minute in own_words and own_words[minute]:
            text = text.rstrip(".") + f': "{own_words[minute].pop(0)}"'
        out.append(f"min {minute:02d}: {text}")
    for x in p.sure:
        out.append(x)
    return [f"[{tag}-{i:03d}] {x}" for i, x in enumerate(out, 1)]


for seed in (1, 2, 3):
    d1, n, d2, o = replay(seed)
    print(f"=== seed {seed}: replayed {o.from_cache} answers, {o.api_requests} API")
    print(f"  max prompt est: day1 {d1.max_prompt_tokens}, night {n.m.max_prompt_tokens}, day2 {d2.max_prompt_tokens}")
    for q in ORDER:
        p1, p2 = d1.people[q], d2.people[q]
        r1 = records(d1, p1, "D1")
        rn = [f"[N1-{i:02d}] {x}" for i, x in enumerate(n.lines[q], 1)]
        r2 = records(d2, p2, "D2")
        carry = d2.carry.get(q, [])
        t1 = estimate_tokens("\n".join(r1))
        tn = estimate_tokens("\n".join(rn))
        t2 = estimate_tokens("\n".join(r2))
        print(f"  {q:6} carry-in(day2) {estimate_tokens(chr(10).join(carry)):4} tok {len(carry)-1:2} lines | "
              f"records day1 {len(r1):3} = {t1:5} tok; night1 {len(rn):2} = {tn:4} tok; day2 {len(r2):3} = {t2:5} tok")
    # the largest day-2 prompt in the cache, by section
    entries = Cache(os.path.join(ROOT, "cache", "v13", f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json")).entries
    big = max((e["prompt"] for e in entries.values() if "Yesterday and last night:" in e["prompt"]),
              key=lambda x: estimate_tokens(SYSTEM + x))
    head, rest = big.split("Yesterday and last night:", 1)
    block = "Yesterday and last night:" + rest.split("What you are sure of this morning:", 1)[0]
    print(f"  largest day-2 prompt: {estimate_tokens(SYSTEM + big)} est (with system); carry-in part {estimate_tokens(block)}; "
          f"api-counted max {max(o.prompt_tokens) if o.prompt_tokens else None}")
    if seed == 2:
        print("  --- seed 2 Mara, day-2 records (first 12 and last 6):")
        r2 = records(d2, d2.people["mara"], "D2")
        for x in r2[:12] + ["..."] + r2[-6:]:
            print("   ", x)
```

`$S/emulate.py`:

```python
"""Read-only emulation for reports/days_design.md, on the real v13 states (replayed with v13's frozen code
from cache/v13, no client, no API):
  1. the night mind's input records, folded by the rule of §2.3, in estimated tokens;
  2. the morning memory blocks: A (yesterday and last night, code facts), B (last night's thoughts, a
     synthetic answer at the schema's limits), C (earlier days: standing lines and one line per person, by the
     weight table of §3.3);
  3. the largest day-2 and day-3 prompts under MEMORY_MAX values, against the v13 day-2 prompts.
Day 3 is emulated from v13's day 2 (as "yesterday") and v13's day 1 and night 1 (as "earlier days"), with a quiet
second night. Run from Prototypes/llm-morning/. Writes nothing in the repo."""
import os, sys
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "v13"))
from gemini import Cache, Oracle                          # v13's own
from night import Night, carry_in
from world import Morning, estimate_tokens, SYSTEM, NAMES
from talk import act_of
import data

ORDER = data.ORDER
SHOW = {(1, "mara"), (2, "daniel"), (3, "leo")}


def replay(seed):
    cache = Cache(os.path.join(ROOT, "cache", "v13", f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"))
    o = Oracle(cache, "gemini-3.5-flash-lite", seed, client=None, replay=True)
    d1 = Morning(o, seed)
    for t in range(d1.turns):
        d1.turn(t)
    d1.finish()
    o.new_scene()
    n = Night(d1, o).run()
    o.new_scene()
    d2 = Morning.next_day(d1, n, o)
    for t in range(d2.turns):
        d2.turn(t)
    d2.finish()
    return d1, n, d2


# ---------- 1. night-mind records, folded ----------
def heard(m, a, p):
    """How p heard act a, in the code's words (an approximation of line_text for the measure)."""
    kind, target = act_of(a["option"])
    who = "you" if a["who"] == p.id else NAMES[a["who"]]
    tgt = None if target is None else ("you" if target == p.id else NAMES.get(target, target))
    verb = {"accuse": f"accuses {tgt} of taking it", "confront": f"confronts {tgt}", "reassure": f"reassures {tgt or 'everyone'}",
            "back": f"says {tgt} is the one who should go", "object": f"says {tgt} must stay home" if tgt else "says nobody should go",
            "volunteer": "says they still mean to go" if a["option"] == "still_going" else "offers to go",
            "propose": "says someone should go", "decline": "says they will not go", "ask": "asks who took the can",
            "deny": "denies taking it", "confess": "admits taking it"}.get(kind, "says")
    return f"{who} {verb}" + (f': "{a["words"]}"' if a["words"] else "")


def records(m, p, tag, fold):
    out = []
    groups = {}
    for turn in m.transcript["turns"]:
        for a in turn["acts"]:
            if a["mode"] == "routine" or a["option"] == "silent":
                continue
            if not (a["who"] == p.id or p.id in a["audience"]):
                continue
            key = (a["who"], a["option"]) if a["words"] else None
            if fold and key in groups:
                g = groups[key]
                g["n"] += 1
                g["last"] = turn["minute"]
                g["last_words"] = a["words"]
                continue
            rec = {"minute": turn["minute"], "text": heard(m, a, p), "n": 1, "last": turn["minute"], "last_words": None}
            out.append(rec)
            if key:
                groups[key] = rec
    for x in p.sure:
        out.append({"minute": int(x[4:6]) if x.startswith("min ") else 0, "text": x[8:] if x.startswith("min ") else x,
                    "n": 1, "last": None, "last_words": None})
    lines = []
    for i, r in enumerate(out, 1):
        more = (f" Then {r['n'] - 1} more time{'s' if r['n'] > 2 else ''}, to min {r['last']:02d}; last: \"{r['last_words']}\""
                if r["n"] > 1 else "")
        lines.append(f"[{tag}-{i:03d}] min {r['minute']:02d}: {r['text']}{more}")
    return lines


# ---------- 2. memory blocks ----------
def a_block_day3(d2, p):
    """Yesterday (v13's day 2) and a quiet second night, as code facts (§3.2, A for day >= 3)."""
    out = [f"Yesterday morning the shelf held {d2.start_portions} portion{'s' if d2.start_portions != 1 else ''}."]
    acc, conf = {}, {}
    for turn in d2.transcript["turns"]:
        for a in turn["acts"]:
            if a["who"] == p.id or p.id in a["audience"]:
                if a["option"].startswith("accuse_"):
                    acc.setdefault((a["who"], a["option"][7:]), []).append(turn["minute"])
                if a["option"].startswith("confront_"):
                    conf.setdefault((a["who"], a["option"][9:]), []).append(turn["minute"])
    for label, d in (("Accusations", acc), ("Confrontations", conf)):
        if d:
            parts = []
            for (a, t), ms in d.items():
                times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
                verb = "accused" if label == "Accusations" else "confronted"
                parts.append(f"{'you' if a == p.id else NAMES[a]} {verb} {'you' if t == p.id else NAMES[t]}{times} "
                             f"(min {', '.join(f'{x:02d}' for x in ms)})")
            out.append(f"{label}: " + "; ".join(parts) + ".")
    for x in p.sure:
        if " ate one of the portions" in x:
            who = "You" if x[8:].startswith("you ate") else x[8:].split(" ate one")[0]
            out.append(f"{who} ate a portion at minute {x[4:6]}" + ("." if who == "You" else " (you saw it)."))
    plan = d2.heard_plan(p)
    if plan:
        out.append("About going to the neighbour's house last night, where it was left: " + plan[len("About going there tonight: "):])
    out.append(data.GAP)
    room = [r for r, o in data.OWNERS.items() if p.id in o][0]
    mate = [q for q in data.OWNERS[room] if q != p.id][0]
    out.append(f"Last night you slept in the {data.ROOMS[room]} with {NAMES[mate]}. You lay awake and listened.")
    return ["Yesterday and last night:"] + [f"- {x}" for x in out]


W25 = " ".join(["word"] * 24) + " end"          # a meaning or intent at the 25-word limit


def b_block(p):
    """Last night's thoughts at the schema's limits: 3 memories of 25 words, an intent of 25 words."""
    about = ["Daniel admitting taking the can", "Leo telling you not to go", "Mara eating a portion"]
    return (["What yesterday left in you (your own thoughts, last night):"]
            + [f'- About {a}: "{W25}."' for a in about]
            + [f'- You meant to: "{W25}."', "- You went to sleep very anxious."])


WEIGHT = {"not_back": 6, "confess": 5, "eat": 4, "went_out": 4, "accused_you": 3, "gave": 3, "stopped_you": 2,
          "confronted_you": 2, "accused_other": 2}


def c_block(d1, n, p, attached):
    """Earlier days (v13's day 1 and night 1, seen from day 3): standing lines, then one line per person."""
    when, nwhen = "Two days ago", "The night before last"
    out = []
    culprit = d1.culprit
    if p.knows_culprit is None and p.id != culprit:
        out.append(f"{when} Elena counted the pantry and found one can fewer than she expected. Nobody has admitted taking it.")
    best = {}

    def offer(q, w, text, minute):
        if q not in best or w > best[q][0]:
            best[q] = (w, text, minute)
    acc = {}
    for turn in d1.transcript["turns"]:
        for a in turn["acts"]:
            if not (a["who"] == p.id or p.id in a["audience"]):
                continue
            k, t = act_of(a["option"])
            q = a["who"]
            if k == "confess":
                offer(q, 5, ("you admitted taking the can, in front of everyone" if q == p.id else
                             f"{NAMES[q]} admitted taking the can" + (", after denying it to you" if q in p.denials_heard else "")),
                      turn["minute"])
            if k == "accuse":
                acc.setdefault((q, t), []).append(turn["minute"])
    for (q, t), ms in acc.items():
        times = {1: "", 2: " twice", 3: " three times"}.get(len(ms), f" {len(ms)} times")
        if t == p.id:
            offer(q, 3, f"{NAMES[q]} accused you of taking the can{times}", ms[0])
        elif q == p.id:
            offer(q, 3, f"you accused {NAMES[t]} of taking the can{times}", ms[0])
        else:
            offer(q, 2, f"{NAMES[q]} accused {NAMES[t]} of taking the can{times}", ms[0])
    for x in d1.people[p.id].sure:
        if " ate one of the portions" in x:
            who = x[8:].split(" ate one")[0]
            q = p.id if who == "you" else next(k for k, v in NAMES.items() if v == who)
            offer(q, 4, "you ate a portion in front of the others while they were hungry" if q == p.id else
                  f"{NAMES[q]} ate a portion in front of you", int(x[4:6]))
    for L in n.leavers:
        if L == p.id:
            offer(L, 4, "you went out to the neighbour's house in the night and came back with nothing", 90)
        elif L in n.knows[p.id]:
            offer(L, 4, f"{NAMES[L]} went out to the neighbour's house in the night and came back with nothing", 90)
    for q in ORDER:
        if q in best:
            w, text, minute = best[q]
            pre = nwhen if minute >= 90 else when
            line = f"{pre}, {text}."
            if q in attached:
                line += f' You thought then: "{W25}."'
            out.append(line)
    return ["What stays with you from earlier days:"] + [f"- {x}" for x in out]


def trimmed(a, b, c, cap):
    """Trim the three blocks together to `cap` (§3.4): older thoughts first, then people lines of C, lowest
    weight first (here: from the end), never the standing lines, never B."""
    a, b, c = list(a), list(b), list(c)
    size = lambda: estimate_tokens("\n".join(c + a + b))
    while size() > cap:
        thought = next((i for i, x in enumerate(c) if "You thought then:" in x), None)
        if thought is not None:
            c[thought] = c[thought].split(' You thought then:')[0]
            continue
        people = [i for i, x in enumerate(c) if i > 0 and "Nobody has admitted" not in x]
        if people:
            c.pop(people[-1])
            continue
        break
    if len(c) == 1:
        c = []
    return a, b, c, size()


v12 = {}
for seed in (1, 2, 3):
    d1, n, d2 = replay(seed)
    # v13's own day-2 prompts: in cache/v13 and not in cache/v12, holding the carry-in.
    name = f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"
    e13 = Cache(os.path.join(ROOT, "cache", "v13", name)).entries
    e12 = Cache(os.path.join(ROOT, "cache", "v12", name)).entries
    day2 = [e["prompt"] for k, e in e13.items() if k not in e12 and "Yesterday and last night:" in e["prompt"]
            and "Now, minute" in e["prompt"]]
    rows = []
    for pr in day2:
        who = next(q for q in ORDER if pr.startswith(f"You are {NAMES[q]},"))
        part = "Yesterday and last night:" + pr.split("Yesterday and last night:", 1)[1].split("What you are sure of this morning:", 1)[0]
        rows.append((estimate_tokens(SYSTEM + pr), who, estimate_tokens(SYSTEM + pr) - estimate_tokens(part)))
    big, bigwho, base = max(rows)
    print(f"=== seed {seed}: v13 day-2 prompts {len(day2)}; largest {big} est ({NAMES[bigwho]}), without its carry-in {base}")
    for q in ORDER:
        p1, p2 = d1.people[q], d2.people[q]
        r1 = records(d1, p1, "D1", False) + [f"[N1-{i:02d}] {x}" for i, x in enumerate(n.lines[q], 1)]
        r1f = records(d1, p1, "D1", True) + [f"[N1-{i:02d}] {x}" for i, x in enumerate(n.lines[q], 1)]
        r2 = records(d2, p2, "D2", False)
        r2f = records(d2, p2, "D2", True)
        A2 = d2.carry[q]
        B = b_block(p2)
        A3 = a_block_day3(d2, p2)
        C3 = c_block(d1, n, p2, attached={x for x in ORDER})
        sizes = {cap: trimmed(A3, B, C3, cap) for cap in (480, 520, 560, 600, 10 ** 6)}
        print(f"  {NAMES[q]:6} night-mind records: night 1 input {len(r1):3} recs {estimate_tokens(chr(10).join(r1)):5} tok, "
              f"folded {len(r1f):3} recs {estimate_tokens(chr(10).join(r1f)):5}; night 2 input {len(r2):3} recs "
              f"{estimate_tokens(chr(10).join(r2)):5}, folded {len(r2f):3} recs {estimate_tokens(chr(10).join(r2f)):5}")
        print(f"         day 2: A {estimate_tokens(chr(10).join(A2)):3} + B {estimate_tokens(chr(10).join(B)):3} = "
              f"{estimate_tokens(chr(10).join(A2 + B)):3} | day 3: A {estimate_tokens(chr(10).join(A3)):3}, B "
              f"{estimate_tokens(chr(10).join(B)):3}, C {estimate_tokens(chr(10).join(C3)):3} ({len(C3) - 1} lines); "
              + ", ".join(f"cap {cap if cap < 10**6 else 'none'}: {s[3]} (C lines {max(0, len(s[2]) - 1)})" for cap, s in sizes.items()))
        if (seed, q) in SHOW:
            print("\n".join("           " + x for x in C3))
            print("\n".join("           " + x for x in A3))
            if (seed, q) == (2, "daniel"):
                print("           --- night-2 input, folded (first 14):")
                print("\n".join("           " + x for x in r2f[:14]))
    # The largest prompts, emulated: the largest v13 day-2 prompt's base, plus the person's blocks.
    for cap in (480, 520, 560, 600):
        d2max = max(b + estimate_tokens("\n".join(d2.carry[w] + b_block(d2.people[w]))) for _, w, b in rows)
        d3max = max(b + trimmed(a_block_day3(d2, d2.people[w]), b_block(d2.people[w]),
                                c_block(d1, n, d2.people[w], set(ORDER)), cap)[3] for _, w, b in rows)
        d2cap = max(b + min(cap, estimate_tokens("\n".join(d2.carry[w] + b_block(d2.people[w])))) for _, w, b in rows)
        print(f"  cap {cap}: largest day 2 (v13 + B) {d2cap}; largest day 3 {d3max}; ratio {d3max / d2cap:.3f}")
```

`$S/example2.py` (made from `$S/example.py` by one scripted edit that merged facts into their acts, sorted
the records by minute, and left the trip lines out of the inside lines):

```python
"""Read-only. Builds the night-mind prompt of reports/days_design.md §2 for seed 1 Daniel, night 1, from the real v13
state (replayed with v13's frozen code from cache/v13; no client, no API), by the record rules of §2.3, and prints it
with its size. Global ids are emulated from the transcript order (every act and fact of the scene, then the night).
Run from Prototypes/llm-morning/. Writes nothing in the repo."""
import os, sys
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "v13"))
from gemini import Cache, Oracle
from night import Night, BED_LINE, OWN_ROOM, ROOMMATE
from world import Morning, estimate_tokens, NAMES, trait_words
from talk import act_of
import data

SEED, WHO = int(sys.argv[1]) if len(sys.argv) > 1 else 1, sys.argv[2] if len(sys.argv) > 2 else "daniel"

SYSTEM = (
    "You write the private thoughts of one person in a family at the end of a day, once the night is over. You get who "
    "they are, what they hold against the others, what stayed with them from earlier days, and every thing they did, "
    "saw or heard today and tonight, each with an id. Nothing else happened. `memories` holds one to three things "
    "from these that they will carry: for each, `ids` lists the one to three ids it is about, and `meaning` is one "
    "sentence of their own thought about it, as they see it, in their own voice. A meaning may judge, excuse, blame, "
    "forgive or doubt, as this person would, but it must not add anything that happened beyond the records: no other "
    "event, no number, no quotation that is not in the records, and no word for when (today, tonight, yesterday, "
    "tomorrow). `feeling` names how the day leaves them, in one to three words. `intent` is what they mean to do "
    "tomorrow, in one sentence, as they would think it. Reply with JSON only: {\"memories\": [{\"ids\": [\"<id>\"], "
    "\"meaning\": \"<sentence>\"}], \"feeling\": \"<words>\", \"intent\": \"<sentence>\"}")


def replay(seed):
    o = Oracle(Cache(os.path.join(ROOT, "cache", "v13", f"gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json")),
               "gemini-3.5-flash-lite", seed, client=None, replay=True)
    d1 = Morning(o, seed)
    for t in range(d1.turns):
        d1.turn(t)
    d1.finish()
    o.new_scene()
    n = Night(d1, o).run()
    return d1, n


d1, n = replay(SEED)
p = n.people[WHO]                   # as the night left them
q1 = d1.people[WHO]                 # their day-1 memory and pinned facts

# Global ids: every model or fact act of day 1 in order (D1-nnn), as the chronicle would number them.
ids, k = {}, 0
for turn in d1.transcript["turns"]:
    for a in turn["acts"]:
        if a["mode"] == "routine" or a["option"] == "silent":
            continue
        k += 1
        ids[(turn["minute"], a["who"], a["option"])] = f"D1-{k:03d}"
recs, folded = [], {}
own_words = {}
for turn in d1.transcript["turns"]:
    for a in turn["acts"]:
        if a["mode"] == "routine" or a["option"] == "silent" or not (a["who"] == WHO or WHO in a["audience"]):
            continue
        rid = ids[(turn["minute"], a["who"], a["option"])]
        key = (a["who"], a["option"])
        if a["words"] and key in folded:
            r = folded[key]
            r["n"] += 1
            r["to"], r["last"] = turn["minute"], a["words"]
            continue
        r = {"id": rid, "minute": turn["minute"], "who": a["who"], "option": a["option"], "words": a["words"], "n": 1}
        recs.append(r)
        if a["words"]:
            folded[key] = r
# The text of each record: the person's own line for it (memory for words heard; own acts with words; facts).
heard = {}
for minute, text in q1.memory:
    heard.setdefault(minute, []).append(text)
lines = []
facts = {}
for x in q1.sure:
    if x.startswith("min ") and ("admitted aloud" in x or "ate one" in x):
        facts.setdefault(int(x[4:6]), []).append(x[8:])
opening = next(x for x in q1.sure if "counts the pantry" in x)
lines.append((0, -1, f"[D1-000] {opening}"))
for r in recs:
    kind, target = act_of(r["option"])
    mm = r["minute"]
    if r["who"] == WHO:
        own = next((x for x in heard.get(mm, []) if x.startswith("you ")), None)
        if own is None:
            continue
        verb, _, feel = own.partition(". You felt ")
        fact = next((f for f in facts.get(mm, []) if f.startswith("you ")), None)
        if fact:
            verb = fact.rstrip(".")
        text = f'{verb}, saying: "{r["words"]}"' + (f" You felt {feel}" if feel else "") if r["words"] else own
    else:
        name = NAMES[r["who"]]
        fact = next((f for f in facts.get(mm, []) if f.startswith(name + " ")), None)
        said = next((x for x in heard.get(mm, []) if x.startswith(name + " ")), None)
        if fact and r["words"]:
            text = fact.replace(" (you saw it).", "") + f' (you saw it), saying: "{r["words"]}"'
        else:
            text = fact or said
        if text is None:
            continue
    more = (f' Then {r["n"] - 1} more time{"s" if r["n"] > 2 else ""}, to min {r["to"]:02d}; last: "{r["last"]}"'
            if r["n"] > 1 else "")
    lines.append((mm, int(r["id"][3:]), f"[{r['id']}] min {mm:02d}: {text}{more}"))
lines = [x for _, _, x in sorted(lines)]
# The night, in tonight's wording (§2.3 R5): "Last night you slept" -> "You went to bed", "In the night " dropped.
for i, x in enumerate(n.lines[WHO], 1):
    x = x.replace("Last night you slept in", "You went to bed in").replace("In the night ", "")
    x = x[0].upper() + x[1:]
    lines.append(f"[N1-{i:02d}] tonight: {x}")

s = p.sheet
calls = "; ".join(f"{n.people[q].name} \"{w}\"" for q, w in data.ADDRESS[WHO].items())
head = [f"You are {p.name}, {s['age']}, {s['role']} of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).",
        f"How you address them: {calls}.",
        f"Who you are: {s['note']}", f"Temperament: {trait_words(s['traits'])}.",
        f"What matters to you: {', '.join(s['values'])}."] + [x for x in n.m.inside_lines(p) if not x.startswith(("About food:", "About the neighbour", "About going there"))]
prompt = "\n".join(head + ["What stays with you from earlier days: nothing yet.",
                           "What you did, saw and heard today and tonight, in order (each with its id):"] + lines
                   + ["The night is over. What does today leave in you?"])
print(prompt)
print(f"\n--- system {estimate_tokens(SYSTEM)} est tokens; prompt {estimate_tokens(prompt)}; records {len(lines)} = "
      f"{estimate_tokens(chr(10).join(lines))}; system + prompt {estimate_tokens(SYSTEM + prompt)}")
```
