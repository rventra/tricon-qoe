import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# BMO-TTICorp transfers that might go to TK
print('=== BMO-TTICorp transfers mentioning TK account or similar amounts ===')
for t in data:
    if t['account'] == 'BMO-TTICorp' and t['type'] == 'withdrawal':
        desc = t['description'].upper()
        if 'TRANSFER' in desc or 'WIRE' in desc:
            if '37441394' in desc or 'PC TRANSFER' in desc or (20000 <= t['amount'] <= 30000):
                print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])

print()
print('=== BMO-TTICorp wires of ~$169K or ~$110K (TWS funding?) ===')
for t in data:
    if t['account'] == 'BMO-TTICorp' and t['type'] == 'withdrawal':
        if t['amount'] in [110000, 169000, 60000, 65000, 68000, 70000, 72000, 75000]:
            print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])

# CNB-TTICorp2 wires
print()
print('=== CNB-TTICorp2 wires to TWS? ===')
for t in data:
    if t['account'] == 'CNB-TTICorp2' and t['type'] == 'withdrawal':
        desc = t['description'].upper()
        if 'WIRE' in desc or 'TRANSFER' in desc:
            print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])
