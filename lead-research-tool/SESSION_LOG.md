# SESSION_LOG.md — AETHERCORE lead-research-tool Session History
# EVERY SESSION MUST APPEND TO THIS FILE BEFORE ENDING
# Format: Session ID | Date | Summary | Tasks completed | Tasks remaining

---

## Session 1 — 2026-03-25
**Summary:** lead-research-toolをAETHERCORE向けに改修。スコアリングシグナルを産廃・建設業向け4条件に変更、営業メールテンプレートを最新版に更新、webappの業界選択を産廃業・建設業のセレクトボックスに変更。claude-context-guard導入によりセッション管理体制を構築。
**Tasks completed:**
- scoring.yaml を産廃・建設業向けシグナルに更新
- api/main.py にAETHERCORE向け営業テンプレートを埋め込み
- webapp/app/page.tsx のタイトル・業界選択をAETHERCORE仕様に変更
- claude-context-guard セーフガードファイル群を初期化
**Tasks remaining:** なし（初期改修完了）
**Decisions made:**
- スコア閾値70点を採用（70点以上が営業対象）
- 産廃/建設で別テンプレートを使用（同一APIエンドポイントで業界判定）
**Next session should start with:** `python -m uvicorn api.main:app --reload` で動作確認、実データでリスト収集テスト
