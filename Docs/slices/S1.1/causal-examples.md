# S1.1 causal examples

Found by `S11CausalExamplesTests`: the first seed on which the night changed a decision
and the want behind the changed decision leads back to the night. Chains are printed
by the trace tool as they are.

## mara_ate_it, mara, seed 1, minute 12

- **Without the night:** comfort:elena because `look_after:elena` (0.76)
- **With the night:** check_pantry because `find_out` (0.53)

The want that led the changed decision, and everything it rests on:

```
Motive [mara]: wants find_out 0.53  {motive=find_out, urgency=0.53, rules=needing_to_know_what_happened, because=memory of threat about missing_can 0.80 x 0.35 = +0.28; value fairness 0.5...
  because Access [mara]: at minute 12, mara in kitchen at minute 12, with daniel, elena, leo  {room=kitchen, present=daniel, elena, leo, hunger=0.55}
  because Experience [mara]: kept it as threat, felt as fear  {meaning=threat, source=witnessed, confidence=1.00, salience=0.80}
    because Interpretation [mara]: read it as threat (0.90)  {meaning=threat, weight=0.90, runner_up=concern 0.60, rules=bad_news_reads_as_a_problem -> concern 0.60 | the_search_is_for_wh...
      because Access [mara]: was there and saw it
        because Event: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not.
      because BeliefChange [mara]: answerable_for(mara,missing_can): 0.00 -> pending
        because Experience [mara]: kept it as took_what_was_not_mine, felt as fear  {meaning=took_what_was_not_mine, source=own intention, confidence=1.00, salience=0.76}
          because Interpretation [mara]: knew their own intention: took_what_was_not_mine  {meaning=took_what_was_not_mine, source=own intention}
            because Access [mara]: was there and saw it
              because Event: In the night Mara eats a can sitting on the kitchen floor.

```


## leo_ate_it, leo, seed 1, first minute (held-out)

- **Wish to be elsewhere:** 0.13 without the night, 0.55 with it
- **First decision without the night:** 1:check_pantry
- **First decision with the night:** 1:check_pantry

```
Motive [leo]: wants avoid_exposure 0.59  {motive=avoid_exposure, urgency=0.59, rules=not_wanting_to_be_looked_at, because=feeling shame 0.41 x 0.80 = +0.33; feeling fear 0.75 x 0.35 = +0.26}
  because Access [leo]: at minute 1, leo in kitchen at minute 1, with daniel, elena, mara
  because Appraisal [leo]: took_what_was_not_mine touched fairness: shame 0.71 (fairness)  {emotion=shame, concern=fairness, intensity=0.71, rules=what_you_did_in_the_night_is_felt_as_sha...
    because Interpretation [leo]: knew their own intention: took_what_was_not_mine  {meaning=took_what_was_not_mine, source=own intention}
      because Access [leo]: was there and saw it
        because Event: In the night Leo eats a can by the light of the open fridge, the one person nobody would suspect.
  because Appraisal [leo]: concern touched family_safety: fear 0.24 (family_safety)  {emotion=fear, concern=family_safety, intensity=0.24, rules=a_problem_is_felt_as_fear_by_the_fearful 0...
    because Interpretation [leo]: read it as concern (0.86)  {meaning=concern, weight=0.86, runner_up=support 0.53, rules=being_told_to_let_it_go -> challenge 0.44 (base 0.30; value contr...
      because Access [leo]: was there and saw it
        because Event: Elena says she is quite sure nobody in this house would take food from the others.
  because Appraisal [leo]: took_what_was_not_mine touched closeness: fear 0.30 (closeness)  {emotion=fear, concern=closeness, intensity=0.30, rules=and_as_being_afraid_of_what_they_will_t...
    because #284 Interpretation, shown above
  because Appraisal [leo]: threat touched family_safety: fear 0.28 (family_safety)  {emotion=fear, concern=family_safety, intensity=0.28, rules=a_threat_is_felt_as_fear 0.33 (base 0.15; t...
    because Interpretation [leo]: read it as threat (0.90)  {meaning=threat, weight=0.90, runner_up=concern 0.60, rules=bad_news_reads_as_a_problem -> concern 0.60 | the_search_is_for_wha...
      because Access [leo]: was there and saw it
        because Event: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not.
      because BeliefChange [leo]: answerable_for(leo,missing_can): 0.00 -> pending
        because Experience [leo]: kept it as took_what_was_not_mine, felt as shame  {meaning=took_what_was_not_mine, source=own intention, confidence=1.00, salience=0.82}
          because #284 Interpretation, shown above
  because Appraisal [leo]: concern touched family_safety: fear 0.24 (family_safety)  {emotion=fear, concern=family_safety, intensity=0.24, rules=a_problem_is_felt_as_fear_by_the_fearful 0...
    because Interpretation [leo]: read it as concern (1.42)  {meaning=concern, weight=1.42, rules=bad_news_reads_as_a_problem -> concern 0.60 | somebody_not_holding_it_together -> concern...
      because Access [leo]: was there and saw it
        because Event: Daniel is not hiding it well.
  because Appraisal [leo]: concern touched family_safety: fear 0.24 (family_safety)  {emotion=fear, concern=family_safety, intensity=0.24, rules=a_problem_is_felt_as_fear_by_the_fearful 0...
    because Interpretation [leo]: read it as concern (1.42)  {meaning=concern, weight=1.42, rules=bad_news_reads_as_a_problem -> concern 0.60 | somebody_not_holding_it_together -> concern...
      because Access [leo]: was there and saw it
        because Event: Elena is not hiding it well.
  because Appraisal [leo]: concern touched family_safety: fear 0.24 (family_safety)  {emotion=fear, concern=family_safety, intensity=0.24, rules=a_problem_is_felt_as_fear_by_the_fearful 0...
    because Interpretation [leo]: read it as concern (1.42)  {meaning=concern, weight=1.42, rules=bad_news_reads_as_a_problem -> concern 0.60 | somebody_not_holding_it_together -> concern...
      because Access [leo]: was there and saw it
        because Event: Mara is not hiding it well.

```

## elena_fed_mara, elena, seed 1, minute 60

- **Without the night:** wait because `keep_peace` (0.93)
- **With the night:** search_room because `find_out` (0.79)

The want that led the changed decision, and everything it rests on:

```
Motive [elena]: wants find_out 0.79  {motive=find_out, urgency=0.79, rules=needing_to_know_what_happened, because=memory of threat about missing_can 0.88 x 0.35 = +0.31; value fairness 0....
  because Access [elena]: at minute 60, elena in kitchen at minute 60, with daniel, leo, mara  {room=kitchen, present=daniel, leo, mara, hunger=0.80}
  because Experience [elena]: kept it as threat, felt as anxiety  {meaning=threat, source=witnessed, confidence=1.00, salience=0.88}
    because Interpretation [elena]: read it as threat (0.90)  {meaning=threat, weight=0.90, runner_up=challenge 0.86, rules=authority_taken_without_asking -> challenge 0.86 (base 0.40; va...
      because Access [elena]: was there and saw it
        because Event: Leo goes through the kitchen.
      because BeliefChange [elena]: answerable_for(elena,missing_can): 0.00 -> pending
        because Experience [elena]: kept it as protect, felt as anxiety  {meaning=protect, source=own intention, confidence=1.00, salience=0.61}
          because Interpretation [elena]: knew their own intention: protect  {meaning=protect, source=own intention}
            because Access [elena]: was there and saw it
              because Event: Mara is still awake and crying. Elena opens a can and gives it to her.

```


