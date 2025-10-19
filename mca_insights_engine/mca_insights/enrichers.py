from pathlib import Path
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .config import ENRICH_DIR, ENABLE_WEB_ENRICHMENT

def _read_seed():
    seed_file = ENRICH_DIR / "enrichment_seed.csv"
    if seed_file.exists():
        return pd.read_csv(seed_file)
    return pd.DataFrame(columns=['CIN','COMPANY_NAME','STATE','STATUS','SOURCE','FIELD','SOURCE_URL'])

def _safe_request(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None

def enrich_sample(changed_cins, master_df, limit=100):
    """Enrich up to 'limit' changed CINs using seeded data or (optionally) live web lookups."""
    out_rows = []
    taken = 0
    seed = _read_seed()
    idx_master = master_df.set_index('CIN')

    for cin in changed_cins:
        if taken >= limit:
            break
        name = idx_master.loc[cin]['Company_Name'] if cin in idx_master.index else ''
        state = idx_master.loc[cin]['State'] if cin in idx_master.index else ''
        status = idx_master.loc[cin]['Company_Status'] if cin in idx_master.index else ''

        # Seed first
        seed_matches = seed[seed['CIN'] == cin]
        if not seed_matches.empty:
            for _, row in seed_matches.iterrows():
                out_rows.append(row.to_dict())
            taken += 1
            continue

        if not ENABLE_WEB_ENRICHMENT:
            # Fallback synthetic enrichment
            out_rows.append({
                'CIN': cin,
                'COMPANY_NAME': name,
                'STATE': state,
                'STATUS': status,
                'SOURCE': 'Seeded (demo)',
                'FIELD': 'Director_Names;Sector;Company_Type',
                'SOURCE_URL': 'N/A'
            })
            taken += 1
            continue

        # Optional: Live web enrichment (very lightweight demo stubs)
        # ZaubaCorp example (structure may change; best-effort demo)
        zurl = f"https://www.zaubacorp.com/companysearchresults/{cin}"
        html = _safe_request(zurl)
        directors = ''
        sector = ''
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                # Extremely naive parsing (for demo) — real world needs robust locators
                directors = ';'.join([a.get_text(strip=True) for a in soup.select('table tr td a')][:3])
                sector = (soup.find('title').get_text(strip=True) if soup.find('title') else '')[:60]
            except Exception:
                pass

        out_rows.append({
            'CIN': cin,
            'COMPANY_NAME': name,
            'STATE': state,
            'STATUS': status,
            'SOURCE': 'ZaubaCorp',
            'FIELD': f'Director_Names={directors};Sector={sector}',
            'SOURCE_URL': zurl
        })
        taken += 1

    out_df = pd.DataFrame(out_rows, columns=['CIN','COMPANY_NAME','STATE','STATUS','SOURCE','FIELD','SOURCE_URL'])
    out_path = ENRICH_DIR / "enriched_changes.csv"
    out_df.to_csv(out_path, index=False)
    return out_path
