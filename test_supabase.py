"""
Test script to verify Supabase connection and insert a test lead
"""
from supabase import create_client

# Replace with your actual Supabase credentials
url = "https://aghavnajgmphznjpjpef.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFnaGF2bmFqZ21waHpuanBqcGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNzUzOTYsImV4cCI6MjA4NjY1MTM5Nn0.UxOJjoJcs5xzsVO2bEzNPCIL5Okoe4kwI-ontSoGIPM"

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
