import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DMDraftGenerator:
    """
    SNS特有の「距離感」を考慮した、刺さるDM案をAIで自動生成する。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_dm(self, target: dict, payment_link: str = None):
        """
        GPT-4oを使用してパーソナライズされたDM案を作成。
        """
        payment_info = f"\n決済リンク(Stripe): {payment_link}" if payment_link else ""
        
        prompt = f"""
あなたはプロのセールスマネージャーです。
以下のターゲットに対して、彼らが抱えている課題を解決するための
短く、かつ非常に説得力のあるDM（ダイレクトメッセージ）の下書きを作成してください。

【ターゲット情報】
- 名前: {target.get('username', '担当者')}
- 検出された課題: {target.get('issue_detected', '業務効率化')}
- 使用言語: {target.get('lang', 'ja')}
- AI知識レベル: {target.get('awareness_level', 'high')}

【最優先事項】
- もし以下の決済リンクが提供されている場合、メッセージの最後の方に必ず自然な形で「こちらから導入可能です」という旨と共にURLを記載してください。
- 決済リンク: {payment_link if payment_link else "なし"}

【制作ルール】
1. 相手の現状（課題）に共感し、ソリューションのメリットを伝えてください。
2. 押し売りではなく、相手の時間を節約するための提案であることを強調してください。
3. 日本語（または指定された言語）で、DM本文のみを出力してください。

【AI知識レベルに応じた調整】
- レベルが "low" の場合: 「AI」「自動化」「生成」「DX」「アルゴリズム」といった専門用語を絶対に避けてください。
  代わりに「24時間働く分身」「デジタル事務スタッフ」「自動片付け」「残業ゼロ」「丸投げ」といった、直感的で優しい言葉を使ってください。
- レベルが "high" の場合: 効率性、最新技術、確実性を強調してロジカルに構成してください。
"""

        try:
            # DRY_RUN時の動作（未設定・空は安全のためドライラン）
            if (os.getenv("DRY_RUN") or "true").lower() == "true":
                return f"[Mock DM for {target['username']}] I noticed you are struggling with {target['issue_detected']}. We have an AI solution to help you."

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional outreach specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            dm_text = response.choices[0].message.content.strip()
            return dm_text
        except Exception as e:
            self.logger.error(f"Error generating DM via OpenAI: {e}")
            # フォールバック（以前の簡易ロジックに近いもの）
            return f"Hi {target['username']}, I noticed you are struggling with {target['issue_detected']}. I have an AI solution that might help. Would you be interested in a quick brief?"
