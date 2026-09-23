# Regulatory and Restricted Category Guidelines for Promotions (Hong Kong)

| | |
|---|---|
| **Document ID** | WTCHK-LEG-GDL-004 |
| **Version** | 1.2 |
| **Effective date** | 1 April 2026 |
| **Document owner** | Compliance & Regulatory Manager, Watsons Hong Kong |
| **Approved by** | Legal Counsel, AS Watson Group (HK) and Commercial Director |
| **Classification** | Internal — **fictional demonstration content.** The regulatory summaries below are simplified for the demonstration and are not legal advice or a statement of actual law. |

---

## 1. Purpose

These guidelines translate Hong Kong consumer protection, pharmacy, health-claim and infant-nutrition requirements into operational rules for promotions. Sections 3 (prohibitions) and 5 (reference prices) are treated as policy under the SOP document hierarchy. Any promotion that engages these guidelines must be screened before commercial checks continue.

## 2. Regulatory context (simplified)

| Area | Operational meaning for promotions |
|---|---|
| **Trade descriptions and pricing claims** | Price comparisons ("was", "save", "% off") must be genuine. A reference price must have been the price actually charged for a meaningful period. "Lowest price" or "cheapest" claims are not permitted without documented market evidence approved by Compliance. |
| **Pharmacy and poisons controls** | Certain medicines may only be sold under pharmacist supervision. Promoting their price to the general public (leaflet, in-store price signage, digital price promotion) is not permitted. |
| **Health and medical claims** | Promotional copy for supplements and devices may not claim to prevent, treat or cure disease. Claims must match the registered or approved product description. |
| **Infant and young-child nutrition** | Marketing practices for infant formula (Stage 1, 0–6 months) and follow-on formula (Stage 2, 6–12 months) are restricted. WTCHK does not run price, value, gift, bundle or loyalty promotions on these products. Growing-up milk (Stage 3+) may be promoted subject to conditions. |
| **Personal data** | Member-targeted promotions must use only permitted data and channels under the Member Rewards privacy notice. |

## 3. Prohibited regulatory classes — no promotion in any mechanic

| Regulatory class (Product Master value) | Description | Rule |
|---|---|---|
| `INFANT_FORMULA_S1` | Infant formula, Stage 1 (0–6 months) | **Prohibited.** No price, value, gift, bundle, member price, bonus points or coupon promotion. No inclusion in any promotional item list. |
| `INFANT_FORMULA_S2` | Follow-on formula, Stage 2 (6–12 months) | **Prohibited**, as above. |
| `PHARMACY_ONLY_P1` | Pharmacy-only medicines sold under pharmacist supervision | **Prohibited** for any public price or value promotion. Professional pharmacy pricing is handled outside this SOP. |
| `PRESCRIPTION` | Prescription-only medicines | **Prohibited.** |
| `TOBACCO` | Tobacco and nicotine products | **Prohibited.** Not ranged; listed for completeness. |

A request containing any item in a prohibited class is stopped at the regulatory screen with outcome `BLOCKED_REGULATORY`. The stop reason must cite this section and the item's regulatory class. The requester may be offered permitted alternatives (for example, items in a permitted class from the same brand or category).

## 4. Restricted regulatory classes — Compliance review required

| Regulatory class | Conditions | Compliance review |
|---|---|---|
| `FORMULA_S3` | Growing-up milk, Stage 3 and above | Permitted for price and value promotions **provided that**: no nutrition or health claims appear in promotional copy beyond the approved product description; the promotion is not bundled with or cross-promoted alongside Stage 1 or 2 products; leaflet placement is not adjacent to Stage 1/2 products. | Mandatory review of copy and placement |
| `HEALTH_SUPPLEMENT` | Vitamins, minerals and supplements | Permitted. Promotional copy limited to approved product descriptions; no disease claims. | Review only if copy includes any functional claim |
| `OTC_GENERAL_SALE` | Medicines on general sale (not pharmacy-only) | Permitted for price promotion. No claims beyond registered indications. Flash promotions not permitted (Margin Policy §3). | Review if copy includes indications |
| `MEDICAL_DEVICE` | Registered or listed medical devices and tests | Permitted. Copy must match listed intended use. | Review of copy |
| `ALCOHOL` | Alcoholic beverages (where ranged) | Permitted for adults; no promotion in App to under-18 segments; no "free alcohol" gifts. | Review of mechanic |
| `COSMETIC_ACTIVE` | Cosmetics with active ingredients (e.g. retinol, high-strength acids) | Permitted. No medicinal claims. | Review if copy includes efficacy claims |

The Compliance review runs in parallel with commercial approval and must be closed before release to setup. Service level: 3 working days.

## 5. Reference prices and comparative claims

### 5.1 Reference price rule

A comparative price claim (for example "Was HK$129", "Save HK$40", "30% off") may be shown only if **both** of the following are true at the promotion start date:

1. The regular price used as the reference has been charged, in the same price zone and channel, for at least **28 consecutive days** within the **90 days** before the promotion start date; and
2. The regular price has **not been increased** in the **14 days** before the promotion start date.

### 5.2 When the rule is not met

The promotion may still proceed with **non-comparative messaging** only — "Special Price HK$45" — with no reference price, saving or percentage displayed in any channel, leaflet or shelf talker. The wording must be reviewed by Compliance before release. The case must record the reason (days at current price, last price change date).

### 5.3 Prohibited claims

"Lowest price", "cheapest in Hong Kong", "best price guaranteed" and similar claims are prohibited unless Compliance has approved documented market evidence within the previous 14 days.

## 6. Promotional wording

- Promotional copy may not attribute disease prevention, treatment or cure to any product.
- Approved product descriptions and claims are held in Product Master (`approvedClaims`). Copy must not extend them.
- "Pharmacist recommended", "doctor recommended" and testimonial-style claims require Compliance approval and evidence.

## 7. Gifts, coupons and bundles

- Gift items must be safe, age-appropriate and, where the qualifying purchase is a regulated product, permitted for that class.
- Coupons must state validity period, channel, exclusions and redemption limit. Coupons may not be applied to prohibited classes.
- Bundles may not combine a prohibited-class item with any other item.

## 8. Compliance review process

1. The case creates a Compliance review task with: items, regulatory classes, mechanic, channels, proposed copy, and the guideline sections engaged.
2. The Compliance & Regulatory Manager (or recorded delegate) reviews within 3 working days and records one of: `APPROVED`, `APPROVED_WITH_WORDING_CHANGES`, `REJECTED`.
3. Wording changes must be applied before setup. Pricing & Promotion Operations may not release a promotion with an open Compliance task.

## 9. Mapping — regulatory class to rule

| Regulatory class | Screen outcome | Comparative claims | Flash allowed | Leaflet allowed |
|---|---|---|---|---|
| `NONE` | Proceed | Subject to §5 | Yes | Yes |
| `HEALTH_SUPPLEMENT` | Proceed; review if claims | Subject to §5 | Yes | Yes |
| `COSMETIC_ACTIVE` | Proceed; review if claims | Subject to §5 | Yes | Yes |
| `OTC_GENERAL_SALE` | Proceed; review if claims | Subject to §5 | No | Yes |
| `MEDICAL_DEVICE` | Proceed; review copy | Subject to §5 | Yes | Yes |
| `FORMULA_S3` | Proceed; mandatory review | Subject to §5 | No | Yes, with placement conditions |
| `ALCOHOL` | Proceed; review mechanic | Subject to §5 | Yes | Yes |
| `INFANT_FORMULA_S1`, `INFANT_FORMULA_S2` | **Blocked** | — | — | — |
| `PHARMACY_ONLY_P1`, `PRESCRIPTION`, `TOBACCO` | **Blocked** | — | — | — |

## 10. Revision history

| Version | Date | Change |
|---|---|---|
| 1.0 | 1 September 2024 | Initial guidelines |
| 1.1 | 1 June 2025 | Added reference price rule (§5) |
| **1.2** | **1 April 2026** | **Added regulatory class mapping (§9); added `COSMETIC_ACTIVE`; clarified Stage 3 conditions** |
