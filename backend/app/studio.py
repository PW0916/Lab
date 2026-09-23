"""Workflow Studio — cached knowledge model, blueprint, feedback and findings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .store import DATA, STORE

_CACHE: dict[str, Any] = {}


def _load_yaml(name: str) -> Any:
    if name not in _CACHE:
        path = DATA / "generated-blueprint" / name
        with path.open(encoding="utf-8") as fh:
            _CACHE[name] = yaml.safe_load(fh)
    return _CACHE[name]


def knowledge_model() -> dict[str, Any]:
    return _load_yaml("knowledge-model.yaml")


def workflow_blueprint() -> dict[str, Any]:
    return _load_yaml("workflow-blueprint.yaml")


def agents_and_skills() -> dict[str, Any]:
    return _load_yaml("agents-and-skills.yaml")


def documents() -> list[dict[str, Any]]:
    km = knowledge_model()["knowledgeModel"]
    docs = []
    folder = DATA / "mock-documents"
    for src in km["sources"]:
        path = folder / src["file"]
        docs.append(
            {
                **src,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return docs


def document_text(file_name: str) -> str:
    path = DATA / "mock-documents" / file_name
    if not path.exists():
        raise FileNotFoundError(file_name)
    return path.read_text(encoding="utf-8")


FEEDBACK_CATALOGUE = [
    {
        "item": 1,
        "from": "Mei Wong",
        "request": "Do not make people fill in forecast and funding for an item that turns out to be prohibited — screen the item first.",
        "decision": "ACCEPTED",
        "effect": "S01 split into S01 (item and intent) and S04 (offer details); S02–S03 run between them.",
        "impact": {"stages": 2, "skills": 1, "scenarios": ["D", "A"]},
    },
    {
        "item": 2,
        "from": "Mei Wong",
        "request": "Pricing Ops does a feasibility check before approval today — it is in the Checklist §2 but missing from the draft.",
        "decision": "ACCEPTED",
        "effect": "New stage S10 Setup feasibility owned by Setup Readiness; Checklist §2 checks moved before routing.",
        "impact": {"stages": 1, "skills": 1, "scenarios": ["A", "G"]},
    },
    {
        "item": 3,
        "from": "Mei Wong",
        "request": "Rachel asked to see any own-brand promotion under 40% margin — add that.",
        "decision": "ACCEPTED_AS_ADVISORY",
        "effect": "A-01 wired to informed routing (Head of Trading FYI). Not a band change. Pending Rachel Tsang confirmation (F-05).",
        "impact": {"stages": 1, "skills": 1, "scenarios": ["A"]},
    },
    {
        "item": 4,
        "from": "Mei Wong",
        "request": "Flash cut-off is 3 working days now, not 5.",
        "decision": "ACCEPTED_WITH_RECORD",
        "effect": "H-07 applies Calendar v2.0 (3 WD). Deviation from SOP §5.2 recorded; SOP revision action logged for Mei (F-02).",
        "impact": {"stages": 1, "skills": 1, "scenarios": ["K"]},
    },
    {
        "item": 5,
        "from": "Mei Wong",
        "request": "Skip the Finance review for Band B under HK$100k to speed things up.",
        "decision": "REJECTED_BY_CONSISTENCY_CHECK",
        "effect": "Contradicts DoA v3.2 §4 (Finance review for all Band B). Studio will not encode a rule that overrides a Level 1 policy; a change request note to Andrew Kwok was generated instead.",
        "impact": {"stages": 0, "skills": 0, "scenarios": []},
        "citation": "DoA v3.2 §4 — Level 1 policy; SOP and this workflow cannot override.",
        "changeRequestTo": {"name": "Andrew Kwok", "role": "Commercial Director / DoA owner", "employeeId": "E10007"},
    },
    {
        "item": 6,
        "from": "Mei Wong",
        "request": "Call them Promotion Owners, not Requesters.",
        "decision": "ACCEPTED",
        "effect": "UI copy and decision pack labels changed; role identifier REQUESTER unchanged in rules.",
        "impact": {"stages": 0, "skills": 0, "scenarios": []},
    },
    {
        "item": 7,
        "from": "Mei Wong",
        "request": "Finance owns economics, Supply Chain owns stock — separate them.",
        "decision": "ACCEPTED",
        "effect": "S07 split into S08 Promotion economics and S09 Supply readiness with separate owners and outputs.",
        "impact": {"stages": 2, "skills": 2, "scenarios": ["A", "G", "M"]},
    },
]


def apply_feedback(item: int, send_change_request: bool = False) -> dict[str, Any]:
    spec = next((f for f in FEEDBACK_CATALOGUE if f["item"] == item), None)
    if not spec:
        return {"ok": False, "error": f"Unknown feedback item {item}"}
    if any(a["item"] == item for a in STORE.studio["appliedFeedback"]):
        return {"ok": True, "alreadyApplied": True, "item": spec}

    if spec["decision"] == "REJECTED_BY_CONSISTENCY_CHECK":
        cr = {
            "to": spec["changeRequestTo"],
            "from": "Mei Wong",
            "subject": "Change request — Band B Finance review threshold",
            "citation": spec["citation"],
            "reasoning": spec["request"],
            "status": "DRAFTED" if not send_change_request else "SENT_SIMULATED",
        }
        STORE.studio["changeRequests"].append(cr)
        STORE.studio["appliedFeedback"].append({**spec, "applied": True})
        return {"ok": True, "item": spec, "changeRequest": cr, "rejected": True}

    STORE.studio["appliedFeedback"].append({**spec, "applied": True})
    if item == 4:
        STORE.studio["flashCutoffDays"] = 3
    if item == 6:
        STORE.studio["labels"]["REQUESTER"] = "Promotion Owner"

    accepted = [a for a in STORE.studio["appliedFeedback"] if a["decision"] != "REJECTED_BY_CONSISTENCY_CHECK"]
    # After the six accepted items (1-4, 6, 7) the blueprint is ready to approve
    return {"ok": True, "item": spec, "acceptedCount": len(accepted)}


def approve_blueprint(by: str = "Mei Wong") -> dict[str, Any]:
    STORE.studio["blueprintVersion"] = "1.0"
    STORE.studio["status"] = "APPROVED_BY_PROCESS_OWNER"
    STORE.studio["approvedBy"] = f"{by}, Head of Trade Marketing (E10105)"
    STORE.studio["approvedOn"] = "2026-09-26"
    STORE.studio["flashCutoffDays"] = 3
    STORE.studio["labels"]["REQUESTER"] = "Promotion Owner"
    return STORE.studio


def _stage_payload(stage: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": stage.get("id"),
        "name": stage.get("name"),
        "owner": stage.get("owner"),
        "rules": stage.get("rules") or [],
        "systems": stage.get("systems") or [],
        "collects": stage.get("collects") or [],
        "outputs": stage.get("outputs") or [],
        "pauseOn": stage.get("pauseOn") or [],
        "stopOn": stage.get("stopOn"),
        "humanTouch": stage.get("humanTouch"),
        "parallel": stage.get("parallel") or [],
    }


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:40] or "node"


def compose_diagram(version_block: dict[str, Any]) -> dict[str, Any]:
    """Blueprint Composer: sequence-flow graph (nodes + flows) from a version.

    Stages become activity nodes. ``stopOn`` becomes an exclusive gateway,
    ``humanTouch`` uploads become a user-task loop, and ``parallel`` becomes
    a parallel split of human nodes with labeled sequence flows — the
    workflow-map, not a stacked list.
    """
    stages = list(version_block.get("stages") or [])
    nodes: list[dict[str, Any]] = []
    flows: list[dict[str, Any]] = []
    rank = 0

    def add_node(
        nid: str,
        kind: str,
        label: str,
        *,
        subtitle: str = "",
        lane: int = 0,
        at: int | None = None,
        stage: dict[str, Any] | None = None,
        terminal: str | None = None,
    ) -> int:
        nonlocal rank
        use = rank if at is None else at
        node: dict[str, Any] = {
            "id": nid,
            "kind": kind,
            "label": label,
            "subtitle": subtitle,
            "rank": use,
            "lane": lane,
        }
        if stage is not None:
            node["stage"] = _stage_payload(stage)
        if terminal:
            node["terminal"] = terminal
        nodes.append(node)
        if at is None:
            rank += 1
        return use

    def add_flow(src: str, tgt: str, label: str = "", kind: str = "sequence") -> None:
        flows.append(
            {
                "id": f"sf-{src}-{tgt}-{_slug(label) or 'seq'}",
                "source": src,
                "target": tgt,
                "label": label,
                "kind": kind,
            }
        )

    add_node("start", "startEvent", "Start", subtitle="Case opened")
    prev = "start"
    pending_label = ""
    skip_incoming: set[str] = set()

    for idx, stage in enumerate(stages):
        sid = str(stage["id"])
        name = str(stage.get("name") or sid)
        owner = str(stage.get("owner") or "")
        next_id = str(stages[idx + 1]["id"]) if idx + 1 < len(stages) else None

        activity_rank = add_node(sid, "activity", f"{sid}  {name}", subtitle=owner, stage=stage)
        if sid not in skip_incoming:
            add_flow(prev, sid, pending_label)
        pending_label = ""
        prev = sid

        if stage.get("stopOn"):
            gid = f"{sid}__xor"
            gw_rank = add_node(gid, "exclusiveGateway", "Gateway", subtitle=str(stage["stopOn"]))
            add_flow(sid, gid)
            add_node(
                f"{sid}__blocked",
                "endEvent",
                "Closed",
                subtitle=str(stage["stopOn"]),
                lane=1,
                at=gw_rank,
                terminal=str(stage["stopOn"]),
            )
            add_flow(gid, f"{sid}__blocked", "BLOCKED")
            prev = gid
            pending_label = "proceed"

        if "upload" in str(stage.get("humanTouch") or "").lower():
            hid = f"{sid}__human"
            add_node(
                hid,
                "userTask",
                "Promotion Owner uploads letter",
                subtitle="Human touch",
                lane=1,
                at=activity_rank,
            )
            add_flow(sid, hid, "evidence needed", kind="association")
            add_flow(hid, sid, "", kind="association")

        parallel = stage.get("parallel") or []
        if parallel:
            split = f"{sid}__and"
            add_node(split, "parallelGateway", "Split", subtitle="Parallel approvals")
            add_flow(sid, split)

            human_ids: list[str] = []
            approver_id = None
            finance_id = None
            row = rank

            def add_human(hid: str, label: str) -> str:
                lane = len(human_ids) % 3
                at = row + len(human_ids) // 3
                add_node(hid, "userTask", label, subtitle="Human decision", lane=lane, at=at)
                add_flow(split, hid)
                human_ids.append(hid)
                return hid

            for item in parallel:
                text = str(item)
                low = text.lower()
                parts = [p.strip() for p in text.replace("->", "→").split("→") if p.strip()]
                if len(parts) > 1 and any("approver" in p.lower() for p in parts[1:]):
                    finance_id = add_human(f"{sid}__{_slug(parts[0])}", parts[0])
                    approver_id = add_human(f"{sid}__approver", parts[1][:1].upper() + parts[1][1:])
                    continue
                hid = add_human(f"{sid}__{_slug(text)}", parts[0] if parts else text)
                if "finance" in low:
                    finance_id = hid
                if "approver" in low:
                    approver_id = hid
            rank = row + max(1, (len(human_ids) + 2) // 3)

            if approver_id is None:
                approver_id = add_human(f"{sid}__approver", "Approver decision")

            if finance_id and approver_id and finance_id != approver_id:
                add_flow(finance_id, approver_id)

            xor = f"{sid}__decision"
            xor_rank = add_node(xor, "exclusiveGateway", "Decision", subtitle="Approve or return")
            add_flow(approver_id, xor)
            add_node(
                f"{sid}__returned",
                "endEvent",
                "Closed",
                subtitle="RETURNED / REJECTED",
                lane=2,
                at=xor_rank,
                terminal="RETURNED_FOR_REVISION / REJECTED",
            )
            add_flow(xor, f"{sid}__returned", "returned / rejected")

            join = f"{sid}__join"
            add_node(join, "parallelGateway", "Join", subtitle="Gates complete", lane=1, at=xor_rank)
            for hid in human_ids:
                if hid not in {approver_id, finance_id}:
                    add_flow(hid, join)

            if next_id:
                add_flow(xor, next_id, "approved")
                add_flow(join, next_id)
                skip_incoming.add(next_id)
                prev = next_id
            else:
                add_node(f"{sid}__end", "endEvent", "End", subtitle="Approved path")
                add_flow(xor, f"{sid}__end", "approved")
                add_flow(join, f"{sid}__end")
                prev = f"{sid}__end"

    if prev and not any(n["id"] == "end" for n in nodes):
        last = next((n for n in nodes if n["id"] == prev), None)
        if last and last["kind"] == "endEvent":
            pass
        else:
            add_node("end", "endEvent", "End", subtitle="Handover complete")
            add_flow(prev, "end")

    counts: dict[str, int] = {}
    for n in nodes:
        counts[n["kind"]] = counts.get(n["kind"], 0) + 1

    return {
        "workflow": version_block.get("name") or "Promotion Request and Approval",
        "version": version_block.get("version"),
        "status": version_block.get("status"),
        "notation": "BPMN sequence flow",
        "nodes": nodes,
        "sequenceFlows": flows,
        "counts": {
            "nodes": len(nodes),
            "sequenceFlows": len(flows),
            "activities": counts.get("activity", 0),
            "gateways": counts.get("exclusiveGateway", 0) + counts.get("parallelGateway", 0),
            "userTasks": counts.get("userTask", 0),
            "events": counts.get("startEvent", 0) + counts.get("endEvent", 0),
            **counts,
        },
    }


def studio_state() -> dict[str, Any]:
    km = knowledge_model()
    bp = workflow_blueprint()
    agents = agents_and_skills()
    rules = km.get("rules") or []
    by_type: dict[str, int] = {}
    for r in rules:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    version = STORE.studio["blueprintVersion"]
    version_block = next(v for v in bp["versions"] if v["version"] == version)
    findings = km.get("findings") or []
    return {
        "studio": STORE.studio,
        "documents": documents(),
        "hierarchy": km["knowledgeModel"]["documentHierarchy"],
        "roles": km.get("roles") or [],
        "rules": rules,
        "ruleCounts": by_type,
        "findings": findings,
        "glossary": km.get("glossary") or [],
        "blueprint": version_block,
        "diagram": compose_diagram(version_block),
        "blueprintAllVersions": bp["versions"],
        "feedbackCatalogue": FEEDBACK_CATALOGUE,
        "agents": agents,
        "systems": km.get("systems") or [],
    }
