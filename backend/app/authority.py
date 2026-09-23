"""DoA v3.2 authority resolution — deterministic, fixture-only."""

from __future__ import annotations

from datetime import date
from typing import Any

from .dates import parse_date
from .store import DemoStore


BAND_ROLES = {
    "A": {"reviewer": None, "approver": "CATEGORY_LEAD", "informed": []},
    "B": {"reviewer": "FINANCE_CONTROLLER", "approver": "HEAD_OF_TRADING", "informed": []},
    "C": {
        "reviewer": "FINANCE_CONTROLLER",
        "approver": "COMMERCIAL_DIRECTOR",
        "informed": ["HEAD_OF_TRADING"],
    },
    "D": {
        "reviewer": "FINANCE_CONTROLLER",
        "approver": "MANAGING_DIRECTOR",
        "informed": ["COMMERCIAL_DIRECTOR"],
    },
}

POLICY_VERSION = "WTCHK-COM-POL-032 v3.2"


def _person_ref(
    store: DemoStore,
    person: dict[str, Any] | None,
    role: str,
    via: str | None = None,
    reason: str | None = None,
) -> dict[str, Any] | None:
    if not person:
        return None
    return {
        "role": role,
        "employeeId": person["employeeId"],
        "name": person["name"],
        "title": person.get("title"),
        "viaDelegation": via,
        "reason": reason,
    }


def _unavailable(person: dict[str, Any], on: date) -> bool:
    for window in person.get("unavailability") or []:
        start = parse_date(window["from"])
        end = parse_date(window["to"])
        if start <= on <= end:
            return True
    return False


def _find_delegation(
    store: DemoStore,
    role: str,
    on: date,
    dtype: str | None = None,
    band: str | None = None,
) -> dict[str, Any] | None:
    matches = []
    for d in store.delegations():
        if d["role"] != role:
            continue
        if parse_date(d["from"]) <= on <= parse_date(d["to"]):
            if dtype and d["type"] != dtype:
                continue
            scope = d.get("bandScope") or []
            if band and scope and band not in scope:
                continue
            matches.append(d)
    # Prefer ABSENCE over STANDING when both match
    matches.sort(key=lambda x: 0 if x["type"] == "ABSENCE" else 1)
    return matches[0] if matches else None


def _holder(store: DemoStore, role: str) -> dict[str, Any] | None:
    return store.person_by_role(role)


def _resolve_role(
    store: DemoStore,
    role: str,
    on: date,
    band: str,
    requester_id: str,
    preparer_ids: list[str],
    flash: bool = False,
) -> dict[str, Any] | None:
    holder = _holder(store, role)
    via = None
    reason = None
    person = holder

    absence = _find_delegation(store, role, on, dtype="ABSENCE", band=band)
    if person and (_unavailable(person, on) or absence):
        dlg = absence or _find_delegation(store, role, on, dtype="ABSENCE", band=band)
        if dlg:
            person = store.person(dlg["delegateId"])
            via = dlg["ref"]
            reason = f"Unavailable {on.isoformat()} — {dlg['reason']}"

    blocked = {requester_id, *preparer_ids}
    if person and person["employeeId"] in blocked:
        dlg = _find_delegation(store, role, on, dtype="STANDING", band=band)
        if dlg:
            person = store.person(dlg["delegateId"])
            via = dlg["ref"]
            reason = (
                f"Segregation of duties — requester {requester_id} "
                f"holds the approving role (DoA §6.1)"
            )
        else:
            # escalate to next band approver
            next_map = {"A": "HEAD_OF_TRADING", "B": "COMMERCIAL_DIRECTOR", "C": "MANAGING_DIRECTOR"}
            next_role = next_map.get(band)
            if next_role:
                person = _holder(store, next_role)
                via = None
                reason = "SoD — no standing delegate; escalated to next band (DoA §6.1)"
                role = next_role

    return _person_ref(store, person, role, via, reason)


def resolve_authority(
    store: DemoStore,
    *,
    category_lead_roles: list[str],
    band: str,
    requester_id: str,
    preparer_ids: list[str] | None = None,
    expected_decision_date: date | str,
    parallel_gates: list[str] | None = None,
    flash: bool = False,
    informed_extras: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    on = parse_date(expected_decision_date)
    preparers = list(preparer_ids or [])
    gates = list(parallel_gates or [])

    spec = BAND_ROLES[band]
    reviewer = None
    approver = None
    additional: list[dict[str, Any]] = []
    informed: list[dict[str, Any]] = []

    if flash and band == "A" and not gates:
        # Flash shortcut: category lead approves, Head of Trading informed same day
        lead_role = category_lead_roles[0] if category_lead_roles else "CATEGORY_LEAD_HEALTH"
        approver = _resolve_role(store, lead_role, on, band, requester_id, preparers, flash)
        informed_role = _resolve_role(store, "HEAD_OF_TRADING", on, band, requester_id, preparers)
        if informed_role:
            informed_role["reason"] = "Flash shortcut — informed same day (DoA §7)"
            informed.append(informed_role)
    elif band == "A":
        for i, lead_role in enumerate(category_lead_roles or ["CATEGORY_LEAD_HEALTH"]):
            resolved = _resolve_role(store, lead_role, on, band, requester_id, preparers)
            if i == 0:
                approver = resolved
            elif resolved:
                additional.append(resolved)
    else:
        if spec["reviewer"]:
            reviewer = _resolve_role(store, spec["reviewer"], on, band, requester_id, preparers)
        approver_role = spec["approver"]
        approver = _resolve_role(store, approver_role, on, band, requester_id, preparers)
        for role in spec["informed"]:
            ref = _resolve_role(store, role, on, band, requester_id, preparers)
            if ref:
                informed.append(ref)

    # Band B+ reviewer ≠ approver
    if (
        reviewer
        and approver
        and reviewer["employeeId"] == approver["employeeId"]
        and band in {"B", "C", "D"}
    ):
        dlg = _find_delegation(store, reviewer["role"], on, dtype="STANDING", band=band)
        if dlg:
            reviewer = _person_ref(
                store,
                store.person(dlg["delegateId"]),
                reviewer["role"],
                dlg["ref"],
                "Reviewer ≠ approver (DoA §6.1)",
            )

    gate_owners: list[dict[str, Any]] = []
    item_roles = category_lead_roles or []
    for gate in gates:
        if gate == "COMPLIANCE":
            go = _resolve_role(store, "COMPLIANCE_MANAGER", on, band, requester_id, preparers)
            if go:
                go["gate"] = "COMPLIANCE"
                gate_owners.append(go)
        elif gate == "SUPPLY_CHAIN":
            supply_role = "SUPPLY_PLANNER_HB"
            if any("BABY" in r or "PERSONAL" in r for r in item_roles):
                # Prefer BPC if any baby/PC item; HB if health/beauty
                if all("BABY" in r or "PERSONAL" in r for r in item_roles):
                    supply_role = "SUPPLY_PLANNER_BPC"
            if any("BEAUTY" in r or "HEALTH" in r for r in item_roles) and not all(
                "BABY" in r or "PERSONAL" in r for r in item_roles
            ):
                supply_role = "SUPPLY_PLANNER_HB"
            go = _resolve_role(store, supply_role, on, band, requester_id, preparers)
            if go:
                go["gate"] = "SUPPLY_CHAIN"
                gate_owners.append(go)
        elif gate == "CUTOFF_EXCEPTION":
            go = _resolve_role(store, "HEAD_OF_TRADING", on, band, requester_id, preparers)
            if go:
                go["gate"] = "CUTOFF_EXCEPTION"
                gate_owners.append(go)

    for extra in informed_extras or []:
        informed.append(extra)

    return {
        "band": band,
        "reviewer": reviewer,
        "approver": approver,
        "additionalApprovers": additional,
        "informed": informed,
        "gateOwners": gate_owners,
        "policyVersion": POLICY_VERSION,
    }
