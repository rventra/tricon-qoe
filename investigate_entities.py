import json

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Look for intercompany transfers
print('=== INTERCOMPANY TRANSFERS (all accounts) ===')
count = 0
for t in data:
    desc = t['description'].upper()
    if 'TRANSFER' in desc:
        count += 1
        if count <= 50:
            print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + str(t['amount']).rjust(10) + ' | ' + t['type'].ljust(10) + ' | ' + t['description'])
print('Total transfers:', count)

print()
print('=== WAREHOUSE / TWS PAYMENTS ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['WAREHOUSE', 'TWS', 'TRICON WAREHOUSE']) and t['type'] == 'withdrawal':
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + str(t['amount']).rjust(10) + ' | ' + t['description'])

print()
print('=== TK / T-K PAYMENTS ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['T-K', 'T K ']) and t['type'] == 'withdrawal':
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + str(t['amount']).rjust(10) + ' | ' + t['description'])

print()
print('=== TTIM / TTIO / TTIA payments from BMO-TTICorp or CNB ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['TTIM', 'TTIO', 'TTIA', 'TTIFU', 'TTIW']) and t['type'] == 'withdrawal':
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + str(t['amount']).rjust(10) + ' | ' + t['description'])

print()
print('=== "LABOR" or "DRIVER" payments (non-payroll) ===')
for t in data:
    desc = t['description'].upper()
    if any(k in desc for k in ['LABOR', 'DRIVER']) and t['type'] == 'withdrawal' and 'BARRETT' not in desc:
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'])
