# Mara's and Elena's behaviour effect on the S1.1 code, counted three ways

Written by hand. Measured by a temporary test run once against commit `a354e98` (S1.1
behaviour plus the S1.2 instrumentation, which changes nothing), then deleted and not
committed. It exists because the S1.1 fresh-seed behaviour test failed after S1.2's
changes, and the fair comparison was what the same measures said before them. The
counting was chosen after that failure was seen, which is why the S1.1 measure is kept
beside it.

Twenty-seed pools. Effect is night against no night across pools; noise is the larger
same-condition difference between the two pools.

| Seeds | Who | Counting | Night vs no night | Noise | Ratio |
|---|---|---|---|---|---|
| 1 to 40 | mara | every decision (the S1.1 measure) | 0.098 | 0.027 | 3.6 |
| 1 to 40 | mara | minutes spent | 0.097 | 0.021 | 4.7 |
| 41 to 80 | mara | every decision | 0.131 | 0.051 | 2.6 |
| 41 to 80 | mara | minutes spent | 0.121 | 0.042 | 2.9 |
| 1 to 40 | elena | every decision | 0.063 | 0.023 | 2.8 |
| 1 to 40 | elena | minutes spent | 0.082 | 0.024 | 3.5 |
| 41 to 80 | elena | every decision | 0.074 | 0.035 | 2.1 |
| 41 to 80 | elena | minutes spent | 0.091 | 0.017 | 5.4 |

("Not counting carrying on" is identical to "every decision" here, because S1.1 had no
carrying on.)

Seeds 1 to 40, per morning:

| Who | Night | Stopped | ... by what they already felt | Decisions | Sitting with somebody, share of minutes |
|---|---|---|---|---|---|
| mara | yes | 11.9 | 6.2 | 17.6 | 64% |
| mara | no | 9.6 | 6.2 | 17.1 | 72% |
| elena | yes | 15.6 | 7.7 | 23.0 | 37% |
| elena | no | 15.0 | 7.5 | 22.5 | 45% |

On the S1.1 code the night made Mara sit with somebody less (64% against 72%). On the
S1.2 code it makes her do it more (78% against 73%, `behaviour-noise-current.md`).
