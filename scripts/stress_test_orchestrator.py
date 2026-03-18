import time
import logging
import random
from datetime import datetime
from scripts.market_explorer import BlueOceanExplorer
from scripts.global_discovery import GlobalDiscovery
from scripts.report_generator import GrowthReportGenerator
from scripts.safety_guardrails import ConsensusEngine
from scripts.invoice_manager import InvoiceManager
from scripts.fulfillment_engine import FulfillmentEngine

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("system_stress_test.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ContinuousOperationTest")

def run_stress_test(iterations=5):
    """
    システムの全機能を統合し、連続稼働をシミュレーションする。
    1. 市場探索 (Market Explorer)
    2. リード発掘 (Global Discovery)
    3. ガードレール/合議 (Consensus Engine)
    4. 成果物生成/実務代行 (Fulfillment / Report)
    5. 請求管理 (Invoice Manager)
    """
    explorer = BlueOceanExplorer()
    discovery = GlobalDiscovery()
    consensus_engine = ConsensusEngine()
    reporter = GrowthReportGenerator()
    fulfillment = FulfillmentEngine()
    invoice_manager = InvoiceManager()

    logger.info("=== STARTING 24H CONTINUOUS OPERATION SIMULATION ===")
    
    for i in range(iterations):
        logger.info(f"--- Cycle {i+1} Start ---")
        
        try:
            # Step 1: Market Explorer
            analysis = explorer.explore_new_opportunities()
            explorer.generate_proposal_report(analysis)
            logger.info(f"Step 1: Found new market opportunity: {analysis['sector_key']}")

            # Step 2: Global Lead Discovery
            sector = analysis['sector_key']
            leads = discovery.discover_new_leads("MajorCity", sector)
            target_lead = leads[0]
            logger.info(f"Step 2: Discovered lead: {target_lead['username']}")

            # Step 3: Safety Guardrails & Consensus
            action_desc = f"Fulfillment for {target_lead['username']} in {sector}"
            consensus_data = consensus_engine.get_consensus(action_desc)
            logger.info(f"Step 3: Consensus achieved: {consensus_data['summary']}")

            if consensus_data['summary'] == "SAFE":
                # Step 4: Fulfillment & Reporting
                # シミュレーション用に一部データを固定
                report_target = {
                    "username": target_lead['username'],
                    "sector": sector,
                    "issue": target_lead['issue'],
                    "lang": "ja"
                }
                # Report生成（レートリミット考慮のため、実際には失敗しても継続）
                try:
                    report_content = reporter.generate_report(report_target)
                    logger.info("Step 4a: Growth Report generated.")
                except Exception as e:
                    logger.warning(f"Step 4a: Report generation failed (simulated): {e}")

                # 実務代行（マニフェスト生成等）
                fulfillment_results = fulfillment.execute_auto_fulfillment(target_lead['username'], sector)
                logger.info(f"Step 4b: Auto-fulfillment executed: {len(fulfillment_results)} tasks.")

                # Step 5: Invoicing
                inv_data = invoice_manager.create_official_invoice(target_lead['username'], 150000)
                invoice_manager.notify_invoice_ready(inv_data)
                logger.info(f"Step 5: Invoice issued and queued: {inv_data['invoice_id']}")

            logger.info(f"--- Cycle {i+1} Success ---")
            
        except Exception as e:
            logger.error(f"Error in Cycle {i+1}: {e}")
            
        # サイクル間のインターバル
        time.sleep(1) 

    logger.info("=== CONTINUOUS OPERATION SIMULATION COMPLETED ===")

if __name__ == "__main__":
    run_stress_test()
