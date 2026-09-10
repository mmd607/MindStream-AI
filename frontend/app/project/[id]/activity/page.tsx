"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ActivityTimeline, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { Activity } from "@/types";

export default function ActivityPage() { const { id } = useParams<{ id: string }>(); const [items, setItems] = useState<Activity[] | null>(null); const [error, setError] = useState(""); useEffect(() => { api.activities(id).then(setItems).catch(value => setError(value instanceof Error ? value.message : "Activity unavailable")); }, [id]); if (error) return <div className="py-10"><ErrorState message={error} /></div>; if (!items) return <div className="py-10"><Loading /></div>; return <div className="py-10"><PageIntro eyebrow="Project history" title="Activity" description="A durable stream of project decisions, analysis runs, and delivery movement." /><div className="card max-w-3xl p-6"><ActivityTimeline items={items} /></div></div>; }
