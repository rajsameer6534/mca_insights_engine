import re
import pandas as pd
import sqlite3
from typing import Dict, Any, List
from .config import DB_PATH

def _connect():
    return sqlite3.connect(DB_PATH)

def query_new_incorporations(state: str = None, days: int = 30) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM change_log WHERE Change_Type='New Incorporation' "
            "AND Date >= date('now','-? day')".replace('?','%d' % days), conn
        )
    if state:
        with _connect() as conn:
            companies = pd.read_sql_query("SELECT CIN, State FROM companies", conn)
        df = df.merge(companies, on='CIN', how='left')
        df = df[df['State'].str.lower() == state.lower()]
    return df

def query_struck_off(days: int = 30) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM change_log WHERE (Change_Type='Deregistered' OR (Change_Type='Field Update' AND Field_Changed='Company_Status' AND New_Value LIKE '%Strike Off%')) "
            "AND Date >= date('now','-? day')".replace('?','%d' % days), conn
        )
    return df

def query_capital_threshold(sector: str = None, min_auth_cap: float = 0.0) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("SELECT * FROM companies", conn)
    if min_auth_cap:
        df = df[df['Authorized_Capital'] >= float(min_auth_cap)]
    if sector:
        # naive: infer by NIC prefix match from sector keywords in name or NIC (demo-ready)
        df = df[df['NIC_Code'].astype(str).str.startswith(tuple([str(i) for i in range(10,20)]))] if 'manufactur' in sector.lower() else df
    return df

def interpret_and_execute(question: str) -> Dict[str, Any]:
    q = question.strip().lower()

    # 1) new incorporations in {state}
    m = re.search(r"new incorporations(?: in ([a-z\s]+))?", q)
    if m:
        st = m.group(1).strip() if m.group(1) else None
        return {"intent": "new_incorporations", "dataframe": query_new_incorporations(state=st)}

    # 2) manufacturing sector with authorized capital above Rs.X
    m = re.search(r"(manufacturing|sector)[^\d]*(?:authorized|auth)[^\d]*(?:capital|cap)[^\d]*([\d]+)", q)
    if m:
        cap = float(m.group(2))
        df = query_capital_threshold(sector='manufacturing', min_auth_cap=cap)
        return {"intent": "capital_threshold", "dataframe": df}

    # 3) struck off last month
    if 'struck off' in q or 'deregistered' in q:
        return {"intent": "struck_off", "dataframe": query_struck_off(days=30)}

    # 4) search company by CIN or name
    m = re.search(r"(?:show|find|search).*([ul][0-9a-z]{2}[0-9]{5}[a-z]{2}[0-9]{6})", q)  # very rough CIN regex
    if m:
        cin = m.group(1).upper()
        with _connect() as conn:
            companies = pd.read_sql_query("SELECT * FROM companies WHERE CIN = ?", conn, params=(cin,))
            changes = pd.read_sql_query("SELECT * FROM change_log WHERE CIN = ? ORDER BY Date", conn, params=(cin,))
        return {"intent": "company_lookup", "company": companies, "changes": changes}

    # Fallback: keyword search by name
    m = re.search(r"(?:company|named|called)\s+([a-z0-9\s\.&-]+)", q)
    if m:
        name = m.group(1).strip()
        with _connect() as conn:
            matches = pd.read_sql_query("SELECT * FROM companies WHERE lower(Company_Name) LIKE ?", conn, params=(f"%{name.lower()}%",))
        return {"intent": "name_search", "dataframe": matches}

    return {"intent": "unknown", "message": "Sorry, I couldn't understand. Try: 'Show new incorporations in Maharashtra' or 'How many companies were struck off last month?'"}
