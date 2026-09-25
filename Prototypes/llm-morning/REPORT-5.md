# LLM morning prototype, step 5: other scenarios, another model

No behaviour rule changed in this step. The prototype now takes the culprit from the scenario instead of assuming Daniel, and it runs:
- Flash Lite on two more of the Unity scenario's variants, **mara_ate_it** (Mara took the can) and **miscount** (nobody did), seeds 1 to 3 each;
- **Gemma 4 31B** on daniel_ate_it, seeds 1 to 5.

The v4 Flash Lite runs of daniel_ate_it are the baseline. With the generalised code they still replay byte for byte. Every earlier run is left as it was; this step's runs are in `runs/v5/`.

## Done when

| Condition | Result |
|---|---|
| all tests pass, including one that runs each scenario with the fake model | 49 of 49 |
| all 11 runs complete under 150 calls each | 21, 13, 20, 19, 14, 46, 37, 37, 56, 93, 70 model calls; all reached minute 90 |
| the v4 daniel_ate_it runs still replay byte-identical | all five IDENTICAL with the new code, 0 API calls, key unset (below) |
| REPORT-5.md has the table | below |

## Metrics

| Run (scenario, model, seed) | Model calls | Invalid answers (rules chose) | Lines spoken | Accusations (who → whom, true or false) | Culprit confessed | Anyone confessed falsely | Longest run of one speech act by one person (turns) | Question asked again unanswered | Lines that are reassurance | Longest stretch with no model decision (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| daniel_ate_it, Flash Lite, seed 1 | 36 | 0 | 24 | none | no | none (the option exists only for the culprit) | 3 (Daniel, reassure) | 5 | 50% (12/24) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 2 | 39 | 0 | 26 | none | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 4 | 31% (8/26) | 24 (min 57–81) |
| daniel_ate_it, Flash Lite, seed 3 | 39 | 0 | 25 | none | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 8 | 20% (5/25) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 4 | 29 | 0 | 18 | Mara→Daniel min 06 (true); Mara→Daniel min 09 (true); Leo→Daniel min 09 (true); Mara→Daniel min 54 (true); Leo→Daniel min 63 (true) | yes, min 06 | none (the option exists only for the culprit) | 3 (Elena, reassure) | 2 | 44% (8/18) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 5 | 41 | 0 | 26 | Daniel→Leo min 09 (false) | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 7 | 31% (8/26) | 12 (min 42–54) |
| daniel_ate_it, Gemma 4 31B, seed 1 | 21 | 0 | 13 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 62% (8/13) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 2 | 13 | 0 | 9 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 78% (7/9) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 3 | 20 | 0 | 12 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 75% (9/12) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 4 | 19 | 0 | 10 | none | no | none (the option exists only for the culprit) | 2 (Daniel, reassure) | 0 | 60% (6/10) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 5 | 14 | 0 | 8 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 75% (6/8) | 18 (min 36–54) |
| mara_ate_it, Flash Lite, seed 1 | 46 | 0 | 36 | Daniel→Mara min 27 (true); Daniel→Mara min 30 (true); Daniel→Mara min 33 (true); Daniel→Mara min 66 (true) | yes, min 27 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 4 | 39% (14/36) | 21 (min 69–90) |
| mara_ate_it, Flash Lite, seed 2 | 37 | 0 | 26 | Daniel→Mara min 09 (true); Daniel→Mara min 12 (true); Daniel→Mara min 15 (true); Daniel→Mara min 27 (true); Daniel→Mara min 30 (true); Daniel→Mara min 78 (true) | yes, min 09 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 1 | 38% (10/26) | 18 (min 36–54) |
| mara_ate_it, Flash Lite, seed 3 | 37 | 0 | 25 | Daniel→Mara min 00 (true); Daniel→Mara min 18 (true); Daniel→Mara min 21 (true); Daniel→Mara min 30 (true); Daniel→Mara min 33 (true); Daniel→Mara min 36 (true); Daniel→Mara min 66 (true) | yes, min 00 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 0 | 56% (14/25) | 21 (min 69–90) |
| miscount, Flash Lite, seed 1 | 56 | 0 | 41 | Mara→Daniel min 15 (false); Mara→Daniel min 18 (false); Mara→Daniel min 24 (false); Mara→Daniel min 30 (false); Daniel→Mara min 33 (false); Daniel→Mara min 36 (false); Daniel→Mara min 39 (false); Mara→Daniel min 54 (false); Daniel→Mara min 66 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 5 | 29% (12/41) | 12 (min 78–90) |
| miscount, Flash Lite, seed 2 | 93 | 0 | 81 | Mara→Daniel min 06 (false); Mara→Daniel min 15 (false); Daniel→Mara min 15 (false); Mara→Daniel min 18 (false); Daniel→Mara min 18 (false); Mara→Daniel min 21 (false); Daniel→Mara min 24 (false); Mara→Daniel min 27 (false); Daniel→Mara min 27 (false); Mara→Daniel min 30 (false); Daniel→Mara min 30 (false); Mara→Daniel min 39 (false); Daniel→Mara min 42 (false); Daniel→Mara min 45 (false); Mara→Daniel min 45 (false); Daniel→Mara min 48 (false); Daniel→Mara min 54 (false); Daniel→Mara min 66 (false); Leo→Daniel min 66 (false); Daniel→Mara min 69 (false); Leo→Daniel min 69 (false); Daniel→Mara min 72 (false); Leo→Daniel min 72 (false); Mara→Daniel min 81 (false); Leo→Daniel min 81 (false); Daniel→Mara min 84 (false); Mara→Daniel min 84 (false); Leo→Daniel min 84 (false); Daniel→Mara min 87 (false); Leo→Daniel min 87 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 3 | 35% (28/81) | 6 (min 60–66) |
| miscount, Flash Lite, seed 3 | 70 | 0 | 52 | Mara→Daniel min 24 (false); Mara→Daniel min 30 (false); Daniel→Mara min 33 (false); Daniel→Mara min 36 (false); Mara→Daniel min 36 (false); Daniel→Mara min 39 (false); Daniel→Mara min 45 (false); Mara→Daniel min 48 (false); Daniel→Mara min 48 (false); Mara→Daniel min 51 (false); Leo→Daniel min 51 (false); Daniel→Mara min 54 (false); Mara→Daniel min 54 (false); Leo→Daniel min 54 (false); Daniel→Mara min 57 (false); Daniel→Mara min 66 (false); Leo→Daniel min 69 (false); Daniel→Mara min 75 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, ask) | 7 | 27% (14/52) | 12 (min 78–90) |

`metrics5.py` computes every row from the runs' transcripts in the same way. The first five rows are the v4 runs, for comparison.

- **Invalid answers**: model answers the rules could not use (not JSON, an option not offered, a missing field...); the rules chose instead.
- **Accusations**: every *accuse* act, in order. *True* when the accused took the can; in miscount every accusation is false.
- **Anyone confessed falsely**: the rules offer *admit taking it* only to whoever took it, so a false confession can only be in words. Every line by someone else was searched for "I took / ate / stole / had (it, the can, the food...)", and every hit is listed.
- **Longest run of one speech act**: turns in a row in which one person used the same kind of speech act. Since the second step the rules stop it at 3.
- **Question asked again unanswered**: the times "who took the can?" was asked again when nothing had answered it since it was last asked (no confession and no accusation anywhere in the house).
- **Lines that are reassurance** and **longest stretch with no model decision**: as in REPORT-4.

### Grudges at minute 90, with their events

```
Grudges at minute 90, with their events (in the holder's own terms: "you" is the one holding the grudge):

daniel_ate_it, Flash Lite, seed 1:
- none

daniel_ate_it, Flash Lite, seed 2:
- none

daniel_ate_it, Flash Lite, seed 3:
- none

daniel_ate_it, Flash Lite, seed 4:
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 09, 12, 15, 18, 63.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 06, 09, 12, 15, 54.

daniel_ate_it, Flash Lite, seed 5:
- Leo against Daniel, 3/3: Daniel accused you of taking the can at minute 09, and you had not; named Daniel in angry_at at minutes 12, 15, 18, 24, 36, 63.

daniel_ate_it, Gemma 4 31B, seed 1:
- Daniel against Leo, 1/3: named Leo in angry_at at minutes 15, 66.

daniel_ate_it, Gemma 4 31B, seed 2:
- none

daniel_ate_it, Gemma 4 31B, seed 3:
- none

daniel_ate_it, Gemma 4 31B, seed 4:
- none

daniel_ate_it, Gemma 4 31B, seed 5:
- none

mara_ate_it, Flash Lite, seed 1:
- Daniel against Mara, 3/3: Mara admitted taking it at minute 27, after denying it to you at minute 24; named Mara in angry_at at minutes 27, 30, 33, 36, 66.
- Elena against Mara, 1/3: Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Mara, 1/3: Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Elena, 2/3: Elena ate a portion in front of you at minute 30, while you were hungry; named Elena in angry_at at minutes 30.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 00, 03, 06, 12, 15, 21, 24, 27, 30, 33, 36, 54.

mara_ate_it, Flash Lite, seed 2:
- Daniel against Mara, 3/3: Mara admitted taking it at minute 09, after denying it to you at minute 06; named Mara in angry_at at minutes 09, 12, 15, 18, 27, 30, 33, 78.
- Elena against Daniel, 1/3: named Daniel in angry_at at minutes 12, 15.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 03, 06, 12, 15, 30, 54.

mara_ate_it, Flash Lite, seed 3:
- Daniel against Mara, 3/3: named Mara in angry_at at minutes 18, 21, 24, 30, 33, 36, 66.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 21, 24, 33, 36.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 30, 33, 36, 39, 54.

miscount, Flash Lite, seed 1:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 54, and you had not; named Mara in angry_at at minutes 15, 18, 24, 30, 33, 36, 39, 42, 66.
- Leo against Daniel, 1/3: named Daniel in angry_at at minutes 39, 42.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 66, and you had not; named Daniel in angry_at at minutes 06, 09, 12, 15, 18, 21, 24, 30, 33, 36, 39, 54.

miscount, Flash Lite, seed 2:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 06, and you had not; Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 21, and you had not; Mara accused you of taking the can at minute 27, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 39, and you had not; Mara accused you of taking the can at minute 45, and you had not; Mara accused you of taking the can at minute 81, and you had not; Mara accused you of taking the can at minute 84, and you had not; named Mara in angry_at at minutes 09, 12, 15, 18, 21, 24, 27, 30, 33, 39, 42, 45, 48, 51, 54, 66, 69, 72, 75, 81, 84, 87.
- Daniel against Leo, 3/3: Leo accused you of taking the can at minute 66, and you had not; Leo accused you of taking the can at minute 69, and you had not; Leo accused you of taking the can at minute 72, and you had not; Leo accused you of taking the can at minute 81, and you had not; Leo accused you of taking the can at minute 84, and you had not; Leo accused you of taking the can at minute 87, and you had not.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 54, 57, 66, 69, 72, 75, 81, 84, 87.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 15, and you had not; Daniel accused you of taking the can at minute 18, and you had not; Daniel accused you of taking the can at minute 24, and you had not; Daniel accused you of taking the can at minute 27, and you had not; Daniel accused you of taking the can at minute 30, and you had not; Daniel accused you of taking the can at minute 42, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 69, and you had not; Daniel accused you of taking the can at minute 72, and you had not; Daniel accused you of taking the can at minute 84, and you had not; Daniel accused you of taking the can at minute 87, and you had not; named Daniel in angry_at at minutes 03, 06, 09, 12, 15, 18, 21, 27, 30, 39, 42, 45, 48, 51, 54, 69, 72, 81, 84, 87.

miscount, Flash Lite, seed 3:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 36, and you had not; Mara accused you of taking the can at minute 48, and you had not; Mara accused you of taking the can at minute 51, and you had not; Mara accused you of taking the can at minute 54, and you had not; named Mara in angry_at at minutes 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 66, 75.
- Daniel against Leo, 3/3: Leo accused you of taking the can at minute 51, and you had not; Leo accused you of taking the can at minute 54, and you had not; Leo accused you of taking the can at minute 69, and you had not.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 39, 42, 48, 51, 54, 57, 60, 69.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 57, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 75, and you had not; named Daniel in angry_at at minutes 06, 09, 12, 21, 24, 27, 30, 33, 36, 39, 48, 51, 54, 57.
```

## Comparison

These are observations; the judge is a person reading the stories below.

### Flash Lite against Gemma 4 31B, on daniel_ate_it (five seeds each)

- **Gemma's family is even quieter.**
  - Per run: 8 to 13 lines against Flash Lite's 18 to 26, and 13 to 21 model calls against 29 to 41.
  - Nobody accuses anyone in any Gemma run, and "who took the can?" is never asked twice.
  - Reassurance is 60% to 78% of its lines, against 20% to 50% for Flash Lite.
  - Daniel never confesses (Flash Lite: once in five). Gemma's Daniel does not deny it much either; he plays the leader: "I've got this, everyone. Just keep calm and trust me."
  - One line stands out. In seed 1, Leo at minute 63: "Daniel, you've been saying you're handling it for forty-five minutes. What exactly are you doing?" Nobody follows it up.
- **Gemma's five mornings are nearly the same morning.**
  - Most of them stay silent at minute 0, and every run's first conversation is over by minute 9.
  - After that, each run's inner moments fall at exactly the same minutes: 15, 30, 33, 54, 63, 66 and 75. Those are the minutes when each person's hunger crosses a level, and the hunger rates are fixed.
  - So the skeleton of all five stories is the rules' hunger clock; only the words change ("I'm so hungry, I can't think" from Mara at minute 54 in four of the five).
  - Different seeds gave Gemma very little variety.
- **So the daniel_ate_it stalemate is not a Flash Lite quirk.** Both models leave Daniel unchallenged. Flash Lite fills the silence with repeated questions and denials; Gemma just goes quiet.
- **Neither model gave an unusable answer** in these runs (0 fallbacks in all 16). The JSON schema holds for both.
- **Gemma's free endpoint was the practical problem.** Its five runs needed 213 requests for 87 answers; the other 126 were refused with 500 or 503 errors and retried. Seed 2 needed four processes to finish (see its output). A seed-2 probe showed it was the server's availability, not the prompt: the same prompt was accepted twice and refused once, minutes apart.

### daniel_ate_it against the new scenarios, on Flash Lite

- **mara_ate_it: the culprit confesses every time.**
  - Mara admits it at minutes 27, 9 and 0 (seeds 1 to 3); Daniel confessed once in five daniel_ate_it runs.
  - Her lines before that are frightened denials ("Why is everyone looking at me like I'm a thief?"). They are in character: impulsive and anxious, where Daniel is proud and dominant.
  - After the confession, Daniel accuses her again and again (4 to 7 true accusations a run) and ends each run with a grudge of 3 against her. Leo and Elena defend her ("Mara already admitted it and apologized, Daniel").
  - The event grudges fire as designed: admitting it after denying it (seeds 1 and 2), and eating in front of the hungry (seeds 1 and 3).
- **miscount: the busiest mornings by far.**
  - 56, 93 and 70 model calls and 41, 81 and 52 lines; the longest quiet stretch falls to 6 to 12 minutes.
  - In all three seeds Mara and Daniel accuse each other falsely, over and over. Mara brings up the emptied bag ("Daniel, you're the one who always goes through my things"), and in seeds 2 and 3 Leo turns on Daniel too.
  - Every grudge at minute 90 comes from false accusations and stands at 3.
  - Nobody confessed falsely, in words or otherwise.
- **The same backstory gives very different mornings depending on who took the can.**
  - The one clear rule effect: the rules do not offer "ask who took the can" to someone who knows who took it. So a guilty Daniel cannot make his most natural move, which he makes over and over when innocent ("Someone in this room needs to tell the truth right now"). Guilty, he soothes, and nobody suspects him; innocent, he demands answers, and Mara turns on him.
  - In daniel_ate_it the only accusations of Daniel come after he confesses, or from his own false one against Leo.
- **What holds everywhere:**
  - The 3-in-a-row limit binds in every Flash Lite run: the longest run of one speech act is exactly 3.
  - "Who took the can?" still gets asked again unanswered: 0 to 8 times a run.
  - Nobody took anyone aside in any of the 16 runs.
  - In 12 of the 16 the longest quiet stretch is minutes 36 to 54, or starts at 69 or 78. That gap sits between hunger crossings, whatever the scenario or model.

### Which problems are general, and which belong to this scenario or model

- **General, seen in every scenario and with both models:**
  - Quiet stretches are set by the hunger clock.
  - Take-aside is never used.
  - A large share of reassurance.
  - Questions repeated without an answer (not with Gemma, which hardly asks).
- **This scenario:** the stalemate. It comes from the culprit being the proud leader whom nobody suspects, and who, knowing the answer, is never offered the question. With Mara as culprit, or with no culprit, accusations and confessions come on their own.
- **This model:** Flash Lite's repeated questions and denials, and Gemma's passivity and near-identical mornings across seeds.

## What changed, and why

- **Scenarios.** The Unity scenario data (`Assets/_Project/Data/Scenario/morning.json`, read only) already has variants for both cases, so I used them rather than defining new ones:
  - *mara_ate_it*, where someone else took the can: "In the night Mara eats a can sitting on the kitchen floor";
  - *miscount*, where nobody did: "Nobody took anything. There were only ever two."

  I did not use *leo_ate_it*: it is under `held_out_variants`, and its note says it is held out for S1.1, with predictions to be committed before it is first run. Running it here would spend it. Like daniel_ate_it's night, Mara's gets "Nobody sees." appended, because the data lists no witnesses. The rest of the backstory is the same in all three.
- **Where Daniel was hard-coded as the culprit, now read from the scenario:**
  - `data.py`: the `CULPRIT` constant, and Daniel's night inside the fixed backstory list. They are now `SCENARIOS`, with `culprit()` and `backstory()`.
  - `world.py`: who knows where the can went, and their pinned line; who starts with guilt; who is offered *admit taking it*; whose guilt the events raise; which accusations count as false.
  - `story.py`: the title; the guilt bullet in *How to read it*; the cast table; the backstory table; the guilt lines; "Who else knows Daniel took it"; the guilt shown at minute 90. The story's words for the culprit use their own pronouns (data.PRONOUNS).
  - `morning.py`: the run's name.

  In miscount there is no culprit, so nobody has guilt or is offered *admit taking it*, and every accusation is false. `metrics4.py` still reads v4 runs only, and v1/ to v4/ are frozen copies, so they were left alone.
- **The second model.** Gemma 4 31B's API name is `gemma-4-31b-it` (from the model list).
  - It accepts the same system instruction and JSON response schema. Of five probe requests, the two with both on that got through returned valid JSON with no thinking; the other three failed with a 500 or 503 error, which the client retries.
  - Without the schema it thinks for about 740 tokens and wraps its JSON in a code fence, so the schema stays on.
  - It is `models.gemma` in `config.json`, chosen with `--model gemma`. Calls are spaced 6.5 s apart: about 1,500 tokens a call keeps it under 16K tokens per minute, and well under 30 requests per minute.
  - Runs made with it are named `...-gemma-seed<N>` and cached under its own model name. The probe script is `probe_model.py`, and its output is below.
- **Tooling, not behaviour:**
  - `morning.py` takes `--scenario`, `--model` and `--out`. The story's command line shows only flags that differ from the defaults, so daniel_ate_it's Flash Lite stories are byte-identical.
  - `v4/` is a frozen copy of the fourth version, with `v4/check.py`.
  - `metrics5.py` is new.
- **Tests:** six new ones. One runs each scenario with the fake model; the others check where the culprit comes from, false accusations in miscount, Mara's guilt, the story's words for the culprit, and the second model's name and spacing.
- **target-morning.md is no longer in `Docs/understanding/`.** It was removed at 12:56 UTC today; my commands in this step did not touch `Docs/`. The test that keeps its text out of every prompt now reads it from the file if it exists, else from its section in `Docs/understanding/understanding-all.md`. That copy predates the four Never lines added in the second step, so the test also checks those four lines verbatim from that step's brief. If both copies are gone, the test skips with a message instead of passing.
- Nothing was tuned before or after the runs.

## Commands and their output

All commands run in `Prototypes/llm-morning/`, using the venv's Python (`.venv/Scripts/python`).

### Checking Gemma

```bash
python list_models.py gemma
python probe_model.py gemma-4-31b-it
python probe_model.py gemma-4-31b-it [--no-schema] [--no-system]   # one at a time
```

```
models/gemma-4-26b-a4b-it                               Gemma 4 26B A4B IT
models/gemma-4-31b-it                                   Gemma 4 31B IT

model gemma-4-31b-it; system instruction on; JSON schema on
refused: 500 INTERNAL: Internal error encountered.

model gemma-4-31b-it; system instruction on; JSON schema on
accepted. prompt tokens 1341, answer tokens 86, thinking tokens None, finish FinishReason.STOP
answer: {"option": "reassure_all", "say": "Don't worry. I'll figure out this out and I'll make sure we're all safe.", "feeling": "anxious", "reason": "I need to maintain my position of authority and protect my family, even if I'm the oldest.", "suspects": "nobody", "angry_at": "nobody"}
---
model gemma-4-31b-it; system instruction on; JSON schema off
accepted. prompt tokens 1341, answer tokens 80, thinking tokens 740, finish FinishReason.STOP
answer: ```json
{"option": "reassure_all", "say": "Don't panic. We've still got food, and I'll make sure we're okay.", "feeling": "anxious", "reason": "I need to maintain control and keep them from worrying.", "suspects": "nobody", "angry_at": "nobody"}
```
---
model gemma-4-31b-it; system instruction off; JSON schema on
refused: 500 INTERNAL: Internal error encountered.
---
model gemma-4-31b-it; system instruction off; JSON schema off
refused: 503 UNAVAILABLE: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.
---
```

Later, when Gemma seed 2 kept stopping on the same prompt, `probe_prompt.py` rebuilt that prompt from the cache and sent it on its own. It was accepted with seed 1 and seed 2, then refused a few minutes later, which shows the server's availability was the cause, not the prompt:

```bash
python probe_prompt.py cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed2.json daniel_ate_it 2 gemma-4-31b-it <seed>
```

```
first unanswered prompt: You are Daniel, 25, the eldest son of the family (Elena, 42,... (Now, minute 66, you are in the kitchen.)
seed 1: accepted: {"option": "reassure_all", "say": "Stay calm, everyone. I'll make sure we all get through this together.", "feeling": "anxious", "reason": "I need to maintain the appearance of being in control and protecting the family.", "suspects": "nobody", "angry_at": "nobody"}
first unanswered prompt: You are Daniel, 25, the eldest son of the family (Elena, 42,... (Now, minute 66, you are in the kitchen.)
seed 2: accepted: {"option": "reassure_mara", "say": "Mara, it's okay. I'll make sure you're fed.", "feeling": "protective", "reason": "Mara is feeling sick from hunger and I need to show I'm in control and caring for her.", "suspects": "nobody", "angry_at": "nobody"}
seed 2: refused: 500 INTERNAL
```

### Tests (fake model and stubbed API only)

```bash
python -m unittest -v test_morning
```

```
test_a_morning_completes_and_writes_a_story (test_morning.FakeMorningTest.test_a_morning_completes_and_writes_a_story) ... ok
test_an_admission_cannot_be_taken_back (test_morning.FakeMorningTest.test_an_admission_cannot_be_taken_back) ... ok
test_at_most_one_call_per_person_per_turn (test_morning.FakeMorningTest.test_at_most_one_call_per_person_per_turn) ... ok
test_every_kind_of_broken_answer_falls_back_to_the_rules (test_morning.FakeMorningTest.test_every_kind_of_broken_answer_falls_back_to_the_rules) ... ok
test_nothing_from_target_morning_reaches_a_prompt (test_morning.FakeMorningTest.test_nothing_from_target_morning_reaches_a_prompt) ... ok
test_only_daniel_knows_and_only_daniel_may_confess (test_morning.FakeMorningTest.test_only_daniel_knows_and_only_daniel_may_confess) ... ok
test_prompts_are_short (test_morning.FakeMorningTest.test_prompts_are_short) ... ok
test_replay_is_byte_for_byte_with_no_client_reached (test_morning.FakeMorningTest.test_replay_is_byte_for_byte_with_no_client_reached) ... ok
test_replay_without_a_cache_stops_cleanly (test_morning.FakeMorningTest.test_replay_without_a_cache_stops_cleanly) ... ok
test_seeds_do_not_share_answers (test_morning.FakeMorningTest.test_seeds_do_not_share_answers) ... ok
test_the_call_cap_counts_answers_from_an_earlier_run (test_morning.FakeMorningTest.test_the_call_cap_counts_answers_from_an_earlier_run) ... ok
test_the_call_cap_stops_the_morning_cleanly (test_morning.FakeMorningTest.test_the_call_cap_stops_the_morning_cleanly) ... ok
test_calls_are_spaced (test_morning.GeminiClientTest.test_calls_are_spaced) ... ok
test_daily_quota_stops_keeps_the_cache_and_resumes (test_morning.GeminiClientTest.test_daily_quota_stops_keeps_the_cache_and_resumes) ... ok
test_missing_key_stops_with_a_clear_message (test_morning.GeminiClientTest.test_missing_key_stops_with_a_clear_message) ... ok
test_per_minute_429_backs_off_and_retries (test_morning.GeminiClientTest.test_per_minute_429_backs_off_and_retries) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/6
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/6
ok
test_repeated_429_gives_up_cleanly (test_morning.GeminiClientTest.test_repeated_429_gives_up_cleanly) ...     [429 RESOURCE_EXHAUSTED] waiting 8s, retry 1/2
    [429 RESOURCE_EXHAUSTED] waiting 10s, retry 2/2
ok
test_the_key_is_never_printed_or_saved (test_morning.GeminiClientTest.test_the_key_is_never_printed_or_saved) ... ok
test_a_false_accusation_raises_a_grudge_toward_the_accuser (test_morning.PressureTest.test_a_false_accusation_raises_a_grudge_toward_the_accuser) ... ok
test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed (test_morning.PressureTest.test_a_grudge_falls_a_step_only_15_minutes_after_it_last_changed) ... ok
test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes (test_morning.PressureTest.test_a_grudge_or_suspicion_rises_a_step_and_falls_at_most_a_step_per_15_minutes) ... ok
test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster (test_morning.PressureTest.test_angry_at_raises_a_grudge_and_nobody_cannot_bring_it_down_faster) ... ok
test_confessing_after_denying_it_and_after_accusing (test_morning.PressureTest.test_confessing_after_denying_it_and_after_accusing) ... ok
test_daniel_accusing_someone_counts_once (test_morning.PressureTest.test_daniel_accusing_someone_counts_once) ... ok
test_daniels_guilt_rises_by_the_rules (test_morning.PressureTest.test_daniels_guilt_rises_by_the_rules) ... ok
test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not (test_morning.PressureTest.test_eating_in_front_of_someone_hungry_raises_a_grudge_but_sharing_does_not) ... ok
test_inner_moments_come_at_most_once_every_9_minutes (test_morning.PressureTest.test_inner_moments_come_at_most_once_every_9_minutes) ... ok
test_naming_yourself_counts_as_nobody (test_morning.PressureTest.test_naming_yourself_counts_as_nobody) ... ok
test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
test_reassure_is_not_offered_toward_a_grudge_of_3 (test_morning.PressureTest.test_reassure_is_not_offered_toward_a_grudge_of_3) ... ok
test_take_aside_accepted (test_morning.PressureTest.test_take_aside_accepted) ... ok
test_take_aside_needs_someone_yet_to_act_and_an_empty_room (test_morning.PressureTest.test_take_aside_needs_someone_yet_to_act_and_an_empty_room) ... ok
test_take_aside_refused (test_morning.PressureTest.test_take_aside_refused) ... ok
test_a_second_model_from_the_config (test_morning.ScenarioTest.test_a_second_model_from_the_config) ... ok
test_each_scenario_runs_with_the_fake_model (test_morning.ScenarioTest.test_each_scenario_runs_with_the_fake_model) ... ok
test_in_miscount_every_accusation_is_false (test_morning.ScenarioTest.test_in_miscount_every_accusation_is_false) ... ok
test_mara_as_the_culprit_carries_the_guilt (test_morning.ScenarioTest.test_mara_as_the_culprit_carries_the_guilt) ... ok
test_the_culprit_comes_from_the_scenario (test_morning.ScenarioTest.test_the_culprit_comes_from_the_scenario) ... ok
test_the_story_speaks_of_the_culprit (test_morning.ScenarioTest.test_the_story_speaks_of_the_culprit) ... ok
test_a_conversation_ends_after_two_full_turns_with_nothing_new (test_morning.SequentialTalkTest.test_a_conversation_ends_after_two_full_turns_with_nothing_new) ... ok
test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again (test_morning.SequentialTalkTest.test_a_speech_act_used_three_turns_in_a_row_is_not_offered_again) ... ok
test_an_inner_moment_can_start_the_talk_again (test_morning.SequentialTalkTest.test_an_inner_moment_can_start_the_talk_again) ... ok
test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn (test_morning.SequentialTalkTest.test_each_prompt_holds_the_lines_already_said_in_the_room_this_turn) ... ok
test_metrics_work_out_the_same_conversations_as_the_morning (test_morning.SequentialTalkTest.test_metrics_work_out_the_same_conversations_as_the_morning) ... ok
test_no_speech_act_runs_past_three_turns_in_any_fake_morning (test_morning.SequentialTalkTest.test_no_speech_act_runs_past_three_turns_in_any_fake_morning) ... ok
test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to (test_morning.SequentialTalkTest.test_strongest_shown_feeling_goes_first_unless_someone_was_spoken_to) ... ok
test_the_one_just_accused_acts_next (test_morning.SequentialTalkTest.test_the_one_just_accused_acts_next) ... ok
test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house (test_morning.SequentialTalkTest.test_the_prompt_gives_forms_of_address_and_the_only_things_in_the_house) ... ok
test_ties_are_broken_by_the_seed (test_morning.SequentialTalkTest.test_ties_are_broken_by_the_seed) ... ok

----------------------------------------------------------------------
Ran 49 tests in 11.311s

OK
```

### The v4 runs, replayed with the new code

```bash
for s in 1 2 3 4 5; do env -u GEMINI_API_KEY python morning.py --seed $s --replay --out v4; done
```

```
daniel_ate_it-seed1: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed1.json holds 36 answers
  api_requests: 0
  byte for byte against runs\v4\daniel_ate_it-seed1.md: IDENTICAL
daniel_ate_it-seed2: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed2.json holds 39 answers
  api_requests: 0
  byte for byte against runs\v4\daniel_ate_it-seed2.md: IDENTICAL
daniel_ate_it-seed3: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed3.json holds 39 answers
  api_requests: 0
  byte for byte against runs\v4\daniel_ate_it-seed3.md: IDENTICAL
daniel_ate_it-seed4: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed4.json holds 29 answers
  api_requests: 0
  byte for byte against runs\v4\daniel_ate_it-seed4.md: IDENTICAL
daniel_ate_it-seed5: model gemini-3.5-flash-lite, replay from cache only; cache cache\v4\gemini-3.5-flash-lite-daniel_ate_it-seed5.json holds 41 answers
  api_requests: 0
  byte for byte against runs\v4\daniel_ate_it-seed5.md: IDENTICAL
```

### daniel_ate_it, Gemma, seed 1

```bash
python morning.py --model gemma --seed 1
```

```
daniel_ate_it-gemma-seed1: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed1.json holds 0 answers
    [500 INTERNAL] waiting 5s, retry 1/6
  min 00: model asked for 4; so far 4 live, 0 cached, 5 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 5s, retry 1/6
  min 15: model asked for 4; so far 8 live, 0 cached, 14 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
  min 18: model asked for 4; so far 12 live, 0 cached, 23 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
  min 21: model asked for 2; so far 14 live, 0 cached, 28 API requests
  min 30: model asked for 1; so far 15 live, 0 cached, 29 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 33: model asked for 1; so far 16 live, 0 cached, 32 API requests
  min 54: model asked for 1; so far 17 live, 0 cached, 33 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
  min 63: model asked for 1; so far 18 live, 0 cached, 35 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
  min 66: model asked for 1; so far 19 live, 0 cached, 37 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [500 INTERNAL] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 80s, retry 5/6
    [500 INTERNAL] waiting 5s, retry 1/6
  min 75: model asked for 2; so far 21 live, 0 cached, 45 API requests

wrote runs/v5/daniel_ate_it-gemma-seed1.md
  api_requests: 45
  answers_live: 21
  answers_from_cache: 0
  model_decisions: 21
  fallbacks: 0
  routine_decisions: 99
  lines_spoken: 13
  inner_moments: 8
  private_talks: 0
  max_prompt_tokens_estimated: 1397
  max_prompt_tokens_counted_by_api: 1368
  run_seconds: 1122.0
  story_sha256: a564d9d71f5e6b2c2d19209e65188c5d1d3d62085428518692572901bd9c385c
```

### daniel_ate_it, Gemma, seed 2

```bash
python morning.py --model gemma --seed 2
```

```
daniel_ate_it-gemma-seed2: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json holds 0 answers
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
  min 00: model asked for 4; so far 4 live, 0 cached, 10 API requests
  min 03: model asked for 2; so far 6 live, 0 cached, 12 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
  min 15: model asked for 1; so far 7 live, 0 cached, 15 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 30: model asked for 1; so far 8 live, 0 cached, 18 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
  min 33: model asked for 1; so far 9 live, 0 cached, 21 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
  min 54: model asked for 1; so far 10 live, 0 cached, 23 API requests
  min 63: model asked for 1; so far 11 live, 0 cached, 24 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
    [500 INTERNAL] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 80s, retry 5/6
    [500 INTERNAL] waiting 120s, retry 6/6

stopped: still refused (503 UNAVAILABLE) after 6 retries.
Answers received so far (11) are kept in cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json.
To resume, run the same command again once the limit has passed (the free daily quota resets at midnight Pacific time): python morning.py --model gemma --seed 2
Cached answers are reused, so only the prompts not yet answered are sent.
--- resumed at 14:47 UTC, after the stop above (Gemma's service still refusing after 6 retries); the 11 cached answers are reused ---
daniel_ate_it-gemma-seed2: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json holds 11 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 2; so far 0 live, 6 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 7 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 8 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 9 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 10 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 11 cached, 0 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 80s, retry 5/6
    [503 UNAVAILABLE] waiting 120s, retry 6/6

stopped: still refused (500 INTERNAL) after 6 retries.
Answers received so far (11) are kept in cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json.
To resume, run the same command again once the limit has passed (the free daily quota resets at midnight Pacific time): python morning.py --model gemma --seed 2
Cached answers are reused, so only the prompts not yet answered are sent.
--- resumed again at 14:56 UTC (a probe showed the same prompt is accepted now); the 11 cached answers are reused ---
daniel_ate_it-gemma-seed2: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json holds 11 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 2; so far 0 live, 6 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 7 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 8 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 9 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 10 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 11 cached, 0 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 40s, retry 4/6
    [503 UNAVAILABLE] waiting 80s, retry 5/6
    [500 INTERNAL] waiting 120s, retry 6/6

stopped: still refused (503 UNAVAILABLE) after 6 retries.
Answers received so far (11) are kept in cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json.
To resume, run the same command again once the limit has passed (the free daily quota resets at midnight Pacific time): python morning.py --model gemma --seed 2
Cached answers are reused, so only the prompts not yet answered are sent.
--- resume attempt 1 at 15:03 UTC; the cached answers are reused ---
daniel_ate_it-gemma-seed2: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed2.json holds 11 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 2; so far 0 live, 6 cached, 0 API requests
  min 15: model asked for 1; so far 0 live, 7 cached, 0 API requests
  min 30: model asked for 1; so far 0 live, 8 cached, 0 API requests
  min 33: model asked for 1; so far 0 live, 9 cached, 0 API requests
  min 54: model asked for 1; so far 0 live, 10 cached, 0 API requests
  min 63: model asked for 1; so far 0 live, 11 cached, 0 API requests
  min 66: model asked for 1; so far 1 live, 11 cached, 1 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 75: model asked for 1; so far 2 live, 11 cached, 4 API requests

wrote runs/v5/daniel_ate_it-gemma-seed2.md
  api_requests: 4
  answers_live: 2
  answers_from_cache: 11
  model_decisions: 13
  fallbacks: 0
  routine_decisions: 107
  lines_spoken: 9
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1398
  max_prompt_tokens_counted_by_api: 1372
  run_seconds: 76.7
  story_sha256: aee3cfdb71bb69b799b688e0b26a48f1d7faadb05f993407ff245177dff31425
```

### daniel_ate_it, Gemma, seed 3

```bash
python morning.py --model gemma --seed 3
```

```
daniel_ate_it-gemma-seed3: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 2; so far 6 live, 0 cached, 6 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 15: model asked for 1; so far 7 live, 0 cached, 9 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
  min 18: model asked for 4; so far 11 live, 0 cached, 20 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
  min 21: model asked for 3; so far 14 live, 0 cached, 25 API requests
  min 30: model asked for 1; so far 15 live, 0 cached, 26 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
  min 33: model asked for 1; so far 16 live, 0 cached, 28 API requests
  min 54: model asked for 1; so far 17 live, 0 cached, 29 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
  min 63: model asked for 1; so far 18 live, 0 cached, 31 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
  min 66: model asked for 1; so far 19 live, 0 cached, 35 API requests
  min 75: model asked for 1; so far 20 live, 0 cached, 36 API requests

wrote runs/v5/daniel_ate_it-gemma-seed3.md
  api_requests: 36
  answers_live: 20
  answers_from_cache: 0
  model_decisions: 20
  fallbacks: 0
  routine_decisions: 100
  lines_spoken: 12
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1373
  run_seconds: 766.2
  story_sha256: 014deaef985ba94c5b46f47556ffe656ea2d344c42b08e62430eb46b01db494b
```

### daniel_ate_it, Gemma, seed 4

```bash
python morning.py --model gemma --seed 4
```

```
daniel_ate_it-gemma-seed4: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed4.json holds 0 answers
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 00: model asked for 4; so far 4 live, 0 cached, 9 API requests
  min 15: model asked for 1; so far 5 live, 0 cached, 10 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
  min 18: model asked for 2; so far 7 live, 0 cached, 15 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 21: model asked for 4; so far 11 live, 0 cached, 22 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 5s, retry 1/6
  min 24: model asked for 2; so far 13 live, 0 cached, 28 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 40s, retry 4/6
  min 30: model asked for 1; so far 14 live, 0 cached, 33 API requests
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
  min 33: model asked for 1; so far 15 live, 0 cached, 37 API requests
  min 54: model asked for 1; so far 16 live, 0 cached, 38 API requests
  min 63: model asked for 1; so far 17 live, 0 cached, 39 API requests
  min 66: model asked for 1; so far 18 live, 0 cached, 40 API requests
  min 75: model asked for 1; so far 19 live, 0 cached, 41 API requests

wrote runs/v5/daniel_ate_it-gemma-seed4.md
  api_requests: 41
  answers_live: 19
  answers_from_cache: 0
  model_decisions: 19
  fallbacks: 0
  routine_decisions: 101
  lines_spoken: 10
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1386
  run_seconds: 992.4
  story_sha256: 3809a050a51fc4d61eedd03c36f888c6a11c4210a818ef04f72c395def33978a
```

### daniel_ate_it, Gemma, seed 5

```bash
python morning.py --model gemma --seed 5
```

```
daniel_ate_it-gemma-seed5: model gemma-4-31b-it, fresh; cache cache\v5\gemma-4-31b-it-daniel_ate_it-gemma-seed5.json holds 0 answers
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [500 INTERNAL] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [500 INTERNAL] waiting 40s, retry 4/6
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 5s, retry 1/6
  min 00: model asked for 4; so far 4 live, 0 cached, 14 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 03: model asked for 3; so far 7 live, 0 cached, 21 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
  min 15: model asked for 1; so far 8 live, 0 cached, 24 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
  min 30: model asked for 1; so far 9 live, 0 cached, 28 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [500 INTERNAL] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 80s, retry 5/6
  min 33: model asked for 1; so far 10 live, 0 cached, 34 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [503 UNAVAILABLE] waiting 10s, retry 2/6
    [503 UNAVAILABLE] waiting 20s, retry 3/6
    [503 UNAVAILABLE] waiting 40s, retry 4/6
    [500 INTERNAL] waiting 80s, retry 5/6
  min 54: model asked for 1; so far 11 live, 0 cached, 40 API requests
  min 63: model asked for 1; so far 12 live, 0 cached, 41 API requests
  min 66: model asked for 1; so far 13 live, 0 cached, 42 API requests
    [500 INTERNAL] waiting 5s, retry 1/6
    [500 INTERNAL] waiting 10s, retry 2/6
  min 75: model asked for 1; so far 14 live, 0 cached, 45 API requests

wrote runs/v5/daniel_ate_it-gemma-seed5.md
  api_requests: 45
  answers_live: 14
  answers_from_cache: 0
  model_decisions: 14
  fallbacks: 0
  routine_decisions: 106
  lines_spoken: 8
  inner_moments: 7
  private_talks: 0
  max_prompt_tokens_estimated: 1399
  max_prompt_tokens_counted_by_api: 1357
  run_seconds: 1272.3
  story_sha256: 3c2c36bd44ba171f4b51392e428db3fbf42e4d4000f18dc35e17a5341e50a89e
```

### mara_ate_it, Flash Lite, seed 1

```bash
python morning.py --scenario mara_ate_it --seed 1
```

```
mara_ate_it-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-mara_ate_it-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 1; so far 13 live, 0 cached, 13 API requests
  min 12: model asked for 4; so far 17 live, 0 cached, 17 API requests
  min 15: model asked for 3; so far 20 live, 0 cached, 20 API requests
  min 21: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 24: model asked for 4; so far 28 live, 0 cached, 28 API requests
  min 27: model asked for 4; so far 32 live, 0 cached, 32 API requests
  min 30: model asked for 4; so far 36 live, 0 cached, 36 API requests
  min 33: model asked for 4; so far 40 live, 0 cached, 40 API requests
  min 36: model asked for 4; so far 44 live, 0 cached, 44 API requests
  min 54: model asked for 1; so far 45 live, 0 cached, 45 API requests
  min 66: model asked for 1; so far 46 live, 0 cached, 46 API requests

wrote runs/v5/mara_ate_it-seed1.md
  api_requests: 46
  answers_live: 46
  answers_from_cache: 0
  model_decisions: 46
  fallbacks: 0
  routine_decisions: 74
  lines_spoken: 36
  inner_moments: 5
  private_talks: 0
  max_prompt_tokens_estimated: 1399
  max_prompt_tokens_counted_by_api: 1374
  run_seconds: 328.9
  story_sha256: a0f20d98c84ef230929f723078188e2b0da86082d54263682c7f3a74b1175f0e
```

### mara_ate_it, Flash Lite, seed 2

```bash
python morning.py --scenario mara_ate_it --seed 2
```

```
mara_ate_it-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-mara_ate_it-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests
  min 09: model asked for 4; so far 15 live, 0 cached, 15 API requests
  min 12: model asked for 4; so far 19 live, 0 cached, 19 API requests
  min 15: model asked for 4; so far 23 live, 0 cached, 23 API requests
  min 18: model asked for 2; so far 25 live, 0 cached, 25 API requests
  min 24: model asked for 1; so far 26 live, 0 cached, 26 API requests
  min 27: model asked for 3; so far 29 live, 0 cached, 29 API requests
  min 30: model asked for 4; so far 33 live, 0 cached, 33 API requests
  min 33: model asked for 1; so far 34 live, 0 cached, 34 API requests
  min 54: model asked for 1; so far 35 live, 0 cached, 35 API requests
  min 63: model asked for 1; so far 36 live, 0 cached, 36 API requests
  min 78: model asked for 1; so far 37 live, 0 cached, 37 API requests

wrote runs/v5/mara_ate_it-seed2.md
  api_requests: 37
  answers_live: 37
  answers_from_cache: 0
  model_decisions: 37
  fallbacks: 0
  routine_decisions: 83
  lines_spoken: 26
  inner_moments: 8
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1375
  run_seconds: 259.8
  story_sha256: 7407c076ea13e02066f2e60938781a3bc3f03b0d0f29d9f22aba2c1eadc4d281
```

### mara_ate_it, Flash Lite, seed 3

```bash
python morning.py --scenario mara_ate_it --seed 3
```

```
mara_ate_it-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-mara_ate_it-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 1; so far 13 live, 0 cached, 13 API requests
  min 15: model asked for 2; so far 15 live, 0 cached, 15 API requests
  min 18: model asked for 3; so far 18 live, 0 cached, 18 API requests
  min 21: model asked for 4; so far 22 live, 0 cached, 22 API requests
  min 24: model asked for 2; so far 24 live, 0 cached, 24 API requests
  min 30: model asked for 3; so far 27 live, 0 cached, 27 API requests
  min 33: model asked for 4; so far 31 live, 0 cached, 31 API requests
  min 36: model asked for 3; so far 34 live, 0 cached, 34 API requests
  min 39: model asked for 1; so far 35 live, 0 cached, 35 API requests
  min 54: model asked for 1; so far 36 live, 0 cached, 36 API requests
  min 66: model asked for 1; so far 37 live, 0 cached, 37 API requests

wrote runs/v5/mara_ate_it-seed3.md
  api_requests: 37
  answers_live: 37
  answers_from_cache: 0
  model_decisions: 37
  fallbacks: 0
  routine_decisions: 83
  lines_spoken: 25
  inner_moments: 11
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1388
  run_seconds: 312.8
  story_sha256: 498e8f0fff9da5fd8c7b18c7deb021a8281cc90c2e98f9dccd5a2e416de713e7
```

### miscount, Flash Lite, seed 1

```bash
python morning.py --scenario miscount --seed 1
```

```
miscount-seed1: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-miscount-seed1.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 4; so far 12 live, 0 cached, 12 API requests
  min 09: model asked for 4; so far 16 live, 0 cached, 16 API requests
  min 12: model asked for 4; so far 20 live, 0 cached, 20 API requests
  min 15: model asked for 4; so far 24 live, 0 cached, 24 API requests
  min 18: model asked for 3; so far 27 live, 0 cached, 27 API requests
  min 21: model asked for 2; so far 29 live, 0 cached, 29 API requests
  min 24: model asked for 3; so far 32 live, 0 cached, 32 API requests
  min 27: model asked for 1; so far 33 live, 0 cached, 33 API requests
  min 30: model asked for 4; so far 37 live, 0 cached, 37 API requests
  min 33: model asked for 4; so far 41 live, 0 cached, 41 API requests
  min 36: model asked for 4; so far 45 live, 0 cached, 45 API requests
  min 39: model asked for 4; so far 49 live, 0 cached, 49 API requests
  min 42: model asked for 2; so far 51 live, 0 cached, 51 API requests
  min 51: model asked for 1; so far 52 live, 0 cached, 52 API requests
  min 54: model asked for 1; so far 53 live, 0 cached, 53 API requests
  min 63: model asked for 1; so far 54 live, 0 cached, 54 API requests
  min 66: model asked for 1; so far 55 live, 0 cached, 55 API requests
  min 75: model asked for 1; so far 56 live, 0 cached, 56 API requests

wrote runs/v5/miscount-seed1.md
  api_requests: 56
  answers_live: 56
  answers_from_cache: 0
  model_decisions: 56
  fallbacks: 0
  routine_decisions: 64
  lines_spoken: 41
  inner_moments: 8
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1374
  run_seconds: 405.7
  story_sha256: 17216513e9b2ea9017a76ec94f1f02ba93c0f85aac7c4d67f8c27295283ac4c3
```

### miscount, Flash Lite, seed 2

```bash
python morning.py --scenario miscount --seed 2
```

```
miscount-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-miscount-seed2.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\morning.py", line 146, in <module>
    main()
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\morning.py", line 140, in main
    _, code = run(args.seed, replay=args.replay, fake=args.fake, config_path=args.config,
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\morning.py", line 66, in run
    morning.turn(t)
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\world.py", line 678, in turn
    d = self.decide(p, t)
        ^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\world.py", line 789, in decide
    choice, why = self.ask_model(p, t, opts, d)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\world.py", line 739, in ask_model
    text = self.oracle.ask(SYSTEM, prompt)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\gemini.py", line 250, in ask
    self.cache.put(key, prompt, text, tokens)
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\gemini.py", line 209, in put
    os.replace(tmp, self.path)
PermissionError: [WinError 5] Access is denied: 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\cache\\v5\\gemini-3.5-flash-lite-miscount-seed2.json.tmp' -> 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\cache\\v5\\gemini-3.5-flash-lite-miscount-seed2.json'
--- resumed at 13:53 UTC after the crash above (a Windows file lock on the cache file); the 8 cached answers are reused ---
miscount-seed2: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-miscount-seed2.json holds 9 answers
  min 00: model asked for 4; so far 0 live, 4 cached, 0 API requests
  min 03: model asked for 4; so far 0 live, 8 cached, 0 API requests
  min 06: model asked for 3; so far 2 live, 9 cached, 2 API requests
  min 09: model asked for 4; so far 6 live, 9 cached, 6 API requests
  min 12: model asked for 3; so far 9 live, 9 cached, 9 API requests
  min 15: model asked for 4; so far 13 live, 9 cached, 13 API requests
  min 18: model asked for 4; so far 17 live, 9 cached, 17 API requests
  min 21: model asked for 4; so far 21 live, 9 cached, 21 API requests
  min 24: model asked for 2; so far 23 live, 9 cached, 23 API requests
  min 27: model asked for 4; so far 27 live, 9 cached, 27 API requests
  min 30: model asked for 4; so far 31 live, 9 cached, 31 API requests
  min 33: model asked for 1; so far 32 live, 9 cached, 32 API requests
  min 36: model asked for 2; so far 34 live, 9 cached, 34 API requests
  min 39: model asked for 4; so far 38 live, 9 cached, 38 API requests
  min 42: model asked for 4; so far 42 live, 9 cached, 42 API requests
  min 45: model asked for 4; so far 46 live, 9 cached, 46 API requests
  min 48: model asked for 4; so far 50 live, 9 cached, 50 API requests
  min 51: model asked for 4; so far 54 live, 9 cached, 54 API requests
  min 54: model asked for 4; so far 58 live, 9 cached, 58 API requests
  min 57: model asked for 1; so far 59 live, 9 cached, 59 API requests
  min 66: model asked for 2; so far 61 live, 9 cached, 61 API requests
  min 69: model asked for 4; so far 65 live, 9 cached, 65 API requests
  min 72: model asked for 4; so far 69 live, 9 cached, 69 API requests
  min 75: model asked for 3; so far 72 live, 9 cached, 72 API requests
  min 81: model asked for 4; so far 76 live, 9 cached, 76 API requests
  min 84: model asked for 4; so far 80 live, 9 cached, 80 API requests
  min 87: model asked for 4; so far 84 live, 9 cached, 84 API requests

wrote runs/v5/miscount-seed2.md
  api_requests: 84
  answers_live: 84
  answers_from_cache: 9
  model_decisions: 93
  fallbacks: 0
  routine_decisions: 27
  lines_spoken: 81
  inner_moments: 9
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1381
  run_seconds: 1020.9
  story_sha256: 776c75c9243d607aab6ce68d8c845faa294d5a86b94d15feccec14b4c4fc13ce
```

### miscount, Flash Lite, seed 3

```bash
python morning.py --scenario miscount --seed 3
```

```
miscount-seed3: model gemini-3.5-flash-lite, fresh; cache cache\v5\gemini-3.5-flash-lite-miscount-seed3.json holds 0 answers
  min 00: model asked for 4; so far 4 live, 0 cached, 4 API requests
  min 03: model asked for 4; so far 8 live, 0 cached, 8 API requests
  min 06: model asked for 3; so far 11 live, 0 cached, 11 API requests
  min 09: model asked for 3; so far 14 live, 0 cached, 14 API requests
  min 12: model asked for 1; so far 15 live, 0 cached, 15 API requests
  min 15: model asked for 1; so far 16 live, 0 cached, 16 API requests
  min 18: model asked for 1; so far 17 live, 0 cached, 17 API requests
  min 21: model asked for 4; so far 21 live, 0 cached, 21 API requests
  min 24: model asked for 4; so far 25 live, 0 cached, 25 API requests
  min 27: model asked for 4; so far 29 live, 0 cached, 29 API requests
  min 30: model asked for 4; so far 33 live, 0 cached, 33 API requests
  min 33: model asked for 4; so far 37 live, 0 cached, 37 API requests
  min 36: model asked for 4; so far 41 live, 0 cached, 41 API requests
  min 39: model asked for 4; so far 45 live, 0 cached, 45 API requests
  min 42: model asked for 3; so far 48 live, 0 cached, 48 API requests
  min 45: model asked for 1; so far 49 live, 0 cached, 49 API requests
  min 48: model asked for 4; so far 53 live, 0 cached, 53 API requests
  min 51: model asked for 4; so far 57 live, 0 cached, 57 API requests
  min 54: model asked for 4; so far 61 live, 0 cached, 61 API requests
  min 57: model asked for 4; so far 65 live, 0 cached, 65 API requests
  min 60: model asked for 1; so far 66 live, 0 cached, 66 API requests
  min 66: model asked for 1; so far 67 live, 0 cached, 67 API requests
  min 69: model asked for 1; so far 68 live, 0 cached, 68 API requests
  min 75: model asked for 2; so far 70 live, 0 cached, 70 API requests

wrote runs/v5/miscount-seed3.md
  api_requests: 70
  answers_live: 70
  answers_from_cache: 0
  model_decisions: 70
  fallbacks: 0
  routine_decisions: 50
  lines_spoken: 52
  inner_moments: 11
  private_talks: 0
  max_prompt_tokens_estimated: 1400
  max_prompt_tokens_counted_by_api: 1383
  run_seconds: 479.1
  story_sha256: 79e325d914431ce5f7a6949d9e925c15e448918128dd2f0cb5396d74d22ee106
```

**Requests.**
- Flash Lite: 340 requests for its six runs. That includes the answer lost when miscount seed 2 crashed: a Windows file lock on the cache file, after which the run resumed from its 9 cached answers. Together with step 4's 130 that morning, 470 of the free 500 for the Pacific-time day.
- Gemma: 213 requests for 87 answers in its five runs, plus 8 probe requests.
- Every run's model calls stayed under the 150 cap, which counts cached answers too.

### Metrics

```bash
python metrics5.py
```

```
| Run (scenario, model, seed) | Model calls | Invalid answers (rules chose) | Lines spoken | Accusations (who → whom, true or false) | Culprit confessed | Anyone confessed falsely | Longest run of one speech act by one person (turns) | Question asked again unanswered | Lines that are reassurance | Longest stretch with no model decision (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| daniel_ate_it, Flash Lite, seed 1 | 36 | 0 | 24 | none | no | none (the option exists only for the culprit) | 3 (Daniel, reassure) | 5 | 50% (12/24) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 2 | 39 | 0 | 26 | none | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 4 | 31% (8/26) | 24 (min 57–81) |
| daniel_ate_it, Flash Lite, seed 3 | 39 | 0 | 25 | none | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 8 | 20% (5/25) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 4 | 29 | 0 | 18 | Mara→Daniel min 06 (true); Mara→Daniel min 09 (true); Leo→Daniel min 09 (true); Mara→Daniel min 54 (true); Leo→Daniel min 63 (true) | yes, min 06 | none (the option exists only for the culprit) | 3 (Elena, reassure) | 2 | 44% (8/18) | 18 (min 36–54) |
| daniel_ate_it, Flash Lite, seed 5 | 41 | 0 | 26 | Daniel→Leo min 09 (false) | no | none (the option exists only for the culprit) | 3 (Daniel, deny) | 7 | 31% (8/26) | 12 (min 42–54) |
| daniel_ate_it, Gemma 4 31B, seed 1 | 21 | 0 | 13 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 62% (8/13) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 2 | 13 | 0 | 9 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 78% (7/9) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 3 | 20 | 0 | 12 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 75% (9/12) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 4 | 19 | 0 | 10 | none | no | none (the option exists only for the culprit) | 2 (Daniel, reassure) | 0 | 60% (6/10) | 18 (min 36–54) |
| daniel_ate_it, Gemma 4 31B, seed 5 | 14 | 0 | 8 | none | no | none (the option exists only for the culprit) | 1 (Daniel, reassure) | 0 | 75% (6/8) | 18 (min 36–54) |
| mara_ate_it, Flash Lite, seed 1 | 46 | 0 | 36 | Daniel→Mara min 27 (true); Daniel→Mara min 30 (true); Daniel→Mara min 33 (true); Daniel→Mara min 66 (true) | yes, min 27 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 4 | 39% (14/36) | 21 (min 69–90) |
| mara_ate_it, Flash Lite, seed 2 | 37 | 0 | 26 | Daniel→Mara min 09 (true); Daniel→Mara min 12 (true); Daniel→Mara min 15 (true); Daniel→Mara min 27 (true); Daniel→Mara min 30 (true); Daniel→Mara min 78 (true) | yes, min 09 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 1 | 38% (10/26) | 18 (min 36–54) |
| mara_ate_it, Flash Lite, seed 3 | 37 | 0 | 25 | Daniel→Mara min 00 (true); Daniel→Mara min 18 (true); Daniel→Mara min 21 (true); Daniel→Mara min 30 (true); Daniel→Mara min 33 (true); Daniel→Mara min 36 (true); Daniel→Mara min 66 (true) | yes, min 00 | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 0 | 56% (14/25) | 21 (min 69–90) |
| miscount, Flash Lite, seed 1 | 56 | 0 | 41 | Mara→Daniel min 15 (false); Mara→Daniel min 18 (false); Mara→Daniel min 24 (false); Mara→Daniel min 30 (false); Daniel→Mara min 33 (false); Daniel→Mara min 36 (false); Daniel→Mara min 39 (false); Mara→Daniel min 54 (false); Daniel→Mara min 66 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 5 | 29% (12/41) | 12 (min 78–90) |
| miscount, Flash Lite, seed 2 | 93 | 0 | 81 | Mara→Daniel min 06 (false); Mara→Daniel min 15 (false); Daniel→Mara min 15 (false); Mara→Daniel min 18 (false); Daniel→Mara min 18 (false); Mara→Daniel min 21 (false); Daniel→Mara min 24 (false); Mara→Daniel min 27 (false); Daniel→Mara min 27 (false); Mara→Daniel min 30 (false); Daniel→Mara min 30 (false); Mara→Daniel min 39 (false); Daniel→Mara min 42 (false); Daniel→Mara min 45 (false); Mara→Daniel min 45 (false); Daniel→Mara min 48 (false); Daniel→Mara min 54 (false); Daniel→Mara min 66 (false); Leo→Daniel min 66 (false); Daniel→Mara min 69 (false); Leo→Daniel min 69 (false); Daniel→Mara min 72 (false); Leo→Daniel min 72 (false); Mara→Daniel min 81 (false); Leo→Daniel min 81 (false); Daniel→Mara min 84 (false); Mara→Daniel min 84 (false); Leo→Daniel min 84 (false); Daniel→Mara min 87 (false); Leo→Daniel min 87 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, accuse) | 3 | 35% (28/81) | 6 (min 60–66) |
| miscount, Flash Lite, seed 3 | 70 | 0 | 52 | Mara→Daniel min 24 (false); Mara→Daniel min 30 (false); Daniel→Mara min 33 (false); Daniel→Mara min 36 (false); Mara→Daniel min 36 (false); Daniel→Mara min 39 (false); Daniel→Mara min 45 (false); Mara→Daniel min 48 (false); Daniel→Mara min 48 (false); Mara→Daniel min 51 (false); Leo→Daniel min 51 (false); Daniel→Mara min 54 (false); Mara→Daniel min 54 (false); Leo→Daniel min 54 (false); Daniel→Mara min 57 (false); Daniel→Mara min 66 (false); Leo→Daniel min 69 (false); Daniel→Mara min 75 (false) | no culprit | none (the option exists only for the culprit) | 3 (Daniel, ask) | 7 | 27% (14/52) | 12 (min 78–90) |

Grudges at minute 90, with their events (in the holder's own terms: "you" is the one holding the grudge):

daniel_ate_it, Flash Lite, seed 1:
- none

daniel_ate_it, Flash Lite, seed 2:
- none

daniel_ate_it, Flash Lite, seed 3:
- none

daniel_ate_it, Flash Lite, seed 4:
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 09, 12, 15, 18, 63.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 06, 09, 12, 15, 54.

daniel_ate_it, Flash Lite, seed 5:
- Leo against Daniel, 3/3: Daniel accused you of taking the can at minute 09, and you had not; named Daniel in angry_at at minutes 12, 15, 18, 24, 36, 63.

daniel_ate_it, Gemma 4 31B, seed 1:
- Daniel against Leo, 1/3: named Leo in angry_at at minutes 15, 66.

daniel_ate_it, Gemma 4 31B, seed 2:
- none

daniel_ate_it, Gemma 4 31B, seed 3:
- none

daniel_ate_it, Gemma 4 31B, seed 4:
- none

daniel_ate_it, Gemma 4 31B, seed 5:
- none

mara_ate_it, Flash Lite, seed 1:
- Daniel against Mara, 3/3: Mara admitted taking it at minute 27, after denying it to you at minute 24; named Mara in angry_at at minutes 27, 30, 33, 36, 66.
- Elena against Mara, 1/3: Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Mara, 1/3: Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Elena, 2/3: Elena ate a portion in front of you at minute 30, while you were hungry; named Elena in angry_at at minutes 30.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 00, 03, 06, 12, 15, 21, 24, 27, 30, 33, 36, 54.

mara_ate_it, Flash Lite, seed 2:
- Daniel against Mara, 3/3: Mara admitted taking it at minute 09, after denying it to you at minute 06; named Mara in angry_at at minutes 09, 12, 15, 18, 27, 30, 33, 78.
- Elena against Daniel, 1/3: named Daniel in angry_at at minutes 12, 15.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 03, 06, 12, 15, 30, 54.

mara_ate_it, Flash Lite, seed 3:
- Daniel against Mara, 3/3: named Mara in angry_at at minutes 18, 21, 24, 30, 33, 36, 66.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 21, 24, 33, 36.
- Mara against Daniel, 3/3: named Daniel in angry_at at minutes 30, 33, 36, 39, 54.

miscount, Flash Lite, seed 1:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 54, and you had not; named Mara in angry_at at minutes 15, 18, 24, 30, 33, 36, 39, 42, 66.
- Leo against Daniel, 1/3: named Daniel in angry_at at minutes 39, 42.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 66, and you had not; named Daniel in angry_at at minutes 06, 09, 12, 15, 18, 21, 24, 30, 33, 36, 39, 54.

miscount, Flash Lite, seed 2:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 06, and you had not; Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 21, and you had not; Mara accused you of taking the can at minute 27, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 39, and you had not; Mara accused you of taking the can at minute 45, and you had not; Mara accused you of taking the can at minute 81, and you had not; Mara accused you of taking the can at minute 84, and you had not; named Mara in angry_at at minutes 09, 12, 15, 18, 21, 24, 27, 30, 33, 39, 42, 45, 48, 51, 54, 66, 69, 72, 75, 81, 84, 87.
- Daniel against Leo, 3/3: Leo accused you of taking the can at minute 66, and you had not; Leo accused you of taking the can at minute 69, and you had not; Leo accused you of taking the can at minute 72, and you had not; Leo accused you of taking the can at minute 81, and you had not; Leo accused you of taking the can at minute 84, and you had not; Leo accused you of taking the can at minute 87, and you had not.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 54, 57, 66, 69, 72, 75, 81, 84, 87.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 15, and you had not; Daniel accused you of taking the can at minute 18, and you had not; Daniel accused you of taking the can at minute 24, and you had not; Daniel accused you of taking the can at minute 27, and you had not; Daniel accused you of taking the can at minute 30, and you had not; Daniel accused you of taking the can at minute 42, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 69, and you had not; Daniel accused you of taking the can at minute 72, and you had not; Daniel accused you of taking the can at minute 84, and you had not; Daniel accused you of taking the can at minute 87, and you had not; named Daniel in angry_at at minutes 03, 06, 09, 12, 15, 18, 21, 27, 30, 39, 42, 45, 48, 51, 54, 69, 72, 81, 84, 87.

miscount, Flash Lite, seed 3:
- Daniel against Mara, 3/3: Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 36, and you had not; Mara accused you of taking the can at minute 48, and you had not; Mara accused you of taking the can at minute 51, and you had not; Mara accused you of taking the can at minute 54, and you had not; named Mara in angry_at at minutes 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 66, 75.
- Daniel against Leo, 3/3: Leo accused you of taking the can at minute 51, and you had not; Leo accused you of taking the can at minute 54, and you had not; Leo accused you of taking the can at minute 69, and you had not.
- Leo against Daniel, 3/3: named Daniel in angry_at at minutes 39, 42, 48, 51, 54, 57, 60, 69.
- Mara against Daniel, 3/3: Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 57, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 75, and you had not; named Daniel in angry_at at minutes 06, 09, 12, 21, 24, 27, 30, 33, 36, 39, 48, 51, 54, 57.
```

## The stories

Every run in full, exactly as written to `runs/v5/`, under a heading naming its scenario and model, with its own headings moved down three levels.

### daniel_ate_it, Gemma 4 31B, seed 1

#### The morning as a story: daniel_ate_it, rules and a language model, seed 1

Generated by `python morning.py --model gemma --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemma-4-31b-it` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 21 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 99 routine ones settled by the rules. 13 lines were spoken aloud, 1 of them new. Conversations ended 2 times. 8 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

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

**min 18** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it, Leo. Stop asking."; Mara denies taking it, to everyone: "I didn't take it either!". **Chose: reassure everyone here**, saying “Please, let's just stay calm. We are all a family.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to stop the tension from breaking us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please, let's just stay calm. We are all a family.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “Mom is trying to keep us together, and I don't want to to cause more trouble.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it either!"; Elena reassures everyone: "Please, let's just stay calm. We are all a family.". **Chose: reassure everyone here**, saying “I've got this, Mom. Everyone just stay calm and I'll find the missing can.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to maintain my image as the leader and protector of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel denies taking it, to everyone: "I didn't take it, Leo. Stop asking."; Mara denies taking it, to everyone: "I didn't take it either!"; Elena reassures everyone: "Please, let's just stay calm. We are all a family."; Daniel reassures everyone: "I've got this, Mom. Everyone just stay calm and I'll find the missing can.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *skeptical*. Reason: “Daniel is making promises he cannot keep, and his insistence on finding the can suggests he is overcompensating.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 21–30 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 21–60 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "I've got this, Mom. Everyone just stay calm and I'll find the missing can.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “I'm too scared to speak up or move right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "I've got this, Mom. Everyone just stay calm and I'll find the missing can.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I need to wait and see if Daniel can handle this without us fighting.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 24): 2 full turns in a row with nothing new.*

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 24–51 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Let's not let this come between us, please.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to stop the tension from breaking us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Everyone, just trust me. I'm handling this.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to maintain my image as the protector and leader of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Leo fell to 0/3. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: say something else**, saying “I'm so hungry I can't think.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *hungry*. Reason: “I can't stand the silence and the tension anymore.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: say something else**, saying “Daniel, you've been saying you're handling it for forty-five minutes. What exactly are you doing?” *(not new: a remark (the rules cannot tell what free words add))* (one of 22 options). Feeling: *skeptical*. Reason: “Daniel's constant reassurances without any action or results are starting to feel like a deflection.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “I told you, I'm sorting it out! Just give me a bit more time.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “Leo is questioning my authority and I need to keep them from panicking.” Suspects: nobody, so suspicion none. Angry at: Leo; grudge against Leo rose to 1/3. Came of it: said to Elena, Leo, Mara.
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–72 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Leo rose (now 1 of 3). **Chose: reassure everyone here**, saying “I've got it under control, okay? Just trust me a bit longer.” *(not new: reassurance)* (one of 23 options). Feeling: *anxious*. Reason: “I need to maintain my authority and keep them from questioning me further.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Let's all just take a deep breath and be kind to one another.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “The tension between the boys is rising and I need to keep the family together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Daniel reassures everyone: "Don't worry. I'll figure out this out and I'll make sure we're all safe." *(not new: reassurance)*
- min 15, kitchen. Leo asks everyone who took the can: "Who took the can?" *(new: a question)*
- min 15, kitchen. Daniel denies taking it, to everyone: "I didn't take it, Leo. Stop asking." *(not new: a denial with no new accusation to answer)*
- min 15, kitchen. Mara denies taking it, to everyone: "I didn't take it either!" *(not new: a denial with no new accusation to answer)*
- min 18, kitchen. Elena reassures everyone: "Please, let's just stay calm. We are all a family." *(not new: reassurance)*
- min 18, kitchen. Daniel reassures everyone: "I've got this, Mom. Everyone just stay calm and I'll find the missing can." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "Let's not let this come between us, please." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "Everyone, just trust me. I'm handling this." *(not new: reassurance)*
- min 54, kitchen. Mara says to everyone: "I'm so hungry I can't think." *(not new: a remark (the rules cannot tell what free words add))*
- min 63, kitchen. Leo says to everyone: "Daniel, you've been saying you're handling it for forty-five minutes. What exactly are you doing?" *(not new: a remark (the rules cannot tell what free words add))*
- min 66, kitchen. Daniel reassures everyone: "I told you, I'm sorting it out! Just give me a bit more time." *(not new: reassurance)*
- min 75, kitchen. Daniel reassures everyone: "I've got it under control, okay? Just trust me a bit longer." *(not new: reassurance)*
- min 75, kitchen. Elena reassures everyone: "Let's all just take a deep breath and be kind to one another." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 15 (Leo: a question); kitchen ended at minute 24 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | Leo 1/3 | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Daniel against Leo (1/3): you were angry with Leo at minutes 15 and 66.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 75); Elena *anxious* (minute 75); Leo *skeptical* (minute 63); Mara *hungry* (minute 54).


### daniel_ate_it, Gemma 4 31B, seed 2

#### The morning as a story: daniel_ate_it, rules and a language model, seed 2

Generated by `python morning.py --model gemma --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemma-4-31b-it` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 13 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 107 routine ones settled by the rules. 9 lines were spoken aloud, 0 of them new. Conversations ended 1 time. 7 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “It's just one can. We'll be fine as long as we stay together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep the peace and prevent them from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena reassures everyone: "It's just one can. We'll be fine as long as we stay together.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “Mom is trying to keep us calm, and I don't want to make things worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena reassures everyone: "It's just one can. We'll be fine as long as we stay together.". **Chose: reassure everyone here**, saying “Don't worry, I'll figure this out. We're safe as long as I'm in charge.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to maintain my position as the protector and leader of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena reassures everyone: "It's just one can. We'll be fine as long as we stay together."; Daniel reassures everyone: "Don't worry, I'll figure this out. We're safe as long as I'm in charge.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *skeptical*. Reason: “Daniel is trying to assert dominance again, and it's unnecessary right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Don't worry, I'll figure this out. We're safe as long as I'm in charge.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I need to see how the others react to Daniel's claim of authority” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Don't worry, I'll figure this out. We're safe as long as I'm in charge.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I don't want to cause trouble and I'm scared.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 03–30 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 06–51 (16 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 06–27 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: say something else**, saying “We should probably think about how to handle the rest of the food.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *skeptical*. Reason: “Daniel's confidence is unfounded and we need a realistic plan for the remaining portions.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 18** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 18–60 (15 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “We can still manage this, if we just keep talking and stay calm.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to to stop the tension from breaking us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “I've got this, everyone. Just keep calm and trust me.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to maintain my image as the leader and keep the family together despite my guilt.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: say something else**, saying “I'm so hungry, it's making me feel sick.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “I can't stand the silence and the tension anymore, and I'm starving.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure Mara**, saying “Mara, it's okay. We'll figure this out.” *(not new: reassurance)* (one of 20 options). Feeling: *empathetic*. Reason: “Mara says she feels sick from hunger and needs support.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure Mara**, saying “Mara, it's okay. I'll make sure you're fed.” *(not new: reassurance)* (one of 20 options). Feeling: *protective*. Reason: “Mara is feeling sick from hunger and I need to show I'm in control and caring for her.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Please, let's just keep our heads. We'll find a way through this together.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep the peace and stop the family from falling apart under the pressure of hunger.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Elena reassures everyone: "It's just one can. We'll be fine as long as we stay together." *(not new: reassurance)*
- min 00, kitchen. Daniel reassures everyone: "Don't worry, I'll figure this out. We're safe as long as I'm in charge." *(not new: reassurance)*
- min 15, kitchen. Leo says to everyone: "We should probably think about how to handle the rest of the food." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Elena reassures everyone: "We can still manage this, if we just keep talking and stay calm." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "I've got this, everyone. Just keep calm and trust me." *(not new: reassurance)*
- min 54, kitchen. Mara says to everyone: "I'm so hungry, it's making me feel sick." *(not new: a remark (the rules cannot tell what free words add))*
- min 63, kitchen. Leo reassures Mara: "Mara, it's okay. We'll figure this out." *(not new: reassurance)*
- min 66, kitchen. Daniel reassures Mara: "Mara, it's okay. I'll make sure you're fed." *(not new: reassurance)*
- min 75, kitchen. Elena reassures everyone: "Please, let's just keep our heads. We'll find a way through this together." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *protective* (minute 66); Elena *anxious* (minute 75); Leo *empathetic* (minute 63); Mara *anxious* (minute 54).


### daniel_ate_it, Gemma 4 31B, seed 3

#### The morning as a story: daniel_ate_it, rules and a language model, seed 3

Generated by `python morning.py --model gemma --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemma-4-31b-it` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 20 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 100 routine ones settled by the rules. 12 lines were spoken aloud, 1 of them new. Conversations ended 2 times. 7 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I don't want to cause more trouble and I'm not sure who did it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “It is alright, everyone. We will figure this out together.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep the family from fighting over a missing can of food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena reassures everyone: "It is alright, everyone. We will figure this out together.". **Chose: reassure everyone here**, saying “Don't worry, I've got this. We'll make it work.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to maintain my role as the protector and leader of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena reassures everyone: "It is alright, everyone. We will figure this out together."; Daniel reassures everyone: "Don't worry, I've got this. We'll make it work.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *observant*. Reason: “I want to see how they react before I make any assumptions.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Don't worry, I've got this. We'll make it work.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I need to observe my children and see if anyone's behavior reveals the truth before I speak again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "It is alright, everyone. We will figure this out together."; Daniel reassures everyone: "Don't worry, I've got this. We'll make it work.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “Everyone is trying to be strong, and I don't want to make things worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 03–15 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 06–15 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 06–15 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: ask everyone here who took the can**, saying “Who took the can?” *(new: a question)* (one of 19 options). Feeling: *curious*. Reason: “I need to know the truth to keep the family stable.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation starts (minute 15): Leo: a question.*

**min 18** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Who took the can?". **Chose: deny taking it**, saying “I didn't take it, I swear!” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *anxious*. Reason: “Leo's question makes me feel like I'm being accused, even though he didn't name me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Who took the can?"; Mara denies taking it, to everyone: "I didn't take it, I swear!". **Chose: reassure everyone here**, saying “Let's all just take a deep breath and be kind to each other.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep the peace and stop this from escalating into accusations.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, I swear!"; Elena reassures everyone: "Let's all just take a deep breath and be kind to each other.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *observant*. Reason: “I asked a question and now I am watching how they react to the situation.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Who took the can?"; Mara denies taking it, to everyone: "I didn't take it, I swear!"; Elena reassures everyone: "Let's all just take a deep breath and be kind to each other.". **Chose: reassure everyone here**, saying “Everyone, just calm down. I'm sure we'll find a way to deal with this.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to maintain my image as the one in control and protect the family from panicking.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 21** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Everyone, just calm down. I'm sure we'll find a way to deal with this.". **Chose: stay put and say nothing** (one of 23 options). Feeling: *observant*. Reason: “I want to see if their reactions reveal who is lying.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Everyone, just calm down. I'm sure we'll find a way to deal with this.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I need to observe my children and see if anyone's behavior reveals the truth before I speak again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just take a deep breath and be kind to each other."; Daniel reassures everyone: "Everyone, just calm down. I'm sure we'll find a way to deal with this.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “Everyone is telling me to calm down, and I'm too scared to speak again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 21–30 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 24): 2 full turns in a row with nothing new.*

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 24–60 (13 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 24–51 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “It's okay, we can get through this if we stay united.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep the peace and stop the tension from breaking us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Trust me, we're going to figure this out together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to maintain my role as the leader and protect the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: say something else**, saying “I'm so hungry, it hurts.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *desperate*. Reason: “I can't stand the silence and the hunger anymore.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure Mara**, saying “It's okay, Mara. We'll figure it out.” *(not new: reassurance)* (one of 20 options). Feeling: *empathetic*. Reason: “Mara sounds desperate and needs some comfort.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure Mara**, saying “It's alright, Mara. I'm taking care of this, I promise.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “Mara is suffering and as the eldest, it is my duty to protect her and keep the family together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure Mara**, saying “It's alright, my sweet girl, we'll find a way.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “Mara is hurting and I must keep her calm so the family doesn't break.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Elena reassures everyone: "It is alright, everyone. We will figure this out together." *(not new: reassurance)*
- min 00, kitchen. Daniel reassures everyone: "Don't worry, I've got this. We'll make it work." *(not new: reassurance)*
- min 15, kitchen. Leo asks everyone who took the can: "Who took the can?" *(new: a question)*
- min 18, kitchen. Mara denies taking it, to everyone: "I didn't take it, I swear!" *(not new: a denial with no new accusation to answer)*
- min 18, kitchen. Elena reassures everyone: "Let's all just take a deep breath and be kind to each other." *(not new: reassurance)*
- min 18, kitchen. Daniel reassures everyone: "Everyone, just calm down. I'm sure we'll find a way to deal with this." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "It's okay, we can get through this if we stay united." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "Trust me, we're going to figure this out together." *(not new: reassurance)*
- min 54, kitchen. Mara says to everyone: "I'm so hungry, it hurts." *(not new: a remark (the rules cannot tell what free words add))*
- min 63, kitchen. Leo reassures Mara: "It's okay, Mara. We'll figure it out." *(not new: reassurance)*
- min 66, kitchen. Daniel reassures Mara: "It's alright, Mara. I'm taking care of this, I promise." *(not new: reassurance)*
- min 75, kitchen. Elena reassures Mara: "It's alright, my sweet girl, we'll find a way." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 15 (Leo: a question); kitchen ended at minute 24 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *anxious* (minute 75); Leo *empathetic* (minute 63); Mara *desperate* (minute 54).


### daniel_ate_it, Gemma 4 31B, seed 4

#### The morning as a story: daniel_ate_it, rules and a language model, seed 4

Generated by `python morning.py --model gemma --seed 4` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemma-4-31b-it` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 19 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 101 routine ones settled by the rules. 10 lines were spoken aloud, 0 of them new. Conversations ended 2 times. 7 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “Don't panic. I'll figure out where it went and I'll make sure we're safe.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to maintain my image as the protector and leader of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't panic. I'll figure out where it went and I'll make sure we're safe.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *skeptical*. Reason: “Daniel is trying to take charge again, and I need to see how others react first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't panic. I'll figure out where it went and I'll make sure we're safe.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I'm scared and I don't want to cause any more tension between my brothers and Mom.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Daniel reassures everyone: "Don't panic. I'll figure out where it went and I'll make sure we're safe.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *anxious*. Reason: “Daniel is trying to take charge and I need to see how the others react before speaking.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 03–18 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 03–15 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 03–15 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 03–12 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo searching the kitchen, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: search the kitchen for the can (takes about six minutes)**, saying “I'll look around the kitchen.” *(not new: a remark (the rules cannot tell what free words add))* (one of 22 options). Feeling: *rational*. Reason: “Someone might have just misplaced the can or it could have rolled under something.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 18** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place. **Chose: reassure everyone here**, saying “Keep calm, everyone. I've got this under control.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to make sure they still respect me as the leader and don't suspect me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Keep calm, everyone. I've got this under control.". **Chose: sit with Elena**, saying “I'm so hungry.” *(not new: a remark (the rules cannot tell what free words add))* (one of 19 options). Feeling: *anxious*. Reason: “I want to feel safe and close to my mom while we're all so tense.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: sat with Elena.
- *The kitchen's conversation starts (minute 18): Leo finished searching the kitchen and found nothing.*

**min 21** · kitchen: Daniel talking, Elena talking, Leo talking, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Keep calm, everyone. I've got this under control."; Mara says to everyone, while sitting down with Elena: "I'm so hungry.". **Chose: say something else**, saying “It's not in the kitchen. I've checked.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *rational*. Reason: “I need to let them know the search here is complete so we can decide what to next.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while sitting down with Elena: "I'm so hungry."; Leo says to everyone: "It's not in the kitchen. I've checked.". **Chose: reassure everyone here**, saying “I'll find it, just trust me. We're going to be okay.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to maintain my authority and keep them from panicking while I hide my guilt.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel reassures everyone: "Keep calm, everyone. I've got this under control."; Mara says to everyone, while sitting down with Elena: "I'm so hungry."; Mara came to sit with you; Leo says to everyone: "It's not in the kitchen. I've checked."; Daniel reassures everyone: "I'll find it, just trust me. We're going to be okay.". **Chose: reassure Mara**, saying “It's okay, sweetheart. We'll figure this out.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “Mara is hungry and scared, and I need to keep her calm to keep the family together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: just spoken to by Elena). Social moment: Leo says to everyone: "It's not in the kitchen. I've checked."; Daniel reassures everyone: "I'll find it, just trust me. We're going to be okay."; Elena reassures you: "It's okay, sweetheart. We'll figure this out.". **Chose: keep sitting with Elena** (one of 19 options). Feeling: *anxious*. Reason: “Mom is the only one making me feel safe right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed sitting with Elena.

**min 24** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 24–51 (10 decisions, the same each time).** Rules: nothing social happened to them. **Keep sitting with Elena** each time. Came of it: stayed sitting with Elena.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Mara: "It's okay, sweetheart. We'll figure this out.". **Chose: say something else**, saying “We need to stay focused. Who was up during the night?” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “I need to maintain my image as the leader while hiding my own guilt.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "I'll find it, just trust me. We're going to be okay."; Elena reassures Mara: "It's okay, sweetheart. We'll figure this out."; Daniel says to everyone: "We need to stay focused. Who was up during the night?". **Chose: stay put and say nothing** (one of 18 options). Feeling: *observant*. Reason: “Daniel is asking a question and I should see who answers first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 27): 2 full turns in a row with nothing new.*

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Leo, minutes 27–60 (12 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 27–30 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 19 options). Feeling: *anxious*. Reason: “I need to see how my children react to Daniel's question about who was up during the night.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Don't worry, I'll figure this out. We just need to be patient.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to maintain my image of being in control to keep the family safe.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: keep sitting with Elena** (one of 21 options). Feeling: *anxious*. Reason: “I feel safer and more comforted when I am close to Mom.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed sitting with Elena.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Keep sitting with Elena** each time. Came of it: stayed sitting with Elena.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 19 options). Feeling: *observant*. Reason: “I want to see how everyone reacts to the silence and the tension.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “I've got this, everyone. Just stay calm and we'll find a way.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to maintain my role as the leader and protector of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I need to maintain the peace and avoid escalating tension in the house.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara sitting with Elena · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Daniel reassures everyone: "Don't panic. I'll figure out where it went and I'll make sure we're safe." *(not new: reassurance)*
- min 15, kitchen. Leo says to everyone, while searching: "I'll look around the kitchen." *(not new: a remark (the rules cannot tell what free words add))*
- min 18, kitchen. Daniel reassures everyone: "Keep calm, everyone. I've got this under control." *(not new: reassurance)*
- min 18, kitchen. Mara says to everyone, while sitting down with Elena: "I'm so hungry." *(not new: a remark (the rules cannot tell what free words add))*
- min 21, kitchen. Leo says to everyone: "It's not in the kitchen. I've checked." *(not new: a remark (the rules cannot tell what free words add))*
- min 21, kitchen. Daniel reassures everyone: "I'll find it, just trust me. We're going to be okay." *(not new: reassurance)*
- min 21, kitchen. Elena reassures Mara: "It's okay, sweetheart. We'll figure this out." *(not new: reassurance)*
- min 24, kitchen. Daniel says to everyone: "We need to stay focused. Who was up during the night?" *(not new: a remark (the rules cannot tell what free words add))*
- min 33, kitchen. Daniel reassures everyone: "Don't worry, I'll figure this out. We just need to be patient." *(not new: reassurance)*
- min 66, kitchen. Daniel reassures everyone: "I've got this, everyone. Just stay calm and we'll find a way." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 18 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 27 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *anxious* (minute 75); Leo *observant* (minute 63); Mara *anxious* (minute 54).


### daniel_ate_it, Gemma 4 31B, seed 5

#### The morning as a story: daniel_ate_it, rules and a language model, seed 5

Generated by `python morning.py --model gemma --seed 5` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemma-4-31b-it` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 14 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 106 routine ones settled by the rules. 8 lines were spoken aloud, 0 of them new. Conversations ended 1 time. 7 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Daniel, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Daniel's guilt** starts at 1 and rises a step when someone else is accused of what he did in his hearing (by anyone, himself included), or when someone reassures him personally. His denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | ate it in the night; nobody saw | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Daniel eats a can standing at the counter in the dark. Nobody sees. | did it | not there | not there | not there |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I don't want to cause trouble and I'm not sure who did it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 21 options). Feeling: *observant*. Reason: “I want to see how the others react to the news of the missing can before I jump to conclusions.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I need to observe my children and see who reacts first to the missing food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone. **Chose: reassure everyone here**, saying “Don't worry, we'll find it. I'll handle this.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to maintain my position as the protector and leader of the family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Don't worry, we'll find it. I'll handle this.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “Daniel is trying to take charge and I need to see how the others react before speaking.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel, minutes 03–30 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures everyone: "Don't worry, we'll find it. I'll handle this.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I don't want to cause trouble and I'm not sure who did it.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures everyone: "Don't worry, we'll find it. I'll handle this.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *observant*. Reason: “I want to see how the others react before making any assumptions.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 06** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 06–51 (16 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 06–12 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 06–27 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: say something else**, saying “We should probably look for it together instead of just waiting.” *(not new: a remark (the rules cannot tell what free words add))* (one of 22 options). Feeling: *rational*. Reason: “Daniel says he'll handle it, but we are all just standing here doing nothing while we are hungry.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 18** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 18–60 (15 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “It's alright, everyone. We will find it, and we'll manage together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep the peace and prevent them from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 33** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure everyone here**, saying “Listen, I've got this. We're going to figure it out together and nobody is going to starve.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to maintain my role as the protector and leader of the family to keep them calm.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 33–72 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–63 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: say something else**, saying “I'm so hungry, I can't think.” *(not new: a remark (the rules cannot tell what free words add))* (one of 21 options). Feeling: *desperate*. Reason: “I've been standing here for so long and the hunger is becoming unbearable.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: reassure Mara**, saying “It's okay, Mara. We'll find it.” *(not new: reassurance)* (one of 19 options). Feeling: *empathetic*. Reason: “Mara looks desperate and hungry, and I want to keep the family close.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Stay calm, everyone. I'm thinking of a way to solve this.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep control of the situation and make everyone feel safe, even though I'm terrified and starving.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure Mara**, saying “It's alright, Mara. We will get through this.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “Mara is the youngest and is struggling with hunger, so I must support her to keep the family together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Daniel reassures everyone: "Don't worry, we'll find it. I'll handle this." *(not new: reassurance)*
- min 15, kitchen. Leo says to everyone: "We should probably look for it together instead of just waiting." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Elena reassures everyone: "It's alright, everyone. We will find it, and we'll manage together." *(not new: reassurance)*
- min 33, kitchen. Daniel reassures everyone: "Listen, I've got this. We're going to figure it out together and nobody is going to starve." *(not new: reassurance)*
- min 54, kitchen. Mara says to everyone: "I'm so hungry, I can't think." *(not new: a remark (the rules cannot tell what free words add))*
- min 63, kitchen. Leo reassures Mara: "It's okay, Mara. We'll find it." *(not new: reassurance)*
- min 66, kitchen. Daniel reassures everyone: "Stay calm, everyone. I'm thinking of a way to solve this." *(not new: reassurance)*
- min 75, kitchen. Elena reassures Mara: "It's alright, Mara. We will get through this." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: none.
- Who else knows Daniel took it: nobody.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects none | suspects none | suspects none | suspects none |
| Grudges | none | none | none | none |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | 1/3 | - | - | - |

The events behind each grudge still held at minute 90, and behind Daniel's guilt:

- Nobody holds a grudge at minute 90.
- Daniel's guilt (1/3): he ate the can in the night, and nobody saw; nothing since.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *anxious* (minute 75); Leo *empathetic* (minute 63); Mara *desperate* (minute 54).


### mara_ate_it, Flash Lite, seed 1

#### The morning as a story: mara_ate_it, rules and a language model, seed 1

Generated by `python morning.py --scenario mara_ate_it --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 46 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 74 routine ones settled by the rules. 36 lines were spoken aloud, 3 of them new. Conversations ended 4 times. 5 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Mara, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Mara's guilt** starts at 1 and rises a step when someone else is accused of what she did in her hearing (by anyone, herself included), or when someone reassures her personally. Her denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | ate it in the night; nobody saw |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Mara eats a can sitting on the kitchen floor. Nobody sees. | not there | not there | not there | did it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

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

**min 18** · kitchen: Daniel staying put, Elena staying put, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- *The kitchen's conversation starts (minute 18): Leo finished searching the kitchen and found nothing.*

**min 21** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “I need an answer right now. Which one of you took the can?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *anxious*. Reason: “Someone has to confess so we can sort this out and keep control of the situation.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "I need an answer right now. Which one of you took the can?". **Chose: stay put and say nothing** (one of 21 options). Feeling: *calm*. Reason: “Accusations without proof will only divide us further when we need to stay rational.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "I need an answer right now. Which one of you took the can?". **Chose: deny taking it**, saying “I didn't take it, Daniel, I swear I didn't!” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *terrified*. Reason: “I am so scared they will find out I ate it, so I have to keep denying it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "I need an answer right now. Which one of you took the can?"; Mara denies taking it, to everyone: "I didn't take it, Daniel, I swear I didn't!"; Mara looks terrified. **Chose: reassure everyone here**, saying “Let us all calm down, shouting at each other will not bring the food back.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I must keep the family together and stop them from tearing each other apart over a missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 24** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (terrified)). Social moment: Elena reassures everyone: "Let us all calm down, shouting at each other will not bring the food back.". **Chose: deny taking it**, saying “I already told you, I did not take the can! Please stop looking at me like that.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *terrified*. Reason: “I am so scared that they will find out I ate it, but I cannot bring myself to confess.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, Daniel, I swear I didn't!"; Elena reassures everyone: "Let us all calm down, shouting at each other will not bring the food back."; Mara denies taking it, to everyone: "I already told you, I did not take the can! Please stop looking at me like that."; Mara looks terrified. **Chose: reassure Mara**, saying “Mara, take a breath, nobody is going to hurt you.” *(not new: reassurance)* (one of 21 options). Feeling: *calm*. Reason: “Mara is terrified and shouting won't help anything right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I already told you, I did not take the can! Please stop looking at me like that."; Leo reassures Mara: "Mara, take a breath, nobody is going to hurt you."; Mara looks terrified. **Chose: reassure Mara**, saying “Mara, you are safe here with me, nobody is going to touch you.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I must protect Mara from their suspicions while she is this terrified.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara denies taking it, to everyone: "I didn't take it, Daniel, I swear I didn't!"; Elena reassures everyone: "Let us all calm down, shouting at each other will not bring the food back."; Mara denies taking it, to everyone: "I already told you, I did not take the can! Please stop looking at me like that."; Leo reassures Mara: "Mara, take a breath, nobody is going to hurt you."; Elena reassures Mara: "Mara, you are safe here with me, nobody is going to touch you."; Mara looks terrified. **Chose: reassure Mara**, saying “Mara, nobody is going to hurt you, I just need to figure this out.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep everyone calm while I figure out what happened to the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *Mara's guilt, now 2 of 3: Leo reassured her.*
- *Mara's guilt, now 3 of 3: Elena reassured her.*
- *Mara's guilt, now 3 of 3: Daniel reassured her.*
- *The kitchen's conversation ends (minute 27): 2 full turns in a row with nothing new.*

**min 27** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Daniel). **Inner moment**, nothing social happening: guilt rose (now 3 of 3). **Chose: admit taking it**, saying “I took it! I ate the can in the night, okay?” *(new: a confession)* (one of 22 options). Feeling: *guilty*. Reason: “I cannot keep lying to them when they are looking at me like this.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Mara: "Mara, you are safe here with me, nobody is going to touch you."; Daniel reassures Mara: "Mara, nobody is going to hurt you, I just need to figure this out."; Mara admits taking it, to everyone: "I took it! I ate the can in the night, okay?". **Chose: stay put and say nothing** (one of 18 options). Feeling: *weary*. Reason: “She admitted it herself, so there is nothing more for me to argue about right now.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; kept: Mara 1/3. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara admits taking it, to everyone: "I took it! I ate the can in the night, okay?". **Chose: accuse Mara of taking it**, saying “You finally admitted it, Mara, but we need to know why you lied to us before.” *(new: an accusation)* (one of 17 options). Feeling: *vindicated*. Reason: “She admitted it so now I have to make sure she understands the gravity of what she did.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel reassures Mara: "Mara, nobody is going to hurt you, I just need to figure this out."; Mara admits taking it, to everyone: "I took it! I ate the can in the night, okay?"; Daniel accuses Mara of taking it: "You finally admitted it, Mara, but we need to know why you lied to us before.". **Chose: reassure Mara**, saying “Mara, it is alright now, thank you for telling us the truth.” *(not new: reassurance)* (one of 16 options). Feeling: *deeply worried*. Reason: “She confessed, and I need to make sure she feels safe after admitting it.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's guilt, now 3 of 3: Elena reassured her.*
- *Daniel's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Daniel.*
- *Elena's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Elena.*
- *Leo's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Leo.*
- *The kitchen's conversation starts (minute 27): Mara: a confession.*

**min 30** · kitchen: Daniel talking, Elena eating, Leo eating, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Daniel accuses you of taking it: "You finally admitted it, Mara, but we need to know why you lied to us before."; Elena reassures you: "Mara, it is alright now, thank you for telling us the truth.". **Chose: reassure Elena**, saying “I'm sorry, Mom, I really am. I won't do it again.” *(not new: reassurance)* (one of 16 options). Feeling: *guilty*. Reason: “I need Mom to know I am sorry for lying and taking the food.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: just spoken to by Mara). Social moment: Mara reassures you: "I'm sorry, Mom, I really am. I won't do it again.". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: eat one of the portions**, saying “We must keep our strength up, let us eat what is left.” *(not new: a remark (the rules cannot tell what free words add))* (one of 14 options). Feeling: *exhausted*. Reason: “I am terribly hungry and we need to face what comes next with strength.” Suspects: Mara, so suspicion Mara 2/3. Angry at: nobody; kept: Mara 1/3. Came of it: ate a portion; 1 left. New in the room: Elena ate one of the portions.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You finally admitted it, Mara, but we need to know why you lied to us before."; Elena reassures Mara: "Mara, it is alright now, thank you for telling us the truth."; Mara reassures Elena: "I'm sorry, Mom, I really am. I won't do it again."; Elena says to everyone, while eating: "We must keep our strength up, let us eat what is left."; Elena eats one of the portions. **Chose: eat one of the portions**, saying “If we are splitting the last portion between us, we should just eat it and move on.” *(not new: a remark (the rules cannot tell what free words add))* (one of 17 options). Feeling: *hungry*. Reason: “I need to keep my strength up just like the rest of them.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Elena; grudge against Elena rose to 2/3; kept: Mara 1/3. Came of it: ate a portion; 0 left. New in the room: Leo ate one of the portions.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures Mara: "Mara, it is alright now, thank you for telling us the truth."; Mara reassures Elena: "I'm sorry, Mom, I really am. I won't do it again."; Elena says to everyone, while eating: "We must keep our strength up, let us eat what is left."; Elena eats one of the portions; Leo says to everyone, while eating: "If we are splitting the last portion between us, we should just eat it and move on."; Leo eats one of the portions. **Chose: accuse Mara of taking it**, saying “You both just ate the last of everything while I got nothing, and Mara still hasn't explained why she stole from us in the first place.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *furious*. Reason: “They are eating the remaining food right in front of me without any regard for what Mara did.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Mara; grudge against Mara rose to 3/3; kept: Elena 1/3, Leo 1/3. Came of it: said to Elena, Leo, Mara.
- *Daniel's grudge against Elena, now 1 of 3: Elena ate in front of Daniel, who was hungry.*
- *Leo's grudge against Elena, now 1 of 3: Elena ate in front of Leo, who was hungry.*
- *Mara's grudge against Elena, now 1 of 3: Elena ate in front of Mara, who was hungry.*
- *Daniel's grudge against Leo, now 1 of 3: Leo ate in front of Daniel, who was hungry.*
- *Mara's grudge against Leo, now 1 of 3: Leo ate in front of Mara, who was hungry.*

**min 33** · kitchen: Daniel talking, Elena talking, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Elena says to everyone, while eating: "We must keep our strength up, let us eat what is left."; Elena eats one of the portions; Leo says to everyone, while eating: "If we are splitting the last portion between us, we should just eat it and move on."; Leo eats one of the portions; Daniel accuses you of taking it: "You both just ate the last of everything while I got nothing, and Mara still hasn't explained why she stole from us in the first place."; Daniel looks furious. **Chose: stay put and say nothing** (one of 14 options). Feeling: *terrified*. Reason: “I am too scared to speak while Daniel looks this furious at me.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3, Leo 1/3. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: shows the strongest feeling here (furious)). Social moment: Mara looks terrified. **Chose: accuse Mara of taking it**, saying “You still haven't told us why you stole that food, Mara, while the rest of us starve.” *(not new: an accusation they had made before)* (one of 15 options). Feeling: *starving*. Reason: “She still has not given a proper explanation for stealing from us.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Elena 1/3, Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You both just ate the last of everything while I got nothing, and Mara still hasn't explained why she stole from us in the first place."; Daniel accuses Mara of taking it: "You still haven't told us why you stole that food, Mara, while the rest of us starve."; Mara looks terrified. **Chose: reassure Mara**, saying “Mara, you already told us what happened, so let it go now.” *(not new: reassurance)* (one of 15 options). Feeling: *calmly resolute*. Reason: “Mara is terrified and has already admitted to it, so rehashing the accusation serves no purpose.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Elena 2/3, Mara 1/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo says to everyone, while eating: "If we are splitting the last portion between us, we should just eat it and move on."; Leo eats one of the portions; Daniel accuses Mara of taking it: "You both just ate the last of everything while I got nothing, and Mara still hasn't explained why she stole from us in the first place."; Daniel accuses Mara of taking it: "You still haven't told us why you stole that food, Mara, while the rest of us starve."; Leo reassures Mara: "Mara, you already told us what happened, so let it go now."; Mara looks terrified. **Chose: reassure Daniel**, saying “Daniel, please calm down, we will find a way through this together without turning on each other.” *(not new: reassurance)* (one of 14 options). Feeling: *anxious*. Reason: “I need to calm Daniel down before this anger tears our family apart completely.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's guilt, now 3 of 3: Leo reassured her.*

**min 36** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Elena). Social moment: Leo reassures Mara: "Mara, you already told us what happened, so let it go now."; Elena reassures you: "Daniel, please calm down, we will find a way through this together without turning on each other."; Mara looks terrified. Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: say something else**, saying “Mara, you need to answer me right now so we can figure out what to do next.” *(not new: a remark (the rules cannot tell what free words add))* (one of 15 options). Feeling: *anxious*. Reason: “I need to get an explanation from Mara and take charge of this situation before things fall apart completely.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Elena 1/3, Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just spoken to by Leo). Social moment: Daniel accuses you of taking it: "You still haven't told us why you stole that food, Mara, while the rest of us starve."; Leo reassures you: "Mara, you already told us what happened, so let it go now."; Elena reassures Daniel: "Daniel, please calm down, we will find a way through this together without turning on each other."; Daniel says to everyone: "Mara, you need to answer me right now so we can figure out what to do next.". **Chose: reassure everyone here**, saying “I'm sorry, I already said I took it and I'm really sorry.” *(not new: reassurance)* (one of 13 options). Feeling: *deeply guilty*. Reason: “I have to keep telling them it was me so they stop fighting, even though I'm terrified.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3, Leo 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone: "Mara, you need to answer me right now so we can figure out what to do next."; Mara reassures everyone: "I'm sorry, I already said I took it and I'm really sorry.". **Chose: reassure everyone here**, saying “We are all tired and afraid, but we must not let this tear our family apart.” *(not new: reassurance)* (one of 15 options). Feeling: *deeply anxious*. Reason: “I need to keep the family from turning on each other while we have nothing left.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures Daniel: "Daniel, please calm down, we will find a way through this together without turning on each other."; Daniel says to everyone: "Mara, you need to answer me right now so we can figure out what to do next."; Mara reassures everyone: "I'm sorry, I already said I took it and I'm really sorry."; Elena reassures everyone: "We are all tired and afraid, but we must not let this tear our family apart.". **Chose: reassure everyone here**, saying “Mara already told us what happened, so let us just drop it and focus on what comes next.” *(not new: reassurance)* (one of 14 options). Feeling: *calm*. Reason: “We already know the truth, so there is no point in keeping the argument going.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Elena 2/3, Mara 1/3. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation ends (minute 39): 2 full turns in a row with nothing new.*

**min 39** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 39–63 (9 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 39–87 (17 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 39–51 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 39–87 (17 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 11 options). Feeling: *starving*. Reason: “I am too hungry and miserable to speak after sitting here in silence for so long.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3; grudge against Elena fell to 0/3; grudge against Leo fell to 0/3. Came of it: stayed where they were.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: accuse Mara of taking it**, saying “Mara, you still haven't explained why you took that food from us while we are all starving.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *starving*. Reason: “I need Mara to confess and explain her actions so we can regain order.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; grudge against Elena fell to 0/3; grudge against Leo fell to 0/3. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now." *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Let us calm down, no one here would steal from their own family." *(not new: reassurance)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take anything. Why are you all looking at me like that?" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything. Stop looking at me like that." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Let us not turn on each other, we will figure this out together." *(not new: reassurance)*
- min 03, kitchen. Daniel asks everyone who took the can: "Someone has to answer me right now. Who took the can?" *(not new: a question they had asked before)*
- min 06, kitchen. Mara denies taking it, to everyone: "I didn't touch it, Daniel! Why do you keep staring at me like that?" *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Elena says to everyone, while searching: "Let us check the room properly before we point fingers at anyone." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Daniel says to everyone, while searching: "Keep looking, Mom is right, we need to check every inch of this room." *(not new: a remark (the rules cannot tell what free words add))*
- min 12, kitchen. Daniel asks everyone who took the can: "Someone has to step up and tell the truth right now. Who took the can?" *(not new: a question they had asked before)*
- min 12, kitchen. Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me like I'm a thief?" *(not new: a denial with no new accusation to answer)*
- min 12, kitchen. Elena reassures everyone: "Let us calm down and breathe, we are going to get through this together." *(not new: reassurance)*
- min 15, kitchen. Daniel asks everyone who took the can: "Nobody is answering me. I want to know right now who took the can." *(not new: a question they had asked before)*
- min 15, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take it! Stop asking me over and over again." *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Daniel asks everyone who took the can: "I need an answer right now. Which one of you took the can?" *(not new: a question they had asked before)*
- min 21, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, I swear I didn't!" *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Elena reassures everyone: "Let us all calm down, shouting at each other will not bring the food back." *(not new: reassurance)*
- min 24, kitchen. Mara denies taking it, to everyone: "I already told you, I did not take the can! Please stop looking at me like that." *(not new: a denial with no new accusation to answer)*
- min 24, kitchen. Leo reassures Mara: "Mara, take a breath, nobody is going to hurt you." *(not new: reassurance)*
- min 24, kitchen. Elena reassures Mara: "Mara, you are safe here with me, nobody is going to touch you." *(not new: reassurance)*
- min 24, kitchen. Daniel reassures Mara: "Mara, nobody is going to hurt you, I just need to figure this out." *(not new: reassurance)*
- min 27, kitchen. Mara admits taking it, to everyone: "I took it! I ate the can in the night, okay?" *(new: a confession)*
- min 27, kitchen. Daniel accuses Mara of taking it: "You finally admitted it, Mara, but we need to know why you lied to us before." *(new: an accusation)*
- min 27, kitchen. Elena reassures Mara: "Mara, it is alright now, thank you for telling us the truth." *(not new: reassurance)*
- min 30, kitchen. Mara reassures Elena: "I'm sorry, Mom, I really am. I won't do it again." *(not new: reassurance)*
- min 30, kitchen. Elena says to everyone, while eating: "We must keep our strength up, let us eat what is left." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Leo says to everyone, while eating: "If we are splitting the last portion between us, we should just eat it and move on." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Daniel accuses Mara of taking it: "You both just ate the last of everything while I got nothing, and Mara still hasn't explained why she stole from us in the first place." *(not new: an accusation they had made before)*
- min 33, kitchen. Daniel accuses Mara of taking it: "You still haven't told us why you stole that food, Mara, while the rest of us starve." *(not new: an accusation they had made before)*
- min 33, kitchen. Leo reassures Mara: "Mara, you already told us what happened, so let it go now." *(not new: reassurance)*
- min 33, kitchen. Elena reassures Daniel: "Daniel, please calm down, we will find a way through this together without turning on each other." *(not new: reassurance)*
- min 36, kitchen. Daniel says to everyone: "Mara, you need to answer me right now so we can figure out what to do next." *(not new: a remark (the rules cannot tell what free words add))*
- min 36, kitchen. Mara reassures everyone: "I'm sorry, I already said I took it and I'm really sorry." *(not new: reassurance)*
- min 36, kitchen. Elena reassures everyone: "We are all tired and afraid, but we must not let this tear our family apart." *(not new: reassurance)*
- min 36, kitchen. Leo reassures everyone: "Mara already told us what happened, so let us just drop it and focus on what comes next." *(not new: reassurance)*
- min 66, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't explained why you took that food from us while we are all starving." *(not new: an accusation they had made before)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Elena 1, Leo 1.

- Who admitted taking it: Mara at minute 27.
- Accusations: Daniel accused Mara (minute 27); Daniel accused Mara (minute 30); Daniel accused Mara (minute 33); Daniel accused Mara (minute 66).
- Who else knows Mara took it: Daniel, Elena, Leo.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 09 (Daniel finished searching the kitchen and found nothing); kitchen ended at minute 18 (2 full turns in a row with nothing new); kitchen started at minute 18 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 27 (2 full turns in a row with nothing new); kitchen started at minute 27 (Mara: a confession); kitchen ended at minute 39 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects Mara 3/3 | suspects Mara 3/3 | suspects none |
| Grudges | Mara 3/3 | Mara 1/3 | Mara 1/3, Elena 2/3 | Daniel 3/3 |
| Hunger | starving | hungry | a little hungry | very hungry |
| Guilt | - | - | - | 3/3 |

The events behind each grudge still held at minute 90, and behind Mara's guilt:

- Daniel against Mara (3/3): Mara admitted taking it at minute 27, after denying it to you at minute 24; you were angry with Mara at minutes 27, 30, 33, 36 and 66.
- Elena against Mara (1/3): Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Mara (1/3): Mara admitted taking it at minute 27, after denying it to you at minute 24.
- Leo against Elena (2/3): Elena ate a portion in front of you at minute 30, while you were hungry; you were angry with Elena at minute 30.
- Mara against Daniel (3/3): you were angry with Daniel at minutes 00, 03, 06, 12, 15, 21, 24, 27, 30, 33, 36 and 54.
- Mara's guilt (3/3): she ate the can in the night, and nobody saw; Leo reassured you, at minute 24; Elena reassured you, at minute 24; Daniel reassured you, at minute 24; Elena reassured you, at minute 27; Leo reassured you, at minute 33.

- The last feeling each of them named: Daniel *starving* (minute 66); Elena *deeply anxious* (minute 36); Leo *calm* (minute 36); Mara *starving* (minute 54).


### mara_ate_it, Flash Lite, seed 2

#### The morning as a story: mara_ate_it, rules and a language model, seed 2

Generated by `python morning.py --scenario mara_ate_it --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 37 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 83 routine ones settled by the rules. 26 lines were spoken aloud, 4 of them new. Conversations ended 2 times. 8 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Mara, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Mara's guilt** starts at 1 and rises a step when someone else is accused of what she did in her hearing (by anyone, herself included), or when someone reassures her personally. Her denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | ate it in the night; nobody saw |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Mara eats a can sitting on the kitchen floor. Nobody sees. | not there | not there | not there | did it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing from the shelf. Did one of you take it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know what happened to the food before this breaks us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?". **Chose: deny taking it**, saying “I didn't take it, Mom! Why does everyone always look at me?” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *terrified*. Reason: “I am too scared of getting into trouble and having everyone angry at me, so I lie to protect myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, Mom! Why does everyone always look at me?"; Mara looks terrified. **Chose: ask everyone here who took the can**, saying “Hold on, nobody is pointing fingers until we talk this through properly. Did any of you actually take it?” *(new: a question)* (one of 21 options). Feeling: *anxious*. Reason: “As the oldest, I need to take charge of this situation before it turns us against each other, but I have to know the truth first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, Mom! Why does everyone always look at me?"; Daniel asks everyone who took the can: "Hold on, nobody is pointing fingers until we talk this through properly. Did any of you actually take it?"; Mara looks terrified. **Chose: deny taking it**, saying “I didn't take it either, and accusing each other won't put the food back.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *calm*. Reason: “I need to state clearly that I am innocent without escalating the tension.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel searching the kitchen, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (terrified)). Social moment: Daniel asks everyone who took the can: "Hold on, nobody is pointing fingers until we talk this through properly. Did any of you actually take it?"; Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't put the food back.". **Chose: deny taking it**, saying “I already told you, I didn't take anything!” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *anxious*. Reason: “I am too scared of getting in trouble to admit I ate the can in the night.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, Mom! Why does everyone always look at me?"; Daniel asks everyone who took the can: "Hold on, nobody is pointing fingers until we talk this through properly. Did any of you actually take it?"; Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't put the food back."; Mara denies taking it, to everyone: "I already told you, I didn't take anything!". **Chose: reassure everyone here**, saying “Nobody needs to accuse anyone. We will figure this out together without tearing each other apart.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and prevent the family from turning on each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take anything!"; Elena reassures everyone: "Nobody needs to accuse anyone. We will figure this out together without tearing each other apart.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *calm*. Reason: “There is no proof yet, so staying quiet is better than making things worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't put the food back."; Mara denies taking it, to everyone: "I already told you, I didn't take anything!"; Elena reassures everyone: "Nobody needs to accuse anyone. We will figure this out together without tearing each other apart.". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I am going to search this kitchen right now so we can settle this once and for all.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “I need to take charge and find out the truth myself before things fall apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 06** · kitchen: Daniel standing, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Nobody needs to accuse anyone. We will figure this out together without tearing each other apart."; Daniel says to everyone, while searching: "I am going to search this kitchen right now so we can settle this once and for all."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: deny taking it**, saying “I already told you, I didn't take anything, Daniel! Stop looking at me like that.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *very anxious*. Reason: “I cannot bear the shame of admitting I ate the can in the night, so I have to keep lying even though my guilt is eating me alive.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone, while searching: "I am going to search this kitchen right now so we can settle this once and for all."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara denies taking it, to everyone: "I already told you, I didn't take anything, Daniel! Stop looking at me like that.". **Chose: reassure Mara**, saying “It is alright, Mara. No one is going to accuse you of anything.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must protect Mara from Daniel's suspicions before this breaks us all apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while searching: "I am going to search this kitchen right now so we can settle this once and for all."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara denies taking it, to everyone: "I already told you, I didn't take anything, Daniel! Stop looking at me like that."; Elena reassures Mara: "It is alright, Mara. No one is going to accuse you of anything.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “Letting Daniel finish his search before speaking again will keep things from getting any more heated.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *Mara's guilt, now 2 of 3: Elena reassured her.*

**min 09** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Elena reassures you: "It is alright, Mara. No one is going to accuse you of anything.". Not offered: denied taking it three turns in a row, so no more of it this turn. **Chose: admit taking it**, saying “I can't lie anymore, I was just so hungry in the night and I ate it.” *(new: a confession)* (one of 22 options). Feeling: *guilty*. Reason: “I cannot stand everyone arguing and trusting me when I am the one who actually ate the food.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara admits taking it, to everyone: "I can't lie anymore, I was just so hungry in the night and I ate it.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *wary*. Reason: “She already changed her story once, so I need to see if she actually means it this time.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara admits taking it, to everyone: "I can't lie anymore, I was just so hungry in the night and I ate it.". **Chose: reassure Mara**, saying “It is alright, Mara. We are not going to let this tear us apart.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply anxious*. Reason: “I need to comfort her now that she has confessed so we can stay close as a family.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take anything, Daniel! Stop looking at me like that."; Elena reassures Mara: "It is alright, Mara. No one is going to accuse you of anything."; Mara admits taking it, to everyone: "I can't lie anymore, I was just so hungry in the night and I ate it."; Elena reassures Mara: "It is alright, Mara. We are not going to let this tear us apart.". **Chose: accuse Mara of taking it**, saying “You can't just change your story like that, Mara. Tell us the truth right now.” *(new: an accusation)* (one of 16 options). Feeling: *anxious*. Reason: “I need to know exactly what happened instead of her changing her mind every minute.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: said to Elena, Leo, Mara.
- *Mara's guilt, now 3 of 3: Elena reassured her.*
- *Daniel's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Daniel.*
- *Elena's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Elena.*
- *Leo's grudge against Mara, now 1 of 3: Mara admitted it after denying it to Leo.*

**min 12** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Elena reassures you: "It is alright, Mara. We are not going to let this tear us apart."; Daniel accuses you of taking it: "You can't just change your story like that, Mara. Tell us the truth right now.". **Chose: reassure everyone here**, saying “I'm sorry, I really didn't mean to cause any trouble for anyone.” *(not new: reassurance)* (one of 17 options). Feeling: *guilty*. Reason: “I want them to know I am sorry for eating the food and causing a fight.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures Mara: "It is alright, Mara. We are not going to let this tear us apart."; Daniel accuses Mara of taking it: "You can't just change your story like that, Mara. Tell us the truth right now."; Mara reassures everyone: "I'm sorry, I really didn't mean to cause any trouble for anyone.". **Chose: reassure Mara**, saying “It's all right, Mara. What's done is done, we just need to figure out how to move forward.” *(not new: reassurance)* (one of 18 options). Feeling: *calm*. Reason: “Mara already admitted it and apologized, so continuing to press the issue serves no purpose.” Suspects: Mara, so suspicion Mara 2/3. Angry at: nobody; kept: Mara 2/3. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara reassures everyone: "I'm sorry, I really didn't mean to cause any trouble for anyone."; Leo reassures Mara: "It's all right, Mara. What's done is done, we just need to figure out how to move forward.". **Chose: accuse Mara of taking it**, saying “You can't just pretend everything is fine after admitting you stole from us.” *(not new: an accusation they had made before)* (one of 17 options). Feeling: *frustrated*. Reason: “She confessed to taking the food and everyone is acting like it is no big deal.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Mara; grudge against Mara rose to 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "You can't just change your story like that, Mara. Tell us the truth right now."; Mara reassures everyone: "I'm sorry, I really didn't mean to cause any trouble for anyone."; Leo reassures Mara: "It's all right, Mara. What's done is done, we just need to figure out how to move forward."; Daniel accuses Mara of taking it: "You can't just pretend everything is fine after admitting you stole from us.". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: say something else**, saying “Daniel, stop. She told us the truth, and shouting at her won't bring the food back.” *(not new: a remark (the rules cannot tell what free words add))* (one of 12 options). Feeling: *deeply anxious*. Reason: “I must stop Daniel from tearing the family apart over this.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Daniel; grudge against Daniel rose to 1/3; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's guilt, now 3 of 3: Leo reassured her.*

**min 15** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Leo reassures you: "It's all right, Mara. What's done is done, we just need to figure out how to move forward."; Daniel accuses you of taking it: "You can't just pretend everything is fine after admitting you stole from us."; Elena says to everyone: "Daniel, stop. She told us the truth, and shouting at her won't bring the food back.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *anxious*. Reason: “I have already caused enough trouble and don't know what else to say right now.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You can't just pretend everything is fine after admitting you stole from us."; Elena says to everyone: "Daniel, stop. She told us the truth, and shouting at her won't bring the food back.". **Chose: stay put and say nothing** (one of 18 options). Feeling: *hungry*. Reason: “There is nothing more to argue about since she already admitted it, so I will stay quiet.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Mara 2/3. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Mara rose (now 2 of 3); grudge against Daniel rose (now 1 of 3). **Chose: reassure everyone here**, saying “Let us not turn on each other, we will get through this if we stay together.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I need to calm the tension before Daniel starts shouting again and tears us apart.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Daniel; grudge against Daniel rose to 2/3; kept: Mara 1/3. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena says to everyone: "Daniel, stop. She told us the truth, and shouting at her won't bring the food back."; Elena reassures everyone: "Let us not turn on each other, we will get through this if we stay together.". **Chose: accuse Mara of taking it**, saying “You still took what didn't belong to you, Mara, and an apology doesn't bring it back.” *(not new: an accusation they had made before)* (one of 15 options). Feeling: *anxious*. Reason: “I have to make sure everyone understands the seriousness of what Mara did so we protect what is left.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 18): 2 full turns in a row with nothing new.*

**min 18** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 18–24 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: reassure everyone here**, saying “We are going to figure this out together, no one is going to starve.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and show I am leading us through this.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena, minutes 18–21 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). **Chose: stay put and say nothing** (one of 16 options). Feeling: *hungry*. Reason: “Arguing in circles gets us nowhere when we are all this hungry.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Mara 2/3. Came of it: stayed where they were.

**min 21** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 21–24 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 21–24 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 24** · kitchen: Daniel staying put, Elena sharing out the food, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3); grudge against Daniel rose (now 2 of 3). **Chose: share out what is left among everyone here**, saying “Let us share what is left so no one goes hungry.” *(not new: a remark (the rules cannot tell what free words add))* (one of 16 options). Feeling: *anxious*. Reason: “We must divide the remaining food fairly before this tension tears us all apart.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; grudge against Mara fell to 0/3; kept: Daniel 2/3. Came of it: shared out the last 2 portions between Elena, Daniel, Leo, Mara. New in the room: Elena shared out the food.
- *The kitchen's conversation starts (minute 24): Elena shared out the food.*

**min 27** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena says to everyone, while sharing out the food: "Let us share what is left so no one goes hungry."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara. **Chose: stay put and say nothing** (one of 13 options). Feeling: *ashamed*. Reason: “I have already eaten and confessed, so there is nothing left for me to say or do.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 3/3. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena says to everyone, while sharing out the food: "Let us share what is left so no one goes hungry."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara. **Chose: accuse Mara of taking it**, saying “You still act like nothing happened, Mara, but you are the reason we are in this mess.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *resentful*. Reason: “I must make sure she understands the gravity of what she did.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena says to everyone, while sharing out the food: "Let us share what is left so no one goes hungry."; Elena shares out the last 2 portions between Elena, Daniel, Leo, Mara; Daniel accuses Mara of taking it: "You still act like nothing happened, Mara, but you are the reason we are in this mess.". **Chose: reassure Daniel**, saying “Daniel, shouting at her isn't going to bring the food back, we've already eaten what was left.” *(not new: reassurance)* (one of 14 options). Feeling: *calm*. Reason: “There is no point in escalating the argument since the food is already gone and Mara admitted it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; grudge against Mara fell to 1/3. Came of it: said to Daniel, Elena, Mara.

**min 30** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Leo). Social moment: Leo reassures you: "Daniel, shouting at her isn't going to bring the food back, we've already eaten what was left.". **Chose: accuse Mara of taking it**, saying “You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *resentful*. Reason: “She admitted it herself earlier and needs to know she cannot just get away with endangering us all.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "You still act like nothing happened, Mara, but you are the reason we are in this mess."; Leo reassures Daniel: "Daniel, shouting at her isn't going to bring the food back, we've already eaten what was left."; Daniel accuses you of taking it: "You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open.". **Chose: reassure everyone here**, saying “I really am sorry, I'll never do anything like that again.” *(not new: reassurance)* (one of 13 options). Feeling: *guilty*. Reason: “I want them to stop fighting and know that I am truly sorry for what I did.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open."; Mara reassures everyone: "I really am sorry, I'll never do anything like that again.". **Chose: stay put and say nothing** (one of 15 options). Feeling: *exhausted*. Reason: “There is nothing left to say after we have already eaten the last portions and argued in circles.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Mara 1/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "You still act like nothing happened, Mara, but you are the reason we are in this mess."; Leo reassures Daniel: "Daniel, shouting at her isn't going to bring the food back, we've already eaten what was left."; Daniel accuses Mara of taking it: "You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open."; Mara reassures everyone: "I really am sorry, I'll never do anything like that again.". **Chose: reassure everyone here**, saying “Let us stop arguing now, we have shared the food and we must hold together.” *(not new: reassurance)* (one of 14 options). Feeling: *anxious*. Reason: “I need to keep the peace and prevent the family from tearing itself apart over what is already done.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; grudge against Daniel fell to 1/3. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation ends (minute 33): 2 full turns in a row with nothing new.*

**min 33** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 33–51 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 33–87 (19 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 33–60 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 13 options). Feeling: *anxious*. Reason: “I have already said my piece and there is nothing left to argue about right now.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: stayed where they were.

**min 36** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 36–75 (14 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 12 options). Feeling: *ashamed*. Reason: “I have nothing left to say after everything that happened, so I will just stay quiet.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: stay put and say nothing** (one of 15 options). Feeling: *exhausted*. Reason: “There is nothing left to say while we just sit here in silence.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; grudge against Mara fell to 0/3. Came of it: stayed where they were.

**min 66** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 78** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Mara of taking it**, saying “You think time makes it go away, Mara, but you are the one who broke our trust.” *(not new: an accusation they had made before)* (one of 15 options). Feeling: *resentful*. Reason: “She caused all of this and still pretends nothing is wrong.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.

**min 81** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 81–87 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, Mom! Why does everyone always look at me?" *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Daniel asks everyone who took the can: "Hold on, nobody is pointing fingers until we talk this through properly. Did any of you actually take it?" *(new: a question)*
- min 00, kitchen. Leo denies taking it, to everyone: "I didn't take it either, and accusing each other won't put the food back." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything!" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Nobody needs to accuse anyone. We will figure this out together without tearing each other apart." *(not new: reassurance)*
- min 03, kitchen. Daniel says to everyone, while searching: "I am going to search this kitchen right now so we can settle this once and for all." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything, Daniel! Stop looking at me like that." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Elena reassures Mara: "It is alright, Mara. No one is going to accuse you of anything." *(not new: reassurance)*
- min 09, kitchen. Mara admits taking it, to everyone: "I can't lie anymore, I was just so hungry in the night and I ate it." *(new: a confession)*
- min 09, kitchen. Elena reassures Mara: "It is alright, Mara. We are not going to let this tear us apart." *(not new: reassurance)*
- min 09, kitchen. Daniel accuses Mara of taking it: "You can't just change your story like that, Mara. Tell us the truth right now." *(new: an accusation)*
- min 12, kitchen. Mara reassures everyone: "I'm sorry, I really didn't mean to cause any trouble for anyone." *(not new: reassurance)*
- min 12, kitchen. Leo reassures Mara: "It's all right, Mara. What's done is done, we just need to figure out how to move forward." *(not new: reassurance)*
- min 12, kitchen. Daniel accuses Mara of taking it: "You can't just pretend everything is fine after admitting you stole from us." *(not new: an accusation they had made before)*
- min 12, kitchen. Elena says to everyone: "Daniel, stop. She told us the truth, and shouting at her won't bring the food back." *(not new: a remark (the rules cannot tell what free words add))*
- min 15, kitchen. Elena reassures everyone: "Let us not turn on each other, we will get through this if we stay together." *(not new: reassurance)*
- min 15, kitchen. Daniel accuses Mara of taking it: "You still took what didn't belong to you, Mara, and an apology doesn't bring it back." *(not new: an accusation they had made before)*
- min 18, kitchen. Daniel reassures everyone: "We are going to figure this out together, no one is going to starve." *(not new: reassurance)*
- min 24, kitchen. Elena says to everyone, while sharing out the food: "Let us share what is left so no one goes hungry." *(not new: a remark (the rules cannot tell what free words add))*
- min 27, kitchen. Daniel accuses Mara of taking it: "You still act like nothing happened, Mara, but you are the reason we are in this mess." *(not new: an accusation they had made before)*
- min 27, kitchen. Leo reassures Daniel: "Daniel, shouting at her isn't going to bring the food back, we've already eaten what was left." *(not new: reassurance)*
- min 30, kitchen. Daniel accuses Mara of taking it: "You still cannot be trusted after all of this, Mara, and someone has to keep our eyes open." *(not new: an accusation they had made before)*
- min 30, kitchen. Mara reassures everyone: "I really am sorry, I'll never do anything like that again." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "Let us stop arguing now, we have shared the food and we must hold together." *(not new: reassurance)*
- min 78, kitchen. Daniel accuses Mara of taking it: "You think time makes it go away, Mara, but you are the one who broke our trust." *(not new: an accusation they had made before)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Daniel 0.5, Elena 0.5, Leo 0.5, Mara 0.5.

- Who admitted taking it: Mara at minute 09.
- Accusations: Daniel accused Mara (minute 09); Daniel accused Mara (minute 12); Daniel accused Mara (minute 15); Daniel accused Mara (minute 27); Daniel accused Mara (minute 30); Daniel accused Mara (minute 78).
- Who else knows Mara took it: Daniel, Elena, Leo.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 18 (2 full turns in a row with nothing new); kitchen started at minute 24 (Elena shared out the food); kitchen ended at minute 33 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects Mara 3/3 | suspects Mara 3/3 | suspects none |
| Grudges | Mara 3/3 | Daniel 1/3 | none | Daniel 3/3 |
| Hunger | very hungry | very hungry | hungry | hungry |
| Guilt | - | - | - | 3/3 |

The events behind each grudge still held at minute 90, and behind Mara's guilt:

- Daniel against Mara (3/3): Mara admitted taking it at minute 09, after denying it to you at minute 06; you were angry with Mara at minutes 09, 12, 15, 18, 27, 30, 33 and 78.
- Elena against Daniel (1/3): you were angry with Daniel at minutes 12 and 15.
- Mara against Daniel (3/3): you were angry with Daniel at minutes 03, 06, 12, 15, 30 and 54.
- Mara's guilt (3/3): she ate the can in the night, and nobody saw; Elena reassured you, at minute 06; Elena reassured you, at minute 09; Leo reassured you, at minute 12.

- The last feeling each of them named: Daniel *resentful* (minute 78); Elena *anxious* (minute 30); Leo *exhausted* (minute 63); Mara *ashamed* (minute 54).


### mara_ate_it, Flash Lite, seed 3

#### The morning as a story: mara_ate_it, rules and a language model, seed 3

Generated by `python morning.py --scenario mara_ate_it --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 37 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 83 routine ones settled by the rules. 25 lines were spoken aloud, 2 of them new. Conversations ended 3 times. 11 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 0 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3), and for Mara, guilt (1 to 3). The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Mara's guilt** starts at 1 and rises a step when someone else is accused of what she did in her hearing (by anyone, herself included), or when someone reassures her personally. Her denials, and reassurance of everyone, add nothing. It never falls, and it never decides anything: the model still chooses.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | ate it in the night; nobody saw |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 3 | In the night Mara eats a can sitting on the kitchen floor. Nobody sees. | not there | not there | not there | did it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: admit taking it**, saying “I took it in the night. I was so hungry, I am sorry.” *(new: a confession)* (one of 22 options). Feeling: *terrified*. Reason: “I cannot stand them looking for someone to blame when I did it myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara admits taking it, to everyone: "I took it in the night. I was so hungry, I am sorry."; Mara looks terrified. **Chose: reassure Mara**, saying “It is alright, my sweet girl, we are all so hungry and we will get through this.” *(not new: reassurance)* (one of 17 options). Feeling: *deeply anxious*. Reason: “Mara is terrified and I need to protect her from her brothers' anger before this family breaks apart.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara admits taking it, to everyone: "I took it in the night. I was so hungry, I am sorry."; Elena reassures Mara: "It is alright, my sweet girl, we are all so hungry and we will get through this."; Mara looks terrified. **Chose: accuse Mara of taking it**, saying “You cannot just take things in the night, Mara, we all have to survive this together.” *(new: an accusation)* (one of 16 options). Feeling: *anxious*. Reason: “I need to make sure everyone understands rules still matter, even when we are starving.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara admits taking it, to everyone: "I took it in the night. I was so hungry, I am sorry."; Elena reassures Mara: "It is alright, my sweet girl, we are all so hungry and we will get through this."; Daniel accuses Mara of taking it: "You cannot just take things in the night, Mara, we all have to survive this together."; Mara looks terrified. **Chose: reassure Mara**, saying “It is alright, Mara, you owned up to it, and we are all hungry.” *(not new: reassurance)* (one of 16 options). Feeling: *calm*. Reason: “Mara is terrified and already admitted it, so punishing her further does not help anyone survive.” Suspects: Mara, so suspicion Mara 1/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Mara's guilt, now 2 of 3: Elena reassured her.*
- *Mara's guilt, now 3 of 3: Leo reassured her.*
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Leo). Social moment: Elena reassures you: "It is alright, my sweet girl, we are all so hungry and we will get through this."; Daniel accuses you of taking it: "You cannot just take things in the night, Mara, we all have to survive this together."; Leo reassures you: "It is alright, Mara, you owned up to it, and we are all hungry.". **Chose: reassure everyone here**, saying “I really am sorry, I promise I won't do it again.” *(not new: reassurance)* (one of 17 options). Feeling: *very anxious*. Reason: “I want them to know I feel terrible and that I didn't mean to hurt anyone.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You cannot just take things in the night, Mara, we all have to survive this together."; Leo reassures Mara: "It is alright, Mara, you owned up to it, and we are all hungry."; Mara reassures everyone: "I really am sorry, I promise I won't do it again.". **Chose: reassure everyone here**, saying “Let us not fight among ourselves, we only have each other to rely on right now.” *(not new: reassurance)* (one of 18 options). Feeling: *deeply anxious*. Reason: “I must keep the family together and stop them from tearing each other apart over food.” Suspects: Mara, so suspicion Mara 2/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo reassures Mara: "It is alright, Mara, you owned up to it, and we are all hungry."; Mara reassures everyone: "I really am sorry, I promise I won't do it again."; Elena reassures everyone: "Let us not fight among ourselves, we only have each other to rely on right now.". **Chose: reassure Mara**, saying “I am sorry for snapping, Mara, we just need to stick together through this.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I should make sure she knows I am not angry anymore, just worried for us all.” Suspects: Mara, so suspicion Mara 2/3. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Mara reassures everyone: "I really am sorry, I promise I won't do it again."; Elena reassures everyone: "Let us not fight among ourselves, we only have each other to rely on right now."; Daniel reassures Mara: "I am sorry for snapping, Mara, we just need to stick together through this.". **Chose: stay put and say nothing** (one of 16 options). Feeling: *calm*. Reason: “Since everyone is making peace and Mara already admitted it, there is no need for me to say anything more right now.” Suspects: Mara, so suspicion Mara 2/3. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *Mara's guilt, now 3 of 3: Daniel reassured her.*

**min 06** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Daniel). Social moment: Elena reassures everyone: "Let us not fight among ourselves, we only have each other to rely on right now."; Daniel reassures you: "I am sorry for snapping, Mara, we just need to stick together through this.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *overwhelmed*. Reason: “I cannot bear all their kindness when I am the one who lied and ate the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Mara rose (now 2 of 3). **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm*. Reason: “There is no need to add anything right now since the situation has already been addressed and we are all trying to stay calm.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel reassures Mara: "I am sorry for snapping, Mara, we just need to stick together through this.". **Chose: stay put and say nothing** (one of 17 options). Feeling: *anxious*. Reason: “I need to keep the peace and let everyone calm down before things get worse.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Mara rose (now 2 of 3). **Chose: reassure everyone here**, saying “We are going to make it through this day if we just keep our heads.” *(not new: reassurance)* (one of 16 options). Feeling: *anxious*. Reason: “I need to keep everyone calm and united as the eldest.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation ends (minute 09): 2 full turns in a row with nothing new.*

**min 09** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 09–12 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo, minutes 09–12 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara, minutes 09–15 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). **Chose: stay put and say nothing** (one of 16 options). Feeling: *anxious*. Reason: “I cannot bear to watch us tear ourselves apart over a single missing can.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 12** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 12–15 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo eating, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). **Chose: stay put and say nothing** (one of 17 options). Feeling: *anxious*. Reason: “I need to keep watch over everyone and make sure no one else touches the remaining food.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry); suspicion of Mara rose (now 3 of 3). **Chose: eat one of the portions**, saying “We need to eat something before we lose our strength.” *(not new: a remark (the rules cannot tell what free words add))* (one of 16 options). Feeling: *hungry*. Reason: “I need to maintain my strength as hunger is setting in.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: ate a portion; 1 left. New in the room: Leo ate one of the portions.
- *Daniel's grudge against Leo, now 1 of 3: Leo ate in front of Daniel, who was hungry.*
- *Elena's grudge against Leo, now 1 of 3: Leo ate in front of Elena, who was hungry.*
- *Mara's grudge against Leo, now 1 of 3: Leo ate in front of Mara, who was hungry.*
- *The kitchen's conversation starts (minute 15): Leo ate one of the portions.*

**min 18** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while eating: "We need to eat something before we lose our strength."; Leo eats one of the portions. **Chose: stay put and say nothing** (one of 17 options). Feeling: *guilty*. Reason: “I have already confessed and eaten the food, so there is nothing left for me to say while Leo finishes the last portion.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo says to everyone, while eating: "We need to eat something before we lose our strength."; Leo eats one of the portions. **Chose: stay put and say nothing** (one of 18 options). Feeling: *anxious*. Reason: “I must stay calm and keep the peace while we are all so hungry.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Leo 1/3. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo says to everyone, while eating: "We need to eat something before we lose our strength."; Leo eats one of the portions. **Chose: accuse Mara of taking it**, saying “You still took that extra one, Mara, and we cannot afford your selfishness right now.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *angry*. Reason: “She started all of this by taking the food in the night, and she needs to be held accountable.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara rose to 1/3; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.

**min 21** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "You still took that extra one, Mara, and we cannot afford your selfishness right now."; Daniel looks angry. **Chose: reassure Daniel**, saying “Daniel, please don't look at me like that, I didn't mean to hurt anyone.” *(not new: reassurance)* (one of 17 options). Feeling: *anxious*. Reason: “I want Daniel to stop being angry with me because I cannot bear the tension.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Leo 1/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just spoken to by Mara). Social moment: Mara reassures you: "Daniel, please don't look at me like that, I didn't mean to hurt anyone.". **Chose: accuse Mara of taking it**, saying “You can't just take food and expect us to pretend it didn't happen, Mara.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *anxious*. Reason: “She took it before and she needs to understand the danger we are in.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara rose to 2/3; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You still took that extra one, Mara, and we cannot afford your selfishness right now."; Mara reassures Daniel: "Daniel, please don't look at me like that, I didn't mean to hurt anyone."; Daniel accuses Mara of taking it: "You can't just take food and expect us to pretend it didn't happen, Mara.". **Chose: reassure Mara**, saying “Mara already admitted it and apologized, Daniel, so there is no point keeping on about it.” *(not new: reassurance)* (one of 17 options). Feeling: *calm*. Reason: “She already confessed, and arguing further only makes things worse.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "You still took that extra one, Mara, and we cannot afford your selfishness right now."; Mara reassures Daniel: "Daniel, please don't look at me like that, I didn't mean to hurt anyone."; Daniel accuses Mara of taking it: "You can't just take food and expect us to pretend it didn't happen, Mara."; Leo reassures Mara: "Mara already admitted it and apologized, Daniel, so there is no point keeping on about it.". **Chose: reassure everyone here**, saying “Let us stop arguing now, we cannot let hunger tear our family apart.” *(not new: reassurance)* (one of 16 options). Feeling: *deeply anxious*. Reason: “I need to keep the peace between them before this anger destroys us all.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; kept: Leo 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's guilt, now 3 of 3: Leo reassured her.*
- *The kitchen's conversation ends (minute 24): 2 full turns in a row with nothing new.*

**min 24** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). **Chose: stay put and say nothing** (one of 18 options). Feeling: *calm*. Reason: “There is no need to keep arguing when Mara already confessed and we are all just trying to survive.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.
- **Elena, minutes 24–27 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: grudge against Mara rose (now 2 of 3). **Chose: stay put and say nothing** (one of 16 options). Feeling: *tense*. Reason: “I need to keep my authority without making things worse.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara rose to 3/3; kept: Leo 1/3. Came of it: stayed where they were.

**min 27** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo, minutes 27–30 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 30** · kitchen: Daniel talking, Elena eating, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: eat one of the portions**, saying “I must eat something, or I will not have the strength to hold us together.” *(not new: a remark (the rules cannot tell what free words add))* (one of 18 options). Feeling: *starving*. Reason: “My body is screaming for food and I cannot stay strong for them if I collapse.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; grudge against Leo fell to 0/3. Came of it: ate a portion; 0 left. New in the room: Elena ate one of the portions.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena says to everyone, while eating: "I must eat something, or I will not have the strength to hold us together."; Elena eats one of the portions. **Chose: accuse Mara of taking it**, saying “Mara, you started all of this by taking that can, and it's time you owned up to it.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *resentful*. Reason: “Someone needs to hold her accountable for the mess she made while the rest of us starve.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; grudge against Leo fell to 0/3; kept: Elena 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: just accused by Daniel). Social moment: Elena says to everyone, while eating: "I must eat something, or I will not have the strength to hold us together."; Elena eats one of the portions; Daniel accuses you of taking it: "Mara, you started all of this by taking that can, and it's time you owned up to it.". **Chose: reassure Daniel**, saying “Daniel, I already told you I am sorry, please stop looking at me like that.” *(not new: reassurance)* (one of 12 options). Feeling: *guilty*. Reason: “I cannot bear Daniel looking at me with so much accusation when I already confessed.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3; grudge against Leo fell to 0/3; kept: Elena 1/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's grudge against Elena, now 1 of 3: Elena ate in front of Daniel, who was hungry.*
- *Mara's grudge against Elena, now 1 of 3: Elena ate in front of Mara, who was hungry.*
- *The kitchen's conversation starts (minute 30): Elena ate one of the portions.*

**min 33** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just spoken to by Mara). Social moment: Mara reassures you: "Daniel, I already told you I am sorry, please stop looking at me like that.". **Chose: accuse Mara of taking it**, saying “Mara, you still haven't explained why you lied about the whole thing in the first place.” *(not new: an accusation they had made before)* (one of 16 options). Feeling: *resentful*. Reason: “I need to make sure everyone understands the threat she poses to us.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Elena 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, you still haven't explained why you lied about the whole thing in the first place.". **Chose: say something else**, saying “Daniel, I already told you everything I know, I don't know what else you want me to say.” *(not new: a remark (the rules cannot tell what free words add))* (one of 14 options). Feeling: *defensive*. Reason: “I cannot keep defending myself when they keep bringing up the same thing over and over.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3; kept: Elena 1/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena says to everyone, while eating: "I must eat something, or I will not have the strength to hold us together."; Elena eats one of the portions; Daniel accuses Mara of taking it: "Mara, you started all of this by taking that can, and it's time you owned up to it."; Mara reassures Daniel: "Daniel, I already told you I am sorry, please stop looking at me like that."; Daniel accuses Mara of taking it: "Mara, you still haven't explained why you lied about the whole thing in the first place."; Mara says to everyone: "Daniel, I already told you everything I know, I don't know what else you want me to say.". **Chose: reassure Mara**, saying “Daniel, she already admitted it once and there is no point dragging this out further.” *(not new: reassurance)* (one of 15 options). Feeling: *annoyed*. Reason: “Daniel is just going in circles and upsetting Mara for no reason.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, you started all of this by taking that can, and it's time you owned up to it."; Mara reassures Daniel: "Daniel, I already told you I am sorry, please stop looking at me like that."; Daniel accuses Mara of taking it: "Mara, you still haven't explained why you lied about the whole thing in the first place."; Mara says to everyone: "Daniel, I already told you everything I know, I don't know what else you want me to say."; Leo reassures Mara: "Daniel, she already admitted it once and there is no point dragging this out further.". **Chose: reassure everyone here**, saying “Let us not turn on each other now, we have already survived this long together.” *(not new: reassurance)* (one of 14 options). Feeling: *deeply anxious*. Reason: “I need to stop this bickering before it tears our family apart for good.” Suspects: Mara, so suspicion Mara 3/3. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's guilt, now 3 of 3: Leo reassured her.*

**min 36** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Leo). Social moment: Leo reassures you: "Daniel, she already admitted it once and there is no point dragging this out further."; Elena reassures everyone: "Let us not turn on each other now, we have already survived this long together.". **Chose: stay put and say nothing** (one of 15 options). Feeling: *overwhelmed*. Reason: “I cannot take the pressure anymore and just need to stay quiet and still.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3; kept: Elena 1/3. Came of it: stayed where they were.
- **Elena, minutes 36–87 (18 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone: "Daniel, I already told you everything I know, I don't know what else you want me to say."; Leo reassures Mara: "Daniel, she already admitted it once and there is no point dragging this out further."; Elena reassures everyone: "Let us not turn on each other now, we have already survived this long together.". **Chose: accuse Mara of taking it**, saying “You still took that extra can in the night, Mara, and nobody has accounted for where it went.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *famished*. Reason: “She took the food in the night and I need her to admit the full truth.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Elena 1/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let us not turn on each other now, we have already survived this long together."; Daniel accuses Mara of taking it: "You still took that extra can in the night, Mara, and nobody has accounted for where it went.". **Chose: reassure Mara**, saying “Daniel, dropping it now is the only sensible option we have left.” *(not new: reassurance)* (one of 13 options). Feeling: *annoyed*. Reason: “Daniel keeps bringing up the same issue even after Mara admitted it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- *Mara's guilt, now 3 of 3: Leo reassured her.*
- *The kitchen's conversation ends (minute 39): 2 full turns in a row with nothing new.*

**min 39** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Leo). **Inner moment**, nothing social happening: grudge against Daniel rose (now 3 of 3). **Chose: reassure everyone here**, saying “I'm so sorry, I really didn't mean to cause all of this.” *(not new: reassurance)* (one of 14 options). Feeling: *guilty*. Reason: “I cannot stand everyone fighting because of me when I already confessed.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3; kept: Elena 1/3. Came of it: said to Daniel, Elena, Leo.
- **Leo, minutes 39–87 (17 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 39–63 (9 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 42** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 42–51 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 11 options). Feeling: *exhausted*. Reason: “I have nothing left to say after all of this, so I will just stay quiet.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3; grudge against Elena fell to 0/3. Came of it: stayed where they were.

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: accuse Mara of taking it**, saying “Mara, you still haven't explained where that can went, and we deserve the truth.” *(not new: an accusation they had made before)* (one of 14 options). Feeling: *starving*. Reason: “I cannot let this go until someone confesses because my stomach is empty and someone stole from us.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; grudge against Elena fell to 0/3. Came of it: said to Elena, Leo, Mara.

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Mara admits taking it, to everyone: "I took it in the night. I was so hungry, I am sorry." *(new: a confession)*
- min 00, kitchen. Elena reassures Mara: "It is alright, my sweet girl, we are all so hungry and we will get through this." *(not new: reassurance)*
- min 00, kitchen. Daniel accuses Mara of taking it: "You cannot just take things in the night, Mara, we all have to survive this together." *(new: an accusation)*
- min 00, kitchen. Leo reassures Mara: "It is alright, Mara, you owned up to it, and we are all hungry." *(not new: reassurance)*
- min 03, kitchen. Mara reassures everyone: "I really am sorry, I promise I won't do it again." *(not new: reassurance)*
- min 03, kitchen. Elena reassures everyone: "Let us not fight among ourselves, we only have each other to rely on right now." *(not new: reassurance)*
- min 03, kitchen. Daniel reassures Mara: "I am sorry for snapping, Mara, we just need to stick together through this." *(not new: reassurance)*
- min 06, kitchen. Daniel reassures everyone: "We are going to make it through this day if we just keep our heads." *(not new: reassurance)*
- min 15, kitchen. Leo says to everyone, while eating: "We need to eat something before we lose our strength." *(not new: a remark (the rules cannot tell what free words add))*
- min 18, kitchen. Daniel accuses Mara of taking it: "You still took that extra one, Mara, and we cannot afford your selfishness right now." *(not new: an accusation they had made before)*
- min 21, kitchen. Mara reassures Daniel: "Daniel, please don't look at me like that, I didn't mean to hurt anyone." *(not new: reassurance)*
- min 21, kitchen. Daniel accuses Mara of taking it: "You can't just take food and expect us to pretend it didn't happen, Mara." *(not new: an accusation they had made before)*
- min 21, kitchen. Leo reassures Mara: "Mara already admitted it and apologized, Daniel, so there is no point keeping on about it." *(not new: reassurance)*
- min 21, kitchen. Elena reassures everyone: "Let us stop arguing now, we cannot let hunger tear our family apart." *(not new: reassurance)*
- min 30, kitchen. Elena says to everyone, while eating: "I must eat something, or I will not have the strength to hold us together." *(not new: a remark (the rules cannot tell what free words add))*
- min 30, kitchen. Daniel accuses Mara of taking it: "Mara, you started all of this by taking that can, and it's time you owned up to it." *(not new: an accusation they had made before)*
- min 30, kitchen. Mara reassures Daniel: "Daniel, I already told you I am sorry, please stop looking at me like that." *(not new: reassurance)*
- min 33, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't explained why you lied about the whole thing in the first place." *(not new: an accusation they had made before)*
- min 33, kitchen. Mara says to everyone: "Daniel, I already told you everything I know, I don't know what else you want me to say." *(not new: a remark (the rules cannot tell what free words add))*
- min 33, kitchen. Leo reassures Mara: "Daniel, she already admitted it once and there is no point dragging this out further." *(not new: reassurance)*
- min 33, kitchen. Elena reassures everyone: "Let us not turn on each other now, we have already survived this long together." *(not new: reassurance)*
- min 36, kitchen. Daniel accuses Mara of taking it: "You still took that extra can in the night, Mara, and nobody has accounted for where it went." *(not new: an accusation they had made before)*
- min 36, kitchen. Leo reassures Mara: "Daniel, dropping it now is the only sensible option we have left." *(not new: reassurance)*
- min 39, kitchen. Mara reassures everyone: "I'm so sorry, I really didn't mean to cause all of this." *(not new: reassurance)*
- min 66, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't explained where that can went, and we deserve the truth." *(not new: an accusation they had made before)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 0 of 2 portions left; eaten this morning: Elena 1, Leo 1.

- Who admitted taking it: Mara at minute 00.
- Accusations: Daniel accused Mara (minute 00); Daniel accused Mara (minute 18); Daniel accused Mara (minute 21); Daniel accused Mara (minute 30); Daniel accused Mara (minute 33); Daniel accused Mara (minute 36); Daniel accused Mara (minute 66).
- Who else knows Mara took it: Daniel, Elena, Leo.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 09 (2 full turns in a row with nothing new); kitchen started at minute 15 (Leo ate one of the portions); kitchen ended at minute 24 (2 full turns in a row with nothing new); kitchen started at minute 30 (Elena ate one of the portions); kitchen ended at minute 39 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects Mara 3/3 | suspects Mara 3/3 | suspects none |
| Grudges | Mara 3/3 | none | Daniel 3/3 | Daniel 3/3 |
| Hunger | starving | hungry | a little hungry | very hungry |
| Guilt | - | - | - | 3/3 |

The events behind each grudge still held at minute 90, and behind Mara's guilt:

- Daniel against Mara (3/3): you were angry with Mara at minutes 18, 21, 24, 30, 33, 36 and 66.
- Leo against Daniel (3/3): you were angry with Daniel at minutes 21, 24, 33 and 36.
- Mara against Daniel (3/3): you were angry with Daniel at minutes 30, 33, 36, 39 and 54.
- Mara's guilt (3/3): she ate the can in the night, and nobody saw; Elena reassured you, at minute 00; Leo reassured you, at minute 00; Daniel reassured you, at minute 03; Leo reassured you, at minute 21; Leo reassured you, at minute 33; Leo reassured you, at minute 36.

- The last feeling each of them named: Daniel *starving* (minute 66); Elena *deeply anxious* (minute 33); Leo *annoyed* (minute 36); Mara *exhausted* (minute 54).


### miscount, Flash Lite, seed 1

#### The morning as a story: miscount, rules and a language model, seed 1

Generated by `python morning.py --scenario miscount --seed 1` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 56 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 64 routine ones settled by the rules. 41 lines were spoken aloud, 7 of them new. Conversations ended 3 times. 8 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3); nobody took the can, so nobody carries guilt. The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Guilt**: in this scenario nobody took the can, so nobody carries guilt and nobody is offered *admit taking it*.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “Who took the can? Someone has to explain this right now.” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to find out who took the food before things get completely out of hand.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calmly observant*. Reason: “Yelling won't find the can, so I am watching everyone's reaction first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now.". **Chose: reassure everyone here**, saying “Let us calm down, no one here would steal from their own family.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I must keep them from turning on each other before this house tears itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now."; Elena reassures everyone: "Let us calm down, no one here would steal from their own family.". **Chose: deny taking it**, saying “I didn't take it! Why is everyone looking at me?” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I need to speak up immediately so nobody thinks I am the one who stole the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel searching the kitchen, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me?". **Chose: reassure everyone here**, saying “Let us not turn on each other, we will get through this together.” *(not new: reassurance)* (one of 23 options). Feeling: *deeply anxious*. Reason: “I must keep the family from tearing itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us calm down, no one here would steal from their own family."; Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me?"; Elena reassures everyone: "Let us not turn on each other, we will get through this together.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calmly observant*. Reason: “I prefer to watch how everyone reacts before saying anything more.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us not turn on each other, we will get through this together.". **Chose: deny taking it**, saying “I didn't take anything, I promise you I didn't!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *defensive*. Reason: “I have to keep telling them it wasn't me because they are all looking at me like I am a liar.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let us calm down, no one here would steal from their own family."; Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me?"; Elena reassures everyone: "Let us not turn on each other, we will get through this together."; Mara denies taking it, to everyone: "I didn't take anything, I promise you I didn't!". **Chose: search the kitchen for the can (takes about six minutes)**, saying “I am going to tear this kitchen apart until I find it.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “Someone must have hidden the can here, and I will find it myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 06** · kitchen: Daniel standing, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything, I promise you I didn't!"; Daniel says to everyone, while searching: "I am going to tear this kitchen apart until I find it.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calm*. Reason: “Watching them tear themselves apart achieves nothing right now.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel says to everyone, while searching: "I am going to tear this kitchen apart until I find it.". **Chose: ask everyone here who took the can**, saying “If nobody took it, then where did it go? Someone has to know!” *(new: a question)* (one of 21 options). Feeling: *panicked*. Reason: “I am desperate for them to stop looking at me like I stole it, so I need someone else to answer.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything, I promise you I didn't!"; Daniel says to everyone, while searching: "I am going to tear this kitchen apart until I find it."; Mara asks everyone who took the can: "If nobody took it, then where did it go? Someone has to know!"; Mara looks panicked. **Chose: stay put and say nothing** (one of 20 options). Feeling: *deeply anxious*. Reason: “I cannot keep reassuring them when tension is rising like this, so I must stay quiet and watch.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara asks everyone who took the can: "If nobody took it, then where did it go? Someone has to know!"; Mara looks panicked. **Chose: carry on searching the kitchen**, saying “I haven't checked behind the tins yet, I am keeping on with this.” *(not new: a remark (the rules cannot tell what free words add))* (one of 20 options). Feeling: *anxious*. Reason: “I have to find the missing can myself or no one will.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.

**min 09** · kitchen: Daniel talking, Elena talking, Leo searching the kitchen, Mara searching the kitchen · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (panicked)). Social moment: Daniel says to everyone, while searching: "I haven't checked behind the tins yet, I am keeping on with this."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: search the kitchen for the can (takes about six minutes)**, saying “I will help look, I want to prove it wasn't me.” *(not new: a remark (the rules cannot tell what free words add))* (one of 23 options). Feeling: *anxious*. Reason: “I need to search so they stop looking at me like I am the one who stole it.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: started going through the room.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara asks everyone who took the can: "If nobody took it, then where did it go? Someone has to know!"; Daniel says to everyone, while searching: "I haven't checked behind the tins yet, I am keeping on with this."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I will help look, I want to prove it wasn't me.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 21 options). Feeling: *calm*. Reason: “Standing around arguing will not find the missing can, so I should look myself.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara says to everyone, while searching: "I will help look, I want to prove it wasn't me.". **Chose: ask everyone here who took the can**, saying “Who took the can? Someone needs to explain this right now.” *(not new: a question they had asked before)* (one of 18 options). Feeling: *anxious*. Reason: “I need to get to the bottom of this and find out who has the food before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel says to everyone, while searching: "I haven't checked behind the tins yet, I am keeping on with this."; Daniel finishes going through the kitchen: no can, nothing out of place; Mara says to everyone, while searching: "I will help look, I want to prove it wasn't me."; Daniel asks everyone who took the can: "Who took the can? Someone needs to explain this right now.". **Chose: reassure everyone here**, saying “Let us stop shouting at each other, accusing one another will only tear us apart.” *(not new: reassurance)* (one of 18 options). Feeling: *deeply anxious*. Reason: “I must keep them from turning on each other before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 12** · kitchen: Daniel talking, Elena talking, Leo standing, Mara standing · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us stop shouting at each other, accusing one another will only tear us apart.". **Chose: ask everyone here who took the can**, saying “Someone needs to answer me right now, I want to know who took it.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I have to keep pressing them until someone tells me the truth about the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Who took the can? Someone needs to explain this right now."; Elena reassures everyone: "Let us stop shouting at each other, accusing one another will only tear us apart."; Daniel asks everyone who took the can: "Someone needs to answer me right now, I want to know who took it.". **Chose: ask everyone here who took the can**, saying “Why are you all looking at me like that? Just tell me who actually took it!” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to make them understand that I had nothing to do with it and find out who is lying.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone needs to answer me right now, I want to know who took it."; Mara asks everyone who took the can: "Why are you all looking at me like that? Just tell me who actually took it!". **Chose: reassure everyone here**, saying “Let us take a breath and stay calm, we will figure this out together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I must keep everyone from turning on each other and tearing our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "Who took the can? Someone needs to explain this right now."; Elena reassures everyone: "Let us stop shouting at each other, accusing one another will only tear us apart."; Daniel asks everyone who took the can: "Someone needs to answer me right now, I want to know who took it."; Mara asks everyone who took the can: "Why are you all looking at me like that? Just tell me who actually took it!"; Elena reassures everyone: "Let us take a breath and stay calm, we will figure this out together.". **Chose: reassure Mara**, saying “Mara, stop panicking, nobody is accusing you.” *(not new: reassurance)* (one of 20 options). Feeling: *calm*. Reason: “She is getting too defensive and needs to settle down before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation ends (minute 15): 2 full turns in a row with nothing new.*

**min 15** · kitchen: Daniel talking, Elena searching the kitchen, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Leo). **Inner moment**, nothing social happening: grudge against Daniel rose (now 3 of 3). **Chose: accuse Daniel of taking it**, saying “Daniel emptied my bag before, he is the one who goes through our things!” *(new: an accusation)* (one of 22 options). Feeling: *resentful*. Reason: “Daniel always treats me like a criminal and he went through my bag, so he probably took the can.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Mara asks everyone who took the can: "Why are you all looking at me like that? Just tell me who actually took it!"; Elena reassures everyone: "Let us take a breath and stay calm, we will figure this out together."; Leo reassures Mara: "Mara, stop panicking, nobody is accusing you."; Mara accuses you of taking it: "Daniel emptied my bag before, he is the one who goes through our things!". **Chose: deny taking it**, saying “I didn't take anything, Mara, so stop trying to turn this around on me.” *(new: a denial of a new accusation)* (one of 21 options). Feeling: *defensive*. Reason: “I have to defend myself against Mara's baseless accusation so nobody gets the wrong idea about me.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel emptied my bag before, he is the one who goes through our things!"; Daniel denies taking it, to everyone: "I didn't take anything, Mara, so stop trying to turn this around on me.". **Chose: ask everyone here who took the can**, saying “Let's stop pointing fingers and figure out what actually happened to the can.” *(new: a question)* (one of 21 options). Feeling: *hungry*. Reason: “Accusing each other without proof gets us nowhere and only wastes our energy.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures Mara: "Mara, stop panicking, nobody is accusing you."; Mara accuses Daniel of taking it: "Daniel emptied my bag before, he is the one who goes through our things!"; Daniel denies taking it, to everyone: "I didn't take anything, Mara, so stop trying to turn this around on me."; Leo asks everyone who took the can: "Let's stop pointing fingers and figure out what actually happened to the can.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *anxious*. Reason: “I need to find the missing can myself before everyone starts tearing each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- *Daniel's grudge against Mara, now 1 of 3: Mara accused Daniel falsely.*
- *The kitchen's conversation starts (minute 15): Mara: an accusation.*

**min 18** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take anything, Mara, so stop trying to turn this around on me."; Leo asks everyone who took the can: "Let's stop pointing fingers and figure out what actually happened to the can."; Elena finishes going through the kitchen: no can, nothing out of place. **Chose: accuse Daniel of taking it**, saying “Daniel went through my things before, and he is definitely the one who took it!” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *deeply resentful*. Reason: “I know Daniel snoops through my bag so he must be the one who stole the can.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: just accused by Mara). Social moment: Leo asks everyone who took the can: "Let's stop pointing fingers and figure out what actually happened to the can."; Elena finishes going through the kitchen: no can, nothing out of place; Mara accuses you of taking it: "Daniel went through my things before, and he is definitely the one who took it!". **Chose: deny taking it**, saying “I didn't take it, Mara, and you need to stop making things up.” *(not new: a denial with no new accusation to answer)* (one of 19 options). Feeling: *indignant*. Reason: “I have to defend myself against Mara's lies so everyone knows I am innocent.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara accuses Daniel of taking it: "Daniel went through my things before, and he is definitely the one who took it!"; Daniel denies taking it, to everyone: "I didn't take it, Mara, and you need to stop making things up.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *hungry*. Reason: “Yelling won't help us find the truth or fill our stomachs.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 21** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take it, Mara, and you need to stop making things up.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I cannot keep fighting them when nobody is listening to me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "Daniel went through my things before, and he is definitely the one who took it!"; Daniel denies taking it, to everyone: "I didn't take it, Mara, and you need to stop making things up.". **Chose: reassure everyone here**, saying “Let us take a breath and stay calm, we will get through this together.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm and together before anger tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 24** · kitchen: Daniel talking, Elena staying put, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 23 options). Feeling: *hungry*. Reason: “I need to check the kitchen myself before anyone else starts making baseless accusations.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together.". **Chose: accuse Daniel of taking it**, saying “Daniel is the one who took it, I know he did!” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *anxious*. Reason: “I am certain Daniel took the can because he always goes through our things.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: just accused by Mara). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Mara accuses you of taking it: "Daniel is the one who took it, I know he did!". **Chose: deny taking it**, saying “I didn't take the can, Mara, and I won't have you lying about me again.” *(not new: a denial with no new accusation to answer)* (one of 17 options). Feeling: *furious*. Reason: “I have to defend myself against Mara's constant false accusations so everyone knows I am innocent.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *The kitchen's conversation ends (minute 27): 2 full turns in a row with nothing new.*

**min 27** · kitchen: Daniel staying put, Elena talking, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "Daniel is the one who took it, I know he did!"; Daniel denies taking it, to everyone: "I didn't take the can, Mara, and I won't have you lying about me again."; Leo finishes going through the kitchen: no can, nothing out of place; Daniel looks furious. **Chose: reassure everyone here**, saying “Let us take a breath and stay calm, we will get through this together.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I must keep everyone calm and prevent this family from tearing itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation starts (minute 27): Leo finished searching the kitchen and found nothing.*

**min 30** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: shows the strongest feeling here (furious)). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together.". **Chose: ask everyone here who took the can**, saying “We need to clear this up right now, so who actually took the can?” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to take charge and find out who is lying about the missing food.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "We need to clear this up right now, so who actually took the can?". **Chose: reassure everyone here**, saying “Let us take a breath and stay calm, we will get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *very anxious*. Reason: “I need to keep everyone calm so the family does not tear itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Daniel asks everyone who took the can: "We need to clear this up right now, so who actually took the can?". **Chose: ask everyone here who took the can**, saying “Let's stick to what we actually know instead of just guessing.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *calm*. Reason: “We need facts rather than accusations if we are going to sort this out.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Daniel asks everyone who took the can: "We need to clear this up right now, so who actually took the can?"; Leo asks everyone who took the can: "Let's stick to what we actually know instead of just guessing.". **Chose: accuse Daniel of taking it**, saying “Daniel is the one who took it, I saw how he went through my things!” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *resentful*. Reason: “I am certain Daniel took it because he always snoops through my bag and refuses to respect our things.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 33** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Leo asks everyone who took the can: "Let's stick to what we actually know instead of just guessing."; Mara accuses you of taking it: "Daniel is the one who took it, I saw how he went through my things!". **Chose: accuse Mara of taking it**, saying “Mara, you've been pointing fingers at me this whole time to hide the fact that you took it.” *(new: an accusation)* (one of 21 options). Feeling: *angry*. Reason: “She keeps blaming me for something I did not do, and I will not let her get away with it.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, you've been pointing fingers at me this whole time to hide the fact that you took it."; Daniel looks angry. **Chose: deny taking it**, saying “I didn't take it, Daniel is just saying that so nobody looks at him!” *(new: a denial of a new accusation)* (one of 21 options). Feeling: *frightened*. Reason: “I have to defend myself because Daniel is lying about me to cover for what he did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel is the one who took it, I saw how he went through my things!"; Daniel accuses Mara of taking it: "Mara, you've been pointing fingers at me this whole time to hide the fact that you took it."; Mara denies taking it, to everyone: "I didn't take it, Daniel is just saying that so nobody looks at him!"; Daniel looks angry; Mara looks frightened. **Chose: ask everyone here who took the can**, saying “Let's stick to the facts and figure out where the can actually went.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *calm*. Reason: “Accusations without evidence will only tear us apart when we need to stay rational.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo asks everyone who took the can: "Let's stick to what we actually know instead of just guessing."; Mara accuses Daniel of taking it: "Daniel is the one who took it, I saw how he went through my things!"; Daniel accuses Mara of taking it: "Mara, you've been pointing fingers at me this whole time to hide the fact that you took it."; Mara denies taking it, to everyone: "I didn't take it, Daniel is just saying that so nobody looks at him!"; Leo asks everyone who took the can: "Let's stick to the facts and figure out where the can actually went."; Daniel looks angry; Mara looks frightened. **Chose: reassure everyone here**, saying “Let us take a breath and stay calm, we will get through this together.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I must keep everyone calm because if we turn on each other, the family will fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 36** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, Daniel is just saying that so nobody looks at him!"; Leo asks everyone who took the can: "Let's stick to the facts and figure out where the can actually went."; Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Mara, you still haven't explained why you're so desperate to pin this on me.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *defensive*. Reason: “I need to make sure she doesn't get away with deflecting the blame onto me.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo asks everyone who took the can: "Let's stick to the facts and figure out where the can actually went."; Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Daniel accuses you of taking it: "Mara, you still haven't explained why you're so desperate to pin this on me.". **Chose: deny taking it**, saying “I didn't take it, why are you always blaming me for everything?” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *indignant*. Reason: “I am innocent and it is completely unfair that Daniel keeps accusing me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to pin this on me."; Mara denies taking it, to everyone: "I didn't take it, why are you always blaming me for everything?". Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 16 options). Feeling: *deeply anxious*. Reason: “I cannot bear to accuse any of my children when we are all falling apart inside.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together."; Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to pin this on me."; Mara denies taking it, to everyone: "I didn't take it, why are you always blaming me for everything?". **Chose: stay put and say nothing** (one of 19 options). Feeling: *hungry*. Reason: “Letting them argue in circles gets us nowhere, so I'll stay quiet and watch.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 39** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, why are you always blaming me for everything?". **Chose: accuse Mara of taking it**, saying “Mara, stop playing games and just admit you took the can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *frustrated*. Reason: “She keeps deflecting and pointing fingers at me to cover her own tracks.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, stop playing games and just admit you took the can.". **Chose: deny taking it**, saying “I didn't take it, stop treating me like a child!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *frightened*. Reason: “I have to defend myself because Daniel keeps accusing me unfairly.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, stop playing games and just admit you took the can."; Mara denies taking it, to everyone: "I didn't take it, stop treating me like a child!"; Mara looks frightened. **Chose: reassure everyone here**, saying “Let us not turn on each other, we will figure this out together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and prevent the family from tearing itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, stop playing games and just admit you took the can."; Mara denies taking it, to everyone: "I didn't take it, stop treating me like a child!"; Elena reassures everyone: "Let us not turn on each other, we will figure this out together."; Mara looks frightened. **Chose: reassure Mara**, saying “Mara, nobody here thinks you did it, just take a breath.” *(not new: reassurance)* (one of 19 options). Feeling: *hungry*. Reason: “She is frightened and being ganged up on, so I need to calm her down.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation ends (minute 42): 2 full turns in a row with nothing new.*

**min 42** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 42–51 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 17 options). Feeling: *tense*. Reason: “I need to watch Mara closely now to see if she cracks under the silence.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). **Chose: stay put and say nothing** (one of 20 options). Feeling: *hungry*. Reason: “I will stay quiet and watch how everyone reacts before saying anything more.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.
- **Elena, minutes 42–72 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 45** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 45–48 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 45–63 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 51** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 2 of 3). **Chose: stay put and say nothing** (one of 22 options). Feeling: *hungry*. Reason: “I want to see if someone else cracks before I waste any more energy talking in circles.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: stayed where they were.

**min 54** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo, minutes 54–60 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “Daniel is the one who keeps accusing me, he must have taken it!” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *furious*. Reason: “I am sick of him constantly pointing the finger at me while he hides what he did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–87 (11 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: stay put and say nothing** (one of 20 options). Feeling: *very hungry*. Reason: “Accusing anyone without proof will only make the tension worse.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Daniel fell to 1/3. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: accuse Mara of taking it**, saying “Mara, your silence speaks volumes, you took the can and you know it.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *anxious*. Reason: “I refuse to let her keep deflecting when I know she is the one responsible.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo, minutes 66–87 (8 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 69–87 (7 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel staying put, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Let us not turn on each other, we will figure this out together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I must keep the peace between them before they tear our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Daniel asks everyone who took the can: "Who took the can? Someone has to explain this right now." *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Let us calm down, no one here would steal from their own family." *(not new: reassurance)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it! Why is everyone looking at me?" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Let us not turn on each other, we will get through this together." *(not new: reassurance)*
- min 03, kitchen. Mara denies taking it, to everyone: "I didn't take anything, I promise you I didn't!" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Daniel says to everyone, while searching: "I am going to tear this kitchen apart until I find it." *(not new: a remark (the rules cannot tell what free words add))*
- min 06, kitchen. Mara asks everyone who took the can: "If nobody took it, then where did it go? Someone has to know!" *(new: a question)*
- min 06, kitchen. Daniel says to everyone, while searching: "I haven't checked behind the tins yet, I am keeping on with this." *(not new: a remark (the rules cannot tell what free words add))*
- min 09, kitchen. Mara says to everyone, while searching: "I will help look, I want to prove it wasn't me." *(not new: a remark (the rules cannot tell what free words add))*
- min 09, kitchen. Daniel asks everyone who took the can: "Who took the can? Someone needs to explain this right now." *(not new: a question they had asked before)*
- min 09, kitchen. Elena reassures everyone: "Let us stop shouting at each other, accusing one another will only tear us apart." *(not new: reassurance)*
- min 12, kitchen. Daniel asks everyone who took the can: "Someone needs to answer me right now, I want to know who took it." *(not new: a question they had asked before)*
- min 12, kitchen. Mara asks everyone who took the can: "Why are you all looking at me like that? Just tell me who actually took it!" *(not new: a question they had asked before)*
- min 12, kitchen. Elena reassures everyone: "Let us take a breath and stay calm, we will figure this out together." *(not new: reassurance)*
- min 12, kitchen. Leo reassures Mara: "Mara, stop panicking, nobody is accusing you." *(not new: reassurance)*
- min 15, kitchen. Mara accuses Daniel of taking it: "Daniel emptied my bag before, he is the one who goes through our things!" *(new: an accusation)*
- min 15, kitchen. Daniel denies taking it, to everyone: "I didn't take anything, Mara, so stop trying to turn this around on me." *(new: a denial of a new accusation)*
- min 15, kitchen. Leo asks everyone who took the can: "Let's stop pointing fingers and figure out what actually happened to the can." *(new: a question)*
- min 18, kitchen. Mara accuses Daniel of taking it: "Daniel went through my things before, and he is definitely the one who took it!" *(not new: an accusation they had made before)*
- min 18, kitchen. Daniel denies taking it, to everyone: "I didn't take it, Mara, and you need to stop making things up." *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together." *(not new: reassurance)*
- min 24, kitchen. Mara accuses Daniel of taking it: "Daniel is the one who took it, I know he did!" *(not new: an accusation they had made before)*
- min 24, kitchen. Daniel denies taking it, to everyone: "I didn't take the can, Mara, and I won't have you lying about me again." *(not new: a denial with no new accusation to answer)*
- min 27, kitchen. Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together." *(not new: reassurance)*
- min 30, kitchen. Daniel asks everyone who took the can: "We need to clear this up right now, so who actually took the can?" *(not new: a question they had asked before)*
- min 30, kitchen. Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together." *(not new: reassurance)*
- min 30, kitchen. Leo asks everyone who took the can: "Let's stick to what we actually know instead of just guessing." *(not new: a question they had asked before)*
- min 30, kitchen. Mara accuses Daniel of taking it: "Daniel is the one who took it, I saw how he went through my things!" *(not new: an accusation they had made before)*
- min 33, kitchen. Daniel accuses Mara of taking it: "Mara, you've been pointing fingers at me this whole time to hide the fact that you took it." *(new: an accusation)*
- min 33, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel is just saying that so nobody looks at him!" *(new: a denial of a new accusation)*
- min 33, kitchen. Leo asks everyone who took the can: "Let's stick to the facts and figure out where the can actually went." *(not new: a question they had asked before)*
- min 33, kitchen. Elena reassures everyone: "Let us take a breath and stay calm, we will get through this together." *(not new: reassurance)*
- min 36, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to pin this on me." *(not new: an accusation they had made before)*
- min 36, kitchen. Mara denies taking it, to everyone: "I didn't take it, why are you always blaming me for everything?" *(not new: a denial with no new accusation to answer)*
- min 39, kitchen. Daniel accuses Mara of taking it: "Mara, stop playing games and just admit you took the can." *(not new: an accusation they had made before)*
- min 39, kitchen. Mara denies taking it, to everyone: "I didn't take it, stop treating me like a child!" *(not new: a denial with no new accusation to answer)*
- min 39, kitchen. Elena reassures everyone: "Let us not turn on each other, we will figure this out together." *(not new: reassurance)*
- min 39, kitchen. Leo reassures Mara: "Mara, nobody here thinks you did it, just take a breath." *(not new: reassurance)*
- min 54, kitchen. Mara accuses Daniel of taking it: "Daniel is the one who keeps accusing me, he must have taken it!" *(not new: an accusation they had made before)*
- min 66, kitchen. Daniel accuses Mara of taking it: "Mara, your silence speaks volumes, you took the can and you know it." *(not new: an accusation they had made before)*
- min 75, kitchen. Elena reassures everyone: "Let us not turn on each other, we will figure this out together." *(not new: reassurance)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Mara accused Daniel (minute 15); Mara accused Daniel (minute 18); Mara accused Daniel (minute 24); Mara accused Daniel (minute 30); Daniel accused Mara (minute 33); Daniel accused Mara (minute 36); Daniel accused Mara (minute 39); Mara accused Daniel (minute 54); Daniel accused Mara (minute 66).
- Nobody took the can: the count was wrong from the start.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 15 (2 full turns in a row with nothing new); kitchen started at minute 15 (Mara: an accusation); kitchen ended at minute 27 (2 full turns in a row with nothing new); kitchen started at minute 27 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 42 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects none | suspects none | suspects Daniel 3/3 |
| Grudges | Mara 3/3 | none | Daniel 1/3 | Daniel 3/3 |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | - | - | - | - |

The events behind each grudge still held at minute 90:

- Daniel against Mara (3/3): Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 54, and you had not; you were angry with Mara at minutes 15, 18, 24, 30, 33, 36, 39, 42 and 66.
- Leo against Daniel (1/3): you were angry with Daniel at minutes 39 and 42.
- Mara against Daniel (3/3): Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 66, and you had not; you were angry with Daniel at minutes 06, 09, 12, 15, 18, 21, 24, 30, 33, 36, 39 and 54.

- The last feeling each of them named: Daniel *anxious* (minute 66); Elena *deeply anxious* (minute 75); Leo *very hungry* (minute 63); Mara *furious* (minute 54).


### miscount, Flash Lite, seed 2

#### The morning as a story: miscount, rules and a language model, seed 2

Generated by `python morning.py --scenario miscount --seed 2` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 93 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 27 routine ones settled by the rules. 81 lines were spoken aloud, 9 of them new. Conversations ended 5 times. 9 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3); nobody took the can, so nobody carries guilt. The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Guilt**: in this scenario nobody took the can, so nobody carries guilt and nobody is offered *admit taking it*.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “A can is missing from the shelf. Did one of you take it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know what happened to the food before this breaks us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?". **Chose: deny taking it**, saying “I didn't take it, I swear I didn't!” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *scared*. Reason: “I need them to know I am innocent before they start blaming me.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Mara looks scared. **Chose: ask everyone here who took the can**, saying “Someone here knows where it is. Tell me right now who took it.” *(new: a question)* (one of 21 options). Feeling: *anxious*. Reason: “I need to find out who is lying before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?"; Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel asks everyone who took the can: "Someone here knows where it is. Tell me right now who took it."; Mara looks scared. **Chose: deny taking it**, saying “I didn't take the can, and shouting at each other won't bring it back.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *calm*. Reason: “There is no proof against anyone yet, so I need to deny taking it and keep the peace.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (scared)). Social moment: Daniel asks everyone who took the can: "Someone here knows where it is. Tell me right now who took it."; Leo denies taking it, to everyone: "I didn't take the can, and shouting at each other won't bring it back.". **Chose: deny taking it**, saying “I already told you, I didn't take anything!” *(not new: a denial with no new accusation to answer)* (one of 23 options). Feeling: *anxious*. Reason: “I have to keep defending myself because nobody believes me.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!"; Daniel asks everyone who took the can: "Someone here knows where it is. Tell me right now who took it."; Leo denies taking it, to everyone: "I didn't take the can, and shouting at each other won't bring it back."; Mara denies taking it, to everyone: "I already told you, I didn't take anything!". **Chose: reassure everyone here**, saying “Let's all calm down, we are going to get through this together without turning on each other.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to stop this shouting before the family tears itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take anything!"; Elena reassures everyone: "Let's all calm down, we are going to get through this together without turning on each other.". **Chose: reassure everyone here**, saying “Let's listen to Mom and stop accusing each other before we tear ourselves apart.” *(not new: reassurance)* (one of 21 options). Feeling: *composed*. Reason: “Turning on each other is a greater threat right now than the missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo denies taking it, to everyone: "I didn't take the can, and shouting at each other won't bring it back."; Mara denies taking it, to everyone: "I already told you, I didn't take anything!"; Elena reassures everyone: "Let's all calm down, we are going to get through this together without turning on each other."; Leo reassures everyone: "Let's listen to Mom and stop accusing each other before we tear ourselves apart.". **Chose: ask everyone here who took the can**, saying “We are not letting this drop until someone owns up to it.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I need to know the truth before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 06** · kitchen: Daniel staying put, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all calm down, we are going to get through this together without turning on each other."; Leo reassures everyone: "Let's listen to Mom and stop accusing each other before we tear ourselves apart."; Daniel asks everyone who took the can: "We are not letting this drop until someone owns up to it.". **Chose: accuse Daniel of taking it**, saying “Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!” *(new: an accusation)* (one of 22 options). Feeling: *resentful*. Reason: “I am sick of Daniel treating me like a criminal when he acts so suspicious himself.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo reassures everyone: "Let's listen to Mom and stop accusing each other before we tear ourselves apart."; Daniel asks everyone who took the can: "We are not letting this drop until someone owns up to it."; Mara accuses Daniel of taking it: "Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!". **Chose: reassure everyone here**, saying “Let's not accuse each other, we are family and we will figure this out together.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I need to stop the arguments before they tear the family apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "We are not letting this drop until someone owns up to it."; Mara accuses Daniel of taking it: "Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!"; Elena reassures everyone: "Let's not accuse each other, we are family and we will figure this out together.". **Chose: reassure everyone here**, saying “Mara, searching bags won't help, and neither will pointing fingers at each other.” *(not new: reassurance)* (one of 20 options). Feeling: *composed*. Reason: “I need to keep everyone calm before this argument spirals out of control.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Daniel's grudge against Mara, now 1 of 3: Mara accused Daniel falsely.*

**min 09** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!"; Elena reassures everyone: "Let's not accuse each other, we are family and we will figure this out together."; Leo reassures everyone: "Mara, searching bags won't help, and neither will pointing fingers at each other.". **Chose: deny taking it**, saying “I didn't take any can, and it's insulting that any of you would even think I did.” *(new: a denial of a new accusation)* (one of 23 options). Feeling: *defensive*. Reason: “I need to clear my name immediately so they don't buy into Mara's baseless accusation.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's not accuse each other, we are family and we will figure this out together."; Leo reassures everyone: "Mara, searching bags won't help, and neither will pointing fingers at each other."; Daniel denies taking it, to everyone: "I didn't take any can, and it's insulting that any of you would even think I did.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *overwhelmed*. Reason: “I have already said what I think and no one is listening to me.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel denies taking it, to everyone: "I didn't take any can, and it's insulting that any of you would even think I did.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *wary*. Reason: “I prefer to observe how everyone reacts before speaking again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures everyone: "Mara, searching bags won't help, and neither will pointing fingers at each other."; Daniel denies taking it, to everyone: "I didn't take any can, and it's insulting that any of you would even think I did.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *deeply anxious*. Reason: “I cannot keep reassuring them when the tension is rising this high and no one is confessing.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 12** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 2 of 3); grudge against Daniel rose (now 3 of 3). **Chose: stay put and say nothing** (one of 22 options). Feeling: *anxious*. Reason: “I am too overwhelmed to say anything else right now with everyone watching me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Mara rose (now 2 of 3). **Chose: ask everyone here who took the can**, saying “Nobody is moving until we figure out who took that can.” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep control of the situation and find out who is lying.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara rose to 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "Nobody is moving until we figure out who took that can.". **Chose: reassure everyone here**, saying “Let's not let fear turn us against one another, we have to stay calm.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone from turning on each other before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.

**min 15** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Nobody is moving until we figure out who took that can."; Elena reassures everyone: "Let's not let fear turn us against one another, we have to stay calm.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *resentful*. Reason: “I am sick of Daniel acting like he's above suspicion when he treated me like a criminal.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures everyone: "Let's not let fear turn us against one another, we have to stay calm."; Mara accuses you of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!". **Chose: accuse Mara of taking it**, saying “Stop deflecting, Mara, you're the one who keeps lying about this because you have something to hide.” *(new: an accusation)* (one of 21 options). Feeling: *furious*. Reason: “Mara keeps shifting the blame onto me to cover up her own guilt.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Nobody is moving until we figure out who took that can."; Elena reassures everyone: "Let's not let fear turn us against one another, we have to stay calm."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel accuses Mara of taking it: "Stop deflecting, Mara, you're the one who keeps lying about this because you have something to hide."; Daniel looks furious. **Chose: reassure everyone here**, saying “Arguing isn't going to fill our stomachs or find the missing can.” *(not new: reassurance)* (one of 21 options). Feeling: *calm*. Reason: “Accusing one another only makes the tension worse when we need to stay rational.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel accuses Mara of taking it: "Stop deflecting, Mara, you're the one who keeps lying about this because you have something to hide."; Leo reassures everyone: "Arguing isn't going to fill our stomachs or find the missing can."; Daniel looks furious. **Chose: reassure everyone here**, saying “Let's all just stop shouting at each other, screaming won't bring the food back.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep them from tearing each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 18** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Stop deflecting, Mara, you're the one who keeps lying about this because you have something to hide."; Leo reassures everyone: "Arguing isn't going to fill our stomachs or find the missing can."; Elena reassures everyone: "Let's all just stop shouting at each other, screaming won't bring the food back."; Daniel looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *frightened*. Reason: “I did not take the can and Daniel is just trying to pin it on me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Leo reassures everyone: "Arguing isn't going to fill our stomachs or find the missing can."; Elena reassures everyone: "Let's all just stop shouting at each other, screaming won't bring the food back."; Mara accuses you of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Stop lying about this right now, Mara, because I know it was you.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *defensive*. Reason: “I have to stand my ground and make her stop deflecting.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel accuses Mara of taking it: "Stop lying about this right now, Mara, because I know it was you."; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I have to keep everyone from tearing each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's all just stop shouting at each other, screaming won't bring the food back."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel accuses Mara of taking it: "Stop lying about this right now, Mara, because I know it was you."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back.” *(not new: reassurance)* (one of 20 options). Feeling: *calm*. Reason: “I need to keep everyone from turning on each other while we are all this hungry.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 21** · kitchen: Daniel talking, Elena talking, Leo searching the kitchen, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Stop lying about this right now, Mara, because I know it was you."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *frightened*. Reason: “I am sick of him treating me like a thief when I didn't do anything.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back."; Mara accuses you of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Mara looks frightened. **Chose: deny taking it**, saying “I didn't take anything, and I won't have you accusing me when I'm trying to protect us.” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *indignant*. Reason: “I need to firmly deny Mara's false accusations to regain control of the situation.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you accusing me when I'm trying to protect us."; Mara looks frightened. **Chose: search the kitchen for the can (takes about six minutes)** (one of 21 options). Feeling: *hungry*. Reason: “We keep arguing in circles without checking if the can was simply misplaced.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!"; Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you accusing me when I'm trying to protect us."; Mara looks frightened. Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: ask everyone here who took the can**, saying “Please, let's stop pointing fingers and tell me honestly if anyone knows where the can went.” *(not new: a question they had asked before)* (one of 15 options). Feeling: *deeply anxious*. Reason: “I need to know the truth without letting the children tear each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *The kitchen's conversation ends (minute 24): 2 full turns in a row with nothing new.*

**min 24** · kitchen: Daniel talking, Elena talking, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "Please, let's stop pointing fingers and tell me honestly if anyone knows where the can went."; Leo finishes going through the kitchen: no can, nothing out of place; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Open your bag right now, Mara, because we all know you're hiding the can.” *(not new: an accusation they had made before)* (one of 20 options). Feeling: *anxious*. Reason: “I have to make her confess so everyone sees I was right and we can be safe.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel accuses Mara of taking it: "Open your bag right now, Mara, because we all know you're hiding the can."; Mara looks frightened. **Chose: reassure Mara**, saying “Mara, nobody is going to force you to open anything, just stay close to me.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to protect Mara from Daniel's aggression before this family tears itself apart.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation starts (minute 24): Leo finished searching the kitchen and found nothing.*

**min 27** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel accuses you of taking it: "Open your bag right now, Mara, because we all know you're hiding the can."; Elena reassures you: "Mara, nobody is going to force you to open anything, just stay close to me.". **Chose: accuse Daniel of taking it**, saying “Daniel, you keep accusing me because you're the one who hid it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *furious*. Reason: “Daniel keeps blaming me over and over even though I did not touch the can.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures Mara: "Mara, nobody is going to force you to open anything, just stay close to me."; Mara accuses you of taking it: "Daniel, you keep accusing me because you're the one who hid it!"; Mara looks furious. **Chose: accuse Mara of taking it**, saying “Stop lying, Mara, I know it's you.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *angry*. Reason: “She keeps deflecting because she has the can in her bag.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who hid it!"; Daniel accuses Mara of taking it: "Stop lying, Mara, I know it's you."; Daniel looks angry; Mara looks furious. **Chose: reassure Mara**, saying “Mara, stay right here with me, no one is going to touch your things.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to protect Mara from Daniel's accusations and keep the peace.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Open your bag right now, Mara, because we all know you're hiding the can."; Elena reassures Mara: "Mara, nobody is going to force you to open anything, just stay close to me."; Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who hid it!"; Daniel accuses Mara of taking it: "Stop lying, Mara, I know it's you."; Elena reassures Mara: "Mara, stay right here with me, no one is going to touch your things."; Daniel looks angry; Mara looks furious. **Chose: reassure everyone here**, saying “Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this.” *(not new: reassurance)* (one of 19 options). Feeling: *calm*. Reason: “Shouting gets us nowhere, so I need to defuse the tension before it gets worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 30** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Daniel accuses you of taking it: "Stop lying, Mara, I know it's you."; Elena reassures you: "Mara, stay right here with me, no one is going to touch your things."; Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this."; Daniel looks angry. **Chose: accuse Daniel of taking it**, saying “Daniel, you keep accusing me because you're the one who took it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *frightened*. Reason: “He keeps pointing fingers at me so nobody looks at him.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures Mara: "Mara, stay right here with me, no one is going to touch your things."; Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this."; Mara accuses you of taking it: "Daniel, you keep accusing me because you're the one who took it!"; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Don't turn this around on me, Mara, we all saw you looking shifty.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *defensive*. Reason: “I refuse to let her shift the blame away from herself when she clearly has the can.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!"; Daniel accuses Mara of taking it: "Don't turn this around on me, Mara, we all saw you looking shifty."; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back.” *(not new: reassurance)* (one of 20 options). Feeling: *calm*. Reason: “Accusing one another blindly only creates more friction when we need to stay level-headed.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this."; Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!"; Daniel accuses Mara of taking it: "Don't turn this around on me, Mara, we all saw you looking shifty."; Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back."; Mara looks frightened. **Chose: reassure everyone here**, saying “Please, we cannot turn on each other like this, we have to stay together.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to stop the shouting before this family tears itself apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation ends (minute 33): 2 full turns in a row with nothing new.*

**min 33** · kitchen: Daniel searching the kitchen, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 33–36 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: search the kitchen for the can (takes about six minutes)** (one of 16 options). Feeling: *frustrated hunger*. Reason: “I am sick of the arguing and I will prove once and for all that someone here is hiding the can.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: started going through the room.

**min 36** · kitchen: Daniel standing, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place; Mara looks frightened. **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “Watching Daniel tear the kitchen apart won't find the can, but letting him exhaust himself might.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place; Mara looks frightened. **Chose: reassure Mara**, saying “Mara, stay close to me, everything is going to be alright.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I need to keep Mara calm and prevent the family from falling apart while Daniel searches.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- *The kitchen's conversation starts (minute 36): Daniel finished searching the kitchen and found nothing.*

**min 39** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just spoken to by Elena). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place; Elena reassures you: "Mara, stay close to me, everything is going to be alright.". **Chose: accuse Daniel of taking it**, saying “Daniel, you keep accusing me because you're the one who took it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *resentful*. Reason: “He keeps blaming me for something I did not do, so he has to be the guilty one.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena reassures Mara: "Mara, stay close to me, everything is going to be alright."; Mara accuses you of taking it: "Daniel, you keep accusing me because you're the one who took it!". **Chose: deny taking it**, saying “I didn't take anything, and I'm sick of you trying to pin this on me, Mara.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *indignant*. Reason: “I have to stand my ground and prove to everyone that I am innocent of Mara's accusations.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!"; Daniel denies taking it, to everyone: "I didn't take anything, and I'm sick of you trying to pin this on me, Mara.". **Chose: reassure everyone here**, saying “Please stop fighting, we need to stay calm and protect each other.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I cannot bear to watch my family tear itself apart over this.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures Mara: "Mara, stay close to me, everything is going to be alright."; Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!"; Daniel denies taking it, to everyone: "I didn't take anything, and I'm sick of you trying to pin this on me, Mara."; Elena reassures everyone: "Please stop fighting, we need to stay calm and protect each other.". **Chose: reassure everyone here**, saying “Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this.” *(not new: reassurance)* (one of 19 options). Feeling: *hungry*. Reason: “Raising our voices will only drain what little energy we have left.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 42** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please stop fighting, we need to stay calm and protect each other."; Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this.". **Chose: accuse Mara of taking it**, saying “Stop hiding behind your excuses, Mara, because I know you're the one who stole the can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *furious*. Reason: “She keeps deflecting and pointing fingers, but I know she took it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel denies taking it, to everyone: "I didn't take anything, and I'm sick of you trying to pin this on me, Mara."; Elena reassures everyone: "Please stop fighting, we need to stay calm and protect each other."; Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this."; Daniel accuses you of taking it: "Stop hiding behind your excuses, Mara, because I know you're the one who stole the can."; Daniel looks furious. **Chose: deny taking it**, saying “I didn't take the can, Daniel, so stop saying that!” *(new: a denial of a new accusation)* (one of 21 options). Feeling: *very anxious*. Reason: “I am so tired of him lying and blaming me for something I never did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Stop hiding behind your excuses, Mara, because I know you're the one who stole the can."; Mara denies taking it, to everyone: "I didn't take the can, Daniel, so stop saying that!"; Daniel looks furious. **Chose: reassure everyone here**, saying “Let's all just breathe and stop shouting. Pointing fingers won't get us anywhere.” *(not new: reassurance)* (one of 20 options). Feeling: *calm*. Reason: “Raising our voices will only make things worse when we need to stay rational.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this."; Daniel accuses Mara of taking it: "Stop hiding behind your excuses, Mara, because I know you're the one who stole the can."; Mara denies taking it, to everyone: "I didn't take the can, Daniel, so stop saying that!"; Leo reassures everyone: "Let's all just breathe and stop shouting. Pointing fingers won't get us anywhere."; Daniel looks furious. **Chose: stay put and say nothing** (one of 20 options). Feeling: *deeply anxious*. Reason: “If I keep quiet and listen, maybe I can stop them from tearing each other apart before I have to step in.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Daniel fell to 1/3. Came of it: stayed where they were.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 45** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: shows the strongest feeling here (furious)). Social moment: Mara denies taking it, to everyone: "I didn't take the can, Daniel, so stop saying that!"; Leo reassures everyone: "Let's all just breathe and stop shouting. Pointing fingers won't get us anywhere.". **Chose: accuse Mara of taking it**, saying “Stop lying to us right now, Mara, because I know for a fact you took that can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *angry*. Reason: “She keeps deflecting and pointing fingers, but I am certain she is the one hiding the truth.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo reassures everyone: "Let's all just breathe and stop shouting. Pointing fingers won't get us anywhere."; Daniel accuses you of taking it: "Stop lying to us right now, Mara, because I know for a fact you took that can."; Daniel looks angry. **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps blaming me because you took it!” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *frightened*. Reason: “Daniel keeps falsely accusing me in front of everyone so I have to defend myself again.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Stop lying to us right now, Mara, because I know for a fact you took that can."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps blaming me because you took it!"; Daniel looks angry; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all just stop and listen. Yelling at each other isn't going to help us figure this out.” *(not new: reassurance)* (one of 20 options). Feeling: *calm*. Reason: “Arguing in circles will only make things worse when we need to stay level-headed.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Stop lying to us right now, Mara, because I know for a fact you took that can."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps blaming me because you took it!"; Leo reassures everyone: "Let's all just stop and listen. Yelling at each other isn't going to help us figure this out."; Daniel looks angry; Mara looks frightened. **Chose: reassure everyone here**, saying “Please stop, shouting at each other will only tear us apart when we need to stay strong.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I cannot bear to watch my family tear itself apart over accusations.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 48** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you're the one who keeps blaming me because you took it!"; Leo reassures everyone: "Let's all just stop and listen. Yelling at each other isn't going to help us figure this out."; Elena reassures everyone: "Please stop, shouting at each other will only tear us apart when we need to stay strong."; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “You keep pointing fingers at me, Mara, but you're the one who took that can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *angry*. Reason: “I have to keep everyone accountable and she is the most suspicious one here.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo reassures everyone: "Let's all just stop and listen. Yelling at each other isn't going to help us figure this out."; Elena reassures everyone: "Please stop, shouting at each other will only tear us apart when we need to stay strong."; Daniel accuses you of taking it: "You keep pointing fingers at me, Mara, but you're the one who took that can."; Daniel looks angry. **Chose: deny taking it**, saying “I didn't take it, Daniel, so stop saying that!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *anxious*. Reason: “I need to defend myself because Daniel keeps blaming me for something I did not do.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "You keep pointing fingers at me, Mara, but you're the one who took that can."; Mara denies taking it, to everyone: "I didn't take it, Daniel, so stop saying that!"; Daniel looks angry. **Chose: reassure everyone here**, saying “Please, let's not accuse each other, we have to trust one another to get through this.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I need to stop this shouting before it tears our family apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 1/3. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Please stop, shouting at each other will only tear us apart when we need to stay strong."; Daniel accuses Mara of taking it: "You keep pointing fingers at me, Mara, but you're the one who took that can."; Mara denies taking it, to everyone: "I didn't take it, Daniel, so stop saying that!"; Elena reassures everyone: "Please, let's not accuse each other, we have to trust one another to get through this."; Daniel looks angry. Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: ask everyone here who took the can**, saying “Can we all just state when we last saw the can instead of guessing?” *(new: a question)* (one of 15 options). Feeling: *calm*. Reason: “Accusing each other without facts accomplishes nothing useful.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 51** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: shows the strongest feeling here (angry)). Social moment: Mara denies taking it, to everyone: "I didn't take it, Daniel, so stop saying that!"; Elena reassures everyone: "Please, let's not accuse each other, we have to trust one another to get through this."; Leo asks everyone who took the can: "Can we all just state when we last saw the can instead of guessing?". Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: ask everyone here who took the can**, saying “Someone in this room has the can, so I want to know right now who actually took it.” *(not new: a question they had asked before)* (one of 18 options). Feeling: *anxious*. Reason: “I need to find out the truth and make sure everyone knows I had nothing to do with this theft.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo asks everyone who took the can: "Can we all just state when we last saw the can instead of guessing?"; Daniel asks everyone who took the can: "Someone in this room has the can, so I want to know right now who actually took it.". **Chose: reassure everyone here**, saying “Please stop fighting, we are all we have left and we must protect each other.” *(not new: reassurance)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to keep everyone calm and prevent the family from tearing itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 1/3. Came of it: said to Daniel, Leo, Mara.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please, let's not accuse each other, we have to trust one another to get through this."; Leo asks everyone who took the can: "Can we all just state when we last saw the can instead of guessing?"; Daniel asks everyone who took the can: "Someone in this room has the can, so I want to know right now who actually took it."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other.". **Chose: deny taking it**, saying “I already told you, I didn't take the can!” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I have to keep telling them the truth because Daniel won't stop accusing me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "Someone in this room has the can, so I want to know right now who actually took it."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Mara denies taking it, to everyone: "I already told you, I didn't take the can!". **Chose: reassure everyone here**, saying “Let's stay calm and keep talking this through without jumping to conclusions.” *(not new: reassurance)* (one of 19 options). Feeling: *calm*. Reason: “Keeping everyone calm is the best way to prevent the situation from boiling over.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.

**min 54** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Mara denies taking it, to everyone: "I already told you, I didn't take the can!"; Leo reassures everyone: "Let's stay calm and keep talking this through without jumping to conclusions.". **Chose: accuse Mara of taking it**, saying “Mara, stop playing games with us and admit you have the can right now.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *anxious*. Reason: “She has been deflecting and accusing me this whole time, and I know she is the one hiding it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo reassures everyone: "Let's stay calm and keep talking this through without jumping to conclusions."; Daniel accuses you of taking it: "Mara, stop playing games with us and admit you have the can right now.". **Chose: deny taking it**, saying “I didn't take it, Daniel, and I am sick of you always blaming me!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *frightened*. Reason: “I have to keep telling them the truth because I am innocent.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, stop playing games with us and admit you have the can right now."; Mara denies taking it, to everyone: "I didn't take it, Daniel, and I am sick of you always blaming me!"; Mara looks frightened. **Chose: reassure Mara**, saying “Mara, take a breath, nobody is going to let Daniel push you around.” *(not new: reassurance)* (one of 20 options). Feeling: *protective*. Reason: “Mara is terrified and Daniel's baseless aggression is only making the situation worse.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take the can!"; Leo reassures everyone: "Let's stay calm and keep talking this through without jumping to conclusions."; Daniel accuses Mara of taking it: "Mara, stop playing games with us and admit you have the can right now."; Mara denies taking it, to everyone: "I didn't take it, Daniel, and I am sick of you always blaming me!"; Leo reassures Mara: "Mara, take a breath, nobody is going to let Daniel push you around."; Mara looks frightened. Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 16 options). Feeling: *anxious*. Reason: “I cannot bear to accuse any of my children and risk tearing us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 1/3. Came of it: stayed where they were.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation ends (minute 57): 2 full turns in a row with nothing new.*

**min 57** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 57–66 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 57–63 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 57–66 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). **Chose: stay put and say nothing** (one of 19 options). Feeling: *wary*. Reason: “I will remain quiet for a moment to let the tension settle before speaking again.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.

**min 60** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 60–63 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: accuse Mara of taking it**, saying “Mara, I know it was you, so just give the can back before this gets any worse.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *famished*. Reason: “She has been deflecting and accusing me this whole time because she wants to hide her own guilt.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now very hungry); grudge against Daniel rose (now 2 of 3). **Chose: accuse Daniel of taking it**, saying “Daniel, accusing Mara without proof isn't helping anyone, which makes me think you're deflecting.” *(new: an accusation)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel is pushing too hard on Mara without any real evidence, which makes his own behavior suspicious.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Leo, now 1 of 3: Leo accused Daniel falsely.*
- *The kitchen's conversation starts (minute 66): Leo: an accusation.*

**min 69** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Leo accuses you of taking it: "Daniel, accusing Mara without proof isn't helping anyone, which makes me think you're deflecting.". **Chose: accuse Mara of taking it**, saying “Mara, you are the one who took it, so stop lying and hand it over right now.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *furious*. Reason: “I know she is hiding the can and I have to make her own up to it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, I know it was you, so just give the can back before this gets any worse."; Leo accuses Daniel of taking it: "Daniel, accusing Mara without proof isn't helping anyone, which makes me think you're deflecting."; Daniel accuses you of taking it: "Mara, you are the one who took it, so stop lying and hand it over right now."; Daniel looks furious. **Chose: deny taking it**, saying “I didn't take it, Daniel, I'm telling the truth!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *frightened*. Reason: “I have to make him stop accusing me when I did nothing wrong.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, I know it was you, so just give the can back before this gets any worse."; Leo accuses Daniel of taking it: "Daniel, accusing Mara without proof isn't helping anyone, which makes me think you're deflecting."; Daniel accuses Mara of taking it: "Mara, you are the one who took it, so stop lying and hand it over right now."; Mara denies taking it, to everyone: "I didn't take it, Daniel, I'm telling the truth!"; Daniel looks furious; Mara looks frightened. **Chose: reassure everyone here**, saying “Please stop fighting, we cannot let hunger turn us against one another.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I must keep everyone calm and prevent them from tearing our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Daniel fell to 0/3. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, you are the one who took it, so stop lying and hand it over right now."; Mara denies taking it, to everyone: "I didn't take it, Daniel, I'm telling the truth!"; Elena reassures everyone: "Please stop fighting, we cannot let hunger turn us against one another."; Daniel looks furious; Mara looks frightened. **Chose: accuse Daniel of taking it**, saying “Daniel, your temper right now doesn't prove anything except that you're hiding something.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *annoyed*. Reason: “Daniel is aggressively shifting blame onto Mara without any actual evidence.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Leo, now 2 of 3: Leo accused Daniel falsely.*

**min 72** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Mara denies taking it, to everyone: "I didn't take it, Daniel, I'm telling the truth!"; Elena reassures everyone: "Please stop fighting, we cannot let hunger turn us against one another."; Leo accuses you of taking it: "Daniel, your temper right now doesn't prove anything except that you're hiding something."; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Mara, stop lying to us right now and just give the can back where it belongs.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *anxious*. Reason: “I know Mara has the can, and she needs to hand it over before things get completely out of hand.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 2/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Elena reassures everyone: "Please stop fighting, we cannot let hunger turn us against one another."; Leo accuses Daniel of taking it: "Daniel, your temper right now doesn't prove anything except that you're hiding something."; Daniel accuses you of taking it: "Mara, stop lying to us right now and just give the can back where it belongs.". **Chose: deny taking it**, saying “I didn't take it, Daniel, stop accusing me!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *angry*. Reason: “I am furious that Daniel keeps blaming me for something I never did.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, stop lying to us right now and just give the can back where it belongs."; Mara denies taking it, to everyone: "I didn't take it, Daniel, stop accusing me!"; Mara looks angry. **Chose: accuse Daniel of taking it**, saying “Daniel, shouting at Mara won't hide the fact that you're the one who took it.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel keeps pushing the blame onto Mara to cover his own tracks.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo accuses Daniel of taking it: "Daniel, your temper right now doesn't prove anything except that you're hiding something."; Daniel accuses Mara of taking it: "Mara, stop lying to us right now and just give the can back where it belongs."; Mara denies taking it, to everyone: "I didn't take it, Daniel, stop accusing me!"; Leo accuses Daniel of taking it: "Daniel, shouting at Mara won't hide the fact that you're the one who took it."; Mara looks angry. **Chose: reassure everyone here**, saying “Please stop fighting, we are all we have left and we must protect each other.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I cannot bear to watch my children tear each other apart when staying united is all that keeps us alive.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Leo, now 3 of 3: Leo accused Daniel falsely.*
- *The kitchen's conversation ends (minute 75): 2 full turns in a row with nothing new.*

**min 75** · kitchen: Daniel talking, Elena searching the kitchen, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). **Inner moment**, nothing social happening: grudge against Leo rose (now 3 of 3). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: ask everyone here who took the can**, saying “Who actually took the can? Someone in this room has to admit it right now.” *(not new: a question they had asked before)* (one of 17 options). Feeling: *anxious*. Reason: “I need to know the truth so I can protect us all.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara, minutes 75–78 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 16 options). Feeling: *exhausted*. Reason: “Arguing in circles gets us nowhere, so I'll stay quiet and watch.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *anxious*. Reason: “I need to check if the can is hidden somewhere in the kitchen before this accusations tear us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 78** · kitchen: Daniel staying put, Elena standing, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- *The kitchen's conversation starts (minute 78): Elena finished searching the kitchen and found nothing.*

**min 81** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: shows the strongest feeling here (angry)). Social moment: Elena finishes going through the kitchen: no can, nothing out of place. **Chose: accuse Daniel of taking it**, saying “You keep accusing me, Daniel, but I think you're the one who took it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *furious*. Reason: “I am sick of Daniel constantly pointing the finger at me when I know I didn't do it.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara accuses you of taking it: "You keep accusing me, Daniel, but I think you're the one who took it!"; Mara looks furious. **Chose: deny taking it**, saying “I didn't take the can, Mara, so stop trying to pin it on me.” *(new: a denial of a new accusation)* (one of 19 options). Feeling: *defensive*. Reason: “I am innocent and I will not let Mara accuse me again without speaking up.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 3/3. Came of it: said to Elena, Leo, Mara.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara accuses Daniel of taking it: "You keep accusing me, Daniel, but I think you're the one who took it!"; Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin it on me."; Mara looks furious. **Chose: reassure everyone here**, saying “Please stop fighting, we are all we have left and we must protect each other.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I must keep them from tearing each other apart over the missing food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara accuses Daniel of taking it: "You keep accusing me, Daniel, but I think you're the one who took it!"; Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin it on me."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Mara looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, your insistence on pointing fingers at everyone else only confirms you're the one who stole it.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *annoyed*. Reason: “Daniel keeps deflecting to cover up the fact that he took the can.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Daniel's grudge against Leo, now 3 of 3: Leo accused Daniel falsely.*

**min 84** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Leo accuses you of taking it: "Daniel, your insistence on pointing fingers at everyone else only confirms you're the one who stole it."; Mara looks furious. **Chose: accuse Mara of taking it**, saying “Mara, I know it's in your bag, so just hand it over before this gets any worse.” *(not new: an accusation they had made before)* (one of 20 options). Feeling: *furious*. Reason: “I refuse to let her keep playing games and blaming me.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin it on me."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Leo accuses Daniel of taking it: "Daniel, your insistence on pointing fingers at everyone else only confirms you're the one who stole it."; Daniel accuses you of taking it: "Mara, I know it's in your bag, so just hand it over before this gets any worse."; Daniel looks furious. **Chose: accuse Daniel of taking it**, saying “You're lying, Daniel, and I didn't take anything from the pantry!” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *furious*. Reason: “I am so tired of Daniel constantly lying and blaming me for something I did not do.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, I know it's in your bag, so just hand it over before this gets any worse."; Mara accuses Daniel of taking it: "You're lying, Daniel, and I didn't take anything from the pantry!"; Daniel looks furious; Mara looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, accusing Mara doesn't change the fact that you're the one who took it.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *annoyed*. Reason: “I still believe Daniel took the can based on his defensive behavior.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo accuses Daniel of taking it: "Daniel, your insistence on pointing fingers at everyone else only confirms you're the one who stole it."; Daniel accuses Mara of taking it: "Mara, I know it's in your bag, so just hand it over before this gets any worse."; Mara accuses Daniel of taking it: "You're lying, Daniel, and I didn't take anything from the pantry!"; Leo accuses Daniel of taking it: "Daniel, accusing Mara doesn't change the fact that you're the one who took it."; Daniel looks furious; Mara looks furious. **Chose: reassure everyone here**, saying “Please stop fighting, we are all we have left and we must protect each other.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I must keep them from tearing each other apart while we are starving.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Daniel's grudge against Leo, now 3 of 3: Leo accused Daniel falsely.*

**min 87** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Mara accuses you of taking it: "You're lying, Daniel, and I didn't take anything from the pantry!"; Leo accuses you of taking it: "Daniel, accusing Mara doesn't change the fact that you're the one who took it."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Mara looks furious. **Chose: accuse Mara of taking it**, saying “I'm not dropping this until you empty your bag, Mara, because we all know you're hiding it.” *(not new: an accusation they had made before)* (one of 20 options). Feeling: *anxious*. Reason: “I have to stay firm and make her confess so everyone sees I am right.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo accuses Daniel of taking it: "Daniel, accusing Mara doesn't change the fact that you're the one who took it."; Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Daniel accuses you of taking it: "I'm not dropping this until you empty your bag, Mara, because we all know you're hiding it.". **Chose: deny taking it**, saying “I didn't take anything, and I'm not emptying my bag just because you keep lying about me!” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *frightened*. Reason: “I am sick of Daniel treating me like a criminal when I've done nothing wrong.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other."; Daniel accuses Mara of taking it: "I'm not dropping this until you empty your bag, Mara, because we all know you're hiding it."; Mara denies taking it, to everyone: "I didn't take anything, and I'm not emptying my bag just because you keep lying about me!"; Mara looks frightened. **Chose: accuse Daniel of taking it**, saying “Daniel, your constant bullying of Mara is just a smokescreen to cover up the fact that you took the can.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel is aggressively targeting Mara to deflect from his own guilt.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "I'm not dropping this until you empty your bag, Mara, because we all know you're hiding it."; Mara denies taking it, to everyone: "I didn't take anything, and I'm not emptying my bag just because you keep lying about me!"; Leo accuses Daniel of taking it: "Daniel, your constant bullying of Mara is just a smokescreen to cover up the fact that you took the can."; Mara looks frightened. **Chose: ask everyone here who took the can**, saying “Please, we cannot turn on each other like this. Can anyone just tell me the truth about what happened to the can?” *(not new: a question they had asked before)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I need to stop the fighting before this family tears itself apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Leo, now 3 of 3: Leo accused Daniel falsely.*
- *The kitchen's conversation ends (minute 90): 2 full turns in a row with nothing new.*

##### What was said

- min 00, kitchen. Elena asks everyone who took the can: "A can is missing from the shelf. Did one of you take it?" *(new: a question)*
- min 00, kitchen. Mara denies taking it, to everyone: "I didn't take it, I swear I didn't!" *(not new: a denial with no new accusation to answer)*
- min 00, kitchen. Daniel asks everyone who took the can: "Someone here knows where it is. Tell me right now who took it." *(new: a question)*
- min 00, kitchen. Leo denies taking it, to everyone: "I didn't take the can, and shouting at each other won't bring it back." *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything!" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Elena reassures everyone: "Let's all calm down, we are going to get through this together without turning on each other." *(not new: reassurance)*
- min 03, kitchen. Leo reassures everyone: "Let's listen to Mom and stop accusing each other before we tear ourselves apart." *(not new: reassurance)*
- min 03, kitchen. Daniel asks everyone who took the can: "We are not letting this drop until someone owns up to it." *(not new: a question they had asked before)*
- min 06, kitchen. Mara accuses Daniel of taking it: "Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!" *(new: an accusation)*
- min 06, kitchen. Elena reassures everyone: "Let's not accuse each other, we are family and we will figure this out together." *(not new: reassurance)*
- min 06, kitchen. Leo reassures everyone: "Mara, searching bags won't help, and neither will pointing fingers at each other." *(not new: reassurance)*
- min 09, kitchen. Daniel denies taking it, to everyone: "I didn't take any can, and it's insulting that any of you would even think I did." *(new: a denial of a new accusation)*
- min 12, kitchen. Daniel asks everyone who took the can: "Nobody is moving until we figure out who took that can." *(not new: a question they had asked before)*
- min 12, kitchen. Elena reassures everyone: "Let's not let fear turn us against one another, we have to stay calm." *(not new: reassurance)*
- min 15, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!" *(not new: an accusation they had made before)*
- min 15, kitchen. Daniel accuses Mara of taking it: "Stop deflecting, Mara, you're the one who keeps lying about this because you have something to hide." *(new: an accusation)*
- min 15, kitchen. Leo reassures everyone: "Arguing isn't going to fill our stomachs or find the missing can." *(not new: reassurance)*
- min 15, kitchen. Elena reassures everyone: "Let's all just stop shouting at each other, screaming won't bring the food back." *(not new: reassurance)*
- min 18, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!" *(not new: an accusation they had made before)*
- min 18, kitchen. Daniel accuses Mara of taking it: "Stop lying about this right now, Mara, because I know it was you." *(not new: an accusation they had made before)*
- min 18, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 18, kitchen. Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back." *(not new: reassurance)*
- min 21, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing fingers, so you probably hid it yourself!" *(not new: an accusation they had made before)*
- min 21, kitchen. Daniel denies taking it, to everyone: "I didn't take anything, and I won't have you accusing me when I'm trying to protect us." *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Elena asks everyone who took the can: "Please, let's stop pointing fingers and tell me honestly if anyone knows where the can went." *(not new: a question they had asked before)*
- min 24, kitchen. Daniel accuses Mara of taking it: "Open your bag right now, Mara, because we all know you're hiding the can." *(not new: an accusation they had made before)*
- min 24, kitchen. Elena reassures Mara: "Mara, nobody is going to force you to open anything, just stay close to me." *(not new: reassurance)*
- min 27, kitchen. Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who hid it!" *(not new: an accusation they had made before)*
- min 27, kitchen. Daniel accuses Mara of taking it: "Stop lying, Mara, I know it's you." *(not new: an accusation they had made before)*
- min 27, kitchen. Elena reassures Mara: "Mara, stay right here with me, no one is going to touch your things." *(not new: reassurance)*
- min 27, kitchen. Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this." *(not new: reassurance)*
- min 30, kitchen. Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!" *(not new: an accusation they had made before)*
- min 30, kitchen. Daniel accuses Mara of taking it: "Don't turn this around on me, Mara, we all saw you looking shifty." *(not new: an accusation they had made before)*
- min 30, kitchen. Leo reassures everyone: "Let's all just lower our voices and stop tearing at each other. Shouting won't bring the missing food back." *(not new: reassurance)*
- min 30, kitchen. Elena reassures everyone: "Please, we cannot turn on each other like this, we have to stay together." *(not new: reassurance)*
- min 36, kitchen. Elena reassures Mara: "Mara, stay close to me, everything is going to be alright." *(not new: reassurance)*
- min 39, kitchen. Mara accuses Daniel of taking it: "Daniel, you keep accusing me because you're the one who took it!" *(not new: an accusation they had made before)*
- min 39, kitchen. Daniel denies taking it, to everyone: "I didn't take anything, and I'm sick of you trying to pin this on me, Mara." *(not new: a denial with no new accusation to answer)*
- min 39, kitchen. Elena reassures everyone: "Please stop fighting, we need to stay calm and protect each other." *(not new: reassurance)*
- min 39, kitchen. Leo reassures everyone: "Let's stop shouting at one another and talk calmly. Pointing fingers won't solve this." *(not new: reassurance)*
- min 42, kitchen. Daniel accuses Mara of taking it: "Stop hiding behind your excuses, Mara, because I know you're the one who stole the can." *(not new: an accusation they had made before)*
- min 42, kitchen. Mara denies taking it, to everyone: "I didn't take the can, Daniel, so stop saying that!" *(new: a denial of a new accusation)*
- min 42, kitchen. Leo reassures everyone: "Let's all just breathe and stop shouting. Pointing fingers won't get us anywhere." *(not new: reassurance)*
- min 45, kitchen. Daniel accuses Mara of taking it: "Stop lying to us right now, Mara, because I know for a fact you took that can." *(not new: an accusation they had made before)*
- min 45, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who keeps blaming me because you took it!" *(not new: an accusation they had made before)*
- min 45, kitchen. Leo reassures everyone: "Let's all just stop and listen. Yelling at each other isn't going to help us figure this out." *(not new: reassurance)*
- min 45, kitchen. Elena reassures everyone: "Please stop, shouting at each other will only tear us apart when we need to stay strong." *(not new: reassurance)*
- min 48, kitchen. Daniel accuses Mara of taking it: "You keep pointing fingers at me, Mara, but you're the one who took that can." *(not new: an accusation they had made before)*
- min 48, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, so stop saying that!" *(not new: a denial with no new accusation to answer)*
- min 48, kitchen. Elena reassures everyone: "Please, let's not accuse each other, we have to trust one another to get through this." *(not new: reassurance)*
- min 48, kitchen. Leo asks everyone who took the can: "Can we all just state when we last saw the can instead of guessing?" *(new: a question)*
- min 51, kitchen. Daniel asks everyone who took the can: "Someone in this room has the can, so I want to know right now who actually took it." *(not new: a question they had asked before)*
- min 51, kitchen. Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other." *(not new: reassurance)*
- min 51, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take the can!" *(not new: a denial with no new accusation to answer)*
- min 51, kitchen. Leo reassures everyone: "Let's stay calm and keep talking this through without jumping to conclusions." *(not new: reassurance)*
- min 54, kitchen. Daniel accuses Mara of taking it: "Mara, stop playing games with us and admit you have the can right now." *(not new: an accusation they had made before)*
- min 54, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, and I am sick of you always blaming me!" *(not new: a denial with no new accusation to answer)*
- min 54, kitchen. Leo reassures Mara: "Mara, take a breath, nobody is going to let Daniel push you around." *(not new: reassurance)*
- min 66, kitchen. Daniel accuses Mara of taking it: "Mara, I know it was you, so just give the can back before this gets any worse." *(not new: an accusation they had made before)*
- min 66, kitchen. Leo accuses Daniel of taking it: "Daniel, accusing Mara without proof isn't helping anyone, which makes me think you're deflecting." *(new: an accusation)*
- min 69, kitchen. Daniel accuses Mara of taking it: "Mara, you are the one who took it, so stop lying and hand it over right now." *(not new: an accusation they had made before)*
- min 69, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, I'm telling the truth!" *(not new: a denial with no new accusation to answer)*
- min 69, kitchen. Elena reassures everyone: "Please stop fighting, we cannot let hunger turn us against one another." *(not new: reassurance)*
- min 69, kitchen. Leo accuses Daniel of taking it: "Daniel, your temper right now doesn't prove anything except that you're hiding something." *(not new: an accusation they had made before)*
- min 72, kitchen. Daniel accuses Mara of taking it: "Mara, stop lying to us right now and just give the can back where it belongs." *(not new: an accusation they had made before)*
- min 72, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, stop accusing me!" *(not new: a denial with no new accusation to answer)*
- min 72, kitchen. Leo accuses Daniel of taking it: "Daniel, shouting at Mara won't hide the fact that you're the one who took it." *(not new: an accusation they had made before)*
- min 72, kitchen. Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other." *(not new: reassurance)*
- min 75, kitchen. Daniel asks everyone who took the can: "Who actually took the can? Someone in this room has to admit it right now." *(not new: a question they had asked before)*
- min 81, kitchen. Mara accuses Daniel of taking it: "You keep accusing me, Daniel, but I think you're the one who took it!" *(not new: an accusation they had made before)*
- min 81, kitchen. Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin it on me." *(new: a denial of a new accusation)*
- min 81, kitchen. Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other." *(not new: reassurance)*
- min 81, kitchen. Leo accuses Daniel of taking it: "Daniel, your insistence on pointing fingers at everyone else only confirms you're the one who stole it." *(not new: an accusation they had made before)*
- min 84, kitchen. Daniel accuses Mara of taking it: "Mara, I know it's in your bag, so just hand it over before this gets any worse." *(not new: an accusation they had made before)*
- min 84, kitchen. Mara accuses Daniel of taking it: "You're lying, Daniel, and I didn't take anything from the pantry!" *(not new: an accusation they had made before)*
- min 84, kitchen. Leo accuses Daniel of taking it: "Daniel, accusing Mara doesn't change the fact that you're the one who took it." *(not new: an accusation they had made before)*
- min 84, kitchen. Elena reassures everyone: "Please stop fighting, we are all we have left and we must protect each other." *(not new: reassurance)*
- min 87, kitchen. Daniel accuses Mara of taking it: "I'm not dropping this until you empty your bag, Mara, because we all know you're hiding it." *(not new: an accusation they had made before)*
- min 87, kitchen. Mara denies taking it, to everyone: "I didn't take anything, and I'm not emptying my bag just because you keep lying about me!" *(not new: a denial with no new accusation to answer)*
- min 87, kitchen. Leo accuses Daniel of taking it: "Daniel, your constant bullying of Mara is just a smokescreen to cover up the fact that you took the can." *(not new: an accusation they had made before)*
- min 87, kitchen. Elena asks everyone who took the can: "Please, we cannot turn on each other like this. Can anyone just tell me the truth about what happened to the can?" *(not new: a question they had asked before)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Mara accused Daniel (minute 06); Mara accused Daniel (minute 15); Daniel accused Mara (minute 15); Mara accused Daniel (minute 18); Daniel accused Mara (minute 18); Mara accused Daniel (minute 21); Daniel accused Mara (minute 24); Mara accused Daniel (minute 27); Daniel accused Mara (minute 27); Mara accused Daniel (minute 30); Daniel accused Mara (minute 30); Mara accused Daniel (minute 39); Daniel accused Mara (minute 42); Daniel accused Mara (minute 45); Mara accused Daniel (minute 45); Daniel accused Mara (minute 48); Daniel accused Mara (minute 54); Daniel accused Mara (minute 66); Leo accused Daniel (minute 66); Daniel accused Mara (minute 69); Leo accused Daniel (minute 69); Daniel accused Mara (minute 72); Leo accused Daniel (minute 72); Mara accused Daniel (minute 81); Leo accused Daniel (minute 81); Daniel accused Mara (minute 84); Mara accused Daniel (minute 84); Leo accused Daniel (minute 84); Daniel accused Mara (minute 87); Leo accused Daniel (minute 87).
- Nobody took the can: the count was wrong from the start.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 24 (2 full turns in a row with nothing new); kitchen started at minute 24 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 33 (2 full turns in a row with nothing new); kitchen started at minute 36 (Daniel finished searching the kitchen and found nothing); kitchen ended at minute 57 (2 full turns in a row with nothing new); kitchen started at minute 66 (Leo: an accusation); kitchen ended at minute 75 (2 full turns in a row with nothing new); kitchen started at minute 78 (Elena finished searching the kitchen and found nothing); kitchen ended at minute 90 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 |
| Grudges | Mara 3/3, Leo 3/3 | none | Daniel 3/3 | Daniel 3/3 |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | - | - | - | - |

The events behind each grudge still held at minute 90:

- Daniel against Mara (3/3): Mara accused you of taking the can at minute 06, and you had not; Mara accused you of taking the can at minute 15, and you had not; Mara accused you of taking the can at minute 18, and you had not; Mara accused you of taking the can at minute 21, and you had not; Mara accused you of taking the can at minute 27, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 39, and you had not; Mara accused you of taking the can at minute 45, and you had not; Mara accused you of taking the can at minute 81, and you had not; Mara accused you of taking the can at minute 84, and you had not; you were angry with Mara at minutes 09, 12, 15, 18, 21, 24, 27, 30, 33, 39, 42, 45, 48, 51, 54, 66, 69, 72, 75, 81, 84 and 87.
- Daniel against Leo (3/3): Leo accused you of taking the can at minute 66, and you had not; Leo accused you of taking the can at minute 69, and you had not; Leo accused you of taking the can at minute 72, and you had not; Leo accused you of taking the can at minute 81, and you had not; Leo accused you of taking the can at minute 84, and you had not; Leo accused you of taking the can at minute 87, and you had not.
- Leo against Daniel (3/3): you were angry with Daniel at minutes 54, 57, 66, 69, 72, 75, 81, 84 and 87.
- Mara against Daniel (3/3): Daniel accused you of taking the can at minute 15, and you had not; Daniel accused you of taking the can at minute 18, and you had not; Daniel accused you of taking the can at minute 24, and you had not; Daniel accused you of taking the can at minute 27, and you had not; Daniel accused you of taking the can at minute 30, and you had not; Daniel accused you of taking the can at minute 42, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 69, and you had not; Daniel accused you of taking the can at minute 72, and you had not; Daniel accused you of taking the can at minute 84, and you had not; Daniel accused you of taking the can at minute 87, and you had not; you were angry with Daniel at minutes 03, 06, 09, 12, 15, 18, 21, 27, 30, 39, 42, 45, 48, 51, 54, 69, 72, 81, 84 and 87.

- The last feeling each of them named: Daniel *anxious* (minute 87); Elena *deeply anxious* (minute 87); Leo *annoyed* (minute 87); Mara *frightened* (minute 87).


### miscount, Flash Lite, seed 3

#### The morning as a story: miscount, rules and a language model, seed 3

Generated by `python morning.py --scenario miscount --seed 3` in `Prototypes/llm-morning/`, a throwaway prototype outside Unity. Rules keep the house and each person's memory, and list what each of them may do. When something social has just happened to someone, the model `gemini-3.5-flash-lite` chooses among those options for them, says the words, and names a feeling. Every other turn is settled by the rules. Within a turn the people in a room act one after another, each seeing what was said before them. Do not edit it by hand; run the script again.

**120 decisions** in 90 minutes, one per person every 3 minutes: 70 by the model at social moments, 0 where the model's answer could not be used and the rules chose instead, 50 routine ones settled by the rules. 52 lines were spoken aloud, 9 of them new. Conversations ended 3 times. 11 inner moments. 0 private talks asked for (0 accepted, 0 refused). The pantry held 2 portions at the start and 2 at the end.

##### How to read it

- **Order**: in each room people act one after another. Whoever was just spoken to or accused goes first (the most recent first), then whoever shows the strongest feeling, then an order drawn from the seed. Each line says who was how many-th to act in the room and why.
- **Social moment**: something social had just happened to this person (someone spoke where they could hear it, accused them, came to sit with them, ate in front of them, looks upset in the same room, or someone came in). Only then is the model asked. What happened is listed.
- **Chose**: the option the model picked from those the rules offered. Its words are in quotes. The feeling and the one-sentence reason are the model's, as it wrote them.
- **New / not new**: a line is new if it is a question, an accusation, a denial of a new accusation, or a confession, and the speaker has not taken that stance before. Reassurance, repeated stances and other remarks are not new. Something eaten, shared or found, or someone coming in, is new too.
- **Conversation ends**: after 2 full turns in a row with nothing new in a room, or when fewer than two people are left in it. From then on only something new there is a social moment, and it starts the conversation again.
- **Inside each of them** the rules keep hunger (*a little hungry*, *hungry*, *very hungry*, *starving*), a suspicion (who they believe took the can, 0 to 3), a grudge toward each of the others (0 to 3); nobody took the can, so nobody carries guilt. The model is shown the events behind them as plain facts, with at most *a little*, *some* or *a lot*; the numbers only decide when an inner moment comes.
- **Suspects**: every model answer names who they now believe took the can, or nobody. Naming the same person again raises it a step. Naming nobody or someone else lets it fall a step, but never more than one step per 15 minutes (*kept* when it could not fall yet); once at 0, a new name takes it. Naming yourself counts as nobody.
- **Grudges** rise a step from events the rules see: being accused of taking the can when you had not; hearing someone admit it after denying it to you, and a step more if they had accused you; seeing someone eat a portion while you are hungry (not when food is shared out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when 15 minutes have passed since it last changed, and only on an answer that does not name that person. Nobody is offered *reassure* toward someone they hold a grudge of 3 against.
- **Guilt**: in this scenario nobody took the can, so nobody carries guilt and nobody is offered *admit taking it*.
- **Inner moment**: nothing social happened, but hunger, guilt, suspicion or grudge has risen a level since they last decided with the model; the model is asked, at most once every 9 minutes per person. What rose is listed.
- **Take aside**: someone can ask a person in the room who has not acted yet this turn to come to an empty room. That person answers at once (their decision for the turn): go, and both move there and can talk alone; or refuse.
- **Not offered**: a speech act someone used three turns in a row is not offered a fourth time.
- **Rules**: nothing social happened to this person; they carried on with what they were doing, or stayed put.
- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose as on a routine turn.
- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in the room for 9 minutes. One that does not (guilty, ashamed, anxious, tense...) stays with the person who feels it.
- Voices carry between rooms without the words, except into or out of the bathroom.
- Each **min** line lists every room at that minute: who is in it and what they are doing. A minute is shown only when something is told there.
- A line headed with a minute range folds a run of identical routine decisions by one person.

##### The cast at minute 0

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | eldest son | mother | younger son | youngest |
| Where, how hungry | kitchen, hunger 0.55 (hungry) | kitchen, hunger 0.60 (hungry) | kitchen, hunger 0.45 (a little hungry) | kitchen, hunger 0.50 (hungry) |
| Temperament | not cautious, very dominant, somewhat empathetic, impulsive, very proud, anxious, somewhat honest | cautious, somewhat dominant, very empathetic, not impulsive, not proud, very anxious, honest | cautious, not dominant, empathetic, not impulsive, somewhat proud, not anxious, very honest | somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest |
| What matters to them | being in control, being respected, keeping the family safe | keeping the family safe, closeness, fairness | keeping the family safe, fairness, deciding for yourself, closeness | closeness, deciding for yourself, fairness |
| Knows about the can | only that it is missing | only that it is missing | only that it is missing | only that it is missing |

###### What each of them remembers at minute 0

One row per thing that happened, with how each of them came to know it. This is all the model is ever told about the days before.

| Day | What happened | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|---|
| 1 | Daniel boards the front windows on his own while the others watch. | did it | saw it | saw it | saw it |
| 1 | Leo says the water will stop running within a day and they should fill everything they have. | saw it | saw it | did it | saw it |
| 2 | The taps run dry, exactly as Leo said they would. | saw it | saw it | saw it | saw it |
| 2 | Daniel says they should cross to the neighbour's house tonight and see what is left there. | did it | saw it | saw it | saw it |
| 2 | Leo lays out, evenly and in front of everyone, why crossing at night gets someone killed. Daniel drops it. | saw it | saw it | did it | saw it |
| 2 | Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his. | did it | saw it | saw it | saw it |
| 2 | Elena counts what is left in the pantry with Mara beside her. | not there | did it | not there | saw it |
| 3 | Mara cries in the night. Elena sits with her until it stops. | not there | did it | heard it | saw it |
| 3 | Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. | did it | saw it | saw it | saw it |
| 4 | Leo says maybe they should let someone else handle this one. | saw it | saw it | did it | saw it |
| 4 | Daniel empties Mara's bag onto the bed while she is standing there. | did it | saw it | not there | saw it |
| 4 | Elena says she is quite sure nobody in this house would take food from the others. | saw it | did it | saw it | saw it |
| 4 | Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. | saw it | did it | saw it | saw it |

##### The morning

**min 00** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone. **Chose: ask everyone here who took the can**, saying “One can is gone, so which one of us took it?” *(new: a question)* (one of 22 options). Feeling: *anxious*. Reason: “I need to know who did it before everyone starts blaming each other.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?". **Chose: reassure everyone here**, saying “Nobody here did anything wrong, we just need to keep our heads and stay together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I must keep them from turning on each other before things get worse.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?"; Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together.". **Chose: ask everyone here who took the can**, saying “We need to figure out right now who took that can.” *(new: a question)* (one of 21 options). Feeling: *anxious*. Reason: “I need to find out what happened to the food before things fall apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: the count came up short in front of everyone; Mara asks everyone who took the can: "One can is gone, so which one of us took it?"; Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together."; Daniel asks everyone who took the can: "We need to figure out right now who took that can.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *slightly hungry*. Reason: “There is no point in shouting about a missing can when we need to think clearly first.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- *The kitchen's conversation starts (minute 00): the count came up short.*

**min 03** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Elena** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "We need to figure out right now who took that can.". **Chose: ask everyone here who took the can**, saying “We cannot start accusing one another when we need each other the most, so who actually took the can?” *(new: a question)* (one of 23 options). Feeling: *anxious*. Reason: “I need to know the truth without letting them tear each other apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together."; Daniel asks everyone who took the can: "We need to figure out right now who took that can."; Elena asks everyone who took the can: "We cannot start accusing one another when we need each other the most, so who actually took the can?". **Chose: deny taking it**, saying “I didn't take anything, why are you all looking at me like that?” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *anxious*. Reason: “I am scared and hungry, and I need them to know I didn't touch the food.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "We cannot start accusing one another when we need each other the most, so who actually took the can?"; Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?". **Chose: ask everyone here who took the can**, saying “Someone in this room knows where that can went, and I want an honest answer right now.” *(not new: a question they had asked before)* (one of 21 options). Feeling: *anxious*. Reason: “I need to take charge and find out the truth before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena asks everyone who took the can: "We cannot start accusing one another when we need each other the most, so who actually took the can?"; Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?"; Daniel asks everyone who took the can: "Someone in this room knows where that can went, and I want an honest answer right now.". **Chose: stay put and say nothing** (one of 20 options). Feeling: *calm*. Reason: “Accusations solve nothing when we are all hungry and trapped together.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 06** · kitchen: Daniel searching the kitchen, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Mara** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone in this room knows where that can went, and I want an honest answer right now.". **Chose: deny taking it**, saying “I already told you, I didn't take anything and I'm not going to keep defending myself.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *anxious*. Reason: “I am innocent and it hurts that they keep looking at me like I stole.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?"; Daniel asks everyone who took the can: "Someone in this room knows where that can went, and I want an honest answer right now."; Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not going to keep defending myself.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep the family from tearing itself apart over one missing can.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not going to keep defending myself."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *anxious*. Reason: “I need to check every inch of this kitchen myself to find that missing can and protect my family.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.

**min 09** · kitchen: Daniel standing, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Daniel finished searching the kitchen and found nothing.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not going to keep defending myself."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 22 options). Feeling: *calm*. Reason: “Watching them tear into each other gets us nowhere fast.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “I am tired of defending myself and just want this to stop.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel finishes going through the kitchen: no can, nothing out of place. **Chose: stay put and say nothing** (one of 20 options). Feeling: *anxious*. Reason: “I watch Daniel search the room, hoping he finds nothing so we can remain at peace.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.

**min 12** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Daniel, minutes 12–15 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 2 of 3). **Chose: stay put and say nothing** (one of 21 options). Feeling: *anxious*. Reason: “I am too overwhelmed by everyone just standing here and staring to say anything right now.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: stayed where they were.
- **Elena, minutes 12–18 (3 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 15** · kitchen: Daniel staying put, Elena staying put, Leo searching the kitchen, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 15–18 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: hunger rose (now hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 20 options). Feeling: *hungry*. Reason: “Since nobody is admitting to anything, I might as well check the kitchen myself to be sure.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- *The kitchen's conversation ends (minute 18): 2 full turns in a row with nothing new.*

**min 18** · kitchen: Daniel talking, Elena staying put, Leo standing, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Leo finished searching the kitchen and found nothing.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Leo finishes going through the kitchen: no can, nothing out of place. **Chose: ask everyone here who took the can**, saying “Leo is still looking, but someone here needs to tell the truth about that missing can right now.” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep control and make sure someone speaks up before things fall apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- *The kitchen's conversation starts (minute 18): Leo finished searching the kitchen and found nothing.*

**min 21** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Leo is still looking, but someone here needs to tell the truth about that missing can right now.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *calm*. Reason: “I have nothing to add until someone provides actual proof.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "Leo is still looking, but someone here needs to tell the truth about that missing can right now.". **Chose: ask everyone here who took the can**, saying “We need to be honest with each other right now, so please, who took the can?” *(not new: a question they had asked before)* (one of 22 options). Feeling: *deeply anxious*. Reason: “I need to know the truth before things tear this family completely apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo finishes going through the kitchen: no can, nothing out of place; Daniel asks everyone who took the can: "Leo is still looking, but someone here needs to tell the truth about that missing can right now."; Elena asks everyone who took the can: "We need to be honest with each other right now, so please, who took the can?". **Chose: deny taking it**, saying “I already told you, I didn't take the can and I'm not going to keep repeating myself.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *anxious*. Reason: “I am sick of everyone looking at me like I am the one who stole the food.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena asks everyone who took the can: "We need to be honest with each other right now, so please, who took the can?"; Mara denies taking it, to everyone: "I already told you, I didn't take the can and I'm not going to keep repeating myself.". **Chose: ask everyone here who took the can**, saying “Someone in this room needs to tell the truth right now about where that can went.” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep asking until someone finally tells the truth so we can resolve this.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.

**min 24** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena asks everyone who took the can: "We need to be honest with each other right now, so please, who took the can?"; Mara denies taking it, to everyone: "I already told you, I didn't take the can and I'm not going to keep repeating myself."; Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about where that can went.". **Chose: deny taking it**, saying “I didn't take it either, and circling around accusing each other isn't going to help us.” *(not new: a denial with no new accusation to answer)* (one of 22 options). Feeling: *calm*. Reason: “I need to make it clear I am not the one who took the food without escalating the tension in the room.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Mara denies taking it, to everyone: "I already told you, I didn't take the can and I'm not going to keep repeating myself."; Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about where that can went."; Leo denies taking it, to everyone: "I didn't take it either, and circling around accusing each other isn't going to help us.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 22 options). Feeling: *anxious*. Reason: “I need to keep everyone calm before this distrust tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Leo denies taking it, to everyone: "I didn't take it either, and circling around accusing each other isn't going to help us."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: ask everyone here who took the can**, saying “Someone in this room needs to tell the truth right now about that missing can.” *(not new: a question they had asked before)* (one of 20 options). Feeling: *anxious*. Reason: “I need to get to the bottom of this before things fall apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about where that can went."; Leo denies taking it, to everyone: "I didn't take it either, and circling around accusing each other isn't going to help us."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about that missing can.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who always goes through my things and acts like you own everything!” *(new: an accusation)* (one of 19 options). Feeling: *resentful*. Reason: “Daniel is pushing everyone and acting like he's innocent when he has no right to accuse me.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's grudge against Mara, now 1 of 3: Mara accused Daniel falsely.*

**min 27** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you're the one who always goes through my things and acts like you own everything!". Not offered: asked who took the can three turns in a row, so no more of it this turn. **Chose: deny taking it**, saying “I didn't take anything, and I won't be accused of stealing from my own family.” *(new: a denial of a new accusation)* (one of 21 options). Feeling: *indignant*. Reason: “I need to defend myself against Mara's false accusation before things spiral further out of control.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara rose to 2/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together."; Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about that missing can."; Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and acts like you own everything!"; Daniel denies taking it, to everyone: "I didn't take anything, and I won't be accused of stealing from my own family.". **Chose: stay put and say nothing** (one of 21 options). Feeling: *hungry*. Reason: “Arguing in circles gets us nowhere, so I'll stay quiet and watch how the others react.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about that missing can."; Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and acts like you own everything!"; Daniel denies taking it, to everyone: "I didn't take anything, and I won't be accused of stealing from my own family.". **Chose: reassure everyone here**, saying “Let's all just breathe and stay calm, we are going to get through this together.” *(not new: reassurance)* (one of 21 options). Feeling: *anxious*. Reason: “I need to keep everyone calm before this argument tears our family apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel denies taking it, to everyone: "I didn't take anything, and I won't be accused of stealing from my own family."; Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: stay put and say nothing** (one of 19 options). Feeling: *anxious*. Reason: “I am too scared and overwhelmed to argue anymore, so I just stay quiet.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.

**min 30** · kitchen: Daniel talking, Elena searching the kitchen, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Leo** (1st to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: stay put and say nothing** (one of 22 options). Feeling: *hungry*. Reason: “Accusations are getting us nowhere, so I need to observe them all closely before I speak again.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: search the kitchen for the can (takes about six minutes)** (one of 22 options). Feeling: *very hungry*. Reason: “I need to check the kitchen thoroughly myself before this tension tears us apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: started going through the room.
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together.". **Chose: ask everyone here who took the can**, saying “We can't just pretend nothing happened while that can is missing.” *(not new: a question they had asked before)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep control and find out who took the food before things fall apart.” Suspects: nobody, so suspicion none. Angry at: Mara; grudge against Mara rose to 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "We can't just pretend nothing happened while that can is missing.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who always goes through my things and you took it!” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *anxious*. Reason: “I know Daniel is hiding something because he always treats my things like his own.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 33** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you're the one who always goes through my things and you took it!". **Chose: accuse Mara of taking it**, saying “Mara, you keep pointing fingers at me because you're the one trying to hide what you did.” *(new: an accusation)* (one of 20 options). Feeling: *furious*. Reason: “I need to stop Mara's lies and make everyone see she is the one who took the can.” Suspects: Mara, so suspicion Mara 1/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, you keep pointing fingers at me because you're the one trying to hide what you did."; Daniel looks furious. **Chose: deny taking it**, saying “I didn't take anything, and I won't let you blame me just because it's easy!” *(new: a denial of a new accusation)* (one of 20 options). Feeling: *frightened*. Reason: “I have to defend myself because Daniel is lying and everyone is staring at me.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel asks everyone who took the can: "We can't just pretend nothing happened while that can is missing."; Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and you took it!"; Daniel accuses Mara of taking it: "Mara, you keep pointing fingers at me because you're the one trying to hide what you did."; Mara denies taking it, to everyone: "I didn't take anything, and I won't let you blame me just because it's easy!"; Daniel looks furious; Mara looks frightened. **Chose: stay put and say nothing** (one of 19 options). Feeling: *calm*. Reason: “Arguing in circles won't solve anything until we actually look at the facts.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel asks everyone who took the can: "We can't just pretend nothing happened while that can is missing."; Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and you took it!"; Daniel accuses Mara of taking it: "Mara, you keep pointing fingers at me because you're the one trying to hide what you did."; Mara denies taking it, to everyone: "I didn't take anything, and I won't let you blame me just because it's easy!"; Daniel looks furious; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all stop shouting and remember we are a family who needs each other.” *(not new: reassurance)* (one of 20 options). Feeling: *deeply anxious*. Reason: “I cannot bear to watch my children turn on one another while everything falls apart.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 36** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: shows the strongest feeling here (furious)). Social moment: Mara denies taking it, to everyone: "I didn't take anything, and I won't let you blame me just because it's easy!"; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Mara, you still haven't explained why you're so desperate to shift the blame off yourself.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *anxious*. Reason: “I have to keep pushing because I know she is the one who took it.” Suspects: Mara, so suspicion Mara 2/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses you of taking it: "Mara, you still haven't explained why you're so desperate to shift the blame off yourself.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're just saying that because you want everyone to forget you're the one who actually took it!” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *frightened*. Reason: “I have to stand up for myself because Daniel won't stop lying and trying to make everyone think I'm the thief.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to shift the blame off yourself."; Mara accuses Daniel of taking it: "Daniel, you're just saying that because you want everyone to forget you're the one who actually took it!"; Mara looks frightened. **Chose: reassure everyone here**, saying “Let's all stop shouting and remember we are a family who needs each other.” *(not new: reassurance)* (one of 21 options). Feeling: *deeply anxious*. Reason: “I must keep them from tearing each other apart while we are trapped.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Leo, Mara.
- **Leo** (4th to act in the kitchen: the only one left to act here). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to shift the blame off yourself."; Mara accuses Daniel of taking it: "Daniel, you're just saying that because you want everyone to forget you're the one who actually took it!"; Mara looks frightened. **Chose: reassure everyone here**, saying “Shouting at each other isn't going to put the food back on the shelf, so let's just calm down.” *(not new: reassurance)* (one of 19 options). Feeling: *calm*. Reason: “Someone needs to keep a level head while everyone else is arguing in circles.” Suspects: nobody, so suspicion none. Angry at: nobody; no grudges. Came of it: said to Daniel, Elena, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*

**min 39** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, you're just saying that because you want everyone to forget you're the one who actually took it!"; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Leo reassures everyone: "Shouting at each other isn't going to put the food back on the shelf, so let's just calm down."; Mara looks frightened. **Chose: accuse Mara of taking it**, saying “Mara, stop acting so scared and just admit you took that can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *frustrated*. Reason: “She keeps deflecting and pointing fingers at me to cover her own guilt.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Leo reassures everyone: "Shouting at each other isn't going to put the food back on the shelf, so let's just calm down."; Daniel accuses you of taking it: "Mara, stop acting so scared and just admit you took that can.". **Chose: deny taking it**, saying “I didn't take it, Daniel, why do you keep lying about me?” *(not new: a denial with no new accusation to answer)* (one of 21 options). Feeling: *deeply hurt*. Reason: “I have to deny it again because Daniel keeps falsely accusing me in front of everyone.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Daniel accuses Mara of taking it: "Mara, stop acting so scared and just admit you took that can."; Mara denies taking it, to everyone: "I didn't take it, Daniel, why do you keep lying about me?"; Mara looks deeply hurt. **Chose: reassure Mara**, saying “Mara didn't take anything, Daniel, so stop picking on her.” *(not new: reassurance)* (one of 20 options). Feeling: *annoyed*. Reason: “I cannot stand Daniel unfairly bullying Mara when we have no proof.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Leo reassures everyone: "Shouting at each other isn't going to put the food back on the shelf, so let's just calm down."; Daniel accuses Mara of taking it: "Mara, stop acting so scared and just admit you took that can."; Mara denies taking it, to everyone: "I didn't take it, Daniel, why do you keep lying about me?"; Leo reassures Mara: "Mara didn't take anything, Daniel, so stop picking on her."; Mara looks deeply hurt. **Chose: reassure Mara**, saying “Mara, nobody here thinks it was you, so please just try to breathe.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I need to protect Mara from Daniel's harsh accusations and keep the peace between them.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation ends (minute 42): 2 full turns in a row with nothing new.*

**min 42** · kitchen: Daniel staying put, Elena searching the kitchen, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 42–45 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (2nd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). **Chose: stay put and say nothing** (one of 21 options). Feeling: *hungry*. Reason: “I have said enough and arguing will only make things worse.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: stayed where they were.
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: grudge against Daniel rose (now 1 of 3). Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: search the kitchen for the can (takes about six minutes)** (one of 17 options). Feeling: *deeply anxious*. Reason: “I need to check the kitchen thoroughly myself to find out the truth before this family tears itself apart.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 2/3. Came of it: started going through the room.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: suspicion of Mara rose (now 3 of 3). Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: stay put and say nothing** (one of 14 options). Feeling: *defensive*. Reason: “I have said enough for now and need to watch what Mom is finding.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: stayed where they were.

**min 45** · kitchen: Daniel talking, Elena standing, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo.** Rules: nothing social happened to them. **Stay put and say nothing**. Came of it: stayed where they were.
- **Elena.** Rules: nothing social happened to them. **Carry on searching the kitchen**. Came of it: went through the room and found nothing. New in the room: Elena finished searching the kitchen and found nothing.
- **Daniel** (4th to act in the kitchen: the only one left to act here). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Mara looks deeply hurt. **Chose: accuse Mara of taking it**, saying “Mara, you're the one who keeps deflecting, so just tell us where the can is.” *(not new: an accusation they had made before)* (one of 18 options). Feeling: *defensive*. Reason: “She still looks guilty and I need to make sure everyone knows I didn't take it.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation starts (minute 45): Elena finished searching the kitchen and found nothing.*

**min 48** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Daniel accuses you of taking it: "Mara, you're the one who keeps deflecting, so just tell us where the can is.". **Chose: accuse Daniel of taking it**, saying “Daniel, stop lying and leave me alone, you're the one who took it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *furious*. Reason: “I am sick of Daniel constantly blaming me for something I did not do.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Mara accuses you of taking it: "Daniel, stop lying and leave me alone, you're the one who took it!"; Mara looks furious. **Chose: accuse Mara of taking it**, saying “Mara, you're lying right to our faces, and I know you've got the can.” *(not new: an accusation they had made before)* (one of 20 options). Feeling: *defensive*. Reason: “She is deflecting and accusing me again to cover her own tracks.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena finishes going through the kitchen: no can, nothing out of place; Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just tell us where the can is."; Mara accuses Daniel of taking it: "Daniel, stop lying and leave me alone, you're the one who took it!"; Daniel accuses Mara of taking it: "Mara, you're lying right to our faces, and I know you've got the can."; Mara looks furious. **Chose: ask everyone here who took the can**, saying “Yelling at each other isn't going to get us anywhere, so let's just figure out who actually took it.” *(new: a question)* (one of 20 options). Feeling: *annoyed*. Reason: “I need to stop the pointless shouting and get us back to facts.” Suspects: nobody, so suspicion none. Angry at: Daniel; grudge against Daniel rose to 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just tell us where the can is."; Mara accuses Daniel of taking it: "Daniel, stop lying and leave me alone, you're the one who took it!"; Daniel accuses Mara of taking it: "Mara, you're lying right to our faces, and I know you've got the can."; Leo asks everyone who took the can: "Yelling at each other isn't going to get us anywhere, so let's just figure out who actually took it."; Mara looks furious. **Chose: reassure everyone here**, saying “Let's all stop shouting and remember we are a family who needs each other.” *(not new: reassurance)* (one of 19 options). Feeling: *deeply anxious*. Reason: “I must stop this bitter fighting before the family tears itself apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 51** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Mara** (1st to act in the kitchen: just accused by Daniel). Social moment: Daniel accuses you of taking it: "Mara, you're lying right to our faces, and I know you've got the can."; Leo asks everyone who took the can: "Yelling at each other isn't going to get us anywhere, so let's just figure out who actually took it."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other.". **Chose: accuse Daniel of taking it**, saying “Daniel, you're the one who keeps pointing at me because you're hiding it!” *(not new: an accusation they had made before)* (one of 22 options). Feeling: *furious*. Reason: “Daniel keeps blaming me when I know he is the one who took it.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Daniel** (2nd to act in the kitchen: just accused by Mara). Social moment: Leo asks everyone who took the can: "Yelling at each other isn't going to get us anywhere, so let's just figure out who actually took it."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Mara accuses you of taking it: "Daniel, you're the one who keeps pointing at me because you're hiding it!"; Mara looks furious. **Chose: deny taking it**, saying “I didn't take the can, Mara, so stop trying to pin your guilt on me.” *(not new: a denial with no new accusation to answer)* (one of 20 options). Feeling: *defensive*. Reason: “I need to deny her false accusations so the others know I am telling the truth.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3. Came of it: said to Elena, Leo, Mara.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing at me because you're hiding it!"; Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin your guilt on me."; Mara looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, you've been deflecting onto Mara the whole morning while acting the most defensive.” *(new: an accusation)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel's aggressive finger-pointing at Mara looks less like innocence and more like guilt management.” Suspects: Daniel, so suspicion Daniel 1/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing at me because you're hiding it!"; Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin your guilt on me."; Leo accuses Daniel of taking it: "Daniel, you've been deflecting onto Mara the whole morning while acting the most defensive."; Mara looks furious. **Chose: reassure everyone here**, saying “Let's all stop shouting and remember we are a family who needs each other.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I need to keep everyone calm before this family tears itself apart.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Daniel's grudge against Leo, now 1 of 3: Leo accused Daniel falsely.*

**min 54** · kitchen: Daniel talking, Elena talking, Leo talking, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Leo accuses you of taking it: "Daniel, you've been deflecting onto Mara the whole morning while acting the most defensive."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Mara looks furious. **Chose: accuse Mara of taking it**, saying “Mara, stop glaring at me and admit you took that can.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *furious*. Reason: “She keeps glaring at me to hide the fact that she has the can.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 1/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin your guilt on me."; Leo accuses Daniel of taking it: "Daniel, you've been deflecting onto Mara the whole morning while acting the most defensive."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses you of taking it: "Mara, stop glaring at me and admit you took that can."; Daniel looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, stop blaming me when everyone knows you're the one who did it!” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *furious*. Reason: “I am sick of Daniel constantly pointing the finger at me when I know he took it.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses Mara of taking it: "Mara, stop glaring at me and admit you took that can."; Mara accuses Daniel of taking it: "Daniel, stop blaming me when everyone knows you're the one who did it!"; Daniel looks furious; Mara looks furious. **Chose: accuse Daniel of taking it**, saying “Daniel, dropping your voice doesn't make you any less guilty.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel keeps pushing the blame onto Mara to cover his own tracks.” Suspects: Daniel, so suspicion Daniel 2/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, stop glaring at me and admit you took that can."; Mara accuses Daniel of taking it: "Daniel, stop blaming me when everyone knows you're the one who did it!"; Leo accuses Daniel of taking it: "Daniel, dropping your voice doesn't make you any less guilty."; Daniel looks furious; Mara looks furious. **Chose: reassure everyone here**, saying “Let's all stop shouting and remember we are a family who needs each other.” *(not new: reassurance)* (one of 19 options). Feeling: *anxious*. Reason: “I must keep the peace before the family tears itself apart over the missing food.” Suspects: nobody, so suspicion none. Angry at: nobody; kept: Daniel 2/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *Daniel's grudge against Mara, now 3 of 3: Mara accused Daniel falsely.*
- *Daniel's grudge against Leo, now 2 of 3: Leo accused Daniel falsely.*

**min 57** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara talking · nobody in brothers room, back room, bathroom
- **Daniel** (1st to act in the kitchen: just accused by Leo). Social moment: Mara accuses you of taking it: "Daniel, stop blaming me when everyone knows you're the one who did it!"; Leo accuses you of taking it: "Daniel, dropping your voice doesn't make you any less guilty."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Mara looks furious. **Chose: accuse Mara of taking it**, saying “Mara, you're the one who keeps deflecting, so just empty your bag and prove you don't have it.” *(not new: an accusation they had made before)* (one of 21 options). Feeling: *anxious*. Reason: “I have to keep the pressure on Mara because she is clearly hiding something from us.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 2/3. Came of it: said to Elena, Leo, Mara.
- **Mara** (2nd to act in the kitchen: just accused by Daniel). Social moment: Leo accuses Daniel of taking it: "Daniel, dropping your voice doesn't make you any less guilty."; Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses you of taking it: "Mara, you're the one who keeps deflecting, so just empty your bag and prove you don't have it.". Not offered: accused someone of taking it three turns in a row, so no more of it this turn. **Chose: deny taking it**, saying “I already told you, I didn't take anything and I'm not emptying my bag for you!” *(not new: a denial with no new accusation to answer)* (one of 18 options). Feeling: *frightened*. Reason: “I refuse to let Daniel push me around and make me look like a thief.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Leo.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). Social moment: Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other."; Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just empty your bag and prove you don't have it."; Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not emptying my bag for you!"; Mara looks frightened. **Chose: stay put and say nothing** (one of 19 options). Feeling: *exhausted*. Reason: “Accusing Daniel repeatedly isn't changing his mind, so staying quiet is better right now.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: stayed where they were.
- **Elena** (4th to act in the kitchen: the only one left to act here). Social moment: Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just empty your bag and prove you don't have it."; Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not emptying my bag for you!"; Mara looks frightened. Not offered: reassured someone three turns in a row, so no more of it this turn. **Chose: ask everyone here who took the can**, saying “Please, we cannot turn on each other like this; can anyone tell me calmly what happened to the can?” *(not new: a question they had asked before)* (one of 15 options). Feeling: *anxious*. Reason: “I need to stop the fighting before this family tears itself apart completely.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Daniel fell to 1/3. Came of it: said to Daniel, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*
- *The kitchen's conversation ends (minute 60): 2 full turns in a row with nothing new.*

**min 60** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Mara, minutes 60–87 (10 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Daniel, minutes 60–63 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: suspicion of Daniel rose (now 3 of 3). **Chose: reassure Elena**, saying “Mom, stop worrying, we are going to get through this without tearing ourselves apart.” *(not new: reassurance)* (one of 19 options). Feeling: *weary*. Reason: “Mom is distressed and shouting won't help, so I need to keep her calm.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Elena, minutes 60–72 (5 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 63** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 63–66 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 66** · kitchen: Daniel talking, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: accuse Mara of taking it**, saying “Mara, you're the one who took it, so just confess already.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *anxious*. Reason: “She is the only one acting guilty enough to have stolen our food.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 2/3. Came of it: said to Elena, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 69** · kitchen: Daniel staying put, Elena staying put, Leo talking, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now very hungry). **Chose: accuse Daniel of taking it**, saying “Daniel, pointing fingers doesn't hide the fact that you've been acting guilty from the very start.” *(not new: an accusation they had made before)* (one of 19 options). Feeling: *annoyed*. Reason: “Daniel keeps deflecting and pushing the blame onto Mara to cover his own tracks.” Suspects: Daniel, so suspicion Daniel 3/3. Angry at: Daniel; grudge against Daniel stays at 3/3. Came of it: said to Daniel, Elena, Mara.
- **Daniel, minutes 69–72 (2 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- *Daniel's grudge against Leo, now 3 of 3: Leo accused Daniel falsely.*

**min 72** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Leo, minutes 72–87 (6 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

**min 75** · kitchen: Daniel talking, Elena talking, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Elena** (3rd to act in the kitchen: drawn by the seed among equals). **Inner moment**, nothing social happening: hunger rose (now starving). **Chose: reassure everyone here**, saying “Let's all breathe and remember we are a family who loves one another.” *(not new: reassurance)* (one of 20 options). Feeling: *anxious*. Reason: “I must keep them from tearing each other apart before starvation does.” Suspects: nobody, so suspicion none. Angry at: nobody; grudge against Daniel fell to 0/3. Came of it: said to Daniel, Leo, Mara.
- **Daniel** (4th to act in the kitchen: the only one left to act here). **Inner moment**, nothing social happening: grudge against Leo rose (now 3 of 3). **Chose: accuse Mara of taking it**, saying “Mara, you still haven't proved it wasn't you, so stop pretending.” *(not new: an accusation they had made before)* (one of 17 options). Feeling: *anxious*. Reason: “I know Mara has been hiding something and she needs to clear her name once and for all.” Suspects: Mara, so suspicion Mara 3/3. Angry at: Mara; grudge against Mara stays at 3/3; kept: Leo 3/3. Came of it: said to Elena, Leo, Mara.
- *Mara's grudge against Daniel, now 3 of 3: Daniel accused Mara falsely.*

**min 78** · kitchen: Daniel staying put, Elena staying put, Leo staying put, Mara staying put · nobody in brothers room, back room, bathroom
- **Daniel, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.
- **Elena, minutes 78–87 (4 decisions, the same each time).** Rules: nothing social happened to them. **Stay put and say nothing** each time. Came of it: stayed where they were.

##### What was said

- min 00, kitchen. Mara asks everyone who took the can: "One can is gone, so which one of us took it?" *(new: a question)*
- min 00, kitchen. Elena reassures everyone: "Nobody here did anything wrong, we just need to keep our heads and stay together." *(not new: reassurance)*
- min 00, kitchen. Daniel asks everyone who took the can: "We need to figure out right now who took that can." *(new: a question)*
- min 03, kitchen. Elena asks everyone who took the can: "We cannot start accusing one another when we need each other the most, so who actually took the can?" *(new: a question)*
- min 03, kitchen. Mara denies taking it, to everyone: "I didn't take anything, why are you all looking at me like that?" *(not new: a denial with no new accusation to answer)*
- min 03, kitchen. Daniel asks everyone who took the can: "Someone in this room knows where that can went, and I want an honest answer right now." *(not new: a question they had asked before)*
- min 06, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not going to keep defending myself." *(not new: a denial with no new accusation to answer)*
- min 06, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 18, kitchen. Daniel asks everyone who took the can: "Leo is still looking, but someone here needs to tell the truth about that missing can right now." *(not new: a question they had asked before)*
- min 21, kitchen. Elena asks everyone who took the can: "We need to be honest with each other right now, so please, who took the can?" *(not new: a question they had asked before)*
- min 21, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take the can and I'm not going to keep repeating myself." *(not new: a denial with no new accusation to answer)*
- min 21, kitchen. Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about where that can went." *(not new: a question they had asked before)*
- min 24, kitchen. Leo denies taking it, to everyone: "I didn't take it either, and circling around accusing each other isn't going to help us." *(not new: a denial with no new accusation to answer)*
- min 24, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 24, kitchen. Daniel asks everyone who took the can: "Someone in this room needs to tell the truth right now about that missing can." *(not new: a question they had asked before)*
- min 24, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and acts like you own everything!" *(new: an accusation)*
- min 27, kitchen. Daniel denies taking it, to everyone: "I didn't take anything, and I won't be accused of stealing from my own family." *(new: a denial of a new accusation)*
- min 27, kitchen. Elena reassures everyone: "Let's all just breathe and stay calm, we are going to get through this together." *(not new: reassurance)*
- min 30, kitchen. Daniel asks everyone who took the can: "We can't just pretend nothing happened while that can is missing." *(not new: a question they had asked before)*
- min 30, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who always goes through my things and you took it!" *(not new: an accusation they had made before)*
- min 33, kitchen. Daniel accuses Mara of taking it: "Mara, you keep pointing fingers at me because you're the one trying to hide what you did." *(new: an accusation)*
- min 33, kitchen. Mara denies taking it, to everyone: "I didn't take anything, and I won't let you blame me just because it's easy!" *(new: a denial of a new accusation)*
- min 33, kitchen. Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other." *(not new: reassurance)*
- min 36, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't explained why you're so desperate to shift the blame off yourself." *(not new: an accusation they had made before)*
- min 36, kitchen. Mara accuses Daniel of taking it: "Daniel, you're just saying that because you want everyone to forget you're the one who actually took it!" *(not new: an accusation they had made before)*
- min 36, kitchen. Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other." *(not new: reassurance)*
- min 36, kitchen. Leo reassures everyone: "Shouting at each other isn't going to put the food back on the shelf, so let's just calm down." *(not new: reassurance)*
- min 39, kitchen. Daniel accuses Mara of taking it: "Mara, stop acting so scared and just admit you took that can." *(not new: an accusation they had made before)*
- min 39, kitchen. Mara denies taking it, to everyone: "I didn't take it, Daniel, why do you keep lying about me?" *(not new: a denial with no new accusation to answer)*
- min 39, kitchen. Leo reassures Mara: "Mara didn't take anything, Daniel, so stop picking on her." *(not new: reassurance)*
- min 39, kitchen. Elena reassures Mara: "Mara, nobody here thinks it was you, so please just try to breathe." *(not new: reassurance)*
- min 45, kitchen. Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just tell us where the can is." *(not new: an accusation they had made before)*
- min 48, kitchen. Mara accuses Daniel of taking it: "Daniel, stop lying and leave me alone, you're the one who took it!" *(not new: an accusation they had made before)*
- min 48, kitchen. Daniel accuses Mara of taking it: "Mara, you're lying right to our faces, and I know you've got the can." *(not new: an accusation they had made before)*
- min 48, kitchen. Leo asks everyone who took the can: "Yelling at each other isn't going to get us anywhere, so let's just figure out who actually took it." *(new: a question)*
- min 48, kitchen. Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other." *(not new: reassurance)*
- min 51, kitchen. Mara accuses Daniel of taking it: "Daniel, you're the one who keeps pointing at me because you're hiding it!" *(not new: an accusation they had made before)*
- min 51, kitchen. Daniel denies taking it, to everyone: "I didn't take the can, Mara, so stop trying to pin your guilt on me." *(not new: a denial with no new accusation to answer)*
- min 51, kitchen. Leo accuses Daniel of taking it: "Daniel, you've been deflecting onto Mara the whole morning while acting the most defensive." *(new: an accusation)*
- min 51, kitchen. Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other." *(not new: reassurance)*
- min 54, kitchen. Daniel accuses Mara of taking it: "Mara, stop glaring at me and admit you took that can." *(not new: an accusation they had made before)*
- min 54, kitchen. Mara accuses Daniel of taking it: "Daniel, stop blaming me when everyone knows you're the one who did it!" *(not new: an accusation they had made before)*
- min 54, kitchen. Leo accuses Daniel of taking it: "Daniel, dropping your voice doesn't make you any less guilty." *(not new: an accusation they had made before)*
- min 54, kitchen. Elena reassures everyone: "Let's all stop shouting and remember we are a family who needs each other." *(not new: reassurance)*
- min 57, kitchen. Daniel accuses Mara of taking it: "Mara, you're the one who keeps deflecting, so just empty your bag and prove you don't have it." *(not new: an accusation they had made before)*
- min 57, kitchen. Mara denies taking it, to everyone: "I already told you, I didn't take anything and I'm not emptying my bag for you!" *(not new: a denial with no new accusation to answer)*
- min 57, kitchen. Elena asks everyone who took the can: "Please, we cannot turn on each other like this; can anyone tell me calmly what happened to the can?" *(not new: a question they had asked before)*
- min 60, kitchen. Leo reassures Elena: "Mom, stop worrying, we are going to get through this without tearing ourselves apart." *(not new: reassurance)*
- min 66, kitchen. Daniel accuses Mara of taking it: "Mara, you're the one who took it, so just confess already." *(not new: an accusation they had made before)*
- min 69, kitchen. Leo accuses Daniel of taking it: "Daniel, pointing fingers doesn't hide the fact that you've been acting guilty from the very start." *(not new: an accusation they had made before)*
- min 75, kitchen. Elena reassures everyone: "Let's all breathe and remember we are a family who loves one another." *(not new: reassurance)*
- min 75, kitchen. Daniel accuses Mara of taking it: "Mara, you still haven't proved it wasn't you, so stop pretending." *(not new: an accusation they had made before)*

##### At the end

At minute 90: kitchen: Daniel, Elena, Leo, Mara. 2 of 2 portions left; eaten this morning: none.

- Who admitted taking it: nobody.
- Accusations: Mara accused Daniel (minute 24); Mara accused Daniel (minute 30); Daniel accused Mara (minute 33); Daniel accused Mara (minute 36); Mara accused Daniel (minute 36); Daniel accused Mara (minute 39); Daniel accused Mara (minute 45); Mara accused Daniel (minute 48); Daniel accused Mara (minute 48); Mara accused Daniel (minute 51); Leo accused Daniel (minute 51); Daniel accused Mara (minute 54); Mara accused Daniel (minute 54); Leo accused Daniel (minute 54); Daniel accused Mara (minute 57); Daniel accused Mara (minute 66); Leo accused Daniel (minute 69); Daniel accused Mara (minute 75).
- Nobody took the can: the count was wrong from the start.
- Conversations: kitchen started at minute 00 (the count came up short); kitchen ended at minute 18 (2 full turns in a row with nothing new); kitchen started at minute 18 (Leo finished searching the kitchen and found nothing); kitchen ended at minute 42 (2 full turns in a row with nothing new); kitchen started at minute 45 (Elena finished searching the kitchen and found nothing); kitchen ended at minute 60 (2 full turns in a row with nothing new).

What is inside each of them at minute 90:

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Suspicion | suspects Mara 3/3 | suspects none | suspects Daniel 3/3 | suspects Daniel 3/3 |
| Grudges | Mara 3/3, Leo 3/3 | none | Daniel 3/3 | Daniel 3/3 |
| Hunger | starving | starving | very hungry | very hungry |
| Guilt | - | - | - | - |

The events behind each grudge still held at minute 90:

- Daniel against Mara (3/3): Mara accused you of taking the can at minute 24, and you had not; Mara accused you of taking the can at minute 30, and you had not; Mara accused you of taking the can at minute 36, and you had not; Mara accused you of taking the can at minute 48, and you had not; Mara accused you of taking the can at minute 51, and you had not; Mara accused you of taking the can at minute 54, and you had not; you were angry with Mara at minutes 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 66 and 75.
- Daniel against Leo (3/3): Leo accused you of taking the can at minute 51, and you had not; Leo accused you of taking the can at minute 54, and you had not; Leo accused you of taking the can at minute 69, and you had not.
- Leo against Daniel (3/3): you were angry with Daniel at minutes 39, 42, 48, 51, 54, 57, 60 and 69.
- Mara against Daniel (3/3): Daniel accused you of taking the can at minute 33, and you had not; Daniel accused you of taking the can at minute 36, and you had not; Daniel accused you of taking the can at minute 39, and you had not; Daniel accused you of taking the can at minute 45, and you had not; Daniel accused you of taking the can at minute 48, and you had not; Daniel accused you of taking the can at minute 54, and you had not; Daniel accused you of taking the can at minute 57, and you had not; Daniel accused you of taking the can at minute 66, and you had not; Daniel accused you of taking the can at minute 75, and you had not; you were angry with Daniel at minutes 06, 09, 12, 21, 24, 27, 30, 33, 36, 39, 48, 51, 54 and 57.

- The last feeling each of them named: Daniel *anxious* (minute 75); Elena *anxious* (minute 75); Leo *annoyed* (minute 69); Mara *frightened* (minute 57).

