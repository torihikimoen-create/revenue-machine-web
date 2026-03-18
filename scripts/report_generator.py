import json
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CrisisScenarioProcessor:
    """
    行政処分、免許停止、莫大な罰金など、経営者が最も恐れる「最悪の未来」を具体化する。
    """
    def __init__(self, data=None):
        self.scenarios = data if data else {}

    def get_crisis_text(self, sector):
        scenario = self.scenarios.get(sector, "法令遵守の不備による業務停止および法的責任の追及。")
        return f"\n【⚠️ 警告：放置した場合の生存リスク】\n{scenario}\n"

class GrowthReportGenerator:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger = logging.getLogger("GrowthReportGenerator")

        # セクターデータの読み込み
        self.sector_data = self._load_sector_data()
        self.crisis_processor = CrisisScenarioProcessor(self.sector_data.get("crisis_scenarios"))

    def _load_sector_data(self):
        json_path = os.path.join(self.project_root, "config", "sector_data.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load sector data JSON: {e}")
            return {}

    def generate_report(self, target):
        """
        ターゲット店舗のデータを基に、AIが改善提案レポート（Growth Report）を生成する。
        """
        sector = target.get('sector', 'サービス業')
        client_name = target.get('username', '貴社')
        
        # 生存危機シナリオを取得
        crisis_alert = self.crisis_processor.get_crisis_text(sector)
        
        # 市場モードの決定 (Japan: Defense/Insurance vs West: Offense/ROI)
        market_mode = "West" if target.get('lang') != 'ja' else "Japan"
        
        # 業界別のインサイト（2026年のリサーチ結果に基づく）
        if market_mode == "Japan":
            sector_insights_map = self.sector_data.get("sector_insights_ja", {})
            sector_insights = sector_insights_map.get(sector, "2026年のリスク回避と業務継続のためのAI導入を強調。")
        else:
            # Western Mode (Offense / ROI / Dominance)
            sector_insights_map = self.sector_data.get("sector_insights_en", {})
            sector_insights = sector_insights_map.get(sector, "Highlight AI as a 'Competitive Advantage' and 'Unbeatable ROI' driver.")

        sector_name = target.get('sector', 'サービス業')
        sector_context = ""
        if sniper_signal := target.get('sniper_signal'):
            sector_context += f"\n【スナイパー検知データ】\n"
            if h_pressure := sniper_signal.get('hiring_pressure'):
                sector_context += f"- 労働供給圧：{h_pressure}（人手不足による経営リスク高）\n"
            if meo_gap := sniper_signal.get('meo_gap'):
                sector_context += f"- 顧客対応ギャップ：{meo_gap}（MEO評価低下の懸念）\n"

        prompt_intro = {
            "Japan": f"あなたは、日本の{sector_name}業界の課題（2026年問題）に精通した、世界ランクのエグゼクティブ・コンサルタントです。",
            "West": f"You are a top-tier executive growth consultant specializing in the {sector_name} sector's market disruption and ROI optimization."
        }.get(market_mode)

        prompt = f"""
{prompt_intro}
以下の企業/施設について、改善提案レポートを作成してください。

【対象 / Target】
名称: {target.get('username', '貴社')}
業種: {sector_name} ({target.get('sector', 'Niche')})
課題（検知された信号）: {target.get('issue', '業務効率化の余地')}
{sector_context}

【市場背景 / Market Insights】
{sector_insights}

5. 【重要】「10日間無料トライアル」の案内と、初動の重要性（「最初の契約」の心理的ハードルを下げる工夫。まずは効果を実感してもらうための特別枠であること、気に入らなければいつでも即時解約可能であることを強調）
6. なぜ「自社でAIを使う」のではなく「この『丸投げ型』自動システム」が必要なのか（技術があっても実行する時間がないオーナーのための代理執行、プロレベルのプロンプト調整、24時間365日の『完全放置』が可能にする機会損失ゼロの実現、DIYによる管理ミスや放置リスクの解消）

顧客が「ChatGPTなら自分でも使えるのでは？」と考えることを先回りし、「ツールを持っていること」と「成果を出すシステムが自動で回り続けること」の決定的な違いを、オーナーの「貴重な時間」という観点から説得してください。

また、メールの1行目に、相手が思わず開きたくなる「個別件名」を生成してください。
形式は必ず：
SUBJECT: [ここに生成した件名]
---
[ここに本文]
という形式にしてください。
言語: {target.get('lang', 'ja')}
"""
        try:
            # DRY_RUN時の動作（未設定・空は安全のためドライラン）
            if (os.getenv("DRY_RUN") or "true").lower() == "true":
                return f"【Mock AI Growth Report for {target.get('username')}】\nScenario: {sector_insights}\nAI analysis complete: 111% ROI potential identified."

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional business consultant specializing in local business growth."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            report_raw = response.choices[0].message.content
            
            # 件名と本文の分離
            if "SUBJECT:" in report_raw and "---" in report_raw:
                parts = report_raw.split("---", 1)
                subject = parts[0].replace("SUBJECT:", "").strip()
                content = parts[1].strip()
                return {"subject": subject, "content": content}
            
            return {"subject": None, "content": report_raw}
        except Exception as e:
            self.logger.error(f"Failed to generate growth report: {e}")
            return {"subject": None, "content": "AIによるレポート生成中にエラーが発生しました。詳細は別途お問い合わせください。"}

    def save_report(self, target, content):
        """
        生成されたレポートをファイルとして保存。
        """
        report_dir = os.path.join(self.project_root, "growth_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # content が辞書の場合は分解
        subject = None
        if isinstance(content, dict):
            subject = content.get('subject')
            content = content.get('content', "")

        safe_name = "".join(x for x in target['username'] if x.isalnum() or x in ('_', '-'))
        filename = f"GrowthReport_{safe_name}_{target['lang']}.txt"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if subject:
                f.write(f"SUBJECT: {subject}\n---\n")
            f.write(content)
            
        self.logger.info(f"Saved Growth Report to {filepath}")
        return filepath
