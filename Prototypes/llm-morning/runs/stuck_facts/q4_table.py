"""Q4 as Markdown tables (same themes and prompts as q4_names.py): for Elena (reassure_all) and Mara (accuse_daniel), scenes 1 and 3,
the 10:30 calm_probe prompt: each line before "Your options:" that matches a theme other than the bare word Daniel
(NIGHT, CAN, FIGHT, TOGETHER), then each line that names Daniel only. Position from the end: the last line of the prompt is 1."""
import json, re, sys
sys.path.insert(0, "runs/stuck_facts")
from sections import sections
from q4_themes import THEMES


def prompts(scene, who):
    d = json.load(open(f"runs/calm_probe/scene{scene}.json"))
    return {mo["clock"]: a["prompt"] for mo in d["moments"] for a in mo["asks"] if a["who"] == who}


def clip(s, n=400):
    s = s.replace("|", "\\|")
    return s if len(s) <= n else s[:n - 3] + "..."


for who, act in (("elena", "reassure_all"), ("mara", "accuse_daniel")):
    for scene in (1, 3):
        text = prompts(scene, who)["10:30"]
        L = text.split("\n")
        secs = sections(text)
        cut = L.index("Your options:")
        rows, only = [], []
        for i in range(cut):
            tags = [t for t, rx in THEMES.items() if re.search(rx, L[i])]
            if set(tags) - {"DANIEL"}:
                rows.append((i, tags))
            elif "DANIEL" in tags:
                only.append(i)
        print(f"#### {who.capitalize()} (chose {act}), scene {scene}, 10:30 prompt ({len(L)} lines, {cut} before the options)")
        print()
        print(f"{len(rows)} lines match NIGHT, CAN, FIGHT or TOGETHER; {len(rows) + len(only)} of the {cut} name Daniel or match one of those.")
        print()
        print("| line | section | from end | themes | text |")
        print("|---|---|---|---|---|")
        for i, tags in rows:
            print(f"| {i+1} | {secs[i][0]} | {len(L)-i} | {', '.join(tags)} | {clip(L[i])} |")
        print()
        print("Lines that name Daniel and match no other theme: " +
              "; ".join(f"{i+1} ({secs[i][0]}, {len(L)-i} from end)" for i in only) + ".")
        print()
