from supabase import create_client, Client
import json

# Supabase config (copied from app.py)
SUPABASE_URL = "https://wpceiqvcdxdnpvfbqxot.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY2VpcXZjZHhkbnB2ZmJxeG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTAyMTcsImV4cCI6MjA4NjcyNjIxN30.ppvw-2QdVdxWMXkDzVd98yKDUdAbic2YzP3HpyGAHCk"

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
