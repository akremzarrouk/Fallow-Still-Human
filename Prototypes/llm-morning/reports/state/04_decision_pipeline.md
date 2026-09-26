# 04 Decision pipeline: from world state to applied action

Prototypes/llm-morning, current version only (v1/ to v4/ ignored). Audited 2026-09-26. Read-only:
nothing was run, no API was called, and nothing was edited except this file. All paths are
relative to `Prototypes/llm-morning/`.

**Sources read in full:** `world.py`, `data.py`, `gemini.py`, `morning.py`. Also read, because
`world.py` depends on them for this pipeline: `talk.py` (imported at world.py:22 for option kinds
and newness), `config.json` (request settings), and the part of `story.py` that consumes the
response fields (story.py:56-84).

**Out of scope (another audit):** knowledge and belief storage, meaning `memory`, `sure`,
`said_lines`, `backstory` and `heard`, and how they are filled and trimmed. They are named below
only where a prompt section reads them or where a response field is written into them.

---

## 0. The pipeline at a glance

| step | what happens | path:line |
|---|---|---|
| 1 | `morning.py` builds the `Oracle` and the `Morning`, then calls `morning.turn(t)` for t = 0..29 (90 min / 3 min per turn). | morning.py:52-66, data.py:76-77, world.py:246 |
| 2 | Each turn: rooms are visited in `data.ROOMS` order. Within a room, `next_to_act` picks who goes next. | world.py:668-674, world.py:614-634 |
| 3 | `decide(p, t)`: build options, collect social triggers, clear them, check for an inner moment. | world.py:773-788 |
| 4 | With a trigger or an inner moment, `ask_model`. Otherwise `routine` (no model). | world.py:788-793 |
| 5 | `ask_model`: snapshot levels, build prompt, `oracle.ask(SYSTEM, prompt)`, mark levels as seen, parse. | world.py:733-743 |
| 6 | Oracle: cache lookup, else `GeminiClient.generate` → `generate_content` with the JSON schema. | gemini.py:230-251, gemini.py:93-115 |
| 7 | `parse`: usable → dict; unusable → reason string. | world.py:543-579 |
| 8 | Usable: update suspicion and grudges from `suspects` / `angry_at`. Unusable: fallback option. | world.py:744-771, world.py:790-791 |
| 9 | `act` → `apply(p, opt, d, ...)`: the chosen option changes the world. | world.py:651-666, world.py:845-1100 |
| 10 | If the option was `aside_*`, the target is asked at once through `decide_aside`. | world.py:680-692, world.py:799-815 |
| 11 | End of turn: moves, voices through walls, arrivals, conversation bookkeeping, hunger rises. | world.py:696-731 |

---

## 1. Scenarios

Defined at data.py:102-117. `DEFAULT_SCENARIO = "daniel_ate_it"` (data.py:118). The CLI accepts
exactly `sorted(data.SCENARIOS)` (morning.py:136). **There are three scenarios. No others exist**
(see NOT FOUND).

| scenario | `culprit` | `night` event (day 3, placed at the `NIGHT` slot, data.py:148) | path |
|---|---|---|---|
| `daniel_ate_it` | `"daniel"` | "In the night Daniel eats a can standing at the counter in the dark. Nobody sees." `{"daniel": "did"}` | data.py:103-107 |
| `mara_ate_it` | `"mara"` | "In the night Mara eats a can sitting on the kitchen floor. Nobody sees." `{"mara": "did"}` | data.py:108-112 |
| `miscount` | `None` | `None` (the event is dropped from the backstory, data.py:160) | data.py:113-116 |

Everything else in the house data is the same across scenarios: people, rooms, `PORTIONS = 2`,
`OPENING`, and the other 12 backstory events (data.py:131-154). What differs flows only from
`culprit` and `night`:

| effect | what the scenario changes | path:line |
|---|---|---|
| Backstory | The night event is included only for a scenario that has one, and only the culprit remembers it: the who-map is `{culprit: "did"}`, and a person is given an event only if they are in its map. | data.py:157-160, world.py:201-202 |
| `knows_culprit` | Set to the culprit's own id for the culprit, `None` for everyone else. | world.py:212 |
| `guilt` | 1 for the culprit, `None` for everyone else. In `miscount` nobody has guilt. | world.py:222 |
| Sure line | The culprit gets "You know where the can went: you ate it yourself in the night, and nobody saw." | world.py:265-266 |
| `ask_who` option | Not offered to anyone with `knows_culprit`, so never offered to the culprit. | world.py:321 |
| `confess` option | Offered only to `self.culprit` (not yet confessed). In `miscount` nobody is offered it. | world.py:332 |
| Grudge for a false accusation | Raised when the accused is not the culprit. In `miscount` (`self.culprit is None`), every accusation counts as false. | world.py:924 |
| Guilt events | Only when a culprit exists (`culprit is not None`). | world.py:852, 871, 932 |
| Conscience line in prompt | Only for a person whose `guilt` is not `None`. | world.py:442-445 |

Same in every scenario: the opening sure line gives Elena "(you did it)" and everyone else
"(you saw it)" (world.py:263-264). Every person gets the opening trigger (world.py:267). The
kitchen conversation starts at minute 0 (world.py:269).

---

## 2. Person state

`Person.__init__` is at world.py:191-225. Static sheet data comes from data.py:16-55.

### 2.1 Levels (what `levels()` returns, world.py:230-235)

These integers are compared to decide on an inner moment (§3.2). The prompt shows them only as
words or events, never as numbers (world.py:424-446).

| level | range | source value | what changes it | path:line |
|---|---|---|---|---|
| `hunger` | 0-3 | `hunger_level(p.hunger)`: <0.5→0, <0.7→1, <0.85→2, else 3 | see `p.hunger` in §2.2 | world.py:87-88 |
| `suspicion` | 0-3 | `p.suspicion.strength` (`Track`) | **only** the `suspects` field of a usable model answer, through `Track.report` | world.py:109-140, 751 |
| `grudges` | per target, 0-3 | `Grudge.strength` | rises: rule events (§2.3) and `angry_at`. Falls: `may_fall` on a usable answer whose `angry_at` is not that person | world.py:143-165, 418-421, 760-765 |
| `guilt` | 1-3, culprit only (key absent otherwise) | `p.guilt` | `add_guilt`, +1, capped at 3. Never falls. | world.py:222, 409-416 |

`Track.report(who, minute)` (world.py:117-134):
- Naming the current target, or anyone while the strength is 0: +1 (`"rose"`), or `"same"` at 3.
- Naming nobody or someone else while the strength is >0: −1 (`"fell"`), but only if at least
  `FALL_EVERY` = 15 min have passed since the last fall; otherwise `"held"`.
- Falling to 0 while naming someone else makes that person the new target at strength 1.
- Naming yourself counts as naming nobody (world.py:748).

`Grudge.rise` (world.py:151-158) is +1 up to 3. Every rise is recorded in `events`, including
rises at 3. `may_fall` (world.py:160-165) is −1 when at least 15 min have passed since the last
rise or fall.

### 2.2 Every other field

| field | range / type | initial | changed at (path:line) |
|---|---|---|---|
| `id`, `name`, `sheet` | static | data.py | never. `sheet` holds `age`, `role`, `note`, `traits` (0-1 floats), `values`, `hunger`, `hunger_rate` (data.py:17-54) |
| `hunger` | float, clamped to [0.0, 1.0] | 0.55 / 0.60 / 0.45 / 0.50 (data.py:25, 34, 43, 53) | +0.004·3·`hunger_rate` per turn for everyone, at the end of every turn (world.py:727-728). −0.4 on `eat` (1065). −0.4·(portions ÷ eaters) on `share` (1089) |
| `room` | key of `data.ROOMS` | `"kitchen"` (198) | set at the end of the turn from `moves` (696-697) |
| `activity` | dict: `kind` ∈ {idle, searching, walking, sitting}, `label`, optional `with`, `until` | idle / "standing at the pantry" (199) | 698, 867, 957, 959, 971, 977, 985, 995, 1027, 1045, 1059, 1081 |
| `feeling` | free string (the model's `feeling`, lowercased) or `None` | `None` (200) | only when `d["mode"] == "model"` (854-855) |
| `feeling_until` | turn index, −1 = not shown | −1 (200) | `t + 3` if `outward(feeling)`, else −1 (856) |
| `triggers` | list of (text, is-new) | `[]`, then the opening trigger (267) | appended at 267, 710, 822 (through `perceive`: 718, 899, 968, 1039, 1051). Cleared at 777 and 806 |
| `history` | list of {t, kind, seq} | `[]` | one entry per act (860) |
| `addressed` | {seq, who, accused} or `None` | `None` | reset on acting (861). Set when a line is aimed at them (902-903) and when their aside is refused (1040) |
| `aside_lead` | person id or `None` | `None` | reset on acting (862). Set on the asker when the other accepts (1031) |
| `searched` | set of rooms | `set()` | a search is finished (994) |
| `knows_culprit` | person id or `None` | 212 | a confession is heard (907) |
| `heard_question` | bool | False | hearing an ask or accuse (904-905), or making one (947-948) |
| `confessed` | bool | False | `confess` (949-950) |
| `eaten` | float | 0.0 | 1066, 1090 |
| `suspicion` | `Track` | target `None`, strength 0 | 751 |
| `suspected_at` | list of minutes | `[]` | reset when the suspect changes (752-753). Appended when the answer names the current suspect (754-755) |
| `grudges` | person → `Grudge` | `{}` | 420, 760, 764 |
| `denials_heard` | person → minute | `{}` | 920-921 |
| `accused_by` | person → minute | `{}` | 922-923 |
| `guilt`, `guilt_events` | see §2.1 | 222-223 | 413-415 |
| `seen` | a `levels()` snapshot | 268 | 740: set to the snapshot taken at 737, *before* the answer is parsed or applied |
| `last_inner` | minute or `None` | `None` | 784 |
| `backstory`, `memory`, `sure`, `said_lines`, `heard` | — | — | knowledge storage, out of scope |

**Needs:** hunger is the only need. **Mood:** the only mood state is the `feeling` string plus
`feeling_until`. `strength(feeling)` (world.py:75-80) turns the string into 0-4 by stem-matching
`SHOWN` (world.py:44-49), adding +1 for "deeply/very/extremely/utterly/so". Anything else is 0 and
"stays inside".

### 2.3 Rule events that raise grudges and guilt

| event | effect | path:line |
|---|---|---|
| A listener hears a confession from someone who earlier denied it to them | grudge(listener → confessor) +1 | world.py:911-915 |
| A listener hears a confession from someone who earlier accused them | grudge(listener → confessor) +1 | world.py:916-919 |
| The target of an accusation is not the culprit | grudge(target → accuser) +1 | world.py:922-928 |
| Someone eats a portion in front of a listener whose hunger level is ≥1 | grudge(listener → eater) +1 | world.py:1068-1075 |
| The culprit accuses someone | guilt +1 | world.py:871-874 |
| The culprit hears someone else accuse a non-culprit | guilt +1 | world.py:932-937 |
| Someone reassures the culprit personally (`reassure_<culprit>`) | guilt +1 | world.py:938-940 |
| The model's own answer names someone in `angry_at` | grudge(self → them) +1, kind `"angry"` | world.py:757-762 |

---

## 3. Who is asked: social triggers, inner moments, routine

`decide` (world.py:773-797):

```
opts = options_for(p)                       # 775
triggers = social_triggers(p, t)            # 776
p.triggers = []                             # 777  cleared whether or not the model answers
if not triggers: check for an inner moment  # 781-787
if triggers or inner: ask_model             # 788-791
else: routine                               # 792-793
```

### 3.1 Social trigger: exact condition (world.py:604-612)

```
talking = self.convos.active[p.room] and (people present in the room) >= 2   # 283-286
found = unique texts in p.triggers where (is_new or talking)                  # 607
if talking: + "<Q> looks <feeling>" for each other Q here with shown(Q, t)    # 608-611
```

`shown(q, t)` = `outward(q.feeling) and q.feeling_until >= t` (world.py:288-289).

Where trigger entries come from, and their is-new flag:

| source | text | is-new | path:line |
|---|---|---|---|
| Opening, everyone | "the count came up short in front of everyone" | True | world.py:267 |
| Hearing a spoken line in the same room | the heard line (`line_text`) | `Newness.line(...)` result | world.py:886, 896-899 |
| Voices through a wall (not into or out of the bathroom) | "Voices from the <room>" | added **only if** the line was new | world.py:702-710 |
| Arrival at turn end, for each person already in the destination | "<P> comes into the <room>", or for the aside partner "You and <P> are in the <room>, away from the others" | True | world.py:711-718 |
| A new fact seen in the room (a finished search, eating, sharing) | the fact text | True | world.py:962-968 (called at 998, 1076, 1096) |
| Aside refused (to the asker only) | "<Q> refuses to go aside with you" | False | world.py:1037-1039 |
| Sat with (to the target only) | "<P> came to sit with you" | False | world.py:1048-1051 |

`Newness.line` (talk.py:45-66) decides is-new for a spoken line:
- confess: always new.
- ask: new only the first time that speaker asks.
- accuse: new only the first time that speaker accuses that target.
- deny: new only if there is an accusation against the speaker that they have not yet denied.
- reassure, say, and any non-speech kind spoken while acting: never new.

**The conversation** is started or kept going by `started` (world.py:271-273 →
talk.py:81-89). Its callers: the opening (269), a new line (888-889), a new fact (965), an
arrival the next turn (640-641). It ends after `QUIET_TURNS` = 2 full turns with nothing new, or
when fewer than 2 people are left (talk.py:91-105, world.py:52, 722).

### 3.2 Inner moment: exact condition (world.py:781-787, 385-392)

All of these must hold:
1. `social_triggers` returned nothing (781).
2. `risen(p)` is non-empty. That is, compared with `p.seen`, at least one of `hunger`, `guilt`,
   `suspicion`, or `grudges[t]` for some t, is now **strictly higher** as an integer level
   (389-391).
3. `p.last_inner is None` or `minute - p.last_inner >= INNER_EVERY` (9) (783, 53).

When it fires: `last_inner = minute`, and `d` gets `inner_kinds`, `inner_families` and `inner`
(the `rise_words` strings, world.py:394-407). This path exists in `decide` only. `decide_aside`
has no inner-moment path.

Timing: `seen` is snapshotted at world.py:737, before the answer, and stored at 740, before
parsing. Suspicion and grudge changes caused by that same answer (751, 760) happen after the
snapshot, so they appear as risen at the next decision. An unusable answer still updates
`seen` (740 runs before the return at 742-743).

### 3.3 Routine (no model) (world.py:375-382)

`keep_searching` if searching and offered; else `sit_<with>` if sitting and offered; else
`silent`.

### 3.4 Order within a room (world.py:614-634)

The sort key is: addressed-or-aside-lead first → most recent `addressed.seq` → strongest shown
feeling → seeded draw (`random.Random(f"{seed}:{t}:{room}")`, world.py:670-671). The result
decides what is already in "Said and done ... before you" for each person.

---

## 4. Options

Built by `options_for(p)` (world.py:315-373), except the two aside replies, which are built in
`decide_aside` (world.py:801-803). "others" = the people still present in the room
(`others_here`, world.py:276-281). **(speech)** means `Option.speech=True`: the prompt marks it
and `say` is required.

### 4.1 Every option type, when offered

| id | label | speech | offered when | path:line |
|---|---|---|---|---|
| `silent` | stay put and say nothing | no | always | world.py:319 |
| `ask_who` | ask everyone here who took the can | yes | others present and `not p.knows_culprit` | world.py:321-322 |
| `deny` | deny taking it | yes | others present, `p.heard_question`, `not p.confessed` | world.py:325-326 |
| `accuse_<q>` | accuse Q of taking it | yes | per other Q. Skipped if `p.confessed`, or if p knows someone else is the culprit and Q is not that person | world.py:327-331 |
| `confess` | admit taking it | yes | others present, `p.id == self.culprit`, `not p.confessed` | world.py:332-333 |
| `reassure_<q>` | reassure Q | yes | per other Q, unless `p.grudges[q].strength >= 3` | world.py:334-338 |
| `reassure_all` | reassure everyone here | yes | more than one other present | world.py:339-340 |
| `say_other` | say something else | yes | others present | world.py:341 |
| `sit_<q>` | sit with Q / keep sitting with Q | no | per other Q whose activity is not searching or walking | world.py:342-347 |
| `aside_<q>` | take Q aside to the <room> | no | per other Q, if `empty_room(p)` finds a free room and Q has not acted this turn | world.py:350-354, 291-301 |
| `keep_searching` | carry on searching the <room> | no | activity is searching and not "settled" | world.py:356-358 |
| `search` | search the <room> for the can (takes about six minutes) | no | not searching, room not in `p.searched`, not settled | world.py:359-361 |
| `go_<room>` | go to the <room> | no | every room except the current one (bathroom included) | world.py:362-364 |
| `eat` | eat one of the portions | no | in the kitchen and `portions > 0` | world.py:365-366 |
| `share` | share out what is left among everyone here | no | as `eat`, and others present | world.py:367-368 |
| `accept_aside` | go with P to the <room> | no | only in `decide_aside` | world.py:801-802 |
| `refuse_aside` | refuse to go with P | no | only in `decide_aside` | world.py:803 |

"settled" = `p.confessed or (p.knows_culprit and p.knows_culprit != p.id)` (world.py:356).

**Repetition filter:** if the person's last acts are the same `SPEECH` kind 3 or more turns in a
row, every option of that kind is removed (world.py:369-372). `SPEECH` = ask, deny, accuse,
confess, reassure, say (talk.py:8). `act_of` groups `reassure_<q>` and `reassure_all` together as
"reassure" (talk.py:11-26). The removed kind is recorded as `d["held_back"]` (world.py:780).

**Empty room for an aside** (world.py:291-301): a room other than the current one with nobody in
it and nobody moving there this turn. The preference order is the person's own room, then the
other private room, then the kitchen, then the bathroom.

### 4.2 What applying each option does (`apply`, world.py:845-1100)

Common to every option (world.py:846-867): `seq` +1. If the mode is `model`, `feeling` and
`feeling_until` are set. A `history` entry is appended. `addressed` and `aside_lead` are reset. A
non-sit, non-speech act stands a sitting person up.

**Any option with words (`say` non-empty)** (world.py:876-960):
- `Newness.line` is called, and a new line starts or keeps the conversation (886-889).
- The line goes into `self.said` and `so_far`.
- Each person present `perceive`s their own version of the line (memory + trigger with the
  is-new flag) and gets a `heard` entry.
- The target of an aimed line (accuse, reassure, aside: `aimed_at`, talk.py:29-32) gets
  `addressed`.
- ask and accuse set `heard_question` for the listeners.
- The speaker's own memory and `said_lines` get the line, with " You felt X." (853, 945-946).
- A voice is queued for the other rooms (941).
- A non-speech option with words is spoken "while <doing>" (878-883, 890-891) and then goes on
  to its own effect. A speech option returns at 955-960.

| kind | effect in the world | path:line |
|---|---|---|
| ask | the speech path above only | 876-960 |
| deny | + each listener's `denials_heard[p] = minute` | 920-921 |
| accuse | + target's `accused_by`. Grudge if the target is not the culprit. Guilt effects (§2.3) | 871-874, 922-937 |
| confess | + listeners' `knows_culprit = p`, a sure line, grudges for an earlier denial or accusation. Speaker `confessed = True`, own sure line | 906-919, 949-952 |
| reassure / reassure_all | + guilt if the target is the culprit | 938-940 |
| say | the speech path only | 876-960 |
| silent | activity idle "staying put". A `so_far` line. A memory line only in model mode. `say` was already dropped by `parse` | 976-982, 576-577 |
| search | activity searching, `until = t+1`. `so_far`. Others perceive "starts going through" (no trigger) | 983-990 |
| keep_searching | `so_far`. When `until <= t`: room added to `searched`, a sure line, `fact()` (new trigger for the others, starts the conversation). A search chosen at turn t finishes when `keep_searching` is applied at turn t+1 | 991-1001 |
| go | `so_far`. Others perceive "leaves for" (no trigger). `leave()`: activity walking, removed from `present`, queued in `moves` | 1002-1009, 970-974 |
| aside | `so_far` line "asks Q to come aside". The others (not the target) perceive it. After `apply` returns, `turn` removes Q from `remaining` and calls `decide_aside(Q, ...)` | 1010-1018, 680-692 |
| accept_aside | both walk, both are removed from `present`, both are queued in `moves` with each other as partner. The asker gets `aside_lead` | 1019-1034 |
| refuse_aside | `so_far`. The asker gets a non-new trigger and `addressed` | 1035-1042 |
| sit | activity sitting with the target. If new: `so_far`, the target gets a non-new trigger, the others perceive it | 1043-1057 |
| eat | portions −1, hunger −0.4. Every onlooker gets a sure line, and a grudge if their hunger level is ≥1. `fact()` | 1058-1079 |
| share | all portions split between the actor and everyone present, hunger −0.4·each. `portions = 0`. `fact()` | 1080-1099 |

The empty-shelf branches at 1060-1063 and 1082-1084 are reached only if `portions <= 0` when the
option is applied. Options are built just before the decision (775), after earlier acts in the
turn.

**End of turn** (world.py:696-731): moves are applied (room changes, activity "just come in").
Voices: a memory line for everyone who did not hear the line directly, except across the
bathroom, plus a trigger if the line was new. Arrivals: a trigger for the people already there,
and `arrivals` starts the room's conversation next turn. `convos.end_turn`. Hunger rises.

---

## 5. What the model sees

### 5.1 The request (gemini.py:93-115)

| item | value | path:line |
|---|---|---|
| model | `gemini-3.5-flash-lite`; `--model gemma` → `gemma-4-31b-it` | config.json:2, 12; morning.py:37-38 |
| `system_instruction` | `SYSTEM` (below) | gemini.py:96, world.py:27-39, 739 |
| `contents` | the prompt, as one string | gemini.py:111-112 |
| `temperature` | 1.0 | config.json:3, gemini.py:97 |
| `seed` | the run's `--seed` | gemini.py:72, 98; morning.py:51 |
| `response_mime_type` | `application/json` | gemini.py:99 |
| `response_schema` | `RESPONSE_SCHEMA` | gemini.py:47-58, 100 |
| `max_output_tokens` | 2048 | config.json:9, gemini.py:101 |
| automatic function calling | disabled | gemini.py:102 |
| returned to world.py | `response.text or ""` | gemini.py:115 |

A cached answer is returned instead of a request when the key sha256(model, seed, system,
prompt) matches (gemini.py:196-198, 230-238).

### 5.2 The system instruction, in full (world.py:27-39)

```
You decide what one person in a family does in the next three minutes. You get who they are, what they remember, what they see now, and the options open to them. They know only what is in their memory. Choose exactly one option id from the list. If the option is marked (speech), `say` must hold the exact words they say, in their own voice, one or two short sentences. For any other option `say` is a short line they say while doing it, or null. `feeling` names what they feel right now in one or two words. `reason` is their reason in one sentence, as they would think it. `suspects` is who they now believe took the can, and `angry_at` is who they are angry with right now: each is one of "Daniel", "Elena", "Leo", "Mara" or "nobody". Reply with JSON only: {"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", "suspects": "<name or nobody>", "angry_at": "<name or nobody>"}
```

It is the same for every call, every person and every scenario.

### 5.3 The prompt's sections, in order (`prompt_for`, world.py:483-540)

The final assembly is at world.py:522-527: `head` + backstory + `pinned` + morning + `now` +
`tail`, joined with `\n`.

| # | section (literal header or first line) | content | built at |
|---|---|---|---|
| 1 | `You are <Name>, <age>, <role> of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).` | the family list is a literal string | world.py:489-490 |
| 2 | `How you address them: ...` | `data.ADDRESS[p]` | world.py:486, 491; data.py:93-98 |
| 3 | `Who you are: <note>` | sheet `note` | world.py:492 |
| 4 | `Temperament: ...` | `trait_words`: ≥0.75 "very X", ≥0.55 "X", ≥0.4 "somewhat X", else "not X" | world.py:493, 95-106 |
| 5 | `What matters to you: ...` | sheet `values` | world.py:494 |
| 6 | `Your body: <hunger words>.` + optional `Since you last decided, you have grown hungrier.` | `HUNGER_WORDS[level]`; the second line if hunger is in `risen(p)` | world.py:426-428, 66 |
| 7 | `About the can (<a little/some/a lot>): you thought <X> took it, at minute(s) ...` or `About the can: you have not settled on who took it.` | suspicion target and strength word, last 4 `suspected_at` | world.py:429-435, 67-68 |
| 8 | `Against <X> (<level word>): <facts>.` per grudge >0, or `Against the others: nothing.` | `grudge_facts`: last 4 event facts + one "you were angry with X at minute(s) ..." line | world.py:436-441, 173-183 |
| 9 | `On your conscience (<level word>): you ate the can in the night, and nobody saw; <last 4 guilt facts>.` | culprit only | world.py:442-445 |
| 10 | `The house: <HOUSE> <HOUSE_THINGS>` | the rooms, and the only things that exist | world.py:495; data.py:79-90 |
| 11 | `What you remember from the days before:` + `- Day N: ... (you did/saw/heard it)` | `p.backstory` (storage out of scope) | world.py:515, 522 |
| 12 | `What you are sure of this morning:` + bullets | `p.sure`, never trimmed | world.py:517, 523 |
| 13 | `Your own last words this morning:` + last 3 | `p.said_lines[-3:]`, if any | world.py:518-519 |
| 14 | `What else happened this morning, most recent last:` + `- (earlier things, left out here)` if trimmed + `- min MM: ...`, or `- nothing else yet` | `p.memory` minus the current minute | world.py:516, 523-525 |
| 15 | `Now, minute MM, you are in the <room>.` | — | world.py:497 |
| 16 | `- Nobody else is here.` or `- <Q> is here, <activity label>.[ <Q> looks <feeling>.]` | the "looks" part only if `shown(q, t)` | world.py:498-503 |
| 17 | `- N portion(s) on the shelf.` | kitchen only | world.py:504-505 |
| 18 | `Said and done in the <room> this turn, before you, in order:` + numbered lines, or `You are the first to act in the <room> this turn.` (only if others are present) | `self.so_far[room]` | world.py:506-511 |
| 19 | `What you have been doing: you have <KIND_DONE>, N turn(s) in a row.` / `In that time: ...` or `In that time nobody has said anything to you or to everyone.` / `Answered you differently from one time to the next: ...` or `Nobody answered you differently ...` | `pattern(p)`: the run of the same act kind, and the lines aimed at them or at everyone since that run began | world.py:512, 449-481, 56-64 |
| 20 | `Your options:` + `- <id>: [(speech) ]<label>` | `opts` in `options_for` order | world.py:513 |

**Trimming** (world.py:520-538): while `estimate_tokens(SYSTEM + text)` (len/3.6 + 1,
world.py:71-72) is over `PROMPT_TOKEN_BUDGET` = 1400 (world.py:51), drop the oldest item in this
order: morning memory while more than 8 are left, then backstory while more than 4 are left,
then morning memory, then backstory. `sure`, `said_lines`, `now` and the options are never
trimmed.

**Not in the prompt:**
- The trigger list itself: `prompt_for` takes `(p, t, opts)` and reads neither `p.triggers` nor
  `d`. Triggers reach the model only as the memory and `so_far` lines written by
  `perceive` / `apply`.
- The `rise_words` of an inner moment. Only the hunger sentence at world.py:427-428 reflects a
  rise.
- For the person asked aside: the text "`<P> asks you to come aside to the <room>`" (world.py:804)
  is used only as a trigger in `d`. The target sees the request through `so_far` (world.py:1012)
  and the two option labels. The target is excluded from `perceive` at world.py:1013-1015.

### 5.4 Two real prompts from the cache

Both come from `cache/v5/`, written by runs with the default `--out v5` (morning.py:35). Cache
files are dated 2026-09-25 14:26 and 15:10; `world.py` and `data.py` were last modified at
14:16 and 14:15. I did not regenerate prompts from the current code, so byte-identity with what
the code would produce today was not checked.

**(a)** `gemini-3.5-flash-lite-mara_ate_it-seed1.json`, first entry: Daniel, minute 00,
prompt_tokens 1277. Every section above appears except 6's second line, 9 (Daniel is not the
culprit here), 13 and 19. Sections 7, 8 and 18 use their "nothing yet" forms. Section 11 has no
day-3 night line. 22 options are offered.

**(b)** `gemini-3.5-flash-lite-miscount-seed2.json`, line 43, in full (prompt_tokens 1336):

```
You are Mara, 17, the youngest, the daughter of the family (Elena, 42, the mother; Daniel, 25; Leo, 21; Mara, 17).
How you address them: Elena "Mom"; Daniel "Daniel"; Leo "Leo".
Who you are: Younger sister. Frightened and easy to read, but old enough to resent being handled like a child. Everything she feels reaches her face before she decides to show it.
Temperament: somewhat cautious, not dominant, very empathetic, impulsive, proud, very anxious, honest.
What matters to you: closeness, deciding for yourself, fairness.
Your body: hungry.
About the can: you have not settled on who took it.
Against Daniel (a little): you were angry with Daniel at minute 03.
The house: The family has shut itself in the house. The water has stopped. Food is short. Rooms: kitchen (the food is kept here); brothers room (Daniel and Leo's room); back room (Elena and Mara's room); bathroom (nothing is heard in or out of it). The only places and things there are: the kitchen, with the pantry shelf where the food is kept, the counter and the dry taps; the brothers room, with Daniel's and Leo's beds; the back room, with Elena's and Mara's beds and Mara's bag; the bathroom; the doors between the rooms; the front door and the front windows, boarded up. Outside, and not to be gone to: the street and the neighbour's house. Do not mention any other object or place.
What you remember from the days before:
- Day 3: Mara freezes in the doorway with something moving in the street. Daniel picks her up and carries her inside. (you saw it)
- Day 4: Leo says maybe they should let someone else handle this one. (you saw it)
- Day 4: Daniel empties Mara's bag onto the bed while she is standing there. (you saw it)
- Day 4: Elena says she is quite sure nobody in this house would take food from the others. (you saw it)
What you are sure of this morning:
- min 00: Elena counts the pantry with everyone standing there. A can that should be on the shelf is not. 2 portions are left. (you saw it)
Your own last words this morning:
- min 00, you denied taking it: "I didn't take it, I swear I didn't!"
- min 03, you denied taking it: "I already told you, I didn't take anything!"
What else happened this morning, most recent last:
- (earlier things, left out here)
- min 03: Elena reassures everyone: "Let's all calm down, we are going to get through this together without turning on each other."
- min 03: Leo reassures everyone: "Let's listen to Mom and stop accusing each other before we tear ourselves apart."
- min 03: Daniel asks everyone who took the can: "We are not letting this drop until someone owns up to it."
Now, minute 06, you are in the kitchen.
- Daniel is here, staying put.
- Elena is here, talking.
- Leo is here, talking.
- 2 portions on the shelf.
Said and done in the kitchen this turn, before you, in order:
1. Daniel stays put and says nothing.
What you have been doing: you have denied taking it, 2 turns in a row.
In that time: Daniel asked who took the can, then asked who took the can; Leo denied taking it, then reassured everyone; Elena reassured everyone.
Answered you differently from one time to the next: Leo.
Your options:
- silent: stay put and say nothing
- ask_who: (speech) ask everyone here who took the can
- deny: (speech) deny taking it
- accuse_daniel: (speech) accuse Daniel of taking it
- accuse_elena: (speech) accuse Elena of taking it
- accuse_leo: (speech) accuse Leo of taking it
- reassure_daniel: (speech) reassure Daniel
- reassure_elena: (speech) reassure Elena
- reassure_leo: (speech) reassure Leo
- reassure_all: (speech) reassure everyone here
- say_other: (speech) say something else
- sit_daniel: sit with Daniel
- sit_elena: sit with Elena
- sit_leo: sit with Leo
- aside_elena: take Elena aside to the back room
- aside_leo: take Leo aside to the back room
- search: search the kitchen for the can (takes about six minutes)
- go_brothers_room: go to the brothers room
- go_back_room: go to the back room
- go_bathroom: go to the bathroom
- eat: eat one of the portions
- share: share out what is left among everyone here
```

Stored response:

```
{"option": "accuse_daniel",
 "say": "Daniel, you searched my bag like I was a thief, so maybe you're the one who actually took it!",
 "feeling": "resentful", "reason": "I am sick of Daniel treating me like a criminal when he acts so suspicious himself.",
 "suspects": "Daniel", "angry_at": "Daniel"}
```

In (b), `aside_daniel` is absent because Daniel had already acted this turn (world.py:352).
Backstory is cut to 4 items and morning memory to 3 by the trimming loop (world.py:531-534).

---

## 6. What the model returns

### 6.1 Schema (gemini.py:47-58)

`object` with six **required** properties:

- `option`: string, with **no enum**
- `say`: string, nullable
- `feeling`: string
- `reason`: string
- `suspects`: string, enum `["Daniel","Elena","Leo","Mara","nobody"]`
- `angry_at`: string, same enum

`FakeClient` returns the same six keys (gemini.py:162-169).

### 6.2 Every field and what the code does with it

| field | checked in `parse` (world.py) | normalised | what the code does with it |
|---|---|---|---|
| `option` | a non-empty string (554-556), then must match an offered `Option.id` after `.strip()` (566-569) | stripped | Chooses the `Option` (794 / 812). `apply` runs its effect (§4.2). Recorded in `d`, the transcript entry `option` (658) and the story (story.py:82). |
| `say` | the key must exist and be `null` or a string (557-558). Required non-empty for a speech option (573-574) | whitespace collapsed, surrounding quotes stripped, `""`/`"null"`/`"none"` → `None` (570-572). Dropped for `silent`, which sets `dropped_line` (576-577) | The words of the spoken line (§4.2): heard, remembered, triggers, voices, `said`, `said_lines`. Transcript `words` (659). Story (story.py:76). |
| `feeling` | a non-empty string (554-556) | whitespace collapsed, lowercased (578) | In model mode: `p.feeling`, and `feeling_until = t+3` if `outward` (855-856). Then: "<Q> looks <feeling>." in others' prompts (502). "<Q> looks <feeling>" as a social trigger while talking (611). The ordering key within a room (620, 631-633). " You felt X." in the speaker's memory lines (853). Story (story.py:83, 327). Not in the transcript entry. |
| `reason` | a non-empty string (554-556) | whitespace collapsed (579) | Stored in `d["reason"]` and printed in the story only (story.py:84). Not used by any rule, not shown in any prompt, not in the transcript entry. |
| `suspects` | case-insensitive exact match to `CHOICES` (559-565, 24-25) | the canonical name | `named()` maps it to an id, with self → nobody (746-749). `Track.report` (751). `suspected_at` (752-755). `d["suspects_result"]`, `d["suspects_now"]`. Transcript (662). Story (story.py:80). Feeds prompt section 7 and inner moments. |
| `angry_at` | same (559-565) | the canonical name | Self → nobody (757). If a person: `grudge.rise(kind="angry")` (760). Every other grudge may fall (763-765). `d["grudge_note"]` (770). Transcript (663). Story (story.py:81). Feeds prompt section 8 and inner moments. |
| any other key | not read | — | ignored |

`parse` also adds `dropped_line` (bool) to the choice (579). `apply` reads it only for the
`silent` outcome text (world.py:981-982).

---

## 7. Parsing and fallback

### 7.1 What counts as unusable (world.py:543-574), checked in this order

1. After `.strip()` and removal of a leading ```` ```json ```` / trailing ```` ``` ```` fence
   (546-547), the text does not parse as JSON → `"not JSON"`. An empty response (`response.text`
   is `None` → `""`, gemini.py:115) lands here.
2. The top level is not an object → `"not a JSON object"`.
3. `option`, `feeling` or `reason` is missing, not a string, or blank → ``"no `<field>`"``.
4. The `say` key is missing, or is neither `null` nor a string → ``"no `say`"``.
5. `suspects` or `angry_at` is not one of Daniel/Elena/Leo/Mara/nobody (case-insensitive,
   exact) → ``"`<field>` is not one of the family or nobody"``.
6. `option` (stripped) is not an offered id → ``"option `<x>` was not offered"``.
7. A speech option comes with no words after normalisation → ``"`<id>` is speech but no words were given"``.

Repaired rather than rejected: `say` on `silent` is dropped (576-577).

### 7.2 What happens then

| path | fallback option | what else | path:line |
|---|---|---|---|
| `decide` | `routine(p, opts)` (keep searching / keep sitting / silent) | `mode="fallback"`, `invalid=<why>`, `say=None` | world.py:790-791 |
| `decide_aside` | `refuse_aside` | same fields | world.py:810-811 |

- There is no re-ask or retry for an unusable answer.
- The unusable text is still written to the cache (gemini.py:250).
- In fallback mode, `feeling` is not updated (world.py:854), suspicion and grudges are not
  touched (ask_model returns at 742-743), `p.seen` has already been updated (740), triggers are
  already cleared (777 / 806), and `last_inner` has already been set (784) if this was an inner
  moment.
- The story prints `**FALLBACK** ... (<invalid>)` (story.py:72-75).
- `meta.fallbacks` counts them (morning.py:93).

API errors are not a fallback. `StopMorning` subclasses (quota, rate limit, call cap, cache miss)
propagate out of `turn` and end the run with exit code 3 (gemini.py:106-126, 239-244;
morning.py:71-78).

### 7.3 Observed in the saved current-version runs (runs/v5/*.meta.json)

| run | model_decisions | fallbacks | routine | lines_spoken | inner_moments | private_talks |
|---|---|---|---|---|---|---|
| daniel_ate_it-gemma-seed1..5 | 21, 13, 20, 19, 14 | 0 ×5 | 99, 107, 100, 101, 106 | 13, 9, 12, 10, 8 | 8, 7, 7, 7, 7 | 0 ×5 |
| mara_ate_it-seed1..3 | 46, 37, 37 | 0 ×3 | 74, 83, 83 | 36, 26, 25 | 5, 8, 11 | 0 ×3 |
| miscount-seed1..3 | 56, 93, 70 | 0 ×3 | 64, 27, 50 | 41, 81, 52 | 8, 9, 11 | 0 ×3 |

No v5 run of `daniel_ate_it` with the default Flash Lite model is on disk. The one "FALLBACK"
hit per story file is the legend line (story.py:198), not a fallback.

---

## 8. Search commands used, and their output

Run from `Prototypes/llm-morning/` unless noted. Output is verbatim; long outputs are shortened
where marked.

```
$ ls -la Prototypes/llm-morning ; wc -l Prototypes/llm-morning/*.py      (from repo root)
  data.py 167, gemini.py 251, morning.py 146, story.py 331, talk.py 105, world.py 1100 lines
  (plus metrics*.py, probe_*.py, list_models.py, test_morning.py; v1/..v4/ directories)
```

```
$ grep -n '"reason"\|\["reason"\]' world.py story.py morning.py gemini.py
world.py:37:    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
world.py:554:        for field in ("option", "feeling", "reason"):
world.py:579:                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None
gemini.py:53:        "reason": {"type": "string"},
gemini.py:57:    "required": ["option", "say", "feeling", "reason", "suspects", "angry_at"],
gemini.py:166:            "reason": f"Fake reason {self.requests}.",
gemini.py:177:                del answer["reason"]

$ grep -n "reason" story.py
65:    order = f" ({ORDINAL[d['place']]} to act in the {data.ROOMS[d['room']]}: {d['order_reason']})"
84:            f"Reason: {quoted(d['reason'])}{inside} Came of it: {d['came_of_it']}{fact}")
155:      "quotes. The feeling and the one-sentence reason are the model's, as it wrote them.")
198:    w("- **FALLBACK**: the model's answer could not be used (the reason is given); the rules chose "
```

```
$ grep -n "feeling" story.py morning.py
story.py:83:            f"{newness(d)} (one of {d['offered']} options). Feeling: *{d['feeling']}*. "
story.py:131:      "those options for them, says the words, and names a feeling. Every other turn is settled "
story.py:147:      "accused goes first (the most recent first), then whoever shows the strongest feeling, "
story.py:155:      "quotes. The feeling and the one-sentence reason are the model's, as it wrote them.")
story.py:200:    w(f"- A feeling that shows on a face (scared, angry, hurt, crying...) is seen by the others in "
story.py:327:        last.append(f"{name} *{mine[-1]['feeling']}* (minute {mine[-1]['minute']:02d})" if mine
story.py:329:    w("- The last feeling each of them named: " + "; ".join(last) + ".")

$ grep -n "\.feeling\b\|feeling_until" world.py
200:        self.feeling, self.feeling_until = None, -1
289:        return outward(q.feeling) and q.feeling_until >= t
502:            look = f" {q.name} looks {q.feeling}." if self.shown(q, t) else ""
611:                    found.append(f"{q.name} looks {q.feeling}")
620:            return (0 if first else 1, -(a["seq"] if a else 0), -strength(q.feeling) * self.shown(q, t), draw[pid])
631:        mine = strength(q.feeling) * self.shown(q, t)
632:        if mine > max(strength(o.feeling) * self.shown(o, t) for o in rest):
633:            return pid, f"shows the strongest feeling here ({q.feeling})"
855:            p.feeling = d["feeling"]
856:            p.feeling_until = t + FEELING_SHOWS_FOR_TURNS if outward(d["feeling"]) else -1
```

```
$ grep -n "suspects\|angry_at\|grudge_note\|suspects_now\|suspects_result" story.py morning.py
story.py:80:    inside = (f" Suspects: {d['suspects']}, so {d['suspects_now']}{kept(d['suspects_result'])}. "
story.py:81:              f"Angry at: {d['angry_at']}; {d['grudge_note']}.")
story.py:177:      "out). Naming someone in `angry_at` raises it a step too. A grudge falls a step only when "
story.py:296:    w("| Suspicion | " + " | ".join(f"{morning.people[p].suspicion.short('suspects')}" for p in data.ORDER) + " |")

$ grep -n "dropped_line\|invalid\|fallback" world.py story.py morning.py
world.py:579:                "reason": " ".join(ans["reason"].split()), "dropped_line": dropped, **named}, None
world.py:791:                d.update(mode="fallback", invalid=why, option=self.routine(p, opts), say=None)
world.py:811:            d.update(mode="fallback", invalid=why, option="refuse_aside", say=None)
world.py:982:                                               if d.get("dropped_line") else "") + "."
story.py:72:    if d["mode"] == "fallback":
story.py:74:                f"answer could not be used ({d['invalid']}), so the rules chose: **{d['label']}**. "
story.py:113:    n_fall = sum(d["mode"] == "fallback" for d in all_d)
morning.py:93:        "fallbacks": sum(d["mode"] == "fallback" for d in all_d),
morning.py:105:    for k in ("api_requests", "answers_live", "answers_from_cache", "model_decisions", "fallbacks",

$ grep -n '"say"\|get("say")' world.py story.py morning.py
world.py:37:    '{"option": "<id>", "say": "<words>" or null, "feeling": "<word>", "reason": "<sentence>", '
world.py:59:    "reassure": "reassured someone", "say": "said something else",
world.py:341:            opts.append(Option("say_other", "say something else", True, kind="say"))
world.py:480:                "reassure": f"reassured {target or 'everyone'}", "say": "spoke to everyone"
world.py:557:        if "say" not in ans or not (ans["say"] is None or isinstance(ans["say"], str)):
world.py:570:        say = " ".join((ans["say"] or "").split()).strip().strip('"').strip() or None
world.py:578:        return {"option": opt.id, "say": say, "feeling": " ".join(ans["feeling"].split()).lower(),
world.py:659:                     "words": d.get("say"), "audience": audience, "mode": d["mode"],
world.py:876:        words = d.get("say")
world.py:884:            spoken_kind = kind if kind in SPEECH else "say"
story.py:76:    said = f", saying {quoted(d['say'])}" if d.get("say") else ""
```

```
$ grep -n "triggers" world.py
206:        self.triggers = []          # (text, is it new) social things since they last acted
267:            p.triggers.append(("the count came up short in front of everyone", True))
604:    def social_triggers(self, p, t):
607:        found = list(dict.fromkeys(text for text, new in p.triggers if new or talking))
710:                    q.triggers.append((line, True))
776:        triggers = self.social_triggers(p, t)
777:        p.triggers = []
779:        d = {"person": p.id, "triggers": triggers, "offered": len(opts),
781:        if not triggers:
788:        if triggers or d.get("inner_kinds"):
805:        triggers = [asked] + [text for text, new in q.triggers if text != asked]
806:        q.triggers = []
807:        d = {"person": q.id, "triggers": list(dict.fromkeys(triggers)), "offered": len(opts),
822:            q.triggers.append(trigger)
```

```
$ grep -n "suspicion.report\|\.rise(\|may_fall(\|add_grudge(\|add_guilt(" world.py
160:    def may_fall(self, minute):
409:    def add_guilt(self, minute, fact, story, record):
418:    def add_grudge(self, holder, against, minute, fact, story, record):
420:        holder.grudge(against.id).rise(minute, fact)
751:        d["suspects_result"] = p.suspicion.report(suspect, minute)
760:            rose = p.grudge(angry).rise(minute, f"you were angry with {NAMES[angry]}", kind="angry")
764:            if t != angry and t in p.grudges and p.grudges[t].may_fall(minute):
873:            self.add_guilt(minute, f"you accused {target.name} of what you did, at minute {minute:02d}",
912:                        self.add_grudge(q, p, minute,
917:                        self.add_grudge(q, p, minute,
925:                        self.add_grudge(q, p, minute,
935:                        self.add_guilt(minute, f"{p.name} accused {target.name} of what you did, "
939:                        self.add_guilt(minute, f"{p.name} reassured you, at minute {minute:02d}",
1072:                    self.add_grudge(q, p, minute,

$ grep -n "guilt -\|guilt =\|guilt +=" world.py
222:        self.guilt = 1 if pid == culprit else None
415:            culprit.guilt += 1

$ grep -n "strength -=\|strength +=\|self.strength = " world.py
122:            self.target, self.strength = who, self.strength + 1
128:        self.strength -= 1
133:                self.target, self.strength = who, 1
156:            self.strength += 1
162:            self.strength -= 1

$ grep -n "\.hunger =" world.py
197:        self.hunger = d["hunger"]
728:            p.hunger = min(1.0, p.hunger + 0.004 * data.MINUTES_PER_TURN * p.sheet["hunger_rate"])
1065:            p.hunger = max(0.0, p.hunger - 0.4)
1089:                q.hunger = max(0.0, q.hunger - 0.4 * each)
```

```
$ grep -n "activity = " world.py
199:        self.activity = {"kind": "idle", "label": "standing at the pantry"}
698:            p.activity = {"kind": "idle", "label": "just come in"}
867:            p.activity = {"kind": "idle", "label": "standing"}
957:                    p.activity = {"kind": "idle", "label": "standing"}
959:                    p.activity = {"kind": "idle", "label": "talking"}
971:            person.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
977:            p.activity = {"kind": "idle", "label": "staying put"}
985:                p.activity = {"kind": "searching", "label": f"searching the {data.ROOMS[room]}",
995:                p.activity = {"kind": "idle", "label": "standing"}
1027:                person.activity = {"kind": "walking", "label": f"leaving for the {data.ROOMS[to]}"}
1045:            p.activity = {"kind": "sitting", "with": target.id, "label": f"sitting with {target.name}"}
1059:            p.activity = {"kind": "idle", "label": "eating"}
1081:            p.activity = {"kind": "idle", "label": "sharing out the food"}

$ grep -n 'Option("\|Option(f"' world.py
319:        opts.append(Option("silent", "stay put and say nothing", kind="silent"))
322:                opts.append(Option("ask_who", "ask everyone here who took the can", True, kind="ask"))
326:                opts.append(Option("deny", "deny taking it", True, kind="deny"))
330:                opts.append(Option(f"accuse_{q.id}", f"accuse {q.name} of taking it", True,
333:                opts.append(Option("confess", "admit taking it", True, kind="confess"))
337:                opts.append(Option(f"reassure_{q.id}", f"reassure {q.name}", True,
340:                opts.append(Option("reassure_all", "reassure everyone here", True, kind="reassure_all"))
341:            opts.append(Option("say_other", "say something else", True, kind="say"))
346:                opts.append(Option(f"sit_{q.id}", ("keep sitting with " if sitting else "sit with ") + q.name,
353:                    opts.append(Option(f"aside_{q.id}", f"take {q.name} aside to the {data.ROOMS[aside]}",
358:            opts.append(Option("keep_searching", f"carry on searching the {room}", kind="keep_searching"))
360:            opts.append(Option("search", f"search the {room} for the can (takes about six minutes)",
364:                opts.append(Option(f"go_{r}", f"go to the {data.ROOMS[r]}", kind="go", to=r))
366:            opts.append(Option("eat", "eat one of the portions", kind="eat"))
368:                opts.append(Option("share", "share out what is left among everyone here", kind="share"))
801:        opts = [Option("accept_aside", f"go with {p.name} to the {data.ROOMS[to]}", kind="accept_aside",
803:                Option("refuse_aside", f"refuse to go with {p.name}", kind="refuse_aside", partner=p.id)]
```

```
$ grep -n '"culprit"\|"night"' data.py
104:        "culprit": "daniel",
105:        "night": (3, "In the night Daniel eats a can standing at the counter in the dark. Nobody sees.",
109:        "culprit": "mara",
110:        "night": (3, "In the night Mara eats a can sitting on the kitchen floor. Nobody sees.",
114:        "culprit": None,
115:        "night": None,
159:    night = SCENARIOS[scenario]["night"]
165:    return SCENARIOS[scenario]["culprit"]

$ grep -n "thirst\|tired\|sleep\|fatigue\|energy\|mood" world.py data.py
(no matches)
```

```
$ ls cache/v5
gemini-3.5-flash-lite-mara_ate_it-seed1.json  ...-seed2.json  ...-seed3.json
gemini-3.5-flash-lite-miscount-seed1.json     ...-seed2.json  ...-seed3.json
gemma-4-31b-it-daniel_ate_it-gemma-seed1.json ... -seed5.json

$ grep -c '"prompt":' cache/v5/*.json
mara_ate_it-seed1:46  seed2:37  seed3:37 | miscount-seed1:56  seed2:93  seed3:70 |
gemma daniel_ate_it-seed1:21  seed2:13  seed3:20  seed4:19  seed5:14            (names shortened)

$ head -c 5000 cache/v5/gemini-3.5-flash-lite-mara_ate_it-seed1.json      → example (a) in §5.4
$ sed -n 43,45p cache/v5/gemini-3.5-flash-lite-miscount-seed2.json        → example (b) in §5.4
  (lines chosen with: grep -n 'In that time: ' FILE | grep 'Against [A-Z][a-z]* (' | grep 'Said and done' | head -1  → 43)

$ for p in 'Said and done in the' 'In that time: ' 'Against [A-Z][a-z]* (' 'About the can (' \
    'earlier things, left out' 'grown hungrier' 'looks '; do grep -c "$p" cache/v5/gemini-3.5-flash-lite-miscount-seed2.json; done
Said and done in the: 72 | In that time: : 77 | Against [A-Z][a-z]* (: 59 | About the can (: 43 |
earlier things, left out: 89 | grown hungrier: 7 | looks : 56

$ ls -l world.py data.py talk.py gemini.py cache/v5/...miscount-seed2.json cache/v5/...mara_ate_it-seed1.json
2026-09-25_14:26 mara_ate_it-seed1.json | 2026-09-25_15:10 miscount-seed2.json |
2026-09-25_14:15 data.py | 2026-09-25_03:12 gemini.py | 2026-09-25_03:02 talk.py | 2026-09-25_14:16 world.py
```

```
$ grep -c "**FALLBACK**: the model" runs/v5/*.md            → 1 in each of the 11 files
$ grep -ho "could not be used ([^)]*)" runs/v5/*.md | sort | uniq -c
     11 could not be used (the reason is given)              → the legend line, story.py:198
$ (per file) model_decisions / fallbacks / routine_decisions / lines_spoken / inner_moments /
  private_talks from runs/v5/*.meta.json                     → table in §7.3
```

---

## 9. NOT FOUND

- **Scenarios other than** `daniel_ate_it`, `mara_ate_it`, `miscount`: none in `data.SCENARIOS`
  (data.py:102-117) or the CLI choices (morning.py:136).
- **Needs other than hunger** (thirst, sleep, fatigue, energy): none (grep: no matches).
- **A numeric mood or emotion state:** none. Mood is only the `feeling` string, with
  `feeling_until`.
- **Trait changes during the morning:** none. Traits are read only at world.py:493.
- **Response fields beyond** `option`, `say`, `feeling`, `reason`, `suspects`, `angry_at`: none.
  Extra keys are ignored by `parse`.
- **A response field for a target or room separate from the option id:** none. Targets are
  encoded in the id (`accuse_<q>`, `go_<room>`, ...; talk.py:11-26).
- **An enum or validation of `option` in the API schema:** none (gemini.py:50). It is validated
  only in `parse` (world.py:566-569).
- **Length limits on `say`, `feeling` or `reason` enforced by code:** none. They are stated only
  in `SYSTEM`.
- **Any use of `reason` by the simulation:** none. It appears only in the story (story.py:84).
- **Re-asking or retrying the model after an unusable answer:** none (world.py:790-791, 810-811).
- **The trigger list as a prompt section:** none (`prompt_for`, world.py:483-540).
- **Inner-moment `rise_words` in the prompt:** none. Only the hunger sentence (world.py:427-428).
- **Suspicion changed by a rule event:** none. It changes only through `suspects`
  (world.py:751).
- **Guilt decreasing:** none (grep: only 222 and 415 assign it).
- **Portions replenished:** none. `portions` only decreases (world.py:1064, 1091).
- **An inner-moment path for a person asked aside:** none (`decide_aside`, world.py:799-815).
- **`accept_aside` / `refuse_aside` decisions in saved v5 runs:** none (`private_talks` = 0 in
  all 11 meta files).
- **A v5 run of `daniel_ate_it` on the default Flash Lite model:** none on disk (only
  `-gemma-seed1..5`).
