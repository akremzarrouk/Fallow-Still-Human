"""No API: which rule moves the v16 cache? Runs the no-API prefix replay of v16 seed 2 (days 1-2, nights 1-2, minds 1-2)
with each rule switched off in turn, and reports whether every ask is still answered from the cache."""
import os, shutil, sys, tempfile
sys.path.insert(0, os.getcwd()); assert not os.environ.get("GEMINI_API_KEY")
import gemini, morning, mind, world

def prefix(label, patch):
    tmp = tempfile.mkdtemp(); n = "gemini-3.5-flash-lite-daniel_ate_it-seed2.json"
    shutil.copy(os.path.join("cache", "v16", n), os.path.join(tmp, n))
    miss = {}
    orig = gemini.Oracle.ask; state = {"scene": 0}; on = gemini.Oracle.new_scene
    def new_scene(self): state["scene"] += 1; return on(self)
    def ask(self, system, prompt, schema=None):
        try: return orig(self, system, prompt, schema)
        except gemini.CacheMiss:
            miss.setdefault("first", (state["scene"], prompt.split(",")[0])); raise
    gemini.Oracle.ask, gemini.Oracle.new_scene = ask, new_scene
    undo = patch()
    try:
        # days=2: days 1-2 with their nights and minds; day 3 is made but not played
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            try: morning.run(2, replay=True, runs_dir=os.path.join(tmp, "r"), cache_dir=tmp, quiet=True, days=2)
            except SystemExit: pass
            except Exception as e: miss.setdefault("exc", repr(e)[:80])
    finally:
        undo(); gemini.Oracle.ask, gemini.Oracle.new_scene = orig, on; shutil.rmtree(tmp)
    print(f"{label:<44} first cache miss: {miss.get('first')}  {miss.get('exc', '')}")

def noop():
    return lambda: None
def no_rule1():
    o = mind.quotes_own_words; mind.quotes_own_words = lambda *a, **k: False
    return lambda: setattr(mind, "quotes_own_words", o)
def no_rule2():
    o = world.INTENT_LINE; world.INTENT_LINE = "\0never"
    return lambda: setattr(world, "INTENT_LINE", o)
def neither():
    u1, u2 = no_rule1(), no_rule2()
    return lambda: (u1(), u2())
prefix("both rules on", noop)
prefix("rule 1 off", no_rule1)
prefix("rule 2 off", no_rule2)
prefix("both off", neither)
