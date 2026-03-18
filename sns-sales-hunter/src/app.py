import logging
import json
from hunter import SNSHunter
from generator import DMDraftGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SNSHunterApp:
    def __init__(self):
        self.hunter = SNSHunter()
        self.generator = DMDraftGenerator()

    def run_hunt(self, platform: str):
        """
        SNS営業キャンペーンを実行。
        """
        logger.info(f"--- SNS Hunting Start on {platform} ---")
        
        # 1. ターゲット補足
        targets = self.hunter.hunt_targets(platform)
        logger.info(f"Detected {len(targets)} High Priority targets who are struggling with DMs.")

        # 2. 提案DM作成
        results = []
        for target in targets:
            logger.info(f"Analyzing and generating DM for {target['username']}...")
            dm = self.generator.create_dm(target)
            
            item = {
                "user": target['username'],
                "issue": target['issue_detected'],
                "suggested_dm": dm
            }
            results.append(item)
            
            logger.info(f"Target: {target['username']} | Priority: {target['priority']}")

        # 3. 営業リスト保存
        with open("../sns_sales_targets.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        logger.info("--- SNS Hunting Phase Complete. List saved to sns_sales_targets.json ---")

if __name__ == "__main__":
    app = SNSHunterApp()
    app.run_hunt("X / Twitter")
