# Playing Leo, step S3 for days 1 and 2: the terminal, the play log, the cap and resume

Mode: implement, from `reports/play_design.md` §2.2, §5.3, §6.1, §8, C6 and §10 S3, on top of `reports/play_s1.md`.
It covers days 1 and 2 only, before S2 (quiet days), so that a person can play Leo now. No live call was made: every
run here used the fake model, with `GEMINI_API_KEY` cleared. Paths are relative to `Prototypes/llm-morning/`; raw
outputs are in `runs/play_s3/`.

## Result

- **C6 and the stdin test were seen failing** before `play.py` existed (§3), **and pass after** (§4).
- **The full suite passes:** 340 tests, OK (§5). After S1 it was 338.
- **§7 check 2 gives the same sha256 as `reports/play_s1.md`** for the fake run's story and transcript (§6).

## How to play live

From `Prototypes/llm-morning/`, with your key in the environment of that shell only (PowerShell):

```
$env:GEMINI_API_KEY = "<your key>"
.venv/Scripts/python.exe play.py --seed 2
```

What to know before you run it:
- **Requests:** a session sends at most 250 (`config.json` `play_max_requests`) and then stops with "stopped: this
  session's 250 requests are spent." Days 1 and 2 with their nights took about 72 asks of the others in v23 (§5.2 of
  the design), so a session should end well before that.
- **Stopping and resuming:** `q`, Ctrl-C or the end of input saves and stops. The command to go on is printed, for
  example `.venv/Scripts/python.exe play.py --resume runs/play/daniel_ate_it-seed2-<UTC time>`.
- **Waiting:** each answer of the others takes about 4.6 s (the 4.5 s gap between calls), shown as "…".
- **Days:** `--days 1` plays day 1 and its night only.
- **Which Python:** use `.venv/Scripts/python.exe`. The system Python has no `google` package, and a live session needs
  it (`reports/self_records.md`).
- **The cache is shared:** the others' answers go to `cache/play/gemini-3.5-flash-lite-daniel_ate_it-seed2.json`. A
  second session with the same seed reuses any answer to an identical prompt, so it starts as the first did until your
  choices differ. Another `--seed` gives other draws, and other first answers.
- **Play without the API:** `.venv/Scripts/python.exe play.py --seed 2 --fake`.

What to bring back is the session folder `runs/play/<name>/`:
- `play.jsonl`, the full log. It holds the others' feelings and reasons, and acts you did not perceive, so read it
  after playing, not during.
- `shown.md`, only what you were shown and what you typed.
- `session.log`.

With the cache, the folder replays with no request.

## 1. What was built

**`play.py` (new)**
- **`session(...)`** runs one session, new or resumed, on `player.play_days`:
  - `--days 1|2` (default 2), `--fake`, `--resume <folder>`, `--scenario`, `--model` and `--max-requests`. `--root`
    (hidden) sets where `runs/` and `cache/` are; it is for the tests.
  - A new session gets the folder `runs/play/<scenario>-seed<N>-<UTC time>/`, and its answers go to
    `cache/play/<model>-<scenario>-seed<N>.json`.
  - Exit codes: 0 done; 3 stopped part way (the cap, the quota, a rate limit, `q`, Ctrl-C, the end of input), and the
    session can be resumed; 1 the log and the game differ on resume.
- **The play log (§8)**, appended and flushed as play goes:
  - `play.jsonl` has records `start` (one per part: seed, days, scenario, model, cache, cap, choices replayed);
    `screen` (`n`, day, minute, kind, the exact text, the option ids); and `choice` (`n`, option or `w`, words, every
    line typed, seconds).
  - It also has `act`: every act of the others in the played turns, except a routine silence, with its feeling and
    reason and `seen_by_leo` (`saw`, `voices` or null). It is written at each screen for the turns completed since,
    and at each day's end.
  - It also has `night` (the others' night decisions), `night_event`, `mind` (the others' night minds) and `session`
    (per part: start, end, live and cached asks, API requests, `stopped`, and how far the acts and scenes are logged).
  - `shown.md` holds the screens and the typed lines only.
  - `session.log` holds what `play_days` says and each part's start and end.
- **The cap (§5.3).**
  - `Capped` wraps the client and refuses to send once `limit` requests have been sent. It raises
    `SessionCapReached`: "stopped: this session's N requests are spent."
  - A `GeminiClient` also checks it before each retry (`stop_at`, below), so retries count.
- **Resume (C6).**
  - `read_log` gives the first start record, the logged screens, the choices and what is logged already.
  - `SessionPlayer` replays each logged choice against its logged screen. A screen that differs stops the session
    with code 1. When the queue empties it records `replay_end = {"n", "live"}`, says "(replayed n screens from the
    log, k live asks; from here you play)", and from then on asks the live player.
  - A screen that was logged without a choice (where `q` was typed) is shown again and is not logged twice.
  - The others' acts and scenes logged in an earlier part are not written again: the `session` record keeps
    `acts_done` and `scenes_done`.
- **The terminal player (§6.1).**
  - It prints the screen and a hint (`w wait · l look · h help · q save and stop` on a turn, without `w` elsewhere),
    and reads one line:
    - a number picks an option;
    - a number then words picks it and says the words;
    - words alone are `say_other`, when it is offered;
    - `w` waits (on a turn only), `l` shows everything Leo remembers and knows, `h` shows the help, and `q` saves and
      stops.
  - §2.2's checks are made on the spot through `player.check`, and nothing happens until the answer can be used:
    - a number out of range;
    - a speech option without words, which asks "What do you say?";
    - `silent` with words;
    - words on a non-speech option at night;
    - `w` where there is nothing to wait for.
  - While the others' answers come, it prints "…".

**`player.py`**
- **The echo:** `Player.chose` keeps the words of the player's last act. The next screen shows Leo's own line of that
  act with them: `you accused Daniel, saying: "Was it you, Daniel?"`, and for free words `you said: "I heard someone
  at the shelf last night."`. On a screen, what Leo is sure of is now listed before the other lines of the same
  minute, so day 1's count comes first.
- **The hooks:** `play_days` takes `log` as a list or a function, and an `on_scene(name, scene)` called as each day,
  night and night mind ends.

**`world.py`:** `player_choice` calls `player.chose` once an answer is taken.

**`gemini.py`:** `SessionCapReached`, and `GeminiClient.stop_at` (None unless a session sets it), checked before every
attempt.

**`config.json`:** `"play_max_requests": 250`.

**With no player nothing changes.** `stop_at` is None unless `play.py` sets it, `play_max_requests` is read only by
`play.py`, and the player hooks are as in S1. The suite and §6 are the check.

**Not built here:**
- quiet days (S2) and the web page;
- the run's story, transcript and meta at a session's end (§8's last item);
- `--days` beyond 2.

## 2. The two new tests (`test_morning.PlayS3Test`)

**C6** (`test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask`). Three sessions of day 1, seed 1,
`--fake`. A live player speaks on every screen that has a (speech) option, and otherwise takes the first option.
1. **A reference session with no cap worth reaching** ends with code 0 and sends more than 21 requests.
2. **A session capped at 20:**
   - it ends with code 3, after exactly 20 requests;
   - its 20 prompts equal the reference's first 20;
   - `play.jsonl` ends with a `session` record whose `stopped` is `stopped: this session's 20 requests are spent.`,
     and that message was printed;
   - the screens are numbered 1 to n, and each has its choice.
3. **`--resume` of its folder:**
   - it ends with code 0 in the same folder;
   - `replay_end == {"n": <the last logged screen>, "live": 0}`, and the replayed last screen's text equals the logged
     one;
   - the first request it sends is the reference's 21st prompt;
   - `play.jsonl`, `shown.md` and `session.log` exist.

**The stdin test** (`test_play_py_on_scripted_stdin_reaches_night_1_bedtime`) runs
`python play.py --seed 2 --fake --root <temp>` as a subprocess. Its stdin is `2 Who took the can?` then 200 lines of
`1`; option 1 is `silent` on a turn, accept on an aside, and `sleep` at bedtime. The test asserts:
- no traceback on stderr;
- `── Night 1 · bedtime ──` on stdout;
- the echo `, saying: "Who took the can?"`;
- exit code 0: days 1 and 2 played to the end.

## 3. Failing, before `play.py`

```
$ .venv/Scripts/python.exe -m unittest test_morning.PlayS3Test.<test> > runs/play_s3/fail_<c6|stdin>.txt 2>&1      # exit 1 each
```

**C6** (`runs/play_s3/fail_c6.txt`):
```
E
======================================================================
ERROR: test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask (test_morning.PlayS3Test.test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8876, in test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask
    import play
ModuleNotFoundError: No module named 'play'

----------------------------------------------------------------------
Ran 1 test in 0.009s

FAILED (errors=1)
```

**The stdin test** (`runs/play_s3/fail_stdin.txt`):
```
F
======================================================================
FAIL: test_play_py_on_scripted_stdin_reaches_night_1_bedtime (test_morning.PlayS3Test.test_play_py_on_scripted_stdin_reaches_night_1_bedtime)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Akrem\Desktop\Projects\Fallow\Prototypes\llm-morning\test_morning.py", line 8918, in test_play_py_on_scripted_stdin_reaches_night_1_bedtime
    self.assertIn("── Night 1 · bedtime ──", r.stdout, r.stdout[-3000:] + r.stderr[-3000:])
AssertionError: '── Night 1 · bedtime ──' not found in '' : C:\Users\Akrem\AppData\Local\Programs\Python\Python312\python.exe: can't open file 'C:\\Users\\Akrem\\Desktop\\Projects\\Fallow\\Prototypes\\llm-morning\\play.py': [Errno 2] No such file or directory


----------------------------------------------------------------------
Ran 1 test in 0.150s

FAILED (failures=1)
```

## 4. Passing, after it

```
$ .venv/Scripts/python.exe -m unittest -v test_morning.PlayS3Test.<test> > runs/play_s3/pass_<c6|stdin>.txt 2>&1   # exit 0 each
```

**C6** (`runs/play_s3/pass_c6.txt`):
```
test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask (test_morning.PlayS3Test.test_c6_the_session_cap_stops_cleanly_and_resumes_with_no_live_ask) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.383s

OK
```

**The stdin test** (`runs/play_s3/pass_stdin.txt`):
```
test_play_py_on_scripted_stdin_reaches_night_1_bedtime (test_morning.PlayS3Test.test_play_py_on_scripted_stdin_reaches_night_1_bedtime) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.093s

OK
```

The S1 tests still pass with these changes, and the S3 tests raise no `ResourceWarning`:
```
$ .venv/Scripts/python.exe -W error::ResourceWarning -m unittest test_morning.PlayS3Test test_morning.PlayerS1Test
Ran 9 tests in 5.061s

OK
```

## 5. The suite

```
$ .venv/Scripts/python.exe -m unittest test_morning > runs/play_s3/suite.stdout.txt 2>&1
Ran 340 tests in 362.416s
OK
```
As before, the run prints the four `[429 RESOURCE_EXHAUSTED] waiting …` lines of the stubbed API (`StubApi`); they are
not requests.

## 6. §7 check 2

```
$ .venv/Scripts/python.exe morning.py --seed 1 --fake --days 4 --out play_check_s3 > runs/play_s3/check.stdout.txt 2>&1   # exit 0
$ sha256sum runs/play_check_s3/fake/daniel_ate_it-seed1.md runs/play_check_s3/fake/daniel_ate_it-seed1.transcript.json
949bd5abf01b5d2bc66e65456360d88b7d4f1fc4cd6d866b51b09de3f13286ad *runs/play_check_s3/fake/daniel_ate_it-seed1.md
7d20b51864a1e39c0b563f57442e0948ffb7acf655e27cac061f9a934b50df68 *runs/play_check_s3/fake/daniel_ate_it-seed1.transcript.json
```
These are `reports/play_s1.md` §6's two values at HEAD `319937d` before S1, and after it:
`949bd5ab…13286ad` and `7d20b518…50df68`.

## 7. Played by hand, against the fake model

Three short sessions through stdin, into the session's scratchpad. They are how the two wording faults below were
found, and how the duplicated acts on resume were found.

**Session 1.** The input was `h`, then `3` (accuse Daniel, no words), then `Was it you, Daniel?`, then `99`, then
`I heard someone at the shelf last night.`, then `w`, then `q`. Exit 3. This is the run with the fixes in
(`scratchpad/try4`). What was printed, cut to the parts that matter:
```
> How to play … (the help)
> What do you say? …
── Day 1 · minute 03 · the kitchen ──
Since you last chose:
  min 00  you accused Daniel, saying: "Was it you, Daniel?"
  min 03  Daniel leaves for the back room.
…
> ! Choose a number from 1 to 13.
> …
── Day 1 · minute 06 · the kitchen ──
Since you last chose:
  min 03  you said: "I heard someone at the shelf last night."
  min 06  Elena starts going through the kitchen.
…
> (w)
── Day 1 · minute 09 · the kitchen ──
Since you last chose:
  min 06  Daniel comes into the kitchen.
…
stopped: you chose to stop.
The session is saved in …/scratchpad/try4/runs/play/daniel_ate_it-seed2-<UTC time>
To go on: python play.py --resume …
```
- The wait at minute 06 lasted one turn, because Daniel came into the kitchen: something reached Leo.
- The same input before the two wording fixes (`scratchpad/try1`) had printed `you said, saying: "…"`, and had listed
  day 1's count after the others' minute-00 acts. Both are fixed (§1, `player.py`).

**Session 2: resume** of a session (`scratchpad/try2`: `l`, `3`, `Was it you, Daniel?`, free words, then `q` at
screen 3). The input was `1`, then `q`:
```
Resuming …: replaying 2 choices…
(replayed 2 screens from the log, 0 live asks; from here you play)
── Day 1 · minute 06 · the kitchen ──
```
Screen 3, at which `q` had been typed, is shown again live and is not logged twice.

**Session 3.** A new session, then a resume. Before the fix in §1, its log held the others' early acts twice. After it:
```
acts 11 distinct 11 | screens [1, 2, 3, 4, 5] | choices [1, 2, 3, 4]
[(1, {'4': 2}, 'stopped: you chose to stop.'), (2, {'4': 4}, 'stopped: you chose to stop.')]
```

## 8. The diff, before the commit

```
$ git diff --stat
 Prototypes/llm-morning/config.json     |  1 +
 Prototypes/llm-morning/gemini.py       |  7 ++++
 Prototypes/llm-morning/player.py       | 34 ++++++++++++++----
 Prototypes/llm-morning/test_morning.py | 66 ++++++++++++++++++++++++++++++++++
 Prototypes/llm-morning/world.py        |  1 +
 5 files changed, 103 insertions(+), 6 deletions(-)
```
`play.py` is new (392 lines).
