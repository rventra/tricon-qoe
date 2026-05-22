import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Search for TTIM/TTIO/TTIA/TFS in bank descriptions
print('=== Searching for TTIM/TTIO/TTIA/TFS in bank descriptions ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['TTIM', 'TTIO', 'TTIA', 'TFS']):
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + t['type'].ljust(10) + ' | $' + str(t['amount']).rjust(12) + ' | ' + t['description'][:80])

# Search for warehouse-related payments from BMO/CNB
print()
print('=== Warehouse-related payments from BMO-TTICorp or CNB ===')
for t in data:
    if t['account'] in ['BMO-TTICorp', 'CNB-TTICorp2'] and t['type'] == 'withdrawal':
        desc = t['description'].upper()
        if any(k in desc for k in ['WAREHOUSE', 'WHSE', 'RENT', 'LEASE', 'TWS']):
            print(t['date'] + ' | ' + t['account'].ljust(15) + ' | $' + str(t['amount']).rjust(12) + ' | ' + t['description'][:80])

# Search for round monthly amounts near ~130K (TTIM/TTIO monthly)
print()
print('=== BMO-TTICorp withdrawals between $100K-$200K (possible warehouse allocations) ===')
for t in data:
    if t['account'] == 'BMO-TTICorp' and t['type'] == 'withdrawal' and 100000 <= t['amount'] <= 200000:
        print(t['date'] + ' | $' + str(t['amount']).rjust(12) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:80])

# Sum DTFS payments
print()
print('=== DTFS payments summary ===')
dtfs_total = 0
dtfs_count = 0
for t in data:
    if 'DTFS' in t['description'].upper():
        dtfs_total += t['amount']
        dtfs_count += 1
        if t['year'] == 2024:
            print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:60])
print(f'Total DTFS payments: {dtfs_count} transactions, ${dtfs_total:,.2f}')

# Check TWS deposits from TTI
print()
print('=== TWS-Warehouse deposits that look like intercompany payments from TTI ===')
for t in data:
    if t['account'] == 'TWS-Warehouse' and t['type'] == 'deposit':
        desc = t['description'].upper()
        if 'FEDWIRE' in desc or 'CITY NATIONAL' in desc or 'TRICON TRANSPORTATION' in desc or 'TRANSFER' in desc:
            print(t['date'] + ' | $' + str(t['amount']).rjust(12) + ' | ' + t['description'][:80])
