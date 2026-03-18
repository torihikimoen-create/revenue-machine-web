import logging
import os

class CleanUpEngine:
    """
    実際にファイルを操作（リネーム・整理）するエンジン。
    FXの注文執行（Execution）と同様、失敗が許されない慎重さが求められます。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_plan(self, plan: list, dry_run: bool = True):
        """
        リネーム実行。dry_run=True の場合はログ出力のみ。
        """
        log_prefix = "[DRY RUN] " if dry_run else "[EXECUTE] "
        success_count = 0
        
        for item in plan:
            old_path = item['full_path']
            new_name = item['suggested_name']
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            self.logger.info(f"{log_prefix}Renaming: {os.path.basename(old_path)} -> {new_name}")
            
            if not dry_run:
                try:
                    os.rename(old_path, new_path)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to rename {old_path}: {e}")
        
        return success_count
