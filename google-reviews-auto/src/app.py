import yaml
import logging
from analyzer import ReviewAnalyzer
from generator import ReplyGenerator

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoReplyApp:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.analyzer = ReviewAnalyzer()
        self.generator = ReplyGenerator()

    def _load_config(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def process_new_reviews(self, mock_reviews):
        """
        新着口コミを処理するメインループ。
        FXでのエントリー判断と同様、規律に従って自動または手動判定を行います。
        """
        for shop in self.config['shops']:
            logger.info(f"Checking reviews for: {shop['name']}...")
            
            # 本来はここで Google API を叩いて新着を取得する
            # 今回は引数の mock_reviews を使用
            for review in mock_reviews.get(shop['id'], []):
                logger.info(f"Processing review: {review['text'][:20]}...")
                
                # 1. 分析
                analysis = self.analyzer.analyze(review['text'], review['rating'])
                
                # 2. 返信案作成
                reply_text = self.generator.generate(analysis, shop)
                
                # 3. 投稿判定 (規律の適用)
                if shop['auto_approve'] and review['rating'] >= 4:
                    logger.info(f"Auto-approving reply for {shop['name']}")
                    self._post_reply(shop['id'], review['id'], reply_text)
                else:
                    logger.info(f"Manual approval required for {shop['name']}. Draft: {reply_text}")

    def _post_reply(self, shop_id, review_id, reply_text):
        """
        Google API を通じて実際に返信するモック
        """
        logger.info(f"Successfully posted reply to {review_id}: {reply_text}")

if __name__ == "__main__":
    # テスト用の模擬データ
    mock_data = {
        "shop_001": [
            {"id": "rev_101", "rating": 5, "text": "とても美味しかったです！接客も最高でした。"},
            {"id": "rev_102", "rating": 2, "text": "料理が来るのが遅すぎました。"}
        ]
    }
    
    app = AutoReplyApp("../config/settings.yaml")
    app.process_new_reviews(mock_data)
