import json
from collections import defaultdict

with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

# Build two sets: files present and files with 0 transactions
files_present = defaultdict(lambda: defaultdict(set))
files_empty = defaultdict(lambda: defaultdict(set))

for file_info in raw['files']:
    fname = file_info['filename'].upper()
    txn_count = sum(len(p['transactions']) for p in file_info['page_extractions'])
    
    # Determine account
    if 'BMO TTI' in fname:
        acct = 'BMO-TTICorp'
    elif 'TTI PARK' in fname:
        acct = 'BMO-TTIPark'
    elif 'CNB' in fname:
        acct = 'CNB-TTICorp2'
    elif '9530' in fname:
        acct = 'TWS-Warehouse'
    elif ' TK' in fname or fname.startswith('2025 TK') or fname.startswith('2026 TK'):
        acct = 'TK-Investments'
    else:
        continue
    
    # Extract year and month
    import re
    year = None
    month = None
    
    m1 = re.search(r'^(\d{4})(\d{2})\d{2}', fname)
    if m1:
        year = int(m1.group(1))
        month = int(m1.group(2))
    else:
        m2 = re.search(r'(\d{4})\s+([A-Z]{3})', fname)
        if m2:
            year = int(m2.group(1))
            mon_str = m2.group(2)
            mon_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            month = mon_map.get(mon_str)
    
    if year and month:
        files_present[acct][year].add(month)
        if txn_count == 0:
            files_empty[acct][year].add(month)

# Now check which months are truly missing (no file) vs. empty (file with 0 txns)
print('=== MISSING vs EMPTY by Account ===')
for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    print()
    print(acct + ':')
    for year in [2023, 2024, 2025, 2026]:
        present = files_present[acct].get(year, set())
        empty = files_empty[acct].get(year, set())
        missing = set(range(1,13)) - present
        
        if missing or empty:
            print(f'  {year}:')
            if missing:
                print(f'    Missing (no file): {sorted(missing)}')
            if empty:
                print(f'    Empty (file exists, 0 txns): {sorted(empty)}')
