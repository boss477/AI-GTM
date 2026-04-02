from supabase import create_client, Client

HUNTER_URL = "https://wpceiqvcdxdnpvfbqxot.supabase.co"
HUNTER_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY2VpcXZjZHhkbnB2ZmJxeG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTAyMTcsImV4cCI6MjA4NjcyNjIxN30.ppvw-2QdVdxWMXkDzVd98yKDUdAbic2YzP3HpyGAHCk"

try:
    print("Connecting to Hunter Agent Supabase...")
    db: Client = create_client(HUNTER_URL, HUNTER_KEY)
   
    # Since we can't run migrations directly via Client, we'll just try to insert a dummy lead with 'status'
    # If it fails, we know we need to add the column manually or via SQL editor.
    # But usually, Supabase allows adding columns on the fly if RLS allows, or we just fail.
    
    # Actually, the user asked to "add a tick mark". 
    # We will assume the column MIGHT NOT EXIST.
    # Best way for this user (Agentic mode) is to instruct them or try to work around it.
    
    # Let's try to update a lead if one existed. Since table is empty, we must create one.
    print("Inserting test lead...")
    test_lead = {
        "company": "Test Selection Inc.",
        "city": "Test City",
        "segment": "Test",
        "intent_signal": "Testing dashboard tick mark",
        "intent_score": 10,
        "status": "SELECTED", # Asking to use this column
        "website": "https://example.com"
    }
    
    response = db.table("leads").insert(test_lead).execute()
    print("SUCCESS: Inserted lead with status 'SELECTED'. Column exists!")

except Exception as e:
    print(f"FAILURE: Could not insert 'status'. Error: {e}")
    print("\n\n*** ACTION REQUIRED ***")
    print("Please go to Supabase Dashboard -> Table Editor -> 'leads' -> 'Add Column'.")
    print("Name: status, Type: text, Default Value: NEW")
