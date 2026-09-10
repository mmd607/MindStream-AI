"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, PageIntro } from "@/components/ui";

export default function ProjectSectionFallback() {
  const { id, section } = useParams<{ id: string; section: string }>();
  return <div className="py-10"><PageIntro eyebrow="Project intelligence" title={section.replaceAll("-", " ")} description="This project view is available from the workspace navigation." /><Card title="Continue exploring"><p className="muted leading-7">Choose a project intelligence section from the navigation above to inspect connected data.</p><Link href={`/project/${id}`} className="focus-ring mt-5 inline-block font-bold text-[var(--accent)]">Back to dashboard →</Link></Card></div>;
}
