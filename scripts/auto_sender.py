import json
import os
import smtplib
import logging
import time
import random
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

class AutoSender:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logger = logging.getLogger("AutoSender")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        
        # 安全策: DRY_RUN が true の場合は、SENDER_MOCK_MODE の設定に関わらず強制的に MOCK モードにする
        env_dry_run = (os.getenv("DRY_RUN") or "true").lower() == "true"
        self.is_mock = (os.getenv("SENDER_MOCK_MODE", "true").lower() == "true") or env_dry_run
        
        if env_dry_run:
            self.logger.info("Global DRY_RUN is enabled. Forcing SENDER_MOCK_MODE to True for safety.")
        
        # セクターデータの読み込み
        self.sector_data = self._load_sector_data()
        
        # 送信クォータ（1日の上限）管理
        self.quota_file = os.path.join(self.project_root, "scripts", "email_quota.json")
        self.MAX_DAILY_SENDS = int(os.getenv("MAX_DAILY_SENDS", 500)) # 環境変数から取得、デフォルト500
        self.ALERT_THRESHOLD = int(self.MAX_DAILY_SENDS * 0.8) # 80% で警告

        # BAN対策：バウンス/拒否を記録し、将来の送信を抑止する
        from scripts.email_suppression import EmailSuppressionList
        self._suppression = EmailSuppressionList(
            storage_path=os.path.join(self.project_root, "scripts", "suppression_list.json"),
            hash_salt=os.getenv("AUDIT_LOG_EMAIL_HASH_SALT", ""),
        )

        # 送信証跡（チャージバック等の証拠用、本文・宛先はハッシュで保持）
        self._audit_log_path = os.path.join(self.project_root, "scripts", "email_audit_log.jsonl")

        # 連続失敗の自動停止（BAN耐性）
        self._max_consecutive_failures = int(os.getenv("MAX_CONSECUTIVE_FAILURES", 3))
        self._consecutive_failures = 0
        self._circuit_breaker_file = os.path.join(self.project_root, "scripts", "email_send_circuit_breaker.json")

    def _trip_circuit_breaker(self, reason: str):
        try:
            from datetime import datetime, timezone
            payload = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
                "consecutive_failures": self._consecutive_failures,
            }
            with open(self._circuit_breaker_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _is_circuit_breaker_tripped(self) -> bool:
        try:
            return os.path.exists(self._circuit_breaker_file)
        except Exception:
            return False

    def _load_sector_data(self):
        json_path = os.path.join(self.project_root, "config", "sector_data.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load sector data JSON: {e}")
            return {}

    def _update_quota(self):
        """今日の送信数をカウントアップする"""
        from datetime import date
        today = str(date.today())
        data = {}
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
            except: pass
        
        if today not in data:
            data = {today: 0}
        
        data[today] += 1
        
        try:
            with open(self.quota_file, 'w') as f:
                json.dump(data, f)
            
            count = data[today]
            if count >= self.MAX_DAILY_SENDS:
                self.logger.error(f"!!! CRITICAL: Daily Email Quota Reached ({count}/{self.MAX_DAILY_SENDS}) !!!")
            elif count >= self.ALERT_THRESHOLD:
                self.logger.warning(f"!!! WARNING: Daily Email Quota approaching limit ({count}/{self.MAX_DAILY_SENDS}) !!!")
        except: pass

    def _is_quota_exceeded(self):
        """今日の送信数が上限に達しているかチェック"""
        from datetime import date
        today = str(date.today())
        if not os.path.exists(self.quota_file):
            return False
        
        try:
            with open(self.quota_file, 'r') as f:
                data = json.load(f)
            count = data.get(today, 0)
            return count >= self.MAX_DAILY_SENDS
        except:
            return False

    def _prepare_body_with_footer(self, body):
        """利用ガイドと特商法リンクをフッターに付与する共通処理"""
        base_url = os.getenv("LP_BASE_URL", "https://torihikimoen-create.github.io/revenue-machine-web/").rstrip("/")
        guide_url = f"{base_url}/guide.html"
        tokushoho_url = f"{base_url}/tokushoho.html"
        
        footer = f"\n\n---\n【利用ガイド】Snap & Send の使い方はこちら:\n{guide_url}\n\n特定商取引法に基づく表記: {tokushoho_url}"
        
        # 本文中のプレースホルダURLを本番用URLに置換
        body_fixed = body.replace("https://aether-core.example.com/trial", f"{base_url}/index.html")
        body_fixed = body_fixed.replace("https://aether-core.example.com", base_url)
        
        return body_fixed.rstrip() + footer

    def _should_skip_address(self, email, username=None):
        """テスト用アドレスや無効なアドレスをスキップする共通処理"""
        if not email or not isinstance(email, str):
            self.logger.warning(f"Invalid email address found for {username or 'Unknown'}: {email}. Skipping.")
            return True
        
        # テスト用ドメインの広範なブロック（run_automation のブロックリストと一致）
        email_lower = email.lower()
        mock_indicators = ["example.", "example.com", "example.co.uk", "test@", "sample@", "localhost", "invalid"]
        if any(indicator in email_lower for indicator in mock_indicators):
            self.logger.warning(f"Safety Guard: Blocking mock/test email {email}")
            return True

        if username and "TEST_" in username:
            self.logger.warning(f"Safety Guard: Skipping mock target {username} ({email})")
            return True

        # BAN対策：過去にバウンス/拒否した宛先は抑止
        if self._suppression.is_suppressed(email):
            self.logger.warning(f"Safety Guard: Suppressed address blocked for {username or 'Unknown'}")
            return True
            
        return False

    def _hash_str(self, s: str) -> str:
        h = hashlib.sha256()
        h.update((s or "").encode("utf-8"))
        return h.hexdigest()

    def _audit_send_event(self, event_type: str, to_email: str, subject: str, body: str, extra: dict | None = None):
        """
        送信/失敗の証跡を JSONL で保持（PIIを直接残さない）。
        """
        try:
            from datetime import datetime, timezone
            payload = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event_type,
                "to_email_hash": self._hash_str((os.getenv("AUDIT_LOG_EMAIL_HASH_SALT", "") + (to_email or "").strip().lower())),
                "subject_hash": self._hash_str(subject or ""),
                "body_hash": self._hash_str(body or ""),
            }
            if extra:
                payload["extra"] = extra
            os.makedirs(os.path.dirname(self._audit_log_path), exist_ok=True)
            with open(self._audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_dynamic_sender_name(self, sector):
        """業界に応じて、最も信頼されやすい送信者名を返す。"""
        names = self.sector_data.get("sender_names", {})
        return names.get(sector, "エーテルコア・ビジネス自動化推進部")

    def send_proposal_email(self, target, content, is_humanized=False):
        """
        B2B案件に対して生成された提案書をメールで送信する。
        is_humanized が False の場合、実送信を拒否するガードレールを持つ。
        """
        # content が辞書（AI個別件名入り）の場合は分解
        ai_subject = None
        if isinstance(content, dict):
            ai_subject = content.get('subject')
            content = content.get('content', "")

        client_name = target.get('username', '貴社')
        # ターゲットにメールアドレスが含まれていない場合はログを出力してスキップ
        to_email = target.get('email')
        
        if self._should_skip_address(to_email, client_name):
            return False

        # セクターデータのデフォルト件名
        sector_subjects = self.sector_data.get("sector_email_subjects", {})
        default_subject = sector_subjects.get(target.get('sector'), f"AI導入による実務自動化と時間創出のご案内")
        
        # AIが生成した個別件名がある場合はそちらを優先（会社名もAIに含めてもらう前提）
        if ai_subject:
            subject = ai_subject
        else:
            # デフォルト件名には自然な形で宛名を入れる
            subject = f"{client_name}様：{default_subject}"
        from_name = self.get_dynamic_sender_name(target.get('sector'))
        
        content_with_footer = self._prepare_body_with_footer(content)

        # 品質ゲート: 人間化されていない文章の実送信をブロックする
        if not is_humanized and not self.is_mock:
            self.logger.error(f"CRITICAL: Attempted to send non-humanized proposal to {to_email}. BLOCKING SEND for quality assurance.")
            return False

        if self.is_mock:
            self.logger.info(f"[MOCK] From: {formataddr((from_name, self.from_email))} To: {to_email}")
            self.logger.info(f"[MOCK] Subject: {subject}")
            self._audit_send_event("mock_send", to_email, subject, content_with_footer)
            return True

        # クォータチェック（上限超過時は送信拒否）
        if self._is_quota_exceeded():
            self.logger.error(f"BLOCKING SEND: Daily quota exceeded for {self.smtp_user}. Prevent account suspension.")
            return False

        # 連続失敗が一定以上の場合は、これ以上送らない（BAN耐性）
        if self._is_circuit_breaker_tripped():
            self.logger.error("BLOCKING SEND: Circuit breaker is tripped due to repeated failures.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr((from_name, self.from_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content_with_footer, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Successfully sent proposal email to {to_email}")
            self._update_quota() # 送信成功時にカウント
            self._audit_send_event("sent", to_email, subject, content_with_footer)
            self._consecutive_failures = 0
            
            # BAN対策：送信後にランダムな待機（5-15秒）を入れる
            wait_time = random.uniform(5, 15)
            self.logger.info(f"Antispam delay: waiting {wait_time:.1f}s before next operation...")
            time.sleep(wait_time)
            
            return True
        except smtplib.SMTPRecipientsRefused as e:
            # SMTP段階での拒否（存在しない宛先など）
            self.logger.error(f"SMTPRecipientsRefused for {to_email}: {e}")
            self._suppression.add(to_email, reason="smtp_recipients_refused", details={"error": str(e)})
            self._audit_send_event("failed", to_email, subject, content_with_footer, extra={"reason": "SMTPRecipientsRefused"})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False
        except smtplib.SMTPDataError as e:
            # 550/553 等の恒久エラーは抑止登録
            code = getattr(e, "smtp_code", None)
            msg = getattr(e, "smtp_error", None)
            self.logger.error(f"SMTPDataError for {to_email}: {code} {msg}")
            if code in (550, 551, 552, 553, 554):
                self._suppression.add(to_email, reason="smtp_data_error", details={"smtp_code": code, "smtp_error": str(msg)})
            self._audit_send_event("failed", to_email, subject, content_with_footer, extra={"reason": "SMTPDataError", "smtp_code": code})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}")
            self._audit_send_event("failed", to_email, subject, content_with_footer, extra={"reason": "Exception", "error": str(e)})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False

    def send_custom_email(self, to_email, subject, body):
        """フィードバック用など、件名・本文を指定して1通送信する。"""
        if self._should_skip_address(to_email):
            return False

        body_with_footer = self._prepare_body_with_footer(body)
        from_name = "AETHER CORE サポート"

        if self.is_mock:
            self.logger.info(f"[MOCK] send_custom_email To: {to_email} Subject: {subject} From: {from_name}")
            self._audit_send_event("mock_send_custom", to_email, subject, body_with_footer)
            return True

        if not self.smtp_user or not self.smtp_password:
            self.logger.error("SMTP credentials not found. Set SMTP_USER and SMTP_PASSWORD.")
            return False

        # クォータチェック
        if self._is_quota_exceeded():
            self.logger.error(f"BLOCKING SEND: Daily quota exceeded for {self.smtp_user}.")
            return False

        if self._is_circuit_breaker_tripped():
            self.logger.error("BLOCKING SEND: Circuit breaker is tripped due to repeated failures.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = formataddr((from_name, self.from_email))
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body_with_footer, "plain"))
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            self.logger.info(f"Successfully sent custom email to {to_email}")
            self._update_quota() # 送信成功時にカウント
            self._audit_send_event("sent_custom", to_email, subject, body_with_footer)
            self._consecutive_failures = 0
            
            # BAN対策：送信後にランダムな待機（5-15秒）を入れる
            wait_time = random.uniform(5, 15)
            self.logger.info(f"Antispam delay: waiting {wait_time:.1f}s before next operation...")
            time.sleep(wait_time)
            
            return True
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"SMTPRecipientsRefused for {to_email}: {e}")
            self._suppression.add(to_email, reason="smtp_recipients_refused", details={"error": str(e)})
            self._audit_send_event("failed_custom", to_email, subject, body_with_footer, extra={"reason": "SMTPRecipientsRefused"})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False
        except smtplib.SMTPDataError as e:
            code = getattr(e, "smtp_code", None)
            msg = getattr(e, "smtp_error", None)
            self.logger.error(f"SMTPDataError for {to_email}: {code} {msg}")
            if code in (550, 551, 552, 553, 554):
                self._suppression.add(to_email, reason="smtp_data_error", details={"smtp_code": code, "smtp_error": str(msg)})
            self._audit_send_event("failed_custom", to_email, subject, body_with_footer, extra={"reason": "SMTPDataError", "smtp_code": code})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send custom email to {to_email}: {e}")
            self._audit_send_event("failed_custom", to_email, subject, body_with_footer, extra={"reason": "Exception", "error": str(e)})
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._trip_circuit_breaker("too_many_consecutive_failures")
            return False

    def send_notification(self, message):
        """
        LINE/Discord通知のプレースホルダー（将来拡張用）
        """
        self.logger.info(f"Notification: {message}")
        # 这里将来可以集成 Webhook
        return True
