# AETHER CORE | 自律型ビジネス・オートメーション・エンジン

## 概要
AETHER COREは、AI「クアッドコア・エンジン」を駆使し、B2Bリードの発見から提案書の生成、個別最適化されたメール送信までを全自動で行う帝国構築システムです。

## プロジェクト構造
- `scripts/`: メインロジック（レポート生成、メール送信、リード発見など）
- `config/`: システム設定
    - `sector_data.json`: **【重要】** 業界別のインサイト、危機シナリオ、メール件名、送信者名を管理。非エンジニアでもここを編集することでアプローチ内容を微調整可能。
- `growth_reports/`: AIが生成した個別の提案書（TXT形式）の保存先。
- `index.html` / `tokushoho.html` / `terms.html` / `privacy.html`: ブランド統一されたLPおよび法的文書。

## 運用・メンテナンス
### アプローチ文面の調整
`config/sector_data.json` を編集してください。以下の項目が調整可能です。
- `crisis_scenarios`: 業界ごとの「生存リスク」の記述
- `sector_insights_ja / en`: レポート生成に使用される市場背景知識
- `sender_names`: 業界ごとに切り替える「最も信頼される送り主」の肩書き
- `sector_email_subjects`: AI個別件名が生成されなかった場合のデフォルト件名

### 安全設計
- `SENDER_MOCK_MODE=true` (環境変数/auto_sender.py): 実際のメール送信を遮断し、ログ出力のみを行います。
- `DRY_RUN=true` (環境変数/run_automation.py): 全エンジンのAPI消費を抑制し、安全にサイクルを確認できます。

## 法的準拠
すべての送信メールには、`LP_BASE_URL` に基づく「特定商取引法に基づく表記」へのリンクが自動的に付与されます。
