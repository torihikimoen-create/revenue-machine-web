import json
import os
import time
import hashlib


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _hash_email(email: str, salt: str = "") -> str:
    normalized = (email or "").strip().lower()
    h = hashlib.sha256()
    h.update((salt + normalized).encode("utf-8"))
    return h.hexdigest()


class EmailSuppressionList:
    """
    バウンス（不達）や拒否が発生した宛先を記録し、将来の送信を抑止する。
    Gmail BAN リスクの主因（存在しないアドレス大量送信）を最小化するための安全装置。
    """

    def __init__(self, storage_path: str, hash_salt: str = ""):
        self.storage_path = storage_path
        self.hash_salt = hash_salt or ""
        self._data = {"version": 1, "updated_at": None, "entries": {}}
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            # 破損していても送信システムを止めない（安全側としては“抑止なし”になる）
            self._data = {"version": 1, "updated_at": None, "entries": {}}

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self._data["updated_at"] = _now_iso()
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            # 送信処理は止めない
            pass

    def is_suppressed(self, email: str) -> bool:
        key = _hash_email(email, self.hash_salt)
        return key in (self._data.get("entries") or {})

    def add(self, email: str, reason: str, details: dict | None = None) -> None:
        key = _hash_email(email, self.hash_salt)
        entries = self._data.setdefault("entries", {})
        # 既存があっても理由を更新（最終時刻・回数を積む）
        entry = entries.get(key, {"first_seen_at": _now_iso(), "count": 0})
        entry["last_seen_at"] = _now_iso()
        entry["count"] = int(entry.get("count", 0)) + 1
        entry["reason"] = reason
        if details:
            entry["details"] = details
        entries[key] = entry
        self._save()

