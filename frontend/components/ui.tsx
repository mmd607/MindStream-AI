import Link from "next/link";

export function Shell({ children }: { children: React.ReactNode }) { return <main className="min-h-screen"><header className="border-b bg-white"><div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5"><Link href="/" className="focus-ring text-lg font-bold">✦ AI Project Architect</Link><span className="eyebrow">MVP / Mock AI</span></div></header>{children}</main>; }
export function Loading() { return <div className="card p-8 text-center muted">Loading blueprint data…</div>; }
export function ErrorState({ message }: { message: string }) { return <div className="card border-red-200 bg-red-50 p-6 text-red-800"><p className="font-semibold">Couldn’t load this view</p><p className="mt-1 text-sm">{message}</p></div>; }
export function Empty({ text = "No data yet. Run analysis to generate this section." }: { text?: string }) { return <div className="card p-8 text-center muted">{text}</div>; }
export function Card({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) { return <section className="card p-6"><div className="mb-5 flex items-center justify-between gap-4"><h2 className="text-lg font-bold">{title}</h2>{action}</div>{children}</section>; }
export function Badge({ children }: { children: React.ReactNode }) { return <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">{children}</span>; }
