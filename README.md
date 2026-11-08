# Telegram AI Bot

A Telegram chatbot powered by the Google Gemini API. It remembers the last 10
exchanges per chat, answers in the user's language (Kazakh / Russian / English)
and has `/start` and `/reset` commands.

Built with **only the Python standard library** – nothing to `pip install`.

## How it works

```
Telegram  --getUpdates (long polling)-->  bot.py  --chat history-->  Gemini API
   ^                                        |
   +------------- sendMessage --------------+
```

- `bot.py` – polling loop, per-chat history, message splitting
- `llm.py` – small Gemini API client
- `tests/` – unit tests (run offline)

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Get a free API key at <https://aistudio.google.com/apikey>.
3. Copy `.env.example` to `.env` and fill in both values.
4. Run:

```bash
python bot.py
```

## Tests

```bash
python -m unittest -v
```

## Ideas for improvement

- Save chat history to a file/SQLite so it survives restarts
- Add a `/mode` command (teacher, translator, coder)
- Rate limiting per user
- Deploy to a free host

> Never commit your `.env` file – it contains secrets (it is in `.gitignore`).
