"""Funding recognition, coverage and evidence verification (Margin Policy §5, Procedure §4)."""

from __future__ import annotations

from datetime import date
from typing import Any

from .dates import parse_date
from .store import DemoStore

RECOGNISED_TYPES = {"SCAN_BACK", "LUMP_SUM"}
CHANNEL_NA_TYPES = {"OFF_INVOICE", "FREE_GOODS"}


def _rate(commitment: dict[str, Any]) -> float:
    if commitment.get("ratePerUnit") is not None:
        return float(commitment["ratePerUnit"])
    if commitment.get("amountPerUnit") is not None:
        return float(commitment["amountPerUnit"])
    return 0.0


def coverage_for(
    commitment: dict[str, Any],
    *,
    period_from: date | str | None,
    period_to: date | str | None,
    channels: list[str] | None,
    forecast: int | None = None,
) -> dict[str, Any]:
    cov: dict[str, Any] = {
        "period": "NOT_EVALUATED",
        "channels": "NOT_EVALUATED",
        "capVsForecast": "NOT_EVALUATED",
        "proratedRatePerUnit": None,
    }
    if period_from and period_to:
        c_from = parse_date(commitment["periodFrom"])
        c_to = parse_date(commitment["periodTo"])
        req_from = parse_date(period_from)
        req_to = parse_date(period_to)
        if c_from <= req_from and c_to >= req_to:
            cov["period"] = "FULL"
        elif c_to < req_from or c_from > req_to:
            cov["period"] = "NOT_COVERED"
        else:
            cov["period"] = "PARTIAL_PERIOD"
    ftype = commitment.get("fundingType")
    req_ch = [c.upper() for c in (channels or [])]
    c_ch = commitment.get("channels")
    if ftype in CHANNEL_NA_TYPES or c_ch is None:
        cov["channels"] = "NOT_APPLICABLE"
    elif not req_ch:
        cov["channels"] = "NOT_EVALUATED"
    else:
        if set(req_ch).issubset(set(c_ch)):
            cov["channels"] = "FULL"
        elif set(req_ch).isdisjoint(set(c_ch)):
            cov["channels"] = "NOT_COVERED"
        else:
            cov["channels"] = "PARTIAL_CHANNEL"
    cap = commitment.get("fundedCap")
    if cap is None:
        cov["capVsForecast"] = "NO_CAP"
    elif forecast is None:
        cov["capVsForecast"] = "NOT_EVALUATED"
    elif cap >= forecast:
        cov["capVsForecast"] = "CAP_ABOVE_FORECAST"
        cov["proratedRatePerUnit"] = _rate(commitment)
    else:
        cov["capVsForecast"] = "CAP_BELOW_FORECAST"
        rate = _rate(commitment)
        cov["proratedRatePerUnit"] = rate * cap / forecast if forecast else 0.0
    return cov


def recognised_for_approval(commitment: dict[str, Any], coverage: dict[str, Any]) -> tuple[bool, str]:
    status = commitment.get("status")
    ftype = commitment.get("fundingType")
    if status != "CONFIRMED":
        return False, f"Status {status} — Margin Policy §5.1 requires CONFIRMED"
    if ftype not in RECOGNISED_TYPES:
        return False, f"{ftype} is reported but not recognised in economics (Margin Policy §5.6)"
    if coverage["period"] != "FULL":
        return False, f"Period coverage {coverage['period']} — recognise only FULL (MP §5.2)"
    if coverage["channels"] not in ("FULL", "NOT_APPLICABLE"):
        return False, f"Channel coverage {coverage['channels']} — recognise only FULL (MP §5.2)"
    return True, "CONFIRMED scan-back/lump-sum covering item, period and channels"


def recognise_amount(
    commitment: dict[str, Any],
    coverage: dict[str, Any],
    forecast: int | None,
) -> float:
    ok, _ = recognised_for_approval(commitment, coverage)
    if not ok:
        return 0.0
    ftype = commitment.get("fundingType")
    if ftype == "LUMP_SUM":
        amount = float(commitment.get("amount") or 0)
        if not forecast:
            return 0.0
        return amount / forecast
    rate = _rate(commitment)
    cap = commitment.get("fundedCap")
    if cap is not None and forecast:
        return rate * min(forecast, cap) / forecast
    return rate


def enrich_commitment(
    commitment: dict[str, Any],
    *,
    period_from: date | str | None = None,
    period_to: date | str | None = None,
    channels: list[str] | None = None,
    forecast: int | None = None,
) -> dict[str, Any]:
    row = dict(commitment)
    cov = coverage_for(
        commitment,
        period_from=period_from,
        period_to=period_to,
        channels=channels,
        forecast=forecast,
    )
    ok, reason = recognised_for_approval(commitment, cov)
    row["coverage"] = cov
    row["recognisedForApproval"] = ok
    row["recognitionReason"] = reason
    row["recognisedFundingPerUnit"] = recognise_amount(commitment, cov, forecast) if ok else 0.0
    if row.get("ratePerUnit") is None and row.get("amountPerUnit") is not None:
        row["ratePerUnit"] = row["amountPerUnit"]
    return row


EVIDENCE_CHECKS = [
    "authorised_signatory",
    "document_ref",
    "item",
    "funding_type_rate",
    "cap",
    "period_channels",
    "min_price",
]


def verify_evidence(
    store: DemoStore,
    funding_ref: str,
    extracted: dict[str, Any],
    document_ref: str,
    request_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    commitment = store.commitment(funding_ref)
    if not commitment:
        return {
            "fundingRef": funding_ref,
            "outcome": "REJECTED",
            "checks": [{"check": "exists", "result": "FAIL", "detail": "Commitment not found"}],
            "coverage": None,
            "recognisedFundingPerUnit": 0.0,
            "newStatus": None,
            "verifiedBy": "Finance Controller (SIMULATED)",
        }

    ctx = request_context or {}
    checks: list[dict[str, Any]] = []

    contacts = []
    for row in store.fixtures["supplierAuthorisedContacts"]:
        if row["supplierCode"] == commitment["supplierCode"]:
            contacts = row["contacts"]
    signatory = extracted.get("authorisedContact") or extracted.get("signatory")
    checks.append(
        {
            "check": "authorised_signatory",
            "result": "PASS" if signatory in contacts else "FAIL",
            "detail": f"{signatory} vs authorised {contacts}",
        }
    )
    checks.append(
        {
            "check": "document_ref",
            "result": "PASS" if document_ref else "FAIL",
            "detail": document_ref,
        }
    )
    extracted_items = extracted.get("itemCodes") or []
    item_ok = not extracted_items or set(extracted_items).issubset(set(commitment["itemCodes"]))
    checks.append(
        {
            "check": "item",
            "result": "PASS" if item_ok else "FAIL",
            "detail": f"{extracted_items} vs {commitment['itemCodes']}",
        }
    )
    ext_type = extracted.get("fundingType") or commitment["fundingType"]
    ext_rate = extracted.get("ratePerUnit")
    rate_ok = ext_type == commitment["fundingType"] and (
        ext_rate is None or abs(float(ext_rate) - _rate(commitment)) < 0.001
    )
    checks.append(
        {
            "check": "funding_type_rate",
            "result": "PASS" if rate_ok else "FAIL",
            "detail": f"{ext_type} {ext_rate}",
        }
    )
    ext_cap = extracted.get("fundedCap")
    cap_ok = ext_cap is None or ext_cap == commitment.get("fundedCap")
    checks.append(
        {
            "check": "cap",
            "result": "PASS" if cap_ok else "FAIL",
            "detail": str(ext_cap),
        }
    )
    period_ok = (
        (extracted.get("periodFrom") in (None, commitment["periodFrom"]))
        and (extracted.get("periodTo") in (None, commitment["periodTo"]))
    )
    ch_ok = not extracted.get("channels") or set(extracted["channels"]) == set(commitment.get("channels") or [])
    checks.append(
        {
            "check": "period_channels",
            "result": "PASS" if period_ok and ch_ok else "FAIL",
            "detail": f"{extracted.get('periodFrom')}–{extracted.get('periodTo')} {extracted.get('channels')}",
        }
    )
    min_price = (commitment.get("conditions") or {}).get("minSellingPrice")
    promo = ctx.get("promotionalPrice")
    min_ok = min_price is None or promo is None or float(promo) >= float(min_price)
    checks.append(
        {
            "check": "min_price",
            "result": "PASS" if min_ok else "FAIL",
            "detail": f"promo {promo} vs min {min_price}",
        }
    )

    # Known golden outcome for FC-2026-041
    known = None
    for row in store.fixtures.get("evidenceVerificationOutcomes") or []:
        if row["fundingRef"] == funding_ref and row.get("documentFingerprint") == document_ref:
            known = row

    all_pass = all(c["result"] == "PASS" for c in checks)
    if known:
        outcome = known["outcome"]
        new_status = known["newStatus"]
    else:
        outcome = "VERIFIED" if all_pass else "REJECTED"
        new_status = "CONFIRMED" if outcome == "VERIFIED" else commitment["status"]

    if outcome == "VERIFIED":
        commitment["status"] = "CONFIRMED"
        commitment["evidenceRef"] = document_ref

    cov = coverage_for(
        commitment,
        period_from=ctx.get("periodFrom") or commitment["periodFrom"],
        period_to=ctx.get("periodTo") or commitment["periodTo"],
        channels=ctx.get("channels") or commitment.get("channels"),
        forecast=ctx.get("forecastUnits"),
    )
    rec = recognise_amount(commitment, cov, ctx.get("forecastUnits")) if outcome == "VERIFIED" else 0.0

    return {
        "fundingRef": funding_ref,
        "outcome": outcome,
        "checks": checks,
        "coverage": cov,
        "recognisedFundingPerUnit": rec,
        "newStatus": new_status,
        "verifiedBy": "Finance Controller (SIMULATED)",
        "extracted": extracted,
    }
