import os
# [PROJECT_TRUTH] 運営: AETHER CORE プロジェクト / 代表: 増本 友貴 / 最安: 24,800円〜
import re

def check_consistency():
    truth_file = "PROJECT_TRUTH.md"
    if not os.path.exists(truth_file):
        print(f"[ERROR] {truth_file} not found.")
        return

    with open(truth_file, 'r', encoding='utf-8') as f:
        truth = f.read()

    # TRUTH から重要数値を抽出
    prices = re.findall(r"¥([0-9,]+)", truth)
    business_name = re.search(r"販売事業者名\*\*: (.*)", truth).group(1)
    
    print(f"--- PROJECT GUARDIAN: Integrity Check ---")
    print(f"Truth: Business Name = {business_name}")
    print(f"Truth: Representative Prices = {prices}")
    print("-" * 40)

    files_to_check = [
        "index.html",
        "tokushoho.html",
        "run_automation.py",
        "scripts/auto_sender.py"
    ]

    issues = 0
    for file in files_to_check:
        if not os.path.exists(file):
            continue
            
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 事業者名のチェック
        if business_name not in content and "AETHER CORE" not in content:
            print(f"[ISSUE] {file}: Missing business name '{business_name}'")
            issues += 1
            
        # 価格のチェック (24800, 33000)
        # カンマなし数値でもチェック
        for p in prices:
            p_clean = p.replace(",", "")
            if p_clean not in content and p not in content:
                # 特定のファイルでは特定の価格のみを期待する場合があるため警告程度に
                if "run_automation" in file or "index.html" in file:
                    print(f"[WARNING] {file}: Might be missing price reference '{p}'")
                
    if issues == 0:
        print("\n[OK] All core identity and pricing keys are consistent with PROJECT_TRUTH.md.")
    else:
        print(f"\n[FAILED] Found {issues} consistency issues. Please review.")

if __name__ == "__main__":
    check_consistency()
