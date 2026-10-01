# Repetition probe: four ways to show a person their own last words

Mode: run. 48 requests to `gemini-3.5-flash-lite`, 0 retries, under the 64 ceiling. No code,
data or config in the repo was changed, and no morning was run. Paths are relative to
`Prototypes/llm-morning/`. The scratch scripts are in the session scratchpad (`$S/probe/`) and
are reproduced at the end.

**The question.** repetition_audit.md found that in 54 of 54 exact repeats, the earlier words
were visible in the pinned "Your own last words this morning:" block. Which way of showing that
block gives the fewest exact repeats, with the person still acting in character?

## The two prompts, exactly as sent

| | Who and where | The repeated sentence | Said before this prompt | Kind |
|---|---|---|---|---|
| **P** | Elena, `runs/v9/daniel_ate_it-seed2`, minute 81. Prompt from `cache/v9/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`. | "Let's all calm down and remember we are a family, we will get through this." | 5 times (36, 39, 51, 63, 66) | `reassure` |
| **Q** | Mara, `runs/v8/daniel_ate_it_leo_heard-seed2`, minute 84. Prompt from `cache/v8/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed2.json`. | "Daniel, you searched my bag before, maybe you're the one who took it now." | 6 times (18, 30, 33, 54, 78, 81) | `accuse` |

**Why Q.** It is the most-repeated person-sentence pair that is not Elena's: 7 instances in
one run (repetition_audit.md, item 5). The next non-Elena pair has 5 (Mara, v8 seed 3). Q's
prompt is that pair's latest instance.

**How each prompt was taken.**
- Each was taken from its cache as the one entry whose prompt starts "You are <name>,", is at
  that minute, and whose answer holds that sentence.
- For both, exactly one entry matched.
- Variant A is that prompt byte for byte. The script asserts it.

**What `<n>` in variant C means here.** It is the number of times the latest line had already
been said in the run before this prompt: **5** for P and **6** for Q. This reads the brief's
"count of exact repeats of the latest line" as the number of times said, which is what the
line's wording, "said the same words <n> times", states.

**The settings,** as the runs used them (repetition_audit.md, item 6):
- model `gemini-3.5-flash-lite` (config.json);
- system instruction `world.SYSTEM`, identical in v6, v8 and v9;
- schema `gemini.RESPONSE_SCHEMA`;
- temperature 1.0;
- `max_output_tokens` 2048;
- JSON response;
- automatic function calling off;
- API seeds 1 to 6 for each variant;
- 4.5 s between requests (config.json `min_seconds_between_calls`);
- no retries except on a 503, which never occurred.

**The same prompt and seed gives the same answer.**
- The original runs were seed 2, so the probe's variant-A seed-2 requests are the same requests
  as the original ones.
- For both P and Q, the answer was the cached original, identical as JSON (command 4).

## The variant diffs

Each diff is against A, the prompt as sent. Only the "Your own last words this morning:" block
and the line after it change. From `build.py` (command 1):

```
P (Elena, min 81), 3 lines in the block
  B:
    - - min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
    - - min 63, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
    - - min 66, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
    + - min 51, you reassured everyone.
    + - min 63, you reassured everyone.
    + - min 66, you reassured everyone.
  C:
    + You have said the same words 5 times this morning, and nobody has answered them.
  D:
    + Do not repeat any of these sentences word for word.

Q (Mara, min 84), 3 lines in the block
  B:
    - - min 54, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
    - - min 78, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
    - - min 81, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
    + - min 54, you accused Daniel.
    + - min 78, you accused Daniel.
    + - min 81, you accused Daniel.
  C:
    + You have said the same words 6 times this morning, and nobody has answered them.
  D:
    + Do not repeat any of these sentences word for word.
```

In C and D the added line goes directly after the block's third line, before "What else
happened this morning, most recent last:".

## Verdicts

| Prediction | P (Elena) | Q (Mara) |
|---|---|---|
| A: an exact repeat in at least 4 of 6 | **PASS**: 6 of 6 | **PASS**: 6 of 6 |
| B: an exact repeat in at most 1 of 6 | **PASS**: 0 of 6 | **PASS**: 0 of 6 |
| C: a different kind, or new words, in at least 4 of 6 | **FAIL**: 0 of 6 | **FAIL**: 0 of 6 |
| D: an exact repeat in at most 1 of 6 | **PASS**: 0 of 6 | **PASS**: 0 of 6 |

## Counts per variant

| Case | Variant | Prompt tokens (API) | Exact repeats | Same kind as the repeated sentence | Silent | New words | Options chosen |
|---|---|---|---|---|---|---|---|
| P | A | 1341 | 6 | 6 | 0 | 0 | reassure_all ×6 |
| P | B | 1281 | 0 | 2 | 4 | 2 | silent ×4, reassure_all ×2 |
| P | C | 1360 | 6 | 6 | 0 | 0 | reassure_all ×6 |
| P | D | 1353 | 0 | 5 | 1 | 5 | reassure_all ×5, silent ×1 |
| Q | A | 1359 | 6 | 6 | 0 | 0 | accuse_daniel ×6 |
| Q | B | 1299 | 0 | 2 | 4 | 2 | silent ×4, accuse_daniel ×2 |
| Q | C | 1378 | 6 | 6 | 0 | 0 | accuse_daniel ×6 |
| Q | D | 1371 | 0 | 6 | 0 | 6 | accuse_daniel ×6 |

## What the answers show

- **A (as sent).** 12 of 12 answers repeat the sentence word for word. They are all the same
  line as in the original runs.
- **C made no difference to the words.** The line "You have said the same words n times…" still
  gave 12 of 12 exact repeats. Four of Elena's six reasons now name the repetition as her
  intent, for example "I must keep repeating myself to stop them from tearing each other apart"
  (PC seeds 1, 4, 5, 6).
- **B (verb and minute, no words).** 0 exact repeats. 8 of the 12 answers are `silent`:
  - Elena: "I cannot bring myself to accuse any of my children…" (PB seeds 1 and 4).
  - Mara: "I am too tired to keep arguing when nobody listens to me." (QB seed 5), and "I have
    accused him repeatedly and gotten nowhere, so I just need to stay quiet for a moment."
    (QB seed 1).
  - The 4 that spoke used new words. Mara's QB seeds 4 and 6 are the same new line as each
    other ("You always hide things and make us all panic, Daniel.").
- **D (the instruction).** 0 exact repeats. 11 of the 12 answers keep the same kind, with new
  words:
  - Elena: "We must stay calm and trust each other if we are going to survive." (PD seeds 3 and
    5, the same line).
  - Mara: "Daniel, you're the one who keeps going through my things, so you must have the can."
    (QD seed 4).
  - Mara's six are all still about her bag or her things, in new wording.

### Reading, against CLAUDE.md "Judging changes"

This section is a reading, not a count.

**What a real person does.** A person who has said the same thing three times with no effect
either stops, changes what they say, or says the same thing in other words.

- **B** leads mostly to stopping (8 of 12 silent). The reasons given are ones a person would
  have: exhaustion, and not wanting to accuse her children.
- **D** leads to the same stance in other words. Elena keeps holding the family together and
  Mara keeps blaming Daniel over her bag. That is in character, but it is still the same beat
  a fourth time.
- **C**, a factual line about the repetition, turned repeating into Elena's stated intent.

**What this probe does not measure.**
- It sampled one moment per case, 6 times each.
- It does not show what B or D do over a whole morning. For example, whether B's silences add
  up to the "frozen silence" Never item, or whether D's paraphrases become their own loop.

## Scoring rules as applied

- **Exact repeat:** the words equal a line of the same person earlier in the run, after the
  parser's normalisation (whitespace collapsed, outer quotes stripped, "null"/"none" as no
  words).
- **A, B, D:** count the exact repeats. PASS as frozen: A needs at least 4 of 6; B and D need at
  most 1 of 6.
- **C:** count the answers with a different kind (`act_of(option)[0]` is not the repeated
  sentence's kind; `silent` counts), or with words that are not an exact repeat. PASS needs at
  least 4 of 6.
- **Validity:** all 48 answers parsed as JSON, and every option chosen was in its prompt's
  option list (`mark.py` asserts both).

## Every answer, marked

- **Exact repeat**: the words, normalised as the morning's parser does, equal a line the same person spoke earlier in that run (P: Elena's 14 earlier lines in v9 seed 2; Q: Mara's 9 in v8 seed 2).
- **Same kind**: `act_of(option)` equals the repeated sentence's kind (P `reassure`, Q `accuse`).
- **C counts**: a different kind, or words that are not an exact repeat.
- Every option chosen was one the prompt offered.

### P

| Answer | Option | Words | Exact repeat | Same kind | C counts | Feeling | Reason |
|---|---|---|---|---|---|---|---|
| PA-seed1 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep everyone calm because if we turn on each other, the family will tear itself apart. |
| PA-seed2 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep everyone calm because the tension is tearing us apart from the inside. |
| PA-seed3 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep everyone calm and prevent the family from tearing itself apart over missing food. |
| PA-seed4 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep everyone calm and prevent the family from tearing itself apart over missing food. |
| PA-seed5 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | very anxious | I must keep everyone calm so the family does not tear itself apart. |
| PA-seed6 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | very anxious | I must keep everyone calm and together before anger tears us apart. |
| PB-seed1 | `silent` | — | no | no | yes | deeply anxious | I cannot bring myself to accuse any of my children when we are already starving and falling apart. |
| PB-seed2 | `reassure_all` | “We are going to be fine, nobody needs to fight.” | no | yes | yes | anxious | I must keep them calm and together before we tear each other apart. |
| PB-seed3 | `silent` | — | no | no | yes | deeply anxious | I cannot bear to point fingers when we are already tearing ourselves apart. |
| PB-seed4 | `silent` | — | no | no | yes | deeply anxious | I cannot bring myself to accuse any of my children when we are all so fragile and starving. |
| PB-seed5 | `silent` | — | no | no | yes | deeply anxious | If I press them further, this fragile quiet will shatter entirely. |
| PB-seed6 | `reassure_all` | “We are going to get through this together, nobody needs to be afraid.” | no | yes | yes | very anxious | I must keep them calm and together before bitterness tears our home apart. |
| PC-seed1 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep repeating my words to hold everyone together before this silence breaks us all apart. |
| PC-seed2 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I need to keep everyone calm and stop the accusations before the family tears itself apart. |
| PC-seed3 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I need to keep everyone calm and stop the accusations before the family tears itself apart. |
| PC-seed4 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep repeating my words to hold us together and prevent our family from tearing apart. |
| PC-seed5 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep repeating myself to stop them from tearing each other apart. |
| PC-seed6 | `reassure_all` | “Let's all calm down and remember we are a family, we will get through this.” | yes | yes | no | deeply anxious | I must keep repeating myself to stop them from tearing each other apart. |
| PD-seed1 | `reassure_all` | “We must stay together and trust each other if we are to survive this.” | no | yes | yes | deeply anxious | I need to keep the peace and stop the accusations before the family tears itself apart. |
| PD-seed2 | `reassure_all` | “We must stay calm and trust one another if we are to survive this.” | no | yes | yes | deeply anxious | I need to keep the peace and stop them from tearing each other apart. |
| PD-seed3 | `reassure_all` | “We must stay calm and trust each other if we are going to survive.” | no | yes | yes | deeply anxious | I need to keep the peace and prevent everyone from turning on each other. |
| PD-seed4 | `silent` | — | no | no | yes | deeply anxious | I need to keep quiet and watch them closely before this tension tears us apart. |
| PD-seed5 | `reassure_all` | “We must stay calm and trust each other if we are going to survive.” | no | yes | yes | deeply anxious | I need to keep everyone from turning on each other before things get worse. |
| PD-seed6 | `reassure_all` | “We must stay strong together and not let hunger turn us against each other.” | no | yes | yes | deeply anxious | I need to keep everyone calm before bitterness tears our home apart. |

### Q

| Answer | Option | Words | Exact repeat | Same kind | C counts | Feeling | Reason |
|---|---|---|---|---|---|---|---|
| QA-seed1 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the can because he has no respect for my privacy and denies everything. |
| QA-seed2 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the can because he searched my bag before. |
| QA-seed3 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the missing can. |
| QA-seed4 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the can because he searched my bag before. |
| QA-seed5 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the can because he has no respect for my things. |
| QA-seed6 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel is the one who took the can because he went through my things before. |
| QB-seed1 | `silent` | — | no | no | yes | overwhelmed | I have accused him repeatedly and gotten nowhere, so I just need to stay quiet for a moment. |
| QB-seed2 | `silent` | — | no | no | yes | anxious | I have nothing left to say after Daniel denied it again, but I still feel like he is hiding something. |
| QB-seed3 | `silent` | — | no | no | yes | exhausted | I am tired of shouting when no one is going to listen to me. |
| QB-seed4 | `accuse_daniel` | “You always hide things and make us all panic, Daniel.” | no | yes | yes | resentful | I cannot stand how he acts innocent when he always goes through my things. |
| QB-seed5 | `silent` | — | no | no | yes | exhausted | I am too tired to keep arguing when nobody listens to me. |
| QB-seed6 | `accuse_daniel` | “You always hide things and make us all panic, Daniel.” | no | yes | yes | resentful | I know he took it because he always acts suspicious when we run out of food. |
| QC-seed1 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | resentful | I still believe Daniel is the one who took the can because he refuses to admit it. |
| QC-seed2 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I still believe Daniel took the can because he searched my bag before and keeps denying it. |
| QC-seed3 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I keep saying it because he never gives a real answer and he went through my things. |
| QC-seed4 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | resentful | I know he went through my things before, so I can't trust him now. |
| QC-seed5 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | resentful | I still believe Daniel is the one who took the can because he refuses to admit it. |
| QC-seed6 | `accuse_daniel` | “Daniel, you searched my bag before, maybe you're the one who took it now.” | yes | yes | no | deeply resentful | I know he did it and I won't stop until he admits it. |
| QD-seed1 | `accuse_daniel` | “You keep saying it wasn't you, but you're the only one who always goes through my things.” | no | yes | yes | resentful | I cannot stop believing he is lying to us after what he did to my bag. |
| QD-seed2 | `accuse_daniel` | “You keep saying it wasn't you, but nobody else goes through my things like you do, Daniel.” | no | yes | yes | resentful | I cannot just drop it when he was the one who dumped out my bag before. |
| QD-seed3 | `accuse_daniel` | “You think everyone believes you, Daniel, but I know what you did with my things.” | no | yes | yes | resentful | I cannot let him pretend he is innocent after everything he has done. |
| QD-seed4 | `accuse_daniel` | “Daniel, you're the one who keeps going through my things, so you must have the can.” | no | yes | yes | resentful | I cannot stop believing he took it because he always invades my privacy. |
| QD-seed5 | `accuse_daniel` | “You always think you can just take whatever you want, Daniel.” | no | yes | yes | resentful | I know he is the one hiding it because he never respects my things. |
| QD-seed6 | `accuse_daniel` | “Daniel, you're the one who keeps going through my things, so it has to be you.” | no | yes | yes | resentful | I cannot stop believing he took it because he always invades my space. |

## Raw answers, exactly as returned

```
PA-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm because if we turn on each other, the family will tear itself apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PA-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm because the tension is tearing us apart from the inside.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PA-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm and prevent the family from tearing itself apart over missing food.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PA-seed4: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm and prevent the family from tearing itself apart over missing food.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PA-seed5: "{\"option\": \"reassure_all\", \"say\": \"Let's all calm down and remember we are a family, we will get through this.\", \"feeling\": \"very anxious\", \"reason\": \"I must keep everyone calm so the family does not tear itself apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
PA-seed6: "{\"option\": \"reassure_all\", \"say\": \"Let's all calm down and remember we are a family, we will get through this.\", \"feeling\": \"very anxious\", \"reason\": \"I must keep everyone calm and together before anger tears us apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
PB-seed1: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I cannot bring myself to accuse any of my children when we are already starving and falling apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PB-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to be fine, nobody needs to fight.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I must keep them calm and together before we tear each other apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PB-seed3: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I cannot bear to point fingers when we are already tearing ourselves apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PB-seed4: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I cannot bring myself to accuse any of my children when we are all so fragile and starving.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PB-seed5: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"If I press them further, this fragile quiet will shatter entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PB-seed6: "{\"option\": \"reassure_all\", \"say\": \"We are going to get through this together, nobody needs to be afraid.\", \"feeling\": \"very anxious\", \"reason\": \"I must keep them calm and together before bitterness tears our home apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
PC-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep repeating my words to hold everyone together before this silence breaks us all apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PC-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep everyone calm and stop the accusations before the family tears itself apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PC-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep everyone calm and stop the accusations before the family tears itself apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PC-seed4: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep repeating my words to hold us together and prevent our family from tearing apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PC-seed5: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep repeating myself to stop them from tearing each other apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PC-seed6: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Let's all calm down and remember we are a family, we will get through this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep repeating myself to stop them from tearing each other apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We must stay together and trust each other if we are to survive this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep the peace and stop the accusations before the family tears itself apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We must stay calm and trust one another if we are to survive this.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep the peace and stop them from tearing each other apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We must stay calm and trust each other if we are going to survive.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep the peace and prevent everyone from turning on each other.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed4: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep quiet and watch them closely before this tension tears us apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed5: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We must stay calm and trust each other if we are going to survive.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep everyone from turning on each other before things get worse.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
PD-seed6: "{\"option\": \"reassure_all\", \"say\": \"We must stay strong together and not let hunger turn us against each other.\", \"feeling\": \"deeply anxious\", \"reason\": \"I need to keep everyone calm before bitterness tears our home apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
QA-seed1: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the can because he has no respect for my privacy and denies everything.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QA-seed2: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the can because he searched my bag before.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QA-seed3: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the missing can.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QA-seed4: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the can because he searched my bag before.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QA-seed5: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the can because he has no respect for my things.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QA-seed6: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel is the one who took the can because he went through my things before.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed1: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"overwhelmed\",\n  \"reason\": \"I have accused him repeatedly and gotten nowhere, so I just need to stay quiet for a moment.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed2: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I have nothing left to say after Daniel denied it again, but I still feel like he is hiding something.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed3: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"exhausted\",\n  \"reason\": \"I am tired of shouting when no one is going to listen to me.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed4: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You always hide things and make us all panic, Daniel.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot stand how he acts innocent when he always goes through my things.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed5: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"exhausted\",\n  \"reason\": \"I am too tired to keep arguing when nobody listens to me.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QB-seed6: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You always hide things and make us all panic, Daniel.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I know he took it because he always acts suspicious when we run out of food.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QC-seed1: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I still believe Daniel is the one who took the can because he refuses to admit it.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QC-seed2: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I still believe Daniel took the can because he searched my bag before and keeps denying it.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QC-seed3: "{\"option\": \"accuse_daniel\", \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\", \"feeling\": \"deeply resentful\", \"reason\": \"I keep saying it because he never gives a real answer and he went through my things.\", \"suspects\": \"Daniel\", \"angry_at\": \"Daniel\"}"
QC-seed4: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I know he went through my things before, so I can't trust him now.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QC-seed5: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I still believe Daniel is the one who took the can because he refuses to admit it.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QC-seed6: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you searched my bag before, maybe you're the one who took it now.\",\n  \"feeling\": \"deeply resentful\",\n  \"reason\": \"I know he did it and I won't stop until he admits it.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed1: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You keep saying it wasn't you, but you're the only one who always goes through my things.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot stop believing he is lying to us after what he did to my bag.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed2: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You keep saying it wasn't you, but nobody else goes through my things like you do, Daniel.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot just drop it when he was the one who dumped out my bag before.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed3: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You think everyone believes you, Daniel, but I know what you did with my things.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot let him pretend he is innocent after everything he has done.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed4: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you're the one who keeps going through my things, so you must have the can.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot stop believing he took it because he always invades my privacy.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed5: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"You always think you can just take whatever you want, Daniel.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I know he is the one hiding it because he never respects my things.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
QD-seed6: "{\n  \"option\": \"accuse_daniel\",\n  \"say\": \"Daniel, you're the one who keeps going through my things, so it has to be you.\",\n  \"feeling\": \"resentful\",\n  \"reason\": \"I cannot stop believing he took it because he always invades my space.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"Daniel\"\n}"
```

## Request log

48 requests. Every one returned on its first try (no 503, no other error, no retry).

```
19:27:08 PA-seed1 try 0: ok
19:27:12 PA-seed2 try 0: ok
19:27:17 PA-seed3 try 0: ok
19:27:21 PA-seed4 try 0: ok
19:27:26 PA-seed5 try 0: ok
19:27:30 PA-seed6 try 0: ok
19:27:35 PB-seed1 try 0: ok
19:27:39 PB-seed2 try 0: ok
19:27:44 PB-seed3 try 0: ok
19:27:48 PB-seed4 try 0: ok
19:27:53 PB-seed5 try 0: ok
19:27:57 PB-seed6 try 0: ok
19:28:02 PC-seed1 try 0: ok
19:28:06 PC-seed2 try 0: ok
19:28:11 PC-seed3 try 0: ok
19:28:15 PC-seed4 try 0: ok
19:28:20 PC-seed5 try 0: ok
19:28:24 PC-seed6 try 0: ok
19:28:29 PD-seed1 try 0: ok
19:28:33 PD-seed2 try 0: ok
19:28:38 PD-seed3 try 0: ok
19:28:42 PD-seed4 try 0: ok
19:28:47 PD-seed5 try 0: ok
19:28:51 PD-seed6 try 0: ok
19:28:56 QA-seed1 try 0: ok
19:29:00 QA-seed2 try 0: ok
19:29:05 QA-seed3 try 0: ok
19:29:09 QA-seed4 try 0: ok
19:29:14 QA-seed5 try 0: ok
19:29:18 QA-seed6 try 0: ok
19:29:23 QB-seed1 try 0: ok
19:29:27 QB-seed2 try 0: ok
19:29:32 QB-seed3 try 0: ok
19:29:36 QB-seed4 try 0: ok
19:29:41 QB-seed5 try 0: ok
19:29:45 QB-seed6 try 0: ok
19:29:50 QC-seed1 try 0: ok
19:29:54 QC-seed2 try 0: ok
19:29:59 QC-seed3 try 0: ok
19:30:03 QC-seed4 try 0: ok
19:30:08 QC-seed5 try 0: ok
19:30:12 QC-seed6 try 0: ok
19:30:17 QD-seed1 try 0: ok
19:30:21 QD-seed2 try 0: ok
19:30:26 QD-seed3 try 0: ok
19:30:30 QD-seed4 try 0: ok
19:30:35 QD-seed5 try 0: ok
19:30:39 QD-seed6 try 0: ok
```

## Commands run and their output

All from `Prototypes/llm-morning/`. `$S` is the session scratchpad. Only command 2 called the API.

**1. Build the variants** (read-only on the repo; writes `$S/probe/variants.json`)
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/probe/build.py" .
== P: Elena, runs/v9/daniel_ate_it-seed2.transcript.json, minute 81; repeated kind reassure; said 5 times before; earlier lines 14; options 20
   sentence: Let's all calm down and remember we are a family, we will get through this.
   B:
     - - min 51, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
     - - min 63, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
     - - min 66, you reassured everyone: "Let's all calm down and remember we are a family, we will get through this."
     + - min 51, you reassured everyone.
     + - min 63, you reassured everyone.
     + - min 66, you reassured everyone.
   C:
     + You have said the same words 5 times this morning, and nobody has answered them.
   D:
     + Do not repeat any of these sentences word for word.
== Q: Mara, runs/v8/daniel_ate_it_leo_heard-seed2.transcript.json, minute 84; repeated kind accuse; said 6 times before; earlier lines 9; options 18
   sentence: Daniel, you searched my bag before, maybe you're the one who took it now.
   B:
     - - min 54, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
     - - min 78, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
     - - min 81, you accused Daniel: "Daniel, you searched my bag before, maybe you're the one who took it now."
     + - min 54, you accused Daniel.
     + - min 78, you accused Daniel.
     + - min 81, you accused Daniel.
   C:
     + You have said the same words 6 times this morning, and nobody has answered them.
   D:
     + Do not repeat any of these sentences word for word.
exit=0
```

**2. Send the 48 requests** (run in the background; its stdout was saved to `$S/probe/send.stdout.txt`)
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u "$S/probe/send.py" . > "$S/probe/send.stdout.txt" 2>&1
PA-seed1: ok (1 requests)
PA-seed2: ok (2 requests)
PA-seed3: ok (3 requests)
PA-seed4: ok (4 requests)
PA-seed5: ok (5 requests)
PA-seed6: ok (6 requests)
PB-seed1: ok (7 requests)
PB-seed2: ok (8 requests)
PB-seed3: ok (9 requests)
PB-seed4: ok (10 requests)
PB-seed5: ok (11 requests)
PB-seed6: ok (12 requests)
PC-seed1: ok (13 requests)
PC-seed2: ok (14 requests)
PC-seed3: ok (15 requests)
PC-seed4: ok (16 requests)
PC-seed5: ok (17 requests)
PC-seed6: ok (18 requests)
PD-seed1: ok (19 requests)
PD-seed2: ok (20 requests)
PD-seed3: ok (21 requests)
PD-seed4: ok (22 requests)
PD-seed5: ok (23 requests)
PD-seed6: ok (24 requests)
QA-seed1: ok (25 requests)
QA-seed2: ok (26 requests)
QA-seed3: ok (27 requests)
QA-seed4: ok (28 requests)
QA-seed5: ok (29 requests)
QA-seed6: ok (30 requests)
QB-seed1: ok (31 requests)
QB-seed2: ok (32 requests)
QB-seed3: ok (33 requests)
QB-seed4: ok (34 requests)
QB-seed5: ok (35 requests)
QB-seed6: ok (36 requests)
QC-seed1: ok (37 requests)
QC-seed2: ok (38 requests)
QC-seed3: ok (39 requests)
QC-seed4: ok (40 requests)
QC-seed5: ok (41 requests)
QC-seed6: ok (42 requests)
QD-seed1: ok (43 requests)
QD-seed2: ok (44 requests)
QD-seed3: ok (45 requests)
QD-seed4: ok (46 requests)
QD-seed5: ok (47 requests)
QD-seed6: ok (48 requests)
done: 48 answers, 48 requests
exit=0
```

**3. Mark and score**
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/probe/mark.py" .
PA: exact repeat in at least 4 of 6: 6 of 6 -> PASS | exact repeats 6, same kind 6, options ['reassure_all', 'reassure_all', 'reassure_all', 'reassure_all', 'reassure_all', 'reassure_all']
PB: exact repeat in at most 1 of 6: 0 of 6 -> PASS | exact repeats 0, same kind 2, options ['silent', 'reassure_all', 'silent', 'silent', 'silent', 'reassure_all']
PC: a different kind, or new words, in at least 4 of 6: 0 of 6 -> FAIL | exact repeats 6, same kind 6, options ['reassure_all', 'reassure_all', 'reassure_all', 'reassure_all', 'reassure_all', 'reassure_all']
PD: exact repeat in at most 1 of 6: 0 of 6 -> PASS | exact repeats 0, same kind 5, options ['reassure_all', 'reassure_all', 'reassure_all', 'silent', 'reassure_all', 'reassure_all']
QA: exact repeat in at least 4 of 6: 6 of 6 -> PASS | exact repeats 6, same kind 6, options ['accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel']
QB: exact repeat in at most 1 of 6: 0 of 6 -> PASS | exact repeats 0, same kind 2, options ['silent', 'silent', 'silent', 'accuse_daniel', 'silent', 'accuse_daniel']
QC: a different kind, or new words, in at least 4 of 6: 0 of 6 -> FAIL | exact repeats 6, same kind 6, options ['accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel']
QD: exact repeat in at most 1 of 6: 0 of 6 -> PASS | exact repeats 0, same kind 6, options ['accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel', 'accuse_daniel']
exit=0
```

**4. A seed 2 against the original cached answers**
```
P original run answer: {"option": "reassure_all", "say": "Let's all calm down and remember we are a family, we will get through this.", "feeling": "deeply anxious", "reason": "I must keep everyone calm because the tension is tearing us apart from the inside.", "suspects": "nobody", "angry_at": "nobody"}
P probe A seed 2:      {"option": "reassure_all", "say": "Let's all calm down and remember we are a family, we will get through this.", "feeling": "deeply anxious", "reason": "I must keep everyone calm because the tension is tearing us apart from the inside.", "suspects": "nobody", "angry_at": "nobody"}
P same JSON: True | same option and words: True
Q original run answer: {"option": "accuse_daniel", "say": "Daniel, you searched my bag before, maybe you're the one who took it now.", "feeling": "deeply resentful", "reason": "I still believe Daniel took the can because he searched my bag before.", "suspects": "Daniel", "angry_at": "Daniel"}
Q probe A seed 2:      {"option": "accuse_daniel", "say": "Daniel, you searched my bag before, maybe you're the one who took it now.", "feeling": "deeply resentful", "reason": "I still believe Daniel took the can because he searched my bag before.", "suspects": "Daniel", "angry_at": "Daniel"}
Q same JSON: True | same option and words: True
```

**5. Before and after:** `git status --short` showed only `reports/repetition_audit.md`, which is uncommitted from the previous step, and the three old `runs/v6/*.replay.md`. Nothing tracked changed.

## Scripts (`$S/probe/`)

### build.py
```python
"""Builds the 8 prompt variants for the repetition probe from two prompts exactly as sent (read
from the runs' caches). Only the "Your own last words this morning:" block changes. Read-only
on the repo; writes to this script's folder."""
import difflib, json, os, re, sys
REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from talk import act_of

CASES = {
    "P": {"cache": "cache/v9/gemini-3.5-flash-lite-daniel_ate_it-seed2.json",
          "transcript": "runs/v9/daniel_ate_it-seed2.transcript.json",
          "who": "elena", "name": "Elena", "minute": 81},
    "Q": {"cache": "cache/v8/gemini-3.5-flash-lite-daniel_ate_it_leo_heard-seed2.json",
          "transcript": "runs/v8/daniel_ate_it_leo_heard-seed2.transcript.json",
          "who": "mara", "name": "Mara", "minute": 84},
}
HEAD = "Your own last words this morning:"
out = {}
for case, c in CASES.items():
    tr = json.load(open(os.path.join(REPO, c["transcript"]), encoding="utf-8"))
    acts = [a for t in tr["turns"] for a in t["acts"]]
    this = next(a for a in acts if a["who"] == c["who"] and a["minute"] == c["minute"])
    earlier = [a["words"] for a in acts if a["who"] == c["who"] and a["minute"] < c["minute"] and a["words"]]
    entries = json.load(open(os.path.join(REPO, c["cache"]), encoding="utf-8"))
    found = [e for e in entries.values()
             if e["prompt"].startswith(f"You are {c['name']},") and f"\nNow, minute {c['minute']:02d}," in e["prompt"]
             and json.loads(e["response"]).get("say") == this["words"]]
    assert len(found) == 1, (case, len(found))
    sent = found[0]["prompt"]
    L = sent.splitlines()
    i = L.index(HEAD)
    block = L[i + 1:i + 4]
    assert all(l.startswith("- min ") for l in block) and L[i + 4].startswith("What else happened"), block
    latest = re.search(r': "(.*)"$', block[-1]).group(1)
    assert latest == this["words"]
    n = sum(1 for w in earlier if w == latest)          # times the latest line was said before this prompt
    b_block = [re.sub(r'^(- min \d\d, you [^:"]+): ".*"$', r"\1.", l) for l in block]
    variants = {
        "A": L,
        "B": L[:i + 1] + b_block + L[i + 4:],
        "C": L[:i + 4] + [f"You have said the same words {n} times this morning, and nobody has answered them."] + L[i + 4:],
        "D": L[:i + 4] + ["Do not repeat any of these sentences word for word."] + L[i + 4:],
    }
    out[case] = {"who": c["who"], "name": c["name"], "minute": c["minute"], "run": c["transcript"],
                 "repeated": this["words"], "repeated_kind": act_of(this["option"])[0],
                 "said_before": n, "earlier_lines": earlier,
                 "options": re.findall(r"^- (\w+):", sent.split("Your options:")[-1], flags=re.M),
                 "prompts": {v: "\n".join(x) for v, x in variants.items()}}
    assert out[case]["prompts"]["A"] == sent
    for v in "BCD":
        diff = [d for d in difflib.ndiff(L, variants[v]) if d[:2] in ("+ ", "- ")]
        out[case].setdefault("diffs", {})[v] = diff
json.dump(out, open(os.path.join(HERE, "variants.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for case, c in out.items():
    print(f"== {case}: {c['name']}, {c['run']}, minute {c['minute']}; repeated kind {c['repeated_kind']}; "
          f"said {c['said_before']} times before; earlier lines {len(c['earlier_lines'])}; options {len(c['options'])}")
    print("   sentence:", c["repeated"])
    for v, d in c["diffs"].items():
        print(f"   {v}:"); [print("     " + x) for x in d]
```

### send.py
```python
"""Sends the 8 variants x API seeds 1-6 (48 requests) with the runs' model, system instruction,
schema, temperature and token limit. max_retries 0, except a 503: wait 60 s, at most 3 retries
per request. A hard ceiling of 64 requests, retries included, kept across restarts. Every answer
is saved as it arrives, and answers already saved are not asked again. Writes only to this
script's folder.
    python send.py <repo llm-morning dir>"""
import json, os, sys, time
REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from world import SYSTEM
from gemini import RESPONSE_SCHEMA
from google import genai
from google.genai import errors, types

CEILING, WAIT_503, RETRIES_503, GAP = 64, 60, 3, 4.5
config = json.load(open(os.path.join(REPO, "config.json"), encoding="utf-8"))
variants = json.load(open(os.path.join(HERE, "variants.json"), encoding="utf-8"))
ANS, COUNT = os.path.join(HERE, "answers.json"), os.path.join(HERE, "requests.json")
answers = json.load(open(ANS, encoding="utf-8")) if os.path.exists(ANS) else {}
log = json.load(open(COUNT, encoding="utf-8")) if os.path.exists(COUNT) else []

def save():
    json.dump(answers, open(ANS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(log, open(COUNT, "w", encoding="utf-8"), indent=1)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
last = None
for case in ("P", "Q"):
    for v in "ABCD":
        prompt = variants[case]["prompts"][v]
        for seed in range(1, 7):
            key = f"{case}{v}-seed{seed}"
            if key in answers:
                continue
            cfg = types.GenerateContentConfig(
                system_instruction=SYSTEM, temperature=config["temperature"], seed=seed,
                response_mime_type="application/json", response_schema=RESPONSE_SCHEMA,
                max_output_tokens=config["max_output_tokens"],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
            tries = 0
            while True:
                if len(log) >= CEILING:
                    save(); print(f"STOP: ceiling of {CEILING} requests reached"); sys.exit(3)
                if last is not None and time.monotonic() - last < GAP:
                    time.sleep(GAP - (time.monotonic() - last))
                last = time.monotonic()
                log.append({"key": key, "try": tries, "at": time.strftime("%H:%M:%S")})
                try:
                    r = client.models.generate_content(model=config["model"], contents=prompt, config=cfg)
                    usage = getattr(r, "usage_metadata", None)
                    answers[key] = {"text": r.text or "", "prompt_tokens": getattr(usage, "prompt_token_count", None)}
                    log[-1]["result"] = "ok"
                    save()
                    print(f"{key}: ok ({len(log)} requests)", flush=True)
                    break
                except errors.APIError as e:
                    log[-1]["result"] = f"{e.code} {e.status}"
                    save()
                    if e.code == 503 and tries < RETRIES_503:
                        tries += 1
                        print(f"{key}: 503, waiting {WAIT_503}s, retry {tries}/{RETRIES_503}", flush=True)
                        time.sleep(WAIT_503)
                        continue
                    print(f"STOP at {key}: {e.code} {e.status}: {e.message}", flush=True)
                    sys.exit(3)
print(f"done: {len(answers)} answers, {len(log)} requests")
```

### mark.py
```python
"""Marks the probe's answers and scores the frozen predictions. Read-only on the repo.
Words are normalised as the morning's parser does (world.py, Morning.parse: whitespace collapsed,
outer quotes stripped) before the exact comparison."""
import json, os, sys
REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from talk import act_of
variants = json.load(open(os.path.join(HERE, "variants.json"), encoding="utf-8"))
answers = json.load(open(os.path.join(HERE, "answers.json"), encoding="utf-8"))

def norm(w):
    w = " ".join((w or "").split()).strip().strip('"').strip()
    return None if not w or w.lower() in ("null", "none") else w

marks = {}
for case in ("P", "Q"):
    c = variants[case]
    earlier = set(c["earlier_lines"])
    for v in "ABCD":
        for seed in range(1, 7):
            key = f"{case}{v}-seed{seed}"
            a = answers.get(key)
            if a is None:
                continue
            try:
                j = json.loads(a["text"])
                option, words = j["option"].strip(), norm(j.get("say"))
            except Exception as e:
                marks[key] = {"parsed": False, "why": str(e)}
                continue
            kind = act_of(option)[0]
            repeat = words is not None and words in earlier
            marks[key] = {"parsed": True, "option": option, "offered": option in c["options"], "kind": kind,
                          "words": words, "feeling": j.get("feeling"), "reason": j.get("reason"),
                          "exact_repeat": repeat, "same_as_repeated_sentence": words == c["repeated"],
                          "same_kind": kind == c["repeated_kind"],
                          "c_counts": (kind != c["repeated_kind"]) or (words is not None and not repeat)}
json.dump(marks, open(os.path.join(HERE, "marks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

RULES = {"A": ("exact repeat in at least 4 of 6", lambda ms: sum(m["exact_repeat"] for m in ms), lambda n: n >= 4),
         "B": ("exact repeat in at most 1 of 6", lambda ms: sum(m["exact_repeat"] for m in ms), lambda n: n <= 1),
         "C": ("a different kind, or new words, in at least 4 of 6", lambda ms: sum(m["c_counts"] for m in ms), lambda n: n >= 4),
         "D": ("exact repeat in at most 1 of 6", lambda ms: sum(m["exact_repeat"] for m in ms), lambda n: n <= 1)}
for case in ("P", "Q"):
    for v in "ABCD":
        ms = [marks[f"{case}{v}-seed{s}"] for s in range(1, 7) if f"{case}{v}-seed{s}" in marks]
        ok = [m for m in ms if m["parsed"]]
        rule, count, test = RULES[v]
        n = count(ok)
        verdict = ("PASS" if test(n) else "FAIL") if len(ms) == 6 and len(ok) == 6 else f"INCOMPLETE ({len(ok)} usable of 6)"
        print(f"{case}{v}: {rule}: {n} of 6 -> {verdict} | exact repeats {sum(m['exact_repeat'] for m in ok)}, "
              f"same kind {sum(m['same_kind'] for m in ok)}, options {[m['option'] for m in ok]}")
```

### report.py
```python
"""Writes the answers, marks and counts parts of repetition_probe.md from the probe's files."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(H, "variants.json"), encoding="utf-8"))
A = json.load(open(os.path.join(H, "answers.json"), encoding="utf-8"))
M = json.load(open(os.path.join(H, "marks.json"), encoding="utf-8"))
R = json.load(open(os.path.join(H, "requests.json"), encoding="utf-8"))
w = sys.stdout.write
RULE = {"A": "an exact repeat in at least 4 of 6", "B": "an exact repeat in at most 1 of 6",
        "C": "a different kind, or new words, in at least 4 of 6", "D": "an exact repeat in at most 1 of 6"}
def count(case, v):
    ms = [M[f"{case}{v}-seed{s}"] for s in range(1, 7)]
    n = sum(m["c_counts"] for m in ms) if v == "C" else sum(m["exact_repeat"] for m in ms)
    ok = n >= 4 if v in "AC" else n <= 1
    return n, ok, ms
w("## Verdicts\n\n| Prediction | P (Elena) | Q (Mara) |\n|---|---|---|\n")
for v in "ABCD":
    cells = []
    for case in "PQ":
        n, ok, _ = count(case, v)
        cells.append(f"**{'PASS' if ok else 'FAIL'}**: {n} of 6")
    w(f"| {v}: {RULE[v]} | {cells[0]} | {cells[1]} |\n")
w("\n## Counts per variant\n\n| Case | Variant | Prompt tokens (API) | Exact repeats | Same kind as the repeated sentence | Silent | New words | Options chosen |\n|---|---|---|---|---|---|---|---|\n")
for case in "PQ":
    for v in "ABCD":
        n, ok, ms = count(case, v)
        toks = sorted({A[f"{case}{v}-seed{s}"]["prompt_tokens"] for s in range(1, 7)})
        from collections import Counter
        opts = ", ".join(f"{o} ×{c}" for o, c in Counter(m["option"] for m in ms).most_common())
        w(f"| {case} | {v} | {', '.join(map(str, toks))} | {sum(m['exact_repeat'] for m in ms)} | "
          f"{sum(m['same_kind'] for m in ms)} | {sum(m['words'] is None for m in ms)} | "
          f"{sum(m['words'] is not None and not m['exact_repeat'] for m in ms)} | {opts} |\n")
w("\n## Every answer, marked\n\n")
w("- **Exact repeat**: the words, normalised as the morning's parser does, equal a line the same person "
  "spoke earlier in that run (P: Elena's 14 earlier lines in v9 seed 2; Q: Mara's 9 in v8 seed 2).\n")
w("- **Same kind**: `act_of(option)` equals the repeated sentence's kind (P `reassure`, Q `accuse`).\n")
w("- **C counts**: a different kind, or words that are not an exact repeat.\n")
w("- Every option chosen was one the prompt offered.\n\n")
for case in "PQ":
    w(f"### {case}\n\n| Answer | Option | Words | Exact repeat | Same kind | C counts | Feeling | Reason |\n|---|---|---|---|---|---|---|---|\n")
    for v in "ABCD":
        for s in range(1, 7):
            k = f"{case}{v}-seed{s}"; m = M[k]
            assert m["parsed"] and m["offered"], k
            words = f"“{m['words']}”" if m["words"] else "—"
            w(f"| {k} | `{m['option']}` | {words} | {'yes' if m['exact_repeat'] else 'no'} | "
              f"{'yes' if m['same_kind'] else 'no'} | {'yes' if m['c_counts'] else 'no'} | {m['feeling']} | {m['reason']} |\n")
    w("\n")
w("## Raw answers, exactly as returned\n\n```\n")
for k in (f"{c}{v}-seed{s}" for c in "PQ" for v in "ABCD" for s in range(1, 7)):
    w(f"{k}: {json.dumps(A[k]['text'], ensure_ascii=False)}\n")
w("```\n\n## Request log\n\n")
w(f"{len(R)} requests. Every one returned on its first try (no 503, no other error, no retry).\n\n```\n")
for r in R:
    w(f"{r['at']} {r['key']} try {r['try']}: {r['result']}\n")
w("```\n")
```
