"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { Badge, Card, Empty, ErrorState, Loading, PageIntro } from "@/components/ui";
import { api } from "@/lib/api";
import type { APIEndpoint, Architecture, Feature, ProjectMember, Task } from "@/types";

type Point = { x: number; y: number };
type GraphComponent = { name: string; responsibility: string };

export default function ArchitecturePage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<Architecture | null | undefined>(undefined);
  const [features, setFeatures] = useState<Feature[]>([]);
  const [apis, setApis] = useState<APIEndpoint[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<"2d" | "3d">("2d");
  const [selected, setSelected] = useState("");
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState<Point>({ x: 0, y: 0 });
  const [drag, setDrag] = useState<{ start: Point; origin: Point } | null>(null);

  useEffect(() => {
    Promise.all([api.architecture(id), api.features(id), api.apis(id), api.tasks(id), api.peopleForProject(id)])
      .then(([architecture, featureData, apiData, taskData, memberData]) => {
        setData(architecture);
        setFeatures(featureData);
        setApis(apiData);
        setTasks(taskData);
        setMembers(memberData);
      })
      .catch(value => setError(value instanceof Error ? value.message : "Architecture unavailable"));
  }, [id]);

  const graphComponents = useMemo<GraphComponent[]>(() => { if (!data) return []; const components = [...data.components_json]; const names = new Set(components.map(item => item.name)); apis.forEach(item => { if (!names.has(item.module)) { names.add(item.module); components.push({ name: item.module, responsibility: `Application module for ${item.module.toLowerCase()} workflows and connected API operations.` }); } }); return components; }, [data, apis]);
  const component = graphComponents.find(item => item.name === selected) ?? graphComponents[0];
  const selectedName = selected || component?.name || "Project core";
  const selectedApis = useMemo(() => apis.filter(item => item.module === selectedName), [apis, selectedName]);
  const selectedFeatures = useMemo(() => features.filter(item => item.module_name === selectedName || selectedApis.some(apiItem => apiItem.feature_name === item.name)), [features, selectedName, selectedApis]);
  const selectedTasks = useMemo(() => tasks.filter(item => item.module_name === selectedName || selectedApis.some(apiItem => apiItem.task_key === item.task_key)), [tasks, selectedName, selectedApis]);
  const owner = members.find(member => member.modules.includes(selectedName))?.name ?? members[0]?.name ?? "Unassigned";
  const selectedDescription = selectedName === "Database" ? "Persistent project entities, relationships, constraints, and generated blueprint records." : selectedName === "External integrations" ? "External providers and service boundaries connected through the API layer." : component?.responsibility ?? "The project core coordinates the connected architecture nodes.";

  if (error) return <div className="py-10"><ErrorState message={error} /></div>;
  if (data === undefined) return <div className="py-10"><Loading /></div>;
  if (!data) return <div className="py-10"><Empty text="Analyze this project to create an architecture view." /></div>;

  function resetView() { setScale(1); setOffset({ x: 0, y: 0 }); }
  function zoom(delta: number) { setScale(value => Math.max(.65, Math.min(1.8, Number((value + delta).toFixed(2))))); }
  function move(event: React.PointerEvent<HTMLDivElement>) {
    if (!drag) return;
    setOffset({ x: drag.origin.x + event.clientX - drag.start.x, y: drag.origin.y + event.clientY - drag.start.y });
  }

  return <div className="py-10">
    <PageIntro eyebrow="Blueprint / system design" title="Architecture" description={`${data.style} · A visual map of the system boundaries, technologies, and communication paths.`} action={<div className="flex rounded-xl border border-[var(--line)] bg-[var(--panel)] p-1"><button onClick={() => setMode("2d")} className={`focus-ring rounded-lg px-3 py-2 text-sm font-bold ${mode === "2d" ? "bg-[var(--ink)] text-[var(--panel)]" : ""}`}>2D structure</button><button onClick={() => setMode("3d")} className={`focus-ring rounded-lg px-3 py-2 text-sm font-bold ${mode === "3d" ? "bg-[var(--ink)] text-[var(--panel)]" : ""}`}>3D structure</button></div>} />
    <div className="grid gap-5 lg:grid-cols-[1fr_.38fr]">
      <Card title={mode === "2d" ? "System graph" : "Spatial structure"} action={mode === "3d" ? <div className="flex items-center gap-1"><button aria-label="Zoom out" title="Zoom out" onClick={() => zoom(-.1)} className="icon-button px-2 py-1">−</button><button aria-label="Reset view" title="Reset view" onClick={resetView} className="icon-button px-2 py-1 text-xs">Reset</button><button aria-label="Zoom in" title="Zoom in" onClick={() => zoom(.1)} className="icon-button px-2 py-1">+</button></div> : <Badge>{graphComponents.length} modules</Badge>}>
        {mode === "2d" ? <TwoDGraph components={graphComponents} selected={selectedName} onSelect={setSelected} /> : <ThreeDGraph components={graphComponents} selected={selectedName} onSelect={setSelected} scale={scale} offset={offset} dragging={Boolean(drag)} onPointerDown={event => setDrag({ start: { x: event.clientX, y: event.clientY }, origin: offset })} onPointerMove={move} onPointerUp={() => setDrag(null)} onPointerLeave={() => setDrag(null)} />}
      </Card>
      <Card title={selectedName}><p className="eyebrow">Selected node</p><p className="muted mt-4 text-sm leading-7">{selectedDescription}</p><div className="mt-5 space-y-3"><Info label="Owner" value={owner} /><Info label="Features" value={selectedName === "Project core" ? features.length : selectedFeatures.length} /><Info label="APIs" value={selectedName === "Project core" ? apis.length : selectedApis.length} /><Info label="Tasks" value={selectedName === "Project core" ? tasks.length : selectedTasks.length} /><Info label="Dependencies" value={data.communication_paths.length} /></div><div className="mt-5 flex flex-wrap gap-2">{(selectedName === "Project core" ? data.communication_paths : data.communication_paths.filter(path => path.toLowerCase().includes(selectedName.toLowerCase()))).slice(0, 4).map(path => <Badge key={path}>{path}</Badge>)}</div></Card>
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-2"><Card title="Architecture rationale"><p className="muted leading-7">{data.rationale}</p><h3 className="mt-6 text-sm font-bold">Communication paths</h3><div className="mt-3 space-y-2">{data.communication_paths.map(path => <div className="rounded-xl bg-[var(--paper)] p-3 text-sm" key={path}>{path}</div>)}</div></Card><Card title="Technology decisions"><div className="space-y-3">{data.technologies_json.map(item => <div className="rounded-xl border border-[var(--line)] p-4" key={item.name}><div className="flex justify-between gap-3"><strong>{item.name}</strong><Badge>chosen</Badge></div><p className="muted mt-2 text-sm">{item.rationale}</p></div>)}</div></Card></div>
  </div>;
}

function Info({ label, value }: { label: string; value: string | number }) { return <div className="rounded-xl border border-[var(--line)] p-3"><p className="muted text-xs">{label}</p><p className="mt-1 text-sm font-semibold">{value}</p></div>; }

function TwoDGraph({ components, selected, onSelect }: { components: GraphComponent[]; selected: string; onSelect: (name: string) => void }) { return <div className="relative min-h-[440px] overflow-hidden rounded-2xl bg-[var(--peach)] p-5"><div className="mx-auto flex max-w-2xl flex-col items-center gap-4 py-4"><Node label="Web client" symbol="01" /><span className="text-2xl text-[var(--accent)]">↓</span><Node label="API layer" symbol="02" /><span className="text-2xl text-[var(--accent)]">↓</span><div className="grid w-full gap-3 sm:grid-cols-2">{components.map((item, index) => <button key={item.name} onClick={() => onSelect(item.name)} className={`focus-ring rounded-2xl border-2 bg-[var(--panel)] p-4 text-left shadow-sm transition hover:-translate-y-1 ${selected === item.name ? "border-[var(--accent)]" : "border-[var(--line)]"}`}><span className="eyebrow">Module 0{index + 1}</span><span className="mt-2 block font-bold">{item.name}</span><span className="muted mt-1 block text-xs">{item.responsibility}</span></button>)}</div><span className="text-2xl text-[var(--accent)]">↓</span><Node label="Relational database" symbol="DB" /></div><p className="absolute bottom-4 left-5 text-xs font-semibold text-[var(--muted)]">Select a module to inspect ownership and connected delivery data.</p></div>; }

function ThreeDGraph({ components, selected, onSelect, scale, offset, dragging, onPointerDown, onPointerMove, onPointerUp, onPointerLeave }: { components: GraphComponent[]; selected: string; onSelect: (name: string) => void; scale: number; offset: Point; dragging: boolean; onPointerDown: (event: React.PointerEvent<HTMLDivElement>) => void; onPointerMove: (event: React.PointerEvent<HTMLDivElement>) => void; onPointerUp: () => void; onPointerLeave: () => void }) {
  const positions = components.map((item, index) => { const angle = (index / Math.max(components.length, 1)) * Math.PI * 2 - Math.PI / 2; return { item, x: Math.cos(angle) * 245, y: Math.sin(angle) * 145, z: index * 8 }; });
  return <div onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerUp} onPointerLeave={onPointerLeave} className={`relative min-h-[520px] overflow-hidden rounded-2xl bg-[radial-gradient(circle_at_center,var(--panel),var(--peach))] ${dragging ? "cursor-grabbing" : "cursor-grab"}`}><div className="absolute bottom-4 left-4 z-20 rounded-lg bg-[var(--panel)]/80 px-3 py-2 text-xs font-semibold text-[var(--muted)]">Drag to pan · use controls to zoom</div><div className="absolute inset-0 [perspective:1000px]"><div className="absolute left-1/2 top-1/2 h-0 w-0 [transform-style:preserve-3d]" style={{ transform: `translate3d(calc(-50% + ${offset.x}px), calc(-50% + ${offset.y}px), 0) scale(${scale}) rotateX(12deg) rotateY(-8deg)`, transformOrigin: "center" }}>{positions.map(({ item, x, y, z }) => <div key={`${item.name}-line`} className="pointer-events-none absolute left-0 top-0 h-1 origin-left bg-[var(--accent)]/35" style={{ width: `${Math.hypot(x, y)}px`, transform: `rotate(${Math.atan2(y, x) * 180 / Math.PI}deg) translateZ(${z / 2}px)` }} />)}<div className="pointer-events-none absolute left-0 top-0 h-1 origin-left bg-[var(--accent)]/35" style={{ width: "230px", transform: "rotate(90deg)" }} /><div className="pointer-events-none absolute left-0 top-0 h-1 origin-left bg-[var(--accent)]/35" style={{ width: "363px", transform: "rotate(-34deg)" }} /><div className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 [transform:translateZ(120px)]"><NodeButton label="Project core" symbol="CORE" selected={selected === "Project core"} onClick={() => onSelect("Project core")} /></div>{positions.map(({ item, x, y, z }, index) => <div key={item.name} className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2" style={{ transform: `translate3d(${x}px, ${y}px, ${z}px)` }}><NodeButton label={item.name} symbol={`M0${index + 1}`} selected={selected === item.name} onClick={() => onSelect(item.name)} /></div>)}<div className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2" style={{ transform: "translate3d(0, 230px, -20px)" }}><NodeButton label="Database" symbol="DB" selected={selected === "Database"} onClick={() => onSelect("Database")} /></div><div className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2" style={{ transform: "translate3d(300px, -205px, 40px)" }}><NodeButton label="External integrations" symbol="EXT" selected={selected === "External integrations"} onClick={() => onSelect("External integrations")} /></div></div></div></div>;
}

function Node({ label, symbol }: { label: string; symbol: string }) { return <div className="w-56 rounded-2xl border-2 border-[var(--accent)] bg-[var(--panel)] p-4 text-center shadow-sm"><span className="eyebrow">{symbol}</span><p className="mt-1 font-bold">{label}</p></div>; }
function NodeButton({ label, symbol, selected, onClick }: { label: string; symbol: string; selected: boolean; onClick: () => void }) { return <button onClick={event => { event.stopPropagation(); onClick(); }} className={`focus-ring w-44 rounded-2xl border-2 bg-[var(--panel)] p-4 text-center shadow-[0_18px_30px_rgba(40,27,49,.16)] transition hover:scale-105 ${selected ? "border-[var(--accent)] ring-4 ring-[var(--accent)]/20" : "border-[var(--line)]"}`}><span className="eyebrow">{symbol}</span><span className="mt-1 block font-bold">{label}</span></button>; }
