import logging

class B2BDealFinder:
    """
    データ整理（15万円）や書類整理（5万円）の大型案件を「釣り上げる」エンジン。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def find_opportunities(self, deal_list: list = None):
        """
        案件リストを抽出。引数があればそれを使用。
        """
        if deal_list:
            self.logger.info(f"Ingesting {len(deal_list)} external deals.")
            return deal_list

        mock_jobs = [
            {
                "client": "株式会社デジタルトランス",
                "title": "社内サーバーのデータ整理・命名ルール統一（ファイル数3万件）",
                "budget": "100,000円〜300,000円",
                "urgency": "High",
                "source": "Corporate Recruiting Page"
            },
            # ... (中略)
        ]
        
        deals = []
        # ... (解析ロジックは従来通り)
    def save_proposal(self, deal: dict, content: any):
        """
        生成された提案書をファイルとして保存。
        """
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prop_dir = os.path.join(base_dir, "proposals")
        os.makedirs(prop_dir, exist_ok=True)
        
        # content が辞書の場合は分解
        subject = None
        if isinstance(content, dict):
            subject = content.get('subject')
            content = content.get('content', "")

        # クライアント名等からファイル名を生成（日本語対応）
        client_name = deal.get('client', deal.get('username', 'Unknown'))
        safe_name = "".join(x for x in client_name if x.isalnum())
        filename = f"Proposal_{safe_name}.txt"
        filepath = os.path.join(prop_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"--- Client: {client_name} ---\n")
            f.write(f"--- Title: {deal.get('title', 'AI Automation')} ---\n")
            if subject:
                f.write(f"--- Subject: {subject} ---\n")
            f.write("\n")
            f.write(content)
            
        self.logger.info(f"Saved business proposal to {filepath}")
        return filepath
