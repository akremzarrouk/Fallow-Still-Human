# Playing Leo: design

Mode: design. No code, prompt or test was changed, and nothing was asked of the Gemini API. Paths are relative to
`Prototypes/llm-morning/`. Counts come from v23's own files (`runs/v23/`, `cache/v23/`, `cache/v16/`, `cache/v22/`),
read with three read-only scripts (§12).

**Goal.** A small demo you can play on the free tier. The player is Leo in `daniel_ate_it`, from day 1, minute 00. Leo
does not know Daniel ate the can. Elena, Daniel and Mara are played by the model as today. An hour of play must fit in
one free day (500 requests, CLAUDE.md) and should use 250 requests or fewer.

**The decisions in one list**
- The screen is built from Leo's own lines, the same ones that build his prompt today, inside `truth.prompting()`
  (`truth.py:25-32`). It never shows his AI-only lines: his suspicion level, his grudge levels or his conscience (§1).
- The player gets exactly the options Leo gets today (`world.py:551-630`), except that the repetition guard is off
  for him (amended at S1). They may add their own words. The act decides what the code does; the words are only what
  the others hear (§2).
- The code still tracks Leo's body, knowledge, place and acts. It stops deciding his feelings, suspicion and grudges,
  his inner, food and lull moments, his night mind and any routine he did not choose (§3).
- The game waits for the player on every played turn Leo is awake. "Wait" lets turns and quiet time run until
  something reaches Leo. Quiet time is skipped by code, as today (§4).
- Others are asked exactly as today. There are three changes, all in player mode only: every line the player says
  counts as new, an act in quiet time starts a stretch capped at 8 asks, and Leo's grudges stay at 0 (§5.1).
- The estimate is about 127 requests in the first hour from day 1, and 187 an hour on later days, at 35 s of thought
  per choice. A fast player reaches about 278 an hour on later days, so a session cap of 250 requests is part of the
  design (§5.2).
- With no player, every hook is off and nothing changes. The checks are the suite and a byte-identical fake run (§7).
- Each session writes a play log that you can bring back. It replays from the cache with 0 live asks, which is also
  how a stopped session resumes (§8).

---

## 1. What the player sees each turn

### 1.1 Built only from Leo

Leo's prompt today is already "what Leo perceives, knows and was told". `Morning.prompt_for` (`world.py:1123-1191`)
builds it from his own `Person` fields:

- `memory`: what he saw and heard, stamped.
- `sure`: facts that are never trimmed.
- `beliefs`: what he was told.
- `backstory`: only the events whose witness list names him (`world.py:321-322`).
- his room, and who is there with their activity.
- `p.door`, `p.water` and `rain_since`, written by the code from the World (`quiet.py:328-339`, `quiet.py:631-676`).

The World cannot be read while it is built (`truth.py:35-39`). So the screen reuses the same builder, in a player mode
that keeps the perceived lines and drops the lines that exist only to steer the model (§1.3). It is never a second
writer of the same facts. Nothing on screen is read from `Morning.culprit`, the chronicle's `fixed`, the World, or
another person's fields, except what `prompt_for` already reads for "Now": the others' room, activity label and shown
face.

### 1.2 The screen

```
── Day 1 · minute 03 · the kitchen ───────────────────────────────
Your body: a little hungry.

Since you last chose:
  min 00  Elena counts the pantry with everyone standing there. She finds one can fewer than she expected and says so.
          2 portions are left.
  min 00  Mara leaves for the back room.
  min 00  Daniel says to everyone: "Nobody touches the shelf until we sort this out."
  min 00  You stayed where you were and said nothing.

Now:
  - Daniel is here, talking.
  - Elena is here, staying put.
  - 2 portions on the shelf.
  Said and done in the kitchen this turn, before you, in order:
  1. Elena stays put and says nothing.

What you do:
  Speak   1 ask everyone here who took the can        2 accuse Daniel of taking it    3 accuse Elena of taking it
          4 reassure Daniel   5 reassure Elena   6 reassure everyone here   7 say something else
  Do      8 stay put and say nothing   9 sit with Daniel   10 sit with Elena   11 take Daniel aside to the brothers room
          12 take Elena aside to the brothers room   13 search the kitchen for the can (takes about six minutes)
          14 eat one of the portions   15 share out what is left among everyone here
  Go      16 go to the brothers room   17 go to the back room   18 go to the bathroom
  w wait (carry on until something reaches you) · l look (all you remember) · h help · q save and stop
> 2 You were up last night, Daniel. I heard you.
```

(The lines are illustrative. Their wording is exactly the wording Leo's lines have today.)

- **Header:** the day, the minute the way his prompt writes it (`data.minute_words`, `data.py:94-96`: "minute 03" on
  days 1 and 2, "10:21" from day 3), and his room.
- **Body:** the first line of `inside_lines` (`world.py:1014-1027`). It includes the "Since you last decided, you
  have grown …" lines.
- **Since you last chose:** every `memory` and `sure` line Leo gained since his last screen, and every belief he was
  given, in the order gained. His own acts are echoed with the words the player typed. On the first screen of a day,
  this section is the day's opening: the carry-in block A and block C (`memory.py`), as his prompt holds them.
- **Now:** the lines `_prompt_for` builds after "Now" (`world.py:1166-1187`): meeting and evening lines, rain, the
  door, who is here, the shelf, and what was said and done in the room this turn before him. The face is the one
  change (L4 in §1.4).
- **What you know (`l`):** the "About …" lines (food, the neighbour's house, going there tonight, water, the street,
  someone missing), any confession he heard, the whole of `memory` and `sure`, and the backstory. The game shows
  these on `l`, and also on the first screen after any of them changes.
- **What you do:** §2.

The first screen of a session is Leo's card: `note` and `values` from `data.py:37-44`, the two family-address lines
and the backstory he holds. It is not repeated per turn.

### 1.3 Kept and dropped

| Line in Leo's prompt today | On screen | Why |
|---|---|---|
| "You are Leo, …", address, note, temperament, values (`world.py:1142-1148`) | once, on the card | who the player plays |
| Body line, "Since you last decided …" (`world.py:1014-1027`) | yes | perceived by the body |
| "About the can: X admitted taking it at …" (`world.py:1031-1042`) | yes | knowledge: a confession he heard |
| "About the can (some): you thought Daniel took it, at …" and "you have not settled …" (`world.py:1043-1063`) | **no** | built from the model's `suspects` answers; the player's stance is the player's |
| About food / neighbour / going there tonight / street / missing / water (`world.py:1065-1068`) | on `l`, and when they change | knowledge the code drew from what he perceived |
| "Against X (level): …" (`world.py:1069-1075`) | **no** | a level the model's `angry_at` raised; the events behind it are already lines he heard |
| "On your conscience …" (`world.py:1076-1079`) | never exists for Leo | culprit only |
| Backstory, carry-in, block C (`world.py:1242-1243`) | first screen of a day, and `l` | his memory |
| Block B, "What yesterday left in you" (`memory.py:49-58`) | **no** | written by Leo's night mind, which is no longer asked (§3) |
| What you are sure of / told today / tell whereabouts (`world.py:1202-1207`) | yes, as new lines | his knowledge |
| "Your own last words …" (`world.py:1208-1209`) | **no** | the player's echo already shows it |
| "What else happened …", trimming, "(earlier things, left out here)" (`world.py:1243-1259`) | new lines only; nothing is trimmed on `l` | the token budget is the model's |
| Now lines (`world.py:1166-1187`) | yes | perception |
| "You are the first to act in the kitchen this turn." | no | noise for a player |
| "What you have been doing … in a row" (`world.py:1083-1108`) | **no** | the model's loop aid |
| Options | yes, grouped | §2 |

### 1.4 Every place the prompt or the state could leak who took the can

| # | Where | What could leak | How the player game handles it |
|---|---|---|---|
| L1 | The terminal progress lines of `morning.run`'s `say` (`morning.py:138`). These cover the weather of every day ahead (`morning.py:143-148`) and every visit to the door ahead (`morning.py:149-155`); each turn's "model asked for N, Q1 for Daniel" and each Q1/Q2/Q5/Q6/Q7 line naming who and why (`morning.py:171-185`, `209-227`); each person's fasting and thirst stage at 21:00 (`morning.py:186-201`); everyone's bedtime choice and who went out with what result (`morning.py:241-248`); and the night minds (`morning.py:254-257`). | Truth about others and about the future, including the culprit's later fasting (L9). | In player mode `say` goes to `session.log` in the session folder, never to the terminal. The terminal prints only screens. |
| L2 | The files written at the end of a run: the story (`story.py:121-267`, which names the culprit at `story.py:138-140`); the transcript, with `"culprit"` (`world.py:442`), every person's `final_state` with guilt (`world.py:1316-1321`), and the chronicle with `fixed.culprit` (`chronicle.py:104-105`) and `knows_culprit` (`chronicle.py:159-168`); and the meta. | The culprit, by name. | They are written into the session folder when the session ends and are never printed. The play log keeps what Leo was shown in its own file (§8). |
| L3 | The cache file, which holds every prompt (`gemini.py:236-241`), including Daniel's "You know where the can went: you ate it yourself in the night, and nobody saw." (`world.py:468`) and "On your conscience" (`world.py:1076-1079`). | The culprit, on disk. | The game never reads it back except through `Oracle.ask`. It is on disk like the source code, and so is not a screen leak. |
| L4 | The face: "X looks <feeling>." writes another person's own feeling words, as their model answered them, into whoever is in the room (`world.py:1176`). `strength` shows any feeling with a stem from `SHOWN` (`world.py:72-77`, `165-170`), so "guilty and afraid" shows whole. | Daniel's model knows what he did; "guilty" or "ashamed" could reach Leo's screen. In the four caches scanned, 0 of Daniel's 7 shown feelings held a guilt word (§12, command 3). | On the **screen**, the face names only the word in the feeling that holds the strongest `SHOWN` stem ("Daniel looks afraid."). The others' prompts stay as today (§11, open point 1). |
| L5 | Leo's "About the can (level): you thought Daniel took it …" (`world.py:1043-1061`). | Not the culprit: someone else's guess (the model's) put in the player's head. | Dropped (§1.3). Leo's suspicion is never raised in player mode (§3). |
| L6 | The scenario `daniel_ate_it_leo_heard` (`data.py:215-219`) gives Leo a `can_note` ("you heard someone open a can … You did not see who."). | A clue by design. It does not name who. | The demo plays `daniel_ate_it` (the default, `data.py:220`), where Leo has no note. `--scenario` can pick the other on purpose. |
| L7 | The others' answers: `reason`, `feeling`, `suspects`, `angry_at` (`world.py:1300-1301`), and their night minds' memories and intents (`mind.py:435-446`). | What Daniel thinks, by his model, which knows. | Never on screen. They are in the play log's full file only (§8). |
| L8 | False accusation: the accused's grudge rises only if they did not take the can (`world.py:1817-1821`). Guilt: the culprit gains guilt when someone else is accused in his hearing, or when he is reassured (`world.py:1825-1833`, `996-1003`). | The others' **behaviour** differs with the truth: Mara accused falsely is indignant, while Daniel accused truly is not. | Kept. It is how people behave (the innocent are angry, the guilty uneasy), it is shown as their acts and words, and it is never written on Leo's screen as text. |
| L9 | Fasting: the culprit's last meal is the can at 03:00 of day 1 (`quiet.py:40`, `170-187`), 8 hours after everyone else's (`quiet.py:39`). His fasting stages, his Q1 asks and the stretches they start therefore come later. | Only through behaviour: Daniel weakening a little later. | Kept, as physics: a fed body holds out longer. No other person's body line is ever on Leo's screen. |
| L10 | Leo's options. `confess` is offered only to the culprit (`world.py:569-570`). `accuse_*` is limited only by `p.knows_culprit`, which a confession he heard sets (`world.py:564-568`, `1790-1793`). | Checked: nothing in Leo's option list depends on the culprit until he has heard a confession. | Frozen case C3 tests that Leo's screens are the same whoever took it. |
| L11 | The story text built mid-run (`morning.py:278`) and the night's story lines (for example "Daniel dozes off (draw …)", `night.py:521`). | Truth about others. | Written only into the L2 files. |
| L12 | Stop messages (`gemini.py:110`, `122`, `125-129`, `284-289`). | Nothing: they hold no prompt or answer. | Printed as they are, with "the session is saved". |

## 2. What the player can do

### 2.1 The same options

Each screen offers exactly `options_for(leo)` (`world.py:551-630`), in its order: the topic options first, then speech,
trip, water, `say_other`, sit, aside, search, go, rain, door and food. **Amended (the user, at S1):** the repetition
guard (a speech act used three turns in a row is not offered a fourth time, `world.py:626-629`) is off for the player
and on for everyone else. A real person can say a thing a fourth time; the guard is there against the model's loops.
Case C9 (§9) holds it.

The terminal groups them under Speak, Do, Go, Door and Food by `act_of(option)[0]` (`talk.py:17-54`). Grouping is
display only; the ids and the order the code uses are unchanged.

There are also four commands that are not acts:
- `w`: wait (§4).
- `l`: look (§1.2).
- `h`: help.
- `q`: save and stop (§8).

### 2.2 Own words

The model's contract for `say` (`world.py:41-53`) applies to the player, checked by the same rules as `parse`
(`world.py:1292-1299`):

- **A (speech) option** needs words. With none, the game asks "What do you say?", and no time passes.
- **Any other option** may carry words: "a short line they say while doing it".
- **`silent` with words** is refused with "Staying silent means saying nothing". `parse` drops such words for the
  model (`world.py:1298-1299`); a player should be told rather than lose their words.
- **Words without an option number** are `say_other`.
- **The words are tidied:** at most 240 characters (the model's "one or two short sentences"), whitespace collapsed,
  and `"` turned into `'`, because every hearer's line puts the words in double quotes (`world.py:1687`).

### 2.3 How the words relate to the act

**The act is what the code acts on. The words are only what is heard.**

- **The act sets the effects:** `accuse_daniel` sets who is addressed (`world.py:1785-1786`), `accused_by`
  (`world.py:1814-1816`), `heard_question` (`world.py:1787-1788`), Newness (`talk.py:89-94`), the guilt and grudge
  rules (`world.py:1817-1833`), the trip record (`world.py:1867-1881`), and the chronicle event and its witnesses
  (`chronicle.py:198-232`).
- **The listeners hear the act's gist and the words together**, as `line_text` writes them (`world.py:1639-1687`):
  `Leo accuses you of taking it: "You were up last night, Daniel. I heard you."`. Words that contradict the act cannot
  hide it; the listener's model gets both, as it does with an AI Leo today.
- **Words on a non-speech act** are heard as said while doing it: `Leo says to everyone, while searching: "…"`
  (`world.py:1755-1765`, `1683-1684`).
- **Words never become a fact.** A player who says "I saw Daniel at the counter last night" has said words. No
  belief, topic, `sure` line or number is made from them: beliefs come only from `tell_*` acts, with claims the code
  builds (`topics.py:208-225`). The others may believe him, as people believe a liar. The code owns the truth.

### 2.4 Decisions that are not a turn of his own

Each of these is a screen with its own short option list. Today each is a model call made on Leo's behalf:
- Someone takes Leo aside: accept or refuse (`world.py:1614-1630`).
- Someone hands Leo a portion: eat it or put it back (`world.py:944-962`).
- Bedtime (`night.py:484-522`), with the rain and further-along options when they apply.
- A night reaction to seeing or hearing someone go out (`night.py:660-725`).
- Leo's answer when someone tries to stop him going out (`night.py:727-737`).

## 3. Leo: what the code still tracks, what it stops deciding

**Still tracked by the code, exactly as today:**
- **Body:** hunger (`world.py:1497`), fasting, sleep debt, thirst, cold and wet (`quiet.py:287-325`), and the night's
  payback for his bedtime choice (`quiet.py:148-153`).
- **Knowledge:** `memory`, `sure`, `beliefs`, `topics`, `knows_culprit` (only from a confession he hears),
  `trip_heard`, `heard_question`, `searched`, `knows_empty`, `missing`, `water`, `door`, `rain_since`.
- **Place:** `room`, `activity`, his routine spans (`quiet.py:1029-1085`), and whether he is away after a night.
- **His acts:** `history`, `said_lines`, his trip positions (`world.py:1867-1881`; they feed the others' trip
  options, `world.py:718-726`, and Q5, `quiet.py:1195-1208`), `exchanged` (`quiet.py:1385-1388`; it feeds the meeting
  lines and Q2), and his Newness stances.
- **The chronicle event for every act** of his that someone perceived (`chronicle.py:198-232`), so the others' night
  minds see his acts as records.

**No longer decided by code or model:**

| What | Today | Player mode |
|---|---|---|
| Feeling | from his answer; shown on his face for 3 turns (`world.py:1717-1719`) | `p.feeling` stays None: the others never read "Leo looks …". Leo's note says "Annoyance shows as withdrawal and dry correction, not volume" (`data.py:39-40`), so a still face is in character |
| Suspicion | `Track` raised by `suspects` (`world.py:1533-1541`) | never raised; no line |
| Grudges | raised by `angry_at` (`world.py:1544-1547`), by false accusations against him (`world.py:1817-1821`), and by a confession after a denial (`world.py:1800-1810`); cooled by rest (`quiet.py:1087-1093`) | none: `take_answer` is not called for him and `add_grudge` skips him. Effects: Q2 between Leo and someone fires only on the other's grudge (`quiet.py:1136-1143`), and no `reassure_<q>` is withheld for a grudge of 3 (`world.py:577-579`) |
| Inner moments, lulls, food moments | asked when a level rises, a room is still, or a draw falls (`world.py:1566-1592`, `895-908`) | none; the player decides every turn anyway |
| Withdraw | code sends him to his room after a silent model answer with a grudge of 3 (`quiet.py:1409-1426`) | only if he chooses it (§4.2). `withdraw_why` already requires `mode == "model"` |
| Rest | code puts him on his bed when it falls due (`quiet.py:1107-1111`, `1240-1248`) | only if he chooses it. The body line says when his eyes are closing (`quiet.py:69`) |
| Night mind | one ask a night (`mind.py:435-446`) | not asked. No block B for him; block C has no thought of his |

**How the others still perceive Leo's acts.** Through the same `apply` (`world.py:1708-2009`), with the decision's
`mode` set to `"player"`:
- Everyone in his room gets the line with his words, and a trigger.
- Whoever he addresses acts first next turn (`world.py:1349-1361`).
- Rooms he is not in hear "Voices from the …" (`world.py:1464-1473`). The bathroom is the exception: nothing is heard
  in or out of it.
- His moves are seen going and coming (`world.py:1970-1976`, `1474-1486`).
- His acts at the door, the rain bin and the shelf do to the World what they do today (`world.py:1744-1748`,
  `1926-1949`).

The only change to how others hear him is Newness, in §5.1.

## 4. When the game waits and when time runs

### 4.1 Played turns (all of days 1 and 2; the stretches of days 3 on)

`Morning.turn` lets each person in each room act once a turn, in order (`world.py:1418-1453`). When Leo's place in his
room's order comes, `decide` (`world.py:1557`) asks the player and blocks until the player answers. So the player sees
what was said before him this turn, as Leo's prompt does.

**The game waits on every played turn Leo is awake in the house, unless the player's standing order is "wait".**
- **`w` (wait)** gives Leo the code's routine for this turn: carry on searching, keep sitting, or stay put silently
  (`world.py:868-875`, mode `routine`, as for anyone not asked). The order then stands, and turns run without a screen,
  until **something reaches Leo**:
  - a line added to his `memory` or `sure`, or a belief;
  - a trigger in his `triggers`: a line, someone coming in, voices, the knock, rain, or being taken aside or handed a
    portion;
  - one of his own body stages rising while he is awake. A stage that rises while he rests is on his next screen
    (as Q1 does not fire for someone asleep, `quiet.py:1178-1180`).
- **A played stretch ending** brings the quiet-time choice (§4.2).
- **The end of the day** brings bedtime (§4.3).
- **A plain choice**, anything but `w`, applies for that turn only.

A real person sitting through a quiet moment does nothing until something happens to them. "Wait" is that, and it
does not make the player press a key every 3 minutes of nothing.

### 4.2 Quiet time (days 3 on)

`quiet.play` (`quiet.py:1572-1632`) plays stretches in turns. Between them, `step` (`quiet.py:1297-1313`) and
`next_event` (`quiet.py:1315-1337`) jump from one event to the next. Player mode adds two things.

**1. The quiet-time choice.** When a stretch closes with Leo awake (`quiet.py:1604-1609`), the player is asked once,
before `assign` would give Leo a routine (`quiet.py:1250-1283`):

```
── Day 3 · 07:18 · the kitchen ──── the talk has died down.
  1 sit in the kitchen      2 lie down on your bed      3 keep to your own room
  4 do something now  (the full option list)
```

- Choices 1 to 3 start that routine for Leo through the same `start` (`quiet.py:1029-1052`). A rest gets its length
  from the same seeded `rest_length` and `rest_end` (`quiet.py:165-167`, `1095-1105`), so the body decides when he
  wakes. A "keep to your room" ends when he leaves it or after 2 hours (`quiet.py:43`). A move to the room is seen
  going and coming (`quiet.py:1113-1128`).
- Choice 4 shows the turn screen (§1.2). See point 2 below.

**The jump.** The code then steps quiet time as today, for everyone, and **shows the next screen at the first minute
at which something reaches Leo**, by the same test as "wait" in §4.1. Most `step` events add a line only to those who
perceive them:
- an arrival is seen only by those awake in the room (`quiet.py:1124-1127`);
- rain is heard by everyone awake (`quiet.py:375-414`);
- a knock is heard by whoever its draw reaches (`quiet.py:586-608`);
- the evening line goes to the room Q5 fires in (`quiet.py:1234-1235`);
- his own rest ends (`quiet.py:1072-1084`).

So everything Leo does not perceive passes with no screen, and the clock on the next screen jumps. Every quiet trigger
that names Leo makes a screen in place of his ask: Q1 for his own need, Q5 if his trip position is the latest, Q6 if he
is in the room it plays, Q7 if he hears the knock. That room is then played as today, so its stretch counts its asks
as today. 21:00 always makes a screen: bedtime.

**2. The player acts in quiet time** (choice 4, or any act on a screen in quiet time). This starts a played stretch
in Leo's room with trigger `"P"`, through `q.begin(stretch, STRETCH_ASKS, …)` (`quiet.py:442-448`, `46`): 8 asks,
inside the day's ordinary 40. The act is taken on the next turn of the grid (`quiet.grid`, `quiet.py:120-122`). The
stretch then runs like any other: it ends when its talk ends (`quiet.py:1604-1609`) and is capped by the day's budget
(`quiet.py:428-435`).

Take a player who walks into the back room at 14:00 to speak to Mara. A real family member would answer him, so the
others are asked. The cap means that after a day of talk the family, like a tired one, goes quiet.

### 4.3 Night

- **Bedtime** is one screen for Leo (`night.py:484-522`). It shows the same Now lines his night prompt has: "Now it
  is night." with his day's gap line, the beds, the dark kitchen, rain, and his promise if he made one.
- **A reaction or an answer** is a screen only if the night's draws bring one to him (§2.4).
- **Everything else in the night** is drawn by code, as today: who wakes, the street, the return (`night.py:546-659`).
- **The next morning's first screen** carries his night lines and the day's opening (§1.2).
- **The others' night minds run** (3 asks). Leo's does not (§3).

### 4.4 The game ends

- **Leo away:** if he goes out in the night and does not come back (`night.py`, `missing`), the player has no one to
  play. The last screen says what Leo last perceived, and the session ends.
- **The last day:** `--days N`, default 10, ends after its bedtime.
- **The session cap** (§5.3) or `q` saves the session and stops it; it can be resumed (§8).

## 5. When the others are asked, and what an hour costs

### 5.1 As today, with three changes in player mode

**The model is asked for Elena, Daniel and Mara exactly when it is today.** In played turns that is when:
- something social reached them: a new line, an arrival, being addressed, voices of a new line, or a quiet trigger
  waiting for them (`world.py:1339-1347`, `1593`);
- a level rose since they last decided, at most every 9 minutes (`world.py:1578-1585`, `82`);
- the trip concern starts (`world.py:1588-1590`);
- a food moment's draw falls (`world.py:1566-1567`);
- they are taken aside or handed a portion (`world.py:1430-1453`).

Otherwise the code decides their routine (`world.py:1599-1600`):
- In quiet time, the code gives them their routines (`quiet.py:1250-1283`) and asks them only for Q1, Q2, Q5, Q6 and
  Q7.
- At night, everyone present is asked their bedtime once, and reactions are asked when the draws bring them.
- Each night mind is one ask per person.
- The caps hold as today: 150 per scene on days 1 and 2 (`config.json` `max_calls_per_morning`, `gemini.py:286-289`);
  on quiet days the morning's 24, a stretch's 8, the ordinary 40, Q5's and Q6's 8, Q7's 18, at most 56 a day, and at
  most 12 quiet asks, 4 per person (`quiet.py:45-46`, `103`, `464-479`).

**Three changes, in player mode only. Each is argued against first.**

1. **Every line the player speaks is new** (Newness, `talk.py:80-123`), so it starts or keeps the talk in his room
   and reaches its hearers as a new trigger.
   - *Against:* the player can keep a room talking for as long as they like, and ask after ask goes out.
   - *For:* today a `say_other` or a reassurance is "not new" (`talk.py:103-104`, `123`). Spoken in a still room, it
     reaches no one as a trigger (`world.py:1342`), so nobody answers. A real family answers when spoken to; a
     player's words met with silence is the most visible failure a player can meet. The day's caps bound the cost,
     and silence once they are spent reads as a family that has stopped talking.
2. **An act in quiet time starts a stretch `"P"`** with the 8 asks of any stretch (§4.2).
   - *Against:* it is a new door to asks.
   - *For:* without it, the player could not speak to anyone between triggers, and no real person waits for a need
     to cross a line before speaking. Its 8 count inside the ordinary 40.
3. **Leo's grudges stay at 0** (§3). Q2 for a pair with Leo then rests on the other's grudge alone (`quiet.py:1136-1143`).

### 5.2 Requests for an hour of play

**Data (v23, seed 2, days 1 to 10; days 1 and 2 are v16's cached answers).** Played turns, the turns Leo is awake in,
and asks per person, from `runs/v23/daniel_ate_it-seed2.transcript.json` (§12, command 1):

| Day | Played turns | Leo awake in | Asks D, E, L, M | Others' asks | Leo's asks |
|---|---|---|---|---|---|
| 1 | 30 | 30 | 14, 13, 14, 12 | 39 | 14 |
| 2 | 30 | 30 | 5, 8, 5, 6 | 19 | 5 |
| 3 | 10 | 10 | 10, 10, 10, 10 | 30 | 10 |
| 4 | 8 | 8 | 8, 8, 8, 8 | 24 | 8 |
| 5 | 14 | 14 | 14, 11, 11, 12 | 37 | 11 |
| 6 | 16 | 9 | 12, 14, 10, 11 | 37 | 10 |
| 7 | 12 | 12 | 12, 9, 10, 9 | 30 | 10 |
| 8 | 14 | 11 | 14, 11, 10, 13 | 38 | 10 |
| 9 | 14 | 11 | 14, 11, 10, 11 | 36 | 10 |
| 10 | 12 | 12 | 12, 6, 10, 8 | 26 | 10 |

Nights (the bedtime ask is everyone's; reactions and answers come with a trip): nights 1, 3, 4, 6, 8 and 9 had 4
asks (Leo 1); night 2 had 7 (Leo 2); nights 5 and 7 had 8 (Leo 2). Each night mind is 4 asks, one of them Leo's. The
v23 meta's totals are 414 day asks, 47 night asks and 36 mind asks, 497 in all (§12, command 2). This matches v23's
"asks recorded: 497" (`reports/v23.md:236`).

**What the player removes.** Leo's 98 day asks, 12 night asks and 9 mind asks. **What the others ask** is assumed to
be what v23's others asked, with the player in Leo's place. An AI Leo spoke in 77 of his 98 asks (§12, command 1),
so v23 already holds a talking Leo. A more talkative player makes more asks, up to the caps (below).

**Player decisions (D)** are the screens:
- one for every played turn Leo is awake in;
- his night screens (1 a night, 2 on a trip night);
- **assumed, not measured:** 4 quiet-time screens per quiet day (the quiet-time choices and the jumps that reach him;
  v23 days 3 to 10 had 2 to 4 stretches a day).

**Others' asks (A)** are their day asks, their night asks and their night minds, 3 a night.

| Phase | D | A | Asks per decision |
|---|---|---|---|
| A, days 1–2 with nights 1–2 | 30 + 1 + 30 + 2 = **63** | 39 + (3 + 3) + 19 + (5 + 3) = **72** | 72 / 63 = **1.14** |
| B, days 3–10 with nights 3–9 | (10+8+14+9+12+11+11+12) + 8×4 + 9 = 87 + 32 + 9 = **128** | 258 + 27 + 21 = **306** | 306 / 128 = **2.39** |
| All | **191** | **378** | 1.98 |

(Phase B's A: day asks 30+24+37+37+30+38+36+26 = 258. Nights 3–9: 3+3+6+3+6+3+3 = 27. Minds: 7 × 3 = 21.)

**Time per decision.** T = s + 4.6 × a:
- s is the player's thinking and typing time. It is **assumed, not measured**: 35 s central, 20 s fast, 50 s slow.
- 4.6 s is v23's measured time per live ask, which the 4.5 s gap between calls sets (`config.json`
  `min_seconds_between_calls`, `gemini.py:87-92`). Session 3 ran 148 live asks from 23:04:06 to 23:15:22, 676 s, so
  4.57 s each (`reports/v23.md:52`).
- The player waits for the others' answers before the next screen.

| Pace | Phase A: T, decisions an hour, asks an hour | Phase B: T, decisions an hour, asks an hour |
|---|---|---|
| central, s = 35 | 35 + 5.26 = 40.3 s; 3600 / 40.3 = 89.4; × 1.14 = **102** | 35 + 11.0 = 46.0 s; 78.3; × 2.39 = **187** |
| fast, s = 20 | 25.3 s; 142.5; **163** | 31.0 s; 116.1; **278** |
| slow, s = 50 | 55.3 s; 65.1; **74** | 61.0 s; 59.0; **141** |

**The first hour from day 1, central pace.** Phase A takes 63 × 40.3 = 2,536 s (42 min) and makes 72 asks. The 1,064 s
left, at 46.0 s each, are 23 decisions of phase B and 23 × 2.39 = 55 asks. The total is **127 requests**, at about
the middle of day 4. At the fast pace, phase A takes 1,591 s (27 min, 72 asks), and the 2,009 s left are 64.8
decisions and 155 asks, **227 requests** in the first hour.

**Later hours** (phase B only): 187 at the central pace, 141 slow, and **278 fast, which is over the target.**

**The worst a player can make.** At most 3 others are asked per played turn (one decision each), plus a few asides
and handed portions. On a quiet day the code's caps bound them at 56 by day, 3 to 6 at night and 3 night minds, about
65. On days 1 and 2 the bound is 150 per scene, and at most about 90 in day 1's 30 turns.

**Requests, not answers.** The quota counts requests. v23 sent 472 requests for 401 live asks: 81 `503` retries in
sessions 1 and 2, and none after (`reports/v23.md:55-57`). Whether a refused `503` counts against the free daily quota
is **NOT KNOWN**. If it does, the central later hour is about 187 × 472/401 = 220.

### 5.3 The session cap

Player mode stops a session cleanly once it has sent `play_max_requests` API requests (`config.json`, default 250,
counted on the client's `requests`, retries included, `gemini.py:112`), before it sends the next one. It stops the way
`CallCapReached` does today (`gemini.py:286-289`). The play log is saved, and the stop message says how to resume
(§8). With 500 a day, that is two capped sessions a free day. At the central pace an hour stays under the cap, so the
cap only stops a fast player, after about 54 minutes of phase B.

## 6. Interface

### 6.1 Now: the terminal

`python play.py --seed 2 [--days 10] [--fake] [--resume runs/play/<session>]`. `--fake` uses `FakeClient`
(`gemini.py:143-214`) for the others and calls no API. Without it, the key is read from `GEMINI_API_KEY` as today
(`gemini.py:34-39`).

- **The engine** is `morning.run` (`morning.py:111`) given a `Player`. Its `decide(screen)` gets a `Screen` (header,
  new lines, Now lines, the option list with ids, labels and speech flags, and the decision's kind: turn, quiet-time,
  aside, handed portion, bedtime, reaction or answer) and returns `{"option", "say"}`.
- **The terminal player** renders the screen (§1.2) and reads one line with `input()`. A number picks an option. A
  number then words picks it and says the words. Words alone are `say_other`. `w`, `l`, `h` and `q` are the commands.
- **A bad line** (an unknown number, a speech option without words, words on `silent`) is answered on the spot, and
  no time passes.
- **While the others' answers come**, the terminal shows "…" and nothing else.

### 6.2 Later: a local web page

What it would need, and no more:

1. **The engine in a worker thread**, with `Player.decide` blocking on a queue. The engine is synchronous and nested:
   `decide` is called deep inside `Morning.turn` and `Night.run`. A thread keeps it unchanged; a terminal and a page
   are two ways of filling the queue.
2. **A local server from the standard library** (`http.server`), bound to `127.0.0.1` only, with three routes:
   - `GET /screen`: the current `Screen` as JSON, with `"waiting": true` while the others are being asked;
   - `POST /choice`: `{"option", "say"}`, checked by the same rules as §2.2;
   - `GET /log`: the shown log (§8).
3. **One static HTML page.** It polls `/screen`, renders the same sections as §1.2 with options as buttons and a text
   box for words, and shows a "thinking" state while waiting.
4. **The key stays in the server process's environment** and never reaches the page.
5. **The same session folder and play log as the terminal**, so a session started in one can be resumed in the other.

## 7. With no player, runs behave exactly as today

- `player=None` is the default everywhere: `morning.run`, `Morning`, `Night`, `NightMind` and `quiet.play`. Every
  hook is `if self.player is not None and p.id == self.player.pid`. With no player, no prompt, option list, order
  string, seed string, cap or file changes. `morning.py` itself keeps its arguments and output.
- **Check 1:** the full test suite passes unchanged: today's tests, untouched, plus the new ones.
- **Check 2:** a fake run (`python morning.py --seed 1 --fake --days 4 --out play_check`) writes a story and a
  transcript whose sha256 equal those of the same command at the commit before the change. Both are recorded in the
  implement report.
- **Check 3, when a run mode allows it:** `--replay` of v23 from `cache/v23` stays byte-identical to
  `runs/v23/daniel_ate_it-seed2.md`, with 0 API calls. A replay is a run, which CLAUDE.md allows only under MODE run.

## 8. The play log, and bringing it back

Each session has a folder, `runs/play/<scenario>-seed<N>-<UTC stamp>/`, and its answers go to
`cache/play/<model>-<scenario>-seed<N>.json`, so v23's caches are never written to.

- **`play.jsonl`**, the full log, one JSON object a line, in order. It holds the truth and is not for reading during
  play:
  - `{"t": "screen", "n", "day", "minute", "kind", "text", "options": [ids]}`: the screen exactly as shown;
  - `{"t": "choice", "n", "option", "say", "input", "seconds"}`: the raw line typed, and the time from screen to
    answer (so the next estimate can use measured paces in place of §5.2's assumptions);
  - `{"t": "act", "day", "minute", "who", "room", "option", "words", "mode", "feeling", "reason", "seen_by_leo"}`:
    every act of the others, including those Leo did not perceive. `seen_by_leo` is whether a line of it reached him;
  - `{"t": "night", …}`: each night decision of the others, and the night's events;
  - `{"t": "session", "start", "end", "asks_live", "asks_cached", "api_requests", "stopped"}`.
- **`shown.md`**: only the screens and the player's choices, in order. It is safe to read and to show someone.
- **`session.log`**: what `say` printed (L1).
- **At the end**, the run's usual story, transcript and meta (L2).

**Resuming and bringing it back.** `--resume <folder>` reads the logged choices in order and feeds them to a replay
player. Each replayed screen must equal the logged one byte for byte; if one differs, the session stops with "the log
and the game differ at screen n". The world is seeded, the draws are seeded and the others' answers come from the
cache, so the replay reaches the last screen with 0 live asks, and live play goes on from there. The same folder
replayed with `--replay` (no client) is how you bring a session back to me: I can rebuild every screen and every act
from it without a single request.

## 9. Frozen cases

Each case is written so it can become one failing test before its step is built. All use `FakeClient` or a scripted
client, `Oracle` and `Cache` in a temporary folder, as the tests do now (`test_morning.py:259-260`). They use a
`ScriptedPlayer` (choices from a list), and `daniel_ate_it`, seed 1, unless they say otherwise. "Scripted others" means
a client that answers each person's prompt with a fixed option by the prompt's first line, the feeling "calm" (shown on
no face), and the words "W-<person>-<minute>" for speech.

**C1. Leo accuses Daniel at minute 03: who hears it.** Scripted others: at minute 00 Mara answers `go_back_room`;
Daniel and Elena answer `silent` throughout. The player chooses `silent` at minute 00, then at minute 03 chooses
`accuse_daniel` with the words `You were up last night, Daniel.`. After turn 1:
- Daniel's `memory` holds `(3, 'Leo accuses you of taking it: "You were up last night, Daniel."')`.
- Elena's `memory` holds `(3, 'Leo accuses Daniel of taking it: "You were up last night, Daniel."')`.
- Mara's `memory` holds `(3, "Voices from the kitchen.")` and no line holding the words.
- Leo's `memory` holds `(3, "you accused Daniel.")`.
- `daniel.accused_by == {"leo": 3}`. Right after Leo's act, `daniel.addressed["accused"] is True`.
- Daniel's next decision, later in turn 1 if he has not yet acted in it, else in turn 2, comes before anyone else left
  in the kitchen, with the order reason "just accused by Leo" (`world.py:1349-1361`). It is a model ask whose
  triggers include `Leo accuses you of taking it: "You were up last night, Daniel."`.
- Daniel's grudges hold no event against Leo (he took it). Leo's suspicion strength and every grudge of Leo are 0.
- Once day 1 is added to the chronicle, its `accuse` event at minute 3 has actor `leo`, target `daniel` and witnesses
  `{"leo": "did", "daniel": "saw", "elena": "saw", "mara": "voices"}`.
- No prompt beginning `You are Leo,` was sent to the oracle.

**C2. The player rests, and time jumps to the next thing Leo perceives.** Day 3 of a scripted-others run (all
`silent`). When the morning stretch ends at minute M0 (`q.morning_end`), the player's quiet-time choice is "lie down on
your bed". Take `until = q.rest_end(leo, M0, quiet.rest_length(1, 3, "leo", 1))`, and assume no visit is due in
`(M0, until]` (`street.next_visit`); the test picks a seed for which this holds.
- The next screen is at minute `until`.
- Its first new line is `you got up from your bed.`.
- No screen was shown at any minute in `(M0, until)`, and the player made no choice between the two screens.
- Leo's span in `q.spans` is `{"routine": "rest", "room": "brothers_room", "start": M0, "end": until}`, with `ended`
  `"time"` or `"rested"` as `rest_end` decided.

**C3. Nothing shown to Leo depends on who took the can.** Scripted others: always `silent`. The player script on day 1
is: minute 00 `ask_who` ("Who took it?"); 03 `accuse_daniel` ("Was it you?"); 06 `accuse_mara` ("Or you?"); 09
`search`; 12 `keep_searching`; 15 `reassure_all` ("We'll manage."); then `w` to the end of the day. At night it is
`sleep`, and on day 2 `w` throughout. The same script is played three times: `daniel_ate_it`, `mara_ate_it` and
`miscount`.
- The three lists of screen texts are identical, byte for byte.
- No screen in any run holds `you ate it yourself`, `On your conscience`, `eats a can`, `Nobody sees` or `culprit`.
- The process's stdout holds no line from `morning.run`'s `say`: no `model asked for`, `Q1,`, `stages:` or
  `bedtime Daniel`.

**C4. The act decides; the words are heard.** Day 1, everyone in the kitchen, scripted others `silent`.
- (a) At minute 00, `reassure_mara` with `Nobody thinks it was you, Mara.`: Mara's `memory` holds
  `(0, 'Leo reassures you: "Nobody thinks it was you, Mara."')`. `mara.addressed["accused"] is False`. `accused_by` is
  empty for everyone, and Daniel's guilt is unchanged at 1 (the reassured person is not the culprit).
- (b) At minute 03, `search` with `Let me look.`: Elena's `memory` holds
  `(3, 'Leo says to everyone, while searching: "Let me look."')`, and Leo's activity is `searching`.
- (c) At minute 06, the number of `say_other` with no words: the game answers "What do you say?". The turn's minute
  stays 06 and no ask is sent.
- (d) The number of `silent` followed by `Not a word`: refused with "Staying silent means saying nothing", and no time
  passes.
- (e) The words `He said "no"` reach the hearers as `He said 'no'`.

**C5. Nobody decides for Leo but the player.** Days 1 to 3 played with a scripted player over a `FakeClient` run.
- No oracle prompt begins `You are Leo,`, and no night-mind prompt is written for Leo.
- Every decision of Leo's has `mode` `"player"` or `"routine"`, and never `"model"` or `"fallback"`.
- At the end, Leo's suspicion strength is 0, his `grudges` are empty or all at 0, and `leo.feeling is None`.
- No prompt sent for anyone holds `Leo looks`.
- With `player=None`, the same command's story and transcript sha256 equal the values recorded before the change (§7,
  check 2).

**C6. The session cap stops cleanly and resumes with no live ask.** A `FakeClient` run with `play_max_requests = 20`,
and a scripted player that speaks on every screen.
- The session stops with exit code 3 and the message `stopped: this session's 20 requests are spent.` after the 20th
  request was answered and before a 21st was sent (`client.requests == 20`).
- `play.jsonl` ends with a `session` record whose `stopped` holds that message.
- `--resume` of the folder replays every logged choice and reaches the last logged screen with 0 live asks, its text
  byte-identical to the logged one.
- Then the first new request is the 21st prompt the first session would have sent.

**C7. Wait in played turns: nothing reaches Leo, so nothing is shown.** Day 1, scripted others always `silent`. At
minute 00 the player chooses `go_brothers_room`; at minute 03, alone there, `w`.
- No further screen on day 1. Leo's decisions from minute 03 to 87 are all `mode` `"routine"`, option `silent`.
- The next screen is night 1's bedtime, with the options `sleep`, `lie_awake`, `watch_door` and `go_next_door`.
- Variant: Daniel's scripted answer at minute 30 is `say_other` with words. Voices are written at the end of the turn
  (`world.py:1464-1473`), after Leo's minute-30 decision. Leo's next screen is therefore at minute 33, and its new
  lines are `min 30  Voices from the kitchen.`.

**C8. A face on the screen names only what a face shows.** Day 1, scripted others; at minute 00 Daniel answers
`silent` with the feeling `guilty and terrified`.
- Leo's screen at minute 03 holds `- Daniel is here, staying put. Daniel looks terrified.`, and no screen holds
  `guilty`.
- The prompt sent for Elena at minute 03 holds `Daniel looks guilty and terrified.`, as today. She is asked then
  because a shown face is a trigger while the kitchen is talking (`world.py:1343-1346`).
- From minute 12 (after `FEELING_SHOWS_FOR_TURNS` = 3 turns, `world.py:78`) no face of Daniel is on Leo's screen.

**C9 (added by the user at S1). The repetition guard is off for the player only.** With the player as Leo,
`accuse_daniel` chosen three turns in a row (minutes 00, 03 and 06) is still offered on the fourth screen (minute 09).
For a person the model plays, three accusations in a row withhold `accuse_*` on the fourth, as today, with a player in
the house or not.

## 10. The build, in three steps

**As built (reports/play_s1.md):**
- S1's entry point is `player.play_days`, which plays days 1 and 2 with their nights and night minds and prints
  nothing. `morning.run` is not changed. C3's stdout check is made on `play_days`.
- C5 covers days 1 and 2 and their nights, as day 3 is a quiet day (S2).
- On days 1 and 2 a "wait" is not broken by the hunger word rising: the "body stages" of §4.1 are the quiet day's
  needs.

**S1. The player in the engine; days 1 and 2 and their nights; no terminal.**
- **Code:** `player.py` (the `Player` interface, `Screen`, `ScriptedPlayer`). The hooks in `Morning.decide`,
  `decide_aside` and `decide_given`, with Leo's food, inner and lull moments off and `take_answer` skipped. Newness
  for the player's lines, and the screen face. The hooks in `Night.ask` and `NightMind.run` (Leo skipped). `say` to a
  file in player mode.
- **The screen builder:** `prompt_for` in player mode, then the §1.3 filter.
- **Ends testable:** C1, C3, C4, C5, C7 and C8 are seen failing first, then pass. The full suite and §7 check 2 pass.

**S2. Quiet days with a player.**
- **Code:** the quiet-time choice at a stretch's end; the jump to the next minute that reaches Leo; the `"P"`
  stretch; Q1, Q5, Q6 and Q7 for Leo as screens; rest and withdraw only when chosen.
- **Ends testable:** C2 is seen failing first, then passes. A scripted player plays days 1 to 4 over `FakeClient` to
  bedtime of day 4 with no error, and §7 check 2 holds again.

**S3. The terminal, the play log, the cap and resume.**
- **Code:** `play.py` (the arguments of §6.1, rendering, input and its checks); `play.jsonl`, `shown.md` and
  `session.log`; `play_max_requests`; `--resume`.
- **Ends playable and testable:** C6 is seen failing first, then passes. `python play.py --seed 2 --fake` can be
  played by hand to night 1. The first live session of the demo, with the API, is then its own prompt under MODE run;
  its play log is the first read of a real player's pace (§5.2's s).

The web page (§6.2) is not a step here; nothing in S1 to S3 is built against it.

## 11. Open points, decided by the user at S1

1. **The face in the others' prompts: as designed.** The screen gets the face word only (L4). The others' prompts keep
   the whole feeling text, so their model behaves as the one v23 measured; 0 guilt words were shown in 4 caches. If a
   play log shows a guilt word in Daniel's face in someone's prompt, this can be looked at again.
2. **Dozing: none.** The code never puts the player's Leo to sleep. With sleep debt at 24 the body line says "your
   eyes close on their own" (`quiet.py:69`), but he stays up if the player says so.
3. **The repetition guard** (`world.py:626-629`): off for the player only, on for everyone else (§2.1, C9).

## 12. Commands and output

All from `Prototypes/llm-morning/`. `GEMINI_API_KEY` was cleared for each command, and none sends a request. The
scripts are in the session's scratchpad. They are short and their full text is below, so they can be run again.

**1. Played turns and asks per person, from the v23 transcript.**
```
$ .venv/Scripts/python.exe -I count_asks.py runs/v23/daniel_ate_it-seed2.transcript.json
scene  turns  leo_in  asks(D,E,L,M)  others  leo  leo_words  others_per_turn  leo_rested_turns
day1      30      30  14,13,14,12         39   14         9             1.30      0
day2      30      30   5, 8, 5, 6         19    5         3             0.63      0
day3      10      10  10,10,10,10         30   10         8             3.00      0
day4       8       8   8, 8, 8, 8         24    8         7             3.00      0
day5      14      14  14,11,11,12         37   11        11             2.64      0
day6      16       9  12,14,10,11         37   10         6             2.31      7
day7      12      12  12, 9,10, 9         30   10         8             2.50      0
day8      14      11  14,11,10,13         38   10         9             2.71      3
day9      14      11  14,11,10,11         36   10         9             2.57      3
day10     12      12  12, 6,10, 8         26   10         7             2.17      0
night   asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
night2  asks  7 (leo 2); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara', 'reaction:leo', 'answer:daniel', 'reaction:mara']
night3  asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
night4  asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
night5  asks  8 (leo 2); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara', 'reaction:leo', 'answer:daniel', 'reaction:elena', 'reaction:mara']
night6  asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
night7  asks  8 (leo 2); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara', 'reaction:leo', 'answer:daniel', 'reaction:elena', 'reaction:mara']
night8  asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
night9  asks  4 (leo 1); kinds ['bedtime:daniel', 'bedtime:elena', 'bedtime:leo', 'bedtime:mara']
{'turns': 160, 'leo_turns': 147, 'leo_asks': 98, 'other_asks': 316, 'night_other': 35, 'night_leo': 12}
```
`leo_in` counts the played turns in which Leo was in the house and not on a rest span. `leo_rested_turns` counts those
in which he was resting.

**2. The v23 meta's ask counts per scene.**
```
$ (PowerShell) read runs/v23/daniel_ate_it-seed2.meta.json
day1 model_decisions=53 fallbacks=0 routine=67 api=0 live=0 cached=53
day2_asks=24 model_dec=24
night1=4 mind1=4 night2=7 mind2=4 day3=40
day4: model=32 fallback=0 routine=0 day_asks=32 quiet_asks=2 stretches=2 morning_end=18 | night3 asks=4 mind asks=4
day5: model=48 fallback=0 routine=8 day_asks=48 quiet_asks=4 stretches=4 morning_end=18 | night4 asks=4 mind asks=4
day6: model=47 fallback=0 routine=17 day_asks=47 quiet_asks=3 stretches=4 morning_end=21 | night5 asks=8 mind asks=4
day7: model=40 fallback=0 routine=8 day_asks=40 quiet_asks=3 stretches=4 morning_end=15 | night6 asks=4 mind asks=4
day8: model=48 fallback=0 routine=8 day_asks=48 quiet_asks=3 stretches=4 morning_end=18 | night7 asks=8 mind asks=4
day9: model=46 fallback=0 routine=10 day_asks=46 quiet_asks=3 stretches=4 morning_end=18 | night8 asks=4 mind asks=4
day10: model=36 fallback=0 routine=12 day_asks=36 quiet_asks=2 stretches=3 morning_end=18 | night9 asks=4 mind asks=4
day3 quiet: day_asks=40 stretches=3 morning_end=18
```
The day asks sum to 53 + 24 + 40 + 32 + 48 + 47 + 40 + 48 + 46 + 36 = 414, the nights to 47 and the minds to 9 × 4 =
36: 497.

**3. Leak scans of the caches (L4, L10).**
```
$ .venv/Scripts/python.exe -I leak_scan.py cache/v23/gemini-3.5-flash-lite-daniel_ate_it-seed2.json
prompts in cache: 548 | Leo's: 132
distinct 'Daniel looks ...' shown to Leo: 1 | total lines: 3
with a guilt word: 0 lines, 0 distinct
Leo prompts holding the culprit's own lines ('you ate it yourself' / 'On your conscience'): 0
$ (the same for cache/v16 seeds 1, 2, 3)
seed1: prompts 236 | Leo's 58 | 'Daniel looks' lines 1 | with a guilt word 0 | culprit's own lines 0
seed2: prompts 147 | Leo's 37 | 'Daniel looks' lines 3 | with a guilt word 0 | culprit's own lines 0
seed3: prompts 184 | Leo's 47 | 'Daniel looks' lines 1 | with a guilt word 0 | culprit's own lines 0
$ .venv/Scripts/python.exe feeling_scan.py . cache/v23/…seed2.json cache/v16/…seed1.json cache/v16/…seed3.json cache/v22/…seed2.json
cache/v23/…seed2.json: Daniel answers 149, feeling shown on the face 2, of them with a guilt word 0: []
cache/v16/…seed1.json: Daniel answers 58, feeling shown on the face 2, of them with a guilt word 0: []
cache/v16/…seed3.json: Daniel answers 45, feeling shown on the face 1, of them with a guilt word 0: []
cache/v22/…seed2.json: Daniel answers 148, feeling shown on the face 2, of them with a guilt word 0: []
```
`feeling_scan.py` imports `world.strength` from the prototype, so it runs without `-I`, with `PYTHONDONTWRITEBYTECODE=1`.

**The scripts.**

`count_asks.py`: for each `dayK` of a transcript, it counts `turns`, the turns where `leo` is in some room of
`t["rooms"]` and not inside one of his `rest` spans (`day["quiet"]["spans"]`), and the acts with `mode` `model` or
`fallback` per person, and Leo's acts with words. For each night it counts `decisions` per person and `ask` kind.

`leak_scan.py`: over a cache file, it takes the prompts starting `You are Leo,`, counts the lines matching
`Daniel looks ([^.]*)\.`, the matches of `guilt|asham|remorse|sheepish|caught|defensive|evasive`, and the prompts
holding `you ate it yourself` or `On your conscience`.

`feeling_scan.py`: over cache files, it takes the answers to prompts starting `You are Daniel,`, reads their
`feeling`, and counts those with `world.strength(feeling) > 0`, and those of them matching `guilt|asham|remorse`.

**4. The diff, at the design's delivery** (before the S1 amendments above). This file was new. It was marked with
`git add -N` (intent to add, nothing staged) so that `git diff --stat` lists it:
```
$ git diff --stat
 Prototypes/llm-morning/reports/play_design.md | 717 ++++++++++++++++++++++++++
 1 file changed, 717 insertions(+)
```
