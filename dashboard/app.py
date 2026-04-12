from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from supabase import create_client, Client
import os
import json
import re
import subprocess
import socket
from datetime import datetime, timezone
from dotenv import load_dotenv
from agno.tools.exa import ExaTools

app = Flask(__name__)
app.secret_key = "super_secret_key_for_demo_session"  # Required for session
load_dotenv()


def check_supabase_reachable(url, name):
    """Check if Supabase URL is DNS-resolvable and reachable before creating client."""
    from urllib.parse import urlparse

    hostname = urlparse(url).hostname
    try:
        socket.getaddrinfo(hostname, 443)
        print(f"[OK] {name} Supabase reachable: {hostname}")
        return True
    except socket.gaierror as e:
        print(f"[FAIL] {name} Supabase UNREACHABLE: {hostname} - {e}")
        print(f"  -> Check if the Supabase project exists and the URL is correct.")
        return False


def get_supabase_client(url, key, name):
    if not url or not key:
        print(f"Critical: Missing URL or key for Supabase {name}")
        return None
    if not check_supabase_reachable(url, name):
        print(f"Critical: Cannot reach Supabase {name} at {url}")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Critical: Failed to initialize Supabase {name}: {e}")
        return None


# Hunter Agent Supabase
HUNTER_URL = "https://wpceiqvcdxdnpvfbqxot.supabase.co"
HUNTER_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY2VpcXZjZHhkbnB2ZmJxeG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTAyMTcsImV4cCI6MjA4NjcyNjIxN30.ppvw-2QdVdxWMXkDzVd98yKDUdAbic2YzP3HpyGAHCk"
EXA_API_KEY = "a4760db1-3cec-4897-9cd7-3be40b7c61eb"

hunter_db = get_supabase_client(HUNTER_URL, HUNTER_KEY, "Hunter")
exa_tools = ExaTools(api_key=EXA_API_KEY, text=True)

# Invoice Agent Supabase
INVOICE_URL_HARDCODED = "https://uiqzkfawnswsrhxkambl.supabase.co"
INVOICE_KEY_HARDCODED = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVpcXprZmF3bnN3c3JoeGthbWJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA5MDU1MjcsImV4cCI6MjA4NjQ4MTUyN30.yhXrNZFnKIioIdClEU7OWGdzJKmjXp7NUluhgRkRR8g"
invoice_db = get_supabase_client(
    INVOICE_URL_HARDCODED, INVOICE_KEY_HARDCODED, "Invoice"
)


# Global Error Handler: Prevents the server from exiting on uncaught exceptions
@app.errorhandler(500)
@app.errorhandler(Exception)
def handle_error(e):
    print(f"Global Error Caught: {e}")
    # Instead of crashing, we gracefully inform the user
    return (
        f"<h3>⚠️ Internal Dashboard Error</h3><p>{str(e)}</p><p><a href='/'>Click here to refresh and try again.</a></p>",
        500,
    )


# ... (Helper functions: build_query, score_intent, extract_company_name, hunter_agent_search remain same) ...
# Copying existing helpers just to be safe with context replacement
def build_query(city, segment):
    if segment == "Coworking":
        return f"{city} coworking space opening OR expansion OR new center"
    elif segment == "Architect":
        return f"{city} design and build commercial office fit-out project"
    elif segment == "Corporate":
        return f"{city} new office campus expansion facility manager"
    return f"{city} office expansion"


def score_intent(text):
    text = text.lower()
    if "expansion" in text or "new office" in text or "opening" in text:
        return 9
    if "renovation" in text or "fit-out" in text:
        return 7
    return 4


def extract_company_name(title):
    keywords = ["adds", "expands", "opens", "enters", "launches", "debuts"]
    title_lower = title.lower()
    for word in keywords:
        if word in title_lower:
            index = title_lower.index(word)
            return title[:index].strip()
    return " ".join(title.split()[:3])


def hunter_agent_search(city, segment, limit):
    query = build_query(city, segment)
    search_results_json = exa_tools.search_exa(query=query, num_results=int(limit))
    try:
        results = json.loads(search_results_json)
    except:
        results = []

    leads = []
    for r in results:
        text_content = r.get("text", "")
        leads.append(
            {
                "company": extract_company_name(r.get("title", "")),
                "website": r.get("url", ""),
                "intent_signal": (text_content or "")[:120],
                "intent_score": score_intent(text_content or ""),
                "city": city,
                "segment": segment,
                "status": "NEW",  # Default status for new leads
            }
        )
    return leads


def parse_strategies():
    strategies = []
    try:
        path = os.path.join(
            os.path.dirname(__file__), "..", "strategist_agent", "great.md"
        )
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        sections = content.split("---")
        for section in sections:
            section = section.strip()
            if not section or not section.startswith("##"):
                continue
            lines = section.split("\n")
            title = lines[0].replace("##", "").strip()
            hook = "N/A"
            reflection = "N/A"
            for i, line in enumerate(lines):
                if "**Hook:**" in line:
                    hook = line.split("**Hook:**")[1].strip()
                if "**Strategy Reflection:**" in line:
                    reflection = line.split("**Strategy Reflection:**")[1].strip()
            strategies.append(
                {"company": title, "hook": hook, "reflection": reflection}
            )
    except:
        pass
    return strategies


@app.route("/")
def dashboard():
    if not hunter_db:
        return (
            "<h3>⚠️ Hunter Supabase is not reachable.</h3>"
            f"<p>URL: {HUNTER_URL}</p>"
            "<p>The Supabase project may be paused, deleted, or the URL is incorrect.</p>"
            "<p>Go to <a href='https://supabase.com/dashboard'>Supabase Dashboard</a> to check your project, then update HUNTER_URL in dashboard/app.py.</p>",
            503,
        )

    query = hunter_db.table("leads").select("*").order("created_at", desc=True)

    last_search_time = session.get("last_search_time")
    search_limit = session.get("search_limit", 10)  # Default to 10 if not set

    if last_search_time:
        # Show leads created AFTER the search button was clicked (with a small buffer)
        query = query.gte("created_at", last_search_time).limit(int(search_limit))
    else:
        # Fallback: Show latest 10
        query = query.limit(10)

    try:
        leads = query.execute().data
    except Exception as e:
        print(f"Error fetching leads: {e}")
        leads = []

    if not invoice_db:
        invoices = []
    else:
        try:
            invoices = (
                invoice_db.table("invoices")
                .select("*")
                .order("created_at", desc=True)
                .limit(5)
                .execute()
                .data
            )
        except Exception as e:
            print(f"Error fetching invoices: {e}")
            invoices = []

    strategies = parse_strategies()
    return render_template(
        "dashboard.html", leads=leads, invoices=invoices, strategies=strategies
    )


@app.route("/search-leads", methods=["POST"])
def search_leads():
    city = request.form.get("city")
    segment = request.form.get("segment")
    limit = request.form.get("limit", 5)

    session["last_search_time"] = datetime.now(timezone.utc).isoformat()
    session["search_limit"] = limit

    if not hunter_db:
        return jsonify(
            {
                "status": "error",
                "message": f"Hunter Supabase is not reachable at {HUNTER_URL}. "
                "Check if the project exists at https://supabase.com/dashboard",
            }
        ), 503

    try:
        leads = hunter_agent_search(city, segment, limit)
        for lead in leads:
            try:
                hunter_db.table("leads").insert(lead).execute()
            except Exception as e:
                print(f"Error inserting individual lead: {e}")
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Error searching leads: {e}")
        return jsonify(
            {"status": "error", "message": f"Search failed (Network Error): {str(e)}"}
        )


@app.route("/run-strategist", methods=["POST"])
def run_strategist():
    try:
        path = os.path.join(os.path.dirname(__file__), "..", "strategist_agent")
        subprocess.run(["python", "workflow.py"], cwd=path)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/create-invoice", methods=["POST"])
def create_invoice_route():
    order_id = request.form.get("order_id")
    if not order_id:
        return jsonify({"status": "error", "message": "Order ID is required"})

    try:
        path = os.path.join(os.path.dirname(__file__), "..", "invoice_system")
        result = subprocess.run(
            ["python", "manual_run.py", "create", order_id],
            cwd=path,
            capture_output=True,
            text=True,
        )

        if "Invoice created successfully" in result.stdout:
            return redirect(url_for("dashboard"))
        else:
            err_msg = f"{result.stdout}\n{result.stderr}".strip()
            return jsonify(
                {"status": "error", "message": err_msg}
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/reset-dashboard", methods=["POST"])
def reset_dashboard():
    session.clear()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
