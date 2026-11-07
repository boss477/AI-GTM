# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Security

- Removed hardcoded Supabase and Exa credentials from `dashboard/` and `hunter_agent/`; they are now
  read from environment variables. **Rotate the old keys:** they remain in Git history.
- Flask debug mode is now opt-in through `FLASK_DEBUG=1` (it was always on).
- `.env` and generated invoices are git-ignored.

### Added

- `.env.example`, `LICENSE` (MIT), security policy, contributing guide, code of conduct, issue and
  PR templates, and a README with setup and run instructions.
- GitHub Actions CI: syntax check and a credential scan on the project's own code.
- Dependabot for pip (per component) and GitHub Actions.

### Changed

- `hunter_agent/requirements.txt` lists `python-dotenv`, which the app now uses.

## Earlier work

Strategist, hunter, furniture and invoice agents, the combined dashboard, the unified ARIA agent and
its Telegram front end.
