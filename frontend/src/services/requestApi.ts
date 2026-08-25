import type { AuditEvent, Category, Priority, Status, WorkRequest } from "../types/request";

const headers = { "Content-Type": "application/json", "X-User-Id": "1", "X-User-Role": "team_lead" };

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api/v1${path}`, { ...options, headers: { ...headers, ...(options.headers || {}) } });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "The request could not be completed.");
  return body.data as T;
}

export const listRequests = () => request<WorkRequest[]>("/requests");
export const getRequest = (id: number) => request<WorkRequest>(`/requests/${id}`);
export const getHistory = (id: number) => request<AuditEvent[]>(`/requests/${id}/history`);
export const createRequest = (payload: Pick<WorkRequest, "title" | "description" | "category" | "priority">) =>
  request<WorkRequest>("/requests", { method: "POST", body: JSON.stringify({ ...payload, status: "open" }) });
export const updateRequest = (id: number, field: "status" | "priority" | "category" | "owner", value: Status | Priority | Category | number) =>
  request<WorkRequest>(`/requests/${id}/${field}`, { method: "PATCH", body: JSON.stringify(field === "owner" ? { assigned_to_id: value } : { [field]: value }) });
