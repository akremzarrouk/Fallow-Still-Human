"""Sends one real turn-0 prompt to a model with the prototype's exact request settings, to see
what it accepts. Prints the outcome and the token counts; never the key.

    python probe_model.py gemma-4-31b-it [--no-schema] [--no-system]
"""
import sys

from gemini import RESPONSE_SCHEMA, Cache, FakeClient, Oracle, require_api_key
from world import SYSTEM, Morning


def main():
    model = sys.argv[1]
    schema = "--no-schema" not in sys.argv
    system = "--no-system" not in sys.argv
    from google import genai
    from google.genai import errors, types
    m = Morning(Oracle(Cache("probe-unused.json"), "probe", 1, client=FakeClient()), 1)
    daniel = m.people["daniel"]
    prompt = m.prompt_for(daniel, 0, m.options_for(daniel))
    config = dict(temperature=1.0, seed=1, max_output_tokens=2048,
                  automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    if system:
        config["system_instruction"] = SYSTEM
    if schema:
        config.update(response_mime_type="application/json", response_schema=RESPONSE_SCHEMA)
    contents = prompt if system else SYSTEM + "\n\n" + prompt
    client = genai.Client(api_key=require_api_key())
    print(f"model {model}; system instruction {'on' if system else 'off'}; "
          f"JSON schema {'on' if schema else 'off'}")
    try:
        r = client.models.generate_content(model=model, contents=contents,
                                           config=types.GenerateContentConfig(**config))
    except errors.APIError as e:
        print(f"refused: {e.code} {e.status}: {e.message}")
        return 1
    u = r.usage_metadata
    print(f"accepted. prompt tokens {u.prompt_token_count}, answer tokens {u.candidates_token_count}, "
          f"thinking tokens {getattr(u, 'thoughts_token_count', None)}, "
          f"finish {r.candidates[0].finish_reason if r.candidates else None}")
    print("answer:", r.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
