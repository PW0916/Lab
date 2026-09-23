# Workflow System Context Intake — Promotion Request and Approval

| | |
|---|---|
| **Prepared by** | Grace Ma (DataLab Business Partner) with Daniel Ng (Pricing & Promotion Ops) and Mei Wong (Head of Trade Marketing) |
| **Date** | 24 September 2026 |
| **Purpose** | Provide the minimum system and data context the agentic platform needs to simulate the workflow without live integration. Business rules are **not** captured here; they live in the uploaded policies and SOP. |
| **Classification** | Internal — **fictional demonstration content** |

This is the only template the BU completes. Everything else is uploaded as-is.

---

## 1. Workflow summary

| Field | Content |
|---|---|
| Workflow name | Promotion Request and Approval |
| Business unit | Watsons Hong Kong (WTCHK) |
| Trigger | A Trade Marketing or Category colleague wants to run a promotion |
| Users | ~35 requesters; 5 Category Leads; Finance Controller; Head of Trading; Commercial Director; Pricing Ops (3); Supply Chain (2); Compliance (2) |
| Volume | 35–45 requests per cycle; peaks of 80+ before `SD1111` and `XMAS26` |
| Today's pain | Requests returned for missing data (~30%); manual margin recalculation by Finance; conflicts discovered late; no status visibility; PromoHub drafts returned for missing event code / price zone |
| Outcome wanted | Requesters get a complete, policy-checked, correctly routed case in one sitting; approvers see a decision pack, not a form |

## 2. Systems engaged

For each system: what it is for in this workflow, the operations the workflow needs, key fields, a representative example, sensitivity, how it will be simulated, and the future integration path.

### 2.1 Product Master (PIM / MDM) — "Item Master"

- **Owner:** Group IT Master Data; business owner Merchandising Operations
- **Purpose in workflow:** Resolve item code to description, hierarchy, brand, own-brand flag, supplier, lifecycle, delist date, regulatory class, barcode status, strategic (hero) flag, approved claims, channel eligibility.
- **Operations needed:** Get item by item code; search by description or barcode.
- **Key fields:** `itemCode`, `barcode`, `descriptionEn`, `descriptionZh`, `brand`, `ownBrand`, `supplierCode`, `hierarchy{division, department, class, subclass}`, `categoryGroup`, `lifecycleStatus`, `delistDate`, `regulatoryClass`, `strategicFlag`, `approvedClaims[]`, `channelEligibility[]`, `packSize`
- **Example:** `WTC-VITC-1000-20` → Watsons Vitamin C 1000mg Effervescent 20s, Own brand, Health / Vitamins & Supplements, `ACTIVE`, `HEALTH_SUPPLEMENT`, `HERO`
- **Sensitivity:** Low (product reference data)
- **Simulation:** Deterministic fixture of ~14 items across categories, including prohibited/restricted classes and a phase-out item
- **Future integration:** Read-only API via Group integration layer (exists for eShop)

### 2.2 ERP — Pricing and Cost

- **Owner:** Group IT ERP; business owners Pricing Ops (prices) and Commercial Finance (costs)
- **Purpose:** Regular price by price zone with price history (needed for the reference price rule); landed cost; confirmed off-invoice adjustments by period.
- **Operations:** Get price by item, price zone, as-of date (with history for 120 days); get cost by item, as-of date (with off-invoice adjustments).
- **Key fields:** `regularPrice`, `priceZone`, `effectiveFrom`, `priceHistory[{price, effectiveFrom, effectiveTo}]`, `daysAtCurrentPrice`, `lastPriceChangeDate`, `lastChangeDirection`; `landedCost`, `costBasis`, `costEffectiveFrom`, `offInvoiceAdjustments[{ref, amountPerUnit, from, to, status}]`
- **Example:** `FRSH-TP-2X150` price 59.9 since 18 Sep 2026 (previously 54.9); landed cost 30.0; off-invoice 4.0/unit 1–31 Oct `CONFIRMED`
- **Sensitivity:** Cost is commercially sensitive — **fictional values only in the demo**
- **Simulation:** Fixture per item; supports fault injection (timeout) to show non-guessing behaviour
- **Future integration:** ERP OData read service; cost access restricted to Finance-scoped service identity

### 2.3 Sales & Stock Insights (Data Warehouse / BI)

- **Owner:** DataLab
- **Purpose:** Baseline weekly units by scope and channel; promotion history (weeks on promotion in rolling 12 weeks by channel); stock on hand; confirmed inbound with ETA; uplift benchmarks by category group and mechanic (from PPE).
- **Operations:** Get item performance by scope; get stock position; get benchmarks.
- **Key fields:** `baselineWeeklyUnits`, `scope`, `channelSplit`, `promoWeeksLast12ByChannel`, `lastPromoUplift`, `stockOnHand`, `inbound[{qty, eta, status}]`, `weeksOfCover`; `benchmarks[{categoryGroup, mechanic, uplift, eventModifiers}]`
- **Sensitivity:** Medium
- **Simulation:** Fixture per item and scope
- **Future integration:** DataLab-owned semantic layer; first candidate for live connection because DataLab controls it

### 2.4 Store Network

- **Owner:** Store Operations
- **Purpose:** Validate store scope codes; store counts; formats; price zone membership.
- **Operations:** Get scope by code.
- **Key fields:** `scopeCode`, `name`, `storeCount`, `priceZones[]`, `formats[]`, `openOnDate`
- **Example:** `PILOT-20` → 20 stores (HKI-CORE and KLN-EAST subset), `HK-STD`
- **Simulation:** Fixture of 12 scope codes

### 2.5 Promotion Management System — "PromoHub"

- **Owner:** Group IT Retail Apps; business owner Pricing & Promotion Ops
- **Purpose:** Promotion cycles and cut-offs; existing planned/approved/active promotions by item, dates and channel (conflict search); event codes; after approval, create and validate a promotion draft.
- **Operations:** Get cycles; search promotions; get event codes; create draft; get draft validation.
- **Key fields:** `cycleCode`, `startDate`, `endDate`, `cutoffs{leaflet, digital, inStore}`, `eventCodes[]`; `promotionId`, `itemCodes[]`, `mechanic`, `channels[]`, `storeScope`, `startDate`, `endDate`, `status`; `draftId`, `validationStatus`, `messages[]`
- **Sensitivity:** Low–medium
- **Simulation:** Fixture with ~8 existing promotions designed to create overlap, adjacency and frequency cases; draft creation is a labelled simulation
- **Future integration:** PromoHub has a REST API used by eShop; write access requires Group IT change approval

### 2.6 Trade Funding Register

- **Owner:** Commercial Finance (Excel + SharePoint list today; moving to a Power Apps register)
- **Purpose:** Supplier funding commitments and status; evidence verification.
- **Operations:** Search commitments by item and period; verify an uploaded confirmation document against a commitment.
- **Key fields:** `fundingRef`, `supplierCode`, `supplierName`, `itemCodes[]`, `fundingType`, `ratePerUnit` / `amount`, `fundedCap`, `periodFrom`, `periodTo`, `channels[]`, `status`, `evidenceRef`, `authorisedContact`
- **Sensitivity:** Commercially sensitive — fictional
- **Simulation:** Fixture with `CONFIRMED`, `AGREED_PENDING_EVIDENCE`, `EXPIRED` and off-invoice records; verification returns deterministic outcomes for the demo document
- **Future integration:** SharePoint list / Dataverse read; verification remains a Finance action

### 2.7 Authority Directory (Delegation of Authority register + HR org data)

- **Owner:** Commercial Director's office with HR
- **Purpose:** Who holds which approval role for which category and band; standing and absence delegations with validity windows; availability.
- **Operations:** Resolve approver, reviewer and informed parties for BU, category, band, requester and expected decision date; get delegations.
- **Key fields:** `role`, `employeeId`, `name`, `title`, `categoryScope[]`, `bandScope[]`, `delegations[{delegateId, from, to, reason, ref}]`, `unavailability[{from, to}]`
- **Sensitivity:** Personal data — **fictional people only**
- **Simulation:** Fixture with the current role-holders and the October absences
- **Future integration:** Entra ID groups plus a Dataverse DoA table

### 2.8 Compliance Register

- **Owner:** Compliance & Regulatory
- **Purpose:** Regulatory class rules (mirrors Guideline §9); open and closed Compliance reviews.
- **Operations:** Get restrictions by regulatory class; create review; get review status.
- **Simulation:** Fixture mapping plus simulated review tasks

### 2.9 Approval & Notification Hub (Teams / Outlook)

- **Owner:** Group IT M365
- **Purpose:** Deliver approval tasks to named people; capture decisions; send FYI notifications and reminders.
- **Operations:** Create task; get task; record decision; send notification.
- **Simulation:** In-demo "inbox" panel where the presenter acts as the approver; every action labelled simulated
- **Future integration:** Teams Approvals / Adaptive Cards via Power Automate or Graph

## 3. Representative data for simulation

The BU has provided fictional but realistic items, prices, costs, stock, promotions, funding records and people so that the simulated systems produce internally consistent results. All values are invented for the demonstration and carry no relationship to real trading data.

## 4. Simulation requirements

1. Every simulated response carries `meta.simulated = true`, the simulated source system name and a fixture version, and the user interface labels it `SIMULATED`.
2. Responses are deterministic for the same inputs so repeated demo runs give the same results.
3. Fault injection is available (for example, ERP cost timeout) to show that the platform pauses and asks rather than estimating.
4. The platform may propose interface shapes from this intake, but the contract and example responses are reviewed by DataLab and Pricing Ops before use. No mock result is synthesised on the fly during a case.
5. Nothing in the simulation writes to any live system.

## 5. Terminology the platform should learn

| Term used by the team | Formal name | Note |
|---|---|---|
| PromoHub | Promotion Management System | Same system |
| Item Master | Product Master (PIM/MDM) | Same system |
| Register | Trade Funding Register | Finance's list |
| Hero SKU / Strategic SKU | Product Master `strategicFlag = HERO` | Trading maintains the flag |
| Cut-off | Approval deadline for an execution route | Per calendar |
| Band | Approval band under the DoA | A–D |
