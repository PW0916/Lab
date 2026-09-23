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
        "blueprintAllVersions": bp["versions"],
        "feedbackCatalogue": FEEDBACK_CATALOGUE,
        "agents": agents,
        "systems": km.get("systems") or [],
    }
