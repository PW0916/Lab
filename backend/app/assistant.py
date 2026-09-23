"""Conversational Workflow Assistant — deterministic intake, explanation and Q&A."""

from __future__ import annotations

import re
from typing import Any

from .cases import cases_for, create_case, refresh_all_tasks, route_case
from .engine import evaluate_request
from .funding import verify_evidence
from .store import STORE

ITEM_ALIASES = [
    (["wtc-vitc-1000-20", "vitamin c", "維他命c", "維他命 c", "effervescent"], "WTC-VITC-1000-20"),
    (["wtc-multi-60", "multivitamin", "綜合維他命"], "WTC-MULTI-60"),
    (["glw-srm-30ml", "glow radiance", "glow serum", "glow"], "GLW-SRM-30ML"),
    (["sunv-spf50-100", "sunveil", "spf50", "spf 50"], "SUNV-SPF50-100"),
    (["pure-if-s1-900", "stage 1", "infant formula", "嬰兒配方", "purenest stage 1", "purenest 1"], "PURE-IF-S1-900"),
    (["pure-gum-s3-900", "stage 3", "growing-up", "growing up", "幼兒成長", "purenest stage 3"], "PURE-GUM-S3-900"),
    (["medr-ibu-200-24", "ibuprofen", "medirelief", "布洛芬"], "MEDR-IBU-200-24"),
    (["frsh-tp-2x150", "freshmint", "toothpaste", "twin pack", "牙膏"], "FRSH-TP-2X150"),
    (["aqua-msk-5p", "aquadew", "mask", "面膜"], "AQUA-MSK-5P"),
    (["omg-fo-1000-100", "omega-3", "omega 3", "oceanpure", "魚油"], "OMG-FO-1000-100"),
    (["derm-cln-150", "dermacalm", "cleanser", "潔面"], "DERM-CLN-150"),
    (["lumi-tnr-200", "lumiere", "lumière", "toner", "爽膚"], "LUMI-TNR-200"),
    (["blsm-lip-4g", "blossom", "lip balm", "潤唇"], "BLSM-LIP-4G"),
    (["kind-dpr-m64", "kindersoft", "nappies", "紙尿"], "KIND-DPR-M64"),
]

SCOPE_ALIASES = {
    "pilot": "PILOT-20",
    "20 store": "PILOT-20",
    "20 pilot": "PILOT-20",
    "pilot-20": "PILOT-20",
    "hong kong island core and kowloon east": "HKI-KLNE",
    "island core and kowloon east": "HKI-KLNE",
    "hki-klne": "HKI-KLNE",
    "island core": "HKI-CORE",
    "hki-core": "HKI-CORE",
    "all stores": "HK-ALL",
    "hk-all": "HK-ALL",
    "everywhere": "HK-ALL",
    "all hong kong": "HK-ALL",
}


def detect_language(text: str) -> str:
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def find_item(text: str) -> str | None:
    low = text.lower()
    # Prefer longer / more specific aliases first
    ranked = sorted(ITEM_ALIASES, key=lambda p: -max(len(a) for a in p[0]))
    for aliases, code in ranked:
        if any(a in low for a in aliases):
            return code
    return None


def find_scope(text: str) -> str | None:
    low = text.lower()
    for alias, code in sorted(SCOPE_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if alias in low:
            return code
    return None


def find_cycle(text: str) -> str | None:
    m = re.search(r"\bC(2[0-8])\b", text, re.I)
    if m:
        return f"C{m.group(1)}"
    low = text.lower()
    if "next cycle" in low or "下一個週期" in low or "下个周期" in low:
        return "C21"
    return None


def find_price(text: str) -> float | None:
    patterns = [
        r"(?:at|to|down to|降至|減至|賣)\s*(?:hk\$|hkd)?\s*(\d+(?:\.\d+)?)",
        r"(?:hk\$|\$)\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:dollars|蚊)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return float(m.group(1))
    return None


def find_forecast(text: str) -> int | None:
    m = re.search(r"(\d[\d,]*)\s*(?:units|unit|件|盒|罐)", text, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    m = re.search(r"forecast\s*(?:of\s*)?(\d[\d,]*)", text, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def find_funding_ref(text: str) -> str | None:
    m = re.search(r"FC-2026-\d{3}", text, re.I)
    return m.group(0).upper() if m else None


def extract_slots(text: str) -> dict[str, Any]:
    low = text.lower()
    slots: dict[str, Any] = {}
    item = find_item(text)
    if item:
        slots["itemCode"] = item
    scope = find_scope(text)
    if scope:
        slots["storeScope"] = scope
    cycle = find_cycle(text)
    if cycle:
        slots["cycle"] = cycle
    price = find_price(text)
    if price is not None and price < 1000:
        slots["promotionalPrice"] = price
    forecast = find_forecast(text)
    if forecast:
        slots["forecast"] = forecast
    ref = find_funding_ref(text)
    if ref:
        slots["fundingRef"] = ref
    if re.search(r"leaflet|夾頁|傳單", low):
        slots["leaflet"] = True
    if re.search(r"no leaflet|without leaflet|唔要夾頁|不要夹页", low):
        slots["leaflet"] = False
    if re.search(r"stores only|store only|門店 only|只係舖|只在店", low):
        slots["channels"] = ["STORE"]
    if re.search(r"all channels|everywhere|全渠道", low):
        slots["channels"] = ["STORE", "ESHOP", "APP"]
        if "storeScope" not in slots:
            slots["storeScope"] = "HK-ALL"
    if re.search(r"eshop|e-shop|網店", low):
        slots.setdefault("channels", ["STORE"]).append("ESHOP")
        slots["channels"] = list(dict.fromkeys(slots["channels"]))
    if re.search(r"\bapp\b", low):
        slots.setdefault("channels", ["STORE"]).append("APP")
        slots["channels"] = list(dict.fromkeys(slots["channels"]))
    if re.search(r"was |save hk|show the saving|show the was|比較價|原價", low):
        slots["comparativeClaimIntended"] = True
    if re.search(r"10%\s*off|member", low) and "infant" in low or "stage 1" in low:
        slots["mechanic"] = "MEMBER_PRICE"
    if re.search(r"flash", low):
        slots["flash"] = True
        slots["promotionType"] = "FLASH"
    if re.search(r"sd1111|singles.?day|11\.11", low):
        slots["eventCode"] = "SD1111"
        slots["promotionType"] = "EVENT"
    if "free goods" in low or "free units" in low:
        slots["fundingRef"] = slots.get("fundingRef") or "FC-2026-058"
    if "scan-back" in low or "scan back" in low or "12 dollars" in low or "12 a unit" in low:
        if not slots.get("fundingRef") and slots.get("itemCode") == "GLW-SRM-30ML":
            slots["fundingRef"] = "FC-2026-041"
    if "fc-2026-033" in low or "lump sum" in low:
        if slots.get("itemCode") == "SUNV-SPF50-100":
            slots["fundingRef"] = "FC-2026-033"
    if "fc-2026-052" in low or "25 a unit" in low or "funds 25" in low:
        if slots.get("itemCode") == "OMG-FO-1000-100":
            slots["fundingRef"] = "FC-2026-052"
    return slots


LETTER_EXTRACTED = {
    "supplierName": "Glow Beauty Laboratories (HK) Ltd",
    "authorisedContact": "Cheryl Kwan",
    "itemCodes": ["GLW-SRM-30ML"],
    "fundingType": "SCAN_BACK",
    "ratePerUnit": 12.0,
    "fundedCap": 2000,
    "periodFrom": "2026-10-01",
    "periodTo": "2026-11-30",
    "channels": ["STORE"],
    "conditions": {"minSellingPrice": 129.0},
}


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def knowledge_answer(text: str) -> str | None:
    low = text.lower()
    if "flash" in low and ("ibuprofen" in low or "medirelief" in low or "布洛芬" in low):
        return (
            "No — `MEDR-IBU-200-24` is PHARMACY_ONLY_P1: no public price promotion in any mechanic "
            "(Guideline §3). Also, OTC general-sale medicines cannot run Flash promotions "
            "(Margin Policy §3)."
        )
    if "flash" in low and ("cut-off" in low or "cutoff" in low or "cut off" in low):
        return (
            "3 working days before the Flash start (Calendar v2.0 §2). Note: SOP v1.4 §5.2 still says 5; "
            "the process owner decided to apply the calendar and log an SOP revision (F-02). "
            "Example: Flash on Sat 3 Oct → approve by Tue 29 Sep (1 Oct is a holiday)."
        )
    if "who approve" in low or "who approves" in low or ("120" in low and "rachel" in low):
        return (
            "Band B → Finance review (Priscilla Lam) then Head of Trading. "
            "If the expected decision date falls 12–16 Oct, Michelle Fung via DLG-2026-018 (DoA §6.3)."
        )
    if "sunveil" in low and ("band c" in low or "why" in low):
        case = STORE.cases.get("PR-2026-1044")
        extra = ""
        if case:
            extra = " Measured values are on case PR-2026-1044."
        return (
            "Band C because three escalations stacked (H-16/H-17 below floor, H-14 unresolved stacking on eShop, "
            f"H-15 frequency > 6). Highest band wins (DoA §5).{extra}"
        )
    return None


def status_answer(actor_id: str) -> str:
    refresh_all_tasks()
    rows = cases_for(actor_id)
    if not rows:
        return f"As of {STORE.clock.isoformat()} you have no cases in this demo session."
    lines = [f"As of {STORE.clock.isoformat()}:"]
    for case in rows:
        ev = case.get("evaluation") or {}
        item = (ev.get("item") or {}).get("descriptionEn") or (case.get("request") or {}).get("itemCode")
        extra = []
        for task in case.get("tasks") or []:
            if task.get("status") == "REASSIGNED":
                extra.append(
                    f"{task['kind']} reassigned to {(task.get('assignee') or {}).get('name')} "
                    f"({(task.get('assignee') or {}).get('viaDelegation')})"
                )
            elif task.get("status") == "REMINDED":
                extra.append(f"{task['kind']} reminded")
        cut = ev.get("cutoffs") or {}
        for route in cut.get("routes") or []:
            if route.get("urgent"):
                extra.append(f"{route['route']} cut-off {route['cutoff']} — {route['daysFromClock']} days left")
        if case.get("draftId"):
            extra.append(f"PromoHub {case['draftId']} [SIMULATED]")
        if case.get("status") in {"SETUP_CONFIRMED", "APPROVED"} and (case.get("request") or {}).get("startDate"):
            if STORE.clock.isoformat() >= (case.get("request") or {})["startDate"]:
                extra.append(f"LIVE from {case['request']['startDate']}")
        lines.append(f"- {case['caseRef']} {item} — **{case['status']}**" + (f" ({'; '.join(extra)})" if extra else ""))
    return "\n".join(lines)


def _sim(text: str) -> str:
    return text


def describe_item(item: dict[str, Any]) -> str:
    hero = "hero SKU" if item.get("strategicFlag") == "HERO" else item.get("strategicFlag")
    brand = "own brand" if item.get("ownBrand") else item.get("brand")
    return (
        f"`{item['itemCode']}` {item['descriptionEn']} — {brand}, {item['lifecycleStatus']}, {hero} "
        f"[SIMULATED · Product Master]"
    )


def format_checks(ev: dict[str, Any]) -> str:
    econ = ev.get("economics") or {}
    lines = ["Checks complete."]
    margin_c = next((c for c in ev.get("checks", []) if c["id"] == "margin"), None)
    if margin_c:
        status = "passes" if margin_c["status"] == "green" else "fails"
        lines.append(
            f"- Margin {margin_c['value']:.2f}% — {status} the {margin_c['floor']:.2f}% floor "
            f"(inputs: promo HK${econ.get('promotionalPrice')}, cost HK${econ.get('effectiveUnitCost')}, "
            f"funding HK${econ.get('recognisedFundingPerUnit')}; "
            f"{econ.get('formula', {}).get('margin')}; {econ.get('policyVersion')})."
        )
    for adv in ev.get("advisories") or []:
        lines.append(f"- Advisory {adv['id']}: {adv['text']}")
    depth_c = next((c for c in ev.get("checks", []) if c["id"] == "depth"), None)
    if depth_c:
        lines.append(f"- Depth {depth_c['value']}%; duration {econ.get('durationDays')} days.")
    freq = next((c for c in ev.get("checks", []) if c["id"] == "frequency"), None)
    if freq:
        bits = [f"{ch} {v['total']}" for ch, v in (freq.get("value") or {}).items()]
        note = f" {freq['note']}." if freq.get("note") else ""
        lines.append(f"- Frequency: {', '.join(bits)} / 6.{note}")
    ref = next((c for c in ev.get("checks", []) if c["id"] == "referencePrice"), None)
    if ref:
        val = ref["value"]
        if val.get("comparativeClaimPermitted"):
            lines.append(f"- Comparative claim permitted: price held {val['daysAtCurrentPrice']} days.")
        elif ev.get("request", {}).get("comparativeClaimIntended"):
            lines.append(
                f"- Comparative claim **not** permitted ({val['daysAtCurrentPrice']} days at price). "
                f"Fallback: {val.get('fallbackWording')}."
            )
            if val.get("nextCycle") and val["nextCycle"].get("permitted"):
                nc = val["nextCycle"]
                lines.append(
                    f"- If you move to {nc['cycle']} ({nc['start']}) the price will have been held "
                    f"{nc['daysAtPrice']} days and the comparison becomes permissible."
                )
    plaus = next((c for c in ev.get("checks", []) if c["id"] == "plausibility"), None)
    if plaus and (plaus.get("value") or {}).get("checked"):
        pv = plaus["value"]
        if pv.get("flagged"):
            lines.append(
                f"- Forecast {pv['forecast']} is {pv['flag']} vs benchmark {pv['benchmark']} "
                f"(range {pv['range']['low']}–{pv['range']['high']})."
            )
            if pv.get("eventSuggestion"):
                lines.append(f"- {pv['eventSuggestion']['note']}")
        else:
            lines.append(f"- Forecast {pv['forecast']} is in line with the benchmark ({pv['benchmark']}).")
    stock = next((c for c in ev.get("checks", []) if c["id"] == "stock"), None)
    if stock:
        sv = stock["value"]
        if sv["ok"]:
            lines.append(f"- Stock cover {sv['cover']} ≥ {sv['need']} — OK.")
        else:
            lines.append(
                f"- Stock cover {sv['cover']} < {sv['need']} — Supply Chain gate."
            )
            if sv.get("expediteOption"):
                ex = sv["expediteOption"]
                lines.append(
                    f"  Expedite option: ETA {ex['eta']}, ~HK${ex['costHkd']}, confirm by {ex['confirmBy']} [SIMULATED]."
                )
    stack = next((c for c in ev.get("checks", []) if c["id"] == "stacking"), None)
    if stack and stack.get("value"):
        for cfl in stack["value"]:
            lines.append(f"- Conflict: {cfl['name']} ({cfl['promotionId']}) on {', '.join(cfl['channels'])}.")
    fund = ev.get("funding") or {}
    if fund.get("recognisedPerUnit"):
        lines.append(f"- Recognised funding HK${fund['recognisedPerUnit']}/unit.")
    band = ev.get("band") or {}
    routing = ev.get("routing") or {}
    approver = (routing.get("approver") or {}).get("name")
    reviewer = (routing.get("reviewer") or {}).get("name")
    lines.append(
        f"- Investment HK${econ.get('investmentRounded'):,.0f} → **Band {band.get('final')}**"
        + (f" → review {reviewer}," if reviewer else " →")
        + f" approver {approver}."
    )
    if ev.get("expectedDecisionDate"):
        lines.append(f"- Expected decision {ev['expectedDecisionDate']}.")
    if ev.get("cutoffs"):
        bits = []
        for r in ev["cutoffs"].get("routes") or []:
            sign = "+" if r["daysFromClock"] >= 0 else ""
            bits.append(f"{r['route']} {r['cutoff']} ({sign}{r['daysFromClock']} days)")
        if bits:
            lines.append(f"- Cut-offs: {'; '.join(bits)}.")
    return "\n".join(lines)


def handle_message(conversation: dict[str, Any], text: str, upload: dict[str, Any] | None = None) -> dict[str, Any]:
    lang = detect_language(text)
    conversation["language"] = lang
    pending = conversation.setdefault("pending", {})
    slots = extract_slots(text)
    for k, v in slots.items():
        if k == "channels" and pending.get("channels") and v:
            pending["channels"] = list(dict.fromkeys([*(pending.get("channels") or []), *v]))
        else:
            pending[k] = v
    pending["requesterId"] = conversation.get("actorId") or STORE.identity_id

    low = text.lower().strip()

    # Status
    if re.search(r"where are my cases|我的個案|我的个案|status of my", low):
        return {"text": status_answer(pending["requesterId"]), "cards": {"cases": cases_for(pending["requesterId"])}}

    # Knowledge
    ka = knowledge_answer(text)
    if ka and not slots.get("promotionalPrice"):
        return {"text": ka, "cards": {"knowledge": True}}

    # Confirmations / choices
    if re.search(r"^yes$|^correct$|^ok$|^send$|^send it$|^yes,? send|^好$|^係$|^对$|^發送$|^发送$", low):
        if pending.get("awaiting") == "confirm_intent":
            pending["awaiting"] = None
            pending["intentConfirmed"] = True
            if pending.get("channels") is None:
                pending["channels"] = ["STORE"]
            if pending.get("leaflet") is None:
                pending["leaflet"] = False
            return _after_intent(pending, conversation)
        if pending.get("awaiting") == "send":
            return _send_case(conversation, pending)
        if pending.get("awaiting") == "event_tag":
            pending["eventCode"] = pending.get("suggestedEvent") or "SD1111"
            pending["promotionType"] = "EVENT"
            pending["awaiting"] = None
            return _run_eval(conversation, pending)
        if pending.get("awaiting") == "funding":
            pending["proceedWithZeroFunding"] = True
            pending["awaiting"] = None
            return _run_eval(conversation, pending)

    if re.search(r"withdraw", low):
        pending["withdraw"] = True
        ev = evaluate_request(STORE, pending)
        ev["status"] = "WITHDRAWN"
        case = create_case(pending, ev)
        conversation["pending"] = {}
        conversation["lastCase"] = case["caseRef"]
        sam = STORE.person_by_role("CATEGORY_LEAD_BEAUTY")
        STORE.notifications.append(
            {
                "notificationId": STORE.next_id("notification"),
                "to": [sam["employeeId"]] if sam else [],
                "kind": "STATUS_UPDATE",
                "caseRef": case["caseRef"],
                "message": f"{case['caseRef']} withdrawn — analysis attached. Notify Samantha Yip.",
                "simulated": True,
            }
        )
        return {
            "text": (
                f"Withdrawn as {case['caseRef']} with the analysis attached; "
                f"{(sam or {}).get('name', 'Samantha Yip')} notified."
            ),
            "cards": {"evaluation": ev, "case": case},
        }

    if re.search(r"option 2|c22 with leaflet|ask rachel", low):
        pending["cycle"] = "C22"
        pending["leaflet"] = True
        pending["requestCutoffException"] = True
        pending["chosenCutoffOption"] = "move_C22_leaflet"
        return _run_eval(conversation, pending, auto_send=True)

    if re.search(r"keep c21|special price", low):
        pending["cycle"] = pending.get("cycle") or "C21"
        pending["comparativeClaimIntended"] = True
        pending["claimFallbackAccepted"] = True
        return _run_eval(conversation, pending, auto_send=True)

    if re.search(r"stage 3|growing-up|298", low) and pending.get("itemCode") in {None, "PURE-IF-S1-900"}:
        pending["itemCode"] = "PURE-GUM-S3-900"
        pending["promotionalPrice"] = pending.get("promotionalPrice") or 298
        pending["storeScope"] = pending.get("storeScope") or "HK-ALL"
        pending["cycle"] = pending.get("cycle") or "C22"
        pending["forecast"] = pending.get("forecast") or 1200
        pending["fundingRef"] = "FC-2026-047"
        pending["channels"] = ["STORE"]
        return _run_eval(conversation, pending)

    if re.search(r"tag it sd1111|tag sd1111|yes.? tag", low):
        pending["eventCode"] = "SD1111"
        pending["promotionType"] = "EVENT"
        return _run_eval(conversation, pending, auto_send=True)

    if re.search(r"retry", low) and pending.get("costUnavailable"):
        pending["costUnavailable"] = False
        STORE.fault = None
        return _run_eval(conversation, pending)

    if upload or re.search(r"letter|upload|我有信", low):
        if pending.get("fundingRef") == "FC-2026-041" or (upload and "041" in str(upload)):
            pending["fundingRef"] = "FC-2026-041"
            ev_preview = evaluate_request(STORE, {**pending, "forceEvaluate": True, "proceedWithZeroFunding": True})
            req = ev_preview.get("request") or pending
            verification = verify_evidence(
                STORE,
                "FC-2026-041",
                LETTER_EXTRACTED,
                "GBL/TF/2026/0917",
                {
                    "periodFrom": req.get("startDate"),
                    "periodTo": req.get("endDate"),
                    "channels": req.get("channels") or ["STORE"],
                    "forecastUnits": pending.get("forecast"),
                    "promotionalPrice": pending.get("promotionalPrice"),
                },
            )
            pending["proceedWithZeroFunding"] = True  # now confirmed
            result = _run_eval(conversation, pending)
            result["cards"] = result.get("cards") or {}
            result["cards"]["verification"] = verification
            result["text"] = (
                "Extracted: Glow Beauty Laboratories, signed by Cheryl Kwan (authorised contact), "
                "ref GBL/TF/2026/0917, item GLW-SRM-30ML, scan-back HK$12.00, cap 2,000, "
                "1 Oct–30 Nov, stores only, minimum selling price HK$129. All seven checks pass → verified; "
                "the Register record is now CONFIRMED [SIMULATED verifier: Finance Controller]. "
                "Note: the letter excludes eShop and the app.\n\n"
                + result["text"]
            )
            return result

    # New / continuing intake
    if pending.get("itemCode"):
        return _progress(conversation, pending, text)

    return {
        "text": (
            "Tell me the item (name or code), the offer, the cycle and the stores. "
            "I will look it up and confirm it back — you do not need a form."
        ),
        "cards": {},
    }


def _progress(conversation: dict[str, Any], pending: dict[str, Any], text: str) -> dict[str, Any]:
    item = STORE.item(pending["itemCode"])
    if not item:
        return {"text": f"I could not find `{pending['itemCode']}` in Product Master [SIMULATED].", "cards": {}}

    # Regulatory early
    ev_reg = evaluate_request(STORE, {**pending, "allowPartial": True})
    if ev_reg.get("status") == "BLOCKED_REGULATORY":
        alts = ev_reg.get("alternatives") or []
        alt_txt = ""
        if alts:
            bits = []
            for a in alts:
                extra = ""
                if a["itemCode"] == "KIND-DPR-M64":
                    extra = (
                        f" — regular margin {a['regularMarginPct']}% vs {a['floorPct']}% floor, "
                        f"anything below HK${a['floorPriceUnfunded']} would need funding"
                    )
                bits.append(f"`{a['itemCode']}` {a['descriptionEn']}{extra}")
            alt_txt = " Permitted options: " + "; ".join(bits) + "."
        conversation["lastEval"] = ev_reg
        case = create_case(pending, ev_reg)
        conversation["pending"] = {"requesterId": pending.get("requesterId")}
        return {
            "text": (
                f"No. {describe_item(item)}. Under the Regulatory Guidelines §3 it cannot be promoted "
                f"in any mechanic — price, member price, points, gifts or bundles. "
                f"I've recorded the request as {case['caseRef']} (BLOCKED_REGULATORY) so there is an audit trail."
                f"{alt_txt}"
            ),
            "cards": {"evaluation": ev_reg, "case": case, "item": item},
        }

    price = STORE.price(item["itemCode"])
    cycle_code = pending.get("cycle")
    cycle = STORE.cycle(cycle_code) if cycle_code else STORE.cycle("C21")
    if not pending.get("cycle"):
        pending["cycle"] = "C21"
        cycle = STORE.cycle("C21")

    need_confirm = not pending.get("intentConfirmed")
    if need_confirm and not (
        pending.get("promotionalPrice")
        and pending.get("forecast")
        and pending.get("storeScope")
        and pending.get("channels")
    ):
        pending["awaiting"] = "confirm_intent"
        scope = STORE.scope(pending.get("storeScope") or "")
        scope_txt = ""
        if scope:
            scope_txt = f" `{scope['scopeCode']}` is {scope['storeCount']} stores."
        elif not pending.get("storeScope"):
            scope_txt = " Which store scope?"
        ch = pending.get("channels")
        ch_q = "" if ch else " Stores only, or digital as well?"
        leaf = pending.get("leaflet")
        leaf_q = "" if leaf is not None else " Leaflet — yes or no?"
        return {
            "text": (
                f"Found {describe_item(item)}. Regular HK${price['regularPrice']} [SIMULATED · ERP]. "
                f"Cycle {pending['cycle']}, {cycle['startDate']}–{cycle['endDate']}.{scope_txt}{ch_q}{leaf_q}"
            ),
            "cards": {"item": item, "price": price, "cycle": cycle, "scope": scope},
        }

    pending["intentConfirmed"] = True
    return _after_intent(pending, conversation)


def _after_intent(pending: dict[str, Any], conversation: dict[str, Any] | None = None) -> dict[str, Any]:
    missing = []
    if pending.get("promotionalPrice") is None:
        missing.append("promotional price")
    if pending.get("forecast") is None:
        missing.append("forecast units for the two weeks")
    if pending.get("storeScope") is None:
        missing.append("store scope")
    if pending.get("channels") is None:
        pending["channels"] = ["STORE"]
    if pending.get("leaflet") is None:
        pending["leaflet"] = False
    if "comparativeClaimIntended" not in pending:
        # ask if we still need more anyway
        if missing:
            missing.append("whether you want a 'was' / save claim")
    if missing:
        pending["awaiting"] = "offer_details"
        item = STORE.item(pending["itemCode"])
        restriction = STORE.restriction(item["regulatoryClass"]) or {}
        return {
            "text": (
                f"Regulatory: {item['regulatoryClass']} — permitted"
                + (
                    ", Compliance review if the copy makes claims."
                    if restriction.get("complianceReview") == "IF_CLAIMS"
                    else "."
                )
                + f" I still need: {', '.join(missing)}."
            ),
            "cards": {"item": item},
        }
    return _run_eval(conversation or {"pending": pending}, pending)


def _run_eval(conversation: dict[str, Any], pending: dict[str, Any], auto_send: bool = False) -> dict[str, Any]:
    if STORE.fault == "erp-cost-timeout" and not pending.get("costRetried"):
        pending["costUnavailable"] = True
    ev = evaluate_request(STORE, pending)
    conversation["lastEval"] = ev
    conversation["pending"] = pending

    if ev.get("status") == "WAITING_DATA":
        pending["costUnavailable"] = True
        return {
            "text": (
                "I couldn't get the cost from ERP — the request timed out. "
                "That means I can't compute the margin or test the floor, and I won't estimate it "
                "(Margin Policy §12). I can retry now, or park the case and tell Finance."
            ),
            "cards": {"evaluation": ev},
        }

    if ev.get("pause") == "FUNDING_EVIDENCE":
        pending["awaiting"] = "funding"
        wf = ev["funding"]["withoutFunding"]
        return {
            "text": (
                f"The Register has {ev['funding']['pending']['fundingRef']}: "
                f"{ev['funding']['pending']['fundingType']} HK${ev['funding']['pending'].get('ratePerUnit')}, "
                f"status **{ev['funding']['pending']['status']}**. "
                "Under the Margin Policy I can only recognise confirmed funding. "
                f"Two options: upload the confirmation letter now, or I proceed with funding at zero "
                f"(margin {wf['marginPct']}%, investment HK${wf['investment']:,.0f}, Band {wf['band']})."
            ),
            "cards": {"evaluation": ev, "funding": ev["funding"]},
        }

    if ev.get("missedLeaflet") and not pending.get("chosenCutoffOption") and not pending.get("requestCutoffException"):
        pending["awaiting"] = "cutoff"
        opts = ev.get("cutoffOptions") or []
        lines = ["The leaflet cut-off for this cycle has already passed, so that route is gone. Options:"]
        for i, opt in enumerate(opts, 1):
            extra = f" — {opt['risk']}" if opt.get("risk") else ""
            note = f" ({opt['note']})" if opt.get("note") else ""
            lines.append(f"{i}. {opt['label']}{extra}{note}")
        return {"text": "\n".join(lines), "cards": {"evaluation": ev}}

    if ev.get("status") in {"EXCEPTION_REVIEW"} and ev.get("cutoffOptions"):
        pending["awaiting"] = "exception"
        lines = [format_checks(ev), "", "I have to stop here rather than route this. Options:"]
        for i, opt in enumerate(ev["cutoffOptions"], 1):
            rec = " — recommended" if opt.get("recommended") else ""
            lines.append(f"{i}. {opt['label']}{rec}")
        return {"text": "\n".join(lines), "cards": {"evaluation": ev}}

    text = format_checks(ev)
    # Event suggestion prompt
    plaus = next((c for c in ev.get("checks", []) if c["id"] == "plausibility"), None)
    if plaus and (plaus.get("value") or {}).get("eventSuggestion") and not pending.get("eventCode"):
        pending["awaiting"] = "event_tag"
        pending["suggestedEvent"] = plaus["value"]["eventSuggestion"]["code"]
        text += "\n\nTag the event code so the forecast check and PromoHub stay aligned?"
        return {"text": text, "cards": {"evaluation": ev}}

    if auto_send:
        pending["awaiting"] = "send"
        return _send_case(conversation, pending)

    pending["awaiting"] = "send"
    text += "\n\nShall I send the decision pack?"
    return {"text": text, "cards": {"evaluation": ev}}


def _send_case(conversation: dict[str, Any], pending: dict[str, Any]) -> dict[str, Any]:
    ev = conversation.get("lastEval") or evaluate_request(STORE, pending)
    if pending.get("withdraw"):
        ev["status"] = "WITHDRAWN"
    case = create_case(pending, ev)
    if case["status"] not in {"BLOCKED_REGULATORY", "WITHDRAWN", "WAITING_DATA"}:
        route_case(case)
    conversation["pending"] = {"requesterId": pending.get("requesterId")}
    conversation["lastCase"] = case["caseRef"]
    routing = ev.get("routing") or {}
    who = (routing.get("reviewer") or routing.get("approver") or {}).get("name")
    extra = ""
    if ev.get("gates"):
        extra = f" Parallel gates: {', '.join(ev['gates'])}."
    return {
        "text": f"Sent. Case {case['caseRef']} is with {who}.{extra}",
        "cards": {"evaluation": ev, "case": case},
    }
