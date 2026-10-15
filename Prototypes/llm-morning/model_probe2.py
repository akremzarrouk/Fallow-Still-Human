"""Model probe 2 (reports/model_probe_play2.md): the same 17 prompts of the play session, same settings,
once each, to more models. Reuses model_probe.py for the prompts and the request settings; changes nothing else.

    python model_probe2.py run MODEL [MODEL ...]     in the order given, each until 17 answers or its stop
    python model_probe2.py table MODEL [MODEL ...]   the side-by-side table (flash-lite and the models), markdown on stdout

A 500 or 503 is waited out (RETRY_WAIT seconds) and the same prompt sent again, at most 3 times; a prompt
refused 4 times stops its model. A 429, or any other error, stops its model at once, the message kept verbatim.
Every request, answered or not, is one line of runs/model_probe/requests2.jsonl (the cap: 80 in all);
requests.jsonl, the first probe's log, is not touched. Raw answers: runs/model_probe/<model>/NN.json.
"""
import json
import os
import sys
import time

import model_probe as mp

CAP2 = 80
RETRIES = 3
RETRY_WAIT = 60.0
TIMEOUT_MS = 120000     # a call with no answer in 2 minutes is dropped and counts as a refusal (the first run hung 43 min without one)
LOG2 = os.path.join(mp.OUT, "requests2.jsonl")


def used2():
    if not os.path.exists(LOG2):
        return 0
    with open(LOG2, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def request(client, types, errors, model, prompt, n):
    """One request. Returns the record: ok, text and counts, or the error verbatim; `seconds` is the time the call took."""
    if used2() >= CAP2:
        sys.exit(f"cap of {CAP2} requests reached; nothing sent")
    config = types.GenerateContentConfig(
        system_instruction=mp.SYSTEM, temperature=1.0, seed=mp.SEED,
        response_mime_type="application/json", response_schema=mp.RESPONSE_SCHEMA,
        max_output_tokens=2048,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        http_options=types.HttpOptions(timeout=TIMEOUT_MS))
    rec = {"model": model, "kind": "ask", "n": n, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t0 = time.monotonic()
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
    except Exception as e:
        rec.update(ok=False, code=None, status=type(e).__name__, message=str(e), details="")
    rec["seconds"] = round(time.monotonic() - t0, 2)
    os.makedirs(mp.OUT, exist_ok=True)
    with open(LOG2, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({k: rec[k] for k in ("model", "n", "utc", "ok", "seconds")}
                           | ({} if rec["ok"] else {"code": rec["code"], "status": rec["status"]}),
                           ensure_ascii=False) + "\n")
    return rec


def save(path, rec):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)


def run_model(client, types, errors, model, prompts, prior=0):
    """prior: attempts already made, unlogged or logged by an earlier process, on the first unanswered prompt."""
    d = os.path.join(mp.OUT, model)
    os.makedirs(d, exist_ok=True)
    answered = 0
    for n in range(1, 18):
        path = os.path.join(d, f"{n:02d}.json")
        if os.path.exists(path):
            answered += 1
            continue
        refused = []
        first_attempt, prior = prior, 0
        for attempt in range(first_attempt, RETRIES + 1):
            rec = request(client, types, errors, model, prompts[n - 1]["prompt"], n)
            if rec["ok"]:
                break
            refused.append(rec)
            print(f"{model} {n} attempt {attempt + 1}: {rec['code']} {rec['status']}", flush=True)
            if rec["code"] not in (500, 503, 504) and rec["status"] != "TimeoutError" and "imeout" not in rec["status"]                     or attempt == RETRIES:
                break
            time.sleep(RETRY_WAIT)
        if rec["ok"]:
            rec["refusals_before"] = [{"code": r["code"], "status": r["status"], "message": r["message"],
                                       "utc": r["utc"], "seconds": r["seconds"]} for r in refused]
            save(path, rec)
            answered += 1
            print(f"{model} {n} ok {rec['seconds']}s", flush=True)
            time.sleep(mp.GAP)
        else:
            save(os.path.join(d, f"{n:02d}.refused2.json"), {"model": model, "n": n, "attempts": refused})
            print(f"{model} stopped at ask {n} after {answered} answers: {rec['code']} {rec['status']}: "
                  f"{rec['message']}", flush=True)
            return answered
    return answered


def table(models):
    rows = mp.session_prompts()
    heads = ["flash-lite (the session)"] + models
    out = ["| # | who | min | situation | " + " | ".join(heads) + " |",
           "|---|---|---|---|" + "---|" * len(heads)]
    minutes = [0, 0, 0, 3, 3, 3, 6, 6, 9, 9, 9, 12, 12, 12, 15, 15, 15]
    for n in range(1, 18):
        prompt = rows[n - 1]["prompt"]
        who = prompt.split(",")[0].replace("You are ", "")
        a = json.loads(rows[n - 1]["response"])
        cells = [f"**{a['option']}**: {a['say'] or '(none)'}"]
        for m in models:
            path = os.path.join(mp.OUT, m, f"{n:02d}.json")
            if not os.path.exists(path):
                cells.append("(no answer)")
                continue
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
            try:
                b = json.loads(rec["text"])
                cells.append(f"**{b['option']}**: {b['say'] or '(none)'}")
            except (ValueError, KeyError, TypeError):
                cells.append("(not a valid answer: " + rec["text"][:80].replace("|", "/").replace("\n", " ") + ")")
        out.append(f"| {n} | {who} | {minutes[n - 1]:02d} | {mp.SITUATIONS[n - 1]} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    mode, models = sys.argv[1], sys.argv[2:]
    prior = 0
    if "--prior" in models:
        i = models.index("--prior")
        prior = int(models[i + 1])
        del models[i:i + 2]
    if mode == "table":
        print(table(models))
        return
    from google import genai
    from google.genai import errors, types
    client = genai.Client(api_key=mp.require_api_key())
    prompts = mp.session_prompts()
    for model in models:
        got = run_model(client, types, errors, model, prompts, prior)
        prior = 0
        print(f"{model}: {got} of 17 answered; {used2()} requests used in all", flush=True)


if __name__ == "__main__":
    main()
