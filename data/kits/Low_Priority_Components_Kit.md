# Low Priority Components Kit (LCSC)

Convenience components for SMD-only designs - nice to have but not essential

---

## Summary

- **Total component types**: 9
- **Total quantity**: 80 pieces
- **Use case:** Complete SMD designs, timing circuits, power conversion
- **Estimated total cost:** ~$3-5 (LCSC pricing)
- **Priority:** Low - you already have through-hole equivalents or can work around these

---

## Component List

| # | Type | Part Number | Manufacturer | Package | Description | Qty | LCSC Code | Est. Price | Notes |
|---|------|-------------|--------------|---------|-------------|-----|-----------|------------|-------|
| 1 | Inductor | SWPA4020S4R7MT | Sunlord | 4020 (SMD) | 4.7µH, 3.2A, 28mΩ | 10 | C409398 | $0.10 ea | For buck converters |
| 2 | Inductor | SWPA4020S100MT | Sunlord | 4020 (SMD) | 10µH, 2.4A, 48mΩ | 10 | C99339 | $0.10 ea | For buck converters |
| 3 | Inductor | SWPA4020S220MT | Sunlord | 4020 (SMD) | 22µH, 1.9A, 95mΩ | 5 | C78452 | $0.10 ea | For buck converters |
| 4 | Logic IC | SN74HC14D | TI / HGSEMI | SOIC-14 | Hex Schmitt trigger inverter | 10 | C5524 | $0.08 ea | Button debouncing |
| 5 | Logic IC | 74LVC1G14GW | Nexperia | SOT-353 | Single Schmitt inverter | 10 | C7475 | $0.05 ea | Compact debouncing |
| 6 | 555 Timer | NE555D | TI / Various | SOIC-8 | Classic 555 timer (SMD) | 10 | C7593 | $0.05 ea | Timing/PWM |
| 7 | 555 Timer | TLC555IDR | TI | SOIC-8 | CMOS 555, lower power | 5 | Need verify | $0.15 ea | Better than NE555 |
| 8 | Crystal | X322516MLB4SI | YXC | 3225 SMD | 16MHz, 20pF load | 10 | C9002 | $0.08 ea | MCU timing |
| 9 | Crystal | X322508MLB4SI | YXC | 3225 SMD | 8MHz, 20pF load | 10 | C115962 | $0.08 ea | MCU timing |

**Total: 80 pieces**

---

## Why These Are Low Priority

| Component | Why Low Priority | When You Need It |
|-----------|------------------|------------------|
| **SMD Inductors** | You already have through-hole inductors (4.7µH-100µH) | SMD-only boards, very compact designs |
| **74HC14D** | You have through-hole SN74HC14N already | SMD-only boards |
| **74LVC1G14** | Can use 74HC14 or MCU GPIO with software debounce | Space-constrained designs |
| **NE555 SMD** | You have through-hole NE555N already | SMD-only boards, or can use MCU timers |
| **TLC555** | Can use NE555 or MCU PWM | Low-power applications |
| **Crystals** | MCU internal oscillators usually sufficient | Precise timing (UART, USB, CAN) |

---

## Component Details

### Power Inductors (4020 Package)

**Why 4020 Package:**

- Good balance of size and current handling
- Similar footprint to common buck converter reference designs
- Much smaller than your through-hole axial inductors
- Works with LMR51430 buck converter you already have

**Specifications:**

#### SWPA4020S4R7MT - 4.7µH

- **Inductance:** 4.7µH ±20%
- **Rated Current:** 3.2A
- **DCR:** 28mΩ max
- **SRF:** >40MHz
- **Size:** 4.0 x 4.0 x 2.0mm
- **LCSC:** C409398

#### SWPA4020S100MT - 10µH

- **Inductance:** 10µH ±20%
- **Rated Current:** 2.4A
- **DCR:** 48mΩ max
- **SRF:** >30MHz
- **LCSC:** C99339

#### SWPA4020S220MT - 22µH

- **Inductance:** 22µH ±20%
- **Rated Current:** 1.9A
- **DCR:** 95mΩ max
- **SRF:** >20MHz
- **LCSC:** C78452

**Use with LMR51430:**
Your LMR51430 buck converter (already in inventory) works great with these:

- 4.7µH: For 12V→5V at high current (>2A)
- 10µH: For 12V→5V or 24V→12V at moderate current
- 22µH: For 24V→5V at lower current

**Comparison to Your Through-Hole Inductors:**

- **You have:** Axial inductors (AICC-02 series, through-hole)
- **These add:** SMD option for compact PCBs
- **When to use SMD:** All-SMD assembly, limited board space
- **When to use THT:** Fine for prototypes, mixed THT/SMD boards

---

### Logic ICs - Schmitt Triggers

#### SN74HC14D - Hex Schmitt Trigger Inverter

**Specifications:**

- **Package:** SOIC-14
- **Supply:** 2V to 6V
- **6 inverters** with Schmitt trigger inputs
- **Hysteresis:** ~0.8V typical at 5V supply
- **Output:** Push-pull
- **LCSC:** C5524

**Use Cases:**

- **Switch/button debouncing** (most common)
- Signal conditioning for noisy inputs
- Oscillators (RC oscillator circuits)
- Waveform squaring (convert sine to square)

**You Already Have:** SN74HC14N (DIP-14, through-hole)

**When to order SMD:**

- All-SMD boards only
- Otherwise use your through-hole version

#### 74LVC1G14 - Single Schmitt Trigger Inverter

**Specifications:**

- **Package:** SOT-353 (tiny, 5-pin)
- **Supply:** 1.65V to 5.5V
- **Single inverter** with Schmitt trigger
- **Hysteresis:** ~0.3V at 3.3V supply
- **LCSC:** C7475

**Use Cases:**

- Single button debouncing when you don't need 6 gates
- Space-constrained designs
- Low-power battery applications

---

### 555 Timers (SMD)

#### NE555D - Classic 555 Timer

**Specifications:**

- **Package:** SOIC-8
- **Supply:** 4.5V to 16V (works with 5V or 12V)
- **Output Current:** 200mA
- **Frequency:** Up to ~500kHz
- **Quiescent:** ~3-6mA (bipolar, not low power)
- **LCSC:** C7593

**You Already Have:** NE555N (DIP-8, through-hole)

**Use Cases:**

- PWM generation
- Timing delays
- Oscillators
- Monostable/astable circuits

#### TLC555IDR - CMOS 555 Timer

**Specifications:**

- **Package:** SOIC-8
- **Supply:** 2V to 15V
- **Output Current:** 100mA
- **Frequency:** Up to ~2MHz
- **Quiescent:** ~170µA (much lower than NE555!)
- **LCSC:** Need to verify

**Why Better Than NE555:**

- Much lower power consumption (170µA vs 3-6mA)
- Higher frequency capability
- Lower supply voltage (works with 3.3V)
- Better for battery applications

**When You Need 555 (vs MCU PWM):**

- Simple standalone timing (no MCU needed)
- Learning/experimenting with analog circuits
- Legacy designs
- **Usually MCU PWM is better** for your projects!

---

### Crystals - Precision Timing

#### X322516MLB4SI - 16MHz Crystal

**Specifications:**

- **Package:** 3225 SMD (3.2 x 2.5mm)
- **Frequency:** 16.000MHz
- **Load Capacitance:** 20pF
- **Tolerance:** ±20ppm
- **Temperature:** -20°C to +70°C
- **LCSC:** C9002

#### X322508MLB4SI - 8MHz Crystal

**Specifications:**

- **Package:** 3225 SMD (3.2 x 2.5mm)
- **Frequency:** 8.000MHz
- **Load Capacitance:** 20pF
- **Tolerance:** ±20ppm
- **LCSC:** C115962

**When You Need External Crystal:**

**Don't need (MCU internal RC oscillator OK):**

- GPIO, timers, ADC for most sensors
- Non-critical timing
- Hobby projects
- Most of your motor/sensor projects

**Do need external crystal:**

- **UART at high baud rates** (115200+) over long periods
- **USB communication** (requires precise 48MHz)
- **CAN bus** (automotive/industrial)
- **RTC (Real-Time Clock)** applications
- **Precision timing** (±0.5% or better)

**Load Capacitors:**
Both crystals specify 20pF load. Use two 22pF capacitors (already in your capacitor kit!) from each crystal pin to ground.

**PIC18F46K22 Note:**
Your PIC18F46K22 (in inventory) has:

- Internal oscillator up to 64MHz (with PLL)
- Good enough for most applications
- Only need external crystal for USB or very precise timing

---

## Quantity Recommendations

| Component | Qty | Justification |
|-----------|-----|---------------|
| 4.7µH inductor | 10 | SMD buck converter builds |
| 10µH inductor | 10 | SMD buck converter builds |
| 22µH inductor | 5 | Less common value |
| 74HC14D | 10 | SMD-only boards needing debounce |
| 74LVC1G14 | 10 | Compact single-gate applications |
| NE555D | 10 | SMD timer circuits |
| TLC555 | 5 | Low-power alternatives |
| 16MHz crystal | 10 | USB or precision timing |
| 8MHz crystal | 10 | Common MCU frequency |

**Total: 80 pieces**

---

## Application Examples

### Example 1: All-SMD Buck Converter (12V→5V, 2A)

```
Components needed (all SMD):
- LMR51430YDDCR (already in inventory)
- SWPA4020S4R7MT inductor (this kit)
- Capacitors (already in passive kit)
- Resistors for feedback (already in resistor kit)
```

### Example 2: Debounced Button with Single Gate

```
Button → 74LVC1G14 (Schmitt trigger) → MCU GPIO
         (with RC filter)

Saves 5 unused gates compared to 74HC14D
```

### Example 3: USB-Capable MCU

```
16MHz Crystal + 22pF caps → PIC18F46K22 → USB communication
(Crystal needed for accurate 48MHz USB clock via PLL)
```

---

## Integration Notes

**Works with your existing components:**

- Inductors pair with LMR51430 buck converter (in inventory)
- Crystals use 22pF caps (in your capacitor kit)
- All ICs use standard 100nF bypass caps (in your kit)
- Schmitt triggers work with resistors from your kit

**Not duplicated from other kits:**

- BJTs (MMBT3904/3906) already in LCSC mixed components kit
- P-FETs (AO3401A) already in LCSC mixed components kit
- These are truly optional additions

---

## LCSC Ordering Notes

**Verified LCSC Codes (Ready to Order):**

- C409398: SWPA4020S4R7MT (4.7µH inductor)
- C99339: SWPA4020S100MT (10µH inductor)
- C78452: SWPA4020S220MT (22µH inductor)
- C5524: SN74HC14D (hex Schmitt trigger)
- C7475: 74LVC1G14GW (single Schmitt trigger)
- C7593: NE555D (555 timer)
- C9002: X322516MLB4SI (16MHz crystal)
- C115962: X322508MLB4SI (8MHz crystal)

**Need Verification:**

- TLC555IDR: Need to search LCSC for correct code

---

## Cost-Benefit Analysis

**Total cost:** ~$3-5 for 80 pieces

**Is it worth it?**

**Order if:**

- You're doing all-SMD assembly
- You want to minimize board space
- You're building USB devices (need crystals)
- You want low-power 555 alternatives

**Skip if:**

- You're happy using through-hole for these components
- You don't mind larger PCBs
- Your MCU internal oscillator is good enough
- You can use MCU peripherals instead of 555 timers

**My Recommendation:**

- **Crystals:** Order these - cheap and essential for USB
- **Inductors:** Skip for now, use your through-hole until you need SMD
- **Logic ICs:** Skip, use through-hole or MCU GPIO
- **555 timers:** Skip, use MCU timers or through-hole NE555

---

## Storage & Organization

**Recommended labeling:**

- "Inductors 4020 SMD (4.7µH-22µH)"
- "Logic ICs SMD"
- "555 Timers SMD"
- "Crystals 8-16MHz"

**Storage:** Standard component storage, ESD precautions for ICs.
