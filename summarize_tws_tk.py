import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Summarize TWS and TK by year and bucket
print('=== TWS-Warehouse ANNUAL SUMMARY ===')
tws = defaultdict(lambda: defaultdict(float))
for t in data:
    if t['account'] == 'TWS-Warehouse':
        tws[t['year']][t['bucket']] += t['amount'] if t['type'] == 'deposit' else -t['amount']

for year in sorted(tws.keys()):
    print(f'Year {year}:')
    for bucket, amt in sorted(tws[year].items()):
        print(f'  {bucket:20}: ${amt:>12,.2f}')
    net = sum(tws[year].values())
    print(f'  NET FLOW: ${net:>12,.2f}')

print()
print('=== TK-Investments ANNUAL SUMMARY ===')
tk = defaultdict(lambda: defaultdict(float))
for t in data:
    if t['account'] == 'TK-Investments':
        tk[t['year']][t['bucket']] += t['amount'] if t['type'] == 'deposit' else -t['amount']

for year in sorted(tk.keys()):
    print(f'Year {year}:')
    for bucket, amt in sorted(tk[year].items()):
        print(f'  {bucket:20}: ${amt:>12,.2f}')
    net = sum(tk[year].values())
    print(f'  NET FLOW: ${net:>12,.2f}')

print()
print('=== BMO-TTICorp TRANSFER WITHDRAWALS (intercompany funding?) ===')
transfers = defaultdict(float)
for t in data:
    if t['account'] == 'BMO-TTICorp' and t['type'] == 'withdrawal' and 'TRANSFER' in t['description'].upper():
        transfers[t['year']] += t['amount']
for year, amt in sorted(transfers.items()):
    print(f'  {year}: ${amt:>12,.2f}')

print()
print('=== BMO-TTIPark TRANSFER WITHDRAWALS ===')
transfers = defaultdict(float)
for t in data:
    if t['account'] == 'BMO-TTIPark' and t['type'] == 'withdrawal' and 'TRANSFER' in t['description'].upper():
        transfers[t['year']] += t['amount']
for year, amt in sorted(transfers.items()):
    print(f'  {year}: ${amt:>12,.2f}')
