<p align="center"><img src="docs/images/logo.svg" alt="AI-GTM logo" width="112" /></p>

<h1 align="center">AI-GTM</h1>

<p align="center"><strong>Turn market signals into approved GTM work your team can execute.</strong></p>

<p align="center">
A strategy workbench for research, planning, approval and execution. It combines agent workflows with
operational tools instead of an ungrounded chatbot, and nothing external happens without an explicit
approval.
</p>

<p align="center">
  <a href="https://github.com/boss477/AI-GTM/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/boss477/AI-GTM/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="license: MIT" src="https://img.shields.io/badge/license-MIT-2b3ea8"></a>
  <img alt="python: 3.10+" src="https://img.shields.io/badge/python-3.10%2B-2b3ea8?logo=python&logoColor=white">
  <a href="https://boss477.github.io/AI-GTM/"><img alt="website: boss477.github.io" src="https://img.shields.io/badge/website-boss477.github.io-2b3ea8"></a>
</p>

<p align="center"><a href="https://boss477.github.io/AI-GTM/"><img src="docs/images/landing-page.webp" alt="The AI-GTM project page" width="100%"></a></p>

<sub>The project page, with the strategy workflow and its approval gate.</sub>

## Contents

1. [Strategy workflow](#strategy-workflow)
2. [Components](#components)
3. [Setup](#setup)
4. [Run](#run)
5. [Design principles](#design-principles)
6. [Security](#security)
7. [Contributing](#contributing)
8. [License](#license)

## Strategy workflow

```mermaid
flowchart LR
  A[Market signal] --> B[Research brief] --> C[Strategist agent]
  C --> D[Approved campaign plan] --> E[Tool execution] --> F[Outcome feedback]
  F --> B
```

## Components

| Path                | What it is                                                                 |
| ------------------- | -------------------------------------------------------------------------- |
| `strategist_agent/` | Strategy workflows and tools                                               |
| `hunter_agent/`     | Lead-hunting Flask app (Exa search, Supabase storage)                      |
| `furniture-agent/`  | Furniture lead agent: Streamlit UI, Telegram bot, lead scoring             |
| `invoice_system/`   | Invoice and proforma automation (Flask, PDF generation, scheduled e-mail)  |
| `dashboard/`        | Combined dashboard over the hunter and invoice agents                      |
| `unified_agent.py`  | One agent (ARIA) that combines the strategist, hunter and invoice skills   |
| `telegram_app.py`   | Telegram front end for the unified agent                                   |
| `plans/`, `docs/`   | Design plans and specs                                                     |

## Setup

Requires Python 3.10 or newer.

```bash
git clone https://github.com/boss477/AI-GTM.git
cd AI-GTM
python -m venv .venv
.venv/Scripts/activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r hunter_agent/requirements.txt -r invoice_system/requirements.txt -r furniture-agent/requirements.txt
cp .env.example .env          # then fill in your own keys
```

All credentials come from the environment. `.env.example` lists every variable; `.env` is
git-ignored.

## Run

```bash
python dashboard/app.py          # dashboard on http://127.0.0.1:5000
python hunter_agent/app.py       # lead hunter (Flask)
python invoice_system/app.py     # invoice system (Flask)
streamlit run furniture-agent/app.py
python telegram_app.py           # Telegram bot for the unified agent
```

The Flask debugger is off by default. Set `FLASK_DEBUG=1` locally if you need it, and never on a
reachable host.

## Design principles

- Agent reasoning is visible and reviewable.
- Approval gates are explicit before external actions.
- Tool boundaries and credentials are documented.
- Research stays connected to an executable next step.

See [DESIGN.md](DESIGN.md) for the product design.

## Security

Never commit credentials. See [SECURITY.md](SECURITY.md) for how secrets are handled and how to
report a vulnerability.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md) first.

## License

[MIT](LICENSE) © boss477. Agno and LangGraph are installed from PyPI under their own licenses; this repository no longer bundles them.
