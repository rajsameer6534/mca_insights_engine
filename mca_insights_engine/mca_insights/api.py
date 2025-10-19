from flask import Flask, request, jsonify
import sqlite3
from .config import DB_PATH

app = Flask(__name__)

def _connect():
    return sqlite3.connect(DB_PATH)

@app.get('/search_company')
def search_company():
    cin = request.args.get('cin')
    name = request.args.get('name')

    with _connect() as conn:
        if cin:
            c = conn.execute("SELECT * FROM companies WHERE CIN = ?", (cin.upper(),))
            rows = [dict(zip([d[0] for d in c.description], r)) for r in c.fetchall()]
        elif name:
            c = conn.execute("SELECT * FROM companies WHERE lower(Company_Name) LIKE ?", (f"%{name.lower()}%",))
            rows = [dict(zip([d[0] for d in c.description], r)) for r in c.fetchall()]
        else:
            rows = []

        if rows:
            cin_val = rows[0]['CIN']
            cl = conn.execute("SELECT CIN, Change_Type, Field_Changed, Old_Value, New_Value, Date FROM change_log WHERE CIN = ? ORDER BY Date", (cin_val,))
            changes = [dict(zip([d[0] for d in cl.description], r)) for r in cl.fetchall()]
        else:
            changes = []

    return jsonify({"results": rows, "change_history": changes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
