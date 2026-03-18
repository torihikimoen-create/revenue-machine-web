import json
import sys

# Ensure the project root is in path
sys.path.append(".")
from sales_sniper_bot.src.generator import ProposalGenerator

def run_london_demo():
    print("======================================================")
    print("🚀 Global Expansion Demo: London Dental Market")
    print("======================================================")
    
    # Load London Leads
    try:
        with open('london_dental_leads.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("Error: london_dental_leads.json not found.")
        return

    generator = ProposalGenerator()
    
    for lead in leads:
        print(f"\n🎯 Target: {lead['name']}")
        print(f"📍 Location: London, UK")
        print(f"⚠️ Issue: {lead['issue']}")
        
        # Generate British English Proposal
        print("\n--- Generating British English Proposal ---")
        proposal = generator.generate(lead, region="London")
        print(proposal)
        
        print("\n✅ Simulation: Proposal sent targeting UK business hours.")
        print("-" * 50)

if __name__ == "__main__":
    run_london_demo()
