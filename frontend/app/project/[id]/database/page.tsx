"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Badge, Card, Empty, ErrorState, Loading } from "@/components/ui";
import type { Entity } from "@/types";

export default function DatabasePage() {
  const { id } = useParams<{ id: string }>(); const [data, setData] = useState<Entity[] | null>(null); const [error, setError] = useState("");
  useEffect(() => { api.database(id).then(setData).catch((e) => setError(e.message)); }, [id]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!data) return <div className="py-10"><Loading /></div>;
  return <div className="py-10"><p className="eyebrow">Blueprint / data model</p><h1 className="mt-2 text-4xl font-bold">Database design</h1><p className="muted mt-3">Entities, fields, keys, and generated relationships.</p><div className="mt-8 grid gap-6 lg:grid-cols-2">{data.length === 0 ? <Empty /> : data.map(entity => <Card key={entity.id} title={entity.name} action={<Badge>{entity.fields.length} fields</Badge>}><p className="muted mb-5 text-sm">{entity.description}</p><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b text-xs uppercase text-slate-500"><th className="pb-2">Field</th><th className="pb-2">Type</th><th className="pb-2">Rules</th></tr></thead><tbody>{entity.fields.map(field => <tr className="border-b last:border-0" key={field.id}><td className="py-3 font-semibold">{field.name}</td><td className="py-3 text-slate-600">{field.data_type}</td><td className="py-3">{field.primary_key && <Badge>PK</Badge>} {field.unique && <Badge>unique</Badge>} {!field.nullable && <span className="text-xs text-slate-500">required</span>}{field.foreign_key && <p className="mt-1 text-xs text-indigo-700">FK → {field.foreign_key}</p>}</td></tr>)}</tbody></table></div></Card>)}</div></div>;
}
