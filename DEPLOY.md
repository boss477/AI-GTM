# Deploying the dashboard

Only `dashboard/app.py` (the Flask command center) is deployed. Two targets are wired
up — **Render** (recommended: always-on, so the routes that shell out to the sibling
agent projects can work) and **Vercel** (serverless).

## Render (recommended)

`render.yaml` defines the service, so no CLI is needed:

1. Push this branch and go to <https://dashboard.render.com> → **New** → **Blueprint**.
2. Connect the `AI-GTM` repo and pick the branch. Render reads `render.yaml`.
3. It prompts for the values marked `sync: false` — `EXA_API_KEY`,
   `HUNTER_SUPABASE_URL/KEY`, `INVOICE_SUPABASE_URL/KEY`. `FLASK_SECRET_KEY` is
   generated automatically.
4. **Apply**. The live URL appears as `https://ai-gtm-dashboard.onrender.com`.

It runs `gunicorn --chdir dashboard --bind 0.0.0.0:$PORT app:app`. The free plan sleeps
after 15 minutes idle, so the first request after a pause takes ~30 s.

To make `/run-strategist` and `/create-invoice` work there, extend `buildCommand` to also
install `strategist_agent` / `invoice_system` dependencies (they need `agno`).

## Vercel

Streamlit UIs, the Telegram bots and the invoice scheduler need an always-on host and
are excluded from the upload via `.vercelignore`.

### What is wired up

| File | Purpose |
|---|---|
| `api/index.py` | Vercel serverless entrypoint; imports the Flask `app` from `dashboard/app.py` |
| `vercel.json` | Rewrites every path to the function and bundles `dashboard/**` (templates) |
| `requirements.txt` | Runtime deps for the function |
| `.vercelignore` | Keeps the vendored `agno/` and `langgraph/` clones out of the upload |
| `.env.example` | The environment variables the dashboard reads |

### Deploy

```bash
npm i -g vercel
vercel login
vercel link            # create/select the project
```

Set the environment variables (Production + Preview), then deploy:

```bash
vercel env add EXA_API_KEY production
vercel env add HUNTER_SUPABASE_URL production
vercel env add HUNTER_SUPABASE_KEY production
vercel env add INVOICE_SUPABASE_URL production
vercel env add INVOICE_SUPABASE_KEY production
vercel env add FLASK_SECRET_KEY production

vercel --prod
```

The command prints the live URL.

### Known limits on Vercel

- `/run-strategist` and `/create-invoice` shell out to `python <script>` in sibling
  directories. Those directories are not uploaded and the serverless runtime has no
  writable project checkout, so both routes return an error JSON in production. Run
  them locally or move them to an always-on worker.
- The Strategist column is always empty in production: `parse_strategies()` reads
  `strategist_agent/great.md`, which is gitignored and excluded from the upload.
- Set `FLASK_SECRET_KEY` in Vercel. Without it the app falls back to a literal key that
  is public in this repo, so session cookies would be forgeable.
- Flask's session cookie holds the `last_search_time` filter; nothing else is stateful.
- Rotate the Exa and Supabase keys that were previously hardcoded in this repo — they
  are still in the git history and must be considered public.

## Run locally

```bash
cp .env.example .env      # fill in the values
pip install -r requirements.txt
python dashboard/app.py   # http://localhost:5000
```
