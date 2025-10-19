import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from .config import DB_PATH, CANONICAL_COLUMNS

SCHEMA_COMPANIES = f"""
CREATE TABLE IF NOT EXISTS companies (
    CIN TEXT PRIMARY KEY,
    Company_Name TEXT,
    Company_Class TEXT,
    Date_of_Incorporation TEXT,
    Authorized_Capital REAL,
    Paidup_Capital REAL,
    Company_Status TEXT,
    NIC_Code TEXT,
    Registered_Address TEXT,
    RoC TEXT,
    State TEXT
);
"""

SCHEMA_CHANGELOG = """
CREATE TABLE IF NOT EXISTS change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    CIN TEXT,
    Change_Type TEXT,
    Field_Changed TEXT,
    Old_Value TEXT,
    New_Value TEXT,
    Date TEXT
);
"""

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(SCHEMA_COMPANIES)
        c.execute(SCHEMA_CHANGELOG)
        conn.commit()

def upsert_companies(rows: List[Dict[str, Any]]):
    with get_conn() as conn:
        c = conn.cursor()
        cols = CANONICAL_COLUMNS
        placeholders = ','.join(['?'] * len(cols))
        sql = f"REPLACE INTO companies ({','.join(cols)}) VALUES ({placeholders})"
        data = [tuple(r.get(k) for k in cols) for r in rows]
        c.executemany(sql, data)
        conn.commit()

def log_changes(rows: List[Dict[str, Any]]):
    if not rows:
        return
    with get_conn() as conn:
        c = conn.cursor()
        sql = """INSERT INTO change_log (CIN, Change_Type, Field_Changed, Old_Value, New_Value, Date)
                 VALUES (?,?,?,?,?,?)"""
        data = [(r['CIN'], r['Change_Type'], r.get('Field_Changed',''), str(r.get('Old_Value','')), str(r.get('New_Value','')), r['Date']) for r in rows]
        c.executemany(sql, data)
        conn.commit()

def export_master_csv(path: Path):
    import pandas as pd
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM companies", conn)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def read_changes_since(date_str: str):
    import pandas as pd
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM change_log WHERE Date >= ?", conn, params=(date_str,))
    return df
