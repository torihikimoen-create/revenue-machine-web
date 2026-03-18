import urllib.parse

def generate_snap_and_send_qr_url(email="eliel8114@gmail.com"):
    """
    スマホでスキャンすると、宛先・件名・本文が自動入力されたメールが開く
    QRコード用のURL（API）を生成します。
    """
    subject = "【AETHER CORE】業務依頼"
    body = "写真を添付してそのまま送信してください。\n---\n依頼内容（例：清書して、要約して等）をここに書いてもOKです。"
    
    # mailtoスキームの作成
    mailto_link = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    # QRコード生成APIのURLを作成 (QRServer APIを使用)
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?data={urllib.parse.quote(mailto_link)}&size=300x300"
    
    return qr_api_url

if __name__ == "__main__":
    url = generate_snap_and_send_qr_url()
    print("-" * 50)
    print("AETHER CORE: Snap & Send QR Code URL")
    print("-" * 50)
    print(f"このURLをブラウザで開くと、QRコードが表示されます:\n{url}")
    print("-" * 50)
    print("パンフレットや初回メールにこの画像リンクを埋め込んでください。")
