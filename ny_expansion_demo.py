import json
import logging
from sales_sniper_bot.src.generator import ProposalGenerator

logging.basicConfig(level=logging.INFO)

def run_ny_demo():
    print("======================================================")
    print("🚀 Global Expansion Demo: New York Dental Market")
    print("======================================================")
    
    # Load NY Leads
    try:
        with open('ny_dental_leads.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("Error: ny_dental_leads.json not found.")
        return

    generator = ProposalGenerator()
    
    for lead in leads:
        print(f"\n🎯 Target: {lead['name']}")
        print(f"📍 Location: New York, USA")
        print(f"⚠️ Issue: {lead['issue']}")
        
        # Generate English Proposal
        print("\n--- Generating English Proposal ---")
        proposal = generator.generate(lead)
        print(proposal)
        
        print("\n✅ Simulation: Proposal sent via contact form.")
        print("-" * 50)

if __name__ == "__main__":
    run_ny_demo()
