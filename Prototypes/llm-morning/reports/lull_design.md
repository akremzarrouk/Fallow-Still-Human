# Design: lull moments (`daniel_ate_it`, v9)

Mode: design. No code was written or changed and no API was called. This file is the only
one this step adds. Paths are relative to `Prototypes/llm-morning/`.

**The problem.** kitchen_audit.md, item 4 and items 2 and 7, found:

- `go_*` was offered in all 414 prompts of the recorded v6/v8 runs and chosen once.
- The model is asked only when something social happens to a person or when something inside
  them rises (`world.py:785-799`). Every other decision goes to `routine()`, which never moves
  anyone (`world.py:377-384`).
- In the v6 baseline, routine made 75, 54 and 95 of the 120 decisions per morning.
- A person alone is asked again only on a new voice through a wall or an inner rise. Leo was
  alone in the brothers room from minute 66 to 87 (8 turns, 24 minutes) without a model
  decision.

**The mechanism.** A lull moment: when a room has been still for a while, a person in it who
would otherwise act by routine is asked the model instead. The prompt gets one extra line
saying how long the room has been still.

**What is compared.** `daniel_ate_it` seeds 1–3 under v9 (the current code plus lull moments)
against `runs/v6/daniel_ate_it-seed1..3`. The two differ from the first lull on.

---

## 1. When it fires

### New state

Neither piece of state is shown to the model except through the line in §2.

- **`last_stir[room]`**: the minute something was last said or done in the room.
  - It starts at `{"kitchen": 0}`, because the count at minute 00 happens there.
  - It is set to the current minute whenever someone in the room does anything other than
    **stay put and say nothing** (`silent`, `world.py:987-993`) or **stay sitting with the
    same person** (`sit_*` with `new == False`, `world.py:1055`, `world.py:1067-1068`).
  - So every spoken line stirs a room, and so do these acts: `search` and `keep_searching`,
    `go_*`, `aside_*`, `accept_aside`, `refuse_aside`, `eat`, `share`, and sitting down with
    someone new.
  - A `silent` answer from the model does not stir, whether it came from a social trigger, an
    inner moment or a lull.
  - It is updated in `apply` as each act happens, so a later actor in the same turn sees the
    stir.
  - At the end of the turn, each move sets `last_stir[destination]` to that turn's minute
    (`world.py:705-707`). Arriving is something done in the room.
- **`p.last_asked`**: the minute of the person's last model decision of any kind.
  - It is set in `ask_model` (`world.py:742-780`), so it covers social decisions, inner
    moments, go-aside answers (`world.py:808-824`) and lulls.
  - A decision whose answer was invalid (a fallback) still counts, because the model was asked.
  - It starts as `None`.

### The rule

In `decide` (`world.py:782-806`), a person's decision this turn is a **lull moment** when all
four of these hold:

1. **No social trigger.** `social_triggers(p, t)` is empty (`world.py:785`, `world.py:613-621`).
2. **No inner moment.** The inner-moment rule does not fire this turn (`world.py:790-796`).
3. **The room has been still for at least `LULL_QUIET = 9` minutes:**
   `minute - last_stir[p.room] >= 9`.
4. **The person has not been asked for at least `LULL_EVERY = 12` minutes:**
   `p.last_asked is None` or `minute - p.last_asked >= 12`.

Priority is social, then inner, then lull, then routine. A lull decision is asked through the
same `ask_model` call as the others, with the same options and the same SYSTEM text. The only
difference is the one prompt line in §2.

**Does it cover a person alone?** Yes, and nothing about it is special. A room with one person
in it stirs only when that person acts, or when someone arrives, which is also a social
trigger for them (`world.py:720-727`).

### How often it repeats

- **Per person:** at most once every 12 minutes, counted from their last model decision of any
  kind. A social decision or an inner moment resets the clock too.
- **Per room:** only while nothing stirs. If a lull decision says or does anything, the room
  stirs, and no one in it gets another lull until 9 minutes have passed with nothing happening.

### Why these numbers

**`LULL_QUIET = 9`.**

- A room stirred at minute s is still at minutes s+3 and s+6. The lull fires at s+9, which is
  the third still turn.
- **Against 6.** A room's conversation ends after `QUIET_TURNS = 2` full turns with nothing
  new, which is 6 minutes (`world.py:52`, `talk.py:98-104`). Nine minutes is one turn past that.
  At 6, a lull could land on the very turn a conversation was declared over.
- **Against the Never rule.** The target-morning "Never" item N9 needs 5 all-quiet turns in a
  row (witness_v6.md, "How each item was read"). A lull at the third still turn comes before a
  stretch reaches that length.
- **It matches `INNER_EVERY = 9`** (`world.py:53`).
- **The table.** In the simulation over the baseline (§9, command 2), Q = 6 and Q = 9 cost
  nearly the same (58/72/41 against 57/71/40). Q = 12 pushes seed 2's first lull to minute 81,
  which leaves one lull chance there instead of several.

**`LULL_EVERY = 12`.**

- **P3 holds by construction.** A person alone who was last asked at minute m acts by routine
  at m+3, m+6 and m+9, and is asked again at m+12. The room has not stirred since m+3 at the
  latest, so it has been still for 9 minutes by then (a search started at m stirs at m+3 when
  it ends).
  - The longest alone stretch without a model decision is therefore 3 turns, 9 minutes, one
    turn inside P3's 12.
  - With 15 it would be 12 minutes, exactly on P3's limit.
- **Cost.** With 9, the simulation adds 18, 10 and 23 lulls and the high estimate for seed 1
  goes over 90. With 12, every seed stays under 90 in the high estimate (§4).
- **Spacing in a group.** With four people still in a room, 12 minutes (4 turns) comes to about
  one lull per turn across the room. The room is never left entirely to routine for more than
  two turns.
- **With inner moments.** 12 ≥ `INNER_EVERY`, so a lull never lands while an inner moment is
  being held back (§3).

---

## 2. What the prompt says

**The line.** It appears only in a lull decision's prompt:

```
Nothing has been said or done in the <room> since minute <MM>.
```

- `<room>` is `data.ROOMS[p.room]`, the room name as the prompt already writes it
  (`world.py:505`).
- `<MM>` is `last_stir[p.room]` formatted `:02d`, the way the prompt writes every minute.

**Examples** from the baseline simulation (§9, command 2):

```
Nothing has been said or done in the kitchen since minute 33.        (seed 1, min 42, Mara)
Nothing has been said or done in the brothers room since minute 63.  (seed 3, min 75, Leo)
```

**Where it goes.** In the "Now" block of `prompt_for` (`world.py:505-521`):

- after the lines saying who is here, or "- Nobody else is here.", and after the portions line
  (`world.py:507-514`);
- before "Said and done in the `<room>` this turn, before you, in order:" or "You are the first
  to act in the `<room>` this turn." (`world.py:515-520`).

It is a fact about the room, so it sits with the other facts about the room at this minute.

**Why it is true by construction.** It states exactly the condition that fired it: no act
other than staying put in silence, or staying seated, since minute MM. In the same prompt,
"Said and done … this turn" can only list "`<name>` stays put and says nothing." or "`<name>`
stays sitting with …" lines (`world.py:989`, `world.py:1067`), because anything else would have
stirred the room and blocked the lull.

**It is not a reason to leave.** The line names no need, no task and no other room. It says
only how long the room has been still.

**Nothing else in the prompt changes.**

- The options, their order and their labels stay as they are (`world.py:317-375`, `world.py:522`).
- The SYSTEM text stays as it is (`world.py:27-39`).
- Every other section stays as it is.
- **One consequence.** The line is 60–70 characters, about 18 estimated tokens
  (`world.py:71-72`). In a lull prompt already near the 1,400 budget, the existing trimming
  (`world.py:529-547`) may drop one more of the oldest memory lines than it would have. That is
  the budget rule working as it always has, not a second change. Test T4 below checks the diff
  on a state with room to spare.
- **Two lines that cannot appear in a lull prompt:**
  - "Since you last decided, you have grown hungrier." cannot appear (`world.py:429-430`). That
    line needs a risen level, and a risen level with 12 or more minutes since the last model
    decision always fires an inner moment first (§3).
  - "- Nobody else is here." (`world.py:508-509`) appears only when it is already true.

---

## 3. How it interacts with the rest

**Conversations.**

- A room that has been still for 9 minutes is never "talking".
  - Every new thing that starts or feeds a conversation is also a stir: a new line
    (`world.py:895-898`), a finished search, eating or sharing (`fact()`, `world.py:973-979`),
    and an arrival (`world.py:649-650`, `world.py:728-729`).
  - A conversation ends after 2 full turns with nothing new, or with fewer than two people
    (`talk.py:91-105`).
  - So a lull never fires where the conversation rules would already be giving out social
    triggers.
- A lull answer that is new starts a conversation through the existing path (`started_by`,
  `world.py:851-852`). The mark that tells whether an inner moment started it
  (`bool(d.get("inner_kinds"))`) is left as it is. For a lull it is `False`.
- Voices through walls are unchanged (`world.py:711-719`). A new line heard from another room
  is a trigger, so that person's decision is social, not a lull.

**Inner moments.**

- **Priority.** An inner moment wins over a lull. Rule 2 means the lull is checked only when
  the inner-moment rule did not fire.
- **A lull never swallows a pending rise.**
  - `p.last_inner` is set only by inner moments, so `p.last_inner <= p.last_asked`.
  - A lull needs `minute - p.last_asked >= 12`, so `minute - p.last_inner >= 12 >= INNER_EVERY`.
  - So if anything had risen (`world.py:387-394`), the inner moment would have been allowed,
    and it would have fired instead.
  - Therefore at a lull nothing has risen, and `p.seen = seen` in `ask_model`
    (`world.py:746-749`) records the same levels it already held.
- A lull does not set `p.last_inner`. An inner moment can come on the turn after a lull, if
  something rises by then.

**Acting order.**

- Unchanged. `next_to_act` (`world.py:623-643`) orders by who was addressed or took someone
  aside, then by the feeling that shows, then by the seed's draw (`world.py:679-680`). None of
  these reads lull state, and no random number is drawn for lulls.
- As with any model decision, a lull answer sets the person's feeling (`world.py:863-865`). A
  feeling that shows can move them earlier on later turns. That is the existing rule.
- A lull answer that speaks, eats or searches puts a line in the room's list for this turn and
  triggers the people who act after it in the same turn. That is the existing path.

**Taking someone aside.** A lull decision gets the full option list, `aside_*` included when
its conditions hold (`world.py:350-356`). If it is chosen, the person asked answers through the
existing `decide_aside` (`world.py:808-824`). That is one more request, which counts toward P5.

**What is recorded.** These are outputs only, and none of them reaches a prompt:

- `d["lull"] = last_stir[room]` on the decision.
- A `"lull"` key on every transcript act (`world.py:667-673`): the still-since minute, or
  `None`.
- A story line, in the form of the inner-moment line (`story.py:67`):
  `**Lull**, nothing said or done in the <room> since minute <MM>`, plus a key line beside
  `story.py:188`.
- A meta count, `"lull_moments"`, next to `"inner_moments"` (`morning.py:97`), also printed in
  the console summary (`morning.py:106-111`).

**Housekeeping, as for v5–v7.**

- `morning.py`'s default `--out` goes from `v8` to `v9` (`morning.py:36`, `morning.py:139`).
- The current code is frozen as `v8/` with a `v8/check.py` that replays `runs/v8`, as
  `v7/check.py` does for v7. So the v8 runs stay replayable.
- This changes no behavior.

---

## 4. Request cost per morning

**Method.** `lull_sim.py` (§9, command 2) walks each v6 baseline transcript act by act and
applies the rule in §1 to every routine act.

- Up to the first lull, the v9 morning is the v6 morning (§5, T5 and T6), so **the first lull
  in each seed is exact**:

  | Seed | First lull | Model decisions before it, answered from the paired cache |
  |---|---|---|
  | 1 | min 42, Mara | 41 |
  | 2 | min 51, Elena | 53 |
  | 3 | min 15, Daniel | 10 |

- After the first lull the simulation assumes each lull answers `silent`, so the rest of the
  transcript runs as it did. That gives the number of lulls if nobody reacts.

**How a quiet decision usually goes.** The closest thing in the baseline to a lull prompt is
an inner moment with nothing social happening. There were 18 in the v6 baseline:

| Chosen | Count |
|---|---|
| silent | 5 |
| reassure_all | 4 |
| accuse_mara | 2 |
| share | 2 |
| keep_searching | 1 |
| accuse_daniel | 1 |
| ask_who | 1 |
| go_brothers_room | 1 |
| deny | 1 |

In the turn of such a moment and the next 3 turns there were on average 2.6 other model
decisions (§9, commands 3 and 4). The high estimate charges every lull 1 + 2.6 = 3.6 requests.
That over-counts, because some of those 2.6 decisions would have happened anyway.

| Seed | Baseline asks | Lulls (all silent) | Low estimate | High estimate (lulls × 3.6) | Answered from the v6 cache (the shared start) | API requests, low to high |
|---|---|---|---|---|---|---|
| 1 | 45 | 12 | 57 | 88 | 41 | 16–47 |
| 2 | 66 | 5 | 71 | 84 | 53 | 18–31 |
| 3 | 25 | 15 | 40 | 79 | 10 | 30–69 |
| **3 seeds** | 136 | 32 | 168 | 251 | 104 | **64–147** |

- **Reading the columns.** "Asks" is every model decision: cached plus live, fallbacks
  included. This is the count P5 is judged on (§6). API requests are the asks minus the cached
  answers.
- **More reuse is possible.** A lull that answers `silent` leaves the other people's prompts as
  they were: the room's list shows "`<name>` stays put and says nothing." either way
  (`world.py:989`). Only the lull-taker's own memory and the feeling they show change
  (`world.py:863-865`, `world.py:990-991`). So some later prompts can still match the v6 cache,
  and live requests can come in below the low end.
- **Hard ceiling.**
  - 150 asks per morning (config.json `max_calls_per_morning`, `gemini.py:242-244`), so 450
    for the three seeds.
  - The free quota is 500 a day. Start on a day with no other use.
- **Alternatives, from the same table:**

  | Q, G | Low estimate | High estimate |
  |---|---|---|
  | 9, 9 | 63 / 76 / 48 | seed 1 at 110, over 90 |
  | 9, 15 | 55 / 70 / 35 | 81 / 80 / 61, but P3 sits exactly on its limit |

---

## 5. Tests

All tests use the fake model or a scripted oracle, with `GEMINI_API_KEY` unset, except T6. T6
reads the committed v6 caches in replay mode, which has no client and cannot call the API
(`gemini.py:239-241`).

| # | What it checks | How |
|---|---|---|
| T1 | **The firing rule, case by case** | Scripted mornings that set `last_stir`, `last_asked` and triggers directly. (a) Room still 6 minutes, last asked 12 ago: routine. Still 9: lull. (b) Still 9, last asked 9 ago: routine. 12 ago: lull. (c) A trigger present: social, not lull. (d) A risen level with `last_inner` 12 ago: inner, not lull. (e) A person who chose `go_*` at minute m and is alone from m+3: routine at m+3, m+6, m+9, lull at m+12, next lull no earlier than m+24 if they stay silent. (f) `keep_searching` stirs, so no lull in that room the turn after. (g) A new `sit_*` stirs; staying seated does not. (h) A model `silent` (social, inner or lull) does not stir. (i) A fallback counts as asked. |
| T2 | **A still room is never talking** | Fake mornings, seeds 1–5. For every lull decision, `self.convos.active[room]` is `False`, or the room has fewer than 2 people, at the moment of the decision. |
| T3 | **The line appears only where it should** | Fake mornings. Every prompt of a decision marked `lull` contains the line exactly once, in the position of §2, with the minute equal to `d["lull"]`. No other prompt contains "Nothing has been said or done in the". The regex `^Nothing has been said or done in the (kitchen\|brothers room\|back room\|bathroom) since minute \d\d\.$` matches the whole line. |
| T4 | **Nothing else in the prompt changes** | On one state, well under budget, build the prompt with and without the lull. `difflib.ndiff` shows exactly one added line, the line of §2, and no removed line. The option ids and their order are equal (`options_for` is not touched). |
| T5 | **Nothing changes before the first lull (fake model)** | For seeds 1–5, run the fake morning with lulls off (`LULL_QUIET = None`) and on. Record every prompt sent. Both lists are equal up to the first prompt holding the line. Every transcript act before that decision is equal once the `"lull"` key is removed. |
| T6 | **The v6 baseline caches pair (real caches, no API)** | For N = 1, 2, 3, run the v9 code in replay mode on a copy of `cache/v6/gemini-3.5-flash-lite-daniel_ate_it-seedN.json`. It must stop with `CacheMiss` at the first lull prompt: seed 1 min 42 Mara, seed 2 min 51 Elena, seed 3 min 15 Daniel. It must have served 41, 53 and 10 answers from the cache before that. Every act before it must equal `runs/v6/daniel_ate_it-seedN.transcript.json` with the `"lull"` key removed. This is what lets §6 R3 pair the runs. |
| T7 | **No lull prompt says hungrier** | Fake mornings. No lull prompt contains "Since you last decided, you have grown hungrier." (§3). |
| T8 | **Alone at most 9 minutes without a model decision** | Scripted oracle that answers `go_back_room` for one person at some minute, then `silent`. Using the P3 counting rule (§6) on the transcript, the longest alone-and-routine stretch is 3 turns. |
| T9 | **Departures are still not triggers** | After a `go_*`, the people left in the room get the memory "`<name>` leaves for the `<room>`." and no trigger (`world.py:1016-1017`). The existing behavior is pinned. |
| T10 | **Recording** | `meta["lull_moments"]` equals the number of acts whose `"lull"` is not `None`. Every such act has `mode` `model` or `fallback`. The story has one "**Lull**" line per lull decision. |
| T11 | **v8 stays replayable** | `v8/check.py` replays the three `runs/v8` mornings byte for byte, with 0 API calls. |
| T12 | **The full suite** | `python -m unittest test_morning` exits 0. Any existing test whose expected fake-morning numbers change because of lulls is listed in the implementation report with its old and new values. |

---

## 6. Run plan

Run mode only, from `Prototypes/llm-morning/`, on the default model (`gemini-3.5-flash-lite`),
scenario `daniel_ate_it`, output `v9`.

**Before any API call**

- **R0. A clean start.** HEAD holds the implementation of §1–§3 and the tests of §5.
  `git status --porcelain` shows nothing tracked as modified. No `runs/v9/` or `cache/v9/`
  exists yet.
- **R1. The suite passes.** `env -u GEMINI_API_KEY .venv/Scripts/python.exe -m unittest test_morning`
  exits 0.
- **R2. The freeze and the pairing hold.** Run `.venv/Scripts/python.exe v6/check.py` and
  `.venv/Scripts/python.exe v8/check.py`: both must report IDENTICAL with 0 API calls. T6 must
  pass.
- **R3. The paired start.** For N = 1, 2, 3, copy the baseline answers:
  `cp cache/v6/gemini-3.5-flash-lite-daniel_ate_it-seedN.json cache/v9/gemini-3.5-flash-lite-daniel_ate_it-seedN.json`.
  - The cache key is model, seed, SYSTEM and prompt (`gemini.py:196-198`).
  - So every prompt identical to a baseline prompt gets the baseline's answer instead of a new
    draw at temperature 1.0. The morning is the v6 morning up to the first lull, then parts
    from there.

**Runs.** One seed at a time. The next starts only after the current one exits 0.

```
.venv/Scripts/python.exe -u morning.py --seed 1 --out v9 > runs/v9/daniel_ate_it-seed1.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 2 --out v9 > runs/v9/daniel_ate_it-seed2.stdout.txt 2>&1
.venv/Scripts/python.exe -u morning.py --seed 3 --out v9 > runs/v9/daniel_ate_it-seed3.stdout.txt 2>&1
```

An exit of 3 (quota, rate limit or call cap) is resumed with the same command once the limit
has passed (`morning.py:71-78`).

**After each run**

- **R4. Totals.** The exit code, the meta totals (`lull_moments` included) and the console
  output.
- **R5. The shared start.** The minute and person of the first lull. It must match T6: 42 Mara,
  51 Elena, 15 Daniel. The number of answers served from the cache is also reported.
- **R6. Every lull.** One row per lull: minute, person, room, still-since minute, option, words,
  reason. A `silent`/non-silent split and the options chosen are included.
- **R7. The line was true.** For every lull prompt in `cache/v9`, the line's minute equals the
  transcript's last stir in that room: the last act there that was not `silent` and not
  "stayed sitting", or the last arrival.
- **R8. The verdicts.** P1–P5 and D1–D2 below, each as a PASS/FAIL line with the evidence rows.

**What run mode delivers:**
- `runs/v9/daniel_ate_it-seed{1,2,3}.{md,transcript.json,meta.json,stdout.txt}`;
- `cache/v9/gemini-3.5-flash-lite-daniel_ate_it-seed{1,2,3}.json`;
- `reports/lull_v9.md`.

---

## 7. Predictions (frozen, verbatim from the brief)

  P1. Someone leaves the kitchen in at least 2 of 3 seeds (v6 baseline:
      1 of 3).
  P2. Two people are together in a room other than the kitchen at least
      once in at least 1 of 3 seeds (baseline: 0 of 3).
  P3. No person is alone for more than 12 in-game minutes without a model
      decision (baseline: Leo, 24 minutes).
  P4. No seed has more target-morning "Never" items than the same seed in
      the v6 baseline (3, 3, 2).
  P5. Requests per morning stay at or below 90.

All counts come from `runs/v9/daniel_ate_it-seedN.transcript.json`, `.meta.json` and `.md`. The
same script runs over `runs/v6/daniel_ate_it-seedN` for the baseline column, and the figures
below are its expected output (§9, commands 5 and 6).

### P1: counting rule

- **A seed holds P1** if at least one transcript act has `room == "kitchen"` and a non-null
  `moved_to` other than `"kitchen"`.
- That covers:
  - a `go_*` out of the kitchen;
  - an accepted aside, for both the asker, whose entry gets `moved_to` when the other comes
    (`world.py:700-701`), and the one who went (`world.py:673`).
- **PASS** if it holds in at least 2 of 3 seeds.
- **Baseline:** seed 3 only, Leo, min 63. That is 1 of 3.

### P2: counting rule

- **A seed holds P2** if either of these shows two or more people in the same room other than
  the kitchen:
  - any turn's `rooms` (occupancy at the start of the turn, `world.py:657`);
  - `final_rooms` (occupancy at minute 90, `world.py:599-600`).
- **PASS** if it holds in at least 1 of 3 seeds.
- **Baseline:** 0 of 3.

### P3: counting rule

- **Alone.** A person is alone in a turn if that turn's `rooms[<their room>]` lists only them.
- **A stretch** is a run of consecutive turns in which the person is alone and their act's
  `mode` is `routine`. Its length is the number of turns × 3 minutes. Acts with mode `model`
  or `fallback` both count as a model decision, because the model was asked.
- A stretch still running at minute 87 is counted as it stands.
- **PASS** if no stretch, for any person in any seed, is longer than 12 minutes (4 turns).
- **Baseline:** Leo, seed 3, minutes 66–87, 8 turns, **24 minutes**.
- **By design** the longest possible stretch is 9 minutes (§1), so a FAIL here means the
  implementation does not follow the design. The report says so if it happens.

### P4: counting rule

- **The sheet.** The 13 items of Docs/understanding/target-morning.md §1, scored with the
  readings of witness_v6.md, "How each item was read", unchanged. One sheet covers the six
  stories (v6 seeds 1–3 and v9 seeds 1–3) in one pass, as in witness_v8.md §P4.
- **One clarification for N9, which this mechanism creates.**
  - That reading already says "Inner moments that choose silence do not break a stretch."
  - A lull that chooses `silent` is read the same way: it does not break an all-quiet stretch.
  - A lull that does anything else breaks it, as any act does.
- **PASS** if the count for v9 seed N is at most the frozen baseline figure for seed N: 3, 3, 2.
- **The baseline is rescored in the same pass.** The rescore is shown next to the verdict, but
  the verdict uses 3, 3, 2. witness_v8.md rescored it as 3, 3, 2: seed 1 N2, N9, N11; seed 2
  N2, N9, N11; seed 3 N2, N9.
- **Borderline marks** are drafted with their quotes and stand unless the user changes them, as
  in witness_v8.md.

### P5: counting rule

- **"Requests per morning"** is the number of model asks the morning made:
  `answers_live + answers_from_cache` in the meta, fallbacks included.
- **Why not the API count.** R3's pairing serves the shared start from the cache, so
  `api_requests` understates what an unpaired morning would send. The ask count is what a
  morning costs without pairing, and it is comparable with the baseline's 45, 66 and 25.
  `api_requests` is reported beside it.
- **PASS** if the count is at most 90 in every seed.
- **Expected:** 57–88, 71–84 and 40–79 (§4).

## 8. Designer's additional predictions (not part of the frozen set)

- **D1. Most lulls are not silent.** More than half of all lull decisions across the three
  seeds choose something other than `silent`.
  - Baseline analog: quiet inner moments in the v6 baseline, 13 of 18 not silent (§4).
  - Counted from R6.
- **D2. N9 mostly disappears.** Target-morning item N9 (5 or more all-quiet turns, read as in
  P4) is absent in at least 2 of 3 v9 seeds.
  - Baseline: present in 3 of 3 (witness_v8.md sheet).
  - Counted from the P4 sheet.

## 9. Commands run and output

All read-only, from `Prototypes/llm-morning/`. `$S` is the session scratchpad. The scripts there
are not in the repository. `lull_sim.py` is reproduced at the end.

**1. The current code reproduces the v6 baseline, so the v6 caches pair with it**

`used_prompts.py` is the in-memory replay from kitchen_audit.md: no client, no files written.
```
$ for s in 1 2 3; do PYTHONDONTWRITEBYTECODE=1 env -u GEMINI_API_KEY python "$S/used_prompts.py" . v6 daniel_ate_it $s | cut -c1-120; done
{"run": "v6/daniel_ate_it-seed1", "cache_entries": 45, "prompts_used": 45, "transcript_identical": true, "per": {"Daniel
{"run": "v6/daniel_ate_it-seed2", "cache_entries": 66, "prompts_used": 66, "transcript_identical": true, "per": {"Elena"
{"run": "v6/daniel_ate_it-seed3", "cache_entries": 25, "prompts_used": 25, "transcript_identical": true, "per": {"Mara":
$ diff v6/story.py story.py && echo "story.py identical"; diff v6/gemini.py gemini.py && echo "gemini.py identical"
213a214,220   (story.py: a `knows()` helper for the witness note; for daniel_ate_it it returns the same
               "only that it is missing" / "ate it in the night; nobody saw" as v6)
gemini.py identical
```

**2. The lull simulation over the v6 baseline**
```
$ python "$S/lull_sim.py"
Q= 6 G= 9 | seed1: +20 (=65), first (39, 'elena', 'kitchen') | seed2: +14 (=80), first (48, 'mara', 'kitchen') | seed3: +23 (=48), first (12, 'leo', 'kitchen')
Q= 6 G=12 | seed1: +13 (=58), first (42, 'mara', 'kitchen') | seed2: +6 (=72), first (51, 'elena', 'kitchen') | seed3: +16 (=41), first (15, 'daniel', 'kitchen')
Q= 9 G= 9 | seed1: +18 (=63), first (42, 'mara', 'kitchen') | seed2: +10 (=76), first (51, 'elena', 'kitchen') | seed3: +23 (=48), first (12, 'leo', 'kitchen')
Q= 9 G=12 | seed1: +12 (=57), first (42, 'mara', 'kitchen') | seed2: +5 (=71), first (51, 'elena', 'kitchen') | seed3: +15 (=40), first (15, 'daniel', 'kitchen')
Q= 9 G=15 | seed1: +10 (=55), first (45, 'leo', 'kitchen') | seed2: +4 (=70), first (63, 'elena', 'kitchen') | seed3: +10 (=35), first (18, 'daniel', 'kitchen')
Q=12 G=12 | seed1: +11 (=56), first (45, 'leo', 'kitchen') | seed2: +3 (=69), first (81, 'elena', 'kitchen') | seed3: +11 (=36), first (15, 'daniel', 'kitchen')
Q=12 G=15 | seed1: +10 (=55), first (45, 'leo', 'kitchen') | seed2: +3 (=69), first (84, 'mara', 'kitchen') | seed3: +8 (=33), first (18, 'daniel', 'kitchen')
Q=15 G=15 | seed1: +6 (=51), first (48, 'elena', 'kitchen') | seed2: +3 (=69), first (84, 'mara', 'kitchen') | seed3: +5 (=30), first (18, 'daniel', 'kitchen')
$ python "$S/lull_sim.py" 9 12
Q= 9 G=12 | seed1: +12 (=57), first (42, 'mara', 'kitchen') | seed2: +5 (=71), first (51, 'elena', 'kitchen') | seed3: +15 (=40), first (15, 'daniel', 'kitchen')
seed1: [(42, 'mara', 'kitchen', 33), (42, 'leo', 'kitchen', 33), (42, 'elena', 'kitchen', 33), (45, 'daniel', 'kitchen', 33), (54, 'elena', 'kitchen', 33), (54, 'leo', 'kitchen', 33), (57, 'daniel', 'kitchen', 33), (75, 'mara', 'kitchen', 66), (84, 'daniel', 'kitchen', 75), (84, 'leo', 'kitchen', 75), (87, 'mara', 'kitchen', 75), (87, 'elena', 'kitchen', 75)]
seed2: [(51, 'elena', 'kitchen', 42), (63, 'elena', 'kitchen', 54), (81, 'elena', 'kitchen', 69), (81, 'mara', 'kitchen', 69), (81, 'leo', 'kitchen', 69)]
seed3: [(15, 'daniel', 'kitchen', 3), (18, 'mara', 'kitchen', 3), (18, 'elena', 'kitchen', 3), (27, 'daniel', 'kitchen', 3), (27, 'leo', 'kitchen', 3), (51, 'mara', 'kitchen', 42), (54, 'daniel', 'kitchen', 42), (63, 'elena', 'kitchen', 54), (72, 'daniel', 'kitchen', 63), (72, 'mara', 'kitchen', 63), (75, 'elena', 'kitchen', 63), (75, 'leo', 'brothers_room', 63), (87, 'mara', 'kitchen', 78), (87, 'elena', 'kitchen', 78), (87, 'leo', 'brothers_room', 63)]
```
Each tuple is (minute, person, room, still since). Seed 3 shows Leo alone in the brothers room
getting lulls at 75 and 87, with routine at 66–72 and 78–84 (3 turns each).

**3. What quiet inner moments chose** (the analog of a lull)
```
v6 daniel_ate_it inner moments with nothing social: 18 {'silent': 5, 'reassure_all': 4, 'accuse_mara': 2, 'share': 2, 'keep_searching': 1, 'accuse_daniel': 1, 'ask_who': 1, 'go_brothers_room': 1, 'deny': 1}
v6 daniel_ate_it_leo_heard inner moments with nothing social: 16 {'search': 5, 'silent': 4, 'ask_who': 4, 'deny': 2, 'share': 1}
v8 daniel_ate_it_leo_heard inner moments with nothing social: 19 {'silent': 5, 'search': 3, 'share': 3, 'deny': 3, 'ask_who': 2, 'accuse_leo': 2, 'accuse_daniel': 1}
```

**4. Model decisions after each quiet inner moment** (v6 baseline: the turn itself plus the next
3, the moment itself excluded)
```
('-seed1', 15, 'leo', 'keep_searching', None, 13)
('-seed1', 30, 'elena', 'reassure_all', False, 4)
('-seed1', 33, 'daniel', 'reassure_all', False, 0)
('-seed1', 54, 'mara', 'silent', None, 1)
('-seed1', 63, 'leo', 'silent', None, 1)
('-seed1', 66, 'daniel', 'reassure_all', False, 1)
('-seed1', 75, 'elena', 'reassure_all', False, 0)
('-seed2', 42, 'daniel', 'accuse_mara', False, 1)
('-seed2', 51, 'daniel', 'accuse_mara', False, 1)
('-seed2', 54, 'mara', 'accuse_daniel', False, 2)
('-seed2', 63, 'leo', 'share', False, 9)
('-seed2', 78, 'daniel', 'silent', None, 0)
('-seed3', 15, 'leo', 'silent', None, 0)
('-seed3', 30, 'elena', 'share', False, 7)
('-seed3', 33, 'daniel', 'silent', None, 5)
('-seed3', 54, 'mara', 'ask_who', False, 1)
('-seed3', 63, 'leo', 'go_brothers_room', None, 0)
('-seed3', 78, 'daniel', 'deny', False, 0)
inner moments: 18 | with a new line: 0 mean other model decisions in that turn + next 3: None | without: 18 mean: 2.6
```

**5. The shared start before the first lull**
```
seed1: first lull min 42 mara; model decisions before it (served from the v6 cache): 41; acting order that turn: ['mara', 'daniel', 'leo', 'elena']
seed2: first lull min 51 elena; model decisions before it (served from the v6 cache): 53; acting order that turn: ['elena', 'daniel', 'mara', 'leo']
seed3: first lull min 15 daniel; model decisions before it (served from the v6 cache): 10; acting order that turn: ['elena', 'mara', 'daniel', 'leo']
```

**6. The baseline figures for P1–P3**, from kitchen_audit.md, command C5:
```
runs/v6/daniel_ate_it-seed1.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it-seed2.transcript.json acts 120 moves [] final_rooms {'kitchen': ['daniel', 'elena', 'leo', 'mara']}
runs/v6/daniel_ate_it-seed3.transcript.json acts 120 moves [(63, 'leo', 'go_brothers_room', 'brothers_room', 'model')] final_rooms {'kitchen': ['daniel', 'elena', 'mara'], 'brothers_room': ['leo']}
```
The v6 seed 3 turns from minute 66 to 87 have Leo alone in the brothers room with mode
`routine` in every turn: 8 turns, 24 minutes (kitchen_audit.md, command C16).

**7. Constants, the test count, and the frozen copies**
```
$ grep -n "INNER_EVERY\|QUIET_TURNS" world.py | head
52:QUIET_TURNS = 2              # full turns with nothing new that end a conversation
53:INNER_EVERY = 9              # minutes: an inner moment at most this often per person
254:        self.convos = Conversations(data.ROOMS, QUIET_TURNS)
792:            if rose and (p.last_inner is None or minute - p.last_inner >= INNER_EVERY):
$ grep -n "def test" test_morning.py | wc -l
69
$ ls v7
__pycache__ check.py data.py gemini.py metrics.py metrics3.py metrics4.py metrics5.py morning.py story.py talk.py world.py
$ grep -n "Inner moment\|nothing social" story.py
59:  63:  (routine lines)
67:        because = "**Inner moment**, nothing social happening: " + "; ".join(d["inner"])
188:    w(f"- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has "
```

### Script: `$S/lull_sim.py`
```python
"""Read-only. Walks the v6 baseline transcripts act by act and counts where a lull moment would
fire under (Q, G): a routine act, the person's room with no stir for >= Q minutes, and >= G
minutes since the person's last model decision. A simulated lull is taken to answer `silent`
(so the rest of the transcript stays as it was); it resets the person's clock.
Stir: any act other than `silent` and other than staying seated (came_of_it "stayed sitting").
An arrival stirs the destination at the minute of the move.
    python lull_sim.py [Q G ...]"""
import json, sys

def sim(seed, Q, G, detail=False):
    tr = json.load(open(f"runs/v6/daniel_ate_it-seed{seed}.transcript.json", encoding="utf-8"))
    stir = {"kitchen": 0}
    asked = {}
    lulls, first = [], None
    for turn in tr["turns"]:
        m = turn["minute"]
        for a in turn["acts"]:
            who, room = a["who"], a["room"]
            if a["mode"] != "routine":
                asked[who] = m
            else:
                quiet = m - stir.get(room, m)
                gap = m - asked.get(who, -999)
                if quiet >= Q and gap >= G:
                    lulls.append((m, who, room, stir.get(room)))
                    asked[who] = m
                    continue          # simulated answer: silent, no stir
            if a["option"] != "silent" and not a["came_of_it"].startswith("stayed sitting"):
                stir[room] = m
            if a.get("moved_to"):
                stir[a["moved_to"]] = m
    return lulls
# ... prints one line per (Q, G) as in command 2, and the per-seed lists when given one pair
```
