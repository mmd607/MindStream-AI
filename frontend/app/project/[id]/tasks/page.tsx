"use client";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Badge, Card, Empty, ErrorState, Loading } from "@/components/ui";
import type { Task } from "@/types";

export default function TasksPage() {
  const { id } = useParams<{ id: string }>(); const [data, setData] = useState<Task[] | null>(null); const [error, setError] = useState(""); const [filter, setFilter] = useState("all");
  useEffect(() => { api.tasks(id).then(setData).catch((e) => setError(e.message)); }, [id]);
  const visible = useMemo(() => data?.filter((x) => filter === "all" || x.priority === filter) || [], [data, filter]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!data) return <div className="py-10"><Loading /></div>;
  return <div className="py-10"><p className="eyebrow">Blueprint / execution plan</p><h1 className="mt-2 text-4xl font-bold">Tasks</h1><p className="muted mt-3">Dependency-aware implementation work assigned to team roles.</p><div className="mt-6 flex flex-wrap items-center gap-3"><span className="muted text-sm">Filter priority:</span>{["all", "critical", "high", "medium", "low"].map(x => <button key={x} onClick={() => setFilter(x)} className={`focus-ring rounded-lg px-3 py-2 text-sm font-semibold ${filter === x ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white"}`}>{x}</button>)}</div><div className="mt-6 grid gap-4">{visible.length === 0 ? <Empty /> : visible.map(item => <Card key={item.id} title={`${item.task_key} · ${item.title}`} action={<div className="flex gap-2"><Badge>{item.priority}</Badge><Badge>{item.effort} pts</Badge></div>}><div className="flex flex-wrap gap-2"><Badge>{item.role_name || "Unassigned"}</Badge><Badge>{item.task_type}</Badge><span className="muted text-sm">{item.status.replace("_", " ")}</span></div><p className="muted mt-3 leading-6">{item.description}</p><h3 className="mt-4 text-sm font-bold">Acceptance criteria</h3><ul className="muted mt-2 list-disc space-y-1 pl-5 text-sm">{item.acceptance_criteria.map(x => <li key={x}>{x}</li>)}</ul>{item.dependency_ids.length > 0 && <div className="mt-4 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">Depends on task IDs: {item.dependency_ids.join(", ")}</div>}</Card>)}</div></div>;
}
