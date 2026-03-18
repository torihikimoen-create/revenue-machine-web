# Cursor 向け実装チェック依頼書 (AETHER CORE 専門エンジン)

Antigravity によって実装された「産廃特化型エンジン」および関連する安全策について、Cursor での精密なコードレビューと検証を依頼します。

## 1. チェック対象ファイル
- `scripts/industry_engines/sanpai_engine.py` (新規)
- `run_automation.py` (統合箇所)
- `scripts/safety_guardrails.py` (専門AIの合議ロジック)

## 2. カーソルへの依頼事項

### A. 専門的ロジックの正確性 (Professional Accuracy)
- [ ] `sanpai_engine.py` の `validate_compliance` 関数において、廃棄物処理法の一般的な罰則規定（無契約委託など）に対する警告メッセージが、実務的に妥当なトーンで記述されているか。
- [ ] 行政報告書生成ロジック (`generate_government_report`) が、将来的な Excel 出力等に耐えうるクリーンなデータ構造になっているか。

### B. 安全性とデータ整合性 (Security & Integrity)
- [ ] `run_automation.py` 内で、機密情報（メールアドレス等）が `sanitize_payload` を通さずに外部API（LLM等）に渡されている箇所がないか、再度静的解析を行ってください。
- [ ] `integrity_checker.py` との連携により、専門エンジンの出力が不正な場合にシステム全体を停止させる「フェイルセーフ」が機能しているか。

### C. ブランドイメージとUX (Brand & Copywriting)
- [ ] 提案メールに挿入される「事前監査結果」の文言が、信頼感を与えつつ、顧客の不安を煽りすぎない（誠実なビジネスパートナーとしての）表現になっているか。

## 3. 検証実行の推奨コマンド
Cursor のターミナルで以下を実行し、エンジンが期待通りに動作するか直接確認してください。
```powershell
# エンジンの単体テスト（エンコーディング不備がないか確認）
python scripts/industry_engines/sanpai_engine.py

# 統合環境のテスト実行（DRY_RUNモード）
$env:DRY_RUN="true"
python run_automation.py
```

---
以上の項目について、実務レベルでの「粗探し」を行い、改善案があれば直接コードに反映してください。
