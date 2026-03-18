import logging
import random

class GoogleMapsSniper:
    """
    Googleマップから「営業の隙」がある店舗を特定するエンジン。
    FXでの「トレンドの転換点」を見つけるように、ビジネスの改善点を探します。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_leads(self, category: str, location: str):
        """
        API（モック）から店舗情報を検索し、未返信口コミの状態を調査。
        """
        # 本来は Google Places API を実行
        mock_leads = [
            {
                "name": "居酒屋 あいうえお",
                "rating": 3.8,
                "total_reviews": 120,
                "unreplied_count": 45, # 45件も放置されている！
                "contact": "info@aiueo-izakaya.jp"
            },
            {
                "name": "カフェ かきくけこ",
                "rating": 4.5,
                "total_reviews": 80,
                "unreplied_count": 2, # 管理が行き届いている
                "contact": "03-1234-5678"
            },
            {
                "name": "美容室 さしすせそ",
                "rating": 3.2,
                "total_reviews": 50,
                "unreplied_count": 30, # 改善の余地大
                "contact": "https://sashisuseso-hair.com/contact"
            }
        ]
        
        qualified_leads = []
        for lead in mock_leads:
            # 営業対象の判定ロジック
            # 未返信が全体の20%以上なら「ホットリード」
            if lead['unreplied_count'] / lead['total_reviews'] > 0.2:
                lead['status'] = "HOT"
                lead['message'] = f"未返信が{lead['unreplied_count']}件あります。AI自動返信の導入で満足度向上が見込めます。"
                qualified_leads.append(lead)
                
        return qualified_leads
