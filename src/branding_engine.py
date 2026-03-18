import os
import json
import logging
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SolarBrandingEngine:
    """
    レポートや哲学からSNS向けの「権威構築コンテンツ」を錬成するエンジン。
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"

    def generate_social_posts(self, source_text, platforms=["X", "LinkedIn"], language="ja"):
        """
        ソーステキストを元に、SNSプラットフォーム別の投稿案を生成する。
        """
        platform_specs = {
            "X": "Short, punchy, thread-ready. Emphasize insight and edge. (Max 280 chars per post)",
            "LinkedIn": "Professional, storytelling style, authoritative, focuses on business value and future vision."
        }
        
        prompt = f"""
You are a High-End Social Media Strategist for AETHER CORE.
Task: Generate authority-building social media posts from the provided "Source Material".
Language: {language}

Source Material:
{source_text[:2000]} # Limit to first 2000 chars

Instructions:
1. For each platform ({', '.join(platforms)}), create a distinct post/thread.
2. Blend "Emotional Lyricism" (Sentiment) with "Hard Business Logic" (Edge).
3. The goal is to make the reader feel that the author (Masumoto) is a visionary leader in AI and Industrial DX.
4. Avoid generic hashtags. Use terms like #AETHERCORE #IndustrialDX.

Platform Specifics:
{json.dumps({p: platform_specs.get(p, "Standard") for p in platforms}, indent=2)}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are the Solar Branding Core of AETHER CORE."},
                          {"role": "user", "content": prompt}]
            )
            posts = response.choices[0].message.content
            print(f"--- [Draft Generated ({language})] ---")
            
            # 印象管理ガードレール（自動チェック）
            safe_posts = self.validate_impression(posts, language)
            return safe_posts
        except Exception as e:
            logger.error(f"Error in generate_social_posts: {e}")
            return "Failed to generate social content."

    def validate_impression(self, content, language="ja"):
        """
        生成された内容が「印象を悪くしないか」をPR視点でチェックする。
        """
        print(f"--- [Safety Check: Running Guardrail for {language}...] ---")
        prompt = f"""
You are a Professional PR Manager and Brand Protector for a high-end AI Visionary.
Review the following social media posts and ensure they do NOT damage the author's reputation.

Content to Review:
{content}

Reputation Check Criteria:
1. ARROGANCE: Is it overly arrogant, dismissive, or condescending?
2. TRUST: Does it sound like "spam", a "scam", or a cheap sales pitch?
3. CULTURE: Is the tone appropriate for the {language} business culture?
4. SOUL: Does it maintain the author's unique "sentimental yet sharp" voice?

Output Rules:
- If the content is risky, rewrite it to be "Visionary, Humble, yet Authoritative".
- If it is safe, return the original content.
- Output ONLY the final, safe content in {language}.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are the Guardian of Brand Reputation."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in validate_impression: {e}")
            return content

if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    engine = SolarBrandingEngine()
    
    # 錬金術で生成されたレポートを読み込む
    report_path = os.path.join("assets", "products", "aether_core_vision_report.md")
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
    except FileNotFoundError:
        report_content = "AETHER CORE is the future of industrial automation and DX."

    print("--- [Solar Branding: Generating Global Authority...] ---")
    
    # 日本語X/LinkedIn向け
    jp_content = engine.generate_social_posts(report_content, platforms=["X", "LinkedIn"], language="ja")
    print("\n[Japanese Authority Content]")
    print(jp_content)

    print("\n" + "="*50 + "\n")

    # 欧米（英語）LinkedIn向け
    en_content = engine.generate_social_posts(report_content, platforms=["LinkedIn"], language="en")
    print("\n[Western Authority Content (LinkedIn)]")
    print(en_content)
