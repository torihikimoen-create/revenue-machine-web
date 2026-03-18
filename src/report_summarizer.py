import json
import os
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ActivitySummarizer:
    """
    システムの複雑なログを、増本様に報告するための「温かみのある報告書」へ変換する。
    """
    def __init__(self, stats_path="daily_stats.json", history_path="leads_history.json"):
        self.stats_path = stats_path
        self.history_path = history_path
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def summarize_today(self):
        """
        本日の活動と成果を要約する。
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        stats = self._load_json(self.stats_path)
        history = self._load_json(self.history_path)
        
        today_stats = stats.get(today_str, {})
        
        # 本日の接触リード数
        count = 0
        current_focus_sectors = []
        for lid, info in history.items():
            if info.get("last_contact", "").startswith(today_str):
                count += 1
                sec = info.get("sector")
                if sec and sec not in current_focus_sectors:
                    current_focus_sectors.append(sec)

        summary_prompt = f"""
Summarize today's business activities for the owner, Masumoto-sama.
CRITICAL: Do NOT hallucinate. Use ONLY the data provided below. If a metric is 0, report it as 0.

Fact Base:
- Date: {today_str}
- Contacts Made (Actual): {count}
- Focus Sectors (Logged): {', '.join(current_focus_sectors) if current_focus_sectors else 'Researching new sectors'}

Instructions:
1. Use a professional and visionary tone, but stay strictly grounded in the facts.
2. If no contacts were made, explain that the system is in standby or research mode.
3. Language: Japanese
4. Do NOT invent customer names, specific feedbacks, or numbers not listed above.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are the Chief Operating Officer of AETHER CORE, reporting to the Owner."},
                          {"role": "user", "content": summary_prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"本日は {count} 件のリードに接触しました。現在は{', '.join(current_focus_sectors)}を中心に活動しています。詳細はStripe画面でもご確認いただけます。"

if __name__ == "__main__":
    # テスト
    summarizer = ActivitySummarizer()
    print("--- [AETHER CORE Daily Insight] ---")
    print(summarizer.summarize_today())
