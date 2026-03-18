import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("InvoiceManager")

class InvoiceManager:
    """
    B2B向けの正式な請求書発行と後払い（Deferred Payment）を管理する。
    """
    def __init__(self):
        self.invoice_dir = "invoices"
        os.makedirs(self.invoice_dir, exist_ok=True)

    def create_official_invoice(self, client_id, amount, currency="JPY"):
        """
        Stripe Invoicing API (シミュレーション) を用いて正式な請求書を発行。
        """
        logger.info(f"Issuing official invoice for client: {client_id}")
        
        invoice_id = f"INV-{client_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
        invoice_data = {
            "invoice_id": invoice_id,
            "client_id": client_id,
            "amount": amount,
            "currency": currency,
            "status": "OPEN",
            "due_date": "月末締め翌月末払い",
            "stripe_invoice_link": f"https://dashboard.stripe.com/test/invoices/{invoice_id}",
            "issued_at": datetime.now().isoformat()
        }
        
        filename = f"{invoice_id}.json"
        filepath = os.path.join(self.invoice_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(invoice_data, f, indent=4, ensure_ascii=False)
            
        return invoice_data

    def notify_invoice_ready(self, invoice_data):
        """
        オーナー（あなた）に対し、発行された請求書の承認・送付準備を通知。
        """
        from scripts.approval_dashboard import ApprovalQueue
        queue = ApprovalQueue()
        queue.add_task(
            client_id=invoice_data['client_id'],
            sector="Finance",
            action_type="InvoiceIssuance",
            content=f"正式請求書 {invoice_data['invoice_id']} ({invoice_data['amount']} {invoice_data['currency']}) の発行準備が完了しました。承認後、クライアントへ送信されます。"
        )

if __name__ == "__main__":
    manager = InvoiceManager()
    inv_data = manager.create_official_invoice("TEST_B2B_CLIENT", 150000)
    manager.notify_invoice_ready(inv_data)
