import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Search bank data for TFS
print('=== TFS mentions in bank data ===')
for t in data:
    desc = t['description'].upper()
    if 'TFS' in desc or 'FREIGHT SERVICE' in desc:
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + t['type'].ljust(10) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:70])

# Check if DTFS is related to TFS
print()
print('=== DTFS mentions (possible TFS payroll/expense) ===')
for t in data:
    desc = t['description'].upper()
    if 'DTFS' in desc:
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + t['type'].ljust(10) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:70])

# Search for TTIM/TTIO/TTIA in bank data
print()
print('=== TTIM/TTIO/TTIA in bank data ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['TTIM', 'TTIO', 'TTIA']):
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + t['type'].ljust(10) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:70])

# Check if any revenue deposits mention warehouse locations
print()
print('=== Revenue deposits with warehouse/location keywords ===')
for t in data:
    if t['type'] == 'deposit' and t['bucket'] == 'Revenue':
        desc = t['description'].upper()
        if any(k in desc for k in ['WAREHOUSE', 'TTIM', 'TTIO', 'TTIA', 'LOCATION']):
            print(t['date'] + ' | ' + t['account'].ljust(15) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])
