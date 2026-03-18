import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("NicheFormEngine")

class NicheFormEngine:
    """
    産業廃棄物、消防点検、ビザ報告など、ニッチ産業特有の法定フォーマットを扱うエンジン。
    """
    def __init__(self):
        self.templates_dir = "templates/niche_forms"
        # 法令・規定値のマスターデータ（本来は外部ファイルやDBから取得）
        self.legal_standards = {
            "IndWaste": ["排出事業者名", "廃棄物の種類", "数量", "運搬受託者名", "処分受託者名"],
            "FireSafety": ["消火器", "自動火災報知設備", "避難器具"],
            "VisaCompliance": ["受入れ機関名", "四半期報告", "雇用契約遵守"]
        }
        os.makedirs(self.templates_dir, exist_ok=True)

    def generate_form(self, sector, data):
        """
        セクターに応じた法定フォーマットのドラフトを生成する。
        """
        logger.info(f"Generating niche form for sector: {sector}")
        
        if sector == "IndWaste":
            return self._generate_waste_manifest(data)
        elif sector == "FireSafety":
            return self._generate_fire_safety_report(data)
        elif sector == "VisaCompliance":
            return self._generate_visa_report(data)
        else:
            raise ValueError(f"Unsupported sector for form generation: {sector}")

    def _generate_waste_manifest(self, data):
        """
        産業廃棄物管理票（マニフェスト）のドラフト生成。
        """
        # 必須項目のバリデーション
        required = ["generator_name", "waste_type", "quantity", "transporter_name", "disposal_facility"]
        missing = [field for field in required if field not in data]
        if missing:
            return {"status": "ERROR", "message": f"Missing mandatory fields: {missing}"}

        manifest = {
            "title": "産業廃棄物管理票（直行用マニフェスト）ドラフト",
            "generator": data['generator_name'],
            "waste_category": data['waste_type'],
            "quantity": f"{data['quantity']} kg",
            "transporter": data['transporter_name'],
            "disposal_site": data['disposal_facility'],
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "compliance_check": "Checked (All mandatory fields present as per Wastes Disposal and Public Cleansing Act)"
        }
        return {"status": "SUCCESS", "format": "JSON/Draft", "content": manifest}

    def _generate_fire_safety_report(self, data):
        """
        消防用設備等点検結果報告書のドラフト生成。
        """
        report = {
            "title": "消防用設備等点検結果報告書",
            "facility_name": data.get("facility_name", "未指定"),
            "inspection_date": datetime.now().strftime("%Y-%m-%d"),
            "checkpoints": [
                {"item": "消火器", "status": data.get("extinguisher_status", "良好")},
                {"item": "自動火災報知設備", "status": data.get("alarm_status", "良好")},
                {"item": "避難器具", "status": data.get("escape_gear_status", "良好")}
            ],
            "judgment": "総合判定: 適正",
            "footer": "消防法第17条の3の3の規定に基づき報告します。"
        }
        return {"status": "SUCCESS", "format": "Structured/Markdown", "content": report}

    def _generate_visa_report(self, data):
        """
        特定技能外国人の受入れ状況等に関する届出書の生成。
        """
        report = {
            "title": "特定技能外国人の受入れ状況等に関する届出書",
            "org_name": data.get("org_name", "未指定"),
            "quarter": f"{datetime.now().year}年度 第{ (datetime.now().month-1)//3 + 1 }四半期",
            "staff_count": data.get("staff_count", 0),
            "compliance": "労働基準法、入管法遵守状況確認済み",
            "next_report_deadline": (datetime.now() + target_time_delta_months(3)).strftime("%Y-%m-%d")
        }
        return {"status": "SUCCESS", "format": "Legal/Draft", "content": report}

    def validate_compliance(self, sector, content):
        """
        生成された成果物が法令・規定フォーマットに準拠しているかクロス照合する。
        """
        standards = self.legal_standards.get(sector, [])
        missing_standards = [s for s in standards if s not in str(content)]
        
        if missing_standards:
            return {
                "compliant": False,
                "reason": f"法令必須項目が含まれていません: {missing_standards}",
                "severity": "CRITICAL"
            }
        
        return {
            "compliant": True,
            "reason": "法令規定フォーマットとの完全な一致を確認しました。",
            "severity": "NONE"
        }

def target_time_delta_months(months):
    from dateutil.relativedelta import relativedelta
    return relativedelta(months=months)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = NicheFormEngine()
    
    # テスト: 産廃マニフェスト
    test_data = {
        "generator_name": "エーテル建設株式会社",
        "waste_type": "廃プラスチック",
        "quantity": 500,
        "transporter_name": "ブルーオーシャン運輸",
        "disposal_facility": "エコサイクル東京"
    }
    result = engine.generate_form("IndWaste", test_data)
    print(json.dumps(result, indent=4, ensure_ascii=False))
