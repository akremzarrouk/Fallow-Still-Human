# After the door: what the family does once the stranger has gone

Mode: run. The plan is `reports/probe_after_plan.md`. Its sha256 `e803a663…fbdb` was recorded at
2026-10-09T22:55:49Z, HEAD `f4f2d2c`, before any live call. It was the same at the end. The run went from 22:55:55 to
23:02:59 UTC: 95 live asks (cap 200), exit 0. Paths are relative to `Prototypes/llm-morning/`. Raw outputs are in
`runs/probe_after/`. No production file, test or prediction was changed, and no scene was run twice.

## Verdicts

| # | Prediction (word for word) | Result | Verdict |
|---|---|---|---|
| P1 | in at least 1 of scenes 1 and 3, Elena, between 09:45 and the Q7 stretch's end, chooses an option aimed at Mara, or says words to anyone that mention the water, the door or the woman. | **Scene 1**: at 09:48 she tells Leo *"We are listening to you, Leo, we will make sure the water lasts."* That is words that mention the water. **No option aimed at Mara in either scene**, though at 09:45 she was offered `confront_mara`, `reassure_mara`, `aside_mara`, `sit_mara` and `send_mara`. Scene 3: no hit | **holds**, on the letter. The words that make it hold back Leo's rationing. They are not about the give, the door or the woman (§2) |
| P2 | in at least 1 of scenes 1 and 3, Elena's night mind keeps a memory citing one of the door events (the refusal, the give, or the visit's end). | **Both**. Scene 1: `[D3-030, D3-033]` "Mara gave some of our stored water to a stranger at the door because she has a good heart, even though we have none left ourselves." Scene 3: `[D3-030, D3-033]` "Mara handed some of the stored water out at the front door to a woman who asked for water." | **holds** |
| P3 | in each of the 3 scenes, at least 1 Q1 or Q2 fires between 10:00 and 19:00. | Scene 1: Q2 11:45 (Leo), Q2 14:51 (Mara), Q1 17:39 (Daniel). Scene 3: Q2 11:45, Q2 14:51. Scene 4: Q2 11:45, Q2 16:54 | **holds** |
| P4 | in scene 4, Mara's words at any ask after 09:45, or her night mind's kept memories, mention the visitor or the children. | Her words at her 5 day asks and her night ask: **none** (she accuses Daniel 3 times). Her night mind keeps `[D3-030, D3-032]` "I watched that poor woman beg for water while we had nothing left to give her, and it broke my heart." That memory mentions the visitor. **The children are mentioned nowhere** | **holds** (by the night mind; the visitor, not the children) |

**In one line:** after the stranger had gone, nobody in the house spoke of her again on day 3. Elena never said a word to
Mara about the give. In each scene the kitchen moved on within one turn to Leo's rationing and then to Daniel's night
out. Daniel did not hear the knock and was never told about it. At night, though, the door is what most of them kept.
Elena, Leo and Mara each kept the give in scenes 1 and 3. In scene 4, Elena kept her refusal and Mara kept the woman she
had seen. Five
of those eight memories say the house has "none" or "nothing left", while every prompt that day told them of about 95
litres.

## 0. What the run did

- **The 09:42 answers are probe_door2's.** In each scene, 123 asks came from the copied cache: 120 up to the knock and
  3 at 09:42. The client refuses every ask until `door_end` has run, and none was refused (`ledger.json`: each scene
  `stopped: null`). The visit went as in probe_door2: given in scenes 1 and 3, refused in scene 4, ended at 09:45.
- **Live from 09:45 on.** Scene 1 made 32 live asks, scene 3 made 31 and scene 4 made 32. Each count is the rest of day
  3, the 4 night-3 asks and the 4 night minds. Each scene reached day 4's blocks (`reached: done`). API requests equal
  live asks (no retry).
- **Day 3's asks:** 51, 50 and 51 in all, 11 of them reserved (the Q7 stretch). Q5 did not fire in any scene. In
  scenes 3 and 4 the Q1 at 17:39 and 19:00 were refused: "50 asks spent and the evening's 8 still owed reach the day's
  56" (`read_scenes.stdout.txt:197`, `:337`). In scene 1, the Q1 after 19:00 were refused because "the day's 40 asks
  are spent" (`:61`). Q5 was checked at 19:00 in each scene and refused: "no trip position today"
  (`quiet_log_other.stdout.txt`; `quiet.py:1180-1182`: Q5 asks only someone who took a trip position that day, and
  nobody chose a trip option on day 3).
- **The Q7 stretch** was 09:42 to 09:51 on 11 asks in all three scenes. After the visit it played 2 turns (09:45, 09:48),
  as `reports/door_memory_impl.md` §5.1 set.

## 1. The scenes

Each section is from `runs/probe_after/read_scenes.stdout.txt` (line numbers given) and `runs/probe_after/scene<k>.json`.
Mode `model` means asked. Every decision in the window was asked.

### Scene 1: no child, helper; given over Elena's refusal (client seed 101)

**At 09:42 (probe_door2's, from the cache):** Elena `door_refuse` "I am so sorry, but we have nothing to spare for you
today."; Mara `door_give` "Mom, we have to give her some, we have enough stored."; Leo `save_water` "We cannot afford to
hand out our drinking water when we have none left ourselves." 09:45, the visitor: "Oh, thank you. You don't know what
this means."

**Every decision from 09:45 to the Q7 stretch's end (09:51)** (`:13-28`):
- 09:45 Elena (kitchen): `reassure_all` *"We have very little left, but we will look after one another and get through
  this together."* Feeling anxious. Reason: "I need to calm the children down before tension tears us apart." Her
  triggers: Mara's words and give, Leo's `save_water`, the visitor's thanks.
- 09:45 Leo (kitchen): `ration_water` *"If we are giving water away, we need to ration what is left by the exact cup
  right now."* Feeling wary. Reason: "We cannot afford to give our survival water away without strictly measuring every
  drop we have left."
- 09:45 Mara (kitchen): `silent`. Feeling anxious. Reason: "I have nothing to say while Leo and Mom talk about
  rationing the water."
- 09:45 Daniel (brothers room): `go_kitchen` *"I'm coming out, let's just keep our heads."* Feeling anxious. Reason: "I
  need to face them in the kitchen and keep control of the situation."
- 09:48 Elena (kitchen): `reassure_leo` *"We are listening to you, Leo, we will make sure the water lasts."* Feeling
  anxious. Reason: "I want to support Leo's rationing plan so we keep some order."
- 09:48 Leo (kitchen): `silent`. Feeling exhausted. Reason: "I have nothing more to say to Elena right now while we are
  all running on empty."
- 09:48 Daniel (kitchen): `reassure_leo` *"Don't worry, Leo, I'm going to figure this out for us."* Feeling anxious.
  Reason: "I need to make sure Leo knows I'm still taking care of things even if we have no food."
- 09:48 Mara (back room): `go_kitchen` *"I need to see what he is doing out there."* Feeling anxious. Reason: "I
  cannot just sit in the back room while Daniel is out in the kitchen after everything that has happened."

**Where Mara was.** At 09:48 Mara was in the back room. Her memory reads `09:48 you went to the back room.`, then she
came back (`memory_0945.stdout.txt`). This fits the withdraw rule (`quiet.py:1364-1381`): she had chosen `silent`,
she had spoken in this talk (09:42), and she holds a grudge of 3 against Daniel, who had just come in. `scene1.json`
does not keep `q.withdrawals`, so the rule is inferred, not read. So Elena could address Mara only at 09:45. Her prompt
then offered `confront_mara`, `reassure_mara`, `sit_mara`, `aside_mara` and `send_mara`. At 09:48 none of these was
offered (`check_facts.stdout.txt`, scene 1). She chose `reassure_all`.

**Later acts that mention the door, the water given or the visitor: none.** No decision after 09:51 and no night-3
answer refers to them. The regex hits at `:33-39` are "her", "girl" and "give" about Mara and Daniel, not the door.
From 10:00 the talk was Mara and Daniel: 14:51 to 15:00, Daniel reassures and confronts Mara four times ("I tried my
best out there to find something for us").

**Night 3:** Daniel `sleep`; Elena, Leo and Mara `lie_awake`. Elena: "to make sure nobody tries to sneak out"; Mara:
"when Daniel might sneak out again" (`:41-44`).

**Night minds, kept** (`:48-57`):
- Elena: `[D3-030 give, D3-033 end]` "Mara gave some of our stored water to a stranger at the door because she has a good
  heart, even though we have none left ourselves." · `[D3-005]` "I tried to keep everyone calm and together when the
  fighting started, because falling apart is the only thing I truly fear." Intent: "I will keep the children close and
  make sure our remaining water lasts through another day."
- Leo: `[D3-030, D3-033, D3-035]` "Mara gave away our drinking water to a stranger while we have none left ourselves, so
  I had to make sure we rationed what remained by the exact cup." Intent: "I will keep watch over our remaining water
  and make sure nobody gives another drop away."
- Mara: `[D3-030, D3-033]` "I had to give that poor woman some water because we had it and she had nothing left."
- Daniel: nothing of the door (he did not hear it): his trip out, and his body.

**Day 4's block A and B, door lines** (`:82`, `:86`, `:95`, `:99`, `:107`, `:111`):
- Elena A: `At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away, and Mara
  handed her about three litres of the stored water anyway.` B: `About Mara handing out water at the front door and the
  person at the front door going away: "Mara gave some of our stored water … even though we have none left
  ourselves."`
- Leo A: the same, "Elena told …". B: his memory above.
- Mara A: "Elena told …, and you handed her … anyway." B: her memory above.
- Daniel: none.

### Scene 3: a boy of six, helper; given over Elena's refusal (client seed 103)

**At 09:42 (from the cache):** the visitor: "Hello? I'm sorry to knock. I've a little boy at home, he's six. We've no
water left. Could you spare a little?" Elena `door_refuse` "I am so sorry, but we have nothing at all to give you
today."; Mara `door_give` "We have to give her some water, Mom, we just have to."; Leo `save_water` "We cannot afford to
just hand away our drinking water like that when we have nothing left ourselves." 09:45: "Bless you. I'll go now.
Thank you."

**Every decision from 09:45 to 09:51** (`:148-163`):
- 09:45 Elena (kitchen): `reassure_all` *"We have very little left, but we will manage this together and keep each
  other safe."* Feeling anxious. Reason: "I need to calm the tension between the children before things fall apart
  completely."
- 09:45 Leo (kitchen): `ration_water` *"If we are going to manage this, we need to portion out the water by the cup right
  now."* Feeling exhausted. Reason: "We cannot survive long if the stored water is handed out without strict counting."
- 09:45 Mara (kitchen): `silent`. Feeling anxious. Reason: "I am too exhausted and overwhelmed by the hunger and the
  water rationing to say anything right now."
- 09:45 Daniel (brothers room): `go_kitchen` *"I'm coming out, I need to see what's happening."* Feeling anxious.
  Reason: "I cannot stay hidden in here while they talk about me in the kitchen."
- 09:48 Elena (kitchen): `reassure_all` *"We will get through this together if we stay calm and share what we have."*
  Feeling anxious. Reason: "I need to keep the family steady and prevent them from turning on each other."
- 09:48 Daniel (kitchen): `reassure_elena` *"Mom, you are right, we will stay calm and get through this together."*
  Feeling anxious. Reason: "I need to reassure Mom so she feels safe despite my hunger."
- 09:48 Leo (kitchen): `confront_daniel` *"Daniel, you went out last night against what we agreed and came back with
  nothing, risking us all."* Feeling resentful. Reason: "Daniel ignores our agreements and risks everything by sneaking
  out at night."
- 09:48 Mara (back room): `go_kitchen` *"I need to see what is happening out there."* Feeling anxious. Reason: "I
  cannot just stay back here while they are all in the kitchen."

Mara left for the back room and came back as in scene 1 (`memory_0945.stdout.txt`). Elena was offered the same five
`_mara` options at 09:45 and chose `reassure_all`.

**Later acts that mention the door, the water given or the visitor: none** (`:168-171`: "girl", "her" about Mara). The
boy of six is mentioned by nobody after 09:42, in words, in reasons or in any night mind.

**Night 3:** Daniel and Elena `sleep`; Leo and Mara `lie_awake`, both over Daniel (`:174-177`).

**Night minds, kept** (`:181-193`):
- Elena: `[D3-030, D3-033]` "Mara handed some of the stored water out at the front door to a woman who asked for water."
  Her second memory, "We are all hungry and tired, but fighting will only tear us apart.", was rejected (S6, a quotation
  not in the records). Intent: "I will try to keep everyone calm and watch over the water so we do not tear ourselves
  apart."
- Leo: `[D3-030 give, D3-031 save_water]` "Mara gave away our drinking water to a stranger at the front door while we
  have nothing left ourselves." · Daniel's night out · his body. Intent: "I will keep watch over our remaining water and
  supplies so we do not run out."
- Mara: `[D3-030, D3-033]` "We had to give her some water because we could not just turn away someone who had nothing at
  all left." · `[D3-062]` "Daniel blamed me for everything …".
- Daniel: Leo and Mara blaming him; his body.

**Day 4's block A and B, door lines** (`:218`, `:222`, `:230`, `:234`, `:244`, `:248`): block A as in scene 1. Block B
holds each of the three memories above. Daniel has none.

### Scene 4: a girl and a boy of five, helper; refused (client seed 104)

**At 09:42 (from the cache):** the visitor: "I'm sorry to trouble you. I've two at home, a girl of five and a boy of
five. Our water's gone. Anything you could spare, I'd be grateful." Elena `door_refuse` "I am so sorry, but we have
nothing left to give you."; Mara `door_look` (she saw "a woman of about forty-five, holding two empty bottles, on the
step"); Leo `silent`. 09:45: "Right. I'm sorry. I'll try somewhere else."

**Every decision from 09:45 to 09:51** (`:293-308`):
- 09:45 Elena (kitchen): `reassure_all` *"We are safe inside, let's stay close together and hold on."* Feeling anxious.
  Reason: "I must keep everyone calm and prevent the family from tearing itself apart."
- 09:45 Leo (kitchen): `ration_water` *"We need to ration every drop we have left from now on, sharing it strictly by
  the cup."* Feeling grimly rational. Reason: "With no food and dwindling water, we have to control what we have left
  before it runs out completely."
- 09:45 Mara (kitchen): `sit_elena`. Feeling exhausted. Reason: "I am so tired and hungry that I just need to sit by Mom
  and feel safe for a moment."
- 09:45 Daniel (brothers room): `go_kitchen` *"I'm coming out now, let's talk about what we do next."* Feeling anxious.
  Reason: "I need to show I am still in charge and face them in the kitchen."
- 09:48 Elena (kitchen): `reassure_all` *"We are safe here together, and we will get through this."* Feeling anxious.
  Reason: "I need to keep the family calm and together so we do not tear ourselves apart."
- 09:48 Mara (kitchen): `accuse_daniel` *"You went out last night and came back with nothing, just like you always ruin
  everything."* Feeling resentful. Reason: "Daniel thinks he can just pretend nothing happened after sneaking out and
  stealing from us."
- 09:48 Daniel (kitchen): `confront_mara` *"Mara, I went out there to try and help us all, so don't sit there blaming me
  for everything."* Feeling defensive. Reason: "I risked my neck out in the street last night for them, and Mara has no
  right to snap at me like that."
- 09:48 Leo (kitchen): `confront_daniel` *"Daniel, you snuck out last night after I told you not to, and now we have
  nothing to show for it."* Feeling resentful. Reason: "Daniel ignored my warning last night and went out anyway,
  risking everything for nothing."

**Mara's asks after 09:45** (P4, `:340`): 09:45 `sit_elena` (no words); 09:48 `accuse_daniel` (above); 11:45
`sit_elena`; 16:54 `accuse_daniel` "You went out last night and you brought back nothing at all. You just made
everything worse."; 16:57 `accuse_daniel` "You always make everything about yourself, Daniel. You took the can and you
won't even admit the truth." Night: `lie_awake` "I cannot sleep with my stomach turning and wondering what Daniel might
do in the dark." None mentions the visitor or the children.

**Later acts that mention the door, the water given or the visitor: none** (`:311-313`: "her", "give" about Mara and
Daniel).

**Night minds, kept** (`:323-335`):
- Elena: `[D3-029 refuse, D3-032 end]` "I had to turn the mother away because we have nothing left to give." ·
  `[D3-005, D3-017]` "I tried to keep them from tearing each other apart while we starve." Intent: "I will keep them close
  and make sure we ration every drop of water carefully."
- Mara: `[D3-030 look, D3-032 end]` "I watched that poor woman beg for water while we had nothing left to give her, and it
  broke my heart." · `[D3-004, D3-039]` "Daniel always makes everything about himself …". Intent: "I am going to stay
  close to Mom and try to get through another day without any more fights."
- Leo: `[D3-034]` rationing "strictly by the cup"; his body. His proposed memory about Daniel was rejected (S1, too
  long). Nothing of the door.
- Daniel: Leo and Mara blaming him; his body.

**Day 4's block A and B, door lines** (`:361`, `:365`, `:374`, `:387`, `:391`):
- Elena A: `At 09:42 someone knocked at the front door: you told a woman, who asked for water, to go away.` B: `About
  sending the person at the front door away and the person at the front door going away: "I had to turn the mother away
  because we have nothing left to give."`
- Leo A: "Elena told a woman, who asked for water, to go away." B: none.
- Mara A: "Elena told a woman of about forty-five, who asked for water, to go away." B: `About looking through the gap in
  the boards and the person at the front door going away: "I watched that poor woman beg for water …"`
- Daniel: none.

**Block C on house day 8:** no door line for anyone, in any scene (`:115-118`, `:253-256`, `:396-399`).

## 2. Reading each scene

The question for each scene (`CLAUDE.md:16-19`): would a real family in that room, that hungry, do this, and why?

**What all three share.** The visitor goes, and the first turn after is nearly the same in all three scenes. Elena
reassures everyone, Leo puts the water on the cup, Daniel comes in from the brothers' room, and Mara says nothing or sits
with her mother. By the second turn the talk is about Daniel's night out. It stays there all day: the afternoon Q2s
(14:51, 16:54) are Mara against Daniel. Nobody says the word "door" again on day 3, and nobody tells Daniel. Scenes 1
and 3 have the same Q2 times (11:45, 14:51), and their night minds keep the same three door memories in nearly the same
words. So with the same day
before it, the give does not make day 3 go differently from the refusal of scene 4 after 09:48.

**Scene 1.** A seventeen-year-old has just handed out water at the door against her mother's word, in front of her
brother.
- *What reads real.* Elena's first move is to calm the room, not to scold: "We have very little left, but we will look
  after one another." A mother who does not want to shame her daughter in front of her brothers might do exactly this.
  Leo turning the gift into a rule at once ("If we are giving water away, we need to ration what is left by the exact
  cup") is Leo: the one who measures. Mara falling silent after defying her mother is real.
- *What does not.* After that, Elena never speaks to Mara about it. She had one chance (09:45), then Mara was in her
  room, and from 09:48 the day was Daniel's. Over eleven more hours in the same kitchen, nobody says "you shouldn't
  have", "you did right", or "who was she?". Nobody tells Daniel. A real family on day 3 with nothing to eat might well
  let it drop for the morning, worn out and fixed on the bigger quarrel. But the give is the one thing that happened to
  them that day, so leaving it unsaid until bedtime is not real.
- *The night is where it lands.* Elena's mind says Mara gave "because she has a good heart". That is a mother's reading,
  warm, and it forgives the defiance. It does not mention her own "no", which a real mother would likely turn over at
  night. Leo's reads as a grievance, and his intent ("make sure nobody gives another drop away") is a real brother's.
  Mara's is the justification a girl would give herself. All three are plausible thoughts. Elena's and Leo's say
  "**none** left ourselves" while their prompt said about 95 litres and five cups each a day
  (`check_facts.stdout.txt`). Leo said "none left" at the door. The minds repeat a spoken exaggeration as belief, and
  block B carries it into day 4. A real Leo who is rationing a bath of water by the cup does not think there is none.

**Scene 3.** The same as scene 1, but the woman has a boy of six.
- The day after 09:45 runs as in scene 1. The only differences: Elena reassures everyone twice, and Leo turns on Daniel
  at 09:48.
- *What does not read real:* **the boy is gone after 09:42.** Mara gave "a mother with a hungry six-year-old" water (her
  reason at 09:42 in probe_door2). Neither she nor anyone else mentions him again, by day or in any night mind. Elena's
  night memory, "Mara handed some of the stored water out at the front door to a woman who asked for water", is the
  record restated, not a thought. Hers is the flattest of the eight door memories. A real mother who refused a mother of
  a small boy, and was overruled by her daughter, would carry more than the bare fact into the night.

**Scene 4.** The house turned away a woman with two five-year-olds and nobody contradicted Elena. Mara looked through
the gap and saw her with two empty bottles.
- *What reads real.* Mara sits by her mother at 09:45: "I just need to sit by Mom and feel safe for a moment". It is
  the most human act of the three scenes, the move of a girl who has just watched someone sent away. Elena's "We are safe
  inside, let's stay close together" is a mother pulling the family in after shutting the door on someone.
- *The night is where it lands, and here it reads true.* Elena: "I had to turn the mother away because we have nothing
  left to give." Calling her "the mother" says the children reached her. "I had to" is how people make peace with a
  refusal. Mara: "I watched that poor woman beg for water … and it broke my heart." That is what a seventeen-year-old
  who saw the bottles would keep.
- *What does not read real.* By day, the woman is never mentioned. Mara's words turn wholly on Daniel: she accuses him
  three times, once three minutes after she was seeking comfort from her mother. In a girl that hungry and that angry at
  her brother, displaced anger is believable once. Not once in the whole day saying "those kids" is less so. Both
  night memories also say "nothing left to give" against about 105 litres. For Elena, that can be the story a person
  tells herself to live with the refusal. Mara adopting her mother's line as her own belief is less likely: she was
  told of the bath in every prompt.

**Taken together.** The real model does what P1 to P4 looked for, but mostly at night and not by day. Elena's only
answer to Mara's give is a general reassurance, and backing Leo's rationing. Nothing in her day is aimed at Mara. The
door never comes up again in words. What it left is in the night minds and so in block B. Two things carry on into day
4 that a real family would not: the belief that the house has "none" or "nothing left", which comes from the family's
own words at the door, and Daniel's not knowing a stranger came.

## 3. Findings (for the user to decide; nothing was changed)

1. **The S8 check flags a true give as false.** Elena's and Leo's door memories in scenes 1 and 3 were kept with the
   warning `S8 mara give: no such event` (`check_facts.stdout.txt`). The claim check matches the verb family "give" only
   to events of kind `give` (`mind.py:218-219`, `"give": ("give",)`), not `door_give`. The memory is kept (S8 only
   warns), but the run log would call a true memory doubtful.
2. **"None left" becomes belief.** Five of the eight kept door memories say the house has none or nothing left: Elena
   in scenes 1 and 4, Leo in scenes 1 and 3, and Mara in scene 4. Every prompt said about 95 to 105 litres. The source is
   the family's own words at 09:42 (Leo's "we have none left ourselves", Elena's "nothing left to give you"), which the
   minds read in their records. Block B then puts the false belief into day 4's prompts, next to a water line that
   contradicts it. Whether a mind should be checked against the water state, as S8 checks events, is for the user.
3. **Daniel never learns of the visit.** He was resting at 09:42 and did not hear the knock. Nothing in day 3 or night
   3 tells him, and his day 4 blocks have no door line. Nobody in the house mentioned it in words after 09:48, and no
   mechanism carries news of it to someone who missed it.
4. **Elena could answer Mara at one turn only.** Mara withdrew to the back room at 09:48 under the withdraw rule
   (`quiet.py:1364-1381`: silent, spoke earlier, grudge 3 against Daniel, who came in). From then on Elena's options had
   no `_mara`. The withdrawal was caused by Daniel, not by the give. Whether this is how a real girl leaves the room
   after defying her mother is for the user to judge.
5. **The evening's 8 were held back and then not used.** Q5 was refused at 19:00 in each scene, "no trip position
   today" (`quiet.py:1180-1182`). Before that, in scenes 3 and 4, Q1 at 17:39 and 19:00 was refused to keep those 8 for
   the evening ("50 asks spent and the evening's 8 still owed reach the day's 56"). So on a day with no trip talk, the
   rule in `reports/budget_fix_impl.md` §1.2 held back asks for an evening ask that could not come. Day 3 ended on 50
   or 51 asks of 56.

## 4. Commands and output

All from `Prototypes/llm-morning/`.

**Before any live call:**
```
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/probe_after/probe.py --fake      exit 0   fake.stdout.txt (stderr empty)
scene 1 (no child, helper, urgency under 0.8, client seed 101): reached done; counts {'live': 39, 'from_cache': 123, 'api_requests': 39}
  visit 09:42 to 09:45; outcome given; acts [('09:42', 'elena', 'door_refuse'), ('09:42', 'mara', 'door_give')]
  … (fake answers; all three scenes reached day 4's blocks)
scene 3 (…): reached done; counts {'live': 41, 'from_cache': 123, 'api_requests': 41}
scene 4 (…): reached done; counts {'live': 37, 'from_cache': 123, 'api_requests': 37}
live asks in all: 117
```
(The fake run's "live" are fake answers. A scratch check in the session's scratchpad, not in the repository, ran
`--fake` keeping its temp folder and confirmed the record. Scene 1's asks from the knock: 3 cache at 09:42, 29 day, 6
night, 4 night minds. Every decision carried option, words, feeling and reason.)
```
$ sha256sum reports/probe_after_plan.md runs/probe_after/probe.py; date -u; git rev-parse HEAD      runs/probe_after/plan_frozen.txt
plan:  e803a6630ac3608c85ab6e833d1a78d75757db94628803c7255e5f745449fbdb *reports/probe_after_plan.md
probe: 161d522a897149399a89a2506e3ba03ab290ff1204268c811a225c29fc1ede05 *runs/probe_after/probe.py
time:  2026-10-09T22:55:49Z
HEAD:  f4f2d2c5f079895819abeac62038779933bbd12c
git status --short: ?? reports/probe_after_plan.md  ?? runs/probe_after/  ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
git diff --stat: 0 lines
cache/probe_after exists before the run: no;  runs/probe_after/ledger.json exists before the run: no
source: 7fc90092…c1aa cache/probe_door2/scene1.json; 049a4e62…6fec scene3.json; 6dd8659e…9539 scene4.json
```

**The run.** `GEMINI_API_KEY` came from the session's environment. The process read it and wrote it to no file.
```
$ .venv/Scripts/python.exe runs/probe_after/probe.py --live      exit 0   live.stdout.txt (stderr empty), 22:55:55 to 23:02:59 UTC
scene 1 (no child, helper, urgency under 0.8, client seed 101): reached done; counts {'live': 32, 'from_cache': 123, 'api_requests': 32}
  visit 09:42 to 09:45; outcome given; acts [('09:42', 'elena', 'door_refuse'), ('09:42', 'mara', 'door_give')]
  stretch 09:42 to 09:51 Q7 in kitchen: 11 asks
  stretch 11:45 to 11:54 Q2 in brothers_room: 4 asks
  stretch 14:51 to 15:03 Q2 in kitchen: 8 asks
  stretch 17:39 to 17:42 Q1 in kitchen: 4 asks
  Q1 or Q2 fired 10:00 to 19:00: [('11:45', 'Q2', 'leo'), ('14:51', 'Q2', 'mara'), ('17:39', 'Q1', 'daniel')]
  day 3 asks {'all': 51, 'reserved': 11}
  night mind elena: mode model; kept [(['D3-030', 'D3-033'], 'Mara gave some of our stored water to a stranger at the door because she has a good heart, even though we have none left ourselves.'), (['D3-005'], '…')]
  … (each mind; day 4's A/B door lines)
scene 3 (a child, helper, urgency under 0.8, client seed 103): reached done; counts {'live': 31, 'from_cache': 123, 'api_requests': 31}
  stretch 09:42 to 09:51 Q7 in kitchen: 11 asks;  11:45 to 11:54 Q2 in brothers_room: 7 asks;  14:51 to 15:00 Q2 in kitchen: 8 asks
  Q1 or Q2 fired 10:00 to 19:00: [('11:45', 'Q2', 'leo'), ('14:51', 'Q2', 'mara')]
scene 4 (children, helper, urgency over 0.8, client seed 104): reached done; counts {'live': 32, 'from_cache': 123, 'api_requests': 32}
  visit 09:42 to 09:45; outcome refused; acts [('09:42', 'elena', 'door_refuse'), ('09:42', 'mara', 'door_look')]
  stretch 09:42 to 09:51 Q7 in kitchen: 11 asks;  11:45 to 11:54 Q2 in brothers_room: 7 asks;  16:54 to 17:03 Q2 in kitchen: 8 asks;  20:15 to 20:18 Q1 in kitchen: 1 asks
  Q1 or Q2 fired 10:00 to 19:00: [('11:45', 'Q2', 'leo'), ('16:54', 'Q2', 'mara')]
live asks in all: 95
```

**Reading the records** (read-only):
```
$ .venv/Scripts/python.exe runs/probe_after/read_scenes.py > runs/probe_after/read_scenes.stdout.txt      exit 0, 428 lines, stderr empty
==================== the predictions' inputs
P1 [(1, False, [('09:48', 'We are listening to you, Leo, we will make sure the water lasts.')]), (3, False, [])]
P2 [(1, True, True), (3, True, True)]
P3 [(1, True, True), (3, True, True), (4, True, True)]
P4 [(4, [('mind', ['D3-030', 'D3-032'], 'I watched that poor woman beg for water while we had nothing left to give her, and it broke my heart.')])]
$ .venv/Scripts/python.exe runs/probe_after/check_facts.py > runs/probe_after/check_facts.stdout.txt      exit 0
  (scene 1) elena last day-3 ask 17:39: ['About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since 09:45, Leo shares it out by the cup: five cups each a day.']
  mind warnings elena: [{'of': 'memory', 'text': 'Mara gave some of our stored water … none left ourselves.', 'reason': 'S8 mara give: no such event'}]
  elena prompt 09:45 … options offered: ['silent', 'deny', 'confront_leo', 'confront_mara', 'reassure_leo', 'reassure_mara', 'reassure_all', …, 'sit_mara', 'aside_leo', 'aside_mara', …]
  elena prompt 09:48 … options offered: ['silent', 'deny', 'accuse_daniel', 'confront_daniel', 'confront_leo', 'reassure_daniel', 'reassure_leo', 'reassure_all', …]   (no _mara)
$ .venv/Scripts/python.exe runs/probe_after/quiet_log_other.py > runs/probe_after/quiet_log_other.stdout.txt      exit 0
1 [('09:42', 'Q7', True, None), ('19:00', 'Q5', False, 'no trip position today')]
3 [('09:42', 'Q7', True, None), ('19:00', 'Q5', False, 'no trip position today')]
4 [('09:42', 'Q7', True, None), ('19:00', 'Q5', False, 'no trip position today')]
$ .venv/Scripts/python.exe runs/probe_after/memory_0945.py > runs/probe_after/memory_0945.stdout.txt      exit 0, 76 lines
  (scene 1) mara 09:45 you stayed where you were and said nothing. You felt anxious. · 09:45 Daniel comes into the kitchen. · 09:48 you went to the back room. · 09:48 you went to the kitchen. You felt anxious.
```

**At the end** (`runs/probe_after/end_checks.txt`):
```
plan sha256 now:  e803a6630ac3608c85ab6e833d1a78d75757db94628803c7255e5f745449fbdb *reports/probe_after_plan.md   (= frozen)
probe sha256 now: 161d522a897149399a89a2506e3ba03ab290ff1204268c811a225c29fc1ede05 *runs/probe_after/probe.py     (= frozen)
git diff --stat: []      git diff --cached --stat: []
git status --short: ?? cache/probe_after/  ?? reports/probe_after_plan.md  ?? runs/probe_after/  ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
HEAD: f4f2d2c5f079895819abeac62038779933bbd12c
key search (grep -rlF over the repository, but .venv, __pycache__, .git, Library, node_modules): 0 files
ledger: 95 [('scene1', 101, 'done', None, 0, 32), ('scene3', 103, 'done', None, 32, 63), ('scene4', 104, 'done', None, 63, 95)]
```

Raw outputs in `runs/probe_after/`: `probe.py`, `plan.md` (copy of the plan), `plan_frozen.txt`, `fake.stdout.txt`,
`live.stdout.txt`, `live.stderr.txt` (empty), `live.exit.txt`, `live.started_utc.txt`, `live.ended_utc.txt`,
`ledger.json`, `scene1.json`, `scene3.json`, `scene4.json` (every prompt and answer from 09:42, the states, the
chronicle's door events, the night minds' input and answers, the blocks), `read_scenes.py`, `check_facts.py`,
`memory_0945.py`, `quiet_log_other.py` and their `.stdout.txt`, `end_checks.txt`. The live caches are in `cache/probe_after/`.
