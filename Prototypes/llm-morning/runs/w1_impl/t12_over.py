"""reports/w1_impl.md: the day and night prompts of the fake runs of test_t12 (seeds 1-3, to day 3) whose estimate
without their blocks is 1400 or more: size, kind, who, the W1 lines in it, and whether it was trimmed."""
import sys
sys.path.insert(0, ".")
import test_morning as T
import world
from world import SYSTEM, estimate_tokens

dirs = T.Dirs()
for seed in (1, 2, 3):
    (_, code), out = T.fake_morning(dirs, seed=seed)
    assert code == 0
for p in T.cached_prompts(dirs):
    night = "\nNow it is night" in p
    if night or T.CARRY_HEAD in p:
        n = estimate_tokens((world.NIGHT_SYSTEM if night else SYSTEM) + T.without_blocks(p))
        if n >= 1400:
            water = [x for x in p.splitlines() if x.startswith(("About water", "Your body"))]
            print(n, "night" if night else "day", p[:40].replace("\n", " "), "|",
                  estimate_tokens("\n".join(water)), "| cut" if "(earlier things, left out here)" in p else "")
dirs.cleanup()
