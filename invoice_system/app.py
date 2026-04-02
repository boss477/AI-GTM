from flask import Flask, request, jsonify, render_template
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json

# Import internal modules
from invoice_service import create_invoice
from scheduler import start_scheduler, check_overdue_invoices

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env file. "
        f"SUPABASE_URL={'set' if SUPABASE_URL else 'MISSING'}, "
        f"SUPABASE_KEY={'set' if SUPABASE_KEY else 'MISSING'}"
    )

# Create Supabase client (still needed for dashboard view)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create Flask app
app = Flask(__name__)

# Start scheduler automatically when app starts
start_scheduler()


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------
@app.route("/")
def home():
    return "Invoice System Running 🚀"


# --------------------------------------------------
# DASHBOARD VIEW
# --------------------------------------------------
@app.route("/dashboard")
def dashboard():
    try:
        invoices = supabase.table("invoices").select("*").execute().data
        alerts = (
            supabase.table("alerts").select("*").eq("resolved", False).execute().data
        )

        return render_template("dashboard.html", invoices=invoices, alerts=alerts)
    except Exception as e:
        return str(e), 500


# --------------------------------------------------
# HEALTH CHECK ROUTE
# --------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "running", "time": datetime.now().isoformat()})


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
