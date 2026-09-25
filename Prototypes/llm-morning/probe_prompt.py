"""Replays a morning from its cache to the first prompt that has no answer, and sends that
prompt once to the model with a given seed. For telling a busy server from a prompt the
server always refuses. Prints the outcome; never the key.

    python probe_prompt.py <cache file> <scenario> <run seed> <model> <probe seed>
"""
import sys

from gemini import RESPONSE_SCHEMA, Cache, CacheMiss, Oracle, require_api_key
from world import SYSTEM, Morning


class Catch(Oracle):
    def ask(self, system, prompt):
        try:
            return super().ask(system, prompt)
        except CacheMiss:
            self.missing = prompt
            raise


def main():
    path, scenario, run_seed, model, probe_seed = sys.argv[1:6]
    oracle = Catch(Cache(path), model, int(run_seed), replay=True)
    m = Morning(oracle, int(run_seed), scenario)
    try:
        for t in range(m.turns):
            m.turn(t)
        print("every prompt has an answer")
        return 0
    except CacheMiss:
        pass
    prompt = oracle.missing
    print(f"first unanswered prompt: {prompt.splitlines()[0][:60]}... "
          f"({[l for l in prompt.splitlines() if l.startswith('Now, minute')][0]})")
    from google import genai
    from google.genai import errors, types
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM, temperature=1.0, seed=int(probe_seed), max_output_tokens=2048,
        response_mime_type="application/json", response_schema=RESPONSE_SCHEMA,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    try:
        client = genai.Client(api_key=require_api_key())
        r = client.models.generate_content(model=model, contents=prompt, config=config)
        print(f"seed {probe_seed}: accepted: {r.text}")
    except errors.APIError as e:
        print(f"seed {probe_seed}: refused: {e.code} {e.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
