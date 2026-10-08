"""Per-day tables for reports/days_v21.md: asks, trip positions, speech and silence, pairs. No API. Run from llm-morning/."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import data
from talk import act_of
from world import TRIP_KINDS
t = json.load(open("runs/v21/daniel_ate_it-seed2.transcript.json", encoding="utf-8"))
m = json.load(open("runs/v21/daniel_ate_it-seed2.meta.json", encoding="utf-8"))
N = {p: data.PEOPLE[p]["name"] for p in data.ORDER}
print("day | day asks | quiet_asks | stretches | q1/q2/q5 fired | model acts | speech | silent | trip-position acts | distinct (kind,target) | morning speech | morning end | rests | withdrawals | night asks | mind asks")
for k in range(3, 11):
    d = t[f"day{k}"]; q = d["quiet"]; mm = m[f"day{k}_quiet"]
    acts = sorted((a for tu in d["turns"] for a in tu["acts"]), key=lambda a: tuple(a["decided_at"]))
    ma = [a for a in acts if a["mode"] == "model"]
    sp = [a for a in ma if a["words"]]
    trip = [a for a in ma if act_of(a["option"])[0] in TRIP_KINDS]
    s0 = q["stretches"][0]
    msp = [a for a in sp if s0["start"] <= a["minute"] < s0["end"]]
    na = m.get(f"night{k}", {}).get("asks") if k < 10 else None
    mi = m.get(f"mind{k}", {}).get("asks") if k < 10 else None
    print(k, mm["day_asks"], mm["quiet_asks"], mm["stretches"], f'{mm["q1_fired"]}/{mm["q2_fired"]}/{mm["q5_fired"]}', len(ma), len(sp), len(ma) - len(sp), len(trip),
          len({act_of(a["option"]) for a in sp}), len(msp), data.clock(mm["morning_end"]), mm["rests"], mm["withdrawals"], na, mi)
print("trip position acts by day:", {k: [(data.clock(a['minute']), N[a['who']], a['option']) for tu in t[f'day{k}']['turns'] for a in tu['acts'] if a['mode']=='model' and act_of(a['option'])[0] in TRIP_KINDS] for k in range(3, 11)})
print("meta totals: live", m["answers_live"], "cached", m["answers_from_cache"], "api", m["api_requests"], "run_seconds", m["run_seconds"], "max_est", m["max_prompt_tokens_estimated"], "api-counted", m["max_prompt_tokens_counted_by_api"])
for k in range(3, 10):
    print("night", k, "asks", m[f"night{k}"]["asks"], "mind", m[f"mind{k}"]["asks"], "kept", m[f"mind{k}"]["memories_kept"], "rejected", m[f"mind{k}"]["memories_rejected"], "api-counted max night", m[f"night{k}"]["max_prompt_tokens_counted_by_api"])
for k in range(3, 11):
    print("api max day", k, m[f"day{k}"].get("max_prompt_tokens_counted_by_api"))
# pair repertoire: pairs used per day (all speech)
for k in range(3, 11):
    d = t[f"day{k}"]
    sp = [a for tu in d["turns"] for a in tu["acts"] if a["mode"] == "model" and a["words"]]
    from collections import Counter
    c = Counter(act_of(a["option"]) for a in sp)
    print("day", k, dict(c.most_common(6)))
