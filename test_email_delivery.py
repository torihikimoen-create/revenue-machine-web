import os
import sys
from dotenv import load_dotenv

# プロジェクトルートを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from scripts.auto_sender import AutoSender

def run_delivery_test():
    load_dotenv()
    
    # テスト送信を成功させるため、一時的に MOCK モードを解除（環境変数は上書きしない）
    sender = AutoSender()
    sender.is_mock = False 
    
    test_target = {
        "username": "増本 (Test)",
        "email": os.getenv("FROM_EMAIL"), # 自分宛
        "sector": "Nursing",
        "lang": "ja"
    }
    
    test_content = """
【重要・テスト送信】AETHER CORE 運用状況確認
増本様

本メールは、AIエージェントによる自動送信到達性テストです。
このメールが届いている場合、SMTPサーバーの設定およびネットワークの疎通は正常です。

本日早朝に行われた165件の送信において、決済リンクがダミーになっていた不備について、
現在AIの叡智を結集して原因究明とリカバリ案の策定を行っております。

ご確認のほど、よろしくお願いいたします。
---
AETHER CORE 実行エンジン
"""
    
    print(f"Sending test email to: {test_target['email']}...")
    success = sender.send_proposal_email(test_target, test_content, is_humanized=True)
    
    if success:
        print("Test email sent SUCCESSFULLY.")
    else:
        print("FAILED to send test email. Check SMTP logs and .env settings.")

if __name__ == "__main__":
    run_delivery_test()
