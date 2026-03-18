# 技術的信頼性証明書（Reliability Report）

**対象システム**: AETHER CORE 実務エンジン（SanpaiComplianceEngine）  
**検証日**: 2026-03-18  
**検証方法**: 自動テスト（`tests/test_execution_reliability.py`）および実務シミュレーション（`simulate_sanpai_work.py`）

---

## 保証している挙動

| 項目 | 内容 |
|------|------|
| **型安全性** | 数量が文字列（OCR 結果等）でも `analyze_manifest` で float に正規化され、`validate_compliance` で TypeError が発生しない。 |
| **必須項目** | マニフェストID・品目・交付日のいずれかが欠落した場合、CRITICAL として検知し `requires_human_review=True` とする。 |
| **負の数量** | 負の値は補完せず CRITICAL（NEGATIVE_QUANTITY）として検知する。 |
| **契約不備** | 契約なし・期限切れはマスターで補完せず、CRITICAL として検知する。 |
| **日付不正** | 契約期限の形式が不正な場合は HIGH（INVALID_DATE_FORMAT）で人間確認を求める。 |
| **空入力** | `None` や空入力ではクラッシュせず、INPUT_INVALID を返す。 |
| **自己修復** | マニフェストIDのみ、履歴に完全一致がある場合に補完する。契約・負数・日付欠落は補完しない。 |

---

## 自動テスト結果

```bash
python -m unittest tests.test_execution_reliability -v
```

- **test_critical_contract_missing**: 契約書なしを CRITICAL で検知 ✅  
- **test_expired_contract**: 期限切れ契約を CRITICAL で検知 ✅  
- **test_quantity_as_string_no_type_error**: 数量が文字列でも数値として検証 ✅  
- **test_missing_required_fields_critical**: 必須項目欠損で CRITICAL ✅  
- **test_negative_quantity_rejected**: 負の数量で CRITICAL ✅  
- **test_invalid_expiry_date_format_high_severity**: 日付形式不正で HIGH ✅  
- **test_empty_input_graceful_handling**: 空入力で INPUT_INVALID ✅  

---

## 実務シミュレーション

`python simulate_sanpai_work.py` により、意地悪な不備データ（契約切れ・契約なし・負の値・ID欠落・日付欠落・異常物量等）を一括投入し、すべての重大不備が「不備あり (要確認)」として検知され、合格件のみが報告書に含まれることを確認している。結果は `docs/artifacts/simulation_result.md` に出力される。

---

## 参照

- 監査の結論・修正内容: [cursor_audit_report.md](cursor_audit_report.md)  
- 詳細監査: [CURSOR_AUDIT_EXECUTION_RELIABILITY.md](CURSOR_AUDIT_EXECUTION_RELIABILITY.md)  
- シミュレーション結果: [artifacts/simulation_result.md](artifacts/simulation_result.md)
