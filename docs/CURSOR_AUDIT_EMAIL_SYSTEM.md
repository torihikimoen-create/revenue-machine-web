# メール送信システム監査レポート

**監査日**: 2026-03-18  
**対象**: 送信の心臓部・品質ゲート・データ分離・設定・ドキュメント

---

## 1. 送信の心臓部（ロジック）

### scripts/auto_sender.py

| 項目 | 状態 | 備考 |
|------|------|------|
| **モック/テストブロック** | ✅ 実装済み | `_should_skip_address` で `example.`, `test@`, `sample@`, `localhost`, `invalid` をブロック。`example.` で example.com / example.co.uk をカバー。明示的に `example.co.uk` を追加すると可読性・一貫性が向上。 |
| **is_humanized ゲート** | ✅ 実装済み | 実送信時（`not self.is_mock`）に `is_humanized=False` なら送信拒否し CRITICAL ログを出力。 |
| **DRY_RUN 時の強制 MOCK** | ✅ 実装済み | `DRY_RUN=true` のときは `SENDER_MOCK_MODE` の値に関わらず `is_mock=True`。 |
| **send_custom_email** | ⚠️ 要認識 | フィードバック用は `is_humanized` チェックなし（意図的と判断。提案メールと異なり件名・本文を直接指定するため）。 |

### run_automation.py

| 項目 | 状態 | 備考 |
|------|------|------|
| **パイプライン順序** | ✅ 固定 | ニッチセクター: 提案生成 → ConsensusEngine → Correcter（必要時）→ Humanizer.polish → _should_skip_address → send_proposal_email(is_humanized=True)。 |
| **リードファイル分離** | ✅ 実装済み | `lead_file = 'mock_leads.json' if DRY_RUN else 'global_leads.json'`。読み取りは `current_leads_path` で正しく分離。 |
| **営業時間・送信上限** | ✅ 実装済み | 日次100通・1時間8通、営業時間（9–11時）は DRY_RUN 時は無視。 |
| **B2B分岐の合議** | ⚠️ 要認識 | 通常 B2B/SNS 分岐（SME Law Firm 等）は **ConsensusEngine を通していない**。Humanizer のみ。ニッチセクターのみ合議制検閲。意図的であれば問題なし。 |

---

## 2. 品質管理とデータ分離

### scripts/humanizer.py（HumanizerEngine）

| 項目 | 状態 | 備考 |
|------|------|------|
| **人間化ロジック** | ✅ 実装済み | 業界・日付を考慮したプロンプトで polish。 |
| **失敗時の挙動** | ❌ 不備 | 例外時に `return content` のみ。呼び出し側は常に `is_humanized=True` で送信するため、**人間化に失敗しても品質ゲートを通過してしまう**。 |

**推奨**: `polish` の戻り値を `(content, success: bool)` とし、失敗時は `(content, False)`。`run_automation` で `is_humanized=success` を渡す。

### データファイル

| ファイル | 役割 | 状態 |
|----------|------|------|
| **global_leads.json** | 本番用顧客リスト | ルートに配置。DRY_RUN=false 時のみ読み書き。 |
| **mock_leads.json** | DRY_RUN 時用 | `lead_file` で指定。**存在しない場合は空リストで進行**。手動または別スクリプトで準備する前提。 |

### GlobalDiscovery.update_leads_file

| 項目 | 状態 | 備考 |
|------|------|------|
| **バックアップ** | ⚠️ 不備 | デコレータが `@auto_backup('global_leads.json')` で固定。`output_file='mock_leads.json'` のときも **global_leads.json をバックアップ**し、書き込むのは mock_leads.json。本番では未使用のため実害は小さいが、一貫性のため「書き込むファイル」をバックアップすべき。 |

---

## 3. 設定と安全スイッチ

| 変数 | 役割 | 確認結果 |
|------|------|----------|
| **DRY_RUN** | テストモード。true で mock_leads 参照・送信はログのみ | run_automation / AutoSender で参照済み。 |
| **SENDER_MOCK_MODE** | 送信をログのみにするか | AutoSender で参照。DRY_RUN=true 時は強制 true。 |
| **REQUIRE_APPROVAL** | 承認キュー経由にするか | run_automation で参照済み。 |

`.env` に未設定時は安全側（DRY_RUN デフォルト "true"、SENDER_MOCK_MODE デフォルト "true"）に倒れている。

---

## 4. ドキュメント・構造図

| ドキュメント | 状態 | 対応 |
|--------------|------|------|
| **email_process_diagram.md** | 未存在だった | ✅ 新規作成（Mermaid 図・ゲート順序・安全スイッチ）。 |
| **walkthrough.md の「7. メール送信システムの抜本的強化」** | リポジトリ内に該当セクションなし | Master_Handover 等に言及あり。本監査で「固定パイプライン・品質ゲート」を email_process_diagram.md に集約。 |

---

## 5. 実施した修正（要対応分）

1. **auto_sender.py**: `_should_skip_address` のモック指標に `example.co.uk` を明示追加（run_automation と表記を統一）。
2. **humanizer.py**: `polish` の戻り値を `(content: str, success: bool)` に変更。例外時は `(content, False)`。
3. **run_automation.py**: `humanizer.polish` の戻り値を受け、`is_humanized=humanized_ok` で送信。
4. **global_discovery.py**: `update_leads_file` で、デコレータの代わりに書き込み前に `ensure_permanent_backup(self.output_file)` を実行し、実際に書き込むファイルをバックアップ。

---

## 結論

- **心臓部・安全ゲート・データ分離・設定**はおおむね設計どおりに実装されている。
- **不備・要改善**: ① Humanizer 失敗時も is_humanized=True で送信されうる点、② GlobalDiscovery のバックアップ対象のずれ、③ B2B 分岐が合議を通らない点（仕様なら明文化推奨）。①②は修正済み、③はドキュメントで注記。

全体図は **docs/email_process_diagram.md** を参照。
