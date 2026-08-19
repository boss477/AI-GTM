# Furniture Lead LangGraph Design

## Goal
Replace the Agno orchestration in `furniture-agent/agno_agent.py` with a small LangGraph workflow while preserving the existing `run_agent(prompt).content` interface.

## Scope
- Modify only `furniture-agent/agno_agent.py` and its requirements.
- Keep `furniture-agent/agent.py`, Exa search, scoring, filtering, and Supabase implementations unchanged.
- Parse the existing natural-language prompt with a small deterministic parser.

## Flow
`parse request -> search leads -> score leads -> filter intent -> save leads -> format response`

The graph state contains the original prompt, city, segment, limit, leads, filtered summary, save result, and response text. Each node performs one existing operation. The graph is compiled once and invoked by `run_agent`.

## Compatibility
`run_agent` returns a response object exposing `.content`, so existing Telegram or script callers remain compatible. The response also exposes the final graph state for programmatic use.

## Testing
Use unit tests with monkeypatched direct tool functions. Verify prompt parsing, node order/output, and `.content` compatibility without making Exa or Supabase calls.
