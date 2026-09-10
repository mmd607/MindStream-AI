import type { Activity, Architecture, Document, Entity, Milestone, Person, Project, ProjectMember, Report, Requirement, Risk, Role, Task, Workspace } from "@/types";

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
  workspace: () => request<Workspace>("/projects/workspace"),
  people: (search = "") => request<Person[]>(`/projects/people${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  person: (id: string) => request<Person>(`/projects/people/${id}`),
  project: (id: string) => request<Project>(`/projects/${id}`),
  create: (data: unknown) => request<Project>("/projects", { method: "POST", body: JSON.stringify(data) }),
  analyze: (id: string) => request<{run_id: string; status: string; message: string}>(`/projects/${id}/analyze`, { method: "POST" }),
  requirements: (id: string) => request<Requirement[]>(`/projects/${id}/requirements`),
  architecture: (id: string) => request<Architecture | null>(`/projects/${id}/architecture`),
  database: (id: string) => request<Entity[]>(`/projects/${id}/database`),
  tasks: (id: string) => request<Task[]>(`/projects/${id}/tasks`),
  team: (id: string) => request<Role[]>(`/projects/${id}/team`),
  peopleForProject: (id: string) => request<ProjectMember[]>(`/projects/${id}/people`),
  reports: (id: string) => request<Report[]>(`/projects/${id}/reports`),
  generateReport: (id: string, type = "health") => request<Report>(`/projects/${id}/reports?report_type=${encodeURIComponent(type)}`, { method: "POST" }),
  report: (id: string) => request<Report>(`/projects/reports/${id}`),
  activities: (id: string) => request<Activity[]>(`/projects/${id}/activities`),
  milestones: (id: string) => request<Milestone[]>(`/projects/${id}/milestones`),
  risks: (id: string) => request<Risk[]>(`/projects/${id}/risks`),
  documentation: (id: string) => request<Document[]>(`/projects/${id}/documentation`),
};

