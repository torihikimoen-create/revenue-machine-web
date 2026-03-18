import openai
import os

class ReplyGenerator:
    """
    分析結果に基づき、LLMを使用してパーソナライズされた返信文を生成するモジュール。
    FXでの「利確後の称賛」のような、温かみと説得力のある文章を目指します。
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def generate(self, review_data: dict, shop_config: dict):
        """
        店舗設定と口コミ分析結果を元に返信を生成する。
        """
        # プロンプトの構築（FXでの戦略と同様に、文脈と規律を重視）
        prompt = f"""
        あなたは店舗のオーナーです。以下の口コミに対して、丁寧で心のこもった返信を書いてください。
        
        【店舗情報】
        店名: {shop_config.get('name')}
        トーン: {shop_config.get('tone', '丁寧')}
        
        【口コミ情報】
        評価: {review_data['original_rating']}星
        感情: {review_data['sentiment']}
        言及されたトピック: {', '.join(review_data['topics'])}
        
        【制約事項】
        - 150字以内で簡潔に。
        - 感謝の気持ちを必ず伝える。
        - 改善が必要な場合は前向きな姿勢を示す。
        """
        
        # 実際にはここに OpenAI API の呼び出しが入る
        # 現時点ではモックの返信を返す（APIキー設定済みなら実行可能に拡張予定）
        return f"（モック返信）{shop_config.get('name')}をご利用いただきありがとうございます！{review_data['sentiment']}な評価、大変励みになります。"
