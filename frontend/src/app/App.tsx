import { useEffect, useState } from "react";
import { ArrowUpRight, ClipboardList, Clock3, Filter, Plus, RefreshCw, ShieldCheck, SlidersHorizontal, X } from "lucide-react";
import { createRequest, getHistory, getRequest, listRequests, updateRequest } from "../services/requestApi";
import type { AuditEvent, Category, Priority, Status, WorkRequest } from "../types/request";

const statuses: Status[] = ["open", "assigned", "in_progress", "resolved", "closed"];
const categories: Category[] = ["feature", "bug", "technical_debt", "incident"];
const priorities: Priority[] = ["low", "medium", "high", "critical"];

function label(value: string) { return value.replace(/_/g, " ").replace(/\b\w/g, (letter: string) => letter.toUpperCase()); }

export function App() {
  const [requests, setRequests] = useState<WorkRequest[]>([]);
  const [selected, setSelected] = useState<WorkRequest | null>(null);
  const [history, setHistory] = useState<AuditEvent[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState<Status | "all">("all");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    setBusy(true); setError("");
    try { setRequests(await listRequests()); } catch (err) { setError(err instanceof Error ? err.message : "Unable to reach TeamPulse."); }
    finally { setBusy(false); }
  }
  async function openRequest(request: WorkRequest) {
    setSelected(request); setError("");
    try { const [fresh, events] = await Promise.all([getRequest(request.id), getHistory(request.id)]); setSelected(fresh); setHistory(events); }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to open this request."); }
  }
  async function mutate(field: "status" | "priority" | "category" | "owner", value: Status | Priority | Category | number) {
    if (!selected) return;
    setBusy(true); setError("");
    try { const updated = await updateRequest(selected.id, field, value); setSelected(updated); setRequests((current) => current.map((item) => item.id === updated.id ? updated : item)); setHistory(await getHistory(updated.id)); }
    catch (err) { setError(err instanceof Error ? err.message : "Update failed."); }
    finally { setBusy(false); }
  }
  useEffect(() => { void refresh(); }, []);

  const visible = filter === "all" ? requests : requests.filter((request) => request.status === filter);
  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><span className="brand-mark"><ClipboardList size={18} /></span><span>Team<span className="brand-accent">Pulse</span></span></div>
      <div className="topbar-meta"><span className="live-dot" /> Local workspace <span className="divider" /> <ShieldCheck size={15} /> Team lead</div>
    </header>
    <main className="workspace">
      <section className="intro-row">
        <div><p className="eyebrow">Engineering work intake</p><h1>Make the work visible.</h1><p className="lede">A focused queue for the decisions that move engineering forward.</p></div>
        <button className="primary-button" onClick={() => setShowCreate(true)}><Plus size={17} /> New request</button>
      </section>
      <section className="summary-grid">
        <div className="summary-card summary-card-main"><div className="summary-label">Active queue</div><strong>{requests.filter((r) => r.status !== "closed").length.toString().padStart(2, "0")}</strong><span>requests in motion</span><ArrowUpRight className="summary-icon" size={22} /></div>
        <div className="summary-card"><div className="summary-label">Needs attention</div><strong>{requests.filter((r) => r.priority === "critical" || r.priority === "high").length.toString().padStart(2, "0")}</strong><span>high priority items</span></div>
        <div className="summary-card"><div className="summary-label">Audit coverage</div><strong>100<span className="small-percent">%</span></strong><span>tracked changes</span></div>
      </section>
      <section className="queue-layout">
        <div className="queue-panel">
          <div className="panel-heading"><div><p className="eyebrow">The queue</p><h2>All engineering requests</h2></div><button className="icon-button" title="Refresh queue" onClick={() => void refresh()}><RefreshCw size={17} className={busy ? "spin" : ""} /></button></div>
          <div className="queue-toolbar"><div className="filter-label"><Filter size={15} /> Filter by status</div><div className="filter-pills"><button className={filter === "all" ? "filter-pill active" : "filter-pill"} onClick={() => setFilter("all")}>All <span>{requests.length}</span></button>{statuses.map((status) => <button key={status} className={filter === status ? "filter-pill active" : "filter-pill"} onClick={() => setFilter(status)}>{label(status)} <span>{requests.filter((r) => r.status === status).length}</span></button>)}</div></div>
          {error && <div className="error-banner">{error}</div>}
          <div className="request-list">{visible.length === 0 && !busy ? <div className="empty-state"><SlidersHorizontal size={22} /><p>No requests in this view.</p><button onClick={() => setShowCreate(true)}>Create the first one</button></div> : visible.map((request) => <button className={selected?.id === request.id ? "request-row selected" : "request-row"} key={request.id} onClick={() => void openRequest(request)}><div className={`category-stripe category-${request.category}`} /><div className="request-row-content"><div className="row-top"><span className="request-id">TP-{String(request.id).padStart(4, "0")}</span><span className={`priority priority-${request.priority}`}>{label(request.priority)}</span></div><strong>{request.title}</strong><p>{request.description}</p><div className="row-bottom"><span className={`status status-${request.status}`}>{label(request.status)}</span><span className="category-name">{label(request.category)}</span><span className="assigned">{request.assigned_to_id ? `Owner #${request.assigned_to_id}` : "Unassigned"}</span></div></div></button>)}</div>
        </div>
        <aside className="detail-panel">{selected ? <><div className="detail-heading"><div><span className="request-id">TP-{String(selected.id).padStart(4, "0")}</span><h2>{selected.title}</h2></div><button className="icon-button" title="Close detail" onClick={() => setSelected(null)}><X size={17} /></button></div><p className="detail-description">{selected.description}</p><div className="detail-fields"><label>Status<select value={selected.status} disabled={busy} onChange={(event) => void mutate("status", event.target.value as Status)}>{statuses.map((status) => <option key={status} value={status}>{label(status)}</option>)}</select></label><label>Priority<select value={selected.priority} disabled={busy} onChange={(event) => void mutate("priority", event.target.value as Priority)}>{priorities.map((priority) => <option key={priority} value={priority}>{label(priority)}</option>)}</select></label><label>Category<select value={selected.category} disabled={busy} onChange={(event) => void mutate("category", event.target.value as Category)}>{categories.map((category) => <option key={category} value={category}>{label(category)}</option>)}</select></label><label>Owner<input type="number" min="1" placeholder="User ID" value={selected.assigned_to_id ?? ""} disabled={busy} onChange={(event) => event.target.value && void mutate("owner", Number(event.target.value))} /></label></div><div className="history-heading"><div><p className="eyebrow">Traceability</p><h3>Change history</h3></div><span className="history-count">{history.length} events</span></div><div className="timeline">{history.length === 0 ? <p className="muted">No changes recorded yet.</p> : history.map((event) => <div className="timeline-item" key={event.id}><span className="timeline-dot" /><div><strong>{label(event.event_type)}</strong><p><span className="old-value">{event.old_value || "None"}</span><span className="timeline-arrow">→</span><span className="new-value">{event.new_value || "None"}</span></p><small><Clock3 size={12} /> {new Date(event.changed_at).toLocaleString()}</small></div></div>)}</div></> : <div className="detail-empty"><div className="detail-empty-icon"><ClipboardList size={25} /></div><h2>Pick a request</h2><p>Select an item from the queue to inspect its status, ownership, and full change history.</p></div>}</aside>
      </section>
    </main>
    {showCreate && <CreateDialog onClose={() => setShowCreate(false)} onCreated={(request) => { setRequests((current) => [request, ...current]); setShowCreate(false); void openRequest(request); }} />}
  </div>;
}

function CreateDialog({ onClose, onCreated }: { onClose: () => void; onCreated: (request: WorkRequest) => void }) {
  const [title, setTitle] = useState(""); const [description, setDescription] = useState(""); const [category, setCategory] = useState<Category>("feature"); const [priority, setPriority] = useState<Priority>("medium"); const [error, setError] = useState(""); const [saving, setSaving] = useState(false);
  async function submit(event: React.FormEvent) { event.preventDefault(); setSaving(true); setError(""); try { onCreated(await createRequest({ title, description, category, priority })); } catch (err) { setError(err instanceof Error ? err.message : "Unable to create request."); setSaving(false); } }
  return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><form className="modal" onSubmit={(event) => void submit(event)}><div className="modal-heading"><div><p className="eyebrow">New intake</p><h2>Create a request</h2></div><button type="button" className="icon-button" title="Close dialog" onClick={onClose}><X size={17} /></button></div><label>Title<input required value={title} onChange={(event) => setTitle(event.target.value)} placeholder="What needs engineering attention?" /></label><label>Description<textarea required value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Give the team enough context to act." rows={4} /></label><div className="form-split"><label>Category<select value={category} onChange={(event) => setCategory(event.target.value as Category)}>{categories.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></label><label>Priority<select value={priority} onChange={(event) => setPriority(event.target.value as Priority)}>{priorities.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select></label></div>{error && <div className="error-banner">{error}</div>}<button className="primary-button modal-submit" disabled={saving}>{saving ? "Creating..." : "Create request"}<ArrowUpRight size={17} /></button></form></div>;
}
