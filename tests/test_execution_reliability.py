import unittest
import os
from scripts.industry_engines.sanpai_engine import SanpaiComplianceEngine

class TestSanpaiReliability(unittest.TestCase):
    def setUp(self):
        self.engine = SanpaiComplianceEngine()

    def test_critical_contract_missing(self):
        """契約書なしの重大違反を確実に検知できるか"""
        data = {
            "id": "ERR001",
            "type": "燃え殻",
            "qty": 10.0,
            "date": "2026-03-01",
            "has_contract": False
        }
        result = self.engine.validate_compliance(self.engine.analyze_manifest(data))
        self.assertFalse(result["is_compliant"])
        self.assertTrue(any(i["code"] == "NO_CONTRACT" for i in result["issues"]))

    def test_expired_contract(self):
        """期限切れ契約を確実に検知できるか"""
        data = {
            "id": "ERR002",
            "type": "汚泥",
            "qty": 5.5,
            "date": "2026-03-01",
            "has_contract": True,
            "contract_expiry": "2023-01-01"
        }
        result = self.engine.validate_compliance(self.engine.analyze_manifest(data))
        self.assertFalse(result["is_compliant"])
        self.assertTrue(any(i["code"] == "CONTRACT_EXPIRED" for i in result["issues"]))

    def test_quantity_as_string_no_type_error(self):
        """数量が文字列でも例外にならず数値として検証されるか (P0)"""
        data = {
            "id": "STR001",
            "type": "廃油",
            "qty": "1.5", # 文字列
            "date": "2026-03-01",
            "has_contract": True
        }
        analyzed = self.engine.analyze_manifest(data)
        self.assertIsInstance(analyzed["quantity"], float)
        self.assertEqual(analyzed["quantity"], 1.5)

    def test_missing_required_fields_critical(self):
        """必須項目（マニフェストID、品目、日付）欠損で CRITICAL になるか (P1)"""
        data = {
            "has_contract": True
        }
        result = self.engine.validate_compliance(self.engine.analyze_manifest(data))
        self.assertFalse(result["is_compliant"])
        codes = [i["code"] for i in result["issues"]]
        self.assertIn("MISSING_MANIFEST_ID", codes)
        self.assertIn("MISSING_WASTE_TYPE", codes)
        self.assertIn("MISSING_ISSUED_DATE", codes)

    def test_negative_quantity_rejected(self):
        """負の数量（AI誤認識）で CRITICAL になるか (P1)"""
        data = {
            "id": "NEG001",
            "type": "廃酸",
            "qty": -10.0,
            "date": "2026-03-01",
            "has_contract": True
        }
        result = self.engine.validate_compliance(self.engine.analyze_manifest(data))
        self.assertTrue(any(i["code"] == "NEGATIVE_QUANTITY" for i in result["issues"]))
        self.assertTrue(result["requires_human_review"])

    def test_invalid_expiry_date_format_high_severity(self):
        """期限日付の形式不正で HIGH になり人間確認を仰ぐか (P1)"""
        data = {
            "id": "DATE001",
            "type": "廃プラスチック類",
            "qty": 1.0,
            "date": "2026-03-01",
            "has_contract": True,
            "contract_expiry": "Invalid Date"
        }
        result = self.engine.validate_compliance(self.engine.analyze_manifest(data))
        self.assertTrue(any(i["code"] == "INVALID_DATE_FORMAT" for i in result["issues"]))
        self.assertTrue(result["requires_human_review"])

    def test_empty_input_graceful_handling(self):
        """空入力でクラッシュせず INPUT_INVALID を返すか (P1)"""
        result = self.engine.validate_compliance(self.engine.analyze_manifest(None))
        self.assertEqual(result["issues"][0]["code"], "INPUT_INVALID")

if __name__ == "__main__":
    unittest.main()
