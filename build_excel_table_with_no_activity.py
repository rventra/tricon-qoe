import json
import re
from collections import defaultdict

# Load raw extraction to find "no activity" files
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

# Find all months with a file but 0 transactions (NO ACTIVITY CONFIRMED)
no_activity_cells = set()
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
        no_activity_cells.add((acct, year, month))

# Load flat JSON for transaction counts
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

grid = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in flat:
    grid[t['account']][int(t['year'])][int(t['month'])] += 1

accounts = ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']
account_names = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

months = []
for y in [2023, 2024, 2025, 2026]:
    for m in range(1, 13):
        months.append((y, m))

# Build output
delimiter = '\t'
header = ['Account'] + [f'{y} {m:02d}' for y, m in months] + ['Total']

lines = [delimiter.join(header)]

for acct in accounts:
    row = [account_names[acct]]
    total = 0
    for y, m in months:
        if (acct, y, m) in no_activity_cells:
            cell = 'NO ACTIVITY CONFIRMED'
            total += 0
        else:
            cnt = grid[acct][y].get(m, 0)
            cell = str(cnt)
            total += cnt
        row.append(cell)
    row.append(str(total))
    lines.append(delimiter.join(row))

# Total row
total_row = ['Total']
grand_total = 0
for y, m in months:
    col_total = 0
    for acct in accounts:
        if (acct, y, m) in no_activity_cells:
            pass  # 0
        else:
            col_total += grid[acct][y].get(m, 0)
    total_row.append(str(col_total))
    grand_total += col_total
total_row.append(str(grand_total))
lines.append(delimiter.join(total_row))

# Write to file
with open('transaction_count_table.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')

# Also print
print('\n'.join(lines))
