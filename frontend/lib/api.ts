import type { Architecture, Document, Entity, Project, Requirement, Role, Task } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) }, cache: "no-store" });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail?.message ?? body?.message ?? "Request failed");
  }
  return response.json();
}

export const api = {
  projects: () => request<Project[]>("/projects"),
  project: (id: string) => request<Project>(`/projects/${id}`),
  create: (data: unknown) => request<Project>("/projects", { method: "POST", body: JSON.stringify(data) }),
  analyze: (id: string) => request<{run_id: string; status: string; message: string}>(`/projects/${id}/analyze`, { method: "POST" }),
  requirements: (id: string) => request<Requirement[]>(`/projects/${id}/requirements`),
  architecture: (id: string) => request<Architecture | null>(`/projects/${id}/architecture`),
  database: (id: string) => request<Entity[]>(`/projects/${id}/database`),
  tasks: (id: string) => request<Task[]>(`/projects/${id}/tasks`),
  team: (id: string) => request<Role[]>(`/projects/${id}/team`),
  documentation: (id: string) => request<Document[]>(`/projects/${id}/documentation`),
};

