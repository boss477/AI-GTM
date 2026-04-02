from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from supabase import create_client
from email_service import send_email
import os
from dotenv import load_dotenv

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


def check_overdue_invoices():
    print("Running Overdue Check...")

    invoices = (
        supabase.table("invoices").select("*").neq("status", "PAID").execute().data
    )

    for invoice in invoices:
        due_date = datetime.strptime(str(invoice["due_date"]), "%Y-%m-%d").date()
        today = datetime.now().date()

        days_overdue = (today - due_date).days

        if days_overdue > 0:
            supabase.table("invoices").update({"days_overdue": days_overdue}).eq(
                "id", invoice["id"]
            ).execute()

            handle_reminders(invoice, days_overdue)


def handle_reminders(invoice, days_overdue):

    customer = (
        supabase.table("orders")
        .select("*")
        .eq("id", invoice["order_id"])
        .execute()
        .data[0]
    )

    if days_overdue == 3:
        send_reminder(customer, invoice, "Friendly Reminder")

    elif days_overdue == 7:
        send_reminder(customer, invoice, "Firm Reminder")

    elif days_overdue >= 14:
        send_reminder(customer, invoice, "Urgent Reminder")
        create_risk_alert(invoice)


def send_reminder(customer, invoice, reminder_type):

    subject = f"{reminder_type}: Invoice {invoice['invoice_number']}"
    body = f"""
    Hi {customer["customer_name"]},

    Invoice {invoice["invoice_number"]} is overdue by {invoice["days_overdue"]} days.
    Kindly process payment at the earliest.

    Thank you.
    """

    send_email(customer["customer_email"], subject, body)

    supabase.table("invoices").update(
        {"reminders_sent": invoice["reminders_sent"] + 1}
    ).eq("id", invoice["id"]).execute()


def create_risk_alert(invoice):

    severity = "HIGH"

    if invoice["total_amount"] >= 2000000 and invoice["days_overdue"] >= 15:
        severity = "CRITICAL"

    supabase.table("invoices").update({"risk_level": severity}).eq(
        "id", invoice["id"]
    ).execute()

    supabase.table("alerts").insert(
        {
            "invoice_id": invoice["id"],
            "severity": severity,
            "message": f"Invoice {invoice['invoice_number']} is {severity} risk.",
        }
    ).execute()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_overdue_invoices, "interval", hours=24)
    scheduler.start()
