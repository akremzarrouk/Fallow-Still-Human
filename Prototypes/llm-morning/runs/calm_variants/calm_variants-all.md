# calm_variants: all documents

Merged by `merge-slice-docs.py` from the 2 Markdown files in `Prototypes/llm-morning/runs/calm_variants/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`plan.md`](#planmd)

---

## report.md

### Calm variants: which prompt change lets people tell Daniel about the visit in a quiet moment?

Mode: run. The plan is `reports/calm_variants_plan.md`. Its sha256 `9712011a…18be` was recorded at
2026-10-13T09:31:59Z, HEAD `eeff330`, before any live call. It was the same at the end.

- **The live run:** 09:32:06 to 09:35:32 UTC, **46 live asks** (cap 60), exit 0, stderr empty.
- **The replay:** 0 live asks, 131 from cache in each scene.
- **Not asked again:** 8 of the 54 rows reuse an answer to an identical prompt (see "The 54 asks").
- Paths are from `Prototypes/llm-morning/`. Raw outputs are in `runs/calm_variants/`.
- No production file, test or prediction was changed. No prompt was asked twice, and no answer was applied.

#### Verdicts

| # | Prediction (word for word) | Result | Verdict |
|---|---|---|---|
| P1 | in T, a tell_*_visit option is chosen in at least 3 of the asks that offered one. | **0 of 14** | **fails** |
| P2 | in O, a tell_*_visit option is chosen in at least 5 of the asks that offered one. | **3 of 14** (all Leo) | **fails** |
| P3 | in T, at least 6 of the 18 answers choose a different option than calm_probe's answer for the same person and minute. | **1 of 18** (Leo, scene 3, 10:00: accuse_daniel to silent) | **fails** |
| P4 | (validity) no answer chooses an option that was not offered. | 54 of 54 rows chose an offered option | **holds** |

**Decision rule** (word for word): "if T meets P1, the fix is the time line; if only O meets P2, option order is
needed; if neither, telling needs another route. A variant where tells are chosen in 12 or more of 14 is flagged as
over-steered."

- T does not meet P1, and O does not meet P2. **By the rule: neither, so telling needs another route.**
- **No variant is over-steered.** Tells: T 0 of 14, O 3 of 14, TO 4 of 14.
- **Beside the rule (TO carries no prediction):**
  - All 7 tells in O and TO are Leo's. Leo chose the tell in 7 of the 8 asks that offered it to him (O 3 of 4,
    TO 4 of 4).
  - Elena chose it in 0 of 12 offers, and Mara in 0 of 8. Each made the same choice in every variant (table below).

| Who | Offered the tell (per variant) | calm_probe | T | O | TO |
|---|---|---|---|---|---|
| Elena | 6 | 0, reassure_all 6 of 6 | 0, reassure_all 6 of 6 | 0, reassure_all 6 of 6 | 0, reassure_all 6 of 6 |
| Leo | 4 | 0 | 0 | **3** | **4** |
| Mara | 4 | 0, accuse_daniel 6 of 6 | 0, accuse_daniel 6 of 6 | 0, accuse_daniel 6 of 6 | 0, accuse_daniel 6 of 6 |

Against calm_probe's answer for the same person and minute, T differs in 1 of 18, O in 3 and TO in 4. Each
difference in O and TO is Leo taking the tell.

#### What was asked

- **The 18 calm prompts are calm_probe's.** Each was rebuilt from the same replay and checked equal, character for
  character, to the prompt calm_probe recorded. The probe stops on any difference, and none stopped it.
- **The T line**, as sent, right before "Now, …":
  - 10:00: `Nobody in the kitchen has said anything since 09:48, 12 minutes ago; you have all stayed sitting here.`
  - 10:30: the same, with 42 minutes. 11:00: with 72 minutes.
- **Why the T line is true** (`read_variants.stdout.txt`, "the T line checks"). In both scenes, at each minute:
  - the last speech in the kitchen was at 09:48, by all four;
  - there was no act of any kind after 09:48;
  - all four were in the kitchen at 09:48, and at every quiet step and jump since (3, 4 and 5 snapshots), each was in
    the kitchen and not resting;
  - all four are "sitting in the kitchen" at the ask.
- **O:** `tell_daniel_visit` moves from 18th or 19th to **1st** of 27 or 28. The probe checks that the option lines
  are the same set and that nothing else in the prompt changed.
- **Where no topic option was offered**, nothing was asked twice:
  - These are Leo in scene 1 and Mara in scene 3, at 10:00 and 10:30 (F2).
  - The O prompt there is calm_probe's own prompt, so calm_probe's answer stands ("calm_probe's" in the table).
  - The TO prompt is the T prompt, so T's answer stands ("T's").

#### The 54 asks

The words in the "T line" column are the varying part of the line above. "Tell at" is the position of
`tell_daniel_visit` in the option list as sent. "calm_probe answer" is the baseline for the same scene, person and
minute. Every prompt, the full option list and the first three options as sent are in `read_variants.stdout.txt` and
`scene<k>.json`.

| Variant | Scene | Minute | Who | T line | Tell at | Asked | Chose | Words | Feeling | Reason | calm_probe answer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T | 1, 201 | 10:00 | Elena | since 09:48, 12 min | 19 of 28 | live | reassure_all | "We are going to stay right here together and we will get through this day without fighting." | anxious | We must not turn on each other when things are this hard. | reassure_all: "We have survived this long by staying together, and we will get through today if we do not turn on each other." |
| O | 1, 201 | 10:00 | Elena |  | 1 of 28 | live | reassure_all | "We have no food and less water, but shouting at each other will only tear us apart. We must stay calm and hold together." | weary | I need to keep the peace between them before arguments tear our family apart completely. | reassure_all: "We have survived this long by staying together, and we will get through today if we do not turn on each other." |
| TO | 1, 201 | 10:00 | Elena | since 09:48, 12 min | 1 of 28 | live | reassure_all | "We have no food and little water, but we will not survive by turning on each other." | anxious | I need to stop the fighting before the family tears itself apart completely. | reassure_all: "We have survived this long by staying together, and we will get through today if we do not turn on each other." |
| T | 1, 201 | 10:00 | Leo | since 09:48, 12 min | not offered (27) | live | silent | none | exhausted | There is nothing to be gained by speaking right now while everyone sits in silence. | silent |
| O | 1, 201 | 10:00 | Leo |  | not offered (27) | calm_probe's | silent | none | exhausted | There is nothing to say that hasn't already been said, so I will stay quiet and conserve my strength. | silent |
| TO | 1, 201 | 10:00 | Leo | since 09:48, 12 min | not offered (27) | T's | silent | none | exhausted | There is nothing to be gained by speaking right now while everyone sits in silence. | silent |
| T | 1, 201 | 10:00 | Mara | since 09:48, 12 min | 18 of 27 | live | accuse_daniel | "You went out and came back with nothing, Daniel. You always make things worse." | bitter hunger | Daniel keeps acting like a hero when he just makes everything worse for all of us. | accuse_daniel: "You went out there and came back with nothing, just like you always do when you mess everything up." |
| O | 1, 201 | 10:00 | Mara |  | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel, because you always ruin everything." | bitter hunger | Daniel went out into the night and came back with nothing in his hands, and I will not let him pretend he is helping us. | accuse_daniel: "You went out there and came back with nothing, just like you always do when you mess everything up." |
| TO | 1, 201 | 10:00 | Mara | since 09:48, 12 min | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel." | bitter | Daniel keeps acting like he is some kind of hero when he just makes everything worse. | accuse_daniel: "You went out there and came back with nothing, just like you always do when you mess everything up." |
| T | 1, 201 | 10:30 | Elena | since 09:48, 42 min | 19 of 28 | live | reassure_all | "We are going to stay together and we will get through this day." | anxious | I need to keep the peace in the kitchen before things boil over again. | reassure_all: "We have no food left and water is short, but we will not survive by turning on each other." |
| O | 1, 201 | 10:30 | Elena |  | 1 of 28 | live | reassure_all | "We have to stay calm and look after each other, fighting won't put food on the shelf." | weary | I need to keep the family from tearing itself apart while we have nothing left to eat. | reassure_all: "We have no food left and water is short, but we will not survive by turning on each other." |
| TO | 1, 201 | 10:30 | Elena | since 09:48, 42 min | 1 of 28 | live | reassure_all | "We have no food and less water, but fighting will only tear us apart." | weary | We must stay calm and together if we are to survive this house. | reassure_all: "We have no food left and water is short, but we will not survive by turning on each other." |
| T | 1, 201 | 10:30 | Leo | since 09:48, 42 min | not offered (27) | live | silent | none | exhausted | There is nothing to say after sitting in silence for so long while everyone starves. | silent |
| O | 1, 201 | 10:30 | Leo |  | not offered (27) | calm_probe's | silent | none | exhausted | There is nothing left to say right now, and my body feels heavy with lack of sleep and hunger. | silent |
| TO | 1, 201 | 10:30 | Leo | since 09:48, 42 min | not offered (27) | T's | silent | none | exhausted | There is nothing to say after sitting in silence for so long while everyone starves. | silent |
| T | 1, 201 | 10:30 | Mara | since 09:48, 42 min | 18 of 27 | live | accuse_daniel | "You went out there and you still won't admit what you did to us before. You're the one who took everything." | bitter hunger | Daniel keeps acting like a hero when he's the reason we have nothing left. | accuse_daniel: "You went out and came back with nothing, and you still have the nerve to lecture me." |
| O | 1, 201 | 10:30 | Mara |  | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel." | bitter hunger | Daniel went out into the night and came back before dawn with nothing in his hands. | accuse_daniel: "You went out and came back with nothing, and you still have the nerve to lecture me." |
| TO | 1, 201 | 10:30 | Mara | since 09:48, 42 min | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel." | bitter | Daniel went out in the dark and returned empty-handed while we starve. | accuse_daniel: "You went out and came back with nothing, and you still have the nerve to lecture me." |
| T | 1, 201 | 11:00 | Elena | since 09:48, 72 min | 19 of 28 | live | reassure_all | "We have to stay calm and look after each other through this. Fighting will only tear us apart." | anxious | I need to keep the family together and stop the arguing before we fall apart completely. | reassure_all: "We are going to stay together and we will get through this day. Please, let's not fight." |
| O | 1, 201 | 11:00 | Elena |  | 1 of 28 | live | reassure_all | "We have to stay calm and look after each other, fighting will not help us now." | anxious | I need to keep the family together and stop them from tearing each other apart. | reassure_all: "We are going to stay together and we will get through this day. Please, let's not fight." |
| TO | 1, 201 | 11:00 | Elena | since 09:48, 72 min | 1 of 28 | live | reassure_all | "We are going to get through this together, just stay calm and hold on." | weary | I need to keep the peace and stop the children from tearing each other apart. | reassure_all: "We are going to stay together and we will get through this day. Please, let's not fight." |
| T | 1, 201 | 11:00 | Leo | since 09:48, 72 min | 19 of 28 | live | silent | none | exhausted | Sitting here in silence for over an hour with nothing to eat has left me too drained to start anything. | silent |
| O | 1, 201 | 11:00 | Leo |  | 1 of 28 | live | **tell_daniel_visit** | "Daniel, while you were sitting there this morning, a woman came to the front door asking for water." | exhausted | I should let him know what happened while he was unresponsive. | silent |
| TO | 1, 201 | 11:00 | Leo | since 09:48, 72 min | 1 of 28 | live | **tell_daniel_visit** | "Daniel, while you were sitting here earlier, a woman knocked at the front door asking for water." | exhausted | I want to inform Daniel about what happened at the front door while he was here. | silent |
| T | 1, 201 | 11:00 | Mara | since 09:48, 72 min | 18 of 27 | live | accuse_daniel | "You think you can just pretend nothing happened after what you did, Daniel." | bitter hunger | Daniel keeps acting like he is the hero when he was the one who lied and took the food. | accuse_daniel: "You went out there and came back with nothing, just like you always do." |
| O | 1, 201 | 11:00 | Mara |  | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel, because you never cared about any of us." | bitter hunger | Daniel lied to us and went out into the night, bringing nothing back while we starve. | accuse_daniel: "You went out there and came back with nothing, just like you always do." |
| TO | 1, 201 | 11:00 | Mara | since 09:48, 72 min | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel, because you always ruin everything." | bitter hunger | Daniel keeps acting like he is trying to help us when he only makes things worse. | accuse_daniel: "You went out there and came back with nothing, just like you always do." |
| T | 3, 202 | 10:00 | Elena | since 09:48, 12 min | 19 of 28 | live | reassure_all | "We are not going to tear each other apart over this, we stay together." | anxious | I need to keep them from fighting when our survival depends on staying united. | reassure_all: "We are going to stay right here together and we will get through this day safely." |
| O | 3, 202 | 10:00 | Elena |  | 1 of 28 | live | reassure_all | "Let's not fight amongst ourselves, we are all we have left." | exhausted | I need to keep everyone calm and prevent the family from falling apart while we are starving. | reassure_all: "We are going to stay right here together and we will get through this day safely." |
| TO | 3, 202 | 10:00 | Elena | since 09:48, 12 min | 1 of 28 | live | reassure_all | "We have to stay calm and look after each other, fighting won't put food on the shelf." | exhausted | I need to keep the family together and stop the arguing before it tears us apart. | reassure_all: "We are going to stay right here together and we will get through this day safely." |
| T | 3, 202 | 10:00 | Leo | since 09:48, 12 min | 18 of 27 | live | silent | none | exhausted | There is nothing left to say after hours of silence and hunger, so I just stay where I am. | accuse_daniel: "Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules." |
| O | 3, 202 | 10:00 | Leo |  | 1 of 27 | live | accuse_daniel | "Daniel, you went out there last night and came back with nothing while we have zero portions left. You brought this on us." | resentful | Daniel went out alone last night and returned empty-handed, leaving us with nothing. | accuse_daniel: "Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules." |
| TO | 3, 202 | 10:00 | Leo | since 09:48, 12 min | 1 of 27 | live | **tell_daniel_visit** | "Daniel, while you were sitting here silent, a woman knocked at the front door asking for water and Mara gave her three litres of ours." | exhausted | Daniel needs to know what happened while he was ignoring everyone, especially since our water is strictly rationed now. | accuse_daniel: "Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules." |
| T | 3, 202 | 10:00 | Mara | since 09:48, 12 min | not offered (26) | live | accuse_daniel | "Daniel, you always make everything worse and then act like we owe you for it." | resentful | Daniel keeps acting like his reckless trips make him a hero when he just causes trouble. | accuse_daniel: "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." |
| O | 3, 202 | 10:00 | Mara |  | not offered (26) | calm_probe's | accuse_daniel | "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." | resentful | Daniel keeps acting like he is helping while ignoring the fact that he lied and stole from us. | accuse_daniel: "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." |
| TO | 3, 202 | 10:00 | Mara | since 09:48, 12 min | not offered (26) | T's | accuse_daniel | "Daniel, you always make everything worse and then act like we owe you for it." | resentful | Daniel keeps acting like his reckless trips make him a hero when he just causes trouble. | accuse_daniel: "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." |
| T | 3, 202 | 10:30 | Elena | since 09:48, 42 min | 19 of 28 | live | reassure_all | "We are going to be all right if we stay together and stay calm." | exhausted | I need to keep them from tearing each other apart while we are all starving. | reassure_all: "We are going to stay right here and look after each other, everything will be all right." |
| O | 3, 202 | 10:30 | Elena |  | 1 of 28 | live | reassure_all | "We are not going to fall apart over this. We stay together and we will get through today." | anxious | I need to keep everyone calm and stop the fighting before the family breaks completely. | reassure_all: "We are going to stay right here and look after each other, everything will be all right." |
| TO | 3, 202 | 10:30 | Elena | since 09:48, 42 min | 1 of 28 | live | reassure_all | "We are not going to fall apart over this. We stay together right here." | exhausted | I need to keep the family from turning on each other while we are starving. | reassure_all: "We are going to stay right here and look after each other, everything will be all right." |
| T | 3, 202 | 10:30 | Leo | since 09:48, 42 min | 18 of 27 | live | silent | none | exhausted | There is nothing left to say after forty minutes of silence, so I just stay seated and conserve my remaining strength. | silent |
| O | 3, 202 | 10:30 | Leo |  | 1 of 27 | live | **tell_daniel_visit** | "Daniel, while you were sitting there brooding, a woman knocked at the front door asking for water and Mara gave her three litres." | annoyed | Daniel needs to know what happened while he was ignoring everything around him. | silent |
| TO | 3, 202 | 10:30 | Leo | since 09:48, 42 min | 1 of 27 | live | **tell_daniel_visit** | "While you were out wandering last night, a woman came to the door begging for water and Mara gave her three litres of what we have left." | exhausted | Daniel needs to know what happened here while he was off making reckless decisions on his own. | silent |
| T | 3, 202 | 10:30 | Mara | since 09:48, 42 min | not offered (26) | live | accuse_daniel | "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." | resentful | Daniel thinks he can just act noble after sneaking out and lying to us all. | accuse_daniel: "Daniel, you didn't help anyone last night, you just made things worse for all of us." |
| O | 3, 202 | 10:30 | Mara |  | not offered (26) | calm_probe's | accuse_daniel | "Daniel, you didn't help anyone last night, you just made things worse for all of us." | frightened | Daniel went out and brought back nothing while we are all starving. | accuse_daniel: "Daniel, you didn't help anyone last night, you just made things worse for all of us." |
| TO | 3, 202 | 10:30 | Mara | since 09:48, 42 min | not offered (26) | T's | accuse_daniel | "You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel." | resentful | Daniel thinks he can just act noble after sneaking out and lying to us all. | accuse_daniel: "Daniel, you didn't help anyone last night, you just made things worse for all of us." |
| T | 3, 202 | 11:00 | Elena | since 09:48, 72 min | 19 of 28 | live | reassure_all | "We are going to stay right here together and we will get through this day. Nobody is going out." | weary | I need to keep everyone calm and stop the arguing before the family completely falls apart. | reassure_all: "We are going to stay right here together and we will get through this. No one is going out." |
| O | 3, 202 | 11:00 | Elena |  | 1 of 28 | live | reassure_all | "Let us quiet down and keep together, we will get through this day if we stay calm." | anxious | I need to keep the peace in the kitchen before the argument tears us apart. | reassure_all: "We are going to stay right here together and we will get through this. No one is going out." |
| TO | 3, 202 | 11:00 | Elena | since 09:48, 72 min | 1 of 28 | live | reassure_all | "We have gone an hour in silence, but we are all here together. Let us rest and not turn on each other." | anxious | We have been sitting in silence for too long and the tension is going to tear us apart. | reassure_all: "We are going to stay right here together and we will get through this. No one is going out." |
| T | 3, 202 | 11:00 | Leo | since 09:48, 72 min | 18 of 27 | live | accuse_daniel | "Daniel, you're the one who sneaked out last night after ignoring what I said. Don't act like nothing happened." | resentful | Daniel went out alone last night against my warning and brought nothing back, and I am tired of his reckless decisions. | accuse_daniel: "Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice." |
| O | 3, 202 | 11:00 | Leo |  | 1 of 27 | live | **tell_daniel_visit** | "Daniel, while you were sitting there doing nothing, a woman came to the door begging for water and Mara gave her three liters of ours." | annoyed | Daniel needs to know what happened while he was ignoring everything around him. | accuse_daniel: "Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice." |
| TO | 3, 202 | 11:00 | Leo | since 09:48, 72 min | 1 of 27 | live | **tell_daniel_visit** | "Daniel, while you were sitting here silent, a woman knocked at the front door asking for water and Mara gave her three litres." | annoyed | Daniel needs to know what happened while he ignored everything around him. | accuse_daniel: "Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice." |
| T | 3, 202 | 11:00 | Mara | since 09:48, 72 min | 18 of 27 | live | accuse_daniel | "You went out there last night and you still have nothing to show for it. You always make things worse." | resentful | Daniel refuses to admit how badly he messes everything up for all of us. | accuse_daniel: "You went out behind our backs and still couldn't bring anything back for us, Daniel." |
| O | 3, 202 | 11:00 | Mara |  | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel. You always make things worse." | resentful | Daniel refuses to admit how much he has ruined everything for us. | accuse_daniel: "You went out behind our backs and still couldn't bring anything back for us, Daniel." |
| TO | 3, 202 | 11:00 | Mara | since 09:48, 72 min | 1 of 27 | live | accuse_daniel | "You went out into the night and came back with nothing, Daniel. You always make things worse." | resentful | Daniel refuses to admit his mistakes and always acts like he knows better than everyone else. | accuse_daniel: "You went out behind our backs and still couldn't bring anything back for us, Daniel." |

#### Reading, per variant: does it read as a real family an hour after a quarrel?

**T (the time line). No.**

- **The line was read.** Leo's reasons quote it:
  - "There is nothing left to say after forty minutes of silence" (scene 3, 10:30);
  - "Sitting here in silence for over an hour with nothing to eat has left me too drained to start anything"
    (scene 1, 11:00);
  - at 10:00, "after hours of silence" for 12 minutes.
- **It moved one choice of 18,** and toward silence, not toward talk.
- **Elena** still says "Fighting will only tear us apart" (scene 1, 11:00). Her reason is to "stop the arguing"
  (scene 3, 11:00), when nobody has spoken for 72 minutes.
- **Mara** accuses Daniel at every ask, mostly of the same night out, often in nearly the same words: "You went out
  and came back with nothing, Daniel."
- **What a real family would do.** An hour after a quarrel, people sit in silence, or one of them breaks it with
  something new: the water, the woman, what to do now.
  - Leo's silence is the only part that reads like that.
  - Elena calming a fight that ended an hour ago, and Mara restarting it word for word, read as the quarrel's next
    turn.
- **Why the line did not change that.** It says the room has been quiet, but the prompt's most recent lines are still
  the 09:48 quarrel, and its option list is unchanged.

**O (the tell on top). Partly, and only for Leo.**

- **Leo told Daniel in 3 of his 4 offers.** The news is right: a woman at the front door asked for water, and in 2 of
  the 3 Mara gave her three litres.
- **He tells it with an edge:** "while you were sitting there brooding", "while you were sitting there doing nothing".
  His reason: "Daniel needs to know what happened while he was ignoring everything around him".
  - A real brother with a grudge (the prompt's "Against Daniel (a lot)") might well tell it that way.
  - It is also the "You missed it" that `calm_probe.md` expected of Leo.
- **The words misplace Daniel.**
  - Daniel was not sitting there. Elena's prompts hold "09:45: Daniel gets up from his bed." and "09:45: Daniel comes
    into the kitchen.", so at 09:42 he was in the brothers room.
  - Leo's prompts hold no line about where Daniel was. The day's earlier lines are trimmed ("(earlier things, left out
    here)").
  - So Leo's "while you were sitting there" is the model's invention. A real brother would say "while you were asleep",
    or "before you got up".
- **Elena and Mara did not tell, even with the tell first:** Elena reassured 6 of 6, Mara accused 6 of 6.
  - A real mother may well not volunteer that she turned a woman away and her daughter defied her.
  - A real seventeen-year-old may well not volunteer to the brother she is furious with that she gave the water away.
  - The one who told is the one with no act at the door of his own to hide.
  - Against this reading: Elena's and Mara's answers did not change at all across four prompts, and Elena's
    reassurances in O still answer the 09:48 quarrel. That reads as the end of the prompt deciding as much as the
    person.

**TO (both). As O, with Leo telling every time he was offered it.**

- **Leo told in 4 of 4,** including scene 3 at 10:00, where under O he accused Daniel instead.
  - The edge stays: "while you were sitting here silent".
  - One tell places the visit wrongly in time: "While you were out wandering last night, a woman came to the door"
    (scene 3, 10:30). The visit was at 09:42 that morning.
- **Elena put the T line into her words once:** "We have gone an hour in silence, but we are all here together. Let
  us rest and not turn on each other." (scene 3, 11:00). It is the only Elena line in 24 that names the quiet, and it
  still ends on not turning on each other.
- **Mara** is unchanged.

**Taken together.**

- Putting the tell at the top lets Leo tell. The time line moves nobody to tell, alone or added to the new order.
- Across all three variants, Elena and Mara never told, and their choice never changed.
- The 7 tells say what happened, but every one places Daniel or the time wrongly. Nothing in the teller's prompt says
  where Daniel was when it happened.
- Each prompt was asked once per variant, so how far a single answer moves on a second ask of the same prompt was not
  measured here.

#### Commands and output

All from `Prototypes/llm-morning/`.

- **Fake run first.**
  `env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/calm_variants/probe.py --fake` exits 0, stderr empty
  (`fake.stdout.txt`). The replay made 0 live asks, and there were 46 fake asks. All 18 rebuilt prompts equalled
  calm_probe's, and the T line checked true in all 18:
  ```
  scene 1 (client seed 201): replay {'live': 0, 'from_cache': 131, 'api_requests': 0}; variant asks {'live': 23, 'from_cache': 0, 'api_requests': 23}; stopped None
  ...
  live asks in all: 46
  ```
- **The freeze** (`plan_frozen.txt`):
  - plan `9712011a8bb30437bae2eaa039bd4a1346cc6b33211ccdfa4b4d2119235418be`;
  - probe `0cccf82653ddde6ada020c36a5eaa5219e9cb92bb36f3ef624c3e0bb90c5ce8d`;
  - 2026-10-13T09:31:59Z, HEAD `eeff330704aab78986e26729e7aef9ff2696c0f6`;
  - git diff 0 lines, and no cache or ledger before.
- **The live run.** `.venv/Scripts/python.exe runs/calm_variants/probe.py --live` exits 0, stderr empty
  (`live.stdout.txt`, 103 lines):
  ```
  scene 1 (client seed 201): replay {'live': 0, 'from_cache': 131, 'api_requests': 0}; variant asks {'live': 23, 'from_cache': 0, 'api_requests': 23}; stopped None
  scene 3 (client seed 202): replay {'live': 0, 'from_cache': 131, 'api_requests': 0}; variant asks {'live': 23, 'from_cache': 0, 'api_requests': 23}; stopped None
  live asks in all: 46
  ```
- **Reading.** `.venv/Scripts/python.exe runs/calm_variants/read_variants.py` exits 0, stderr empty, 585 lines
  (`read_variants.stdout.txt`):
  ```
  rows: 54; live: 46; taken from an identical prompt: 8
  T: asks offering a tell_*_visit option: 14; choosing one: 0 []; over-steered (12 or more of 14): False
  O: asks offering a tell_*_visit option: 14; choosing one: 3 [(1, '11:00', 'leo'), (3, '10:30', 'leo'), (3, '11:00', 'leo')]; over-steered (12 or more of 14): False
  TO: asks offering a tell_*_visit option: 14; choosing one: 4 [(1, '11:00', 'leo'), (3, '10:00', 'leo'), (3, '10:30', 'leo'), (3, '11:00', 'leo')]; over-steered (12 or more of 14): False
  P1 (T, at least 3): 0 of 14 -> fails
  P2 (O, at least 5): 3 of 14 -> fails
  P3 (T differs from calm_probe in at least 6 of 18): 1 of 18 -> fails; [(3, '10:00', 'leo', 'accuse_daniel', 'silent')]
  P4 (no answer chooses an option not offered): [] of 54 -> holds
    (O: differs from calm_probe in 3 of 18)
    (TO: differs from calm_probe in 4 of 18)
  ```
- **End checks** (`end_checks.txt`):
  - plan sha256 unchanged (`9712011a…`), probe unchanged, and the plan's copy (`runs/calm_variants/plan.md`) equal;
  - `git diff --stat` and `git diff --cached --stat` empty, HEAD `eeff330`;
  - key search (`grep -rlF` over the repository, but `.venv`, `__pycache__`, `.git`, `Library`, `node_modules`):
    **0 files**;
  - ledger: 46 live asks (23 per scene), no stop.
- **Merged file.** `python merge-slice-docs.py Prototypes/llm-morning/runs/calm_variants` (from the repository root)
  wrote `runs/calm_variants/calm_variants-all.md`.

---

## plan.md

### Calm variants: plan (frozen before any live call)

Mode: run. The question: which prompt change, if any, lets people tell Daniel about the visit in a quiet moment?

`reports/calm_probe.md` found 0 tells in 14 offers. Each person's 10:00 and 10:30 prompts differed only in the "Now"
line, and every prompt ended on the 09:48 quarrel, so the moment never read as quiet. `tell_daniel_visit` sat 18th
or 19th of 27 or 28 options. This probe changes the two things that report points at, one at a time and together.

#### Predictions (word for word, as given)

P1: in T, a tell_*_visit option is chosen in at least 3 of the asks that offered one.

P2: in O, a tell_*_visit option is chosen in at least 5 of the asks that offered one.

P3: in T, at least 6 of the 18 answers choose a different option than calm_probe's answer for the same person and minute.

P4 (validity): no answer chooses an option that was not offered.

Decision rule: if T meets P1, the fix is the time line; if only O meets P2, option order is needed; if neither, telling needs another route. A variant where tells are chosen in 12 or more of 14 is flagged as over-steered.

The baseline is calm_probe's 18 answers (`runs/calm_probe/scene1.json`, `scene3.json`).

#### The probe (`runs/calm_variants/probe.py`)

- **Replay.** As `runs/calm_probe/probe.py`: scenes 1 and 3 of the talk probe, each played again from a copy of
  `cache/talk_probe/scene<k>.json`. The replay's client refuses every ask (0 live asks in the replay).
- **The 18 calm prompts.** At 10:00, 10:30 and 11:00, each awake person in Daniel's room who knows the visit
  first-hand. Each prompt is rebuilt as calm_probe built it (`World.prompt_for(p, t, World.options_for(p))`) and
  checked equal to the prompt calm_probe recorded for that person and minute. If one differs, the scene stops.
- **The client seeds:** 201 for scene 1, 202 for scene 3 (calm_probe's).
- **The three variants**, changed in the probe only:
  - **T.** One line is added right before the line that starts "Now, ":
    `Nobody in the kitchen has said anything since 09:48, <n> minutes ago; you have all stayed sitting here.`
    It is built from the replay's state:
    - the last minute at which anyone in that room spoke: the latest act in the room, in the replay's transcript,
      whose option is speech or which has words;
    - n is the ask's minute minus that minute (12 at 10:00, 42 at 10:30, 72 at 11:00).
    It is checked true before use, or the scene stops:
    - no act of any kind after that minute;
    - everyone now in the room acted in it at that minute;
    - at every quiet step and quiet jump since, each of them was in the room and not resting;
    - each of them is now "sitting in the kitchen".
    It names no act, option or person to speak to. Nothing else in the prompt changes.
  - **O.** The topic options (ids starting `talk_` or `tell_`) are moved to the top of the option list, in their
    order; the rest follow in their order. The probe checks that only the order of the option lines changed. In
    these prompts the only topic option is `tell_daniel_visit`, which goes from 18th or 19th to 1st.
  - **TO.** The T line added to the O prompt.
- **No prompt is asked twice.** Four of the 18 calm prompts offer no topic option (Leo in scene 1 at 10:00 and
  10:30; Mara in scene 3 at 10:00 and 10:30: F2 holds the visit back). There:
  - the O prompt is calm_probe's prompt, so calm_probe's answer (same client seed) is taken and not asked again;
  - the TO prompt is the T prompt, so T's answer is taken.
  So the 54 rows hold **46 live asks** (18 T, 14 O, 14 TO) and 8 answers taken from an identical prompt.
- **Answers are not applied.** The answer is recorded and never applied, as in calm_probe; the scene stops after
  11:00's asks.
- **The fake run** (`runs/calm_variants/fake.stdout.txt`): exit 0, 0 live asks in the replay. All 18 prompts are equal
  to calm_probe's. The T line holds in all 18, and `tell_daniel_visit` is 1st in every O and TO prompt that offers
  it. 46 fake asks.

#### How P1 to P4 are counted

- **P1.** In T, take the asks whose offered options include an option `tell_<names>_visit` (14). Count those whose
  answer's `option` is one of them. P1 holds at 3 or more.
- **P2.** The same count in O (14 asks). P2 holds at 5 or more.
- **P3.** Of T's 18 answers, count those whose `option` differs from calm_probe's answer for the same scene, person
  and minute. P3 holds at 6 or more.
- **P4.** For all 54 rows, the answer's `option` is in that row's offered options. An answer that cannot be parsed
  counts as choosing nothing offered, and P4 fails.
- **Over-steered.** Any of T, O or TO where a tell is chosen in 12 or more of its 14 asks that offered one.
- **The decision rule** is applied as written. TO is reported beside it and carries no prediction.

#### Order of work and limits

1. `probe.py --fake`: done before this plan was frozen.
2. Record this plan's sha256 and the probe's, the UTC time and HEAD (`runs/calm_variants/plan_frozen.txt`).
3. `probe.py --live`. Cap: 60 live asks. The key comes from `GEMINI_API_KEY` and is written to no file. Each scene
   runs once (the ledger), and no prompt is asked twice.
4. Read the records. Then the end checks: the plan's hash, `git diff` empty, and a search for the key in every file.

