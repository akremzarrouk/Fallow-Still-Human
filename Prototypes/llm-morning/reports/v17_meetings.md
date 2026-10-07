# v17: why the meetings after the morning replay the morning's quarrel

Mode: investigate. Read only: no code changed, no API called, `runs/v17` and `cache/v17` not written. Paths are
relative to `Prototypes/llm-morning/`.

**Sources:**
- **The day-3 prompts and answers** come from a no-API replay of v17 seeds 1–3, from a temp copy of `cache/v17`
  (`runs/v17_meetings/scripts/replay_v17.py`).
  - The replayed stories are byte-identical to `runs/v17/*.md`, with 0 live answers. `cache/v17`'s sha256s were
    the same after (§6).
  - The replay also recorded every grudge after each played turn, which no v17 file holds.
- **Extracts** are in `runs/v17_meetings/`: `prompts/seed{1,2,3}_first_q2.txt` (the three full prompts and their
  answers), `asks.txt` (every ask after the morning, its options and choice), `kinds.txt`, `grudges.txt`,
  `trip_lines.txt`, `meeting_first_acts.txt`.

**"After the morning"** means from `day3.quiet.morning_end` on: min 18, min 09 and min 18. That gives 62 asks: 18, 28
and 16.

## 1. The first Q2 ask of each seed

| Seed | Asked | Minute | Q2 entry (`runs/v17/daniel_ate_it-seedN.md`, "After the morning") | Full prompt |
|---|---|---|---|---|
| 1 | Mara | 10:39 | "Daniel comes into the kitchen, where Mara is (their last line at min 15; Daniel holds 1, Mara holds 3): Mara is asked." | `prompts/seed1_first_q2.txt` (79 lines + answer) |
| 2 | Mara (Leo also asked, after her) | 10:18 | "Daniel comes into the kitchen, where Mara is (their last line at min 06; Daniel holds 0, Mara holds 3): Mara is asked." | `prompts/seed2_first_q2.txt` (89 lines) |
| 3 | Leo (Mara also asked, after him) | 10:48 | "Daniel comes into the kitchen, where Leo is (their last line at min 15; Daniel holds 2, Leo holds 3): Leo is asked." | `prompts/seed3_first_q2.txt` (88 lines) |

### 1.1 How the meeting is described

**A line saying that Daniel came in: NOT FOUND in any of the three prompts.** Daniel's arrival appears only as his
presence and his act this turn:
- **Seed 1**, lines 55–61: "Now, 10:39, you are in the kitchen." / "- Daniel is here, talking." / "- Elena is here,
  talking." / "Said and done in the kitchen this turn, before you, in order:" / "1. Daniel reassures everyone: "We
  are going to be fine, I promise you both that I am looking after us."" / "2. Elena reassures everyone: …"
- **Seed 2**, lines 59–65: "Now, 10:18, you are in the kitchen." / "- Daniel is here, talking." / "- Elena is here,
  sitting in the kitchen." / "- Leo is here, sitting in the kitchen." / … / "1. Daniel reassures everyone: "We are
  going to make it through this together, I promise you. Just stay calm.""
- **Seed 3**, lines 58–64: "Now, 10:48, you are in the kitchen." / "- Daniel is here, talking." / "- Elena is here,
  sitting in the kitchen." / "- Mara is here, sitting in the kitchen." / … / "1. Daniel reassures everyone: "We are
  going to figure this out, I promise you all.""

**Why the arrival is missing**, from the code:
1. **Q2's text is not shown.** It is "Daniel comes into the kitchen" (`quiet.py:386`). It is queued as the ask's
   trigger text (`quiet.py:246`) and put first among that person's triggers (`world.py:1371`).
   - `prompt_for` and `prompt_parts` (`world.py:973`–`1069`) never read triggers: "trigger" does not occur in
     that range (§6, command 4).
   - Triggers only decide whether the model is asked (`world.py:1392`).
2. **The memory line is cut.** The arrival is also written to each awake person there as a memory line, "Daniel comes
   into the kitchen." (`quiet.py:353`), at the meeting's minute.
   - Memory lines at the current minute are left out: `morning = [... for m, x in p.memory if m != minute]  # this
     turn is above` (`world.py:1026`).

**What the "this morning" blocks end with, just before "Now":**
- **Seed 1**, lines 41–54: "Your own last words this morning: - min 09, you confronted Daniel. - min 12, you
  accused Daniel. - min 15, you accused Daniel."
  - Then: "What else happened this morning", ending "min 15: you accused Daniel. You felt resentful." / "min 18:
    Daniel goes to the brothers room." / … / "10:36: you got up from your bed." / "10:36: you went to the kitchen."
- **Seed 2**, lines 45–58: own last words "min 00, you confronted Daniel." / "min 03, …" / "min 06, …". Then the
  min 09 moves, "09:33: you got up from your bed.", and "09:33: you went to the kitchen."
- **Seed 3**, lines 44–57: own last words "min 09, you accused Daniel." / "min 12, you confronted Daniel." / "min 15,
  you confronted Daniel."
  - Then: "min 15: Mara confronts Daniel: "Daniel, you snuck out last night and brought back nothing. Why did you
    risk everything for nothing?"" / … / "10:18: you got up from your bed." / "10:18: you went to the kitchen."
- **Between the morning's end and the meeting**, the only memory lines are the routine ones: going, lying down,
  getting up.

### 1.2 What comes first in each prompt

The order is the same in all three, line by line:

| Section | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| "You are …", the person | 1–5 | 1–5 | 1–5 |
| "Your body: …" | 6–7 | 6 | 6 |
| "About the can: …", about food, the neighbour's house | 8–10 | 7–9 | 7–9 |
| **"Against Daniel (a lot): …"** | **11** | **10** | **10** |
| The house | 13 | 11 | 11 |
| The days before, earlier days, yesterday and last night, last night's thoughts | 14–38 | 12–42 | 12–41 |
| What you are sure of, own last words, what else happened | 39–54 | 43–58 | 42–57 |
| "Now, …" | 55 | 59 | 58 |
| Options | 62–79 | 66–89 | 65–88 |

**The grudge lines, quoted** (written by `world.py:926`):
- **Seed 1**, line 11: "Against Daniel (a lot): you were angry with Daniel this morning at minutes 06, 09, 12 and
  15."
- **Seed 2**, line 10: "Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying
  it to you at minute 06; you were angry with Daniel last night; and this morning at minutes 00, 03 and 06."
- **Seed 3**, line 10: "Against Daniel (a lot): yesterday, Daniel accused you of taking the can at minute 27, and
  you had not; … yesterday, Daniel had accused you of it at minute 30; you were angry with Daniel this morning at
  minutes 06, 09, 12 and 15."

**The first act of each meeting.** In the first played turn of every triggered stretch, the act decided first was
Daniel's, in 8 of 10. The two others start with a routine `silent` of Elena's: seed 2 at 15:24 and seed 3 at
16:54 (`runs/v17_meetings/meeting_first_acts.txt`, from the transcripts' `decided_at`).
- **The first meetings:** seed 1 at 10:39, Daniel `reassure_all`; seed 2 at 10:18, Daniel `reassure_all`; seed 3 at
  10:48, Daniel `reassure_all`.
- **How the order is chosen:** `next_to_act` (`world.py:1153`). Someone just addressed or taking someone aside goes
  first, then the strongest feeling shown, then the seed's draw. The reason for each turn is kept in the turn log
  (`order_reason`), and it is NOT FOUND in the transcripts.

**The answers to these three prompts** (end of each prompt file):

| Seed | Answer |
|---|---|
| 1 | Mara `accuse_daniel`: "You keep promising things while we starve, Daniel, but you're the one who took the food." |
| 2 | Mara `accuse_daniel`: "You went out into the night and came back with nothing, Daniel. Why did you even go?" |
| 3 | Leo `confront_daniel`: "Empty promises don't feed anyone, Daniel. Especially after you snuck out last night against everyone's word." |

## 2. Options offered and chosen, every ask after the morning

From `runs/v17_meetings/kinds.txt`, grouped by `talk.act_of` kind (`talk.py:13`). Per ask: `runs/v17_meetings/asks.txt`.

| Kind | Asks offering it (of 62) | Options of that kind offered | Times chosen |
|---|---|---|---|
| confront | 61 | 149 | 27 |
| reassure (`reassure_<q>` and `reassure_all`) | 54 | 165 | 23 |
| accuse | 40 | 40 | 8 |
| silent | 62 | 62 | 3 |
| go | 62 | 186 | 1 |
| back (`send_<q>`) | 61 | 149 | 0 |
| propose (`propose_trip`) | 61 | 61 | 0 |
| say (`say_other`) | 61 | 61 | 0 |
| sit | 61 | 149 | 0 |
| volunteer | 61 | 61 | 0 |
| aside | 44 | 76 | 0 |
| deny | 40 | 40 | 0 |

**Who chose what, and at whom:**

| Seed | Chosen options |
|---|---|
| 1 | `reassure_all` 6, `accuse_daniel` 5, `confront_daniel` 2, `confront_mara` 2, `reassure_mara` 1, `go_kitchen` 1, `silent` 1 |
| 2 | `confront_daniel` 11, `reassure_all` 6, `reassure_leo` 6, `accuse_daniel` 3, `confront_leo` 1, `silent` 1 |
| 3 | `confront_daniel` 7, `confront_leo` 3, `reassure_all` 2, `reassure_daniel` 2, `confront_mara` 1, `silent` 1 |

**Who offered what:** `accuse` was offered only to Elena, Leo and Mara, and only `accuse_daniel`: `if p.confessed or
(p.knows_culprit and p.id != p.knows_culprit and q.id != p.knows_culprit): continue` (`world.py:500`). `deny` was
offered to the same 40: `if p.heard_question and not p.confessed` (`world.py:497`).

## 3. Option kinds in the code that were never offered after the morning

The kinds come from `world.py` `options_for` (`world.py:487`), `trip_options` and `trip_options_day2`
(`world.py:554`, `world.py:584`), `food_options` (`world.py:776`), `decide_given` (`world.py:810`) and
`decide_aside` (`world.py:1413`).

| Kind (option ids) | The condition that hid it | The state in v17's day 3 |
|---|---|---|
| ask (`ask_who`) | `if not p.knows_culprit:` (`world.py:493`) | Offered in 0 of 120 day-3 asks. Elena, Leo and Mara's prompts say "About the can: Daniel admitted taking it …"; Daniel's say "About the can: you ate it yourself, and you admitted it two days ago." (seeds 1, 2) and "… yesterday." (seed 3). |
| confess (`confess`) | `if p.id == self.culprit and not p.confessed:` (`world.py:504`) | Daniel has confessed (same line). |
| deny, for Daniel | `if p.heard_question and not p.confessed:` (`world.py:497`) | Daniel has confessed. Offered to the other three. |
| accuse, for Daniel | `if p.confessed or …: continue` (`world.py:500`) | Daniel has confessed. |
| search, keep_searching | `settled = p.confessed or (p.knows_culprit and p.knows_culprit != p.id)` (`world.py:535`) | Everyone is settled. |
| eat, share | `if p.room == "kitchen" and self.portions > 0:` (`world.py:544`) | "About food: the shelf holds 0 portions …" in all 62 prompts (`trip_lines.txt`). |
| A food moment: eat, `give_<q>`, share | `food_due`: `self.portions <= 0 … return False` (`world.py:765`) | 0 portions. |
| eat_given, refuse_given | `decide_given`, only for someone handed a portion (`world.py:810`) | Nobody gave a portion: `give` was never offered. |
| accept_aside, refuse_aside | `decide_aside`, only for someone taken aside (`world.py:1413`) | `aside` offered 76 times, chosen 0 (§2). |
| still_going (volunteer kind) | `if own != ("volunteer", None): … else: still_going` (`world.py:595`–`598`); `own` comes from `p.trip_heard` | `p.trip_heard … = {}` at each next day (`night.py:848`). No trip position was taken on day 3 in any seed (§6, command 7). |
| nobody_goes | `if p.trip_raised and own != ("object", None):` (`world.py:603`) | `p.trip_raised = False` at each next day (`night.py:848`). It is set only by a propose, volunteer or back act (`world.py:1634`–`1635`), and there were none. |
| `keep_<q>_home` | `self.named_to_go(p, q.id)` (`world.py:606`), which reads `p.trip_heard` | Empty, as above. |
| refuse_to_go (decline) | `if (backed or own == ("volunteer", None)) …` (`world.py:609`–`610`) | Nobody backed or volunteered. |
| Day 1's trip forms (`back_<q>`, `object_trip`, `object_<q>`, `decline`) | `if self.day != 4: return self.trip_options_day2(…)` (`world.py:559`) | Day 3 is house day 6. |

## 4. Grudges: 07:00, each meeting, 21:00

From `runs/v17_meetings/grudges.txt`.
- **"07:00"** is after `next_day`, before any turn. **"At a meeting"** is after every played turn before it.
- Each meeting's levels agree with the `grudges` that quiet.py's Q2 entry recorded.
- Grudges at 0 all day are left out.

**Seed 1:**

| Holder → target | 07:00 | 10:39 Q2 | 11:00 Q2 | 13:00 Q2 | 21:00 |
|---|---|---|---|---|---|
| Daniel → Leo | 0 | 1 | 0 | 0 | 0 |
| Daniel → Mara | 0 | 1 | 1 | 3 | 3 |
| Leo → Daniel | **3** | **3** | **3** | **3** | **3** |
| Mara → Daniel | **3** | **3** | **3** | **3** | **3** |
| Mara → Leo | 2 | 1 | 0 | 0 | 0 |

**Seed 2:**

| Holder → target | 07:00 | 10:18 Q2 | 10:27 Q1 | 12:18 Q2 | 15:24 Q2 | 21:00 |
|---|---|---|---|---|---|---|
| Daniel → Leo | 0 | 0 | 0 | 0 | 1 | 0 |
| Leo → Daniel | **3** | **3** | **3** | **3** | **3** | **3** |
| Mara → Daniel | **3** | **3** | **3** | **3** | **3** | **3** |

**Seed 3:**

| Holder → target | 07:00 | 10:48 Q2 | 12:48 Q2 | 16:54 Q2 | 21:00 |
|---|---|---|---|---|---|
| Daniel → Leo | 1 | 2 | 1 | 3 | 2 |
| Daniel → Mara | 0 | 0 | 0 | 0 | 1 |
| Leo → Daniel | **3** | **3** | **3** | **3** | **3** |
| Leo → Mara | 1 | 0 | 0 | 0 | 0 |
| Mara → Daniel | **3** | **3** | **3** | **3** | **3** |
| Mara → Leo | 1 | 0 | 0 | 0 | 0 |

**Every change on day 3,** by the played minute it came in (`grudges.txt`, "changes"):
- **Seed 1:**
  - min 03: Daniel → Leo 0 → 1;
  - min 06: Daniel → Mara 0 → 1;
  - min 15: Mara → Leo 2 → 1 (fell);
  - 10:39: Daniel → Leo 1 → 0, Daniel → Mara 1 → 0, Mara → Leo 1 → 0 (all fell);
  - 10:45, 11:00, 11:03: Daniel → Mara 0 → 1 → 2 → 3.
- **Seed 2:** 12:24, Daniel → Leo 0 → 1; 15:24, Daniel → Leo 1 → 0 (fell).
- **Seed 3:**
  - min 06: Daniel → Leo 1 → 2;
  - min 15: Leo → Mara and Mara → Leo 1 → 0 (fell);
  - 10:48: Daniel → Leo 2 → 1 (fell);
  - 12:48, 12:51: Daniel → Leo → 2 → 3;
  - 16:54: Daniel → Leo 3 → 2 (fell), Daniel → Mara 0 → 1.
- **Every rise was an `angry_at` answer.** No event rise happened on day 3.
- **Leo's and Mara's grudges against Daniel did not change** in any seed.

**What changes a grudge during a day, in the code:**

| Change | Code | When |
|---|---|---|
| Rise by one, up to 3 | `Grudge.rise` (`world.py:217`) | Called by `take_answer` when an answer names someone as `angry_at` (`world.py:1344`). Also by `add_grudge` (`world.py:868`) for events the rules see: a false accusation (`world.py:1587`); a confession after a denial or an accusation (`world.py:1570`–`1579`); eating in front of a hungry person (`world.py:1771`–`1775`, `world.py:1824`–`1828`). |
| Fall by one | `Grudge.may_fall` (`world.py:226`): only if `minute - self.last_change >= FALL_EVERY`, which is 15 (`world.py:81`) | Called only in `take_answer`, for each grudge whose target is not that answer's `angry_at`: `if t != angry and t in p.grudges and p.grudges[t].may_fall(minute)` (`world.py:1348`). |
| `last_change` set to 0 | `night.py:844` | At each next day; the strength is kept. |
| A fall with time alone, or in quiet mode | NOT FOUND | `quiet.py` only reads `strength` (`quiet.py:362`–`364`, `quiet.py:571`). |

**`angry_at` in every day-3 answer of Leo and Mara** (§6, command 6):
- seed 1: Mara 11 of 11 "Daniel", Leo 7 of 7;
- seed 2: Leo 12 of 12, Mara 9 of 9;
- seed 3: Mara 9 of 9, Leo 11 of 11.

**Who Q2 asks:** "The holder of the higher grudge is asked, B on a tie": `asked = a if ga > gb else b`
(`quiet.py:369`). Q2 fires at a grudge of 2 or more (`quiet.py:38`, `quiet.py:364`).

## 5. The trip question in the afternoon

**Is it open?** Yes, in every day-3 ask.
- `next_day` sets `m.trip = {"minute": 0, "why": ["carried over from yesterday"], "asked": []}` (`night.py:809`).
- `trip_options` returns no position only `if self.trip is None` (`world.py:557`).
- So `propose_trip`, `volunteer` and `send_<q>` were offered in 61 of the 62 asks after the morning (§2). They were
  chosen 0 times.

**Which trip options were offered:** `propose_trip`, `volunteer` and `send_<q>`. `still_going`, `nobody_goes`,
`keep_<q>_home` and `refuse_to_go` were not, for the reasons in §3.

**What the prompts say about tonight** (`runs/v17_meetings/trip_lines.txt`: every distinct line, with how many of
the 62 asks carry it):
- **A line "About going there tonight:"** (`heard_plan`, `world.py:642`, added by `trip_lines`, `world.py:671`):
  NOT FOUND in any of the 120 day-3 prompts.
  - `heard_plan` returns None when `p.trip_heard` is empty, and `night.py:848` empties it each next day.
- **The house line**, all 62: "Outside, and not to be gone to this morning: the street and the neighbour's house."
  - This is `HOUSE_THINGS_AFTER_TRIP` (`data.py:144`), chosen when `self.trip` is set (`world.py:993`).
- **About food**, all 62: "About food: the shelf holds 0 portions, and there is no other food in the house, so there
  is nothing to eat today."
- **The neighbour's house**, one line per person, as the night left it. For example:
  - "About the neighbour's house: Daniel went there last night and came back with nothing. Outside is dangerous."
    (23 asks, seeds 2 and 3);
  - "… you went in last night and found no food there." (15, Daniel, seeds 2 and 3);
  - "… its people left in the first days, so there may be food there." (6, Elena, seeds 2 and 3).
- **Yesterday's plan, in block A**, where the person heard one. Seed 2, Mara, 6 asks: "About going to the neighbour's
  house last night, where it was left: you said Daniel is the one who should go (min 06); Leo said Daniel is the one
  who should go (min 06); Daniel said he still means to go (min 09); Elena said nobody should go (min 12)." Each
  seed has one such line per person (`trip_lines.txt`).
- **The backstory line**, 62 asks: "- Day 2: Daniel says they should cross to the neighbour's house tonight and see
  what is left there."
- **The only "tonight" in the option labels:** `propose_trip`, "say someone should go to the neighbour's house
  tonight"; `volunteer`, "offer to go there tonight yourself"; `send_<q>`, "say <q> is the one who should go there
  tonight".

## 6. Commands and output

From `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset.
```
$ sha256sum cache/v17/*.json > $S/v17cache.sha                       ($S: the session scratchpad)
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/v17_meetings/scripts/replay_v17.py runs/v17_meetings/replay
daniel_ate_it-seed1: day-3 asks 40; live 0; story identical to runs/v17: True      (seeds 2 and 3: the same)
$ sha256sum -c $S/v17cache.sha                                        # seed1, seed2, seed3: OK
```

1. **The three prompts** (asks #24, #13 and #25 of day 3), written with their answers to
   `runs/v17_meetings/prompts/`. `wc -l`: 89, 99, 98.
2. **`runs/v17_meetings/scripts/asks.py asks > asks.txt`:** "asks after the morning: 62".
3. **`asks.py kinds > kinds.txt`:** the §2 tables (its last line is the chosen options by seed).
4. **Triggers in the prompt code:** `awk` over `world.py` from `def prompt_for` (line 973) to `def social_triggers`
   (line 1143), printing lines with "trigger". Output: none. The defs in that range: 973 `prompt_for`, 1020
   `prompt_parts`, 1070 `parse`, 1108 `run`, 1114 `finish`.
5. **`asks.py trip > trip_lines.txt`;** a count of "About going there tonight" in the day-3 prompts:
   "day-3 prompts with About going there tonight: 0 of 120".
6. **`PYTHONIOENCODING=utf-8 … grudges.py > grudges.txt`** (the §4 tables and changes); and `angry_at` of Leo's and
   Mara's day-3 answers:
   ```
   seed 1 day-3 angry_at of Leo and Mara: {('Mara', 'Daniel'): 11, ('Leo', 'Daniel'): 7}
   seed 2 day-3 angry_at of Leo and Mara: {('Leo', 'Daniel'): 12, ('Mara', 'Daniel'): 9}
   seed 3 day-3 angry_at of Leo and Mara: {('Mara', 'Daniel'): 9, ('Leo', 'Daniel'): 11}
   ```
7. **Trip acts on day 3, `ask_who`, and Daniel's can line:**
   ```
   seed 1: day-3 trip acts []; ask_who offered in 0 of 40 day-3 asks; Daniel's can lines ['About the can: you ate it yourself, and you admitted it two days ago.']
   seed 2: day-3 trip acts []; ask_who offered in 0 of 40 day-3 asks; Daniel's can lines ['About the can: you ate it yourself, and you admitted it two days ago.']
   seed 3: day-3 trip acts []; ask_who offered in 0 of 40 day-3 asks; Daniel's can lines ['About the can: you ate it yourself, and you admitted it yesterday.']
   ```
8. **The first acts of each triggered stretch** (from `decided_at`; written to `meeting_first_acts.txt`).
