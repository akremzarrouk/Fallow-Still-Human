# Target morning: what a believable run looks like

This is not a script. It describes the range of mornings we accept for the
scenario `daniel_ate_it`, and it is the standard every change is judged
against: run the narrator, read the story, check it against this file.

## The family

- Elena, 42, the mother. She controls the food.
- Daniel, 25, the eldest. He ate the can in the night, alone, unseen.
- Leo, 21. He clashed with Daniel in the days before over who decides.
- Mara, 17, the youngest.

Nobody else. No zombies yet: the family's behaviour must be believable first.

## 1. Never (a run with any of these is wrong)

- A person acts as if they do not know what they did. Daniel does not try to
  "find out" what happened to the can he ate.
- A person checks something they just watched someone else check, for the
  same reason (three people counting the shelf Elena just counted).
- A person keeps a fact from their own earlier act as if it never happened
  (Elena counting again because her first count "does not count").
- A person sits with someone who is busy searching, walking or leaving.
- A person stops comforting someone because another family member joins them,
  instead of staying or joining.
- After the missing can is discovered, nobody says anything.
- A person pictures a room as empty when they left people in it.
- An important social choice (who to comfort, who to suspect) is settled by
  chance alone when the people involved differ in ways that should matter.
- Long stretches where everyone does nothing and nothing about them changes
  in a way the story can show.
- Everyone speaks at once and nobody answers the line before theirs.
- A person repeats the same kind of line many turns in a row with no effect.
- Someone who was wronged forgives within minutes, with no lasting cost.
- A person mentions objects or places the house does not have.

## 2. Possible (each run should show some of these, never all by force)

- Elena asks aloud who took the can.
- Daniel lies, deflects or stays quiet, and shows it: avoids looking at
  people, avoids Elena, avoids the kitchen or the food.
- Daniel offers to search, to look innocent rather than to find anything.
- Leo gets defensive ("don't look at me") or suspects Daniel.
- Mara is scared or upset; she may defend someone, cry, or ask them to stop.
- Elena tries to hold the family together ("we share what's left, nobody eats
  alone").
- Hunger is handled by a rule or an arrangement (Elena decides when and how
  portions are shared), not by everyone standing still.
- Someone questions Daniel directly, and that becomes a turning point.
- Daniel confesses (more likely if honest and weighed down by guilt).
- Daniel blames Leo or someone else (more likely if proud and afraid).

## 3. Should vary (between seeds and between personalities)

- What Daniel does: silence, confession, or blaming someone.
- Who suspects whom, and whether anyone suspects Daniel at all.
- Whether and when the food is shared, and who decides.
- Who comforts whom, for a reason the story can name.

If every run tells the same story, the simulation is a script. If runs differ
only by chance and not by who the people are, it is noise.

## How to judge a change

1. Run the narrator on `daniel_ate_it` with at least two seeds.
2. Count the "Never" items that appear. A change must not add any.
3. Note which "Possible" items appear.
4. A change is an improvement if Never items go down, or Possible items go up
   with no new Never items, and the story reads more like four real people.
5. The final judge is a human reading the story, not a metric.
