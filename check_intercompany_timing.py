import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# TK deposits by week
print('=== TK-Investments PC TRANSFER CREDITS by week ===')
tk_deposits = [t for t in data if t['account'] == 'TK-Investments' and t['type'] == 'deposit' and 'TRANSFER' in t['description'].upper()]
for t in sorted(tk_deposits, key=lambda x: x['date']):
    print(t['date'] + ' | $' + str(t['amount']).rjust(10))

# TTI (BMO-TTICorp) transfer withdrawals by week  
print()
print('=== BMO-TTICorp TRANSFER WITHDRAWALS by week ===')
tti_transfers = [t for t in data if t['account'] == 'BMO-TTICorp' and t['type'] == 'withdrawal' and 'TRANSFER' in t['description'].upper()]
for t in sorted(tti_transfers, key=lambda x: x['date'])[:30]:
    print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:60])

print('...')
print(f'Total BMO-TTICorp transfer withdrawals: {len(tti_transfers)} transactions')

# Sum by month for 2025
print()
print('=== TK monthly transfer deposits 2025 ===')
tk_monthly = defaultdict(float)
for t in tk_deposits:
    if t['year'] == 2025:
        tk_monthly[t['month']] += t['amount']
for m in sorted(tk_monthly):
    print(f'  {m:02d}: ${tk_monthly[m]:>10,.2f}')
print(f'  TOTAL: ${sum(tk_monthly.values()):>10,.2f}')
