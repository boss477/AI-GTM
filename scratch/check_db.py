from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
url = os.getenv("INVOICE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = os.getenv("INVOICE_SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Fetching orders to check IDs...")
res = supabase.table("orders").select("id").order("id", desc=True).limit(10).execute()
print(f"Max ID found: {res.data[0]['id'] if res.data else 'No orders'}")
print("Recent IDs:", [r['id'] for r in res.data])
