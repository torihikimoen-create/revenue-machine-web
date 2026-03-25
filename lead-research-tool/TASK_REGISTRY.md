# TASK_REGISTRY.md — AETHERCORE lead-research-tool Permanent Task Log
# EVERY TASK EVER CREATED MUST BE LOGGED HERE WITH A TIMESTAMP
# DROPPING TASKS IS ABSOLUTELY UNACCEPTABLE
# Status: done | in-progress | pending | blocked | re-queued

---

## T001 — 2026-03-25 — done
**Task:** scoring.yaml を産廃・建設業向け4シグナルに変更
**Session:** 1
**Result:** no_digital_manifest(30) / no_greenfile_system(30) / small_company(20) / has_contact_form(20) に更新

## T002 — 2026-03-25 — done
**Task:** api/main.py にAETHERCORE向け営業メールテンプレートを埋め込み
**Session:** 1
**Result:** SANPAI_BODY / KENSETSU_BODY 定数として実装、outreach_draft エンドポイントで業界判定

## T003 — 2026-03-25 — done
**Task:** webapp/app/page.tsx をAETHERCORE仕様に更新
**Session:** 1
**Result:** タイトル変更・業界セレクトボックス・sender情報をAETHERCORE名義に変更

## T004 — 2026-03-25 — pending
**Task:** SerpAPI連携の実動作確認（SERPAPI_KEY設定後）
**Session:** —
**Note:** SERPAPI_KEYが未設定の場合はseed-generatorモードで動作する。実データ収集には要設定。

## T005 — 2026-03-25 — pending
**Task:** webapp を `npm run dev` で起動しブラウザ動作確認
**Session:** —
**Note:** webapp/ディレクトリで `npm install && npm run dev` を実行

## T006 — 2026-03-25 — pending
**Task:** sent_list.csvとの統合（既存form_filler.pyの送信履歴と連携）
**Session:** —
**Note:** revenue-machine/sent_list.csv と leads.db の重複排除が必要か検討
