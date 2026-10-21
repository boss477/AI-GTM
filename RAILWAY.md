# Deploying to Railway

The repo is a monorepo: each app below becomes its own Railway **service** inside one
Railway project, all pointing at this same GitHub repo.

| App | Root Directory | Config file path | Public URL? |
| --- | --- | --- | --- |
| Dashboard (Flask) | `/` | `railway/dashboard.json` | yes |
| Invoice system (Flask) | `/invoice_system` | `railway/invoice_system.json` | yes |
| Furniture agent (Streamlit) | `/furniture-agent` | `railway/furniture_agent.json` | yes |
| Telegram bot (worker) | `/` | `railway/telegram.json` | no |

The dashboard and the Telegram bot run from the repo root because they import/execute the
sibling projects (`strategist_agent`, `hunter_agent`, `invoice_system`); their dependencies
live in the root `requirements.txt`.

## Steps

1. Create a Railway project: **New Project → Deploy from GitHub repo → boss477/AI-GTM**.
2. For each app in the table: **New → GitHub Repo → same repo**, then in the service's
   **Settings**:
   - *Source → Root Directory*: the value from the table.
   - *Config-as-code → Config file path*: the value from the table
     (paths are relative to the repo root).
3. Add the variables from `.env.example` under the service's **Variables** tab
   (only the ones that service needs).
4. For the three web services, **Settings → Networking → Generate Domain**. The start
   commands already bind to `0.0.0.0:$PORT`, which is what Railway requires. The Telegram
   bot is a worker (long polling) — do not give it a domain.
5. Deploy. Logs are under the service's **Deployments** tab.

## Notes

- Nixpacks auto-detects Python and installs from the `requirements.txt` found in the
  service's root directory.
- `invoice_system` exposes `/health`, used as its healthcheck.
- Railway's filesystem is ephemeral: generated invoice PDFs written to
  `invoice_system/invoices/` disappear on redeploy. Attach a volume or upload them to
  Supabase Storage if they need to persist.
- `unified_agent.py` (Telegram bot) talks to an OpenAI-compatible endpoint at
  `LOCAL_BASE_URL`. A `localhost` Ollama URL will not work from Railway — point it at a
  publicly reachable endpoint (e.g. OpenAI, or a tunnelled local model).
