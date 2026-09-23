# Supplier Funding Confirmation Letter (uploaded during Scenario B)

> **Fictional document** — Glow Beauty Laboratories (HK) Limited is an invented supplier for demonstration purposes.

---

**GLOW BEAUTY LABORATORIES (HK) LIMITED**
Unit 1801, 18/F, Tower B, Kowloon Bay Business Centre, Kowloon Bay, Hong Kong
Tel +852 2xxx xxxx · trade@glowbeauty-labs.example

Date: **29 September 2026**
Our reference: **GBL/TF/2026/0917**
Your reference: **FC-2026-041**

To: Commercial Finance, Watsons Hong Kong
cc: Samantha Yip, Category Lead — Skincare

**Subject: Trade funding confirmation — Glow Radiance Serum 30ml, Cycles C22–C24 2026**

Dear Sir / Madam,

We confirm the following trade funding for Watsons Hong Kong:

| WTCHK item code | Supplier article | Description | Funding type | Rate | Maximum funded quantity |
|---|---|---|---|---|---|
| GLW-SRM-30ML | GB-1140-030 | Glow Radiance Serum 30ml | Scan-back (per unit sold) | HK$12.00 | 2,000 units |

**Covered period:** 1 October 2026 to 30 November 2026 (inclusive)
**Covered channels:** Watsons Hong Kong physical stores (all formats). This confirmation does not cover watsons.com.hk, the Watsons app or third-party marketplaces.
**Claim mechanism:** Watsons HK to provide scan data within 30 days of promotion end; Glow Beauty will issue a credit note against the next invoice.
**Conditions:** Funding applies to promotions at or above HK$129 selling price. Funding is not payable on units sold through clearance.

This confirmation supersedes our email of 17 September 2026.

Yours faithfully,

*(signed)*

**Cheryl Kwan**
Key Account Director, Watsons Group
Glow Beauty Laboratories (HK) Limited
cheryl.kwan@glowbeauty-labs.example

*Company chop affixed*

---

## Expected verification outcome (demo)

| Check | Result |
|---|---|
| Authorised contact | Cheryl Kwan is listed as authorised for supplier `S-GLW-114` → pass |
| Funding reference matches register | FC-2026-041 → pass |
| Item covered | GLW-SRM-30ML → pass |
| Funding type, rate, cap | SCAN_BACK, HK$12.00, cap 2,000 → matches register |
| Period covers promotion (22 Oct–4 Nov 2026) | 1 Oct–30 Nov → **FULL** |
| Channels cover promotion (STORE only in the request) | STORE → **FULL**. If ESHOP were requested, outcome would be `PARTIAL_CHANNEL` |
| Price condition (≥ HK$129) | Requested HK$139 → pass |
| Cap vs forecast | Cap 2,000 vs forecast 1,800 → no proration |
| Register status after verification | `AGREED_PENDING_EVIDENCE` → `CONFIRMED` (verifier: Finance Controller, simulated) |
