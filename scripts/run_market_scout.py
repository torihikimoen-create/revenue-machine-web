import time
import logging
from scripts.market_explorer import BlueOceanExplorer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MarketScoutSlot")

def run_24h_monitoring():
    """
    24時間体制の市場監視スロット。定期的に世界のトレンドをスキャンし、チャンスがあれば提案を生成する。
    """
    explorer = BlueOceanExplorer()
    logger.info("Starting 24/7 Market Monitoring Slot...")
    
    # プロトタイプ用：1回実行して終了（実際にはwhile Trueで一定間隔実行）
    try:
        analysis = explorer.explore_new_opportunities()
        proposal_path = explorer.generate_proposal_report(analysis)
        logger.info(f"Scout successful. Proposal queued for approval: {proposal_path}")
    except Exception as e:
        logger.error(f"Scout error: {e}")

if __name__ == "__main__":
    run_24h_monitoring()
