"""reports/probe_after.md: the quiet log's entries other than Q1 and Q2, from the knock, in each scene (read-only).

    python runs/probe_after/quiet_log_other.py        from Prototypes/llm-morning/
"""
import json, os, sys
sys.path.insert(0, os.getcwd())
import quiet
for k in (1, 3, 4):
    r = json.load(open(os.path.join("runs", "probe_after", f"scene{k}.json"), encoding="utf-8"))
    print(k, [(quiet.clock(e["minute"]), e["kind"], e["fired"], e.get("why")) for e in r["quiet_log"]
              if e["kind"] not in ("Q1", "Q2")])
