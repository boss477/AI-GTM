from agno.tools import Toolkit
from agno.utils.log import logger
import sys
import os

# Ensure we can import from existing directories
sys.path.append(os.path.abspath("strategist_agent"))
sys.path.append(os.path.abspath("hunter-agent"))
sys.path.append(os.path.abspath("invoice_system"))

# Existing imports
from strategist_agent.tools import StrategistTools
from hunter_agent.app import hunter_agent, save_leads_to_supabase
from invoice_system.invoice_service import create_invoice, supabase as invoice_supabase

class UnifiedToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="unified_toolkit")
        self.strategist_tools = StrategistTools()
        
        # Register Strategist tools
        self.register(self.strategist_tools.enrich_lead)
        self.register(self.strategist_tools.save_to_great_md)
        
        # Register Hunter tool
        self.register(self.hunt_leads)
        
        # Register Invoice tool
        self.register(self.manage_invoice)

    def hunt_leads(self, city: str, segment: str, limit: int = 5) -> str:
        """
        Searches for new business leads (Hunter Agent).
        Returns a summary of leads found and saved to Supabase.
        """
        logger.info(f"Hunting for {segment} leads in {city}...")
        try:
            leads = hunter_agent(city, segment, limit)
            save_leads_to_supabase(leads, city, segment)
            return f"Found {len(leads)} leads in {city} ({segment}). Saved to database."
        except Exception as e:
            logger.error(f"Hunter error: {e}")
            return f"Error hunting leads: {str(e)}"

    def manage_invoice(self, order_id: str, action: str = "create") -> str:
        """
        Manages invoicing (Invoice Agent).
        Currently supports 'create' action for a given order ID.
        """
        logger.info(f"Invoice action '{action}' for order {order_id}...")
        try:
            if action.lower() == "create":
                result = create_invoice(order_id)
                if "error" in result:
                    return f"Error: {result['error']}"
                return f"Invoice {result['invoice_number']} created successfully and sent to client."
            else:
                return f"Action '{action}' not yet supported. Use 'create' for now."
        except Exception as e:
            logger.error(f"Invoice error: {e}")
            return f"Error managing invoice: {str(e)}"
