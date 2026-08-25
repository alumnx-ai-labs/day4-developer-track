export type Category = "feature" | "bug" | "technical_debt" | "incident";
export type Priority = "low" | "medium" | "high" | "critical";
export type Status = "open" | "assigned" | "in_progress" | "resolved" | "closed";

export interface WorkRequest {
  id: number;
  title: string;
  description: string;
  category: Category;
  priority: Priority;
  status: Status;
  created_at: string;
  created_by_id: number;
  assigned_to_id: number | null;
}

export interface AuditEvent {
  id: number;
  request_id: number;
  event_type: string;
  old_value: string;
  new_value: string;
  changed_by: number;
  changed_at: string;
  reason?: string | null;
}
