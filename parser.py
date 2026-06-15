"""
ACU Routing Parser
-------------------
Reads the FY26_ACU_Routing.xlsx "Routing" sheet, applies the required
filters, drops the unneeded columns, and groups everything by Inventory ID
(with the per-activity rows nested underneath).

Filters applied:
    - Type        == "Labor"
    - CLASS       == "DL"
    - CLASS.1     == "DL"

Columns dropped:
    - BOM ID        (always identical to Inventory ID, so redundant)
    - Status
    - UOM           (always "MIN" for this filtered set)

Output structure (dict keyed by Inventory ID):

{
    "1AF2202L": {
        "inventory_id": "1AF2202L",
        "revision_descr": "PG ANTI FOULING PAINT RED 4L",
        "revision": "03",
        "notes": "CRN RD23-CR055",
        "production_line": "L01 - L1 COATINGS",
        "production_line_code": "L01",
        "activities": [
            {
                "type": "Labor",
                "item_id": "L01 LABELING/CODING",
                "qty_required": 0.1245,
                "activities": "L01 LABELING/CODING",
                "class": "DL",
                "class_1": "DL"
            },
            ...
        ]
    },
    ...
}

Notes:
    - "Item ID" and "ACTIVITIES" are always identical in the source data
      but both are kept since the user listed both.
    - There are TWO "Production Line" columns in the source (Production
      Line / Production Line.1, which pandas reads as "Production Line"
      and "Production Line.1"). Both are kept, but lifted up to the
      PRODUCT level (one per Inventory ID) since they are always the
      same across all activities for a given item code:
          production_line       -> the descriptive one  (e.g. "L01 - L1 COATINGS")
          production_line_code  -> the short code one    (e.g. "L01")
"""

import json
import math
from pathlib import Path

import pandas as pd


SOURCE_COLUMNS = [
    "Inventory ID",
    "Revision Descr.",
    "Revision",
    "Notes",
    "Type",
    "Item ID",
    "Qty Required",
    "ACTIVITIES",
    "Production Line",
    "Production Line.1",
    "CLASS",
    "CLASS.1",
]

# Fields that describe the PRODUCT (one value per Inventory ID)
PRODUCT_FIELDS = {
    "Inventory ID": "inventory_id",
    "Revision Descr.": "revision_descr",
    "Revision": "revision",
    "Notes": "notes",
    "Production Line": "production_line",
    "Production Line.1": "production_line_code",
}

# Fields that describe an ACTIVITY (one row per labor step)
ACTIVITY_FIELDS = {
    "Type": "type",
    "Item ID": "item_id",
    "Qty Required": "qty_required",
    "ACTIVITIES": "activities",
    "CLASS": "class",
    "CLASS.1": "class_1",
}


def _clean(value):
    """Convert pandas/NumPy values into plain JSON-friendly Python values."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    return value


def parse_acu_routing(filepath: str) -> dict:
    """Parse the ACU routing workbook into a dict keyed by Inventory ID."""
    df = pd.read_excel(filepath, sheet_name="Routing")

    # 1. Filter: Type == Labor, CLASS == DL, CLASS.1 == DL
    filtered = df[
        (df["Type"] == "Labor")
        & (df["CLASS"] == "DL")
        & (df["CLASS.1"] == "DL")
    ]

    # 2. Keep only the columns we care about
    filtered = filtered[SOURCE_COLUMNS]

    # 3. Group by Inventory ID
    result: dict = {}
    for _, row in filtered.iterrows():
        inv_id = row["Inventory ID"]

        if inv_id not in result:
            product = {
                new_key: _clean(row[old_key])
                for old_key, new_key in PRODUCT_FIELDS.items()
            }
            product["activities"] = []
            result[inv_id] = product

        activity = {
            new_key: _clean(row[old_key])
            for old_key, new_key in ACTIVITY_FIELDS.items()
        }
        result[inv_id]["activities"].append(activity)

    return result


if __name__ == "__main__":
    SOURCE_FILE = "FY26_ACU_Routing.xlsx"
    OUTPUT_FILE = "./output/acu_routing_parsed.json"

    data = parse_acu_routing(SOURCE_FILE)

    print(f"Parsed {len(data)} unique inventory IDs")
    total_activities = sum(len(v["activities"]) for v in data.values())
    print(f"Total activity rows: {total_activities}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved to {OUTPUT_FILE}")

    # show one sample with multiple activities
    sample_key = next(k for k, v in data.items() if len(v["activities"]) > 1)
    print("\nSample entry:")
    print(json.dumps({sample_key: data[sample_key]}, indent=2))