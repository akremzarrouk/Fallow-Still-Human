"""Model probe (reports/model_probe.md): can a stronger free model answer the 17 prompts the play
session of 2026-10-14T22:50:37Z sent? Reads the prompts from cache/play; changes nothing else.

    python model_probe.py probe MODEL [MODEL ...]       one minimal request each, no retry
    python model_probe.py run MODEL [--first N]         the cached prompts, once each, in order
    python model_probe.py table MODEL [MODEL ...]       the side-by-side table, as markdown, on stdout

Same settings as GeminiClient.generate (system, schema, temperature, seed 2, max_output_tokens).
Raw answers go to runs/model_probe/<model>/NN.json. Every request is counted in
runs/model_probe/requests.jsonl, whose line count is the cap (40). Never prints the key.
"""
import json
import os
import sys
import time

from gemini import RESPONSE_SCHEMA, require_api_key
from world import SYSTEM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "runs", "model_probe")
CACHE = os.path.join(HERE, "cache", "play", "gemini-3.5-flash-lite-daniel_ate_it-seed2.json")
CAP = 40
SEED = 2
GAP = 7.0           # seconds between requests: under every per-minute limit the earlier reports met


def session_prompts():
    """The 17 prompts of the session: the last 17 entries of the cache, in the order they were stored."""
    with open(CACHE, encoding="utf-8") as f:
        entries = json.load(f)
    return list(entries.values())[-17:]


def used():
    path = os.path.join(OUT, "requests.jsonl")
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def log_request(row):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "requests.jsonl"), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def send(client, types, errors, model, prompt, kind, n):
    """One request, no retry. Returns the record that was saved."""
    if used() >= CAP:
        sys.exit(f"cap of {CAP} requests reached; nothing sent")
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM, temperature=1.0, seed=SEED,
        response_mime_type="application/json", response_schema=RESPONSE_SCHEMA,
        max_output_tokens=2048,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = {"model": model, "kind": kind, "n": n, "utc": started}
    try:
        r = client.models.generate_content(model=model, contents=prompt, config=config)
        u = r.usage_metadata
        rec.update(ok=True, text=r.text or "",
                   finish=str(r.candidates[0].finish_reason) if r.candidates else None,
                   prompt_tokens=getattr(u, "prompt_token_count", None),
                   answer_tokens=getattr(u, "candidates_token_count", None),
                   thought_tokens=getattr(u, "thoughts_token_count", None))
    except errors.APIError as e:
        rec.update(ok=False, code=e.code, status=e.status, message=e.message, details=str(e.details))
    except Exception as e:         # not an API error: record it, send nothing more
        rec.update(ok=False, code=None, status=type(e).__name__, message=str(e), details="")
    log_request({k: rec[k] for k in ("model", "kind", "n", "utc", "ok")})
    return rec


# The situation of each of the 17 asks, in one line (from "Now, minute .." and "Said and done .." of the prompt).
SITUATIONS = [
    "Opening: first to act, nobody has spoken; Daniel, Leo, Mara at the pantry; 2 portions",
    "Elena has just asked everyone who took the can",
    "Elena asked who took it; Mara has just denied it",
    "Everyone has denied it or spoken; she is the first to act again",
    "Elena has just said nobody is accusing anyone; Mara has denied once",
    "Elena reassured everyone, Leo stayed silent, Mara asked who took it; he denied once",
    "Daniel stayed silent; she has asked who took it once",
    "Mara has just said someone must know where it went; Daniel silent",
    "She has asked who took it twice; first to act this turn",
    "Mara is searching the kitchen; Leo has just accused her (Elena) of eating it at night",
    "Leo has just accused Elena; Elena has just denied it and looks hurt; Mara searching",
    "Leo has just said \"Only mom did not deny it\"; she has denied once",
    "Leo said \"Only mom did not deny it\"; Elena denied it again and looks hurt; Mara had been searching",
    "Leo, Elena (hurt) and Mara have just spoken; he accused someone last turn",
    "Daniel has just admitted taking it; she is first to act; she had denied twice",
    "Elena has just said \"Thank you for telling the truth\" to him",
    "Elena thanked Daniel, Daniel told Elena he has it under control",
]


def table(models):
    rows = session_prompts()
    heads = ["flash-lite (the session)"] + models
    out = ["| # | who | min | situation | " + " | ".join(heads) + " |",
           "|---|---|---|---|" + "---|" * len(heads)]
    minutes = [0, 0, 0, 3, 3, 3, 6, 6, 9, 9, 9, 12, 12, 12, 15, 15, 15]
    for n in range(1, 18):
        prompt = rows[n - 1]["prompt"]
        who = prompt.split(",")[0].replace("You are ", "")
        cells = []
        a = json.loads(rows[n - 1]["response"])
        cells.append(f"**{a['option']}**: {a['say'] or '(none)'}")
        for m in models:
            path = os.path.join(OUT, m, f"{n:02d}.json")
            if not os.path.exists(path):
                cells.append("(no answer)")
                continue
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
            b = json.loads(rec["text"])
            cells.append(f"**{b['option']}**: {b['say'] or '(none)'}")
        out.append(f"| {n} | {who} | {minutes[n - 1]:02d} | {SITUATIONS[n - 1]} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    mode = sys.argv[1]
    if mode == "table":
        print(table(sys.argv[2:]))
        return
    models = [a for a in sys.argv[2:] if not a.startswith("--") and not a.replace(".", "").isdigit()]
    from google import genai
    from google.genai import errors, types
    client = genai.Client(api_key=require_api_key())
    if mode == "probe":
        for model in models:
            prompt = ('Options:\n- stay: (speech) You say nothing and stay.\nChoose "stay" and say "Hello".')
            rec = send(client, types, errors, model, prompt, "probe", 0)
            d = os.path.join(OUT, model)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "probe.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            print(model, "->", "answered" if rec["ok"] else f"refused {rec['code']} {rec['status']}")
            time.sleep(GAP)
    elif mode == "run":
        model = models[0]
        first = int(sys.argv[sys.argv.index("--first") + 1]) if "--first" in sys.argv else 17
        if "--wait" in sys.argv:
            time.sleep(float(sys.argv[sys.argv.index("--wait") + 1]))
        prompts = session_prompts()
        d = os.path.join(OUT, model)
        os.makedirs(d, exist_ok=True)
        for n in range(1, first + 1):
            path = os.path.join(d, f"{n:02d}.json")
            if os.path.exists(path):        # a prompt that has an answer is never asked again
                continue
            rec = send(client, types, errors, model, prompts[n - 1]["prompt"], "ask", n)
            if not rec["ok"]:               # a refusal is kept apart; the prompt is still unanswered
                path = os.path.join(d, f"{n:02d}.refused.json")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            print(n, "ok" if rec["ok"] else f"refused {rec['code']} {rec['status']}", flush=True)
            if not rec["ok"]:
                print("  stopped:", rec["message"][:300])
                break
            time.sleep(GAP)


if __name__ == "__main__":
    main()
