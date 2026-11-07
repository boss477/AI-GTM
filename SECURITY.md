# Security Policy

## Supported versions

Security fixes go into the `main` branch.

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Report them privately through
[GitHub's private vulnerability reporting](https://github.com/boss477/AI-GTM/security/advisories/new).
Include steps to reproduce and the impact.

You will get an acknowledgment within a week. Once a fix lands, you will be credited in the
changelog unless you prefer to stay anonymous.

## Secrets

- All credentials are read from environment variables (see [.env.example](.env.example)). `.env` is
  git-ignored. CI fails if a Supabase or Exa credential is committed anywhere in the repository.
- **Credentials that were committed in earlier versions must be treated as compromised** even though
  the current code no longer contains them: Git history keeps them. Rotate the Exa API key and the
  Supabase keys of each project, and confirm Row Level Security is enabled on every table so the
  `anon` key cannot read or write data it should not.
- Use the Supabase `service_role` key only on a trusted server, never in a browser or a public
  repository.

## Operational notes

| Area                 | Guidance                                                                                                                     |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Flask apps           | The debugger is off unless `FLASK_DEBUG=1`. It allows remote code execution; never enable it on a reachable host.           |
| Agents and tools     | Agents act through explicit tools. Keep approval gates before any external action such as sending e-mail or messages.       |
| Generated invoices   | `invoice_system/invoices/` holds generated PDFs that can contain customer and bank details. New files are git-ignored, but PDFs committed earlier were removed from the current tree but **remain in Git history** until the history is rewritten; treat any customer or bank details in them as exposed. |
| Dependencies         | Agno and LangGraph are installed from PyPI; report their vulnerabilities upstream. `.github/dependabot.yml` keeps the pinned requirements current. |
