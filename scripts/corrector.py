import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIProposalCorrector:
    """
    合議制チェックで REJECT された提案書を専門家AIのフィードバックに基づき修正する。
    """
    def __init__(self):
        self.logger = logging.getLogger("AIProposalCorrector")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def correct_proposal(self, original_content: str, consensus_report: dict):
        """
        フィードバックを反映して修正版を作成。
        """
        rejection_reasons = "\n".join([f"- {o['expert']}: {o['message']}" for o in consensus_report['opinions'] if o['status'] == 'REJECTED'])
        fact_violations = "\n".join(consensus_report['fact_checks'].get('violations', []))

        prompt = f"""
あなたは優秀なビジネスエディターです。
AIが作成した以下の提案書に対し、専門家チームから「NG（REJECTED）」判定が出ました。
以下の指摘事項および法的事実に基づき、内容を完璧に修正してください。

【元の提案内容】
{original_content}

【指摘事項】
{rejection_reasons}

【法的事実（裏取り結果）】
{fact_violations}

【修正の鉄則】
1. 指摘された誤った年号や施行日は、法的事実に基づき正確に書き直してください。現在は「2026年3月」です。2024年問題などは「すでに施行された規制への定着・最適化」という文脈で扱ってください。
2. 「今、この瞬間」「理由は明確」といった急かす・断定的なAI特有の表現は削除し、自然で落ち着いたビジネス文書にしてください。
3. 誰が担当しても、といった表現は「どなたが担当されても」などのより丁寧な敬語表現に置き換えてください。
4. 「他社に勝つ」「利益独占」等の攻撃的な文言は、誠実で謙虚な表現に置き換えてください。
5. 修正後の文章も、プロフェッショナルかつ誠実なビジネス日本語として完成させてください。
6. 元の提案書の構成（決済リンク、無料トライアルの案内等）は維持してください。
7. 法的リスクがある箇所は、単に削除するのではなく、正しい情報に基づき「リスク回避の提案」として再構成してください。
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # 修正はより高性能なモデルで行う
                messages=[
                    {"role": "system", "content": "You are a professional business copy editor. Fix the errors and return only the corrected text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            corrected_content = response.choices[0].message.content.strip()
            self.logger.info("Proposal successfully corrected by AI.")
            return corrected_content
        except Exception as e:
            self.logger.error(f"Error correcting proposal: {e}")
            return original_content # 失敗した場合は元の内容を返す（後のフローで承認待ちになる）
