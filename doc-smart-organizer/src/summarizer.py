import logging

class DocSummarizer:
    """
    抽出された情報と全文を元に、人間が読むためのサマリーを作成するエンジン。
    FXの「1日予測サマリー」のような、要点を突いた文章を生成します。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def summarize(self, text: str, metadata: dict):
        """
        内容を3つのポイントで要約する。
        """
        # 実際にはLLM（OpenAI等）を呼び出して生成する
        # ここではビジネス書類の典型的なパターンに基づいたモック実装
        
        summary_points = [
            f"本書類は {metadata.get('vendor')} 関連の公式文書です。",
            f"{metadata.get('date')} 付で、金額 {metadata.get('amount')} の内容を含みます。"
        ]
        
        if "契約" in text:
            summary_points.append("主要な契約条項、または合意事項が含まれています。確認が必要です。")
        elif "請求" in text:
            summary_points.append("支払いに関する通知です。期日に注意してください。")
        else:
            summary_points.append("一般的な業務連絡または資料です。")

        return summary_points

    def determine_importance(self, text: str, metadata: dict):
        """
        書類の緊急度・重要度を判定する。
        """
        if "至急" in text or "契約" in text or int(metadata.get('amount', '0').replace('円', '').replace(',', '')) > 1000000:
            return "High"
        return "Normal"
