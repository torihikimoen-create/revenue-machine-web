import json
import re
import logging
import os

class AdComplianceEngine:
    def __init__(self, master_data_path=None):
        self.logger = logging.getLogger("AdComplianceEngine")
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.master_data_path = master_data_path or os.path.join(project_root, "config", "ad_compliance_master.json")
        self.master_data = self._load_master_data()

    def _load_master_data(self):
        try:
            with open(self.master_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load ad compliance master data: {e}")
            return {"ng_patterns": []}

    def check_copy(self, text: str):
        """
        広告文のリーガルチェックを行う。
        戻り値: {
            "is_safe": bool,
            "issues": list,
            "risk_score": float,
            "original_text": str
        }
        """
        issues = []
        severity_map = {"CRITICAL": 1.0, "HIGH": 0.7, "MEDIUM": 0.4, "LOW": 0.1}
        total_risk = 0.0

        for p in self.master_data.get("ng_patterns", []):
            pattern = p["pattern"]
            if p.get("is_regex"):
                match = re.search(pattern, text)
            else:
                match = pattern in text if pattern else None

            if match:
                severity = p["severity"]
                issues.append({
                    "detected_pattern": pattern,
                    "severity": severity,
                    "law": p["law"],
                    "reason": p["reason"],
                    "suggestion": p["suggestion"]
                })
                total_risk += severity_map.get(severity, 0.1)

        confidence_score = max(0.0, 1.0 - total_risk)
        
        return {
            "is_safe": len(issues) == 0,
            "issues": sorted(issues, key=lambda x: severity_map.get(x["severity"], 0), reverse=True),
            "confidence_score": round(confidence_score, 2),
            "requires_human_review": confidence_score < 0.8 or any(i["severity"] == "CRITICAL" for i in issues),
            "original_text": text
        }

    def suggest_alternative(self, text: str, mode: str = "ad_copy", sector: str = "General"):
        """
        AI(Humanizer等)を使用して、法的リスクを解消した代替案を生成する。
        """
        from scripts.humanizer import HumanizerEngine
        humanizer = HumanizerEngine()
        
        result = self.check_copy(text)
        if result['is_safe']:
            return text, result

        # 指示文の構築
        forbidden_patterns = [issue['detected_pattern'] for issue in result['issues']]
        legal_reasons = "\n".join([f"- {i['detected_pattern']}: {i['reason']}" for i in result['issues']])
        
        instructions = f"""
指示された「禁止表現」を絶対に含めず、かつ指摘された「法的リスク」を解消してください。
■禁止表現: {forbidden_patterns}
■指摘された法的リスク:
{legal_reasons}
■元の文章: {text}
"""
        
        polished, success = humanizer.polish(instructions, sector=sector, mode=mode)
        
        # 再チェック
        final_check = self.check_copy(polished)
        return polished, final_check
