import json

with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

print('=== ALL files with 0 transactions in raw extraction ===')
for fi in raw['files']:
    txn_count = sum(len(p['transactions']) for p in fi['page_extractions'])
    if txn_count == 0:
        print('  ' + fi['filename'] + ' | ' + str(fi['pages']) + 'p | ' + str(txn_count) + 'txns')
