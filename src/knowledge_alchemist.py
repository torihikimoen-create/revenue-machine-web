import os
import json
import logging
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class KnowledgeAlchemist:
    """
    断片的な知識や思考を、体系化された「商品（デジタル資産）」へと錬金するエンジン。
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o" # 高品質な編集が必要なため、上位モデルを使用

    def ingest_raw_material(self, sources):
        """
        複数のソース（歌詞、メモ、ログ等）を統合する。
        """
        combined = "\n\n".join([f"--- Source: {s['name']} ---\n{s['content']}" for s in sources])
        return combined

    def distill_into_product(self, raw_material, product_theme="Business Strategy"):
        """
        未構造データを解析し、章立てされたレポート形式の商品に変換する。
        """
        prompt = f"""
You are a World-Class Editor and Product Strategist.
Your task is to transform the following "Raw Material" into a high-value, sellable Digital Product (Intelligence Report).

Theme: {product_theme}
Target Audience: Entrepreneurs and Executives looking for the "Blue Ocean" in AI and Automation.

Raw Material:
{raw_material}

Instructions:
1. Identify the "core soul" or "unique philosophy" in the material (especially if it contains artistic elements like lyrics).
2. Structure the content into a multi-chapter report:
   - Executive Summary
   - The Philosophy (The Soul)
   - Market Analysis (The Edge)
   - Actionable Implementation Steps
   - Conclusion
3. Use a tone that is "Premium, Deep, and Authoritative".
4. Output the result in beautiful Markdown format.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You convert chaos into gold."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in distill_into_product: {e}")
            return "Failed to distill knowledge."

    def save_product(self, content, filename):
        """
        生成した商品をファイルとして保存する。
        """
        save_path = os.path.join("assets", "products", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Product saved to: {save_path}")
        return save_path

# デモ用データ
if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    alchemist = KnowledgeAlchemist()
    
    # ソース1: 増本様の歌詞（ブランドの魂）
    lyrics = """
    ルーティンの今日も終わる　濃度の境界線
    窓際センチメンタル　泣き笑いの翼
    """
    
    # ソース2: ブルーオーシャン・リサーチ（市場の実利）
    research = """
    産廃業界、介護業界、建設業界。
    法改正によるコンプライアンス需要と、ITリテラシーの乖離が「真のブルーオーシャン」。
    AETHER COREは、その乖離を埋める「聖域（サンクチュアリ）」となる。
    """
    
    sources = [
        {"name": "Masumoto's Lyrics", "content": lyrics},
        {"name": "Blue Ocean Research", "content": research}
    ]
    
    print("--- [Distilling Knowledge into Gold...] ---")
    raw = alchemist.ingest_raw_material(sources)
    product_md = alchemist.distill_into_product(raw, product_theme="AETHER CORE: The Sacred Industrial Revolution")
    
    # 保存
    alchemist.save_product(product_md, "aether_core_vision_report.md")
    print("\n[Preview of the Product]")
    print(product_md[:500] + "...")
