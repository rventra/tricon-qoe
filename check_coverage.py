import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Build a grid of what we have by account and month
grid = defaultdict(lambda: defaultdict(int))
months = {}
for t in data:
    ym = f"{t['year']}-{int(t['month']):02d}"
    grid[t['account']][ym] += 1
    months[ym] = True

all_months = sorted(months.keys())

print('=== Transaction Count by Account and Month ===')
header = 'Account           | ' + ' | '.join(m[:7] for m in all_months)
print(header)
print('-' * len(header))
for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    counts = [str(grid[acct].get(m, 0)).rjust(5) for m in all_months]
    print(acct.ljust(17) + ' | ' + ' | '.join(counts))

# Sum by month for key accounts
print()
print('=== Monthly Totals by Account ===')
for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    monthly = defaultdict(float)
    for t in data:
        if t['account'] == acct:
            ym = f"{t['year']}-{int(t['month']):02d}"
            monthly[ym] += t['amount'] if t['type'] == 'deposit' else -t['amount']
    print()
    print(f'{acct}:')
    for ym in sorted(monthly.keys()):
        print(f'  {ym}: ${monthly[ym]:>12,.2f}')
