import logging
import json
from sniper import GoogleMapsSniper
from generator import ProposalGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SalesAutomationApp:
    def __init__(self):
        self.sniper = GoogleMapsSniper()
        self.generator = ProposalGenerator()

    def run_campaign(self, category: str, location: str):
        """
        営業キャンペーンを自動実行する。
        """
        logger.info(f"--- Campaign Start: {category} in {location} ---")
        
        # 1. ターゲット（リード）の抽出
        leads = self.sniper.search_leads(category, location)
        logger.info(f"Found {len(leads)} qualified HOT leads.")

        # 2. 各リードへの個別提案作成
        campaign_results = []
        for lead in leads:
            logger.info(f"Generating proposal for: {lead['name']}...")
            proposal = self.generator.generate(lead)
            
            result = {
                "store": lead['name'],
                "contact": lead['contact'],
                "proposal_preview": proposal[:100] + "..."
            }
            campaign_results.append(result)
            
            # 本来はここで自動メール送信 or フォーム投稿APIへ
            logger.info(f"Proposal ready for {lead['name']} (Contact: {lead['contact']})")

        # 3. 営業進捗レポートの出力
        with open("../sales_leads_report.json", "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, ensure_ascii=False, indent=2)
            
        logger.info("--- Campaign Planning Phase Complete ---")

if __name__ == "__main__":
    app = SalesAutomationApp()
    app.run_campaign("レストラン", "東京都中央区")
