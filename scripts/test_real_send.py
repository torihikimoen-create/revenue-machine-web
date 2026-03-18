import sys
import os

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from scripts.auto_sender import AutoSender
from dotenv import load_dotenv

def main():
    # .env を読み込む
    load_dotenv(os.path.join(project_root, ".env"))

    # このテストのみ、環境変数で DRY_RUN を明示的に無効化
    os.environ["DRY_RUN"] = "false"
    
    print("--- AETHER CORE: Real-Mode Email Test ---")
    print(f"Target: eliel8114@gmail.com")
    print(f"Mode: REAL (DRY_RUN=false)")
    print("-----------------------------------------")

    sender = AutoSender()
    
    # ターゲット情報の構築
    target = {
        "email": "eliel8114@gmail.com",
        "username": "増本テスト株式会社（実機テスト）",
        "sector": "nursing"
    }

    # テスト用の本文（AutoSender側で https://aether-core.example.com/trial が置換されるかを確認）
    content = """増本テスト株式会社
代表者様

いつも大変お世話になっております。
エーテルコア・ビジネス自動化推進部のAIアシスタントでございます。

貴社の介護現場における事務負担を、最新のAI技術によって「ゼロ」にするご提案をさせていただきます。
具体的には、手書きの記録や複雑なマニフェストをスマホで撮るだけで、自動的に集計・報告書化する仕組みです。

現在、10日間の無料トライアルを実施しております。
初期費用も0円で開始いただけますので、ぜひこの機会にご検討いただけますと幸いです。

詳細は以下のリンクよりご確認いただけます。
https://aether-core.example.com/trial

何卒よろしくお願い申し上げます。"""

    # 送信実行（is_humanized=True にしてガードレールを通過させる）
    success = sender.send_proposal_email(
        target=target,
        content=content,
        is_humanized=True
    )

    if success:
        print("\n✅ テストメールの送信に成功しました！")
        print("増本様の eliel8114@gmail.com で受信を確認してください。")
    else:
        print("\n❌ テストメールの送信に失敗しました。")
        print("logs/email_system.log またはコンソール出力を確認してください。")

if __name__ == "__main__":
    main()
