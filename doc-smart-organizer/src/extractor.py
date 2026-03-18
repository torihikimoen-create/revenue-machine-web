import logging
import re

class DocExtractor:
    """
    書類から重要なメタデータ（日付、金額、企業名等）を抽出するエンジン。
    FXでのチャートパターン認識と同様、ノイズの中から「有意なシグナル」を捉えます。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_metadata(self, text: str):
        """
        正規表現と文脈解析（将来的にLLM）を用いて情報を抽出する。
        """
        # 日付の抽出 (YYYY/MM/DD 等)
        date_pattern = r'\b(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)\b'
        date_match = re.search(date_pattern, text)
        
        # 金額の抽出 (￥1,000, 100,000円 等)
        amount_pattern = r'[￥¥\\$](\d{1,3}(?:,\d{3})*)|(\d{1,3}(?:,\d{3})*)円'
        amount_match = re.search(amount_pattern, text)
        
        # 会社名/取引先の単純な抽出手法（実際にはLLMで高精度化する）
        vendors = ["株式会社", "合同会社", "Inc.", "Corp."]
        vendor_found = "Unknown"
        for v in vendors:
            if v in text:
                # 会社名っぽいのを周辺から探す（簡易版）
                idx = text.find(v)
                vendor_found = text[max(0, idx-10):idx+len(v)]
                break

        return {
            "date": date_match.group(0) if date_match else "N/A",
            "amount": amount_match.group(0) or amount_match.group(1) if amount_match else "0",
            "vendor": vendor_found.strip(),
            "confidence": 0.85 # FXと同様、確信度を重要視
        }
