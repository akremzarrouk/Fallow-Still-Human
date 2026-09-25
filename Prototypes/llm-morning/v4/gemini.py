"""Where a decision's raw text comes from: the Gemini API, a fake, or the cache.

Nothing here knows about the morning. A client turns a prompt into text; the
Oracle puts a cache in front of it and, in replay, refuses to reach any client.
"""
import hashlib
import json
import os
import re
import sys
import time


class StopMorning(Exception):
    """Ends a morning cleanly. The message says why and how to go on."""


class DailyQuotaExhausted(StopMorning):
    pass


class RateLimited(StopMorning):
    pass


class CallCapReached(StopMorning):
    pass


class CacheMiss(StopMorning):
    pass


def require_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        sys.exit("GEMINI_API_KEY is not set. Set it in the environment and run again "
                 "(nothing was called).")
    return key


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "option": {"type": "string"},
        "say": {"type": "string", "nullable": True},
        "feeling": {"type": "string"},
        "reason": {"type": "string"},
        "suspects": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
        "angry_at": {"type": "string", "enum": ["Daniel", "Elena", "Leo", "Mara", "nobody"]},
    },
    "required": ["option", "say", "feeling", "reason", "suspects", "angry_at"],
}


class GeminiClient:
    """Real calls. Spaces them, backs off on 429 and 5xx, counts every request sent."""

    def __init__(self, config, seed, api=None, sleep=time.sleep, clock=time.monotonic):
        from google import genai
        from google.genai import types
        self._types = types
        key = require_api_key()
        self._client = api if api is not None else genai.Client(api_key=key)
        del key
        self.model = config["model"]
        self.seed = seed
        self.temperature = config["temperature"]
        self.min_gap = config["min_seconds_between_calls"]
        self.max_calls = config["max_calls_per_morning"]
        self.max_retries = config["max_retries"]
        self.backoff = config["backoff_base_seconds"]
        self.backoff_max = config["backoff_max_seconds"]
        self.max_output_tokens = config["max_output_tokens"]
        self.requests = 0
        self.last_prompt_tokens = None
        self._sleep = sleep
        self._clock = clock
        self._last = None

    def _space(self):
        if self._last is not None:
            wait = self.min_gap - (self._clock() - self._last)
            if wait > 0:
                self._sleep(wait)
        self._last = self._clock()

    def generate(self, system, prompt):
        from google.genai import errors
        config = self._types.GenerateContentConfig(
            system_instruction=system,
            temperature=self.temperature,
            seed=self.seed,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            max_output_tokens=self.max_output_tokens,
            automatic_function_calling=self._types.AutomaticFunctionCallingConfig(disable=True),
        )
        attempt = 0
        while True:
            if self.requests >= self.max_calls:
                raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
            self._space()
            self.requests += 1
            try:
                response = self._client.models.generate_content(
                    model=self.model, contents=prompt, config=config)
                usage = getattr(response, "usage_metadata", None)
                self.last_prompt_tokens = getattr(usage, "prompt_token_count", None)
                return response.text or ""
            except errors.APIError as e:
                detail = str(e.details)
                if e.code == 429 and re.search(r"PerDay", detail):
                    raise DailyQuotaExhausted("stopped: the daily request quota for this model is used up.")
                retryable = e.code == 429 or (e.code or 0) >= 500
                if not retryable:
                    raise StopMorning(f"stopped: the API refused the request: {e.code} {e.status}: "
                                      f"{e.message}")
                if attempt >= self.max_retries:
                    raise RateLimited(f"stopped: still refused ({e.code} {e.status}) after "
                                      f"{self.max_retries} retries.")
                wait = min(self.backoff * (2 ** attempt), self.backoff_max)
                hinted = re.search(r"retryDelay'?:\s*'(\d+(?:\.\d+)?)s'", detail)
                if hinted:
                    wait = max(wait, float(hinted.group(1)) + 1)
                print(f"    [{e.code} {e.status}] waiting {wait:.0f}s, retry {attempt + 1}/{self.max_retries}",
                      flush=True)
                self._sleep(wait)
                attempt += 1


class FakeClient:
    """Canned answers for building and testing. Reads the option ids back out of the
    prompt and picks one by a hash of the prompt. Every `invalid_every`-th answer is
    broken in one of several ways, in turn, so the fallback path is exercised."""

    BROKEN = ["not json", "unknown option", "missing field", "speech without words"]

    def __init__(self, invalid_every=5, fail_with=None, max_calls=150):
        self.invalid_every = invalid_every
        self.fail_with = fail_with or {}
        self.max_calls = max_calls
        self.requests = 0
        self.model = "fake"

    def generate(self, system, prompt):
        if self.requests >= self.max_calls:
            raise CallCapReached(f"stopped: this morning reached {self.max_calls} API requests.")
        self.requests += 1
        if self.requests in self.fail_with:
            raise self.fail_with[self.requests]
        block = prompt.split("Your options:")[-1]
        options = re.findall(r"^- (\w+):", block, flags=re.M)
        h = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
        pick = options[h % len(options)] if options else "stay"
        speaking = re.search(rf"^- {pick}: \(speech\)", block, flags=re.M) is not None
        answer = {
            "option": pick,
            "say": f"[fake line {self.requests}]" if speaking else None,
            "feeling": ["afraid", "calm", "ashamed", "angry", "tired"][h % 5],
            "reason": f"Fake reason {self.requests}.",
            "suspects": ["Daniel", "Elena", "Leo", "Mara", "nobody"][(h // 7) % 5],
            "angry_at": ["Daniel", "Elena", "Leo", "Mara", "nobody"][(h // 11) % 5],
        }
        if self.invalid_every and self.requests % self.invalid_every == 0:
            kind = self.BROKEN[(self.requests // self.invalid_every - 1) % len(self.BROKEN)]
            if kind == "not json":
                return "I think I would rather say nothing."
            if kind == "unknown option":
                answer["option"] = "fly_away"
            elif kind == "missing field":
                del answer["reason"]
            elif kind == "speech without words":
                answer["option"] = next((o for o in options if re.search(
                    rf"^- {o}: \(speech\)", block, flags=re.M)), "fly_away")
                answer["say"] = None
        return json.dumps(answer)


class Cache:
    """Every answer ever received, keyed by model, seed and the exact prompt."""

    def __init__(self, path):
        self.path = path
        self.entries = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.entries = json.load(f)

    @staticmethod
    def key(model, seed, system, prompt):
        text = "\n\x1e".join([model, str(seed), system, prompt])
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, key):
        entry = self.entries.get(key)
        return entry["response"] if entry else None

    def put(self, key, prompt, response, prompt_tokens=None):
        self.entries[key] = {"prompt": prompt, "response": response, "prompt_tokens": prompt_tokens}
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)


class Oracle:
    """The one door to a model. Cached answers first; in replay, nothing else."""

    def __init__(self, cache, model_name, seed, client=None, replay=False, max_calls=None):
        self.cache = cache
        self.max_calls = max_calls      # for the whole morning, answers already cached included
        self.model_name = model_name
        self.seed = seed
        self.client = client
        self.replay = replay
        self.from_cache = 0
        self.live = 0
        self.prompt_tokens = []     # as counted by the API, where it said

    @property
    def api_requests(self):
        return self.client.requests if self.client else 0

    def ask(self, system, prompt):
        key = Cache.key(self.model_name, self.seed, system, prompt)
        cached = self.cache.get(key)
        if cached is not None:
            self.from_cache += 1
            tokens = self.cache.entries[key].get("prompt_tokens")
            if tokens:
                self.prompt_tokens.append(tokens)
            return cached
        if self.replay or self.client is None:
            raise CacheMiss("stopped: replay found a prompt with no cached answer, so this "
                            "morning cannot be replayed from the cache.")
        if self.max_calls is not None and self.from_cache + self.client.requests >= self.max_calls:
            raise CallCapReached(f"stopped: this morning reached {self.max_calls} model calls "
                                 f"({self.from_cache} of them answered in an earlier run).")
        text = self.client.generate(system, prompt)
        self.live += 1
        tokens = getattr(self.client, "last_prompt_tokens", None)
        if tokens:
            self.prompt_tokens.append(tokens)
        self.cache.put(key, prompt, text, tokens)
        return text
