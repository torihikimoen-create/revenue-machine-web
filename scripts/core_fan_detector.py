import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("CoreFanDetector")
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), '..', 'user_analytics.json')

def score_users():
    """
    ユーザーの活動状況に基づいて「熱量」をスコアリングする
    """
    if not os.path.exists(ANALYTICS_FILE):
        return []

    with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scored_users = []
    for user_id, info in data.items():
        score = 0
        events = info.get("events", [])
        
        # スコアリングロジック
        for event in events:
            if event["event_type"] == "aha_moment":
                score += 50 # 成功体験は大きい
            elif event["event_type"] == "onboarding_completed":
                score += 20
            elif event["event_type"] == "feedback_sent":
                score += 15 # 対話に応じるのは熱心
            else:
                score += 5 # 通常アクティビティ
        
        scored_users.append({
            "user_id": user_id,
            "score": score,
            "event_count": len(events),
            "last_active": info.get("last_active")
        })

    # スコア順にソート
    scored_users.sort(key=lambda x: x["score"], reverse=True)
    return scored_users

def get_top_fans(limit=5):
    """
    特に熱量の高い「コアファン（ベスタ層）」を抽出
    """
    users = score_users()
    top_fans = [u for u in users if u["score"] >= 100] # 100点以上をコアファンと定義
    return top_fans[:limit]

if __name__ == "__main__":
    fans = get_top_fans()
    print("Top Fans (Vesta Layer):")
    for fan in fans:
        print(f"- {fan['user_id']}: Score {fan['score']}")
