# Breadboarding Adapter Kit

SMD to DIP adapter boards for breadboard prototyping with surface-mount components

---

## Summary

- **Total component types**: 9
- **Total quantity**:
  - **Minimal kit**: 13-19 pieces (single-project breadboarding)
  - **Full library**: 46-88 pieces (permanent adapter collection)
- **Estimated total cost**:
  - **Minimal kit**: ~$5-9 (budget) or ~$38-54 (premium SchmartBoard)
  - **Full library**: ~$18-30 (budget) or ~$128-249 (premium SchmartBoard)
- **Use case**: Enable breadboard prototyping with SMD components
- **Primary sources**: AliExpress, eBay, Amazon (budget) | Digikey, Mouser (premium SchmartBoard)

---

## Core Adapter List

| # | Adapter Type | Package Converts | Pin Count | Use For | Qty | Unit Price (Budget) | Unit Price (Premium) | Extended (Budget) | Extended (Premium) | Notes |
| --- | ------------- | ---------------- | --------- | ------- | --- | ------------------- | ------------------- | ----------------- | ----------------- | ----- |
| 1 | SOT-23 to DIP | SOT-23-3 → 0.1" DIP | 3-pin | MOSFETs, BJTs, small regulators | 10-20 | $0.20-0.50 | $2.50 | $3-5 | $25-50 | Most common adapter |
| 2 | SOT-23-6 to DIP | SOT-23-6 → 0.1" DIP | 6-pin | Buck converters (LMR51430) | 3-5 | $0.30-0.80 | $3.00 | $2-3 | $9-15 | Critical for switching regulators |
| 3 | SOT-223 to DIP | SOT-223 → 0.1" DIP | 4-pin | LDO regulators (AMS1117) | 5-10 | $0.30-0.60 | $3.50 | $2-3 | $18-35 | Voltage regulators |
| 4 | TQFP-44 to DIP | TQFP-44 (0.8mm) → 0.1" DIP | 44-pin | PIC18F46K22-I/PT | 2-3 | $0.50-1.50 | $4-7 | $1-3 | $8-21 | Fine pitch (0.8mm) |
| 5 | SOIC-14 to DIP-14 | SOIC-14 → DIP-14 | 14-pin | Logic ICs (74HC14D) | 3-5 | $0.40-0.80 | $3.50 | $2-3 | $11-18 | Logic IC adapters |
| 6 | SOD-323 to DIP | SOD-323 → 0.1" DIP | 2-pin | Signal diodes, Zeners | 10-20 | $0.20-0.40 | $2.00 | $2-3 | $20-40 | Small signal diodes |
| 7 | SMA to DIP | SMA → 0.1" DIP | 2-pin | Schottky diodes (SS14, SS34) | 5-10 | $0.20-0.40 | $2.50 | $2-3 | $13-25 | Power diodes |
| 8 | 0805 Component Strips | 0805 → 0.1" DIP | Dual/Quad | Resistors, capacitors | 5-10 | $0.30-0.60 | $3.00 | $2-3 | $15-30 | 2-4 components per strip |
| 9 | 1206 Component Strips | 1206 → 0.1" DIP | Dual/Quad | High-power resistors | 3-5 | $0.30-0.60 | $3.00 | $2-3 | $9-15 | 1/4W resistors |

**TOTAL: 46-88 adapters, $18-30 (budget) or $128-249 (premium)**

---

## Component Categories

### Active Component Adapters (Priority 1)

**SOT-23 Family (3 types, 18-35 total):**

- **SOT-23 (3-pin)** - 10-20 pcs
  - AO3400A, SI2302, IRLML6244 (N-MOSFETs)
  - AO3401A (P-MOSFET)
  - MMBT3904, MMBT3906 (BJTs)
  - Small linear regulators

- **SOT-23-6 (6-pin)** - 3-5 pcs
  - LMR51430 buck converter
  - Other 6-pin switching regulators
  - Op-amps in SOT-23-6

- **SOT-223 (4-pin)** - 5-10 pcs
  - AMS1117-3.3, AMS1117-5.0 (LDOs)
  - LM317 SOT-223 variant

**Use:** Transistor/regulator testing on breadboard

### Microcontroller Adapters (Priority 2)

**TQFP Adapters (1 type, 2-3 total):**

- **TQFP-44 (0.8mm pitch)** - 2-3 pcs
  - PIC18F46K22-I/PT microcontroller
  - Other 44-pin TQFP devices
  - Requires fine-pitch soldering skills

**Use:** MCU prototyping and testing

### Logic IC Adapters (Priority 2)

**SOIC Adapters (1 type, 3-5 total):**

- **SOIC-14 to DIP-14** - 3-5 pcs
  - 74HC14D Schmitt trigger
  - Other 14-pin SOIC logic ICs
  - Op-amps in SOIC-8 (if ordered later)

**Use:** Logic IC breadboard integration

### Diode Adapters (Priority 3)

**Small Signal Diodes (2 types, 15-30 total):**

- **SOD-323** - 10-20 pcs
  - 1N4148WS signal diodes
  - B5819WS Schottky diodes
  - MM3Z series Zener diodes (3.3V, 5.1V, 12V)
  - DESD5V0U1BA TVS diodes

- **SMA** - 5-10 pcs
  - SS14, SS34 Schottky diodes

**Use:** Protection circuits, signal diodes on breadboard

### Passive Component Adapters (Priority 4)

**Resistor/Capacitor Strips (2 types, 8-15 total):**

- **0805 Dual/Quad strips** - 5-10 pcs
  - 0805 resistors (main kit: 163 values)
  - 0805 capacitors (C0G/NP0, X7R)
  - Quick R/C network prototyping

- **1206 Dual/Quad strips** - 3-5 pcs
  - 1206 1/4W resistors
  - Higher power applications

**Use:** Quick passive component testing (lower priority since through-hole alternatives available)

---

## Sourcing Strategy

### Budget Approach (Recommended)

**Source:** AliExpress, eBay, Amazon

**Advantages:**

- Low cost ($0.20-0.80 per adapter)
- Bulk quantities available
- Total kit cost: ~$18-30

**Disadvantages:**

- Requires SMD soldering skills
- No pre-tinning or grooved pads
- Shipping time (2-4 weeks from AliExpress)

**Search Terms:**

- "SOT-23 to DIP adapter PCB"
- "SMD to DIP adapter kit"
- "TQFP-44 breakout board"
- "SOT-223 adapter"

### Premium Approach (SchmartBoard)

**Source:** Digikey, Mouser, SparkFun

**SchmartBoard Part Numbers:**

- SOT-23-3: SchmartBoard 201-0006-01
- SOT-223: SchmartBoard 201-0013-01
- TQFP-44: SchmartBoard 201-0007-01
- SOIC-14: SchmartBoard 201-0015-01

**Advantages:**

- Pre-tinned grooved pads
- Easy hand soldering (no hot air needed)
- Fast shipping (1-2 days)
- Professional quality

**Disadvantages:**

- Expensive ($2.50-7.00 per adapter)
- Total kit cost: ~$128-249

### Hybrid Approach (Best Value)

**Premium (SchmartBoard) for difficult packages:**

- TQFP-44 (fine pitch, worth the premium)
- SOT-23-6 (buck converter critical components)

**Budget (Generic) for simple packages:**

- SOT-23-3 (easy to solder)
- SOT-223 (larger pads)
- SOD-323, SMA diodes

**Estimated cost:** ~$25-40

---

## Priority Ordering

### Phase 1: Essential Active Components (Order First)

| Adapter | Qty | Priority | Justification |
| ------- | --- | -------- | ------------- |
| SOT-23 (3-pin) | 10-15 | **HIGH** | Most common package, enables all transistor/MOSFET testing |
| SOT-223 | 5 | **HIGH** | Voltage regulators needed for every project |
| SOT-23-6 | 3-5 | **MEDIUM** | Buck converters (but can use LDOs for breadboarding) |

**Cost:** ~$5-10 (budget) or ~$15-30 (premium)

### Phase 2: Complex Components (Order Second)

| Adapter | Qty | Priority | Justification |
| ------- | --- | -------- | ------------- |
| TQFP-44 | 2-3 | **MEDIUM** | Only need for 2 PIC chips in stock |
| SOIC-14 | 3-5 | **LOW** | Consider ordering 74HC14 in DIP-14 instead |

**Cost:** ~$3-6 (budget) or ~$20-40 (premium)

### Phase 3: Diodes & Passives (Optional)

| Adapter | Qty | Priority | Justification |
| ------- | --- | -------- | ------------- |
| SOD-323 | 10-20 | **LOW** | Nice to have, but many through-hole diode alternatives exist |
| SMA | 5-10 | **LOW** | Can wire SMD diodes with leads for testing |
| 0805/1206 strips | 5-10 | **VERY LOW** | You have extensive through-hole R/C inventory |

**Cost:** ~$6-12 (budget) or ~$45-90 (premium)

---

## Alternative Strategy: Order Through-Hole Equivalents

Before buying adapters, consider ordering DIP versions of components:

| SMD Component (Needs Adapter) | Through-Hole Alternative | In Stock? |
| ----------------------------- | ------------------------ | --------- |
| MMBT3904/3906 (SOT-23) | 2N3904/2N3906 (TO-92) | ✅ **Yes** |
| AO3400A (SOT-23) | 2N7000 (TO-92) | ✅ **Yes** (lower current) |
| AMS1117 (SOT-223) | LM317T (TO-220) | ✅ **Yes** (adjustable) |
| 74HC14D (SOIC-14) | 74HC14 (DIP-14) | ❌ No - **consider ordering** |
| PIC18F46K22-I/PT (TQFP-44) | PIC18F46K22-I/P (DIP-40) | ❌ No - **consider ordering** |

**Recommendation:** You already have many through-hole alternatives! Focus adapters on SMD-only components.

---

## Buck Converter Special Considerations

### Why Buck Converters Need Special Attention

The **LMR51430 (SOT-23-6)** buck converter is challenging on breadboards:

**Issues:**

- High-frequency switching (400kHz-2.2MHz)
- Breadboard parasitic capacitance/inductance
- Long jumper wires cause EMI and instability
- Requires close-coupled capacitors

**Solutions:**

1. **SOT-23-6 Adapter + Breadboard** (Quick Testing)
   - Use adapter with short wires
   - Keep input/output caps very close
   - Expect some noise/instability

2. **Dedicated Buck Module** (Recommended)
   - Build complete circuit on proto board
   - Include all support components
   - Add pin headers for I/O
   - Reusable and reliable

3. **Use LDO for Breadboard** (Simplest)
   - AMS1117-3.3/5.0 on SOT-223 adapter
   - Less efficient but breadboard-friendly
   - Reserve buck converters for PCBs

---

## Integration with Your Inventory

### Components That Will Use These Adapters

**From Current Inventory (SMD):**

- 5× LMR51430 buck converters (SOT-23-6)
- 2× PIC18F46K22-I/PT microcontrollers (TQFP-44)
- 4 SMD resistor values (0805)
- 3 SMD capacitor values

**From Planned Orders (SMD Kits):**

- 163× 0805 resistors (1% tolerance kit)
- 68× 0805/1206 capacitors (mixed kit)
- 50× SS14/SS34 Schottky diodes (SMA)
- 130× 1N4148WS, B5819WS diodes (SOD-323)
- 70× MOSFETs (SOT-23): AO3400A, SI2302, IRLML6244, AO3401A
- 60× BJTs (SOT-23): MMBT3904, MMBT3906
- 20× LDO regulators (SOT-223): AMS1117-3.3, AMS1117-5.0
- 5× 74HC14D logic ICs (SOIC-14)
- 125× Zener/TVS diodes (SOD-323): MM3Z series, DESD5V0U1BA

**Total SMD Components:** ~650+ pieces across 315+ unique values

---

## Minimal Starter Kit (Single-Project Breadboarding)

For **one breadboard project at a time** with reusable adapters:

| Adapter Type | Minimal Qty | Budget Cost | Premium Cost | Reasoning |
| --- | --- | --- | --- | --- |
| SOT-23 (3-pin) | 3-4 | $1-2 | $8-10 | 2-3 MOSFETs/transistors per project, 1 spare |
| SOT-223 | 2 | $1 | $7 | 1-2 voltage regulators per project |
| SOT-23-6 | 1 | $0.50 | $3 | Only 1 buck converter at a time |
| TQFP-44 | 1 | $1 | $5 | Only 1 microcontroller per project |
| SOIC-14 | 1-2 | $0.50-1 | $4-7 | 1 logic IC, maybe 2 max |
| SOD-323 | 3-4 | $1 | $6-8 | A few signal/Zener diodes |
| SMA | 2-3 | $0.50-1 | $5-8 | Couple Schottky flyback diodes |
| 0805 strips | 0-2 | $0-1 | $0-6 | **Skip** - you have through-hole alternatives |
| 1206 strips | 0 | $0 | $0 | **Skip** - you have through-hole alternatives |
| **TOTAL** | **13-19** | **$5-9** | **$38-54** | |

### Trade-offs: Minimal vs. Library Approach

**Minimal Approach (13-19 adapters):**

- ✅ Lower cost ($5-9 budget, $38-54 premium)
- ✅ Less storage space needed
- ✅ Good for testing SMD components before committing to PCB
- ❌ Requires desoldering/resoldering when switching components
- ❌ SMD soldering/desoldering is tedious and risks damaging pads
- ❌ Can only work on one project at a time

**Library Approach (46-88 adapters from Core List):**

- ✅ Common components stay permanently mounted
- ✅ No desoldering - grab the adapter you need
- ✅ Can keep multiple breadboard projects assembled
- ✅ Faster prototyping iteration
- ❌ Higher cost ($18-30 budget, $128-249 premium)
- ❌ More storage space needed

### Expansion Strategy

**Start minimal, then expand based on usage:**

1. **Order minimal set first** (13-19 adapters above)
2. **After 2-3 projects, identify common components** you use repeatedly
3. **Add dedicated adapters** for those common components:
   - If you always use AO3400A MOSFETs, add 2-3 permanent adapters
   - If you prototype with AMS1117-3.3 often, add 1-2 permanent adapters
4. **Expand to library approach** only if you:
   - Work on multiple projects simultaneously
   - Constantly desolder the same components
   - Want to keep breadboard prototypes intact

---

## Recommended Initial Order

**Starter Kit (Budget-Friendly):**

| Adapter | Qty | Source | Est. Cost |
| ------- | --- | ------ | --------- |
| SOT-23 (3-pin) | 10 | AliExpress | $3-5 |
| SOT-223 | 5 | AliExpress | $2-3 |
| SOT-23-6 | 3 | AliExpress | $2-3 |
| TQFP-44 | 2 | AliExpress | $1-3 |
| **TOTAL** | **20** | | **$8-14** |

This covers 90% of your SMD component needs for breadboarding.

---

## Storage & Organization

**Recommended storage:**

- Keep unused adapters in anti-static bags
- Label pre-soldered adapters clearly (e.g., "AO3400A on SOT-23 adapter")
- Store in small compartment boxes
- Consider dedicating some adapters permanently to common components

**Labeling suggestions:**

- "SOT-23 Adapters - Blank (10 pcs)"
- "SOT-223 Adapters - Blank (5 pcs)"
- "LMR51430 Buck Module (assembled)"
- "PIC18F46K22 TQFP-44 (assembled)"

---

## Notes

- **Soldering required:** All adapters require SMD soldering skills
- **Reusability:** Can desolder and reuse adapters, but tedious
- **Alternative:** Keep one adapter per common component permanently soldered
- **For production:** Always use SMD components directly on PCBs (smaller, better performance)
- **For prototyping:** Adapters enable testing before committing to PCB design
- **Learning tool:** Good practice for SMD soldering on forgiving, cheap PCBs

---

## Future Expansion

**If you add more SMD packages later:**

- SOIC-8 adapters (for op-amps, other 8-pin ICs)
- QFN adapters (for modern high-density ICs)
- MSOP/TSSOP adapters (for analog ICs)
- DO-214AA (SMB) adapters (for SMBJ15A TVS diodes)
