import os
import json
import logging
from datetime import datetime
try:
    from scripts.auto_sender import AutoSender
except ImportError:
    from auto_sender import AutoSender

class OnboardingManager:
    """
    契約成立（Stripe決済等）後のオンボーディングと実務セットアップを自動化する。
    """
    def __init__(self):
        self.logger = logging.getLogger("OnboardingManager")
        self.sender = AutoSender()
        self.clients_dir = 'clients'
        os.makedirs(self.clients_dir, exist_ok=True)

    def process_new_contract(self, stripe_event):
        """
        Stripe Webhook等から契約情報を受け取り、初期セットアップを行う。
        """
        # 本来は stripe_event から抽出
        client_id = stripe_event.get('client_id', 'unknown_client')
        sector = stripe_event.get('sector', 'General')
        email = stripe_event.get('email')

        self.logger.info(f"New contract detected: {client_id} ({sector})")
        
        # 1. クライアント専用フォルダと設定の作成
        client_path = os.path.join(self.clients_dir, client_id)
        os.makedirs(client_path, exist_ok=True)
        
        config = {
            "client_id": client_id,
            "sector": sector,
            "email": email,
            "contract_date": datetime.now().isoformat(),
            "status": "onboarding",
            "access_granted": False
        }
        
        with open(os.path.join(client_path, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        # 2. 初期セットアップ（アクセス権リクエスト）メールの送信
        self.send_onboarding_welcome(client_id, sector, email)
        
        return client_path

    def send_onboarding_welcome(self, client_id, sector, email):
        """
        クライアントに対し、実務開始のためのアクセス権付与を依頼する。
        """
        prompt_context = {
            "LocalGov": "アナログ資料の共有用Google Driveフォルダへのアクセス権",
            "ProfService": "チェック対象の契約書・提案テンプレートの共有",
            "Medical": "日報データ出力用アカウントの連携",
            "General": "実務に必要な各種アカウントへのアクセス権"
        }
        
        request_item = prompt_context.get(sector, prompt_context["General"])
        
        subject = f"【重要】{client_id}様：自動化実務開始のためのセットアップご案内"
        content = f"""
{client_id} 様

この度は「全自動ビジネス帝国」のAI自動化パッケージをご契約いただき、誠にありがとうございます。
これより、貴社の業務をAIが丸投げで代行する環境を構築いたします。

実務を開始するために、以下の手順で{request_item}をお願いいたします。

1. 以下の専用フォルダに資料をアップロードしてください。
   [共有フォルダ：https://example.com/drive/{client_id}]

2. 完了後、このメールにご返信いただくか、管理パネルの「準備完了」ボタンを押してください。

AIがデータを検知次第、即座に実務（分析・生成・整理）を開始いたします。
ご不明な点がございましたら、いつでもお気軽にお問い合わせください。

---
AETHER CORE Fulfillment Engine
"""
        # テスト送信
        target = {"username": client_id, "email": email}
        self.sender.send_proposal_email(target, content) # メソッド名が汎用的だがこれを使用
        self.logger.info(f"Onboarding email sent to {email}")

if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    manager = OnboardingManager()
    test_event = {
        "client_id": "TEST_Niche_Client",
        "sector": "LocalGov",
        "email": "owner@example.gov.jp"
    }
    manager.process_new_contract(test_event)
