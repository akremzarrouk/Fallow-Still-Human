# Never item update: inactivity, and judging rules in CLAUDE.md

Mode: implement. Two text files changed, no code. Commit: **`a7bffab3ef6a04f143d7b050aba9d360d4269ebc`**
(`a7bffab`).

## What changed

| File | Change |
|---|---|
| Docs/understanding/target-morning.md:31-32 | The Never item "Long stretches where everyone does nothing and nothing about them changes in a way the story can show." is replaced by "Long stretches where nothing anyone does shows how they feel.", with the line "Changed 29 Sep 2026: silence is normal; frozen silence is not." under it. |
| CLAUDE.md:15-19 | The "## Judging changes" block, verbatim. |

**CLAUDE.md was already edited before this step.** At the start, `git status` showed CLAUDE.md
modified. Its uncommitted diff was exactly the requested block, appended at the end with one blank
line before it. Appending it again would have written it twice. So CLAUDE.md was committed as
found, and this step made no edit to it. The diff below is the committed state, and it matches the
brief character for character.

**The note's placement.** "Add one line under it" was read as a continuation line of the same
bullet, indented two spaces like the file's other wrapped items. It stays part of the item.

**Consequence for earlier reports (fact, no change made).** The Never sheets in witness_v6.md,
witness_v8.md and lull_v9.md score N9 with the old wording and its reading ("every decision in the
house is stay put and say nothing" for 5 turns). Those reports were not edited.

## The diff

```
$ git show a7bffab
commit a7bffab3ef6a04f143d7b050aba9d360d4269ebc
Author: Akrem
Date:   Tue Sep 29 18:08:19 2026 +0100

    Target morning: the inactivity Never item judges frozen silence, not silence; judging rules in CLAUDE.md

diff --git a/CLAUDE.md b/CLAUDE.md
index 0393e26..184f5f3 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -11,3 +11,9 @@ Never stop processes by name or broad filters; only by the exact process ID you
 - Read-only. Cite path:line. Write NOT FOUND when something does not exist.
   No opinions.
 - Every deliverable includes the commands run and their output.
+
+## Judging changes
+- Judge every change by what a real family would do in this situation,
+  not by whether a number moves. A metric is a clue, never the goal.
+- Before proposing a mechanism, argue against it first: would a real
+  person do this, and for what reason?
diff --git a/Docs/understanding/target-morning.md b/Docs/understanding/target-morning.md
index a64c4a1..6cb55ea 100644
--- a/Docs/understanding/target-morning.md
+++ b/Docs/understanding/target-morning.md
@@ -28,8 +28,8 @@ Nobody else. No zombies yet: the family's behaviour must be believable first.
 - A person pictures a room as empty when they left people in it.
 - An important social choice (who to comfort, who to suspect) is settled by
   chance alone when the people involved differ in ways that should matter.
-- Long stretches where everyone does nothing and nothing about them changes
-  in a way the story can show.
+- Long stretches where nothing anyone does shows how they feel.
+  Changed 29 Sep 2026: silence is normal; frozen silence is not.
 - Everyone speaks at once and nobody answers the line before theirs.
 - A person repeats the same kind of line many turns in a row with no effect.
 - Someone who was wronged forgives within minutes, with no lasting cost.
```

## Commands run and output

```
$ git status --porcelain
 M CLAUDE.md
?? Prototypes/llm-morning/cache/v9/
?? Prototypes/llm-morning/reports/lull_v9.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
?? Prototypes/llm-morning/runs/v9/
$ grep -n "Long stretches" -B1 -A3 Docs/understanding/target-morning.md
30-  chance alone when the people involved differ in ways that should matter.
31:- Long stretches where everyone does nothing and nothing about them changes
32-  in a way the story can show.
33-- Everyone speaks at once and nobody answers the line before theirs.
34-- A person repeats the same kind of line many turns in a row with no effect.
$ git diff CLAUDE.md
(the CLAUDE.md hunk shown above)
```

The item was edited (the Edit tool, one replacement). Then:

```
$ git diff --stat
 CLAUDE.md                            | 6 ++++++
 Docs/understanding/target-morning.md | 4 ++--
 2 files changed, 8 insertions(+), 2 deletions(-)
$ grep -c "everyone does nothing" Docs/understanding/target-morning.md
0
$ grep -n "Long stretches where nothing anyone does shows how they feel.\|Changed 29 Sep 2026" Docs/understanding/target-morning.md
31:- Long stretches where nothing anyone does shows how they feel.
32:  Changed 29 Sep 2026: silence is normal; frozen silence is not.
$ git add Docs/understanding/target-morning.md CLAUDE.md && git commit
$ git log --oneline -1
a7bffab Target morning: the inactivity Never item judges frozen silence, not silence; judging rules in CLAUDE.md
```

## Git status

**Not clean apart from the three replay.md files.** `Prototypes/llm-morning/world.py` is modified,
and this step did not make that change:

```
$ git diff Prototypes/llm-morning/world.py
@@ -56,7 +56,8 @@ PROMPT_TOKEN_BUDGET = 1400   # estimated; the API counted 1,370 at most in the s
 QUIET_TURNS = 2              # full turns with nothing new that end a conversation
 INNER_EVERY = 9              # minutes: an inner moment at most this often per person
 FALL_EVERY = 15              # minutes: a suspicion or grudge falls at most one step this often
-LULL_QUIET = 9               # minutes a room must be still before a lull (None: no lulls)
+LULL_QUIET = None            # minutes a room must be still before a lull (None: no lulls);
+                             # off since reports/lull_v9.md, 9 in reports/lull_design.md
 LULL_EVERY = 12              # minutes since a person was last asked before a lull
```

- It appeared in the working tree during this step, after the first `git status` above, which did
  not list it.
- The brief forbids code changes here, so it was neither committed nor reverted.

**The v9 run outputs.** At the start, `runs/v9/`, `cache/v9/` and `reports/lull_v9.md` were
untracked. During this step they were committed by `dc3f42d` ("LLM morning: v9 runs (lull
moments), seeds 1-3, cache and report"), which was not made by this step. A `git add` of those paths
afterwards staged nothing.

```
$ git log --oneline -3
a7bffab Target morning: the inactivity Never item judges frozen silence, not silence; judging rules in CLAUDE.md
dc3f42d LLM morning: v9 runs (lull moments), seeds 1-3, cache and report
ac80bc6 LLM morning: report for the lull-moment implementation
```

This report is committed on its own after `a7bffab`.
