# CLAUDE.md — AETHERCORE lead-research-tool
# This file is auto-read by Claude Code at every session start.
# Last updated: 2026-03-25

## プロジェクト概要
- プロジェクト名：AETHERCORE lead-research-tool
- 用途：産廃・建設業向け営業リスト自動収集ツール
- オーナー：増本友貴（AETHERCORE）
- 詳細はSESSION_LOG.md / TASK_REGISTRY.md / DECISIONS.mdを参照

## CRITICAL: READ THESE FILES FIRST BEFORE ANY WORK

1. **`SESSION_LOG.md`** — 過去セッションの作業履歴。必ず最初に読む。
2. **`TASK_REGISTRY.md`** — 全タスクと状態。新タスク作成前に確認。
3. **`DECISIONS.md`** — 設計判断の記録。明示的承認なしに矛盾した行動は不可。
4. **`FEATURE_LIST.json`** — 全機能のpass/failトラッカー。
5. **`COMMENTS.md`** — 増本さんの発言ログ（削除禁止）。
6. **`plans/`** — 過去セッションのアーカイブ済み計画。直近3件を全文読む。

## DROPPING TASKS IS ABSOLUTELY UNACCEPTABLE

タスクを落とすことはプロジェクトの完全失敗を意味する。作成したすべてのタスクは `TASK_REGISTRY.md` にタイムスタンプ付きで記録する。セッション内に完了できないタスクは `pending` として残す。

セッション終了前・コンテキスト上限前に必ずセッションログとタスクレジストリを更新する。

## PRESERVE USER COMMENTS — MANDATORY

増本さんの発言はすべて `COMMENTS.md` にタイムスタンプ・セッションIDと共に記録する。アクション済みになったコメントは削除可。

## USER AUDITS YOUR WORK

増本さんはいつでも `/audit` を呼べる。すべてのタスクはplan・decision・commentに追跡可能でなければならない。

## プロジェクト仕様

### スコアリングシグナル（config/scoring.yaml）
- `no_digital_manifest` (+30) — マニフェスト電子化未対応（産廃業向け）
- `no_greenfile_system` (+30) — グリーンファイル電子化未対応（建設業向け）
- `small_company` (+20) — 中小企業（上場なし）
- `has_contact_form` (+20) — お問い合わせフォームあり
- 合計100点満点。70点以上を営業対象とする。

### 対応業界
- 産廃業（主ターゲット）
- 建設業（副ターゲット）

### 営業メールテンプレート
- 産廃業：件名「産廃マニフェスト管理をAIで自動化するサービスのご案内」
- 建設業：件名「安全書類の確認作業をAIで自動化するサービスのご案内」
- 本文は api/main.py の `SANPAI_BODY` / `KENSETSU_BODY` 定数を参照

### 料金（2026-03-25現在）
- 無料診断：登録から7日間 または 5回使用後（1回3枚まで）
- 月額プラン：14,800円（税込）／枚数・回数制限なし

## Git Conventions

- コミットは `S{session}-{sequence}_{short-description}` タグ付き
  - 例: `S1-001_add-scoring`, `S1-002_fix-db-migration`
  - セッション番号はSESSION_LOG.mdから取得、sequenceはセッション内で001から
  - `git tag "S{session}-{seq}_{desc}" HEAD` でタグ付け
  - `git push && git push --tags` で毎回プッシュ
- 修正コメントは `<!-- AMENDMENT vX.Y (YYYY-MM-DD): description -->` 形式

## Plan Archiving

実行済みの計画は `plans/S{session}-{seq}_{description}.md` にアーカイブする。

## Itemisation Protocol

ITEMISATION: enabled

コードブロックに階層番号を付与してセクション参照を可能にする。`/itemise` で適用。
無効化する場合は上の行を `ITEMISATION: disabled` に変更する。

## 連絡先・事業者情報

- 事業者名：AETHERCORE
- 代表：増本 友貴
- メール：torihikimoen@gmail.com
- TEL（携帯）：070-9001-6242 ※営業文章はこちらを使用
- TEL（固定）：0955-73-1130 ※コンビニ払い審査用のみ
- ホームページ：https://torihikimoen-create.github.io/revenue-machine-web/

## フォルダ構成・インフラ情報

### メインプロジェクト `C:\Users\himic\Desktop\revenue-machine\`
- `form_filler.py`      # 営業フォーム自動送信
- `sent_list.csv`       # 送信履歴
- `followup_reminder.py`# フォローアップ管理
- `list_collector.py`   # 営業リスト自動収集
- `test_bot.py`         # 自動テスト
- `line_bot.py`         # 産廃ボット
- `green_bot.py`        # 建設ボット
- `.env`                # 環境変数

### lead-research-tool `C:\Users\himic\.gemini\antigravity\scratch\business-automation\lead-research-tool\`

### Renderデプロイ
- 産廃ボット：https://aether-sanpai-bot.onrender.com
- 建設ボット：https://aether-green-bot.onrender.com

### LINE
- 産廃：@315yriby
- 建設：@591yxdrx

### GitHub
- https://github.com/torihikimoen-create/revenue-machine-web
