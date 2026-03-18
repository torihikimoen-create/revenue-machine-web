import os
import json
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrityChecker")

HASH_REGISTRY_FILE = "config/integrity_hashes.json"

def calculate_hash(file_path):
    """ファイルの内容からSHA-256ハッシュを計算する"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_json_structure(file_path, required_keys=None):
    """JSONファイルが読み込み可能で、必要なキーが含まれているか検証する"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 基本的な型チェック（空でないこと）
        if data is None:
            return False, "Data is None"
        
        # 構造の検証
        if required_keys:
            if isinstance(data, list):
                if not all(all(k in item for k in required_keys) for item in data if isinstance(item, dict)):
                    return False, f"Missing required keys in list items: {required_keys}"
            elif isinstance(data, dict):
                if not all(k in data for k in required_keys):
                    return False, f"Missing required keys in dictionary: {required_keys}"
        
        return True, "Structure is valid"
    except json.JSONDecodeError as e:
        return False, f"JSON Decode Error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def run_audit(target_files, verify_against_registry=False):
    """
    指定されたファイル群の整合性を一括チェックする。
    target_files: list of tuples (file_path, required_keys)
    verify_against_registry: True の場合、config/integrity_hashes.json に記録されたハッシュと照合する。
    """
    logger.info("--- Starting Data Integrity Audit ---")
    registry = {}
    if verify_against_registry and os.path.exists(HASH_REGISTRY_FILE):
        try:
            with open(HASH_REGISTRY_FILE, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load hash registry: {e}")

    all_passed = True
    results = []

    for file_path, keys in target_files:
        if not os.path.exists(file_path):
            logger.warning(f"File not found, skipping: {file_path}")
            continue

        is_valid, msg = verify_json_structure(file_path, keys)
        file_hash = calculate_hash(file_path)

        # レジストリと照合（正規化パスでキー取得）
        norm_path = os.path.normpath(file_path)
        if verify_against_registry and norm_path in registry:
            if registry[norm_path] != file_hash:
                is_valid = False
                msg = f"Hash mismatch vs registry (possible tampering). Expected prefix: {registry[norm_path][:10]}..."
                all_passed = False

        status = "PASSED" if is_valid else "FAILED"
        if not is_valid:
            all_passed = False

        logger.info(f"Audit Result for {os.path.basename(file_path)}: {status} ({msg}) | Hash: {file_hash[:10]}...")
        results.append({
            "file": file_path,
            "valid": is_valid,
            "message": msg,
            "hash": file_hash
        })

    if all_passed:
        logger.info("✅ ALL INTEGRITY CHECKS PASSED.")
    else:
        logger.error("❌ INTEGRITY AUDIT FAILED. CRITICAL DATA CORRUPTION POSSIBLE.")

    return all_passed, results


def save_hashes_to_registry(results):
    """
    監査結果のハッシュを config/integrity_hashes.json に保存する。
    次回 run_audit(verify_against_registry=True) で改ざん検知に利用する。
    """
    registry = {}
    for r in results:
        norm_path = os.path.normpath(r["file"])
        registry[norm_path] = r["hash"]
    os.makedirs(os.path.dirname(HASH_REGISTRY_FILE) or ".", exist_ok=True)
    with open(HASH_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    logger.info(f"Hash registry updated: {HASH_REGISTRY_FILE}")

if __name__ == "__main__":
    # テスト実行
    files_to_check = [
        ("global_leads.json", []),
        ("approval_queue.json", []),
        ("leads_history.json", [])
    ]
    run_audit(files_to_check)
