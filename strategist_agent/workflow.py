from agno.agent import Agent
from agno.utils.log import logger
from supabase import create_client, Client
from tools import StrategistTools
import os
import json
import socket
from urllib.parse import urlparse
from typing import Optional

# Loading environment variables
load_dotenv()

# Hunter Agent's Supabase (Source of Leads)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate Supabase connectivity at startup
supabase: Optional[Client] = None
hostname = urlparse(SUPABASE_URL).hostname
try:
    socket.getaddrinfo(hostname, 443)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except socket.gaierror as e:
    logger.error(f"Hunter Supabase UNREACHABLE: {hostname} - {e}")
    logger.error(
        "Check if the Supabase project exists at https://supabase.com/dashboard"
    )
except Exception as e:
    logger.error(f"Failed to initialize Supabase: {e}")
    supabase = None


class StrategistWorkflow:
    def __init__(self):
        self.tools = StrategistTools()

    def get_recent_leads(self, limit=5):
        """Fetch recent leads from Hunter Agent's Supabase table."""
        if not supabase:
            logger.error("Supabase client is not initialized. Cannot fetch leads.")
            return []
        try:
            # Fetch latest 5 leads
            response = (
                supabase.table("leads")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            return []

    def get_outcomes_context(self):
        """Read outcomes.md to provide self-learning context."""
        if os.path.exists("outcomes.md"):
            with open("outcomes.md", "r", encoding="utf-8") as f:
                return f.read()
        return "No past outcomes recorded yet."

    def run(self):
        """Execute the Strategist Workflow."""
        print("Starting Strategist Agent Check...")

        leads = self.get_recent_leads()
        if not leads:
            print("No leads found in Supabase.")
            return

        outcomes_context = self.get_outcomes_context()
        print(f"Found {len(leads)} leads. Processing with context from outcomes.md...")

        for lead in leads:
            company = lead.get("company")
            website = lead.get("website")
            lead_id = lead.get("id")  # Get the ID

            if not company:
                continue

            print(f"Processing: {company}...")

            # Step 1: Enrich and Plan Strategy (passing ID and supabase client)
            enriched_json = self.tools.enrich_lead(
                company,
                website,
                outcomes_context,
                lead_id=lead_id,
                supabase_client=supabase,
            )

            # Step 2: Save to great.md
            result = self.tools.save_to_great_md(enriched_json)
            print(f"  -> {result}")


if __name__ == "__main__":
    workflow = StrategistWorkflow()
    workflow.run()
