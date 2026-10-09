# door_after: all documents

Merged by `merge-slice-docs.py` from the 1 Markdown files in `Prototypes/llm-morning/runs/door_after/`, which remain the sources. Regenerate this file whenever they change.

## Contents

- [`report.md`](#reportmd)

---

## report.md

### After the door: what the house does and keeps once a visit ends

Mode: investigate, read-only. HEAD `d26d264`. Paths are relative to `Prototypes/llm-morning/`. No API call was made:
every command ran with `GEMINI_API_KEY` removed, and every answer after 09:42 is the fake model's (`gemini.FakeClient`).
Files written: this report and `runs/door_after/` only. `git diff` is empty (§6).

#### Summary

| # | Question | Answer, in short |
|---|---|---|
| 1 | Who is asked after a visit ends, with what trigger; does anything refer to the door or to who refused and who gave? | The Q7 stretch plays on while the kitchen talks, on what is left of its 18 asks (no longer door asks). Triggers in the first turn after are the door acts and the visitor's last line; after that, none. **No option** refers to the door once the visit has ended. Prompt lines do, in five kinds; **no line, trigger or option links the give to the refusal: NOT FOUND.** No quiet trigger (Q1, Q2, Q5, Q6) is tied to a door visit: NOT FOUND. |
| 2 | Trace of scene 1 to 12:00 | §2 and `runs/door_after/noon_scene1.stdout.txt`. 3 asks at 09:42 (the cached live answers), 15 asks from 09:45 to 09:54, then the stretch's cap; from 10:00 every quiet trigger is refused: "the day's 40 asks are spent". |
| 3 | Memory, night mind input, next day's block A | Day 3's memory holds each door act as each one perceived it; Mara's own record of her give reads "you said". The night mind gets the refusal and the give as separate records. Block A gets **one** door line, the give; **the refusal is not in block A: NOT FOUND**. Block C never holds a door refusal (no key), and on house day 8 holds no door line at all. |
| 4 | Relationship or tension state updated by the door acts | **None among the family: NOT FOUND.** Grudge, suspicion and feeling change only through the answer's own fields (`angry_at`, `suspects`, `feeling`), as for any act. The street holds one: the visiting household's `kind`, `surplus` and `refused` toward no. 9 (`street.py:503-526`). Scene 1: h13's `kind` 0.6 → 0.9, `surplus` 0.5 → 0.8, `refused` unset. |
| 5 | Turn order by minute | The seed string includes the turn `t` (`world.py:468-472`), so the draws differ by minute. At t = 54 to 58, Elena draws lowest of the three in all 5. The order of the other two differs (t 55: Leo before Mara; the others: Mara before Leo). Over all 280 turns of day 3, the lowest draw is Elena 97, Mara 93, Leo 90. |

#### 0. How the trace was made

- `runs/door_after/trace.py` imports `runs/probe_door2/probe.py` (not run) and uses its `VISITORS` and `visitor()`. It
  copies `cache/probe_door2/scene<k>.json` to a temp folder, plays v16 seed 2 to day 3 from the cache, puts the
  probe's visitor at the front door at 09:42, and plays on with `FakeClient` behind the cache. The temp folder is deleted
  after.
- `probe.day3` keeps its chronicle in a local variable. `trace.py` repeats the same calls in the same order, keeping
  the chronicle (`day3_keep`, `trace.py`, bottom). It asserts `oracle.live == 0` through night 2, as the probe does.
- **The 09:42 answers are the live ones.** In `noon_scene1.json` the three asks at 09:42 have `source: cache`. They
  are the answers recorded in `runs/probe_door2/scene1.json`: Elena `door_refuse`, Mara `door_give`, Leo `save_water`.
  Every answer from 09:45 on is the fake model's ("[fake line 3]" and so on). What the family decides after 09:42 is
  therefore not evidence. What the code does with it, and what it shows each person, is.
- Three traces: `noon 1` (scene 1, given over a refusal, to 12:00), `noon 2` (scene 2, refused, to 12:00), and
  `full 1` (scene 1 to bedtime, night 3, the night minds, day 4's blocks).

#### 1. After a visit ends: who is asked, with what trigger, and what refers to the door

##### 1.1 How a visit ends, in code

- A give ends the visit at the next turn: `door_after` queues the `given` line and `leave` (`quiet.py:754-755`). A
  refusal does the same with `refused_polite`/`refused_flat` (`quiet.py:756-760`). The give is checked first, so a give
  and a refusal in one turn end it as "given".
- At the next turn's `door_before`, the queued line is said (`door_speak`, `quiet.py:649-651`) and "leave" sets
  `going` (`quiet.py:675-679`). Then `door_views` runs, and `door_end` (`quiet.py:681-682`) writes each one's line and
  sets `self.door = None` (`quiet.py:826`).
- With `self.door` None, `door_views` sets everyone's `p.door = None` (`quiet.py:592-595`). So the door options are
  gone: they are offered only `if p.door is not None and p.door["options"] and p.room == "kitchen"` (`world.py:605-606`).
- `door_asks` asks nobody: `if self.door is None or self.door_full(): return` (`quiet.py:833-834`).

##### 1.2 Who is asked on the following turns

**In played time (the Q7 stretch goes on).**
- A stretch closes only when no room is talking, nobody is arriving, and no visit is on:
  `if not any(m.convos.active.values()) and not m.arrivals and q.door is None:` (`quiet.py:1439`).
- The Q7 stretch began with `q.begin(stretch, DOOR_ASKS, f"the door's {DOOR_ASKS} asks are spent", reserved=True)`
  (`quiet.py:1454`): a cap of the asks so far plus 18 (`quiet.py:421-427`).
- After the visit, its asks are ordinary asks under that cap. `spent(p)` exempts only a door ask:
  `door = p is not None and self.door is not None and p.door is not None …` (`quiet.py:412-414`).
- In each turn, everyone in a room is asked by `decide` if they have a trigger, an inner moment, a trip moment, a lull
  or a pending quiet ask, and the asks are not spent (`world.py:1568-1575`). Otherwise their routine is played
  (`world.py:1574-1575`, `routine`, `world.py:853-860`).
- When the cap is reached, `after_turn` ends every conversation (`quiet.py:1249-1253`) and the stretch closes.

**In quiet time.** The triggers are Q1, a need crossing a line (`quiet.py:1024-1050`); Q2, a grudge meeting
(`quiet.py:987-1022`); Q5, the evening at 19:00 (`quiet.py:1052`); Q6, rain (`quiet.py:365`); and Q7, a knock, at most
once a day (`q7_done`, `quiet.py:495`, `:505`). Q1 and Q2 are refused once the day's 40 asks are spent (`budget`,
`quiet.py:442-452`). **A quiet trigger tied to a door visit after it ends: NOT FOUND.** Q2 is chosen by grudge
strength (`quiet.py:993-996`), and no door act raises a grudge (§4).

**In the traces** (`noon_scene1.stdout.txt`, `noon_scene2.stdout.txt`; all from 09:45 on are fake answers):

| | Scene 1 (given over a refusal) | Scene 2 (refused) |
|---|---|---|
| Visit | 09:42 to 09:45 | 09:42 to 09:45 |
| Q7 stretch | 09:42 to 10:00, 18 asks: 3 door asks at 09:42, 15 at 09:45-09:54 | the same: 09:42 to 10:00, 18 asks |
| Asked after the visit | 09:45 Elena, Leo, Mara, Daniel; 09:48 Elena, Leo, Mara; 09:51 Elena, Mara, Leo, Daniel; 09:54 Elena, Daniel, Mara | 09:45 Elena, Leo, Mara, Daniel; 09:48 Leo, Daniel, Mara, Elena; 09:51 Daniel, Elena, Mara, Leo; 09:54 Daniel, Elena, Leo |
| 09:57 | all routine (the stretch's 18 spent: 24 + 18 = 42 asks) | the same |
| Quiet triggers to 12:00 | Q2 at 10:00, 11:42, 11:51: none fired ("the day's 40 asks are spent", or a line between them minutes before) | Q2 at 10:00, 11:42, 11:45: none fired, for the same reasons |
| Day's asks at 12:00 | 42 | 42 |

In the full trace (scene 1), the only other ask of day 3 is Q5 at 19:00 (Mara, trigger "it is evening, and in two
hours everyone goes to bed"), with its own 8 asks. Q2 at 14:36 to 14:51 and Q1 at 17:39, 19:00, 19:45 and 20:09 were
all refused: "the day's 40 asks are spent" (`full_scene1.stdout.txt`, quiet log).

##### 1.3 Triggers that refer to the door

- **Where they come from.** A perceived act is put in `p.triggers` with whether it is new (`perceive`,
  `world.py:1608-1612`). The visitor's line is put there too, in played turns only (`door_speak`, `quiet.py:704-706`).
  `social_triggers` keeps the new ones, and all of them while the room is talking (`world.py:1315-1323`). They are
  cleared when that person decides (`p.triggers = []`, `world.py:1545`).
- **So what each one perceived after acting at 09:42 is their trigger at 09:45.** Scene 1, 09:45 (`noon_scene1.json`):
  - Elena: `Mara says to everyone, while handing water out at the front door: "Mom, we have to give her some, we have
    enough stored."`; `Mara hands some of the stored water out at the front door`; `Leo says nobody should use the
    stored water for washing or the toilet any more: "We cannot afford to hand out our drinking water when we have none
    left ourselves."`; `A woman's voice at the front door says: "Oh, thank you. You don't know what this means."`
  - Leo: `Elena asks you to come aside to the back room` (a fake act), `A woman's voice at the front door says: "Oh,
    thank you. …"`
  - Mara: Leo's `save_water` line, the visitor's thanks, `Elena looks afraid`.
- **From 09:48 on, no trigger refers to the door** in either scene (the trigger lists in §2 and in
  `noon_scene2.stdout.txt`).
- Scene 2, 09:45: everyone's first trigger is the visitor's parting line, `A woman's voice at the front door says: "I
  understand. I'm sorry to have bothered you. Look after yourselves."`.

##### 1.4 Options that refer to the door event: NOT FOUND

Every option offered after 09:42 in scene 1 (`runs/door_after/search_links.stdout.txt`, the union over the prompts):
`accept_aside, accuse_daniel, aside_daniel, aside_leo, aside_mara, confront_daniel, confront_elena, confront_leo,
confront_mara, deny, go_back_room, go_bathroom, go_brothers_room, go_kitchen, keep_daniel_home, keep_elena_home,
nobody_goes, propose_far, propose_trip, ration_water, reassure_all, reassure_*, refuse_aside, refuse_to_go, say_other,
send_*, silent, sit_*, volunteer, volunteer_far`. No `door_*` option, and no option naming the visit, the refusal or
the give.

##### 1.5 Prompt lines that refer to the door event

Five kinds, each built by code:

| Line (scene 1, Elena, 09:45, quoted) | Built by | How long it stays (full trace) |
|---|---|---|
| `- 09:45: at 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water.` (under "What you are sure of today") | `door_end`, `quiet.py:814-815` (`p.sure`); shown at `world.py:1186` | all day 3, in every prompt of Elena, Leo and Mara; at night too |
| `- 09:42, you told the person at the door to go away.` (under "Your own last words today") | `world.py:1841` (`said_lines`); the last 3, `world.py:1187-1188` | Elena's prompts to 09:57; not at 19:00 |
| `- 09:42: you told the person at the door to go away. You felt anxious.` / `- 09:42: Mara hands some of the stored water out at the front door.` and the others (under "What else happened today") | each one's `p.memory`: §3.1 | trimmed oldest first to the token budget (`world.py:1216-1235`): Leo's last at 09:48, Mara's and Elena's at 09:51 |
| `What you have been doing: you have told the person at the door to go away, 1 turn in a row.` | `pattern`, `world.py:1068-1075` | Elena at 09:45 only |
| `About water: … Since 09:42, none of it goes on the toilet or on washing.` | Leo's `save_water` rule (`world.py:1713-1714`, `quiet.water_rule`) | all day |

`runs/door_after/door_lines_by_ask.stdout.txt` lists the door lines in every prompt of day 3 after the visit. From
09:54 on, and at 19:00 to 19:06 (Q5), the only door line in any prompt is the sure line of the give.

**A line, trigger or option that links the give to the refusal (that Mara gave after Elena refused, or against her):
NOT FOUND.** Searched over every post-visit prompt of both noon traces (`runs/door_after/search_links.py`) with
`overr|despite|against (?:Elena|Mara|your)|although|even though|after Elena|refus|defi|disobey` (§6). The hits are
`refuse_aside` acts and a night-2 memory ("despite my warning"), none about the door.

#### 2. The trace: scene 1 from the knock to 12:00

`runs/door_after/noon_scene1.stdout.txt` holds each decision with its triggers and the door lines of its prompt.
`noon_scene1.json` holds each full prompt and answer. Mode: `model` = asked; `routine` = not asked
(`world.py:1574-1575`). Source: `cache` = the live answer of probe_door2; `fake` = `FakeClient`.

| Time | Who | Room | Mode | Source | Quiet ask | Option | Triggers |
|---|---|---|---|---|---|---|---|
| 09:42 | Elena | kitchen | model | cache | Q7 | `door_refuse` "I am so sorry, but we have nothing to spare for you today." | someone is knocking at the front door; Mara accuses Daniel … (from min 15) |
| 09:42 | Mara | kitchen | model | cache | Q7 | `door_give` "Mom, we have to give her some, we have enough stored." | the knock; Elena tells the person at the front door to go away: "…" |
| 09:42 | Leo | kitchen | model | cache | Q7 | `save_water` "We cannot afford to hand out our drinking water when we have none left ourselves." | the knock; Mara accuses Daniel …; Elena's refusal; Mara's words; Mara hands some of the stored water out |
| 09:42 | Daniel | brothers room | routine | – | – | `silent` | – |
| 09:45 | Elena | kitchen | model | fake | – | `aside_leo` | Mara's words and give; Leo's save_water; the visitor's "Oh, thank you. …" |
| 09:45 | Leo | kitchen | model | fake | – | `refuse_aside` | Elena asks you to come aside …; the visitor's thanks |
| 09:45 | Mara | kitchen | model | fake | – | `say_other` | Leo's save_water; the visitor's thanks; Elena looks afraid |
| 09:45 | Daniel | brothers room | model | fake | – | `silent` | Voices from the kitchen |
| 09:48 | Elena, Leo, Mara | kitchen | model | fake | – | `confront_leo`, `send_elena`, `deny` | fake lines of 09:45 |
| 09:48 | Daniel | brothers room | routine | – | – | `silent` | – |
| 09:51 | Elena, Mara, Leo; Daniel | kitchen; brothers room | model | fake | – | `silent`, `send_elena`, `go_brothers_room`; `go_kitchen` | fake lines; Voices from the kitchen |
| 09:54 | Elena, Daniel, Mara | kitchen | model | fake | – | `confront_daniel`, `volunteer_far`, `propose_far` | fake lines; Daniel comes into the kitchen |
| 09:54 | Leo | brothers room | routine | – | – | `silent` | – |
| 09:57 | all four | – | routine | – | – | `reassure_all` (Elena, model, fake), then `silent` ×3 routine | the stretch's cap: 42 asks |
| 10:00 to 12:00 | nobody asked | | | | | sits from 10:00; rests from 11:42 and 11:51 | Q2 ×5 refused (§1.2) |

**Every prompt line that mentions the door, the visitor or the water given** (scene 1, from 09:45; the static house
line, which names "the front door … with a gap in the boards", and the option list are left out; the night-2 lines
about Daniel's trip that name the front door are in the stdout file):
- **09:45, Elena:** the sure line of the give; "Your own last words: 09:42, you told the person at the door to go away.";
  memory `09:42: Someone knocked at the front door.`, `09:42: A woman's voice at the front door says: "Sorry to bother
  you. …".`, `09:42: you told the person at the door to go away. You felt anxious.`, `09:42: Mara says to everyone,
  while handing water out at the front door: "Mom, we have to give her some, we have enough stored."`, `09:42: Mara
  hands some of the stored water out at the front door.`; `What you have been doing: you have told the person at the
  door to go away, 1 turn in a row.`; `About water: the bath holds about 50 litres … Since 09:42, none of it goes on the
  toilet or on washing.`
- **09:45, Leo:** the sure line; memory: the knock, the visitor's first line, `09:42: Elena tells the person at the
  front door to go away: "I am so sorry, but we have nothing to spare for you today."`, Mara's words, Mara's give.
- **09:45, Mara:** `- 09:45: at 09:42 someone knocked at the front door: you handed a woman, who asked for water, about
  three litres of the stored water.`; memory: the knock, the first line, Elena's refusal with its words, `09:42: you
  handed a woman of about forty-five at the door about three litres of the stored water. You felt anxious.`
- **09:45, Daniel:** none.
- **09:48:** Elena: the sure line, her last words, Mara's words and give, the thanks, `09:45: Footsteps go away along
  the street.`; Leo: the sure line, the footsteps; Mara: the sure line, her give, the thanks, the footsteps.
- **09:51:** Elena: the sure line, her last words, the thanks, the footsteps; Mara: the sure line, the thanks, the
  footsteps; Leo: the sure line.
- **09:54 and 09:57:** Elena: the sure line and her last words; Mara: the sure line; Daniel: none.

#### 3. What memory, the night mind and block A hold about scene 1

##### 3.1 Each person's memory on day 3 (`p.memory`)

Quoted from `noon_scene1.stdout.txt` (the same lines in `full_scene1`), 09:42 to 09:45:

| | Elena | Leo | Mara | Daniel |
|---|---|---|---|---|
| knock | `Someone knocked at the front door.` | the same | the same | – (did not hear it: `by_knock` has no Daniel) |
| first line | `A woman's voice at the front door says: "Sorry to bother you. Is there any water in the house you could spare? I've nothing left.".` | the same | the same | – |
| the refusal | `you told the person at the door to go away. You felt anxious.` | `Elena tells the person at the front door to go away: "I am so sorry, but we have nothing to spare for you today."` | the same as Leo | `Voices from the kitchen.` |
| the give | `Mara says to everyone, while handing water out at the front door: "Mom, …"` and `Mara hands some of the stored water out at the front door.` | the same | `you said. You felt anxious.` and `you handed a woman of about forty-five at the door about three litres of the stored water. You felt anxious.` | – |
| save_water | `Leo says nobody should use the stored water …: "…"` | `you said nobody should use the stored water for washing or the toilet any more. You felt wary.` | as Elena | – |
| 09:45 | `A woman's voice at the front door says: "Oh, thank you. You don't know what this means.".` and `Footsteps go away along the street.` | the same | the same | `Voices from the kitchen.` |

Built by:
- the knock: `quiet.py:577`;
- the visitor's lines: `quiet.py:703` (`p.memory.append((minute, heard + "."))`);
- the footsteps: `quiet.py:679`;
- one's own speech: `world.py:1838-1840`. "Their own lines reach them without the words: minute and verb only". The
  verb comes from `mine = {…}.get(kind, "said")` (`world.py:1798-1813`). `door_give` is not in that table, so Mara's own
  words at the door are kept as `you said.`;
- one's own door act: `world.py:1903`, `p.memory.append((minute, (door_line or f"you {KIND_DONE[kind]}.") + feel))`,
  with `door_line` from `door_act` (`quiet.py:735`);
- what others did: `perceive`, `world.py:1608-1612`, with `line_text` (`world.py:1650-1651`; `world.py:1894-1902` for a
  give).

Day 3's memory does not reach day 4: `next_day` sets `p.memory, p.said_lines, … = [], [], …` (`night.py:1228`) and
`p.sure = [f"min 00: …"]` (`night.py:1259`).

##### 3.2 The chronicle (day 3), from which the night mind reads

`chronicle.add_day` takes each act from the transcript (`chronicle.py:177-213`) and the door events from
`quiet.items()` (`quiet.py:1392-1393`). Quoted from `full_scene1.stdout.txt`:

| Id | Kind | Witnesses | Views (quoted) |
|---|---|---|---|
| D3-027 | knock | Elena, Leo, Mara: heard | `Someone knocked at the front door.` |
| D3-028 | door_line | Elena, Leo, Mara: heard | `A woman's voice at the front door said: "Sorry to bother you. …"` |
| D3-029 | door_refuse (Elena) | Elena did; Leo, Mara saw; Daniel voices | Elena: `you told the person at the door to go away, saying: "I am so sorry, but we have nothing to spare for you today." You felt anxious.` · Leo, Mara: `Elena tells the person at the front door to go away: "…"` · Daniel: `Voices from the kitchen.` |
| D3-030 | door_give (Mara) | Mara did; Elena, Leo saw; Daniel voices | Elena, Leo: `Mara says to everyone, while handing water out at the front door: "Mom, we have to give her some, we have enough stored." Mara hands some of the stored water out at the front door.` · **Mara: `you said, saying: "Mom, we have to give her some, we have enough stored." You felt anxious.`** · Daniel: `Voices from the kitchen.` |
| D3-031 | save_water (Leo) | Leo did; Elena, Mara saw; Daniel voices | `Leo says nobody should use the stored water …: "We cannot afford to hand out our drinking water when we have none left ourselves."` |
| D3-032 | door_line | Elena, Leo, Mara: heard | `A woman's voice at the front door said: "Oh, thank you. You don't know what this means."` |
| D3-033 | door_end | Elena, Leo, Mara: saw | the summary: `At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored water.` (Mara: `you handed`) |

Mara's view of D3-030 is built by `view_text` (`chronicle.py:68-83`): for the actor, `memory[0]` only, with the
words. Her first memory line of the act is `you said. You felt anxious.`, so her view of her give does not say that she
gave. The give is stated to her in D3-033.

##### 3.3 The night mind's input

`NightMind._prompt_for` (`mind.py:402-427`) puts, after the head and "What stays with you from earlier days", the
records of `records(chron, pid, 3)` (`mind.py:51-95`), bounded by `bound_records` (`mind.py:98-114`). Each record is
every day-3 and night-3 event the person witnessed, with their view. Quoted (`full_scene1.stdout.txt`, the door
records):
- **Elena:** `[D3-027] 09:42: Someone knocked at the front door.` · `[D3-028] 09:42: A woman's voice at the front door
  said: "Sorry to bother you. …"` · `[D3-029] 09:42: you told the person at the door to go away, saying: "I am so
  sorry, but we have nothing to spare for you today." You felt anxious.` · `[D3-030] 09:42: Mara says to everyone, while
  handing water out at the front door: "Mom, we have to give her some, we have enough stored." Mara hands some of the
  stored water out at the front door.` · `[D3-031] …` · `[D3-032] 09:45: … "Oh, thank you. …"` · `[D3-033] 09:45: At
  09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres of the stored
  water.`
- **Leo:** D3-027 to D3-033, with D3-029 as `Elena tells the person at the front door to go away: "…"` and D3-031 as his
  own.
- **Mara:** D3-027, D3-028, D3-029 (`Elena tells the person at the front door to go away: "…"`), **D3-030 as `09:42: you
  said, saying: "Mom, we have to give her some, we have enough stored." You felt anxious.`**, D3-031, D3-032, D3-033
  (`you handed …`).
- **Daniel:** `[D3-029] 09:42: Voices from the kitchen.` (`records` keeps voices once per room and minute,
  `mind.py:68-73`).

So the night mind gets the refusal and the give as two records in order. No record says one followed the other or went
against it: NOT FOUND. The night minds' answers in the trace are the fake model's (`Fake thought 35.`), so what a mind
would make of it is not evidence here.

##### 3.4 Day 4's block A (and B and C)

Block A is `carry_in_later` (`night.py:1006-1077`). The door's line is added by
`for sc in q.door_scenes: if p.id in sc["summary"]: out.append(sc["summary"][p.id])` (`night.py:1066-1069`). Quoted
(`full_scene1.stdout.txt`, day 4's blocks):
- **Elena:** `- At 09:42 someone knocked at the front door: Mara handed a woman, who asked for water, about three litres
  of the stored water.`
- **Leo:** the same.
- **Mara:** `- At 09:42 someone knocked at the front door: you handed a woman, who asked for water, about three litres
  of the stored water.`
- **Daniel:** no door line (no summary for him: he did not hear the knock, `quiet.py:792-794`).

**Elena's refusal in block A: NOT FOUND.** The summary of a given visit names only the giver (`quiet.py:802-805`,
`if sc["outcome"] == "given": g = sc["give"]["by"] …`). The refusal's line (`quiet.py:806-808`) is written only when
the outcome is "refused". Block A's other lines (accusations, confrontations, the trip positions, the afternoon, the
night) hold no door line.

**Block B** is the night mind's kept memories, each named by `gist` (`memory.py:39-44`). The gists of the door kinds:
`"door_give": "handing out water at the front door"`, `"door_refuse": "sending the person at the front door away"`
(`chronicle.py:58-62`). In the trace, Leo's fake memory cited D3-030 and his block B reads `- About Mara handing out
water at the front door: "Fake thought 35."`.

**Block C** reads only events of day index ≤ today − 2 (`memory.py:74-76`), so D3 first reaches it on house day 8. Its
person lines have a key for `door_give` and `door_open` (`memory.py:126-127`, weight 4 and 3, `memory.py:26`) and **none
for `door_refuse`: NOT FOUND**. One line per person is kept, the heaviest, and at equal weight the older
(`memory.py:138-140`). Computed on the chronicle through night 3 for house day 8 (`trace.py`, `block_c_day8`), no
person's block C holds a door line. Mara's line in everyone's block is `Four days ago, you ate a portion in front of the
others.` / `Four days ago, Mara ate a portion in front of you.`: an `eat` (weight 4, D1) is older than the `door_give`
(weight 4, D3).

#### 4. Relationship or tension state

**Among the family: NOT FOUND.** The family's states are each person's `grudges` (`Grudge`, `world.py:230-258`),
`suspicion` (`Track`, `world.py:196-227`), `guilt`, and `feeling`.
- A grudge rises by `add_grudge` (`world.py:990-994`). It is called for a confession after a denial or an accusation
  (`world.py:1765`, `:1771`, `:1781`) and for eating in front of a hungry person (`world.py:1998`, `:2055`). No door kind
  calls it: the door branch of `apply` (`world.py:1715-1717`, `:1894-1905`) only records and is perceived.
- A grudge also rises when an answer names someone in `angry_at` (`world.py:1517-1521`, fact `"you were angry with
  {name}"`). Suspicion moves with the answer's `suspects` (`world.py:1508-1516`), and feeling with the answer's
  `feeling` (`world.py:1686-1688`). Any act's answer carries these fields.

**What changed with scene 1's acts** (the cached live answers at 09:42; `noon_scene1.stdout.txt`, state):

| | Before the knock (09:42) | At the visit's end (09:45) | From |
|---|---|---|---|
| Elena | grudges none; suspicion Daniel 3; feeling exhausted | the same; feeling **anxious** | her answer: `suspects` Daniel, `angry_at` nobody |
| Leo | grudge Daniel 2; suspicion Daniel 3; exhausted | suspicion Daniel **2**; feeling **wary** | `suspects` nobody (`Track.report(None)` falls a step) |
| Mara | grudge Daniel 2; suspicion Daniel 3; resentful | grudge Daniel **3** (fact: "you were angry with Daniel"); feeling **anxious** | `angry_at` Daniel |
| Daniel | grudge Leo 2; guilt 3; anxious | unchanged | not asked |

No grudge between Elena and Mara, or Leo and Mara, rose at 09:42. The grudges that rose later in the trace (Elena
against Mara at 09:48; Leo against Elena at 09:45) come from fake answers' `angry_at`, and their facts read `you were
angry with Mara` / `you were angry with Elena`. The prompt shows such a grudge as `Against Mara (a little): two days
ago, Mara ate a portion in front of you at minute 54, while you were hungry; you were angry with Mara today at 09:48.`
(`world.py:1060`, `grudge_facts` `world.py:265-293`). It shows no door fact.

**In the street: one.** `street.end_visit` (`street.py:503-526`) updates the visiting household's beliefs about the
family's house (no. 9). On "given" it adds `kind_step` to `kind` and `surplus`. On anything else it counts `refused`,
and on "refused" it lowers `kind`. It always appends a deed. These are the household's, about the house, not about a
person.
- Scene 1 (given): h13's `kind` 0.6 → 0.9; `surplus` 0.5 → 0.8; `refused` unset; deed `{"kind": "given", "qty": 3.0,
  "good": "water"}`. Elena's refusal, in the same turn, is not recorded there: `end_visit` gets only the outcome.
- Scene 2 (refused): h29's `kind` 0.6 → 0.3; `refused` 1; deed `{"kind": "refused"}`.

#### 5. The turn order by minute

`world.py:468-472`:
```
    def order_string(self, t, room):
        """The seed string of a room's turn order (reports/days_design.md, §4.4): days 1 and 2 share one."""
        if self.day <= 5:
            return f"{self.seed}:{t}:{room}"
        return f"{self.seed}:day{day_index(self.day)}:{t}:{room}"
```
- Used at `world.py:1395-1396`: `rng = random.Random(self.order_string(t, room))`, then one draw per person.
- `next_to_act` takes the minimum of `(0 if addressed or leading an aside else 1, -(seq addressed), -strength(feeling) ×
  shown, draw)` (`world.py:1331-1332`). So a person spoken to, or showing a stronger feeling, goes before the draw.
  Among equals, the lowest draw goes first ("drawn by the seed among equals").
- The string includes `t`, so the draws differ by minute. Day 3 is house day 6, so the string is
  `2:day3:<t>:kitchen`.

The kitchen's three at 5 consecutive turns (`runs/door_after/order_draws.stdout.txt`):

| t | Clock | Draws (Daniel, Elena, Leo, Mara) | The three by draw |
|---|---|---|---|
| 54 | 09:42 | 0.5710, **0.1592**, 0.5654, 0.2049 | Elena, Mara, Leo |
| 55 | 09:45 | 0.0229, **0.2135**, 0.4360, 0.7768 | Elena, Leo, Mara |
| 56 | 09:48 | 0.8356, **0.2788**, 0.9977, 0.3045 | Elena, Mara, Leo |
| 57 | 09:51 | 0.0711, **0.3200**, 0.4912, 0.3678 | Elena, Mara, Leo |
| 58 | 09:54 | 0.8223, **0.2258**, 0.5965, 0.5373 | Elena, Mara, Leo |

- The draws differ at every minute. Elena's is the lowest of the three at all five, and the order of the other two
  differs at t 55.
- Over all 280 turns of day 3 (t = 0 to 279), the lowest draw of the three is Elena 97, Mara 93, Leo 90. The six orders
  occur 59, 51, 48, 42, 42 and 38 times (`order_draws.stdout.txt`).
- The acting order observed in the traces (`kitchen_order.stdout.txt`): scene 1, 09:42 Elena, Mara, Leo ("drawn by the
  seed among equals"); 09:45 Elena (drawn), Leo ("asked aside by Elena"), Mara. Scene 2, 09:45 Elena, Leo (both
  drawn), Mara ("just spoken to by Leo"); 09:48 Leo first ("shows the strongest feeling here (afraid)").

#### 6. Commands and output

All from `Prototypes/llm-morning/`, with `GEMINI_API_KEY` removed.

```
$ git log --oneline -1
d26d264 LLM morning: the second door probe as it ran (…)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/door_after/trace.py noon 1 > runs/door_after/noon_scene1.stdout.txt     exit 0, stderr empty
=== noon, scene 1 (no child, helper, urgency under 0.8); stopped at 12:00; asks {'day': 42, 'from_cache': 123, 'fake': 15}
visit: 09:42 to 09:45; outcome given; acts [[162, 'elena', 'door_refuse', 'I am so sorry, but we have nothing to spare for you today.'], [162, 'mara', 'door_give', 'Mom, we have to give her some, we have enough stored.']]
said: [('09:42', "Sorry to bother you. Is there any water in the house you could spare? I've nothing left."), ('09:45', "Oh, thank you. You don't know what this means.")]
…  (every decision, the quiet log, stretches, spans, memory, sure lines, state, order draws: 349 lines)
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/door_after/trace.py noon 2 > runs/door_after/noon_scene2.stdout.txt     exit 0, stderr empty
=== noon, scene 2 (no child, helper, urgency over 0.8); stopped at 12:00; asks {'day': 42, 'from_cache': 123, 'fake': 15}
visit: 09:42 to 09:45; outcome refused; acts [[162, 'elena', 'door_refuse', 'We have nothing to spare, please go away.']]
$ env -u GEMINI_API_KEY .venv/Scripts/python.exe runs/door_after/trace.py full 1 > runs/door_after/full_scene1.stdout.txt     exit 0, stderr empty
=== full, scene 1 (no child, helper, urgency under 0.8); stopped at None; asks {'day': 50, 'from_cache': 123, 'fake': 23}
…  (day 3's door events in the chronicle, night 3's prompts, the night minds' input, day 4's blocks, block C on day 8)
$ .venv/Scripts/python.exe runs/door_after/door_lines_by_ask.py > runs/door_after/door_lines_by_ask.stdout.txt     exit 0
$ .venv/Scripts/python.exe runs/door_after/order_draws.py > runs/door_after/order_draws.stdout.txt     exit 0
day_index(6) = 3
t 54 (09:42) '2:day3:54:kitchen': draws daniel 0.5710, elena 0.1592, leo 0.5654, mara 0.2049; the kitchen's three by draw: elena, mara, leo
t 55 (09:45) '2:day3:55:kitchen': draws daniel 0.0229, elena 0.2135, leo 0.4360, mara 0.7768; the kitchen's three by draw: elena, leo, mara
t 56 (09:48) '2:day3:56:kitchen': draws daniel 0.8356, elena 0.2788, leo 0.9977, mara 0.3045; the kitchen's three by draw: elena, mara, leo
t 57 (09:51) '2:day3:57:kitchen': draws daniel 0.0711, elena 0.3200, leo 0.4912, mara 0.3678; the kitchen's three by draw: elena, mara, leo
t 58 (09:54) '2:day3:58:kitchen': draws daniel 0.8223, elena 0.2258, leo 0.5965, mara 0.5373; the kitchen's three by draw: elena, mara, leo
all 280 turns of day 3 (t = 0 to 279): lowest draw of the three: elena 97, leo 90, mara 93
the six orders of the three: elena > mara > leo 59; mara > elena > leo 51; leo > elena > mara 48; leo > mara > elena 42; mara > leo > elena 42; elena > leo > mara 38
$ .venv/Scripts/python.exe runs/door_after/kitchen_order.py > runs/door_after/kitchen_order.stdout.txt     exit 0
scene 1:
  09:42: 1. elena (drawn by the seed among equals); 2. mara (drawn by the seed among equals); 3. leo (the only one left to act here)
  09:45: 1. elena (drawn by the seed among equals); 2. leo (asked aside by Elena); 3. mara (the only one left to act here)
  …
scene 2:
  09:42: 1. elena (drawn by the seed among equals); 2. mara (drawn by the seed among equals); 3. leo (the only one left to act here)
  09:45: 1. elena (drawn by the seed among equals); 2. leo (drawn by the seed among equals); 3. mara (just spoken to by Leo)
  09:48: 1. leo (shows the strongest feeling here (afraid)); 2. daniel (just spoken to by Leo); 3. mara (asked aside by Daniel); 4. elena (the only one left to act here)
  …
```

**The search for a line linking the give to the refusal** (over `noon_scene1.json` and `noon_scene2.json`, every
prompt after 09:42, the part before "Your options:"). Pattern
`overr|despite|against (?:Elena|Mara|your)|although|even though|after Elena|refus|defi|disobey`:
```
$ .venv/Scripts/python.exe runs/door_after/search_links.py > runs/door_after/search_links.stdout.txt     exit 0, 23 lines
1 165 leo ['- About Daniel getting up in the night and telling Daniel, low, not to go: "Daniel left in the dark alone despite my warning …"']
1 165 mara ['2. Leo refuses to go with Elena.']
1 168 elena ['- 09:45: Leo refuses to go aside with you.']
1 168 leo ['Against Elena (a little): yesterday, Elena ate a portion Daniel gave her, …; you were angry with Elena today at 09:45.', '- About Daniel … despite my warning …', '- 09:45: you refused to go aside with Elena. You felt calm.', 'What you have been doing: you have refused to go aside, 1 turn in a row.']
… (scene 1 to 09:57 and scene 2 to 09:54: only refuse_aside acts, "Against …" grudge lines and the night-2 memory)
1 options offered after 09:42: ['accept_aside', 'accuse_daniel', 'aside_daniel', 'aside_leo', 'aside_mara', 'confront_daniel', 'confront_elena', 'confront_leo', 'confront_mara', 'deny', 'go_back_room', 'go_bathroom', 'go_brothers_room', 'go_kitchen', 'keep_daniel_home', 'keep_elena_home', 'nobody_goes', 'propose_far', 'propose_trip', 'ration_water', 'reassure_all', 'reassure_daniel', 'reassure_elena', 'reassure_leo', 'reassure_mara', 'refuse_aside', 'refuse_to_go', 'say_other', 'send_daniel', 'send_elena', 'send_leo', 'send_mara', 'silent', 'sit_daniel', 'sit_elena', 'sit_leo', 'sit_mara', 'volunteer', 'volunteer_far']
```

**At the end:**
```
$ git diff --stat           (empty)
$ git status --short        ?? runs/door_after/   ?? reports/door_after_facts.md   ?? runs/v6/daniel_ate_it-seed{1,2,3}.replay.md
```

Raw outputs in `runs/door_after/`: `trace.py`, `door_lines_by_ask.py`, `order_draws.py`, `search_links.py`,
`kitchen_order.py`; `noon_scene1.json`,
`noon_scene2.json`, `full_scene1.json` (every prompt and answer, the states, the chronicle's door events, the night
minds' input, the blocks); the `.stdout.txt` and `.stderr.txt` of each command.

