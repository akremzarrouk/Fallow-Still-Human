# Talk probe: plan (frozen before any live call)

Mode: run. The probe is `runs/talk_probe/probe.py`, from `runs/probe_after/probe.py`. It runs scenes 1, 3 and 4 with
client seeds 101, 103 and 104. Scene k's cache starts as a copy of `cache/probe_door2/scene<k>.json`, so no live ask
is possible before 09:45. It plays live from 09:45 to day 4's blocks. The cap is 150 live asks in all and 60 in a
scene. The key comes from `GEMINI_API_KEY` and is written to no file. No scene runs twice (the ledger).

The question: do topics and telling make the stranger part of the family's day, and does Daniel come to know?

The checks and predictions below are copied word for word from `reports/talk_design.md` §7, with the amendments that
apply to them. Nothing in them is changed. Headings are one level down here.

P1 rests on ordinary asks only (no Q8, A2); if it fails, that is evidence for Q8, not for changing P1.

## The user's amendments (copied from `reports/talk_design.md`)

### Amended by the user

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

## Validity checks (§7.2, word for word)

### Validity checks (all must pass before any prediction is read)

| # | Check | Counting rule |
|---|---|---|
| V1 | Fake run first | `probe.py --fake` (fake model, temp folder) exits 0 for all three scenes and reaches `done`. |
| V2 | Nothing live before 09:45 | each scene: `from_cache` = 123, and the ledger shows no ask refused before `door_end`. |
| V3 | Topics open on time | no topic option in any prompt before 09:45 (search every recorded prompt for `- talk_`, `- tell_`). |
| V4 | Claims are the teller's view | for every `tell` event, each listener's `told` view equals the claim the builder gives for (teller, listener) from the teller's door summary (string equality, recomputed in the reading script). |
| V5 | The guard holds | §7.3, P3. It is code-enforced, so a failure here is a bug, not a result. |

## Predictions (§7.3, word for word, as amended)

### Predictions (frozen before any live call)

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

## Live-ask budget (§7.4, as amended)

### Live-ask budget

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

## How the rules meet the code (fixed here, before any live call; no rule is changed)

The implementation (`reports/talk_impl.md`, commit 095931a) follows A3. Three rules name a field the amended code does
not have, or a format it writes another way. Each is read as follows; the reading script is
`runs/talk_probe/read_talk.py`.

1. **V4's "each listener's `told` view"**: A3 removed the `told` witness kind and put the claim in the listener's
   belief store. So V4 compares each listener's belief claim from a tell with `topics.claim(<teller's topic entry>,
   teller, listener, day)`, the builder, recomputed from the teller's entry as saved in `scene<k>.json`.
2. **P1's first clause, a `tell` event "whose `about` includes"**: the implemented `tell` event has no `about` field
   (the belief carries it). The first clause can never count by itself. A scene counts by the amended second clause:
   Daniel holds a belief whose `about` includes that scene's `door_end` event. The reading script also prints the
   tell events to Daniel.
3. **P5's "a line starting `Yesterday at`"**: block A's lines are written with a "- " bullet. The bullet is removed
   before the line is read.
4. **P4's denominator** is read from the recorded asks: each day-3 ask from 09:45 that is not a night mind, whose
   prompt lists at least one `- talk_` or `- tell_` option. "Chose one" means the answer's `option` is one of those
   offered.
5. **P6's "a teller who heard the line that named them"**: the teller is a witness of the visit's first `door_line`
   event (the line that names the children in scenes 3 and 4). The check is whether Daniel's claim contains "boy of
   six" (scene 3) or "girl and boy of five" (scene 4). A scene where Daniel is not told has nothing to count, and is
   NOT TESTED for P6.

## Order of work

1. `probe.py --fake` (V1): done before this plan was frozen. `runs/talk_probe/fake.stdout.txt`, exit 0, all three
   scenes `done`.
2. Record this plan's sha256, the probe's and the reading script's, the UTC time and HEAD (`plan_frozen.txt`).
3. `probe.py --live`.
4. `read_talk.py`. V2 to V5 first; if any fails, the report says which and stops there.
5. At the end: the hashes again, `git diff` empty, and a search for the key in every file.
