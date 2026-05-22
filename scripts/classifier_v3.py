import json
import re

CUSTOMERS = [
    "AMAZON", "HONDA", "ARMADA", "BECTON", "BEST-LOG", "BESTLOG", 
    "BROTHER INT", "BUSCEMI", "CAPITAL LOGISTICS", "CMA CGM", "CMA/CGM", 
    "CORCORAN", "COSCO", "EXPEDITORS", "FALCON", "FARBER", 
    "GEORGE P. JOHNSON", "GPJCOMPANY", "GET JPN", "GET - JPN", "HAVI", 
    "INTEGRITY CARGO", "ISAGENIX", "ITG TRANSPORT", "KUEHNE", "MAERSK", 
    "MALLORY", "MASTERPIECE", "MEDITERRANEAN", "MEIKO", 
    "MITSUI", "NIPPON", "OCEAN LINK", "OCEAN NETWORK", "OLIMP", "ONEILL", 
    "OOCL", "ORR FIRE", "PEACE INT", "PRIME TRANSPORT", "RANON", 
    "ROCK-IT", "ROLYS", "ROYAL COCO", "SCAN GLOBAL", "SCHAEFER", 
    "SHAEFER", "SHOCKWAVE", "SIENA FOODS", "SUNSET", 
    "TEAMPOWER", "TOTAL LOGISTICS", "TOTAL QUALITY", "TOTO", "VTMI", 
    "VYAIRE", "WEST COAST TRENDS", "WM STONE", "W.M. STONE", "WTS CUSTOMS",
    "CASS INFO", "OTR CAPITAL"
]

FREIGHT_PROVIDERS = [
    "BLUE BIRD", "BRISAS", "CEA TRUCKING", "CNN TRANS", "ECP TRANSPORT", 
    "ENRIQUEZ", "EZ FREIGHT", "GDL EXPRESS", "GI TRANSPORT", "JT TRANS", 
    "LAND AMERICA", "MVM TRUCKING", "OBLATOS", "REX RAPID", "TRINITY PORT", "YOGI"
]

def classify_transaction(t_type, desc):
    """Applies business logic to classify Tricon Transportation transactions."""
    desc_upper = desc.upper()
    
    # Categorize Freight Providers first (Applies to both OPEX and Refunds/Contra-Expense)
    if any(fp in desc_upper for fp in FREIGHT_PROVIDERS):
        reason = "Freight provider (Contra-Expense/Refund)" if t_type == "deposit" else "Subcontracted Services (OPEX)"
        return "OPEX-Non Payroll", "High", reason

    # Base Categorization for Deposits
    if t_type == "deposit":
        if any(cust in desc_upper for cust in CUSTOMERS):
            return "Revenue", "High", "Direct customer payment or freight processor"
        elif "LOAN" in desc_upper:
            return "Financing", "High", "Proceeds from loan"
        elif "TRANSFER" in desc_upper and "ZELLE" not in desc_upper:
            return "Financing", "Medium", "Intercompany (e.g. to T-K) or financing transfer"
        else:
            return "Revenue", "High", "Customer payment, parking revenue, or general deposit"
            
    # Categorization for Withdrawals
    if "BARRETT" in desc_upper:
        return "Payroll", "High", "Barrett Business Services PEO / Payroll"
    elif "CALSAVERS" in desc_upper:
        return "Payroll", "High", "Retirement contribution / Payroll deduction"
    elif "PAYCARGO" in desc_upper:
        return "OPEX-Non Payroll", "High", "Freight / logistics payment"
    elif any(k in desc_upper for k in ["AM NAT INS", "AMERICAN GENERAL", "AMERICAN GEN", "BANNER LIFE", "INSURANCE", "IPFS"]):
        return "OPEX-Non Payroll", "High", "Insurance premium or financing"
    elif "AMEX" in desc_upper or "AMERICAN EXPRESS" in desc_upper:
        return "OPEX-Non Payroll", "High", "Credit card payment"
    elif any(k in desc_upper for k in ["DTFS", "GM FINANCIAL", "GMF", "AFFIRM"]):
        return "Financing", "High", "Equipment Lease/Loan/POS Financing"
    elif "LOAN" in desc_upper:
        return "Financing", "High", "Loan payment"
    elif "WIRE" in desc_upper and t_type == "withdrawal":
        return "Vendor Payment", "Medium", "Outgoing wire transfer"
    elif "TRANSFER" in desc_upper and "ZELLE" not in desc_upper:
        return "Financing", "Medium", "Intercompany to T-K / Internal bank transfer"
    elif any(k in desc_upper for k in ["TAX", "IRS", "FRANCHISE TAX BO"]):
        return "OPEX-Non Payroll", "High", "Tax payment"
    elif any(k in desc_upper for k in ["FEE", "SERV CHG", "PAPER STMT", "BMO HARRIS"]):
        return "OPEX-Non Payroll", "High", "Bank or service fees"
    elif "CHECK" in desc_upper or "CK" in desc_upper or re.search(r'^\d{3,6}\s*[\^\*]?$', desc.strip()):
        return "Vendor Payment", "Medium", "Check issued to vendor"
    
    return "OPEX-Non Payroll", "Low", "Unclassified withdrawal"

def main():
    with open('master_raw_extractions/MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
        data = json.load(f)

    metadata = data.get("_metadata", {})
    ext_method = metadata.get("extraction_method", "")
    ext_at = metadata.get("generated_at", "")

    flat_transactions = []
    tid = 1

    for file_info in data.get("files", []):
        filename = file_info.get("filename", "")
        full_path = file_info.get("full_path", "")
        
        # 1. Map Accounts
        account = ""
        account_number = ""
        if "Account #9530" in full_path:
            account = "TWS-Warehouse"
            account_number = "9530"
        elif "BMO TTI CORP1" in filename or "0677032724" in full_path:
            account = "BMO-TTICorp"
            account_number = "0677032724"
        elif "0069956696" in full_path or "TTI PARK" in filename:
            account = "BMO-TTIPark"
            account_number = "0069956696"
        elif "CNB" in full_path:
            account = "CNB-TTICorp2"
            account_number = "CNB"
        elif "TK" in full_path:
            account = "TK-Investments"
            account_number = "TK"
            
        # 2. Parse Year Context from filename
        year_match = re.search(r'20\d{2}', filename)
        file_year = year_match.group(0) if year_match else ""
        
        for page in file_info.get("page_extractions", []):
            for trans in page.get("transactions", []):
                raw_date = trans.get("date", "")
                desc = trans.get("description", "")
                amt = trans.get("amount", 0.0)
                t_type = trans.get("type", "")
                
                # 3. Standardize Dates
                p_date = ""
                t_month = ""
                try:
                    parts = raw_date.replace('-', '/').split('/')
                    if len(parts) >= 2:
                        t_month = parts[0].zfill(2)
                        d = parts[1].zfill(2)
                        if file_year:
                            p_date = f"{file_year}-{t_month}-{d}"
                except:
                    pass
                
                # 4. Extract Check Numbers
                chk = None
                cm = re.search(r'(?i)check\s*(?:no\.?\s*)?(\d+)', desc)
                if cm:
                    chk = cm.group(1)
                elif re.search(r'^\d{3,6}\s*[\^\*]?$', desc.strip()):
                    chk = re.sub(r'[^\d]', '', desc.strip())
                    
                # 4b. Extract Reference/Trace Numbers
                ref_num = None
                ref_match = re.search(r'(?:Trace#|Trn:|Transaction#)[\s:]*([A-Za-z0-9]+)', desc, re.IGNORECASE)
                if ref_match:
                    ref_num = ref_match.group(1)
                    
                # 5. Apply Classification
                bucket, conf, reason = classify_transaction(t_type, desc)

                flat_transactions.append({
                    "id": tid,
                    "date": p_date or raw_date,
                    "year": file_year,
                    "month": t_month,
                    "account": account,
                    "account_number": account_number,
                    "amount": amt,
                    "type": t_type,
                    "description": desc,
                    "check_number": chk,
                    "reference_number": ref_num,
                    "bucket": bucket,
                    "confidence": conf,
                    "reasoning": reason,
                    "statement_file": filename,
                    "source_file": full_path,
                    "extraction_method": ext_method,
                    "extracted_at": ext_at
                })
                tid += 1

    # Output the flattened JSON array
    output_file = 'tricon_classified_transactions.json'
    with open(output_file, 'w') as out_f:
        json.dump(flat_transactions, out_f, indent=2)
        
    print(f"Successfully exported {len(flat_transactions)} classified transactions to {output_file}")

if __name__ == "__main__":
    main()
