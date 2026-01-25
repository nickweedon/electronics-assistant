# Motor Control & Power Components Kit (Digikey)

Essential power management components for motor/pump/solenoid control projects

---

## Summary

- **Total component types**: 14
- **Total quantity**: 190 pieces
- **Use case**: Current sensing, overcurrent protection, bulk power filtering for dual-rail MCU projects
- **Estimated total cost**: ~$35-45 (at listed MOQ quantities)
- **Source**: Digikey (primary)

---

## Component List

| # | Type | Part Number | Manufacturer | Specs | Package | Qty | DigiKey P/N | Unit Price @ MOQ | Total | MOQ |
|---|------|-------------|--------------|-------|---------|-----|-------------|------------------|-------|-----|
| **Current Sense Resistors (2W, 2512 package)** | | | | | | | | | | |
| 1 | Current Sense | CRF2512-FZ-R010ELF | Bourns | 0.01Ω 1% 2W | 2512 | 10 | CRF2512-FZ-R010ELFTR-ND | $0.13 | $1.30 | 4000 |
| 2 | Current Sense | PE2512FKE7W0R01L | YAGEO | 0.01Ω 1% 2W | 2512 | 10 | YAG2167TR-ND | $0.17 | $1.70 | 4000 |
| 3 | Current Sense | MCS3264R015FER | Ohmite | 0.015Ω 1% 2W | 2512 | 10 | 273-MCS3264R015FERTR-ND | $0.19 | $1.90 | 4000 |
| 4 | Current Sense | CSRN2512FK10L0 | Stackpole | 0.01Ω 1% 2W | 2512 | 10 | CSRN2512FK10L0TR-ND | $0.21 | $2.10 | 1000 |
| 5 | Current Sense | WSL2512R0100FEA18 | Vishay Dale | 0.01Ω 1% 2W | 2512 | 10 | WSLH-.01TR-ND | $0.21 | $2.10 | 2000 |
| **Bulk Electrolytic Capacitors** | | | | | | | | | | |
| 6 | Cap Aluminum | EMZS250ARA102MJA0G | Chemi-Con | 1000µF 20% 25V | SMD | 10 | 565-5120-2-ND | $0.37 | $3.70 | 500 |
| 7 | Cap Aluminum | EEV-FK1E102Q | Panasonic | 1000µF 20% 25V | SMD | 10 | PCE3462TR-ND | $0.61 | $6.10 | 200 |
| 8 | Cap Aluminum | 35TLV2200M16X21.5 | Rubycon | 2200µF 20% 35V | SMD 16x21.5mm | 10 | 1189-2111-2-ND | $1.63 | $16.30 | 75 |
| 9 | Cap Aluminum | VE-222M1VTR-1621S | SURGE | 2200µF 20% 35V | SMD 16x21mm | 10 | 4403-VE-222M1VTR-1621STR-ND | $1.32 | $13.20 | 100 |
| **PTC Resettable Fuses** | | | | | | | | | | |
| 10 | PTC Fuse | 0ZCJ0100FF2E | Bel Fuse | 1A 6V | 1206 | 30 | 5923-0ZCJ0100FF2ETR-ND | $0.09 | $2.70 | 3000 |
| 11 | PTC Fuse | MF-NSMF050-2 | Bourns | 0.5A 13.2V | 1206 | 30 | MF-NSMF050-2TR-ND | $0.15 | $4.50 | 3000 |
| 12 | PTC Fuse | 0ZCG0200FF2C | Bel Fuse | 2A 8V | 1812 | 30 | 5923-0ZCG0200FF2CTR-ND | $0.10 | $3.00 | 2000 |
| 13 | PTC Fuse | MINISMDC200F-2 | Littelfuse | 2A 8V | 1812 | 30 | MINISMDC200F-2TR-ND | $0.22 | $6.60 | 2000 |
| 14 | PTC Fuse | 0ZCG0300FF2B | Bel Fuse | 3A 6V | 1812 | 30 | 5923-0ZCG0300FF2BTR-ND | $0.14 | $4.20 | 1500 |

**TOTAL: 190 pieces, ~$67.40 (at listed prices for listed quantities)**

**Note:** Prices shown are for MOQ (minimum order quantity) pricing. You may need to order full MOQs or pay higher cut-tape pricing.

---

## Component Details

### Current Sense Resistors (2W, 2512 Package)

#### Why Current Sensing?

For motor/pump/solenoid control, current sensing enables:

- **Overcurrent detection**: Detect motor stall or shorts
- **Power monitoring**: Measure actual power consumption
- **Fault protection**: Shut down before damage occurs
- **PWM current control**: Feedback for current-mode control

#### Usage Circuit

```
12V/24V Power ──[Rsense]──[Load (Motor/Solenoid)]──[N-MOSFET]── GND
                    |
              Op-Amp/ADC (measure voltage drop)
```

**Current calculation:** I = V_sense / R_sense

#### Parts Selection

| Value | Part Number | Manufacturer | Max Current @ 2W | Typical Use |
|-------|-------------|--------------|------------------|-------------|
| 0.01Ω | CRF2512-FZ-R010ELF | Bourns | 14.1A | High current (motors >5A) |
| 0.01Ω | PE2512FKE7W0R01L | YAGEO | 14.1A | Alternative source |
| 0.015Ω | MCS3264R015FER | Ohmite | 11.5A | Medium current (3-10A) |
| 0.01Ω | WSL2512R0100FEA18 | Vishay | 14.1A | Precision option |

**Selection guide:**

- **0.01Ω**: For high-current loads (5-15A) - gives 0.05-0.15V drop
- **0.015Ω**: For medium loads (2-10A) - gives 0.03-0.15V drop
- Voltage drop should be < 200mV for efficiency
- Use op-amp (MCP6002 from your kit) to amplify for ADC

**Why 2512 (2W) package?**

- Higher power rating prevents thermal drift
- Better heat dissipation
- More accurate at high currents

---

### Bulk Electrolytic Capacitors

#### Why Bulk Caps for Motor Control?

Motors create **huge current spikes** when starting/stopping:

- **Inrush current**: 3-10× running current
- **Back-EMF spikes**: When PWM switches off
- **Ripple current**: From PWM switching

Your small caps (22µF-470µF from passive kit) **cannot handle this alone**.

#### Usage

```
12V/24V Input ─┬─[TVS/Fuse]─┬─[1000µF-2200µF Bulk]─┬─ Buck Converter
               │             │                       │
              GND           GND                [100nF local bypass]
                                                     │
                                              MCU/Motor Driver
```

#### Parts Selection

**1000µF/25V (for 12V rail):**

| Part | Manufacturer | Size | ESR | Ripple Current |
|------|--------------|------|-----|----------------|
| EMZS250ARA102MJA0G | Chemi-Con | SMD | Low | High |
| EEV-FK1E102Q | Panasonic | SMD | Low | High |

**2200µF/35V (for 24V rail or higher margin):**

| Part | Manufacturer | Size | Price/Unit @ MOQ |
|------|--------------|------|------------------|
| 35TLV2200M16X21.5 | Rubycon | 16x21.5mm | $1.63 |
| VE-222M1VTR-1621S | SURGE | 16x21mm | $1.32 (better value) |

**Quantity Recommendations:**

- **1000µF/25V**: 10 pieces (1-2 per 12V motor project)
- **2200µF/35V**: 10 pieces (1-2 per 24V motor project)

**Placement:**

- As close as possible to motor driver or buck converter input
- Parallel with smaller caps (your 100µF from passive kit)

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

#### Usage Circuit

```
12V/24V Input ──[PTC Fuse]──[Bulk Cap]──[Motor Driver]── Load
                    |
               (Trips on overcurrent,
                resets when cool)
```

#### Parts Selection

**1A Rating (for sensors, small loads):**

| Part | Voltage | Package | Price @ MOQ | Use Case |
|------|---------|---------|-------------|----------|
| 0ZCJ0100FF2E | 6V | 1206 | $0.09 | 5V logic protection |
| MF-NSMF050-2 | 13.2V | 1206 | $0.15 | 12V sensor protection |

**2A Rating (for small motors, solenoids):**

| Part | Voltage | Package | Price @ MOQ | Use Case |
|------|---------|---------|-------------|----------|
| 0ZCG0200FF2C | 8V | 1812 | $0.10 | 12V small motors |
| MINISMDC200F-2 | 8V | 1812 | $0.22 | Alternative (Littelfuse) |

**3A Rating (for larger motors, pumps):**

| Part | Voltage | Package | Price @ MOQ | Use Case |
|------|---------|---------|-------------|----------|
| 0ZCG0300FF2B | 6V | 1812 | $0.14 | 12V motors up to 3A |

**Selection Guide:**

- **Hold current** (I_hold): Normal operating current
- **Trip current** (I_trip): Typically 2× I_hold
- Choose PTC rated for 1.5-2× your expected load current
- Voltage rating must exceed your rail voltage

**Quantity:** 30 pieces each (3-4 projects worth, plus spares)

---

## Application Examples

### Example 1: 12V Motor Current Sensing

```
12V Rail ──[2200µF bulk]──[0.01Ω sense]──[Motor]──[AO3400A MOSFET]── GND
                              │                         │
                         MCP6002 amp              MCU PWM control
                              │
                          MCU ADC
```

**Current calculation:**

- Motor draws 5A
- Voltage across 0.01Ω = 5A × 0.01Ω = 0.05V (50mV)
- Amplify 10× with op-amp → 0.5V to MCU ADC
- Power dissipation: P = I² × R = 5² × 0.01 = 0.25W (well within 2W rating)

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
24V Input ──┬──[PTC 2A]──[Bulk 1000µF]── Motor 1 Driver
            │
            └──[PTC 3A]──[Bulk 2200µF]── Motor 2 Driver (larger)
```

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

## Why These Components Are Essential

### For Your Dual-Rail Motor Projects

1. **Current Sense Resistors:**
   - **Problem:** Can't tell if motor is stalled or drawing too much current
   - **Solution:** Sense resistor + op-amp + ADC = real-time current monitoring
   - **Result:** Prevent MOSFET/driver damage, implement soft-start, measure power

2. **Bulk Capacitors:**
   - **Problem:** Small caps can't handle motor inrush (3-10× normal current)
   - **Solution:** Large bulk caps provide energy reservoir for current spikes
   - **Result:** Stable voltage, prevent brownouts, protect buck converter

3. **PTC Fuses:**
   - **Problem:** Motor stall or short destroys expensive MOSFETs/drivers
   - **Solution:** Self-resetting fuse trips on overcurrent, resets when cooled
   - **Result:** Automatic protection, no manual intervention, reusable

### Industry Best Practices

- **Automotive/Industrial:** Always use current sensing + overcurrent protection
- **Motor drivers:** TI, Infineon, ST all recommend bulk caps 10× larger than logic caps
- **Reliability:** PTC fuses standard in consumer electronics with motors (printers, fans, pumps)

---

## Ordering Notes

### MOQ Challenges

Most parts have high MOQs (1000-4000 pieces). Options:

1. **Order full reel** if you'll use them across many projects
2. **Cut-tape pricing** (Digikey offers, ~2-3× more expensive)
3. **Digi-Reel** (custom reel, pays cutting fee once)
4. **Group buy** with other hobbyists

### Alternative: Through-Hole Options

If SMD MOQs are too high, through-hole alternatives exist:

- **Current sense:** Vishay WSL series in through-hole packages
- **Bulk caps:** Radial aluminum electrolytics (22mm spacing)
- **PTC fuses:** Bourns/Littelfuse radial PTCs

*Let me know if you want me to create a through-hole version of this kit.*

---

## Pricing Summary (Realistic for Hobby Use)

### Option 1: Buy Minimum Quantities Listed Above

- **Total:** ~$67.40
- **Issue:** Requires buying 75-4000 pieces per part (way more than needed)

### Option 2: Cut-Tape Pricing (10 pieces each)

| Component Type | Qty | Est. Cut-Tape Price | Total |
|----------------|-----|---------------------|-------|
| Current Sense (5 types) | 50 | $0.50 each | $25 |
| 1000µF/25V caps | 10 | $1.50 each | $15 |
| 2200µF/35V caps | 10 | $3.00 each | $30 |
| PTC Fuses (5 types) | 50 | $0.40 each | $20 |
| **TOTAL** | **120** | | **~$90** |

### Option 3: LCSC Lower MOQ Alternative (RECOMMENDED)

**See actual LCSC kit:** [Motor_Control_Components_LCSC_Kit.md](Motor_Control_Components_LCSC_Kit.md)

**LCSC pricing summary:**

- Budget tier: ~$11 + shipping ($10-15) = **$21-26 total**
- Good tier: ~$15 + shipping ($10-15) = **$25-30 total**
- Mixed tier: ~$13 + shipping = **$23-28 total**

**Savings vs Digikey cut-tape:** 60-75% cheaper!

**Trade-off:** 1-2 week shipping vs Digikey's 2-3 days

---

## Next Steps

1. **Review LCSC kit** - See [Motor_Control_Components_LCSC_Kit.md](Motor_Control_Components_LCSC_Kit.md) for actual components with LCSC codes
2. **Decide on supplier:**
   - **LCSC** = Lower MOQs (10-50pcs), cheaper (60-75% savings), slower shipping (1-2 weeks) - **RECOMMENDED**
   - **Digikey** = Fast shipping (2-3 days), higher MOQs or cut-tape pricing
3. **Start with essentials:** Order current sense resistors and bulk caps first, add PTC fuses later
4. **Plan first project** to test current sensing + protection

---

## Storage & Organization

**Recommended labeling:**

- "Current Sense 0.01Ω-0.015Ω 2W 2512"
- "Bulk Caps 1000µF/25V"
- "Bulk Caps 2200µF/35V"
- "PTC Fuses 1A-3A SMD"

**Storage:** ESD-safe containers, keep in dry environment (capacitors sensitive to humidity).
