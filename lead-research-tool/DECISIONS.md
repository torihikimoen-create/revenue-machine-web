# DECISIONS.md — AETHERCORE lead-research-tool Architectural Decisions Register
# NEVER CONTRADICT THESE DECISIONS WITHOUT EXPLICIT USER APPROVAL

---

## D001 — 2026-03-25
**Decision:** スコアリングシグナルを産廃・建設業の4条件に特化する
**Why:** 汎用的な動画広告スコアリングから、AETHERCOREのターゲット業界向けに特化することで精度を上げる
**How to apply:** 他業界のシグナルは追加しない。業界拡張は新フィールドを追加する形で対応する。

## D002 — 2026-03-25
**Decision:** 営業メールテンプレートはapi/main.pyに定数として埋め込む（外部ファイル不使用）
**Why:** テンプレートファイルの読み込みエラーリスクを排除。form_filler.pyと同期を手動で管理。
**How to apply:** テンプレート更新時はapi/main.pyのSANPAI_BODY/KENSETSU_BODYを直接編集する。

## D003 — 2026-03-25
**Decision:** スコア閾値は70点（LEAD_SCORE_THRESHOLD環境変数で変更可能）
**Why:** 4シグナル合計100点のうち、最低2条件（no_digital_manifest + small_company = 50点 or no_greenfile_system + has_contact_form = 50点）だけでは不十分。70点は中確度以上を担保する最低ライン。
**How to apply:** デフォルト70点を維持。下げる場合は増本さんの承認を得ること。

## D004 — 2026-03-25
**Decision:** DBファイルはapi/leads.dbに配置（SQLite）
**Why:** Renderや他の環境への移行時に簡単に差し替えられる。外部DBは不要（営業リスト規模は数千件以内）。
**How to apply:** 本格スケールアップ時はPostgreSQLへの移行を検討する。
