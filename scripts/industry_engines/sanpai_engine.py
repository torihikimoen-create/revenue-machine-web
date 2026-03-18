import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger("SanpaiEngine")

class SanpaiComplianceEngine:
    """
    産業廃棄物処理（マニフェスト管理）に特化した専門処理エンジン。
    廃棄物処理法に基づくバリデーションと、行政報告用データの生成を行う。
    """
    def __init__(self):
        # 法令知識ベースのシミュレーション
        self.regulations = {
            "retention_period_years": 5,
            "report_deadline_month": 6,
            "standard_waste_types": ["燃え殻", "汚泥", "廃油", "廃酸", "廃アルカリ", "廃プラスチック類"]
        }
        # マスターデータのロード（自己修復用）
        self.master_data_path = os.path.join(os.path.dirname(__file__), "master_data.json")
        self.master_data = self._load_master_data()

    def _load_master_data(self):
        try:
            if os.path.exists(self.master_data_path):
                with open(self.master_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load master data: {e}")
        return {"contracts": [], "manifest_history": []}

    def _auto_heal(self, data):
        """
        データの不備をマスターデータや履歴から自動補完・修正する。
        監査方針: 負の数量・必須項目欠損・契約なし/期限切れは補完せず CRITICAL のままとする。
        マニフェストIDのみ、履歴に完全一致がある場合に補完する（台帳との突合で確実な場合のみ）。
        """
        healed_logs = []

        # 1. 契約はマスターで補完しない（契約なし・期限切れはすべて validate_compliance で CRITICAL 検知）

        # 2. マニフェストIDの補完（履歴に一致がある場合のみ）
        if not data.get("manifest_id") and data.get("waste_type") is not None:
            history = self.master_data.get("manifest_history", [])
            qty_val = data.get("quantity")
            match = next(
                (h for h in history if h["type"] == data.get("waste_type") and (h["qty"] == qty_val or (isinstance(qty_val, (int, float)) and abs(float(h["qty"]) - float(qty_val)) < 1e-6))),
                None,
            )
            if match:
                data["manifest_id"] = match["id"]
                healed_logs.append(f"Fixed: Restored missing Manifest ID {match['id']} from history")

        # 3. 負の数量は補完しない（validate_compliance で CRITICAL として検知する方針）
        # 4. 日付欠落は補完しない（必須項目として CRITICAL のまま）

        if healed_logs:
            data["_healed"] = True
            data["_healed_logs"] = healed_logs
            logger.info(f"Auto-Healed: {'; '.join(healed_logs)}")
        
        return data

    def _is_expired(self, expiry_date_str):
        if not expiry_date_str: return True
        try:
            expiry = datetime.strptime(str(expiry_date_str).strip()[:10], "%Y-%m-%d")
            return expiry < datetime.now()
        except:
            return True

    def analyze_manifest(self, raw_data):
        """
        生データ（マニフェスト）を解析し、構造化データに変換する。
        数値や単位の正規化を行い、さらに自己修復を行う。
        """
        logger.info("Analyzing Industrial Waste Manifest data...")
        if not raw_data or not isinstance(raw_data, dict):
            return {"_input_error": "INPUT_INVALID"}

        # 数量の正規化
        qty_raw = raw_data.get("qty") or raw_data.get("quantity") or 0
        try:
            quantity = float(qty_raw) if qty_raw is not None else 0.0
        except (TypeError, ValueError):
            quantity = -1.0

        # 単位の正規化
        unit_raw = raw_data.get("unit") or "t"
        unit = str(unit_raw).strip().lower() if unit_raw else "t"
        if unit not in ("t", "kg", "m3", "l"):
            unit = "unknown"

        structured_data = {
            "manifest_id": raw_data.get("id") or raw_data.get("manifest_id"),
            "waste_type": raw_data.get("type") or raw_data.get("waste_type"),
            "quantity": quantity,
            "unit": unit,
            "issued_date": raw_data.get("date") or raw_data.get("issued_date"),
            "contract_exists": bool(raw_data.get("has_contract", False)),
            "expiry_date": raw_data.get("contract_expiry"),
        }
        
        # 自己修復プロセスの実行
        return self._auto_heal(structured_data)

    def validate_compliance(self, data):
        """
        廃棄物処理法および関連法規に基づいた厳格なバリデーション。
        自己修復済みのデータに対しては、警告レベルを下げて自動パスさせる。
        """
        if data.get("_input_error"):
            return {
                "is_compliant": False,
                "requires_human_review": True,
                "confidence_score": 0.0,
                "issues": [{"severity": "CRITICAL", "code": "INPUT_INVALID", "message": "入力データが空または不正です。"}]
            }

        issues = []
        confidence_score = 1.0  # 初期値は満点
        healed_msgs = data.get("_healed_logs", [])

        # 1. 必須項目の欠落チェック
        required_fields = {
            "manifest_id": ("MISSING_MANIFEST_ID", "マニフェストID（交付番号）が欠落しています。"),
            "waste_type": ("MISSING_WASTE_TYPE", "産業廃棄物の種類（品目）が指定されていません。"),
            "issued_date": ("MISSING_ISSUED_DATE", "交付年月日が記載されていません。"),
        }
        for field, (code, msg) in required_fields.items():
            if not data.get(field):
                issues.append({"severity": "CRITICAL", "code": code, "message": msg})
                confidence_score -= 0.5

        # 2. 確定的な法的チェック（決定論的ロジック）
        # 委託契約書の有無チェック
        if not data.get("contract_exists"):
            issues.append({
                "severity": "CRITICAL",
                "code": "NO_CONTRACT",
                "message": "【重大違反】委託契約書の存在が確認できません。廃棄物処理法第12条の3第1項に抵触します。"
            })
            confidence_score -= 0.5

        # 3. 契約期限のチェック
        if data.get("expiry_date"):
            try:
                expiry = datetime.strptime(str(data["expiry_date"]).strip()[:10], "%Y-%m-%d")
                if expiry < datetime.now():
                    issues.append({
                        "severity": "CRITICAL",
                        "code": "CONTRACT_EXPIRED",
                        "message": f"【重大違反】委託契約が期限切れです（期限: {data['expiry_date']}）。"
                    })
                    confidence_score -= 0.4
            except (ValueError, TypeError):
                issues.append({
                    "severity": "HIGH",
                    "code": "INVALID_DATE_FORMAT",
                    "message": "契約期限の形式が不正です。実務上のリスクを避けるため、手動確認が必要です。"
                })
                confidence_score -= 0.3

        # 4. 品目コードの妥当性
        if data.get("waste_type") and data.get("waste_type") not in self.regulations["standard_waste_types"]:
            issues.append({
                "severity": "LOW",
                "code": "NON_STANDARD_TYPE",
                "message": f"品目 '{data.get('waste_type')}' は標準的な分類外です。自治体独自の解釈を確認してください。"
            })
            confidence_score -= 0.1

        # 5. 数量の異常検知
        quantity = data.get("quantity")
        if quantity is not None:
            if quantity < 0:
                issues.append({
                    "severity": "CRITICAL",
                    "code": "NEGATIVE_QUANTITY",
                    "message": "数量が負の値です。入力ミスまたはデータ不備の可能性が高いです。"
                })
                confidence_score -= 0.6
            elif quantity > 1000:  # 異常な大量廃棄
                issues.append({
                    "severity": "MEDIUM",
                    "code": "UNUSUAL_QUANTITY",
                    "message": "数量が異常に大きいです。入力ミス（桁ずれ等）または特殊な処理の可能性があります。"
                })
                confidence_score -= 0.2

        # 6. 自己修復結果の判定反映（マニフェストIDの履歴補完のみ緩和）
        for h_msg in healed_msgs:
            if "Fixed: Restored missing Manifest ID" in h_msg:
                issues = [i for i in issues if i["code"] != "MISSING_MANIFEST_ID"]
                confidence_score += 0.4

        # 7. 実務遂行判定
        requires_human = confidence_score < 0.8 or any(i["severity"] == "CRITICAL" for i in issues)

        return {
            "is_compliant": len([i for i in issues if i["severity"] in ["CRITICAL", "HIGH"]]) == 0,
            "requires_human_review": requires_human,
            "confidence_score": min(1.0, max(0.0, confidence_score)),
            "issues": issues,
            "audit_timestamp": datetime.now().isoformat(),
        }

    def generate_government_report(self, processed_items):
        """
        自治体提出用（産業廃棄物管理票交付状況報告書）のフォーマットを生成。
        Excel 等への出力を想定し、details はキーが統一された辞書のリストとする。
        """
        logger.info("Generating Government Compliance Report...")
        # 数値は float に正規化（Excel 出力時に型崩れを防ぐ）
        def _norm_item(item):
            q = item.get("quantity", 0)
            try:
                qty = float(q) if q is not None else 0.0
            except (TypeError, ValueError):
                qty = 0.0
            return {
                "manifest_id": str(item.get("manifest_id", "")),
                "waste_type": str(item.get("waste_type", "")),
                "quantity": qty,
                "unit": str(item.get("unit", "t")),
                "issued_date": str(item.get("issued_date", "")),
                "contract_exists": bool(item.get("contract_exists", False)),
                "expiry_date": str(item.get("expiry_date", "")),
            }
        details = [_norm_item(i) for i in processed_items]
        report = {
            "report_type": "産業廃棄物管理票交付状況報告書",
            "period": f"{datetime.now().year - 1}年度",
            "summary": {
                "total_count": len(details),
                "total_quantity": round(sum(i["quantity"] for i in details), 2),
                "unit": "t",
            },
            "details": details,
            "generated_at": datetime.now().isoformat(),
        }
        return report

if __name__ == "__main__":
    # エンジンの単体テスト
    engine = SanpaiComplianceEngine()
    test_manifest = {
        "id": "M12345678",
        "type": "廃プラスチック類",
        "qty": "5.2",
        "date": "2026-03-01",
        "has_contract": False,
        "contract_expiry": "2026-02-28"
    }
    
    analyzed = engine.analyze_manifest(test_manifest)
    audit_result = engine.validate_compliance(analyzed)
    
    print("\n=== Sanpai Engine Audit Report ===")
    print(f"Compliance Status: {'PASS' if audit_result['is_compliant'] else 'FAIL'}")
    for issue in audit_result["issues"]:
        print(f"[{issue['severity']}] {issue['code']}: {issue['message']}")
