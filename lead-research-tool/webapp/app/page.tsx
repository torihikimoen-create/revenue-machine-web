"use client";

import { useEffect, useMemo, useState } from "react";

type Lead = {
  id: number;
  company_name: string;
  website?: string;
  industry: string;
  city?: string;
  contact_email?: string;
  demand_score: number;
  score_reason?: string;
  outreach_status?: "new" | "sent" | "replied";
  last_contacted_at?: string;
  outreach_note?: string;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function Page() {
  const [industry, setIndustry] = useState("産廃業");
  const [city, setCity] = useState("tokyo");
  const [leads, setLeads] = useState<Lead[]>([]);
  const [minScore, setMinScore] = useState(0);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);
  const [note, setNote] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "new" | "sent" | "replied">("all");
  const [repliedFirst, setRepliedFirst] = useState(false);

  const selectedLead = useMemo(
    () => leads.find((l) => l.id === selectedLeadId) ?? null,
    [leads, selectedLeadId]
  );

  const refreshLeads = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        min_score: String(minScore),
        limit: "100",
      });
      if (statusFilter !== "all") {
        params.set("outreach_status", statusFilter);
      }
      if (repliedFirst) {
        params.set("replied_first", "true");
      }
      const resp = await fetch(`${API_BASE}/leads?${params.toString()}`);
      const data = await resp.json();
      setLeads(data.items || []);
    } finally {
      setLoading(false);
    }
  };

  const buildExportQuery = () => {
    const params = new URLSearchParams({
      min_score: String(minScore),
    });
    if (statusFilter !== "all") {
      params.set("outreach_status", statusFilter);
    }
    if (repliedFirst) {
      params.set("replied_first", "true");
    }
    return params.toString();
  };

  useEffect(() => {
    refreshLeads();
  }, [statusFilter, repliedFirst]);

  const collect = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/collect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ industry, city, limit: 10 }),
      });
      await refreshLeads();
    } finally {
      setLoading(false);
    }
  };

  const enrichEmails = async () => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/enrich-emails`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ limit: 30 }),
      });
      await refreshLeads();
    } finally {
      setLoading(false);
    }
  };

  const runQuickScore = async (leadId: number) => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead_id: leadId,
          no_digital_manifest: true,
          no_greenfile_system: true,
          small_company: true,
          has_contact_form: true,
        }),
      });
      await refreshLeads();
    } finally {
      setLoading(false);
    }
  };

  const updateOutreachStatus = async (
    leadId: number,
    status: "new" | "sent" | "replied"
  ) => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/outreach-status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead_id: leadId,
          status,
          note: note || undefined,
        }),
      });
      await refreshLeads();
    } finally {
      setLoading(false);
    }
  };

  const generateDraft = async () => {
    if (!selectedLeadId) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/outreach-draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead_id: selectedLeadId,
          sender_name: "増本 友貴",
          sender_company: "AETHERCORE",
        }),
      });
      const data = await resp.json();
      setSubject(data.subject || "");
      setBody(data.body || "");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <h1>AETHERCORE 営業リストツール</h1>
      <p>産廃業・建設業の営業先を収集し、営業ドラフトを生成します。</p>

      <section className="card">
        <h2>1) 収集</h2>
        <div className="row">
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            <option value="産廃業">産廃業</option>
            <option value="建設業">建設業</option>
          </select>
          <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="city" />
          <button onClick={collect} disabled={loading}>
            候補を追加
          </button>
          <button onClick={enrichEmails} disabled={loading}>
            メール補完
          </button>
        </div>
      </section>

      <section className="card">
        <h2>2) リード一覧</h2>
        <div className="row" style={{ marginBottom: 8 }}>
          <input
            type="number"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value || 0))}
          />
          <button onClick={refreshLeads} disabled={loading}>
            再読み込み
          </button>
          <select
            value={statusFilter}
            onChange={(e) =>
              setStatusFilter(e.target.value as "all" | "new" | "sent" | "replied")
            }
          >
            <option value="all">全ステータス</option>
            <option value="new">未送信のみ</option>
            <option value="sent">送信済みのみ</option>
            <option value="replied">返信ありのみ</option>
          </select>
          <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input
              type="checkbox"
              checked={repliedFirst}
              onChange={(e) => setRepliedFirst(e.target.checked)}
            />
            返信あり優先
          </label>
          <button
            onClick={() => window.open(`${API_BASE}/leads/export.csv?${buildExportQuery()}`, "_blank")}
            disabled={loading}
          >
            CSVエクスポート
          </button>
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Industry</th>
              <th>Email</th>
              <th>Score</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td>{lead.id}</td>
                <td>{lead.company_name}</td>
                <td>{lead.industry}</td>
                <td>{lead.contact_email || "-"}</td>
                <td className="score">{lead.demand_score}</td>
                <td>{lead.outreach_status || "new"}</td>
                <td>
                  <div className="row">
                    <button onClick={() => runQuickScore(lead.id)} disabled={loading}>
                      クイックスコア
                    </button>
                    <button onClick={() => setSelectedLeadId(lead.id)}>選択</button>
                    <button onClick={() => updateOutreachStatus(lead.id, "sent")} disabled={loading}>
                      送信済み
                    </button>
                    <button
                      onClick={() => updateOutreachStatus(lead.id, "replied")}
                      disabled={loading}
                    >
                      返信あり
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>3) 営業ドラフト生成</h2>
        <p>選択中: {selectedLead ? `${selectedLead.company_name} (#${selectedLead.id})` : "なし"}</p>
        <button onClick={generateDraft} disabled={!selectedLeadId || loading}>
          ドラフト生成
        </button>
        <div style={{ marginTop: 10 }}>
          <input value={subject} readOnly placeholder="Subject" style={{ width: "100%" }} />
        </div>
        <div style={{ marginTop: 10 }}>
          <textarea value={body} readOnly rows={10} style={{ width: "100%" }} />
        </div>
        <div style={{ marginTop: 10 }}>
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="ステータス更新メモ（任意）"
            style={{ width: "100%" }}
          />
        </div>
      </section>
    </main>
  );
}
