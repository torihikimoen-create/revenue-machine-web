import os
import hashlib
import logging

class FileAnalyzer:
    """
    ファイルシステムの現況を分析し、リネーム候補を抽出するエンジン。
    FXのボラティリティ検出と同様、データの「歪み」を見つけ出します。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_file_list(self, directory: str):
        """パスを再帰的にスキャンし、ファイル情報を取得する。"""
        files_info = []
        for root, _, files in os.walk(directory):
            for name in files:
                path = os.path.join(root, name)
                files_info.append({
                    "original_name": name,
                    "full_path": path,
                    "ext": os.path.splitext(name)[1],
                    "hash": self._get_hash(path)
                })
        return files_info

    def _get_hash(self, path: str):
        """重複検知用のファイルハッシュ計算。"""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def suggest_new_name(self, file_info: dict, rule_config: dict):
        """
        AIによる新ファイル名の提案（モック版）。
        本来はLLMが内容（OCR結果等）を見て命名します。
        """
        # 命名ルール例: [日付]_[会社名]_[内容].[拡張子]
        # 現在はファイル名からの推測ベース
        name = file_info['original_name']
        prefix = rule_config.get('prefix', 'ORG')
        
        # 簡易的なクリーンアップ
        clean_name = name.replace(" ", "_").replace("のコピー", "").replace("(1)", "")
        return f"{prefix}_{clean_name}"
