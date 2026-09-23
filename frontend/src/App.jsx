import React, { useEffect, useState } from "react";
import { demo } from "./api";
import Studio from "./Studio.jsx";
import Assistant from "./Assistant.jsx";

const FAULTS = [
  { value: "", label: "No fault" },
  { value: "erp-cost-timeout", label: "ERP cost timeout" },
  { value: "promohub-validation-warning", label: "PromoHub validation warning" },
  { value: "funding-register-unavailable", label: "Funding register unavailable" },
];

export default function App() {
  const [state, setState] = useState(null);
  const [view, setView] = useState("studio");
  const [err, setErr] = useState("");

  async function refresh() {
    const s = await demo.state();
    setState(s);
  }

  useEffect(() => {
    refresh().catch((e) => setErr(e.message));
  }, []);

  if (!state) {
    return (
      <div className="main">
        <h1>Loading WTCHK demo…</h1>
        <p className="lede">{err || "Connecting to the mock system layer."}</p>
      </div>
    );
  }

  const people = state.people || [];

  return (
    <div className="app">
      <header className="chrome">
        <div className="brand">
          <strong>Watsons HK · WTCHK</strong>
          <span>Promotion Approval · citizen demo · fictional</span>
        </div>
        <div className="tabs">
          <button className={view === "studio" ? "on" : ""} onClick={() => setView("studio")}>
            Workflow Studio
          </button>
          <button className={view === "assistant" ? "on" : ""} onClick={() => setView("assistant")}>
            Workflow Assistant
          </button>
        </div>
        <div className="controls">
          <label>
            Acting as
            <select
              value={state.identity.employeeId}
              onChange={async (e) => {
                await demo.identity(e.target.value);
                refresh();
              }}
            >
              {people.map((p) => (
                <option key={p.employeeId} value={p.employeeId}>
                  {p.name} · {p.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Demo clock
            <input
              type="date"
              value={state.clock}
              onChange={async (e) => {
                await demo.clock(e.target.value);
                refresh();
              }}
            />
          </label>
          <label>
            Fault
            <select
              value={state.fault || ""}
              onChange={async (e) => {
                await demo.fault(e.target.value);
                refresh();
              }}
            >
              {FAULTS.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </label>
          <button
            className="ghost"
            onClick={async () => {
              await demo.reset(false);
              refresh();
            }}
          >
            Reset
          </button>
          <button
            className="solid"
            onClick={async () => {
              await demo.reset(true);
              refresh();
            }}
          >
            Seed storyline
          </button>
        </div>
      </header>
      <div className="workspace">
        {view === "studio" ? (
          <Studio state={state} onChange={refresh} />
        ) : (
          <Assistant state={state} onChange={refresh} />
        )}
      </div>
    </div>
  );
}
