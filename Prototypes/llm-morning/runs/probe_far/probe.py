"""The far-street probe (reports/probe_far.md). Standalone: no repo code, prompt or cache is changed.

    python runs/probe_far/probe.py build      write cases/*_probe.txt from cases/*_control.txt (no API)
    python runs/probe_far/probe.py ask        5 control and 5 probe asks per case, live, past the cache;
                                              every raw answer to answers/
    python runs/probe_far/probe.py score      F1 and F2 from answers/ (no API)

Run from Prototypes/llm-morning/. The cases are v18's first Q2 prompts, as sent (cache/v18). Each sample k = 1..5 is
asked with seed 100 + k, in both arms, so each control answer has a probe answer at the same seed.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
HERE = os.path.join("runs", "probe_far")
CASES = {"seed1_mara": 1, "seed2_mara": 2, "seed3_leo": 3}
SEEDS = [101, 102, 103, 104, 105]
STREET = ("About the street: the houses further along it have not been searched; nobody knows what is left in them, "
          "and it is further and more dangerous than next door.")
OPTIONS = ["- propose_far: (speech) say someone should try the houses further along the street tonight",
           "- volunteer_far: (speech) offer to go further along the street tonight yourself"]
FAR = ("propose_far", "volunteer_far")
E2_WORDS = ("snuck", "sneak", "went out", "came back", "with nothing", "empty-handed", "took the food", "promise")
MAX_ASKS = 30


def path(*p):
    return os.path.join(HERE, *p)


def build():
    for case in CASES:
        lines = open(path("cases", f"{case}_control.txt"), encoding="utf-8").read().split("\n")
        i = next(i for i, x in enumerate(lines) if x.startswith("About the neighbour's house:"))
        lines.insert(i + 1, STREET)
        j = lines.index("- say_other: (speech) say something else")
        lines[j:j] = OPTIONS
        open(path("cases", f"{case}_probe.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print(f"{case}: street line after line {i + 1}; options before line {j + 1} (say_other)")


def ask():
    from gemini import GeminiClient, load_config
    config = load_config("config.json")
    system = open(path("cases", "system.txt"), encoding="utf-8").read()
    os.makedirs(path("answers"), exist_ok=True)
    asked = 0
    for case in CASES:
        for arm in ("control", "probe"):
            prompt = open(path("cases", f"{case}_{arm}.txt"), encoding="utf-8").read()
            for k, seed in enumerate(SEEDS, 1):
                out = path("answers", f"{case}_{arm}_{k}.json")
                if os.path.exists(out):
                    continue
                if asked >= MAX_ASKS:
                    sys.exit(f"stopped: {MAX_ASKS} live asks reached")
                client = GeminiClient(config, seed)
                text = client.generate(system, prompt)
                asked += 1
                json.dump({"case": case, "arm": arm, "sample": k, "seed": seed, "model": config["model"],
                           "temperature": config["temperature"], "api_requests": client.requests, "raw": text},
                          open(out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
                print(f"{case} {arm} {k} (seed {seed}): {client.requests} API request(s); live asks so far {asked}",
                      flush=True)


def score():
    rows = []
    for case in CASES:
        for arm in ("control", "probe"):
            for k in range(1, 6):
                a = json.load(open(path("answers", f"{case}_{arm}_{k}.json"), encoding="utf-8"))
                ans = json.loads(a["raw"])
                words = ans.get("say") or ""
                low = words.lower()
                rows.append({"case": case, "arm": arm, "k": k, "option": ans.get("option"), "say": words,
                             "angry_at": ans.get("angry_at"), "far_option": ans.get("option") in FAR,
                             "tonight": "tonight" in low,
                             "further": "further along" in low or "houses" in low,
                             "e2": [w for w in E2_WORDS if w in low]})
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    p = [r for r in rows if r["arm"] == "probe"]
    c = [r for r in rows if r["arm"] == "control"]
    f1p = sum(r["far_option"] or r["tonight"] or r["further"] for r in p)
    f1c = sum(r["tonight"] for r in c)
    e2p, e2c = sum(bool(r["e2"]) for r in p), sum(bool(r["e2"]) for r in c)
    print(f"\nF1 probe answers choosing a far option or speaking of tonight or the houses further along: {f1p} of "
          f"{len(p)}; control answers speaking of tonight: {f1c} of {len(c)} -> "
          f"{'PASS' if f1p >= 5 and f1c <= 2 else 'FAIL'}")
    print(f"F2 answers with an E2 phrase: probe {e2p} of {len(p)}, control {e2c} of {len(c)} -> "
          f"{'PASS' if e2p / len(p) < e2c / len(c) else 'FAIL'}")


if __name__ == "__main__":
    {"build": build, "ask": ask, "score": score}[sys.argv[1]]()
