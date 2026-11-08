"""Minimal Gemini API client. Standard library only (no pip install needed)."""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def _load_env(path=".env"):
    """Load KEY=VALUE pairs from a .env file into os.environ (if it exists)."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()


class LLMError(RuntimeError):
    """Raised when the LLM API call fails."""


def chat(messages, system=None, model=None, timeout=60):
    """Send a conversation to Gemini and return the reply text.

    messages: list of {"role": "user" | "model", "text": "..."}
    """
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set. Put it in a .env file.")
    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [
            {"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages
        ]
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")[:300]
        raise LLMError(f"API error {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise LLMError(f"Network error: {e.reason}") from e
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError) as e:
        raise LLMError(f"Unexpected response: {str(data)[:300]}") from e


def ask(prompt, system=None, **kwargs):
    """Single-turn helper."""
    return chat([{"role": "user", "text": prompt}], system=system, **kwargs)
