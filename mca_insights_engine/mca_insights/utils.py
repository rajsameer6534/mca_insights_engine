import re
from datetime import datetime

def normalize_cin(cin: str) -> str:
    return re.sub(r"\s+", "", cin.upper()) if isinstance(cin, str) else cin

def to_float(x):
    try:
        if x is None or x == '':
            return 0.0
        # Remove commas and currency symbols
        x = str(x).replace(',', '').replace('₹', '').strip()
        return float(x)
    except Exception:
        return 0.0

def parse_date(s: str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None
