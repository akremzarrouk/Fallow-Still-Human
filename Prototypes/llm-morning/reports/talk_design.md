# Talk design: bringing something up, and telling someone who missed it

Mode: design. No code, no tests, no live call. Paths are from `Prototypes/llm-morning/`; line numbers are at HEAD
65fee7c.

## Amended by the user

These amendments, given by the user before implementation, override the text below wherever they differ. Each section
they change is marked *Amended (A…)* under its heading.

- **(A1) Topics in v1: the door visit only.** The topic table stays generic, so that food is one entry later.
- **(A2) No Q8 in v1.** Telling happens only at asks that happen anyway.
- **(A3) No `told` witness kind.**
  - The listener's claim goes into a **per-person belief store**: owner, claim text, about (event ids), source (the
    teller), minute, how (`"told"`).
  - The chronicle's witnesses stay "who perceived it".
  - The tell act is a chronicle event of its own, as designed.
- **(A4) Who reads beliefs.**
  - The night mind shows a person's beliefs of that day as records stamped at the minute told. S2 lets them be
    cited, and S8 counts a belief's events as known to its owner.
  - Block A carries each one next morning ("Yesterday at HH:MM, Elena told you that ...").
  - Block C does not read beliefs in v1.
  - Beliefs persist on the person, but are shown only on their day, that night and next morning.

**Sections changed:** Summary of decisions (rows 1, 2, 5), §1.1, §1.3, §2.2, §2.3, §2.4, §2.5, §4, §5, §7.3, §7.4,
§8, §9.

**Amended later, by the user (tell fix, `reports/tell_fix_impl.md`):** the topic options now come **first** in the option
list (§1.3, §4, Summary row 4), and while a tell is offered its teller's prompt says where each listener was, as the
teller perceived it (§4). Why: `reports/calm_variants.md`. With `tell_daniel_visit` moved from 18th or 19th to 1st, Leo
told Daniel in 7 of his 8 offers (0 of 4 at 18th or 19th); nobody else moved: Elena and Mara told in none of their
offers at any position. All 7 tells placed Daniel wrongly ("while you were sitting there"), and the teller's prompt had
no line on where Daniel was at 09:42.

## Why

`reports/talk_facts.md` found that no option carries a topic or is built from the past (§2). `say_other` was offered
in 608 decisions and chosen once (§1.3). Nobody learns of an event they missed, apart from a few cases the code sets
(§3).

In `reports/probe_after.md`, the woman at the door was not spoken of after 09:51 in any scene, and Daniel never learned
she came (§2, §3 findings 3 and 5). The people who saw her kept her at night (P2, P4), so the event mattered to them.
What was missing was a way to say it by day, and for the one who missed it to come to know.

## Sources read

| Source | Used for |
|---|---|
| `reports/talk_facts.md` | all of it |
| `reports/probe_after.md` §2, §3 | what went wrong, scene by scene |
| `CLAUDE.md:15-28` ("Judging changes", "North Star principles") | the principles below |
| `reports/repetition_probe.md` (Verdicts, "What the answers show") | the repetition lessons |
| `reports/food_wording_probe.md`, `reports/food_confront_impl.md` | the wording lessons |
| `quiet.py:815-880` (`door_end`), `chronicle.py`, `mind.py`, `memory.py`, `night.py:1040-1075` (block A) | where things land |

**The North Star vision doc (its speech-as-claims and mind-map parts): NOT FOUND.** No file holds "speech as claim",
"mind map" or "mindmap", and the only "North Star" text outside reports is `CLAUDE.md` (searched the repository,
`~/Desktop` and `~/Documents`; §10). This design follows the principles in `CLAUDE.md:21-28` instead. If the vision
doc exists elsewhere, items 2 and 3 should be checked against it before implementation.

**The lessons this design must respect:**

- **L1. A line that describes an act makes the small model do that act** (`CLAUDE.md:26-27`).
  - The food moment's old line made 18 of 18 eat. The neutral line "You are starving, and there is food on the
    shelf in front of everyone" made 5 of 18 give or share (`food_wording_probe.md`, Verdicts).
  - Putting `share` first in the option list moved Daniel from 1 share in 6 to 6 in 6 (same table, variant C): the
    order of options steers too.
- **L2. Showing a person their own words makes them repeat them.** 12 of 12 answers repeated word for word with the
  words shown, and 0 of 12 with only the verb and minute shown (`repetition_probe.md`, variants A and B).
- **L3. A line that counts repetitions turns repetition into intent.** "You have said the same words n times" still
  gave 12 of 12 repeats, and Elena's reasons named repeating as her aim (variant C). So fading has to be done by the
  code offering less, never by a line telling the person they have said it before.
- **L4. The code owns what happened and who perceived it; the AI owns the words** (`CLAUDE.md:22-25`). Who knows what
  is state, so it is the code's. What a person says is the model's.

## Summary of decisions

*Amended (A1-A4): row 1 is the visit only; row 2 has no `told` witness kind and no Q8, the claim is a belief; row 5 has no Q8.*

| # | Decision |
|---|---|
| 1 | **Topics.** From day 3 on (quiet days only), two kinds of event of the same day can become a topic: a **visit to the front door** (one topic per visit) and **food taken from the shelf** (eat, a portion given, a share). A person is offered a topic only if they perceived it, or were told it. **At most 2 topic options in a prompt.** Fading is by code: per speaker, 60 minutes off after choosing it and **at most 2 choices of one topic a day**; per room, 30 minutes off after anyone raises it; talk closes 6 hours after the topic opens and at the end of its day. |
| 2 | **Tell.** Offered when the speaker perceived the event first-hand, and someone awake in the room has neither perceived it nor been told. The listener keeps the words as speech, and a **claim built by code from the teller's own view**, marked "{Teller} told you that …", as a sure line. The chronicle gets a `tell` event and a new witness kind **`told`** on the events told of. The night mind shows it as a record stamped at the telling. Block A carries the claim next morning. A new quiet trigger, **Q8**, asks the knower once when the one who missed it comes in. |
| 3 | **Words versus claim.** In v1, choosing `tell_…` is choosing to tell what one saw: the claim is the teller's view whatever the words say. A mismatch between words and claim is logged as a warning only. Softening, leaving out and lying are left for a later version, where a claim can differ from the view. |
| 4 | **Labels.** `talk about {referent}` and `tell {Names} about {referent}`. The referent names only what the speaker perceived: never the outcome, the children, a judgment or their own earlier words. Topic options sit in a fixed place, ~~after `say_other`, never first~~ **first in the list** (tell fix). |
| 5 | **Cost.** At most about 44 tokens of options in a prompt, kept outside the trimming budget. About 57 tokens for each claim a listener holds. One night-mind record and one block-A line for each told topic. No new asks from the options themselves. Q8 adds at most one stretch per (topic, listener) a day, inside the existing 40 and 56. |

**Deviation from the brief:** the frozen cases replay from cache **through 09:42, not 09:51**. Under this design the
09:45 and 09:48 prompts differ from `probe_after`'s, because the visit becomes a topic when it ends at 09:45, so their
cached answers cannot answer them. Keeping topics closed until 09:51 would bend the design to fit the cache, and it
would skip the minutes a real family talks most (§7.1).

---

## 1. Bringing something up

### 1.1 Which events can become a topic

*Amended (A1): only the `visit` row is built in v1. The table stays generic; `food` is a later entry.*

**Decision.** Two kinds of event of the current day, from day 3 on (`m.quiet is not None`):

| Topic | Made of | Opens | Who has it |
|---|---|---|---|
| `visit` | one door visit: knock, the visitor's lines, the door acts, the end | at `door_end` | whoever has a door summary that is not the bare knocking line (`quiet.py:834-871`: at the door, heard the knock in words, or heard the visitor speak); and whoever is told |
| `food_<actor>` | the actor's latest `eat`, `eat_given`, `give` or `share` of the day (`memory.WEIGHT` 3 or 4) | at the act | whoever perceived the act ("did"/"saw"); and whoever is told |

**Argument against.**

- *A real family talks about anything: a quarrel, a fear, the night before.* A whitelist of two is far from that.
- *Why not use every event of weight 3 or more, or every event at all?* That would include accusations, confrontations
  and reassurances.
- *Food on day 3 is rare*: the shelf is at 0 in every frozen scene, so `food` is untested by the probe.
- *The night's trips are the family's biggest topic,* and they are left out.

**Why it stands.**

- **The aim is news, not the general conversation, which the model already holds.**
  - Accusations and confrontations already have options that name their target, and are chosen all day (`probe_after`
    §2: Mara accused Daniel 9 times in scene 1).
  - A topic option for them would be a second door to the same quarrel, and the model takes doors it is shown (L1).
  - The two kinds chosen are the ones where **someone can be absent and the fact matters to them**: a stranger was
    given or refused the house's water, and someone ate from the shelf.
- **Night trips already reach the whole house by morning** (`night.py:195-205`, `trips_known`), and the water rule
  reaches everyone through the water line (`quiet.py:327-338`). A topic for them would add nothing a person does not
  already know.
- **The confession** is left out because hearsay of who took the can would set `knows_culprit` (`chronicle.py:120`) by
  a new route into the day-1 plot. That is its own decision (§8).
- **`food` is kept, though the probe cannot test it.** It is the other plain case of news a person can miss: the shelf
  is the family's shared stake. It is tested by unit tests only, and is behind the same day gate.

**The day gate.** No topic on days 1 and 2. So v16's days 1 and 2, and day 3 until the knock, have byte-identical
prompts (§6), and the frozen cases replay from cache to 09:42.

### 1.2 For whom

**Decision.** p is offered T if:
- p is awake, with someone else awake in the room (topic options are speech, like `say_other`, `world.py:544-578`);
- p **knows** T: p perceived T (any witness kind but `voices`), or p was told T; and
- T is open for p (§1.4).

**Argument against.** A person who only heard knocking from another room knows little, and one who was told knows only
what they heard. Should they be able to raise it?

**Why it stands.** Yes, for `talk`: "Who was at the door this morning?" is exactly how someone who heard only knocking
raises it. Their referent says only what they perceived ("the knocking at the front door at 09:42", §4). For `tell`, a
first-hand account is required (§2.1).

### 1.3 How many in a prompt

*Amended (A1): with the visit only, a prompt holds at most one topic option in v1. The cap of 2 and the ranking stay in the code for later topics.*

*Amended (tell fix, `reports/tell_fix_impl.md`): this order is now also their place: the topic options are the first
options in the list, in this order, and no other option moves (`reports/calm_variants.md`: at the top, Leo told in 7 of
8 offers; at 18th or 19th, in 0 of 4).*

**Decision.** At most **2** topic options in a prompt, and at most **one option per topic**:
- `tell_<names>_<T>` if someone present lacks T;
- otherwise `talk_<T>`.

When there are more than 2: tell options before talk options, then the heavier topic (`visit` 4, `food` as
`memory.WEIGHT`), then the more recent.

**Argument against.**
- With two topics a day, why cap at all?
- One option per topic hides the choice between telling the one who missed it and talking to the room.

**Why it stands.**
- The cap bounds prompt length and mirroring pressure on a day with several food acts.
- Telling someone in front of the room *is* talking about it with the room: the others hear the words (§2.3). A
  second option for the same thing would double the topic's weight in the list (L1).

### 1.4 How a topic fades

Every rule here is in the code's offer. None is a prompt line (L3). A person never sees a count, a "you already said
this" or their own earlier words about it (L2).

| Rule | What it does |
|---|---|
| **F1. Window** | `talk_T` is offered from T's opening for 6 hours (the visit at 09:45: until 15:45), and never after the end of T's day. `tell_*_T` is offered until the end of the day after T's: the one who missed it can be told next morning. |
| **F2. Speaker cooldown** | After p chooses `talk_T` or `tell_*_T`, neither is offered to p for 60 minutes (20 turns). |
| **F3. Guard** | p chooses T's options **at most 2 times a day**, counting `talk_T` and every `tell_*_T` together. After the 2nd, none of T's options is offered to p that day. |
| **F4. Room** | After anyone raises T in a room, `talk_T` is not offered to anyone in that room for 30 minutes. A reply to the one who raised it goes through the ordinary options, with the reply's own words. |
| **F5. Told** | `tell_*_T` for q closes for everyone once q knows T. |
| (existing) | Any speech kind used 3 turns in a row is not offered a 4th time (`world.py:611-614`). `talk` and `tell` are kinds of their own, so this applies to them. |

**Argument against.** Real people return to a shock many times a day: Elena may well bring the woman up five times.
A cap of 2 is unhuman. Hiding the option for 60 minutes also hides it at the moment someone new walks in.

**Why it stands.**
- **"Mechanisms may be unhuman; the output must read as human"** (`CLAUDE.md:28`). The cap does not stop anyone
  speaking of the woman. Any option's words can mention her, and the cap counts only the topic options. It only
  limits how often the code holds the topic out.
- The small model takes what it is shown (L1) and repeats what it said (L2). A topic offered every ask for six hours,
  with no cap, would be chosen turn after turn, and the day would become the visit on a loop: the same failure
  `repetition_audit.md` found with reassurance.
- A new person walking in is handled by `tell` and Q8 (§2.5), which F2 does not block for other speakers.

---

## 2. Telling someone who missed it

### 2.1 When it is offered

**Decision.** `tell_<names>_<T>` is offered to p when:
- p knows T **first-hand**: witness kind `did`, `saw` or `heard`; for a visit, p holds a door summary with an outcome;
- at least one person awake in p's room neither perceived T nor was told it (those are `<names>`, in family order);
- F1 to F5 allow it.

**Argument against.**
- *Someone told can pass it on*: Daniel, told by Elena, could tell Leo if Leo had missed it.
- *A teller may deliberately keep it from someone,* and an option offered at every ask while they are together
  pushes them to tell (L1).

**Why it stands.**
- **Second-hand telling** needs a claim of a claim ("Daniel told you that Elena had told him…"). In a house of four
  where three saw the visit it barely arises, so it is left for later (§8). A told person can still `talk` about it.
- **Keeping it from someone** stays a real choice. The option is offered, not taken: in `probe_after` scene 1 Elena
  was offered `confront_mara` and did not take it (P1). Choosing not to tell is visible in the log as offers not
  taken. Nothing in the prompt says the listener does not know, apart from the label itself (§4).

### 2.2 What the listener keeps: a claim, marked with its source

*Amended (A3): the claim is kept in the listener's belief store, not as a sure line. The day's prompts show it among "What you are sure of" from the store.*

**Decision.** The code builds the claim from **the teller's own view**, never from the world.

For a visit, it is the teller's door summary (`quiet.py:834-871`, built for the teller as viewpoint), rendered for the
listener:
- the teller's "you" becomes their name with "herself" or "himself";
- the listener's name becomes "you";
- what the visitor said she needed is added, **as the teller heard it**, when the teller heard the line that names it
  (the household's children as `door_heard_impl.md` words them).

So:
- *Scene 1, Elena to Daniel:* "Elena told you that at 09:42 a woman knocked at the front door and asked for water;
  that Elena herself told her to go away, and that Mara handed her about three litres of the stored water anyway."
- *Scene 3, Leo to Daniel:* "Leo told you that at 09:42 a woman knocked at the front door and asked for water for her
  boy of six; that Elena told her to go away, and that Mara handed her about three litres of the stored water anyway."
- *Scene 4, Mara to Daniel* (she looked through the gap): "Mara told you that at 09:42 a woman of about forty-five
  knocked at the front door and asked for water for her girl and boy of five; that Elena told her to go away."

For food: "{Teller} told you that at {clock} {Name} ate a portion from the shelf." (and the same for gave … a portion
and shared out the food).

**Argument against.**
- *A claim built by code puts words in the teller's mouth.* The listener holds a sentence the teller never said.
- *Why should Daniel know "about three litres"* when Elena may only have said "some water"?

**Why it stands.**
- **The claim is not what was said; it is what the listener now holds as having been told.** It is marked as such,
  and the words are kept beside it (§2.3), so the prompt shows both.
- "The code owns the truth: what happened, who perceived it" (`CLAUDE.md:22`). Who has been told what is exactly
  such a truth. It must be state, because the model cannot be trusted to carry it: the night minds' "none left"
  against about 95 litres (`probe_after` finding 2) is what happens when belief comes from free words.
- The claim never holds more than the teller perceived: it is built from the teller's summary, which states each act
  only if the teller perceived it (`quiet.py:843-866`).
- The marking matters. "Elena told you" is true even if Elena were wrong. So the listener's night mind can doubt it,
  and nothing in the code treats it as Daniel's own sight (§2.4).

### 2.3 Where it lands

*Amended (A3, A4): no `told` witness kind; the events told of keep their witnesses. The claim is a belief (owner, claim, about, source, minute, how). The night mind's records, S2, S8 and block A read the belief store; block C does not. The site table below is not needed: no witness list changes.*

| Where | What |
|---|---|
| **Listener's memory** | The words, as any speech line, through `perceive` (`world.py:1608-1612`): `Elena tells you about the woman at the front door: "<words>"`. |
| **Listener's sure lines** | `<clock>: <claim>`. Never trimmed for the rest of the day (`world.py:1186`). |
| **Others in the room** | The words, as speech to the named listeners: `Elena tells Daniel about the woman at the front door: "<words>"`. |
| **Teller's memory** | `you told Daniel about the woman at the front door.` with no words, as for all own speech (`world.py:1841-1844`; L2). |
| **Newness** | New the first time per (teller, topic, listener), so it starts a conversation as a new fact does (`talk.py:65`). |
| **Chronicle: the telling** | A new event of kind `tell`: actor the teller, `members` the listeners, `about` the topic's event ids, the words. Witnesses as for any speech: `did`, `saw`, `voices`. |
| **Chronicle: the events told of** | Each event in `about` gets each listener as a witness of the new kind **`told`**, with `views[q]` = the claim and `seen_at[q]` = the minute of the telling. (`seen_at` already exists for routine spans, `mind.py:79`.) |
| **Night mind** | `records()` (`mind.py:55-86`) shows a `told` event at its `seen_at`, with the claim as its text: `[D3-030] 10:03: Elena told you that …`. S2 (`mind.py:285`) lets the listener cite it. S8's `matching` (`mind.py:202`) counts `told` events as known: Daniel's "Mara gave water away" is not a false claim; it is what he was told. |
| **Block A, next morning** | One line per topic told: `Yesterday at 10:03, Elena told you that …`, beside the door summary that witnesses get (`night.py:1066-1069`). |
| **Block C** | Not in v1. C phrases events as seen ("Two days ago, Mara ate a portion in front of you", `memory.py`), so a `told` event would read as witnessed. `memory.py:77`, `177` and `189` keep only perceived kinds. What a person told keeps comes through their night mind's memories (B, then C's "You thought then"). |

**Every place that reads `witnesses`** must decide whether `told` counts. The list (`grep 'in e["witnesses"]|witnesses.get(|["witnesses"]['`):

| Site | `told` counts? | Why |
|---|---|---|
| `chronicle.py:112` (`perceived`) | no | it says "perceived" |
| `chronicle.py:120` (`knows_culprit` from a confession) | no | confession is not a topic in v1 (§1.1) |
| `chronicle.py:137` (gists) | yes | the listener's name for it |
| `memory.py:77`, `177`, `189`; `memory.py:95` | no | block C (above), and "has not come back" lines |
| `mind.py:58`, `65` (records) | yes | shown at `seen_at` with the claim |
| `mind.py:202` (S8 `matching`) | yes | the claim is what they were told |
| `mind.py:285` (S2) | yes | they may cite what they were told |
| `night.py` (night witnesses), `quiet.py:180` (`last_meals`) | no | perception only |

The rule for the implementation: a helper `perceived(e, pid)` (any kind but `told`) and `knows(e, pid)` (any kind),
and each site above uses the one in its row.

**Argument against.**
- *Writing `told` into another event's witnesses blurs the chronicle's one meaning:* who perceived it.
- *Why not just the `tell` event,* which Daniel did perceive?

**Why it stands.**
- **The `tell` event alone leaves the claim nowhere.** Its view for Daniel would be Elena's words. The night mind
  would then infer the visit from free words, as it inferred "none left": the failure this design is meant to end.
- **With `told`, the chronicle says exactly what is true:** Daniel did not see D3-030, and he was told of it at 10:03,
  in Elena's account.
- The blur is contained by the site table: nothing that means "perceived" reads `told`.

### 2.4 The listener's own view afterwards

*Amended (A3): "their records say told" becomes: their night-mind record of it is the belief, stamped at the minute told.*

**Decision.** Once told, the listener **knows** T:
- they may `talk` about it (§1.2);
- `tell` to them closes (F5);
- their prompts hold the claim in their sure lines.

They do not get the teller's door summary as their own: the summary is for those who perceived the visit. Their
records say "told".

**Argument against.** If Daniel is told twice (by Elena at 09:48 and Leo at 11:45), why should the second not add
anything?

**Why it stands.** F5 closes `tell` once Daniel knows, so a second tell is not offered. Leo can still `talk` about the
woman with Daniel in the room, and Daniel hears those words as speech. Two differing accounts (one teller softening)
belong with v2's claims that can differ from views (§3).

### 2.5 Q8: the knower is asked when the one who missed it comes in

*Amended (A2): not in v1.*

**Decision.** A new quiet trigger, Q8, built like Q2 (`quiet.py`'s `arrive`):
- **When:** q comes into a room, or wakes from rest in one, and an awake p there knows an open topic T first-hand
  that q does not know.
- **No stretch running:** p is asked once for (T, q).
- **Who is asked, when several know:** `did` before `saw` before `heard`, then family order.
- **What p is shown:** the same arrival line p perceives anyway ("Daniel comes into the kitchen"). No line says
  Daniel does not know.
- **Budget:** like Q2: ordinary, inside the 40 and the 56, and refused when `budget()` says so.
- **Stretch:** it starts one, as Q2 does (`STRETCH_ASKS` 8).
- **At most:** once per (T, q) a day.
- **Inside a running stretch:** nothing is needed, because everyone in the room is asked anyway.

**Argument against.**
- It adds a trigger, and quiet-day asks are scarce. `probe_after`'s day 3 spent 50 or 51 of 56.
- It also chooses who is asked, which is a small piece of judgment in code.

**Why it stands.**
- **Without Q8, telling depends on chance.** In quiet mode nobody is asked when someone walks in, so the moment a
  real family tells ("You missed it, a woman came to the door") would pass unasked. Daniel was home all day in all
  three scenes and was never told.
- **The code picks only who is asked, not what they do.** The one who did the act is asked first because they are
  the one the topic is about, not because they must speak. They may choose anything, and the log shows it.
- **Cost is small and bounded** (§5).

### 2.6 Telling at night

**Not in v1.** The night's options are their own set (`night.py:502-736`). Telling in a low voice at bedtime is real
(Leo and Daniel share a room). It is left for later (§8), so that the night stays as `night_design.md` built it until
the day's telling has been seen to work.

---

## 3. Words versus claim

**Decision (v1).**
- **Choosing `tell_<names>_<T>` is choosing to tell what one perceived.** The claim is the teller's view, whatever the
  words. The words are kept as spoken (§2.3).
- **A mismatch is logged, never acted on.** A run-log check, **T1**, warns when a tell's words name nothing of the
  topic, or deny its outcome.
  - "Name nothing": none of the topic's anchors. For a visit: front door, knock, the visitor as perceived (woman, man,
    someone), water or food, the actors' names. For food: portion, ate, food, shelf, the actor's name.
  - "Deny its outcome": a negation word before the outcome's verb, as S8 reads negation (`mind.py:258`).
  - Like S8 since `checks_to_warnings.md`, T1 changes nothing in the listener's state.

**Argument against.**
- **This is not how telling works.** If Mara says to Daniel "Someone knocked, it was nothing", a real Daniel knows
  only that someone knocked and that Mara thought it nothing. Under v1 he holds "Mara told you that … Mara herself
  handed her about three litres", which Mara never said. The claim outruns the words.
- **A lie (the teller saying "we gave nothing") cannot happen in v1 at all.** So the listener always learns the
  truth as the teller saw it.

**Why it stands for v1, and what is left.**
- **The code cannot read what free words add** (`talk.py:69`, Newness: "the rules cannot read what free words add").
  Building the claim from the words would make state depend on parsing the model's prose: the "none left" failure
  again.
- **The model already chooses the act.** In v1 the act is "tell what you saw", and its words are its manner. A person
  who wants to soften or hide it can choose another option with words that mention the topic (`talk`, `say_other`,
  `reassure`). Those carry no claim, and the listener keeps only the words.
- **So v1 cannot express a told lie, and does not pretend to.**
- **Left for later**, needing claims that can differ from the view: speech-as-claims, if the vision doc says so.
  - *A partial tell:* an option `tell_part_<…>` whose claim leaves out the teller's own act.
  - *A false tell:* a claim that differs from the view, with the listener's belief built from the claim and the
    chronicle keeping both.
  - *A claim heard in ordinary speech:* Leo's "we have none left ourselves" heard as a claim about the stores.
    `probe_after` finding 2 is exactly this. v1 does not touch it.
  - *Two differing accounts held by one listener.*

  T1's warnings, counted over the frozen cases, say how often the words in v1 already differ from the claim: the
  measure of how much v2 is needed.

---

## 4. Option labels

*Amended (A1): only the visit's referents apply in v1.*

**Decision.**

| Option | id | Label (exact form) |
|---|---|---|
| talk | `talk_visit`, `talk_food_<actor>` | `talk about {referent}` |
| tell | `tell_<names>_visit`, `tell_<names>_food_<actor>` | `tell {Names} about {referent}` |

Both are marked `(speech)`, so `say` holds the words (`world.py:1180`, `43-46`).

**The referent** is a noun phrase from what the speaker perceived, with the clock:
- **visit:**
  - "the woman at the front door at 09:42" when they heard the visitor or saw her (her description as `door_end`
    words it);
  - "someone at the front door at 09:42" when they heard a voice but no word of who;
  - "the knocking at the front door at 09:42" when they only heard knocking.
- **food:** `chronicle.gist`'s phrase for the act with the actor named: "Leo eating a portion at 11:00", "Elena giving
  Mara a portion at 11:00", "Mara sharing out the food at 11:00".

**The referent never holds:**
- the outcome ("the woman you turned away", "the water Mara gave");
- the children;
- a feeling or judgment ("the poor woman", "Mara's defiance");
- the speaker's own earlier words (L2);
- a count ("again", L3).

**Place:** ~~topic options come right after `say_other` in the list, in the order of §1.3, before `sit_` and
`aside_`. Never first.~~

*Amended (tell fix, `reports/tell_fix_impl.md`):* **topic options come first in the list**, in the order of §1.3; every
other option keeps its place relative to the rest. **Why** (`reports/calm_variants.md`, variant O):
- With `tell_daniel_visit` moved from 18th or 19th to 1st, and nothing else changed, Leo told Daniel in 3 of his 4
  offers (7 of 8 with variant TO), against 0 of 4 at 18th or 19th.
- Nobody else moved: Elena reassured and Mara accused in all their asks, at either position. So the place does not
  make everyone tell. It lets the one with a reason to tell do it.
- The worry below (order steers) is real, and was measured: no variant was over-steered (at most 4 of 14 tells).

*Also amended (tell fix):* while a `tell_<names>_<T>` is offered to p, p's sure block holds, per listener, what p
perceived of where they were: "<Name> was not in the kitchen when the woman came to the door", with "; <he|she> came
in at HH:MM" only if p perceived that arrival. It goes once the listener knows T (F5 closes the tell). Why: all 7 tells
in `calm_variants.md` placed Daniel wrongly ("while you were sitting there"), and the teller's prompt said nothing of
where he had been. The line states a situation, not an act: it names no option and tells nobody to speak.

**Argument against.**
- *Every label is an act; "tell Daniel about …" tells the model that Daniel does not know, and invites telling* (L1).
- *Leaving the children out of the label hides what makes the visit matter in scenes 3 and 4.*
- *"talk about" is vaguer than "bring up",* which says that the person starts it.

**Why it stands.**
- **An option is an act by nature;** L1 is about lines that are not options. The food probe's lesson was that a
  *situation line* naming eating made everyone eat, and that *order* steers. So no situation line is added ("Daniel
  missed the visit" is not written anywhere), and the topic options get a fixed middle place. *(Tell fix: the
  place is now first, see above. The whereabouts line does imply that the listener missed it; it is shown only while
  the tell is already offered, so it adds no act the option list does not already hold.)*
- **"tell {Names}" is the minimum that makes the option mean telling.** Who is absent from the knowledge is a fact
  the label must carry; how it matters is not.
- **The children are in the claim and in the memory** of those who heard them. A label that named them would weight
  the topic by its pathos, a judgment the model owns, not the code.
- **"talk about" was chosen over "bring up"** because "bring up" carries a nuance of confronting someone with it;
  "talk about" leaves the manner to the words.

---

## 5. Cost

*Amended (A2, A3): no Q8, so no asks are added; the claim is shown from the belief store, at the same length.*

**Prompt length**, from `estimate_tokens` (`world.py:135-137`; §10, command 4):

| Line | Est. tokens | Where |
|---|---|---|
| `- tell_daniel_visit: (speech) tell Daniel about the woman at the front door at 09:42` | 24 | options, **outside** the trimming budget (as the trip and W1 options, `world.py:1203`, `1213`) so that they never push a memory line out |
| `- talk_visit: (speech) talk about the woman at the front door at 09:42` | 20 | as above |
| at most 2 topic options | ≤ 44 | about 2% of the day-3 prompts from 09:42 (scene 1: 1954 to 2157 tokens, median 2075) |
| the listener's claim (sure line) | about 57 | inside the budget, as all sure lines. With the prompt already over the budget, it may trim one or two of the oldest "What else happened" lines |
| the teller's own line | about 10 | memory |
| night-mind record of a told event | about 60 per topic | inside `RECORDS_MAX` 1600 (`mind.py:31`) |
| block A line | about 60 per topic | inside `MEMORY_MAX` 560, shared with B and C (`memory.py:9`). A, B and C trim under one bound (`memory.bounded`), so on a heavy day a told line can push out a C line |

**Asks per day:**
- **The options add no ask:** they appear at asks that happen anyway.
- **Q8** adds at most one ask, and one stretch, per (topic, listener) a day, only when no stretch is running. With one
  visit and at most three who missed it, that is **at most 3 Q8 a day**, each starting a stretch of up to 8 asks.
- **The day caps still bind:** the ordinary 40 and the day's 56, with the evening's 8 owed only while someone holds a
  trip position (`reports/two_fixes_impl.md`). So the worst case moves asks within the cap; it cannot raise the day
  above 56.
- **In the frozen cases** Daniel comes into the kitchen inside the Q7 stretch (09:45), so Q8 is expected to fire at
  most once a scene.

**Code:** the topic table (two entries), the referent and claim builders, the `told` kind with its site table (§2.3),
F1 to F5, Q8, T1. No change to weights, caps or the night.

---

## 6. What must stay the same

- **No topic, no change:** with no open topic, every prompt is byte-identical to now. This holds for days 1 and 2
  (day gate), and for day 3 until the first topic opens.
- **Tests that must show it:**
  - v16 seeds 1 to 3 replay from `cache/v16` with 0 API requests;
  - `probe_door2`'s scenes replay to 09:42 with 0 live asks;
  - the frozen versions v1 to v14 are not touched (`CLAUDE.md:7`).
- **The chronicle's existing witness kinds keep their meaning:** `told` is added, never substituted. Every site in
  §2.3's table is tested for its row.

---

## 7. Frozen cases

### 7.1 What is run

`probe_after`'s scenes 1, 3 and 4 (`runs/probe_after/probe.py`): v16 seed 2 to day 3, the same visitor at 09:42 (h13,
h16, h23), client seeds 101, 103 and 104. They run on the implementation's commit, then on to day 4's blocks. Day 4 is
not played.

- **Replayed from cache through 09:42.** Scene k's cache starts as a copy of `cache/probe_door2/scene<k>.json`, as
  `probe_after` did (`probe.py:8-11`). It answers every ask through the knock minute: 123 a scene.
  - The client refuses every ask until `door_end` has run (`probe_after`'s `Capped` client).
  - So no live ask is possible before 09:45.
- **Live from 09:45** to day 4's blocks: the rest of day 3, night 3's asks, the night minds.
- **Why not 09:51, as the brief asks.** At 09:45 the visit has ended and is a topic. Elena, Leo and Mara are offered
  `tell_daniel_visit` or `talk_visit` from their 09:45 ask on, and Daniel comes in at 09:45. So the 09:45 and 09:48
  prompts are not `probe_after`'s, and `cache/probe_after`'s answers to them cannot be used. The only way to replay to
  09:51 is to keep topics closed until the Q7 stretch ends. That drops the minutes right after the door, when a real
  family talks most, to fit a cache. Not taken; **decision 1 for the user (§9)**.
- **Not `cache/probe_after` as the source:** a byte-identical prompt after 09:45 (Daniel's, if nobody has told him
  yet) would reuse one of `probe_after`'s answers inside a different run. With `probe_door2`'s cache as the source,
  every ask from 09:45 is this run's own.
- **The budget fix differs too.** `reports/two_fixes_impl.md` came after `probe_after`. On a day with no trip
  position, the evening's 8 are no longer held back, so Q1 at 17:39 and 19:00 can fire where `probe_after` refused
  them. Differences after 17:39 are not all this design's. The report must separate them: list every Q1 that
  `probe_after` refused and this run fired.

### 7.2 Validity checks (all must pass before any prediction is read)

| # | Check | Counting rule |
|---|---|---|
| V1 | Fake run first | `probe.py --fake` (fake model, temp folder) exits 0 for all three scenes and reaches `done`. |
| V2 | Nothing live before 09:45 | each scene: `from_cache` = 123, and the ledger shows no ask refused before `door_end`. |
| V3 | Topics open on time | no topic option in any prompt before 09:45 (search every recorded prompt for `- talk_`, `- tell_`). |
| V4 | Claims are the teller's view | for every `tell` event, each listener's `told` view equals the claim the builder gives for (teller, listener) from the teller's door summary (string equality, recomputed in the reading script). |
| V5 | The guard holds | §7.3, P3. It is code-enforced, so a failure here is a bug, not a result. |

### 7.3 Predictions (frozen before any live call)

*Amended (A3): in P1, "Daniel holds `told` on that door_end event" becomes "Daniel holds a belief whose about includes that door_end event".*

Each counts over the run's records (`runs/talk_probe/scene<k>.json`, as `probe_after`'s). "Day 3" means from 09:45 to
the end of the day's last turn. "Night 3" means its night asks and night minds.

| # | Prediction | Counting rule |
|---|---|---|
| **P1** | **Daniel learns of the visit by night 3 in at least 2 of 3 scenes.** | A scene counts if the chronicle holds a `tell` event on day 3 whose `members` include `daniel` and whose `about` includes that scene's `door_end` event, or if Daniel holds `told` on that `door_end` event. The night is included in the window, but v1 has no telling at night (§2.6), so in practice it is day 3. |
| **P2** | **The visitor or the children are brought up after 10:00 in at least 1 of 3 scenes.** | A scene counts if any decision on day 3 at a minute ≥ 180 (10:00) either chose `talk_visit` or a `tell_*_visit`, or has words that match, case-insensitive, `\b(woman\|visitor\|stranger\|front door\|knock\w*\|boy\|girl\|child\|children\|kids?)\b`. Door acts are excluded (there are none after 09:45). |
| **P3** | **Repetition guard: no person chooses one topic more than 2 times on day 3.** | Per scene, per person, per topic: count decisions whose option is `talk_T` or any `tell_*_T`. Every count ≤ 2. (Code-enforced; also V5.) |
| **P4** | **The topic is not chosen at most chances: over the three scenes, a topic option is chosen in at most 40% of the day-3 decisions that offered one.** | Denominator: model decisions on day 3 whose prompt lists at least one `- talk_` or `- tell_` option. Numerator: those that chose one. A check on L1: offered is not taken. |
| **P5** | **Whoever is told keeps it into day 4.** | In every scene that counts for P1, Daniel's day-4 block A holds a line starting `Yesterday at` and containing `told you that at 09:42`. |
| **P6** | **A told claim names the children where the teller heard them.** | In scenes 3 and 4, every claim given to Daniel about the visit names the child or children ("boy of six"; "girl and boy of five"), when the teller is one who heard the line that named them. All three did, `probe_after` §1. (Follows from V4 if the builder is right; it is listed because the claim is the only place the children reach Daniel.) |

**Not predicted:** whether the night minds stop writing "none left" (`probe_after` finding 2). This design does not
touch claims about the stores (§3).

### 7.4 Live-ask budget

*Amended (A2): no Q8 stretch; the expected count is 32 to 40 a scene, the caps are unchanged.*

- **The quota:** 500 requests a day free (`CLAUDE.md:5-6`).
- **The baseline:** `probe_after` made 95 live asks: 32, 31 and 32. Each scene is the rest of day 3, night 3's 4 asks
  and 4 night minds.
- **What this adds:** at most 1 Q8 stretch a scene (up to 8 asks), and Q1s the budget fix no longer refuses (up to 8).
  Expected 32 to 48 a scene.
- **Cap: 150 live asks in all three scenes;** a scene stops at 60 live asks (the run then marks it stopped and reads
  what it has). No scene runs twice (the ledger, as `probe_after`).
- **The fake run** (V1) makes no live call. The plan file and the probe's sha256 are recorded before the live run,
  and checked again at the end, as `probe_after` did.

---

## 8. Left for later

*Amended (A1-A4): food as a topic, Q8, and beliefs in block C join this list.*

| What | Why not v1 |
|---|---|
| Claims that differ from the view: partial tells, lies, two accounts | §3. Needs the claim to be its own state, apart from truth. |
| Claims in ordinary speech ("none left") | `probe_after` finding 2. The same need. |
| Second-hand telling | §2.1. Rare in a house of four. Needs a claim of a claim. |
| Telling at night | §2.6. The night's options are their own set. |
| The confession as a topic | §1.1. Hearsay would set `knows_culprit` by a new route. |
| Topics from earlier days ("the woman yesterday") | F1 closes talk at day's end. The night mind's B and C already carry what each kept. |
| `told` in block C | §2.3. C's lines read as witnessed. |
| Other topic kinds (a quarrel, a fear, a rule made) | §1.1. They have options already, or reach everyone already. |

## 9. Decisions for the user

*Amended: decisions 2 (Q8) and 4 (food) were taken by A2 and A1. The vision doc (5) is unchanged.*

1. **The replay point (§7.1).** This design replays to 09:42 and goes live from 09:45. To replay to 09:51 as the brief
   says, topics would have to stay closed until the Q7 stretch ends, which I argue against.
2. **Whether Q8's cost is acceptable** (§2.5, §5), or whether telling should rely only on asks that happen anyway. In
   the frozen cases, Daniel's 09:45 arrival is inside the stretch, so P1 does not depend on Q8.
3. **The guard's number** (2 a day, F3) and **talk's window** (6 hours, F1) are judgment, not measurement.
   `repetition_probe.md` measured single moments, not a day.
4. **`food` as a v1 topic** that the frozen cases cannot exercise (§1.1), or visit only in v1.
5. **The vision doc.** If it exists outside the repository, items 2 and 3 should be checked against its
   speech-as-claims and mind-map parts.

## 10. Commands run

All read-only; from the repository root or `Prototypes/llm-morning/`.

1. **The vision doc.** All three searches found nothing but `CLAUDE.md` and reports that cite it:
   - `find . -iname "CLAUDE.md"`, then `grep -rli "north star" --include=*.md .`: `./CLAUDE.md` and 7 files in
     `Prototypes/llm-morning/reports/`.
   - `grep -rIli "mind-map|mindmap|mind map|north star|northstar" --exclude-dir=Library --exclude-dir=.git …`: the
     same files.
   - `grep -rIli "north star" --include=*.md --include=*.txt Desktop Documents` (from `~`, without the prototype):
     `Desktop/Projects/Fallow/CLAUDE.md` only.
2. **The door events of `probe_after`'s scenes**, read from `runs/probe_after/scene{1,3,4}.json` `day3_events`:
   - Witnesses of `door_end` in every scene: Elena, Leo and Mara, not Daniel.
   - The summaries name no child: scene 4's Mara has "a woman of about forty-five".
   - The visitor's first line names "a little boy at home, he's six" (scene 3) and "a girl of five and a boy of five"
     (scene 4).
3. **Where each one was, and the asks from 09:45**, read from `day4_blocks[*]["A"]` and `asks`:
   - Daniel was in the kitchen 09:51 to 11:45 in all three scenes, with Elena and Mara (scene 1) or all three
     (scenes 3, 4).
   - Day asks from 09:45: 24 (scene 1), 23 (scene 3), 24 (scene 4). Elena, Leo and Mara were each asked at 09:45 and
     09:48.
4. **Tokens.** `estimate_tokens` of the two option lines and a claim line: 24, 20, 57. Scene 1's day prompts from
   09:42: n 27, min 1954, median 2075, max 2157.
5. **The `witnesses` sites:** `grep -n 'in e["witnesses"]|witnesses.get(|["witnesses"]['` over the `.py` files: the
   table in §2.3 (`memory.py:95` reads `went["witnesses"]`, added by reading).
