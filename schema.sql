-- ============================================================
-- ACU Routing Schema
-- ============================================================
-- Mirrors the structure of acu_routing_parsed.json:
--   - one row per item code (inventory_id)  -> products
--   - one row per labor activity            -> activities
-- ============================================================

DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS products;

-- One row per item code (the "product level" fields from the JSON)
CREATE TABLE products (
    inventory_id           VARCHAR(50) PRIMARY KEY,
    revision_descr         TEXT,
    revision                VARCHAR(10),
    notes                   TEXT,
    production_line         TEXT,
    production_line_code   VARCHAR(20)
);

-- One row per labor activity, linked back to its product
CREATE TABLE activities (
    id              SERIAL PRIMARY KEY,
    inventory_id   VARCHAR(50) NOT NULL REFERENCES products(inventory_id) ON DELETE CASCADE,
    type            VARCHAR(20),
    item_id         TEXT,
    qty_required   DOUBLE PRECISION,
    activity_name   TEXT,   -- this is the "activities" field from the JSON (same value as item_id)
    class           VARCHAR(10),
    class_1         VARCHAR(10),
    sort_order      INTEGER  -- preserves the original order of activities for an item
);

CREATE INDEX idx_activities_inventory_id ON activities (inventory_id);
