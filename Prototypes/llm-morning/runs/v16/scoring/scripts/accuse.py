"""Read only: (1) Daniel's denials, accusations, confrontations and confessions in the chronicle of seeds 2 and 3,
for M2 part 1 (b); (2) each night-mind prompt's size and the estimated size of its records (R8 bound 1,600)."""
import json
import os
import re
import sys
sys.path.insert(0, os.getcwd())
from world import estimate_tokens   # noqa: E402  (the repo's own)
sys.stdout.reconfigure(encoding="utf-8")
for s in (2, 3):
    tr = json.load(open(f"runs/v16/daniel_ate_it-seed{s}.transcript.json", encoding="utf-8"))
    for e in tr["chronicle"]["events"]:
        if e["actor"] == "daniel" and (e["option"] or "").startswith(("accuse_", "confront_", "deny", "confess")):
            print(s, e["id"], f"min {e['minute']:02d}", e["option"], repr(e["words"]))
R = "What you did, saw and heard today and tonight, in order (each with its id):"
for s in (1, 2, 3):
    cache = json.load(open(f"cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{s}.json", encoding="utf-8"))
    for e in cache.values():
        p = e["prompt"]
        if R in p:
            recs = [x for x in p.split("\n") if re.match(r"^\[[DN]\d-\d+\]", x)]
            k = 2 if any(x.startswith("[N2-") for x in recs) else 1
            print(f"seed {s} mind{k} {p[8:p.index(',')]:6} records {len(recs):2}, records est {estimate_tokens(chr(10).join(recs))}, "
                  f"api prompt {e.get('prompt_tokens')}")
