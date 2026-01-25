# Medium Priority Components Kit (LCSC)

Signal conditioning, isolation, and noise reduction components for dual-rail MCU projects

---

## Summary

- **Total component types**: 4
- **Total quantity**: 80 pieces
- **Use case**: Sensor conditioning, isolation, EMI filtering
- **Estimated total cost**: ~$5-7 (LCSC pricing)

---

## Component List

| # | Type | Part Number | Manufacturer | Package | Description | Qty | LCSC Code | Est. Price |
|---|------|-------------|--------------|---------|-------------|-----|-----------|------------|
| 1 | Op-Amp | MCP6002-I/SN | Microchip | SOIC-8 | Dual RRIO op-amp, rail-to-rail I/O | 10 | C7377 | $0.15-0.20 ea |
| 2 | Op-Amp | TLV2372IDR | Texas Instruments | SOIC-8 | Dual RRIO op-amp, 3MHz GBW | 10 | Need to verify | $0.30-0.40 ea |
| 3 | Optocoupler | PC817C | Sharp / LiteOn | DIP-4 (SMD) | 4-pin optocoupler, 5000Vrms | 40 | C44452 | $0.05-0.08 ea |
| 4 | Ferrite Bead | GZ2012D601TF | Sunlord | 0805 | 600Ω@100MHz, 2A | 50 | C1017 | $0.01-0.02 ea |

---

## Component Details

### 1. MCP6002-I/SN - Dual Rail-to-Rail Op-Amp

**Specifications:**

- **Manufacturer:** Microchip Technology
- **Package:** SOIC-8
- **Type:** Dual operational amplifier
- **Supply:** 1.8V to 6V (perfect for 3.3V/5V rails)
- **Input/Output:** Rail-to-rail
- **GBW:** 1MHz
- **Offset:** ±4.5mV max
- **Quiescent:** 100µA/amplifier (low power)
- **LCSC:** C7377

**Use Cases:**

- Sensor signal conditioning (temperature, pressure, current)
- Active filters (low-pass, high-pass, band-pass)
- Voltage followers/buffers
- Summing/difference amplifiers
- Comparators (with hysteresis)
- Current sensing (shunt amplifier)

**Why This Part:**

- Extremely common, well-stocked at LCSC
- Low cost (~$0.15-0.20)
- Single supply operation (no dual rails needed)
- RRIO perfect for ADC interfacing
- Low power for battery applications

---

### 2. TLV2372IDR - Dual RRIO Op-Amp (Alternative)

**Specifications:**

- **Manufacturer:** Texas Instruments
- **Package:** SOIC-8
- **Type:** Dual operational amplifier
- **Supply:** 2.7V to 16V (works with both 5V and 12V rails)
- **Input/Output:** Rail-to-rail
- **GBW:** 3MHz (faster than MCP6002)
- **Offset:** ±1mV max (better precision)
- **LCSC:** Need to verify code

**Use Cases:**

- Higher speed signal conditioning
- Precision measurements
- Audio applications
- Active filters requiring higher bandwidth

**Why This Part:**

- Higher performance alternative to MCP6002
- Better for fast-changing signals
- Can operate from 12V rail if needed

---

### 3. PC817C - Optocoupler

**Specifications:**

- **Manufacturer:** Sharp / LiteOn / Various
- **Package:** DIP-4 (SMD version: SOP-4)
- **Type:** Single channel optocoupler
- **Isolation:** 5000Vrms
- **CTR (Current Transfer Ratio):** 80-160% (C grade)
- **Forward Voltage:** 1.2V typical
- **Collector-Emitter Voltage:** 35V max
- **Forward Current:** 50mA max
- **LCSC:** C44452 (verify package - DIP vs SOP)

**Use Cases for Your Dual-Rail Projects:**

- **Isolation between 12V/24V power rail and logic rail**
- Motor/solenoid control signal isolation
- AC mains detection (zero-crossing)
- Protecting MCU from high-voltage circuits
- Interfacing with industrial 24V signals
- Galvanic isolation for safety

**Typical Circuit:**

```
12V/24V Side:              Logic Side (3.3V/5V):

Input Signal               VCC (3.3V or 5V)
    |                          |
    +---[Resistor]---+         R (pullup)
                     |         |
    PC817 LED    [PC817]   Collector----> MCU Input
    (pins 1,2)       |         |
                     |     Emitter
    GND          Ground      Ground
```

**Why This Part:**

- Industry standard, cheap (~$0.05-0.08)
- Essential for safe isolation
- Prevents ground loops
- Protects expensive MCU from high-voltage faults

---

### 4. GZ2012D601TF - Ferrite Bead (600Ω@100MHz)

**Specifications:**

- **Manufacturer:** Sunlord
- **Package:** 0805 (2012 metric)
- **Impedance:** 600Ω @ 100MHz
- **DC Resistance:** 150mΩ max
- **Rated Current:** 2A
- **Voltage:** 50V
- **LCSC:** C1017

**Use Cases:**

- **Power rail noise filtering** (buck converter output)
- EMI suppression on clock lines
- Analog/digital power isolation
- USB data line filtering
- Motor driver power supply filtering
- Reducing switching noise coupling

**Typical Application:**

```
Noisy Power     Ferrite      Clean Power
(Buck Output) --[Bead 600Ω]-- (to MCU VCC)
                                   |
                                [100nF]
                                   |
                                  GND
```

**Why This Part:**

- Very cheap (~$0.01-0.02)
- 2A rating suitable for most MCU/sensor loads
- 600Ω good balance for filtering without excessive voltage drop
- Common at LCSC, good availability

---

## Quantity Recommendations

| Component | Qty | Justification |
|-----------|-----|---------------|
| MCP6002 | 10 | 2 op-amps per chip, 5 projects' worth |
| TLV2372 | 10 | Alternative for higher performance needs |
| PC817C | 40 | Multiple isolation points per project (2-4 each) |
| Ferrite Beads | 50 | Many needed per board (5-10 per project) |

**Total: 80 pieces (plus 30 additional if ordering both op-amp types)**

---

## Application Examples for Your Projects

### Example 1: Current Sensing for Motor Control

```
Motor Current (via shunt resistor) → MCP6002 (amplify) → MCU ADC
                                      ↓
                                 PC817 (fault signal to MCU if overcurrent)
```

### Example 2: Isolated 12V Input to MCU

```
12V Sensor/Switch → PC817 input → PC817 output → MCU GPIO
(isolated)                          (3.3V logic level)
```

### Example 3: Clean Power for Analog Sensors

```
5V Buck Converter → Ferrite Bead → Clean 5V for sensors
                                         ↓
                    Sensor → MCP6002 buffer → MCU ADC
```

---

## Integration with Existing Components

**Works with your resistor/capacitor kits:**

- Op-amp feedback networks: Resistors from your 0805 1% kit
- Op-amp stability: Capacitors from your ceramic cap kit
- Optocoupler current limiting: 220Ω-1KΩ from your resistor kit
- Ferrite bead decoupling: 100nF caps from your kit

**Complements your protection kit:**

- Op-amps for conditioning signals after TVS protection
- Optocouplers for isolation beyond TVS protection
- Ferrite beads work with your bypass caps for comprehensive filtering

---

## LCSC Ordering Notes

**Verified LCSC Codes (Ready to Order):**

- C7377: MCP6002-I/SN (Microchip, SOIC-8)
- C44452: PC817C (verify if DIP-4 or SOP-4 SMD)
- C1017: GZ2012D601TF (Sunlord, 0805)

**Need Verification:**

- TLV2372IDR: Need to search LCSC for correct code and pricing

**Alternative Sources:**

- If LCSC stock is low, these are also available from:
  - Mouser (more expensive)
  - Digikey (more expensive)
  - AliExpress (cheaper but longer shipping)

---

## Why These Are Medium Priority

**Op-Amps:**

- Essential for sensor conditioning
- Can work around without them using digital methods, but analog conditioning is often better
- Not as critical as protection components

**Optocouplers:**

- **Highly recommended** for dual-rail designs
- Provides safety isolation between high voltage (12V/24V) and logic
- Can be skipped if you're very careful with grounding, but risky

**Ferrite Beads:**

- Nice to have for EMI reduction
- Can use inductors or just capacitors instead
- Improves noise immunity but not absolutely required

---

## Next Steps

1. **Verify LCSC codes** for TLV2372 and PC817C package options
2. **Check stock availability** on LCSC before ordering
3. **Consider quantities** based on your project pipeline
4. **Review datasheets** for specific application circuits

---

## Storage & Organization

**Recommended labeling:**

- "Op-Amps RRIO SOIC-8"
- "PC817 Optocouplers"
- "Ferrite Beads 0805 600Ω"

**Storage:** Standard component storage, ESD precautions for ICs.
