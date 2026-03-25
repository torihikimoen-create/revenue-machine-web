import os
import re
import sqlite3
from datetime import datetime, timezone
from io import StringIO
from contextlib import closing
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import csv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "leads.db"
DEFAULT_THRESHOLD = int(os.getenv("LEAD_SCORE_THRESHOLD", "70"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

app = FastAPI(title="AETHERCORE 営業リストツール API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_conn()) as conn:
        conn.execute(
            """
            create table if not exists leads (
              id integer primary key autoincrement,
              company_name text not null,
              website text,
              industry text not null,
              city text,
              contact_email text,
              source text,
              no_digital_manifest integer not null default 0,
              no_greenfile_system integer not null default 0,
              small_company integer not null default 0,
              has_contact_form integer not null default 0,
              demand_score integer not null default 0,
              score_reason text,
              created_at text not null default current_timestamp,
              updated_at text not null default current_timestamp
            )
            """
        )
        conn.execute(
            "create unique index if not exists idx_leads_company_city on leads(company_name, city)"
        )
        conn.execute("create unique index if not exists idx_leads_website on leads(website)")
        existing_columns = {
            row["name"] for row in conn.execute("pragma table_info(leads)").fetchall()
        }
        # 旧カラムからの移行 or 新規追加
        for col, default in [
            ("no_digital_manifest", "0"),
            ("no_greenfile_system", "0"),
            ("small_company", "0"),
            ("has_contact_form", "0"),
            ("outreach_status", "'new'"),
            ("last_contacted_at", "NULL"),
            ("outreach_note", "NULL"),
        ]:
            if col not in existing_columns:
                conn.execute(f"alter table leads add column {col} text not null default {default}")
        conn.commit()


def score_company(
    no_digital_manifest: bool,
    no_greenfile_system: bool,
    small_company: bool,
    has_contact_form: bool,
) -> tuple[int, str]:
    score = 0
    reasons = []
    if no_digital_manifest:
        score += 30
        reasons.append("マニフェスト電子化未対応")
    if no_greenfile_system:
        score += 30
        reasons.append("グリーンファイル電子化未対応")
    if small_company:
        score += 20
        reasons.append("中小企業（上場なし）")
    if has_contact_form:
        score += 20
        reasons.append("お問い合わせフォームあり")
    if score < 50:
        reasons.append("情報収集段階")
    return score, " / ".join(reasons)


def normalize_website(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    u = url.strip()
    if not u:
        return None
    if not u.startswith("http://") and not u.startswith("https://"):
        u = "https://" + u
    return u


def extract_first_email(text: str) -> Optional[str]:
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    match = re.search(pattern, text)
    if not match:
        return None
    email = match.group(0)
    if email.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".webp")):
        return None
    return email


def scrape_contact_email(website: Optional[str]) -> Optional[str]:
    normalized = normalize_website(website)
    if not normalized:
        return None
    headers = {"User-Agent": "AethercoreLeadTool/0.2 (+contact enrichment)"}
    try:
        resp = requests.get(normalized, timeout=8, headers=headers)
        if resp.ok:
            email = extract_first_email(resp.text)
            if email:
                return email
            for path in ("/contact", "/contact-us", "/inquiry", "/company"):
                sub = requests.get(urljoin(normalized, path), timeout=8, headers=headers)
                if sub.ok:
                    email = extract_first_email(sub.text)
                    if email:
                        return email
    except Exception:
        return None
    return None


def fetch_serpapi_map_leads(industry: str, city: str, limit: int) -> list[dict]:
    if not SERPAPI_KEY:
        return []
    params = {
        "engine": "google_maps",
        "q": f"{industry} {city}",
        "hl": "ja",
        "gl": "jp",
        "api_key": SERPAPI_KEY,
    }
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("local_results", [])[:limit]

    leads: list[dict] = []
    for item in items:
        title = item.get("title")
        if not title:
            continue
        links = item.get("links") or {}
        website = links.get("website") or item.get("website")
        leads.append(
            {
                "company_name": title,
                "website": website,
                "industry": industry,
                "city": city,
                "contact_email": None,
                "source": "serpapi-google-maps",
            }
        )
    return leads


# ── 営業メールテンプレート ─────────────────────────────────────────

SANPAI_SUBJECT = "産廃マニフェスト管理をAIで自動化するサービスのご案内"
SANPAI_BODY = """\
はじめまして。AETHERCOREと申します。
産廃業者様向けのAI審査・診断サービスをご提供しております。
━━━━━━━━━━━━━━━━━━
【実際の診断例】
▼ 現場写真を1枚送信
▼ AIの判定結果
■ 推定品目：混合廃棄物（金属くず・廃プラスチック類・木くず・ガラスくず等）
■ 処分区分：中間処理（選別・破砕）→ 金属類はリサイクル、残渣は最終処分
■ 注意：銅線（非鉄金属）が混入、有価物としてリサイクル可能
　　　　液体容器の残留物確認が必要
━━━━━━━━━━━━━━━━━━
「これ何の品目？」が写真1枚で即解決します。
マニフェスト・契約書のテキストをコピペするだけでAI審査も可能です。
【料金】
・無料診断：登録から7日間の経過、または5回使用後（1回で3枚までの画像診断ができます）
・月額プラン：14,800円（税込）／月額契約後は回数・枚数制限なしでご利用いただけます
LINEで写真を送るだけ。現場担当者様がそのまま使えます。
ご興味があればお気軽にご連絡ください。
AETHERCORE
https://torihikimoen-create.github.io/revenue-machine-web/
torihikimoen@gmail.com
TEL：070-9001-6242"""

KENSETSU_SUBJECT = "安全書類の確認作業をAIで自動化するサービスのご案内"
KENSETSU_BODY = """\
突然のご連絡失礼いたします。
AI業務効率化ツールを提供しているAETHERCOREの増本と申します。
御社では、作業員名簿・施工体制台帳などの
グリーンファイルのチェック作業に時間をとられていませんか？
弊社のAI審査ボットをLINEに追加いただくだけで、
書類の写真を送るだけで不備を即座に自動チェックします。
【特徴】
・24時間365日、数秒でチェック完了
・記載漏れ・様式ミスを自動検出
・LINEで完結（アプリ不要）
・まず無料でお試しいただけます
【料金】
・無料診断：登録から7日間の経過、または5回使用後（1回で3枚までの画像診断ができます）
・月額プラン：14,800円（税込）／月額契約後は回数・枚数制限なしでご利用いただけます
ご興味があればお気軽にご連絡ください。
AETHERCORE
https://torihikimoen-create.github.io/revenue-machine-web/
torihikimoen@gmail.com
TEL：070-9001-6242"""


class CollectRequest(BaseModel):
    industry: str = Field(default="産廃業")
    city: str = Field(default="tokyo")
    limit: int = Field(default=10, ge=1, le=50)


class ScoreRequest(BaseModel):
    lead_id: int
    no_digital_manifest: bool = False
    no_greenfile_system: bool = False
    small_company: bool = False
    has_contact_form: bool = False


class OutreachRequest(BaseModel):
    lead_id: int
    sender_name: str = "増本 友貴"
    sender_company: str = "AETHERCORE"


class EnrichEmailRequest(BaseModel):
    lead_id: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)


class OutreachStatusRequest(BaseModel):
    lead_id: int
    status: str = Field(pattern="^(new|sent|replied)$")
    note: Optional[str] = None


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/collect")
def collect_candidates(payload: CollectRequest) -> dict:
    source_used = "seed-generator"
    candidates = []
    errors = []
    try:
        candidates = fetch_serpapi_map_leads(payload.industry, payload.city, payload.limit)
        if candidates:
            source_used = "serpapi-google-maps"
    except Exception as exc:
        errors.append(str(exc))

    inserted = 0
    skipped = 0
    with closing(get_conn()) as conn:
        if not candidates:
            candidates = []
            for idx in range(payload.limit):
                candidates.append(
                    {
                        "company_name": f"{payload.city.title()} {payload.industry} Sample {idx + 1}",
                        "website": f"https://example-{payload.industry}-{idx + 1}.com",
                        "industry": payload.industry,
                        "city": payload.city,
                        "contact_email": f"info{idx + 1}@example-{payload.industry}.com",
                        "source": "seed-generator",
                    }
                )
        for c in candidates:
            website = normalize_website(c.get("website"))
            company_name = c.get("company_name")
            city = c.get("city")
            exists = conn.execute(
                """
                select id from leads
                where (company_name = ? and city = ?)
                   or (website is not null and website = ?)
                limit 1
                """,
                (company_name, city, website),
            ).fetchone()
            if exists:
                skipped += 1
                continue
            conn.execute(
                """
                insert into leads(company_name, website, industry, city, contact_email, source)
                values (?, ?, ?, ?, ?, ?)
                """,
                (
                    company_name,
                    website,
                    c.get("industry"),
                    city,
                    c.get("contact_email"),
                    c.get("source"),
                ),
            )
            inserted += 1
        conn.commit()
    return {"inserted": inserted, "skipped": skipped, "source": source_used, "errors": errors}


@app.post("/score")
def apply_score(payload: ScoreRequest) -> dict:
    score, reason = score_company(
        payload.no_digital_manifest,
        payload.no_greenfile_system,
        payload.small_company,
        payload.has_contact_form,
    )
    with closing(get_conn()) as conn:
        cur = conn.execute(
            """
            update leads
            set no_digital_manifest = ?,
                no_greenfile_system = ?,
                small_company = ?,
                has_contact_form = ?,
                demand_score = ?,
                score_reason = ?,
                updated_at = current_timestamp
            where id = ?
            """,
            (
                int(payload.no_digital_manifest),
                int(payload.no_greenfile_system),
                int(payload.small_company),
                int(payload.has_contact_form),
                score,
                reason,
                payload.lead_id,
            ),
        )
        conn.commit()
    if cur.rowcount == 0:
        return {"updated": False, "error": "Lead not found"}
    return {"updated": True, "score": score, "reason": reason}


@app.get("/leads")
def list_leads(
    min_score: int = Query(default=0, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=200),
    industry: Optional[str] = None,
    outreach_status: Optional[str] = Query(default=None, pattern="^(new|sent|replied)$"),
    replied_first: bool = Query(default=False),
) -> dict:
    query = "select * from leads where demand_score >= ?"
    params: list = [min_score]
    if industry:
        query += " and industry = ?"
        params.append(industry)
    if outreach_status:
        query += " and outreach_status = ?"
        params.append(outreach_status)
    if replied_first:
        query += " order by case when outreach_status = 'replied' then 0 else 1 end, demand_score desc, id desc"
    else:
        query += " order by demand_score desc, id desc"
    query += " limit ?"
    params.append(limit)

    with closing(get_conn()) as conn:
        rows = conn.execute(query, params).fetchall()

    return {
        "threshold": DEFAULT_THRESHOLD,
        "count": len(rows),
        "items": [dict(r) for r in rows],
    }


@app.get("/leads/export.csv")
def export_leads_csv(
    min_score: int = Query(default=0, ge=0, le=100),
    industry: Optional[str] = None,
    outreach_status: Optional[str] = Query(default=None, pattern="^(new|sent|replied)$"),
    replied_first: bool = Query(default=False),
) -> StreamingResponse:
    query = "select * from leads where demand_score >= ?"
    params: list = [min_score]
    if industry:
        query += " and industry = ?"
        params.append(industry)
    if outreach_status:
        query += " and outreach_status = ?"
        params.append(outreach_status)
    if replied_first:
        query += " order by case when outreach_status = 'replied' then 0 else 1 end, demand_score desc, id desc"
    else:
        query += " order by demand_score desc, id desc"
    with closing(get_conn()) as conn:
        rows = [dict(r) for r in conn.execute(query, params).fetchall()]

    output = StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    else:
        writer = csv.writer(output)
        writer.writerow(["id", "company_name", "industry", "demand_score"])
    output.seek(0)
    filename = f"leads_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


@app.post("/outreach-draft")
def outreach_draft(payload: OutreachRequest) -> dict:
    with closing(get_conn()) as conn:
        row = conn.execute("select * from leads where id = ?", (payload.lead_id,)).fetchone()
    if not row:
        return {"ok": False, "error": "Lead not found"}

    lead = dict(row)
    industry = lead.get("industry", "")

    if industry == "産廃業":
        subject = SANPAI_SUBJECT
        body = SANPAI_BODY
    elif industry == "建設業":
        subject = KENSETSU_SUBJECT
        body = KENSETSU_BODY
    else:
        # 業界不明時は産廃テンプレをデフォルト
        subject = SANPAI_SUBJECT
        body = SANPAI_BODY

    return {"ok": True, "subject": subject, "body": body}


@app.post("/enrich-emails")
def enrich_emails(payload: EnrichEmailRequest) -> dict:
    with closing(get_conn()) as conn:
        if payload.lead_id:
            targets = conn.execute(
                "select id, website from leads where id = ? limit 1", (payload.lead_id,)
            ).fetchall()
        else:
            targets = conn.execute(
                """
                select id, website from leads
                where (contact_email is null or contact_email = '')
                order by demand_score desc, id desc
                limit ?
                """,
                (payload.limit,),
            ).fetchall()

        updated = 0
        for t in targets:
            email = scrape_contact_email(t["website"])
            if not email:
                continue
            conn.execute(
                "update leads set contact_email = ?, updated_at = current_timestamp where id = ?",
                (email, t["id"]),
            )
            updated += 1
        conn.commit()
    return {"processed": len(targets), "updated": updated}


@app.post("/outreach-status")
def update_outreach_status(payload: OutreachStatusRequest) -> dict:
    timestamp = (
        datetime.now(timezone.utc).isoformat(timespec="seconds")
        if payload.status in {"sent", "replied"}
        else None
    )
    with closing(get_conn()) as conn:
        cur = conn.execute(
            """
            update leads
            set outreach_status = ?,
                outreach_note = ?,
                last_contacted_at = coalesce(?, last_contacted_at),
                updated_at = current_timestamp
            where id = ?
            """,
            (payload.status, payload.note, timestamp, payload.lead_id),
        )
        conn.commit()
    if cur.rowcount == 0:
        return {"updated": False, "error": "Lead not found"}
    return {"updated": True}
