"""The stakes probe (reports/probe_stakes.md). Standalone: no repo code, prompt or cache is changed.

    python runs/probe_stakes/probe.py build      write cases/*_probe.txt from cases/*_control.txt (no API)
    python runs/probe_stakes/probe.py ask        5 control and 5 probe asks per case, live, past the cache;
                                                 every raw answer to answers/
    python runs/probe_stakes/probe.py score      S1 and S2 from answers/ (no API)

Run from Prototypes/llm-morning/. The cases are v21's four night-8 bedtime prompts, as sent (capture.py rebuilt them and
checked each against its cache key). Each sample k = 1..5 is asked with seed 100 + k, in both arms.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
HERE = os.path.join("runs", "probe_stakes")
CASES = ["daniel", "elena", "leo", "mara"]
SEEDS = [101, 102, 103, 104, 105]
LINE = "You know your body: without food, you will not last many more days."
GO = ("go_next_door", "go_further")
# S2: a reason "speaks of dying, surviving or not lasting" if it has one of these (each answer is also read by hand).
STAKES = re.compile(r"\b(die|dies|died|dying|death|dead|perish\w*|surviv\w*|alive)\b"
                    r"|\b(?:not|n't|cannot|can't|won't|never)\s+(?:\w+\s+)?last\b|\brunning out of time\b", re.I)
MAX_ASKS = 40


def path(*p):
    return os.path.join(HERE, *p)


def build():
    for case in CASES:
        lines = open(path("cases", f"{case}_control.txt"), encoding="utf-8").read().split("\n")
        i = next(i for i, x in enumerate(lines) if x.startswith("Your body:"))
        lines.insert(i + 1, LINE)
        open(path("cases", f"{case}_probe.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print(f"{case}: line inserted after line {i + 1} ({lines[i][:60]}...)")


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


def rows():
    out = []
    for case in CASES:
        for arm in ("control", "probe"):
            for k in range(1, 6):
                a = json.load(open(path("answers", f"{case}_{arm}_{k}.json"), encoding="utf-8"))
                try:
                    ans = json.loads(a["raw"])
                except ValueError:
                    ans = {}
                reason = ans.get("reason") or ""
                out.append({"case": case, "arm": arm, "k": k, "seed": a["seed"], "option": ans.get("option"),
                            "say": ans.get("say"), "feeling": ans.get("feeling"), "reason": reason,
                            "go": ans.get("option") in GO, "stakes": bool(STAKES.search(reason)),
                            "stakes_words": [m.group(0) for m in STAKES.finditer(reason)]})
    return out


def score():
    rs = rows()
    print(json.dumps(rs, ensure_ascii=False, indent=1))
    p = [r for r in rs if r["arm"] == "probe"]
    c = [r for r in rs if r["arm"] == "control"]
    s1p, s1c = sum(r["go"] for r in p), sum(r["go"] for r in c)
    s2p, s2c = sum(r["stakes"] for r in p), sum(r["stakes"] for r in c)
    print(f"\nS1 probe answers choosing go_next_door or go_further: {s1p} of {len(p)}; control: {s1c} of {len(c)} -> "
          f"{'PASS' if s1p >= 4 and s1c <= 1 else 'FAIL'}")
    print(f"S2 probe answers whose reason speaks of dying, surviving or not lasting: {s2p} of {len(p)} (need "
          f"{(len(p) + 1) // 2}); control: {s2c} of {len(c)} -> {'PASS' if 2 * s2p >= len(p) else 'FAIL'}")
    for case in CASES:
        for arm in ("control", "probe"):
            sub = [r for r in rs if r["case"] == case and r["arm"] == arm]
            print(f"  {case} {arm}: options {[r['option'] for r in sub]}; stakes reasons {sum(r['stakes'] for r in sub)} of 5")


if __name__ == "__main__":
    {"build": build, "ask": ask, "score": score}[sys.argv[1]]()
