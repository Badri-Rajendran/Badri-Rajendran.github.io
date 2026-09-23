# Badri.ai — chat endpoint

A small Python serverless function that answers questions about Badri for the chat widget on https://badri-rajendran.github.io. It keeps the OpenAI key server-side, builds the system prompt from `knowledge/*.md`, and streams answers back as server-sent events.

Design: [`docs/badri-ai-chatbot-design.md`](../docs/badri-ai-chatbot-design.md). Deployment and configuration notes are kept privately and aren't part of this repo.

## Layout

| File | Purpose |
|---|---|
| `main.py` | HTTP entry point: request checks and streaming |
| `llm.py` | OpenAI call; yields `("delta", …)` / `("done", …)` events |
| `prompt.py` | Joins `knowledge/persona.md`, `knowledge/badri.md` and optional `knowledge/private.md` |
| `validation.py` | Request checks and `ApiError` |
| `ratelimit.py` | In-memory sliding-window limiter |
| `sse.py` | SSE frame formatting |
| `config.py` | Settings from environment variables |
| `knowledge/` | What the bot knows. **The repo is public: only put facts here you're happy to publish.** |

## Run locally

```bash
cd server
python3.13 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                      # offline; OpenAI is faked

export OPENAI_API_KEY=sk-...          # your key, only in your shell
.venv/bin/functions-framework --target chat --source main.py --port 8080
```

Then serve the site from the repo root with `python3 -m http.server 8000` and open http://localhost:8000. On `localhost`, the widget talks to `http://localhost:8080`.

## Private facts

For facts you'd rather not commit (relocation, start date, salary, hobbies), create `knowledge/private.md` (git-ignored). It's appended to the prompt under "Additional facts". It is still readable by anyone who coaxes the bot into revealing its prompt, so never put secrets in it.
