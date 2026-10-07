"""P3, read only: for each of the 4 memories restored by the check fix, whether that night mind proposed it again in
v16, its verdict, and in how many of that person's v16-only prompts (cache/v16 entries not in cache/v15) it appears,
by the day the prompt belongs to. Run from Prototypes/llm-morning/."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
R = "What you did, saw and heard today and tonight, in order (each with its id):"
FOUR = [(1, 1, "elena", "memory", "I heard the front door open in the night and found Daniel's bed empty before he returned with nothing in his hands."),
        (1, 1, "mara", "intent", "I am going to ask Daniel why he went out into the night and came back with nothing."),
        (1, 2, "daniel", "memory", "I lay awake in the dark with Leo, listening and starving, knowing the responsibility is mine alone."),
        (3, 2, "elena", "memory", "Someone went out into the dark and came back before dawn and I stayed in bed while my children took risks.")]
for s, k, pid, kind, text in FOUR:
    tr = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    old = json.load(open(f"cache/v15/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    new = json.load(open(f"cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    r = tr[f"mind{k}"][pid]
    if kind == "intent":
        produced, verdict = r["intent"] == text, r["intent_verdict"]
    else:
        hit = [m for m in r["memories"] if m["meaning"] == text]
        produced, verdict = bool(hit), (hit[0]["verdict"] if hit else None)
    mine = [e["prompt"] for key, e in new.items() if key not in old and e["prompt"].startswith(f"You are {pid.capitalize()},")]
    day = sum(text in p for p in mine if R not in p and "\nNow it is night" not in p)
    night = sum(text in p for p in mine if "\nNow it is night" in p and R not in p)
    mind = sum(text in p for p in mine if R in p)
    print(f"seed {s} mind {k} {pid} {kind}: produced again {produced}; verdict {verdict}; in their v16-only prompts: "
          f"{day} day, {night} night, {mind} mind")
