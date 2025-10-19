from pathlib import Path
import json
import pandas as pd
from .config import SUMMARIES_DIR

def generate_daily_summary(change_log_csv: Path, out_date: str):
    df = pd.read_csv(change_log_csv)
    total_new = (df['Change_Type'] == 'New Incorporation').sum()
    total_dereg = (df['Change_Type'] == 'Deregistered').sum()
    total_updates = (df['Change_Type'] == 'Field Update').sum()

    note_status = df[df['Field_Changed'] == 'Company_Status']
    notable_status = note_status['CIN'].unique().tolist()

    summary = {
        "date": out_date,
        "new_incorporations": int(total_new),
        "deregistered": int(total_dereg),
        "updated_records": int(total_updates),
        "notable_status_changes_CINs": notable_status[:20],
    }

    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    json_path = SUMMARIES_DIR / f"daily_summary_{out_date}.json"
    txt_path = SUMMARIES_DIR / f"daily_summary_{out_date}.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Daily Summary ({out_date})\n\n")
        f.write(f"New incorporations: {total_new}\n")
        f.write(f"Deregistered: {total_dereg}\n")
        f.write(f"Updated records: {total_updates}\n")
        if notable_status:
            f.write(f"Notable CINs with status changes: {', '.join(notable_status[:20])}\n")

    return json_path, txt_path
