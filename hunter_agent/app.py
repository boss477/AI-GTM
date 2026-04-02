from flask import Flask, render_template, request
from agno.tools.exa import ExaTools
from supabase import create_client, Client
import os
import json
import re

app = Flask(__name__)

# ---------------------------
# Initialize Exa via Agno Tools
# ---------------------------
# Note: In a production environment, use environment variables for keys
EXA_API_KEY = "a4760db1-3cec-4897-9cd7-3be40b7c61eb"
exa_tools = ExaTools(api_key=EXA_API_KEY, text=True)

# Supabase config
SUPABASE_URL = "https://wpceiqvcdxdnpvfbqxot.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwY2VpcXZjZHhkbnB2ZmJxeG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTAyMTcsImV4cCI6MjA4NjcyNjIxN30.ppvw-2QdVdxWMXkDzVd98yKDUdAbic2YzP3HpyGAHCk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------
# Build Search Query
# ---------------------------
def build_query(city, segment):
    if segment == "Coworking":
        return f"{city} coworking space opening OR expansion OR new center"
    elif segment == "Architect":
        return f"{city} design and build commercial office fit-out project"
    elif segment == "Corporate":
        return f"{city} new office campus expansion facility manager"
    else:
        return f"{city} office expansion"

# ---------------------------
# Intent Scoring
# ---------------------------
def score_intent(text):
    text = text.lower()

    if "expansion" in text or "new office" in text or "opening" in text:
        return 9
    if "renovation" in text or "fit-out" in text:
        return 7
    return 4


def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)   # remove brackets content
    text = re.sub(r"\*+", "", text)       # remove stars
    text = re.sub(r"Advertisement", "", text, flags=re.IGNORECASE)
    return text.strip()

def extract_company_name(title):
    keywords = ["adds", "expands", "opens", "enters", "launches", "debuts"]

    title_lower = title.lower()

    for word in keywords:
        if word in title_lower:
            index = title_lower.index(word)
            return title[:index].strip()

    # fallback: first 3 words
    return " ".join(title.split()[:3])

def save_leads_to_supabase(leads, city, segment):
    for lead in leads:
        # Check for duplicates in DB before inserting if needed, 
        # but for now we just insert as per original logic, 
        # relying on the frontend/agent deduplication for the current run.
        supabase.table("leads").insert({
            "company": lead["company"],
            "website": lead["website"],
            "intent_signal": lead["intent_signal"],
            "intent_score": lead["intent_score"],
            "city": city,
            "segment": segment
        }).execute()


# ---------------------------
# Hunter Agent Logic
# ---------------------------
def hunter_agent(city, segment, limit):
    query = build_query(city, segment)
    
    # Use Agno's ExaTools to search
    # search_exa returns a JSON string, so we need to parse it
    search_results_json = exa_tools.search_exa(query=query, num_results=int(limit))
    try:
        results = json.loads(search_results_json)
    except json.JSONDecodeError:
        results = []

    leads = []

    for r in results:
        # ExaTools returns a list of dictionaries with 'url', 'title', 'text', etc.
        text_content = r.get("text", "")
        cleaned_text = clean_text(text_content or "")
        score = score_intent(cleaned_text)
        
        title = r.get("title", "")
        
        leads.append({
            "company": extract_company_name(title),
            "website": r.get("url", ""),
            "intent_signal": cleaned_text[:120],
            "intent_score": score
        })


    # Deduplication: Remove duplicates based on company name
    unique_leads = {}
    for lead in leads:
        company = lead["company"]
        # If company not seen, or if seen but new one has higher score (optional logic, here simpler)
        if company not in unique_leads:
             unique_leads[company] = lead
        else:
            # If we want to keep the one with higher score
            if lead["intent_score"] > unique_leads[company]["intent_score"]:
                unique_leads[company] = lead
    
    leads = list(unique_leads.values())

    # Sort by highest intent
    leads = sorted(leads, key=lambda x: x["intent_score"], reverse=True)

    return leads


@app.route("/", methods=["GET", "POST"])
def index():
    leads = []

    if request.method == "POST":
        city = request.form["city"]
        segment = request.form["segment"]
        limit = request.form["limit"]

        leads = hunter_agent(city, segment, limit)
        save_leads_to_supabase(leads, city, segment)


    return render_template("index.html", leads=leads)


if __name__ == "__main__":
    app.run(debug=True)

    