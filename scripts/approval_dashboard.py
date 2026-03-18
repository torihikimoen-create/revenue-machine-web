import os
import json
import logging
from datetime import datetime
from scripts.safety_guardrails import ConsensusEngine, auto_backup

logger = logging.getLogger("ApprovalDashboard")

class ApprovalQueue:
    """
    オーナーの承認を待つアクションを管理するキューシステム。
    """
    def __init__(self):
        self.queue_file = "approval_queue.json"
        self._load_queue()

    def _load_queue(self):
        if os.path.exists(self.queue_file):
            with open(self.queue_file, "r", encoding="utf-8") as f:
                self.queue = json.load(f)
        else:
            self.queue = []

    def add_task(self, client_id, sector, action_type, content, metadata=None):
        """
        AIが実行したいアクションを承認待ちとして追加。
        metadata にはメールアドレス等の実行に必要な情報を含める。
        """
        engine = ConsensusEngine()
        consensus = engine.get_consensus(f"{action_type}: {content}")
        
        # AIの合議結果に基づく初期ステータスの設定
        task_id = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{client_id[:5]}"
        status = "PENDING"
        if consensus.get("summary") == "CAUTION":
            status = "REVIEW_REQUIRED"

        task = {
            "task_id": task_id,
            "client_id": client_id,
            "sector": sector,
            "action_type": action_type,
            "content": content,
            "metadata": metadata or {},
            "consensus": consensus,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "executed_at": None
        }
        self.queue.append(task)
        self._save_queue()
        logger.info(f"New pending task added to Dashboard: {task['task_id']}")

    @auto_backup('approval_queue.json')
    def _save_queue(self):
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=4, ensure_ascii=False)

    def approve_task(self, task_id):
        """
        タスクを承認し、実行をトリガーする。
        """
        for task in self.queue:
            if task['task_id'] == task_id:
                if task['status'] in ['APPROVED', 'EXECUTED']:
                    logger.warning(f"Task {task_id} is already {task['status']}.")
                    return False
                
                task['status'] = 'APPROVED'
                logger.info(f"Task {task_id} APPROVED by Owner. Proceeding to execution...")
                success = self.execute_task(task)
                if success:
                    task['status'] = 'EXECUTED'
                    task['executed_at'] = datetime.now().isoformat()
                else:
                    task['status'] = 'FAILED'
                
                self._save_queue()
                return success
        return False

    def execute_task(self, task):
        """
        アクションタイプに応じた実際の処理を実行する。
        """
        action_type = task.get("action_type")
        content = task.get("content")
        metadata = task.get("metadata", {})
        
        try:
            if action_type == "EmailProposal":
                from scripts.auto_sender import AutoSender
                sender = AutoSender()
                # AutoSender.send_proposal_email は target (dict) と content を受け取る
                target = {
                    "username": task.get("client_id"),
                    "email": metadata.get("email"),
                    "sector": task.get("sector"),
                    "lang": metadata.get("lang", "ja")
                }
                return sender.send_proposal_email(target, content)
            
            elif action_type in ["MarketExpansion", "LegalFormGeneration", "Fulfillment", "InvoiceIssuance", "DataSubmission"]:
                # これらのアクションは、現時点では「承認済み・実行済み」として記録することを主目的とする
                # （将来的に専用の生成エンジンや外部API連携を統合する拡張性を保持）
                logger.info(f"Task {task['task_id']} ({action_type}) marked as processed.")
                return True
                
            else:
                logger.warning(f"Unknown action_type: {action_type}")
                return False
        except Exception as e:
            logger.error(f"Execution failed for task {task['task_id']}: {e}")
            return False

    def reject_task(self, task_id):
        """
        タスクを却下する。
        """
        for task in self.queue:
            if task['task_id'] == task_id:
                task['status'] = 'REJECTED'
                self._save_queue()
                return True
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    q = ApprovalQueue()
    # テスト用タスク追加
    q.add_task(
        "TEST_Niche_Client", 
        "LocalGov", 
        "EmailProposal", 
        "テスト提案内容です。",
        metadata={"email": "test@example.com", "lang": "ja"}
    )
