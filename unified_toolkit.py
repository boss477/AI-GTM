from agno.tools import Toolkit
from agno.utils.log import logger
import sys
import os

# Ensure we can import from existing directories
sys.path.append(os.path.abspath("strategist_agent"))
sys.path.append(os.path.abspath("hunter-agent"))
sys.path.append(os.path.abspath("invoice_system"))

import uuid

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
        
        # Register Image Upload tool
        self.register(self.upload_furniture_image)

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

    def create_telegram_invoice(self, public_url: str, price: int):
        try:
            # We'll use absolute paths just to be safe
            import os
            original_dir = os.getcwd()
            os.chdir("invoice_system")
            
            order_data = {
                "customer_name": "Telegram Customer",
                "customer_email": "telegram@example.com",
                "order_value": price,
                "line_items": [{
                    "sno": 1,
                    "description": "Telegram Furniture Request",
                    "picture": public_url,
                    "size": "TBD",
                    "upholstery_top": "TBD",
                    "base": "TBD",
                    "leg_polish": "TBD",
                    "units": 1,
                    "net_price": price,
                    "total": price,
                    "remark": "Requested via Telegram"
                }]
            }
            try:
                res = invoice_supabase.table('orders').insert(order_data).execute()
                order_id = res.data[0]['id']
            except Exception as e:
                # If we get a duplicate key error (common in Supabase when sequences are out of sync)
                if "duplicate key" in str(e).lower() or "23505" in str(e):
                    logger.warning("Duplicate key detected. Fetching max ID and retrying manually...")
                    max_id_res = invoice_supabase.table('orders').select('id').order('id', desc=True).limit(1).execute()
                    next_id = (max_id_res.data[0]['id'] + 1) if max_id_res.data else 1
                    order_data['id'] = next_id
                    res = invoice_supabase.table('orders').insert(order_data).execute()
                    order_id = res.data[0]['id']
                else:
                    raise e
            
            result = create_invoice(order_id)
            
            os.chdir(original_dir) # switch back
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            # Since create_invoice ran in 'invoice_system', the relative path returned is
            # starting from there. We'll make it an absolute path.
            pdf_path_abs = os.path.join(original_dir, "invoice_system", result["pdf_file"])
            result["absolute_pdf_path"] = pdf_path_abs
            return result
        except Exception as e:
            logger.error(f"Telegram Invoice error: {e}")
            return f"Error creating telegram invoice: {str(e)}"

    def upload_furniture_image(self, file_bytes: bytes, filename: str = None) -> str:
        """
        Uploads a furniture image (e.g. a chair) to the Supabase 'chairs' storage bucket.
        Returns the public URL of the uploaded image.
        """
        logger.info("Uploading furniture image to Supabase Storage (chairs bucket)...")
        try:
            if not filename:
                filename = f"img_{uuid.uuid4().hex[:8]}.jpg"
                
            response = invoice_supabase.storage.from_("chairs").upload(
                file=file_bytes,
                path=filename,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Construct public URL (assuming bucket is public)
            public_url = invoice_supabase.storage.from_("chairs").get_public_url(filename)
            logger.info(f"Image uploaded successfully: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return f"Error uploading image: {str(e)}"
