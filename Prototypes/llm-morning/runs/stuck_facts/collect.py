"""Read-only. Collects the probes' live day-phase answers (talk_probe, calm_variants, calm_probe) into runs/stuck_facts/asks.json, one record per ask:
dataset, scene, variant, day, clock, minute, who, option, say, prompt, source. No API call: it only reads files and
refuses to run with a key set. (v22 is in collect_v22.py.)
Cross-checks: every live probe prompt is in the matching cache file with the same option."""
import json, os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY"), "a key is set: this script must make no live call"
OUT = "runs/stuck_facts"
recs, checks = [], []

def cache_prompts(path):
    return {v["prompt"]: json.loads(v["response"]) for v in json.load(open(path)).values()
            if v["response"].lstrip().startswith("{") and '"option"' in v["response"]}

def opt_of(answer):
    a = json.loads(answer)
    return a["option"], a.get("say")

# 1. talk_probe: live day asks, day 3 (runs/talk_probe/scene<k>.json "asks", source == live, phase == day)
for k in (1, 3, 4):
    cp = cache_prompts(f"cache/talk_probe/scene{k}.json")
    d = json.load(open(f"runs/talk_probe/scene{k}.json"))
    n = ok = 0
    for a in d["asks"]:
        if a["phase"] != "day" or a["source"] != "live":
            continue
        o, say = opt_of(a["answer"]); n += 1
        ok += (a["prompt"] in cp and cp[a["prompt"]]["option"] == o)
        m = int(a["minute"])
        recs.append(dict(dataset="talk_probe", scene=k, variant="", day=3, minute=m,
                         clock=re.search(r"\nNow, (.*?), you are", a["prompt"]).group(1), who=a["who"], option=o, say=say,
                         prompt=a["prompt"], source="live"))
    checks.append(("talk_probe", k, "live day asks", n, "in cache with same option", ok))

# 2. calm_variants: rows with how == live (46), and calm_probe's 18 live asks
for k in (1, 3):
    cp = cache_prompts(f"cache/calm_variants/scene{k}.json")
    d = json.load(open(f"runs/calm_variants/scene{k}.json"))
    n = ok = 0
    for mo in d["moments"]:
        for a in mo["asks"]:
            if a["how"] != "live":
                continue
            n += 1; ok += (a["prompt"] in cp and cp[a["prompt"]]["option"] == a["option"])
            recs.append(dict(dataset="calm_variants", scene=k, variant=a["variant"], day=3, minute=int(mo["minute"]),
                             clock=mo["clock"], who=a["who"], option=a["option"], say=a["say"],
                             prompt=a["prompt"], source="live"))
    checks.append(("calm_variants", k, "live asks", n, "in cache with same option", ok))
    cpp = cache_prompts(f"cache/calm_probe/scene{k}.json")
    d = json.load(open(f"runs/calm_probe/scene{k}.json"))
    n = ok = 0
    for mo in d["moments"]:
        for a in mo["asks"]:
            n += 1; ok += (a["prompt"] in cpp and cpp[a["prompt"]]["option"] == a["option"])
            recs.append(dict(dataset="calm_probe", scene=k, variant="P", day=3, minute=int(mo["minute"]),
                             clock=mo["clock"], who=a["who"], option=a["option"], say=a["say"],
                             prompt=a["prompt"], source="live"))
    checks.append(("calm_probe", k, "live asks", n, "in cache with same option", ok))

json.dump(recs, open(f"{OUT}/asks.json", "w"), indent=1)
print("records", len(recs))
for c in checks:
    print(c)
import collections
print(collections.Counter((r["dataset"], r["scene"]) for r in recs))
