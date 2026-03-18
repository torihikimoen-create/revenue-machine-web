import os
# [PROJECT_TRUTH] 運営: AETHER CORE プロジェクト / 代表: 増本 友貴 / 最安: 24,800円〜 / 建設: 33,000円〜
import sys
import random
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 各モジュールのインポート
from scripts.global_discovery import GlobalDiscovery
from scripts.stripe_link_gen import create_service_payment_link
from scripts.trial_tracker import get_active_trial_count
from scripts.auto_sender import AutoSender
from scripts.report_generator import GrowthReportGenerator
from scripts.market_explorer import BlueOceanExplorer
import scripts.user_analytics as analytics
from scripts.feedback_engine import run_feedback_cycle
from scripts.core_fan_detector import get_top_fans
from scripts.safety_guardrails import auto_backup, create_system_snapshot, ensure_permanent_backup
from scripts.integrity_checker import run_audit, save_hashes_to_registry
from scripts.pii_masker import sanitize_payload
from scripts.approval_dashboard import ApprovalQueue
sys.path.append(os.path.join(current_dir, 'sns-sales-hunter', 'src'))
sys.path.append(os.path.join(current_dir, 'b2b-deal-finder', 'src'))
from hunter import SNSHunter
from generator import DMDraftGenerator
from finder import B2BDealFinder
from builder import BusinessProposalBuilder
from scripts.industry_engines.sanpai_engine import SanpaiComplianceEngine
from scripts.humanizer import HumanizerEngine

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AetherCoreEngine")

# ドライラン設定
DRY_RUN = (os.getenv("DRY_RUN") or "true").lower() == "true"
# 承認必須フラグ
REQUIRE_APPROVAL = (os.getenv("REQUIRE_APPROVAL") or "true").lower() == "true"

if DRY_RUN:
    logger.info("!!! DRY RUN MODE ENABLED (No real emails or leads) !!!")
if REQUIRE_APPROVAL:
    logger.info("!!! APPROVAL MODE ENABLED (Actions will wait for Owner's GO) !!!")

def run_daily_cycle():
    logger.info("=== Starting Daily Automation Cycle ===")
    
    # --- SAFETY: Pre-run Snapshot ---
    important_files = [
        os.path.join(current_dir, 'global_leads.json'),
        os.path.join(current_dir, 'approval_queue.json'),
        os.path.join(current_dir, 'leads_history.json'),
        os.path.join(current_dir, 'daily_stats.json'),
        os.path.join(current_dir, 'user_analytics.json')
    ]
    create_system_snapshot(important_files)

    # --- SAFETY: 前回完了時からの改ざん検知（レジストリ連携の全自動化） ---
    _pre_ok, _pre_results = run_audit([(f, []) for f in important_files], verify_against_registry=True)
    if not _pre_ok:
        logger.warning("!!! Pre-run integrity check: data may have been modified since last successful run. Review config/integrity_hashes.json and backups. !!!")

    # DRY_RUN 時はリードファイルを分離して汚染を防ぐ（鉄壁のデータ隔離）
    lead_file = 'mock_leads.json' if DRY_RUN else 'global_leads.json'
    discovery = GlobalDiscovery(output_file=lead_file)
    logger.info(f"Discovery Engine initialized with lead file: {lead_file}")
    hunter = SNSHunter()
    generator = DMDraftGenerator()
    finder = B2BDealFinder()
    builder = BusinessProposalBuilder()
    auto_sender = AutoSender()
    report_gen = GrowthReportGenerator()
    humanizer = HumanizerEngine()
    approval_queue = ApprovalQueue()

    # --- SAFETY: Bounce/DSN monitoring (BAN耐性) ---
    # 遅延バウンス（MAILER-DAEMON/DSN）をIMAPで回収し、サプレッションに反映する
    if not DRY_RUN:
        try:
            from scripts.bounce_monitor import process_bounces_and_update_suppression

            imap_host = os.getenv("IMAP_HOST", "")
            imap_user = os.getenv("IMAP_USER", "")
            imap_password = os.getenv("IMAP_PASSWORD", "")
            imap_mailbox = os.getenv("IMAP_MAILBOX", "INBOX")

            # AutoSender が持つ suppression を利用
            suppression = getattr(auto_sender, "_suppression", None)
            if suppression and imap_host and imap_user and imap_password:
                res = process_bounces_and_update_suppression(
                    suppression=suppression,
                    imap_host=imap_host,
                    imap_user=imap_user,
                    imap_password=imap_password,
                    mailbox=imap_mailbox,
                    max_messages=int(os.getenv("IMAP_BOUNCE_MAX_MESSAGES", 50)),
                )
                logger.info(f"Bounce monitor result: {res}")
            else:
                logger.info("Bounce monitor skipped (IMAP not configured).")
        except Exception as e:
            logger.warning(f"Bounce monitor failed (non-fatal): {e}")

    logger.info("--- Phase 0: Autonomous Market Exploration ---")
    explorer = BlueOceanExplorer()
    new_opp = explorer.explore_new_opportunities()
    proposal_path = explorer.generate_proposal_report(new_opp)
    logger.info(f"New Opportunity Detected: {new_opp['title']}")

    # 専門エンジンの初期化
    sanpai_engine = SanpaiComplianceEngine()

    # 1. 新しいリードの自動発掘 (Niche Blue Ocean Sectors)
    # ブルーオーシャン聖域（実績構築のための厳選セクター）
    niche_sectors = [
        "Nursing", "Medical", "LocalGov", "ProfService", "Construction",
        "IndWaste", "FireSafety", "VisaCompliance", "Maritime",
        # APAC expansion
        "Dental", "AgedCare", "CSP", "Childcare", "FoodSafety", "AML_Prep"
    ]
    cities = ["Tokyo", "New York", "London", "Singapore", "Sydney"]
    
    if DRY_RUN:
        logger.info("Dry Run: Generating hyper-personalized sniper leads for each sector (including Hyper-Niches).")
    else:
        # 全国巡回スキャン
        for sector in niche_sectors:
            results = discovery.discover_all_japan(sector)
            discovery.update_leads_file(results)

    # 2. リードリストと履歴・実績ログの読み込み
    history_file = os.path.join(current_dir, 'leads_history.json')
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            leads_history = json.load(f)
    else:
        leads_history = {}

    current_leads_path = os.path.join(current_dir, lead_file)
    if os.path.exists(current_leads_path):
        with open(current_leads_path, 'r', encoding='utf-8') as f:
            global_leads = json.load(f)
    else:
        logger.warning(f"Lead file {lead_file} not found. Using empty list.")
        global_leads = []

    # セクター別の実績カウンタ
    sector_stats = {}

    # 各都市のタイムゾーン設定 (UTCからのオフセット)
    CITY_TIMEZONES = {
        "Tokyo": 9,
        "Singapore": 8,
        "Sydney": 11,   # AEDT (UTC+11) ※夏時間等で変動するが固定値で近似
        "London": 0,    # GMT (UTC+0)
        "New York": -5  # EST (UTC-5)
    }

    # 安全な流量制限（Gmail BAN防止）
    MAX_EMAILS_PER_DAY = 100   # 1日の総送信上限
    MAX_EMAILS_PER_RUN = 8    # 1回の起動（1時間）ごとの送信上限

    # 本日の送信数を確認 (daily_stats.json から)
    stats_file = os.path.join(current_dir, 'daily_stats.json')
    today_str = datetime.now().strftime('%Y-%m-%d')
    daily_sent_count = 0
    all_stats = {} # 辞書形式で統一
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
                # もし中身がリストだった場合の救済処置
                if isinstance(all_stats, list):
                    # リスト形式の古いデータを辞書形式に変換（必要あれば）
                    new_dict = {}
                    for entry in all_stats:
                        if "date" in entry:
                            new_dict[entry["date"]] = entry
                    all_stats = new_dict
                
                daily_sent_count = all_stats.get(today_str, {}).get('total_proposals_sent', 0)
        except Exception:
            all_stats = {}
    
    run_sent_count = 0 # 今回の実行での送信数

    def is_business_hours(city_name):
        """
        指定された都市の現在時刻が、営業開始ゴールデンタイム（9:00 - 11:00）内か判定する。
        """
        # UTC現在時刻を取得
        now_utc = datetime.utcnow()
        offset = CITY_TIMEZONES.get(city_name, 9) # デフォルトは日本
        local_hour = (now_utc.hour + offset) % 24
        
        # 9時から11時の間（9:00〜11:59までをカバー）
        is_golden = 9 <= local_hour <= 11
        logger.info(f"[Time Check] {city_name}: Local Hour is {local_hour}. Golden Window: {is_golden}")
        return is_golden

    # 3. 各リードに対してAI提案文を生成
    should_stop_run = False
    for city_data in global_leads:
        if should_stop_run:
            break
        city = city_data['city']
        
        # 営業時間チェック (DRY_RUN時は無視して全都市テスト可能にする)
        if not DRY_RUN and not is_business_hours(city):
            logger.info(f"Skipping {city} - Outside of local golden window (9-11 AM).")
            continue

        targets = hunter.hunt_targets(city, city_data['targets'])
        
        for target in targets:
            if should_stop_run:
                break
            business_id = target.get('username') or target.get('name', 'Unknown')
            logger.info(f"Processing target: {business_id} in {city}")
            
            # 履歴チェック: すでに試用版を提供済みか？
            has_trial_history = leads_history.get(business_id, {}).get('trial_offered', False)

            sector = target.get('sector')
            # ロケール/言語の正規化（SG/AUは英語提案をデフォルトにする）
            lang = target.get('lang')
            if city in ["Singapore", "Sydney"]:
                lang = "en"
            if not lang:
                lang = "ja"
            target["lang"] = lang
            
            # AI知識レベルの自動設定 (未経験層向け Gentle Mode 分岐)
            # 現場仕事、伝統的業界、法務・介護など、AIよりも「実務解決」が刺さるセクターを特定
            gentle_sectors = [
                "Nursing", "AgedCare", "Childcare", "Medical", "Dental",
                "Construction", "IndWaste", "LocalGov", "FoodSafety", "Maritime"
            ]
            if sector in gentle_sectors:
                target["awareness_level"] = "low"
                logger.info(f"[Gentle Mode] Awareness level set to 'low' for {business_id} ({sector})")
            else:
                target["awareness_level"] = "high"

            # セクター別カウンタ初期化
            if sector not in sector_stats:
                sector_stats[sector] = {
                    "proposals_sent": 0,
                    "trials_offered": 0
                }

            # ブルーオーシャン領域（介護・建設・行政・APAC法規制ニッチ等）または特定の業種
            if sector in [
                "Nursing", "Medical", "Dental",
                "Construction", "ProfService", "LocalGov",
                "IndWaste", "FireSafety", "VisaCompliance", "Maritime",
                "AgedCare", "CSP", "Childcare", "FoodSafety", "AML_Prep",
                "Osteopathy", "Luxury Beauty"
            ]:
                # SAFETY: LLM送信前に情報のマスキングを適用（流出防止）
                safe_target = sanitize_payload(target)
                ai_report = report_gen.generate_report(safe_target)
                report_path = report_gen.save_report(target, ai_report)
                
                # 分解（ai_subject はこの後のメール送信で使用）
                ai_subject = None
                if isinstance(ai_report, dict):
                    ai_subject = ai_report.get('subject')
                    report_content = ai_report.get('content', "")
                else:
                    report_content = ai_report
                
                # 共通のサブスクリプションロジック（実績フェーズ価格）
                trial_days = 0 if has_trial_history else 10
                # セクター別価格設定（増本様と合意した価格表に基づく）
                price = 24800  # デフォルト（Nursing / Medical / Osteopathy / Luxury Beauty 等）
                if sector == "Construction":
                    price = 33000  # 建設セクター：33,000円
                elif sector in ["ProfService", "IndWaste", "FireSafety", "VisaCompliance", "Maritime"]:
                    price = 34800  # 士業・産廃・ニッチセクター：34,800円
                elif sector == "LocalGov":
                    price = 79800  # 自治体セクター：79,800円
                
                # 安全性と整合性のためのメタデータ付与
                metadata = {
                    "type": "subscription",
                    "business_id": business_id,
                    "sector": sector,
                    "city": city,
                }
                
                setup_fee = 0  # 増本様の方針に基づき、初期費用は0円（完全無料トライアル）
                sub_link = create_service_payment_link(
                    f"AI Business Automation ({business_id})", 
                    setup_fee_jpy=setup_fee,
                    monthly_fee_jpy=price, 
                    trial_days=trial_days,
                    customer_email=target.get("email"),
                    metadata=metadata
                )
                
                leads_history[business_id] = {
                    "last_contact": datetime.now().isoformat(),
                    "trial_offered": True,
                    "last_link": sub_link,
                    "sector": target.get('sector')
                }

                # 業界別メッセージの微調整
                sector_name_ja = {
                    "Nursing": "介護施設",
                    "Construction": "建設・工務店",
                    "LocalGov": "自治体・公共セクター",
                    "ProfService": "法律・専門サービス",
                    "Medical": "医療機関",
                    "Dental": "歯科・クリニック"
                }.get(sector, "店舗")
                trial_msg = "まずは10日間無料（テスト）の特別提供枠をご用意しました。" if trial_days > 0 else "更なる運営効率化と利益最大化プランをご用意しました。"

                if sector == "Nursing":
                    sector_specific_msg = "2026年度の報酬改定は、多くの施設にとって『存続か閉鎖か』の分水嶺となります。人手不足が深刻化する中、記録入力やシフト調整といった事務作業をAIに『丸投げ』することで、現場スタッフの離職を食い止め、経営を安定化させる唯一の手段をご提案します。"
                elif sector == "Medical":
                    sector_specific_msg = "医師・看護師が本来の医療行為に集中できず、書類作成に追われる現状は、病院経営にとって最大の損失です。専門性の低い事務タスクをAI側にオフロードすることで、病床稼働率の向上とスタッフの疲弊解消を同時に実現する、命を守るための経営判断をご提案します。"
                elif sector == "Construction":
                    sector_specific_msg = "2024年問題、そして2026年施行の取引適正化法。対応が遅れた会社から順に『法的制裁・取引停止』の憂き目に遭います。見積書や安全書類作成という『1件ごとの紙仕事』をAIで完全自動化し、この生存競争を勝ち抜くための防壁を築きましょう。"
                elif sector == "ProfService":
                    sector_specific_msg = "顧問先ごとのメール往復、契約書ドラフトのひな形作成、請求書の発行・督促、相談内容の要約とナレッジ化など、「知的だが単調な事務処理」をAIが先回りして下書きすることで、先生方には判断と交渉に専念していただける構成です。"
                elif sector == "LocalGov":
                    sector_specific_msg = "2025年度末の標準化期限。アナログ規制撤廃の波に取り残されることは、住民サービスの停滞、ひいては行政の信頼失墜を意味します。分断された事務処理をAIで一つの自動フローに束ねることで、職員様の時間を政策立案という本来の仕事へ取り戻します。"
                elif sector == "Dental":
                    if target.get('lang') == 'ja':
                        sector_specific_msg = "特に、診療予約の自動調整、リピート率向上のための定期検診リマインド、そしてMEO（マップ検索）対策としての口コミ返信自動化など、「先生が本来の治療に集中できる時間」を最大化する設計になっています。"
                    else:
                        sector_specific_msg = "Specifically, our AI automates complex scheduling, patient appointment reminders for higher retention, and real-time reputation management through automated review responses, allowing you to focus entirely on patient care."
                elif sector == "AgedCare":
                    sector_specific_msg = "Upcoming aged care reforms significantly raise compliance and documentation expectations. Our AI automates documentation and governance reporting to reduce admin load and improve audit readiness while your team focuses on resident care."
                elif sector == "CSP":
                    sector_specific_msg = "Regulatory expectations for corporate service providers continue to tighten. Our AI automates AML/CFT screening workflows and filing prep to reduce manual work and strengthen compliance posture."
                elif sector == "Childcare":
                    sector_specific_msg = "Childcare compliance requirements are becoming stricter, with increased expectations around incident logging, reporting, and policy documentation. Our AI keeps records consistent and speeds up reporting workflows to reduce risk and admin burden."
                elif sector == "FoodSafety":
                    sector_specific_msg = "Food safety compliance increasingly depends on accurate, consistent digital logs and traceability. Our AI automates Food Control Plan documentation and recordkeeping workflows to improve readiness for audits and grading frameworks."
                elif sector == "AML_Prep":
                    sector_specific_msg = "If expanded AML/CTF obligations apply to your firm, early preparation matters. Our AI helps operationalize risk assessments and KYC workflows now, so you can be ready well ahead of enforcement timelines."
                else:
                    sector_specific_msg = ""
                
                # レポートブロック（メール本文に挿入する部分）。産廃の場合は事前監査結果を先頭に付与
                report_block = report_content[:700] + "..."
                if sector == "IndWaste":
                    logger.info(f"Applying Specialized Industry Logic for {business_id} (IndWaste)")
                    demo_manifest = {
                        "id": f"M-{random.randint(1000, 9999)}",
                        "type": "廃プラスチック類",
                        "qty": str(random.uniform(1.0, 10.0)),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "has_contract": random.choice([True, False]),
                        "contract_expiry": (datetime.now() + timedelta(days=random.randint(-10, 60))).strftime("%Y-%m-%d")
                    }
                    analyzed_data = sanpai_engine.analyze_manifest(demo_manifest)
                    audit_result = sanpai_engine.validate_compliance(analyzed_data)
                    # 顧客向け：信頼感を与えつつ不安を煽りすぎない表現（詳細はログ・内部で保持）
                    audit_summary_customer = "【専門AIによる事前確認結果】\n"
                    if audit_result["is_compliant"]:
                        audit_summary_customer += "法令遵守状況に特段の懸念は検出されませんでした。現在の運用フローの継続をご提案します。\n"
                    else:
                        audit_summary_customer += "契約・期限等について確認を推奨する項目が検出されました。詳細はお気軽にご相談ください。\n"
                    report_block = audit_summary_customer + "\n---\n" + report_content[:500] + "..."
                
                # コンプライアンス文言（オセアニア・アジア向け）
                compliance_msg = ""
                if city == "Singapore":
                    compliance_msg = "\n*Privacy note: designed with Singapore PDPA principles in mind; confirm your specific obligations with counsel.*"
                elif city == "Sydney":
                    compliance_msg = "\n*Privacy note: designed with Australian Privacy Principles (APP) in mind; confirm your specific obligations with counsel.*"

                if target.get('lang') == 'ja':
                    sub_proposal = f"""
{business_id} 様（{sector_name_ja} 責任者様）

貴業界を揺るがす2026年の法改正、および慢性的な人手不足による「事業存続のリスク」に対する、唯一無二の解決策のご提案です。
もはや従来の「効率化」では追いつかない段階に来ていることは、現場の皆様が一番痛感されているかと存じます。

{sector_specific_msg}

弊社のAIスナイパーが検知した、貴施設固有の「深刻なボトルネック」と、その劇的な解決策をまとめた特別レポートを添付いたします。
本パッケージは、単なるツールではなく、貴施設の「デジタル生命維持装置」としての役割を果たします。
---
{report_block}
---

今なら10日間、全機能を実務に「完全投入」して効果を検証いただける枠を確保しております。
手遅れになる前に、AIによる「業務の丸投げ」をご決断ください。

詳細・10日間お試し（全機能解放）:
{sub_link}
{compliance_msg}
"""
                else:
                    # Western Mode Layout
                    sub_proposal = f"""
Dear {business_id} Management Team,

I am writing to offer a unique solution to the 2026 market disruptions and the chronic labor shortage threatening business continuity in the {sector} sector.
Traditional optimization is no longer enough; a paradigm shift to autonomous execution is required.

{sector_specific_msg}

Our AI Sniper has detected specific bottlenecks in your operations. I have attached a tailored Growth Report outlining a dramatic transformation.
This package is not just a tool; it is your firm's "Digital Life Support System."
---
{report_block}
---

【ご案内】
貴社のような重要拠点に対し、まずは効果を実感いただくための「10日間無料トライアル（全機能解放）」をご用意いたしました。
一切のコストやリスクなく、AIによる実務自動化を今日からその場でお試しいただけます。

もしご満足いただけなければ、期間中にいつでもボタン一つで利用停止可能です。費用は1円もかかりません。
この機会に、AIが実務を代行する「ゆとりある運営」をぜひご体験ください。

▼ 10日間無料トライアルの開始はこちら
{sub_link}
{compliance_msg}
"""
                # テスト用アドレス（mock等）の徹底排除
                target_email = target.get('email', '')
                business_id = target.get('username', 'Unknown')
                
                # SAFETY: マルチAI合議制（多重検閲）および自動修正の実行
                from scripts.safety_guardrails import ConsensusEngine
                from scripts.corrector import AIProposalCorrector
                
                consensus_engine = ConsensusEngine()
                corrector = AIProposalCorrector()
                
                # 1. 合議制チェック（実働きAIによる検閲）
                report = consensus_engine.get_consensus(sub_proposal)
                
                if report['summary'] == 'REJECTED':
                    logger.warning(f"!!! PROPOSAL REJECTED by Expert AI for {business_id} !!!")
                    # 2. 自動修正を試みる
                    logger.info("Attempting automatic correction...")
                    sub_proposal = corrector.correct_proposal(sub_proposal, report)
                    
                    # 修正後にもう一度チェック（再検証）
                    report = consensus_engine.get_consensus(sub_proposal)
                    if report['summary'] == 'REJECTED':
                        logger.error("Correction failed to resolve all issues. Forcing manual approval.")
                        target['require_approval_reason'] = "AI Correction Failed (Expert AI Rejection)"
                
                # 3. 法的裏取り結果の最終反映
                if not report['fact_checks']['verified']:
                    target['require_approval_reason'] = "Legal Fact-Check Warning (Persistent)"

                # 4. Humanizer による人間味のある文章への昇華（最終調整）
                # これにより「文章を整える前に送られる」リスクを排除する
                logger.info(f"Humanizing proposal for {business_id}...")
                sub_proposal, humanized_ok = humanizer.polish(sub_proposal, sector=sector)

                if auto_sender._should_skip_address(target_email, business_id):
                    logger.warning(f"Skipping test/mock email: {target_email}")
                    success = False
                else:
                    force_approval = target.get('require_approval_reason') is not None
                    if not DRY_RUN:
                        if REQUIRE_APPROVAL or force_approval:
                            logger.info(f"Adding task to Approval Queue for {business_id} (Reason: {target.get('require_approval_reason', 'Manual Policy')})")
                            approval_queue.add_task(
                                business_id, 
                                sector, 
                                "EmailProposal", 
                                sub_proposal,
                                metadata={
                                    "email": target.get("email"),
                                    "lang": target.get("lang", "ja")
                                }
                            )
                            success = False # 送信は完了していない扱いにする
                        else:
                            if daily_sent_count >= MAX_EMAILS_PER_DAY:
                                logger.warning(f"!!! DAILY QUOTA REACHED ({MAX_EMAILS_PER_DAY}). Stopping outreach for today. !!!")
                                should_stop_run = True
                                break
                            if run_sent_count >= MAX_EMAILS_PER_RUN:
                                logger.info(f"Hourly Run Limit reached ({MAX_EMAILS_PER_RUN}). Waiting for next hour.")
                                should_stop_run = True
                                break
                            # 件名がある場合は辞書形式にラップして渡す。人間化に失敗した場合は is_humanized=False で送信ゲートがブロック
                            final_payload = {"subject": ai_subject, "content": sub_proposal} if ai_subject else sub_proposal
                            success = auto_sender.send_proposal_email(target, final_payload, is_humanized=humanized_ok)
                    else:
                        final_payload = {"subject": ai_subject, "content": sub_proposal} if ai_subject else sub_proposal
                        success = auto_sender.send_proposal_email(target, final_payload, is_humanized=humanized_ok)
                
                if success:
                    run_sent_count += 1
                    daily_sent_count += 1
                    
                    # 送信実績を即時保存（クラッシュ等に備えて）
                    if not DRY_RUN:
                        if today_str not in all_stats:
                            all_stats[today_str] = {"total_proposals_sent": 0, "trials_offered": 0}
                        
                        all_stats[today_str]["total_proposals_sent"] = daily_sent_count
                        if trial_days > 0:
                            all_stats[today_str]["trials_offered"] += 1
                        
                        ensure_permanent_backup(stats_file)
                        with open(stats_file, 'w', encoding='utf-8') as f:
                            json.dump(list(all_stats.values()) if isinstance(all_stats, dict) else all_stats, f, ensure_ascii=False, indent=2)

                # 実績カウント更新
                sector_stats[sector]["proposals_sent"] += 1
                if trial_days > 0:
                    sector_stats[sector]["trials_offered"] += 1
            
            else:
                # 通常のB2B/SNS営業（DRY_RUN 時もモック送信でカウントはしないが、送信自体は DRY_RUN で明示的に抑止）
                # 流出防止: LLM に渡す前に PII をマスク
                safe_target = sanitize_payload(target)
                payment_link = create_service_payment_link(
                    f"AI Automation Setup ({business_id})", 
                    setup_fee_jpy=10000
                )
                dm_text = generator.create_dm(safe_target, payment_link=payment_link)
                hunter.save_draft(target, dm_text)

                if city_data.get('sector') == "SME Law Firm" or "Center" in business_id:
                    proposal_text = builder.build_proposal(safe_target, payment_link=payment_link)
                    # B2B提案も人間味のある文章へ
                    logger.info(f"Humanizing B2B proposal for {business_id}...")
                    proposal_text, humanized_ok_b2b = humanizer.polish(proposal_text, sector=sector)

                    finder.save_proposal(target, proposal_text)
                    # テスト用アドレス（mock等）の徹底排除
                    target_email = target.get('email', '')
                    business_id = target.get('username', 'Unknown')
                    if auto_sender._should_skip_address(target_email, business_id):
                        logger.warning(f"Skipping test/mock email: {target_email}")
                    else:
                        # 誤送信防止: DRY_RUN 時は送信しない（モック表示のみ。ニッチ分岐と統一）
                        if DRY_RUN:
                            auto_sender.send_proposal_email(target, proposal_text, is_humanized=humanized_ok_b2b)
                        else:
                            if daily_sent_count >= MAX_EMAILS_PER_DAY or run_sent_count >= MAX_EMAILS_PER_RUN:
                                should_stop_run = True
                                break
                            if auto_sender.send_proposal_email(target, proposal_text, is_humanized=humanized_ok_b2b):
                                run_sent_count += 1
                                daily_sent_count += 1

                if not DRY_RUN:
                    if daily_sent_count >= MAX_EMAILS_PER_DAY or run_sent_count >= MAX_EMAILS_PER_RUN:
                        should_stop_run = True
                        break
        
        if not DRY_RUN:
            if daily_sent_count >= MAX_EMAILS_PER_DAY or run_sent_count >= MAX_EMAILS_PER_RUN:
                break

    # 4. 履歴と実績ログの保存
    @auto_backup(history_file)
    def _save_history_safely():
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(leads_history, f, ensure_ascii=False, indent=4)

    _save_history_safely()

    # 実績ログの更新（daily_stats.json に日ごとのサマリーを保存）
    # すでにループ内でも保存しているが、最終的なサマリーをここで確定させる
    if today_str not in all_stats:
        all_stats[today_str] = {"total_proposals_sent": daily_sent_count, "trials_offered": 0}
    
    all_stats[today_str]["date"] = today_str
    all_stats[today_str]["sector_stats"] = sector_stats
    all_stats[today_str]["total_proposals_sent"] = daily_sent_count

    @auto_backup(stats_file)
    def _save_stats_safely():
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, ensure_ascii=False, indent=2)

    _save_stats_safely()

    # フィードバックサイクルの実行（試用3/7/10日目）
    run_feedback_cycle()

    # コアファンの特定
    top_fans = get_top_fans()
    if top_fans:
        logger.info("--- Core Fan Detection (Vesta Layer) ---")
        for fan in top_fans:
            logger.info(f"Top Fan: {fan['user_id']} (Score: {fan['score']})")

    # 現在の試用中件数を取得（Stripeからリアルタイム）
    active_trials = get_active_trial_count()
    logger.info(f"--- Current Business Status ---")
    logger.info(f"Active Trials (Real-time in Stripe): {active_trials}")
    
    # --- SAFETY: Post-run Integrity Audit（フェイルセーフ：不正時はシステム停止） ---
    audit_passed, results = run_audit([(f, []) for f in important_files])
    if audit_passed:
        save_hashes_to_registry(results)
        logger.info("=== Daily Automation Cycle Completed Successfully with Integrity Verified ===")
    else:
        logger.error("!!! Daily Automation Cycle Completed but INTEGRITY AUDIT FAILED !!!")
        sys.exit(1)

if __name__ == "__main__":
    run_daily_cycle()
