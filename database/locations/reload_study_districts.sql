-- 1) Create location tables if missing (no passwords, no USE)
-- Select your DB on the left first (e.g. u924861691_enatha_survey)

CREATE TABLE IF NOT EXISTS provinces (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_province_name (name),
    INDEX idx_provinces_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS districts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    province_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_district_parent_name (province_id, name),
    INDEX idx_districts_province (province_id),
    INDEX idx_districts_status (status),
    CONSTRAINT fk_district_province FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sectors (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_sector_parent_name (district_id, name),
    INDEX idx_sectors_district (district_id),
    INDEX idx_sectors_status (status),
    CONSTRAINT fk_sector_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cells (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sector_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cell_parent_name (sector_id, name),
    INDEX idx_cells_sector (sector_id),
    INDEX idx_cells_status (status),
    CONSTRAINT fk_cell_sector FOREIGN KEY (sector_id) REFERENCES sectors(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS villages (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cell_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_village_parent_name (cell_id, name),
    INDEX idx_villages_cell (cell_id),
    INDEX idx_villages_status (status),
    CONSTRAINT fk_village_cell FOREIGN KEY (cell_id) REFERENCES cells(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2) Clear and load study districts

DELETE FROM villages;
DELETE FROM cells;
DELETE FROM sectors;
DELETE FROM districts;
DELETE FROM provinces;

START TRANSACTION;

INSERT INTO provinces (name, status) SELECT 'Eastern Province', 'active' FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM provinces WHERE name = 'Eastern Province');
INSERT INTO provinces (name, status) SELECT 'Kigali City', 'active' FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM provinces WHERE name = 'Kigali City');
INSERT INTO provinces (name, status) SELECT 'Northern Province', 'active' FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM provinces WHERE name = 'Northern Province');

INSERT INTO districts (province_id, name, status) SELECT p.id, 'Gasabo', 'active' FROM provinces p WHERE p.name = 'Kigali City' AND NOT EXISTS (SELECT 1 FROM districts d WHERE d.province_id = p.id AND d.name = 'Gasabo');
INSERT INTO districts (province_id, name, status) SELECT p.id, 'Bugesera', 'active' FROM provinces p WHERE p.name = 'Eastern Province' AND NOT EXISTS (SELECT 1 FROM districts d WHERE d.province_id = p.id AND d.name = 'Bugesera');
INSERT INTO districts (province_id, name, status) SELECT p.id, 'Gakenke', 'active' FROM provinces p WHERE p.name = 'Northern Province' AND NOT EXISTS (SELECT 1 FROM districts d WHERE d.province_id = p.id AND d.name = 'Gakenke');

INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Kimironko', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Kimironko');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Kinyinya', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Kinyinya');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Gisozi', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Gisozi');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Remera', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Remera');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Nyamata', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Nyamata');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Mayange', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Mayange');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Cyabingo', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Cyabingo');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Nemba', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Nemba');
INSERT INTO sectors (district_id, name, status) SELECT d.id, 'Ruli', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND NOT EXISTS (SELECT 1 FROM sectors s WHERE s.district_id = d.id AND s.name = 'Ruli');

INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Kibagabaga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kimironko' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Kibagabaga');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Murama', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Murama');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Kagugu', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Kagugu');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Musezero', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Gisozi' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Musezero');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Rukiri II', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Rukiri II');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Unspecified', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Unspecified');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Kayumba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Kayumba');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Nyamata y''Umujyi', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Nyamata y''Umujyi');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Nyamata/Town', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Nyamata/Town');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Gakamba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Gakamba');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Kibenga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Kibenga');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Muramba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Cyabingo' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Muramba');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Mucaca', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Mucaca');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Gahinga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Gahinga');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Gisozi', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Gisozi');
INSERT INTO cells (sector_id, name, status) SELECT s.id, 'Ruli Centre', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Ruli' AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.sector_id = s.id AND c.name = 'Ruli Centre');

INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Rugero', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kimironko' AND c.name = 'Kibagabaga' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Rugero');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Taba', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND c.name = 'Murama' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Taba');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND c.name = 'Kagugu' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Gisozi' AND c.name = 'Musezero' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND c.name = 'Rukiri II' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND c.name = 'Unspecified' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Kayumba' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Nyamata y''Umujyi' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Nyamata/Town' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND c.name = 'Gakamba' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND c.name = 'Kibenga' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Gahama', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Cyabingo' AND c.name = 'Muramba' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Gahama');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Cyahafi', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Mucaca' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Cyahafi');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Bukurura', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Gahinga' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Bukurura');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Muganwa', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Gisozi' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Muganwa');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Mucaca' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');
INSERT INTO villages (cell_id, name, status) SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Ruli' AND c.name = 'Ruli Centre' AND NOT EXISTS (SELECT 1 FROM villages v WHERE v.cell_id = c.id AND v.name = 'Unspecified');

COMMIT;

-- Verify:
-- SELECT p.name province, d.name district, COUNT(*) n
-- FROM provinces p JOIN districts d ON d.province_id=p.id
-- JOIN sectors s ON s.district_id=d.id JOIN cells c ON c.sector_id=s.id
-- JOIN villages v ON v.cell_id=c.id GROUP BY p.name, d.name;
