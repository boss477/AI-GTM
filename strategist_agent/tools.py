from agno.tools import Toolkit
from agno.utils.log import logger
import httpx
import json

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Perplexity API Key
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

class StrategistTools(Toolkit):
    def __init__(self):
        super().__init__(name="strategist_tools")
        self.register(self.enrich_lead)
        self.register(self.save_to_great_md)

    def enrich_lead(self, company_name: str, website: str, outcomes_context: str = "", lead_id: int = None, supabase_client = None) -> str:
        """
        Enriches lead data using Perplexity API with self-learning context.
        Found verified contact info, business context, and personalized outreach hook.
        
        Args:
            company_name (str): Name of the company.
            website (str): Website URL.
            outcomes_context (str): Past outcomes from outcomes.md to inform the strategy.
            lead_id (int): ID of the lead in Supabase (optional).
            supabase_client: Supabase client instance (optional).
            
        Returns:
            str: JSON string containing enriched data.
        """
        logger.info(f"Enriching lead: {company_name}...")
        
        # Mark as PROCESSING
        if lead_id and supabase_client:
            try:
                supabase_client.table("leads").update({"status": "PROCESSING"}).eq("id", lead_id).execute()
            except Exception as e:
                logger.warning(f"Failed to update status to PROCESSING: {e}")

        prompt = (
            f"Analyze these past outreach outcomes to act as a self-learning agent:\n"
            f"{outcomes_context}\n\n"
            f"Based on what worked or failed above, research the company '{company_name}' (Website: {website}). "
            f"Find the following information for a B2B furniture sales outreach:\n"
            f"1. Verified Company Name & Location\n"
            f"2. Contact Information (Prioritize: Email, Phone, LinkedIn of decision makers like Office Manager, CEO, Founder)\n"
            f"3. Business focus/positioning\n"
            f"4. Size/Scale\n"
            f"5. Suggest a personalized outreach hook based on their recent news/projects AND successful past strategies.\n"
            f"6. Explicitly state why you chose this strategy based on past outcomes (Reflection).\n\n"
            f"Return the response as JSON with keys: 'company_name', 'location', 'contact_info', 'business_summary', 'outreach_hook', 'channel_suggestion', 'reflection'."
        )

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        }
            
        payload = {
            "model": "sonar-pro", 
            "messages": [
                {"role": "system", "content": "You are a B2B sales strategist. Be precise and find actionable contact info. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = httpx.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            # Clean up JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Mark as SELECTED if successful
            if lead_id and supabase_client:
                try:
                    supabase_client.table("leads").update({"status": "SELECTED"}).eq("id", lead_id).execute()
                except Exception as e:
                    logger.warning(f"Failed to update status to SELECTED: {e}")

            return content
        except Exception as e:
            logger.error(f"Error enriching {company_name}: {e}")
            # Mark as FAILED or IGNORED
            if lead_id and supabase_client:
                try:
                    supabase_client.table("leads").update({"status": "FAILED"}).eq("id", lead_id).execute()
                except: pass
            return json.dumps({"company_name": company_name, "error": str(e)})

    def save_to_great_md(self, enriched_data_json: str):
        """
        Saves the enriched lead strategy to great.md file.
        
        Args:
            enriched_data_json (str): JSON string returned by enrich_lead.
        """
        try:
            data = json.loads(enriched_data_json)
            if "error" in data:
                logger.warning(f"Skipping save for {data['company_name']} due to error.")
                return "Skipped due to error"

            content = f"## {data.get('company_name', 'Unknown')}\n\n"
            content += f"**Location:** {data.get('location', 'N/A')}\n\n"
            content += f"**Business Summary:**\n{data.get('business_summary', 'N/A')}\n\n"
            content += f"**Contact Info:**\n{data.get('contact_info', 'N/A')}\n\n"
            content += f"**Outreach Strategy:**\n"
            content += f"- **Channel:** {data.get('channel_suggestion', 'Email')}\n"
            content += f"- **Hook:** {data.get('outreach_hook', 'N/A')}\n"
            content += f"- **Strategy Reflection:** {data.get('reflection', 'N/A')}\n\n"
            content += "---\n\n"
            
            with open("great.md", "a", encoding="utf-8") as f:
                f.write(content)
            
            return "Strategy saved to great.md"
        except Exception as e:
            return f"Error saving to file: {str(e)}"
