import json

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

print('=== TWS-Warehouse ALL DEPOSITS ===')
for t in data:
    if t['account'] == 'TWS-Warehouse' and t['type'] == 'deposit':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:80])

print()
print('=== TK-Investments ALL DEPOSITS (non-transfer) ===')
for t in data:
    if t['account'] == 'TK-Investments' and t['type'] == 'deposit' and 'TRANSFER' not in t['description'].upper():
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:80])
