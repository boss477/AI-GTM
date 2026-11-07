import os
from dotenv import load_dotenv

load_dotenv()
from supabase import create_client, Client
import json

# Supabase config (from the environment, see .env.example)
SUPABASE_URL = os.environ["HUNTER_SUPABASE_URL"]
SUPABASE_KEY = os.environ["HUNTER_SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Fetch last 10 leads
    response = supabase.table("leads").select("*").order("id", desc=True).limit(10).execute()
    data = response.data
    
    print(f"Found {len(data)} leads in Supabase (showing last 10):")
    for lead in data:
        print(f"- {lead.get('company', 'N/A')} ({lead.get('city', 'N/A')}) - Score: {lead.get('intent_score')}")
        
except Exception as e:
    print(f"Error fetching from Supabase: {e}")
