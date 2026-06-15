# secrag

**secrag** is a full-stack web app that lets you chat with U.S. SEC filings. Point it at a company and a filing (e.g. Apple's latest 10-K), and an LLM agent answers questions about it by retrieving the relevant passages and financial statements straight from the source document — a retrieval-augmented-generation (RAG) system purpose-built for EDGAR data.

> ⚠️ **Status:** This is an archived project, open-sourced for reference and as a portfolio piece. It is no longer actively maintained or deployed. The code is shared as-is.

---

## What it does

- **Conversational filing analysis.** Ask natural-language questions about a specific SEC filing and get grounded, cited answers streamed back token-by-token.
- **Financial-statement retrieval.** The agent can pull structured financial tables (balance sheet, income statement, cash-flow statement, statement of changes in equity, comprehensive income) parsed from a filing's XBRL data.
- **Filing digests.** Generate a quick markdown overview of a filing, including buy/sell indicators.
- **Accounts, subscriptions, and usage limits.** Sign-up/login (email or OAuth), token-metered usage, and paid tiers via Stripe.

## How it works

The agent is a LangChain OpenAI-tools agent (`gpt-4o-mini`) with three tools:

| Tool | Purpose |
| --- | --- |
| `financial_data_filing_retriever` | Retrieves a specific financial statement from the filing's parsed XBRL data. |
| `non-financial_data_filing_retriever` | Semantic search over the full filing text via the FAISS vector store. |
| `google_search` | Fallback web search when the filing alone can't answer the question. |

Filings are fetched and parsed from SEC EDGAR using [`edgartools`](https://github.com/dgunning/edgartools), converted to markdown, chunked, and embedded with OpenAI embeddings into a FAISS index. Embedding jobs run asynchronously via Celery + Redis. Answers stream to the browser over WebSockets.

## Tech stack

**Frontend** — Vue 3 (Vue CLI), Vuex, Vue Router, Axios, `socket.io-client`, `markdown-it` / `marked` with KaTeX & MathJax for rendering formulas, Stripe.js, Supabase JS. The client builds to `client/dist`, which the server serves as static files.

**Backend** — Python, FastAPI on Uvicorn (ASGI), `fastapi-socketio` for streaming, LangChain + OpenAI, FAISS vector store, Celery + Redis for background embedding, `edgartools` for EDGAR/XBRL parsing, Google Generative AI (Gemini) for filing digests.

**Data & services** — Supabase (Postgres + auth), MongoDB (chat history), Stripe (payments), Gmail SMTP (transactional email), Logtail + Telegram (operational logging/alerts).

## Repository layout

```
.
├── app.py                  # ASGI entrypoint (FastAPI app + socket.io)
├── wsgi.py                 # alt entrypoint
├── filing_digest.py        # standalone filing-digest generator (Gemini)
├── client/                 # Vue 3 single-page app
│   └── src/                # views, components, store, router
├── server/                 # FastAPI backend
│   ├── __init__.py         # app factory: mounts routes, static client, services
│   ├── globals.py          # config singleton, Mongo client
│   ├── authentication/     # sign-up / login / account routes
│   ├── dashboard/          # chat + RAG agent (utils/: llm, vectorstore, edgar, search)
│   ├── subscription/       # Stripe billing + webhooks
│   ├── general/            # shared routes + DB utils
│   ├── github/             # GitHub auto-deploy webhook
│   └── lib_secrag/         # vendored edgartools
├── crons/                  # filing scraper + logging
├── database/               # local data: vectorstore, filings, markdowns, logs
└── .github/                # issue/PR templates
```

## Getting started

### Prerequisites

- Python 3.11+ and Node 18+
- A Redis instance (for Celery)
- Accounts/keys for: OpenAI, Google Generative AI, Supabase, Stripe, MongoDB, and a Gmail account with an [App Password](https://support.google.com/accounts/answer/185833).

### 1. Configure environment

All configuration is read from a `.env` file (loaded via `python-dotenv`). Copy the template and fill in your own values:

```bash
cp .env.example .env
# then edit .env
```

See [`.env.example`](./.env.example) for the full list of variables (database, app secrets, Stripe, Supabase, LLM keys, EDGAR identity, etc.).

### 2. Backend

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --port 5000
```

Background embedding tasks require a Celery worker running against your Redis broker.

### 3. Frontend

```bash
cd client
npm install
npm run serve                       # dev server
# or
npm run build                       # outputs to client/dist for the server to serve
```

Set the dev/prod API and socket URLs in `client/src/config.js`.

### External setup notes

- **Supabase** — create a project, set up the user tables, enable your chosen auth providers, and add a redirect URL pointing to the post-auth handler route.
- **Stripe** — create the basic and premium products (each with a monthly and yearly price) plus the token-replenish price, and configure a webhook. The webhook secret differs between dev and prod.
- **EDGAR** — SEC requires an identifying `User-Agent`; set `EDGAR_IDENTITY` to `"Your Name your_email@domain.com"`.

## Deployment

The app is containerized (see the Docker configuration) and was deployed on [render.com](https://render.com): connect the repo, supply environment variables, and point the service at the Dockerfile. The container builds the client, installs dependencies, and runs the server on port 5000.

A GitHub webhook (`/gh` route) together with `autoupdate.sh` supported pull-and-restart auto-deploys on a self-managed host via a systemd service.

## License

Released under the [MIT License](./LICENSE). You're free to use, modify, and distribute this code; it comes with no warranty.

---

*secrag — chat with SEC filings.*
