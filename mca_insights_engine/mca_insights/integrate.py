from pathlib import Path
import pandas as pd
from .config import CANONICAL_COLUMNS, SELECTED_STATES
from .utils import normalize_cin, to_float

def load_and_normalize_state_csv(path: Path, state: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Map/ensure canonical columns exist (sample data already matches; but handle missing gracefully)
    colmap = {
        'CIN': 'CIN',
        'Company_Name': 'Company_Name',
        'Company_Class': 'Company_Class',
        'Date_of_Incorporation': 'Date_of_Incorporation',
        'Authorized_Capital': 'Authorized_Capital',
        'Paidup_Capital': 'Paidup_Capital',
        'Company_Status': 'Company_Status',
        'NIC_Code': 'NIC_Code',
        'Registered_Address': 'Registered_Address',
        'RoC': 'RoC',
        'State': 'State',
    }
    # Rename if needed
    df = df.rename(columns={k: v for k, v in colmap.items() if k in df.columns and k != v})
    # Ensure columns
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    # Clean
    df['CIN'] = df['CIN'].apply(normalize_cin)
    df['Authorized_Capital'] = df['Authorized_Capital'].apply(to_float)
    df['Paidup_Capital'] = df['Paidup_Capital'].apply(to_float)
    df['State'] = state
    # Drop duplicates by CIN (keep last)
    df = df.drop_duplicates(subset=['CIN'], keep='last')
    # Restrict to canonical columns
    df = df[CANONICAL_COLUMNS].copy()
    return df

def consolidate_snapshot_dir(snapshot_dir: Path) -> pd.DataFrame:
    pieces = []
    for state in SELECTED_STATES:
        # Expect filenames like state_name.csv in the directory
        fname = state.lower().replace(' ', '_') + '.csv'
        fpath = snapshot_dir / fname
        if not fpath.exists():
            continue
        df = load_and_normalize_state_csv(fpath, state)
        pieces.append(df)
    if not pieces:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    master = pd.concat(pieces, ignore_index=True)
    # Final dedupe
    master = master.drop_duplicates(subset=['CIN'], keep='last')
    return master
