"""Q4. For Elena (chose reassure_all) and Mara (chose accuse_daniel) in calm_probe / calm_variants: every line of the prompt
before "Your options:" that names the target (Daniel) or the subject of the act chosen. Read-only.
Lines are taken from the 10:30 prompt of version P (calm_probe), scenes 1 and 3; the 10:00 and 11:00 prompts and versions T, O,
TO hold the same lines except those listed by q3_fixed.py. Position from the end: the last line of the prompt is 1.
Themes (a line can have several), each a regular expression on the line:
  DANIEL   the word Daniel (Mara's target)
  NIGHT    Daniel's night out: went there / out / to the neighbour; the neighbour's house tonight; going out; cross; should go;
           means to go; into the night; came back; the front door being opened; nothing in his hands; bed was empty
  CAN      the can; taking it; took the can; denied taking; denying it
  FIGHT    accus*, confront*, angry, fight*, quarrel, argu*
  TOGETHER together; apart; family whole / safe; keeping the family; closeness; reassur*; stay calm; stay together"""
import collections, json, re, sys
sys.path.insert(0, "runs/stuck_facts")
from sections import sections

THEMES = {
    "DANIEL": r"\bDaniel\b",
    "NIGHT": (r"went (there|out|to the neighbour)|neighbour's house (tonight|and see)|going out|\bcrossed?\b|\bshould go\b|"
              r"means to go|go out|into the night|came back|front door being opened|nothing in his hands|bed was empty"),
    "CAN": r"\bthe can\b|taking it|took the can|denied taking|denying it",
    "FIGHT": r"accus|confront|\bangry\b|\bfight|quarrel|argu",
    "TOGETHER": r"together|\bapart\b|family (whole|safe)|keeping the family|closeness|reassur|stay calm|stay together",
}


def prompts(scene, who):
    d = json.load(open(f"runs/calm_probe/scene{scene}.json"))
    return {mo["clock"]: a["prompt"] for mo in d["moments"] for a in mo["asks"] if a["who"] == who}


for who, act in (("elena", "reassure_all"), ("mara", "accuse_daniel")):
    for scene in (1, 3):
        text = prompts(scene, who)["10:30"]
        L = text.split("\n")
        secs = sections(text)
        cut = L.index("Your options:")
        print(f"\n## {who} (chose {act}), scene {scene}, 10:30 prompt: {cut} lines before the options, {len(L)} in all")
        per = collections.OrderedDict()
        for i in range(cut):
            tags = [t for t, rx in THEMES.items() if re.search(rx, L[i])]
            a = per.setdefault(secs[i][0], [0, 0, collections.Counter()])
            a[1] += 1
            if set(tags) - {"DANIEL"}:
                a[0] += 1
            for t in tags:
                a[2][t] += 1
        for sec, (n, tot, c) in per.items():
            print(f"   {sec:38s} {n:2d} of {tot:2d} lines tagged NIGHT/CAN/FIGHT/TOGETHER   {dict(c)}")
        print("   --- lines tagged NIGHT / CAN / FIGHT / TOGETHER (line no. | section | from end | tags | text)")
        for i in range(cut):
            tags = [t for t, rx in THEMES.items() if re.search(rx, L[i])]
            if set(tags) - {"DANIEL"}:
                print(f"   {i+1:3d} | {secs[i][0]:34s} | {len(L)-i:3d} | {','.join(tags):28s} | {L[i]}")
        d = [i for i in range(cut) if re.search(THEMES["DANIEL"], L[i])]
        print(f"   --- lines that name Daniel: {len(d)} of {cut}; by section: " + str(dict(collections.Counter(secs[i][0] for i in d))))
        print("   --- the lines that name Daniel and are in none of the lists above (line no. | section | from end | text)")
        for i in d:
            tags = [t for t, rx in THEMES.items() if re.search(rx, L[i])]
            if not (set(tags) - {"DANIEL"}):
                print(f"   {i+1:3d} | {secs[i][0]:34s} | {len(L)-i:3d} | {L[i][:150]}")
