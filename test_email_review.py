import os
import json
from scripts.approval_dashboard import ApprovalQueue

def test_enhanced_review():
    queue = ApprovalQueue()
    
    # 意図的に不備のあるメール（宛名なし、短い）
    bad_email = "Hello, buy our product now."
    print("--- Testing BAD Email Review ---")
    queue.add_task("test_client", "Tech", "EmailProposal", bad_email)
    
    # 最新のタスクを確認
    with open("approval_queue.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    last_task = data[-1]
    print(f"Task ID: {last_task['task_id']}")
    print(f"Status: {last_task['status']}")
    for op in last_task['consensus']['opinions']:
        if op['expert'] == "Brand Expert":
            print(f"Brand Expert Opinion: {op['status']} - {op['message']}")

    # 適切なメール（宛名あり、十分な長さ）
    good_email = "Dear Nursing Home Manager,\nWe have analyzed your efficiency and created a custom report for your facility. Please check the attached file..."
    print("\n--- Testing GOOD Email Review ---")
    queue.add_task("test_client_good", "Nursing", "EmailProposal", good_email)
    
    with open("approval_queue.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    last_task = data[-1]
    print(f"Task ID: {last_task['task_id']}")
    print(f"Status: {last_task['status']}")
    for op in last_task['consensus']['opinions']:
        if op['expert'] == "Brand Expert":
            print(f"Brand Expert Opinion: {op['status']} - {op['message']}")

if __name__ == "__main__":
    test_enhanced_review()
