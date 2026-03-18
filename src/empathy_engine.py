import os
import sys
import json
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmpathyEngine:
    """
    ユーザーの感情と文脈を解析し、先回りしたアクションを提案するエンジン。
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini" # コスト効率重視

    def analyze_interaction(self, logs, culture="ja"):
        """
        インタラクションログ（メッセージ、滞在時間、エラー等）から感情を抽出する。
        """
        prompt = f"""
Analyze the following user interaction logs and identify "hidden dissatisfaction" or "unarticulated needs".
Cultural Context: {culture} (ja=High Context/Empathy, en=Low Context/Direct)

Logs:
{json.dumps(logs, indent=2, ensure_ascii=False)}

Return a JSON with:
1. sentiment_score (0.0 to 1.0, lower means more unhappy)
2. detected_emotions (list)
3. hidden_stress_point (string)
4. suggested_approach (gentle or direct)
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are an expert in business psychology and customer success."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in analyze_interaction: {e}")
            return {"sentiment_score": 0.5, "detected_emotions": ["unknown"], "hidden_stress_point": "Analysis failed"}

    def generate_preemptive_message(self, analysis, target_name, culture="ja"):
        """
        分析結果に基づき、先回りした「寄り添い」または「解決」メッセージを生成する。
        """
        tone_instruction = {
            "ja": "寄り添い、共感、丁寧、謙虚。相手の心境を察するような表現。 (High Context)",
            "en": "Direct, solution-oriented, authoritative, efficient. Focus on resolving the stress point. (Low Context)"
        }

        prompt = f"""
Generate a preemptive customer success message for {target_name} in {culture} language.
Analysis: {json.dumps(analysis, ensure_ascii=False)}
Tone Instruction: {tone_instruction.get(culture, "Standard")}

The message should address the 'hidden_stress_point' without being creepy, making the user feel 'understood'.
Output ONLY the message content in {culture} language.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": f"You are AETHER CORE Empathy AI for {culture} market."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in generate_preemptive_message: {e}")
            return "Something went wrong, please check the logs."

def save_results(jp_analysis, jp_message, en_analysis, en_message):
    results = {
        "jp": {"analysis": jp_analysis, "message": jp_message},
        "en": {"analysis": en_analysis, "message": en_message}
    }
    with open("empathy_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nResults saved to empathy_results.json")

# デモ用データ
if __name__ == "__main__":
    # Windowsでのエンコーディング問題を回避
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    engine = EmpathyEngine()
    
    # テストケース1: 日本（言いたいけど言えない、設定に時間がかかっている）
    jp_logs = [
        {"action": "click_settings", "timestamp": "10:00:01"},
        {"action": "stay_settings", "duration_sec": 300},
        {"action": "cancel_settings", "timestamp": "10:05:01"}
    ]
    print("--- [JP Demo] Analying Japanese User Tension ---")
    jp_analysis = engine.analyze_interaction(jp_logs, culture="ja")
    print(json.dumps(jp_analysis, indent=2, ensure_ascii=False))
    print("\n[Preemptive Message (JP)]")
    jp_message = engine.generate_preemptive_message(jp_analysis, "佐藤様", culture="ja")
    print(jp_message)

    print("\n" + "="*50 + "\n")

    # テストケース2: 海外（効率が悪い、もっと早く動きたい）
    en_logs = [
        {"action": "run_automation", "status": "wait_queue", "timestamp": "11:00:01"},
        {"action": "refresh_dashboard", "count": 15, "timestamp": "11:05:01"}
    ]
    print("--- [EN Demo] Analyzing Western User Impatience ---")
    en_analysis = engine.analyze_interaction(en_logs, culture="en")
    print(json.dumps(en_analysis, indent=2, ensure_ascii=False))
    print("\n[Preemptive Message (EN)]")
    en_message = engine.generate_preemptive_message(en_analysis, "Mr. Smith", culture="en")
    print(en_message)
    
    # 結果を保存
    save_results(jp_analysis, jp_message, en_analysis, en_message)
