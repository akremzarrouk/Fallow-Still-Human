# Repetition audit: repeated sentences, and whether the speaker could see them

Investigation, read-only. No API was called. Date: 2026-09-29. Paths are relative to
`Prototypes/llm-morning/`. `world.py:N` citations are to the current code (HEAD `342005f`).

**Which code made which runs.**

| Runs | Code |
|---|---|
| `runs/v6` | `v6/` |
| `runs/v8` | `v8/` |
| `runs/v9` | the current code with `LULL_QUIET = 9`, as it was at `1c50d44` |

Everything cited below (own words, trimming, the pattern block, the repeat filter, the request
settings) is the same in all three. The v6→current diffs touch only the "About the can" line
and the lull code (kitchen_audit.md, command C3; lull_impl.md, diff).

**Every prompt in item 5 is exact.** Each of the 12 runs (v6 ×6, v8 ×3, v9 ×3) was replayed in
memory from its own cache with the code that made it, with no client and no files written.
Every replayed transcript equals the saved one (command 1), so each decision is paired with the
prompt it was actually sent.

---

## 1. What of a person's own earlier words reaches their prompt

There are two places, and only one of them is protected from trimming.

**(a) "Your own last words this morning:" (pinned, never trimmed)** — `world.py:541-542`

- **What it holds:** the person's last **3** spoken lines, whatever their age:
  `p.said_lines[-3:]`.
- **Format** (`world.py:987`): `min MM, you <verb>: "<words>"`. `<verb>` is from `mine`
  (`world.py:983-985`): "asked who took it", "denied taking it", "accused <name>", "admitted
  taking it", "reassured <name/everyone>", or "said".
- **Why it is never trimmed:** it is part of `pinned` (`world.py:540-542`). The trimming loop
  only removes items from `morning` and `back` (`world.py:554-561`).
- **In the 12 runs:** 503 of the 581 prompts sent had this block, showing 1,250 own lines
  (command 3).

**(b) "What else happened this morning, most recent last:" (trimmed first)** — `world.py:539`,
`world.py:546-548`

- **What it holds:** every memory entry except the current minute's. Each spoken line of the
  person's own is stored as `you <verb>: "<words>". You felt <feeling>.` (`world.py:986`).
- **The trimming order when over 1,400 estimated tokens** (`world.py:551-561`):
  1. memory, oldest first, down to 8 entries;
  2. then backstory down to 4 lines;
  3. then the rest of memory, oldest first;
  4. then more backstory.
- A cut adds the marker `- (earlier things, left out here)` (`world.py:547`).
- **In the 12 runs:** 541 of 581 prompts carry the marker. Memory lines kept per prompt: min 0,
  median 2, max 8 (command 3).

**Elsewhere:**
- The `sure` list (`world.py:540`) holds a person's own act only for a confession, as "you
  admitted aloud that you took the can" without the words (`world.py:992-993`). No repeated
  sentence in item 5 is a confession.
- The "What you have been doing" block (item 4) gives the **kind** of their recent acts, never
  their words.

## 2. What of others' reactions to those words reaches their prompt

**Where others' reactions can appear:**

| Source | Where | What it says |
|---|---|---|
| Others' spoken lines, in full, as memory | `perceive`, `world.py:853-857`, called from `world.py:938` with `line_text` (`world.py:859-875`) | For example `Daniel denies taking it, to everyone: "<words>"`. These are subject to the same trimming as (b) above: median 2 memory lines kept. |
| Lines said earlier in the same turn | "Said and done in the <room> this turn, before you, in order:" (`world.py:529-532`), from `so_far` (`world.py:934`) | Never trimmed, but it covers the current turn only. |
| A face | `- <name> is here, <activity>. <name> looks <feeling>.` (`world.py:522-524`) | Only for a feeling that shows (the `SHOWN` stems), for `FEELING_SHOWS_FOR_TURNS = 3` turns (`world.py:54`, `world.py:891`, `world.py:301`). The prompt does not connect it to any line. |
| A summary of replies | The pattern block, "In that time: …" (`world.py:469-494`) | Replies **by kind** since the start of the person's current run of same-kind acts ("Daniel denied taking it, then denied taking it"). Not the words (`world.py:496-501`). See item 4. |

**What does not reach the prompt:**
- The social triggers are used only to decide whether the model is asked
  (`world.py:627-635`). They are not printed in the prompt.
- Whether a line counted as "new" (`talk.py:45-66`) is not in the prompt.

**At the 54 repeat instances of item 5:**
- The last column of the table counts other people's spoken lines in that prompt dated after
  the speaker's previous instance: memory lines with a later minute, plus this turn's "Said and
  done" lines.
- The counts were: 0 in 9 instances, 1 in 12, 2 in 25, 3 in 7, 4 in 1 (command 5).

## 3. The repeat filter

**The rule.** `world.py:381-385`:

```python
        # A speech act used three turns in a row is not offered a fourth time.
        kind, n = self.repeating(p)
        if kind in SPEECH and n >= 3:
            opts = [o for o in opts if act_of(o.id)[0] != kind]
```

- `repeating` (`world.py:317-326`) counts the person's **latest acts in a row with the same
  kind**, from `p.history`.
- `p.history` gets **every** act, routine ones included (`world.py:899`, in `apply`).
- The kind is from `act_of` (`talk.py:11-26`): `reassure_all` and `reassure_<x>` are both
  `reassure`, `accuse_<x>` is `accuse`, `say_other` is `say`.
- `SPEECH` is ask, deny, accuse, confess, reassure and say (`talk.py:8`).
- When the filter applies, the decision records `held_back` (`world.py:805`).

**What it does not catch**, from the rule itself and the item 5 data:

1. **Words.** It compares kinds, never words. No code compares a new line's words with earlier
   lines: NOT FOUND. `Newness` (`talk.py:45-66`) compares kinds and targets. A reassurance is
   always "not new"; a repeated question is "a question they had asked before".
2. **Anything with a gap.** Any other act in between, including a routine `silent`, resets the
   count. In 36 of the 54 later instances the person's act just before was of a different kind
   (0 in a row). Examples:
   - v9 seed 2, Elena, min 51: her previous three acts were routine `silent`. The pattern block
     said "you have stayed put and said nothing, 3 turns in a row".
   - v9 seed 2, Elena, min 81: "4 turns in a row" of silence.
3. **The first three in a row.** The fourth is removed, not the second or third. 5 of the
   later instances had 2 same-kind acts just before them (the third in a row). 13 had 1
   (command 5).
4. **A switch of kind with the same words.** This does not occur in the data: every one of the
   26 repeated sentences kept one option in all its instances (command 6).
5. **After one turn of something else**, the kind is offered again (test
   `test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again`, test_morning.py).

## 4. "Nobody answered you differently from one time to the next"

**Where.** `world.py:469-494` (`pattern`), added to the "Now" block at `world.py:535`.

**How the block is built:**
1. `kind, n = repeating(p)`: the kind and length of the person's current run of same-kind
   acts, silence and search included (`world.py:472-476`). It prints
   `What you have been doing: you have <KIND_DONE[kind]>, <n> turn(s) in a row.` (`KIND_DONE`,
   `world.py:63-71`).
2. It collects every line the person **heard** since the first act of that run: lines by
   others, aimed at them or at everyone (`h["seq"] > first`, `world.py:477-480`; `p.heard` is
   filled at `world.py:939`).
3. **If there are none:** `In that time nobody has said anything to you or to everyone.`
   (`world.py:481-483`).
4. **Otherwise:**
   - `In that time: <name> <verb>, then <verb>; …` (`world.py:484-491`). The verbs come from
     `heard_verb` (`world.py:496-501`) and are kinds only: "asked who took the can", "denied
     taking it", "accused you/someone", "admitted taking it", "reassured you/everyone", "spoke
     to everyone".
   - Then either `Answered you differently from one time to the next: <names>.` for each
     speaker whose verbs were not all the same, or `Nobody answered you differently from one
     time to the next.` (`world.py:492-493`).

**What it means, as computed:**
- The line is printed when at least one person spoke to them or to everyone during their
  current run, and every such speaker used the same kind of line each time.
- Someone who spoke only once counts as "not differently".
- It is about the other people's **kinds** of reply, not about the person's own words, and not
  about whether anything changed.
- The run can be a run of silence. At v9 seed 2 min 81, Elena's prompt says "you have stayed
  put and said nothing, 4 turns in a row. In that time: Daniel denied taking it, then denied
  taking it. Nobody answered you differently…" — though she had last spoken at minute 66.

**At the 54 repeat instances:**

| First pattern line | Instances |
|---|---|
| "you have stayed put and said nothing" | 30 |
| "you have reassured someone" | 8 |
| "you have accused someone of taking it" | 6 |
| "you have searched" | 3 |
| "you have denied taking it" | 3 |
| "you have said something else" | 2 |
| "you have asked who took the can" | 2 |

| Last pattern line | Instances |
|---|---|
| "Nobody answered you differently from one time to the next." | 41 |
| "In that time nobody has said anything to you or to everyone." | 9 |
| "Answered you differently…" | 4 |

(command 4)

## 5. Repeated sentences, and whether the earlier instance was visible

**Method.**
- "Word for word" means that the act's `words` strings are identical (exact match), for the
  same person in the same run.
- The runs covered are runs/v6 (6), runs/v8 (3) and runs/v9 (3).
- **Visible** means the earlier instance's exact words, in quotes, appear in the later
  instance's own prompt. The "Quoted line" column gives the line holding the most recent earlier
  instance.

**Totals** (command 2):

| Run | Lines spoken | Sentences said more than once | Later instances |
|---|---|---|---|
| v6/daniel_ate_it-seed1 | 28 | 1 | 3 |
| v6/daniel_ate_it-seed2 | 48 | 3 | 6 |
| v6/daniel_ate_it-seed3 | 9 | 2 | 2 |
| v6/daniel_ate_it_leo_heard-seed1 | 26 | 1 | 1 |
| v6/daniel_ate_it_leo_heard-seed2 | 28 | 3 | 4 |
| v6/daniel_ate_it_leo_heard-seed3 | 17 | 1 | 2 |
| v8/daniel_ate_it_leo_heard-seed1 | 39 | 2 | 2 |
| v8/daniel_ate_it_leo_heard-seed2 | 50 | 2 | 9 |
| v8/daniel_ate_it_leo_heard-seed3 | 21 | 4 | 9 |
| v9/daniel_ate_it-seed1 | 35 | 3 | 7 |
| v9/daniel_ate_it-seed2 | 51 | 3 | 8 |
| v9/daniel_ate_it-seed3 | 29 | 1 | 1 |
| **12 runs** | **381** | **26** (21 distinct person-sentence pairs) | **54** |

**Visibility:**
- **Earlier instance visible: 54 of 54. Not visible: 0.**
- The pinned "Your own last words" block held an earlier instance in all 54. The morning memory
  also held one in 13 (command 4).
- **Every** earlier instance was visible in 44 of 54. In the other 10, the oldest instances had
  left the 3-line pinned block. At least the three most recent were always there.

**Overlap between runs.** v9 seeds share their start with v6 seeds up to the first lull (min 42,
51, 15; lull_impl.md). So v9 rows at earlier minutes repeat the matching v6 rows. For example:
- v9 seed 1 rows at min 24 and 30 = v6 seed 1 rows 1–2;
- v9 seed 2 rows at min 24 and 39 = v6 seed 2 rows 4–5.

**The case in the brief (v9 seed 2, Elena).**
- The sentence was "Let's all calm down and remember we are a family, we will get through
  this." It was spoken **6** times, not 3: minutes 36, 39, 51, 63, 66 and 81, all
  `reassure_all`.
- The instances at 51, 63 and 81 are lull decisions (lull_v9.md). 36, 39 and 66 are not.
- At minutes 63, 66 and 81, all three lines of her "Your own last words" block were this same
  sentence. At min 81 (command 7):

  ```
  Your own last words this morning:
  - min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
  - min 63, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
  - min 66, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
  What else happened this morning, most recent last:
  - (earlier things, left out here)
  - min 69: Daniel denies taking it, to everyone: "I did not take anything, Mara is just trying to cover up her own guilt."
  - min 72: Daniel denies taking it, to everyone: "I did not take anything, Mara is just lying again."
  Now, minute 81, you are in the kitchen.
  - Daniel is here, staying put.
  - Leo is here, staying put.
  - Mara is here, staying put.
  - 0 portions on the shelf.
  Nothing has been said or done in the kitchen since minute 72.
  You are the first to act in the kitchen this turn.
  What you have been doing: you have stayed put and said nothing, 4 turns in a row.
  In that time: Daniel denied taking it, then denied taking it.
  Nobody answered you differently from one time to the next.
  ```

  Her prompts at 36, 39, 51, 63 and 66 are in command 7.

### The item 5 table

The last two columns:
- **"Same kind just before"** is the number of the person's acts immediately before this one
  with the same kind, routine acts included (item 3).
- **"Others' spoken lines…"** is item 2's count.

| # | Run | Person | Sentence | Said at (option) | This instance | Earlier visible? | Earlier minutes in the prompt (section) | Quoted line | Same kind just before (acts in a row) | Others' spoken lines in the prompt since the previous instance |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | v6/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 75 (reassure_all) | 24 | **Yes** | 21 (own last words); 21 (morning memory) | `min 21, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 2 | 1 |
| 2 | v6/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 75 (reassure_all) | 30 | **Yes** | 21, 24 (own last words) | `min 24, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 2 |
| 3 | v6/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 75 (reassure_all) | 75 | **Yes** | 21, 24, 30 (own last words) | `min 30, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 2 |
| 4 | v6/daniel_ate_it-seed2 | Elena | “Let's all take a deep breath and keep our heads, we will figure this out together.” | 18 (reassure_all), 24 (reassure_all) | 24 | **Yes** | 18 (own last words) | `min 18, you reassured everyone: "Let's all take a deep breath and keep our heads, we will figure this out together."` | 0 | 3 |
| 5 | v6/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 66 (reassure_all), 69 (reassure_all) | 39 | **Yes** | 36 (own last words); 36 (morning memory) | `min 36, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 1 | 2 |
| 6 | v6/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 66 (reassure_all), 69 (reassure_all) | 66 | **Yes** | 36, 39 (own last words) | `min 39, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 0 | 3 |
| 7 | v6/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 66 (reassure_all), 69 (reassure_all) | 69 | **Yes** | 36, 39, 66 (own last words); 66 (morning memory) | `min 66, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 1 | 2 |
| 8 | v6/daniel_ate_it-seed2 | Mara | “You keep accusing me because you are trying to hide what you did, Daniel.” | 54 (accuse_daniel), 66 (accuse_daniel), 69 (accuse_daniel) | 66 | **Yes** | 54 (own last words) | `min 54, you accused Daniel: "You keep accusing me because you are trying to hide what you did, Daniel."` | 0 | 0 |
| 9 | v6/daniel_ate_it-seed2 | Mara | “You keep accusing me because you are trying to hide what you did, Daniel.” | 54 (accuse_daniel), 66 (accuse_daniel), 69 (accuse_daniel) | 69 | **Yes** | 54, 66 (own last words) | `min 66, you accused Daniel: "You keep accusing me because you are trying to hide what you did, Daniel."` | 1 | 0 |
| 10 | v6/daniel_ate_it-seed3 | Mara | “Who took it? Please, someone just tell us the truth.” | 00 (ask_who), 54 (ask_who) | 54 | **Yes** | 00 (own last words) | `min 00, you asked who took it: "Who took it? Please, someone just tell us the truth."` | 0 | 1 |
| 11 | v6/daniel_ate_it-seed3 | Daniel | “I already told you, none of us took it, so let's just stop accusing each other.” | 03 (deny), 78 (deny) | 78 | **Yes** | 03 (own last words) | `min 03, you denied taking it: "I already told you, none of us took it, so let's just stop accusing each other."` | 0 | 1 |
| 12 | v6/daniel_ate_it_leo_heard-seed1 | Mara | “If none of you actually took it, someone has to explain how it just disappeared from the shelf.” | 33 (ask_who), 81 (ask_who) | 81 | **Yes** | 33 (own last words) | `min 33, you asked who took it: "If none of you actually took it, someone has to explain how it just disappeared from the shelf."` | 0 | 2 |
| 13 | v6/daniel_ate_it_leo_heard-seed2 | Mara | “If none of us took it, then where did it go? Someone has to know.” | 03 (ask_who), 12 (ask_who) | 12 | **Yes** | 03 (own last words) | `min 03, you asked who took it: "If none of us took it, then where did it go? Someone has to know."` | 0 | 2 |
| 14 | v6/daniel_ate_it_leo_heard-seed2 | Daniel | “Let's all just calm down, we are going to get through this together.” | 09 (reassure_all), 15 (reassure_all) | 15 | **Yes** | 09 (own last words) | `min 09, you reassured everyone: "Let's all just calm down, we are going to get through this together."` | 0 | 2 |
| 15 | v6/daniel_ate_it_leo_heard-seed2 | Elena | “Let's not accuse each other, we need to stay calm and trust one another.” | 12 (reassure_all), 15 (reassure_all), 36 (reassure_all) | 15 | **Yes** | 12 (own last words); 12 (morning memory) | `min 12, you reassured everyone: "Let's not accuse each other, we need to stay calm and trust one another."` | 1 | 1 |
| 16 | v6/daniel_ate_it_leo_heard-seed2 | Elena | “Let's not accuse each other, we need to stay calm and trust one another.” | 12 (reassure_all), 15 (reassure_all), 36 (reassure_all) | 36 | **Yes** | 12, 15 (own last words) | `min 15, you reassured everyone: "Let's not accuse each other, we need to stay calm and trust one another."` | 0 | 2 |
| 17 | v6/daniel_ate_it_leo_heard-seed3 | Mara | “Please, someone just tell us the truth.” | 03 (ask_who), 21 (ask_who), 54 (ask_who) | 21 | **Yes** | 03 (own last words) | `min 03, you asked who took it: "Please, someone just tell us the truth."` | 1 | 3 |
| 18 | v6/daniel_ate_it_leo_heard-seed3 | Mara | “Please, someone just tell us the truth.” | 03 (ask_who), 21 (ask_who), 54 (ask_who) | 54 | **Yes** | 03, 21 (own last words) | `min 21, you asked who took it: "Please, someone just tell us the truth."` | 0 | 2 |
| 19 | v8/daniel_ate_it_leo_heard-seed1 | Mara | “If none of us took it, then where is the can? Someone has to know.” | 33 (ask_who), 45 (ask_who) | 45 | **Yes** | 33 (own last words) | `min 33, you asked who took it: "If none of us took it, then where is the can? Someone has to know."` | 0 | 4 |
| 20 | v8/daniel_ate_it_leo_heard-seed1 | Elena | “Let us not fall apart now, we are all we have left.” | 48 (reassure_all), 66 (reassure_all) | 66 | **Yes** | 48 (own last words) | `min 48, you reassured everyone: "Let us not fall apart now, we are all we have left."` | 0 | 2 |
| 21 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 30 | **Yes** | 18 (own last words) | `min 18, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 0 | 2 |
| 22 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 33 | **Yes** | 18, 30 (own last words) | `min 30, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 1 | 2 |
| 23 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 54 | **Yes** | 18, 30, 33 (own last words) | `min 33, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 0 | 2 |
| 24 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 78 | **Yes** | 30, 33, 54 (own last words) | `min 54, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 0 | 3 |
| 25 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 81 | **Yes** | 33, 54, 78 (own last words); 78 (morning memory) | `min 78, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 1 | 2 |
| 26 | v8/daniel_ate_it_leo_heard-seed2 | Mara | “Daniel, you searched my bag before, maybe you're the one who took it now.” | 18 (accuse_daniel), 30 (accuse_daniel), 33 (accuse_daniel), 54 (accuse_daniel), 78 (accuse_daniel), 81 (accuse_daniel), 84 (accuse_daniel) | 84 | **Yes** | 54, 78, 81 (own last words); 81 (morning memory) | `min 81, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."` | 2 | 1 |
| 27 | v8/daniel_ate_it_leo_heard-seed2 | Daniel | “Leo, stop looking at me like that, you are the one who took it.” | 33 (accuse_leo), 36 (accuse_leo), 66 (accuse_leo), 78 (accuse_leo) | 36 | **Yes** | 33 (own last words) | `min 33, you accused Leo: "Leo, stop looking at me like that, you are the one who took it."` | 2 | 0 |
| 28 | v8/daniel_ate_it_leo_heard-seed2 | Daniel | “Leo, stop looking at me like that, you are the one who took it.” | 33 (accuse_leo), 36 (accuse_leo), 66 (accuse_leo), 78 (accuse_leo) | 66 | **Yes** | 33, 36 (own last words) | `min 36, you accused Leo: "Leo, stop looking at me like that, you are the one who took it."` | 0 | 0 |
| 29 | v8/daniel_ate_it_leo_heard-seed2 | Daniel | “Leo, stop looking at me like that, you are the one who took it.” | 33 (accuse_leo), 36 (accuse_leo), 66 (accuse_leo), 78 (accuse_leo) | 78 | **Yes** | 33, 36, 66 (own last words) | `min 66, you accused Leo: "Leo, stop looking at me like that, you are the one who took it."` | 0 | 0 |
| 30 | v8/daniel_ate_it_leo_heard-seed3 | Mara | “Who took it? Please, someone just tell us the truth.” | 00 (ask_who), 33 (ask_who), 36 (ask_who), 54 (ask_who), 78 (ask_who) | 33 | **Yes** | 00 (own last words) | `min 00, you asked who took it: "Who took it? Please, someone just tell us the truth."` | 0 | 2 |
| 31 | v8/daniel_ate_it_leo_heard-seed3 | Mara | “Who took it? Please, someone just tell us the truth.” | 00 (ask_who), 33 (ask_who), 36 (ask_who), 54 (ask_who), 78 (ask_who) | 36 | **Yes** | 33 (own last words); 33 (morning memory) | `min 33, you asked who took it: "Who took it? Please, someone just tell us the truth."` | 1 | 2 |
| 32 | v8/daniel_ate_it_leo_heard-seed3 | Mara | “Who took it? Please, someone just tell us the truth.” | 00 (ask_who), 33 (ask_who), 36 (ask_who), 54 (ask_who), 78 (ask_who) | 54 | **Yes** | 33, 36 (own last words); 36 (morning memory) | `min 36, you asked who took it: "Who took it? Please, someone just tell us the truth."` | 0 | 1 |
| 33 | v8/daniel_ate_it_leo_heard-seed3 | Mara | “Who took it? Please, someone just tell us the truth.” | 00 (ask_who), 33 (ask_who), 36 (ask_who), 54 (ask_who), 78 (ask_who) | 78 | **Yes** | 33, 36, 54 (own last words) | `min 54, you asked who took it: "Who took it? Please, someone just tell us the truth."` | 0 | 3 |
| 34 | v8/daniel_ate_it_leo_heard-seed3 | Elena | “Please, someone just tell me the truth so we can deal with this together.” | 03 (ask_who), 36 (ask_who) | 36 | **Yes** | 03 (own last words) | `min 03, you asked who took it: "Please, someone just tell me the truth so we can deal with this together."` | 0 | 3 |
| 35 | v8/daniel_ate_it_leo_heard-seed3 | Mara | “Please, someone just tell us the truth.” | 03 (ask_who), 24 (ask_who) | 24 | **Yes** | 03 (own last words) | `min 03, you asked who took it: "Please, someone just tell us the truth."` | 0 | 2 |
| 36 | v8/daniel_ate_it_leo_heard-seed3 | Daniel | “I told you, none of us touched it, so let's just drop this right now.” | 33 (deny), 36 (deny), 39 (deny), 66 (deny) | 36 | **Yes** | 33 (own last words) | `min 33, you denied taking it: "I told you, none of us touched it, so let's just drop this right now."` | 1 | 1 |
| 37 | v8/daniel_ate_it_leo_heard-seed3 | Daniel | “I told you, none of us touched it, so let's just drop this right now.” | 33 (deny), 36 (deny), 39 (deny), 66 (deny) | 39 | **Yes** | 33, 36 (own last words); 36 (morning memory) | `min 36, you denied taking it: "I told you, none of us touched it, so let's just drop this right now."` | 2 | 0 |
| 38 | v8/daniel_ate_it_leo_heard-seed3 | Daniel | “I told you, none of us touched it, so let's just drop this right now.” | 33 (deny), 36 (deny), 39 (deny), 66 (deny) | 66 | **Yes** | 33, 36, 39 (own last words) | `min 39, you denied taking it: "I told you, none of us touched it, so let's just drop this right now."` | 0 | 1 |
| 39 | v9/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 51 (reassure_all), 63 (reassure_all), 75 (reassure_all) | 24 | **Yes** | 21 (own last words); 21 (morning memory) | `min 21, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 2 | 1 |
| 40 | v9/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 51 (reassure_all), 63 (reassure_all), 75 (reassure_all) | 30 | **Yes** | 21, 24 (own last words) | `min 24, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 2 |
| 41 | v9/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 51 (reassure_all), 63 (reassure_all), 75 (reassure_all) | 51 | **Yes** | 21, 24, 30 (own last words) | `min 30, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 2 |
| 42 | v9/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 51 (reassure_all), 63 (reassure_all), 75 (reassure_all) | 63 | **Yes** | 24, 30, 51 (own last words); 51 (morning memory) | `min 51, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 1 |
| 43 | v9/daniel_ate_it-seed1 | Elena | “Let us hold together and keep our peace, we will get through this.” | 21 (reassure_all), 24 (reassure_all), 30 (reassure_all), 51 (reassure_all), 63 (reassure_all), 75 (reassure_all) | 75 | **Yes** | 30, 51, 63 (own last words) | `min 63, you reassured everyone: "Let us hold together and keep our peace, we will get through this."` | 0 | 2 |
| 44 | v9/daniel_ate_it-seed1 | Mara | “Can someone please just tell me the truth so we can stop this?” | 24 (ask_who), 42 (ask_who) | 42 | **Yes** | 24 (own last words) | `min 24, you asked who took it: "Can someone please just tell me the truth so we can stop this?"` | 0 | 2 |
| 45 | v9/daniel_ate_it-seed1 | Mara | “Can someone please just tell me the truth so this can finally end?” | 54 (ask_who), 75 (ask_who) | 75 | **Yes** | 54 (own last words) | `min 54, you asked who took it: "Can someone please just tell me the truth so this can finally end?"` | 0 | 2 |
| 46 | v9/daniel_ate_it-seed2 | Elena | “Let's all take a deep breath and keep our heads, we will figure this out together.” | 18 (reassure_all), 24 (reassure_all) | 24 | **Yes** | 18 (own last words) | `min 18, you reassured everyone: "Let's all take a deep breath and keep our heads, we will figure this out together."` | 0 | 3 |
| 47 | v9/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 51 (reassure_all), 63 (reassure_all), 66 (reassure_all), 81 (reassure_all) | 39 | **Yes** | 36 (own last words); 36 (morning memory) | `min 36, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 1 | 2 |
| 48 | v9/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 51 (reassure_all), 63 (reassure_all), 66 (reassure_all), 81 (reassure_all) | 51 | **Yes** | 36, 39 (own last words); 39 (morning memory) | `min 39, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 0 | 1 |
| 49 | v9/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 51 (reassure_all), 63 (reassure_all), 66 (reassure_all), 81 (reassure_all) | 63 | **Yes** | 36, 39, 51 (own last words) | `min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 0 | 1 |
| 50 | v9/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 51 (reassure_all), 63 (reassure_all), 66 (reassure_all), 81 (reassure_all) | 66 | **Yes** | 39, 51, 63 (own last words) | `min 63, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 1 | 2 |
| 51 | v9/daniel_ate_it-seed2 | Elena | “Let's all calm down and remember we are a family, we will get through this.” | 36 (reassure_all), 39 (reassure_all), 51 (reassure_all), 63 (reassure_all), 66 (reassure_all), 81 (reassure_all) | 81 | **Yes** | 51, 63, 66 (own last words) | `min 66, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."` | 0 | 2 |
| 52 | v9/daniel_ate_it-seed2 | Mara | “You keep pointing at me because you're the one who actually stole it, Daniel.” | 54 (accuse_daniel), 66 (accuse_daniel), 69 (accuse_daniel) | 66 | **Yes** | 54 (own last words) | `min 54, you accused Daniel: "You keep pointing at me because you're the one who actually stole it, Daniel."` | 0 | 0 |
| 53 | v9/daniel_ate_it-seed2 | Mara | “You keep pointing at me because you're the one who actually stole it, Daniel.” | 54 (accuse_daniel), 66 (accuse_daniel), 69 (accuse_daniel) | 69 | **Yes** | 54, 66 (own last words) | `min 66, you accused Daniel: "You keep pointing at me because you're the one who actually stole it, Daniel."` | 1 | 0 |
| 54 | v9/daniel_ate_it-seed3 | Elena | “Let's not tear ourselves apart over this, we are all we have left.” | 21 (reassure_all), 24 (reassure_all) | 24 | **Yes** | 21 (own last words) | `min 21, you reassured everyone: "Let's not tear ourselves apart over this, we are all we have left."` | 1 | 0 |

## 6. Temperature and seed per request

| What | Where | Value |
|---|---|---|
| Temperature | config.json `"temperature": 1.0`, read at gemini.py:73, sent at gemini.py:97 | **1.0** for every request. config.json has not changed since `8b183d4`, the first prototype commit (command 9). |
| Seed | `GeminiClient(config, seed)` at morning.py:52, stored at gemini.py:72, sent as `seed=self.seed` at gemini.py:98 in `GenerateContentConfig` (gemini.py:95-103) | **The morning's seed** (1, 2 or 3) for every request of that morning. It is the same value on every request, for every person and minute. |
| The other request settings | gemini.py:95-103 | `response_mime_type="application/json"`, `response_schema=RESPONSE_SCHEMA`, `max_output_tokens` 2048 (config.json), system instruction = `SYSTEM` |
| The same in v6 and v8 | `v6/gemini.py` and `v8/gemini.py` lines 61-135 are identical to the current file. The file at `1c50d44`, which made v9, is identical in full (command 9). | — |

The seed is also part of the cache key (gemini.py:196-198). So within one morning an identical
prompt is never sent twice: its answer is served from the cache (gemini.py:230-238).

---

## NOT FOUND list

- Any code that compares a new line's **words** with the speaker's earlier lines. The filter
  (`world.py:381-385`) and `Newness` (`talk.py:45-66`) compare kinds and targets only.
- Any prompt line that marks an own earlier line as already said, or as said word for word.
  The pinned block lists the lines (`world.py:541-542`) and nothing more.
- Any prompt line that says whether an own earlier line had an effect. The pattern block gives
  others' replies by kind (`world.py:469-494`).
- Any words in the system instruction about repeating, saying something again, varying,
  "same", "already", "earlier" or "before" (`world.py:31-43`; command 8).
- A per-request seed that differs within a morning. Every request carries the morning's seed
  (gemini.py:98).
- In item 5, a later instance whose earlier instance was not in its prompt: **0 of 54**.
- In item 5, a repeated sentence spoken under two different options: **0 of 26**.
- Others' reactions tied to a specific line. A shown feeling (`world.py:523`) is printed without
  reference to any line.

---

## Commands run and their output

All read-only, from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset and
`PYTHONDONTWRITEBYTECODE=1`. `$S` is the session scratchpad. Its scripts are reproduced at the
end and are not in the repository. Nothing in the repository was written except this file.
`git status --short` before writing it showed only the three old
`runs/v6/daniel_ate_it-seed*.replay.md`.

**1. Replay each run in memory with the code that made it, and dump every decision's prompt**
```
$ for sc in daniel_ate_it daniel_ate_it_leo_heard; do for s in 1 2 3; do python "$S/rep_replay.py" v6 v6 $sc $s - > "$S/rep/v6-$sc-$s.json"; done; done
$ for s in 1 2 3; do python "$S/rep_replay.py" v8 v8 daniel_ate_it_leo_heard $s - > "$S/rep/v8-daniel_ate_it_leo_heard-$s.json"; python "$S/rep_replay.py" . v9 daniel_ate_it $s 9 > "$S/rep/v9-daniel_ate_it-$s.json"; done
v6/daniel_ate_it-seed1 identical: True model decisions: 45
v6/daniel_ate_it-seed2 identical: True model decisions: 66
v6/daniel_ate_it-seed3 identical: True model decisions: 25
v6/daniel_ate_it_leo_heard-seed1 identical: True model decisions: 44
v6/daniel_ate_it_leo_heard-seed2 identical: True model decisions: 43
v6/daniel_ate_it_leo_heard-seed3 identical: True model decisions: 29
v8/daniel_ate_it_leo_heard-seed1 identical: True model decisions: 56
v8/daniel_ate_it_leo_heard-seed2 identical: True model decisions: 67
v8/daniel_ate_it_leo_heard-seed3 identical: True model decisions: 39
v9/daniel_ate_it-seed1 identical: True model decisions: 51
v9/daniel_ate_it-seed2 identical: True model decisions: 69
v9/daniel_ate_it-seed3 identical: True model decisions: 47
$ git status --short
?? runs/v6/daniel_ate_it-seed1.replay.md
?? runs/v6/daniel_ate_it-seed2.replay.md
?? runs/v6/daniel_ate_it-seed3.replay.md
```
v9 was replayed with the current code and `LULL_QUIET` set to 9 in memory, which is the code at
`1c50d44`.

**2. Find repeated sentences, and check each later prompt for the earlier words**
```
$ python "$S/rep_find.py" "$S/rep" "$S/rep_rows.json"
run | lines spoken | sentences said more than once | later instances
v6/daniel_ate_it-seed1 | 28 | 1 | 3
v6/daniel_ate_it-seed2 | 48 | 3 | 6
v6/daniel_ate_it-seed3 | 9 | 2 | 2
v6/daniel_ate_it_leo_heard-seed1 | 26 | 1 | 1
v6/daniel_ate_it_leo_heard-seed2 | 28 | 3 | 4
v6/daniel_ate_it_leo_heard-seed3 | 17 | 1 | 2
v8/daniel_ate_it_leo_heard-seed1 | 39 | 2 | 2
v8/daniel_ate_it_leo_heard-seed2 | 50 | 2 | 9
v8/daniel_ate_it_leo_heard-seed3 | 21 | 4 | 9
v9/daniel_ate_it-seed1 | 35 | 3 | 7
v9/daniel_ate_it-seed2 | 51 | 3 | 8
v9/daniel_ate_it-seed3 | 29 | 1 | 1
later instances: 54 | earlier visible: 54 | not visible: 0
```

**3. Trimming and the pinned block, over every prompt the 12 runs sent**
```
prompts used by the 12 runs: 581; with the trim marker: 541; memory lines kept per prompt: min 0, median 2, max 8
prompts with 'Your own last words': 503; own lines shown there: 1250
```

**4. Visible minutes and sections per later instance, and the pattern lines** (the per-instance
lines are the table's columns 6–8)
```
sections holding an earlier instance (count of later instances): {'morning memory': 13, 'own last words (pinned)': 54}
later instances with every earlier instance visible: 44 of 54
first pattern line (what they had been doing):
  30  What you have been doing: you have stayed put and said nothing
  8  What you have been doing: you have reassured someone
  6  What you have been doing: you have accused someone of taking it
  3  What you have been doing: you have searched
  3  What you have been doing: you have denied taking it
  2  What you have been doing: you have said something else
  2  What you have been doing: you have asked who took the can
last pattern line:
  41  Nobody answered you differently from one time to the next.
  9  In that time nobody has said anything to you or to everyone.
  2  Answered you differently from one time to the next: Elena.
  1  Answered you differently from one time to the next: Daniel, Elena.
  1  Answered you differently from one time to the next: Daniel.
```

**5. The table, and the counts in its last two columns**
```
$ PYTHONIOENCODING=utf-8 python "$S/rep_table.py" "$S/rep_rows.json" "$S/rep" > "$S/rep_table.md"
$ awk -F'|' 'NR>2{print $11}' rep_table.md | sort | uniq -c        # same kind just before
     36  0
     13  1
      5  2
$ awk -F'|' 'NR>2{print $12}' rep_table.md | sort -n | uniq -c     # others' lines since the previous instance
      9  0
     12  1
     25  2
      7  3
      1  4
```
Column `$11` is "Same kind just before" (36 + 13 + 5 = 54). Column `$12` is "Others' spoken
lines" (9 + 12 + 25 + 7 + 1 = 54).

**6. Did any repeated sentence change option?**
```
repeated sentences: 26 | with more than one option among their instances: 0
distinct (person, sentence) across runs: 21
```

**7. Elena, v9 seed 2: every instance's "own last words", memory and "Now" blocks**

The sentence is "Let's all calm down and remember we are a family, we will get through this."
Only the blocks named are shown.

```
=== min 36 (reassure_all) ===
Your own last words this morning:
- min 21, you said: "Daniel, stop shouting at your sister, we are not going to survive if we tear each other apart."
- min 24, you reassured everyone: "Let's all take a deep breath and keep our heads, we will figure this out together."
- min 27, you reassured everyone: "Let's not accuse each other blindly when we need every ounce of trust we have left."
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 33: Daniel accuses Mara of taking it: "You are the one who keeps pushing and deflecting, Mara, because you are trying to hide what you did."
Now, minute 36, you are in the kitchen.
- Daniel is here, talking.
- Leo is here, staying put.
- Mara is here, talking. Mara looks furious.
- 2 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Mara accuses Daniel of taking it: "You always blame me for everything, Daniel, and I am sick of it."
2. Daniel denies taking it, to everyone: "I didn't take anything, Mara, and you need to stop making false accusations."
3. Leo stays put and says nothing.
What you have been doing: you have searched, 2 turns in a row.
In that time: Mara asked who took the can; Daniel denied taking it.
Nobody answered you differently from one time to the next.

=== min 39 (reassure_all) ===
Your own last words this morning:
- min 24, you reassured everyone: "Let's all take a deep breath and keep our heads, we will figure this out together."
- min 27, you reassured everyone: "Let's not accuse each other blindly when we need every ounce of trust we have left."
- min 36, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 36: you reassured everyone: "Let's all calm down and remember we are a family, we will get through this.". You felt anxious.
Now, minute 39, you are in the kitchen.
- Daniel is here, talking.
- Leo is here, staying put.
- Mara is here, talking. Mara looks frightened.
- 2 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Mara accuses Daniel of taking it: "You can't prove a single thing, Daniel, stop looking at me like that."
2. Daniel accuses Mara of taking it: "You have been pointing fingers this whole time, Mara, to cover up your own guilt."
What you have been doing: you have reassured someone, 1 turn in a row.
In that time nobody has said anything to you or to everyone.

=== min 51 (reassure_all) ===
Your own last words this morning:
- min 27, you reassured everyone: "Let's not accuse each other blindly when we need every ounce of trust we have left."
- min 36, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
- min 39, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 39: you reassured everyone: "Let's all calm down and remember we are a family, we will get through this.". You felt very anxious.
- min 42: Daniel accuses Mara of taking it: "You still have no explanation for your behavior, Mara, which means you are the one hiding the truth."
Now, minute 51, you are in the kitchen.
- Daniel is here, staying put.
- Leo is here, staying put.
- Mara is here, staying put.
- 2 portions on the shelf.
Nothing has been said or done in the kitchen since minute 42.
You are the first to act in the kitchen this turn.
What you have been doing: you have stayed put and said nothing, 3 turns in a row.
In that time nobody has said anything to you or to everyone.

=== min 63 (reassure_all) ===
Your own last words this morning:
- min 36, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
- min 39, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
- min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 51: Daniel accuses Mara of taking it: "You are just deflecting because you know you took it, Mara."
- min 54: Mara accuses Daniel of taking it: "You keep pointing at me because you're the one who actually stole it, Daniel."
Now, minute 63, you are in the kitchen.
- Daniel is here, staying put.
- Leo is here, staying put.
- Mara is here, staying put. Mara looks furious.
- 2 portions on the shelf.
Nothing has been said or done in the kitchen since minute 54.
Said and done in the kitchen this turn, before you, in order:
1. Mara stays put and says nothing.
What you have been doing: you have stayed put and said nothing, 3 turns in a row.
In that time nobody has said anything to you or to everyone.

=== min 66 (reassure_all) ===
Your own last words this morning:
- min 39, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
- min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
- min 63, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 63: Leo says to everyone, while sharing out the food: "We are just going to starve ourselves arguing, let's just divide what is left right now."
Now, minute 66, you are in the kitchen.
- Daniel is here, talking.
- Leo is here, sharing out the food.
- Mara is here, talking.
- 0 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Mara accuses Daniel of taking it: "You keep pointing at me because you're the one who actually stole it, Daniel."
2. Daniel denies taking it, to everyone: "I did not take anything, Mara is just trying to shift the blame off herself."
What you have been doing: you have reassured someone, 1 turn in a row.
In that time: Leo spoke to everyone; Daniel denied taking it.
Nobody answered you differently from one time to the next.

=== min 81 (reassure_all) ===
(as quoted in item 5)
```

**8. The system instruction's wording, and code that mentions repetition**
```
$ python -c "import world, re; ..."
'repeat' in SYSTEM: False
'again' in SYSTEM: False
'different' in SYSTEM: False
'same' in SYSTEM: False
'already' in SYSTEM: False
'earlier' in SYSTEM: False
'before' in SYSTEM: False
$ grep -n -i "repeat\|again\|differen\|same words\|already" world.py | head
7:   (module docstring: "sees what was already said and done in the room this turn")
118: (Track docstring: "again raises it a step")
151, 237-238, 266, 317, 383, 419, 431 (grudge docstrings, `acted`, `repeating`, the filter, rise words)
```
None of these is a check on words.

**9. The request settings**
```
$ grep -n "GeminiClient(config, seed)" morning.py
52:                  else GeminiClient(config, seed))
$ grep -n "self.seed = seed\|self.temperature = \|temperature=self.temperature\|seed=self.seed\|GenerateContentConfig(" gemini.py
72:        self.seed = seed
73:        self.temperature = config["temperature"]
95:        config = self._types.GenerateContentConfig(
97:            temperature=self.temperature,
98:            seed=self.seed,
219:        self.seed = seed
$ head -3 config.json ; git log --format='%h %s' -- config.json | head -3
{
  "model": "gemini-3.5-flash-lite",
  "temperature": 1.0,
8b183d4 LLM morning prototype, steps 1 to 5
$ for v in v6 v8; do diff <(sed -n 61,135p $v/gemini.py) <(sed -n 61,135p gemini.py) >/dev/null && echo "$v gemini.py 61-135 identical"; done
v6 gemini.py 61-135 identical
v8 gemini.py 61-135 identical
$ git show 1c50d44:Prototypes/llm-morning/gemini.py | diff - gemini.py && echo "v9-time gemini.py identical"
v9-time gemini.py identical
```
gemini.py:219 is `Oracle`'s seed, used for the cache key.

### Scripts (scratchpad)

`$S/rep_replay.py`:
```python
"""Replays one recorded run in memory from its cache with the code that made it (no client, no
files written) and dumps, for every model decision in the order asked: minute, person, option,
words, and the exact prompt. Also says whether the replayed transcript equals the saved one.
    python rep_replay.py <code dir> <runs/cache subdir> <scenario> <seed> <lull minutes or ->"""
import json, os, sys
code, sub, scenario, seed, lull = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, code) if code != "." else ROOT)
import world
from gemini import Cache
if lull != "-":
    world.LULL_QUIET = int(lull)
MODEL = "gemini-3.5-flash-lite"
cache = Cache(os.path.join(ROOT, "cache", sub, f"{MODEL}-{scenario}-seed{seed}.json"))

class Rec:
    def __init__(self):
        self.prompts = []
    def ask(self, system, prompt):
        r = cache.get(Cache.key(MODEL, seed, system, prompt))
        if r is None:
            raise SystemExit("cache miss")
        self.prompts.append(prompt)
        return r

rec = Rec()
m = world.Morning(rec, seed, scenario)
for t in range(m.turns):
    m.turn(t)
m.finish()
saved = json.load(open(os.path.join(ROOT, "runs", sub, f"{scenario}-seed{seed}.transcript.json"), encoding="utf-8"))
asked = [(rec_["minute"], d) for rec_ in m.log for d in rec_["decisions"] if d["mode"] != "routine"]
assert len(asked) == len(rec.prompts)
out = {"run": f"{sub}/{scenario}-seed{seed}", "identical": saved == json.loads(json.dumps(m.transcript)),
       "decisions": [{"minute": mi, "who": d["person"], "option": d["option"], "say": d.get("say"),
                      "mode": d["mode"], "prompt": p} for (mi, d), p in zip(asked, rec.prompts)]}
json.dump(out, sys.stdout, ensure_ascii=False)
```

`$S/rep_find.py` (the core loop):
```python
for f in sorted(glob.glob(sys.argv[1] + "/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    groups = defaultdict(list)
    for x in d["decisions"]:
        if x["say"]:
            groups[(x["who"], x["say"])].append(x)
    reps = {k: v for k, v in groups.items() if len(v) > 1}
    for (who, words), xs in sorted(reps.items(), key=lambda kv: kv[1][0]["minute"]):
        for k in range(1, len(xs)):
            later, earlier = xs[k], xs[:k]
            lines = later["prompt"].splitlines()
            hits = [(i, l) for i, l in enumerate(lines) if f'"{words}"' in l]      # visible = exact words in quotes
            seen_min = sorted({int(m) for _, l in hits for m in re.findall(r"min (\d\d)", l)})
            # section(lines, i): the nearest heading above the hit
            #   ("Your own last words this morning:", "What else happened this morning", ...)
```

`$S/rep_table.py` builds the item 5 table from `rep_rows.json`:
- **"Same kind just before"** counts the person's transcript acts immediately before this one
  whose `act_of` kind matches.
- **"Others' spoken lines"** counts the prompt's memory lines `- min MM: <Name> …: "` with MM
  greater than the previous instance's minute, plus this turn's "Said and done" lines by others.
