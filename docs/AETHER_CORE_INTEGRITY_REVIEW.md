# AETHER CORE 整合性・セキュリティレビュー

**対象**: `scripts/integrity_checker.py`, `scripts/safety_guardrails.py`  
**参照**: brain 内 `walkthrough.md`（本日の意思決定・作業フロー）

---

## 1. 結論サマリー

| 項目 | 状態 | 備考 |
|------|------|------|
| 書き込み前の永久バックアップ | ⚠️ ほぼ担保（1箇所ギャップ） | ループ内の `daily_stats.json` 直接書き込みにバックアップなし → 修正済み |
| 終了時のハッシュ検証 | ⚠️ 構造検証＋ハッシュ記録のみ | レジストリとの照合で「前回実行後の改ざん検知」を追加済み |
| セキュリティ観点 | ✅ 問題なし | パストラバーサル・権限・ログの扱いは適切 |

---

## 2. 永久バックアップの確認

### 2.1 実装（safety_guardrails.py）

- **`auto_backup(target_file_path)`**  
  書き込み前に `backups/PERMANENT/<sanitized_filename>/<filename>.<timestamp>.bak` に `shutil.copy2` でコピー。  
  上書き・削除しない設計で、永久保存に相当。
- **パス**: デコレータは `os.path.basename(target_file_path)` でディレクトリを無視し、`backups/PERMANENT/` は CWD 相対。  
  `run_automation.py` はプロジェクトルートで実行される想定のため、バックアップは `backups/PERMANENT/...` に格納される。

### 2.2 適用箇所

- **global_leads.json**: `GlobalDiscovery.update_leads_file` に `@auto_backup('global_leads.json')` → ✅
- **approval_queue.json**: `ApprovalQueue._save_queue` に `@auto_backup('approval_queue.json')` → ✅
- **leads_history.json**: `run_automation.py` の `_save_history_safely()` に `@auto_backup(history_file)` → ✅
- **daily_stats.json（最終保存）**: `_save_stats_safely()` に `@auto_backup(stats_file)` → ✅
- **daily_stats.json（ループ内）**: 送信実績の即時保存で **直接 `open(stats_file,'w')` + `json.dump`** → ❌ **バックアップなし**

### 2.3 修正内容

- `safety_guardrails.py` に **`ensure_permanent_backup(file_path)`** を追加（デコレータと同様の永久バックアップ処理）。
- `run_automation.py` のループ内で `daily_stats.json` を書き込む直前に **`ensure_permanent_backup(stats_file)`** を呼ぶよう変更。  
  → すべての書き込みで永久バックアップが取られるように統一。

---

## 3. 終了時のハッシュ検証

### 3.1 実装（integrity_checker.py）

- **`calculate_hash(file_path)`**: SHA-256 でファイルハッシュを計算。
- **`verify_json_structure(file_path, required_keys)`**: JSON の読み込みと必要キー検証。
- **`run_audit(target_files)`**: 各ファイルについて構造検証＋ハッシュ計算し、結果を返す。  
  **注意**: `config/integrity_hashes.json`（HASH_REGISTRY_FILE）は定義されているが、従来は未使用だった。

### 3.2 ギャップ

- 終了時に「ハッシュを計算してログ出力」はしているが、  
  **「前回確定した正と照合する」** 仕組みがなく、改ざん・破損の検知が不十分だった。

### 3.3 修正内容

- **`save_hashes_to_registry(results)`** を追加: 監査成功時に `results` のハッシュを `config/integrity_hashes.json` に保存。
- **`run_audit(..., verify_against_registry=False)`** を拡張:  
  `verify_against_registry=True` かつレジストリにエントリがあるファイルについて、現在のハッシュとレジストリのハッシュを照合。不一致なら FAILED。
- **run_automation.py**:
  - 終了時: 従来どおり `run_audit` → 成功時のみ **`save_hashes_to_registry(results)`** を実行し、その時点のハッシュを「確定値」として記録。
  - 必要に応じて、実行開始時などに `run_audit(..., verify_against_registry=True)` を呼ぶことで、前回終了時からの改ざん検知が可能。

これにより、「終了時にハッシュを確定し、次回以降そのハッシュで整合性を検証する」流れが明確になる。

---

## 4. セキュリティ観点のチェック

- **パストラバーサル**: バックアップ先は `os.path.basename` でサニタイズ済み。`integrity_checker` は指定パスのみ読むため問題なし。
- **権限**: バックアップ・レジストリはプロセス権限で作成。特権昇格の余地なし。
- **ログ**: ハッシュは先頭のみログ出力（`file_hash[:10]...`）。機密データの過剰露出なし。
- **ConsensusEngine / UratoriEngine**: 事実確認・合議はモック実装であり、外部API呼び出し時の認証・入力検証は別途必要（既知の前提）。

---

## 5. 運用上の注意

- **実行ディレクトリ**: `run_automation.py` はプロジェクトルートを CWD として実行すること。  
  そうでない場合、`important_files` の絶対パスと `backups/PERMANENT/` の相対パスが意図どおりに対応する。
- **初回実行**: レジストリが存在しない状態で `verify_against_registry=True` にすると、照合はスキップされる（ファイルが存在する場合のみハッシュ比較）。

---

## 6. AI起因リスクへの設計（流出・改ざん・消去）

**質問**: これらのプログラムは、AIによる重要データの流出・改ざん・データ消去などのミスが起こらないように設計されているか。

### 6.1 評価サマリー

| リスク | 設計状況 | 備考 |
|--------|----------|------|
| **重要データの流出** | ✅ 対策済み | APIキーは環境変数のみ。**PIIマスキング**（`pii_masker.py`）で LLM 送信前にメール・電話番号等を自動マスク。 |
| **改ざん** | ✅ 設計済み | 書き込み前永久バックアップ、終了時ハッシュ検証＋レジストリ記録、**開始時にレジストリ照合で改ざん検知**。 |
| **データ消去ミス** | ✅ 設計済み | 上書き前に必ずバックアップ。削除操作は ConsensusEngine で WARNING、本番コードにファイル削除はなし。 |

### 6.2 データ流出の防止

- **APIキー・認証情報**: `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`, `SMTP_PASSWORD` 等はすべて `os.getenv()` で取得。コードやログに平文で出さない。
- **ログ**: メール送信時は `To: {to_email}` 程度。本文・件名全文はログに出さない。ハッシュは先頭10文字のみ。
- **PIIマスキング（antigravity 対応済み）**: `scripts/pii_masker.py` を実装。LLM に送る直前に `sanitize_payload` でメールアドレス・電話番号・クレジットカード番号等を検知し `[email_MASKED]` 等に置換。`run_automation.py` のニッチ向けレポート生成では `safe_target = sanitize_payload(target)` を適用してから `report_gen.generate_report(safe_target)` を呼んでおり、機密情報の意図しない流出リスクを極小化している。

### 6.3 改ざんの防止

- 書き込み前の **永久バックアップ**（`@auto_backup` / `ensure_permanent_backup`）により、上書き前の状態が残る。
- 終了時の **run_audit** で JSON 構造検証＋ハッシュ計算。成功時は **save_hashes_to_registry** で `config/integrity_hashes.json` にハッシュを記録。
- **レジストリ連携の全自動化（antigravity 対応済み）**: 次回実行の**開始時**に `run_audit(..., verify_against_registry=True)` を実行。前回完了時から外部でデータが書き換えられていれば警告を出し、改ざん検知体制が一巡する。
- AIがファイルを直接書き換えるインターフェースはない（所定のスクリプトのみが JSON を書く）。

### 6.4 データ消去・誤上書きの防止

- **削除系**: `safety_guardrails.ConsensusEngine` は "delete" / "remove" を含むアクションを WARNING 扱い。本番コードに `os.remove` で重要データを消す処理はない（テスト用 `safety_guardrails` の `__main__` のみ）。
- **上書き**: 重要 JSON（global_leads, approval_queue, leads_history, daily_stats）はすべて、書き込み前にバックアップを取る設計に統一済み。消去ではなく「上書き」が起きても復旧可能。

### 6.5 誤送信・誤実行の防止（AI判断の暴走対策）

- **DRY_RUN**: 未設定・空の場合は **true とみなす**二重の安全弁。本番送信・Stripe 発行・OpenAI 呼び出しは DRY_RUN 時はモック。
- **REQUIRE_APPROVAL**: ニッチ向けメールは承認キュー経由にでき、オーナー承認後にのみ送信。
- **ギャップ**: 「通常のB2B/SNS営業」分岐（`run_automation.py` の else 節）では、送信前に **DRY_RUN** を明示的に見ていない。`AutoSender` の `SENDER_MOCK_MODE` と各モジュール内の DRY_RUN に依存しているため、**ニッチ分岐と通常分岐で挙動を揃える**なら、通常分岐でも「DRY_RUN のときは送信しない」と明示することを推奨。

### 6.6 その他

- **監査対象の拡大（antigravity 対応済み）**: `user_analytics.json` およびループ内で更新される `daily_stats.json` を、`important_files` に含め永久バックアップ（実行前スナップショット）および終了時のハッシュ検証・レジストリ記録の対象にした。開始時の改ざんチェックも同一リストで実施。
- **growth_reports / 各種ドラフト**: レポートや下書きの保存先はバックアップ対象外。必要なら対象ファイル一覧を拡張可能。

---

*レビュー実施日: 2026-03-15（walkthrough.md および最新コードに基づく）*
