import sys
import os
import logging

# プロジェクトルートを追加
sys.path.append(os.getcwd())

from scripts.auto_sender import AutoSender

logging.basicConfig(level=logging.INFO)

def test_subjects():
    sender = AutoSender()
    # モックモード強制
    sender.is_mock = True
    
    test_cases = [
        {"username": "テスト介護施設", "sector": "Nursing", "email": "nursing@real-test.jp"},
        {"username": "テスト建設会社", "sector": "Construction", "email": "const@real-test.jp"},
        {"username": "テスト産廃業者", "sector": "IndWaste", "email": "waste@real-test.jp"},
        {"username": "テスト保育園", "sector": "Childcare", "email": "child@real-test.jp"},
    ]
    
    print("\n--- Testing Default Personalized Subjects ---")
    for target in test_cases:
        sender.send_proposal_email(target, "本文テスト")

    print("\n--- Testing AI Generated Subject (Dictionary Input) ---")
    ai_payload = {
        "subject": "【緊急】2026年法改正に伴う事務負担をゼロにするAI特別対談のご案内",
        "content": "AIが生成した本文です。"
    }
    sender.send_proposal_email(test_cases[0], ai_payload)

if __name__ == "__main__":
    test_subjects()
