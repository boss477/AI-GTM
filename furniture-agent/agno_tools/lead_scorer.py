"""
Agno tool wrapper for lead scoring functionality

This module wraps the existing agent.py scoring functions as Agno tools.
No modifications to the original agent.py code.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agno.agent import Function

load_dotenv()


def _score_leads(leads: list) -> list:
    """
    Score leads based on furniture buying intent signals.
    
    This function wraps the existing scoring logic from agent.py
    without modifying the original code.
    
    Args:
        leads: List of lead dictionaries
    
    Returns:
        List of leads with intent scores (already scored from search)
    """
    # Import existing function - NO CHANGES to agent.py
    from agent import score_intent
    
    scored_leads = []
    for lead in leads:
        # Get the intent signal text
        intent_signal = lead.get("intent_signal", "")
        
        # Score the lead using existing function
        score = score_intent(intent_signal) if intent_signal else lead.get("intent_score", 4)
        
        lead["intent_score"] = score
        scored_leads.append(lead)
    
    # Sort by intent score (highest first)
    scored_leads = sorted(scored_leads, key=lambda x: x.get("intent_score", 0), reverse=True)
    
    return scored_leads


def _filter_high_intent_leads(leads: list, min_score: int = 7) -> dict:
    """
    Filter leads by intent score threshold.
    
    Args:
        leads: List of lead dictionaries
        min_score: Minimum intent score to include (default: 7)
    
    Returns:
        Dictionary with filtered leads and summary
    """
    if not leads:
        return {
            "high_intent_leads": [],
            "medium_intent_leads": [],
            "low_intent_leads": [],
            "summary": "No leads to filter"
        }
    
    high_intent = []
    medium_intent = []
    low_intent = []
    
    for lead in leads:
        score = lead.get("intent_score", 0)
        
        if score >= 9:
            high_intent.append(lead)
        elif score >= 7:
            medium_intent.append(lead)
        else:
            low_intent.append(lead)
    
    return {
        "high_intent_leads": high_intent,
        "medium_intent_leads": medium_intent,
        "low_intent_leads": low_intent,
        "summary": f"Found {len(high_intent)} high-intent (9-10), {len(medium_intent)} medium (7-8), {len(low_intent)} low (below 7)"
    }


# Create Agno tool wrapper for scoring leads
score_leads = Function(
    name="score_leads",
    description="Score leads based on furniture buying intent signals. Uses keyword analysis to assign intent scores (10=highest, 4=lowest) and sorts leads by score.",
    parameters={
        "type": "object",
        "properties": {
            "leads": {
                "type": "array",
                "description": "List of lead dictionaries to score"
            }
        },
        "required": ["leads"]
    },
    entrypoint=_score_leads,
)


# Create Agno tool wrapper for filtering leads
filter_high_intent_leads = Function(
    name="filter_high_intent_leads",
    description="Filter leads by intent score threshold. Returns separate lists for high-intent (9-10), medium-intent (7-8), and low-intent (below 7) leads.",
    parameters={
        "type": "object",
        "properties": {
            "leads": {
                "type": "array",
                "description": "List of lead dictionaries to filter"
            },
            "min_score": {
                "type": "integer",
                "description": "Minimum intent score for high-intent classification (default: 7)"
            }
        },
        "required": ["leads"]
    },
    entrypoint=_filter_high_intent_leads,
)


# Convenience functions for direct use (not as Agno tools)
def score_leads_direct(leads: list) -> list:
    """Direct function call to score leads (not wrapped as Agno tool)."""
    return _score_leads(leads)


def filter_high_intent_leads_direct(leads: list, min_score: int = 7) -> dict:
    """Direct function call to filter leads (not wrapped as Agno tool)."""
    return _filter_high_intent_leads(leads, min_score)
