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
            product_type: "Finished Good (FG)"
            bm_production_line: "L01 - L1 COATINGS"
            bm_production_line_code: "L01"
            fg_production_line: "L01 - L1 COATINGS"
            fg_production_line_code: "L01"
            activities:
              - type: "Labor"
                item_id: "L01 LABELING/CODING"
                activities: "L01 LABELING/CODING"
                class: "DL"
                class_1: "DL"
                pax: 1
                machine: 1
                time_min: 0.1245
              - type: "Labor"
                item_id: "L01 FILLING"
                activities: "L01 FILLING"
                class: "DL"
                class_1: "DL"
                pax: 2
                machine: 1
                time_min: 0.1499
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
            SELECT inventory_id, revision_descr, revision, notes, product_type,
                   bm_production_line, bm_production_line_code,
                   fg_production_line, fg_production_line_code
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
            SELECT type, item_id, activity_name AS activities,
                   class, class_1, pax, machine, time_min
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
              product_type: "Finished Good (FG)"
              bm_production_line: "L01 - L1 COATINGS"
              bm_production_line_code: "L01"
              fg_production_line: "L01 - L1 COATINGS"
              fg_production_line_code: "L01"
    """
    q = request.args.get("q", "").strip()
    limit = request.args.get("limit", 50, type=int)

    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        if q:
            cur.execute(
                """
                SELECT inventory_id, revision_descr, revision, product_type,
                       bm_production_line, bm_production_line_code,
                       fg_production_line, fg_production_line_code
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
                SELECT inventory_id, revision_descr, revision, product_type,
                       bm_production_line, bm_production_line_code,
                       fg_production_line, fg_production_line_code
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
@app.get("/api/production-lines")
def get_production_lines():
    """
    List all production lines and their activities
    ---
    tags:
      - Production Lines
    responses:
      200:
        description: List of production lines with associated activities
        examples:
          application/json:
            - production_line_code: "L01"
              production_line_name: "L01 - L1 COATINGS"
              activities:
                - activity_name: "L01 MIXING"
                  sort_order: 1
                - activity_name: "L01 MILLING"
                  sort_order: 2
            - production_line_code: "L02"
              production_line_name: "L02 - L2 COATINGS"
              activities:
                - activity_name: "L02 FILLING"
                  sort_order: 1
    """
    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        # 1. Pull all production lines
        cur.execute(
            """
            SELECT production_line_code, production_line_name
            FROM production_lines
            ORDER BY production_line_code
            """
        )
        lines = cur.fetchall()

        # 2. Pull all line activities
        cur.execute(
            """
            SELECT production_line_code, activity_name, sort_order
            FROM line_activities
            ORDER BY production_line_code, sort_order
            """
        )
        activities = cur.fetchall()

        # 3. Group activities under their line
        line_map = {}
        for line in lines:
            code = line["production_line_code"]
            line_map[code] = {
                "production_line_code": code,
                "production_line_name": line["production_line_name"],
                "activities": [],
            }

        for act in activities:
            code = act["production_line_code"]
            if code in line_map:
                line_map[code]["activities"].append(
                    {
                        "activity_name": act["activity_name"],
                        "sort_order": act["sort_order"],
                    }
                )

        return jsonify(list(line_map.values()))
    finally:
        conn.close()


@app.get("/api/production-lines/<line_code>")
def get_production_line(line_code):
    """
    Get a single production line and its activities
    ---
    tags:
      - Production Lines
    parameters:
      - name: line_code
        in: path
        type: string
        required: true
        description: Production line code (case-insensitive)
        example: L01
    responses:
      200:
        description: Production line details with activities
        examples:
          application/json:
            production_line_code: "L01"
            production_line_name: "L01 - L1 COATINGS"
            activities:
              - activity_name: "L01 MIXING"
                sort_order: 1
              - activity_name: "L01 MILLING"
                sort_order: 2
      404:
        description: Production line not found
        examples:
          application/json: {"error": "Production line not found", "line_code": "L99"}
    """
    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        cur.execute(
            """
            SELECT production_line_code, production_line_name
            FROM production_lines
            WHERE UPPER(production_line_code) = UPPER(%s)
            """,
            (line_code,),
        )
        line = cur.fetchone()

        if line is None:
            return (
                jsonify(
                    {
                        "error": "Production line not found",
                        "line_code": line_code,
                    }
                ),
                404,
            )

        cur.execute(
            """
            SELECT activity_name, sort_order
            FROM line_activities
            WHERE UPPER(production_line_code) = UPPER(%s)
            ORDER BY sort_order
            """,
            (line_code,),
        )
        activities = cur.fetchall()

        result = dict(line)
        result["activities"] = [dict(a) for a in activities]

        return jsonify(result)
    finally:
        conn.close()
        
        
from flask import request  # make sure this is already imported

@app.put("/api/production-lines/<line_code>")
def update_production_line(line_code):
    """
    Replace a production line and its activities atomically
    ---
    tags:
      - Production Lines
    parameters:
      - name: line_code
        in: path
        type: string
        required: true
        description: Existing production line code
        example: L01
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            production_line_name:
              type: string
              example: "Line 01 COATINGS"
            activities:
              type: array
              items:
                type: object
                properties:
                  activity_name:
                    type: string
                  sort_order:
                    type: integer
                  stage:
                    type: string
                    enum: [BM, FG]
              example:
                - activity_name: "MIXING"
                  sort_order: 1
                  stage: "BM"
                - activity_name: "FILLING"
                  sort_order: 2
                  stage: "FG"
    responses:
      200:
        description: Line updated
        examples:
          application/json: {"message": "Production line updated", "line_code": "L01", "activities": 11}
      404:
        description: Line not found
      400:
        description: Invalid JSON
    """
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    new_name = body.get("production_line_name")
    activities = body.get("activities", [])

    conn = get_connection()
    try:
        cur = get_dict_cursor(conn)

        # 1. Verify line exists
        cur.execute(
            "SELECT production_line_code FROM production_lines WHERE UPPER(production_line_code) = UPPER(%s)",
            (line_code,),
        )
        if cur.fetchone() is None:
            return jsonify({"error": "Production line not found", "line_code": line_code}), 404

        # 2. Update line name (if provided)
        if new_name:
            cur.execute(
                "UPDATE production_lines SET production_line_name = %s WHERE production_line_code = %s",
                (new_name, line_code),
            )

        # 3. Atomic replacement of activities
        cur.execute(
            "DELETE FROM line_activities WHERE production_line_code = %s",
            (line_code,),
        )
        for act in activities:
            cur.execute(
                """
                INSERT INTO line_activities
                    (production_line_code, activity_name, sort_order, stage)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    line_code,
                    act.get("activity_name"),
                    act.get("sort_order"),
                    act.get("stage"),
                ),
            )

        conn.commit()
        return jsonify({
            "message": "Production line updated",
            "line_code": line_code,
            "activities": len(activities),
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)