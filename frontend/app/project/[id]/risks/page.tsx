"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, Empty, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Risk } from "@/types";

const severityLevels = ["critical", "high", "medium", "low"];
const probabilityLevels = ["high", "medium", "low"];

export default function RisksPage() {
  const { id } = useParams<{ id: string }>();
  const [risks, setRisks] = useState<Risk[] | null>(null);
  const [error, setError] = useState(""); const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);
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
            {severityLevels.map(severity => <div key={severity} className="mb-2 grid grid-cols-[90px_repeat(3,1fr)] gap-2"><div className="flex items-center text-xs font-bold capitalize">{severity} impact</div>{probabilityLevels.map(probability => <div key={probability} className={`min-h-20 rounded-xl border p-2 ${severity === "critical" || (severity === "high" && probability !== "low") ? "border-[#e6a09b] bg-[#fff0ee]" : severity === "medium" || probability === "medium" ? "border-[#e7c979] bg-[#fff8dc]" : "border-[#b9d9c7] bg-[#edf8f0]"}`}>{matrixRisk(severity, probability).map(risk => <button key={risk.id} onClick={() => setSelectedRisk(risk)} className="mb-1 block w-full rounded-lg bg-[var(--panel)] p-2 text-left text-xs font-semibold shadow-sm">{risk.title}</button>)}</div>)}</div>)}
          </div>
        </div>
      </Card>
      <div className="mt-5 grid gap-4 md:grid-cols-2">{risks.map(risk => <div key={risk.id} role="button" tabIndex={0} onClick={() => setSelectedRisk(risk)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") setSelectedRisk(risk); }} className="focus-ring cursor-pointer text-left"><Card title={risk.title} action={<StatusBadge status={risk.severity} />}><p className="muted leading-7">{risk.description}</p><div className="mt-4 grid grid-cols-2 gap-3 text-xs"><div className="rounded-xl bg-[var(--peach)] p-3"><span className="muted block">Probability</span><strong className="mt-1 block capitalize">{risk.probability}</strong></div><div className="rounded-xl bg-[var(--peach)] p-3"><span className="muted block">Status</span><strong className="mt-1 block capitalize">{risk.status}</strong></div></div><p className="muted mt-4 text-sm"><strong className="text-[var(--ink)]">Mitigation:</strong> {risk.mitigation}</p><p className="muted mt-3 text-xs">Owner: {risk.owner_name} · Click for details</p></Card></div>)}</div>
      {selectedRisk && <div role="dialog" aria-modal="true" aria-label={`${selectedRisk.title} details`} className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-5" onClick={() => setSelectedRisk(null)}><div className="card max-w-xl p-6" onClick={event => event.stopPropagation()}><div className="flex items-start justify-between gap-4"><div><p className="eyebrow">Risk detail</p><h2 className="mt-2 text-2xl font-bold">{selectedRisk.title}</h2></div><button aria-label="Close risk details" onClick={() => setSelectedRisk(null)} className="icon-button">×</button></div><p className="muted mt-5 leading-7">{selectedRisk.description}</p><div className="mt-5 grid grid-cols-2 gap-3 text-sm"><Info label="Severity" value={selectedRisk.severity} /><Info label="Probability" value={selectedRisk.probability} /><Info label="Status" value={selectedRisk.status} /><Info label="Owner" value={selectedRisk.owner_name} /></div><p className="muted mt-5 text-sm leading-7"><strong className="text-[var(--ink)]">Mitigation:</strong> {selectedRisk.mitigation}</p></div></div>}
    </>}
  </div>;
}

function Info({ label, value }: { label: string; value: string }) { return <div className="rounded-xl border border-[var(--line)] p-3"><span className="muted block text-xs">{label}</span><strong className="mt-1 block capitalize">{value}</strong></div>; }
