# 🏢 MCA Insights Engine

> A data-driven system that **consolidates**, **tracks**, and **enriches** Ministry of Corporate Affairs (MCA) company master data with daily change detection, AI-powered summaries, and a conversational dashboard.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-ff4b4b.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 📚 Table of Contents
- [Problem Overview](#-problem-overview)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Setup](#-setup)
- [Quick Start (Demo Data)](#-quick-start-demo-data)
- [Using Real MCA Files](#-using-real-mca-files)
- [Workflow Details](#-workflow-details)
- [Enrichment Logic](#-enrichment-logic)
- [Dashboard & API](#-dashboard--api)
- [AI Insight Layer](#-ai-insight-layer)
- [Deliverables Checklist](#-deliverables-checklist)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Credits](#-credits)
- [License](#-license)

---

## 🧩 Problem Overview
MCA publishes company master data as **state-wise CSV files** on data.gov.in.  
Tracking changes (new incorporations, deregistrations, capital/status updates) across states and days is **not feasible manually**. The raw data also lacks context (directors, industry tags, etc.), and evaluators need an **auditable** way to see **what changed, when, and why**.

---

## 🎯 Objectives
Build a Python application that:
1. **Consolidates** & normalizes state-wise MCA data into a master dataset  
2. **Detects** daily per-company changes (new, removed, field updates)  
3. **Enriches** changed records with public web data  
4. **Summarizes** each day automatically (AI-style daily report)  
5. Provides a **Streamlit dashboard** + optional **REST API**  
6. Enables **conversational querying** of the dataset

---

## ✨ Key Features
- Canonical schema across 5 RoC/state datasets: **Maharashtra, Gujarat, Delhi, Tamil Nadu, Karnataka**
- Change categories: **New Incorporation**, **Deregistered**, **Field Update** (e.g., `Company_Status`, `Authorized_Capital`)
- Structured change logs with: `CIN, Change_Type, Field_Changed, Old_Value, New_Value, Date`
- Enrichment for **50–100** changed companies using public sources
- **Daily AI Summary** (JSON/TXT): totals & notable changes
- **Streamlit Dashboard**: search, filters, change history, summaries, chat
- **Optional REST API**: `/search_company?cin=...` or `?name=...`
- **SQLite** master DB for reproducibility & auditability

---

## 🏗️ Architecture

State CSVs (daily snapshots)
│
▼
[Integration & Normalization]
│ -> canonical master (SQLite + CSV)
▼
[Change Detection: day N-1 vs day N]
│ -> CSV change logs (per day)
▼
[Enrichment (50–100 changed CINs)]
│ -> enriched_changes.csv
▼
[AI Summary]
│ -> daily_summary_<date>.json/.txt
▼
[Dashboard (Streamlit)] + [REST API (Flask)]
└── Search, Filters, Change History, Chat

yaml
Copy code

---

## 📁 Project Structure

> **Note:** The codebase uses an inner package folder. Run commands from the **inner** `mca_insights_engine` directory.

MCA_INSIGHTS_ENGINE/
└─ mca_insights_engine/
├─ apps/
│ ├─ dashboard_app.py # Streamlit UI (search, filters, chat, summaries)
│ └─ flask_api.py # Optional REST API wrapper
├─ data/
│ └─ snapshots/ # Daily state CSVs (demo snapshots included via generator)
├─ mca_insights/
│ ├─ init.py
│ ├─ ai_summary.py # Daily summary writer (JSON/TXT)
│ ├─ api.py # Flask app with /search_company
│ ├─ change_detector.py # New/Deregistered/Field updates
│ ├─ config.py # Paths, schema, states
│ ├─ database.py # SQLite (companies, change_log)
│ ├─ enrichers.py # Enrichment (seeded + optional live web)
│ ├─ integrate.py # Consolidate/normalize snapshots
│ └─ utils.py # Helpers
├─ outputs/
│ ├─ changelogs/
│ ├─ enrichment/
│ ├─ summaries/
│ ├─ master.db # Auto-created
│ └─ master_latest.csv # Auto-created
├─ run_pipeline.py # Orchestrates the end-to-end flow
├─ sample_data_generator.py # Creates 3 demo snapshot days for 5 states
├─ requirements.txt
├─ .env.example
├─ LICENSE
└─ README.md

yaml
Copy code

---

## ⚙️ Setup

> Requires **Python 3.10+**

```bash
# 1) Go into the inner project folder (IMPORTANT)
cd mca_insights_engine

# 2) (Recommended) Create and activate a venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt
Optional: copy environment template

bash
Copy code
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
🚀 Quick Start (Demo Data)
The repo includes a generator that creates 3 daily snapshots for the 5 states, so you can run everything end-to-end without external downloads.

bash
Copy code
# from mca_insights_engine/
python sample_data_generator.py

# Run the full pipeline (integrate → detect → enrich → summarize)
python run_pipeline.py
Outputs to verify:

outputs/master_latest.csv and outputs/master.db

outputs/changelogs/changes_2025-10-18.csv, changes_2025-10-19.csv

outputs/enrichment/enriched_changes.csv

outputs/summaries/daily_summary_2025-10-19.json and .txt

📥 Using Real MCA Files
Create folders:

bash
Copy code
data/snapshots/<YYYY-MM-DD>/
Place state-wise CSVs with these exact names:

Copy code
maharashtra.csv
gujarat.csv
delhi.csv
tamil_nadu.csv
karnataka.csv
Then re-run:

bash
Copy code
python run_pipeline.py
The loader normalizes columns to the canonical schema:

javascript
Copy code
CIN, Company_Name, Company_Class, Date_of_Incorporation,
Authorized_Capital, Paidup_Capital, Company_Status,
NIC_Code, Registered_Address, RoC, State
🔄 Workflow Details
1) Integration
Reads each selected state's CSV for a given date

Normalizes types (capital → float), trims/uppercases CIN, dedupes by CIN

Exports master_latest.csv and updates outputs/master.db (table: companies)

2) Change Detection
Compares previous vs current snapshot per CIN

Generates rows with:

javascript
Copy code
CIN, Change_Type, Field_Changed, Old_Value, New_Value, Date
Categories:

New Incorporation (in current but not previous)

Deregistered (in previous but not current)

Field Update (value changed for tracked fields)

Writes CSV per day into outputs/changelogs/

3) Enrichment
For up to 100 changed CINs (latest day), creates enriched_changes.csv with:

objectivec
Copy code
CIN, COMPANY_NAME, STATE, STATUS, SOURCE, FIELD, SOURCE_URL
Default: seeded/deterministic enrichment for offline stability

Optional: live web enrichment (best-effort; set in .env)

ini
Copy code
ENABLE_WEB_ENRICHMENT=true
4) AI Summary
Counts:

New incorporations

Deregistered

Field updates

Writes both JSON and TXT (e.g., daily_summary_2025-10-19.*)

📊 Dashboard & API
Streamlit Dashboard
bash
Copy code
# IMPORTANT: run from the inner mca_insights_engine folder
streamlit run apps/dashboard_app.py
Tabs:

🔎 Explore: search by CIN/Name, filter by Year/State/Status, view change history

💬 Chat with MCA Data: conversational queries (rule-based intents)

📈 Daily Summary: renders JSON summaries

If you prefer to run from another folder, add this to the top of apps/dashboard_app.py:

python
Copy code
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
REST API (Optional)
bash
Copy code
python apps/flask_api.py
# GET http://localhost:8000/search_company?cin=<CIN>
# GET http://localhost:8000/search_company?name=<partial>
Response example:

json
Copy code
{
  "results": [{ "CIN": "UXX...", "Company_Name": "...", "...": "..." }],
  "change_history": [
    { "CIN": "UXX...", "Change_Type": "Field Update", "Field_Changed": "Company_Status", "Old_Value": "Active", "New_Value": "Strike Off", "Date": "2025-10-19" }
  ]
}
🧠 AI Insight Layer
Daily Summary Generator
Produces concise summaries after each update:

yaml
Copy code
New incorporations: 124
Deregistered: 5
Updated records: 42
Stored in outputs/summaries/

Conversational Query (Rule-Based)
Handles prompts like:

“Show new incorporations in Maharashtra”

“How many companies were struck off last month?”

“manufacturing authorized capital above 1000000”

The intent parser can be swapped for an LLM (OpenAI, etc.) with minimal changes. See .env.example.

✅ Deliverables Checklist
 Source code & documentation (this README)

 Processed master dataset (CSV + SQLite)

 Three daily change logs (demo snapshots)

 Enriched dataset for changed CINs

 AI daily summary (TXT/JSON)

 Streamlit dashboard + optional REST API

 Reproducible workflow, clean structure, and auditability

🛠️ Troubleshooting
ModuleNotFoundError: mca_insights

Always run from the inner folder:

bash
Copy code
cd mca_insights_engine
streamlit run apps/dashboard_app.py
Or add to the top of dashboard_app.py:

python
Copy code
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
No outputs created

Ensure you ran:

bash
Copy code
python sample_data_generator.py
python run_pipeline.py
Check write permissions in outputs/

Empty dashboard tables

Verify outputs/master.db exists and outputs/changelogs/*.csv are not empty

🗺️ Roadmap
Scheduled ingestion (cron/Airflow)

Data.gov.in API integration & retries

NIC → Sector mapping expansion

RAG-style LLM Q&A over SQLite

PDF/CSV export of charts & reports

🙏 Credits
Problem statement and evaluation context: Aadiswan

Public sources referenced for enrichment: ZaubaCorp, API Setu, Indian Kanoon, GST Portal, MCA21
