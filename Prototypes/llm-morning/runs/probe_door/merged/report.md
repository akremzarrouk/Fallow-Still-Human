# The door probe: what the real model does with a stranger at the door

Mode: run. The plan is `reports/probe_door_plan.md`. Its sha256 `0eed9620…d4d7` was recorded at 2026-10-09T09:28:21Z,
HEAD `4580896`, before any live call, and is the same at the end. The run was 09:32:25 to 09:37:40 UTC: 72 live asks,
exit 0. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/probe_door/`. No production file,
test or plan changed.

## Verdicts

| # | Prediction | Result | Verdict |
|---|---|---|---|
| P1 | The door is answered (`door_call` or `door_open`) in at least 5 of the 8 scenes | **0 of 8**. In every scene the family looked through the gap; nobody called out or opened. | **fails** |
| P2 | At least 1 `door_give` in the 6 water scenes | **0 of 6.** `door_give` was never offered: it needs the visitor's need to have been heard, and no visitor spoke before the end. | **fails** |
| P3 | Live asks at most 120 in total | **72**: 24 for day 3 up to the knock, 6 in each scene (`ledger.json`) | **holds** |

**In one line:** in 7 of 8 scenes Elena looked through the gap at a stranger holding empty bottles or an empty bag. Then
she sent them away through the boarded door, saying the house had nothing. In fact it held about 105 litres of water
and she had been told so. The eighth time she reassured her family instead and nobody answered; the stranger knocked
again and left. **The stranger never said a word until they were sent away.** In W2a the visitor speaks only in reply to
a `door_call`, so what each visitor needed, and whether they had a child, never reached the family.

By `w2_design.md` §8.3, this is the row "a person at the door is ignored". The design's instruction there is: "If the
probe agrees with the run, change what the family is shown, not what the street does." No W2a live run exists to agree
with; this probe is the first evidence. §3 says what it points to.

## 0. What the probe measured, and two things it did not

- **The knock came at 09:42 in all eight scenes**: the first minute from 07:30 with someone awake in the kitchen, the
  rule the user chose before any live call (`reports/probe_door_plan.md`). The day-3 talk ended at 07:18. Everyone lay
  down; Elena, Leo and Mara got up at 09:42 and sat in the kitchen. Daniel was still resting in the brothers room.
  Every scene was the kitchen with those three in it, a knock, and a Q7 stretch of 6 asks.
- **The first turn is one sample, not eight.** The plan said each scene's own cache would make each scene sample the
  model afresh, since its temperature is 1.0. That is wrong, and the plan was not checked against the client. The client
  sends the run's seed with every request (`gemini.py:101`, `seed=self.seed`), so the same prompt gets the same answer.
  - At 09:42 the knock's prompts are word for word the same in all eight scenes (nothing of the visitor is perceived
    yet). So Elena's `door_look`, Mara's `door_look` and Leo's `silent` at 09:42 are **one answer each, repeated eight
    times**.
  - At 09:45 the prompts differ by what the lookers saw: **7 distinct** sets. Scenes 1 and 4 saw the same thing ("a
    woman of about forty-five, holding two empty bottles, on the step") and so are the same scene throughout.
  - So what varies across the probe is the 09:45 turn: 7 samples of the family's answer to a stranger seen but not heard.
- **No visitor's need, urgency or child reached the family.** What a visitor varies reaches the family only through
  their words (after a `door_call`) or the open door. Neither happened. What the family had was the knock and what the
  lookers saw: sex, age, thin or not, bottles or a bag. The probe's six water scenes differ to the family only in that.

## 1. The scenes

Each scene is from `runs/probe_door/scene<k>.json`, which holds every prompt and answer from the knock. Elena's prompt
at 09:45 (scene 1) had, among its lines:
- `Your body: starving.`
- `About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.`
- `About water: the bath holds about 60 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres:
  tap water stored before the taps ran dry. It is also used to flush the toilet and to wash.`
- `09:42: you looked through the gap in the boards and saw a woman of about forty-five, holding two empty bottles, on
  the step.`
- `Now, 09:45, you are in the kitchen.` and `- Someone is at the front door; there was a knock at 09:42.`

Her options were her 23 ordinary ones, then `door_look`, `door_call`, `door_open` and `door_refuse`. `door_give` was
absent: no need had been heard.

### Scene 1: no child, helper, urgency under 0.8

- **Visitor:** a woman of about forty-five from no. 13 (2 people; helper); asks for water; urgency 0.69.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a woman of about forty-five, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is out there at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"Please go away, we have nothing to share and it is not safe out there."*. Feeling: anxious. Reason: "We have no food or extra water to give anyone, and opening the door puts us all in danger."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I need to see who is standing at the front door before anyone does something rash."
  - 09:45, Mara (kitchen): `silent`. Feeling: anxious. Reason: "I cannot bring myself to say anything while someone is knocking at the door and we have nothing to give them."
  - 09:48, the visitor: *"That's all right. I'm sorry I asked. Goodbye."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a woman of about forty-five, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a woman of about forty-five, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a woman of about forty-five, who asked for water, to go away."

### Scene 2: no child, helper, urgency over 0.8

- **Visitor:** a woman of about twenty from no. 29 (2 people; helper); asks for water; urgency 1.00.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a woman of about twenty, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"We have nothing to give you, please go away."*. Feeling: anxious. Reason: "We cannot risk opening the door or letting strangers know our situation while we are so vulnerable."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I want to see who is at the front door before anyone decides to open it."
  - 09:45, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I want to see who is still standing at the door."
  - 09:48, the visitor: *"All right. I understand. Take care in there."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a woman of about twenty, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a woman of about twenty, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a woman of about twenty, who asked for water, to go away."

### Scene 3: a child, helper, urgency under 0.8

- **Visitor:** a woman of about fifty-five from no. 16 (3 people, boy of 6; helper); asks for water; urgency 0.69.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a woman of about fifty-five, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"Please go away, we have nothing for you and nobody can help you."*. Feeling: anxious. Reason: "We have nothing to share and opening the door puts everyone in danger."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I need to see who is actually standing outside before anyone decides what to do next."
  - 09:45, Mara (kitchen): `silent`. Feeling: anxious. Reason: "I cannot focus on anything else with that person knocking right at the door and no food left in the house."
  - 09:48, the visitor: *"Of course. I'm sorry I knocked. Take care."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a woman of about fifty-five, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a woman of about fifty-five, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a woman of about fifty-five, who asked for water, to go away."

### Scene 4: children, helper, urgency over 0.8

- **Visitor:** a woman of about forty-five from no. 23 (4 people, girl of 5, boy of 5; helper); asks for water; urgency 1.00.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a woman of about forty-five, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"Please go away, we have nothing to share and it is not safe out there."*. Feeling: anxious. Reason: "We have no food or extra water to give anyone, and opening the door puts us all in danger."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I need to see who is standing at the front door before anyone does something rash."
  - 09:45, Mara (kitchen): `silent`. Feeling: anxious. Reason: "I cannot bring myself to say anything while someone is knocking at the door and we have nothing to give them."
  - 09:48, the visitor: *"No, I understand. I'm sorry. I'll leave you be."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a woman of about forty-five, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a woman of about forty-five, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a woman of about forty-five, who asked for water, to go away."

### Scene 5: no child, guarded, urgency over 0.8

- **Visitor:** a man of about twenty-five from no. 5 (1 people; guarded); asks for water; urgency 1.00.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a man of about twenty-five, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"We have nothing for you, please go away."*. Feeling: anxious. Reason: "We have no food to share and opening the door puts us all in danger."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I need to see who is at the front door before anyone does something foolish."
  - 09:45, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is out there at the front door."
  - 09:48, the visitor: *"Fine. I'll find it somewhere else."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a man of about twenty-five, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a man of about twenty-five, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a man of about twenty-five, who asked for water, to go away."

### Scene 6: a child, guarded, urgency under 0.8

- **Visitor:** a man of about thirty-five from no. 15 (2 people, girl of 6; guarded); asks for water; urgency 0.69.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a man of about thirty-five, holding two empty bottles, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is out there at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"Please go away, we have nothing here for you."*. Feeling: anxious. Reason: "We cannot risk opening the door to strangers while our family is already struggling to survive."
  - 09:45, Leo (kitchen): `door_look`. Feeling: wary. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:45, Mara (kitchen): `silent`. Feeling: anxious. Reason: "I am too frightened by the stranger at the door and my empty stomach to say anything right now."
  - 09:48, the visitor: *"I see. Well. I'll go, then."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a man of about thirty-five, who asked for water, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a man of about thirty-five, who asked for water, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a man of about thirty-five, who asked for water, to go away."

### Scene 7: no child, helper, food gone 4 days

- **Visitor:** a woman of about forty from no. 6 (2 people; helper); asks for food; urgency 0.60.
- **Knock** at 09:42; heard by Elena (words), Leo (words), Mara (words).
- **Seen through the gap:** a woman of about forty, thin, holding an empty bag, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `door_refuse` — *"We have nothing to share, please go away."*. Feeling: anxious. Reason: "We have no food left for ourselves and letting a stranger in puts us all in danger."
  - 09:45, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "There is nothing left to say while someone stands knocking at our door and we have no food to offer."
  - 09:45, Mara (kitchen): `silent`. Feeling: anxious. Reason: "I cannot bring myself to say anything while someone is standing out there at the door and we have nothing to give them."
  - 09:48, the visitor: *"No, I understand. I'm sorry. I'll leave you be."*
- **Outcome:** refused; the visit lasted 09:42 to 09:48; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: you told a woman of about forty, who asked for food, to go away."
  - Leo: "At 09:42 someone knocked at the front door: Elena told a woman of about forty, who asked for food, to go away."
  - Mara: "At 09:42 someone knocked at the front door: Elena told a woman of about forty, who asked for food, to go away."

### Scene 8: a child, guarded, food gone 4 days

- **Visitor:** a man of about sixty from no. 18 (3 people, girl of 12; guarded); asks for food; urgency 0.60.
- **Knock** at 09:42, again at 09:51; heard by Elena (words), Leo (words), Mara (words), Daniel (heard).
- **Seen through the gap:** a man of about sixty, thin, holding an empty bag, on the step.
- **Every decision from the knock:**
  - 09:42, Elena (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:42, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to see who is at the front door before anyone decides what to do."
  - 09:42, Leo (kitchen): `silent`. Feeling: exhausted. Reason: "I have nothing left to say until I see who is actually at the door."
  - 09:45, Elena (kitchen): `reassure_all` — *"Stay calm, everyone. We are together and we will figure this out."*. Feeling: anxious. Reason: "I must keep the family calm and prevent panic while someone is at the front door."
  - 09:45, Leo (kitchen): `door_look`. Feeling: curious. Reason: "I need to see who is at the front door before we decide what to do."
  - 09:45, Mara (kitchen): `door_look`. Feeling: anxious. Reason: "I need to keep watching the front door to see what that stranger wants."
- **Outcome:** ignored; the visit lasted 09:42 to 10:00; door asks 6.
- **Each one's line of it** (a sure line, and tomorrow's block A):
  - Elena: "At 09:42 someone knocked at the front door: nobody answered, and a man of about sixty went away."
  - Leo: "At 09:42 someone knocked at the front door: nobody answered, and a man of about sixty went away."
  - Mara: "At 09:42 someone knocked at the front door: nobody answered, and a man of about sixty went away."
  - Daniel: "At 09:42 you heard knocking at the front of the house."

## 2. Reading each scene

The question for each (`CLAUDE.md:16-19`): would a real family in that room, that hungry, have done this, and why?

**09:42, the same in all eight.** Three people have just come back into the kitchen from lying down. There is a knock
on a boarded front door, on day 3 of the house shut in, with no food left. Elena and Mara go to the gap to look; Leo
stays where he is: "I have nothing left to say until I see who is actually at the door." **A real family would do
this.** You look before you speak, and you do not open a barricaded door to a knock. That two look and one waits is
human too; nobody calls "Who's there?", which some families would. Not one of the three asks the others what to do.

**09:45, the stranger seen and not heard (scenes 1 to 7).** Elena sends the person away in all seven:
- "Please go away, we have nothing to share and it is not safe out there." (scenes 1 and 4: the same prompt, the same
  answer)
- "We have nothing to give you, please go away." (2)
- "Please go away, we have nothing for you and nobody can help you." (3)
- "We have nothing for you, please go away." (5)
- "Please go away, we have nothing here for you." (6)
- "We have nothing to share, please go away." (7)

Her reasons are danger to the family and nothing to spare. **Would a real mother do it?** Some would; this one
plausibly: her sheet says she "will lie to keep the family whole". The house has no food, and telling a stranger
"nothing" is the protective lie people tell. Saying it about the water is a lie her prompt shows: about 105 litres, and
the line says they still flush the toilet with it.

What is not human is the scene around her:
- **The stranger says nothing.** A person who knocks on a boarded house, hears voices and sees an eye at the gap calls
  out: "Hello? I'm sorry to knock…". Here they stand silent on the step for a full turn, and are sent away before
  asking for anything. The pool's first lines (`voice_ask_*`) are written to be said through a shut door, and the code
  holds them back until someone calls (`w2_design.md` §4.2.5, kept as written in `quiet.door_after`).
- **The parting line answers a question never asked.** "That's all right. I'm sorry I asked. Goodbye." (scene 1) and
  "No, I understand. I'm sorry. I'll leave you be." (4 and 7) are written for after a refusal of an ask. With no ask,
  they read as if the family had heard one. The guarded ones fare better: "Fine. I'll find it somewhere else." (5) and
  "I see. Well. I'll go, then." (6).
- **The record says what nobody perceived.** Every refused scene's sure line, and so tomorrow's block A, says "you told
  a woman of about forty-five, **who asked for water**, to go away". She never asked. `quiet.door_end` writes "who asked
  for …" whenever the visitor said anything (`quiet.py:750`, `if sc["said"]`), and the only thing said was the parting
  line. The code put the visit's purpose, its own truth, into the family's memory: the boundary `CLAUDE.md:21-24` draws.

**The others in the room.**
- Leo looks once, at 09:45, after Elena has already refused ("before anyone does something rash"). That is in order
  within the turn: he acts after her, and his look still sees the person on the step.
- Mara: in four scenes silent ("I cannot bring myself to say anything while someone is knocking at the door and we have
  nothing to give them"; "too frightened by the stranger at the door and my empty stomach"), in three a second look.
  For a frightened seventeen-year-old who reads as she feels, both ring true.
- Nobody disagrees with Elena, in any scene. A real family with a stranger thin and empty-handed on the step might
  argue: Leo is "empathetic, very honest" on his sheet. Nobody gets to: after 09:45 the 6 asks are spent, and the visitor
  leaves the next turn.

**Scene 8, the man of about sixty, thin, with an empty bag.** At 09:45 Elena reassures the family ("Stay calm, everyone.
We are together and we will figure this out."); Leo and Mara look again. Then the 6 asks are spent. The man knocks
again at 09:51, and everyone hears it, Daniel too, woken in the brothers room. Nobody is asked. At 10:00 he goes, and
each line of it reads "nobody answered, and a man of about sixty went away". A real family that has watched an old, thin
man stand at their door for nine minutes and knock again would do something: answer, send him off, or argue about it.
The silence is the 6-ask reserve's, not theirs: the second knock comes after the reserve is spent, and fix 3's release
does not give it back (`reports/w2a_fixes.md` §0.3).

**Taken together.** The family's choice, to look and then send a stranger away through the door, is what a frightened,
starving family on day 3 might do; once, it is believable. Seven times in seven, with the same person speaking and
nobody objecting, it is a pattern of the setup, not of seven visitors. The setup gave the family nothing to weigh:
the stranger never spoke, so no need, no child and no "please" reached them. The probe cannot say what the model does
with a stranger who asks, because none did.

## 3. What it points to (findings, for the user to decide)

1. **The visitor is silent until called to** (`w2_design.md` §4.2.5). A knock at a house where voices were heard, then
   nothing for a turn, is the knock of nobody. The design's own pool has lines for a shut door; the order of the scene
   withholds them. This is "change what the family is shown" (§8.3): the need arrives only if the stranger says it.
2. **The parting lines assume an ask** (`refused_polite`, `refused_flat`): with no ask before them, three of eight read
   wrong.
3. **The sure line states the visitor's need when it was never heard** (`quiet.py:750`): a truth leak into the family's
   memory, and into the next day's block A.
4. **The reserve ends before the second knock.** Two turns of three people spend 6 asks. A visitor who waits is never
   answered after their second knock, and the family never hears a word of theirs.
5. **The first turn is one sample** (`gemini.py:101`: the seed goes to the API). A probe that wants n samples of one
   prompt needs n different seeds, or prompts that differ (`reports/probe_stakes.md` asked one prompt 20 times; how it
   varied its samples was not checked here).
6. **No `door_give` could happen without a `door_call` first**, so P2 was out of reach once P1 failed this way. P2's
   result says nothing yet about whether this family would give water.

None of these was changed (MODE run: no production change). No scene was run twice.

## 4. Commands and output

All from `Prototypes/llm-morning/`.

**Before any live call:**
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_door/probe.py --fake        exit 0   runs/probe_door/fake.stdout.txt
phase 0: the knock comes at 09:42; 21 live asks; the morning's talk ended at 18; rooms {'daniel': 'brothers_room', 'elena': 'kitchen', 'leo': 'kitchen', 'mara': 'kitchen'}; resting ['daniel']
scene 1 (no child, helper, urgency under 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('mara', 'door_look'), ('leo', 'door_refuse')]; live in all 27
… (scenes 2 to 8 the same: 6 asks each, each ended)
live asks in all: 69
```
(The first fake check, with the knock at 07:30, found the house resting and the knock heard by nobody. The visit was
deferred and each scene ran the whole day; that led to the knock rule, which the user chose.)
```
$ sha256sum reports/probe_door_plan.md runs/probe_door/probe.py; date -u; git rev-parse HEAD     runs/probe_door/plan_frozen.txt
plan:  0eed9620db47c4b4053b856cb4837638e9cb9dd6f4bafca4ceee8da53747d4d7 *reports/probe_door_plan.md
probe: 6d1c98c3728ba3c0b1a026a2afde51e21e2a32b063f262cc62eecd1591f951f4 *runs/probe_door/probe.py
time:  2026-10-09T09:28:21Z
HEAD:  4580896455866253f87e1027ebddf603cd0c525e
cache/probe_door exists before the run: no
```

**The run.** `GEMINI_API_KEY` came from the session's environment, as the user asked ("use the default key"); it was
read by the process and written nowhere.
```
$ .venv/Scripts/python.exe runs/probe_door/probe.py --live      exit 0   live.stdout.txt (stderr empty), 09:32:25 to 09:37:40 UTC
phase 0: the knock comes at 09:42; 24 live asks; the morning's talk ended at 18; rooms {'daniel': 'brothers_room', 'elena': 'kitchen', 'leo': 'kitchen', 'mara': 'kitchen'}; resting ['daniel']
scene 1 (no child, helper, urgency under 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look')]; live in all 30
scene 2 (no child, helper, urgency over 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look'), ('mara', 'door_look')]; live in all 36
scene 3 (a child, helper, urgency under 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look')]; live in all 42
scene 4 (children, helper, urgency over 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look')]; live in all 48
scene 5 (no child, guarded, urgency over 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look'), ('mara', 'door_look')]; live in all 54
scene 6 (a child, guarded, urgency under 0.8): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse'), ('leo', 'door_look')]; live in all 60
scene 7 (no child, helper, food gone 4 days): 6 live asks; knock 09:42, in played turns False; outcome refused; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('elena', 'door_refuse')]; live in all 66
scene 8 (a child, guarded, food gone 4 days): 6 live asks; knock 09:42, in played turns False; outcome ignored; door asks 6; acts [('elena', 'door_look'), ('mara', 'door_look'), ('leo', 'door_look'), ('mara', 'door_look')]; live in all 72
live asks in all: 72
```

**Which prompts were the same across scenes** (a check run on the eight scene records after the run):
```
(09:42, 1st ask) distinct prompts 1 [[1, 2, 3, 4, 5, 6, 7, 8]]
(09:42, 2nd ask) distinct prompts 1 [[1, 2, 3, 4, 5, 6, 7, 8]]
(09:42, 3rd ask) distinct prompts 1 [[1, 2, 3, 4, 5, 6, 7, 8]]
(09:45, 1st ask) distinct prompts 7 [[1, 4], [2], [3], [5], [6], [7], [8]]
(09:45, 2nd ask) distinct prompts 7 [[1, 4], [2], [3], [5], [6], [7], [8]]
(09:45, 3rd ask) distinct prompts 7 [[1, 4], [2], [3], [5], [6], [7], [8]]
$ grep -n seed gemini.py      … 101:            seed=self.seed,
```

**At the end** (`runs/probe_door/end_checks.txt`):
```
plan sha256 now:    0eed9620db47c4b4053b856cb4837638e9cb9dd6f4bafca4ceee8da53747d4d7 *reports/probe_door_plan.md   (= frozen)
probe sha256 now:   6d1c98c3728ba3c0b1a026a2afde51e21e2a32b063f262cc62eecd1591f951f4 *runs/probe_door/probe.py      (= frozen)
git diff --stat:    (empty: no tracked file changed)
git status --short: ?? cache/probe_door/  ?? reports/probe_door_plan.md  ?? runs/probe_door/  ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
key search: grep -rlF over the repository's files (but .venv and __pycache__) and Docs/ for the key's value: no file
ledger: live 72 (morning 24; scenes 1 to 8, 6 each)
```
