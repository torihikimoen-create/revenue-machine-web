import subprocess
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DomainVerifier")

class DomainVerifier:
    """
    DNSレコード（SPF, DKIM, DMARC）の設定状況を検証するツール。
    """
    def __init__(self, domain):
        self.domain = domain

    def check_dns(self, record_type, subdomain=""):
        target = f"{subdomain}.{self.domain}" if subdomain else self.domain
        try:
            # Windowsのnslookupを使用
            result = subprocess.run(
                ["nslookup", "-type=TXT", target],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            logger.error(f"DNS check failed: {e}")
            return ""

    def verify_spf(self):
        logger.info(f"Checking SPF for {self.domain}...")
        output = self.check_dns("TXT")
        if "v=spf1" in output:
            match = re.search(r'"(v=spf1[^"]*)"', output)
            record = match.group(1) if match else "Found but could not parse"
            logger.info(f"✅ SPF Record Detected: {record}")
            return {"status": "OK", "record": record}
        logger.warning("❌ SPF Record MISSING or invalid.")
        return {"status": "FAIL", "record": None}

    def verify_dmarc(self):
        logger.info(f"Checking DMARC for {self.domain}...")
        output = self.check_dns("TXT", subdomain="_dmarc")
        if "v=DMARC1" in output:
            match = re.search(r'"(v=DMARC1[^"]*)"', output)
            record = match.group(1) if match else "Found but could not parse"
            logger.info(f"✅ DMARC Record Detected: {record}")
            return {"status": "OK", "record": record}
        logger.warning("❌ DMARC Record MISSING.")
        return {"status": "FAIL", "record": None}

    def run_diagnostic(self):
        print(f"\n--- Domain Reputation Diagnostic: {self.domain} ---")
        spf = self.verify_spf()
        dmarc = self.verify_dmarc()
        
        print("\n[Diagnostic Summary]")
        print(f"SPF:   [{spf['status']}] {spf['record'] if spf['record'] else 'Record not found'}")
        print(f"DMARC: [{dmarc['status']}] {dmarc['record'] if dmarc['record'] else 'Record not found'}")
        
        if spf['status'] == "OK" and dmarc['status'] == "OK":
            print("\n✅ Domain is ready for high-reputation outreach.")
        else:
            print("\n⚠️ ACTION REQUIRED: Update DNS based on the setup guide.")

if __name__ == "__main__":
    import sys
    domain_to_check = sys.argv[1] if len(sys.argv) > 1 else "google.com" # テスト用にgoogle.comをデフォルトに
    verifier = DomainVerifier(domain_to_check)
    verifier.run_diagnostic()
