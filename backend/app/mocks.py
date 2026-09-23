"""OpenAPI mock system layer — 9 systems, 26 endpoints, fixture-only."""

from __future__ import annotations

import time
from datetime import date
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .authority import resolve_authority
from .dates import (
    add_working_days,
    effective_created_working_day,
    parse_date,
    working_days_between,
)
from .economics import price_history_fields
from .engine import validate_draft
from .funding import enrich_commitment, verify_evidence
from .store import STORE, DemoStore

router = APIRouter()

LATENCY = {
    "Product Master": 0.15,
    "ERP": 0.40,
    "Sales & Stock Insights": 0.30,
    "PromoHub": 0.25,
    "Trade Funding Register": 0.25,
    "Authority Directory": 0.15,
    "Compliance Register": 0.15,
    "Store Network": 0.15,
    "Approval & Notification Hub": 0.20,
}


def _sleep(source: str, store: DemoStore) -> None:
    if store.skip_fault_latency:
        return
    time.sleep(LATENCY.get(source, 0.15))


def _clock(x_demo_clock: str | None, store: DemoStore) -> date:
    if x_demo_clock:
        return parse_date(x_demo_clock)
    return store.clock


def _fault(x_demo_fault: str | None, store: DemoStore) -> str | None:
    return x_demo_fault or store.fault


def _err(source: str, code: str, message: str, status: int, retryable: bool = False) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "meta": STORE.meta(source),
            "error": {"code": code, "message": message, "retryable": retryable},
        },
    )


@router.get("/product-master/items/{item_code}")
def get_item(
    item_code: str,
    x_demo_clock: str | None = Header(default=None, alias="X-Demo-Clock"),
    x_demo_fault: str | None = Header(default=None, alias="X-Demo-Fault"),
):
    _sleep("Product Master", STORE)
    item = STORE.item(item_code)
    if not item:
        return _err("Product Master", "NOT_FOUND", f"Item {item_code} not found", 404)
    return {"meta": STORE.meta("Product Master"), "item": item}


@router.get("/product-master/items")
def search_items(query: str | None = None, barcode: str | None = None, department: str | None = None):
    _sleep("Product Master", STORE)
    q = (query or "").lower()
    items = []
    for item in STORE.items():
        if barcode and item.get("barcode") != barcode:
            continue
        if department and (item.get("hierarchy") or {}).get("department") != department:
            continue
        blob = " ".join(
            [
                item["itemCode"],
                item.get("descriptionEn") or "",
                item.get("descriptionZh") or "",
                item.get("brand") or "",
            ]
        ).lower()
        if q and q not in blob:
            continue
        items.append(
            {
                "itemCode": item["itemCode"],
                "descriptionEn": item["descriptionEn"],
                "brand": item["brand"],
                "lifecycleStatus": item["lifecycleStatus"],
                "regulatoryClass": item["regulatoryClass"],
            }
        )
    return {"meta": STORE.meta("Product Master"), "items": items}


@router.get("/erp/prices")
def get_price(
    itemCode: str,
    priceZone: str = "HK-STD",
    asOf: str | None = None,
    x_demo_clock: str | None = Header(default=None, alias="X-Demo-Clock"),
):
    _sleep("ERP", STORE)
    clock = _clock(x_demo_clock, STORE)
    as_of = parse_date(asOf, clock)
    row = STORE.price(itemCode, priceZone)
    if not row:
        return _err("ERP", "NOT_FOUND", f"Price for {itemCode} not found", 404)
    fields = price_history_fields(row, as_of)
    return {
        "meta": STORE.meta("ERP", as_of.isoformat()),
        "price": {
            "itemCode": itemCode,
            "priceZone": row.get("priceZone", priceZone),
            "regularPrice": row["regularPrice"],
            "currency": "HKD",
            "effectiveFrom": row["effectiveFrom"],
            "history": row.get("history") or [],
            **fields,
        },
    }


@router.get("/erp/costs")
def get_cost(
    itemCode: str,
    periodFrom: str,
    periodTo: str,
    x_demo_clock: str | None = Header(default=None, alias="X-Demo-Clock"),
    x_demo_fault: str | None = Header(default=None, alias="X-Demo-Fault"),
):
    fault = _fault(x_demo_fault, STORE)
    if fault == "erp-cost-timeout":
        if not STORE.skip_fault_latency:
            time.sleep(8)
        return _err(
            "ERP",
            "UPSTREAM_TIMEOUT",
            "ERP cost service did not respond within 8s",
            504,
            retryable=True,
        )
    _sleep("ERP", STORE)
    from .engine import _effective_cost

    result = _effective_cost(STORE, itemCode, parse_date(periodFrom), parse_date(periodTo))
    if not result.get("available"):
        return _err("ERP", "NOT_FOUND", f"Cost for {itemCode} not found", 404)
    return {
        "meta": STORE.meta("ERP"),
        "cost": {
            "itemCode": itemCode,
            "landedCost": result["landedCost"],
            "currency": "HKD",
            "costEffectiveFrom": (STORE.cost(itemCode) or {}).get("costEffectiveFrom"),
            "offInvoiceAdjustments": result["offInvoiceAdjustments"],
            "effectiveUnitCost": result["effectiveUnitCost"],
            "effectiveUnitCostBasis": result["effectiveUnitCostBasis"],
        },
    }


@router.get("/insights/items/{item_code}/performance")
def get_performance(
    item_code: str,
    scope: str,
    asOf: str | None = None,
    x_demo_clock: str | None = Header(default=None, alias="X-Demo-Clock"),
):
    _sleep("Sales & Stock Insights", STORE)
    perf = STORE.performance(item_code)
    if not perf:
        return _err("Sales & Stock Insights", "NOT_FOUND", f"Performance for {item_code} not found", 404)
    scopes = perf.get("scopes") or {}
    row = scopes.get(scope) or scopes.get("HK-ALL")
    if not row:
        return _err("Sales & Stock Insights", "NOT_FOUND", f"Scope {scope} not found", 404)
    history = []
    for promo in STORE.promotions():
        if item_code in promo.get("itemCodes", []) and promo.get("status") == "ENDED":
            history.append(
                {
                    "promotionId": promo["promotionId"],
                    "from": promo["startDate"],
                    "to": promo["endDate"],
                    "weeks": 2,
                    "uplift": None,
                }
            )
    return {
        "meta": STORE.meta("Sales & Stock Insights", asOf),
        "performance": {
            "itemCode": item_code,
            "scope": scope,
            "baselineWeeklyUnits": row["baselineWeeklyUnits"],
            "baselineBasis": "median of last 8 non-promotional weeks",
            "channelSplit": row.get("channelSplit") or {},
            "promoWeeksLast12ByChannel": perf.get("promoWeeksLast12ByChannel") or {},
            "promoHistory": history,
        },
    }


@router.get("/insights/items/{item_code}/stock")
def get_stock(item_code: str, asOf: str | None = None):
    _sleep("Sales & Stock Insights", STORE)
    row = STORE.stock(item_code)
    if not row:
        return _err("Sales & Stock Insights", "NOT_FOUND", f"Stock for {item_code} not found", 404)
    perf = STORE.performance(item_code) or {}
    hk = ((perf.get("scopes") or {}).get("HK-ALL") or {}).get("baselineWeeklyUnits") or 0
    weeks = round(row["stockOnHand"] / hk, 1) if hk else None
    return {
        "meta": STORE.meta("Sales & Stock Insights", asOf),
        "stock": {
            "itemCode": item_code,
            "stockOnHand": row["stockOnHand"],
            "inbound": row.get("inbound") or [],
            "weeksOfCoverAtBaseline": weeks,
        },
    }


@router.get("/insights/benchmarks")
def get_benchmarks(benchmarkGroup: str | None = None, mechanic: str | None = None):
    _sleep("Sales & Stock Insights", STORE)
    data = STORE.fixtures["benchmarks"]
    uplift = data["uplift"]
    if benchmarkGroup:
        uplift = {benchmarkGroup: uplift.get(benchmarkGroup, {})}
        if mechanic:
            uplift = {benchmarkGroup: {mechanic: (uplift.get(benchmarkGroup) or {}).get(mechanic)}}
    return {
        "meta": STORE.meta("Sales & Stock Insights"),
        "source": data["source"],
        "uplift": uplift,
        "modifiers": data["modifiers"],
    }


@router.get("/stores/scopes/{scope_code}")
def get_scope(scope_code: str, openOn: str | None = None):
    _sleep("Store Network", STORE)
    scope = STORE.scope(scope_code)
    if not scope or scope.get("invalid"):
        return _err("Store Network", "NOT_FOUND", f"Scope {scope_code} not found", 404)
    return {"meta": STORE.meta("Store Network"), "scope": scope}


@router.get("/stores/scopes")
def list_scopes():
    _sleep("Store Network", STORE)
    scopes = [s for s in STORE.scopes() if not s.get("invalid")]
    return {"meta": STORE.meta("Store Network"), "scopes": scopes}


@router.get("/promohub/cycles")
def get_cycles(from_: str | None = Query(default=None, alias="from"), to: str | None = None):
    _sleep("PromoHub", STORE)
    cycles = STORE.cycles()
    return {"meta": STORE.meta("PromoHub"), "cycles": cycles, "blackouts": STORE.fixtures.get("blackouts") or []}


@router.get("/promohub/event-codes")
def get_event_codes():
    _sleep("PromoHub", STORE)
    return {"meta": STORE.meta("PromoHub"), "eventCodes": STORE.fixtures["eventCodes"]}


@router.get("/promohub/promotions")
def search_promotions(
    itemCode: str | None = None,
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = None,
    channel: str | None = None,
    status: str | None = None,
):
    _sleep("PromoHub", STORE)
    rows = []
    for p in STORE.promotions():
        if itemCode and itemCode not in p.get("itemCodes", []):
            continue
        if channel and channel not in (p.get("channels") or []):
            continue
        if status and p.get("status") != status:
            continue
        if from_ and to:
            if p["endDate"] < from_ or p["startDate"] > to:
                continue
        rows.append(p)
    return {"meta": STORE.meta("PromoHub"), "promotions": rows}


@router.post("/promohub/drafts", status_code=201)
def create_draft(body: dict[str, Any]):
    _sleep("PromoHub", STORE)
    case_ref = body.get("caseRef")
    if any(d.get("caseRef") == case_ref for d in STORE.drafts.values()):
        return _err("PromoHub", "DUPLICATE_DRAFT", "Draft already exists for this case reference", 409)
    if not body.get("decisionPackId") or not body.get("priceZone"):
        return _err("PromoHub", "VALIDATION", "Missing decision pack or price zone", 422)
    if body.get("promotionType") == "EVENT" and not body.get("eventCode"):
        return _err("PromoHub", "VALIDATION", "Event promotions require an event code", 422)
    number = (case_ref or "PR-2026-0000").split("-")[-1]
    draft_id = f"PD-2026-{number}"
    draft = {
        "draftId": draft_id,
        "status": "DRAFT",
        "description": f"{body.get('description', 'Promotion')} [SIMULATED]",
        "createdAt": STORE.now_iso(),
        "caseRef": case_ref,
        "payload": body,
        "priceZone": body.get("priceZone"),
    }
    STORE.drafts[draft_id] = draft
    return {"meta": STORE.meta("PromoHub"), "draft": draft}


@router.get("/promohub/drafts/{draft_id}/validation")
def get_draft_validation(
    draft_id: str,
    x_demo_fault: str | None = Header(default=None, alias="X-Demo-Fault"),
):
    _sleep("PromoHub", STORE)
    fault = _fault(x_demo_fault, STORE)
    return {"meta": STORE.meta("PromoHub"), "validation": validate_draft(STORE, draft_id, fault)}


@router.get("/funding/commitments")
def search_funding(
    itemCode: str,
    periodFrom: str | None = None,
    periodTo: str | None = None,
    channel: str | None = None,
    includeExpired: bool = True,
    x_demo_fault: str | None = Header(default=None, alias="X-Demo-Fault"),
):
    fault = _fault(x_demo_fault, STORE)
    if fault == "funding-register-unavailable":
        return _err("Trade Funding Register", "UNAVAILABLE", "Funding register unavailable", 503)
    _sleep("Trade Funding Register", STORE)
    rows = []
    for c in STORE.commitments():
        if itemCode not in c.get("itemCodes", []):
            continue
        if not includeExpired and c.get("status") == "EXPIRED":
            continue
        rows.append(
            enrich_commitment(
                c,
                period_from=periodFrom,
                period_to=periodTo,
                channels=[channel] if channel else None,
            )
        )
    return {"meta": STORE.meta("Trade Funding Register"), "commitments": rows}


@router.get("/funding/commitments/{funding_ref}")
def get_funding(funding_ref: str):
    _sleep("Trade Funding Register", STORE)
    c = STORE.commitment(funding_ref)
    if not c:
        return _err("Trade Funding Register", "NOT_FOUND", f"{funding_ref} not found", 404)
    return {"meta": STORE.meta("Trade Funding Register"), "commitment": enrich_commitment(c)}


@router.post("/funding/commitments/{funding_ref}/evidence-verifications")
def post_evidence(funding_ref: str, body: dict[str, Any]):
    _sleep("Trade Funding Register", STORE)
    result = verify_evidence(
        STORE,
        funding_ref,
        body.get("extracted") or {},
        body.get("documentRef") or "",
        body.get("requestContext"),
    )
    return {"meta": STORE.meta("Trade Funding Register"), "verification": result}


@router.post("/authority/resolve")
def post_resolve(body: dict[str, Any]):
    _sleep("Authority Directory", STORE)
    routing = resolve_authority(
        STORE,
        category_lead_roles=body.get("categoryLeadRoles") or [],
        band=body["band"],
        requester_id=body["requesterId"],
        preparer_ids=body.get("preparerIds") or [],
        expected_decision_date=body["expectedDecisionDate"],
        parallel_gates=body.get("parallelGates") or [],
        flash=bool(body.get("flash")),
    )
    return {"meta": STORE.meta("Authority Directory"), "routing": routing}


@router.get("/authority/delegations")
def get_delegations(role: str | None = None, asOf: str | None = None):
    _sleep("Authority Directory", STORE)
    on = parse_date(asOf, STORE.clock)
    rows = []
    for d in STORE.delegations():
        if role and d["role"] != role:
            continue
        if parse_date(d["from"]) <= on <= parse_date(d["to"]):
            rows.append(d)
    return {"meta": STORE.meta("Authority Directory"), "delegations": rows}


@router.get("/compliance/restrictions/{regulatory_class}")
def get_restriction(regulatory_class: str):
    _sleep("Compliance Register", STORE)
    row = STORE.restriction(regulatory_class)
    if not row:
        return _err("Compliance Register", "NOT_FOUND", f"{regulatory_class} not found", 404)
    return {"meta": STORE.meta("Compliance Register"), "restriction": row}


@router.post("/compliance/reviews", status_code=201)
def create_review(body: dict[str, Any]):
    _sleep("Compliance Register", STORE)
    review_id = STORE.next_id("review")
    due = body.get("dueDate") or add_working_days(STORE.clock, 3).isoformat()
    assignee = resolve_authority(
        STORE,
        category_lead_roles=[],
        band="A",
        requester_id="SYSTEM",
        expected_decision_date=due,
        parallel_gates=["COMPLIANCE"],
    )
    owner = (assignee.get("gateOwners") or [None])[0]
    review = {
        "reviewId": review_id,
        "caseRef": body.get("caseRef"),
        "reason": body.get("reason"),
        "assignedTo": owner,
        "dueDate": due,
        "status": "OPEN",
        "itemCodes": body.get("itemCodes"),
        "wordingChanges": [],
    }
    STORE.reviews[review_id] = review
    return {"meta": STORE.meta("Compliance Register"), "review": review}


@router.get("/compliance/reviews/{review_id}")
def get_review(review_id: str):
    _sleep("Compliance Register", STORE)
    row = STORE.reviews.get(review_id)
    if not row:
        return _err("Compliance Register", "NOT_FOUND", f"{review_id} not found", 404)
    return {"meta": STORE.meta("Compliance Register"), "review": row}


def _refresh_task(task: dict[str, Any], clock: date) -> dict[str, Any]:
    if task.get("status") in {"DECIDED"}:
        return task
    created = parse_date(task.get("createdAt"))
    effective = effective_created_working_day(created)
    wd = working_days_between(effective, clock)
    assignee_id = (task.get("assignee") or {}).get("employeeId")
    person = STORE.person(assignee_id) if assignee_id else None
    unavailable = False
    if person:
        for window in person.get("unavailability") or []:
            if parse_date(window["from"]) <= clock <= parse_date(window["to"]):
                unavailable = True
    if unavailable or wd >= 3:
        # re-resolve via delegations
        role = (task.get("assignee") or {}).get("role")
        if role:
            from .authority import _find_delegation

            dlg = _find_delegation(STORE, role, clock, dtype="ABSENCE")
            if dlg:
                delegate = STORE.person(dlg["delegateId"])
                if delegate and task.get("status") != "REASSIGNED":
                    task["status"] = "REASSIGNED"
                    task["previousAssignee"] = task.get("assignee")
                    task["assignee"] = {
                        "role": role,
                        "employeeId": delegate["employeeId"],
                        "name": delegate["name"],
                        "viaDelegation": dlg["ref"],
                        "reason": dlg["reason"],
                    }
                    task.setdefault("history", []).append(
                        {
                            "at": clock.isoformat(),
                            "event": "REASSIGNED",
                            "detail": f"{dlg['ref']} → {delegate['name']}",
                        }
                    )
    elif wd >= 1 and task.get("status") == "OPEN":
        task["status"] = "REMINDED"
        task.setdefault("history", []).append(
            {"at": clock.isoformat(), "event": "REMINDED", "detail": "Reminder after 1 working day"}
        )
    return task


@router.post("/approvals/tasks", status_code=201)
def create_task(body: dict[str, Any]):
    _sleep("Approval & Notification Hub", STORE)
    task_id = STORE.next_id("task")
    person = STORE.person(body["assigneeId"])
    task = {
        "taskId": task_id,
        "caseRef": body.get("caseRef"),
        "kind": body.get("kind"),
        "assignee": {
            "role": None,
            "employeeId": body["assigneeId"],
            "name": (person or {}).get("name"),
            "viaDelegation": body.get("delegationRef"),
        },
        "status": "OPEN",
        "createdAt": STORE.now_iso(),
        "dueDate": body.get("dueDate"),
        "decisionPackId": body.get("decisionPackId"),
        "summary": body.get("summary"),
        "decision": None,
        "decidedBy": None,
        "decidedAt": None,
        "conditions": [],
        "comment": None,
        "history": [{"at": STORE.now_iso(), "event": "CREATED", "detail": body.get("kind")}],
    }
    STORE.tasks[task_id] = task
    return {"meta": STORE.meta("Approval & Notification Hub"), "task": task}


@router.get("/approvals/tasks/{task_id}")
def get_task(task_id: str, x_demo_clock: str | None = Header(default=None, alias="X-Demo-Clock")):
    _sleep("Approval & Notification Hub", STORE)
    task = STORE.tasks.get(task_id)
    if not task:
        return _err("Approval & Notification Hub", "NOT_FOUND", f"{task_id} not found", 404)
    clock = _clock(x_demo_clock, STORE)
    return {"meta": STORE.meta("Approval & Notification Hub"), "task": _refresh_task(task, clock)}


@router.post("/approvals/tasks/{task_id}/decision")
def record_decision(task_id: str, body: dict[str, Any]):
    _sleep("Approval & Notification Hub", STORE)
    task = STORE.tasks.get(task_id)
    if not task:
        return _err("Approval & Notification Hub", "NOT_FOUND", f"{task_id} not found", 404)
    decider = body.get("decidedBy")
    assignee_id = (task.get("assignee") or {}).get("employeeId")
    if decider != assignee_id and not body.get("delegationRef"):
        return _err("Approval & Notification Hub", "FORBIDDEN", "Decider is not the assignee", 403)
    task["status"] = "DECIDED"
    task["decision"] = body.get("decision")
    task["decidedBy"] = {
        "employeeId": decider,
        "name": (STORE.person(decider) or {}).get("name"),
        "viaDelegation": body.get("delegationRef"),
    }
    task["decidedAt"] = STORE.now_iso()
    task["conditions"] = body.get("conditions") or []
    task["comment"] = body.get("comment")
    task.setdefault("history", []).append(
        {"at": STORE.now_iso(), "event": "DECIDED", "detail": body.get("decision")}
    )
    case = STORE.cases.get(task.get("caseRef"))
    if case:
        from .engine import apply_approval_to_case

        apply_approval_to_case(STORE, case, task)
    return {"meta": STORE.meta("Approval & Notification Hub"), "task": task}


@router.post("/notifications", status_code=202)
def send_notification(body: dict[str, Any]):
    _sleep("Approval & Notification Hub", STORE)
    nid = STORE.next_id("notification")
    row = {**body, "notificationId": nid, "createdAt": STORE.now_iso(), "simulated": True}
    STORE.notifications.append(row)
    return {"meta": STORE.meta("Approval & Notification Hub"), "notificationId": nid}
