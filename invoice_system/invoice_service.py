from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
from invoice_pdf import generate_invoice
from email_service import send_email

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env file. "
        f"SUPABASE_URL={'set' if SUPABASE_URL else 'MISSING'}, "
        f"SUPABASE_KEY={'set' if SUPABASE_KEY else 'MISSING'}"
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_invoice_number():
    today = datetime.now().strftime("%Y%m%d")
    unique = datetime.now().strftime("%H%M%S")
    return f"INV-{today}-{unique}"


def create_invoice(order_id):

    # Fetch Order
    order_response = supabase.table("orders").select("*").eq("id", order_id).execute()

    if not order_response.data:
        return {"error": "Order not found"}

    order = order_response.data[0]

    # Calculations
    subtotal = float(order["order_value"]) * float(order["milestone_percentage"])
    tax = subtotal * 0.18
    total_amount = subtotal + tax

    invoice_number = generate_invoice_number()

    due_date_obj = datetime.now() + timedelta(days=7)
    due_date = due_date_obj.strftime("%Y-%m-%d")  # formatted string

    # Insert Invoice in DB
    invoice_data = {
        "order_id": order_id,
        "invoice_number": invoice_number,
        "subtotal": subtotal,
        "tax": tax,
        "total_amount": total_amount,
        "due_date": due_date,
        "status": "UNPAID",
    }

    invoice_response = supabase.table("invoices").insert(invoice_data).execute()
    invoice = invoice_response.data[0]

    # Generate PDF
    pdf_file = generate_invoice(
        invoice_number,
        order["customer_name"],
        order["customer_email"],
        total_amount,
        due_date,
    )

    # Send Email
    subject = f"Invoice {invoice_number}"

    body = f"""
Hi {order["customer_name"]},

Please find your invoice attached.

Invoice Number: {invoice_number}
Amount: ₹{total_amount:.2f}
Due Date: {due_date}

Thank you.
"""

    send_email(order["customer_email"], subject, body)

    # Update Sent Date
    supabase.table("invoices").update({"sent_date": datetime.now().isoformat()}).eq(
        "id", invoice["id"]
    ).execute()

    return {
        "message": "Invoice created successfully",
        "invoice_number": invoice_number,
        "pdf_file": pdf_file,
    }
