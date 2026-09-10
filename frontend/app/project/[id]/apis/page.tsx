"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Card, Empty, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { APIEndpoint } from "@/types";

const methods = ["ALL", "GET", "POST", "PATCH", "DELETE"];

export default function APIsPage() {
  const { id } = useParams<{ id: string }>(); const [items, setItems] = useState<APIEndpoint[] | null>(null); const [method, setMethod] = useState("ALL"); const [query, setQuery] = useState(""); const [error, setError] = useState("");
  useEffect(() => { api.apis(id).then(setItems).catch(value => setError(value instanceof Error ? value.message : "API explorer unavailable")); }, [id]);
  const visible = useMemo(() => items?.filter(item => (method === "ALL" || item.method === method) && `${item.path} ${item.module} ${item.purpose}`.toLowerCase().includes(query.toLowerCase())) ?? [], [items, method, query]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!items) return <div className="py-10"><Loading /></div>;
  return <div className="py-10"><PageIntro eyebrow="Blueprint / integration surface" title="API explorer" description="Searchable endpoints connected to their module, feature, delivery task, and owner." action={<input aria-label="Search APIs" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search paths or modules..." className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm" />} /><div className="mb-5 flex flex-wrap gap-2">{methods.map(value => <button key={value} onClick={() => setMethod(value)} className={`focus-ring rounded-xl px-3 py-2 text-xs font-bold ${method === value ? "bg-[var(--ink)] text-[var(--panel)]" : "border border-[var(--line)] bg-[var(--panel)]"}`}>{value}</button>)}</div>{visible.length === 0 ? <Empty text="No endpoints match this filter." /> : <div className="grid gap-3">{visible.map(item => <Card key={item.id} title={item.path} action={<span className="rounded-lg bg-[var(--ink)] px-2 py-1 text-xs font-bold text-[var(--panel)]">{item.method}</span>}><div className="flex flex-wrap gap-2"><Badge>{item.module}</Badge><Badge>{item.status}</Badge>{item.task_key && <Badge>{item.task_key}</Badge>}</div><p className="muted mt-4 leading-6">{item.purpose}</p><div className="mt-5 grid gap-3 text-sm sm:grid-cols-3"><div><p className="muted text-xs">Feature</p><p className="mt-1 font-semibold">{item.feature_name ?? "Unlinked"}</p></div><div><p className="muted text-xs">Owner</p><p className="mt-1 font-semibold">{item.owner_name}</p></div><div><p className="muted text-xs">Payload</p><p className="mt-1 font-semibold">{item.request_schema} → {item.response_schema}</p></div></div></Card>)}</div>}</div>;
}
