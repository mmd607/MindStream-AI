"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Person } from "@/types";

export default function PersonPage({ params }: { params: Promise<{ id: string }> }) {
  const [person, setPerson] = useState<Person | null>(null); const [error, setError] = useState("");
  useEffect(() => { params.then(value => api.person(value.id)).then(setPerson).catch(value => setError(value instanceof Error ? value.message : "Person unavailable")); }, [params]);
  if (error) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><ErrorState message={error} /></div>;
  if (!person) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><Loading /></div>;
  return <div className="mx-auto max-w-[1100px] px-5 py-10 lg:px-8"><Link href="/people" className="muted text-sm">← All people</Link><PageIntro eyebrow="Person profile" title={person.name} description={person.title} /><div className="grid gap-5 lg:grid-cols-[.8fr_1.2fr]"><Card title="Current workload"><p className="muted text-sm">{person.email}</p><div className="mt-6 grid grid-cols-2 gap-3"><div className="metric-card metric-purple"><p className="muted text-xs">Active tasks</p><p className="mt-2 text-3xl font-bold">{person.active_task_count}</p></div><div className="metric-card metric-green"><p className="muted text-xs">Completed</p><p className="mt-2 text-3xl font-bold">{person.completed_task_count}</p></div></div></Card><Card title="Projects"><div className="space-y-3">{person.projects.map(project => <Link href={`/project/${project.id}`} key={project.id} className="focus-ring flex items-center justify-between rounded-xl border border-[var(--line)] p-4 hover:bg-[var(--peach)]"><span className="font-semibold">{project.name}</span><StatusBadge status={project.status} /></Link>)}</div></Card></div></div>;
}
