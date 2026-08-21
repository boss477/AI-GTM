# Deploying the dashboard to Vercel

Only `dashboard/app.py` (the Flask command center) is deployed. Streamlit UIs, the
Telegram bots and the invoice scheduler need an always-on host and are excluded via
`.vercelignore`.

## What is wired up

| File | Purpose |
|---|---|
| `api/index.py` | Vercel serverless entrypoint; imports the Flask `app` from `dashboard/app.py` |
| `vercel.json` | Rewrites every path to the function and bundles `dashboard/**` (templates) |
| `requirements.txt` | Runtime deps for the function |
| `.vercelignore` | Keeps the vendored `agno/` and `langgraph/` clones out of the upload |
| `.env.example` | The environment variables the dashboard reads |

## Deploy

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

## Run locally

```bash
cp .env.example .env      # fill in the values
pip install -r requirements.txt
python dashboard/app.py   # http://localhost:5000
```

## Known limits on Vercel

- `/run-strategist` and `/create-invoice` shell out to `python <script>` in sibling
  directories. Those directories are not uploaded and the serverless runtime has no
  writable project checkout, so both routes return an error JSON in production. Run
  them locally or move them to an always-on worker.
- Flask's session cookie holds the `last_search_time` filter; nothing else is stateful.
- Rotate the Exa and Supabase keys that were previously hardcoded in this repo — they
  are still in the git history and must be considered public.
