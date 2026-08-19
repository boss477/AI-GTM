"""
Test script to verify Supabase connection and insert a test lead
"""
from supabase import create_client

# Replace with your actual Supabase credentials
url = "https://aghavnajgmphznjpjpef.supabase.co"
key = "***REMOVED***"

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
