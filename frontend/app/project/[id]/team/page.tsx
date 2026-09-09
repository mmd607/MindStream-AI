"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Card, Empty, ErrorState, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import type { Role } from "@/types";

export default function TeamPage() {
  const { id } = useParams<{ id: string }>(); const [data, setData] = useState<Role[] | null>(null); const [error, setError] = useState("");
  useEffect(() => { api.team(id).then(setData).catch((e) => setError(e.message)); }, [id]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!data) return <div className="py-10"><Loading /></div>;
  return <div className="py-10"><p className="eyebrow">Blueprint / ownership</p><h1 className="mt-2 text-4xl font-bold">Team roles</h1><p className="muted mt-3">Responsibilities and task assignments from the generated plan.</p><div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{data.length === 0 ? <Empty /> : data.map(role => <Card key={role.id} title={role.name} action={<Badge>{role.task_count} tasks</Badge>}><p className="muted text-sm leading-6">{role.description}</p>{role.assigned_task_titles.length > 0 && <><h3 className="mt-5 text-sm font-bold">Assigned responsibilities</h3><ul className="muted mt-2 list-disc space-y-1 pl-5 text-sm">{role.assigned_task_titles.map(title => <li key={title}>{title}</li>)}</ul></>}</Card>)}</div></div>;
}
