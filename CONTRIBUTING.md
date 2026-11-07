# Contributing

Thanks for helping. AI-GTM runs agents that can touch real services (search, databases, e-mail,
messaging), so changes are reviewed with that in mind.

## Ground rules

- Be kind. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
- Open an issue before a large change so we can agree on the approach.
- Keep pull requests focused: one change, one reason.
- **Never commit credentials**, customer data or generated invoices. Read keys from the environment
  and add new variables to [.env.example](.env.example).
- Keep approval gates in front of any action that sends something outside the system.

## Setup

See [Setup in the README](README.md#setup).

## Before you open a pull request

```bash
python -m compileall -q strategist_agent hunter_agent furniture-agent invoice_system dashboard unified_agent.py unified_toolkit.py telegram_app.py
```

CI runs the same syntax check and a credential scan across the repository.

- Add a line under **Unreleased** in [CHANGELOG.md](CHANGELOG.md).
- Update the README if the change is user-facing.

## Commit messages

Short, imperative, with a type prefix: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`,
`refactor:`, `security:`.
