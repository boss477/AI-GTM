"""
Agno tool wrapper for Exa search functionality

This module wraps the existing agent.py functions as Agno tools.
No modifications to the original agent.py code.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agno.agent import Function

load_dotenv()


def _search_leads(city: str, segment: str, limit: int = 10) -> list:
    """
    Search for furniture leads using Exa API.
    
    This function wraps the existing furniture_agent() from agent.py
    without modifying the original code.
    
    Args:
        city: Target city for lead search (e.g., "Chennai", "Mumbai")
        segment: Type of building/space (Office, Coworking, Hotel, Restaurant, Residential, Retail)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of lead dictionaries with company, website, intent_score, etc.
    """
    # Import existing function - NO CHANGES to agent.py
    from agent import furniture_agent
    
    # Call existing function
    leads = furniture_agent(city, segment, limit)
    
    return leads


# Create Agno tool wrapper
search_leads = Function(
    name="search_leads",
    description="Search for furniture sales leads in a specific city and segment using Exa API. Returns companies with potential furniture buying intent based on new openings, renovations, or expansion signals.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Target city for lead search (e.g., 'Chennai', 'Mumbai', 'Bangalore')"
            },
            "segment": {
                "type": "string", 
                "description": "Type of building/space: Office, Coworking, Hotel, Restaurant, Residential, or Retail"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10
            }
        },
        "required": ["city", "segment"]
    },
    entrypoint=_search_leads,
)


# Convenience function for direct use (not as Agno tool)
def search_leads_direct(city: str, segment: str, limit: int = 10) -> list:
    """
    Direct function call to search leads (not wrapped as Agno tool).
    
    Use this when you need to call the function directly without Agno.
    """
    return _search_leads(city, segment, limit)
