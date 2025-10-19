import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from mca_insights.config import DB_PATH, SELECTED_STATES, MASTER_CSV, SUMMARIES_DIR
from mca_insights.chatbot import interpret_and_execute



st.set_page_config(page_title="MCA Insights Engine", layout="wide")

def _connect():
    return sqlite3.connect(DB_PATH)

st.title("MCA Insights Engine")

tab1, tab2, tab3 = st.tabs(["🔎 Explore", "💬 Chat with MCA Data", "📈 Daily Summary"])

with tab1:
    st.subheader("Search & Filters")
    q = st.text_input("Search by CIN or Company Name")
    cols = st.columns(3)
    with cols[0]:
        year = st.selectbox("Incorporation Year", options=["All"] + [str(y) for y in range(2000, 2026)])
    with cols[1]:
        state = st.selectbox("State", options=["All"] + SELECTED_STATES)
    with cols[2]:
        status = st.selectbox("Company Status", options=["All", "Active", "Strike Off", "Amalgamated", "Dormant"])

    with _connect() as conn:
        df = pd.read_sql_query("SELECT * FROM companies", conn)

    if q:
        if len(q) >= 5:
            df = df[(df['CIN'].str.contains(q.upper())) | (df['Company_Name'].str.contains(q, case=False))]

    if year != "All":
        df = df[df['Date_of_Incorporation'].str.startswith(year)]
    if state != "All":
        df = df[df['State'] == state]
    if status != "All":
        df = df[df['Company_Status'].str.contains(status, case=False, na=False)]

    st.dataframe(df, use_container_width=True, height=400)

    st.markdown("#### Change History (select a CIN)")
    selected_cin = st.text_input("CIN for history")
    if selected_cin:
        with _connect() as conn:
            ch = pd.read_sql_query("SELECT * FROM change_log WHERE CIN = ? ORDER BY Date", conn, params=(selected_cin.upper(),))
        st.dataframe(ch, use_container_width=True, height=300)

with tab2:
    st.subheader("Ask questions in natural language")
    question = st.text_input("e.g., 'Show new incorporations in Maharashtra'")
    if st.button("Ask") and question.strip():
        res = interpret_and_execute(question)
        if 'dataframe' in res:
            st.dataframe(res['dataframe'], use_container_width=True)
            st.success(f"Intent: {res['intent']} — {len(res['dataframe'])} rows")
        elif res.get('intent') == 'company_lookup':
            st.write("**Company**")
            st.dataframe(res['company'], use_container_width=True, height=150)
            st.write("**Change History**")
            st.dataframe(res['changes'], use_container_width=True, height=220)
        elif res.get('intent') == 'name_search':
            st.dataframe(res['dataframe'], use_container_width=True)
        else:
            st.info(res.get('message', 'Sorry, no result.'))

with tab3:
    st.subheader("Daily Summaries")
    files = sorted([p for p in Path(SUMMARIES_DIR).glob("daily_summary_*.json")])
    for f in files:
        st.write(f"**{f.name}**")
        st.json(pd.read_json(f).to_dict(orient='records')[0] if f.exists() else {})
