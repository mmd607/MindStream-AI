"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, Empty, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Risk } from "@/types";

const levels = ["high", "medium", "low"];

export default function RisksPage() {
  const { id } = useParams<{ id: string }>();
  const [risks, setRisks] = useState<Risk[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.risks(id).then(setRisks).catch(value => setError(value instanceof Error ? value.message : "Risks unavailable")); }, [id]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>;
  if (!risks) return <div className="py-10"><Loading /></div>;
  const matrixRisk = (severity: string, probability: string) => risks.filter(risk => risk.severity.toLowerCase() === severity && risk.probability.toLowerCase() === probability);
  return <div className="py-10">
    <PageIntro eyebrow="Project intelligence" title="Risks" description="Delivery risks are visible, owned, and connected to the project status." />
    {risks.length === 0 ? <Empty text="No risks have been recorded for this project." /> : <>
      <Card title="Risk matrix" action={<span className="muted text-xs">Probability × impact</span>}>
        <div className="overflow-x-auto">
          <div className="min-w-[560px]">
            <div className="mb-2 grid grid-cols-[90px_repeat(3,1fr)] gap-2 text-center text-xs font-bold"><span /><span>High probability</span><span>Medium probability</span><span>Low probability</span></div>
            {levels.map(severity => <div key={severity} className="mb-2 grid grid-cols-[90px_repeat(3,1fr)] gap-2"><div className="flex items-center text-xs font-bold capitalize">{severity} impact</div>{levels.map(probability => <div key={probability} className={`min-h-20 rounded-xl border p-2 ${severity === "high" && probability !== "low" ? "border-[#e6a09b] bg-[#fff0ee]" : severity === "medium" || probability === "medium" ? "border-[#e7c979] bg-[#fff8dc]" : "border-[#b9d9c7] bg-[#edf8f0]"}`}>{matrixRisk(severity, probability).map(risk => <Link key={risk.id} href={`/project/${id}/risks`} className="mb-1 block rounded-lg bg-[var(--panel)] p-2 text-xs font-semibold shadow-sm">{risk.title}</Link>)}</div>)}</div>)}
          </div>
        </div>
      </Card>
      <div className="mt-5 grid gap-4 md:grid-cols-2">{risks.map(risk => <Card key={risk.id} title={risk.title} action={<StatusBadge status={risk.severity} />}><p className="muted leading-7">{risk.description}</p><div className="mt-4 grid grid-cols-2 gap-3 text-xs"><div className="rounded-xl bg-[var(--peach)] p-3"><span className="muted block">Probability</span><strong className="mt-1 block capitalize">{risk.probability}</strong></div><div className="rounded-xl bg-[var(--peach)] p-3"><span className="muted block">Status</span><strong className="mt-1 block capitalize">{risk.status}</strong></div></div><p className="muted mt-4 text-sm"><strong className="text-[var(--ink)]">Mitigation:</strong> {risk.mitigation}</p><p className="muted mt-3 text-xs">Owner: {risk.owner_name}</p></Card>)}</div>
    </>}
  </div>;
}
