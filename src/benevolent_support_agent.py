import os
import json
import logging
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# プロジェクトルートのscriptsをインポートできるように設定
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scripts.stripe_link_gen import create_service_payment_link
from scripts.trial_tracker import has_active_subscription

class BenevolentSupportAgent:
    """
    現場担当者の「困りごと」をAIで解決し、心理的・時間的余裕を創出する支援エージェント。
    """
    def __init__(self, sector="Sanpai"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.sector = sector

    def diagnose_and_assist(self, user_problem):
        """
        悩みを聞き、その場で具体的な解決（ドラフト、解説）を行う。
        """
        prompt = f"""
You are a Benevolent AI Support Agent specializing in the {self.sector} industry.
Your mission is to GENUINELY HELP a stressed field worker.

User's Stress Point:
{user_problem}

Instructions:
1. Be empathetic and professional. Use a "Gentle & Supportive" tone.
2. Provide a concrete solution immediately (e.g., a draft for a report, a simplified explanation of a law, or a step-by-step checklist).
3. Do NOT focus on sales. Focus on "Removing the Burden".
4. If applicable, mention that AETHER CORE will be there to automate this for them regularly.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": f"You are the Helping Hand for {self.sector} workers."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in diagnose_and_assist: {e}")
            return "お手伝いしようとしたのですが、少し接続がうまくいきませんでした。すぐに改善いたしますので、少々お待ちくださいね。"

    def issue_support_ticket(self, user_context, user_email=None, amount=2980):
        """
        特定の支援内容に対する、1回限りの「お助けチケット」を発行する。
        """
        service_name = f"Support Ticket for {user_context[:20]}..."
        try:
            # すでにサブスクリプション契約があるユーザーには、二重課金防止のためチケットを出さない
            if user_email and has_active_subscription(user_email):
                logger.info(
                    f"Skipping one-off support ticket for {user_email} (active subscription detected)."
                )
                return (
                    "すでに継続サポートプランをご利用いただいているため、"
                    "追加の単発チケットは不要と判断しました。現在のプラン内で最大限サポートいたします。"
                )

            # 単発決済（recurring=False）として発行し、「どの文脈か」をメタデータに記録
            ticket_url = create_service_payment_link(
                service_name,
                setup_fee_jpy=amount,
                metadata={
                    "type": "support_ticket",
                    "sector": self.sector,
                    "context": user_context[:100],
                },
            )
            
            message = f"""
---
[AETHER CORE 支援チケット]
もし、今回の事務作業や手続きをすべて私にお任せいただけるなら、こちらのチケットをご利用ください。
あなたの貴重な時間を本業のために取り戻すお手伝いをいたします。

チケットURL: {ticket_url}
内容: {self.sector} に関する事務代行（1回分）
"""
            return message
        except Exception as e:
            logger.error(f"Error in issue_support_ticket: {e}")
            return ""

    def propose_subscription(self, user_email, sector_price=24800):
        """
        チケット利用が習慣化したユーザーに対し、定額制（サブスク）への移行を提案する。
        """
        try:
            # サブスクリプション決済リンク（recurring=True）
            sub_link = create_service_payment_link(
                f"AI Business Support Pack ({self.sector})",
                monthly_fee_jpy=sector_price,
                trial_days=7,
                customer_email=user_email,
                metadata={
                    "type": "subscription",
                    "sector": self.sector,
                },
            )
            
            message = f"""
---
[AETHER CORE プレミアム支援のご案内]
いつもご利用いただきありがとうございます。
あなたの業務ログを分析したところ、定期的な代行により、これまでに合計数時間分の「自由な時間」が創出されています。

毎回チケットを購入する手間を省き、24時間体制であなたをフルサポートする「プレミアム支援パック」への移行をご検討されませんか？
今なら7日間の無料期間が付いています。

移行用リンク: {sub_link}
月額料金: {sector_price:,}円（税込）
特典: 優先サポート、全事務作業の自動代行、法改正の先行通知
"""
            return message
        except Exception as e:
            logger.error(f"Error in propose_subscription: {e}")
            return ""
if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 産廃業界の担当者が「法改正の事務手続き」に絶望しているケース
    user_trouble = """
    2026年の法改正でマニフェストの管理が電子化されると聞きました。
    うちはまだ紙でやっていて、職員も高齢なので何から手をつけていいか分からず、毎日不安です。
    """
    
    agent = BenevolentSupportAgent(sector="産業廃棄物管理 (Sanpai)")
    
    print(f"--- [AETHER CORE Support: Helping a troubled worker in {agent.sector}] ---")
    support_message = agent.diagnose_and_assist(user_trouble)
    print("\n[AI Support Response]")
    print(support_message)
    
    # チケットの発行デモ
    print("\n--- [Issuing a Support Ticket as a Helping Hand] ---")
    ticket_message = agent.issue_support_ticket("Sanpai Electronic Manifest Setup", amount=3000)
    print(ticket_message)
