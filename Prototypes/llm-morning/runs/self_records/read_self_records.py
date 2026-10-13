"""Reads runs/self_records/scene<k>.json against calm_probe's answers (runs/calm_probe/scene<k>.json): the verdicts on
P1-P4, every ask as a Markdown table row, choices per person and version, and how often each person's words repeat
across the three minutes (reports/stuck_facts.md §1's measure: words = `say` lower-cased, [a-z0-9']+, as a set; a pair
counts when |A & B| / max(|A|, |B|) >= 0.6; word-for-word equal after lower-casing and trimming; silent is not paired).
No live call."""
import collections
import itertools
import json
import re

ORDER = ("elena", "leo", "mara")
rows = []
for k in (1, 3):
    rows += json.load(open(f"runs/self_records/scene{k}.json", encoding="utf-8"))["asks"]
base = []
for k in (1, 3):
    for mo in json.load(open(f"runs/calm_probe/scene{k}.json", encoding="utf-8"))["moments"]:
        for a in mo["asks"]:
            base.append(dict(version="P", scene=k, clock=a["clock"], who=a["who"], option=a["option"], say=a["say"],
                             feeling=a["feeling"], reason=a["reason"], how="calm_probe", valid=a["valid"]))
allrows = base + rows


def words(say):
    return set(re.findall(r"[a-z0-9']+", (say or "").lower()))


def esc(s):
    return "" if s is None else str(s).replace("|", "\\|").replace("\n", " ")


print("## Counts")
print(f"rows: {len(rows)}; how: {dict(collections.Counter(r['how'] for r in rows))}")
print(f"valid: {sum(r['valid'] for r in rows)} of {len(rows)}")
print()
print("## Verdicts")
sw = [r for r in rows if r["version"] == "SW"]
changed = [r for r in sw if r["option"] != r["baseline"]["option"]]
print(f"P1: SW answers with a different option than calm_probe's: {len(changed)} of {len(sw)} "
      f"(needs >= 6): {'holds' if len(changed) >= 6 else 'fails'}")
for r in changed:
    print(f"    scene {r['scene']} {r['clock']} {r['who']}: {r['baseline']['option']} -> {r['option']}")
mara_s = [r for r in rows if r["version"] == "S" and r["who"] == "mara" and r["how"] == "live"]
n = sum(r["option"] == "accuse_daniel" for r in mara_s)
print(f"P2: S, Mara's live asks choosing accuse_daniel: {n} of {len(mara_s)} (needs <= 3): "
      f"{'holds' if n <= 3 else 'fails'}")
el_w = [r for r in rows if r["version"] == "W" and r["who"] == "elena"]
n = sum(r["option"] == "reassure_all" for r in el_w)
print(f"P3: W, Elena's asks choosing reassure_all: {n} of {len(el_w)} (needs <= 3): {'holds' if n <= 3 else 'fails'}")
bad = [r for r in rows if not r["valid"]]
print(f"P4: answers choosing an option not offered: {len(bad)} of {len(rows)}: {'holds' if not bad else 'fails'}")
print()
print("## Choices changed against calm_probe, per version")
for v in ("S", "W", "SW"):
    vs = [r for r in rows if r["version"] == v]
    ch = [f"s{r['scene']} {r['clock']} {r['who']} {r['baseline']['option']}->{r['option']}" for r in vs
          if r["option"] != r["baseline"]["option"]]
    print(f"{v}: {len(ch)} of {len(vs)}: {ch}")
print()
print("## Options per person and version (both scenes, 6 asks each)")
print("| person | P (calm_probe) | S | W | SW |")
print("|---|---|---|---|---|")
for w in ORDER:
    cells = []
    for v in ("P", "S", "W", "SW"):
        c = collections.Counter(r["option"] for r in allrows if r["version"] == v and r["who"] == w)
        cells.append(", ".join(f"{o} {n}" for o, n in c.most_common()))
    print(f"| {w} | " + " | ".join(cells) + " |")
print()
print("## Every ask, beside calm_probe's answer")
print("| version | scene | minute | person | lines removed / added | choice | words | feeling | reason | calm_probe: choice | calm_probe: words | calm_probe: feeling | calm_probe: reason |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
vo = {"S": 0, "W": 1, "SW": 2}
for r in sorted(rows, key=lambda r: (vo[r["version"]], r["scene"], r["clock"], ORDER.index(r["who"]))):
    b = r["baseline"]
    mark = "" if r["option"] == b["option"] else " **(changed)**"
    print(f"| {r['version']} | {r['scene']} | {r['clock']} | {r['who']} | -{r['lines_removed']} / +{r['lines_added']} | "
          f"`{r['option']}`{mark} | {esc(r['say'])} | {esc(r['feeling'])} | {esc(r['reason'])} | `{b['option']}` | "
          f"{esc(b['say'])} | {esc(b['feeling'])} | {esc(b['reason'])} |")
print()
print("## Words repeating across the three minutes (per scene, person, version; 3 asks, up to 3 pairs)")
print("| person | scene | version | options at 10:00 / 10:30 / 11:00 | pairs with words | pairs >= 0.6 | word-for-word equal | share per pair (10:00-10:30, 10:00-11:00, 10:30-11:00) |")
print("|---|---|---|---|---|---|---|---|")
tot = collections.defaultdict(lambda: [0, 0, 0])
for w in ORDER:
    for k in (1, 3):
        for v in ("P", "S", "W", "SW"):
            rs = sorted([r for r in allrows if r["version"] == v and r["who"] == w and r["scene"] == k],
                        key=lambda r: r["clock"])
            assert len(rs) == 3
            shares, n, hi, eq = [], 0, 0, 0
            for a, b in itertools.combinations(rs, 2):
                wa, wb = words(a["say"]), words(b["say"])
                if not wa or not wb:
                    shares.append("-")
                    continue
                s = len(wa & wb) / max(len(wa), len(wb))
                n += 1
                hi += s >= 0.6
                eq += a["say"].strip().lower() == b["say"].strip().lower()
                shares.append(f"{s:.2f}")
            t = tot[(w, v)]
            t[0] += n
            t[1] += hi
            t[2] += eq
            print(f"| {w} | {k} | {v} | {' / '.join(r['option'] for r in rs)} | {n} | {hi} | {eq} | {', '.join(shares)} |")
print()
print("## Totals per person and version (both scenes)")
print("| person | version | pairs with words | pairs >= 0.6 | word-for-word equal |")
print("|---|---|---|---|---|")
for w in ORDER:
    for v in ("P", "S", "W", "SW"):
        t = tot[(w, v)]
        print(f"| {w} | {v} | {t[0]} | {t[1]} | {t[2]} |")
print()
print("## The same words in two versions of the same prompt (word-for-word, lower-cased)")
for k in (1, 3):
    for c in ("10:00", "10:30", "11:00"):
        for w in ORDER:
            rs = [r for r in allrows if r["scene"] == k and r["clock"] == c and r["who"] == w and r["say"]]
            for a, b in itertools.combinations(rs, 2):
                if a["say"].strip().lower() == b["say"].strip().lower():
                    print(f"scene {k} {c} {w}: {a['version']} = {b['version']}: {a['say']!r}")
print()
print("## Words shared across versions: the opening of each answer that has words")
for w in ORDER:
    c = collections.Counter(" ".join(re.findall(r"[a-z0-9']+", r["say"].lower())[:5]) for r in allrows
                            if r["who"] == w and r["say"])
    print(f"{w}: {c.most_common(6)}")
print()
print("## What the words and reasons name, per person and version (P = calm_probe)")
OUT = re.compile(r"went out|go out|going out|sneak|out there|out into|out last night|out in the")
for w, field, rx, label in (("mara", "say", OUT, "words name Daniel's going out"),
                            ("leo", "say", OUT, "words name Daniel's going out"),
                            ("mara", "say", re.compile(r"\btook\b|\btake\b|stole|lied|\blies\b"), "words name the can (took, stole, lied)"),
                            ("elena", "reason", re.compile(r"apart"), "reason says 'apart'"),
                            ("elena", "say", re.compile(r"together|each other"), "words say 'together' or 'each other'")):
    cells = []
    for v in ("P", "S", "W", "SW"):
        rs = [r for r in allrows if r["who"] == w and r["version"] == v]
        n = sum(bool(rx.search((r[field] or "").lower())) for r in rs)
        cells.append(f"{v} {n} of {len(rs)}")
    print(f"{w}: {label}: " + "; ".join(cells))
FIGHT = re.compile(r"argu|fight|bicker|tear|turn(ing)? on|apart")
for w in ORDER:
    cells = []
    for v in ("P", "S", "W", "SW"):
        rs = [r for r in allrows if r["who"] == w and r["version"] == v]
        cells.append(f"{v} {sum(bool(FIGHT.search((r['reason'] or '').lower())) for r in rs)} of {len(rs)}")
    print(f"{w}: reason names arguing, fighting, bickering, tearing, turning on or apart: " + "; ".join(cells))
