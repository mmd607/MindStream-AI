"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { Insight } from "@/types";

export default function InsightsPage() { const { id } = useParams<{ id: string }>(); const [items, setItems] = useState<Insight[] | null>(null); const [error, setError] = useState(""); useEffect(() => { api.insights(id).then(setItems).catch(value => setError(value instanceof Error ? value.message : "Insights unavailable")); }, [id]); if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!items) return <div className="py-10"><Loading /></div>; return <div className="py-10"><PageIntro eyebrow="Project intelligence" title="AI insights" description="Deterministic observations derived from the project&apos;s current architecture, requirements, delivery, team, and risk data." /><div className="grid gap-4 md:grid-cols-2">{items.map(item => <Card key={item.kind} title={item.title} action={<span className={`status status-${item.severity === "danger" ? "at_risk" : item.severity === "success" ? "completed" : "planning"}`}>{item.severity}</span>}><p className="muted leading-7">{item.body}</p></Card>)}</div></div>; }
