"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Card, Empty, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Report } from "@/types";

export default function ReportsWorkspacePage() {
  const [reports, setReports] = useState<Report[] | null>(null);
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("newest");
  const [error, setError] = useState("");
  useEffect(() => { api.allReports().then(setReports).catch(value => setError(value instanceof Error ? value.message : "Reports unavailable")); }, []);
  const visible = useMemo(() => [...(reports ?? [])].filter(item => filter === "all" || item.status === filter || item.report_type === filter).sort((a, b) => sort === "score" ? (b.score ?? 0) - (a.score ?? 0) : new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime()), [reports, filter, sort]);
  if (error) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><ErrorState message={error} /></div>;
  if (!reports) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><Loading /></div>;
  return <div className="mx-auto max-w-[1200px] px-5 py-10 lg:px-8"><PageIntro eyebrow="Workspace intelligence" title="Reports" description="A cross-project view of generated analysis, health, architecture, risk, and delivery reports." action={<div className="flex gap-2"><select aria-label="Filter reports" value={filter} onChange={event => setFilter(event.target.value)} className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--panel)] px-3 py-3 text-sm"><option value="all">All reports</option><option value="generated">Generated</option><option value="archived">Archived</option><option value="architecture">Architecture</option><option value="health">Health</option><option value="risk">Risk</option></select><select aria-label="Sort reports" value={sort} onChange={event => setSort(event.target.value)} className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--panel)] px-3 py-3 text-sm"><option value="newest">Newest</option><option value="score">Highest score</option></select></div>} />{visible.length === 0 ? <Empty text="No reports match this view." /> : <div className="grid gap-4 md:grid-cols-2">{visible.map(report => <Link key={report.id} href={`/project/${report.project_id}/reports/${report.id}`} className="focus-ring"><Card title={report.title} action={<StatusBadge status={report.status} />}><p className="eyebrow">{report.project_name ?? "Project report"}</p><p className="muted mt-3 text-sm leading-6">{report.summary}</p><div className="mt-5 flex items-center justify-between text-xs"><span className="badge">{report.report_type}</span><span className="muted">{report.score ? `${report.score} / 100` : "No score"}</span></div></Card></Link>)}</div>}</div>;
}
