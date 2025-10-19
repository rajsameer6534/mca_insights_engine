import random
from pathlib import Path
import pandas as pd
from datetime import date, timedelta
from mca_insights.config import SNAPSHOTS_DIR, SELECTED_STATES, CANONICAL_COLUMNS

random.seed(42)

ROCS = {
    "Maharashtra": "RoC-Mumbai",
    "Gujarat": "RoC-Ahmedabad",
    "Delhi": "RoC-Delhi",
    "Tamil Nadu": "RoC-Chennai",
    "Karnataka": "RoC-Bangalore"
}
CLASSES = ["Private", "Public", "Private (Ltd by shares)"]
STATUSES = ["Active", "Strike Off", "Amalgamated", "Dormant"]
NIC_CODES = ["10", "11", "46", "47", "62", "63", "64", "70", "71", "72", "86", "96"]

def make_cin(seq: int, state_idx: int) -> str:
    # Very rough fake CIN: U + 2 letters + 5 digits + 2 letters + 6 digits
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s1 = letters[state_idx % 26] + letters[(state_idx + 5) % 26]
    s2 = f"{seq:05d}"
    s3 = letters[(state_idx + 8) % 26] + letters[(state_idx + 13) % 26]
    s4 = f"{random.randint(100000, 999999)}"
    return f"U{s1}{s2}{s3}{s4}"

def generate_company(seq, state, state_idx):
    inc_year = random.randint(2005, 2025)
    inc_date = f"{inc_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    auth = random.choice([1e5, 2e5, 5e5, 1e6, 2e6, 5e6, 1e7])
    paid = auth * random.choice([0.5, 0.8, 1.0])
    status = random.choice(["Active"]*5 + ["Strike Off"] + ["Amalgamated"] + ["Dormant"])
    nic = random.choice(NIC_CODES)
    cin = make_cin(seq, state_idx)
    name = f"{state[:3].upper()}-{random.choice(['Tech','Agro','Foods','Retail','Fin','Info','Consult'])}-{seq} Pvt Ltd"
    address = f"{random.randint(1,200)}, {state}"
    return {
        "CIN": cin,
        "Company_Name": name,
        "Company_Class": random.choice(CLASSES),
        "Date_of_Incorporation": inc_date,
        "Authorized_Capital": float(auth),
        "Paidup_Capital": float(paid),
        "Company_Status": status,
        "NIC_Code": nic,
        "Registered_Address": address,
        "RoC": ROCS[state],
        "State": state,
    }

def write_snapshot(day: str, base_seq_start: int = 1, per_state: int = 120, del_ratio: float = 0.05):
    SNAPSHOTS_DIR.joinpath(day).mkdir(parents=True, exist_ok=True)
    for i, state in enumerate(SELECTED_STATES):
        rows = [generate_company(seq=base_seq_start + j, state=state, state_idx=i) for j in range(per_state)]
        df = pd.DataFrame(rows)
        df.to_csv(SNAPSHOTS_DIR / day / (state.lower().replace(' ', '_') + '.csv'), index=False)

def mutate_snapshot(prev_day: str, new_day: str, add_ratio: float = 0.15, upd_ratio: float = 0.15, del_ratio: float = 0.05):
    # Read previous snapshot, apply adds/updates/deletions, write new snapshot
    p = SNAPSHOTS_DIR / prev_day
    n = SNAPSHOTS_DIR / new_day
    n.mkdir(parents=True, exist_ok=True)

    for state in SELECTED_STATES:
        f = p / (state.lower().replace(' ', '_') + '.csv')
        df = pd.read_csv(f)

        # Delete some rows
        n_del = int(len(df)*del_ratio)
        n_del = max(1, n_del)
        to_del = set(random.sample(list(df['CIN']), k=n_del))
        df2 = df[~df['CIN'].isin(to_del)].copy()

        # Update some rows: status/capital
        n_upd = int(len(df2)*upd_ratio)
        n_upd = max(1, n_upd)
        to_upd = set(random.sample(list(df2['CIN']), k=n_upd))
        for idx in df2.index:
            if df2.loc[idx, 'CIN'] in to_upd:
                # Flip status or tweak capital
                if random.random() < 0.5:
                    df2.loc[idx, 'Company_Status'] = random.choice(["Active", "Strike Off", "Amalgamated", "Dormant"])
                else:
                    df2.loc[idx, 'Authorized_Capital'] = float(df2.loc[idx, 'Authorized_Capital'] * random.choice([0.8, 1.2, 1.5]))

        # Add some new companies
        try:
            base_seq = int(df['CIN'].str.extract(r'(\d{5})')[0].astype('Int64').dropna().max()) + 1
        except Exception:
            base_seq = 10000
        n_add = int(len(df)*add_ratio)
        n_add = max(1, n_add)
        adds = []
        for j in range(n_add):
            adds.append(generate_company(seq=base_seq + j, state=state, state_idx=list(SELECTED_STATES).index(state)))
        out = pd.concat([df2, pd.DataFrame(adds)], ignore_index=True)
        out.to_csv(n / (state.lower().replace(' ', '_') + '.csv'), index=False)

if __name__ == "__main__":
    # Demo: create 3 days of snapshots 2025-10-17, 2025-10-18, 2025-10-19
    write_snapshot("2025-10-17", base_seq_start=1, per_state=140)
    mutate_snapshot("2025-10-17", "2025-10-18", add_ratio=0.18, upd_ratio=0.20, del_ratio=0.06)
    mutate_snapshot("2025-10-18", "2025-10-19", add_ratio=0.18, upd_ratio=0.22, del_ratio=0.06)
    print("Demo snapshots created.")
