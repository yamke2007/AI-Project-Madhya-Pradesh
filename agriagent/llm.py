"""Optional local LLM (Ollama). No paid API, no downloads at run time.

Used only where fixed rules cannot decide: the meaning of table headers that
the English/Hindi keyword rules do not recognise. Every call is recorded in
the agent trace. If Ollama is not running, the caller keeps the rule result
and the run notes say the model was unavailable (nothing is guessed).

    ollama serve & ; ollama pull qwen2.5:3b
    AGRIAGENT_MODEL=qwen2.5:3b  (default)   AGRIAGENT_LLM=off  (disable)
"""
import json
import os
import re
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("AGRIAGENT_MODEL", "qwen2.5:3b")
_state = {}


def available():
    if os.environ.get("AGRIAGENT_LLM", "on").lower() == "off":
        return False
    if "up" not in _state:
        try:
            with urllib.request.urlopen(URL + "/api/tags", timeout=2) as r:
                _state["up"] = r.status == 200
        except Exception:
            _state["up"] = False
    return _state["up"]


def chat_json(system, user, timeout=120):
    """Return parsed JSON from the model, or None when unavailable/invalid."""
    if not available():
        return None
    body = json.dumps({"model": MODEL, "stream": False, "format": "json", "options": {"temperature": 0},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL + "/api/chat", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = json.loads(r.read())["message"]["content"]
    except Exception:
        return None
    try:
        return json.loads(content)
    except ValueError:
        m = re.search(r"\{.*\}", content, re.S)
        try:
            return json.loads(m.group(0)) if m else None
        except ValueError:
            return None
