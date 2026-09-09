"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Badge, Card, Empty, ErrorState, Loading } from "@/components/ui";
import type { Project, Requirement } from "@/types";

export default function Requirements() {
  const { id } = useParams<{ id: string }>();
  const [items, setItems] = useState<Requirement[] | null>(null); const [project, setProject] = useState<Project | null>(null); const [error, setError] = useState("");
  useEffect(() => { Promise.all([api.requirements(id), api.project(id)]).then(([requirements, detail]) => { setItems(requirements); setProject(detail); }).catch((e) => setError(e.message)); }, [id]);
  if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!items || !project) return <div className="py-10"><Loading /></div>;
  const lists = [["Assumptions", project.assumptions], ["Constraints", project.constraints], ["Risks", project.risks], ["Open questions", project.open_questions]];
  return <div className="py-10"><p className="eyebrow">Blueprint / requirements</p><h1 className="mt-2 text-4xl font-bold">Requirements</h1><p className="muted mt-3">Validated behaviors, quality attributes, actors, and planning context.</p><div className="mt-8 grid gap-6 lg:grid-cols-2"><Card title="Actors"><div className="flex flex-wrap gap-2">{project.actors.length ? project.actors.map(actor => <Badge key={actor}>{actor}</Badge>) : <span className="muted text-sm">No actors generated yet.</span>}</div></Card><Card title="Objective"><p className="muted leading-7">{project.objective || "No objective generated yet."}</p></Card></div><div className="mt-6 grid gap-4 sm:grid-cols-2">{lists.map(([title, values]) => <Card key={title as string} title={title as string}><ul className="muted list-disc space-y-2 pl-5 text-sm">{(values as string[]).length ? (values as string[]).map(item => <li key={item}>{item}</li>) : <li>None recorded</li>}</ul></Card>)}</div><div className="mt-6 grid gap-4">{items.length === 0 ? <Empty /> : items.map(item => <Card key={item.id} title={item.title} action={<Badge>{item.priority}</Badge>}><div className="flex gap-2"><Badge>{item.category.replace("_", " ")}</Badge><span className="muted text-xs">source: {item.source}</span></div><p className="muted mt-4 leading-7">{item.description}</p></Card>)}</div></div>;
}
