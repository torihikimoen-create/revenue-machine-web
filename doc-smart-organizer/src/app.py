import logging
import json
import os
from extractor import DocExtractor
from summarizer import DocSummarizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocOrganizerApp:
    def __init__(self):
        self.extractor = DocExtractor()
        self.summarizer = DocSummarizer()

    def process_folder(self, input_data):
        """
        フォルダ内の全ドキュメントを処理する。
        """
        logger.info("Starting High-Value Document Research & Organization...")
        
        results = []
        for doc in input_data:
            logger.info(f"Analyzing document: {doc['name']}...")
            
            # 1. メタデータ抽出
            metadata = self.extractor.extract_metadata(doc['content'])
            
            # 2. 要約作成
            summary = self.summarizer.summarize(doc['content'], metadata)
            
            # 3. 重要度判定
            priority = self.summarizer.determine_importance(doc['content'], metadata)
            
            result = {
                "file_name": doc['name'],
                "priority": priority,
                "metadata": metadata,
                "summary": summary
            }
            results.append(result)
            
            logger.info(f"[{priority}] Analysis complete for {doc['name']}")

        # 結果の保存（5万円の価値がある納品物）
        output_path = "../output/research_report.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Research report generated at {output_path}")

if __name__ == "__main__":
    # テスト用の模擬書類データ
    mock_documents = [
        {
            "name": "202603_業務委託契約書.pdf",
            "content": "株式会社アルファと山田太郎は、以下の通り業務委託契約を締結する。日付：2026年3月10日。金額は月額500,000円とする。"
        },
        {
            "name": "サーバー保守費用請求書.png",
            "content": "請求書。株式会社ベータ様へ。サーバー保守代金として ￥1,200,000 を請求いたします。至急お支払いください。2026/03/12"
        },
        {
            "name": "定例ミーティング議事録.txt",
            "content": "2026/03/13の定例会議の記録です。特に大きな決定事項はありません。"
        }
    ]
    
    app = DocOrganizerApp()
    app.process_folder(mock_documents)
