"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Card, Empty, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { APIEndpoint, Feature } from "@/types";

export default function StructurePage() {
  const { id } = useParams<{ id: string }>();
  const [features, setFeatures] = useState<Feature[] | null>(null);
  const [apis, setApis] = useState<APIEndpoint[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([api.features(id), api.apis(id)]).then(([featureData, apiData]) => { setFeatures(featureData); setApis(apiData); }).catch(value => setError(value instanceof Error ? value.message : "Structure unavailable")); }, [id]);
  const modules = useMemo(() => Array.from(new Set([...(features?.map(item => item.module_name) ?? []), ...apis.map(item => item.module)])).sort(), [features, apis]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>;
  if (!features) return <div className="py-10"><Loading /></div>;
  return <div className="py-10"><PageIntro eyebrow="Product / structure" title="Product structure" description="Expand modules to follow the relationship from requirements to features, APIs, and delivery tasks." /><Card title="Interactive structure" action={<Badge>{modules.length} modules</Badge>}>{modules.length === 0 ? <Empty /> : <div className="space-y-3">{modules.map(module => { const children = features.filter(feature => feature.module_name === module); const moduleApis = apis.filter(item => item.module === module); return <details key={module} open className="rounded-2xl border border-[var(--line)] bg-[var(--paper)] p-4"><summary className="cursor-pointer list-none font-bold"><span className="mr-3 text-[var(--accent)]">◈</span>{module}<span className="muted ml-2 text-xs">{children.length} features · {moduleApis.length} APIs</span></summary><div className="mt-4 grid gap-2 pl-6 md:grid-cols-2">{children.map(feature => <div key={feature.id} className="rounded-xl border border-[var(--line)] bg-[var(--panel)] p-4"><p className="font-semibold">{feature.name}</p><p className="muted mt-1 text-sm leading-6">{feature.description}</p><div className="mt-3 flex flex-wrap gap-2"><Badge>{feature.status}</Badge>{feature.task_key && <Badge>{feature.task_key}</Badge>}</div></div>)}{children.length === 0 && <p className="muted rounded-xl border border-dashed border-[var(--line)] p-4 text-sm">Module is represented by linked API endpoints.</p>}{moduleApis.map(item => <div key={item.id} className="rounded-xl border border-dashed border-[var(--line)] bg-[var(--panel)] p-3 text-xs"><span className="badge mr-2">{item.method}</span><span className="font-mono">{item.path}</span><p className="muted mt-2">Owner: {item.owner_name}</p></div>)}</div></details>; })}</div>}</Card></div>;
}
