# Agno Integration Plan for Furniture Lead Agent

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT FLOW                              │
├─────────────────────────────────────────────────────────────┤
│  Telegram Bot                                               │
│      │                                                      │
│      ▼                                                      │
│  bot.py (hunt_command)                                      │
│      │                                                      │
│      ▼                                                      │
│  agent.py (furniture_agent)                                 │
│      │                                                      │
│      ├──► build_query()                                     │
│      ├──► search_with_exa()                                │
│      ├──► extract_lead_details()                            │
│      │       └──► score_intent()                           │
│      └──► sort leads                                        │
│                                                              │
│      ▼                                                      │
│  supabase_client.py (save_leads)                            │
│      │                                                      │
│      ▼                                                      │
│  Supabase Database                                          │
└─────────────────────────────────────────────────────────────┘
```

## Current Files

| File | Purpose |
|------|---------|
| [`furniture-agent/bot.py`](furniture-agent/bot.py:1) | Telegram bot entry point |
| [`furniture-agent/agent.py`](furniture-agent/agent.py:1) | Lead search & scoring logic |
| [`furniture-agent/supabase_client.py`](furniture-agent/supabase_client.py:1) | Supabase storage |
| [`furniture-agent/.env`](furniture-agent/.env:1) | Environment variables |

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TARGET FLOW (with Agno)                      │
├─────────────────────────────────────────────────────────────────┤
│  Telegram Bot                                                   │
│      │                                                          │
│      ▼                                                          │
│  bot.py (hunt_command)                                         │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Agno Agent (agno_agent.py)                              │   │
│  │  - Reasoning layer for orchestration                      │   │
│  │  - Decides when to search, score, store                  │   │
│  │                                                           │   │
│  │  Tools (agno_tools/):                                    │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │   │
│  │  │ exa_search   │ │ save_leads   │ │ score_leads  │     │   │
│  │  │   .py        │ │    .py       │ │     .py      │     │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
│      │                                                          │
│      ▼                                                          │
│  Existing Modules (unchanged):                                 │
│  - agent.py (imported by tools)                                │
│  - supabase_client.py (imported by tools)                      │
│                                                              │
│      ▼                                                          │
│  Supabase Database                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Recommended Folder Structure

```
furniture-agent/
├── bot.py                    # Entry point (UNCHANGED)
├── agent.py                  # Core logic (UNCHANGED)
├── supabase_client.py        # Storage (UNCHANGED)
├── .env                      # Env vars (UNCHANGED)
├── requirements.txt           # Add agno
│
├── agno_tools/               # NEW: Agno tool wrappers
│   ├── __init__.py
│   ├── exa_search.py         # Wraps agent.py search functions
│   ├── supabase_storage.py  # Wraps supabase_client.py
│   └── lead_scorer.py        # Wraps agent.py scoring
│
├── agno_agent.py             # NEW: Agno agent configuration
│
└── test_agno.py             # NEW: Test script
```

## Implementation Details

### 1. Tool Wrappers Pattern

Each tool wraps existing functions WITHOUT modifying them:

#### exa_search.py
```python
"""Agno tool wrapper for Exa search - wraps agent.py functions"""
from agno.tools import Function
from agent import build_query, search_with_exa, extract_lead_details

# Import existing functions and wrap them as Agno tools
# NO CHANGES to agent.py - just import and use
```

#### supabase_storage.py
```python
"""Agno tool wrapper for Supabase - wraps supabase_client.py"""
from supabase_client import save_leads, get_leads

# Import existing functions and wrap them as Agno tools
# NO CHANGES to supabase_client.py - just import and use
```

#### lead_scorer.py
```python
"""Agno tool wrapper for lead scoring - wraps agent.py functions"""
from agent import score_intent

# Import existing functions and wrap them as Agno tools
# NO CHANGES to agent.py - just import and use
```

### 2. Agno Agent Configuration

```python
# agno_agent.py
from agno import Agent
from agno_tools import exa_search, supabase_storage, lead_scorer

lead_hunter_agent = Agent(
    name="Furniture Lead Hunter",
    model="openai/gpt-4o-mini",  # Or your preferred model
    tools=[exa_search, supabase_storage, lead_scorer],
    instructions="""
    You are a furniture lead hunting assistant.
    
    When user asks to hunt for leads:
    1. Use exa_search to find leads in the specified city and segment
    2. Use lead_scorer to filter/highlight high-intent leads
    3. Use supabase_storage to save the leads
    4. Return a summarized response to the user
    """,
    show_tool_calls=True,
)
```

### 3. Minimal Integration with Telegram Bot

In bot.py, add an optional Agno path:

```python
# bot.py - Minimal changes
from agent import furniture_agent          # EXISTING
from supabase_client import save_leads    # EXISTING
from agno_agent import lead_hunter_agent  # NEW (optional)

# Option A: Keep existing flow (NO CHANGES)
async def hunt_command(update, context):
    leads = furniture_agent(city, segment)
    save_leads(leads)
    # ... rest unchanged

# Option B: Use Agno for orchestration (NEW)
async def hunt_command_agno(update, context):
    response = lead_hunter_agent.run(f"Hunt for {segment} leads in {city}")
    # Process response and send to Telegram
```

## Migration Strategy

### Phase 1: Zero-Downtime Setup
1. Add `agno` to requirements.txt
2. Create `agno_tools/` directory with wrappers
3. Create `agno_agent.py` configuration
4. Test in isolation with `test_agno.py`

### Phase 2: Parallel Run
1. Keep existing bot.py unchanged
2. Create new command `/hunt_agno` 
3. Run both paths simultaneously
4. Compare results

### Phase 3: Gradual Migration
1. Add feature flag in .env: `USE_AGNO=false`
2. Set `USE_AGNO=true` to switch
3. Monitor for issues

### Phase 4: Full Migration
1. Deprecate old flow
2. Update bot.py to use Agno
3. Document any breaking changes

## Key Principles

| Principle | Implementation |
|-----------|----------------|
| **No rewriting** | Import existing functions, don't modify |
| **Adapter pattern** | Tools wrap functions, not replace |
| **Stateless tools** | Tools call functions, maintain no state |
| **Async compatible** | Use async/await for Telegram handlers |
| **No circular imports** | Separate `agno_tools/` from core logic |
| **Environment preserved** | Keep using existing .env variables |

## Deliverables Checklist

- [x] Folder structure defined
- [x] Tool wrapper examples created
- [x] Agent configuration documented
- [x] Integration steps defined
- [x] Migration strategy outlined

## Next Steps

To proceed with implementation, respond with:
1. **"Start implementation"** - I'll create the files in Code mode
2. **"Show me more details"** - I can expand on any section
3. **"Modify the architecture"** - Suggest changes to the plan
