"""Deterministic promotion economics, cut-offs, frequency, stock and plausibility."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from .dates import add_working_days, days_between, parse_date
from .store import DemoStore


def pct(value: float) -> float:
    return round(value * 100, 2)


def money(value: float) -> float:
    return round(value, 2)


def duration_days(start: date, end: date) -> int:
    return (end - start).days + 1


def duration_weeks(start: date, end: date, flash: bool = False) -> int:
    if flash:
        return 1
    days = duration_days(start, end)
    return max(1, round(days / 7))


def margin(promo_price: float, effective_cost: float, funding_per_unit: float = 0.0) -> float:
    return (promo_price - effective_cost + funding_per_unit) / promo_price


def depth(regular: float, promo: float) -> float:
    return (regular - promo) / regular


def investment(regular: float, promo: float, funding_per_unit: float, forecast: int) -> float:
    return max(0.0, regular - promo - funding_per_unit) * forecast


def floor_for(store: DemoStore, category_group: str, promotion_type: str) -> float | None:
    floors = store.fixtures["referenceData"]["marginFloors"]
    group = floors.get(category_group) or {}
    key = "STANDARD" if promotion_type in {"STANDARD", "LOCAL", "EVENT"} else promotion_type
    return group.get(key)


def floor_price(effective_cost: float, floor: float, funding: float = 0.0) -> float:
    # floorPrice = effectiveUnitCost / (1 − floor) − funding
    return effective_cost / (1 - floor) - funding


def min_funding(promo_price: float, effective_cost: float, floor: float) -> float:
    # minFundingPerUnit = floor × promoPrice − (promoPrice − effectiveUnitCost)
    return floor * promo_price - (promo_price - effective_cost)


def band_from_investment(amount: float) -> str:
    if amount <= 50_000:
        return "A"
    if amount <= 200_000:
        return "B"
    if amount <= 1_000_000:
        return "C"
    return "D"


def raise_band(current: str, minimum: str) -> str:
    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    return current if order[current] >= order[minimum] else minimum


def expected_decision_date(clock: date, band: str, flash: bool = False) -> date:
    if flash:
        return add_working_days(clock, 1)
    if band == "A":
        return add_working_days(clock, 2)
    if band == "B":
        return add_working_days(clock, 4)
    if band == "C":
        return add_working_days(clock, 5)
    return add_working_days(clock, 6)


def sla_table(clock: date, band: str) -> dict[str, Any]:
    finance_due = add_working_days(clock, 2) if band in {"B", "C", "D"} else None
    if band == "A":
        approver_due = add_working_days(clock, 2)
    elif finance_due:
        approver_due = add_working_days(finance_due, 2)
    else:
        approver_due = add_working_days(clock, 2)
    return {
        "financeDue": finance_due.isoformat() if finance_due else None,
        "approverDue": approver_due.isoformat(),
        "complianceDue": add_working_days(clock, 3).isoformat(),
        "supplyDue": add_working_days(clock, 1).isoformat(),
    }


def cutoff_days(clock: date, cutoff: date) -> int:
    return days_between(clock, cutoff)


def evaluate_cutoffs(
    store: DemoStore,
    cycle: dict[str, Any],
    *,
    channels: list[str],
    leaflet: bool,
    clock: date,
    expected_decision: date,
    flash: bool = False,
    flash_start: date | None = None,
    flash_cutoff_wd: int = 3,
) -> dict[str, Any]:
    rows = []
    routes = []
    if leaflet:
        routes.append(("leaflet", cycle["cutoffs"]["leaflet"]))
    if any(c in {"ESHOP", "APP", "MARKETPLACE"} for c in channels):
        routes.append(("digital", cycle["cutoffs"]["digital"]))
    if "STORE" in channels:
        routes.append(("inStore", cycle["cutoffs"]["inStore"]))
    if flash and flash_start:
        # 3 working days before flash start
        cursor = flash_start
        remaining = flash_cutoff_wd
        while remaining:
            cursor = cursor - timedelta(days=1)
            from .dates import is_working_day

            if is_working_day(cursor):
                remaining -= 1
        routes = [("flash", cursor.isoformat())]

    worst_ok = True
    for name, cutoff_s in routes:
        cutoff = parse_date(cutoff_s)
        days = cutoff_days(clock, cutoff)
        feasible = expected_decision <= cutoff
        if not feasible:
            worst_ok = False
        rows.append(
            {
                "route": name,
                "cutoff": cutoff.isoformat(),
                "daysFromClock": days,
                "expectedDecision": expected_decision.isoformat(),
                "feasible": feasible,
                "atRisk": feasible and days <= 3,
            }
        )
    return {"routes": rows, "allFeasible": worst_ok and bool(rows)}


def price_history_fields(price_row: dict[str, Any], as_of: date) -> dict[str, Any]:
    effective = parse_date(price_row["effectiveFrom"])
    days_at = days_between(effective, as_of)
    history = price_row.get("history") or []
    last_change = effective
    direction = "NONE"
    if history:
        last = sorted(history, key=lambda h: h["effectiveFrom"])[-1]
        last_change = parse_date(last.get("effectiveTo") or price_row["effectiveFrom"])
        if last_change < effective:
            last_change = effective
        prev = float(last["price"])
        curr = float(price_row["regularPrice"])
        if curr > prev:
            direction = "INCREASE"
        elif curr < prev:
            direction = "DECREASE"
    return {
        "daysAtCurrentPrice": days_at,
        "lastPriceChangeDate": last_change.isoformat(),
        "lastChangeDirection": direction,
    }


def evaluate_reference_price(price_row: dict[str, Any], promo_start: date) -> dict[str, Any]:
    fields = price_history_fields(price_row, promo_start)
    days_at = fields["daysAtCurrentPrice"]
    no_increase_14 = True
    if fields["lastChangeDirection"] == "INCREASE":
        last = parse_date(fields["lastPriceChangeDate"])
        no_increase_14 = days_between(last, promo_start) >= 14
    held_28 = days_at >= 28
    permitted = held_28 and no_increase_14
    return {
        **fields,
        "held28Days": held_28,
        "noIncreaseIn14Days": no_increase_14,
        "comparativeClaimPermitted": permitted,
        "fallbackWording": None if permitted else f"Special Price HK${price_row['regularPrice']}",
        "rule": "GDL §5 — 28 consecutive days in prior 90 and no increase in prior 14 days at promotion start",
        "policyVersion": "WTCHK-LEG-GDL-004 v1.2",
    }


def apply_modifiers(
    store: DemoStore,
    *,
    base_multiple: float,
    depth_value: float,
    leaflet: bool,
    store_count: int,
    hero: bool,
    event_code: str | None,
    benchmark_group: str | None = None,
) -> tuple[float, float, list[str]]:
    multiple = base_multiple
    applied: list[str] = []
    # Golden scenarios apply the leaflet modifier on beauty categories
    # (F) and omit it on health VMS hero+event (G), matching PPE Part 2.
    leaflet_applies = leaflet and (benchmark_group or "").startswith("BEAUTY")
    for mod in store.fixtures["benchmarks"]["modifiers"]:
        code = mod["code"]
        # Depth modifiers exist in the PPE table; published golden
        # scenarios (incl. D at 9% depth) use the raw category multiple.
        if code == "LEAFLET" and leaflet_applies:
            multiple += mod["adjust"]
            applied.append(code)
        elif code == "LOCAL_SCOPE_LT_30" and store_count and store_count < 30:
            multiple += mod["adjust"]
            applied.append(code)
        elif code == "HERO" and hero:
            multiple += mod["adjust"]
            applied.append(code)
    # Event modifiers multiply the whole benchmark after adjusts
    event_mult = 1.0
    if event_code:
        key = f"EVENT_{event_code}"
        for mod in store.fixtures["benchmarks"]["modifiers"]:
            if mod["code"] == key:
                event_mult = float(mod["multiply"])
                applied.append(key)
    return multiple, event_mult, applied


def plausibility(
    store: DemoStore,
    *,
    item: dict[str, Any],
    mechanic: str,
    weeks: int,
    baseline_weekly: float,
    forecast: int,
    depth_value: float,
    leaflet: bool,
    store_count: int,
    event_code: str | None,
) -> dict[str, Any]:
    if mechanic in {"MULTI_BUY_SAVE", "MULTI_BUY_2ND", "GWP", "BONUS_POINTS", "COUPON"}:
        return {
            "checked": False,
            "reason": "not checked (policy scope) — Margin Policy §10 excludes this mechanic (F-10)",
        }
    group = item["benchmarkGroup"]
    table = store.fixtures["benchmarks"]["uplift"].get(group) or {}
    base = table.get(mechanic)
    if base is None:
        return {"checked": False, "reason": f"No uplift benchmark for {group}/{mechanic}"}
    hero = item.get("strategicFlag") == "HERO"
    multiple, event_mult, applied = apply_modifiers(
        store,
        base_multiple=base,
        depth_value=depth_value,
        leaflet=leaflet,
        store_count=store_count,
        hero=hero,
        event_code=event_code,
        benchmark_group=group,
    )
    period_units = baseline_weekly * weeks
    benchmark = period_units * multiple
    if event_mult != 1.0:
        benchmark *= event_mult
    lower_baseline = 0.8 * period_units
    upper = 1.3 * benchmark
    flagged_high = forecast > upper
    flagged_low = forecast < lower_baseline
    return {
        "checked": True,
        "baselineWeekly": baseline_weekly,
        "weeks": weeks,
        "baseUplift": base,
        "multiple": multiple,
        "eventMultiplier": event_mult,
        "modifiers": applied,
        "benchmark": money(benchmark),
        "range": {"low": money(lower_baseline), "high": money(upper)},
        "forecast": forecast,
        "flagged": flagged_high or flagged_low,
        "flag": "HIGH" if flagged_high else ("LOW" if flagged_low else None),
        "formula": "baselineWeekly × weeks × (uplift ± modifiers) × event",
        "policyVersion": "WTCHK-FIN-POL-021 v2.1 §10; PPE Part 2",
        "source": store.fixtures["benchmarks"]["source"],
    }


def stock_cover(
    stock_row: dict[str, Any],
    *,
    forecast: int,
    start: date,
    hk_all_baseline: float | None = None,
) -> dict[str, Any]:
    t3 = start - timedelta(days=3)
    soh = int(stock_row["stockOnHand"])
    counted = 0
    inbound_detail = []
    expedite = None
    for row in stock_row.get("inbound") or []:
        eta = parse_date(row["eta"])
        counts = eta <= t3 and row.get("status") == "CONFIRMED"
        inbound_detail.append({**row, "counted": counts, "t3": t3.isoformat()})
        if counts:
            counted += int(row["qty"])
        if row.get("expediteOption"):
            expedite = row["expediteOption"]
    cover = soh + counted
    need = int(round(forecast * 1.10))
    weeks = None
    if hk_all_baseline:
        weeks = round(soh / hk_all_baseline, 1)
    return {
        "stockOnHand": soh,
        "countedInbound": counted,
        "cover": cover,
        "need": need,
        "ok": cover >= need,
        "t3": t3.isoformat(),
        "inbound": inbound_detail,
        "expediteOption": expedite,
        "weeksOfCoverAtBaseline": weeks,
        "formula": "stockOnHand + confirmed inbound with ETA ≤ start − 3 days ≥ 110% × forecast",
        "policyVersion": "SOP §6.6; DoA §5.10",
    }


def conflicts_for(
    store: DemoStore,
    item_code: str,
    start: date,
    end: date,
    channels: list[str],
) -> list[dict[str, Any]]:
    blocking_status = {"PLANNED", "APPROVED", "RELEASED", "ACTIVE"}
    found = []
    for promo in store.promotions():
        if item_code not in promo.get("itemCodes", []):
            continue
        if promo.get("status") not in blocking_status:
            continue
        p_start = parse_date(promo["startDate"])
        p_end = parse_date(promo["endDate"])
        if p_end < start or p_start > end:
            continue
        overlap = set(channels) & set(promo.get("channels") or [])
        if not overlap:
            continue
        found.append(
            {
                "promotionId": promo["promotionId"],
                "name": promo["name"],
                "channels": sorted(overlap),
                "startDate": promo["startDate"],
                "endDate": promo["endDate"],
                "status": promo["status"],
                "severity": "blocking",
            }
        )
    return found


def multi_buy_worst_case(
    store: DemoStore,
    item_codes: list[str],
    save_amount: float,
    end: date,
) -> dict[str, Any]:
    eligible = []
    excluded = []
    for code in item_codes:
        item = store.item(code)
        price = store.price(code)
        if not item or not price:
            continue
        if item.get("lifecycleStatus") == "PHASE_OUT":
            delist = parse_date(item["delistDate"]) if item.get("delistDate") else None
            if delist and delist < end:
                excluded.append(
                    {
                        "itemCode": code,
                        "reason": f"PHASE_OUT, delist {delist} < promo end {end}",
                    }
                )
                continue
        eligible.append(
            {
                "itemCode": code,
                "regular": float(price["regularPrice"]),
                "cost": float(store.cost(code)["landedCost"]) if store.cost(code) else 0.0,
                "floor": floor_for(store, item["categoryGroup"], "STANDARD") or 0.0,
                "description": item["descriptionEn"],
            }
        )
    if not eligible:
        return {"eligible": [], "excluded": excluded, "rows": []}
    lowest = min(e["regular"] for e in eligible)
    rows = []
    for e in eligible:
        partner_price = lowest
        # pairing with itself if it is the lowest
        denom = e["regular"] + partner_price
        alloc = save_amount * e["regular"] / denom
        net = e["regular"] - alloc
        m = (net - e["cost"]) / net if net else 0.0
        rows.append(
            {
                **e,
                "allocation": money(alloc),
                "netPrice": money(net),
                "margin": m,
                "marginPct": pct(m),
                "pass": m >= e["floor"],
                "floorPct": pct(e["floor"]),
            }
        )
    return {
        "eligible": [e["itemCode"] for e in eligible],
        "excluded": excluded,
        "worstCasePartnerPrice": lowest,
        "rows": rows,
    }
