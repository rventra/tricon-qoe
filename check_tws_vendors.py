import json

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

print('=== TWS-Warehouse VENDOR PAYMENTS (check details) ===')
for t in data:
    if t['account'] == 'TWS-Warehouse' and t['type'] == 'withdrawal' and t['bucket'] == 'Vendor Payment':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:80])

print()
print('=== TWS-Warehouse OPEX (non-payroll, non-vendor) ===')
for t in data:
    if t['account'] == 'TWS-Warehouse' and t['type'] == 'withdrawal' and t['bucket'] == 'OPEX-Non Payroll':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:80])
