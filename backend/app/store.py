"""Fixture-backed in-memory store for the nine simulated systems and demo session."""

from __future__ import annotations

import copy
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .dates import DEFAULT_CLOCK, parse_date

HKT = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class DemoStore:
    def __init__(self) -> None:
        self.fixtures = _load_json(DATA / "mock-apis" / "fixtures.json")
        self.reset()

    def reset(self) -> None:
        self.clock: date = parse_date(self.fixtures["meta"]["demoClock"], DEFAULT_CLOCK)
        self.fault: str | None = None
        self.identity_id: str = "E10801"  # Jason Lo
        self.language: str = "en"
        self.skip_fault_latency: bool = False
        self.cases: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Any]] = {}
        self.drafts: dict[str, dict[str, Any]] = {}
        self.reviews: dict[str, dict[str, Any]] = {}
        self.notifications: list[dict[str, Any]] = []
        self.conversations: dict[str, dict[str, Any]] = {}
        self.funding = copy.deepcopy(self.fixtures["fundingCommitments"])
        self.counters = {
            "case": 1042,
            "task": 3301,
            "review": 187,
            "supply": 52,
            "notification": 7001,
        }
        self.studio = {
            "blueprintVersion": "0.1",
            "status": "DRAFT_PROPOSED",
            "approvedBy": None,
            "approvedOn": None,
            "appliedFeedback": [],
            "changeRequests": [],
            "flashCutoffDays": 5,
            "labels": {"REQUESTER": "Requester"},
        }

    # ----- lookups -----
    def items(self) -> list[dict[str, Any]]:
        return self.fixtures["productMaster"]

    def item(self, code: str) -> dict[str, Any] | None:
        code_u = code.upper()
        for row in self.items():
            if row["itemCode"].upper() == code_u:
                return row
        return None

    def people(self) -> list[dict[str, Any]]:
        return self.fixtures["authorityDirectory"]["people"]

    def person(self, employee_id: str) -> dict[str, Any] | None:
        for row in self.people():
            if row["employeeId"] == employee_id:
                return row
        return None

    def person_by_role(self, role: str) -> dict[str, Any] | None:
        for row in self.people():
            if role in row.get("roles", []):
                return row
        return None

    def delegations(self) -> list[dict[str, Any]]:
        return self.fixtures["authorityDirectory"]["delegations"]

    def cycles(self) -> list[dict[str, Any]]:
        return self.fixtures["promoCycles"]

    def cycle(self, code: str) -> dict[str, Any] | None:
        for row in self.cycles():
            if row["cycleCode"].upper() == code.upper():
                return row
        return None

    def scopes(self) -> list[dict[str, Any]]:
        return self.fixtures["storeScopes"]

    def scope(self, code: str) -> dict[str, Any] | None:
        for row in self.scopes():
            if row["scopeCode"].upper() == code.upper():
                return row
        return None

    def price(self, item_code: str, zone: str = "HK-STD") -> dict[str, Any] | None:
        for row in self.fixtures["erpPrices"]:
            if row["itemCode"] == item_code and row.get("priceZone", "HK-STD") == zone:
                return row
        for row in self.fixtures["erpPrices"]:
            if row["itemCode"] == item_code:
                return row
        return None

    def cost(self, item_code: str) -> dict[str, Any] | None:
        for row in self.fixtures["erpCosts"]:
            if row["itemCode"] == item_code:
                return row
        return None

    def performance(self, item_code: str) -> dict[str, Any] | None:
        for row in self.fixtures["insightsPerformance"]:
            if row["itemCode"] == item_code:
                return row
        return None

    def stock(self, item_code: str) -> dict[str, Any] | None:
        for row in self.fixtures["insightsStock"]:
            if row["itemCode"] == item_code:
                return row
        return None

    def restriction(self, regulatory_class: str) -> dict[str, Any] | None:
        for row in self.fixtures["complianceRestrictions"]:
            if row["regulatoryClass"] == regulatory_class:
                return row
        return None

    def promotions(self) -> list[dict[str, Any]]:
        return self.fixtures["promotions"]

    def commitments(self) -> list[dict[str, Any]]:
        return self.funding

    def commitment(self, ref: str) -> dict[str, Any] | None:
        for row in self.funding:
            if row["fundingRef"] == ref:
                return row
        return None

    def next_id(self, kind: str) -> str:
        if kind == "case":
            n = self.counters["case"]
            self.counters["case"] += 1
            return f"PR-2026-{n:04d}"
        if kind == "task":
            n = self.counters["task"]
            self.counters["task"] += 1
            return f"AT-2026-{n:04d}"
        if kind == "review":
            n = self.counters["review"]
            self.counters["review"] += 1
            return f"CR-2026-{n:04d}"
        if kind == "supply":
            n = self.counters["supply"]
            self.counters["supply"] += 1
            return f"SG-2026-{n:04d}"
        if kind == "notification":
            n = self.counters["notification"]
            self.counters["notification"] += 1
            return f"NT-2026-{n:04d}"
        raise ValueError(kind)

    def now_iso(self) -> str:
        return datetime(self.clock.year, self.clock.month, self.clock.day, 9, 0, tzinfo=HKT).isoformat()

    def meta(self, source: str, as_of: str | None = None) -> dict[str, Any]:
        return {
            "simulated": True,
            "source": source,
            "fixtureVersion": self.fixtures["meta"]["fixtureVersion"],
            "asOf": as_of or self.now_iso(),
        }

    def identity(self) -> dict[str, Any]:
        person = self.person(self.identity_id) or self.people()[0]
        return person


STORE = DemoStore()
