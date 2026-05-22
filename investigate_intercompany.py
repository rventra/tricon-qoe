import json

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Summarize transfers by account and direction
print('=== TRANSFERS SUMMARY BY ACCOUNT ===')
from collections import defaultdict
summary = defaultdict(lambda: {'deposit': 0.0, 'withdrawal': 0.0, 'count_dep': 0, 'count_wd': 0})

for t in data:
    desc = t['description'].upper()
    if 'TRANSFER' in desc:
        d = summary[t['account']]
        d[t['type']] += t['amount']
        d['count_dep' if t['type'] == 'deposit' else 'count_wd'] += 1

for acct, vals in sorted(summary.items()):
    print(acct.ljust(15) + ' | Deposits: ' + str(vals['count_dep']).rjust(3) + ' / $' + str(round(vals['deposit'],2)).rjust(12) + 
          ' | Withdrawals: ' + str(vals['count_wd']).rjust(3) + ' / $' + str(round(vals['withdrawal'],2)).rjust(12))

print()
print('=== TWS DEPOSITS that are transfers (possible intercompany funding) ===')
for t in data:
    desc = t['description'].upper()
    if 'TRANSFER' in desc and t['type'] == 'deposit' and t['account'] == 'TWS-Warehouse':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'])

print()
print('=== TK DEPOSITS that are transfers ===')
for t in data:
    desc = t['description'].upper()
    if 'TRANSFER' in desc and t['type'] == 'deposit' and t['account'] == 'TK-Investments':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'])

print()
print('=== TK ALL WITHDRAWALS (sample) ===')
for t in data:
    if t['account'] == 'TK-Investments' and t['type'] == 'withdrawal':
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:80])

print()
print('=== TWS ALL WITHDRAWALS (sample, non-Barrett) ===')
for t in data:
    if t['account'] == 'TWS-Warehouse' and t['type'] == 'withdrawal' and 'BARRETT' not in t['description'].upper():
        print(t['date'] + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['bucket'].ljust(15) + ' | ' + t['description'][:80])
