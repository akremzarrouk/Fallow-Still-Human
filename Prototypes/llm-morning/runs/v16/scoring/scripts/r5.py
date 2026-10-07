"""R5 (days_design §7.3): day 1 of each v15 run equals v11, on the real files. Read only. Run from
Prototypes/llm-morning/."""
import json
import sys

for s in (1, 2, 3):
    try:
        story = open(f"runs/v16/daniel_ate_it-seed{s}.md", encoding="utf-8").read()
        tr = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
        meta = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.meta.json", encoding="utf-8"))
    except FileNotFoundError:
        print(f"seed {s}: no run")
        continue
    v11 = open(f"runs/v11/daniel_ate_it-seed{s}.md", encoding="utf-8").read()
    v11tr = json.load(open(f"runs/v11/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    head = story[:story.index("# The night\n")]
    d1 = meta["day1"]
    print(f"seed {s}: day 1 asks {d1['answers_live'] + d1['answers_from_cache']} (API {d1['api_requests']}, "
          f"cached {d1['answers_from_cache']}); story before '# The night' "
          f"{'IDENTICAL' if head == v11 else 'DIFFERS'} to runs/v11; transcript day1 "
          f"{'IDENTICAL' if tr['day1'] == v11tr else 'DIFFERS'}")
