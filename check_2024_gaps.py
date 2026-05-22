import json
from collections import defaultdict

with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    data = json.load(f)

print("=== 2024 Bank Statement Coverage by Account ===\n")

for acct in ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']:
    print(f"{acct}")
    
    # Count deposits and withdrawals by month for 2024
    deposits = defaultdict(int)
    withdrawals = defaultdict(int)
    
    for t in data:
        if t['account'] == acct and str(t['year']) == '2024':
            month = int(t['month'])
            if t['type'] == 'deposit':
                deposits[month] += 1
            else:
                withdrawals[month] += 1
    
    dep_months = sorted(deposits.keys())
    wd_months = sorted(withdrawals.keys())
    
    # Build present strings
    if dep_months:
        dep_present = ', '.join(f"{m:02d}" for m in dep_months)
    else:
        dep_present = "NONE"
    
    if wd_months:
        wd_present = ', '.join(f"{m:02d}" for m in wd_months)
    else:
        wd_present = "NONE"
    
    # Build missing strings
    dep_missing = [m for m in range(1, 13) if m not in dep_months]
    wd_missing = [m for m in range(1, 13) if m not in wd_months]
    
    if dep_missing:
        dep_missing_str = ', '.join(f"{m:02d}" for m in dep_missing) + f" ({len(dep_missing)} months)"
    else:
        dep_missing_str = "NONE"
    
    if wd_missing:
        wd_missing_str = ', '.join(f"{m:02d}" for m in wd_missing) + f" ({len(wd_missing)} months)"
    else:
        wd_missing_str = "NONE"
    
    print(f"  Deposits:    Present={dep_present}  |  Missing={dep_missing_str}")
    print(f"  Withdrawals: Present={wd_present}  |  Missing={wd_missing_str}")
    
    # Count transactions
    dep_count = sum(deposits.values())
    wd_count = sum(withdrawals.values())
    print(f"  Total transactions: {dep_count} deposits, {wd_count} withdrawals")
    print()
