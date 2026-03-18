import logging
import json
from finder import B2BDealFinder
from builder import BusinessProposalBuilder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BigDealAutomationApp:
    def __init__(self):
        self.finder = B2BDealFinder()
        self.builder = BusinessProposalBuilder()

    def run(self):
        logger.info("--- B2B Deal Hunting Start ---")
        
        # 1. 案件発掘
        opportunities = self.finder.find_opportunities()
        logger.info(f"Detected {len(opportunities)} profitable B2B deals.")

        # 2. 提案書作成
        proposals = []
        for deal in opportunities:
            logger.info(f"Building formal proposal for {deal['client']}...")
            text = self.builder.build_proposal(deal)
            
            proposals.append({
                "client": deal['client'],
                "budget": deal['budget'],
                "proposal": text
            })

        # 3. 営業進捗レポート
        with open("../b2b_opportunities.json", "w", encoding="utf-8") as f:
            json.dump(proposals, f, ensure_ascii=False, indent=2)
            
        logger.info("--- B2B Hunting Complete. Ready for formal outreach ---")

if __name__ == "__main__":
    app = BigDealAutomationApp()
    app.run()
