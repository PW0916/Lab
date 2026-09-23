import React, { useEffect, useRef, useState } from "react";
import { assistant as assistantApi, cases as casesApi } from "./api";

function Simulated() {
  return <span className="badge sim">SIMULATED</span>;
}

function Checks({ evaluation }) {
  if (!evaluation) return null;
  if (evaluation.status === "BLOCKED_REGULATORY") {
    return (
      <div className="card">
        <span className="badge red">BLOCKED</span>
        <h4>Regulatory screen</h4>
        <p>{evaluation.regulatory?.statement}</p>
        <p className="muted">{evaluation.regulatory?.citation}</p>
      </div>
    );
  }
  const econ = evaluation.economics || {};
  return (
    <div>
      <div className="card" style={{ marginBottom: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <h4>Item facts</h4>
          <Simulated />
        </div>
        <p>
          <strong>{evaluation.item?.descriptionEn}</strong>
          <div className="muted">
            {evaluation.item?.itemCode} · {evaluation.item?.ownBrand ? "Own brand" : evaluation.item?.brand} ·{" "}
            {evaluation.item?.strategicFlag} · {evaluation.item?.regulatoryClass}
          </div>
        </p>
      </div>
      {(evaluation.checks || []).map((c) => (
        <div className="check" key={c.id}>
          <div>
            <span className={`badge ${c.status}`}>{c.status.toUpperCase()}</span> {c.title}{" "}
            <span className="muted">{(c.ruleIds || []).join(" ")}</span>
            {c.formula && <div className="formula">{c.formula}</div>}
          </div>
          <strong>
            {typeof c.value === "number" ? c.value : ""}
            {c.unit || ""}
            {c.id === "margin" ? `% / ${c.floor}%` : ""}
          </strong>
        </div>
      ))}
      {econ.investment != null && (
        <div className="card" style={{ marginTop: 10 }}>
          <h4>
            Band {evaluation.band?.final} · HK${Number(econ.investmentRounded || econ.investment).toLocaleString()}
          </h4>
          <p className="formula">
            {econ.formula?.investment} · {econ.policyVersion}
          </p>
          <p className="muted">
            Approver {(evaluation.routing?.approver || {}).name}
            {evaluation.routing?.reviewer ? ` · review ${evaluation.routing.reviewer.name}` : ""}
            {evaluation.expectedDecisionDate ? ` · due ${evaluation.expectedDecisionDate}` : ""}
          </p>
        </div>
      )}
    </div>
  );
}

function DecisionPack({ pack, onDecide, task }) {
  if (!pack) return null;
  return (
    <article className="card">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h4>Decision pack {pack.id}</h4>
        <Simulated />
      </div>
      <p className="muted">Humans decide. This is a recommendation with sources, not an approval.</p>
      {(pack.sections || []).slice(0, 8).map((s) => (
        <div key={s.title} style={{ marginBottom: 8 }}>
          <strong>{s.title}</strong>
          <div className="muted">{typeof s.body === "string" ? s.body : JSON.stringify(s.body)?.slice(0, 220)}</div>
        </div>
      ))}
      {task && (
        <div className="btn-row">
          <button className="solid" onClick={() => onDecide("APPROVE")}>
            Approve
          </button>
          <button className="ghost" onClick={() => onDecide("APPROVE_WITH_CONDITIONS")}>
            Approve with conditions
          </button>
          <button className="ghost" onClick={() => onDecide("RETURN_FOR_REVISION")}>
            Return
          </button>
          <button className="danger" onClick={() => onDecide("REJECT")}>
            Reject
          </button>
        </div>
      )}
    </article>
  );
}

export default function Assistant({ state, onChange }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "I can take a promotion request in English or 中文. Name the item — I will look it up and confirm it back. I will not guess a cost or a margin.",
    },
  ]);
  const [text, setText] = useState("");
  const [inbox, setInbox] = useState([]);
  const [allCases, setAllCases] = useState([]);
  const [selected, setSelected] = useState(null);
  const [tab, setTab] = useState("case");
  const end = useRef(null);

  async function refreshSide() {
    const [box, list] = await Promise.all([casesApi.inbox(state.identity.employeeId), casesApi.list()]);
    setInbox(box.inbox || []);
    setAllCases(list.all || []);
  }

  useEffect(() => {
    refreshSide();
  }, [state.identity.employeeId, state.clock, state.caseCount]);

  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(value) {
    const payload = value ?? text;
    if (!payload.trim()) return;
    setText("");
    setMessages((m) => [...m, { role: "user", text: payload }]);
    const res = await assistantApi.send(payload, state.identity.employeeId);
    const reply = res.reply;
    setMessages((m) => [...m, { role: "assistant", text: reply.text, cards: reply.cards }]);
    if (reply.cards?.case) setSelected(reply.cards.case);
    if (reply.cards?.evaluation && !reply.cards.case) {
      setSelected({ evaluation: reply.cards.evaluation, status: reply.cards.evaluation.status });
    }
    await refreshSide();
    onChange();
  }

  async function decide(task, decision) {
    await casesApi.decide(task.taskId, { decision, decidedBy: state.identity.employeeId });
    await refreshSide();
    const latest = await casesApi.get(task.caseRef);
    setSelected(latest);
    onChange();
    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        text: `${state.identity.name} recorded ${decision} on ${task.caseRef} (${task.kind}).`,
      },
    ]);
  }

  const ev = selected?.evaluation;

  return (
    <div className="assistant">
      <aside className="nav">
        <h3>Inbox · {state.identity.name}</h3>
        {inbox.length === 0 && <p className="muted">No open tasks for this person.</p>}
        {inbox.map((row) => (
          <button
            key={row.task.taskId}
            className={selected?.caseRef === row.task.caseRef ? "on" : ""}
            onClick={() => {
              setSelected(row.case);
              setTab("pack");
            }}
          >
            <div className="muted">{row.task.kind}</div>
            {row.task.caseRef}
            <div className="muted">{row.task.status}</div>
          </button>
        ))}
        <h3 style={{ marginTop: 18 }}>Cases</h3>
        {allCases.map((c) => (
          <button key={c.caseRef} className={selected?.caseRef === c.caseRef ? "on" : ""} onClick={() => setSelected(c)}>
            {c.caseRef}
            <div className="muted">{c.status}</div>
          </button>
        ))}
      </aside>
      <section style={{ display: "grid", gridTemplateRows: "1fr auto", minHeight: 0, background: "#efe8d8" }}>
        <div className="thread">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              {m.text}
            </div>
          ))}
          <div ref={end} />
        </div>
        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Name the item, the price, the cycle…"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <label className="ghost" style={{ padding: "10px 12px", borderRadius: 12 }}>
            Upload letter
            <input
              type="file"
              hidden
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setMessages((m) => [...m, { role: "user", text: `Uploaded ${file.name}` }]);
                const res = await assistantApi.upload(file, state.identity.employeeId);
                const reply = res.reply;
                setMessages((m) => [...m, { role: "assistant", text: reply.text, cards: reply.cards }]);
                if (reply.cards?.case) setSelected(reply.cards.case);
                await refreshSide();
              }}
            />
          </label>
          <button className="solid" type="submit">
            Send
          </button>
        </form>
      </section>
      <aside className="panel">
        <div className="tabs" style={{ marginBottom: 10 }}>
          <button className={tab === "case" ? "on" : ""} onClick={() => setTab("case")} style={{ color: "inherit" }}>
            Case
          </button>
          <button className={tab === "pack" ? "on" : ""} onClick={() => setTab("pack")} style={{ color: "inherit" }}>
            Decision pack
          </button>
        </div>
        {!selected && <p className="muted">Checks, routing and the decision pack will land here.</p>}
        {selected && tab === "case" && (
          <>
            <div className="muted">
              {selected.caseRef || "Draft"} · {selected.status}
            </div>
            <Checks evaluation={ev} />
            {inbox.find((i) => i.task.caseRef === selected.caseRef) && (
              <div className="btn-row">
                <button
                  className="solid"
                  onClick={() =>
                    decide(inbox.find((i) => i.task.caseRef === selected.caseRef).task, "APPROVE")
                  }
                >
                  Approve
                </button>
                <button
                  className="ghost"
                  onClick={() =>
                    decide(
                      inbox.find((i) => i.task.caseRef === selected.caseRef).task,
                      "RETURN_FOR_REVISION"
                    )
                  }
                >
                  Return
                </button>
                <button
                  className="danger"
                  onClick={() =>
                    decide(inbox.find((i) => i.task.caseRef === selected.caseRef).task, "REJECT")
                  }
                >
                  Reject
                </button>
              </div>
            )}
            {selected.handover && (
              <article className="card" style={{ marginTop: 10 }}>
                <h4>Handover to Pricing Ops</h4>
                <Simulated />
                {(selected.handover.timeline || []).map((t) => (
                  <div key={t.code} className="muted">
                    {t.code} {t.date} — {t.action}
                  </div>
                ))}
                {selected.draftId && <p>PromoHub {selected.draftId}</p>}
                {selected.validation && <p>Validation {selected.validation.status}</p>}
              </article>
            )}
          </>
        )}
        {selected && tab === "pack" && (
          <DecisionPack
            pack={selected.decisionPack}
            task={(inbox.find((i) => i.task.caseRef === selected.caseRef) || {}).task}
            onDecide={(d) => {
              const row = inbox.find((i) => i.task.caseRef === selected.caseRef);
              if (row) decide(row.task, d);
            }}
          />
        )}
      </aside>
    </div>
  );
}
