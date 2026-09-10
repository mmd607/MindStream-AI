"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { Card, Empty, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { SearchItem, SearchResult } from "@/types";

const groupLabels: Record<string, string> = { projects: "Projects", people: "People", requirements: "Requirements", features: "Features", apis: "APIs", tasks: "Tasks", reports: "Reports", risks: "Risks" };

export default function SearchPage() {
  const [query, setQuery] = useState(""); const [result, setResult] = useState<SearchResult | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { const initial = new URLSearchParams(window.location.search).get("q") ?? ""; setQuery(initial); if (initial.length >= 2) runSearch(initial); }, []);
  async function runSearch(value: string) { if (value.trim().length < 2) return; setBusy(true); setError(""); try { setResult(await api.search(value.trim())); } catch (errorValue) { setError(errorValue instanceof Error ? errorValue.message : "Search unavailable"); } finally { setBusy(false); } }
  function submit(event: FormEvent) { event.preventDefault(); runSearch(query); }
  const groups = result ? Object.entries(result.groups).filter(([, items]) => items.length > 0) : [];
  return <div className="mx-auto max-w-[1100px] px-5 py-10 lg:px-8"><PageIntro eyebrow="Workspace / global search" title="Search intelligence" description="Find projects, people, requirements, features, APIs, tasks, reports, and risks from one place." /><form onSubmit={submit} className="mb-8 flex gap-2"><input autoFocus value={query} onChange={event => setQuery(event.target.value)} placeholder="Search projects, people, tasks..." className="focus-ring min-w-0 flex-1 rounded-xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3" /><button disabled={busy || query.trim().length < 2} className="focus-ring rounded-xl bg-[var(--ink)] px-5 py-3 text-sm font-bold text-[var(--panel)] disabled:opacity-40">{busy ? "Searching..." : "Search"}</button></form>{error && <ErrorState message={error} />}{!result && !busy && <Empty text="Type at least two characters to search the workspace." />}{result && groups.length === 0 && <Empty text={`No intelligence found for “${result.query}”.`} />}{groups.map(([group, items]) => <Card key={group} title={groupLabels[group] ?? group}><div className="grid gap-2 sm:grid-cols-2">{items.map(item => <SearchResultLink key={`${item.kind}-${item.id}`} item={item} />)}</div></Card>)}</div>;
}

function SearchResultLink({ item }: { item: SearchItem }) { const href = item.kind === "project" ? `/project/${item.id}` : item.kind === "person" ? `/people/${item.id}` : item.kind === "report" ? `/project/${item.project_id}/reports/${item.id}` : `/project/${item.project_id}/${item.kind === "api" ? "apis" : item.kind === "risk" ? "risks" : item.kind === "task" ? "tasks" : item.kind === "requirement" ? "requirements" : "requirements"}`; return <Link href={href} className="focus-ring rounded-xl border border-[var(--line)] p-4 hover:bg-[var(--peach)]"><p className="font-semibold">{item.title}</p><p className="muted mt-1 line-clamp-2 text-sm">{item.subtitle}</p></Link>; }
