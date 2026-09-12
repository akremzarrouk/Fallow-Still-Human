# S1.2 baseline

The state at the end of S1.1 (commit `0cc78c3`), measured before anything in deliberation
changed. Instrumentation was added first and changed no behaviour: the full suite passed,
220 of 220 (the 218 S1.1 tests plus two diagnosis tests), and every report the suite
regenerates under `Docs/slices/S0`, `S1` and `S1.1` came out byte for byte identical.

## From the S1 and S1.1 tests (40 seeds per condition unless stated)

| Measure | Value |
|---|---|
| Different people, same morning (mean pairwise) | 0.65 to 0.66 per condition, closest pair 0.29 |
| Temperament swap, Daniel wearing Leo's data | 0.73 |
| One person, different nights (S1 metric) | 0.03, largest 0.10 |
| Settled by the seed | 47.6% |
| Ties between genuinely different actions | 40.8% |
| Worst back-and-forth pacing | 17 |
| Eating, starving and alone, 30 mornings | 0 |
| Interruptions, one morning (`daniel_ate_it`, seed 3) | 32 |
| Held-out P6, Leo's first decision unchanged by his night | 20 of 20 seeds |

## Behaviour against the noise floor (S1.1, twenty-seed pools)

| Who | Night vs no night | Largest same-condition difference | Above the noise |
|---|---|---|---|
| Mara | 0.098 | 0.027 | yes |
| Elena | 0.063 | 0.023 | yes |
| Daniel, ate it | 0.072 | 0.067 | no |
| Daniel, hid it | 0.070 | 0.071 | no |
| Mara, fresh seeds 41 to 80 | 0.131 | 0.051 | yes |
| Elena, fresh seeds 41 to 80 | 0.074 | 0.035 | yes |

## From the new audit (five conditions, seeds 1 to 20, 7,960 decisions)

Full tables in `audit-before.md` and `reach-before.md`.

| Measure | Value |
|---|---|
| Decisions per person per morning | 19.9 |
| Deciding because interrupted | 44.3% of decisions |
| Interruptions per morning | 35.3 |
| ... caused by an event that itself stirred less than the threshold | 46.8% |
| Walks followed by something the want behind them did not serve | 46.8% |
| Standing still chosen / on top | 40.6% / 45.2% |
| Settled by the seed / between different kinds | 48.3% / 41.2% |
| Pacing, mean per person per morning / worst | 0.36 / 17 |
| `avoid_exposure` decisive | 1.9% of the decisions it was present in |
| `keep_peace` / `guard_supplies` decisive | 55.9% / 49.7% |
| Mara, first decision: best option changed by her night | 0 of 20 seeds |
| Mara, same minute in both worlds, different choice | 65 of 184 |
