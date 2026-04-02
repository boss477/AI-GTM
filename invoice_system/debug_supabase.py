from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(f"Connecting to: {SUPABASE_URL}")

try:
    # Try to select all from orders
    response = supabase.table("orders").select("*").execute()
    print(f"Data found in 'orders': {response.data}")
    
    # Try to select all from invoices
    response_inv = supabase.table("invoices").select("*").execute()
    print(f"Data found in 'invoices': {response_inv.data}")

except Exception as e:
    print(f"Error: {e}")
