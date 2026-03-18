import os
import sys
import logging
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(current_dir, ".env"))

if current_dir not in sys.path:
    sys.path.append(current_dir)

from scripts.safety_guardrails import ConsensusEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegalStrictnessTest")

def test_legal_rejection():
    engine = ConsensusEngine()
    
    # テストケース1: 法的な年号の間違い（2024年問題を2026年問題と記述）
    bad_proposal = """
    2026年問題が差し迫る中、貴社の建設現場の効率化を提案します。
    改正建設業法の2024年施行に対応するため、早期の導入をご検討ください。
    """
    
    logger.info("--- Testing Case 1: Incorrect Law Dates ---")
    result = engine.get_consensus(bad_proposal)
    
    print(f"Summary: {result['summary']}")
    print(f"Verified: {result['fact_checks']['verified']}")
    for violation in result['fact_checks']['violations']:
        print(f"Violation Detected: {violation}")
    
    for opinion in result['opinions']:
        if opinion['expert'] == "Legal Counsel":
            print(f"Legal Counsel Opinion: {opinion['status']} - {opinion['message']}")

    # テストケース2: 攻撃的な文言
    aggressive_proposal = """
    AIを導入して他社を蹴落とし、市場を独占しましょう。
    2024年問題も、わが社のツールを使えば競合他社に圧倒的な差をつけられます。
    """
    
    logger.info("\n--- Testing Case 2: Aggressive Language ---")
    result = engine.get_consensus(aggressive_proposal)
    print(f"Summary: {result['summary']}")
    for opinion in result['opinions']:
        if opinion['expert'] == "Brand Expert":
            print(f"Brand Expert Opinion: {opinion['status']} - {opinion['message']}")

if __name__ == "__main__":
    test_legal_rejection()
