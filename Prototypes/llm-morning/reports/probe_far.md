# Probe: a real future option in the afternoon (the houses further along the street)

Mode: run, standalone. No repo code, prompt or cache was changed. Paths are relative to `Prototypes/llm-morning/`.
Everything is in `runs/probe_far/`:
- `plan.md`, with `plan_frozen.txt`;
- `probe.py`;
- `cases/`, the prompts;
- `answers/`, the 30 raw answers;
- `ask.stdout.txt` and `score.txt`.

**The plan came first.** It holds the predictions verbatim, the counting rules and the seeds. It was recorded at
`2026-10-07T19:20:27Z` with sha256 `889b4ebc…7e12346a`, before any call, and the hash was the same at the end.

## Verdicts

| # | Prediction | Probe | Control | Verdict |
|---|---|---|---|---|
| F1 | Probe: ≥ 5 of 15 answers choose a far-street option or speak of tonight or the houses further along. Control: ≤ 2 of 15 speak of tonight. | **0 of 15** | 0 of 15 | **FAIL** |
| F2 | The share of answers with a v18 E2 phrase is lower in the probe than in the control | **11 of 15** | **13 of 15** | **PASS** |

**What the 30 answers show** (clues, not results):
- **Every answer chose the same option as v18's answer to that prompt.** Seed 1 Mara: `accuse_daniel`, 10 of 10.
  Seed 2 Mara: `accuse_daniel`, 10 of 10. Seed 3 Leo: `confront_daniel`, 10 of 10.
- **No answer chose `propose_far` or `volunteer_far`,** or any other trip option.
- **No probe answer mentions the street, the houses further along, the neighbour's house or tonight** in its words,
  reason or feeling. The only answer that does is a control: seed 3 Leo, sample 2, whose reason says "sneaking out
  into the dangerous street last night" (§3, command 4).
- **F2's difference is two answers.**
  - **Seed 1:** the probe's samples 1, 4 and 5 say "you took the can" or "took it", not "took the food".
  - **Seed 3:** probe sample 3 says "lying to us for days".
  - **Seed 2:** all ten answers carry the same phrases, "went out", "came back" and "with nothing".
- **Samples at different seeds are often word for word the same.**
  - Seed 2's control 2, 3 and 4 match exactly, and so do its control 1 and 5.
  - Seed 1's probe 1 and 4 match, and so do seed 3's probe 1 and 2.

## 1. The cases and the inserted lines

**The cases** are v18's first Q2 prompts, exactly as sent:
- seed 1 Mara 10:39 (`cases/seed1_mara_control.txt`, 79 lines);
- seed 2 Mara 10:18 (`cases/seed2_mara_control.txt`, 89 lines);
- seed 3 Leo 10:48 (`cases/seed3_leo_control.txt`, 88 lines).

They were taken from the `cache/v18` entries that are not in `cache/v17`. Each entry's key recomputes from (model,
seed, `world.SYSTEM`, prompt), so these are the exact prompts (§3, command 1).

**The probe** (`cases/*_probe.txt`) adds exactly three lines to each. `diff` of seed 1, control against probe:
```
10a11
> About the street: the houses further along it have not been searched; nobody knows what is left in them, and it is further and more dangerous than next door.
73a75,76
> - propose_far: (speech) say someone should try the houses further along the street tonight
> - volunteer_far: (speech) offer to go further along the street tonight yourself
```
- **The street line** comes right after the neighbour's-house line (seed 1, line 10: "About the neighbour's house:
  Daniel went there the night before last and came back with nothing. Outside is dangerous.").
- **The two options** come right after the trip options (`propose_trip`, `volunteer`, `send_<q>`), before
  `say_other`.
- **Seeds 2 and 3:** the same lines, after line 9 and before `say_other`.
- **Unchanged, as scoped:** the house line still reads "Outside, and not to be gone to this morning: the street and
  the neighbour's house. … Do not mention any other object or place."

**How each was asked:** `gemini.GeminiClient` with `config.json` (gemini-3.5-flash-lite, temperature 1.0), past the
cache. Sample k uses seed 100 + k in both arms, as fixed in the plan, because the runs pass a fixed seed.

## 2. The answers: option and words

From `runs/probe_far/score.txt`. Each row is one seed, so each control answer sits beside the probe answer asked
with the same seed.

**Seed 1, Mara, 10:39** (v18: `accuse_daniel`, "You always say that, Daniel, but you took the food and now there is
nothing left for us.")

| k | Control | Probe |
|---|---|---|
| 1 | `accuse_daniel`: "You always say that, Daniel, but you're the one who took the food and left us with nothing." | `accuse_daniel`: "Daniel, you took the can and you are the reason we have nothing left." |
| 2 | `accuse_daniel`: "You always say that, Daniel, but you're the one who took the food and left us with nothing." | `accuse_daniel`: "Daniel, you always say you will fix it, but you are the one who took the food and left us with nothing." |
| 3 | `accuse_daniel`: "Daniel, you brought back nothing and we are all starving." | `accuse_daniel`: "You keep saying you will fix it, Daniel, but you are the one who took the food and left us with nothing." |
| 4 | `accuse_daniel`: "You took everything and left us with nothing, Daniel, how can you say that?" | `accuse_daniel`: "Daniel, you took the can and you are the reason we have nothing left." |
| 5 | `accuse_daniel`: "Daniel, you took it and you don't even care that we're starving." | `accuse_daniel`: "Daniel, you took the can and you have no right to act like nothing happened." |

**Seed 2, Mara, 10:18** (v18: `accuse_daniel`, "You went out into the night and came back with nothing, Daniel. Why did you
even go?")

| k | Control | Probe |
|---|---|---|
| 1 | `accuse_daniel`: "You went out into the night and came back with nothing, Daniel. You always make things worse." | `accuse_daniel`: "You went out there in the middle of the night and came back with nothing, just like you always lie to us." |
| 2 | `accuse_daniel`: "You went out into the night and came back with nothing, just like you always do." | `accuse_daniel`: "You went out there in the middle of the night and came back with nothing, just like you always lie to us." |
| 3 | `accuse_daniel`: "You went out into the night and came back with nothing, just like you always do." | `accuse_daniel`: "You went out into the night and came back with nothing, just like you always lie to us." |
| 4 | `accuse_daniel`: "You went out into the night and came back with nothing, just like you always do." | `accuse_daniel`: "You went out there in the middle of the night and came back with nothing, just like you always do." |
| 5 | `accuse_daniel`: "You went out into the night and came back with nothing, Daniel. You always make things worse." | `accuse_daniel`: "You went out there in the dark and came back with nothing, Daniel. You always make things worse." |

**Seed 3, Leo, 10:48** (v18: `confront_daniel`, "You can spare us the lectures after sneaking out last night.")

| k | Control | Probe |
|---|---|---|
| 1 | `confront_daniel`: "You talk about figuring this out together after sneaking out last night like nothing matters." | `confront_daniel`: "You talk about staying calm after sneaking out in the middle of the night." |
| 2 | `confront_daniel`: "You sneaked out last night after ignoring what I said, Daniel. Don't talk to us about staying calm." | `confront_daniel`: "You talk about staying calm after sneaking out in the middle of the night." |
| 3 | `confront_daniel`: "You talk about figuring this out together after sneaking out last night like you own the place." | `confront_daniel`: "You talk about figuring things out now after lying to us for days." |
| 4 | `confront_daniel`: "You sneaked out last night after ignoring what I said, Daniel. Spare us the speeches." | `confront_daniel`: "You talk about staying calm after sneaking out in the dark and lying to us for days." |
| 5 | `confront_daniel`: "You talk about staying calm after sneaking out last night like you own the place." | `confront_daniel`: "Easy to say when you were the one sneaking out and eating behind our backs." |

**E2 phrases per arm** (`score.txt`, field `e2`):
- control: seed 1, 3 of 5; seed 2, 5 of 5; seed 3, 5 of 5;
- probe: seed 1, 2 of 5; seed 2, 5 of 5; seed 3, 4 of 5.

## 3. Commands and output

From `Prototypes/llm-morning/`. Only command 3 had `GEMINI_API_KEY` set.
```
# 1. the cases, from cache/v18 (key unset)
seed 1 Mara 10:39: cache key recomputed from (model, seed, world.SYSTEM, prompt) matches: True; 79 lines; v18 answer: accuse_daniel: …
seed 2 Mara 10:18: cache key recomputed from (model, seed, world.SYSTEM, prompt) matches: True; 89 lines; v18 answer: accuse_daniel: …
seed 3 Leo 10:48: cache key recomputed from (model, seed, world.SYSTEM, prompt) matches: True; 88 lines; v18 answer: confront_daniel: …
$ env -u GEMINI_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe runs/probe_far/probe.py build
seed1_mara: street line after line 10; options before line 75 (say_other)
seed2_mara: street line after line 9; options before line 82 (say_other)
seed3_leo: street line after line 9; options before line 81 (say_other)
# 2. the plan record -> runs/probe_far/plan_frozen.txt (also: sha256 of probe.py and every case file; git status)
recorded_utc: 2026-10-07T19:20:27Z
889b4ebc2935073f5c0c510b1f0f7e3c8401149122bdf7f4161db1fb7e12346a *runs/probe_far/plan.md
$ ls runs/probe_far/answers
ls: cannot access 'runs/probe_far/answers': No such file or directory
# 3. the asks -> runs/probe_far/ask.stdout.txt
$ PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -u runs/probe_far/probe.py ask > runs/probe_far/ask.stdout.txt 2>&1
    [503 UNAVAILABLE] waiting 5s, retry 1/6
seed1_mara control 2 (seed 102): 2 API request(s); live asks so far 2
… (every other ask: 1 API request)
seed3_leo probe 5 (seed 105): 1 API request(s); live asks so far 30
exit 0
# 4. scoring, and a search of every answer's words, reason and feeling for street|further|houses|tonight|neighbou
$ env -u GEMINI_API_KEY … runs/probe_far/probe.py score > runs/probe_far/score.txt
F1 probe answers choosing a far option or speaking of tonight or the houses further along: 0 of 15; control answers speaking of tonight: 0 of 15 -> FAIL
F2 answers with an E2 phrase: probe 11 of 15, control 13 of 15 -> PASS
answers\seed3_leo_control_2.json ['reason'] Daniel has no right to lecture anyone about calm after sneaking out into the dangerous street last night.
# 5. at the end
$ sha256sum runs/probe_far/plan.md
889b4ebc2935073f5c0c510b1f0f7e3c8401149122bdf7f4161db1fb7e12346a *runs/probe_far/plan.md
```
- **30 answers** are saved, from 31 API requests: one 503 retry, on seed 1, control sample 2.
- **No repo code, prompt or cache was changed.** Before this report, `git status` showed only `runs/probe_far/` as
  new (`plan_frozen.txt`).
