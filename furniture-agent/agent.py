"""
Furniture Lead Agent - Core Logic
Finds new buildings/offices with potential to sell furniture
"""

import os
from exa_py import Exa
from dotenv import load_dotenv

load_dotenv()

# Initialize Exa
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

# Segment definitions with furniture-relevant search queries
SEGMENT_QUERIES = {
    "Office": "new office building construction OR office space opening OR corporate office expansion OR commercial office fit-out",
    "Coworking": "coworking space opening OR shared office launch OR new coworking center OR coworking fit-out",
    "Hotel": "new hotel opening OR hotel renovation OR hospitality project OR hotel interior fit-out",
    "Restaurant": "new restaurant opening OR cafe launch OR dining space renovation OR restaurant fit-out",
    "Residential": "new apartment complex OR residential project launch OR housing development OR model apartment",
    "Retail": "new retail store opening OR shopping mall expansion OR showroom launch OR retail fit-out"
}

# Decision maker roles by segment
DECISION_MAKER_ROLES = {
    "Office": "Procurement Manager / Facilities Head",
    "Coworking": "Operations Manager / Founder",
    "Hotel": "Operations Director / General Manager",
    "Restaurant": "Owner / Operations Manager",
    "Residential": "Project Manager / Procurement Head",
    "Retail": "Store Manager / Operations Head"
}


def build_query(city: str, segment: str) -> str:
    """
    Build search query based on city and segment.
    """
    base_query = SEGMENT_QUERIES.get(segment, SEGMENT_QUERIES["Office"])
    return f"{city} {base_query}"


def score_intent(text: str) -> int:
    """
    Score intent based on furniture buying signals.
    
    High Intent (9-10): New openings, fit-outs, interior design
    Medium Intent (7-8): Renovations, refurbishments
    Low Intent (4-6): Planning, proposed projects
    """
    text = text.lower()
    
    # High intent signals
    high_intent_keywords = [
        "new opening", "grand opening", "construction complete", 
        "fit-out", "interior design", "soft opening", "launch",
        "inauguration", "commissioned", "operational"
    ]
    
    # Medium intent signals
    medium_intent_keywords = [
        "renovation", "refurbishment", "redesign", "reopening",
        "expansion", "upgrade", "modernization", "restoration"
    ]
    
    # Low intent signals
    low_intent_keywords = [
        "planning", "proposed", "upcoming", "future", "pipeline",
        "announcement", "approval", "tender", "bid"
    ]
    
    # Check high intent first
    for keyword in high_intent_keywords:
        if keyword in text:
            return 10
    
    # Check medium intent
    for keyword in medium_intent_keywords:
        if keyword in text:
            return 8
    
    # Check low intent
    for keyword in low_intent_keywords:
        if keyword in text:
            return 5
    
    # Default score
    return 4


def extract_lead_details(result, segment: str) -> dict:
    """
    Extract lead information from Exa search result.
    """
    # Extract company name from title
    title = result.title or ""
    if "|" in title:
        company = title.split("|")[0].strip()
    elif ":" in title:
        company = title.split(":")[0].strip()
    else:
        company = title[:50].strip()
    
    # Get text snippet
    text = result.text or ""
    
    # Score the intent
    intent_score = score_intent(text)
    
    # Get decision maker role
    decision_maker = DECISION_MAKER_ROLES.get(segment, "Procurement Manager")
    
    return {
        "company": company,
        "website": result.url,
        "intent_signal": text[:150] if text else "No signal available",
        "intent_score": intent_score,
        "decision_maker": decision_maker,
        "segment": segment
    }


def search_with_exa(query: str, limit: int = 10):
    """
    Search using Exa API.
    """
    try:
        response = exa.search(
            query=query,
            num_results=int(limit),
            text=True,
            highlights=True
        )
        return response.results
    except Exception as e:
        print(f"Error during Exa search: {e}")
        return []


def furniture_agent(city: str, segment: str, limit: int = 10):
    """
    Main Furniture Lead Agent function.
    
    Args:
        city: Target city for lead search
        segment: Type of building/space (Office, Coworking, Hotel, Restaurant, Residential, Retail)
        limit: Maximum number of results
    
    Returns:
        List of lead dictionaries with company, website, intent_score, etc.
    """
    print(f"\n🔍 Hunting furniture leads: {segment} in {city}")
    print(f"   Limit: {limit} results\n")
    
    # Build the search query
    query = build_query(city, segment)
    print(f"📝 Search Query: {query}\n")
    
    # Search with Exa
    results = search_with_exa(query, limit)
    
    if not results:
        print("❌ No results found.")
        return []
    
    # Extract lead details
    leads = []
    for r in results:
        lead = extract_lead_details(r, segment)
        lead["city"] = city
        leads.append(lead)
    
    # Sort by intent score (highest first)
    leads = sorted(leads, key=lambda x: x["intent_score"], reverse=True)
    
    print(f"✅ Found {len(leads)} leads\n")
    
    # Print summary
    print(f"{'Company':<35} {'Score':<8} {'Segment':<12}")
    print("-" * 60)
    for lead in leads:
        print(f"{lead['company'][:35]:<35} {lead['intent_score']}/10   {lead['segment']:<12}")
    
    return leads


# Run directly for testing
if __name__ == "__main__":
    # Example usage
    city = "Chennai"
    segment = "Office"
    limit = 5
    
    leads = furniture_agent(city, segment, limit)
