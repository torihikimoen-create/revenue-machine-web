import os
import json
import re

class LPUpdater:
    """
    エンジンの稼働結果を読み取り、LPの表示内容を自動更新する。
    """
    def __init__(self, lp_path: str):
        self.lp_path = lp_path
        self.html_file = os.path.join(lp_path, 'index.html')

    def update_revenue(self, new_revenue: int):
        """
        index.html内の収益表示を書き換える。
        """
        if not os.path.exists(self.html_file):
            print(f"Error: {self.html_file} not found.")
            return

        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # HTML内の ¥1,240,500 形式の箇所を置換
        formatted_revenue = f"¥{new_revenue:,}"
        pattern = r'id="stat-revenue">¥[\d,]+</span>'
        replacement = f'id="stat-revenue">{formatted_revenue}</span>'
        
        new_content = re.sub(pattern, replacement, content)

        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"LP Updated: Revenue set to {formatted_revenue}")

if __name__ == "__main__":
    # テスト実行
    updater = LPUpdater("c:/Users/himic/.gemini/antigravity/scratch/business-automation/official-landing-page")
    # 例：現在の124万から1万増えたと仮定
    updater.update_revenue(1250500)
