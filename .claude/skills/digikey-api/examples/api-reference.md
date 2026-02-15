# DigiKey API Reference

Complete field reference for all API responses.

## search.py

### keyword — POST /products/v4/search/keyword

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| Keywords | string | Yes | Search terms |
| Limit | int | No | Results per page, 1-50 (default: 10) |
| Offset | int | No | Starting index (default: 0) |
| ManufacturerId | string | No | Filter by manufacturer |
| CategoryId | string | No | Filter by category |
| SearchOptionList | string[] | No | Filters: LeadFree, RoHSCompliant, InStock |
| SortOptions.Field | string | No | Sort field (see below) |
| SortOptions.SortOrder | string | No | Ascending or Descending |

**Sort fields:** None, Packaging, ProductStatus, DigiKeyProductNumber,
ManufacturerProductNumber, Manufacturer, MinimumQuantity, QuantityAvailable,
Price, Supplier, PriceManufacturerStandardPackage

**Response:**

```json
{
  "Products": [{
    "ManufacturerProductNumber": "STM32F407VGT6",
    "UnitPrice": 12.50,
    "QuantityAvailable": 5000,
    "ProductUrl": "https://www.digikey.com/...",
    "DatasheetUrl": "https://...",
    "PhotoUrl": "https://...",
    "BackOrderNotAllowed": false,
    "NormallyStocking": true,
    "Discontinued": false,
    "EndOfLife": false,
    "Ncnr": false,
    "Description": {
      "ProductDescription": "IC MCU 32BIT 1MB FLASH 100LQFP",
      "DetailedDescription": "ARM Cortex-M4 STM32F4 Microcontroller..."
    },
    "Manufacturer": {"Id": 497, "Name": "STMicroelectronics"},
    "ProductStatus": {"Id": 0, "Status": "Active"},
    "ProductVariations": [{
      "DigiKeyProductNumber": "497-STM32F407VGT6-ND",
      "MinimumOrderQuantity": 1,
      "StandardPackage": 1,
      "QuantityAvailableforPackageType": 5000,
      "MarketPlace": false,
      "DigiReelFee": null,
      "PackageType": {"Id": 1, "Name": "Tray"},
      "StandardPricing": [
        {"BreakQuantity": 1, "UnitPrice": 12.50, "TotalPrice": 12.50},
        {"BreakQuantity": 10, "UnitPrice": 11.25, "TotalPrice": 112.50}
      ],
      "MyPricing": []
    }],
    "Category": {"CategoryId": 801, "Name": "Microcontrollers", "ParentId": 743},
    "Parameters": [
      {"ParameterId": 1, "ParameterText": "Core Processor", "ValueText": "ARM Cortex-M4"},
      {"ParameterId": 2, "ParameterText": "Flash Size", "ValueText": "1MB"}
    ]
  }],
  "ProductsCount": 150,
  "ExactMatches": [],
  "FilterOptions": {}
}
```

### product-details — GET /products/v4/search/{pn}/productdetails

Response wraps product data under `Product` key. Access with `--query 'Product.FieldName'`.

Top-level keys: `SearchLocaleUsed`, `Product`, `AccountIdUsed`, `CustomerIdUsed`.

The `Product` object has all keyword search fields plus:

| Field | Type | Description |
|---|---|---|
| DigiKeyPartNumber | string | DigiKey part number |
| ManufacturerPartNumber | string | Manufacturer part number |
| StandardPricing | array | Price tiers at product level |
| MinimumOrderQuantity | int | MOQ |
| StandardPackage | int | Standard package quantity |
| ReachStatus | string | REACH compliance |
| RohsStatus | string | RoHS compliance |
| LeadStatus | string | Lead-free status |
| HtsusCode | string | Harmonized tariff code |
| TariffDescription | string | Tariff description |
| Eccn | string | Export control number |

### substitutions — GET /products/v4/search/{pn}/substitutions

**Args:** `--product-number`, `--limit`

**Response:**

```json
{
  "Products": [{ /* same Product schema */ }],
  "ProductsCount": 5,
  "RequestedProductNumber": "497-STM32F407VGT6-ND"
}
```

### media — GET /products/v4/search/{pn}/media

**Response:**

```json
{
  "MediaLinks": [
    {"MediaType": "Product Photo", "Title": "...", "Url": "https://..."},
    {"MediaType": "Datasheet", "Title": "...", "Url": "https://..."}
  ],
  "DigiKeyPartNumber": "497-STM32F407VGT6-ND"
}
```

### manufacturers — GET /products/v4/search/manufacturers

**Response:**

```json
{
  "Manufacturers": [{"Id": 497, "Name": "STMicroelectronics"}, ...],
  "ManufacturersCount": 5000
}
```

### categories — GET /products/v4/search/categories[/{id}]

**Response:**

```json
{
  "Categories": [{
    "CategoryId": 801,
    "ParentId": 743,
    "Name": "Microcontrollers",
    "ProductCount": 15000,
    "NewProductCount": 200,
    "ImageUrl": null
  }],
  "CategoriesCount": 500
}
```

## pricing.py

### product — via GET /products/v4/search/{pn}/productdetails

Extracts pricing from product details. Calculates unit price for requested quantity.

**Args:** `--product-number`, `--quantity`, `--customer-id`, `--query`

**Response:**

```json
{
  "ManufacturerPartNumber": "SN74HC595N",
  "UnitPrice": 1.64,
  "QuantityAvailable": 15066,
  "RequestedQuantity": 10,
  "ProductUrl": "https://...",
  "Variations": [{
    "DigiKeyProductNumber": "296-1600-5-ND",
    "PackageType": "Tube",
    "MinimumOrderQuantity": 1,
    "StandardPackage": 1,
    "QuantityAvailableforPackageType": 15066,
    "CalculatedUnitPrice": 1.204,
    "ExtendedPrice": 12.04,
    "StandardPricing": [
      {"BreakQuantity": 1, "UnitPrice": 1.64, "TotalPrice": 1.64},
      {"BreakQuantity": 10, "UnitPrice": 1.204, "TotalPrice": 12.04},
      {"BreakQuantity": 25, "UnitPrice": 1.0936, "TotalPrice": 27.34}
    ],
    "MyPricing": []
  }]
}
```

### digi-reel — GET /products/v4/search/{pn}/digireelpricing

Falls back to product details if dedicated endpoint unavailable.

**Args:** `--product-number`, `--quantity` (required)

## lists.py

### get-all — GET /mylists/v1/lists

**Response:** Array of list objects:

```json
[{
  "Id": "1YUO179R33",
  "ListName": "My Components",
  "CreatedBy": "",
  "CustomerId": 13205640,
  "TotalParts": 25,
  "DateCreated": "2024-01-15T10:30:00Z",
  "DateLastAccessed": "2024-02-01T14:00:00Z",
  "Tags": [],
  "ListSettings": {"Visibility": "private", "PackagePreference": "cutTapeOrTR"},
  "CanEdit": true
}]
```

### create — POST /mylists/v1/lists

**Body:** `{"ListName": "...", "Tags": [...], "Source": "..."}`

**Response:** List ID string

### get — GET /mylists/v1/lists/{id}

Same as get-all item, optionally with `PartsList` if `--include-parts`.

### rename — PUT /mylists/v1/lists/{id}/listName/{name}

**Response:** 204 No Content (success message)

### delete — DELETE /mylists/v1/lists/{id}

**Response:** 204 No Content (success message)

## list_parts.py

### get-all — GET /mylists/v1/lists/{id}/parts

**Args:** `--list-id`, `--start-index`, `--limit`, `--include-attrition`

**Response:**

```json
{
  "TotalParts": 25,
  "PartsList": [{
    "PartId": 1942531,
    "UniqueId": "abc123def456",
    "CustomerReference": "R1",
    "ReferenceDesignator": "R1",
    "Notes": "",
    "MinOrderQty": 1,
    "MaxOrderQty": 0,
    "RequestedPartNumber": "296-8875-1-ND",
    "DigiKeyPartNumber": "296-8875-1-ND",
    "ManufacturerPartNumber": "SN74HC595N",
    "Manufacturer": "Texas Instruments",
    "Description": "IC SHIFT REGISTER 8BIT 16DIP",
    "PartStatus": "Active",
    "PartStatusCode": "0",
    "Availability": "In Stock",
    "QuantityAvailable": 45000,
    "SelectedQuantityIndex": 0,
    "Attrition": 0,
    "VendorLeadWeeks": 0,
    "PartDetailUrl": "https://...",
    "PrimaryDatasheetUrl": "https://...",
    "ImageUrl": "https://...",
    "ThumbnailUrl": "https://...",
    "Category": "Logic - Shift Registers",
    "Quantities": [{
      "QuantityRequested": 10,
      "CalculatedQuantity": 10,
      "TargetPrice": null,
      "SelectedPackType": "Tube",
      "IsInactive": false,
      "PackOptions": [{
        "PartId": 1942531,
        "DigiKeyPartNumber": "296-8875-1-ND",
        "Quantity": 10,
        "PackType": "Tube",
        "QuantityAvailable": 45000,
        "MinimumOrderQuantity": 1,
        "CalculatedUnitPrice": 0.56,
        "ExtendedPrice": 5.60,
        "BreakPrice": 0.56,
        "BreakQuantity": 1,
        "IsUpsell": false,
        "FormattedUnitPrice": "$0.56",
        "FormattedExtendedPrice": "$5.60"
      }]
    }],
    "Flags": {
      "NonStock": false,
      "IsNCNR": false,
      "IsMatched": true,
      "IsMarketPlace": false,
      "BoNotAllowed": false,
      "IsEditable": true
    },
    "Substitutes": [],
    "AlternateParts": [],
    "ReachStatus": "REACH Unaffected",
    "RohsStatusMessage": "RoHS Compliant",
    "Eccn": "EAR99",
    "CountryOfOrigin": "CN"
  }]
}
```

### add — POST /mylists/v1/lists/{id}/parts

**Body:** Array of part objects:

```json
[{
  "RequestedPartNumber": "296-8875-1-ND",
  "CustomerReference": "R1",
  "ReferenceDesignator": "R1",
  "Notes": "8-bit shift register",
  "Quantities": [{"Quantity": 10}]
}]
```

**Response:** Array of UniqueId strings

### get — GET /mylists/v1/lists/{id}/parts/{partId}

Same schema as single item in get-all PartsList.

### update — PUT /mylists/v1/lists/{id}/parts/{partId}

**Body:** Fields to update (CustomerReference, Notes, etc.)

**Response:** Updated part object

### delete — DELETE /mylists/v1/lists/{id}/parts/{partId}

**Response:** 204 No Content (success message)

## auth.py

### status

Shows: client_id_set, client_secret_set, environment, client_token validity,
user_token status, refresh_token status, token age.

### refresh

Force-refreshes the user OAuth token using the stored refresh token.

### login-url

Generates the OAuth authorization URL for browser-based login.

### set-tokens

Saves user_token and refresh_token to the token file.

**Args:** `--user-token`, `--refresh-token`
