# Fix: the food line of whoever is handed a portion

Mode: implement. No API was called: every command ran with `GEMINI_API_KEY` unset, or in replay
mode, which has no client. Paths are relative to `Prototypes/llm-morning/`.

## Result

| | |
|---|---|
| Commit | **`4d39f4a`** (`world.py`, `test_morning.py`). This report is committed on its own after it. |
| New test | `BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it`: **FAIL before, ok after** (§3). |
| Full suite | **159 tests, OK** in 78.4 s (§3). |
| Day 1 from the v11 caches | 55, 53, 45 answers, 0 API requests; story and transcript **IDENTICAL** to `runs/v11` (§4). |
| v12 and v11 checks | **IDENTICAL**, 3 of 3 each, 0 API calls (§4). |
| git status | Clean apart from the three old `runs/v6/*.replay.md` files. |

## 1. What was wrong

body_impl.md §1:
- While Q decides whether to eat a portion just handed to them, the portion is off the shelf and
  in Q's hand (body_design §2.5).
- Q's "About food:" line counted only the shelf. In seed 2, with 1 portion, it read:

```
About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
```

That is false for Q, who is holding food.

## 2. The new line

**Only in Q's prompt for that answer** (`decide_given`), the line is:

```
About food: the shelf holds <N portion(s)>, and you hold the portion <Giver> has just handed you; there is no other food in the house, so <conclusion>.
```

**How it is worked out:**
- `<N>` is still the shelf.
- `<conclusion>` follows the existing rule (`food_line`, night_design §5.3), applied to
  the food that exists: the shelf plus the portion in Q's hand.
  - With at least one portion counted, it is never "there is nothing to eat today".

**Seed 2** (1 portion, four people present), the exact line the new test checks:

```
About food: the shelf holds 0 portions, and you hold the portion Elena has just handed you; there is no other food in the house, so there is not one portion each.
```

**What does not change:**
- Everyone else's line, and Q's own line once their answer is given. `Morning.holding` is set
  only around Q's ask in `decide_given`, and cleared after it.
- The prompt's budget count uses the same line (`trip_lines`), so it measures what Q is shown.

## 3. Tests

**Before the fix** (the test written first, on the code at `74ad9d3`):

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it
test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it (test_morning.BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it) ... FAIL

======================================================================
FAIL: test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it (test_morning.BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 3476, in test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it
    self.assertEqual(line, f"About food: the shelf holds 0 portions, and you hold the portion {G} has just handed "
AssertionError: 'Abou[35 chars] and there is no other food in the house, so t[25 chars]day.' != 'Abou[35 chars] and you hold the portion Elena has just hande[73 chars]ach.'
- About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.
+ About food: the shelf holds 0 portions, and you hold the portion Elena has just handed you; there is no other food in the house, so there is not one portion each.


----------------------------------------------------------------------
Ran 1 test in 0.246s

FAILED (failures=1)
exit=1
```

**After the fix:**

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest -v test_morning.BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it
test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it (test_morning.BodyTest.test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.234s

OK
exit=0
```

**The full suite after the fix** (its last lines; the dots and the stubbed-API retry messages above them are left out):

```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -m unittest test_morning
…
Ran 159 tests in 78.403s

OK
exit=0
```

**What the test checks**, in seed 2 (1 portion), with day 1 from the v11 cache, a scripted night, and a food moment forced for the first to act at minute 00, who gives the portion to the last:
- the line in Q's prompt is exactly §2's, and Q's prompt nowhere says "nothing to eat today";
- the giver's line, before the gift: `About food: the shelf holds 1 portion, and there is no other food in the house, so there is not one portion each.` (unchanged);
- the other two, after Q has eaten it: `About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.` (unchanged), equal to `food_line()` with no person.

## 4. Replays

`$S/impl/replay_day1.py` is the read-only script reproduced in body_impl.md §7.

```
$ python $S/replay_day1.py
daniel_ate_it-seed1: day 1 replayed 55 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed2: day 1 replayed 53 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
daniel_ate_it-seed3: day 1 replayed 45 answers from cache/v11, 0 API requests; story IDENTICAL to runs/v11, transcript IDENTICAL
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
```

## 5. The diff

```diff
$ git show 4d39f4a
diff --git a/Prototypes/llm-morning/test_morning.py b/Prototypes/llm-morning/test_morning.py
index bf799b4..8036700 100644
--- a/Prototypes/llm-morning/test_morning.py
+++ b/Prototypes/llm-morning/test_morning.py
@@ -3461,6 +3461,29 @@ class BodyTest(unittest.TestCase):
         self.assertEqual(story.count("**Food moment**"), len(moments))
         self.assertEqual(meta["day2_asks"], sum(a["mode"] != "routine" for a in acts))
 
+    # body_fix.md
+    def test_the_food_line_counts_the_portion_in_the_hand_of_whoever_was_handed_it(self):
+        o = self.order_at_0(2)                                   # seed 2: 1 portion on the shelf
+        giver, q, w1, w2 = o[0], o[3], o[1], o[2]
+        G = data.PEOPLE[giver]["name"]
+        day2, client = self.day2_of(2, {giver: [f"give_{q}"], q: ["eat_given"]}, only(giver, 0))
+        day2.turn(0)
+
+        def food(who):
+            prompt = next(x for w, p, x in client.prompts if p == who and w == 0)
+            return prompt, next(x for x in prompt.split("\n") if x.startswith("About food:"))
+        held, line = food(q)
+        self.assertEqual(line, f"About food: the shelf holds 0 portions, and you hold the portion {G} has just handed "
+                               f"you; there is no other food in the house, so there is not one portion each.")
+        self.assertNotIn("nothing to eat today", held)
+        # Everyone else's line is the shelf's, as before: the giver's before the gift, the others' after it.
+        self.assertEqual(food(giver)[1], "About food: the shelf holds 1 portion, and there is no other food in the "
+                                         "house, so there is not one portion each.")
+        for w in (w1, w2):
+            self.assertEqual(food(w)[1], "About food: the shelf holds 0 portions, and there is no other food in the "
+                                         "house, so there is nothing to eat today.")
+        self.assertEqual(day2.food_line(), food(w1)[1])
+
     # B-T12
     def test_b_t12_v12_still_replays(self):
         done = run_check("v12")
diff --git a/Prototypes/llm-morning/world.py b/Prototypes/llm-morning/world.py
index 1ad9d54..a93a7b1 100644
--- a/Prototypes/llm-morning/world.py
+++ b/Prototypes/llm-morning/world.py
@@ -365,6 +365,7 @@ class Morning:
         self.trip_acts = []         # (minute, who, kind, target, words), every position taken
         self.trip_now = set()       # during the turn it starts: who is asked because of it
         self.food_turn = None       # day 2: the turn of the house's last food moment
+        self.holding = None         # day 2: (who, from whom) while someone decides about a handed portion
         if day != 4:
             return                  # day 2's opening is set up by next_day
         for p in self.people.values():
@@ -610,13 +611,18 @@ class Morning:
             return []
         plan = self.heard_plan(p)
         if self.day != 4:
-            return [self.food_line(), self.neighbour.get(p.id, NEIGHBOUR_UNKNOWN)] + ([plan] if plan else [])
+            return [self.food_line(p), self.neighbour.get(p.id, NEIGHBOUR_UNKNOWN)] + ([plan] if plan else [])
         return [data.ABOUT_FOOD, data.ABOUT_NEIGHBOUR] + ([plan] if plan else [])
 
-    def food_line(self):
-        """Day 2's "About food:" line: what the shelf holds, and what that means for those here."""
+    def food_line(self, p=None):
+        """Day 2's "About food:" line: what the shelf holds, and what that means for those here. For
+        whoever is deciding about a portion just handed to them (reports/body_fix.md), the line also
+        says they hold it and who handed it, and what it means counts that portion too."""
         n = self.portions
         k = sum(q.room is not None for q in self.people.values())
+        held = p is not None and self.holding is not None and self.holding[0] == p.id
+        if held:
+            n += 1
         if n == 0:
             so = "there is nothing to eat today"
         elif n < k:
@@ -625,6 +631,9 @@ class Morning:
             so = "there is one portion each, and nothing after that"
         else:
             so = f"there are {n // k} portions each, and nothing after that"
+        if held:
+            return (f"About food: the shelf holds {portions_text(self.portions)}, and you hold the portion "
+                    f"{NAMES[self.holding[1]]} has just handed you; there is no other food in the house, so {so}.")
         return f"About food: the shelf holds {portions_text(n)}, and there is no other food in the house, so {so}."
 
     def plan_text(self):
@@ -746,7 +755,9 @@ class Morning:
         q.triggers = []
         d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
              "held_back": None, "given_by": p.id}
+        self.holding = (q.id, p.id)             # while q decides, the portion is in q's hand
         choice, why = self.ask_model(q, t, opts, d, f"{p.name} has just handed you one of the portions.")
+        self.holding = None
         if not choice:
             d.update(mode="fallback", invalid=why, option="refuse_given", say=None)
         opt = next(o for o in opts if o.id == d["option"])
```
