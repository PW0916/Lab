# Supplier Trade Funding Procedure

| | |
|---|---|
| **Document ID** | WTCHK-FIN-PRC-006 |
| **Version** | 1.3 |
| **Effective date** | 1 March 2026 |
| **Document owner** | Finance Controller, Commercial |
| **Applies to** | Category Management, Trade Marketing, Commercial Finance, Accounts Receivable |
| **Classification** | Internal — **fictional demonstration content** |

---

## 1. Purpose

This procedure defines how supplier trade funding for promotions is negotiated, recorded, evidenced, recognised in promotion approvals, claimed and audited. Its objective is that no promotion is approved on the strength of funding that the supplier has not committed in writing.

## 2. Funding types

| Type | Register code | Description | Effect on promotion economics |
|---|---|---|---|
| Scan-back | `SCAN_BACK` | Supplier pays a fixed amount per unit sold during the promotion, claimed from scan data | Recognised funding per unit |
| Lump sum | `LUMP_SUM` | Fixed contribution to a named promotion or period | Converted to per unit over forecast units (Margin Policy §5.4) |
| Off-invoice | `OFF_INVOICE` | Reduced purchase price on POs during a period | Reduces effective unit cost (Margin Policy §5.5) |
| Free goods | `FREE_GOODS` | Additional units supplied free | Not recognised for approval |
| Co-op marketing | `COOP_MEDIA` | Contribution to leaflet, digital or in-store media | Not recognised in promotion economics; recorded for marketing budget |

## 3. Negotiation and recording

1. The Category Lead or Category Manager negotiates funding within the Joint Business Plan (JBP) envelope for the supplier.
2. Every agreed funding item is recorded in the **Trade Funding Register** within two working days of agreement, with: supplier code, item code(s), funding type, rate or amount, maximum funded quantity (if any), covered period, covered channels, requesting promotion or event, and the supplier contact who agreed.
3. On creation the record has status `DRAFT`. When the supplier has agreed by email but has not yet issued a confirmation letter, the status is `AGREED_PENDING_EVIDENCE`.

## 4. Confirmation evidence

### 4.1 Requirements

A funding commitment moves to `CONFIRMED` only when a confirmation document is filed against the register record that:

- is issued on the supplier's letterhead or from a supplier corporate email domain by an **authorised supplier contact** (listed in the supplier master as authorised to commit funding);
- identifies the **supplier**, **WTCHK**, and a **funding reference**;
- lists the **item code(s)** covered (WTCHK item codes or supplier article numbers with a mapping);
- states the **funding type, rate or amount**, and any **maximum funded quantity**;
- states the **covered period** (start and end dates) and **covered channels**;
- states the **claim mechanism** (scan data, invoice deduction, credit note);
- is **dated and signed** (or carries a verifiable e-signature or email header).

### 4.2 Verification

Commercial Finance verifies the document against the register record and marks the outcome `VERIFIED` or `REJECTED` with reasons (for example, item not listed, period does not cover the promotion, contact not authorised). Verification is recorded with the verifier's name and date. The register status becomes `CONFIRMED` only on `VERIFIED`.

### 4.3 Coverage checks at approval

When a promotion request claims funding, the check compares the register record with the request: item, period, channels and forecast against cap. Outcomes are reported as `FULL`, `PARTIAL_PERIOD`, `PARTIAL_CHANNEL`, `CAP_BELOW_FORECAST`, `NOT_COVERED`. Only `FULL` (with cap proration where applicable) is recognised; other outcomes are reported to the requester with the specific gap so an amended confirmation can be sought.

## 5. Statuses

| Status | Meaning | Recognised for approval |
|---|---|---|
| `DRAFT` | Recorded, not yet agreed | No |
| `AGREED_PENDING_EVIDENCE` | Agreed informally; confirmation document not filed | No |
| `CONFIRMED` | Confirmation document filed and verified | Yes, subject to coverage |
| `EXPIRED` | Covered period has ended, or confirmation validity has lapsed | No |
| `CLAIMED` | Claim raised on supplier after the promotion | No (historic) |
| `CANCELLED` | Withdrawn by supplier or WTCHK | No |

## 6. Claims and accrual

- Scan-back and lump-sum funding are accrued at promotion end based on actual units and claimed within 30 days by Accounts Receivable, using scan data from the Data Warehouse.
- Off-invoice funding requires no claim; Commercial Finance reconciles PO prices to the register.
- Claims that differ from the recognised amount by more than 10% are reported to the Finance Controller with reasons.

## 7. Controls and audit

- The register is reconciled monthly to the general ledger accrual.
- No register record may be moved to `CONFIRMED` by the person who negotiated it.
- Confirmation documents are retained for seven years with the register record.
- Internal Audit samples confirmed commitments each half-year for compliance with section 4.

## 8. Confirmation letter template (summary)

Supplier letterhead · Date · Funding reference · Addressee: Watsons Hong Kong, Commercial Finance · Item table (WTCHK item code, description, funding type, rate/amount, cap) · Covered period · Covered channels · Claim mechanism · Conditions · Authorised contact name, title, signature · Supplier company chop (optional).

## 9. Revision history

| Version | Date | Change |
|---|---|---|
| 1.1 | 1 July 2024 | Added `AGREED_PENDING_EVIDENCE` status |
| 1.2 | 1 April 2025 | Added coverage outcomes (§4.3) |
| **1.3** | **1 March 2026** | **Added authorised supplier contact requirement; added `COOP_MEDIA`; clarified off-invoice treatment** |
