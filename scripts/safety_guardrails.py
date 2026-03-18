import logging
import random
import functools
import re
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def auto_backup(target_file_path):
    """
    破壊的な操作の前にファイルをバックアップするデコレータ。
    永続的に保存し、過去のデータを上書き・削除しない。

    注意: 処理中の「中間状態」（メモリ上のみで未書き込みのデータ）は
    クラッシュ時に失われる。0.1% も失わない復旧には、重要処理の
    1件完了ごとの ensure_permanent_backup またはチェックポイント保存を推奨。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.path.exists(target_file_path):
                file_name = os.path.basename(target_file_path)
                backup_dir = os.path.join("backups", "PERMANENT", file_name.replace(".", "_"))
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                backup_path = os.path.join(backup_dir, f"{file_name}.{timestamp}.bak")
                
                import shutil
                shutil.copy2(target_file_path, backup_path)
                
                logger.info(f"[Safety] PERMANENT backup created for {file_name} at {backup_path}")
            else:
                logger.warning(f"[Safety] No file to backup at {target_file_path}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def ensure_permanent_backup(file_path):
    if not os.path.exists(file_path):
        return
    file_name = os.path.basename(file_path)
    backup_dir = os.path.join("backups", "PERMANENT", file_name.replace(".", "_"))
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = os.path.join(backup_dir, f"{file_name}.{timestamp}.bak")
    import shutil
    shutil.copy2(file_path, backup_path)
    logger.info(f"[Safety] PERMANENT backup created for {file_name} at {backup_path}")

def create_system_snapshot(paths_to_snap):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap_dir = os.path.join("backups", "prerun_snaps", f"snap_{timestamp}")
    os.makedirs(snap_dir, exist_ok=True)
    
    import shutil
    for path in paths_to_snap:
        if os.path.exists(path):
            target = os.path.join(snap_dir, os.path.basename(path))
            shutil.copy2(path, target)
            logger.info(f"[Safety] Pre-run snapshot created for {os.path.basename(path)}")

class UratoriEngine:
    """
    ハルシネーション（AIの嘘）を防ぐための「裏取り」実行エンジン。
    2026年3月の最新法的根拠に基づく厳格な検証を行う。
    """
    VERIFIED_LAWS = {
        "2024年問題": {"year": "2024", "desc": "建設・運送・医療の残業規制。2026年現在は人手不足による事業継続リスクが表面化し、倒産・取引停止事例が報告されている。"},
        "改正建設業法": {"year": "2025", "desc": "2025年4月全面施行。著しく短い工期の禁止、労務費適正化の遵守義務、中央建設業審議会による労務費基準の告示。"},
        "中小受託取引適正化法": {"year": "2026", "desc": "2026年1月施行。手形払いの原則廃止、買いたたき厳罰化、書面による取引条件の明示義務。"},
        "臨時介護報酬改定": {"year": "2026", "desc": "2026年4月施行予定の令和8年度改定。介護職員の処遇改善加算の一本化とさらなる上乗せ、財務状況の公表義務化。"},
        "育児介護休業法": {"year": "2025", "desc": "2025年4月/10月順次施行。3歳までのテレワーク努力義務、子どもの看護休暇の対象拡大。"},
        "電子帳簿保存法": {"year": "2024", "desc": "2024年1月完全義務化。電子取引データの出力書面による保存は不可。"},
        "手形廃止": {"year": "2026", "desc": "2026年までに全国の銀行・手形交換所での紙の手形・小切手の原則廃止。"},
        "システム標準化": {"year": "2026", "desc": "2026年3月末（2025年度末）が自治体20業務のシステム標準化・移行の最終期限。"},
        "虐待防止通報義務": {"year": "2025", "desc": "2025年4月施行の改正児童福祉法。施設内虐待の早期発見・通報体制の強化。"},
        "電子マニフェスト詳細化": {"year": "2027", "desc": "廃棄物処理法施行規則の改正予定。排出事業者の管理責任がさらに強化される見込み。"}
    }

    def __init__(self):
        self.logger = logging.getLogger("UratoriEngine")

    def verify_fact(self, content):
        violations = []
        found_claims = []
        sentences = re.split(r'[。！？\n]', content)

        for law_name, data in self.VERIFIED_LAWS.items():
            year = data['year']
            law_mentioned = False
            
            for sentence in sentences:
                if not sentence.strip(): continue
                if law_name in sentence:
                    law_mentioned = True
                    masked = sentence.replace(law_name, "[LAW]")
                    found_years = re.findall(r'20\d{2}', masked)
                    if found_years and year not in found_years:
                        violations.append(f"法的期限の誤認: {law_name} の記述において、正しくは {year}年 ですが文中に {found_years}年 が言及されています。")
            
            if law_mentioned:
                found_claims.append(law_name)
                if year not in content:
                    violations.append(f"施行年の欠落: {law_name} に関する記述がありますが、正しい施行年（{year}年）が記載されていません。")

        return {
            "verified": len(violations) == 0,
            "claims_detected": found_claims,
            "violations": violations,
            "risk_level": "CRITICAL" if violations else "NORMAL"
        }

class ConsensusEngine:
    """
    専門家AIによる合議制判定。法務チェックを最優先ガードレールとする。
    """
    def __init__(self):
        self.logger = logging.getLogger("ConsensusEngine")
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.experts = [
            {"name": "Legal Counsel", "role": "Compliance", "prompt": "あなたは超厳格な法務AIです。裏取りデータと1ミリでも矛盾があれば『即座に REJECTED』してください。嘘は許されません。"},
            {"name": "Brand Expert", "role": "Tone", "prompt": "ブランド責任者です。攻撃的な文言を排除してください。"},
            {"name": "Operations Expert", "role": "Efficiency", "prompt": "運営責任者です。実用的な提案かを判定してください。"}
        ]

    def get_consensus(self, content):
        uratori = UratoriEngine()
        fact_check = uratori.verify_fact(content)
        
        opinions = []
        for expert in self.experts:
            try:
                # 法務AIには裏取り結果を「神の宣告」として渡す
                extra = f"\n【裏取りによる法的事実】: {fact_check['violations'] if not fact_check['verified'] else '不備なし'}" if expert['name'] == "Legal Counsel" else ""
                
                # 法務AIが裏取りで不認定なら、AIの思考に関わらず入力を絞る
                prompt_suffix = "法的不備が1つでもあれば、問答無用で REJECTED にしてください。" if expert['name'] == "Legal Counsel" else ""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"{expert['prompt']}\n{extra}\n{prompt_suffix}\n必ず以下のJSON形式で回答してください。\n{{\"status\": \"APPROVED\"または\"REJECTED\", \"reason\": \"理由\"}}"},
                        {"role": "user", "content": f"提案内容:\n{content}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.0
                )
                import json
                res_data = json.loads(response.choices[0].message.content)
                status = res_data.get("status", "REJECTED")
                
                # 法務AIが裏取りで不認定、または施行年などの不整合を検知した場合、システム側で強制REJECT
                if expert['name'] == "Legal Counsel":
                    if not fact_check['verified'] or status == "REJECTED":
                        status = "REJECTED"
                        violation_msg = "\n".join(fact_check['violations'])
                        res_data["reason"] = f"【鉄壁ガードレール：強制リジェクト】以下の法的リスク/不備を検知しました:\n{violation_msg}\n{res_data.get('reason', '')}"

                opinions.append({"expert": expert['name'], "status": status, "message": res_data.get("reason", "")})
            except Exception as e:
                opinions.append({"expert": expert['name'], "status": "ERROR", "message": str(e)})

        is_safe = all(o['status'] == 'APPROVED' for o in opinions)
        return {
            "summary": "SAFE" if is_safe else "REJECTED",
            "opinions": opinions,
            "fact_checks": fact_check
        }
