import os
import re
from collections import defaultdict

base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

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

empty_folders = [
    (os.path.join(base_path, 'Account #9530', 'Empty Statements'), 'TWS-Warehouse'),
    (os.path.join(base_path, 'BMO', 'Empty Statements'), 'BMO-TTICorp'),
    (os.path.join(base_path, 'CNB', 'Empty Statements'), 'CNB-TTICorp2'),
    (os.path.join(base_path, 'TK', 'Empty Statements'), 'TK-Investments'),
    (os.path.join(base_path, 'TWS Bank Statements', 'Empty Statements'), 'TWS-Warehouse'),
]

for folder, acct in empty_folders:
    print(f'Checking: {folder}')
    if os.path.exists(folder):
        files = [f for f in os.listdir(folder) if f.endswith('.pdf')]
        print(f'  Found {len(files)} PDF files')
        for fname in files:
            year, month = get_year_month_from_filename(fname)
            print(f'    {fname} -> year={year}, month={month}')
            if year and month:
                no_activity_months[acct][year].add(month)
    else:
        print('  FOLDER DOES NOT EXIST')

print()
print('=== no_activity_months ===')
for acct in no_activity_months:
    for year in no_activity_months[acct]:
        print(f'  {acct} {year}: {sorted(no_activity_months[acct][year])}')
