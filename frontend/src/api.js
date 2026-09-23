export async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
    body: opts.body && typeof opts.body !== "string" ? JSON.stringify(opts.body) : opts.body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data?.error?.message || res.statusText);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export const demo = {
  state: () => api("/api/demo/state"),
  reset: (seed = false) => api("/api/demo/reset", { method: "POST", body: { seed } }),
  clock: (clock) => api("/api/demo/clock", { method: "POST", body: { clock } }),
  fault: (fault) => api("/api/demo/fault", { method: "POST", body: { fault } }),
  identity: (employeeId) => api("/api/demo/identity", { method: "POST", body: { employeeId } }),
};

export const studio = {
  load: () => api("/api/studio"),
  document: (file) => api(`/api/studio/documents/${encodeURIComponent(file)}`),
  finding: (id) => api(`/api/studio/findings/${id}`),
  feedback: (item, send = false) => api("/api/studio/feedback", { method: "POST", body: { item, send } }),
  approve: () => api("/api/studio/approve", { method: "POST", body: {} }),
};

export const assistant = {
  send: (text, actorId) => api("/api/assistant/message", { method: "POST", body: { text, actorId } }),
  upload: async (file, actorId) => {
    const fd = new FormData();
    fd.append("file", file);
    if (actorId) fd.append("actorId", actorId);
    const res = await fetch("/api/assistant/upload", { method: "POST", body: fd });
    return res.json();
  },
};

export const cases = {
  list: () => api("/api/cases"),
  get: (id) => api(`/api/cases/${id}`),
  inbox: (employeeId) => api(`/api/inbox${employeeId ? `?employeeId=${employeeId}` : ""}`),
  decide: (taskId, body) => api(`/api/inbox/${taskId}/decide`, { method: "POST", body }),
};
