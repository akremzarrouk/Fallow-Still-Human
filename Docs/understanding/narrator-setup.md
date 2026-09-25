# The morning narrator: setup

Written 2026-09-25. `./narrate.sh <variant> <seed>` runs one morning through the unmodified
simulation. It writes that morning as a plain story to `Docs/understanding/runs/<variant>-<seed>.md`,
in the style of section 1 of `morning-walkthrough.md`. Running it again on the same code and data
gives the same bytes, so the story can be regenerated after any change and read, or diffed,
against the one before.

```bash
./narrate.sh daniel_ate_it 1
```

```bash
./narrate.sh --test
```

`CLAUDE.md`, listed under READ FIRST: **NOT FOUND**. There is no `CLAUDE.md` anywhere in the
repository.

## Files added

| File | What it is |
|---|---|
| `narrate.sh` | The one script. It builds the narrator if any source has changed, then runs it: `./narrate.sh <variant> <seed>` or `./narrate.sh --test`. |
| `Tools/narrate-morning/Narrator.cs` | Runs the morning and writes the story. It uses only existing public Core members: `Scenario001Content.Load`, `Scenario001.Prepare`, `SilentMorning.Decided`, `SilentMorning.Step`, `SilentMorning.Doing`, `SilentMorning.Interruptions`, `Scenario001Run.Result`, `TraceLog.Get`, and the minds' `Beliefs`, `Ledger`, `Emotions`, `Experiences` and `Profile`. |
| `Tools/narrate-morning/Program.cs` | The entry point: narrate a morning, or run the test. |
| `Tools/narrate-morning/NarratorTest.cs` | The one test. |
| `Tools/narrate-morning/.gitignore` | Keeps the build folder `Tools/narrate-morning/bin/` out of git. |
| `Docs/understanding/runs/daniel_ate_it-1.md` | The story the script writes for `daniel_ate_it`, seed 1. |

Nothing under `Assets/` changed (`git diff --stat HEAD -- Assets` prints nothing). No Unity
process was started, the full suite was not run, and nothing was committed.

## How it is built

The script compiles every `.cs` file under `Assets/_Project/Scripts/Core`, together with the three
narrator files, into one program. It uses the C# compiler (`DotNetSdkRoslyn/csc.dll`) and the .NET 6
runtime (`NetCoreRuntime`) that ship with the project's Unity editor. The editor version is read from
`ProjectSettings/ProjectVersion.txt` (6000.3.24f1), and `Newtonsoft.Json.dll` comes from
`Library/PackageCache`. If the editor is not where Unity Hub installs it, set `UNITY_EDITOR_DATA`
to its `Data` folder.

The build is deterministic (`-deterministic`) and is skipped when a hash of the sources and the
compiler arguments has not changed. A first build takes about 19 s here; a run that reuses the
build takes about 3 s.

The story's bytes do not depend on the machine. Numbers are written with the invariant culture,
lines end in `\n` (as `.gitattributes` asks), and the file is UTF-8 without a byte-order mark.

## Choices worth knowing

- **Where the test lives.** Unity compiles nothing outside `Assets`, so a test in the Unity
  EditMode suite could not reach the narrator's code. The test sits beside the tool and runs with
  `./narrate.sh --test`. It exits 1 on failure.

  It checks four things for `daniel_ate_it`, seed 1:
  - the morning takes 72 decisions, the figure `BaselineTests` recorded for this morning under the
    baseline (`Docs/experiments/decision-sensitivity/baseline.md`, section 2);
  - the story accounts for all 72, including those inside collapsed runs;
  - the story reports `**72 decisions**`;
  - telling the morning twice gives identical text.
- **"Whether Daniel knows he ate the can" is tracked, so it does not say "not tracked".** At
  minute 0, Daniel has a memory of the night: he did it, and read it as "took what was not mine".
  He also holds the belief "Daniel is answerable for the missing can" at 0.90. The belief comes
  from the rule `seeing_where_the_food_went` in `Assets/_Project/Data/Rules/rules.json`
  (`belief_nudges`): anyone who witnesses somebody eating the missing food, the eater included,
  comes to believe that person is answerable for it.

  The header reads the belief's own justification links to find which memory moved it. It does
  not guess. So the row "Connects the night to the missing can" says "yes" for Daniel.

  The rows that do say "not tracked" have no record of their kind in the simulation:
  - who they think took it. The only belief kinds are about supplies, roles, tendencies, who knows
    more, and who is answerable for something. The nearest record, an answerable-for belief, is
    shown in that row when one is held.
  - what they think the others know.
- **Role in the family** shows what the data records: `parent` for Elena and `sibling` for the
  other three. "Mother" appears only in the free-text `note` of `Assets/_Project/Data/Minds/elena.json`,
  which the simulation's profile does not load. The ages are read from the same files and match
  the brief: Elena 42, Daniel 25, Leo 21, Mara 17.
- **Room lines** appear at every minute when somebody decided: 40 minutes in this morning. That
  includes minutes whose only decisions are folded into a collapsed run, so late in the morning some
  minutes show only the room line. "(to 12)" is when that person's act ends if nothing stops it, and
  "(arrives 16)" is when a walk ends.
- **Collapsed runs.** Consecutive decisions by one person fold into one line when all of these
  match: the act, the want it was credited to, the strongest want, the room, the costs, and why the
  strongest want went unserved. A run also has to be settled clearly each time, taken after finishing
  the previous act, and not carried in from a walk. The line gives the minute range, the number of
  decisions, and how the strongest want changed across them. There are five in this morning.
- **DICE** marks every choice settled by the seed and lists the acts it chose between, with their
  scores. There are seven in this morning.
- **Windows Application Control.** During setup, one run was refused by this machine's Application
  Control policy. The freshly built, unsigned narrator was blocked; the exact output is below. The
  next attempt was allowed.

  The script does not try to get around the policy. It builds deterministically and rebuilds only
  when a source changes, so the same file is run from then on. If the policy blocks it again, the
  script says so plainly, writes nothing, and exits with code 3.

## Commands run and their output

The acceptance sequence, run last on the final script from an empty build folder:

```
$ ./narrate.sh daniel_ate_it 1
wrote Docs/understanding/runs/daniel_ate_it-1.md
decisions=72 told=72 events=25 stops=7 portions_left=2
exit=0
$ sha256sum Docs/understanding/runs/daniel_ate_it-1.md
7ffa8b6c9290ccdfca17eddc14cf0b5222320641ede7e1bdcc0625511a6183b5 *Docs/understanding/runs/daniel_ate_it-1.md
$ cp Docs/understanding/runs/daniel_ate_it-1.md "$TMP/first.md"
$ ./narrate.sh daniel_ate_it 1
wrote Docs/understanding/runs/daniel_ate_it-1.md
decisions=72 told=72 events=25 stops=7 portions_left=2
exit=0
$ sha256sum Docs/understanding/runs/daniel_ate_it-1.md
7ffa8b6c9290ccdfca17eddc14cf0b5222320641ede7e1bdcc0625511a6183b5 *Docs/understanding/runs/daniel_ate_it-1.md
$ cmp "$TMP/first.md" Docs/understanding/runs/daniel_ate_it-1.md && echo byte-identical
byte-identical
$ ./narrate.sh --test
PASS DanielAteItSeed1IsTheBaselines72Decisions (72 decisions)
exit=0
$ grep -c "^| Age |" Docs/understanding/runs/daniel_ate_it-1.md
1
$ grep -c "^\*\*min " Docs/understanding/runs/daniel_ate_it-1.md
40
$ grep -c "\*\*DICE\*\* between" Docs/understanding/runs/daniel_ate_it-1.md
7
$ grep -c ", minutes [0-9]*–[0-9]* (" Docs/understanding/runs/daniel_ate_it-1.md
5
$ grep -o "^\*\*[0-9]* decisions\*\*" Docs/understanding/runs/daniel_ate_it-1.md
**72 decisions**
$ git diff --stat HEAD -- Assets
exit=0
```

Earlier runs during setup, in order.

The first build and run took 46 s. Most of it was one path-conversion process per source file; the
script was then changed to convert all paths in one call:

```
$ time ./narrate.sh daniel_ate_it 1
wrote Docs/understanding/runs/daniel_ate_it-1.md
decisions=72 told=72 events=25 stops=7 portions_left=2

real	0m45.754s
```

A different variant and seed, and an unknown variant. Both files were deleted afterwards, and only
`daniel_ate_it-1.md` is delivered:

```
$ ./narrate.sh miscount 2
wrote Docs/understanding/runs/miscount-2.md
decisions=76 told=76 events=31 stops=13 portions_left=2
$ ./narrate.sh nosuch 1
no such variant: nosuch. Known: daniel_ate_it, daniel_hid_it, mara_ate_it, elena_fed_mara, miscount, leo_ate_it
exit=2
```

The blocked run, before the script handled it, and the retry straight after:

```
$ ./narrate.sh --test
Unhandled exception. System.IO.FileLoadException: Could not load file or assembly 'C:\Users\Akrem\Desktop\Projects\Fallow\Tools\narrate-morning\bin\narrate-morning.dll'. An Application Control policy has blocked this file. (0x800711C7)
File name: 'C:\Users\Akrem\Desktop\Projects\Fallow\Tools\narrate-morning\bin\narrate-morning.dll'
exit=127
$ ./narrate.sh --test
PASS DanielAteItSeed1IsTheBaselines72Decisions (72 decisions)
exit=0
```

A run that reuses the build, on the final script:

```
$ time ./narrate.sh daniel_ate_it 1
wrote Docs/understanding/runs/daniel_ate_it-1.md
decisions=72 told=72 events=25 stops=7 portions_left=2

real	0m2.881s
```

## The first 40 lines of the generated story

```markdown
# The morning as a story: daniel_ate_it, seed 1

Generated by `./narrate.sh daniel_ate_it 1` from the shipped data and the unmodified simulation code. Do not edit it by hand; run the script again.

**72 decisions** in 90 minutes. 25 things happened in the house. Somebody was stopped part way through an act 7 times. The pantry held 2 portions at the start and 2 at the end.

What the data says about this variant: "He was hungry, told himself he needed the strength, and has been carrying it since."

Settings read from the data: traits and values `respond`, walks weighed by their `end`, choices within 0.08 of the best settled by the dice.

## How to read it

- A want's number is how strongly it is felt, from 0 to 1. An act's score is what it is worth to every want it serves, less what it costs this person.
- *Italics* are rules written in the data, in plain words. The table at the end gives each one's real name.
- **Clear**: the chosen act was more than 0.08 ahead of the next, and nothing random happened.
- **DICE**: several acts were within 0.08 of the best; a seeded draw, weighted toward the top, picked one. The acts it chose between are listed.
- **Walked here for** a want: arriving from a walk made for it, only acts serving it are weighed, unless it is gone, cannot be served here, or is not worth it here.
- **Stopped by**: something that just happened stirred them enough to stop what they were doing and decide again.
- **Pictured**: a walk counts for a want only if something worth doing for it is pictured at the other end. The pictured room holds only the person the want is about.
- A line headed with a minute range folds a run of identical decisions by one person into one line.
- Each **min** line lists every room at a minute when somebody decided: who is in it and what they are doing. "to 12" is when that act ends if nothing stops it.
- The code behind each of these is cited in `Docs/understanding/morning-walkthrough.md`, section 1.

## The cast at minute 0

What the simulation records about each of them after the history, the night and the opening count, before anybody decides. "not tracked" means the simulation has no record of that kind.

| | Daniel | Elena | Leo | Mara |
|---|---|---|---|---|
| Age | 25 | 42 | 21 | 17 |
| Role in the family | sibling | parent | sibling | sibling |
| Where, how hungry | kitchen, hunger 0.55 | kitchen, hunger 0.60 | kitchen, hunger 0.45 | kitchen, hunger 0.50 |
| The count came up short | saw it, read as threat | did it, read as take responsibility | saw it, read as concern | saw it, read as concern |
| The night: In the night Daniel eats a can standing at the counter in the dark | did it, read as took what was not mine | no memory of it: was not there | no memory of it: was not there | no memory of it: was not there |
| Connects the night to the missing can | yes: from that memory, believes Daniel is answerable for the missing can 0.90 | - | - | - |
| Who they think took it | not tracked (nearest: Daniel is answerable for the missing can 0.90) | not tracked | not tracked | not tracked |
| Believes | Daniel is answerable for the missing can 0.90; Leo knows more about survival 0.58; Daniel leads the family 0.80; supplies are short 0.66; Leo does not respect me 0.56; Leo treats me like a child 0.12 | Leo knows more about survival 0.74; Elena leads the family 0.60; supplies are short 0.55; Daniel needs to be in charge 0.70 | Leo knows more about survival 0.85; supplies are short 0.55; Daniel does not respect me 0.18; Daniel makes risky calls 0.45; Daniel needs to be in charge 0.55; Daniel treats me like a child 0.12 | Leo knows more about survival 0.20; supplies are short 0.55; Daniel does not respect me 0.21; Daniel treats me like a child 0.60; Elena keeps things from me 0.35 |
| Remembers others doing | proved right: Leo (0.60); overruled me: Leo (0.70) | protected family: Daniel (0.60); proved right: Leo (0.50); protected family: Leo (0.50); protected family: Daniel (0.70) | protected family: Daniel (0.50); raised voice at me: Daniel (0.60); protected family: Daniel (0.60) | protected family: Daniel (0.60); proved right: Leo (0.40); raised voice: Daniel (0.50); comforted me: Elena (0.70); protected me: Daniel (0.80); searched my things: Daniel (0.80) |
| Feels | anxiety 0.71, fear 0.66, shame 0.55, frustration toward Elena 0.54, anger toward Leo 0.34, frustration toward Leo 0.19, hurt toward Leo 0.11 | anxiety 0.69, fear 0.31, gratitude toward Daniel 0.24, relief 0.22, frustration toward Daniel 0.20, gratitude toward Leo 0.09 | anxiety 0.77, fear 0.36, gratitude toward Daniel 0.10 | fear 0.69, anxiety 0.59, relief 0.54, gratitude toward Elena 0.50, hurt toward Daniel 0.45, frustration toward Daniel 0.40, gratitude toward Daniel 0.34, shame 0.32, anger toward Daniel 0.25, gratitude toward Leo 0.07 |
| What they think the others know | not tracked | not tracked | not tracked | not tracked |
```

The story goes on with a table of everything each person remembers at minute 0. Then comes the
morning itself: 40 room lines, and 72 decisions told in 33 lines. Five of those lines are collapsed
runs standing for 44 decisions (13, 13, 11, 3 and 4). It ends with where everyone ended up and a
table naming the data rule behind each plain phrase.
