import os
import sys
import json
import logging
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 必要なディレクトリをパスに追加
sys.path.append(os.path.join(current_dir, 'b2b-deal-finder', 'src'))
sys.path.append(current_dir)

from builder import BusinessProposalBuilder
from scripts.safety_guardrails import ConsensusEngine
from scripts.corrector import AIProposalCorrector
from scripts.auto_sender import AutoSender
from scripts.humanizer import HumanizerEngine

load_dotenv(os.path.join(current_dir, ".env"))
logging.basicConfig(level=logging.ERROR) # ログは最小限に

def preview_proposals():
    # DRY_RUNを一時的に無効化して実際に生成
    os.environ["DRY_RUN"] = "false"
    
    builder = BusinessProposalBuilder()
    consensus_engine = ConsensusEngine()
    corrector = AIProposalCorrector()
    humanizer = HumanizerEngine()
    sender = AutoSender()
    
    # システム内の実際のターゲットリストから上位3件を取得（またはシミュレート）
    # ここでは global_leads.json の実データを反映
    test_deals = [
        {
            "username": "青山筋膜整体理学BODY 表参道店",
            "sector": "Osteopathy",
            "title": "複数店舗向けAI自動返信・予約管理パッケージ",
            "awareness_level": "low",
            "budget": "月額33,000円",
            "city": "Tokyo",
            "lang": "ja"
        },
        {
            "username": "Target_Nursing_兵庫_0247",
            "sector": "Nursing",
            "title": "2026年報酬改定対応・介護事務AIアシスタント",
            "awareness_level": "low",
            "budget": "月額11,000円",
            "city": "兵庫",
            "lang": "ja"
        },
        {
            "username": "Target_Construction_広島_0247",
            "sector": "Construction",
            "title": "2024年問題克服・工期適正化支援AIシステム",
            "awareness_level": "high",
            "budget": "月額55,000円",
            "city": "広島",
            "lang": "ja"
        }
    ]
    
    print("=== AETHER CORE Actual Email Preview (Final Form) ===\n")
    
    results = []
    for deal in test_deals:
        # 1. 生成
        proposal_obj = builder.build_proposal(deal, payment_link="https://buy.stripe.com/test_sample_link")
        
        # JSONから本文を取り出し（あるいは文字列の場合に対応）
        subject = proposal_obj.get("subject", f"【ご提案】{deal['username']}様への業務効率化案")
        content = proposal_obj.get("content", proposal_obj)

        # 2. 検閲
        review = consensus_engine.get_consensus(content)
        
        if review["summary"] == "REJECTED":
            content = corrector.correct_proposal(content, review)
            
        # 3. 人間味の付加（Humanize）を追加
        print(f"--- Humanizing content for {deal['username']} ---")
        content, _ = humanizer.polish(content, sector=deal['sector'], current_date="2026-03-18")
            
        # 4. AutoSender のテンプレートに流し込む（フッター等が付加される）
        full_body = sender._prepare_body_with_footer(content)
        
        results.append({
            "target": deal['username'],
            "sector": deal['sector'],
            "subject": subject,
            "body": full_body
        })

    with open(os.path.join(current_dir, "tmp/final_email_previews.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    preview_proposals()
