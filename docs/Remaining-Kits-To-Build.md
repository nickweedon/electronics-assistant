# **Remaining kits to build**

\# \*\*Remaining kits to build\*\*

\#\# \*\*Complete SMD Component Assessment (Corrected)\*\*

\#\#\# \*\*What You're Planning to Buy (4 Lists)\*\*

| List | Parts | Package | Range | Coverage |
| \----- | \----- | \----- | \----- | \----- |
| \*\*Claude\_Resistors\_1\_percent\_unique\_qty25\*\* | 163 | 0805, 1/8W, 1% | 1Ω–10MΩ | ✅ Excellent |
| \*\*E24\_Resistors\_0806\_11M\_up\_5pct\_qty25\*\* | 21 | 0805, 1/8W, 5% | 11MΩ–82MΩ | ✅ Ultra-high R |
| \*\*E12\_Resistors\_1206\_Quarter\_Watt\*\* | 63 | 1206, 1/4W | 0Ω–1MΩ | ✅ Higher power |
| \*\*E24\_Capacitors\_Mixed\*\* | 68 | 0805/SMD | 10pF–470µF | ✅ Comprehensive |

\#\#\# \*\*Resistor Coverage Summary\*\*

| Range | 0805 1% (1/8W) | 0805 5% (1/8W) | 1206 (1/4W) |
| \----- | \----- | \----- | \----- |
| 1Ω–100Ω | ✅ Dense | — | ✅ E12 |
| 100Ω–1KΩ | ✅ Dense | — | ✅ E12 |
| 1KΩ–10KΩ | ✅ Dense | — | ✅ E12 |
| 10KΩ–100KΩ | ✅ Dense | — | ✅ E12 |
| 100KΩ–1MΩ | ✅ Dense | — | ✅ E12 |
| 1MΩ–10MΩ | ✅ Dense | — | — |
| 11MΩ–82MΩ | — | ✅ E24 | — |

\#\#\# \*\*Capacitor Coverage Summary\*\*

| Range | Dielectric | Voltage | Package |
| \----- | \----- | \----- | \----- |
| 10pF–10nF | C0G/NP0 | 50V | 0805 ✅ |
| 12nF–100nF | X7R | 50V | 0805 ✅ |
| 150nF–1µF | X7R | 50V | 0805 ✅ |
| 2.2µF–4.7µF | X7R | 50V | 0805 ✅ |
| 10µF | X7R | 50V | 1210 ✅ |
| 22µF–470µF | Polymer/Hybrid/Elec | 50V | SMD ✅ |

\*\*Your passive coverage is excellent\!\*\*

\---

\#\#\# \*\*Current PartsBox SMD Inventory\*\*

| Type | What You Have |
| \----- | \----- |
| Resistors | 4 values only (330Ω, 1K, 3.01K, 10K) |
| Capacitors | 0.1µF, 10µF, 22µF |
| \*\*MOSFETs\*\* | IRLML0030TRPBF (30V/5.3A) — \*\*only 1 type\*\* |
| \*\*Regulators\*\* | LM317EMP (adj), LMR51430 (buck) |
| \*\*Inductors\*\* | \*\*Through-hole axial:\*\* 4.7µH, 10µH, 22µH, 47µH, 100µH |
| MCU | PIC18F46K22-I/PT |
| Misc | Tactile switches, audio jack, DC jack, LEDs |

\---

\#\# \*\*🔴 Remaining Gaps (Active Components)\*\*

\#\#\# \*\*1. N-Channel MOSFETs (Variety) — HIGH PRIORITY\*\*

You have only 1 type. For your 12V/24V motor/solenoid/pump driving:

| Part | Package | Vds | Id | Rds(on) | Gate Threshold |
| \----- | \----- | \----- | \----- | \----- | \----- |
| AO3400A | SOT-23 | 30V | 5.7A | 26mΩ | 1.4V (logic-level) |
| SI2302CDS | SOT-23 | 20V | 2.6A | 50mΩ | 1.2V |
| IRLML6244 | SOT-23 | 20V | 6.3A | 21mΩ | 1V |
| \*\*For 24V/higher current:\*\* |  |  |  |  |  |
| AOD4184A | TO-252 | 40V | 50A | 4.5mΩ | 2.5V |

\*\*Qty:\*\* 10-20 each of 2-3 SOT-23 types

\---

\#\#\# \*\*2. SMD Schottky Diodes — HIGH PRIORITY\*\*

\*\*You have ZERO.\*\* Critical for flyback protection on inductive loads:

| Part | Package | Vrrm | If | Vf |
| \----- | \----- | \----- | \----- | \----- |
| SS14 | SMA | 40V | 1A | 0.5V |
| SS34 | SMA | 40V | 3A | 0.5V |
| B5819WS | SOD-323 | 40V | 1A | 0.45V |

\*\*Qty:\*\* 20-50 of SS14 or SS34

\---

\#\#\# \*\*3. Power Inductors — LOWER PRIORITY\*\*

\*\*You DO have through-hole inductors available\*\* (Abracon and Bourns axial inductors):
\- 4.7µH (77F4R7K-TR-RC)
\- 10µH (AICC-02-100K-T)
\- 22µH (AICC-02-220K-T)
\- 47µH (AICC-02-470K-T)
\- 100µH (AICC-02-101K-T)

These through-hole parts can be used with your LMR51430 buck converter using adapter boards or for through-hole prototypes. SMD power inductors (e.g., 4.7µH-22µH in 1210 or larger SMD packages) would be convenient for SMD-only boards but are no longer critical.

\*\*Qty (if ordering SMD):\*\* 5-10 each of 4.7µH and 10µH

\---

\#\#\# \*\*4. Fixed LDO Regulators — MEDIUM PRIORITY\*\*

| Part | Output | Package | Iout |
| \----- | \----- | \----- | \----- |
| AMS1117-3.3 | 3.3V | SOT-223 | 1A |
| AMS1117-5.0 | 5V | SOT-223 | 1A |
| AP2112K-3.3 | 3.3V | SOT-23-5 | 600mA |

\*\*Qty:\*\* 5-10 each

\---

\#\#\# \*\*5. SMD Signal Diodes — MEDIUM PRIORITY\*\*

| Part | Package | Use Case |
| \----- | \----- | \----- |
| 1N4148WS | SOD-323 | Fast switching |
| BAT54S | SOT-23 | Dual Schottky |

\*\*Qty:\*\* 20-50 of 1N4148WS

\---

\#\#\# \*\*6. SMD BJTs — LOWER PRIORITY\*\*

| Part | Type | Package |
| \----- | \----- | \----- |
| MMBT3904 | NPN | SOT-23 |
| MMBT3906 | PNP | SOT-23 |

\*\*Qty:\*\* 20-50 each

\---

\#\#\# \*\*7. P-Channel MOSFETs — LOWER PRIORITY\*\*

For high-side switching and reverse polarity protection:

| Part | Package | Vds | Id |
| \----- | \----- | \----- | \----- |
| AO3401A | SOT-23 | \-30V | \-4A |

\*\*Qty:\*\* 10-20

\---

\#\# \*\*Summary Table\*\*

| Priority | Category | Status | Action |
| \----- | \----- | \----- | \----- |
| ✅ DONE | 0805 Resistors 1% | Planned (163 values) | — |
| ✅ DONE | 0805 Resistors 5% 11M+ | Planned (21 values) | — |
| ✅ DONE | 1206 Resistors 1/4W | Planned (63 values) | — |
| ✅ DONE | Capacitors 10pF–470µF | Planned (68 values) | — |
| 🔴 HIGH | N-CH MOSFETs | Only 1 type | Add 2-3 varieties |
| 🔴 HIGH | Schottky Diodes | \*\*NONE\*\* | SS14, SS34, B5819WS |
| 🟢 LOW | Power Inductors | \*\*Have THT\*\* | Optional SMD upgrade |
| 🟡 MED | Fixed LDOs | Partial | AMS1117-3.3/5.0 |
| 🟡 MED | Signal Diodes | \*\*NONE\*\* | 1N4148WS |
| 🟢 LOW | SMD BJTs | \*\*NONE\*\* | MMBT3904/3906 |
| 🟢 LOW | P-CH MOSFETs | \*\*NONE\*\* | AO3401A |
