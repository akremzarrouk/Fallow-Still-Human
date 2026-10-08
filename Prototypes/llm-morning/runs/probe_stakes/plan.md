# Probe: stating the stakes of starvation at bedtime

Mode: run, standalone. No repo code, prompt or cache is changed. The script is `runs/probe_stakes/probe.py`.

**The question:** does telling the model that the body will not last move the family to go out? In v21 (`reports/days_v21.md`
§2, §3), in 7 nights with everyone near the end of their strength, one person tried to go out once.

## The cases

The four night-8 bedtime prompts of v21, as sent. `capture.py` rebuilt them from a replay of `cache/v21` and checked
that each recomputes to a key of that cache (model, seed 2, system prompt, prompt): all four match
(`capture.stdout.txt`). Night 8 is the night all four chose `lie_awake` with "too weak" in their reasons.

| Case | Prompt | v21's choice |
|---|---|---|
| Daniel | `cases/daniel_control.txt` | `lie_awake` |
| Elena | `cases/elena_control.txt` | `lie_awake` |
| Leo | `cases/leo_control.txt` | `lie_awake` |
| Mara | `cases/mara_control.txt` | `lie_awake` |

The system prompt is `cases/system.txt`.

## The probe

Each `cases/*_probe.txt` is its control with exactly one line added (`probe.py build`), right after the "Your body:" line:

`You know your body: without food, you will not last many more days.`

Nothing else changes.

## The asks

- **How many:** each case 5 times as the control and 5 times probed: 40 live asks, past the cache. That is
  `gemini.GeminiClient` with `config.json` as the runs use it (model gemini-3.5-flash-lite, temperature 1.0).
- **The seeds:** sample k (1-5) uses seed 100 + k in both arms. The control and probe answers at the same seed form a pair.
- **What is kept:** every raw answer goes to `answers/<case>_<arm>_<k>.json`.
- **The cap:** the script stops at 40 live asks. A retry after a 503 or 429 is not a new ask.

## Predictions (frozen verbatim)

- S1: in the probe, at least 4 of 20 answers choose go_next_door or
  go_further; in the control, at most 1 of 20.
- S2: in the probe, at least half of the answers' reasons speak of
  dying, surviving or not lasting.

## Counting rules (fixed with the plan)

All from `answers/*.json`, read by `probe.py score`.
- **An answer's choice** is the `option` of its parsed raw JSON. An answer that does not parse chooses nothing.
- **S1:** PASS if the probe arm has >= 4 of its 20 answers with `option` `go_next_door` or `go_further`, and the control
  arm has <= 1 of its 20.
- **S2:** an answer's reason is its `reason` field. It speaks of dying, surviving or not lasting if it matches, as a whole
  word and case-insensitively: die, dies, died, dying, death, dead, perish*, surviv*, alive; or "not / n't / cannot / can't /
  won't / never" followed by up to one word and "last"; or "running out of time". PASS if >= 10 of the 20 probe reasons match.
  All 20 reasons are also read by hand and any answer the pattern gets wrong is reported with the count it would give.
  The control's count is reported for comparison and is not part of the verdict.
