# Promotion Setup and Go-Live Checklist

| | |
|---|---|
| **Document ID** | WTCHK-OPS-CHK-010 |
| **Version** | 1.0 |
| **Effective date** | 1 September 2026 |
| **Document owner** | Pricing & Promotion Operations Lead |
| **Applies to** | Pricing & Promotion Operations, Marketing (Leaflet & Digital), Store Operations, eCommerce Operations |
| **Classification** | Internal — **fictional demonstration content** |

---

## 1. Purpose

This checklist is used by Pricing & Promotion Operations ("Pricing Ops") to confirm that an approved promotion can be set up correctly in PromoHub, released to POS and eShop, and executed in stores on the go-live date. It also defines the feasibility checks Pricing Ops performs **before** business approval so that unworkable requests are not approved.

## 2. Pre-approval feasibility check

Pricing Ops confirms the following for every request before it reaches the approver. A failed check returns the request for revision with the reason.

| # | Check | Pass condition | Data source |
|---|---|---|---|
| 2.1 | Item exists and is active | Item code found; lifecycle `ACTIVE`, `NEW`, or `PHASE_OUT` with delist date after promotion end | Product Master |
| 2.2 | Barcode active | Primary barcode status `ACTIVE` | Product Master |
| 2.3 | Mechanic supported for channel | Mechanic listed in SOP Appendix B for each requested channel | SOP Appendix B / PromoHub mechanic list |
| 2.4 | Price zone identified | `HK-STD` or `HK-AIRPORT`; airport stores excluded from `HK-ALL` unless stated | ERP |
| 2.5 | Store scope valid | Scope code exists in Store Network and contains at least one open store on the start date | Store Network |
| 2.6 | Event code valid (Event type) | Event code exists in PromoHub for the dates | PromoHub |
| 2.7 | Dates and times | Start 00:00 HKT on a cycle start (Standard/Local) or explicit times (Flash); end 23:59 HKT | Calendar |
| 2.8 | Lead time | Approval expected before the cut-off for the execution route | Calendar |
| 2.9 | Loyalty configuration (Member mechanics) | Loyalty team confirmation reference present | Loyalty team |
| 2.10 | Gift SKU (GWP) | Gift item code exists and stock allocated | Product Master / Stock |
| 2.11 | No duplicate draft | No existing PromoHub draft for the same case reference | PromoHub |

## 3. Post-approval setup timeline

Days are calendar days before the promotion start date (T).

| When | Action | Owner | Evidence recorded on case |
|---|---|---|---|
| T-10 (or within 1 working day of approval if later) | Create promotion draft in PromoHub with approved terms; attach case reference and decision pack ID | Pricing Ops | PromoHub draft ID |
| T-10 | Run PromoHub validation (item, price, dates, scope, mechanic, conflicts) | Pricing Ops | Validation result |
| T-9 | Confirm draft matches approved case (price, dates, scope, mechanic, item list) — four-eyes check | Pricing Ops (second person) | Reviewer name |
| T-7 | Shelf-talker / POS material print order | Marketing | Print order ref |
| T-5 | Store bulletin published (in-store promotions) | Store Operations | Bulletin ref |
| T-3 | eShop / App promotion configured and previewed | eCommerce Ops | Preview link |
| T-3 | Compliance and Supply Chain gates closed (if opened) | Pricing Ops confirms | Gate task IDs |
| T-2 | Price file released to POS; PromoHub status `RELEASED` | Pricing Ops | Release ref |
| T-1 | POS test transaction in two pilot stores; eShop test order | Pricing Ops / eCommerce Ops | Test refs |
| T (go-live, by 09:00 HKT) | Go-live check: price displayed and scanning correctly in sample stores and online | Pricing Ops | Go-live check result |
| T+1 | Variance report (any store or channel not executing) | Pricing Ops | Variance report |

## 4. Release control

- No promotion is released to POS or eShop without an approved case reference and a `RELEASED` PromoHub status.
- A promotion with an open Compliance or Supply Chain gate may be drafted and validated but not released.
- Any change to approved terms after approval requires re-approval at the original band or higher.

## 5. Go-live day and rollback

- If a price is scanning incorrectly, Pricing Ops issues a corrective price file within two hours and notifies Store Operations.
- If a promotion must be withdrawn after go-live (regulatory, supplier, stock), the Head of Trading approves the withdrawal; Pricing Ops rolls back the price file and Store Operations issues a bulletin. Customers charged the promotional price before rollback are not affected.

## 6. Data handling

Pricing Ops uses only ERP and Product Master data for setup. Data from a test, training or simulation environment may not be used to create a live promotion. Any test draft must be labelled `TEST` in its description and deleted within 30 days.

## 7. Revision history

| Version | Date | Change |
|---|---|---|
| **1.0** | **1 September 2026** | **Initial issue, consolidating the Pricing Ops working checklist** |
