"""
Agno tool wrapper for Supabase storage functionality

This module wraps the existing supabase_client.py functions as Agno tools.
No modifications to the original supabase_client.py code.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agno.agent import Function

load_dotenv()


def _save_leads_to_db(leads: list) -> dict:
    """
    Save leads to Supabase database.
    
    This function wraps the existing save_leads() from supabase_client.py
    without modifying the original code.
    
    Args:
        leads: List of lead dictionaries with company, website, intent_score, etc.
    
    Returns:
        Dictionary with success status and message
    """
    # Import existing function - NO CHANGES to supabase_client.py
    from supabase_client import save_leads
    
    if not leads:
        return {
            "success": False,
            "message": "No leads to save",
            "count": 0
        }
    
    # Call existing function
    success = save_leads(leads)
    
    return {
        "success": success,
        "message": f"Saved {len(leads)} leads to database" if success else "Failed to save leads",
        "count": len(leads) if success else 0
    }


def _get_leads_from_db(limit: int = 100, segment: str = None, city: str = None) -> list:
    """
    Fetch leads from Supabase database.
    
    This function wraps the existing get_leads() from supabase_client.py
    without modifying the original code.
    
    Args:
        limit: Maximum number of leads to fetch (default: 100)
        segment: Optional filter by segment (e.g., "Office", "Hotel")
        city: Optional filter by city
    
    Returns:
        List of lead dictionaries
    """
    # Import existing function - NO CHANGES to supabase_client.py
    from supabase_client import get_leads
    
    # Call existing function
    leads = get_leads(limit=limit, segment=segment, city=city)
    
    return leads


# Create Agno tool wrapper for saving leads
save_leads_to_db = Function(
    name="save_leads_to_db",
    description="Save leads to Supabase database for persistent storage. Use this after finding leads to store them permanently.",
    parameters={
        "type": "object",
        "properties": {
            "leads": {
                "type": "array",
                "description": "List of lead dictionaries with company, website, intent_score, city, segment fields"
            }
        },
        "required": ["leads"]
    },
    entrypoint=_save_leads_to_db,
)


# Create Agno tool wrapper for fetching leads
get_leads_from_db = Function(
    name="get_leads_from_db",
    description="Retrieve leads from Supabase database. Can filter by segment, city, or limit results.",
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of leads to fetch",
                "default": 100
            },
            "segment": {
                "type": "string",
                "description": "Filter by segment (e.g., 'Office', 'Hotel', 'Restaurant')"
            },
            "city": {
                "type": "string",
                "description": "Filter by city"
            }
        },
        "required": []
    },
    entrypoint=_get_leads_from_db,
)


# Convenience functions for direct use (not as Agno tools)
def save_leads_direct(leads: list) -> dict:
    """Direct function call to save leads (not wrapped as Agno tool)."""
    return _save_leads_to_db(leads)


def get_leads_direct(limit: int = 100, segment: str = None, city: str = None) -> list:
    """Direct function call to get leads (not wrapped as Agno tool)."""
    return _get_leads_from_db(limit, segment, city)
