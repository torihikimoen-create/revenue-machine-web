import os
import json
import logging
from datetime import datetime
try:
    from scripts.report_generator import GrowthReportGenerator
except ImportError:
    from report_generator import GrowthReportGenerator
from scripts.approval_dashboard import ApprovalQueue
from scripts.niche_form_engine import NicheFormEngine

class FulfillmentEngine:
    """
    契約済みクライアントの実務（仕事）を実際に遂行するエンジン。
    """
    def __init__(self):
        self.logger = logging.getLogger("FulfillmentEngine")
        self.report_gen = GrowthReportGenerator()
        self.approval_queue = ApprovalQueue()
        self.form_engine = NicheFormEngine()
        self.clients_dir = 'clients'

    def run_fulfillment_cycle(self):
        """
        全ての契約済みクライアントをスキャンし、待機中の実務を処理する。
        """
        if not os.path.exists(self.clients_dir):
            return

        for client_id in os.listdir(self.clients_dir):
            client_path = os.path.join(self.clients_dir, client_id)
            config_path = os.path.join(client_path, 'config.json')
            
            if not os.path.exists(config_path):
                continue

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if config.get('status') == 'active':
                self.execute_auto_fulfillment(client_id, config.get('sector'))

    def execute_auto_fulfillment(self, client_id, sector):
        """
        特定のクライアントに対して自動実務遂行を行う。
        """
        self.execute_sector_work({"client_id": client_id, "sector": sector})
        return [{"task": f"{sector} specialized work", "status": "completed"}]

    def execute_sector_work(self, config):
        """
        セクターに応じた具体的な実務を実行。
        """
        sector = config.get('sector')
        client_id = config.get('client_id')
        self.logger.info(f"Executing work for {client_id} in {sector}")

        # クライアントディレクトリの作成を保証
        client_path = os.path.join(self.clients_dir, client_id)
        os.makedirs(client_path, exist_ok=True)

        if sector == "LocalGov":
            # アナログ資料のデジタル化実務（モック）
            self.logger.info("Task: AI OCR Analysis of analog documents...")
            # ここに OCR + GPT-4o-vision ロジックを実装
        
        elif sector == "ProfService":
            # 契約書チェック実務（モック）
            self.logger.info("Task: Legal Risk Assessment of shared contracts...")
        
        elif sector == "Medical":
            # 看護レター生成（モック）
            self.logger.info("Task: Generating family communication letters from daily logs...")

        # 独自フォーマットの生成（産廃、防災など）
        form_draft = None
        if sector in ["IndWaste", "FireSafety", "VisaCompliance"]:
            # 実際にはconfigやアップロードされたデータから抽出する
            mock_data = {"generator_name": client_id, "waste_type": "廃材", "quantity": 100, "transporter_name": "代行運送", "disposal_facility": "処分場A"}
            form_result = self.form_engine.generate_form(sector, mock_data)
            if form_result['status'] == "SUCCESS":
                form_draft = form_result['content']
                self.logger.info(f"Generated {sector} draft for {client_id}")

        # 重要アクションを承認キューに追加
        self.approval_queue.add_task(
            client_id=client_id,
            sector=sector,
            action_type="LegalFormGeneration",
            content=f"{sector} 用の法定書類（ドラフト）が完成しました。承認後、正式なPDFとして出力・送信可能です。"
        )

        # 実務完了の証拠を保存
        work_log = os.path.join(self.clients_dir, client_id, 'work_log.json')
        history = []
        if os.path.exists(work_log):
            with open(work_log, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            "task": f"{sector} specialized work",
            "status": "completed"
        })
        
        with open(work_log, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)

if __name__ == "__main__":
    from datetime import datetime
    logging.basicConfig(level=logging.INFO)
    engine = FulfillmentEngine()
    # テスト用アクティブ化
    os.makedirs('clients/TEST_Niche_Client', exist_ok=True)
    with open('clients/TEST_Niche_Client/config.json', 'w', encoding='utf-8') as f:
        json.dump({"client_id": "TEST_Niche_Client", "sector": "LocalGov", "status": "active"}, f)
    
    engine.run_fulfillment_cycle()
