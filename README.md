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
- Change categories: **New Incorporation**, **Deregistered**, **Field Update**
- Structured change logs with:  
  `CIN, Change_Type, Field_Changed, Old_Value, New_Value, Date`
- Enrichment for **50–100** changed companies using public sources
- **Daily AI Summary** (JSON/TXT): totals & notable changes
- **Streamlit Dashboard**: search, filters, change history, summaries, chat
- **Optional REST API**: `/search_company?cin=...` or `?name=...`
- **SQLite** master DB for reproducibility & auditability

---

## 🏗️ Architecture

<img width="564" height="798" alt="image" src="https://github.com/user-attachments/assets/d1b1cb23-443a-4ba5-92f3-12d3fd637e74" />

---

## ⚙️ Setup

> Requires **Python 3.10+**

```bash
# Go into the inner project folder
cd mca_insights_engine

# Create and activate venv
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
python sample_data_generator.py
python run_pipeline.py
<img width="520" height="301" alt="image" src="https://github.com/user-attachments/assets/060a907a-f6d5-4780-a0b3-398c12932bc4" />
# Run:

python run_pipeline.py

# Streamlit Dashboard
cd mca_insights_engine
streamlit run apps/dashboard_app.py

Dashboard
<img width="1886" height="884" alt="image" src="https://github.com/user-attachments/assets/1e433029-9982-4976-8f38-cec3544bb7c6" />


