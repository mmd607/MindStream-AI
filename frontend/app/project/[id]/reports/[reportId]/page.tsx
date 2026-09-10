"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { Report } from "@/types";

export default function ReportDetailPage() {
  const { reportId } = useParams<{ id: string; reportId: string }>(); const [report, setReport] = useState<Report | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { api.report(reportId).then(setReport).catch(value => setError(value instanceof Error ? value.message : "Report unavailable")); }, [reportId]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!report) return <div className="py-10"><Loading /></div>;
  const currentReport = report;
  async function archive() { setBusy(true); try { setReport(await api.updateReport(currentReport.id, currentReport.status === "archived" ? "generated" : "archived")); } catch (value) { setError(value instanceof Error ? value.message : "Could not update report"); } finally { setBusy(false); } }
  return <div className="py-10"><Link href={`/project/${report.project_id}/reports`} className="muted text-sm">← Reports</Link><PageIntro eyebrow={`${report.report_type} / AI analysis`} title={report.title} description={`Generated ${new Date(report.generated_at).toLocaleString()} by ${report.generated_by}.`} action={<button onClick={archive} disabled={busy} className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm font-bold">{busy ? "Saving..." : report.status === "archived" ? "Restore report" : "Archive report"}</button>} /><div className="grid gap-5 lg:grid-cols-[1fr_.35fr]"><article className="card p-6"><pre className="whitespace-pre-wrap font-sans text-sm leading-7">{report.content}</pre></article><Card title="Report score"><p className="text-5xl font-bold">{report.score ?? "—"}<span className="muted text-base"> / 100</span></p><p className="muted mt-4 text-sm">This report is generated from the project&apos;s current structured data.</p></Card></div></div>;
}
