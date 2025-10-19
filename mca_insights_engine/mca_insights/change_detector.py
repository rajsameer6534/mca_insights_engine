from pathlib import Path
import pandas as pd
from datetime import datetime
from .config import CANONICAL_COLUMNS
from .utils import normalize_cin

KEY_FIELDS = [c for c in CANONICAL_COLUMNS if c not in ('Registered_Address',)]  # track most fields

def detect_changes(prev_df: pd.DataFrame, curr_df: pd.DataFrame, date_str: str):
    # Normalize CIN keys
    prev = prev_df.copy()
    prev['CIN'] = prev['CIN'].apply(normalize_cin)
    curr = curr_df.copy()
    curr['CIN'] = curr['CIN'].apply(normalize_cin)

    prev_idx = prev.set_index('CIN')
    curr_idx = curr.set_index('CIN')

    prev_cins = set(prev_idx.index)
    curr_cins = set(curr_idx.index)

    new_cins = curr_cins - prev_cins
    removed_cins = prev_cins - curr_cins
    intersect = prev_cins & curr_cins

    changes = []

    # New incorporations
    for cin in sorted(new_cins):
        changes.append({
            'CIN': cin,
            'Change_Type': 'New Incorporation',
            'Field_Changed': '',
            'Old_Value': '',
            'New_Value': '',
            'Date': date_str
        })

    # Deregistered (missing today)
    for cin in sorted(removed_cins):
        changes.append({
            'CIN': cin,
            'Change_Type': 'Deregistered',
            'Field_Changed': '',
            'Old_Value': '',
            'New_Value': '',
            'Date': date_str
        })

    # Field updates
    for cin in sorted(intersect):
        prev_row = prev_idx.loc[cin]
        curr_row = curr_idx.loc[cin]
        for field in KEY_FIELDS:
            pv = str(prev_row.get(field))
            cv = str(curr_row.get(field))
            if pv != cv:
                changes.append({
                    'CIN': cin,
                    'Change_Type': 'Field Update',
                    'Field_Changed': field,
                    'Old_Value': pv,
                    'New_Value': cv,
                    'Date': date_str
                })

    change_df = pd.DataFrame(changes, columns=['CIN','Change_Type','Field_Changed','Old_Value','New_Value','Date'])
    return change_df
