"""Part 4 of reports/v22_gaps.md (read only, no API): the sections of the largest v22 prompt (day 9, Daniel, 2602) with their
estimates, and which sit outside the trimming budget. A no-API replay of a temp copy of cache/v22, with prompt_parts
wrapped to record the exact `block` (the characters estimate_tokens is told not to count)."""
import os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import data, gemini, morning, world
from talk import act_of

SC = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11): SC += [f"night{k-1}", f"mind{k-1}", f"day{k}"]
tmp = tempfile.mkdtemp(); n = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
shutil.copy(os.path.join("cache", "v22", n), os.path.join(tmp, n))
st = {"scene": 0, "less": None, "calls": []}; rec = []
orig_new, orig_parts, orig_est = gemini.Oracle.new_scene, world.Morning.prompt_parts, world.estimate_tokens
def new_scene(self):
    st["scene"] += 1; return orig_new(self)
def est(text, less=0):
    st["calls"].append(less); return orig_est(text, less)
def parts(self, p, opts, head, now, system, when, minute):
    st["calls"] = []
    text = orig_parts(self, p, opts, head, now, system, when, minute)
    loop_less = st["calls"][-2] if len(st["calls"]) >= 2 else st["calls"][-1]   # the last call is max_prompt_tokens's, with no `less`
    block_parts = {}
    tail = ["Your options:"] + [f"- {o.id}: {'(speech) ' if o.speech else ''}{o.label}" for o in opts]
    keep = p.trip_memories if self.trip else set()
    if self.trip:
        house = head[-1][len(f"The house: {data.HOUSE} "):]
        block_parts["trip lines"] = sum(len(x) + 1 for x in self.trip_lines(p))
        block_parts["trip options"] = sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if act_of(o.id)[0] in world.TRIP_KINDS)
        block_parts["kept day-2 memories"] = sum(len(f"- {x}") + 1 for x in keep)
        block_parts["house line beyond HOUSE_THINGS"] = max(0, len(house) - len(data.HOUSE_THINGS))
    block_parts["carry"] = sum(len(x) + 1 for x in self.carry.get(p.id, []))
    if self.quiet is not None:
        block_parts["W1 water line + rain Now line"] = sum(len(x) + 1 for x in head + now if x.startswith("About water:") or x in world.W1_NOW)
        block_parts["W1 options (save/ration/collect)"] = sum(len(x) + 1 for o, x in zip(opts, tail[1:]) if o.id in world.W1_OPTIONS)
        if not self.trip:
            block_parts["yard"] = len(data.YARD[1]) - len(data.YARD[0])
    rec.append({"scene": SC[min(st["scene"], len(SC) - 1)], "who": p.id, "text": text, "system": system, "less": loop_less,
                "block_parts": block_parts, "estimate": orig_est(system + text)})
    return text
gemini.Oracle.new_scene, world.Morning.prompt_parts, world.estimate_tokens = new_scene, parts, est
try:
    morning.run(2, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True, days=10)
finally:
    gemini.Oracle.new_scene, world.Morning.prompt_parts, world.estimate_tokens = orig_new, orig_parts, orig_est
    shutil.rmtree(tmp)
r = max((x for x in rec if x["scene"] == "day9"), key=lambda x: x["estimate"])
print(f"largest day/night prompt: scene {r['scene']}, {r['who']}, estimate {r['estimate']}; `block` passed to estimate_tokens {r['less']} characters "
      f"= {r['less']/3.6:.0f} tokens; counted against the budget: {orig_est(r['system'] + r['text'], r['less'])} (PROMPT_TOKEN_BUDGET {world.PROMPT_TOKEN_BUDGET})")
print("outside the budget (summing to block): " + str(r["block_parts"]) + f"  = {sum(r['block_parts'].values())} characters")
open("runs/v22gaps/day9_daniel_2602_prompt.txt", "w", encoding="utf-8", newline="\n").write(r["text"])

# the sections
sections = []; cur = None
for l in r["text"].splitlines():
    if l.startswith("- ") and cur is not None and cur["head"] not in ("Your options:",) or (l.startswith("- ") and cur is not None):
        cur["lines"].append(l)
    else:
        cur = {"head": l, "lines": []}; sections.append(cur)
def toks(chars): return chars / 3.6
bp = r["block_parts"]
OUT = {"About food:": "outside (trip lines)", "About the neighbour's house:": "outside (trip lines)", "About the street:": "outside (trip lines)",
       "About going out at night:": "outside (trip lines)", "About going there tonight:": "outside (trip lines)",
       "About water:": "outside (W1 water line)", "What stays with you": "outside (carry: memory block C)",
       "Yesterday and last night:": "outside (carry: memory block A)", "What yesterday left in you": "outside (carry: memory block B)"}
print()
print(f"system prompt: {len(r['system'])} chars = {toks(len(r['system'])):.0f} tokens (world.SYSTEM), counted in the budget, not trimmable")
print(f"prompt: {len(r['text'])} chars = {toks(len(r['text'])):.0f} tokens; system + prompt = {orig_est(r['system'] + r['text'])}")
print()
print("%-6s %-6s  %s" % ("chars", "tokens", "section (status)"))
for s_ in sections:
    chars = sum(len(x) + 1 for x in [s_["head"]] + s_["lines"])
    h = s_["head"]; status = "inside, not trimmable"
    for key, val in OUT.items():
        if h.startswith(key): status = val
    if h.startswith("The house:"): status = f"inside, not trimmable; {bp['house line beyond HOUSE_THINGS']} chars of it outside (trip)"
    if h.startswith("What you remember from the days before"): status = f"inside, trimmable; {bp['kept day-2 memories']} chars of it outside (kept memories)"
    if h.startswith("What else happened"): status = "inside, trimmable (oldest cut first)"
    if h.startswith("Your options"): status = f"inside; {bp['trip options'] + bp['W1 options (save/ration/collect)']} chars of it outside (trip + W1 options)"
    print("%-6d %-6.0f  %s  [%s]%s" % (chars, toks(chars), h[:62], status, f"  (+{len(s_['lines'])} lines)" if s_["lines"] else ""))
print()
print(f"`block` (outside the budget): {r['less']} chars = {toks(r['less']):.0f} tokens; counted against PROMPT_TOKEN_BUDGET: "
      f"{orig_est(r['system'] + r['text'], r['less'])} <= {world.PROMPT_TOKEN_BUDGET}")
print("parts of `block`, chars / tokens:")
for k, v in bp.items(): print(f"   {k:<38} {v:>5} / {toks(v):.0f}")
