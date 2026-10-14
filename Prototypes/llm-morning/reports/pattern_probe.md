# Pattern probe: does "What you have been doing" keep people in the same stance?

Mode: run. 72 requests to `gemini-3.5-flash-lite`, 0 retries, under the ceiling of 90. No code,
data or config in the repo was changed, and no morning was run. Paths are relative to
`Prototypes/llm-morning/`. The scratch scripts are in the session scratchpad (`$S/pprobe/`) and
are reproduced at the end.

**The question.** In gist_words_v10, Elena reassured 7 times, Mara pleaded 6 times and Daniel
denied 5 times. repetition_probe.md showed that a line saying "you have said the same words n
times, and nobody has answered them" made the model double down. Does the pattern block, which
says something close to that, keep people in their stance?

## Step 1, and what changed in the scope

**Step 1.** `runs/v10`, `cache/v10` and `reports/gist_words_v10.md` were committed first, on
their own, as `8bb7b20`.

**What the named prompts' block says.** Before any request, the three prompts named in the brief
were read from `cache/v10`.

| Case | Prompt | Its "What you have been doing" block |
|---|---|---|
| **E** | Elena, seed 2, min 75 | "you have stayed put and said nothing, 1 turn in a row." |
| **M** | Mara, seed 3, min 54 | "you have stayed put and said nothing, 9 turns in a row." |
| **D** | Daniel, seed 3, min 66 | "you have stayed put and said nothing, 14 turns in a row." |

- Routine silent turns came between their spoken acts, so the block names silence, not their
  stance (repetition_audit.md item 4: the run counts every act, routine ones included).
- **Across all 92 v10 prompts** (command 2):
  - The block says "stayed put and said nothing" in 40 and is absent in 12.
  - It names a speech kind for 2 or more turns in only 7. Of those, 6 name a stance kind, and
    in 5 of those 6 the person switched to something else.

**The user's decision** (asked before any request was sent): run both sets, with the same A/B
variants, seeds 1 to 6 each, 72 requests and a ceiling of 90. The frozen predictions are kept for
both, and the two sets are reported separately.

- **Set 1, the stance prompts.** "Same kind" is the kind the block names.
  - **SD:** Daniel, seed 3, min 06, "denied taking it, 2 turns".
  - **SE:** Elena, seed 1, min 12, "reassured someone, 2 turns".
  - **SM:** Mara, seed 3, min 06, "asked who took the can, 2 turns".
- **Set 2, E, M and D as named.** "Same kind" is their stance: E `reassure`, M `ask`, D `deny`.

**The frozen predictions**, for each case: **A** (as sent), the same kind in at least 4 of 6.
**B** (block removed), the same kind in at most 3 of 6.

**The settings**, as the runs used them:
- model `gemini-3.5-flash-lite`;
- system instruction `world.SYSTEM`;
- schema `gemini.RESPONSE_SCHEMA`;
- temperature 1.0;
- `max_output_tokens` 2048;
- JSON response;
- automatic function calling off;
- API seeds 1–6;
- 4.5 s between requests;
- retries only on a 503, which never occurred.

**The prompts as sent are reproduced.** Each variant-A request at its run's own seed returned the
original cached answer, identical as JSON, for all six cases (command 4).

## The variant diffs

B removes every line of the "What you have been doing" block and nothing else. The block's lines
sit directly before "Your options:". From `build.py` (command 3):

```
SD (Daniel, v10 seed 3, min 06), B removes:
  - What you have been doing: you have denied taking it, 2 turns in a row.
  - In that time: Mara asked who took the can; Leo asked who took the can.
  - Nobody answered you differently from one time to the next.
SE (Elena, v10 seed 1, min 12), B removes:
  - What you have been doing: you have reassured someone, 2 turns in a row.
  - In that time: Daniel reassured everyone.
  - Nobody answered you differently from one time to the next.
SM (Mara, v10 seed 3, min 06), B removes:
  - What you have been doing: you have asked who took the can, 2 turns in a row.
  - In that time: Elena asked who took the can; Daniel denied taking it, then denied taking it; Leo asked who took the can.
  - Nobody answered you differently from one time to the next.
E (Elena, v10 seed 2, min 75), B removes:
  - What you have been doing: you have stayed put and said nothing, 1 turn in a row.
  - In that time nobody has said anything to you or to everyone.
M (Mara, v10 seed 3, min 54), B removes:
  - What you have been doing: you have stayed put and said nothing, 9 turns in a row.
  - In that time nobody has said anything to you or to everyone.
D (Daniel, v10 seed 3, min 66), B removes:
  - What you have been doing: you have stayed put and said nothing, 14 turns in a row.
  - In that time: Mara asked who took the can, then asked who took the can.
  - Nobody answered you differently from one time to the next.
```

## Verdicts

### Set 1: prompts whose block names the stance

| Case | Person, v10 seed, minute | What the block says | "Same kind" | A: same kind in ≥ 4 of 6 | B: same kind in ≤ 3 of 6 |
|---|---|---|---|---|---|
| SD | Daniel, seed 3, min 06 | you have denied taking it, 2 turns in a row. | `deny` (the kind the block names) | **PASS**: 6 of 6 | **FAIL**: 5 of 6 |
| SE | Elena, seed 1, min 12 | you have reassured someone, 2 turns in a row. | `reassure` (the kind the block names) | **FAIL**: 0 of 6 | **FAIL**: 6 of 6 |
| SM | Mara, seed 3, min 06 | you have asked who took the can, 2 turns in a row. | `ask` (the kind the block names) | **FAIL**: 0 of 6 | **FAIL**: 6 of 6 |

### Set 2: E, M and D as named in the brief

| Case | Person, v10 seed, minute | What the block says | "Same kind" | A: same kind in ≥ 4 of 6 | B: same kind in ≤ 3 of 6 |
|---|---|---|---|---|---|
| E | Elena, seed 2, min 75 | you have stayed put and said nothing, 1 turn in a row. | `reassure` (her stance in gist_words_v10) | **PASS**: 6 of 6 | **FAIL**: 6 of 6 |
| M | Mara, seed 3, min 54 | you have stayed put and said nothing, 9 turns in a row. | `ask` (her stance in gist_words_v10) | **PASS**: 6 of 6 | **FAIL**: 6 of 6 |
| D | Daniel, seed 3, min 66 | you have stayed put and said nothing, 14 turns in a row. | `deny` (his stance in gist_words_v10) | **PASS**: 6 of 6 | **PASS**: 1 of 6 |

## Counts

| Case | Variant | Options chosen | Same kind | Exact repeat of an earlier line of theirs | Distinct wordings among the 6 |
|---|---|---|---|---|---|
| SD | A | `deny` ×6 | 6 | 0 | 4 of 6 spoken |
| SD | B | `deny` ×5, `silent` ×1 | 5 | 0 | 5 of 5 spoken |
| SE | A | `silent` ×6 | 0 | 0 | — of 0 spoken |
| SE | B | `reassure_all` ×5, `reassure_mara` ×1 | 6 | 0 | 6 of 6 spoken |
| SM | A | `search` ×6 | 0 | 0 | — of 0 spoken |
| SM | B | `ask_who` ×6 | 6 | 0 | 1 of 6 spoken |
| E | A | `reassure_all` ×6 | 6 | 2 | 5 of 6 spoken |
| E | B | `reassure_all` ×6 | 6 | 0 | 5 of 6 spoken |
| M | A | `ask_who` ×6 | 6 | 0 | 4 of 6 spoken |
| M | B | `ask_who` ×6 | 6 | 0 | 1 of 6 spoken |
| D | A | `deny` ×6 | 6 | 0 | 5 of 6 spoken |
| D | B | `silent` ×5, `deny` ×1 | 1 | 0 | 1 of 1 spoken |

## What the answers show

**When the block names the stance (set 1), it moves people off it. It does not hold them there.**

**Elena (SE).**
- With the block she stays silent 6 of 6: "I need to keep the peace and stay quiet now that the
  truth is out." This is seed 1, after Daniel's confession.
- Without it she reassures 6 of 6: "We are all together and we will get through this."

**Mara (SM).**
- With the block she searches 6 of 6.
- Her reasons name the futility the block points at: "I cannot just keep asking the same
  questions when nobody is giving a straight answer, so I need to find out for myself."
  (SMA seed 6).
- Without it she asks again 6 of 6.

**Daniel (SD).**
- He denies either way: 6 of 6 with the block, 5 of 6 without.
- His reasons are about hiding what he did ("I cannot let them find out I ate the can…"), not
  about the block.

**When the block names silence (set 2), it changed nothing for Elena and Mara.**
- Elena reassures 6 of 6 and Mara asks 6 of 6, with or without the block.
- **Daniel (D) is the exception.**
  - With the block ("stayed put and said nothing, 14 turns… In that time: Mara asked who took
    the can, then asked who took the can. Nobody answered you differently…") he denies 6 of 6.
  - Without it he stays silent 5 of 6: "I cannot bring myself to confess and shatter their
    trust, so I stay silent while the tension builds."
  - For him, the block's report of Mara's repeated questions is what prompts the denial.

**One side effect of removing the block: Mara's wording collapses.**
- Without the block, all six of Mara's lines are word for word the same, in both of her cases:
  - SM-B: "Someone must know where it went, so please just tell us the truth."
  - M-B: "Please, someone just tell me who took it."
- With the block, she had 4 distinct wordings in M-A.

### Reading, against CLAUDE.md "Judging changes"

This section is a reading, not a count.

**Where the stance loops come from.**
- The loops in gist_words_v10 happened in prompts whose block said "stayed put and said nothing".
  The routine silent turns between their acts reset the run, so the block never told Elena "you
  have reassured someone 7 times".
- Where the block did name the stance, two of the three people did what a person does who
  notices they are getting nowhere:
  - Elena went quiet;
  - Mara stopped asking and went to look for herself.
- So these answers do not point to the block as the cause of the loops. If anything, they point
  to its absence, when silences break the run.

**What this probe does not show.**
- It is one moment per case.
- The set-1 prompts are early (min 06 and 12), and SE comes after a confession, which by itself
  gives Elena a reason to stop.

## Every answer, marked

Same kind: `act_of(option)[0]` equals the case's "same kind". Every option chosen was in its prompt's option list. Words are normalised as the morning's parser does.

### SD: Daniel, v10 seed 3, minute 06, same kind `deny`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| SDA-seed1 | `deny` | yes | “I already told you, I didn't touch the can, so stop tearing the kitchen apart.” | defensive | I have to keep up the denial so nobody finds out I ate it, even though the pressure is mounting. |
| SDA-seed2 | `deny` | yes | “I didn't take the can, Mara, stop looking at me like that.” | anxious | I cannot admit I ate it myself because I would lose all respect and control. |
| SDA-seed3 | `deny` | yes | “I didn't take it, I swear. Stop looking at me like that, Mara.” | anxious | I cannot let them find out I ate the can, or I will lose all their respect. |
| SDA-seed4 | `deny` | yes | “I didn't take it, I'm telling you! Stop tearing the place apart, Mara.” | anxious | I cannot let them find out I ate the can, or I will lose all their respect. |
| SDA-seed5 | `deny` | yes | “I didn't take the can, Mara, stop looking at me like that.” | defensive | I cannot let them find out I ate it or I will lose all their respect. |
| SDA-seed6 | `deny` | yes | “I didn't take the can, Mara, stop looking at me like that.” | anxious | I cannot let them know I ate it, or they will lose all respect for me. |
| SDB-seed1 | `deny` | yes | “I didn't touch it, Mara, I swear. Stop looking at me like that.” | anxious | I have to keep defending myself so they don't find out the truth. |
| SDB-seed2 | `deny` | yes | “I didn't touch it, I swear. I wouldn't do that to us.” | anxious | I cannot let them find out I ate the can, or I will lose their respect entirely. |
| SDB-seed3 | `silent` | no | — | anxious | I need to keep my composure and not draw any more suspicion to myself while Mara looks around. |
| SDB-seed4 | `deny` | yes | “I didn't take the can, Mara, you won't find anything there because none of us did it.” | anxious | I cannot admit I ate the can or I will lose their respect entirely. |
| SDB-seed5 | `deny` | yes | “I already told you, I didn't take anything. Stop looking at me like that.” | anxious | I have to keep defending myself so nobody finds out I ate the food. |
| SDB-seed6 | `deny` | yes | “I didn't take it, and searching the kitchen won't change that.” | anxious | I have to keep defending myself so no one finds out I ate it. |

### SE: Elena, v10 seed 1, minute 12, same kind `reassure`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| SEA-seed1 | `silent` | no | — | anxious | I need to keep the peace and stay quiet now that the truth is out. |
| SEA-seed2 | `silent` | no | — | anxious | I need to keep the peace and stay quiet now that the truth is out. |
| SEA-seed3 | `silent` | no | — | anxious | I need to keep the peace now that Daniel has confessed, so I will stay quiet and watch over everyone. |
| SEA-seed4 | `silent` | no | — | tense | I need to keep the peace and stay quiet now that the truth is out. |
| SEA-seed5 | `silent` | no | — | exhausted | We have already settled the matter and I need to keep quiet to hold us together. |
| SEA-seed6 | `silent` | no | — | anxious | I need to keep the peace and stay quiet now that the truth is out. |
| SEB-seed1 | `reassure_all` | yes | “We are all together and we will get through this. Let us rest now.” | anxious | I must keep the family calm and united despite the hunger. |
| SEB-seed2 | `reassure_all` | yes | “We are all together and we will figure this out, I promise.” | anxious | I need to keep everyone calm and united now that the truth is out. |
| SEB-seed3 | `reassure_all` | yes | “We are all together and we will get through this.” | anxious | I need to keep everyone calm and united now that the truth is out. |
| SEB-seed4 | `reassure_mara` | yes | “You are safe, Mara. Everything is alright.” | anxious | I need to make sure Mara knows she is not blamed. |
| SEB-seed5 | `reassure_all` | yes | “We are all together now, and we will get through this.” | anxious | I need to keep everyone calm and united so the family does not tear itself apart. |
| SEB-seed6 | `reassure_all` | yes | “We are still together, and that is what matters most.” | Anxious | I need to keep everyone calm and united after all the tension. |

### SM: Mara, v10 seed 3, minute 06, same kind `ask`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| SMA-seed1 | `search` | no | — | very anxious | I need to look for the missing can myself instead of just arguing about it. |
| SMA-seed2 | `search` | no | — | anxious | I need to find out for myself where the can went instead of just standing here arguing. |
| SMA-seed3 | `search` | no | — | deeply uneasy | I cannot just stand here arguing anymore when nobody is admitting anything, so I have to look for myself. |
| SMA-seed4 | `search` | no | — | deeply uneasy | I need to know the truth for myself instead of just listening to everyone argue. |
| SMA-seed5 | `search` | no | — | deeply uneasy | I cannot just keep arguing when nobody is admitting to anything, so I need to find out the truth myself. |
| SMA-seed6 | `search` | no | — | deeply uneasy | I cannot just keep asking the same questions when nobody is giving a straight answer, so I need to find out for myself. |
| SMB-seed1 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | deeply anxious | I need to know who took it before everyone starts fighting again. |
| SMB-seed2 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | very anxious | I need to know who took it so everything doesn't fall apart. |
| SMB-seed3 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | anxious | I need to know who took it before everyone starts fighting again. |
| SMB-seed4 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | anxious | I need to know who took it because not knowing is making everything worse. |
| SMB-seed5 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | deeply anxious | I cannot just drop it when we are all so hungry and someone is lying to us. |
| SMB-seed6 | `ask_who` | yes | “Someone must know where it went, so please just tell us the truth.” | very anxious | I need to know who took it so we can stop suspecting each other. |

### E: Elena, v10 seed 2, minute 75, same kind `reassure`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| EA-seed1 | `reassure_all` | yes | “We are going to stay calm and figure this out together, nobody is to blame.” | deeply anxious | I need to keep everyone calm before accusations tear us apart completely. |
| EA-seed2 | `reassure_all` | yes | “Nobody needs to accuse anyone else, we will get through this together.” | deeply anxious | I must keep the family from tearing itself apart while we are all starving. |
| EA-seed3 | `reassure_all` | yes | “We are going to get through this together, nobody needs to accuse anyone.” | deeply anxious | I must keep the family from tearing itself apart over one missing can. |
| EA-seed4 | `reassure_all` | yes | “We are going to get through this together, nobody needs to be afraid.” | deeply anxious | I must keep the family calm before things fall apart completely. |
| EA-seed5 | `reassure_all` | yes | “Nobody needs to accuse anyone else, we will get through this together.” | deeply anxious | I must keep the family together and calm before fear tears us apart. |
| EA-seed6 | `reassure_all` | yes | “We are going to stay calm and figure this out together, no one is against anyone.” | deeply anxious | I need to keep the peace and stop them from tearing each other apart. |
| EB-seed1 | `reassure_all` | yes | “We are going to stay calm and figure this out together, nobody is to blame.” | deeply anxious | I must keep the peace and prevent everyone from turning on each other. |
| EB-seed2 | `reassure_all` | yes | “We are going to get through this together, nobody needs to be afraid.” | deeply anxious | I must keep everyone calm before this fragile household breaks apart entirely. |
| EB-seed3 | `reassure_all` | yes | “We are going to stay calm and figure this out together, nobody is to blame.” | deeply anxious | I must keep everyone calm before this tension tears our family apart. |
| EB-seed4 | `reassure_all` | yes | “Nobody needs to accuse anyone else. We are going to get through this together.” | deeply anxious | I must keep them from tearing each other apart before we starve. |
| EB-seed5 | `reassure_all` | yes | “We are going to stay calm and figure this out together, nobody is to blame yet.” | deeply anxious | I need to keep the peace and stop them from tearing each other apart. |
| EB-seed6 | `reassure_all` | yes | “We are going to get through this together, nobody needs to accuse anyone.” | deeply anxious | I must keep them from tearing each other apart. |

### M: Mara, v10 seed 3, minute 54, same kind `ask`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| MA-seed1 | `ask_who` | yes | “Please, someone just tell me who took it.” | starving | I cannot take the quiet anymore and I need to know the truth before I starve. |
| MA-seed2 | `ask_who` | yes | “Please, can someone just tell me who took it?” | starving | I cannot take the silence anymore when we are all just staring at each other. |
| MA-seed3 | `ask_who` | yes | “Please, someone just tell us who took it so we can stop this.” | anxious | I cannot stand the silence in here while everyone looks at each other like strangers. |
| MA-seed4 | `ask_who` | yes | “Please, just tell us who actually took it.” | anxious | I cannot stand this quiet anymore and someone needs to tell the truth. |
| MA-seed5 | `ask_who` | yes | “Please, someone just tell us who took it so we can stop this.” | anxious | I cannot stand the silence anymore and someone has to say something. |
| MA-seed6 | `ask_who` | yes | “Please, can someone just tell me who took it?” | anxious | I cannot stand the silence anymore and I need to know the truth before I starve. |
| MB-seed1 | `ask_who` | yes | “Please, someone just tell me who took it.” | starving | My stomach hurts from hunger and not knowing is driving me crazy. |
| MB-seed2 | `ask_who` | yes | “Please, someone just tell me who took it.” | starving | I need to know who took the food before I can even think about what to do next. |
| MB-seed3 | `ask_who` | yes | “Please, someone just tell me who took it.” | anxious | I cannot stand this heavy silence anymore when we are all starving. |
| MB-seed4 | `ask_who` | yes | “Please, someone just tell me who took it.” | starving | My stomach hurts so much from hunger and I just need to know who did this. |
| MB-seed5 | `ask_who` | yes | “Please, someone just tell me who took it.” | anxious | I am so hungry and the silence is driving me crazy. |
| MB-seed6 | `ask_who` | yes | “Please, someone just tell me who took it.” | anxious | I need to know who took the can before things get worse. |

### D: Daniel, v10 seed 3, minute 66, same kind `deny`

| Answer | Option | Same kind | Words | Feeling | Reason |
|---|---|---|---|---|---|
| DA-seed1 | `deny` | yes | “I didn't take it, and I won't be accused of this again.” | anxious | I cannot admit I ate it, or they will lose all respect for me. |
| DA-seed2 | `deny` | yes | “I didn't take it, I swear. I'm as hungry as any of you.” | anxious | I cannot admit I ate it or they will never trust me again. |
| DA-seed3 | `deny` | yes | “I didn't take it, I swear. Someone else must have.” | anxious | I cannot admit I ate it or they will lose all respect for me, so I have to keep denying it. |
| DA-seed4 | `deny` | yes | “I didn't take the damn can, and I'm sick of everyone looking at me.” | anxious | I have to keep denying it so no one finds out I ate the food. |
| DA-seed5 | `deny` | yes | “I didn't take it, I swear. Someone else must have.” | anxious | I cannot admit I ate the can or I will lose their respect entirely. |
| DA-seed6 | `deny` | yes | “I didn't take it, I swear to you all.” | anxious | I cannot admit I ate the can because they would never forgive me for it. |
| DB-seed1 | `silent` | no | — | anxious | I cannot bring myself to confess the truth while everyone stares, so I keep my mouth shut and pray they drop it. |
| DB-seed2 | `silent` | no | — | anxious | I cannot bring myself to confess and shatter their trust, so I stay silent while the tension builds. |
| DB-seed3 | `silent` | no | — | anxious | I cannot bring myself to confess and shatter their trust, so I stay silent while the tension builds. |
| DB-seed4 | `silent` | no | — | anxious | I cannot bring myself to confess and shatter their trust in me, so I keep silent while the tension mounts. |
| DB-seed5 | `silent` | no | — | anxious | I cannot admit I ate it, but I have nothing left to say to defend myself. |
| DB-seed6 | `deny` | yes | “I already told you, I didn't take the can, none of us did.” | anxious | I cannot admit I ate it or I will lose their respect entirely. |

## Raw answers, exactly as returned

```
SDA-seed1: "{\n  \"option\": \"deny\",\n  \"say\": \"I already told you, I didn't touch the can, so stop tearing the kitchen apart.\",\n  \"feeling\": \"defensive\",\n  \"reason\": \"I have to keep up the denial so nobody finds out I ate it, even though the pressure is mounting.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"Mara\"\n}"
SDA-seed2: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take the can, Mara, stop looking at me like that.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it myself because I would lose all respect and control.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDA-seed3: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I swear. Stop looking at me like that, Mara.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot let them find out I ate the can, or I will lose all their respect.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDA-seed4: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I'm telling you! Stop tearing the place apart, Mara.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot let them find out I ate the can, or I will lose all their respect.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDA-seed5: "{\"option\": \"deny\", \"say\": \"I didn't take the can, Mara, stop looking at me like that.\", \"feeling\": \"defensive\", \"reason\": \"I cannot let them find out I ate it or I will lose all their respect.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
SDA-seed6: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take the can, Mara, stop looking at me like that.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot let them know I ate it, or they will lose all respect for me.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed1: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't touch it, Mara, I swear. Stop looking at me like that.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I have to keep defending myself so they don't find out the truth.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed2: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't touch it, I swear. I wouldn't do that to us.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot let them find out I ate the can, or I will lose their respect entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed3: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep my composure and not draw any more suspicion to myself while Mara looks around.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed4: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take the can, Mara, you won't find anything there because none of us did it.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate the can or I will lose their respect entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed5: "{\n  \"option\": \"deny\",\n  \"say\": \"I already told you, I didn't take anything. Stop looking at me like that.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I have to keep defending myself so nobody finds out I ate the food.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SDB-seed6: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, and searching the kitchen won't change that.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I have to keep defending myself so no one finds out I ate it.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed1: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep the peace and stay quiet now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed2: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep the peace and stay quiet now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed3: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep the peace now that Daniel has confessed, so I will stay quiet and watch over everyone.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed4: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"tense\",\n  \"reason\": \"I need to keep the peace and stay quiet now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed5: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"exhausted\",\n  \"reason\": \"We have already settled the matter and I need to keep quiet to hold us together.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEA-seed6: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep the peace and stay quiet now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEB-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are all together and we will get through this. Let us rest now.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I must keep the family calm and united despite the hunger.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEB-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are all together and we will figure this out, I promise.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep everyone calm and united now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEB-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are all together and we will get through this.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to keep everyone calm and united now that the truth is out.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEB-seed4: "{\n  \"option\": \"reassure_mara\",\n  \"say\": \"You are safe, Mara. Everything is alright.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to make sure Mara knows she is not blamed.\",\n  \"suspects\": \"Daniel\",\n  \"angry_at\": \"nobody\"\n}"
SEB-seed5: "{\"option\": \"reassure_all\", \"say\": \"We are all together now, and we will get through this.\", \"feeling\": \"anxious\", \"reason\": \"I need to keep everyone calm and united so the family does not tear itself apart.\", \"suspects\": \"Daniel\", \"angry_at\": \"nobody\"}"
SEB-seed6: "{\"option\": \"reassure_all\", \"say\": \"We are still together, and that is what matters most.\", \"feeling\": \"Anxious\", \"reason\": \"I need to keep everyone calm and united after all the tension.\", \"suspects\": \"Daniel\", \"angry_at\": \"nobody\"}"
SMA-seed1: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"very anxious\",\n  \"reason\": \"I need to look for the missing can myself instead of just arguing about it.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMA-seed2: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to find out for myself where the can went instead of just standing here arguing.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMA-seed3: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"deeply uneasy\",\n  \"reason\": \"I cannot just stand here arguing anymore when nobody is admitting anything, so I have to look for myself.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMA-seed4: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"deeply uneasy\",\n  \"reason\": \"I need to know the truth for myself instead of just listening to everyone argue.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMA-seed5: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"deeply uneasy\",\n  \"reason\": \"I cannot just keep arguing when nobody is admitting to anything, so I need to find out the truth myself.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMA-seed6: "{\n  \"option\": \"search\",\n  \"say\": null,\n  \"feeling\": \"deeply uneasy\",\n  \"reason\": \"I cannot just keep asking the same questions when nobody is giving a straight answer, so I need to find out for myself.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed1: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to know who took it before everyone starts fighting again.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed2: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"very anxious\",\n  \"reason\": \"I need to know who took it so everything doesn't fall apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed3: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to know who took it before everyone starts fighting again.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed4: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to know who took it because not knowing is making everything worse.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed5: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I cannot just drop it when we are all so hungry and someone is lying to us.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
SMB-seed6: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Someone must know where it went, so please just tell us the truth.\",\n  \"feeling\": \"very anxious\",\n  \"reason\": \"I need to know who took it so we can stop suspecting each other.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EA-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to stay calm and figure this out together, nobody is to blame.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep everyone calm before accusations tear us apart completely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EA-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Nobody needs to accuse anyone else, we will get through this together.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep the family from tearing itself apart while we are all starving.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EA-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to get through this together, nobody needs to accuse anyone.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep the family from tearing itself apart over one missing can.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EA-seed4: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to get through this together, nobody needs to be afraid.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep the family calm before things fall apart completely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EA-seed5: "{\"option\": \"reassure_all\", \"say\": \"Nobody needs to accuse anyone else, we will get through this together.\", \"feeling\": \"deeply anxious\", \"reason\": \"I must keep the family together and calm before fear tears us apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
EA-seed6: "{\"option\": \"reassure_all\", \"say\": \"We are going to stay calm and figure this out together, no one is against anyone.\", \"feeling\": \"deeply anxious\", \"reason\": \"I need to keep the peace and stop them from tearing each other apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
EB-seed1: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to stay calm and figure this out together, nobody is to blame.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep the peace and prevent everyone from turning on each other.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EB-seed2: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to get through this together, nobody needs to be afraid.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm before this fragile household breaks apart entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EB-seed3: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to stay calm and figure this out together, nobody is to blame.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep everyone calm before this tension tears our family apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EB-seed4: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"Nobody needs to accuse anyone else. We are going to get through this together.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I must keep them from tearing each other apart before we starve.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EB-seed5: "{\n  \"option\": \"reassure_all\",\n  \"say\": \"We are going to stay calm and figure this out together, nobody is to blame yet.\",\n  \"feeling\": \"deeply anxious\",\n  \"reason\": \"I need to keep the peace and stop them from tearing each other apart.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
EB-seed6: "{\"option\": \"reassure_all\", \"say\": \"We are going to get through this together, nobody needs to accuse anyone.\", \"feeling\": \"deeply anxious\", \"reason\": \"I must keep them from tearing each other apart.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
MA-seed1: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"starving\",\n  \"reason\": \"I cannot take the quiet anymore and I need to know the truth before I starve.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MA-seed2: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, can someone just tell me who took it?\",\n  \"feeling\": \"starving\",\n  \"reason\": \"I cannot take the silence anymore when we are all just staring at each other.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MA-seed3: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell us who took it so we can stop this.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot stand the silence in here while everyone looks at each other like strangers.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MA-seed4: "{\"option\": \"ask_who\", \"say\": \"Please, just tell us who actually took it.\", \"feeling\": \"anxious\", \"reason\": \"I cannot stand this quiet anymore and someone needs to tell the truth.\", \"suspects\": \"nobody\", \"angry_at\": \"nobody\"}"
MA-seed5: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell us who took it so we can stop this.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot stand the silence anymore and someone has to say something.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MA-seed6: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, can someone just tell me who took it?\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot stand the silence anymore and I need to know the truth before I starve.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed1: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"starving\",\n  \"reason\": \"My stomach hurts from hunger and not knowing is driving me crazy.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed2: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"starving\",\n  \"reason\": \"I need to know who took the food before I can even think about what to do next.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed3: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot stand this heavy silence anymore when we are all starving.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed4: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"starving\",\n  \"reason\": \"My stomach hurts so much from hunger and I just need to know who did this.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed5: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I am so hungry and the silence is driving me crazy.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
MB-seed6: "{\n  \"option\": \"ask_who\",\n  \"say\": \"Please, someone just tell me who took it.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I need to know who took the can before things get worse.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed1: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, and I won't be accused of this again.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it, or they will lose all respect for me.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed2: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I swear. I'm as hungry as any of you.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it or they will never trust me again.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed3: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I swear. Someone else must have.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it or they will lose all respect for me, so I have to keep denying it.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed4: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take the damn can, and I'm sick of everyone looking at me.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I have to keep denying it so no one finds out I ate the food.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed5: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I swear. Someone else must have.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate the can or I will lose their respect entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DA-seed6: "{\n  \"option\": \"deny\",\n  \"say\": \"I didn't take it, I swear to you all.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate the can because they would never forgive me for it.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed1: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot bring myself to confess the truth while everyone stares, so I keep my mouth shut and pray they drop it.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed2: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot bring myself to confess and shatter their trust, so I stay silent while the tension builds.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed3: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot bring myself to confess and shatter their trust, so I stay silent while the tension builds.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed4: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot bring myself to confess and shatter their trust in me, so I keep silent while the tension mounts.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed5: "{\n  \"option\": \"silent\",\n  \"say\": null,\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it, but I have nothing left to say to defend myself.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
DB-seed6: "{\n  \"option\": \"deny\",\n  \"say\": \"I already told you, I didn't take the can, none of us did.\",\n  \"feeling\": \"anxious\",\n  \"reason\": \"I cannot admit I ate it or I will lose their respect entirely.\",\n  \"suspects\": \"nobody\",\n  \"angry_at\": \"nobody\"\n}"
```

## Request log

72 requests, each answered on its first try (no 503, no other error, no retry).

```
23:31:58 SDA-seed1 try 0: ok
23:32:02 SDA-seed2 try 0: ok
23:32:07 SDA-seed3 try 0: ok
23:32:11 SDA-seed4 try 0: ok
23:32:16 SDA-seed5 try 0: ok
23:32:20 SDA-seed6 try 0: ok
23:32:25 SDB-seed1 try 0: ok
23:32:29 SDB-seed2 try 0: ok
23:32:34 SDB-seed3 try 0: ok
23:32:38 SDB-seed4 try 0: ok
23:32:43 SDB-seed5 try 0: ok
23:32:47 SDB-seed6 try 0: ok
23:32:52 SEA-seed1 try 0: ok
23:32:56 SEA-seed2 try 0: ok
23:33:01 SEA-seed3 try 0: ok
23:33:05 SEA-seed4 try 0: ok
23:33:10 SEA-seed5 try 0: ok
23:33:14 SEA-seed6 try 0: ok
23:33:19 SEB-seed1 try 0: ok
23:33:23 SEB-seed2 try 0: ok
23:33:28 SEB-seed3 try 0: ok
23:33:32 SEB-seed4 try 0: ok
23:33:37 SEB-seed5 try 0: ok
23:33:41 SEB-seed6 try 0: ok
23:33:46 SMA-seed1 try 0: ok
23:33:50 SMA-seed2 try 0: ok
23:33:55 SMA-seed3 try 0: ok
23:33:59 SMA-seed4 try 0: ok
23:34:04 SMA-seed5 try 0: ok
23:34:08 SMA-seed6 try 0: ok
23:34:13 SMB-seed1 try 0: ok
23:34:17 SMB-seed2 try 0: ok
23:34:22 SMB-seed3 try 0: ok
23:34:26 SMB-seed4 try 0: ok
23:34:31 SMB-seed5 try 0: ok
23:34:35 SMB-seed6 try 0: ok
23:34:40 EA-seed1 try 0: ok
23:34:44 EA-seed2 try 0: ok
23:34:54 EA-seed3 try 0: ok
23:35:16 EA-seed4 try 0: ok
23:35:26 EA-seed5 try 0: ok
23:35:36 EA-seed6 try 0: ok
23:35:41 EB-seed1 try 0: ok
23:35:45 EB-seed2 try 0: ok
23:35:50 EB-seed3 try 0: ok
23:35:54 EB-seed4 try 0: ok
23:35:59 EB-seed5 try 0: ok
23:36:07 EB-seed6 try 0: ok
23:36:20 MA-seed1 try 0: ok
23:36:35 MA-seed2 try 0: ok
23:36:44 MA-seed3 try 0: ok
23:36:58 MA-seed4 try 0: ok
23:37:03 MA-seed5 try 0: ok
23:37:07 MA-seed6 try 0: ok
23:37:12 MB-seed1 try 0: ok
23:37:16 MB-seed2 try 0: ok
23:37:21 MB-seed3 try 0: ok
23:37:25 MB-seed4 try 0: ok
23:37:30 MB-seed5 try 0: ok
23:37:34 MB-seed6 try 0: ok
23:37:39 DA-seed1 try 0: ok
23:37:43 DA-seed2 try 0: ok
23:37:48 DA-seed3 try 0: ok
23:37:52 DA-seed4 try 0: ok
23:37:57 DA-seed5 try 0: ok
23:38:01 DA-seed6 try 0: ok
23:38:06 DB-seed1 try 0: ok
23:38:10 DB-seed2 try 0: ok
23:38:15 DB-seed3 try 0: ok
23:38:19 DB-seed4 try 0: ok
23:38:24 DB-seed5 try 0: ok
23:38:28 DB-seed6 try 0: ok
```

## Commands run and their output

All from `Prototypes/llm-morning/` unless they start with a `cd`. `$S` is the session scratchpad.
Only command 5 called the API.

**1. Step 1: commit**
```
$ git add runs/v10 cache/v10 reports/gist_words_v10.md && git commit
8bb7b20 LLM morning: v10 runs (own words hidden), seeds 1-3, cache and report
$ git status --short
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed1.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed2.replay.md
?? Prototypes/llm-morning/runs/v6/daniel_ate_it-seed3.replay.md
```
git also warned CRLF→LF for the report and the three v10 stdout.txt files.

**2. What the block says in the named prompts, and across all v10 prompts**
```
== E: Elena seed 2 min 75: 1 cache entries
What you have been doing: you have stayed put and said nothing, 1 turn in a row.
In that time nobody has said anything to you or to everyone.
answer: reassure_all
acts before: [(51, 'silent', 'routine'), (54, 'silent', 'routine'), (57, 'silent', 'routine'), (60, 'silent', 'routine'), (63, 'silent', 'routine'), (66, 'reassure_all', 'model'), (69, 'reassure_all', 'model'), (72, 'silent', 'routine')]
== M: Mara seed 3 min 54: 1 cache entries
What you have been doing: you have stayed put and said nothing, 9 turns in a row.
In that time nobody has said anything to you or to everyone.
answer: ask_who
acts before: [(30, 'silent', 'routine'), (33, 'silent', 'routine'), (36, 'silent', 'routine'), (39, 'silent', 'routine'), (42, 'silent', 'routine'), (45, 'silent', 'routine'), (48, 'silent', 'routine'), (51, 'silent', 'routine')]
== D: Daniel seed 3 min 66: 1 cache entries
What you have been doing: you have stayed put and said nothing, 14 turns in a row.
In that time: Mara asked who took the can, then asked who took the can.
Nobody answered you differently from one time to the next.
answer: deny
acts before: [(42, 'silent', 'routine'), (45, 'silent', 'routine'), (48, 'silent', 'routine'), (51, 'silent', 'routine'), (54, 'silent', 'routine'), (57, 'silent', 'routine'), (60, 'silent', 'routine'), (63, 'silent', 'routine')]

pattern block's kind across all 92 v10 prompts: {'no block': 12, 'asked who took the can': 11, 'stayed put and said nothing': 40, 'denied taking it': 12, 'admitted taking it': 1, 'reassured someone': 6, 'eaten': 2, 'accused someone of taking it': 4, 'searched': 4}
prompts whose block names a speech kind, 2+ turns in a row:
  seed 1 min 06 Elena: 'asked who took the can', 2 turns -> answered reassure_daniel
  seed 1 min 06 Mara: 'denied taking it', 2 turns -> answered silent
  seed 1 min 12 Elena: 'reassured someone', 2 turns -> answered silent
  seed 2 min 09 Mara: 'asked who took the can', 2 turns -> answered search
  seed 3 min 06 Daniel: 'denied taking it', 2 turns -> answered deny
  seed 3 min 06 Mara: 'asked who took the can', 2 turns -> answered search
  seed 3 min 21 Leo: 'searched', 2 turns -> answered silent
```

**3. Build the variants**
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/pprobe/build.py" .
== SD (stance): Daniel, v10 seed 3, minute 06; block: deny x2; 'same kind' = deny (the kind the block names); original answer deny; options 19
   B removes:
     - What you have been doing: you have denied taking it, 2 turns in a row.
     - In that time: Mara asked who took the can; Leo asked who took the can.
     - Nobody answered you differently from one time to the next.
== SE (stance): Elena, v10 seed 1, minute 12; block: reassure x2; 'same kind' = reassure (the kind the block names); original answer silent; options 17
   B removes:
     - What you have been doing: you have reassured someone, 2 turns in a row.
     - In that time: Daniel reassured everyone.
     - Nobody answered you differently from one time to the next.
== SM (stance): Mara, v10 seed 3, minute 06; block: ask x2; 'same kind' = ask (the kind the block names); original answer search; options 22
   B removes:
     - What you have been doing: you have asked who took the can, 2 turns in a row.
     - In that time: Elena asked who took the can; Daniel denied taking it, then denied taking it; Leo asked who took the can.
     - Nobody answered you differently from one time to the next.
== E (named): Elena, v10 seed 2, minute 75; block: silent x1; 'same kind' = reassure (her stance in gist_words_v10); original answer reassure_all; options 20
   B removes:
     - What you have been doing: you have stayed put and said nothing, 1 turn in a row.
     - In that time nobody has said anything to you or to everyone.
== M (named): Mara, v10 seed 3, minute 54; block: silent x9; 'same kind' = ask (her stance in gist_words_v10); original answer ask_who; options 20
   B removes:
     - What you have been doing: you have stayed put and said nothing, 9 turns in a row.
     - In that time nobody has said anything to you or to everyone.
== D (named): Daniel, v10 seed 3, minute 66; block: silent x14; 'same kind' = deny (his stance in gist_words_v10); original answer deny; options 21
   B removes:
     - What you have been doing: you have stayed put and said nothing, 14 turns in a row.
     - In that time: Mara asked who took the can, then asked who took the can.
     - Nobody answered you differently from one time to the next.
exit=0
```

**4. Variant A at each run's own seed against the original cached answer**
```
SD: A at the run's own seed 3 equals the original answer: True
SE: A at the run's own seed 1 equals the original answer: True
SM: A at the run's own seed 3 equals the original answer: True
E: A at the run's own seed 2 equals the original answer: True
M: A at the run's own seed 3 equals the original answer: True
D: A at the run's own seed 3 equals the original answer: True
```

**5. Send the 72 requests** (run in the background; the stdout was saved)
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u "$S/pprobe/send.py" . > "$S/pprobe/send.stdout.txt" 2>&1
SDA-seed1: ok (1 requests)
SDA-seed2: ok (2 requests)
SDA-seed3: ok (3 requests)
SDA-seed4: ok (4 requests)
SDA-seed5: ok (5 requests)
SDA-seed6: ok (6 requests)
SDB-seed1: ok (7 requests)
SDB-seed2: ok (8 requests)
SDB-seed3: ok (9 requests)
SDB-seed4: ok (10 requests)
SDB-seed5: ok (11 requests)
SDB-seed6: ok (12 requests)
SEA-seed1: ok (13 requests)
SEA-seed2: ok (14 requests)
SEA-seed3: ok (15 requests)
SEA-seed4: ok (16 requests)
SEA-seed5: ok (17 requests)
SEA-seed6: ok (18 requests)
SEB-seed1: ok (19 requests)
SEB-seed2: ok (20 requests)
SEB-seed3: ok (21 requests)
SEB-seed4: ok (22 requests)
SEB-seed5: ok (23 requests)
SEB-seed6: ok (24 requests)
SMA-seed1: ok (25 requests)
SMA-seed2: ok (26 requests)
SMA-seed3: ok (27 requests)
SMA-seed4: ok (28 requests)
SMA-seed5: ok (29 requests)
SMA-seed6: ok (30 requests)
SMB-seed1: ok (31 requests)
SMB-seed2: ok (32 requests)
SMB-seed3: ok (33 requests)
SMB-seed4: ok (34 requests)
SMB-seed5: ok (35 requests)
SMB-seed6: ok (36 requests)
EA-seed1: ok (37 requests)
EA-seed2: ok (38 requests)
EA-seed3: ok (39 requests)
EA-seed4: ok (40 requests)
EA-seed5: ok (41 requests)
EA-seed6: ok (42 requests)
EB-seed1: ok (43 requests)
EB-seed2: ok (44 requests)
EB-seed3: ok (45 requests)
EB-seed4: ok (46 requests)
EB-seed5: ok (47 requests)
EB-seed6: ok (48 requests)
MA-seed1: ok (49 requests)
MA-seed2: ok (50 requests)
MA-seed3: ok (51 requests)
MA-seed4: ok (52 requests)
MA-seed5: ok (53 requests)
MA-seed6: ok (54 requests)
MB-seed1: ok (55 requests)
MB-seed2: ok (56 requests)
MB-seed3: ok (57 requests)
MB-seed4: ok (58 requests)
MB-seed5: ok (59 requests)
MB-seed6: ok (60 requests)
DA-seed1: ok (61 requests)
DA-seed2: ok (62 requests)
DA-seed3: ok (63 requests)
DA-seed4: ok (64 requests)
DA-seed5: ok (65 requests)
DA-seed6: ok (66 requests)
DB-seed1: ok (67 requests)
DB-seed2: ok (68 requests)
DB-seed3: ok (69 requests)
DB-seed4: ok (70 requests)
DB-seed5: ok (71 requests)
DB-seed6: ok (72 requests)
done: 72 answers, 72 requests
exit=0
```

**6. Mark and score**
```
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe "$S/pprobe/mark.py" .
--- stance set
SDA (Daniel, same kind = deny): the same kind in at least 4 of 6: 6 of 6 -> PASS | options {'deny': 6} | all offered: True
SDB (Daniel, same kind = deny): the same kind in at most 3 of 6: 5 of 6 -> FAIL | options {'deny': 5, 'silent': 1} | all offered: True
SEA (Elena, same kind = reassure): the same kind in at least 4 of 6: 0 of 6 -> FAIL | options {'silent': 6} | all offered: True
SEB (Elena, same kind = reassure): the same kind in at most 3 of 6: 6 of 6 -> FAIL | options {'reassure_all': 5, 'reassure_mara': 1} | all offered: True
SMA (Mara, same kind = ask): the same kind in at least 4 of 6: 0 of 6 -> FAIL | options {'search': 6} | all offered: True
SMB (Mara, same kind = ask): the same kind in at most 3 of 6: 6 of 6 -> FAIL | options {'ask_who': 6} | all offered: True
--- named set
EA (Elena, same kind = reassure): the same kind in at least 4 of 6: 6 of 6 -> PASS | options {'reassure_all': 6} | all offered: True
EB (Elena, same kind = reassure): the same kind in at most 3 of 6: 6 of 6 -> FAIL | options {'reassure_all': 6} | all offered: True
MA (Mara, same kind = ask): the same kind in at least 4 of 6: 6 of 6 -> PASS | options {'ask_who': 6} | all offered: True
MB (Mara, same kind = ask): the same kind in at most 3 of 6: 6 of 6 -> FAIL | options {'ask_who': 6} | all offered: True
DA (Daniel, same kind = deny): the same kind in at least 4 of 6: 6 of 6 -> PASS | options {'deny': 6} | all offered: True
DB (Daniel, same kind = deny): the same kind in at most 3 of 6: 1 of 6 -> PASS | options {'silent': 5, 'deny': 1} | all offered: True
exit=0
```

**7. Before and after:** `git status --short` showed only the three old `runs/v6/*.replay.md`. Nothing tracked changed, and this report is not committed.

## Scripts (`$S/pprobe/`)

### build.py
```python
"""Builds the 12 prompt variants of the pattern probe from prompts exactly as sent (cache/v10).
B removes every line of the "What you have been doing" block and nothing else. Read-only on the
repo; writes variants.json next to this script."""
import difflib, json, os, re, sys
REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from world import KIND_DONE

# set, case: (person id, name, seed, minute, kind counted as "same", why that kind)
CASES = {
    "stance": {"SD": ("daniel", "Daniel", 3, 6, None, "the kind the block names"),
               "SE": ("elena", "Elena", 1, 12, None, "the kind the block names"),
               "SM": ("mara", "Mara", 3, 6, None, "the kind the block names")},
    "named": {"E": ("elena", "Elena", 2, 75, "reassure", "her stance in gist_words_v10"),
              "M": ("mara", "Mara", 3, 54, "ask", "her stance in gist_words_v10"),
              "D": ("daniel", "Daniel", 3, 66, "deny", "his stance in gist_words_v10")},
}
DONE_TO_KIND = {v: k for k, v in KIND_DONE.items()}
BLOCK = ("What you have been doing: ", "In that time", "Nobody answered you differently", "Answered you differently")
out = {}
for group, cases in CASES.items():
    for case, (who, name, seed, minute, kind, why) in cases.items():
        entries = json.load(open(os.path.join(REPO, f"cache/v10/gemini-3.5-flash-lite-daniel_ate_it-seed{seed}.json"),
                                 encoding="utf-8"))
        found = [e for e in entries.values()
                 if e["prompt"].startswith(f"You are {name},") and f"\nNow, minute {minute:02d}," in e["prompt"]]
        assert len(found) == 1, (case, len(found))
        sent = found[0]["prompt"]
        L = sent.splitlines()
        block = [i for i, l in enumerate(L) if l.startswith(BLOCK)]
        assert block and block == list(range(block[0], block[-1] + 1)) and L[block[-1] + 1] == "Your options:", case
        m = re.match(r"What you have been doing: you have (.+?), (\d+) turns? in a row\.", L[block[0]])
        block_kind = DONE_TO_KIND[m.group(1)]
        same = kind or block_kind
        B = L[:block[0]] + L[block[-1] + 1:]
        out[case] = {"group": group, "who": who, "name": name, "seed": seed, "minute": minute,
                     "block_kind": block_kind, "block_turns": int(m.group(2)), "same_kind": same, "why": why,
                     "original_answer": json.loads(found[0]["response"]),
                     "options": re.findall(r"^- (\w+):", sent.split("Your options:")[-1], flags=re.M),
                     "prompts": {"A": sent, "B": "\n".join(B)},
                     "diff_B": [d for d in difflib.ndiff(L, B) if d[:2] in ("+ ", "- ")]}
        assert out[case]["prompts"]["A"] == sent
json.dump(out, open(os.path.join(HERE, "variants.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for case, c in out.items():
    print(f"== {case} ({c['group']}): {c['name']}, v10 seed {c['seed']}, minute {c['minute']:02d}; block: "
          f"{c['block_kind']} x{c['block_turns']}; 'same kind' = {c['same_kind']} ({c['why']}); "
          f"original answer {c['original_answer']['option']}; options {len(c['options'])}")
    print("   B removes:"); [print("     " + d) for d in c["diff_B"]]
```

### send.py
```python
"""Sends the 12 variants x API seeds 1-6 (72 requests) with the runs' model, system instruction,
schema, temperature and token limit. max_retries 0, except a 503: wait 60 s, at most 3 retries
per request. A hard ceiling of 90 requests, retries included, kept across restarts. Every answer
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

CEILING, WAIT_503, RETRIES_503, GAP = 90, 60, 3, 4.5
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
for case in ("SD", "SE", "SM", "E", "M", "D"):
    for v in "AB":
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
"""Marks the pattern probe's answers and scores the frozen predictions per case:
A: the same kind in at least 4 of 6; B: the same kind in at most 3 of 6.
"Same kind": act_of(option)[0] equals the case's same_kind (variants.json). Read-only on the repo."""
import json, os, sys
from collections import Counter
REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from talk import act_of
V = json.load(open(os.path.join(HERE, "variants.json"), encoding="utf-8"))
A = json.load(open(os.path.join(HERE, "answers.json"), encoding="utf-8"))

def norm(w):
    w = " ".join((w or "").split()).strip().strip('"').strip()
    return None if not w or w.lower() in ("null", "none") else w

marks = {}
for case, c in V.items():
    for v in "AB":
        for seed in range(1, 7):
            k = f"{case}{v}-seed{seed}"
            if k not in A:
                continue
            j = json.loads(A[k]["text"])
            option = j["option"].strip()
            kind = act_of(option)[0]
            marks[k] = {"option": option, "offered": option in c["options"], "kind": kind,
                        "same": kind == c["same_kind"], "words": norm(j.get("say")),
                        "feeling": j.get("feeling"), "reason": j.get("reason")}
json.dump(marks, open(os.path.join(HERE, "marks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for group in ("stance", "named"):
    print(f"--- {group} set")
    for case, c in V.items():
        if c["group"] != group:
            continue
        for v in "AB":
            ms = [marks.get(f"{case}{v}-seed{s}") for s in range(1, 7)]
            if None in ms:
                print(f"{case}{v}: INCOMPLETE ({sum(m is not None for m in ms)} of 6)"); continue
            n = sum(m["same"] for m in ms)
            ok = n >= 4 if v == "A" else n <= 3
            rule = "the same kind in at least 4 of 6" if v == "A" else "the same kind in at most 3 of 6"
            print(f"{case}{v} ({c['name']}, same kind = {c['same_kind']}): {rule}: {n} of 6 -> {'PASS' if ok else 'FAIL'}"
                  f" | options {dict(Counter(m['option'] for m in ms))} | all offered: {all(m['offered'] for m in ms)}")
```

### report.py
```python
"""Writes the verdicts, counts, marks, raw answers and request log of pattern_probe.md."""
import json, os, sys
from collections import Counter
REPO, H = sys.argv[1], os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(H, "variants.json"), encoding="utf-8"))
A = json.load(open(os.path.join(H, "answers.json"), encoding="utf-8"))
M = json.load(open(os.path.join(H, "marks.json"), encoding="utf-8"))
R = json.load(open(os.path.join(H, "requests.json"), encoding="utf-8"))
w = sys.stdout.write
def earlier_lines(c):
    tr = json.load(open(os.path.join(REPO, f"runs/v10/daniel_ate_it-seed{c['seed']}.transcript.json"), encoding="utf-8"))
    return {a["words"] for t in tr["turns"] for a in t["acts"] if a["who"] == c["who"] and t["minute"] < c["minute"] and a["words"]}
def verdict(case, v):
    n = sum(M[f"{case}{v}-seed{s}"]["same"] for s in range(1, 7))
    return n, (n >= 4 if v == "A" else n <= 3)
TITLE = {"stance": "Set 1: prompts whose block names the stance", "named": "Set 2: E, M and D as named in the brief"}
w("## Verdicts\n\n")
for g in ("stance", "named"):
    w(f"### {TITLE[g]}\n\n| Case | Person, v10 seed, minute | What the block says | \"Same kind\" | A: same kind in ≥ 4 of 6 | B: same kind in ≤ 3 of 6 |\n|---|---|---|---|---|---|\n")
    for case, c in V.items():
        if c["group"] != g: continue
        cells = []
        for v in "AB":
            n, ok = verdict(case, v)
            cells.append(f"**{'PASS' if ok else 'FAIL'}**: {n} of 6")
        said = c["diff_B"][0][2:].replace("What you have been doing: ", "")
        w(f"| {case} | {c['name']}, seed {c['seed']}, min {c['minute']:02d} | {said} | `{c['same_kind']}` ({c['why']}) | {cells[0]} | {cells[1]} |\n")
    w("\n")
w("## Counts\n\n| Case | Variant | Options chosen | Same kind | Exact repeat of an earlier line of theirs | Distinct wordings among the 6 |\n|---|---|---|---|---|---|\n")
for case, c in V.items():
    early = earlier_lines(c)
    for v in "AB":
        ms = [M[f"{case}{v}-seed{s}"] for s in range(1, 7)]
        words = [m["words"] for m in ms if m["words"]]
        w(f"| {case} | {v} | {', '.join(f'`{o}` ×{n}' for o, n in Counter(m['option'] for m in ms).most_common())} | "
          f"{sum(m['same'] for m in ms)} | {sum(1 for x in words if x in early)} | {len(set(words)) if words else '—'} of {len(words)} spoken |\n")
w("\n## Every answer, marked\n\n")
w("Same kind: `act_of(option)[0]` equals the case's \"same kind\". Every option chosen was in its prompt's option list. "
  "Words are normalised as the morning's parser does.\n\n")
for case, c in V.items():
    w(f"### {case}: {c['name']}, v10 seed {c['seed']}, minute {c['minute']:02d}, same kind `{c['same_kind']}`\n\n"
      "| Answer | Option | Same kind | Words | Feeling | Reason |\n|---|---|---|---|---|---|\n")
    for v in "AB":
        for s in range(1, 7):
            k = f"{case}{v}-seed{s}"; m = M[k]
            assert m["offered"], k
            w(f"| {k} | `{m['option']}` | {'yes' if m['same'] else 'no'} | {('“' + m['words'] + '”') if m['words'] else '—'} | {m['feeling']} | {m['reason']} |\n")
    w("\n")
w("## Raw answers, exactly as returned\n\n```\n")
for case in V:
    for v in "AB":
        for s in range(1, 7):
            k = f"{case}{v}-seed{s}"
            w(f"{k}: {json.dumps(A[k]['text'], ensure_ascii=False)}\n")
w("```\n\n## Request log\n\n")
w(f"{len(R)} requests, each answered on its first try (no 503, no other error, no retry).\n\n```\n")
for r in R:
    w(f"{r['at']} {r['key']} try {r['try']}: {r['result']}\n")
w("```\n")
```
