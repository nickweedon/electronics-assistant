# Protection Components Kit

Essential protection components for dual-rail MCU projects (12V/24V + 3.3V/5V logic)

---

## Summary

- **Total component types**: 5
- **Total quantity**: 185 pieces
- **Use case**: Overvoltage protection, ESD protection, voltage references
- **Estimated total cost**: ~$11.50 (at 3k quantity pricing)

---

## Component List

| # | Type | Part Number | Manufacturer | Voltage | Package | Description | Qty | Unit Price @ 3k | Total |
|---|------|-------------|--------------|---------|---------|-------------|-----|-----------------|-------|
| 1 | Zener Diode | MM3Z3V3T1G | onsemi | 3.3V | SOD-323 | 300mW Zener for 3.3V rail protection | 50 | $0.017 | $0.85 |
| 2 | Zener Diode | MM3Z5V1T1G | onsemi | 5.1V | SOD-323 | 300mW Zener for 5V rail protection | 50 | $0.017 | $0.85 |
| 3 | Zener Diode | MM3Z12VT1G | onsemi | 12V | SOD-323 | 300mW Zener for 12V rail protection | 25 | $0.018 | $0.45 |
| 4 | TVS Diode | DESD5V0U1BA-7 | Diodes Inc | 5V | SOD-323 | Bidirectional TVS for 5V logic I/O | 40 | $0.028 | $1.12 |
| 5 | TVS Diode | SMBJ15A | YAGEO | 15V | DO-214AA | Bidirectional TVS for 12V rail | 20 | $0.0523 | $1.05 |

**Note:** Prices shown are for 3000-piece reel quantities. Smaller quantities available at higher unit prices.

---

## Component Details

### Zener Diodes (SOD-323)

#### 1. MM3Z3V3T1G - 3.3V Zener

- **Manufacturer:** onsemi
- **Voltage:** 3.3V (±5%)
- **Power:** 300mW
- **Package:** SOD-323
- **DigiKey P/N:** MM3Z3V3T1GOSTR-ND
- **Stock:** 73,589 available
- **Use cases:**
  - 3.3V rail overvoltage protection
  - Voltage reference for analog circuits
  - Reverse polarity protection indicator

#### 2. MM3Z5V1T1G - 5.1V Zener

- **Manufacturer:** onsemi
- **Voltage:** 5.1V (±5%)
- **Power:** 300mW
- **Package:** SOD-323
- **DigiKey P/N:** MM3Z5V1T1GOSTR-ND
- **Stock:** 144,000 available
- **Use cases:**
  - 5V rail overvoltage protection
  - Voltage reference for 5V systems
  - MCU I/O clamping (with series resistor)

#### 3. MM3Z12VT1G - 12V Zener

- **Manufacturer:** onsemi
- **Voltage:** 12V (±5%)
- **Power:** 300mW
- **Package:** SOD-323
- **DigiKey P/N:** MM3Z12VT1GOSTR-ND
- **Stock:** 119,812 available
- **Use cases:**
  - 12V rail overvoltage protection
  - Voltage reference for 12V systems
  - Reverse polarity protection

---

### TVS/ESD Protection Diodes

#### 4. DESD5V0U1BA-7 - 5V TVS

- **Manufacturer:** Diodes Incorporated
- **Working Voltage:** 5VWM
- **Breakdown Voltage:** 7.2V typ
- **Package:** SOD-323
- **Type:** Bidirectional
- **DigiKey P/N:** DESD5V0U1BA-7DITR-ND
- **Stock:** 137,614 available
- **Use cases:**
  - UART/I2C/SPI communication line protection
  - MCU I/O pin ESD protection
  - Sensor interface protection
  - USB data line protection

#### 5. SMBJ15A - 15V TVS

- **Manufacturer:** YAGEO
- **Working Voltage:** 15VWM
- **Breakdown Voltage:** 16.7V typ, 24.4V max clamp
- **Package:** DO-214AA (SMB)
- **Type:** Bidirectional
- **DigiKey P/N:** 13-SMBJ15A/TR13TR-ND
- **Stock:** 3,338 available
- **Alternative:** P6SMBJ15A from Diotec (3,363 stock, $0.061 @ 3k)
- **Use cases:**
  - 12V power rail overvoltage/transient protection
  - Motor/solenoid flyback protection (with Schottky)
  - Automotive/industrial 12V interface protection
  - Power supply input protection

---

## Application Guidelines

### Zener Diode Usage

**Overvoltage Protection Circuit:**

```
Power Rail ----[Series Resistor]----+---- Protected Output
                                    |
                                  [Zener]
                                    |
                                   GND
```

- **Series resistor:** Calculate based on max current and power dissipation
- **Example for 5V protection:** 100Ω - 1KΩ typical

**Voltage Reference:**

- Use with current limiting resistor from higher voltage
- Provides stable reference voltage
- Low impedance output (good for ADC references)

### TVS Diode Usage

**I/O Protection (5V Logic):**

```
External Signal ----[Series Resistor 100Ω-1KΩ]----+---- MCU I/O Pin
                                                   |
                                              [DESD5V0U1BA]
                                                   |
                                                  GND
```

**Power Rail Protection (12V):**

```
12V Input ----[SMBJ15A]---- Protected 12V Rail
              |
             GND
```

- Place TVS close to connector or entry point
- Keep traces short for effective transient suppression
- Add series resistance on signal lines for current limiting

---

## Quantity Recommendations

| Component | Qty | Justification |
|-----------|-----|---------------|
| 3.3V Zener | 50 | Multiple projects, voltage references, I/O protection |
| 5.1V Zener | 50 | Most common logic voltage, high usage |
| 12V Zener | 25 | Power rail protection, lower usage than logic levels |
| 5V TVS | 40 | Multiple I/O pins per project (UART, I2C, SPI, sensors) |
| 15V TVS | 20 | 1-2 per project for power rail protection |

**Total: 185 pieces**

---

## Pricing Summary

| Component | Qty | Unit Price @ 3k | Extended |
|-----------|-----|-----------------|----------|
| MM3Z3V3T1G | 50 | $0.017 | $0.85 |
| MM3Z5V1T1G | 50 | $0.017 | $0.85 |
| MM3Z12VT1G | 25 | $0.018 | $0.45 |
| DESD5V0U1BA-7 | 40 | $0.028 | $1.12 |
| SMBJ15A | 20 | $0.0523 | $1.05 |
| **TOTAL** | **185** | | **$4.32** |

**Note:** These are individual piece prices at reel quantities. To order less than a full reel, you'll typically pay cut-tape pricing which is higher.

**MOQ Considerations:**

- All parts have 3000-piece MOQ for reel pricing shown above
- Smaller quantities available as cut tape or Digi-Reel at higher unit prices
- For hobby use, consider ordering as cut tape (typically 2-3x reel price)

---

## Integration with Existing Inventory

### Complements Your Current Stock

**Already have (through-hole):**

- 1N4148 signal diodes (DO-35)
- Zeners: 3.3V, 3.6V, 5.1V, 5.6V, 6.2V, 9.1V, 12V, 15V (DO-35)

**This kit adds (SMD):**

- Equivalent Zeners in SOD-323 for PCB designs
- TVS/ESD protection (not currently in inventory)
- Higher surge capability for power rails

### Works With Your Passive Kits

Protection circuits require supporting passives:

- **Series resistors:** Already covered by your 0805 resistor kit (100Ω-1KΩ range)
- **Bypass caps:** Already covered by your capacitor kit (100nF typical)

---

## Why These Components Are Essential

### For Your Dual-Rail Projects

1. **12V/24V Power Rail:**
   - SMBJ15A protects against automotive/industrial transients
   - 12V Zener provides voltage reference and overvoltage clamping

2. **3.3V/5V Logic Rail:**
   - Zeners protect against regulator failure or overvoltage
   - TVS diodes protect MCU I/O from ESD and voltage spikes

3. **Common Failure Scenarios Prevented:**
   - Motor/solenoid back-EMF damaging MCU
   - Static discharge on connectors
   - Voltage spikes from inductive loads
   - Hot-plugging of sensors/actuators
   - Automotive load dump transients (if using 12V/24V from vehicles)

### Industry Best Practices

- **IEC 61000-4-2:** ESD protection requirements (DESD5V0U1BA meets this)
- **Automotive:** ISO 7637-2 requires transient protection (SMBJ15A suitable)
- **Consumer electronics:** Most manufacturers spec TVS on all external I/O

---

## Next Steps

1. **Add to Digikey list** for ordering
2. **Consider additional protection:**
   - Optocouplers for galvanic isolation (see medium priority list)
   - Ferrite beads for EMI filtering (see medium priority list)
3. **Review datasheets** for specific application circuits
4. **Plan PCB layout** with protection close to connectors/entry points

---

## Storage & Organization

**Recommended labeling:**

- "Zeners 3V3-12V SOD-323"
- "TVS 5V-15V SMD"

**Storage:** Keep in anti-static bags/containers. These are ESD-sensitive components.
