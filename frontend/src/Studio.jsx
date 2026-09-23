import React, { useEffect, useState } from "react";
import { studio as studioApi } from "./api";
import WorkflowDiagram from "./WorkflowDiagram.jsx";

const NAV = [
  ["workspace", "Knowledge workspace"],
  ["model", "Knowledge model"],
  ["findings", "Findings"],
  ["blueprint", "Blueprint"],
  ["agents", "Agents & skills"],
  ["review", "Review & change"],
  ["tests", "Test & publish"],
];

function RuleHover({ id, rules }) {
  const rule = (rules || []).find((r) => r.id === id);
  return (
    <span className="cite" title={rule ? `${rule.title} — ${rule.statement} (${rule.source})` : id}>
      {id}
    </span>
  );
}

export default function Studio({ state, onChange }) {
  const [data, setData] = useState(null);
  const [page, setPage] = useState("workspace");
  const [doc, setDoc] = useState(null);
  const [finding, setFinding] = useState(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    setData(await studioApi.load());
  }
  useEffect(() => {
    load();
  }, [state.studio.blueprintVersion, state.studio.appliedFeedback?.length]);

  if (!data) return <div className="main">Loading Studio…</div>;

  const rules = data.rules || [];
  const applied = new Set((data.studio.appliedFeedback || []).map((f) => f.item));

  async function applyItem(item, send = false) {
    setBusy(true);
    try {
      await studioApi.feedback(item, send);
      await load();
      onChange();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="studio">
      <aside className="nav">
        <h3>Workflow Studio</h3>
        {NAV.map(([id, label]) => (
          <button key={id} className={page === id ? "on" : ""} onClick={() => setPage(id)}>
            {label}
          </button>
        ))}
        <p className="muted" style={{ marginTop: 16 }}>
          Blueprint {data.studio.blueprintVersion} · {data.studio.status.replaceAll("_", " ")}
        </p>
      </aside>
      <section className="main">
        {page === "workspace" && (
          <>
            <h1>SharePoint folder, as-is</h1>
            <p className="lede">
              Twelve documents a BU would leave on SharePoint, plus one intake. The platform reads them
              unchanged. Nothing here is a live AS Watson policy.
            </p>
            <div className="grid cards-3">
              {data.documents.map((d) => (
                <article key={d.id} className="card" onClick={async () => setDoc(await studioApi.document(d.file))} style={{ cursor: "pointer" }}>
                  <div className="level">Level {String(d.level)} · {d.id}</div>
                  <h4>{d.doc}</h4>
                  <p className="muted">{d.file}</p>
                </article>
              ))}
            </div>
            {doc && (
              <article className="card" style={{ marginTop: 16 }}>
                <h4>{doc.file}</h4>
                <div className="doc-preview">{doc.text}</div>
              </article>
            )}
          </>
        )}

        {page === "model" && (
          <>
            <h1>Knowledge model</h1>
            <p className="lede">
              {rules.length} rules extracted · {data.ruleCounts.HARD} hard · {data.ruleCounts.JUDGEMENT} judgement ·{" "}
              {data.ruleCounts.ADVISORY} advisory · {data.ruleCounts.DERIVED} derived. Hover a rule ID for the citation.
            </p>
            <div className="grid cards-4" style={{ marginBottom: 16 }}>
              {Object.entries(data.ruleCounts).map(([k, v]) => (
                <article key={k} className="card">
                  <div className="muted">{k}</div>
                  <h1 style={{ fontSize: 32 }}>{v}</h1>
                </article>
              ))}
            </div>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Title</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {rules.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <RuleHover id={r.id} rules={rules} />
                    </td>
                    <td>
                      <span className="badge gold">{r.type}</span>
                    </td>
                    <td>
                      {r.title}
                      <div className="muted">{r.statement}</div>
                    </td>
                    <td className="muted">{r.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {page === "findings" && (
          <>
            <h1>Consistency findings</h1>
            <p className="lede">
              Hierarchy wins: Level 1 policies over SOP, over checklists, over minutes. Three findings need a
              process-owner decision before publish.
            </p>
            <div className="grid cards-2">
              {data.findings.map((f) => (
                <article
                  key={f.id}
                  className={`card finding ${f.severity}`}
                  onClick={() => setFinding(f)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="level">
                    {f.id} · {f.severity} · {f.status}
                  </div>
                  <h4>{f.title}</h4>
                  <p>{f.detail}</p>
                  <p className="muted">Resolution: {f.resolution}</p>
                </article>
              ))}
            </div>
            {finding && (
              <article className="card" style={{ marginTop: 16 }}>
                <h4>
                  {finding.id} — {finding.title}
                </h4>
                <p>{finding.detail}</p>
                {finding.id === "F-02" && (
                  <div className="btn-row">
                    <button className="solid" disabled={busy || applied.has(4)} onClick={() => applyItem(4)}>
                      Apply 3 working days and log the SOP revision
                    </button>
                  </div>
                )}
              </article>
            )}
          </>
        )}

        {page === "blueprint" && (
          <>
            <h1>
              Blueprint {data.blueprint.version}{" "}
              <span className="badge green">{data.blueprint.status}</span>
            </h1>
            <p className="lede">
              {data.blueprint.summary} The composer generated a sequence-flow diagram —
              activities, exclusive and parallel gateways, human tasks and labeled flows.
              Click a node for rules, systems, pauses and outputs.
            </p>
            <WorkflowDiagram diagram={data.diagram} rules={rules} />
          </>
        )}

        {page === "agents" && (
          <>
            <h1>Agents and skills</h1>
            <p className="lede">
              8 Studio agents, 12 runtime agents, 34 skills. 21 reusable across workflows; 13 specific to promotion
              approval. No citizen writes a prompt.
            </p>
            <h4>Studio</h4>
            <div className="grid cards-2">
              {(data.agents.studioAgents || []).map((a) => (
                <article key={a.id} className="card">
                  <div className="level">{a.id}</div>
                  <h4>{a.name}</h4>
                  <p>{a.purpose}</p>
                  <p className="muted">{(a.skills || []).join(" · ")}</p>
                </article>
              ))}
            </div>
            <h4 style={{ marginTop: 20 }}>Runtime</h4>
            <div className="grid cards-2">
              {(data.agents.runtimeAgents || []).map((a) => (
                <article key={a.id} className="card">
                  <div className="level">{a.id}</div>
                  <h4>{a.name}</h4>
                  <p>{a.purpose}</p>
                </article>
              ))}
            </div>
          </>
        )}

        {page === "review" && (
          <>
            <h1>Mei’s review of draft 0.1</h1>
            <p className="lede">
              Plain-language feedback. The platform accepts, accepts as advisory, records a deviation — or refuses
              when a Level 1 policy would be overridden.
            </p>
            {(data.feedbackCatalogue || []).map((f) => (
              <article key={f.item} className="card" style={{ marginBottom: 10 }}>
                <div className="level">
                  Item {f.item} · {f.decision.replaceAll("_", " ")}
                  {applied.has(f.item) ? " · applied" : ""}
                </div>
                <h4>{f.request}</h4>
                <p>{f.effect}</p>
                {f.citation && <p className="muted">{f.citation}</p>}
                <div className="btn-row">
                  {f.decision === "REJECTED_BY_CONSISTENCY_CHECK" ? (
                    <button className="danger" disabled={busy || applied.has(5)} onClick={() => applyItem(5, true)}>
                      Reject and send change request to Andrew Kwok
                    </button>
                  ) : (
                    <button className="solid" disabled={busy || applied.has(f.item)} onClick={() => applyItem(f.item)}>
                      Apply
                    </button>
                  )}
                </div>
              </article>
            ))}
          </>
        )}

        {page === "tests" && (
          <>
            <h1>Test and publish</h1>
            <p className="lede">
              13 golden scenarios (A–M) with expected values computed from fixtures v2.0. Approve a numbered
              blueprint only after the findings you own are resolved.
            </p>
            <div className="card">
              <h4>Blueprint 1.0</h4>
              <p>
                Fourteen stages. Progressive intake, split economics/supply, Pricing Ops feasibility, A-01 informed
                routing, Flash cut-off 3 working days.
              </p>
              <p className="muted">
                Applied feedback: {(data.studio.appliedFeedback || []).map((f) => f.item).join(", ") || "none yet"}
              </p>
              <div className="btn-row">
                <button
                  className="solid"
                  disabled={busy || data.studio.status === "APPROVED_BY_PROCESS_OWNER"}
                  onClick={async () => {
                    setBusy(true);
                    await studioApi.approve();
                    await load();
                    onChange();
                    setBusy(false);
                  }}
                >
                  Approve blueprint 1.0 as process owner
                </button>
              </div>
              {data.studio.approvedBy && (
                <p className="badge green" style={{ marginTop: 12 }}>
                  APPROVED_BY_PROCESS_OWNER · {data.studio.approvedBy} · {data.studio.approvedOn}
                </p>
              )}
            </div>
          </>
        )}
      </section>
      <aside className="panel">
        <span className="badge sim">SIMULATED systems only at runtime</span>
        <h4 style={{ marginTop: 12 }}>Roles</h4>
        {(data.roles || []).map((r) => (
          <div key={r.role} className="muted" style={{ marginBottom: 6 }}>
            <strong>{r.label}</strong>
            <div>{r.source}</div>
          </div>
        ))}
        <h4>Glossary</h4>
        {(data.glossary || []).slice(0, 6).map((g) => (
          <p key={g.term} className="muted">
            <strong>{g.term}.</strong> {g.definition}
          </p>
        ))}
      </aside>
    </div>
  );
}
