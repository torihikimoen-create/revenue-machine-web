import logging
import os
from dotenv import load_dotenv

load_dotenv()

class SNSHunter:
    """
    SNSのプロフィールから「DM対応に悩んでいる」人を特定するエンジン。
    マーケットの不均衡（需要はあるが供給が追いたいていない状態）をFX同様に見抜きます。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def hunt_targets(self, platform: str, target_list: list = None):
        """
        特定のプラットフォームからターゲットを抽出。
        引数に target_list が与えられた場合はそれを使用し、なければモックを使用。
        """
        if target_list:
            self.logger.info(f"Ingesting {len(target_list)} external targets for {platform}.")
            qualified_targets = []
            for t in target_list:
                # 簡易的なフィルタリング（フォロワー数などがあれば）
                t['priority'] = "High" if t.get('followers', 0) > 1000 or t.get('issue') else "Medium"
                # プロフィール情報のマッピング（global_leads.json の形式に合わせる）
                refined_target = {
                    "username": t.get('name', t.get('username', 'unknown')),
                    "followers": t.get('followers', 0),
                    "bio": t.get('issue', t.get('bio', '')),
                    "issue_detected": t.get('issue', 'General outreach'),
                    "lang": t.get('lang', 'ja'),
                    "email": t.get('email'),
                    "sector": t.get('sector')
                }
                qualified_targets.append(refined_target)
            return qualified_targets

        # 本来は各SNSのSearch APIを使用 (モック)
        mock_profiles = [
            {
                "username": "@famous_creator",
                "followers": 50000,
                "bio": "YouTubeやってます！現在DMの返信はできません。お仕事はメールで。",
                "issue_detected": "DM対応のパンク",
                "lang": "ja"
            }
        ]
        
        qualified_targets = []
        for p in mock_profiles:
            if p['followers'] > 10000:
                p['priority'] = "High"
                qualified_targets.append(p)
                
        return qualified_targets

    def save_draft(self, target: dict, dm_text: str):
        """
        生成されたDM下書きをファイルとして保存。
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        draft_dir = os.path.join(base_dir, "drafts")
        os.makedirs(draft_dir, exist_ok=True)
        
        # ファイル名を安全にする
        safe_name = "".join(x for x in target['username'] if x.isalnum() or x in ('_', '-'))
        filename = f"{safe_name}_{target['lang']}.txt"
        filepath = os.path.join(draft_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"--- Target: {target['username']} ---\n")
            f.write(f"--- Issue: {target['issue_detected']} ---\n\n")
            f.write(dm_text)
            
        self.logger.info(f"Saved DM draft to {filepath}")
        return filepath
