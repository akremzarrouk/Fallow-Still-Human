# Fallow: audit and direction, November 2026

Written 2026-11-11 by Claude Fable 5.2. MODE: design. No code, test, prompt or data file was changed. This file is
the only file written in the repository. Nothing was sent to the Gemini API. Paths are relative to the repository
root. `[E7]` and the like point to the evidence appendix at the end, which lists every command run and its key
output. Anything I could not check is marked **NOT VERIFIED** and listed in section 14.

---

## 0. Plain-language summary

**Where the project is.** There are two separate attempts at the same game in this repository.

1. **The Unity/C# simulation** (10 to 24 September). Four people who decide what to do from rules about wants and
   feelings. Nobody speaks, there is no player, and nothing is drawn on screen. Its own README says three of the
   four people stand still for most of a morning.
2. **The Python prototype** (25 September to 15 October). Code keeps the house, the bodies, the water, the weather
   and who saw what. A free Google model (Gemini) picks what each person does from a list and writes what they
   say. This is where you can play Leo.

**The one finding that matters most.** In the Python prototype, the code decides nothing a person does except
"stay silent" and "sleep". I ran a ten-day week with the model made to answer nothing: 484 acts, of which 448 were
"stay silent" and 36 were "sleep", and not one word was spoken `[E10]`. So the game today does not run without
the model. Everything a person does is the model's.

**Why you felt stuck.** For three weeks the work was trying to make a small free model behave like a family by
changing the wording of what it is told. The project's own probes show this does not work: across four different
wordings of the same moment, Elena chose "reassure everyone" 6 times out of 6 every time, and Mara chose "accuse
Daniel" 6 out of 6 every time (`Prototypes/llm-morning/reports/calm_variants.md:34-36`). Each attempt cost a
design note, an implementation note, a probe plan and a probe report. There are 115 such reports, about 69,000
lines, against about 10,000 lines of game code `[E5]`. The testing was careful and honest. It was testing the
wrong thing: a model you do not control, instead of a game you do.

**What I recommend.**

- **Code decides everything.** Each person gets a small code "brain": needs that build up, a temperament, what they
  know, how they stand with each other person. In each situation the brain scores the few things that person
  could do and picks one. No model is called while the game runs.
- **Keep the Python prototype's world. Do not port to C# now.** The part of the Python code that keeps the truth
  (who saw what, bodies, water, weather, the street, the nights) works and is tested. Porting would use up the
  whole Fable window and produce no new game. Port once, later, when an hour of play has been judged good.
- **Leave the Unity/C# simulation as it is.** It is a finished experiment, not the game.
- **Change the scenario a little.** Today the family has two portions of food and then nothing for ten days, so
  there are no meals, no sharing and nothing to decide. Give them food for about four days, so that meals, fairness
  and the night trips matter.
- **An LLM is not needed in the game at all.** It is worth using only outside the game, to draft many versions of
  each spoken line that you then keep in a file. Later, and only as an option that can be switched off, it could
  turn a sentence the player types into one of the game's own choices.
- **Change the method.** Each day ends with something you read or play for fifteen minutes, not with a report.

**What the next five days are.** 12 Nov: the code brain replaces the model, and the game runs with the model off.
13 Nov: feelings, trust and suspicion kept by code; food and meals. 14 Nov: a full seven-day week with something
new each day. 15 Nov: the spoken lines and a short diary of the week that you read. 16 Nov: you play Leo for an
hour. Each day has a pass/fail test, defined in sections 8 to 10.

**What I am not sure of.** Whether code-chosen behaviour with written lines will make you *care* cannot be proved
on paper. The plan puts a readable week in front of you on 15 Nov and a playable hour on 16 Nov so that you find
out early, and section 13 says what to do if the answer is no.

---

## 1. What is in the repository

| Part | Where | Size | State |
|---|---|---|---|
| C# simulation core | `Assets/_Project/Scripts/Core` | 8,554 lines `[E3]` | No speech, no player, no scene |
| C# tests and experiments | `Assets/_Project/Tests/EditMode` | 28,586 lines, 456 test cases `[E3][E12]` | Last recorded run 454 of 456 passed, 3 h 5 min, on 2026-09-24 `[E12]` |
| Python prototype | `Prototypes/llm-morning/*.py` | 10,172 lines in 18 modules `[E5]` | Runs; every act is the model's |
| Python tests | `Prototypes/llm-morning/test_morning.py` | 9,457 lines, 349 tests `[E5][E7]` | 208 run and pass, 141 are skipped `[E7]` |
| Frozen copies of old versions | `Prototypes/llm-morning/v1` to `v14` | 14 folders `[E5]` | Kept only to replay old runs |
| Reports | `Prototypes/llm-morning/reports/*.md`, `REPORT*.md` | 115 files, 69,406 lines; plus 7,863 `[E5]` | |
| Slice and experiment docs | `Docs/` | 160 Markdown files `[E5]` | |
| Play sessions | `Prototypes/llm-morning/runs/play/` | 3 sessions `[E15]` | The longest reached day 1, minute 30 |

History: 184 commits; 62 up to 24 September (the C# work), 122 after (the Python work); the last on 15 October
`[E4]`. Nothing has been committed for 27 days. The current branch `quiet-day-stage-a` is 50 commits ahead of its
copy on GitHub `[E13]`, so five weeks of work exist only on this computer.

---

## 2. What works and what does not

### 2.1 Works

| # | Claim | Evidence |
|---|---|---|
| W1 | The Python engine plays a whole ten-day week from start to end with no API, in 19 seconds. | `[E8]`: exit 0, `run_seconds: 19.4`, 568 asks answered by the fake model |
| W2 | The Python suite passes: 349 tests, OK, 141 skipped, 226 s. | `[E7]` |
| W3 | Code already owns the physical truth: weather by seed, water in litres, fasting, thirst and sleep debt, a street of households that come to the door, night trips with outcomes. | `[E8]` (the run prints each day's weather and a visit on day 6); `Prototypes/llm-morning/quiet.py:27-40`, `truth.py:49-70`, `street.py:72`, `night.py:772` |
| W4 | Code records what happened and who perceived it, and nobody's view can read the truth: the world object raises an error if it is read while a person's view is being built. | `Prototypes/llm-morning/chronicle.py:101-149`; `truth.py:21-47` |
| W5 | The player's screen is built only from what Leo perceived, and a scripted-player test class covers it. | `Prototypes/llm-morning/reports/play_design.md:12-13`; `test_morning.py:8869` |
| W6 | A play loop exists: sessions are logged, capped at 250 requests and can be resumed. | `Prototypes/llm-morning/play.py:300-376`; `config.json:6`; `[E15]` |
| W7 | When the model has something new to react to, single scenes read well. | `Prototypes/llm-morning/reports/v23.md:100-112` (the stranger at the door on day 6; the brothers bickering on day 7) |
| W8 | The engine has a structured record of what each person heard (who, what kind of act, at whom), not only text. | `Prototypes/llm-morning/world.py:377` |
| W9 | The C# core traces every decision to its causes and is deterministic. | `Docs/understanding/runs/daniel_ate_it-1.md:1-20`; **NOT VERIFIED** today (suite not run) |

### 2.2 Does not work

| # | Claim | Evidence |
|---|---|---|
| N1 | **With the model off, nobody does anything.** Ten days, model answering nothing: 448 "silent", 36 "sleep", 0 lines spoken, nobody eats. | `[E10]` |
| N2 | The reason: the only decision the code makes on its own is "carry on searching, carry on sitting, or stay silent". | `Prototypes/llm-morning/world.py:956-963` |
| N3 | In the real ten-day run (v23) every act that is not "silent" came from the model: 461 model acts; 227 code acts, all 227 "silent". | `[E9]` |
| N4 | **The week does not read as lived.** In v23, 25 of 32 person-days were held by one option; nobody ate on any day; on day 10 the family's last words are a quarrel about a can opened on day 1. The report's own verdict on days 9 and 10 is "No". | `Prototypes/llm-morning/reports/v23.md:12`, `:80`, `:124`, `:126-129` |
| N5 | **The small model cannot be steered by wording.** Four wordings: Elena `reassure_all` 6 of 6 in each, Mara `accuse_daniel` 6 of 6 in each. Removing people's records of their own acts: 3 of 18 answers changed. Telling starving people they will not last: 0 of 20 went out for food. | `reports/calm_variants.md:34-36`; `reports/self_records.md:17-19`; `reports/probe_stakes.md:14` (all under `Prototypes/llm-morning/`) |
| N6 | **The free tier is not a base for a game.** The v23 week took five sessions over two days: one stop on errors, one request that hung for eight hours, one stop on the daily quota. Stronger free models allow 20 requests a day or answer with errors. | `Prototypes/llm-morning/reports/v23.md:35-41`, `:48-55`; `reports/model_probe_play2.md:8-12` |
| N7 | **An hour of play has not happened.** Three sessions. The longest reached day 1, minute 30 with 31 requests. In both real sessions Daniel confessed within 15 game minutes (minute 15 and minute 12), and in one Mara forgave him six minutes later, which the project's own standard lists as a "Never". Play is limited to days 1 and 2. | `Prototypes/llm-morning/runs/play/daniel_ate_it-seed2-20261014T143852Z/shown.md:262`, `:304`, `:380`; `[E15]`; `Docs/understanding/target-morning.md:35`; `Prototypes/llm-morning/play.py:373` |
| N8 | The player's screen is the model's prompt with numbers on it: 20 to 22 options every three game minutes. | `Prototypes/llm-morning/runs/play/daniel_ate_it-seed2-20261014T143852Z/shown.md:36-56`, `:74-96` |
| N9 | Each turn of play waits on the network: the client waits at least 4.5 s between requests, and a turn asks up to three people. The third session took 8 min 39 s for five choices and 17 requests. | `Prototypes/llm-morning/config.json:4`; `[E15]` |
| N10 | 141 of 349 Python tests are switched off, because they replay stored model answers that no longer match the changed prompts. | `[E7]`; `Prototypes/llm-morning/test_morning.py:47` |
| N11 | The C# simulation is inert: 72 decisions in 90 minutes, the pantry holds 2 portions at the start and 2 at the end, and three people "stay put" from minute 30 to 90. Daniel, who ate the can, spends the morning "wanting to know what happened to the can" and searching rooms for it, which is the first "Never" of the project's own standard. | `Docs/understanding/runs/daniel_ate_it-1.md:5`, `:68`, `:74`; `README.md:173-174`; `Docs/understanding/target-morning.md:18-19` |
| N12 | Unity is used only to run tests. There is one scene (the template's) and no game script. | `[E12]` |
| N13 | The C# suite takes longer than its own script allows: 11,094 s recorded, against a 7,200 s timeout. | `[E12]`; `run-tests.sh:13` |
| N14 | There is no document that says what the player does or why they would care. The "North Star" is eight lines about the code and the model. | `CLAUDE.md:24-31`; `Prototypes/llm-morning/reports/talk_design.md:56-59` (the search for a vision doc: NOT FOUND) |

---

## 3. The real mistakes

### 3.1 In direction

1. **The same problem was attacked twice from opposite ends, and both ends left out the player.**
   - The C# attempt tried to grow believable behaviour from a general theory of wants and feelings. After two weeks
     and 23 slices and experiments it had no speech and people who stand still (N11). Its last five experiments were
     about how to *represent a reason* in test code; the final one reports that the new layer "changed no real
     decision" (`README.md:86`).
   - The Python attempt handed all behaviour to a model and spent three weeks on what the model is told (N3, N5).
   - Neither started from "what does the player do in an hour, and why would they care". The first play session was
     on 14 October, five weeks in `[E15]`, and that one session exposed five faults at once that the probes had not
     (`Prototypes/llm-morning/reports/play_fix1.md:3-9`).
2. **The work went into physics while the family was given nothing to do.** The engine tracks tap water to the half
   litre, rain in millimetres and five stages of fasting (`Prototypes/llm-morning/quiet.py:28-29`). But what a person
   can *do* is: talk about the can, reassure, sit, search, change rooms, eat or share while food lasts, and a few
   water and door acts (`Prototypes/llm-morning/world.py:608-695`). There are no meals, chores, watches or repairs. A
   week reads as lived when things get done in it.
3. **The scenario cannot carry a week.** The shelf holds 2 portions (`Prototypes/llm-morning/data.py:78`). After that
   there is no food for ten days (N4). With nothing to eat there is nothing to share, hide, ration or be fair about,
   so the only subject left is the can. The loop about the can is partly the model's fault and partly the
   scenario's.
4. **The whole day is shaped by a request quota.** A day may ask the model 40 times, a quiet stretch 12, a visit at
   the door 18, and time is skipped between "triggers" so that the 500 free requests last
   (`Prototypes/llm-morning/quiet.py:45-50`, `:92-103`). Much of `quiet.py`'s 1,664 lines rations a resource that a
   code brain does not use.

### 3.2 In method

1. **A heavy experimental method was applied to every small step.** A change meant a design note, an implementation
   note, a frozen plan with a hash, predictions, a run, and a report. You named this yourself on 14 October (the
   "two lanes" note) but by then it had produced 115 reports `[E5]`. The method is right for a claim like "the week
   reads as lived". It is the wrong tool for "should Elena answer Leo first".
2. **The thing under test was a model nobody here controls.** Probes of 18 or 20 answers from a free model, at
   temperature 1.0 (`Prototypes/llm-morning/config.json:3`), were treated as measurements of the design. Most
   predictions failed (v23: P1; calm variants: P1 to P3; self records: P1 to P3; stakes: S1 and S2), and each failure
   led to another wording change, not to the question "should the model be deciding this at all".
3. **Tests were tied to prompt text.** Stored answers are found by a hash of the exact prompt
   (`Prototypes/llm-morning/gemini.py:235-237`). Any change to any line a person is told orphans the stored answers,
   so tests die: 145 were retired in one commit (N10). A test suite that punishes every change slows every change.
4. **The acceptance check for the last code changes could not see behaviour.** "The fake 4-day run exits 0" is the
   run check in each of the last three commits that changed code `[E4]`. The fake model picks an option by a hash
   of the prompt
   (`Prototypes/llm-morning/gemini.py:178-181`). It proves the plumbing holds. It says nothing about whether the
   family behaves like one.
5. **The judge was a document, not an experience.** The standard says "the final judge is a human reading the story"
   (`Docs/understanding/target-morning.md:71`). The ten-day story file is 487 KB `[E8]`. Nobody reads that. In
   practice the judge became tables of counts, which `CLAUDE.md:19-20` says must not be the goal.
6. **Language models judged language models.** In the C# experiments the "blind readers" who checked whether reasons
   read correctly were model subagents (`reports/state/03_experiment_history.md:156`). That is a loop with no person
   in it.
7. **Assistants were told to give no opinions** (`CLAUDE.md:14-15`, for investigations). That is sound for fact-finding.
   But no other kind of session was asked for a judgement on direction either, so the project produced facts for
   seven weeks and decisions only inside small steps.
8. **Housekeeping risk.** 50 unpushed commits and all play sessions untracked `[E13]`.

### 3.3 In code

1. **No code path for behaviour** (N1, N2). This is the central defect and follows from the design, not from a bug.
2. **The model owns state, against the project's own rule.** Each answer carries `suspects` and `angry_at`
   (`Prototypes/llm-morning/world.py:42-54`), and the code turns those into each person's suspicion and grudge levels
   (`world.py:1633-1661`). `CLAUDE.md:26` says "The AI never owns state".
3. **The can is built into the engine.** Options such as `ask_who`, `deny`, `accuse_*` and `confess` are written into
   `options_for` (`Prototypes/llm-morning/world.py:615-628`), and `Person` carries a dozen can-specific fields
   (`world.py:385-398`). A second kind of trouble means editing the 2,297-line engine `[E3]`.
4. **Days 1 and 2 last 90 minutes each; later days run 07:00 to 21:00** (`Prototypes/llm-morning/data.py:79`,
   `quiet.py:27`). Two time models in one week.
5. **One test file of 9,457 lines and 14 frozen copies of the code** `[E5]`. Both exist to serve replay of stored
   model answers.
6. **The typed words of the player change nothing in the code.** Only the chosen act has effects; the words are
   passed to the other people's prompts (`Prototypes/llm-morning/reports/play_design.md:173-188`). With the model
   off, typed words would do nothing at all. The design in section 7 therefore uses chosen lines, not typed ones.
7. **C# side:** the rule "anything about a person enters as a weight, never as a threshold" and "nothing may name a
   member of the cast" (`README.md:136-141`) forbid exactly the authored, specific rules ("Elena never accuses her
   children first") that make a written character feel like someone.

### 3.4 In the North Star (`CLAUDE.md:24-31`)

| Line | Verdict | Why |
|---|---|---|
| "The code owns the truth … The AI owns judgment and words. The AI never owns state." | **Replace** | "Judgment" is what a person does next. That is the game. Giving it to the model is why the game cannot run without one. The last sentence is also not true of the code (3.3, point 2). |
| "The code draws conclusions from what people perceive; the AI decides what they do about it." | **Replace** | Same reason. Keep the first half: people act only on what they perceived. |
| "A line that describes an act makes the small model do that act. State situations; leave the choice open." | **Drop** | It is a note about one small model's habits, not a principle of the game. That it reached the North Star shows where the project's attention had moved. It was also broken on request in the last fix (`Prototypes/llm-morning/reports/play_fix2.md:86-87`). |
| "Mechanisms may be unhuman; the output must read as human." | **Keep, and use it** | This is the right principle and it was not used. It allows a hidden "director" that makes sure something new happens each day. Instead, a choice made by code was once logged as a breach of the North Star (`Prototypes/llm-morning/reports/stage_b_fixes.md:169-171`). |
| "Judge every change by what a real family would do" (`CLAUDE.md:19-20`) | **Keep, but it is half a standard** | A real family in a boarded house is mostly silent and dull. A game selects. The missing half: does the player have something to decide, and does it come back to them later? |
| (missing) | **Add** | Nothing in the North Star mentions the player. |

Proposed replacement, for you to accept or change (not applied; this is a design document):

- The game runs with no model. Code owns the truth, what each person does, and every outcome.
- People act only on what they have perceived or been told.
- Every act has a reason the diary can state in one plain sentence.
- Something new happens every day. Nobody repeats an act the same day without a new cause.
- What Leo does comes back: later, someone treats him differently, and the game can say why.
- Mechanisms may be unhuman; the output must read as human.
- Judge by reading the week and by playing it. Numbers only check that the machinery ran.

---

## 4. The goal, made concrete

**(a) A simulated week that reads as lived.** A seven-day diary of at most two pages a day in which:

1. every day something gets done (water fetched, a meal shared, the door watched, a trip made or refused);
2. every day one thing happens that has not happened before;
3. people refer back: at least three acts in the week happen because of something on an earlier day, and the diary
   says so;
4. each of the four does at least one thing only they would do;
5. none of the "Never" items of `Docs/understanding/target-morning.md:16-36` appears.

**(b) An hour as Leo where the player cares.** About sixty choices over seven days, one a minute. Caring is not
produced by good sentences. It comes from five things the code can provide:

- **They need something from you.** Mara wants to be treated as grown; Daniel wants not to lose face; Elena wants
  someone to carry part of the load. Each can be met or refused by Leo's choices.
- **Kindness costs.** Giving your share makes your own body weaker, and the game shows it.
- **They remember.** What Leo did on Tuesday changes what Mara does on Thursday, and she says why.
- **You know things they do not.** What Leo heard or found is his to tell or keep.
- **Some things cannot be undone.** A night trip can go wrong. Trust lost stays lost for days.

At the end of the hour the game prints, for each of the three, where they stand with Leo and the three things he
did that put them there.

---

## 5. What an LLM is still worth, on the free tier

**Inside the running game: nothing.** Behaviour, choices and outcomes are code. Spoken lines are read from a file.

| Use | Worth it? | Why code cannot do it | Limits |
|---|---|---|---|
| **Drafting line variants, outside the game.** For each speaker, act and tone, ask for 10 to 20 ways to say it; a person keeps the good ones in a data file. | **Yes.** | Code cannot write natural, varied sentences; a person can, slowly. About 100 requests fill a bank of 1,500 lines, once. | The game never calls the model; the file is the product. The coding assistant can also write these lines directly, so even Gemini is optional. |
| **Turning a typed sentence into one of the game's own choices**, as an optional input method. | **Later, optional, off by default.** | Understanding free text is the one thing only a language model does well. | The menu must stay complete without it. A timeout, an error or a doubtful match falls back to the menu. The two stronger free models measured took a median of 8.5 and 9.9 s per answer (`Prototypes/llm-morning/reports/model_probe_play2.md:14-21`); a wait like that may make it not worth having. |
| Choosing what a person does | **No.** | Code can, and must, under the constraint. | N3 to N6. |
| Writing the diary's prose | **No.** | Templates over the event record are enough, and stay true to it. | A model states things that did not happen (`Prototypes/llm-morning/reports/v19_contradictions.md:1-8` is an investigation of false statements about the past in the spoken lines of days 3 to 5). |
| Judging whether a week reads well | **No.** | The judge is you. | 3.2, point 6. |

---

## 6. Architectures compared, and the choice

### 6.1 Four candidates

**A. Keep the model in the loop and add code as a fallback.** The model decides when it answers; rules decide when
it does not.

**B. Drives and practices: code brains on the existing Python world.** Each person has drives that build (hunger,
fear, guilt, grievance, wanting company), a temperament, knowledge and a stance toward each other person. A
"practice" is a named situation (the missing can, a meal, a chore, planning a trip, a knock at the door, a
quarrel, the night) that offers a few moves. The brain scores the moves from the person's own state and picks.
Lines come from a file. A small "director" deals one new trouble a day. This is the family of design used by
shipped social games without language models, such as *Prom Week* and *Versu*.

**C. An authored story deck.** The week is a set of written scenes with conditions ("day 3 or later, water below
20 L, Mara trusts Leo"). The simulation is a handful of numbers. Choices and outcomes are written by hand.

**D. Return to the C# core and add speech to it.**

### 6.2 Comparison

| | A. Model plus fallback | **B. Drives and practices** | C. Story deck | D. C# core |
|---|---|---|---|---|
| Runs with the model off | Yes, but as a different game | **Yes, fully** | Yes, fully | Yes |
| Least AI inside the game | No: the model stays the main brain | **Yes** | Yes | Yes |
| A week that reads as lived | Shown not to (N4) | Likely, if every day has work and one new trouble | Very likely, at a high writing cost | Shown not to (N11) |
| The player cares within an hour | Not shown (N7) | Plausible: reciprocity and cost are built in | Most reliable | No player exists |
| Different weeks from different seeds and people | Some | **Yes** | Only what is written | Yes |
| Reuses what works (W1 to W8) | All | **Truth, perception, nights, street, player loop** | Little | None of the Python |
| Work before a first playable | Small | **About three days** | A week or more of writing | Weeks |
| Can be tested without a model | Half of it | **All of it, with exact expected acts** | All of it | All of it |
| Main risk | Two brains that disagree; N5 and N6 remain | Flat or mechanical people | Not a simulation any more; it stops surprising | Two weeks of evidence against |

### 6.3 The choice: **B**

Reasons, in order of weight:

1. It is the only candidate that meets the hard constraint *and* keeps what the project has built that works.
2. It turns testing into something exact: "in this situation Elena does this" is a test that passes or fails in
   milliseconds, with no quota and no sampling.
3. It keeps the game a simulation, which is what `README.md:3-4` says Fallow is.
4. It borrows the two cheap strengths of C: written lines, and a director that deals events. "Mechanisms may be
   unhuman."

Argued against first, as `CLAUDE.md:21-22` asks: would code-chosen people read as people? The C# attempt was also
code-chosen and came out inert. Three differences make B a different bet: B has speech and social moves, which the
C# core never had (`README.md:14`); B allows written, specific rules per person, which the C# rules forbade
(3.3, point 7); and B is judged by reading and playing from the third day, not by 456 tests of theory.

### 6.4 Language and engine

| Option | For | Against |
|---|---|---|
| **Stay in Python (chosen)** | The working truth layer is here (W1 to W8). Tests run in under four minutes `[E7]`; a week runs in seconds `[E8]`. No tool to install: Python 3.12.10 is present `[E11]`. A text game needs no engine. | Not the language of a later Unity game. Shipping a Python game to strangers is awkward. |
| Pure C# now | Ready for Unity later; types. | About 10,000 lines to port `[E5]` before any new behaviour exists; no .NET SDK is installed `[E11]`; a design that is not yet proven would be ported, which is what happened once already with the C# core. |
| Unity now | The eventual home. | Unity adds nothing a text game needs today. It has been only a slow test runner here (N12, N13). |
| Something else (Godot, a web page) | A nicer screen. | Same objection: presentation before the design is proven. |

**Decision: Python until an hour of play has been judged good. Then port once.** To make the later port cheap:
keep the decision code free of file and screen access, keep people, practices, moves and lines in data files, and
keep the tests as "situation in, act out" cases that can be re-run against any port. The Unity project and the C#
core stay untouched. A simple local web page for the player's screen is a small later step in Python (section 11,
S6) and does not need an engine.

**The checkpoint for porting** (all three): the LLM-off test of section 8 passes; you have played an hour and want
to play again; and there is a concrete need Python cannot meet (pictures, sound, giving it to other people).

---

## 7. The chosen design

Module names below are proposals. "Keep" means the existing file is used as it is.

### 7.1 Layers

| Layer | What it holds | Files |
|---|---|---|
| 1. Truth | Rooms, shelf, water, weather, the street, what happened and who perceived it | Keep: `truth.py`, `weather.py`, `water.py`, `street.py`, `chronicle.py`, `night.py`'s trip tables, `data.py` |
| 2. Perception | Each person's memory, facts, what they were told, what they heard and from whom | Keep: the `Person` fields at `world.py:370-378`, `:441-443`; the guard in `truth.py` |
| 3. Heart (new) | Per person, by code only: body needs; a stance toward each other person; suspicion from evidence; guilt; a mood that shows on the face; one current intention | `heart.py` |
| 4. Practices (new) | The situations and the moves each offers | `practices.py` plus `data/practices.json` |
| 5. Brain (new) | Scores the offered moves for one person and picks one, with the reason | `brain.py` |
| 6. Week (new) | The day's beats; the director's deck of troubles | `week.py`, `data/troubles.json` |
| 7. Words (new) | Lines by speaker, move and tone | `data/lines.json`, `words.py` |
| 8. Telling | The diary of the week; Leo's screen | Adapt `story.py`, `player.py`, `play.py` |

The model client (`gemini.py`), the prompts in `world.py`, the request budgets in `quiet.py`, the night mind
(`mind.py`) and the frozen folders are not used in code mode. They stay in place until the hour of play is judged,
then move to a `legacy/` folder (section 11, S9).

### 7.2 The heart

- **Stance toward each other person:** a short list of remembered acts, each with a kind, a day and a weight
  ("gave me her share, day 2, +2"; "accused me falsely, day 1, −2"). Trust is their sum, held between −3 and +3.
  Ordinary acts fade by half every two days. A few marks do not fade (a betrayal, a rescue). Every later act that
  depends on trust can name the remembered act behind it. This replaces the grudge levels the model raised
  (`world.py:1650-1653`) and extends the event-driven grudges that already exist (`world.py:245-262`).
- **Suspicion:** points from things perceived, never from a guess: left the room when the question was asked;
  denied before being asked; accused someone right after being accused; was heard up in the night. Temperament
  bends it: Mara's suspicion follows whom she resents; Elena's is slow for her own children.
- **Guilt, fear, grievance, wanting company, hunger, thirst, tiredness:** each a number that rises with time or
  events and falls when acted on. A drive that is not acted on gains weight, so sooner or later something happens.
  This is the answer to both standing still (N11) and the silent house (N1).
- **Mood on the face:** set by code from the strongest drive, so that others can react to it. Today it is a word the
  model returns (`world.py:70-78`).
- **Intention:** one thing a person has decided to do and has not yet done ("tell Mom tonight", "go next door after
  dark"), with an end date. It keeps people from changing their mind every three minutes.

### 7.3 Practices and moves

A practice has roles, a few moves, and an end. The first set:

| Practice | Moves (examples) | Ends when |
|---|---|---|
| The missing can | ask who; deny; accuse; deflect; defend someone; call for calm; walk out; confess; search | confession, or everyone has spoken and nothing is new: left unresolved, which sours the next meal |
| A meal (morning and evening) | propose how to split; agree; object; give your share; take more; refuse to eat | everyone has eaten or declined |
| The day's work | take a task (water, watch, boards, count stores, look after someone); assign one; refuse; do it together | tasks taken or left |
| Planning a trip | propose; volunteer; object; back someone; settle who goes | a decision, or bedtime |
| A knock at the door | look; call out; open; give; refuse | the visitor leaves (exists: `quiet.py:750-890`) |
| A quarrel | confront; justify; apologise; walk out; step between | repair, or one leaves; it cannot restart the same day without a new cause |
| Someone is upset | sit with; reassure; leave them be | they settle or leave |
| The night | sleep; lie awake; watch; go out; talk in the dark with whoever shares the room | morning (exists: `night.py:467-552`) |

Each move states, in data: who may do it and when (from what that person perceives); what it does (using the
effects the engine already applies, `world.py:1854` onward); and its **considerations**. A consideration is a
weight on one fact about the actor's own state. Example, for `confess`:

```
confess:
  + 1.2 × guilt (0 to 1)
  + 0.5 × honest
  − 0.6 × proud
  + 0.6 if alone with one person they trust
  − 0.2 × people listening
  − 0.4 if just accused in front of others      (shame hardens)
  offered only to whoever took it; chosen only above 0.6
```

The brain adds up each offered move, takes the best, and where two are within 0.05 lets the seed choose. It keeps
the three largest terms as the reason, which the diary prints in plain words ("because it had been on him since
the night, and they were alone").

Three rules keep it from looping or freezing:

1. **Once is enough.** After a move, the same person cannot make the same move at the same target on the same
   subject again that day unless something new has happened.
2. **Pressure finds a way out.** A drive nobody acts on grows until some move for it wins.
3. **A scene must change something** (a fact learned, a decision, a stance, a body) or end.

People may have **written quirks** in their data ("Elena does not accuse her children first"; "Daniel volunteers
before he thinks"). The engine still names nobody; the data may.

### 7.4 The week

- **A day is a few beats**, the same seven days through: morning (water, the first meal), the day's work, the
  afternoon (the day's trouble), the evening (the second meal, tomorrow's plan), the night. A beat starts the
  practices that apply in each room; a practice plays in the existing short turns until it ends. Between beats time
  passes with no decisions. This replaces the trigger and budget rules (3.1, point 4) in code mode.
- **The director** holds a seeded deck of troubles, each with conditions, and deals one a day, never the same twice:
  rain and the bin; a knock (exists); the tap running low; someone weak; a noise in the street at night; something
  found next door; Mara wanting to go out; a cut hand. It deals harder ones from day 5.
- **The scenario change:** start with food for about four days on short portions, so that meals happen, the night
  trips matter by day 4, and the can is the first trouble and not the only subject. Daniel's confession becomes a
  move scored like any other, so *how Leo handles him* decides whether he confesses, hardens, or goes out at night to
  make it right.

### 7.5 Words, the diary, and Leo

- **Lines:** `data/lines.json`, keyed by speaker, move and tone, with three to eight variants each and slots for
  names and things. The code picks by seed and never the same variant twice running. Every move has a plain default
  line, so nothing is ever unsaid for want of text.
- **The diary:** per day, at most 60 lines: the beat, who did and said what, and the reason. This is what you read.
- **Leo's screen:** the situation in a few lines, then at most seven choices, each shown as the line Leo would say
  or the thing he would do, with "something else…" opening the rest. No typing is needed. The other three answer at
  once.

---

## 8. The LLM-off test (pass/fail)

One test, `test_llm_off.py`. It plays seven days, seeds 1, 2 and 3, twice each: with Leo played by code, and with a
scripted player as Leo. **It passes only if every clause holds for every run.** A clause is in force from the date
shown; earlier than that it is reported but does not fail the test. Until 14 Nov the run is ten days through the
existing day loop (section 10); from 14 Nov it is the seven-day week.

| # | Clause | In force from |
|---|---|---|
| L1 | **No model.** `GEMINI_API_KEY` is unset; importing `google.genai` is blocked; opening a network socket raises; no model client is constructed; a counter of calls to any model interface reads 0. | 12 Nov |
| L2 | **Same seed, same week.** Two runs of one seed give byte-identical transcripts. At least two of the three seeds differ from each other. | 12 Nov |
| L3 | **Code decided everything.** Every act is marked `code`, `routine` or `player`. None is `model` or `fallback`. | 12 Nov |
| L4 | **Valid.** Every chosen move was offered. Every spoken move has words, and the words come from the line file. | 12 Nov |
| L5 | **Alive.** On every day, each person at home and awake makes at least 3 acts that are not silent, sleep, rest or sitting idle; the house speaks at least 12 lines and at most 80. | 14 Nov |
| L6 | **Not stuck.** No person makes the same move at the same target more than twice in a day. No person says the same sentence twice in a day. At most 4 of the 28 person-days have one move taking half or more of that person's acts (v23's own measure, where it was 25 of 32: `Prototypes/llm-morning/reports/v23.md:12`). | 14 Nov |
| L7 | **Bodies make sense.** On any day that begins with food on the shelf, someone eats. Nobody reaches "thin and weak" with food on the shelf. Nobody is "badly thirsty" with more than 5 L stored. | 14 Nov |
| L8 | **New each day.** Each day's record holds one trouble not seen earlier that week, perceived by someone, and at least one later act names it as its reason. | 14 Nov |
| L9 | **Leo matters.** The same seed played by two scripts, a kind Leo and a cold Leo, gives by day 3 at least one different act toward Leo from each of two other people, and each difference names a recorded act of Leo's as its reason. | 16 Nov |
| L10 | **Fast.** The whole test finishes in under 60 s. | 12 Nov |

What this test does not tell you: whether the week is good. It only shows that code decided everything, that the
house is alive, and that nothing loops. Whether it reads as lived is judged by you reading `week.md` on 15 Nov and
playing on 16 Nov (`CLAUDE.md:20`: "A metric is a clue, never the goal").

---

## 9. Plan, 12 to 16 November

Each day ends with the suite green, the LLM-off test passing for the clauses then in force, and something for you
to read or play for fifteen to thirty minutes. One journal entry of at most a page per day in
`Prototypes/llm-morning/reports/journal.md`. No other reports. If a day runs short, cut from the bottom of its
"Build" list, never the test gate.

| Day | Build | Test gate | You |
|---|---|---|---|
| **12 Nov. The code brain.** | `brain.py` with the first rules (section 10). The three places that ask the model (`world.py:1608`, `night.py:427`, `mind.py:435`) take a brain instead when one is given. `--code` on `morning.py` and `play.py`. A small starter line table. | Section 10's cases B1 to B14. L1 to L4, L10. The old suite and the fake-run hashes unchanged. | Play day 1 as Leo with `--code` for 15 minutes. Write down three things that felt wrong. |
| **13 Nov. The heart, and food.** | `heart.py`: stance from remembered acts, suspicion from evidence, guilt, mood on the face, one intention; in code mode the model-shaped fields no longer set state. Food for about four days. The meal practice. | Scripted cases: a remembered kindness changes a later choice and is named as the reason; a false accusation is remembered and fades by half in two days; Daniel confesses alone with Elena at high guilt and not in front of everyone; a meal is eaten on each of days 1 to 3. | Play days 1 and 2. Does anyone treat you differently on day 2 because of day 1? |
| **14 Nov. The week.** | `week.py`: seven full days in beats, with no request budgets. The work practice. The director with at least five troubles. Nights reuse `night.py`. | L1 to L8, L10. | Read the raw record of seed 2, one line per act. Is there a day where nothing happened? |
| **15 Nov. Words and the diary.** | `data/lines.json` with at least 400 lines across the four speakers. The diary of at most 60 lines a day, with reasons. | No move without a line; no sentence twice in a day; diary length; L1 to L8 still pass. | Read two whole weeks (two seeds), about 20 minutes. Mark every line that sounds wrong. **This is the first real judgement of goal (a).** |
| **16 Nov. Leo's hour.** | The player in the week loop: at most seven choices a screen; remembered acts shown when they come back; save and resume; the end-of-week page. | L9; a scripted hour (60 choices) completes; all earlier clauses. | **Play for an hour.** Then say, without notes, what each of the three wanted from you. That answer, in your words, goes in the journal. Fable revises section 11's specs from it. |

---

## 10. The first build step (12 Nov): frozen test cases and predictions

**Frozen.** The cases and the predictions below are fixed before any code is written. The implementer does not edit
them. If one turns out to be wrong, it is recorded as wrong, with the reason, and left in place.

### 10.1 Scope of the step

- New file `Prototypes/llm-morning/brain.py`: `CodeBrain.choose(person, options, context)` returns the same fields
  the engine takes from the model today (`option`, `say`, `feeling`, `reason`, `suspects`, `angry_at`), so nothing
  downstream changes. It may read only the `Person` it decides for and a `context` of what that person can see:
  who is in the room, what they are visibly doing, their shown mood, and the structured record of what was said
  this turn (`world.py:377`).
- `Morning.ask_model` (`world.py:1608-1631`) and `Night.ask` (`night.py:427-454`) ask the brain when one is set and
  never touch the oracle. The night mind (`mind.py:435-447`) is skipped when a brain is set.
- `morning.run(..., brain=...)`, `python morning.py --seed N --code --days 10`, `python play.py --code`.
- The existing day loop, option lists and budgets are **not** changed in this step.
- New tests in a new file, `Prototypes/llm-morning/test_brain.py`. `test_morning.py` is not edited.

### 10.2 The first rules (the first that applies wins; ties by seed)

Traits are those of `Prototypes/llm-morning/data.py:17-56`. "Once" means once per person, target and day.

1. **Handed a portion:** eat it if at least "hungry"; else put it back.
2. **Asked aside:** go, unless holding a grudge of 2 or more against the asker.
3. **Night.** Bedtime: go next door if they offered to today and are not yet "thin and weak"; lie awake if anxious
   ≥ 0.75; else sleep. Seeing someone leave: try to stop them if empathetic ≥ 0.7; else stay in bed. Stopped at the
   door: go anyway if proud ≥ 0.6.
4. **Owes an answer** (`world.py:697-707`). To an accusation, if innocent: deny, then nothing more is owed. If they
   took it: confess when guilt is 3; else deny, at most twice a day, then go to their own room. To a confrontation,
   a reassurance or being spoken to: one line back to that person.
5. **At the door:** look first, once; then refuse if cautious ≥ 0.6, else call out.
6. **Food on the shelf, in the kitchen:** with others present, share it out if empathetic ≥ 0.7 and someone here is
   "very hungry" or worse. Alone: eat if "starving", or if "very hungry" and impulsive ≥ 0.6.
7. **Rain, and the bin is not out:** set it out if cautious ≥ 0.6 or dominant ≥ 0.8, once.
8. **The can, not yet known.** Whoever counted the shelf asks who took it, once. Someone with suspicion of 2 or more
   who is impulsive ≥ 0.6 or dominant ≥ 0.8 accuses that person, once. Someone proud ≥ 0.5 who heard the question
   and has not answered denies, once.
9. **Whoever took it,** with guilt of 2 or more, in a room with others and owing no answer: goes to their own room,
   once per conversation.
10. **Someone here looks upset:** sit with them, or reassure them if sitting is not offered, if empathetic ≥ 0.7 and
    no grudge of 2 or more against them, once.
11. **The trip, once it is raised:** volunteer if dominant ≥ 0.8 and proud ≥ 0.8; object to a volunteer if cautious
    ≥ 0.7; decline if anxious ≥ 0.75; each once.
12. **Water:** say it must be rationed if cautious ≥ 0.7, once in the week.
13. **Otherwise** the existing routine (`world.py:956-963`).

`suspects` is the person the code's evidence points to (left the room within two turns of the question or an
accusation; accused someone straight after being accused; a night note such as `data.py:218-222` gives), else
nobody. `angry_at` is whoever accused them falsely this day, else nobody. This feeds the existing levels for one
day only; 13 Nov replaces it.

### 10.3 Frozen test cases

Unit cases build a `Person` by hand and call `choose`. Run cases play through `morning.run` in code mode.

| # | Kind | Situation | Expected |
|---|---|---|---|
| B1 | run | Seeds 1 to 3, 10 days, `--code`, no oracle, network blocked | Exit 0; 0 model calls; under 60 s for all three |
| B2 | run | Seed 2 twice | Transcripts byte-identical |
| B3 | run | Seeds 1 to 3 | Every act is `code` or `routine`; none `model`, none `fallback` |
| B4 | run | Seeds 1 to 3 | Every chosen option was offered; every spoken option has words; no words contain `[fake` |
| B5 | unit | The brain's `context` is built inside `truth.prompting()` | No `TruthLeak` is raised |
| B6 | run | Seed 2, `daniel_ate_it` and `mara_ate_it`, day 1, minute 00 | Leo's first act is the same in both (he cannot know who took it) |
| B7 | run | `daniel_ate_it`, seeds 1 to 3, day 1 | Elena's first act at minute 00 is `ask_who` |
| B8 | run | Scripted Leo accuses Elena at minute 09 (the case of `Prototypes/llm-morning/reports/play_fix2.md:3-5`) | Elena's next act is `deny`; it is not `reassure_all` and is not aimed at Daniel |
| B9 | run | `daniel_ate_it`, seeds 1 to 3, all days | Daniel never chooses `ask_who`, `search` or `keep_searching` (`Docs/understanding/target-morning.md:18-19`) |
| B10 | unit | Daniel, asked, guilt 1 / Daniel, accused, guilt 3 | `deny` / `confess` |
| B11 | unit | Elena in the kitchen, food on the shelf, Mara "very hungry" / Mara alone, "starving" / Leo alone, "very hungry" | `share` / `eat` / not `eat` |
| B12 | run | Seeds 1 to 3, all days | No person chooses the same option more than twice in one day, `silent` and the night's `sleep` aside |
| B13 | unit | Bedtime: Daniel volunteered today, fasting stage 1 / Mara / Leo | `go_next_door` / `lie_awake` / `sleep` |
| B14 | run | `python -m unittest test_morning`; `morning.run(1, fake=True, days=4)` with no brain | 349 tests, OK (skipped=141) `[E7]`; story sha256 `3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9`, transcript `dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8` (the baseline of `Prototypes/llm-morning/reports/play_fix2.md:20-21`, reproduced today `[E17]`) |

### 10.4 Frozen predictions

Written before the step, to be scored after it. F5 predicts a shortfall on purpose.

| # | Prediction | Compare with |
|---|---|---|
| F1 | B1 to B14 all pass on the first full run after the code is complete. | |
| F2 | Each ten-day run has at least 150 acts that are neither silent nor sleep, and at least 60 spoken lines. | Model off today: 0 and 0 `[E10]`. v23 with the model: 420 model acts other than "silent" `[E9]`. |
| F3 | Day 1, `daniel_ate_it`, seeds 1 to 3: Daniel denies at least once in all three; he confesses before minute 30 in none; he confesses on day 1 in at most one. | Play with the model: confession at minute 15 and at minute 12 (N7). |
| F4 | Both portions are eaten or shared by the end of day 2 in at least two of three seeds. | Model off today: nobody eats in ten days `[E10]`. |
| F5 | **Days 3 to 10 will be thin:** fewer than 10 spoken lines on at least five of the eight days, because once the can is settled these first rules give people little to do. This is the gap that 13 and 14 Nov fill. If this prediction fails because the days are busy, look for a loop before being pleased. | |
| F6 | At most 6 pairs of word-for-word equal lines by one person in one day, per run. | v23: 6; v22: 23 (`Prototypes/llm-morning/reports/v23.md:14`). |
| F7 | A scripted player's whole day 1 (30 turns) in code mode takes under 5 s and 0 requests. | With the model: 17 requests and 8 min 39 s for five choices `[E15]`. |
| F8 | Your own verdict after 15 minutes of play, recorded in your words. My guess: "plainer sentences, saner people, and it answers at once." Not pass/fail. | |

---

## 11. After 17 November: small specs for Opus or Sonnet

Each is one session or less. Each ends with the LLM-off test and the suite passing. Order matters only where noted.

| # | Spec | Tests that must pass | Done when |
|---|---|---|---|
| S1 | **Repair.** Moves for apology and making amends inside the quarrel practice; an apology accepted only if trust is above −2 or an amend was made. | Unit: accepted and refused cases; run: a quarrel on day 2 is repaired or still named on day 4 | The diary shows one repair and one refusal across seeds 1 to 3 |
| S2 | **Night talk.** Two people who share a room may talk in the dark: a private place to confess, ask, or promise. | Unit: offered only to room-mates awake; run: Daniel's confession to Leo is possible at night | A scripted Leo can draw a confession at night that he cannot draw in the kitchen |
| S3 | **Clues.** The empty can, hidden somewhere by seed; who was heard up; a search can find it. Leo can show it or keep it. | Unit: found only where it is; shown evidence raises suspicion in those who see it | Two scripts (shows it; keeps it) give different day 3s |
| S4 | **The other scenarios** in code mode: `mara_ate_it`, `miscount`. | LLM-off test on both; B6 extended | Three seeds of each read as different weeks |
| S5 | **Lines, second pass.** Bring each speaker to 150 lines; a check that flags a line used more than three times in a week. | No default line used where a written one exists; the usage check | You read a week and mark fewer than five lines |
| S6 | **A local web page for Leo's screen**, served by Python's standard library. No new dependency. | The scripted hour passes through the page's handler | You play in a browser |
| S7 | **Care for the weak.** A person "thin and weak" or hurt can be looked after; doing it builds trust and costs the carer rest. | Unit and run cases | A week with one person down still passes L5 |
| S8 | **The end-of-week page**, in full: for each person, their stance and the three acts of Leo's behind it; what the house has left. | Golden-file test on two scripted weeks | You recognise your own week in it |
| S9 | **Clear the ground.** Move `gemini.py`, the prompts, `mind.py`, the budgets, `v1` to `v14`, the retired tests and the probe scripts to `legacy/`. Split the tests by subject. Only after the hour of play is judged good. | The LLM-off test and the code-mode tests pass with `legacy/` deleted from the path | `import` of anything in `legacy/` from the game fails a test |
| S10 | **A week table** (`python week_table.py --seed N`): per day, food, water, acts by kind, the day's trouble. A tool for you, not a report. | Runs in under 5 s | You use it instead of asking for an investigation |
| S11 | **Typed input, optional.** A model maps a typed sentence to one offered choice; off by default; falls back to the menu on any doubt, error or 3 s timeout. | With the feature on and the network blocked, the game plays exactly as with it off | Only if, after S1 to S8, you still want to type |
| S12 | **The street as week two.** Neighbours from `street.py` as people with needs who remember what the house did at the door. | LLM-off test over 14 days | After the port decision, not before |
| S13 | **The port decision.** Check the three conditions of 6.4. If met, write the port plan; the "situation in, act out" tests are the port's acceptance tests. | | A yes or no in the journal, with the reason |

---

## 12. Method from here

1. **One lane.** Build, run the tests, then *you* read one day or play ten minutes. That is the check.
2. **The frozen method is kept for two claims only:** "the week reads as lived" and "an hour of play holds". Each is
   settled by you reading or playing, with what you expect written down first.
3. **One page a day** in a journal. No design note, implementation note or probe report per change.
4. **Tests state a situation and the act expected.** No test depends on stored model answers.
5. **When something feels wrong in play, the fix is a rule or a line, the same day.** If the same kind of thing
   feels wrong three times, that is a design question, and it gets one page.
6. **Ask the assistant for a judgement when you want direction.** "No opinions" stays for investigations only.
7. **Push the branch** today, before any new work `[E13]`.

Proposed changes to `CLAUDE.md` (not made): replace lines 24 to 31 with the seven lines at the end of section 3.4;
replace the Gemini rule at lines 5 to 6 with "The game makes no model call. Model calls are allowed only in
`legacy/` and in line-drafting scripts, and only when the prompt's MODE is run."

---

## 13. Risks, and what would change this advice

| Risk | Sign | Response |
|---|---|---|
| Code-chosen people feel mechanical | On 15 Nov you can predict what each will say next | More written quirks per person and more line variants first. If two more days do not fix it, move the *hour of play* to architecture C (written scenes over the same truth layer, heart and lines). Nothing built by then is lost. |
| The week is busy but empty | L5 to L8 pass and you are bored | The director's troubles are too mild or do not force a choice between people. Rewrite the deck before touching the brain. |
| Five days is too much | A day's gate is not green by evening | Cut from the bottom of that day's list; carry the rest into the Opus specs. The order of days does not change. |
| The old engine resists | 14 Nov needs changes deep in `world.py` or `quiet.py` | Write `week.py` as a new small loop that calls the existing turn code for scenes, and leave the old loop alone. |
| Writing 400 lines is slow | 15 Nov ends with fewer than 200 | Ship defaults plus written lines for the three practices you see most; the rest is S5. |
| I am wrong about the model | A free model appears that is reliable and can be steered | It still could not be the brain under your constraint. It would only make S11 more attractive. |

What I have not done, and you should weigh: I have not played the game, I did not run the Unity suite, and I did
not call any model. My reading of how the game feels rests on your three session logs and the project's own
reports.

---

## 14. NOT VERIFIED

1. The Unity suite's current result. Not run (about three hours; N13). The figures are from `test-results.xml`,
   dated 2026-09-24.
2. That the C# narrator still builds and gives the stored morning. `./narrate.sh` was not run, because it writes
   into the repository.
3. Whether the 141 skipped Python tests would pass if they could run. They need stored model answers that no
   longer match.
4. How long a real hour of play takes, or how it feels. No session reached an hour (N7). The first session's
   three hours of clock time include an unknown amount of time away from the keyboard.
5. The speed of `gemini-3.5-flash-lite` per answer. The repository measures only stronger models
   (`Prototypes/llm-morning/reports/model_probe_play2.md:14-19`).
6. Today's free-tier limits. Nothing was sent; the figures are from reports of 13 to 15 October.
7. The claims about *Prom Week* and *Versu* in 6.1 are from my own knowledge, not from anything in the repository.
8. Reports read in part only. Of the 115 reports I read in full or in their result sections: `v23`, `play_design`
   (to §3), `play_fix1`, `play_fix2`, `model_probe_play2`, `stuck_facts`, `self_records`, `calm_variants`,
   `probe_stakes`, the two under `reports/state/`, and the three under the root `reports/state/`. The others I know
   through commit messages and cross-references.

---

## Appendix: every command run, and its key output

All from Git Bash. `S` is the session's scratch folder outside the repository
(`C:\Users\Akrem\AppData\Local\Temp\claude\1bce08cb0c2bed6c\138ef89d-5db1-475b-b04c-522cebbe38f9\scratchpad`). Every
run wrote its files there. `git status --short` listed the same 31 entries before and after the runs `[E16]`.
Python is `Prototypes/llm-morning/.venv/Scripts/python.exe`, always with `GEMINI_API_KEY` unset and
`PYTHONDONTWRITEBYTECODE=1`.

**E1. Shape of the repository**
```
$ git ls-files | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn | head
   1675 Prototypes/llm-morning
    290 Assets/_Project
     92 Docs/slices
     91 Docs/experiments
$ git log --oneline | wc -l
184
```

**E2. Listings.** `ls` of `Prototypes/llm-morning`, its `reports/`, `runs/`, `Docs/*`, `investigations/`,
`reports/state/`, `Tools/`. Key output: 18 current `.py` modules, `v1` to `v14`, 115 report files, the run folders
named in this document.

**E3. Code size**
```
$ wc -l Prototypes/llm-morning/*.py | sort -rn | head -4
   9457 test_morning.py
   2297 world.py
   1664 quiet.py
   1276 night.py
$ cat Assets/_Project/Scripts/Core/*/*.cs | wc -l
8554
$ cat Assets/_Project/Tests/EditMode/*.cs | wc -l
28586
```

**E4. History**
```
$ git log --format='%h %ad %s' --date=short | cut -c1-230        (184 lines; first and last shown)
e079555 2026-10-15 LLM morning: playing Leo, fix 2 amended ... 349 tests OK (skipped=141); the fake 4-day run exits 0, same pair 3a3d2ff2..., dfd50303...; no live call
...
91d4341 2026-09-10 chore: bootstrap Unity project for Fallow slice S0
$ git log --format='%ad' --date=short | awk '$1<="2026-09-24"{a++} $1>"2026-09-24"{b++} END{print a, b}'
62 122
$ git log -1 --format='%h %ad' --date=iso
e079555 2026-10-15 19:08:10 +0100
```
"The fake 4-day run exits 0" is in the messages of `e079555`, `bfb1c23` and `b3f7549`, the last three commits that
changed code. The two between them (`f8880d3`, `dc2db9a`) are model probes that changed no code.

**E5. Reports against code**
```
$ ls Prototypes/llm-morning/reports/*.md | wc -l            -> 115
$ cat Prototypes/llm-morning/reports/*.md | wc -l           -> 69406
$ cat Prototypes/llm-morning/REPORT*.md | wc -l             -> 7863
$ find Docs -name '*.md' | wc -l                            -> 160
$ cat Prototypes/llm-morning/{world,quiet,night,street,story,mind,morning,play,gemini,chronicle,data,memory,topics,player,truth,talk,weather,water}.py | wc -l
10172
$ ls -d Prototypes/llm-morning/v*/ | wc -l                  -> 14
```

**E6. Files read** (no output to quote): `README.md`; `CLAUDE.md` and `git diff CLAUDE.md` (three lines added, not
committed); `Docs/understanding/target-morning.md`; `reports/state/01_repo_map.md`, `02_csharp_core.md` (§4 to §8),
`03_experiment_history.md` (§1 to §4); under `Prototypes/llm-morning/`: `reports/state/05_results_quality.md`
(to §6), the reports named in section 14 point 8, `gemini.py:146-304`, `world.py:20-138`, `:359-457`, `:597-720`,
`:950-969`, `:1443-1712`, `quiet.py:1-112`, `:1236-1315`, `night.py:427-526`, `morning.py:1-160`, `:416-453`,
`data.py:1-90`, `config.json`, and the three play sessions' `shown.md` and `session.log`;
`Docs/understanding/runs/daniel_ate_it-1.md:1-60`, `:95-135`; `investigations/n9-root-cause.md:1-25`.

**E7. The Python suite**
```
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 python -m unittest test_morning      (in Prototypes/llm-morning)
Ran 349 tests in 225.470s
OK (skipped=141)
real    3m47.864s
```

**E8. A ten-day week with the fake model**
```
$ python -c "import sys, morning; meta, code = morning.run(2, fake=True, runs_dir=sys.argv[1], cache_dir=sys.argv[2], days=10); print('exit code', code)" S/fake10/runs S/fake10/cache
  weather day 1: wet, 2.5 mm (09:00 to 13:09); 7.7 to 14.2 °C outdoors, 15.0 °C indoors
  ...
  street day 6 09:27: a visit to the front door from no. 6 (ask water)
  ...
  run_seconds: 19.4
exit code 0
real    0m21.053s
$ ls -la S/fake10/runs
 486578 daniel_ate_it-seed2.md
1714978 daniel_ate_it-seed2.transcript.json
meta: 'api_requests': 568, 'answers_live': 568, 'days': 10
```

**E9. Who decided each act** (`S/modes.py`: walks a transcript and counts every record that has a `mode` and an
`option`)
```
$ python S/modes.py S/fake10/runs/daniel_ate_it-seed2.transcript.json Prototypes/llm-morning/runs/v23/daniel_ate_it-seed2.transcript.json
fake10:  acts with a mode: 811 {'model': 425, 'fallback': 109, 'routine': 277}
    routine [('silent', 275), ('sit_leo', 1), ('sit_mara', 1)]
v23:     acts with a mode: 688 {'model': 461, 'routine': 227}
    model [('accuse_daniel', 88), ('reassure_all', 62), ('confront_daniel', 54), ('silent', 41), ('lie_awake', 29), ('still_going', 26), ('confront_leo', 22), ('confront_mara', 20)]
    routine [('silent', 227)]
```

**E10. A ten-day week with the model answering nothing** (`S/llm_off.py`: a client whose every answer is the empty
string, passed to `morning.run(2, client=..., days=10)`; then the same count as E9)
```
$ python S/llm_off.py <prototype folder> S/off10/runs S/off10/cache
exit code 0 | asks that got an empty reply: 163
acts: 484 {'fallback': 127, 'routine': 357}
options chosen: [('silent', 448), ('sleep', 36)]
lines spoken: 0
```

**E11. Tools on this computer**
```
$ dotnet --version      -> bash: dotnet: command not found
$ python --version      -> Python 3.12.10
$ ls "/c/Program Files/Unity/Hub/Editor/"   -> 6000.3.24f1
$ godot --version       -> bash: godot: command not found
$ node --version        -> v24.17.0
```

**E12. Unity and the C# suite**
```
$ find Assets -name '*.unity'                           -> Assets/Scenes/SampleScene.unity
$ grep -rlE 'MonoBehaviour' Assets --include=*.cs       -> (no output)
$ find Assets -name '*.prefab' | wc -l                  -> 0
$ grep -oE '<test-run [^>]*>' test-results.xml
<test-run id="2" testcasecount="456" result="Failed(Child)" total="456" passed="454" failed="2" ... start-time="2026-09-24 01:56:49Z" end-time="2026-09-24 05:01:43Z" duration="11094.8859012">
$ grep -n 'timeout' run-tests.sh
13:  --format json --no-banner --non-interactive --timeout 7200 >"$LOG" 2>&1
```

**E13. Branches**
```
$ git branch -vv
  archive/never-checker 8c7c8e9 Archive: target-morning audit (untracked until now)
  main                  01f0c9b [origin/main: behind 2] ...
* quiet-day-stage-a     e079555 [origin/quiet-day-stage-a: ahead 50] ...
```

**E14. Line numbers.** `grep -n` for each `path:line` cited: `CLAUDE.md` ("North Star" at 24 to 31);
`data.py` (`PORTIONS = 2` at 78, `MINUTES = 90` at 79); `play.py` (`--days` choices `(1, 2)` at 373); `truth.py`
(`TruthLeak` at 21); `mind.py:435-447`; `test_morning.py:47` and `:8869`; `reports/v23.md:12`, `:80`, `:128`;
`reports/calm_variants.md:34-36`; `reports/self_records.md:17-19`; `reports/probe_stakes.md:14-15`;
`reports/state/03_experiment_history.md:156`; `reports/play_design.md:23`; `reports/stage_b_fixes.md:170`;
`README.md:14`, `:86`, `:136-140`, `:173-174`; `Docs/understanding/runs/daniel_ate_it-1.md:5`, `:68`, `:74`;
`CLAUDE.md:5-6`, `:14-15`, `:19-22` (by `cat -n`); `data.py:218-220` (the `daniel_ate_it_leo_heard` scenario);
`reports/play_fix2.md:20-21` (the two baseline hashes).

**E15. The play sessions**
```
$ ls -la Prototypes/llm-morning/runs/play/*
daniel_ate_it-seed2-20261014T143829Z   play.jsonl 655 B, shown.md 105 B          (started and stopped)
daniel_ate_it-seed2-20261014T143852Z   play.jsonl 33029 B, shown.md 17609 B
daniel_ate_it-seed2-20261014T225035Z   play.jsonl 20761 B, shown.md 12216 B
$ cat .../20261014T143852Z/session.log
2026-10-14T14:38:54Z part 1: seed 2, daniel_ate_it, days 2, model gemini-3.5-flash-lite, at most 250 requests ...
2026-10-14T17:46:24Z part 1 ended: stopped: you chose to stop.; 31 live, 0 cached, 31 API requests
$ cat .../20261014T225035Z/session.log
2026-10-14T22:50:37Z part 1: seed 2, daniel_ate_it, days 1, ...
2026-10-14T22:59:16Z part 1 ended: stopped: you chose to stop.; 17 live, 0 cached, 17 API requests
```
The second session's last screen is "Day 1 · minute 30" (`shown.md:380`). The third session's screens, with the
option lists filtered out by `grep -vE`, show five choices and "Daniel admitted taking it at minute 12".

**E16. Nothing in the repository changed**
```
$ git status --short | wc -l        (before the runs, and after)
31
31
```
The two listings hold the same 31 paths (`M CLAUDE.md`, and 30 untracked folders and files under
`Prototypes/llm-morning/cache`, `Prototypes/llm-morning/runs` and `investigations/`), all present before this
session. After this file was written the count is 32.

**E17. The fake 4-day baseline, reproduced**
```
$ python -c "import sys, morning; meta, code = morning.run(1, fake=True, runs_dir=sys.argv[1], cache_dir=sys.argv[2], days=4, quiet=True); print('exit code', code, 'story_sha256', meta['story_sha256'])" S/fake4/runs S/fake4/cache
exit code 0 story_sha256 3a3d2ff2924f513cdfbf2863659d6a924dafae1dca372f339f15514a504008a9
$ sha256sum S/fake4/runs/daniel_ate_it-seed1.transcript.json
dfd50303bcd5156f4198adff78686693e19288ba275af7975c47c3646d63eaa8
```
