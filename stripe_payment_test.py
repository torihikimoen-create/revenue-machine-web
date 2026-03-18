import stripe
import os
import logging
from dotenv import load_dotenv

# .envファイルからAPIキーを読み込み
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StripePaymentManager:
    """
    自動化システムの収益をStripe経由で集金するマネージャー。
    FXの利益確定注文（Take Profit）を現実世界で実行するエンジンです。
    """
    
    def create_test_payment(self, amount: int, currency: str = "jpy", description: str = ""):
        """
        テスト用の決済（PaymentIntent）を作成する。
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description=description,
                payment_method="pm_card_visa", # テスト用のVISAカード
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never",
                }
            )
            logger.info(f"Payment successful! ID: {intent.id}, Amount: {amount} {currency}")
            return intent
        except Exception as e:
            logger.error(f"Payment failed: {e}")
            return None

if __name__ == "__main__":
    manager = StripePaymentManager()
    
    # デモ: 4つのビジネスの収益をシミュレーション
    businesses = [
        {"name": "Google口コミ返信 (Phase 1)", "amount": 30000},
        {"name": "SNS未返信DM整理 (Phase 2)", "amount": 50000},
        {"name": "書類リサーチ・事前整理 (Phase 3)", "amount": 50000},
        {"name": "データ整理・命名ルール統一 (Phase 4)", "amount": 150000},
    ]
    
    logger.info("--- Starting Automated Profit Collection Test ---")
    for biz in businesses:
        logger.info(f"Collecting payment for: {biz['name']}...")
        manager.create_test_payment(
            amount=biz['amount'],
            description=f"Automated service fee for {biz['name']}"
        )
    logger.info("--- All test payments processed ---")
