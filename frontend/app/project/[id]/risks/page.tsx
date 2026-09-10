"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, Empty, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Risk } from "@/types";

export default function RisksPage() { const { id } = useParams<{ id: string }>(); const [risks, setRisks] = useState<Risk[] | null>(null); const [error, setError] = useState(""); useEffect(() => { api.risks(id).then(setRisks).catch(value => setError(value instanceof Error ? value.message : "Risks unavailable")); }, [id]); if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!risks) return <div className="py-10"><Loading /></div>; return <div className="py-10"><PageIntro eyebrow="Project intelligence" title="Risks" description="Delivery risks are visible, owned, and connected to the project status." />{risks.length === 0 ? <Empty text="No risks have been recorded for this project." /> : <div className="grid gap-4 md:grid-cols-2">{risks.map(risk => <Card key={risk.id} title={risk.title} action={<StatusBadge status={risk.severity} />}><p className="muted leading-7">{risk.description}</p><div className="mt-5 flex justify-between text-xs"><span className="muted">Owner: {risk.owner_name}</span><span className="font-semibold capitalize">{risk.status}</span></div></Card>)}</div>}</div>; }
