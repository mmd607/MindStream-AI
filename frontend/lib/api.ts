import type { Activity, APIEndpoint, Architecture, Document, Entity, Feature, Insight, Milestone, Person, Project, ProjectComparison, ProjectMember, Report, Requirement, Risk, Role, SearchResult, Task, TraceabilityLink, Workspace } from "@/types";

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
  allPeople: (search = "") => request<Person[]>(`/people${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  person: (id: string) => request<Person>(`/projects/people/${id}`),
  personProjects: (id: string) => request<Project[]>(`/people/${id}/projects`),
  project: (id: string) => request<Project>(`/projects/${id}`),
  updateStatus: (id: string, status: string, reason = "") => request<Project>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify({ status, reason }) }),
  create: (data: unknown) => request<Project>("/projects", { method: "POST", body: JSON.stringify(data) }),
  analyze: (id: string) => request<{run_id: string; status: string; message: string}>(`/projects/${id}/analyze`, { method: "POST" }),
  requirements: (id: string) => request<Requirement[]>(`/projects/${id}/requirements`),
  features: (id: string) => request<Feature[]>(`/projects/${id}/features`),
  traceability: (id: string) => request<TraceabilityLink[]>(`/projects/${id}/traceability`),
  apis: (id: string, params = "") => request<APIEndpoint[]>(`/projects/${id}/apis${params ? `?${params}` : ""}`),
  architecture: (id: string) => request<Architecture | null>(`/projects/${id}/architecture`),
  database: (id: string) => request<Entity[]>(`/projects/${id}/database`),
  tasks: (id: string) => request<Task[]>(`/projects/${id}/tasks`),
  team: (id: string) => request<Role[]>(`/projects/${id}/team`),
  peopleForProject: (id: string) => request<ProjectMember[]>(`/projects/${id}/people`),
  reports: (id: string) => request<Report[]>(`/projects/${id}/reports`),
  generateReport: (id: string, type = "health") => request<Report>(`/projects/${id}/reports?report_type=${encodeURIComponent(type)}`, { method: "POST" }),
  regenerateReport: (projectId: string, reportId: string) => request<Report>(`/projects/${projectId}/reports/${reportId}/regenerate`, { method: "POST" }),
  allReports: (params = "") => request<Report[]>(`/reports${params ? `?${params}` : ""}`),
  report: (id: string) => request<Report>(`/projects/reports/${id}`),
  updateReport: (id: string, status: "generated" | "archived") => request<Report>(`/projects/reports/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
  compare: (ids: string[]) => request<ProjectComparison[]>(`/projects/compare?${ids.map(id => `ids=${encodeURIComponent(id)}`).join("&")}`),
  search: (query: string) => request<SearchResult>(`/projects/search?q=${encodeURIComponent(query)}`),
  insights: (id: string) => request<Insight[]>(`/projects/${id}/insights`),
  activities: (id: string) => request<Activity[]>(`/projects/${id}/activities`),
  milestones: (id: string) => request<Milestone[]>(`/projects/${id}/milestones`),
  risks: (id: string) => request<Risk[]>(`/projects/${id}/risks`),
  documentation: (id: string) => request<Document[]>(`/projects/${id}/documentation`),
};

