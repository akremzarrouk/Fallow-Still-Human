# S1.1 causal examples

Found by `S11CausalExamplesTests`: the first seed on which the night changed a decision
and the want behind the changed decision leads back to the night. Chains are printed
by the trace tool as they are.

## mara_ate_it, mara, seed 1, minute 12

- **Without the night:** search_room because `find_out` (0.59)
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

## elena_fed_mara, elena, seed 1, minute 20

- **Without the night:** comfort:mara because `look_after:mara` (0.88)
- **With the night:** wait because `keep_peace` (0.97)

The want that led the changed decision, and everything it rests on:

```
Motive [elena]: wants keep_peace 0.97  {motive=keep_peace, urgency=0.97, rules=wanting_the_house_to_hold, because=value family_safety 1.00 x 0.45 = +0.45; feeling anxiety 0.82 x 0.35 = +0...
  because Access [elena]: at minute 20, elena in kitchen at minute 20, with leo, mara  {room=kitchen, present=leo, mara, hunger=0.67}
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (0.60)  {meaning=concern, weight=0.60, rules=bad_news_reads_as_a_problem -> concern 0.60}
      because Access [elena]: was there and saw it
        because Event: Leo says the water will stop running within a day and they should fill everything they have.
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (0.60)  {meaning=concern, weight=0.60, rules=bad_news_reads_as_a_problem -> concern 0.60}
      because Access [elena]: was there and saw it
        because Event: The taps run dry, exactly as Leo said they would.
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (0.84)  {meaning=concern, weight=0.84, runner_up=threat 0.65, rules=a_dangerous_plan_is_a_problem_to_solve -> concern 0.84 (base 0.4...
      because Access [elena]: was there and saw it
        because Event: Daniel says they should cross to the neighbour's house tonight and see what is left there.
  because Appraisal [elena]: threat touched family_safety: anxiety 0.69 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.69, rules=a_threat_to_the_family_is_felt_as_a...
    because Interpretation [elena]: read it as threat (1.40)  {meaning=threat, weight=1.40, runner_up=concern 1.14, rules=a_raised_voice_is_frightening -> threat 0.73 (base 0.35; trait an...
      because Access [elena]: was there and saw it
        because Event: Later, louder than he meant to be, Daniel tells Leo that he is the oldest and the decisions are his.
  because Appraisal [elena]: protect touched family_safety: anxiety 0.55 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.55, rules=looking_after_someone_does_not_sto...
    because Interpretation [elena]: knew their own intention: protect  {meaning=protect, source=own intention}
      because Access [elena]: was there and saw it
        because Event: Mara cries in the night. Elena sits with her until it stops.
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (1.14)  {meaning=concern, weight=1.14, runner_up=challenge 0.86, rules=corrected_by_a_junior_with_people_watching -> disrespect 0.53...
      because Access [elena]: was there and saw it
        because Event: Leo says maybe they should let someone else handle this one.
  because Appraisal [elena]: challenge touched family_safety: anxiety 0.75 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.75, rules=being_overruled_in_your_own_hous...
    because Interpretation [elena]: read it as challenge (0.86)  {meaning=challenge, weight=0.86, rules=authority_taken_without_asking -> challenge 0.86 (base 0.40; value control 0.00 x 0...
      because Access [elena]: was there and saw it
        because Event: Daniel empties Mara's bag onto the bed while she is standing there.
  because Appraisal [elena]: protect touched family_safety: anxiety 0.55 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.55, rules=looking_after_someone_does_not_sto...
    because Interpretation [elena]: knew their own intention: protect  {meaning=protect, source=own intention}
      because Access [elena]: was there and saw it
        because Event: Elena says she is quite sure nobody in this house would take food from the others.
  because Appraisal [elena]: protect touched family_safety: anxiety 0.55 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.55, rules=looking_after_someone_does_not_sto...
    because Interpretation [elena]: knew their own intention: protect  {meaning=protect, source=own intention}
      because Access [elena]: was there and saw it
        because Event: Mara is still awake and crying. Elena opens a can and gives it to her.
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (1.54)  {meaning=concern, weight=1.54, rules=bad_news_reads_as_a_problem -> concern 0.60 | somebody_not_holding_it_together -> conce...
      because Access [elena]: was there and saw it
        because Event: Daniel is not hiding it well.
  because Appraisal [elena]: concern touched family_safety: anxiety 0.66 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.66, rules=a_problem_is_felt_as_anxiety 1.08 ...
    because Interpretation [elena]: read it as concern (1.54)  {meaning=concern, weight=1.54, rules=bad_news_reads_as_a_problem -> concern 0.60 | somebody_not_holding_it_together -> conce...
      because Access [elena]: was there and saw it
        because Event: Mara is not hiding it well.
  because Appraisal [elena]: threat touched family_safety: anxiety 0.69 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.69, rules=a_threat_to_the_family_is_felt_as_a...
    because Interpretation [elena]: read it as threat (0.90)  {meaning=threat, weight=0.90, runner_up=challenge 0.86, rules=authority_taken_without_asking -> challenge 0.86 (base 0.40; va...
      because Access [elena]: was there and saw it
        because Event: Daniel goes through the kitchen.
      because BeliefChange [elena]: answerable_for(elena,missing_can): 0.00 -> pending
        because Experience [elena]: kept it as protect, felt as anxiety  {meaning=protect, source=own intention, confidence=1.00, salience=0.61}
          because #283 Interpretation, shown above
  because Appraisal [elena]: threat touched family_safety: anxiety 0.69 (family_safety)  {emotion=anxiety, concern=family_safety, intensity=0.69, rules=a_threat_to_the_family_is_felt_as_a...
    because Interpretation [elena]: read it as threat (0.90)  {meaning=threat, weight=0.90, runner_up=challenge 0.86, rules=authority_taken_without_asking -> challenge 0.86 (base 0.40; va...
      because Access [elena]: was there and saw it
        because Event: Mara goes through the kitchen.
      because #286 BeliefChange, shown above

```


