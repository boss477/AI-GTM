from supabase import create_client, Client

HUNTER_URL = "https://wpceiqvcdxdnpvfbqxot.supabase.co"
HUNTER_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY2VpcXZjZHhkbnB2ZmJxeG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTAyMTcsImV4cCI6MjA4NjcyNjIxN30.ppvw-2QdVdxWMXkDzVd98yKDUdAbic2YzP3HpyGAHCk"

try:
    print("Connecting to Hunter Agent Supabase...")
    db: Client = create_client(HUNTER_URL, HUNTER_KEY)
    
    # Check if we can read leads
    response = db.table("leads").select("*").limit(1).execute()
    print("SUCCESS: Connection established.")
    
    if response.data:
        lead = response.data[0]
        print(f"Sample Lead Keys: {list(lead.keys())}")
        if "status" in lead:
            print("INFO: 'status' column exists.")
        else:
            print("WARNING: 'status' column MISSING. We need to handle this manually or update schema.")
    else:
        print("INFO: Table is empty, but accessible.")

except Exception as e:
    print(f"FAILURE: {e}")
