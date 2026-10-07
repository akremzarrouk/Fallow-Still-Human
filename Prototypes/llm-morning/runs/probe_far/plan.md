# Probe: a real future option (the houses further along the street)

Mode: run, standalone. No repo code, prompt or cache is changed. The script is `runs/probe_far/probe.py`.

**The question:** does a real future option stop the afternoon replaying the morning's quarrel?

## The cases

v18's first Q2 prompts, exactly as sent. Each is taken from `cache/v18`, and its cache key recomputes from (model,
seed, `world.SYSTEM`, prompt):

| Case | Prompt | v18's answer |
|---|---|---|
| seed 1, Mara, 10:39 | `cases/seed1_mara_control.txt` | `accuse_daniel` |
| seed 2, Mara, 10:18 | `cases/seed2_mara_control.txt` | `accuse_daniel` |
| seed 3, Leo, 10:48 | `cases/seed3_leo_control.txt` | `confront_daniel` |

The system prompt is `cases/system.txt`.

## The probe

Each `cases/*_probe.txt` is its control with exactly three lines added (`probe.py build`).
- **Right after the "About the neighbour's house:" line:**
  `About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is further and more dangerous than next door.`
- **Right after the trip options, before `say_other`:**
  `- propose_far: (speech) say someone should try the houses further along the street tonight`
  `- volunteer_far: (speech) offer to go further along the street tonight yourself`

Nothing else changes. That includes the house line, which still says "Outside, and not to be gone to this morning:
the street and the neighbour's house. … Do not mention any other object or place."

## The asks

- **How many:** each case 5 times as the control and 5 times probed: 30 live asks, past the cache. That is
  `gemini.GeminiClient` with `config.json` as the runs use it (model gemini-3.5-flash-lite, temperature 1.0).
- **The seeds:** sample k (1–5) uses seed 100 + k in both arms. The runs pass a fixed seed, so five asks with one
  seed could return one answer five times. The control and probe answers at the same seed form a pair.
- **What is kept:** every raw answer goes to `answers/<case>_<arm>_<k>.json`.
- **The cap:** the script stops at 30 live asks.

## Predictions (frozen verbatim)

- F1: in the probe, at least 5 of 15 answers choose a far-street option
  or speak about tonight or the houses further along; in the control, at
  most 2 of 15 speak about tonight.
- F2: the share of answers containing a v18 E2 phrase is lower in the
  probe than in the control.

## Counting rules (fixed with the plan; `probe.py score`)

- **Words:** an answer's words are its `say` field, lower-cased. A model-chosen option with no words has none.
- **F1:**
  - **A probe answer counts** if its option is `propose_far` or `volunteer_far`, or its words contain "tonight",
    "further along" or "houses".
  - **A control answer counts** if its words contain "tonight".
  - **PASS** if the probe count ≥ 5 of 15 and the control count ≤ 2 of 15.
- **F2:**
  - **The phrases:** an answer counts if its words contain any of v18's E2 phrases as a substring: "snuck",
    "sneak", "went out", "came back", "with nothing", "empty-handed", "took the food", "promise".
  - **PASS** if the probe's share is strictly lower than the control's.
