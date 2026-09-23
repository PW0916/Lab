"""Golden scenarios A–M against the deterministic engine and mock derived fields."""

from __future__ import annotations

import pytest

from backend.app.authority import resolve_authority
from backend.app.dates import add_working_days, days_between, parse_date
from backend.app.economics import (
    band_from_investment,
    depth,
    investment,
    margin,
    min_funding,
    money,
    pct,
    stock_cover,
)
from backend.app.engine import evaluate_request
from backend.app.funding import verify_evidence
from backend.app.store import DemoStore, STORE


@pytest.fixture(autouse=True)
def fresh_store():
    STORE.reset()
    STORE.skip_fault_latency = True
    yield
    STORE.reset()


def eval_a(**extra):
    req = {
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
    }
    req.update(extra)
    return evaluate_request(STORE, req)


def test_a_vitamin_c_band_a():
    ev = eval_a()
    assert ev["item"]["strategicFlag"] == "HERO"
    assert ev["item"]["ownBrand"] is True
    assert ev["item"]["regulatoryClass"] == "HEALTH_SUPPLEMENT"
    econ = ev["economics"]
    assert econ["effectiveUnitCost"] == 55.0
    assert econ["marginPct"] == 38.20
    assert econ["floorPct"] == 38.0
    assert econ["floorPass"] is True
    assert econ["depthPct"] == 31.01
    assert econ["durationDays"] == 14
    assert econ["investment"] == 40_000
    assert ev["band"]["final"] == "A"
    assert ev["routing"]["approver"]["name"] == "Vivian Chan"
    assert ev["routing"]["approver"]["employeeId"] == "E10234"
    assert any(a["id"] == "A-01" for a in ev["advisories"])
    assert any(i["name"] == "Rachel Tsang" for i in ev["routing"]["informed"])
    freq = next(c for c in ev["checks"] if c["id"] == "frequency")
    assert freq["value"]["STORE"]["total"] == 4
    ref = next(c for c in ev["checks"] if c["id"] == "referencePrice")
    assert ref["value"]["daysAtCurrentPrice"] == 221
    assert ref["value"]["comparativeClaimPermitted"] is True
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["benchmark"] == 960
    assert plaus["value"]["range"]["low"] == 256
    assert plaus["value"]["range"]["high"] == 1248
    assert plaus["value"]["flagged"] is False
    stock = next(c for c in ev["checks"] if c["id"] == "stock")
    assert stock["value"]["stockOnHand"] == 14200
    assert stock["value"]["need"] == 1100
    assert stock["value"]["ok"] is True
    instore = next(r for r in ev["cutoffs"]["routes"] if r["route"] == "inStore")
    assert instore["cutoff"] == "2026-10-01"
    assert instore["daysFromClock"] == 3
    assert ev["expectedDecisionDate"] == "2026-09-30"


def test_b_glow_serum_funding_then_band_b():
    paused = evaluate_request(
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
    assert paused["pause"] == "FUNDING_EVIDENCE"
    assert paused["funding"]["pending"]["status"] == "AGREED_PENDING_EVIDENCE"
    assert paused["funding"]["withoutFunding"]["marginPct"] == 41.01
    assert paused["funding"]["withoutFunding"]["investment"] == 108_000
    assert paused["funding"]["withoutFunding"]["band"] == "B"

    result = verify_evidence(
        STORE,
        "FC-2026-041",
        {
            "authorisedContact": "Cheryl Kwan",
            "itemCodes": ["GLW-SRM-30ML"],
            "fundingType": "SCAN_BACK",
            "ratePerUnit": 12.0,
            "fundedCap": 2000,
            "periodFrom": "2026-10-01",
            "periodTo": "2026-11-30",
            "channels": ["STORE"],
        },
        "GBL/TF/2026/0917",
        {
            "periodFrom": "2026-10-22",
            "periodTo": "2026-11-04",
            "channels": ["STORE"],
            "forecastUnits": 1800,
            "promotionalPrice": 139,
        },
    )
    assert result["outcome"] == "VERIFIED"
    assert all(c["result"] == "PASS" for c in result["checks"])
    assert STORE.commitment("FC-2026-041")["status"] == "CONFIRMED"

    ev = evaluate_request(
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
    assert ev["economics"]["marginPct"] == 49.64
    assert ev["economics"]["investment"] == 86_400
    assert ev["band"]["final"] == "B"
    assert ev["economics"]["depthPct"] == 30.15
    freq = next(c for c in ev["checks"] if c["id"] == "frequency")
    assert freq["value"]["STORE"]["total"] == 6
    assert freq["status"] == "amber"
    assert ev["routing"]["reviewer"]["name"] == "Priscilla Lam"
    assert ev["routing"]["approver"]["name"] == "Rachel Tsang"
    assert ev["expectedDecisionDate"] == "2026-10-05"
    stock = next(c for c in ev["checks"] if c["id"] == "stock")
    assert stock["value"]["cover"] == 7400
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["benchmark"] == 1824
    assert not any(a["id"] == "A-02" for a in ev["advisories"])


def test_c_sunveil_exception():
    ev = evaluate_request(
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
        },
    )
    econ = ev["economics"]
    assert econ["recognisedFundingPerUnit"] == 0
    assert pct(margin(145, 112, 0)) == 22.76
    assert econ["marginPct"] == -2.75
    margin_c = next(c for c in ev["checks"] if c["id"] == "margin")
    assert margin_c["floorPrice"] == 164.71
    assert margin_c["minFundingPerUnit"] == 37.88
    assert margin_c["regularAlreadyBelowFloor"] is True
    stack = next(c for c in ev["checks"] if c["id"] == "stacking")
    assert any(cfl["promotionId"] == "PM-2026-1180" for cfl in stack["value"])
    freq = next(c for c in ev["checks"] if c["id"] == "frequency")
    assert freq["value"]["STORE"]["total"] == 8
    assert freq["value"]["ESHOP"]["total"] == 8
    assert ev["band"]["valueBand"] == "B"
    assert ev["band"]["final"] == "C"
    assert ev["routing"]["reviewer"]["name"] == "Priscilla Lam"
    assert ev["routing"]["approver"]["name"] == "Andrew Kwok"
    assert ev["economics"]["depthPct"] == 24.83


def test_d_infant_formula_blocked_and_stage3():
    blocked = evaluate_request(
        STORE,
        {
            "itemCode": "PURE-IF-S1-900",
            "mechanic": "MEMBER_PRICE",
            "cycle": "C22",
            "requesterId": "E10822",
        },
    )
    assert blocked["status"] == "BLOCKED_REGULATORY"
    codes = {a["itemCode"] for a in blocked["alternatives"]}
    assert "PURE-GUM-S3-900" in codes
    assert "KIND-DPR-M64" in codes
    kind = next(a for a in blocked["alternatives"] if a["itemCode"] == "KIND-DPR-M64")
    assert kind["regularMarginPct"] == 19.58
    assert kind["floorPriceUnfunded"] == 185.37

    ev = evaluate_request(
        STORE,
        {
            "itemCode": "PURE-GUM-S3-900",
            "promotionalPrice": 298,
            "storeScope": "HK-ALL",
            "channels": ["STORE"],
            "cycle": "C22",
            "forecast": 1200,
            "fundingRef": "FC-2026-047",
            "requesterId": "E10822",
            "proceedWithZeroFunding": True,
        },
    )
    assert ev["economics"]["marginPct"] == 17.11
    assert ev["economics"]["investment"] == 18_000
    assert ev["band"]["final"] == "A"
    assert ev["routing"]["approver"]["name"] == "Ivan Cheng"
    assert "COMPLIANCE" in ev["gates"]
    gate = next(g for g in ev["routing"]["gateOwners"] if g.get("gate") == "COMPLIANCE")
    assert gate["name"] == "Jonathan Lee"
    assert gate["viaDelegation"] == "DLG-2026-019"
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["benchmark"] == 1230


def test_e_freshmint_reference_price():
    ev = evaluate_request(
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
            "requesterId": "E10822",
        },
    )
    ref = next(c for c in ev["checks"] if c["id"] == "referencePrice")
    assert ref["value"]["daysAtCurrentPrice"] == 20
    assert ref["value"]["comparativeClaimPermitted"] is False
    assert ref["value"]["noIncreaseIn14Days"] is True
    assert ev["cost"]["effectiveUnitCost"] == 26.0
    assert ev["economics"]["marginPct"] == 42.22
    assert ev["economics"]["depthPct"] == 24.87
    assert ev["economics"]["investment"] == 23_840
    assert ev["band"]["final"] == "A"
    assert ev["routing"]["approver"]["name"] == "Winnie Tam"
    assert "COMPLIANCE" in ev["gates"]
    assert ref["value"]["nextCycle"]["cycle"] == "C22"
    assert ref["value"]["nextCycle"]["daysAtPrice"] == 34
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["benchmark"] == 1976


def test_f_aquadew_missed_leaflet():
    ev = evaluate_request(
        STORE,
        {
            "itemCode": "AQUA-MSK-5P",
            "promotionalPrice": 69,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "leaflet": True,
            "cycle": "C21",
            "forecast": 4000,
            "fundingRef": "FC-2026-058",
            "requesterId": "E10815",
            "proceedWithZeroFunding": True,
        },
    )
    assert ev["missedLeaflet"] is True
    leaflet = next(r for r in ev["cutoffs"]["routes"] if r["route"] == "leaflet")
    assert leaflet["cutoff"] == "2026-09-17"
    assert leaflet["daysFromClock"] == -11
    assert ev["economics"]["recognisedFundingPerUnit"] == 0
    assert ev["economics"]["marginPct"] == 40.58
    assert ev["economics"]["depthPct"] == 22.47
    # Chosen option 2 — C22 with leaflet
    ev2 = evaluate_request(
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
    assert ev2["economics"]["investment"] == 80_000
    assert ev2["band"]["final"] == "B"
    freq = next(c for c in ev2["checks"] if c["id"] == "frequency")
    assert freq["value"]["APP"]["total"] == 5
    stack = next(c for c in ev2["checks"] if c["id"] == "stacking")
    assert stack["value"] == []
    assert ev2["routing"]["approver"]["name"] == "Rachel Tsang"
    assert "CUTOFF_EXCEPTION" in ev2["gates"]


def test_g_omega3_event_stock_gate():
    ev0 = evaluate_request(
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
            "requesterId": "E10801",
        },
    )
    assert ev0["economics"]["marginPct"] == 37.19
    assert ev0["economics"]["investment"] == 157_500
    assert ev0["band"]["final"] == "B"
    plaus = next(c for c in ev0["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["benchmark"] == 3120
    assert plaus["value"]["flagged"] is True
    assert plaus["value"]["eventSuggestion"]["code"] == "SD1111"
    assert plaus["value"]["eventSuggestion"]["withEvent"]["benchmark"] == 4368

    ev = evaluate_request(
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
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["flagged"] is False
    assert any(a["id"] == "A-03" for a in ev["advisories"])
    stock = next(c for c in ev["checks"] if c["id"] == "stock")
    assert stock["value"]["cover"] == 2900
    assert stock["value"]["need"] == 4950
    assert stock["value"]["ok"] is False
    assert "SUPPLY_CHAIN" in ev["gates"]
    assert ev["routing"]["reviewer"]["name"] == "Priscilla Lam"
    assert ev["routing"]["approver"]["name"] == "Rachel Tsang"
    kelvin = next(g for g in ev["routing"]["gateOwners"] if g.get("gate") == "SUPPLY_CHAIN")
    assert kelvin["name"] == "Kelvin Ho"


def test_h_mix_and_match():
    ev = evaluate_request(
        STORE,
        {
            "itemCodes": [
                "GLW-SRM-30ML",
                "AQUA-MSK-5P",
                "DERM-CLN-150",
                "LUMI-TNR-200",
                "SUNV-SPF50-100",
                "BLSM-LIP-4G",
            ],
            "itemCode": "GLW-SRM-30ML",
            "mechanic": "MULTI_BUY_SAVE",
            "saveAmount": 30,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "leaflet": True,
            "cycle": "C24",
            "forecast": 2500,
            "promotionalPrice": 89,  # placeholder for primary
            "requesterId": "E10815",
            "proceedWithZeroFunding": True,
        },
    )
    mb = ev["multiBuy"]
    assert any(x["itemCode"] == "BLSM-LIP-4G" for x in mb["excluded"])
    by = {r["itemCode"]: r for r in mb["rows"]}
    assert by["GLW-SRM-30ML"]["marginPct"] == 54.00
    assert by["AQUA-MSK-5P"]["marginPct"] == 44.59
    assert by["DERM-CLN-150"]["marginPct"] == 48.94
    assert by["LUMI-TNR-200"]["marginPct"] == 49.92
    assert by["SUNV-SPF50-100"]["marginPct"] == 11.40
    assert by["SUNV-SPF50-100"]["pass"] is False
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["checked"] is False
    assert ev["economics"]["investment"] == 75_000
    assert ev["band"]["final"] in {"B", "C"}  # floor fail on SUNV raises to C


def test_i_sod_and_reband():
    ev = evaluate_request(
        STORE,
        {
            "itemCode": "WTC-MULTI-60",
            "promotionalPrice": 119,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "cycle": "C22",
            "forecast": 800,
            "requesterId": "E10234",
        },
    )
    assert ev["economics"]["marginPct"] == 47.90
    assert ev["economics"]["investment"] == 32_000
    assert ev["band"]["valueBand"] == "A"
    assert ev["routing"]["approver"]["name"] == "Tommy Chu"
    assert ev["routing"]["approver"]["viaDelegation"] == "DLG-2026-011"
    plaus = next(c for c in ev["checks"] if c["id"] == "plausibility")
    assert plaus["value"]["flag"] == "LOW"

    ev2 = evaluate_request(
        STORE,
        {
            "itemCode": "WTC-MULTI-60",
            "promotionalPrice": 119,
            "storeScope": "HK-ALL",
            "channels": ["STORE", "ESHOP", "APP"],
            "cycle": "C22",
            "forecast": 4500,
            "requesterId": "E10234",
        },
    )
    assert ev2["economics"]["investment"] == 180_000
    assert ev2["band"]["final"] == "B"
    assert ev2["routing"]["approver"]["name"] == "Rachel Tsang"
    assert ev2["routing"]["reviewer"]["name"] == "Priscilla Lam"
    plaus2 = next(c for c in ev2["checks"] if c["id"] == "plausibility")
    assert plaus2["value"]["flagged"] is False


def test_k_knowledge():
    from backend.app.assistant import knowledge_answer

    a = knowledge_answer("Can I run a Flash on MediRelief Ibuprofen this weekend?")
    assert "PHARMACY_ONLY_P1" in a
    assert "Flash" in a
    b = knowledge_answer("What's the Flash cut-off?")
    assert "3 working days" in b
    assert "F-02" in b
    c = knowledge_answer("Who approves a HK$120k promotion if Rachel is away?")
    assert "Michelle Fung" in c
    assert "DLG-2026-018" in c


def test_m_erp_timeout_then_retry():
    ev = evaluate_request(
        STORE,
        {
            "itemCode": "DERM-CLN-150",
            "promotionalPrice": 95,
            "storeScope": "HK-ALL",
            "channels": ["STORE"],
            "cycle": "C22",
            "forecast": 2500,
            "requesterId": "E10815",
            "costUnavailable": True,
        },
    )
    assert ev["status"] == "WAITING_DATA"
    ev2 = evaluate_request(
        STORE,
        {
            "itemCode": "DERM-CLN-150",
            "promotionalPrice": 95,
            "storeScope": "HK-ALL",
            "channels": ["STORE"],
            "cycle": "C22",
            "forecast": 2500,
            "requesterId": "E10815",
        },
    )
    assert ev2["economics"]["marginPct"] == 45.26
    assert ev2["economics"]["depthPct"] == 20.17
    assert ev2["economics"]["investment"] == 60_000
    assert ev2["band"]["final"] == "B"
    stack = next(c for c in ev2["checks"] if c["id"] == "stacking")
    assert stack["value"] == []  # STORE-only does not conflict with APP+ESHOP
    stock = next(c for c in ev2["checks"] if c["id"] == "stock")
    assert stock["value"]["cover"] == 7200


def test_mock_price_days_and_authority_sod():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.get(
        "/asw-wtchk/erp/prices",
        params={"itemCode": "FRSH-TP-2X150", "priceZone": "HK-STD", "asOf": "2026-10-08"},
    )
    assert r.status_code == 200
    assert r.json()["meta"]["simulated"] is True
    assert r.json()["price"]["daysAtCurrentPrice"] == 20
    assert r.json()["price"]["lastChangeDirection"] == "INCREASE"

    r = client.post(
        "/asw-wtchk/authority/resolve",
        json={
            "businessUnit": "WTCHK",
            "categoryLeadRoles": ["CATEGORY_LEAD_HEALTH"],
            "band": "A",
            "requesterId": "E10234",
            "expectedDecisionDate": "2026-09-30",
        },
    )
    assert r.json()["routing"]["approver"]["name"] == "Tommy Chu"
    assert r.json()["routing"]["approver"]["viaDelegation"] == "DLG-2026-011"


def test_studio_feedback_reject_doa():
    from backend.app.studio import apply_feedback, approve_blueprint

    rejected = apply_feedback(5, send_change_request=True)
    assert rejected["rejected"] is True
    assert STORE.studio["changeRequests"][0]["to"]["employeeId"] == "E10007"
    apply_feedback(1)
    apply_feedback(2)
    apply_feedback(3)
    apply_feedback(4)
    apply_feedback(6)
    apply_feedback(7)
    approved = approve_blueprint()
    assert approved["status"] == "APPROVED_BY_PROCESS_OWNER"
    assert approved["flashCutoffDays"] == 3
    assert approved["labels"]["REQUESTER"] == "Promotion Owner"
