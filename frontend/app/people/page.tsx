"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Card, Empty, ErrorState, Loading, PageIntro, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import type { Person } from "@/types";

export default function PeoplePage() {
  const [people, setPeople] = useState<Person[] | null>(null); const [query, setQuery] = useState(""); const [error, setError] = useState("");
  useEffect(() => { api.people().then(setPeople).catch(value => setError(value instanceof Error ? value.message : "People unavailable")); }, []);
  const visible = useMemo(() => people?.filter(item => `${item.name} ${item.title}`.toLowerCase().includes(query.toLowerCase())) ?? [], [people, query]);
  if (error) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><ErrorState message={error} /></div>;
  if (!people) return <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><Loading /></div>;
  return <div className="mx-auto max-w-[1440px] px-5 py-10 lg:px-8"><PageIntro eyebrow="Workspace / people" title="People" description="See who is contributing across projects, what they own, and where their capacity is going." action={<input aria-label="Search people" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search people..." className="focus-ring rounded-xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm" />} />{visible.length === 0 ? <Empty text="No people match this search." /> : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{visible.map(person => <Link href={`/people/${person.id}`} key={person.id} className="focus-ring"><Card title={person.name} action={<span className="avatar inline-flex">{person.name.split(" ").map(part => part[0]).join("")}</span>}><p className="muted text-sm">{person.title}</p><div className="mt-5 grid grid-cols-3 gap-2"><div><p className="text-xl font-bold">{person.project_count}</p><p className="muted text-xs">projects</p></div><div><p className="text-xl font-bold">{person.active_task_count}</p><p className="muted text-xs">active tasks</p></div><div><p className="text-xl font-bold">{person.completed_task_count}</p><p className="muted text-xs">completed</p></div></div><div className="mt-5 flex flex-wrap gap-2">{person.projects.slice(0, 3).map(project => <StatusBadge key={project.id} status={project.status} />)}</div></Card></Link>)}</div>}</div>;
}
