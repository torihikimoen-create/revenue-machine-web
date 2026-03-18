import logging
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class BusinessProposalBuilder:
    """
    大型案件を勝ち取るための、ロジカルで説得力のある提案書をAIで作成する。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def build_proposal(self, deal: dict, payment_link: str = None):
        """
        GPT-4oを使用して正式なビジネス提案書を作成。
        """
        
        # クライアント名を取得（client または username）
        client_name = deal.get('client', deal.get('username', '貴社'))
        
        prompt = f"""
あなたはB2B営業のエキスパートです。
以下の案件内容に基づき、クライアントが即決したくなるような
論理的でプロフェッショナルな「提案書」の本文を作成してください。

【案件・クライアント情報】
- クライアント: {client_name}
- 案件名: {deal.get('title', 'AI導入による業務自動化パッケージ')}
- 予算: {deal.get('budget', '要相談')}
- AI知識レベル: {deal.get('awareness_level', 'high')}

【最優先事項】
- メッセージの最後に、必ず以下の決済リンク（お見積り兼決済URL）を記載し、ここから着手可能であることを伝えてください。
- 決済リンク: {payment_link if payment_link else "別途ご案内"}

【構成案】
1. 相手の現状に対し、「2024年問題や法改正への対応が一段落した今だからこそ、現場のさらなる安定と負担軽減を進める好機である」という前向きかつ落ち着いた視点を提示。
2. 導入直後から「あんなに手間のかかっていたルーチン作業が自動化され、現場に心にゆとりが生まれる」という実務上の具体的な変化を優しく描写。
3. 24時間365日の自動代行が、日々の「うっかりミス」や「確認漏れ」を防ぎ、「どなたが担当されても」同じ品質で運営できる安心感の裏付け。
4. 「今、この瞬間」といった言葉は使わず、将来にわたる持続可能な体制づくりとしての提案。
5. 10日間無料トライアル（全機能解放）への丁寧な誘導。まずは「現在の運用がどれほど楽になるか、リスクなく確かめていただくための期間」であることを伝えてください。

【禁止事項】
- 「競争優位」「他社に勝つ」「利益を独占」「市場を圧倒」といった攻撃的、野心的な表現は厳禁。
- 「今、この瞬間」「理由は明確です」「遅れると大変なことになります」といった、AI特有の急かす・威圧的な表現は一切使用しないでください。
- 日本企業が好む「安心」「安全」「現場の負担軽減」「ミスの防止」「スムーズな移行」といった言葉を、相手を尊重した丁寧な言葉遣い（謙譲語・尊敬語を適切に）で使用してください。
- 誰が（who）を指す際は「どなたが」とするなど、品位のある言葉を選んでください。
- 建設セクター等の場合、件名に「2024年問題」と入れると2026年現在は古く感じられるため、避けてください。

【AI知識レベルに応じた調整】
- レベルが "low" の場合: 「AI」「アルゴリズム」「LLM」「ハルシネーション」「プロンプト」等の用語は使用禁止です。
  「実務を肩代わりするデジタルスタッフ」「ミスのない自動集計」「魔法のように業務が終わる仕組み」といった言葉を選んでください。
- レベルが "high" の場合: AIの専門性、精度、モデルの優位性をロジカルに提示してください。
"""

        try:
            # DRY_RUN時の動作（未設定・空は安全のためドライラン）
            if (os.getenv("DRY_RUN") or "true").lower() == "true":
                return f"【Mock Proposal for {client_name}】\nRegarding your need for {deal.get('title')}, we propose an AI-driven solution..."

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional B2B business development manager. You MUST output your response in JSON format with two keys: 'subject' and 'content'."},
                    {"role": "user", "content": prompt + "\n\n【出力形式】\n以下のJSON形式で出力してください。\n{\n  \"subject\": \"ターゲットが思わず開封したくなる、パーソナライズされた魅力的な件名\",\n  \"content\": \"提案書の本文\"\n}"}
                ],
                response_format={ "type": "json_object" },
                temperature=0.7
            )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            self.logger.error(f"Error building proposal via OpenAI: {e}")
            # フォールバック
            return {
                "subject": f"【効率化のご提案】{client_name}様の実務負担軽減について",
                "content": f"【業務効率化のご提案：{client_name} 御中】\n「{deal.get('title', 'AI導入')}」に関するAI自動化ソリューションのご案内..."
            }
