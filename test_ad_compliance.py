import sys
import os
import json

# プロジェクトルートを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from scripts.industry_engines.ad_compliance_engine import AdComplianceEngine
from scripts.humanizer import HumanizerEngine

def test_experiment():
    engine = AdComplianceEngine()
    humanizer = HumanizerEngine()
    
    test_copies = [
        "このサプリを飲めば、絶対に10kg痩せて、病気も全て治ります。日本一の究極ダイエットです。",
        "年齢より若返る魔法のような美容液。アンチエイジング効果でシワが完全に消えます。",
        "毎日の潤いをサポートする、こだわりの国産成分を配合した美容液です。"
    ]
    
    output_lines = []
    output_lines.append("="*60)
    output_lines.append("  Ad Compliance AI Agent: MVP Test Simulation")
    output_lines.append("="*60 + "\n")
    
    for i, copy in enumerate(test_copies):
        output_lines.append(f"--- [Test {i+1}] Case ---")
        output_lines.append(f"Input: {copy}\n")
        
        # 1. リーガルチェック
        result = engine.check_copy(copy)
        
        output_lines.append(f"Safe Status: {'PASSED' if result['is_safe'] else 'RISKY'}")
        output_lines.append(f"Confidence Score: {result['confidence_score']}")
        
        if result['issues']:
            output_lines.append("Detected Legal Issues:")
            for issue in result['issues']:
                output_lines.append(f"  - [{issue['severity']}] {issue['law']}: {issue['reason']}")
                output_lines.append(f"    Suggestion: {issue['suggestion']}")
        
        # 2. リライト
        if result['requires_human_review']:
            output_lines.append("\nRefining with Humanizer AI (Safety-First)...")
            
            # 抽出された NG パターンを禁止語句として明示
            forbidden_patterns = [issue['detected_pattern'] for issue in result['issues']]
            legal_reasons = "\n".join([f"- {i['detected_pattern']}: {i['reason']}" for i in result['issues']])
            
            # 指示文の強化
            instructions = f"""
【最重要：法的コンプライアンス遵守】
以下の文章には、薬機法・景表法上の重大なリスクが含まれています。
以下の「禁止表現」を絶対に含めず、かつ指摘された「法的リスク」を完全に解消した上で、
商品の魅力（ベネフィット）を引き出すプロのコピーライティングに昇華させてください。

■禁止表現（絶対に使用しないでください）:
{forbidden_patterns}

■指摘された法的リスク:
{legal_reasons}

■元の文章:
{copy}
"""
            # Humanizer.polish の引数を拡張するか、プロンプトを差し替える必要があるが、
            # 現状のpolishメソッドは sector を受け取るので、そこに乗せるか、一時的にプロンプトを結合する。
            # ここでは実験のため、content 自体を指示文付きの構造化データにして渡す。
            
            polished, success = humanizer.polish(instructions, sector="Beauty/Health", current_date="2026-03-18", mode="ad_copy")
            
            final_check = engine.check_copy(polished)
            
            output_lines.append(f"Polished Text: {polished}")
            output_lines.append(f"Final Integrity Status: {'SECURE' if final_check['is_safe'] else 'STILL HAS RISKS'}")
            if not final_check['is_safe']:
                output_lines.append("Remaining Issues:")
                for i in final_check['issues']:
                    output_lines.append(f"  - {i['detected_pattern']}: {i['reason']}")
        else:
            output_lines.append("\nText is clean. No rewrite required.")
            
        output_lines.append("-" * 60 + "\n")

    # ファイルに書き出し
    with open('test_ad_results.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))
    print("Test results saved to test_ad_results.txt")

if __name__ == "__main__":
    test_experiment()
