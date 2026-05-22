import json
import re
import os
from collections import defaultdict

base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

# Load raw extraction
with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

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

# Build status per cell: 'present', 'no_activity', or 'missing'
status = defaultdict(lambda: defaultdict(dict))

# 1. From raw extraction files
for file_info in raw['files']:
    fname = file_info['filename']
    acct = get_account(fname)
    if not acct:
        continue
    year, month = get_year_month(fname)
    if not year or not month:
        continue
    txn_count = sum(len(p['transactions']) for p in file_info['page_extractions'])
    if txn_count == 0:
        status[acct][year][month] = 'no_activity'
    else:
        status[acct][year][month] = 'present'

# 2. From Empty Statements folders (files not in raw extraction)
empty_folders = [
    (os.path.join(base_path, 'Account #9530', 'Empty Statements'), 'TWS-Warehouse'),
    (os.path.join(base_path, 'BMO', 'Empty Statements'), 'BMO-TTICorp'),
    (os.path.join(base_path, 'CNB', 'Empty Statements'), 'CNB-TTICorp2'),
    (os.path.join(base_path, 'TK', 'Empty Statements'), 'TK-Investments'),
    (os.path.join(base_path, 'TWS Bank Statements', 'Empty Statements'), 'TWS-Warehouse'),
]

for folder, acct in empty_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            if fname.endswith('.pdf'):
                year, month = get_year_month(fname)
                if year and month and month not in status[acct][year]:
                    status[acct][year][month] = 'no_activity'

accounts = ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']
account_names = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

mon_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

def format_months(months):
    if not months:
        return ''
    months = sorted(months)
    ranges = []
    start = months[0]
    end = months[0]
    for m in months[1:]:
        if m == end + 1:
            end = m
        else:
            ranges.append((start, end))
            start = m
            end = m
    ranges.append((start, end))
    parts = []
    for s, e in ranges:
        if s == e:
            parts.append(mon_names[s])
        else:
            parts.append(f'{mon_names[s]}-{mon_names[e]}')
    return ', '.join(parts)

# Build table
print('Bank Account\t2022\t2023\t2024\t2025\t2026')

for acct in accounts:
    row = [account_names[acct]]
    for year in [2022, 2023, 2024, 2025, 2026]:
        present = [m for m in range(1,13) if status[acct][year].get(m) == 'present']
        no_activity = [m for m in range(1,13) if status[acct][year].get(m) == 'no_activity']
        missing = [m for m in range(1,13) if m not in status[acct][year]]
        
        parts = []
        if missing:
            parts.append(format_months(missing))
        if no_activity:
            parts.append('(' + format_months(no_activity) + ' no activity)')
        
        if not parts:
            cell = 'Complete'
        else:
            cell = ', '.join(parts)
        
        row.append(cell)
    print('\t'.join(row))

# Also print summary of no_activity cells
print()
print('=== NO ACTIVITY months ===')
for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        no_activity = [m for m in range(1,13) if status[acct][year].get(m) == 'no_activity']
        if no_activity:
            print(f'  {account_names[acct]} {year}: {format_months(no_activity)}')
