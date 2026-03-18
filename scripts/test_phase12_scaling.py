import logging
import json
from scripts.global_discovery import GlobalDiscovery
from scripts.report_generator import GrowthReportGenerator
from scripts.invoice_manager import InvoiceManager

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Phase12Verifier")

def test_scaling_flow():
    logger.info("Starting Phase 12 Scaling & Crisis-Driven Flow Verification...")
    
    # 1. Deep Research for High-Value Leads
    discovery = GlobalDiscovery()
    target = discovery.mock_leads[0]
    target['personalized_pain'] = discovery.researcher.verify_client_pain(target['name'], target['sector'])
    logger.info(f"Verified target with Deep Research: {target['name']} -> {target['personalized_pain']}")
    
    # 2. Generate Crisis-Driven Value Report
    reporter = GrowthReportGenerator()
    # Note: Target names should match report_generator's expected keys
    report_target = {
        "username": target['name'],
        "sector": target['sector'],
        "issue": target['issue'],
        "lang": target['lang']
    }
    report_content = reporter.generate_report(report_target)
    logger.info("Generated crisis-driven report (first 200 chars):")
    logger.info(report_content[:200] + "...")
    
    # 3. Create Official Invoice
    inv_manager = InvoiceManager()
    inv_data = inv_manager.create_official_invoice(target['name'], 500000) # High-end B2B price
    inv_manager.notify_invoice_ready(inv_data)
    logger.info(f"Completed Phase 12 flow for {target['name']}. Invoice queued: {inv_data['invoice_id']}")

if __name__ == "__main__":
    test_scaling_flow()
