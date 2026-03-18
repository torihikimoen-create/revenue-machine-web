import os
import json
import logging
import random
from datetime import datetime

# モック用のディレクトリデータ（実際にはWebスクレイピングやAPIを使用）
MOCK_DIRECTORIES = {
    "WasteManagement": [
        {"name": "エコ・サイクル株式会社", "address": "東京都江東区...", "contact": "03-xxxx-xxxx", "url": "http://eco-cycle-example.jp"},
        {"name": "クリーン・フューチャー", "address": "大阪府堺市...", "contact": "06-xxxx-xxxx", "url": "http://clean-future-example.com"},
    ],
    "CareFacilities": [
        {"name": "さくら介護センター", "address": "神奈川県横浜市...", "contact": "045-xxxx-xxxx", "url": "http://sakura-care-example.org"},
        {"name": "ひまわり高齢者住宅", "address": "愛知県名古屋市...", "contact": "052-xxxx-xxxx", "url": "http://himawari-senior.example.net"},
    ]
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DirectoryScout")

class DirectoryScout:
    """
    各種業界ディレクトリを巡回し、法人情報を収集してリスト化するプロトタイプ。
    """
    def __init__(self):
        self.output_file = "directory_leads.json"

    def crawl_directory(self, sector):
        """
        特定のセクターのディレクトリを巡回（シミュレーション）。
        """
        logger.info(f"Crawling industry directory for {sector}...")
        
        # 実際にはここにBeautifulSoup等のスクレイピングロジックが入る
        results = MOCK_DIRECTORIES.get(sector, [])
        
        found_leads = []
        for entry in results:
            lead = {
                "timestamp": datetime.now().isoformat(),
                "company_name": entry["name"],
                "address": entry["address"],
                "contact": entry["contact"],
                "url": entry["url"],
                "sector": sector,
                "scout_method": "DirectoryScraping",
                "status": "NEW"
            }
            found_leads.append(lead)
            
        self.save_leads(found_leads)
        return found_leads

    def save_leads(self, leads):
        data = []
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        
        data.extend(leads)
        
        # 重複削除 (社名で簡易チェック)
        seen_names = set()
        unique_data = []
        for l in data:
            if l["company_name"] not in seen_names:
                seen_names.add(l["company_name"])
                unique_data.append(l)
        
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Total directory leads in {self.output_file}: {len(unique_data)}")

if __name__ == "__main__":
    scout = DirectoryScout()
    
    # 産業廃棄物と介護セクターを調査
    scout.crawl_directory("WasteManagement")
    scout.crawl_directory("CareFacilities")
    
    # 結果の表示
    if os.path.exists(scout.output_file):
        with open(scout.output_file, "r", encoding="utf-8") as f:
            all_leads = json.load(f)
            print(f"\n--- [COLLECTED DIRECTORY LEADS] ({len(all_leads)} entries) ---")
            for l in all_leads[:5]:  # 最初の5件を表示
                print(f"[{l['sector']}] {l['company_name']} | Contact: {l['contact']} | URL: {l['url']}")
