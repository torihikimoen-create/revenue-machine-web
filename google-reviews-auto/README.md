# Google口コミ返信自動化システム (Phase 1)

## 概要
Google Business Profileに投稿された口コミを検知し、AI（LLM）を用いて店舗のブランドイメージに沿った最適な返信を自動生成・投稿するシステムです。

## ターゲット収益
- 月額：30,000円 / 1店舗

## 技術構成
- **Backend**: Python 3.10+
- **AI**: OpenAI API (GPT-4o)
- **API**: Google Business Profile API
- **Infrastructure**: 定時実行（Cloud Functions / Lambda 予定）

## 実装ファイルの役割
- `src/app.py`: メインロジック（定期実行およびAPI調整）
- `src/analyzer.py`: 口コミの感情・内容分析
- `src/generator.py`: LLMを用いた返信文生成
- `config/settings.yaml`: 店舗ごとのトーン＆マナー設定
