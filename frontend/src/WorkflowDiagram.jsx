import React, { useMemo, useState } from "react";

const COL = 236;
const ROW = 118;
const PAD_X = 48;
const PAD_Y = 36;

function metrics(kind) {
  if (kind === "startEvent" || kind === "endEvent") return { w: 44, h: 44 };
  if (kind === "exclusiveGateway" || kind === "parallelGateway") return { w: 56, h: 56 };
  if (kind === "userTask") return { w: 200, h: 70 };
  return { w: 210, h: 74 };
}

function centerOf(node) {
  const { w, h } = metrics(node.kind);
  const x = PAD_X + node.lane * COL;
  const y = PAD_Y + node.rank * ROW;
  return { x: x + w / 2, y: y + h / 2, left: x, top: y, w, h };
}

function edgePath(from, to) {
  const a = centerOf(from);
  const b = centerOf(to);
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (Math.abs(dx) < 8) {
    const y1 = a.y + a.h / 2 - 4;
    const y2 = b.y - b.h / 2 + 4;
    return `M ${a.x} ${y1} L ${b.x} ${y2}`;
  }
  if (Math.abs(dy) < 8) {
    const x1 = a.x + (dx > 0 ? a.w / 2 - 4 : -a.w / 2 + 4);
    const x2 = b.x + (dx > 0 ? -b.w / 2 + 4 : b.w / 2 - 4);
    return `M ${x1} ${a.y} L ${x2} ${b.y}`;
  }
  const x1 = a.x;
  const y1 = a.y + a.h / 2 - 2;
  const x2 = b.x;
  const y2 = b.y - b.h / 2 + 2;
  const midY = (y1 + y2) / 2;
  return `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
}

function NodeShape({ node, selected, onSelect }) {
  const { left, top, w, h } = centerOf(node);
  const cls = `wf-node ${node.kind}${selected ? " selected" : ""}`;
  const pick = () => onSelect(node);
  if (node.kind === "startEvent" || node.kind === "endEvent") {
    return (
      <g className={cls} data-node-id={node.id} onClick={pick} transform={`translate(${left},${top})`}>
        <circle cx={w / 2} cy={h / 2} r={node.kind === "endEvent" ? 18 : 16} />
        {node.kind === "endEvent" && <circle cx={w / 2} cy={h / 2} r={13} className="inner" />}
        <text x={w / 2} y={h + 14} textAnchor="middle">
          {node.label}
        </text>
      </g>
    );
  }
  if (node.kind === "exclusiveGateway" || node.kind === "parallelGateway") {
    return (
      <g className={cls} data-node-id={node.id} onClick={pick} transform={`translate(${left},${top})`}>
        <polygon points={`${w / 2},2 ${w - 2},${h / 2} ${w / 2},${h - 2} 2,${h / 2}`} />
        <text x={w / 2} y={h / 2 + 5} textAnchor="middle" className="gw-mark">
          {node.kind === "parallelGateway" ? "+" : "×"}
        </text>
        <text x={w / 2} y={h + 14} textAnchor="middle">
          {node.label}
        </text>
      </g>
    );
  }
  return (
    <g className={cls} data-node-id={node.id} onClick={pick} transform={`translate(${left},${top})`}>
      <rect x="0" y="0" width={w} height={h} rx="10" />
      {node.kind === "userTask" && <rect x="6" y="6" width={w - 12} height={h - 12} rx="7" className="inner" />}
      <text x={12} y={26} className="title">
        {node.label.length > 28 ? `${node.label.slice(0, 26)}…` : node.label}
      </text>
      <text x={12} y={48} className="sub">
        {node.subtitle}
      </text>
    </g>
  );
}

function Inspector({ node, rules }) {
  if (!node) {
    return (
      <p className="muted">
        Click a node for its rules, systems, pauses and outputs. Sequence flows carry the
        gateway labels (BLOCKED, proceed, approved).
      </p>
    );
  }
  const stage = node.stage;
  return (
    <article className="card">
      <div className="level">
        {node.kind} · {node.id}
      </div>
      <h4>{node.label}</h4>
      {node.subtitle && <p className="muted">{node.subtitle}</p>}
      {node.terminal && <p>Terminates as {node.terminal}</p>}
      {stage && (
        <>
          <p className="muted">Owner {stage.owner}</p>
          {!!stage.systems?.length && <p>Systems: {stage.systems.join(", ")}</p>}
          {!!stage.rules?.length && (
            <p>
              {(stage.rules || []).map((id) => {
                const rule = (rules || []).find((r) => r.id === id);
                return (
                  <span key={id} className="rule-chip" title={rule ? `${rule.title} — ${rule.source}` : id}>
                    {id}
                  </span>
                );
              })}
            </p>
          )}
          {!!stage.pauseOn?.length && <p>Pause: {stage.pauseOn.join("; ")}</p>}
          {!!stage.outputs?.length && <p className="muted">Outputs: {stage.outputs.join("; ")}</p>}
          {stage.humanTouch && <p>Human touch: {stage.humanTouch}</p>}
        </>
      )}
    </article>
  );
}

export default function WorkflowDiagram({ diagram, rules }) {
  const [selectedId, setSelectedId] = useState(null);
  const byId = useMemo(() => Object.fromEntries((diagram?.nodes || []).map((n) => [n.id, n])), [diagram]);
  const selected = byId[selectedId];

  if (!diagram?.nodes?.length) return <p className="muted">No sequence-flow diagram generated.</p>;

  const maxLane = Math.max(...diagram.nodes.map((n) => n.lane || 0), 0);
  const maxRank = Math.max(...diagram.nodes.map((n) => n.rank || 0), 0);
  const width = PAD_X * 2 + (maxLane + 1) * COL;
  const height = PAD_Y * 2 + (maxRank + 1) * ROW + 20;
  const c = diagram.counts || {};

  return (
    <div className="wf">
      <div className="wf-meta">
        <span className="badge gold">{diagram.notation}</span>
        <span className="muted">
          {c.activities || 0} activities · {c.gateways || 0} gateways · {c.userTasks || 0} human
          tasks · {c.sequenceFlows || 0} sequence flows
        </span>
      </div>
      <div className="wf-body">
      <div className="wf-canvas">
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Workflow sequence flow">
          <defs>
            <marker id="wf-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" />
            </marker>
          </defs>
          {(diagram.sequenceFlows || []).map((f) => {
            const from = byId[f.source];
            const to = byId[f.target];
            if (!from || !to) return null;
            const d = edgePath(from, to);
            const a = centerOf(from);
            const b = centerOf(to);
            return (
              <g key={f.id} className={`wf-flow ${f.kind || "sequence"}`}>
                <path d={d} markerEnd="url(#wf-arrow)" />
                {f.label && (
                  <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 8} textAnchor="middle">
                    {f.label}
                  </text>
                )}
              </g>
            );
          })}
          {diagram.nodes.map((n) => (
            <NodeShape key={n.id} node={n} selected={n.id === selectedId} onSelect={(node) => setSelectedId(node.id)} />
          ))}
        </svg>
      </div>
      <div className="wf-inspector">
        <Inspector node={selected} rules={rules} />
      </div>
      </div>
    </div>
  );
}
