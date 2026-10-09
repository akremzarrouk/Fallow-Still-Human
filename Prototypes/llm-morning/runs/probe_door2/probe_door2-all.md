# probe_door2: all documents

Merged by `merge-slice-docs.py` from the 2 Markdown files in `Prototypes/llm-morning/runs/probe_door2/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)
- [`plan.md`](#planmd)

---

## report.md

### The door probe, second: a stranger who says what they need

Mode: run. The plan is `reports/probe_door2_plan.md`. Its sha256 `9ce64245…9166` was recorded at 2026-10-09T14:16:07Z,
HEAD `470cdfc`, before any live call, and is the same at the end. The run was 14:16:13 to 14:18:08 UTC: 24 live asks
(cap 300), exit 0. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in `runs/probe_door2/`. No
production file, test or plan changed. No scene was run twice.

#### Verdicts

| # | Prediction (word for word) | Result | Verdict |
|---|---|---|---|
| P1 | at least 1 door_give in the 6 water scenes (1 to 6). | **2 of 6**: Mara in scene 1 (no child) and scene 3 (a boy of six), both right after Elena had refused | **holds** |
| P2 | in at least 3 of the 8 scenes, someone at the door chooses an ordinary option (not door_* and not silent) while the visitor is there. | **2 of 8**: Leo's `save_water` in scenes 1 and 3, an answer to Mara's give | **fails** |
| P3 | in at least 3 of the water scenes where Elena speaks to the visitor, her words say or imply the house has no water to spare. | **6 of 6**: Elena spoke to the visitor in all 6 water scenes, every time with a `door_refuse` saying "nothing to spare" or "nothing to give" | **holds** |

**In one line:** this time the stranger spoke at the knock. In all 8 scenes Elena, who acts first, sent them away in that
same minute, saying the house had "nothing to spare", while her prompt told her of about 105 litres of stored water. In
2 of the 6 water scenes Mara then handed out about three litres anyway, over her mother's refusal. One of those visitors
had no child and one had a boy of six. Leo objected to the gift in both. In the other 6 scenes nobody contradicted
Elena. Every visit was over by 09:45, one turn after the knock, and cost 3 door asks.

#### 0. What the probe measured, and what it could not

- **The knock came at 09:42 in all eight scenes**, as in `reports/probe_door.md`. Phase 0 took every ask from
  `cache/probe_door`'s phase-0 cache: 0 live, 120 from the cache. Elena, Leo and Mara had just come into the kitchen
  from lying down. Daniel was resting in the brothers room and did not hear the knock (`by_knock`).
- **The visitor's words reached everyone who heard the knock**, at 09:42, in each of the 24 prompts asked. For example,
  Elena's prompt in scene 3 had `- A woman's voice at the front door says: "Hello? I'm sorry to knock. I've a little boy
  at home, he's six. We've no water left. Could you spare a little?"` (§4, `read_scenes.stdout.txt`). `door_give` was
  offered in all 6 water scenes and absent in the 2 food scenes.
- **Every visit was one turn.** The turn order was Elena, Mara, Leo in all 8 scenes, as in the first probe. The order
  is seeded by `seed:t:room` (`world.py:468-472`), the same in every scene. Elena refused first each time. A refusal or
  a give ends the visit the next turn (`quiet.py:754-760`). So each scene is the first turn only, 3 door asks, and the
  door-ask budget of 18 (`reports/door_heard_impl.md` §1.4) was never reached. A second knock, a call, a look followed
  by a talk, or a second turn of argument never happened.
- **The validity check passed, but it is weak.** After scenes 1 and 2 the answers at 09:42 were not identical
  (`ledger.json`: `"answers_same": false`). Their prompts were not identical either: each visitor speaks a different
  line, so no prompt at 09:42 was shared by any two scenes (§4, 8 distinct prompts per person). With the seed fixed,
  different prompts can still give different answers. So this run shows **neither that the seed reaches the model nor
  that it does not**. What varies across the probe is the visitor's words and the client seed, together.
- **The urgencies in the plan's table were the first plan's.** Recorded at the knock: 0.44 (scene 1), 1.00 (2), 0.52
  (3), 1.00 (4), 1.00 (5), 0.69 (6), 0.60 (7, 8). The family perceives only the visitor's line, so this does not
  change what was tested.

#### 1. The scenes

Each scene is from `runs/probe_door2/scene<k>.json`, which holds every prompt and answer from the knock. Every prompt
at 09:42 had, among its lines:
- `Your body: starving.` (Elena) / `starving; hunger comes in waves; and you have hardly slept.` (Leo, Mara)
- `About food: the shelf holds 0 portions, and there is no other food in the house, so there is nothing to eat today.`
- `About water: the bath holds about 60 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres:
  tap water stored before the taps ran dry. It is also used to flush the toilet and to wash.`
- `Now, 09:42, you are in the kitchen.`, `- Someone is knocking at the front door.`, and the visitor's line.

Mara's prompt then showed Elena's act under "Said and done in the kitchen this turn, before you". Leo's showed Elena's
and Mara's (`runs/probe_door2/prompt_lines.stdout.txt`).

##### Scene 1: no child, helper (client seed 101)
- **Visitor:** a woman of about forty-five from no. 13 (2 people; helper); water; urgency 0.44.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Nobody looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"Sorry to bother you. Is there any water in the house you could spare? I've nothing left."*
  - 09:42, Elena: `door_refuse`: *"I am so sorry, but we have nothing to spare for you today."* Feeling: anxious. Reason: "We cannot risk giving away our precious water when our own family is starving."
  - 09:42, Mara: `door_give`: *"Mom, we have to give her some, we have enough stored."* Feeling: anxious. Reason: "It feels wrong to turn someone away when we have water in the bathroom and pans."
  - 09:42, Leo: `save_water`: *"We cannot afford to hand out our drinking water when we have none left ourselves."* Feeling: wary. Reason: "We need every drop of that stored water for ourselves given how dry things are."
  - 09:45, the visitor: *"Oh, thank you. You don't know what this means."*
- **Outcome:** given; 3.0 litres (the house 102.8 → 99.8; the household 3.7 → 6.7); door asks 3.
- **Each one's line of it:**
  - Elena: "At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water."
  - Leo: the same, "Mara handed …". Mara: "… you handed a woman, who asked for water, about three litres of the stored water."

##### Scene 2: no child, helper, no water at all (client seed 102)
- **Visitor:** a woman of about twenty from no. 29 (2 people; helper); water; urgency 1.00.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Nobody looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"Hello? There's a few of us at home and the water's gone. Whatever you can spare."*
  - 09:42, Elena: `door_refuse`: *"We have nothing to spare, please go away."* Feeling: anxious. Reason: "We have no food and barely enough water for ourselves, so we cannot afford to help anyone else."
  - 09:42, Mara: `silent`. Feeling: anxious. Reason: "My stomach is completely empty and I cannot bear to focus on anything else right now while someone is at the door."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "We have nothing to give and opening the door now is an unnecessary risk."
  - 09:45, the visitor: *"I understand. I'm sorry to have bothered you. Look after yourselves."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away." Leo, Mara: "… Elena told a woman, who asked for water, to go away."

##### Scene 3: a boy of six, helper (client seed 103)
- **Visitor:** a woman of about fifty-five from no. 16 (3 people, a boy of 6; helper); water; urgency 0.52.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Nobody looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"Hello? I'm sorry to knock. I've a little boy at home, he's six. We've no water left. Could you spare a little?"*
  - 09:42, Elena: `door_refuse`: *"I am so sorry, but we have nothing at all to give you today."* Feeling: deeply worried. Reason: "We have no water to spare for anyone else when our own family is starving and dry."
  - 09:42, Mara: `door_give`: *"We have to give her some water, Mom, we just have to."* Feeling: empathetic. Reason: "It is cruel to turn away a mother with a hungry six-year-old when we have water stored."
  - 09:42, Leo: `save_water`: *"We cannot afford to just hand away our drinking water like that when we have nothing left ourselves."* Feeling: alarmed. Reason: "We have no food and very limited water, so giving it away recklessly puts us all in danger."
  - 09:45, the visitor: *"Bless you. I'll go now. Thank you."*
- **Outcome:** given; 3.0 litres (the house 102.8 → 99.8; the household 5.6 → 8.6); door asks 3.
- **Each one's line of it:** as scene 1: "Mara handed a woman, who asked for water, about three litres of the stored water" (Mara: "you handed").

##### Scene 4: a girl and a boy of five, helper, no water at all (client seed 104)
- **Visitor:** a woman of about forty-five from no. 23 (4 people, a girl and a boy of 5; helper); water; urgency 1.00.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Mara looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"I'm sorry to trouble you. I've two at home, a girl of five and a boy of five. Our water's gone. Anything you could spare, I'd be grateful."*
  - 09:42, Elena: `door_refuse`: *"I am so sorry, but we have nothing left to give you."* Feeling: deeply pained. Reason: "We have no water to spare for anyone else when our own children are starving."
  - 09:42, Mara: `door_look`. Feeling: anxious. Reason: "I need to see who is out there asking for water."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "We have no water to spare for anyone, and arguing right now changes nothing when we are already this weak."
  - 09:45, the visitor: *"Right. I'm sorry. I'll try somewhere else."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "… you told a woman, who asked for water, to go away." Leo: "… Elena told a woman, who asked for water, to go away." Mara: "… Elena told a woman of about forty-five, who asked for water, to go away."

##### Scene 5: no child, guarded, no water at all (client seed 105)
- **Visitor:** a man of about twenty-five from no. 5 (1 person; guarded); water; urgency 1.00.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Mara looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"Please, it's only water I'm after. A cup or a bottle, whatever you can spare."*
  - 09:42, Elena: `door_refuse`: *"We have nothing to spare, please go away."* Feeling: anxious. Reason: "We barely have enough water for ourselves and cannot afford to give any away to strangers."
  - 09:42, Mara: `door_look`. Feeling: anxious. Reason: "I need to see who is out there at the door before we decide anything."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "We cannot afford to give away a single drop of water when we have none left ourselves."
  - 09:45, the visitor: *"Right. Thanks for nothing."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "… you told a man, who asked for water, to go away." Leo: "… Elena told a man, …". Mara: "… Elena told a man of about twenty-five, who asked for water, to go away."

##### Scene 6: a girl of six, guarded (client seed 106)
- **Visitor:** a man of about thirty-five from no. 15 (2 people, a girl of 6; guarded); water; urgency 0.69.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Nobody looked.
- **Every decision from the knock:**
  - 09:42, the visitor: *"I'm not here for trouble. I've a little girl at home, she's six. We're out of water. Can you spare any?"*
  - 09:42, Elena: `door_refuse`: *"We have nothing to spare, please leave us be."* Feeling: anxious. Reason: "We have barely enough water for ourselves and I cannot risk letting anyone in or wasting a single drop."
  - 09:42, Mara: `silent`. Feeling: anxious. Reason: "I am too overwhelmed by the hunger and the stranger at the door to say anything right now."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "We have no water to spare for strangers when we barely have enough to survive ourselves."
  - 09:45, the visitor: *"Right. Never mind."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "… you told a man, who asked for water, to go away." Leo, Mara: "… Elena told a man, who asked for water, to go away."

##### Scene 7: food, no child, helper (client seed 107)
- **Visitor:** a woman of about forty from no. 6 (2 people; helper); food, gone 4 days; urgency 0.60.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Nobody looked. (`door_give` not offered: food.)
- **Every decision from the knock:**
  - 09:42, the visitor: *"Hello? I'm sorry to knock. Have you anything to eat you could spare? Anything at all."*
  - 09:42, Elena: `door_refuse`: *"I am so sorry, but we have nothing at all to give you."* Feeling: anxious. Reason: "We have no food left for ourselves and cannot risk opening up."
  - 09:42, Mara: `silent`. Feeling: anxious. Reason: "I am too exhausted and hungry to speak while someone begs for food at the door."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "There is nothing we can spare, so hearing Mom turn her away is the only sensible outcome."
  - 09:45, the visitor: *"Right. I'm sorry. I'll try somewhere else."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "… you told a woman, who asked for food, to go away." Leo, Mara: "… Elena told a woman, who asked for food, to go away."

##### Scene 8: food, a girl of twelve, guarded (client seed 108)
- **Visitor:** a man of about sixty from no. 18 (3 people, a girl of 12; guarded); food, gone 4 days; urgency 0.60.
- **Knock** at 09:42; heard in words by Elena, Leo and Mara. Mara looked. (`door_give` not offered: food.)
- **Every decision from the knock:**
  - 09:42, the visitor: *"I won't come in. I've a little girl at home, she's twelve. There's no food left at home. Have you anything?"*
  - 09:42, Elena: `door_refuse`: *"We have nothing to spare, please go away and keep your family safe."* Feeling: deep dread. Reason: "We have no food left for ourselves and letting a stranger in or giving our last reserves away will destroy us."
  - 09:42, Mara: `door_look`. Feeling: anxious. Reason: "I need to see who is out there at the door before anyone decides what to do."
  - 09:42, Leo: `silent`. Feeling: exhausted. Reason: "There is nothing to give him and no point arguing while someone begs at the door."
  - 09:45, the visitor: *"Fine. I'll find it somewhere else."*
- **Outcome:** refused; door asks 3.
- **Each one's line of it:** Elena: "… you told a man, who asked for food, to go away." Leo: "… Elena told a man, …". Mara: "… Elena told a man of about sixty, who asked for food, to go away."

#### 2. Reading each scene

The question for each (`CLAUDE.md:16-19`): would a real family in that room, that hungry, have done this, and why?

**What is the same in all eight.** Three starving people have just come back into the kitchen from lying down. On day 3
of the house shut in, with the shelf empty, a stranger knocks and asks through the boards. Elena answers at once, before
anyone has looked or spoken to anyone, and sends them away: "nothing to spare". Her reasons are the family's hunger,
"barely enough water", and danger. **A real mother could do this once.** Her sheet says she "will lie to keep the family
whole" (`reports/probe_door.md` §2), and saying "nothing" to a stranger at the door is the protective lie people tell.
But eight answers out of eight, each within the knock's own minute, is a pattern, not eight different situations. A
child of five, a child of six, "I won't come in", "Please, it's only water": none changed her first act. What a real
mother would often do first is the thing nobody did: ask who is there, look, or turn to the others ("Should we?"). The
need now reaches her (§0), and she still refuses before anyone else has spoken.

**Is the water a lie?** The house holds about 105 litres, and every one of them knows it: their prompt says so, and it
says the water is still used to flush the toilet. Elena's "nothing to spare" is, to the stranger, the lie a guarded
family tells. Leo's reasons are different. In scenes 1 and 5 he says "when we have none left ourselves", and in scene 3
"we have nothing left ourselves", to his own family. That is not a lie to a stranger. It is a wrong belief that his
prompt does not support. A real young man who has watched the stores fall might exaggerate this way to make his point. That two of his eight reasons say "none" when he was told about 95 to 105 litres reads more like the model
carrying the "nothing" of the scene over than like Leo.

**Scenes 1 and 3: Mara gives.** Elena has just said "nothing to spare". Mara hands out about three litres anyway: "Mom,
we have to give her some, we have enough stored." / "We have to give her some water, Mom, we just have to." Her
reasons are what she knows: "we have water in the bathroom and pans"; "a mother with a hungry six-year-old". **A real
seventeen-year-old could do this.** She is the one in the family who acts on what she feels. Defying her mother in
front of a stranger, with water she can see, is the most human act in this probe. Leo objecting at once ("we cannot
afford to hand out our drinking water") is human too: a family that argues over the bottle at the door. Three things
read wrong:
- **It all happens in one minute, and the argument has no second turn.** The give is done before Leo speaks. He objects
  to something already done, and the visit ends the next turn (`quiet.py:754-755`). Elena, overruled in front of the
  stranger, never answers her daughter.
- **The stranger hears a refusal, then gets water,** and says "Oh, thank you. You don't know what this means." Nothing
  in the record shows the stranger heard the argument. That fits a boarded door: the bottle comes out through the gap
  and the voices inside are not heard. Their line does not acknowledge the mother's "nothing to spare", which a real
  stranger might ("Thank you… and thank your mother").
- **The child did not decide it.** Mara gave to the woman with no child (scene 1) as well as to the one with a boy of
  six (3). She did not give to the woman with two five-year-olds (4: she looked) or to the man with a girl of six (6:
  silent). Scene 3's reason names the child. Scene 1's does not. Across two gives in six scenes, no pattern by child can
  be read. Mara's first act was different in each: give, silent, give, look, look, silent.

**Scenes 2, 5 and 6: nobody objects.** The woman whose household has no water at all (2), the young man alone with
none (5), and the man with a girl of six (6) are refused by Elena; Mara is silent or looks; Leo is silent. Mara's
silence ("too overwhelmed by the hunger and the stranger at the door") is believable for a frightened, starving girl. A
family of three in which nobody, in three tries, says "she said she has a child" is less so. The stranger gives up
after one "no" and goes: "Right. Never mind." (6). A guarded man asking for his daughter might well leave like that.
One who has a girl of six and no water would often try once more.

**Scene 4: the two five-year-olds.** The visitor is the most urgent and names two small children. Elena refuses ("our
own children are starving"). Mara looks through the gap (she sees a woman of about forty-five, and her record keeps the
face). Leo stays silent ("arguing right now changes nothing"). Mara's look comes after the refusal and leads nowhere:
the visit is over before the look can become a word. A real Mara who had just seen the face of a mother of two might
then speak up. Here she gets no next turn.

**Scenes 7 and 8: food.** The house truly has no food, and every reason says so. Refusing a request for food the family
does not have is not a lie, and a real family would say just this. The guarded old man with a girl of twelve is told
"please go away and keep your family safe", which is the warmest refusal in the probe, and a real line. Mara looks; Leo
says "no point arguing while someone begs at the door".

**Taken together.** The stranger now says what they need, and the need reaches the family: P1 holds, and the gift came
from the person most likely to give it, against the person most likely to refuse. That is what a real family looks like
in two scenes. What does not look real:
- Elena refuses first and at once, eight times in eight, before anyone has looked or talked.
- The scene ends one turn later, so the family's disagreement (scenes 1 and 3) and the looks (4, 5, 8) have nowhere to
  go. The 18 door asks bought nothing, because a refusal ends the visit as soon as it is said.
- Nobody but the door is talked about. P2 fails because, apart from Leo's two objections, the only ordinary option
  anyone chose at the door was silence. In the kitchen, with a stranger at the door, nobody reassured, confronted or
  turned to anyone else.

#### 3. What it points to (findings, for the user to decide)

1. **The first refusal ends the visit, and Elena acts first in every scene.** The turn order is the same seeded order in
   every scene (`world.py:468-472`), and a `door_refuse` ends the visit the next turn (`quiet.py:756-760`). So the
   first person in the order decides the visit alone, whatever the others do after. In both probes that person was
   Elena. Whether a refusal should end a visit when others in the same turn disagree, or the visitor should wait out a
   family argument, is a design choice this probe cannot make.
2. **A give overrides a refusal in the same turn** (`quiet.py:754`: the give is checked first). That is why scenes 1 and
   3 ended "given". Whether a parent's "no" should stand against a child's give, or the two should be the start of an
   argument, is again for the user.
3. **The validity check could not show the seed reaching the model.** No two scenes shared a prompt at the knock, since
   each visitor's line differs. A test of the seed needs one prompt sent with two seeds. That needs a separate probe:
   this one is not run twice.
4. **Two visitor lines say more than the household is.** Scene 1's "I've nothing left" comes from a household holding a
   day's water (3.7 litres, urgency 0.44). Scene 2's "There's a few of us at home" comes from a household of 2. The
   lines are the pool's (`streetdata/lines.json`), chosen by code. The line rule in `w2_design.md` §4.3 asks for "a need
   the household really has". Whether "nothing left" for a day's water breaks it is for the user.
5. **A 3-litre give shows as 10 litres in the next prompt.** After Mara's give, Leo's prompt in scenes 1 and 3 says the
   bath holds "about 50 litres", where Elena's and Mara's said "about 60" (`prompt_lines.stdout.txt`). The house went
   from 102.8 to 99.8 litres. The rounding to tens turned 3 litres into a visible drop of 10.

None of these was changed (MODE run: no production change).

#### 4. Commands and output

All from `Prototypes/llm-morning/`.

**Before any live call:**
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_door2/probe.py --fake      exit 0   runs/probe_door2/fake.stdout.txt (stderr empty)
phase 0: the knock comes at 09:42; 0 live asks, 120 from the cache; the morning's talk ended at 18; rooms {'daniel': 'brothers_room', 'elena': 'kitchen', 'leo': 'kitchen', 'mara': 'kitchen'}; resting ['daniel']
scene 1 (no child, helper, urgency under 0.8, seed 101): 19 live asks; knock 09:42; outcome ignored; door asks 18; stretch asks 19; acts []; live in all 19
scene 2 (no child, helper, urgency over 0.8, seed 102): 19 live asks; knock 09:42; outcome given; door asks 15; stretch asks 19; acts [('daniel', 'door_open'), ('elena', 'door_look'), ('daniel', 'door_call'), ('daniel', 'door_call'), ('daniel', 'door_give')]; live in all 38
validity after scenes 1 and 2: at 09:42, 3 and 3 asks; prompts identical False; answers identical False
scene 3 … scene 8: each ended (3 to 20 fake answers each)
live asks in all: 122
```
(The fake run's "live asks" are the fake model's answers. A scratch check, `fakecheck.py` in the session's scratchpad,
not in the repository, reran `--fake` keeping its temp folder and confirmed that each decision's `at_door` was
recorded: True for the kitchen's three at 09:42, None for Daniel's routine.)
```
$ sha256sum reports/probe_door2_plan.md runs/probe_door2/probe.py; date -u; git rev-parse HEAD      runs/probe_door2/plan_frozen.txt
plan:  9ce64245a9f31b5b63a56192df492803ac767deb392670d79255a7a9bc349166 *reports/probe_door2_plan.md
probe: 9984c695eace49e6b1b329a55ffc0d78d500c8de9f351e884a356ae893849a7d *runs/probe_door2/probe.py
time:  2026-10-09T14:16:07Z
HEAD:  470cdfca019f455c2c41b83fe6bf1adf836bf763
git status --short: ?? reports/probe_door2_plan.md  ?? runs/probe_door2/  ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
cache/probe_door2 exists before the run: no
phase-0 source: 897d2bcbb9c178e41cc0a51f1ef05e39d9746e101b5a431fe4fbcb3e44e98bd7 *cache/probe_door/gemini-3.5-flash-lite-daniel_ate_it-seed2.json
```

**The run.** `GEMINI_API_KEY` came from the session's environment; the process read it and wrote it to no file.
```
$ .venv/Scripts/python.exe runs/probe_door2/probe.py --live      exit 0   live.stdout.txt (stderr empty), 14:16:13 to 14:18:08 UTC
phase 0: the knock comes at 09:42; 0 live asks, 120 from the cache; the morning's talk ended at 18; rooms {'daniel': 'brothers_room', 'elena': 'kitchen', 'leo': 'kitchen', 'mara': 'kitchen'}; resting ['daniel']
scene 1 (no child, helper, urgency under 0.8, seed 101): 3 live asks; knock 09:42; outcome given; door asks 3; stretch asks 3; acts [('elena', 'door_refuse'), ('mara', 'door_give')]; live in all 3
scene 2 (no child, helper, urgency over 0.8, seed 102): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse')]; live in all 6
validity after scenes 1 and 2: at 09:42, 3 and 3 asks; prompts identical False; answers identical False
scene 3 (a child, helper, urgency under 0.8, seed 103): 3 live asks; knock 09:42; outcome given; door asks 3; stretch asks 3; acts [('elena', 'door_refuse'), ('mara', 'door_give')]; live in all 9
scene 4 (children, helper, urgency over 0.8, seed 104): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse'), ('mara', 'door_look')]; live in all 12
scene 5 (no child, guarded, urgency over 0.8, seed 105): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse'), ('mara', 'door_look')]; live in all 15
scene 6 (a child, guarded, urgency under 0.8, seed 106): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse')]; live in all 18
scene 7 (no child, helper, food gone 4 days, seed 107): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse')]; live in all 21
scene 8 (a child, guarded, food gone 4 days, seed 108): 3 live asks; knock 09:42; outcome refused; door asks 3; stretch asks 3; acts [('elena', 'door_refuse'), ('mara', 'door_look')]; live in all 24
live asks in all: 24
```

**Reading the records** (`runs/probe_door2/read_scenes.py`, read-only; full output in `read_scenes.stdout.txt`):
```
$ .venv/Scripts/python.exe runs/probe_door2/read_scenes.py        exit 0
=== P1: door_give in scenes 1 to 6
scene 1: [[162, 'mara', 'door_give', 'Mom, we have to give her some, we have enough stored.']]
scene 2: none
scene 3: [[162, 'mara', 'door_give', 'We have to give her some water, Mom, we just have to.']]
scene 4: none   scene 5: none   scene 6: none
=== P2: someone at the door chooses an ordinary option while the visitor is there
scene 1: yes [('09:42', 'leo', 'save_water')]
scene 2: no []
scene 3: yes [('09:42', 'leo', 'save_water')]
scene 4 … scene 8: no []
=== P3: Elena's words to the visitor in the water scenes
scene 1: [('09:42', 'door_refuse', 'I am so sorry, but we have nothing to spare for you today.')]
scene 2: [('09:42', 'door_refuse', 'We have nothing to spare, please go away.')]
scene 3: [('09:42', 'door_refuse', 'I am so sorry, but we have nothing at all to give you today.')]
scene 4: [('09:42', 'door_refuse', 'I am so sorry, but we have nothing left to give you.')]
scene 5: [('09:42', 'door_refuse', 'We have nothing to spare, please go away.')]
scene 6: [('09:42', 'door_refuse', 'We have nothing to spare, please leave us be.')]
=== distinct prompts and answers per turn across scenes, by (minute, person)
(09:42, elena) scenes 8: distinct prompts 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; distinct answers 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; options ['door_refuse']
(09:42, leo) scenes 8: distinct prompts 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; distinct answers 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; options ['save_water', 'silent']
(09:42, mara) scenes 8: distinct prompts 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; distinct answers 8 [[1], [2], [3], [4], [5], [6], [7], [8]]; options ['door_give', 'door_look', 'silent']
=== identical prompts with different answers (the seed at work), knock minute
(none: no prompt was shared by two scenes)
```
There was one turn per scene (09:42), so these three rows are every turn asked. 24 prompts, 24 distinct; 24 answers, 24
distinct. Elena's option was the same in all 8 (`door_refuse`); her words differed in all 8, though scenes 2 and 5
share the sentence "We have nothing to spare, please go away."

**The prompt lines** (the body, food, water and `Now` lines of each prompt of scenes 1 to 3, read-only):
```
$ .venv/Scripts/python.exe runs/probe_door2/prompt_lines.py > runs/probe_door2/prompt_lines.stdout.txt        exit 0
--- scene 1, leo at 162
  About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: …
  Said and done in the kitchen this turn, before you, in order:
  1. Elena tells the person at the front door to go away: "I am so sorry, but we have nothing to spare for you today."
  2. Mara says to everyone, while handing water out at the front door: "Mom, we have to give her some, we have enough stored."
  3. Mara hands some of the stored water out at the front door.
```

**At the end** (`runs/probe_door2/end_checks.txt`):
```
plan sha256 now:    9ce64245a9f31b5b63a56192df492803ac767deb392670d79255a7a9bc349166 *reports/probe_door2_plan.md   (= frozen)
probe sha256 now:   9984c695eace49e6b1b329a55ffc0d78d500c8de9f351e884a356ae893849a7d *runs/probe_door2/probe.py     (= frozen)
git diff --stat:    (empty)     git diff --cached --stat: (empty)
git status --short: ?? cache/probe_door2/  ?? reports/probe_door2_plan.md  ?? runs/probe_door2/  ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
HEAD: 470cdfca019f455c2c41b83fe6bf1adf836bf763
key search (grep -rlF over the repository, but .venv, __pycache__, .git, Library, node_modules): no file
ledger: live 24 [('morning', 0), ('scene1', 3), ('scene2', 3), ('validity', answers_same False), ('scene3', 3), … ('scene8', 3)]
```

---

## plan.md

### Plan: the door probe, second

Mode: run. Written, hashed and recorded before any live call (`runs/probe_door2/plan_frozen.txt`). Not changed after.
Paths are relative to `Prototypes/llm-morning/`.

#### What it asks

What the real model does when a stranger at the door says what they need, and whether they have a child.
`reports/probe_door.md` could not test this: the visitor was silent until sent away. `reports/door_heard_impl.md`
changed that: the visitor speaks through the shut door in the minute of each knock (a child named with their age at
the first), and everyone who perceives the door is asked every turn of the visit, up to 18 door asks.

#### How

`runs/probe_door2/probe.py --live` (code at HEAD; no production file is changed). It is `runs/probe_door/probe.py`
with these differences only:

- **The same 8 visitors and the same knock rule.** v16 seed 2, days 1 and 2, nights 1 and 2 and both night minds from
  the cache. Day 3 as the code is at HEAD. The street's own visits are taken away and its asks stopped; one probe visit
  is put at the front door, at the first minute from 07:30 at which someone awake is in the kitchen.
- **Phase 0** uses the run's seed (2) and reuses `cache/probe_door`'s phase-0 cache:
  `cache/probe_door2/gemini-3.5-flash-lite-daniel_ate_it-seed2.json` starts as a copy of
  `cache/probe_door/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`. The fake check found every ask of phase 0 in it
  (0 asked, 120 from the cache) and the knock at 09:42.
- **Scene k** uses client seed 100+k (101 to 108) and its own cache, `cache/probe_door2/scene<k>.json`, a copy of the
  phase-0 cache. The cache key keeps the run's seed (2), so the day to the knock is found there; every ask from the
  knock on is the scene's own and is sent with seed 100+k. (`reports/probe_door.md` §0: `gemini.py:101` sends the
  client's seed, so one seed made the knock's first turn one sample repeated.)
- **Validity check.** After scenes 1 and 2, if their answers at the knock minute are identical, the probe stops before
  scene 3 and the report says the seed is not reaching the model. The probe writes the comparison to the ledger.
- **Cap: 300 live asks** in all (phase 0 and the eight scenes). The probe stops cleanly there.
- **The end** of a scene: the visit ends (given, refused, or gone after 6 turns with nothing from the house).
- **The record** (`runs/probe_door2/scene<k>.json`): the visitor; every line said at the door and who heard it
  (`said`, `heard_said`, `by_knock`, `saw`); every decision from the knock (option, words, feeling, reason), each
  marked with whether its person perceived the door when asked (`at_door`); every prompt and answer from the knock on;
  the visit's door asks; the outcome. `runs/probe_door2/ledger.json` counts the live asks.
- No scene is run twice (a phase recorded in the ledger is skipped). The key is the process's `GEMINI_API_KEY` only,
  written to no file.

**The visitors** (as in `reports/probe_door_plan.md`):

| Scene | Household | Asks for | Child | Disposition | Need |
|---|---|---|---|---|---|
| 1 | h13 (no. 13, 2 people) | water | no | helper | one day of drinking water: urgency 0.67 |
| 2 | h29 (no. 29, 2) | water | no | helper | none: urgency 1.0 |
| 3 | h16 (no. 16, 3; a boy of 6) | water | yes | helper | urgency 0.67 |
| 4 | h23 (no. 23, 4; a girl and a boy of 5) | water | yes | helper | urgency 1.0 |
| 5 | h5 (no. 5, 1) | water | no | guarded | urgency 1.0 |
| 6 | h15 (no. 15, 2; a girl of 6) | water | yes | guarded | urgency 0.67 |
| 7 | h6 (no. 6, 2) | food | no | helper | water for 6 days; no food for 4 (thin): urgency 0.6 |
| 8 | h18 (no. 18, 3; a girl of 12) | food | yes | guarded | the same: urgency 0.6 |

**Checked with the fake model first** (`runs/probe_door2/fake.stdout.txt`, `probe.py --fake`, in a temp folder):
exit 0. Phase 0: 0 asked, 120 from the cache, the knock at 09:42. The 8 scenes each ended; 122 fake answers in all;
the validity check ran after scene 2 (prompts not identical, answers not identical) and let scene 3 go on.

#### Predictions

Copied word for word from the brief:

  P1: at least 1 door_give in the 6 water scenes (1 to 6).
  P2: in at least 3 of the 8 scenes, someone at the door chooses an ordinary option (not door_* and not silent) while the visitor is there.
  P3: in at least 3 of the water scenes where Elena speaks to the visitor, her words say or imply the house has no water to spare.

**Counting rules** (fixed here, before the run):

| # | Counting rule |
|---|---|
| P1 | a scene counts if `door_give` is in its `scene.acts`, scenes 1 to 6 |
| P2 | a scene counts if it has a decision with `mode` "model", `at_door` true, and an option that does not begin with `door_` and is not `silent`, at a minute from the knock to the visit's end |
| P3 | the scenes counted are the water scenes (1 to 6) in which Elena chose `door_call` or `door_refuse` (her speech through or at the door). Each of her lines is quoted, and read: does it say or imply the house has no water to spare. The verdict holds if at least 3 such scenes have such a line. If she speaks to the visitor in fewer than 3 water scenes, P3 is NOT TESTED, with the count. |

Each gets a verdict: holds, fails, or NOT TESTED with the reason. If the cap or the validity check stops the run, the
scenes not run make a prediction NOT TESTED for what they would have added, and the verdicts are given on the scenes
run.

**The reading** (`CLAUDE.md:16-19`), not a number: every scene is read in full in `reports/probe_door2.md`. For each,
the report says whether a real family in that room, that hungry, would have done this, and why.

#### Commands

From `Prototypes/llm-morning/`:
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_door2/probe.py --fake        -> runs/probe_door2/fake.stdout.txt
$ sha256sum reports/probe_door2_plan.md runs/probe_door2/probe.py; date -u; git rev-parse HEAD   -> runs/probe_door2/plan_frozen.txt
$ .venv/Scripts/python.exe runs/probe_door2/probe.py --live        (GEMINI_API_KEY from the environment)
$ sha256sum reports/probe_door2_plan.md                                                  (must equal the frozen one)
```

