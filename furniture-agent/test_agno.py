"""
Test script for Agno integration

This script tests the Agno tools and agent configuration.
Run with: python test_agno.py
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test 1: Import tool wrappers
print("=" * 60)
print("Test 1: Importing tool wrappers...")
print("=" * 60)

try:
    from agno_tools import (
        search_leads,
        save_leads_to_db,
        get_leads_from_db,
        score_leads,
        filter_high_intent_leads,
    )
    print("SUCCESS: All tool wrappers imported")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

# Test 2: Test Exa search tool
print("\n" + "=" * 60)
print("Test 2: Testing Exa search tool...")
print("=" * 60)

try:
    from agno_tools.exa_search import search_leads_direct
    
    # This will make an actual API call - comment out to skip
    # leads = search_leads_direct("Chennai", "Office", limit=3)
    # print(f"Found {len(leads)} leads")
    
    print("SUCCESS: Exa search tool ready (API call skipped for testing)")
except Exception as e:
    print(f"FAILED: {e}")

# Test 3: Test Supabase storage tool
print("\n" + "=" * 60)
print("Test 3: Testing Supabase storage tool...")
print("=" * 60)

try:
    from agno_tools.supabase_storage import save_leads_direct
    
    # Test with mock data
    test_leads = [
        {
            "company": "Test Company",
            "website": "https://test.com",
            "intent_signal": "New office opening",
            "intent_score": 9,
            "city": "Test City",
            "segment": "Office",
            "decision_maker": "Procurement Manager"
        }
    ]
    
    result = save_leads_direct(test_leads)
    print(f"Result: {result}")
    print("SUCCESS: Supabase storage tool ready")
except Exception as e:
    print(f"FAILED: {e}")

# Test 4: Test lead scorer tool
print("\n" + "=" * 60)
print("Test 4: Testing lead scorer tool...")
print("=" * 60)

try:
    from agno_tools.lead_scorer import score_leads_direct, filter_high_intent_leads_direct
    
    test_leads = [
        {"company": "High Intent", "intent_signal": "Grand opening next month", "intent_score": 5},
        {"company": "Low Intent", "intent_signal": "Planning phase", "intent_score": 5},
    ]
    
    scored = score_leads_direct(test_leads)
    filtered = filter_high_intent_leads_direct(test_leads)
    
    print(f"Scored leads: {scored}")
    print(f"Filtered: {filtered['summary']}")
    print("SUCCESS: Lead scorer tools ready")
except Exception as e:
    print(f"FAILED: {e}")

# Test 5: Test Agno agent creation
print("\n" + "=" * 60)
print("Test 5: Testing Agno agent creation...")
print("=" * 60)

try:
    from agno_agent import lead_hunter_agent
    
    print(f"Agent name: {lead_hunter_agent.name}")
    print(f"Agent model: {lead_hunter_agent.model}")
    print(f"Number of tools: {len(lead_hunter_agent.tools)}")
    print("SUCCESS: Agno agent created successfully")
except Exception as e:
    print(f"FAILED: {e}")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("""
All tests completed! To run the full integration:

1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variables in .env:
   - EXA_API_KEY
   - SUPABASE_URL
   - SUPABASE_KEY
   - OPENAI_API_KEY (or your preferred model)

3. Run the agent:
   python agno_agent.py

4. To integrate with Telegram bot, add this to bot.py:
   
   from agno_agent import run_agent
   
   async def hunt_command_agno(update, context):
       response = run_agent(f"Hunt for {segment} leads in {city}")
       await context.bot.send_message(chat_id=update.effective_chat.id, text=response.content)
""")
