# 05: results quality: how mornings are judged, and what the v5 runs look like

Read-only investigation, 2026-09-26. Nothing was run except read, search, hash and dump commands (listed at the end). No file was edited except this one. Paths are relative to the repo root (`C:\Users\Akrem\Desktop\Projects\Fallow`) unless they start with `runs/`, `cache/` or `REPORT`, which are relative to `Prototypes/llm-morning/`.

Where this file lives: there is no top-level `reports/` directory in the repo. `Prototypes/llm-morning/reports/` already exists (it holds `llm_call_audit.md`), so this file is `Prototypes/llm-morning/reports/state/05_results_quality.md`.

**Short answer to "which run do the reports rate best and worst": none.** No report gives a verdict, score or ranking for any v5 run. So the two excerpts below follow the fallback rule in the brief: seed 1 of two different scenarios. The two are `daniel_ate_it` (Gemma 4 31B), the scenario the target morning covers, and `mara_ate_it` (Flash Lite). They are the first two scenarios in REPORT-5's order.

---

## 1. The judging standard

### 1.1 The target morning, in full

Source: `Docs/understanding/target-morning.md`. The file is tracked in git (last commit `8b183d4`, 2026-09-26 00:31 +0100) and has no uncommitted changes.

> # Target morning: what a believable run looks like
>
> This is not a script. It describes the range of mornings we accept for the
> scenario `daniel_ate_it`, and it is the standard every change is judged
> against: run the narrator, read the story, check it against this file.
>
> ## The family
>
> - Elena, 42, the mother. She controls the food.
> - Daniel, 25, the eldest. He ate the can in the night, alone, unseen.
> - Leo, 21. He clashed with Daniel in the days before over who decides.
> - Mara, 17, the youngest.
>
> Nobody else. No zombies yet: the family's behaviour must be believable first.
>
> ## 1. Never (a run with any of these is wrong)
>
> - A person acts as if they do not know what they did. Daniel does not try to
>   "find out" what happened to the can he ate.
> - A person checks something they just watched someone else check, for the
>   same reason (three people counting the shelf Elena just counted).
> - A person keeps a fact from their own earlier act as if it never happened
>   (Elena counting again because her first count "does not count").
> - A person sits with someone who is busy searching, walking or leaving.
> - A person stops comforting someone because another family member joins them,
>   instead of staying or joining.
> - After the missing can is discovered, nobody says anything.
> - A person pictures a room as empty when they left people in it.
> - An important social choice (who to comfort, who to suspect) is settled by
>   chance alone when the people involved differ in ways that should matter.
> - Long stretches where everyone does nothing and nothing about them changes
>   in a way the story can show.
> - Everyone speaks at once and nobody answers the line before theirs.
> - A person repeats the same kind of line many turns in a row with no effect.
> - Someone who was wronged forgives within minutes, with no lasting cost.
> - A person mentions objects or places the house does not have.
>
> ## 2. Possible (each run should show some of these, never all by force)
>
> - Elena asks aloud who took the can.
> - Daniel lies, deflects or stays quiet, and shows it: avoids looking at
>   people, avoids Elena, avoids the kitchen or the food.
> - Daniel offers to search, to look innocent rather than to find anything.
> - Leo gets defensive ("don't look at me") or suspects Daniel.
> - Mara is scared or upset; she may defend someone, cry, or ask them to stop.
> - Elena tries to hold the family together ("we share what's left, nobody eats
>   alone").
> - Hunger is handled by a rule or an arrangement (Elena decides when and how
>   portions are shared), not by everyone standing still.
> - Someone questions Daniel directly, and that becomes a turning point.
> - Daniel confesses (more likely if honest and weighed down by guilt).
> - Daniel blames Leo or someone else (more likely if proud and afraid).
>
> ## 3. Should vary (between seeds and between personalities)
>
> - What Daniel does: silence, confession, or blaming someone.
> - Who suspects whom, and whether anyone suspects Daniel at all.
> - Whether and when the food is shared, and who decides.
> - Who comforts whom, for a reason the story can name.
>
> If every run tells the same story, the simulation is a script. If runs differ
> only by chance and not by who the people are, it is noise.
>
> ## How to judge a change
>
> 1. Run the narrator on `daniel_ate_it` with at least two seeds.
> 2. Count the "Never" items that appear. A change must not add any.
> 3. Note which "Possible" items appear.
> 4. A change is an improvement if Never items go down, or Possible items go up
>    with no new Never items, and the story reads more like four real people.
> 5. The final judge is a human reading the story, not a metric.

### 1.2 The second copy, and what REPORT-5 says about the file

- A second copy is the `## target-morning.md` section of `Docs/understanding/understanding-all.md` (lines 687–755). Compared with the file above, it lacks four Never lines: "Everyone speaks at once…", "A person repeats the same kind of line…", "Someone who was wronged forgives within minutes…" and "A person mentions objects or places…". The diff command and its output are at the end.
- `Prototypes/llm-morning/REPORT-5.md:195`:
  > **target-morning.md is no longer in `Docs/understanding/`.** It was removed at 12:56 UTC today; my commands in this step did not touch `Docs/`. The test that keeps its text out of every prompt now reads it from the file if it exists, else from its section in `Docs/understanding/understanding-all.md`. That copy predates the four Never lines added in the second step, so the test also checks those four lines verbatim from that step's brief.
- The file exists at that path today, committed in `8b183d4` ("LLM morning prototype, steps 1 to 5").

### 1.3 Criteria for the other two scenarios

- **Criteria written for `mara_ate_it` or `miscount`: NOT FOUND.** The target morning's scope is `daniel_ate_it` only ("the range of mornings we accept for the scenario `daniel_ate_it`").
- The only stated intent for those two scenarios is the `note` field of each variant in `Assets/_Project/Data/Scenario/morning.json`:
  - `mara_ate_it` (line 186): `"Seventeen, frightened, and it was there."`
  - `miscount` (line 236): `"Nobody took anything. There were only ever two. This one can never be solved, and is here to see what the house does with a question that has no answer."`

---

## 2. How judging is done

| What | By | Where | Quote |
|---|---|---|---|
| The standard's own procedure | a person | `Docs/understanding/target-morning.md`, "How to judge a change" | "The final judge is a human reading the story, not a metric." |
| The v5 report's stance | a person (the report only makes observations) | `Prototypes/llm-morning/REPORT-5.md:121` | "These are observations; the judge is a person reading the stories below." (REPORT.md:60, REPORT-2.md:50, REPORT-3.md:83 and REPORT-4.md:71 use the same sentence.) |
| The metrics table | a script | `Prototypes/llm-morning/metrics5.py`, run as `python metrics5.py` | docstring: "The metrics table for the fifth step: every run, whatever its scenario or model." REPORT-5.md:39: "`metrics5.py` computes every row from the runs' transcripts in the same way." |
| Keeping the standard out of the prompts | a unit test | `Prototypes/llm-morning/test_morning.py:199–222` (`test_nothing_from_target_morning_reaches_a_prompt`; the file path is set at :32) | line 222: `f"target-morning text in a prompt: {piece!r}"`. This is a leak guard, not a judgment of a run. |
| A model as judge | — | — | **NOT FOUND.** No code sends a story to a model for judging. `metrics5.py` does not call the model client (the search for `judge\|generate_content\|oracle` in it found nothing). |
| A count of Never items, or a list of Possible items, for any v5 run | — | — | **NOT FOUND.** Lines 1–1071 of REPORT-5 (everything before the stories) never mention "Never", "Possible", "Should vary" or "believ", except the file-status note at line 195. Earlier reports do name Never items for earlier runs: REPORT-2.md:54, REPORT-3.md:99, REPORT-4.md:77. |

---

## 3. Every v5 run

Scenario, seed and model come from each `runs/v5/<run>.meta.json`. The numbers come from the metrics table at `Prototypes/llm-morning/REPORT-5.md:18–37`, which is the output of `metrics5.py` (REPORT-5.md:984–1001). They are measurements, not a verdict or score. REPORT-5 gives no verdict or score for any run.

| Run (story path) | Scenario | Seed | Model | Verdict or score in the reports | Recorded metrics (REPORT-5.md row) | Run-specific statements in REPORT-5 |
|---|---|---|---|---|---|---|
| `runs/v5/daniel_ate_it-gemma-seed1.md` | daniel_ate_it | 1 | gemma-4-31b-it | NOT FOUND | :27. 21 calls, 0 invalid, 13 lines, no accusations, no confession, longest run 1 (Daniel, reassure), 0 repeated questions, 62% reassurance (8/13), longest quiet 18 min (36–54) | :130 "One line stands out. In seed 1, Leo at minute 63: "Daniel, you've been saying you're handling it for forty-five minutes. What exactly are you doing?" Nobody follows it up." · Grudge at minute 90 (:70): "Daniel against Leo, 1/3: named Leo in angry_at at minutes 15, 66." |
| `runs/v5/daniel_ate_it-gemma-seed2.md` | daniel_ate_it | 2 | gemma-4-31b-it | NOT FOUND | :28. 13 calls, 0 invalid, 9 lines, no accusations, no confession, longest run 1, 0 repeated questions, 78% reassurance (7/9), longest quiet 18 min (36–54) | :138 "Seed 2 needed four processes to finish (see its output)." |
| `runs/v5/daniel_ate_it-gemma-seed3.md` | daniel_ate_it | 3 | gemma-4-31b-it | NOT FOUND | :29. 20 calls, 0 invalid, 12 lines, no accusations, no confession, longest run 1, 0 repeated questions, 75% reassurance (9/12), longest quiet 18 min (36–54) | none beyond the Gemma-wide statements in section 4 |
| `runs/v5/daniel_ate_it-gemma-seed4.md` | daniel_ate_it | 4 | gemma-4-31b-it | NOT FOUND | :30. 19 calls, 0 invalid, 10 lines, no accusations, no confession, longest run 2 (Daniel, reassure), 0 repeated questions, 60% reassurance (6/10), longest quiet 18 min (36–54) | none beyond the Gemma-wide statements |
| `runs/v5/daniel_ate_it-gemma-seed5.md` | daniel_ate_it | 5 | gemma-4-31b-it | NOT FOUND | :31. 14 calls, 0 invalid, 8 lines, no accusations, no confession, longest run 1, 0 repeated questions, 75% reassurance (6/8), longest quiet 18 min (36–54) | none beyond the Gemma-wide statements |
| `runs/v5/mara_ate_it-seed1.md` | mara_ate_it | 1 | gemini-3.5-flash-lite | NOT FOUND | :32. 46 calls, 0 invalid, 36 lines, 4 true accusations (Daniel→Mara), culprit confessed min 27, longest run 3 (Daniel, accuse), 4 repeated questions, 39% reassurance (14/36), longest quiet 21 min (69–90) | :143 "Mara admits it at minutes 27, 9 and 0 (seeds 1 to 3)" · :146 "The event grudges fire as designed: admitting it after denying it (seeds 1 and 2), and eating in front of the hungry (seeds 1 and 3)." |
| `runs/v5/mara_ate_it-seed2.md` | mara_ate_it | 2 | gemini-3.5-flash-lite | NOT FOUND | :33. 37 calls, 0 invalid, 26 lines, 6 true accusations (Daniel→Mara), confessed min 09, longest run 3 (Daniel, accuse), 1 repeated question, 38% reassurance (10/26), longest quiet 18 min (36–54) | :143 and :146 (seeds 1 to 3, and seeds 1 and 2) |
| `runs/v5/mara_ate_it-seed3.md` | mara_ate_it | 3 | gemini-3.5-flash-lite | NOT FOUND | :34. 37 calls, 0 invalid, 25 lines, 7 true accusations (Daniel→Mara), confessed min 00, longest run 3 (Daniel, accuse), 0 repeated questions, 56% reassurance (14/25), longest quiet 21 min (69–90) | :143 and :146 (seeds 1 to 3, and seeds 1 and 3) |
| `runs/v5/miscount-seed1.md` | miscount | 1 | gemini-3.5-flash-lite | NOT FOUND | :35. 56 calls, 0 invalid, 41 lines, 9 false accusations (Mara↔Daniel), no culprit, longest run 3 (Daniel, accuse), 5 repeated questions, 29% reassurance (12/41), longest quiet 12 min (78–90) | :149 "In all three seeds Mara and Daniel accuse each other falsely, over and over." |
| `runs/v5/miscount-seed2.md` | miscount | 2 | gemini-3.5-flash-lite | NOT FOUND | :36. 93 calls, 0 invalid, 81 lines, 30 false accusations (Mara↔Daniel, Leo→Daniel), no culprit, longest run 3 (Daniel, accuse), 3 repeated questions, 35% reassurance (28/81), longest quiet 6 min (60–66) | :149 "…in seeds 2 and 3 Leo turns on Daniel too." · :973 the run crashed on "a Windows file lock on the cache file, after which the run resumed from its 9 cached answers." |
| `runs/v5/miscount-seed3.md` | miscount | 3 | gemini-3.5-flash-lite | NOT FOUND | :37. 70 calls, 0 invalid, 52 lines, 18 false accusations (Mara↔Daniel, Leo→Daniel), no culprit, longest run 3 (Daniel, ask), 7 repeated questions, 27% reassurance (14/52), longest quiet 12 min (78–90) | :149 (seeds 2 and 3) |

REPORT-5.md:18–37 also has five v4 rows (daniel_ate_it, Flash Lite, seeds 1–5). They are there for comparison and are not v5 runs: "The first five rows are the v4 runs, for comparison." (REPORT-5.md:39).

---

## 4. Failures and weaknesses the reports name

All from `Prototypes/llm-morning/REPORT-5.md`, quoted as written, unless another path is given.

**Gemma 4 31B on daniel_ate_it**
- :125 "**Gemma's family is even quieter.**"
- :128 "Reassurance is 60% to 78% of its lines, against 20% to 50% for Flash Lite."
- :129 "Daniel never confesses (Flash Lite: once in five). Gemma's Daniel does not deny it much either; he plays the leader: "I've got this, everyone. Just keep calm and trust me.""
- :130 "…Leo at minute 63: "Daniel, you've been saying you're handling it for forty-five minutes. What exactly are you doing?" Nobody follows it up."
- :131 "**Gemma's five mornings are nearly the same morning.**"
- :133 "After that, each run's inner moments fall at exactly the same minutes: 15, 30, 33, 54, 63, 66 and 75. Those are the minutes when each person's hunger crosses a level, and the hunger rates are fixed."
- :134 "So the skeleton of all five stories is the rules' hunger clock; only the words change ("I'm so hungry, I can't think" from Mara at minute 54 in four of the five)."
- :135 "Different seeds gave Gemma very little variety."
- :136 "**So the daniel_ate_it stalemate is not a Flash Lite quirk.** Both models leave Daniel unchallenged. Flash Lite fills the silence with repeated questions and denials; Gemma just goes quiet."
- :138 "**Gemma's free endpoint was the practical problem.** Its five runs needed 213 requests for 87 answers; the other 126 were refused with 500 or 503 errors and retried."

**Across scenarios (Flash Lite)**
- :152–153 "**The same backstory gives very different mornings depending on who took the can.** The one clear rule effect: the rules do not offer "ask who took the can" to someone who knows who took it. So a guilty Daniel cannot make his most natural move, which he makes over and over when innocent…"
- :154 "In daniel_ate_it the only accusations of Daniel come after he confesses, or from his own false one against Leo."
- :157 ""Who took the can?" still gets asked again unanswered: 0 to 8 times a run."
- :158 "Nobody took anyone aside in any of the 16 runs."
- :159 "In 12 of the 16 the longest quiet stretch is minutes 36 to 54, or starts at 69 or 78. That gap sits between hunger crossings, whatever the scenario or model."

**The report's own sorting of problems** (:163–169)
- "**General, seen in every scenario and with both models:**" "Quiet stretches are set by the hunger clock." · "Take-aside is never used." · "A large share of reassurance." · "Questions repeated without an answer (not with Gemma, which hardly asks)."
- "**This scenario:** the stalemate. It comes from the culprit being the proud leader whom nobody suspects, and who, knowing the answer, is never offered the question."
- "**This model:** Flash Lite's repeated questions and denials, and Gemma's passivity and near-identical mornings across seeds."

**Run failures (process, not story)**
- miscount seed 2 crash, REPORT-5.md:876: `PermissionError: [WinError 5] Access is denied: '…\\cache\\v5\\gemini-3.5-flash-lite-miscount-seed2.json.tmp' -> '…\\cache\\v5\\gemini-3.5-flash-lite-miscount-seed2.json'`, then at :877 "--- resumed at 13:53 UTC after the crash above (a Windows file lock on the cache file); the 8 cached answers are reused ---". (The next line says the cache "holds 9 answers"; :973 says "resumed from its 9 cached answers".)
- Gemma seed 2 stops, REPORT-5.md:434, :454, :474: "stopped: still refused (503 UNAVAILABLE) after 6 retries." / "(500 INTERNAL)" / "(503 UNAVAILABLE)".
- A request-count mismatch, `Prototypes/llm-morning/reports/llm_call_audit.md:76`: "Gemma: 216 / 5 = 43.2 requests per run (range 36–49). REPORT-5.md:138 and :974 say **213**; the gap of 3 is note ²."

**Named weaknesses that are not in REPORT-5**: NOT FOUND. No other document found by the searches below discusses the v5 runs' story quality.

---

## 5. Excerpt A: daniel_ate_it, Gemma 4 31B, seed 1, minutes 00–15

**Why this run:** the brief's fallback (no report rates any run), seed 1 of the `daniel_ate_it` scenario.
**Source:** `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed1.md`, lines 62–84: the blocks **min 00** through **min 15**, which cover minutes 00–17. The file's SHA-256 is `a564d9d7…9bd9c385c`, the same as `story_sha256` in its `.meta.json`. The raw record is `runs/v5/daniel_ate_it-gemma-seed1.transcript.json`.

The story text, verbatim. The story itself groups identical routine turns (for example "minutes 03–12 (4 decisions, the same each time)"):

**min 00** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “Don't worry. I'll figure out this out and I'll make sure we're all safe.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to maintain my position of authority and protect my family, even if I'm the oldest.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't worry. I'll figure out this out and I'll make sure we're all safe.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *skeptical*. Reason: “Daniel is attempting to take charge again, but his promises don't find the missing food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't worry. I'll figure out this out and I'll make sure we're all safe.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I need to observe my children and see how they react to Daniel's confidence.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't worry. I'll figure out this out and I'll make sure we're all safe.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *anxious*. Reason: “I'm too scared to accuse anyone when things are already so tense.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: ask everyone here who took the can**, saying “Who took the can?” *(new: a question)* (one of 22 options). Feeling: *curious*. Reason: “We need to know the truth to manage our food properly.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Who took the can?". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I need to wait and see if anyone admits it before I react.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Who took the can?". **Chose: deny taking it**, saying “I didn't take it, Leo. Stop asking.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I need to maintain my authority and protect the family, so I cannot admit I ate it.” Suspects: nobody, so suspicion none. Angry at: Leo; grudge against Leo rose to 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Who took the can?"; Daniel denies taking it, to everyone: "I didn't take it, Leo. Stop asking.". **Chose: deny taking it**, saying “I didn't take it either!” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “Leo is asking everyone, and I want them to know I'm honest.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation starts (minute 15): Leo: a question.*

The same minutes as recorded in `daniel_ate_it-gemma-seed1.transcript.json`, one row per act. The field values are unchanged (`words` shown as a JSON string, empty when `null`). `mode` is `model` when the model chose and `routine` when the rules did:

| minute | who | room | mode | option | words | came_of_it |
|---|---|---|---|---|---|---|
| 00 | daniel | kitchen | model | reassure_all | "Don't worry. I'll figure out this out and I'll make sure we're all safe." | said to Elena, Leo, Mara. |
| 00 | leo | kitchen | model | silent |  | stayed where they were. |
| 00 | elena | kitchen | model | silent |  | stayed where they were. |
| 00 | mara | kitchen | model | silent |  | stayed where they were. |
| 03 | elena | kitchen | routine | silent |  | stayed where they were. |
| 03 | leo | kitchen | routine | silent |  | stayed where they were. |
| 03 | mara | kitchen | routine | silent |  | stayed where they were. |
| 03 | daniel | kitchen | routine | silent |  | stayed where they were. |
| 06 | leo | kitchen | routine | silent |  | stayed where they were. |
| 06 | mara | kitchen | routine | silent |  | stayed where they were. |
| 06 | elena | kitchen | routine | silent |  | stayed where they were. |
| 06 | daniel | kitchen | routine | silent |  | stayed where they were. |
| 09 | leo | kitchen | routine | silent |  | stayed where they were. |
| 09 | mara | kitchen | routine | silent |  | stayed where they were. |
| 09 | daniel | kitchen | routine | silent |  | stayed where they were. |
| 09 | elena | kitchen | routine | silent |  | stayed where they were. |
| 12 | daniel | kitchen | routine | silent |  | stayed where they were. |
| 12 | mara | kitchen | routine | silent |  | stayed where they were. |
| 12 | elena | kitchen | routine | silent |  | stayed where they were. |
| 12 | leo | kitchen | routine | silent |  | stayed where they were. |
| 15 | leo | kitchen | model | ask_who | "Who took the can?" | said to Daniel, Elena, Mara. |
| 15 | elena | kitchen | model | silent |  | stayed where they were. |
| 15 | daniel | kitchen | model | deny | "I didn't take it, Leo. Stop asking." | said to Elena, Leo, Mara. |
| 15 | mara | kitchen | model | deny | "I didn't take it either!" | said to Daniel, Elena, Leo. |

---

## 6. Excerpt B: mara_ate_it, Flash Lite, seed 1, minutes 00–15

**Why this run:** the brief's fallback, seed 1 of a second scenario, `mara_ate_it`.
**Source:** `Prototypes/llm-morning/runs/v5/mara_ate_it-seed1.md`, lines 62–101: the blocks **min 00** through **min 15**, which cover minutes 00–17. The file's SHA-256 is `a0f20d98…b1175f0e`, the same as `story_sha256` in its `.meta.json`. The raw record is `runs/v5/mara_ate_it-seed1.transcript.json`.

The story text, verbatim:

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Who took the can? Someone has to explain this right now.” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to find out who took the food before things get completely out of hand.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calmly observant*. Reason: “Yelling won't find the can, so I am watching everyone's reaction first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now.". **Chose: reassure everyone here**, saying “Let us calm down, no one here would steal from their own family.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I must keep them from turning on each other before this house tears itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now."; Elena reassures everyone: "Let us calm down, no one here would steal from their own family.". **Chose: deny taking it**, saying “I didn't take anything. Why are you all looking at me like that?” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *terrified*. Reason: “I am so scared they will find out I ate the can that I have to deny it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (terrified)). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). **Chose: deny taking it**, saying “I already told you, I didn't take anything. Stop looking at me like that.” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *terrified*. Reason: “I am too scared to admit I ate the can, so I have to keep lying.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything. Why are you all looking at me like that?"; Mara denies taking it, to everyone: "I already told you, I didn't take anything. Stop looking at me like that."; Mara looks terrified. **Chose: reassure everyone here**, saying “Let us not turn on each other, we will figure this out together.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and prevent the family from tearing itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us calm down, no one here would steal from their own family."; Mara denies taking it, to everyone: "I didn't take anything. Why are you all looking at me like that?"; Mara denies taking it, to everyone: "I already told you, I didn't take anything. Stop looking at me like that."; Elena reassures everyone: "Let us not turn on each other, we will figure this out together."; Mara looks terrified. **Chose: stay put and say nothing** (one of 21 options). Feeling: *calmly observant*. Reason: “Accusing anyone without facts solves nothing, so I will watch how they react.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let us calm down, no one here would steal from their own family."; Mara denies taking it, to everyone: "I didn't take anything. Why are you all looking at me like that?"; Mara denies taking it, to everyone: "I already told you, I didn't take anything. Stop looking at me like that."; Elena reassures everyone: "Let us not turn on each other, we will figure this out together."; Mara looks terrified. **Chose: ask everyone here who took the can**, saying “Someone has to answer me right now. Who took the can?” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I need to get to the bottom of this before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 06** · kitchen: Daniel searching the kitchen, Elena searching the kitchen, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (terrified)). Social moment: Elena reassures everyone: "Let us not turn on each other, we will figure this out together."; Daniel asks everyone who took the can: "Someone has to answer me right now. Who took the can?". **Chose: deny taking it**, saying “I didn't touch it, Daniel! Why do you keep staring at me like that?” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *extremely anxious*. Reason: “I am terrified they will find out I ate the can, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone has to answer me right now. Who took the can?"; Mara denies taking it, to everyone: "I didn't touch it, Daniel! Why do you keep staring at me like that?". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calmly observant*. Reason: “There is no proof yet, so staying quiet and watching everyone is the wisest course.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone has to answer me right now. Who took the can?"; Mara denies taking it, to everyone: "I didn't touch it, Daniel! Why do you keep staring at me like that?". **Chose: search the kitchen for the can (takes about six minutes)**, saying “Let us check the room properly before we point fingers at anyone.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *deeply anxious*. Reason: “I need to find out the truth myself without letting them tear each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara denies taking it, to everyone: "I didn't touch it, Daniel! Why do you keep staring at me like that?"; Elena says to everyone, while searching: "Let us check the room properly before we point fingers at anyone.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “Keep looking, Mom is right, we need to check every inch of this room.” *(not new: a remark (the rules cannot tell what free words add))* (one of 19 options). Feeling: *anxious*. Reason: “I need to take charge and find where that can went before things get out of hand.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 09** · kitchen: Daniel standing, Elena standing, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while searching: "Keep looking, Mom is right, we need to check every inch of this room."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: carry on searching the kitchen** (one of 20 options). Feeling: *deeply anxious*. Reason: “I must keep looking through the kitchen to make sure we have not missed any sign of the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- *The kitchen's conversation starts (minute 09): Daniel finished searching the kitchen and found nothing.*

**min 12** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “Someone has to step up and tell the truth right now. Who took the can?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *anxious*. Reason: “I need to take charge and get a straight answer before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place; Elena finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "Someone has to step up and tell the truth right now. Who took the can?". **Chose: deny taking it**, saying “I didn't take it! Why is everyone looking at me like I'm a thief?” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *very anxious*. Reason: “I am too scared to admit I ate it, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone has to step up and tell the truth right now. Who took the can?"; Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me like I'm a thief?". **Chose: reassure everyone here**, saying “Let us calm down and breathe, we are going to get through this together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep the family from tearing itself apart before we starve.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place; Elena finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "Someone has to step up and tell the truth right now. Who took the can?"; Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me like I'm a thief?"; Elena reassures everyone: "Let us calm down and breathe, we are going to get through this together.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “Arguing solves nothing until we look at the actual facts.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 15** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 23 options). Feeling: *hungry*. Reason: “Accusing each other gets us nowhere, so I am going to look for actual evidence.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Elena, minutes 15–18 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me like I'm a thief?"; Elena reassures everyone: "Let us calm down and breathe, we are going to get through this together.". **Chose: ask everyone here who took the can**, saying “Nobody is answering me. I want to know right now who took the can.” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to get an answer because someone is lying and hiding the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let us calm down and breathe, we are going to get through this together."; Daniel asks everyone who took the can: "Nobody is answering me. I want to know right now who took the can.". **Chose: deny taking it**, saying “I already told you, I didn't take it! Stop asking me over and over again.” *(not new: a denial with no new accusation to answer)* (one of 18 options). Feeling: *anxious*. Reason: “I cannot admit I ate it or they will hate me, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation ends (minute 18): 2 full turns in a row with nothing new.*

The same minutes as recorded in `mara_ate_it-seed1.transcript.json`:

| minute | who | room | mode | option | words | came_of_it |
|---|---|---|---|---|---|---|
| 00 | daniel | kitchen | model | ask_who | "Who took the can? Someone has to explain this right now." | said to Elena, Leo, Mara. |
| 00 | leo | kitchen | model | silent |  | stayed where they were. |
| 00 | elena | kitchen | model | reassure_all | "Let us calm down, no one here would steal from their own family." | said to Daniel, Leo, Mara. |
| 00 | mara | kitchen | model | deny | "I didn't take anything. Why are you all looking at me like that?" | said to Daniel, Elena, Leo. |
| 03 | mara | kitchen | model | deny | "I already told you, I didn't take anything. Stop looking at me like that." | said to Daniel, Elena, Leo. |
| 03 | elena | kitchen | model | reassure_all | "Let us not turn on each other, we will figure this out together." | said to Daniel, Leo, Mara. |
| 03 | leo | kitchen | model | silent |  | stayed where they were. |
| 03 | daniel | kitchen | model | ask_who | "Someone has to answer me right now. Who took the can?" | said to Elena, Leo, Mara. |
| 06 | mara | kitchen | model | deny | "I didn't touch it, Daniel! Why do you keep staring at me like that?" | said to Daniel, Elena, Leo. |
| 06 | leo | kitchen | model | silent |  | stayed where they were. |
| 06 | elena | kitchen | model | search | "Let us check the room properly before we point fingers at anyone." | started going through the room. |
| 06 | daniel | kitchen | model | search | "Keep looking, Mom is right, we need to check every inch of this room." | started going through the room. |
| 09 | leo | kitchen | routine | silent |  | stayed where they were. |
| 09 | mara | kitchen | routine | silent |  | stayed where they were. |
| 09 | daniel | kitchen | routine | keep_searching |  | went through the room and found nothing. |
| 09 | elena | kitchen | model | keep_searching |  | went through the room and found nothing. |
| 12 | daniel | kitchen | model | ask_who | "Someone has to step up and tell the truth right now. Who took the can?" | said to Elena, Leo, Mara. |
| 12 | mara | kitchen | model | deny | "I didn't take it! Why is everyone looking at me like I'm a thief?" | said to Daniel, Elena, Leo. |
| 12 | elena | kitchen | model | reassure_all | "Let us calm down and breathe, we are going to get through this together." | said to Daniel, Leo, Mara. |
| 12 | leo | kitchen | model | silent |  | stayed where they were. |
| 15 | leo | kitchen | model | search |  | started going through the room. |
| 15 | elena | kitchen | routine | silent |  | stayed where they were. |
| 15 | daniel | kitchen | model | ask_who | "Nobody is answering me. I want to know right now who took the can." | said to Elena, Leo, Mara. |
| 15 | mara | kitchen | model | deny | "I already told you, I didn't take it! Stop asking me over and over again." | said to Daniel, Elena, Leo. |

---

## 7. NOT FOUND

1. A verdict, score or rating for any of the 11 v5 runs, in REPORT-5, `reports/llm_call_audit.md`, `Docs/understanding/commit-log.md` or any other file that names the v5 runs.
2. A best or worst v5 run named in any report. The excerpts use the brief's seed-1 fallback because of this.
3. A count of target-morning "Never" items, or a list of "Possible" or "Should vary" items, for any v5 run.
4. A target morning or judging criteria for `mara_ate_it` or `miscount`. Only the scenario `note` fields exist (section 1.3).
5. A model or LLM used as a judge of stories.
6. Named weaknesses of the v5 runs outside REPORT-5 and `reports/llm_call_audit.md`.
7. A top-level `reports/` directory at the repo root. This file went to `Prototypes/llm-morning/reports/state/` instead.

---

## 8. Commands used and their output

Run from the repo root, or from `Prototypes/llm-morning/` where the path shows it, in Git Bash. None of them writes to the repo. The two scratch files (`acts.py` and the excerpt files) were in the session scratchpad, outside the repo.

**Find the prototype, its runs and any existing `reports/state`**
```bash
ls Prototypes/llm-morning; ls -R Prototypes/llm-morning/runs/v5; ls reports; ls Prototypes/llm-morning/reports
find . -path ./Library -prune -o -type d -name state -print; find . -name "0?_*.md" -not -path "./Library/*"
```
```
runs/v5: 11 runs × {.md, .meta.json, .stdout.txt, .transcript.json}, plus gemma-models.stdout.txt,
         metrics5.stdout.txt, probe-gemma-seed2.stdout.txt, unittest.stdout.txt, v4-replay.stdout.txt
ls: cannot access 'reports': No such file or directory
llm_call_audit.md
(find: no output)
```

**Find judging documents**
```bash
git ls-files | grep -i -E "target|criteri|judg|verdict|rubric|believab"
git log --oneline -3 -- Docs/understanding/target-morning.md; git status --short Docs/understanding/
```
```
Docs/understanding/target-morning.md
8b183d4 LLM morning prototype, steps 1 to 5
?? Docs/understanding/commit-log.md
```

**Compare target-morning.md with its copy in understanding-all.md**
```bash
sed -n 687,760p Docs/understanding/understanding-all.md | sed 's/^#### /## /; s/^### /# /' > "$TEMP/ua.md"
diff <(sed 's/[[:space:]]*$//' Docs/understanding/target-morning.md) <(sed 's/[[:space:]]*$//' "$TEMP/ua.md" | tail -n +3)
```
```
33,36d32
< - Everyone speaks at once and nobody answers the line before theirs.
< - A person repeats the same kind of line many turns in a row with no effect.
< - Someone who was wronged forgives within minutes, with no lasting cost.
< - A person mentions objects or places the house does not have.
71a68,72
>
> ---
>
> ## runs/daniel_ate_it-1.md
>
```
(`$TEMP/ua.md` is a temp file outside the repo. The `71a68,72` lines are the start of the next merged section, not part of the target morning.)

**Find every document that mentions the v5 runs**
```bash
grep -rl -E "runs/v5|REPORT-5|gemma-seed|miscount-seed|mara_ate_it-seed" --include=*.md --include=*.txt --include=*.py --include=*.json . | grep -v -E "^./(Library|Temp)/" | grep -v "/cache/"
```
```
./Docs/understanding/commit-log.md
./Prototypes/llm-morning/metrics5.py
./Prototypes/llm-morning/REPORT-5.md
./Prototypes/llm-morning/reports/llm_call_audit.md
./Prototypes/llm-morning/runs/v5/<each run>.meta.json and .stdout.txt   (22 files)
./Prototypes/llm-morning/test_morning.py
```
`commit-log.md` only lists the v5 file paths (lines 164–314). `llm_call_audit.md` counts API requests and tokens and gives no story verdict. The search below found no judging words in either file:
```bash
grep -n -i -E "v5|REPORT-5|gemma|miscount|mara_ate|best|worst|believ|verdict|judg" Docs/understanding/commit-log.md Prototypes/llm-morning/reports/llm_call_audit.md
```
(Output: only path lists and request/token tables. No line contains best, worst, believ, verdict or judg.)

**Search the reports and code for judging**
```bash
grep -n -i -E "judge|target-morning|target morning|never item|possible item|believab" Prototypes/llm-morning/REPORT*.md Prototypes/llm-morning/*.py Docs/understanding/understanding-all.md Docs/understanding/morning-walkthrough.md Docs/understanding/narrator-setup.md
```
```
REPORT-2.md:50:These are observations; the judge is a person reading the stories below.
REPORT-2.md:54:… The last 84, 63 and 81 minutes are everyone staying put in silence: the target's Never item "Long stretches where everyone does nothing". …
REPORT-2.md:71:- **`target-morning.md` was not changed.** …
REPORT-2.md:74:  - `talk.py` holds the newness and conversation rules, shared by the simulation and the metrics, so old and new runs are judged by the same code;
REPORT-3.md:83:These are observations; the judge is a person reading the stories below.
REPORT-3.md:99:  - Seed 2: all three forgive him within three minutes of the confession ("It is okay, Daniel") … That is the target's Never item "Someone who was wronged forgives within minutes, with no lasting cost". …
REPORT-4.md:71:These are observations; the judge is a person reading the stories below.
REPORT-4.md:77:  … That is close to the target's Never item "A person repeats the same kind of line many turns in a row with no effect".
REPORT-5.md:121:These are observations; the judge is a person reading the stories below.
REPORT-5.md:195:- **target-morning.md is no longer in `Docs/understanding/`.** …
REPORT.md:30: … Ages and roles match `target-morning.md`; nothing else from that file is used. |
REPORT.md:43: … It contains no target-morning text; a test checks every sentence of that file against every prompt.
REPORT.md:60:These are observations; the judge is a person reading the stories below.
data.py:10:Ages and family roles match Docs/understanding/target-morning.md. Nothing else from that
test_morning.py:32:TARGET = os.path.join(HERE, "..", "..", "Docs", "understanding", "target-morning.md")
test_morning.py:204:            self.skipTest("neither target-morning.md nor its copy in understanding-all.md was found")
test_morning.py:222:                self.assertNotIn(piece.lower(), p.lower(), f"target-morning text in a prompt: {piece!r}")
understanding-all.md:687:## target-morning.md
understanding-all.md:748:#### How to judge a change
understanding-all.md:755:5. The final judge is a human reading the story, not a metric.
```
(Some lines are shortened with "…". Every REPORT-5 line after 1071 is excluded because it is story text.)

**Check for Never/Possible judgments in REPORT-5, and for a model judge in metrics5.py**
```bash
cd Prototypes/llm-morning
awk 'NR<=1071' REPORT-5.md | grep -n -E "Never|Possible|Should vary|believ"
grep -n -i -E "judge|generate_content|oracle" metrics5.py
```
```
195:- **target-morning.md is no longer in `Docs/understanding/`.** … That copy predates the four Never lines added in the second step, …
(metrics5.py: no output)
```

**Scenario, seed and model of each run**
```bash
cd Prototypes/llm-morning/runs/v5
for f in *.meta.json; do python -c "import json;d=json.load(open('$f'));print('$f',d['scenario'],d['seed'],d['model'],d['model_decisions'],d['lines_spoken'],d['story'])"; done
```
```
daniel_ate_it-gemma-seed1.meta.json daniel_ate_it 1 gemma-4-31b-it 21 13 runs/v5/daniel_ate_it-gemma-seed1.md
daniel_ate_it-gemma-seed2.meta.json daniel_ate_it 2 gemma-4-31b-it 13 9 runs/v5/daniel_ate_it-gemma-seed2.md
daniel_ate_it-gemma-seed3.meta.json daniel_ate_it 3 gemma-4-31b-it 20 12 runs/v5/daniel_ate_it-gemma-seed3.md
daniel_ate_it-gemma-seed4.meta.json daniel_ate_it 4 gemma-4-31b-it 19 10 runs/v5/daniel_ate_it-gemma-seed4.md
daniel_ate_it-gemma-seed5.meta.json daniel_ate_it 5 gemma-4-31b-it 14 8 runs/v5/daniel_ate_it-gemma-seed5.md
mara_ate_it-seed1.meta.json mara_ate_it 1 gemini-3.5-flash-lite 46 36 runs/v5/mara_ate_it-seed1.md
mara_ate_it-seed2.meta.json mara_ate_it 2 gemini-3.5-flash-lite 37 26 runs/v5/mara_ate_it-seed2.md
mara_ate_it-seed3.meta.json mara_ate_it 3 gemini-3.5-flash-lite 37 25 runs/v5/mara_ate_it-seed3.md
miscount-seed1.meta.json miscount 1 gemini-3.5-flash-lite 56 41 runs/v5/miscount-seed1.md
miscount-seed2.meta.json miscount 2 gemini-3.5-flash-lite 93 81 runs/v5/miscount-seed2.md
miscount-seed3.meta.json miscount 3 gemini-3.5-flash-lite 70 52 runs/v5/miscount-seed3.md
```

**Scenario notes for the two new variants**
```bash
sed -n 180,260p Assets/_Project/Data/Scenario/morning.json
```
(Output quoted in section 1.3: the `note` lines at 186 and 236.)

**Locate the minute blocks and check the story files are unchanged**
```bash
cd Prototypes/llm-morning/runs/v5
grep -n "^\*\*min " daniel_ate_it-gemma-seed1.md | head -8; grep -n "^\*\*min " mara_ate_it-seed1.md | head -8
sha256sum daniel_ate_it-gemma-seed1.md mara_ate_it-seed1.md
```
```
62:**min 00** … 69:**min 03** … 75:**min 06** … 78:**min 15** … 85:**min 18** …   (daniel_ate_it-gemma-seed1.md)
62:**min 00** … 69:**min 03** … 75:**min 06** … 82:**min 09** … 89:**min 12** … 95:**min 15** … 102:**min 18** …   (mara_ate_it-seed1.md)
a564d9d71f5e6b2c2d19209e65188c5d1d3d62085428518692572901bd9c385c *daniel_ate_it-gemma-seed1.md
a0f20d98c84ef230929f723078188e2b0da86082d54263682c7f3a74b1175f0e *mara_ate_it-seed1.md
```
Both match `story_sha256` in their `.meta.json` (and REPORT-5.md:396 and :719).

**Extract the excerpts**
```bash
sed -n 62,84p  runs/v5/daniel_ate_it-gemma-seed1.md   # Excerpt A, story text
sed -n 62,101p runs/v5/mara_ate_it-seed1.md           # Excerpt B, story text
python acts.py runs/v5/daniel_ate_it-gemma-seed1.transcript.json 0 15   # Excerpt A, transcript rows
python acts.py runs/v5/mara_ate_it-seed1.transcript.json 0 15           # Excerpt B, transcript rows
```
The output of each command is the corresponding excerpt in sections 5 and 6, pasted without changes. `acts.py`, a scratch script outside the repo:
```python
"""Print every recorded act from a transcript.json between two minutes, fields verbatim."""
import json, sys
path, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(path, encoding="utf-8"))
print("| minute | who | room | mode | option | words | came_of_it |")
print("|---|---|---|---|---|---|---|")
for t in d["turns"]:
    for a in t["acts"]:
        if lo <= a["minute"] <= hi:
            w = "" if a["words"] is None else json.dumps(a["words"], ensure_ascii=False)
            print(f"| {a['minute']:02d} | {a['who']} | {a['room']} | {a['mode']} | {a['option']} | {w} | {a['came_of_it']} |")
```

**Read in full or in part:** `CLAUDE.md`, `Prototypes/llm-morning/REPORT-5.md` (lines 1–1100, plus headings), `Docs/understanding/target-morning.md`, the two story files and transcripts above, and the meta files of all 11 runs.
