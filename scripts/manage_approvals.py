import os
import sys
import logging
import json

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

import sys
import io

# 出力のエンコーディングを強制的に UTF-8 に設定 (Windows環境の UnicodeEncodeError 対策)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

from scripts.approval_dashboard import ApprovalQueue

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ApprovalManager")

def display_queue(queue):
    pending_tasks = [t for t in queue if t['status'] in ['PENDING', 'REVIEW_REQUIRED']]
    if not pending_tasks:
        print("\n✨ 承認待ちのタスクはありません。")
        return []
    
    print("\n--- [PENDING TASKS] ---")
    for i, task in enumerate(pending_tasks):
        status_icon = "!" if task['status'] == 'REVIEW_REQUIRED' else "-"
        print(f"[{i}] {status_icon} ID: {task['task_id']}")
        print(f"    Client: {task['client_id']} ({task['sector']})")
        print(f"    Action: {task['action_type']}")
        print(f"    Consensus: {task['consensus'].get('summary')} (Risk: {task['consensus'].get('overall_risk_score')})")
        print("-" * 30)
    return pending_tasks

def main():
    approval_queue = ApprovalQueue()
    
    while True:
        pending_tasks = display_queue(approval_queue.queue)
        if not pending_tasks:
            break
            
        print("\nコマンド: [番号] 承認 / [r + 番号] 却下 / [v + 番号] 内容表示 / [q] 終了")
        choice = input(">> ").strip().lower()
        
        if choice == 'q':
            break
        
        try:
            if choice.startswith('v'):
                idx = int(choice[1:])
                task = pending_tasks[idx]
                print(f"\n--- 📄 タスク詳細: {task['task_id']} ---")
                print(f"内容:\n{task['content']}")
                print(f"\n--- 🤖 AI Consensus: {task['consensus'].get('summary')} ---")
                for opinion in task['consensus'].get('opinions', []):
                    status_symbol = "✅" if opinion['status'] == 'APPROVED' else "⚠️"
                    print(f"[{status_symbol}] {opinion['expert']}: {opinion['message']}")
                
                # 裏取り（Fact Check）結果の表示
                fact_checks = task['consensus'].get('fact_checks', [])
                if fact_checks:
                    print(f"\n--- 🔍 Fact Check (裏取り結果) ---")
                    for fc in fact_checks:
                        if fc:
                            v_symbol = "✔️" if fc['verified'] else "❌"
                            print(f"[{v_symbol}] {fc['keyword']}: {fc['message']} ({fc['confidence']})")
                
                print(f"\nメタデータ: {task.get('metadata', {})}")
                input("\nEnterで戻る...")
                
            elif choice.startswith('r'):
                idx = int(choice[1:])
                task_id = pending_tasks[idx]['task_id']
                if approval_queue.reject_task(task_id):
                    print(f"✅ タスク {task_id} を却下しました。")
                
            else:
                idx = int(choice)
                task_id = pending_tasks[idx]['task_id']
                print(f"🚀 タスク {task_id} を実行中...")
                success = approval_queue.approve_task(task_id)
                if success:
                    print(f"✅ 実行完了！")
                else:
                    print(f"❌ 実行失敗。ログを確認してください。")
                    
        except (ValueError, IndexError):
            print("❌ 無効な入力です。")

if __name__ == "__main__":
    main()
