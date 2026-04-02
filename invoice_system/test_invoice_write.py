from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env file. "
        f"SUPABASE_URL={'set' if SUPABASE_URL else 'MISSING'}, "
        f"SUPABASE_KEY={'set' if SUPABASE_KEY else 'MISSING'}"
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(f"Testing write access to 'invoices'...")

try:
    # Try to insert a dummy invoice (will remove it later or mark as deleted)
    test_invoice = {
        "order_id": 5,  # assuming order 5 exists as per user
        "invoice_number": "TEST-WRITE-ACCESS",
        "subtotal": 1.0,
        "tax": 0.18,
        "total_amount": 1.18,
        "due_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "TEST",
    }

    response = supabase.table("invoices").insert(test_invoice).execute()
    print("SUCCESS: Write access to 'invoices' confirmed.")
    print(response.data)

    # Clean up
    # supabase.table("invoices").delete().eq("invoice_number", "TEST-WRITE-ACCESS").execute()
    # print("Cleaned up test record.")

except Exception as e:
    print(f"FAILURE: Could not write to 'invoices'.")
    print(f"Error: {e}")
