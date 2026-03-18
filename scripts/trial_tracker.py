import stripe
import os
import logging
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
logger = logging.getLogger(__name__)

def has_active_subscription(customer_email):
    """
    指定されたメールアドレスのユーザーが、現在有効なサブスクリプションを持っているか確認する。
    """
    if not customer_email:
        return False
        
    try:
        # 顧客を検索
        customers = stripe.Customer.list(email=customer_email, limit=1).data
        if not customers:
            return False
            
        customer_id = customers[0].id
        # サブスクリプションをリストアップ
        subs = stripe.Subscription.list(customer=customer_id, status="active", limit=1).data
        return len(subs) > 0
    except Exception as e:
        logger.error(f"Error checking active subscription for {customer_email}: {e}")
        return False

def is_eligible_for_trial(customer_email):
    """
    指定されたメールアドレスのユーザーが、無料トライアルを利用可能（過去に利用していない）か確認する。
    """
    if not customer_email:
        return True # メールアドレス不明の場合は安全側に倒す（が、基本は渡す運用）
        
    try:
        customers = stripe.Customer.list(email=customer_email, limit=1).data
        if not customers:
            return True # 新規顧客なら利用可能
            
        customer_id = customers[0].id
        # 過去の全サブスクリプションをチェック（キャンセル済み含む）
        subs = stripe.Subscription.list(customer=customer_id, status="all").data
        for sub in subs:
            # trial_start が存在する、または過去にあった場合は利用不可とみなす
            if sub.trial_start is not None:
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking trial eligibility for {customer_email}: {e}")
        return False # 不明な場合はリスク回避のため利用不可とするか、要件に合わせて調整

def get_active_subscriptions():
    """
    Stripe上のすべてのアクティブなサブスクリプションを取得する。
    """
    try:
        return stripe.Subscription.list(status="active", expand=["data.customer"]).data
    except Exception as e:
        logger.error(f"Error fetching active subscriptions: {e}")
        return []

def get_trial_days_elapsed(subscription):
    """
    トライアル開始日からの経過日数を計算する。
    """
    if not subscription.trial_start:
        return 0
    
    from datetime import datetime
    start_date = datetime.fromtimestamp(subscription.trial_start)
    delta = datetime.now() - start_date
    return delta.days

def get_active_trial_count():
    """
    Stripe上のアクティブなトライアル件数を取得する。
    """
    return len(get_active_subscriptions())
