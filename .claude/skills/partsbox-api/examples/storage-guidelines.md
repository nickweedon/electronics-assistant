# Storage Location Guidelines

Follow these guidelines when recommending storage locations for components during stock-in or inventory organization.

## SMD Box Usage (type_smd-box)

**RESERVED FOR:** Small SMD components and PCB-mounted parts that fit in small compartments.

**Appropriate for:**

- SMD resistors (0402, 0603, 0805, 1206, etc.)
- SMD capacitors (ceramic, tantalum)
- SMD inductors and ferrite beads
- Small SMD ICs (SOT23, SOT89, SOT223, SOIC, TSSOP)
- SMD LEDs and diodes
- Small SMD transistors and MOSFETs

**NOT appropriate for:**

- Adapter boards (even if they're for SMD packages - use drawer cabinets instead)
- Through-hole components
- Modules or breakout boards
- Large components (>5mm per side)
- Cylindrical components (motors, batteries)

**Reason:** SMD boxes have small compartments (~18mm x 16mm) designed for hundreds of tiny SMD parts. Adapter boards and larger items waste space and belong in drawer cabinets or StowAway boxes.

## ESD-Safe SMD Box Usage (type_smd-box + esd_yes)

**RESERVED FOR:** ESD-sensitive components that are ALSO small enough for SMD boxes (same size constraints as regular SMD boxes).

**Appropriate for:**

- ESD-sensitive SMD ICs (microcontrollers, processors, memory chips)
- CMOS logic ICs in SMD packages
- RF/wireless ICs in SMD packages
- High-speed interface ICs (USB, HDMI, Ethernet PHYs)
- Precision analog ICs (ADCs, DACs, op-amps with CMOS inputs)

**NOT appropriate for:**

- Non-sensitive passive components (resistors, capacitors, LEDs)
- Large ICs or modules (use ESD-safe drawer cabinets)
- Through-hole components
- Adapter boards (not ESD-sensitive - they're just PCBs with pads)

**Reason:** ESD-safe SMD boxes are premium storage (limited quantity) reserved for ESD-sensitive SMD ICs. Use regular SMD boxes for passives and non-ESD drawer storage for larger items.

## Drawer Cabinet Usage (type_drawer-cabinet)

**APPROPRIATE FOR:**

- Adapter boards (SMD-to-DIP converters, breakout boards)
- Through-hole components (resistors, capacitors, ICs)
- Medium-sized modules and dev boards
- Connectors and headers
- Prototype supplies (perfboard, breadboards)

**Example storage assignments:**

- All SMD-to-DIP adapters → Large drawer (grouped together for PCB work)
- Through-hole voltage regulators → Standard drawer
- Arduino shields and modules → Standard drawer

## StowAway Box Usage (type_plano-stowaway)

**APPROPRIATE FOR:**

- Cylindrical components (motors, batteries, solenoids)
- Large irregular-shaped items
- Development boards (Raspberry Pi, Arduino)
- Bulky connectors and cables
- Tools and accessories

**Example storage assignments:**

- Vibration motors → StowAway compartment (use dividers to separate types)
- Stepper motors → StowAway compartment
- Battery packs → StowAway compartment

## Storage Decision Examples

### Example 1: SC-70/SOT23 SMD-to-DIP Adapter Boards (5 pcs)

- Component type: Adapter board (PCB with pads)
- Size: ~20mm x 15mm
- ESD-sensitive? NO (passive PCB)
- SMD box? **NO** - Adapter boards are NOT small SMD components
- Recommendation: **Drawer cabinet** (large drawer to group all adapters together)

### Example 2: 0805 Ceramic Capacitors (300 pcs)

- Component type: SMD capacitor
- Size: 2.0mm x 1.25mm (0805 package)
- ESD-sensitive? NO (passive component)
- SMD box? **YES** - Perfect fit for SMD box compartments
- Recommendation: **Regular SMD box** (type_smd-box, esd_no)

### Example 3: ATtiny85 Microcontroller in SOIC-8 (10 pcs)

- Component type: SMD IC (microcontroller)
- Size: 5.0mm x 4.0mm (SOIC-8 package)
- ESD-sensitive? YES (CMOS IC)
- SMD box? **YES** - Fits in SMD box compartments
- Recommendation: **ESD-safe SMD box** (type_smd-box, esd_yes)

### Example 4: Vibration Motors 10mm dia (6 pcs)

- Component type: Cylindrical motor
- Size: 10mm diameter x 3mm thick
- ESD-sensitive? NO (electromechanical)
- SMD box? **NO** - Cylindrical shape doesn't fit well in rectangular compartments
- Recommendation: **StowAway box** (type_plano-stowaway with dividers)

### Example 5: QFP-64 to DIP Adapter Board (1 pc)

- Component type: Adapter board (large)
- Size: ~50mm x 50mm
- ESD-sensitive? NO (passive PCB)
- SMD box? **NO** - Far too large, and it's an adapter board
- Recommendation: **Drawer cabinet** (large drawer with other adapters)
