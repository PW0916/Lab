# Promotion Request Form — Template and Completion Guidance

| | |
|---|---|
| **Document ID** | WTCHK-TM-FORM-PR-2026 |
| **Version** | 2026.2 (Excel template `PR_Form_2026v2.xlsx` and Microsoft Forms mirror) |
| **Document owner** | Head of Trade Marketing |
| **Classification** | Internal — **fictional demonstration content** |

This document describes the form BU teams complete today. It is included so the platform can learn the exact fields, permitted values and validation that requesters are already used to, and so that the conversational intake asks for the same things in the same language.

---

## Section A — Requester

| Field | Type | Required | Validation / values |
|---|---|---|---|
| Requester name | Text | Yes | Must match Authority Directory |
| Employee ID | Text | Yes | Format `E#####` |
| Function | Dropdown | Yes | Trade Marketing / Category Management / Marketing / eCommerce |
| Category | Dropdown | Yes | From merchandise hierarchy level 2 |
| Contact (Teams/email) | Text | Yes | |

## Section B — Promotion

| Field | Type | Required | Validation / values |
|---|---|---|---|
| Campaign / promotion name | Text | Yes | ≤ 60 characters; used as PromoHub description |
| Promotion type | Dropdown | Yes | Standard / Flash / Local / Event / Clearance |
| Event code | Dropdown | If Event | From calendar |
| Mechanic | Dropdown | Yes | PRICE_CUT / PCT_OFF / MULTI_BUY_SAVE / MULTI_BUY_2ND / BOGO / GWP / MEMBER_PRICE / BONUS_POINTS / COUPON / BUNDLE |
| Start date | Date | Yes | Must be a cycle start unless Flash/Event |
| End date | Date | Yes | Must be a cycle end unless Flash/Event; ≤ 28 days for Standard/Local |
| Flash start / end time (HKT) | Time | If Flash | ≤ 72 hours |
| Channels | Multi-select | Yes | STORE / ESHOP / APP / MARKETPLACE |
| Store scope code | Dropdown | If STORE | From Store Network scope list |
| Leaflet inclusion | Yes/No | Yes | If Yes, leaflet cut-off applies |

## Section C — Items and offer

Repeat per item (or attach the item list sheet for multi-buy/bundle).

| Field | Type | Required | Validation / values |
|---|---|---|---|
| Item code | Text | Yes | Product Master lookup; description, brand, category, regular price and status auto-filled |
| Barcode (cross-check) | Text | No | 13 digits |
| Regular price (auto) | Currency | Auto | ERP `HK-STD` |
| Promotional price / offer terms | Currency or text | Yes | For PRICE_CUT: HKD to one decimal place. For MULTI_BUY_SAVE: saving amount and qualifying quantity |
| Forecast units (or sets) | Integer | Yes | > 0; see guidance |
| Comparative claim intended | Yes/No | Yes | "Was / Save / % off" messaging — triggers reference price check |

## Section D — Supplier funding

| Field | Type | Required | Validation / values |
|---|---|---|---|
| Funding declared | Yes/No | Yes | |
| Supplier code | Text | If Yes | Supplier master |
| Funding type | Dropdown | If Yes | SCAN_BACK / LUMP_SUM / OFF_INVOICE / FREE_GOODS / COOP_MEDIA |
| Rate / amount (HKD) | Currency | If Yes | |
| Maximum funded quantity | Integer | No | |
| Funding reference | Text | No | Trade Funding Register reference `FC-YYYY-NNN` if known |
| Evidence attached | Yes/No | If Yes | Confirmation letter (PDF) |

## Section E — Rationale and attachments

| Field | Type | Required | Guidance |
|---|---|---|---|
| Objective | Dropdown | Yes | Volume / Margin / Traffic / Clearance / Competitive response / New product trial / Supplier event |
| Business rationale | Text (≤ 800 characters) | Yes | Objective, expected outcome, competitive or seasonal context, why now |
| Forecast basis | Text | Yes | Baseline used, uplift assumed, source |
| Exception requested | Yes/No + text | Yes | If Yes, state the rule, reason, benefit and mitigation |
| Attachments | Files | No | Funding letter, competitor price evidence, supplier brief |

## Completion guidance (from the form's "Read me" tab)

1. Look up the item first — if the item shows `PHASE_OUT` or `DELISTED`, talk to your Category Lead before requesting.
2. Baseline weekly units for your scope are on the Sales & Stock Insights dashboard ("Promo planning" view). Multiply by the number of weeks and by the category uplift benchmark in the latest PPE. Explain any big difference.
3. Funding counts only when Finance has confirmed it. If your supplier has agreed by email, say so — but expect the request to be treated as unfunded until the letter is filed.
4. Check the PromoHub calendar for other promotions on your item. Two price offers on the same item in the same channel at the same time will be blocked.
5. If you want to say "was HK$X", the regular price needs to have been stable for a while — the form will warn you if the price changed recently.
6. Approval takes up to five working days. Count back from the cut-off.

## Known limitations of the current form (from the Trade Marketing improvement log)

- The form does not check PromoHub for conflicts; requesters find out at the checking step.
- Store scope codes are typed free-text in the Forms mirror, causing invalid scopes.
- Funding evidence is attached as a PDF and manually matched to the register.
- Forecast plausibility is not checked at entry.
- No visibility of case status after submission; requesters chase by email.
