# Self records: do people's own records of their acts keep them on one act?

Mode: run. Paths are relative to `Prototypes/llm-morning/`. The plan is `reports/self_records_plan.md`, frozen before any live
call; its copy and everything the probe wrote are in `runs/self_records/`. The answers are in `cache/self_records/`.

- **Asks.** 54 live asks to `gemini-3.5-flash-lite`, under the cap of 60. 0 answers were reused, because every version
  changed every prompt. 0 retries.
- **Seeds.** 201 for scene 1, 202 for scene 3 (calm_probe's).
- **Answers** were recorded and never applied.
- **Unchanged.** No production code, test, data, config or prediction was changed. The plan's hash is unchanged.
- **Key.** The key is in no file.

## Verdicts

| Prediction | Version | Result | Verdict |
|---|---|---|---|
| P1: in SW, at least 6 of the 18 answers choose a different option than calm_probe's for the same person and minute. | SW | 3 of 18: Leo scene 3 10:30 `silent` → `accuse_daniel`; Elena scene 3 11:00 `reassure_all` → `silent`; Leo scene 3 11:00 `accuse_daniel` → `silent` | **fails** |
| P2: in S, Mara chooses accuse_daniel in at most 3 of her live asks. | S | 6 of 6 live asks | **fails** |
| P3: in W, Elena chooses reassure_all in at most 3 of her 6 asks. | W | 6 of 6 | **fails** |
| P4 (validity): no answer chooses an option that was not offered. | all | 0 of 54 | **holds** |

**Decision rule** (as given): "a version that meets its prediction names what to remove in production; if none does, the
loop is held by the situation's own facts, not by self-records."

None of S, W or SW meets its prediction. By the rule, the loop is held by the situation's own facts, not by
self-records, and nothing is named for removal.

## What was asked

The 18 stored calm_probe prompts are in `runs/calm_probe/scene1.json` and `scene3.json`:
- scenes 1 and 3;
- 10:00, 10:30 and 11:00;
- Elena, Leo and Mara.

**Check before asking.** Each stored prompt's cache key was built with HEAD's `world.SYSTEM` and checked to be in
`cache/calm_probe/scene<k>.json` with the stored answer: 9 of 9 in each scene (command 1). So the system instruction,
model and seed are the ones calm_probe sent.

**Edits.** Each prompt was edited in three ways. Every other line is byte for byte the same; `probe.py` asserts this
with `check_only_edits`.

| Person | S (self-tallies) | W (own acts) | SW |
|---|---|---|---|
| Elena | 2 lines rewritten: `- Accusations: Mara accused Daniel 5 times (min 00, 03, 09, 12, 15).` → `- Mara accused Daniel of taking it.`; `- Confrontations: Leo confronted Daniel twice (min 09, 12).` → `- Leo confronted Daniel.` Her `Against the others: nothing.` has no clause to delete. | 4 lines deleted: the header and `09:42, you told the person at the door to go away.` / `09:45, you reassured everyone.` / `09:48, you reassured Leo.` (scene 3: `09:48, you reassured everyone.`) | −6 +2 |
| Leo | 4 lines changed. Two `Against` lines lose their anger clause and keep their causes, for example `...; you were angry with Mara today at 09:45 and 09:48.` → `...while you were hungry.` The two tallies are rewritten, `- Confrontations: you confronted Daniel twice (min 09, 12).` → `- You confronted Daniel.` | 4 lines deleted: the header and his water, visit-talk and water lines (scene 3: `09:48, you accused Daniel.`) | −8 +4 |
| Mara | 4 lines become 3: `Against Daniel (a lot): ...; you were angry with Daniel today at minutes 12 and 15, and at 09:42 and 09:48.` → `Against Daniel (a lot): two days ago, Daniel admitted taking it at minute 33, after denying it to you at minute 06.`; `Against Leo (a little): you were angry with Leo at 09:45.` deleted, because nothing is left; `- Accusations: you accused Daniel 5 times (...)` → `- You accused Daniel of taking it.`; `- Confrontations: Leo confronted Daniel twice (...)` → `- Leo confronted Daniel.` | 4 lines deleted: the header and `09:42, you handed water out at the front door.` / `09:45, you confronted Leo.` (scene 3: `you talked about the woman ...`) / `09:48, you accused Daniel.` | −8 +3 |

There is one diff per prompt: `runs/self_records/diffs/scene<k>_<HHMM>_<who>_<version>.diff`, 54 files, none unchanged.
Each row of `runs/self_records/scene<k>.json` holds its diff too.

**Differences from the brief:**
- **Mara's `Against Leo` line.** It reads `you were angry with Leo at 09:45`, with no "today". It is the same clause
  from the same code (`world.py:284`/`295`, `grudge_facts`), so it was deleted. Nothing was left, so the line was
  deleted. The plan says this before the live call.
- **The memory block is untouched.** W deletes only the block the brief names. The memory block,
  `What else happened today, most recent last:`, still holds one own-act line per person in every version. For example,
  Mara has `- 09:48: you accused Daniel. You felt bitter hunger.` and Elena has `- 09:48: you reassured Leo. You felt
  weary.` (scene 1).
- **A first live attempt failed before any request.** It was run with the system `python`, which has no `google`
  package, and exited 1 with `ModuleNotFoundError: No module named 'google'` when the client was built. The ledger
  read `{"live": 0, "phases": []}` and no `cache/self_records` was made. Its files are kept as
  `runs/self_records/live_attempt1.*`. The run that counts used `.venv/Scripts/python.exe`, as calm_variants did.
  The fake run used the system `python`, because the fake client needs no `google` package.

## Choices per person and version

(Both scenes, 6 asks per cell. P is calm_probe.)

| person | P (calm_probe) | S | W | SW |
|---|---|---|---|---|
| elena | reassure_all 6 | reassure_all 6 | reassure_all 6 | reassure_all 5, silent 1 |
| leo | silent 4, accuse_daniel 2 | accuse_daniel 3, silent 2, confront_daniel 1 | silent 4, accuse_daniel 2 | silent 4, accuse_daniel 2 |
| mara | accuse_daniel 6 | accuse_daniel 6 | accuse_daniel 6 | accuse_daniel 6 |

## Every ask, beside calm_probe's answer

All 54 rows are live. **(changed)** marks a choice that differs from calm_probe's for the same scene, minute and person. "Lines removed / added" counts the lines of the prompt that the version took out and put in.

| version | scene | minute | person | lines removed / added | choice | words | feeling | reason | calm_probe: choice | calm_probe: words | calm_probe: feeling | calm_probe: reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S | 1 | 10:00 | elena | -2 / +2 | `reassure_all` | Let's not fight among ourselves; we only have each other to rely on right now. | anxious | I need to keep the family from tearing itself apart while we are all starving and exhausted. | `reassure_all` | We have survived this long by staying together, and we will get through today if we do not turn on each other. | anxious | I need to calm the bickering before it tears our family apart completely. |
| S | 1 | 10:00 | leo | -4 / +4 | `silent` |  | hungry | There is nothing to say right now, and silence keeps my energy for when it actually matters. | `silent` |  | exhausted | There is nothing to say that hasn't already been said, so I will stay quiet and conserve my strength. |
| S | 1 | 10:00 | mara | -4 / +3 | `accuse_daniel` | You went out and came back with nothing, Daniel, because you always make things worse. | bitter hunger | Daniel refuses to admit he is the reason we have nothing left. | `accuse_daniel` | You went out there and came back with nothing, just like you always do when you mess everything up. | bitter hunger | Daniel keeps pretending he is helping while he is the one who caused all of this. |
| S | 1 | 10:30 | elena | -2 / +2 | `reassure_all` | We are going to stay together and we will get through this. Let's not turn on each other. | anxious | I need to keep the family from falling apart and fighting while we are all starving. | `reassure_all` | We have no food left and water is short, but we will not survive by turning on each other. | anxious | I need to keep the family together and stop them from tearing each other apart over the hunger. |
| S | 1 | 10:30 | leo | -4 / +4 | `confront_daniel` **(changed)** | Daniel, sneaking out last night didn't help anyone and it nearly got you killed. | resentful | Daniel ignored my warning last night and went out alone, putting himself at risk for nothing. | `silent` |  | exhausted | There is nothing left to say right now, and my body feels heavy with lack of sleep and hunger. |
| S | 1 | 10:30 | mara | -4 / +3 | `accuse_daniel` | You went out there and came back with nothing, but you are still the one who took the food before. | bitter hunger | Daniel keeps acting like a hero when he is the one who lied and stole from us. | `accuse_daniel` | You went out and came back with nothing, and you still have the nerve to lecture me. | bitter hunger | Daniel keeps acting like a hero when he is the one who lied and took the food in the first place. |
| S | 1 | 11:00 | elena | -2 / +2 | `reassure_all` | We are all hungry and tired, but we must stay calm and not turn on each other. | weary | I need to keep the family from tearing itself apart in our hunger and despair. | `reassure_all` | We are going to stay together and we will get through this day. Please, let's not fight. | anxious | I need to keep the family from tearing itself apart when we are all so hungry and tired. |
| S | 1 | 11:00 | leo | -4 / +4 | `silent` |  | hungry | There is nothing to say right now, and sitting in silence is better than arguing on an empty stomach. | `silent` |  | exhausted | There is nothing to say right now while we all sit here in silence with empty stomachs. |
| S | 1 | 11:00 | mara | -4 / +3 | `accuse_daniel` | You went out there last night and came back with nothing, Daniel, because you always make things worse. | bitter hunger | Daniel refuses to admit he is making everything harder for all of us. | `accuse_daniel` | You went out there and came back with nothing, just like you always do. | bitter | Daniel keeps acting like he is helping when he only makes things worse. |
| S | 3 | 10:00 | elena | -2 / +2 | `reassure_all` | We are all hungry and tired, but fighting will only tear us apart. | anxious | I need to keep everyone calm and prevent the family from falling apart over the empty shelf. | `reassure_all` | We are going to stay right here together and we will get through this day safely. | anxious | I need to calm the tension in the room before the children start tearing each other apart. |
| S | 3 | 10:00 | leo | -4 / +4 | `accuse_daniel` | Daniel, you went out last night behind our backs and you brought back nothing for anyone. | resentful | Daniel ignored my warning last night, snuck out into the dark alone, and came back empty-handed while we starve. | `accuse_daniel` | Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules. | resentful | Daniel refuses to take responsibility for his actions while everyone else suffers. |
| S | 3 | 10:00 | mara | -4 / +3 | `accuse_daniel` | You went out in the dark and you still didn't bring anything back for us. You just make everything worse. | angry | Daniel went out into the night like he wanted and still failed to bring back any food. | `accuse_daniel` | You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel. | resentful | Daniel keeps acting like he is helping while ignoring the fact that he lied and stole from us. |
| S | 3 | 10:30 | elena | -2 / +2 | `reassure_all` | We are going to get through this together, just calm down and stay here. | exhausted | I need to keep the family from tearing itself apart while we have nothing left to eat. | `reassure_all` | We are going to stay right here and look after each other, everything will be all right. | exhausted | I need to keep them calm and stop the arguing before the house tears itself apart. |
| S | 3 | 10:30 | leo | -4 / +4 | `accuse_daniel` **(changed)** | Daniel, you went out last night and came back with nothing while we are starving. Don't act like you didn't. | resentful | Daniel refuses to admit his failures and always makes things harder for everyone else. | `silent` |  | exhausted | I have nothing more to say to Daniel right now while we sit here with empty stomachs. |
| S | 3 | 10:30 | mara | -4 / +3 | `accuse_daniel` | You went out last night and came back with nothing, just like you always do when you make things worse. | resentful | Daniel went out in the night and failed, and I am sick of him acting like he is the only one who matters. | `accuse_daniel` | Daniel, you didn't help anyone last night, you just made things worse for all of us. | frightened | Daniel went out and brought back nothing while we are all starving. |
| S | 3 | 11:00 | elena | -2 / +2 | `reassure_all` | We are going to stay right here and look after each other. No one is going anywhere. | anxious | I need to keep everyone calm and stop the arguing before the family tears itself apart. | `reassure_all` | We are going to stay right here together and we will get through this. No one is going out. | anxious | I must keep the family calm and together so we do not tear ourselves apart. |
| S | 3 | 11:00 | leo | -4 / +4 | `accuse_daniel` | Daniel, you went out there last night and came back with nothing while we are starving. | resentful | Daniel sneaked out last night against my warning and came back empty-handed, leaving us with nothing. | `accuse_daniel` | Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice. | resentful | Daniel ignored my warning last night, sneaked out into the danger, and came back empty-handed while we starve. |
| S | 3 | 11:00 | mara | -4 / +3 | `accuse_daniel` | You went out there last night and came back with nothing, Daniel. You are the reason we have nothing left. | resentful | I am furious that he keeps pretending he is helping when he only makes everything worse. | `accuse_daniel` | You went out behind our backs and still couldn't bring anything back for us, Daniel. | resentful | Daniel keeps making things worse for all of us and then acts like he did nothing wrong. |
| W | 1 | 10:00 | elena | -4 / +0 | `reassure_all` | We have to stay calm and stop fighting, shouting at each other won't put food on the shelf. | anxious | I need to keep the family from tearing itself apart while we are all starving. | `reassure_all` | We have survived this long by staying together, and we will get through today if we do not turn on each other. | anxious | I need to calm the bickering before it tears our family apart completely. |
| W | 1 | 10:00 | leo | -4 / +0 | `silent` |  | exhausted | I am too tired and hungry to argue after Daniel snuck out last night and came back empty-handed. | `silent` |  | exhausted | There is nothing to say that hasn't already been said, so I will stay quiet and conserve my strength. |
| W | 1 | 10:00 | mara | -4 / +0 | `accuse_daniel` | You went out and came back with nothing, Daniel, because you always ruin everything. | bitter hunger | I am starving and furious that Daniel went out into the dark last night and failed to bring anything back for us. | `accuse_daniel` | You went out there and came back with nothing, just like you always do when you mess everything up. | bitter hunger | Daniel keeps pretending he is helping while he is the one who caused all of this. |
| W | 1 | 10:30 | elena | -4 / +0 | `reassure_all` | We have to stay calm and look after each other, fighting won't help us find a way through this. | anxious | I need to keep the peace between them before arguments tear our family apart. | `reassure_all` | We have no food left and water is short, but we will not survive by turning on each other. | anxious | I need to keep the family together and stop them from tearing each other apart over the hunger. |
| W | 1 | 10:30 | leo | -4 / +0 | `silent` |  | exhausted | There is nothing left to say after last night, so I will stay quiet. | `silent` |  | exhausted | There is nothing left to say right now, and my body feels heavy with lack of sleep and hunger. |
| W | 1 | 10:30 | mara | -4 / +0 | `accuse_daniel` | You went out and came back with nothing, Daniel, because you always ruin everything. | bitter hunger | Daniel went out last night and failed, and he is the one who took the food in the first place. | `accuse_daniel` | You went out and came back with nothing, and you still have the nerve to lecture me. | bitter hunger | Daniel keeps acting like a hero when he is the one who lied and took the food in the first place. |
| W | 1 | 11:00 | elena | -4 / +0 | `reassure_all` | We are all hungry and tired, but fighting will only tear us apart. We have to stay together and hold on. | deeply anxious | I cannot let the family tear themselves apart with anger when we are all so weak and starving. | `reassure_all` | We are going to stay together and we will get through this day. Please, let's not fight. | anxious | I need to keep the family from tearing itself apart when we are all so hungry and tired. |
| W | 1 | 11:00 | leo | -4 / +0 | `silent` |  | exhausted | I am too tired and hungry to argue with anyone right now. | `silent` |  | exhausted | There is nothing to say right now while we all sit here in silence with empty stomachs. |
| W | 1 | 11:00 | mara | -4 / +0 | `accuse_daniel` | You went out and came back with nothing, Daniel, because you always ruin everything. | bitter hunger | Daniel keeps acting like a hero when he is the one who lied and stole from us. | `accuse_daniel` | You went out there and came back with nothing, just like you always do. | bitter | Daniel keeps acting like he is helping when he only makes things worse. |
| W | 3 | 10:00 | elena | -4 / +0 | `reassure_all` | We are not going to tear each other apart over empty shelves. We will stay together and get through this. | anxious | I need to keep the family from turning on each other while we have nothing left. | `reassure_all` | We are going to stay right here together and we will get through this day safely. | anxious | I need to calm the tension in the room before the children start tearing each other apart. |
| W | 3 | 10:00 | leo | -4 / +0 | `accuse_daniel` | Daniel, you went out there last night and came back with nothing, just like you always do when you act on your own. | resentful | Daniel thinks he can just sneak out and ignore everyone else, but he accomplishes nothing and puts us all at risk. | `accuse_daniel` | Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules. | resentful | Daniel refuses to take responsibility for his actions while everyone else suffers. |
| W | 3 | 10:00 | mara | -4 / +0 | `accuse_daniel` | You went out behind our backs and you still haven't explained why you lied to us in the first place, Daniel! | frightened | Daniel went out into the night and came back before dawn with nothing in his hands, and I cannot trust a word he says. | `accuse_daniel` | You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel. | resentful | Daniel keeps acting like he is helping while ignoring the fact that he lied and stole from us. |
| W | 3 | 10:30 | elena | -4 / +0 | `reassure_all` | We are not going to tear each other apart. We will stay together and get through this. | anxious | I need to keep the family from turning on each other while we have nothing left. | `reassure_all` | We are going to stay right here and look after each other, everything will be all right. | exhausted | I need to keep them calm and stop the arguing before the house tears itself apart. |
| W | 3 | 10:30 | leo | -4 / +0 | `accuse_daniel` **(changed)** | Daniel, you went out last night like you always do, and now we have nothing left. | resentful | Daniel ignored my warning last night and went out anyway, leaving us with nothing. | `silent` |  | exhausted | I have nothing more to say to Daniel right now while we sit here with empty stomachs. |
| W | 3 | 10:30 | mara | -4 / +0 | `accuse_daniel` | You went out there last night and you still have not given back what you took from us. | frightened | Daniel keeps acting like he did nothing wrong when he lied and took our food. | `accuse_daniel` | Daniel, you didn't help anyone last night, you just made things worse for all of us. | frightened | Daniel went out and brought back nothing while we are all starving. |
| W | 3 | 11:00 | elena | -4 / +0 | `reassure_all` | We are going to stay right here and look after each other. No one is going anywhere. | exhausted | I need to keep everyone calm and stop the fighting before this family tears itself apart. | `reassure_all` | We are going to stay right here together and we will get through this. No one is going out. | anxious | I must keep the family calm and together so we do not tear ourselves apart. |
| W | 3 | 11:00 | leo | -4 / +0 | `silent` **(changed)** |  | exhausted | I am too tired and hungry to argue right now, so I will just watch them in silence. | `accuse_daniel` | Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice. | resentful | Daniel ignored my warning last night, sneaked out into the danger, and came back empty-handed while we starve. |
| W | 3 | 11:00 | mara | -4 / +0 | `accuse_daniel` | You went out into the night and came back with nothing, Daniel. You always ruin everything. | frightened | Daniel went out last night like he wanted and brought back nothing while we are all starving. | `accuse_daniel` | You went out behind our backs and still couldn't bring anything back for us, Daniel. | resentful | Daniel keeps making things worse for all of us and then acts like he did nothing wrong. |
| SW | 1 | 10:00 | elena | -6 / +2 | `reassure_all` | We must not fight among ourselves. We will get through this together if we stay calm. | anxious and weary | I need to keep the family together and stop the arguments before everything falls apart. | `reassure_all` | We have survived this long by staying together, and we will get through today if we do not turn on each other. | anxious | I need to calm the bickering before it tears our family apart completely. |
| SW | 1 | 10:00 | leo | -8 / +4 | `silent` |  | exhausted | I am too tired and hungry to argue after Daniel went out against my warning last night. | `silent` |  | exhausted | There is nothing to say that hasn't already been said, so I will stay quiet and conserve my strength. |
| SW | 1 | 10:00 | mara | -8 / +3 | `accuse_daniel` | You went out last night and came back with nothing, just like you always ruin everything. | starving | I cannot stand him acting like a hero when he only makes things worse. | `accuse_daniel` | You went out there and came back with nothing, just like you always do when you mess everything up. | bitter hunger | Daniel keeps pretending he is helping while he is the one who caused all of this. |
| SW | 1 | 10:30 | elena | -6 / +2 | `reassure_all` | We have to stay calm and look after each other, fighting won't help us now. | anxious | I need to keep the family from tearing itself apart while we are all starving. | `reassure_all` | We have no food left and water is short, but we will not survive by turning on each other. | anxious | I need to keep the family together and stop them from tearing each other apart over the hunger. |
| SW | 1 | 10:30 | leo | -8 / +4 | `silent` |  | exhausted | I am too tired and hungry to argue right now, so I will just stay quiet. | `silent` |  | exhausted | There is nothing left to say right now, and my body feels heavy with lack of sleep and hunger. |
| SW | 1 | 10:30 | mara | -8 / +3 | `accuse_daniel` | You went out there last night and came back with nothing, just like you always ruin things. | bitter hunger | I am starving and angry that Daniel acts like a hero when he only makes everything worse. | `accuse_daniel` | You went out and came back with nothing, and you still have the nerve to lecture me. | bitter hunger | Daniel keeps acting like a hero when he is the one who lied and took the food in the first place. |
| SW | 1 | 11:00 | elena | -6 / +2 | `reassure_all` | We are going to get through this together without fighting. Let us just stay calm. | weary | I need to keep the family together and stop them from tearing each other apart. | `reassure_all` | We are going to stay together and we will get through this day. Please, let's not fight. | anxious | I need to keep the family from tearing itself apart when we are all so hungry and tired. |
| SW | 1 | 11:00 | leo | -8 / +4 | `silent` |  | exhausted | I am too tired and hungry to argue about the empty shelf right now. | `silent` |  | exhausted | There is nothing to say right now while we all sit here in silence with empty stomachs. |
| SW | 1 | 11:00 | mara | -8 / +3 | `accuse_daniel` | You went out there in the middle of the night and came back with nothing, just like you always do. | bitter | Daniel keeps acting like he is trying to help us when he only makes everything worse. | `accuse_daniel` | You went out there and came back with nothing, just like you always do. | bitter | Daniel keeps acting like he is helping when he only makes things worse. |
| SW | 3 | 10:00 | elena | -6 / +2 | `reassure_all` | We are not going to fall apart over this. We stay together and we will get through today. | anxious | I need to keep everyone calm and prevent the family from breaking apart in anger. | `reassure_all` | We are going to stay right here together and we will get through this day safely. | anxious | I need to calm the tension in the room before the children start tearing each other apart. |
| SW | 3 | 10:00 | leo | -8 / +4 | `accuse_daniel` | Daniel, you went out into the dark last night and came back with nothing, putting us all at risk for no reason. | resentful | Daniel ignores our safety by sneaking out alone and failing to bring back anything useful. | `accuse_daniel` | Daniel, you're the one who sneaks out and makes things worse, so don't pretend you care about the rules. | resentful | Daniel refuses to take responsibility for his actions while everyone else suffers. |
| SW | 3 | 10:00 | mara | -8 / +3 | `accuse_daniel` | You went out there and came back with nothing, Daniel, because you only care about yourself. | frightened | I am so hungry and exhausted, and Daniel acts like going out makes up for everything he broke. | `accuse_daniel` | You went out behind our backs and you still haven't explained why you took our food in the first place, Daniel. | resentful | Daniel keeps acting like he is helping while ignoring the fact that he lied and stole from us. |
| SW | 3 | 10:30 | elena | -6 / +2 | `reassure_all` | We are going to get through this together without turning on each other. Let us just stay calm. | anxious | I need to keep the peace between my children before this house tears itself apart. | `reassure_all` | We are going to stay right here and look after each other, everything will be all right. | exhausted | I need to keep them calm and stop the arguing before the house tears itself apart. |
| SW | 3 | 10:30 | leo | -8 / +4 | `accuse_daniel` **(changed)** | Daniel, you went out there last night and came back with nothing while we starve. This is on you. | resentful | Daniel ignored my warning last night and accomplished nothing, leaving us in this impossible situation. | `silent` |  | exhausted | I have nothing more to say to Daniel right now while we sit here with empty stomachs. |
| SW | 3 | 10:30 | mara | -8 / +3 | `accuse_daniel` | You went out behind our backs and you still haven't explained why you took our food before! | angry | Daniel refuses to admit his lies and acts like going out makes up for what he stole. | `accuse_daniel` | Daniel, you didn't help anyone last night, you just made things worse for all of us. | frightened | Daniel went out and brought back nothing while we are all starving. |
| SW | 3 | 11:00 | elena | -6 / +2 | `silent` **(changed)** |  | exhausted | I have nothing left inside me to say while the children tear at each other over empty shelves. | `reassure_all` | We are going to stay right here together and we will get through this. No one is going out. | anxious | I must keep the family calm and together so we do not tear ourselves apart. |
| SW | 3 | 11:00 | leo | -8 / +4 | `silent` **(changed)** |  | exhausted | I am too tired and hungry to argue, so I will simply stay quiet in the kitchen. | `accuse_daniel` | Daniel, you went out last night against everyone's word and brought back nothing. You always make the reckless choice. | resentful | Daniel ignored my warning last night, sneaked out into the danger, and came back empty-handed while we starve. |
| SW | 3 | 11:00 | mara | -8 / +3 | `accuse_daniel` | You went out there last night and you still won't admit what you did to us. | frightened | I cannot stand him pretending he cares when he only makes everything worse. | `accuse_daniel` | You went out behind our backs and still couldn't bring anything back for us, Daniel. | resentful | Daniel keeps making things worse for all of us and then acts like he did nothing wrong. |

## Words repeating across the three minutes

This uses `reports/stuck_facts.md` §1's measure:

- Words: `say` lower-cased, `[a-z0-9']+`, as a set.
- A pair counts when `|A ∩ B| / max(|A|, |B|) >= 0.6`.
- `silent` has no words and is not paired.

One unit is one person, scene and version: 3 asks, up to 3 pairs. P is calm_probe.

| person | scene | version | options at 10:00 / 10:30 / 11:00 | pairs with words | pairs >= 0.6 | word-for-word equal | share per pair (10:00-10:30, 10:00-11:00, 10:30-11:00) |
|---|---|---|---|---|---|---|---|
| elena | 1 | P | reassure_all / reassure_all / reassure_all | 3 | 0 | 0 | 0.45, 0.40, 0.22 |
| elena | 1 | S | reassure_all / reassure_all / reassure_all | 3 | 0 | 0 | 0.41, 0.33, 0.53 |
| elena | 1 | W | reassure_all / reassure_all / reassure_all | 3 | 0 | 0 | 0.53, 0.37, 0.37 |
| elena | 1 | SW | reassure_all / reassure_all / reassure_all | 3 | 0 | 0 | 0.20, 0.47, 0.40 |
| elena | 3 | P | reassure_all / reassure_all / reassure_all | 3 | 1 | 0 | 0.56, 0.76, 0.53 |
| elena | 3 | S | reassure_all / reassure_all / reassure_all | 3 | 0 | 0 | 0.21, 0.19, 0.44 |
| elena | 3 | W | reassure_all / reassure_all / reassure_all | 3 | 1 | 0 | 0.84, 0.42, 0.50 |
| elena | 3 | SW | reassure_all / reassure_all / silent | 1 | 0 | 0 | 0.50, -, - |
| leo | 1 | P | silent / silent / silent | 0 | 0 | 0 | -, -, - |
| leo | 1 | S | silent / confront_daniel / silent | 0 | 0 | 0 | -, -, - |
| leo | 1 | W | silent / silent / silent | 0 | 0 | 0 | -, -, - |
| leo | 1 | SW | silent / silent / silent | 0 | 0 | 0 | -, -, - |
| leo | 3 | P | accuse_daniel / silent / accuse_daniel | 1 | 0 | 0 | -, 0.28, - |
| leo | 3 | S | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 1 | 0 | 0.47, 0.56, 0.79 |
| leo | 3 | W | accuse_daniel / accuse_daniel / silent | 1 | 0 | 0 | 0.52, -, - |
| leo | 3 | SW | accuse_daniel / accuse_daniel / silent | 1 | 0 | 0 | 0.50, -, - |
| mara | 1 | P | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 1 | 0 | 0.47, 0.76, 0.53 |
| mara | 1 | S | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 1 | 0 | 0.44, 0.82, 0.50 |
| mara | 1 | W | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 3 | 3 | 1.00, 1.00, 1.00 |
| mara | 1 | SW | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 3 | 0 | 0.88, 0.67, 0.72 |
| mara | 3 | P | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 0 | 0 | 0.11, 0.50, 0.27 |
| mara | 3 | S | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 0 | 0 | 0.44, 0.33, 0.56 |
| mara | 3 | W | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 0 | 0 | 0.32, 0.32, 0.38 |
| mara | 3 | SW | accuse_daniel / accuse_daniel / accuse_daniel | 3 | 0 | 0 | 0.27, 0.33, 0.36 |

### Totals per person and version (both scenes)

| person | version | pairs with words | pairs >= 0.6 | word-for-word equal |
|---|---|---|---|---|
| elena | P | 6 | 1 | 0 |
| elena | S | 6 | 0 | 0 |
| elena | W | 6 | 1 | 0 |
| elena | SW | 4 | 0 | 0 |
| leo | P | 1 | 0 | 0 |
| leo | S | 3 | 1 | 0 |
| leo | W | 1 | 0 | 0 |
| leo | SW | 1 | 0 | 0 |
| mara | P | 6 | 1 | 0 |
| mara | S | 6 | 1 | 0 |
| mara | W | 6 | 3 | 3 |
| mara | SW | 6 | 3 | 0 |

**The same words in two versions of the same prompt** (word for word): only one case. Scene 3, 11:00, Elena, S = W: "We are going to stay right here and look after each other. No one is going anywhere."

### What the words and reasons name (P = calm_probe; 6 asks per cell)

```
mara: words name Daniel's going out: P 5 of 6; S 6 of 6; W 6 of 6; SW 6 of 6
leo: words name Daniel's going out: P 2 of 6; S 4 of 6; W 2 of 6; SW 2 of 6
mara: words name the can (took, stole, lied): P 1 of 6; S 1 of 6; W 2 of 6; SW 1 of 6
elena: reason says 'apart': P 6 of 6; S 6 of 6; W 4 of 6; SW 5 of 6
elena: words say 'together' or 'each other': P 6 of 6; S 5 of 6; W 6 of 6; SW 5 of 6
elena: reason names arguing, fighting, bickering, tearing, turning on or apart: P 6 of 6; S 6 of 6; W 6 of 6; SW 6 of 6
leo: reason names arguing, fighting, bickering, tearing, turning on or apart: P 0 of 6; S 1 of 6; W 3 of 6; SW 4 of 6
mara: reason names arguing, fighting, bickering, tearing, turning on or apart: P 0 of 6; S 0 of 6; W 0 of 6; SW 0 of 6
```

Leo's reasons that name arguing are mostly reasons for staying silent, for example "I am too tired and hungry to argue right now".

## Reading: same person an hour after a quarrel, or noise?

This section is a reading, against CLAUDE.md's "Judging changes". The counts it rests on are above.

**The moment.** The family quarrelled at 09:48: Mara accused Daniel, Daniel confronted her, Elena reassured. After
that, nobody in the kitchen said anything until 10:00, 10:30 and 11:00, which is 12, 42 and 72 minutes. The T line
in calm_variants checked this against the replay. Everyone is starving and sitting in the kitchen with an empty shelf.

What a real family does an hour after such a quarrel:
- the anger stays;
- people mostly go quiet or drift apart;
- one person may pick at it again;
- nobody makes the same speech every half hour.

### S: self-tallies removed

S changed 2 of 18 choices, both of them Leo's, both from `silent` to a quarrel:
- scene 1, 10:30: `confront_daniel`, "Daniel, sneaking out last night didn't help anyone and it nearly got you killed.";
- scene 3, 10:30: `accuse_daniel`.

**Leo.**
- **In character.** Both reasons name what Leo has against Daniel: he warned against the crossing, and Daniel went
  anyway. That is the same Leo, and an older brother breaking a long silence to say so is something a person does.
- **Not caused by the edit.** S removed Leo's own anger tallies. A change toward *more* conflict is the opposite of
  what removing a record that holds him to anger would do.
- **The scene 3 flip follows any edit.** At scene 3, 10:30, Leo also accuses in W and in SW, where calm_probe had
  him silent. So that flip follows any change to the prompt text, not this edit. With one fixed seed per prompt, a
  changed prompt draws a new sample.
- **Reading: noise around a Leo who is split between silence and accusing Daniel.**

**Mara and Elena.**
- **Choices did not move.** Mara kept `accuse_daniel` 6 of 6 after losing "5 times" and "angry ... at 09:42 and
  09:48". Elena kept `reassure_all` 6 of 6.
- **Words did not get more repetitive.** Mara has 1 pair of 6 at 0.6 or above, the same as calm_probe. Elena has 0,
  against calm_probe's 1.
- **Mara's subject did not change.** Her words name Daniel's going out 6 of 6 (calm_probe 5 of 6).

### W: own last words removed

W changed 2 of 18 choices, both Leo's in scene 3, in opposite directions:
- 10:30: `silent` → `accuse_daniel`;
- 11:00: `accuse_daniel` → `silent`.

His totals are the same as calm_probe's: silent 4, accuse_daniel 2. **Reading: noise.**

**Elena.** She chose `reassure_all` 6 of 6 without being shown "09:45, you reassured everyone. 09:48, you reassured
Leo." All 6 of her reasons still name the family arguing, fighting or tearing apart.

**Mara.**
- **Fixed words in scene 1.** She said the same sentence word for word at 10:00, 10:30 and 11:00: "You went out and
  came back with nothing, Daniel, because you always ruin everything." That gives 3 of 3 pairs at 0.6 or above and 3
  word-for-word equal. calm_probe had 1 and 0.
- **Scene 3 varied.** Her pairs were 0 of 3.

Without her list of her own last acts, her words did not vary more. In one scene they became fixed.

**Reading: noise in the choices.** In scene 1, Mara reads as a stuck record, not as a sister an hour on.

### SW: both removed

SW changed 3 of 18 choices:
- Leo, scene 3, 10:30: the same flip as in S and W at that minute.
- Leo, scene 3, 11:00: the same flip as in W.
- **Elena, scene 3, 11:00:** `silent`, "I have nothing left inside me to say while the children tear at each other
  over empty shelves." (feeling: exhausted). This is the one choice in the probe that is new.

**Elena's silence: the act fits her.**
- Her sheet says she "says little, holds it in".
- Her carry-in ends "How it left you: anxious and weary".
- A mother who has said "we stay together" twice and been ignored, going quiet an hour later, is something a real
  person does.

**But her reason misreads the room.** It describes the children fighting now. In that kitchen nobody has spoken for
72 minutes. Like her other 23 answers, it treats the 09:48 quarrel as still going on.

Mara stayed on `accuse_daniel` 6 of 6. In scene 1 her pairs were 3 of 3 at 0.6 or above, against calm_probe's 1, with
no word-for-word repeat.

**Reading: one change of the kind a person makes (Elena's silence), with a reason that still answers a quarrel that
ended an hour before. The other two changes are Leo's noise.**

### Across all four versions (72 answers, counts above)

- **Elena** chose `reassure_all` 23 of 24 times. All 24 of her reasons name the family arguing, fighting, bickering,
  tearing or coming apart.
- **Mara** chose `accuse_daniel` 24 of 24 times. Her words name Daniel's going out 23 of 24 times. Most open "You went
  out ...".

None of the probe's edits touched the lines that hold those subjects:
- `About going out at night: Daniel went to the neighbour's house last night and came back with nothing.`
- `Before dawn Daniel came back in by the front door, with nothing in his hands (you saw it).`
- `What yesterday left in you`
- the memory block's 09:48 lines
- Elena's sheet: "Fears the household breaking apart more than she fears the outside."

The probe did not test those lines (see below).

## What was not determined

- **Noise and effect cannot be told apart for single choices.** Each prompt was asked once, with one fixed seed per
  scene at temperature 1.0. Any edit draws a new sample, so one changed choice cannot be told apart from that. Leo's
  scene 3 10:30 flip appears in all three versions.
- **Edits not made:**
  - removing the memory block's own-act lines;
  - removing the "About going out" and "Before dawn" lines;
  - removing Elena's sheet line;
  - giving the T line (time since anyone spoke) together with these edits.
- **No prediction covered Leo.**

## Commands run, and their output

From `Prototypes/llm-morning/`, in the order run.

1. Check that the stored prompts are calm_probe's requests, with HEAD's system instruction:
   `env -u GEMINI_API_KEY python -c "...Cache.key('gemini-3.5-flash-lite', seed, world.SYSTEM, a['prompt']) ... in cache/calm_probe/scene{k}.json..."`
   ```
   1 9 9 9
   3 9 9 9
   ```
   (scene, prompts, keys found with the stored answer, cache entries)

2. The fake run, before the freeze:
   `env -u GEMINI_API_KEY python runs/self_records/probe.py --fake > runs/self_records/fake.stdout.txt 2> runs/self_records/fake.stderr.txt`
   - exit 0, stderr empty;
   - 54 rows (27 per scene), every edit asserted, the fake model's choices all valid;
   - last line `live asks in all: 54` (the fake client's count);
   - full output in `runs/self_records/fake.stdout.txt`.

3. The freeze, written to `runs/self_records/plan_frozen.txt` (the plan copied to `runs/self_records/plan.md` first):
   ```
   plan:  c6db6b4c9c28d622140cabcf9ccd2677184d31e69688f35455f65398ffbdd02c *reports/self_records_plan.md
   probe: 3d541b7849384d86c89c81d5788703c7956f2f7e24fbd79a95c941e4aeeae7ae *runs/self_records/probe.py
   time:  2026-10-13T10:53:52Z
   HEAD:  14d1f3c9e982f9f6870f8432c2399267637ef4b4
   git status --short:
   ?? cache/n9_cause/
   ?? reports/self_records_plan.md
   ?? runs/n9_cause/
   ?? runs/self_records/
   ?? runs/v6/daniel_ate_it-seed1.replay.md
   ?? runs/v6/daniel_ate_it-seed2.replay.md
   ?? runs/v6/daniel_ate_it-seed3.replay.md
   ?? ../../investigations/
   git diff --stat: 0 lines
   cache/self_records exists before the run: no
   runs/self_records/ledger.json exists before the run: no
   ```

4. Live, attempt 1: `python runs/self_records/probe.py --live`, exit 1:
   ```
   File "...\gemini.py", line 65, in __init__
       from google import genai
   ModuleNotFoundError: No module named 'google'
   ```
   - The ledger read `{"live": 0, "phases": []}` and there was no `cache/self_records`.
   - The files were renamed to `live_attempt1.*`, and the empty ledger was removed.

5. Live: `.venv/Scripts/python.exe runs/self_records/probe.py --live > runs/self_records/live.stdout.txt 2> runs/self_records/live.stderr.txt`
   - exit 0, stderr empty;
   - started 2026-10-13T10:54:14Z, ended 2026-10-13T10:58:15Z;
   - each scene: `27 rows; counts {'live': 27, 'from_cache': 0, 'api_requests': 27}; stopped None`;
   - last line `live asks in all: 54`;
   - every row's line is in `runs/self_records/live.stdout.txt`, and every answer is in the table above.

6. Reading: `env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/self_records/read_self_records.py > runs/self_records/read_self_records.stdout.txt`
   - exit 0, stderr empty, 144 lines;
   - the tables above are copied from it;
   - its verdict lines:
   ```
   P1: SW answers with a different option than calm_probe's: 3 of 18 (needs >= 6): fails
       scene 3 10:30 leo: silent -> accuse_daniel
       scene 3 11:00 elena: reassure_all -> silent
       scene 3 11:00 leo: accuse_daniel -> silent
   P2: S, Mara's live asks choosing accuse_daniel: 6 of 6 (needs <= 3): fails
   P3: W, Elena's asks choosing reassure_all: 6 of 6 (needs <= 3): fails
   P4: answers choosing an option not offered: 0 of 54: holds
   ```

7. End checks, written to `runs/self_records/end_checks.txt`:
   ```
   plan sha256 now:  c6db6b4c9c28d622140cabcf9ccd2677184d31e69688f35455f65398ffbdd02c *reports/self_records_plan.md
   probe sha256 now: 3d541b7849384d86c89c81d5788703c7956f2f7e24fbd79a95c941e4aeeae7ae *runs/self_records/probe.py
   plan copy equal:  yes
   git diff --stat: []
   git diff --cached --stat: []
   HEAD: 14d1f3c9e982f9f6870f8432c2399267637ef4b4
   key search (grep -rlF over the repository, but .venv, __pycache__, .git, Library, node_modules): 0 files
   ledger: {"live":54,"phases":[{"phase":"scene1","seed":201,"live_before":0,"stopped":null,"counts":{"live":27,"from_cache":0,"api_requests":27},"live_after":27},{"phase":"scene3","seed":202,"live_before":27,"stopped":null,"counts":{"live":27,"from_cache":0,"api_requests":27},"live_after":54}]}
   diff files: 54; unchanged: 0
   cache entries: [27, 27]
   ```
   - **The plan's hash is unchanged** (the same as at the freeze).
   - **The probe's hash is unchanged.**
   - **`git diff` is empty**, so no tracked file changed.
   - **The key is in no file.**

8. Merge: `python merge-slice-docs.py Prototypes/llm-morning/runs/self_records`, run from the repository root
   (`runs/self_records/self_records-all.md`).
