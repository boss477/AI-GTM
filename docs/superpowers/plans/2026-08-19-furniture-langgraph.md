# Furniture Lead LangGraph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the furniture lead agent's Agno orchestration with a LangGraph state workflow without changing existing lead functions or callers.

**Architecture:** `agno_agent.py` will define a typed graph state, parse the existing prompt format, run search/scoring/filter/save nodes, and return a response object with `.content`. Existing direct wrappers remain the integration boundary for Exa and Supabase.

**Tech Stack:** Python, LangGraph `StateGraph`, pytest, existing Exa and Supabase wrappers.

---

### Task 1: Add graph behavior tests

**Files:**
- Create: `furniture-agent/test_langgraph_agent.py`

- [ ] Write tests for parsing `Find hotel furniture leads in Chennai, limit to 5`, graph execution with patched functions, and `.content` compatibility.
- [ ] Run `pytest test_langgraph_agent.py -q` and confirm the new tests fail because the LangGraph implementation is not present.

### Task 2: Implement LangGraph orchestration

**Files:**
- Modify: `furniture-agent/agno_agent.py`
- Modify: `furniture-agent/requirements.txt`

- [ ] Define typed state and a response dataclass.
- [ ] Parse city, segment, and limit from existing prompt forms.
- [ ] Add search, score, filter, save, and format nodes to a compiled `StateGraph`.
- [ ] Keep `run_agent(prompt)` and return `.content`.
- [ ] Add `langgraph` to requirements.
- [ ] Run `pytest test_langgraph_agent.py -q` and confirm it passes.

### Task 3: Validate compatibility

**Files:**
- Test: `furniture-agent/test_langgraph_agent.py`

- [ ] Run the focused tests again after any cleanup.
- [ ] Run Python syntax compilation for the changed modules.
- [ ] Do not call live Exa or Supabase services.
