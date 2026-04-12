"""
invoice_service.py  –  Invoice orchestration layer
Fetches order data from Supabase, builds the Performa Invoice PDF,
saves a record, and sends the email.
"""

import os
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import create_client

from invoice_pdf import generate_performa_invoice, generate_invoice
from email_service import send_email

load_dotenv()

SUPABASE_URL = os.getenv("INVOICE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("INVOICE_SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "INVOICE_SUPABASE_URL and INVOICE_SUPABASE_KEY must be set in environment variables or .env file. "
        f"URL={'set' if SUPABASE_URL else 'MISSING'}, "
        f"KEY={'set' if SUPABASE_KEY else 'MISSING'}"
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
# Default seller / bank info (override via DB or env)
# ─────────────────────────────────────────────
DEFAULT_SELLER = {
    "name":    os.getenv("SELLER_NAME",    "SHEARLING SKINS PVT LTD"),
    "address": os.getenv("SELLER_ADDRESS", "PLOT NO 84 SECTOR 8 IMT MANESAR GURGAON(HR) PINCODE-122052"),
    "gstin":   os.getenv("SELLER_GSTIN",   "06AALCS1032L1ZC"),
}

DEFAULT_CONTACT = {
    "person": os.getenv("CONTACT_PERSON", "Ms. TANNU PHOGAT"),
    "mobile": os.getenv("CONTACT_MOBILE", "9910088313"),
    "email":  os.getenv("CONTACT_EMAIL",  "be1@shearling.in"),
}

DEFAULT_BANK = {
    "beneficiary_name": os.getenv("BANK_BENEFICIARY", "SHEARLING SKINS PVT LTD"),
    "bank_name":        os.getenv("BANK_NAME",        "DEUTSCHE BANK"),
    "account_no":       os.getenv("BANK_ACCOUNT",     "100041596120019"),
    "ifsc_code":        os.getenv("BANK_IFSC",        "DEUT0784PBC"),
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _generate_pi_number():
    today  = datetime.now().strftime("%Y%m%d")
    unique = datetime.now().strftime("%H%M%S")
    return f"{today}-{unique}"


def _parse_line_items(order: dict) -> list:
    """
    Try to extract furniture line items from the order.
    Supports:
      • order["line_items"]  – JSON array stored in Supabase column
      • Fallback: single-item from legacy order_value / milestone_percentage
    """
    raw = order.get("line_items")

    if raw:
        items = json.loads(raw) if isinstance(raw, str) else raw
        enriched = []
        for i, item in enumerate(items, 1):
            net  = float(item.get("net_price", 0))
            units = int(item.get("units", 1))
            enriched.append({
                "sno":           item.get("sno", i),
                "description":   item.get("description", ""),
                "picture":       item.get("picture", None),
                "size":          item.get("size", ""),
                "upholstery_top": item.get("upholstery_top", ""),
                "base":          item.get("base", ""),
                "leg_polish":    item.get("leg_polish", ""),
                "units":         units,
                "net_price":     net,
                "total":         float(item.get("total", net * units)),
                "remark":        item.get("remark", ""),
            })
        return enriched

    # Legacy fallback – single milestone line item
    order_value = float(order.get("order_value") or 0)
    milestone   = float(order.get("milestone_percentage") or 1.0)
    amount      = order_value * milestone
    return [{
        "sno":           1,
        "description":   "Milestone Payment",
        "picture":       None,
        "size":          "",
        "upholstery_top": "",
        "base":          "",
        "leg_polish":    "",
        "units":         1,
        "net_price":     amount,
        "total":         amount,
        "remark":        "",
    }]


# ─────────────────────────────────────────────
# Main service function
# ─────────────────────────────────────────────
def create_invoice(order_id):
    # ── 1. Fetch Order ──────────────────────────
    order_resp = supabase.table("orders").select("*").eq("id", order_id).execute()
    if not order_resp.data:
        return {"error": f"Order {order_id} not found"}

    order = order_resp.data[0]

    # ── 2. Build invoice metadata ────────────────
    pi_number = _generate_pi_number()
    revision  = order.get("revision", 1)
    pi_date   = datetime.now().strftime("%d %b %Y")

    # ── 3. Build customer / contact blocks ───────
    customer = {
        "name":           order.get("customer_name", ""),
        "contact_person": order.get("customer_contact_person", ""),
        "address":        order.get("customer_address", ""),
        "mobile":         order.get("customer_mobile", ""),
        "email":          order.get("customer_email", ""),
    }

    # Allow per-order overrides; fall back to defaults
    seller = {
        "name":    order.get("seller_name",    DEFAULT_SELLER["name"]),
        "address": order.get("seller_address", DEFAULT_SELLER["address"]),
        "gstin":   order.get("seller_gstin",   DEFAULT_SELLER["gstin"]),
    }
    contact = {
        "person": order.get("contact_person", DEFAULT_CONTACT["person"]),
        "mobile": order.get("contact_mobile", DEFAULT_CONTACT["mobile"]),
        "email":  order.get("contact_email",  DEFAULT_CONTACT["email"]),
    }
    bank = {
        "beneficiary_name": order.get("bank_beneficiary", DEFAULT_BANK["beneficiary_name"]),
        "bank_name":        order.get("bank_name",        DEFAULT_BANK["bank_name"]),
        "account_no":       order.get("bank_account",     DEFAULT_BANK["account_no"]),
        "ifsc_code":        order.get("bank_ifsc",        DEFAULT_BANK["ifsc_code"]),
    }

    # ── 4. Parse line items ───────────────────────
    line_items   = _parse_line_items(order)
    total_amount = sum(item["total"] for item in line_items)

    # Performa totals
    packaging    = total_amount * 0.03
    subtotal     = total_amount + packaging
    gst          = subtotal * 0.18
    grand_total  = subtotal + gst

    # ── 5. Save invoice record to Supabase ────────
    due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    invoice_data = {
        "order_id":       order_id,
        "invoice_number": f"PI-{pi_number}",
        "subtotal":       round(subtotal, 2),
        "tax":            round(gst, 2),
        "total_amount":   round(grand_total, 2),
        "due_date":       due_date,
        "status":         "UNPAID",
    }
    invoice_resp = supabase.table("invoices").insert(invoice_data).execute()
    invoice      = invoice_resp.data[0]

    # ── 6. Generate PDF ───────────────────────────
    logo_path = order.get("logo_path", None)
    pdf_file  = generate_performa_invoice(
        pi_number    = pi_number,
        revision     = revision,
        pi_date      = pi_date,
        seller       = seller,
        customer     = customer,
        contact      = contact,
        line_items   = line_items,
        bank_details = bank,
        logo_path    = logo_path,
    )

    # ── 7. Send Email ─────────────────────────────
    subject = f"Performa Invoice PI#{pi_number} – {seller['name']}"
    body = f"""Hi {customer['name']},

Please find your Performa Invoice attached.

PI Number  : PI#{pi_number}
Date       : {pi_date}
Grand Total: Rs. {grand_total:,.2f}
Due Date   : {due_date}

Best regards,
{contact['person']}
{seller['name']}
"""
    send_email(customer["email"], subject, body, attachment=pdf_file)

    # ── 8. Mark sent date ─────────────────────────
    supabase.table("invoices").update({"sent_date": datetime.now().isoformat()}).eq(
        "id", invoice["id"]
    ).execute()

    return {
        "message":        "Performa Invoice created successfully",
        "invoice_number": f"PI-{pi_number}",
        "grand_total":    round(grand_total, 2),
        "pdf_file":       pdf_file,
    }
