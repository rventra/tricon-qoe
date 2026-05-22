import json
from collections import defaultdict

with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

# Determine account for each file
def get_account(fname):
    upper = fname.upper()
    if 'BMO TTI' in upper or 'BMO_TTI' in upper:
        return 'BMO-TTICorp (0677032724)'
    elif 'TTI PARK' in upper or 'TTI_PARK' in upper:
        return 'BMO-TTIPark (0069956696)'
    elif 'CNB' in upper:
        return 'CNB-TTICorp2 (248017740)'
    elif '9530' in upper:
        return 'TWS-Warehouse (959089530)'
    elif 'TK' in upper:
        return 'TK-Investments (037441394)'
    return None

# Build coverage from actual transaction dates in raw extraction
coverage = defaultdict(lambda: defaultdict(set))  # account -> year -> set of months

for file_info in raw['files']:
    fname = file_info['filename']
    account = get_account(fname)
    if not account:
        continue
    
    for page in file_info['page_extractions']:
        for txn in page['transactions']:
            date_str = txn.get('date', '')
            if not date_str or date_str == 'N/A':
                continue
            # Parse MM-DD-YY or MM/DD/YY
            parts = date_str.replace('/', '-').split('-')
            if len(parts) >= 3:
                try:
                    month = int(parts[0])
                    year = int(parts[2])
                    if year < 50:
                        year += 2000
                    elif year < 100:
                        year += 1900
                    if 2020 <= year <= 2030 and 1 <= month <= 12:
                        coverage[account][year].add(month)
                except ValueError:
                    pass

# Also check flat JSON for additional date coverage (deduped but more reliable dates)
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

account_map = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

for t in flat:
    acct = account_map.get(t['account'])
    if acct:
        year = int(t['year'])
        month = int(t['month'])
        coverage[acct][year].add(month)

years = [2022, 2023, 2024, 2025, 2026]
accounts = sorted(coverage.keys())

def format_missing(present_months):
    all_months = set(range(1, 13))
    missing = sorted(all_months - present_months)
    if not missing:
        return 'Complete'
    mon_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    
    # Group contiguous
    ranges = []
    start = missing[0]
    end = missing[0]
    for m in missing[1:]:
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

print('Bank Statement Coverage by Account')
print('(Cells show MISSING months; "Complete" = all 12 months available)')
print('=' * 115)
print()

header = f'{"Bank Account":<40} | {"2022":<16} | {"2023":<16} | {"2024":<16} | {"2025":<16} | {"2026":<16}'
print(header)
print('-' * len(header))

for acct in accounts:
    row = f'{acct:<40}'
    for year in years:
        present = coverage[acct].get(year, set())
        missing = format_missing(present)
        row += f' | {missing:<16}'
    print(row)
