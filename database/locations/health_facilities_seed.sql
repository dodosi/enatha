-- Select your app database in phpMyAdmin LEFT panel BEFORE running this file.
-- Do not include USE enatha_survey (hosting DB name differs).
-- Study health facilities master list (from reviewer Excel)
-- Import after selecting your database.

CREATE TABLE IF NOT EXISTS health_facilities (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    facility_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    facility_level VARCHAR(80) NOT NULL,
    district_name VARCHAR(120) NOT NULL,
    sector_name VARCHAR(120) NULL,
    cell_name VARCHAR(120) NULL,
    village_name VARCHAR(120) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hf_district (district_name),
    INDEX idx_hf_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO health_facilities
(facility_code, name, facility_type, facility_level, district_name, sector_name, cell_name, village_name)
VALUES
('GAS-KIB-DH', 'Kibagabaga DH', 'Public', 'District Hospital', 'Gasabo', 'Kimironko', 'Kibagabaga', 'Rugero'),
('GAS-KAG-HC', 'Kagugu HC', 'Public', 'Health Center', 'Gasabo', 'Kinyinya', 'Kagugu', NULL),
('GAS-KIN-HC', 'Kinyinya HC', 'Public', 'Health Center', 'Gasabo', 'Kinyinya', 'Murama', 'Taba'),
('GAS-URW-HP', 'Urwego Health Post', 'Public', 'Post de Sante', 'Gasabo', NULL, NULL, NULL),
('GAS-KAG-MC', 'Kagugu Medical Clinic', 'Public', 'Post de Sante', 'Gasabo', 'Kinyinya', 'Kagugu', NULL),
('GAS-PLA-PC', 'Plateau Clinic / Polyclinique du Plateau', 'Private', 'Private Clinic', 'Gasabo', 'Remera', NULL, NULL),
('GAS-LCS-PC', 'La Croix du Sud', 'Private', 'Private Clinic', 'Gasabo', 'Remera', NULL, NULL),
('GAS-BCP-PH', 'Bella Care Pharmacy', 'Private', 'Private Pharmacy', 'Gasabo', 'Gisozi', 'Musezero', NULL),
('GAS-NGA-PH', 'Ngabo Pharmacy', 'Private', 'Private Pharmacy', 'Gasabo', 'Remera', 'Rukiri II', NULL),
('BUG-NYA-DH', 'Nyamata DH', 'Public', 'District Hospital', 'Bugesera', 'Nyamata', 'Kayumba', NULL),
('BUG-NYA-HC', 'Nyamata HC', 'Public', 'Health Center', 'Bugesera', 'Nyamata', 'Nyamata y''Umujyi', NULL),
('BUG-MAY-HC', 'Mayange HC', 'Public', 'Health Center', 'Bugesera', 'Mayange', 'Gakamba', NULL),
('BUG-NY2-HP', 'Nyamata Second Generation HP', 'Public', 'Post de Sante', 'Bugesera', NULL, NULL, NULL),
('BUG-KIB-HP', 'Kibenga HP', 'Public', 'Post de Sante', 'Bugesera', 'Mayange', 'Kibenga', NULL),
('BUG-BDC-PC', 'Benefactor David Clinic', 'Private', 'Private Clinic', 'Bugesera', 'Nyamata', 'Nyamata y''Umujyi', NULL),
('BUG-STE-PC', 'Stella Clinic', 'Private', 'Private Clinic', 'Bugesera', 'Nyamata', NULL, NULL),
('BUG-ESP-PH', 'Emma Sanitas Pharmacy LTD', 'Private', 'Private Pharmacy', 'Bugesera', 'Nyamata', 'Nyamata/Town', NULL),
('BUG-TGP-PH', 'The Guardian Pharmacy', 'Private', 'Private Pharmacy', 'Bugesera', 'Nyamata', 'Nyamata/Town', NULL),
('GAK-NEM-DH', 'Nemba DH', 'Public', 'District Hospital', 'Gakenke', 'Nemba', 'Mucaca', NULL),
('GAK-CYA-HC', 'Cyabingo HC', 'Public', 'Health Center', 'Gakenke', 'Cyabingo', 'Muramba', 'Gahama'),
('GAK-NEM-HC', 'Nemba HC', 'Public', 'Health Center', 'Gakenke', 'Nemba', 'Mucaca', 'Cyahafi'),
('GAK-GAH-HP', 'Gahinga HP', 'Public', 'Post de Sante', 'Gakenke', 'Nemba', 'Gahinga', 'Bukurura'),
('GAK-GIS-HP', 'Gisozi HP', 'Public', 'Post de Sante', 'Gakenke', 'Nemba', 'Gisozi', 'Muganwa'),
('GAK-PLM-PC', 'Polyclinic La Medicale', 'Private', 'Private Clinic', 'Gakenke', NULL, NULL, NULL),
('GAK-CMP-PC', 'Clinique Medicale Peace', 'Private', 'Private Clinic', 'Gakenke', NULL, NULL, NULL),
('GAK-MUS-PH', 'Pharmacy Musasa Ltd', 'Private', 'Private Pharmacy', 'Gakenke', 'Ruli', 'Ruli Centre', NULL),
('GAK-SUC-PH', 'Success Pharmacy Ltd', 'Private', 'Private Pharmacy', 'Gakenke', NULL, NULL, NULL)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    facility_type = VALUES(facility_type),
    facility_level = VALUES(facility_level),
    district_name = VALUES(district_name),
    sector_name = VALUES(sector_name),
    cell_name = VALUES(cell_name),
    village_name = VALUES(village_name),
    status = 'active';
