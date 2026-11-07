"""
Test script to verify Supabase connection and insert a test lead
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Credentials come from the environment (see .env.example)
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_ANON_KEY"]

# Create Supabase client
supabase = create_client(url, key)

# Test data - matching the furniture_leads table schema
test_lead = {
    "company": "Test Corp",
    "website": "https://testcorp.com",
    "intent_signal": "Looking for bulk furniture suppliers",
    "intent_score": 85,
    "city": "Chennai",
    "segment": "Furniture",
    "decision_maker_role": "Procurement Manager"
}

print("Inserting test lead into furniture_leads table...")
print(f"Data: {test_lead}")

# Insert the lead
response = supabase.table("furniture_leads").insert(test_lead).execute()

print("\nResponse:", response)

if response.data:
    print(f"Successfully inserted lead!")
    print(f"Inserted data: {response.data}")
else:
    print("No data returned, but insert may have succeeded")
    print(f"Response: {response}")
