import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

grid = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in data:
    grid[t['account']][str(t['year'])][int(t['month'])] += 1

print('=== BMO-TTIPark 2025 ===')
for m in range(1, 13):
    print(f'  {m:02d}: {grid["BMO-TTIPark"]["2025"].get(m, 0)}')

print()
print('=== BMO-TTIPark 2026 ===')
for m in range(1, 13):
    print(f'  {m:02d}: {grid["BMO-TTIPark"]["2026"].get(m, 0)}')

print()
print('=== TK-Investments 2025 ===')
for m in range(1, 13):
    print(f'  {m:02d}: {grid["TK-Investments"]["2025"].get(m, 0)}')

print()
print('=== TK-Investments 2026 ===')
for m in range(1, 13):
    print(f'  {m:02d}: {grid["TK-Investments"]["2026"].get(m, 0)}')

print()
print('=== CNB-TTICorp2 2024 ===')
for m in range(1, 13):
    print(f'  {m:02d}: {grid["CNB-TTICorp2"]["2024"].get(m, 0)}')
