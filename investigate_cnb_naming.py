import fitz
import re
import os

base = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements\CNB\Transaction Level Statements'
empty_base = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements\CNB\Empty Statements'

print('=== CNB Transaction Level Statements - Actual Periods ===')
files = sorted([f for f in os.listdir(base) if f.endswith('.pdf')])

for fname in files:
    path = os.path.join(base, fname)
    doc = fitz.open(path)
    text = doc[0].get_text()
    
    stmt_date = re.search(r'This statement:\s*([^\n]+)', text)
    last_stmt = re.search(r'Last statement:\s*([^\n]+)', text)
    
    print(f'{fname}')
    if stmt_date:
        print(f'  Statement date: {stmt_date.group(1).strip()}')
    if last_stmt:
        print(f'  Last statement: {last_stmt.group(1).strip()}')
    print()

print('=== CNB Empty Statements - Actual Periods ===')
if os.path.exists(empty_base):
    files = sorted([f for f in os.listdir(empty_base) if f.endswith('.pdf')])
    for fname in files:
        path = os.path.join(empty_base, fname)
        doc = fitz.open(path)
        text = doc[0].get_text()
        
        stmt_date = re.search(r'This statement:\s*([^\n]+)', text)
        last_stmt = re.search(r'Last statement:\s*([^\n]+)', text)
        
        print(f'{fname}')
        if stmt_date:
            print(f'  Statement date: {stmt_date.group(1).strip()}')
        if last_stmt:
            print(f'  Last statement: {last_stmt.group(1).strip()}')
        print()
