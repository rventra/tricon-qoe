import json
import re
from collections import defaultdict

with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

# Determine account
def get_account(fname):
    upper = fname.upper()
    if 'BMO TTI' in upper:
        return 'BMO-TTICorp'
    elif 'TTI PARK' in upper or 'TTI_PARK' in upper:
        return 'BMO-TTIPark'
    elif 'CNB' in upper:
        return 'CNB-TTICorp2'
    elif '9530' in upper:
        return 'TWS-Warehouse'
    elif ' TK' in upper or upper.startswith('2025 TK') or upper.startswith('2026 TK'):
        return 'TK-Investments'
    return None

# Extract year and month from filename
def get_year_month(fname):
    m1 = re.search(r'^(\d{4})(\d{2})\d{2}', fname)
    if m1:
        return int(m1.group(1)), int(m1.group(2))
    
    m2 = re.search(r'(\d{4})\s+([A-Z]{3})', fname.upper())
    if m2:
        year = int(m2.group(1))
        mon_str = m2.group(2)
        mon_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
        month = mon_map.get(mon_str)
        if month:
            return year, month
    return None, None

files_present = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for file_info in raw['files']:
    fname = file_info['filename']
    acct = get_account(fname)
    if not acct:
        continue
    
    year, month = get_year_month(fname)
    if not year or not month:
        continue
    
    txn_count = sum(len(p['transactions']) for p in file_info['page_extractions'])
    files_present[acct][year][month] = txn_count

# Now check which months have files with 0 transactions
print('=== Months with files but 0 transactions (NO ACTIVITY) ===')
for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    for year in [2023, 2024, 2025, 2026]:
        no_activity = []
        for month in range(1, 13):
            if month in files_present[acct][year] and files_present[acct][year][month] == 0:
                no_activity.append(month)
        if no_activity:
            mon_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
            print(f'  {acct} {year}: {", ".join(mon_names[m] for m in no_activity)}')

print()
print('=== Full breakdown ===')
for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    print()
    print(acct + ':')
    for year in [2023, 2024, 2025, 2026]:
        present_with_txn = []
        no_activity = []
        missing = []
        for month in range(1, 13):
            if month in files_present[acct][year]:
                if files_present[acct][year][month] == 0:
                    no_activity.append(month)
                else:
                    present_with_txn.append(month)
            else:
                missing.append(month)
        
        mon_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        parts = []
        if present_with_txn:
            parts.append(f'Complete: {len(present_with_txn)} months')
        if no_activity:
            parts.append(f'No Activity: {", ".join(mon_names[m] for m in no_activity)}')
        if missing:
            parts.append(f'Missing: {", ".join(mon_names[m] for m in missing)}')
        if parts:
            print(f'  {year}: {" | ".join(parts)}')
