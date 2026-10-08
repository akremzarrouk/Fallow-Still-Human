"""No API: runs/v22/run_capped.py's cap with a stub in place of the real generate, cap 3."""
import importlib.util, os, sys
sys.path.insert(0, os.getcwd())
assert not os.environ.get("GEMINI_API_KEY")
import gemini
sent = []
gemini.GeminiClient.generate = lambda self, system, prompt, schema=None: sent.append(prompt) or "ok"
spec = importlib.util.spec_from_file_location("run_capped", "runs/v22/run_capped.py")
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
print("CAP in the file:", rc.CAP, "| ARGS:", rc.ARGS)
rc.install(cap=3)
c = object.__new__(gemini.GeminiClient)
try:
    for i in range(5):
        c.generate("s", f"p{i}")
except gemini.CallCapReached as e:
    print("cap raised:", e, "| requests sent to api:", len(sent), "| counter:", rc.state["sent"])
