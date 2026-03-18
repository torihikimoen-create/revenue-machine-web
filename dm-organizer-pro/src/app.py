import logging
import json
from collector import DMCollector
from classifier import DMClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DMOrganizerApp:
    def __init__(self):
        self.collector = DMCollector()
        self.classifier = DMClassifier()

    def run(self):
        """
        DM整理のメインプロセスを実行する。
        """
        logger.info("Starting DM Organization process...")
        
        # 1. 収集
        messages = self.collector.fetch_all()
        logger.info(f"Collected {len(messages)} messages from all platforms.")
        
        # 2. 分類・整理
        organized_list = []
        for msg in messages:
            analysis = self.classifier.classify(msg['text'])
            item = {
                "source": msg['platform'],
                "from": msg['sender'],
                "content": msg['text'],
                "analysis": analysis
            }
            organized_list.append(item)
            
            # 3. ログ出力（通知の代わり）
            logger.info(f"[{analysis['priority']}] {msg['platform']} from {msg['sender']}: {analysis['label']}")
            if analysis['priority'] == "High":
                logger.warning(f"--- ACTION REQUIRED: {msg['text'][:30]}... ---")

        # 整理結果を保存
        with open("../organized_dm.json", "w", encoding="utf-8") as f:
            json.dump(organized_list, f, ensure_ascii=False, indent=2)
        
        logger.info("DM Organization complete. Results saved to organized_dm.json")

if __name__ == "__main__":
    app = DMOrganizerApp()
    app.run()
