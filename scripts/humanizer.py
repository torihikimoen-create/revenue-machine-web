import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class HumanizerEngine:
    """
    法的チェック済みの文章を、熟練のコピーライターの視点で「人間らしい」温かみのあるビジネス文書に昇華させる。
    """
    def __init__(self):
        self.logger = logging.getLogger("HumanizerEngine")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def polish(self, content: str, sector: str = "General", current_date: str = "2026-03-18", mode: str = "letter"):
        """
        文章に「血の通った」ニュアンスを加え、AI特有の機械感を排除する。
        mode: 'letter' (ビジネスレター形式), 'ad_copy' (広告コピー/SNS形式)
        """
        if mode == "ad_copy":
            system_instruction = "You are a master of Japanese advertising copywriting and compliance. Your goal is to make the copy catchy and persuasive while strictly following legal constraints."
            mode_prompt = f"""
あなたはキャリア20年以上の、日本を代表する「広告コピーライター」兼「リーガルチェッカー」です。
ターゲット（{sector}業界）向けの広告コピーを、キャッチーで魅力的な表現を維持しつつ、
【薬機法・景表法】の法的リスクを完全に回避した「安全で売れるコピー」にリライトしてください。

【制約事項】
1. **ビジネスレター形式の禁止**: 「拝啓」「敬具」「貴社ますます〜」といった挨拶は一切不要です。
2. **キャッチコピーの維持**: 短く、心に刺さる言葉選びをしてください。
3. **法的リスクの回避**: 指示された禁止表現やリスクを、法的に安全な代替表現（言い換え）に昇華させてください。
4. **自然な日本語**: AIが書いたような説明的な文章ではなく、リズムの良いプロのコピーにしてください。
"""
        else:
            system_instruction = "You are a master of Japanese business copywriting. Your goal is to eliminate AI-ness and add human soul to the text."
            mode_prompt = f"""
あなたはキャリア20年以上の、日本を代表するビジネスコピーライターです。
ターゲット（{sector}業界）に対し、AIが生成した以下の提案メールを、
「人間が心を込めて書いた手紙」のような、自然で温かみがあり、かつ信頼感のある文章にリライトしてください。

【リライトの指針】
1. **季節感と時間軸の正確性**: 現在は【{current_date}】（春）です。
2. **AI特有の構造を解体する**: 箇条書き依存や機械的な要約構造を避け、自然な文章として構成してください。
3. **人間らしい気遣いの付加**: 相手の苦労や現場の状況を察する言葉を添えてください。
"""

        prompt = f"""
{mode_prompt}

【元の文章 / 指示内容】
{content}

【最終的な目的】
読み手が「これはAIが作ったテンプレートだな」と感じることなく、心に響く文章に変えてください。
返信は、修正後の本文のみを返してください。
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            polished_content = response.choices[0].message.content.strip()
            self.logger.info(f"Content successfully humanized in {mode} mode.")
            return (polished_content, True)
        except Exception as e:
            self.logger.error(f"Error humanizing content: {e}")
            return (content, False)
