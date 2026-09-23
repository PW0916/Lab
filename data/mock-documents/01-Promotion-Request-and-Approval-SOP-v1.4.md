# Promotion Request and Approval — Standard Operating Procedure

| | |
|---|---|
| **Document ID** | WTCHK-COM-SOP-014 |
| **Version** | 1.4 |
| **Effective date** | 1 July 2026 |
| **Document owner** | Head of Trade Marketing, Watsons Hong Kong |
| **Approved by** | Commercial Director |
| **Next review** | 30 June 2027 |
| **Applies to** | Trade Marketing, Category Management, Commercial Finance, Pricing & Promotion Operations, Supply Chain Planning, Compliance, Store Operations (Watsons Hong Kong, "WTCHK") |
| **Classification** | Internal — **fictional demonstration content** |

---

## 1. Purpose, scope and document hierarchy

### 1.1 Purpose

This SOP defines how a promotion for Watsons Hong Kong is requested, checked, approved, handed over for setup and evaluated. It exists so that every promotion is commercially sound, legally compliant, executable in stores and online, and approved by the right person before any price or mechanic reaches a customer.

### 1.2 Scope

In scope: temporary price and value promotions for items ranged in WTCHK stores, watsons.com.hk ("eShop"), the Watsons HK app ("App") and approved third-party marketplaces. This includes Standard, Flash, Local, Event and Clearance promotions and all mechanics listed in section 2.3.

Out of scope: permanent price changes (see Price Change Procedure WTCHK-COM-SOP-009), loyalty programme rule changes (Member Rewards Operating Manual), supplier-funded media without a price or value element, and Group-mandated cross-BU campaigns, which follow the Group Commercial Campaign Procedure but are still set up under section 8 of this SOP.

### 1.3 Document hierarchy

Where documents disagree, the higher document governs:

1. **Policies** — Delegation of Authority for Promotions and Pricing (WTCHK-COM-POL-032); Promotional Pricing, Margin and Funding Policy (WTCHK-FIN-POL-021); Regulatory and Restricted Category Guidelines (WTCHK-LEG-GDL-004, treated as policy for prohibitions).
2. **This SOP** and the Supplier Trade Funding Procedure (WTCHK-FIN-PRC-006).
3. **Operational checklists and calendars** — Promotion Setup and Go-Live Checklist (WTCHK-OPS-CHK-010); Promotion Cycle Calendar (WTCHK-TM-CAL-2026H2).
4. **Working notes, meeting minutes and email guidance** — informative only until incorporated into a controlled document.

Operational thresholds (approval limits, margin floors, cut-off days) are always read from the controlling policy or calendar, not from examples in this SOP.

---

## 2. Definitions

| Term | Meaning |
|---|---|
| **Promotion** | A time-bound change to price or value on one or more items, in one or more channels, requiring approval under this SOP. |
| **Promotion cycle** | The two-week trading period starting on a Thursday to which promotions are aligned. Cycles are numbered C01–C26 within the financial year (see calendar WTCHK-TM-CAL-2026H2). |
| **Promotion type** | Standard, Flash, Local, Event or Clearance — see 2.2. Determines duration limits, cut-offs and margin floor. |
| **Mechanic** | The form of the offer (price cut, multi-buy, gift with purchase, etc.) — see 2.3. Determines required inputs and POS/eShop setup. |
| **Regular price** | The current shelf price for the price zone as held in ERP. |
| **Promotional price** | The customer-facing price during the promotion. For multi-buy mechanics, the allocated price per item under the Margin Policy allocation method. |
| **Net promotion investment** | The margin given away by the promotion as defined in the Delegation of Authority policy, section 3. |
| **Store scope** | The set of stores in which the promotion applies, expressed as a scope code maintained by Store Operations (e.g. `HK-ALL`, `HKI-CORE`, `PILOT-20`). |
| **Channel** | `STORE`, `ESHOP`, `APP`, `MARKETPLACE`. |
| **Price zone** | Pricing grouping in ERP — `HK-STD` (all stores except airport) or `HK-AIRPORT`. |
| **Hero SKU** | A strategically important item designated by Trading. The hero SKU list is maintained by the Trading team. |
| **PromoHub** | Working name used by Pricing & Promotion Operations for the promotion management system in which promotions are created, validated and released to POS and eShop. |
| **Case** | A single promotion request tracked from submission to closure, with identifier `PR-YYYY-NNNN`. |
| **Working day** | Monday to Friday excluding Hong Kong general holidays. |

### 2.2 Promotion types

| Type | Definition | Maximum duration | Typical use |
|---|---|---|---|
| **Standard** | Price or value promotion aligned to one or two promotion cycles, in leaflet, in-store and/or digital | 28 days (two cycles) | Cycle promotions, supplier-funded price cuts |
| **Flash** | Short, high-impact price promotion, in-store and/or digital, not in leaflet | 72 hours | Weekend flash sale, app-only flash |
| **Local** | Promotion limited to a named store cluster or fewer than 30 stores, typically to respond to local competition or footfall | 28 days | Store cluster response, new store opening |
| **Event** | Promotion tied to a named trading event code (e.g. `MAF26` Mid-Autumn, `SD1111`, `BF26`, `XMAS26`, `CNY27`) | Event window as published | Seasonal events |
| **Clearance** | Price reduction on items with lifecycle status `PHASE_OUT` or `DELISTED`, to exit stock | Until stock exhausted, reviewed each cycle | Range exit |

### 2.3 Mechanics

| Code | Mechanic | Customer-facing example | Notes |
|---|---|---|---|
| `PRICE_CUT` | Temporary price reduction | "HK$89 (was HK$129)" | Comparative "was" price is subject to reference price rules (Guideline section 5) |
| `PCT_OFF` | Percentage off regular price | "20% off" | Setup as PRICE_CUT at item level in PromoHub |
| `MULTI_BUY_SAVE` | Buy N items, save HK$X | "Buy any 2, save HK$30" | Mix-and-match across an item list; margin tested by allocation method |
| `MULTI_BUY_2ND` | Second item at a discount | "2nd item 50% off" | Same-item or item-list |
| `BOGO` | Buy one get one free | "Buy 1 get 1 free" | Treated as 50% depth on two units |
| `GWP` | Gift with purchase | "Free travel kit with any HK$300 spend on brand X" | Gift item must be a ranged SKU or approved non-ranged gift |
| `MEMBER_PRICE` | Member-exclusive price | "Members HK$99" | Requires loyalty programme configuration; not permitted for prohibited regulatory classes |
| `BONUS_POINTS` | Extra loyalty points | "5× points" | Value promotion; investment calculated on point cost |
| `COUPON` | Coupon or voucher redemption | "HK$20 off with coupon" | Coupon terms must pass Compliance review |
| `BUNDLE` | Fixed bundle at a set price | "Skincare set HK$299" | Bundle code required from Product Master |

---

## 3. Roles and responsibilities

| Role | Responsibilities in this SOP |
|---|---|
| **Requester** (Trade Marketing Executive, Category Manager or Category Lead) | Prepares the request with complete and accurate inputs; declares supplier funding honestly; responds to information requests within one working day; owns the business rationale. |
| **Category Lead** | Owns category P&L; approves Band A promotions for their category (DoA); confirms supplier funding negotiations; decides whether to pursue exceptions. |
| **Head of Trade Marketing** | Owns this SOP, the promotion calendar and the request form; arbitrates process questions; monitors process KPIs. |
| **Finance Controller, Commercial** | Reviews margin, funding recognition and investment for Band B and above; owns the Margin Policy interpretation. |
| **Head of Trading** | Approves Band B promotions; approves cut-off exceptions; is informed of Band C decisions. |
| **Commercial Director** | Approves Band C promotions and all policy exceptions; owns the DoA policy. |
| **Managing Director** | Approves Band D promotions. |
| **Pricing & Promotion Operations Lead** | Confirms setup feasibility; creates and validates promotions in PromoHub after approval; releases price files; confirms go-live. |
| **Supply Chain Planner** | Confirms stock availability where cover is insufficient; arranges expedites or allocations. |
| **Compliance & Regulatory Manager** | Reviews restricted-category promotions, comparative price claims and promotional wording; maintains the Regulatory Guidelines. |
| **Store Operations** | Publishes store bulletins; confirms in-store execution; reports execution issues. |
| **Marketing (Leaflet & Digital)** | Produces leaflet, shelf-talker and digital creative to cut-off. |

---

## 4. Preparing a request

### 4.1 Required information — all mechanics

1. Requester name, role and business function.
2. Item code(s) (Product Master item code) or approved bundle code; barcode optional for cross-check.
3. Promotion type (section 2.2) and mechanic (section 2.3).
4. Proposed promotional price, discount or offer terms.
5. Start and end dates (aligned to a promotion cycle unless Flash or Event).
6. Channel(s) and store scope code.
7. Forecast units for the promotion period (total units sold at the promotional terms).
8. Supplier funding declaration: none / claimed (supplier, funding type, amount, funding reference if known).
9. Business rationale (minimum: objective, expected outcome, competitive or seasonal context).
10. Leaflet inclusion required: yes / no.

### 4.2 Additional information by mechanic

| Mechanic | Additional required inputs |
|---|---|
| `MULTI_BUY_SAVE`, `MULTI_BUY_2ND`, `BUNDLE` | Full eligible item list; whether mix-and-match is allowed; maximum redemptions per transaction |
| `GWP` | Gift item code or description, gift cost, gift quantity available, spend threshold |
| `MEMBER_PRICE`, `BONUS_POINTS` | Member segment (all members / tier / new members); points cost confirmation from Loyalty team |
| `COUPON` | Coupon code, distribution channel, redemption limit, terms wording |
| Flash (any mechanic) | Exact start and end time (HKT); channel; confirmation that no leaflet is required |
| Event (any mechanic) | Event code from the calendar |
| Clearance | Confirmation of lifecycle status and remaining stock; target exit date |

### 4.3 Item eligibility

- Item lifecycle status must be `ACTIVE` or `NEW`. `PHASE_OUT` items are eligible only if the promotion ends on or before the delist date, or as Clearance. `DELISTED` items are not eligible except as Clearance.
- Items in a **prohibited regulatory class** may not be promoted in any mechanic (Guideline section 3). Items in a **restricted regulatory class** require Compliance review (Guideline section 4).
- Barcodes must be active in Product Master; PromoHub cannot set up an item whose barcode is inactive.

### 4.4 Forecast guidance

Forecast units are the total units expected to sell at the promotional terms in the requested scope and period. Requesters should start from the baseline weekly rate for the scope (available from the Sales & Stock Insights dashboard) and apply the uplift benchmark for the category and mechanic from the latest Post-Promotion Evaluation. Forecasts materially above or below benchmark must be explained in the rationale.

### 4.5 Supplier funding

Only funding recorded in the Trade Funding Register with status `CONFIRMED` and valid evidence is recognised in margin and investment calculations (Margin Policy section 5; Funding Procedure). Funding agreed verbally or by email but not yet confirmed must be declared as "claimed, evidence pending"; the request can proceed with funding recognised as zero, or pause until evidence is filed.

---

## 5. Submission timing

### 5.1 Alignment to cycles

Standard and Local promotions start on the first day of a promotion cycle and end on the last day of a cycle. Flash promotions may start on any day. Event promotions follow the published event window.

### 5.2 Cut-offs

Requests must be **approved** (not merely submitted) by the cut-off for the intended execution route. Cut-offs are published in the Promotion Cycle Calendar and are counted back from the promotion start date:

| Execution route | Cut-off (calendar days before start unless stated) |
|---|---|
| Leaflet inclusion (print) | Per calendar — currently 21 days |
| Digital only (eShop / App) | Per calendar — currently 10 days |
| In-store price change with shelf talker, no leaflet | Per calendar — currently 7 days |
| Flash (in-store and/or digital) | 5 working days |

> **Implementation note (v1.3):** Requesters should allow two working days for Finance review and two for approver decision when planning against the cut-off.

If a cut-off cannot be met, the requester may (a) move the promotion to the next cycle, (b) change the execution route to one whose cut-off can still be met, or (c) request a cut-off exception from the Head of Trading, giving the commercial reason and the operational impact confirmed by Pricing & Promotion Operations.

---

## 6. Checking procedure

Checks 6.1 to 6.8 are performed for every request before it is routed for approval. The person or system performing the check records the result, the data source and the timestamp on the case.

### 6.1 Item and commercial data

Retrieve from Product Master and ERP: item description, brand, category hierarchy, own-brand flag, supplier, lifecycle status and delist date, regulatory class, barcode status, regular price for the price zone, current landed cost and any confirmed off-invoice adjustment for the promotion period. Retrieve from Sales & Stock Insights: baseline weekly units for the scope, promotion history for the last 12 weeks, stock on hand and confirmed inbound.

### 6.2 Regulatory eligibility screen

Apply the Regulatory Guidelines. Prohibited classes stop the request immediately with the reason and the guideline reference. Restricted classes create a Compliance review task that runs in parallel with the commercial approval; the promotion may not be released to setup until Compliance has approved.

### 6.3 Completeness

Confirm all required inputs under section 4 are present and internally consistent (for example, dates align to a cycle, the store scope code exists, the mechanic is supported for the channel). Request missing information from the requester; the case clock pauses while waiting.

### 6.4 Funding recognition

Look up the Trade Funding Register for commitments covering the item, period and channel. Apply the recognition rules in the Margin Policy section 5. Where the requester claims funding that is not `CONFIRMED`, pause and offer the requester the choice to file evidence or proceed with funding recognised as zero.

### 6.5 Calendar conflicts, stacking and frequency

Search PromoHub for planned, approved or active promotions on the same item(s). A promotion is **blocked** if another price or value mechanic applies to the same item, channel and overlapping dates, unless the earlier promotion is withdrawn or the request is re-scoped. Count promotion weeks in the rolling 12 weeks before the start date and apply the frequency rule in the Margin Policy section 7.

### 6.6 Promotion economics and stock cover

Calculate promotional margin, discount depth, net promotion investment, and — where the margin floor is not met — the minimum promotional price or minimum funding per unit needed to meet the floor. Apply the forecast plausibility check in the Margin Policy section 10. Confirm stock cover: stock on hand plus confirmed inbound arriving at least three days before the start date must be at least 110% of forecast units; otherwise create a Supply Chain confirmation task.

### 6.7 Reference price and claims

For any mechanic that displays a comparative price ("was", "save", "% off"), apply the reference price rule in the Guidelines section 5. Where the comparison is not permitted, the promotion may proceed only with non-comparative "Special Price" messaging and Compliance review of the wording.

### 6.8 Approval routing

Determine the approval band and any escalation under the Delegation of Authority policy. Resolve the named approver, reviewer and informed parties from the Authority Directory as at the expected decision date, apply segregation of duties, and identify the recorded delegate if the primary approver is unavailable.

---

## 7. Approval

### 7.1 Decision pack

Every request routed for approval carries a decision pack containing: request facts; item and commercial data with sources and timestamps; regulatory screen result; funding recognition result and evidence references; conflict and frequency results; economics with formulas and inputs; stock cover result; reference price result; approval band, escalation conditions triggered and named approvers; open conditions; recommendation; and the versions of this SOP and each policy applied.

### 7.2 Decision options

| Decision | Meaning | Who |
|---|---|---|
| **Approve** | Proceed to setup as requested | Approver for the band |
| **Approve with conditions** | Proceed subject to stated conditions (e.g. funding evidence before go-live, wording change) | Approver for the band |
| **Return for revision** | Requester to change price, dates, scope, mechanic or forecast and resubmit | Reviewer or approver |
| **Reject** | Do not proceed; reason recorded | Approver for the band |
| **Escalate** | Refer to the next band with reason | Reviewer or approver |

Approval is given only by a human holding the authorised role. Systems and agents prepare, route and record but do not approve (DoA section 8).

### 7.3 Service levels

| Step | Target |
|---|---|
| Completeness and checks (6.1–6.8) | Same working day for complete requests |
| Finance review (Band B and above) | 2 working days |
| Approver decision | 2 working days from receipt of the decision pack |
| Compliance review | 3 working days |
| Supply Chain confirmation | 1 working day |
| Reminder to approver | After 1 working day without decision |
| Escalation to recorded delegate | After 3 working days without decision, or immediately if the approver is recorded as unavailable |

The end-to-end target from complete submission to decision is 5 working days for Band A and B, and 8 working days for Band C.

---

## 8. After approval — handover and setup

1. The case is handed to Pricing & Promotion Operations with the approved terms and the decision pack reference.
2. Pricing & Promotion Operations creates the promotion in PromoHub, validates it and confirms the setup identifier back to the case (Checklist section 3).
3. Marketing produces leaflet, shelf-talker and digital assets to the timelines in the Checklist.
4. Store Operations issues the store bulletin for in-store promotions.
5. Price files are released to POS and eShop per the Checklist. No promotion may be released without an approved case reference.
6. On the go-live day, Pricing & Promotion Operations completes the go-live check and records any variance.

---

## 9. Post-promotion evaluation

Within 10 working days after the promotion ends, the requester completes a Post-Promotion Evaluation (PPE) covering: forecast vs actual units, uplift vs baseline, realised margin vs approved, funding claimed vs recognised, stock-outs, and learning. Category-level uplift benchmarks are refreshed from PPEs each quarter and published for use in forecasting (section 4.4).

---

## 10. Exceptions and escalation

Any departure from a policy rule (margin floor, depth, frequency, duration, stacking) is an **exception** and must be approved by the Commercial Director under the DoA policy, with Finance review, regardless of investment. The request must state the exception sought, the reason, the expected commercial benefit and the proposed mitigation. Exceptions are recorded in the exceptions log and reported to the Commercial Director monthly.

Process disputes (for example, whether a request is complete) are referred to the Head of Trade Marketing.

---

## 11. Records and audit

- Every case has a unique identifier `PR-YYYY-NNNN` and retains the request, all check results with sources, the decision pack, decisions with decision-maker and timestamp, setup confirmation and PPE.
- Case records are retained for seven years.
- Decisions made by delegates must record the delegation reference.
- Data obtained from any simulated or test environment must be labelled as such and may not be used as evidence for a live promotion.

---

## 12. Process KPIs

| KPI | Target |
|---|---|
| First-time-right submissions (no return for information) | ≥ 70% |
| Submission to decision, Band A/B | ≤ 5 working days |
| Promotions set up correctly at go-live (no price variance) | ≥ 99% |
| Post-promotion evaluations completed on time | ≥ 90% |
| Exceptions as a share of approved promotions | ≤ 10% |

---

## 13. Revision history

| Version | Date | Change |
|---|---|---|
| 1.2 | 1 March 2025 | Added Flash type; added Compliance review for comparative claims |
| 1.3 | 15 January 2026 | Added stock-cover check (6.6); added implementation note on Band B (see below); added PPE section |
| 1.4 | 1 July 2026 | Added Event and Clearance types; aligned cut-off table to the calendar; added mechanic table |

> **Implementation note (retained from v1.3):** For planning purposes, Band B covers investments between HK$50,001 and HK$150,000; anything above requires the Commercial Director. Refer to the DoA policy for current limits.

---

## Appendix A — Request form fields (current Excel / Forms template)

See WTCHK-TM-FORM-PR-2026 (Promotion Request Form). Mandatory fields: Requester, Function, Category, Item code(s), Description (auto), Promotion type, Mechanic, Regular price (auto), Promotional price / offer, Start date, End date, Channels, Store scope code, Forecast units, Funding declared (Y/N), Supplier, Funding type, Funding amount, Funding reference, Leaflet (Y/N), Business rationale, Attachments.

## Appendix B — Mechanic setup requirements (summary)

| Mechanic | POS | eShop / App | Leaflet | Loyalty config | Notes |
|---|---|---|---|---|---|
| PRICE_CUT / PCT_OFF | Item price override | Item price override | Yes if requested | No | Standard |
| MULTI_BUY_SAVE / MULTI_BUY_2ND | Promotion group | Cart rule | Yes if requested | No | Item list maintained in PromoHub |
| BOGO | Promotion group | Cart rule | Yes if requested | No | |
| GWP | Promotion group with gift SKU | Cart rule with gift SKU | Yes if requested | No | Gift SKU stock allocated |
| MEMBER_PRICE | Member price flag | Member price flag | Members-only messaging | Yes | Loyalty team lead time 10 days |
| BONUS_POINTS | Loyalty rule | Loyalty rule | Optional | Yes | |
| COUPON | Coupon rule | Coupon code | Optional | Optional | Compliance-reviewed terms |
| BUNDLE | Bundle SKU | Bundle SKU | Yes if requested | No | Bundle code from Product Master |

## Appendix C — Case outcome codes

`READY_FOR_APPROVAL` · `MORE_INFO_REQUIRED` · `RETURNED_FOR_REVISION` · `EXCEPTION_REVIEW` · `BLOCKED_REGULATORY` · `APPROVED` · `APPROVED_WITH_CONDITIONS` · `REJECTED` · `WITHDRAWN` · `SETUP_CONFIRMED` · `LIVE` · `ENDED` · `PPE_COMPLETE`
