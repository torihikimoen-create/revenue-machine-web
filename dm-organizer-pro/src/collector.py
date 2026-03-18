import logging

class DMCollector:
    """
    複数SNS（Instagram, X, LinkedIn等）から未読DMを収集するモジュール。
    FXのティックデータ収集と同様、リアルタイム性が重要です。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def fetch_all(self):
        """
        API（モック）から全SNSの未読メッセージを取得する。
        """
        # 本来は各プラットフォームのAPIを個別に叩く
        mock_messages = [
            {
                "id": "msg_001",
                "platform": "Instagram",
                "sender": "tanaka_taro",
                "text": "来週の予約について相談したいのですが、空きはありますか？",
                "timestamp": "2026-03-13T19:00:00Z"
            },
            {
                "id": "msg_002",
                "platform": "X",
                "sender": "crypto_bot",
                "text": "【至急】最新の投資案件について詳しく教えます！URLをクリック...",
                "timestamp": "2026-03-13T19:30:00Z"
            },
            {
                "id": "msg_003",
                "platform": "LinkedIn",
                "sender": "hr_manager",
                "text": "突然のご連絡失礼いたします。弊社の採用プロジェクトについて...",
                "timestamp": "2026-03-13T18:45:00Z"
            }
        ]
        return mock_messages
