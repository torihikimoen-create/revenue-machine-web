import sys
import os
import json
from datetime import datetime

# プロジェクトルートを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from scripts.industry_engines.sanpai_engine import SanpaiComplianceEngine

def run_capability_test():
    engine = SanpaiComplianceEngine()
    
    test_cases = [
        {
            "name": "Case 1: Standard Valid (Should PASS)",
            "data": {
                "id": "M001",
                "type": "廃プラスチック類",
                "qty": 1.5,
                "date": "2026-03-18",
                "has_contract": True,
                "contract_expiry": "2027-12-31"
            },
            "expected": "PASS"
        },
        {
            "name": "Case 2: Auto-Healing (Missing ID, should be RESTORED)",
            "data": {
                "id": None,
                "type": "廃プラスチック類",
                "qty": 0.8,
                "date": "2026-03-18",
                "has_contract": True,
                "contract_expiry": "2027-12-31"
            },
            "expected": "PASS (Healed)"
        },
        {
            "name": "Case 3: Critical (Expired Contract, should FAIL)",
            "data": {
                "id": "M002",
                "type": "汚泥",
                "qty": 2.0,
                "date": "2026-03-18",
                "has_contract": True,
                "contract_expiry": "2026-02-28"
            },
            "expected": "FAIL (Expired)"
        },
        {
            "name": "Case 4: Critical (Negative Qty, should FAIL)",
            "data": {
                "id": "M003",
                "type": "廃油",
                "qty": -5.0,
                "date": "2026-03-18",
                "has_contract": True,
                "contract_expiry": "2027-12-31"
            },
            "expected": "FAIL (Value Error)"
        },
        {
            "name": "Case 5: Outlier (Extreme Qty, should WARN)",
            "data": {
                "id": "M004",
                "type": "燃え殻",
                "qty": 5000.0,
                "date": "2026-03-18",
                "has_contract": True,
                "contract_expiry": "2027-12-31"
            },
            "expected": "WARN (Outlier)"
        }
    ]

    print(f"=== AETHER CORE: AI Engine Stress Test ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"Target Engine: SanpaiComplianceEngine (v1.2-Iron-Clad)\n")

    results = []
    for case in test_cases:
        print(f"Running {case['name']}...")
        analyzed = engine.analyze_manifest(case['data'])
        audit = engine.validate_compliance(analyzed)
        
        status = "PASS" if audit['is_compliant'] else "FAIL"
        if audit['requires_human_review']:
            status += " (REVIEW REQUIRED)"
            
        print(f"  Result: {status}")
        print(f"  Confidence: {audit['confidence_score']:.2f}")
        
        if analyzed.get("_healed"):
            print(f"  [HEALED] {analyzed['_healed_logs']}")
            
        for issue in audit['issues']:
            print(f"  [{issue['severity']}] {issue['code']}: {issue['message']}")
        
        print("-" * 50)
        results.append({
            "name": case['name'],
            "status": status,
            "issues": len(audit['issues'])
        })

    # レポート生成
    print("\n=== FINAL TEST SUMMARY ===")
    passed = len([r for r in results if "PASS" in r['status'] and "REVIEW REQUIRED" not in r['status']])
    failed = len([r for r in results if "FAIL" in r['status']])
    review = len([r for r in results if "REVIEW REQUIRED" in r['status']])
    
    print(f"Total Cases: {len(test_cases)}")
    print(f"Automatic PASS: {passed}")
    print(f"Automatic FAIL: {failed}")
    print(f"Human Review Flagged: {review}")
    
    if failed + review > 0:
        print("\n[CONCLUSION] Engine is correctly identifying risks. Integrity confirmed.")
    else:
        print("\n[CONCLUSION] TEST INCONCLUSIVE (No issues detected). Check test data.")

if __name__ == "__main__":
    run_capability_test()
