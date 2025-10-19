from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHANGELOGS_DIR = OUTPUTS_DIR / "changelogs"
ENRICH_DIR = OUTPUTS_DIR / "enrichment"
SUMMARIES_DIR = OUTPUTS_DIR / "summaries"
DB_PATH = OUTPUTS_DIR / "master.db"
MASTER_CSV = OUTPUTS_DIR / "master_latest.csv"

# States/ROCs selected
SELECTED_STATES = ["Maharashtra", "Gujarat", "Delhi", "Tamil Nadu", "Karnataka"]

# Canonical schema
CANONICAL_COLUMNS = [
    "CIN",
    "Company_Name",
    "Company_Class",
    "Date_of_Incorporation",
    "Authorized_Capital",
    "Paidup_Capital",
    "Company_Status",
    "NIC_Code",
    "Registered_Address",
    "RoC",
    "State",
]

# NIC to Sector (minimal demo map; expand as needed)
NIC_SECTOR_MAP = {
    "10": "Manufacturing",
    "11": "Manufacturing",
    "46": "Wholesale Trade",
    "47": "Retail Trade",
    "62": "IT Services",
    "63": "Information Services",
    "64": "Financial Services",
    "70": "Management/Consulting",
    "71": "R&D/Engineering",
    "72": "R&D/Science",
    "86": "Healthcare",
    "96": "Personal Services",
}

# Enrichment options
ENABLE_WEB_ENRICHMENT = str(os.getenv("ENABLE_WEB_ENRICHMENT", "false")).lower() == "true"
