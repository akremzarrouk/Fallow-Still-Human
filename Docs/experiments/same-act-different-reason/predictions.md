# Same act, different reason: predictions

Written **before the experiment was run**, and kept as written.

The question: when one physical act is performed for different reasons, can the
current simulation keep the difference, and does anything read it?

The brief separates three questions and this file keeps them separate:

1. **Representation** — can the same act carry different intentions at all?
2. **Propagation** — does that difference survive act → event → perception → appraisal/memory/belief?
3. **Behaviour** — can it end in a different act?

A failure at 3 is not a failure at 1. A failure at 2 is the important one.

## What was read before predicting, and what was not

Predictions are worthless if they are written after the answer. So, exactly:

- **Read before predicting:** the rule files and the perception code, to find
  which rules are *keyed* on which labels. This is static structure, not a
  result, and the brief asks for predictions "refined before execution if the
  actual existing code requires a more precise formulation". Where a prediction
  follows from that reading rather than from a guess, it is marked **(from the
  rules)** and claims no credit.
- **Not read, not run, not known:** any measurement. No arm of this experiment
  had been run when this file was written. Everything about what actually
  happens — which emotions land and how hard, what the witness makes of it,
  whether any later decision moves, whether removing the intent restores the
  baseline byte for byte — was open.

## The reader map, from the rules

Six intentions exist in the shipped vocabulary (`self_meanings`):
`take_responsibility`, `share_information`, `protect`, `assert_authority`,
`prevent_argument`, `took_what_was_not_mine`.

Searching every rule file for rules keyed on any of them finds **four, all in
appraisal**:

| Intention | Rules that read it |
|---|---|
| `assert_authority` | `asserting_yourself_is_done_angry` -> anger |
| `protect` | `looking_after_someone_does_not_stop_the_worry` -> anxiety |
| `took_what_was_not_mine` | `what_you_did_in_the_night_is_felt_as_shame` -> shame; `and_as_being_afraid_of_what_they_will_think` -> fear |
| `take_responsibility` | **none** |
| `share_information` | **none** |
| `prevent_argument` | **none** |

No interpretation rule, no belief nudge, no motivation rule and no decision rule
is keyed on any intention. Memory scalers can match a stored meaning by name,
but the only two names used anywhere are `concern` and `threat`, which no
intention can ever equal.

## The vocabulary question, asked in advance

The brief names three motivation contexts — `find_out`, `restore_standing`,
`get_food` — and asks whether the existing labels can say what each one intends.
**(from the rules)** The answer available before running anything:

| Want | Nearest shipped intention | Is it the same thing? |
|---|---|---|
| `restore_standing` | `assert_authority` | **Yes.** The shipped backstory already pairs them (b06) |
| `find_out` | `take_responsibility` | **No, but it is the shipped precedent.** p02 is Daniel searching the house with intent `take_responsibility`, glossed "searching the house is what someone in charge does". That is the intention of a man in charge, not the intention of a man who wants to know |
| `get_food` | **nothing** | No label in the vocabulary says "I want food". `took_what_was_not_mine` is about having done wrong, not about wanting to eat |

So one of the brief's three intentions is inexpressible and a second is only
approximately expressible. Rather than invent labels, the experiment runs **all
six shipped intentions** on the one act, plus a no-intent baseline, and reports
the vocabulary gap as a result in its own right.

## Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | The same physical act, by the same person, at the same minute, in the same world, can be executed under each of the six intentions | any arm fails to produce the act, or the acts differ physically |
| P2 | With the hook unset, and with the hook set but returning null, the whole morning is identical to the baseline — every act, every margin, every event | any difference |
| P3 | The intention survives execution and is carried on the `WorldEvent` | the event's intent is null or wrong |
| P4 | The actor recovers the intention: his reading of his own act **is** the intention, at weight 1.00, with no rule consulted | he reads it by rule instead |
| P5 | A witness in the same room receives **nothing** that distinguishes the arms: same access, same reading, same weight, same everything | the witness differs between arms |
| P6 | **(from the rules)** Exactly one existing reader consumes the intention — appraisal — and it consumes only three of the six | a second kind of reader turns out to consume it, or appraisal does not |
| P7 | Where a reader exists (`assert_authority`, `protect`, `took_what_was_not_mine`), the actor's emotions after his own act differ from the baseline | the emotions are identical |
| P8 | Where no reader exists (`take_responsibility`, `share_information`, `prevent_argument`), everything downstream is identical **except the string kept in memory** | something else moves |
| P9 | Setting an intention does not only add. It **replaces** the reading the rules would have given, so an arm with an unread intention can end up with *less* than the baseline: the baseline's rule-derived meaning, and any memory of it, is gone | the rule-derived reading survives alongside the intention |
| P10 | The stored intention is invisible to every memory scaler, because the only meanings any scaler names are `concern` and `threat` | a scaler reads it |
| P11 | At least one arm changes a later decision in the same morning | no arm moves any decision |
| P12 | No new action, want, rule, number or production mechanism is needed to run any of this | one is needed |

**Committed in advance, and riskier:**

- The strongest arm should be `assert_authority`, because it is the only
  intention whose reader produces an emotion aimed at somebody — and on this act
  the event has **no target**, so the anger should land aimed at nobody. Whether
  an untargeted anger then does anything is unknown to me.
- `took_what_was_not_mine` has two readers, so it may produce more feeling than
  `assert_authority` despite being a worse fit for a man counting his own
  pantry. If so, the size of an intention's effect is decided by how many rules
  happen to name it, not by what it means. I expect this.
- P9 is the prediction I would most like to be wrong about, and the one I think
  is most likely to be right.

**What would make this a major result:** P7 and P11 both holding, by a traceable
path. **What would reproduce the known bottleneck:** P5, P6 and P8 holding
together — the distinction exists on the event, and almost nothing in the
simulation is built to read it.
