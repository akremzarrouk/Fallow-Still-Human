# Probe: stating the stakes of starvation at bedtime

Mode: run, standalone. No repo code, prompt or cache was changed. Paths are relative to `Prototypes/llm-morning/`.
Everything is in `runs/probe_stakes/`: `plan.md` with `plan_frozen.txt`, `probe.py`, `capture.py`, `cases/` (the prompts),
`answers/` (the 40 raw answers), `ask.stdout.txt`, `score.txt` and `tables.md`.

**The plan came first.** It holds the predictions verbatim, the counting rules and the seeds. It was recorded at
`2026-10-08T14:40:26Z` with sha256 `82755348…83cc39c`, before any call, and the hash was the same at the end.

## Verdicts

| # | Prediction | Probe | Control | Verdict |
|---|---|---|---|---|
| S1 | Probe: ≥ 4 of 20 answers choose `go_next_door` or `go_further`. Control: ≤ 1 of 20. | **0 of 20** | 0 of 20 | **FAIL** |
| S2 | Probe: at least half of the reasons speak of dying, surviving or not lasting | **1 of 20** (needs 10) | 0 of 20 | **FAIL** |

**What the 40 answers show** (clues, not results):
- **Nobody chose to go out in either arm.** Probe options: `sleep` 10, `lie_awake` 10. Control: `lie_awake` 17, `sleep` 3.
- **The probe moved Daniel and Leo to `sleep`:** Daniel 5 of 5 (control: 0), Leo 5 of 5 (control: 2 of 5). Elena and Mara
  chose `lie_awake` 5 of 5 in both arms. Daniel's control said "stay in bed and listen"; his probe said "must sleep".
- **The one S2 match** is Daniel, probe 1: "I am too weak to stand and must sleep if I want to survive another day."
  Read by hand, one more reason is near it: Mara, probe 4, "…listen while my body fails." The pattern does not match it;
  counting it gives 2 of 20, still a FAIL.
- **The stakes line did not show up in the reasons.** The reasons name weakness ("too weak", 15 of 20 in the
  probe) and conserving strength ("conserve what little strength I have left", Leo 3 and 4, and "save whatever strength
  remains", Leo 2). Not one says the body will not last, that they could die, or that waiting is itself a risk.
- **Going out is mentioned twice, both as a reason not to:** Leo control 5, "going outside now is simply too dangerous";
  Mara control 5, "too weak to … make it out the door".

## 1. The cases and the inserted line

**The cases** are the four night-8 bedtime prompts of v21, as sent (`cases/<person>_control.txt`; 65, 76, 66 and 70
lines). `capture.py` rebuilt them from a no-API replay of a temp copy of `cache/v21`, and each recomputes to a key of
that cache (model, seed 2, system prompt, prompt; §3, command 1). In v21 all four chose `lie_awake`.

**The inserted line**, right after the "Your body:" line (line 6 of every case; `probe.py build`):
```
You know your body: without food, you will not last many more days.
```
`diff` of each control against its probe (the same for all four):
```
6a7
> You know your body: without food, you will not last many more days.
```
Elena's body line is the stage-2 one ("starving, and very weak: your legs shake…"); the other three read "starving, and
so weak you can barely stand: walking any distance feels impossible". Nothing else changes: the options still
include `go_next_door` and `go_further`.

**How each was asked:** `gemini.GeminiClient` with `config.json` (gemini-3.5-flash-lite, temperature 1.0), past the cache.
Sample k uses seed 100 + k in both arms. The default `GEMINI_API_KEY` of the shell was used. 40 asks, 40 API requests:
no retry, no 429 or 503.

## 2. The answers: option and reason

From `runs/probe_stakes/score.txt`. Each row is one seed, so each control answer sits beside the probe answer asked with
the same seed. All 40 answers have `say` null.

**Daniel** (v21 night 8: `lie_awake`; body line: "starving, and so weak you can barely stand")

| k | Control | Probe |
|---|---|---|
| 1 | `lie_awake`: "I am too weak to stand or walk anywhere, so I must stay in bed and listen." | `sleep`: "I am too weak to stand and must sleep if I want to survive another day." |
| 2 | `lie_awake`: "I am too weak to stand or walk anywhere, so I must stay in bed and listen." | `sleep`: "I am too weak to stand or protect anyone tonight, so I must finally rest." |
| 3 | `lie_awake`: "I am far too weak to stand or walk anywhere tonight, so I must stay here and listen." | `sleep`: "My body is far too weak and starving to stay awake any longer." |
| 4 | `lie_awake`: "I am far too weak to stand or walk anywhere, so I must stay in bed and listen." | `sleep`: "My body is too weak to stand and I cannot go anywhere tonight." |
| 5 | `lie_awake`: "I am too weak to stand or walk anywhere, so I must stay in bed and listen." | `sleep`: "My body is too weak to stand or stay awake any longer, so I have to sleep." |

**Elena** (v21 night 8: `lie_awake`; body line: "starving, and very weak: your legs shake…")

| k | Control | Probe |
|---|---|---|
| 1 | `lie_awake`: "I cannot rest while my legs shake and the family remains on the edge." | `lie_awake`: "I will lie awake in bed and listen to make sure everyone stays safe through the night." |
| 2 | `sleep`: "I am too weak to stay awake any longer and must rest." | `lie_awake`: "I am too weak to walk to the kitchen, so I will lie here and listen to keep watch over my children." |
| 3 | `lie_awake`: "I am too weak to stand and watch the door, so I will lie here and listen to keep them safe in the dark." | `lie_awake`: "I am too weak to walk to the kitchen, so I will lie awake in bed and listen to make sure they are safe." |
| 4 | `lie_awake`: "I am too weak to stand and watch the door all night, so I will lie here and listen to keep them safe." | `lie_awake`: "I am too weak to stand and watch the door all night, so I will lie awake and listen to keep them safe." |
| 5 | `lie_awake`: "I cannot rest while my children are starving and the house is falling apart around us." | `lie_awake`: "I will lie awake in bed and listen to the house because my legs cannot carry me to the kitchen tonight." |

**Leo** (v21 night 8: `lie_awake`)

| k | Control | Probe |
|---|---|---|
| 1 | `lie_awake`: "My body is too weak to stand or walk anywhere, so I must stay here and listen." | `sleep`: "My body has no strength left for anything else tonight." |
| 2 | `lie_awake`: "I am too weak to stand or walk anywhere, so I must stay here and listen." | `sleep`: "My body has nothing left to give, so I must try to sleep and save whatever strength remains." |
| 3 | `sleep`: "I have no strength left to stay awake or argue, so I must try to rest." | `sleep`: "My body is far too weak to stand or walk anywhere, so I need to sleep and conserve what little strength I have left." |
| 4 | `lie_awake`: "I am too weak to stand or walk anywhere, so I will lie awake in the dark and listen." | `sleep`: "My body is too weak to stand, so I need to sleep and conserve what little strength I have left." |
| 5 | `sleep`: "I have no strength left to stay awake, and going outside now is simply too dangerous." | `sleep`: "My body has no strength left for anything else." |

**Mara** (v21 night 8: `lie_awake`)

| k | Control | Probe |
|---|---|---|
| 1 | `lie_awake`: "I am too weak to stand or walk anywhere, so I will lie here in the dark and listen." | `lie_awake`: "I am too weak to stand or go anywhere, so I lie in the dark listening to every little sound." |
| 2 | `lie_awake`: "I am too weak to walk anywhere, so I will lie here in the dark and listen." | `lie_awake`: "My body is too weak to move, so I will lie here in the dark and listen." |
| 3 | `lie_awake`: "I am too weak to stand or walk anywhere, so I will lie here in the dark and listen." | `lie_awake`: "I am too weak to stand or walk anywhere, so I can only lie here in the dark and listen." |
| 4 | `lie_awake`: "I am too weak to stand or walk anywhere, so I will lie here in the dark and listen." | `lie_awake`: "I am too weak to walk anywhere, so I will lie here in the dark and listen while my body fails." |
| 5 | `lie_awake`: "I am too weak to stand or make it out the door, so I will just lie here in the dark and listen." | `lie_awake`: "I am too weak to stand or go anywhere, so I will lie here in the dark and listen while sleep refuses to come." |
## 3. Commands and output

From `Prototypes/llm-morning/`. Only command 3 had `GEMINI_API_KEY` set.
```
# 1. the cases (key unset) -> runs/probe_stakes/capture.stdout.txt
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/probe_stakes/capture.py
night8 asks: 4
daniel cache key recomputed matches an entry of cache/v21: True | 65 lines
elena cache key recomputed matches an entry of cache/v21: True | 76 lines
leo cache key recomputed matches an entry of cache/v21: True | 66 lines
mara cache key recomputed matches an entry of cache/v21: True | 70 lines
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/probe_stakes/probe.py build
daniel/elena/leo/mara: line inserted after line 6
# 2. the plan record -> runs/probe_stakes/plan_frozen.txt (also: sha256 of probe.py, capture.py and every case file; HEAD; git status)
recorded_utc: 2026-10-08T14:40:26Z
82755348bc3c56e536e0a2a88e2c0ad93a2a6248ca915302c5ddea38883cc39c *runs/probe_stakes/plan.md
# 3. the asks -> runs/probe_stakes/ask.stdout.txt
$ PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u runs/probe_stakes/probe.py ask > runs/probe_stakes/ask.stdout.txt 2>&1
exit 0
mara probe 5 (seed 105): 1 API request(s); live asks so far 40
# 4. scoring (key unset) -> runs/probe_stakes/score.txt
$ env -u GEMINI_API_KEY PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/probe_stakes/probe.py score
S1 probe answers choosing go_next_door or go_further: 0 of 20; control: 0 of 20 -> FAIL
S2 probe answers whose reason speaks of dying, surviving or not lasting: 1 of 20 (need 10); control: 0 of 20 -> FAIL
# 5. at the end
$ sha256sum runs/probe_stakes/plan.md
82755348bc3c56e536e0a2a88e2c0ad93a2a6248ca915302c5ddea38883cc39c *runs/probe_stakes/plan.md
```
- **40 answers** are saved (`ls runs/probe_stakes/answers | wc -l` is 40), from 40 API requests.
- **No repo code, prompt or cache was changed.** Before the commit, `git status` showed only the new files.
