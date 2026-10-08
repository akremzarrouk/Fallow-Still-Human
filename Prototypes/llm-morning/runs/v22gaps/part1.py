"""Part 1 of reports/v22_gaps.md (read only, no API). Run from Prototypes/llm-morning/ with GEMINI_API_KEY unset."""
import collections, json, os, re, sys
sys.path.insert(0, os.getcwd()); sys.argv = ["x"]
exec(open("runs/w22/scoring/w1_score.py", encoding="utf-8").read().split("if __name__")[0])

t, _ = load("runs/v22")
c = json.load(open("cache/v22/gemini-3.5-flash-lite-daniel_ate_it-seed2.json", encoding="utf-8"))
live = [(k, c[k]["prompt"], json.loads(c[k]["response"])) for k in list(c)[147:]]

def now_of(p):
    return next((l for l in p.splitlines() if l.startswith("Now")), "")

def block(p, head):
    L = p.splitlines()
    if head not in L:
        return None
    i = L.index(head) + 1
    out = []
    while i < len(L) and L[i].startswith("- "):
        out.append(L[i]); i += 1
    return out

# ---- 1a. Mara's day 3 lines of the frame "You went out into the night/dark and came back with nothing, Daniel. Why did you even go?"
FRAME = re.compile(r"went out into the (night|dark) and came back with nothing, Daniel\. Why did you even go\?")
print("== 1a. Mara, day 3: every speech act")
for a in speech(t["day3"]):
    if a["who"] == "mara":
        print(f"  {data.clock(a['minute']):>6} {a['option']:<16} {a['words']}")
mara = [a for a in speech(t["day3"]) if a["who"] == "mara"]
frame = [a for a in mara if FRAME.search(a["words"])]
print(f"\n  frame lines: {len(frame)}; word for word: {dict(collections.Counter(a['words'] for a in frame))}")
print(f"  morning (min 00-18, the first stretch): {sum(1 for a in frame if a['minute'] < 21)}; after: {sum(1 for a in frame if a['minute'] >= 21)}")
print(f"  Mara's speech acts on day 3: {len(mara)}")

print("\n== 1a. what each prompt showed of her own earlier words")
for a in frame:
    m = [(k, p, r) for k, p, r in live if p.startswith("You are Mara") and "Your options:" in p and "Now it is night" not in p
         and r.get("say") == a["words"] and now_of(p).startswith("Now, " + (f"minute {a['minute']:02d}" if a['minute'] < 90 else data.clock(a['minute'])))]
    k, p, r = m[0]
    own = block(p, "Your own last words this morning:") or block(p, "Your own last words today:")
    print(f"\n-- {data.clock(a['minute'])} [{a['option']}] {a['words']}")
    print(f"   {now_of(p)}")
    print(f"   'Your own last words' block: {own}")
    mem = [l for l in p.splitlines() if re.match(r"- (min \d+|\d\d:\d\d): you ", l)]
    print(f"   own lines in 'What else happened this morning': {mem}")
    quoted = [l for l in p.splitlines() if re.match(r"- (min \d+|\d\d:\d\d)[:,] you [^\"]*\"", l)]
    print(f"   own lines with quoted words: {quoted}")
    src = [l for l in p.splitlines() if re.search(r"nothing", l) and not l.startswith("- min") and not l.startswith("- silent")
           and 'nobody' not in l.lower()[:0]]
    for l in src[:6]:
        print(f"   standing line with 'nothing': {l[:200]}")
    intent = [l for l in p.splitlines() if l.startswith("- You meant to")]
    print(f"   intent line: {intent}")
    open(f"runs/v22gaps/mara_d3_{data.clock(a['minute']).replace(':','')}_{a['minute']:03d}.txt", "w", encoding="utf-8", newline="\n").write(p)

# ---- 1b. the hiding on day 3+ and in stretches
print("\n== 1b. own quoted words in the live prompts of days 3-10")
own_q = re.compile(r"^- (min \d+|\d\d:\d\d)[:,] you [^\"\n]*[:]? ?\"")
bad = []; nblock = 0; nday = 0; stretch_block = 0
for k, p, r in live:
    if "Your options:" not in p or "Now it is night" in p:
        continue
    nday += 1
    own = block(p, "Your own last words this morning:") or block(p, "Your own last words today:")
    if own:
        nblock += 1
        if any('"' in l for l in own):
            bad.append((p[:40], own))
    for l in p.splitlines():
        if own_q.match(l):
            bad.append((p[:40], l))
print(f"  day prompts {nday}; with the 'Your own last words' block {nblock}; lines with quoted own words {len(bad)}")
for b in bad[:5]: print("   ", b)
by_when = collections.Counter("today" if ("Your own last words today:" in p) else "this morning" if ("Your own last words this morning:" in p) else "none"
                              for k, p, r in live if "Your options:" in p and "Now it is night" not in p)
print(f"  block headings: {dict(by_when)}")

# ---- 1c. lines said word for word 2+ times, per person per day
def repeats(t):
    out = {}
    for k in range(3, DAYS + 1):
        if f"day{k}" not in t: continue
        for q in data.ORDER:
            ws = [a["words"] for a in speech(t[f"day{k}"]) if a["who"] == q]
            cnt = collections.Counter(ws)
            rep = {w: n for w, n in cnt.items() if n >= 2}
            out[(k, q)] = (len(ws), sum(rep.values()), len(rep), max(rep.values()) if rep else 0)
    return out
r21 = repeats(load("runs/v21")[0]); r22 = repeats(t)
print("\n== 1c. per person per day: speech acts / acts in a repeated text / distinct repeated texts / most repeats")
print("day  person | v21 acts rep texts max | v22 acts rep texts max")
for k in range(3, 11):
    for q in data.ORDER:
        a, b = r21[(k, q)], r22[(k, q)]
        print(f"{k:>3}  {NAME[q]:<6} | {a[0]:>3} {a[1]:>3} {a[2]:>2} {a[3]:>2} | {b[0]:>3} {b[1]:>3} {b[2]:>2} {b[3]:>2}")
for name, r in (("v21", r21), ("v22", r22)):
    print(f"{name}: speech acts {sum(v[0] for v in r.values())}; in a repeated text (same person, same day) {sum(v[1] for v in r.values())}; distinct repeated texts {sum(v[2] for v in r.values())}; person-days with a repeat {sum(1 for v in r.values() if v[1])} of {len(r)}")
    for q in data.ORDER:
        print(f"   {NAME[q]:<6} acts {sum(r[(k,q)][0] for k in range(3,11))}, in repeated texts {sum(r[(k,q)][1] for k in range(3,11))}, texts {sum(r[(k,q)][2] for k in range(3,11))}")
