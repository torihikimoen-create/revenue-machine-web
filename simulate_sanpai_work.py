import logging
import json
import os
from datetime import datetime
from scripts.industry_engines.sanpai_engine import SanpaiComplianceEngine

# ログ設定を簡潔にする
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def simulate_real_work():
    engine = SanpaiComplianceEngine()
    
    # 1. 顧客から預かった実務データ（マニフェスト10件分のシミュレーション）
    manifest_data_list = [
        {"id": "M001", "type": "廃プラスチック類", "qty": 1.2, "unit": "t", "date": "2026-03-15", "has_contract": True, "contract_expiry": "2027-12-31"},
        {"id": "M002", "type": "廃酸", "qty": 0.5, "unit": "t", "date": "2026-03-15", "has_contract": True, "contract_expiry": "2027-12-31"},
        {"id": "M003", "type": "燃え殻", "qty": "2.0", "unit": "t", "date": "2026-03-16", "has_contract": True, "contract_expiry": "2027-12-31"}, # 型不整合(数値文字列)
        {"id": "M004", "type": "医療廃棄物", "qty": 0.1, "unit": "t", "date": "2026-03-16", "has_contract": True, "contract_expiry": "2026-03-10"}, # 契約切れ
        {"id": "M005", "type": "汚泥", "qty": 15.0, "unit": "t", "date": "2026-03-17", "has_contract": False, "contract_expiry": None}, # 契約なし
        {"id": "M006", "type": "廃油", "qty": -1.0, "unit": "t", "date": "2026-03-17", "has_contract": True, "contract_expiry": "2027-12-31"}, # 負の値
        {"id": "M007", "type": "謎の物体", "qty": 0.3, "unit": "t", "date": "2026-03-18", "has_contract": True, "contract_expiry": "2027-12-31"}, # 標準外品目
        {"id": None, "type": "廃プラスチック類", "qty": 0.8, "unit": "t", "date": "2026-03-18", "has_contract": True, "contract_expiry": "2027-12-31"}, # ID欠落
        {"id": "M009", "type": "廃アルカリ", "qty": 1200.0, "unit": "t", "date": "2026-03-18", "has_contract": True, "contract_expiry": "2027-12-31"}, # 異常な物量
        {"id": "M010", "type": "燃え殻", "qty": 0.5, "unit": "t", "date": None, "has_contract": True, "contract_expiry": "2027-12-31"}, # 日付欠落
    ]

    print(f"\n{'='*60}")
    print(f"  Practical Work Simulation: Batch Manifest Audit (N={len(manifest_data_list)})")
    print(f"{'='*60}\n")

    # Markdownレポート用のバッファ
    md_report = []
    md_report.append("# 実務遂行シミュレーション結果報告書")
    md_report.append(f"\n実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_report.append("\n## 処理対象データの一括精査結果")
    md_report.append("\n| ID | 判定 | リスク検知内容 |")
    md_report.append("| :--- | :--- | :--- |")

    processed_items = []
    compliance_passed_count = 0
    high_risk_count = 0

    for raw in manifest_data_list:
        # 1. 解析 (型正規化)
        analyzed = engine.analyze_manifest(raw)
        
        # 2. バリデーション (鉄壁ガード)
        result = engine.validate_compliance(analyzed)
        
        # 判定ラベルの作成
        status_label = "合格" if result["is_compliant"] else "不備あり"
        if result["requires_human_review"]:
            status_label += " (要確認)"
            high_risk_count += 1
        
        # 課題内容の集約
        issue_msgs = "<br>".join([i['message'] for i in result['issues']]) if result['issues'] else "なし"
        
        # ログ出力 (ASCII安全)
        print(f"ID: {str(analyzed['manifest_id']):<6} | Status: {status_label}")
        
        # Markdown行の追加
        md_report.append(f"| {analyzed['manifest_id']} | {status_label} | {issue_msgs} |")

        if result["is_compliant"]:
            compliance_passed_count += 1
            processed_items.append(analyzed)

    # 3. 自治体提出用レポートの生成
    report = engine.generate_government_report(processed_items)
    
    summary_section = f"""
## 処理サマリー
- **総処理件数**: {len(manifest_data_list)}件
- **法規準拠(合格)**: {compliance_passed_count}件
- **重大リスク検知**: {high_risk_count}件 (すべて自動停止・人間確認へ)
- **生成レポート**: {report['report_type']}
- **合計数量**: {report['summary']['total_quantity']} {report['summary']['unit']}
"""
    md_report.append(summary_section)

    print(f"\n{'-'*60}")
    print(f"  Simulation Summary")
    print(f"{'-'*60}")
    print(f"Total: {len(manifest_data_list)}")
    print(f"Passed: {compliance_passed_count}")
    print(f"High Risk: {high_risk_count}")
    print(f"{'-'*60}\n")
    
    # Markdown報告書をアーティファクトとして保存（リポジトリ内 docs/artifacts）
    repo_root = os.path.dirname(os.path.abspath(__file__))
    artifact_dir = os.path.join(repo_root, "docs", "artifacts")
    os.makedirs(artifact_dir, exist_ok=True)
    md_path = os.path.join(artifact_dir, "simulation_result.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_report))

    # JSONレポートを保存
    json_path = os.path.join(artifact_dir, "simulation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"Success: Simulation results saved to {md_path}\n")

if __name__ == "__main__":
    simulate_real_work()
