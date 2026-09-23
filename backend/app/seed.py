"""Optional storyline seed so Scenario L can be shown without replaying A–G live."""

from __future__ import annotations

from datetime import date

from .cases import create_case, decide_task, route_case
from .dates import parse_date
from .engine import evaluate_request
from .funding import verify_evidence
from .store import STORE

LETTER = {
    "supplierName": "Glow Beauty Laboratories (HK) Ltd",
    "authorisedContact": "Cheryl Kwan",
    "itemCodes": ["GLW-SRM-30ML"],
    "fundingType": "SCAN_BACK",
    "ratePerUnit": 12.0,
    "fundedCap": 2000,
    "periodFrom": "2026-10-01",
    "periodTo": "2026-11-30",
    "channels": ["STORE"],
}


def _at(day: str) -> None:
    STORE.clock = parse_date(day)


def seed_storyline() -> None:
    """Replay A–G with the dates from golden scenario L."""
    STORE.skip_fault_latency = True
    _at("2026-09-28")

    # A
    ev_a = evaluate_request(
        STORE,
        {
            "itemCode": "WTC-VITC-1000-20",
            "promotionalPrice": 89,
            "storeScope": "PILOT-20",
            "channels": ["STORE"],
            "leaflet": False,
            "cycle": "C21",
            "forecast": 1000,
            "comparativeClaimIntended": True,
            "requesterId": "E10801",
            "promotionType": "LOCAL",
        },
    )
    case_a = create_case(ev_a["request"], ev_a)
    route_case(case_a)
    for tid in list(case_a["tasks"]):
        task = STORE.tasks[tid]
        if task["kind"] == "APPROVAL":
            decide_task(tid, "APPROVE", "E10234")

    # B
    ev_b_pause = evaluate_request(
        STORE,
        {
            "itemCode": "GLW-SRM-30ML",
            "promotionalPrice": 139,
            "storeScope": "HKI-KLNE",
            "channels": ["STORE"],
            "leaflet": False,
            "cycle": "C22",
            "forecast": 1800,
            "fundingRef": "FC-2026-041",
            "requesterId": "E10815",
        },
    )
    verify_evidence(
        STORE,
        "FC-2026-041",
        LETTER,
        "GBL/TF/2026/0917",
        {
            "periodFrom": "2026-10-22",
            "periodTo": "2026-11-04",
            "channels": ["STORE"],
            "forecastUnits": 1800,
            "promotionalPrice": 139,
        },
    )
    ev_b = evaluate_request(
        STORE,
        {
            "itemCode": "GLW-SRM-30ML",
            "promotionalPrice": 139,
            "storeScope": "HKI-KLNE",
            "channels": ["STORE"],
            "leaflet": False,
            "cycle": "C22",
            "forecast": 1800,
            "fundingRef": "FC-2026-041",
            "requesterId": "E10815",
            "proceedWithZeroFunding": True,
        },
    )
    case_b = create_case(ev_b["request"], ev_b)
    route_case(case_b)

    # C withdraw
    ev_c = evaluate_request(
        STORE,
        {
            "itemCode": "SUNV-SPF50-100",
            "promotionalPrice": 109,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP"],
            "leaflet": True,
            "cycle": "C22",
            "forecast": 3000,
            "fundingRef": "FC-2026-033",
            "requesterId": "E10815",
            "proceedWithZeroFunding": True,
            "withdraw": True,
        },
    )
    ev_c["status"] = "WITHDRAWN"
    create_case(ev_c["request"], ev_c)

    # E
    ev_e = evaluate_request(
        STORE,
        {
            "itemCode": "FRSH-TP-2X150",
            "promotionalPrice": 45,
            "storeScope": "HKI-CORE",
            "channels": ["STORE"],
            "leaflet": False,
            "cycle": "C21",
            "forecast": 1600,
            "comparativeClaimIntended": True,
            "claimFallbackAccepted": True,
            "requesterId": "E10822",
        },
    )
    case_e = create_case(ev_e["request"], ev_e)
    route_case(case_e)
    for tid in list(case_e["tasks"]):
        task = STORE.tasks[tid]
        if task["kind"] == "APPROVAL":
            decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))

    # F
    ev_f = evaluate_request(
        STORE,
        {
            "itemCode": "AQUA-MSK-5P",
            "promotionalPrice": 69,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "leaflet": True,
            "cycle": "C22",
            "forecast": 4000,
            "fundingRef": "FC-2026-058",
            "requesterId": "E10815",
            "requestCutoffException": True,
            "proceedWithZeroFunding": True,
        },
    )
    case_f = create_case(ev_f["request"], ev_f)
    route_case(case_f)

    # G
    ev_g = evaluate_request(
        STORE,
        {
            "itemCode": "OMG-FO-1000-100",
            "promotionalPrice": 199,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "leaflet": True,
            "cycle": "C23",
            "forecast": 4500,
            "fundingRef": "FC-2026-052",
            "eventCode": "SD1111",
            "promotionType": "EVENT",
            "requesterId": "E10801",
        },
    )
    case_g = create_case(ev_g["request"], ev_g)
    route_case(case_g)

    # Advance B/E/F/G along the L timeline by rewriting createdAt on tasks
    # Finance B completed 1 Oct; approval created 1 Oct
    _at("2026-10-01")
    if case_b.get("tasks"):
        for tid in list(case_b["tasks"]):
            task = STORE.tasks[tid]
            if task["kind"] == "FINANCE_REVIEW" and task["status"] != "DECIDED":
                task["createdAt"] = "2026-09-28T09:00:00+08:00"
                decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))
        for tid in list(case_b["tasks"]):
            task = STORE.tasks[tid]
            if task["kind"] == "APPROVAL":
                task["createdAt"] = "2026-10-01T09:00:00+08:00"

    # E compliance close 2 Oct
    _at("2026-10-02")
    for tid in list(case_e.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "COMPLIANCE_GATE":
            decide_task(
                tid,
                "APPROVE_WITH_CONDITIONS",
                (task.get("assignee") or {}).get("employeeId"),
                conditions=["Special Price HK$45"],
            )
    case_e["status"] = "SETUP_CONFIRMED"
    case_e["wordingChanges"] = ["Special Price HK$45"]

    # F cut-off exception 30 Sep, Band B approved 2 Oct
    _at("2026-09-30")
    for tid in list(case_f.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "CUTOFF_EXCEPTION":
            decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))
    _at("2026-10-01")
    for tid in list(case_f.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "FINANCE_REVIEW" and task["status"] != "DECIDED":
            decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))
    _at("2026-10-02")
    for tid in list(case_f.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "APPROVAL" and task["status"] != "DECIDED":
            decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))
    case_f["leafletInProduction"] = True

    # G expedite 9 Oct
    _at("2026-10-09")
    for tid in list(case_g.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "SUPPLY_GATE":
            decide_task(tid, "GATE_CLEARED", (task.get("assignee") or {}).get("employeeId"))
        if task["kind"] == "FINANCE_REVIEW" and task["status"] != "DECIDED":
            decide_task(tid, "APPROVE", (task.get("assignee") or {}).get("employeeId"))
    for tid in list(case_g.get("tasks") or []):
        task = STORE.tasks[tid]
        if task["kind"] == "APPROVAL":
            task["createdAt"] = "2026-10-01T09:00:00+08:00"

    _at("2026-09-28")
    STORE.skip_fault_latency = False
