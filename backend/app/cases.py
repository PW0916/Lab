"""Case, task and inbox helpers used by the Workflow Assistant."""

from __future__ import annotations

from typing import Any

from .dates import add_working_days
from .engine import (
    apply_approval_to_case,
    assemble_decision_pack,
    create_promohub_draft,
    evaluate_request,
    handover_note,
    validate_draft,
)
from .store import STORE


def create_case(request: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    case_ref = STORE.next_id("case")
    number = case_ref.split("-")[-1]
    pack_id = f"DP-2026-{number}-v1"
    requester = request.get("requesterId") or STORE.identity_id
    case = {
        "caseRef": case_ref,
        "decisionPackId": pack_id,
        "requesterId": requester,
        "requesterName": (STORE.person(requester) or {}).get("name"),
        "status": evaluation.get("status") or "INTAKE",
        "createdAt": STORE.clock.isoformat(),
        "clockCreated": STORE.clock.isoformat(),
        "request": evaluation.get("request") or request,
        "evaluation": evaluation,
        "openGates": [f"{g}_GATE" if not g.endswith("_GATE") and g != "CUTOFF_EXCEPTION" else (
            "CUTOFF_EXCEPTION" if g == "CUTOFF_EXCEPTION" else f"{g}_GATE" if g in {"COMPLIANCE", "SUPPLY_CHAIN"} else g
        ) for g in evaluation.get("gates") or []],
        "tasks": [],
        "timeline": [{"at": STORE.now_iso(), "event": "CREATED", "detail": evaluation.get("status")}],
        "draftId": None,
        "approvedAt": None,
        "approvedBy": None,
    }
    # normalize gates
    gates = []
    for g in evaluation.get("gates") or []:
        if g == "COMPLIANCE":
            gates.append("COMPLIANCE_GATE")
        elif g == "SUPPLY_CHAIN":
            gates.append("SUPPLY_GATE")
        elif g == "CUTOFF_EXCEPTION":
            gates.append("CUTOFF_EXCEPTION")
        else:
            gates.append(g)
    case["openGates"] = gates
    if case["status"] == "BLOCKED_REGULATORY":
        case["status"] = "BLOCKED_REGULATORY"
    elif case["status"] == "WITHDRAWN":
        pass
    elif case["status"] in {"CHECKS_COMPLETE", "EXCEPTION_REVIEW"}:
        pass
    STORE.cases[case_ref] = case
    case["decisionPack"] = assemble_decision_pack(STORE, case, evaluation)
    return case


def route_case(case: dict[str, Any]) -> dict[str, Any]:
    ev = case["evaluation"]
    routing = ev.get("routing") or {}
    band = (ev.get("band") or {}).get("final")
    tasks = []
    if case["status"] in {"BLOCKED_REGULATORY", "WITHDRAWN", "WAITING_DATA"}:
        return case
    if band in {"B", "C", "D"} and routing.get("reviewer"):
        task = _make_task(
            case,
            "FINANCE_REVIEW",
            routing["reviewer"],
            add_working_days(STORE.clock, 2).isoformat(),
            f"Finance review Band {band} {case['caseRef']}",
        )
        tasks.append(task)
        case["status"] = "AWAITING_FINANCE_REVIEW"
    elif routing.get("approver"):
        due = ev.get("expectedDecisionDate")
        task = _make_task(case, "APPROVAL", routing["approver"], due, f"Approve {case['caseRef']}")
        tasks.append(task)
        case["status"] = "AWAITING_APPROVAL"
    for gate in ev.get("gates") or []:
        owner = next((g for g in routing.get("gateOwners") or [] if g.get("gate") == gate), None)
        if not owner:
            continue
        kind = {
            "COMPLIANCE": "COMPLIANCE_GATE",
            "SUPPLY_CHAIN": "SUPPLY_GATE",
            "CUTOFF_EXCEPTION": "CUTOFF_EXCEPTION",
        }.get(gate, gate)
        due_days = 3 if gate == "COMPLIANCE" else (1 if gate == "SUPPLY_CHAIN" else 2)
        task = _make_task(
            case,
            kind,
            owner,
            add_working_days(STORE.clock, due_days).isoformat(),
            f"{kind} {case['caseRef']}",
        )
        tasks.append(task)
        if case["status"] == "CHECKS_COMPLETE":
            case["status"] = "AWAITING_GATES"
    # FYI notifications
    for informed in routing.get("informed") or []:
        nid = STORE.next_id("notification")
        STORE.notifications.append(
            {
                "notificationId": nid,
                "to": [informed["employeeId"]],
                "kind": "FYI",
                "caseRef": case["caseRef"],
                "message": informed.get("reason") or "FYI",
                "simulated": True,
            }
        )
    case["tasks"] = [t["taskId"] for t in tasks]
    case["timeline"].append({"at": STORE.now_iso(), "event": "ROUTED", "detail": case["status"]})
    return case


def _make_task(case: dict[str, Any], kind: str, person: dict[str, Any], due: str, summary: str) -> dict[str, Any]:
    task_id = STORE.next_id("task")
    task = {
        "taskId": task_id,
        "caseRef": case["caseRef"],
        "kind": kind,
        "assignee": person,
        "status": "OPEN",
        "createdAt": STORE.now_iso(),
        "dueDate": due,
        "decisionPackId": case["decisionPackId"],
        "summary": summary,
        "decision": None,
        "decidedBy": None,
        "decidedAt": None,
        "conditions": [],
        "comment": None,
        "history": [{"at": STORE.now_iso(), "event": "CREATED", "detail": kind}],
    }
    STORE.tasks[task_id] = task
    return task


def decide_task(task_id: str, decision: str, decided_by: str, **kwargs: Any) -> dict[str, Any]:
    task = STORE.tasks[task_id]
    task["status"] = "DECIDED"
    task["decision"] = decision
    task["decidedBy"] = {
        "employeeId": decided_by,
        "name": (STORE.person(decided_by) or {}).get("name"),
        "viaDelegation": kwargs.get("delegationRef"),
    }
    task["decidedAt"] = STORE.now_iso()
    task["conditions"] = kwargs.get("conditions") or []
    task["comment"] = kwargs.get("comment")
    case = STORE.cases.get(task["caseRef"])
    if case:
        apply_approval_to_case(STORE, case, task)
        case["timeline"].append(
            {"at": STORE.now_iso(), "event": "DECISION", "detail": f"{task['kind']} {decision}"}
        )
        # After finance, open approval if not already
        if task["kind"] == "FINANCE_REVIEW" and decision in {"APPROVE", "APPROVE_WITH_CONDITIONS"}:
            ev = case["evaluation"]
            routing = ev.get("routing") or {}
            if routing.get("approver") and not any(
                STORE.tasks[t].get("kind") == "APPROVAL"
                for t in case.get("tasks", [])
                if t in STORE.tasks
            ):
                t2 = _make_task(
                    case,
                    "APPROVAL",
                    routing["approver"],
                    ev.get("expectedDecisionDate"),
                    f"Approve {case['caseRef']}",
                )
                case["tasks"].append(t2["taskId"])
                case["status"] = "AWAITING_APPROVAL"
        if case.get("status") in {"APPROVED", "APPROVED_WITH_CONDITIONS"} and not case.get("draftId"):
            if not case.get("openGates"):
                try:
                    draft = create_promohub_draft(STORE, case, case["evaluation"])
                    validation = validate_draft(STORE, draft["draftId"], STORE.fault)
                    case["validation"] = validation
                    case["handover"] = handover_note(case["evaluation"], STORE.clock)
                    case["status"] = "SETUP_CONFIRMED"
                    case["timeline"].append(
                        {"at": STORE.now_iso(), "event": "DRAFT", "detail": draft["draftId"]}
                    )
                except ValueError:
                    pass
    return task


def inbox_for(employee_id: str) -> list[dict[str, Any]]:
    from .mocks import _refresh_task

    rows = []
    for task in STORE.tasks.values():
        _refresh_task(task, STORE.clock)
        assignee = (task.get("assignee") or {}).get("employeeId")
        if assignee == employee_id and task.get("status") != "DECIDED":
            case = STORE.cases.get(task.get("caseRef"))
            rows.append({"task": task, "case": _public_case(case) if case else None})
    return rows


def _public_case(case: dict[str, Any] | None) -> dict[str, Any] | None:
    if not case:
        return None
    return {
        "caseRef": case["caseRef"],
        "status": case["status"],
        "requesterId": case["requesterId"],
        "requesterName": case.get("requesterName"),
        "createdAt": case["createdAt"],
        "request": case.get("request"),
        "evaluation": case.get("evaluation"),
        "decisionPack": case.get("decisionPack"),
        "decisionPackId": case.get("decisionPackId"),
        "openGates": case.get("openGates"),
        "tasks": [STORE.tasks[t] for t in case.get("tasks", []) if t in STORE.tasks],
        "draftId": case.get("draftId"),
        "validation": case.get("validation"),
        "handover": case.get("handover"),
        "approvedAt": case.get("approvedAt"),
        "approvedBy": case.get("approvedBy"),
        "timeline": case.get("timeline"),
        "liveFrom": (case.get("request") or {}).get("startDate") if case["status"] in {"SETUP_CONFIRMED", "APPROVED"} else None,
    }


def cases_for(employee_id: str) -> list[dict[str, Any]]:
    from .mocks import _refresh_task

    for task in STORE.tasks.values():
        _refresh_task(task, STORE.clock)
    rows = []
    for case in STORE.cases.values():
        involved = case["requesterId"] == employee_id
        for tid in case.get("tasks", []):
            task = STORE.tasks.get(tid)
            if task and (task.get("assignee") or {}).get("employeeId") == employee_id:
                involved = True
        routing = (case.get("evaluation") or {}).get("routing") or {}
        for bucket in ("approver", "reviewer"):
            person = routing.get(bucket)
            if person and person.get("employeeId") == employee_id:
                involved = True
        for person in routing.get("informed") or []:
            if person.get("employeeId") == employee_id:
                involved = True
        if involved:
            rows.append(_public_case(case))
    return rows


def refresh_all_tasks() -> None:
    from .mocks import _refresh_task

    for task in STORE.tasks.values():
        _refresh_task(task, STORE.clock)
    # Scenario L live flags
    for case in STORE.cases.values():
        ev = case.get("evaluation") or {}
        cut = ev.get("cutoffs") or {}
        for route in cut.get("routes") or []:
            days = route.get("daysFromClock")
            # recompute vs current clock
            from .dates import days_between, parse_date

            days = days_between(STORE.clock, parse_date(route["cutoff"]))
            route["daysFromClock"] = days
            route["urgent"] = 0 <= days <= 2
