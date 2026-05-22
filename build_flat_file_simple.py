import json
import re
import os
import fitz
from collections import defaultdict
import calendar

# 1. Flat JSON counts (ground truth for transactions)
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

flat_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in flat:
    yr = int(t['year']) if isinstance(t['year'], (int, str)) else t['year']
    mo = int(t['month']) if isinstance(t['month'], (int, str)) else t['month']
    flat_counts[t['account']][yr][mo] += 1

# 2. Scan ONLY Empty Statements folders for "no activity" confirmations
base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

empty_folders = [
    (os.path.join(base_path, 'Account #9530', 'Empty Statements'), 'TWS-Warehouse'),
    (os.path.join(base_path, 'CNB', 'Empty Statements'), 'CNB-TTICorp2'),
]

def read_actual_date_from_pdf(path):
    """Read actual statement date from inside PDF"""
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        
        # Try CNB format: "This statement: Month DD, YYYY"
        stmt_match = re.search(r'This statement:\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
        if stmt_match:
            date_str = stmt_match.group(1).strip().replace(',', '')
            parts = date_str.split()
            mon_map = {'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,
                       'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12}
            month = mon_map.get(parts[0].upper())
            year = int(parts[-1])
            if month and 2020 <= year <= 2030:
                return year, month
        
        # Try TWS format: "Month DD, YYYY through Month DD, YYYY"
        range_match = re.search(r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})\s+through\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
        if range_match:
            date_str = range_match.group(2).strip().replace(',', '')
            parts = date_str.split()
            mon_map = {'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,
                       'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12}
            month = mon_map.get(parts[0].upper())
            year = int(parts[-1])
            if month and 2020 <= year <= 2030:
                return year, month
    except:
        pass
    return None, None

def parse_filename_date(fname):
    """Parse YYYYMMDD from filename like 20230531"""
    m = re.search(r'^(\d{4})(\d{2})\d{2}', fname)
    if m:
        return int(m.group(1)), int(m.group(2))
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
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith('.pdf'):
            continue
        path = os.path.join(folder, fname)
        
        if acct == 'CNB-TTICorp2':
            year, month = read_actual_date_from_pdf(path)
        else:
            year, month = parse_filename_date(fname)
        
        if year and month:
            no_activity_months[acct][year].add(month)
            print(f'  Empty statement: {fname} -> {year}-{month:02d}')

# Also check raw extraction for files with 0 transactions
with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

for file_info in raw['files']:
    fname = file_info['filename']
    upper = fname.upper()
    
    acct = None
    if '9530' in upper:
        acct = 'TWS-Warehouse'
    elif 'CNB' in upper:
        acct = 'CNB-TTICorp2'
    else:
        continue
    
    txn_count = sum(len(p['transactions']) for p in file_info['page_extractions'])
    if txn_count == 0:
        year, month = parse_filename_date(fname)
        if year and month:
            no_activity_months[acct][year].add(month)
            print(f'  Raw extraction 0 txn: {fname} -> {year}-{month:02d}')

# 3. Build flat file
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
            txn_count = flat_counts[acct][year].get(month, 0)
            is_no_activity = month in no_activity_months[acct].get(year, set())
            
            if txn_count > 0:
                status = 'Provided'
            elif is_no_activity:
                status = 'Provided'
            else:
                status = 'Missing'
            
            day = last_day(year, month)
            date_str = f'{year}-{month:02d}-{day:02d}'
            
            line = f'{account_names[acct]}\t{date_str}\t{year}\t{month:02d}\t{status}\t{txn_count}'
            lines.append(line)

# Write
output_path = 'bank_statement_status_flat.txt'
with open(output_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'\nWrote {len(lines)-1} rows to {output_path}')

# Verify totals
total_txns = sum(flat_counts[acct][year].get(month, 0) for acct in accounts for year in [2022,2023,2024,2025,2026] for month in range(1,13))
print(f'Total transactions in flat JSON: {total_txns}')

# Show Provided with 0 txns
print()
print('=== Provided with 0 transactions (No Activity Confirmed) ===')
count = 0
for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            txn_count = flat_counts[acct][year].get(month, 0)
            is_no_activity = month in no_activity_months[acct].get(year, set())
            if txn_count == 0 and is_no_activity:
                print(f'  {account_names[acct]} {year}-{month:02d}')
                count += 1
print(f'Total: {count} months')
