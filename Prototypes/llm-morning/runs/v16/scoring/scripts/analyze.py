"""Reads runs/v16 (transcript, meta, story) and cache/v16, and prints what reports/days_v15.md needs. Read only.
body_v13's analyze.py (body_v13.md §11), widened to three days, two nights and two night minds.
Run from Prototypes/llm-morning/.

    python analyze.py counts          per seed and scene: asks, API, cache, fallbacks, largest prompts
    python analyze.py night N K       night K (1 or 2): every decision, noticing, group and line
    python analyze.py mind N K        night mind K: each person's prompt size, every memory with its records
    python analyze.py acts N D        every model-decided act of day D (2 or 3), as markdown rows
    python analyze.py never N D       mechanical inputs for the Never sheet of day D
    python analyze.py screen N        M1's screen over day-3 acts
    python analyze.py blocks N        day 3's "What each of them carried in"
    python analyze.py convo N D       day D's conversations: spoken lines, speakers, acts aimed at each person
    python analyze.py echoes N        each kept memory and intent, then the same person's acts the next day
    python analyze.py objects N D     N13's object screen and N10's three-speaker turns for day D
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
RUNS = "runs/v16"
CACHE = "cache/v16/gemini-3.5-flash-lite-daniel_ate_it-seed{}.json"
NAMES = {"daniel": "Daniel", "elena": "Elena", "leo": "Leo", "mara": "Mara"}
ROOMS = {"kitchen": "kitchen", "brothers_room": "brothers room", "back_room": "back room", "bathroom": "bathroom"}
TITLE = {2: "# The next morning (day 5)", 3: "# The third morning (day 6)"}
RECORDS = "What you did, saw and heard today and tonight, in order (each with its id):"
EARLIER = "What stays with you from earlier days:"
TRIP = re.compile(r"^(propose_trip|volunteer|still_going|send_\w+|nobody_goes|keep_\w+_home|refuse_to_go)$")
M1 = re.compile(r"can|took|take|ate|eaten|admit|confess|lie|lied|liar|accus|blame|search|portion|offered|count|"
                r"two days|first day|day before yesterday|before all this", re.I)
OBJ = re.compile(r"\b(torch|knife|knives|flashlight|lamp|candle|light|table|chair|cupboard|cabinet|fridge|stove|oven|"
                 r"sink|bread|rice|water|bottle|jar|tin|box|bag|backpack|car|garden|yard|garage|basement|attic|roof|"
                 r"window|door|hall|hallway|stairs|bed|blanket|radio|phone|gun|weapon|rope|key|lock|map|road|town|"
                 r"store|shop|market|pantry|counter|tap|taps|shelf|shelves|street|house|room|kitchen|bathroom)s?\b", re.I)


def load(seed):
    base = f"{RUNS}/daniel_ate_it-seed{seed}"
    tr = json.load(open(base + ".transcript.json", encoding="utf-8"))
    meta = json.load(open(base + ".meta.json", encoding="utf-8"))
    story = open(base + ".md", encoding="utf-8").read()
    return tr, meta, story


def day_part(story, d):
    part = story[story.index(TITLE[d]):]
    return part[part.index("## The morning"):part.index("## What was said")]


def day_lines(story, d):
    """(minute, name, feeling, reason, mode) for every model or fallback line of day D, in order."""
    out, minute = [], None
    for line in day_part(story, d).split("\n"):
        m = re.match(r"^\*\*min (\d\d)\*\*", line)
        if m:
            minute = int(m.group(1))
            continue
        m = re.match(r"^- \*\*(\w+)\*\* \(", line)
        if not m:
            continue
        if "**FALLBACK**" in line:
            out.append((minute, m.group(1), None, None, "fallback"))
            continue
        f = re.search(r"Feeling: \*(.*?)\*\. Reason: “(.*?)” Suspects:", line)
        out.append((minute, m.group(1), f.group(1) if f else None, f.group(2) if f else None, "model"))
    return out


def model_acts(tr, story, d):
    rows = []
    lines = day_lines(story, d)
    used = [False] * len(lines)
    for turn in tr[f"day{d}"]["turns"]:
        for a in turn["acts"]:
            if a["mode"] == "routine":
                continue
            i = next((k for k, x in enumerate(lines) if not used[k] and x[0] == turn["minute"]
                      and x[1] == NAMES[a["who"]]), None)
            feel = reason = None
            if i is not None:
                used[i] = True
                feel, reason = lines[i][2], lines[i][3]
            rows.append({"minute": turn["minute"], "who": a["who"], "room": a["room"], "option": a["option"],
                         "words": a["words"], "feeling": feel, "reason": reason, "mode": a["mode"],
                         "matched": i is not None, "inner": a.get("inner"), "food": a.get("food_moment")})
    return rows


def cell(x):
    return "—" if x is None else str(x).replace("|", "\\|")


def mind_prompts(seed):
    """person -> {k: (prompt, shown)} for each night-mind prompt in the cache; shown: id -> the text shown for it."""
    cache = json.load(open(CACHE.format(seed), encoding="utf-8"))
    out = {}
    for e in cache.values():
        p = e["prompt"]
        if RECORDS not in p:
            continue
        who = p[len("You are "):p.index(",")].lower()
        k = 2 if re.search(r"\[N2-\d\d\]", p) else 1
        shown = {}
        for line in p.split("\n"):
            m = re.match(r"^- \[([^\]]+)\] (.*)$", line)
            if m:
                for i in m.group(1).split(", "):
                    shown.setdefault(i, "(earlier) " + m.group(2))
            m = re.match(r"^\[([DN]\d-\d+)\] (.*)$", line)
            if m:
                shown.setdefault(m.group(1), m.group(2))
        out.setdefault(who, {})[k] = (p, shown, e.get("prompt_tokens"))
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "counts":
        for s in (1, 2, 3):
            try:
                tr, meta, _ = load(s)
            except FileNotFoundError:
                print(f"seed {s}: no run")
                continue
            print(f"seed {s}: total asks {meta['answers_live'] + meta['answers_from_cache']} (live {meta['answers_live']}, "
                  f"cached {meta['answers_from_cache']}), API {meta['api_requests']}; seconds {meta['run_seconds']}; "
                  f"max est {meta['max_prompt_tokens_estimated']} api {meta['max_prompt_tokens_counted_by_api']}; "
                  f"sha {meta['story_sha256']}")
            for k, asks in (("day1", None), ("night", meta["night1_asks"]), ("mind1", meta["mind1_asks"]),
                            ("day2", meta["day2_asks"]), ("night2", meta["night2_asks"]), ("mind2", meta["mind2_asks"]),
                            ("day3", meta["day3_asks"])):
                x = meta[k]
                a = x["answers_live"] + x["answers_from_cache"]
                fb = x.get("fallbacks")
                if k.startswith("mind"):
                    fb = sum(r["mode"] == "fallback" for r in tr[k].values())
                if k.startswith("night"):
                    fb = sum(d["mode"] == "fallback" for d in tr[k]["decisions"])
                extra = ""
                if k.startswith("day") and k != "day1":
                    extra = (f" model {x['model_decisions']} routine {x['routine_decisions']} lines {x['lines_spoken']}"
                             f" inner {x['inner_moments']} trip_acts {x['trip_acts']} food {x.get('food_moments')}"
                             f" give {x.get('give_answers')}")
                if k.startswith("mind"):
                    extra = (f" proposed {x['memories_proposed']} kept {x['memories_kept']} rejected "
                             f"{x['memories_rejected']}")
                print(f"  {k:6} asks {a:3} (meta {asks}) api {x['api_requests']:3} cached {x['answers_from_cache']:3} "
                      f"fallbacks {fb} max est {x.get('max_prompt_tokens_estimated')} api "
                      f"{x.get('max_prompt_tokens_counted_by_api')}{extra}")
            m6 = sum(meta[k] for k in ("night1_asks", "mind1_asks", "day2_asks", "night2_asks", "mind2_asks",
                                       "day3_asks"))
            api6 = sum(meta[k] for k in ("night1_api_requests" if "night1_api_requests" in meta else "night_api_requests",
                                         "mind1_api_requests", "day2_api_requests", "night2_api_requests",
                                         "mind2_api_requests", "day3_api_requests"))
            print(f"  M6 sum {m6} (API {api6}); leavers {meta['leavers']} {meta['outcome']}; leavers2 {meta['leavers2']}"
                  f" {meta['outcome2']}; away1 {meta['night']['away']} away2 {meta['night2']['away']}; house "
                  f"{meta['night']['house']} left2 {meta['night2']['house_left']}")
            r = meta["day3"]["max_prompt_tokens_estimated"] / meta["day2"]["max_prompt_tokens_estimated"]
            print(f"  M3 day2 max est {meta['day2']['max_prompt_tokens_estimated']} (api "
                  f"{meta['day2']['max_prompt_tokens_counted_by_api']}), day3 max est "
                  f"{meta['day3']['max_prompt_tokens_estimated']} (api {meta['day3']['max_prompt_tokens_counted_by_api']}),"
                  f" ratio {r:.3f}")
        return
    seed = int(sys.argv[2])
    tr, meta, story = load(seed)
    if cmd == "night":
        night = tr["night" if sys.argv[3] == "1" else "night2"]
        print("house", night["house"], round(night["house_u"], 3) if night["house_u"] is not None else None,
              "left", night["house_left"], "shelf", night["portions_before"], "->", night["portions_after"],
              "away", night["away"])
        print("bedtime hunger", {k: (None if v is None else round(v, 3)) for k, v in night["bedtime_hunger"].items()})
        print("morning hunger", {k: (None if v is None else round(v, 3)) for k, v in night["morning_hunger"].items()})
        for d in night["decisions"]:
            print(f"DECISION {d['ask']:8} {NAMES[d['person']]:6} where={d['where']} mode={d['mode']} option={d['option']} "
                  f"say={d.get('say')!r} feeling={d.get('feeling')!r} reason={d.get('reason')!r} "
                  f"suspects={d.get('suspects')} angry_at={d.get('angry_at')} note={d.get('grudge_note')} "
                  f"invalid={d.get('invalid')}")
            if d["ask"] != "bedtime":
                print("   now:", " / ".join(d["now"][-2:]))
        for n in night["noticing"]:
            print("NOTICE", n)
        for g in night["groups"]:
            print("GROUP", g)
        for p, lines in night["lines"].items():
            print("LINES", NAMES[p], lines)
    elif cmd == "mind":
        k = int(sys.argv[3])
        prompts = mind_prompts(seed)
        res = tr[f"mind{k}"]
        for pid, r in res.items():
            prompt, shown, api_tokens = prompts.get(pid, {}).get(k, (None, {}, None))
            n_rec = sum(1 for x in (prompt or "").split("\n") if re.match(r"^\[[DN]\d-\d+\]", x))
            n_early = sum(1 for x in (prompt or "").split("\n") if x.startswith("- ["))
            print(f"== {NAMES[pid]}: mode {r['mode']} invalid {r['invalid']}; prompt {r['prompt_tokens']} est, "
                  f"{api_tokens} api; {n_rec} records, {n_early} earlier lines")
            print(f"   feeling {r['feeling']!r} ({r['feeling_verdict']}); intent {r['intent']!r} ({r['intent_verdict']})")
            ans = json.loads(r["answer"]) if r["answer"] else {}
            if r["intent"] is None:
                print(f"   intent as answered: {ans.get('intent')!r}")
            for m in r["memories"]:
                print(f"   MEMORY {m['ids']} {m['meaning']!r} -> {m['verdict']}")
                for i in m["ids"] or []:
                    print(f"      [{i}] {shown.get(i, '(not shown)')}")
            if sys.argv[4:] == ["prompt"]:
                print(prompt)
    elif cmd == "acts":
        d = int(sys.argv[3])
        rows = model_acts(tr, story, d)
        print(f"unmatched: {sum(not r['matched'] for r in rows)} of {len(rows)}")
        for r in rows:
            print(f"| {r['minute']:02d} | {NAMES[r['who']]} | {ROOMS[r['room']]} | `{r['option']}` | {cell(r['words'])} | "
                  f"{cell(r['feeling'])} | {cell(r['reason'])} | {r['mode']} |")
    elif cmd == "never":
        d = int(sys.argv[3])
        day = tr[f"day{d}"]
        rows = model_acts(tr, story, d)
        print("fallbacks:", sum(r["mode"] == "fallback" for r in rows))
        kinds = {}
        for r in rows:
            k = re.sub(r"_(daniel|elena|leo|mara)$", "", r["option"])
            kinds.setdefault(r["who"], []).append((r["minute"], k))
        for who, ks in kinds.items():
            print(NAMES[who], [f"{m:02d}:{k}" for m, k in ks])
        spoke = sorted({t["minute"] for t in day["turns"] for a in t["acts"] if a["words"]})
        print("minutes with a spoken line:", spoke)
        print("convo_log:", [(c["minute"], c["room"], c["what"], c["why"]) for c in day["convo_log"]])
        print("final rooms:", day["final_rooms"], "away:", day["away"])
        for turn in day["turns"]:
            for a in turn["acts"]:
                if a["option"].startswith(("sit_", "search", "keep_searching", "eat", "share", "give_", "refuse_given",
                                           "go_", "aside", "accept", "refuse_aside", "move")) or a.get("moved_to"):
                    print("ACT", turn["minute"], a["who"], a["option"], a["mode"], a["room"], a.get("moved_to"))
        # N9's (b): the feelings of model decisions, by minute, to check which show
        print("feelings:", [(r["minute"], r["who"], r["option"], r["feeling"]) for r in rows if r["option"] == "silent"
                            or r["mode"] != "model"][:80])
        for line in story[story.index(TITLE[d]):].split("\n"):
            if line.startswith("## At the end"):
                break
    elif cmd == "screen":
        rows = model_acts(tr, story, 3)
        for r in rows:
            text = (r["words"] or "") + " || " + (r["reason"] or "")
            if M1.search(text):
                hits = sorted({h.lower() for h in M1.findall(text)})
                print(f"{r['minute']:02d} {NAMES[r['who']]:6} {r['option']:18} {r['words']!r} | {r['reason']!r} {hits}")
    elif cmd == "blocks":
        part = story[story.index(TITLE[3]):]
        print(part[part.index("## What each of them carried in"):part.index("## The morning")])
    elif cmd == "convo":
        d = int(sys.argv[3])
        day = tr[f"day{d}"]
        log = day["convo_log"]
        print("convo_log:", [(c["minute"], c["room"], c["what"], c["why"]) for c in log])
        spans, start = [], None
        for c in log:
            if c["room"] != "kitchen":
                continue
            if c["what"] == "started":
                start = c["minute"]
            elif c["what"] == "ended" and start is not None:
                spans.append((start, c["minute"]))
                start = None
        if start is not None:
            spans.append((start, 90))
        for a, b in spans:
            acts = [(t["minute"], x) for t in day["turns"] if a <= t["minute"] < b for x in t["acts"]
                    if x["room"] == "kitchen" and x["words"]]
            speakers = {}
            aimed = {}
            for _, x in acts:
                speakers[x["who"]] = speakers.get(x["who"], 0) + 1
                m = re.search(r"_(daniel|elena|leo|mara)$", x["option"])
                if m:
                    aimed[m.group(1)] = aimed.get(m.group(1), 0) + 1
            kinds = {}
            for _, x in acts:
                kinds.setdefault(x["who"], []).append(x["option"])
            print(f"kitchen conversation {a:02d}-{b:02d}: {len(acts)} spoken lines; speakers {speakers}; aimed at {aimed}")
            for who, ks in kinds.items():
                print(f"   {NAMES[who]}: {ks}")
    elif cmd == "echoes":
        for k, d in ((1, 2), (2, 3)):
            rows = model_acts(tr, story, d)
            for pid, r in tr[f"mind{k}"].items():
                kept = [m for m in r["memories"] if m["verdict"] == "kept"]
                print(f"== mind {k} {NAMES[pid]}: intent {r['intent']!r}; feeling {r['feeling']!r}")
                for m in kept:
                    print(f"   KEPT {m['ids']} {m['meaning']!r}")
                for x in rows:
                    if x["who"] == pid:
                        print(f"   day{d} {x['minute']:02d} {x['option']:18} {x['words']!r} | {x['reason']!r}")
    elif cmd == "grudges":
        d = int(sys.argv[3])
        part = story[story.index(TITLE[d]):]
        nxt = part.find("\n# ", 1)
        part = part[:nxt if nxt > 0 else None]
        minute = None
        for line in part.split("\n"):
            m = re.match(r"^\*\*min (\d\d)\*\*", line)
            if m:
                minute = m.group(1)
            m = re.match(r"^- \*\*(\w+)\*\*", line)
            g = re.search(r"Angry at: ([^.]*?(?:fell|dropped|rose|stays)[^.]*)\.", line)
            if m and g:
                print(minute, m.group(1), g.group(1))
        i = part.find("| Grudges")
        print(part[i:part.find("\n", i)])
    elif cmd == "objects":
        d = int(sys.argv[3])
        hits = {}
        for t in tr[f"day{d}"]["turns"]:
            for a in t["acts"]:
                for w in OBJ.findall(a["words"] or ""):
                    hits.setdefault(w.lower(), []).append(f"{t['minute']:02d} {a['who']}")
        print("object words:", hits)
        for t in tr[f"day{d}"]["turns"]:
            speakers = [(a["who"], a["option"]) for a in t["acts"] if a["words"]]
            if len(speakers) >= 3:
                print(f"  N10 candidate min {t['minute']:02d}: {speakers}")


if __name__ == "__main__":
    main()
