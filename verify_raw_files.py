import json

with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

print('=== CNB 2024 Files ===')
for fi in raw['files']:
    if 'CNB' in fi['filename'].upper() and '2024' in fi['filename']:
        txn_count = sum(len(p['transactions']) for p in fi['page_extractions'])
        print('  ' + fi['filename'] + ' | ' + str(fi['pages']) + 'p | ' + str(txn_count) + 'txns')

print()
print('=== TWS 2024 Files ===')
for fi in raw['files']:
    if '9530' in fi['filename'] and '2024' in fi['filename']:
        txn_count = sum(len(p['transactions']) for p in fi['page_extractions'])
        print('  ' + fi['filename'] + ' | ' + str(fi['pages']) + 'p | ' + str(txn_count) + 'txns')
