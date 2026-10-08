"""Runs `python morning.py --seed 2 --out v22 --days 10` with one addition: a 470-ask cap (reports/days_v22_plan.md).

The cap is a counter on GeminiClient.generate. When CAP live asks have been sent, the next one raises
gemini.CallCapReached (a StopMorning) before any request goes out; the run then exits 3 as for any stop. No prompt,
option or answer is changed.

    GEMINI_API_KEY=... python runs/v22/run_capped.py        (from Prototypes/llm-morning/)
"""
import os
import sys

sys.path.insert(0, os.getcwd())
import gemini    # noqa: E402
import morning   # noqa: E402

CAP = 470
ARGS = ["morning.py", "--seed", "2", "--out", "v22", "--days", "10"]
state = {"sent": 0}


def install(cap=CAP):
    orig = gemini.GeminiClient.generate
    state["sent"] = 0

    def generate(self, system, prompt, schema=None):
        if state["sent"] >= cap:
            raise gemini.CallCapReached(f"stopped: the {cap}-ask cap of reports/days_v22_plan.md was reached "
                                        f"({state['sent']} live asks sent).")
        state["sent"] += 1
        return orig(self, system, prompt) if schema is None else orig(self, system, prompt, schema=schema)
    gemini.GeminiClient.generate = generate
    return orig


if __name__ == "__main__":
    install()
    sys.argv = ARGS
    morning.main()
