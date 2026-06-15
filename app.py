"""
ACU Routing API
---------------
Simple Flask API for looking up routing/activity data by item code.

No authentication - for local testing with Postman only.

Run:
    python app.py

Main endpoint:
    GET /api/items/<item_code>
        -> returns the product info + nested list of activities

Other endpoints:
    GET /api/health
        -> simple health check
    GET /api/items?q=<search term>
        -> browse/search item codes (partial match on inventory_id
           or revision_descr), useful for finding a valid item code
           to test with
"""

from flasgger import Swagger
from flask import Flask, jsonify, request

from db import get_connection, get_dict_cursor

app = Flask(__name__)

app.config["SWAGGER"] = {
    "title": "ACU Routing API",
    "uiversion": 3,
    "specs_route": "/docs/",
}
swagger = Swagger(app)


@app.get("/api/health")
def health():
    """
    Health check
    ---
    tags:
      - Health
    responses:
      200:
        description: API is up
        examples:
          application/json: {"status": "ok"}
    """
    return jsonify({"status": "ok"})


@app.get("/api/items/<item_code>")
def get_item(item_code):
    """
    Look up an item code's routing details
    ---
    tags:
      - Items
    parameters:
      - name: item_code
        in: path
        type: string
        required: true
        description: The inventory ID / item code (case-insensitive)
        example: 1AF2202L
    responses:
      200:
        description: Routing details for the item, including activities
        examples:
          application/json:
            inventory_id: "1AF2202L"
            revision_descr: "PG ANTI FOULING PAINT RED 4L"
            revision: "03"
            notes: "CRN RD23-CR055"
            production_line: "L01 - L1 COATINGS"
            production_line_code: "L01"
            activities:
              - type: "Labor"
                item_id: "L01 LABELING/CODING"
                qty_required: 0.1245
                activities: "L01 LABELING/CODING"
                class: "DL"
                class_1: "DL"
              - type: "Labor"
                item_id: "L01 FILLING"
                qty_required: 0.1499
                activities: "L01 FILLING"
                class: "DL"
                class_1: "DL"
      404:
        description: Item code not found
        examples:
          application/json: {"error": "Item code not found", "item_code": "xxxxx"}
    """
    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        # Case-insensitive exact match on inventory_id
        cur.execute(
            """
            SELECT inventory_id, revision_descr, revision, notes,
                   production_line, production_line_code
            FROM products
            WHERE UPPER(inventory_id) = UPPER(%s)
            """,
            (item_code,),
        )
        product = cur.fetchone()

        if product is None:
            return (
                jsonify(
                    {
                        "error": "Item code not found",
                        "item_code": item_code,
                    }
                ),
                404,
            )

        cur.execute(
            """
            SELECT type, item_id, qty_required, activity_name AS activities,
                   class, class_1
            FROM activities
            WHERE inventory_id = %s
            ORDER BY sort_order
            """,
            (product["inventory_id"],),
        )
        activities = cur.fetchall()

        result = dict(product)
        result["activities"] = [dict(a) for a in activities]

        return jsonify(result)
    finally:
        conn.close()


@app.get("/api/items")
def search_items():
    """
    Browse / search item codes
    ---
    tags:
      - Items
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Partial, case-insensitive match on inventory_id or revision_descr
        example: woodglue
      - name: limit
        in: query
        type: integer
        required: false
        default: 50
        description: Max number of results
    responses:
      200:
        description: List of matching items (summary, no activities)
        examples:
          application/json:
            - inventory_id: "1AF2202L"
              revision_descr: "PG ANTI FOULING PAINT RED 4L"
              revision: "03"
              production_line: "L01 - L1 COATINGS"
              production_line_code: "L01"
    """
    q = request.args.get("q", "").strip()
    limit = request.args.get("limit", 50, type=int)

    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        if q:
            cur.execute(
                """
                SELECT inventory_id, revision_descr, revision,
                       production_line, production_line_code
                FROM products
                WHERE inventory_id ILIKE %s OR revision_descr ILIKE %s
                ORDER BY inventory_id
                LIMIT %s
                """,
                (f"%{q}%", f"%{q}%", limit),
            )
        else:
            cur.execute(
                """
                SELECT inventory_id, revision_descr, revision,
                       production_line, production_line_code
                FROM products
                ORDER BY inventory_id
                LIMIT %s
                """,
                (limit,),
            )

        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)