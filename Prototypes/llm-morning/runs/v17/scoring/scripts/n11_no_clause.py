"""N11 as score.py counts it, but without P2's target clause (the design's §9.2 "N11-mech" reading), on v16
and v17 day 3s. Read only. Run from Prototypes/llm-morning/."""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "runs", "v17", "scoring", "scripts"))
import score                                         # noqa: E402

for v in ("v16", "v17"):
    n = 0
    for seed in (1, 2, 3):
        t, _ = score.load(v, seed)
        runs = score.n11(t["day3"], clause=False)
        n += bool(runs)
        print(f"{v} seed {seed}: {len(runs)} runs without the target clause")
    print(f"{v}: N11 without the target clause on {n} of 3 days")
