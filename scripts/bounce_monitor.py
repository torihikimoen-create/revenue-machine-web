import os
import re
import email
import imaplib
from email.header import decode_header


def _decode_mime_header(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = ""
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            out += chunk.decode(enc or "utf-8", errors="ignore")
        else:
            out += chunk
    return out


def _extract_failed_recipients(raw_text: str) -> set[str]:
    """
    DSN（Delivery Status Notification）やバウンス本文から、失敗した宛先を抽出する。
    雑に取りすぎると危険なので、メールアドレス形式のみ抽出する。
    """
    if not raw_text:
        return set()
    # 代表的な DSN 表現とメールアドレス抽出
    emails = set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", raw_text, flags=re.I))
    return {e.strip().lower() for e in emails}


def process_bounces_and_update_suppression(
    *,
    suppression,
    imap_host: str,
    imap_user: str,
    imap_password: str,
    mailbox: str = "INBOX",
    search_query: str = '(FROM "MAILER-DAEMON" OR FROM "postmaster" OR SUBJECT "Delivery Status Notification" OR SUBJECT "Undeliver" OR SUBJECT "Mail Delivery")',
    max_messages: int = 50,
    mark_seen: bool = True,
):
    """
    IMAP でバウンス/DSNを検索し、抽出した宛先を suppression に登録する。
    - suppression: EmailSuppressionList 互換（.add/.is_suppressed）
    """
    if not (imap_host and imap_user and imap_password):
        return {"ok": False, "reason": "imap_not_configured", "processed": 0, "suppressed_added": 0}

    processed = 0
    added = 0
    imap = imaplib.IMAP4_SSL(imap_host)
    try:
        imap.login(imap_user, imap_password)
        imap.select(mailbox)

        typ, data = imap.search(None, search_query)
        if typ != "OK":
            return {"ok": False, "reason": "imap_search_failed", "processed": 0, "suppressed_added": 0}

        msg_ids = data[0].split()
        # 新しいものから処理
        msg_ids = msg_ids[::-1][:max_messages]

        for msg_id in msg_ids:
            typ, msg_data = imap.fetch(msg_id, "(RFC822)")
            if typ != "OK" or not msg_data:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subject = _decode_mime_header(msg.get("Subject", ""))

            # 本文抽出（text/plain 優先）
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get("Content-Disposition") or "")
                    if ctype == "text/plain" and "attachment" not in disp:
                        payload = part.get_payload(decode=True) or b""
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset, errors="ignore")
                        break
            else:
                payload = msg.get_payload(decode=True) or b""
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="ignore")

            candidates = _extract_failed_recipients(body)
            # 自分自身/運営宛のメールは除外
            owner_email = (os.getenv("SMTP_USER") or "").strip().lower()
            if owner_email:
                candidates.discard(owner_email)

            for addr in candidates:
                if not suppression.is_suppressed(addr):
                    suppression.add(addr, reason="dsn_bounce_detected", details={"subject": subject[:120]})
                    added += 1

            processed += 1

            if mark_seen:
                imap.store(msg_id, "+FLAGS", "\\Seen")

        return {"ok": True, "processed": processed, "suppressed_added": added}
    finally:
        try:
            imap.logout()
        except Exception:
            pass

