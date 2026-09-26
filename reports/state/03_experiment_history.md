# 03 · Experiment history: timeline and verdicts

Prepared 2026-09-26 by read-only inspection of the repository at HEAD `8b183d4`.
Nothing was run except search commands, `git log` and file reads. This file is the
only file written.

Conventions:
- Paths are relative to the repo root.
- **Date** gives the in-file `Date:` line where one exists, then the git commits
  (first / last) that touch the experiment's folder.
- **Verdict** is the word the report itself uses. "none" means the report states
  no KEEP / MODIFY / REBUILD / ABANDON verdict.
- **Reason** paraphrases the report's own reasoning in one line, staying close to
  its wording. It adds no judgment.
- Section 5 has the commands and their output. Section 6 lists every file found,
  each with its timeline row or marked "not an experiment".

---

## 1. Timeline (oldest first)

| # | Name | Date | Question tested | Verdict | One-line reason given | Source |
|---|---|---|---|---|---|---|
| 1 | Slice S0, the causal spine | 2026-09-10 (git `6933dcd`…`0cc78c3`, 09-10 to 09-12) | With one shared rule set and only per-character data, does the same event produce distinct, explicable perception, memory, belief, appraisal and emotion across four characters? | **KEEP** | "The representation carries the weight the later slices need… and the trace is good enough to argue with" (readings 48/48, feelings 40/48, 0 character branches). | `Docs/slices/S0/review.md` |
| 2 | Slice S1, the silent house | 2026-09-12 (git `5d613b9`…`b45f007`, 09-12 to 09-15) | Do the S0 minds produce meaningfully different autonomous physical decisions in the same circumstances? | **MODIFY** | Personality reaches behaviour (0.62) but circumstance almost does not (same person across nights 0.04); fix that before S2. | `Docs/slices/S1/review.md` §15 |
| 3 | Slice S1.1, circumstance → motivation → behaviour | 2026-09-12 (git `160dc2d`…`b45f007`) | Can the same person behave differently because something happened to them, not because of personality (counterfactual night)? | **MODIFY** | Effect carried with four small changes (not REBUILD), but a changed want reaches behaviour only when it need not compete through a deliberation layer that is "40% coin flips and has no memory of intent". | `Docs/slices/S1.1/report.md` §I |
| 4 | Slice S1.2, deliberation | 2026-09-13 (git `a354e98`…`b45f007`) | Does changed circumstance lead to changed motivation, then changed candidate appeal, then changed intention or action? | **MODIFY** | Keep C1 and C2; deliberation arithmetic is now correct, and what still blocks a changed person is standing wants nothing satisfies, which is a motivation-layer problem. | `Docs/slices/S1.2/report.md` §8 |
| 5 | Slice S1.3, acting on a want (hunger and food) | 2026-09-15 (git `3331002`…`b45f007`) | Does acting on a want (eating) produce a traceable update to that want? | **KEEP** | The lifecycle mechanism is small, traceable end to end and changes nothing where nothing happens; "nobody eats" is caused by price, not by the lifecycle. | `Docs/slices/S1.3/report.md` §11 |
| 6 | Slice S1.4, looking after somebody | 2026-09-15 (git `50bf671`…`b45f007`) | Does what happens to the person being looked after, as the helper perceives it, change the helper's want? | **MODIFY** | The three changes are causal, local and traceable (KEEP each), but criterion 8 fails: `look_after` is 83 % standing want, and two tests regress. | `Docs/slices/S1.4/report.md` §13 |
| 7 | Slice S1.5, traits and values as dispositions | 2026-09-15 (git `e6e469c`…`360f087`) | Should traits and values raise wants at every moment (A) or only scale a response to a circumstance (B, `respond`)? | **MODIFY** | A is the wrong model (53 % of urgency with nothing behind it), but shipping B would trade "a wrong model for visibly wrong behaviour" (pacing 0.43 → 2.74). | `Docs/slices/S1.5/report.md` §10 |
| 8 | Slice S1.6, a walk given up | 2026-09-16 (git `eeb29fe`…`b777a05`) | When a person walks to an end not worth pursuing, what should that change, and where does the missing link belong? | **MODIFY**, "and then move on" | The link belongs in deliberation (M2 `means: end`, pacing 2.74 → 0.07) and in the event record (M1, a minute on scripted events); ship B + M1 + M2 as the S1 baseline. | `Docs/slices/S1.6/report.md` §11 |
| 9 | Slice S1.7, can yesterday change tomorrow? | 2026-09-16 (git `1d59e43`…`dd9065c`, 09-16 to 09-17) | Does a past event change a later decision? | **MODIFY** ("not in this slice's subject matter") | History changes meaning as a step function (11 slights nothing, 12th everything), changed the act in 2 of 27 circumstances (both seed ties), and is below noise over a morning; the fix (reading weight reaching intensity) is for a later slice. | `Docs/slices/S1.7/report.md` §8 |
| 10 | System understanding audit (and census) | 2026-09-17 (git `36a1ec5`, `dd9065c`) | Across S0–S1.7, what does the implemented system actually do, compared with what was intended? | Per-component table (§29); overall: "do not implement S1.8 as specified yet" | "We repeatedly assumed a stage carried information across a boundary, and it dropped it"; choose the baseline first, then measure the motivation-to-action transfer function. | `Docs/audit/system-understanding-audit.md` §1, §28, §29; `Docs/audit/census.md` |
| 11 | Decision sensitivity | 2026-09-19 in file (git `c243050` ships Model B; `500066c`…`95d0b50`, 2026-09-20) | How far must a want move before the act changes? | **MODIFY** | Motivation reaches deliberation almost everywhere (1.9 % no candidate) but the act barely responds (median 0.36 to be preferred); the loss is in how wants become acts, so interpretation strength "should wait". | `Docs/experiments/decision-sensitivity/report.md` §15 |
| 12 | Action representation audit | 2026-09-19 in file (git `b6882f9`, 2026-09-20) | Does the reason survive the act? | **MODIFY** | "Of 918 world events the morning's acts produced, none carries an intent"; change focus from hub-act sharing to carrying intentional meaning across the action boundary. | `Docs/experiments/action-representation/report.md` §1, §13 |
| 13 | Intent-carrying action | 2026-09-20 (git `a79a048`…`95d0b50`) | If an act's reason survives act → event → perception, does it change later interpretation, state and decisions? | **KEEP** | Meaning survives in 373 of 373 carried acts, but it changes behaviour only where a rule already reads that meaning; keep the hook, unset. | `Docs/experiments/intent-carrying/report.md` §12 |
| 14 | One episode | 2026-09-20 (git `b075664`…`95d0b50`) | Can something that happens to a person change what they do, through existing mechanisms only? | **KEEP** | The composition works: wants changed in 17 of 17 runs and acts in 7 of 17, but it fades within about an hour ("carries a moment, not a history"). | `Docs/experiments/episode/report.md` §13 |
| 15 | Accumulated interpersonal history | 2026-09-20 (git `7413758`…`95d0b50`) | Can repeated history with a person change what a later identical event means? | **KEEP** | Elena's reading flips threat → disrespect at N = 12 (10 of 10 seeds); the act does not change (10 of 10), and the next bottleneck "is not in this machinery". | `Docs/experiments/accumulated-history/report.md` §12 |
| 16 | Same act, different reason | 2026-09-20 (git `c9af832` predictions, `1ddded6`, `db2be76`) | What distinguishes the same physical act chosen for different reasons? | **MODIFY** | The action layer carried six reasons with no change; modify the reading side: the vocabulary (no word for half of what a person wants) and the readers (3 of 6 intentions have none). | `Docs/experiments/same-act-different-reason/report.md` §15 |
| 17 | Intention formation | git `8ede500` predictions + frozen `intentions.json` (2026-09-20), `b285b8c`, `dce227d` (2026-09-21) | Can an intention be derived from a want and context without a universal Want → Intention table? | **KEEP** (the hypothesis and approach only; nothing to production) | 6 of 7 wants many-valued over 3,826 held-out decisions with ten authored rules and no engine change; `look_after` → `protect` 851 of 851 is the named failure. | `Docs/experiments/intention-formation/report.md` §11 |
| 18 | Intention generalization | git `132e86e` predictions (2026-09-20), `18d1163`, `dce227d` (2026-09-21) | Do the frozen rules generalize to 2,187 undesigned profiles, or are they a table fitted to four people? | **MODIFY** (formation's KEEP revised) | It generalizes (56 signatures, 0 character encoding), but ranking is by a sum: cloning a rule moves 2,898 outcomes, a weight-preserving split moves 0. | `Docs/experiments/intention-generalization/report.md` §10 |
| 19 | Intention ranking | git `964d056` predictions, `9ccb8d4`, `568e1c0` (2026-09-22) | What must an intention selector satisfy to be a causal mechanism rather than an arbitrary ranking? | **MODIFY** | Sound below ranking (0 of 642,978 compatibility changes), unsound at ranking: one copied rule reverses 48.8 % of conclusions; a theorem says anonymous sums cannot fix it. | `Docs/experiments/intention-ranking/report.md` §14 |
| 20 | Intention representation | git `a21fc76` predictions, `2ae1070` (2026-09-22), `2fed9f8` (2026-09-23) | Can evidence identity stop the way rules are written from becoming part of the person, while keeping what is proven? | **MODIFY** | Evidence identity (B) is invariant to every restatement, but 660 conclusions (242 by policy alone) rest on an undeclared answer to whether one fact cited by two reasons counts once. | `Docs/experiments/intention-representation/report.md` §14 |
| 21 | Causal routes | git `3780435` predictions (2026-09-23), `9648a9b`, `5d0f6b8` (2026-09-23) | What must a representation hold to tell "two reasons on one fact" from "one reason written twice"? | **MODIFY** | Declared route identity (D) separates them in 2,187 of 2,187 cells and passes 18 of 18 families, but cannot compute an enabler (91 innocent "theft" cells) or a target-specific circumstance. | `Docs/experiments/causal-routes/report.md` §13 |
| 22 | Reason semantics | git `e5a5131` predictions (2026-09-23), `8ec782c` (2026-09-24) | What must a simulated reason contain to tell different causal explanations apart without silent weights, hidden gates or score arithmetic? | **MODIFY** ("Recommendation") | Five distinctions are required; C meets every check but carries "alternative" and a hold-back declaration readers did not reproduce, so no representation met all four KEEP criteria. | `Docs/experiments/reason-semantics/report.md` §13 |
| 23 | Route applicability | git `431db11` predictions + protocol (2026-09-24 02:12), `b344056`, `8cdf644` (2026-09-24) | What must a route contain to decide whether it applies at all, before its support and inhibitors are combined? | none overall; per-construct KEEP / MODIFY / REBUILD ("Nothing") / ABANDON lists | One applicability layer (C) passes 10 of 10 families (A 3, B 6); on real mornings it changes no decision of its own: all 99 changes come from the precondition-carries-no-weight choice. | `Docs/experiments/route-applicability/review.md` §1, §9 |
| 24 | LLM morning prototype, step 1 | REPORT.md mtime 2026-09-25 01:57; git `8b183d4` (2026-09-26) | Can rules keep the house while a Gemini model picks options, speaks and names a feeling at social moments only? | none | Stated as observations for "a person reading the stories": reads as four people talking, but loops, a social gate that fails both ways, and invented world. | `Prototypes/llm-morning/REPORT.md` |
| 25 | LLM morning prototype, step 2: sequential conversation | REPORT-2.md mtime 2026-09-25 02:40; git `8b183d4` | Does acting in sequence within a turn, with repetition capped, make people answer each other? | none | People answer each other (up to 86 % of lines) and repetition is capped, but talk ends almost at once (last 63–84 minutes silent). | `Prototypes/llm-morning/REPORT-2.md` |
| 26 | LLM morning prototype, step 3: inner pressure and grudges | REPORT-3.md mtime 2026-09-25 03:24; git `8b183d4` | Do hunger, suspicion, grudge and guilt, with inner moments, keep the house from freezing? | none | The longest silent stretch fell to 15–18 minutes, but Daniel confesses at minute 3 in all three runs, and in seed 2 all forgive within three minutes. | `Prototypes/llm-morning/REPORT-3.md` |
| 27 | LLM morning prototype, step 4: guilt and grudges from events | REPORT-4.md mtime 2026-09-25 13:56; git `8b183d4` | Do guilt and grudges driven by rule-seen events (not verdict phrases) change the morning? | none | The minute-3 confession is gone (1 confession in 5 runs), but what replaced it "is mostly a stalemate"; the triggering events seldom happened. | `Prototypes/llm-morning/REPORT-4.md` |
| 28 | LLM morning prototype, step 5: other scenarios, another model | REPORT-5.md mtime 2026-09-25 16:07; git `8b183d4` | Are the step-4 problems general, or specific to `daniel_ate_it` or to Flash Lite (vs `mara_ate_it`, `miscount`, Gemma 4 31B)? | none | The stalemate belongs to the scenario; quiet stretches set by the hunger clock, unused take-aside and heavy reassurance are general; repetition (Flash Lite) and passivity (Gemma) belong to the models. | `Prototypes/llm-morning/REPORT-5.md` |

---

## 2. Ideas explicitly rejected, abandoned, deferred or found failed

Only items the reports themselves label rejected, taken out, ABANDON, DEFER,
FAILED (as a proposed fix or representation), "should wait", or "not used".

| Idea | Label in source | Stated reason | Source |
|---|---|---|---|
| C3: move standing still's unearned credit onto the acts it avoids | **Rejected** ("taken out") | Removing it collapsed the cast: sitting-with rose from 30 % to 67 % of choices, Elena–Leo gap 0.39 → 0.04; the credit is "load-bearing and unearned" and stays in, pinned as a known defect. | `Docs/slices/S1.2/report.md` §2–3; `Docs/slices/S1.2/c3-rejected/` |
| S1.3 `PursuitOutcome` as the carrier for wants that read memory | **ABANDON** for that kind of want (kept for needs) | S1.4 answered the social want through sight and memory (`steady`, `until`), not through the outcome record. | `Docs/slices/S1.4/report.md` §13 |
| Traits and values as standing wants (Model A) | **ABANDON as the model** (S1.5); **ABANDON** (S1.6); **ABANDON as the shipped model** (audit) | 53 % of urgency, 37 % of wants with nothing behind them, every stand-still led by one; "proven wrong in S1.5, still shipped". Model B shipped in `c243050`. | `Docs/slices/S1.5/report.md` §10; `Docs/slices/S1.6/report.md` §11; `Docs/audit/system-understanding-audit.md` §29 |
| The gate B0 | **ABANDON** | "Lets the whole standing part back in on any trace of a circumstance." | `Docs/slices/S1.5/report.md` §10 |
| Outcome feedback (learning from a walk given up) | **Ruled out by measurement** | Foresight predicts 92.5 % of pointless walks from what the walker already knew; the rest is presence. A lapse-learning mechanism would not explain the first walk. | `Docs/slices/S1.6/report.md` §6 |
| A durable open question carrying `find_out` | **DEFER** | To "when a question can be answered"; building it now "would recreate a want that never fades". | `Docs/slices/S1.6/report.md` §6, §11 |
| Where people were last seen | **DEFER** | The residue it would remove is 75 walks in 50 mornings, "and honest". | `Docs/slices/S1.6/report.md` §11 |
| Brief's suggested S1.7 scenario (accusation, defence, later request, measure compliance) | **Not used** | No compliance action exists; the ledger record it would rest on is read by no rule; nothing in the pipeline writes a ledger entry. | `Docs/slices/S1.7/report.md` §1; `Docs/slices/S1.7/held-out-predictions.md` |
| Treating "the character remembers" as evidence | **ABANDON** | "Eleven memories that change nothing, and a twelfth that changes everything." | `Docs/slices/S1.7/report.md` §8 |
| The ledger | **REBUILD** when relationships matter | "Authored, mostly unread, and cannot support any claim." | `Docs/slices/S1.7/report.md` §8; `Docs/audit/system-understanding-audit.md` §29 |
| S1.8: propagating interpretation strength (reading margin → intensity) | **Do not implement yet** (audit); **should wait** (decision sensitivity); "UNPROVEN, and the evidence argues it would feed the same compression" | A graded input to a layer that responds as a step function is unlikely to show a difference; the loss is downstream, in the want-to-act step. | `Docs/audit/system-understanding-audit.md` §28; `Docs/experiments/decision-sensitivity/report.md` §12, §14–15 |
| Authored belief effects | **ABANDON** when inference exists | "The one use moves a belief nothing reads." | `Docs/audit/system-understanding-audit.md` §29 |
| Soothe (Comfort writing into another mind) | **ABANDON** when being comforted is appraised | "Locality exception; roughly neutral in effect." | `Docs/audit/system-understanding-audit.md` §29; `README.md` Known defects |
| Candidate generation as the bottleneck (hypothesis C) | **FAILED** | 1.9 % of want/decision pairs have no candidate act. | `Docs/experiments/decision-sensitivity/report.md` §12; `Docs/experiments/action-representation/report.md` §10 |
| Hypothesis A: the action layer is already sensitive enough | **FAILED** | Small changes of motivation (≤ 0.10) make another act certain in 2.5 % of pairs. | `Docs/experiments/decision-sensitivity/report.md` §1, §12 |
| Redesigning the want-to-act mapping now | **Should wait** | Its compression is "partly an artifact of this scenario"; redesign now "would be tuning the proposals to one house". | `Docs/experiments/action-representation/report.md` §12 |
| Shared hub actions as a problem in themselves | **FAILED** (as a problem in itself) | Walks are legitimate sharing; sharing becomes destructive only because the end is dropped. | `Docs/experiments/action-representation/report.md` §1, §10 |
| Shipping a want → meaning mapping | **Do not ship** | "Nothing here says which meaning a want expresses, and the whole effect depends on that choice." | `Docs/experiments/intent-carrying/report.md` §12 |
| Adding readers for the three unread self-meanings | **Do not add** | "That is the next question, not a patch." | `Docs/experiments/intent-carrying/report.md` §12 |
| Preserving intent alone as sufficient to change the life | **FAILED** | `take_responsibility`: 367 acts, 0 changed feelings, wants, acts or mornings. | `Docs/experiments/intent-carrying/report.md` §11 |
| Durable belief reaching later behaviour after one episode | **FAILED** | It changes only the weight of a later reading, "which is discarded". | `Docs/experiments/episode/report.md` §12 |
| A relationship score, history strength or memory-to-action rule | **Do not add** | "The next bottleneck is not in this machinery." | `Docs/experiments/accumulated-history/report.md` §12 |
| Rebuilding the action layer | Rejected in the verdict | "Rebuilding it would be rebuilding the part that worked." | `Docs/experiments/same-act-different-reason/report.md` §15 |
| Any intention system in production | "Not kept, and not proposed" | No rule promoted out of the experiment folder; vocabulary (6) and reader set (3 of 6) must be settled first. | `Docs/experiments/intention-formation/report.md` §11 |
| Ranking candidates by an additive sum | **FAILED** as a principle | A duplicate rule changes 2,898 outcomes with the person untouched. | `Docs/experiments/intention-generalization/report.md` §9–10 |
| Every aggregator in the family (as a replacement for the sum) | **FAILED** | "Each gives up restatement, splitting, weight or monotonicity" (theorem, 0 of 6 measured). | `Docs/experiments/intention-ranking/report.md` §5, §13 |
| Textual deduplication as a fix | **FAILED** | "Defeated by a 0.99 copy." | `Docs/experiments/intention-ranking/report.md` §13 |
| Reason identity (C) as the unit | **FAILED** as a replacement | "Silently defeated by partial restatement" (19,062 changes, none flagged). | `Docs/experiments/intention-representation/report.md` §1, §13 |
| Representations A, B, C for reasons (causal routes) | **FAILED** | None can hold the critical pair (identical in 2,187 of 2,187 cells). | `Docs/experiments/causal-routes/report.md` §12 |
| D as a complete causal structure | **FAILED** | Cannot compute the enabler; cannot represent the circumstance readers read in `real_protect`. | `Docs/experiments/causal-routes/report.md` §12 |
| The author's relation declarations | **FAILED** as a reading others share | Reviewers matched each other but not the author on 3 of 4 real pairs. | `Docs/experiments/causal-routes/report.md` §12 |
| The "alternative" relation (only the stronger reason operates) | **Drop** "until a case exists that readers read as one-or-other" | Read as declared by 1 of 6 readers; no reader explained an exclusion by strength. | `Docs/experiments/reason-semantics/report.md` §1, §13 |
| Separate "exclusive" and "opposed" relations | **Not needed as relations** | Circumstances carry exclusive; parts and direction carry opposed. | `Docs/experiments/reason-semantics/report.md` §1 |
| Copying another reason's gate as a substitute for a reference | **FAILED** | Wrong in 1,458 cells after one edit to the other reason. | `Docs/experiments/reason-semantics/report.md` §1, §12 |
| PV2 as implemented | **FAILED** | Listed under FAILED for every representation; not implemented (§9). | `Docs/experiments/reason-semantics/report.md` §11–12 |
| Conditions and circumstances as separate constructs | **ABANDON** | "They never behave differently" (0 of 209,952); keep the words as documentation. | `Docs/experiments/route-applicability/review.md` §9 |
| Generic presence standing in for a particular person's presence | **ABANDON** | Activates a target-bound route in 17,496 of 39,366 cells. | `Docs/experiments/route-applicability/review.md` §9 |
| Discarding rules that weigh zero or less, as "does not apply" | **ABANDON** | Conflates strength with applicability (families F and G). | `Docs/experiments/route-applicability/review.md` §9 |
| Inferring roles from the kind of fact (C-kind) | **FAILED** (counterexample) | Breaks the evidence case (26,244), generic presence (6,561) and an irrelevant-fact control (6,561). | `Docs/experiments/route-applicability/review.md` §1, §9 |
| LLM prototype, first two real attempts | **Aborted by hand** after 14 and 35 requests | Answers showed rules bugs (deny after confessing; forgetting one's own confession when the prompt was trimmed). | `Prototypes/llm-morning/REPORT.md` "Aborted attempts" |
| v3 prompt verdict phrases ("is crushing you", "weighs on you heavily", "You are furious with…") | **Removed** in step 4 | REPORT-4 states the removal but not the reason. REPORT-3 links the minute-3 confession in all three runs to the "weighs on you heavily" / "is crushing you" prompt text. | `Prototypes/llm-morning/REPORT-4.md` intro; `Prototypes/llm-morning/REPORT-3.md` "What stands out" |
| Running `leo_ate_it` in the LLM prototype | **Not used** | It is a held-out variant for S1.1, with predictions to be committed before its first run; "running it here would spend it". | `Prototypes/llm-morning/REPORT-5.md` "What changed, and why" |

---

## 3. Open questions and next steps the reports list as unresolved

| From | Open item, as listed | Source |
|---|---|---|
| S0 | Questions for the reviewer: accept that Leo and Elena feel anxiety but do not show it; whether authored `belief_effects` survive past S3; whether `neutral` stays a real reading. Carry-overs: decide the emotion intensity scale and fix salience; add a held-out event with expectations written after freezing. | `Docs/slices/S0/review.md` "Recommendation", "Questions for you" |
| S1 | Four changes before S2: a reason that outlives a decision; stop summing appeal; more than one outlet for shame and guilt; un-saturate urgency. Gate: same person across conditions should differ by > 0.2. Questions: S2 in 3D first?; comfort writing into another mind; keep `eat`?; batch size. Unproven: circumstances reaching behaviour at all, scaling past seven wants, generalising beyond this house, the ambiguity band. | `Docs/slices/S1/review.md` §14, §15, "Questions for you" |
| S1.1 | Before S2: intent persistence and summed-appeal crowding; keep feelings apart by cause; rename or split `find_out`; generalise the belief rule beyond one topic. UNPROVEN: the mechanism generalises to other kinds of circumstance. | `Docs/slices/S1.1/report.md` §H, §I |
| S1.2 | The next change belongs in motivation ("a want that has been served should be satisfied"); outside S1.2's scope. UNPROVEN: why Mara's behaviour effect shrank. Ties 40 %; nobody eats. | `Docs/slices/S1.2/report.md` §6, §7, §8 |
| S1.3 | Whether a need can ever outweigh standing values (should Leo starve rather than take food?); the lifecycle on a want that reads no need; means and end for repeated walks; whether the eater should know their own intention. | `Docs/slices/S1.3/report.md` §12 |
| S1.4 | What a want is when nothing in the circumstances calls for it (before a second social want); then S1.3's means-and-end question. The regression must be answered before building further on social wants. | `Docs/slices/S1.4/report.md` §13, §14 |
| S1.5 | Means and end under B; before it, the opening memory that never fades (minute −1 read as fully fresh). | `Docs/slices/S1.5/report.md` §10 |
| S1.6 | Shipping B + M1 + M2 changes the regression baseline; the tests pinning A must be "turned round or re-pinned deliberately, one by one" (a review decision). Next: something happens to a person during the morning and later behaviour changes. Band is absolute (96 of 373 no-want decisions went to the seed). | `Docs/slices/S1.6/report.md` §6, §11 |
| S1.7 | Next: whether making a reading's margin reach its intensity turns the step into a slope and reaches the act above noise. Beliefs that never decay (MODIFY). Not tested: other personalities, speech, a scenario with more to do, B with the S1.6 fixes. | `Docs/slices/S1.7/report.md` §6, §8 |
| Audit | Step 0: choose the baseline. Step 1: the motivation-to-action transfer function. Alongside: diagnose null intent on morning acts; trace action availability. "Speech / LLM boundary: UNKNOWN: not implemented". | `Docs/audit/system-understanding-audit.md` §28, §29 |
| Decision sensitivity | Investigate in order: (1) the want-to-act mapping; (2) the ambiguity band (decides 20–31 % of decisions by seed); (3) what happens after the argmax. UNKNOWN: the mapping with acts that do not yet exist (speech, compliance). | `Docs/experiments/decision-sensitivity/report.md` §12, §14 |
| Action representation | Candidate next: a switch letting a morning act carry an intent derived from its leading want. Decision needed (the user's): the mapping between 7 wants and 6 self-meanings; whether a witness should ever infer an intent. | `Docs/experiments/action-representation/report.md` §12 |
| Intent carrying | Next: separate the private effect from the social one (same act and meaning, with and without an audience). UNPROVEN: pairing of want to meaning. UNKNOWN: whether intent should be inferable by witnesses. | `Docs/experiments/intent-carrying/report.md` §11, §13 |
| Episode | Next: the half-life of a lived moment (second encounter at 5, 10, 20, 40, 60 minutes). Design question: "what, other than a feeling, should make a person act on something that happened to them an hour ago?" | `Docs/experiments/episode/report.md` §14 |
| Accumulated history | "What act does `restore_standing` have that `find_out` does not? Today, none." UNPROVEN: whether 12 means anything in general. UNKNOWN: history changing how a different kind of act is read. | `Docs/experiments/accumulated-history/report.md` §11, §13 |
| Same act, different reason | The vocabulary (no word for wanting to eat; half of what a person wants) and the readers (one kind, covering half the intentions). UNPROVEN: witness intention inference. | `Docs/experiments/same-act-different-reason/report.md` §13–15 |
| Intention formation | The vocabulary (six intentions) and the reader set (three of six read). UNPROVEN: generalisation past one cast and house; whether intentions are right. | `Docs/experiments/intention-formation/report.md` §10–12 |
| Intention generalization | Modify how candidates are ranked. UNPROVEN: a larger vocabulary, a second house, feelings and memories; whether 28.6 % single-candidate cells are fixable without redesigning gating. UNKNOWN: generalisation once scoring is fixed. | `Docs/experiments/intention-generalization/report.md` §9, §10 |
| Intention ranking | Untested direction: evidence identity, no discard, declared possibility, reported ties, the fixture as audit. UNPROVEN: whether plausibility belongs in a gate; whether the 35.7 % single-winner share is authoring or architecture. | `Docs/experiments/intention-ranking/report.md` §10, §13 |
| Intention representation | A declared combination rule for one fact cited by several reasons, decided "on psychological grounds"; "the next step is a decision, not code". | `Docs/experiments/intention-representation/report.md` §13, §14 |
| Causal routes | Add as declared structure: enabling conditions as conditions (plus a selection decision for a candidate with no active reason); the circumstance each route is about; relations between co-active routes. UNPROVEN: whether the `protect` and `assert_authority` routes combine or exclude; "only the stronger operates"; the sole candidate with no active reason. A human panel "is the obvious next check". | `Docs/experiments/causal-routes/report.md` §11–13 |
| Reason semantics | Six vocabulary changes before implementation. Modelling choices left open: whether a condition carries strength; how independent reasons combine; hold-back floor; viability threshold; reinforcement size; graded conditions; exclusion by strength. UNPROVEN for human readers. | `Docs/experiments/reason-semantics/report.md` §10, §12–14 |
| Route applicability | NEXT EXPERIMENT: the selection layer (P0, P1, C-split, "applicable, strength ≤ 0" as unsupported) on the three route states and the 272 live cells, with blind human readers; decide the precondition-weight choice (99 real decisions) alongside. | `Docs/experiments/route-applicability/review.md` §6, §9 |
| LLM step 2 | Ways to let talk last longer "are yours to choose" (two quiet turns; first denial counts as new; naming someone new counts). | `Prototypes/llm-morning/REPORT-2.md` "What stands out" |
| LLM step 3 | Ways to change the confession or the forgiving "are yours to choose" (guilt raised only by direct reassurance; grudge lowers reassurance; stronger grudge words). | `Prototypes/llm-morning/REPORT-3.md` "What stands out" |
| LLM step 4 | For the next step, "yours to choose": the model rarely accuses anyone on its own; an unanswered question never turns into pressure. | `Prototypes/llm-morning/REPORT-4.md` "What stands out" |
| LLM step 5 | Seen in every scenario and with both models: quiet stretches set by the hunger clock; take-aside never used; heavy reassurance; questions repeated without answer. | `Prototypes/llm-morning/REPORT-5.md` "Which problems are general" |
| Standing failures | Two tests fail since S1.4 in every recorded suite run: the pacing gate (`S1ExperimentTests.SomebodyStillPacesBetweenTwoRoomsAndThisIsHowBadly`) and the emergent-moment fading check. | `README.md` Known defects; `CONTEXT_REPORT.md` §10.3; every experiment report's suite line |

---

## 4. NOT FOUND

- **A file named `*SPEC*` or `*spec*`**, or any document titled a spec. The only filename match is the unrelated `Docs/slices/S1/traces/a-mother-made-to-feel-like-a-suspect.txt`. The nearest spec-like files are frozen predictions, protocols and experiment data (section 6), plus `Docs/understanding/target-morning.md` (acceptance criteria for judging a run).
- **A single ledger of experiments with their verdicts.** `CONTEXT_REPORT.md` §7 tables the slices and experiments with dates and summaries, but it gives a verdict only for reason semantics ("MODIFY").
- **Any KEEP / MODIFY / REBUILD / ABANDON verdict for the LLM morning prototype**, steps 1 to 5. The reports give observations and say "the judge is a person reading the stories".
- **One overall verdict word for route applicability.** `review.md` gives only per-construct KEEP / MODIFY / REBUILD / ABANDON lists.
- **The reviewer's decision on any recommendation.** S0 and S1 say "awaiting your … decision", and later reports say "stopped for review". No file records the reply. The only recorded action is commit `c243050`, "ship Model B with both S1.6 fixes as the primary baseline", which the decision-sensitivity report describes.
- **A slice or experiment folder for S1.8** (interpretation strength). `Docs/slices/` holds S0 to S1.7 only.
- **A folder or test fixture for the follow-up experiments these reports name:**
  - the selection layer (route applicability);
  - the private-versus-social effect (intent carrying);
  - the half-life of a lived moment (episode).

  No matching `Docs/experiments/` folder or `Assets/_Project/Tests/EditMode` file name was found (section 5.6).
- **Human reviewers.** Every annotation used language-model subagents. "Human reviewers were not available" (`Docs/experiments/route-applicability/review.md` §2).
- **An architecture or roadmap document.** Stated by the audit: "There is no architecture or roadmap document in the repository" (`Docs/audit/system-understanding-audit.md`, "How to read this document").
- **An in-file date** for these reports: same-act-different-reason, intention-formation, intention-generalization, intention-ranking, intention-representation, causal-routes, reason-semantics and route-applicability. Their dates above come from git.
- **Git history for `Prototypes/llm-morning/reports/` (all of it), `Docs/understanding/commit-log.md`, `CONTEXT_REPORT.md` and `reports/state/`.** All are untracked (section 5.1). Their dates are the in-file dates.

---

## 5. Search commands used, and their output

Run from the repo root in Git Bash. Output is pasted verbatim, and was captured again while this file was being written.

### 5.1 Working tree state

~~~~bash
git status --short
~~~~

~~~~text
?? CLAUDE.md
?? CONTEXT_REPORT.md
?? Docs/understanding/commit-log.md
?? Prototypes/llm-morning/reports/
?? Tools/
?? narrate.sh
?? reports/
~~~~

### 5.2 Full commit history, oldest first (dates)

~~~~bash
git log --reverse --format='%h %ad %s' --date=iso
~~~~

~~~~text
91d4341 2026-09-10 21:23:15 +0100 chore: bootstrap Unity project for Fallow slice S0
8c88cc9 2026-09-10 21:28:48 +0100 data: S0 cast, event script, and designer expectation table
9344a41 2026-09-10 21:34:41 +0100 feat: character profiles, vocabulary, and data validation
a61c8f0 2026-09-10 21:44:08 +0100 feat: belief store, ledger, emotions, and the causal trace
6e53051 2026-09-10 21:56:13 +0100 feat: rules model, loader, validator, and the interpreter
63dd953 2026-09-10 22:00:51 +0100 feat: appraisal and the full per-event pipeline
6933dcd 2026-09-10 22:08:10 +0100 feat: scenario 001 measured against the expectation table
8994215 2026-09-10 22:09:58 +0100 docs: slice S0 review and project readme
3a81ede 2026-09-10 22:11:38 +0100 docs: check S0 against the plan worked example for p01
5d613b9 2026-09-12 17:57:27 +0100 feat: the deciding layer, and the S1 held-out predictions
f0b0253 2026-09-12 18:53:07 +0100 feat: slice S1, the silent house
160dc2d 2026-09-12 20:35:17 +0100 test: S1.1 counterfactual harness, diagnosis, and a held-out condition
06d92eb 2026-09-12 21:16:54 +0100 fix: S1.1 circumstance pathway, three measured changes
b310c67 2026-09-12 21:18:09 +0100 docs: S1.1 held-out predictions for leo_ate_it, before it has been run
0cc78c3 2026-09-12 22:11:47 +0100 feat: slice S1.1, circumstance to motivation to behaviour
a354e98 2026-09-13 00:21:36 +0100 test: S1.2 deliberation audit and diagnosis, behaviour unchanged
15c3175 2026-09-13 01:41:33 +0100 feat: slice S1.2, deliberation
3331002 2026-09-15 00:52:14 +0100 test: S1.3 diagnosis of wanting food, behaviour unchanged
cfcee77 2026-09-15 01:55:11 +0100 feat: slice S1.3, what acting on a want does to it (hunger and food)
50bf671 2026-09-15 02:44:13 +0100 test: S1.4 diagnosis of wanting to look after somebody, behaviour unchanged
56c6c7e 2026-09-15 02:45:49 +0100 docs: S1.4 hypothesis and held-out predictions, before any S1.4 code
b45f007 2026-09-15 04:10:18 +0100 feat: slice S1.4, what looking after somebody does to wanting to
e6e469c 2026-09-15 04:24:43 +0100 test: S1.5 diagnosis of where wants come from, behaviour unchanged
c8f788e 2026-09-15 04:25:26 +0100 docs: S1.5 hypothesis, the alternative and held-out predictions, before any code for it
360f087 2026-09-15 14:47:55 +0100 feat: slice S1.5, traits and values as dispositions (diagnostic)
eeb29fe 2026-09-16 02:16:00 +0100 test: S1.6 diagnosis of walking to ends already found not worth it, behaviour unchanged
c57687a 2026-09-16 02:17:53 +0100 docs: S1.6 hypothesis, the two mechanisms and held-out predictions, before any code for them
556b023 2026-09-16 03:24:08 +0100 feat: slice S1.6, weighing a walk by its end and timing the lived day
1d59e43 2026-09-16 03:34:16 +0100 docs: S1.7 hypothesis, design and held-out predictions, before any code for it
b777a05 2026-09-16 03:38:03 +0100 docs: S1.6 full-suite tally and regression check confirmed
a08dd62 2026-09-17 00:49:51 +0100 feat: slice S1.7, whether a past event changes a later decision
36a1ec5 2026-09-17 00:50:01 +0100 docs: system understanding audit of the implemented simulation
dd9065c 2026-09-17 16:47:03 +0100 docs: full-suite result for S1.7 and the audit; no clear choice changed
c243050 2026-09-20 04:01:18 +0100 feat: ship Model B with both S1.6 fixes as the primary baseline
500066c 2026-09-20 04:01:33 +0100 feat: decision sensitivity, how far a want must move before the act does
b6882f9 2026-09-20 04:01:47 +0100 docs: action representation audit, the reason does not survive the act
a79a048 2026-09-20 04:02:01 +0100 feat: carry what a person meant onto the event their act becomes
b075664 2026-09-20 04:02:20 +0100 feat: one lived episode, and how long it carries
7413758 2026-09-20 04:02:21 +0100 feat: accumulated history changes what a later event means
95d0b50 2026-09-20 05:09:29 +0100 docs: full-suite result for the five experiments, and one correction
c9af832 2026-09-20 17:59:49 +0100 docs: predictions for the same-act-different-reason experiment
1ddded6 2026-09-20 18:26:56 +0100 feat: one act, six reasons, and who is left to read the difference
db2be76 2026-09-20 19:41:05 +0100 docs: full-suite result for the same-act experiment
8ede500 2026-09-20 20:45:27 +0100 docs: predictions and blind-authored candidate rules for intention formation
b285b8c 2026-09-20 20:56:30 +0100 feat: a want constrains an intention without deciding it
132e86e 2026-09-20 21:49:56 +0100 docs: predictions and held-out people for the generalization experiment
18d1163 2026-09-20 22:00:57 +0100 feat: the ten rules are a reusable function of a person, ranked by an arbitrary sum
dce227d 2026-09-21 00:01:46 +0100 docs: full-suite result for the two intention experiments
964d056 2026-09-22 21:07:23 +0100 docs: predictions for the intention ranking experiment
9ccb8d4 2026-09-22 21:29:26 +0100 feat: what an intention selector must satisfy, and where ranking breaks it
a21fc76 2026-09-22 21:46:42 +0100 docs: predictions for the intention representation experiment
568e1c0 2026-09-22 23:03:00 +0100 docs: full-suite result for the intention ranking experiment
2ae1070 2026-09-22 23:36:22 +0100 feat: evidence identity stops restatement, and leaves one decision open
3780435 2026-09-23 00:30:00 +0100 docs: predictions, route declarations and annotation for the causal-route experiment
2fed9f8 2026-09-23 01:22:36 +0100 docs: full-suite result for the intention representation experiment
9648a9b 2026-09-23 02:08:58 +0100 feat: declared causal routes tell two reasons from one reason twice, and fall short twice
5d0f6b8 2026-09-23 06:13:17 +0100 docs: full-suite result for the causal-route experiment
e5a5131 2026-09-23 22:02:19 +0100 docs: predictions, cases and annotation for the reason-semantics experiment
8ec782c 2026-09-24 01:42:32 +0100 feat: what a simulated reason has to contain, before any formula
431db11 2026-09-24 02:12:09 +0100 docs: predictions, protocol and cases for the route-applicability experiment
b344056 2026-09-24 02:55:57 +0100 feat: route applicability is one layer, one construct, and needs a target
8cdf644 2026-09-24 06:02:38 +0100 docs: full-suite result for the route-applicability experiment
8b183d4 2026-09-26 00:31:43 +0100 LLM morning prototype, steps 1 to 5
~~~~

### 5.3 First and last commit touching each experiment folder

~~~~bash
for d in Docs/slices/S0 Docs/slices/S1 Docs/slices/S1.1 Docs/slices/S1.2 Docs/slices/S1.3 Docs/slices/S1.4 Docs/slices/S1.5 Docs/slices/S1.6 Docs/slices/S1.7 Docs/audit Docs/experiments/decision-sensitivity Docs/experiments/action-representation Docs/experiments/intent-carrying Docs/experiments/episode Docs/experiments/accumulated-history Docs/experiments/same-act-different-reason Docs/experiments/intention-formation Docs/experiments/intention-generalization Docs/experiments/intention-ranking Docs/experiments/intention-representation Docs/experiments/causal-routes Docs/experiments/reason-semantics Docs/experiments/route-applicability Prototypes/llm-morning Docs/understanding; do echo "$d | first: $(git log --reverse --format="%h %ad" --date=short -- $d | head -1) | last: $(git log -1 --format="%h %ad" --date=short -- $d)"; done
~~~~

~~~~text
Docs/slices/S0 | first: 6933dcd 2026-09-10 | last: 0cc78c3 2026-09-12
Docs/slices/S1 | first: 5d613b9 2026-09-12 | last: b45f007 2026-09-15
Docs/slices/S1.1 | first: 160dc2d 2026-09-12 | last: b45f007 2026-09-15
Docs/slices/S1.2 | first: a354e98 2026-09-13 | last: b45f007 2026-09-15
Docs/slices/S1.3 | first: 3331002 2026-09-15 | last: b45f007 2026-09-15
Docs/slices/S1.4 | first: 50bf671 2026-09-15 | last: b45f007 2026-09-15
Docs/slices/S1.5 | first: e6e469c 2026-09-15 | last: 360f087 2026-09-15
Docs/slices/S1.6 | first: eeb29fe 2026-09-16 | last: b777a05 2026-09-16
Docs/slices/S1.7 | first: 1d59e43 2026-09-16 | last: dd9065c 2026-09-17
Docs/audit | first: 36a1ec5 2026-09-17 | last: dd9065c 2026-09-17
Docs/experiments/decision-sensitivity | first: 500066c 2026-09-20 | last: 95d0b50 2026-09-20
Docs/experiments/action-representation | first: b6882f9 2026-09-20 | last: b6882f9 2026-09-20
Docs/experiments/intent-carrying | first: a79a048 2026-09-20 | last: 95d0b50 2026-09-20
Docs/experiments/episode | first: b075664 2026-09-20 | last: 95d0b50 2026-09-20
Docs/experiments/accumulated-history | first: 7413758 2026-09-20 | last: 95d0b50 2026-09-20
Docs/experiments/same-act-different-reason | first: c9af832 2026-09-20 | last: db2be76 2026-09-20
Docs/experiments/intention-formation | first: 8ede500 2026-09-20 | last: dce227d 2026-09-21
Docs/experiments/intention-generalization | first: 132e86e 2026-09-20 | last: dce227d 2026-09-21
Docs/experiments/intention-ranking | first: 964d056 2026-09-22 | last: 568e1c0 2026-09-22
Docs/experiments/intention-representation | first: a21fc76 2026-09-22 | last: 2fed9f8 2026-09-23
Docs/experiments/causal-routes | first: 3780435 2026-09-23 | last: 5d0f6b8 2026-09-23
Docs/experiments/reason-semantics | first: e5a5131 2026-09-23 | last: 8ec782c 2026-09-24
Docs/experiments/route-applicability | first: 431db11 2026-09-24 | last: 8cdf644 2026-09-24
Prototypes/llm-morning | first: 8b183d4 2026-09-26 | last: 8b183d4 2026-09-26
Docs/understanding | first: 8b183d4 2026-09-26 | last: 8b183d4 2026-09-26
~~~~

### 5.4 Files whose name contains REPORT or SPEC (any case)

~~~~bash
find . -path ./Library -prune -o -path '*/.venv' -prune -o -path ./.git -prune -o \( -iname '*report*' -o -iname '*spec*' \) -print | sort
~~~~

~~~~text
./Assets/_Project/Scripts/Core/Sim/S0Report.cs
./Assets/_Project/Scripts/Core/Sim/S0Report.cs.meta
./Assets/_Project/Scripts/Core/Sim/S1Report.cs
./Assets/_Project/Scripts/Core/Sim/S1Report.cs.meta
./CONTEXT_REPORT.md
./Docs/experiments/accumulated-history/report.md
./Docs/experiments/action-representation/report.md
./Docs/experiments/causal-routes/report.md
./Docs/experiments/decision-sensitivity/report.md
./Docs/experiments/episode/report.md
./Docs/experiments/intent-carrying/report.md
./Docs/experiments/intention-formation/report.md
./Docs/experiments/intention-generalization/report.md
./Docs/experiments/intention-ranking/report.md
./Docs/experiments/intention-representation/report.md
./Docs/experiments/reason-semantics/report.md
./Docs/experiments/same-act-different-reason/report.md
./Docs/slices/S1.1/report.md
./Docs/slices/S1.2/report.md
./Docs/slices/S1.3/report.md
./Docs/slices/S1.4/report.md
./Docs/slices/S1.5/report.md
./Docs/slices/S1.6/report.md
./Docs/slices/S1.7/report.md
./Docs/slices/S1/traces/a-mother-made-to-feel-like-a-suspect.txt
./Prototypes/llm-morning/REPORT-2.md
./Prototypes/llm-morning/REPORT-3.md
./Prototypes/llm-morning/REPORT-4.md
./Prototypes/llm-morning/REPORT-5.md
./Prototypes/llm-morning/REPORT.md
./Prototypes/llm-morning/reports
./reports
~~~~

### 5.5 Files containing a verdict word (KEEP, ABANDON, REBUILD, MODIFY)

~~~~bash
grep -rlE '\b(KEEP|ABANDON|REBUILD|MODIFY)\b' --include='*.md' --include='*.txt' --include='*.cs' --include='*.py' --include='*.json' . --exclude-dir=Library --exclude-dir=.venv --exclude-dir=.git --exclude-dir=Logs | sort
~~~~

~~~~text
./Assets/_Project/Tests/EditMode/ReasonSemanticsExperimentTests.cs
./CONTEXT_REPORT.md
./Docs/audit/system-understanding-audit.md
./Docs/experiments/accumulated-history/accumulated-history-all.md
./Docs/experiments/accumulated-history/report.md
./Docs/experiments/action-representation/action-representation-all.md
./Docs/experiments/action-representation/report.md
./Docs/experiments/causal-routes/causal-routes-all.md
./Docs/experiments/causal-routes/classification.json
./Docs/experiments/causal-routes/predictions.md
./Docs/experiments/causal-routes/report.md
./Docs/experiments/causal-routes/results.md
./Docs/experiments/decision-sensitivity/decision-sensitivity-all.md
./Docs/experiments/decision-sensitivity/report.md
./Docs/experiments/episode/episode-all.md
./Docs/experiments/episode/report.md
./Docs/experiments/intent-carrying/intent-carrying-all.md
./Docs/experiments/intent-carrying/report.md
./Docs/experiments/intention-formation/intention-formation-all.md
./Docs/experiments/intention-formation/report.md
./Docs/experiments/intention-generalization/intention-generalization-all.md
./Docs/experiments/intention-generalization/report.md
./Docs/experiments/intention-ranking/classification.json
./Docs/experiments/intention-ranking/intention-ranking-all.md
./Docs/experiments/intention-ranking/predictions.md
./Docs/experiments/intention-ranking/report.md
./Docs/experiments/intention-ranking/results.md
./Docs/experiments/intention-representation/classification.json
./Docs/experiments/intention-representation/intention-representation-all.md
./Docs/experiments/intention-representation/predictions.md
./Docs/experiments/intention-representation/report.md
./Docs/experiments/intention-representation/results.md
./Docs/experiments/reason-semantics/classification.json
./Docs/experiments/reason-semantics/measurements.md
./Docs/experiments/reason-semantics/predictions.md
./Docs/experiments/reason-semantics/reason-semantics-all.md
./Docs/experiments/reason-semantics/report.md
./Docs/experiments/reason-semantics/results.md
./Docs/experiments/route-applicability/predictions.md
./Docs/experiments/route-applicability/review.md
./Docs/experiments/route-applicability/route-applicability-all.md
./Docs/experiments/same-act-different-reason/report.md
./Docs/experiments/same-act-different-reason/same-act-different-reason-all.md
./Docs/slices/S0/review.md
./Docs/slices/S1.1/report.md
./Docs/slices/S1.2/report.md
./Docs/slices/S1.3/report.md
./Docs/slices/S1.4/report.md
./Docs/slices/S1.5/S1.5-all.md
./Docs/slices/S1.5/report.md
./Docs/slices/S1.6/S1.6-all.md
./Docs/slices/S1.6/report.md
./Docs/slices/S1.7/S1.7-all.md
./Docs/slices/S1.7/report.md
./Docs/slices/S1/review.md
./reports/state/03_experiment_history.md
~~~~

### 5.6 Files containing "verdict" (any case)

~~~~bash
grep -rliE 'verdict' --include='*.md' . --exclude-dir=Library --exclude-dir=.venv --exclude-dir=.git --exclude-dir=Logs | sort
~~~~

~~~~text
./Docs/audit/system-understanding-audit.md
./Docs/experiments/action-representation/action-representation-all.md
./Docs/experiments/action-representation/report.md
./Docs/experiments/causal-routes/causal-routes-all.md
./Docs/experiments/causal-routes/predictions.md
./Docs/experiments/causal-routes/report.md
./Docs/experiments/causal-routes/results.md
./Docs/experiments/decision-sensitivity/decision-sensitivity-all.md
./Docs/experiments/decision-sensitivity/report.md
./Docs/experiments/intention-formation/intention-formation-all.md
./Docs/experiments/intention-formation/report.md
./Docs/experiments/intention-generalization/intention-generalization-all.md
./Docs/experiments/intention-generalization/report.md
./Docs/experiments/intention-generalization/results.md
./Docs/experiments/intention-ranking/intention-ranking-all.md
./Docs/experiments/intention-ranking/predictions.md
./Docs/experiments/intention-ranking/report.md
./Docs/experiments/intention-ranking/results.md
./Docs/experiments/intention-representation/intention-representation-all.md
./Docs/experiments/intention-representation/predictions.md
./Docs/experiments/intention-representation/report.md
./Docs/experiments/intention-representation/results.md
./Docs/experiments/reason-semantics/measurements.md
./Docs/experiments/reason-semantics/predictions.md
./Docs/experiments/reason-semantics/reason-semantics-all.md
./Docs/experiments/reason-semantics/report.md
./Docs/experiments/reason-semantics/results.md
./Docs/experiments/same-act-different-reason/report.md
./Docs/experiments/same-act-different-reason/same-act-different-reason-all.md
./Prototypes/llm-morning/REPORT-4.md
./Prototypes/llm-morning/REPORT-5.md
./Prototypes/llm-morning/reports/state/05_results_quality.md
./reports/state/03_experiment_history.md
~~~~

### 5.7 Markdown files containing "experiment" (any case), excluding generated LLM run output

~~~~bash
grep -rliE 'experiment' --include='*.md' . --exclude-dir=Library --exclude-dir=.venv --exclude-dir=.git --exclude-dir=Logs | grep -v 'Prototypes/llm-morning/runs/' | sort
~~~~

~~~~text
./CONTEXT_REPORT.md
./Docs/audit/system-understanding-audit.md
./Docs/experiments/accumulated-history/accumulated-history-all.md
./Docs/experiments/accumulated-history/measurements.md
./Docs/experiments/accumulated-history/predictions.md
./Docs/experiments/accumulated-history/report.md
./Docs/experiments/accumulated-history/results.md
./Docs/experiments/action-representation/action-representation-all.md
./Docs/experiments/action-representation/report.md
./Docs/experiments/causal-routes/annotation/protocol.md
./Docs/experiments/causal-routes/causal-routes-all.md
./Docs/experiments/causal-routes/measurements.md
./Docs/experiments/causal-routes/predictions.md
./Docs/experiments/causal-routes/report.md
./Docs/experiments/causal-routes/results.md
./Docs/experiments/decision-sensitivity/baseline.md
./Docs/experiments/decision-sensitivity/decision-sensitivity-all.md
./Docs/experiments/decision-sensitivity/report.md
./Docs/experiments/decision-sensitivity/results.md
./Docs/experiments/episode/episode-all.md
./Docs/experiments/episode/measurements.md
./Docs/experiments/episode/predictions.md
./Docs/experiments/episode/report.md
./Docs/experiments/episode/results.md
./Docs/experiments/intent-carrying/intent-carrying-all.md
./Docs/experiments/intent-carrying/predictions.md
./Docs/experiments/intent-carrying/report.md
./Docs/experiments/intent-carrying/results.md
./Docs/experiments/intention-formation/intention-formation-all.md
./Docs/experiments/intention-formation/measurements.md
./Docs/experiments/intention-formation/predictions.md
./Docs/experiments/intention-formation/report.md
./Docs/experiments/intention-formation/results.md
./Docs/experiments/intention-generalization/intention-generalization-all.md
./Docs/experiments/intention-generalization/measurements.md
./Docs/experiments/intention-generalization/predictions.md
./Docs/experiments/intention-generalization/report.md
./Docs/experiments/intention-generalization/results.md
./Docs/experiments/intention-ranking/intention-ranking-all.md
./Docs/experiments/intention-ranking/measurements.md
./Docs/experiments/intention-ranking/predictions.md
./Docs/experiments/intention-ranking/report.md
./Docs/experiments/intention-ranking/results.md
./Docs/experiments/intention-representation/intention-representation-all.md
./Docs/experiments/intention-representation/measurements.md
./Docs/experiments/intention-representation/predictions.md
./Docs/experiments/intention-representation/report.md
./Docs/experiments/intention-representation/results.md
./Docs/experiments/reason-semantics/annotation/protocol.md
./Docs/experiments/reason-semantics/measurements.md
./Docs/experiments/reason-semantics/predictions.md
./Docs/experiments/reason-semantics/reason-semantics-all.md
./Docs/experiments/reason-semantics/report.md
./Docs/experiments/reason-semantics/results.md
./Docs/experiments/route-applicability/measurements.md
./Docs/experiments/route-applicability/predictions.md
./Docs/experiments/route-applicability/protocol.md
./Docs/experiments/route-applicability/results.md
./Docs/experiments/route-applicability/review.md
./Docs/experiments/route-applicability/route-applicability-all.md
./Docs/experiments/same-act-different-reason/measurements.md
./Docs/experiments/same-act-different-reason/predictions.md
./Docs/experiments/same-act-different-reason/report.md
./Docs/experiments/same-act-different-reason/results.md
./Docs/experiments/same-act-different-reason/same-act-different-reason-all.md
./Docs/slices/S1.1/diagnosis.md
./Docs/slices/S1.1/experiment-results.md
./Docs/slices/S1.1/report.md
./Docs/slices/S1.2/experiment-results.md
./Docs/slices/S1.2/report.md
./Docs/slices/S1.3/experiment-results.md
./Docs/slices/S1.3/report.md
./Docs/slices/S1.4/attribution.md
./Docs/slices/S1.4/experiment-results.md
./Docs/slices/S1.4/report.md
./Docs/slices/S1.5/S1.5-all.md
./Docs/slices/S1.5/experiment-results.md
./Docs/slices/S1.5/report.md
./Docs/slices/S1.5/walks.md
./Docs/slices/S1.6/S1.6-all.md
./Docs/slices/S1.6/diagnosis.md
./Docs/slices/S1.6/experiment-results.md
./Docs/slices/S1.6/held-out-predictions.md
./Docs/slices/S1.6/report.md
./Docs/slices/S1.7/S1.7-all.md
./Docs/slices/S1.7/experiment-results.md
./Docs/slices/S1.7/held-out-predictions.md
./Docs/slices/S1.7/report.md
./Docs/slices/S1/review.md
./Docs/understanding/commit-log.md
./Docs/understanding/morning-walkthrough.md
./Docs/understanding/narrator-setup.md
./Docs/understanding/understanding-all.md
./README.md
./reports/state/01_repo_map.md
./reports/state/02_csharp_core.md
./reports/state/03_experiment_history.md
~~~~

### 5.8 Verdict and recommendation lines, per report

~~~~bash
for f in Docs/slices/S0/review.md Docs/slices/S1/review.md Docs/slices/S1.*/report.md Docs/audit/system-understanding-audit.md Docs/experiments/*/report.md Docs/experiments/route-applicability/review.md Prototypes/llm-morning/REPORT*.md; do echo "=== $f ($(wc -l <$f) lines)"; grep -nE "\b(KEEP|ABANDON|REBUILD|MODIFY)\b|[Vv]erdict|[Rr]ecommend" "$f" | head -30 | cut -c1-220; done
~~~~

~~~~text
=== Docs/slices/S0/review.md (249 lines)
4:Status: complete, awaiting your KEEP / MODIFY / REBUILD decision.
227:## Recommendation
229:**KEEP.** The representation carries the weight the later slices need to put on
237:   recommendation is show less, which makes it an expression matter and leaves
=== Docs/slices/S1/review.md (518 lines)
4:Status: complete, awaiting your KEEP / MODIFY / REBUILD / ABANDON decision.
459:## 15. Recommendation
461:**MODIFY.**
502:1. **Do you accept MODIFY with those four changes, or would you rather see S2 in
=== Docs/slices/S1.1/report.md (304 lines)
262:## I. Recommendation
264:**MODIFY.**
267:not a REBUILD. Its core claim now has direct counterfactual evidence. But the evidence
=== Docs/slices/S1.2/report.md (245 lines)
213:## 8. Recommendation
215:**MODIFY.** Keep C1 and C2. Do not try to fix the rest of this in deliberation.
=== Docs/slices/S1.3/report.md (330 lines)
305:## 11. Recommendation
307:**KEEP.**
=== Docs/slices/S1.4/report.md (437 lines)
398:## 13. Recommendation
400:**MODIFY.**
405:abstraction. Not REBUILD, not ABANDON.
417:| `steady` sight, `reassurance` reading, `until` on memory terms | KEEP |
418:| Presence check on sitting with somebody | KEEP |
419:| S1.3 `PursuitOutcome` as the carrier for wants that read memory | ABANDON for this kind of want (keep it for needs) |
420:| The slice's effect on the house | MODIFY: the regression must be answered before building further on social wants |
422:## 14. Recommended next experiment
=== Docs/slices/S1.5/report.md (365 lines)
340:## 10. Recommendation
342:**MODIFY.**
346:| The source instrument (`MotivationSources`, the audit hook) | **KEEP** |
347:| Traits and values as standing wants (A) | **ABANDON as the model.** It stays the shipped default only because nothing that replaces it works yet. |
348:| Traits and values as dispositions (B, `respond`) | **MODIFY.** Keep it as the direction and the switch; do not ship it until the pacing it exposes has a cause-based answer. |
349:| The gate (B0) | **ABANDON**. The bench shows it lets the whole standing part back in on any trace of a circumstance. |
351:Not REBUILD: the switch is a few lines, and B fitted the existing pipeline without a new
352:abstraction. Not KEEP: shipping B now would trade a wrong model for visibly wrong behaviour.
354:**Recommended next experiment, after review:**
=== Docs/slices/S1.6/report.md (373 lines)
342:## 11. Recommendation
344:**MODIFY**, and then move on.
348:| The foresight instrument and the walk records (`S16Measures`) | **KEEP** |
349:| M2, a walk credited only when its end could be worth doing (`means: end`) | **KEEP**, and ship: it completes S1.2's intention design, adds no number, and is traceable at every decision. |
350:| M1, scripted events of the lived day carry a minute | **KEEP**, and ship as data: `"minute": 0` on `p01`–`p03` and the opening. |
351:| Traits and values as standing wants (A) | **ABANDON**, as S1.5 said. Nothing that hid the loop is worth keeping. |
=== Docs/slices/S1.7/report.md (271 lines)
230:## 8. Recommendation
232:**MODIFY**, and the modification is not in this slice's subject matter.
236:| The S1.7 instrument (`S17Measures`, the arms, the response curve) | **KEEP.** It measures where causal influence dies, which is the question worth asking of every later slice. |
237:| The belief loop as the longitudinal carrier | **KEEP.** It works, it is general, it is traceable, and it cost nothing. |
238:| Treating "the character remembers" as evidence of anything | **ABANDON.** This slice measured the gap directly: eleven memories that change nothing, and a twelfth that changes everything. |
239:| The categorical channel as the *only* route for history about people | **MODIFY**, next slice. See below. |
240:| Beliefs that never decay | **MODIFY**, and recognise it as the same defect as S1.6's never-fading memory. |
241:| The ledger | **REBUILD** when relationships matter. It is authored, mostly unread, and cannot support any claim. |
=== Docs/audit/system-understanding-audit.md (1848 lines)
40:recommended: `decisions.json` sets neither `dispositions` nor `means`, so the shipped model is
98:**Recommendation** (section 28): do not implement S1.8 as specified yet. First, make the baseline
960:**Verdict: a hybrid, and specifically *continuous weighing feeding a categorical selector whose
1234:**Verdict: in the shipped simulation personality acts as both DISPOSITION** (interpretation,
1291:| Stage | Recorded | Causal source recorded | Relevant input recorded | Why reconstructible | Verdict |
1407:| **Shipped configuration is not the recommended one** | **this audit** | S1.5-S1.7 findings describe the current system | S1.7 ran on A with M1/M2 off; recommendations accumulated unshipped | new |
1432:4. **Recommendations were measured and not adopted**, so the thing we reason about (B with the fixes)
1750:## 28. Recommended Next Experiment
1764:**Step 0: a decision, not an experiment.** Choose the baseline. S1.5 and S1.6 recommended B with M1
1815:## 29. KEEP / MODIFY / REBUILD / ABANDON Assessment
1819:| Access and perception gate | **KEEP** | the best-evidenced property of the system |
1820:| World event as structured record | **KEEP** | clean; ready for speech acts; drop or use `directness` |
1821:| Interpretation as competing weighted rules | **MODIFY** | sound mechanism; the discarded weight and per-label summation need a deliberate decision |
1822:| Appraisal | **MODIFY** | personal and traceable, but a meaning-keyed table; no goal/agency/coping dimension; concern unused |
1823:| Emotion store and clock decay | **KEEP**, with the cause-merging and self-reading defects recorded | |
1824:| Memory (Experience) | **MODIFY** | stores meaning, not event; only 4 terms read it; untimed scripted events |
1825:| Recall (same-day, freshness, `until`) | **KEEP** mechanism, **MODIFY** data (minutes) | |
1826:| Beliefs and nudge rules | **KEEP** | the only working longitudinal carrier; decay and access questions open |
1827:| Authored belief effects | **ABANDON** when inference exists | the one use moves a belief nothing reads |
1828:| Ledger | **REBUILD** when relationships are the subject | authored, mostly unread, never produced |
1829:| Motivation, Model A (standing) | **ABANDON** as the shipped model | proven wrong in S1.5, still shipped |
1830:| Motivation, Model B (respond) | **KEEP** as the direction; decide whether to ship | |
1831:| Urgency knee | **KEEP** | |
1832:| Action catalog (seven acts) | **MODIFY** | too few outlets; investigation cannot succeed; availability untraced |
1833:| Proposals with fixed fit | **MODIFY** | means are never checked against what the want reads |
1834:| Summed appeal | **MODIFY** | breadth beats urgency; S1.2 showed it cannot simply be removed |
1835:| Costs | **KEEP** | the main carrier of personality as disposition |
1836:| Intention across a walk | **KEEP** | keeps only the leading reason |
1837:| Walks weighed by their end (M2) | **KEEP**; decide whether to ship | |
1838:| Ambiguity band and seeded pick | **KEEP** mechanism, **MODIFY** frequency | 38 % is weighing flatness |
=== Docs/experiments/accumulated-history/report.md (285 lines)
230:## 12. Recommendation
232:**KEEP.**
=== Docs/experiments/action-representation/report.md (438 lines)
184:**Verdict.** High sharing is not bad in itself, and for walks it is largely legitimate. It is
299:**Verdict: a legitimate behavioural choice with an artifactual representation.** Refraining
390:## 13. Recommendation
392:**MODIFY.**
=== Docs/experiments/causal-routes/report.md (586 lines)
54:**Verdict: MODIFY** (section 13), by the criteria committed before the
74:relation the author declared. The verdict does not depend on it.
413:  the responses were read.** The verdict does not rest on it.
454:## 13. Verdict
456:# MODIFY
460:> **KEEP**: D passes the retained and the new invariants. A, B and C fail the
466:> **MODIFY**: D does all it is built for, but a needed piece of causal structure
471:> **REBUILD**: the intention architecture cannot carry route identity without
475:> **ABANDON**: no representation can tell the critical pair apart, even with
478:**What was met.** Every quantitative condition of KEEP was met:
486:**Why not KEEP.** The last KEEP condition speaks of the families, and every
488:compute, the enabler, and the MODIFY row names it explicitly. D adds the belief
491:this MODIFY.**
498:**Not REBUILD.** The critical distinction was expressed over the same staged
506:**Not ABANDON.** D tells the critical pair apart in every cell.
508:**What MODIFY means here:**
=== Docs/experiments/decision-sensitivity/report.md (636 lines)
131:   These are S1.6's recommendation (its section 11) verbatim.
171:What it represents now is a **reference**, as S1.5 and S1.6 recommended, not the model.
369:| Hypothesis | Verdict |
564:## 15. Recommendation
566:**MODIFY.**
=== Docs/experiments/episode/report.md (288 lines)
236:**KEEP.**
=== Docs/experiments/intent-carrying/report.md (345 lines)
289:**KEEP.**
=== Docs/experiments/intention-formation/report.md (317 lines)
257:## 11. Verdict
259:# KEEP
=== Docs/experiments/intention-generalization/report.md (288 lines)
229:## 10. Verdict
231:# MODIFY
233:Last time this line was **KEEP**. The generalization evidence would still support
=== Docs/experiments/intention-ranking/report.md (475 lines)
41:**Verdict: MODIFY** (section 14). The problem sits in ranking and in how a rule
438:## 14. Verdict
440:# MODIFY
442:The criteria were committed with the predictions. MODIFY required the violations
446:and **6.1 %**, against a REBUILD threshold of 1 %. The violations are exactly
447:where MODIFY puts them.
458:**Not REBUILD:** no stage below ranking failed. **Not ABANDON:** the reproduction
=== Docs/experiments/intention-representation/report.md (465 lines)
52:**Verdict: MODIFY**, for the representation experiment, by the criteria committed
425:## 14. Verdict
427:# MODIFY
429:These criteria were committed with the predictions. **KEEP** needed everything
431:invent. **MODIFY** applies when all of that holds except that some conclusion B
443:**Not REBUILD:** B failed nothing it was built to pass, and lost none of what was
444:already proven. **Not ABANDON:** every representation can state reasons as
447:**What MODIFY means here:** carry forward evidence identity, statement
=== Docs/experiments/reason-semantics/report.md (537 lines)
67:**Recommendation: MODIFY** (section 13), by the criteria committed before the
394:  single case, and the verdict leans on it.
439:## 13. Recommendation
441:# MODIFY
444:- **KEEP** needs one representation that (i) passes every check of every
448:- **MODIFY** applies when one meets (i) and (ii) but none meets all four.
449:- **REBUILD** applies when none meets (i) and (ii).
460:**Not REBUILD.** Every required distinction was expressed within the existing
466:**What MODIFY means, concisely.** Before any implementation, the vocabulary
480:This is a recommendation about vocabulary, not an implementation.
=== Docs/experiments/same-act-different-reason/report.md (348 lines)
230:| Want | An intention that says what it intends | Verdict |
322:## 15. Verdict
324:# MODIFY
=== Docs/experiments/route-applicability/review.md (394 lines)
322:### KEEP
330:### MODIFY
340:### REBUILD
345:### ABANDON
372:**Nothing has been implemented. This is a recommendation about vocabulary, not
=== Prototypes/llm-morning/REPORT-2.md (633 lines)
=== Prototypes/llm-morning/REPORT-3.md (1020 lines)
=== Prototypes/llm-morning/REPORT-4.md (1574 lines)
3:Guilt and grudges now come from events the rules see: who accused whom falsely, who admitted it after denying it, who ate in front of someone hungry. The prompt shows them as those events, in plain dated lines, with at
113:  - new tests cover each event grudge (a false accusation, a true one raising nothing, confessing after denying and after accusing, eating in front of someone hungry or not hungry, a share-out), the 15-minute fall, t
159:test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
=== Prototypes/llm-morning/REPORT-5.md (3570 lines)
288:test_no_prompt_holds_the_old_verdicts (test_morning.PressureTest.test_no_prompt_holds_the_old_verdicts) ... ok
=== Prototypes/llm-morning/REPORT.md (1066 lines)
~~~~

### 5.9 Explicitly rejected, deferred or postponed ideas

~~~~bash
grep -rniE 'rejected|ruled out|was not used|taken out|\bDEFER\b|do not ship|not proposed|should wait|must not be done' --include='*.md' Docs README.md Prototypes/llm-morning/REPORT*.md | grep -v -- '-all.md' | cut -c1-260
~~~~

~~~~text
Docs/audit/system-understanding-audit.md:1384:| Summed appeal rewards breadth | S1 | adding reasons is neutral | nobody eats; standing still collects three part-reasons | **unchanged**; C3 rejected (S1.2) |
Docs/experiments/action-representation/report.md:386:The second question (the mapping from wants to acts) should wait. Its compression is partly
Docs/experiments/causal-routes/report.md:101:They were fixed before the run. They are not proposed as the formula. On the
Docs/experiments/decision-sensitivity/report.md:574:how wants become acts. Interpretation strength should wait until the step from wants to acts
Docs/experiments/intent-carrying/results.md:65:The five design conditions, seeds 1-10. Every search carries the meaning of the want that led it: `find_out` -> `take_responsibility`, `restore_standing` -> `assert_authority`, nothing otherwise. **This mapping is
Docs/experiments/intention-formation/report.md:268:Not kept, and not proposed: anything in production. No intention system is being
Docs/experiments/intention-ranking/report.md:303:reasons reading identical evidence. They are a malformed rule set to be rejected,
Docs/experiments/reason-semantics/measurements.md:524:- #3 sonnet: Show that valuing control and being dominant combined to produce a felt entitlement to decide the matter personally, strong enough to assert authority rather than defer.
Docs/slices/S1.2/c3-rejected/collapse.md:1:# C3, rejected: removing standing still's unearned credit
Docs/slices/S1.2/report.md:13:| `c3-rejected/` | The change that was tried and taken out, with what it did |
Docs/slices/S1.2/report.md:49:| C3 | **The unearned credit moved.** Each want's weight on standing still moved, at the same weight, onto the acts it avoids. Which acts come from the event rules: the only acts anybody reads as a slight, a challenge or a threat.
Docs/slices/S1.2/report.md:64:## 3. C3, and why it was taken out
Docs/slices/S1.2/report.md:68:Removing it collapsed the cast (`c3-rejected/collapse.md`):
Docs/slices/S1.2/report.md:201:| That advantage removed | **FAILED**: removal collapses personality, so it was taken out |
Docs/slices/S1.5/diagnosis-before.md:50:| Taken out | Decisions whose top option changes |
Docs/slices/S1.5/diagnosis-current.md:50:| Taken out | Decisions whose top option changes |
Docs/slices/S1.5/report.md:348:| Traits and values as dispositions (B, `respond`) | **MODIFY.** Keep it as the direction and the switch; do not ship it until the pacing it exposes has a cause-based answer. |
Docs/slices/S1.6/report.md:255:**Outcome feedback, the alternative,** was ruled out by measurement rather than argument:
Docs/slices/S1.6/report.md:353:| A durable open question carrying `find_out` | **DEFER** to when a question can be answered. |
Docs/slices/S1.6/report.md:354:| Where people were last seen | **DEFER**; the residue it would remove is 75 walks in 50 mornings and honest. |
Docs/slices/S1.7/report.md:13:| `held-out-predictions.md` | The hypothesis, why the suggested scenario was rejected, and eight predictions, committed before any S1.7 code (`1d59e43`) |
Docs/slices/S1.7/report.md:30:## 1. Why the suggested scenario was not used
Docs/slices/S1.7/report.md:253:It must not be done inside this slice, and I have not done it. It changes every number in every
Docs/understanding/morning-walkthrough.md:147:  weighed walking to the kitchen for food and rejected it: he pictured eating there as not worth it
Prototypes/llm-morning/REPORT.md:44:- **The answer.** JSON `{option, say, feeling, reason}`, requested with a response schema. It is rejected, and the rules choose instead, when it isn't JSON, a field is missing, the option wasn't offered, or a speech option h
~~~~

### 5.10 Checks behind the NOT FOUND list

~~~~bash
echo "--- slice folders"; ls Docs/slices; echo "--- experiment folders"; ls Docs/experiments; echo "--- test fixtures named like the listed follow-ups (selection, half-life, private/audience, S1.8, interpretation strength)"; ls Assets/_Project/Tests/EditMode | grep -iE "selection|halflife|half|private|audience|s18|interpretationstrength"; echo "(end of list)"; echo "--- documents mentioning human reviewers/panel/readers"; grep -rliE "human (reviewer|panel|reader)" Docs --include=*.md | grep -v -- "-all.md"; echo "--- in-file Date: lines"; grep -m1 -nE "^Date" Docs/slices/*/review.md Docs/slices/S1.*/report.md Docs/experiments/*/report.md Docs/experiments/route-applicability/review.md | cut -c1-120
~~~~

~~~~text
--- slice folders
S0
S1
S1.1
S1.2
S1.3
S1.4
S1.5
S1.6
S1.7
--- experiment folders
accumulated-history
action-representation
causal-routes
decision-sensitivity
episode
intent-carrying
intention-formation
intention-generalization
intention-ranking
intention-representation
reason-semantics
route-applicability
same-act-different-reason
--- test fixtures named like the listed follow-ups (selection, half-life, private/audience, S1.8, interpretation strength)
(end of list)
--- documents mentioning human reviewers/panel/readers
Docs/experiments/causal-routes/annotation/protocol.md
Docs/experiments/causal-routes/report.md
Docs/experiments/reason-semantics/report.md
Docs/experiments/route-applicability/protocol.md
Docs/experiments/route-applicability/review.md
--- in-file Date: lines
Docs/slices/S0/review.md:3:Date: 2026-09-10
Docs/slices/S1/review.md:3:Date: 2026-09-12
Docs/slices/S1.1/report.md:3:Date: 2026-09-12. Status: complete, stopped for review.
Docs/slices/S1.2/report.md:3:Date: 2026-09-13. Status: complete, stopped for review.
Docs/slices/S1.3/report.md:3:Date: 2026-09-15. Status: complete, stopped for review.
Docs/slices/S1.4/report.md:3:Date: 2026-09-15. Status: complete, stopped for review.
Docs/slices/S1.5/report.md:3:Date: 2026-09-15. Status: complete, stopped for review. A narrow diagnostic experiment:
Docs/slices/S1.6/report.md:3:Date: 2026-09-16. Status: complete, stopped for review. Two switchable defect fixes, measur
Docs/slices/S1.7/report.md:3:Date: 2026-09-16. Status: complete, stopped for review. **No mechanism was added and no rul
Docs/experiments/accumulated-history/report.md:3:Date: 2026-09-20. Status: complete, stopped for review. **A small verti
Docs/experiments/action-representation/report.md:3:Date: 2026-09-19. Status: complete, stopped for review. **An audit, n
Docs/experiments/decision-sensitivity/report.md:3:Date: 2026-09-19. Status: complete, stopped for review. **Not S1.8.** 
Docs/experiments/episode/report.md:3:Date: 2026-09-20. Status: complete, stopped for review. **Not a system audit and no
Docs/experiments/intent-carrying/report.md:3:Date: 2026-09-20. Status: complete, stopped for review. **Not S1.8.** One s
~~~~

## 6. Coverage: every report, spec and experiment file found

Inventory command (its output is the Path column below):

~~~~bash
find CLAUDE.md CONTEXT_REPORT.md README.md Docs reports Assets/_Project/Data/Experiments Assets/_Project/Data/Tests Prototypes/llm-morning Tools -path '*/.venv' -prune -o -type f ! -name '*.meta' \( -name '*.md' -o -name '*.txt' -o -name '*.json' -o -name '*.csv' -o -name '*.py' \) -print | grep -vE 'Prototypes/llm-morning/(v[1-4]/|[a-z_0-9]+\.py$)' | sort
~~~~

Left out on purpose: the prototype's code (`Prototypes/llm-morning/*.py` and the frozen copies in `v1/` to `v4/`), and the shipped simulation data (`Assets/_Project/Data/{Minds,Rules,Scenario}`). Neither is a report or a spec. Section 5.4 also turned up `Assets/_Project/Scripts/Core/Sim/S0Report.cs` and `S1Report.cs`. They are *not an experiment*: they are code that writes the S0 and S1 trace documents (rows 1 and 2). Each row below gives the file's timeline row from section 1, or *not an experiment* with the reason.

Five files appeared while this file was being written, apparently from other sessions: `reports/state/01_repo_map.md`, `reports/state/02_csharp_core.md`, `Prototypes/llm-morning/reports/knowledge_audit.md`, and `04_decision_pipeline.md` and `05_results_quality.md` in `Prototypes/llm-morning/reports/state/`. None was in the first inventory, and none contains an experiment. Only their opening lines were read, to classify them.

| Path | Assignment |
|---|---|
| `Assets/_Project/Data/Experiments/causal-routes.json` | 21 (causal routes) |
| `Assets/_Project/Data/Experiments/held-out-people.json` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Assets/_Project/Data/Experiments/intentions.json` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Assets/_Project/Data/Experiments/reason-semantics.json` | 22 (reason semantics) |
| `Assets/_Project/Data/Experiments/route-applicability.json` | 23 (route applicability) |
| `Assets/_Project/Data/Tests/expectations.json` | 1 (S0) |
| `CLAUDE.md` | not an experiment: project instruction file (one rule about stopping processes) |
| `CONTEXT_REPORT.md` | not an experiment: read-only context report for a reviewer, 2026-09-24, untracked |
| `Docs/audit/census.md` | 10 (audit) |
| `Docs/audit/system-understanding-audit.md` | 10 (audit) |
| `Docs/experiments/accumulated-history/accumulated-history-all.md` | 15 (accumulated history) |
| `Docs/experiments/accumulated-history/measurements.md` | 15 (accumulated history) |
| `Docs/experiments/accumulated-history/predictions.md` | 15 (accumulated history) |
| `Docs/experiments/accumulated-history/report.md` | 15 (accumulated history) |
| `Docs/experiments/accumulated-history/results.md` | 15 (accumulated history) |
| `Docs/experiments/action-representation/action-representation-all.md` | 12 (action representation) |
| `Docs/experiments/action-representation/diagnostic.md` | 12 (action representation) |
| `Docs/experiments/action-representation/report.md` | 12 (action representation) |
| `Docs/experiments/causal-routes/annotation/items.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/protocol.md` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-1.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-2.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-3.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-4.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-5.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/annotation/responses/reviewer-6.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/causal-routes-all.md` | 21 (causal routes) |
| `Docs/experiments/causal-routes/classification.json` | 21 (causal routes) |
| `Docs/experiments/causal-routes/measurements.md` | 21 (causal routes) |
| `Docs/experiments/causal-routes/predictions.md` | 21 (causal routes) |
| `Docs/experiments/causal-routes/report.md` | 21 (causal routes) |
| `Docs/experiments/causal-routes/results.md` | 21 (causal routes) |
| `Docs/experiments/decision-sensitivity/baseline.md` | 11 (decision sensitivity) |
| `Docs/experiments/decision-sensitivity/decision-sensitivity-all.md` | 11 (decision sensitivity) |
| `Docs/experiments/decision-sensitivity/report.md` | 11 (decision sensitivity) |
| `Docs/experiments/decision-sensitivity/results.md` | 11 (decision sensitivity) |
| `Docs/experiments/episode/episode-all.md` | 14 (episode) |
| `Docs/experiments/episode/measurements.md` | 14 (episode) |
| `Docs/experiments/episode/predictions.md` | 14 (episode) |
| `Docs/experiments/episode/report.md` | 14 (episode) |
| `Docs/experiments/episode/results.md` | 14 (episode) |
| `Docs/experiments/intent-carrying/intent-carrying-all.md` | 13 (intent carrying) |
| `Docs/experiments/intent-carrying/predictions.md` | 13 (intent carrying) |
| `Docs/experiments/intent-carrying/report.md` | 13 (intent carrying) |
| `Docs/experiments/intent-carrying/results.md` | 13 (intent carrying) |
| `Docs/experiments/intention-formation/intention-formation-all.md` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Docs/experiments/intention-formation/measurements.md` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Docs/experiments/intention-formation/predictions.md` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Docs/experiments/intention-formation/report.md` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Docs/experiments/intention-formation/results.md` | 17 (intention formation; the frozen rules are reused by 18 to 23) |
| `Docs/experiments/intention-generalization/intention-generalization-all.md` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Docs/experiments/intention-generalization/measurements.md` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Docs/experiments/intention-generalization/predictions.md` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Docs/experiments/intention-generalization/report.md` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Docs/experiments/intention-generalization/results.md` | 18 (intention generalization; the sweep is reused by 19 to 23) |
| `Docs/experiments/intention-ranking/classification.json` | 19 (intention ranking) |
| `Docs/experiments/intention-ranking/intention-ranking-all.md` | 19 (intention ranking) |
| `Docs/experiments/intention-ranking/measurements.md` | 19 (intention ranking) |
| `Docs/experiments/intention-ranking/predictions.md` | 19 (intention ranking) |
| `Docs/experiments/intention-ranking/report.md` | 19 (intention ranking) |
| `Docs/experiments/intention-ranking/results.md` | 19 (intention ranking) |
| `Docs/experiments/intention-representation/classification.json` | 20 (intention representation) |
| `Docs/experiments/intention-representation/intention-representation-all.md` | 20 (intention representation) |
| `Docs/experiments/intention-representation/measurements.md` | 20 (intention representation) |
| `Docs/experiments/intention-representation/predictions.md` | 20 (intention representation) |
| `Docs/experiments/intention-representation/report.md` | 20 (intention representation) |
| `Docs/experiments/intention-representation/results.md` | 20 (intention representation) |
| `Docs/experiments/reason-semantics/annotation/items.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/protocol.md` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-1.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-2.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-3.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-4.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-5.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/annotation/responses/reviewer-6.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/classification.json` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/measurements.md` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/prediction-model.py` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/predictions.md` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/reason-semantics-all.md` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/report.md` | 22 (reason semantics) |
| `Docs/experiments/reason-semantics/results.md` | 22 (reason semantics) |
| `Docs/experiments/route-applicability/annotation/items.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-1.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-2.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-3.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-4.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-5.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/annotation/responses/reviewer-6.json` | 23 (route applicability) |
| `Docs/experiments/route-applicability/measurements.md` | 23 (route applicability) |
| `Docs/experiments/route-applicability/prediction-model.py` | 23 (route applicability) |
| `Docs/experiments/route-applicability/predictions.md` | 23 (route applicability) |
| `Docs/experiments/route-applicability/protocol.md` | 23 (route applicability) |
| `Docs/experiments/route-applicability/results.md` | 23 (route applicability) |
| `Docs/experiments/route-applicability/review.md` | 23 (route applicability) |
| `Docs/experiments/route-applicability/route-applicability-all.md` | 23 (route applicability) |
| `Docs/experiments/same-act-different-reason/measurements.md` | 16 (same act) |
| `Docs/experiments/same-act-different-reason/predictions.md` | 16 (same act) |
| `Docs/experiments/same-act-different-reason/report.md` | 16 (same act) |
| `Docs/experiments/same-act-different-reason/results.md` | 16 (same act) |
| `Docs/experiments/same-act-different-reason/same-act-different-reason-all.md` | 16 (same act) |
| `Docs/slices/S0/review.md` | 1 (S0) |
| `Docs/slices/S0/traces/event-by-event.md` | 1 (S0) |
| `Docs/slices/S0/traces/expectation-results.md` | 1 (S0) |
| `Docs/slices/S0/traces/full-trace.txt` | 1 (S0) |
| `Docs/slices/S0/traces/where-everyone-stands.md` | 1 (S0) |
| `Docs/slices/S0/traces/why-they-felt-that.md` | 1 (S0) |
| `Docs/slices/S1.1/baseline.md` | 3 (S1.1) |
| `Docs/slices/S1.1/causal-examples.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis-after-c1.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis-after-c2.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis-after-c3.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis-before.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis-current.md` | 3 (S1.1) |
| `Docs/slices/S1.1/diagnosis.md` | 3 (S1.1) |
| `Docs/slices/S1.1/experiment-results.md` | 3 (S1.1) |
| `Docs/slices/S1.1/fading-rate-current.md` | 3 (S1.1) |
| `Docs/slices/S1.1/fading-rate.md` | 3 (S1.1) |
| `Docs/slices/S1.1/held-out-predictions.md` | 3 (S1.1) |
| `Docs/slices/S1.1/held-out-results.md` | 3 (S1.1) |
| `Docs/slices/S1.1/report.md` | 3 (S1.1) |
| `Docs/slices/S1.2/audit-after-c1.md` | 4 (S1.2) |
| `Docs/slices/S1.2/audit-after-c2.md` | 4 (S1.2) |
| `Docs/slices/S1.2/audit-before.md` | 4 (S1.2) |
| `Docs/slices/S1.2/audit-current.md` | 4 (S1.2) |
| `Docs/slices/S1.2/baseline-behaviour.md` | 4 (S1.2) |
| `Docs/slices/S1.2/baseline.md` | 4 (S1.2) |
| `Docs/slices/S1.2/behaviour-noise-current.md` | 4 (S1.2) |
| `Docs/slices/S1.2/c3-rejected/audit.md` | 4 (S1.2) |
| `Docs/slices/S1.2/c3-rejected/collapse.md` | 4 (S1.2) |
| `Docs/slices/S1.2/c3-rejected/reach.md` | 4 (S1.2) |
| `Docs/slices/S1.2/c3-rejected/what-each-of-them-did.md` | 4 (S1.2) |
| `Docs/slices/S1.2/c3-rejected/what-was-behind-it.md` | 4 (S1.2) |
| `Docs/slices/S1.2/diagnosis.md` | 4 (S1.2) |
| `Docs/slices/S1.2/experiment-results.md` | 4 (S1.2) |
| `Docs/slices/S1.2/reach-after-c1.md` | 4 (S1.2) |
| `Docs/slices/S1.2/reach-after-c2.md` | 4 (S1.2) |
| `Docs/slices/S1.2/reach-before.md` | 4 (S1.2) |
| `Docs/slices/S1.2/reach-current.md` | 4 (S1.2) |
| `Docs/slices/S1.2/report.md` | 4 (S1.2) |
| `Docs/slices/S1.3/diagnosis-after.md` | 5 (S1.3) |
| `Docs/slices/S1.3/diagnosis-before.md` | 5 (S1.3) |
| `Docs/slices/S1.3/diagnosis-current.md` | 5 (S1.3) |
| `Docs/slices/S1.3/diagnosis.md` | 5 (S1.3) |
| `Docs/slices/S1.3/experiment-results.md` | 5 (S1.3) |
| `Docs/slices/S1.3/report.md` | 5 (S1.3) |
| `Docs/slices/S1.4/attribution.md` | 6 (S1.4) |
| `Docs/slices/S1.4/diagnosis-after.md` | 6 (S1.4) |
| `Docs/slices/S1.4/diagnosis-before.md` | 6 (S1.4) |
| `Docs/slices/S1.4/diagnosis-current.md` | 6 (S1.4) |
| `Docs/slices/S1.4/diagnosis.md` | 6 (S1.4) |
| `Docs/slices/S1.4/experiment-results.md` | 6 (S1.4) |
| `Docs/slices/S1.4/held-out-predictions.md` | 6 (S1.4) |
| `Docs/slices/S1.4/held-out-results.md` | 6 (S1.4) |
| `Docs/slices/S1.4/report.md` | 6 (S1.4) |
| `Docs/slices/S1.5/S1.5-all.md` | 7 (S1.5) |
| `Docs/slices/S1.5/diagnosis-before.md` | 7 (S1.5) |
| `Docs/slices/S1.5/diagnosis-current.md` | 7 (S1.5) |
| `Docs/slices/S1.5/diagnosis.md` | 7 (S1.5) |
| `Docs/slices/S1.5/experiment-results.md` | 7 (S1.5) |
| `Docs/slices/S1.5/held-out-predictions.md` | 7 (S1.5) |
| `Docs/slices/S1.5/held-out-results.md` | 7 (S1.5) |
| `Docs/slices/S1.5/report.md` | 7 (S1.5) |
| `Docs/slices/S1.5/walks.md` | 7 (S1.5) |
| `Docs/slices/S1.6/S1.6-all.md` | 8 (S1.6) |
| `Docs/slices/S1.6/diagnosis-before.md` | 8 (S1.6) |
| `Docs/slices/S1.6/diagnosis-current.md` | 8 (S1.6) |
| `Docs/slices/S1.6/diagnosis.md` | 8 (S1.6) |
| `Docs/slices/S1.6/experiment-results.md` | 8 (S1.6) |
| `Docs/slices/S1.6/held-out-predictions.md` | 8 (S1.6) |
| `Docs/slices/S1.6/held-out-results.md` | 8 (S1.6) |
| `Docs/slices/S1.6/report.md` | 8 (S1.6) |
| `Docs/slices/S1.7/S1.7-all.md` | 9 (S1.7) |
| `Docs/slices/S1.7/diagnosis-before.md` | 9 (S1.7) |
| `Docs/slices/S1.7/diagnosis-current.md` | 9 (S1.7) |
| `Docs/slices/S1.7/diagnosis.md` | 9 (S1.7) |
| `Docs/slices/S1.7/experiment-results.md` | 9 (S1.7) |
| `Docs/slices/S1.7/held-out-predictions.md` | 9 (S1.7) |
| `Docs/slices/S1.7/report.md` | 9 (S1.7) |
| `Docs/slices/S1/batch/decisions.csv` | 2 (S1) |
| `Docs/slices/S1/batch/what-each-of-them-did.md` | 2 (S1) |
| `Docs/slices/S1/batch/what-was-behind-it.md` | 2 (S1) |
| `Docs/slices/S1/held-out-predictions.md` | 2 (S1) |
| `Docs/slices/S1/held-out-results.md` | 2 (S1) |
| `Docs/slices/S1/review.md` | 2 (S1) |
| `Docs/slices/S1/traces/a-mother-made-to-feel-like-a-suspect.txt` | 2 (S1) |
| `Docs/slices/S1/traces/full-trace-daniel_ate_it-seed1.txt` | 2 (S1) |
| `Docs/slices/S1/traces/morning-daniel_ate_it.md` | 2 (S1) |
| `Docs/slices/S1/traces/morning-daniel_hid_it.md` | 2 (S1) |
| `Docs/slices/S1/traces/morning-elena_fed_mara.md` | 2 (S1) |
| `Docs/slices/S1/traces/morning-mara_ate_it.md` | 2 (S1) |
| `Docs/slices/S1/traces/morning-miscount.md` | 2 (S1) |
| `Docs/slices/S1/traces/smoke-morning.md` | 2 (S1) |
| `Docs/understanding/commit-log.md` | not an experiment: log of the commit of the LLM prototype, untracked |
| `Docs/understanding/morning-walkthrough.md` | not an experiment: one baseline morning told plainly (written 2026-09-24 at `8cdf644`) |
| `Docs/understanding/narrator-setup.md` | not an experiment: setup notes for the `narrate.sh` story tool |
| `Docs/understanding/runs/daniel_ate_it-1.md` | not an experiment: narrator output, one baseline morning |
| `Docs/understanding/target-morning.md` | not an experiment: acceptance criteria (Never / Possible / Should vary) for judging a run |
| `Docs/understanding/understanding-all.md` | not an experiment: merged copy of `Docs/understanding/` |
| `Prototypes/llm-morning/REPORT-2.md` | 25 (LLM step 2) |
| `Prototypes/llm-morning/REPORT-3.md` | 26 (LLM step 3) |
| `Prototypes/llm-morning/REPORT-4.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/REPORT-5.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/REPORT.md` | 24 (LLM step 1) |
| `Prototypes/llm-morning/cache/aborted/attempt1-seed1.json` | 24 (LLM step 1, aborted attempts) |
| `Prototypes/llm-morning/cache/aborted/attempt1-seed2.json` | 24 (LLM step 1, aborted attempts) |
| `Prototypes/llm-morning/cache/aborted/attempt2-seed1.json` | 24 (LLM step 1, aborted attempts) |
| `Prototypes/llm-morning/cache/gemini-3.5-flash-lite-daniel_ate_it-seed1.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/cache/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/cache/gemini-3.5-flash-lite-daniel_ate_it-seed3.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/cache/v2/gemini-3.5-flash-lite-daniel_ate_it-seed1.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/cache/v2/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/cache/v2/gemini-3.5-flash-lite-daniel_ate_it-seed3.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/cache/v3/gemini-3.5-flash-lite-daniel_ate_it-seed1.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/cache/v3/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/cache/v3/gemini-3.5-flash-lite-daniel_ate_it-seed3.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/cache/v4/gemini-3.5-flash-lite-daniel_ate_it-seed1.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/cache/v4/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/cache/v4/gemini-3.5-flash-lite-daniel_ate_it-seed3.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/cache/v4/gemini-3.5-flash-lite-daniel_ate_it-seed4.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/cache/v4/gemini-3.5-flash-lite-daniel_ate_it-seed5.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed1.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed2.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed3.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-miscount-seed1.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-miscount-seed2.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemini-3.5-flash-lite-miscount-seed3.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed1.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed2.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed3.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed4.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/cache/v5/gemma-4-31b-it-daniel_ate_it-gemma-seed5.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/config.json` | not an experiment: prototype configuration |
| `Prototypes/llm-morning/reports/knowledge_audit.md` | not an experiment: read-only audit of what each prototype character knows, 2026-09-26, untracked; appeared during this inspection |
| `Prototypes/llm-morning/reports/llm_call_audit.md` | not an experiment: read-only audit of Gemini API call sites, 2026-09-26, untracked |
| `Prototypes/llm-morning/reports/state/04_decision_pipeline.md` | not an experiment: sibling state report (prototype decision pipeline), 2026-09-26, untracked; appeared during this inspection |
| `Prototypes/llm-morning/reports/state/05_results_quality.md` | not an experiment: sibling state report (how prototype runs are judged; states no report ranks any v5 run), 2026-09-26, untracked; appeared during this inspection |
| `Prototypes/llm-morning/requirements.txt` | not an experiment: prototype configuration |
| `Prototypes/llm-morning/runs/cmp.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.md` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.meta.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.replay.md` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.replay.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed1.transcript.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed2.md` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed2.meta.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed2.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed2.transcript.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed3.md` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed3.meta.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed3.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/daniel_ate_it-seed3.transcript.json` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/list_models.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/probe-gemma-1.stdout.txt` | 28 (LLM step 5, Gemma probe) |
| `Prototypes/llm-morning/runs/probe-gemma-2.stdout.txt` | 28 (LLM step 5, Gemma probe) |
| `Prototypes/llm-morning/runs/unittest.stdout.txt` | 24 (LLM step 1) |
| `Prototypes/llm-morning/runs/v2/cmp.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.md` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.meta.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.replay.md` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.replay.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed1.transcript.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed2.md` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed2.meta.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed2.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed2.transcript.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed3.md` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed3.meta.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed3.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/daniel_ate_it-seed3.transcript.json` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/metrics.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/unittest.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v2/v1-transcript.stdout.txt` | 25 (LLM step 2) |
| `Prototypes/llm-morning/runs/v3/cmp.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.md` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.meta.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.replay.md` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.replay.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed1.transcript.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed2.md` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed2.meta.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed2.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed2.transcript.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed3.md` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed3.meta.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed3.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/daniel_ate_it-seed3.transcript.json` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/metrics3.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/unittest.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/v1-transcript.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v3/v2-check.stdout.txt` | 26 (LLM step 3) |
| `Prototypes/llm-morning/runs/v4/cmp.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.meta.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.replay.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.replay.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed1.transcript.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed2.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed2.meta.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed2.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed2.transcript.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed3.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed3.meta.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed3.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed3.transcript.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed4.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed4.meta.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed4.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed4.transcript.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed5.md` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed5.meta.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed5.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/daniel_ate_it-seed5.transcript.json` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/earlier.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/metrics4.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/quota-note.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v4/unittest.stdout.txt` | 27 (LLM step 4) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed1.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed1.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed1.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed1.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed2.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed2.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed2.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed2.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed3.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed3.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed3.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed3.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed4.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed4.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed4.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed4.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed5.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed5.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed5.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/daniel_ate_it-gemma-seed5.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/gemma-models.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed1.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed1.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed1.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed1.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed2.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed2.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed2.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed2.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed3.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed3.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed3.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/mara_ate_it-seed3.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/metrics5.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed1.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed1.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed1.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed1.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed2.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed2.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed2.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed2.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed3.md` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed3.meta.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed3.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/miscount-seed3.transcript.json` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/probe-gemma-seed2.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/unittest.stdout.txt` | 28 (LLM step 5) |
| `Prototypes/llm-morning/runs/v5/v4-replay.stdout.txt` | 28 (LLM step 5) |
| `README.md` | not an experiment: project readme; its Known defects section summarises slice findings |
| `Tools/narrate-morning/bin/narrate-morning.runtimeconfig.json` | not an experiment: build output of the narrator tool |
| `Tools/narrate-morning/bin/stderr.txt` | not an experiment: build output of the narrator tool |
| `reports/state/01_repo_map.md` | not an experiment: sibling state report (repository map), 2026-09-26, untracked; appeared during this inspection |
| `reports/state/02_csharp_core.md` | not an experiment: sibling state report (C# core), 2026-09-26, untracked; appeared during this inspection |
| `reports/state/03_experiment_history.md` | not an experiment: this deliverable |

Files in the inventory: 376. Rows marked UNASSIGNED: 0.
