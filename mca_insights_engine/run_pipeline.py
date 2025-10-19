from pathlib import Path
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from mca_insights.config import SNAPSHOTS_DIR, OUTPUTS_DIR, CHANGELOGS_DIR, MASTER_CSV
from mca_insights.integrate import consolidate_snapshot_dir
from mca_insights.change_detector import detect_changes
from mca_insights.database import init_db, upsert_companies, log_changes, export_master_csv
from mca_insights.enrichers import enrich_sample
from mca_insights.ai_summary import generate_daily_summary

def run_for_dates(dates):
    load_dotenv()
    init_db()
    prev_df = None
    enriched_path = None
    last_change_csv = None

    for d in dates:
        snap_dir = SNAPSHOTS_DIR / d
        print(f"[+] Consolidating snapshot {d} ...")
        curr_df = consolidate_snapshot_dir(snap_dir)

        if prev_df is None:
            # First day: seed master without changes
            upsert_companies(curr_df.to_dict(orient='records'))
            export_master_csv(MASTER_CSV)
            prev_df = curr_df.copy()
            print(f"Seeded master with {len(curr_df)} companies for {d}.")
            continue

        print(f"[+] Detecting changes {dates[dates.index(d)-1]} -> {d} ...")
        ch = detect_changes(prev_df, curr_df, d)
        CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
        change_csv = CHANGELOGS_DIR / f"changes_{d}.csv"
        ch.to_csv(change_csv, index=False)
        last_change_csv = change_csv

        # Apply updates to DB (use latest data)
        upsert_companies(curr_df.to_dict(orient='records'))
        log_changes(ch.to_dict(orient='records'))
        export_master_csv(MASTER_CSV)
        prev_df = curr_df.copy()

    if last_change_csv is not None:
        # Enrich changed CINs (from the latest change file)
        latest_changes = pd.read_csv(last_change_csv)
        changed_cins = latest_changes['CIN'].unique().tolist()
        master_latest = pd.read_csv(MASTER_CSV)
        print(f"[+] Enriching {min(100, len(changed_cins))} changed CINs ...")
        enriched_path = enrich_sample(changed_cins, master_latest, limit=100)
        print(f"[+] Enriched output -> {enriched_path}")

        # AI daily summary
        print(f"[+] Generating daily summary for {dates[-1]} ...")
        generate_daily_summary(last_change_csv, dates[-1])

    print("[✓] Pipeline complete.")

if __name__ == "__main__":
    # Expect three dates (YYYY-MM-DD) present under data/snapshots/
    # Defaults to the demo dates we ship with the project.
    demo_dates = ["2025-10-17", "2025-10-18", "2025-10-19"]
    run_for_dates(demo_dates)
