# Electronics Assistant

An AI assistant workspace configured to help with hobby electronics projects, PCB design, and component inventory management.

## Overview

This workspace provides specialized assistance for electronics enthusiasts working on small PCB designs with microcontrollers, dual power bus systems (12V/24V and 3.3V/5V rails), and typical hobby electronics components.

## Features

- **Component Inventory Management**: Integration with PartsBox for tracking on-hand components
- **Parts Ordering**: DigiKey MyLists integration for managing active orders
- **Smart Search**: JMESPath-powered queries for finding components by specifications
- **Documentation**: Google Docs integration for maintaining project documentation and references

## Quick Start

1. Review [CLAUDE.md](CLAUDE.md) for the assistant's role and terminology
2. Explore the [docs/](docs/) folder for detailed guidelines on using various MCP servers
3. Reference the inventory summaries to understand available components

## Documentation

### MCP Server Guidelines

- [Digikey MCP Server Guidelines](docs/Digikey-MCP-Server-Guidelines.md) - Rules for searching, ordering, and building component kits
- [PartsBox MCP Server Guidelines](docs/PartsBox-MCP-Server-Guidelines.md) - Inventory management best practices
- [Google Docs MCP Server Guidelines](docs/Google-Docs-MCP-Server-Guidelines.md) - Documentation standards
- [Using JMESPath](docs/Using-JMESPath.md) - Query syntax and filtering techniques

### Inventory & Planning

- [PartsBox Through-Hole Summary](docs/PartsBox-Through-Hole-Summary.md) - Current through-hole component inventory
- [Remaining Kits To Build](docs/Remaining-Kits-To-Build.md) - SMD component gaps and priorities
- [Active Lists Summary](docs/Active-Lists-Summary.md) - Contents of active DigiKey lists

## Terminology

- **Stock/Items on hand**: Components tracked in PartsBox inventory
- **Items to order/buy**: Components in active DigiKey MyLists
- **`ref_` lists**: Archived DigiKey reference lists (not for active purchasing)
- **Active lists**: DigiKey lists containing items intended for purchase

## Typical Project Context

Projects typically involve:
- Small PCB designs with microcontrollers
- Dual power bus design (12V/24V for motors/pumps/solenoids + 3.3V/5V for logic)
- Power conversion using linear regulators or buck converters
- Mix of through-hole and SMD components

## Current Inventory Status

### Through-Hole (THT)
- ✅ Excellent coverage: resistors, capacitors, basic logic ICs
- ✅ Good selection: diodes, microcontrollers (PIC)
- ⚠️ Basic: transistors, linear ICs, regulators

### SMD Components
- ✅ Planned: Comprehensive resistor kits (0805 1%, 1206 1/4W)
- ✅ Planned: Capacitor kit (10pF-470µF)
- 🔴 High Priority Gaps: N-channel MOSFETs (variety), Schottky diodes
- 🟡 Medium Priority: Fixed LDO regulators, signal diodes
- 🟢 Lower Priority: BJTs, P-channel MOSFETs, SMD power inductors

## MCP Servers

This workspace uses several MCP (Model Context Protocol) servers:

- **DigiKey MCP Server**: Component search and MyLists management
- **PartsBox MCP Server**: Inventory tracking and stock management
- **Google Docs MCP Server**: Documentation and reference materials
- **Playwright MCP Server**: Web automation for dynamic content

## Best Practices

1. **Search Strategy**: Use broad keyword searches with JMESPath filtering rather than many specific queries
2. **Component Selection**: Prioritize low cost and availability
3. **Stock Verification**: Ensure parts are in stock with sufficient quantity before ordering
4. **Batch Operations**: Limit API calls to ≤200 items for performance
5. **Permission**: Always ask before modifying lists or performing non-read-only operations

## Contributing

This is a personal workspace. Guidelines and documentation are maintained in the [docs/](docs/) folder and synced with Google Drive.
