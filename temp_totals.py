import json, csv
from collections import defaultdict
from datetime import datetime

def parse_d(d):
    for fmt in ["%m/%d/%Y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(d.split(" ")[0], fmt)
        except:
            pass
    return None

def clean_amt(a):
    s = str(a).replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
    if not s or s == "-" or s == ".":
        return 0.0
    return float(s)

# Bank JSON
with open(r"C:\Users\New User\.claude\projects\Tricon QOE\data\flat\bank_transactions_flat.json", encoding="utf-8") as f:
    bank_all = json.load(f)

# TTI GL
with open(r"Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Data Request\1.3 General Ledger\flattened files\TTI_GEN_LEDGER_Flattened.csv", encoding="utf-8-sig") as f:
    tti_gl = list(csv.DictReader(f))

gl_accts = ['BMO Corporate Account - Other', 'CNB Corp.']

# Filter 2024
gl_2024 = []
for r in tti_gl:
    d = parse_d(r.get("Date", ""))
    if d and d.year == 2024 and r.get("Primary GL Account", "") in gl_accts:
        gl_2024.append(r)

bank_2024 = [t for t in bank_all if parse_d(t.get("date", "")) and parse_d(t.get("date", "")).year == 2024]

# By account totals
print("=" * 70)
print("2024 TTI - TOTAL CASH ACTIVITY")
print("=" * 70)

# GL side
print("\n--- GENERAL LEDGER (Cash Accounts) ---")
gl_total_dep = 0.0
gl_total_wd = 0.0
for acct in gl_accts:
    dep = sum(clean_amt(r["Amount"]) for r in gl_2024 if r["Primary GL Account"] == acct and clean_amt(r["Amount"]) > 0)
    wd = sum(abs(clean_amt(r["Amount"])) for r in gl_2024 if r["Primary GL Account"] == acct and clean_amt(r["Amount"]) < 0)
    net = dep - wd
    cnt = len([r for r in gl_2024 if r["Primary GL Account"] == acct])
    gl_total_dep += dep
    gl_total_wd += wd
    print(f"  {acct}:")
    print(f"    Deposits:      ${dep:>14,.0f}")
    print(f"    Withdrawals:   ${wd:>14,.0f}")
    print(f"    Net:           ${net:>14,.0f}")
    print(f"    Transactions:  {cnt:>14}")

print(f"\n  GL COMBINED:")
print(f"    Total Deposits:     ${gl_total_dep:>14,.0f}")
print(f"    Total Withdrawals:  ${gl_total_wd:>14,.0f}")
print(f"    Net Cash Flow:      ${gl_total_dep - gl_total_wd:>14,.0f}")
print(f"    Total Transactions: {len(gl_2024):>14}")

# Bank side
print("\n--- BANK STATEMENTS ---")
bank_acct_map = {
    'BMO-TTICorp': 'BMO/0677032724',
    'BMO-TTIPark': 'BMO/0069956696',
    'CNB-TTICorp2': 'CNB',
    'TWS-Warehouse': 'TWS',
    'TK-Investments': 'TK',
}
bank_total_dep = 0.0
bank_total_wd = 0.0
for acct in sorted(set(t.get("account","") for t in bank_2024)):
    dep = sum(abs(float(str(t.get("amount","0")).replace(",",""))) for t in bank_2024 if t.get("account") == acct and float(str(t.get("amount","0")).replace(",","")) > 0)
    wd = sum(abs(float(str(t.get("amount","0")).replace(",",""))) for t in bank_2024 if t.get("account") == acct and float(str(t.get("amount","0")).replace(",","")) < 0)
    net = dep - wd
    cnt = len([t for t in bank_2024 if t.get("account") == acct])
    bank_total_dep += dep
    bank_total_wd += wd
    print(f"  {acct}:")
    print(f"    Deposits:      ${dep:>14,.0f}")
    print(f"    Withdrawals:   ${wd:>14,.0f}")
    print(f"    Net:           ${net:>14,.0f}")
    print(f"    Transactions:  {cnt:>14}")

print(f"\n  BANK COMBINED:")
print(f"    Total Deposits:     ${bank_total_dep:>14,.0f}")
print(f"    Total Withdrawals:  ${bank_total_wd:>14,.0f}")
print(f"    Net Cash Flow:      ${bank_total_dep - bank_total_wd:>14,.0f}")
print(f"    Total Transactions: {len(bank_2024):>14}")

# Now: what are the outstanding checks in context?
print("\n" + "=" * 70)
print("OUTSTANDING CHECKS - IN CONTEXT")
print("=" * 70)

# Load recon to find NO MATCH checks
recon = list(csv.DictReader(open(r"Z:\Shared\Selenius Holdings\From Northcastle\Bank Statement to GL tie out\2024\GL_to_Bank_Recon_2024_TTI.csv", encoding="utf-8-sig")))
no_match_checks = [r for r in recon if r.get("match_status") == "NO MATCH" and "Check" in r.get("gl_type", "")]
total_nm_check = sum(abs(clean_amt(r.get("gl_amount","0"))) for r in no_match_checks)
print(f"\n  NO MATCH checks in recon: {len(no_match_checks)} totaling ${total_nm_check:,.0f}")

# What % of total GL withdrawals?
pct_of_gl = (total_nm_check / gl_total_wd * 100) if gl_total_wd else 0
print(f"  As % of GL withdrawals (${gl_total_wd:,.0f}): {pct_of_gl:.1f}%")

# These checks - by month
by_month = defaultdict(lambda: {"count":0, "amt":0})
for r in no_match_checks:
    d = parse_d(r.get("gl_date",""))
    if d:
        m = d.strftime("%Y-%m")
        by_month[m]["count"] += 1
        by_month[m]["amt"] += abs(clean_amt(r.get("gl_amount","0")))

print(f"\n  By month:")
for m in sorted(by_month.keys()):
    d = by_month[m]
    print(f"    {m}: {d['count']:>3} checks  ${d['amt']:>12,.0f}")

# Which bank account do the GL accounts map to?
print("\n--- GL ACCOUNT -> BANK ACCOUNT MAPPING ---")
print("  GL 'BMO Corporate Account - Other' = Bank 'BMO-TTICorp'")
print("  GL 'CNB Corp.' = Bank 'CNB-TTICorp2'")
print("  GL 'Tricon Freight Services - CNB' = Bank 'CNB-TTICorp2' (same CNB)")
print("  Bank 'BMO-TTIPark' = NO GL account in TTI books")
print("  Bank 'TWS-Warehouse' = NO GL cash account in TTI books")
print("  Bank 'TK-Investments' = TK entity, not TTI")

# GL amounts that are "in" the bank accounts (what's been matched)
print("\n--- GL AMOUNTS PROVEN BY BANK ---")
exact = sum(abs(clean_amt(r.get("gl_amount","0"))) for r in recon if r.get("match_status") == "EXACT")
prox = sum(abs(clean_amt(r.get("gl_amount","0"))) for r in recon if r.get("match_status") == "PROXIMITY")
nm = sum(abs(clean_amt(r.get("gl_amount","0"))) for r in recon if r.get("match_status") == "NO MATCH")
print(f"  EXACT matched:     ${exact:>14,.0f}")
print(f"  PROXIMITY matched: ${prox:>14,.0f}")
print(f"  NO MATCH:          ${nm:>14,.0f}")
print(f"  TOTAL GL in recon: ${exact+prox+nm:>14,.0f}")
print(f"  Proven by bank:    ${exact+prox:>14,.0f}  ({(exact+prox)/(exact+prox+nm)*100:.1f}%)")