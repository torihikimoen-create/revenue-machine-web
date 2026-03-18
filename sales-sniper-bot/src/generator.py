import logging

class ProposalGenerator:
    """
    抽出したリードに対し、心を動かす提案文を自動作成するエンジン。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate(self, lead: dict, region="Japan"):
        """
        Generates a high-converting proposal tailored to the region.
        Supported: Japan, New York, London
        """
        name = lead.get('name', 'Owner')
        issue = lead.get('issue', 'online reviews')
        
        if region == "New York":
            return f"Subject: Strategic Optimization for {name} (NYC)\n\nDear Doctor,\n\nI noticed a critical opportunity regarding your online presence: {issue}.\n\nIn the competitive NYC market, this is a missed opportunity for growth. I have already drafted several AI-optimized responses tailored to your brand voice..."
        elif region == "London":
            # British English tone: polite yet professional
            return f"Subject: Professional Online Reputation Management for {name}\n\nDear Clinical Director,\n\nIn the competitive London market, {issue} is a concern we can resolve. A well-managed Google profile is key to patient trust. We can automate your responses while maintaining a professional British tone..."
        else:
            return f"【ご提案：{name} 様】\n\nGoogleマップの口コミ管理について\n\n現在、貴店の状況を確認したところ、{issue} という課題があるようです。\n\n放置された口コミは機会損失に直結します。弊社のAIシステムで、全件へ丁寧な返信を完了させることが可能です。"
