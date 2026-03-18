import sys
import os
import json
import logging
from dotenv import load_dotenv

# プロジェクトルートを追加
sys.path.append(os.getcwd())

from b2b_deal_finder.src.builder import BusinessProposalBuilder
from b2b_deal_finder.src.finder import B2BDealFinder

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_proposal_generation():
    # DRY_RUNを一時的に解除して実際にAIに生成させる
    os.environ["DRY_RUN"] = "false"
    
    builder = BusinessProposalBuilder()
    finder = B2BDealFinder()
    
    test_deal = {
        "username": "テスト建設工事株式会社",
        "client": "テスト建設工事株式会社",
        "sector": "Construction",
        "title": "安全書類および見積管理の自動化",
        "awareness_level": "low"
    }
    
    payment_link = "https://buy.stripe.com/test_real_link"
    
    print("\n--- Generating AI Proposal with NEW PROMPTS ---")
    proposal_data = builder.build_proposal(test_deal, payment_link)
    
    print(f"\n[SUBJECT]: {proposal_data.get('subject')}")
    print("\n[CONTENT PREVIEW (First 500 chars)]:")
    print(proposal_data.get('content')[:500] + "...")
    
    # 保存のテスト
    filepath = finder.save_proposal(test_deal, proposal_data)
    print(f"\nSaved to: {filepath}")

    # DRY_RUNを戻す
    os.environ["DRY_RUN"] = "true"

if __name__ == "__main__":
    test_proposal_generation()
