import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Count by account, year, month
grid = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in data:
    grid[t['account']][str(t['year'])][int(t['month'])] += 1

accounts = ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']
account_names = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

# Build all month columns in order
months = []
for y in [2023, 2024, 2025, 2026]:
    for m in range(1, 13):
        months.append((y, m))

# Header
header_cols = ['Account'] + [f'{y} {m:02d}' for y, m in months] + ['Total']
delimiter = '\t'
print(delimiter.join(header_cols))

# Data rows
for acct in accounts:
    row = [account_names[acct]]
    total = 0
    for y, m in months:
        cnt = grid[acct][str(y)].get(m, 0)
        row.append(str(cnt))
        total += cnt
    row.append(str(total))
    print(delimiter.join(row))

# Total row
total_row = ['Total']
grand_total = 0
for y, m in months:
    col_total = sum(grid[acct][str(y)].get(m, 0) for acct in accounts)
    total_row.append(str(col_total))
    grand_total += col_total
total_row.append(str(grand_total))
print(delimiter.join(total_row))
