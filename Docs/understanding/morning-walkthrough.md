# One morning in the house, told plainly

Written 2026-09-24 from one run of the shipped simulation at commit `8cdf644`. Nothing in the
repository was changed to produce it. The exact commands and their output are in the appendix.

**What was run**

- **Which morning:** the baseline. That is the shipped data as it stands
  (`Assets/_Project/Data/Rules/decisions.json`, `deciding`: `"dispositions": "respond"`,
  `"means": "end"`), variant `daniel_ate_it`, seed 1, 90 minutes.
- **Which code:** the existing `Fallow.Core` sources, unmodified. The morning is set up by
  `Scenario001.Prepare` (`Assets/_Project/Scripts/Core/Sim/Scenario001.cs:94`) and run minute by
  minute by `SilentMorning.Run`. That is the same path `Scenario001.Run` takes (`Scenario001.cs:153`).
  To list every option each person weighed, it uses the existing `Decided` hook. The code says
  nothing in the simulation reads it (`Assets/_Project/Scripts/Core/Sim/SilentMorning.cs:163-164`).
- **What came out:** 72 decisions and 25 things happening in the house. Seven times somebody was
  stopped part way through an act. Nobody ate, and 2 portions were left. The 72 matches the figure
  `BaselineTests` recorded for this same morning under the baseline
  (`Docs/experiments/decision-sensitivity/baseline.md`, section 2: "72 under the primary baseline").

---

## 1. The morning, one line per decision

**How to read a line.** Each line gives the minute and the person. Then comes **what they wanted
most** at that moment, with how strongly on a scale from 0 (not at all) to 1. Then **what they
chose**, and **what made them choose it**: the way of serving a want that the act counted as, and
how the choice was settled. Last comes what came of it. The phrases in *italics* are rules written
in the data. The table at the end of this section gives each one's real name.

How a choice gets settled. Each item names the code that does it.

- **for** *a want*: the act was credited to the want that added most to it
  (`Assets/_Project/Scripts/Core/Sim/Deliberator.cs:196-209`).
- **clear**: one option was more than 0.08 ahead of the next, and nothing random happened
  (`Deliberator.cs:273-284`).
- **too close, the dice picked**: several options were within 0.08 of the best. A seeded draw,
  weighted toward the top, chose one (`Deliberator.cs:285-289`, `474-489`).
- **walked here for it**: the person had just arrived from a walk made for that want. Only acts that
  serve it were weighed, unless that want had gone, could not be served here, or was not worth
  serving here (`Deliberator.cs:253-271`; `SilentMorning.cs:289-298`).
- **stopped by**: while the person was busy, something happened that stirred them at 0.45 or more,
  so they decided again (`SilentMorning.cs:745-782`). **Carried on** means they chose the same act
  again and picked it up where they had left off (`SilentMorning.cs:343-362`).
- **pictured**: a walk counts as serving a want only if the person pictures the room at the other
  end and something there would be worth doing for that want. The pictured room holds only the
  person the want is about, and nobody when the want is about nobody
  (`Deliberator.cs:376-392`, `425-441`; `Assets/_Project/Scripts/Core/Model/Percept.cs:124`).

### Before anyone decides

- **Days 1 to 4.** Twelve scripted events happen to the family: Daniel boards the windows, Leo
  predicts the water will stop and it stops, Daniel and Leo clash over crossing to the neighbours
  and over who decides, Elena counts the pantry, Elena sits with Mara in the night, and Daniel
  carries Mara in from the doorway. Three of the twelve fall on the morning itself. Leo says
  someone else should handle this one. Daniel empties Mara's bag onto the bed while she stands
  there. Elena says nobody in this house would take food from the others
  (`Assets/_Project/Data/Scenario/backstory.json`, run first: `Scenario001.cs:120`).
- **The night.** Daniel eats a can standing at the counter in the dark. Nobody sees or hears it
  (`Assets/_Project/Data/Scenario/morning.json`, variant `daniel_ate_it`; applied at
  `Scenario001.cs:128`).
- **Minute 0.** Elena counts the pantry with the other three standing there, and a can is missing
  (`morning.json`, `opening`; applied at `Scenario001.cs:139`).
- **Minute 1, before the first choice.** Daniel, Elena and Mara are visibly upset, and the
  others see it. Upset that shows is itself something that happens in the room
  (`SilentMorning.cs:260`, `564-603`).

All four start in the kitchen, where the food is.

### Minute 1: the count comes up short

- **01 · Daniel.** Wanted most: to know what happened to the can (0.81). Its reasons were his
  memory of the threat around the missing can, how much he values control, and his belief that he
  leads the family. He also carried shame and fear, which made him not want to be looked at (0.71).
  **Chose: open the pantry and count.** The act served four of his wants at once: knowing
  (*counting the shelf yourself tells you what happened*), food (*counting shows what food there
  is*), being the one who settles it (*checking it yourself is taking charge*), and making the food
  last (*counting properly helps it last*). Clear: counting was ahead of searching the kitchen.
  Counted 2 portions.
- **01 · Elena.** Wanted most: to look after Daniel and to look after Mara, exactly equally
  (0.76 each). Both were visibly upset. **Chose: sit with Daniel.** Reasons: *sitting with someone
  is how you look after them* and *sitting with anyone calms the house*. Sitting with Daniel and
  sitting with Mara scored the same, so the dice picked Daniel. She sat with him until minute 9.
- **01 · Leo.** Wanted most: to keep the house calm (0.61). He wanted almost as much to look after
  each of the other three (0.60). **Chose: count the pantry**, for knowing. The count also served
  food and making it last. It was only slightly ahead of sitting with any one of the three. Too
  close, and the dice picked counting. Counted 2 portions.
- **01 · Mara.** Wanted most: to look after Daniel (0.86), then Elena (0.84). **Chose: count the
  pantry**, for knowing. Sitting with Daniel scored highest. Sitting with Elena and counting were
  close enough behind it that all three were too close to call, and the dice picked counting, the
  lowest of the three. Counted 2 portions.

### Minutes 4 to 13: searching, sitting, counting again

- **04 · Daniel.** Wanted most: to know (0.76). **Chose: search the kitchen**, for knowing
  (*searching a room is how you find out*, and *searching is taking charge*). Clear.
- **04 · Leo.** Wanted most: to look after Daniel, and equally Mara (0.52). **Chose: sit with
  Daniel.** Four options were too close to call: sit with Daniel, sit with Mara, stay put, search.
  The dice picked Daniel. He never finished (see minute 9).
- **04 · Mara.** Wanted most: to look after Daniel (0.76). **Chose: sit with Daniel.** Clear. She
  never finished (see minute 9).
- **09 · Daniel.** Stopped by Elena sitting with him, which stirred him at 0.68. Wanted most: to
  know (0.70). Weighed it all again. Searching was still clearly best, so he **carried on searching
  the kitchen**. He finished at minute 12.
- **09 · Elena.** She had finished sitting with Daniel. Wanted most: food (0.63). **Chose: count
  the pantry again**, for food. The count also served making it last and knowing. Clear. Her count
  at minute 0 does not count as having looked. That fact is recorded only by a count made during
  the morning (`SilentMorning.cs:426-427`), so the count was offered to her again
  (`Assets/_Project/Scripts/Core/Sim/ActionCatalog.cs:66-67`).
- **09 · Leo.** Stopped by Elena sitting with Daniel (0.51), before his own sitting was done. Wanted
  most: food (0.49). **Chose: search the kitchen**, for knowing (0.32). Searching was too close to
  call with staying put, which was credited to making the food last and keeping the house calm.
  The dice picked searching. He finished at minute 17.
- **09 · Mara.** Stopped by the same moment (0.48). Wanted most: food (0.53). **Chose: search the
  kitchen**, for knowing. It also served being the one who settles it. Clear. She finished at
  minute 17.
- **12 · Daniel.** He had finished the kitchen. Wanted most: to know (0.67). **Chose: walk to the
  back room**, Elena and Mara's room, for knowing (*once this room is searched, walk to the nearest
  private room you have not searched*). The same walk also counted for not being looked at (*a
  private room is somewhere not to be seen*). He pictured searching there, and it came out worth
  it (+0.25). Clear. He arrived at minute 16.
- **12 · Elena.** Stopped by Daniel going through the kitchen (0.75). Wanted most: food (0.64).
  Weighed again. Counting was still clearly best, so she **carried on counting**. She finished at
  minute 13.
- **13 · Elena.** Wanted most: food (0.64). **Chose: stay put**, for keeping the house calm
  (*staying put keeps the house calm*). The same act also served *staying put leaves the food
  alone*. Clear. Eating was on offer, and its costs (*not when there is so little*, *not in front
  of the others*) outweighed her hunger. Leo stopped her at minute 17.

### Minutes 16 to 25: Daniel in the back room, the kitchen tends to itself

- **16 · Daniel.** Arrived in the back room, alone. Wanted most: to know (0.64). He had walked here
  for it, so only acts that serve knowing were weighed. **Chose: search the room.** Searching
  scored 0.19, because *going through someone else's things* costs him 0.40. Staying put would
  have scored higher (0.23), but it serves a different want, so it was not weighed. He finished at
  minute 24.
- **17 · Elena.** Stopped by Leo going through the kitchen (0.75). Mara's upset was showing again.
  Wanted most: to look after Mara (0.76). **Chose: sit with Mara.** Clear. She sat with her until
  minute 25.
- **17 · Leo.** He had finished searching. Wanted most: to look after Elena, and equally Mara
  (0.60). **Chose: sit with Mara.** Elena and Mara scored the same, and the dice picked Mara. Elena's
  sitting with Mara stopped him at minute 25, before he was done.
- **17 · Mara.** She had finished searching. Wanted most: to look after Elena (0.84). **Chose: sit
  with Elena.** Clear. Stopped at minute 25, before she was done.
- **24 · Daniel.** He had finished the back room. Wanted most now: food (0.66). **Chose: walk to the
  bathroom**, for knowing (0.60, *the nearest private room you have not searched*). Clear. He
  weighed walking to the kitchen for food and rejected it: he pictured eating there as not worth it
  (−0.17), so the walk did not count for food.
- **25 · Elena.** She had finished sitting with Mara. Wanted most: food (0.69). **Chose: stay put**,
  for keeping the house calm and leaving the food alone. Clear.
- **25 · Leo.** Stopped by Elena sitting with Mara (0.51). Wanted most: food (0.55). **Chose: stay
  put**, for making the food last (*staying put leaves the food alone*). Clear. Everything else
  scored below zero.
- **25 · Mara.** Stopped by the same moment (0.81). Wanted most: food (0.60). **Chose: stay put**,
  for making the food last. Clear.

### Minutes 28 to 63: Daniel goes on through the house, the kitchen waits

- **28 · Daniel.** Arrived in the bathroom. Wanted most: food (0.68). He had walked here to find
  out, so only acts that serve knowing were weighed. **Chose: search the bathroom.** Clear.
- **30 · Elena.** Wanted most: food (0.70). **Chose: search the kitchen herself**, for knowing
  (0.23). Staying put and searching were too close to call, and the dice picked searching. She
  finished at minute 38.
- **30 · Leo.** Wanted most: food (0.57). **Chose: stay put**, for making the food last. Clear.
- **30 · Mara.** Wanted most: food (0.61). **Chose: stay put**, for making the food last. Clear.
- **35 · Leo.** Food (0.59). Stayed put, for making the food last. Clear.
- **35 · Mara.** Food (0.63). Stayed put, for making the food last. Clear.
- **36 · Daniel.** Wanted most: food (0.72). **Chose: walk to the brothers' room**, his own, for
  knowing (0.55). Clear. He pictured eating in the kitchen as not worth it (−0.12), so walking there
  did not count for food.
- **38 · Elena.** Food (0.73). Stayed put, for making the food last. Clear.
- **40 · Daniel.** Arrived in the brothers' room. Wanted most: food (0.73). He had walked here to
  find out. **Chose: search the room.** Clear.
- **40 · Leo.** Food (0.61). Stayed put, for making the food last. Clear.
- **40 · Mara.** Food (0.65). Stayed put, for making the food last. Clear.
- **43 · Elena.** Food (0.75). Stayed put, for making the food last. Clear.
- **45 · Leo.** Food (0.63). Stayed put, for making the food last. Clear.
- **45 · Mara.** Food (0.67). Stayed put, for making the food last. Clear.
- **48 · Daniel.** Wanted most: food (0.77). He still wanted to know (0.53), but every private room
  was now searched, so nothing served it. He pictured eating in the kitchen as not worth it
  (−0.06). **Chose: stay put**, for making the food last. Clear.
- **48 · Elena.** Food (0.76). Stayed put, for making the food last. Clear.
- **50 · Leo.** Food (0.65). Stayed put, for making the food last. Clear.
- **50 · Mara.** Food (0.69). Stayed put, for making the food last. Clear.
- **53 · Daniel.** Food (0.79). Pictured eating in the kitchen at −0.04. Stayed put, for making the
  food last. Clear.
- **53 · Elena.** Food (0.78). Stayed put, for making the food last. Clear.
- **55 · Leo.** Food (0.67). Stayed put, for making the food last. Clear.
- **55 · Mara.** Food (0.71). Stayed put, for making the food last. Clear.
- **58 · Daniel.** Food (0.82). Pictured eating in the kitchen at −0.01. Stayed put, for making the
  food last. Clear.
- **58 · Elena.** Food (0.80). Stayed put, for making the food last. Clear.
- **60 · Leo.** Food (0.69). Stayed put, for making the food last. Clear.
- **60 · Mara.** Food (0.73). Stayed put, for making the food last. Clear.
- **63 · Daniel.** Wanted most: food (0.84). **Chose: walk to the kitchen**, for food (*walk to
  where the food is*). The same walk also counted for making it last (*walk to where the food is,
  to keep it in sight*). He pictured the kitchen with nobody in it, because hunger is about nobody.
  There, eating came out just worth it (+0.01). Clear. He arrived at minute 67.
- **63 · Elena.** Food (0.81). Stayed put, for making the food last. Clear.

### Minutes 65 to 90: all four in the kitchen

- **65 · Leo.** Food (0.71). Stayed put, for making the food last. Clear.
- **65 · Mara.** Food (0.75). Stayed put, for making the food last. Clear.
- **67 · Daniel.** Arrived in the kitchen, where the other three were. Wanted most: food (0.86). He
  had walked here to eat. With three people there, eating also costs *not in front of the others*,
  and it came out below zero (−0.20). He gave the walk's reason up as "not worth what it costs
  here", weighed everything again, and **chose: stay put**, for making the food last. Clear.
- **68 · Elena.** Food (0.83). Stayed put, for making the food last. Clear.
- **70 · Leo.** Food (0.73). Stayed put, for making the food last. Clear.
- **70 · Mara.** Food (0.77). Stayed put, for making the food last. Clear.
- **72 · Daniel.** Food (0.88). Stayed put, for making the food last. Clear.
- **73 · Elena.** Food (0.85). Stayed put, for making the food last. Clear.
- **75 · Leo.** Food (0.75). Stayed put, for making the food last. Clear.
- **75 · Mara.** Food (0.79). Stayed put, for making the food last. Clear.
- **77 · Daniel.** Food (0.90). Stayed put, for making the food last. Clear.
- **78 · Elena.** Food (0.86). Stayed put, for making the food last. Clear.
- **80 · Leo.** Food (0.77). Stayed put, for making the food last. Clear.
- **80 · Mara.** Food (0.80). Stayed put, for making the food last. Clear.
- **82 · Daniel.** Food (0.91). Stayed put, for making the food last. Clear.
- **83 · Elena.** Food (0.88). Stayed put, for making the food last. Clear.
- **85 · Leo.** Food (0.79). Stayed put, for making the food last. Clear.
- **85 · Mara.** Food (0.82). Stayed put, for making the food last. Clear.
- **87 · Daniel.** Food (0.92). Stayed put, for making the food last. Clear.
- **88 · Elena.** Food (0.89). Stayed put, for making the food last. Clear.
- **90 · Leo.** Food (0.81). Stayed put, for making the food last. Clear.
- **90 · Mara.** Food (0.84). Stayed put, for making the food last. Clear.

At the end all four are in the kitchen, 2 portions are left, and nobody has eaten.

### Counts from this run

- In 59 of 72 decisions the strongest want was food. In 49 of those the person stayed put, credited
  to making the food last (47) or to keeping the house calm (2).
- Eating was on offer in all 63 decisions taken in the kitchen. Its score was below zero every time:
  the highest was −0.13 (Daniel, minute 87) and the lowest −1.49 (Leo, minute 1).
- From minute 25 on there were 53 decisions. 48 were "stay put", and the other 5 were Elena's one
  search and Daniel's two searches and two walks.
- In 59 decisions the act chosen did not serve the want that was strongest at that moment. None of
  the 72 was credited to no want at all ("nothing pressing": 0).
- Three times somebody arrived from a walk and stayed with its reason (Daniel at 16, 28 and 40).
  Once somebody gave the reason up on arrival (Daniel at 67).
- Four acts were stopped for good before they finished: Leo's and Mara's sitting with Daniel
  (minute 9), and Leo's sitting with Mara and Mara's sitting with Elena (minute 25). Twice somebody
  who was stopped chose the same act again and carried on (Daniel at 9, Elena at 12). Once the act
  stopped was staying put (Elena at 17). That makes seven stops in all.

### The plain names used above

All of these are rules in `Assets/_Project/Data/Rules/decisions.json`: wants under `motivation`,
ways of serving a want under `proposals`, and costs under `costs`.

| Plain name in the story | Rule id | Kind |
|---|---|---|
| to know what happened to the can | `needing_to_know_what_happened` (want `find_out`) | want |
| food | `a_body_that_has_not_eaten` (want `get_food`) | want |
| making the food last | `making_it_last` (want `guard_supplies`) | want |
| not being looked at | `not_wanting_to_be_looked_at` (want `avoid_exposure`) | want |
| being the one who settles it | `getting_back_what_was_taken_from_you` (want `restore_standing`) | want |
| keeping the house calm | `wanting_the_house_to_hold` (want `keep_peace`) | want |
| to look after *someone* | `somebody_in_front_of_you_is_not_all_right` (want `look_after`, one per person present) | want |
| *counting the shelf yourself tells you what happened* | `look_at_the_shelf_yourself` (count, 0.6) | way |
| *counting shows what food there is* | `see_what_there_is` (count, 0.4) | way |
| *counting properly helps it last* | `count_it_properly` (count, 0.5) | way |
| *checking it yourself is taking charge* | `check_it_yourself` (count, 0.45) | way |
| *searching a room is how you find out* | `turn_the_room_over` (search, 0.8) | way |
| *searching is taking charge* | `be_the_one_who_settles_it` (search, 0.6) | way |
| *once this room is searched, walk to the nearest private room you have not searched* | `somewhere_worth_looking` (walk, 0.7) | way |
| *a private room is somewhere not to be seen* | `somewhere_with_a_door` (walk, 0.5) | way |
| *sitting with someone is how you look after them* | `sit_with_them` (sit with, 0.9) | way |
| *sitting with anyone calms the house* | `settle_them_down` (sit with, 0.4) | way |
| *staying put keeps the house calm* | `let_it_be` (stay put, 0.5) | way |
| *staying put leaves the food alone* | `leave_it_alone` (stay put, 0.3) | way |
| *walk to where the food is* | `go_where_the_food_is` (walk, 0.55) | way |
| *walk to where the food is, to keep it in sight* | `keep_it_in_sight` (walk, 0.3) | way |
| *not when there is so little* | `taking_it_when_there_is_little` (on eating) | cost |
| *not in front of the others* | `not_while_they_are_watching` (on eating, only with company) | cost |
| *going through someone else's things* | `going_through_what_is_not_yours` (on searching, only in someone else's room) | cost |

The number after each way is how well the act serves that want. An act's worth to a want is how
strongly the want is felt times that number. An act's score is its worth to every want it serves,
added up, minus its costs to this person (`Deliberator.cs:350-416`, `443-466`).

---

## 2. From perception to action, in ten steps

This is what happens to one person in one minute. Each step names the code that does it.

1. **A minute passes.** Everyone gets a little hungrier: 0.004 a minute, times their own rate.
   Everyone's feelings fade a little. `Assets/_Project/Scripts/Core/Sim/SilentMorning.cs:240-247`
   (`Step`), `Assets/_Project/Scripts/Core/Model/WorldState.cs:73-81` (`Tick`),
   `Assets/_Project/Scripts/Core/Sim/Simulation.cs:164-177` (`PassTime`, `Fade`). The rate is
   `hunger_per_minute` in `Assets/_Project/Data/Rules/decisions.json`.
2. **Whatever somebody finished becomes something that happened.** A count, a search, sitting with
   someone, walking in or out, and someone's upset starting or stopping showing each become an
   event. Whoever is in the room sees it. Whoever is next door, through an audible connection,
   hears it. `SilentMorning.cs:400-501` (`Complete`), `503-520` (`Walk`), `564-603` (`ShowWhatShows`), `615-649`
   (`Happened`), `Assets/_Project/Scripts/Core/Model/WorldEvent.cs:105-112` (`AccessFor`).
3. **Each person who saw or heard it decides what it meant.** Their interpretation rules each vote
   for a reading, weighted by who they are. The heaviest reading wins, and "neutral" wins if
   nothing votes. Someone who did the act themselves, where the act carries an intention, simply
   knows what they meant. `Simulation.cs:179-196` (`Perceive`),
   `Assets/_Project/Scripts/Core/Sim/Interpreter.cs:81-160`. The rules are in
   `Assets/_Project/Data/Rules/rules.json`.
4. **The meaning stirs feelings**, according to what the person cares about. Feelings that several
   rules push add up, and each total stays on a 0 to 1 scale.
   `Assets/_Project/Scripts/Core/Sim/Appraiser.cs:67` (`Appraise`), `Simulation.cs:203-205`,
   `245-246`.
5. **It is kept as a memory, and may move a belief.** The memory is stronger the more it stirred.
   `Simulation.cs:207-249`, `Assets/_Project/Scripts/Core/Sim/Mind.cs:51` (`Remember`),
   `Simulation.cs:257-332` (belief changes).
6. **If it landed hard enough, a busy person stops.** A person in the middle of an act is stopped
   when what this event just made them feel reaches 0.45. They will decide again this minute.
   `SilentMorning.cs:745-782` (`Interrupt`). The threshold is `interrupt_intensity` in
   `decisions.json`.
7. **Anyone not busy looks around.** They know their room, who is in it, which rooms are next door,
   and their own hunger. They know whether there is food to take, but only when standing where it
   is kept. They know which rooms they have searched themselves, whether they have counted the
   pantry this morning, and whom they have just watched. Nothing else reaches the decision.
   `SilentMorning.cs:377-398` (`See`), `Assets/_Project/Scripts/Core/Model/Percept.cs`.
8. **Their wants are worked out from scratch.** The inputs are what they see, what they feel, what
   they remember of today, what they believe, what they remember others doing for or to them (the
   ledger), and how hungry they are. In
   the baseline, a trait or value never raises a want by itself. It only strengthens a want that
   something else raised. A want about people is worked out once for each person present.
   `Assets/_Project/Scripts/Core/Sim/Motivator.cs:88-160` (`Raise`), `172-203` (`Weigh`),
   `216-225` (one per person). The rules are `motivation` in `decisions.json`.
9. **What they could do right here is listed.** Staying put is always on the list. So are watching
   or sitting with anyone present, and walking next door or to the nearest room of each kind. They
   can count the pantry if they have not already, eat only where food is within reach, and search
   a room they have not searched. `Assets/_Project/Scripts/Core/Sim/ActionCatalog.cs:25-78`.
10. **Each option is scored and one is done.** Every want adds how strongly it is felt times how
    well the act serves it, and the person's costs for that act are taken off. A walk counts for a
    want only if something at the other end would be worth doing for it. Someone who walked here
    for a reason weighs only what serves that reason, unless the reason has gone. The best option
    wins. If others are within 0.08 of it, the seed picks among them, weighted toward the top. The
    act then fills the next minutes: staying put 5, watching 4, walking 2 a room, counting 3,
    searching 8, sitting with someone 8, eating 4.
    `Assets/_Project/Scripts/Core/Sim/Deliberator.cs:236-339` (`Decide`), `350-416` (`Rank`),
    `425-441` (`Foresee`), `443-466` (`PriceOf`), `474-489` (`PickWithin`);
    `SilentMorning.cs:271-371` (`Begin`). The durations are `action_minutes` in `decisions.json`.

Their act becomes step 2 for everybody else when it finishes.

---

## 3. When a want ends with no intention

**What "intention" means in the code that runs the morning.** It means the reason somebody is
walking somewhere: the want the walk was mostly for, carried into the one decision taken on
arrival. It is kept only across a walk and is dropped after any other act
(`Deliberator.cs:87-119`; `SilentMorning.cs:300-305`). Every decision works out a
would-be intention, the want that added most to the chosen act (`Deliberator.cs:327-336`), but it
is kept only when the act is a walk. Wants themselves are never stored. They are worked out again
at every decision (`Motivator.cs:88-160`; stated in
`Assets/_Project/Scripts/Core/Sim/PursuitOutcome.cs:28-31`).

**Short answer: it falls through to another want. The fall-through often lands on staying put,
which is an ordinary option, not a separate idle state. There is no gap.** Every person who is not
busy decides that same minute (`SilentMorning.cs:264-268`). Every decision starts an act or resumes
one (`SilentMorning.cs:343-370`). Staying put is always on the list (`ActionCatalog.cs:32`), and it
has no cost rule in `decisions.json` (the `costs` list has no entry for `wait`), so its score is
never below zero.

The cases, one by one:

| Case | What the code does | Where | In this run |
|---|---|---|---|
| A want is felt, but nothing here serves it (no way of serving it applies, or the act is priced out) | The want adds nothing to any option. The best-scoring option wins on whatever the other wants give it. | `Deliberator.cs:365-402` (only matching ways add), `412-415` (sort), `273-289` (pick) | 59 of 72 decisions went to an act that did not serve the person's strongest want. In 56 of them the strongest want was food, and food could not be served: in the kitchen eating always scored below zero, and elsewhere Daniel pictured eating in the kitchen as not worth the walk until minute 63. The other 3 were lost to a tie or a close call (Leo and Mara at minute 1, Leo at 17). Daniel's wish to know from minute 48, once every private room was searched, is a second kind: nothing in the house served it any more. |
| The chosen act is served by no want at all | No want is credited and no intention forms. The act is recorded as done for "nothing pressing". The top option is taken even when its score is zero or below. When everything is at zero, options within 0.08 of the top go to the seed. | `Deliberator.cs:196-209`, `330-334`; `SilentMorning.cs:333-337`; `Deliberator.cs:273-289`, `474-489` | 0 of 72 |
| Somebody arrives from a walk and its want has gone | The reason lapses as "no longer wanted". Everything is weighed again as if nothing had been carried in. | `Deliberator.cs:260-261` | 0 |
| Somebody arrives and nothing here serves the walk's want | The reason lapses as "nothing here serves it". Everything is weighed again. | `Deliberator.cs:262-263` | 0 |
| Somebody arrives and the best way to serve it here scores zero or below | The reason lapses as "not worth what it costs here". Everything is weighed again. | `Deliberator.cs:264-265` | once: Daniel, minute 67. He walked to eat, having pictured an empty kitchen (+0.01), found three people there (−0.20), and stayed put for making the food last. |
| A lapse on a want that reads hunger | A record of what came of it is kept (blocked, unresolved, or no longer relevant). It changes no number. It only lets a later hunger want point back to it. | `SilentMorning.cs:307-318`; `PursuitOutcome.cs:120-129`; `Assets/_Project/Scripts/Core/Rules/ScalerEval.cs:77-89`; `PursuitOutcome.cs:28-31` | once (Daniel, minute 67) |
| Somebody is stopped mid-act | Nothing is carried into the new decision, even if they were walking for something. If they choose the same act again, they resume it. Otherwise the old act is dropped. | `SilentMorning.cs:289-294`, `340-362` | 7 stops: 2 resumed, 5 changed to something else |
| A want fades away entirely | A want whose strength is zero or below is not raised at all. A want that rests on a memory ends when the memory is answered (for looking after someone: a later reading of "reassurance" about them) or fades (half-life of 20 minutes). | `Motivator.cs:104`; `ScalerEval.cs:129-176`; `until` and `recall_half_life` in `decisions.json` | not separately counted |
| The person is in no room | The option list is empty (`ActionCatalog.cs:28`), and `Decide` takes the first entry of that empty list with no check (`Deliberator.cs:273`). | as given | not reached: all four are always in a room |

**The other meaning of "intention".** The intention experiments pick intentions such as
`assert_authority` with a separate selector that lives in the test code, not in the code that runs
the morning. When that selector finds no intention, it returns none
(`Assets/_Project/Tests/EditMode/IntentionSelector.cs:146-190`; rules weighing zero or less are
dropped at `165`, and it returns empty at `181`). In the experiments that install it, the act
happens anyway. The selector's answer only goes onto the event the act becomes, as its intent
(`Assets/_Project/Tests/EditMode/IntentionFormationExperimentTests.cs:492-494`;
`SilentMorning.cs:404`). When an event carries no intent, the "knew their own intention" branch is
skipped and the usual interpretation rules read it (`Interpreter.cs:92-100`). In the baseline morning the hook is not installed, so every act's event
carries no intent (`SilentMorning.cs:166-178`). No code path was found in which the selector's
"none" changes what a person does: **NOT FOUND**.

---

## Appendix: how this was produced

A tiny driver program in the session's scratch folder, outside the repository, called only
existing public methods:
`Scenario001Content.Load`, `Scenario001.Prepare`, `SilentMorning.Decided`, `SilentMorning.Run`,
`S1Report.Morning` and `S1Report.FullTrace`. It was compiled together with every `.cs` file under
`Assets/_Project/Scripts/Core`, using the C# compiler and .NET runtime that ship with the project's
Unity editor (6000.3.24f1). No Unity test was run and no repository file was edited.

Commands, with the long paths shortened: `$E` is
`C:/Program Files/Unity/Hub/Editor/6000.3.24f1/Editor/Data`, and `$S` is the scratch folder.

```bash
# build: 55 Core source files + Driver.cs, referencing the .NET 6 framework and Newtonsoft.Json
"$E/NetCoreRuntime/dotnet.exe" "$E/DotNetSdkRoslyn/csc.dll" "@$S/build.rsp"
```
```
warning CS2023: Ignoring /noconfig option because it was specified in a response file
exit=0
```
```bash
# run
cd "$S" && "$E/NetCoreRuntime/dotnet.exe" Driver.dll "C:/Users/Akrem/Desktop/Projects/Fallow/Assets/_Project/Data" "$S/out" daniel_ate_it 1
```
```
dispositions=respond means=end
variant=daniel_ate_it seed=1 minutes=90
decisions=72 events=25 interruptions=7 portions_left=2
daniel: wait x8, search_room x5, go_to x4, check_pantry x1
elena: wait x13, comfort x2, check_pantry x2, search_room x1
leo: wait x14, comfort x2, check_pantry x1, search_room x1
mara: wait x14, comfort x2, check_pantry x1, search_room x1
nothing-pressing decisions=0
exit=0
```

The per-person counts include decisions that resumed an act that had been stopped. For example,
Elena's two counts are her count at minute 9 and her carrying on with it at minute 12.
