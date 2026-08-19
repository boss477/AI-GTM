"""
Agno Agent Configuration for Furniture Lead Hunter

This module configures the Agno agent that orchestrates the lead hunting workflow.
It uses the existing functions via tool wrappers without modifying the original code.
"""

import os
import sys
"""LangGraph orchestration for the furniture lead workflow."""

import re
from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agent import furniture_agent, score_intent
from supabase_client import save_leads

SEGMENTS = ("Office", "Coworking", "Hotel", "Restaurant", "Residential", "Retail")


class LeadState(TypedDict, total=False):
    prompt: str
    city: str
    segment: str
    limit: int
    leads: list[dict[str, Any]]
    filtered: dict[str, Any]
    save_result: dict[str, Any]
    response: str


@dataclass
class AgentResponse:
    content: str
    state: LeadState


def parse_request(prompt: str) -> dict[str, Any]:
    """Extract city, segment, and result limit from the existing prompt format."""
    segment = next(
        (candidate for candidate in SEGMENTS if re.search(rf"\b{candidate}\b", prompt, re.I)),
        "Office",
    )
    city_match = re.search(r"\bin\s+(.+?)(?:,?\s+limit\b|$)", prompt, re.I)
    if not city_match:
        raise ValueError("Prompt must include a city, for example: 'leads in Chennai'")

    limit_match = re.search(r"\blimit\s*(?:to|=)?\s*(\d+)", prompt, re.I)
    return {
        "city": city_match.group(1).strip(" ,"),
        "segment": segment,
        "limit": int(limit_match.group(1)) if limit_match else 10,
    }


def search_leads_direct(city: str, segment: str, limit: int) -> list[dict[str, Any]]:
    return furniture_agent(city, segment, limit)


def score_leads_direct(leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for lead in leads:
        lead["intent_score"] = score_intent(lead.get("intent_signal", ""))
        scored.append(lead)
    return sorted(scored, key=lambda lead: lead.get("intent_score", 0), reverse=True)


def filter_high_intent_leads_direct(
    leads: list[dict[str, Any]], min_score: int = 7
) -> dict[str, Any]:
    high = [lead for lead in leads if lead.get("intent_score", 0) >= 9]
    medium = [lead for lead in leads if min_score <= lead.get("intent_score", 0) < 9]
    low = [lead for lead in leads if lead.get("intent_score", 0) < min_score]
    return {
        "high_intent_leads": high,
        "medium_intent_leads": medium,
        "low_intent_leads": low,
        "summary": (
            f"Found {len(high)} high-intent (9-10), "
            f"{len(medium)} medium (7-8), {len(low)} low (below 7)"
        ),
    }


def save_leads_direct(leads: list[dict[str, Any]]) -> dict[str, Any]:
    if not leads:
        return {"success": False, "message": "No leads to save", "count": 0}
    success = save_leads(leads)
    return {
        "success": success,
        "message": f"Saved {len(leads)} leads" if success else "Failed to save leads",
        "count": len(leads) if success else 0,
    }


def parse_node(state: LeadState) -> LeadState:
    return parse_request(state["prompt"])


def search_node(state: LeadState) -> LeadState:
    return {
        "leads": search_leads_direct(
            city=state["city"],
            segment=state["segment"],
            limit=state["limit"],
        )
    }


def score_node(state: LeadState) -> LeadState:
    return {"leads": score_leads_direct(state.get("leads", []))}


def filter_node(state: LeadState) -> LeadState:
    return {"filtered": filter_high_intent_leads_direct(state.get("leads", []))}


def save_node(state: LeadState) -> LeadState:
    return {"save_result": save_leads_direct(state.get("leads", []))}


def format_node(state: LeadState) -> LeadState:
    leads = state.get("leads", [])
    names = ", ".join(lead.get("company", "Unknown") for lead in leads) or "none"
    return {
        "response": (
            f"Found {len(leads)} {state['segment']} leads in {state['city']}: {names}. "
            f"{state['filtered']['summary']}. {state['save_result']['message']}."
        )
    }


def _build_graph():
    graph = StateGraph(LeadState)
    graph.add_node("parse", parse_node)
    graph.add_node("search", search_node)
    graph.add_node("score", score_node)
    graph.add_node("filter", filter_node)
    graph.add_node("save", save_node)
    graph.add_node("format", format_node)
    graph.add_edge(START, "parse")
    graph.add_edge("parse", "search")
    graph.add_edge("search", "score")
    graph.add_edge("score", "filter")
    graph.add_edge("filter", "save")
    graph.add_edge("save", "format")
    graph.add_edge("format", END)
    return graph.compile()


lead_graph = _build_graph()


class _LeadHunterAgent:
    name = "Furniture Lead Hunter"
    model = "LangGraph StateGraph"
    tools = [search_leads_direct, score_leads_direct, filter_high_intent_leads_direct, save_leads_direct]

    def run(self, prompt: str) -> AgentResponse:
        return run_agent(prompt)


lead_hunter_agent = _LeadHunterAgent()


def run_agent(prompt: str) -> AgentResponse:
    state = lead_graph.invoke({"prompt": prompt})
    return AgentResponse(content=state["response"], state=state)


if __name__ == "__main__":
    print(run_agent("Find hotel furniture leads in Chennai, limit to 5").content)
