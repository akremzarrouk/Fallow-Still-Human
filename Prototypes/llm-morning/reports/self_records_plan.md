# Self records: plan (frozen before any live call)

Mode: run. The question: do people's own records of their acts keep them on one act?

`reports/stuck_facts.md` found that in the calm prompts, where there is no pattern line, Elena chose `reassure_all`
24 of 24 times and Mara chose `accuse_daniel` 20 of 20 times. Three blocks in those prompts record a person's own
acts:
- Mara's grudge line lists the times she was angry ("you were angry with Daniel today at minutes 12 and 15, and at
  09:42 and 09:48").
- Yesterday's block counts acts ("Mara accused Daniel 5 times (min ...)").
- "Your own last words today" lists each person's own last acts.

This probe removes those records, one kind at a time and both together, from the same 18 prompts.

## Predictions (word for word, as given)

P1: in SW, at least 6 of the 18 answers choose a different option than calm_probe's for the same person and minute.

P2: in S, Mara chooses accuse_daniel in at most 3 of her live asks.

P3: in W, Elena chooses reassure_all in at most 3 of her 6 asks.

P4 (validity): no answer chooses an option that was not offered.

Decision rule: a version that meets its prediction names what to remove in production; if none does, the loop is held by the situation's own facts, not by self-records.

Which prediction belongs to which version: S to P2, W to P3, SW to P1. P4 covers all three.

The baseline is calm_probe's 18 answers (`runs/calm_probe/scene1.json`, `scene3.json`).

## The probe (`runs/self_records/probe.py`)

- **The 18 prompts.** The stored calm_probe prompts, taken as they are: scenes 1 and 3; 10:00, 10:30 and 11:00;
  Elena, Leo and Mara (each awake person in Daniel's room who knows of the visit first-hand). No replay.
- **The model and system instruction** are calm_probe's: `gemini-3.5-flash-lite` and `world.SYSTEM`.
  Before any ask, each stored prompt's cache key is built with HEAD's `world.SYSTEM` and checked. It must be in
  `cache/calm_probe/scene<k>.json` with the stored answer. If one is not, the scene stops.
- **The client seeds** are calm_probe's: 201 for scene 1, 202 for scene 3.
- **The three versions** are text edits only. Every other line stays byte for byte the same, in the same order; the
  probe asserts this for each prompt.
  - **S (self-tallies).**
    - In each `Against <Name> (<level>): ...` line, the clause `you were angry with <Name> ...` is deleted, and the
      causes before it are kept. A line with nothing left is deleted.
    - In `Yesterday and last night:`, each `- Accusations: ...` or `- Confrontations: ...` line is rewritten as who did
      it to whom, once, with no count and no minutes. For example, `- Mara accused Daniel of taking it.`,
      `- You accused Daniel of taking it.`, `- Leo confronted Daniel.`
  - **W (own acts).** `Your own last words today:` and its `- ` lines are deleted.
  - **SW.** Both. The probe checks that SW equals W applied to S.
- **What the versions change, per person.** These are the same at all three minutes and in both scenes, except where noted.
  - **Elena.**
    - S rewrites 2 lines: Mara's accusations and Leo's confrontations. Her `Against the others: nothing.` has no
      clause to delete.
    - W deletes 4 lines.
  - **Leo.**
    - S changes 4 lines: his two `Against` lines lose their anger clause, and the two tallies are rewritten.
    - W deletes 4 lines.
  - **Mara.**
    - S changes 4 lines into 3:
      - `Against Daniel (a lot)` keeps "two days ago, Daniel admitted taking it at minute 33, after denying it to
        you at minute 06".
      - `Against Leo (a little): you were angry with Leo at 09:45.` has nothing left, so it is deleted. Its clause
        reads "at 09:45", not "today at 09:45". It is the same clause from the same code (`world.py:284`/`295`,
        `grudge_facts`).
      - The two tallies are rewritten.
    - W deletes 4 lines.
  - Every version changes every one of the 18 prompts, so no answer is expected to be reused. The rule still stands:
    an unchanged prompt takes calm_probe's answer, marked, and a prompt already asked in this probe is not asked
    again.
- **A diff per prompt** goes to `runs/self_records/diffs/scene<k>_<HHMM>_<who>_<version>.diff`. Each row of
  `runs/self_records/scene<k>.json` also holds its diff.
- **Answers** are recorded and never applied.
- **Cap.** At most 60 live asks in all, enforced by the client wrapper. 54 are expected.
- **The key** is read from `GEMINI_API_KEY` and written to no file.
- **The fake run** (`--fake`) uses a temp folder and the fake model. It writes nothing in the repository.

## Measures

- **Choice changed:** the answer's `option` differs from calm_probe's for the same scene, minute and person.
- **Words repeating across the three minutes,** per scene, person and version, with calm_probe as the fourth version.
  The measure is `reports/stuck_facts.md` §1's:
  - Words: the `say` text, lower-cased, split on letters, digits and apostrophes, as a set.
  - A pair of answers counts when `|A ∩ B| / max(|A|, |B|) >= 0.6`.
  - Word-for-word equal answers are counted too.
  - `silent` has no words and is not paired.
