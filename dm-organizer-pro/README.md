# SNS未返信DM一括整理システム (Phase 2)

## 概要
Instagram, X (Twitter), LinkedIn, Facebookなどの複数のSNSアカウントに届くダイレクトメッセージ（DM）を一括収集し、AIが重要度や内容を自動分類・整理するシステムです。

## ターゲット収益
- 月額：50,000円 / 1社（またはインフルエンサー）

## コア機能
1. **Multi-Channel Collector**: 各SNSプラットフォームから未読DMをポーリング。
2. **AI Classifier**: LLM (GPT-4) を用いて「至急の問い合わせ」「一般的な挨拶」「スパム・営業」を自動判定。
3. **Draft Reply**: メッセージ内容に合わせた返信の下書きを生成。
4. **Notification**: 重要なメッセージのみをSlackやDiscordに即時通知。

## 技術スタック
- Python, OpenAI API, 各種SNS API連携モジュール
