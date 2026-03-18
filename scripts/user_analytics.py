import os
import json
import logging
from datetime import datetime

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("UserAnalytics")

ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), '..', 'user_analytics.json')

def log_event(user_id, event_type, metadata=None):
    """
    ユーザーイベントを記録する（Aha! Momentや離脱ポイントの特定用）
    """
    now = datetime.now()
    event = {
        "timestamp": now.isoformat(),
        "event_type": event_type,
        "metadata": metadata or {}
    }
    
    data = {}
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
            
    if user_id not in data:
        data[user_id] = {
            "first_seen": now.isoformat(),
            "events": []
        }
        
    data[user_id]["events"].append(event)
    data[user_id]["last_active"] = now.isoformat()
    
    with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Event logged for {user_id}: {event_type}")

def get_aha_moment_stats():
    """
    「最初の成果（Aha! Moment）」に到達したユーザーの統計を計算
    """
    if not os.path.exists(ANALYTICS_FILE):
        return {"total_users": 0, "aha_reached": 0}
        
    with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_users = len(data)
    aha_reached = 0
    
    for user_id, info in data.items():
        if any(e["event_type"] == "aha_moment" for e in info["events"]):
            aha_reached += 1
            
    return {
        "total_users": total_users,
        "aha_reached": aha_reached,
        "conversion_rate": (aha_reached / total_users * 100) if total_users > 0 else 0
    }

if __name__ == "__main__":
    # テスト用
    log_event("test_user_001", "onboarding_started")
    log_event("test_user_001", "aha_moment", {"detail": "First AI Proposal Sent"})
    print(get_aha_moment_stats())
