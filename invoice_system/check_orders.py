from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("orders").select("id").limit(5).execute()
    data = response.data
    print("Existing Order IDs:", [item['id'] for item in data])
except Exception as e:
    print(f"Error: {e}")
