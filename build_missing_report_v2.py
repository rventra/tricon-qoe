import json
import re
import os
from collections import defaultdict
from datetime import date
import calendar

# 1. Load flat JSON - months with transactions
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

flat_months = defaultdict(lambda: defaultdict(set))
flat_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in flat:
    flat_months[t['account']][int(t['year'])].add(int(t['month']))
    flat_counts[t['account']][int(t['year'])][int(t['month'])] += 1

# 2. Scan Empty Statements folders
base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

empty_folders = [
    (os.path.join(base_path, 'Account #9530', 'Empty Statements'), 'TWS-Warehouse'),
    (os.path.join(base_path, 'BMO', 'Empty Statements'), 'BMO-TTICorp'),
    (os.path.join(base_path, 'CNB', 'Empty Statements'), 'CNB-TTICorp2'),
    (os.path.join(base_path, 'TK', 'Empty Statements'), 'TK-Investments'),
    (os.path.join(base_path, 'TWS Bank Statements', 'Empty Statements'), 'TWS-Warehouse'),
]

def get_year_month_from_filename(fname):
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

no_activity_months = defaultdict(lambda: defaultdict(set))

for folder, acct in empty_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            if fname.endswith('.pdf'):
                year, month = get_year_month_from_filename(fname)
                if year and month:
                    no_activity_months[acct][year].add(month)

# Also check raw extraction for files with 0 transactions
with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

for file_info in raw['files']:
    fname = file_info['filename']
    upper = fname.upper()
    
    acct = None
    if 'BMO TTI' in upper:
        acct = 'BMO-TTICorp'
    elif 'TTI PARK' in upper or 'TTI_PARK' in upper:
        acct = 'BMO-TTIPark'
    elif 'CNB' in upper:
        acct = 'CNB-TTICorp2'
    elif '9530' in upper:
        acct = 'TWS-Warehouse'
    elif ' TK' in upper or upper.startswith('2025 TK') or upper.startswith('2026 TK'):
        acct = 'TK-Investments'
    
    if not acct:
        continue
    
    year, month = get_year_month_from_filename(fname)
    if not year or not month:
        continue
    
    txn_count = sum(len(p['transactions']) for p in file_info['page_extractions'])
    if txn_count == 0:
        no_activity_months[acct][year].add(month)

print('DEBUG: no_activity_months contents:')
for acct in no_activity_months:
    for year in no_activity_months[acct]:
        print(f'  {acct} {year}: {sorted(no_activity_months[acct][year])}')
print()

# 3. Build flat report
accounts = ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']
account_names = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

def last_day(year, month):
    return calendar.monthrange(year, month)[1]

lines = []
header = 'Account\tDate\tYear\tMonth\tStatus\tTxnCount'
lines.append(header)

for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            has_flat = month in flat_months[acct].get(year, set())
            has_empty = month in no_activity_months[acct].get(year, set())
            
            if has_flat:
                status = 'Present'
                txn_count = flat_counts[acct][year].get(month, 0)
            elif has_empty:
                status = 'No Activity'
                txn_count = 0
            else:
                status = 'Missing'
                txn_count = 0
            
            day = last_day(year, month)
            date_str = f'{year}-{month:02d}-{day:02d}'
            
            line = f'{account_names[acct]}\t{date_str}\t{year}\t{month:02d}\t{status}\t{txn_count}'
            lines.append(line)

# Write to file
output_path = 'bank_statement_status_flat.txt'
with open(output_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Wrote {len(lines)-1} rows to {output_path}')
print()

# Verify total
total_txns = sum(flat_counts[acct][year].get(month, 0) for acct in accounts for year in [2022,2023,2024,2025,2026] for month in range(1,13))
print(f'Total transactions in flat JSON: {total_txns}')
