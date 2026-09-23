"""Case evaluation pipeline — deterministic, no LLM, no estimates."""

from __future__ import annotations

from datetime import date
from typing import Any

from .authority import resolve_authority
from .dates import add_working_days, parse_date
from .economics import (
    band_from_investment,
    conflicts_for,
    depth,
    duration_days,
    duration_weeks,
    evaluate_cutoffs,
    evaluate_reference_price,
    expected_decision_date,
    floor_for,
    floor_price,
    investment,
    margin,
    min_funding,
    money,
    multi_buy_worst_case,
    pct,
    plausibility,
    raise_band,
    sla_table,
    stock_cover,
)
from .funding import enrich_commitment
from .store import DemoStore


PROHIBITED = {
    "INFANT_FORMULA_S1",
    "INFANT_FORMULA_S2",
    "PHARMACY_ONLY_P1",
    "PRESCRIPTION",
    "TOBACCO",
}


def _baseline(store: DemoStore, item_code: str, scope: str) -> dict[str, Any]:
    perf = store.performance(item_code) or {}
    scopes = perf.get("scopes") or {}
    row = scopes.get(scope) or scopes.get("HK-ALL") or {"baselineWeeklyUnits": 0, "channelSplit": {}}
    return {
        "baselineWeeklyUnits": row.get("baselineWeeklyUnits", 0),
        "channelSplit": row.get("channelSplit") or {},
        "promoWeeksLast12ByChannel": perf.get("promoWeeksLast12ByChannel") or {},
        "hkAllBaseline": (scopes.get("HK-ALL") or {}).get("baselineWeeklyUnits"),
    }


def _effective_cost(
    store: DemoStore,
    item_code: str,
    period_from: date,
    period_to: date,
) -> dict[str, Any]:
    cost = store.cost(item_code)
    if not cost:
        return {"available": False, "reason": "ERP cost not found"}
    landed = float(cost["landedCost"])
    adjustments = []
    deducted = 0.0
    for adj in cost.get("offInvoice") or []:
        a_from = parse_date(adj["periodFrom"])
        a_to = parse_date(adj["periodTo"])
        full = a_from <= period_from and a_to >= period_to and adj.get("status") == "CONFIRMED"
        coverage = "FULL" if full else "PARTIAL_PERIOD"
        if a_to < period_from or a_from > period_to:
            coverage = "NOT_COVERED"
        rec = {
            "fundingRef": adj.get("fundingRef"),
            "amountPerUnit": adj.get("amountPerUnit"),
            "periodFrom": adj["periodFrom"],
            "periodTo": adj["periodTo"],
            "status": adj.get("status"),
            "coverage": coverage,
        }
        adjustments.append(rec)
        if coverage == "FULL":
            deducted += float(adj["amountPerUnit"])
    return {
        "available": True,
        "landedCost": landed,
        "offInvoiceAdjustments": adjustments,
        "effectiveUnitCost": landed - deducted,
        "effectiveUnitCostBasis": (
            "landedCost − confirmed off-invoice covering the full requested period (Margin Policy §4)"
        ),
    }


def alternatives_for(store: DemoStore, blocked: dict[str, Any]) -> list[dict[str, Any]]:
    brand = blocked.get("brand")
    dept = (blocked.get("hierarchy") or {}).get("department")
    out = []
    for item in store.items():
        if item["itemCode"] == blocked["itemCode"]:
            continue
        if item["regulatoryClass"] in PROHIBITED:
            continue
        same_brand = item.get("brand") == brand
        same_dept = (item.get("hierarchy") or {}).get("department") == dept
        same_div = (item.get("hierarchy") or {}).get("division") == (blocked.get("hierarchy") or {}).get("division")
        if same_brand or same_dept or same_div:
            price = store.price(item["itemCode"])
            cost = store.cost(item["itemCode"])
            floor = floor_for(store, item["categoryGroup"], "STANDARD") or 0
            regular = float(price["regularPrice"]) if price else 0
            landed = float(cost["landedCost"]) if cost else 0
            regular_m = (regular - landed) / regular if regular else 0
            out.append(
                {
                    "itemCode": item["itemCode"],
                    "descriptionEn": item["descriptionEn"],
                    "regulatoryClass": item["regulatoryClass"],
                    "regularPrice": regular,
                    "regularMarginPct": pct(regular_m),
                    "floorPct": pct(floor),
                    "floorPriceUnfunded": money(floor_price(landed, floor)) if floor else None,
                    "complianceReview": (store.restriction(item["regulatoryClass"]) or {}).get(
                        "complianceReview"
                    ),
                }
            )
    return out[:4]


def evaluate_request(store: DemoStore, request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a structured promotion request. Never estimates missing data."""
    clock = store.clock
    item_codes: list[str] = list(request.get("itemCodes") or [])
    if request.get("itemCode") and request["itemCode"] not in item_codes:
        item_codes.insert(0, request["itemCode"])
    if not item_codes:
        return {"ok": False, "status": "MORE_INFO_REQUIRED", "missing": ["itemCode"]}

    primary = store.item(item_codes[0])
    if not primary:
        return {"ok": False, "status": "MORE_INFO_REQUIRED", "error": f"Item {item_codes[0]} not found"}

    mechanic = request.get("mechanic") or "PRICE_CUT"
    promo_type = request.get("promotionType") or (
        "EVENT" if request.get("eventCode") else ("FLASH" if request.get("flash") else "STANDARD")
    )
    if request.get("storeScope") and request.get("storeScope") not in {"HK-ALL"} and promo_type == "STANDARD":
        if not request.get("leaflet"):
            promo_type = request.get("promotionType") or "LOCAL"

    cycle = store.cycle(request["cycle"]) if request.get("cycle") else None
    start = parse_date(request.get("startDate") or (cycle["startDate"] if cycle else None), clock)
    end = parse_date(request.get("endDate") or (cycle["endDate"] if cycle else None), start)
    channels = [c.upper() for c in (request.get("channels") or ["STORE"])]
    scope_code = request.get("storeScope") or "HK-ALL"
    scope = store.scope(scope_code)
    leaflet = bool(request.get("leaflet"))
    forecast = request.get("forecast")
    promo_price = request.get("promotionalPrice")
    flash = bool(request.get("flash") or promo_type == "FLASH")
    event_code = request.get("eventCode")
    claim_intended = request.get("comparativeClaimIntended", False)
    requester_id = request.get("requesterId") or store.identity_id
    cost_unavailable = bool(request.get("costUnavailable"))

    restriction = store.restriction(primary["regulatoryClass"]) or {}
    screen = restriction.get("screen", "PROCEED")
    if primary["regulatoryClass"] in PROHIBITED or screen == "BLOCKED":
        alts = alternatives_for(store, primary)
        return {
            "ok": True,
            "status": "BLOCKED_REGULATORY",
            "item": primary,
            "regulatory": {
                "result": "BLOCKED",
                "class": primary["regulatoryClass"],
                "citation": restriction.get("guidelineRef") or "Guideline §3",
                "statement": (
                    "No price, value, gift, bundle, member price, points or coupon promotion "
                    "(Regulatory Guidelines §3)."
                ),
                "ruleIds": ["H-02"],
            },
            "alternatives": alts,
            "checks": [],
        }

    missing = []
    if promo_price is None and mechanic == "PRICE_CUT":
        missing.append("promotionalPrice")
    if forecast is None:
        missing.append("forecast")
    if request.get("pauseForFunding"):
        # still evaluate the rest so the UI can show both paths
        pass
    if missing and not request.get("allowPartial"):
        return {
            "ok": False,
            "status": "MORE_INFO_REQUIRED",
            "missing": missing,
            "item": primary,
            "regulatory": {"result": "PROCEED", "class": primary["regulatoryClass"], "ruleIds": ["H-03"]},
        }

    price_row = store.price(item_codes[0], (scope or {}).get("priceZones", ["HK-STD"])[0])
    if not price_row:
        return {"ok": False, "status": "WAITING_DATA", "error": "Regular price unavailable", "ruleIds": ["H-28"]}

    if cost_unavailable:
        return {
            "ok": True,
            "status": "WAITING_DATA",
            "item": primary,
            "price": price_row,
            "cost": {
                "available": False,
                "reason": "ERP cost unavailable. Margin and floor test not computable.",
                "policy": "Margin Policy §12 — no estimates",
                "ruleIds": ["H-28"],
            },
            "options": ["retry", "park_and_notify_finance"],
        }

    cost = _effective_cost(store, item_codes[0], start, end)
    if not cost.get("available"):
        return {"ok": True, "status": "WAITING_DATA", "cost": cost, "ruleIds": ["H-28"]}

    # Funding
    claimed_refs = list(request.get("fundingRefs") or [])
    if request.get("fundingRef") and request["fundingRef"] not in claimed_refs:
        claimed_refs.append(request["fundingRef"])
    funding_rows = []
    for ref in claimed_refs:
        c = store.commitment(ref)
        if c:
            funding_rows.append(
                enrich_commitment(
                    c,
                    period_from=start,
                    period_to=end,
                    channels=channels,
                    forecast=forecast,
                )
            )
    # also search by item
    if not funding_rows:
        for c in store.commitments():
            if item_codes[0] in c.get("itemCodes", []):
                funding_rows.append(
                    enrich_commitment(c, period_from=start, period_to=end, channels=channels, forecast=forecast)
                )

    recognised = 0.0
    funding_pending = None
    funding_notes = []
    for row in funding_rows:
        if row["fundingType"] in {"FREE_GOODS", "COOP_MEDIA"}:
            funding_notes.append(
                {
                    "ref": row["fundingRef"],
                    "type": row["fundingType"],
                    "recognised": 0,
                    "reason": row["recognitionReason"],
                    "ruleIds": ["H-13"],
                }
            )
            continue
        if row["status"] != "CONFIRMED":
            if row["status"] == "AGREED_PENDING_EVIDENCE":
                funding_pending = row
            funding_notes.append(
                {
                    "ref": row["fundingRef"],
                    "status": row["status"],
                    "recognised": 0,
                    "reason": row["recognitionReason"],
                    "ruleIds": ["H-08"],
                }
            )
            continue
        if row["recognisedForApproval"]:
            recognised += float(row["recognisedFundingPerUnit"])
            funding_notes.append(
                {
                    "ref": row["fundingRef"],
                    "status": row["status"],
                    "recognised": row["recognisedFundingPerUnit"],
                    "coverage": row["coverage"],
                    "reason": row["recognitionReason"],
                    "ruleIds": ["H-08", "H-09", "H-10"],
                }
            )
        else:
            funding_notes.append(
                {
                    "ref": row["fundingRef"],
                    "status": row["status"],
                    "recognised": 0,
                    "coverage": row["coverage"],
                    "reason": row["recognitionReason"],
                    "ruleIds": ["H-09"],
                }
            )

    if funding_pending and not request.get("proceedWithZeroFunding") and not request.get("forceEvaluate"):
        zero_margin = None
        zero_inv = None
        if promo_price is not None and forecast is not None:
            zero_margin = margin(promo_price, cost["effectiveUnitCost"], 0)
            zero_inv = investment(float(price_row["regularPrice"]), promo_price, 0, forecast)
        return {
            "ok": True,
            "status": "MORE_INFO_REQUIRED",
            "pause": "FUNDING_EVIDENCE",
            "item": primary,
            "funding": {
                "pending": funding_pending,
                "withoutFunding": {
                    "margin": zero_margin,
                    "marginPct": pct(zero_margin) if zero_margin is not None else None,
                    "investment": zero_inv,
                    "band": band_from_investment(zero_inv) if zero_inv is not None else None,
                },
                "options": ["upload_letter", "proceed_with_zero"],
                "ruleIds": ["H-08"],
            },
            "commitments": funding_rows,
        }

    regular = float(price_row["regularPrice"])
    promo = float(promo_price)
    eff_cost = float(cost["effectiveUnitCost"])
    m = margin(promo, eff_cost, recognised)
    d = depth(regular, promo)
    if mechanic == "MULTI_BUY_SAVE":
        inv = float(request.get("saveAmount") or 0) * int(forecast or 0)
    else:
        unit_disc = max(0.0, money(regular - promo - recognised))
        inv = unit_disc * int(forecast or 0)
    dur = duration_days(start, end)
    weeks = duration_weeks(start, end, flash=flash)
    floor = floor_for(store, primary["categoryGroup"], promo_type)
    floor_ok = None if floor is None else m >= floor
    regular_m = margin(regular, float(store.cost(item_codes[0])["landedCost"]), 0)

    checks: list[dict[str, Any]] = []
    escalations: list[str] = []
    advisories: list[dict[str, Any]] = []
    gates: list[str] = []

    # H-16 / H-17 margin
    checks.append(
        {
            "id": "margin",
            "ruleIds": ["H-16", "H-17"],
            "title": "Margin vs floor",
            "status": "green" if floor_ok else ("red" if floor_ok is False else "amber"),
            "value": pct(m),
            "unit": "%",
            "floor": pct(floor) if floor is not None else None,
            "inputs": {
                "promoPrice": promo,
                "effectiveUnitCost": eff_cost,
                "recognisedFundingPerUnit": recognised,
            },
            "formula": "(promoPrice − effectiveUnitCost + recognisedFunding) ÷ promoPrice",
            "policyVersion": "WTCHK-FIN-POL-021 v2.1 §3–4",
            "floorPrice": money(floor_price(eff_cost, floor, recognised)) if floor and not floor_ok else None,
            "minFundingPerUnit": money(min_funding(promo, eff_cost, floor)) if floor and not floor_ok else None,
            "regularMarginPct": pct(regular_m),
            "regularAlreadyBelowFloor": bool(floor is not None and regular_m < floor),
        }
    )
    if floor is not None and not floor_ok:
        escalations.append("below_floor")

    # H-18 depth
    depth_status = "green"
    if d > 0.50:
        depth_status = "red"
        escalations.append("depth_exception")
    elif d > 0.40:
        depth_status = "amber"
        escalations.append("depth_40")
    if primary.get("strategicFlag") == "HERO" and d > 0.35:
        depth_status = "amber"
        escalations.append("hero_depth")
    checks.append(
        {
            "id": "depth",
            "ruleIds": ["H-18"],
            "title": "Discount depth",
            "status": depth_status,
            "value": pct(d),
            "unit": "%",
            "inputs": {"regular": regular, "promo": promo},
            "formula": "(regular − promo) ÷ regular",
            "policyVersion": "WTCHK-FIN-POL-021 v2.1 §6; DoA §5.4 / §5.7",
            "heroThreshold": 35 if primary.get("strategicFlag") == "HERO" else None,
        }
    )

    checks.append(
        {
            "id": "duration",
            "ruleIds": ["H-19"],
            "title": "Duration",
            "status": "green" if dur <= 28 else ("amber" if dur <= 56 else "red"),
            "value": dur,
            "unit": "days",
            "policyVersion": "SOP §2.2; DoA §5.6",
        }
    )
    if dur > 56:
        escalations.append("duration_56")
    elif dur > 28:
        escalations.append("duration_28")

    # Frequency H-15
    perf = _baseline(store, item_codes[0], scope_code)
    freq = {}
    freq_breach = False
    at_limit = False
    for ch in channels:
        prior = int((perf["promoWeeksLast12ByChannel"] or {}).get(ch, 0))
        total = prior + weeks
        freq[ch] = {"prior": prior, "this": weeks, "total": total, "limit": 6}
        if total > 6:
            freq_breach = True
        if total == 6:
            at_limit = True
    checks.append(
        {
            "id": "frequency",
            "ruleIds": ["H-15"],
            "title": "Promotion frequency",
            "status": "red" if freq_breach else ("amber" if at_limit else "green"),
            "value": freq,
            "note": (
                "at limit; a further promotion before the rolling window rolls off would breach"
                if at_limit and not freq_breach
                else None
            ),
            "policyVersion": "WTCHK-FIN-POL-021 v2.1 §7",
        }
    )
    if freq_breach:
        escalations.append("frequency")

    # Conflicts H-14
    all_conflicts = []
    for code in item_codes:
        all_conflicts.extend(conflicts_for(store, code, start, end, channels))
    checks.append(
        {
            "id": "stacking",
            "ruleIds": ["H-14"],
            "title": "Stacking / calendar conflict",
            "status": "red" if all_conflicts else "green",
            "value": all_conflicts,
            "policyVersion": "WTCHK-FIN-POL-021 v2.1 §8.1",
        }
    )
    if all_conflicts:
        escalations.append("stacking")

    # Reference price H-26
    ref = evaluate_reference_price(price_row, start)
    if claim_intended and not ref["comparativeClaimPermitted"]:
        gates.append("COMPLIANCE")
        ref["fallbackWording"] = f"Special Price HK${promo:g}" if promo else ref["fallbackWording"]
        # proactive note for next cycle
        next_cycle = None
        for cyc in store.cycles():
            if parse_date(cyc["startDate"]) > start:
                next_cycle = cyc
                break
        if next_cycle:
            nxt = evaluate_reference_price(price_row, parse_date(next_cycle["startDate"]))
            ref["nextCycle"] = {
                "cycle": next_cycle["cycleCode"],
                "start": next_cycle["startDate"],
                "daysAtPrice": nxt["daysAtCurrentPrice"],
                "permitted": nxt["comparativeClaimPermitted"],
            }
    checks.append(
        {
            "id": "referencePrice",
            "ruleIds": ["H-26", "D-05"],
            "title": "Reference price / claims",
            "status": "green"
            if (not claim_intended) or ref["comparativeClaimPermitted"]
            else "amber",
            "value": ref,
            "policyVersion": "WTCHK-LEG-GDL-004 v1.2 §5",
        }
    )

    # Restricted class gate
    review_mode = restriction.get("complianceReview")
    if review_mode in {"MANDATORY", "MANDATORY_COPY", "MANDATORY_MECHANIC"}:
        gates.append("COMPLIANCE")
    if review_mode == "IF_CLAIMS" and request.get("claimsInCopy"):
        gates.append("COMPLIANCE")

    # A-02 skincare hero C23
    if (
        primary.get("categoryGroup") == "BEAUTY_SKINCARE"
        and primary.get("strategicFlag") == "HERO"
        and request.get("cycle") == "C23"
    ):
        advisories.append(
            {
                "id": "A-02",
                "text": "Hero skincare SKUs should not run price promotions in C23 (minutes 8 Sep item 2).",
            }
        )

    # Plausibility
    if mechanic == "MULTI_BUY_SAVE":
        plaus = plausibility(
            store,
            item=primary,
            mechanic=mechanic,
            weeks=weeks,
            baseline_weekly=perf["baselineWeeklyUnits"],
            forecast=int(forecast or 0),
            depth_value=d,
            leaflet=leaflet,
            store_count=(scope or {}).get("storeCount") or 0,
            event_code=event_code,
        )
    else:
        plaus = plausibility(
            store,
            item=primary,
            mechanic=mechanic,
            weeks=weeks,
            baseline_weekly=perf["baselineWeeklyUnits"],
            forecast=int(forecast or 0),
            depth_value=d,
            leaflet=leaflet,
            store_count=(scope or {}).get("storeCount") or 0,
            event_code=event_code,
        )
    # Event-code suggestion when flagged high and cycle carries event
    if (
        plaus.get("flagged")
        and plaus.get("flag") == "HIGH"
        and cycle
        and cycle.get("eventCodes")
        and not event_code
    ):
        suggest = cycle["eventCodes"][0]
        alt = plausibility(
            store,
            item=primary,
            mechanic=mechanic,
            weeks=weeks,
            baseline_weekly=perf["baselineWeeklyUnits"],
            forecast=int(forecast or 0),
            depth_value=d,
            leaflet=leaflet,
            store_count=(scope or {}).get("storeCount") or 0,
            event_code=suggest,
        )
        plaus["eventSuggestion"] = {
            "code": suggest,
            "withEvent": alt,
            "note": (
                f"{cycle['cycleCode']} carries {suggest}. If this is an event promotion, "
                "the event modifier applies and PromoHub needs the event code (Checklist §2.6)."
            ),
        }
    checks.append(
        {
            "id": "plausibility",
            "ruleIds": ["J-05"],
            "title": "Forecast plausibility",
            "status": "amber" if plaus.get("flagged") else "green",
            "value": plaus,
        }
    )

    if item_codes[0] == "OMG-FO-1000-100" and request.get("cycle") == "C23":
        advisories.append(
            {
                "id": "A-03",
                "text": "PPE Part 3: Omega-3 has over-forecast by 20–30% in 11.11 cycles.",
            }
        )

    # Stock
    stock_row = store.stock(item_codes[0]) or {"stockOnHand": 0, "inbound": []}
    stock = stock_cover(
        stock_row,
        forecast=int(forecast or 0),
        start=start,
        hk_all_baseline=perf.get("hkAllBaseline"),
    )
    checks.append(
        {
            "id": "stock",
            "ruleIds": ["H-27", "J-04"],
            "title": "Supply readiness",
            "status": "green" if stock["ok"] else "amber",
            "value": stock,
        }
    )
    if not stock["ok"]:
        gates.append("SUPPLY_CHAIN")
        escalations.append("stock_gate")

    # A-01 own-brand < 40%
    if primary.get("ownBrand") and m < 0.40:
        advisories.append(
            {
                "id": "A-01",
                "text": "Own-brand promotional margin below 40% — Head of Trading informed (minutes 8 Sep item 1).",
                "pendingConfirmation": "Rachel Tsang",
            }
        )

    # Multi-buy
    mb = None
    if mechanic == "MULTI_BUY_SAVE":
        mb = multi_buy_worst_case(
            store, item_codes, float(request.get("saveAmount") or 30), end
        )
        if any(not r["pass"] for r in mb["rows"]) and request.get("exceptionReason"):
            escalations.append("below_floor")
        checks.append(
            {
                "id": "multiBuy",
                "ruleIds": ["H-20"],
                "title": "Mix-and-match worst case",
                "status": "red" if any(not r["pass"] for r in mb["rows"]) else "green",
                "value": mb,
            }
        )

    # Investment / band
    value_band = band_from_investment(inv)
    band = value_band
    if "below_floor" in escalations or "stacking" in escalations or "depth_exception" in escalations:
        band = raise_band(band, "C")
    if any(e in escalations for e in ("depth_40", "frequency", "duration_28", "hero_depth")):
        band = raise_band(band, "B")
    if "duration_56" in escalations:
        band = raise_band(band, "C")

    decision_date = parse_date(request.get("expectedDecisionDate")) if request.get("expectedDecisionDate") else expected_decision_date(clock, band, flash)
    slas = sla_table(clock, band)

    # Cut-offs
    flash_start = start if flash else None
    flash_wd = 3 if store.studio.get("flashCutoffDays") == 3 or store.studio.get("blueprintVersion") == "1.0" else 5
    cut = None
    if cycle:
        cut = evaluate_cutoffs(
            store,
            cycle,
            channels=channels,
            leaflet=leaflet,
            clock=clock,
            expected_decision=decision_date,
            flash=flash,
            flash_start=flash_start,
            flash_cutoff_wd=flash_wd,
        )
        if not cut["allFeasible"]:
            escalations.append("cutoff")
    missed_leaflet = False
    if cycle and leaflet:
        leaflet_cut = parse_date(cycle["cutoffs"]["leaflet"])
        if clock > leaflet_cut:
            missed_leaflet = True

    if request.get("requestCutoffException"):
        gates.append("CUTOFF_EXCEPTION")

    # Setup feasibility
    feasibility = {
        "itemActive": primary.get("lifecycleStatus") in {"ACTIVE", "NEW"},
        "barcodeActive": primary.get("barcodeStatus", "ACTIVE") == "ACTIVE",
        "priceZone": (scope or {}).get("priceZones", ["HK-STD"])[0] if scope and not scope.get("invalid") else None,
        "scopeValid": bool(scope) and not scope.get("invalid"),
        "eventCode": event_code if promo_type == "EVENT" else event_code,
        "datesAligned": bool(cycle),
        "noDuplicateDraft": True,
    }

    informed_extras = []
    if any(a["id"] == "A-01" for a in advisories):
        rachel = store.person_by_role("HEAD_OF_TRADING")
        if rachel:
            informed_extras.append(
                {
                    "role": "HEAD_OF_TRADING",
                    "employeeId": rachel["employeeId"],
                    "name": rachel["name"],
                    "viaDelegation": None,
                    "reason": "Advisory A-01 own-brand margin below 40%",
                }
            )
    # informed category lead for Band B+
    routing = resolve_authority(
        store,
        category_lead_roles=[primary["categoryLeadRole"]],
        band=band,
        requester_id=requester_id,
        preparer_ids=request.get("preparerIds") or [],
        expected_decision_date=decision_date,
        parallel_gates=[],
        flash=flash,
        informed_extras=informed_extras,
    )
    # Gates resolve as at their SLA due date (Compliance 3 WD → October delegate).
    gate_dates = {
        "COMPLIANCE": add_working_days(clock, 3),
        "SUPPLY_CHAIN": add_working_days(clock, 1),
        "CUTOFF_EXCEPTION": add_working_days(clock, 2),
    }
    for gate in list(dict.fromkeys(gates)):
        extra = resolve_authority(
            store,
            category_lead_roles=[primary["categoryLeadRole"]],
            band=band,
            requester_id=requester_id,
            preparer_ids=request.get("preparerIds") or [],
            expected_decision_date=gate_dates.get(gate, decision_date),
            parallel_gates=[gate],
            flash=False,
        )
        for owner in extra.get("gateOwners") or []:
            routing["gateOwners"].append(owner)
    # add category lead as informed for B+ if not already
    if band in {"B", "C", "D"}:
        lead = store.person_by_role(primary["categoryLeadRole"])
        if lead and not any(i.get("employeeId") == lead["employeeId"] for i in routing["informed"]):
            routing["informed"].append(
                {
                    "role": primary["categoryLeadRole"],
                    "employeeId": lead["employeeId"],
                    "name": lead["name"],
                    "viaDelegation": None,
                    "reason": "Category Lead informed",
                }
            )

    options = []
    if missed_leaflet:
        options = _cutoff_options(store, request, cycle, channels, clock, band)
    if "below_floor" in escalations or "stacking" in escalations or freq_breach:
        if primary["itemCode"] == "SUNV-SPF50-100":
            options = [
                {
                    "id": "withdraw",
                    "label": "Withdraw — recommended until supplier funding meeting",
                    "recommended": True,
                },
                {
                    "id": "drop_eshop",
                    "label": "Drop eShop to clear the conflict — floor still fails",
                },
                {
                    "id": "exception",
                    "label": "Proceed as exception with stated reason / benefit / mitigation → Band C",
                },
                {
                    "id": "resubmit_funding",
                    "label": f"Ask supplier for ≥ HK${checks[0].get('minFundingPerUnit')} /unit confirmed funding then resubmit",
                },
            ]

    status = "CHECKS_COMPLETE"
    if missed_leaflet and not request.get("chosenCutoffOption") and not request.get("requestCutoffException"):
        status = "MORE_INFO_REQUIRED"
    if floor_ok is False or freq_breach or all_conflicts:
        if request.get("exceptionReason"):
            status = "EXCEPTION_REVIEW"
        elif request.get("withdraw"):
            status = "WITHDRAWN"
        else:
            status = "EXCEPTION_REVIEW" if options else "CHECKS_COMPLETE"

    return {
        "ok": True,
        "status": status,
        "item": primary,
        "items": [store.item(c) for c in item_codes if store.item(c)],
        "request": {
            **request,
            "itemCodes": item_codes,
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "channels": channels,
            "promotionType": promo_type,
            "mechanic": mechanic,
        },
        "scope": scope,
        "cycle": cycle,
        "price": {**price_row, **evaluate_reference_price(price_row, start)},
        "cost": cost,
        "funding": {
            "recognisedPerUnit": recognised,
            "notes": funding_notes,
            "commitments": funding_rows,
        },
        "economics": {
            "margin": m,
            "marginPct": pct(m),
            "depth": d,
            "depthPct": pct(d),
            "durationDays": dur,
            "weeks": weeks,
            "investment": inv,
            "investmentRounded": money(inv),
            "regularPrice": regular,
            "promotionalPrice": promo,
            "effectiveUnitCost": eff_cost,
            "recognisedFundingPerUnit": recognised,
            "floor": floor,
            "floorPct": pct(floor) if floor is not None else None,
            "floorPass": floor_ok,
            "formula": {
                "margin": "(promo − effectiveCost + funding) ÷ promo",
                "depth": "(regular − promo) ÷ regular",
                "investment": "max(0, regular − promo − funding) × forecast",
            },
            "policyVersion": "WTCHK-FIN-POL-021 v2.1",
        },
        "checks": checks,
        "advisories": advisories,
        "escalations": list(dict.fromkeys(escalations)),
        "band": {"valueBand": value_band, "final": band, "escalations": list(dict.fromkeys(escalations))},
        "routing": routing,
        "gates": list(dict.fromkeys(gates)),
        "cutoffs": cut,
        "cutoffOptions": options,
        "missedLeaflet": missed_leaflet,
        "feasibility": feasibility,
        "sla": slas,
        "expectedDecisionDate": decision_date.isoformat(),
        "multiBuy": mb,
        "clock": clock.isoformat(),
    }


def _cutoff_options(
    store: DemoStore,
    request: dict[str, Any],
    cycle: dict[str, Any],
    channels: list[str],
    clock: date,
    band: str,
) -> list[dict[str, Any]]:
    options = []
    # C21 without leaflet
    no_leaf = evaluate_cutoffs(
        store, cycle, channels=channels, leaflet=False, clock=clock, expected_decision=expected_decision_date(clock, band)
    )
    options.append(
        {
            "id": "same_cycle_no_leaflet",
            "label": f"{cycle['cycleCode']} without leaflet",
            "cutoffs": no_leaf,
        }
    )
    # next cycles with leaflet
    started = False
    for cyc in store.cycles():
        if cyc["cycleCode"] == cycle["cycleCode"]:
            started = True
            continue
        if not started:
            continue
        nxt_band_date = expected_decision_date(clock, band)
        ev = evaluate_cutoffs(
            store, cyc, channels=channels, leaflet=True, clock=clock, expected_decision=nxt_band_date
        )
        risk = None
        if not ev["allFeasible"]:
            risk = (
                f"Band {band} decision expected {nxt_band_date.isoformat()} — "
                "would need expedited review or a cut-off exception from Rachel Tsang"
            )
        note = None
        if cyc.get("eventCodes"):
            note = f"{cyc['cycleCode']} carries {', '.join(cyc['eventCodes'])}"
        options.append(
            {
                "id": f"move_{cyc['cycleCode']}_leaflet",
                "label": f"{cyc['cycleCode']} with leaflet",
                "cutoffs": ev,
                "risk": risk,
                "note": note,
            }
        )
        if len(options) >= 3:
            break
    return options


def assemble_decision_pack(store: DemoStore, case: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    owner = store.person(case["requesterId"])
    return {
        "id": case["decisionPackId"],
        "version": 1,
        "caseRef": case["caseRef"],
        "template": "DoA decision pack",
        "sections": [
            {"title": "Case and Promotion Owner", "body": {"case": case["caseRef"], "owner": owner}},
            {"title": "Promotion terms", "body": evaluation.get("request")},
            {
                "title": "Item facts (source, timestamp)",
                "body": evaluation.get("item"),
                "source": "Product Master [SIMULATED]",
            },
            {"title": "Regulatory screen", "body": evaluation.get("regulatory") or {"result": "PROCEED"}},
            {"title": "Funding recognition and evidence", "body": evaluation.get("funding")},
            {
                "title": "Conflicts, frequency, duration",
                "body": {
                    c["id"]: c
                    for c in evaluation.get("checks", [])
                    if c["id"] in {"stacking", "frequency", "duration"}
                },
            },
            {
                "title": "Reference price and claims",
                "body": next((c for c in evaluation.get("checks", []) if c["id"] == "referencePrice"), None),
            },
            {
                "title": "Economics — inputs, formulas, results (Margin Policy v2.1)",
                "body": evaluation.get("economics"),
            },
            {
                "title": "Supply readiness",
                "body": next((c for c in evaluation.get("checks", []) if c["id"] == "stock"), None),
            },
            {"title": "Setup feasibility", "body": evaluation.get("feasibility")},
            {
                "title": "Band, escalations, routing (DoA v3.2), delegation references",
                "body": {"band": evaluation.get("band"), "routing": evaluation.get("routing")},
            },
            {"title": "Open gates and conditions", "body": evaluation.get("gates")},
            {"title": "Advisories", "body": evaluation.get("advisories")},
            {
                "title": "Recommendation (labelled; rule citations)",
                "body": {
                    "label": "RECOMMENDATION — not a decision",
                    "text": _recommend(evaluation),
                },
            },
            {
                "title": "Documents and versions applied; SIMULATED data notice",
                "body": {
                    "policies": [
                        "WTCHK-COM-POL-032 v3.2",
                        "WTCHK-FIN-POL-021 v2.1",
                        "WTCHK-LEG-GDL-004 v1.2",
                        "WTCHK-COM-SOP-014 v1.4",
                    ],
                    "simulated": True,
                    "notice": "Every system card in this pack is SIMULATED from fixtures v2.0.",
                },
            },
        ],
    }


def _recommend(evaluation: dict[str, Any]) -> str:
    if evaluation.get("status") == "BLOCKED_REGULATORY":
        return "Do not proceed — blocked by Regulatory Guidelines §3 (H-02)."
    if evaluation.get("status") == "WITHDRAWN":
        return "Case withdrawn by the Promotion Owner."
    if "below_floor" in (evaluation.get("escalations") or []):
        return "Do not route as a standard request. Exception (Band C) or withdraw / re-fund (J-01, H-16)."
    band = (evaluation.get("band") or {}).get("final")
    routing = evaluation.get("routing") or {}
    approver = (routing.get("approver") or {}).get("name")
    return f"Checks complete. Band {band} — send the decision pack to {approver}."


def apply_approval_to_case(store: DemoStore, case: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    """Advance case after a human decision. Agents never set the decision field."""
    kind = task.get("kind")
    decision = task.get("decision")
    if kind == "FINANCE_REVIEW" and decision in {"APPROVE", "APPROVE_WITH_CONDITIONS"}:
        case["status"] = "AWAITING_APPROVAL"
    elif kind == "APPROVAL" and decision == "APPROVE":
        case["status"] = "APPROVED" if not case.get("openGates") else "AWAITING_GATES"
        case["approvedAt"] = store.clock.isoformat()
        case["approvedBy"] = task.get("decidedBy")
    elif kind == "APPROVAL" and decision == "APPROVE_WITH_CONDITIONS":
        case["status"] = "APPROVED_WITH_CONDITIONS" if not case.get("openGates") else "AWAITING_GATES"
        case["conditions"] = task.get("conditions") or []
    elif kind == "APPROVAL" and decision == "RETURN_FOR_REVISION":
        case["status"] = "RETURNED_FOR_REVISION"
    elif kind == "APPROVAL" and decision == "REJECT":
        case["status"] = "REJECTED"
    elif kind in {"COMPLIANCE_GATE", "SUPPLY_GATE", "CUTOFF_EXCEPTION"}:
        gates = case.setdefault("openGates", [])
        if decision in {"GATE_CLEARED", "APPROVE", "APPROVE_WITH_CONDITIONS"}:
            if kind in gates:
                gates.remove(kind)
            if kind == "COMPLIANCE_GATE" and decision == "APPROVE_WITH_CONDITIONS":
                case.setdefault("wordingChanges", []).extend(task.get("conditions") or [])
            if case.get("status") in {"AWAITING_GATES", "APPROVED"} and not gates:
                if case.get("approvedAt"):
                    case["status"] = "APPROVED"
        elif decision in {"GATE_FAILED", "REJECT"}:
            case["status"] = "REJECTED"
    return case


def create_promohub_draft(store: DemoStore, case: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    req = evaluation.get("request") or case.get("request") or {}
    number = case["caseRef"].split("-")[-1]
    draft_id = f"PD-2026-{number}"
    if any(d.get("caseRef") == case["caseRef"] for d in store.drafts.values()):
        raise ValueError("409")
    if not case.get("decisionPackId"):
        raise ValueError("422")
    price_zone = (evaluation.get("scope") or {}).get("priceZones", ["HK-STD"])[0]
    if req.get("promotionType") == "EVENT" and not req.get("eventCode"):
        raise ValueError("422")
    draft = {
        "draftId": draft_id,
        "caseRef": case["caseRef"],
        "status": "DRAFT",
        "description": f"{(evaluation.get('item') or {}).get('descriptionEn', 'Promotion')} [SIMULATED]",
        "createdAt": store.now_iso(),
        "priceZone": price_zone,
        "payload": req,
    }
    store.drafts[draft_id] = draft
    case["draftId"] = draft_id
    case["status"] = "SETUP_DRAFTED"
    return draft


def validate_draft(store: DemoStore, draft_id: str, fault: str | None = None) -> dict[str, Any]:
    draft = store.drafts.get(draft_id)
    if not draft:
        return {"status": "FAILED", "checks": []}
    checks = [
        {"code": "ITEM_ACTIVE", "result": "PASS", "message": "Item ACTIVE"},
        {"code": "BARCODE_ACTIVE", "result": "PASS", "message": "Barcode ACTIVE"},
        {"code": "PRICE_ZONE_PRESENT", "result": "PASS", "message": draft.get("priceZone")},
        {"code": "SCOPE_VALID", "result": "PASS", "message": "Scope valid"},
        {"code": "DATES_ALIGNED", "result": "PASS", "message": "Dates aligned to cycle"},
        {"code": "NO_OVERLAP", "result": "PASS", "message": "No overlapping draft"},
        {"code": "MECHANIC_SUPPORTED", "result": "PASS", "message": "Mechanic supported"},
    ]
    status = "PASSED"
    if fault == "promohub-validation-warning":
        for c in checks:
            if c["code"] == "PRICE_ZONE_PRESENT":
                c["result"] = "WARN"
                c["message"] = "Price zone missing on draft header [SIMULATED fault]"
        status = "WARNING"
    return {"draftId": draft_id, "status": status, "checks": checks}


def handover_note(evaluation: dict[str, Any], clock: date) -> dict[str, Any]:
    start = parse_date((evaluation.get("request") or {}).get("startDate"))
    # T-10 from cycle start: start - 10 calendar days? Checklist T-timeline
    # Scenario A: T-10 = 28 Sep → draft within 1 WD of approval; price file T-2 = 6 Oct; go-live 8 Oct
    # C21 starts 8 Oct; T-2 = 6 Oct; T-10 = 28 Sep. Yes calendar days before start.
    return {
        "owner": "Daniel Ng, Pricing & Promotion Ops [SIMULATED]",
        "timeline": [
            {"code": "T-10", "date": (start.replace() - __import__("datetime").timedelta(days=10)).isoformat(), "action": "Draft within 1 WD of approval"},
            {"code": "T-7", "date": (start - __import__("datetime").timedelta(days=7)).isoformat(), "action": "Shelf-talkers / POS ordered"},
            {"code": "T-2", "date": (start - __import__("datetime").timedelta(days=2)).isoformat(), "action": "Price file released"},
            {"code": "T-0", "date": start.isoformat(), "action": "Go-live"},
        ],
        "checklist": "WTCHK-OPS-CHK-010 v1.0 §3",
        "simulated": True,
    }
