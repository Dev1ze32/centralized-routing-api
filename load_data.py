"""
Load Data
---------
Creates the schema (if not already created) and loads
acu_routing_parsed.json into the products / activities tables.

Usage:
    python load_data.py [path_to_json]

If no path is given, defaults to "acu_routing_parsed.json" in the
current directory.
"""

import json
import sys
from pathlib import Path

from db import get_connection

DEFAULT_JSON_PATH = "./output/acu_routing_parsed.json"
SCHEMA_PATH = "schema.sql"


def create_schema(conn):
    schema_sql = Path(SCHEMA_PATH).read_text()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("Schema created (existing tables dropped & recreated).")


def load_json(conn, json_path: str):
    with open(json_path) as f:
        data = json.load(f)

    with conn.cursor() as cur:
        for inventory_id, product in data.items():
            cur.execute(
                """
                INSERT INTO products
                    (inventory_id, revision_descr, revision, notes,
                     production_line, production_line_code)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (inventory_id) DO UPDATE SET
                    revision_descr = EXCLUDED.revision_descr,
                    revision = EXCLUDED.revision,
                    notes = EXCLUDED.notes,
                    production_line = EXCLUDED.production_line,
                    production_line_code = EXCLUDED.production_line_code
                """,
                (
                    inventory_id,
                    product.get("revision_descr"),
                    product.get("revision"),
                    product.get("notes"),
                    product.get("production_line"),
                    product.get("production_line_code"),
                ),
            )

            # Clear out any previously loaded activities for this item
            # (keeps re-runs idempotent)
            cur.execute(
                "DELETE FROM activities WHERE inventory_id = %s",
                (inventory_id,),
            )

            for order, activity in enumerate(product.get("activities", [])):
                cur.execute(
                    """
                    INSERT INTO activities
                        (inventory_id, type, item_id, qty_required,
                         activity_name, class, class_1, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        inventory_id,
                        activity.get("type"),
                        activity.get("item_id"),
                        activity.get("qty_required"),
                        activity.get("activities"),
                        activity.get("class"),
                        activity.get("class_1"),
                        order,
                    ),
                )

    conn.commit()
    print(f"Loaded {len(data)} products from {json_path}")


def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON_PATH

    conn = get_connection()
    try:
        create_schema(conn)
        load_json(conn, json_path)
    finally:
        conn.close()


if __name__ == "__main__":
    main()