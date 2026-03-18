import os
import random
import logging
import json
from datetime import datetime

# モック用のSNSシグナル（実際にはAPI等でキーワード監視を行う）
SNS_MOCK_SIGNALS = [
    {"platform": "X", "user": "biz_owner_tokyo", "text": "産廃のマニフェスト電子化、中小には負担がデカすぎる。誰か自動化してくれ...", "sector": "WasteManagement"},
    {"platform": "X", "user": "care_manager_jp", "text": "特定技能の報告関係、また不備指摘された。事務作業だけで一日が終わる。", "sector": "CareGiverVisa"},
    {"platform": "LinkedIn", "user": "logistics_pro", "text": "CLO選任の法改正、準備が間に合っていない企業が多い。アウトソース先を探している。", "sector": "TruckLogistics"},
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SNSScout")

class SNSScout:
    """
    SNS上の「悲鳴（シグナル）」を検知し、リード候補として抽出するプロトタイプ。
    """
    def __init__(self):
        self.results_file = "sns_leads.json"

    def scan_for_pain_signals(self, keyword_list):
        """
        特定のキーワードに関連する痛みのシグナルをスキャンするシミュレーション。
        """
        logger.info(f"Scanning SNS for signals matching keywords: {keyword_list}")
        
        found_leads = []
        # シミュレーション：ランダムにシグナルをピックアップ
        for _ in range(random.randint(1, 3)):
            signal = random.choice(SNS_MOCK_SIGNALS)
            lead = {
                "timestamp": datetime.now().isoformat(),
                "platform": signal["platform"],
                "source_user": signal["user"],
                "content": signal["text"],
                "detected_sector": signal["sector"],
                "intent_score": random.randint(70, 95)  # 購買意欲・痛みの深さのスコアリング
            }
            found_leads.append(lead)
        
        self.save_leads(found_leads)
        return found_leads

    def save_leads(self, leads):
        data = []
        if os.path.exists(self.results_file):
            with open(self.results_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        data.extend(leads)
        
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(leads)} new SNS leads to {self.results_file}")

if __name__ == "__main__":
    scout = SNSScout()
    # キーワード「自動化」「事務負担」「法改正」などでスキャン
    keywords = ["自動化", "事務負担", "法改正", "義務化"]
    leads = scout.scan_for_pain_signals(keywords)
    
    print("\n--- [DETECTED SNS SIGNALS] ---")
    for l in leads:
        print(f"[{l['platform']}] @{l['source_user']}: {l['content']} (Intent: {l['intent_score']}%)")
