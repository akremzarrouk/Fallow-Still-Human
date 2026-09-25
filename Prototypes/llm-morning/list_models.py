"""Lists the models this GEMINI_API_KEY can call with generateContent.

    python list_models.py [filter]      e.g. python list_models.py flash-lite

Makes no generate calls. Never prints the key.
"""
import sys

from gemini import require_api_key


def main():
    key = require_api_key()
    from google import genai
    client = genai.Client(api_key=key)
    wanted = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    for m in client.models.list():
        actions = m.supported_actions or []
        if "generateContent" not in actions:
            continue
        if wanted and wanted not in m.name.lower() and wanted not in (m.display_name or "").lower():
            continue
        print(f"{m.name:55} {m.display_name}")


if __name__ == "__main__":
    main()
