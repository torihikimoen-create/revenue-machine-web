import os
import shutil
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataOrganizer:
    """
    ユーザーの「戦利品」フォルダをプロの基準で整理するエンジン。
    """
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.output_dir = os.path.join(os.path.dirname(source_dir), "整理済み_戦利品")
        
        # カテゴリ定義
        self.categories = {
            "01_EAs_and_Source": [".ex5", ".mq5", ".mq4", ".ex4"],
            "02_Indicators_and_Tools": ["Indicators", ".zip"], # zipはツール類と仮定
            "03_Backtest_Reports": [".htm", ".html", ".gif", ".csv"],
            "04_Documents_and_Notes": [".docx", ".pdf", ".md", ".txt"],
            "05_Media_and_Design": [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mp3"],
            "06_Executables_and_Installers": [".exe", ".vsix"],
            "07_Archives": [".rar", ".zip"]
        }

    def analyze_and_plan(self):
        """現在のファイルを分析し、移動先を決定する。"""
        plan = []
        files = os.listdir(self.source_dir)
        
        for filename in files:
            filepath = os.path.join(self.source_dir, filename)
            if os.path.isdir(filepath):
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            target_folder = "99_Others" # デフォルト
            
            # カテゴリ判定
            for folder, extensions in self.categories.items():
                if ext in extensions:
                    target_folder = folder
                    break
            
            # 特殊なキーワードによる判定
            if "Angle_Harmony" in filename:
                target_folder = "01_EAs_and_Source"
            elif "ReportTester" in filename or "StrategyTester" in filename:
                target_folder = "03_Backtest_Reports"

            plan.append({
                "original": filename,
                "target_folder": target_folder
            })
        return plan

    def execute(self, dry_run=True):
        """整理を実演する。"""
        plan = self.analyze_and_plan()
        logger.info(f"--- {'DRY RUN' if dry_run else 'EXECUTION'} START ---")
        
        if not dry_run:
            os.makedirs(self.output_dir, exist_ok=True)
            for folder in self.categories.keys():
                os.makedirs(os.path.join(self.output_dir, folder), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, "99_Others"), exist_ok=True)

        for item in plan:
            src = os.path.join(self.source_dir, item['original'])
            dst = os.path.join(self.output_dir, item['target_folder'], item['original'])
            
            if dry_run:
                logger.info(f"[PLAN] {item['original']} -> {item['target_folder']}/")
            else:
                shutil.copy2(src, dst) # 安全のためコピーから開始
        
        logger.info(f"--- {'DRY RUN' if dry_run else 'EXECUTION'} COMPLETE ---")
        return plan

if __name__ == "__main__":
    # 文字化け回避のため、カレントディレクトリのサブフォルダとして指定
    target = os.path.join(os.getcwd(), "戦利品") 
    organizer = RealDataOrganizer(target)
    organizer.execute(dry_run=False)
