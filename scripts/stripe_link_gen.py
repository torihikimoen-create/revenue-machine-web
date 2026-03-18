import stripe
import os
import logging
from dotenv import load_dotenv
from scripts.trial_tracker import is_eligible_for_trial

load_dotenv()

# Stripe APIキーの設定
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_service_payment_link(service_name, setup_fee_jpy=0, monthly_fee_jpy=0, trial_days=0, customer_email=None, metadata=None):
    """
    導入費（一括）と月額課金（定期・トライアル付）を組み合わせた決済リンクを生成。
    """
    if (os.getenv("DRY_RUN") or "true").lower() == "true":
        logger.info(f"[MOCK] Skipping Stripe Link for {service_name}")
        return "https://buy.stripe.com/test_placeholder"

    # トライアル資格チェック
    actual_trial_days = trial_days
    if monthly_fee_jpy > 0 and trial_days > 0 and customer_email:
        if not is_eligible_for_trial(customer_email):
            actual_trial_days = 0

    try:
        line_items = []
        
        # 1. 導入費（初期費用）の作成
        if setup_fee_jpy > 0:
            setup_prod = stripe.Product.create(
                name=f"{service_name} (初期セットアップ費用)",
                description="システム導入・初期設定および2026年問題対応ロードマップ作成費用。"
            )
            setup_price = stripe.Price.create(
                product=setup_prod.id,
                unit_amount=setup_fee_jpy,
                currency="jpy"
            )
            line_items.append({"price": setup_price.id, "quantity": 1})

        # 2. 月額課金の作成
        if monthly_fee_jpy > 0:
            monthly_prod = stripe.Product.create(
                name=f"{service_name} (月額AI運用保守)",
                description=f"24時間365日のAI自動監査および実務執行代行費用。{actual_trial_days}日間の無料トライアル付。"
            )
            monthly_price = stripe.Price.create(
                product=monthly_prod.id,
                unit_amount=monthly_fee_jpy,
                currency="jpy",
                recurring={"interval": "month"}
            )
            line_items.append({"price": monthly_price.id, "quantity": 1})

        if not line_items:
            raise ValueError("Both setup_fee and monthly_fee are zero.")

        # 3. 決済リンクの作成
        link_data = {
            "line_items": line_items,
            "after_completion": {"type": "redirect", "redirect": {"url": "https://torihikimoen-create.github.io/revenue-machine-web/index.html"}},
            "payment_method_types": ["card"],
            "metadata": metadata
        }

        if monthly_fee_jpy > 0:
            link_data["payment_method_collection"] = "always"
            if actual_trial_days > 0:
                link_data["subscription_data"] = {"trial_period_days": actual_trial_days}

        payment_link = stripe.PaymentLink.create(**link_data)

        logger.info(f"Generated Combined Link for {service_name}: {payment_link.url}")
        return payment_link.url

    except Exception as e:
        logger.error(f"Error creating Combined Stripe Link: {e}")
        return "https://buy.stripe.com/test_placeholder"

if __name__ == "__main__":
    # テスト実行
    print("Testing Stripe Link Generation...")
    url = create_service_payment_link("AI Setup Fee (Tokyo Clinic)", 50000)
    print(f"Test URL: {url}")
