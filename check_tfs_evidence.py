import json

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

# Search for TFS in bank data
print('=== TFS mentions in bank data ===')
for t in data:
    desc = t['description'].upper()
    if 'TFS' in desc or 'FREIGHT SERVICE' in desc or 'FREIGHT SERV' in desc:
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | ' + t['type'].ljust(10) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])

# Check if TFS has its own bank account
print()
print('=== Unique bank accounts in flat data ===')
accounts = set(t['account'] for t in data)
for a in sorted(accounts):
    print('  ' + a)

# Search for EIN or TFS in payroll
print()
print('=== Any payroll checks mentioning TFS or EIN 88-3562627 ===')
for t in data:
    desc = t['description'].upper()
    if t['bucket'] == 'Payroll' and ('TFS' in desc or '3562627' in desc or 'FREIGHT' in desc):
        print(t['date'] + ' | ' + t['account'].ljust(15) + ' | $' + str(t['amount']).rjust(10) + ' | ' + t['description'][:70])
