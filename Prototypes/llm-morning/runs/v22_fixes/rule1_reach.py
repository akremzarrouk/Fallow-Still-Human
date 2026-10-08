"""No API: how many kept night-mind memories and intents of v21 and v22 (minds 3-9) quote the person's own words, by the
new rule (re-judged against the run's own chronicle). Read only."""
import json, os, sys, types
sys.path.insert(0, os.getcwd()); assert not os.environ.get("GEMINI_API_KEY")
import mind
for run in ("v21", "v22"):
    t = json.load(open(f"runs/{run}/daniel_ate_it-seed2.transcript.json", encoding="utf-8"))
    chron = types.SimpleNamespace(events=t["chronicle"]["events"])
    kept = hit = 0; rows = []
    for k in range(3, 10):
        for pid, r in t[f"mind{k}"].items():
            for m in r["memories"]:
                if m["verdict"] == "kept":
                    kept += 1
                    if mind.quotes_own_words(m["meaning"], chron, pid):
                        hit += 1; rows.append((k, pid, "memory", m["meaning"][:100]))
            if r.get("intent_verdict") == "kept" and r.get("intent"):
                kept += 1
                if mind.quotes_own_words(r["intent"], chron, pid):
                    hit += 1; rows.append((k, pid, "intent", r["intent"][:100]))
    print(f"{run}: kept memories and intents of minds 3-9: {kept}; that quote the person's own words: {hit}")
    for x in rows: print("   ", x)
