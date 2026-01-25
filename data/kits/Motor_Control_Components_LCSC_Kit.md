# Motor Control & Power Components Kit (LCSC)

Essential power management components for motor/pump/solenoid control projects - LCSC lower MOQ alternative

---

## Summary

- **Total component types**: 14
- **Total quantity**: 180-200 pieces
- **Use case**: Current sensing, overcurrent protection, bulk power filtering for dual-rail MCU projects
- **Estimated total cost**: ~$11-16 components + $10-15 shipping = **$21-31 total**
- **Source**: LCSC (primary)

**Advantages over Digikey:**

- **Much lower MOQs**: 10-50 pieces vs 1000-4000 pieces
- **Lower prices**: 40-65% cheaper than Digikey cut-tape pricing
- **Good stock**: Most components well-stocked

**Trade-offs:**

- Longer shipping: 1-2 weeks vs 2-3 days
- Fewer premium brands
- Bulk caps are through-hole (industry standard for these values)

---

## Component List

| # | Type | Part Number | Manufacturer | Specs | Package | LCSC | Stock | MOQ | Unit Price @ Qty | Qty | Extended |
|---|------|-------------|--------------|-------|---------|------|-------|-----|------------------|-----|----------|
| **Current Sense Resistors (2W, 2512 package) - Budget Tier** | | | | | | | | | | | |
| 1 | Current Sense | FRM252WFR020TN | FOJAN | 0.02Ω 1% 2W ±50ppm/°C | 2512 | C7420049 | 41,840 | 10 | $0.031 @ 10+ | 10 | $0.31 |
| 2 | Current Sense | FRM252WFR050TN | FOJAN | 0.05Ω 1% 2W ±50ppm/°C | 2512 | C7420008 | 9,950 | 10 | $0.046 @ 10+ | 10 | $0.46 |
| 3 | Current Sense | FRM252WFR100TN | FOJAN | 0.1Ω 1% 2W ±50ppm/°C | 2512 | C7420048 | 40,650 | 10 | $0.046 @ 10+ | 10 | $0.46 |
| 4 | Current Sense | YLRY12-2-15F | Yezhan | 0.015Ω 1% 2W | 2512 | C20608729 | 10,860 | 10 | $0.048 @ 10+ | 10 | $0.48 |
| **Current Sense Resistors (1-2W, 2512 package) - Good Tier (UNI-ROYAL)** | | | | | | | | | | | |
| 5 | Current Sense | 25121WF100MT4E | UNI-ROYAL | 0.01Ω 1% 1W ±1500ppm/°C | 2512 | C127692 | 19,160 | 20 | $0.038 @ 20+ | 20 | $0.76 |
| 6 | Current Sense | 25121WF150MT4E | UNI-ROYAL | 0.015Ω 1% 1W ±1500ppm/°C | 2512 | C44883 | 2,530 | 10 | $0.044 @ 10+ | 10 | $0.44 |
| 7 | Current Sense | 25121WF200MT4E | UNI-ROYAL | 0.02Ω 1% 1W ±1000ppm/°C | 2512 | C127705 | 23,780 | 20 | $0.040 @ 20+ | 20 | $0.79 |
| 8 | Current Sense | 25121WF500MT4E | UNI-ROYAL | 0.05Ω 1% 1W ±800ppm/°C | 2512 | C127698 | 33,940 | 20 | $0.038 @ 20+ | 20 | $0.76 |
| 9 | Current Sense | 25121WF100LT4E | UNI-ROYAL | 0.1Ω 1% 1W ±800ppm/°C | 2512 | C25466 | 28,140 | 20 | $0.037 @ 20+ | 20 | $0.73 |
| **Bulk Electrolytic Capacitors (Through-Hole)** | | | | | | | | | | | |
| 10 | Cap Aluminum | (TH) | Econd | 1000µF 25V 3000hrs@105°C | TH D10×L20mm | C46867075 | High | 10 | $0.069 @ 10+ | 10 | $0.69 |
| 11 | Cap Aluminum | (TH alt) | JIERR | 1000µF ±20% 25V 60mΩ@100kHz | TH D10×L20mm | C51953439 | High | 10 | $0.135 @ 10+ | 10 | $1.35 |
| 12 | Cap Aluminum | (TH) | Econd | 2200µF ±20% 35V 30mΩ | TH D13×L25mm | C49332869 | High | 10 | $0.129 @ 10+ | 10 | $1.29 |
| 13 | Cap Aluminum | (TH alt) | JIERR | 2200µF ±20% 35V 28mΩ@100kHz | TH D13×L25mm | C51904469 | High | 10 | $0.338 @ 10+ | 10 | $3.38 |
| **PTC Resettable Fuses** | | | | | | | | | | | |
| 14 | PTC Fuse | SMD1206-100C-16V | BNstar | 1A 16V | 1206 | C2760271 | 22,460 | 10 | $0.030 @ 10+ | 30 | $0.89 |
| 15 | PTC Fuse | MINISMDC200F-2 | Littelfuse | 2A 8V 20mΩ | 1812 | C720175 | 6,805 | 5 | $0.144 @ 5+ | 30 | $4.33 |
| 16 | PTC Fuse | 1812L300/16GR | LUTE | 3A 16V | 1812 | C18198349 | 24,800 | 10 | $0.060 @ 10+ | 30 | $1.81 |

**TOTAL (Budget option - rows 1-4, 10, 12, 14-16): 180 pieces, ~$10.72**
**TOTAL (Good option - rows 5-9, 11, 13, 14-16): 200 pieces, ~$15.24**
**TOTAL (Mixed - rows 1-4, 10, 13, 14-16): 190 pieces, ~$12.81**

---

## Component Details

### Current Sense Resistors (2512 Package)

#### Why These Values?

For motor/pump/solenoid control, current sensing enables:

- **Overcurrent detection**: Detect motor stall or shorts
- **Power monitoring**: Measure actual power consumption
- **Fault protection**: Shut down before damage occurs
- **PWM current control**: Feedback for current-mode control

#### Budget Tier: FOJAN / Yezhan

**FOJAN** - Good quality, excellent price/performance:

- 2W power rating (better than 1W for high current)
- ±50ppm/°C temperature coefficient
- 1% tolerance
- Excellent stock levels
- **Best for**: Hobbyist/prototype projects

**Yezhan** - Budget alternative:

- 2W power rating
- Good availability
- Similar pricing to FOJAN

#### Good Tier: UNI-ROYAL

**UNI-ROYAL** - Reliable brand, widely used:

- 1W power rating (sufficient for most motor applications)
- Better temperature coefficient for 0.05Ω and 0.1Ω (±800ppm/°C)
- Excellent stock across all values
- MOQ 20 pieces (very reasonable)
- **Best for**: Production or when consistency matters

#### Value Selection Guide

| Value | Max Current @ 2W | Typical Use | Voltage Drop @ 5A |
|-------|------------------|-------------|-------------------|
| 0.01Ω | 14.1A | High current motors (>5A) | 50mV |
| 0.015Ω | 11.5A | Medium current (3-10A) | 75mV |
| 0.02Ω | 10A | Medium current (3-10A) | 100mV |
| 0.05Ω | 6.3A | Lower current (1-5A) | 250mV |
| 0.1Ω | 4.5A | Low current (<3A), precision sensing | 500mV |

**Recommended starter set:**

- 0.01Ω or 0.02Ω: For motor current sensing
- 0.05Ω or 0.1Ω: For lower-current loads or precision applications

---

### Bulk Electrolytic Capacitors

#### Why Bulk Caps for Motor Control?

Motors create **huge current spikes** when starting/stopping:

- **Inrush current**: 3-10× running current
- **Back-EMF spikes**: When PWM switches off
- **Ripple current**: From PWM switching

Your small caps (22µF-470µF from passive kit) **cannot handle this alone**.

#### Why Through-Hole for Bulk Caps?

**Important Note:** Through-hole is the **industry standard** for high-value bulk electrolytic capacitors (>1000µF) due to:

- Better heat dissipation
- Higher ripple current capability
- Much lower cost (SMD options are 5-10× more expensive)
- Easier to mount securely for high vibration applications
- Standard practice in motor control and power electronics

#### 1000µF/25V Options

**Budget Option (C46867075 - Econd):**

- Size: D10×L20mm
- 3000hrs @ 105°C lifetime
- Price: $0.07 each @ 10+
- Excellent stock
- **Best for**: Cost-sensitive designs (recommended)

**Good Option (C51953439 - JIERR):**

- Size: D10×L20mm
- 50mΩ ESR @100kHz (better performance)
- Price: $0.14 each @ 10+
- **Best for**: When you need better ESR/ripple current

#### 2200µF/35V Options

**Budget Option (C49332869 - Econd):**

- Size: D13×L25mm
- 30mΩ ESR
- Price: $0.13 each @ 10+
- Excellent stock
- **Best for**: Cost-sensitive designs (recommended)

**Good Option (C51904469 - JIERR):**

- Size: D13×L25mm
- 28mΩ ESR @100kHz (slightly better)
- Price: $0.34 each @ 10+ (2.6× more expensive)
- **Best for**: When performance matters more than cost

#### Quantity Recommendations

- **1000µF/25V**: 10 pieces (1-2 per 12V motor project)
- **2200µF/35V**: 10 pieces (1-2 per 24V motor project)

#### Placement

- As close as possible to motor driver or buck converter input
- Parallel with smaller caps (your 100µF from passive kit)
- Add 100nF ceramic bypass caps nearby

---

### PTC Resettable Fuses

#### Why Resettable Fuses?

**Critical for motor protection:**

- Motor stalls → overcurrent → destroy MOSFETs/driver
- PTC fuse heats up, goes high resistance, limits current
- After fault clears, cools down and resets automatically

**Better than regular fuses:**

- No replacement needed
- Fast response (vs slow-blow)
- Self-resetting (vs one-time)

#### Parts Selection

**1A Rating (C2760271 - BNstar):**

- 16V max voltage (works with 5V, 12V rails)
- 1206 package
- $0.03 @ 10+
- Excellent stock (22,460)
- **Use case**: 5V logic protection, sensors, small loads

**2A Rating (C720175 - Littelfuse):**

- 8V max voltage (12V rail protection)
- 1812 package
- 20mΩ resistance
- Littelfuse = premium brand
- $0.14 @ 5+
- **Use case**: Small motors, solenoids on 12V

**3A Rating (C18198349 - LUTE):**

- 16V max voltage (works with 12V rail)
- 1812 package
- Budget-friendly: $0.06 @ 10+
- Excellent stock (24,800)
- **Use case**: Larger motors, pumps up to 3A

#### Selection Guide

| Rating | Max Voltage | Package | Use Case | Typical Trip Current |
|--------|-------------|---------|----------|---------------------|
| 1A | 16V | 1206 | Logic, sensors | ~2A |
| 2A | 8V | 1812 | Small motors (12V) | ~4A |
| 3A | 16V | 1812 | Larger motors | ~6A |

**Selection tip**: Choose PTC rated for 1.5-2× your expected load current to avoid nuisance tripping.

---

## Application Examples

### Example 1: 12V Motor Current Sensing

```
12V Rail ──[2200µF bulk]──[0.02Ω sense]──[Motor]──[AO3400A MOSFET]── GND
                              │                         │
                         MCP6002 amp              MCU PWM control
                              │
                          MCU ADC
```

**Current calculation:**

- Motor draws 3A
- Voltage across 0.02Ω = 3A × 0.02Ω = 0.06V (60mV)
- Amplify 10× with op-amp → 0.6V to MCU ADC
- Power dissipation: P = I² × R = 3² × 0.02 = 0.18W (well within 2W rating)

### Example 2: Motor Protection with PTC

```
24V Input ──[3A PTC Fuse]──[2200µF/35V]──[Motor Driver]── Motor
                                                             │
                                                        If stall occurs:
                                                        Motor draws 15A
                                                        → PTC trips
                                                        → Current limited
                                                        → MOSFETs safe
```

### Example 3: Dual Motor System

```
12V Input ──┬──[2A PTC]──[1000µF]── Motor 1 Driver
            │
            └──[3A PTC]──[1000µF]── Motor 2 Driver (larger)
```

---

## Comparison: Budget vs Good Tier

### Budget Tier (FOJAN/Yezhan + Econd caps + BNstar/LUTE fuses)

**Pros:**

- **Excellent value**: ~$11 for components, ~$21-26 total with shipping
- Good quality for hobbyist use
- All components in stock
- Econd caps have good 3000hr @ 105°C rating

**Cons:**

- Wider temperature coefficient for current sense resistors
- Less consistent lot-to-lot than premium brands

**Best for:** Hobbyist projects, prototyping, learning, cost-sensitive builds

### Good Tier (UNI-ROYAL + JIERR caps + Littelfuse)

**Pros:**

- Better temperature stability on current sense resistors
- JIERR caps have lower ESR (better performance)
- More consistent specifications
- Premium fuse brand (Littelfuse)

**Cons:**

- ~1.4× more expensive than budget tier (~$15 vs ~$11)

**Best for:** Production, when consistency matters, commercial projects

---

## Pricing Summary

### Option 1: Budget Build (Recommended for Hobbyists)

| Component Type | Qty | Unit Price | Total |
|----------------|-----|------------|-------|
| Current sense (FOJAN/Yezhan, 4 values) | 40 | $0.04 avg | $1.71 |
| 1000µF/25V (Econd TH) | 10 | $0.07 | $0.69 |
| 2200µF/35V (Econd TH) | 10 | $0.13 | $1.29 |
| 1A PTC (BNstar) | 30 | $0.03 | $0.89 |
| 2A PTC (Littelfuse) | 30 | $0.14 | $4.33 |
| 3A PTC (LUTE) | 30 | $0.06 | $1.81 |
| **SUBTOTAL** | **180** | | **$10.72** |

**Plus shipping:** ~$10-15
**Grand total:** ~$21-26

### Option 2: Good Build (Better Performance)

| Component Type | Qty | Unit Price | Total |
|----------------|-----|------------|-------|
| Current sense (UNI-ROYAL, 5 values) | 90 | $0.04 avg | $3.48 |
| 1000µF/25V (JIERR TH) | 10 | $0.14 | $1.35 |
| 2200µF/35V (JIERR TH) | 10 | $0.34 | $3.38 |
| 1A PTC (BNstar) | 30 | $0.03 | $0.89 |
| 2A PTC (Littelfuse) | 30 | $0.14 | $4.33 |
| 3A PTC (LUTE) | 30 | $0.06 | $1.81 |
| **SUBTOTAL** | **200** | | **$15.24** |

**Plus shipping:** ~$10-15
**Grand total:** ~$25-30

### Option 3: Mixed (Good Value/Performance Balance)

- Budget current sense resistors (FOJAN/Yezhan)
- Budget 1000µF cap (Econd TH)
- Good 2200µF cap (JIERR TH)
- Same PTCs

**Total:** ~$13 + shipping = **$23-28**

---

## vs Digikey Comparison

| Component | Digikey MOQ | Digikey Cut-Tape (10pc) | LCSC (10pc Budget) | LCSC (10pc Good) | Savings |
|-----------|-------------|------------------------|-------------------|-----------------|---------|
| Current sense 0.01Ω | 1000-4000 | $5.00 | $0.46 | $0.76 | 85-91% |
| Current sense 0.02Ω | 1000-4000 | $5.00 | $0.31 | $0.79 | 84-94% |
| 1000µF/25V (TH) | 200-500 | $15.00 | $0.69 | $1.35 | 91-95% |
| 2200µF/35V (TH) | 75-100 | $30.00 | $1.29 | $3.38 | 89-96% |
| 1A PTC | 3000 | $6.00 | $0.89 | $0.89 | 85% |
| 2A PTC | 2000 | $6.60 | $4.33 | $4.33 | 34% |

**Overall Savings:** 60-75% cheaper for budget tier, 50-65% for good tier

---

## Integration with Your Other Kits

**Works with passive components:**

- Gate resistors for MOSFETs: 1K-10K from your 0805 resistor kit
- Op-amp feedback for current sense amp: Resistors from your kit
- Bypass caps for bulk caps: 100nF from your capacitor kit

**Works with active components (LCSC Mixed Kit):**

- N-MOSFETs (AO3400A, SI2302) for motor switching
- Op-amps (MCP6002) for current sense amplification
- Schottky diodes (SS14, SS34) for flyback protection

**Works with protection kit (Digikey):**

- TVS diodes (SMBJ15A) on 12V/24V input for transient protection
- Zener diodes (MM3Z12VT1G) for overvoltage clamping

---

## Ordering Notes

### Stock Availability

All components shown have good stock levels (>2,000 pieces) as of search date.

### MOQ (Minimum Order Quantity)

- Current sense resistors: 10-20 pieces
- Bulk caps: 5-10 pieces
- PTC fuses: 5-10 pieces

**Much better than Digikey's 75-4000 piece MOQs!**

### Shipping

- Typical cost: $10-15 for orders <$50
- Delivery time: 1-2 weeks to US/EU
- Free shipping often available for orders >$50

### Recommended Order Workflow

1. Create account on LCSC.com
2. Add parts to cart using LCSC codes (C-codes)
3. Review cart and check stock one final time
4. Place order and track shipment

---

## Storage & Organization

**Recommended labeling:**

- "Current Sense 0.01Ω-0.1Ω 2W 2512"
- "Bulk Caps 1000µF/25V TH"
- "Bulk Caps 2200µF/35V TH"
- "PTC Fuses 1A-3A SMD"

**Storage:**

- ESD-safe containers for current sense resistors and fuses
- Keep capacitors in dry environment (sensitive to humidity)
- Label clearly with value and LCSC code for easy reordering

---

## Next Steps

1. **Decide on tier**: Budget (~$21-26 shipped) vs Good (~$25-30 shipped) vs Mixed (~$23-28 shipped)
2. **Review LCSC codes** in table above
3. **Add to LCSC cart** using codes
4. **Order and wait 1-2 weeks** for delivery
5. **Test with first motor project** - start with current sensing + overcurrent protection

---

## Notes

- **Quality**: Budget LCSC brands work fine for hobby projects, but use good brands for production
- **Through-hole is normal**: For high-value electrolytic caps, through-hole is industry standard
- **Lead time**: Factor in 1-2 week delivery vs Digikey's 2-3 days
- **Reordering**: LCSC codes (C-codes) make reordering easy and exact

**Pro tip:** Start with budget tier to learn motor control concepts, then upgrade to good tier for production designs if needed!
