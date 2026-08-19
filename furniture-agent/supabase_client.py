"""
Furniture Lead Agent - Supabase Client
Handles database storage for leads
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

try:
    import streamlit as st
    _has_streamlit = True
except Exception:
    _has_streamlit = False

load_dotenv()

def _get_secret(name: str):
    if not _has_streamlit:
        return None
    try:
        return st.secrets.get(name)
    except Exception:
        return None

url: str = os.getenv("SUPABASE_URL") or _get_secret("SUPABASE_URL")
key: str = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_KEY")
    or _get_secret("SUPABASE_KEY")
)

def is_valid_supabase_url(value: str | None) -> bool:
    if not value:
        return False
    if value in {"your_supabase_url", "your_supabase_url_here", "https://xxxxx.supabase.co"}:
        return False
    return value.startswith("https://") and "supabase.co" in value

def is_valid_supabase_key(value: str | None) -> bool:
    if not value:
        return False
    if value in {"your_supabase_key", "your_supabase_key_here", "your_anon_key_here"}:
        return False
    return True

if is_valid_supabase_url(url) and is_valid_supabase_key(key):
    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        supabase = None
else:
    if not is_valid_supabase_url(url):
        print("⚠️ Supabase URL is missing or invalid. Leads will not be saved.")
    if not is_valid_supabase_key(key):
        print("⚠️ Supabase key is missing or invalid. Leads will not be saved.")
    supabase = None


def save_leads(leads: list) -> bool:
    """
    Save leads to Supabase database.
    
    Args:
        leads: List of lead dictionaries
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not supabase:
        print("⚠️ Supabase not configured. Skipping save.")
        return False
    
    if not leads:
        print("⚠️ No leads to save.")
        return False
    
    try:
        # Transform leads to match table schema
        transformed_leads = []
        for lead in leads:
            transformed_leads.append({
                "company": lead.get("company", ""),
                "website": lead.get("website", ""),
                "intent_signal": lead.get("intent_signal", ""),
                "intent_score": lead.get("intent_score", 0),
                "city": lead.get("city", ""),
                "segment": lead.get("segment", ""),
                "decision_maker_role": lead.get("decision_maker", "")
            })
        
        # Upsert leads to table
        response = supabase.table("furniture_leads").upsert(transformed_leads).execute()
        
        if response.data:
            print(f"✅ Saved {len(leads)} leads to Supabase")
            return True
        else:
            print(f"⚠️ No data returned from Supabase: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving to Supabase: {e}")
        return False


def get_leads(limit: int = 100, segment: str = None, city: str = None) -> list:
    """
    Fetch leads from Supabase.
    
    Args:
        limit: Maximum number of leads to fetch
        segment: Optional filter by segment
        city: Optional filter by city
    
    Returns:
        List of lead dictionaries
    """
    if not supabase:
        print("⚠️ Supabase not configured.")
        return []
    
    try:
        query = supabase.table("furniture_leads").select("*")
        
        if segment:
            query = query.eq("segment", segment)
        if city:
            query = query.eq("city", city)
        
        response = query.limit(limit).execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"❌ Error fetching from Supabase: {e}")
        return []
