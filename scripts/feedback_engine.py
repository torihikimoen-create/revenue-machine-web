import os
import logging
from scripts.trial_tracker import get_active_subscriptions, get_trial_days_elapsed
from scripts.auto_sender import AutoSender
import scripts.user_analytics as analytics

logger = logging.getLogger("FeedbackEngine")
auto_sender = AutoSender()

def run_feedback_cycle():
    """
    試用期間中のユーザーに対して、3日・7日・10日目のヒアリングメールを自動送信する
    """
    if (os.getenv("DRY_RUN") or "true").lower() == "true":
        logger.info("Feedback Cycle skipped (DRY_RUN).")
        return
    logger.info("Starting Feedback Cycle (Mercury Retrograde Strategy)")
    subscriptions = get_active_subscriptions()
    
    for sub in subscriptions:
        customer = sub.customer
        email = customer.email
        days_elapsed = get_trial_days_elapsed(sub)
        user_id = email # シンプルにEmailをIDとして使用
        
        logger.info(f"Checking Feedback for {email} (Day {days_elapsed})")
        
        if days_elapsed == 3:
            send_day_3_feedback(user_id, email)
        elif days_elapsed == 7:
            send_day_7_feedback(user_id, email)
        elif days_elapsed == 10:
            send_day_10_feedback(user_id, email)

def send_day_3_feedback(user_id, email):
    # 共同開発者として立てるトーン
    subject = "【共同開発のお願い】AETHER COREの使い心地はいかがでしょうか？"
    body = f"""
{email} 様

AETHER COREをご利用いただき、ありがとうございます。
現在、サービス開始から3日が経過しましたが、最初の自動化設定はスムーズに完了しましたでしょうか？

実は現在、AIの挙動をより「実務」に最適化するためのテスト期間（水星逆行期間）として、
初期ユーザーの皆様を「共同開発者」としてお迎えし、フィードバックを頂いております。

もし、設定でつまづいている点や「ここがもっとこうなれば良いのに」という点がございましたら、
このメールに返信する形でお気軽にお知らせください。

あなたの声が、このAIを完成させます。
    """
    if auto_sender.send_custom_email(email, subject, body):
        analytics.log_event(user_id, "feedback_sent", {"day": 3})

def send_day_7_feedback(user_id, email):
    subject = "【深掘りヒアリング】AIに「任せきれなかった作業」はありますか？"
    body = f"""
{email} 様

試用開始から1週間が経ちました。AIの稼働状況はいかがでしょうか。

さらにサービスを磨き上げるため、ぜひ教えてください。
「この1週間で、AIに任せきれなかった（自分でやるしかなかった）作業」は何でしょうか？

また、もしこのAIがあなたの優秀な秘書なら、あと何をしてほしいですか？

より「不足（ブルーオーシャン）」を埋めるサービスへと進化させるため、
ぜひ率直なご意見をお聞かせください。
    """
    if auto_sender.send_custom_email(email, subject, body):
        analytics.log_event(user_id, "feedback_sent", {"day": 7})

def send_day_10_feedback(user_id, email):
    subject = "【最終日】今後の継続と、価格についてのご相談"
    body = f"""
{email} 様

本日で10日間の無料試用期間が終了となります。

最後にご相談です。
このサービスを今後プロ版（有料）として継続する場合、
適正な価格は月額いくら程度だとお考えでしょうか？

1. 11,000円（Basic: 月数回の自動化のみ）
2. 33,000円（Standard: 毎日フル稼働 ＋ 優先サポート）
3. 55,000円〜（Premium: カスタマイズ構築 ＋ 専属AI保守）

また、もし「継続しない」と判断された場合、最大の理由は何でしょうか？

頂いた内容は、今後の正式リリースの際の重要な指標とさせていただきます。
10日間、ありがとうございました。
    """
    if auto_sender.send_custom_email(email, subject, body):
        analytics.log_event(user_id, "feedback_sent", {"day": 10})

if __name__ == "__main__":
    run_feedback_cycle()
