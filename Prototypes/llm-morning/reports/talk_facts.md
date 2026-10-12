# Talk facts: bringing something up, learning of what one missed, and the stores in the night mind

Investigation, read-only. Starts from `reports/probe_after.md`: the visitor was not mentioned after 09:51, Daniel was
never told, and the night minds wrote "none left" against about 95 litres. Paths are from `Prototypes/llm-morning/`;
line numbers are at HEAD 65fee7c. No live call was made. Every script ran with `GEMINI_API_KEY` unset.
Nothing in the repository was changed except `runs/talk_facts/` and this report.

## Answers in short

| # | Question | Answer |
|---|---|---|
| 1 | Options; which take a topic; `say_other` | No option has a topic field: an `Option` holds id, label, speech flag and act (kind, target, to, partner) (`world.py:303-305`). `say_other` is offered as `- say_other: (speech) say something else` (`world.py:578`, `1180`). Its words are the model's `say`, with no check on what they are about. A listener keeps the words in a line `"<Name> says to everyone: "<words>""`, a `heard` entry of kind `say`, and a trigger. Chosen **1 time** in 669 distinct cached decisions (offered in 608 of them). |
| 2 | How options are decided; any built from the past | `options_for` (`world.py:539-615`): from who is here, the room, the shelf, the water level, the door, the rain and the trip state. Some options are gated by state left by past acts (a question heard, a confession, grudge ≥ 3, trip positions heard, a room searched, the water rule). No option is built from a sure line, a memory line or an earlier event: **NOT FOUND**. |
| 3 | Learning of an event not perceived | For a door visit: **NOT FOUND**. The door summary and its records go only to those who perceived the visit (`quiet.py:830-874`; `night.py:1066-1069`). Paths that do exist: who went out at night is the whole house's by morning (`night.py:195-205`); the water line is given to everyone in the house (`quiet.py:327-338`); a confession heard sets `knows_culprit` (`world.py:1752-1758`). A line whose words mention an event gives the listener only the words: no other field changes for `say_other` (`world.py:1730-1747`). |
| 4 | Stores in the night-mind prompt | **Yes, water.** The night-mind prompt carries `inside_lines` except lines that start "About food:", "About the neighbour's house:" or "About going there tonight:" (`mind.py:33`, `413`). The "About water:" line stays (`world.py:1052-1053`). Leo's night-3 prompt, line 10: `About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since 09:45, you share it out by the cup: five cups each a day.` No "About food:" line. The only shelf line is record D3-001 ("…this morning it holds 0 portions"). |
| 5 | Day 4: block B "none left" next to the water line | **Yes**, for Elena and Leo. The day-4 water line was built (`quiet.py:212-213` → `323` → `337-338`) but not saved by the probe. A replay of scene 1 from its own cache (0 live calls; day-4 blocks and night minds equal to the saved ones) rebuilt it and a day-4 min-00 prompt. Elena's prompt: line 12 `About water: … about 50 litres … about 45 litres … Since yesterday, Leo shares it out by the cup: five cups each a day.` and line 41 `- About Mara handing out water at the front door …: "… even though we have none left ourselves."`. Leo's: line 12 (the same, "you share") and line 39 (`"… while we have none left ourselves, …"`). |

## 1. Options, topics and `say_other`

### 1.1 The options

An option is `Option(id, label, speech=False, **act)` (`world.py:303-305`). The act keys used are `kind`, `target`,
`to` and `partner`. There is no topic, subject, event id or quotation field: **NOT FOUND**.

The options of a day decision, all from `World.options_for` (`world.py:539-615`). With someone else in the room:

| id | label (quoted) | line | speech |
|---|---|---|---|
| `silent` | "stay put and say nothing" | 543 | no |
| `ask_who` | "ask everyone here who took the can" | 546 | yes |
| `deny` | "deny taking it" | 550 | yes |
| `accuse_<q>` | "accuse {q} of taking it" | 555 | yes |
| `confess` | "admit taking it" | 557 | yes |
| `confront_<q>` | "confront {q} about something they did" | 562-563 | yes |
| `reassure_<q>` | "reassure {q}" | 567-568 | yes |
| `reassure_all` | "reassure everyone here" | 570 | yes |
| trip options | `propose_trip`, `volunteer`, `object_trip`, `back_<q>`, `object_<q>`, `decline` (day 4); `propose_trip`, `volunteer`/`still_going`, `send_<q>`, `nobody_goes`, `keep_<q>_home`, `refuse_to_go`, `propose_far`, `volunteer_far` (other days) | 635-701 | yes |
| `save_water` | "say nobody should use the stored water for washing or the toilet any more" | 573 | yes |
| `ration_water` | "say the water must be shared out by the cup from now on" | 576 | yes |
| `say_other` | "say something else" | 578 | yes |
| `sit_<q>` | "sit with {q}" / "keep sitting with {q}" | 583-584 | no |
| `aside_<q>` | "take {q} aside to the {room}" | 589 | no |

In any company: `keep_searching` / `search` (595-598), `go_<room>` (601), `collect_rain` (603), door options
(`door_look`, `door_call`, `door_open`, `door_give`, `door_refuse`, 618-633), `eat` (608), `share` (610).

Elsewhere: food moments (`eat`, `give_<q>`, `share`, `world.py:895-900`), a handed portion (`eat_given`,
`refuse_given`, 932-933), an aside (`accept_aside`, `refuse_aside`, 1591-1593), and the night's own options
(`night.py:502-736`).

**Which take a topic:** none by field. A speech option's words are the model's `say`. The system prompt says: "If the
option is marked (speech), `say` must hold the exact words they say, in their own voice, one or two short sentences"
(`world.py:43-46`). Two labels leave their subject open: `say_other` ("say something else") and `confront_<q>` ("about
something they did"). Neither carries what that subject is.

### 1.2 `say_other`

- **Prompt text.** The options are listed as `- {id}: {'(speech) ' if speech}{label}` (`world.py:1180`), so
  `- say_other: (speech) say something else`. That is the only form seen in the caches (`count_say_other.stdout.txt`:
  `its option line, as offered: ['- say_other: (speech) say something else']`).
- **When offered.** In every day decision with someone else in the room (`world.py:544`, `578`). It is held back, like
  any speech kind, after 3 turns in a row of it (`world.py:611-614`).
- **What the speaker may say.** Anything. The answer check requires only that a speech option has non-empty words
  (`world.py:1268-1272`). Any check on what the words are about: **NOT FOUND**
  (`grep -n 'len(say|SAY_MAX|…' world.py night.py quiet.py talk.py`: only `world.py:1268`, `1276`; `night.py:441-442`).
- **Its kind.** `act_of("say_other")` → `("say", None)` (`talk.py:32-33`). It is aimed at nobody: `aimed_at` returns
  None for `say` (`talk.py:52-55`).
- **What each listener keeps** (`world.py:1730-1747`):
  - A memory line through `perceive`, with the text from `line_text`'s last branch:
    `gist = f"{p.name} says to everyone"` then `return f"{gist}: \"{words}\""` (`world.py:1655-1656`). For example:
    `Daniel says to everyone: "<words>"`.
  - A `heard` entry: `{"seq", "who", "kind": "say", "target": None}` (`world.py:1746-1747`).
  - A trigger `(text, new)` (`world.py:1745`). Its later wording is "spoke to everyone" (`world.py:1100`), used in
    the "In that time:" pattern line (`world.py:1086`).
  - The speaker keeps `you said.` with no words (`world.py:1816`, the `.get(kind, "said")` default; `1841-1844`).
- **Next day and the night mind.** The chronicle event is kind `say` (`chronicle.py:210-212`). Its gist is "speaking
  to everyone" (`chronicle.py:33`). Each witness's view is the memory line they got, words included
  (`chronicle.py:71-85`). The night mind's records show that view to witnesses only (`mind.py:58-60`).
  - Block C has no key for `say`: no line comes of it (`memory.py:100-130`; the `WEIGHT` table, `memory.py:17-27`).
  - Block A's lines: knock summaries, accusations, confrontations and the after-morning line (see the day-4 blocks in
    §5). A `say` line in block A: **NOT FOUND** in the scene-1 blocks.
- **No flag is set by a `say_other` line**, unlike `ask`/`accuse` (`heard_question`, 1750-1751), `confess`
  (`knows_culprit`, 1752-1758), `deny`, and `accuse` aimed at the listener (1774-1784).

### 1.3 Count in the caches

Each cache entry is one answer received from the model (`gemini.Cache.put`, `gemini.py:236`). The probe caches start
as copies of earlier ones (`runs/probe_after/probe.py:8-11`), so answers are also counted once by cache key.

```
$ .venv/Scripts/python.exe runs/talk_facts/count_say_other.py > runs/talk_facts/count_say_other.stdout.txt      exit 0
cache/v16\gemini-3.5-flash-lite-daniel_ate_it-seed1.json: {'entries': 236, 'decisions': 224, 'say_other': 1}
cache/v16\gemini-3.5-flash-lite-daniel_ate_it-seed2.json: {'entries': 147, 'decisions': 139, 'say_other': 0}
cache/v16\gemini-3.5-flash-lite-daniel_ate_it-seed3.json: {'entries': 184, 'decisions': 176, 'say_other': 0}
== cache/v16 total (with copies): {'entries': 567, 'decisions': 539, 'say_other': 1}
cache/probe_door2\gemini-3.5-flash-lite-daniel_ate_it-seed2.json: {'entries': 171, 'decisions': 163, 'say_other': 0}
cache/probe_door2\scene1.json … scene8.json: {'entries': 174, 'decisions': 166, 'say_other': 0} each
== cache/probe_door2 total (with copies): {'entries': 1563, 'decisions': 1491, 'say_other': 0}
cache/probe_after\scene1.json: {'entries': 206, 'decisions': 194, 'say_other': 0}
cache/probe_after\scene3.json: {'entries': 205, 'decisions': 193, 'say_other': 0}
cache/probe_after\scene4.json: {'entries': 206, 'decisions': 194, 'say_other': 0}
== cache/probe_after total (with copies): {'entries': 617, 'decisions': 581, 'say_other': 0}
== distinct cache keys over all three: 709; with an option: 669; say_other: 1
  cache/v16\gemini-3.5-flash-lite-daniel_ate_it-seed1.json | Daniel | [] | say: 'I went out there and I survived, so I know we can find a way through this without arguing.'
== distinct decisions whose prompt offered say_other: 608 of 669
```

The one choice: v16 seed 1, Daniel, at `Now, minute 09, you are in the kitchen.`, with `"reason": "I need to show
them I am in control and keep us focused instead of fighting."` ("decisions" are entries whose answer has an
`option`. The rest are night-mind answers.)

## 2. How the options at an ask are decided

`World.decide` takes the options from `self.options_for(p)` (`world.py:1543`). The exceptions are a food moment
(`food_options`, `world.py:1541-1542`, `895-900`), an aside (`world.py:1591`), a handed portion (`world.py:932`) and
the night (`night.py`). Triggers, quiet asks (`pending["texts"]`, `world.py:1546-1547`) and meeting or evening lines
(`world.py:1149-1150`) go into the prompt's lines, not into the options.

What `options_for` reads (`world.py:539-615`), by kind:

| Read | Options | Now, or left by the past |
|---|---|---|
| `others_here(p)` | all speech, `sit_`, `aside_` (only with someone there) | now |
| `p.knows_culprit` | `ask_who` (541-546); `accuse_<q>` filtered (552-553) | past: own act, or a confession heard (`world.py:1752-1758`) |
| `p.heard_question`, `p.confessed` | `deny` (549-550), `confess` (556-557) | past: set by an `ask`/`accuse` heard or made (1750-1751, 1846). It is not reset by `next_day` (`night.py:1228-1229` resets memory, said_lines, history, heard, triggers, trip_heard, proposed, trip_raised) |
| `self.day != 4` | `confront_<q>` (560-563) | the day |
| `p.grudges[q].strength >= 3` | `reassure_<q>` left out (565-566) | past: grudges come from events |
| `self.trip`, `p.trip_heard`, `p.proposed`, `p.trip_raised`, `p.knows_empty` | trip options (635-701) | past: positions heard today (1831-1840); `knows_empty` from the nights (`night.py:157-165`, `1182`) |
| `p.water["level"]` | `save_water`, `ration_water` (572-577) | the house's water rule, set by those acts (`quiet.py:337`) |
| `p.activity`, `p.searched` | `keep_searching`, `search` (593-598) | past: rooms searched |
| `rain_action(p)` | `collect_rain` (602-604; 765-767) | now: rain, bin |
| `p.door` | door options (605-606, 618-633) | now: the visit under way (`quiet.py:628-681`) |
| `self.portions` | `eat`, `share` (607-610) | now |
| `p.history` | any speech kind used 3 turns in a row is left out (611-614) | past: own last turns |

**An option built from something past** (a sure line, a memory line or an earlier event as its content or label):
**NOT FOUND**. Past state above only gates options. No label holds an earlier event, and no option id or act names
one.

## 3. Learning of an event one did not perceive

**Who keeps an act.** By day, an act reaches `seen` (those in the room) through `perceive` (`world.py:1608-1612`).
`World.views[seq]` stores what each person got of each act (`world.py:1366-1378`). The chronicle's witnesses come
from it: "did", "saw", or "voices" from another room (`chronicle.py:205-207`). Block C keeps only events with `pid in
e["witnesses"]` (`memory.py:76-77`). The night mind does the same (`mind.py:58`).

**The door visit.** The summary line ("At 09:42 someone knocked at the front door: …") is written in `door_end` for
`witnesses = set(sc["at_door"]) | set(sc["heard_said"])` (`quiet.py:830-833`), each from what that person perceived
(`quiet.py:834-871`). It goes into their sure lines (871) and, next morning, into block A (`night.py:1066-1069`:
`if p.id in sc["summary"]`). Someone who only heard the knock gets "At … you heard knocking at the front of the house."
(`quiet.py:872-874`).

In scene 1 (`runs/talk_facts/door_witnesses.stdout.txt`), Daniel is not a witness of the knock, the visitor's lines or
the visit's end. He has "voices" for the refusal, the give and `save_water`. His view of each is `Voices from the
kitchen.`

```
  D3-027 knock None {'elena': 'heard', 'leo': 'heard', 'mara': 'heard'}
  D3-029 door_refuse elena {'elena': 'did', 'leo': 'saw', 'mara': 'saw', 'daniel': 'voices'}
     daniel's view: Voices from the kitchen.
  D3-030 door_give mara {'mara': 'did', 'elena': 'saw', 'leo': 'saw', 'daniel': 'voices'}
     daniel's view: Voices from the kitchen.
  D3-033 door_end None {'mara': 'saw', 'elena': 'saw', 'leo': 'saw'}
```

A path by which someone who missed a visit learns of it later: **NOT FOUND**. Daniel's prompts from 09:45 to his night
mind have no line on the visit apart from the fixed "The house:" line (`runs/talk_facts/daniel_lines.stdout.txt`).
His day-4 block A has no door line (§5). His night-3 records from 09:42 to 09:51 are `[D3-029] 09:42: Voices from the
kitchen.`, his own line at 09:45, Elena's reassurance of Leo at 09:48 ("…we will make sure the water lasts."), and
arrivals and sitting.

**Paths that do carry something a person did not perceive** (found in the code read):
- **Night trips.** "who went is the whole house's by the next morning" (`night.py:195-205`, `trips_known`). The
  outcome is "as the house saw it" (`night.py:208-216`, `seen_outcome`). It is used in the "About the street:" and
  "About going out at night:" lines (`night.py:227-261`).
- **A missing person.** The morning opening says who is not back, and how each one knows it: "with", "saw", "heard",
  or "gone" (`night.py:168-180`, `1254-1258`).
- **The shelf and water at dawn.** "So someone brought food/water into the house in the night" (`night.py:1241-1253`).
- **The water line.** It is built for every person in the house each tick: `for p in self.people(): … p.water =
  {"line": water.describe(...)}` (`quiet.py:327-338`; `people()` is everyone not away, `quiet.py:267-268`). It states
  the amount, the rule, since when and who holds it (`water.py:66-90`). Daniel's water line from his 09:45 ask on:
  `… about 50 litres … about 45 litres … Since 09:45, Leo shares it out by the cup: five cups each a day.` It does not
  name the give.
- **A confession heard.** It sets `knows_culprit` and a sure line, "{Name} admitted taking the can: "…" (you heard
  it)" (`world.py:1752-1758`). This is learning of the night's taking from words, by the act's kind, not by its
  content.

**If someone's words mention an event the listener did not perceive.** The listener keeps the words in a memory line,
the `heard` entry and a trigger (§1.2). For `say_other`, and for any speech kind but those above, nothing else about
the event is set. A mechanism that reads the words and records an event, a fact or a sure line from them: **NOT
FOUND**. Next day, the words reach the listener's night-mind records only as the view text of the speech event they
witnessed (`chronicle.py:71-85`; `mind.py:58-60`).

## 4. The stores in the night mind's prompt

`NightMind._prompt_for` (`mind.py:404-428`) builds the head from the sheet, then:
`head += [x for x in self.n.m.inside_lines(p) if not x.startswith(INSIDE_LEFT_OUT)]` (`mind.py:413`). `INSIDE_LEFT_OUT =
("About food:", "About the neighbour's house:", "About going there tonight:")` (`mind.py:33`). `inside_lines` adds
`p.water["line"]` when there is one (`world.py:1052-1053`). The "About water:" line is not left out. Then come the
earlier days, and the records (`mind.py:415-427`).

```
$ .venv/Scripts/python.exe runs/talk_facts/stores_lines.py > runs/talk_facts/stores_lines.stdout.txt
==== Q4: Leo's night-3 mind prompt (mind_input.leo.prompt)
prompt lines: 64
  head line 6: Your body: starving, for days now: you feel light and slow, and standing up fast greys your sight for a moment; and you have barely slept for nights; your eyes close on their own.
  head line 7: About the can: Daniel admitted taking it two days ago, at minute 33.
  head line 8: About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is further and more dangerous than next door.
  head line 9: About going out at night: Daniel went to the neighbour's house last night and came back with nothing.
  head line 10: About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since 09:45, you share it out by the cup: five cups each a day.
  lines starting 'About water:' / 'About food:': ['About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since 09:45, you share it out by the cup: five cups each a day.']
  every line naming water, litres, portions, the shelf, food or the store:
  18: [D3-001] min 00: Everyone gets up and comes into the kitchen. Last night the shelf held 0 portions; this morning it holds 0 portions. (you saw it)
  30: [D3-028] 09:42: A woman's voice at the front door said: "Sorry to bother you. Is there any water in the house you could spare? I've nothing left."
  32: [D3-030] 09:42: Mara says to everyone, while handing water out at the front door: "Mom, we have to give her some, we have enough stored." Mara hands some of the stored water out at the front door.
  33: [D3-031] 09:42: you said nobody should use the stored water for washing or the toilet any more, saying: "We cannot afford to hand out our drinking water when we have none left ourselves." You felt wary.
  35: [D3-033] 09:45: At 09:42 someone knocked at the front door: Elena told a woman, who asked for water, to go away, and Mara handed her about three litres of the stored water anyway.
  36: [D3-035] 09:45: you said the water must be shared out by the cup from now on, saying: "If we are giving water away, we need to ration what is left by the exact cup right now." You felt wary.
  38: [D3-037] 09:48: Elena reassures you: "We are listening to you, Leo, we will make sure the water lasts."
  (also matched: lines 3, 11, 13-16, 22-23, 45, 54-55: the sheet, the can, grudges, earlier days, sitting lines)
```

The water line is head line 10. It is the same in all four night-3 prompts but for "you share" / "Leo shares"
(Daniel's: `daniel_lines.stdout.txt`, `mind mind: water line`). Leo's own record D3-031 holds his words "we have none
left ourselves". There is no "About food:" line: it is left out by `INSIDE_LEFT_OUT`. The food on the shelf appears
only in record D3-001.

## 5. Day 4: block B's "none left" and the water line

**Saved by the probe.** `runs/probe_after/scene1.json`'s `day4_blocks` (in full in `stores_lines.stdout.txt`):

- Elena's B: `- About Mara handing out water at the front door and the person at the front door going away: "Mara gave
  some of our stored water to a stranger at the door because she has a good heart, even though we have none left
  ourselves."` Her intent: `"I will keep the children close and make sure our remaining water lasts through another
  day."`
- Leo's B: `- About Mara handing out water at the front door and the person at the front door going away: "Mara gave
  away our drinking water to a stranger while we have none left ourselves, so I had to make sure we rationed what
  remained by the exact cup."`
- Mara's B: `"I had to give that poor woman some water because we had it and she had nothing left."` Daniel's B: no
  water or door line.

The probe saved no day-4 prompt or water line. In `scene1.json`, "About water:" appears only under `asks` (35
distinct, all day 3 or night 3) and `mind_input` (4) (`stores_lines.stdout.txt`, its last section). The probe stores
`d4.blocks` only (`runs/probe_after/probe.py:251-252`). The water line **was built**: `next_day` calls
`quiet.setup(m, chronicle)` from day index 3 on (`night.py:1178-1179`). That runs `q.tick(0)` (`quiet.py:212-213`),
which calls `self.sense(minute)` (`quiet.py:323`), which sets `p.water["line"]` for everyone in the house
(`quiet.py:337-338`).

**Where the two sit in a day prompt.**
- The head holds `inside_lines`, the water line among them (`world.py:1125`, `1052-1053`).
- `m.carry[q] = r["C"] + r["A"] + r["B"]` (`night.py:1204`) goes into every day prompt after "What you remember from
  the days before:" (`world.py:1218-1219`).
- From the first speech act of the day, the intent line is removed from it (`world.py:1190-1193`).
- The carry and the water line are counted outside the trimming budget (`world.py:1207`, `1209-1212`), and only `morning`
  and `back` are trimmed (`world.py:1217-1235`).

**Rebuilt by replay.** Scene 1 was replayed from its own cache with the code at cb5b6bf, unpacked into the session
scratchpad (outside the repository). Its `.py` files are those of f4f2d2c, the HEAD the probe ran at. The client
raises on any ask, so every answer had to come from the cache. A day-4 min-00 prompt was then built (not sent) with
`d4.prompt_for(p, 0, d4.options_for(p))`.

```
$ git archive cb5b6bf Prototypes/llm-morning | tar -x -C <scratchpad>/at_cb5b6bf --exclude='Prototypes/llm-morning/v*'
$ git diff --stat cb5b6bf f4f2d2c -- Prototypes/llm-morning/*.py          (no output: the .py files are the same)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/talk_facts/replay_day4.py <scratchpad>/at_cb5b6bf/Prototypes/llm-morning > runs/talk_facts/replay_day4.stdout.txt      exit 0, stderr empty
replay reached: done; from_cache 155; live 0; api_requests 0
day-4 blocks equal to runs/probe_after/scene1.json's: True
night-3 mind answers equal to the saved ones: True

day 4: m.day 7; quiet set up; away []

== elena
  p.water['line'] at day 4 min 00: About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since yesterday, Leo shares it out by the cup: five cups each a day.
  prompt line 12/82: About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since yesterday, Leo shares it out by the cup: five cups each a day.
  prompt line 15/82: What you remember from the days before:
  prompt line 40/82: What yesterday left in you (your own thoughts, last night):
  prompt line 41/82: - About Mara handing out water at the front door and the person at the front door going away: "Mara gave some of our stored water to a stranger at the door because she has a good heart, even though we have none left ourselves."
  prompt line 55/82: Your options:

== leo
  p.water['line'] at day 4 min 00: About water: … Since yesterday, you share it out by the cup: five cups each a day.
  prompt line 12/78: About water: the bath holds about 50 litres and the pans, kettle, bottles and buckets in the kitchen about 45 litres: tap water stored before the taps ran dry. Since yesterday, you share it out by the cup: five cups each a day.
  prompt line 39/78: - About Mara handing out water at the front door and the person at the front door going away: "Mara gave away our drinking water to a stranger while we have none left ourselves, so I had to make sure we rationed what remained by the exact cup."

== mara
  prompt line 12/80: About water: … Since yesterday, Leo shares it out by the cup: five cups each a day.
  prompt line 41/80: - About handing out water at the front door and the person at the front door going away: "I had to give that poor woman some water because we had it and she had nothing left."

== daniel
  prompt line 12/79: About water: … Since yesterday, Leo shares it out by the cup: five cups each a day.
  (no B line about the water or the door)
```

So on day 4 of scene 1, block B's "none left" line (Elena, line 41; Leo, line 39) is in the same prompt as the water
line (line 12), which says about 50 and about 45 litres. This is the prompt of a decision at min 00, built and not
sent. Day 4 was not played, by the probe or here.

## 6. Commands and outputs

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` unset. Raw outputs in `runs/talk_facts/`:

| Script | Output | Exit |
|---|---|---|
| `count_say_other.py` (Q1) | `count_say_other.stdout.txt` | 0 |
| `stores_lines.py` (Q4, Q5 blocks) | `stores_lines.stdout.txt` | 0 |
| `daniel_lines.py` (Q3) | `daniel_lines.stdout.txt` | 0 |
| inline read of `day3_events` (Q3) | `door_witnesses.stdout.txt` | 0 |
| `replay_day4.py` (Q5) | `replay_day4.stdout.txt`, `replay_day4.stderr.txt` (empty) | 0 |

Two first runs failed and were fixed before the runs above:
- `stores_lines.py` failed on a regex with a bad escape (`re.error: unterminated character set at position 12`),
  after printing Q4 and the blocks. It was fixed and re-run, exit 0; the output file is the re-run's.
- `daniel_lines.py` first matched the fixed "The house:" line in every prompt. It was re-run with that line left out.

Code was read with `grep -n` and `sed -n` over `world.py`, `talk.py`, `quiet.py`, `night.py`, `mind.py`, `memory.py`,
`chronicle.py`, `water.py`, `gemini.py` and `runs/probe_after/probe.py`. The line numbers above are from those reads.
`git status` after the work: only `runs/talk_facts/`, `reports/talk_facts.md`, and the 3 untracked
`runs/v6/*.replay.md` that were already there.
