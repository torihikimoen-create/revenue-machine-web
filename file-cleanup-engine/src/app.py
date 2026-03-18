import logging
import os
from analyzer import FileAnalyzer
from engine import CleanUpEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileCleanupApp:
    def __init__(self):
        self.analyzer = FileAnalyzer()
        self.engine = CleanUpEngine()

    def run_cleanup_project(self, target_dir: str):
        """プロジェクトごとのデータ整理タスクを実行する。"""
        logger.info(f"Starting Data Organization Project for: {target_dir}")
        
        # 1. スキャン
        files = self.analyzer.get_file_list(target_dir)
        logger.info(f"Detected {len(files)} files.")

        # 2. 命名プランの作成 (規律あるルールの適用)
        rule_config = {"prefix": "2026_PRJ_A"}
        plan = []
        for f in files:
            suggested_name = self.analyzer.suggest_new_name(f, rule_config)
            plan.append({**f, "suggested_name": suggested_name})

        # 3. Dry-Run（プロの事前確認）
        self.engine.execute_plan(plan, dry_run=True)
        
        logger.info("Project planning complete. Ready for Execution phase.")

if __name__ == "__main__":
    # テスト用のダミーファイル作成
    test_dir = "../test_files"
    os.makedirs(test_dir, exist_ok=True)
    open(os.path.join(test_dir, "見積書 修正(1).pdf"), 'w').close()
    open(os.path.join(test_dir, "名称未設定 3.xlsx"), 'w').close()
    open(os.path.join(test_dir, "重要な資料.txt"), 'w').close()
    
    app = FileCleanupApp()
    app.run_cleanup_project(test_dir)
