-- ============================================================
-- 1. REBUILD MASTER ACTIVITIES LIST (Remove Phase Constraint)
-- ============================================================
DROP TABLE IF EXISTS line_activities CASCADE;

CREATE TABLE line_activities (
    id                      SERIAL PRIMARY KEY,
    production_line_code    VARCHAR(20) NOT NULL REFERENCES production_lines(production_line_code) ON DELETE CASCADE,
    activity_name           TEXT NOT NULL,
    sort_order              INTEGER NOT NULL,
    -- Unique constraint now only cares that an activity isn't duplicated on the same line
    UNIQUE (production_line_code, activity_name) 
);

CREATE INDEX idx_line_activities_line_code ON line_activities (production_line_code);

-- ============================================================
-- 2. UPGRADE PRODUCTS TABLE (Support BM and FG Lines independently)
-- ============================================================
-- Rename the existing single line columns to designate them as 'BM'
ALTER TABLE products 
    RENAME COLUMN production_line TO bm_production_line;
ALTER TABLE products 
    RENAME COLUMN production_line_code TO bm_production_line_code;

-- Add the new columns for the 'FG' phase
ALTER TABLE products 
    ADD COLUMN fg_production_line TEXT,
    ADD COLUMN fg_production_line_code VARCHAR(20);

-- Apply Foreign Key constraints so both phases look up valid lines
ALTER TABLE products
    ADD CONSTRAINT fk_products_bm_line 
    FOREIGN KEY (bm_production_line_code) REFERENCES production_lines(production_line_code),
    
    ADD CONSTRAINT fk_products_fg_line 
    FOREIGN KEY (fg_production_line_code) REFERENCES production_lines(production_line_code);


INSERT INTO production_lines (production_line_code, production_line_name) VALUES
    ('Line01',  'Line 01 COATINGS'),
    ('Line02',  'Line 02 CYANO BOTTLE FILLING'),
    ('Line03',  'Line 03 CYANO TUBE FILLING'),
    ('Line04A', 'Line 04A ELASTO MIXING'),
    ('Line04B', 'Line 04B SEMI AUTO FILLING'),
    ('Line04C', 'Line 04C AUTO FILLING'),
    ('Line05',  'Line 05 EPOXY CLAY'),
    ('Line06',  'Line 06 EPOXY LINE'),
    ('Line07',  'Line 07 EPOXY TUBE FILLING'),
    ('Line08',  'Line 08'),
    ('Line09',  'Line 09 EPS - BLOCKS'),
    ('Line09A', 'Line 09A EPS - CUTTING'),
    ('Line10',  'Line 10 CONTACT BOND'),
    ('Line11',  'Line 11 SILICONE FILLING LINE'),
    ('Line12',  'Line 12 SPECIAL PRODUCTS - EPOXY BASED'),
    ('Line13',  'Line 13 SPECIAL PRODUCTS - WATER BASED'),
    ('Line14',  'Line 14 SKIM COAT'),
    ('SIPS',    'STRUCTURAL INSULATED PANEL')
ON CONFLICT DO NOTHING;


-- ------------------------------------------------------------
-- Populate the Redesigned line_activities table
-- Note: 'phase' constraint is removed. Activities are bound 
-- strictly to the production line.
-- ------------------------------------------------------------
INSERT INTO line_activities (production_line_code, activity_name, sort_order) VALUES
    ('Line01', 'MIXING', 1),
    ('Line01', 'MILLING', 2),
    ('Line01', 'LETDOWN', 3),
    ('Line01', 'TINTING', 4),
    ('Line01', 'CODING', 5),
    ('Line01', 'LABELING', 6),
    ('Line01', 'BOX PREPARATION', 7),
    ('Line01', 'MANUAL TRANSFER BM TO FILLING TANK', 8),
    ('Line01', 'FILLING', 9),
    ('Line01', 'CAPPING', 10),
    ('Line01', 'PACKING/PALLETIZING', 11),

    ('Line02', 'STICKERING', 1),
    ('Line02', 'CODING', 2),
    ('Line02', 'FILLING', 3),
    ('Line02', 'NOZZLE & CAPPING', 4),
    ('Line02', 'CAP TIGHTENING', 5),
    ('Line02', 'PLUNGERING', 6),
    ('Line02', 'TWIST TIE', 7),
    ('Line02', 'PACKING/PALLETIZING', 8),

    ('Line03', 'FILLING', 1),
    ('Line03', 'PACKING/PALLETIZING', 2),
    ('Line03', 'TRANSFER TO SUBCON', 3),

    ('Line04A', 'MIXING', 1),
    ('Line04A', 'CODING', 2),
    ('Line04A', 'BOX PREPARATION', 3),
    ('Line04A', 'TRANSFER BM TO ARO PUMP', 4),
    ('Line04A', 'SCOOPING', 5),
    ('Line04A', 'FILLING', 6),
    ('Line04A', 'PLUNGERING', 7),
    ('Line04A', 'SEALING', 8),
    ('Line04A', 'CAPPING', 9),
    ('Line04A', 'PACKING/PALLETIZING', 10),

    ('Line04B', 'MIXING', 1),
    ('Line04B', 'CODING', 2),
    ('Line04B', 'BOX PREPARATION', 3),
    ('Line04B', 'TRANSFER BM TO ARO PUMP', 4),
    ('Line04B', 'SCOOPING', 5),
    ('Line04B', 'FILLING', 6),
    ('Line04B', 'PLUNGERING', 7),
    ('Line04B', 'SEALING', 8),
    ('Line04B', 'CAPPING', 9),
    ('Line04B', 'PACKING/PALLETIZING', 10),

    ('Line04C', 'MIXING', 1),
    ('Line04C', 'CODING', 2),
    ('Line04C', 'BOX PREPARATION', 3),
    ('Line04C', 'TRANSFER BM TO ARO PUMP', 4),
    ('Line04C', 'SCOOPING', 5),
    ('Line04C', 'FILLING', 6),
    ('Line04C', 'PLUNGERING', 7),
    ('Line04C', 'SEALING', 8),
    ('Line04C', 'CAPPING', 9),
    ('Line04C', 'PACKING/PALLETIZING', 10),

    ('Line05', 'CUTTING', 1),
    ('Line05', 'STICKERING', 2),
    ('Line05', 'PACKING/PALLETIZING', 3),

    ('Line06', 'MIXING', 1),
    ('Line06', 'CODING', 2),
    ('Line06', 'LABELING', 3),
    ('Line06', 'BOX PREPARATION', 4),
    ('Line06', 'TRANSFER OF BM TO ARO PUMP', 5),
    ('Line06', 'FILLING', 6),
    ('Line06', 'CAPPING', 7),
    ('Line06', 'PACKING/PALLETIZING', 8),

    ('Line07', 'MIXING', 1),
    ('Line07', 'PRE HEAT OF BM', 2),
    ('Line07', 'FILLING', 3),
    ('Line07', 'PACKING/PALLETIZING', 4),
    ('Line07', 'TRANSFER TO SUBCON', 5),

    ('Line09', 'BEADS PRE EXPANSION', 1),
    ('Line09', 'MOLDING', 2),
    ('Line09', 'CUTTING', 3),

    ('Line09A', 'BEADS PRE EXPANSION', 1),
    ('Line09A', 'MOLDING', 2),
    ('Line09A', 'CUTTING', 3),

    ('Line10', 'CODING', 1),
    ('Line10', 'LABELING', 2),
    ('Line10', 'BOX PREPARATION', 3),
    ('Line10', 'FILLING', 4),
    ('Line10', 'CAPPING', 5),
    ('Line10', 'PACKING/PALLETIZING', 6),

    ('Line11', 'CODING', 1),
    ('Line11', 'FILLING', 2),
    ('Line11', 'SCOOPING', 3),
    ('Line11', 'PLUNGERING', 4),
    ('Line11', 'SEALING', 5),
    ('Line11', 'STICKERING', 6),
    ('Line11', 'PACKING/PALLETIZING', 7),
    ('Line11', 'TRANSFER TO SUBCON', 8),
    -- Custom actions pulled from the Woodglue routing file
    ('Line11', 'UNBOXING', 9),
    ('Line11', 'BATCH CODING', 10),
    ('Line11', 'PLACING OF CODED PAIL STICKER LABEL', 11),
    ('Line11', 'REBOXING', 12),
    ('Line11', 'PUTTING TEMPORARY BOX LABEL (PRINTED STICKER LABEL)', 13),
    ('Line11', 'PLACING OF QR CODE ON THE BOXES', 14),

    ('Line12', 'MIXING', 1),
    ('Line12', 'MELTING', 2),
    ('Line12', 'CODING', 3),
    ('Line12', 'LABELING', 4),
    ('Line12', 'BOX PREPARATION', 5),
    ('Line12', 'MANUAL TRANSFER BM TO FILLING TANK', 6),
    ('Line12', 'FILLING', 7),
    ('Line12', 'CAPPING', 8),
    ('Line12', 'SEALING', 9),
    ('Line12', 'PLUNGERING', 10),
    ('Line12', 'PACKING/PALLETIZING', 11),

    ('Line13', 'MIXING', 1),
    ('Line13', 'MELTING', 2),
    ('Line13', 'CODING', 3),
    ('Line13', 'LABELING', 4),
    ('Line13', 'BOX PREPARATION', 5),
    ('Line13', 'MANUAL TRANSFER BM TO FILLING TANK', 6),
    ('Line13', 'FILLING', 7),
    ('Line13', 'CAPPING', 8),
    ('Line13', 'SEALING', 9),
    ('Line13', 'PLUNGERING', 10),
    ('Line13', 'PACKING/PALLETIZING', 11),

    ('Line14', 'MIXING', 1),
    ('Line14', 'SIEVING', 2),
    ('Line14', 'CODING', 3),
    ('Line14', 'LABELING', 4),
    ('Line14', 'BOX PREPARATION', 5),
    ('Line14', 'FILLING', 6),
    ('Line14', 'CAPPING', 7),
    ('Line14', 'SEALING', 8),
    ('Line14', 'PACKING/PALLETIZING', 9),

    ('SIPS', 'BEADS PRE EXPANSION', 1),
    ('SIPS', 'MOLDING (BLOCK)', 2),
    ('SIPS', 'CUTTING (LAMINATE)', 3),
    ('SIPS', 'GLUING', 4),
    ('SIPS', 'PANEL ASSEMBLY', 5)
ON CONFLICT DO NOTHING;

ALTER TABLE products ADD COLUMN product_type VARCHAR(50);

-- Drop the existing FK if it exists (safe to run even if named differently)
ALTER TABLE line_activities
DROP CONSTRAINT IF EXISTS line_activities_production_line_code_fkey;

-- Re-add it with CASCADE on update and delete
ALTER TABLE line_activities
ADD CONSTRAINT line_activities_production_line_code_fkey
FOREIGN KEY (production_line_code)
REFERENCES production_lines(production_line_code)
ON UPDATE CASCADE
ON DELETE CASCADE;