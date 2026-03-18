import logging

class DMClassifier:
    """
    メッセージ内容を分析し、重要度（Priority）を判定するAIエンジン。
    FXのトレンド判定と同様に、文脈とキーワードから真偽を見抜きます。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def classify(self, message_text: str):
        """
        LLM（モック解析）を用いてメッセージを分類する。
        """
        # 判断基準の定義
        urgent_keywords = ["予約", "納期", "至急", "トラブル", "返金"]
        spam_keywords = ["投資案件", "稼げる", "URLをクリック", "仮想通貨"]
        
        priority = "Medium"
        label = "General"
        
        # ロジックの適用（将来的にLLMへリプレイス）
        if any(kw in message_text for kw in urgent_keywords):
            priority = "High"
            label = "Business Inquiry"
        elif any(kw in message_text for kw in spam_keywords):
            priority = "Low"
            label = "Spam / Sales"
        elif "採用" in message_text or "ご連絡失礼" in message_text:
            priority = "Medium"
            label = "Partnership"
            
        return {
            "priority": priority,
            "label": label,
            "suggested_action": "Reply Immediately" if priority == "High" else "Archive" if priority == "Low" else "Later"
        }
