"""No API: replays v22 seed 2 (a temp copy of cache/v22, days=10) on the changed code and names the first prompt the
cache has no answer for, the cached v22 prompt that was asked at that place, and the first lines that differ. Then the
same with each rule switched off, to say which rule causes which miss. Run with GEMINI_API_KEY unset."""
import difflib, io, contextlib, json, os, re, shutil, sys, tempfile
sys.path.insert(0, os.getcwd()); assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning, mind, world, quiet

NAME = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
SRC = os.path.join("cache", "v22", NAME)
CACHED = json.load(open(SRC, encoding="utf-8"))
LIVE = [CACHED[k]["prompt"] for k in list(CACHED)[147:]]       # the 402 live prompts, in the order they were asked
SCENES = ["day1", "night1", "mind1", "day2", "night2", "mind2", "day3"]
for k in range(4, 11): SCENES += [f"night{k-1}", f"mind{k-1}", f"day{k}"]

def replay(label, rule1=True, rule2=True, rule3=True, show=True):
    tmp = tempfile.mkdtemp(); shutil.copy(SRC, os.path.join(tmp, NAME))
    undo = []
    if not rule1:
        o = mind.quotes_own_words; mind.quotes_own_words = lambda *a, **k: False; undo.append(lambda o=o: setattr(mind, "quotes_own_words", o))
    if not rule2:
        o = world.INTENT_LINE; world.INTENT_LINE = "\0never"; undo.append(lambda o=o: setattr(world, "INTENT_LINE", o))
    if not rule3:
        o = world.Morning.rain_action     # off = Q6 as it was: hear_rain is told an action exists; the options are as they are
        def faked(p, _o=o):
            f = sys._getframe(1)
            while f:
                if f.f_code.co_name == "hear_rain":
                    return True
                f = f.f_back
            return _o(p)
        world.Morning.rain_action = staticmethod(faked); undo.append(lambda o=o: setattr(world.Morning, "rain_action", staticmethod(o)))
    st = {"scene": 0, "asks": 0, "miss": None}
    orig, on = gemini.Oracle.ask, gemini.Oracle.new_scene
    def new_scene(self):
        st["scene"] += 1; return on(self)
    def ask(self, system, prompt, schema=None):
        try:
            r = orig(self, system, prompt, schema); st["asks"] += 1; return r
        except gemini.CacheMiss:
            st["miss"] = (SCENES[min(st["scene"], len(SCENES) - 1)], st["asks"], system, prompt); raise
    gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            morning.run(2, replay=True, runs_dir=os.path.join(tmp, "runs"), cache_dir=tmp, quiet=True, days=10)
    except BaseException as e:
        st["exc"] = type(e).__name__
    finally:
        gemini.Oracle.ask, gemini.Oracle.new_scene = orig, on
        for u in undo: u()
        shutil.rmtree(tmp)
    m = st["miss"]
    if not m:
        print(f"[{label}] no cache miss: {st['asks']} asks answered from cache; ended with {st.get('exc', 'the run finishing')}"); return
    scene, n, system, prompt = m
    expected = LIVE[n - 96] if n >= 96 else None
    who = re.match(r"You are (\w+),", prompt)
    now = [l for l in prompt.splitlines() if l.startswith("Now")][:1]
    print(f"[{label}] FIRST MISS at ask {n} (live ask {n - 96}), scene {scene}, {who.group(1) if who else '?'}; {now}")
    if show and expected:
        d = [l for l in difflib.unified_diff(expected.splitlines(), prompt.splitlines(), "cached v22 prompt", "prompt now", lineterm="", n=0)
             if not l.startswith("@@")]
        for l in d[:14]: print("      " + l[:230])
        print(f"      ({len(d) - 2} differing lines in all)")
replay("all three rules on")
replay("rule 2 off", rule2=False)
replay("rules 2 and 3 off (rule 1 only)", rule2=False, rule3=False)
replay("rules 1 and 2 off (rule 3 only)", rule1=False, rule2=False)
replay("rules 1 and 3 off (rule 2 only)", rule1=False, rule3=False)
replay("all three off (the check: v22 as it ran)", False, False, False, show=False)
