# SMD Kit Recommendations

## Overview

Based on the gap analysis of your current inventory, this document provides component recommendations with LCSC pricing. These components fill critical gaps for your dual-rail MCU projects (12V/24V + 3.3V/5V).

**Pricing Date:** January 2026
**Source:** LCSC Electronics

---

## Priority 1: Critical Gaps (HIGH)

### 1.1 SMD Schottky Diodes

**Use Case:** Flyback protection on inductive loads (motors, solenoids, pumps)
**Current Inventory:** NONE

| Part | Package | Specs | LCSC Code | Manufacturer | Price (each) | Rec. Qty |
|------|---------|-------|-----------|--------------|--------------|----------|
| **SS14** | SMA (DO-214AC) | 40V 1A | C2837270 | JSMSEMI | $0.011 | 50 |
| SS14 | SMA | 40V 1A | C2480 | MDD | $0.016 | - |
| **SS34** | SMA (DO-214AC) | 40V 3A | C2837271 | JSMSEMI | $0.021 | 30 |
| SS34 | SMA | 40V 3A | C8678 | MDD | $0.029 | - |
| **B5819WS** | SOD-323 | 40V 1A | C916992 | JSMSEMI | $0.012 | 50 |
| B5819WS | SOD-323 | 40V 1A | C64886 | MDD | $0.020 | - |

**Recommendation:**
- SS14 (C2837270): 50 pcs @ $0.55 - General purpose, good for 12V circuits
- SS34 (C2837271): 30 pcs @ $0.63 - Higher current for motor flyback
- B5819WS (C916992): 50 pcs @ $0.60 - Small footprint for tight layouts

**Total: ~$1.78**

---

### 1.2 N-Channel MOSFETs (Logic-Level)

**Use Case:** Low-side switching for 12V/24V loads
**Current Inventory:** Only IRLML0030TRPBF (30V/5.3A)

| Part | Package | Vds | Id | Rds(on) | LCSC Code | Manufacturer | Price | Rec. Qty |
|------|---------|-----|----|---------|-----------| -------------|-------|----------|
| **AO3400A** | SOT-23 | 30V | 5.7A | 26mΩ | C5224194 | ElecSuper | $0.024 | 20 |
| AO3400A | SOT-23 | 30V | 5.7A | 26mΩ | C20917 | AOS (orig) | $0.079 | - |
| **SI2302** | SOT-23 | 20V | 2.6A | 50mΩ | C2891732 | YONGYUTAI | $0.011 | 20 |
| SI2302 | SOT-23 | 20V | 2.6A | 50mΩ | C5224179 | ElecSuper | $0.014 | - |
| **IRLML6244** | SOT-23 | 20V | 6.3A | 21mΩ | C5438459 | KUU | $0.020 | 15 |
| IRLML6244 | SOT-23 | 20V | 6.3A | 21mΩ | C143946 | Infineon | $0.109 | - |

**Recommendation:**
- AO3400A (C5224194): 20 pcs @ $0.48 - Best general purpose, 30V rating
- SI2302 (C2891732): 20 pcs @ $0.22 - Low Vgs threshold, excellent for 3.3V MCU drive
- IRLML6244 (C5438459): 15 pcs @ $0.30 - Lowest Rds(on), highest current

**Total: ~$1.00**

---

## Priority 2: Medium Gaps

### 2.1 Fixed LDO Voltage Regulators

**Use Case:** Simple 3.3V/5V power rails without adjustable feedback
**Current Inventory:** LM317EMP (adjustable only)

| Part | Output | Package | Iout | LCSC Code | Manufacturer | Price | Rec. Qty |
|------|--------|---------|------|-----------|--------------|-------|----------|
| **AMS1117-3.3** | 3.3V | SOT-223 | 1A | C347222 | UMW | $0.036 | 10 |
| AMS1117-3.3 | 3.3V | SOT-223 | 1A | C426566 | Slkor | $0.035 | - |
| AMS1117-3.3 | 3.3V | SOT-223 | 1A | C6186 | AMS (orig) | $0.178 | - |
| **AMS1117-5.0** | 5V | SOT-223 | 1A | C18212701 | TECH PUBLIC | $0.033 | 10 |
| AMS1117-5.0 | 5V | SOT-223 | 1A | C6068482 | GOODWORK | $0.030 | - |
| AMS1117-5.0 | 5V | SOT-223 | 1A | C6187 | AMS (orig) | $0.200 | - |

**Recommendation:**
- AMS1117-3.3 (C347222): 10 pcs @ $0.36
- AMS1117-5.0 (C18212701): 10 pcs @ $0.33

**Total: ~$0.69**

---

### 2.2 SMD Signal Diodes

**Use Case:** Fast switching, clamping, logic protection
**Current Inventory:** 1N4148 through-hole only

| Part | Package | Specs | LCSC Code | Manufacturer | Price | Rec. Qty |
|------|---------|-------|-----------|--------------|-------|----------|
| **1N4148WS** | SOD-323 | 75V 150mA | C917117 | JSMSEMI | $0.0052 | 50 |
| 1N4148WS | SOD-323 | 75V 150mA | C5249630 | ElecSuper | $0.0054 | - |
| 1N4148WS | SOD-323 | 75V 150mA | C118873 | onsemi | $0.0403 | - |

**Recommendation:**
- 1N4148WS (C917117): 50 pcs @ $0.26

**Total: ~$0.26**

---

### 2.3 P-Channel MOSFETs

**Use Case:** High-side switching, reverse polarity protection
**Current Inventory:** NONE

| Part | Package | Vds | Id | Rds(on) | LCSC Code | Manufacturer | Price | Rec. Qty |
|------|---------|-----|----|---------|-----------| -------------|-------|----------|
| **AO3401A** | SOT-23 | -30V | -4A | 44mΩ | C2938368 | GOODWORK | $0.029 | 15 |
| AO3401A | SOT-23 | -30V | -4A | 44mΩ | C347476 | UMW | $0.030 | - |

**Recommendation:**
- AO3401A (C2938368): 15 pcs @ $0.44

**Total: ~$0.44**

---

## Priority 3: Lower Priority

### 3.1 SMD BJT Transistors

**Use Case:** General amplification, switching small loads
**Current Inventory:** 2N3904/2N3906 through-hole only

| Part | Type | Package | LCSC Code | Manufacturer | Price | Rec. Qty |
|------|------|---------|-----------|--------------|-------|----------|
| **MMBT3904** | NPN | SOT-23 | C916374 | JSMSEMI | $0.0055 | 30 |
| MMBT3904 | NPN | SOT-23 | C727127 | TWGMC | $0.0056 | - |
| **MMBT3906** | PNP | SOT-23 | C727128 | TWGMC | $0.0045 | 30 |
| MMBT3906 | PNP | SOT-23 | C916375 | JSMSEMI | $0.0062 | - |

**Recommendation:**
- MMBT3904 (C916374): 30 pcs @ $0.17
- MMBT3906 (C727128): 30 pcs @ $0.14

**Total: ~$0.31**

---

## Order Summary

### Recommended LCSC Order

| Priority | Component | LCSC Code | Qty | Unit Price | Total |
|----------|-----------|-----------|-----|------------|-------|
| HIGH | SS14 Schottky | C2837270 | 50 | $0.011 | $0.55 |
| HIGH | SS34 Schottky | C2837271 | 30 | $0.021 | $0.63 |
| HIGH | B5819WS Schottky | C916992 | 50 | $0.012 | $0.60 |
| HIGH | AO3400A N-FET | C5224194 | 20 | $0.024 | $0.48 |
| HIGH | SI2302 N-FET | C2891732 | 20 | $0.011 | $0.22 |
| HIGH | IRLML6244 N-FET | C5438459 | 15 | $0.020 | $0.30 |
| MED | AMS1117-3.3 LDO | C347222 | 10 | $0.036 | $0.36 |
| MED | AMS1117-5.0 LDO | C18212701 | 10 | $0.033 | $0.33 |
| MED | 1N4148WS Signal | C917117 | 50 | $0.005 | $0.26 |
| MED | AO3401A P-FET | C2938368 | 15 | $0.029 | $0.44 |
| LOW | MMBT3904 NPN | C916374 | 30 | $0.006 | $0.17 |
| LOW | MMBT3906 PNP | C727128 | 30 | $0.005 | $0.14 |

### **Estimated Component Total: $4.48**

*Note: LCSC has minimum order quantities and shipping costs will apply. These are per-piece prices at low quantities; bulk pricing may be lower.*

---

## Notes

### Manufacturer Selection
- **JSMSEMI, UMW, TWGMC, ElecSuper**: Chinese manufacturers with good quality/price ratio
- **onsemi, Infineon, AOS**: Original brand manufacturers (higher price, datasheet accuracy)
- For prototyping, generic equivalents work well; for production, consider original brands

### Still Not Covered (From Original Gap Analysis)
- SMD Zener Diodes (MM3Z series) - Have THT versions
- SMD Power Inductors - Have THT axial inductors
- Schmitt Trigger Logic (74LVC1G14) - Have THT 74HC14
- SMD Op-Amps (MCP6002) - Have THT TLV2372
- SMD 555 Timer - Have THT NE555

These can be ordered later if SMD versions become necessary for specific projects.

---

## LCSC BOM File

To create an LCSC BOM file for direct upload:

```bash
uv run python scripts/lcsc_tool.py create-bom-file \
  C2837270:50 C2837271:30 C916992:50 \
  C5224194:20 C2891732:20 C5438459:15 \
  C347222:10 C18212701:10 C917117:50 \
  C2938368:15 C916374:30 C727128:30 \
  -o data/SMD_Kit_Gap_Fill_BOM.csv --lcsc-codes
```
