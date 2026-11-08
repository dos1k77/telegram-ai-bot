"""Telegram AI assistant bot (long polling, standard library only)."""
import json
import os
import time
import urllib.error
import urllib.request

import llm

SYSTEM_PROMPT = (
    "You are a friendly study assistant. Answer in the same language the user "
    "writes in (Kazakh, Russian or English). Be clear and concise. "
    "If you are not sure about something, say so."
)
MAX_TURNS = 10          # how many user/bot exchanges to remember per chat
TG_LIMIT = 4000         # Telegram message limit is 4096 characters

histories = {}          # chat_id -> list of {"role", "text"}


def split_text(text, limit=TG_LIMIT):
    """Split a long reply into pieces that fit into one Telegram message."""
    parts = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


def trim_history(history, max_turns=MAX_TURNS):
    """Keep only the last max_turns exchanges (2 messages each)."""
    return history[-max_turns * 2:]


def tg(token, method, **params):
    """Call a Telegram Bot API method."""
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(params).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["result"]


def handle_message(token, chat_id, text):
    if text.startswith("/start"):
        reply = "Сәлем! Мен ИИ-көмекшімін. Сұрағыңызды жазыңыз. /reset — әңгімені тазалау."
    elif text.startswith("/reset"):
        histories.pop(chat_id, None)
        reply = "Әңгіме тазаланды."
    else:
        history = histories.setdefault(chat_id, [])
        history.append({"role": "user", "text": text})
        try:
            tg(token, "sendChatAction", chat_id=chat_id, action="typing")
            reply = llm.chat(history, system=SYSTEM_PROMPT)
            history.append({"role": "model", "text": reply})
        except llm.LLMError as e:
            history.pop()  # drop the question that failed
            print("LLM error:", e)
            reply = "Кешіріңіз, қазір жауап бере алмадым. Кейінірек қайталап көріңіз."
        histories[chat_id] = trim_history(history)
    for part in split_text(reply):
        tg(token, "sendMessage", chat_id=chat_id, text=part)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set. Put it in a .env file.")
    print("Bot is running. Press Ctrl+C to stop.")
    offset = None
    while True:
        try:
            updates = tg(token, "getUpdates", offset=offset, timeout=30)
        except (urllib.error.URLError, TimeoutError) as e:
            print("Network error, retrying:", e)
            time.sleep(5)
            continue
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message") or {}
            text = msg.get("text")
            if text:
                handle_message(token, msg["chat"]["id"], text)


if __name__ == "__main__":
    main()
