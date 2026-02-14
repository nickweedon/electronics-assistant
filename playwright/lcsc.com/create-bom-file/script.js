#!/usr/bin/env node

/**
 * LCSC Create BOM File
 * Generate LCSC BOM CSV file from part codes and quantities
 *
 * Parameters:
 * - input: JSON file with parts array OR inline JSON string (required)
 * - output: Output CSV file path (required)
 * - useLcscCodes: If true, treat input as LCSC codes; if false, treat as MPNs (default: false)
 *
 * Alternatively:
 * - parts: Comma-separated list of PART:QTY (e.g., "C137394:100,C1525:50")
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = {};
process.argv.slice(2).forEach(arg => {
  const [key, value] = arg.replace('--', '').split('=');
  args[key] = value;
});

const inputFile = args.input;
const outputFile = args.output;
const useLcscCodes = args.useLcscCodes === 'true' || args.lcscCodes === 'true';
const partsArg = args.parts;

if (!outputFile) {
  console.error('[ERROR] output parameter is required');
  console.error('Usage: node script.js --input=parts.json --output=bom.csv [--useLcscCodes=false]');
  console.error('   or: node script.js --parts="C137394:100,C1525:50" --output=bom.csv --useLcscCodes=true');
  process.exit(1);
}

if (!inputFile && !partsArg) {
  console.error('[ERROR] Either --input or --parts parameter is required');
  console.error('Usage: node script.js --input=parts.json --output=bom.csv');
  console.error('   or: node script.js --parts="C137394:100,C1525:50" --output=bom.csv');
  process.exit(1);
}

/**
 * Parse item specification in format CODE or CODE:QTY
 */
function parseItemSpec(spec, defaultQty = 100) {
  spec = spec.trim();
  if (spec.includes(':')) {
    const [code, qtyStr] = spec.split(':', 2);
    return { partNumber: code.trim(), quantity: parseInt(qtyStr.trim()) };
  } else {
    return { partNumber: spec, quantity: defaultQty };
  }
}

/**
 * Generate CSV content
 */
function generateBomCsv(parts, useLcscCodes) {
  const lines = [];

  // Header row (matching LCSC BOM template)
  const headers = [
    'Quantity',
    'Manufacture Part Number',
    'Manufacturer(optional)',
    'Description(optional)',
    'LCSC Part Number(optional)',
    'Package(optional)',
    'Customer Part Number(optional)',
    '',
    ''
  ];

  lines.push(headers.join(','));

  // Data rows
  for (const part of parts) {
    const row = new Array(9).fill('');
    row[0] = part.quantity;

    if (useLcscCodes) {
      // Populate LCSC Part Number column (column 4, index 4)
      row[4] = part.partNumber;
    } else {
      // Populate Manufacture Part Number column (column 1, index 1)
      row[1] = part.partNumber;
    }

    lines.push(row.join(','));
  }

  return lines.join('\n');
}

/**
 * Main execution
 */
async function main() {
  const startTime = Date.now();

  try {
    let parts = [];

    // Load parts from input
    if (inputFile) {
      console.error(`[INFO] Loading parts from ${inputFile}...`);

      const inputContent = fs.readFileSync(inputFile, 'utf8');
      let parsedInput;

      try {
        parsedInput = JSON.parse(inputContent);
      } catch (e) {
        console.error(`[ERROR] Failed to parse JSON from ${inputFile}: ${e.message}`);
        process.exit(1);
      }

      // Handle different input formats
      if (Array.isArray(parsedInput)) {
        // Array of objects with partNumber/lcscCode and quantity
        parts = parsedInput.map(item => ({
          partNumber: item.partNumber || item.lcscCode || item.code || item.mpn || '',
          quantity: item.quantity || item.qty || 100
        }));
      } else if (typeof parsedInput === 'object') {
        // Single object
        parts = [{
          partNumber: parsedInput.partNumber || parsedInput.lcscCode || parsedInput.code || '',
          quantity: parsedInput.quantity || parsedInput.qty || 100
        }];
      } else {
        console.error('[ERROR] Input must be a JSON array or object');
        process.exit(1);
      }
    } else if (partsArg) {
      // Parse from --parts argument
      console.error(`[INFO] Parsing parts from command line...`);
      const partSpecs = partsArg.split(',');
      parts = partSpecs.map(spec => parseItemSpec(spec));
    }

    if (parts.length === 0) {
      console.error('[ERROR] No parts found in input');
      process.exit(1);
    }

    console.error(`[INFO] Processing ${parts.length} parts...`);

    // Generate CSV content
    const csvContent = generateBomCsv(parts, useLcscCodes);

    // Ensure output directory exists
    const outputDir = path.dirname(outputFile);
    if (outputDir && outputDir !== '.') {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Write CSV file
    fs.writeFileSync(outputFile, csvContent, 'utf8');

    const duration = Date.now() - startTime;

    console.error(`[INFO] BOM file created: ${outputFile}`);
    console.error(`[INFO] Total parts: ${parts.length}`);

    // Output structured JSON result
    const result = {
      success: true,
      data: {
        outputFile: path.resolve(outputFile),
        partCount: parts.length,
        useLcscCodes: useLcscCodes,
        parts: parts
      },
      metadata: {
        timestamp: new Date().toISOString(),
        duration: duration
      }
    };

    console.log(JSON.stringify(result, null, 2));

  } catch (error) {
    console.error(`[ERROR] ${error.message}`);

    const duration = Date.now() - startTime;

    // Output error as JSON
    const errorResult = {
      success: false,
      data: null,
      metadata: {
        timestamp: new Date().toISOString(),
        duration: duration
      },
      error: {
        message: error.message,
        stack: error.stack
      }
    };

    console.log(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

// Run main function
main().catch(error => {
  console.error(`[FATAL] ${error.message}`);
  process.exit(1);
});
