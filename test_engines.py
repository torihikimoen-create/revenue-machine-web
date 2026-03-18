import os
import json
import sys
import logging
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 各エンジンのソースディレクトリをパスに追加
sys.path.append(os.path.join(current_dir, 'sns-sales-hunter', 'src'))
sys.path.append(os.path.join(current_dir, 'b2b-deal-finder', 'src'))

# 修正後のインポート（プロジェクト構造に依存しない形）
try:
    from hunter import SNSHunter
    from generator import DMDraftGenerator
    from finder import B2BDealFinder
    from builder import BusinessProposalBuilder
    from scripts.stripe_link_gen import create_service_payment_link
except ImportError as e:
    print(f"Import Error: {e}")
    # 代替インポート試行
    from sns_sales_hunter.src.hunter import SNSHunter
    from sns_sales_hunter.src.generator import DMDraftGenerator
    from b2b_deal_finder.src.finder import B2BDealFinder
    from b2b_deal_finder.src.builder import BusinessProposalBuilder
    from scripts.stripe_link_gen import create_service_payment_link

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_engines():
    print("=== Testing Global AI Outreach Engines (Monetized) ===\n")
    
    hunter = SNSHunter()
    generator = DMDraftGenerator()
    finder = B2BDealFinder()
    builder = BusinessProposalBuilder()

    # global_leads.json を読み込み
    with open(os.path.join(current_dir, 'global_leads.json'), 'r', encoding='utf-8') as f:
        global_leads = json.load(f)

    for city_data in global_leads:
        city = city_data['city']
        sector = city_data['sector']
        print(f"--- Processing City: {city} | Sector: {sector} ---")

        # 1. SNS Hunter Test
        targets = hunter.hunt_targets(city, city_data['targets'])
        for t in targets:
            print(f"\n[SNS] Target: {t['username']} (Lang: {t['lang']})")
            
            # 決済リンクの生成（テスト価格 10,000円）
            payment_link = create_service_payment_link(f"SNS AI Setup ({t['username']})", setup_fee_jpy=10000)
            
            dm = generator.create_dm(t, payment_link=payment_link)
            print(f"Draft DM (Monetized):\n{dm[:250]}...")
            
            # 下書き保存
            hunter.save_draft(t, dm)

        # 2. B2B Deal Finder Test
        if sector == "SME Law Firm":
            mock_deal = {
                "client": city_data['targets'][0]['name'],
                "title": "Automated Case File Organization & AI Summary",
                "budget": "250,000円",
                "urgency": "High",
                "source": "Direct Discovery"
            }
            print(f"\n[B2B] Generating Proposal for: {mock_deal['client']}")
            
            # 高額決済リンクの生成（手付金 50,000円）
            payment_link = create_service_payment_link(f"B2B AI Deposit ({mock_deal['client']})", setup_fee_jpy=50000)
            
            proposal = builder.build_proposal(mock_deal, payment_link=payment_link)
            print(f"Proposal Hint (Monetized): {proposal[:200]}...")
            
            # 提案書保存
            finder.save_proposal(mock_deal, proposal)

if __name__ == "__main__":
    # Windowsでのエンコーディング問題を回避
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    test_engines()
