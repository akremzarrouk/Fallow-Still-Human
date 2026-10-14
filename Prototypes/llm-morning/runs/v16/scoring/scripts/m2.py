"""M2 part 1 (a), by code (days_design §8): every kept memory's cited ids are events the person witnessed; and in
which later prompts (from cache/v16) each kept memory and intent appears. Read only. Run from Prototypes/llm-morning/."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    tr = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    cache = json.load(open(f"cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    events = {e["id"]: e for e in tr["chronicle"]["events"]}
    prompts = [e["prompt"] for e in cache.values()]
    total = bad = 0
    for k in (1, 2):
        for pid, r in tr[f"mind{k}"].items():
            name = pid.capitalize()
            mine = [p for p in prompts if p.startswith(f"You are {name},")]
            for m in r["memories"]:
                if m["verdict"] != "kept":
                    continue
                total += 1
                wit = [i for i in m["ids"] if pid not in events[i]["witnesses"]]
                bad += bool(wit)
                where = {"day": 0, "night": 0, "mind": 0, "others": 0}
                for p in mine:
                    if m["meaning"] in p:
                        where["mind" if RECORDS in p else "night" if "\nNow it is night" in p else "day"] += 1
                where["others"] = sum(m["meaning"] in p for p in prompts if not p.startswith(f"You are {name},"))
                print(f"seed {s} mind{k} {name:6} ids {m['ids']} witnessed by them: {'yes' if not wit else 'NO ' + str(wit)};"
                      f" in their later prompts: {where['day']} day, {where['night']} night, {where['mind']} mind;"
                      f" in anyone else's: {where['others']}")
            if r["intent"]:
                n = sum(r["intent"] in p for p in mine if RECORDS not in p)
                print(f"seed {s} mind{k} {name:6} intent in their later prompts: {n}")
    print(f"seed {s}: kept memories {total}, citing an unwitnessed event: {bad}")
