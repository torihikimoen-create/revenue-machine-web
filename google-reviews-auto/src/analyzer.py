import logging

class ReviewAnalyzer:
    """
    Google口コミの内容を分析し、感情や主要なトピックを抽出するモジュール。
    FXでのテクニカル指標の読み解きと同様に、微細なニュアンス（モメンタム）を捉えます。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, review_text: str, rating: int):
        """
        口コミテキストとスターレーティングから、返信のトーンを決定する。
        """
        # シンプルなルールベースと将来的なLLM連携のハイブリッド設計
        sentiment = "positive" if rating >= 4 else "neutral" if rating == 3 else "negative"
        
        # 特定のキーワード（「高い」「遅い」「美味しい」等）の抽出ロジック（将来的に拡張）
        topics = []
        if "味" in review_text or "おいしい" in review_text:
            topics.append("food_quality")
        if "接客" in review_text or "サービス" in review_text:
            topics.append("service")
            
        return {
            "sentiment": sentiment,
            "topics": topics,
            "original_rating": rating
        }
